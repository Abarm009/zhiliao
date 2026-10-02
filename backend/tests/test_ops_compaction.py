"""compaction —— L3 会话压缩测试（dsh compaction-basic 契约）。"""

from __future__ import annotations

import json

import pytest

from wagent_backend.llm import client
from wagent_backend.ops.agent import compaction, pruner
from wagent_backend.ops.agent.compaction import (CHECKPOINT_PREAMBLE,
                                                 COMPACTION_INSTRUCTION,
                                                 SUMMARY_CLOSE_TAG, SUMMARY_OPEN_TAG)
from wagent_backend.ops.agent.events import EventLog

SYSTEM = "你是设施运维 Agent。"
TOOLS = [{"type": "function", "function": {"name": "resolve_space",
                                           "parameters": {}}}]


def _u(text, source=None):
    return {"id": "u" + text[:3], "role": "user",
            "content": [{"type": "text", "text": text}],
            "source": source or {"kind": "user"}}


def _a(text, calls=None):
    blocks = [{"type": "text", "text": text}] if text else []
    for c in calls or []:
        blocks.append({"type": "tool-call", "id": c[0], "name": c[1], "arguments": c[2]})
    return {"id": "a1", "role": "assistant", "content": blocks,
            "source": {"kind": "model", "provider": "dashscope", "model": "qwen"}}


def _tr(call_id, result_text):
    return {"id": "t1", "role": "user",
            "content": [{"type": "tool-result", "toolCallId": call_id,
                         "content": [{"type": "text", "text": result_text}],
                         "isError": False}],
            "source": {"kind": "tool", "callId": call_id}}


def _fake_stream(summary_text="## Primary Request and Intent\n- 修空调", *, error=None):
    """摘要假流：吞掉入参，吐固定摘要（或 error finish）。"""
    seen = []

    def stream(messages, tools=None, **kwargs):
        seen.append((messages, tools, kwargs))
        from wagent_backend.llm import assembler as asm
        if error:
            yield asm.finish_chunk({"kind": "error",
                                    "failure": {"message": error, "code": "BOOM"}})
            return
        yield asm.block_start(0, "text")
        yield asm.text_delta(0, summary_text)
        yield asm.block_end(0, {"type": "text", "text": summary_text})
        yield asm.finish_chunk({"kind": "stop"})
    return stream, seen


def _rich_log():
    """user → assistant(tool-call) → tool/result → user → assistant（可压缩的厚历史）。"""
    log = EventLog()
    log.append("turn/start", {"turn": 1})
    log.append("user/message", _u("A座25楼东侧空调又不制冷了" * 40), surface_op="append")
    log.append("assistant/message", {"message": _a("先查历史", [("c1", "query_workorder_history", "{}")])},
               surface_op="append")
    log.append("tool/result", {"turn": 1, "step": 1, "message": _tr("c1", "WO-B25-0720 电动阀执行器更换……" * 30),
                               "meta": {"name": "query_workorder_history", "digest": "…", "duration_ms": 3}},
               surface_op="append")
    log.append("user/message", _u("麻烦尽快处理" * 10), surface_op="append")
    log.append("assistant/message", {"message": _a("收到，正在诊断。")},
               surface_op="append")
    return log


# ── 模板逐字（dsh summarizer.ts）─────────────────────────

def test_templates_verbatim():
    assert SUMMARY_OPEN_TAG == "<compacted-summary>"
    assert SUMMARY_CLOSE_TAG == "</compacted-summary>"
    assert COMPACTION_INSTRUCTION.startswith(
        "You are now acting as a compaction engine for this AI coding assistant.")
    for section in ["Primary Request and Intent", "Key Technical Concepts",
                    "Files and Code", "Errors and Fixes", "Pending Jobs",
                    "Current Work", "Next Step", "Critical Context"]:
        assert f"## {section}" in COMPACTION_INSTRUCTION
    assert "PRIOR checkpoint" in COMPACTION_INSTRUCTION
    assert CHECKPOINT_PREAMBLE.startswith("This is an automatically generated checkpoint")


# ── 区段选择 ─────────────────────────────────────────────

def test_select_range_head_anchored_and_retains_tail():
    log = _rich_log()
    retain = 60   # 尾部保留 ~60 估算 token → 只压缩头部
    rng = compaction.select_compactable_range(log, retain)
    nodes = log.surface_nodes
    assert rng is not None
    assert rng["start"] == nodes[0]           # 头锚定
    assert rng["end"] in nodes                # 是真实节点
    assert rng["end"] != nodes[-1]            # 尾部有保留
    # 保留段的估算 token ≥ retain
    kept = [t for seq, t in log.measure_surface()
            if nodes.index(seq) > nodes.index(rng["end"])]
    assert sum(kept) >= retain


