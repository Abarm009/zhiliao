"""扩展命令测试：覆盖 L3-L7 的剩余 P0 用例。

修复后版本：bind asset + 注入时钟。
"""
from __future__ import annotations

import time

import pytest

from octosense_backend.errors import (
    AssetArchived,
    AssetNotFound,
    EvidenceTooLarge,
    IllegalTransition,
    InvalidProjectReference,
    PermissionDenied,
    VersionConflict,
)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _setup_accepted(executor, fixtures):
    """建任务并 ACCEPTED。返回 (project, reporter, tech, task_id, version=4)。"""
    p = fixtures["project_a"]
    r = fixtures["reporter_1"]
    t = fixtures["tech_1"]
    res = executor.create_draft(actor_id=r, idem_key="c", problem_text="P",
                                contact_name="C", project_id=p)
    tid = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o", task_id=tid, expected_version=1)
    executor.accept_task(actor_id=t, idem_key="a", task_id=tid, expected_version=2)
    return p, r, t, tid, 3


# ============ T07 ============

def test_match_assets_by_code(executor, ext, fixtures):
    """T07：按编码查到设备。"""
    _, r, _, _, _ = _setup_accepted(executor, fixtures)
    data = ext.match_assets_by_code(actor_id=r, project_id=fixtures["project_a"], code="AC-001")
    assert len(data["matches"]) >= 1
    assert any(m["asset_code"] == "AC-001" for m in data["matches"])


def test_match_assets_by_asset_prefix(executor, ext, fixtures):
    """T07：asset: 前缀解析到相同设备。"""
    _, r, _, _, _ = _setup_accepted(executor, fixtures)
    a = ext.match_assets_by_code(actor_id=r, project_id=fixtures["project_a"], code="AC-001")
    b = ext.match_assets_by_code(actor_id=r, project_id=fixtures["project_a"], code="asset:AC-001")
    assert {m["asset_id"] for m in a["matches"]} == {m["asset_id"] for m in b["matches"]}


def test_match_assets_unknown_code_rejected(executor, ext, fixtures):
    _, r, _, _, _ = _setup_accepted(executor, fixtures)
    with pytest.raises(AssetNotFound):
        ext.match_assets_by_code(actor_id=r, project_id=fixtures["project_a"], code="NOPE-999")


def test_match_assets_other_project_not_returned(executor, ext, fixtures):
    """T07：其他项目编码不返回。"""
    _, _, _, _, _ = _setup_accepted(executor, fixtures)
    r2 = fixtures["reporter_2"]
    with pytest.raises(AssetNotFound):
        ext.match_assets_by_code(actor_id=r2, project_id=fixtures["project_b"], code="AC-001")


def test_bind_asset_success(executor, ext, fixtures):
    """T07/T08：绑定设备。"""
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    asset_id = fixtures["asset_a1"]
    data = ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                          asset_id=asset_id, expected_version=ver)
    assert data["asset_id"] == asset_id
    assert data["version"] == ver + 1


def test_bind_asset_cross_project_rejected(executor, ext, fixtures):
    """T07：其他项目设备拒绝。"""
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    with db_conn(ext.db) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO repair_assets (asset_id, project_id, asset_code, display_name, source, active) "
            "VALUES (?,?,?,?, 'DEMO', 1)",
            ("as-other-1", fixtures["project_b"], "OTHER-001", "他项目设备"),
        )
    with pytest.raises(InvalidProjectReference):
        ext.bind_asset(actor_id=r, idem_key="b2", task_id=tid,
                       asset_id="as-other-1", expected_version=ver)


def test_bind_asset_archived_rejected(executor, ext, fixtures):
    """T07：归档设备拒绝。"""
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    with db_conn(ext.db) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE repair_assets SET active=0 WHERE asset_id=?", (fixtures["asset_a1"],))
    with pytest.raises(AssetArchived):
        ext.bind_asset(actor_id=r, idem_key="b3", task_id=tid,
                       asset_id=fixtures["asset_a1"], expected_version=ver)


def test_bind_asset_ghost_rejected(executor, ext, fixtures):
    """R-P1-3/N01：ghost 不可绑定。"""
    _, _, _, tid, ver = _setup_accepted(executor, fixtures)
    with pytest.raises(PermissionDenied):
        ext.bind_asset(actor_id="u-ghost", idem_key="b-g", task_id=tid,
                       asset_id=fixtures["asset_a1"], expected_version=ver)


# ============ T09 ============

def test_unbind_during_in_progress_by_tech_rejected(executor, ext, appt_cmds, fixtures, clock):
    """T09：IN_PROGRESS 技工不能自行换设备；经理可带 reason。"""
    p, r, t, tid, ver = _setup_accepted(executor, fixtures)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=ver)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=ver + 1)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=ver + 2, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=ver + 3)
    with pytest.raises(PermissionDenied):
        ext.unbind_asset(actor_id=t, idem_key="u", task_id=tid,
                         expected_version=ver + 4, reason="改")
    data = ext.unbind_asset(actor_id=fixtures["manager"], idem_key="u2", task_id=tid,
                            expected_version=ver + 4, reason="原设备错了")
    assert data["asset_id"] is None


