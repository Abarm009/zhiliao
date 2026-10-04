"""附加命令：confirm_appointment / reject_appointment / reassign。

修复 V06：
  - 确认时只排除**同一任务**即将被替换的旧 CONFIRMED 预约；本任务的旧预约不再
    参与冲突检查，其他任务（含同技工跨项目）的重叠仍会被拒。
  - 提议有有效期 `min(24h, 开始时间 - 现在)`；过期确认返回 410
    （APPOINTMENT_EXPIRED），不使用客户端时间。
  - 改派在事务内释放旧技工的 PROPOSED/CONFIRMED 预约并取消到期提醒作业。

所有写操作走 `CommandExecutor` 的统一幂等边界（命令级指纹 + 原结果回放）。
"""

from __future__ import annotations

import json
from typing import Any, Callable

from octosense_backend import authorization as auth
from octosense_backend import idempotency as idem
from octosense_backend.commands import CommandExecutor
from octosense_backend.db import Database
from octosense_backend.jobs import schedule_appointment_reminders
from octosense_backend.errors import (
    AppointmentExpired,
    DraftMissingField,
    IllegalTransition,
    OctoSenseError,
    PermissionDenied,
    TaskNotFound,
    VersionConflict,
)


class AppointmentCommands:
    def __init__(self, db: Database, executor: CommandExecutor | None = None,
                 clock: Callable[[], int] | None = None):
        self.db = db
        self.executor = executor or CommandExecutor(db, clock=clock)
        if clock is not None:
            self.executor._clock = clock

    # ---- 复用 CommandExecutor 的执行边界 ----

    def _run(self, *, command: str, actor_id: str, idem_key: str, task_id: str,
             expected_version: int, params: dict, body: Callable[[Any, str | None], dict]):
        return self.executor._run(command=command, actor_id=actor_id, idem_key=idem_key,
                                  task_id=task_id, expected_version=expected_version,
                                  params=params, body=body)

    def _resolve(self, conn, task_id: str) -> dict:
        row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        return dict(row)

    # ---- confirm ----

    def confirm_appointment(self, actor_id: str, idem_key: str, task_id: str,
                            expected_version: int, appointment_id: str | None = None) -> dict:
        """原报修人确认当前 PROPOSED 预约为 CONFIRMED；任务 ACCEPTED→SCHEDULED。"""

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            # 服务端对象授权：只有能看见该任务、且是原报修人的主体可以确认
            self.executor._assert_visible(conn, task, actor_id)
            if actor_id != task["reporter_id"]:
                raise PermissionDenied("only original reporter can confirm appointment")
            if task["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(
                    f"cannot confirm appointment from task status {task['status']}")
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            if appointment_id:
                appt = conn.execute(
                    "SELECT * FROM repair_appointments WHERE appointment_id=? AND task_id=?",
                    (appointment_id, task_id)).fetchone()
            else:
                appt = conn.execute(
                    "SELECT * FROM repair_appointments WHERE task_id=? AND status='PROPOSED' "
                    "ORDER BY created_at_ms DESC LIMIT 1", (task_id,)).fetchone()
            if appt is None:
                raise IllegalTransition("no PROPOSED appointment to confirm")
            if appt["status"] != "PROPOSED":
                raise IllegalTransition(
                    f"appointment {appt['appointment_id']} is {appt['status']}, not PROPOSED")
            tech_id = appt["technician_id"]
            start, end = appt["start_at_ms"], appt["end_at_ms"]
            now = self.executor.now()
            # 提议有效期：min(提出后 24h, 预约开始时间)
            validity = min(self.executor.appt_defaults["proposal_validity_ms"],
                           max(0, start - appt["created_at_ms"]))
            valid_until = appt["created_at_ms"] + validity
            if now > valid_until:
                raise AppointmentExpired(
                    f"proposal {appt['appointment_id']} expired at {valid_until}; "
                    "ask the technician to propose a new slot")
            if now >= end:
                raise AppointmentExpired(
                    f"proposal window already ended at {end}")
            # 冲突检查：只排除本任务即将被替换的旧确认预约
            overlap = conn.execute(
                "SELECT appointment_id FROM repair_appointments "
                "WHERE technician_id=? AND status='CONFIRMED' AND task_id<>? "
                "AND start_at_ms < ? AND end_at_ms > ?",
                (tech_id, task_id, end, start)).fetchone()
            if overlap:
                raise OctoSenseError(
                    "CONCURRENT_CONFLICT",
                    f"technician {tech_id} has a conflicting confirmed appointment "
                    f"in another task {overlap['appointment_id']}", http_status=409)
            conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='CONFIRMED'", (now, task_id))
            conn.execute(
                "UPDATE repair_appointments SET status='CONFIRMED', confirmed_by=?, "
                "updated_at_ms=? WHERE appointment_id=?",
                (actor_id, now, appt["appointment_id"]))
            target_status = "SCHEDULED" if task["status"] == "ACCEPTED" else task["status"]
            self.executor._transition(
                conn, task_id, expected_version, target_status, actor_id,
                "confirm_appointment",
                extra_after={"appointment_id": appt["appointment_id"],
                             "appointment_status": "CONFIRMED",
                             "start_at_ms": start, "end_at_ms": end,
                             "technician_id": tech_id, "confirmed_by": actor_id})
            schedule_appointment_reminders(
                self.db, task_id, appt["appointment_id"], tech_id, actor_id, start, end,
                clock=lambda: self.executor.now())
            return {"task_id": task_id, "appointment_id": appt["appointment_id"],
                    "status": "CONFIRMED", "task_status": target_status,
                    "task_version": task["version"] + 1,
                    "start_at_ms": start, "end_at_ms": end, "technician_id": tech_id,
                    "confirmed_by": actor_id}

        res = self._run(command="confirm_appointment", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "expected_version": expected_version,
                                "appointment_id": appointment_id or ""},
                        body=body)
        return res.data

    # ---- reject ----

    def reject_appointment(self, actor_id: str, idem_key: str, task_id: str,
                           expected_version: int, reason: str) -> dict:
        """原报修人拒绝当前 PROPOSED；有旧 CONFIRMED 保持 SCHEDULED，否则回 ACCEPTED。"""
        if not reason or not reason.strip():
            raise DraftMissingField("reject reason required")

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            if actor_id != task["reporter_id"]:
                raise PermissionDenied("only original reporter can reject appointment")
            if task["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(
                    f"cannot reject appointment from task status {task['status']}")
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            proposed = conn.execute(
                "SELECT appointment_id FROM repair_appointments "
                "WHERE task_id=? AND status='PROPOSED'", (task_id,)).fetchall()
            if not proposed:
                raise IllegalTransition("no PROPOSED appointment to reject")
            conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status='PROPOSED'", (self.executor.now(), task_id))
            old_confirmed = conn.execute(
                "SELECT 1 FROM repair_appointments WHERE task_id=? AND status='CONFIRMED' "
                "LIMIT 1", (task_id,)).fetchone()
            target_status = "SCHEDULED" if old_confirmed else "ACCEPTED"
            self.executor._transition(
                conn, task_id, expected_version, target_status, actor_id, "reject_appointment",
                extra_after={"reason": reason, "kept_confirmed": bool(old_confirmed)})
            return {"task_id": task_id, "status": target_status,
                    "task_version": task["version"] + 1, "reason": reason,
                    "kept_confirmed": bool(old_confirmed)}

        res = self._run(command="reject_appointment", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "expected_version": expected_version,
                                "reason": reason},
                        body=body)
        return res.data

    # ---- reassign ----

    def reassign(self, actor_id: str, idem_key: str, task_id: str,
                 new_assignee_id: str, expected_version: int, reason: str) -> dict:
        """经理改派 ACCEPTED/SCHEDULED 未开工任务；释放旧预约并取消提醒作业。"""
        if not reason or not reason.strip():
            raise DraftMissingField("reassign reason required")
        if not new_assignee_id:
            raise DraftMissingField("new_assignee_id required")

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            if task["status"] not in {"ACCEPTED", "SCHEDULED"}:
                raise IllegalTransition(f"cannot reassign from {task['status']}")
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            if "MANAGER" not in roles:
                raise PermissionDenied("only project manager can reassign")
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            if not auth.technician_ok(conn, new_assignee_id, task["project_id"],
                                      task["category"]):
                raise PermissionDenied(
                    f"{new_assignee_id} is not a skill-matched TECHNICIAN in this project")
            released = conn.execute(
                "UPDATE repair_appointments SET status='SUPERSEDED', updated_at_ms=? "
                "WHERE task_id=? AND status IN ('CONFIRMED','PROPOSED')",
                (self.executor.now(), task_id)).rowcount
            jobs = self.executor._cancel_pending_jobs(conn, task_id)
            self.executor._transition(
                conn, task_id, expected_version, "ACCEPTED", actor_id, "reassign",
                extra_after={"assignee_id": new_assignee_id, "reason": reason})
            conn.execute("UPDATE repair_tasks SET assignee_id=? WHERE task_id=?",
                         (new_assignee_id, task_id))
            return {"task_id": task_id, "assignee_id": new_assignee_id,
                    "status": "ACCEPTED", "task_version": task["version"] + 1,
                    "reason": reason, "released_appointments": released,
                    "cancelled_jobs": jobs}

        res = self._run(command="reassign", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "expected_version": expected_version,
                                "new_assignee_id": new_assignee_id, "reason": reason},
                        body=body)
        return res.data
