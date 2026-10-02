"""嵌套 conftest：注入 backend/src 到 sys.path 并提供 octosense_backend fixture。

修复后版本：
  - 新签名 actor_resolver(project_id, actor_id)
  - 提供 clock 注入 fixture
"""
import sys
import tempfile
from pathlib import Path

import pytest

# conftest.py 自身: backend/tests/octosense_backend/conftest.py
# parents[0] = tests/octosense_backend
# parents[1] = tests
# parents[2] = backend
SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from octosense_backend.appointments import AppointmentCommands
from octosense_backend.commands import CommandExecutor
from octosense_backend.db import Database
from octosense_backend.extended import ExtendedCommands
from octosense_backend.seed import seed_demo


@pytest.fixture
def db(tmp_path) -> Database:
    d = Database(tmp_path / "test.db")
    d.init_schema()
    yield d


@pytest.fixture
def fixtures(db: Database) -> dict[str, str]:
    return seed_demo(db)


@pytest.fixture
def actor_resolver(db: Database):
    """新签名：actor_resolver(project_id, actor_id) -> set[str] of roles in this project。"""
    def resolve(project_id: str, actor_id: str) -> set[str]:
        conn = db.conn()
        try:
            rows = conn.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
                (actor_id, project_id),
            ).fetchall()
            return {r["role"] for r in rows}
        finally:
            conn.close()
    return resolve


@pytest.fixture
def clock():
    """默认测试时钟：返回当前时间（毫秒）。

    测试可通过 monkeypatch 替换为可控时钟注入到执行器。
    """
    import time
    return lambda: int(time.time() * 1000)


@pytest.fixture
def executor(db: Database, actor_resolver, clock) -> CommandExecutor:
    return CommandExecutor(db, actor_resolver, clock=clock)


@pytest.fixture
def appt_cmds(db: Database) -> AppointmentCommands:
    return AppointmentCommands(db)


@pytest.fixture
def ext(db: Database, tmp_path, clock) -> ExtendedCommands:
    """默认 evidence_root 锚到临时目录，避免污染工程 runtime。"""
    e = ExtendedCommands(db, evidence_root=tmp_path / "evidence")
    e._clock = clock
    return e
