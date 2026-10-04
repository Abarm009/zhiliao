"""预约命令测试：提议 / 确认 / 拒绝 / 改约 / 冲突 / 有效期 / 时钟。

对应 T10/T11/T12/T13/T14/T22 与 V05/V06。
"""
from __future__ import annotations

import json

import pytest

from octosense_backend.commands import APPOINTMENT_DEFAULTS, CommandExecutor
from octosense_backend.db import Database
from octosense_backend.errors import (
    AppointmentExpired,
    AppointmentWindowInvalid,
    ConcurrentConflict,
    DraftMissingField,
    IdempotencyConflict,
    IllegalTransition,
    OctoSenseError,
    PermissionDenied,
    VersionConflict,
)

from world import (
    AS_AC, ELECTRICAL, HVAC, MGR, PA, PB, R1, R2, SP_ROOM, T1, T2, World,
    expect_error, ok, okd, task_row,
)

DAY = 24 * 3600 * 1000


# ---------- T10 提议不直接 SCHEDULED ----------

def test_first_proposal_keeps_accepted(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    data = w.propose(tid=tid)
    assert data["status"] == "ACCEPTED"
    assert data["appointment_status"] == "PROPOSED"
    assert task_row(db, tid)["status"] == "ACCEPTED"
    conn = db.conn()
    ap = conn.execute("SELECT * FROM repair_appointments WHERE appointment_id=?",
                      (data["appointment_id"],)).fetchone()
    conn.close()
    assert ap["status"] == "PROPOSED"
    assert ap["proposed_by"] == T1


def test_only_current_assignee_or_manager_can_propose(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    start = clock() + DAY
    with pytest.raises(PermissionDenied):
        executor.propose_appointment(actor_id=T2, idem_key="k-t2", task_id=tid,
                                     start_at_ms=start, end_at_ms=start + 1800 * 1000,
                                     expected_version=task_row(db, tid)["version"])
    # 经理可代提议，事件记录操作者
    data = ok(executor.propose_appointment(
        actor_id=MGR, idem_key="k-mgr", task_id=tid, start_at_ms=start,
        end_at_ms=start + 1800 * 1000,
        expected_version=task_row(db, tid)["version"]), "propose_appointment")
    assert data["proposed_by"] == MGR
    assert data["technician_id"] == T1


def test_non_reporter_cannot_confirm_appointment(executor, ext, appt_cmds, db, clock):
    """T10/Q04：非报修人不能确认预约。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    with pytest.raises(PermissionDenied):
        appt_cmds.confirm_appointment(actor_id=MGR, idem_key="k-mc", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
    with pytest.raises(PermissionDenied):
        appt_cmds.confirm_appointment(actor_id=T1, idem_key="k-tc", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_confirm_marks_scheduled_and_confirmed(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    data = w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    assert data["status"] == "CONFIRMED"
    assert data["task_status"] == "SCHEDULED"
    assert data["confirmed_by"] == R1
    assert task_row(db, tid)["status"] == "SCHEDULED"


# ---------- V05 幂等 ----------

def test_confirm_replay_returns_full_original_result(executor, ext, appt_cmds, db, clock):
    """V05：首次确认与完全相同请求重试必须是同一 action_id 和完整原结果。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, key="k-appt")
    v = task_row(db, tid)["version"]
    first = okd(appt_cmds.confirm_appointment(
        actor_id=R1, idem_key="k-confirm", task_id=tid, expected_version=v,
        appointment_id=appt["appointment_id"]), "confirm_appointment")
    second = okd(appt_cmds.confirm_appointment(
        actor_id=R1, idem_key="k-confirm", task_id=tid, expected_version=v,
        appointment_id=appt["appointment_id"]), "confirm replay")
    assert second["idempotent_replay"] is True
    assert second["action_id"] == first["action_id"]
    assert second["result"] == first, "回放必须给完整原结果，不只 task_id/command"
    conn = db.conn()
    n = conn.execute("SELECT COUNT(*) AS n FROM repair_appointments WHERE appointment_id=? "
                     "AND status='CONFIRMED'",
                     (appt["appointment_id"],)).fetchone()["n"]
    ver = conn.execute("SELECT version FROM repair_tasks WHERE task_id=?",
                       (tid,)).fetchone()["version"]
    conn.close()
    assert n == 1
    assert ver == v + 1, "replay 不得重复 bump 任务版本"


def test_confirm_replay_with_changed_version_is_conflict(executor, ext, appt_cmds, db, clock):
    """V05：同 key 改 expected_version → 409，不是 NameError/500。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, key="k-appt")
    v = task_row(db, tid)["version"]
    okd(appt_cmds.confirm_appointment(actor_id=R1, idem_key="k-confirm2", task_id=tid,
                                      expected_version=v,
                                      appointment_id=appt["appointment_id"]),
        "confirm_appointment")
    with pytest.raises(IdempotencyConflict):
        appt_cmds.confirm_appointment(actor_id=R1, idem_key="k-confirm2", task_id=tid,
                                      expected_version=v + 1,
                                      appointment_id=appt["appointment_id"])


# ---------- V06 改约不再与自己冲突 ----------

def test_reschedule_excluding_replaced_confirmed(executor, ext, appt_cmds, db, clock):
    """V06：平移 1 秒的新提议可确认；旧确认预约被排除于冲突检查。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    start, end = appt["start_at_ms"], appt["end_at_ms"]
    moved = w.propose(tid=tid, start=start + 1000, key="k-move")
    assert moved["start_at_ms"] == start + 1000
    data = w.confirm(tid=tid, appointment_id=moved["appointment_id"], key="k-confirm-move")
    assert data["appointment_id"] == moved["appointment_id"]
    conn = db.conn()
    rows = conn.execute("SELECT appointment_id, status FROM repair_appointments WHERE task_id=?",
                        (tid,)).fetchall()
    conn.close()
    by_id = {r["appointment_id"]: r["status"] for r in rows}
    assert by_id[appt["appointment_id"]] == "SUPERSEDED"
    assert by_id[moved["appointment_id"]] == "CONFIRMED"
    assert task_row(db, tid)["status"] == "SCHEDULED"


def test_reschedule_conflicts_with_other_task_blocked(executor, ext, appt_cmds, db, clock):
    """T11：同技工在**其他任务**上的重叠确认仍被拒（含跨项目）。"""
    w = World(executor, ext, None, db, clock)
    tid_a = w.accepted()
    appt_a = w.propose(tid=tid_a)
    w.confirm(tid=tid_a, appointment_id=appt_a["appointment_id"])
    # 同一技工 T1 在 prj-B 也有角色（跨项目同技工）
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                 "VALUES ('prj-B','u-tech-1','TECHNICIAN','HVAC')")
    conn.execute("INSERT OR IGNORE INTO repair_spaces (space_id, project_id, name) "
                 "VALUES ('sp-b-1','prj-B','B 项目会议室')")
    conn.close()
    tid_b = w.open(key="k-draft-b", reporter=R2, project=PB, space="sp-b-1")
    v = task_row(db, tid_b)["version"]
    ok(executor.accept_task(actor_id=T1, idem_key="k-acc-b", task_id=tid_b,
                            expected_version=v), "accept_task")
    # 任务 B 提议与任务 A 确认区间内部重叠的窗口 → 冲突
    with pytest.raises(ConcurrentConflict):
        executor.propose_appointment(
            actor_id=T1, idem_key="k-propose-b", task_id=tid_b,
            start_at_ms=appt_a["start_at_ms"] + 60000,
            end_at_ms=appt_a["end_at_ms"] - 60000,
            expected_version=task_row(db, tid_b)["version"])
    assert task_row(db, tid_b)["status"] == "ACCEPTED"


