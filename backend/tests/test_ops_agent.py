"""Agent 主循环测试 —— 用脚本化 fake complete（不调真实模型）。"""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from wagent_backend.llm.embedder import local_embed
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.runner import parse_decision, run_turn
from wagent_backend.ops.data.db import connect, init_db
from wagent_backend.ops.data.seed import seed
from wagent_backend.ops.tools.context import ToolContext

from _baseline_helpers import stream_of

AS_OF = datetime(2026, 8, 23, 10, 0)

DECISION_JSON = """收尾：给出最终决策。

```json
{
  "space_id": "SP-A-25-E",
  "asset_id": "FCU-A25-01",
  "symptom": "no_cooling",
  "root_cause": "valve_actuator_failure",
  "root_cause_confidence": 0.9,
  "is_repeat_fault": true,
  "repeat_evidence": ["WO-B25-0720", "WO-B25-0811"],
  "recommended_action": "replace_valve_actuator",
  "liability": "unclear",
  "liability_basis": "no_basis",
  "estimated_cost_cny": 1800,
  "escalate": false,
  "escalate_reason": null,
  "memory_ids_used": ["INS-REPLAY-001"],
  "tenant_message": "您好，已定位为电动阀执行器故障，本次将直接更换。",
  "manager_message": "复发 3 次，建议换阀。"
}
```"""


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("WAGENT_OPS_DB", str(tmp_path / "ops.db"))
    monkeypatch.setenv("WAGENT_SESSIONS_DIR", str(tmp_path / "sessions"))
    conn = connect()
    init_db(conn)
    seed(conn, local_embed)
    return ToolContext(as_of=AS_OF, conn=conn, embedder=local_embed)


def _tc(call_id: str, name: str, args: dict) -> dict:
    return {"id": call_id, "name": name,
            "arguments": json.dumps(args, ensure_ascii=False)}


def _wo_step(call_id: str = "c-wo") -> dict:
    """建单步：出 Decision 前必须实际建单（runner 的 wo-nudge 拦截，只放行一次重试）。"""
    return {"role": "assistant", "content": "建单。",
            "tool_calls": [_tc(call_id, "create_workorder",
                               {"space_id": "SP-A-25-E", "asset_id": "FCU-A25-01",
                                "raw_text": "A座25楼东侧空调又不制冷了",
                                "symptom": "no_cooling"})]}


def _blocks(e):
    return e["data"]["message"]["content"]


def _text(e):
    return "".join(b.get("text", "") for b in _blocks(e) if b.get("type") == "text")


def _reasoning(e):
    return "".join(b.get("text", "") for b in _blocks(e) if b.get("type") == "reasoning")


def _result(e):
    """tool/result 的完整结果 dict（从 ToolResultMessage 内容文本解出）。"""
    return json.loads(e["data"]["message"]["content"][0]["content"][0]["text"])


def test_full_turn_with_tools_and_decision(env):
    steps = [
        {"role": "assistant", "content": "先解析空间位置。",
         "tool_calls": [_tc("c1", "resolve_space",
                            {"text": "A座25楼东侧空调又不制冷了"})]},
        {"role": "assistant", "content": "再查设备运行参数。",
         "tool_calls": [_tc("c2", "get_assets_serving_space",
                            {"space_id": "SP-A-25-E"})]},
        _wo_step("c3"),
        {"role": "assistant", "content": DECISION_JSON},
    ]
    calls = []

    def fake(messages, tools):
        calls.append((messages, tools))
        return steps[len(calls) - 1]

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A座25楼东侧空调又不制冷了", "full")

    assert result["reason"] == "completed"
    dec = result["decision"]
    assert dec["root_cause"] == "valve_actuator_failure"
    assert dec["memory_ids_used"] == ["INS-REPLAY-001"]

    types = [e["type"] for e in log.events]
    assert "turn/start" in types and "user/message" in types
    assert types.count("assistant/message") == 4
    assert types.count("tool/call") == 3
    assert types.count("tool/result") == 3
    assert "decision" in types and types[-1] == "turn/end"

    # 消息派生：user → assistant(tool_calls) → tool → assistant → ...
    msgs = log.derive_messages()
    assert msgs[0]["role"] == "user"
    tc1 = next(b for b in msgs[1]["content"] if b.get("type") == "tool-call")
    assert tc1["name"] == "resolve_space"
    tr = msgs[2]["content"][0]
    assert tr["type"] == "tool-result" and tr["toolCallId"] == "c1"
    assert msgs[-1]["role"] == "assistant"

    # 第二次模型调用能看到工具结果（surface 投影生效）
    assert any("SP-A-25-E" in str(m.get("content")) for m in calls[1][0])
    # full 档拿到 11 个工具 schema
    assert len(calls[0][1]) == 11


