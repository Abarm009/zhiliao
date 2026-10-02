"""核心命令测试：覆盖 T02/T04/T05/T11/T20/T21 子集。

修复后版本：完整业务流程 + bind asset + 注入时钟。
"""
from __future__ import annotations

import time

import pytest

from octosense_backend.errors import (
    ConcurrentConflict,
    DraftMissingField,
    IdempotencyConflict,
    IllegalTransition,
    PermissionDenied,
    VersionConflict,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _setup_completed(executor, ext, appt_cmds, fixtures, clock):
    """建任务并推到 AWAITING_ACCEPTANCE；START 时间钳在 CONFIRMED 窗口内。

    返回 task_id 与提交后的 version。
    """
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="k-create", problem_text="空调不制冷",
                                contact_name="张三", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="k-confirm", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="k-accept", task_id=tid, expected_version=2)
    executor.bind_asset = ext.bind_asset.__get__(executor, type(executor)) if False else None
    # bind asset (T09 显式要求)
    ext.bind_asset(actor_id=r, idem_key="k-bind", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    # 提议预约：start 在 5 分钟后，时长 30 分钟
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="k-propose",
                                       task_id=tid, start_at_ms=start, end_at_ms=end,
                                       expected_version=4)
    appt_id = pr.data["appointment_id"]
    # 报修人确认 → CONFIRMED + task SCHEDULED
    appt_cmds.confirm_appointment(actor_id=r, idem_key="k-confappt",
                                  task_id=tid, expected_version=5,
                                  appointment_id=appt_id)
    # 时钟注入到 CONFIRMED 窗口中段
    clock._offset_ms = (start + end) // 2 - _now_ms()
    def fixed_clock():
        return _now_ms() + getattr(clock, "_offset_ms", 0)
    executor._clock = fixed_clock
    executor.start_progress(actor_id=t, idem_key="k-start", task_id=tid, expected_version=6)
    # 上传 READY 证据
    ext.upload_evidence(actor_id=t, idem_key="k-ev1", task_id=tid,
                        filename="note.txt", mime_type="text/plain",
                        payload=b"site-note-bytes-18-by", expected_version=7)
    # 完工
    res = executor.submit_completion(actor_id=t, idem_key="k-complete",
                                     task_id=tid, expected_version=8,
                                     completion_text="已更换压缩机")
    return tid, res.data["version"]


