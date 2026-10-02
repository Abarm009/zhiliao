"""Web API 测试 —— TestClient + 依赖注入替换 LLM，全程不调真实模型。"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from wagent_backend.web import deps
from wagent_backend.web.app import create_app


@pytest.fixture()
def client():
    app = create_app()
    return TestClient(app)


# ── 基础与图谱 ──────────────────────────────────────────────


def test_health(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_graph_data(client):
    r = client.get("/api/graph")
    assert r.status_code == 200
    data = r.json()
    # 种子含公共设施层（500+ 节点），断言结构而非具体计数
    assert data["stats"]["node_count"] == len(data["nodes"])
    ids = {n["id"] for n in data["nodes"]}
    assert "DEV-HFC227-001" in ids and "BLD-A" in ids and "FAU-A13-M" in ids
    assert len(data["categories"]) == 8
    assert all("label" in e for e in data["edges"])


def test_graph_entity_found(client):
    r = client.get("/api/graph/entity/DEV-HFC227-001")
    assert r.status_code == 200
    body = r.json()
    assert body["entity"]["name"] == "七氟丙烷驱动气瓶"
    assert len(body["edges"]) == 6


def test_graph_entity_404(client):
    assert client.get("/api/graph/entity/不存在").status_code == 404


def test_graph_reset_roundtrip(client):
    # 先让图长大，再重置回种子
    def fake(messages, **kw):
        return json.dumps(
            [
                {
                    "subject": {"name": "测试风机", "type": "Device"},
                    "predicate": "managed_by_dept",
                    "object": {"name": "工程部", "type": "Department"},
                    "attrs": {},
                }
            ],
            ensure_ascii=False,
        )

    app = client.app
    # 注意：override 必须是零参函数，FastAPI 会解析其签名注入 query 参数
    app.dependency_overrides[deps.get_complete_text] = lambda: fake
    before = client.get("/api/graph").json()["stats"]["node_count"]
    r = client.post("/api/extract", data={"text": "测试工单"})
    assert r.json()["grown"] is True
    assert client.get("/api/graph").json()["stats"]["node_count"] == before + 1

    reset = client.post("/api/graph/reset")
    assert reset.json()["node_count"] == before
    app.dependency_overrides.clear()


# ── 聊天（注入假 complete_msg：第一轮调工具，第二轮给结论） ──


def test_chat_with_tool_calls(client):
    state = {"calls": 0}

    def fake_complete(messages, tools=None):
        state["calls"] += 1
        if state["calls"] == 1:
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "name": "kg_get_space_chain",
                        "arguments": json.dumps({"entity_id": "七氟丙烷驱动气瓶"}),
                    }
                ],
            }
        # 第二轮：模型应已收到工具结果
        tool_msgs = [m for m in messages if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        assert "气体灭火气瓶间" in tool_msgs[0]["content"]
        return {"role": "assistant", "content": "它装在气体灭火气瓶间。"}

    client.app.dependency_overrides[deps.get_complete_msg] = lambda: fake_complete
    r = client.post(
        "/api/chat", json={"message": "七氟丙烷驱动气瓶在哪？", "history": []}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["reply"] == "它装在气体灭火气瓶间。"
    assert body["rounds"] == 2
    assert body["tool_calls"][0]["name"] == "kg_get_space_chain"
    client.app.dependency_overrides.clear()


def test_chat_empty_message_rejected(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422


# ── 抽取 ────────────────────────────────────────────────────


def test_extract_requires_input(client):
    assert client.post("/api/extract").status_code == 400


def test_extract_text_grows_graph(client):
    def fake(messages, **kw):
        return json.dumps(
            [
                {
                    "subject": {"name": "B座12层1203室风机盘管", "type": "Device"},
                    "predicate": "located_in",
                    "object": {"name": "B座12层1203室", "type": "Room"},
                    "attrs": {"现象": "不制冷"},
                },
                {
                    "subject": {"name": "B座12层1203室风机盘管", "type": "Device"},
                    "predicate": "has_manage_person",
                    "object": {"name": "刘志强", "type": "Person"},
                    "attrs": {},
                },
            ],
            ensure_ascii=False,
        )

    client.app.dependency_overrides[deps.get_complete_text] = lambda: fake
    before = client.get("/api/graph").json()["stats"]["node_count"]
    r = client.post("/api/extract", data={"text": "B座1203空调不制冷，刘志强处理。"})
    assert r.status_code == 200
    body = r.json()
    assert body["grown"] is True
    assert len(body["added_nodes"]) == 3      # 设备/房间/人员
    assert len(body["added_edges"]) == 2
    assert client.get("/api/graph").json()["stats"]["node_count"] == before + 3
    client.app.dependency_overrides.clear()
    from wagent_backend.graphRAG.store import get_store

    get_store(rebuild=True)  # 清理现场


def test_extract_bad_llm_output_is_502(client):
    client.app.dependency_overrides[deps.get_complete_text] = (
        lambda: (lambda messages, **kw: "模型今天心情不好")
    )
    assert client.post("/api/extract", data={"text": "工单"}).status_code == 502
    client.app.dependency_overrides.clear()
