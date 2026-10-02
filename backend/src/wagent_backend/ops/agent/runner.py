"""runner —— Agent 主循环（参考 deepseek-harness 的 turn/step 结构，只留核心）。

    run_turn(stream, ctx, log, text, tier) -> dict

铁律：
  * 一切皆事件 —— 循环里的每一步都写进 EventLog，消息列表是派生物；
    surface 事件（user/message | assistant/message | tool/result）必须带 surfaceOp；
  * 工具错误不炸循环 —— run_tool 返回 error 信封，模型自己换路；
  * 安全关键词在模型之外拦截（policy.safety_hit）；
  * judge_liability 判"必须人工"也在模型之外硬停（policy.judge_liability_escalation）；
  * 结束的正路有三种：模型输出 Decision JSON（completed）、
    模型判定信息不足向租户追问（awaiting_input，无围栏纯文本 = 在对用户说话）、
    或被策略强制升级（safety / policy_escalate / step_limit / max_rounds）。
    格式提醒只在模型「试图给 Decision 但契约校验失败」
    （有围栏，或带 Decision 特征字段的裸 JSON）时给一次。

事件形状对齐 dsh：assistant/message.content 是块数组（reasoning/text/tool-call 按流序）；
tool/result 是 ToolResultMessage（单 tool-result 块，错误信封在内容文本内部）；
user/message 的 data 即完整消息。reasoning 块仅展示，_wire 不回灌模型——有守卫测试。

通讯方式对齐 dsh：模型走**流式**。每个 chunk 先落 assistant/chunk（token 级回放保真），
BlockAssembler 边收边组，流尾发 assistant/message（sourceEventSeqs=chunk seqs，usage 搭车）。
每轮首步发 request/header（initial/resume/change，含 system 全文+tools）与
request/context（首次与变化时）。_force_escalate 是模型外硬路径：直接产块化消息，无 chunk。

stream 注入：生产传 llm.client.stream，测试传 conftest.stream_of(fake) —— runner 不 import openai。
"""

from __future__ import annotations

import json
import re
import time
import uuid
from datetime import timedelta
from typing import Any, Callable, Iterator

from pydantic import ValidationError

from wagent_backend.llm import client
from wagent_backend.llm.assembler import (BlockAssembler, reasoning_of, text_of,
                                          tool_calls_of)
from wagent_backend.ops.agent import compaction
from wagent_backend.ops.agent.compaction import context_window
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.policy import (judge_liability_escalation,
                                             repeat_escalation, safety_hit)
from wagent_backend.ops.agent.prompts import build_system_prompt, tier_tools
from wagent_backend.ops.contracts import Decision, LiabilityEnum
from wagent_backend.ops.data import repo
from wagent_backend.ops.tools.context import ToolContext
from wagent_backend.ops.tools.digest import digest
from wagent_backend.ops.tools.registry import as_openai_tools, run_tool

Stream = Callable[..., Any]   # (messages, tools) -> Iterator[StreamChunk dict]

MAX_TOOL_CALLS = 40   # 单轮工具调用总数上限
MAX_ROUNDS = 30       # 单轮模型往返轮数上限

# 出 Decision 前允许不建单的处置动作（故事 B：欠费锁机缴费恢复不派工）；
# 其余报修必须先实际调用 create_workorder，否则拦截重试一次（wo-nudge）
_WO_EXEMPT_ACTIONS = {"restore_after_payment"}

_JSON_FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
_PHONE_RE = re.compile(r"1\d{10}")


def _mask_phone(text: str | None) -> str | None:
    """租户可见文本的手机号硬脱敏（提示词约束的兜底，防模型把补全的号码回显给租户）。"""
    return _PHONE_RE.sub("****", text) if text else text


# tenant_message 引用历史工单/复发的特征（提示词禁令的兜底）：
# 命中即整句替换为「已受理」模板——租户只需要受理结果，复发证据走 manager_message
_TENANT_HISTORY_RE = re.compile(
    r"WO-\d|复发|历史工单|曾多次|多次报修|往期|此前|上次|近\s*90\s*天|"
    r"近期.{0,8}(多次|反复|频发)|反复出现|第\s*[一二三四五六七八九十\d]+\s*次"
)