def test_create_draft_to_open_to_accepted_to_completed_happy(executor, ext, appt_cmds, fixtures, clock):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]

    res = executor.create_draft(actor_id=r, idem_key="k-create-1",
                                problem_text="空调不制冷", contact_name="张三",
                                project_id=p)
    assert res.ok
    task_id = res.data["task_id"]

    # 同 key 重发：返回同 task_id（幂等）
    res2 = executor.create_draft(actor_id=r, idem_key="k-create-1",
                                 problem_text="空调不制冷", contact_name="张三",
                                 project_id=p)
    assert res2.ok and res2.data["idempotent_replay"] is True
    assert res2.data["task_id"] == task_id

    with pytest.raises(VersionConflict):
        executor.confirm_draft(actor_id=r, idem_key="k-confirm-bad",
                               task_id=task_id, expected_version=99)

    res = executor.confirm_draft(actor_id=r, idem_key="k-confirm-1",
                                 task_id=task_id, expected_version=1)
    assert res.ok
    assert res.data["status"] == "OPEN"
    assert res.data["version"] == 2

    res = executor.accept_task(actor_id=t, idem_key="k-accept-1",
                               task_id=task_id, expected_version=2)
    assert res.ok
    assert res.data["status"] == "ACCEPTED"
    assert res.data["assignee_id"] == t

    # 绑设备
    ext.bind_asset(actor_id=r, idem_key="k-bind", task_id=task_id,
                   asset_id=fixtures["asset_a1"], expected_version=3)

    # 提议预约（保持 ACCEPTED）
    start = _now_ms() + 5 * 60_000
    end = start + 30 * 60_000
    res = executor.propose_appointment(actor_id=t, idem_key="k-propose-1",
                                       task_id=task_id, start_at_ms=start, end_at_ms=end,
                                       expected_version=4)
    assert res.ok
    assert res.data["status"] == "ACCEPTED"  # 修复 Q02
    assert res.data["version"] == 5
    appt_id = res.data["appointment_id"]

    # 确认预约 → task SCHEDULED
    appt_res = appt_cmds.confirm_appointment(actor_id=r, idem_key="k-confappt",
                                             task_id=task_id, expected_version=5,
                                             appointment_id=appt_id)
    assert appt_res["task_status"] == "SCHEDULED"
    assert appt_res["task_version"] == 6

    # 注入时钟到 CONFIRMED 窗口
    def fixed():
        return (start + end) // 2
    executor._clock = fixed

    res = executor.start_progress(actor_id=t, idem_key="k-start-1",
                                  task_id=task_id, expected_version=6)
    assert res.ok
    assert res.data["status"] == "IN_PROGRESS"
    assert res.data["version"] == 7

    # 无证据不能完工
    # 先退到 IN_PROGRESS 前的状态需要新任务，改为：先上传然后隔离再试
    ext.upload_evidence(actor_id=t, idem_key="k-ev0", task_id=task_id,
                        filename="bad.jpg", mime_type="image/jpeg",
                        payload=b"x", expected_version=7)
    ext.quarantine_evidence(actor_id=fixtures["manager"], idem_key="q-ev",
                            task_id=task_id, evidence_id=ext.list_evidence(actor_id=r, task_id=task_id)["evidence"][0]["evidence_id"],
                            expected_version=7, reason="不通过")
    with pytest.raises(DraftMissingField):
        executor.submit_completion(actor_id=t, idem_key="k-complete-bad",
                                    task_id=task_id, expected_version=8,
                                    completion_text="已更换压缩机")

    ext.upload_evidence(actor_id=t, idem_key="k-ev1", task_id=task_id,
                        filename="note.txt", mime_type="text/plain",
                        payload=b"site-note-bytes-18-by", expected_version=7)

    res = executor.submit_completion(actor_id=t, idem_key="k-complete-1",
                                     task_id=task_id, expected_version=7,
                                     completion_text="已更换压缩机")
    assert res.ok
    assert res.data["status"] == "AWAITING_ACCEPTANCE"
    assert res.data["version"] == 8
    # completion_id 持久化（N09）
    assert "completion_id" in res.data
    assert res.data["round"] == 1

    # 技工不能自验
    with pytest.raises(PermissionDenied):
        executor.accept_completion(actor_id=t, idem_key="k-accept-finish",
                                    task_id=task_id, expected_version=8)

    res = executor.accept_completion(actor_id=r, idem_key="k-accept-finish-2",
                                      task_id=task_id, expected_version=8)
    assert res.ok
    assert res.data["status"] == "COMPLETED"
    assert res.data["version"] == 9


def test_two_techs_one_task_only_one_accepts(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t1 = fixtures["tech_1"]

    res = executor.create_draft(actor_id=r, idem_key="k-c1", problem_text="P",
                                contact_name="张", project_id=p)
    task_id = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="k-o1", task_id=task_id, expected_version=1)

    a = executor.accept_task(actor_id=t1, idem_key="k-a1",
                             task_id=task_id, expected_version=2)
    assert a.ok

    t2 = fixtures["tech_2"]
    # tech_2 应被拒绝（accept 仅 OPEN，已是 ACCEPTED）
    with pytest.raises((IllegalTransition, VersionConflict)):
        executor.accept_task(actor_id=t2, idem_key="k-a2",
                             task_id=task_id, expected_version=2)


