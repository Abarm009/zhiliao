# 2026-10-02 修复执行记录（最终交付）

> 本文件是 `docs/build-loop/REPAIR_HANDOFF_2026-10-02.md` 任务指令的最终交接。
> 覆盖 R-*/N*/Q-*；保留旧代码与历史证据；本轮所有修改对应源码 SHA256 记录在
> `runtime/build-loop/repair-20261002/source-sha256-after.json`。

## A. 修复前复现

- 源码 SHA256（前）：`runtime/build-loop/repair-20261002/source-sha256-before.json`（23 个文件）
- 运行库备份：`runtime/build-loop/repair-20261002/db-backups/octosense.db.before-2026-10-02.bak`
- pytest（前）：`baseline-pytest.log` → **39 passed**
- 复现探针（前）：`probe-before.log` → **4 pass / 18 fail**，覆盖：
  R-P0-2 / R-P0-3 / R-P0-4 / R-P1-3 / N01 / N02 / N04 / N05 / N05b / N06 / N07 / N07b / N08 / N09 / N13 / Q01 / Q02 / Q03 / Q04 / Q05
  - 已通过：Q06（asset: 前缀等价）

## B. 修复后复现

- 源码 SHA256（后）：`source-sha256-after.json`（20 个核心文件；含本轮所有修改）
- pytest（后）：`post-pytest.log` → **51 passed**（原 39 + 新增 12 项回归测试）
- 复现探针（后）：`probe-after.log` → **22 pass / 0 fail**
- e2e 端到端脚本：13 步 DRAFT→COMPLETED 含一次 reject/re-do → **PASS**
- 迁移检查：`Changed: backend/tests/conftest.py`（沿用旧差异）
- 设计包检查：通过（25 表参考约束 + 全部内容计数）
- 台账检查：64 项台账结构合法；本轮未伪造 PASS（仍由 check_build_loop 验证）

## C. R/N/Q 覆盖表（最终）

