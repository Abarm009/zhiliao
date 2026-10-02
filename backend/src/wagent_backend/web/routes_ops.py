"""ops 路由 —— 设施运维 Agent 的会话/回放/洞察 API。

    POST /api/ops/chat             发一轮报修（自动建会话；as_of 会话级固化）
    POST /api/ops/chat/stream      同上的 SSE 实时回放（事件每产生一条推一条）
    GET  /api/ops/sessions         会话列表
    GET  /api/ops/sessions/search  L5 跨会话检索（纯 Web 端点）
    GET  /api/ops/session/{sid}    单会话完整事件流（回放用）
    POST /api/ops/reset            删库重灌演示数据
    GET  /api/ops/insights         L3 洞察 + 审核队列 + 验证流水（经理视角）
    POST /api/ops/wo/{wo_id}/liability  经理手动调整责任方（append-only 事件）
"""

from __future__ import annotations

import json
import queue
import threading
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from wagent_backend.llm import client
from wagent_backend.llm.embedder import get_embedder
from wagent_backend.ops.agent import session as sess
from wagent_backend.ops.agent.events import EventLog
from wagent_backend.ops.agent.prompts import TIERS
from wagent_backend.ops.agent.runner import run_turn
from wagent_backend.ops.data import repo
from wagent_backend.ops.data.db import connect, init_db, is_empty, jload, truth_leak_check
from wagent_backend.ops.data.seed import reset as seed_reset, seed
from wagent_backend.ops.tools.context import ToolContext

router = APIRouter(prefix="/api/ops", tags=["ops"])

_JSON_COLS = ("evidence_wo_ids", "predicted_symptoms", "actions", "roles",
              "skills", "certifications", "buildings")
_DROP_COLS = ("embedding",)


def _ensure_db(conn) -> None:
    if is_empty(conn):
        init_db(conn)
        seed(conn, get_embedder())


def _row(r) -> dict:
    d = dict(r)
    for k in _DROP_COLS:
        d.pop(k, None)
    for k in _JSON_COLS:
        if k in d and isinstance(d[k], str):
            d[k] = jload(d[k])
    return d


def _get_complete():
    """依赖注入的模型流（dsh 通讯方式：stream → StreamChunk 迭代器）。"""
    try:
        client.complete_msg  # 触发配置检查
        return client.stream
    except client.LLMConfigError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None
    tier: str = "full"
    as_of: str | None = Field(
        default=None,
        description="回放模式场景时间（ISO），会话创建时固化；缺省=交互模式（系统时间）",
    )


@router.post("/chat")
def chat(req: ChatRequest, complete=Depends(_get_complete)) -> dict:
    if req.tier not in TIERS:
        raise HTTPException(status_code=400, detail=f"tier 必须是 {TIERS} 之一")
    sid, tier, as_of, log = _prepare(req)
    seq0 = len(log.events)
    ctx = ToolContext(as_of=as_of, conn=connect(), embedder=get_embedder())
    result = run_turn(complete, ctx, log, req.text, tier)
    ctx.conn.close()

    return {
        "session_id": sid,
        "tier": tier,
        "as_of": as_of.strftime("%Y-%m-%dT%H:%M:%S"),
        "result": result,
        "events": log.events[seq0:],
        "meta": log.meta(),
        "tokens": log.token_estimate(),
    }


def _prepare(req: ChatRequest) -> tuple[str, str, datetime, EventLog]:
    """chat 与 chat/stream 共用的会话准备：建/载会话，返回 (session_id, tier, as_of, log)。"""
    conn = connect()
    _ensure_db(conn)
    conn.close()
    if req.session_id:
        log = sess.load(req.session_id)
        if log is None:
            raise HTTPException(status_code=404, detail="会话不存在")
        start = next((e["data"] for e in log.events
                      if e["type"] == "session/start"), {})
        tier = start.get("tier", req.tier)
        as_of_str = start.get("as_of")
        as_of = datetime.fromisoformat(as_of_str) if as_of_str else datetime.now()
        return start.get("session_id") or req.session_id, tier, as_of, log
    as_of = datetime.fromisoformat(req.as_of) if req.as_of else datetime.now()
    sid, log = sess.create(req.tier, as_of)
    return sid, req.tier, as_of, log


