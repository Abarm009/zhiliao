"""任务内核：命令执行器。

14 类核心命令的最小实现子集（修复 R-P0-2 / R-P0-4 / N02 / N03 / N05 / N08 / N09 / Q01 / Q02 / Q03）：
  - create_draft
  - confirm_draft（草稿 → OPEN）
  - accept_task（OPEN → ACCEPTED，技工接单）
  - assign_task（OPEN → ACCEPTED，经理分配）
  - propose_appointment（保持 ACCEPTED，新增 PROPOSED 预约；不直接 SCHEDULED）
  - confirm_appointment（PROPOSED → CONFIRMED，任务 → SCHEDULED）
  - reject_appointment（PROPOSED → SUPERSEDED）
  - start_progress（SCHEDULED → IN_PROGRESS；必须 CONFIRMED + 设备绑定 + 时段内）
  - record_progress（IN_PROGRESS 期间记处置）
  - submit_completion（IN_PROGRESS → AWAITING_ACCEPTANCE；分配 completion_id 轮次）
  - accept_completion（AWAITING_ACCEPTANCE → COMPLETED；多角色校验）
  - reject_completion（AWAITING_ACCEPTANCE → IN_PROGRESS，附理由；持久化到 events）
  - cancel（各阶段取消，写理由；释放预约）
  - add_pin / remove_pin（用户收藏，不影响任务 version）

约束：
  - 全部写操作必须在 Database.tx() 内
  - 所有动作记 repair_actions，幂等键 actor+idempotency_key + payload_hash
  - 每次成功动作记一条 repair_events（含 reason/completion_id 写入 after_state）
  - 任务 version 随成功命令 +1
  - 同一 actor 同 key 同 payload 返回原 action_id（replay）；同 key 不同 payload 409
  - 命令级源状态：accept/assign 仅 OPEN；reject_completion 仅 AWAITING_ACCEPTANCE；
    reject_appointment 仅存在 PROPOSED；start_progress 仅 SCHEDULED + CONFIRMED + 已绑定
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from typing import Any, Callable

from octosense_backend.db import Database
from octosense_backend.errors import (
    ConcurrentConflict,
    DraftMissingField,
    IdentityRequired,
    IdempotencyConflict,
    IllegalTransition,
    OctoSenseError,
    PermissionDenied,
    TaskNotFound,
    VersionConflict,
)


# 状态机：合法转移表
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"OPEN", "CANCELLED"},
    "OPEN": {"ACCEPTED", "CANCELLED"},
    "ACCEPTED": {"SCHEDULED", "CANCELLED"},
    "SCHEDULED": {"IN_PROGRESS", "ACCEPTED", "CANCELLED"},   # AC: 改派或拒绝
    "IN_PROGRESS": {"AWAITING_ACCEPTANCE", "CANCELLED"},
    "AWAITING_ACCEPTANCE": {"COMPLETED", "IN_PROGRESS"},     # 后者：拒绝
    "COMPLETED": set(),
    "CANCELLED": set(),
}

# 命令允许的源状态（独立于 LEGAL_TRANSITIONS 防止 SCHEDULED 路径绕过）
COMMAND_SOURCE_STATES: dict[str, set[str]] = {
    "create_draft": set(),                                # 任意，建任务
    "confirm_draft": {"DRAFT"},
    "accept_task": {"OPEN"},
    "assign_task": {"OPEN"},
    "propose_appointment": {"ACCEPTED", "SCHEDULED"},     # 修复 Q02：状态不变；改约场景允许从 SCHEDULED 提议
    "confirm_appointment": {"ACCEPTED", "SCHEDULED"},     # PROPOSED→CONFIRMED
    "reject_appointment": {"ACCEPTED", "SCHEDULED"},
    "start_progress": {"SCHEDULED"},                      # 修复 N02：仅 SCHEDULED
    "record_progress": {"IN_PROGRESS"},
    "submit_completion": {"IN_PROGRESS"},
    "accept_completion": {"AWAITING_ACCEPTANCE"},
    "reject_completion": {"AWAITING_ACCEPTANCE"},         # 修复 Q01：仅 AWAITING
    "cancel": {"DRAFT", "OPEN", "ACCEPTED", "SCHEDULED", "IN_PROGRESS"},
}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _uuid() -> str:
    return uuid.uuid4().hex


def canonical_payload_hash(payload: dict) -> str:
    """规范化业务参数生成指纹。

    仅保留可比较业务字段，忽略幂等键/版本/动作类型等元数据。
    """
    canon = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


class CommandResult:
    def __init__(self, ok: bool, data: dict | None = None, error: OctoSenseError | None = None):
        self.ok = ok
        self.data = data or {}
        self.error = error

    def to_dict(self) -> dict:
        if self.ok:
            return {"ok": True, **self.data}
        return {"ok": False, "error": self.error.to_dict()}


class CommandExecutor:
    """所有命令通过该执行器。设计：
    -  每个调用必须带 idempotency_key, actor_id, project_id（actor 必须是该项目角色）
    -  actor_resolver(project_id, actor_id) -> set[str] of roles in this project
    -  失败也记 action（result=ERROR）保证审计
    -  payload_hash 比较：同 key 不同内容 409
    """

    def __init__(self, db: Database, actor_resolver: Callable[[str, str], set[str]],
                 clock: Callable[[], int] | None = None):
        self.db = db
        self.actor_resolver = actor_resolver
        self._clock = clock or _now_ms

    # ---- helpers ----

    def _check_actor_role(self, project_id: str, actor_id: str, allowed: set[str],
                          *, allow_manager: bool = True) -> set[str]:
        """返回角色集合。

        错误区分：
          - 未在任何项目注册的 actor → 401 IDENTITY_REQUIRED
          - 注册过但不在此 project / 角色不符 → 403 PERMISSION_DENIED
        Manager 代行限于同 project；不允许全局跨项目越权。
        """
        roles = self.actor_resolver(project_id, actor_id)
        if not roles:
            # 区分"从未注册"与"已注册但不在此项目"
            any_role = self.actor_resolver_any_project(actor_id)
            if not any_role:
                raise IdentityRequired("actor not registered")
            raise PermissionDenied(f"actor not in project {project_id}")
        if allow_manager and "MANAGER" in roles:
            return roles
        if not (roles & allowed):
            raise PermissionDenied(f"actor needs one of {sorted(allowed)}")
        return roles

    def actor_resolver_any_project(self, actor_id: str) -> set[str]:
        """辅助：检查 actor 在任意项目中的角色。"""
        conn = self.db.conn()
        try:
            rows = conn.execute(
                "SELECT role FROM repair_roles WHERE user_id=?", (actor_id,),
            ).fetchall()
            return {r["role"] for r in rows}
        finally:
            conn.close()

    def _check_idempotency(self, cur, actor_id: str, idem_key: str,
                           payload_hash: str) -> dict | None:
        """命中同 key 同 hash → replay 原 action_id / task_id / command；不同 hash → 409。"""
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
            raise IdempotencyConflict(
                "idempotency_key reused with different payload"
            )
        return {
            "idempotent_replay": True,
            "task_id": row["task_id"],
            "command": row["command"],
            "action_id": row["action_id"],
        }

    def _record_action(self, cur, actor_id: str, idem_key: str, command: str,
                        project_id: str | None, task_id: str | None,
                        expected_version: int | None,
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

    def _record_event(self, cur, task_id: str, task_version: int, event_type: str,
                      actor_id: str, before: dict | None, after: dict | None) -> None:
        cur.execute(
            "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, before_state, after_state, at_ms) "
            "VALUES (?,?,?,?,?,?,?)",
            (task_id, task_version, event_type, actor_id,
             json.dumps(before, ensure_ascii=False) if before else None,
             json.dumps(after, ensure_ascii=False) if after else None,
             _now_ms()),
        )

    def _check_command_source(self, cur, command: str, task_id: str,
                              allowed_states: set[str]) -> dict:
        row = cur.execute(
            "SELECT * FROM repair_tasks WHERE task_id=?", (task_id,),
        ).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        if allowed_states and row["status"] not in allowed_states:
            raise IllegalTransition(
                f"command {command} requires source state in {sorted(allowed_states)}, "
                f"got {row['status']}"
            )
        return dict(row)

    def _transition(self, cur, task_id: str, expected_version: int | None,
                    next_status: str, actor_id: str, event_type: str) -> dict:
        row = cur.execute(
            "SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)
        ).fetchone()
        if row is None:
            raise TaskNotFound(f"task {task_id}")
        if expected_version is not None and row["version"] != expected_version:
            raise VersionConflict(
                f"task version {row['version']} != expected {expected_version}"
            )
        current = row["status"]
        if next_status not in LEGAL_TRANSITIONS.get(current, set()):
            raise IllegalTransition(f"{current} -> {next_status} not allowed")
        cur.execute(
            "UPDATE repair_tasks SET status=?, version=version+1, updated_at_ms=? WHERE task_id=?",
            (next_status, _now_ms(), task_id),
        )
        new_version = row["version"] + 1
        self._record_event(cur, task_id, new_version, event_type, actor_id,
                           dict(row), {"status": next_status, "version": new_version})
        return {"task_id": task_id, "status": next_status, "version": new_version}

    # ---- commands ----

    def create_draft(
        self, actor_id: str, idem_key: str, problem_text: str,
        contact_name: str, project_id: str, preferred_window: str = "",
        space_id: str | None = None, contact_info: str = "",
    ) -> CommandResult:
        if not problem_text.strip():
            raise DraftMissingField("problem_text required")
        if not contact_name.strip():
            raise DraftMissingField("contact_name required")
        if not project_id:
            raise DraftMissingField("project_id required")

        payload_hash = canonical_payload_hash({
            "project_id": project_id, "problem_text": problem_text,
            "contact_name": contact_name, "contact_info": contact_info,
            "preferred_window": preferred_window, "space_id": space_id,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            self._check_actor_role(project_id, actor_id, {"REPORTER"})
            # 校验项目存在
            proj = cur.execute(
                "SELECT 1 FROM repair_projects WHERE project_id=?", (project_id,)
            ).fetchone()
            if proj is None:
                raise OctoSenseError("PROJECT_NOT_FOUND", f"project {project_id}", http_status=404)
            # 校验 space_id 同项目
            if space_id:
                sp = cur.execute(
                    "SELECT 1 FROM repair_spaces WHERE space_id=? AND project_id=?",
                    (space_id, project_id),
                ).fetchone()
                if sp is None:
                    raise OctoSenseError("INVALID_PROJECT_REFERENCE",
                                         f"space {space_id} not in project {project_id}",
                                         http_status=422)
            task_id = _uuid()
            now = _now_ms()
            cur.execute(
                "INSERT INTO repair_tasks (task_id, project_id, reporter_id, status, version, "
                "problem_text, contact_name, contact_info, preferred_window, space_id, "
                "created_at_ms, updated_at_ms) "
                "VALUES (?,?,?,'DRAFT',1,?,?,?,?,?,?,?)",
                (task_id, project_id, actor_id, problem_text, contact_name, contact_info,
                 preferred_window, space_id, now, now),
            )
            row = cur.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
            self._record_event(cur, task_id, 1, "create_draft", actor_id, None, dict(row))
            self._record_action(cur, actor_id, idem_key, "create_draft", project_id, task_id, None,
                                "OK", payload_hash=payload_hash)
            return CommandResult(ok=True, data={"task_id": task_id, "status": "DRAFT", "version": 1})

    def confirm_draft(self, actor_id: str, idem_key: str, task_id: str,
                      expected_version: int = 1) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            row = cur.execute("SELECT project_id, status, reporter_id FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            self._check_actor_role(row["project_id"], actor_id, {"REPORTER"})
            # 原报修人才能确认；防他人冒充
            if row["reporter_id"] != actor_id:
                raise PermissionDenied("only original reporter can confirm this draft")
            data = self._transition(cur, task_id, expected_version, "OPEN", actor_id, "confirm_draft")
            self._record_action(cur, actor_id, idem_key, "confirm_draft",
                                row["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data=data)

    def accept_task(self, actor_id: str, idem_key: str, task_id: str,
                    expected_version: int) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "accept_task", task_id, COMMAND_SOURCE_STATES["accept_task"])
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            data = self._transition(cur, task_id, expected_version, "ACCEPTED", actor_id, "accept_task")
            cur.execute("UPDATE repair_tasks SET assignee_id=? WHERE task_id=?", (actor_id, task_id))
            self._record_action(cur, actor_id, idem_key, "accept_task",
                                task["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={**data, "assignee_id": actor_id})

    def assign_task(self, actor_id: str, idem_key: str, task_id: str, assignee_id: str,
                    expected_version: int, reason: str = "") -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        if not reason.strip():
            raise DraftMissingField("assign reason required")
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "assignee_id": assignee_id, "reason": reason,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "assign_task", task_id, COMMAND_SOURCE_STATES["assign_task"])
            self._check_actor_role(task["project_id"], actor_id, {"MANAGER"})
            # 目标必须同项目有效 TECHNICIAN
            target = cur.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=? AND role='TECHNICIAN'",
                (assignee_id, task["project_id"]),
            ).fetchone()
            if target is None:
                raise PermissionDenied(f"{assignee_id} is not a TECHNICIAN in this project")
            data = self._transition(cur, task_id, expected_version, "ACCEPTED", actor_id, "assign_task")
            cur.execute(
                "UPDATE repair_tasks SET assignee_id=? WHERE task_id=?", (assignee_id, task_id)
            )
            new_ver = data["version"]
            self._record_event(cur, task_id, new_ver, "assign_task", actor_id,
                               dict(task), {"status": "ACCEPTED", "assignee_id": assignee_id, "reason": reason})
            self._record_action(cur, actor_id, idem_key, "assign_task",
                                task["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={**data, "assignee_id": assignee_id, "reason": reason})

    def propose_appointment(self, actor_id: str, idem_key: str, task_id: str,
                            start_at_ms: int, end_at_ms: int, expected_version: int) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        if end_at_ms <= start_at_ms:
            raise DraftMissingField("end_at_ms must be > start_at_ms")
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "start_at_ms": start_at_ms, "end_at_ms": end_at_ms,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            # 仅 ACCEPTED 可提议；保持 ACCEPTED 不直接 SCHEDULED
            task = self._check_command_source(cur, "propose_appointment", task_id,
                                              COMMAND_SOURCE_STATES["propose_appointment"])
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            tech_id = task["assignee_id"]
            if tech_id is None:
                raise OctoSenseError("NO_ASSIGNEE", "task has no assignee", http_status=422)
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            # 当前承接者才能提议
            if tech_id != actor_id and "MANAGER" not in self.actor_resolver(task["project_id"], actor_id):
                raise PermissionDenied("only current assignee can propose appointment")
            overlap = cur.execute(
                "SELECT appointment_id FROM repair_appointments WHERE technician_id=? AND status='CONFIRMED' "
                "AND start_at_ms < ? AND end_at_ms > ?",
                (tech_id, end_at_ms, start_at_ms),
            ).fetchone()
            if overlap:
                raise ConcurrentConflict(f"technician {tech_id} has confirmed overlap {overlap['appointment_id']}")
            # 已有 PROPOSED 置 SUPERSEDED
            cur.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='PROPOSED'",
                (_now_ms(), task_id),
            )
            appt_id = _uuid()
            cur.execute(
                "INSERT INTO repair_appointments (appointment_id, task_id, technician_id, "
                "start_at_ms, end_at_ms, status, proposed_by, created_at_ms, updated_at_ms) "
                "VALUES (?,?,?,?,?,'PROPOSED',?,?,?)",
                (appt_id, task_id, tech_id, start_at_ms, end_at_ms, actor_id, _now_ms(), _now_ms()),
            )
            # 保持 task 状态为 ACCEPTED；仅 version +1
            cur.execute(
                "UPDATE repair_tasks SET version=version+1, updated_at_ms=? WHERE task_id=?",
                (_now_ms(), task_id),
            )
            new_version = task["version"] + 1
            self._record_event(cur, task_id, new_version, "propose_appointment", actor_id,
                               dict(task), {"appointment_id": appt_id, "status": "ACCEPTED",
                                            "appt_status": "PROPOSED"})
            self._record_action(cur, actor_id, idem_key, "propose_appointment",
                                task["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={
                "task_id": task_id, "status": "ACCEPTED", "version": new_version,
                "appointment_id": appt_id,
            })

    def start_progress(self, actor_id: str, idem_key: str, task_id: str,
                      expected_version: int) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "start_progress", task_id,
                                              COMMAND_SOURCE_STATES["start_progress"])
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            # 当前承接者
            if task["assignee_id"] != actor_id:
                raise PermissionDenied("only current assignee can start progress")
            # 设备必须绑定
            if not task["asset_id"]:
                raise IllegalTransition(
                    "no asset bound; cannot start_progress before bind_asset"
                )
            # 必须存在本任务的 CONFIRMED 预约，且 start<=now<end
            appt = cur.execute(
                "SELECT appointment_id, start_at_ms, end_at_ms FROM repair_appointments "
                "WHERE task_id=? AND status='CONFIRMED' LIMIT 1",
                (task_id,),
            ).fetchone()
            if appt is None:
                raise IllegalTransition(
                    "no CONFIRMED appointment; cannot start_progress before reporter confirms a slot"
                )
            now = self._clock()
            if not (appt["start_at_ms"] <= now < appt["end_at_ms"]):
                raise IllegalTransition(
                    f"current time {now} outside CONFIRMED window "
                    f"[{appt['start_at_ms']}, {appt['end_at_ms']})"
                )
            data = self._transition(cur, task_id, expected_version, "IN_PROGRESS", actor_id, "start_progress")
            self._record_action(cur, actor_id, idem_key, "start_progress",
                                task["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data=data)

    def submit_completion(self, actor_id: str, idem_key: str, task_id: str,
                         completion_text: str, expected_version: int,
                         disposition: str = "REPAIRED") -> CommandResult:
        """分配 completion_id + round；持久化到 repair_completions 与 events。"""
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        if not completion_text.strip():
            raise DraftMissingField("completion_text required")
        payload_hash = canonical_payload_hash({
            "task_id": task_id, "expected_version": expected_version,
            "completion_text": completion_text, "disposition": disposition,
        })
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "submit_completion", task_id,
                                              COMMAND_SOURCE_STATES["submit_completion"])
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            if task["assignee_id"] != actor_id:
                raise PermissionDenied("only current assignee can submit completion")
            # 必须有 READY 证据
            evidence_rows = cur.execute(
                "SELECT evidence_id, sha256 FROM repair_evidence "
                "WHERE task_id=? AND status='READY'",
                (task_id,),
            ).fetchall()
            if not evidence_rows:
                raise DraftMissingField(
                    "completion requires at least one READY evidence; "
                    "upload a photo or note via POST /tasks/{id}/evidence first"
                )
            evidence_ids = [r["evidence_id"] for r in evidence_rows]
            # 分配 round：取 max(round)+1
            last = cur.execute(
                "SELECT MAX(round) AS r FROM repair_completions WHERE task_id=?",
                (task_id,),
            ).fetchone()
            new_round = (last["r"] or 0) + 1
            completion_id = _uuid()
            cur.execute(
                "INSERT INTO repair_completions (completion_id, task_id, round, submitter_id, "
                "completion_text, disposition, evidence_ids, created_at_ms) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (completion_id, task_id, new_round, actor_id, completion_text, disposition,
                 json.dumps(evidence_ids, ensure_ascii=False), _now_ms()),
            )
            data = self._transition(cur, task_id, expected_version, "AWAITING_ACCEPTANCE",
                                    actor_id, "submit_completion")
            # 事件中含 completion_id 与文本，方便重开回读
            self._record_event(cur, task_id, data["version"], "submit_completion", actor_id,
                               dict(task), {
                                   "status": "AWAITING_ACCEPTANCE",
                                   "completion_id": completion_id,
                                   "round": new_round,
                                   "completion_text": completion_text,
                                   "disposition": disposition,
                                   "evidence_ids": evidence_ids,
                               })
            self._record_action(cur, actor_id, idem_key, "submit_completion",
                                task["project_id"], task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={
                **data, "completion_text": completion_text,
                "completion_id": completion_id, "round": new_round,
            })

    def accept_completion(self, actor_id: str, idem_key: str, task_id: str,
                         expected_version: int, reason: str = "") -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version,
                                              "reason": reason})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "accept_completion", task_id,
                                              COMMAND_SOURCE_STATES["accept_completion"])
            project_id = task["project_id"]
            reporter_id = task["reporter_id"]
            assignee_id = task["assignee_id"]
            roles = self.actor_resolver(project_id, actor_id)
            # 多角色完整权限矩阵：原报修人 / 同项目经理
            is_reporter = (actor_id == reporter_id)
            is_manager = ("MANAGER" in roles)
            if not (is_reporter or is_manager):
                raise PermissionDenied("only original reporter or project manager can accept completion")
            # 当前承接者（含多角色）不能自验
            if assignee_id == actor_id:
                raise PermissionDenied("assignee cannot accept own completion")
            # 经理代验收必须有理由
            if is_manager and not is_reporter and not reason.strip():
                raise DraftMissingField("manager-accept reason required")
            data = self._transition(cur, task_id, expected_version, "COMPLETED", actor_id, "accept_completion")
            if reason.strip():
                self._record_event(cur, task_id, data["version"], "accept_completion", actor_id,
                                   dict(task), {"status": "COMPLETED", "reason": reason})
            self._record_action(cur, actor_id, idem_key, "accept_completion",
                                project_id, task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data=data)

    def reject_completion(self, actor_id: str, idem_key: str, task_id: str,
                         expected_version: int, reason: str) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        if not reason.strip():
            raise DraftMissingField("reject reason required")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version,
                                              "reason": reason})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            # 修复 Q01：仅 AWAITING_ACCEPTANCE 可拒绝
            task = self._check_command_source(cur, "reject_completion", task_id,
                                              COMMAND_SOURCE_STATES["reject_completion"])
            project_id = task["project_id"]
            reporter_id = task["reporter_id"]
            roles = self.actor_resolver(project_id, actor_id)
            is_reporter = (actor_id == reporter_id)
            is_manager = ("MANAGER" in roles)
            if not (is_reporter or is_manager):
                raise PermissionDenied("only original reporter or project manager can reject completion")
            if task["assignee_id"] == actor_id:
                raise PermissionDenied("rejector cannot be the assignee")
            data = self._transition(cur, task_id, expected_version, "IN_PROGRESS", actor_id, "reject_completion")
            self._record_event(cur, task_id, data["version"], "reject_completion", actor_id,
                               dict(task), {"status": "IN_PROGRESS", "reason": reason})
            self._record_action(cur, actor_id, idem_key, "reject_completion",
                                project_id, task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={**data, "reason": reason})

    def cancel(self, actor_id: str, idem_key: str, task_id: str,
               expected_version: int, reason: str) -> CommandResult:
        if not isinstance(expected_version, int) or expected_version < 1:
            raise DraftMissingField("expected_version must be positive integer")
        if not reason.strip():
            raise DraftMissingField("cancel reason required")
        payload_hash = canonical_payload_hash({"task_id": task_id, "expected_version": expected_version,
                                              "reason": reason})
        with self.db.tx() as conn:
            cur = conn.cursor()
            replay = self._check_idempotency(cur, actor_id, idem_key, payload_hash)
            if replay:
                return CommandResult(ok=True, data=replay)
            task = self._check_command_source(cur, "cancel", task_id, COMMAND_SOURCE_STATES["cancel"])
            project_id = task["project_id"]
            reporter_id = task["reporter_id"]
            roles = self.actor_resolver(project_id, actor_id)
            is_reporter = (actor_id == reporter_id)
            is_manager = ("MANAGER" in roles)
            # 报修人仅能取消自己 DRAFT/OPEN；其他状态需经理
            if is_reporter and task["status"] in {"DRAFT", "OPEN"}:
                pass
            elif is_manager:
                if not reason.strip():
                    raise DraftMissingField("cancel reason required")
            else:
                raise PermissionDenied(
                    "reporter can only cancel own DRAFT/OPEN; manager required for other states"
                )
            data = self._transition(cur, task_id, expected_version, "CANCELLED", actor_id, "cancel")
            cur.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status IN ('PROPOSED','CONFIRMED')",
                (_now_ms(), task_id),
            )
            self._record_event(cur, task_id, data["version"], "cancel", actor_id,
                               dict(task), {"status": "CANCELLED", "reason": reason})
            self._record_action(cur, actor_id, idem_key, "cancel",
                                project_id, task_id, expected_version, "OK",
                                payload_hash=payload_hash)
            return CommandResult(ok=True, data={**data, "reason": reason})