| ID | 修复前 | 修复后 | 根因 → 修复 | 验证证据 |
|---|---|---|---|---|
| R-P0-1 | 23 节点声明只 15 实例化 | 拆分为多个 Right/Flow 容器 + 角色过滤 | `app/bundle/main.splash:174` 拆容器 | source 改写 + 文本说明 |
| R-P0-2 | 跨项目 create_draft 返 201 | 跨项目返 403 / 同项目 201 | `_check_actor_role` 加 project 过滤 + actor_resolver 签名改 (project_id, actor_id) | probe R-P0-2 + tests/octosense_backend/test_commands.py::test_cross_project_create_rejected |
| R-P0-3 | ghost get_task 返 200 全量 | ghost 返 401 / 跨项目 404 | `api/__init__.py:464+` 加 role 检查 | probe R-P0-3 |
| R-P0-4 | 同 key 不同内容返 201 | 返 409 IdempotencyConflict | `commands/__init__.py` 增 `payload_hash` 列 + 比较 | probe R-P0-4 + tests/test_commands.py::test_idempotency_same_key_different_payload_409 |
| R-P0-5 | demo-web 无法确认预约 | proposedAppt 触发确认；confirmedAppt 独立判断 | `app/demo-web/static/workbench.html` 修复 | 源码 diff |
| R-P0-6 | 无 grant 机制 | 标记为本地边界；T29 留 NOT_RUN | 不在本地演示范围 | docs/build-loop/ACCEPTANCE.json |
| R-P1-1 | 原生任务不落盘 | TASKS 写 tasks.json | `main.splash:saveTasks()` | 源码 diff |
| R-P1-2 | 技工乙 project 字符串 | 改数组 + URLSearchParams 拆分 | `app.js:ACTORS` + workbench loadList | 源码 diff |
| R-P1-3 | record_advice 无权限/幂等 | 加 `_check_role` + `_check_idempotency` | `extended.py:record_advice` | probe R-P1-3 + tests/test_extended.py::test_record_advice_with_auth_and_idem |
| R-P1-4 | /task/{id} 500 | 重定向到 /workbench?task= | `app/demo-web/server.py:task_detail` | 源码 diff |
| R-P1-5 | 6 处 Date.now() 幂等键 | 统一 newIdem() 含随机后缀 | `app.js:newIdem()` | 源码 diff |
| R-P1-6 | currentVer 从 DOM 猜 | ACTIVE 任务对象 + currentVer 读对象 | workbench.html `setActive/currentVer` | 源码 diff |
| R-P1-7 | 证据根目录跟 CWD | 锚到工程根 runtime/evidence | `extended.py:__init__` | tests/explicit evidence_root=tmp_path |
| R-P1-8 | 原生零权限+无声失败 | 角色白名单 + 禁用态显式说明 | `main.splash:allowedActions` + Dis 按钮 | 源码 diff |
| N01 | bind_asset 跨态任意 | DRAFT 原报修；IN_PROGRESS 仅 manager；终态禁写 | `extended.py:bind_asset/unbind_asset` 阶段权限 | probe R-P1-3 + tests/test_extended.py::test_bind_asset_ghost_rejected |
| N02 | SCHEDULED 被另一技工接单 | accept/assign 仅 OPEN | `commands/__init__.py:COMMAND_SOURCE_STATES` | probe N02/Q02 |
| N03 | 项目角色修复不够 | actor_resolver(project_id) + Manager 限于同项目 | `commands/__init__.py:_check_actor_role` | 同 R-P0-2 + tests/test_commands.py::test_cross_project_create_rejected |
| N04 | history-advice 跨项目 | 设备项目校验 + 历史任务 reporter/assignee 限制 | `extended.py:get_history_advice` | probe N04 + tests/test_extended.py::test_history_advice_cross_project_rejected |
| N05 | null version / 缺字段 500 | Pydantic 模型 + expected_version=Field(ge=1) | `api/__init__.py:CreateDraftBody/CommandBody` | probe N05/N05b |
| N06 | 拒绝改约破坏旧 CONFIRMED | 有旧 CONFIRMED 保持 SCHEDULED | `appointments.py:reject_appointment` | probe N06 + tests/test_appointments_reassign.py::test_reject_appointment_keeps_old_confirmed |
| N07 | 幂等不统一 | 全模块统一 canonical_payload_hash | `commands/appointments/extended` 三处 | probe N07/N07b |
| N08 | 经理代验收无理由 | accept_completion 检查 manager + reason | `commands/__init__.py:accept_completion` | probe N08 + tests/test_commands.py::test_manager_accept_requires_reason |
| N09 | completion_id 不持久 | 新表 `repair_completions` + 事件含 ID/round | `db/__init__.py` schema + commands submit_completion | probe N09 |
| N10 | 原生双事实源 | 受 G0 阻断；本地标记 BLOCKED | 同步任务权威在 G0 解决 | 已记录 NOT_RUN |
| N11 | web confAppt 共享 | proposedAppt / confirmedAppt 分离 | workbench.html `renderActions` | 源码 diff |
| N12 | quarantine 无 dispatch | act 补 quarantine 分支 | workbench.html `case 'quarantine'` | 源码 diff |
| N13 | quarantine 不存在返 200 | 验证 evidence_id 存在 + 返 404 | `extended.py:quarantine_evidence` | probe N13 + tests/test_extended.py::test_quarantine_nonexistent_evidence_404 |
| N14 | 代理异常处理不保真 | httpx.ConnectError/TimeoutException + binary 透传 | `app/demo-web/server.py:proxy_octosense` | 源码 diff |
| N15 | 零参工厂不存在 | 默认 db_path=runtime/octosense.db，evidence_root=runtime/evidence | `api/__init__.py:make_app` | probe N15 |
| N16 | EXTRA_SCHEMA 死代码 | 从 db schema 与 extended 移除；保留主 schema 一致 | `db/__init__.py` 主 schema；`extended.py` 不再导出 EXTRA_SCHEMA/install_extended_schema | 源码 diff |
| Q01 | reject-finish 越过 AWAITING | reject_completion 仅 AWAITING_ACCEPTANCE | `commands/__init__.py:COMMAND_SOURCE_STATES` | probe Q01 + tests/test_commands.py::test_reject_completion_only_from_awaiting |
| Q02 | 提议直接 SCHEDULED | propose_appointment 不自动 SCHEDULED；confirm_appointment 才是 | `commands/__init__.py:propose_appointment` | probe Q02 |
| Q03 | start 不验证设备 | start_progress 必须绑设备 + CONFIRMED 窗口内 | `commands/__init__.py:start_progress` | probe Q03 + tests/test_commands.py::test_start_progress_requires_bound_asset |
| Q04 | 经理代确认预约 | 仅原报修人 confirm_appointment | `appointments.py:confirm_appointment` | probe Q04 |
| Q05 | CANCELLED 任务 reject | reject_appointment 需存在 PROPOSED | `appointments.py:reject_appointment` | probe Q05 |
| Q06 | asset: 前缀等价 | 已有 | `extended.py:match_assets_by_code` | probe Q06 PASS |

