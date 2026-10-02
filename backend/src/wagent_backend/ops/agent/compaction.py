"""compaction —— L3 会话压缩（dsh compaction-basic 的 Python 移植）。

压力触发（估算 ≥ 0.8×上下文窗口）→ 先跑 pruner（模型无关）→ 复测仍超 →
把头锚定区段（保留尾部 0.16×窗口原文）交给**同一个流式模型**摘要成
英文八段 checkpoint → 用 4 条事件原子落日志（start/summary/替换/end）。

铁律（与 dsh 相同）：
  * 工具配对不切分 —— assistant 的 tool-call 块与其 tool/result 必须同进退；
  * must-be-smaller —— framed 摘要估算必须严格小于被遮蔽内容，否则抛错；
  * fail-closed —— 摘要失败（error/max-tokens/空文本）记 compaction/end.error
    并向上抛，绝不落一个坏 checkpoint；
  * 日志永不改写 —— 替换是 user/message(replace) 遮蔽旧节点，原文永在。

环境开关：WAGENT_COMPACTION=1（默认开）；WAGENT_CONTEXT_WINDOW=32768
（演示可调小触发压缩）。
"""

from __future__ import annotations

import os
import re
import uuid
from typing import Any

from wagent_backend.llm import client
from wagent_backend.llm.assembler import BlockAssembler, text_of
from wagent_backend.ops.agent import pruner, surface
from wagent_backend.ops.agent.events import EventLog

# ── 配置（dsh compaction-basic 默认值）───────────────────
_THRESHOLD_RATIO = 0.8   # 压力阈值 = 0.8 × 窗口
_RETAIN_RATIO = 0.16     # 尾部原文保留 = 0.16 × 窗口
_MAX_TOKENS = 8192       # 摘要调用 max_tokens
_RETRIES = 1             # 阈值未降到以下的重试次数（共 _RETRIES+1 次尝试）


def context_window() -> int:
    """上下文窗口（token）——request/context 与压缩压力共用；演示可调小。"""
    try:
        return int(os.environ.get("WAGENT_CONTEXT_WINDOW", "32768"))
    except ValueError:
        return 32768


def enabled() -> bool:
    return os.environ.get("WAGENT_COMPACTION", "1") == "1"


# ── 摘要指令（dsh summarizer.ts 逐字英文）────────────────
SUMMARY_OPEN_TAG = "<compacted-summary>"
SUMMARY_CLOSE_TAG = "</compacted-summary>"

COMPACTION_INSTRUCTION = "\n".join([
    "You are now acting as a compaction engine for this AI coding assistant. Condense the conversation ABOVE into a structured checkpoint that lets another model resume the work with no loss of essential context.",
    "",
    "Output EXACTLY the Markdown structure below: keep every section, in order. Use terse bullets, not prose paragraphs. Write \"(none)\" for an empty section — never drop a section.",
    "",
    "## Primary Request and Intent",
    "- [the user's original and evolving goals; quote verbatim where the exact wording matters]",
    "",
    "## Key Technical Concepts",
    "- [technologies, frameworks, patterns, and conventions in play]",
    "",
    "## Files and Code",
    "- [exact path: why it matters, key changes or snippets]",
    "",
    "## Errors and Fixes",
    "- [error: how it was resolved, plus any related user feedback]",
    "",
    "## Pending Jobs",
    "- [explicitly requested work not yet completed]",
    "",
    "## Current Work",
    "- [precisely what was in progress at this checkpoint]",
    "",
    "## Next Step",
    "- [the single next action, directly in line with the most recent request, or \"(none)\"]",
    "",
    "## Critical Context",
    "- [decisions and their rationale, constraints, user preferences, open questions, data needed to continue]",
    "",
    "Rules:",
    "- Write concise English engineering prose. Preserve exact file paths, commands, error strings, identifiers, numeric values, function signatures, and syntax fragments.",
    "- Capture user feedback and explicit instructions faithfully, especially corrections.",
    "- Do NOT mention this summarization request or that the context was compacted.",
    "- Output only the checkpoint text: do not call any tool or take any other action.",
    f"- If the conversation already contains a {SUMMARY_OPEN_TAG} block, it is a PRIOR checkpoint. Do not copy it forward verbatim: preserve still-true facts, drop stale ones, and merge newer information into a single consolidated summary under the same structure.",
])

CHECKPOINT_PREAMBLE = (
    "This is an automatically generated checkpoint condensing an earlier span of the "
    "conversation to free up context. Treat the captured context as established "
    "background and build on it without restating it. Continue the task directly from "
    "the messages that follow, without acknowledging this checkpoint."
)


# ── 工具配对平衡（dsh tool-pairing.ts 的裁点判定）────────

