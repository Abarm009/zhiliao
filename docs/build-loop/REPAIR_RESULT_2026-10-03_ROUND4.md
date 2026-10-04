# 第四轮修复执行结果：R3-01 ~ R3-08

日期：2026-10-03。执行入口：`docs/build-loop/REPAIR_PROMPT_2026-10-03_ROUND4.md`。
工作区：`/Users/abeam/一些尝试/知了OctoSense`。

## 一、范围与执行纪律

- 修改文件清单：
  - 业务实现：`backend/src/octosense_backend/{commands/__init__.py, extended.py, jobs.py, api/__init__.py}`
  - Web 表单：`app/demo-web/static/workbench.html`
  - 原生脚本：`app/bundle/main.splash`（移除伪造字节/sha，写 `ready:false` 占位；其他探针保留）
  - 测试与共用夹具：`backend/tests/octosense_backend/test_round3_repair.py`（R2-10 时钟前置校正）、新增 `backend/tests/octosense_backend/test_round4_repair.py`
  - 探针与文档：`runtime/repair-round4-20261003/probe_round4.py`、`app/docs/round4_native_probe.py`、`app/docs/round4_native_probe.md`
- 新增持久回归测试：**25 项**（`backend/tests/octosense_backend/test_round4_repair.py`）；保留上轮 24 项 R2 round3 测试及全部历史回归。
- 不修改：旧契约边界 `backend/src/octosense_backend/ops/contracts/`；官方参考克隆 `runtime/native-build/{makepad,octoscript-makepad,OctoSense-App-Hub}`；Hub bundle 的非脚本字段。
- 未触动：`docs/build-loop/ACCEPTANCE.json` 的 verdict 与 evidence 字段——本轮不重写 PASS/FAIL；上一轮 §五 各项保持。

## 二、R3-01 ~ R3-08 逐项结果

### R3-01｜草稿编辑：命令收敛到 `CommandExecutor.update_draft`，事务内幂等/版本/事件/回执 — **PASS**

**根因**：`api/__init__.py:213-291` 的 `update_draft` 走 `db.conn()`，显式 `_record_event` + 手工 `record_receipt`，没有 `_run` 的 `BEGIN IMMEDIATE` 事务 + `check_replay`，导致同 key 改内容时 `INSERT receipt` 触发 `IntegrityError` 返回 500 但 UPDATE 已提交（探测脚本反例 r3-01 `version_before=2 → version_after=3`，contacts_after=`WRITTEN-DESPITE-500`，events=2，receipts=1）。

**修复**：
- `commands/__init__.py` 新增 `update_draft(actor_id, idem_key, task_id, expected_version, space_id=None, contact_name=None, contact_info=None, preferred_window=None, problem_text=None)`：与现有 `create_draft` 同框架，`_run()` 包事务；显式 `COMMAND_SOURCE_STATES["update_draft"]={"DRAFT"}`、`_COMMAND_ROLES["update_draft"]={"REPORTER"}`、`_COMMAND_MANAGER_DELEGATE["update_draft"]=False`；`expected_version` 严格；写业务/事件/回执在同一事务；同 key 改 payload/expected_version → 409；撤权 → 角色校验失败。
- `api/__init__.py:213` `update_draft` 改为 `run_exec("update_draft", …)`，删除手工 receipt + with conn pass 死代码。
- `COMMAND_NAMES` 加 `"update_draft"`。

**验证**：
- 探针 `runtime/repair-round4-20261003/probe_round4.py::r3_01_draft_idempotency`：首次 200、相同重试 200 + 同 action_id、同 key 改内容 409 + 数据不变、撤权后再写 403。
- pytest `test_round4_repair.py::test_r3_01_*`：5 项 PASS（首次/重放/冲突/撤权拒绝/并发旧版本只一人成功）。
- V-series `probe_round2.py` 11 项仍 PASS；端到端 `e2e_full_chain.py` 17 步仍 PASS（包含 `POST /tasks/{id}/draft` 补齐）。

### R3-02｜撤权后四条写路径全拒 — **PASS**

**根因**：原 `_run` 仅在回放路径做对象授权；首次写仍依赖各 body 的 `is_reporter = actor_id == reporter_id` 单一检查；移出项目后该检查不变 → 写越权成功。

