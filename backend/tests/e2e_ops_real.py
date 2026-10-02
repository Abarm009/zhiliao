"""真实模型端到端冒烟（不进 pytest —— 手动跑，需要 .env 里的真实 key）。

    uv run python tests/e2e_ops_real.py

跑三个场景（回放口径 as_of=2026-08-23 10:00，临时库）：
    A. full 档 · 复发链     → 期望 root_cause=valve_actuator_failure + is_repeat_fault
    B. full 档 · 欠费锁机   → 期望 root_cause=billing_suspension（只看 lock_status 通道）
    C. l1 档  · 无记忆对照  → 无历史可查，允许判断偏差，但流程必须完整
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from wagent_backend.llm import client
from wagent_backend.llm.embedder import get_embedder
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.runner import run_turn
from wagent_backend.ops.data.db import connect, init_db
from wagent_backend.ops.data.seed import seed
from wagent_backend.ops.tools.context import ToolContext

AS_OF = datetime(2026, 8, 23, 10, 0)

CASES = [
    ("A 复发链·full", "full",
     "你好，A座25楼东侧的会议室空调又不出冷风了，这已经是最近第三次了，能不能彻底修好？"),
    ("B 欠费锁机·full", "full",
     "A座1106瑜伽馆的空调开不了机，面板按了没反应，麻烦尽快看下。"),
    ("C 无记忆对照·l1", "l1",
     "A座25楼东侧的空调不制冷，风是热的。"),
]


def main() -> None:
    if not client.is_configured():
        print("✗ 未配置 LLM_API_KEY（agent/.env）")
        return
    print(f"✓ 模型：{client.model_name()}\n")

    tmp = tempfile.mkdtemp(prefix="wagent-ops-e2e-")
    os.environ["WAGENT_OPS_DB"] = os.path.join(tmp, "ops.db")
    os.environ["WAGENT_SESSIONS_DIR"] = os.path.join(tmp, "sessions")
    conn = connect()
    init_db(conn)
    seed(conn, get_embedder())

    for name, tier, text in CASES:
        ctx = ToolContext(as_of=AS_OF, conn=connect(), embedder=get_embedder())
        log = EventLog()
        print(f"── {name} ─────────────────────────────────")
        print(f"租户：{text}")
        result = run_turn(client.stream, ctx, log, text, tier)
        for ev in log.events:
            if ev["type"] == "assistant/message":
                blocks = ev["data"]["message"]["content"]
                text_out = next((b["text"] for b in blocks
                                 if b.get("type") == "text" and b.get("text")), "")
                think = next((b["text"] for b in blocks
                              if b.get("type") == "reasoning" and b.get("text")), "")
                if text_out:
                    print(f"  💭 {text_out.splitlines()[0][:80]}")
                elif think:
                    print(f"  🧠 {think.splitlines()[0][:80]}")
            elif ev["type"] == "tool/result":
                payload = ev["data"]["message"]["content"][0]["content"][0]["text"]
                mark = "✗" if json.loads(payload).get("error") else "✓"
                meta = ev["data"]["meta"]
                print(f"  {mark} {meta['name']:<26} {meta['digest']}")
        dec = result.get("decision")
        if dec:
            print(f"  → Decision: {dec['root_cause']} conf={dec['root_cause_confidence']} "
                  f"repeat={dec['is_repeat_fault']} evidence={dec['repeat_evidence']} "
                  f"action={dec['recommended_action']} liability={dec['liability']} "
                  f"mem={dec['memory_ids_used']}")
        print(f"  → reason={result['reason']}  tokens≈{log.token_estimate()}\n")
        ctx.conn.close()


if __name__ == "__main__":
    main()