def test_select_range_never_splits_tool_pair():
    # 尾预算刚好落在 tool-call 与 tool/result 之间 → 必须退到配对平衡边界
    log = EventLog()
    log.append("turn/start", {"turn": 1})
    log.append("user/message", _u("u1" * 200), surface_op="append")          # 0
    log.append("assistant/message", {"message": _a(None, [("c1", "resolve_space", "{}")])},
               surface_op="append")                                          # 1
    log.append("tool/result", {"turn": 1, "step": 1, "message": _tr("c1", "ok"),
                               "meta": {"name": "resolve_space", "digest": "…", "duration_ms": 1}},
               surface_op="append")                                          # 2
    log.append("user/message", _u("u2"), surface_op="append")                # 3
    priced = log.measure_surface()
    # 保留 = 最后两个节点（user2 + tool/result）→ keep 想落在 assistant 与
    # tool/result 之间，平衡约束逼它退到 assistant 之前
    retain = priced[-1][1] + priced[-2][1]
    rng = compaction.select_compactable_range(log, retain)
    assert rng == {"start": log.surface_nodes[0], "end": log.surface_nodes[0]}
    # 只压头节点（user1）；assistant+result 成对保留


def test_select_range_nothing_compactable():
    log = EventLog()
    log.append("user/message", _u("hi"), surface_op="append")
    assert compaction.select_compactable_range(log, 0) is None  # 尾预算 0 也得保留最后节点语义？


# ── 事务：恰好 4 事件、must-be-smaller、fail-closed ──────

def test_compact_region_exactly_four_events_and_replace():
    log = _rich_log()
    stream, seen = _fake_stream()
    nodes = log.surface_nodes
    start, end = nodes[0], nodes[2]
    n0 = len(log.events)
    result = compaction.compact_region(stream, log, start, end, turn=1,
                                       system=SYSTEM, tools=TOOLS)

    added = log.events[n0:]
    assert [e["type"] for e in added] == [
        "compaction/start", "compaction/summary", "user/message", "compaction/end"]
    cid = added[0]["data"]["compactionId"]
    assert result["compactionId"] == cid
    # summary 记录影子区段与溯源
    assert added[1]["data"]["shadowedSeqs"] == [start, nodes[1], end]
    assert added[1]["data"]["shadowedTokenCount"] > 0
    assert added[1]["data"]["summary"][0]["type"] == "text"
    # 替换节点：checkpoint 三段式 + plugin 来源 + surfaceOp replace + 溯源覆盖
    repl = added[2]
    texts = [b["text"] for b in repl["data"]["content"]]
    assert texts[0] == f"{CHECKPOINT_PREAMBLE}\n\n{SUMMARY_OPEN_TAG}"
    assert texts[2] == SUMMARY_CLOSE_TAG
    assert repl["data"]["source"] == {"kind": "plugin", "plugin": "compaction",
                                      "compactionId": cid}
    assert repl["surfaceOp"] == {"op": "replace", "start": start, "end": end}
    assert set([start, nodes[1], end]) <= set(repl["sourceEventSeqs"])
    # surface：区段 3 节点换成 1 个 checkpoint 节点
    assert log.surface_nodes == [repl["seq"], *nodes[3:]]
    # 摘要调用复放了 system + 区段消息 + 尾部指令（前缀缓存对齐）
    msgs = seen[0][0]
    assert msgs[0] == {"role": "system", "content": SYSTEM}
    assert msgs[-1]["content"][0]["text"] == COMPACTION_INSTRUCTION
    assert seen[0][2]["max_tokens"] == compaction._MAX_TOKENS
    assert seen[0][2]["thinking"] is False


def test_compact_region_summary_must_be_smaller():
    log = _rich_log()
    huge = "摘要不算小：" + "细节满满 " * 3000   # framed 后 ≥ 被遮蔽内容
    stream, _ = _fake_stream(huge)
    nodes = log.surface_nodes
    n0 = len(log.events)
    with pytest.raises(ValueError, match="not smaller"):
        compaction.compact_region(stream, log, nodes[0], nodes[2], turn=1,
                                  system=SYSTEM, tools=TOOLS)
    added = log.events[n0:]
    # fail-closed：start 之后恰好一条带 error 的 end，没有 summary/替换
    assert [e["type"] for e in added] == ["compaction/start", "compaction/end"]
    assert "not smaller" in added[1]["data"]["error"]
    assert log.surface_nodes == nodes   # surface 未变


def test_compact_region_error_finish_fail_closed():
    log = _rich_log()
    stream, _ = _fake_stream(error="upstream boom")
    nodes = log.surface_nodes
    with pytest.raises(client.LLMError):
        compaction.compact_region(stream, log, nodes[0], nodes[2], turn=1,
                                  system=SYSTEM, tools=TOOLS)
    assert log.events[-1]["type"] == "compaction/end"
    assert "upstream boom" in log.events[-1]["data"]["error"]


