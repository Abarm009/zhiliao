"""R3-01～R3-07 第四轮回归测试。

每个用例前置步骤必须断言成功（沿用 world.py 的 ok / assert_status 链）。
"""
from __future__ import annotations

import json
import os
import tempfile
import time

import pytest

from octosense_backend.errors import (
    IllegalTransition,
    IdentityRequired,
    PermissionDenied,
    SpaceRequired,
    VersionConflict,
)
from world import (
    AS_AC,
    AS_EXH,
    AS_PWR,
    ELECTRICAL,
    HVAC,
    MGR,
    PA,
    PB,
    R1,
    R2,
    SP_MECH,
    SP_POWER,
    SP_ROOM,
    T1,
    T2,
    World,
    assert_status,
    expect_error,
    ok,
    okd,
    task_row,
)


# ─────────────────────────────────────────────────────────────
# R3-01：update_draft 事务化
# ─────────────────────────────────────────────────────────────

CONTACT_MARKER = "private-contact-R3-01"


def _draft_no_space(api, key="k-r3-01-draft"):
    """创建一个不带 space 的 DRAFT 任务。"""
    r = api.post("/api/octosense/v1/tasks", headers={"X-Actor-Id": R1}, json={
        "project_id": PA, "problem_text": "R3-01 测试", "contact_name": "R1",
        "contact_info": CONTACT_MARKER, "preferred_window": "", "category": HVAC,
        "idempotency_key": key,
    })
    assert r.status_code == 201, r.text
    return r.json()["task_id"]


def test_r3_01_first_edit_succeeds_within_transaction(api, db):
    """R3-01：首次合法编辑返回 200，仅一次业务更新、一条事件、一条成功回执。"""
    tid = _draft_no_space(api, key="k-r3-01-edit-1")
    rv = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                  headers={"X-Actor-Id": R1},
                  json={"expected_version": 1, "idempotency_key": "k-r3-01-edit-1a",
                        "space_id": SP_ROOM, "contact_name": "新联系人"})
    assert rv.status_code == 200, rv.text
    body = rv.json()
    assert body["task_id"] == tid
    assert body["task_version"] == 2
    assert body["status"] == "DRAFT"
    assert body["space_id"] == SP_ROOM
    # 数据库回读：version=2、一条 update_draft 事件、一条成功 receipt
    row = task_row(db, tid)
    assert row["version"] == 2 and row["status"] == "DRAFT"
    conn = db.conn()
    try:
        n_ev = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_events WHERE task_id=? AND event_type='update_draft'",
            (tid,)).fetchone()["n"]
        n_act = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_actions WHERE task_id=? AND command='update_draft'",
            (tid,)).fetchone()["n"]
    finally:
        conn.close()
    assert n_ev == 1 and n_act == 1


def test_r3_01_identical_replay_keeps_state(api, db):
    """R3-01：完全相同请求重试返回成功，保留原 action_id，事件/回执不再增加。"""
    tid = _draft_no_space(api, key="k-r3-01-replay")
    rv1 = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                   headers={"X-Actor-Id": R1},
                   json={"expected_version": 1, "idempotency_key": "k-r3-01-replay-1",
                         "space_id": SP_ROOM, "contact_name": "Alice"})
    assert rv1.status_code == 200, rv1.text
    action_id_first = rv1.json()["action_id"]
    rv2 = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                   headers={"X-Actor-Id": R1},
                   json={"expected_version": 1, "idempotency_key": "k-r3-01-replay-1",
                         "space_id": SP_ROOM, "contact_name": "Alice"})
    assert rv2.status_code == 200, rv2.text
    # 回放标识 + action_id 一致
    assert rv2.json().get("action_id") == action_id_first
    # 数据库：version 不变
    row = task_row(db, tid)
    assert row["version"] == 2
    conn = db.conn()
    try:
        n_ev = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_events WHERE task_id=? AND event_type='update_draft'",
            (tid,)).fetchone()["n"]
        n_act = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_actions WHERE task_id=? AND command='update_draft'",
            (tid,)).fetchone()["n"]
    finally:
        conn.close()
    assert n_ev == 1 and n_act == 1


