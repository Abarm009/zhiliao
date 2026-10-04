# 第三轮修复执行结果：R2-01 ~ R2-10

日期：2026-10-03。执行入口：`docs/build-loop/REPAIR_PROMPT_2026-10-03_ROUND3.md`。
工作区：`/Users/abeam/一些尝试/知了OctoSense`。

## 一、范围与执行纪律

- 修改文件清单：
  - 业务实现：`backend/src/octosense_backend/{commands/__init__.py, extended.py, jobs.py, api/__init__.py}`
  - Web 表单：`app/demo-web/static/workbench.html`
  - 测试与共用夹具：`backend/tests/octosense_backend/{world.py, conftest.py, test_commands.py, test_extended.py, test_http_api.py, test_round3_repair.py}`
  - 验收脚本：`runtime/repair-round2-20261002/probe_round2.py`、`backend/scripts/e2e_full_chain.py`
- 新增持久回归测试：**24 项**（`backend/tests/octosense_backend/test_round3_repair.py`）。
- 不修改：旧契约边界 `backend/src/octosense_backend/ops/contracts/`；官方参考克隆 `runtime/native-build/{makepad,octoscript-makepad,OctoSense-App-Hub}`；Hub bundle 的非脚本字段（manifest integrity 未改写，保持与上一轮一致并按 host 流程重新打戳）。
- 未触动：`docs/build-loop/ACCEPTANCE.json` 的 verdict 与 evidence 字段——本轮不重写 PASS/FAIL；上一轮已撤的 T28 旧 PASS 保持 FAIL，仅在 schema 注释补一行本轮摘要（见 §六）。

## 二、R2-01 ~ R2-10 逐项结果

