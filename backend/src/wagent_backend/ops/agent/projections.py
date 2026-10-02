"""projections —— L2 投影（dsh session-projection 的 Python 移植）。

ProjectionDefinition：一个领域的状态驱动计算单元 —— key / init / apply /
view / state_version，全部是纯同步函数；state 必须是纯 JSON（持久化缓存
的前提）。域只出数学（init/apply/view），框架（SessionProjections）负责
驱动、水位 cell 与变更通知——两侧互不相识。

铁律（与 dsh 相同）：
  * 整值规则：apply 收完整事件，view 输出**整值** wire payload（不是增量）；
  * 同引用 = 零通知：单元对事件不感兴趣必须返回**同一个** state 对象
    （dsh Object.is 门 → Python 的 is），引用未变就不通知下游；
  * 惰性建账：cell 带水位（observedSeq），落后时（载入的日志未经 append
    直接填 events）在驱动/读取点补折全量（dsh cellFor 的 lazy build）。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from wagent_backend.ops.agent import surface


@dataclass(frozen=True)
class ProjectionDefinition:
    """dsh ProjectionDefinition：三个纯函数 + 声明，绝不藏一个不透明 getter。"""

    key: str
    init: Callable[[], Any]
    apply: Callable[[Any, dict[str, Any]], Any]   # (state, event) -> state；同引用=零通知
    view: Callable[[Any], dict[str, Any]]         # state -> 整值读取面
    state_version: int = 1                        # 缓存失效版本（state 形状/折叠语义变了要 bump）


# ── meta 投影（替代旧 meta() 全量扫描；view 字段名不变）────────

def _meta_init() -> dict[str, Any]:
    return {"session": None,     # session/start data
            "started_at": None,  # 首事件时间
            "turns": 0, "last_turn": None,
            "last_text": "",     # 最后一条用户原文（插件消息不算）
            "last_decision": None,
            "tokens": 0,         # surface 估算和（节点账本同步维护）
            "nodes": [],         # surface 节点 seq（镜像 surface.apply_event）
            "prices": {}}        # seq(str) -> 估算 token


def _fold_nodes(state: dict[str, Any], ev: dict[str, Any]) -> tuple[list, dict, int] | None:
    """镜像 surface.apply_event 的节点账本，同步维护 tokens。
    返回 (nodes, prices, tokens) 新三元组；非 surface 事件返回 None。"""
    from wagent_backend.ops.agent.events import EventLog

    op = ev.get("surfaceOp")
    if op is None:
        return None
    msg = surface.derive_event_message(ev)
    price = EventLog._msg_tokens(msg) if msg is not None else 0
    nodes, prices, tokens = state["nodes"], state["prices"], state["tokens"]
    if op == "append":
        return ([*nodes, ev["seq"]], {**prices, str(ev["seq"]): price},
                tokens + price)
    i, j = nodes.index(op["start"]), nodes.index(op["end"])   # validate_surface 已保证在位
    removed = nodes[i:j + 1]
    np_ = {**prices}
    for s in removed:
        np_.pop(str(s), None)
    np_[str(ev["seq"])] = price
    return ([*nodes[:i], ev["seq"], *nodes[j + 1:]], np_,
            tokens - sum(prices.get(str(s), 0) for s in removed) + price)


def _meta_apply(state: dict[str, Any], ev: dict[str, Any]) -> dict[str, Any]:
    t = ev["type"]
    nxt, changed = state, False
    if nxt["started_at"] is None:
        nxt = {**nxt, "started_at": ev.get("time")}
        changed = True
    if t == "session/start":
        nxt = {**nxt, "session": ev["data"]}
        changed = True
    elif t == "turn/start":
        turn = ev["data"].get("turn")
        if turn != nxt["last_turn"]:   # 轮号宿主分配且单调 → 槽位法计不重复轮数
            nxt = {**nxt, "turns": nxt["turns"] + 1, "last_turn": turn}
            changed = True
    elif t == "user/message":
        d = ev["data"]
        if d.get("source", {}).get("kind") == "user":   # 插件消息（提醒/checkpoint）不算用户原文
            text = "".join(b.get("text", "") for b in d.get("content") or []
                           if isinstance(b, dict))
            nxt = {**nxt, "last_text": text}
            changed = True
    elif t == "decision":
        nxt = {**nxt, "last_decision": ev["data"].get("decision")}
        changed = True
    folded = _fold_nodes(nxt, ev)
    if folded is not None:
        nxt = {**nxt, "nodes": folded[0], "prices": folded[1], "tokens": folded[2]}
        changed = True
    return nxt if changed else state   # 不感兴趣：原对象原样返回（同引用=零通知）


def _meta_view(state: dict[str, Any]) -> dict[str, Any]:
    s = state["session"] or {}
    return {"session_id": s.get("session_id"), "tier": s.get("tier"),
            "as_of": s.get("as_of"), "started_at": state["started_at"],
            "turns": state["turns"], "last_text": state["last_text"],
            "last_decision": state["last_decision"], "tokens": state["tokens"]}


META_PROJECTION = ProjectionDefinition(
    key="meta", init=_meta_init, apply=_meta_apply, view=_meta_view, state_version=1)


# ── 注册表 + 驱动（dsh ctx.sessionProjections 的单会话版）────────

ChangeListener = Callable[[str, dict[str, Any], int], None]   # (key, view 整值, seq)


class SessionProjections:
    """一个 EventLog 上的一致投影切面。

    drive：一条已提交事件过所有单元 —— 先补折水位缺口，再 apply + 引用比较，
    引用变了才带整值 view 通知监听器（seq=引发变更的事件）。
    snapshot：整值读取切面；落后 cell 惰性补折到日志尾。
    """

    def __init__(self, log: Any = None,
                 definitions: tuple[ProjectionDefinition, ...] = (META_PROJECTION,)):
        self._log = log
        self._defs: dict[str, ProjectionDefinition] = {}
        self._cells: dict[str, dict[str, Any]] = {}   # key -> {"state", "seq": 水位}
        self._refs: dict[str, int] = {}               # 共享同一单元的注册者数（dsh refs）
        self._listeners: list[ChangeListener] = []
        for d in definitions:
            self.register(d)

    def register(self, definition: ProjectionDefinition) -> Callable[[], None]:
        """注册单元（可晚注册：cell 从 init 惰性折全量日志）。返回注销器。

        同 key 同版本重复注册 → 引用计数 +1（最后一个注销者才移除 key）；
        同 key 不同版本 → 拒绝（缓存契约说 state 形状不同，不能共享 cell）。
        """
        if not isinstance(definition.state_version, int) or definition.state_version < 0:
            raise ValueError(f"投影 {definition.key} 的 state_version 必须是非负整数")
        key = definition.key
        existing = self._defs.get(key)
        if existing is None:
            self._defs[key] = definition
            self._cells[key] = {"state": definition.init(), "seq": -1}
            self._refs[key] = 0
        elif existing.state_version != definition.state_version:
            raise ValueError(f"投影 {key} 已注册于 state_version "
                             f"{existing.state_version}，拒绝 {definition.state_version}")
        self._refs[key] += 1

        def _dispose() -> None:
            if key not in self._refs:
                return
            self._refs[key] -= 1
            if self._refs[key] <= 0:   # 最后一个注册者退出 → key 从切面消失
                self._refs.pop(key, None)
                self._defs.pop(key, None)
                self._cells.pop(key, None)
        return _dispose

    def on_changed(self, listener: ChangeListener) -> Callable[[], None]:
        self._listeners.append(listener)

        def _dispose() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)
        return _dispose

    def _fold_to(self, key: str, last_seq: int) -> None:
        """cell 补折到 events[last_seq]（含）；历史前缀静默，不通知（dsh buildCell）。"""
        cell, d = self._cells[key], self._defs[key]
        state = cell["state"]
        for ev in self._log.events[cell["seq"] + 1: last_seq + 1]:
            state = d.apply(state, ev)
        cell["state"], cell["seq"] = state, last_seq

    def drive(self, ev: dict[str, Any]) -> None:
        """一条已提交事件过所有单元（EventLog.append 追加即驱动）。"""
        for key, d in list(self._defs.items()):
            cell = self._cells[key]
            if cell["seq"] < ev["seq"] - 1:
                self._fold_to(key, ev["seq"] - 1)   # 载入日志的迟到建账：先折历史再进门
            nxt = d.apply(cell["state"], ev)
            changed = nxt is not cell["state"]      # 同引用 = 零通知
            cell["state"], cell["seq"] = nxt, ev["seq"]
            if changed and self._listeners:
                value = d.view(nxt)
                for fn in list(self._listeners):
                    fn(key, value, ev["seq"])

    def snapshot(self) -> dict[str, Any]:
        """整值读取：每个 key 一个整值 view（落后 cell 惰性补折到日志尾）。"""
        if self._log is not None:
            last = len(self._log.events) - 1
            for key in self._defs:
                if self._cells[key]["seq"] < last:
                    self._fold_to(key, last)
        return {key: d.view(self._cells[key]["state"])
                for key, d in self._defs.items()}
