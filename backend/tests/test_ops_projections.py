"""projections —— L2 投影注册表测试（dsh session-projection 契约）。"""

from __future__ import annotations

import pytest

from wagent_backend.ops.agent import projections
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.projections import (META_PROJECTION,
                                                  ProjectionDefinition,
                                                  SessionProjections)


def _u(text, source=None):
    return {"id": "u" + text[:2], "role": "user",
            "content": [{"type": "text", "text": text}],
            "source": source or {"kind": "user"}}


def _a(text):
    return {"id": "a1", "role": "assistant",
            "content": [{"type": "text", "text": text}],
            "source": {"kind": "model", "provider": "dashscope", "model": "qwen"}}


def _tr(call_id, text):
    return {"id": "t1", "role": "user",
            "content": [{"type": "tool-result", "toolCallId": call_id,
                         "content": [{"type": "text", "text": text}],
                         "isError": False}],
            "source": {"kind": "tool", "callId": call_id}}


# ── meta 投影：折叠 ≡ 旧全量扫描 ──────────────────────────

def test_meta_projection_matches_full_scan():
    log = EventLog()
    log.append("session/start", {"session_id": "S-1", "tier": "full",
                                 "as_of": "2026-08-23T10:00:00"})
    log.append("turn/start", {"turn": 1})
    u1 = log.append("user/message", _u("A座25楼东侧空调又不制冷了" * 30),
                    surface_op="append")
    a1 = log.append("assistant/message", {"message": _a("先查历史" * 50)},
                    surface_op="append")
    log.append("turn/start", {"turn": 2})
    # 插件消息（格式提醒）不算用户原文
    log.append("user/message", _u("（格式提醒）请输出合法 JSON",
                                  {"kind": "plugin", "plugin": "format-nudge"}),
               surface_op="append")
    u2 = log.append("user/message", _u("麻烦尽快处理" * 10), surface_op="append")
    log.append("decision", {"turn": 2, "decision": {"space_id": "sp-1"}})

    m = log.meta()
    assert m == {"session_id": "S-1", "tier": "full", "as_of": "2026-08-23T10:00:00",
                 "started_at": log.events[0]["time"], "turns": 2,
                 "last_text": "麻烦尽快处理" * 10,
                 "last_decision": {"space_id": "sp-1"},
                 "tokens": log.token_estimate()}

    # replace 型 surface 事件（压缩 checkpoint）→ 节点账本同步：tokens 仍与
    # derive_messages 的口径一致；日志级 last_text 不受影响（原事件永留日志）
    before = log.token_estimate()
    shadowed = [u1["seq"], a1["seq"]]
    log.append("user/message", _u("checkpoint 摘要", {"kind": "plugin",
                                                     "plugin": "compaction"}),
               surface_op={"op": "replace", "start": shadowed[0], "end": shadowed[1]},
               source_event_seqs=[shadowed[0], shadowed[1]])
    m2 = log.meta()
    assert m2["tokens"] == log.token_estimate() < before   # 账本跟着 splice 走
    assert m2["last_text"] == "麻烦尽快处理" * 10           # 遮蔽不改变日志级语义
    assert m2["turns"] == 2 and m2["last_decision"] == {"space_id": "sp-1"}


def test_meta_projection_tracks_tool_result_replace():
    """pruner 的 content-only replace：单节点换单节点，tokens 跟着变小。"""
    log = EventLog()
    call = log.append("tool/call", {"turn": 1, "step": 1, "callId": "c1",
                                    "name": "get_assets_serving_space",
                                    "arguments": "{}"})
    tr = log.append("tool/result", {"turn": 1, "step": 1,
                                    "message": _tr("c1", "Z" * 10000),
                                    "meta": {"name": "get_assets_serving_space",
                                             "digest": "…", "duration_ms": 1}},
                    surface_op="append", source_event_seqs=[call["seq"]])
    assert log.meta()["tokens"] == log.token_estimate()
    log.append("tool/result", {"turn": 1, "step": 1,
                               "message": _tr("c1", "head [...裁剪...] tail"),
                               "meta": {"name": "get_assets_serving_space",
                                        "digest": "…", "duration_ms": 1}},
               surface_op={"op": "replace", "start": tr["seq"], "end": tr["seq"]},
               source_event_seqs=[tr["seq"]])
    assert log.meta()["tokens"] == log.token_estimate()


# ── 注册表契约：同引用零通知 / 整值 / 水位 ────────────────

