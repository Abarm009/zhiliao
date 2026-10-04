"""HTTP API：命令执行边界的 FastAPI 包装。

固定版本 0.4.0。修复：
  - V10：`_PROJECT_ROOT` 用 paths.find_project_root 定位工程根，不再锚错一层；
    `expected_version` 在 Pydantic（StrictInt）与领域层双重严格校验，拒绝 bool/None。
  - V02/V03：list/get/events/evidence/pins/history 全部走 authorization 的对象可见性。
  - V11：get_task 的成功响应与数据库事实一致；失败返回统一错误信封（不把错误包成 200）。
  - T17：SSE 只做授权的变更提示；重连用游标，游标过旧全量回读，绝不重放写命令。
  - T23：站内通知 + 到期提醒作业由服务端时钟驱动，只提醒、不自动验收。
  - R2-08：全局 tick 改为内部端点；普通用户 GET /jobs 只看到自己有权的任务。
  - R2-10：HTTP tick 复用 `executor` 注入时钟，不重新读取系统时间。
"""

from __future__ import annotations

import asyncio
import base64
import json
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import Body, FastAPI, File, Form as FormParam, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, StrictInt, field_validator

from octosense_backend import authorization as auth
from octosense_backend import idempotency as idem
from octosense_backend.appointments import AppointmentCommands
from octosense_backend.commands import API_VERSION, CommandExecutor
from octosense_backend.db import Database
from octosense_backend.errors import OctoSenseError
from octosense_backend.extended import ExtendedCommands
from octosense_backend.paths import default_db_path, default_evidence_root, find_project_root
from octosense_backend.seed import seed_demo

API_PREFIX = "/api/octosense/v1"

COMMAND_NAMES = [
    "create_draft", "update_draft", "confirm_draft", "accept_task", "assign_task",
    "propose_appointment", "confirm_appointment", "reject_appointment", "reassign",
    "start_progress", "record_progress", "submit_completion", "accept_completion",
    "reject_completion", "cancel", "bind_asset", "unbind_asset", "upload_evidence",
    "list_evidence", "download_evidence", "quarantine_evidence", "add_pin",
    "remove_pin", "list_pins", "list_tasks", "match_assets_by_code",
    "get_history_advice", "record_advice",
]

# 工程根：从本文件向上找标记，避免 parents[3] 落到 backend/（V10）
_PROJECT_ROOT = find_project_root(Path(__file__).resolve())


class CreateDraftBody(BaseModel):
    project_id: str = Field(min_length=1, max_length=64)
    problem_text: str = Field(min_length=1, max_length=2000)
    contact_name: str = Field(min_length=1, max_length=64)
    contact_info: str = Field(default="", max_length=200)
    preferred_window: str = Field(default="", max_length=200)
    category: str = Field(default="OTHER", max_length=32)
    space_id: Optional[str] = Field(default=None, max_length=64)
    idempotency_key: str = Field(min_length=1, max_length=200)

    @field_validator("project_id", "problem_text", "contact_name", "idempotency_key")
    @classmethod
    def _no_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v

    @field_validator("category")
    @classmethod
    def _cat(cls, v: str) -> str:
        if v not in auth.VALID_CATEGORIES:
            raise ValueError(f"must be one of {sorted(auth.VALID_CATEGORIES)}")
        return v


class UpdateDraftBody(BaseModel):
    """R2-03：补齐 DRAFT 字段。space_id 跨项目时被拒；category 与 project_id 不能改。"""
    expected_version: StrictInt = Field(ge=1, le=2**31 - 1)
    idempotency_key: str = Field(min_length=1, max_length=200)
    space_id: Optional[str] = Field(default=None, max_length=64)
    contact_name: Optional[str] = Field(default=None, max_length=64)
    contact_info: Optional[str] = Field(default=None, max_length=200)
    preferred_window: Optional[str] = Field(default=None, max_length=200)
    problem_text: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("contact_name", "problem_text", "idempotency_key")
    @classmethod
    def _no_blank(cls, v):
        if v is not None and isinstance(v, str) and not v.strip():
            raise ValueError("must not be blank when provided")
        return v


