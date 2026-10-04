"""嵌套 conftest：注入 backend/src 到 sys.path 并提供 octosense_backend fixture。

所有 fixture 共享同一个 CommandExecutor（统一命令执行边界）与同一个可注入时钟，
避免各模块各持一份时钟造成“服务端时间”不一致。
"""
import sys
import tempfile
import time
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from octosense_backend.appointments import AppointmentCommands
from octosense_backend.commands import CommandExecutor
from octosense_backend.db import Database
from octosense_backend.extended import ExtendedCommands
from octosense_backend.seed import seed_demo


class MutableClock:
    """可注入的服务端时钟（毫秒）。测试通过 set/advance 控制它。"""

    def __init__(self, now: int | None = None):
        self.now = int(now if now is not None else time.time() * 1000)

    def __call__(self) -> int:
        return self.now

    def set(self, now: int) -> None:
        self.now = int(now)

    def advance(self, delta_ms: int) -> None:
        self.now += int(delta_ms)


@pytest.fixture
def db(tmp_path) -> Database:
    """每个测试独立临时库，并装入合成种子夹具。

    夹具是合法允许路径的前提（项目/角色/技能/服务关系），不播种的测试会误报
    “actor not registered”。测试一律不得依赖任何在跑实例或工程运行库。
    """
    d = Database(tmp_path / "test.db")
    d.init_schema()
    seed_demo(d)
    yield d


@pytest.fixture
def fixtures(db: Database) -> dict[str, str]:
    return seed_demo(db)


@pytest.fixture
def clock() -> MutableClock:
    return MutableClock()


@pytest.fixture
def executor(db: Database, clock) -> CommandExecutor:
    return CommandExecutor(db, clock=clock)


@pytest.fixture
def appt_cmds(db: Database, executor: CommandExecutor, clock) -> AppointmentCommands:
    return AppointmentCommands(db, executor=executor, clock=clock)


@pytest.fixture
def ext(db: Database, executor: CommandExecutor, clock, tmp_path) -> ExtendedCommands:
    """evidence_root 默认锚到临时目录，避免污染工程 runtime。"""
    return ExtendedCommands(db, evidence_root=tmp_path / "evidence", clock=clock,
                            executor=executor)


@pytest.fixture
def api(db, clock, tmp_path):
    """TestClient：与 `db` fixture 共用同一临时库，使 db fixture 的 DELETE/INSERT
    立即对 API 可见；evidence_root 仍锚到独立子目录避免污染 db 路径。"""
    from fastapi.testclient import TestClient
    from octosense_backend.api import API_PREFIX, make_app
    app = make_app(db.db_path, tmp_path / "api-evidence", clock=clock)
    client = TestClient(app)
    return client
