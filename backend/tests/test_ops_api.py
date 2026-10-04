"""ops Web API 测试 —— TestClient + fake LLM（真实模型端到端见 README 演示步骤）。"""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from wagent_backend.llm.embedder import local_embed
from wagent_backend.web import routes_ops
from wagent_backend.web.app import create_app

from _baseline_helpers import stream_of

DECISION = (
    '```json\n{"space_id": "SP-A-25-E", "asset_id": "FCU-A25-01", '
    '"symptom": "no_cooling", "root_cause": "valve_actuator_failure", '
    '"root_cause_confidence": 0.9, "is_repeat_fault": true, '
    '"repeat_evidence": ["WO-B25-0811"], '
    '"recommended_action": "replace_valve_actuator", "liability": "unclear", '
    '"liability_basis": "no_basis", "escalate": false, '
    '"memory_ids_used": [], "tenant_message": "已安排换阀。", '
    '"manager_message": "复发，换阀。"}\n```'
)


def _fake_complete(messages, tools):
    return {"role": "assistant", "content": DECISION}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    monkeypatch.setenv("WAGENT_SESSIONS_DIR", str(tmp_path / "sessions"))
    monkeypatch.setenv("WAGENT_EMBEDDING", "local")
    app = create_app()
    app.dependency_overrides[routes_ops._get_complete] = lambda: stream_of(_fake_complete)
    return TestClient(app)


