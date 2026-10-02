"""pruner —— 工具结果中段裁剪测试（dsh compaction-tool-result-pruner 契约）。"""

from __future__ import annotations

from wagent_backend.ops.agent import pruner
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.pruner import PRUNE_MARKER, HEAD_CHARS, TAIL_CHARS, THRESHOLD_CHARS


def _tool_result_ev(call_id="c1", text="x", n=None):
    return {"message": {"id": "m", "role": "user",
                        "content": [{"type": "tool-result", "toolCallId": call_id,
                                     "content": [{"type": "text", "text": "x" * (n or len(text))
                                                  if n else text}],
                                     "isError": False}],
                        "source": {"kind": "tool", "callId": call_id}},
            "meta": {"name": "get_assets_serving_space", "digest": "…", "duration_ms": 1}}


def test_constants_verbatim():
    assert PRUNE_MARKER == "\n\n[... tool result middle pruned ...]\n\n"
    assert (THRESHOLD_CHARS, HEAD_CHARS, TAIL_CHARS) == (8192, 4096, 1024)
    assert HEAD_CHARS + len(PRUNE_MARKER) + TAIL_CHARS <= THRESHOLD_CHARS  # 不变量


def test_within_budget_untouched():
    blocks = [{"type": "text", "text": "short"}]
    assert pruner.prune_content(blocks) is None


def test_prune_keeps_head_and_tail_single_marker():
    text = "A" * 10000
    out = pruner.prune_content([{"type": "text", "text": text}])
    assert out is not None
    new = out[0]["text"]
    assert new.startswith("A" * HEAD_CHARS)
    assert new.endswith("A" * TAIL_CHARS)
    assert new.count(PRUNE_MARKER) == 1                     # marker 恰一个
    assert len(new) == HEAD_CHARS + len(PRUNE_MARKER) + TAIL_CHARS
    assert len(new) < len(text) and len(new) <= THRESHOLD_CHARS


def test_marker_in_first_intersecting_block_multiblock():
    # 两个文本块：第一个与删除区间相交 → marker 落在第一个
    blocks = [{"type": "text", "text": "B" * 5000},
              {"type": "text", "text": "C" * 5000}]
    out = pruner.prune_content(blocks)
    joined = "".join(b["text"] for b in out if b.get("text"))
    assert joined.count(PRUNE_MARKER) == 1
    assert joined.startswith("B" * HEAD_CHARS)              # 头保留完整
    assert joined.endswith("C" * TAIL_CHARS)                # 尾保留完整
    # 非文本块原样保留、顺序不变
    blocks2 = [{"type": "text", "text": "D" * 9000},
               {"type": "image", "url": "u"}]
    out2 = pruner.prune_content(blocks2)
    assert any(b.get("type") == "image" for b in out2)


def test_session_prune_replaces_content_only_and_keeps_original():
    log = EventLog()
    call = log.append("tool/call", {"turn": 1, "step": 1, "callId": "c1",
                                    "name": "get_assets_serving_space", "arguments": "{}"})
    full = _tool_result_ev(text="Z" * 10000)["message"]
    log.append("tool/result", {"turn": 1, "step": 1, "message": full, "meta": full and {}},
               surface_op="append", source_event_seqs=[call["seq"]])
    before_nodes = list(log.surface_nodes)

    result = pruner.prune_session(log)

    assert len(result["pruned"]) == 1
    entry = result["pruned"][0]
    assert entry["charsBefore"] == 10000
    assert entry["charsAfter"] == HEAD_CHARS + len(PRUNE_MARKER) + TAIL_CHARS
    # 事件对：compaction/prune + 替换 tool/result（surface 单节点换单节点）
    types = [e["type"] for e in log.events]
    assert types[-2:] == ["compaction/prune", "tool/result"]
    prune_ev, repl = log.events[-2], log.events[-1]
    assert prune_ev["data"]["shadowedSeqs"] == [before_nodes[0]]
    assert repl["surfaceOp"] == {"op": "replace", "start": before_nodes[0], "end": before_nodes[0]}
    # 原全文事件永留日志（只是不再位于 surface）
    assert "Z" * 9000 in str(log.events[before_nodes[0]])
    assert PRUNE_MARKER in repl["data"]["message"]["content"][0]["content"][0]["text"]
    # 派生消息（模型可见面）已换成裁剪版
    msgs = log.derive_messages()
    assert PRUNE_MARKER in msgs[-1]["content"][0]["content"][0]["text"]


def test_session_prune_skips_small_results():
    log = EventLog()
    call = log.append("tool/call", {"turn": 1, "step": 1, "callId": "c1",
                                    "name": "resolve_space", "arguments": "{}"})
    ev = _tool_result_ev(text='{"matches": []}')
    log.append("tool/result", {"turn": 1, "step": 1,
                               "message": ev["message"], "meta": {}},
               surface_op="append", source_event_seqs=[call["seq"]])
    assert pruner.prune_session(log) == {"pruned": [], "charsRemoved": 0}
    assert len(log.events) == 2   # 什么也没追加