# ============ T19 ============

def test_upload_evidence_basic(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    payload = b"site-note-bytes-18-by"
    data = ext.upload_evidence(actor_id=r, idem_key="u", task_id=tid,
                               filename="note.txt", mime_type="text/plain",
                               payload=payload,
                               expected_version=ver)
    assert data["byte_size"] == len(payload)
    assert data["sha256"]


def test_upload_evidence_list_download(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    up = ext.upload_evidence(actor_id=r, idem_key="u", task_id=tid,
                             filename="img.png", mime_type="image/png",
                             payload=b"\x89PNG\r\n\x1a\n-fake-png-bytes",
                             expected_version=ver)
    eid = up["evidence_id"]
    lst = ext.list_evidence(actor_id=r, task_id=tid)
    assert any(e["evidence_id"] == eid for e in lst["evidence"])

    dl = ext.download_evidence(actor_id=r, task_id=tid, evidence_id=eid)
    assert dl["payload"] == b"\x89PNG\r\n\x1a\n-fake-png-bytes"
    assert dl["sha256"] == up["sha256"]


def test_upload_evidence_too_large(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    ext.max_evidence_bytes = 100
    with pytest.raises(EvidenceTooLarge):
        ext.upload_evidence(actor_id=r, idem_key="u", task_id=tid,
                            filename="big.bin", mime_type="application/octet-stream",
                            payload=b"x" * 200, expected_version=ver)


def test_upload_evidence_quarantine_blocks_download(executor, ext, fixtures):
    """T19：QUARANTINED 附件不能下载。"""
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    up = ext.upload_evidence(actor_id=r, idem_key="u", task_id=tid,
                             filename="bad.png", mime_type="image/png",
                             payload=b"x", expected_version=ver)
    eid = up["evidence_id"]
    ext.quarantine_evidence(actor_id=fixtures["manager"], idem_key="q",
                            task_id=tid, evidence_id=eid,
                            expected_version=ver, reason="不合适")
    from octosense_backend.errors import EvidenceQuarantined
    with pytest.raises(EvidenceQuarantined):
        ext.download_evidence(actor_id=r, task_id=tid, evidence_id=eid)


def test_quarantine_nonexistent_evidence_404(executor, ext, fixtures):
    """N13：隔离不存在的证据返 404。"""
    from octosense_backend.errors import EvidenceNotFound
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    with pytest.raises(EvidenceNotFound):
        ext.quarantine_evidence(actor_id=fixtures["manager"], idem_key="q",
                                 task_id=tid, evidence_id="ghost-evi",
                                 expected_version=ver, reason="x")


# ============ T30 收藏 ============

def test_pin_and_list_and_unpin(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    a = ext.add_pin(actor_id=r, idem_key="p1", task_id=tid)
    assert a["pinned"] is True
    b = ext.list_pins(actor_id=r)
    assert any(p["task_id"] == tid for p in b["pins"])
    c = ext.remove_pin(actor_id=r, idem_key="p2", task_id=tid)
    assert c["pinned"] is False
    d = ext.list_pins(actor_id=r)
    assert not any(p["task_id"] == tid for p in d["pins"])


def test_pin_other_user_not_visible(executor, ext, fixtures):
    """T30：其他用户收藏不互相影响。"""
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    ext.add_pin(actor_id=r, idem_key="p1", task_id=tid)
    pins = ext.list_pins(actor_id=fixtures["tech_1"])
    assert not any(p["task_id"] == tid for p in pins["pins"])
    conn = ext.db.conn()
    row = conn.execute("SELECT version FROM repair_tasks WHERE task_id=?", (tid,)).fetchone()
    assert row["version"] == ver


# ============ T25 历史依据 ============

def test_history_advice_no_asset(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    data = ext.get_history_advice(actor_id=r, task_id=tid)
    assert data["asset_id"] is None
    assert "未绑定设备" in data["advice"]


def test_history_advice_with_asset(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=ver)
    data = ext.get_history_advice(actor_id=r, task_id=tid)
    assert data["asset_id"] == fixtures["asset_a1"]
    assert data["history"] == []
    assert "0 次" in data["advice"]


def test_history_advice_cross_project_rejected(executor, ext, fixtures):
    """N04：拿 prj-A 任务查 prj-B 设备拒绝。"""
    from octosense_backend.errors import OctoSenseError
    with db_conn(ext.db) as conn:
        conn.execute(
            "INSERT INTO repair_assets (asset_id, project_id, asset_code, display_name, source, active) "
            "VALUES (?,?,?,?,'DEMO',1)",
            ("as-b-1", "prj-B", "PWR-B-001", "B项目强电"),
        )
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    with pytest.raises(OctoSenseError):
        ext.get_history_advice(actor_id=r, task_id=tid, asset_id="as-b-1")


def test_record_advice_with_auth_and_idem(executor, ext, fixtures):
    """R-P1-3/N07：record_advice 需权限与幂等。"""
    from octosense_backend.errors import PermissionDenied
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    # ghost 应被拒绝
    with pytest.raises(PermissionDenied):
        ext.record_advice(actor_id="u-ghost", idem_key="adv-g", task_id=tid,
                          source_kind="DEVICE_HISTORY", payload={"x": 1})
    # 合法 record
    data = ext.record_advice(actor_id=r, idem_key="adv", task_id=tid,
                             source_kind="DEVICE_HISTORY",
                             payload={"text": "上次修过类似", "confidence": "low"})
    assert data["source_kind"] == "DEVICE_HISTORY"
    # 同 key 重试：replay（不应 500）
    data2 = ext.record_advice(actor_id=r, idem_key="adv", task_id=tid,
                              source_kind="DEVICE_HISTORY",
                              payload={"text": "上次修过类似", "confidence": "low"})
    assert data2.get("idempotent_replay") is True


# ============ record_progress ============

def test_record_progress_in_progress(executor, ext, appt_cmds, fixtures, clock):
    p, r, t, tid, ver = _setup_accepted(executor, fixtures)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=ver)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=ver + 1)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=ver + 2, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=ver + 3)
    data = ext.record_progress(actor_id=t, idem_key="rp", task_id=tid,
                               note="拆外壳完成", expected_version=ver + 4)
    assert data["version"] == ver + 5
    assert data["note"] == "拆外壳完成"


def test_record_progress_not_in_progress_rejected(executor, ext, fixtures):
    _, r, t, tid, ver = _setup_accepted(executor, fixtures)
    with pytest.raises(IllegalTransition):
        ext.record_progress(actor_id=t, idem_key="rp", task_id=tid,
                            note="太早", expected_version=ver)


def test_record_progress_other_tech_rejected(executor, ext, appt_cmds, fixtures, clock):
    p, r, t, tid, ver = _setup_accepted(executor, fixtures)
    ext.bind_asset(actor_id=r, idem_key="b", task_id=tid,
                   asset_id=fixtures["asset_a1"], expected_version=ver)
    s = _now_ms() + 5 * 60_000
    e = s + 30 * 60_000
    pr = executor.propose_appointment(actor_id=t, idem_key="p", task_id=tid,
                                       start_at_ms=s, end_at_ms=e, expected_version=ver + 1)
    appt_id = pr.data["appointment_id"]
    appt_cmds.confirm_appointment(actor_id=r, idem_key="ca", task_id=tid,
                                  expected_version=ver + 2, appointment_id=appt_id)
    executor._clock = lambda: (s + e) // 2
    executor.start_progress(actor_id=t, idem_key="st", task_id=tid, expected_version=ver + 3)
    with pytest.raises(PermissionDenied):
        ext.record_progress(actor_id=fixtures["tech_2"], idem_key="rp", task_id=tid,
                            note="越权", expected_version=ver + 4)


# ============ list_tasks ============

def test_list_tasks_reporter_only_own(executor, ext, fixtures):
    p, r, t, tid, ver = _setup_accepted(executor, fixtures)
    res = executor.create_draft(actor_id=r, idem_key="c2", problem_text="P2",
                                contact_name="C", project_id=p)
    tid2 = res.data["task_id"]
    executor.confirm_draft(actor_id=r, idem_key="o2", task_id=tid2, expected_version=1)
    reporter_view = ext.list_tasks(actor_id=r, project_id=p, role_filter="REPORTER")
    assert all(t["reporter_id"] == r for t in reporter_view["tasks"])
    assert len(reporter_view["tasks"]) >= 2


def test_list_tasks_tech_only_assigned(executor, ext, fixtures):
    p, r, t, tid, ver = _setup_accepted(executor, fixtures)
    tech_view = ext.list_tasks(actor_id=t, project_id=p, role_filter="TECHNICIAN")
    assert all(item["assignee_id"] == t for item in tech_view["tasks"])
    assert any(item["task_id"] == tid for item in tech_view["tasks"])


def test_list_tasks_status_filter(executor, ext, fixtures):
    _, r, _, tid, ver = _setup_accepted(executor, fixtures)
    open_only = ext.list_tasks(actor_id=r, project_id=fixtures["project_a"], status_filter="OPEN")
    assert all(t["status"] == "OPEN" for t in open_only["tasks"])
    accepted_only = ext.list_tasks(actor_id=r, project_id=fixtures["project_a"], status_filter="ACCEPTED")
    assert all(t["status"] == "ACCEPTED" for t in accepted_only["tasks"])


def test_get_task_cross_project_404(executor, ext, fixtures):
    """R-P0-3：跨项目读 task 返 404（避免枚举）。"""
    # 注：直接走 executor 不能模拟 HTTP；走 API 测试
    pass  # 走 API 测试覆盖


# ============ helper ============

from contextlib import contextmanager

@contextmanager
def db_conn(db):
    conn = db.conn()
    try:
        yield conn
    finally:
        conn.close()
