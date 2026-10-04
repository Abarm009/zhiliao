"""扩展命令测试：设备身份、证据附件、收藏、处置建议、列表视图与授权。

对应 T07/T08/T09/T18/T19/T22/T30/T33–T35 与 V02/V03/V04/V07/V08/V09/V10。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from octosense_backend import authorization as auth
from octosense_backend.errors import (
    AssetArchived,
    AssetNotFound,
    DraftMissingField,
    EvidenceIntegrity,
    EvidenceNotFound,
    EvidenceQuarantined,
    EvidenceTooLarge,
    IllegalTransition,
    InvalidKind,
    InvalidProjectReference,
    InvalidRoleFilter,
    InvalidVersion,
    OctoSenseError,
    PermissionDenied,
    ServiceRelationMissing,
    TaskNotFound,
    VersionConflict,
)

from world import (
    AS_AC, AS_EXH, AS_PWR, ELECTRICAL, GHOST, HVAC, MGR, PA, PB, R1, R2, SP_MECH,
    SP_POWER, SP_ROOM, T1, T2, World, ok, okd, task_row,
)


# ============ T07 设备解析 ============

def test_match_assets_by_code(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    data = okd(ext.match_assets_by_code(actor_id=R1, project_id=PA, code="AC-001"),
               "match_assets_by_code")
    assert data["resolved_by"] == "asset_code"
    assert any(m["asset_code"] == "AC-001" for m in data["matches"])


def test_asset_prefix_resolves_stable_asset_id(executor, ext, db, clock):
    """V07/Q06：asset:<asset_id> 必须解析到稳定 ID，不是 asset_code。"""
    w = World(executor, ext, None, db, clock)
    w.open()
    by_code = okd(ext.match_assets_by_code(actor_id=R1, project_id=PA, code="AC-001"),
                  "match by code")
    by_id = okd(ext.match_assets_by_code(actor_id=R1, project_id=PA, code="asset:as-a-1"),
                "match by asset id")
    assert by_id["resolved_by"] == "asset_id"
    assert by_id["matches"][0]["asset_id"] == "as-a-1"
    assert {m["asset_id"] for m in by_code["matches"]} == {"as-a-1"}


def test_asset_prefix_with_code_rejected(executor, ext, db, clock):
    """V07：asset:AC-001 是错误载荷——asset: 后面必须是 asset_id。"""
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(AssetNotFound):
        ext.match_assets_by_code(actor_id=R1, project_id=PA, code="asset:AC-001")


def test_asset_prefix_cross_project_rejected(executor, ext, db, clock):
    """R1 在 prj-B 无角色 → 403；跨项目 asset_id 不得借 asset: 前缀读取。"""
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(PermissionDenied):
        ext.match_assets_by_code(actor_id=R1, project_id=PB, code="asset:as-a-1")


def test_match_assets_unknown_code_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(AssetNotFound):
        ext.match_assets_by_code(actor_id=R1, project_id=PA, code="NOPE-999")


def test_match_assets_other_project_not_returned(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(AssetNotFound):
        ext.match_assets_by_code(actor_id=R2, project_id=PB, code="AC-001")


def test_archived_asset_not_returned(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    conn = db.conn()
    conn.execute("UPDATE repair_assets SET active=0 WHERE asset_id=?", (AS_AC,))
    conn.close()
    with pytest.raises(AssetArchived):
        ext.match_assets_by_code(actor_id=R1, project_id=PA, code="asset:as-a-1")


def test_asset_detail_shows_location_and_service_relations(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    data = okd(ext.get_asset_detail(actor_id=R1, asset_id=AS_AC, project_id=PA),
               "get_asset_detail")
    assert data["asset"]["asset_code"] == "AC-001"
    assert SP_ROOM in data["services_space_ids"]
    assert SP_MECH in data["installed_at_space_ids"]
    assert SP_ROOM not in data["installed_at_space_ids"], "安装位置不等于服务空间"


# ============ T08/T09 绑定 ============

def test_bind_asset_success(executor, ext, db, clock):
    """R2-09：OPEN 阶段绑设备由经理完成。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    data = w.bind(tid=tid, actor=MGR, asset_id=AS_AC)
    assert data["asset_id"] == AS_AC
    assert task_row(db, tid)["asset_id"] == AS_AC


