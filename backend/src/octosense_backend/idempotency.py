"""统一幂等实现（core / appointments / extended / 所有适配器共用）。

修复 V05 / V11：
  - 指纹必须包含 command、actor、project、task、expected_version 与规范化业务参数；
    因此 pin 与 unpin 即使 key 相同也必定 409，不会互相回放。
  - `IdempotencyConflict` 的导入集中在这里，避免各模块 NameError → 500。
  - 首次成功保存完整原结果（repair_actions.result_json）；重试回放返回**同一
    action_id + 完整原结果**，而不是只剩 task_id/command。
  - 回放发生在对象授权之后：重放仍会重新校验主体对任务的当前访问权。
  - `repair_actions` 只保存成功回执（UNIQUE(actor_id, idempotency_key)）；
    失败尝试另写 `repair_action_failures` 追加式审计表，业务回滚不会丢，
    也不会把失败留成成功回执，同一 key 失败后仍可按修正参数重试。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from typing import Any

from octosense_backend.errors import IdempotencyConflict


def _now_ms() -> int:
    return int(time.time() * 1000)


def canonical_hash(payload: Any) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def normalize_params(params: dict | None) -> dict:
    """去掉空值与 None，避免 '' 与缺失造成假冲突。"""
    out: dict[str, Any] = {}
    for k, v in (params or {}).items():
        if v is None:
            continue
        if isinstance(v, str) and v == "":
            continue
        out[k] = v
    return out


def fingerprint(command: str, actor_id: str, project_id: str | None, task_id: str | None,
                expected_version: int | None, params: dict | None = None) -> str:
    """命令级指纹：换命令即换指纹。"""
    return canonical_hash({
        "command": command,
        "actor_id": actor_id,
        "project_id": project_id,
        "task_id": task_id,
        "expected_version": expected_version,
        "params": normalize_params(params),
    })


def find_receipt(conn: sqlite3.Connection, actor_id: str, idem_key: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM repair_actions WHERE actor_id=? AND idempotency_key=?",
        (actor_id, idem_key),
    ).fetchone()


def check_replay(conn: sqlite3.Connection, actor_id: str, idem_key: str,
                 fp: str) -> dict | None:
    """命中同 (actor, key) 的成功回执：
      - 指纹不同（含命令不同）→ 409
      - 历史 NULL 指纹         → 409（无法证明同一请求，绝不静默放行）
      - 指纹相同               → 返回完整原结果
    """
    row = find_receipt(conn, actor_id, idem_key)
    if row is None:
        return None
    stored_fp = row["payload_hash"]
    if stored_fp is None or stored_fp != fp:
        raise IdempotencyConflict("idempotency_key reused with a different command or payload")
    original = load_result(row)
    if original is None:
        raise IdempotencyConflict(
            "legacy receipt stored no result payload; cannot replay the original response"
        )
    return {
        "idempotent_replay": True,
        "action_id": row["action_id"],
        "command": row["command"],
        "task_id": row["task_id"],
        "created_at_ms": row["created_at_ms"],
        "result": original,
    }


def load_result(row: sqlite3.Row) -> dict | None:
    raw = None
    try:
        raw = row["result_json"]
    except (IndexError, KeyError):
        raw = None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def record_receipt(conn: sqlite3.Connection, actor_id: str, idem_key: str, command: str,
                   project_id: str | None, task_id: str | None,
                   expected_version: int | None, fp: str,
                   response: dict | None = None, action_id: str | None = None) -> str:
    action_id = action_id or uuid.uuid4().hex
    conn.execute(
        "INSERT INTO repair_actions (action_id, idempotency_key, actor_id, project_id, command, "
        "task_id, expected_version, result, error_code, error_detail, payload_hash, result_json, "
        "created_at_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (action_id, idem_key, actor_id, project_id, command, task_id, expected_version,
         "OK", None, None, fp,
         json.dumps(response, ensure_ascii=False) if response is not None else None,
         _now_ms()),
    )
    return action_id


def record_failure(db, actor_id: str, idem_key: str, command: str,
                   project_id: str | None, task_id: str | None,
                   expected_version: int | None, fp: str,
                   error_code: str, error_detail: str) -> bool:
    """追加式失败审计（独立事务）。返回是否写入。"""
    try:
        with db.tx() as conn:
            conn.execute(
                "INSERT INTO repair_action_failures (failure_id, idempotency_key, actor_id, "
                "project_id, command, task_id, expected_version, payload_hash, error_code, "
                "error_detail, created_at_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (uuid.uuid4().hex, idem_key, actor_id, project_id, command, task_id,
                 expected_version, fp, error_code, str(error_detail)[:500], _now_ms()),
            )
            return True
    except Exception:
        return False


def strict_positive_int(value: Any, field: str = "expected_version") -> int:
    """严格正整数：拒绝 None、bool、float、字符串与 <=0。"""
    from octosense_backend.errors import InvalidVersion
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidVersion(
            f"{field} must be a strict positive integer, got {type(value).__name__}")
    if value < 1:
        raise InvalidVersion(f"{field} must be >= 1, got {value}")
    return value