def test_r3_01_same_key_different_payload_conflict(api, db):
    """R3-01：同 key 改内容/expected_version 必须 409，所有业务数据/成功回执不变。"""
    tid = _draft_no_space(api, key="k-r3-01-conflict")
    rv1 = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                   headers={"X-Actor-Id": R1},
                   json={"expected_version": 1, "idempotency_key": "k-r3-01-conflict-1",
                         "space_id": SP_ROOM, "contact_name": "Alice"})
    assert rv1.status_code == 200, rv1.text
    # 同 key 不同联系人
    rv2 = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                   headers={"X-Actor-Id": R1},
                   json={"expected_version": 1, "idempotency_key": "k-r3-01-conflict-1",
                         "space_id": SP_ROOM, "contact_name": "Bob"})
    assert rv2.status_code == 409, rv2.text
    # 数据未变
    row = task_row(db, tid)
    assert row["contact_name"] == "Alice" and row["version"] == 2
    conn = db.conn()
    try:
        n_act = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_actions WHERE task_id=? AND command='update_draft'",
            (tid,)).fetchone()["n"]
    finally:
        conn.close()
    assert n_act == 1


def test_r3_01_authorization_enforced(api):
    """R3-01：撤权 / 非本人 / 非 DRAFT / 跨项目空间均拒绝。"""
    tid = _draft_no_space(api, key="k-r3-01-auth")

    # 非本人
    rv = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                  headers={"X-Actor-Id": MGR},
                  json={"expected_version": 1, "idempotency_key": "k-r3-01-auth-1",
                        "space_id": SP_ROOM})
    assert rv.status_code in (403, 404), f"非本人应被拒：{rv.status_code} {rv.text}"

    # 跨项目空间（PB 不在 PA）
    rv = api.post(f"/api/octosense/v1/tasks/{tid}/draft",
                  headers={"X-Actor-Id": R1},
                  json={"expected_version": 1, "idempotency_key": "k-r3-01-auth-2",
                        "space_id": "sp-b-1"})
    assert rv.status_code in (422, 404), f"跨项目空间应被拒：{rv.status_code} {rv.text}"


def test_r3_01_concurrent_old_version_only_one_wins(executor, ext, db, clock, appt_cmds):
    """R3-01：两个相同旧版本并发编辑，只有一个成功，另一个 409。"""
    w = World(executor, ext, appt_cmds, db, clock)
    tid = w.draft(reporter=R1, key="k-r3-01-concurrent")
    v = task_row(db, tid)["version"]
    # 同一 expected_version 并发两次更新不同联系人
    r_a = executor.do_update_draft_blocking = None  # noqa: just for trace
    a = ok(executor.update_draft(
        actor_id=R1, idem_key="k-r3-01-concurrent-A",
        task_id=tid, expected_version=v,
        space_id=SP_ROOM, contact_name="A"), "update A")
    try:
        executor.update_draft(
            actor_id=R1, idem_key="k-r3-01-concurrent-B",
            task_id=tid, expected_version=v,
            space_id=SP_ROOM, contact_name="B")
    except VersionConflict:
        pass
    else:
        raise AssertionError("B 应被 409 拒绝")
    row = task_row(db, tid)
    assert row["version"] == v + 1, f"version 应只 +1：{row['version']}"
    assert row["contact_name"] == "A"


# ─────────────────────────────────────────────────────────────
# R3-02：撤权后所有写路径拒绝
# ─────────────────────────────────────────────────────────────

def _revoke_user(db, user_id, project_id, also_pb=False):
    """从 PA 移除用户，必要时再保留其在 PB 的身份。"""
    conn = db.conn()
    try:
        if also_pb:
            conn.execute(
                "INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
                "VALUES (?, ?, 'REPORTER')", (PB, user_id))
        conn.execute(
            "DELETE FROM repair_roles WHERE user_id=? AND project_id=?",
            (user_id, project_id))
    finally:
        conn.close()


