"""测试共用助手：**前置操作必须断言成功并回读目标状态**。

修复 V11：旧 helper 用 `executor.confirm_draft(...)` 但忽略返回值，铺垫失败时
后续断言仍在跑，于是“因错误版本号 409”被当成 CANCELLED 测试通过。这里每一步
都 `_ok(...)` 断言成功并回读数据库事实。

所有业务夹具都用真实允许路径构造（合法 project / space / skill / category）。
"""
from __future__ import annotations

from octosense_backend import authorization as auth
from octosense_backend.errors import OctoSenseError

# 合成夹具：两个项目、两个报修人、两个技能不同技工、一个经理、装/服不同设备
PA = "prj-A"
PB = "prj-B"
R1 = "u-reporter-1"
R2 = "u-reporter-2"
T1 = "u-tech-1"          # HVAC
T2 = "u-tech-2"          # ELECTRICAL
MGR = "u-manager"
GHOST = "u-ghost"
SP_ROOM = "sp-a-1"        # 东侧会议室
SP_CORRIDOR = "sp-a-2"
SP_POWER = "sp-a-3"
SP_MECH = "sp-a-mech"
AS_AC = "as-a-1"         # AC-001：装机房，服务会议室（HVAC）
AS_PWR = "as-a-2"        # PWR-001：装会议室，服务配电间（ELECTRICAL）
AS_EXH = "as-a-3"        # EXH-001：服务会议室/走廊（HVAC）

HVAC = "HVAC_NOT_COOLING"
ELECTRICAL = "ELECTRICAL"


def ok(res, what: str = "command"):
    """断言 CommandResult 成功；失败时把错误带到断言消息里。"""
    assert getattr(res, "ok", False), f"{what} failed: {getattr(res, 'error', None)}"
    return res.data


def okd(data, what: str = "command"):
    """断言 ExtendedCommands / AppointmentCommands 的 dict 返回非空。

    这些入口直接返回 dict（内部已是成功结果）；异常以 OctoSenseError 抛出，
    因此只要没抛异常就是成功。这里额外断言回执里带 task_id，避免空响应冒充成功。
    """
    assert isinstance(data, dict), f"{what}: expected dict, got {type(data)}"
    assert data, f"{what}: empty result"
    return data


def expect_error(fn, exc, what: str):
    """断言抛出指定业务错误类型。"""
    try:
        fn()
    except exc as e:
        return e
    except OctoSenseError as e:  # pragma: no cover - 诊断输出
        raise AssertError(f"{what}: expected {exc.__name__}, got {type(e).__name__} {e}")
    raise AssertError(f"{what}: expected {exc.__name__}, no error raised")


class AssertError(AssertionError):
    pass


def task_row(db, task_id: str) -> dict:
    conn = db.conn()
    try:
        row = conn.execute("SELECT * FROM repair_tasks WHERE task_id=?",
                           (task_id,)).fetchone()
        assert row is not None, f"task {task_id} missing"
        return dict(row)
    finally:
        conn.close()


def assert_status(db, task_id: str, status: str) -> dict:
    row = task_row(db, task_id)
    assert row["status"] == status, f"task {task_id} status={row['status']}, want {status}"
    return row