class CommandBody(BaseModel):
    """所有命令型路由的基础 body：expected_version 是严格正整数（拒绝 bool/None）。"""
    expected_version: StrictInt = Field(ge=1, le=2**31 - 1)
    idempotency_key: str = Field(min_length=1, max_length=200)
    assignee_id: Optional[str] = Field(default=None, max_length=64)
    reason: Optional[str] = Field(default=None, max_length=2000)
    start_at_ms: Optional[StrictInt] = Field(default=None)
    end_at_ms: Optional[StrictInt] = Field(default=None)
    completion_text: Optional[str] = Field(default=None, max_length=4000)
    note: Optional[str] = Field(default=None, max_length=4000)
    kind: Optional[str] = Field(default="NOTE", max_length=32)
    asset_id: Optional[str] = Field(default=None, max_length=64)
    appointment_id: Optional[str] = Field(default=None, max_length=64)
    disposition: Optional[str] = Field(default="REPAIRED", max_length=64)


class BindAssetBody(CommandBody):
    reason: Optional[str] = Field(default=None, max_length=2000)


class IdemBody(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=200)


class RejectAppointmentBody(BaseModel):
    expected_version: StrictInt = Field(ge=1, le=2**31 - 1)
    idempotency_key: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=2000)


class AdviceBody(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=200)
    source_kind: str = Field(min_length=1, max_length=64)
    payload: dict = Field(default_factory=dict)