def _sanitize_tenant_message(text: str, decision: Decision, wo_id: str | None) -> str:
    """租户消息兜底：引用历史工单/复发信息 → 替换为「已受理」模板（提示词约束的硬兜底）。"""
    if not _TENANT_HISTORY_RE.search(text):
        return text
    if decision.escalate:
        return "您的报修已受理，我们已安排专员跟进，将尽快与您联系。"
    accepted = f"您的报修已受理（工单号 {wo_id}）" if wo_id else "您的报修已受理"
    return accepted + "，服务人员将尽快上门处理，请保持电话畅通。"
_BLD_RE = re.compile(r"[A-Za-z0-9]+\s*[座栋楼]")
_ROOM_RE = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]?)\s?-?(\d{3,4})(?!\d)")  # a1010 / B-1913 / 1106
# 位置类型关键词 → space_type；男/女卫再细到 zone
_SPACE_TYPE_KWS = (
    ("电梯厅", ("电梯厅",)),
    ("卫生间", ("洗手间", "卫生间", "厕所", "男卫", "女卫", "男厕", "女厕")),
    ("停车场", ("停车场", "车库", "车位")),
    ("设备房", ("设备房", "机房", "空调机房")),
    ("设备间", ("设备间",)),
)
_ZONE_KWS = (
    ("东侧", ("东侧",)), ("西侧", ("西侧",)), ("南侧", ("南侧",)), ("北侧", ("北侧",)),
    ("核心筒", ("核心筒",)),
    ("男", ("男卫", "男厕", "男洗手间")), ("女", ("女卫", "女厕", "女洗手间")),
)


# ── 消息构造（dsh 块词表）────────────────────────────────

def _user_message(text: str, source: dict | None = None) -> dict[str, Any]:
    return {"id": uuid.uuid4().hex, "role": "user",
            "content": [{"type": "text", "text": text}],
            "source": source or {"kind": "user"}}


def _assistant_message(content: str | None, reasoning: str | None,
                       tool_calls: list[dict] | None) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    if reasoning:  # 思考先于正文（dsh：thinking 模式下 reasoning 交错在前）
        blocks.append({"type": "reasoning", "text": reasoning})
    if content:
        blocks.append({"type": "text", "text": content})
    for tc in tool_calls or []:
        blocks.append({"type": "tool-call", "id": tc["id"],
                       "name": tc["name"], "arguments": tc["arguments"]})
    return {"id": uuid.uuid4().hex, "role": "assistant", "content": blocks,
            "source": {"kind": "model", "provider": client.provider_name(),
                       "model": client.model_name()}}


def _tool_result_message(call_id: str, result: dict) -> dict[str, Any]:
    """dsh ToolResultMessage：user 角色，content 恰一个 tool-result 块。
    错误信封 {"error":{code,message,hint}} 保留在内容文本内部（契约不变）。"""
    return {"id": uuid.uuid4().hex, "role": "user",
            "content": [{"type": "tool-result", "toolCallId": call_id,
                         "content": [{"type": "text",
                                      "text": json.dumps(result, ensure_ascii=False,
                                                         default=str)}],
                         "isError": bool(isinstance(result, dict) and result.get("error"))}],
            "source": {"kind": "tool", "callId": call_id}}


def _log_assistant(log: EventLog, turn: int, step: int,
                   content: str | None, reasoning: str | None,
                   tool_calls: list[dict] | None) -> None:
    log.append("assistant/message", {
        "turn": turn, "step": step,
        "message": _assistant_message(content, reasoning, tool_calls),
    }, surface_op="append")


# ── 流式步：chunk 留痕 + 组装 → assistant/message（dsh 通讯方式）──

def _log_request(log: EventLog, system: dict, tools: list[dict], *,
                 first_step: bool) -> None:
    """每轮（loop 实例）首步发 request/header；内容变了发 change，否则 resume。
    request/context 只在首次或变化时发。dsh：请求头留痕让回放能还原「模型当时看到什么」。"""
    header = {"config": {"model": client.model_name(), "provider": client.provider_name()},
              "system": system["content"], "tools": tools}
    prev = next((e for e in reversed(log.events) if e["type"] == "request/header"), None)
    if prev is None:
        log.append("request/header", {"header": header, "reason": "initial"})
    elif first_step:
        reason = "change" if prev["data"]["header"] != header else "resume"
        log.append("request/header", {"header": header, "reason": reason})
    context = {"provider": client.provider_name(), "model": client.model_name(),
               "contextWindow": context_window()}
    prev_ctx = next((e for e in reversed(log.events) if e["type"] == "request/context"), None)
    if prev_ctx is None or prev_ctx["data"] != context:
        log.append("request/context", context)


