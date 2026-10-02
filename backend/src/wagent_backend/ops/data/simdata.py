"""仿真测试数据导入 —— data/simseed/（仿真器 git d0a9f93 的确定性产出）。

数据来源与再生成方式见 data/simseed/PROVENANCE.md。要点：
- 时间轴终点 2026-08-23，与演示种子 seed.BASE 同日对齐；
- 只导入 L1 快照 + L2 工单事件流，**ground_truth.jsonl 有意不随仓**；
- ID 天然不与手工演示种子冲突（楼栋加 BLD-SIM- 前缀，其余编号体系不同）；
- asset_runtime 为合成快照（仿真器不导出运行参数），按 asset_id 的 CRC32
  做种子保证确定性；欠费锁机状态从 L2 工单证据推导；
- L3 洞察由 L2 聚合生成（同设备同判断复发 ≥3 次），与 Agent 回放归纳同源，
  不触碰任何真值表。

开关：WAGENT_OPS_SIMSEED=0 关闭（单测默认关闭以提速；运行时默认开启）。
"""

from __future__ import annotations

import io
import json
import os
import random
import sqlite3
import zlib
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from wagent_backend.ops.data.db import DATA_DIR, iso, jdump

SIMSEED_DIR = DATA_DIR / "simseed"
L1_FILE = SIMSEED_DIR / "l1_seed.json"
L2_FILE = SIMSEED_DIR / "l2_events.jsonl"

# 仿真世界是独立园区（A/B/C 三塔），加前缀与演示种子「汇金广场」隔开
SIM_PROPERTY_ID = "PRP-SIM-001"
BUILDINGS: dict[str, tuple[str, str, int]] = {
    "A": ("BLD-SIM-A", "仿真A座", 18),
    "B": ("BLD-SIM-B", "仿真B座", 18),
    "C": ("BLD-SIM-C", "仿真C座", 18),
}
SIM_START = "2025-08-16"

# 需要补进 asset_type 表的仿真设备类型
EXTRA_ASSET_TYPES = [
    ("CHILLER", "冷水机组", "HVAC"),
]

# 欠费锁机的可见窗口：最近一次锁机判断在此天数内且无更晚的「充值恢复」
LOCK_WINDOW_DAYS = 30
# L3 归纳：统计窗口 / 最少复发次数 / 上限
INSIGHT_WINDOW_DAYS = 240
INSIGHT_MIN_REPEAT = 3
INSIGHT_LIMIT = 12


def simseed_enabled() -> bool:
    return os.environ.get("WAGENT_OPS_SIMSEED", "0") == "1"


def simseed_available() -> bool:
    return L1_FILE.exists() and L2_FILE.exists()


def _load() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    l1 = json.loads(io.open(L1_FILE, encoding="utf-8").read())
    wos = [json.loads(line)
           for line in io.open(L2_FILE, encoding="utf-8") if line.strip()]
    wos.sort(key=lambda w: w["wo_id"])
    return l1, wos


def import_sim_seed(conn: sqlite3.Connection, embedder,
                    base: datetime | None = None) -> dict[str, int] | None:
    """把仿真种子灌入库（假定紧随演示 seed() 之后调用，未灌过才动作）。

    返回统计 dict；未启用/文件缺失/已导入时返回 None。
    """
    if not simseed_enabled() or not simseed_available():
        return None
    if conn.execute("SELECT 1 FROM property WHERE property_id = ?",
                    (SIM_PROPERTY_ID,)).fetchone():
        return None  # 已导入，幂等

    l1, wos = _load()
    base = base or datetime(2026, 8, 23, 9, 0, 0)
    locked = _locked_spaces(wos, base)

    n_spaces = _l1(conn, l1, wos, locked, base)
    n_wos = _l2(conn, wos)
    n_ins = _l3(conn, embedder, wos, base)
    return {"spaces": n_spaces, "assets": len(l1["assets"]),
            "tenants": len(l1["tenants"]), "workorders": n_wos,
            "insights": n_ins}


# ── L1 事实层 ─────────────────────────────────────────────────