def test_bind_asset_cross_project_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    conn = db.conn()
    conn.execute("INSERT INTO repair_assets (asset_id, project_id, asset_code, display_name, "
                 "source, active) VALUES ('as-other-1','prj-B','OTHER-001','他项目设备','DEMO',1)")
    conn.close()
    with pytest.raises(InvalidProjectReference):
        ext.bind_asset(actor_id=R1, idem_key="b2", task_id=tid, asset_id="as-other-1",
                       expected_version=task_row(db, tid)["version"])


def test_bind_asset_archived_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    conn = db.conn()
    conn.execute("UPDATE repair_assets SET active=0 WHERE asset_id=?", (AS_AC,))
    conn.close()
    with pytest.raises(AssetArchived):
        ext.bind_asset(actor_id=R1, idem_key="b3", task_id=tid, asset_id=AS_AC,
                       expected_version=task_row(db, tid)["version"])
    assert task_row(db, tid)["asset_id"] is None


def test_bind_asset_ghost_rejected(executor, ext, db, clock):
    """ghost（未注册主体）不可绑定，且与 403 区分。"""
    from octosense_backend.errors import IdentityRequired
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(IdentityRequired):
        ext.bind_asset(actor_id=GHOST, idem_key="b-g", task_id=tid, asset_id=AS_AC,
                       expected_version=task_row(db, tid)["version"])
    assert task_row(db, tid)["asset_id"] is None


def test_bind_same_install_location_without_service_relation_rejected(executor, ext, db, clock):
    """T08：PWR-001 安装在会议室，但只服务配电间——不能因同安装位置误绑。

    R2-09：OPEN 阶段由经理绑定。
    """
    w = World(executor, ext, None, db, clock)
    tid = w.open(category=HVAC, space=SP_ROOM)
    with pytest.raises(ServiceRelationMissing):
        ext.bind_asset(actor_id=MGR, idem_key="b-svc", task_id=tid, asset_id=AS_PWR,
                       expected_version=task_row(db, tid)["version"])
    assert task_row(db, tid)["asset_id"] is None


def test_bind_without_confirmed_space_rejected(executor, ext, db, clock):
    """设备绑定必须挂在已确认的服务空间上。"""
    w = World(executor, ext, None, db, clock)
    tid = w.draft()
    conn = db.conn()
    conn.execute("UPDATE repair_tasks SET space_id=NULL WHERE task_id=?", (tid,))
    conn.close()
    from octosense_backend.errors import SpaceRequired
    with pytest.raises(SpaceRequired):
        ext.bind_asset(actor_id=R1, idem_key="b-sp", task_id=tid, asset_id=AS_AC,
                       expected_version=task_row(db, tid)["version"])


def test_bind_requires_current_assignee_or_manager(executor, ext, db, clock):
    """OPEN 阶段非经理不能绑定。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(PermissionDenied):
        ext.bind_asset(actor_id=T2, idem_key="b-t2", task_id=tid, asset_id=AS_PWR,
                       expected_version=task_row(db, tid)["version"])


def test_unbind_requires_reason_and_keeps_trace(executor, ext, db, clock):
    """R2-09：OPEN 阶段解绑由经理完成。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    w.bind(tid=tid, actor=MGR, asset_id=AS_AC)
    with pytest.raises(DraftMissingField):
        ext.unbind_asset(actor_id=MGR, idem_key="u0", task_id=tid,
                         expected_version=task_row(db, tid)["version"], reason="")
    data = okd(ext.unbind_asset(actor_id=MGR, idem_key="u1", task_id=tid,
                                expected_version=task_row(db, tid)["version"],
                                reason="选错设备"), "unbind_asset")
    assert data["previous_asset_id"] == AS_AC
    assert task_row(db, tid)["asset_id"] is None


def test_unbind_during_in_progress_by_tech_rejected(executor, ext, db, clock, appt_cmds):
    """T09/V04：IN_PROGRESS 只能经理带理由换设备。"""
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    with pytest.raises(PermissionDenied):
        ext.unbind_asset(actor_id=T1, idem_key="u2", task_id=tid,
                         expected_version=task_row(db, tid)["version"], reason="换设备")
    data = okd(ext.unbind_asset(actor_id=MGR, idem_key="u3", task_id=tid,
                                expected_version=task_row(db, tid)["version"],
                                reason="现场设备登记错误"), "unbind_asset")
    assert data["previous_asset_id"] == AS_AC
    assert task_row(db, tid)["asset_id"] is None


