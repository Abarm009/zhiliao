"""持久化提醒作业（T13 / T23）。

规则：
  - 作业落 `repair_jobs`（PENDING/DONE/CANCELLED），去重键唯一，重启后可恢复。
  - 只生成站内通知 + 事件，**不**自动验收、不自动开工、不自动完工。
  - 改约 / 取消 / 验收 / 退回会取消相关 PENDING 作业，旧作业不会误触发。
  - 时间一律取自可注入的服务端时钟；客户端时间不可信。
  - R2-07：执行器发送前再校验任务、预约和完成轮次；与终止/退回合规时才发，
    否则直接 CANCELLED。
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Callable

from octosense_backend.db import Database
from octosense_backend.errors import OctoSenseError


# 作业类型 → 触发该提醒时任务**必须**所处的状态。任务不满足时，run_due_jobs 会取消。
# R3-06：开始前的提醒只能在 SCHEDULED 阶段发送；进入 IN_PROGRESS/AWAITING/COMPLETED/CANCELLED
# 后任何"即将开始"类提醒必须失效（哪怕 fire_at_ms 已经过期）。
JOB_REQUIRED_STATES: dict[str, set[str]] = {
    "APPOINTMENT_UPCOMING": {"SCHEDULED"},
    "APPOINTMENT_UPCOMING_REPORTER": {"SCHEDULED"},
    "APPOINTMENT_OVERDUE": {"SCHEDULED"},   # 一旦进入 IN_PROGRESS/ACCEPTED 等就不该再催
    "ACCEPTANCE_DUE": {"AWAITING_ACCEPTANCE"},  # 已 COMPLETED 或退回 IN_PROGRESS 必须取消
}


def _uuid() -> str:
    return uuid.uuid4().hex


def _now(clock: Callable[[], int] | None) -> int:
    return int(clock() if clock else time.time() * 1000)


def schedule_appointment_reminders(db: Database, task_id: str, appointment_id: str,
                                   technician_id: str, reporter_id: str,
                                   start_at_ms: int, end_at_ms: int,
                                   clock: Callable[[], int] | None = None) -> dict:
    """为一次 CONFIRMED 预约登记三条提醒：技术开始前 / 报修人开始前 / 超时未开工。

    R2-07：改约时也要取消本任务的 APPOINTMENT_UPCOMING_REPORTER；旧代码漏了这一类，
    导致旧时间仍向报修人发提醒。
    """
    now = _now(clock)
    jobs = []
    with db.tx() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
            "WHERE task_id=? AND status='PENDING' AND kind IN "
            "('APPOINTMENT_UPCOMING','APPOINTMENT_UPCOMING_REPORTER',"
            "'APPOINTMENT_OVERDUE')", (now, task_id))
        rows = [
            ("APPOINTMENT_UPCOMING", start_at_ms - 60 * 60 * 1000, technician_id,
             {"user_id": technician_id,
              "body": f"预约将于 1 小时后开始（task {task_id}）"}),
            ("APPOINTMENT_UPCOMING_REPORTER", start_at_ms - 60 * 60 * 1000, reporter_id,
             {"user_id": reporter_id,
              "body": f"你的报修预约将于 1 小时后开始（task {task_id}）"}),
            ("APPOINTMENT_OVERDUE", end_at_ms + 5 * 60 * 1000, reporter_id,
             {"user_id": reporter_id,
              "body": f"预约已超时，需要重新预约（task {task_id}）"}),
        ]
        for kind, fire_at, _user_unused, payload in rows:
            if fire_at <= now:
                continue
            user_id = payload["user_id"]
            body = payload["body"]
            job_id = _uuid()
            dedupe = f"{kind}:{appointment_id}:{user_id}"
            try:
                cur.execute(
                    "INSERT INTO repair_jobs (job_id, kind, task_id, appointment_id, "
                    "fire_at_ms, status, payload, dedupe_key, created_at_ms, updated_at_ms) "
                    "VALUES (?,?,?,?,?,'PENDING',?,?,?,?)",
                    (job_id, kind, task_id, appointment_id, fire_at,
                     json.dumps(payload, ensure_ascii=False),
                     dedupe, now, now))
                jobs.append({"job_id": job_id, "kind": kind, "fire_at_ms": fire_at})
            except OctoSenseError:
                raise
            except Exception:
                # 去重键冲突：同一次预约重复登记视为已登记
                pass
    return {"scheduled": jobs}


def schedule_acceptance_reminder(db: Database, task_id: str, reporter_id: str,
                                 round_number: int = 1,
                                 clock: Callable[[], int] | None = None) -> dict:
    """验收超时只提醒，不自动验收。

    R2-07：dedupe_key 含 round 序号；同一 task+reporter 不同 round 可独立登记。
    登记前先取消本任务之前 PENDING 的 ACCEPTANCE_DUE（避免上一轮已注册但未触发的提醒
    在退回/新一轮提交后误触发旧重复的提醒）。
    """
    now = _now(clock)
    with db.tx() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
            "WHERE task_id=? AND status='PENDING' AND kind='ACCEPTANCE_DUE'",
            (now, task_id))
        job_id = _uuid()
        dedupe = f"ACCEPTANCE_DUE:{task_id}:{reporter_id}:{round_number}"
        try:
            cur.execute(
                "INSERT INTO repair_jobs (job_id, kind, task_id, fire_at_ms, status, payload, "
                "dedupe_key, created_at_ms, updated_at_ms) VALUES (?,?,?,?,'PENDING',?,?,?,?)",
                (job_id, "ACCEPTANCE_DUE", task_id, now + 24 * 3600 * 1000,
                 json.dumps({"user_id": reporter_id, "round": round_number,
                             "body": f"待你验收的维修已提交完工（task {task_id}，第 {round_number} 轮）"},
                            ensure_ascii=False), dedupe, now, now))
            return {"scheduled": [{"job_id": job_id, "kind": "ACCEPTANCE_DUE", "round": round_number}]}
        except Exception:
            return {"scheduled": []}


def run_due_jobs(db: Database, clock: Callable[[], int] | None = None) -> int:
    """执行到期的 PENDING 作业：写站内通知 + 事件；同一去重键只执行一次。

    R2-07：发送前按任务当前阶段校验；处于不可触发阶段的作业直接 CANCELLED。
    R3-06：补一层校验——开始前/超时类提醒必须存在有效 CONFIRMED 预约，
           验收提醒必须存在当前 round 的 completion；否则作业取消。
    R3-07：执行前还要验证接收者当前仍是该项目成员且对该任务有可见权；
           否则该作业取消，不写通知。
    """
    from octosense_backend import authorization as _auth
    now = _now(clock)
    fired = 0
    with db.tx() as conn:
        cur = conn.cursor()
        due = cur.execute(
            "SELECT * FROM repair_jobs WHERE status='PENDING' AND fire_at_ms<=? "
            "ORDER BY fire_at_ms LIMIT 200", (now,)).fetchall()
        # 一次性拉取本批任务状态以避免 N+1 查询
        task_ids = {job["task_id"] for job in due if job["task_id"]}
        task_status: dict[str, str] = {}
        task_rows: dict[str, dict] = {}
        if task_ids:
            qmarks = ",".join("?" * len(task_ids))
            for r in cur.execute(
                    f"SELECT task_id, status, project_id, reporter_id, assignee_id, "
                    f"category FROM repair_tasks WHERE task_id IN ({qmarks})",
                    tuple(sorted(task_ids))):
                task_status[r["task_id"]] = r["status"]
                task_rows[r["task_id"]] = dict(r)
        for job in due:
            try:
                payload = json.loads(job["payload"] or "{}")
            except (TypeError, ValueError):
                payload = {}
            user_id = payload.get("user_id")
            if not user_id:
                cur.execute(
                    "UPDATE repair_jobs SET status='DONE', updated_at_ms=? WHERE job_id=?",
                    (now, job["job_id"]))
                continue
            tid = job["task_id"]
            current_status = task_status.get(tid) if tid else None
            task_row = task_rows.get(tid) if tid else None
            # R2-07：阶段不满足时取消
            required = JOB_REQUIRED_STATES.get(job["kind"])
            if required is not None and (current_status is None or current_status not in required):
                cur.execute(
                    "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                    "WHERE job_id=?", (now, job["job_id"]))
                continue
            # R3-06：开始前提醒必须存在有效 CONFIRMED 预约，且时刻仍在窗口前
            if job["kind"] in ("APPOINTMENT_UPCOMING", "APPOINTMENT_UPCOMING_REPORTER",
                                "APPOINTMENT_OVERDUE"):
                job_appt_id = job["appointment_id"]
                appt = None
                if job_appt_id:
                    appt = cur.execute(
                        "SELECT appointment_id, status, start_at_ms, end_at_ms "
                        "FROM repair_appointments WHERE appointment_id=?",
                        (job_appt_id,)).fetchone()
                if appt is None or appt["status"] != "CONFIRMED":
                    cur.execute(
                        "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                        "WHERE job_id=?", (now, job["job_id"]))
                    continue
                if job["kind"] in ("APPOINTMENT_UPCOMING", "APPOINTMENT_UPCOMING_REPORTER"):
                    if now >= appt["start_at_ms"]:
                        cur.execute(
                            "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                            "WHERE job_id=?", (now, job["job_id"]))
                        continue
            # R3-06：验收提醒必须存在当前 round 的 completion
            if job["kind"] == "ACCEPTANCE_DUE":
                target_round = payload.get("round")
                if target_round is None:
                    cur.execute(
                        "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                        "WHERE job_id=?", (now, job["job_id"]))
                    continue
                comp = cur.execute(
                    "SELECT round FROM repair_completions WHERE task_id=? AND round=?",
                    (tid, target_round)).fetchone()
                if comp is None:
                    cur.execute(
                        "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                        "WHERE job_id=?", (now, job["job_id"]))
                    continue
            # R3-07：验证接收者当前仍是该项目成员且对该任务有可见权
            if task_row is not None:
                roles = _auth.roles_of(cur, user_id, task_row["project_id"])
                if not roles:
                    cur.execute(
                        "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                        "WHERE job_id=?", (now, job["job_id"]))
                    continue
                if not _auth.task_visible(cur, user_id, task_row):
                    cur.execute(
                        "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
                        "WHERE job_id=?", (now, job["job_id"]))
                    continue
            body = payload.get("body") or f"{job['kind']} for task {job['task_id']}"
            cur.execute(
                "INSERT INTO repair_notifications (notification_id, user_id, task_id, kind, "
                "body, created_at_ms) VALUES (?,?,?,?,?,?)",
                (_uuid(), user_id, job["task_id"], job["kind"], body, now))
            if job["task_id"]:
                cur.execute(
                    "INSERT INTO repair_events (task_id, task_version, event_type, actor_id, "
                    "after_state, at_ms) VALUES (?,?,?,?,?,?)",
                    (job["task_id"], 0, "job_reminder", user_id,
                     json.dumps({"kind": job["kind"], "body": body,
                                 "round": payload.get("round")},
                                ensure_ascii=False), now))
            cur.execute(
                "UPDATE repair_jobs SET status='DONE', updated_at_ms=? WHERE job_id=?",
                (now, job["job_id"]))
            fired += 1
    return fired


def cancel_task_jobs(db: Database, task_id: str, clock: Callable[[], int] | None = None) -> int:
    now = _now(clock)
    with db.tx() as conn:
        cur = conn.execute(
            "UPDATE repair_jobs SET status='CANCELLED', updated_at_ms=? "
            "WHERE task_id=? AND status='PENDING'", (now, task_id))
        return cur.rowcount or 0
