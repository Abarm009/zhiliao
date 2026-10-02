"""抽取器单测 —— 假 LLM 注入，验证解析/本体校验/实体链接/去重入图。"""

from __future__ import annotations

import json

from wagent_backend.graphRAG.extractor import TripleExtractor
from wagent_backend.graphRAG.store import get_store

# 一段典型工单对应的期望三元组
WO_TRIPLES = [
    {
        "subject": {"name": "B座12层1203室风机盘管", "type": "Device"},
        "predicate": "located_in",
        "object": {"name": "B座12层1203室", "type": "Room"},
        "attrs": {"现象": "空调不制冷", "处置": "清洗滤网"},
    },
    {
        "subject": {"name": "B座12层1203室风机盘管", "type": "Device"},
        "predicate": "has_manage_person",
        "object": {"name": "刘志强", "type": "Person"},
        "attrs": {},
    },
    {
        "subject": {"name": "B座12层1203室风机盘管", "type": "Device"},
        "predicate": "managed_by_dept",
        "object": {"name": "工程部", "type": "Department"},   # 已有实体 → 链接
        "attrs": {},
    },
]


def _fake_complete(payload):
    return lambda messages, **kw: payload


def _stats():
    s = get_store().stats()
    return s["node_count"], s["edge_count"]


def test_extract_and_apply_grows_graph():
    n0, e0 = _stats()
    ext = TripleExtractor(_fake_complete(json.dumps(WO_TRIPLES, ensure_ascii=False)))

    triples = ext.extract(text="B座12层1203室租户报修空调不制冷，工程部刘志强清洗滤网。")
    assert len(triples) == 3
    assert triples[0].attrs["现象"] == "空调不制冷"

    report = ext.apply(get_store(), triples)
    assert report.grown is True
    # 新建：设备、房间、刘志强；工程部已存在 → 链接不重建
    assert {n.name for n in report.added_nodes} == {
        "B座12层1203室风机盘管", "B座12层1203室", "刘志强",
    }
    assert len(report.added_edges) == 3
    n1, e1 = _stats()
    assert (n1, e1) == (n0 + 3, e0 + 3)

    # 属性挂到了设备节点上
    dev = get_store().find_by_name("B座12层1203室风机盘管")[0]
    assert get_store().entity(dev)["attrs"]["现象"] == "空调不制冷"

    get_store(rebuild=True)  # 清理现场


def test_apply_idempotent_same_order_twice():
    ext = TripleExtractor(_fake_complete(json.dumps(WO_TRIPLES, ensure_ascii=False)))
    ext.apply(get_store(), ext.extract(text="任意文本"))
    _, e1 = _stats()
    # 同一段工单再抽一次：不重复建节点/边
    report2 = ext.apply(get_store(), ext.extract(text="任意文本"))
    assert report2.grown is False
    _, e2 = _stats()
    assert e1 == e2
    get_store(rebuild=True)


def test_ontology_violations_skipped():
    bad = [
        {  # 未知关系
            "subject": {"name": "风机盘管", "type": "Device"},
            "predicate": "repaired_by",
            "object": {"name": "刘志强", "type": "Person"},
            "attrs": {},
        },
        {  # 主体类型不符（located_in 主体应为 Device）
            "subject": {"name": "刘志强", "type": "Person"},
            "predicate": "located_in",
            "object": {"name": "1203室", "type": "Room"},
            "attrs": {},
        },
        {  # 客体类型不符（located_in 客体应为 Room）
            "subject": {"name": "风机盘管", "type": "Device"},
            "predicate": "located_in",
            "object": {"name": "刘志强", "type": "Person"},
            "attrs": {},
        },
    ]
    ext = TripleExtractor(_fake_complete(json.dumps(bad, ensure_ascii=False)))
    report = ext.apply(get_store(), ext.extract(text="任意文本"))
    assert report.grown is False
    assert len(report.skipped) == 3
    assert any("未知关系" in s["reason"] for s in report.skipped)
    assert any("主体应为" in s["reason"] for s in report.skipped)
    assert any("客体应为" in s["reason"] for s in report.skipped)


def test_parse_tolerates_fenced_and_think_output():
    raw = "<think>让我想想…</think>\n```json\n" + json.dumps(
        WO_TRIPLES[:1], ensure_ascii=False
    ) + "\n```"
    ext = TripleExtractor(_fake_complete(raw))
    triples = ext.extract(text="任意")
    assert len(triples) == 1
    assert triples[0].predicate == "located_in"
    get_store(rebuild=True)


def test_parse_raises_on_garbage():
    ext = TripleExtractor(_fake_complete("抱歉我不知道"))
    import pytest

    with pytest.raises(ValueError):
        ext.extract(text="任意")


def test_extract_requires_input():
    ext = TripleExtractor(_fake_complete("[]"))
    import pytest

    with pytest.raises(ValueError):
        ext.extract()


def test_vendor_triple_blocked():
    """硬规则：工单抽取不建供应商节点（京东等购买渠道不是台账供应商）。"""
    payload = json.dumps([{
        "subject": {"name": "某新风机", "type": "Device"},
        "predicate": "supplied_by",
        "object": {"name": "京东", "type": "Vendor"},
        "attrs": {},
    }], ensure_ascii=False)
    ext = TripleExtractor(_fake_complete(payload))
    report = ext.apply(get_store(), ext.extract(text="任意文本"))
    assert not report.grown
    assert "不建供应商" in report.skipped[0]["reason"]
    assert not get_store().find_by_name("京东")
    get_store(rebuild=True)  # 清理现场


def test_room_synonym_links_to_existing_room():
    """口语同义词链接：「13楼男卫生间」应链接到已有的 RM-A-13-WCM（A栋13层男洗手间），
    不得新建游离的 EXT-ROO 节点（回归：演示图谱曾因此出现游离的「13楼男洗手间」）。"""
    payload = json.dumps([{
        "subject": {"name": "13楼男卫生间水龙头", "type": "Device"},
        "predicate": "located_in",
        "object": {"name": "13楼男卫生间", "type": "Room"},
        "attrs": {"现象": "漏水"},
    }], ensure_ascii=False)
    ext = TripleExtractor(_fake_complete(payload))
    n0, _ = _stats()
    report = ext.apply(get_store(), ext.extract(text="13楼男卫生间水龙头漏水"))
    # 只新增设备节点；房间链接到 RM-A-13-WCM
    assert [n.entity_id for n in report.added_nodes] != []
    assert all(not n.entity_id.startswith("EXT-ROO") for n in report.added_nodes)
    assert report.added_edges[0]["to"] == "RM-A-13-WCM"
    n1, _ = _stats()
    assert n1 == n0 + 1
    get_store(rebuild=True)  # 清理现场