def _stream_step(stream: Stream, log: EventLog, turn: int, step: int,
                 system: dict, tools: list[dict]) -> list[dict]:
    """跑一次流式模型调用：逐 chunk 留痕+组装，流尾发 assistant/message。

    返回组装好的 content 块（按流序）。finish.error → raise LLMError
    （调用方的 except 承接为 llm_error，已收的 chunk 仍留在日志里）。
    """
    asm = BlockAssembler()
    chunk_seqs: list[int] = []
    for chunk in stream([system, *log.derive_messages()], tools):
        ev = log.append("assistant/chunk", {"turn": turn, "step": step, "chunk": chunk})
        chunk_seqs.append(ev["seq"])
        asm.push(chunk)
    if asm.finish.get("kind") == "error":
        failure = asm.finish.get("failure") or {}
        raise client.LLMError(failure.get("message") or "model error",
                              failure.get("code") or "LLM_ERROR")
    data: dict[str, Any] = {
        "turn": turn, "step": step,
        "message": {"id": uuid.uuid4().hex, "role": "assistant",
                    "content": asm.blocks(),
                    "source": {"kind": "model", "provider": client.provider_name(),
                               "model": client.model_name()}}}
    if asm.usage is not None:
        data["usage"] = asm.usage
    log.append("assistant/message", data, surface_op="append",
               source_event_seqs=chunk_seqs or None)
    return data["message"]["content"]


# ── Decision 解析 ───────────────────────────────────────

def parse_decision(content: str | None) -> tuple[Decision | None, str | None]:
    """从最后一条 assistant 消息里提取并校验 Decision。

    正常路径读取 ```json 围栏；同时容忍模型在一句收尾说明后输出裸 JSON。
    裸 JSON 只有同时出现 tenant_message / manager_message 等 Decision 特征字段时
    才会尝试解析，避免把普通回复里的任意 JSON 示例误判成最终决策。

    返回 (决策, 错误描述)：未发现 Decision 候选时皆为 None；发现候选但不合法时
    决策为 None、错误描述为校验失败原因（供格式提醒原样转告模型，便于自纠）。
    """
    if not content:
        return None, None
    m = _JSON_FENCE.search(content)
    if m:
        try:
            obj = json.loads(m.group(1))
            return Decision.model_validate(obj), None
        except (json.JSONDecodeError, ValidationError) as e:
            return None, str(e)

    decoder = json.JSONDecoder()
    required_hints = {"space_id", "symptom", "tenant_message", "manager_message"}
    for start in (m.start() for m in re.finditer(r"\{", content)):
        try:
            obj, _ = decoder.raw_decode(content, start)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict) or not required_hints.issubset(obj):
            continue
        try:
            return Decision.model_validate(obj), None
        except ValidationError as e:
            return None, str(e)
    return None, None


# ── 工具执行（tool/call + tool/result 事件对）────────────

