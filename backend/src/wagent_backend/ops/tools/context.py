"""ToolContext —— 工具调用的横切上下文（依赖注入点）。

as_of 时间基准（工具说明 §1.4）：时间必须由调用方注入，工具不读系统时钟。
    回放/评测：场景时间；交互演示：系统时间；MCP：可选参数覆盖。
embedder：recall/write_memory 的向量服务，由上层注入（真实 api / 测试 local）。
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from wagent_backend.llm.embedder import EmbedFn


@dataclass
class ToolContext:
    as_of: datetime
    conn: sqlite3.Connection
    embedder: EmbedFn

    @classmethod
    def interactive(
        cls, conn: sqlite3.Connection, embedder: EmbedFn
    ) -> ToolContext:
        """交互演示：系统时间。"""
        return cls(as_of=datetime.now(), conn=conn, embedder=embedder)
