"""6 个 LLM 工具的单测：每个至少 1 正例 + 错误路径负例。"""

from __future__ import annotations

import pytest

from wagent_backend.graphRAG.store import get_store
from wagent_backend.tools import kg_tools as tools
from wagent_backend.tools.kg_tools import KG_TOOL_REGISTRY

DEV = "DEV-HFC227-001"
DEPT = "DEPT-ENG"
FLR = "FLR-A-B1"
ROOM = "RM-A-B1-01"
PRJ = "PRJ-001"


# ── ① kg_get_schema ─────────────────────────────────────────


def test_get_schema():
    out = tools.run_tool("kg_get_schema")
    assert out["error"] is None
    assert len(out["node_types"]) == 8
    assert len(out["relation_types"]) == 8
    assert out["node_types"]["Device"]["label"] == "设备"
    assert out["relation_types"]["located_in"]["subject"] == "Device"


# ── ② kg_search_entities ────────────────────────────────────


def test_search_by_keyword():
    out = tools.run_tool("kg_search_entities", keyword="气瓶")
    names = [m["name"] for m in out["matches"]]
    assert "七氟丙烷驱动气瓶" in names
    assert "气体灭火气瓶间" in names


def test_search_by_type_and_keyword():
    out = tools.run_tool("kg_search_entities", keyword="王", entity_type="Person")
    assert [m["entity_id"] for m in out["matches"]] == ["P-RESP-01"]


def test_search_alias_hit():
    out = tools.run_tool("kg_search_entities", keyword="气瓶间")
    assert out["matches"][0]["entity_id"] == ROOM


def test_search_not_found():
    out = tools.run_tool("kg_search_entities", keyword="摩天轮")  # 图内必无的词
    assert out["error"]["code"] == "not_found"


def test_search_invalid_type():
    out = tools.run_tool("kg_search_entities", keyword="x", entity_type="Robot")
    assert out["error"]["code"] == "invalid_input"


# ── ③ kg_get_entity ─────────────────────────────────────────


def test_get_entity_by_name():
    out = tools.run_tool("kg_get_entity", entity_id="七氟丙烷驱动气瓶")
    assert out["error"] is None
    assert out["entity"]["entity_id"] == DEV
    assert "设备编号" in out["entity"]["attrs"]          # 登记表字段原样保留
    assert out["entity"]["attrs"]["使用状态"] == "在用"


def test_get_entity_not_found():
    out = tools.run_tool("kg_get_entity", entity_id="不存在的设备")
    assert out["error"]["code"] == "not_found"


def test_resolve_ambiguous():
    # 构造共享别名的两个实体，验证 ambiguous 分支；测完重建种子图清理现场
    store = get_store()
    store.add_entity("__A1", "Person", "张三", aliases=["老张"])
    store.add_entity("__A2", "Person", "张三丰", aliases=["老张"])
    try:
        _, err = tools._resolve(store, "老张")
        assert err is not None and err.code == "ambiguous"
    finally:
        get_store(rebuild=True)


# ── ④ kg_get_relations ──────────────────────────────────────


def test_relations_of_device():
    out = tools.run_tool("kg_get_relations", entity_id=DEV)
    rels = {(e["direction"], e["relation"]) for e in out["edges"]}
    # 设备的 6 条出边：位置/部门/供应商/三类人员
    assert rels == {
        ("out", "located_in"),
        ("out", "managed_by_dept"),
        ("out", "supplied_by"),
        ("out", "has_responsible_person"),
        ("out", "received_by"),
        ("out", "has_manage_person"),
    }


def test_relations_reverse_room_to_device():
    out = tools.run_tool(
        "kg_get_relations", entity_id="气瓶间", direction="in", relation="located_in"
    )
    assert [e["other"]["entity_id"] for e in out["edges"]] == [DEV]


def test_relations_part_of_both_directions():
    out = tools.run_tool("kg_get_relations", entity_id=FLR, relation="part_of")
    pairs = {(e["direction"], e["other"]["name"]) for e in out["edges"]}
    assert pairs == {("out", "A座"), ("in", "气体灭火气瓶间")}


def test_relations_invalid_direction():
    out = tools.run_tool("kg_get_relations", entity_id=DEV, direction="sideways")
    assert out["error"]["code"] == "invalid_input"


# ── ⑤ kg_find_path ──────────────────────────────────────────


def test_find_path_direct_edge():
    out = tools.run_tool("kg_find_path", source_id=DEV, target_id=DEPT)
    assert out["found"] is True
    assert len(out["hops"]) == 1
    assert out["hops"][0]["relation"] == "managed_by_dept"
    assert out["hops"][0]["from_name"] == "七氟丙烷驱动气瓶"


def test_find_path_two_hops():
    out = tools.run_tool("kg_find_path", source_id=ROOM, target_id=DEPT)
    assert out["found"] is True
    assert len(out["hops"]) == 2