def _location_hint(ctx: ToolContext, log: EventLog,
                   failed_calls: list[tuple[dict, dict]]) -> dict[str, Any] | None:
    """定位失败时尽量带出已知位置信息，供前端位置卡片逐级预选（用户仍可手动调整）。

    楼栋：优先取 resolve_space 入参的 building_hint（模型已抽取），其次用户原文
    「B座/B栋/3号楼」，再兜底门牌字母前缀（a1010 → A栋）。
    楼层：「25楼」字样，或门牌号前两位（a1010 → 10 楼，B1913 → 19 楼）。
    位置类型/区域：「洗手间/电梯厅/停车场…」→ space_type，「东侧/男卫…」→ zone；
    前端在空间库过滤后唯一命中时才预选具体位置，宁缺毋滥。
    """
    raws: list[str] = []
    for tc, _ in failed_calls:
        try:
            args = json.loads(tc.get("arguments") or "{}")
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(args, dict) and args.get("building_hint"):
            raws.append(str(args["building_hint"]))
    user_texts = [t for e in log.events if e["type"] == "user/message"
                  for t in [EventLog._user_text(e)] if t]
    if not raws:
        for t in user_texts:
            raws.extend(m.group(0) for m in _BLD_RE.finditer(t))
        for t in reversed(user_texts):   # 门牌字母前缀兜底（a1010 → a → A栋）
            m = _ROOM_RE.search(t)
            if m and m.group(1):
                raws.append(m.group(1))
                break
    building = None
    for raw in reversed(raws):  # 后提到的优先
        bld_id = repo.resolve_building_hint(ctx.conn, raw)
        if bld_id:
            building = repo.building_name(ctx.conn, bld_id)
            break
    floor = None
    for t in reversed(user_texts):
        m = re.search(r"(\d+)\s*楼", t)
        if m:
            floor = int(m.group(1))
            break
    if floor is None:
        for t in reversed(user_texts):   # 门牌前两位 = 楼层（1010 → 10，405 → 4）
            m = _ROOM_RE.search(t)
            if m:
                floor = int(m.group(2)[:-2])
                break
    joined = " ".join(user_texts)
    space_type = next((tp for tp, kws in _SPACE_TYPE_KWS if any(k in joined for k in kws)),
                      None)
    zone = next((z for z, kws in _ZONE_KWS if any(k in joined for k in kws)), None)
    if building is None and floor is None and space_type is None and zone is None:
        return None
    return {"building": building, "floor": floor,
            "space_type": space_type, "zone": zone}


def _exec_tool_calls(ctx: ToolContext, log: EventLog, turn: int, step: int,
                     tool_calls: list[dict], *,
                     guard: Callable[[str, dict], dict | None] | None = None,
                     ) -> list[tuple[str, dict]]:
    """执行一批工具调用并留痕；返回 (工具名, 结果) 列表供后置策略检查。"""
    results: list[tuple[str, dict]] = []
    for tc in tool_calls:
        call_ev = log.append("tool/call", {
            "turn": turn, "step": step, "callId": tc["id"],
            "name": tc["name"], "arguments": tc["arguments"],
        })
        duration_ms = 0
        try:
            kwargs = json.loads(tc["arguments"] or "{}")
            if not isinstance(kwargs, dict):
                raise ValueError("arguments 必须是 JSON 对象")
        except (json.JSONDecodeError, ValueError) as e:
            result = {"error": {"code": "invalid_input",
                                "message": f"工具参数不是合法 JSON：{e}", "hint": None}}
        else:
            result = guard(tc["name"], kwargs) if guard else None
            if result is None:
                t0 = time.perf_counter()
                result = run_tool(tc["name"], ctx, **kwargs)
                duration_ms = int((time.perf_counter() - t0) * 1000)
        log.append("tool/result", {
            "turn": turn, "step": step,
            "message": _tool_result_message(tc["id"], result),
            "meta": {"name": tc["name"], "digest": digest(tc["name"], result),
                     "duration_ms": duration_ms},
        }, surface_op="append", source_event_seqs=[call_ev["seq"]])
        results.append((tc["name"], result))
    return results


def _unresolved_location_guard(name: str, args: dict) -> dict | None:
    """位置未确认时，禁止产生面向项目经理的业务副作用。"""
    blocked = name == "create_workorder" or (
        name == "notify" and args.get("recipient_role") == "facility_manager"
    )
    if not blocked:
        return None
    return {"error": {
        "code": "ambiguous",
        "message": "具体报修空间尚未确认，当前不得建单或通知设施经理",
        "hint": "先直接向租户确认具体位置；收到补充并成功解析空间后再继续",
    }}


def _repeat_escalation(ctx: ToolContext, tc: dict, result: dict) -> tuple[str, str] | None:
    """create_workorder 后置：同空间同症状未闭环工单堆到阈值 → 强制转人工。"""
    try:
        args = json.loads(tc["arguments"] or "{}")
    except json.JSONDecodeError:
        return None
    space_id, symptom = args.get("space_id"), args.get("symptom")
    if not space_id or not symptom:
        return None
    open_ids = repo.wo_open_same_symptom(
        ctx.conn, space_id, symptom,
        ctx.as_of - timedelta(days=90), ctx.as_of,
        exclude_wo_id=result.get("wo_id"))
    return repeat_escalation(open_ids)