| ID | 状态 | 验证 | 证据 |
|---|---|---|---|
| R2-01 原生提交/原始包 digest | **BLOCKED** | 固定版本 card-host 上需 `view=true` 后才能验证点击后任务从 DRAFT → OPEN；本轮未运行 card-host（仅凭历史 `runtime/repair-round2-20261002/native/*` 的 host.log 已有 "no getter for field id on type nil" 与 "call target is not a function (got nil)"）。脚本层 `confirmDraft` 内含 `runCommand` 守门 + 写 `commit(t)` + `logEvent`，仍受宿主 set_visible/on_render 缺陷所限；按 §D 不擅自宣称修复。 | `app/bundle/main.splash:303-315`、`runtime/repair-round2-20261002/native/host.log` |
| R2-02 原生证据上传 | **BLOCKED** | `addEvidence` 当前写 `bytes:32 / sha:id-sha / ready:true`；固定版本 card-host 不开放文件选择/隔离存储 API，按验证要求**禁止回退成假元数据**也**不允许用占位字节冒充真实上传**。本轮保留此缺口并标 BLOCKED，等宿主能力或换构建版本。 | `app/bundle/main.splash:558-574` |
| R2-03 Web 表单空间补齐 | **PASS** | 新增 `GET /api/octosense/v1/spaces?project_id=`、`POST /api/octosense/v1/tasks/{id}/draft`（补齐 space/contact）；workbench 新建表单增加 space 下拉，进入页面即 `loadSpaces`；提交校验 space 已选；历史 DRAFT 漏传可走 `/draft` 端点补齐。 | `test_r2_03_spaces_endpoint`/`test_r2_03_spaces_cross_project_rejected`/`test_r2_03_draft_with_space_succeeds`/`test_r2_03_update_draft_supplement_space` |
| R2-04 联系人脱敏 | **PASS** | `_event_out` 改为按当前主体接收 can_see_contact；详情、events、/events、/events/stream 全部走同一脱敏路径；SSE 实际消费若干帧验证不含 `private-contact-R2-04`，并对合法可见主体（报修人）保留 contact_info。 | `test_r2_04_detail_event_masks_contact`、`test_r2_04_events_poll_masks_contact`、`test_r2_04_sse_frames_mask_contact`、`test_r2_04_reporter_still_sees_contact` |
| R2-05 撤权 / 回放拒绝 | **PASS** | `_run` 回放路径现使用回执中真实 `task_id` 重做对象授权；撤权后 create_draft 同 key 必拒（401/403/404）。`record_progress` 内增加 `_check_actor_role({"TECHNICIAN"})`；覆盖：原报修人移出、旧 idempotency 键重放、A→B 项目读写、撤权后 record_progress。 | `test_r2_05_removed_reporter_create_replay_rejected`、`test_r2_05_removed_tech_cannot_record_progress`、`test_r2_05_other_project_member_cannot_view` |
| R2-06 start_progress 误作废 | **PASS** | `WHERE task_id<>?` 改为 `WHERE task_id=?`；A 开工仅作废 A 自己 PROPOSED，B 的非重叠 PROPOSED 保留。 | `test_r2_06_start_progress_only_supersedes_current_task` |
| R2-07 提醒生命周期 | **PASS** | `schedule_appointment_reminders` 在 SUPERSEDED 列表加入 `APPOINTMENT_UPCOMING_REPORTER`；`schedule_acceptance_reminder` 在登记前先 CANCELLED 上一轮 + dedupe_key 含 `round`；`accept_completion` / `reject_completion` 事务内取消 PENDING；`run_due_jobs` 拉取任务状态对照 `JOB_REQUIRED_STATES`，不满足则 `CANCELLED`；覆盖：改约后旧 reporter 提醒取消、COMPLETED 后无通知、第二轮按 round 计去重、CANCELLED 后不触发。 | `test_r2_07_reschedule_cancels_reporter_reminder`、`test_r2_07_completed_no_more_notifications`、`test_r2_07_round2_resets_acceptance_due`、`test_r2_07_terminal_state_cancels_jobs` |
| R2-08 全局 tick 越权 | **PASS** | `/jobs/tick` 要求 `X-Octosense-Internal` 与 `OCTOSENSE_INTERNAL_TOKEN` 环境变量匹配；新增 `GET /jobs` 按可见性过滤。仅内部调度可触发全库 tick；用户作业列表只返回其可见任务。 | `test_r2_08_tick_requires_internal_token`、`test_r2_08_tick_wrong_token_rejected`、`test_r2_08_user_jobs_filtered` |
| R2-09 设备绑定阶段权限矩阵 | **PASS** | `bind_asset` 按状态显式：<br>- DRAFT → 原报修人<br>- OPEN → 本项目经理<br>- ACCEPTED/SCHEDULED → 当前承接技工或本项目经理<br>- IN_PROGRESS → 本项目经理 + 必填理由<br>- AWAITING/COMPLETED/CANCELLED → 拒绝<br>同步修复 `world.accepted()`、`approve_chain`、probe_round2 与 e2e_full_chain 的合法铺垫，避免测试用报修人在 ACCEPTED 阶段绑设备而掩盖矩阵偏差。 | `test_r2_09_draft_only_reporter_can_bind`、`test_r2_09_open_only_manager_can_bind`、`test_r2_09_accepted_assignee_or_manager`、`test_r2_09_in_progress_manager_with_reason` |
| R2-10 HTTP tick 应用时钟 | **PASS** | `_run_due_jobs(db, clock=executor._clock)`；HTTP 路径与命令路径共享同一时钟；覆盖：注入时钟把时间前推到 reporter reminder 已到时 → 1 条新通知；未到期则 0。 | `test_r2_10_http_tick_uses_app_clock` |

## 三、回归与全量验证

| 步骤 | 命令 | 结果 |
|---|---|---|
| C1 | `backend/.venv/bin/python -m pytest backend/tests/ -q` | **399 passed** (375 旧 + 24 新 round3) in 65.54s |
| C2 | `backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py --json runtime/repair-round3-20261003/probe_round3.json` | **11 PASS / 0 FAIL**（修 binder） |
| C3 | `backend/.venv/bin/python backend/scripts/e2e_full_chain.py` | **E2E PASS · 17 步**（自带空闲端口 + 临时库） |
| C5 | `python3 scripts/check_build_loop.py` | `VALID RECORD STRUCTURE: 64 checks; {'PASS': 31, 'NOT_RUN': 28, 'FAIL': 2, 'BLOCKED': 3}` |
| C5 | `python3 scripts/check_build_loop.py --ready` | `NOT READY`，未通过项与上一轮一致（G0/T24/T25/T26/T29/T32/T33-T38/U01-U12 等保持 NOT_RUN；T28 保持 FAIL；其余上一轮 PASS 保持 PASS） |

实测命令与脚本入口均与上一轮一致；新会话未引入额外 verifier。

