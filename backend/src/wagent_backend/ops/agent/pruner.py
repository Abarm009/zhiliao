"""pruner —— L3 工具结果中段裁剪（dsh compaction-tool-result-pruner 的 Python 移植）。

模型无关、确定性：超预算（8192 码点）的 tool-result 文本中段被替换为
PRUNE_MARKER，保留头 4096 + 尾 1024；不改变块的种类与顺序。
落日志方式（重放安全）：每个被裁节点先记 compaction/prune（影子定价），
再追加一个 **content-only 替换**的 tool/result（surfaceOp replace 单节点，
仅 message.content[0].content 变化）——原全文事件永留日志，回放永远可恢复。
"""

from __future__ import annotations

from typing import Any

# ── 常量（dsh config.ts 逐字）────────────────────────────
PRUNE_MARKER = "\n\n[... tool result middle pruned ...]\n\n"
THRESHOLD_CHARS = 8192   # 超过才裁
HEAD_CHARS = 4096        # 保留头
TAIL_CHARS = 1024        # 保留尾


def _measure(blocks: list[dict[str, Any]]) -> int:
    """文本块的 Unicode 码点总数（非文本块计 0）——Python str 天然按码点计。"""
    return sum(len(b.get("text") or "") for b in blocks if b.get("type") == "text")


def prune_content(blocks: list[dict[str, Any]]) -> list[dict[str, Any]] | None:
    """裁掉超预算的文本中段；预算内返回 None（不动）。

    头/尾预算跨块累计；marker 只插一次（落在首个与删除区间相交的文本块）。
    不变量：裁后必须小于阈值且严格小于原文，否则抛错。
    """
    total = _measure(blocks)
    if total <= THRESHOLD_CHARS:
        return None

    removed_start = HEAD_CHARS
    removed_end = total - TAIL_CHARS
    pruned: list[dict[str, Any]] = []
    consumed = 0
    marker_inserted = False

    for block in blocks:
        if block.get("type") != "text":
            pruned.append(block)
            continue
        text = block.get("text") or ""
        n = len(text)
        block_start = consumed
        block_end = block_start + n
        head_end = min(n, max(0, removed_start - block_start))
        tail_start = min(n, max(0, removed_end - block_start))
        intersects = block_start < removed_end and block_end > removed_start
        marker = PRUNE_MARKER if (intersects and not marker_inserted) else ""
        if marker:
            marker_inserted = True
        new_text = text[:head_end] + marker + text[tail_start:]
        if new_text:
            pruned.append({**block, "text": new_text})
        consumed = block_end

    if not marker_inserted:
        raise ValueError("tool-result prune: failed to locate the removed text span")
    after = _measure(pruned)
    if after > THRESHOLD_CHARS or after >= total:
        raise ValueError("tool-result prune: replacement must be smaller and within threshold")
    return pruned


def prune_session(log) -> dict[str, Any]:
    """对当前 surface 上所有超预算 tool/result 节点：compaction/prune + 替换。

    返回 {"pruned": [(原seq, 新seq, callId, charsBefore, charsAfter)], "charsRemoved": n}。
    每次替换保留完整事件数据、仅 content 变化、引用被遮蔽节点（回放可恢复输入），
    并紧邻前置一条 compaction/prune 影子定价事件。
    """
    from wagent_backend.ops.agent.events import EventLog

    entries: list[dict[str, Any]] = []
    chars_removed = 0
    for seq in list(log.surface_nodes):
        ev = log.events[seq]
        if ev["type"] != "tool/result":
            continue
        tb = ev["data"]["message"]["content"][0]
        content = tb.get("content") or []
        new_content = prune_content(content)
        if new_content is None:
            continue
        before, after = _measure(content), _measure(new_content)
        log.append("compaction/prune", {
            "shadowedRange": {"start": seq, "end": seq},
            "shadowedSeqs": [seq],
            "shadowedTokenCount": EventLog._msg_tokens(ev["data"]["message"]),
        })
        replacement = log.append("tool/result", {
            **ev["data"],
            "message": {**ev["data"]["message"],
                        "content": [{**tb, "content": new_content}]},
        }, surface_op={"op": "replace", "start": seq, "end": seq},
           source_event_seqs=[seq])
        entries.append({"originalSeq": seq, "replacementSeq": replacement["seq"],
                        "callId": ev["data"]["message"].get("source", {}).get("callId"),
                        "charsBefore": before, "charsAfter": after})
        chars_removed += before - after
    return {"pruned": entries, "charsRemoved": chars_removed}
