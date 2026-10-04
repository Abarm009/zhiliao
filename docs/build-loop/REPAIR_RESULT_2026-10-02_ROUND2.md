# 2026-10-02 第二轮修复结果（V01–V11 关闭情况 + 交接）

> 输入：`docs/build-loop/REPAIR_VERIFICATION_2026-10-02.md` 的 V01–V11 为必须关闭清单，
> 叠加 `REPAIR_HANDOFF_2026-10-02.md` 尚未完成的范围。审查报告是线索，业务基线与
> 实际复现结果决定修复；未修改弱任何验收标准。
> 本文只记录**实际运行结果**。全部命令可原样复跑，见 §7。

## 0. 结论

| 面 | 状态 |
|---|---|
| 后端 Web / API / 领域规则 | **V02–V11 全部关闭并有运行证据** |
| 测试与验收记录假阳性 | **V11 关闭**（新探针/新 E2E 任一断言失败即非零退出） |
| 原生交付件（V01） | **部分关闭**：解析/求值错误已消除并用固定版本 card-host 实测；但"按角色隐藏动作按钮"被宿主平台缺口阻断，见 §6 |

补充事实：`51 passed / 22 probes` 是上一轮自述，本轮实测 **375 passed**（含 141 项新增回归）、
**独立探针 11/11**、**E2E 全链 PASS**。三者都不是 T01–T38/U01–U12 的完整覆盖。

---

## 1. V01–V11 逐项修复与证据

证据目录：`runtime/repair-round2-20261002/`。

