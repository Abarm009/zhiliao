"""digest —— 每个工具返回值的一句话人话摘要（中栏流水默认显示，点击才展开 JSON）。

需求梳理 §4：原始 JSON 铺满中栏没人看得见；
这 11 条摘要文案是页面的一部分。只读 result 里的字段，不做业务判断。
"""

from __future__ import annotations

from typing import Any


def digest(name: str, result: dict[str, Any]) -> str:
    err = result.get("error")
    if err:
        return f"⚠ {err.get('message', '调用失败')}"
    fn = _DIGESTS.get(name)
    return fn(result) if fn else str(result)[:120]


def _resolve_space(r: dict) -> str:
    ms = r.get("matches", [])
    if not ms:
        return "无候选"
    head = ms[0]
    more = f" 等 {len(ms)} 个候选" if len(ms) > 1 else ""
    zone = f"-{head['zone']}" if head.get("zone") else ""
    return f"命中 {head['space_id']}（{head['building']} {head['floor']}F{zone}）{more}"


def _assets(r: dict) -> str:
    assets = r.get("assets", [])
    if not assets:
        return "无服务设备"
    parts = []
    for a in assets[:3]:
        rt = a.get("runtime") or {}
        hints = []
        if rt.get("lock_status") and rt["lock_status"] != "normal":
            hints.append(f"锁机:{rt['lock_status']}")
        if rt.get("valve_position_pct") == 0 and (rt.get("water_flow_lpm") or 0) > 0:
            hints.append(f"阀位0%·流量{rt['water_flow_lpm']}")
        tag = f"（{'，'.join(hints)}）" if hints else ""
        parts.append(f"{a['asset_id']} {a['asset_name']}{tag}")
    return f"{len(assets)} 台设备：" + "；".join(parts)


def _history(r: dict) -> str:
    wos = r.get("work_orders", [])
    if not wos:
        return f"窗口内无工单（total={r.get('total_count', 0)}）"
    closed = sum(1 for w in wos if w.get("closed"))
    span = f"{wos[-1]['created_at'][:10]} ~ {wos[0]['created_at'][:10]}"
    return f"{len(wos)} 张工单（{closed} 张已闭环，{span}）"


def _recall(r: dict) -> str:
    items = r.get("items", [])
    if not items:
        return "无相关洞察"
    parts = [
        f"{m['insight_id']}（conf {m['confidence']:.2f}"
        + (f"，命中 {m['hit_count']}/{m['trial_count']}" if m.get("trial_count") else "")
        + ("，低置信" if m.get("low_confidence") else "")
        + f"）"
        for m in items
    ]
    return "召回洞察 " + "；".join(parts)


def _write(r: dict) -> str:
    return f"写入洞察 {r.get('insight_id')}" if r.get("insight_id") else "写入失败"


def _verify(r: dict) -> str:
    hit = "✓ 命中" if r.get("hit") else "✗ 未命中"
    return (
        f"{r.get('insight_id')}：{hit}，置信 "
        f"{r.get('confidence_before')}→{r.get('confidence_after')}"
        f"（{r.get('hit_count')}/{r.get('trial_count')}）"
    )


def _judge(r: dict) -> str:
    liability = {"owner": "业主", "tenant": "租户", "shared": "共同",
                 "vendor": "供应商", "unclear": "不明确"}.get(r.get("liability"), "?")
    basis = {"contract_clause": "合同条款", "default_mapping": "默认映射",
             "no_basis": "无依据"}.get(r.get("basis"), "?")
    clauses = f"[{','.join(r['clause_ids'])}]" if r.get("clause_ids") else ""
    flag = " · 需人工" if r.get("requires_human") else ""
    return f"责任={liability}（依据{basis}{clauses}）{flag}"


def _create(r: dict) -> str:
    return f"创建工单 {r.get('wo_id')}" if r.get("wo_id") else "创建失败"


def _tech(r: dict) -> str:
    ts = r.get("technicians", [])
    if not ts:
        return "无匹配技工"
    parts = [f"{t['name']}（{'/'.join(t['skills'])}·{t['shift']}·{'在班' if t['available'] else '不在班'}）"
             for t in ts[:3]]
    return f"{len(ts)} 名候选：" + "；".join(parts)


def _notify(r: dict) -> str:
    return f"送达回执 {r.get('receipt_id')} @ {str(r.get('delivered_at'))[:19]}"


def _escalate(r: dict) -> str:
    return f"升级票据 {r.get('ticket_id')}" if r.get("ticket_id") else "升级失败"


_DIGESTS = {
    "resolve_space": _resolve_space,
    "get_assets_serving_space": _assets,
    "query_workorder_history": _history,
    "recall_memory": _recall,
    "write_memory": _write,
    "verify_memory_prediction": _verify,
    "judge_liability": _judge,
    "create_workorder": _create,
    "find_technician": _tech,
    "notify": _notify,
    "escalate_to_human": _escalate,
}
