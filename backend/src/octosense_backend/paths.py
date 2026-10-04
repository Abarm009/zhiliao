"""工程根与运行目录解析。

修复 V10：
  - api/__init__.py 用 parents[3] 得到的是 `backend/`，默认数据库/附件因此落到
    `backend/runtime/`，与文档要求的 `<工程根>/runtime/` 不一致。
  - 这里用“向上寻找工程标记”的方式定位工程根，不依赖 CWD，也不依赖相对层数。
  - 显式配置（参数或环境变量）始终优先。
"""

from __future__ import annotations

import os
from pathlib import Path

# 工程根标记：按顺序探测，命中任意一个即认为找到工程根
_ROOT_MARKERS = ("AGENTS.md", "backend/src/octosense_backend", "docs/implementation")


def find_project_root(start: Path | None = None) -> Path:
    """从 start（默认本文件位置）向上找工程根；找不到时退回 start 的祖父目录。"""
    start = (start or Path(__file__).resolve()).resolve()
    if start.is_file():
        start = start.parent
    for cand in [start, *start.parents]:
        for marker in _ROOT_MARKERS:
            if (cand / marker).exists():
                return cand
    # 兜底：本文件位于 <root>/backend/src/octosense_backend/paths.py → parents[4]
    return Path(__file__).resolve().parents[4]


PROJECT_ROOT = find_project_root()


def resolve_runtime_dir(env_var: str, default_name: str) -> Path:
    """显式环境变量 > 工程根 runtime/<default_name>。"""
    raw = os.environ.get(env_var)
    if raw and raw.strip():
        return Path(raw).expanduser()
    return PROJECT_ROOT / "runtime" / default_name


def default_db_path() -> Path:
    return resolve_runtime_dir("OCTOSENSE_DB", "octosense.db")


def default_evidence_root() -> Path:
    return resolve_runtime_dir("OCTOSENSE_EVIDENCE_ROOT", "evidence")
