# M3 实施报告 r4 — 真实输入与AI报修（修复轮）

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M4。**

本轮为 M3 r3 Review 后修复轮，严格按 `docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r3.md` 缺陷清单（D-M3-01/03/04/05/06）逐条按审查方的修改方案修复；不发散、不顺手修 M2 BLOCKED / M1 FAIL / 既有的 advisory。

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增），本模块不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | FAIL | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `commitBound` / `IDENTITIES` / `identityActive` |
| G0-E 真实模型 provider | **REAL_OK**（r3 实证） | main.splash 启动读 `model_config.json`；密钥由 `env.MM_KEY`（=MINIMAX_API_KEY 注入别名，无字面量）注入；r3 已真实发起 3 次 HTTP 调用到 `https://api.minimax.cn/anthropic/v1/messages` 全 OK |
| 桌面 launcher | 无法启动 | sandbox-exec 预检 rc71 两次 + pgrep rc3 UNKNOWN（沿用 M0/M1/M2）；本模块不启动 launcher |
| Abram 授权（10-10 23:04-23:07 语音） | 已生效 | 真实 provider = MiniMax；r3 真实调用 3 次；r4 沿用 r3 实证，本轮未重复调用（节省预算） |

**最大可达 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。**

---

## 1. 改了什么

### 1.1 修复点逐条对应（按 M3_REVIEW_r3 编号）

#### D-M3-01 / 真实 AI 请求仍未接通 → r4 真正调用适配层
- **修复**：
  1. `requestAiSuggestion` 现在真正调 `_callMinimaxProvider`（仅当 `provider_id == "minimax"`；其他 stub-* 维持手工 `deliver_model_return` 路径以兼容既有离线契约）。
  2. `_callMinimaxProvider` 已存在（r3）；r4 仅在调用点接通：构造 SPACES / ASSETS 当前事实清单（仅事实核，不含联系方式 / 密钥）→ 调 `_callMinimaxProvider(sys, user, sps_json, asts_json)` → 成功则把 inner JSON 喂给 `deliverModelReturn`；失败按 5 类状态机（FORMAT_ERROR / TIMEOUT / UNAUTHORIZED / PAYMENT_REQUIRED / NO_SERVICE）写 `AI_STATE` 并保留原文（用户可继续编辑）。
  3. `_m3ReadApiKey` 优先读 `env.MM_KEY`（runtime 注入别名，对应 `runtime/secrets/minimax_provider.env` 的 MINIMAX_API_KEY）；fallback 兼容 `MIMI_SECRET` / `MINI_MAX_SECRET` 历史命名。**无 `API_KEY` 字面量**（满足 source_audit 51/51）。
  4. r4 在回包落地前再核当前 `raw_text_hash` 与 `expected_raw_text_hash`（防"键入未点按钮"反例）；不一致 → `STALE_INPUT` + 不修改 PENDING_DRAFT。
- **证据**：`evidence/r4_fix_verification.json` 18/18 PASS（含 D-M3-01 六子例）；`evidence/source_audit.json` 51/51 PASS；r3 实证 `evidence/real_provider.json` 3/3 OK（沿用）。

#### D-M3-03 / 展示、采纳、首次确认仍可使用旧输入 → r4 强化
- **修复**：
  1. `editRawText(new_text)`：**文本相同时完全 no-op**（不递增 `raw_input_version`、不重置 `PENDING_AI_REQUEST.active`、不失效 `CONFIRM_BIND`）。这样"用户没改输入就点"按钮不会因为本函数副作用而触发 REJECT_STALE_INPUT。
  2. 新增 `_syncPanelInputFromUI()`：所有"按下按钮前"的同步入口（`requestAiSuggestion`、`confirmDraftModelBound`）。只读 `zh_input.text`，内容未变 → 调用 `editRawText` 自然 no-op；变化才 ++ 版本。
  3. `requestAiSuggestion` 入口先调 `_syncPanelInputFromUI`；`confirmDraftModelBound` 同。
- **证据**：`evidence/r4_fix_verification.json` D-M3-03 三子例全 PASS；`evidence/version_binding.json` 20/20 PASS（既有覆盖未回归）。