def test_safety_precheck_bypasses_model(env):
    def boom(messages, tools):  # 模型被调用即失败
        raise AssertionError("安全路径不得调用模型")

    log = EventLog()
    result = run_turn(stream_of(boom), env, log, "三楼电梯困人了，快来人！", "full")
    assert result["reason"] == "safety"
    assert result["escalate"]["ticket_id"].startswith("TKT-")
    assert result["needs"] == "safety_intake" and result["location_hint"] is None
    types = [e["type"] for e in log.events]
    assert "decision" not in types  # 无 Decision，不编造


def test_safety_precheck_location_hint(env):
    """安全拦截也带 location_hint（「A栋有煤气味」→ A栋），前端安全补全卡据此预选。"""
    log = EventLog()
    result = run_turn(lambda m, t: None, env, log, "A栋有煤气味", "full")
    assert result["reason"] == "safety"
    assert result["needs"] == "safety_intake"
    assert result["location_hint"] == {"building": "A栋", "floor": None, "space_type": None, "zone": None}
    end = [e for e in log.events if e["type"] == "turn/end"][-1]
    assert end["data"]["needs"] == "safety_intake"
    assert end["data"]["location_hint"] == {"building": "A栋", "floor": None, "space_type": None, "zone": None}


def test_decision_parse_retry_once(env):
    BAD = '收尾。\n\n```json\n{"space_id": "S"}\n```'  # 有围栏但契约校验失败
    steps = [
        {"role": "assistant", "content": BAD},            # → 触发格式提醒
        _wo_step(),                                       # 先建单
        {"role": "assistant", "content": DECISION_JSON},  # 重试成功
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A1608 空调异响", "l1")
    assert result["reason"] == "completed"
    nudges = [e for e in log.events if e["type"] == "user/message"
              and e["data"].get("source", {}).get("plugin") == "format-nudge"]
    assert len(nudges) == 1
    # 被提醒的那条回复也进了事件流（trace 不留缺口）
    assert any(e["type"] == "assistant/message" and "space_id" in _text(e)
               for e in log.events)
    # 提醒消息也进了派生消息（模型第二次能看到）
    assert any("格式提醒" in str(m.get("content")) for m in log.derive_messages())


def test_parse_failed_after_retry(env):
    BAD = '```json\n{"space_id": "S"}\n```'   # 围栏存在但永远校验不过
    steps = [{"role": "assistant", "content": BAD}] * 3
    it = iter(steps)

    log = EventLog()
    result = run_turn(stream_of(lambda m, t: next(it)), env, log, "x", "off")
    assert result["reason"] == "parse_failed"


def test_awaiting_input_on_plain_reply(env):
    """无围栏纯文本 = 在对用户说话（寒暄/追问）—— 正常结局，不提醒不报警。"""
    log = EventLog()
    result = run_turn(
        stream_of(lambda m, t: {"role": "assistant", "content": "你好，请描述具体报修内容。"}),
        env, log, "hi", "full")
    assert result["reason"] == "awaiting_input"
    assert result["needs"] is None and result["reply"]
    types = [e["type"] for e in log.events]
    assert "assistant/message" in types and types[-1] == "turn/end"
    assert not [e for e in log.events
                if e["data"].get("source", {}).get("plugin") == "format-nudge"]


def test_awaiting_input_needs_location(env):
    """本轮 resolve_space 失败 + 模型追问 → needs=location（前端据此弹位置选择器）。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "顶楼空中花园"})]},
        {"role": "assistant", "content": "位置库里没有「顶楼空中花园」，请补充门牌号。"},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "顶楼空中花园漏水", "full")
    assert result["reason"] == "awaiting_input" and result["needs"] == "location"
    assert result["location_hint"] is None  # 原文无楼栋线索


def test_decision_blocked_when_space_unresolved(env):
    """定位失败却直接出 Decision → 硬停等待租户补充，不落 decision。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "顶楼空中花园"})]},
        {"role": "assistant", "content": DECISION_JSON},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "顶楼空中花园漏水", "full")
    assert result["reason"] == "awaiting_input" and result["needs"] == "location"
    assert not [e for e in log.events if e["type"] == "decision"]
    assert [e for e in log.events
            if e["data"].get("source", {}).get("plugin") == "location-nudge"]