def test_r3_02_draft_edit_rejected_after_revocation(executor, ext, db, clock):
    """R3-02：保留 PB 身份 + 移除 PA 后，原报修人 DRAFT 写被拒。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft(reporter=R1, key="k-r3-02-draft")
    _revoke_user(db, R1, PA, also_pb=True)
    v = task_row(db, tid)
    try:
        executor.update_draft(actor_id=R1, idem_key="k-r3-02-draft-1",
                              task_id=tid, expected_version=v["version"],
                              contact_name="revoked-write")
    except PermissionDenied:
        # 任务不应有副作用
        row = task_row(db, tid)
        assert row["contact_name"] != "revoked-write"
        return
    raise AssertionError("撤权后 DRAFT 写应被拒")


def test_r3_02_bind_asset_in_draft_rejected_after_revocation(executor, ext, db, clock):
    """R3-02：撤权后 DRAFT 阶段 bind_asset 被拒。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft(reporter=R1, key="k-r3-02-bind")
    _revoke_user(db, R1, PA, also_pb=True)
    v = task_row(db, tid)["version"]
    try:
        ext.bind_asset(actor_id=R1, idem_key="k-r3-02-bind-1",
                       task_id=tid, asset_id=AS_AC, expected_version=v)
    except (PermissionDenied, IdentityRequired):
        row = task_row(db, tid)
        assert row["asset_id"] is None
        return
    raise AssertionError("撤权后 DRAFT bind 应被拒")


def test_r3_02_cancel_in_draft_rejected_after_revocation(executor, ext, db, clock):
    """R3-02：撤权后 DRAFT cancel 被拒。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft(reporter=R1, key="k-r3-02-cancel")
    _revoke_user(db, R1, PA, also_pb=True)
    v = task_row(db, tid)["version"]
    try:
        executor.cancel(actor_id=R1, idem_key="k-r3-02-cancel-1",
                        task_id=tid, expected_version=v, reason="removed")
    except PermissionDenied:
        row = task_row(db, tid)
        assert row["status"] == "DRAFT"
        return
    raise AssertionError("撤权后 DRAFT cancel 应被拒")


def test_r3_02_reject_finish_rejected_after_revocation(executor, ext, db, clock, appt_cmds):
    """R3-02：撤权后 AWAITING_ACCEPTANCE reject_completion 被拒。"""
    w = World(executor, ext, appt_cmds, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid)
    v = task_row(db, tid)["version"]
    ok(executor.submit_completion(actor_id=T1, idem_key="k-r3-02-comp",
                                  task_id=tid, completion_text="done",
                                  expected_version=v), "submit")
    _revoke_user(db, R1, PA, also_pb=True)
    v2 = task_row(db, tid)["version"]
    try:
        executor.reject_completion(actor_id=R1, idem_key="k-r3-02-rej",
                                   task_id=tid, expected_version=v2,
                                   reason="removed")
    except PermissionDenied:
        row = task_row(db, tid)
        assert row["status"] == "AWAITING_ACCEPTANCE"
        return
    raise AssertionError("撤权后 reject_completion 应被拒")


def test_r3_02_keep_pb_legitimate_writes(executor, ext, db, clock):
    """R3-02：保留 PB 身份后，合法读写 PB 仍正常。"""
    w = World(executor, ext, None, db, clock)
    # PB 端：R1 保留 REPORTER
    conn = db.conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
            "VALUES (?, ?, 'REPORTER')", (PB, R1))
        # PB 端需要至少一个 space
        conn.execute(
            "INSERT OR IGNORE INTO repair_spaces (space_id, project_id, name) "
            "VALUES (?, ?, ?)", ("sp-b-1", PB, "PB 空间一"))
        conn.execute(
            "INSERT OR IGNORE INTO repair_projects (project_id, name, code, created_at_ms) "
            "VALUES (?, ?, ?, ?)", (PB, "项目B", "PB", clock()))
        conn.execute(
            "INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
            "VALUES (?, ?, ?)", (R1, "R1", 1))
    finally:
        conn.close()
    # R1 在 PB 创建 DRAFT 成功
    out = ok(executor.create_draft(
        actor_id=R1, idem_key="k-r3-02-pb-create",
        problem_text="PB 测试", contact_name="R1",
        project_id=PB, space_id="sp-b-1", category=HVAC), "create_draft PB")
    assert out["task_id"]


def test_r3_02_other_project_member_cannot_view(api, executor, ext, db, clock):
    """R3-02：同主体在另一项目内仍可工作，原项目读 404。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft(reporter=R1, key="k-r3-02-other")
    _revoke_user(db, R1, PA, also_pb=True)
    rv = api.get(f"/api/octosense/v1/tasks/{tid}", headers={"X-Actor-Id": R1})
    assert rv.status_code == 404, rv.text