def test_same_reference_zero_notification_and_whole_value():
    log = EventLog()
    log.append("session/start", {"session_id": "S-1", "tier": "full", "as_of": None})
    calls: list[tuple[str, dict, int]] = []
    log.projections.on_changed(lambda key, value, seq: calls.append((key, value, seq)))
    # 不感兴趣的事件（chunk）：apply 返回同一 state 对象 → 零通知
    for i in range(3):
        log.append("assistant/chunk", {"turn": 1, "step": 1,
                                       "chunk": {"type": "text-delta", "index": 0,
                                                 "text": "x"}})
    assert calls == []
    ev = log.append("user/message", _u("报修"), surface_op="append")
    assert len(calls) == 1
    key, value, seq = calls[0]
    assert key == "meta"
    assert value == log.projections.snapshot()["meta"]   # 整值（非增量）
    assert seq == ev["seq"]
    assert "报修" in value["last_text"]


def test_late_register_folds_full_log():
    """晚注册的单元从 init 惰性折全量日志（dsh cellFor lazy build）。"""
    log = EventLog()
    log.append("turn/start", {"turn": 1})
    log.append("user/message", _u("第一句"), surface_op="append")
    log.append("turn/start", {"turn": 2})
    log.append("user/message", _u("第二句"), surface_op="append")

    def _counter_apply(s, ev):
        t = ev["type"]
        if t == "user/message":
            return {**s, "users": s["users"] + 1}
        if t == "turn/start":
            return {**s, "turns": s["turns"] + 1}
        return s   # 不感兴趣：同对象返回

    counter = ProjectionDefinition(
        key="counter", init=lambda: {"users": 0, "turns": 0},
        apply=_counter_apply,
        view=lambda s: {"users": s["users"], "turns": s["turns"]})
    log.projections.register(counter)
    assert log.projections.snapshot()["counter"] == {"users": 2, "turns": 2}
    # 注册后继续追加：增量驱动接力
    log.append("turn/start", {"turn": 3})
    assert log.projections.snapshot()["counter"] == {"users": 2, "turns": 3}


def test_register_version_conflict_refs_and_disposer():
    reg = SessionProjections(definitions=())
    d1 = reg.register(META_PROJECTION)
    d2 = reg.register(META_PROJECTION)   # 同版本重复注册：引用计数
    assert "meta" in reg.snapshot()
    # 版本冲突：拒绝共享 cell
    conflict = ProjectionDefinition(key="meta", init=lambda: {}, apply=lambda s, e: s,
                                    view=lambda s: {}, state_version=2)
    with pytest.raises(ValueError, match="state_version"):
        reg.register(conflict)
    with pytest.raises(ValueError, match="非负整数"):
        reg.register(ProjectionDefinition(key="bad", init=lambda: {}, apply=lambda s, e: s,
                                          view=lambda s: {}, state_version=-1))
    d1()
    assert "meta" in reg.snapshot()      # 还剩一个注册者 → key 保留
    d2()
    assert reg.snapshot() == {}          # 最后一个退出 → key 从切面消失


def test_snapshot_catches_up_bypassed_events():
    """store.load_events 直接填 events（不经 append）→ 读取点惰性补折。"""
    log = EventLog()
    log.events.append({"seq": 0, "type": "session/start", "time": "2026-08-23T10:00:00.000Z",
                       "data": {"session_id": "S-9", "tier": "lite",
                                "as_of": "2026-08-23T10:00:00"}})
    log.events.append({"seq": 1, "type": "turn/start", "time": "t1", "data": {"turn": 1}})
    log.events.append({"seq": 2, "type": "user/message", "time": "t2",
                       "data": _u("载入路径"), "surfaceOp": "append"})
    log.surface_nodes = [2]
    m = log.meta()
    assert m["session_id"] == "S-9" and m["turns"] == 1
    assert m["last_text"] == "载入路径"
    assert m["started_at"] == "2026-08-23T10:00:00.000Z"
    # 载入后继续追加：drive 先补水位缺口再进门
    log.append("turn/start", {"turn": 2})
    assert log.meta()["turns"] == 2


def test_projection_module_doc_rules():
    """三条铁律有出处：整值/同引用/惰性建账。"""
    assert projections.ProjectionDefinition is ProjectionDefinition
    assert META_PROJECTION.key == "meta" and META_PROJECTION.state_version == 1
    # 不感兴趣事件：apply 返回同一对象（首事件要落 started_at，先跨过去）
    s0 = META_PROJECTION.apply(META_PROJECTION.init(),
                               {"type": "session/start", "time": "t", "data": {}})
    assert META_PROJECTION.apply(s0, {"type": "assistant/chunk", "time": "t",
                                      "data": {}}) is s0
