"""图谱手工编辑 API 测试 —— 增/删/改/关联，全程不调真实模型。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from wagent_backend.web.app import create_app

DEV = "DEV-HFC227-001"
FLR = "FLR-A-B1"
P_RESP = "P-RESP-01"


@pytest.fixture()
def client():
    return TestClient(create_app())


@pytest.fixture(autouse=True)
def _reset_store():
    """每个用例前后都重灌种子，互不影响也不污染其他测试文件。"""
    from wagent_backend.graphRAG.store import get_store

    get_store(rebuild=True)
    yield
    get_store(rebuild=True)


# ── schema ──────────────────────────────────────────────


def _stats(client) -> dict:
    """实时统计（图谱已含公共设施层，用例一律对基线做相对断言）。"""
    return client.get("/api/graph").json()["stats"]


def test_schema_endpoint(client):
    r = client.get("/api/graph/schema")
    assert r.status_code == 200
    body = r.json()
    assert len(body["node_types"]) == 8
    assert len(body["relation_types"]) == 8
    assert body["relation_types"]["located_in"]["subject"] == "Device"
    assert body["relation_types"]["located_in"]["object"] == "Room"


# ── 新建节点 + 关系 ──────────────────────────────────────


def test_create_entity_with_link_out(client):
    """direction=out：新节点 → 目标（新 Room part_of 已有 Floor）。"""
    before = _stats(client)
    r = client.post("/api/graph/entity", json={
        "type": "Room", "name": "新风机房", "attrs": {"空间类型": "设备用房"},
        "link": {"target_id": FLR, "relation": "part_of", "direction": "out"},
    })
    assert r.status_code == 201
    body = r.json()
    assert body["entity"]["entity_type"] == "Room"
    assert body["entity"]["attrs"]["空间类型"] == "设备用房"
    assert body["edge"] == {"from": body["entity"]["entity_id"], "to": FLR,
                            "relation": "part_of"}
    stats = _stats(client)
    assert stats["node_count"] == before["node_count"] + 1
    assert stats["edge_count"] == before["edge_count"] + 1


def test_create_entity_with_link_in(client):
    """direction=in：目标 → 新节点（已有 Device has_responsible_person 新 Person）。"""
    r = client.post("/api/graph/entity", json={
        "type": "Person", "name": "张三",
        "link": {"target_id": DEV, "relation": "has_responsible_person",
                 "direction": "in"},
    })
    assert r.status_code == 201
    new_id = r.json()["entity"]["entity_id"]
    assert r.json()["edge"] == {"from": DEV, "to": new_id,
                                "relation": "has_responsible_person"}
    edges = client.get(f"/api/graph/entity/{new_id}").json()["edges"]
    assert edges[0]["direction"] == "in" and edges[0]["other"]["entity_id"] == DEV


def test_create_entity_invalid_relation_400_and_no_leftover(client):
    """端点类型不符 → 400，且不残留半截节点。"""
    before = _stats(client)
    r = client.post("/api/graph/entity", json={
        "type": "Person", "name": "李四",
        "link": {"target_id": DEV, "relation": "located_in", "direction": "out"},
    })
    assert r.status_code == 400
    assert "主体应为" in r.json()["detail"]
    assert _stats(client)["node_count"] == before["node_count"]


def test_create_entity_bad_type_400(client):
    r = client.post("/api/graph/entity", json={"type": "Robot", "name": "x"})
    assert r.status_code == 400


def test_create_entity_link_target_404(client):
    r = client.post("/api/graph/entity", json={
        "type": "Person", "name": "王五",
        "link": {"target_id": "不存在", "relation": "received_by", "direction": "in"},
    })
    assert r.status_code == 404


# ── 已有节点建边 ─────────────────────────────────────────


def test_link_existing_nodes(client):
    before = _stats(client)
    r = client.post("/api/graph/relation", json={
        "src": DEV, "dst": P_RESP, "relation": "received_by",
    })
    assert r.status_code == 201
    assert _stats(client)["edge_count"] == before["edge_count"] + 1


def test_link_existing_duplicate_400(client):
    r = client.post("/api/graph/relation", json={
        "src": DEV, "dst": P_RESP, "relation": "has_responsible_person",
    })
    assert r.status_code == 400
    assert "已存在" in r.json()["detail"]


def test_link_existing_wrong_direction_400(client):
    """方向反了：Person 不能是 has_responsible_person 的主体。"""
    r = client.post("/api/graph/relation", json={
        "src": P_RESP, "dst": DEV, "relation": "has_responsible_person",
    })
    assert r.status_code == 400
    assert "主体应为" in r.json()["detail"]


def test_link_existing_endpoint_404(client):
    r = client.post("/api/graph/relation", json={
        "src": DEV, "dst": "不存在", "relation": "received_by",
    })
    assert r.status_code == 404


# ── 编辑节点 ─────────────────────────────────────────────


def test_patch_entity_merge_attrs(client):
    r = client.patch(f"/api/graph/entity/{DEV}", json={
        "name": "七氟丙烷驱动气瓶（改名）",
        "attrs": {"品牌": "新品牌", "巡检备注": "手工补录", "使用状态": ""},
    })
    assert r.status_code == 200
    ent = r.json()["entity"]
    assert ent["name"] == "七氟丙烷驱动气瓶（改名）"
    assert ent["attrs"]["品牌"] == "新品牌"          # 覆盖
    assert ent["attrs"]["巡检备注"] == "手工补录"     # 新增
    assert "使用状态" not in ent["attrs"]             # 空字符串=删除
    assert "设备编号" in ent["attrs"]                 # 未提交的键不动
    # 已落盘
    from wagent_backend.graphRAG.store import GraphStore

    assert GraphStore.load().entity(DEV)["attrs"]["品牌"] == "新品牌"


def test_patch_entity_404(client):
    r = client.patch("/api/graph/entity/不存在", json={"name": "x"})
    assert r.status_code == 404


def test_patch_entity_empty_name_400(client):
    r = client.patch(f"/api/graph/entity/{DEV}", json={"name": "  "})
    assert r.status_code == 400


# ── 删除节点 ─────────────────────────────────────────────


def test_delete_entity_cascades_edges(client):
    before = _stats(client)
    r = client.delete(f"/api/graph/entity/{DEV}")
    assert r.status_code == 200
    body = r.json()
    assert body["deleted"]["entity_id"] == DEV
    assert body["edge_count"] == 6                   # 种子中设备的 6 条出入边
    assert len(body["removed_edges"]) == 6
    assert client.get(f"/api/graph/entity/{DEV}").status_code == 404
    stats = _stats(client)
    assert stats["node_count"] == before["node_count"] - 1
    assert stats["edge_count"] == before["edge_count"] - 6


def test_delete_entity_404(client):
    assert client.delete("/api/graph/entity/不存在").status_code == 404