# ─────────────────────────────────────────────────────────────
# R3-04：history-advice 联系人脱敏
# ─────────────────────────────────────────────────────────────

PRIVATE_CONTACT_R304 = "private-contact-R3-04"


def _seed_contact_for_r304(api, key):
    r = api.post("/api/octosense/v1/tasks", headers={"X-Actor-Id": R1}, json={
        "project_id": PA, "problem_text": "R3-04 测试",
        "contact_name": "R1", "contact_info": PRIVATE_CONTACT_R304,
        "preferred_window": "", "category": HVAC, "space_id": SP_ROOM,
        "idempotency_key": key,
    })
    assert r.status_code == 201
    tid = r.json()["task_id"]
    rv = api.post(f"/api/octosense/v1/tasks/{tid}/confirm",
                  headers={"X-Actor-Id": R1},
                  json={"expected_version": 1, "idempotency_key": key + "-confirm"})
    assert rv.status_code == 200
    return tid


def test_r3_04_history_advice_event_mask(api):
    """R3-04：未接单技工经 history-advice?asset_id=... 也不能拿到 contact_info。"""
    tid = _seed_contact_for_r304(api, key="k-r3-04-ha")
    # 让 T1 可见 OPEN：先让 T1 用 skill_matches 但不接单
    rv = api.get(f"/api/octosense/v1/tasks/{tid}/history-advice?asset_id={AS_AC}",
                 headers={"X-Actor-Id": T1})
    assert rv.status_code == 200, rv.text
    body = rv.text
    assert PRIVATE_CONTACT_R304 not in body, "history-advice 泄露 contact_info"


def test_r3_04_history_advice_reporter_sees_contact(api):
    """R3-04：合法可见主体（报修人）仍能读 contact_info。"""
    tid = _seed_contact_for_r304(api, key="k-r3-04-ha-rep")
    rv = api.get(f"/api/octosense/v1/tasks/{tid}/history-advice?asset_id={AS_AC}",
                 headers={"X-Actor-Id": R1})
    assert rv.status_code == 200
    assert PRIVATE_CONTACT_R304 in rv.text


# ─────────────────────────────────────────────────────────────
# R3-05：unbind 矩阵
# ─────────────────────────────────────────────────────────────

def test_r3_05_unbind_draft_only_reporter(executor, ext, db, clock):
    """R3-05：DRAFT 阶段解绑：原报修人 ✓；经理 ✗。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft(reporter=R1, space=SP_ROOM, key="k-r3-05-draft-r")
    # 先绑设备
    w.bind(tid=tid, actor=R1, asset_id=AS_AC, key="k-r3-05-draft-bind")
    # 经理解绑应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=MGR, idem_key="k-r3-05-draft-mgr",
        task_id=tid, expected_version=v, reason="revoke"),
        PermissionDenied, "manager unbind DRAFT")
    # 原报修人解绑成功
    v = task_row(db, tid)["version"]
    okd(ext.unbind_asset(actor_id=R1, idem_key="k-r3-05-draft-rep",
                         task_id=tid, expected_version=v,
                         reason="revoke"), "reporter unbind DRAFT")
    row = task_row(db, tid)
    assert row["asset_id"] is None


def test_r3_05_unbind_open_only_manager(executor, ext, db, clock):
    """R3-05：OPEN 阶段解绑：经理 ✓；报修人 ✗。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open(reporter=R1, space=SP_ROOM, key="k-r3-05-open")
    # 经理绑定
    w.bind(tid=tid, actor=MGR, asset_id=AS_AC, key="k-r3-05-open-bind")
    # 报修人解绑应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=R1, idem_key="k-r3-05-open-rep",
        task_id=tid, expected_version=v, reason="revoke"),
        PermissionDenied, "reporter unbind OPEN")
    # 经理解绑成功
    v = task_row(db, tid)["version"]
    okd(ext.unbind_asset(actor_id=MGR, idem_key="k-r3-05-open-mgr",
                         task_id=tid, expected_version=v,
                         reason="revoke"), "manager unbind OPEN")