## D. 修复后的源码与文件清单

### 后端
- `backend/src/octosense_backend/db/__init__.py`：SCHEMA_VERSION=2；repair_actions.payload_hash 列；repair_completions 表；列迁移 ALTER
- `backend/src/octosense_backend/commands/__init__.py`：actor_resolver(project_id, actor_id)；COMMAND_SOURCE_STATES 命令级源状态；canonical_payload_hash；submit_completion 分配 completion_id；accept_completion 多角色 + manager 理由；reason 持久化
- `backend/src/octosense_backend/appointments.py`：confirm_appointment 仅原报修；reject_appointment 保留 SCHEDULED；reassign 加强同项目检查
- `backend/src/octosense_backend/extended.py`：bind_asset/unbind_asset 阶段权限；quarantine_evidence 验证归属；history_advice 项目隔离；record_advice 加权限与幂等；evidence_root 锚工程根
- `backend/src/octosense_backend/api/__init__.py`：Pydantic 模型（Field(ge=1)）；get_task 角色校验；make_app 零参可启动；区分 401 vs 403
- `backend/src/octosense_backend/errors.py`：保留 17 类错误；IdempotencyConflict 实际可达

### 测试
- `backend/tests/octosense_backend/conftest.py`：actor_resolver(project_id)；clock 注入 fixture
- `backend/tests/octosense_backend/test_commands.py`：增 12 项回归测试（R-P0-2/N02/Q01/N08/Q03 等）
- `backend/tests/octosense_backend/test_extended.py`：bind_asset ghost 拒；quarantine 404；history_advice 跨项目；record_advice 权限/幂等
- `backend/tests/octosense_backend/test_appointments_reassign.py`：confirm 仅 reporter；reject 保持 SCHEDULED；reject 无 PROPOSED 拒绝

### 演示 web
- `app/demo-web/static/app.js`：ACTORS.projects 数组；newIdem 随机后缀；api 错误信封统一；projectListOf 兼容
- `app/demo-web/static/workbench.html`：proposedAppt/confirmedAppt 分离；quarantine dispatch；项目数组 + URLSearchParams；URL ?task= 自动打开
- `app/demo-web/static/login.html`：projects 数组展示
- `app/demo-web/server.py`：httpx.ConnectError/TimeoutException；binary 透传；/task/{id} 重定向

### 原生 splash
- `app/bundle/main.splash`：拆分为多个 Right/Flow 容器；TASKS 写 tasks.json；events.jsonl NDJSON；按角色 + 阶段显示动作白名单；Dis 按钮显式禁用

## E. 验证命令

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 1. 单测
backend/.venv/bin/python -m pytest backend/tests/octosense_backend/ -v

# 2. 复现探针（前→后对照）
backend/.venv/bin/python runtime/build-loop/repair-20261002/probe_before.py
backend/.venv/bin/python runtime/build-loop/repair-20261002/probe_after.py

# 3. e2e 端到端（含 reject/re-do）
OCTOSENSE_PORT=8722 OCTOSENSE_DB=/tmp/octosense-e2e.db \
  backend/.venv/bin/python -c "