def test_unresolved_location_blocks_workorder_and_manager_notify(env):
    """位置歧义时，模型即使违规调用，也不能建单或通知项目经理。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "B座2楼洗手间"})]},
        {"role": "assistant", "content": "先建单并通知项目经理。",
         "tool_calls": [
             _tc("c2", "create_workorder", {"raw_text": "B座2楼洗手间漏水",
                                               "symptom": "water_leak"}),
             _tc("c3", "notify", {"channel": "wecom",
                                      "recipient_role": "facility_manager",
                                      "recipient_id": "FM-001", "message": "漏水"}),
         ]},
        {"role": "assistant", "content": "请确认是B座2楼男卫生间还是女卫生间？"},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "B座2楼洗手间漏水", "full")
    assert result["reason"] == "awaiting_input" and result["needs"] == "location"
    blocked = [_result(e) for e in log.events if e["type"] == "tool/result"
               and e["data"]["meta"]["name"] in {"create_workorder", "notify"}]
    assert len(blocked) == 2
    assert all(r["error"]["code"] == "ambiguous" for r in blocked)
    assert not any(r.get("wo_id") or r.get("receipt_id") for r in blocked)


def test_empty_reply_nudged_once(env):
    """空回复（只有 reasoning 无正文）→ 提醒一次后出 Decision，正常 completed。"""
    steps = [
        {"role": "assistant", "content": ""},
        _wo_step(),
        {"role": "assistant", "content": DECISION_JSON},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A1913 灯坏了", "full")
    assert result["reason"] == "completed"
    assert [e for e in log.events
            if e["data"].get("source", {}).get("plugin") == "empty-reply-nudge"]


def test_empty_reply_twice_falls_through(env):
    """提醒只给一次：连续空回复不无限循环，第二次按 awaiting_input 收尾。"""
    def fake(messages, tools):
        return {"role": "assistant", "content": ""}

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A1913 灯坏了", "full")
    assert result["reason"] == "awaiting_input" and not result["reply"]
    assert len([e for e in log.events
                if e["data"].get("source", {}).get("plugin") == "empty-reply-nudge"]) == 1


def test_tenant_message_phone_masked(env):
    """tenant_message 里的手机号落盘前硬脱敏（模型违规回显补全号码的兜底）。"""
    dec = DECISION_JSON.replace("已定位为电动阀执行器故障，本次将直接更换。",
                                "已受理，师傅将联系您 18642089888 上门。")
    log = EventLog()
    result = run_turn(stream_of(lambda m, t: {"role": "assistant", "content": dec}),
                      env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "completed"
    tm = result["decision"]["tenant_message"]
    assert "18642089888" not in tm and "****" in tm


def test_awaiting_input_location_hint_building(env):
    """用户原话提到「B座」但定位失败 → location_hint 带出楼栋供卡片预选。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "B座电梯厅"})]},
        {"role": "assistant", "content": "请问具体在 B 座几楼哪个位置？"},
    ]

    def fake(messages, tools):
        return steps.pop(0)

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "B座电梯厅有水渍", "full")
    assert result["reason"] == "awaiting_input" and result["needs"] == "location"
    assert result["location_hint"] == {"building": "B栋", "floor": None, "space_type": "电梯厅", "zone": None}
    end = [e for e in log.events if e["type"] == "turn/end"][-1]
    assert end["data"]["location_hint"] == {"building": "B栋", "floor": None, "space_type": "电梯厅", "zone": None}


def test_awaiting_input_location_hint_floor(env):
    """原话提到「B座25楼」→ hint 同时带出楼栋和楼层，位置下拉只剩该层空间。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "B座25楼"})]},
        {"role": "assistant", "content": "请问在 25 楼哪个位置？"},
    ]

    def fake(messages, tools):
        return steps.pop(0)

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "B座25楼空调不制冷", "full")
    assert result["needs"] == "location"
    assert result["location_hint"] == {"building": "B栋", "floor": 25, "space_type": None, "zone": None}


def test_awaiting_input_location_hint_room_style(env):
    """门牌式描述「a1010洗手间」：楼栋取字母前缀、楼层取门牌前两位、类型取洗手间。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space", {"text": "a1010洗手间"})]},
        {"role": "assistant", "content": "请问是 A 栋 10 楼的男卫还是女卫？"},
    ]

    def fake(messages, tools):
        return steps.pop(0)

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "a1010洗手间有异味", "full")
    assert result["needs"] == "location"
    assert result["location_hint"] == {"building": "A栋", "floor": 10,
                                       "space_type": "卫生间", "zone": None}


