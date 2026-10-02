"""events —— 会话的追加型事件日志（dsh Session 的 Python 移植，L0+L1）。

铁律（与 dsh 相同）：**一切皆事件，消息列表是派生物**。
LLM 看到的 messages 由 surface 事件（user/message、assistant/message、
tool/result）投影而来；前端三栏回放消费同一份事件流 —— 没有第二套运行数据。

事件信封：{"seq", "type", "time", "data"} + 仅 surface 三类附加事件级
"surfaceOp"（"append" | {"op":"replace","start","end"}）与可选 "sourceEventSeqs"。
seq = len(events)（连续性契约，即行号）；data 在追加点做 JSON 快照（拷贝+校验）；
追加即发布（on_append 钩子，SSE 用）；持久化走写-behind writer（store.SessionWriter）。

事件词表（type → data）：
    session/start      {session_id, tier, as_of}
    turn/start         {turn}
    user/message       data 即完整消息 {id, role:"user", content:[{type:"text",text}],
                                          source:{kind:"user"}|{kind:"plugin",plugin:"format-nudge"|"compaction",…}}
    request/header     {header:{config:{model,provider}, system<全文>, tools[schemas]}, reason:initial|resume|change}
    request/context    {provider, model, contextWindow}（首次与变化时）
    assistant/chunk    {turn, step, chunk:<StreamChunk>}          # log-only，token 级回放保真
    assistant/message  {turn, step, message:{id, role:"assistant",
                        content:[text|reasoning|tool-call 块…按流序],
                        source:{kind:"model",provider,model}}, usage?}
    tool/call          {turn, step, callId, name, arguments<原始串>}   # log-only
    tool/result        {turn, step, message:<ToolResultMessage：role:"user"，
                        content 恰一个 tool-result 块{toolCallId,content,isError?}>,
                        meta:{name, digest, duration_ms}}
    decision           {turn, decision(Decision dump)}
    compaction/start   {compactionId, turn}
    compaction/summary {compactionId, summary[text 块], shadowedRange{start,end},
                        shadowedSeqs[], shadowedTokenCount, provider, model, maxTokens?, usage?}
    compaction/prune   {shadowedRange{start,end}, shadowedSeqs[], shadowedTokenCount}
    compaction/end     {compactionId, turn, error?}
    turn/end           {turn, reason: completed|awaiting_input|safety|policy_escalate|
                        step_limit|max_rounds|parse_failed|llm_error, needs?, location_hint?, detail?}
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from wagent_backend.ops.agent import projections, surface

SURFACE_TYPES = surface.SURFACE_TYPES


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _snapshot(data: dict[str, Any]) -> dict[str, Any]:
    """追加点 JSON 快照：拷贝一份进日志（调用方后续改动不影响日志），
    非 JSON 可序列化的值在追加点即抛（dsh snapshotJsonValue 的宽松版：default=str）。"""
    try:
        return json.loads(json.dumps(data, ensure_ascii=False, default=str))
    except (TypeError, ValueError) as e:
        raise ValueError(f"事件 data 必须可 JSON 序列化：{e}") from e


class EventLog:
    """内存事件列表 + surface 状态 + 写-behind 持久化。

    on_append：可选订阅者 callback(ev) —— 每条事件入日志后立即回调（追加即发布）。
    Web 流式接口用它把事件实时推给浏览器（dsh 的实时回放）。
    """

    def __init__(self, path=None):
        self.events: list[dict[str, Any]] = []
        self.surface_nodes: list[int] = []   # surface 事件 seq（模型可见顺序）
        self.replace_generation = 0          # 每次 replace +1（派生缓存失效水位）
        self.on_append: Callable[[dict[str, Any]], None] | None = None
        self.projections = projections.SessionProjections(self)   # L2 投影（meta 注册于默认表）
        self._path = path                    # 持久化目标（writer 绑定后生效）
        self._writer = None                  # store.SessionWriter（延迟绑定）
        # 派生缓存（dsh deriveMessages 的增量水位）
        self._derived: list[dict[str, Any]] = []
        self._derived_nodes = 0
        self._derived_generation = 0

    # ── 追加（append 即发布）──────────────────────────────

    def append(self, type_: str, data: dict[str, Any], *,
               surface_op: Any = None,
               source_event_seqs: list[int] | None = None) -> dict[str, Any]:
        ev: dict[str, Any] = {"seq": len(self.events), "type": type_,
                              "time": _now_iso(), "data": _snapshot(data)}
        if surface_op is not None:
            ev["surfaceOp"] = surface_op
        if source_event_seqs is not None:
            ev["sourceEventSeqs"] = source_event_seqs
        surface.validate_surface(ev, self.surface_nodes, self.events)  # push 前校验
        self.events.append(ev)
        self.surface_nodes, replaced = surface.apply_event(self.surface_nodes, ev)
        if replaced:
            self.replace_generation += 1
        if self._writer is not None:
            self._writer.append(ev)
        if self.on_append is not None:
            self.on_append(ev)
        self.projections.drive(ev)   # 事件已提交 → eager 过所有投影单元
        return ev

    # ── 派生：LLM 消息列表（surface 投影，dsh deriveMessages）──

    def derive_messages(self) -> list[dict[str, Any]]:
        """增量投影：缓存 + nodes 水位；replace（generation 变化）清缓存重建。"""
        if self._derived_generation != self.replace_generation:
            self._derived = []
            self._derived_nodes = 0
            self._derived_generation = self.replace_generation
        for seq in self.surface_nodes[self._derived_nodes:]:
            msg = surface.derive_event_message(self.events[seq])
            if msg is not None:
                self._derived.append(msg)
        self._derived_nodes = len(self.surface_nodes)
        return list(self._derived)

    # ── 度量（压缩/裁剪的压力测量）────────────────────────

    @staticmethod
    def _msg_tokens(msg: dict[str, Any]) -> int:
        chars = 0
        for b in msg.get("content") or []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool-result":   # 完整结果在嵌套 content 文本里
                chars += sum(len(t.get("text") or "")
                             for t in b.get("content") or [] if isinstance(t, dict))
            else:
                chars += len(b.get("text") or "") + len(b.get("arguments") or "")
        return chars // 2

    def token_estimate(self) -> int:
        """粗估 surface 字符量 / 2（演示口径：档位对比 context 成本用）。"""
        return sum(self._msg_tokens(m) for m in self.derive_messages())

    def measure_surface(self) -> list[tuple[int, int]]:
        """[(seq, est_tokens)]：surface 逐节点度量（select_compactable_range 用）。"""
        out: list[tuple[int, int]] = []
        for seq in self.surface_nodes:
            msg = surface.derive_event_message(self.events[seq])
            if msg is not None:
                out.append((seq, self._msg_tokens(msg)))
        return out

    # ── 持久化（L4，写-behind writer）─────────────────────

    def bind_writer(self, writer) -> None:
        self._writer = writer

    def flush(self) -> None:
        """持久化屏障：把写-behind 缓冲全部落盘（轮末/读取前调用）。"""
        if self._writer is not None:
            self._writer.flush()

    @classmethod
    def load(cls, path) -> "EventLog":
        from wagent_backend.ops.agent.store import load_events
        return load_events(path)

    # ── 会话元信息（L2 meta 投影的整值读取）───────────────

    @staticmethod
    def _user_text(ev: dict[str, Any]) -> str | None:
        d = ev["data"]
        if d.get("source", {}).get("kind") != "user":
            return None  # 插件消息（格式提醒/压缩 checkpoint）不算用户原文
        return "".join(b.get("text", "") for b in d.get("content") or []
                       if isinstance(b, dict))

    def meta(self) -> dict[str, Any]:
        return self.projections.snapshot()["meta"]