def _force_escalate(ctx: ToolContext, log: EventLog, turn: int, step: int,
                    reason: str, detail: str) -> dict:
    """策略强制升级（安全/步数上限）—— 不经模型，直接调工具并留痕。"""
    tc = {"id": f"call-esc-{turn}-{step}", "name": "escalate_to_human",
          "arguments": json.dumps({"reason": reason, "detail": detail},
                                  ensure_ascii=False)}
    _log_assistant(log, turn, step, detail, "策略拦截", [tc])
    _exec_tool_calls(ctx, log, turn, step, [tc])
    text = next(e["data"]["message"]["content"][0]["content"][0]["text"]
                for e in reversed(log.events) if e["type"] == "tool/result")
    return json.loads(text)


# ── 主入口 ──────────────────────────────────────────────

def run_turn(stream: Stream, ctx: ToolContext, log: EventLog,
             text: str, tier: str) -> dict[str, Any]:
    """一轮报修的主循环；轮末 flush 是显式持久化屏障（写-behind 落盘）。"""
    try:
        return _run_turn(stream, ctx, log, text, tier)
    finally:
        log.flush()


def _run_turn(stream: Stream, ctx: ToolContext, log: EventLog,
              text: str, tier: str) -> dict[str, Any]:
    turn = 1 + len([e for e in log.events if e["type"] == "turn/start"])
    log.append("turn/start", {"turn": turn})
    log.append("user/message", _user_message(text), surface_op="append")

    # 1) 安全前置拦截 —— 模型不参与（基线 §10）
    kw = safety_hit(text)
    if kw:
        result = _force_escalate(
            ctx, log, turn, 0, "safety_precheck",
            f"报修文本命中安全关键词「{kw}」，已跳过模型推理直接升级人工处理。原文：{text}",
        )
        # 带上已知楼栋（如「A栋有煤气味」），前端安全补全卡据此预选
        hint = _location_hint(ctx, log, [])
        log.append("turn/end", {"turn": turn, "reason": "safety",
                                "needs": "safety_intake", "location_hint": hint})
        return {"turn": turn, "reason": "safety", "escalate": result,
                "needs": "safety_intake", "location_hint": hint}

    tools = as_openai_tools(tier_tools(tier))
    system = {"role": "system", "content": build_system_prompt(tier)}
    calls_used = 0
    nudged = False  # Decision 格式重试只给一次
    empty_nudged = False  # 空回复（只有思考没有正文）的提醒也只给一次
    wo_created = False   # 本轮是否已成功调用 create_workorder
    wo_id_created: str | None = None  # 本轮建单成功的工单号（判责落流水/租户消息模板用）
    last_judge: dict | None = None   # 本轮最近一次成功的 judge_liability 结果（判责唯一事实源）
    wo_nudged = False    # 未建单就出 Decision 的提醒只给一次
    space_unresolved = False  # 本轮最后一次 resolve_space 是否失败/歧义
    space_failed: list[tuple[dict, dict]] = []  # 最近一批失败的 resolve_space (call, result)

    for step in range(1, MAX_ROUNDS + 1):
        # 2) 步前压力检查（dsh between-step pressure）→ 请求头留痕 → 流式模型调用
        try:
            compaction.compact_if_needed(stream, log, system["content"], tools, turn=turn)
        except Exception:
            pass  # fail-closed：失败已在 compaction/end.error 留痕，本轮照常继续
        _log_request(log, system, tools, first_step=(step == 1))
        retried_overflow = False
        while True:
            try:
                blocks = _stream_step(stream, log, turn, step, system, tools)
                break
            except Exception as e:  # 网络/配额/finish.error 等上游故障
                if compaction.is_context_overflow(e) and not retried_overflow:
                    # 上下文溢出：强制压缩一次后原步重试（dsh overflow 恢复）
                    retried_overflow = True
                    try:
                        compaction.compact_if_needed(stream, log, system["content"],
                                                     tools, turn=turn,
                                                     trigger="context-overflow")
                    except Exception:
                        pass
                    continue
                log.append("turn/end", {"turn": turn, "reason": "llm_error",
                                        "detail": f"{type(e).__name__}: {e}"})
                return {"turn": turn, "reason": "llm_error", "error": str(e)}

        content = text_of(blocks) or None
        reasoning = reasoning_of(blocks)   # qwen3 thinking 的思考过程（仅展示）
        tool_calls = tool_calls_of(blocks)

        # 3) 终局：无工具调用 → 三分支（assistant/message 已在 _stream_step 落日志）
        if not tool_calls:
            decision, dec_err = parse_decision(content)
            if decision is not None:
                if space_unresolved:
                    # 位置未确认时硬停在租户补充阶段。不能依赖模型重试是否守规，
                    # 更不能在第二次违规输出时放行 Decision / 项目经理流转。
                    log.append("user/message", _user_message(
                        "（位置确认）空间定位尚未成功（resolve_space 未命中或歧义），"
                        "请不要直接给出 ```json 决策块；先用一两句话向租户复述问题，"
                        "并请其补充具体位置（楼栋/楼层/门牌号或区域），等待租户回复。",
                        {"kind": "plugin", "plugin": "location-nudge"}),
                        surface_op="append")
                    reply = ("已收到您的报修，但目前存在多个位置候选。请在下方补充具体位置，"
                             "确认后我们再继续诊断和建单。")
                    _log_assistant(log, turn, step, reply, None, None)
                    loc_hint = _location_hint(ctx, log, space_failed)
                    log.append("turn/end", {"turn": turn, "reason": "awaiting_input",
                                            "needs": "location", "location_hint": loc_hint})
                    return {"turn": turn, "reason": "awaiting_input",
                            "needs": "location", "location_hint": loc_hint, "reply": reply}
                if (not wo_created and not wo_nudged and not decision.escalate
                        and decision.recommended_action not in _WO_EXEMPT_ACTIONS):
                    # 未实际建单就出 Decision（tenant_message 却声称已受理/上门），
                    # 与位置/格式提醒同款：退回重试一次，第二次放行留痕
                    wo_nudged = True
                    log.append("user/message", _user_message(
                        "（建单提醒）本轮报修尚未实际调用 create_workorder 建单，"
                        "不得直接输出 ```json 决策块。请先完成建单（需要技工候选时先 "
                        "find_technician），再只输出决策块；确属无需建单的场景"
                        "（如缴费恢复）请在 recommended_action 中如实体现。",
                        {"kind": "plugin", "plugin": "wo-nudge"}),
                        surface_op="append")
                    continue
                # 判责一致性：Decision 的 liability/liability_basis 必须等于
                # judge_liability 的确定性返回（经理视角与工具结果同一事实源），
                # 模型自行发挥的值一律以工具为准改写；
                # 同时把判责补写进工单流水（append-only），工单溯源弹窗才能取到同一判定。
                if last_judge is not None:
                    j_liab = LiabilityEnum(last_judge["liability"])
                    j_basis = last_judge["basis"]
                    if (decision.liability != j_liab
                            or decision.liability_basis != j_basis):
                        decision.liability = j_liab
                        decision.liability_basis = j_basis
                    if wo_id_created:
                        repo.insert_wo_event(
                            ctx.conn, wo_id_created, ctx.as_of, "liability_judged",
                            liability=decision.liability.value,
                            note=f"Agent 判责：{decision.liability.value}"
                                 f"（{decision.liability_basis}）",
                        )
                        ctx.conn.commit()
                decision.tenant_message = _mask_phone(
                    _sanitize_tenant_message(
                        decision.tenant_message, decision, wo_id_created))
                log.append("decision", {"turn": turn, "decision": decision.model_dump(mode="json")})
                log.append("turn/end", {"turn": turn, "reason": "completed"})
                return {"turn": turn, "reason": "completed",
                        "decision": decision.model_dump(mode="json")}
            attempted = dec_err is not None
            if attempted and not nudged:
                # 试图给 Decision 但契约校验失败 → 把失败原因转告模型，提醒重试一次
                nudged = True
                short = re.sub(r"\s+", " ", dec_err or "")[:300]
                log.append("user/message", _user_message(
                    "（格式提醒）上一条回复的 ```json 决策块未通过契约校验"
                    + (f"（{short}）" if short else "")
                    + "，请按系统提示词的字段要求修正后重新只输出该 JSON 代码块。",
                    {"kind": "plugin", "plugin": "format-nudge"}),
                    surface_op="append")
                continue
            if attempted:
                log.append("turn/end", {"turn": turn, "reason": "parse_failed"})
                return {"turn": turn, "reason": "parse_failed"}
            if not (content or "").strip() and not empty_nudged:
                # 空回复（只有 reasoning、无正文）：租户视角什么都不会显示，
                # 等同死路——提醒一次，要求对租户说话或出 Decision（实测 qwen3.7-flash
                # 会把提示词新规复述进思考后空正文收尾）
                empty_nudged = True
                log.append("user/message", _user_message(
                    "（输出提醒）上一条回复没有正文。请直接向租户说明处理进展"
                    "（例如已建单受理、下一步安排），或按格式只输出 ```json 决策块结束本轮。",
                    {"kind": "plugin", "plugin": "empty-reply-nudge"}),
                    surface_op="append")
                continue
            # 无围栏 = 在对用户说话（追问/寒暄/说明）——正常结局，等用户补充后继续
            needs = "location" if space_unresolved else None
            loc_hint = _location_hint(ctx, log, space_failed) if needs else None
            log.append("turn/end", {"turn": turn, "reason": "awaiting_input",
                                    "needs": needs, "location_hint": loc_hint})
            return {"turn": turn, "reason": "awaiting_input",
                    "needs": needs, "location_hint": loc_hint, "reply": content}

        # 4) 中间步：执行工具（assistant/message 已在 _stream_step 落日志）
        results = _exec_tool_calls(
            ctx, log, turn, step, tool_calls,
            guard=_unresolved_location_guard if space_unresolved else None,
        )
        calls_used += len(tool_calls)
        # 记录本轮最后一次 resolve_space 是否失败/歧义（awaiting_input 的 needs 判定用）
        for tc, (name, result) in zip(tool_calls, results):
            if name == "resolve_space":
                space_unresolved = bool(result.get("error"))
                space_failed = [(tc, result)] if space_unresolved else []
            if name == "create_workorder" and not result.get("error"):
                wo_created = True
                wo_id_created = result.get("wo_id") or wo_id_created
            if name == "judge_liability" and not result.get("error"):
                last_judge = result

        # 5) 后置策略硬停：判责 requires_human / 同症未闭环堆单复发 → 强制升级，
        #    不再产 Decision（同批次其他工具已执行完毕，既成事实，升级事件照样留痕）
        esc = None
        for tc, (name, result) in zip(tool_calls, results):
            if name == "judge_liability":
                esc = judge_liability_escalation(result)
            elif name == "create_workorder" and not result.get("error"):
                esc = _repeat_escalation(ctx, tc, result)
            if esc:
                break
        if esc:
            reason, detail = esc
            prefix = ("复发后置策略强制升级（同症未闭环工单堆单）"
                      if reason == "repeat_failure_2x" else
                      "判责后置策略强制升级（judge_liability 返回 requires_human）")
            result = _force_escalate(ctx, log, turn, step + 1, reason,
                                     f"{prefix}：{detail}")
            log.append("turn/end", {"turn": turn, "reason": "policy_escalate"})
            return {"turn": turn, "reason": "policy_escalate", "escalate": result}

        if calls_used >= MAX_TOOL_CALLS:
            result = _force_escalate(
                ctx, log, turn, step + 1, "step_limit",
                f"单轮工具调用达上限（{MAX_TOOL_CALLS} 次），停止推理转人工复核。",
            )
            log.append("turn/end", {"turn": turn, "reason": "step_limit"})
            return {"turn": turn, "reason": "step_limit", "escalate": result}

    # 6) 轮数上限
    result = _force_escalate(
        ctx, log, turn, MAX_ROUNDS, "step_limit",
        f"模型往返轮数达上限（{MAX_ROUNDS} 轮）仍未给出 Decision，转人工复核。",
    )
    log.append("turn/end", {"turn": turn, "reason": "max_rounds"})
    return {"turn": turn, "reason": "max_rounds", "escalate": result}