def test_awaiting_input_location_hint_from_tool_arg(env):
    """模型传了 building_hint 时，即使原文无「座/栋」字样也能带出楼栋。"""
    steps = [
        {"role": "assistant", "content": "先解析位置。",
         "tool_calls": [_tc("c1", "resolve_space",
                            {"text": "电梯厅", "building_hint": "B座"})]},
        {"role": "assistant", "content": "请问在几楼？"},
    ]

    def fake(messages, tools):
        return steps.pop(0)

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "电梯厅有水渍", "full")
    assert result["location_hint"] == {"building": "B栋", "floor": None, "space_type": "电梯厅", "zone": None}


def test_llm_error_recorded(env):
    def boom(messages, tools):
        raise RuntimeError("quota exceeded")

    log = EventLog()
    result = run_turn(stream_of(boom), env, log, "空调坏了", "l1l2")
    assert result["reason"] == "llm_error"
    end = [e for e in log.events if e["type"] == "turn/end"][-1]
    assert "quota" in end["data"]["detail"]


def test_tool_error_does_not_break_loop(env):
    steps = [
        {"role": "assistant", "content": "查一个不存在的空间。",
         "tool_calls": [_tc("c1", "get_assets_serving_space",
                            {"space_id": "SP-NONE"})]},
        _wo_step("c2"),
        {"role": "assistant", "content": DECISION_JSON},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "空调坏了", "full")
    assert result["reason"] == "completed"
    tr = next(e for e in log.events if e["type"] == "tool/result")
    assert _result(tr)["error"]["code"] == "not_found"
    assert tr["data"]["meta"]["digest"]


def test_parse_decision_variants():
    assert parse_decision(None) == (None, None)
    assert parse_decision("没有围栏的纯文本") == (None, None)
    d, err = parse_decision("```json\n{\"space_id\": \"S\"}\n```")   # 缺必填字段
    assert d is None and err  # 错误描述非空（格式提醒要转告模型）
    d, err = parse_decision(DECISION_JSON)
    assert d is not None and err is None and d.is_repeat_fault is True


def test_bare_decision_after_preamble_completes(env):
    """回归：模型漏写 ```json 围栏时，裸 Decision 不得作为普通回复返给租户。"""
    bare = DECISION_JSON[DECISION_JSON.index("{"):DECISION_JSON.rindex("}") + 1]
    obj = json.loads(bare)
    obj["tenant_message"] = "您的报修已受理，环境人员将尽快上门处理。"
    content = ("好的，工单已受理。设施经理简报将同步流转：\n"
               + json.dumps(obj, ensure_ascii=False))

    parsed, err = parse_decision(content)
    assert parsed is not None and err is None

    log = EventLog()
    result = run_turn(
        stream_of(lambda messages, tools: {"role": "assistant", "content": content}),
        env, log, "A栋15楼男洗手间马桶坏了", "off",
    )
    assert result["reason"] == "completed"
    assert result["decision"]["tenant_message"] == "您的报修已受理，环境人员将尽快上门处理。"
    assert any(e["type"] == "decision" for e in log.events)
    assert [e for e in log.events if e["type"] == "turn/end"][-1]["data"]["reason"] == "completed"


def test_reasoning_recorded_display_only(env):
    """qwen3 thinking 的 reasoning 进事件流（thought 字段）供页面展示，
    但绝不回灌模型消息列表（derive_messages 只投影 content/tool_calls）。"""
    steps = [
        {"role": "assistant", "content": "先解析空间位置。",
         "reasoning": "租户提到 A座25楼东侧，先调 resolve_space 定位。",
         "tool_calls": [_tc("c1", "resolve_space",
                            {"text": "A座25楼东侧空调又不制冷了"})]},
        _wo_step("c2"),
        {"role": "assistant", "content": DECISION_JSON,
         "reasoning": "同点位 60 天三次报修，判阀执行器故障。"},
    ]
    calls = []

    def fake(messages, tools):
        calls.append((messages, tools))
        return steps[len(calls) - 1]

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "completed"

    thoughts = [_reasoning(e) for e in log.events
                if e["type"] == "assistant/message"]
    assert thoughts[0] == "租户提到 A座25楼东侧，先调 resolve_space 定位。"
    assert thoughts[-1] == "同点位 60 天三次报修，判阀执行器故障。"
    # 展示字段不进模型消息列表
    assert all("reasoning" not in m and "thought" not in m
               for m in log.derive_messages())


