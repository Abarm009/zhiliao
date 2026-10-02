"""11 个工具的行为测试 —— 正例 + 错误协议（临时库 + 本地向量，不碰 API）。"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from wagent_backend.llm.embedder import local_embed
from wagent_backend.ops.data.db import connect, init_db, truth_leak_check
from wagent_backend.ops.data.seed import seed
from wagent_backend.ops.tools.context import ToolContext
from wagent_backend.ops.tools.registry import run_tool

AS_OF = datetime(2026, 8, 23, 10, 0)


@pytest.fixture()
def ctx(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    conn = connect()
    init_db(conn)
    seed(conn, local_embed)
    return ToolContext(as_of=AS_OF, conn=conn, embedder=local_embed)


# ── 1. resolve_space ─────────────────────────────────

def test_resolve_space_by_floor_zone(ctx):
    r = run_tool("resolve_space", ctx, text="A座25楼东侧会议室空调又不制冷了")
    assert r["error"] is None and len(r["matches"]) == 1
    m = r["matches"][0]
    assert m["space_id"] == "SP-A-25-E" and m["zone"] == "东侧"


def test_resolve_space_alias(ctx):
    r = run_tool("resolve_space", ctx, text="A25东")
    assert r["matches"][0]["space_id"] == "SP-A-25-E"
    assert r["matches"][0]["match_confidence"] == 0.90


def test_resolve_space_not_found(ctx):
    r = run_tool("resolve_space", ctx, text="顶楼空中花园")
    assert r["error"]["code"] == "not_found"


def test_resolve_space_ambiguous(ctx):
    # 造一个别名冲突：两个空间都有别名「25楼东侧」
    ctx.conn.execute(
        "INSERT INTO space VALUES ('SP-X','BLD-A',25,'西侧',NULL,'房源',50,NULL,?)",
        (json.dumps(["25楼东侧"]),),
    )
    ctx.conn.commit()
    r = run_tool("resolve_space", ctx, text="25楼东侧")
    assert r["error"]["code"] == "ambiguous"
    assert len(r["matches"]) == 2  # 候选仍返回，交给上层确认


def test_resolve_space_building_hint(ctx):
    r = run_tool("resolve_space", ctx, text="1106", building_hint="A栋")
    assert r["matches"][0]["space_id"] == "SP-A-11-1106"
    bad = run_tool("resolve_space", ctx, text="1106", building_hint="C栋")
    assert bad["error"]["code"] == "not_found"


def test_resolve_space_alias_substring(ctx):
    # 口语带楼栋前缀/现象后缀：别名子串包含档（0.85）命中 13楼男卫生间
    r = run_tool("resolve_space", ctx, text="a栋13楼男卫生间有异味")
    assert r["error"] is None and len(r["matches"]) == 1
    m = r["matches"][0]
    assert m["space_id"] == "SP-A-13-WCM"
    assert m["match_confidence"] == 0.85


def test_resolve_space_floor_zone_restroom(ctx):
    # 卫生间 zone 就是 男/女：楼层+区域档（0.50）也能命中
    r = run_tool("resolve_space", ctx, text="13楼这一层男卫生间味很大")
    assert r["error"] is None and len(r["matches"]) == 1
    m = r["matches"][0]
    assert m["space_id"] == "SP-A-13-WCM"
    assert m["match_confidence"] == 0.50


def test_resolve_space_restroom_synonym(ctx):
    # 口语「男洗手间」归一为「男卫生间」，别名子串档命中
    r = run_tool("resolve_space", ctx, text="a栋13楼男洗手间漏水")
    assert r["error"] is None and len(r["matches"]) == 1
    assert r["matches"][0]["space_id"] == "SP-A-13-WCM"


def test_resolve_space_floor_type_narrows_down(ctx):
    # 无男女：楼层+类型收敛到男/女卫两个候选（ambiguous 交上层确认），而非 not_found
    r = run_tool("resolve_space", ctx, text="a栋13楼洗手间")
    assert r["error"]["code"] == "ambiguous"
    assert len(r["matches"]) == 2
    assert {m["space_type"] for m in r["matches"]} == {"卫生间"}


# ── 2. get_assets_serving_space ──────────────────────

def test_assets_serving_with_runtime(ctx):
    r = run_tool("get_assets_serving_space", ctx, space_id="SP-A-25-E")
    ids = {a["asset_id"] for a in r["assets"]}
    assert ids == {"FCU-A25-01", "AHU-A-25", "SD-A25-01"}
    fcu = next(a for a in r["assets"] if a["asset_id"] == "FCU-A25-01")
    # 机关 1：阀位 0% 但流量 >0 → 阀卡死
    assert fcu["runtime"]["valve_position_pct"] == 0.0
    assert fcu["runtime"]["water_flow_lpm"] == 12.4
    assert fcu["is_overdue_service"] is True


def test_assets_lock_status_visible(ctx):
    r = run_tool("get_assets_serving_space", ctx, space_id="SP-A-11-1106")
    assert r["assets"][0]["runtime"]["lock_status"] == "billing_locked"


def test_assets_category_filter_and_not_found(ctx):
    r = run_tool("get_assets_serving_space", ctx, space_id="SP-A-25-E", category="FIRE")
    assert [a["asset_id"] for a in r["assets"]] == ["SD-A25-01"]
    assert run_tool("get_assets_serving_space", ctx,
                    space_id="SP-None")["error"]["code"] == "not_found"


# ── 3. query_workorder_history ───────────────────────

def test_wo_history_repeat_chain(ctx):
    r = run_tool("query_workorder_history", ctx, scope="asset",
                 id="FCU-A25-01", window="90d")
    assert r["error"] is None
    # 按创建时间倒序（最近优先）
    assert [w["wo_id"] for w in r["work_orders"]] == [
        "WO-B25-0811", "WO-B25-0720", "WO-B25-0624",
    ]
    w2 = r["work_orders"][1]
    assert w2["closed"] is True
    # 纯派工事件不算处置；诊断事件算
    assert all(d["technician_id"] for d in w2["dispositions"])
    assert any(d["action_taken"] == "temporary_valve_override"
               for d in w2["dispositions"])


def test_wo_history_empty_window_is_not_error(ctx):
    r = run_tool("query_workorder_history", ctx, scope="space",
                 id="SP-A-16-1608", window="7d")
    assert r["error"] is None and r["work_orders"] == [] and r["total_count"] == 0


def test_wo_history_invalid_window_and_scope(ctx):
    assert run_tool("query_workorder_history", ctx, scope="asset",
                    id="FCU-A25-01", window="14d")["error"]["code"] == "invalid_input"
    assert run_tool("query_workorder_history", ctx, scope="asset",
                    id="FCU-XXX")["error"]["code"] == "not_found"


def test_wo_history_tenant_scope(ctx):
    r = run_tool("query_workorder_history", ctx, scope="tenant",
                 id="TEN-002", window="90d")
    assert {w["wo_id"] for w in r["work_orders"]} == {
        "WO-B25-0624", "WO-B25-0720", "WO-B25-0811",
    }


# ── 4. recall_memory ─────────────────────────────────

def test_recall_memory_ranked(ctx):
    r = run_tool("recall_memory", ctx, query="空调反复不制冷 电动阀",
                 scope_type="asset", scope_id="FCU-A25-01")
    assert r["items"][0]["insight_id"] == "INS-REPLAY-001"
    assert r["items"][0]["confidence"] == 0.82
    assert len(r["items"][0]["evidence_wo_ids"]) == 3


def test_recall_memory_no_future_insight(ctx):
    early = ToolContext(as_of=datetime(2026, 7, 30), conn=ctx.conn,
                        embedder=local_embed)
    r = run_tool("recall_memory", early, query="阀 执行器",
                 scope_type="asset", scope_id="FCU-A25-01")
    # INS-REPLAY-001 生成于 8/12，7/30 视角下不可见
    assert all(i["insight_id"] != "INS-REPLAY-001" for i in r["items"])


def test_recall_memory_scope_rules(ctx):
    assert run_tool("recall_memory", ctx, query="x",
                    scope_type="any")["error"] is None
    assert run_tool("recall_memory", ctx, query="x", scope_type="asset")["error"][
        "code"] == "invalid_input"
    assert run_tool("recall_memory", ctx, query="x", scope_type="asset",
                    scope_id="FCU-XXX")["error"]["code"] == "not_found"


# ── 5. write_memory ──────────────────────────────────

def test_write_memory_happy(ctx):
    r = run_tool("write_memory", ctx, scope_type="asset", scope_id="FCU-A19-13",
                 body_md="A1913 风量小与租户改装风管相关，处置前先核对装修记录。",
                 confidence=0.6, evidence_wo_ids=["WO-B19-0704"], source="agent_runtime",
                 predicted_root_cause="tenant_modification")
    assert r["insight_id"] == "INS-0003"
    got = run_tool("recall_memory", ctx, query="风量小 装修",
                   scope_type="asset", scope_id="FCU-A19-13")
    assert got["items"][0]["insight_id"] == "INS-0003"


def test_write_memory_rejects_no_evidence(ctx):
    r = run_tool("write_memory", ctx, scope_type="asset", scope_id="FCU-A19-13",
                 body_md="无证据洞察", confidence=0.9, evidence_wo_ids=["WO-NOPE"],
                 source="agent_runtime")
    assert r["error"]["code"] == "not_found"


def test_write_memory_time_travel_rejected(ctx):
    early = ToolContext(as_of=datetime(2026, 8, 1), conn=ctx.conn,
                        embedder=local_embed)
    r = run_tool("write_memory", early, scope_type="asset", scope_id="FCU-A25-01",
                 body_md="引用未来工单", confidence=0.9,
                 evidence_wo_ids=["WO-B25-0811"], source="agent_runtime")  # 8/11 创建 > 8/1 场景时间
    assert r["error"]["code"] == "invalid_input"


# ── 6. verify_memory_prediction ──────────────────────

def test_verify_hit_then_miss_moves_to_review(ctx):
    hit = run_tool("verify_memory_prediction", ctx, insight_id="INS-REPLAY-002",
                   wo_id="WO-A11-0803", actual_root_cause="billing_suspension")
    assert hit["hit"] is True
    assert hit["confidence_before"] == 0.58
    assert hit["confidence_after"] == pytest.approx(0.58 + 0.10 * 0.42, abs=1e-4)
    assert hit["moved_to_review_queue"] is False

    miss = run_tool("verify_memory_prediction", ctx, insight_id="INS-REPLAY-002",
                    wo_id="WO-A11-0709", actual_root_cause="power_supply_fault")
    assert miss["hit"] is False
    assert miss["confidence_after"] == pytest.approx(
        hit["confidence_after"] * 0.85, abs=1e-4)
    assert miss["moved_to_review_queue"] is True


def test_verify_rejects_open_wo_and_duplicate(ctx):
    wo = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                  raw_text="测试未闭环", symptom="no_cooling")
    assert run_tool("verify_memory_prediction", ctx, insight_id="INS-REPLAY-001",
                    wo_id=wo["wo_id"],
                    actual_root_cause="filter_clogged")["error"]["code"] == "invalid_input"
    assert run_tool("verify_memory_prediction", ctx, insight_id="INS-REPLAY-001",
                    wo_id="WO-B25-0811",
                    actual_root_cause="filter_clogged")["error"]["code"] == "invalid_input"


# ── 7. judge_liability ───────────────────────────────

def test_judge_clause_conflict_requires_human(ctx):
    r = run_tool("judge_liability", ctx, symptom="no_cooling", space_id="SP-A-25-E",
                 hypothesized_root_cause="valve_actuator_failure")
    assert r["liability"] == "unclear" and r["requires_human"] is True
    assert set(r["clause_ids"]) == {"CL-004", "CL-005"}


def test_judge_unique_clause(ctx):
    r = run_tool("judge_liability", ctx, symptom="no_cooling", space_id="SP-A-19-1913",
                 hypothesized_root_cause="filter_clogged")
    assert (r["liability"], r["basis"]) == ("tenant", "contract_clause")
    assert r["clause_ids"] == ["CL-002"]


def test_judge_default_mapping_and_cost_threshold(ctx):
    r = run_tool("judge_liability", ctx, symptom="no_cooling", space_id="SP-A-16-1608",
                 hypothesized_root_cause="fan_motor_fault")
    assert (r["liability"], r["basis"]) == ("owner", "default_mapping")
    expensive = run_tool("judge_liability", ctx, symptom="no_cooling", space_id="SP-A-16-1608",
                         hypothesized_root_cause="fan_motor_fault",
                         estimated_cost_cny=8000)
    assert expensive["requires_human"] is True


def test_judge_no_basis(ctx):
    r = run_tool("judge_liability", ctx, symptom="no_cooling", space_id="SP-A-25-E")
    assert r["liability"] == "unclear" and r["requires_human"] is True


def test_judge_cost_threshold_boundary(ctx):
    """费用阈值严格 >5000：边界两侧都不容错（后置硬停策略依赖它）。"""
    base = dict(symptom="no_cooling", space_id="SP-A-19-1913",
                hypothesized_root_cause="filter_clogged")
    for cost in (4999.99, 5000.00):
        r = run_tool("judge_liability", ctx, **base, estimated_cost_cny=cost)
        assert r["requires_human"] is False, cost
    r = run_tool("judge_liability", ctx, **base, estimated_cost_cny=5000.01)
    assert r["requires_human"] is True
    assert "5000" in r["requires_human_reason"]


# ── 8. create_workorder ──────────────────────────────

def test_create_workorder_full(ctx):
    r = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                 raw_text="25楼东侧空调又不制冷了",
                 symptom="no_cooling", urgency="紧急",
                 asset_id="FCU-A25-01", assigned_technician_id="TEC-001",
                 hypothesized_root_cause="valve_actuator_failure",
                 recommended_action="replace_valve_actuator",
                 liability="unclear",
                 briefing_note="历史两次手动开阀治标，本次直接换阀执行器。",
                 evidence_wo_ids=["WO-B25-0720", "WO-B25-0811"])
    assert r["wo_id"].startswith("WO-260823-")
    # 交底进了 dispatched 事件
    evs = ctx.conn.execute(
        "SELECT note FROM work_order_event WHERE wo_id=?", (r["wo_id"],)
    ).fetchall()
    assert any("换阀执行器" in (e["note"] or "") for e in evs)


def test_create_workorder_rejects_non_serving_asset(ctx):
    r = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                 raw_text="x", symptom="no_cooling", asset_id="FCU-A19-13")
    assert r["error"]["code"] == "invalid_input"


def test_create_workorder_without_space(ctx):
    """全盘接受（2026-08-27）：位置未定也先建单，审计负载带班组预判。"""
    from wagent_backend.ops.data.repo import wo_suggested_team
    r = run_tool("create_workorder", ctx, space_id=None,
                 raw_text="b座25楼电梯口有一滩水渍", symptom="water_leak", urgency="紧急")
    assert r["wo_id"]
    assert wo_suggested_team(ctx.conn, r["wo_id"]) == "环境"


def test_create_workorder_team_mapping(ctx):
    """三班组预判口径：水渍/卫生→环境，吸烟/聚集→秩序，维修→工程（默认）。"""
    from wagent_backend.ops.data.repo import wo_suggested_team
    cases = [("smoking", "秩序"), ("sanitation", "环境"), ("overcrowding", "秩序"),
             ("no_cooling", "工程")]
    for symptom, team in cases:
        r = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                     raw_text=f"测试{symptom}", symptom=symptom)
        assert wo_suggested_team(ctx.conn, r["wo_id"]) == team, symptom


def test_create_workorder_asset_requires_space(ctx):
    """带 asset_id 但没有 space_id：无法校验服务关系，拒绝。"""
    r = run_tool("create_workorder", ctx, space_id=None, raw_text="x",
                 symptom="no_cooling", asset_id="FCU-A25-01")
    assert r["error"]["code"] == "invalid_input"


def test_create_workorder_blank_strings_normalized(ctx):
    """模型把「无」写成 ""/"None"/"null" 时归一化为 NULL，不得撞外键（2026-08-31 线上事故）。"""
    r = run_tool("create_workorder", ctx, space_id="SP-A-13-WCF",
                 raw_text="A栋13楼女卫异味", symptom="odor",
                 asset_id="", assigned_technician_id="None")
    assert r.get("wo_id"), r
    row = ctx.conn.execute("SELECT asset_id FROM work_order WHERE wo_id=?",
                           (r["wo_id"],)).fetchone()
    assert row["asset_id"] is None


def test_create_workorder_repeat_check(ctx):
    """建单前确定性查重：同空间同症状 90 天内的已有工单随返回注入（复发判定用）。"""
    r = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                 raw_text="25楼东侧空调又不制冷了", symptom="no_cooling")
    assert set(r["repeat_evidence"]) == {"WO-B25-0624", "WO-B25-0720", "WO-B25-0811"}
    assert "3 张同类工单" in r["repeat_hint"]
    # 不同症状不命中
    r2 = run_tool("create_workorder", ctx, space_id="SP-A-25-E",
                  raw_text="25楼东侧漏水", symptom="water_leak")
    assert r2["repeat_evidence"] == [] and r2["repeat_hint"] is None


# ── 9. find_technician ───────────────────────────────

def test_find_technician_ranking(ctx):
    r = run_tool("find_technician", ctx, skill="HVAC", building_id="BLD-B",
                 at="2026-08-23T10:00:00")
    assert [t["technician_id"] for t in r["technicians"]][:2] == ["TEC-001", "TEC-005"]
    assert r["technicians"][0]["available"] is True
    night = next(t for t in r["technicians"] if t["technician_id"] == "TEC-002")
    assert night["available"] is False


def test_find_technician_cert_filter(ctx):
    r = run_tool("find_technician", ctx, skill="HVAC", building_id="BLD-B",
                 certification="制冷设备维修工")
    assert [t["technician_id"] for t in r["technicians"]] == ["TEC-001"]


# ── 10/11. notify + escalate ─────────────────────────

def test_notify_receipts(ctx):
    r = run_tool("notify", ctx, channel="wecom", recipient_role="tenant_contact",
                 recipient_id="C-002", message="已安排技工")
    assert r["receipt_id"].startswith("RCPT-")
    fm = run_tool("notify", ctx, channel="wecom", recipient_role="facility_manager",
                  recipient_id="FM-001", message="简报")
    assert fm["error"] is None
    assert run_tool("notify", ctx, channel="wecom", recipient_role="tenant_contact",
                    recipient_id="C-999",
                    message="x")["error"]["code"] == "not_found"


def test_escalate_ticket(ctx):
    r = run_tool("escalate_to_human", ctx, reason="contract_ambiguous",
                 detail="条款冲突", space_id="SP-A-25-E", asset_id="FCU-A25-01")
    assert r["ticket_id"].startswith("TKT-")


# ── 注册表协议 ───────────────────────────────────────

def test_unknown_tool_and_bad_args(ctx):
    assert run_tool("kg_search", ctx)["error"]["code"] == "invalid_input"
    r = run_tool("resolve_space", ctx)  # 缺必填 text
    assert r["error"]["code"] == "invalid_input"


def test_truth_leak_check_clean(ctx):
    assert truth_leak_check(ctx.conn) == []