def _balance_cuts(log: EventLog) -> list[bool]:
    """每个裁点是否「无未应答的 tool-call 跨过」。

    surface 节点序折叠：assistant 的 tool-call 块开 N 个配对、tool/result 应答
    一个。cuts[i] = 前 i 个节点处理完后 pending==0（i=0 恒真）。
    """
    pending = 0
    cuts = [True]
    for seq in log.surface_nodes:
        ev = log.events[seq]
        msg = ev["data"] if ev["type"] == "user/message" else ev["data"].get("message") or {}
        if ev["type"] == "assistant/message":
            pending += sum(1 for b in msg.get("content") or []
                           if b.get("type") == "tool-call")
        elif ev["type"] == "tool/result":
            pending = max(0, pending - 1)
        cuts.append(pending == 0)
    return cuts


def _balanced_before(log: EventLog, seq: int) -> bool:
    return _balance_cuts(log)[log.surface_nodes.index(seq)]


def _balanced_after(log: EventLog, seq: int) -> bool:
    return _balance_cuts(log)[log.surface_nodes.index(seq) + 1]


# ── 区段选择（dsh selectCompactableRange）────────────────

def select_compactable_range(log: EventLog, retain_tokens: int) -> dict[str, int] | None:
    """从尾向前累计 retain_tokens 得保留起点 keep，向左退到配对平衡边界，
    返回头锚定区间 {start: nodes[0], end: nodes[keep-1]}；无可压缩返回 None。"""
    priced = log.measure_surface()
    if not priced:
        return None
    nodes = log.surface_nodes
    accumulated = 0
    keep = len(priced)
    for i in range(len(priced) - 1, -1, -1):
        accumulated += priced[i][1]
        keep = i
        if accumulated >= retain_tokens:
            break
    if keep == 0:
        return None
    cuts = _balance_cuts(log)
    while keep > 0 and not cuts[keep]:
        keep -= 1
    if keep == 0:
        return None
    return {"start": nodes[0], "end": nodes[keep - 1]}


# ── 摘要（dsh summarizeWithLlm：复用同一 stream，fail-closed）──

def summarize(stream, system: str, tools: list[dict], region_messages: list[dict]) -> dict:
    """复放被遮蔽区段（前缀= system + 工具清单，KV 缓存对齐）+ 尾部压缩指令。

    只投影文本块（dsh summaryText）；error/max-tokens/空文本 → 抛错（fail-closed）。
    """
    instruction = {"id": uuid.uuid4().hex, "role": "user",
                   "content": [{"type": "text", "text": COMPACTION_INSTRUCTION}],
                   "source": {"kind": "plugin", "plugin": "compaction"}}
    messages = [{"role": "system", "content": system}, *region_messages, instruction]
    asm = BlockAssembler()
    for chunk in stream(messages, tools, max_tokens=_MAX_TOKENS, thinking=False):
        asm.push(chunk)
    finish = asm.finish
    if finish.get("kind") == "error":
        failure = finish.get("failure") or {}
        raise client.LLMError(failure.get("message") or "summarization error",
                              failure.get("code") or "LLM_ERROR")
    if finish.get("kind") == "max-tokens":
        raise client.LLMError("summarization truncated at the token cap (incomplete checkpoint)",
                              "MAX_TOKENS")
    summary_text = text_of(asm.blocks()).strip()
    if not summary_text:
        raise client.LLMError("summarization produced no text summary content", "EMPTY_SUMMARY")
    return {"summaryText": summary_text,
            "provider": client.provider_name(), "model": client.model_name(),
            "maxTokens": _MAX_TOKENS, "usage": asm.usage}


def frame_summary(summary_text: str) -> list[dict[str, Any]]:
    """dsh frameSummary：PREAMBLE + 开标签 / 摘要 / 闭标签 三个文本块。"""
    return [{"type": "text", "text": f"{CHECKPOINT_PREAMBLE}\n\n{SUMMARY_OPEN_TAG}"},
            {"type": "text", "text": summary_text},
            {"type": "text", "text": SUMMARY_CLOSE_TAG}]


# ── 压缩事务（dsh compactSurfaceRegion：恰好 4 条事件）─────

