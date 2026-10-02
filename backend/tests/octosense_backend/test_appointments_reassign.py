"""T06 / T12 测试：appointments + reassign。

修复后版本：Q04 经理不能代确认；N06 拒绝改约保留 SCHEDULED。
"""
from __future__ import annotations

import time

import pytest

from octosense_backend.appointments import AppointmentCommands
from octosense_backend.errors import (
    IllegalTransition,
    OctoSenseError,
    PermissionDenied,
    VersionConflict,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


@pytest.fixture
def appt_cmds(db) -> AppointmentCommands:
    return AppointmentCommands(db)


def _setup_accepted_task(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    return p, r, t, tid


def test_confirm_rejects_unknown_actor(executor, appt_cmds, fixtures):
    p, r, t, tid = _setup_accepted_task(executor, fixtures)
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t, idem_key="p1", task_id=tid,
                                       start_at_ms=start, end_at_ms=end, expected_version=3)
    assert res.ok
    with pytest.raises(PermissionDenied):
        appt_cmds.confirm_appointment(actor_id="u-no-such-user", idem_key="x",
                                      task_id=tid, expected_version=4)


def test_confirm_only_reporter_no_manager_substitute(executor, appt_cmds, fixtures):
    """Q04：经理不能代确认预约。"""
    p, r, t, tid = _setup_accepted_task(executor, fixtures)
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t, idem_key="p1", task_id=tid,
                                       start_at_ms=start, end_at_ms=end, expected_version=3)
    appt_id = res.data["appointment_id"]
    with pytest.raises(PermissionDenied):
        appt_cmds.confirm_appointment(actor_id=fixtures["manager"], idem_key="mgr-conf",
                                      task_id=tid, expected_version=4,
                                      appointment_id=appt_id)


def test_reject_appointment_keeps_old_confirmed(executor, appt_cmds, fixtures):
    """T12 / N06：拒绝 PROPOSED 保留旧 CONFIRMED → task 保持 SCHEDULED。"""
    p, r, t, tid = _setup_accepted_task(executor, fixtures)
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t, idem_key="p1", task_id=tid,
                                       start_at_ms=start, end_at_ms=end, expected_version=3)
    appt_id_1 = res.data["appointment_id"]
    res = appt_cmds.confirm_appointment(actor_id=r, idem_key="conf1",
                                        task_id=tid, expected_version=4,
                                        appointment_id=appt_id_1)
    assert res["task_status"] == "SCHEDULED"
    # 走 ext 绑定
    from octosense_backend.extended import ExtendedCommands
    ext = ExtendedCommands(executor.db)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=5)
    # 再提议（不同时间） — 在 SCHEDULED 仍可提议
    start2 = end + 60 * 60 * 1000
    end2 = start2 + 60 * 60 * 1000
    res = executor.propose_appointment(actor_id=t, idem_key="p2", task_id=tid,
                                       start_at_ms=start2, end_at_ms=end2, expected_version=6)
    assert res.ok
    # 拒绝新提议；保留旧 CONFIRMED，task 保持 SCHEDULED
    res = appt_cmds.reject_appointment(actor_id=r, idem_key="rj1",
                                       task_id=tid, expected_version=7, reason="时间不行")
    assert res["status"] == "SCHEDULED"
    # 第一个预约仍 CONFIRMED
    conn = executor.db.conn()
    row = conn.execute(
        "SELECT status FROM repair_appointments WHERE appointment_id=?",
        (appt_id_1,),
    ).fetchone()
    assert row["status"] == "CONFIRMED"


def test_reject_appointment_when_no_proposed_rejected(executor, appt_cmds, fixtures):
    """Q05：不存在 PROPOSED 时拒绝命令。"""
    p, r, t, tid = _setup_accepted_task(executor, fixtures)
    # 当前无 PROPOSED，直接 reject 应失败
    with pytest.raises(IllegalTransition):
        appt_cmds.reject_appointment(actor_id=r, idem_key="rj0",
                                      task_id=tid, expected_version=3, reason="x")


def test_reassign_scheduled_releases_appointment(executor, appt_cmds, fixtures):
    """T06：经理改派 SCHEDULED 任务，旧预约 SUPERSEDED，任务回 ACCEPTED。"""
    p, r, t1, tid = _setup_accepted_task(executor, fixtures)
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t1, idem_key="p1", task_id=tid,
                                       start_at_ms=start, end_at_ms=end, expected_version=3)
    appt_id = res.data["appointment_id"]
    res = appt_cmds.confirm_appointment(actor_id=r, idem_key="conf1",
                                        task_id=tid, expected_version=4,
                                        appointment_id=appt_id)
    assert res["task_status"] == "SCHEDULED"
    mgr = fixtures["manager"]
    t2 = fixtures["tech_2"]
    res = appt_cmds.reassign(actor_id=mgr, idem_key="reassign-1",
                              task_id=tid, new_assignee_id=t2,
                              expected_version=5, reason="原技工忙")
    assert res["status"] == "ACCEPTED"
    assert res["assignee_id"] == t2
    conn = executor.db.conn()
    row = conn.execute(
        "SELECT status FROM repair_appointments WHERE appointment_id=?",
        (appt_id,),
    ).fetchone()
    assert row["status"] == "SUPERSEDED"


def test_reassign_in_progress_rejected(executor, appt_cmds, fixtures, clock):
    """IN_PROGRESS 任务禁止改派。"""
    p, r, t, tid = _setup_accepted_task(executor, fixtures)
    from octosense_backend.extended import ExtendedCommands
    ext = ExtendedCommands(executor.db)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t, idem_key="p1", task_id=tid,
                                       start_at_ms=start, end_at_ms=end, expected_version=4)
    appt_id = res.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="conf1",
                                   task_id=tid, expected_version=5,
                                   appointment_id=appt_id)
    executor._clock = lambda: (start + end) // 2
    executor.start_progress(actor_id=t, idem_key="st1", task_id=tid, expected_version=6)
    mgr = fixtures["manager"]
    t2 = fixtures["tech_2"]
    with pytest.raises(IllegalTransition):
        appt_cmds.reassign(actor_id=mgr, idem_key="reassign-2",
                            task_id=tid, new_assignee_id=t2,
                            expected_version=7, reason="已开工")