def test_find_path_no_path_within_hops():
    out = tools.run_tool("kg_find_path", source_id=PRJ, target_id=DEPT, max_hops=1)
    assert out["found"] is False
    assert out["error"]["code"] == "not_found"


# ── ⑥ kg_get_space_chain ────────────────────────────────────


def test_space_chain_of_device():
    out = tools.run_tool("kg_get_space_chain", entity_id=DEV)
    chain = [c["name"] for c in out["chain"]]
    assert chain == ["七氟丙烷驱动气瓶", "气体灭火气瓶间", "AB1F", "A座", "示范广场项目部"]


def test_space_chain_of_room():
    out = tools.run_tool("kg_get_space_chain", entity_id=ROOM)
    assert [c["entity_type"] for c in out["chain"]] == [
        "Room", "Floor", "Building", "Project",
    ]


def test_space_chain_of_person_rejected():
    out = tools.run_tool("kg_get_space_chain", entity_id="王建国")
    assert out["error"]["code"] == "invalid_input"
    assert "kg_get_relations" in out["error"]["hint"]


# ── 注册表与 OpenAI 导出 ─────────────────────────────────────


def test_registry_has_seven_tools():
    assert sorted(KG_TOOL_REGISTRY) == [
        "kg_count_entities",
        "kg_find_path",
        "kg_get_entity",
        "kg_get_relations",
        "kg_get_schema",
        "kg_get_space_chain",
        "kg_search_entities",
    ]


def test_run_tool_unknown_name():
    out = tools.run_tool("check_billing_status")
    assert out["error"]["code"] == "invalid_input"


def test_run_tool_invalid_kwargs():
    out = tools.run_tool("kg_search_entities", limit=0)  # 违反 ge=1
    assert out["error"]["code"] == "invalid_input"


def test_as_openai_tools():
    specs = tools.as_openai_tools()
    assert len(specs) == 7
    for spec in specs:
        assert spec["type"] == "function"
        fn = spec["function"]
        assert fn["name"].startswith("kg_")
        assert fn["description"]
        assert "properties" in fn["parameters"] or fn["parameters"].get("type") == "object"


# ── ⑦ kg_count_entities —— 跨区域聚合统计 ─────────────────────


def test_count_toilets_in_building_male_restrooms():
    """「A栋男洗手间马桶数量」：一次调用出总数（30 层 × 3 马桶 = 90）。"""
    out = tools.run_tool(
        "kg_count_entities", keyword="马桶", scope="A栋", location_keyword="男洗手间"
    )
    assert out["error"] is None
    assert out["count"] == 90
    assert out["scope"]["entity_id"] == "BLD-A"
    assert all("男洗手间" in m["name"] for m in out["matched"])
    assert not out["truncated"]


def test_count_location_synonym_normalized():
    """口语「男卫生间/男厕所」自动归一为规范名「男洗手间」，命中同一批实体。"""
    a = tools.run_tool("kg_count_entities", keyword="马桶",
                       scope="A栋", location_keyword="男卫生间")
    b = tools.run_tool("kg_count_entities", keyword="马桶",
                       scope="A栋", location_keyword="男洗手间")
    c = tools.run_tool("kg_count_entities", keyword="马桶",
                       scope="A栋", location_keyword="男厕所")
    assert a["count"] == b["count"] == c["count"] == 90


def test_count_floor_scope_and_no_scope():
    # 单层男卫马桶 = 3；全图马桶 = A栋 30 层 × (男3+女3) + B栋 6 层 × (男3+女3) = 216
    out = tools.run_tool("kg_count_entities", keyword="马桶",
                         scope="FLR-A-25", location_keyword="男卫生间")
    assert out["count"] == 3
    out_all = tools.run_tool("kg_count_entities", keyword="马桶")
    assert out_all["count"] == 216
    assert out_all["scope"] is None


def test_count_scope_not_found():
    out = tools.run_tool("kg_count_entities", keyword="马桶", scope="摩天轮")
    assert out["error"]["code"] == "not_found"


def test_count_invalid_type():
    out = tools.run_tool("kg_count_entities", keyword="马桶", entity_type="Robot")
    assert out["error"]["code"] == "invalid_input"


# ── 存储层：持久化 roundtrip ─────────────────────────────────


def test_store_persistence_roundtrip(tmp_path):
    from wagent_backend.graphRAG.store import GraphStore

    store = get_store()
    path = store.save(tmp_path / "rt.json")
    loaded = GraphStore.load(path)
    assert loaded.to_dict() == store.to_dict()


def test_next_entity_id_monotonic():
    store = get_store()
    a = store.next_entity_id("Person")
    store.add_entity(a, "Person", "临时人")
    try:
        assert store.next_entity_id("Person") != a
    finally:
        get_store(rebuild=True)