def compact_region(stream, log: EventLog, start: int, end: int, *, turn: int,
                   system: str, tools: list[dict]) -> dict[str, Any]:
    """把 surface 区段 [start, end]（inclusive）摘要为一个 checkpoint 替换节点。

    成功恰好 4 条事件：compaction/start → compaction/summary →
    user/message(replace, plugin=compaction) → compaction/end。
    任何失败：恰好补一条 compaction/end(error) 后抛出（fail-closed）。
    """
    nodes = log.surface_nodes
    si, ei = nodes.index(start), nodes.index(end)
    shadowed = nodes[si:ei + 1]
    if not _balanced_before(log, start):
        raise ValueError(f"compactRegion: start seq {start} 不是配对平衡边界（会切开 tool-call/result 对）")
    if not _balanced_after(log, end):
        raise ValueError(f"compactRegion: end seq {end} 不是配对平衡边界（步骤尚未闭合）")

    region_messages = [m for m in (surface.derive_event_message(log.events[s])
                                   for s in shadowed) if m is not None]
    shadowed_tokens = sum(t for _, t in log.measure_surface()[si:ei + 1])
    compaction_id = uuid.uuid4().hex
    start_ev = log.append("compaction/start", {"compactionId": compaction_id, "turn": turn})
    try:
        result = summarize(stream, system, tools, region_messages)
        checkpoint = frame_summary(result["summaryText"])
        framed_tokens = EventLog._msg_tokens({"content": checkpoint})
        if framed_tokens >= shadowed_tokens:
            raise ValueError(
                f"summary is not smaller than the shadowed content "
                f"({framed_tokens} estimated framed tokens >= {shadowed_tokens})")
        summary_ev = log.append("compaction/summary", {
            "compactionId": compaction_id,
            "summary": [{"type": "text", "text": result["summaryText"]}],
            "shadowedRange": {"start": start, "end": end},
            "shadowedSeqs": shadowed,
            "shadowedTokenCount": shadowed_tokens,
            "provider": result["provider"], "model": result["model"],
            "maxTokens": result["maxTokens"], "usage": result["usage"],
        })
        log.append("user/message", {
            "id": uuid.uuid4().hex, "role": "user", "content": checkpoint,
            "source": {"kind": "plugin", "plugin": "compaction", "compactionId": compaction_id},
        }, surface_op={"op": "replace", "start": start, "end": end},
           source_event_seqs=[start_ev["seq"], summary_ev["seq"], *shadowed])
    except Exception as e:
        log.append("compaction/end", {"compactionId": compaction_id, "turn": turn,
                                      "error": f"{type(e).__name__}: {e}"})
        raise
    log.append("compaction/end", {"compactionId": compaction_id, "turn": turn})
    return {"compactionId": compaction_id, "startSeq": start_ev["seq"],
            "summarySeq": summary_ev["seq"],
            "shadowedRange": {"start": start, "end": end}, "shadowedSeqs": shadowed,
            "shadowedTokenCount": shadowed_tokens}


# ── 自动门闩（dsh compactIfNeeded：pressure / context-overflow）──

def compact_if_needed(stream, log: EventLog, system: str, tools: list[dict], *,
                      turn: int, trigger: str = "pressure") -> dict[str, Any] | None:
    """步间压力检查（pressure：低于阈值 noop）或溢出强制压缩（overflow：绕过阈值）。

    pressure：先跑模型无关的 pruner，复测仍超阈值才摘要；重试 _RETRIES+1 次
    仍超 → 抛错（调用方继续本轮，事件已留痕）。
    """
    if not enabled():
        return None
    window = context_window()
    threshold = int(window * _THRESHOLD_RATIO)
    retain = int(window * _RETAIN_RATIO)

    if trigger == "context-overflow":
        pruner.prune_session(log)
        rng = select_compactable_range(log, 0)   # 保留 0：强制一次有用的缩减
        if rng is None:
            return None
        return compact_region(stream, log, rng["start"], rng["end"],
                              turn=turn, system=system, tools=tools)

    if log.token_estimate() < threshold:
        return None
    pruner.prune_session(log)
    if log.token_estimate() < threshold:
        return None
    result: dict[str, Any] | None = None
    for _attempt in range(_RETRIES + 1):
        rng = select_compactable_range(log, retain)
        if rng is None:
            return result
        result = compact_region(stream, log, rng["start"], rng["end"],
                                turn=turn, system=system, tools=tools)
        if log.token_estimate() < threshold:
            return result
    total = log.token_estimate()
    raise RuntimeError(
        f"compaction still above threshold after {_RETRIES + 1} compaction attempts "
        f"({total} estimated tokens >= threshold {threshold})")


# ── 溢出识别（dsh isContextWindowExceededError 的子集）────

_CONTEXT_OVERFLOW_RE = re.compile(
    r"context_length_exceeded"
    r"|\bmaximum context (?:length|window)\b"
    r"|\b(?:input|prompt|request|messages?)\b.{0,40}"
    r"\b(?:exceed(?:s|ed)?|overflows?|is\s+larger\s+than)\b.{0,40}\bcontext\b"
    r"|\btoo\s+(?:large|long)\s+for\s+(?:(?:this|the)\s+)?model",
    re.IGNORECASE,
)


def is_context_overflow(exc: BaseException) -> bool:
    """上游报「请求超出上下文窗口」措辞的识别（OpenAI 兼容系常见文案）。"""
    return bool(_CONTEXT_OVERFLOW_RE.search(str(exc)))