def _l1(conn: sqlite3.Connection, l1: dict, wos: list[dict],
        locked: set[str], base: datetime) -> int:
    conn.execute("INSERT INTO property VALUES (?,?,?,?)",
                 (SIM_PROPERTY_ID, "仿真测试园区（seed=42）", None, None))
    conn.executemany(
        "INSERT INTO building VALUES (?,?,?,?,?)",
        [(bid, SIM_PROPERTY_ID, name, floors, 0)
         for bid, name, floors in BUILDINGS.values()],
    )
    conn.executemany(
        "INSERT OR IGNORE INTO asset_type VALUES (?,?,?)", EXTRA_ASSET_TYPES)

    bmap = {k: v[0] for k, v in BUILDINGS.items()}
    conn.executemany(
        "INSERT INTO space VALUES (?,?,?,?,?,?,?,?,?)",
        [(s["space_id"], bmap[s["building_id"]], s["floor"], s["zone"],
          s["unit_no"], s["space_type"], s["area_sqm"],
          jdump(s.get("merged_from") or None), jdump(s.get("aliases") or None))
         for s in l1["spaces"]],
    )

    # FK 立即校验：先插无父设备，再逐层插子设备（FCU→AHU→CHILLER 链）
    pending = list(l1["assets"])
    inserted: set[str] = set()
    while pending:
        batch = [a for a in pending
                 if not a.get("parent_asset_id")
                 or a["parent_asset_id"] in inserted]
        if not batch:
            break
        conn.executemany(
            "INSERT INTO asset VALUES (" + ",".join(["?"] * 23) + ")",
            [_asset_row(a, bmap) for a in batch],
        )
        inserted |= {a["asset_id"] for a in batch}
        pending = [a for a in pending if a["asset_id"] not in inserted]

    rec = iso(base)
    serves = []
    for sp_id, asset_ids in l1["space_served_by_asset"].items():
        for i, aid in enumerate(asset_ids):
            role = "primary" if i == 0 else "partial"
            coverage = 1.0 if i == 0 else 0.5
            serves.append((sp_id, aid, role, coverage, SIM_START, None, rec, "simulator"))
    conn.executemany("INSERT INTO space_served_by_asset VALUES (?,?,?,?,?,?,?,?)", serves)

    _runtime(conn, l1, locked, base)

    conn.executemany(
        "INSERT INTO tenant VALUES (?,?,?)",
        [(t["tenant_id"], t["name"], t["industry"]) for t in l1["tenants"]],
    )
    conn.executemany(
        "INSERT INTO contact VALUES (?,?,?,?,?)",
        [(t["contact_id"], t["tenant_id"], t["contact_name"], None, "wecom")
         for t in l1["tenants"]],
    )
    conn.executemany(
        "INSERT INTO tenant_occupies_space VALUES (?,?,?,?,?)",
        [(tid, sp_id, SIM_START, None, rec)
         for sp_id, tid in l1["occupancy"].items()],
    )
    conn.executemany(
        "INSERT INTO technician VALUES (?,?,?,?,?,?)",
        [(t["technician_id"], t["name"], jdump(t["skills"]), jdump([]),
          bmap.get(t["home_building"]), t["shift"]) for t in l1["technicians"]],
    )
    return len(l1["spaces"])


def _asset_row(a: dict, bmap: dict[str, str]) -> tuple:
    return (
        a["asset_id"], a.get("asset_no"), a["asset_name"], a["asset_type"],
        a.get("spec_model"), a.get("brand"), bmap[a["building_id"]],
        a.get("floor"), a.get("located_in"), a.get("parent_asset_id"),
        a.get("commissioned_date"), a.get("design_life_years"),
        int(a.get("is_overdue_service") or 0), a.get("warranty_until"),
        a.get("vendor_name"), None, a.get("ownership"),
        a.get("responsible_dept"), a.get("responsible_person"), None,
        a.get("criticality"), a.get("status", "在用"), None,
    )


def _runtime(conn: sqlite3.Connection, l1: dict, locked: set[str],
             base: datetime) -> None:
    """合成运行快照 —— 确定性（CRC32(asset_id) 做随机种子），只快照 BASE 时刻。

    锁机规则（全部来自 L2 证据，不碰真值）：空间的 FCU 处于锁机集合 →
    该 FCU lock_status=billing_locked，阀位/流量归零、风机停转。
    """
    ts = iso(base - timedelta(minutes=30))
    locked_assets: set[str] = set()
    for sp_id, asset_ids in l1["space_served_by_asset"].items():
        if sp_id in locked:
            fcu = next((a for a in asset_ids if a.startswith("FCU-")), None)
            if fcu:
                locked_assets.add(fcu)

    rows = []
    for a in l1["assets"]:
        aid, atype = a["asset_id"], a["asset_type"]
        if atype not in ("FCU", "AHU"):
            continue
        rng = random.Random(zlib.crc32(aid.encode()) & 0xFFFFFFFF)
        if aid in locked_assets:
            rows.append((aid, ts, 27.1 + rng.random(), 27.5 + rng.random(), 22.0,
                         0.0, 0.0, "off", 0.0, "billing_locked"))
            continue
        supply = round(18 + rng.random() * 6, 1)
        valve = 0.0 if rng.random() < 0.02 else round(40 + rng.random() * 55, 1)
        flow = round(6 + rng.random() * 8, 1) if atype == "FCU" \
            else round(150 + rng.random() * 110, 1)
        rows.append((aid, ts, supply, round(supply + 4 + rng.random() * 4, 1),
                     round(24 + rng.random() * 2, 1), valve, flow,
                     rng.choice(["mid", "high"]), round(6 + rng.random() * 7, 1),
                     "normal"))
    conn.executemany("INSERT INTO asset_runtime VALUES (?,?,?,?,?,?,?,?,?,?)", rows)


