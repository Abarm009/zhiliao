"""扩展命令：设备、证据、收藏、处置建议、列表视图。

修复：
  - V02/V03：list_tasks / get_history_advice / 证据 / 收藏 全部改用
    `authorization.task_visible` 的同一对象可见性规则；role 过滤只能缩小。
  - V04：`_check_role` 真正检查 allowed；IN_PROGRESS 换设备必须同项目经理 + 理由，
    并保存旧值/新值/操作者。
  - V07：普通编码走 asset_code；`asset:<asset_id>` 走稳定 asset_id，再校验项目与归档。
  - V08：upload 用暂存→原子改名；completion 侧另有附件完整性校验。
  - V09：绑定必须满足“服务空间—设备”有效服务关系，不只是同项目。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Callable

from octosense_backend import authorization as auth
from octosense_backend import idempotency as idem
from octosense_backend.commands import CommandExecutor, _EVIDENCE_MIME_PREFIXES
from octosense_backend.db import Database
from octosense_backend.errors import (
    AssetArchived,
    AssetNotFound,
    DraftMissingField,
    EvidenceNotFound,
    EvidenceQuarantined,
    EvidenceTooLarge,
    IllegalTransition,
    InvalidKind,
    InvalidProjectReference,
    OctoSenseError,
    PermissionDenied,
    ServiceRelationMissing,
    SpaceRequired,
    TaskNotFound,
    VersionConflict,
)

# 命令级源状态
BIND_ALLOWED_STATES = {"DRAFT", "OPEN", "ACCEPTED", "SCHEDULED", "IN_PROGRESS"}

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


def _uuid() -> str:
    return uuid.uuid4().hex


def safe_filename(name: str) -> str:
    """去掉路径分隔与危险字符，避免目录穿越。"""
    base = os.path.basename(name or "")
    base = _SAFE_NAME.sub("_", base)
    return base[:120] or "unnamed"


class ExtendedCommands:
    def __init__(self, db: Database, evidence_root=None,
                 clock: Callable[[], int] | None = None,
                 executor: CommandExecutor | None = None,
                 max_evidence_bytes: int | None = None):
        self.db = db
        from octosense_backend.paths import default_evidence_root
        self.evidence_root = Path(evidence_root) if evidence_root else default_evidence_root()
        self.evidence_root.mkdir(parents=True, exist_ok=True)
        self.max_evidence_bytes = int(
            max_evidence_bytes
            if max_evidence_bytes is not None
            else os.environ.get("OCTOSENSE_EVIDENCE_MAX_BYTES", str(10 * 1024 * 1024)))
        self._clock = clock
        self.executor = executor or CommandExecutor(db, clock=clock)
        if clock is not None:
            self.executor._clock = clock

    # ---------- helpers ----------

    def now(self) -> int:
        return int(self._clock() if self._clock else __import__("time").time() * 1000)

    def _run(self, *, command: str, actor_id: str, idem_key: str, task_id: str | None,
             expected_version: int | None, params: dict, body: Callable[[Any, str | None], dict]):
        return self.executor._run(command=command, actor_id=actor_id, idem_key=idem_key,
                                  task_id=task_id, expected_version=expected_version,
                                  params=params, body=body)

    def _resolve(self, conn, task_id: str) -> dict:
        row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        return dict(row)

    def _check_role(self, conn, project_id: str, actor_id: str, allowed: set[str]) -> set[str]:
        """真正检查 allowed（修复 V04）：旧实现只判断项目成员存在。"""
        return self.executor._check_actor_role(project_id, actor_id, allowed)

    def _resolve_actor(self, conn, project_id: str, actor_id: str, allowed: set[str]) -> set[str]:
        roles = self.executor._check_actor_role(project_id, actor_id, allowed,
                                                allow_manager=True)
        return roles

    # ---------- 设备（T07/T08/T09） ----------

    def resolve_asset(self, conn, project_id: str, code: str) -> dict:
        """普通编码 → asset_code；`asset:<asset_id>` → 稳定 asset_id。"""
        raw = (code or "").strip()
        if not raw or len(raw) > 128:
            raise OctoSenseError("ASSET_CODE_INVALID", "code empty or too long", http_status=422)
        if raw.startswith("asset:"):
            asset_id = raw[len("asset:"):].strip()
            if not asset_id:
                raise OctoSenseError("ASSET_CODE_INVALID", "asset: payload empty",
                                     http_status=422)
            row = conn.execute(
                "SELECT asset_id, project_id, asset_code, display_name, source, active "
                "FROM repair_assets WHERE asset_id=?", (asset_id,)).fetchone()
            if row is None:
                raise AssetNotFound(f"asset_id {asset_id} not found")
            if row["project_id"] != project_id:
                raise AssetNotFound("asset belongs to another project")
            if not row["active"]:
                raise AssetArchived(asset_id)
            return dict(row)
        rows = conn.execute(
            "SELECT asset_id, project_id, asset_code, display_name, source, active "
            "FROM repair_assets WHERE asset_code=?", (raw,)).fetchall()
        hits = [dict(r) for r in rows
                if r["project_id"] == project_id and r["active"]]
        if not hits:
            raise AssetNotFound(f"no active asset in project {project_id} with code {raw}")
        return hits[0] if len(hits) == 1 else {"matches": hits}

    def match_assets_by_code(self, actor_id: str, project_id: str, code: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            self._resolve_actor(cur, project_id, actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            raw = (code or "").strip()
            if raw.startswith("asset:"):
                asset = self.resolve_asset(cur, project_id, raw)
                return {"code": raw, "matches": [asset], "resolved_by": "asset_id"}
            if not raw or len(raw) > 128:
                raise OctoSenseError("ASSET_CODE_INVALID", "code empty or too long",
                                     http_status=422)
            rows = cur.execute(
                "SELECT asset_id, asset_code, display_name, source, active "
                "FROM repair_assets WHERE project_id=? AND asset_code=?", (project_id, raw)
            ).fetchall()
            hits = []
            for r in rows:
                if not r["active"]:
                    continue
                hits.append({"asset_id": r["asset_id"], "asset_code": r["asset_code"],
                             "display_name": r["display_name"], "source": r["source"]})
            if not hits:
                raise AssetNotFound(f"no active asset in this project with code {raw}")
            return {"code": raw, "matches": hits, "resolved_by": "asset_code"}

    def bind_asset(self, actor_id: str, idem_key: str, task_id: str,
                   asset_id: str, expected_version: int, reason: str = "") -> dict:
        idem.strict_positive_int(expected_version)
        if not asset_id:
            raise DraftMissingField("asset_id required")

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            if task["status"] not in BIND_ALLOWED_STATES:
                raise IllegalTransition(
                    f"cannot bind asset in terminal state {task['status']}")
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            asset = conn.execute(
                "SELECT asset_id, project_id, active, asset_code, display_name, source "
                "FROM repair_assets WHERE asset_id=?", (asset_id,)).fetchone()
            if asset is None:
                raise AssetNotFound(asset_id)
            if asset["project_id"] != task["project_id"]:
                raise InvalidProjectReference("asset not in task's project")
            if not asset["active"]:
                raise AssetArchived(asset_id)
            status = task["status"]
            # R3-02：第一次写操作必须先验证主体仍是当前项目成员。
            # 撤权后即使 actor_id 与原报修人/原承接者匹配，roles_of 仍返回空集。
            # 下面按状态做矩阵检查前，先确保 actor 仍是该项目成员：
            member_roles = self._check_role(
                conn, task["project_id"], actor_id,
                {"REPORTER", "TECHNICIAN", "MANAGER"})
            is_manager = "MANAGER" in member_roles
            # R2-09 / R3-05：按业务基线显式按阶段定义主体权限矩阵：
            #   DRAFT                              → 原报修人
            #   OPEN                               → 本项目经理
            #   ACCEPTED / SCHEDULED               → 当前承接技工 或 本项目经理
            #   IN_PROGRESS                        → 本项目经理（理由必填）
            #   AWAITING_ACCEPTANCE/COMPLETED/CANCELLED → 拒绝（只能走合法退回流程）
            is_reporter = actor_id == task["reporter_id"]
            is_assignee = (task["assignee_id"] is not None
                           and actor_id == task["assignee_id"])
            if status == "DRAFT":
                if not (is_reporter and "REPORTER" in member_roles):
                    raise PermissionDenied("only original reporter can bind asset in DRAFT")
            elif status == "OPEN":
                if not is_manager:
                    raise PermissionDenied("only project manager can bind asset in OPEN")
            elif status in {"ACCEPTED", "SCHEDULED"}:
                if not (is_assignee or is_manager):
                    raise PermissionDenied(
                        "only current assignee or manager can bind asset at "
                        f"{status} stage")
            elif status == "IN_PROGRESS":
                # V04：仅同项目经理 + 必填理由
                if not is_manager:
                    raise PermissionDenied(
                        "only project manager can rebind asset during IN_PROGRESS")
                if not (reason or "").strip():
                    raise DraftMissingField(
                        "changing the asset during IN_PROGRESS requires a reason")
            else:
                # AWAITING_ACCEPTANCE / COMPLETED / CANCELLED
                raise IllegalTransition(
                    f"cannot rebind asset in {status} stage; must cancel + reopen")
            # V09/T08：必须存在有效“服务空间—设备”服务关系
            if not task.get("space_id"):
                raise SpaceRequired(
                    "bind an asset only after the task has a confirmed service space")
            if not auth.service_relation_ok(conn, asset_id, task["space_id"]):
                raise ServiceRelationMissing(
                    f"asset {asset['asset_code']} does not service space "
                    f"{task['space_id']}; same install location is not a service relation")
            old_asset_id = task["asset_id"]
            conn.execute(
                "UPDATE repair_tasks SET asset_id=?, version=version+1, updated_at_ms=? "
                "WHERE task_id=?", (asset_id, self.now(), task_id))
            new_ver = task["version"] + 1
            self.executor._record_event(
                conn, task_id, new_ver, "bind_asset", actor_id,
                {"asset_id": old_asset_id, "status": status},
                {"asset_id": asset_id, "asset_code": asset["asset_code"],
                 "reason": reason or None, "operator": actor_id,
                 "services_space_id": task["space_id"]})
            return {"task_id": task_id, "asset_id": asset_id,
                    "asset_code": asset["asset_code"], "task_version": new_ver,
                    "previous_asset_id": old_asset_id, "reason": reason or None}

        res = self._run(command="bind_asset", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "asset_id": asset_id,
                                "expected_version": expected_version,
                                "reason": reason or ""},
                        body=body)
        return res.data

    def unbind_asset(self, actor_id: str, idem_key: str, task_id: str,
                     expected_version: int, reason: str) -> dict:
        idem.strict_positive_int(expected_version)
        if not (reason or "").strip():
            raise DraftMissingField("reason required")

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            if task["status"] not in BIND_ALLOWED_STATES:
                raise IllegalTransition(f"cannot unbind asset in terminal state {task['status']}")
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            # R3-02：先验证仍是当前项目成员；R3-05：unbind 与 bind 共用阶段/主体矩阵
            member_roles = self._check_role(
                conn, task["project_id"], actor_id,
                {"REPORTER", "TECHNICIAN", "MANAGER"})
            is_manager = "MANAGER" in member_roles
            is_reporter = actor_id == task["reporter_id"]
            is_assignee = (task["assignee_id"] is not None
                           and actor_id == task["assignee_id"])
            status = task["status"]
            if status == "DRAFT":
                if not (is_reporter and "REPORTER" in member_roles):
                    raise PermissionDenied(
                        "only original reporter can unbind asset in DRAFT")
            elif status == "OPEN":
                if not is_manager:
                    raise PermissionDenied(
                        "only project manager can unbind asset in OPEN")
            elif status in {"ACCEPTED", "SCHEDULED"}:
                if not (is_assignee or is_manager):
                    raise PermissionDenied(
                        "only current assignee or manager can unbind asset at "
                        f"{status} stage")
            elif status == "IN_PROGRESS":
                if not is_manager:
                    raise PermissionDenied(
                        "only project manager can unbind asset during IN_PROGRESS")
                if not (reason or "").strip():
                    raise DraftMissingField(
                        "unbinding asset during IN_PROGRESS requires a reason")
            else:
                raise IllegalTransition(
                    f"cannot unbind asset in {status} stage; must cancel + reopen")
            old_asset_id = task["asset_id"]
            conn.execute(
                "UPDATE repair_tasks SET asset_id=NULL, version=version+1, updated_at_ms=? "
                "WHERE task_id=?", (self.now(), task_id))
            new_ver = task["version"] + 1
            self.executor._record_event(
                conn, task_id, new_ver, "unbind_asset", actor_id,
                {"asset_id": old_asset_id, "status": task["status"]},
                {"asset_id": None, "reason": reason, "operator": actor_id})
            return {"task_id": task_id, "asset_id": None, "task_version": new_ver,
                    "previous_asset_id": old_asset_id, "reason": reason}

        res = self._run(command="unbind_asset", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "expected_version": expected_version,
                                "reason": reason},
                        body=body)
        return res.data

    def get_asset_detail(self, actor_id: str, asset_id: str, project_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            self._resolve_actor(cur, project_id, actor_id,
                                {"REPORTER", "TECHNICIAN", "MANAGER"})
            row = cur.execute(
                "SELECT asset_id, project_id, asset_code, display_name, source, active "
                "FROM repair_assets WHERE asset_id=?", (asset_id,)).fetchone()
            if row is None:
                raise AssetNotFound(asset_id)
            if row["project_id"] != project_id:
                raise InvalidProjectReference("asset not in project")
            return {"asset": dict(row),
                    "services_space_ids": auth.asset_services(cur, asset_id),
                    "installed_at_space_ids": auth.asset_locations(cur, asset_id)}

    # ---------- 证据附件（T19/T30） ----------

    def upload_evidence(self, actor_id: str, idem_key: str, task_id: str,
                        filename: str, mime_type: str, payload: bytes,
                        expected_version: int) -> dict:
        idem.strict_positive_int(expected_version)
        filename = safe_filename(filename)
        if not filename or not (filename or "").strip():
            raise DraftMissingField("filename required")
        if not payload:
            raise DraftMissingField("payload empty")
        if len(payload) > self.max_evidence_bytes:
            raise EvidenceTooLarge(f"max {self.max_evidence_bytes} bytes")
        if not any(mime_type.startswith(p) for p in _EVIDENCE_MIME_PREFIXES):
            raise OctoSenseError("EVIDENCE_MIME_REJECTED", mime_type, http_status=422)
        sha = hashlib.sha256(payload).hexdigest()

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            is_reporter = actor_id == task["reporter_id"]
            is_assignee = (task["assignee_id"] is not None
                           and actor_id == task["assignee_id"])
            is_manager = "MANAGER" in roles
            if not (is_reporter or is_assignee or is_manager):
                raise PermissionDenied(
                    "only reporter, current assignee, or manager can upload evidence")
            existing = conn.execute(
                "SELECT COUNT(*) AS n FROM repair_evidence WHERE task_id=? AND status='READY'",
                (task_id,)).fetchone()["n"]
            if existing >= 10:
                raise OctoSenseError("EVIDENCE_QUOTA", "max 10 evidence items per task",
                                     http_status=422)
            evidence_id = _uuid()
            target_dir = self.evidence_root / task_id
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / f"{evidence_id}.bin"
            tmp_path = target_dir / f"{evidence_id}.tmp"
            try:
                tmp_path.write_bytes(payload)
                tmp_path.rename(target_path)
            except Exception:
                for p in (tmp_path, target_path):
                    try:
                        if p.exists():
                            p.unlink()
                    except OSError:
                        pass
                raise
            conn.execute(
                "INSERT INTO repair_evidence (evidence_id, task_id, uploader_id, filename, "
                "mime_type, byte_size, sha256, storage_path, status, created_at_ms) "
                "VALUES (?,?,?,?,?,?,?,?, 'READY', ?)",
                (evidence_id, task_id, actor_id, filename, mime_type, len(payload), sha,
                 str(target_path), self.now()))
            return {"evidence_id": evidence_id, "task_id": task_id,
                    "filename": filename, "byte_size": len(payload), "sha256": sha,
                    "task_version": task["version"]}

        res = self._run(command="upload_evidence", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "expected_version": expected_version,
                                "filename": filename, "mime_type": mime_type, "sha256": sha},
                        body=body)
        return res.data

    def list_evidence(self, actor_id: str, task_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            rows = cur.execute(
                "SELECT evidence_id, filename, mime_type, byte_size, sha256, status, "
                "uploader_id, created_at_ms FROM repair_evidence WHERE task_id=? "
                "ORDER BY created_at_ms", (task_id,)).fetchall()
            return {"task_id": task_id, "evidence": [dict(r) for r in rows]}

    def download_evidence(self, actor_id: str, task_id: str, evidence_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            ev = cur.execute(
                "SELECT * FROM repair_evidence WHERE evidence_id=? AND task_id=?",
                (evidence_id, task_id)).fetchone()
            if ev is None:
                raise EvidenceNotFound(evidence_id)
            if ev["status"] == "QUARANTINED":
                raise EvidenceQuarantined(evidence_id)
            path = Path(ev["storage_path"])
            if not path.exists():
                raise EvidenceNotFound(f"{evidence_id} file missing from storage")
            payload = path.read_bytes()
            if hashlib.sha256(payload).hexdigest() != ev["sha256"]:
                raise EvidenceQuarantined(f"sha mismatch on {evidence_id}")
            return {"evidence_id": evidence_id, "filename": ev["filename"],
                    "mime_type": ev["mime_type"], "byte_size": ev["byte_size"],
                    "payload": payload, "sha256": ev["sha256"]}

    def quarantine_evidence(self, actor_id: str, idem_key: str, task_id: str,
                            evidence_id: str, expected_version: int, reason: str) -> dict:
        idem.strict_positive_int(expected_version)
        if not (reason or "").strip():
            raise DraftMissingField("reason required")

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            # R3-02：第一次写必须先验证主体仍是当前项目成员
            roles = auth.roles_of(conn, actor_id, task["project_id"])
            if not roles:
                raise PermissionDenied(f"actor not in project {task['project_id']}")
            is_reporter = actor_id == task["reporter_id"] and "REPORTER" in roles
            is_manager = "MANAGER" in roles
            if not (is_reporter or is_manager):
                raise PermissionDenied("only reporter or manager can quarantine evidence")
            ev = conn.execute(
                "SELECT evidence_id FROM repair_evidence WHERE evidence_id=? AND task_id=?",
                (evidence_id, task_id)).fetchone()
            if ev is None:
                raise EvidenceNotFound(evidence_id)
            changed = conn.execute(
                "UPDATE repair_evidence SET status='QUARANTINED' "
                "WHERE evidence_id=? AND task_id=?", (evidence_id, task_id)).rowcount
            if changed != 1:
                raise EvidenceNotFound(evidence_id)
            self.executor._record_event(
                conn, task_id, task["version"] + 1, "quarantine_evidence", actor_id,
                {"evidence_id": evidence_id}, {"status": "QUARANTINED", "reason": reason})
            conn.execute(
                "UPDATE repair_tasks SET version=version+1, updated_at_ms=? WHERE task_id=?",
                (self.now(), task_id))
            return {"evidence_id": evidence_id, "status": "QUARANTINED",
                    "reason": reason, "task_version": task["version"] + 1}

        res = self._run(command="quarantine_evidence", actor_id=actor_id, idem_key=idem_key,
                        task_id=task_id, expected_version=expected_version,
                        params={"task_id": task_id, "evidence_id": evidence_id,
                                "expected_version": expected_version, "reason": reason},
                        body=body)
        return res.data

    # ---------- 收藏（T30） ----------

    def add_pin(self, actor_id: str, idem_key: str, task_id: str) -> dict:
        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            conn.execute(
                "INSERT OR IGNORE INTO repair_pins (project_id, user_id, task_id, created_at_ms) "
                "VALUES (?,?,?,?)", (task["project_id"], actor_id, task_id, self.now()))
            return {"task_id": task_id, "pinned": True, "task_version": task["version"]}

        return self._run(command="add_pin", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=None,
                         params={"task_id": task_id}, body=body).data

    def remove_pin(self, actor_id: str, idem_key: str, task_id: str) -> dict:
        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            removed = conn.execute(
                "DELETE FROM repair_pins WHERE user_id=? AND task_id=?",
                (actor_id, task_id)).rowcount
            return {"task_id": task_id, "pinned": False, "removed": bool(removed),
                    "task_version": task["version"]}

        return self._run(command="remove_pin", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=None,
                         params={"task_id": task_id}, body=body).data

    def list_pins(self, actor_id: str) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            rows = cur.execute(
                "SELECT p.task_id, p.created_at_ms, t.status, t.problem_text, t.project_id, "
                "t.category, t.reporter_id, t.assignee_id, t.version AS task_version "
                "FROM repair_pins p JOIN repair_tasks t ON t.task_id=p.task_id "
                "WHERE p.user_id=? ORDER BY p.created_at_ms DESC",
                (actor_id,)).fetchall()
            pins = [dict(r) for r in rows
                    if auth.task_visible(cur, actor_id, r)]
            return {"pins": pins}

    # ---------- 处置记录 ----------

    def record_progress(self, actor_id: str, idem_key: str, task_id: str,
                        note: str, kind: str, expected_version: int) -> dict:
        """IN_PROGRESS 期间记处置；子类 INSPECTION/REPAIR/WAITING_PARTS/NOTE。"""
        idem.strict_positive_int(expected_version)
        if not (note or "").strip():
            raise DraftMissingField("note required")
        if kind not in {"INSPECTION", "REPAIR", "WAITING_PARTS", "NOTE"}:
            raise InvalidKind(kind)

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            if task["status"] != "IN_PROGRESS":
                raise IllegalTransition(
                    f"record_progress requires IN_PROGRESS, got {task['status']}")
            if task["assignee_id"] != actor_id:
                raise PermissionDenied("only current assignee can record progress")
            # R2-05：除"仍是承接者"之外，必须仍是本项目内的 TECHNICIAN；
            # 被移出项目或撤掉角色 → 拒绝，避免撤权后仍能写。
            roles = self.executor._check_actor_role(
                task["project_id"], actor_id, {"TECHNICIAN"}, allow_manager=False)
            if expected_version != task["version"]:
                raise VersionConflict(
                    f"task version {task['version']} != expected {expected_version}")
            new_ver = task["version"] + 1
            conn.execute("UPDATE repair_tasks SET version=?, updated_at_ms=? WHERE task_id=?",
                         (new_ver, self.now(), task_id))
            self.executor._record_event(
                conn, task_id, new_ver, "record_progress", actor_id,
                {"status": task["status"]},
                {"note": note, "kind": kind, "operator": actor_id})
            return {"task_id": task_id, "task_version": new_ver, "note": note, "kind": kind}

        return self._run(command="record_progress", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=expected_version,
                         params={"task_id": task_id, "expected_version": expected_version,
                                 "note": note, "kind": kind},
                         body=body).data

    # ---------- 列表与历史建议（V02/V03） ----------

    def list_tasks(self, actor_id: str, project_id: str,
                   role_filter: str | None = None,
                   status_filter: str | None = None,
                   category_filter: str | None = None,
                   limit: int = 50) -> dict:
        """服务端按主体推导可见集合；客户端 role 只能在该主体角色内再缩小。"""
        with self.db.tx() as conn:
            cur = conn.cursor()
            roles = auth.roles_of(cur, actor_id, project_id)
            if not roles:
                raise PermissionDenied(f"actor not in project {project_id}")
            effective = auth.narrow_role(cur, actor_id, project_id, role_filter)
            if effective is None:
                # 服务端按主体最严可见范围推导
                if "MANAGER" in roles and "TECHNICIAN" not in roles and "REPORTER" not in roles:
                    effective = "MANAGER"
                elif "TECHNICIAN" in roles and "REPORTER" not in roles:
                    effective = "TECHNICIAN"
                elif "REPORTER" in roles and "TECHNICIAN" not in roles:
                    effective = "REPORTER"
                # 多角色：不加过滤，取并集（下面用 task_visible 统一判定）
            rows = cur.execute(
                "SELECT * FROM repair_tasks WHERE project_id=?", (project_id,)).fetchall()
            out = []
            for r in rows:
                if not auth.task_visible(cur, actor_id, r):
                    continue
                if effective == "REPORTER" and r["reporter_id"] != actor_id:
                    continue
                if effective == "TECHNICIAN" and not (
                        r["assignee_id"] == actor_id
                        or (r["status"] == "OPEN"
                            and auth.skill_matches(cur, actor_id, project_id, r["category"]))):
                    continue
                if status_filter and r["status"] != status_filter:
                    continue
                if category_filter and r["category"] != category_filter:
                    continue
                masked = dict(r)
                if not auth.can_see_contact(cur, actor_id, r):
                    masked["contact_info"] = None
                out.append({
                    "task_id": masked["task_id"], "project_id": masked["project_id"],
                    "status": masked["status"], "version": masked["version"],
                    "category": masked["category"], "problem_text": masked["problem_text"],
                    "reporter_id": masked["reporter_id"], "assignee_id": masked["assignee_id"],
                    "asset_id": masked["asset_id"], "space_id": masked["space_id"],
                    "contact_name": masked["contact_name"],
                    "contact_info": masked["contact_info"],
                    "preferred_window": masked["preferred_window"],
                    "created_at_ms": masked["created_at_ms"],
                    "updated_at_ms": masked["updated_at_ms"],
                })
            out.sort(key=lambda x: x["updated_at_ms"], reverse=True)
            return {"project_id": project_id, "tasks": out[: int(limit)],
                    "count": min(len(out), int(limit)), "effective_role": effective,
                    "roles": sorted(roles)}

    def get_history_advice(self, actor_id: str, task_id: str,
                           asset_id: str | None = None) -> dict:
        with self.db.tx() as conn:
            cur = conn.cursor()
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            roles = auth.roles_of(cur, actor_id, task["project_id"])
            is_manager = "MANAGER" in roles
            can_see_contact = auth.can_see_contact(cur, actor_id, task)
            target_asset = asset_id or task["asset_id"]
            if target_asset is None:
                return {"task_id": task_id, "asset_id": None, "history": [], "events": [],
                        "advice": "未绑定设备，无历史依据"}
            asset_row = cur.execute(
                "SELECT project_id, active, asset_code, display_name FROM repair_assets "
                "WHERE asset_id=?", (target_asset,)).fetchone()
            if (asset_row is None or asset_row["project_id"] != task["project_id"]
                    or not asset_row["active"]):
                raise OctoSenseError("INVALID_PROJECT_REFERENCE",
                                     "asset not visible to this task", http_status=404)
            sql = ("SELECT task_id, project_id, reporter_id, assignee_id, status, "
                   "problem_text, category, created_at_ms, updated_at_ms FROM repair_tasks "
                   "WHERE project_id=? AND asset_id=? AND task_id<>?")
            params: list[Any] = [task["project_id"], target_asset, task_id]
            if not is_manager:
                sql += " AND (reporter_id=? OR assignee_id=?)"
                params.extend([actor_id, actor_id])
            sql += " ORDER BY updated_at_ms DESC LIMIT 10"
            history = cur.execute(sql, tuple(params)).fetchall()
            # 历史明细也按当前主体过滤（防止跨项目/无关系任务经 asset_id 泄漏）
            visible_history = [dict(h) for h in history
                               if auth.task_visible(cur, actor_id, h) or is_manager]
            events = cur.execute(
                "SELECT seq, event_type, actor_id, after_state, at_ms FROM repair_events "
                "WHERE task_id=? ORDER BY seq DESC LIMIT 20", (task_id,)).fetchall()
            # R3-04：events 嵌套字段也按当前主体授权做脱敏；
            # 不能因为是 history-advice 端点就把 after_state 原样回写。
            def _mask_event(snapshot):
                if snapshot is None or not isinstance(snapshot, dict):
                    return snapshot
                if can_see_contact:
                    return snapshot
                out = dict(snapshot)
                if "contact_info" in out:
                    out["contact_info"] = None
                return out
            masked_events = []
            for e in events:
                ed = dict(e)
                try:
                    after = json.loads(ed["after_state"]) if ed.get("after_state") else None
                except (TypeError, ValueError):
                    after = None
                ed["after_state"] = _mask_event(after)
                masked_events.append(ed)
            advice = (
                f"该设备过去有 {len(visible_history)} 次可见维修记录，最近状态："
                f"{visible_history[0]['status'] if visible_history else '无'}"
            )
            return {"task_id": task_id, "asset_id": target_asset,
                    "asset_code": asset_row["asset_code"],
                    "asset_display_name": asset_row["display_name"],
                    "history": visible_history,
                    "events": masked_events,
                    "advice": advice}

    def record_advice(self, actor_id: str, idem_key: str, task_id: str,
                      source_kind: str, payload: dict) -> dict:
        if source_kind not in {"DEVICE_HISTORY", "STAGE_HINT", "PROGRESS_NOTE"}:
            raise InvalidKind(source_kind)

        def body(conn, fp):
            task = self._resolve(conn, task_id)
            self.executor._assert_visible(conn, task, actor_id)
            advice_id = _uuid()
            conn.execute(
                "INSERT INTO repair_advice (advice_id, task_id, actor_id, source_kind, "
                "payload, created_at_ms) VALUES (?,?,?,?,?,?)",
                (advice_id, task_id, actor_id, source_kind,
                 json.dumps(payload, ensure_ascii=False), self.now()))
            return {"advice_id": advice_id, "task_id": task_id, "source_kind": source_kind,
                    "task_version": task["version"]}

        return self._run(command="record_advice", actor_id=actor_id, idem_key=idem_key,
                         task_id=task_id, expected_version=None,
                         params={"task_id": task_id, "source_kind": source_kind,
                                 "payload": payload},
                         body=body).data
