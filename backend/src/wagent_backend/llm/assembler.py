"""assembler —— 提供者中立的流式块词汇 + 组装器（dsh llm/assembler.ts 的 Python 移植）。

StreamChunk 判别字典（与 dsh 逐字段一致，键用 camelCase 对齐事件日志）：
    {"type": "block-start",     "index": i, "blockType": "text"|"reasoning"|"tool-call"}
    {"type": "text-delta",      "index": i, "text": s}
    {"type": "reasoning-delta", "index": i, "text": s}
    {"type": "tool-call-delta", "index": i, "id": s, "name": s?, "argumentsDelta": s}
    {"type": "block-end",       "index": i, "block": <完整块>}
    {"type": "usage",           "usage": {"inputTokens": n, "outputTokens": n}}
    {"type": "finish",          "reason": {"kind": "stop"|"tool-calls"|"max-tokens"|"error",
                                           "failure"?: {"message": s, "code": s}}}

reasoning 是一等信息（dsh 把 DeepSeek/qwen 的思考过程建模为首类块类型，先于正文交错）。
BlockAssembler 是唯一的组装算法：稀疏 {index: 部分块} + order[]（首次见到 index 的顺序）；
delta 只追加；block-end 权威冻结（闭块后的迟到 delta 忽略，先关闭者胜）；
blocks() 按流序返回；max-tokens 终态丢弃 tool-call 块（截断的参数不可安全执行）；
流结束而无 finish 时默认 stop。
"""

from __future__ import annotations

from typing import Any


# ── chunk 构造器（测试与 client.stream 共用）──────────────

def block_start(index: int, block_type: str) -> dict[str, Any]:
    return {"type": "block-start", "index": index, "blockType": block_type}


def text_delta(index: int, text: str) -> dict[str, Any]:
    return {"type": "text-delta", "index": index, "text": text}


def reasoning_delta(index: int, text: str) -> dict[str, Any]:
    return {"type": "reasoning-delta", "index": index, "text": text}


def tool_call_delta(index: int, id: str, arguments_delta: str,
                    name: str | None = None) -> dict[str, Any]:
    d: dict[str, Any] = {"type": "tool-call-delta", "index": index,
                         "id": id, "argumentsDelta": arguments_delta}
    if name:
        d["name"] = name
    return d


def block_end(index: int, block: dict[str, Any]) -> dict[str, Any]:
    return {"type": "block-end", "index": index, "block": block}


def usage_chunk(usage: dict[str, Any]) -> dict[str, Any]:
    return {"type": "usage", "usage": usage}


def finish_chunk(reason: dict[str, Any]) -> dict[str, Any]:
    return {"type": "finish", "reason": reason}


# ── 块提取（runner 的旧三件套：正文 / 思考 / 工具调用）────

def text_of(blocks: list[dict[str, Any]]) -> str:
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")


def reasoning_of(blocks: list[dict[str, Any]]) -> str:
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "reasoning")


def tool_calls_of(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [b for b in blocks if b.get("type") == "tool-call"]


class _Partial:
    """组装中的部分块（dsh PartialBlock）。block 非 None 表示已被 block-end 冻结。"""

    __slots__ = ("block_type", "text", "call_id", "call_name", "call_args", "block")

    def __init__(self, block_type: str):
        self.block_type = block_type
        self.text = ""
        self.call_id: str | None = None
        self.call_name: str | None = None
        self.call_args = ""
        self.block: dict[str, Any] | None = None


class BlockAssembler:
    """逐 chunk 聚合为 content 块列表（dsh 的「唯一组装算法」）。"""

    def __init__(self):
        self._partials: dict[int, _Partial] = {}
        self._order: list[int] = []
        self._usage: dict[str, Any] | None = None
        self._finish: dict[str, Any] | None = None

    def push(self, chunk: dict[str, Any]) -> None:
        t = chunk["type"]
        if t in ("text-delta", "reasoning-delta"):
            p = self._ensure(chunk["index"], "text" if t == "text-delta" else "reasoning")
            if p.block is not None:
                return  # 已闭块：忽略迟到 delta
            p.text += chunk["text"]
        elif t == "tool-call-delta":
            p = self._ensure(chunk["index"], "tool-call")
            if p.block is not None:
                return
            p.call_id = chunk.get("id") or p.call_id
            if chunk.get("name"):
                p.call_name = chunk["name"]
            p.call_args += chunk.get("argumentsDelta") or ""
        elif t == "block-end":
            block = chunk["block"]
            p = self._ensure(chunk["index"], block.get("type", ""))
            if p.block is None:  # 先关闭者胜，后续 close 忽略
                p.block = block
        elif t == "usage":
            self._usage = chunk["usage"]
        elif t == "finish":
            self._finish = chunk["reason"]
        # block-start 不带状态：块在首个 delta 到达时惰性建立（容忍缺失 block-start 的流）

    def _ensure(self, index: int, block_type: str) -> _Partial:
        p = self._partials.get(index)
        if p is None:
            p = _Partial(block_type)
            self._partials[index] = p
            self._order.append(index)
        return p

    def _assemble(self, p: _Partial, index: int) -> dict[str, Any]:
        if p.block_type in ("text", "reasoning"):
            return {"type": p.block_type, "text": p.text}
        return {"type": "tool-call", "id": p.call_id or f"call-{index}",
                "name": p.call_name or "", "arguments": p.call_args}

    def blocks(self) -> list[dict[str, Any]]:
        drop_tools = self._finish is not None and self._finish.get("kind") == "max-tokens"
        out: list[dict[str, Any]] = []
        for i in self._order:
            p = self._partials[i]
            block = p.block if p.block is not None else self._assemble(p, i)
            if drop_tools and block.get("type") == "tool-call":
                continue
            out.append(block)
        return out

    @property
    def usage(self) -> dict[str, Any] | None:
        return self._usage

    @property
    def finish(self) -> dict[str, Any]:
        return self._finish if self._finish is not None else {"kind": "stop"}