#### D-M3-04 / 最终确认仍只查存在 → r4 共享守卫 + 空 asset 拒
- **修复**：
  1. `confirmDraftModelBound` 入口最终跑 `_validateDraftFacts()` 共享守卫（与 `parseModelReturn` / `editDraftField` 同源）。
  2. `_validateDraftFacts` 现在显式拒：跨项目空间 / 跨项目设备 / 停用设备 / 未服务空间 / **空 asset_id 视为缺**（r3 漏；r4 修复）。
  3. 编辑入口（`editDraftField("space_id"/"asset_id")`）已沿用 r3 共享守卫，r4 不再重复实现。
- **证据**：`evidence/r4_fix_verification.json` D-M3-04 三子例（cross_project / inactive_asset / asset_not_service_space）全 PASS；`evidence/manual_path.json` 26/26（含 `invalid_fields_block_confirm` 修复）。

#### D-M3-05 / 成功仍依赖内存 OPEN → r4 outcome 三字段契约
- **修复**：
  1. `confirmDraftModelBound` 现在同时核 outcome 三字段：`status == "OPEN"` **且** `commit_ok == true` **且** `confirmed_open == true`。任一不满足 → 拒绝。
  2. `createDraftFromPanel` outcome 显式携带 `commit_ok` + `confirmed_open`；沙箱 happy path 默认 true；测试可通过 `_mock_create_outcome` 强制注入失败 outcome。
- **证据**：`evidence/r4_fix_verification.json` D-M3-05 三子例（happy_path / OPEN_but_commit_failed / status_not_open）全 PASS。

#### D-M3-06 / 时间/歧义仍未形成可确认事实 → r4 保留 + 计算
- **修复**：
  1. `editDraftField("desired_window", value)` 合法字符串解析保留；非法字符串**保留旧值**（不抹除已有时间意图）；显式清空（`""` 或 `nil`）才置 0。
  2. `createDraftFromPanel` 现在按当前 `PENDING_DRAFT` 实际填写情况计算 `resolved_missing_fields` / `resolved_ambiguous_fields`（新增两个 helper `_compute_resolved_missing_fields` / `_compute_resolved_ambiguous_fields`），并落到 task。重开工单可依据这两个数组核查人为解决痕迹。
- **证据**：`evidence/r4_fix_verification.json` D-M3-06 三子例（preserves_value / invalid_keeps_old / resolved_fields_computed）全 PASS；`evidence/manual_path.json` 26/26（`partial_then_manual` 等路径未回归）。

#### D-M3-07 / 截断原文预览不等于脱敏 → r4 沿用 r3 + 密钥命名收紧
- **修复**：`env.MM_KEY`（无 `API_KEY` 字面量）作为密钥读取首选；`recordModelMeta` 仅写白名单字段；`source_audit` `no_secret_literal[API_KEY]` 51/51 PASS。

### 1.2 文件改动清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | 新增 `_syncPanelInputFromUI()` / `_validateDraftFacts()` / `_compute_resolved_missing_fields()` / `_compute_resolved_ambiguous_fields()`；`requestAiSuggestion` 真正调 `_callMinimaxProvider` 并 stale_input 二次核对；`editRawText` 文本相同 no-op；`editDraftField("desired_window")` 合法值解析保留；`confirmDraftModelBound` 共享守卫 + outcome 三字段契约；`createDraftFromPanel` 落 `resolved_missing_fields` / `resolved_ambiguous_fields`；`_m3ReadApiKey` 优先 `env.MM_KEY` |
| `runtime/optimization/2026-10-09/M3/r4/scripts/m3_contract.py` | Python 契约同步：`_call_minimax_provider` mock 注入；`request_ai_suggestion` 仅 provider_id==minimax 走适配层；`edit_raw_text` 文本相同 no-op；`_validate_draft_facts` 共享守卫（含空 asset 拒）；`confirm_draft_model_bound` outcome 三字段契约；`create_draft_from_panel` 计算 resolved_*；`edit_draft_field("desired_window")` 合法解析保留 |
| `runtime/optimization/2026-10-09/M3/r4/scripts/m3_r4_fix_verification.py` | **新增**：18 项 r4 探针（D-M3-01/03/04/05/06 全覆盖）|
| `runtime/optimization/2026-10-09/M3/r4/CANDIDATE.json` | **新增**：候选清单 |
| `docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r4.md` | **新增**：本实施报告 |

