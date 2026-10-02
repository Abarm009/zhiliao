"""surface —— L1 模型可见面（dsh core/session/src/surface.ts 的 Python 移植）。

只有三类事件进入模型历史（surface 事件）：
    user/message | assistant/message | tool/result
它们**必须**携带事件级 surfaceOp 标记（"append" 或 {"op":"replace","start","end"}），
其余类型携带即抛错——标记与事件类型互斥是结构不变量，靠 append 点校验保证。

surface 状态 = nodes（surface 事件 seq，按模型可见顺序）+ replace_generation
（每次 replace +1，用作派生缓存的失效水位）。日志永不改写：
压缩/裁剪用 replace 型新事件**遮蔽**旧节点，而不是删除它们。
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SURFACE_TYPES = frozenset({"user/message", "assistant/message", "tool/result"})


def derive_event_message(ev: dict[str, Any]) -> dict[str, Any] | None:
    """surface 事件 → 模型消息；非 surface 事件（边界/chunk/留痕）投影为 None。

    user/message → data 本身（data 即完整消息，不再包一层）；
    assistant/message → data["message"]（空 content 只承载 usage，不入历史）；
    tool/result → data["message"]。
    """
    t = ev["type"]
    if t == "user/message":
        return ev["data"]
    if t == "assistant/message":
        msg = ev["data"].get("message")
        if msg is not None and not msg.get("content"):
            return None
        return msg
    if t == "tool/result":
        return ev["data"].get("message")
    return None


def _is_replace_op(op: Any) -> bool:
    return (isinstance(op, dict) and set(op) == {"op", "start", "end"}
            and op["op"] == "replace"
            and isinstance(op["start"], int) and isinstance(op["end"], int)
            and op["start"] >= 0 and op["end"] >= 0)


def validate_surface(ev: dict[str, Any], nodes: list[int],
                     events: list[dict[str, Any]]) -> None:
    """append 点校验（dsh surfaceOpOf / assertProvenance / assertToolResultRewrite）。

    ev 尚未入列表：seq 已定，sourceEventSeqs 只能引用更早的事件。
    """
    t = ev["type"]
    op = ev.get("surfaceOp")
    srcs = ev.get("sourceEventSeqs")

    # 1) 标记与类型互斥
    if t not in SURFACE_TYPES:
        if op is not None or srcs is not None:
            raise ValueError(f"session 事件 {t} 不是 surface 类型，不能携带 surfaceOp/sourceEventSeqs")
        return
    if op is None:
        raise ValueError(f"session 事件 {t} 是 surface 类型，必须携带 surfaceOp 标记")
    if op != "append" and not _is_replace_op(op):
        raise ValueError(f"非法 surfaceOp：{op!r}")

    # 2) 溯源：非负、不重复、全部指向更早事件
    if srcs is not None:
        if (not isinstance(srcs, list)
                or any(not isinstance(s, int) or s < 0 for s in srcs)
                or len(set(srcs)) != len(srcs)):
            raise ValueError(f"sourceEventSeqs 必须是不重复的非负整数列表：{srcs!r}")
        seq = ev["seq"]
        if any(s >= seq for s in srcs):
            raise ValueError(f"sourceEventSeqs 只能引用更早的事件：{srcs!r} vs seq={seq}")

    # 3) replace：start/end 必须都在当前 nodes 中（start 位 ≤ end 位），
    #    且 sourceEventSeqs 必须覆盖全部被遮蔽节点
    if _is_replace_op(op):
        start, end = op["start"], op["end"]
        try:
            i, j = nodes.index(start), nodes.index(end)
        except ValueError as e:
            raise ValueError(f"replace 的 start/end 必须是当前 surface 节点：{start}/{end}") from e
        if i > j:
            raise ValueError(f"replace 区间非法：start {start} 在 end {end} 之后")
        shadowed = nodes[i:j + 1]
        if srcs is None or not set(shadowed) <= set(srcs):
            raise ValueError(f"sourceEventSeqs 必须覆盖全部被遮蔽节点 {shadowed}")
        # tool/result 的 replace 只允许「改写单个在位 tool/result 且仅内容变化」
        if t == "tool/result":
            if len(shadowed) != 1:
                raise ValueError("tool/result 的 surface 替换只能改写单个节点")
            old = events[shadowed[0]]
            if old["type"] != "tool/result":
                raise ValueError("tool/result 的 surface 替换目标不是 tool/result")
            _assert_content_only(old["data"], ev["data"])


def _assert_content_only(old_data: dict[str, Any], new_data: dict[str, Any]) -> None:
    """除 tool-result 块的内层 content 外必须全等（dsh assertToolResultRewrite）。"""
    a, b = deepcopy(old_data), deepcopy(new_data)
    for d in (a, b):
        try:
            d["message"]["content"][0]["content"] = None
        except (KeyError, IndexError, TypeError):
            pass
    if a != b:
        raise ValueError("tool/result 替换只允许改写 message.content[0].content")


def apply_event(nodes: list[int], ev: dict[str, Any]) -> tuple[list[int], bool]:
    """fold surface 状态；返回 (新 nodes, 是否 replace)。

    append → 尾部 push；replace → splice 掉 inclusive [start,end] 段并原地插入新 seq。
    """
    if ev["type"] not in SURFACE_TYPES:
        return nodes, False
    op = ev["surfaceOp"]
    seq = ev["seq"]
    if op == "append":
        return [*nodes, seq], False
    i, j = nodes.index(op["start"]), nodes.index(op["end"])
    return [*nodes[:i], seq, *nodes[j + 1:]], True
