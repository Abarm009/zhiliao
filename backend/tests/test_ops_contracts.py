"""契约守卫 —— 冻结副本的结构不变量 + 真值隔离红线。"""

from __future__ import annotations

from pathlib import Path

import wagent_backend.ops.contracts as C
from wagent_backend.ops.agent import prompts as P

EXPECTED_TOOLS = {
    "resolve_space", "get_assets_serving_space", "query_workorder_history",
    "recall_memory", "write_memory", "verify_memory_prediction",
    "judge_liability", "create_workorder", "find_technician", "notify",
    "escalate_to_human",
}


def test_registry_exactly_11_frozen_tools():
    assert set(C.TOOL_REGISTRY) == EXPECTED_TOOLS
    assert len(C.TOOL_REGISTRY) == 11


def test_enum_counts_frozen():
    assert len({e.value for e in C.SymptomEnum}) == 11  # 2026-08-27 +3 非设备类
    assert len({e.value for e in C.RootCauseEnum}) == 18
    assert len({e.value for e in C.ActionEnum}) == 22
    assert len({e.value for e in C.LiabilityEnum}) == 5


def test_every_tool_has_io_models():
    for name, (inp, out) in C.TOOL_REGISTRY.items():
        assert hasattr(inp, "model_validate"), name
        assert hasattr(out, "model_validate"), name


def test_decision_fields_frozen():
    fields = set(C.Decision.model_fields)
    for f in ("space_id", "symptom", "root_cause", "root_cause_confidence",
              "is_repeat_fault", "repeat_evidence", "recommended_action",
              "liability", "escalate", "memory_ids_used"):
        assert f in fields, f


def test_truth_isolation_no_answer_leak_in_prompts():
    """SYMPTOM_CANDIDATE_CAUSES / CURATIVE_ACTIONS 绝不进 prompt / runner。"""
    from wagent_backend.ops.agent import runner as R

    # 模块没有 import 答案表（docstring 里的警示语不算）
    for sym in ("SYMPTOM_CANDIDATE_CAUSES", "CURATIVE_ACTIONS"):
        assert not hasattr(P, sym)
        assert not hasattr(R, sym)
    # 真正到达模型的系统提示词里不能出现答案表内容
    for tier in P.TIERS:
        sp = P.build_system_prompt(tier)
        assert "SYMPTOM_CANDIDATE_CAUSES" not in sp
        assert "CURATIVE_ACTIONS" not in sp
        assert "candidate_causes" not in sp.lower()


def test_tier_tool_gating():
    """四档工具集严格递增：off=6 → l1=7 → l1l2=8 → full=11（消融设计）。"""
    off, l1, l1l2, full = (P.tier_tools(t) for t in P.TIERS)
    assert set(off) < set(l1) < set(l1l2) < set(full)
    assert (len(off), len(l1), len(l1l2), len(full)) == (6, 7, 8, 11)
    assert set(l1) - set(off) == {"get_assets_serving_space"}
    assert set(l1l2) - set(l1) == {"query_workorder_history"}
    assert set(full) - set(l1l2) == {
        "recall_memory", "write_memory", "verify_memory_prediction",
    }


def test_tier_prompts_no_device_leak():
    """off 档没有设备工具，提示词不得提它；字段解读（billing_locked 等）
    任何一档都不给直接答案 —— 「知道该看哪字段」是记忆的产出。"""
    sp_off = P.build_system_prompt("off")
    assert "get_assets_serving_space" not in sp_off
    assert "billing_locked" not in sp_off
    sp_l1 = P.build_system_prompt("l1")
    assert "get_assets_serving_space" in sp_l1
    for tier in P.TIERS:
        assert "billing_locked" not in P.build_system_prompt(tier)


def test_vendored_copies_carry_provenance():
    base = Path(C.__file__).parent
    assert "冻结" in (base / "enums.py").read_text(encoding="utf-8")
    assert "冻结" in (base / "schemas.py").read_text(encoding="utf-8")