def test_bind_in_terminal_state_rejected(executor, ext, appt_cmds, db, clock):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    w.evidence(tid=tid, key="k-ev-final")
    w.complete(tid=tid, key="k-c-final")
    w.accept_finish(tid=tid, key="k-af-final")
    with pytest.raises(IllegalTransition):
        ext.bind_asset(actor_id=MGR, idem_key="b-final", task_id=tid, asset_id=AS_EXH,
                       expected_version=task_row(db, tid)["version"], reason="补登设备")


def test_bind_version_conflict(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(VersionConflict):
        ext.bind_asset(actor_id=R1, idem_key="b-vc", task_id=tid, asset_id=AS_AC,
                       expected_version=99)


def test_bind_rejects_invalid_version_type(executor, ext, db, clock):
    """V10：领域层同样拒绝 bool/None。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    for bad in (None, True, "1", 1.5):
        with pytest.raises(InvalidVersion):
            ext.bind_asset(actor_id=R1, idem_key=f"b-bad-{bad}", task_id=tid,
                           asset_id=AS_AC, expected_version=bad)


# ============ T19/T22 证据 ============

def test_upload_evidence_basic(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, filename="site.png", mime="image/png",
                     payload=b"png-bytes-0123456789")
    conn = db.conn()
    row = conn.execute("SELECT * FROM repair_evidence WHERE evidence_id=?", (eid,)).fetchone()
    conn.close()
    assert row["status"] == "READY"
    assert Path(row["storage_path"]).exists()
    assert row["sha256"]


def test_upload_evidence_too_large(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    ext.max_evidence_bytes = 16
    with pytest.raises(EvidenceTooLarge):
        ext.upload_evidence(actor_id=R1, idem_key="ev-big", task_id=tid,
                            filename="big.bin", mime_type="application/octet-stream",
                            payload=b"x" * 32, expected_version=task_row(db, tid)["version"])


def test_upload_evidence_rejects_directory_traversal(executor, ext, db, clock):
    """文件名必须规范化，禁止目录穿越。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, filename="../../etc/passwd", mime="text/plain")
    conn = db.conn()
    row = conn.execute("SELECT storage_path FROM repair_evidence WHERE evidence_id=?",
                       (eid,)).fetchone()
    conn.close()
    assert str(ext.evidence_root) in row["storage_path"]
    assert "/etc/" not in row["storage_path"]
    assert Path(row["storage_path"]).exists()


def test_upload_evidence_list_download(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, payload=b"download-me-please")
    listing = okd(ext.list_evidence(actor_id=R1, task_id=tid), "list_evidence")
    assert [e["evidence_id"] for e in listing["evidence"]] == [eid]
    data = okd(ext.download_evidence(actor_id=R1, task_id=tid, evidence_id=eid),
               "download_evidence")
    assert data["payload"] == b"download-me-please"
    assert data["byte_size"] == len(b"download-me-please")


def test_upload_evidence_quarantine_blocks_download(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, payload=b"will-be-quarantined")
    okd(ext.quarantine_evidence(actor_id=MGR, idem_key="q1", task_id=tid, evidence_id=eid,
                                expected_version=task_row(db, tid)["version"],
                                reason="疑似非现场照片"), "quarantine_evidence")
    with pytest.raises(EvidenceQuarantined):
        ext.download_evidence(actor_id=R1, task_id=tid, evidence_id=eid)
    conn = db.conn()
    row = conn.execute("SELECT status FROM repair_evidence WHERE evidence_id=?",
                       (eid,)).fetchone()
    conn.close()
    assert row["status"] == "QUARANTINED"


