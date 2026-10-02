"""HTTP API：L1 核心 + L3-L7 扩展命令的 FastAPI 包装。

修复：
  - N15：make_app 零参可启动（默认 db_path=runtime/octosense.db，evidence_root=runtime/evidence）
  - R-P0-3：get_task 增加项目角色校验，越权返 404
  - N05：所有命令实际使用 Pydantic 模型；expected_version 必填正整数
  - N14：代理错误由 demo-web 处理；本层只确保错误信封一致

身份：X-Actor-Id 请求头（演示用）。生产必须从可信会话/原生 Bearer 取得 actor。

L1 路径（核心状态机）：
  POST /api/octosense/v1/tasks                          create_draft
  POST /api/octosense/v1/tasks/{id}/confirm            confirm_draft
  POST /api/octosense/v1/tasks/{id}/accept             accept_task
  POST /api/octosense/v1/tasks/{id}/assign             assign_task (manager)
  POST /api/octosense/v1/tasks/{id}/appointments       propose_appointment
  POST /api/octosense/v1/tasks/{id}/appointments/{a}/confirm   confirm_appointment
  POST /api/octosense/v1/tasks/{id}/appointments/{a}/reject    reject_appointment
  POST /api/octosense/v1/tasks/{id}/appointments/reject        reject_appointment (no id)
  POST /api/octosense/v1/tasks/{id}/reassign           reassign (manager)
  POST /api/octosense/v1/tasks/{id}/start              start_progress
  POST /api/octosense/v1/tasks/{id}/progress           record_progress
  POST /api/octosense/v1/tasks/{id}/complete           submit_completion
  POST /api/octosense/v1/tasks/{id}/accept-finish      accept_completion
  POST /api/octosense/v1/tasks/{id}/reject-finish      reject_completion
  POST /api/octosense/v1/tasks/{id}/cancel             cancel

L3 设备：
  GET  /api/octosense/v1/assets/match?project_id=&code=
  POST /api/octosense/v1/tasks/{id}/bind-asset         bind_asset
  POST /api/octosense/v1/tasks/{id}/unbind-asset       unbind_asset

L4 证据：
  POST /api/octosense/v1/tasks/{id}/evidence          upload_evidence (multipart)
  GET  /api/octosense/v1/tasks/{id}/evidence          list_evidence
  GET  /api/octosense/v1/tasks/{id}/evidence/{eid}    download_evidence
  POST /api/octosense/v1/tasks/{id}/evidence/{eid}/quarantine   quarantine_evidence

L5 收藏 / 助手 / 视图：
  POST /api/octosense/v1/tasks/{id}/pin               add_pin
  POST /api/octosense/v1/tasks/{id}/unpin             remove_pin
  GET  /api/octosense/v1/pins                         list_pins
  GET  /api/octosense/v1/tasks                        list_tasks
  GET  /api/octosense/v1/tasks/{id}/history-advice    get_history_advice
  POST /api/octosense/v1/tasks/{id}/advice            record_advice

只读：
  GET  /api/octosense/v1/tasks/{id}                   get_task
  GET  /api/octosense/v1/health
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from fastapi import Body, FastAPI, File, Form as FormParam, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from octosense_backend.commands import CommandExecutor
from octosense_backend.appointments import AppointmentCommands
from octosense_backend.db import Database
from octosense_backend.errors import OctoSenseError
from octosense_backend.extended import ExtendedCommands
from octosense_backend.seed import seed_demo


# 项目根：锚到 backend/src 的 3 层上级 = 工程根
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _resolve(db: Database):
    """actor_resolver(project_id, actor_id) -> set[str] of roles in this project。"""
    def resolve(project_id: str, actor_id: str) -> set[str]:
        conn = db.conn()
        try:
            rows = conn.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
                (actor_id, project_id),
            ).fetchall()
            return {r["role"] for r in rows}
        finally:
            conn.close()
    return resolve


# ---- Pydantic 模型（模块级，避免局部类引起 forward-ref 解析失败） ----

class CreateDraftBody(BaseModel):
    project_id: str = Field(min_length=1, max_length=64)
    problem_text: str = Field(min_length=1, max_length=2000)
    contact_name: str = Field(min_length=1, max_length=64)
    contact_info: str = Field(default="", max_length=200)
    preferred_window: str = Field(default="", max_length=200)
    space_id: Optional[str] = Field(default=None, max_length=64)
    idempotency_key: str = Field(min_length=1, max_length=200)

    @field_validator("project_id", "problem_text", "contact_name", "idempotency_key")
    @classmethod
    def _no_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v


class CommandBody(BaseModel):
    """所有命令型路由的基础 body：expected_version 必填正整数。"""
    expected_version: int = Field(ge=1, le=2**31)
    idempotency_key: str = Field(min_length=1, max_length=200)
    assignee_id: Optional[str] = Field(default=None, max_length=64)
    reason: Optional[str] = Field(default=None, max_length=2000)
    start_at_ms: Optional[int] = Field(default=None)
    end_at_ms: Optional[int] = Field(default=None)
    completion_text: Optional[str] = Field(default=None, max_length=4000)
    note: Optional[str] = Field(default=None, max_length=4000)
    asset_id: Optional[str] = Field(default=None, max_length=64)
    appointment_id: Optional[str] = Field(default=None, max_length=64)
    disposition: Optional[str] = Field(default="REPAIRED", max_length=64)


class IdemBody(BaseModel):
    """仅幂等键的命令（pin 等）。"""
    idempotency_key: str = Field(min_length=1, max_length=200)


class RejectAppointmentBody(BaseModel):
    expected_version: int = Field(ge=1, le=2**31)
    idempotency_key: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=2000)


class AdviceBody(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=200)
    source_kind: str = Field(min_length=1, max_length=64)
    payload: dict = Field(default_factory=dict)


def make_app(db_path: str | Path | None = None,
             evidence_root: str | Path | None = None,
             clock=None) -> FastAPI:
    """构造 FastAPI app。

    N15：零参可启动。
      - db_path 默认 OCTOSENSE_DB 环境变量 → runtime/octosense.db（工程根下）
      - evidence_root 默认 OCTOSENSE_EVIDENCE_ROOT → runtime/evidence
      - clock 注入式服务端时钟（测试用）
    """
    if db_path is None:
        db_path = Path(os.environ.get("OCTOSENSE_DB") or (_PROJECT_ROOT / "runtime" / "octosense.db"))
    if evidence_root is None:
        evidence_root = Path(os.environ.get("OCTOSENSE_EVIDENCE_ROOT")
                             or (_PROJECT_ROOT / "runtime" / "evidence"))
    db = Database(db_path)
    db.init_schema()
    seed_demo(db)
    executor = CommandExecutor(db, _resolve(db), clock=clock)
    appt = AppointmentCommands(db)
    ext = ExtendedCommands(db, evidence_root=evidence_root, clock=clock)

    app = FastAPI(title="OctoSense Backend", version="0.3.0")

    def actor_or_400(x_actor_id: str | None) -> str:
        if not x_actor_id or not x_actor_id.strip():
            raise HTTPException(401, detail={"code": "IDENTITY_REQUIRED",
                                              "detail": "X-Actor-Id required"})
        # 区分完全未注册的 ghost 与仅在指定 project 无权
        conn = db.conn()
        try:
            any_role = conn.execute(
                "SELECT 1 FROM repair_roles WHERE user_id=? LIMIT 1",
                (x_actor_id,),
            ).fetchone()
            if any_role is None:
                raise HTTPException(401, detail={"code": "IDENTITY_REQUIRED",
                                                  "detail": "X-Actor-Id not registered"})
        finally:
            conn.close()
        return x_actor_id

    def handle_result(res, status_code: int = 200):
        if res.ok:
            return JSONResponse(res.data, status_code=status_code)
        err = res.error
        raise HTTPException(err.http_status, detail=err.to_dict())

    @app.get("/api/octosense/v1/health")
    def health():
        return {"ok": True, "service": "octosense-backend", "version": "0.3.0",
                "commands": ["create_draft", "confirm_draft", "accept_task", "assign_task",
                             "propose_appointment", "confirm_appointment", "reject_appointment",
                             "reassign", "start_progress", "record_progress", "submit_completion",
                             "accept_completion", "reject_completion", "cancel",
                             "bind_asset", "unbind_asset", "upload_evidence", "list_evidence",
                             "download_evidence", "quarantine_evidence",
                             "add_pin", "remove_pin", "list_pins", "list_tasks",
                             "match_assets_by_code", "get_history_advice", "record_advice"]}

    @app.post("/api/octosense/v1/tasks")
    def create_draft(body: CreateDraftBody, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.create_draft(
                actor_id=actor, idem_key=body.idempotency_key,
                problem_text=body.problem_text,
                project_id=body.project_id,
                contact_name=body.contact_name,
                contact_info=body.contact_info,
                preferred_window=body.preferred_window,
                space_id=body.space_id,
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res, status_code=201)

    @app.post("/api/octosense/v1/tasks/{task_id}/confirm")
    def confirm_draft(task_id: str, body: CommandBody,
                      x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.confirm_draft(actor_id=actor, idem_key=body.idempotency_key,
                                          task_id=task_id, expected_version=body.expected_version)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/accept")
    def accept_task(task_id: str, body: CommandBody,
                    x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.accept_task(actor_id=actor, idem_key=body.idempotency_key,
                                        task_id=task_id, expected_version=body.expected_version)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/assign")
    def assign_task(task_id: str, body: CommandBody,
                    x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.assign_task(actor_id=actor, idem_key=body.idempotency_key,
                                        task_id=task_id, expected_version=body.expected_version,
                                        assignee_id=body.assignee_id or "",
                                        reason=body.reason or "")
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/appointments")
    def propose_appointment(task_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.propose_appointment(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                start_at_ms=body.start_at_ms or 0, end_at_ms=body.end_at_ms or 0,
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/appointments/{appointment_id}/confirm")
    def confirm_appointment(task_id: str, appointment_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = appt.confirm_appointment(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                appointment_id=appointment_id,
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/appointments/reject")
    def reject_appointment(task_id: str, body: RejectAppointmentBody,
                           x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = appt.reject_appointment(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                reason=body.reason,
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/reassign")
    def reassign(task_id: str, body: CommandBody,
                 x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = appt.reassign(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, new_assignee_id=body.assignee_id or "",
                expected_version=body.expected_version, reason=body.reason or "",
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/start")
    def start_progress(task_id: str, body: CommandBody,
                       x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.start_progress(actor_id=actor, idem_key=body.idempotency_key,
                                          task_id=task_id, expected_version=body.expected_version)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/progress")
    def record_progress(task_id: str, body: CommandBody,
                        x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.record_progress(actor_id=actor, idem_key=body.idempotency_key,
                                       task_id=task_id, note=body.note or "",
                                       expected_version=body.expected_version)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/complete")
    def submit_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.submit_completion(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                completion_text=body.completion_text or "",
                disposition=body.disposition or "REPAIRED",
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/accept-finish")
    def accept_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.accept_completion(actor_id=actor, idem_key=body.idempotency_key,
                                              task_id=task_id,
                                              expected_version=body.expected_version,
                                              reason=body.reason or "")
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/reject-finish")
    def reject_completion(task_id: str, body: CommandBody,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.reject_completion(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                reason=body.reason or "",
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    @app.post("/api/octosense/v1/tasks/{task_id}/cancel")
    def cancel(task_id: str, body: CommandBody,
               x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            res = executor.cancel(
                actor_id=actor, idem_key=body.idempotency_key,
                task_id=task_id, expected_version=body.expected_version,
                reason=body.reason or "",
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return handle_result(res)

    # ---- L3 设备 ----

    @app.get("/api/octosense/v1/assets/match")
    def match_assets(project_id: str = Query(...), code: str = Query(...),
                     x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.match_assets_by_code(actor_id=actor, project_id=project_id, code=code)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/bind-asset")
    def bind_asset(task_id: str, body: CommandBody,
                   x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.bind_asset(actor_id=actor, idem_key=body.idempotency_key,
                                  task_id=task_id, asset_id=body.asset_id or "",
                                  expected_version=body.expected_version)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/unbind-asset")
    def unbind_asset(task_id: str, body: CommandBody,
                     x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.unbind_asset(actor_id=actor, idem_key=body.idempotency_key,
                                    task_id=task_id, expected_version=body.expected_version,
                                    reason=body.reason or "")
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    # ---- L4 证据附件 ----

    @app.post("/api/octosense/v1/tasks/{task_id}/evidence")
    async def upload_evidence(task_id: str,
                              idempotency_key: str = FormParam(...),
                              expected_version: int = FormParam(...),
                              file: UploadFile = File(...),
                              x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            payload_bytes = file.file.read()
            data = ext.upload_evidence(
                actor_id=actor, idem_key=idempotency_key, task_id=task_id,
                filename=file.filename or "", mime_type=file.content_type or "application/octet-stream",
                payload=payload_bytes, expected_version=expected_version,
            )
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data, status_code=201)

    @app.get("/api/octosense/v1/tasks/{task_id}/evidence")
    def list_evidence(task_id: str, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.list_evidence(actor_id=actor, task_id=task_id)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.get("/api/octosense/v1/tasks/{task_id}/evidence/{evidence_id}")
    def download_evidence(task_id: str, evidence_id: str,
                          x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.download_evidence(actor_id=actor, task_id=task_id, evidence_id=evidence_id)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        import base64
        return JSONResponse({
            "evidence_id": data["evidence_id"],
            "filename": data["filename"],
            "mime_type": data["mime_type"],
            "byte_size": data["byte_size"],
            "sha256": data["sha256"],
            "payload_b64": base64.b64encode(data["payload"]).decode("ascii"),
        })

    @app.post("/api/octosense/v1/tasks/{task_id}/evidence/{evidence_id}/quarantine")
    def quarantine_evidence(task_id: str, evidence_id: str, body: CommandBody,
                            x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.quarantine_evidence(actor_id=actor, idem_key=body.idempotency_key,
                                            task_id=task_id, evidence_id=evidence_id,
                                            expected_version=body.expected_version,
                                            reason=body.reason or "")
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    # ---- L5 收藏 / 助手 / 视图 ----

    @app.post("/api/octosense/v1/tasks/{task_id}/pin")
    def add_pin(task_id: str, body: IdemBody,
                x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.add_pin(actor_id=actor, idem_key=body.idempotency_key, task_id=task_id)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/unpin")
    def remove_pin(task_id: str, body: IdemBody,
                   x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.remove_pin(actor_id=actor, idem_key=body.idempotency_key, task_id=task_id)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.get("/api/octosense/v1/pins")
    def list_pins(x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.list_pins(actor_id=actor)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.get("/api/octosense/v1/tasks")
    def list_tasks(project_id: str = Query(...),
                   role: str | None = Query(None),
                   status: str | None = Query(None),
                   limit: int = Query(50, ge=1, le=200),
                   x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.list_tasks(actor_id=actor, project_id=project_id,
                                  role_filter=role, status_filter=status, limit=limit)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.get("/api/octosense/v1/tasks/{task_id}/history-advice")
    def get_history_advice(task_id: str, asset_id: str | None = Query(None),
                           x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.get_history_advice(actor_id=actor, task_id=task_id, asset_id=asset_id)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.post("/api/octosense/v1/tasks/{task_id}/advice")
    def record_advice(task_id: str, body: AdviceBody,
                      x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        try:
            data = ext.record_advice(actor_id=actor, idem_key=body.idempotency_key,
                                     task_id=task_id, source_kind=body.source_kind,
                                     payload=body.payload)
        except OctoSenseError as e:
            raise HTTPException(e.http_status, detail=e.to_dict())
        return JSONResponse(data)

    @app.get("/api/octosense/v1/tasks/{task_id}")
    def get_task(task_id: str, x_actor_id: str | None = Header(default=None)):
        actor = actor_or_400(x_actor_id)
        conn = db.conn()
        try:
            row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
            if row is None:
                raise HTTPException(404, detail={"code": "TASK_NOT_FOUND", "detail": task_id})
            project_id = row["project_id"]
            # R-P0-3：详情授权；无项目成员返 404（避免枚举）
            role_rows = conn.execute(
                "SELECT role FROM repair_roles WHERE user_id=? AND project_id=?",
                (actor, project_id),
            ).fetchall()
            if not role_rows:
                raise HTTPException(404, detail={"code": "TASK_NOT_FOUND", "detail": task_id})
            # 取所有事件 + appointments + evidence + completions
            events = conn.execute(
                "SELECT seq, event_type, actor_id, before_state, after_state, at_ms FROM repair_events "
                "WHERE task_id=? ORDER BY seq", (task_id,),
            ).fetchall()
            appts = conn.execute(
                "SELECT appointment_id, technician_id, start_at_ms, end_at_ms, status, proposed_by, confirmed_by, reason "
                "FROM repair_appointments WHERE task_id=? ORDER BY start_at_ms", (task_id,),
            ).fetchall()
            evidence = conn.execute(
                "SELECT evidence_id, mime_type, byte_size, sha256, status, uploader_id, filename, created_at_ms "
                "FROM repair_evidence WHERE task_id=? ORDER BY created_at_ms", (task_id,),
            ).fetchall()
            pins = conn.execute(
                "SELECT user_id, created_at_ms FROM repair_pins WHERE task_id=?", (task_id,),
            ).fetchall()
            completions = conn.execute(
                "SELECT completion_id, round, submitter_id, completion_text, disposition, evidence_ids, created_at_ms "
                "FROM repair_completions WHERE task_id=? ORDER BY round", (task_id,),
            ).fetchall()
            return {
                "task": dict(row),
                "events": [
                    {"seq": e["seq"], "event_type": e["event_type"], "actor_id": e["actor_id"],
                     "before": json.loads(e["before_state"]) if e["before_state"] else None,
                     "after": json.loads(e["after_state"]) if e["after_state"] else None,
                     "at_ms": e["at_ms"]} for e in events
                ],
                "appointments": [dict(a) for a in appts],
                "evidence": [dict(ev) for ev in evidence],
                "pins": [dict(p) for p in pins],
                "completions": [dict(c) for c in completions],
            }
        finally:
            conn.close()

    @app.exception_handler(OctoSenseError)
    def on_octosense_error(request: Request, exc: OctoSenseError):
        return JSONResponse(exc.to_dict(), status_code=exc.http_status)

    return app
