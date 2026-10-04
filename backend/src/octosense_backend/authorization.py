"""统一对象授权与可见性规则。

修复 V02 / V03 / V04 / V09：
  - 服务端按**已认证主体** + 项目角色 + 任务关系 + 技能 + 阶段推导可见集合；
    客户端 `role` 参数只能在该主体真实拥有的角色中再**缩小**，绝不能扩权。
  - 详情 / 列表 / 事件 / 附件 / 收藏 / 历史建议共用同一入口，不再各自判断。
  - 技工可见范围 = 本人承接任务 ∪ 本项目技能匹配的 OPEN 待接单任务。
  - 敏感联系方式（contact_info）在接单前对技工脱敏。

规则来源：docs/implementation/01_REQUIREMENTS.md §3 权限矩阵。
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Iterable

# R01：P0 症状稳定枚举 → 需要的技能（OTHER 不限定技能）
CATEGORY_SKILL: dict[str, str | None] = {
    "HVAC_NOT_COOLING": "HVAC",
    "WATER_LEAK": "PLUMBING",
    "ELECTRICAL": "ELECTRICAL",
    "OTHER": None,
}

VALID_CATEGORIES = set(CATEGORY_SKILL)
VALID_ROLES = {"REPORTER", "TECHNICIAN", "MANAGER"}


def parse_skills(raw: str | None) -> set[str]:
    """`skills` 列存逗号分隔字符串；空/None → 空集合。"""
    if not raw:
        return set()
    return {s.strip() for s in str(raw).split(",") if s.strip()}


def roles_of(conn: sqlite3.Connection, actor_id: str, project_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
        (actor_id, project_id),
    ).fetchall()
    return {r["role"] for r in rows}


def skills_of(conn: sqlite3.Connection, actor_id: str, project_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT skills FROM repair_roles "
        "WHERE user_id=? AND project_id=? AND role='TECHNICIAN'",
        (actor_id, project_id),
    ).fetchall()
    out: set[str] = set()
    for r in rows:
        out |= parse_skills(r["skills"])
    return out


def required_skill(category: str | None) -> str | None:
    return CATEGORY_SKILL.get(category or "OTHER")


def skill_matches(conn: sqlite3.Connection, actor_id: str, project_id: str,
                  category: str | None) -> bool:
    need = required_skill(category)
    if need is None:
        return True
    return need in skills_of(conn, actor_id, project_id)


def technician_ok(conn: sqlite3.Connection, actor_id: str, project_id: str,
                  category: str | None) -> bool:
    """可自主接单/被分配/改派的技工：本项目 TECHNICIAN 角色 + 技能匹配。"""
    if "TECHNICIAN" not in roles_of(conn, actor_id, project_id):
        return False
    return skill_matches(conn, actor_id, project_id, category)


def projects_of(conn: sqlite3.Connection, actor_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT DISTINCT project_id FROM repair_roles WHERE user_id=?",
        (actor_id,),
    ).fetchall()
    return {r["project_id"] for r in rows}


def projects_with_role(conn: sqlite3.Connection, actor_id: str, role: str) -> set[str]:
    rows = conn.execute(
        "SELECT project_id FROM repair_roles WHERE user_id=? AND role=?",
        (actor_id, role),
    ).fetchall()
    return {r["project_id"] for r in rows}


def task_visible(conn: sqlite3.Connection, actor_id: str, row: Any) -> bool:
    """对象级可见性：与列表/事件/附件/收藏/历史建议完全一致。"""
    project_id = row["project_id"]
    roles = roles_of(conn, actor_id, project_id)
    if not roles:
        return False                      # 非本项目成员：一律不可见
    reporter_id = row["reporter_id"]
    assignee_id = row["assignee_id"]
    status = row["status"]
    if actor_id == reporter_id:
        return True                       # 报修人看自己的任务
    if assignee_id is not None and actor_id == assignee_id:
        return True                       # 技工看自己承接的任务
    if "MANAGER" in roles:
        return True                       # 经理看授权项目全部任务
    if "TECHNICIAN" in roles and status == "OPEN":
        # 接单前可见的前提是技能匹配；技能不匹配不算可见
        return skill_matches(conn, actor_id, project_id, row["category"] if "category" in row.keys() else None)
    return False


def visible_task_ids(conn: sqlite3.Connection, actor_id: str, project_id: str) -> set[str]:
    rows = conn.execute(
        "SELECT task_id, project_id, reporter_id, assignee_id, status, category "
        "FROM repair_tasks WHERE project_id=?",
        (project_id,),
    ).fetchall()
    return {r["task_id"] for r in rows if task_visible(conn, actor_id, r)}


def can_see_contact(conn: sqlite3.Connection, actor_id: str, row: Any) -> bool:
    """敏感联系方式：报修人 / 当前承接者 / 经理可见；其他人（含待接单技工）脱敏。"""
    if actor_id == row["reporter_id"]:
        return True
    if row["assignee_id"] is not None and actor_id == row["assignee_id"]:
        return True
    roles = roles_of(conn, actor_id, row["project_id"])
    return "MANAGER" in roles


def narrow_role(conn: sqlite3.Connection, actor_id: str, project_id: str,
                role_filter: str | None) -> str | None:
    """把客户端 role 过滤值收敛成该主体真实拥有的角色之一。

    - None            → 不额外过滤（返回服务端按主体推导的范围）
    - 主体真实拥有的角色 → 按该角色再缩小
    - 其它任何值      → 403（不允许靠 role 参数扩权）
    """
    if role_filter is None or role_filter == "":
        return None
    rf = role_filter.strip().upper()
    if rf not in VALID_ROLES:
        raise _invalid_role(f"unknown role {role_filter!r}")
    if rf not in roles_of(conn, actor_id, project_id):
        raise _invalid_role(f"caller is not a {rf} in project {project_id}")
    return rf


def _invalid_role(detail: str):
    from octosense_backend.errors import InvalidRoleFilter
    return InvalidRoleFilter(detail)


def masks_for(conn: sqlite3.Connection, actor_id: str, row: Any) -> list[str]:
    """返回需要脱敏的字段名列表。"""
    if can_see_contact(conn, actor_id, row):
        return []
    return ["contact_info"]


def service_relation_ok(conn: sqlite3.Connection, asset_id: str, space_id: str) -> bool:
    """设备—服务空间的有效服务关系（不是安装位置相同）。"""
    row = conn.execute(
        "SELECT 1 FROM repair_asset_services "
        "WHERE asset_id=? AND space_id=? AND relation='SERVICES'",
        (asset_id, space_id),
    ).fetchone()
    return row is not None


def asset_services(conn: sqlite3.Connection, asset_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT space_id FROM repair_asset_services "
        "WHERE asset_id=? AND relation='SERVICES'",
        (asset_id,),
    ).fetchall()
    return [r["space_id"] for r in rows]


def asset_locations(conn: sqlite3.Connection, asset_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT space_id FROM repair_asset_services "
        "WHERE asset_id=? AND relation='INSTALLED_AT'",
        (asset_id,),
    ).fetchall()
    return [r["space_id"] for r in rows]