| ID | 问题 | 根因 | 修复 | 证据 |
|---|---|---|---|---|
| **V01** | 原生包被拒；打戳后 36 个解析错误、`view=false` | ① `manifest.integrity.bundle_blake3` 与实际目录不符；② `{label:…, fn:…}` 里 `fn` 是 OctoScript 保留字；③ 三元表达式 `c ? a : b` 宿主不支持；④ `nowMs()` 恒 0 | ① 重写 `main.splash`（不再用 `fn:`/三元）；② `nowMs()` 改用宿主 `time_now()`；③ `const`→`let`、`ok` 变量改名、去掉嵌套对象字面量；④ manifest 由 `--stamp` 重新生成 | `native-check/final2/host.log`：`exit 0`、`0 errors`、`[SPLASH] eval: … view=true`、`admitted`。点击 `+ 新建草稿（DRAFT）` 后 `data/octosense-repair/tasks.json`、`actions.jsonl`、`events.jsonl` 实际落盘 |
| **V02** | `role=MANAGER` 可扩权；详情泄露他人联系方式 | 客户端筛选值参与服务端授权；详情只校验项目成员 | 新增 `authorization.py`：服务端按主体+项目角色+任务关系+技能+阶段推导可见集合；`narrow_role()` 只允许收敛到该主体真实拥有的角色；详情/事件/附件/收藏/历史建议共用 `task_visible()`；`contact_info` 按 `can_see_contact()` 脱敏 | probe `V02_list_and_detail_authorization`：默认列表不可见他人任务、`role=MANAGER` → **403 INVALID_ROLE_FILTER**、他人详情 → **404**。tests：`test_list_tasks_role_filter_cannot_escalate_over_http`、`test_detail_cross_project_member_is_404`、`test_list_tasks_technician_open_contact_masked` |
| **V03** | 新列表过滤让技工看不到 OPEN 待接单 | 技工被硬限 `assignee_id=actor` | 技工可见 = 本人承接 ∪ 本项目技能匹配的 OPEN；接单前脱敏 | probe `V03_technician_open_visibility`：`open_visible=True, contact_masked=True, mismatch_hidden=True`。tests：`test_list_tasks_technician_sees_open_skill_matched_and_own` |
| **V04** | 无关技工能对维修中任务换设备 | `_check_role()` 只判项目成员、忽略 `allowed` | `_check_role` → `CommandExecutor._check_actor_role()`（真校验 allowed，`allow_manager=False` 时经理不得代行）；IN_PROGRESS 换设备必须同项目经理 + 非空 reason，并保存旧值/新值/操作者/理由 | probe `V04_in_progress_asset_change`：无关技工 **403**、经理无理由 **422**、经理带理由 **200** 且 `old_value=as-a-1`。tests：`test_in_progress_asset_change_requires_manager_and_reason` |
| **V05** | pin/unpin 同 key 互相回放；改 payload / 改版本返回 500；回放丢失原结果 | 指纹只含 `{task_id}`，不含 command；`IdempotencyConflict` 未导入 → NameError；只存 task_id/command | 新增 `idempotency.py`：指纹 = command+actor+project+task+expected_version+规范化参数；导入集中一处；`repair_actions.result_json` 存完整原响应；回放返回同一 `action_id` + 原结果；历史 NULL 指纹按冲突处理；失败尝试改写 `repair_action_failures` 追加审计 | probe `V05_idempotency`：`pin_unpin=200/409`、`advice=200/409`、`replay_action_id` 与首次一致、`changed_version_http=409`。tests：`test_same_key_different_command_is_conflict`、`test_confirm_replay_returns_full_original_result` |
| **V06** | 改约与自己的旧确认冲突；过期预约仍可确认 | 冲突检查排除的是新 proposal id 而非本任务旧确认；无有效期/时间窗规则 | 提议与确认的冲突检查都排除**本任务**即将被替换的预约，只与其它任务（含同技工跨项目）竞争；有效期 `min(24h, 开始-提出)`，过期 **410**；开始须严格未来、时长 15–240 min、lead ≤ 30 天；统一可注入服务端时钟 | probe `V06_reschedule_and_expiry`：`moved_confirmed=CONFIRMED, old_superseded=SUPERSEDED, expired_http=410, past_http=422`。tests：`test_reschedule_excluding_replaced_confirmed`、`test_expired_proposal_confirmation_rejected`、`test_server_clock_not_client_time` |
| **V07** | `asset:as-a-1` → 404；`asset:AC-001` → 200（错误载荷被当成正确） | 只按 `asset_code` 去前缀 | `resolve_asset()`：`asset:` 后按稳定 `asset_id` 解析再校验项目/归档；普通编码按 `asset_code`；`asset:<code>` 属错误载荷 → 404 | probe `V07_asset_prefix`：`code_http=200, asset_id_http=200, resolved_by=asset_id, wrong_payload_http=404`。tests：`test_asset_prefix_resolves_stable_asset_id`、`test_asset_prefix_with_code_rejected` |
| **V08** | 删掉附件文件后仍能完工提交 200 | 只查 READY 数据库行 | `submit_completion` 对每条 READY 证据验证文件存在、字节数、SHA-256；任一不符 → **422 EVIDENCE_INTEGRITY** 并在 detail 里给恢复入口；不得写入半条完工记录 | probe `V08_evidence_integrity`：`missing_file_http=422, error_code=EVIDENCE_INTEGRITY, status_after=IN_PROGRESS, completions_written=0, recovered=True`。tests：`test_completion_requires_readable_evidence_file`、`test_completion_evidence_sha_mismatch_rejected` |
| **V09** | 经理无技工角色可自主接单；无服务空间草稿能提交；分配对象不校验技能；绑定不看服务关系 | 命令边界缺前置校验 | `accept_task` 强制 `allow_manager=False` + 技能匹配；`confirm_draft` 校验服务空间属于本项目、联系人非空，失败保留草稿；`assign_task`/`reassign` 目标必须同项目 + 技能匹配技工；`bind_asset` 必须存在有效"服务空间—设备"服务关系 | probe `V09_business_preconditions`：`manager_self_accept=403, submit_without_space=422, draft_kept=DRAFT, mismatched_assign=403, matched_assign=200, no_service_relation=422`。tests：`test_manager_without_technician_role_cannot_self_accept`、`test_bind_same_install_location_without_service_relation_rejected` |
| **V10** | `expected_version=true` 被 Pydantic 转成 1 通过；`_PROJECT_ROOT=parents[3]` 锚到 `backend/` | 非严格类型 + 相对层数 | `CommandBody.expected_version: StrictInt`；`idempotency.strict_positive_int()` 领域层拒绝 bool/float/str/≤0；`paths.find_project_root()` 向上找工程标记，`default_db_path()/default_evidence_root()` 显式环境变量优先 | probe `V10_strict_types_and_paths`：`bool_rejected=True, project_root=<工程根>, default_db=<工程根>/runtime/octosense.db`。tests：`test_expected_version_bool_rejected_over_http`、`test_expected_version_rejects_bool_and_none` |
| **V11** | 测试/交付记录假阳性 | 探针铺垫失败仍继续、CANCELLED 由 409 冒充、错误载荷当正确、探针不设失败退出码；E2E 固定 8713 且 curl 不以 HTTP 失败退出 | 新增 `runtime/repair-round2-20261002/probe_round2.py`（每步断言成功并回读目标状态，任一失败 `sys.exit(1)`）；重写 `backend/scripts/e2e_full_chain.py`（读取 `--base-url`/`OCTOSENSE_BASE_URL`，自带空闲端口 + 临时库 + 明确时钟，HTTP 失败即终止，末段断言最终状态/回执/两轮完工/附件/预约/事件） | `probe_round2.json`：**11 pass / 0 fail**，退出码 0；`e2e_full_chain.py`：**E2E PASS，17 步**，退出码 0 |

