"""session —— 会话目录与生命周期（data/sessions/*.jsonl，首行 session 头）。"""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from wagent_backend.ops.agent import store
from wagent_backend.ops.agent.events import EventLog

SESSIONS_DIR = Path(__file__).resolve().parents[4] / "data" / "sessions"


def _sessions_dir() -> Path:
    import os

    return Path(os.environ.get("WAGENT_SESSIONS_DIR") or SESSIONS_DIR)


def new_session_id() -> str:
    return "S-" + datetime.now().strftime("%m%d-%H%M%S") + "-" + secrets.token_hex(2)


def create(tier: str, as_of: datetime) -> tuple[str, EventLog]:
    _sessions_dir().mkdir(parents=True, exist_ok=True)
    sid = new_session_id()
    path = _sessions_dir() / f"{sid}.jsonl"
    log = EventLog(path)
    # 首行 session 头（版本契约）+ 写-behind writer（dsh persistence 同款）
    log.bind_writer(store.SessionWriter(path, store.header_line(
        sid, tier, as_of.strftime("%Y-%m-%dT%H:%M:%S"),
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")))
    log.append("session/start", {
        "session_id": sid, "tier": tier,
        "as_of": as_of.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    return sid, log


def load(session_id: str) -> EventLog | None:
    path = _sessions_dir() / f"{session_id}.jsonl"
    if not path.exists():
        return None
    try:
        log = store.load_events(path)
    except (ValueError, json.JSONDecodeError, OSError):
        return None  # 旧格式/损坏文件拒读（README 注明需清空 data/sessions/）
    log.bind_writer(store.SessionWriter(path))  # 续聊也要持久化（文件已存在不重写头）
    return log


def list_sessions() -> list[dict]:
    out = []
    for p in sorted(_sessions_dir().glob("*.jsonl"), reverse=True):
        try:
            log = store.load_events(p)
        except (ValueError, json.JSONDecodeError, OSError):
            continue
        if log.events:
            m = log.meta()
            m["session_id"] = m["session_id"] or p.stem
            out.append(m)
    return out


def search_sessions(q: str) -> list[dict]:
    """L5 跨会话检索（dsh session-search 的最小移植；纯 Web 端点，不进模型工具）。

    q 对用户原文与工具结果摘要做包含匹配；返回命中会话的 meta + 命中片段。
    真值隔离不受影响：只扫事件里的用户文本与 digest，不触 truth_*。
    """
    q = q.strip()
    if not q:
        return []
    out = []
    for p in sorted(_sessions_dir().glob("*.jsonl"), reverse=True):
        try:
            log = store.load_events(p)
        except (ValueError, json.JSONDecodeError, OSError):
            continue
        texts = [t for e in log.events if e["type"] == "user/message"
                 for t in [EventLog._user_text(e)] if t and q in t]
        digests = [e["data"]["meta"]["digest"] for e in log.events
                   if e["type"] == "tool/result"
                   and q in (e["data"].get("meta") or {}).get("digest", "")]
        if not texts and not digests:
            continue
        m = log.meta()
        m["session_id"] = m["session_id"] or p.stem
        m["matched_text"] = texts[-1][:120]
        m["matched_digests"] = digests[:5]
        out.append(m)
    return out
