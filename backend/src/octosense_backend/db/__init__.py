"""数据库 schema 与连接管理。

精简版 L1 schema（核心 8 张表）：
  - repair_projects       项目
  - repair_users          业务账号
  - repair_roles          项目内角色（REPORTER/TECHNICIAN/MANAGER）
  - repair_spaces         服务空间
  - repair_assets         设备身份
  - repair_tasks          维修任务（task_id, status, version, expected_version, idempotency_key）
  - repair_actions        命令动作回执（动作幂等、actor、结果）
  - repair_events         业务事件流（seq, task_version, 事件类型, 关键前后值）

约束：
  - 同一任务最多一个 ACCEPTED 预约
  - 同技工同区间不可重叠
  - 幂等键全局唯一（org + actor + key）
  - 任务 version 单调递增
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

SCHEMA_VERSION = 2

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS repair_projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    created_at_ms INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS repair_users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    is_demo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS repair_roles (
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('REPORTER','TECHNICIAN','MANAGER')),
    skills TEXT,
    PRIMARY KEY (project_id, user_id, role),
    FOREIGN KEY (project_id) REFERENCES repair_projects(project_id),
    FOREIGN KEY (user_id) REFERENCES repair_users(user_id)
);

CREATE TABLE IF NOT EXISTS repair_spaces (
    space_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES repair_projects(project_id)
);

CREATE TABLE IF NOT EXISTS repair_assets (
    asset_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    asset_code TEXT NOT NULL,
    display_name TEXT NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('DEMO','LOCAL_IMPORT','EXTERNAL_SNAPSHOT')),
    active INTEGER NOT NULL DEFAULT 1,
    UNIQUE (project_id, asset_code),
    FOREIGN KEY (project_id) REFERENCES repair_projects(project_id)
);

CREATE TABLE IF NOT EXISTS repair_tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    reporter_id TEXT NOT NULL,
    assignee_id TEXT,
    asset_id TEXT,
    space_id TEXT,
    status TEXT NOT NULL CHECK (status IN (
        'DRAFT','OPEN','ACCEPTED','SCHEDULED','IN_PROGRESS',
        'AWAITING_ACCEPTANCE','COMPLETED','CANCELLED'
    )),
    version INTEGER NOT NULL DEFAULT 1,
    problem_text TEXT,
    contact_name TEXT,
    contact_info TEXT,
    preferred_window TEXT,
    created_at_ms INTEGER NOT NULL,
    updated_at_ms INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES repair_projects(project_id),
    FOREIGN KEY (reporter_id) REFERENCES repair_users(user_id)
);

CREATE INDEX IF NOT EXISTS ix_tasks_project_status ON repair_tasks(project_id, status);
CREATE INDEX IF NOT EXISTS ix_tasks_assignee ON repair_tasks(assignee_id);

CREATE TABLE IF NOT EXISTS repair_actions (
    action_id TEXT PRIMARY KEY,
    idempotency_key TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    project_id TEXT,
    command TEXT NOT NULL,
    task_id TEXT,
    expected_version INTEGER,
    result TEXT NOT NULL,            -- 'OK' | 'ERROR'
    error_code TEXT,
    error_detail TEXT,
    payload_hash TEXT,
    created_at_ms INTEGER NOT NULL,
    UNIQUE (actor_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS ix_actions_task ON repair_actions(task_id);
CREATE INDEX IF NOT EXISTS ix_actions_project ON repair_actions(project_id, command);

CREATE TABLE IF NOT EXISTS repair_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    task_version INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    before_state TEXT,
    after_state TEXT,
    at_ms INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_events_task ON repair_events(task_id, seq);

CREATE TABLE IF NOT EXISTS repair_appointments (
    appointment_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    technician_id TEXT NOT NULL,
    start_at_ms INTEGER NOT NULL,
    end_at_ms INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('PROPOSED','CONFIRMED','SUPERSEDED','CANCELLED')),
    proposed_by TEXT NOT NULL,
    confirmed_by TEXT,
    reason TEXT,
    created_at_ms INTEGER NOT NULL,
    updated_at_ms INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id)
);

CREATE INDEX IF NOT EXISTS ix_appt_tech ON repair_appointments(technician_id, status, start_at_ms);

CREATE TABLE IF NOT EXISTS repair_evidence (
    evidence_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    uploader_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    byte_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('READY','QUARANTINED')),
    created_at_ms INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id)
);
CREATE INDEX IF NOT EXISTS ix_evidence_task ON repair_evidence(task_id, status);

CREATE TABLE IF NOT EXISTS repair_pins (
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL,
    PRIMARY KEY (project_id, user_id, task_id),
    FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id)
);
CREATE INDEX IF NOT EXISTS ix_pins_user ON repair_pins(user_id, created_at_ms);

CREATE TABLE IF NOT EXISTS repair_advice (
    advice_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    source_kind TEXT NOT NULL CHECK (source_kind IN ('DEVICE_HISTORY','STAGE_HINT','PROGRESS_NOTE')),
    payload TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id)
);
CREATE INDEX IF NOT EXISTS ix_advice_task ON repair_advice(task_id, created_at_ms);

CREATE TABLE IF NOT EXISTS repair_completions (
    completion_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    round INTEGER NOT NULL,
    submitter_id TEXT NOT NULL,
    completion_text TEXT NOT NULL,
    disposition TEXT,
    evidence_ids TEXT,                       -- JSON 数组
    created_at_ms INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id),
    UNIQUE (task_id, round)
);
CREATE INDEX IF NOT EXISTS ix_completions_task ON repair_completions(task_id, round);
"""


class Database:
    """单进程 SQLite 数据库封装。允许多连接（每线程一连接）做真实并发测试。"""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._local = threading.local()
        self._init_lock = threading.Lock()
        self._initialized = False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,        # autocommit OFF, we use explicit BEGIN IMMEDIATE
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        return conn

    def init_schema(self) -> None:
        """显式 schema 迁移；不复用任何过时的 EXTRA_SCHEMA。

        旧库（v1）将自动 ALTER 增加 payload_hash 列，幂等。
        """
        with self._init_lock:
            if self._initialized:
                return
            conn = self._connect()
            try:
                conn.executescript(SCHEMA_SQL)
                # 列迁移（旧库 v1 → v2）
                cols = {row["name"] for row in conn.execute(
                    "PRAGMA table_info(repair_actions)"
                ).fetchall()}
                if "payload_hash" not in cols:
                    conn.execute("ALTER TABLE repair_actions ADD COLUMN payload_hash TEXT")
                tables = {row["name"] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()}
                if "repair_completions" not in tables:
                    conn.execute(
                        "CREATE TABLE repair_completions ("
                        "completion_id TEXT PRIMARY KEY,"
                        "task_id TEXT NOT NULL,"
                        "round INTEGER NOT NULL,"
                        "submitter_id TEXT NOT NULL,"
                        "completion_text TEXT NOT NULL,"
                        "disposition TEXT,"
                        "evidence_ids TEXT,"
                        "created_at_ms INTEGER NOT NULL,"
                        "FOREIGN KEY (task_id) REFERENCES repair_tasks(task_id),"
                        "UNIQUE (task_id, round))"
                    )
                    conn.execute(
                        "CREATE INDEX ix_completions_task "
                        "ON repair_completions(task_id, round)"
                    )
                self._initialized = True
            finally:
                conn.close()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        """原子事务边界。所有业务写操作必须走这里。"""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            self.init_schema()
            conn = self._connect()
            self._local.conn = conn
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    def conn(self) -> sqlite3.Connection:
        """只读连接（无事务）。"""
        self.init_schema()
        return self._connect()