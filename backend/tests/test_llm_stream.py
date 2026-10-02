"""client.stream 流式翻译测试 —— 假 OpenAI 流（不调真实模型）。

覆盖 dsh llm-deepseek/translate.ts 的移植要点：思考先序/正文块、工具片段拼接、
空首帧不开块、block-end×N → usage → finish 尾序、finish_reason 映射、_wire 序列化。
"""

from __future__ import annotations

from types import SimpleNamespace

from wagent_backend.llm import client


# ── 假 OpenAI 流（结构对齐 openai>=1.x 的 ChatCompletionChunk）──

class _FakeCompletions:
    def __init__(self, chunks, capture):
        self._chunks, self._capture = chunks, capture

    def create(self, **kwargs):
        self._capture.update(kwargs)
        return iter(self._chunks)


class _FakeClient:
    def __init__(self, chunks, capture):
        self.chat = SimpleNamespace(completions=_FakeCompletions(chunks, capture))


def _delta(content=None, reasoning=None, tool_calls=None):
    return SimpleNamespace(content=content, reasoning_content=reasoning,
                           tool_calls=tool_calls)


def _tc(index, id=None, name=None, arguments=None):
    return SimpleNamespace(index=index, id=id,
                           function=SimpleNamespace(name=name, arguments=arguments))


def _chunk(delta=None, finish=None, usage=None):
    choices = [SimpleNamespace(delta=delta, finish_reason=finish)] if (delta or finish) else []
    return SimpleNamespace(choices=choices, usage=usage)


def _run(monkeypatch, chunks):
    capture: dict = {}
    monkeypatch.setattr(client, "_client", lambda: _FakeClient(chunks, capture))
    return list(client.stream([{"role": "user", "content": "x"}])), capture


def test_reasoning_then_text_block_order(monkeypatch):
    out, _ = _run(monkeypatch, [
        _chunk(delta=_delta(reasoning="思")), _chunk(delta=_delta(reasoning="考")),
        _chunk(delta=_delta(content="答")), _chunk(finish="stop"),
    ])
    kinds = [(c["type"], c.get("blockType", c.get("index"))) for c in out]
    # 思考块先开（index 0），正文块后开（index 1）；block-end 按开块顺序
    assert kinds == [("block-start", "reasoning"), ("reasoning-delta", 0),
                     ("reasoning-delta", 0), ("block-start", "text"),
                     ("text-delta", 1), ("block-end", 0), ("block-end", 1),
                     ("finish", None)]
    assert out[-1]["reason"] == {"kind": "stop"}


def test_block_end_carries_accumulated_text(monkeypatch):
    """回归：尾序 block-end 的权威块必须带全部 delta 文本（曾发空串被组装器冻结）。"""
    from wagent_backend.llm.assembler import BlockAssembler

    out, _ = _run(monkeypatch, [
        _chunk(delta=_delta(reasoning="先想")),
        _chunk(delta=_delta(content="你")), _chunk(delta=_delta(content="好")),
        _chunk(finish="stop"),
    ])
    asm = BlockAssembler()
    for c in out:
        asm.push(c)
    assert asm.blocks() == [{"type": "reasoning", "text": "先想"},
                            {"type": "text", "text": "你好"}]


def test_tool_call_fragments_concatenate(monkeypatch):
    out, _ = _run(monkeypatch, [
        _chunk(delta=_delta(tool_calls=[_tc(0, id="call-1", name="resolve_space", arguments='{"q"')])),
        _chunk(delta=_delta(tool_calls=[_tc(0, arguments=': "A座"}')])),
        _chunk(finish="tool_calls"),
    ])
    deltas = [c for c in out if c["type"] == "tool-call-delta"]
    # 第二帧没带 id/name，仍要带上已知状态（dsh adapter 同款）
    assert deltas[0]["id"] == "call-1" and deltas[0]["name"] == "resolve_space"
    assert deltas[1]["id"] == "call-1" and deltas[1]["argumentsDelta"] == ': "A座"}'
    end = next(c for c in out if c["type"] == "block-end")
    assert end["block"] == {"type": "tool-call", "id": "call-1",
                            "name": "resolve_space", "arguments": '{"q": "A座"}'}
    assert out[-1]["reason"] == {"kind": "tool-calls"}


def test_empty_first_chunk_opens_no_block(monkeypatch):
    out, _ = _run(monkeypatch, [
        _chunk(delta=_delta(reasoning="")), _chunk(delta=_delta(content="好")),
        _chunk(finish="stop"),
    ])
    assert all(c.get("blockType") != "reasoning" for c in out)
    assert out[-1]["reason"] == {"kind": "stop"}


def test_usage_before_finish_nothing_after(monkeypatch):
    out, _ = _run(monkeypatch, [
        _chunk(delta=_delta(content="a")), _chunk(finish="stop"),
        _chunk(usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5)),
    ])
    assert [c["type"] for c in out[-3:]] == ["block-end", "usage", "finish"]
    assert out[-2]["usage"] == {"inputTokens": 10, "outputTokens": 5}


def test_done_missing_maps_to_stop(monkeypatch):
    out, _ = _run(monkeypatch, [_chunk(delta=_delta(content="x"))])
    assert out[-1]["reason"] == {"kind": "stop"}


def test_empty_stream_empty_response_error(monkeypatch):
    out, _ = _run(monkeypatch, [_chunk(finish="stop")])
    assert out == [{"type": "finish", "reason": {"kind": "error", "failure": {
        "message": "model returned a completed response with no content",
        "code": "EMPTY_RESPONSE"}}}]


def test_finish_length_maps_max_tokens(monkeypatch):
    out, _ = _run(monkeypatch, [_chunk(delta=_delta(content="x")), _chunk(finish="length")])
    assert out[-1]["reason"] == {"kind": "max-tokens"}


def test_content_filter_maps_error(monkeypatch):
    out, _ = _run(monkeypatch, [_chunk(finish="content_filter")])
    assert out[-1]["reason"]["kind"] == "error"
    assert out[-1]["reason"]["failure"]["code"] == "CONTENT_FILTER"


def test_stream_request_options(monkeypatch):
    _, capture = _run(monkeypatch, [_chunk(delta=_delta(content="x"))])
    assert capture["stream"] is True
    assert capture["stream_options"] == {"include_usage": True}
    assert capture["extra_body"] == {"enable_thinking": True}  # 默认开思考


def test_wire_drops_reasoning_and_maps_tool_result():
    wire = client._wire([
        {"role": "system", "content": "sys"},
        {"id": "u1", "role": "user",
         "content": [{"type": "text", "text": "你好"}], "source": {"kind": "user"}},
        {"id": "a1", "role": "assistant",
         "content": [{"type": "reasoning", "text": "想"},
                     {"type": "text", "text": ""},
                     {"type": "tool-call", "id": "c1", "name": "notify", "arguments": "{}"}],
         "source": {}},
        {"id": "t1", "role": "user",
         "content": [{"type": "tool-result", "toolCallId": "c1",
                      "content": [{"type": "text", "text": '{"ok": true}'}],
                      "isError": False}],
         "source": {}},
    ])
    assert wire[0] == {"role": "system", "content": "sys"}
    assert wire[1] == {"role": "user", "content": "你好"}
    # reasoning 块不回灌；正文空则 None；tool-call 块 → OpenAI tool_calls
    assert wire[2] == {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c1", "type": "function",
         "function": {"name": "notify", "arguments": "{}"}}]}
    assert wire[3] == {"role": "tool", "tool_call_id": "c1", "content": '{"ok": true}'}