def test_chat_creates_session_and_archives_decision(client):
    r = client.post("/api/ops/chat", json={
        "text": "A座25楼东侧空调又不制冷了", "tier": "full",
        "as_of": "2026-08-23T10:00:00",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["result"]["reason"] == "completed"
    assert data["result"]["decision"]["root_cause"] == "valve_actuator_failure"
    sid = data["session_id"]
    assert sid.startswith("S-")

    # 会话可回放：完整事件流
    r2 = client.get(f"/api/ops/session/{sid}")
    assert r2.status_code == 200
    assert r2.json()["meta"]["tier"] == "full"
    assert any(e["type"] == "decision" for e in r2.json()["events"])

    # 第二轮复用同一会话（as_of 固化）
    r3 = client.post("/api/ops/chat", json={
        "text": "麻烦尽快", "session_id": sid,
    })
    assert r3.status_code == 200 and r3.json()["session_id"] == sid
    assert r3.json()["as_of"] == "2026-08-23T10:00:00"


def test_safety_text_escalates_without_llm(client):
    r = client.post("/api/ops/chat", json={"text": "电梯困人了", "tier": "full"})
    data = r.json()
    assert data["result"]["reason"] == "safety"
    assert data["result"]["escalate"]["ticket_id"].startswith("TKT-")


def test_sessions_list_and_insights(client):
    client.post("/api/ops/chat", json={"text": "A1106 空调开不了", "tier": "l1"})
    lst = client.get("/api/ops/sessions").json()["sessions"]
    assert len(lst) == 1 and lst[0]["tier"] == "l1"

    ins = client.get("/api/ops/insights").json()
    assert len(ins["insights"]) == 2
    assert ins["truth_leaks"] == []
    ids = {i["insight_id"] for i in ins["insights"]}
    assert "INS-REPLAY-001" in ids


def test_wo_trace_endpoint(client):
    r = client.get("/api/ops/wo/WO-B25-0811")
    assert r.status_code == 200
    d = r.json()
    assert d["work_order"]["symptom"] == "no_cooling"
    assert any(e["event_type"] == "closed" for e in d["events"])
    assert client.get("/api/ops/wo/WO-NOPE").status_code == 404


def test_reset_rebuilds_seed(client):
    client.post("/api/ops/chat", json={"text": "x", "tier": "off"})
    r = client.post("/api/ops/chat", json={"text": "空调坏", "tier": "full"})
    assert r.json()["result"]["reason"] == "completed"
    assert client.post("/api/ops/reset").json()["ok"] is True
    after = client.get("/api/ops/insights").json()["insights"]
    assert len(after) == 2  # 回到种子


def test_ops_page_served(client):
    r = client.get("/ops")
    assert r.status_code == 200
    assert "三栏" in r.text or "租户视角" in r.text
    # / 默认首页 = ops 回放台；/ops 是别名；图谱页面挪到 /graph
    assert client.get("/").text == r.text
    g = client.get("/graph")
    assert g.status_code == 200 and "GraphRAG" in g.text


def test_chat_validates_tier(client):
    r = client.post("/api/ops/chat", json={"text": "x", "tier": "l9"})
    assert r.status_code == 400


# ── SSE 流式接口 ─────────────────────────────────────────

def _streaming_complete(messages, tools):
    """先调一次工具，再给 Decision —— 验证事件逐条流出的顺序。"""
    if not any(m.get("role") == "user" and any(
            b.get("type") == "tool-result" for b in m.get("content") or [])
            for m in messages):
        return {"role": "assistant", "content": "我先解析报修位置。",
                "tool_calls": [{
                    "id": "call-1", "type": "function",
                    "name": "resolve_space",
                    "arguments": json.dumps(
                        {"text": "A座25楼东侧会议室空调又不制冷了"},
                        ensure_ascii=False),
                }]}
    return {"role": "assistant", "content": DECISION}


def _parse_sse(text: str) -> list[dict]:
    frames = [ln[len("data: "):] for ln in text.splitlines()
              if ln.startswith("data: ")]
    return [json.loads(f) for f in frames]


def test_chat_stream_emits_events_in_order(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    monkeypatch.setenv("WAGENT_SESSIONS_DIR", str(tmp_path / "sessions"))
    monkeypatch.setenv("WAGENT_EMBEDDING", "local")
    app = create_app()
    app.dependency_overrides[routes_ops._get_complete] = lambda: stream_of(_streaming_complete)
    client = TestClient(app)

    r = client.post("/api/ops/chat/stream", json={
        "text": "A座25楼东侧空调又不制冷了", "tier": "full",
        "as_of": "2026-08-23T10:00:00",
    })
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    msgs = _parse_sse(r.text)
    assert msgs[0]["type"] == "__start" and msgs[0]["session_id"].startswith("S-")
    assert msgs[-1]["type"] == "__done"
    assert msgs[-1]["result"]["reason"] == "completed"
    assert msgs[-1]["error"] is None

    types = [m["type"] for m in msgs[1:-1]]
    # 事件按产生顺序流出：用户消息 → 请求头 → chunk×N → message → 工具对 → 决策 → 收尾
    assert types[0] == "turn/start" and types[1] == "user/message"
    assert types[2] == "request/header" and "request/context" in types
    assert "assistant/chunk" in types
    assert types.index("assistant/chunk") < types.index("assistant/message")
    assert "tool/call" in types and "tool/result" in types
    assert types.index("tool/call") < types.index("tool/result")
    assert "decision" in types and types[-1] == "turn/end"

    # 工具事件带 call_id / digest，前端据此回填「执行中」卡片；
    # 且工具在工作线程里真实执行成功（连接线程归属正确）
    call = next(m for m in msgs if m["type"] == "tool/call")
    result = next(m for m in msgs if m["type"] == "tool/result")
    assert call["data"]["callId"] == "call-1"
    tb = result["data"]["message"]["content"][0]   # ToolResultMessage 单 tool-result 块
    assert tb["toolCallId"] == "call-1" and not tb.get("isError")
    assert result["data"]["meta"]["digest"]
    payload = json.loads(tb["content"][0]["text"])  # 完整结果在内容文本内部
    assert payload["error"] is None
    assert payload["matches"][0]["space_id"] == "SP-A-25-E"


def test_chat_stream_safety_short_circuit(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    monkeypatch.setenv("WAGENT_SESSIONS_DIR", str(tmp_path / "sessions"))
    monkeypatch.setenv("WAGENT_EMBEDDING", "local")
    app = create_app()
    calls = []
    app.dependency_overrides[routes_ops._get_complete] = \
        lambda: lambda m, t: calls.append(1)  # 只记调用，模型不应被碰到
    client = TestClient(app)

    msgs = _parse_sse(client.post("/api/ops/chat/stream", json={
        "text": "三楼电梯困人了，快来人！", "tier": "full",
    }).text)
    assert msgs[-1]["result"]["reason"] == "safety"
    assert msgs[-1]["error"] is None
    assert msgs[-1]["result"]["escalate"]["ticket_id"].startswith("TKT-")
    assert not calls


def test_sessions_search(client):
    """L5 跨会话检索（纯 Web 端点）：用户原文包含匹配，空查询空结果。"""
    client.post("/api/ops/chat", json={"text": "A座25楼东侧空调又不制冷了", "tier": "l1"})
    client.post("/api/ops/chat", json={"text": "B座3楼漏水", "tier": "l1"})
    r = client.get("/api/ops/sessions/search", params={"q": "空调"}).json()
    assert r["query"] == "空调"
    assert len(r["sessions"]) == 1
    assert "空调" in r["sessions"][0]["matched_text"]
    assert r["sessions"][0]["tier"] == "l1"
    assert client.get("/api/ops/sessions/search", params={"q": " "}).json()["sessions"] == []
    assert client.get("/api/ops/sessions/search", params={"q": "不存在词"}).json()["sessions"] == []


def test_spaces_hierarchy(client):
    """位置选择器数据源：四级字段齐全（项目/楼栋/楼层/位置）。"""
    r = client.get("/api/ops/spaces")
    assert r.status_code == 200
    spaces = r.json()["spaces"]
    assert spaces
    s = spaces[0]
    assert {"space_id", "property_name", "building_name", "floor"} <= set(s)
    assert any(s["space_id"] == "SP-A-25-E" for s in spaces)


def test_teams_endpoint(client):
    """三班组及其成员：环境/秩序有人（种子），工程为 HVAC/ELEC/PLUMB。"""
    r = client.get("/api/ops/teams")
    assert r.status_code == 200
    teams = {t["team"]: t["members"] for t in r.json()["teams"]}
    assert set(teams) == {"秩序", "环境", "工程"}
    assert [m["technician_id"] for m in teams["环境"]] == ["TEC-006", "TEC-007"]
    assert [m["technician_id"] for m in teams["秩序"]] == ["TEC-008", "TEC-009"]
    assert len(teams["工程"]) == 5


def test_dispatch_wo(client):
    """项目经理派单：写 append-only dispatched 事件；班组/人选校验。"""
    client.get("/api/ops/teams")  # 触发建库灌种子
    r = client.post("/api/ops/wo/WO-B25-0811/dispatch",
                    json={"team": "环境", "technician_id": "TEC-006"})
    assert r.status_code == 200 and r.json()["ok"]
    d = client.get("/api/ops/wo/WO-B25-0811").json()
    last = d["events"][-1]
    assert last["event_type"] == "dispatched" and last["technician_id"] == "TEC-006"
    assert "环境" in last["note"]

    assert client.post("/api/ops/wo/WO-B25-0811/dispatch",
                       json={"team": "保洁"}).status_code == 400
    assert client.post("/api/ops/wo/WO-B25-0811/dispatch",
                       json={"team": "工程", "technician_id": "TEC-006"}).status_code == 400
    assert client.post("/api/ops/wo/WO-NOPE/dispatch",
                       json={"team": "工程"}).status_code == 404


def test_adjust_liability_endpoint(client):
    client.get("/api/ops/teams")  # 触发建库灌种子
    r = client.post("/api/ops/wo/WO-B25-0811/liability", json={"liability": "owner"})
    assert r.status_code == 200 and r.json()["liability"] == "owner"

    # append-only 留痕：溯源流水最后一条即调整事件
    d = client.get("/api/ops/wo/WO-B25-0811").json()
    last = d["events"][-1]
    assert last["event_type"] == "liability_adjusted" and last["liability"] == "owner"
    assert "物业" in last["note"]

    # shared 由判责产出、不在经理手选范围；非法值与不存在工单分别 400/404
    assert client.post("/api/ops/wo/WO-B25-0811/liability",
                       json={"liability": "shared"}).status_code == 400
    assert client.post("/api/ops/wo/WO-NOPE/liability",
                       json={"liability": "owner"}).status_code == 404


def test_asset_detail_endpoint(client):
    """设备 360：台账 + 运行快照 + 工单列表（状态从流水推导）。"""
    client.get("/api/ops/teams")  # 触发建库灌种子
    r = client.get("/api/ops/asset/FCU-A25-01")
    assert r.status_code == 200
    body = r.json()
    assert body["asset"]["asset_name"] == "风机盘管" and body["asset"]["category"] == "HVAC"
    assert body["runtime"]["lock_status"] == "normal"
    assert len(body["workorders"]) == 3  # 故事 A 复发链三单
    assert {w["status"] for w in body["workorders"]} == {"已完成"}

    # 状态推导：无事件=待派单；有 dispatched 无 closed=维修中
    from wagent_backend.ops.data.db import connect

    conn = connect()
    conn.execute("INSERT INTO work_order (wo_id, created_at, space_id, asset_id,"
                 " raw_text, symptom, urgency) VALUES"
                 " ('WO-T-0901','2026-09-01T09:00:00','SP-A-13-WCM','FAUCET-A13-01',"
                 " '水龙头滴水','water_leak','一般')")
    conn.execute("INSERT INTO work_order (wo_id, created_at, space_id, asset_id,"
                 " raw_text, symptom, urgency) VALUES"
                 " ('WO-T-0902','2026-09-02T09:00:00','SP-A-13-WCM','FAUCET-A13-01',"
                 " '水龙头又滴水','water_leak','一般')")
    conn.execute("INSERT INTO work_order_event (wo_id,ts,event_type) VALUES"
                 " ('WO-T-0902','2026-09-02T10:00:00','dispatched')")
    conn.commit()
    conn.close()

    r2 = client.get("/api/ops/asset/FAUCET-A13-01")
    assert r2.status_code == 200
    st = {w["wo_id"]: w["status"] for w in r2.json()["workorders"]}
    assert st == {"WO-T-0901": "待派单", "WO-T-0902": "维修中"}

    assert client.get("/api/ops/asset/NOPE").status_code == 404