@router.post("/chat/stream")
def chat_stream(req: ChatRequest, complete=Depends(_get_complete)) -> StreamingResponse:
    """SSE 实时回放（deepseek-harness 式）：事件每产生一条就推一条。

    协议：`data: {事件JSON}\n\n`；首帧 __start（带 session_id），末帧 __done
    （带 run_turn 结果 / meta / token 估算）。run_turn 在工作线程里跑，
    事件经 EventLog.on_append → queue → 本生成器流出。
    """
    if req.tier not in TIERS:
        raise HTTPException(status_code=400, detail=f"tier 必须是 {TIERS} 之一")
    sid, tier, as_of, log = _prepare(req)

    q: queue.Queue = queue.Queue()
    log.on_append = q.put
    outcome: dict = {}

    def _worker() -> None:
        # SQLite 连接必须在**使用它的线程**里创建（check_same_thread）
        ctx = ToolContext(as_of=as_of, conn=connect(), embedder=get_embedder())
        try:
            outcome["result"] = run_turn(complete, ctx, log, req.text, tier)
        except Exception as e:  # 防御：不让工作线程异常卡住流
            outcome["error"] = f"{type(e).__name__}: {e}"
        finally:
            ctx.conn.close()
            log.flush()  # 持久化屏障：轮末写-behind 缓冲全部落盘
            q.put(None)

    threading.Thread(target=_worker, daemon=True).start()

    def _gen():
        yield f"data: {json.dumps({'type': '__start', 'session_id': sid, 'tier': tier}, ensure_ascii=False)}\n\n"
        while True:
            ev = q.get()
            if ev is None:
                break
            yield f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
        yield "data: " + json.dumps({
            "type": "__done",
            "session_id": sid,
            "result": outcome.get("result"),
            "error": outcome.get("error"),
            "meta": log.meta(),
            "tokens": log.token_estimate(),
        }, ensure_ascii=False, default=str) + "\n\n"

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/teams")
def teams() -> dict:
    """项目经理派单卡：三个固定班组及其成员（按技能归组，impl.TEAM_SKILLS）。"""
    from wagent_backend.ops.tools.impl import TEAMS, TEAM_SKILLS

    conn = connect()
    _ensure_db(conn)
    techs = repo.technicians_all(conn)
    conn.close()
    out = []
    for team in TEAMS:
        skills = TEAM_SKILLS[team]
        members = [
            {"technician_id": t["technician_id"], "name": t["name"], "shift": t["shift"]}
            for t in techs if skills & set(jload(t["skills"], []) or [])
        ]
        out.append({"team": team, "members": members})
    return {"teams": out}


class DispatchRequest(BaseModel):
    team: str
    technician_id: str | None = None


@router.post("/wo/{wo_id}/dispatch")
def dispatch_wo(wo_id: str, req: DispatchRequest) -> dict:
    """项目经理派单：班组必选、人可选（选人必须属于该班组）。

    写 append-only 的 dispatched 事件（L2 事件流，不改原工单行）。
    """
    from wagent_backend.ops.tools.impl import TEAMS, TEAM_SKILLS

    conn = connect()
    _ensure_db(conn)
    try:
        if repo.wo_get(conn, wo_id) is None:
            raise HTTPException(status_code=404, detail=f"工单 {wo_id} 不存在")
        if req.team not in TEAMS:
            raise HTTPException(status_code=400, detail=f"班组必须是 {TEAMS} 之一")
        if req.technician_id:
            t = repo.technician_get(conn, req.technician_id)
            if t is None:
                raise HTTPException(status_code=404, detail=f"技工不存在：{req.technician_id}")
            if not (TEAM_SKILLS[req.team] & set(jload(t["skills"], []) or [])):
                raise HTTPException(status_code=400,
                                    detail=f"{req.technician_id} 不属于 {req.team} 班组")
        note = f"项目经理派单 → {req.team} 班组"
        if req.technician_id:
            note += f" · {req.technician_id}"
        repo.insert_wo_event(conn, wo_id, datetime.now(), "dispatched",
                             technician_id=req.technician_id, note=note)
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "wo_id": wo_id, "team": req.team, "technician_id": req.technician_id}


# 经理可手动调整的责任方（LiabilityEnum 冻结五值中去掉 shared「共同承担」）。
# 标签即经理视角下拉显示文案；owner 对租户侧口径即「物业」（业主方/物业方同一侧）。
LIABILITY_EDITABLE = {"unclear": "不明确", "tenant": "租户", "vendor": "外部", "owner": "物业"}


class LiabilityRequest(BaseModel):
    liability: str


