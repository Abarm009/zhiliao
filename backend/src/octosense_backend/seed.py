"""种子数据生成器：用于 L1 测试与最小演示初始化。

根据 01_REQUIREMENTS.md "比赛数据：至少两个项目、两个报修人、两个技能不同技工和一经理"。
所有数据来自合成种子，来源明确标注，不迁移私有真实资料。
"""

from __future__ import annotations

import time

from octosense_backend.db import Database


def _now() -> int:
    return int(time.time() * 1000)


def seed_demo(db: Database) -> dict[str, str]:
    """插入比赛演示所需最小夹具。返回键值映射便于测试。"""
    db.init_schema()
    now = _now()
    fixtures = {
        "project_a": "prj-A",
        "project_b": "prj-B",
        "reporter_1": "u-reporter-1",
        "reporter_2": "u-reporter-2",
        "tech_1": "u-tech-1",
        "tech_2": "u-tech-2",
        "manager": "u-manager",
        "space_a1": "sp-a-1",
        "asset_a1": "as-a-1",
        "asset_a2": "as-a-2",
    }
    rows = [
        # 项目
        ("repair_projects", (fixtures["project_a"], "项目A", "PA", now)),
        ("repair_projects", (fixtures["project_b"], "项目B", "PB", now)),
        # 账号（演示用户；is_demo=1）
        ("repair_users", (fixtures["reporter_1"], "报修人一", 1)),
        ("repair_users", (fixtures["reporter_2"], "报修人二", 1)),
        ("repair_users", (fixtures["tech_1"], "技工甲（HVAC）", 1)),
        ("repair_users", (fixtures["tech_2"], "技工乙（电气）", 1)),
        ("repair_users", (fixtures["manager"], "经理丙", 1)),
        # 角色
        ("repair_roles", (fixtures["project_a"], fixtures["reporter_1"], "REPORTER", None)),
        ("repair_roles", (fixtures["project_a"], fixtures["tech_1"], "TECHNICIAN", "HVAC")),
        ("repair_roles", (fixtures["project_a"], fixtures["tech_2"], "TECHNICIAN", "ELECTRICAL")),
        ("repair_roles", (fixtures["project_a"], fixtures["manager"], "MANAGER", None)),
        ("repair_roles", (fixtures["project_b"], fixtures["reporter_2"], "REPORTER", None)),
        ("repair_roles", (fixtures["project_b"], fixtures["tech_2"], "TECHNICIAN", "ELECTRICAL")),
        # 服务空间
        ("repair_spaces", (fixtures["space_a1"], fixtures["project_a"], "东侧会议室")),
        # 设备
        ("repair_assets", (fixtures["asset_a1"], fixtures["project_a"], "AC-001", "会议室空调", "DEMO", 1)),
        ("repair_assets", (fixtures["asset_a2"], fixtures["project_a"], "PWR-001", "强电箱", "DEMO", 1)),
    ]
    with db.tx() as conn:
        cur = conn.cursor()
        for table, row in rows:
            if table == "repair_projects":
                cur.execute(
                    "INSERT OR IGNORE INTO repair_projects (project_id, name, code, created_at_ms) "
                    "VALUES (?,?,?,?)", row,
                )
            elif table == "repair_users":
                cur.execute(
                    "INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) "
                    "VALUES (?,?,?)", row,
                )
            elif table == "repair_roles":
                cur.execute(
                    "INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) "
                    "VALUES (?,?,?,?)", row,
                )
            elif table == "repair_spaces":
                cur.execute(
                    "INSERT OR IGNORE INTO repair_spaces (space_id, project_id, name) "
                    "VALUES (?,?,?)", row,
                )
            elif table == "repair_assets":
                cur.execute(
                    "INSERT OR IGNORE INTO repair_assets (asset_id, project_id, asset_code, display_name, source, active) "
                    "VALUES (?,?,?,?,?,?)", row,
                )
    return fixtures