"""surface —— L1 校验与 fold 的守卫测试（dsh surface.py 移植的契约）。"""

import pytest

from wagent_backend.ops.agent.events import EventLog


def _u(text):
    return {"id": "u1", "role": "user", "content": [{"type": "text", "text": text}],
            "source": {"kind": "user"}}


def _a(text):
    return {"id": "a1", "role": "assistant",
            "content": [{"type": "text", "text": text}],
            "source": {"kind": "model", "provider": "dashscope", "model": "qwen"}}


def test_surface_op_mandatory_and_forbidden():
    log = EventLog()
    # surface 类型缺 surfaceOp → 抛
    with pytest.raises(ValueError, match="surfaceOp"):
        log.append("user/message", _u("hi"))
    # 非 surface 类型携带 → 抛
    with pytest.raises(ValueError, match="不是 surface 类型"):
        log.append("assistant/chunk", {"chunk": {}}, surface_op="append")
    with pytest.raises(ValueError, match="不是 surface 类型"):
        log.append("tool/call", {"name": "x"}, source_event_seqs=[0])
    # 合法 append
    log.append("user/message", _u("hi"), surface_op="append")
    assert log.surface_nodes == [0]
    # 非法 op 值
    with pytest.raises(ValueError, match="非法 surfaceOp"):
        log.append("user/message", _u("again"), surface_op={"op": "delete"})


def test_replace_splices_nodes_and_bumps_generation():
    log = EventLog()
    log.append("user/message", _u("1"), surface_op="append")          # seq 0
    log.append("user/message", _u("2"), surface_op="append")          # seq 1
    log.append("assistant/message", {"message": _a("旧")}, surface_op="append")  # seq 2
    gen = log.replace_generation
    # replace [0,1] → 新节点顶替两节点
    log.append("user/message", _u("checkpoint"), surface_op={"op": "replace", "start": 0, "end": 1},
               source_event_seqs=[0, 1])
    assert log.surface_nodes == [3, 2]
    assert log.replace_generation == gen + 1


def test_derive_cache_rebuilds_after_replace():
    log = EventLog()
    log.append("user/message", _u("长原文"), surface_op="append")
    log.append("user/message", _u("更多"), surface_op="append")
    assert [m["content"][0]["text"] for m in log.derive_messages()] == ["长原文", "更多"]
    log.append("user/message", _u("摘要"), surface_op={"op": "replace", "start": 0, "end": 1},
               source_event_seqs=[0, 1])
    # 缓存失效重建：只看到摘要
    assert [m["content"][0]["text"] for m in log.derive_messages()] == ["摘要"]
    # 再追加走增量路径
    log.append("user/message", _u("新"), surface_op="append")
    assert [m["content"][0]["text"] for m in log.derive_messages()] == ["摘要", "新"]


def test_source_seqs_must_cover_shadowed_and_reference_past():
    log = EventLog()
    log.append("user/message", _u("1"), surface_op="append")          # 0
    log.append("user/message", _u("2"), surface_op="append")          # 1
    # 覆盖不全
    with pytest.raises(ValueError, match="覆盖全部被遮蔽节点"):
        log.append("user/message", _u("x"), surface_op={"op": "replace", "start": 0, "end": 1},
                   source_event_seqs=[0])
    # 引用自身/未来
    with pytest.raises(ValueError, match="只能引用更早的事件"):
        log.append("user/message", _u("x"), surface_op={"op": "replace", "start": 0, "end": 1},
                   source_event_seqs=[0, 1, 99])
    # start/end 不在 nodes
    with pytest.raises(ValueError, match="当前 surface 节点"):
        log.append("user/message", _u("x"), surface_op={"op": "replace", "start": 5, "end": 6},
                   source_event_seqs=[0, 1])
    # 区间乱序
    with pytest.raises(ValueError, match="区间非法"):
        log.append("user/message", _u("x"), surface_op={"op": "replace", "start": 1, "end": 0},
                   source_event_seqs=[0, 1])


def test_tool_result_replace_content_only():
    log = EventLog()
    log.append("tool/call", {"callId": "c1", "name": "get_assets", "arguments": "{}"})
    full = {"id": "m1", "role": "user",
            "content": [{"type": "tool-result", "toolCallId": "c1",
                         "content": [{"type": "text", "text": "x" * 9000}], "isError": False}],
            "source": {"kind": "tool", "callId": "c1"}}
    log.append("tool/result", {"message": full}, surface_op="append",
               source_event_seqs=[0])
    # 非单个目标
    log.append("user/message", _u("u"), surface_op="append")
    with pytest.raises(ValueError, match="只能改写单个节点"):
        log.append("tool/result", {"message": full}, surface_op={"op": "replace", "start": 1, "end": 2},
                   source_event_seqs=[1, 2])
    # 目标不是 tool/result（seq 2 是 user/message）
    with pytest.raises(ValueError, match="不是 tool/result"):
        log.append("tool/result", {"message": full}, surface_op={"op": "replace", "start": 2, "end": 2},
                   source_event_seqs=[2])
    # 合法：只改 content[0].content（裁剪）
    pruned = {"id": "m1", "role": "user",
              "content": [{"type": "tool-result", "toolCallId": "c1",
                           "content": [{"type": "text", "text": "head … tail"}], "isError": False}],
              "source": {"kind": "tool", "callId": "c1"}}
    log.append("tool/result", {"message": pruned},
               surface_op={"op": "replace", "start": 1, "end": 1}, source_event_seqs=[1])
    assert log.surface_nodes == [3, 2]
    # meta 等其他字段变化 → 拒绝
    tampered = {"turn": 1, "message": {"id": "m1", "role": "user",
                 "content": [{"type": "tool-result", "toolCallId": "c1",
                              "content": [{"type": "text", "text": "z"}], "isError": False}],
                 "source": {"kind": "tool", "callId": "c1"}}}
    with pytest.raises(ValueError, match="只允许改写"):
        log.append("tool/result", tampered,
                   surface_op={"op": "replace", "start": 3, "end": 3}, source_event_seqs=[3])


def test_empty_assistant_message_derives_none():
    log = EventLog()
    log.append("user/message", _u("q"), surface_op="append")
    log.append("assistant/message",
               {"message": {"id": "a", "role": "assistant", "content": [],
                            "source": {"kind": "model", "provider": "p", "model": "m"}},
                "usage": {"prompt_tokens": 1, "completion_tokens": 1}},
               surface_op="append")
    msgs = log.derive_messages()
    assert len(msgs) == 1 and msgs[0]["content"][0]["text"] == "q"