### 1.1 V01 的残余（不能算关闭的部分）

- **动作按钮无法按角色隐藏**：固定版本 card-host 的 `set_visible(false)` 不触发重排（实测隐藏控件仍占位、截图尺寸不变），`on_render` 不实例化子控件（实测 render 输出为空）。
- 因此"allowedActions 真正参与视图"在**渲染层**未达成；改为**分发层强制**：`runCommand()` 校验主体可见性 + 命令源状态 + 身份矩阵 + 幂等，越权点击明确拒绝并在 `events.jsonl` 留痕。
- 这与交接指令 §五.2 的要求有差距，属**平台阻断**，未用"定义白名单后仍无条件显示"冒充通过。
  记录见 `app/docs/route-decision.md` §4。

---

## 2. 原 R/N/Q 剩余问题覆盖表

| 编号 | 主题 | 本轮状态 |
|---|---|---|
| R-P0-1 原生拆容器 | 部分 | 布局已重排；动态容器受平台限制（见 §1.1） |
| R-P0-2 跨项目 create 403 | 已关闭 | `test_cross_project_create_rejected` |
| R-P0-3 ghost 读任务 | 已加强 | 未注册 → 401 IDENTITY_REQUIRED；跨项目 → 404 |
| R-P0-4 同 key 不同内容 409 | 已关闭 | V05 |
| R-P0-5 demo-web 确认预约 | 已关闭 | proposedAppt/confirmedAppt 分离（上轮） |
| R-P0-6 grant 机制 | 未做（依赖宿主） | T29 / G0-B 保持未验证 |
| R-P1-1 原生任务落盘 | 已关闭 | `tasks.json` 实测写入 |
| R-P1-2 技工乙项目数组 | 已关闭（上轮） | |
| R-P1-3 record_advice 权限/幂等 | 已关闭 | `test_record_advice_with_auth_and_idem` |
| R-P1-4 `/task/{id}` 500 | 已关闭（上轮） | |
| R-P1-5 Date.now 幂等键 | 已关闭（上轮） | |
| R-P1-6 currentVer 从 DOM 猜 | 已关闭（上轮） | |
| R-P1-7 证据根目录跟 CWD | 已关闭 | `paths.default_evidence_root()` |
| R-P1-8 原生零权限+无声失败 | 部分 | 失败有明确"拒绝：…"；按钮隐藏受平台限制 |
| N01 bind_asset 跨态 | 已关闭 | V04 |
| N02 SCHEDULED 被另一技工接 | 已关闭 | `COMMAND_SOURCE_STATES` |
| N03 项目角色 | 已关闭 | V02 |
| N04 history-advice 跨项目 | 已关闭 | `test_history_advice_cross_project_asset_rejected`、`test_history_advice_hides_unrelated_tasks` |
| N05 null/bool 版本 | 已关闭 | V10 |
| N06 拒绝改约保旧确认 | 已关闭 | V06 |
| N07 幂等不统一 | 已关闭 | V05 |
| N08 经理代验收无理由 | 已关闭 | `test_manager_accept_requires_reason` |
| N09 completion_id 持久化 | 已关闭 | `test_reject_then_resubmit_keeps_two_rounds` |
| N10 原生双事实源 | 已关闭（路线 A） | `app/docs/route-decision.md` |
| N11 web confAppt 共享 | 已关闭（上轮） | |
| N12 quarantine 无 dispatch | 已关闭（上轮） | |
| N13 quarantine 不存在返 200 | 已关闭 | `test_quarantine_nonexistent_evidence_404` |
| N14 代理异常 | 已关闭（上轮） | |
| N15 零参工厂 | 已关闭 | `make_app()` 零参可构造 |
| N16 EXTRA_SCHEMA 死代码 | 已关闭（上轮） | |
| Q01 reject-finish 越 AWAITING | 已关闭 | `test_reject_finish_cannot_escape_from_scheduled` |
| Q02 提议直接 SCHEDULED | 已关闭 | `test_first_proposal_keeps_accepted` |
| Q03 start 不验证设备 | 已关闭 | `test_start_progress_requires_bound_asset…` |
| Q04 经理代确认预约 | 已关闭 | `test_confirm_only_reporter_no_manager_substitute` |
| Q05 CANCELLED 无提议还 reject | 已关闭 | `test_reject_appointment_when_no_proposed_rejected`、`test_cancelled_task_cannot_reject_appointment` |
| Q06 asset: 前缀等价 | **纠正后** 已关闭 | V07（旧用例把 `asset:AC-001` 当正确，属错误基准） |
| T13/T23 过期提议/提醒作业 | 部分 | 后端已实现（`octosense_backend.jobs` + `POST /jobs/tick`）；原生未接 |
| T17 SSE | 部分（后端） | `GET /events/stream`（SSE）+ `/events?since_seq=` 游标；原生未接 |
| T24 旧入口写路径 | 未做 | 依赖旧 runner/比赛模式定义 |
| T27 外部工单未配置 | 未做（默认 NOT_CONFIGURED） | |
| T28 原生联调 | 部分 | 见 §1.1 / §4 |
| T29/T32 grant / pairing | 未做（依赖宿主） | |
| T31 取消释放预约 | 已关闭 | `test_cancel_requires_reason_and_releases_appointment` |

