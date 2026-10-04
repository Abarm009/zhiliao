"""任务内核：命令执行边界（所有写操作的唯一入口）。

固定版本：0.4.0。本文件综合修复 R-P0-2/3/4、N01–N09、Q01–Q06、V02–V11。

不变量：
  - 每个命令都在 `Database.tx()`（BEGIN IMMEDIATE）内；成功回执、事件、业务写
    要么全提交要么全回滚。
  - 服务端按已认证主体 + 项目角色 + 任务关系 + 技能 + 阶段推导权限；客户端任何
    参数（含 role）只能缩小范围。
  - `expected_version` 是严格正整数；命令有独立允许源状态表。
  - 指纹 = command + actor + project + task + expected_version + 规范化业务参数；
    同 key 不同命令/参数 → 409；同 key 同内容 → 原 action_id + 完整原结果。
  - 回放发生在对象授权之后；主体失去访问权时重放同样被拒。
  - 失败尝试写 `repair_action_failures` 追加审计，不回滚业务，也不留成成功回执。
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Callable

from octosense_backend import authorization as auth
from octosense_backend import idempotency as idem
from octosense_backend.db import Database
from octosense_backend.errors import (
    AppointmentWindowInvalid,
    ConcurrentConflict,
    DraftMissingField,
    EvidenceIntegrity,
    IdentityRequired,
    IllegalTransition,
    InvalidProjectReference,
    NoAssignee,
    OctoSenseError,
    PermissionDenied,
    SkillMismatch,
    SpaceRequired,
    TaskNotFound,
    VersionConflict,
)
from octosense_backend.jobs import schedule_acceptance_reminder
from octosense_backend.paths import default_db_path, default_evidence_root  # noqa: F401

API_VERSION = "0.4.0"

# 状态机：合法转移表
LEGAL_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"OPEN", "CANCELLED"},
    "OPEN": {"ACCEPTED", "CANCELLED"},
    "ACCEPTED": {"SCHEDULED", "CANCELLED"},
    "SCHEDULED": {"IN_PROGRESS", "ACCEPTED", "CANCELLED"},
    "IN_PROGRESS": {"AWAITING_ACCEPTANCE", "CANCELLED"},
    "AWAITING_ACCEPTANCE": {"COMPLETED", "IN_PROGRESS"},
    "COMPLETED": set(),
    "CANCELLED": set(),
}

# 命令允许的源状态（独立于 LEGAL_TRANSITIONS，专门封堵 SCHEDULED 绕过路径）
COMMAND_SOURCE_STATES: dict[str, set[str]] = {
    "create_draft": set(),
    "update_draft": {"DRAFT"},
    "confirm_draft": {"DRAFT"},
    "accept_task": {"OPEN"},
    "assign_task": {"OPEN"},
    "propose_appointment": {"ACCEPTED", "SCHEDULED"},
    "confirm_appointment": {"ACCEPTED", "SCHEDULED"},
    "reject_appointment": {"ACCEPTED", "SCHEDULED"},
    "start_progress": {"SCHEDULED"},
    "record_progress": {"IN_PROGRESS"},
    "submit_completion": {"IN_PROGRESS"},
    "accept_completion": {"AWAITING_ACCEPTANCE"},
    "reject_completion": {"AWAITING_ACCEPTANCE"},
    "cancel": {"DRAFT", "OPEN", "ACCEPTED", "SCHEDULED", "IN_PROGRESS"},
}

# 预约产品默认值（01_REQUIREMENTS.md §8，可配置，非赛事硬规则）
APPOINTMENT_DEFAULTS = {
    "max_lead_ms": 30 * 24 * 3600 * 1000,     # 开始不得晚于当前时间 + 30 天
    "min_duration_ms": 15 * 60 * 1000,
    "max_duration_ms": 240 * 60 * 1000,
    "proposal_validity_ms": 24 * 3600 * 1000,  # min(24h, 开始时间 - 现在)
}

_EVIDENCE_MIME_PREFIXES = ("image/", "text/", "application/json", "application/octet-stream")


def _now_ms() -> int:
    return int(time.time() * 1000)


def _uuid() -> str:
    return uuid.uuid4().hex


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
    """所有命令通过该执行器。"""

    def __init__(self, db: Database, actor_resolver: Callable[[str, str], set[str]] | None = None,
                 clock: Callable[[], int] | None = None,
                 evidence_root=None,
                 appointment_defaults: dict | None = None):
        self.db = db
        self._clock = clock or _now_ms
        self.evidence_root = evidence_root
        self.appt_defaults = dict(APPOINTMENT_DEFAULTS)
        if appointment_defaults:
            self.appt_defaults.update(appointment_defaults)
        # actor_resolver 保留以兼容旧调用方签名；授权统一走 authorization 模块
        self.actor_resolver = actor_resolver or (lambda project_id, actor_id: set())

    # ---------- 通用 ----------

    def now(self) -> int:
        return int(self._clock())

    def _check_actor_role(self, project_id: str, actor_id: str, allowed: set[str],
                          *, allow_manager: bool = False) -> set[str]:
        """按项目解析角色。

        错误区分：从未注册 → 401；已注册但不在项目/角色不符 → 403。
        `allow_manager=False` 用于自主接单等场景：经理不得隐式代行技工。
        """
        conn = self.db.conn()
        try:
            roles = auth.roles_of(conn, actor_id, project_id)
            any_role = conn.execute(
                "SELECT 1 FROM repair_roles WHERE user_id=? LIMIT 1", (actor_id,)
            ).fetchone()
        finally:
            conn.close()
        if any_role is None:
            raise IdentityRequired(f"actor {actor_id} not registered")
        if not roles:
            raise PermissionDenied(f"actor not in project {project_id}")
        if roles & allowed:
            return roles
        if allow_manager and "MANAGER" in roles:
            return roles
        raise PermissionDenied(f"actor needs one of {sorted(allowed)}")

    def _resolve_task(self, conn, task_id: str) -> dict:
        row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        return dict(row)

    def _assert_visible(self, conn, task: dict, actor_id: str) -> None:
        if not auth.task_visible(conn, actor_id, task):
            raise TaskNotFound(task["task_id"])

    def _check_source(self, task: dict, command: str) -> None:
        allowed = COMMAND_SOURCE_STATES[command]
        if allowed and task["status"] not in allowed:
            raise IllegalTransition(
                f"command {command} requires source state in {sorted(allowed)}, "
                f"got {task['status']}")

    def _transition(self, conn, task_id: str, expected_version: int | None,
                    next_status: str, actor_id: str, event_type: str,
                    extra_before: dict | None = None,
                    extra_after: dict | None = None) -> dict:
        row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        if expected_version is not None and row["version"] != expected_version:
            raise VersionConflict(f"task version {row['version']} != expected {expected_version}")
        current = row["status"]
        if next_status != current and next_status not in LEGAL_TRANSITIONS.get(current, set()):
            raise IllegalTransition(f"{current} -> {next_status} not allowed")
        conn.execute(
            "UPDATE repair_tasks SET status=?, version=version+1, updated_at_ms=? WHERE task_id=?",
            (next_status, self.now(), task_id),
        )
        new_version = row["version"] + 1
        before = dict(row)
        if extra_before:
            before.update(extra_before)
        after = {"status": next_status, "version": new_version}
        if extra_after:
            after.update(extra_after)
        self._record_event(conn, task_id, new_version, event_type, actor_id, before, after)
        return {"task_id": task_id, "status": next_status, "version": new_version}

    def _record_event(self, conn, task_id: str, task_version: int, event_type: str,
                      actor_id: str, before: dict | None, after: dict | None) -> None:
        conn.execute(
            "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, "
            "before_state, after_state, at_ms) VALUES (?,?,?,?,?,?,?)",
            (task_id, task_version, event_type, actor_id,
             json.dumps(before, ensure_ascii=False) if before else None,
             json.dumps(after, ensure_ascii=False) if after else None,
             self.now()),
        )

    def _cancel_pending_jobs(self, conn, task_id: str) -> int:
        cur = conn.execute(
            "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
            "WHERE task_id=? AND status='PENDING'",
            (self.now(), task_id),
        )
        return cur.rowcount if cur.rowcount is not None else 0

    # ---------- 统一执行边界 ----------

    def _run(self, *, command: str, actor_id: str, idem_key: str,
             task_id: str | None, expected_version: int | None, params: dict,
             body: Callable[[Any, str | None], dict], project_id: str | None = None) -> CommandResult:
        """命令模板：幂等 → 授权 → 校验 → 写 → 回执；失败另记审计。

        `body(conn, fp)` 返回完整响应 dict；该 dict 会原样存入 result_json，
        保证重试回放能给出与首次完全一致的响应。
        """
        fp: str | None = None
        try:
            with self.db.tx() as conn:
                cur = conn.cursor()
                resolved_project = project_id
                if task_id is not None:
                    row = conn.execute(
                        "SELECT project_id FROM repair_tasks WHERE task_id=?", (task_id,)
                    ).fetchone()
                    if row is not None:
                        resolved_project = row["project_id"]
                fp = idem.fingerprint(command, actor_id, resolved_project, task_id,
                                      expected_version, params)
                replay = idem.check_replay(cur, actor_id, idem_key, fp)
                if replay is not None:
                    # 回放不得绕过当前访问权：重新做一次对象授权。
                    # 关键修复 R2-05：create_draft 的 task_id 由 body 生成，回执里存真实
                    # task_id；旧代码只在 task_id 非空时校验，导致原报修人撤权后仍能
                    # 通过回放拿到原 task + 重放结果。
                    replay_task_id = task_id or replay.get("task_id") or (replay.get("result") or {}).get("task_id")
                    if replay_task_id is not None:
                        task = self._resolve_task(conn, replay_task_id)
                        self._assert_visible(conn, task, actor_id)
                        self._check_actor_role(
                            task["project_id"], actor_id,
                            _COMMAND_ROLES.get(command, set()),
                            allow_manager=_COMMAND_MANAGER_DELEGATE.get(command, False))
                    else:
                        # 没有 task_id 的命令（如 create_draft）：用项目维度授权
                        self._check_actor_role(
                            resolved_project, actor_id,
                            _COMMAND_ROLES.get(command, set()),
                            allow_manager=_COMMAND_MANAGER_DELEGATE.get(command, False))
                    return CommandResult(ok=True, data=replay)
                data = body(conn, fp)
                # create_draft 之类任务的 task_id 由 body 生成：回执必须记真实对象，
                # 否则重放只拿到 task_id=None，不是“完整原结果”。
                receipt_task_id = task_id or data.get("task_id")
                stored = dict(data)
                stored["task_id"] = receipt_task_id
                action_id = _uuid()
                idem.record_receipt(
                    conn, actor_id, idem_key, command, resolved_project, receipt_task_id,
                    expected_version, fp, response={**stored, "action_id": action_id},
                    action_id=action_id)
                return CommandResult(ok=True, data={**stored, "action_id": action_id})
        except OctoSenseError as e:
            if fp is None:
                fp = idem.fingerprint(command, actor_id, project_id, task_id,
                                      expected_version, params)
            idem.record_failure(self.db, actor_id, idem_key, command, project_id, task_id,
                                expected_version, fp, e.code, e.detail)
            raise

    # ---------- 命令 ----------

    def create_draft(self, actor_id: str, idem_key: str, problem_text: str,
                     contact_name: str, project_id: str, preferred_window: str = "",
                     space_id: str | None = None, contact_info: str = "",
                     category: str = "OTHER") -> CommandResult:
        if not problem_text or not problem_text.strip():
            raise DraftMissingField("problem_text required")
        if not contact_name or not contact_name.strip():
            raise DraftMissingField("contact_name required")
        if not project_id:
            raise DraftMissingField("project_id required")
        if category not in auth.VALID_CATEGORIES:
            raise DraftMissingField(f"category must be one of {sorted(auth.VALID_CATEGORIES)}")

        def body(conn, fp):
            self._check_actor_role(project_id, actor_id, {"REPORTER"})
            proj = conn.execute(
                "SELECT 1 FROM repair_projects WHERE project_id=?", (project_id,)).fetchone()
            if proj is None:
                raise OctoSenseError("PROJECT_NOT_FOUND", f"project {project_id}", http_status=404)
            if space_id is not None:
                sp = conn.execute(
                    "SELECT 1 FROM repair_spaces WHERE space_id=? AND project_id=?",
                    (space_id, project_id)).fetchone()
                if sp is None:
                    raise InvalidProjectReference(
                        f"space {space_id} not in project {project_id}")
            task_id = _uuid()
            now = self.now()
            conn.execute(
                "INSERT INTO repair_tasks (task_id, project_id, reporter_id, category, status, "
                "version, problem_text, contact_name, contact_info, preferred_window, space_id, "
                "created_at_ms, updated_at_ms) VALUES (?,?,?,?,'DRAFT',1,?,?,?,?,?,?,?)",
                (task_id, project_id, actor_id, category, problem_text, contact_name,
                 contact_info, preferred_window, space_id, now, now))
            row = self._resolve_task(conn, task_id)
            self._record_event(conn, task_id, 1, "create_draft", actor_id, None, row)
            return {"task_id": task_id, "status": "DRAFT", "version": 1,
                    "project_id": project_id, "category": category}

        return self._run(command="create_draft", actor_id=actor_id, idem_key=idem_key,
                         task_id=None, expected_version=None, project_id=project_id,
                         params={"project_id": project_id, "problem_text": problem_text,
                                 "contact_name": contact_name, "contact_info": contact_info,
                                 "preferred_window": preferred_window, "space_id": space_id,
                                 "category": category},
                         body=body)

    def update_draft(self, actor_id: str, idem_key: str, task_id: str,
                     expected_version: int,
                     space_id: str | None = None,
                     contact_name: str | None = None,
                     contact_info: str | None = None,
                     preferred_window: str | None = None,
                     problem_text: str | None = None) -> CommandResult:
        """R3-01：把 DRAFT 阶段字段补齐/调整收敛到统一命令边界。

        业务约束（与原 _run 既有能力一致；写法和 `_run` 同框架）：
          - 仅允许原报修人本人；
          - 仅允许 DRAFT 状态；
          - `space_id` 必须仍在同项目且本任务已存在的设备服务关系不被破坏；
          - project_id / category 不允许修改（保持原 P0 决定）。
        """
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            # 必须在 DRAFT
            if task["status"] != "DRAFT":
                raise IllegalTransition(
                    f"update_draft requires DRAFT, got {task['status']}")
            # 仅原报修人；项目成员中仍是 REPORTER 才会到这里（_run 已经做过对象授权）。
            if task["reporter_id"] != actor_id:
                raise PermissionDenied("only original reporter can update draft")
            # 项目级授权：仍是本项目 REPORTER
            self._check_actor_role(task["project_id"], actor_id, {"REPORTER"})
            # 严格版本检查
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            # space_id 跨项目 / 不存在 → 422
            if space_id is not None:
                sp = conn.execute(
                    "SELECT 1 FROM repair_spaces WHERE space_id=? AND project_id=?",
                    (space_id, task["project_id"])).fetchone()
                if sp is None:
                    raise InvalidProjectReference(
                        f"space {space_id} not in project {task['project_id']}")
            # 计算新值；任意字段传 None → 保持旧值
            new_space_id = space_id if space_id is not None else task["space_id"]
            new_contact_name = contact_name if contact_name is not None else task["contact_name"]
            new_contact_info = contact_info if contact_info is not None else task["contact_info"]
            new_preferred = preferred_window if preferred_window is not None else task["preferred_window"]
            new_problem = problem_text if problem_text is not None else task["problem_text"]
            # 联系人非空守卫
            if not (new_contact_name or "").strip():
                raise DraftMissingField("contact_name required")
            now = self.now()
            old_version = task["version"]
            new_version = old_version + 1
            conn.execute(
                "UPDATE repair_tasks SET space_id=?, contact_name=?, contact_info=?, "
                "preferred_window=?, problem_text=?, version=?, updated_at_ms=? "
                "WHERE task_id=?",
                (new_space_id, new_contact_name, new_contact_info, new_preferred,
                 new_problem, new_version, now, task_id))
            self._record_event(
                conn, task_id, new_version, "update_draft", actor_id,
                {"space_id": task["space_id"], "contact_name": task["contact_name"],
                 "contact_info": task["contact_info"], "preferred_window": task["preferred_window"],
                 "problem_text": task["problem_text"], "version": old_version},
                {"space_id": new_space_id, "contact_name": new_contact_name,
                 "contact_info": new_contact_info, "preferred_window": new_preferred,
                 "problem_text": new_problem, "operator": actor_id,
                 "version": new_version})
            return {"task_id": task_id, "task_version": new_version,
                    "status": "DRAFT", "space_id": new_space_id,
                    "contact_name": new_contact_name,
                    "contact_info": new_contact_info,
                    "preferred_window": new_preferred,
                    "problem_text": new_problem}

        params = {"task_id": task_id, "expected_version": expected_version}
        if space_id is not None:
            params["space_id"] = space_id
        if contact_name is not None:
            params["contact_name"] = contact_name
        if contact_info is not None:
            params["contact_info"] = contact_info
        if preferred_window is not None:
            params["preferred_window"] = preferred_window
        if problem_text is not None:
            params["problem_text"] = problem_text
        return self._run(command="update_draft", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params=params, body=body)

    def confirm_draft(self, actor_id: str, idem_key: str, task_id: str,
                      expected_version: int) -> CommandResult:
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "confirm_draft")
            self._check_actor_role(task["project_id"], actor_id, {"REPORTER"})
            if task["reporter_id"] != actor_id:
                raise PermissionDenied("only original reporter can confirm this draft")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            # 提交前业务必填项：项目仍在、服务空间属于本项目、联系人已填
            proj = conn.execute(
                "SELECT 1 FROM repair_projects WHERE project_id=?", (task["project_id"],)
            ).fetchone()
            if proj is None:
                raise OctoSenseError("PROJECT_NOT_FOUND", task["project_id"], http_status=404)
            if not task.get("space_id"):
                raise SpaceRequired(
                    "confirm a service space before submitting; draft is kept as DRAFT")
            sp = conn.execute(
                "SELECT 1 FROM repair_spaces WHERE space_id=? AND project_id=?",
                (task["space_id"], task["project_id"])).fetchone()
            if sp is None:
                raise InvalidProjectReference(
                    f"space {task['space_id']} not in project {task['project_id']}")
            if not (task.get("contact_name") or "").strip():
                raise DraftMissingField("contact_name required before submitting")
            data = self._transition(conn, task_id, expected_version, "OPEN", actor_id,
                                    "confirm_draft")
            return {**data, "project_id": task["project_id"]}

        return self._run(command="confirm_draft", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version},
                         body=body)

    def accept_task(self, actor_id: str, idem_key: str, task_id: str,
                    expected_version: int) -> CommandResult:
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "accept_task")
            # V09：经理没有 TECHNICIAN 角色不得自主接单
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"},
                                   allow_manager=False)
            if not auth.skill_matches(conn, actor_id, task["project_id"], task["category"]):
                raise SkillMismatch(
                    f"technician skill does not cover category {task['category']}")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            data = self._transition(conn, task_id, expected_version, "ACCEPTED", actor_id,
                                    "accept_task")
            conn.execute("UPDATE repair_tasks SET assignee_id=? WHERE task_id=?",
                         (actor_id, task_id))
            return {**data, "assignee_id": actor_id}

        return self._run(command="accept_task", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version},
                         body=body)

    def assign_task(self, actor_id: str, idem_key: str, task_id: str, assignee_id: str,
                    expected_version: int, reason: str = "") -> CommandResult:
        idem.strict_positive_int(expected_version)
        if not reason or not reason.strip():
            raise DraftMissingField("assign reason required")
        if not assignee_id:
            raise DraftMissingField("assignee_id required")

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "assign_task")
            self._check_actor_role(task["project_id"], actor_id, {"MANAGER"})
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            # 分配对象必须是同项目、有效技能匹配的技工（V09）
            if not auth.technician_ok(conn, assignee_id, task["project_id"], task["category"]):
                raise PermissionDenied(
                    f"{assignee_id} is not a skill-matched TECHNICIAN in this project")
            data = self._transition(conn, task_id, expected_version, "ACCEPTED", actor_id,
                                    "assign_task",
                                    extra_after={"assignee_id": assignee_id, "reason": reason})
            conn.execute("UPDATE repair_tasks SET assignee_id=? WHERE task_id=?",
                         (assignee_id, task_id))
            return {**data, "assignee_id": assignee_id, "reason": reason}

        return self._run(command="assign_task", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "assignee_id": assignee_id, "reason": reason},
                         body=body)

    def propose_appointment(self, actor_id: str, idem_key: str, task_id: str,
                            start_at_ms: int, end_at_ms: int,
                            expected_version: int) -> CommandResult:
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "propose_appointment")
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"},
                                   allow_manager=True)
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            tech_id = task["assignee_id"]
            if tech_id is None:
                raise NoAssignee("task has no assignee")
            # 当前承接者可提议；经理可代提议，但事件记录操作者
            if tech_id != actor_id and "MANAGER" not in auth.roles_of(
                    conn, actor_id, task["project_id"]):
                raise PermissionDenied("only current assignee can propose appointment")
            self._validate_window(start_at_ms, end_at_ms)
            # 冲突：同技工、跨项目所有 CONFIRMED
            # 冲突检查排除本任务自身即将被替换的旧确认预约：改约本质就是把旧窗口
            # 平移，旧的 CONFIRMED 在新提议确认前仍然有效，不能反过来挡住新提议。
            overlap = conn.execute(
                "SELECT appointment_id FROM repair_appointments WHERE technician_id=? "
                "AND status='CONFIRMED' AND task_id<>? "
                "AND start_at_ms < ? AND end_at_ms > ?",
                (tech_id, task_id, end_at_ms, start_at_ms)).fetchone()
            if overlap:
                raise ConcurrentConflict(
                    f"technician {tech_id} has confirmed overlap {overlap['appointment_id']}")
            now = self.now()
            valid_until = min(now + self.appt_defaults["proposal_validity_ms"], start_at_ms)
            conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='PROPOSED'", (now, task_id))
            appt_id = _uuid()
            conn.execute(
                "INSERT INTO repair_appointments (appointment_id, task_id, technician_id, "
                "start_at_ms, end_at_ms, status, proposed_by, created_at_ms, updated_at_ms) "
                "VALUES (?,?,?,?,?,'PROPOSED',?,?,?)",
                (appt_id, task_id, tech_id, start_at_ms, end_at_ms, actor_id, now, now))
            conn.execute(
                "UPDATE repair_tasks SET version=version+1, updated_at_ms=? WHERE task_id=?",
                (now, task_id))
            new_version = task["version"] + 1
            self._record_event(conn, task_id, new_version, "propose_appointment", actor_id,
                               task, {"appointment_id": appt_id, "appt_status": "PROPOSED",
                                      "task_status": task["status"], "start_at_ms": start_at_ms,
                                      "end_at_ms": end_at_ms, "valid_until_ms": valid_until,
                                      "proposed_by": actor_id,
                                      "technician_id": tech_id})
            return {"task_id": task_id, "status": task["status"], "version": new_version,
                    "appointment_id": appt_id, "appointment_status": "PROPOSED",
                    "start_at_ms": start_at_ms, "end_at_ms": end_at_ms,
                    "valid_until_ms": valid_until, "technician_id": tech_id,
                    "proposed_by": actor_id}

        return self._run(command="propose_appointment", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "start_at_ms": start_at_ms, "end_at_ms": end_at_ms},
                         body=body)

    def _validate_window(self, start_at_ms: int, end_at_ms: int) -> None:
        d = self.appt_defaults
        now = self.now()
        if not isinstance(start_at_ms, int) or not isinstance(end_at_ms, int):
            raise DraftMissingField("start_at_ms/end_at_ms must be integers")
        if end_at_ms <= start_at_ms:
            raise DraftMissingField("end_at_ms must be > start_at_ms")
        duration = end_at_ms - start_at_ms
        if duration < d["min_duration_ms"] or duration > d["max_duration_ms"]:
            raise AppointmentWindowInvalid(
                f"duration {duration}ms outside "
                f"[{d['min_duration_ms']}, {d['max_duration_ms']}]")
        if start_at_ms <= now:
            raise AppointmentWindowInvalid(
                "start_at_ms must be in the future relative to the server clock")
        if start_at_ms > now + d["max_lead_ms"]:
            raise AppointmentWindowInvalid(
                f"start_at_ms later than the {d['max_lead_ms'] // 86400000}-day lead limit")

    def start_progress(self, actor_id: str, idem_key: str, task_id: str,
                       expected_version: int) -> CommandResult:
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "start_progress")
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            if task["assignee_id"] != actor_id:
                raise PermissionDenied("only current assignee can start progress")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            if not task["asset_id"]:
                raise IllegalTransition(
                    "no asset bound; cannot start_progress before bind_asset")
            appt = conn.execute(
                "SELECT appointment_id, start_at_ms, end_at_ms, technician_id "
                "FROM repair_appointments WHERE task_id=? AND status='CONFIRMED' LIMIT 1",
                (task_id,)).fetchone()
            if appt is None:
                raise IllegalTransition(
                    "no CONFIRMED appointment; cannot start_progress before reporter confirms")
            if appt["technician_id"] != actor_id:
                raise PermissionDenied("confirmed appointment belongs to another technician")
            now = self.now()
            if not (appt["start_at_ms"] <= now < appt["end_at_ms"]):
                raise IllegalTransition(
                    f"current time {now} outside CONFIRMED window "
                    f"[{appt['start_at_ms']}, {appt['end_at_ms']})")
            # 开工使本任务未确认提议失效，防止迟到确认改变已开工任务。
            # R2-06 修复：原 SQL 用 `task_id<>?` 把同技工其他任务的 PROPOSED 误作废；
            # 正确语义是仅作废本任务的未确认 PROPOSED，其他任务的冲突由预约冲突规则处理。
            conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='PROPOSED'",
                (now, task_id))
            # R3-06：进入 IN_PROGRESS 后，所有 APPOINTMENT_UPCOMING/UPCOMING_REPORTER/OVERDUE
            # 类作业立即作废；再开工一次也不能重复失效。
            self._cancel_pending_jobs(conn, task_id)
            data = self._transition(conn, task_id, expected_version, "IN_PROGRESS", actor_id,
                                    "start_progress",
                                    extra_after={"appointment_id": appt["appointment_id"]})
            return data

        return self._run(command="start_progress", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version},
                         body=body)

    def submit_completion(self, actor_id: str, idem_key: str, task_id: str,
                          completion_text: str, expected_version: int,
                          disposition: str = "REPAIRED") -> CommandResult:
        idem.strict_positive_int(expected_version)
        if not completion_text or not completion_text.strip():
            raise DraftMissingField("completion_text required")
        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "submit_completion")
            self._check_actor_role(task["project_id"], actor_id, {"TECHNICIAN"})
            # R2-05：再次确认 actor 仍是当前承接者（即使角色在 say 路径里查过，
            # 这里对回放路径同样成立；_run 已在 body 之前做一次对象授权）。
            if task["assignee_id"] != actor_id:
                raise PermissionDenied("only current assignee can submit completion")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            # V08：不仅检查 READY 行，还验证附件实际存在且完整
            rows = conn.execute(
                "SELECT evidence_id, sha256, byte_size, storage_path FROM repair_evidence "
                "WHERE task_id=? AND status='READY'", (task_id,)).fetchall()
            if not rows:
                raise DraftMissingField(
                    "completion requires at least one READY evidence; upload one first")
            import hashlib
            from pathlib import Path
            bad: list[str] = []
            for r in rows:
                path = Path(r["storage_path"])
                if not path.exists():
                    bad.append(f"{r['evidence_id']}:missing")
                    continue
                payload = path.read_bytes()
                if len(payload) != r["byte_size"]:
                    bad.append(f"{r['evidence_id']}:size")
                    continue
                if hashlib.sha256(payload).hexdigest() != r["sha256"]:
                    bad.append(f"{r['evidence_id']}:sha256")
            if bad:
                raise EvidenceIntegrity(
                    "evidence not readable or incomplete: " + ", ".join(bad) +
                    "; re-upload via POST /tasks/{id}/evidence before completing")
            evidence_ids = [r["evidence_id"] for r in rows]
            last = conn.execute(
                "SELECT MAX(round) AS r FROM repair_completions WHERE task_id=?",
                (task_id,)).fetchone()
            new_round = (last["r"] or 0) + 1
            completion_id = _uuid()
            conn.execute(
                "INSERT INTO repair_completions (completion_id, task_id, round, submitter_id, "
                "completion_text, disposition, evidence_ids, created_at_ms) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (completion_id, task_id, new_round, actor_id, completion_text, disposition,
                 json.dumps(evidence_ids, ensure_ascii=False), self.now()))
            data = self._transition(conn, task_id, expected_version, "AWAITING_ACCEPTANCE",
                                    actor_id, "submit_completion",
                                    extra_after={"completion_id": completion_id,
                                                 "round": new_round,
                                                 "completion_text": completion_text,
                                                 "disposition": disposition,
                                                 "evidence_ids": evidence_ids})
            schedule_acceptance_reminder(self.db, task_id, task["reporter_id"],
                                         round_number=new_round,
                                         clock=self._clock)
            return {**data, "completion_text": completion_text,
                    "completion_id": completion_id, "round": new_round,
                    "evidence_ids": evidence_ids}

        return self._run(command="submit_completion", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "completion_text": completion_text,
                                 "disposition": disposition},
                         body=body)

    def accept_completion(self, actor_id: str, idem_key: str, task_id: str,
                          expected_version: int, reason: str = "") -> CommandResult:
        idem.strict_positive_int(expected_version)

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "accept_completion")
            # R3-02：第一次写必须先验证主体仍是当前项目成员
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            if not roles:
                raise PermissionDenied(f"actor not in project {task['project_id']}")
            is_reporter = (actor_id == task["reporter_id"]) and ("REPORTER" in roles)
            is_manager = ("MANAGER" in roles)
            if not (is_reporter or is_manager):
                raise PermissionDenied(
                    "only original reporter or project manager can accept completion")
            # 当前承接者（含多角色）不能自验
            if task["assignee_id"] == actor_id:
                raise PermissionDenied("assignee cannot accept own completion")
            if is_manager and not is_reporter and not (reason or "").strip():
                raise DraftMissingField("manager-accept reason required")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            last = conn.execute(
                "SELECT round, completion_id FROM repair_completions WHERE task_id=? "
                "ORDER BY round DESC LIMIT 1", (task_id,)).fetchone()
            data = self._transition(conn, task_id, expected_version, "COMPLETED", actor_id,
                                    "accept_completion",
                                    extra_after={"reason": reason,
                                                 "accepted_round": last["round"] if last else None,
                                                 "completion_id": last["completion_id"] if last else None})
            # R2-07：COMPLETED 后任何剩余 PENDING 提醒（ACCEPTANCE_DUE/UPCOMING/...）作废，
            # 已创建的历史通知保留；不再产生新通知。
            self._cancel_pending_jobs(conn, task_id)
            return {**data, "reason": reason,
                    "accepted_round": last["round"] if last else None}

        return self._run(command="accept_completion", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "reason": reason},
                         body=body)

    def reject_completion(self, actor_id: str, idem_key: str, task_id: str,
                          expected_version: int, reason: str) -> CommandResult:
        idem.strict_positive_int(expected_version)
        if not reason or not reason.strip():
            raise DraftMissingField("reject reason required")

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "reject_completion")
            # R3-02：第一次写必须先验证主体仍是当前项目成员
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            if not roles:
                raise PermissionDenied(f"actor not in project {task['project_id']}")
            is_reporter = (actor_id == task["reporter_id"]) and ("REPORTER" in roles)
            is_manager = ("MANAGER" in roles)
            if not (is_reporter or is_manager):
                raise PermissionDenied(
                    "only original reporter or project manager can reject completion")
            if task["assignee_id"] == actor_id:
                raise PermissionDenied("rejector cannot be the assignee")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            last = conn.execute(
                "SELECT round, completion_id FROM repair_completions WHERE task_id=? "
                "ORDER BY round DESC LIMIT 1", (task_id,)).fetchone()
            data = self._transition(conn, task_id, expected_version, "IN_PROGRESS", actor_id,
                                    "reject_completion",
                                    extra_after={"reason": reason,
                                                 "rejected_round": last["round"] if last else None,
                                                 "completion_id": last["completion_id"] if last else None})
            # R2-07：退回 IN_PROGRESS 时取消当前轮次的 ACCEPTANCE_DUE 等提醒；
            # 新的 ACCEPTANCE_DUE 由后续 submit_completion 按新 round 注册。
            self._cancel_pending_jobs(conn, task_id)
            return {**data, "reason": reason,
                    "rejected_round": last["round"] if last else None}

        return self._run(command="reject_completion", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "reason": reason},
                         body=body)

    def cancel(self, actor_id: str, idem_key: str, task_id: str,
               expected_version: int, reason: str) -> CommandResult:
        idem.strict_positive_int(expected_version)
        if not reason or not reason.strip():
            raise DraftMissingField("cancel reason required")

        def body(conn, fp):
            task = self._resolve_task(conn, task_id)
            self._check_source(task, "cancel")
            # R3-02：第一次写必须先验证主体仍是当前项目成员
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            if not roles:
                raise PermissionDenied(f"actor not in project {task['project_id']}")
            is_reporter = (actor_id == task["reporter_id"]) and ("REPORTER" in roles)
            is_manager = ("MANAGER" in roles)
            if is_reporter and task["status"] in {"DRAFT", "OPEN"}:
                pass
            elif is_manager:
                pass
            else:
                raise PermissionDenied(
                    "reporter can only cancel own DRAFT/OPEN; manager required for other states")
            if expected_version != task["version"]:
                raise VersionConflict(f"task version {task['version']} != expected {expected_version}")
            data = self._transition(conn, task_id, expected_version, "CANCELLED", actor_id,
                                    "cancel", extra_after={"reason": reason})
            released = conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status IN ('PROPOSED','CONFIRMED')",
                (self.now(), task_id)).rowcount
            jobs = self._cancel_pending_jobs(conn, task_id)
            return {**data, "reason": reason,
                    "released_appointments": released, "cancelled_jobs": jobs}

        return self._run(command="cancel", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "reason": reason},
                         body=body)


# 命令 → 回放时需要的角色集合（回放不得绕过授权）
_COMMAND_ROLES: dict[str, set[str]] = {
    "create_draft": {"REPORTER"},
    "update_draft": {"REPORTER"},
    "confirm_draft": {"REPORTER"},
    "accept_task": {"TECHNICIAN"},
    "assign_task": {"MANAGER"},
    "propose_appointment": {"TECHNICIAN"},
    "confirm_appointment": {"REPORTER"},
    "reject_appointment": {"REPORTER"},
    "reassign": {"MANAGER"},
    "start_progress": {"TECHNICIAN"},
    "record_progress": {"TECHNICIAN"},
    "submit_completion": {"TECHNICIAN"},
    "accept_completion": {"REPORTER", "MANAGER"},
    "reject_completion": {"REPORTER", "MANAGER"},
    "cancel": {"REPORTER", "MANAGER"},
    "bind_asset": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "unbind_asset": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "upload_evidence": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "list_evidence": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "download_evidence": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "quarantine_evidence": {"REPORTER", "MANAGER"},
    "add_pin": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "remove_pin": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "list_pins": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "match_assets_by_code": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "get_asset_detail": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "get_history_advice": {"REPORTER", "TECHNICIAN", "MANAGER"},
    "record_advice": {"REPORTER", "TECHNICIAN", "MANAGER"},
}

# 是否允许 MANAGER 在非本人主要角色时代行（回放授权用）
_COMMAND_MANAGER_DELEGATE: dict[str, bool] = {
    "create_draft": True,
    "update_draft": False,
    "confirm_draft": False,
    "accept_task": False,
    "assign_task": True,
    "propose_appointment": True,
    "start_progress": False,
    "submit_completion": False,
    "accept_completion": True,
    "reject_completion": True,
    "cancel": True,
}
