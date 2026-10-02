"""BlockAssembler 组装测试 —— dsh「唯一组装算法」的移植验证。"""

from __future__ import annotations

from wagent_backend.llm.assembler import (
    BlockAssembler, block_end, finish_chunk, reasoning_delta, text_delta,
    tool_call_delta,
)


def test_merge_deltas_and_stream_order():
    a = BlockAssembler()
    # 乱序 index：blocks() 按首次见到的顺序（流序），不是数字序
    a.push(text_delta(5, "a"))
    a.push(reasoning_delta(2, "b"))
    assert a.blocks() == [{"type": "text", "text": "a"},
                          {"type": "reasoning", "text": "b"}]


def test_block_end_freezes_ignores_stragglers():
    a = BlockAssembler()
    a.push(text_delta(0, "部分"))
    a.push(block_end(0, {"type": "text", "text": "最终"}))
    a.push(text_delta(0, "迟到"))  # 闭块后的迟到 delta 忽略
    assert a.blocks() == [{"type": "text", "text": "最终"}]


def test_max_tokens_drops_tool_calls():
    a = BlockAssembler()
    a.push(text_delta(0, "x"))
    a.push(tool_call_delta(1, "call-1", "{}", "notify"))
    a.push(finish_chunk({"kind": "max-tokens"}))
    # 截断的参数不可安全执行 —— 丢弃 tool-call 块
    assert a.blocks() == [{"type": "text", "text": "x"}]


def test_finish_defaults_stop():
    assert BlockAssembler().finish == {"kind": "stop"}


def test_tool_call_defaults():
    a = BlockAssembler()
    a.push(tool_call_delta(3, "", '{"q":1}'))  # 无 id 无 name
    assert a.blocks() == [{"type": "tool-call", "id": "call-3",
                           "name": "", "arguments": '{"q":1}'}]


def test_usage_rides_assembler():
    a = BlockAssembler()
    a.push({"type": "usage", "usage": {"inputTokens": 3, "outputTokens": 4}})
    assert a.usage == {"inputTokens": 3, "outputTokens": 4}