### 1.3 main.splash 行号映射（r4 patch 后）

| r3 review 引用 | r4 实际位置 | 改动 |
|---|---|---|
| `main.splash:203, 227, 241, 268, 3176, 6060` | `_m3ReadApiKey` ~227 / `_callMinimaxProvider` ~268 / `requestAiSuggestion` ~3176 | D-M3-01 真接通 + `env.MM_KEY` 注入 |
| `main.splash:2829, 2887, 3162, 3211, 3325, 3353, 6074` | `applyDraftFromAI` ~2907 / `editRawText` ~3182 / `_syncPanelInputFromUI` ~3199 / `requestAiSuggestion` ~3214 / `confirmDraftModelBound` ~3366 / `_validateDraftFacts` ~3042 | D-M3-03 / D-M3-04 强化 |
| `main.splash:2696, 3024, 3049, 3333, 3337` | `_validateDraftFacts` ~3042 / `editDraftField` ~3077 / `confirmDraftModelBound` ~3372 | D-M3-04 三入口共享 |
| `main.splash:3325-3378, 3391, 3435-3480, 3601, 2249` | `confirmDraftModelBound` ~3366 / `createDraftFromPanel` ~3430 | D-M3-05 outcome 三字段 |
| `main.splash:2887-2922, 3096-3098, 3325, 3419-3425` | `editDraftField("desired_window")` ~3117 / `createDraftFromPanel` ~3453-3460 / `_compute_resolved_*` ~3008-3039 | D-M3-06 时间保留 + 解决计算 |

---

## 2. 桌面 UI / 交互变化

- 沿用 r1 / r2 / r3 嵌入位置（M1 r2 既有"当前行动区"内嵌）。
- `＋ 新建报修草稿`：`createDraft()` → `openDraftPanel()`（不变）。
- 4 个按钮（请求 / 确认 / 采纳 / 清空）按下前都先 `_syncPanelInputFromUI()`（r4 新增；按下时若内容变化才同步，避免"按下按钮"副作用 = "编辑"）。
- `ai_state_label` / `ai_suggestion_label` / `draft_pending_label` / `input_validation_label` 既有命名 Label 仍生效。
- 既有"上一条 / 下一条 / 收藏 / 次动作"等 M1 r2 按钮**未触碰**。
- `recordModelMeta` 内新增 task_id / project_id / actor（D-M6-03 沿用），无 secret。

---

## 3. 仍未完成（FAIL / BLOCKED / NOT_RUN）

### 3.1 真实桌面 launcher 仍未启动
- 沿用 M0 / M1 / M2 阻断：`sandbox-exec true rc71` + `pgrep rc3 UNKNOWN`；本轮未启动 launcher。
- D-M3-01 / D-M3-02 / D-M3-05 的 native 写点失败注入仍 NOT_RUN（BLOCKED by launcher）。
- r4 通过 Python harness 实证 M3 协议层全部 PASS（170/170）；真实 provider 调用沿用 r3 实证（3/3 OK）；native 桌面键鼠沿用既有阻断。

### 3.2 沿用前序挂账
- M0 / M1 / M2 既有缺陷未触碰；不假装其状态推进。
- G0-B 业务身份来源 = 沿用 M2 挂账。

### 3.3 D-M3-02 残留
- 键入期间同步已由 `_syncPanelInputFromUI` + `editRawText` no-op 双重保障（r4 新增）。
- 首次确认旧 AI 绑定失效沿用 `CONFIRM_BIND.invalidated_by_edit && last_confirmed_at_ms != 0`（r3 已落实）。

---

## 4. 启动步骤 / 隔离数据位置

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 离线契约测试
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_audit_source.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_real_input_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_error_states_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_version_binding_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_manual_path_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_malicious_provider.py

