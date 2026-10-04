"""种子数据生成器：比赛演示夹具。

依据 docs/implementation/01_REQUIREMENTS.md §5：“至少两个项目、两个报修人、
两个技能不同技工和一经理、含安装/服务空间不同的设备、重叠预约场景”。

合成数据，来源明确，不迁移私有真实资料。
"""

from __future__ import annotations

import time

from octosense_backend.db import Database


def _now() -> int:
    return int(time.time() * 1000)


def seed_demo(db: Database) -> dict[str, str]:
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
        "space_a1": "sp-a-1",            # 东侧会议室（服务空间）
        "space_a2": "sp-a-2",            # 东侧走廊（服务空间）
        "space_a3": "sp-a-3",            # 配电间（服务空间）
        "space_mech": "sp-a-mech",       # 机房（安装位置，不作为会议空调服务空间）
        "asset_a1": "as-a-1",            # AC-001 会议室空调：装机房，服务会议室
        "asset_a2": "as-a-2",            # PWR-001 强电箱：装会议室，服务配电间
        "asset_a3": "as-a-3",            # EXH-001 新风机：装机房，服务会议室/走廊
    }
    with db.tx() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT OR IGNORE INTO repair_projects (project_id, name, code, created_at_ms) "
            "VALUES (?,?,?,?)",
            [("prj-A", "项目A", "PA", now), ("prj-B", "项目B", "PB", now)],
        )
        cur.executemany(
            "INSERT OR IGNORE INTO repair_users (user_id, display_name, is_demo) VALUES (?,?,?)",
            [("u-reporter-1", "报修人一", 1), ("u-reporter-2", "报修人二", 1),
             ("u-tech-1", "技工甲（HVAC）", 1), ("u-tech-2", "技工乙（电气）", 1),
             ("u-manager", "经理丙", 1)],
        )
        # 角色：一个用户可在多个项目有角色；技工带技能（逗号分隔）
        cur.executemany(
            "INSERT OR IGNORE INTO repair_roles (project_id, user_id, role, skills) VALUES (?,?,?,?)",
            [
                ("prj-A", "u-reporter-1", "REPORTER", None),
                ("prj-A", "u-tech-1", "TECHNICIAN", "HVAC"),
                ("prj-A", "u-tech-2", "TECHNICIAN", "ELECTRICAL"),
                ("prj-A", "u-manager", "MANAGER", None),
                ("prj-B", "u-reporter-2", "REPORTER", None),
                # 技工乙在项目B也有 ELECTRICAL 角色：用于跨项目同技工预约冲突（T11）
                ("prj-B", "u-tech-2", "TECHNICIAN", "ELECTRICAL"),
            ],
        )
        cur.executemany(
            "INSERT OR IGNORE INTO repair_spaces (space_id, project_id, name) VALUES (?,?,?)",
            [("sp-a-1", "prj-A", "东侧会议室"),
             ("sp-a-2", "prj-A", "东侧走廊"),
             ("sp-a-3", "prj-A", "配电间"),
             ("sp-a-mech", "prj-A", "机房（安装位置）")],
        )
        cur.executemany(
            "INSERT OR IGNORE INTO repair_assets (asset_id, project_id, asset_code, "
            "display_name, source, active) VALUES (?,?,?,?,?,?)",
            [("as-a-1", "prj-A", "AC-001", "会议室空调", "DEMO", 1),
             ("as-a-2", "prj-A", "PWR-001", "强电箱", "DEMO", 1),
             ("as-a-3", "prj-A", "EXH-001", "新风机", "DEMO", 1)],
        )
        # 安装位置 ≠ 服务空间（T08）
        cur.executemany(
            "INSERT OR IGNORE INTO repair_asset_services (asset_id, space_id, relation) "
            "VALUES (?,?,?)",
            [
                # AC-001 安装在机房，但服务东侧会议室
                ("as-a-1", "sp-a-mech", "INSTALLED_AT"),
                ("as-a-1", "sp-a-1", "SERVICES"),
                # PWR-001 安装在东侧会议室（同安装位置），但服务配电间 —— 不能因同位置误绑
                ("as-a-2", "sp-a-1", "INSTALLED_AT"),
                ("as-a-2", "sp-a-3", "SERVICES"),
                # EXH-001 服务会议室与走廊
                ("as-a-3", "sp-a-mech", "INSTALLED_AT"),
                ("as-a-3", "sp-a-1", "SERVICES"),
                ("as-a-3", "sp-a-2", "SERVICES"),
            ],
        )
    return fixtures
