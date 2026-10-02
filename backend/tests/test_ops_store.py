"""store —— L4 持久化契约：首行头/撕裂尾/seq 连续/写-behind 落盘。"""

import json

import pytest

from wagent_backend.ops.agent import store
from wagent_backend.ops.agent.events import EventLog


def _u(text):
    return {"id": "u1", "role": "user", "content": [{"type": "text", "text": text}],
            "source": {"kind": "user"}}


def _write_session(path, events, header=None, *, torn=False, version=1):
    """手工写一个会话文件（不走 writer，模拟磁盘上的任意状态）。"""
    h = header if header is not None else store.header_line(
        "S-test", "full", "2026-08-30T10:00:00", "2026-08-30T10:00:00.000Z")
    if version != 1:
        h = {**h, "version": version}
    lines = [json.dumps(h, ensure_ascii=False)]
    lines += [json.dumps(e, ensure_ascii=False) for e in events]
    body = "\n".join(lines) + ("\n" if not torn else "")
    path.write_text(body, encoding="utf-8")


def _ev(seq, kind, data):
    e = {"seq": seq, "type": kind, "time": "2026-08-30T10:00:00.000Z", "data": data}
    if kind in ("user/message", "assistant/message", "tool/result"):
        e["surfaceOp"] = "append"
    return e


def test_header_version_mismatch_refused(tmp_path):
    p = tmp_path / "s.jsonl"
    _write_session(p, [_ev(0, "session/start", {"session_id": "S-test"})], version=2)
    with pytest.raises(ValueError, match="版本不符"):
        store.load_events(p)
    # 头行不是 session 类型同样拒读
    _write_session(p, [_ev(0, "session/start", {})],
                   header={"type": "event", "version": 1})
    with pytest.raises(ValueError, match="版本不符"):
        store.load_events(p)


def test_torn_tail_dropped(tmp_path):
    p = tmp_path / "s.jsonl"
    good = [_ev(0, "session/start", {"session_id": "S-test"}),
            _ev(1, "user/message", _u("hello"))]
    _write_session(p, good)
    # 追加一条撕裂行（写了一半崩溃）
    with open(p, "a", encoding="utf-8") as f:
        f.write('{"seq":2,"type":"user/mess')
    log = store.load_events(p)
    assert len(log.events) == 2          # 撕裂尾行被容忍丢弃
    assert log.surface_nodes == [1]
    assert log.derive_messages()[0]["content"][0]["text"] == "hello"


def test_seq_must_be_contiguous(tmp_path):
    p = tmp_path / "s.jsonl"
    _write_session(p, [_ev(0, "session/start", {}),
                       _ev(2, "user/message", _u("skip"))])   # 丢了 seq=1
    with pytest.raises(ValueError, match="seq 不连续"):
        store.load_events(p)


def test_write_behind_flush_and_reload_roundtrip(tmp_path):
    p = tmp_path / "s.jsonl"
    log = EventLog(p)
    log.bind_writer(store.SessionWriter(p, store.header_line(
        "S-rt", "full", "2026-08-30T10:00:00", "2026-08-30T10:00:00.000Z")))
    log.append("session/start", {"session_id": "S-rt", "tier": "full",
                                 "as_of": "2026-08-30T10:00:00"})
    log.append("user/message", _u("问题"), surface_op="append")
    log.append("assistant/message", {"message": {
        "id": "a", "role": "assistant", "content": [{"type": "text", "text": "回答"}],
        "source": {"kind": "model", "provider": "dashscope", "model": "qwen"}}},
        surface_op="append")
    # 满 64 条批缓冲会内联落盘；这里只有 3 条 → 显式 flush 屏障
    log.flush()

    back = store.load_events(p)
    assert [e["type"] for e in back.events] == [
        "session/start", "user/message", "assistant/message"]
    assert back.surface_nodes == [1, 2]
    assert [m["content"][0]["text"] for m in back.derive_messages()] == ["问题", "回答"]
    # 头行仍是第一行且带版本
    first = json.loads(p.read_text(encoding="utf-8").split("\n", 1)[0])
    assert first["type"] == "session" and first["version"] == store.SESSION_FORMAT_VERSION


def test_concurrent_flush_preserves_order(tmp_path):
    """模块 flusher 线程与显式 flush 并发时，落盘顺序必须等于追加顺序。

    回归：flush 曾在锁外写盘，大批次（assistant/message）与小批次（turn/end）
    竞态导致乱序落盘 → load_events seq 校验拒读 → 前端报「会话不存在」。
    """
    p = tmp_path / "s.jsonl"
    log = EventLog(p)
    log.bind_writer(store.SessionWriter(p, store.header_line(
        "S-race", "full", "2026-08-30T10:00:00", "2026-08-30T10:00:00.000Z")))
    big = "x" * 4000  # 大事件写盘慢，放大竞态窗口
    for i in range(200):
        log.append("assistant/chunk", {"turn": 1, "step": 1,
                                       "chunk": {"type": "text-delta", "text": big}})
        if i % 3 == 0:
            log.flush()  # 与模块 flusher 线程（0.2s 周期）并发
    log.flush()

    back = store.load_events(p)  # 乱序会在这里抛 seq 不连续
    assert [e["seq"] for e in back.events] == list(range(200))