def test_quarantine_nonexistent_evidence_404(executor, ext, db, clock):
    """N13：隔离不存在的 evidence 必须 404，不能返回成功。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(EvidenceNotFound):
        ext.quarantine_evidence(actor_id=MGR, idem_key="q-none", task_id=tid,
                                evidence_id="no-such-evidence",
                                expected_version=task_row(db, tid)["version"], reason="x")


def test_quarantine_requires_reason_and_authority(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, payload=b"auth-check")
    with pytest.raises(DraftMissingField):
        ext.quarantine_evidence(actor_id=R1, idem_key="q-nr", task_id=tid, evidence_id=eid,
                                expected_version=task_row(db, tid)["version"], reason="")
    # 技工不是报修人也不是经理 → 403
    with pytest.raises(PermissionDenied):
        ext.quarantine_evidence(actor_id=T1, idem_key="q-na", task_id=tid, evidence_id=eid,
                                expected_version=task_row(db, tid)["version"], reason="x")


def test_download_evidence_of_other_task_not_found(executor, ext, db, clock):
    """V08：其他任务的附件不能拿来当本任务证据。"""
    w = World(executor, ext, None, db, clock)
    tid_a = w.open()
    tid_b = w.open(key="k-draft-b", category=ELECTRICAL, space=SP_POWER)
    eid_a = w.evidence(tid=tid_a, actor=MGR, payload=b"task-a-evidence")
    with pytest.raises(EvidenceNotFound):
        ext.download_evidence(actor_id=R1, task_id=tid_b, evidence_id=eid_a)


def test_missing_evidence_file_reported(executor, ext, db, clock):
    """V08：文件缺失时下载给出明确错误，而不是伪造空内容。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    eid = w.evidence(tid=tid, actor=MGR, payload=b"will-vanish")
    conn = db.conn()
    path = conn.execute("SELECT storage_path FROM repair_evidence WHERE evidence_id=?",
                        (eid,)).fetchone()["storage_path"]
    conn.close()
    Path(path).unlink()
    with pytest.raises(EvidenceNotFound):
        ext.download_evidence(actor_id=R1, task_id=tid, evidence_id=eid)


# ============ T30 收藏 ============

def test_pin_and_list_and_unpin(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    okd(ext.add_pin(actor_id=R1, idem_key="p1", task_id=tid), "add_pin")
    pins = okd(ext.list_pins(actor_id=R1), "list_pins")["pins"]
    assert [p["task_id"] for p in pins] == [tid]
    assert pins[0]["task_version"] == task_row(db, tid)["version"]
    okd(ext.remove_pin(actor_id=R1, idem_key="p2", task_id=tid), "remove_pin")
    assert okd(ext.list_pins(actor_id=R1), "list_pins")["pins"] == []


def test_pin_other_user_not_visible(executor, ext, db, clock):
    """T30：收藏互不影响，且 task.version 不因收藏改变。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    v_before = task_row(db, tid)["version"]
    okd(ext.add_pin(actor_id=R1, idem_key="p3", task_id=tid), "add_pin")
    assert task_row(db, tid)["version"] == v_before
    # R2 不是本项目成员 → 看不见该任务，也不能收藏
    with pytest.raises(OctoSenseError):
        ext.add_pin(actor_id=R2, idem_key="p4", task_id=tid)
    assert okd(ext.list_pins(actor_id=R2), "list_pins")["pins"] == []


def test_pin_unpin_same_key_conflict(executor, ext, db, clock):
    """V05：pin 与 unpin 是不同命令，同 key 不得互相回放。"""
    from octosense_backend.errors import IdempotencyConflict
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    okd(ext.add_pin(actor_id=R1, idem_key="shared", task_id=tid), "add_pin")
    with pytest.raises(IdempotencyConflict):
        ext.remove_pin(actor_id=R1, idem_key="shared", task_id=tid)
    pins = okd(ext.list_pins(actor_id=R1), "list_pins")["pins"]
    assert any(p["task_id"] == tid for p in pins), "unpin 不得借 pin 的回放生效"


def test_pin_replay_same_key_same_command(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    first = okd(ext.add_pin(actor_id=R1, idem_key="p-replay", task_id=tid), "add_pin")
    second = okd(ext.add_pin(actor_id=R1, idem_key="p-replay", task_id=tid), "add_pin replay")
    assert second["idempotent_replay"] is True
    assert second["action_id"] == first["action_id"]
    assert second["result"] == first


# ============ T18 列表与授权 ============

def test_list_tasks_reporter_only_own(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    mine = w.open()
    other = w.open(key="k-draft-other", reporter=R1)  # 同报修人；再造一个他人任务
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
                 "VALUES ('prj-A','u-reporter-2','REPORTER')")
    conn.close()
    theirs = w.open(key="k-draft-theirs", reporter=R2)
    data = okd(ext.list_tasks(actor_id=R1, project_id=PA), "list_tasks")
    ids = {t["task_id"] for t in data["tasks"]}
    assert mine in ids and other in ids
    assert theirs not in ids, "报修人不得看到他人任务"
    assert all(t["reporter_id"] == R1 for t in data["tasks"])


def test_list_tasks_technician_sees_open_skill_matched_and_own(executor, ext, db, clock):
    """V03：技工可见 = 本人承接 ∪ 本项目技能匹配的 OPEN。"""
    w = World(executor, ext, None, db, clock)
    my_task = w.accepted()                                    # T1 承接
    hvac_open = w.open(key="k-hvac-open")                     # 待接单，HVAC
    electrical_open = w.open(key="k-elec-open", category=ELECTRICAL, space=SP_POWER)
    data = okd(ext.list_tasks(actor_id=T1, project_id=PA), "list_tasks")
    ids = {t["task_id"] for t in data["tasks"]}
    assert my_task in ids, "承接任务必须可见"
    assert hvac_open in ids, "技能匹配的 OPEN 待接单必须可见"
    assert electrical_open not in ids, "技能不匹配的 OPEN 不得可见"


def test_list_tasks_technician_open_contact_masked(executor, ext, db, clock):
    """V02：接单前的 OPEN 任务对技工脱敏 contact_info。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open(contact_info="手机 13800000000")
    data = okd(ext.list_tasks(actor_id=T1, project_id=PA), "list_tasks")
    row = [t for t in data["tasks"] if t["task_id"] == tid][0]
    assert row["contact_info"] is None, "接单前不得泄露敏感联系方式"


def test_list_tasks_role_filter_cannot_escalate(executor, ext, db, clock):
    """V02：role=MANAGER 不能把报修人的可见范围扩大。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
                 "VALUES ('prj-A','u-reporter-2','REPORTER')")
    conn.close()
    other = w.open(key="k-draft-x", reporter=R2)
    base = okd(ext.list_tasks(actor_id=R2, project_id=PA), "list_tasks")
    assert other in {t["task_id"] for t in base["tasks"]}
    assert tid not in {t["task_id"] for t in base["tasks"]}
    with pytest.raises(InvalidRoleFilter):
        ext.list_tasks(actor_id=R2, project_id=PA, role_filter="MANAGER")
    # 缩小到自己的角色是允许的
    narrowed = okd(ext.list_tasks(actor_id=R2, project_id=PA, role_filter="REPORTER"),
                   "list_tasks narrowed")
    assert other in {t["task_id"] for t in narrowed["tasks"]}


def test_list_tasks_unknown_role_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(InvalidRoleFilter):
        ext.list_tasks(actor_id=R1, project_id=PA, role_filter="SUPERUSER")


def test_list_tasks_non_member_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    w.open()
    with pytest.raises(PermissionDenied):
        ext.list_tasks(actor_id=GHOST, project_id=PA)


def test_list_tasks_status_filter(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    open_task = w.open()
    acc_task = w.accepted(key="k-draft-acc")
    data = okd(ext.list_tasks(actor_id=R1, project_id=PA, status_filter="OPEN"),
               "list_tasks status")
    ids = {t["task_id"] for t in data["tasks"]}
    assert open_task in ids and acc_task not in ids


def test_detail_invisible_task_not_found(executor, ext, db, clock):
    """T18/V02：无权 task_id 一律 404，不可枚举。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
                 "VALUES ('prj-A','u-reporter-2','REPORTER')")
    conn.close()
    # 通过对象可见性判断：他人任务对 R2 不可见
    conn = db.conn()
    row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (tid,)).fetchone()
    assert auth.task_visible(conn, R2, row) is False
    conn.close()
    with pytest.raises(TaskNotFound):
        ext.list_evidence(actor_id=R2, task_id=tid)


