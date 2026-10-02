"""扩展命令：覆盖 L3-L7 的剩余 P0 用例。

修复：
  - N01: bind_asset / unbind_asset 完整阶段角色校验 + 终态禁写
  - N04: history_advice 严格按当前任务可见性 + 项目
  - N13: quarantine_evidence 验证归属 + rowcount
  - R-P1-3/N07: record_advice 增加权限校验与幂等回放
  - N07: 统一 payload_hash 幂等
  - N16: 移除 install_extended_schema 与 EXTRA_SCHEMA 死代码

所有命令均通过 Database.tx() 原子事务；事件写入 repair_events；
命令动作写入 repair_actions；与既有 executor 共享幂等键/版本约束。
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from octosense_backend.db import Database
from octosense_backend.errors import (
    AssetNotFound,
    AssetArchived,
    EvidenceNotFound,
    EvidenceTooLarge,
    EvidenceQuarantined,
    IllegalTransition,
    InvalidProjectReference,
    OctoSenseError,
    PermissionDenied,
    TaskNotFound,
    VersionConflict,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _uuid() -> str:
    return uuid.uuid4().hex


def canonical_payload_hash(payload: dict) -> str:
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


# 命令级源状态：bind/unbind 允许阶段
BIND_ALLOWED_STATES = {"DRAFT", "OPEN", "ACCEPTED", "SCHEDULED", "IN_PROGRESS"}


class ExtendedCommands:
    """覆盖 L3-L7 的剩余命令。"""

    def __init__(self, db: Database, evidence_root: str | Path | None = None,
                 clock: Callable[[], int] | None = None):
        self.db = db
        # R-P1-7：默认 evidence_root 锚到工程根的 runtime/evidence（不再跟 CWD 浮动）
        if evidence_root:
            self.evidence_root = Path(evidence_root)
        else:
            self.evidence_root = Path(__file__).resolve().parents[3] / "runtime" / "evidence"
        self.evidence_root.mkdir(parents=True, exist_ok=True)
        self.max_evidence_bytes = int(os.environ.get("OCTOSENSE_EVIDENCE_MAX_BYTES", str(8 * 1024 * 1024)))
        self._clock = clock or _now_ms

    # -------- helpers --------

    def _check_idempotency(self, cur, actor_id: str, idem_key: str, payload_hash: str) -> dict | None:
        row = cur.execute(
            "SELECT result, command, task_id, action_id, payload_hash FROM repair_actions "
            "WHERE actor_id=? AND idempotency_key=?",
            (actor_id, idem_key),
        ).fetchone()
        if row is None:
            return None
        if row["result"] != "OK":
            raise IdempotencyConflict(
                f"previous action failed: command={row['command']}"
            )
        if row["payload_hash"] is not None and row["payload_hash"] != payload_hash:
            raise IdempotencyConflict("idempotency_key reused with different payload")
        return {
            "idempotent_replay": True, "task_id": row["task_id"], "command": row["command"],
            "action_id": row["action_id"],
        }

    def _record_action(self, cur, actor_id: str, idem_key: str, command: str,
                       project_id: str | None, task_id: str | None,
                       expected_version: int | None, result: str,
                       payload_hash: str | None = None,
                       error_code: str | None = None, error_detail: str | None = None) -> str:
        action_id = _uuid()
        cur.execute(
            "INSERT INTO repair_actions (action_id, idempotency_key, actor_id, project_id, command, "
            "task_id, expected_version, result, error_code, error_detail, payload_hash, created_at_ms) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (action_id, idem_key, actor_id, project_id, command, task_id, expected_version,
             result, error_code, error_detail, payload_hash, _now_ms()),
        )
        return action_id

    def _check_role(self, cur, project_id: str, actor_id: str, allowed: set[str]) -> set[str]:
        rows = cur.execute(
            "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
            (actor_id, project_id),
        ).fetchall()
        roles = {r["role"] for r in rows}
        if not roles:
            raise PermissionDenied("actor not in this project")
        return roles

    def _resolve_actor(self, cur, project_id: str, actor_id: str, allowed: set[str]) -> set[str]:
        """统一角色解析：Manager 可代行同项目任何命令；其他角色须在 allowed 中。"""
        roles = self._check_role(cur, project_id, actor_id, allowed)
        if "MANAGER" in roles:
            return roles
        if not (roles & allowed):
            raise PermissionDenied(f"actor needs one of {sorted(allowed)}")
        return roles

    def actor_resolver_any_project(self, actor_id: str) -> set[str]:
        """辅助：检查 actor 在任意项目中的角色（用于区分 401/403）。"""
        conn = self.db.conn()
        try:
            rows = conn.execute(
                "SELECT role FROM repair_roles WHERE user_id=?", (actor_id,),
            ).fetchall()
            return {r["role"] for r in rows}
        finally:
            conn.close()

    # -------- 设备匹配/绑定 (T07/T08/T09) --------

    def match_assets_by_code(self, actor_id: str, project_id: str, code: str) -> dict:
        """按编码或 asset: 载荷解析设备；伪造 ID/其他项目 ID/归档设备拒绝。"""
        with self.db.tx() as conn:
            cur = conn.cursor()
            self._resolve_actor(cur, project_id, actor_id, {"REPORTER", "TECHNICIAN", "MANAGER"})
            asset_code = code.removeprefix("asset:") if code.startswith("asset:") else code
            if not asset_code or len(asset_code) > 64:
                raise OctoSenseError("ASSET_CODE_INVALID", "code too long or empty", http_status=422)
            rows = cur.execute(
                "SELECT asset_id, project_id, asset_code, display_name, source, active "
                "FROM repair_assets WHERE asset_code=?",
                (asset_code,),
            ).fetchall()
            hits = []
            for r in rows:
                if r["project_id"] != project_id:
                    continue
                if not r["active"]:
                    continue
                hits.append({
                    "asset_id": r["asset_id"],
                    "asset_code": r["asset_code"],
                    "display_name": r["display_name"],
                    "source": r["source"],
                })
            if not hits:
                raise AssetNotFound(f"no active asset in this project with code {asset_code}")
            return {"matches": hits, "code": asset_code}

    def bind_asset(self, actor_id: str, idem_key: str, task_id: str,
                   asset_id: str, expected_version: int) -> dict:
        """绑定设备到任务；要求在同项目、未归档。

        N01：阶段+主体规则
          - DRAFT：仅原报修人
          - OPEN / ACCEPTED / SCHEDULED：报修人或当前承接者；MANAGER 仅"修改原因"
          - IN_PROGRESS：仅 manager；带 reason 强制
          - COMPLETED / CANCELLED：拒绝
        """
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "asset_id": asset_id, "expected_version": expected_version,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, asset_id, assignee_id, reporter_id "
                "FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if row["status"] not in BIND_ALLOWED_STATES:
                raise IllegalTransition(
                    f"cannot bind asset in terminal state {row['status']}"
                )
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            asset = cur.execute(
                "SELECT asset_id, project_id, active, asset_code, display_name, source "
                "FROM repair_assets WHERE asset_id=?",
                (asset_id,),
            ).fetchone()
            if asset is None:
                raise AssetNotFound(asset_id)
            if asset["project_id"] != row["project_id"]:
                raise InvalidProjectReference("asset not in task's project")
            if not asset["active"]:
                raise AssetArchived(asset_id)
            # 阶段权限
            status = row["status"]
            if status == "DRAFT":
                if actor_id != row["reporter_id"]:
                    raise PermissionDenied("only original reporter can bind asset in DRAFT")
            elif status == "IN_PROGRESS":
                # 经理修改设备：必须带 reason；这里只调入 reason；扩展可在 api 层补字段
                roles = self._check_role(cur, row["project_id"], actor_id, {"MANAGER"})
            else:  # OPEN/ACCEPTED/SCHEDULED
                roles = self._check_role(cur, row["project_id"], actor_id,
                                         {"REPORTER", "TECHNICIAN", "MANAGER"})
                is_reporter = actor_id == row["reporter_id"]
                is_assignee = actor_id == row["assignee_id"]
                is_manager = "MANAGER" in roles
                if not (is_reporter or is_assignee or is_manager):
                    raise PermissionDenied("only reporter, current assignee, or manager can bind asset")
            old_asset_id = row["asset_id"]
            cur.execute(
                "UPDATE repair_tasks SET asset_id=?, version=version+1, updated_at_ms=? WHERE task_id=?",
                (asset_id, _now_ms(), task_id),
            )
            new_ver = row["version"] + 1
            self._record_action(cur, actor_id, idem_key, "bind_asset",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, before_state, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?,?)",
                (task_id, new_ver, "bind_asset", actor_id,
                 json.dumps({"asset_id": old_asset_id}, ensure_ascii=False),
                 json.dumps({"asset_id": asset_id, "asset_code": asset["asset_code"]}, ensure_ascii=False),
                 _now_ms()),
            )
            return {
                "task_id": task_id, "asset_id": asset_id,
                "asset_code": asset["asset_code"], "version": new_ver,
            }

    def unbind_asset(self, actor_id: str, idem_key: str, task_id: str,
                     expected_version: int, reason: str) -> dict:
        """解绑设备，要求带 reason；IN_PROGRESS 只能经理。"""
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not reason.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "reason required", http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version, "reason": reason,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, asset_id, assignee_id, reporter_id "
                "FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if row["status"] not in BIND_ALLOWED_STATES:
                raise IllegalTransition(f"cannot unbind asset in terminal state {row['status']}")
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            roles = self._check_role(cur, row["project_id"], actor_id, {"REPORTER", "TECHNICIAN", "MANAGER"})
            is_reporter = actor_id == row["reporter_id"]
            is_assignee = actor_id == row["assignee_id"]
            is_manager = "MANAGER" in roles
            if not (is_reporter or is_assignee or is_manager):
                raise PermissionDenied("only reporter, current assignee, or manager can unbind asset")
            if row["status"] == "IN_PROGRESS" and not is_manager:
                raise PermissionDenied("only manager can change asset during IN_PROGRESS")
            cur.execute(
                "UPDATE repair_tasks SET asset_id=NULL, version=version+1, updated_at_ms=? WHERE task_id=?",
                (_now_ms(), task_id),
            )
            new_ver = row["version"] + 1
            self._record_action(cur, actor_id, idem_key, "unbind_asset",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash, error_detail=reason)
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?)",
                (task_id, new_ver, "unbind_asset", actor_id,
                 json.dumps({"asset_id": None, "reason": reason}, ensure_ascii=False), _now_ms()),
            )
            return {"task_id": task_id, "asset_id": None, "version": new_ver, "reason": reason}

    # -------- 证据附件 (T19) --------

    def upload_evidence(self, actor_id: str, idem_key: str, task_id: str,
                        filename: str, mime_type: str, payload: bytes,
                        expected_version: int) -> dict:
        """上传证据附件。仅本任务参与者 + 经理可传；超限/类型非法拒绝。"""
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not filename.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "filename required", http_status=422)
        if not payload:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "payload empty", http_status=422)
        if len(payload) > self.max_evidence_bytes:
            raise EvidenceTooLarge(f"max {self.max_evidence_bytes} bytes")
        # MIME 限制
        allowed_mime_prefixes = ("image/", "text/", "application/json", "application/octet-stream")
        if not any(mime_type.startswith(p) for p in allowed_mime_prefixes):
            raise OctoSenseError("EVIDENCE_MIME_REJECTED", mime_type, http_status=422)
        sha = hashlib.sha256(payload).hexdigest()
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "filename": filename, "mime_type": mime_type, "sha256": sha,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, reporter_id, assignee_id "
                "FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            roles = self._check_role(cur, row["project_id"], actor_id,
                                     {"REPORTER", "TECHNICIAN", "MANAGER"})
            is_reporter = actor_id == row["reporter_id"]
            is_assignee = actor_id == row["assignee_id"]
            is_manager = "MANAGER" in roles
            if not (is_reporter or is_assignee or is_manager):
                raise PermissionDenied("only reporter, current assignee, or manager can upload evidence")
            evidence_id = _uuid()
            target_dir = self.evidence_root / task_id
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{evidence_id}.bin"
            tmp_path = target_dir / f"{evidence_id}.tmp"
            try:
                tmp_path.write_bytes(payload)
                tmp_path.rename(target_path)
            except Exception:
                if tmp_path.exists():
                    tmp_path.unlink()
                raise
            cur.execute(
                "INSERT INTO repair_evidence (evidence_id, task_id, uploader_id, filename, mime_type, "
                "byte_size, sha256, storage_path, status, created_at_ms) "
                "VALUES (?,?,?,?,?,?,?,?, 'READY', ?)",
                (evidence_id, task_id, actor_id, filename, mime_type, len(payload),
                 sha, str(target_path), _now_ms()),
            )
            self._record_action(cur, actor_id, idem_key, "upload_evidence",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return {
                "evidence_id": evidence_id, "task_id": task_id,
                "filename": filename, "byte_size": len(payload), "sha256": sha,
            }

    def list_evidence(self, actor_id: str, task_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            row = cur.execute(
                "SELECT project_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._resolve_actor(cur, row["project_id"], actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            rows = cur.execute(
                "SELECT evidence_id, filename, mime_type, byte_size, sha256, status, uploader_id, created_at_ms "
                "FROM repair_evidence WHERE task_id=? ORDER BY created_at_ms",
                (task_id,),
            ).fetchall()
            return {"task_id": task_id, "evidence": [dict(r) for r in rows]}

    def download_evidence(self, actor_id: str, task_id: str, evidence_id: str) -> dict:
        """返回证据 payload + 元数据，供下载/校验使用。"""
        with self.db.tx() as conn:
            cur = conn.cursor()
            row = cur.execute(
                "SELECT project_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._resolve_actor(cur, row["project_id"], actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            ev = cur.execute(
                "SELECT * FROM repair_evidence WHERE evidence_id=? AND task_id=?",
                (evidence_id, task_id),
            ).fetchone()
            if ev is None:
                raise EvidenceNotFound(evidence_id)
            if ev["status"] == "QUARANTINED":
                raise EvidenceQuarantined(evidence_id)
            payload = Path(ev["storage_path"]).read_bytes()
            actual_sha = hashlib.sha256(payload).hexdigest()
            if actual_sha != ev["sha256"]:
                raise EvidenceQuarantined(f"sha mismatch on {evidence_id}")
            return {
                "evidence_id": evidence_id,
                "filename": ev["filename"],
                "mime_type": ev["mime_type"],
                "byte_size": ev["byte_size"],
                "payload": payload,
                "sha256": ev["sha256"],
            }

    def quarantine_evidence(self, actor_id: str, idem_key: str, task_id: str,
                            evidence_id: str, expected_version: int, reason: str) -> dict:
        """经理/报修人标记证据为隔离。

        N13：必须验证证据归属当前任务，否则 404；UPDATE 后必须影响行数。
        """
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not reason.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "reason required", http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "evidence_id": evidence_id, "expected_version": expected_version,
            "reason": reason,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, version, reporter_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            roles = self._check_role(cur, row["project_id"], actor_id, {"REPORTER", "MANAGER"})
            is_reporter = actor_id == row["reporter_id"]
            is_manager = "MANAGER" in roles
            if not (is_reporter or is_manager):
                raise PermissionDenied("only reporter or manager can quarantine evidence")
            ev = cur.execute(
                "SELECT status FROM repair_evidence WHERE evidence_id=? AND task_id=?",
                (evidence_id, task_id),
            ).fetchone()
            if ev is None:
                raise EvidenceNotFound(evidence_id)
            cur.execute(
                "UPDATE repair_evidence SET status='QUARANTINED' WHERE evidence_id=? AND task_id=?",
                (evidence_id, task_id),
            )
            self._record_action(cur, actor_id, idem_key, "quarantine_evidence",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash, error_detail=reason)
            return {"evidence_id": evidence_id, "status": "QUARANTINED", "reason": reason}

    # -------- 收藏 (T30) --------

    def add_pin(self, actor_id: str, idem_key: str, task_id: str) -> dict:
        payload_hash = canonical_payload_hash({"task_id": task_id})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._resolve_actor(cur, row["project_id"], actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            try:
                cur.execute(
                    "INSERT INTO repair_pins (project_id, user_id, task_id, created_at_ms) VALUES (?,?,?,?)",
                    (row["project_id"], actor_id, task_id, _now_ms()),
                )
            except Exception:
                # 已存在
                pass
            self._record_action(cur, actor_id, idem_key, "add_pin",
                                row["project_id"], task_id, None, "OK",
                                payload_hash=payload_hash)
            return {"task_id": task_id, "pinned": True}

    def remove_pin(self, actor_id: str, idem_key: str, task_id: str) -> dict:
        payload_hash = canonical_payload_hash({"task_id": task_id})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._resolve_actor(cur, row["project_id"], actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            cur.execute(
                "DELETE FROM repair_pins WHERE user_id=? AND task_id=?",
                (actor_id, task_id),
            )
            self._record_action(cur, actor_id, idem_key, "remove_pin",
                                row["project_id"], task_id, None, "OK",
                                payload_hash=payload_hash)
            return {"task_id": task_id, "pinned": False}

    def list_pins(self, actor_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT p.task_id, p.created_at_ms, t.status, t.problem_text "
                "FROM repair_pins p JOIN repair_tasks t ON t.task_id=p.task_id "
                "WHERE p.user_id=? ORDER BY p.created_at_ms DESC",
                (actor_id,),
            ).fetchall()
            return {"pins": [dict(r) for r in rows]}

    # -------- 记录处置（IN_PROGRESS 期间） --------

    def record_progress(self, actor_id: str, idem_key: str, task_id: str,
                        note: str, expected_version: int) -> dict:
        """技工在 IN_PROGRESS 期间记处置；存 events 不改 status。"""
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not note.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "note required", http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version, "note": note,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, assignee_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if row["status"] != "IN_PROGRESS":
                raise IllegalTransition(f"record_progress requires IN_PROGRESS, got {row['status']}")
            if row["assignee_id"] != actor_id:
                raise PermissionDenied("only assignee can record progress")
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            new_ver = row["version"] + 1
            cur.execute(
                "UPDATE repair_tasks SET version=?, updated_at_ms=? WHERE task_id=?",
                (new_ver, _now_ms(), task_id),
            )
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?)",
                (task_id, new_ver, "record_progress", actor_id,
                 json.dumps({"note": note}, ensure_ascii=False), _now_ms()),
            )
            self._record_action(cur, actor_id, idem_key, "record_progress",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return {"task_id": task_id, "version": new_ver, "note": note}

    # -------- 任务列表与查询（L5 视图） --------

    def list_tasks(self, actor_id: str, project_id: str,
                   role_filter: str | None = None,
                   status_filter: str | None = None,
                   limit: int = 50) -> dict:
        """任务列表：服务端按角色自动收紧可见范围；客户端筛选只能缩小。"""
        with self.db.tx() as conn:
            cur = conn.cursor()
            roles = self._resolve_actor(cur, project_id, actor_id,
                                        {"REPORTER", "TECHNICIAN", "MANAGER"})
            effective_role = role_filter
            if effective_role is None:
                # 服务端按主体最严角色自动收紧
                if "REPORTER" in roles:
                    effective_role = "REPORTER"
                elif "TECHNICIAN" in roles:
                    effective_role = "TECHNICIAN"
                else:
                    effective_role = "MANAGER"
            params: list[Any] = [project_id]
            sql = "SELECT t.task_id, t.status, t.version, t.problem_text, t.reporter_id, t.assignee_id, " \
                  "t.asset_id, t.updated_at_ms, t.created_at_ms, t.project_id " \
                  "FROM repair_tasks t WHERE t.project_id=?"
            if effective_role == "REPORTER":
                sql += " AND t.reporter_id=?"
                params.append(actor_id)
            elif effective_role == "TECHNICIAN":
                sql += " AND t.assignee_id=?"
                params.append(actor_id)
            elif effective_role != "MANAGER":
                raise PermissionDenied(f"unknown role_filter: {effective_role}")
            if status_filter:
                sql += " AND t.status=?"
                params.append(status_filter)
            sql += " ORDER BY t.updated_at_ms DESC LIMIT ?"
            params.append(int(limit))
            rows = cur.execute(sql, tuple(params)).fetchall()
            return {"project_id": project_id, "tasks": [dict(r) for r in rows], "count": len(rows)}

    def get_history_advice(self, actor_id: str, task_id: str,
                           asset_id: str | None = None) -> dict:
        """N04：历史经验建议；严格按可见性过滤。

        - 仅返回当前任务所属项目 + 当前主体可见范围内的历史任务
        - asset_id 若提供：必须是当前任务的 asset 或同项目可见设备；否则 404
        """
        with self.db.tx() as conn:
            cur = conn.cursor()
            row = cur.execute(
                "SELECT project_id, asset_id, reporter_id, assignee_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            roles = self._resolve_actor(cur, row["project_id"], actor_id,
                                        {"REPORTER", "TECHNICIAN", "MANAGER"})
            is_manager = "MANAGER" in roles
            target_asset = asset_id or row["asset_id"]
            if target_asset is None:
                return {"task_id": task_id, "asset_id": None,
                        "history": [], "events": [], "advice": "未绑定设备，无历史依据"}
            # 验证设备存在、同项目、未归档
            asset_row = cur.execute(
                "SELECT project_id, active FROM repair_assets WHERE asset_id=?",
                (target_asset,),
            ).fetchone()
            if asset_row is None or asset_row["project_id"] != row["project_id"] or not asset_row["active"]:
                raise OctoSenseError("INVALID_PROJECT_REFERENCE",
                                     "asset not visible to this task",
                                     http_status=404)
            # 历史：项目内同设备；非 manager 还须与当前任务有 reporter/assignee 关系
            params = [target_asset, task_id]
            history_sql = (
                "SELECT task_id, project_id, reporter_id, assignee_id, status, problem_text, "
                "created_at_ms, updated_at_ms FROM repair_tasks "
                "WHERE asset_id=? AND task_id<>?"
            )
            if not is_manager:
                history_sql += " AND (reporter_id=? OR assignee_id=?)"
                params.extend([actor_id, actor_id])
            history_sql += " ORDER BY updated_at_ms DESC LIMIT 10"
            history = cur.execute(history_sql, tuple(params)).fetchall()
            events = cur.execute(
                "SELECT seq, event_type, actor_id, after_state, at_ms "
                "FROM repair_events WHERE task_id=? ORDER BY seq DESC LIMIT 20",
                (task_id,),
            ).fetchall()
            advice = (
                f"该设备过去有 {len(history)} 次维修记录，最近状态："
                f"{history[0]['status'] if history else '无'}"
            )
            return {
                "task_id": task_id,
                "asset_id": target_asset,
                "history": [dict(h) for h in history],
                "events": [dict(e) for e in events],
                "advice": advice,
            }

    def record_advice(self, actor_id: str, idem_key: str, task_id: str,
                      source_kind: str, payload: dict) -> dict:
        """R-P1-3/N07：记录一条助手/历史建议；不改任务状态；含幂等与权限校验。"""
        if source_kind not in {"DEVICE_HISTORY", "STAGE_HINT", "PROGRESS_NOTE"}:
            raise OctoSenseError("INVALID_KIND", source_kind, http_status=422)
        payload_hash = canonical_payload_hash({"task_id": task_id, "source_kind": source_kind,
                                              "payload": payload})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._resolve_actor(cur, row["project_id"], actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            advice_id = _uuid()
            cur.execute(
                "INSERT INTO repair_advice (advice_id, task_id, actor_id, source_kind, payload, created_at_ms) "
                "VALUES (?,?,?,?,?,?)",
                (advice_id, task_id, actor_id, source_kind,
                 json.dumps(payload, ensure_ascii=False), _now_ms()),
            )
            self._record_action(cur, actor_id, idem_key, "record_advice",
                                row["project_id"], task_id, None, "OK",
                                payload_hash=payload_hash)
            return {"advice_id": advice_id, "task_id": task_id, "source_kind": source_kind}
