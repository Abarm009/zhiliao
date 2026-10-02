"""space_id 桥接端点测试 —— 图谱 ↔ ops 工单只读互查（临时库，不碰真实数据）。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from wagent_backend.llm.embedder import local_embed
from wagent_backend.ops.data.db import connect, init_db
from wagent_backend.ops.data.seed import seed
from wagent_backend.web.app import create_app

DEV = "DEV-HFC227-001"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """受控 ops 库：种子数据 + 一条绑定 SP-A-13-WCM 的工单。"""
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    conn = connect()
    init_db(conn)
    seed(conn, local_embed)
    conn.execute(
        "INSERT INTO work_order (wo_id, created_at, space_id, raw_text, symptom, urgency)"
        " VALUES ('WO-T-001', '2026-09-01T09:34:00', 'SP-A-13-WCM',"
        "         'a栋13楼男卫生间有异味', 'odor', '一般')",
    )
    conn.commit()
    conn.close()
    return TestClient(create_app())


@pytest.fixture(autouse=True)
def _reset_store():
    """每个用例前后都重灌种子图谱（与 test_graph_edit.py 同一约定）。"""
    from wagent_backend.graphRAG.store import get_store

    get_store(rebuild=True)
    yield
    get_store(rebuild=True)


def test_entity_workorders_without_space_id(client):
    """节点无 space_id 属性 → 空列表，不报错。"""
    r = client.get(f"/api/graph/entity/{DEV}/workorders")
    assert r.status_code == 200
    assert r.json() == {"space_id": None, "workorders": []}


def test_entity_workorders_404(client):
    assert client.get("/api/graph/entity/NOPE/workorders").status_code == 404


def test_by_space_404(client):
    assert client.get("/api/graph/by-space/SP-NONE").status_code == 404


def test_bridge_roundtrip(client):
    """建带 space_id 的 Room 节点 → 双向互查都通。"""
    r = client.post("/api/graph/entity", json={
        "type": "Room", "name": "13楼男洗手间",
        "attrs": {"space_id": "SP-A-13-WCM"},
    })
    assert r.status_code == 201
    eid = r.json()["entity"]["entity_id"]

    r = client.get("/api/graph/by-space/SP-A-13-WCM")
    assert r.status_code == 200
    assert r.json()["entity"]["entity_id"] == eid

    r = client.get(f"/api/graph/entity/{eid}/workorders")
    assert r.status_code == 200
    body = r.json()
    assert body["space_id"] == "SP-A-13-WCM"
    assert [w["wo_id"] for w in body["workorders"]] == ["WO-T-001"]
    assert body["workorders"][0]["symptom"] == "odor"