def test_history_advice_no_asset(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    data = okd(ext.get_history_advice(actor_id=R1, task_id=tid), "get_history_advice")
    assert data["asset_id"] is None and data["history"] == []


def test_history_advice_with_asset(executor, ext, db, clock):
    """R2-09：OPEN 阶段绑设备由经理完成。"""
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    w.bind(tid=tid, actor=MGR, asset_id=AS_AC)
    data = okd(ext.get_history_advice(actor_id=R1, task_id=tid), "get_history_advice")
    assert data["asset_id"] == AS_AC
    assert data["asset_code"] == "AC-001"


def test_history_advice_cross_project_asset_rejected(executor, ext, db, clock):
    """N04：asset_id 不能用于跨项目读取。"""
    w = World(executor, ext, None, db, clock)
    conn = db.conn()
    conn.execute("INSERT INTO repair_projects (project_id, name, code, created_at_ms) "
                 "VALUES ('prj-C','项目C','PC',0)")
    conn.execute("INSERT INTO repair_spaces (space_id, project_id, name) "
                 "VALUES ('sp-c-1','prj-C','C 空间')")
    conn.execute("INSERT INTO repair_assets (asset_id, project_id, asset_code, display_name, "
                 "source, active) VALUES ('as-c-1','prj-C','XC-001','C 项目设备','DEMO',1)")
    conn.execute("INSERT INTO repair_roles (project_id, user_id, role) "
                 "VALUES ('prj-C','u-reporter-1','REPORTER')")
    conn.close()
    tid = w.open(project="prj-C", space="sp-c-1")
    with pytest.raises(OctoSenseError):
        ext.get_history_advice(actor_id=R1, task_id=tid, asset_id=AS_AC)


def test_history_advice_hides_unrelated_tasks(executor, ext, db, clock):
    """T33：非 manager 只能看到与本人有关系的同设备历史。

    R2-09：OPEN 阶段绑设备由经理完成。
    """
    w = World(executor, ext, None, db, clock)
    conn = db.conn()
    conn.execute("INSERT OR IGNORE INTO repair_roles (project_id, user_id, role) "
                 "VALUES ('prj-A','u-reporter-2','REPORTER')")
    conn.close()
    tid_a = w.open()
    w.bind(tid=tid_a, actor=MGR, asset_id=AS_AC, key="k-bind-a")
    tid_b = w.open(key="k-draft-hist-b", reporter=R2)
    w.bind(tid=tid_b, actor=MGR, asset_id=AS_AC, key="k-bind-b")
    data = okd(ext.get_history_advice(actor_id=R1, task_id=tid_a), "get_history_advice")
    hist_ids = {h["task_id"] for h in data["history"]}
    assert tid_b not in hist_ids, "他人同设备任务不得泄漏给非经理"


def test_record_advice_with_auth_and_idem(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    first = okd(ext.record_advice(actor_id=R1, idem_key="a1", task_id=tid,
                                  source_kind="DEVICE_HISTORY", payload={"hits": 2}),
                "record_advice")
    second = okd(ext.record_advice(actor_id=R1, idem_key="a1", task_id=tid,
                                   source_kind="DEVICE_HISTORY", payload={"hits": 2}),
                 "record_advice replay")
    assert second["idempotent_replay"] is True
    assert second["action_id"] == first["action_id"]
    assert second["result"] == first


def test_record_advice_invalid_kind(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(InvalidKind):
        ext.record_advice(actor_id=R1, idem_key="a-bad", task_id=tid,
                          source_kind="MADE_UP", payload={})


def test_record_advice_invisible_task_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.open()
    with pytest.raises(TaskNotFound):
        ext.record_advice(actor_id=GHOST, idem_key="a-g", task_id=tid,
                          source_kind="STAGE_HINT", payload={})


# ============ 处置记录 ============

def test_record_progress_in_progress(executor, ext, db, clock, appt_cmds):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    data = okd(ext.record_progress(actor_id=T1, idem_key="rp1", task_id=tid,
                                   note="到场检查压缩机", kind="INSPECTION",
                                   expected_version=task_row(db, tid)["version"]),
               "record_progress")
    assert data["kind"] == "INSPECTION"
    conn = db.conn()
    ev = conn.execute("SELECT after_state FROM repair_events WHERE task_id=? "
                      "AND event_type='record_progress'", (tid,)).fetchone()
    conn.close()
    assert json.loads(ev["after_state"])["note"] == "到场检查压缩机"
    assert task_row(db, tid)["status"] == "IN_PROGRESS"


def test_record_progress_not_in_progress_rejected(executor, ext, db, clock):
    w = World(executor, ext, None, db, clock)
    tid = w.accepted()
    with pytest.raises(IllegalTransition):
        ext.record_progress(actor_id=T1, idem_key="rp2", task_id=tid, note="x", kind="NOTE",
                            expected_version=task_row(db, tid)["version"])


def test_record_progress_other_tech_rejected(executor, ext, db, clock, appt_cmds):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    with pytest.raises(PermissionDenied):
        ext.record_progress(actor_id=T2, idem_key="rp3", task_id=tid, note="x", kind="NOTE",
                            expected_version=task_row(db, tid)["version"])


def test_record_progress_invalid_kind(executor, ext, db, clock, appt_cmds):
    w = World(executor, ext, None, db, clock)
    tid, _, _ = w.in_progress()
    # P0 不提供任意百分比进度：kind 必须是确定的处置子类
    with pytest.raises(InvalidKind):
        ext.record_progress(actor_id=T1, idem_key="rp4", task_id=tid, note="x",
                            kind="PERCENT_80", expected_version=task_row(db, tid)["version"])
