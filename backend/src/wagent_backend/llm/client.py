"""LLM 客户端 —— OpenAI 兼容接口封装（默认 qwen3.7-flash）。

配置来源（优先级从高到低）：
    1. 环境变量 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
    2. agent/.env 配置文件（KEY=VALUE，本模块启动时自动加载；
       文件里的空值和 # 注释行会被忽略）
    3. 内置默认：qwen3.7-flash @ DashScope compatible-mode

对外暴露四个函数，其余层不直接碰 openai：
    complete_text(messages, tools=None) -> str        抽取器用（纯文本回复）
    complete_msg(messages, tools=None) -> dict        graph chat 用（含 tool_calls，非流式）
    stream(messages, tools=None, ...) -> Iterator     ops agent 用（流式，dsh StreamChunk 词汇）
    _wire(messages) -> list[dict]                     块字典消息 → OpenAI 线上格式
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.7-flash"

_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def _load_env_file() -> None:
    """加载 agent/.env —— 只填环境变量里还没有的坑（环境变量优先）。"""
    if not _ENV_FILE.exists():
        return
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


_load_env_file()


class LLMConfigError(RuntimeError):
    """LLM 未配置（缺 API key 等），上层转成对用户的友好提示。"""


def model_name() -> str:
    return os.environ.get("LLM_MODEL") or DEFAULT_MODEL


def is_configured() -> bool:
    """LLM 是否已配置（kg-web 启动时打印提示用）。"""
    _load_env_file()
    return bool(os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY"))


def _base_url() -> str:
    return (
        os.environ.get("LLM_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_BASE_URL
    )


def _api_key() -> str:
    key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise LLMConfigError(
            "未配置 LLM_API_KEY（或 OPENAI_API_KEY）。"
            "阿里云 DashScope 的 key 兼容 OpenAI 协议，直接设置即可。"
        )
    return key


@lru_cache(maxsize=1)
def _client() -> Any:  # openai.OpenAI（惰性 import，缺包时报错更友好）
    try:
        from openai import OpenAI
    except ImportError as e:  # pragma: no cover
        raise LLMConfigError("未安装 openai：uv sync") from e
    return OpenAI(base_url=_base_url(), api_key=_api_key())


def _chat(messages: list[dict], tools: list[dict] | None = None,
          thinking: bool = False) -> Any:
    extra = {"enable_thinking": True} if thinking else None
    return _client().chat.completions.create(
        model=model_name(), messages=messages, tools=tools or None,
        extra_body=extra,
        # openai>=1.x：tools=None 表示不开 function calling
    )


def complete_text(messages: list[dict], tools: list[dict] | None = None) -> str:
    """纯文本回复（抽取器用）。messages 里的多模态 content 原样透传。"""
    resp = _chat(messages, tools)
    return resp.choices[0].message.content or ""


def thinking_enabled() -> bool:
    """qwen3 思考输出开关（LLM_THINKING=0 关闭；默认开——页面要展示思考过程）。"""
    return os.environ.get("LLM_THINKING", "1") != "0"


def complete_msg(
    messages: list[dict], tools: list[dict] | None = None
) -> dict[str, Any]:
    """回复成普通 dict（agent loop 用，与具体 SDK 解耦）：

    {"role": "assistant", "content": str|None,
     "reasoning": str|None,            # qwen3 thinking 的思考过程（reasoning_content）
     "tool_calls": [{"id": str, "name": str, "arguments": str}] | None}
    """
    msg = _chat(messages, tools, thinking=thinking_enabled()).choices[0].message
    out: dict[str, Any] = {"role": "assistant", "content": msg.content,
                           "reasoning": getattr(msg, "reasoning_content", None)}
    if msg.tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": tc.function.arguments or "{}",
            }
            for tc in msg.tool_calls
        ]
    return out


class LLMError(RuntimeError):
    """流式终态错误（code：EMPTY_RESPONSE / CONTENT_FILTER / CONTEXT_WINDOW_EXCEEDED…）。"""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


def provider_name() -> str:
    """提供者标识（进 assistant/message 的 source.provider，dsh 同款字段）。"""
    url = _base_url().lower()
    for name in ("dashscope", "deepseek", "openai", "anthropic", "azure"):
        if name in url:
            return name
    return "custom"


def _text(blocks: list[dict]) -> str:
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def _wire(messages: list[dict]) -> list[dict]:
    """块字典消息 → OpenAI 线上格式（dsh serialize 口径）。

    user 消息：text 块拼接 → {"role":"user","content":text}
    assistant 消息：text 块拼接（空则 None）+ tool-call 块 → tool_calls[]；
    reasoning 块不回灌（思考仅展示——结构化取代旧 thought-drop 规则）
    tool-result 消息（content[0] 是 tool-result 块）→ {"role":"tool","tool_call_id",…}
    system 消息原样透传。
    """
    out: list[dict] = []
    for m in messages:
        role = m.get("role")
        if role == "system":
            out.append({"role": "system", "content": m.get("content")})
            continue
        raw = m.get("content")
        if isinstance(raw, str):  # 容忍 OpenAI 风格纯文本消息
            out.append({"role": role or "user", "content": raw})
            continue
        blocks = raw or []
        if blocks and blocks[0].get("type") == "tool-result":
            tb = blocks[0]
            out.append({"role": "tool", "tool_call_id": tb.get("toolCallId"),
                        "content": _text(tb.get("content") or [])})
            continue
        if role == "user":
            out.append({"role": "user", "content": _text(blocks)})
        else:
            msg: dict[str, Any] = {"role": "assistant", "content": _text(blocks) or None}
            tcs = [b for b in blocks if b.get("type") == "tool-call"]
            if tcs:
                msg["tool_calls"] = [
                    {"id": b["id"], "type": "function",
                     "function": {"name": b["name"], "arguments": b["arguments"]}}
                    for b in tcs
                ]
            out.append(msg)
    return out


def stream(messages: list[dict], tools: list[dict] | None = None, *,
           max_tokens: int | None = None, thinking: bool | None = None):
    """OpenAI 兼容流式 → dsh StreamChunk 生成器（llm-deepseek/translate.ts 的移植）。

    尾序契约与 dsh 相同：block-end×N → usage（如有）→ finish，finish 后无任何产出。
    Python SDK 自己消费 [DONE] 哨兵，因此「流自然结束」即对应 dsh 的 [DONE] 分支。
    error 终态以 finish chunk 交付（runner 据此走 llm_error）；传输异常自然向上抛。
    qwen 思考模式仅流式可用（DashScope 约束），本函数即 enable_thinking 的正确打开方式。
    """
    from wagent_backend.llm.assembler import (
        block_end, block_start, finish_chunk, reasoning_delta,
        text_delta, tool_call_delta, usage_chunk,
    )

    kwargs: dict[str, Any] = {
        "model": model_name(), "messages": _wire(messages), "tools": tools or None,
        "stream": True, "stream_options": {"include_usage": True},
    }
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    if thinking_enabled() if thinking is None else thinking:
        kwargs["extra_body"] = {"enable_thinking": True}
    resp = _client().chat.completions.create(**kwargs)

    order: list[int] = []           # 块 index（首次开块顺序，dsh 单 text 块 + 单 reasoning 块）
    partial: dict[int, dict] = {}   # index → {"type","text","id","name","args"}
    next_index = 0
    text_i: int | None = None       # 交叉流式时正文/思考各自追加到同一块（dsh 同款）
    reasoning_i: int | None = None
    tool_i: dict[int, int] = {}     # 线上 tool_calls[i].index → 我们的块 index
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None

    def _open(block_type: str) -> int:
        nonlocal next_index
        i = next_index
        next_index += 1
        partial[i] = {"type": block_type, "text": "", "id": None, "name": None, "args": ""}
        order.append(i)
        return i

    for chunk in resp:
        u = getattr(chunk, "usage", None)
        if u is not None:
            usage = {"inputTokens": getattr(u, "prompt_tokens", 0) or 0,
                     "outputTokens": getattr(u, "completion_tokens", 0) or 0}
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            continue
        ch = choices[0]
        delta = getattr(ch, "delta", None)
        if delta is not None:
            # 思考先判：thinking 模式下 reasoning_content 先于/交错于 content（dsh 同序）
            reasoning = getattr(delta, "reasoning_content", None)
            if isinstance(reasoning, str) and reasoning:  # 空首帧不开块
                if reasoning_i is None:
                    reasoning_i = _open("reasoning")
                    yield block_start(reasoning_i, "reasoning")
                partial[reasoning_i]["text"] += reasoning   # 尾序 block-end 的权威全文
                yield reasoning_delta(reasoning_i, reasoning)
            content = getattr(delta, "content", None)
            if isinstance(content, str) and content:
                if text_i is None:
                    text_i = _open("text")
                    yield block_start(text_i, "text")
                partial[text_i]["text"] += content
                yield text_delta(text_i, content)
            for tc in getattr(delta, "tool_calls", None) or []:
                key = tc.index if tc.index is not None else 0
                if key not in tool_i:
                    tool_i[key] = _open("tool-call")
                    yield block_start(tool_i[key], "tool-call")
                i = tool_i[key]
                p = partial[i]
                if tc.id:
                    p["id"] = tc.id  # qwen 常首帧给全 id+name，后续帧只给 arguments 片段
                fn = getattr(tc, "function", None)
                if fn is not None:
                    if fn.name:
                        p["name"] = fn.name
                    if fn.arguments:
                        p["args"] += fn.arguments
                        yield tool_call_delta(i, p["id"] or f"call-{key}",
                                              fn.arguments, p["name"])
        if getattr(ch, "finish_reason", None):
            finish_reason = ch.finish_reason

    # 流结束：block-end×N（按开块顺序）→ usage → finish
    for i in order:
        p = partial[i]
        if p["type"] in ("text", "reasoning"):
            block = {"type": p["type"], "text": p["text"]}
        else:
            block = {"type": "tool-call", "id": p["id"] or f"call-{i}",
                     "name": p["name"] or "", "arguments": p["args"]}
        yield block_end(i, block)
    if usage is not None:
        yield usage_chunk(usage)
    if finish_reason == "tool_calls":
        yield finish_chunk({"kind": "tool-calls"})
    elif finish_reason == "length":
        yield finish_chunk({"kind": "max-tokens"})
    elif finish_reason in (None, "stop"):
        if not order:  # 宣称完成却零产出 —— dsh 同款失败
            yield finish_chunk({"kind": "error", "failure": {
                "message": "model returned a completed response with no content",
                "code": "EMPTY_RESPONSE"}})
            return
        yield finish_chunk({"kind": "stop"})
    else:  # content_filter 等异常终态
        yield finish_chunk({"kind": "error", "failure": {
            "message": f"upstream finish_reason: {finish_reason}",
            "code": str(finish_reason).upper()}})