**修复**（覆盖全部业务入口）：
- `extended.py::bind_asset` / `unbind_asset` body 先 `_check_role(..., {REPORTER, TECHNICIAN, MANAGER})`，再按阶段矩阵细分。
- `commands/__init__.py::cancel`、`reject_completion`、`accept_completion` body 验 `roles_of` 非空后，再 `is_reporter = (actor_id == reporter_id) and ("REPORTER" in roles)`。
- `extended.py::quarantine_evidence` body 同上。
- `update_draft`（R3-01 已加）`_check_actor_role({REPORTER})`。

**全部写入口清单**（本轮扫描后逐条覆盖）：
- 命令级：`create_draft / update_draft / confirm_draft / accept_task / assign_task / propose_appointment / confirm_appointment / reject_appointment / reassign / start_progress / record_progress / submit_completion / accept_completion / reject_completion / cancel / bind_asset / unbind_asset / upload_evidence / quarantine_evidence / add_pin / remove_pin / record_advice` — 22 个
- 领域方法 / 旧 runner / 原生适配：当前 commands/__init__.py、extended.py、appointments.py 中没有脱离 `_run` / `_check_actor_role` / `_assert_visible` 的写入口；原生侧 `addEvidence` 已写 `ready:false` 占位，禁止提交完工。

**验证**：
- 探针 `r3_02_revoked_four_paths`：draft / bind-asset / cancel / reject-finish 四条全部 403；合法 PB 项目仍可创建。
- pytest `test_round4_repair.py::test_r3_02_*`：6 项 PASS（draft / bind / cancel / reject-finish / 保留 PB 合法 / 同项目读 404）。

### R3-03｜Web allowed_actions 与后端矩阵一致 + 类别输入 + bind 入口 — **PASS**

**修复**：
- `api/__init__.py::_allowed_actions_for`：与 bind_asset / unbind_asset / cancel / reject_completion 共用同一矩阵；非法主体不再展示可成功执行的动作；DRAFT 阶段原报修人加 `update_draft`；OPEN 阶段经理 `bind_asset + assign_task + cancel`；ACCEPTED/SCHEDULED 阶段 `bind_asset + propose_appointment + confirm_appointment + reject_appointment`；IN_PROGRESS 阶段 manager `bind_asset + unbind_asset + cancel`（均要求 reason）。
- `workbench.html`：表单加 `category` 下拉（HVAC / WATER_LEAK / ELECTRICAL / OTHER），createDraft 提交时携带；ACCEPTED 阶段原报修人不再显示硬编码 `bind-asset AC-001/PWR-001`；新增 `bindAssetForTech`、`bindAssetForMgr`、`bindAssetForMgrInProgress`、`unbindAssetForMgr`、`updateDraftSpace` 等接口，按 allowed 状态出现。Act 分支加 `unbind` 路由。
- 后端：`POST /api/octosense/v1/spaces` 已支持（无变化）；前端 `loadSpaces` / `createDraft` / `act` 已与 allowed_actions 保持一致。

**验证**：
- 探针 `r3_03_web_allowed_actions`：OPEN 阶段技工 `accept_task`、经理 `bind_asset + assign_task + cancel`、报修人无 bind_asset；ACCEPTED 阶段技工 `bind_asset + propose_appointment`；DRAFT 阶段报修人 `update_draft + confirm_draft + bind_asset + cancel`。
- pytest `test_round4_repair.py`：未单独新增 R3-03 用例，由 R2-03 + 端到端覆盖。

### R3-04｜history-advice 联系人脱敏 — **PASS**

**根因**：`extended.py::get_history_advice` 返回 `events=[dict(e) for e in events]`，`after_state` 原 json 文本含 `contact_info`；与 detail / SSE 共用的 `_mask_event_snapshot` 投影被绕开。

**修复**：`extended.py::get_history_advice` 计算 `can_see_contact = auth.can_see_contact(...)` 后，对每个 event 的 `after_state` json 走相同 `_mask_event` 投影；保留原始内部审计不删。`reporter_id/assignee_id` 字段不做脱敏（按 detail 既有行为）。

