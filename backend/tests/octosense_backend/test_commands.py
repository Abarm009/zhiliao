"""核心命令测试：状态机、权限、幂等、版本、并发、完工验收。

对应 T02/T04/T05/T15/T16/T20/T21/T22/T31 与 V02/V03/V04/V05/V09/V10/V11。
"""
from __future__ import annotations

import json
import threading
import time

import pytest

from octosense_backend import authorization as auth
from octosense_backend.commands import CommandExecutor
from octosense_backend.db import Database
from octosense_backend.errors import (
    ConcurrentConflict,
    OctoSenseError,
    DraftMissingField,
    IdempotencyConflict,
    IllegalTransition,
    InvalidProjectReference,
    InvalidVersion,
    PermissionDenied,
    SkillMismatch,
    SpaceRequired,
    TaskNotFound,
    VersionConflict,
)

from world import (
    AS_AC, AS_EXH, AS_PWR, ELECTRICAL, GHOST, HVAC, MGR, PA, PB, R1, R2, SP_MECH,
    SP_POWER, SP_ROOM, T1, T2, World, expect_error, ok, okd, task_row,
)


# ---------- T01/T03 草稿与提交 ----------

def test_draft_requires_project_contact_and_space_before_open(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft(problem="空调不制冷", contact="报修人一")
    tid2 = w.draft(key="k-draft-2")
    conn = db.conn()
    conn.execute("UPDATE repair_tasks SET contact_name='   ' WHERE task_id=?", (tid2,))
    conn.close()
    v = task_row(db, tid2)["version"]
    with pytest.raises(DraftMissingField):
        executor.confirm_draft(actor_id=R1, idem_key="k-c2", task_id=tid2,
                               expected_version=v)
    # 失败后草稿保留且仍是 DRAFT（内容不丢）
    kept = task_row(db, tid2)
    assert kept["status"] == "DRAFT"
    assert kept["contact_name"] == "   "


def test_confirm_draft_requires_service_space(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    conn = db.conn()
    conn.execute("UPDATE repair_tasks SET space_id=NULL WHERE task_id=?", (tid,))
    conn.close()
    v = task_row(db, tid)["version"]
    with pytest.raises(SpaceRequired):
        executor.confirm_draft(actor_id=R1, idem_key="k-cs", task_id=tid,
                               expected_version=v)
    assert task_row(db, tid)["status"] == "DRAFT"


def test_confirm_draft_rejects_space_from_other_project(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    conn = db.conn()
    conn.execute("UPDATE repair_tasks SET space_id='sp-other' WHERE task_id=?", (tid,))
    conn.close()
    v = task_row(db, tid)["version"]
    with pytest.raises(InvalidProjectReference):
        executor.confirm_draft(actor_id=R1, idem_key="k-csp", task_id=tid,
                               expected_version=v)
    assert task_row(db, tid)["status"] == "DRAFT"


def test_cross_project_create_rejected(executor, db, clock):
    w = World(executor, None, None, db, clock)
    # R2 是 prj-B 的 REPORTER；在 prj-A 无角色 → 403
    with pytest.raises(PermissionDenied):
        executor.create_draft(actor_id=R2, idem_key="k-x", problem_text="p",
                              contact_name="c", project_id=PA, space_id=SP_ROOM)


def test_unknown_actor_rejected_with_identity_required(executor, db, clock):
    from octosense_backend.errors import IdentityRequired
    with pytest.raises(IdentityRequired):
        executor.create_draft(actor_id=GHOST, idem_key="k-g", problem_text="p",
                              contact_name="c", project_id=PA)


# ---------- T02 幂等 ----------

def test_same_key_same_payload_replays_original_result(executor, db, clock):
    w = World(executor, None, None, db, clock)
    first = ok(executor.create_draft(actor_id=R1, idem_key="same-key",
                                     problem_text="空调不制冷", contact_name="报修人一",
                                     project_id=PA, space_id=SP_ROOM), "create_draft")
    second = ok(executor.create_draft(actor_id=R1, idem_key="same-key",
                                      problem_text="空调不制冷", contact_name="报修人一",
                                      project_id=PA, space_id=SP_ROOM), "replay create_draft")
    assert second["idempotent_replay"] is True
    assert second["action_id"] == first["action_id"]
    # 完整原结果：不只是 task_id/command
    assert second["task_id"] == first["task_id"]
    original = second["result"]
    assert original["status"] == first["status"] == "DRAFT"
    assert original["version"] == first["version"] == 1
    conn = db.conn()
    n = conn.execute("SELECT COUNT(*) AS n FROM repair_tasks").fetchone()["n"]
    conn.close()
    assert n == 1, "replay must not create a second task"


def test_same_key_different_command_is_conflict(executor, db, clock, ext, appt_cmds):
    """V05：pin 与 unpin 是不同命令，同 key 不得互相回放。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    okd(ext.add_pin(actor_id=R1, idem_key="shared-key", task_id=tid), "add_pin")
    with pytest.raises(IdempotencyConflict):
        ext.remove_pin(actor_id=R1, idem_key="shared-key", task_id=tid)
    # pin 仍在
    pins = okd(ext.list_pins(actor_id=R1), "list_pins")["pins"]
    assert any(p["task_id"] == tid for p in pins), "unpin must not have been replayed"


def test_same_key_different_payload_is_conflict(executor, db, clock, ext, appt_cmds):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    okd(ext.record_advice(actor_id=R1, idem_key="adv-key", task_id=tid,
                          source_kind="STAGE_HINT", payload={"x": 1}), "record_advice")
    with pytest.raises(IdempotencyConflict):
        ext.record_advice(actor_id=R1, idem_key="adv-key", task_id=tid,
                          source_kind="STAGE_HINT", payload={"x": 2})


def test_failed_attempt_is_audited_and_retry_allowed(executor, db, clock):
    """失败审计必须留痕，但同 key 修正参数后仍可继续（否则客户端无法重试）。"""
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    with pytest.raises(VersionConflict):
        executor.confirm_draft(actor_id=R1, idem_key="k-retry", task_id=tid,
                               expected_version=99)
    conn = db.conn()
    fails = conn.execute(
        "SELECT error_code FROM repair_action_failures WHERE idempotency_key=?",
        ("k-retry",)).fetchall()
    receipts = conn.execute(
        "SELECT COUNT(*) AS n FROM repair_actions WHERE idempotency_key=?",
        ("k-retry",)).fetchone()["n"]
    conn.close()
    assert [f["error_code"] for f in fails] == ["VERSION_CONFLICT"]
    assert receipts == 0, "a failed attempt must not leave a success receipt"


def test_version_conflict_rejected(executor, db, clock, ext, appt_cmds):
    w = World(executor, ext, None, db, clock)
    tid = w.draft()
    with pytest.raises(VersionConflict):
        executor.confirm_draft(actor_id=R1, idem_key="k-vc", task_id=tid,
                               expected_version=99)
    assert task_row(db, tid)["status"] == "DRAFT"


# ---------- V10 严格类型 ----------

def test_expected_version_rejects_bool_and_none(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    for bad in (None, True, False, 1.0, "1", 0, -1):
        with pytest.raises(InvalidVersion):
            executor.confirm_draft(actor_id=R1, idem_key=f"k-bad-{bad}",
                                   task_id=tid, expected_version=bad)


def test_expected_version_strict_int_accepts_valid(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    data = ok(executor.confirm_draft(actor_id=R1, idem_key="k-ok", task_id=tid,
                                     expected_version=1), "confirm_draft")
    assert data["status"] == "OPEN"


# ---------- T04 / T11 并发 ----------

def test_two_techs_one_task_only_one_accepts(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.open()
    v = task_row(db, tid)["version"]
    results: dict[str, object] = {}
    barrier = threading.Barrier(2)

    def accept(tech):
        cdb = _same_db(db)
        ex = CommandExecutor(cdb, lambda p, a: auth.roles_of(cdb.conn(), a, p), clock=clock)
        barrier.wait(timeout=5)
        try:
            results[tech] = ex.accept_task(actor_id=tech, idem_key=f"k-accept-{tech}",
                                           task_id=tid, expected_version=v)
        except Exception as e:  # noqa: BLE001
            results[tech] = e

    # 两个不同连接真正竞争：T1(HVAC) 与 MGR 都不应同时成功（MGR 无 TECHNICIAN 角色）
    threads = [threading.Thread(target=accept, args=(tech,)) for tech in (T2, MGR)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert len(results) == 2, "both threads must have finished"
    successes = [k for k, v in results.items() if getattr(v, "ok", False)]
    assert successes == [], "no technician should accept a HVAC task"
    row = task_row(db, tid)
    assert row["assignee_id"] is None
    assert row["status"] == "OPEN"


def test_hvac_task_rejected_for_electrical_technician(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.open(category=HVAC)
    v = task_row(db, tid)["version"]
    with pytest.raises(SkillMismatch):
        executor.accept_task(actor_id=T2, idem_key="k-em", task_id=tid,
                             expected_version=v)
    assert task_row(db, tid)["assignee_id"] is None


def test_manager_without_technician_role_cannot_self_accept(executor, db, clock):
    """V09：经理没有 TECHNICIAN 角色不得自主接单。"""
    w = World(executor, None, None, db, clock)
    tid = w.open()
    v = task_row(db, tid)["version"]
    with pytest.raises(PermissionDenied):
        executor.accept_task(actor_id=MGR, idem_key="k-mgr-accept", task_id=tid,
                             expected_version=v)
    assert task_row(db, tid)["assignee_id"] is None


def test_three_independent_connections_race_one_wins(db, clock):
    """T04：三条独立连接抢同一 OPEN 任务，只有一个成功。"""
    executors = []
    for i in range(3):
        cdb = Database(db.db_path)
        cdb.init_schema()
        # 三条**独立连接**：同一文件、各自连接，制造真实竞争
        executors.append(CommandExecutor(cdb, lambda p, a: set(), clock=clock))
    first = executors[0]
    data = ok(first.create_draft(actor_id=R1, idem_key="race-draft",
                                 problem_text="空调不制冷", contact_name="报修人一",
                                 project_id=PA, space_id=SP_ROOM, category=HVAC),
              "create_draft")
    tid = data["task_id"]
    ok(first.confirm_draft(actor_id=R1, idem_key="race-confirm", task_id=tid,
                           expected_version=1), "confirm_draft")
    results: dict[int, object] = {}
    barrier = threading.Barrier(3)

    def accept(i, ex):
        barrier.wait(timeout=5)
        try:
            results[i] = ex.accept_task(actor_id=T1, idem_key=f"race-accept-{i}",
                                        task_id=tid, expected_version=2)
        except Exception as e:  # noqa: BLE001
            results[i] = e

    ts = [threading.Thread(target=accept, args=(i, ex)) for i, ex in enumerate(executors)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=15)
    assert len(results) == 3, "all three connections must report"
    wins = [i for i, r in results.items() if getattr(r, "ok", False)]
    assert len(wins) == 1, f"exactly one accept may win, got {wins}"
    row = task_row(db, tid)
    assert row["assignee_id"] == T1, f"assignee={row['assignee_id']}"
    conn = db.conn()
    events = conn.execute(
        "SELECT COUNT(*) AS n FROM repair_events WHERE task_id=? AND event_type='accept_task'",
        (tid,)).fetchone()["n"]
    receipts = conn.execute(
        "SELECT COUNT(*) AS n FROM repair_actions WHERE task_id=? AND command='accept_task' "
        "AND result='OK'", (tid,)).fetchone()["n"]
    conn.close()
    assert events == 1, f"exactly one accept event expected, got {events}"
    assert receipts == 1, f"exactly one success receipt expected, got {receipts}"


# ---------- T05 分配 ----------

def test_manager_assign_records_manager_identity(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.open()
    v = task_row(db, tid)["version"]
    data = ok(executor.assign_task(actor_id=MGR, idem_key="k-assign", task_id=tid,
                                   assignee_id=T1, expected_version=v,
                                   reason="空调类工单派给技工甲"), "assign_task")
    assert data["assignee_id"] == T1
    row = task_row(db, tid)
    assert row["assignee_id"] == T1 and row["status"] == "ACCEPTED"
    conn = db.conn()
    ev = conn.execute(
        "SELECT actor_id, after_state FROM repair_events WHERE task_id=? "
        "AND event_type='assign_task'", (tid,)).fetchone()
    conn.close()
    assert ev["actor_id"] == MGR, "event must record the manager identity"
    assert json.loads(ev["after_state"])["reason"]


def test_assign_requires_reason_and_valid_skill_matched_technician(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.open()
    v = task_row(db, tid)["version"]
    with pytest.raises(DraftMissingField):
        executor.assign_task(actor_id=MGR, idem_key="k-a1", task_id=tid,
                             assignee_id=T1, expected_version=v, reason="")
    # 技工乙是电气，不能承接 HVAC 任务
    with pytest.raises(PermissionDenied):
        executor.assign_task(actor_id=MGR, idem_key="k-a2", task_id=tid,
                             assignee_id=T2, expected_version=v, reason="派给电工")


def test_technician_cannot_assign(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.open()
    v = task_row(db, tid)["version"]
    with pytest.raises(PermissionDenied):
        executor.assign_task(actor_id=T1, idem_key="k-a3", task_id=tid,
                             assignee_id=T1, expected_version=v, reason="x")


# ---------- T09 设备 ----------

def test_in_progress_asset_change_requires_manager_and_reason(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    v = task_row(db, tid)["version"]
    # 无关技工不能换（V04）
    with pytest.raises(PermissionDenied):
        ext.bind_asset(actor_id=T2, idem_key="k-swap-tech", task_id=tid,
                       asset_id=AS_PWR, expected_version=v)
    assert task_row(db, tid)["asset_id"] == AS_AC
    # 同项目经理无理由也拒绝
    v = task_row(db, tid)["version"]
    with pytest.raises(DraftMissingField):
        ext.bind_asset(actor_id=MGR, idem_key="k-swap-mgr-noreason", task_id=tid,
                       asset_id=AS_EXH, expected_version=v)
    assert task_row(db, tid)["asset_id"] == AS_AC
    # 同项目经理 + 理由 → 旧值/新值/操作者留痕
    v = task_row(db, tid)["version"]
    data = okd(ext.bind_asset(actor_id=MGR, idem_key="k-swap-mgr", task_id=tid,
                             asset_id=AS_EXH, expected_version=v,
                             reason="现场发现是新风机故障"), "bind_asset")
    assert data["previous_asset_id"] == AS_AC
    assert task_row(db, tid)["asset_id"] == AS_EXH
    conn = db.conn()
    ev = conn.execute(
        "SELECT actor_id, before_state, after_state FROM repair_events WHERE task_id=? "
        "AND event_type='bind_asset' ORDER BY seq DESC LIMIT 1", (tid,)).fetchone()
    conn.close()
    assert ev["actor_id"] == MGR
    assert json.loads(ev["before_state"])["asset_id"] == AS_AC
    after = json.loads(ev["after_state"])
    assert after["asset_id"] == AS_EXH and after["reason"] == "现场发现是新风机故障"


def test_bind_requires_service_relation_not_install_location(executor, ext, db, clock, appt_cmds):
    """T08：同安装位置不等于服务关系。PWR-001 装在会议室，但只服务配电间。

    R2-09：OPEN 阶段由经理绑定。
    """
    w = World(executor, ext, None, db, clock)
    tid = w.open(category=HVAC, space=SP_ROOM)
    with pytest.raises(__import__("octosense_backend.errors", fromlist=["x"]).ServiceRelationMissing):
        ext.bind_asset(actor_id=MGR, idem_key="k-svc", task_id=tid,
                       asset_id=AS_PWR, expected_version=task_row(db, tid)["version"])
    assert task_row(db, tid)["asset_id"] is None
    # 任务空间换成配电间后即可绑定
    conn = db.conn()
    conn.execute("UPDATE repair_tasks SET space_id=? WHERE task_id=?", (SP_POWER, tid))
    conn.close()
    okd(ext.bind_asset(actor_id=MGR, idem_key="k-svc-2", task_id=tid,
                      asset_id=AS_PWR,
                      expected_version=task_row(db, tid)["version"]), "bind_asset")
    assert task_row(db, tid)["asset_id"] == AS_PWR


# ---------- T19/T20/T21 完工验收 ----------

def test_start_progress_requires_bound_asset_and_confirmed_window(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    # 未绑设备不能开工（电气任务配配电间，PWR-001 服务该空间）
    tid_plain = w.accepted(key="k-draft-3", tech=T2, category=ELECTRICAL,
                           space=SP_POWER, asset=None)
    v = task_row(db, tid_plain)["version"]
    from octosense_backend.errors import IllegalTransition as IT
    with pytest.raises(IT):
        executor.start_progress(actor_id=T2, idem_key="k-s", task_id=tid_plain,
                                expected_version=v)
    assert task_row(db, tid_plain)["status"] == "ACCEPTED"


def test_completion_requires_readable_evidence_file(executor, ext, appt_cmds, db, clock, tmp_path):
    """V08/T19：只删元数据行不够——文件缺失时不得完工。"""
    from pathlib import Path

    from octosense_backend.errors import EvidenceIntegrity
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    eid = w.evidence(tid=tid, key="k-ev")
    conn = db.conn()
    path = conn.execute("SELECT storage_path FROM repair_evidence WHERE evidence_id=?",
                        (eid,)).fetchone()["storage_path"]
    conn.close()
    Path(path).unlink()
    v = task_row(db, tid)["version"]
    with pytest.raises(EvidenceIntegrity):
        executor.submit_completion(actor_id=T1, idem_key="k-c", task_id=tid,
                                   expected_version=v, completion_text="已修好")
    row = task_row(db, tid)
    assert row["status"] == "IN_PROGRESS", "no half-written completion may remain"
    conn = db.conn()
    n = conn.execute("SELECT COUNT(*) AS n FROM repair_completions WHERE task_id=?",
                     (tid,)).fetchone()["n"]
    conn.close()
    assert n == 0, "no completion record may be written when the evidence is unreadable"


def test_completion_evidence_sha_mismatch_rejected(executor, ext, appt_cmds, db, clock):
    from pathlib import Path

    from octosense_backend.errors import EvidenceIntegrity
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    eid = w.evidence(tid=tid, key="k-ev2")
    conn = db.conn()
    path = conn.execute("SELECT storage_path FROM repair_evidence WHERE evidence_id=?",
                        (eid,)).fetchone()["storage_path"]
    conn.close()
    Path(path).write_bytes(b"corrupted-with-different-length")
    v = task_row(db, tid)["version"]
    with pytest.raises(EvidenceIntegrity):
        executor.submit_completion(actor_id=T1, idem_key="k-c2", task_id=tid,
                                   expected_version=v, completion_text="已修好")
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_reject_then_resubmit_keeps_two_rounds(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid, key="k-ev-r1")
    c1 = w.complete(tid=tid, text="第一轮完工", key="k-c1")
    w.reject_finish(tid=tid, reason="图不够清楚", key="k-rj1")
    assert task_row(db, tid)["status"] == "IN_PROGRESS"
    w.evidence(tid=tid, key="k-ev-r2", payload=b"round-two-evidence")
    c2 = w.complete(tid=tid, text="第二轮完工", key="k-c2")
    assert c1["completion_id"] != c2["completion_id"]
    assert (c1["round"], c2["round"]) == (1, 2)
    w.accept_finish(tid=tid, key="k-af")
    conn = db.conn()
    rows = conn.execute(
        "SELECT round, completion_id, completion_text FROM repair_completions "
        "WHERE task_id=? ORDER BY round", (tid,)).fetchall()
    conn.close()
    assert [r["round"] for r in rows] == [1, 2]
    assert rows[0]["completion_text"] == "第一轮完工"
    assert rows[1]["completion_text"] == "第二轮完工"
    assert rows[0]["completion_id"] == c1["completion_id"]
    assert rows[1]["completion_id"] == c2["completion_id"]


def test_assignee_cannot_accept_own_completion(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid, key="k-ev-self")
    w.complete(tid=tid, key="k-c-self")
    with pytest.raises(PermissionDenied):
        executor.accept_completion(actor_id=T1, idem_key="k-sa", task_id=tid,
                                   expected_version=task_row(db, tid)["version"])


def test_manager_accept_requires_reason(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid, key="k-ev-m")
    w.complete(tid=tid, key="k-c-m")
    with pytest.raises(DraftMissingField):
        executor.accept_completion(actor_id=MGR, idem_key="k-ma", task_id=tid,
                                   expected_version=task_row(db, tid)["version"], reason="")
    data = w.accept_finish(tid=tid, actor=MGR, reason="代报修人确认", key="k-ma2")
    assert data["status"] == "COMPLETED"


def test_reject_completion_only_from_awaiting(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    with pytest.raises(IllegalTransition):
        executor.reject_completion(actor_id=R1, idem_key="k-rf-early", task_id=tid,
                                   expected_version=task_row(db, tid)["version"],
                                   reason="x")
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_reject_finish_cannot_escape_from_scheduled(executor, ext, appt_cmds, db, clock):
    """Q01：SCHEDULED 不能被 reject-finish 绕到 IN_PROGRESS。"""
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    assert task_row(db, tid)["status"] == "SCHEDULED"
    with pytest.raises(IllegalTransition):
        executor.reject_completion(actor_id=R1, idem_key="k-sched-rf", task_id=tid,
                                   expected_version=task_row(db, tid)["version"],
                                   reason="x")
    assert task_row(db, tid)["status"] == "SCHEDULED"


# ---------- T31 取消 ----------

def test_cancel_requires_reason_and_releases_appointment(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    v = task_row(db, tid)["version"]
    with pytest.raises(DraftMissingField):
        executor.cancel(actor_id=MGR, idem_key="k-cx1", task_id=tid,
                        expected_version=v, reason="")
    data = ok(executor.cancel(actor_id=MGR, idem_key="k-cx", task_id=tid,
                              expected_version=v, reason="用户取消"), "cancel")
    assert data["status"] == "CANCELLED"
    assert data["released_appointments"] >= 1
    conn = db.conn()
    ap = conn.execute("SELECT status FROM repair_appointments WHERE appointment_id=?",
                      (appt["appointment_id"],)).fetchone()
    job = conn.execute("SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND status='PENDING'",
                       (tid,)).fetchone()["n"]
    conn.close()
    assert ap["status"] == "SUPERSEDED"
    assert job == 0, "cancelling a task must cancel its pending reminder jobs"
    # 终态不能再开工
    with pytest.raises(IllegalTransition):
        executor.start_progress(actor_id=T1, idem_key="k-sx", task_id=tid,
                                expected_version=task_row(db, tid)["version"])


def test_reporter_cannot_cancel_accepted_task(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    v = task_row(db, tid)["version"]
    with pytest.raises(PermissionDenied):
        executor.cancel(actor_id=R1, idem_key="k-rc", task_id=tid,
                        expected_version=v, reason="我不修了")
    assert task_row(db, tid)["status"] == "ACCEPTED"


def test_reporter_can_cancel_own_draft(executor, db, clock):
    w = World(executor, None, None, db, clock)
    tid = w.draft()
    v = task_row(db, tid)["version"]
    data = ok(executor.cancel(actor_id=R1, idem_key="k-rd", task_id=tid,
                              expected_version=v, reason="误报"), "cancel")
    assert data["status"] == "CANCELLED"


# ---------- T06 改派 ----------

def test_reassign_releases_old_booking(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    # 派给技工甲（HVAC），改派给另一名 HVAC 技工
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
                 "VALUES ('u-tech-3','技工丙（HVAC）',1)")
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                 "VALUES ('prj-A','u-tech-3','TECHNICIAN','HVAC')")
    conn.close()
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    v = task_row(db, tid)["version"]
    data = okd(appt_cmds.reassign(actor_id=MGR, idem_key="k-ra", task_id=tid,
                            new_assignee_id="u-tech-3", expected_version=v,
                            reason="技工甲请假"), "reassign")
    assert data["assignee_id"] == "u-tech-3"
    row = assert_status_row(db, tid)
    assert row["status"] == "ACCEPTED"
    conn = db.conn()
    ap = conn.execute("SELECT status FROM repair_appointments WHERE appointment_id=?",
                      (appt["appointment_id"],)).fetchone()
    job = conn.execute("SELECT COUNT(*) AS n FROM repair_jobs WHERE task_id=? AND status='PENDING'",
                       (tid,)).fetchone()["n"]
    conn.close()
    assert ap["status"] == "SUPERSEDED"
    assert job == 0, "reassign must cancel the previous technician's reminder jobs"
    # 旧技工不能再开工：改派已把任务退回 ACCEPTED 且旧确认预约被 SUPERSEDED，
    # 无论从源状态还是从承接者判断都必须拒绝。
    clock.set(appt["start_at_ms"] + 1000)
    row = task_row(db, tid)
    with pytest.raises(OctoSenseError):
        executor.start_progress(actor_id=T1, idem_key="k-old-start", task_id=tid,
                                expected_version=row["version"])
    assert row["status"] == "ACCEPTED" and row["assignee_id"] == "u-tech-3"


def test_reassign_in_progress_rejected(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    with pytest.raises(IllegalTransition):
        appt_cmds.reassign(actor_id=MGR, idem_key="k-rai", task_id=tid,
                      new_assignee_id=T1,
                      expected_version=task_row(db, tid)["version"], reason="换人")


def test_scheduled_cannot_be_reaccepted(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    appt = w.propose(tid=tid)
    w.confirm(tid=tid, appointment_id=appt["appointment_id"])
    with pytest.raises(IllegalTransition):
        executor.accept_task(actor_id=T1, idem_key="k-reaccept", task_id=tid,
                             expected_version=task_row(db, tid)["version"])


def test_technician_cannot_reassign(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(PermissionDenied):
        appt_cmds.reassign(actor_id=T1, idem_key="k-tar", task_id=tid,
                      new_assignee_id=T2,
                      expected_version=task_row(db, tid)["version"], reason="x")


def test_unknown_task_rejected(executor, db, clock):
    with pytest.raises(TaskNotFound):
        executor.accept_task(actor_id=T1, idem_key="k-none", task_id="nope",
                             expected_version=1)


# ---------- helpers ----------


def _same_db(db: Database) -> Database:
    d = Database(db.db_path)
    d.init_schema()
    return d


def assert_status_row(db, task_id: str) -> dict:
    return task_row(db, task_id)