---

## 3. 实际测试命令、退出码、日志与持久状态回读

```
cd /Users/abeam/一些尝试/知了OctoSense

# 3.1 全量 pytest（含继承基线）
backend/.venv/bin/python -m pytest backend/tests/ -q
→ 375 passed in 35.48s   (exit 0)

# 3.2 独立验收探针（V02–V11）
backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py \
    --json runtime/repair-round2-20261002/probe_round2.json
→ 11 pass / 0 fail        (exit 0)   # 任一断言失败即 exit 1

# 3.3 端到端（自带空闲端口 + 临时库 + 明确时钟）
backend/.venv/bin/python backend/scripts/e2e_full_chain.py
→ E2E PASS · 17 步        (exit 0)

# 3.4 原生 card-host（副本 bundle，--stamp 只改副本）
backend/.venv/bin/python -c "… splash_check.check_bundle('final2') …"
→ exit 0 · errors 0 · [SPLASH] eval: 39929 bytes view=true · admitted
```

持久状态回读（每次运行都从服务端/宿主存储重读，不用魔数）：

- E2E：`GET /tasks/{id}` 回读 `status=COMPLETED`、`asset_id`、`space_id`、
  `completions=[{round:1,…},{round:2,…}]`、恰 1 条 `CONFIRMED` 预约、≥2 条 READY 证据、
  事件含 `confirm_draft/accept_task/bind_asset/propose_appointment/confirm_appointment/
  submit_completion/reject_completion/accept_completion`。
