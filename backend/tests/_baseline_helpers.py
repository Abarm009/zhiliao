"""继承基线测试的公共 helper（从旧 WAgent 工作区复制，不依赖旧目录）。

原来的 `from conftest import stream_of` 在两种 conftest.py 同名时会被解析到
`backend/tests/octosense_backend/conftest.py`，导致 test_ops_agent /
test_ops_api 收集失败。helper 抽成普通模块后，导入路径唯一、无名称碰撞。
"""
from __future__ import annotations


def _pieces(text: str, size: int = 16) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] or [""]


def chunks_of(resp: dict) -> list[dict]:
    """{content, reasoning, tool_calls, usage?} → StreamChunk 序列。

    文本切成 16 字符小片，让 delta 合并路径真的被走到。
    """
    from wagent_backend.llm import assembler as asm

    chunks: list[dict] = []
    idx = 0
    if resp.get("reasoning"):
        chunks.append(asm.block_start(idx, "reasoning"))
        chunks += [asm.reasoning_delta(idx, p) for p in _pieces(resp["reasoning"])]
        chunks.append(asm.block_end(idx, {"type": "reasoning", "text": resp["reasoning"]}))
        idx += 1
    if resp.get("content"):
        chunks.append(asm.block_start(idx, "text"))
        chunks += [asm.text_delta(idx, p) for p in _pieces(resp["content"])]
        chunks.append(asm.block_end(idx, {"type": "text", "text": resp["content"]}))
        idx += 1
    for tc in resp.get("tool_calls") or []:
        chunks.append(asm.block_start(idx, "tool-call"))
        chunks.append(asm.tool_call_delta(idx, tc["id"], tc["arguments"], name=tc["name"]))
        chunks.append(asm.block_end(idx, {
            "type": "tool-call", "id": tc["id"], "name": tc["name"],
            "arguments": tc["arguments"]}))
        idx += 1
    if resp.get("usage"):
        chunks.append(asm.usage_chunk(resp["usage"]))
    chunks.append(asm.finish_chunk(
        {"kind": "tool-calls" if resp.get("tool_calls") else "stop"}))
    return chunks


def stream_of(fn):
    """complete 型 fake(messages, tools)→dict 包装成 stream 型 callable→迭代器。"""
    def _stream(messages, tools=None, **kwargs):
        return iter(chunks_of(fn(messages, tools)))
    return _stream