def make_app(db_path: str | Path | None = None,
             evidence_root: str | Path | None = None,
             clock=None) -> FastAPI:
    if db_path is None:
        db_path = default_db_path()
    if evidence_root is None:
        evidence_root = default_evidence_root()
    db = Database(db_path)
    db.init_schema()
    seed_demo(db)
    executor = CommandExecutor(db, clock=clock)
    appt = AppointmentCommands(db, executor=executor, clock=clock)
    ext = ExtendedCommands(db, evidence_root=evidence_root, clock=clock, executor=executor)

    app = FastAPI(title="OctoSense Backend", version=API_VERSION)

    # ---------- 通用 ----------

    def actor_or_401(x_actor_id: str | None) -> str:
        if not x_actor_id or not x_actor_id.strip():
            raise HTTPException(401, detail={"code": "IDENTITY_REQUIRED",
                                             "detail": "X-Actor-Id required"})
        conn = db.conn()
        try:
            row = conn.execute(
                "SELECT 1 FROM repair_roles WHERE user_id=? LIMIT 1", (x_actor_id,)).fetchone()
            if row is None:
                raise HTTPException(401, detail={
                    "code": "IDENTITY_REQUIRED", "detail": "X-Actor-Id not registered"})
        finally:
            conn.close()
        return x_actor_id

    def call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())

    def run_exec(method_name: str, status_code: int = 200, **kwargs):
        """统一调用 CommandExecutor / ExtendedCommands 并把 CommandResult 转响应。

        幂等回放时把原结果展开到顶层，保证重试响应与首次成功**形状一致**——
        不能首次返回预约/完工信息，重试只剩 task_id 和 command。
        """
        target = getattr(executor, method_name, None)
        if target is None:
            target = getattr(ext, method_name)
        res = call(target, **kwargs)
        data = res.data if hasattr(res, "data") else res
        return JSONResponse(_replay_data(data), status_code=status_code)

    @app.exception_handler(OctoSenseError)
    async def _on_error(request: Request, exc: OctoSenseError):
        return JSONResponse(exc.to_dict(), status_code=exc.http_status)

    @app.get(API_PREFIX + "/health")
    def health():
        return {"ok": True, "service": "octosense-backend", "version": API_VERSION,
                "schema_version": 2, "commands": COMMAND_NAMES}

    # ---------- L1 创建与状态机 ----------

    @app.post(API_PREFIX + "/tasks")
    def create_draft(body: CreateDraftBody, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("create_draft", status_code=201, actor_id=actor,
                        idem_key=body.idempotency_key,
                        problem_text=body.problem_text, project_id=body.project_id,
                        contact_name=body.contact_name, contact_info=body.contact_info,
                        preferred_window=body.preferred_window, space_id=body.space_id,
                        category=body.category)

    @app.post(API_PREFIX + "/tasks/{task_id}/confirm")
    def confirm_draft(task_id: str, body: CommandBody,
                      x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("confirm_draft", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version)

    @app.post(API_PREFIX + "/tasks/{task_id}/draft")
    def update_draft(task_id: str, body: UpdateDraftBody,
                     x_actor_id: str | None = Header(default=None)):
        """R2-03 / R3-01：本人 DRAFT 阶段补充字段（space/contact/problem 等）。

        R3-01：完全收敛到 `executor.update_draft` 命令边界——同一事务内
        校验当前授权、版本、写业务行、记事件、落成功回执。重复键冲突
        不会留下半写状态；幂等回放返回与首次成功形状相同的响应。
        不允许修改 project_id / category（破坏后续指派/接单链路）。
        """
        actor = actor_or_401(x_actor_id)
        return run_exec("update_draft", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        space_id=body.space_id,
                        contact_name=body.contact_name,
                        contact_info=body.contact_info,
                        preferred_window=body.preferred_window,
                        problem_text=body.problem_text)

    @app.post(API_PREFIX + "/tasks/{task_id}/accept")
    def accept_task(task_id: str, body: CommandBody,
                    x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("accept_task", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version)

    @app.post(API_PREFIX + "/tasks/{task_id}/assign")
    def assign_task(task_id: str, body: CommandBody,
                    x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("assign_task", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        assignee_id=body.assignee_id or "", reason=body.reason or "")

    @app.post(API_PREFIX + "/tasks/{task_id}/appointments")
    def propose_appointment(task_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        if body.start_at_ms is None or body.end_at_ms is None:
            raise HTTPException(422, detail={"code": "DRAFT_MISSING_FIELD",
                                             "detail": "start_at_ms/end_at_ms required"})
        return run_exec("propose_appointment", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        start_at_ms=body.start_at_ms, end_at_ms=body.end_at_ms)

    @app.post(API_PREFIX + "/tasks/{task_id}/appointments/{appointment_id}/confirm")
    def confirm_appointment(task_id: str, appointment_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(appt.confirm_appointment, actor_id=actor,
                    idem_key=body.idempotency_key, task_id=task_id,
                    expected_version=body.expected_version,
                    appointment_id=appointment_id)
        return JSONResponse(_replay_data(data))

    @app.post(API_PREFIX + "/tasks/{task_id}/appointments/reject")
    def reject_appointment(task_id: str, body: RejectAppointmentBody,
                           x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(appt.reject_appointment, actor_id=actor,
                    idem_key=body.idempotency_key, task_id=task_id,
                    expected_version=body.expected_version, reason=body.reason)
        return JSONResponse(_replay_data(data))

    @app.post(API_PREFIX + "/tasks/{task_id}/reassign")
    def reassign(task_id: str, body: CommandBody,
                 x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(appt.reassign, actor_id=actor, idem_key=body.idempotency_key,
                    task_id=task_id, new_assignee_id=body.assignee_id or "",
                    expected_version=body.expected_version, reason=body.reason or "")
        return JSONResponse(_replay_data(data))

    @app.post(API_PREFIX + "/tasks/{task_id}/start")
    def start_progress(task_id: str, body: CommandBody,
                       x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("start_progress", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version)

    @app.post(API_PREFIX + "/tasks/{task_id}/progress")
    def record_progress(task_id: str, body: CommandBody,
                        x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("record_progress", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        note=body.note or "", kind=body.kind or "NOTE")

    @app.post(API_PREFIX + "/tasks/{task_id}/complete")
    def submit_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("submit_completion", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        completion_text=body.completion_text or "",
                        disposition=body.disposition or "REPAIRED")

    @app.post(API_PREFIX + "/tasks/{task_id}/accept-finish")
    def accept_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("accept_completion", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        reason=body.reason or "")

    @app.post(API_PREFIX + "/tasks/{task_id}/reject-finish")
    def reject_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("reject_completion", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        reason=body.reason or "")

    @app.post(API_PREFIX + "/tasks/{task_id}/cancel")
    def cancel(task_id: str, body: CommandBody,
               x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("cancel", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        reason=body.reason or "")

    # ---------- L3 设备 ----------

    @app.get(API_PREFIX + "/assets/match")
    def match_assets(project_id: str = Query(...), code: str = Query(...),
                     x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.match_assets_by_code, actor_id=actor,
                                 project_id=project_id, code=code))

    @app.get(API_PREFIX + "/spaces")
    def list_spaces(project_id: str = Query(...),
                    x_actor_id: str | None = Header(default=None)):
        """列出本项目下的服务空间，供新建/补齐草稿使用。

        R2-03：Web 表单此前没有 space 选择控件，导致 confirm_draft 返回 SPACE_REQUIRED。
        """
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            roles = auth.roles_of(conn, actor, project_id)
            if not roles:
                raise HTTPException(403, detail={
                    "code": "PERMISSION_DENIED",
                    "detail": f"actor not in project {project_id}"})
            rows = conn.execute(
                "SELECT space_id, project_id, name FROM repair_spaces "
                "WHERE project_id=? ORDER BY name", (project_id,)).fetchall()
            return JSONResponse({"project_id": project_id,
                                 "spaces": [dict(r) for r in rows]})
        finally:
            conn.close()

    @app.get(API_PREFIX + "/assets/{asset_id}")
    def asset_detail(asset_id: str, project_id: str = Query(...),
                     x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.get_asset_detail, actor_id=actor,
                                 asset_id=asset_id, project_id=project_id))

    @app.post(API_PREFIX + "/tasks/{task_id}/bind-asset")
    def bind_asset(task_id: str, body: BindAssetBody,
                   x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("bind_asset", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, asset_id=body.asset_id or "",
                        expected_version=body.expected_version, reason=body.reason or "")

    @app.post(API_PREFIX + "/tasks/{task_id}/unbind-asset")
    def unbind_asset(task_id: str, body: BindAssetBody,
                     x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return run_exec("unbind_asset", actor_id=actor, idem_key=body.idempotency_key,
                        task_id=task_id, expected_version=body.expected_version,
                        reason=body.reason or "")

    # ---------- L4 证据 ----------

    @app.post(API_PREFIX + "/tasks/{task_id}/evidence")
    async def upload_evidence(task_id: str,
                              idempotency_key: str = FormParam(...),
                              expected_version: str = FormParam(...),
                              file: UploadFile = File(...),
                              x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        # 表单里的 expected_version 必须逐个严格校验
        try:
            ev = idem.strict_positive_int(int(expected_version))
        except (TypeError, ValueError):
            raise HTTPException(422, detail={
                "code": "INVALID_VERSION",
                "detail": f"expected_version must be a strict positive integer, "
                          f"got {expected_version!r}"})
        payload_bytes = file.file.read()
        data = call(ext.upload_evidence, actor_id=actor, idem_key=idempotency_key,
                    task_id=task_id, filename=file.filename or "",
                    mime_type=file.content_type or "application/octet-stream",
                    payload=payload_bytes, expected_version=ev)
        return JSONResponse(_replay_data(data), status_code=201)

    @app.get(API_PREFIX + "/tasks/{task_id}/evidence")
    def list_evidence(task_id: str, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.list_evidence, actor_id=actor, task_id=task_id))

    @app.get(API_PREFIX + "/tasks/{task_id}/evidence/{evidence_id}")
    def download_evidence(task_id: str, evidence_id: str,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(ext.download_evidence, actor_id=actor, task_id=task_id,
                    evidence_id=evidence_id)
        return JSONResponse({
            "evidence_id": data["evidence_id"], "filename": data["filename"],
            "mime_type": data["mime_type"], "byte_size": data["byte_size"],
            "sha256": data["sha256"],
            "payload_b64": base64.b64encode(data["payload"]).decode("ascii"),
        })

    @app.post(API_PREFIX + "/tasks/{task_id}/evidence/{evidence_id}/quarantine")
    def quarantine_evidence(task_id: str, evidence_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(ext.quarantine_evidence, actor_id=actor,
                    idem_key=body.idempotency_key, task_id=task_id,
                    evidence_id=evidence_id, expected_version=body.expected_version,
                    reason=body.reason or "")
        return JSONResponse(_replay_data(data))

    # ---------- L5 收藏 / 助手 / 列表 ----------

    @app.post(API_PREFIX + "/tasks/{task_id}/pin")
    def add_pin(task_id: str, body: IdemBody, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(ext.add_pin, actor_id=actor, idem_key=body.idempotency_key,
                    task_id=task_id)
        return JSONResponse(_replay_data(data))

    @app.post(API_PREFIX + "/tasks/{task_id}/unpin")
    def remove_pin(task_id: str, body: IdemBody, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        data = call(ext.remove_pin, actor_id=actor, idem_key=body.idempotency_key,
                    task_id=task_id)
        return JSONResponse(_replay_data(data))

    @app.get(API_PREFIX + "/pins")
    def list_pins(x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.list_pins, actor_id=actor))

    @app.get(API_PREFIX + "/tasks")
    def list_tasks(project_id: str = Query(...),
                   role: str | None = Query(None),
                   status: str | None = Query(None),
                   category: str | None = Query(None),
                   limit: int = Query(50, ge=1, le=200),
                   x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.list_tasks, actor_id=actor, project_id=project_id,
                                 role_filter=role, status_filter=status,
                                 category_filter=category, limit=limit))

    @app.get(API_PREFIX + "/tasks/{task_id}/history-advice")
    def get_history_advice(task_id: str, asset_id: str | None = Query(None),
                           x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        actor = actor_or_401(x_actor_id)
        return JSONResponse(call(ext.get_history_advice, actor_id=actor, task_id=task_id,
                                 asset_id=asset_id))

    @app.post(API_PREFIX + "/tasks/{task_id}/advice")
    def record_advice(task_id: str, body: AdviceBody,
                      x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        actor = actor_or_401(x_actor_id)
        data = call(ext.record_advice, actor_id=actor, idem_key=body.idempotency_key,
                    task_id=task_id, source_kind=body.source_kind, payload=body.payload)
        return JSONResponse(_replay_data(data))

    # ---------- 只读详情 / 事件 / 通知 ----------

    @app.get(API_PREFIX + "/tasks/{task_id}")
    def get_task(task_id: str, x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?",
                               (task_id,)).fetchone()
            if row is None:
                raise HTTPException(404, detail={"code": "TASK_NOT_FOUND", "detail": task_id})
            if not auth.task_visible(conn, actor, row):
                # 不区分"不存在"与"无权"，避免枚举
                raise HTTPException(404, detail={"code": "TASK_NOT_FOUND", "detail": task_id})
            task = dict(row)
            can_see_contact = auth.can_see_contact(conn, actor, row)
            if not can_see_contact:
                task["contact_info"] = None
            events = conn.execute(
                "SELECT seq, task_id, task_version, event_type, actor_id, before_state, "
                "after_state, at_ms FROM repair_events WHERE task_id=? ORDER BY seq",
                (task_id,)).fetchall()
            appts = conn.execute(
                "SELECT appointment_id, technician_id, start_at_ms, end_at_ms, status, "
                "proposed_by, confirmed_by, reason, created_at_ms, updated_at_ms "
                "FROM repair_appointments WHERE task_id=? ORDER BY start_at_ms",
                (task_id,)).fetchall()
            evidence = conn.execute(
                "SELECT evidence_id, mime_type, byte_size, sha256, status, uploader_id, "
                "filename, created_at_ms FROM repair_evidence WHERE task_id=? "
                "ORDER BY created_at_ms", (task_id,)).fetchall()
            pins = conn.execute(
                "SELECT user_id, created_at_ms FROM repair_pins WHERE task_id=?",
                (task_id,)).fetchall()
            completions = conn.execute(
                "SELECT completion_id, round, submitter_id, completion_text, disposition, "
                "evidence_ids, created_at_ms FROM repair_completions WHERE task_id=? "
                "ORDER BY round", (task_id,)).fetchall()
            advice = conn.execute(
                "SELECT advice_id, actor_id, source_kind, payload, created_at_ms "
                "FROM repair_advice WHERE task_id=? ORDER BY created_at_ms",
                (task_id,)).fetchall()
            asset = None
            if task.get("asset_id"):
                a = conn.execute(
                    "SELECT asset_id, asset_code, display_name, source, active "
                    "FROM repair_assets WHERE asset_id=?", (task["asset_id"],)).fetchone()
                if a is not None:
                    asset = dict(a)
            space = None
            if task.get("space_id"):
                s = conn.execute(
                    "SELECT space_id, project_id, name FROM repair_spaces WHERE space_id=?",
                    (task["space_id"],)).fetchone()
                if s is not None:
                    space = dict(s)
            return JSONResponse({
                "task": task, "asset": asset, "space": space,
                "allowed_actions": _allowed_actions_for(conn, actor, task),
                "events": [_event_out(e, actor, can_see_contact) for e in events],
                "appointments": [dict(a) for a in appts],
                "evidence": [dict(ev) for ev in evidence],
                "pins": [dict(p) for p in pins],
                "completions": [dict(c) for c in completions],
                "advice": [dict(x) for x in advice],
            })
        finally:
            conn.close()

    @app.get(API_PREFIX + "/events")
    def events_since(project_id: str | None = Query(None),
                     since_seq: int = Query(0, ge=0),
                     limit: int = Query(100, ge=1, le=500),
                     x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        """HTTP 快照 + 游标。只返回当前主体可见任务的事件。"""
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            project_ids = ([project_id] if project_id
                           else sorted(auth.projects_of(conn, actor)))
            visible: set[str] = set()
            task_rows_for_visibility: dict[str, dict] = {}
            for pid in project_ids:
                if not auth.roles_of(conn, actor, pid):
                    continue
                visible |= auth.visible_task_ids(conn, actor, pid)
            if not visible:
                return JSONResponse({"events": [], "next_cursor": since_seq})
            # R2-04：拉一次任务行只为解析 can_see_contact，避免每个事件再开查询。
            task_id_rows = conn.execute(
                f"SELECT * FROM repair_tasks WHERE task_id IN ({','.join('?' * len(visible))})",
                tuple(sorted(visible))).fetchall()
            for tr in task_id_rows:
                task_rows_for_visibility[tr["task_id"]] = dict(tr)
            qmarks = ",".join("?" * len(visible))
            rows = conn.execute(
                f"SELECT seq, task_id, task_version, event_type, actor_id, before_state, "
                f"after_state, at_ms FROM repair_events WHERE seq>? AND task_id IN ({qmarks}) "
                f"ORDER BY seq LIMIT ?",
                (since_seq, *sorted(visible), limit)).fetchall()
            last = rows[-1]["seq"] if rows else since_seq
            cursor_row = conn.execute(
                "SELECT MAX(seq) AS m FROM repair_events").fetchone()
            out_events = []
            for e in rows:
                trow = task_rows_for_visibility.get(e["task_id"])
                can_see_contact = bool(trow) and auth.can_see_contact(conn, actor, trow)
                out_events.append(_event_out(e, actor, can_see_contact))
            return JSONResponse({"events": out_events,
                                 "next_cursor": last,
                                 "head_seq": cursor_row["m"] or 0})
        finally:
            conn.close()

    @app.get(API_PREFIX + "/events/stream")
    async def events_stream(request: Request, project_id: str | None = Query(None),
                            since_seq: int = Query(0, ge=0),
                            x_actor_id: str | None = Header(default=None)) -> StreamingResponse:
        """SSE：仅授权的变更提示。断线用 Last-Event-ID / cursor 续传；不回放写命令。"""
        actor = actor_or_401(x_actor_id)
        last_event_id = request.headers.get("Last-Event-ID")
        if last_event_id:
            try:
                since_seq = max(since_seq, int(last_event_id))
            except ValueError:
                pass
        conn = db.conn()
        try:
            cursor_row = conn.execute("SELECT MAX(seq) AS m FROM repair_events").fetchone()
            head = cursor_row["m"] or 0
        finally:
            conn.close()
        if since_seq == 0 or (head - since_seq) > 5000:
            # 游标过旧/缺失 → 全量刷新提示（不是写命令重放）
            since_seq = 0

        async def gen():
            cursor = since_seq
            yield f"retry: 2000\n\n"
            yield (f"event: snapshot\ndata: "
                   f"{json.dumps({'cursor': cursor, 'head_seq': head}, ensure_ascii=False)}\n\n")
            deadline = time.monotonic() + 30.0
            while time.monotonic() < deadline:
                if await request.is_disconnected():
                    break
                conn = db.conn()
                try:
                    project_ids = ([project_id] if project_id
                                   else sorted(auth.projects_of(conn, actor)))
                    visible: set[str] = set()
                    task_rows_for_visibility: dict[str, dict] = {}
                    for pid in project_ids:
                        if not auth.roles_of(conn, actor, pid):
                            continue
                        visible |= auth.visible_task_ids(conn, actor, pid)
                    if visible:
                        task_id_rows = conn.execute(
                            f"SELECT * FROM repair_tasks WHERE task_id IN "
                            f"({','.join('?' * len(visible))})",
                            tuple(sorted(visible))).fetchall()
                        for tr in task_id_rows:
                            task_rows_for_visibility[tr["task_id"]] = dict(tr)
                    rows = []
                    if visible:
                        qmarks = ",".join("?" * len(visible))
                        rows = conn.execute(
                            f"SELECT seq, task_id, task_version, event_type, actor_id, "
                            f"before_state, after_state, at_ms FROM repair_events "
                            f"WHERE seq>? AND task_id IN ({qmarks}) ORDER BY seq LIMIT 200",
                            (cursor, *sorted(visible))).fetchall()
                    for e in rows:
                        cursor = e["seq"]
                        # R2-04：长连接发送前按当前主体重新评估访问权；
                        # 主体可能在新帧之间被移除项目，不能用上一次的判断。
                        trow = task_rows_for_visibility.get(e["task_id"])
                        can_see_contact = bool(trow) and auth.can_see_contact(conn, actor, trow)
                        payload = json.dumps(_event_out(e, actor, can_see_contact),
                                              ensure_ascii=False)
                        yield f"id: {cursor}\nevent: change\ndata: {payload}\n\n"
                finally:
                    conn.close()
                await asyncio.sleep(1.0)
            yield "event: end\ndata: {}\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream",
                                   headers={"Cache-Control": "no-cache",
                                            "X-Accel-Buffering": "no"})

    @app.get(API_PREFIX + "/notifications")
    def list_notifications(x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        """R3-07：读取端必须按当前主体对任务的可见性投影；已撤权/不可见任务的通知不返回。"""
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            rows = conn.execute(
                "SELECT notification_id, task_id, kind, body, created_at_ms, read_at_ms "
                "FROM repair_notifications WHERE user_id=? ORDER BY created_at_ms DESC LIMIT 100",
                (actor,)).fetchall()
            # 仅保留当前主体仍能看见对应任务的通知；task_id 为空的（例如系统级通知）也保留。
            task_cache: dict[str, dict | None] = {}
            out = []
            for r in rows:
                tid = r["task_id"]
                if tid is None:
                    out.append(dict(r))
                    continue
                if tid not in task_cache:
                    row = conn.execute(
                        "SELECT * FROM repair_tasks WHERE task_id=?", (tid,)
                    ).fetchone()
                    task_cache[tid] = dict(row) if row else None
                t = task_cache[tid]
                if t is None:
                    continue                              # 任务已被清理
                if not auth.task_visible(conn, actor, t):
                    continue                              # 已撤权/无权
                out.append(dict(r))
            return JSONResponse({"notifications": out})
        finally:
            conn.close()

    @app.post(API_PREFIX + "/notifications/{notification_id}/read")
    def mark_read(notification_id: str, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            conn.execute(
                "UPDATE repair_notifications SET read_at_ms=? "
                "WHERE notification_id=? AND user_id=?", (_now(), notification_id, actor))
            return JSONResponse({"notification_id": notification_id, "read": True})
        finally:
            conn.close()

    @app.post(API_PREFIX + "/jobs/tick")
    def jobs_tick(x_actor_id: str | None = Header(default=None),
                  x_internal_token: str | None = Header(default=None,
                                                          alias="X-Octosense-Internal")) -> JSONResponse:
        """到期提醒作业：只生成站内通知，绝不自动验收/自动开工。

        R2-08：只允许内部调度器调用。请求必须带 `X-Octosense-Internal` 头，
        值与 `OCTOSENSE_INTERNAL_TOKEN` 环境变量一致；缺失或不匹配 → 401。
        仍要求 `X-Actor-Id` 已注册，便于审计调用者。
        """
        actor = actor_or_401(x_actor_id)
        import os as _os
        expected = _os.environ.get("OCTOSENSE_INTERNAL_TOKEN", "")
        if not expected or x_internal_token != expected:
            raise HTTPException(401, detail={
                "code": "INTERNAL_SCHEDULER_REQUIRED",
                "detail": "POST /jobs/tick is reserved for the internal scheduler; "
                          "configure OCTOSENSE_INTERNAL_TOKEN and send X-Octosense-Internal header"})
        fired = _run_due_jobs(db, clock=executor._clock)
        return JSONResponse({"fired": fired})

    @app.get(API_PREFIX + "/jobs")
    def list_jobs(x_actor_id: str | None = Header(default=None)) -> JSONResponse:
        """用户可见的作业：仅返回其当前有权访问任务的相关作业。

        R2-08：上一轮 /jobs/tick 同时把全库前 50 条 PENDING 作业返回，泄露其它项目
        的任务 ID/预约时间。现在拆为只读端点，按 actor 的项目/对象可见性过滤。
        """
        actor = actor_or_401(x_actor_id)
        conn = db.conn()
        try:
            visible: set[str] = set()
            for pid in auth.projects_of(conn, actor):
                if not auth.roles_of(conn, actor, pid):
                    continue
                visible |= auth.visible_task_ids(conn, actor, pid)
            if not visible:
                return JSONResponse({"jobs": []})
            qmarks = ",".join("?" * len(visible))
            rows = conn.execute(
                f"SELECT job_id, kind, task_id, appointment_id, fire_at_ms, status "
                f"FROM repair_jobs WHERE status='PENDING' AND task_id IN ({qmarks}) "
                f"ORDER BY fire_at_ms LIMIT 50",
                tuple(sorted(visible))).fetchall()
            return JSONResponse({"jobs": [dict(r) for r in rows]})
        finally:
            conn.close()

    return app


def _now() -> int:
    return int(time.time() * 1000)


def _replay_data(data: Any) -> Any:
    """幂等回放时把原结果展开到顶层，保持与首次成功完全一致的形状。"""
    if isinstance(data, dict) and data.get("idempotent_replay"):
        payload = dict(data)
        replay = payload.pop("result", None)
        if isinstance(replay, dict):
            payload.update(replay)
        return payload
    return data


def _mask_event_snapshot(snapshot: dict, can_see_contact: bool) -> dict:
    """对事件快照里敏感联系方式字段脱敏；其它字段保持原值以保审计。

    - 不能看联系人的主体（接单前技工 / 跨项目）永远拿不到 `contact_info`。
    - `contact_name` 不脱敏：用于事件历史中追溯报修人称呼，不属于联系方式。
    """
    if snapshot is None:
        return snapshot
    if not isinstance(snapshot, dict):
        return snapshot
    out = dict(snapshot)
    if not can_see_contact and "contact_info" in out:
        out["contact_info"] = None
    return out


def _event_out(e, actor: str, can_see_contact: bool) -> dict:
    """按当前主体感知的事件输出：详情、SSE、轮询共用同一脱敏规则。

    修复 R2-04：原 `_event_out` 直接 dump `before/after` 整张任务快照，事件流会泄露
    `contact_info`。这里对快照统一脱敏，长连接推送前重新评估主体访问权。
    """
    before = json.loads(e["before_state"]) if e["before_state"] else None
    after = json.loads(e["after_state"]) if e["after_state"] else None
    return {"seq": e["seq"], "task_id": e["task_id"], "task_version": e["task_version"],
            "event_type": e["event_type"], "actor_id": e["actor_id"],
            "before": _mask_event_snapshot(before, can_see_contact),
            "after": _mask_event_snapshot(after, can_see_contact),
            "at_ms": e["at_ms"]}


def _allowed_actions_for(conn, actor: str, task: dict) -> list[str]:
    """供 UI 使用的动作白名单（服务端推导；客户端只能渲染不能扩权）。

    R3-03：与后端 bind_asset / unbind_asset / cancel / reject_completion 共用同一
    阶段+主体矩阵，并把 `update_draft` 暴露给 DRAFT 阶段原报修人；非法主体不再展示可
    成功执行的动作。
    """
    roles = auth.roles_of(conn, actor, task["project_id"])
    if not roles:
        return []                              # 非项目成员无可执行动作
    status = task["status"]
    is_reporter = actor == task["reporter_id"]
    is_assignee = task["assignee_id"] is not None and actor == task["assignee_id"]
    is_manager = "MANAGER" in roles
    is_tech = "TECHNICIAN" in roles
    is_rep = is_reporter and "REPORTER" in roles
    out: list[str] = []
    # DRAFT：补齐/确认/绑设备/取消 —— 仅原报修人
    if status == "DRAFT":
        if is_rep:
            out += ["update_draft", "confirm_draft", "bind_asset", "cancel"]
    # OPEN：经理可绑可派；技能匹配技工可接单；原报修人可取消
    if status == "OPEN":
        if is_manager:
            out += ["bind_asset", "assign_task", "cancel"]
        if is_rep:
            out.append("cancel")
        if is_tech and auth.skill_matches(
                conn, actor, task["project_id"], task["category"]):
            out.append("accept_task")
    # ACCEPTED / SCHEDULED：当前承接技工或经理可绑/提议；原报修人可确认/拒绝/取消
    if status in {"ACCEPTED", "SCHEDULED"}:
        if is_assignee:
            out.append("bind_asset")
        if is_manager:
            out.append("bind_asset")
        if is_assignee:
            out.append("propose_appointment")
        if is_rep:
            out += ["confirm_appointment", "reject_appointment", "cancel"]
        if is_manager:
            out.append("cancel")
    if status == "SCHEDULED" and is_assignee:
        out.append("start_progress")
    if status == "SCHEDULED" and is_manager:
        out.append("reassign")
    # IN_PROGRESS：当前承接技工可处置/完工/解绑；经理需理由才能换/解
    if status == "IN_PROGRESS":
        if is_assignee:
            out += ["record_progress", "submit_completion", "unbind_asset"]
        if is_manager:
            out += ["bind_asset", "unbind_asset", "cancel"]
    # AWAITING_ACCEPTANCE：原报修人 / 经理验收或退回；承接者不能自验
    if status == "AWAITING_ACCEPTANCE" and not is_assignee:
        if is_rep:
            out += ["accept_completion", "reject_completion"]
        if is_manager:
            out += ["accept_completion", "reject_completion"]
    # 收藏：项目成员可对可见任务添加/移除收藏
    if is_rep or is_assignee or is_manager:
        out.append("pin")
    # 去重保序
    seen: set[str] = set()
    uniq: list[str] = []
    for a in out:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    return uniq


def _run_due_jobs(db: Database, clock=None) -> int:
    """服务端时钟驱动的到期提醒：去重 + 只写站内通知。

    R2-10：传入 `executor._clock` 保证 HTTP 路径与命令路径共享同一时钟，
    不让客户端通过伪造 now 绕过时间守卫。
    """
    from octosense_backend.jobs import run_due_jobs
    return run_due_jobs(db, clock=clock)