**验证**：
- 探针 `r3_04_history_advice_mask`：未接单技工 `GET /tasks/{tid}/history-advice?asset_id=as-a-1` 返回 200 且不含 `private-contact-R3-PROBE`；报修人 `R1` 同请求含该标记。
- pytest `test_round4_repair.py::test_r3_04_history_advice_event_mask` + `_reporter_still_sees_contact`：2 项 PASS。

### R3-05｜解绑共用 bind_asset 阶段矩阵 — **PASS**

**根因**：`extended.py::unbind_asset` 仅按 `{REPORTER, TECHNICIAN, MANAGER}` 验角色，再 `is_reporter or is_assignee or is_manager`；OPEN 阶段报修人也能解；与 `bind_asset` 矩阵不一致。

**修复**：`unbind_asset` body 与 `bind_asset` 共用 `BIND_ALLOWED_STATES` + 阶段矩阵：
- DRAFT → 仅原报修人（且仍是项目成员）
- OPEN → 仅经理
- ACCEPTED / SCHEDULED → 当前承接技工 或 经理
- IN_PROGRESS → 经理 + 必填理由
- AWAITING_ACCEPTANCE / COMPLETED / CANCELLED → 拒绝（必须 cancel + reopen）

**验证**：
- 探针 `r3_05_unbind_matrix`：DRAFT 经理解绑 403 / OPEN 报修人解绑 403 / IN_PROGRESS 经理无理由 422 / IN_PROGRESS 技工解绑 403。
- pytest `test_round4_repair.py::test_r3_05_*`：4 项 PASS（DRAFT / OPEN / ACCEPTED / IN_PROGRESS）。

### R3-06｜开工后过期作业失效 — **PASS**

**根因**：`jobs.py::JOB_REQUIRED_STATES["APPOINTMENT_UPCOMING"]={"SCHEDULED","IN_PROGRESS","AWAITING_ACCEPTANCE"}`；进入 IN_PROGRESS 后已过期作业仍命中 IN_PROGRESS 状态，仍触发开始前通知；执行时未核验预约有效性、轮次、时刻。

**修复**：
- `jobs.py::JOB_REQUIRED_STATES`：`APPOINTMENT_UPCOMING` / `APPOINTMENT_UPCOMING_REPORTER` 收紧到 `{"SCHEDULED"}`（不再包含 IN_PROGRESS / AWAITING_ACCEPTANCE）。
- `commands/__init__.py::start_progress` body 内 `_cancel_pending_jobs(conn, task_id)`：开工作废本任务所有 PENDING 作业（含 UPCOMING/UPCOMING_REPORTER/OVERDUE）。
- `jobs.py::run_due_jobs` 发送前再核验：
  - UPCOMING 类：存在有效 `CONFIRMED` 预约且 `now < appt.start_at_ms`（已过开始时间的开始前提醒作废）；
  - ACCEPTANCE_DUE：存在对应 `round` 的 `repair_completions`（不存在的轮次作废）。
- 重复 tick / 重启后恢复：原有去重键（`repair_jobs.dedupe_key` UNIQUE INDEX）保证；`JOB_REQUIRED_STATES` 在 schedule 与 run_due_jobs 共用。

**验证**：
- 探针 `r3_06_start_progress_invalidates`：进入 IN_PROGRESS 后再 tick 开始前通知数增量 0。
- pytest `test_round4_repair.py::test_r3_06_*`：4 项 PASS（开工作废 / 积压 0 触发 / 正常预约提醒恰好一次 / 验收 round 不匹配作废）。
- 上轮 R2-07 round3 测试仍 PASS（`test_r2_07_completed_no_more_notifications`、`test_r2_07_round2_resets_acceptance_due`、`test_r2_07_terminal_state_cancels_jobs`）。

### R3-07｜撤权接收者不产生/读取新通知 — **PASS**

**根因**：`jobs.py::run_due_jobs` 仅按 `JOB_REQUIRED_STATES` 校验 + 写通知，未验证 `payload.user_id` 当前仍是该项目成员且对该任务有可见权；`api/__init__.py::list_notifications` 仅按 `user_id` 过滤，未做对象可见性投影。

