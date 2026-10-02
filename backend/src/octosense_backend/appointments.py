"""附加命令：confirm_appointment / reject_appointment / reassign。

修复：
  - Q02：confirm_appointment 是 ACCEPTED→SCHEDULED 的唯一路径；propose 仅生成 PROPOSED 预约
  - Q04：confirm_appointment 仅原报修人；Manager P0 不代确认
  - Q05：reject_appointment 仅当存在 PROPOSED 时才允许
  - N06：reject_appointment 若存在旧 CONFIRMED 保持 SCHEDULED；无 CONFIRMED 才退回 ACCEPTED
  - N07：统一 payload_hash 幂等
  - 持久化 reason 到 events / action
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid

from octosense_backend.db import Database
from octosense_backend.errors import (
    IllegalTransition,
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


class AppointmentCommands:
    def __init__(self, db: Database):
        self.db = db

    def _record_action(self, cur, actor_id: str, idem_key: str, command: str,
                        project_id: str, task_id: str, expected_version: int | None,
                        result: str, payload_hash: str | None = None,
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

    def _check_idempotency(self, cur, actor_id: str, idem_key: str, payload_hash: str) -> dict | None:
        row = cur.execute(
            "SELECT result, error_code, error_detail, command, task_id, action_id, payload_hash "
            "FROM repair_actions WHERE actor_id=? AND idempotency_key=?",
            (actor_id, idem_key),
        ).fetchone()
        if row is None:
            return None
        if row["result"] != "OK":
            raise IdempotencyConflict(
                f"previous action failed: {row['error_code']}: {row['error_detail']}"
            )
        if row["payload_hash"] is not None and row["payload_hash"] != payload_hash:
            raise IdempotencyConflict("idempotency_key reused with different payload")
        return {
            "idempotent_replay": True,
            "task_id": row["task_id"],
            "command": row["command"],
            "action_id": row["action_id"],
        }

    def confirm_appointment(
        self, actor_id: str, idem_key: str, task_id: str,
        expected_version: int, appointment_id: str | None = None,
    ) -> dict:
        """原报修人确认当前 PROPOSED 预约为 CONFIRMED。
        旧 CONFIRMED 置 SUPERSEDED；task.version +=1；状态由 ACCEPTED→SCHEDULED。
        """
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "appointment_id": appointment_id or "",
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, reporter_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            # Q04：仅原报修人（不允许 Manager 代确认）
            if actor_id != row["reporter_id"]:
                raise PermissionDenied("only original reporter can confirm appointment")
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            if row["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(
                    f"cannot confirm appointment from task status {row['status']}"
                )
            if appointment_id:
                appt = cur.execute(
                    "SELECT * FROM repair_appointments WHERE appointment_id=? AND task_id=?",
                    (appointment_id, task_id),
                ).fetchone()
            else:
                appt = cur.execute(
                    "SELECT * FROM repair_appointments WHERE task_id=? AND status='PROPOSED'",
                    (task_id,),
                ).fetchone()
            if appt is None or appt["status"] != "PROPOSED":
                raise IllegalTransition("no PROPOSED appointment to confirm")
            tech_id = appt["technician_id"]
            start, end = appt["start_at_ms"], appt["end_at_ms"]
            # 冲突检查：排除当前将被替换的预约
            overlap = cur.execute(
                "SELECT appointment_id FROM repair_appointments WHERE technician_id=? AND status='CONFIRMED' "
                "AND appointment_id<>? AND start_at_ms < ? AND end_at_ms > ?",
                (tech_id, appt["appointment_id"], end, start),
            ).fetchone()
            if overlap:
                raise OctoSenseError(
                    "CONCURRENT_CONFLICT", f"tech {tech_id} overlap {overlap['appointment_id']}",
                    http_status=409,
                )
            # 旧 CONFIRMED 置 SUPERSEDED
            cur.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='CONFIRMED'",
                (_now_ms(), task_id),
            )
            # 新 PROPOSED 改 CONFIRMED
            cur.execute(
                "UPDATE repair_appointments SET status='CONFIRMED', confirmed_by=?, updated_at_ms=? "
                "WHERE appointment_id=?",
                (actor_id, _now_ms(), appt["appointment_id"]),
            )
            # task 状态：仅原 ACCEPTED 才升 SCHEDULED
            if row["status"] == "ACCEPTED":
                cur.execute(
                    "UPDATE repair_tasks SET status='SCHEDULED', version=version+1, updated_at_ms=? "
                    "WHERE task_id=?",
                    (_now_ms(), task_id),
                )
            else:
                cur.execute(
                    "UPDATE repair_tasks SET version=version+1, updated_at_ms=? WHERE task_id=?",
                    (_now_ms(), task_id),
                )
            new_ver = row["version"] + 1
            self._record_action(cur, actor_id, idem_key, "confirm_appointment",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?)",
                (task_id, new_ver, "confirm_appointment", actor_id,
                 json.dumps({
                     "appointment_id": appt["appointment_id"], "status": "CONFIRMED",
                     "task_status": "SCHEDULED" if row["status"] == "ACCEPTED" else row["status"],
                 }, ensure_ascii=False),
                 _now_ms()),
            )
            return {
                "task_id": task_id, "appointment_id": appt["appointment_id"],
                "status": "CONFIRMED", "task_version": new_ver,
                "task_status": "SCHEDULED" if row["status"] == "ACCEPTED" else row["status"],
            }

    def reject_appointment(
        self, actor_id: str, idem_key: str, task_id: str,
        expected_version: int, reason: str,
    ) -> dict:
        """原报修人拒绝当前 PROPOSED 预约。
        - 有旧 CONFIRMED：保持 SCHEDULED
        - 无旧 CONFIRMED：保持 ACCEPTED
        - 不存在 PROPOSED：拒绝
        """
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not reason.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "reject reason required", http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version, "reason": reason,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version, reporter_id FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if actor_id != row["reporter_id"]:
                raise PermissionDenied("only original reporter can reject appointment")
            if row["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(
                    f"cannot reject appointment from task status {row['status']}"
                )
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            # Q05：必须存在 PROPOSED 才能拒绝
            proposed = cur.execute(
                "SELECT appointment_id FROM repair_appointments WHERE task_id=? AND status='PROPOSED'",
                (task_id,),
            ).fetchall()
            if not proposed:
                raise IllegalTransition("no PROPOSED appointment to reject")
            cur.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='PROPOSED'",
                (_now_ms(), task_id),
            )
            # N06：保留旧 CONFIRMED；只有无旧 CONFIRMED 才退回 ACCEPTED
            old_confirmed = cur.execute(
                "SELECT 1 FROM repair_appointments WHERE task_id=? AND status='CONFIRMED' LIMIT 1",
                (task_id,),
            ).fetchone()
            target_status = "SCHEDULED" if old_confirmed else "ACCEPTED"
            if row["status"] != target_status:
                cur.execute(
                    "UPDATE repair_tasks SET status=?, version=version+1, updated_at_ms=? WHERE task_id=?",
                    (target_status, _now_ms(), task_id),
                )
            else:
                cur.execute(
                    "UPDATE repair_tasks SET version=version+1, updated_at_ms=? WHERE task_id=?",
                    (_now_ms(), task_id),
                )
            new_ver = row["version"] + 1
            self._record_action(cur, actor_id, idem_key, "reject_appointment",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash, error_detail=reason)
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?)",
                (task_id, new_ver, "reject_appointment", actor_id,
                 json.dumps({"status": target_status, "reason": reason}, ensure_ascii=False),
                 _now_ms()),
            )
            return {"task_id": task_id, "status": target_status, "version": new_ver, "reason": reason}

    def reassign(
        self, actor_id: str, idem_key: str, task_id: str,
        new_assignee_id: str, expected_version: int, reason: str,
    ) -> dict:
        """经理改派 ACCEPTED/SCHEDULED 任务；释放旧预约、任务回 ACCEPTED。"""
        if not isinstance(expected_version, int) or expected_version < 1:
            raise OctoSenseError("DRAFT_MISSING_FIELD", "expected_version must be positive integer",
                                 http_status=422)
        if not reason.strip():
            raise OctoSenseError("DRAFT_MISSING_FIELD", "reassign reason required", http_status=422)
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "new_assignee_id": new_assignee_id, "reason": reason,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return replay
            row = cur.execute(
                "SELECT project_id, status, version FROM repair_tasks WHERE task_id=?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if row["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(f"cannot reassign from {row['status']}")
            roles = cur.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
                (actor_id, row["project_id"]),
            ).fetchall()
            if not any(r["role"] == "MANAGER" for r in roles):
                raise PermissionDenied("only project manager can reassign")
            if expected_version != row["version"]:
                raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
            target_roles = cur.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=? AND role='TECHNICIAN'",
                (new_assignee_id, row["project_id"]),
            ).fetchall()
            if not target_roles:
                raise PermissionDenied(f"{new_assignee_id} is not a TECHNICIAN in this project")
            cur.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status IN ('CONFIRMED','PROPOSED')",
                (_now_ms(), task_id),
            )
            cur.execute(
                "UPDATE repair_tasks SET assignee_id=?, status='ACCEPTED', version=version+1, updated_at_ms=? "
                "WHERE task_id=?",
                (new_assignee_id, _now_ms(), task_id),
            )
            new_ver = row["version"] + 1
            self._record_action(cur, actor_id, idem_key, "reassign",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash, error_detail=reason)
            cur.execute(
                "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, before_state, after_state, at_ms) "
                "VALUES (?,?,?,?,?,?,?)",
                (task_id, new_ver, "reassign", actor_id,
                 json.dumps({"status": row["status"]}, ensure_ascii=False),
                 json.dumps({"assignee_id": new_assignee_id, "status": "ACCEPTED", "reason": reason},
                            ensure_ascii=False),
                 _now_ms()),
            )
            return {
                "task_id": task_id, "assignee_id": new_assignee_id,
                "status": "ACCEPTED", "version": new_ver, "reason": reason,
            }