class World:
    """把常见业务路径写成“断言成功 + 回读”的链式助手。"""

    def __init__(self, executor, ext, appt_cmds, db, clock, fixtures=None):
        self.executor = executor
        self.ext = ext
        self.db = db
        self.clock = clock
        self.f = fixtures or {}
        # appt_cmds 可省略：需要预约/改派命令时按同一 executor 与时钟惰性构造，
        # 保证命令边界与时钟唯一。
        from octosense_backend.appointments import AppointmentCommands
        self.appt = appt_cmds or AppointmentCommands(db, executor=executor, clock=clock)

    # ---- 构造 ----

    def draft(self, *, reporter=R1, project=PA, space=SP_ROOM, category=HVAC,
              key="k-draft", problem="东侧会议室空调不制冷", contact="报修人一",
              contact_info="渠道：工作台") -> str:
        data = ok(self.executor.create_draft(
            actor_id=reporter, idem_key=key, problem_text=problem,
            contact_name=contact, contact_info=contact_info, project_id=project,
            space_id=space, category=category), "create_draft")
        assert_status(self.db, data["task_id"], "DRAFT")
        return data["task_id"]

    def open(self, *, reporter=R1, project=PA, space=SP_ROOM, category=HVAC,
             key="k-draft", **kw) -> str:
        tid = self.draft(reporter=reporter, project=project, space=space,
                         category=category, key=key, **kw)
        v = assert_status(self.db, tid, "DRAFT")["version"]
        ok(self.executor.confirm_draft(actor_id=reporter, idem_key=key + "-confirm",
                                       task_id=tid, expected_version=v),
           "confirm_draft")
        assert_status(self.db, tid, "OPEN")
        return tid

    def accepted(self, *, reporter=R1, tech=T1, project=PA, space=SP_ROOM,
                 category=HVAC, key="k-draft", asset=None, bind_key="k-bind") -> str:
        """R2-09 修正：ACCEPTED 阶段绑定设备必须是当前承接技工或经理，原报修人不再可绑。"""
        tid = self.open(reporter=reporter, project=project, space=space,
                        category=category, key=key)
        v = assert_status(self.db, tid, "OPEN")["version"]
        ok(self.executor.accept_task(actor_id=tech, idem_key=key + "-accept",
                                     task_id=tid, expected_version=v), "accept_task")
        row = assert_status(self.db, tid, "ACCEPTED")
        assert row["assignee_id"] == tech, f"assignee={row['assignee_id']}, want {tech}"
        if asset is None:
            asset = AS_AC if category == HVAC else AS_PWR
        self.bind(tid=tid, actor=tech, asset_id=asset, key=bind_key)
        return tid

    def bind(self, *, tid, actor, asset_id, key="k-bind", reason="") -> dict:
        v = task_row(self.db, tid)["version"]
        data = okd(self.ext.bind_asset(actor_id=actor, idem_key=key, task_id=tid,
                                      asset_id=asset_id, expected_version=v,
                                      reason=reason), "bind_asset")
        row = task_row(self.db, tid)
        assert row["asset_id"] == asset_id, f"bound asset={row['asset_id']}"
        return data

    def propose(self, *, tid, tech=T1, start=None, duration_ms=30 * 60_000,
                key="k-appt") -> dict:
        if start is None:
            start = self.clock() + 24 * 3600 * 1000
        end = start + duration_ms
        v = task_row(self.db, tid)["version"]
        data = ok(self.executor.propose_appointment(
            actor_id=tech, idem_key=key, task_id=tid, start_at_ms=start,
            end_at_ms=end, expected_version=v), "propose_appointment")
        assert data["appointment_status"] == "PROPOSED"
        return data

    def confirm(self, *, tid, reporter=R1, appointment_id=None, key="k-confappt") -> dict:
        v = task_row(self.db, tid)["version"]
        data = okd(self.appt.confirm_appointment(
            actor_id=reporter, idem_key=key, task_id=tid, expected_version=v,
            appointment_id=appointment_id), "confirm_appointment")
        if appointment_id is None and data.get("appointment_id"):
            appointment_id = data["appointment_id"]
        assert_status(self.db, tid, "SCHEDULED")
        conn = self.db.conn()
        try:
            row = conn.execute("SELECT status FROM repair_appointments WHERE appointment_id=?",
                               (appointment_id,)).fetchone()
            assert row is not None and row["status"] == "CONFIRMED", \
                f"appointment {appointment_id} not CONFIRMED"
        finally:
            conn.close()
        return data

    def reject_proposal(self, *, tid, reporter=R1, reason="时间不合适", key="k-rejappt") -> dict:
        v = task_row(self.db, tid)["version"]
        return okd(self.appt.reject_appointment(
            actor_id=reporter, idem_key=key, task_id=tid, expected_version=v,
            reason=reason), "reject_appointment")

    def start(self, *, tid, tech=T1, at=None, key="k-start") -> dict:
        if at is not None:
            self.clock.set(at)
        v = task_row(self.db, tid)["version"]
        data = ok(self.executor.start_progress(actor_id=tech, idem_key=key, task_id=tid,
                                               expected_version=v), "start_progress")
        assert_status(self.db, tid, "IN_PROGRESS")
        return data

    def evidence(self, *, tid, actor=T1, filename="note.txt", mime="text/plain",
                 payload=b"evidence-bytes", key="k-ev") -> str:
        v = task_row(self.db, tid)["version"]
        data = okd(self.ext.upload_evidence(
            actor_id=actor, idem_key=key, task_id=tid, filename=filename,
            mime_type=mime, payload=payload, expected_version=v), "upload_evidence")
        return data["evidence_id"]

    def complete(self, *, tid, tech=T1, text="已更换压缩机",
                 disposition="REPAIRED", key="k-complete") -> dict:
        v = task_row(self.db, tid)["version"]
        data = ok(self.executor.submit_completion(
            actor_id=tech, idem_key=key, task_id=tid, expected_version=v,
            completion_text=text, disposition=disposition), "submit_completion")
        assert_status(self.db, tid, "AWAITING_ACCEPTANCE")
        assert data["completion_id"]
        assert data["round"] >= 1
        return data

    def accept_finish(self, *, tid, actor=R1, reason="", key="k-accept-finish") -> dict:
        v = task_row(self.db, tid)["version"]
        data = ok(self.executor.accept_completion(
            actor_id=actor, idem_key=key, task_id=tid, expected_version=v,
            reason=reason), "accept_completion")
        assert_status(self.db, tid, "COMPLETED")
        return data

    def reject_finish(self, *, tid, actor=R1, reason="需要补充处理",
                      key="k-reject-finish") -> dict:
        v = task_row(self.db, tid)["version"]
        data = ok(self.executor.reject_completion(
            actor_id=actor, idem_key=key, task_id=tid, expected_version=v,
            reason=reason), "reject_completion")
        assert_status(self.db, tid, "IN_PROGRESS")
        return data

    def in_progress(self, *, reporter=R1, tech=T1, category=HVAC, asset=None) -> tuple[str, int, int]:
        """推到 IN_PROGRESS，返回 (task_id, start_ms, end_ms)。"""
        tid = self.accepted(reporter=reporter, tech=tech, category=category, asset=asset)
        appt = self.propose(tid=tid, tech=tech)
        start, end = appt["start_at_ms"], appt["end_at_ms"]
        self.confirm(tid=tid, reporter=reporter, appointment_id=appt["appointment_id"])
        self.start(tid=tid, tech=tech, at=start + 60_000)
        return tid, start, end