# ── 建单硬拦截（wo-nudge）─────────────────────────────────


def test_decision_without_workorder_nudged_once(env):
    """未实际建单就出 Decision → 建单提醒一次；再次违规放行留痕（防死循环）。"""
    def fake(messages, tools):
        return {"role": "assistant", "content": DECISION_JSON}

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "completed"
    nudges = [e for e in log.events if e["type"] == "user/message"
              and e["data"].get("source", {}).get("plugin") == "wo-nudge"]
    assert len(nudges) == 1
    # 提醒消息进派生消息列表（模型第二次调用能看到）
    assert any("建单提醒" in str(m.get("content")) for m in log.derive_messages())


def test_decision_exempt_action_without_workorder(env):
    """豁免动作（缴费恢复不派工）允许不建单直接出 Decision，不触发建单提醒。"""
    dec = DECISION_JSON.replace('"recommended_action": "replace_valve_actuator"',
                                '"recommended_action": "restore_after_payment"')
    log = EventLog()
    result = run_turn(stream_of(lambda m, t: {"role": "assistant", "content": dec}),
                      env, log, "A1106 空调开不了", "full")
    assert result["reason"] == "completed"
    assert not [e for e in log.events
                if e["data"].get("source", {}).get("plugin") == "wo-nudge"]


# ── 判责后置硬停策略（policy_escalate）────────────────────


def _judge_then_decision(judge_args: dict):
    """fake complete：第一步判责，第二步建单，第三步（若未被判责策略拦下）给 Decision。"""
    steps = [
        {"role": "assistant", "content": "先判责。",
         "tool_calls": [_tc("c1", "judge_liability", judge_args)]},
        _wo_step("c2"),
        {"role": "assistant", "content": DECISION_JSON},
    ]
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    return fake


def _escalate_call_reason(log: EventLog) -> str:
    call = next(e for e in log.events if e["type"] == "tool/call"
                and e["data"]["name"] == "escalate_to_human")
    return json.loads(call["data"]["arguments"])["reason"]


def test_policy_escalate_on_cost_threshold(env):
    """judge_liability 判 requires_human（金额 5000.01 超阈）→ 硬停升级，
    即使模型本来打算输出 escalate=false 的 Decision。"""
    log = EventLog()
    result = run_turn(stream_of(_judge_then_decision({
        "space_id": "SP-A-19-1913", "symptom": "no_cooling",
        "hypothesized_root_cause": "filter_clogged",
        "estimated_cost_cny": 5000.01,
    })), env, log, "A1913 空调不制冷", "full")
    assert result["reason"] == "policy_escalate"
    assert result["escalate"]["ticket_id"].startswith("TKT-")
    assert "decision" not in [e["type"] for e in log.events]
    assert _escalate_call_reason(log) == "cost_threshold"


@pytest.mark.parametrize("cost", [4999.99, 5000.00])
def test_policy_not_triggered_at_or_below_threshold(env, cost):
    log = EventLog()
    result = run_turn(stream_of(_judge_then_decision({
        "space_id": "SP-A-19-1913", "symptom": "no_cooling",
        "hypothesized_root_cause": "filter_clogged",
        "estimated_cost_cny": cost,
    })), env, log, "A1913 空调不制冷", "full")
    assert result["reason"] == "completed"


