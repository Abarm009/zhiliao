"""T06 / T12 收尾：改派与拒绝改约的对象授权与事实保留。

与 test_appointments.py 的分工：本文件专注“授权拒绝”和“旧事实保留”两条分支，
不重复 happy path。
"""
from __future__ import annotations

import pytest

from octosense_backend.errors import (
    DraftMissingField,
    IllegalTransition,
    OctoSenseError,
    PermissionDenied,
)

from world import (
    AS_AC, HVAC, MGR, PA, PB, R1, R2, T1, T2, World, ok, okd, task_row,
)

DAY = 24 * 3600 * 1000


def _add_hvac_tech(db, uid="u-tech-7", project=PA):
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
                 "VALUES (?,?,1)", (uid, f"技工 {uid}（HVAC）"))
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                 "VALUES (?,?, 'TECHNICIAN', 'HVAC')", (project, uid))
    conn.close()
    return uid


def test_confirm_rejects_unknown_actor(executor, appt_cmds, db, clock, ext):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    with pytest.raises(OctoSenseError):
        appt_cmds.confirm_appointment(actor_id="u-ghost", idem_key="k-ghost", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_confirm_only_reporter_no_manager_substitute(executor, appt_cmds, db, clock, ext):
    """Q04：P0 经理不代确认预约。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    with pytest.raises(PermissionDenied):
        appt_cmds.confirm_appointment(actor_id=MGR, idem_key="k-mgr", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_reject_appointment_keeps_old_confirmed(executor, appt_cmds, db, clock, ext):
    """N06：有旧 CONFIRMED 时拒绝新提议，任务保持 SCHEDULED，旧预约仍可开工。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    start = appt["start_at_ms"]
    moved = w.propose(tid=tid, start=start + DAY, key="k-move")
    data = w.reject_proposal(tid=tid, reason="改到第二天不方便", key="k-rej")
    assert data["kept_confirmed"] is True
    assert task_row(db, tid)["status"] == "SCHEDULED"
    conn = db.conn()
    by_id = {r["appointment_id"]: r["status"] for r in conn.execute(
        "SELECT appointment_id, status FROM repair_appointments WHERE task_id=?",
        (tid,)).fetchall()}
    conn.close()
    assert by_id[appt["appointment_id"]] == "CONFIRMED"
    assert by_id[moved["appointment_id"]] == "SUPERSEDED"
    clock.set(start + 60000)
    w.start(tid=tid, at=start + 60000)
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_reject_appointment_when_no_proposed_rejected(executor, appt_cmds, db, clock, ext):
    """Q05：无 PROPOSED 不得 reject；不得产生虚假成功回执。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(IllegalTransition):
        appt_cmds.reject_appointment(actor_id=R1, idem_key="k-no-proposed", task_id=tid,
                                     expected_version=task_row(db, tid)["version"],
                                     reason="不要了")
    assert task_row(db, tid)["status"] == "ACCEPTED"
    conn = db.conn()
    n = conn.execute("SELECT COUNT(*) AS n FROM repair_actions WHERE idempotency_key=?",
                     ("k-no-proposed",)).fetchone()["n"]
    conn.close()
    assert n == 0, "失败的拒绝不得留下 OK 回执"


def test_reassign_scheduled_releases_appointment(executor, appt_cmds, db, clock, ext):
    """T06：改派 SCHEDULED 任务：旧确认 SUPERSEDED、任务回 ACCEPTED、旧技工失效。"""
    new_tech = _add_hvac_tech(db)
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    v = task_row(db, tid)["version"]
    data = okd(appt_cmds.reassign(actor_id=MGR, idem_key="k-reassign", task_id=tid,
                                  new_assignee_id=new_tech, expected_version=v,
                                  reason="技工甲请假"), "reassign")
    assert data["assignee_id"] == new_tech
    assert data["released_appointments"] >= 1
    row = task_row(db, tid)
    assert row["status"] == "ACCEPTED" and row["assignee_id"] == new_tech
    conn = db.conn()
    ap = conn.execute("SELECT status FROM repair_appointments WHERE appointment_id=?",
                      (appt["appointment_id"],)).fetchone()
    jobs = conn.execute(
        "SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND status='PENDING'",
        (tid,)).fetchone()["n"]
    ev = conn.execute("SELECT actor_id, after_state FROM repair_events WHERE task_id=? "
                      "AND event_type='reassign'", (tid,)).fetchone()
    conn.close()
    assert ap["status"] == "SUPERSEDED"
    assert jobs == 0, "改派必须取消原技工的到期提醒作业"
    assert ev["actor_id"] == MGR
    clock.set(appt["start_at_ms"] + 1000)
    with pytest.raises(OctoSenseError):
        w.executor.start_progress(actor_id=T1, idem_key="k-old-start", task_id=tid,
                                  expected_version=task_row(db, tid)["version"])


def test_reassign_requires_reason(executor, appt_cmds, db, clock, ext):
    _add_hvac_tech(db, uid="u-tech-8")
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(DraftMissingField):
        appt_cmds.reassign(actor_id=MGR, idem_key="k-r0", task_id=tid,
                           new_assignee_id="u-tech-8",
                           expected_version=task_row(db, tid)["version"], reason="")


def test_reassign_in_progress_rejected(executor, appt_cmds, db, clock, ext):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    with pytest.raises(IllegalTransition):
        appt_cmds.reassign(actor_id=MGR, idem_key="k-ri", task_id=tid,
                           new_assignee_id=T1,
                           expected_version=task_row(db, tid)["version"], reason="换人")
    row = task_row(db, tid)
    assert row["status"] == "IN_PROGRESS" and row["assignee_id"] == T1


def test_reassign_target_must_be_skill_matched(executor, appt_cmds, db, clock, ext):
    """V09：改派对象必须是同项目、技能匹配的有效技工。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(PermissionDenied):
        appt_cmds.reassign(actor_id=MGR, idem_key="k-rs", task_id=tid,
                           new_assignee_id=T2,   # 电气，不能承接 HVAC
                           expected_version=task_row(db, tid)["version"],
                           reason="派给电工")
    assert task_row(db, tid)["assignee_id"] == T1


def test_reassign_replay_returns_original(executor, appt_cmds, db, clock, ext):
    """V05：改派的幂等回放必须给完整原结果。"""
    new_tech = _add_hvac_tech(db, uid="u-tech-6")
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    v = task_row(db, tid)["version"]
    first = okd(appt_cmds.reassign(actor_id=MGR, idem_key="k-ra", task_id=tid,
                                   new_assignee_id=new_tech, expected_version=v,
                                   reason="技工甲请假"), "reassign")
    second = okd(appt_cmds.reassign(actor_id=MGR, idem_key="k-ra", task_id=tid,
                                    new_assignee_id=new_tech, expected_version=v,
                                    reason="技工甲请假"), "reassign replay")
    assert second["idempotent_replay"] is True
    assert second["action_id"] == first["action_id"]
    assert second["result"] == first
    row = task_row(db, tid)
    assert row["version"] == v + 1, "replay 不得再 bump 版本"