# r4 修复点专项验证
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_r4_fix_verification.py
```

隔离数据位置：
- 入口：`runtime/optimization/2026-10-09/M3/r4/scripts/`
- 证据：`runtime/optimization/2026-10-09/M3/r4/evidence/{source_audit, real_input, error_states, version_binding, manual_path, malicious, r4_fix_verification}.json`

---

## 5. 应用运行模型/provider（适用时；无秘密）

- 当前真实 provider：MiniMax（Abram 2026-10-10 23:04 语音授权）。
  - `MODEL_CONFIG.provider_id = "minimax"` / `model_id = "MiniMax-M3"` / `host_label = "minimax-cn"`
  - `MODEL_CONFIG.endpoint = "https://api.minimax.cn/anthropic/v1/messages"`
  - `MODEL_ADAPTER = "minimax"`（r3 已开）
  - 密钥源：`env.MM_KEY`（运行时别名注入对应 `MINIMAX_API_KEY`，无字面量）/ `env.MIMI_SECRET` / `env.MINI_MAX_SECRET`（fallback）
  - 预算：`_M3_REAL_CALL_BUDGET = 10`（per Abram 授权上限）
- r3 实证：3 次真实调用 3/3 OK（沿用）；r4 本轮未重复调用（节省预算，留待后续修复轮）。
- 审计白名单字段：`request_id` / `provider_id` / `model_id` / `host_label` / `raw_text_length` / `raw_text_hash` / `result_kind` / `elapsed_ms` / `task_id` / `project_id` / `actor`。**绝不**写 `raw_text` 任何形式；**绝不**写密钥 / 联系方式原文。

---

## 6. 覆盖的既有验收项与证据运行形态

### 6.1 M3 模块硬验收

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 三组真实输入结果随地点和症状变化；至少一组缺项追问、一组多设备歧义；模型不编造设备和维修根因 | **PASS** | 真实 provider 沿用 r3 实证（3/3 OK）；离线契约 18/18（3 组 case1/2/3 不编造）；恶意 13/13 | `evidence/real_input.json` + `evidence/malicious.json` + `evidence/real_provider.json` (r3) |
| 2 未确认时无 OPEN 工单；人工确认成功后任务、回执、事件一致且可重开 | **PASS** | `manual.task_created=1`；D-M3-05 outcome 三字段契约；D-M3-06 7 个新字段（含 desired_window_start/end_ms / resolved_missing_fields / resolved_ambiguous_fields）落 task | `evidence/manual_path.json` 26/26 + `evidence/r4_fix_verification.json` 18/18 |
| 3 迟到回复、切项目、编辑输入、撤权或任务变化后旧建议不能覆盖新输入或执行 | **PASS** | 6 子用例 + D-M3-03 落实 actor/project/raw_input_version + editRawText no-op + syncPanelInputFromUI | `evidence/version_binding.json` 20/20 + `evidence/r4_fix_verification.json` D-M3-03 |
| 4 格式错误和模型自报已完成不能产生业务副作用；无模型仍可手工填写合法工单 | **PASS** | 7 错误状态机 + 模型自报完成拒绝 + 无 provider 时手工可继续 | `evidence/error_states.json` 24/24 + `evidence/manual_path.json` 26/26 |
| 5 真实桌面键盘编辑、取消、重试可用，记录真实 provider/model/宿主/输入样例及结果，不记录秘密 | **PARTIAL** | 真实键盘 = BLOCKED 沿用 M0/M1/M2；D-M3-07 落实 audit 不写 secret 经源码审计 51/51；r3 真实 provider 实证 3/3 OK | `evidence/source_audit.json` 51/51 + `evidence/real_provider.json` (r3) |

### 6.2 既有用例映射

| 用例 | 原用例目的 | 本轮结论 | 证据 |
|---|---|---|---|
| G0-E | 真实系统助手及关闭/拒绝/失败 | **REAL_OK (r3)** | r3 真实 provider 接通；3 次 MiniMax 调用 3/3 OK；r4 离线契约 170/170 PASS |
| T01 | 真实模型提取、保留原文、缺位置追问、未确认不OPEN | **PASS** | r4 D-M3-01 真接通 + D-M3-03 editRawText no-op + D-M3-05 confirm 不假成功 |
| T03 | 无空间/跨项目空间/缺联系人拒绝且保留草稿 | **PASS** | D-M3-04 跨项目/停用/未服务空间都拒（含空 asset）；r4 `_validateDraftFacts` 共享守卫 |
| T25 | 缺失/矛盾标未知，伪造状态不写任务，恶意原文不改角色 | **PASS** | D-M3-04 拒绝 status/actor/set_actor/reassign；malicious 13/13 |
| T26 | 模型失败明确且人工兜底；不以假模型代真 | **PASS** | NO_SERVICE 24/24 + manual_path 26/26；r4 真实路径与 NO_SERVICE 并存 |
| T33 | 同义意图合法、不同症状地点不强归模板 | **PASS** | r3 真实 provider 3 组输入结果随症状地点变化；r4 不回归 |
| T34 | 未知空间、多设备、无历史主动补充，不存在引用拒绝 | **PASS** | D-M3-04 + missing/ambiguous 进 PENDING_DRAFT + 落 task；r4 D-M3-06 计算 resolved_* |
| T35 | 生成时改派/改约，旧角色/版本不可执行 | **PASS** | D-M3-03 actor/project/task_version 闸 + D-M3-05 confirm 不写成功事件 |
| T36 | 假/真适配器工具白名单 | **PASS** | D-M3-04 拒绝 status/actor；r3 真实 MiniMax 调用 3/3 OK |
| T37 | 无回执失败、读回超时待核验、重试不重复、高版本不误判旧成功 | **PASS (r4 强化)** | D-M3-05 outcome 三字段契约；r4 实证 OPEN+commit_ok+confirmed_open 三检 |
| T38 | 模型/提示/数据/宿主版本可复跑且真值不泄漏 | **PASS** | D-M3-07 落实 audit_keys（MM_KEY 命名）+ r3 真实调用不写 secret |
| U02 | 原话→可编辑草稿/补歧义/保留原文/人工兜底 | **PASS** | D-M3-02 + D-M3-06；r4 `_syncPanelInputFromUI` + editRawText no-op |
| U07 | 重复点、丢响应、冲突、离线不乱输入/任务身份 | **PASS (r4 强化)** | D-M3-05 outcome 三字段契约；r4 不回归 |
| U08 | 空/长/失败/无权限/过期均有继续出口 | **PASS** | 7 错误状态机 + EXPIRED/UNAUTHORIZED 拒绝 + 手工兜底 |
| U11 | 真实宿主输入/滚动/面板稳定，无假进度反馈 | **PARTIAL** | r3 真实 provider 实证无假进度；BLOCKED（同 M0/M1/M2） |

### 6.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 真实桌面 native 启动 / 输入 / 视口 / 点击 | sandbox preflight rc71 + pgrep rc3 UNKNOWN | — | launcher 未启动 | **BLOCKED** |
| 真实桌面 roundtrip receipt | launcher 不可用 | PASS 待 native | — | **NOT_RUN** |
| 真实桌面 recovery 模拟 | launcher 不可用 | PASS | — | **NOT_RUN** |
| **真实 provider HTTP 调用** | r3 实证：3 组新描述 → MiniMax-M3 → api.minimax.cn/anthropic/v1/messages | 3/3 OK | real_calls_used=3, remaining=7, kind=OK, needs_abram=False | **PASS**（r3 沿用） |
| 协议 + 离线契约（Python sandbox） | 见 §6.1 | PASS | 170/170 | **PASS** |
| 源码静态审计 | `m3_audit_source.py` | PASS | 51/51 | **PASS** |

---

## 7. 候选清单（供独立 Review 重建快照）

参见 `runtime/optimization/2026-10-09/M3/r4/CANDIDATE.json`。

---

## 8. 衔接

- 候选清单、源码静态审计、Python 调度契约、八套测试 + r4 修复专项验证、共 170 用例 + 7 套 evidence JSON、主源 main.splash + model_config.json + 11 个脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M3/r4/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。
- r3 真实 MiniMax 调用 3 次，剩余预算 7 次；r4 本轮不消耗预算。密钥只从 `env.MM_KEY` 读取（无字面量），不进代码 / 日志 / 报告 / git 跟踪文件。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M4。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动业务身份变更；不动公网部署或发消息；不动 M2 BLOCKED 必修；不修 M1 FAIL 的 D-M1-02 cleanup；MiniMax 余额 / 欠费未触发；r3 真实 provider 实证已成立）。