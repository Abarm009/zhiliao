"""agent loop —— function-calling 循环（web 聊天与 CLI demo 共用）。

依赖注入：complete(messages, tools) -> dict 由调用方提供
（生产=llm.client.complete_msg，测试=假函数），本模块不碰具体 SDK。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from wagent_backend.tools.kg_tools import as_openai_tools, run_tool

CompleteMsg = Callable[[list[dict], list[dict] | None], dict]

SYSTEM_PROMPT = (
    "你是楼宇设备台账问答助手，基于知识图谱工具回答。"
    "先调 kg_get_schema 了解本体；不确定实体 ID 时先 kg_search_entities；"
    "数量/统计类问题（如「A栋男洗手间有多少个马桶」）直接用 kg_count_entities "
    "一次拿总数，不要逐楼层/逐房间翻关系；"
    "用已知事实回答，图谱里查不到就直说查不到，不要编造。"
    "回答末尾用一行「依据：…」列出你用到的实体 ID。"
)

MAX_ROUNDS = 8


class ToolCallTrace(BaseModel):
    name: str
    arguments: str
    result_brief: str = Field(description="工具返回的前 200 字，前端展示用")


class ChatResult(BaseModel):
    reply: str
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    rounds: int = 0


def run(
    complete: CompleteMsg,
    message: str,
    history: list[dict[str, str]] | None = None,
    max_rounds: int = MAX_ROUNDS,
) -> ChatResult:
    """跑一轮完整对话：LLM ↔ kg_* 工具，直到给出最终回复。

    history 只传 user/assistant 的 {role, content}（前端聊天记录），
    工具消息不跨轮保留，避免破坏 OpenAI 协议的 tool_call 配对。
    """
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in (history or [])[-6:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": message})

    tools = as_openai_tools()
    traces: list[ToolCallTrace] = []
    result = ChatResult(reply="（模型没有返回内容）")
    for round_no in range(1, max_rounds + 1):
        result.rounds = round_no
        msg = complete(messages, tools)
        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            result.reply = (msg.get("content") or "").strip() or result.reply
            result.tool_calls = traces
            return result
        messages.append(
            {
                "role": "assistant",
                "content": msg.get("content"),
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    }
                    for tc in tool_calls
                ],
            }
        )
        for tc in tool_calls:
            try:
                args = json.loads(tc["arguments"] or "{}")
            except json.JSONDecodeError:
                args = {}
            tool_result = run_tool(tc["name"], **args)
            brief = json.dumps(tool_result, ensure_ascii=False)
            traces.append(
                ToolCallTrace(name=tc["name"], arguments=tc["arguments"], result_brief=brief[:200])
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": brief,
                }
            )
    result.reply = "（工具调用轮次用尽，请换个问法或缩小问题范围）"
    result.tool_calls = traces
    return result