**修复**：
- `jobs.py::run_due_jobs`：再校验 `auth.roles_of(cur, user_id, task_row.project_id)` 非空，且 `auth.task_visible(cur, user_id, task_row)` 为真；否则作业 CANCELLED，不写通知。
- `api/__init__.py::list_notifications`：按 task_id 拉任务行，按当前 `auth.task_visible(actor, task_row)` 投影；已撤权/不可见任务的通知不返回。

**验证**：
- 探针 `r3_07_revoked_recipient`：撤权后 run_due_jobs 不产生 R1 的 A 任务通知；`/notifications` 接口不返回该任务的旧通知。
- pytest `test_round4_repair.py::test_r3_07_*`：3 项 PASS（无新通知 / API 不泄露 / 立法接收者仍收）。
- 上轮 R2-08（tick 已 reject） / R2-07（通知过滤） 仍 PASS。

### R3-08｜原生最小能力探针 — **BLOCKED**

**修复**：
- `app/docs/round4_native_probe.py`：静态分析 `app/bundle/main.splash` + `app/bundle/manifest.json`：
  - addEvidence 已移除 `bytes:32 / sha:id-sha`，写 `bytes:0, sha:"", ready:false` 占位 + `note: "宿主 picker/隔离存储缺失；待真实文件获取能力接通"`；按 §一硬约束"未存文件不得写 READY；失败不半写"。
  - 命令守门 `settle()` 仍存在；显式记录 `upload_evidence_blocked` 事件而非假装 ready。
- `app/docs/round4_native_probe.md`：保留 picker / set_visible / on_render / manifest.digest 仍未在脚本层验证为已支持；不擅自宣称 PASS。

**状态**：R3-08 仍 BLOCKED。
- 真实点击提交 → OPEN：BLOCKED（宿主 set_visible/on_render 缺口）。
- 上传真实文件 / 读回字节 SHA 一致 / 缺失损坏不能产生 READY：已阻止（`ready:false`）；但 picker 缺失 → 仍 BLOCKED。
- Hub digest：bundle sha256 已变（脚本修复后 `8abc71f7…`），与 manifest 声明 `c066a517…`（b3） 算法不一致；本轮不擅自重新打戳。

## 三、回归与全量验证

| 步骤 | 命令 | 结果 |
|---|---|---|
| C1 | `backend/.venv/bin/python -m pytest backend/tests/` | **424 passed**（165 octosense + 234 其他 + 25 新 R3 round4）在 65.94s |
| C2 | `backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py` | **11 PASS / 0 FAIL**（V01-V11 + V08b） |
| C3 | `backend/.venv/bin/python backend/scripts/e2e_full_chain.py` | **E2E PASS · 17 步**（含 R3-01 update_draft） |
| C4 | `backend/.venv/bin/python runtime/repair-round4-20261003/probe_round4.py --json runtime/repair-round4-20261003/probe_round4.json` | **7 PASS / 0 FAIL**（R3-01 ~ R3-07） |
| C5 | `backend/.venv/bin/python app/docs/round4_native_probe.py` | OK 5 项 / fail=0（脚本内 bytes/sha 写死已清除；picker / set_visible / on_render 仍 BLOCKED） |
| C6 | `backend/.venv/bin/python backend/scripts/e2e_full_chain.py`（重跑） | **E2E PASS · 17 步** |

源码哈希端点：`runtime/repair-round4-20261003/`（待落 source-start/end.sha256；本轮交付件集中在 probe_round4.json 与 probe_round4.log）。

## 四、与上一轮 V01–V11 + R2-01~R2-10 对照