def test_compact_region_rejects_unbalanced_boundary():
    log = _rich_log()
    stream, _ = _fake_stream()
    nodes = log.surface_nodes
    # end 落在 assistant(tool-call) 与 tool/result 之间（= 只遮到 assistant）
    with pytest.raises(ValueError, match="平衡边界"):
        compaction.compact_region(stream, log, nodes[0], nodes[1], turn=1,
                                  system=SYSTEM, tools=TOOLS)
    assert "compaction/start" not in [e["type"] for e in log.events]  # 校验先于 start


# ── 自动门闩 ─────────────────────────────────────────────

def test_compact_if_needed_below_threshold_noop(monkeypatch):
    monkeypatch.setenv("WAGENT_CONTEXT_WINDOW", "32768")
    log = _rich_log()
    n0 = len(log.events)
    stream, _ = _fake_stream()
    assert compaction.compact_if_needed(stream, log, SYSTEM, TOOLS, turn=1) is None
    assert len(log.events) == n0   # 低于阈值：什么也不做


def test_compact_if_needed_pressure_with_small_window(monkeypatch):
    monkeypatch.setenv("WAGENT_CONTEXT_WINDOW", "700")   # 演示口径：小窗口逼出压缩
    log = _rich_log()
    stream, _ = _fake_stream()
    assert log.token_estimate() > 560   # 0.8×700
    result = compaction.compact_if_needed(stream, log, SYSTEM, TOOLS, turn=2)
    assert result is not None
    assert "compaction/summary" in [e["type"] for e in log.events]
    assert log.token_estimate() < 560   # 压缩后低于阈值
    # 模型可见历史：第一条变成 checkpoint（PREAMBLE 开头）
    msgs = log.derive_messages()
    assert msgs[0]["content"][0]["text"].startswith(CHECKPOINT_PREAMBLE)


def test_compact_if_needed_disabled(monkeypatch):
    monkeypatch.setenv("WAGENT_COMPACTION", "0")
    monkeypatch.setenv("WAGENT_CONTEXT_WINDOW", "100")
    log = _rich_log()
    stream, _ = _fake_stream()
    assert compaction.compact_if_needed(stream, log, SYSTEM, TOOLS, turn=1) is None
    assert "compaction/summary" not in [e["type"] for e in log.events]


def test_is_context_overflow():
    assert compaction.is_context_overflow(
        RuntimeError("This model maximum context length is 128000 tokens"))
    assert compaction.is_context_overflow(
        RuntimeError("code=context_length_exceeded input too large"))
    assert compaction.is_context_overflow(
        RuntimeError("Error code: 400 - messages too long for this model"))
    assert not compaction.is_context_overflow(RuntimeError("quota exceeded"))
    assert not compaction.is_context_overflow(RuntimeError("connection reset"))


def test_overflow_trigger_forces_reduction(monkeypatch):
    """context-overflow：绕过阈值，retain=0 强制一次平衡缩减。"""
    log = _rich_log()
    stream, _ = _fake_stream()
    result = compaction.compact_if_needed(stream, log, SYSTEM, TOOLS, turn=1,
                                          trigger="context-overflow")
    assert result is not None
    assert log.surface_nodes[0] != _rich_log().surface_nodes[0]
    # 原日志事件全部保留（追加不删改）
    assert "compaction/start" in [e["type"] for e in log.events]


def test_prune_runs_before_summary(monkeypatch):
    """pressure 路径：先跑模型无关裁剪，复测仍超才摘要。"""
    monkeypatch.setenv("WAGENT_CONTEXT_WINDOW", "1000")
    log = _rich_log()
    # 造一个超预算 tool/result，后再补一条用户消息（保证尾部保留段不含巨无霸）
    big = {"id": "b", "role": "user",
           "content": [{"type": "tool-result", "toolCallId": "c1",
                        "content": [{"type": "text", "text": "Q" * 20000}],
                        "isError": False}],
           "source": {"kind": "tool", "callId": "c1"}}
    log.append("tool/result", {"turn": 1, "step": 9, "message": big, "meta": {}},
               surface_op="append", source_event_seqs=[1])
    log.append("user/message", _u("后续跟进 " * 100), surface_op="append")
    stream, _ = _fake_stream()
    result = compaction.compact_if_needed(stream, log, SYSTEM, TOOLS, turn=2)
    assert result is not None
    types = [e["type"] for e in log.events]
    assert "compaction/prune" in types                      # 裁剪先发生
    assert types.index("compaction/prune") < types.index("compaction/summary")
    last_tr = [e for e in log.events if e["type"] == "tool/result"][-1]
    assert pruner.PRUNE_MARKER in last_tr["data"]["message"]["content"][0]["content"][0]["text"]