def _locked_spaces(wos: list[dict], base: datetime) -> set[str]:
    """从 L2 推导仍处锁机状态的空间：最近锁机判断在窗口内且无更晚的充值恢复。"""
    last: dict[str, dict] = {}
    for w in wos:
        d = w.get("disposition") or {}
        sp = w["space_id"]
        if d.get("reported_cause") == "billing_suspension":
            last.setdefault(sp, {})["billing"] = w["created_at"]
        if d.get("action_taken") == "restore_after_payment":
            last.setdefault(sp, {})["restore"] = w["created_at"]
    locked = set()
    for sp, stamps in last.items():
        billing = datetime.fromisoformat(stamps.get("billing", "1970-01-01T00:00:00"))
        restore = datetime.fromisoformat(stamps.get("restore", "1970-01-01T00:00:00"))
        if billing > restore and (base - billing).days <= LOCK_WINDOW_DAYS:
            locked.add(sp)
    return locked


# ── L2 工单事件流（append-only）───────────────────────────────

def _l2(conn: sqlite3.Connection, wos: list[dict]) -> int:
    conn.executemany(
        "INSERT INTO work_order VALUES (?,?,?,?,?,?,?,?)",
        [(w["wo_id"], w["created_at"], w["space_id"], w["asset_id"],
          w.get("reporter_contact_id"), w["raw_text"], w.get("symptom"),
          w.get("urgency") or "一般") for w in wos],
    )
    evs = []
    for w in wos:
        d = w.get("disposition") or {}
        tec = d.get("technician_id")
        t0 = datetime.fromisoformat(w["created_at"])
        evs.append((w["wo_id"], iso(t0 + timedelta(hours=1)), "dispatched",
                    tec, None, None, None, None, None, None))
        evs.append((w["wo_id"], iso(t0 + timedelta(hours=2)), "diagnosed",
                    tec, d.get("reported_cause"), d.get("action_taken"), None,
                    d.get("note"), None, None))
        if d.get("closed", True):
            evs.append((w["wo_id"], iso(t0 + timedelta(hours=3)), "closed",
                        tec, None, None, None, None, None, None))
    conn.executemany(
        "INSERT INTO work_order_event (wo_id,ts,event_type,technician_id,"
        "reported_cause,action_taken,liability,note,material_cost,labor_cost) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)", evs)
    return len(wos)


# ── L3 归纳洞察（只从 L2 可见信息聚合，与回放归纳同源）─────────

def _l3(conn: sqlite3.Connection, embedder, wos: list[dict],
        base: datetime) -> int:
    horizon = iso(base - timedelta(days=INSIGHT_WINDOW_DAYS))
    groups: dict[tuple[str, str], list[dict]] = {}
    for w in wos:
        if w["created_at"] < horizon:
            continue
        cause = (w.get("disposition") or {}).get("reported_cause")
        if cause:
            groups.setdefault((w["asset_id"], cause), []).append(w)

    ranked = sorted(
        (g for g in groups.values() if len(g) >= INSIGHT_MIN_REPEAT),
        key=lambda g: (-len(g), g[0]["asset_id"]),
    )[:INSIGHT_LIMIT]

    for i, g in enumerate(ranked, 1):
        aid, cause = g[0]["asset_id"], (g[0].get("disposition") or {})["reported_cause"]
        symptom = g[-1].get("symptom") or "同症状"
        actions = Counter((w.get("disposition") or {}).get("action_taken") or "—"
                          for w in g)
        top_action = actions.most_common(1)[0][0]
        evidence = [w["wo_id"] for w in g[-5:]]
        n = len(g)
        last_ts = datetime.fromisoformat(g[-1]["created_at"])
        body = (
            f"该设备近 {INSIGHT_WINDOW_DAYS} 天内因「{symptom}」被报修 {n} 次"
            f"（{' / '.join(evidence)}）：技工历次判断均为 {cause}，历次处置以"
            f"「{top_action}」为主，未见根治记录。再次接到该点位报修时，应优先"
            f"排查 {cause} 并考虑根治性处置，避免以重复临时措施关单。"
        )
        conn.execute(
            "INSERT INTO insight VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f"INS-SIM-{i:03d}", "asset", aid, body, jdump(embedder(body)),
             cause, min(0.5 + 0.08 * (n - INSIGHT_MIN_REPEAT), 0.85), 0, 0,
             jdump(evidence), iso(last_ts + timedelta(hours=2)), None,
             "agent_replay"),
        )
    return len(ranked)