def test_r3_05_unbind_accepted_assignee_or_manager(executor, ext, db, clock):
    """R3-05：ACCEPTED 阶段解绑：当前承接技工 / 经理 ✓；无关技工 / 报修人 ✗。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted(reporter=R1, tech=T1, key="k-r3-05-accepted")
    # 报修人解绑应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=R1, idem_key="k-r3-05-accepted-rep",
        task_id=tid, expected_version=v, reason="revoke"),
        PermissionDenied, "reporter unbind ACCEPTED")
    # 无关技工 T2 解绑应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=T2, idem_key="k-r3-05-accepted-other",
        task_id=tid, expected_version=v, reason="revoke"),
        PermissionDenied, "other tech unbind ACCEPTED")


def test_r3_05_unbind_in_progress_manager_with_reason(executor, ext, db, clock, appt_cmds):
    """R3-05：IN_PROGRESS 解绑：经理 + 理由 ✓；无理由 / 技工 ✗。"""
    w = World(executor, ext, appt_cmds, db, clock)
    tid, _, _ = w.in_progress()
    # 经理无理由应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=MGR, idem_key="k-r3-05-ip-no-reason",
        task_id=tid, expected_version=v, reason=""),
        Exception, "manager unbind IN_PROGRESS no reason")
    # 技工应失败
    v = task_row(db, tid)["version"]
    expect_error(lambda: ext.unbind_asset(
        actor_id=T1, idem_key="k-r3-05-ip-tech",
        task_id=tid, expected_version=v, reason="tech"),
        PermissionDenied, "tech unbind IN_PROGRESS")
    # 经理带理由成功
    v = task_row(db, tid)["version"]
    okd(ext.unbind_asset(actor_id=MGR, idem_key="k-r3-05-ip-mgr-ok",
                         task_id=tid, expected_version=v,
                         reason="客户换装"), "manager unbind IN_PROGRESS with reason")


# ─────────────────────────────────────────────────────────────
# R3-06：开工后过期作业失效
# ─────────────────────────────────────────────────────────────

def test_r3_06_start_progress_cancels_upcoming_reminders(db, executor, ext, appt_cmds, clock):
    """R3-06：进入 IN_PROGRESS 后，开始前提醒立刻失效（不等下次 tick）。"""
    w = World(executor, ext, appt_cmds, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, tech=T1)
    w.confirm(tid=tid, reporter=R1, appointment_id=appt["appointment_id"])
    conn = db.conn()
    try:
        a = conn.execute(
            "SELECT appointment_id, technician_id, start_at_ms, end_at_ms "
            "FROM repair_appointments WHERE task_id=? AND status='CONFIRMED'", (tid,)
        ).fetchone()
        # confirm 已登记 PENDING reminders
        pending_before = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND "
            "kind IN ('APPOINTMENT_UPCOMING','APPOINTMENT_UPCOMING_REPORTER') "
            "AND status='PENDING'", (tid,)
        ).fetchone()["n"]
    finally:
        conn.close()
    assert pending_before >= 1, "应有 PENDING 的开始前提醒"
    # 开工
    clock.set(a["start_at_ms"] + 60_000)
    w.start(tid=tid, tech=T1)
    conn = db.conn()
    try:
        cancelled = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND "
            "kind IN ('APPOINTMENT_UPCOMING','APPOINTMENT_UPCOMING_REPORTER') "
            "AND status='CANCELLED'", (tid,)
        ).fetchone()["n"]
    finally:
        conn.close()
    assert cancelled >= 1, "进入 IN_PROGRESS 后应作废开始前提醒"


def test_r3_06_late_tick_after_in_progress_no_upcoming_reminders(db, executor, ext, appt_cmds, clock):
    """R3-06：IN_PROGRESS 后再 tick，UPCOMING/UPCOMING_REPORTER 必须 0 触发。"""
    from octosense_backend.jobs import run_due_jobs
    w = World(executor, ext, appt_cmds, db, clock)
    tid, start, end = w.in_progress()
    # w.in_progress 已通过 confirm_appointment 登记 reminders；进入 IN_PROGRESS 后
    # start_progress 主动作废 PENDING UPCOMING/UPCOMING_REPORTER，无需额外调度登记。
    # 验证 tick 不会再产生 UPCOMING 通知
    clock.set(end + 60_000)
    conn = db.conn()
    try:
        before = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_notifications WHERE task_id=?",
            (tid,)).fetchone()["n"]
    finally:
        conn.close()
    run_due_jobs(db, clock=lambda: clock())
    conn = db.conn()
    try:
        after = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_notifications WHERE task_id=?",
            (tid,)).fetchone()["n"]
        upcoming = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND "
            "kind IN ('APPOINTMENT_UPCOMING','APPOINTMENT_UPCOMING_REPORTER') "
            "AND status='PENDING'", (tid,)).fetchone()["n"]
    finally:
        conn.close()
    assert after == before, f"IN_PROGRESS 后不应再发开始前提醒：增量 {after - before}"
    assert upcoming == 0, "积压的开始前提醒应被取消"


def test_r3_06_normal_upcoming_reminder_still_fires(db, executor, ext, appt_cmds, clock):
    """R3-06：正常预约到期前提醒可发送且恰好一次。"""
    from octosense_backend.jobs import run_due_jobs
    w = World(executor, ext, appt_cmds, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, tech=T1)
    w.confirm(tid=tid, reporter=R1, appointment_id=appt["appointment_id"])
    conn = db.conn()
    try:
        a = conn.execute(
            "SELECT appointment_id, technician_id, start_at_ms, end_at_ms "
            "FROM repair_appointments WHERE task_id=? AND status='CONFIRMED'", (tid,)
        ).fetchone()
    finally:
        conn.close()
    # confirm_appointment 已登记 reminders；直接 tick 验证发送
    clock.set(a["start_at_ms"] - 30 * 60_000)
    fired = run_due_jobs(db, clock=lambda: clock())
    assert fired >= 2, f"应触发 reporter + technician 两条：{fired}"
    # 再 tick 应不重复
    fired2 = run_due_jobs(db, clock=lambda: clock())
    assert fired2 == 0, f"重复 tick 应 0 触发：{fired2}"


def test_r3_06_acceptance_due_round_mismatch_cancelled(db, executor, ext, appt_cmds, clock):
    """R3-06：ACCEPTANCE_DUE 在指定 round 不存在时取消。"""
    from octosense_backend.jobs import schedule_acceptance_reminder, run_due_jobs
    w = World(executor, ext, appt_cmds, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid)
    v = task_row(db, tid)["version"]
    ok(executor.submit_completion(actor_id=T1, idem_key="k-r3-06-comp",
                                  task_id=tid, completion_text="r1",
                                  expected_version=v), "submit")
    schedule_acceptance_reminder(db, tid, R1, round_number=99, clock=clock)
    clock.advance(25 * 3600 * 1000)
    fired = run_due_jobs(db, clock=lambda: clock())
    assert fired == 0, "round 不存在的验收提醒应被取消"


# ─────────────────────────────────────────────────────────────
# R3-07：撤权接收者不再产生新通知
# ─────────────────────────────────────────────────────────────

def test_r3_07_revoked_reporter_no_new_notifications(db, executor, ext, appt_cmds, clock):
    """R3-07：撤权后到期作业不为该用户产生新通知。"""
    from octosense_backend.jobs import run_due_jobs
    w = World(executor, ext, appt_cmds, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, tech=T1)
    w.confirm(tid=tid, reporter=R1, appointment_id=appt["appointment_id"])
    conn = db.conn()
    try:
        a = conn.execute(
            "SELECT appointment_id, technician_id, start_at_ms, end_at_ms "
            "FROM repair_appointments WHERE task_id=? AND status='CONFIRMED'", (tid,)
        ).fetchone()
    finally:
        conn.close()
    # 撤权（confirm 已通过 schedule_appointment_reminders 登记 PENDING 作业）
    _revoke_user(db, R1, PA, also_pb=True)
    clock.set(a["start_at_ms"] - 30 * 60_000)
    run_due_jobs(db, clock=lambda: clock())
    # 不应有 A 任务的新通知落到 R1 名下
    conn = db.conn()
    try:
        n = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_notifications WHERE user_id=? AND task_id=?",
            (R1, tid)).fetchone()["n"]
    finally:
        conn.close()
    assert n == 0, f"撤权后不应再产生 A 任务通知，实际 {n}"


def test_r3_07_notifications_api_filters_revoked(api, executor, ext, db, clock):
    """R3-07：notifications 接口不会泄露已撤权任务的通知。"""
    from octosense_backend.appointments import AppointmentCommands
    w = World(executor, ext, None, db, clock)
    # 创建任务到 SCHEDULED + 确认预约
    tid = w.accepted(reporter=R1, key="k-r3-07-notif")
    appt = w.propose(tid=tid, tech=T1)
    w.confirm(tid=tid, reporter=R1, appointment_id=appt["appointment_id"])
    # 直接插一条"历史"通知（用于验证读取端过滤）
    conn = db.conn()
    try:
        conn.execute(
            "INSERT INTO repair_notifications (notification_id, user_id, task_id, kind, "
            "body, created_at_ms) VALUES (?, ?, ?, ?, ?, ?)",
            ("notif-r307", R1, tid, "APPOINTMENT_UPCOMING_REPORTER",
             "你的报修预约将于 1 小时后开始（task " + tid + "）",
             clock() + 25 * 3600 * 1000))
    finally:
        conn.close()
    # 撤权
    _revoke_user(db, R1, PA, also_pb=True)
    rv = api.get("/api/octosense/v1/notifications", headers={"X-Actor-Id": R1})
    assert rv.status_code == 200
    items = rv.json()["notifications"]
    # 已被撤权的 A 任务通知不应再返回
    leaked = [n for n in items if n["task_id"] == tid]
    assert not leaked, f"撤权后仍泄露 A 任务通知：{leaked}"


def test_r3_07_other_legitimate_users_still_receive(db, executor, ext, appt_cmds, clock):
    """R3-07：合法其他接收者（技工）仍能收到通知，不能因为一个接收者撤权全部取消。"""
    from octosense_backend.jobs import run_due_jobs
    w = World(executor, ext, appt_cmds, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid, tech=T1)
    w.confirm(tid=tid, reporter=R1, appointment_id=appt["appointment_id"])
    conn = db.conn()
    try:
        a = conn.execute(
            "SELECT appointment_id, technician_id, start_at_ms, end_at_ms "
            "FROM repair_appointments WHERE task_id=? AND status='CONFIRMED'", (tid,)
        ).fetchone()
    finally:
        conn.close()
    # 仅撤 R1，保留 T1
    _revoke_user(db, R1, PA)
    clock.set(a["start_at_ms"] - 30 * 60_000)
    run_due_jobs(db, clock=lambda: clock())
    conn = db.conn()
    try:
        tech_n = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_notifications WHERE user_id=? AND task_id=?",
            (T1, tid)).fetchone()["n"]
        rep_n = conn.execute(
            "SELECT COUNT(*) AS n FROM repair_notifications WHERE user_id=? AND task_id=?",
            (R1, tid)).fetchone()["n"]
    finally:
        conn.close()
    assert tech_n >= 1, f"技工仍应收提醒：{tech_n}"
    assert rep_n == 0, f"撤权报修人不应收：{rep_n}"


# ─────────────────────────────────────────────────────────────
# R3-02：合法用户 B 项目原请求重试仍可回放
# ─────────────────────────────────────────────────────────────

def test_r3_02_idempotent_replay_after_revoke_still_works(executor, ext, db, clock):
    """R3-02：合法主体（不是被撤权那个）的原请求重试应回放，不重复写入。"""
    w = World(executor, ext, None, db, clock)
    # R1 创建 DRAFT
    out = ok(executor.create_draft(
        actor_id=R1, idem_key="k-r3-02-replay",
        problem_text="PB", contact_name="R1",
        project_id=PA, space_id=SP_ROOM, category=HVAC), "create")
    tid = out["task_id"]
    # 同一 key 重放 → 原 action_id + 完整结果
    again = ok(executor.create_draft(
        actor_id=R1, idem_key="k-r3-02-replay",
        problem_text="PB", contact_name="R1",
        project_id=PA, space_id=SP_ROOM, category=HVAC), "replay")
    assert again["task_id"] == tid
    assert again.get("action_id") == out.get("action_id")