def test_concurrent_appointment_overlap_proposed_does_not_conflict(executor, fixtures):
    """PROPOSED 不预占技工资源；冲突检测仅对 CONFIRMED 生效。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]

    res = executor.create_draft(actor_id=r, idem_key="c1", problem_text="p1",
                                contact_name="z", project_id=p)
    t1 = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o1", task_id=t1, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="acc1", task_id=t1, expected_version=2)
    s = _now_ms() + 3600_000
    e = s + 60 * 60 * 1000
    res = executor.propose_appointment(actor_id=t, idem_key="pr1", task_id=t1,
                                       start_at_ms=s, end_at_ms=e, expected_version=3)
    assert res.ok

    res = executor.create_draft(actor_id=r, idem_key="c2", problem_text="p2",
                                contact_name="z", project_id=p)
    t2 = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o2", task_id=t2, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="acc2", task_id=t2, expected_version=2)
    res = executor.propose_appointment(
        actor_id=t, idem_key="pr2", task_id=t2,
        start_at_ms=s + 30 * 60 * 1000, end_at_ms=e + 30 * 60 * 1000, expected_version=3,
    )
    assert res.ok


def test_idempotency_same_key_same_payload(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    a = executor.create_draft(actor_id=r, idem_key="X", problem_text="P",
                              contact_name="C", project_id=p)
    assert a.ok
    b = executor.create_draft(actor_id=r, idem_key="X", problem_text="P",
                              contact_name="C", project_id=p)
    assert b.ok and b.data.get("idempotent_replay") is True


def test_idempotency_same_key_different_payload_409(executor, fixtures):
    """R-P0-4：同 key 不同 payload 返 IdempotencyConflict (409)。"""
    from octosense_backend.errors import IdempotencyConflict
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    executor.create_draft(actor_id=r, idem_key="Y", problem_text="P1",
                          contact_name="C1", project_id=p)
    with pytest.raises(IdempotencyConflict):
        executor.create_draft(actor_id=r, idem_key="Y", problem_text="P2",
                              contact_name="C2", project_id=p)


def test_version_conflict(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    res = executor.create_draft(actor_id=r, idem_key="k", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    with pytest.raises(VersionConflict):
        executor.confirm_draft(actor_id=r, idem_key="k2",
                               task_id=tid, expected_version=2)


def test_illegal_transition(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    res = executor.create_draft(actor_id=r, idem_key="k", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    with pytest.raises(IllegalTransition):
        executor.accept_task(actor_id=fixtures["tech_1"], idem_key="k",
                             task_id=tid, expected_version=1)


def test_reject_completion_returns_to_in_progress(executor, ext, appt_cmds, fixtures, clock):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]

    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=4)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=5, appointment_id=appt_id)
    # 注入时钟到窗口内
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=6)
    ext.upload_evidence(actor_id=t, idem_key="ev1", task_id=tid,
                        filename="v1.txt", mime_type="text/plain",
                        payload=b"xxxx", expected_version=7)
    res = executor.submit_completion(actor_id=t, idem_key="cp", task_id=tid,
                                     expected_version=7, completion_text="修了")
    assert res.ok and res.data["version"] == 8

    res = executor.reject_completion(actor_id=r, idem_key="rj",
                                     task_id=tid, expected_version=8, reason="还需清理")
    assert res.ok
    assert res.data["status"] == "IN_PROGRESS"
    assert res.data["version"] == 9
    assert res.data["reason"] == "还需清理"

    # 二次完工产生新 completion_id / round
    executor._clock = lambda: (s + e) // 2 + 60_000  # 仍在窗口
    ext.upload_evidence(actor_id=t, idem_key="ev2", task_id=tid,
                        filename="v2.txt", mime_type="text/plain",
                        payload=b"yyyy", expected_version=9)
    res = executor.submit_completion(actor_id=t, idem_key="cp2", task_id=tid,
                                     expected_version=9, completion_text="修了2")
    assert res.ok and res.data["round"] == 2


def test_cancel_requires_reason(executor, fixtures):
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    with pytest.raises(DraftMissingField):
        executor.cancel(actor_id=r, idem_key="x", task_id=tid,
                        expected_version=1, reason="")


def test_permission_denied(executor, fixtures):
    """不在项目角色中的用户被拒绝。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    with pytest.raises((PermissionDenied, __import__('octosense_backend.errors', fromlist=['IdentityRequired']).IdentityRequired)):
        executor.accept_task(actor_id="u-no-such-user", idem_key="x",
                             task_id=tid, expected_version=2)


def test_start_progress_requires_confirmed_appointment(executor, fixtures):
    """PROPOSED 而未 CONFIRMED 不能开工。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                 start_at_ms=s, end_at_ms=e, expected_version=3)
    # 此时任务仍在 ACCEPTED（fix Q02），且 PROPOSED 而未 CONFIRMED
    with pytest.raises(IllegalTransition):
        executor.start_progress(actor_id=t, idem_key="st-bad",
                                task_id=tid, expected_version=4)


def test_start_progress_requires_bound_asset(executor, ext, appt_cmds, fixtures, clock):
    """Q03：未绑定设备不能开工。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=3)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=4, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    with pytest.raises(IllegalTransition):
        executor.start_progress(actor_id=t, idem_key="st",
                                task_id=tid, expected_version=5)