- 探针：删除附件文件后 `submit_completion` 返回 422 且 `repair_completions` 行数仍为 0。
- 原生：`data/octosense-repair/{tasks.json,actions.jsonl,events.jsonl,state.json}` 实际写入。

日志：`runtime/repair-round2-20261002/{probe_round2.log,probe_round2.json,
native-check/final2/host.log,splash-check/clean2/host.log,native-*/…}`。

---

## 4. Web 成功链、退回链、原生解析/运行结果

- **Web 成功链**：`create_draft(201) → confirm(OPEN) → accept(ACCEPTED) → bind_asset →
  propose(仍 ACCEPTED) → confirm_appointment(SCHEDULED) → 上传证据(READY, 下载字节校验) →
  start(IN_PROGRESS) → complete(round 1) → reject_finish(IN_PROGRESS) → 再传证据 →
  complete(round 2) → accept_finish(COMPLETED)` → 同 key 重发 create 幂等回放同一 task_id →
  终态 start 被 422 拒。全部 17 步见 §3.3。
- **退回链**：`reject_finish` 后任务回 `IN_PROGRESS`、`rejected_round=1`，第二轮到
  `round=2` 且 `completion_id` 不同；`repair_completions` 两轮都可回读。
- **原生解析/运行**：`exit 0 / 0 errors / view=true / admitted`；点击新建草稿后宿主
  隔离存储三份文件均写入。**未完成**：按角色隐藏动作按钮（平台缺口）、关闭重开后同
  task_id/轮次回读的自测脚本（`native_verify.py` 已就绪，被 §1.1 的平台问题挡住后半段）。

---

## 5. 全部 T/U/G0 的真实状态

### 5.1 T01–T38（业务用例）

- **已关闭并有运行证据**：T02 T03 T04 T05 T06 T07 T08 T09 T10 T11 T12 T13(部分)
  T15 T16 T18 T19 T20 T21 T22 T30 T31。
- **部分 / 仅一端**：T17（后端 SSE 已实现，原生未接）、T23（后端 jobs 已实现，原生未接）、
  T28（原生点击 + 落盘已验证；重开回读与角色投影受阻）。
- **未接通 / 保持未验证**：T01 T25 T26 T33–T38（真实模型与 octos 助手，未授权未配置）、
  T14（Asia/Shanghai 换算与"明天下午"核对：服务端窗口规则已实现，时区展示未做专项用例）、
  T24（旧入口统一边界）、T27（外部工单默认未配置，本地可独立完工验收已验证）、
  T29 T32（grant / pairing，依赖宿主）。

### 5.2 U01–U12（原生 UI 专项）

**全部未执行**。需要真人视觉/键盘/窄窗/文字放大验收。本轮只提供可运行的脚本应用与截图管线，
未做人工验收；不由执行模型冒充人。

### 5.3 G0–G5（门槛）

| 门槛 | 状态 |
|---|---|
| G0.1 工具与入口 | 通过（固定版本 card-host 构建、admitted、脚本求值 view=true） |
| G0.2 存储与命令 | 通过（点击→落盘→回读）；崩溃一致性未证明 |
| G0.3 身份与协作 | **未通过**。三个独立会话在 Web/API 侧有真实隔离（不同 actor + 服务端授权矩阵 + 独立 DB 连接抢单只一人成功）；原生宿主身份/grant 未接通，界面切身份仅开发调试 |
| G0.4 Agent | **未接通**（未授权 provider） |
| G0.5 证据与跟进 | 部分（证据索引 + 完工守卫已验证；真实拍照/后台唤醒未验证） |
| G0.6 路线冻结 | 通过（`app/docs/route-decision.md`：路线 A，不塞 Python 服务、不自行转公网） |
| G1–G4 | 见 §2 覆盖表 |
| G5 提交材料 | **未授权外部递交**（P06/P07/P08 保持 BLOCKED） |

