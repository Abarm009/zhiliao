"""仿真测试数据（simseed）导入测试 —— 打开 WAGENT_OPS_SIMSEED 全量灌入后验证。

数据由 git d0a9f93 的仿真器确定性生成（seed=42, 373 天，终点 2026-08-23），
见 data/simseed/PROVENANCE.md。此处验证：规模 / 完整性 / 真值隔离 / FK /
确定性（验收 V1）/ 洞察铁律 / 工具层可用性。
"""

from __future__ import annotations

import io
import json
import os
from datetime import datetime

import pytest

from wagent_backend.llm.embedder import local_embed
from wagent_backend.ops.data.db import connect, init_db, truth_leak_check
from wagent_backend.ops.data.seed import seed
from wagent_backend.ops.tools.context import ToolContext
from wagent_backend.ops.tools.registry import run_tool

AS_OF = datetime(2026, 8, 23, 10, 0)


def _save_env(*keys: str) -> dict[str, str | None]:
    return {k: os.environ.get(k) for k in keys}


def _restore_env(saved: dict[str, str | None]) -> None:
    for k, v in saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


@pytest.fixture(scope="module")
def ctx(tmp_path_factory):
    saved = _save_env("WAGENT_OPS_DB", "WAGENT_OPS_SIMSEED")
    os.environ["WAGENT_OPS_DB"] = str(tmp_path_factory.mktemp("sim") / "ops.db")
    os.environ["WAGENT_OPS_SIMSEED"] = "1"
    conn = connect()
    init_db(conn)
    seed(conn, local_embed)
    yield ToolContext(as_of=AS_OF, conn=conn, embedder=local_embed)
    conn.close()
    _restore_env(saved)


def test_import_scale_and_integrity(ctx):
    # 演示种子之上叠加仿真数据（216 空间 / 276 设备 / 3086 工单）
    counts = {t: ctx.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("space", "asset", "work_order", "technician")}
    assert counts["space"] >= 216 + 5
    assert counts["asset"] >= 276 + 6
    assert counts["work_order"] >= 3000 + 6
    assert counts["technician"] >= 12 + 5
    assert ctx.conn.execute(
        "SELECT COUNT(*) FROM tenant_occupies_space").fetchone()[0] >= 200
    # 仿真园区是独立 property，与演示种子「汇金广场」并存
    assert ctx.conn.execute("SELECT COUNT(*) FROM property").fetchone()[0] == 2
    # L2 append-only 触发器对仿真工单同样生效
    with pytest.raises(Exception):
        ctx.conn.execute("DELETE FROM work_order WHERE space_id = 'SP-A-0201'")


def test_truth_isolation_and_fk(ctx):
    assert truth_leak_check(ctx.conn) == []
    assert ctx.conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_insight_rules(ctx):
    rows = ctx.conn.execute(
        "SELECT insight_id, predicted_root_cause, confidence, "
        "evidence_wo_ids, generated_at, source FROM insight "
        "WHERE insight_id LIKE 'INS-SIM-%'").fetchall()
    assert rows, "应由 L2 聚合出至少一条复发洞察"
    for r in rows:
        evidence = json.loads(r["evidence_wo_ids"])
        assert len(evidence) >= 3
        # 证据工单真实存在，且洞察生成晚于全部证据（时间旅行铁律）
        last_ev = ctx.conn.execute(
            "SELECT MAX(created_at) FROM work_order WHERE wo_id IN "
            f"({','.join('?' * len(evidence))})", evidence).fetchone()[0]
        assert last_ev and r["generated_at"] > last_ev
        assert 0.0 <= r["confidence"] <= 1.0
        assert r["source"] == "agent_replay"
        assert r["predicted_root_cause"]


def test_runtime_snapshot_consistency(ctx):
    locked = ctx.conn.execute(
        "SELECT asset_id, valve_position_pct, water_flow_lpm, fan_speed "
        "FROM asset_runtime WHERE lock_status = 'billing_locked'").fetchall()
    for r in locked:  # 锁机快照的可观测特征必须自洽
        assert r["valve_position_pct"] == 0.0 and r["water_flow_lpm"] == 0.0
        assert r["fan_speed"] == "off"
    assert ctx.conn.execute(
        "SELECT COUNT(*) FROM asset_runtime WHERE lock_status = 'normal' "
        "AND asset_id LIKE 'FCU-%'").fetchone()[0] > 100


def test_determinism(ctx, tmp_path_factory):
    """验收 V1：同 seed 两次导入，库内容一致（规模 + 洞察全文）。"""
    saved = _save_env("WAGENT_OPS_DB", "WAGENT_OPS_SIMSEED")
    os.environ["WAGENT_OPS_DB"] = str(tmp_path_factory.mktemp("sim2") / "ops.db")
    os.environ["WAGENT_OPS_SIMSEED"] = "1"
    conn = connect()
    init_db(conn)
    seed(conn, local_embed)
    try:
        for t in ("space", "asset", "work_order", "asset_runtime", "insight"):
            assert conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] == \
                ctx.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        bodies = [r[0] for r in conn.execute(
            "SELECT body_md FROM insight WHERE insight_id LIKE 'INS-SIM-%' "
            "ORDER BY insight_id")]
        assert bodies == [r[0] for r in ctx.conn.execute(
            "SELECT body_md FROM insight WHERE insight_id LIKE 'INS-SIM-%' "
            "ORDER BY insight_id")]
    finally:
        conn.close()
        _restore_env(saved)


# ── 工具层可用性：仿真数据必须能被 11 个工具正常消费 ──────────

def test_resolve_space_by_sim_alias(ctx):
    r = run_tool("resolve_space", ctx, text="A座2楼东侧空调漏水")
    ids = [m["space_id"] for m in r["matches"]]
    if r.get("error"):
        # 「2楼东侧」在 A/B/C 三塔均有别名命中 → 歧义返回候选是设计行为
        assert r["error"]["code"] == "ambiguous" and "SP-A-0201" in ids, r
        r2 = run_tool("resolve_space", ctx, text="A座2楼东侧空调漏水",
                      building_hint="仿真A座")
        assert not r2.get("error"), r2
        assert r2["matches"][0]["space_id"] == "SP-A-0201", r2
    else:
        assert "SP-A-0201" in ids, r


def test_query_workorder_history_on_sim_asset(ctx):
    # 从 l2 文件动态挑一个 90 天窗口内工单最多的仿真末端设备
    from wagent_backend.ops.data.simdata import L2_FILE
    horizon = "2026-05-25"
    counts: dict[str, int] = {}
    for line in io.open(L2_FILE, encoding="utf-8"):
        w = json.loads(line)
        if w["created_at"] >= horizon and w["asset_id"].startswith(("FCU-", "AHU-")):
            counts[w["asset_id"]] = counts.get(w["asset_id"], 0) + 1
    asset = max(counts, key=lambda k: counts[k])
    r = run_tool("query_workorder_history", ctx, scope="asset", id=asset,
                 window="90d")
    assert not r.get("error"), r
    assert r["total_count"] >= counts[asset] - 1
    assert all(w.get("raw_text") for w in r["work_orders"])


def test_recall_memory_scoped_to_sim_insight(ctx):
    row = ctx.conn.execute(
        "SELECT scope_id FROM insight WHERE insight_id LIKE 'INS-SIM-%' "
        "ORDER BY insight_id LIMIT 1").fetchone()
    r = run_tool("recall_memory", ctx, query="该设备反复报修，历次临时处置未根治",
                 scope_type="asset", scope_id=row["scope_id"])
    assert not r.get("error"), r
    assert any(m["insight_id"].startswith("INS-SIM-") for m in r["items"]), r