def test_adjacent_intervals_do_not_conflict(executor, ext, appt_cmds, db, clock):
    """T11：半开区间 [start,end)，相邻不冲突。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    start, end = appt["start_at_ms"], appt["end_at_ms"]
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
                 "VALUES ('u-tech-4','技工肆（HVAC）',1)")
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                 "VALUES ('prj-A','u-tech-4','TECHNICIAN','HVAC')")
    conn.close()
    tid_b = w.open(key="k-draft-adj")
    v = task_row(db, tid_b)["version"]
    ok(executor.accept_task(actor_id="u-tech-4", idem_key="k-adj-acc", task_id=tid_b,
                            expected_version=v), "accept_task")
    # 邻接区间（end == appt.start）不应冲突：先确认一个紧邻的窗口
    data = ok(executor.propose_appointment(
        actor_id="u-tech-4", idem_key="k-adj-propose", task_id=tid_b,
        start_at_ms=end, end_at_ms=end + 1800 * 1000,
        expected_version=task_row(db, tid_b)["version"]), "propose_appointment")
    assert data["appointment_status"] == "PROPOSED"


# ---------- T12 拒绝保留旧预约 ----------

def test_reject_reschedule_keeps_old_confirmed(executor, ext, appt_cmds, db, clock):
    """T12/N06：拒绝改约保留旧 CONFIRMED 与 SCHEDULED，并能按旧预约开工。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    start, end = appt["start_at_ms"], appt["end_at_ms"]
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
    # 仍能按旧预约开工
    clock.set(start + 60000)
    w.start(tid=tid, at=start + 60000)
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_reject_first_proposal_returns_to_accepted(executor, ext, appt_cmds, db, clock):
    """T12：第一份提议被拒且无旧 CONFIRMED → 任务回 ACCEPTED。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    data = w.reject_proposal(tid=tid, reason="这个时间不行", key="k-rej-first")
    assert data["kept_confirmed"] is False
    assert data["status"] == "ACCEPTED"
    assert task_row(db, tid)["status"] == "ACCEPTED"
    conn = db.conn()
    ap = conn.execute("SELECT status FROM repair_appointments WHERE appointment_id=?",
                      (appt["appointment_id"],)).fetchone()
    conn.close()
    assert ap["status"] == "SUPERSEDED"


def test_reject_requires_reason(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    w.propose(tid=tid)
    with pytest.raises(DraftMissingField):
        appt_cmds.reject_appointment(actor_id=R1, idem_key="k-nr", task_id=tid,
                                     expected_version=task_row(db, tid)["version"],
                                     reason="")


def test_reject_without_proposal_rejected(executor, ext, appt_cmds, db, clock):
    """Q05：没有 PROPOSED 不得 reject，也不得留下虚假的 ACCEPTED。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(IllegalTransition):
        appt_cmds.reject_appointment(actor_id=R1, idem_key="k-np", task_id=tid,
                                     expected_version=task_row(db, tid)["version"],
                                     reason="不要了")


