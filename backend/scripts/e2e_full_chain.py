#!/usr/bin/env python3
"""OctoSense 端到端链：DRAFT → COMPLETED（含一次退回/重做），真实 HTTP + 临时库。

修复 V11 / 交接指令 §6.2：
  - 读取传入的 BASE_URL / DB / EVIDENCE_ROOT / OCTOSENSE_PORT，**不**固定 8713，
    不会打到用户正在运行的实例。
  - 自带独立端口 + 独立临时库 + 可注入服务端时钟；启动、跑链、关停都由本脚本控制。
  - 任何 HTTP 失败立即非零退出；最后断言最终状态、回执、两轮完工记录、附件与预约事实。
  - 每一步都回读服务端状态，不用魔数 version，不断言"页面出现绿勾"。

用法：
  backend/.venv/bin/python backend/scripts/e2e_full_chain.py            # 自起服务
  backend/.venv/bin/python backend/scripts/e2e_full_chain.py --base-url http://127.0.0.1:PORT
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "backend" / "src"
PY = ROOT / "backend" / ".venv" / "bin" / "python"

REPORTER, TECH, MGR = "u-reporter-1", "u-tech-1", "u-manager"
PROJECT = "prj-A"
SPACE = "sp-a-1"          # 东侧会议室
ASSET = "as-a-1"          # AC-001：服务东侧会议室
CATEGORY = "HVAC_NOT_COOLING"
DAY_MS = 86_400_000


class Fail(AssertionError):
    pass


def check(cond: bool, msg: str):
    if not cond:
        raise Fail(msg)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def req(base: str, method: str, route: str, actor: str, body=None, raw: bytes | None = None):
    url = base + route
    data = None
    headers = {"X-Actor-Id": actor}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    elif raw is not None:
        data = raw
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            payload = resp.read()
            return resp.status, (json.loads(payload) if payload else {})
    except urllib.error.HTTPError as e:
        payload = e.read()
        try:
            parsed = json.loads(payload)
        except (ValueError, TypeError):
            parsed = {"raw": payload.decode("utf-8", "replace")}
        return e.code, parsed


def ok(status: int, body, what: str) -> dict:
    check(status in (200, 201), f"{what}: HTTP {status} {json.dumps(body, ensure_ascii=False)}")
    return body


def upload(base: str, tid: str, actor: str, key: str, version: int,
           filename: str, content: bytes, ctype: str):
    # multipart 体：idempotency_key / expected_version / file 三个字段
    boundary = "octosense-e2e-boundary"
    ctype_header = "multipart/form-data; boundary=" + boundary
    pre = [
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="idempotency_key"\r\n\r\n',
        key.encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="expected_version"\r\n\r\n',
        str(version).encode(), b"\r\n",
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode(),
        f"Content-Type: {ctype}\r\n\r\n".encode(),
        content, b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    url = base + "/api/octosense/v1/tasks/" + tid + "/evidence"
    r = urllib.request.Request(url, data=b"".join(pre),
                               headers={"X-Actor-Id": actor, "Content-Type": ctype_header},
                               method="POST")
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except (ValueError, TypeError):
            return e.code, {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("OCTOSENSE_BASE_URL"))
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--db", default=None)
    ap.add_argument("--evidence-root", default=None)
    args = ap.parse_args()

    steps: list[str] = []
    server = None
    tmpdir = None
    base = args.base_url
    if base:
        check(base.startswith("http://127.0.0.1:") or base.startswith("http://localhost:"),
              f"只允许 loopback BASE_URL，收到 {base}")
    else:
        port = args.port or free_port()
        tmpdir = tempfile.mkdtemp(prefix="octosense-e2e-")
        db = args.db or str(Path(tmpdir) / "e2e.db")
        evidence = args.evidence_root or str(Path(tmpdir) / "evidence")
        Path(tmpdir, "run.py").write_text(
            "import time, uvicorn\n"
            "from octosense_backend.api import make_app\n"
            f"app = make_app({db!r}, {evidence!r})\n"
            f"uvicorn.run(app, host='127.0.0.1', port={port}, log_level='warning')\n",
            encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        server = subprocess.Popen([str(PY), str(Path(tmpdir) / "run.py")], cwd=ROOT, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        base = f"http://127.0.0.1:{port}"
        for _ in range(60):
            try:
                with urllib.request.urlopen(base + "/api/octosense/v1/health",
                                            timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:  # noqa: BLE001
                time.sleep(0.25)
        else:
            out = b""
            if server is not None and server.stdout is not None:
                try:
                    server.terminate()
                    server.wait(timeout=3)
                    out = server.stdout.read()
                except Exception:  # noqa: BLE001
                    pass
            check(False, f"服务未在 {base} 就绪\n子进程输出：\n"
                         f"{out.decode('utf-8', 'replace')[-2000:]}")

    try:
        prefix = "/api/octosense/v1"

        # [1] 草稿 + 提交
        tid = ok(*req(base, "POST", prefix + "/tasks", REPORTER, {
            "project_id": PROJECT, "problem_text": "东侧会议室空调不制冷，希望明天下午处理",
            "contact_name": "报修人一", "contact_info": "渠道：工作台",
            "space_id": SPACE, "category": CATEGORY,
            "idempotency_key": "e2e-create",
        }), "create_draft")["task_id"]
        steps.append(f"create_draft task={tid}")

        status, detail = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        ok(status, detail, "get_task")
        v = detail["task"]["version"]
        check(detail["task"]["status"] == "DRAFT", f"创建后应为 DRAFT，实际 {detail['task']['status']}")
        steps.append(f"DRAFT v{v}")

        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/confirm", REPORTER,
                          {"expected_version": v, "idempotency_key": "e2e-confirm"})
        ok(status, out, "confirm_draft")
        check(out["status"] == "OPEN", f"提交后应为 OPEN，实际 {out}")
        steps.append("→ OPEN")

        # [2] 接单
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/accept", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-accept"})
        ok(status, out, "accept_task")
        check(out["assignee_id"] == TECH, f"承接者应为 {TECH}，实际 {out}")
        steps.append(f"→ ACCEPTED (assignee={out['assignee_id']})")

        # [3] 绑定设备（AC-001 服务东侧会议室）
        # R2-09：ACCEPTED 阶段绑设备由当前承接技工（TECH）完成；不再是报修人。
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/bind-asset", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-bind",
                           "asset_id": ASSET})
        ok(status, out, "bind_asset")
        check(out["asset_id"] == ASSET, f"绑定应生效，实际 {out}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        check(det["task"]["asset_id"] == ASSET, "回读的设备与绑定结果不一致")
        steps.append(f"→ bind_asset {ASSET}")

        # [4] 提议 + 确认预约（首次提议保持 ACCEPTED）
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        # 提议一个 5 秒后开始、持续 20 分钟的窗口：既满足"开始必须在未来"的
        # 服务端时钟校验，又让脚本能在合理等待后真正开工（不用客户端伪造时间）。
        start = int(time.time() * 1000) + 5_000
        end = start + 20 * 60_000
        status, appt = req(base, "POST", f"{prefix}/tasks/{tid}/appointments", TECH,
                           {"expected_version": v, "idempotency_key": "e2e-propose",
                            "start_at_ms": start, "end_at_ms": end})
        ok(status, appt, "propose_appointment")
        check(appt["appointment_status"] == "PROPOSED", f"提议状态错误：{appt}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        check(det["task"]["status"] == "ACCEPTED", "首次提议不得把任务改成 SCHEDULED")
        steps.append("→ PROPOSED (task stays ACCEPTED)")

        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST",
                          f"{prefix}/tasks/{tid}/appointments/{appt['appointment_id']}/confirm",
                          REPORTER, {"expected_version": v, "idempotency_key": "e2e-confirm-appt"})
        ok(status, out, "confirm_appointment")
        check(out["status"] == "CONFIRMED", f"确认结果应为 CONFIRMED，实际 {out}")
        check(out["task_status"] == "SCHEDULED", f"确认后任务应 SCHEDULED，实际 {out}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        check(det["task"]["status"] == "SCHEDULED", "回读的任务状态不是 SCHEDULED")
        steps.append("→ CONFIRMED / SCHEDULED")

        # [5] 上传证据
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, ev = upload(base, tid, TECH, "e2e-evidence", v,
                            "site-note.txt", b"on-site inspection note\n" * 4, "text/plain")
        ok(status, ev, "upload_evidence")
        eid = ev["evidence_id"]
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}/evidence", REPORTER)
        check(any(e["evidence_id"] == eid and e["status"] == "READY"
                  for e in det["evidence"]), f"附件未回读为 READY：{det}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}/evidence/{eid}", REPORTER)
        ok(st, det, "download_evidence")
        import base64
        check(base64.b64decode(det["payload_b64"]) == b"on-site inspection note\n" * 4,
              "下载回来的附件字节不一致")
        steps.append(f"→ evidence {eid} (READY, bytes verified)")

        # [6] 开工（必须落在确认预约的窗口内：start <= now < end）
        wait_s = max(0.0, (start - int(time.time() * 1000)) / 1000.0)
        if wait_s > 0:
            steps.append(f"等待 {wait_s:.1f}s 进入预约窗口")
            time.sleep(wait_s + 0.5)
        now_ms = int(time.time() * 1000)
        check(start <= now_ms < end,
              f"当前时间 {now_ms} 不在确认窗口 [{start}, {end}) 内，不能开工")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/start", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-start"})
        ok(status, out, "start_progress")
        check(out["status"] == "IN_PROGRESS", f"开工后应 IN_PROGRESS，实际 {out}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        check(det["task"]["status"] == "IN_PROGRESS", "回读状态不是 IN_PROGRESS")
        steps.append("→ IN_PROGRESS")

        # [7] 完工第一轮 → 退回 → 完工第二轮 → 验收
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/complete", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-complete-1",
                           "completion_text": "已更换压缩机"})
        ok(status, out, "submit_completion")
        first_id = out["completion_id"]
        check(out["round"] == 1, f"第一轮 round 应为 1，实际 {out}")
        check(out["status"] == "AWAITING_ACCEPTANCE", f"完工后应 AWAITING_ACCEPTANCE，实际 {out}")
        steps.append(f"→ AWAITING_ACCEPTANCE round=1 completion_id={first_id}")

        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/reject-finish", REPORTER,
                          {"expected_version": v, "idempotency_key": "e2e-reject",
                           "reason": "照片没拍到更换后的铭牌"})
        ok(status, out, "reject_completion")
        check(out["status"] == "IN_PROGRESS", f"退回后应 IN_PROGRESS，实际 {out}")
        check(out["rejected_round"] == 1, f"退回应关联第 1 轮，实际 {out}")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        check(det["task"]["status"] == "IN_PROGRESS", "回读状态不是 IN_PROGRESS")
        steps.append("→ 退回 IN_PROGRESS (round 1)")

        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, ev2 = upload(base, tid, TECH, "e2e-evidence-2", v,
                             "nameplate.txt", b"nameplate after replacement\n", "text/plain")
        ok(status, ev2, "upload_evidence (round 2)")
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/complete", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-complete-2",
                           "completion_text": "已补齐铭牌照片与处理记录"})
        ok(status, out, "submit_completion (round 2)")
        second_id = out["completion_id"]
        check(out["round"] == 2, f"第二轮 round 应为 2，实际 {out}")
        check(second_id != first_id, "第二轮必须是新的 completion_id")
        steps.append(f"→ AWAITING_ACCEPTANCE round=2 completion_id={second_id}")

        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/accept-finish", REPORTER,
                          {"expected_version": v, "idempotency_key": "e2e-accept-finish"})
        ok(status, out, "accept_completion")
        check(out["status"] == "COMPLETED", f"验收后应 COMPLETED，实际 {out}")
        check(out["accepted_round"] == 2, f"验收应关联第 2 轮，实际 {out}")
        steps.append("→ COMPLETED")

        # [7] 幂等回放：同 key 重发 create，必须给同一 task 且不新增任务
        status, out = req(base, "POST", prefix + "/tasks", REPORTER, {
            "project_id": PROJECT, "problem_text": "东侧会议室空调不制冷，希望明天下午处理",
            "contact_name": "报修人一", "contact_info": "渠道：工作台",
            "space_id": SPACE, "category": CATEGORY, "idempotency_key": "e2e-create"})
        ok(status, out, "create_draft replay")
        check(out.get("idempotent_replay") is True, f"同 key 重发应回放：{out}")
        check(out.get("task_id") == tid, f"回放应给出同一 task_id：{out}")
        steps.append(f"→ idempotent replay task_id={out.get('task_id')}")

        # [8] 终态不能再开工；取消需理由
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        v = det["task"]["version"]
        status, out = req(base, "POST", f"{prefix}/tasks/{tid}/start", TECH,
                          {"expected_version": v, "idempotency_key": "e2e-start-after-done"})
        check(status == 422, f"终态开工应 422，实际 {status} {out}")
        steps.append(f"→ 终态开工被拒 ({status})")

        # [9] 最终事实回读
        st, det = req(base, "GET", f"{prefix}/tasks/{tid}", REPORTER)
        ok(st, det, "final get_task")
        task = det["task"]
        check(task["status"] == "COMPLETED", f"最终状态应为 COMPLETED，实际 {task['status']}")
        check(task["asset_id"] == ASSET, "最终设备与绑定不一致")
        check(task["space_id"] == SPACE, "最终服务空间不一致")
        rounds = [c["round"] for c in det["completions"]]
        texts = [c["completion_text"] for c in det["completions"]]
        check(rounds == [1, 2], f"完工轮次应为 [1,2]，实际 {rounds}")
        check(texts[0] == "已更换压缩机" and texts[1].startswith("已补齐"), f"完工文本不符：{texts}")
        conf = [a for a in det["appointments"] if a["status"] == "CONFIRMED"]
        check(len(conf) == 1, f"应恰有一个 CONFIRMED 预约，实际 {len(conf)}")
        ev_ready = [e for e in det["evidence"] if e["status"] == "READY"]
        check(len(ev_ready) >= 2, f"应至少两条 READY 附件，实际 {len(ev_ready)}")
        event_types = [e["event_type"] for e in det["events"]]
        for needed in ("confirm_draft", "accept_task", "bind_asset", "propose_appointment",
                       "confirm_appointment", "submit_completion", "reject_completion",
                       "accept_completion"):
            check(needed in event_types, f"事件流缺少 {needed}")
        steps.append("final facts: status/asset/space/rounds/appointments/evidence/events ✓")

        print("\n".join(f"  {i + 1}. {s}" for i, s in enumerate(steps)))
        print(f"\nE2E PASS · task={tid} · base={base}")
        return 0
    except Fail as e:
        print(f"\nE2E FAIL · {e}", file=sys.stderr)
        print("已完成步骤：", file=sys.stderr)
        for i, s in enumerate(steps):
            print(f"  {i + 1}. {s}", file=sys.stderr)
        return 1
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
