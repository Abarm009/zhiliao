"""repo —— 工具层的唯一数据入口（薄 SQL 层，无业务规则）。

业务规则（校验、排序、判定顺序）全部在 tools/impl.py；
本模块只做存取，便于以后换库（如回到 Postgres）只改这里。
"""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from typing import Any

from wagent_backend.ops.data.db import iso, jdump, jload


# ── 空间 / 楼栋 ───────────────────────────────────────────────

def building_exists(conn: sqlite3.Connection, building_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM building WHERE building_id=?", (building_id,)
    ).fetchone() is not None


def resolve_building_hint(conn: sqlite3.Connection, hint: str) -> str | None:
    """building_hint 宽容解析：BLD-A / A栋 / A座 / A楼 / A 都能落到 building_id。"""
    h = (hint or "").strip()
    if not h:
        return None
    forms = {h.upper(), h.replace("座", "栋").replace("楼", "栋")}
    head = h[0]
    if head.isascii() and head.isalpha():
        forms.update({f"BLD-{head.upper()}", f"{head.upper()}栋"})
    for row in conn.execute("SELECT building_id, name FROM building"):
        if row["building_id"] in forms or (row["name"] or "") in forms:
            return row["building_id"]
    return None


def space_get(conn: sqlite3.Connection, space_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM space WHERE space_id=?", (space_id,)).fetchone()


def spaces_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM space ORDER BY space_id").fetchall()


def building_name(conn: sqlite3.Connection, building_id: str) -> str:
    row = conn.execute(
        "SELECT name FROM building WHERE building_id=?", (building_id,)
    ).fetchone()
    return row["name"] if row else building_id


def spaces_hierarchy(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """位置选择器数据：空间 + 楼栋 + 项目（前端 项目/楼栋/楼层/位置 四级下拉）。"""
    return conn.execute(
        """
        SELECT s.space_id, s.floor, s.zone, s.unit_no, s.space_type,
               b.building_id, b.name AS building_name,
               p.property_id, p.name AS property_name
          FROM space s
          JOIN building b ON b.building_id = s.building_id
          JOIN property p ON p.property_id = b.property_id
         ORDER BY p.property_id, b.building_id, s.floor, s.space_id
        """
    ).fetchall()


# ── 设备 / 服务关系 / 运行快照 ────────────────────────────────

def asset_get(conn: sqlite3.Connection, asset_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM asset WHERE asset_id=?", (asset_id,)).fetchone()


def assets_serving(
    conn: sqlite3.Connection, space_id: str, as_of: datetime
) -> list[sqlite3.Row]:
    """as_of 时有效的服务关系 + 台账 + 类型（运行快照另查）。"""
    return conn.execute(
        """
        SELECT s.*, a.*, t.category AS _category, t.name AS _type_name,
               sra.service_role AS _service_role, sra.coverage_pct AS _coverage_pct
          FROM space_served_by_asset sra
          JOIN asset a ON a.asset_id = sra.asset_id
          JOIN asset_type t ON t.asset_type_id = a.asset_type_id
          JOIN space s ON s.space_id = sra.space_id
         WHERE sra.space_id = ?
           AND sra.valid_from <= ?
           AND (sra.valid_to IS NULL OR sra.valid_to >= ?)
        """,
        (space_id, iso(as_of)[:10], iso(as_of)[:10]),
    ).fetchall()


def runtime_latest(
    conn: sqlite3.Connection, asset_id: str, as_of: datetime
) -> sqlite3.Row | None:
    """ts <= as_of 的最新一条 —— 禁止读取未来快照。"""
    return conn.execute(
        "SELECT * FROM asset_runtime WHERE asset_id=? AND ts<=? ORDER BY ts DESC LIMIT 1",
        (asset_id, iso(as_of)),
    ).fetchone()


# ── 工单 / 事件 / 流水（L2，只追加）──────────────────────────

def wo_get(conn: sqlite3.Connection, wo_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM work_order WHERE wo_id=?", (wo_id,)).fetchone()


def wo_open_same_symptom(
    conn: sqlite3.Connection,
    space_id: str,
    symptom: str,
    start: datetime,
    end: datetime,
    exclude_wo_id: str | None = None,
) -> list[str]:
    """同空间同症状、窗口内、尚未闭环（无 closed 事件）的其他工单号 —— 复发硬停用。"""
    rows = conn.execute(
        "SELECT w.wo_id FROM work_order w"
        " WHERE w.space_id=? AND w.symptom=?"
        " AND w.created_at >= ? AND w.created_at <= ?"
        " AND w.wo_id != COALESCE(?, '')"
        " AND NOT EXISTS (SELECT 1 FROM work_order_event e"
        "                 WHERE e.wo_id = w.wo_id AND e.event_type = 'closed')"
        " ORDER BY w.created_at, w.wo_id",
        (space_id, symptom, iso(start), iso(end), exclude_wo_id),
    ).fetchall()
    return [r["wo_id"] for r in rows]


def wo_events(conn: sqlite3.Connection, wo_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM work_order_event WHERE wo_id=? ORDER BY ts, event_id", (wo_id,)
    ).fetchall()


def wo_list_by_scope(
    conn: sqlite3.Connection,
    scope: str,
    scope_id: str,
    start: datetime,
    end: datetime,
) -> list[sqlite3.Row]:
    sql = "SELECT DISTINCT w.* FROM work_order w"
    params: list[Any] = []
    if scope == "asset":
        sql += " WHERE w.asset_id=?"
        params = [scope_id]
    elif scope == "space":
        sql += " WHERE w.space_id=?"
        params = [scope_id]
    elif scope == "building":
        sql += " JOIN space s ON s.space_id = w.space_id WHERE s.building_id=?"
        params = [scope_id]
    elif scope == "tenant":
        # 工单发生时刻，该空间由该租户占用（工具说明 §4 tenant scope 连接）
        sql += (
            " JOIN tenant_occupies_space tos ON tos.space_id = w.space_id"
            " AND w.created_at >= tos.valid_from"
            " AND (tos.valid_to IS NULL OR w.created_at <= tos.valid_to + 'T23:59:59')"
            " WHERE tos.tenant_id=?"
        )
        params = [scope_id]
    sql += " AND w.created_at >= ? AND w.created_at <= ? ORDER BY w.created_at DESC, w.wo_id"
    params += [iso(start), iso(end)]
    return conn.execute(sql, params).fetchall()


def next_wo_id(conn: sqlite3.Connection, as_of: datetime) -> str:
    stem = as_of.strftime("WO-%y%m%d")
    n = conn.execute(
        "SELECT COUNT(*) c FROM work_order WHERE wo_id LIKE ?", (stem + "-%",)
    ).fetchone()["c"]
    return f"{stem}-{n + 1:03d}"


def insert_workorder(
    conn: sqlite3.Connection,
    wo_id: str,
    created_at: datetime,
    space_id: str | None,
    asset_id: str | None,
    reporter_contact_id: str | None,
    raw_text: str,
    symptom: str,
    urgency: str,
) -> None:
    conn.execute(
        "INSERT INTO work_order VALUES (?,?,?,?,?,?,?,?)",
        (wo_id, iso(created_at), space_id, asset_id, reporter_contact_id,
         raw_text, symptom, urgency),
    )


def insert_wo_event(
    conn: sqlite3.Connection,
    wo_id: str,
    ts: datetime,
    event_type: str,
    technician_id: str | None = None,
    reported_cause: str | None = None,
    action_taken: str | None = None,
    liability: str | None = None,
    note: str | None = None,
    material_cost: float | None = None,
    labor_cost: float | None = None,
) -> None:
    conn.execute(
        "INSERT INTO work_order_event (wo_id,ts,event_type,technician_id,reported_cause,"
        "action_taken,liability,note,material_cost,labor_cost) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (wo_id, iso(ts), event_type, technician_id, reported_cause, action_taken,
         liability, note, material_cost, labor_cost),
    )


def insert_event_log(
    conn: sqlite3.Connection,
    ts: datetime,
    source: str,
    payload: dict,
    asset_id: str | None = None,
    space_id: str | None = None,
) -> int:
    cur = conn.execute(
        "INSERT INTO event_log (ts,source,asset_id,space_id,payload) VALUES (?,?,?,?,?)",
        (iso(ts), source, asset_id, space_id, jdump(payload)),
    )
    return cur.lastrowid or 0


def event_log_seq(conn: sqlite3.Connection, source: str, prefix: str) -> int:
    """为 receipt/ticket 生成序号：按同源事件计数 +1。"""
    rows = conn.execute("SELECT payload FROM event_log WHERE source=?", (source,)).fetchall()
    n = 0
    import json as _json

    for r in rows:
        p = _json.loads(r["payload"])
        rid = p.get("receipt_id") or p.get("ticket_id") or ""
        if rid.startswith(prefix):
            n += 1
    return n + 1


# ── 合同 / 租户 / 技工 ───────────────────────────────────────

def clauses_valid(conn: sqlite3.Connection, space_id: str, as_of: date) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM contract_clause WHERE space_id=? AND valid_from<=? "
        "AND (valid_to IS NULL OR valid_to>=?) ORDER BY clause_id",
        (space_id, as_of.isoformat(), as_of.isoformat()),
    ).fetchall()


def tenant_exists(conn: sqlite3.Connection, tenant_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM tenant WHERE tenant_id=?", (tenant_id,)
    ).fetchone() is not None


def contact_get(conn: sqlite3.Connection, contact_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM contact WHERE contact_id=?", (contact_id,)).fetchone()


def technicians_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM technician ORDER BY technician_id").fetchall()


def technician_get(conn: sqlite3.Connection, technician_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM technician WHERE technician_id=?", (technician_id,)
    ).fetchone()


# ── L3 洞察 ──────────────────────────────────────────────────

def insight_get(conn: sqlite3.Connection, insight_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM insight WHERE insight_id=?", (insight_id,)).fetchone()


def insight_list(
    conn: sqlite3.Connection, scope_type: str | None, scope_id: str | None
) -> list[sqlite3.Row]:
    if scope_type and scope_type != "any":
        return conn.execute(
            "SELECT * FROM insight WHERE scope_type=? AND scope_id=? ORDER BY insight_id",
            (scope_type, scope_id),
        ).fetchall()
    return conn.execute("SELECT * FROM insight ORDER BY insight_id").fetchall()


def latest_evidence_ts(conn: sqlite3.Connection, wo_ids: list[str]) -> datetime | None:
    """全部证据工单的最大 created_at；任一不存在返回 None。"""
    if not wo_ids:
        return None
    marks = ",".join("?" for _ in wo_ids)
    rows = conn.execute(
        f"SELECT wo_id, created_at FROM work_order WHERE wo_id IN ({marks})", wo_ids
    ).fetchall()
    if len(rows) != len(set(wo_ids)):
        return None
    times = [datetime.fromisoformat(r["created_at"]) for r in rows]
    return max(times) if times else None


def next_insight_id(conn: sqlite3.Connection) -> str:
    n = conn.execute("SELECT COUNT(*) c FROM insight").fetchone()["c"]
    return f"INS-{n + 1:04d}"


def insert_insight(
    conn: sqlite3.Connection,
    insight_id: str,
    scope_type: str,
    scope_id: str,
    body_md: str,
    embedding: list[float],
    predicted_root_cause: str | None,
    confidence: float,
    evidence_wo_ids: list[str],
    generated_at: datetime,
    source: str,
) -> None:
    conn.execute(
        "INSERT INTO insight VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (insight_id, scope_type, scope_id, body_md, jdump(embedding),
         predicted_root_cause, confidence, 0, 0, jdump(evidence_wo_ids),
         iso(generated_at), None, source),
    )


def update_insight_stats(
    conn: sqlite3.Connection,
    insight_id: str,
    confidence: float,
    hit_count: int,
    trial_count: int,
    verified_at: datetime,
) -> None:
    conn.execute(
        "UPDATE insight SET confidence=?, hit_count=?, trial_count=?, last_verified=? "
        "WHERE insight_id=?",
        (confidence, hit_count, trial_count, iso(verified_at), insight_id),
    )


def verification_exists(conn: sqlite3.Connection, insight_id: str, wo_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM insight_verification WHERE insight_id=? AND wo_id=?",
        (insight_id, wo_id),
    ).fetchone() is not None


def insert_verification(
    conn: sqlite3.Connection,
    insight_id: str,
    wo_id: str,
    predicted: str,
    actual: str,
    hit: bool,
    before: float,
    after: float,
    verified_at: datetime,
) -> None:
    conn.execute(
        "INSERT INTO insight_verification "
        "(insight_id,wo_id,predicted,actual,hit,confidence_before,confidence_after,verified_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (insight_id, wo_id, predicted, actual, int(hit), before, after, iso(verified_at)),
    )


def in_review_queue(conn: sqlite3.Connection, insight_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM insight_review_queue WHERE insight_id=? AND resolved_at IS NULL",
        (insight_id,),
    ).fetchone() is not None


def enqueue_review(conn: sqlite3.Connection, insight_id: str, reason: str, now: datetime) -> bool:
    if in_review_queue(conn, insight_id):
        return False
    conn.execute(
        "INSERT INTO insight_review_queue VALUES (?,?,?,?)",
        (insight_id, reason, iso(now), None),
    )
    return True


def verifications_all(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM insight_verification ORDER BY verification_id"
    ).fetchall()


def wo_suggested_team(conn: sqlite3.Connection, wo_id: str) -> str | None:
    """建单时写入审计事件的班组预判（workorder_created.suggested_team）。"""
    for r in conn.execute(
        "SELECT payload FROM event_log WHERE source='agent' ORDER BY event_id"
    ):
        p = jload(r["payload"], {}) or {}
        if p.get("kind") == "workorder_created" and p.get("wo_id") == wo_id:
            return p.get("suggested_team")
    return None