本地就绪门 `scripts/check_build_loop.py --ready` 仍未 READY：U01–U12、真实模型、
原生角色投影、外部递交均未执行——**不因此把失败归因于外部项**。

---

## 6. 未完成项、明确阻断与恢复步骤

### 6.1 阻断：固定版本 card-host 的 OctoScript 编译缺陷

实测（证据 `runtime/repair-round2-20261002/native-*/host.log` 与 `splash-check/*/host.log`）：

1. `set_visible(false)` 不触发重排；
2. `on_render` 不实例化子控件；
3. `const` 不产生可见绑定（须 `let`）；`ok` 是保留字；fn 内跨声明顺序调用会解析为 nil；
   对象字面量嵌套对象字面量使所在函数失效；
4. `? :` 不支持；`string` 无 `.hash()`/`.substr()`；`fn` 不能作对象 key。

**恢复步骤**：
1. 在 `runtime/native-build/OctoSense-App-Hub` 升到修复 1/2 的构建，重跑
   `backend/.venv/bin/python runtime/repair-round2-20261002/native_verify.py`；
2. 或在宿主侧修 `View::on_render` / `set_visible` 的重排路径；
3. 或改用 `PortalList` 一类原生列表控件承载动作行。

### 6.2 未完成项清单（按依赖）

| 项 | 依赖 | 现状 |
|---|---|---|
| 原生按角色隐藏动作按钮 | 平台缺口 1/2 | 分发层已守门；渲染层未做 |
| 原生关闭重开同 task_id/轮次回读 | 上述 + `native_verify.py` 后半段 | 脚本就绪待跑 |
| 原生 SSE / 站内通知 | 宿主能力 | 后端已实现 |
| T01/T25/T26/T33–T38 真实模型 | 用户授权 provider | NOT_RUN |
| T29/T32 grant / pairing | 宿主 session | NOT_RUN |
| U01–U12 真人 UI 验收 | 人 | 未执行 |
| T24 旧 runner / MCP 写路径统一边界 | 比赛模式定义 | 未做 |
| P06/P07/P08 外部递交 | 用户授权 | BLOCKED |

### 6.3 恢复入口（精确断点）

```sh
cd /Users/abeam/一些尝试/知了OctoSense
# A. 先确认后端仍然全绿（应 375 passed）
backend/.venv/bin/python -m pytest backend/tests/ -q
# B. 探针（应 11 pass / 0 fail）
backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py
# C. E2E（应 E2E PASS）
backend/.venv/bin/python backend/scripts/e2e_full_chain.py
# D. 原生：换/修宿主构建后重跑（当前卡在 §6.1）
backend/.venv/bin/python runtime/repair-round2-20261002/native_verify.py
# E. 记台账（只检查记录结构，不执行应用测试）
python3 scripts/check_build_loop.py
python3 scripts/verify_migration.py
python3 docs/implementation/verify_pack.py
```

---

## 7. 原样可运行的启动与验收命令

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# ── 后端单测 + 继承基线
backend/.venv/bin/python -m pytest backend/tests/ -q

# ── 零参启动（默认 <工程根>/runtime/octosense.db、<工程根>/runtime/evidence）
backend/.venv/bin/python -c "
import uvicorn
from octosense_backend.api import make_app
make_app()   # 零参；OCTOSENSE_DB / OCTOSENSE_EVIDENCE_ROOT 可覆盖
uvicorn.run(make_app(), host='127.0.0.1', port=8713, log_level='warning')
"

# ── 显式配置启动（任意 cwd 均可）
OCTOSENSE_DB=/tmp/o.db OCTOSENSE_EVIDENCE_ROOT=/tmp/o-ev \
backend/.venv/bin/python -c "
import uvicorn
from octosense_backend.api import make_app
uvicorn.run(make_app(), host='127.0.0.1', port=8713, log_level='warning')
"

# ── 独立验收探针（V02–V11；任一断言失败 exit 1）
backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py \
    --json runtime/repair-round2-20261002/probe_round2.json

