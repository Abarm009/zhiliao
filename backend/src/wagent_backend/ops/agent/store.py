"""store —— L4 会话持久化（dsh session-persistence-jsonl 的 Python 移植）。

布局：每会话一个追加型 JSONL；**首行是 session 头**（版本契约，版本不符拒读）；
事件一行一条（紧凑分隔符——chunk 事件量大）。写-behind：追加不做 I/O，
模块级单 flusher 线程统一管理全部 writer（200ms 上限延迟或缓冲 ≥64 条即刷），
轮末 flush() 是显式持久化屏障；写失败回填缓冲保序重试。
读取：撕裂尾行（无换行符）容忍丢弃；seq 必须连续；边读边 fold surface。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

SESSION_FORMAT_VERSION = 1
_FLUSH_INTERVAL = 0.2   # 秒：flusher 最大批延迟（dsh DEFAULT_WRITE_BATCH_MAX_DELAY_MS=200）
_FLUSH_BATCH = 64       # 缓冲到达即刷的条数


def header_line(sid: str, tier: str, as_of: str, created_at: str) -> dict[str, Any]:
    """文件首行的 session 头（dsh HeaderLine；tier/as_of 是 wagent 的存储元数据）。"""
    return {"type": "session", "version": SESSION_FORMAT_VERSION, "id": sid,
            "createdAt": created_at, "tier": tier, "as_of": as_of}


class SessionWriter:
    """单会话的写-behind writer。文件已存在则续写（不重写头行）。"""

    def __init__(self, path: Path, header: dict[str, Any] | None = None):
        self._path = Path(path)
        self._buf: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        if header is not None and not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w", encoding="utf-8") as f:
                f.write(json.dumps(header, ensure_ascii=False) + "\n")
        with _registry_lock:
            _writers.add(self)

    def append(self, ev: dict[str, Any]) -> None:
        with self._lock:
            self._buf.append(ev)
            big = len(self._buf) >= _FLUSH_BATCH
        if big:
            self.flush()
        else:
            _wake_event.set()

    def flush(self) -> None:
        # 文件写必须持锁：swap 与 write 分离会让 flusher 线程与轮末 flush 竞态，
        # 大批次（assistant/message）写盘慢、小批次（turn/end）后来先到 → 事件乱序落盘，
        # load_events 的 seq 连续校验拒读，会话表现为「不存在」。
        with self._lock:
            batch, self._buf = self._buf, []
            if not batch:
                return
            data = "".join(json.dumps(ev, ensure_ascii=False,
                                      separators=(",", ":")) + "\n" for ev in batch)
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(data)
            except OSError:
                self._buf = batch + self._buf  # 回填缓冲保序，等下次重试
                raise

    def close(self) -> None:
        self.flush()
        with _registry_lock:
            _writers.discard(self)


# ── 模块级单 flusher 线程（不为每个会话起线程）────────────

_writers: set[SessionWriter] = set()
_registry_lock = threading.Lock()
_wake_event = threading.Event()


def _flusher_loop() -> None:
    while True:
        _wake_event.wait(_FLUSH_INTERVAL)
        _wake_event.clear()
        with _registry_lock:
            writers = list(_writers)
        for w in writers:
            try:
                w.flush()
            except OSError:
                pass  # 单会话写失败不拖累其他会话；缓冲保序重试


threading.Thread(target=_flusher_loop, name="session-writer", daemon=True).start()


def load_events(path: Path) -> "Any":
    """读会话文件 → EventLog（surface 校验 + fold）。

    抛 ValueError：头行缺失/版本不符/seq 不连续。撕裂尾行（最后一行无换行符）容忍丢弃。
    """
    from wagent_backend.ops.agent import surface
    from wagent_backend.ops.agent.events import EventLog

    raw = Path(path).read_text(encoding="utf-8").split("\n")
    if raw and raw[-1] == "":
        raw.pop()  # 文件以换行结尾的正常情况
    elif raw:
        raw.pop()  # 尾行无换行 = 撕裂写，丢弃（dsh 同款容忍）
    if not raw:
        raise ValueError(f"会话文件为空：{path}")
    header = json.loads(raw[0])
    if header.get("type") != "session" or header.get("version") != SESSION_FORMAT_VERSION:
        raise ValueError(f"会话文件版本不符（期望 {SESSION_FORMAT_VERSION}）：{path}")
    log = EventLog()
    for i, line in enumerate(raw[1:]):
        ev = json.loads(line)
        if ev.get("seq") != i:
            raise ValueError(f"seq 不连续：期望 {i}，得到 {ev.get('seq')}")
        surface.validate_surface(ev, log.surface_nodes, log.events)
        log.events.append(ev)
        log.surface_nodes, replaced = surface.apply_event(log.surface_nodes, ev)
        if replaced:
            log.replace_generation += 1
    return log