@router.post("/wo/{wo_id}/liability")
def adjust_liability(wo_id: str, req: LiabilityRequest) -> dict:
    """经理手动调整责任方：append-only 写 liability_adjusted 事件，不改原判定记录。"""
    if req.liability not in LIABILITY_EDITABLE:
        raise HTTPException(status_code=400,
                            detail=f"责任方必须是 {sorted(LIABILITY_EDITABLE)} 之一")
    conn = connect()
    _ensure_db(conn)
    try:
        if repo.wo_get(conn, wo_id) is None:
            raise HTTPException(status_code=404, detail=f"工单 {wo_id} 不存在")
        repo.insert_wo_event(conn, wo_id, datetime.now(), "liability_adjusted",
                             liability=req.liability,
                             note=f"经理调整责任方 → {LIABILITY_EDITABLE[req.liability]}")
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "wo_id": wo_id, "liability": req.liability}


@router.get("/asset/{asset_id}")
def asset_detail(asset_id: str) -> dict:
    """设备 360 视图：台账 + 最新运行快照 + 工单列表。

    工单状态从处置流水推导（不新增字段）：无事件=待派单；
    有 dispatched 无 closed=维修中；有 closed=已完成。
    """
    conn = connect()
    _ensure_db(conn)
    try:
        a = repo.asset_get(conn, asset_id)
        if a is None:
            raise HTTPException(status_code=404, detail=f"设备不存在：{asset_id}")
        asset = _row(a)
        t = conn.execute("SELECT name, category FROM asset_type WHERE asset_type_id=?",
                         (asset["asset_type_id"],)).fetchone()
        asset["type_name"] = t["name"] if t else None
        asset["category"] = t["category"] if t else None
        rt = repo.runtime_latest(conn, asset_id, datetime.now())
        wos = []
        for w in repo.wo_list_by_scope(conn, "asset", asset_id,
                                       datetime(2000, 1, 1), datetime(2100, 1, 1)):
            types = {e["event_type"] for e in repo.wo_events(conn, w["wo_id"])}
            d = _row(w)
            d["status"] = ("已完成" if "closed" in types
                           else "维修中" if "dispatched" in types else "待派单")
            wos.append(d)
        return {"asset": asset,
                "runtime": _row(rt) if rt else None,
                "workorders": wos}
    finally:
        conn.close()


@router.get("/spaces")
def spaces() -> dict:
    """位置选择器的四级下拉数据（项目/楼栋/楼层/位置）——Agent 定位失败时由前端弹出。"""
    conn = connect()
    _ensure_db(conn)
    rows = [dict(r) for r in repo.spaces_hierarchy(conn)]
    conn.close()
    return {"spaces": rows}


@router.get("/sessions")
def sessions() -> dict:
    return {"sessions": sess.list_sessions()}


@router.get("/sessions/search")
def sessions_search(q: str = "") -> dict:
    """L5 跨会话检索（纯 Web 端点；dsh L5 在 wagent 不做成模型工具）。"""
    return {"query": q, "sessions": sess.search_sessions(q)}


@router.get("/session/{sid}")
def session_detail(sid: str) -> dict:
    log = sess.load(sid)
    if log is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    meta = log.meta()
    meta["session_id"] = meta.get("session_id") or sid
    return {"meta": meta, "events": log.events, "tokens": log.token_estimate()}


@router.post("/reset")
def reset() -> dict:
    conn = connect()
    seed_reset(conn, get_embedder())
    conn.close()
    return {"ok": True}


@router.get("/wo/{wo_id}")
def wo_detail(wo_id: str) -> dict:
    """工单溯源弹窗：工单本体 + 处置流水 + 责任 + 技工（全部来自已记录数据）。"""
    conn = connect()
    _ensure_db(conn)
    wo = repo.wo_get(conn, wo_id)
    if wo is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"工单 {wo_id} 不存在")
    events = [_row(e) for e in repo.wo_events(conn, wo_id)]
    # 派工信息在处置流水里（dispatched 事件的 technician_id）
    tech_id = next((e["technician_id"] for e in reversed(events) if e["technician_id"]), None)
    tech = repo.technician_get(conn, tech_id) if tech_id else None
    team = repo.wo_suggested_team(conn, wo_id)
    conn.close()
    return {
        "work_order": _row(wo),
        "events": events,
        "technician": _row(tech) if tech else None,
        "suggested_team": team,
    }


@router.get("/insights")
def insights() -> dict:
    conn = connect()
    _ensure_db(conn)
    rows = []
    for r in repo.insight_list(conn, None, None):
        d = _row(r)
        d["in_review_queue"] = repo.in_review_queue(conn, r["insight_id"])
        d["verifications"] = [
            _row(v) for v in repo.verifications_all(conn)
            if v["insight_id"] == r["insight_id"]
        ]
        rows.append(d)
    leaks = truth_leak_check(conn)
    conn.close()
    return {"insights": rows, "truth_leaks": leaks}