# ── 端到端（自带空闲端口/临时库/明确时钟；也可接外部实例）
backend/.venv/bin/python backend/scripts/e2e_full_chain.py
OCTOSENSE_BASE_URL=http://127.0.0.1:8713 backend/.venv/bin/python backend/scripts/e2e_full_chain.py

# ── 原生（副本 bundle + 独立 app-data，只读 app/bundle 原件）
backend/.venv/bin/python runtime/repair-round2-20261002/native_verify.py

# ── 记录检查器（只检查记录与文件结构，不执行应用测试）
python3 scripts/check_build_loop.py
python3 scripts/verify_migration.py
python3 docs/implementation/verify_pack.py
```

---

## 8. 当前源码哈希、包摘要、运行进程与端口

- 源码哈希清单：`runtime/repair-round2-20261002/source-sha256-round2.json`（本轮结束时重新生成）。
- Hub 包摘要：`app/bundle/manifest.json` 的 `integrity.bundle_blake3` 由 `--stamp` 生成；
  实测值见 `runtime/repair-round2-20261002/native-check/*/host.log` 的
  `card-host: stamped … with digest <…>` 行（每次 `--stamp` 会变；原包 digest
  `c066a517…` 与实际不符，是 V01 的 REFUSED 根因）。
- **运行进程与端口**：本轮所有进程（uvicorn / card-host）均在各自脚本结束时自行关闭；
  收尾时本机**无** OctoSense 相关常驻进程占用 8713/8722/8791–8842。
  app/bundle 原件未被 `--stamp` 改写（只在副本上打戳）。

---

## 9. 本轮改动文件清单

### 后端（新增）
- `backend/src/octosense_backend/paths.py` — 工程根/运行目录解析（V10）
- `backend/src/octosense_backend/authorization.py` — 统一对象可见性、角色收敛、技能/服务关系（V02/V03/V04/V09）
- `backend/src/octosense_backend/idempotency.py` — 统一指纹/回放/回执/失败审计/严格整数（V05/V10）
- `backend/src/octosense_backend/jobs.py` — 持久化提醒作业（只提醒、不自动验收）

### 后端（重写）
- `commands/__init__.py`、`appointments.py`、`extended.py`、`api/__init__.py`、`db/__init__.py`、
  `errors.py`、`seed.py`

### 测试（新增/重写）
- `backend/tests/octosense_backend/world.py`（铺垫必须断言成功并回读）
- `backend/tests/octosense_backend/{test_commands,test_appointments,test_appointments_reassign,test_extended,test_http_api}.py`
- `backend/tests/conftest.py`、`backend/tests/_baseline_helpers.py`（修复 `from conftest import stream_of` 名称碰撞）
- `backend/pyproject.toml`（`pythonpath = ["tests"]`）

### 脚本 / 原生 / 文档
- `backend/scripts/e2e_full_chain.py`（重写；Shell 版已停用并说明原因）
- `app/bundle/main.splash`（重写）
- `app/docs/route-decision.md`（新增）
- `runtime/repair-round2-20261002/**`（本轮全部证据）

---

## 10. 本地就绪门实测输出

```
$ python3 scripts/check_build_loop.py
VALID RECORD STRUCTURE: 64 checks; {'PASS': 31, 'NOT_RUN': 28, 'FAIL': 2, 'BLOCKED': 3}
Records only. No application, model, UI or publishing tests were executed.

$ python3 scripts/check_build_loop.py --ready
NOT READY: candidate='octosense-backend@0.4.0 · 15 表/27 命令 · 统一命令边界 authorization+idempotency+jobs'
  unpassed: G0-B G0-D G0-E G0-F | T01 T23 T24 T25 T26 T28 T29 T32 T33 T34 T35 T36 T37 T38 | U01–U12
  other_revision: G0-A G0-C | T04 T06 T07 T09 T10 T11 T12 T14 T15 T19 T20 T21 T22 T27 T30 T31 | P01–P05
  FAIL: T28（旧 PASS 已撤销）、T29
```