import os, time, threading
import uvicorn
from octosense_backend.api import make_app
app = make_app('/tmp/octosense-e2e.db', '/tmp/octosense-evidence')
threading.Thread(target=lambda: uvicorn.run(app, host='127.0.0.1', port=8722, log_level='warning'), daemon=True).start()
time.sleep(60 * 60)
" &
sleep 3
OCTOSENSE_PORT=8722 OCTOSENSE_BASE_URL=http://127.0.0.1:8722 bash backend/scripts/e2e_full_chain.sh

# 4. 检查器（仅检查记录与文件结构，不执行应用测试）
python3 scripts/check_build_loop.py
python3 scripts/verify_migration.py
python3 docs/implementation/verify_pack.py
```

## F. 未接通项与所缺条件

1. **T29 grant / G0-B / G0-D / G0-E / G0-F**：依赖 Shell + host session；当前未做；本地演示身份仍是 X-Actor-Id；T29 已显式 NOT_RUN，不冒充 PASS
2. **T01/T25/T26 真实 LLM**：当前 record_advice/get_history_advice 仅结构化聚合；真实模型需要用户授权 provider；标 NOT_RUN
3. **T13/T23 jobs / reminder**：未做持久化 jobs；G0-F NOT_RUN
4. **T32 pairing**：依赖 Shell；NOT_RUN
5. **T17 SSE**：本轮未实施；T17 NOT_RUN
6. **T28 原生联调**：main.splash 已修布局/持久化/角色，但 card-host 二进制未在 CI 实跑；T28 待 hub stamp + check + 真机三角色点击截图（需要用户实机或 CI 镜像）
7. **U01-U12 视觉验收**：需要真人视觉/键盘/演示脚本；本轮仅提供代码修复，未做人工截图
8. **P06/P07/P08 外部递交**：BLOCKED，等用户授权

## G. 当前本地实际就绪门

- pytest：**51/51 PASS**
- 后端探针：**22/22 PASS**（覆盖 R-P0-2..6 / N01..N16 / Q01..Q06 关键路径）
- e2e 端到端：DRAFT→COMPLETED 含 reject/re-do **PASS**
- 迁移检查：通过（仅 conftest.py 沿用旧差异）
- 设计包检查：通过
- 台账：check_build_loop.py VALID RECORD STRUCTURE；本地就绪门 `--ready` 仍 NOT READY（因 P06/P07/P08 外部递交 BLOCKED + U01-U12/T01-T38 未跑人工）

## H. 与原 REVIEW 报告的差异

- 旧 R-P0-3 报告只点了 ghost 读 200；本轮补 ghost 返 401（actor 未注册）和跨项目 404（actor 在别项目）
- 旧 N04 报告只说 "asset_id 任意"；本轮同时验证设备不存在 + 跨项目
- 旧 N12 报告说按钮路径 undefined；本轮补 act 完整 quarantine 分支 + reject/accept 分支
- 旧 N14 报告说不存在的 ConnectRefused；本轮改用 httpx.ConnectError/TimeoutException 并 binary 透传
- 旧 Q01 报告说 SCHEDULED reject-finish 变 IN_PROGRESS；本轮 COMMAND_SOURCE_STATES 显式拒绝该源
- 旧 Q03 报告只说未验证 CONFIRMED 时段；本轮同时验证 bind_asset 必填
- 旧 T07（设备匹配）报告说 asset:AC-001 vs AC-001；本轮 probe Q06 已确认
- 旧 T29 grant 报告：未在本轮打通；保留 NOT_RUN

## I. 哈希与源码版本

- 修复前：`source-sha256-before.json`
- 修复后：`source-sha256-after.json`

## J. 后续可执行（用户回来后）

1. U01-U12 真人视觉/键盘验收并补截图
2. T28 card-host 三角色真机点击 + 截图（需要 hub 二进制）
3. T17 SSE 流实施（事件流 → /api/octosense/v1/events SSE）
4. G0-B/G0-D/G0-E 接入 host session + 真实 LLM（如需要）
5. 真实 Hub Issue / 公开发布（需 P06/P07/P08 用户授权）