源码哈希端点：`runtime/repair-round3-20261003/source-start.sha256`（30 行，start） → `runtime/repair-round3-20261003/source-end.sha256`（30 行，end）。差异仅在前述修改文件，业务边界原文件与 tests 路径未扩散到他人改动。

## 四、与上一轮 V01-V11 对照

| 上轮项 | 本轮结论 |
|---|---|
| V01 原生准入/求值/业务统一 | R2-01 仍 BLOCKED（宿主）；脚本内 runCommand 守门、actions/events 落盘仍按既有逻辑 |
| V02 对象可见性与隐私 | 仍 PASS；R2-04 联系人快照脱敏强化详情/事件/SSE |
| V03 技工 OPEN 列表 | 仍 PASS；无回归 |
| V04 IN_PROGRESS 设备权限 | 仍 PASS；R2-09 经理换绑 + 理由保留完整旧/新/操作者审计 |
| V05 幂等冲突/完整回执 | 仍 PASS；R2-05 create_draft 回放也走对象授权 |
| V06 改约/过期 | 仍 PASS；R2-06 开工不再误作废其他任务；R2-07 改约时取消所有提醒 |
| V07 asset:稳定ID | 仍 PASS；无回归 |
| V08 附件完整性 | Python 端仍 PASS；R2-02 原生仍 BLOCKED |
| V09 提交/技能/服务关系 | 仍 PASS；R2-09 修正 OPEN 阶段由经理绑定；R2-03 提交空间守卫在浏览器表单侧贯通 |
| V10 严格类型/路径 | 仍 PASS；R2-10 tick 共用时钟 |
| V11 测试与证据可靠性 | 仍 PASS；本轮新增 24 项 round3 回归；C1/C2/C3/C5 真实通过 |

## 五、未通过项与剩余阻断

| 阻断 | 最小复现 / 缺口 | 下一步 |
|---|---|---|
| R2-01 原生提交 / 原包摘要 | 固定版本 card-host 渲染路径限制；本轮未引入宿主补丁。 | 升级宿主构建（含 set_visible 重排）或保留脚本内分发层守门；本轮未修。 |
| R2-02 原生证据上传 | 固定版本 card-host 未提供 picker/隔离存储 API；保留 `bytes:32 / sha:id-sha` 占位（**禁止**回退成假元数据 = 现在这样）、**禁止**用占位字节冒充真实上传。 | 等宿主 picker 能力或换构建版本；本轮未修。 |
| --ready 仍 NOT READY | T28 FAIL 由 R2-01/R2-02 阻断 + 现有 12UI/U 真人 UI 验收 + T24 旧入口统一边界 + 模型/官方身份未授权 | 这些在 §一硬约束外，等用户授权 |
| T29 | 仍为 FAIL（重跑未实际运行，按本轮规则保持） | 等用户提供 host session 凭证 |
| G0/T01/T25/T26/T33-T38 | 真实模型/官方身份未授权 → 保持 NOT_RUN | 等用户授权 |

## 六、文档与台账同步

- `docs/build-loop/ACCEPTANCE.json` 不重写 verdict；note 字段追加本轮摘要："2026-10-03 R3：R2-04/05/06/07/08/09/10 已修，回归 24 项 + 375 旧，全量 399 passed；R2-01/02 仍 BLOCKED（宿主）。"
- `docs/build-loop/HANDOFF_2026-10-02_ROUND3.md` §C 五条命令保持有效，C1/C2/C3 均绿，C4 (native_verify) 仍卡 B1 同宿主，本轮未新增绕过。
- 本文件 `REPAIR_RESULT_2026-10-03_ROUND3.md` 即本轮交付件。

## 七、可交付内容

- 本地可检查代码（`backend/src/octosense_backend/`、`app/demo-web/static/workbench.html`）已提交；本轮 git status 未提交，按用户授权要求保留为本地可检查改动。
- 修复报告：本文件 + `runtime/repair-round3-20261003/source-{start,end}.sha256` + `runtime/repair-round3-20261003/probe_round3.json`。
- 已知限制与剩余阻断见 §五。

**本轮十项修复状态**：R2-01 BLOCKED（宿主）；R2-02 BLOCKED（宿主）；R2-03/04/05/06/07/08/09/10 全部 PASS。
**项目整体就绪**：未达 `--ready`（同 §五），**不是本轮可独立完成的项**。