def test_policy_escalate_on_contract_conflict(env):
    """条款真冲突（命中多条条款、无金额）→ 强制升级，reason=contract_ambiguous。"""
    log = EventLog()
    result = run_turn(stream_of(_judge_then_decision({
        "space_id": "SP-A-25-E", "symptom": "no_cooling",
        "hypothesized_root_cause": "valve_actuator_failure",
    })), env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "policy_escalate"
    assert _escalate_call_reason(log) == "contract_ambiguous"


def test_policy_soft_on_no_basis(env):
    """无根因可判（no_basis、无命中条款、无金额）→ 不硬停，流程照常走完。
    （环境/秩序类日常事项没有判责对象，2026-08-27 全盘接受口径）"""
    log = EventLog()
    result = run_turn(stream_of(_judge_then_decision({
        "space_id": "SP-A-25-E", "symptom": "water_leak",
    })), env, log, "电梯厅地面有水渍", "full")
    assert result["reason"] == "completed"
    assert not [e for e in log.events if e["type"] == "tool/result"
                and e["data"]["meta"]["name"] == "escalate_to_human"]


# ── 复发后置硬停策略（repeat_failure_2x：同症未闭环堆单）────────


def _repeat_wo_steps(n: int, then_decision: bool = False):
    """fake complete：对 A1608 连续建 n 张异响工单（种子的历史异响单均已闭环，
    不计入未闭环口径），随后（可选）给 Decision。"""
    steps = [
        {"role": "assistant", "content": f"建单 {i}。",
         "tool_calls": [_tc(f"c-wo-{i}", "create_workorder",
                            {"space_id": "SP-A-16-1608", "asset_id": "FCU-A16-08",
                             "raw_text": "A1608空调有异响", "symptom": "abnormal_noise"})]}
        for i in range(1, n + 1)
    ]
    if then_decision:
        steps.append({"role": "assistant", "content": DECISION_JSON})
    calls = []

    def fake(messages, tools):
        out = steps[len(calls)]
        calls.append(1)
        return out

    return fake


def test_policy_escalate_on_open_repeats(env):
    """同空间同症状未闭环工单达 3 张、第 4 次报修建单落地 → 硬停升级
    （repeat_failure_2x），即使模型还想继续走流程。"""
    log = EventLog()
    result = run_turn(stream_of(_repeat_wo_steps(4, then_decision=True)),
                      env, log, "A1608 空调又有异响了", "full")
    assert result["reason"] == "policy_escalate"
    assert result["escalate"]["ticket_id"].startswith("TKT-")
    assert "decision" not in [e["type"] for e in log.events]
    assert _escalate_call_reason(log) == "repeat_failure_2x"


def test_policy_not_triggered_below_open_threshold(env):
    """未闭环 2 张（第 3 次建单）仍不触发——历史已闭环的复发链不是硬停对象。"""
    log = EventLog()
    result = run_turn(stream_of(_repeat_wo_steps(3, then_decision=True)),
                      env, log, "A1608 空调异响", "full")
    assert result["reason"] == "completed"
    assert not [e for e in log.events if e["type"] == "tool/result"
                and e["data"]["meta"]["name"] == "escalate_to_human"]


@pytest.mark.parametrize("tier,n", [("off", 6), ("l1", 7), ("l1l2", 8), ("full", 11)])
def test_runner_passes_exactly_tier_tools(env, tier, n):
    """四档同一案例：模型实际拿到的工具数严格递增（消融有效性的前提）。"""
    calls = []

    def fake(messages, tools):
        calls.append(tools)
        return {"role": "assistant", "content": DECISION_JSON}

    result = run_turn(stream_of(fake), env, EventLog(), "空调坏了", tier)
    assert result["reason"] == "completed"
    assert len(calls[0]) == n


def test_stream_events_request_header_chunks_usage(env):
    """dsh 通讯留痕：request/header 每轮一次（initial→resume）、context 只在变化时、
    逐 chunk 留痕、assistant/message.sourceEventSeqs=chunk seqs、usage 搭车。"""
    steps = [
        {"role": "assistant", "content": "先解析空间位置。",
         "reasoning": "先定位。", "usage": {"inputTokens": 120, "outputTokens": 30},
         "tool_calls": [_tc("c1", "resolve_space",
                            {"text": "A座25楼东侧空调又不制冷了"})]},
        _wo_step("c2"),
        {"role": "assistant", "content": DECISION_JSON,
         "reasoning": "定位成功，出决策。", "usage": {"inputTokens": 300, "outputTokens": 90}},
    ]
    calls = []

    def fake(messages, tools):
        calls.append(messages)
        return steps[len(calls) - 1]

    log = EventLog()
    result = run_turn(stream_of(fake), env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "completed"

    headers = [e for e in log.events if e["type"] == "request/header"]
    assert len(headers) == 1 and headers[0]["data"]["reason"] == "initial"
    h = headers[0]["data"]["header"]
    assert h["config"]["model"] and h["config"]["provider"]
    assert "工具" in h["system"] and len(h["tools"]) == 11
    # context 只发一次（内容未变）
    ctxs = [e for e in log.events if e["type"] == "request/context"]
    assert len(ctxs) == 1 and ctxs[0]["data"]["contextWindow"] > 0

    # chunk 事件在 message 之前，message 的 sourceEventSeqs 精确指向本步 chunk
    types = [e["type"] for e in log.events]
    assert types.index("request/header") < types.index("assistant/chunk")         < types.index("assistant/message")
    step1_chunks = [e for e in log.events if e["type"] == "assistant/chunk"
                    and e["data"]["step"] == 1]
    assert step1_chunks
    am1 = next(e for e in log.events if e["type"] == "assistant/message"
               and e["data"]["step"] == 1)
    assert am1["sourceEventSeqs"] == [c["seq"] for c in step1_chunks]
    assert am1["data"]["usage"] == {"inputTokens": 120, "outputTokens": 30}
    # 块序：reasoning 在 text 之前
    kinds = [b["type"] for b in am1["data"]["message"]["content"]]
    assert kinds.index("reasoning") < kinds.index("text")

    # 第二轮（同会话同档位）：header reason=resume，context 不再发
    run_turn(stream_of(lambda m, t: {"role": "assistant", "content": "已收到，尽快。"}),
             env, log, "麻烦尽快", "full")
    headers = [e for e in log.events if e["type"] == "request/header"]
    assert [d["data"]["reason"] for d in headers] == ["initial", "resume"]
    assert len([e for e in log.events if e["type"] == "request/context"]) == 1

# ── 判责一致性 + 租户消息兜底 ─────────────────────────────


def test_decision_liability_reconciled_with_judge(env):
    """判责一致性：Decision.liability/liability_basis 以 judge_liability 工具结果为准
    （模型自行填的 unclear 被改写），且判定补写 liability_judged 事件进工单流水，
    保证经理视角的决策卡、工具结果、工单溯源弹窗三处一致。"""
    log = EventLog()
    result = run_turn(stream_of(_judge_then_decision({
        "space_id": "SP-A-19-1913", "symptom": "no_cooling",
        "hypothesized_root_cause": "filter_clogged",
    })), env, log, "A1913 空调不制冷", "full")
    assert result["reason"] == "completed"

    judge_res = next(
        json.loads(e["data"]["message"]["content"][0]["content"][0]["text"])
        for e in log.events
        if e["type"] == "tool/result" and e["data"]["meta"]["name"] == "judge_liability"
    )
    dec = result["decision"]
    assert dec["liability"] == judge_res["liability"]
    assert dec["liability_basis"] == judge_res["basis"]

    wo_id = next(
        json.loads(e["data"]["message"]["content"][0]["content"][0]["text"])["wo_id"]
        for e in log.events
        if e["type"] == "tool/result" and e["data"]["meta"]["name"] == "create_workorder"
    )
    from wagent_backend.ops.data import repo
    liab_events = [e for e in repo.wo_events(env.conn, wo_id)
                   if e["event_type"] == "liability_judged"]
    assert len(liab_events) == 1
    assert liab_events[0]["liability"] == judge_res["liability"]


def test_tenant_message_history_reference_replaced(env):
    """租户消息兜底：tenant_message 引用历史工单/复发信息 → 整句替换为「已受理」模板。"""
    dec = DECISION_JSON.replace(
        "您好，已定位为电动阀执行器故障，本次将直接更换。",
        "已受理。该位置近 90 天曾多次报修（WO-B25-0810），本次将重点排查复发原因。")
    log = EventLog()
    result = run_turn(stream_of(lambda m, t: {"role": "assistant", "content": dec}),
                      env, log, "A座25楼东侧空调又不制冷了", "full")
    assert result["reason"] == "completed"
    tm = result["decision"]["tenant_message"]
    assert "WO-" not in tm and "多次" not in tm and "复发" not in tm
    assert "已受理" in tm


def test_tenant_message_clean_text_untouched(env):
    """未引用历史的 tenant_message 原样保留（兜底不误伤正常文案）。"""
    dec = DECISION_JSON.replace(
        "您好，已定位为电动阀执行器故障，本次将直接更换。",
        "您的报修已受理，工程人员将尽快上门处理，请保持电话畅通。")
    log = EventLog()
    result = run_turn(stream_of(lambda m, t: {"role": "assistant", "content": dec}),
                      env, log, "A座25楼东侧空调不制冷", "full")
    assert result["decision"]["tenant_message"] == \
        "您的报修已受理，工程人员将尽快上门处理，请保持电话畅通。"