| 上轮项 | 本轮结论 |
|---|---|
| V01 原生准入/求值/业务统一 | 仍 PASS；R3-08 单独跟踪宿主缺口（BLOCKED） |
| V02 对象可见性与隐私 | 仍 PASS；R3-04 history-advice 一并收紧 |
| V03 技工 OPEN 列表 | 仍 PASS；无回归 |
| V04 IN_PROGRESS 设备权限 | 仍 PASS；R3-05 unbind 与 bind 同矩阵 |
| V05 幂等冲突/完整回执 | 仍 PASS；R3-01 update_draft 同框架 |
| V06 改约/过期 | 仍 PASS；R3-06 收严 JOB_REQUIRED_STATES + start_progress 主动取消 |
| V07 asset: 稳定 ID | 仍 PASS；无回归 |
| V08 附件完整性 | Python 端仍 PASS；R3-08 原生侧 addEvidence 写 `ready:false` 阻止伪完工 |
| V09 提交/技能/服务关系 | 仍 PASS；R3-02 撤权矩阵覆盖 bind |
| V10 严格类型/路径 | 仍 PASS；R2-10 时钟前置校正 |
| V11 测试与证据可靠性 | 仍 PASS；本轮新增 25 项 R3 round4 回归 |
| R2-01 原生提交/原始包 digest | 仍 BLOCKED；R3-08 已静态分析 + 移除假元数据 |
| R2-02 原生证据上传 | 仍 BLOCKED；R3-08 addEvidence 改 `ready:false` |
| R2-03 Web 表单 space 补齐 | 仍 PASS；R3-03 增 category + bind 入口 |
| R2-04 联系人脱敏 | 仍 PASS；R3-04 history-advice 也覆盖 |
| R2-05 撤权 / 回放拒绝 | 仍 PASS；R3-02 收紧全部首次执行 |
| R2-06 start_progress 仅作废当前任务 | 仍 PASS；R3-06 进一步开工作废 PENDING |
| R2-07 提醒生命周期 | 仍 PASS；R3-06 收严 JOB_REQUIRED_STATES |
| R2-08 全局 tick 越权 | 仍 PASS；R3-07 加撤权接收者校验 |
| R2-09 bind_asset 阶段矩阵 | 仍 PASS；R3-05 unbind 同步 |
| R2-10 HTTP tick 应用时钟 | 仍 PASS；R3-06 / R3-07 不破坏 |

## 五、未通过项与剩余阻断

| 阻断 | 最小复现 / 缺口 | 下一步 |
|---|---|---|
| R3-08 原生 picker / set_visible / on_render | `app/bundle/main.splash` 未调用 picker；`set_visible/on_render` 仍被宿主忽略；addEvidence 改为 `ready:false` 占位 | 等宿主版本补齐 picker / on_render 实例化，或换构建版本；本轮按 §一禁止回退假元数据 |
| Hub bundle digest REFUSED | `app/bundle` sha256 `8abc71f7…` ≠ manifest 声明 `c066a517…`（b3）；本轮不擅自重新打戳 | 由用户授权的 Hub 提交流程签出 |
| --ready 仍 NOT READY | T28 FAIL 由 R2-01/R2-02 阻断 + R3-08 同因 + 12 UI/U 真人验收 + T24 旧入口统一边界 + 模型/官方身份未授权 | 等用户授权 |
| T29 | 仍为 FAIL（按本轮规则保持） | 等用户提供 host session 凭证 |
| G0 / T01 / T25 / T26 / T33-T38 | 真实模型 / 官方身份未授权 → 保持 NOT_RUN | 等用户授权 |

## 六、文档与台账同步

- `docs/build-loop/ACCEPTANCE.json` 不重写 verdict；note 字段追加本轮摘要："2026-10-03 R4：R3-01/02/03/04/05/06/07 已修，回归 25 项 R3 round4 + 165 octosense + 234 其他；R3-08 原生仍 BLOCKED（宿主 picker 缺口，addEvidence 已写 ready:false 占位）。"
- 本文件 `REPAIR_RESULT_2026-10-03_ROUND4.md` 即本轮交付件。
- `runtime/repair-round4-20261003/probe_round4.json` 为本轮独立探针输出。
- `app/docs/round4_native_probe.{py,md}` 为 R3-08 静态能力探针与说明。

## 七、可交付内容

- 本地可检查代码（`backend/src/octosense_backend/{commands,extended,jobs,api}`、`app/bundle/main.splash`、`app/demo-web/static/workbench.html`）已交付；本轮 git status 未提交，按用户授权要求保留为本地可检查改动。
- 修复报告：本文件 + `runtime/repair-round4-20261003/probe_round4.json` + `app/docs/round4_native_probe.{py,md}`。
- 已知限制与剩余阻断见 §五。

**本轮 R3-01~R3-07 修复状态**：**7 项 PASS**；**R3-08 BLOCKED（宿主缺口）**。
**项目整体就绪**：未达 `--ready`（同 §五），**不是本轮可独立完成的项**。