def test_cancelled_task_cannot_reject_appointment(executor, ext, appt_cmds, db, clock):
    """Q05：CANCELLED 任务不能凭空 reject 出一个成功回执。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    ok(executor.cancel(actor_id=MGR, idem_key="k-cx", task_id=tid,
                       expected_version=task_row(db, tid)["version"],
                       reason="用户取消"), "cancel")
    with pytest.raises(IllegalTransition):
        appt_cmds.reject_appointment(actor_id=R1, idem_key="k-cr", task_id=tid,
                                     expected_version=task_row(db, tid)["version"],
                                     reason="取消后还想拒绝")


# ---------- T13/T14 有效期与时间窗 ----------

def test_expired_proposal_confirmation_rejected(executor, ext, appt_cmds, db, clock):
    """T13/V06：过期提议确认 → 410，且不改变任务状态。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    # 快进到提议有效期之后（min(24h, 开始 - 提出)）
    clock.advance(APPOINTMENT_DEFAULTS["proposal_validity_ms"] + 60_000)
    with pytest.raises(AppointmentExpired):
        appt_cmds.confirm_appointment(actor_id=R1, idem_key="k-exp", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_server_clock_not_client_time(executor, ext, appt_cmds, db, clock):
    """T13：客户端伪造“当前时间”无效——窗口校验只用服务端时钟。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    now = clock()
    # 过去时段：无论客户端怎么声称都被拒
    with pytest.raises(AppointmentWindowInvalid):
        executor.propose_appointment(actor_id=T1, idem_key="k-past", task_id=tid,
                                     start_at_ms=now - 2 * 3600 * 1000,
                                     end_at_ms=now - 3600 * 1000,
                                     expected_version=task_row(db, tid)["version"])
    # 超过 30 天上限
    with pytest.raises(AppointmentWindowInvalid):
        executor.propose_appointment(actor_id=T1, idem_key="k-far", task_id=tid,
                                     start_at_ms=now + 31 * DAY,
                                     end_at_ms=now + 31 * DAY + 1800 * 1000,
                                     expected_version=task_row(db, tid)["version"])
    # 时长过短 / 过长
    with pytest.raises(AppointmentWindowInvalid):
        executor.propose_appointment(actor_id=T1, idem_key="k-short", task_id=tid,
                                     start_at_ms=now + DAY,
                                     end_at_ms=now + DAY + 5 * 60 * 1000,
                                     expected_version=task_row(db, tid)["version"])
    with pytest.raises(AppointmentWindowInvalid):
        executor.propose_appointment(actor_id=T1, idem_key="k-long", task_id=tid,
                                     start_at_ms=now + DAY,
                                     end_at_ms=now + DAY + 241 * 60 * 1000,
                                     expected_version=task_row(db, tid)["version"])
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_end_before_start_rejected(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    now = clock() + DAY
    with pytest.raises(DraftMissingField):
        executor.propose_appointment(actor_id=T1, idem_key="k-rev", task_id=tid,
                                     start_at_ms=now, end_at_ms=now - 1,
                                     expected_version=task_row(db, tid)["version"])


def test_new_proposal_supersedes_previous(executor, ext, appt_cmds, db, clock):
    """同一任务最多一个有效 PROPOSED。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    a = w.propose(tid=tid, key="k-p1")
    b = w.propose(tid=tid, key="k-p2", start=clock() + 2 * DAY)
    conn = db.conn()
    by_id = {r["appointment_id"]: r["status"] for r in conn.execute(
        "SELECT appointment_id, status FROM repair_appointments WHERE task_id=?",
        (tid,)).fetchall()}
    conn.close()
    assert by_id[a["appointment_id"]] == "SUPERSEDED"
    assert by_id[b["appointment_id"]] == "PROPOSED"


def test_start_progress_supersedes_late_proposals(executor, ext, appt_cmds, db, clock):
    """开工使其他未确认提议失效。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    w.start(tid=tid, at=appt["start_at_ms"] + 1000)
    conn = db.conn()
    by_id = {r["appointment_id"]: r["status"] for r in conn.execute(
        "SELECT appointment_id, status FROM repair_appointments WHERE task_id=?",
        (tid,)).fetchall()}
    conn.close()
    assert by_id[appt["appointment_id"]] == "CONFIRMED"
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_late_confirm_after_start_rejected(executor, ext, appt_cmds, db, clock):
    """已开工后迟到的确认不得改变预约事实。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    w.start(tid=tid, at=appt["start_at_ms"] + 1000)
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
                 "VALUES ('u-tech-5','技工伍（HVAC）',1)")
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                 "VALUES ('prj-A','u-tech-5','TECHNICIAN','HVAC')")
    conn.close()
    with pytest.raises(OctoSenseError):
        appt_cmds.confirm_appointment(actor_id=R1, idem_key="k-late", task_id=tid,
                                      expected_version=task_row(db, tid)["version"],
                                      appointment_id=appt["appointment_id"])