def test_submit_completion_requires_ready_evidence(executor, ext, appt_cmds, fixtures, clock):
    """P1：零证据（且 QUARANTINED 不算）不能完工。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=4)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=5, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=6)
    with pytest.raises(DraftMissingField):
        executor.submit_completion(actor_id=t, idem_key="cp-bad",
                                    task_id=tid, expected_version=7,
                                    completion_text="修了")
    up = ext.upload_evidence(actor_id=t, idem_key="u1", task_id=tid,
                              filename="x.jpg", mime_type="image/jpeg",
                              payload=b"x", expected_version=7)
    ext.quarantine_evidence(actor_id=fixtures["manager"], idem_key="q1",
                             task_id=tid, evidence_id=up["evidence_id"],
                             expected_version=7, reason="不通过")
    with pytest.raises(DraftMissingField):
        executor.submit_completion(actor_id=t, idem_key="cp-bad2",
                                    task_id=tid, expected_version=7,
                                    completion_text="修了")
    ext.upload_evidence(actor_id=t, idem_key="u2", task_id=tid,
                        filename="ok.jpg", mime_type="image/jpeg",
                        payload=b"y", expected_version=7)
    res = executor.submit_completion(actor_id=t, idem_key="cp-ok",
                                      task_id=tid, expected_version=7,
                                      completion_text="修了")
    assert res.ok
    assert res.data["status"] == "AWAITING_ACCEPTANCE"
    assert res.data["version"] == 8


def test_cross_project_create_rejected(executor, fixtures):
    """R-P0-2/N03：跨项目不能建草稿。"""
    from octosense_backend.errors import IdentityRequired, PermissionDenied
    # u-reporter-2 不在 prj-A
    with pytest.raises((IdentityRequired, PermissionDenied)):
        executor.create_draft(actor_id=fixtures["reporter_2"], idem_key="cp1",
                              problem_text="x", contact_name="y",
                              project_id=fixtures["project_a"])
    # u-reporter-1 不在 prj-B
    with pytest.raises((IdentityRequired, PermissionDenied)):
        executor.create_draft(actor_id=fixtures["reporter_1"], idem_key="cp2",
                              problem_text="x", contact_name="y",
                              project_id=fixtures["project_b"])


def test_scheduled_cannot_be_reaccepted(executor, ext, appt_cmds, fixtures, clock):
    """N02/Q02：SCHEDULED 任务不可被另一技工重新接单。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=4)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=5, appointment_id=appt_id)
    # 现在 task=SCHEDULED，tech_2 不可接
    with pytest.raises(IllegalTransition):
        executor.accept_task(actor_id=fixtures["tech_2"], idem_key="a2",
                             task_id=tid, expected_version=6)


def test_reject_completion_only_from_awaiting(executor, ext, appt_cmds, fixtures, clock):
    """Q01：reject-finish 仅 AWAITING_ACCEPTANCE。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=4)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=5, appointment_id=appt_id)
    # 此时 SCHEDULED，reject-finish 应拒
    with pytest.raises(IllegalTransition):
        executor.reject_completion(actor_id=r, idem_key="rj",
                                    task_id=tid, expected_version=6, reason="x")


def test_manager_accept_requires_reason(executor, ext, appt_cmds, fixtures, clock):
    """N08：经理代验收必须有理由。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=3)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=4)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=5, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=6)
    ext.upload_evidence(actor_id=t, idem_key="ev", task_id=tid,
                        filename="x.txt", mime_type="text/plain",
                        payload=b"x", expected_version=7)
    executor.submit_completion(actor_id=t, idem_key="cp", task_id=tid,
                                expected_version=7, completion_text="修了")
    # 经理无理由拒绝
    with pytest.raises(DraftMissingField):
        executor.accept_completion(actor_id=fixtures["manager"], idem_key="ac-mgr",
                                    task_id=tid, expected_version=8, reason="")
    # 经理带理由 → 成功
    res = executor.accept_completion(actor_id=fixtures["manager"], idem_key="ac-mgr2",
                                      task_id=tid, expected_version=8, reason="经理代验收")
    assert res.ok
    assert res.data["status"] == "COMPLETED"
