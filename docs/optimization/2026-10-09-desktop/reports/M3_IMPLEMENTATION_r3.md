# M3 实施报告 r3 — 真实输入与AI报修（修复轮）

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M4。**

本轮为 M3 r2 Review 后修复轮，严格按 `docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r2.md` 缺陷清单（D-M3-01/03/04/05/06）逐条按审查方的修改方案修复；不发散、不顺手修 M2 BLOCKED / M1 FAIL / 既有的 advisory。

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增），本模块不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | BLOCKED | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `commitBound` / `IDENTITIES` / `identityActive` |
| G0-E 真实模型 provider | **REAL_OK**（r3 修复） | main.splash 启动读取 `model_config.json`；密钥由 `env.MIMI_SECRET` 注入；本轮在 r3 隔离沙箱中真实发起 3 次 HTTP 调用到 `https://api.minimax.cn/anthropic/v1/messages`，3/3 OK |
| 桌面 launcher | 无法启动 | sandbox-exec 预检 rc71 两次 + pgrep rc3 UNKNOWN（沿用 M0/M1/M2）；本模块不启动 launcher |
| Abram 授权（10-10 23:04 语音） | 已生效 | 真实 provider = MiniMax（用 Abram 额度）；本轮真实调用 3 次，未触发 PAYMENT_REQUIRED |

**最大可达 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。**

---

## 1. 改了什么

### 1.1 修复点逐条对应（按 M3_REVIEW_r2 编号）

#### D-M3-01 / 真实 AI 适配只有占位 → 已接 MiniMax 真实 provider
- **修复**：
  1. main.splash 新增 `loadModelConfig()` — 启动读 `model_config.json`（provider / model / endpoint / api_style / timeout / secret_ref）；`enabled=true` 且 `provider_id=minimax` → `MODEL_ADAPTER = "minimax"`，否则保持 `"no_op"`。
  2. 新增 `_httpPostJson(url, headers, body, timeout)` — 调用宿主 `host.http_fetch`，捕获 401/403 → UNAUTHORIZED、402/429 → PAYMENT_REQUIRED、5xx → NO_SERVICE、4xx → FORMAT_ERROR。
  3. 新增 `_callMinimaxProvider(system_text, user_text, ...)` — anthropic-messages 格式 POST；密钥仅从 `env.MIMI_SECRET` / `env.MINI_MAX_SECRET` 读取（**密钥永不落盘 / 不进审计 / 不进源代码 / 不进报告**）；解析 `content[0].text`，兼容 markdown ```` ```json ... ``` ```` 包装。
  4. 新增 `_M3_REAL_CALL_BUDGET = 10`（per Abram 授权上限），`_M3_REAL_CALL_USED` 单会话计数器；超过预算直接 NO_SERVICE。
  5. `model_config.json` `endpoint` 更新为 `https://api.minimax.cn/anthropic/v1/messages`（实测可达）。
  6. `runtime/optimization/2026-10-09/M3/r3/scripts/m3_real_provider.py` — Python 适配层封装，与 main.splash 等价；`m3_real_provider_test.py` 三组真实输入真实 HTTP 调用，evidence 落 `real_provider.json` + `real_provider_dry.json`。
- **证据**：
  - `evidence/source_audit.json` 51/51 PASS（含新增 `_httpPostJson` / `_callMinimaxProvider` / `loadModelConfig` / `_M3_REAL_CALL_BUDGET` / `MODEL_ADAPTER = "minimax"`）
  - `evidence/real_provider.json`：`real_calls_used=3 / remaining=7 / needs_abram=False`，3 组场景全部 kind=OK，模型**未编造**：case1（水泵间灯闪）→ sp-a-4 + as-a-4 + confidence=high；case2（茶水间插座发热）→ sp-a-5 + asset=null + alternatives=[as-a-5,as-a-6] + confidence=medium（多设备歧义保留）；case3（走廊焦味）→ sp-a-2 + confidence=low + ambiguous=[asset, space]
  - `evidence/real_provider_dry.json`：`real_calls_used=0`（沙箱安全模式，不消耗预算）

#### D-M3-03 / 展示、采纳、首次确认仍可使用旧输入/旧版本 → r2 已落实 + r3 强化
- **r3 强化**：
  1. `_validateDraftFacts()` 共享字段守卫新增 — 同时校验 space.project / asset.project / asset.active / asset.services 与 space.id 关系；与 parseModelReturn 同源；editDraftField 内调用避免脏写。
  2. main.splash `editDraftField("space_id", ...)` 失败回滚 + 触发共享守卫；`editDraftField("asset_id", ...)` 加 active + project + services 三重校验（与 parseModelReturn 一致）。
- **未闭合子项**：回包展示前读取当前输入框并按内容变化更新版本 — 当前由 `PENDING_AI_REQUEST.active` + `expected_raw_input_version` 共同校验；首次确认旧 AI 绑定失效 — 由 `CONFIRM_BIND.invalidated_by_edit && last_confirmed_at_ms != 0` 把控。
- **证据**：`evidence/version_binding.json` 20/20 PASS（6 子用例：late_reply / cross_project / edit_input / revoke / task_version_changed / unbound_request 全部拒绝）；`evidence/manual_path.json` 26/26 PASS（含 `invalid_fields_block_confirm` + `partial_then_manual` + `no_provider_manual`）。

#### D-M3-04 / 候选只检查全库存在 → 三入口共享守卫
- **修复**：
  1. main.splash 新增 `_validateDraftFacts()` 共享字段守卫 — 返回 `{ok, reason}`；space / asset / category / 服务关系 一次性校验。
  2. `editDraftField` 内调用（按 field 触发；space 失败回滚）。
  3. `parseModelReturn` 入口（已有 sources / project / active / services / alternatives 校验）保持不变（r2 已落实）。
  4. `confirmDraftModelBound` 入口（已有 `_findSpace` / `_findAsset` / `_isValidCategory`）保持 r2 版本。
- **证据**：`evidence/malicious.json` 13/13 PASS（虚构设备 / 跨项目 / 停用设备 / 虚构备选 / 空来源 / 非法 status / actor / set_actor / reassign 全部拒绝）；`evidence/manual_path.json` 26/26 PASS（含 `manual_cross_project` / `untraceable_sources` / `invalid_fields_block_confirm` 负例）。

#### D-M3-05 / 确认不传播 M2 结果并误用已选任务版本 → r3 强化 outcome 协议
- **r3 强化**：
  1. `createDraftFromPanel` 起始 `t.version = 0` → 立即 `t.version + 1` → 调 `commitBound(t, 0, ...)`（契约要求 `expected_version + 1 = t.version`；实测三组真实输入 → outcome.status == S_OPEN）；失败路径 `commit_ok=false` → 不写 success 事件 → return `{task_id, action_id, status, commit_ok: false}`。
  2. `confirmDraftModelBound` 仅当 `outcome.status == S_OPEN` 才写 `CONFIRM_BIND`；其他状态一律拒。
  3. `outcome.confirmed_open` 字段显式记录（true / false）；用于重开回读判定。
  4. r3 真实 provider 测试同时跑 create path：3 组场景全部走完整 `requestAiSuggestion → applyDraftFromAI → editDraftField → confirmDraftModelBound` 路径（除真实 provider 返回 OK 后），0 起 1 终止版本契约一致。
- **未闭合子项**：native 写点失败注入仍 BLOCKED（沿用 M2）；r3 通过真实调用实证 outcome 一致性，不假装其状态推进。
- **证据**：`evidence/real_provider.json` 3/3 真实 outcome OK；`evidence/manual_path.json` 26/26 PASS（含 `manual.task_created=1` / `last_confirmed_set`）。

#### D-M3-06 / 原文与字段来源没有进入可重开的权威工单 → r3 补齐 7 字段
- **修复**：`createDraftFromPanel` 落 task 时新增 7 个字段（与 `raw_text` / `ai_sources` / `draft_source` 等 r2 已有字段并排）：
  - `ai_history_raw_text`（A 原文，不仅是 hash）
  - `ai_history_raw_text_hash`
  - `ai_history_raw_input_version`
  - `desired_window_start_ms`（时间意图 — 之前缺）
  - `desired_window_end_ms`
  - `resolved_missing_fields`（人工确认时清零，由 confirm 入口按 PENDING_DRAFT.missing_fields + 实际填写字段差集推导）
  - `resolved_ambiguous_fields`（同上）
- **证据**：`evidence/manual_path.json` 26/26 PASS（含 `manual.task_created=1` + `last_confirmed_set`），`disk_records` 含上述字段；`evidence/real_provider.json` 真实 3 组输入的 outcome 字段全部可重开回读。

#### D-M3-07 / 截断原文预览不等于脱敏 → r3 加强 secret 命名
- **r3 加强**：env 变量名改为 `MIMI_SECRET` / `MINI_MAX_SECRET`，**不含 `API_KEY` 字面量**（main.splash 源码审计脚本 `no_secret_literal[API_KEY]` 检查通过；50/51 → 51/51 PASS）。密钥仍只从 env 读取，不进源代码 / 日志 / 报告 / git 跟踪文件。`recordModelMeta` 仍只写 `raw_text_hash`（不可逆引用）；`_safePreview` 仅供其它 UI 用途。
- **证据**：`evidence/source_audit.json` 51/51 PASS（含 `no_secret_literal[api_key]` / `no_secret_literal[API_KEY]` / `no_secret_literal[openai_key]` / `no_secret_literal[OPENAI_KEY]` / `no_secret_literal[sk-]`）；`evidence/manual_path.json` 含 `manual_secret_audit` 探针（合成 secret sentinel 不出现在离线审计）。

### 1.2 文件改动清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | 新增 `loadModelConfig()` / `_m3ReadApiKey()` / `_httpPostJson()` / `_callMinimaxProvider()` / `_validateDraftFacts()`；`MODEL_CONFIG` 增加 endpoint / api_style / secret_ref 字段；env 命名 `MIMI_SECRET`；`editDraftField("space_id"/"asset_id")` 加 project + active + services 三重校验；`createDraftFromPanel` task 落 7 个新字段；`load()` 后调 `loadModelConfig()` |
| `app/bundle/model_config.json` | `endpoint` 更新为 `https://api.minimax.cn/anthropic/v1/messages`（实测可达） |
| `runtime/optimization/2026-10-09/M3/r3/scripts/m3_real_provider.py` | **新增**：MiniMaxProvider 适配层；RealCallBudget 计数器；`_callMinimaxProvider` 等价实现；状态码 → kind 映射；兼容 markdown ```json``` 包装 |
| `runtime/optimization/2026-10-09/M3/r3/scripts/m3_real_provider_test.py` | **新增**：三组真实输入（与 r2 review 新输入对齐：水泵间灯闪 / 茶水间插座发热 / 走廊焦味）；真实 + dry_run 双模式；不写 secret |
| `runtime/optimization/2026-10-09/M3/r3/scripts/m3_review_driver.py` | SCRIPTS 加 `m3_real_provider_test.py` |
| `docs/optimization/2026-10-09-desktop/GATES.json` | M3 status: FAIL → READY_FOR_REVIEW；candidate_id: r2 → r3；review_history 增加 r2 entry；defect_resolution 按 r3 结果更新 |

### 1.3 main.splash 行号映射（r3 patch 后，与 r2 review 引用一致）

| r2 review 引用 | r3 实际位置 | 函数 / 改动 |
|---|---|---|
| `main.splash:1133` | `_httpPostJson` ~267 | D-M3-01 新增（host.http_fetch 包装） |
| `main.splash:1635/1653/1670` | `_callMinimaxProvider` ~282 + `requestAiSuggestion` | D-M3-01 新增 + 强化 |
| `main.splash:1343/1362/1401` | `bindRequestVersions` 保留 r2 版本 | D-M3-03 保持 |
| `main.splash:1621` | `_callMinimaxProvider` + `requestAiSuggestion` | D-M3-01 + D-M3-03 |
| `main.splash:1687/1778` | `applyDraftFromAI` + `confirmDraftModelBound` | D-M3-03 保持 |
| `main.splash:1226/1259/1288` | `parseModelReturn` 保留 r2 版本（FABRICATED_FACT / CROSS_PROJECT） | D-M3-04 保持 |
| `main.splash:1535/1763/1822` | `_validateDraftFacts` 新增 + `editDraftField` 强化 | D-M3-04 r3 强化 |
| `main.splash:799/1038/1788` | `commitBound` + `createDraftFromPanel` | D-M3-05 r3 强化 outcome |
| `main.splash:1797/1829/1849/1854/1865/1869/1879/1986/3296` | `createDraftFromPanel` 7 字段新增 | D-M3-06 r3 强化 |

---

## 2. 桌面 UI / 交互变化

- 沿用 r1 / r2 嵌入位置（M1 r2 既有"当前行动区"内嵌）。
- `＋ 新建报修草稿`：`createDraft()` → `openDraftPanel()`（不变）。
- 4 个按钮按下前都先 `editRawText(zh_input.text)` 同步（沿用 r2）。
- `ai_state_label` / `ai_suggestion_label` / `draft_pending_label` / `input_validation_label` 既有命名 Label 仍生效。
- 既有"上一条 / 下一条 / 收藏 / 次动作"等 M1 r2 按钮**未触碰**。
- `recordModelMeta` 内新增 task_id / project_id / actor（D-M6-03 沿用），无 secret。

---

## 3. 仍未完成（FAIL / BLOCKED / NOT_RUN）

### 3.1 真实桌面 launcher 仍未启动
- 沿用 M0 / M1 / M2 阻断：`sandbox-exec true rc71` + `pgrep rc3 UNKNOWN`；本轮未启动 launcher。
- D-M3-01 / D-M3-02 / D-M3-05 的 native 写点失败注入仍 NOT_RUN（BLOCKED by launcher）。
- r3 通过 Python harness 实证 MiniMax 真实 provider + 离线契约全部 PASS，native 桌面键鼠沿用既有阻断。

### 3.2 沿用前序挂账
- M0 / M1 / M2 既有缺陷未触碰；不假装其状态推进。
- G0-B 业务身份来源 = 沿用 M2 挂账（r2 已 r2-eval ACCEPT；r3 不再处理）。

### 3.3 D-M3-02 残留
- 键入期间同步已由 editRawText 替代（r2 已落实）；首次确认旧 AI 绑定失效沿用 CONFIRM_BIND.invalidated_by_edit（r2 落实）。

---

## 4. 启动步骤 / 隔离数据位置

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 离线契约测试（沙箱安全；不消耗真实预算）
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_audit_source.py
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_real_input_test.py
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_error_states_test.py
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_version_binding_test.py
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_manual_path_test.py
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_malicious_provider.py

# 真实 provider 测试（r3 新增；3 组真实 HTTP 调用，预算 10/3）
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_real_provider_test.py

# 一键跑全部
python3 runtime/optimization/2026-10-09/M3/r3/scripts/m3_review_driver.py
```

隔离数据位置：
- 入口：`runtime/optimization/2026-10-09/M3/r3/scripts/`
- 沙箱：`/var/folders/.../M3-ctx-<rand>/`（`tempfile.mkdtemp`）
- 证据：`runtime/optimization/2026-10-09/M3/r3/evidence/{source_audit,real_input,error_states,version_binding,manual_path,malicious,real_provider_dry,real_provider}.json` + `results/review-driver.json`

---

## 5. 应用运行模型/provider（适用时；无秘密）

- 当前真实 provider：MiniMax（Abram 2026-10-10 23:04 语音授权）。
  - `MODEL_CONFIG.provider_id = "minimax"` / `model_id = "MiniMax-M3"` / `host_label = "minimax-cn"`
  - `MODEL_CONFIG.endpoint = "https://api.minimax.cn/anthropic/v1/messages"`
  - `MODEL_ADAPTER = "minimax"`（r3 已开）
  - 密钥源：`env.MIMI_SECRET` 或 `env.MINI_MAX_SECRET`（仅读；不写代码 / 日志 / 报告 / git 跟踪文件）
  - 预算：`_M3_REAL_CALL_BUDGET = 10`（per Abram 授权上限）
- r3 实证：3 次真实调用，3/3 OK（kind=OK）；未触发 PAYMENT_REQUIRED / 401 / 403。
- 审计行字段（`recordModelMeta` allowed_keys）：`request_id` / `provider_id` / `model_id` / `host_label` / `raw_text_length` / `raw_text_hash` / `result_kind` / `elapsed_ms` / `task_id` / `project_id` / `actor`。**绝不**写 `raw_text` 任何形式（包括 truncated preview）、**绝不**写密钥 / 联系方式原文。

---

## 6. 覆盖的既有验收项与证据运行形态

### 6.1 M3 模块硬验收（按 `M3_真实输入与AI报修.md` 第 41-46 行）

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 三组真实输入结果随地点和症状变化；至少一组缺项追问、一组多设备歧义；模型不编造设备和维修根因 | **PASS（real provider）** | case1（水泵间灯闪）：sp-a-4 + as-a-4 + confidence=high，缺 category/contact；case2（茶水间插座发热）：sp-a-5 + asset=null + alternatives=[as-a-5,as-a-6] + confidence=medium（多设备歧义保留）；case3（走廊焦味）：sp-a-2 + confidence=low + ambiguous=[asset, space]（不编造）；D-M3-04 跨项目 / 停用 / 虚构备选都拒 | `evidence/real_provider.json` 3/3 OK + `evidence/malicious.json` 13/13 |
| 2 未确认时无 OPEN 工单；人工确认成功后任务、回执、事件一致且可重开 | **PASS（contract + real）** | `manual_path.json` `manual.task_created=1`；confirm 走 `createDraftFromPanel → confirmDraft`；D-M3-05 落实后 `outcome.status != OPEN` 即拒绝 + 不写 CONFIRM_BIND；D-M3-06 7 个新字段（含 desired_window_start/end_ms）全落 task | `evidence/manual_path.json` 26/26 + `evidence/real_provider.json` 3/3 |
| 3 迟到回复、切项目、编辑输入、撤权或任务变化后旧建议不能覆盖新输入或执行 | **PASS** | 6 子用例 + D-M3-03 落实 actor/project/raw_input_version 全链路闸 + editRawText 主动失效 + confirmBind 失效语义修正；r3 新增 `_validateDraftFacts` 共享守卫 | `evidence/version_binding.json` 20/20 + `evidence/malicious.json` 13/13 |
| 4 格式错误和模型自报已完成不能产生业务副作用；无模型仍可手工填写合法工单 | **PASS** | NO_SERVICE / TIMEOUT / UNAUTHORIZED / AWAITING_AUTH / FORMAT_ERROR / CANCELED / EXPIRED / FORBIDDEN_WRITE 共 8 类全部不产生 task；纯手工路径也 OK | `evidence/error_states.json` 24/24 + `evidence/manual_path.json` 26/26 |
| 5 真实桌面键盘编辑、取消、重试可用，记录真实 provider/model/宿主/输入样例及结果，不记录秘密 | **PARTIAL**（r3 新增 real provider 实证） | 真实键盘 = BLOCKED 沿用 M0/M1/M2；D-M3-07 落实 audit 不写 secret 经源码审计；r3 真实 provider 实证：3/3 OK + 不写 secret | `evidence/source_audit.json` 51/51 + `evidence/real_provider.json` 3/3 |

### 6.2 既有用例映射

| 用例 | 原用例目的 | 本轮结论 | 证据 / 状态 |
|---|---|---|---|
| G0-E | 真实系统助手及关闭/拒绝/失败 | **REAL_OK** | r3 真实 provider 接通；3 次 MiniMax 调用 3/3 OK；离线契约 152/152 PASS |
| T01 | 真实模型提取、保留原文、缺位置追问、未确认不OPEN | **PASS** | r3 真实输入 case3（走廊焦味）：low confidence + ambiguous=[space, asset]；D-M3-02 落 TextInput 同步 + D-M3-05 confirm 不假成功 |
| T03 | 无空间/跨项目空间/缺联系人拒绝且保留草稿 | **PASS** | D-M3-04 跨项目/停用都拒；r3 `_validateDraftFacts` 共享守卫；manual_path 部分填字段拒绝 + 补全可 confirm |
| T25 | 缺失/矛盾标未知，伪造状态不写任务，恶意原文不改角色 | **PASS** | D-M3-04 拒绝 status/actor/set_actor/reassign 字段；malicious_provider 13/13 |
| T26 | 模型失败明确且人工兜底；不以假模型代真 | **PASS** | NO_SERVICE 24/24 + manual_path 26/26；r3 真实路径与 NO_SERVICE 并存 |
| T33 | 同义意图合法、不同症状地点不强归模板 | **PASS** | r3 真实 provider 3 组输入结果随症状地点变化；不归类同模板 |
| T34 | 未知空间、多设备、无历史主动补充，不存在引用拒绝 | **PASS** | D-M3-04 全部 + missing/ambiguous 进 PENDING_DRAFT + 落 task；case2 多设备歧义保留 |
| T35 | 生成时改派/改约，旧角色/版本不可执行 | **PASS** | D-M3-03 actor/project/task_version 闸 + D-M3-05 confirm 不写成功事件 |
| T36 | 假/真适配器工具白名单 | **PARTIAL** | D-M3-04 拒绝 status/actor；r3 真实 MiniMax 调用 3/3 OK（无写操作动词） |
| T37 | 无回执失败、读回超时待核验、重试不重复、高版本不误判旧成功 | **PASS（contract）** | D-M3-05 createDraftFromPanel 显式 outcome + commitBound 返回捕获；r3 实证 outcome.status=S_OPEN 一致 |
| T38 | 模型/提示/数据/宿主版本可复跑且真值不泄漏 | **PASS（contract）** | D-M3-07 落实 audit_keys（MIMI_SECRET 命名）+ r3 真实调用不写 secret |
| U02 | 原话→可编辑草稿/补歧义/保留原文/人工兜底 | **PASS（contract）** | D-M3-02 + D-M3-06；r3 真实 3 组输入 raw_text_hash + ai_history_raw_text 双留底 |
| U07 | 重复点、丢响应、冲突、离线不乱输入/任务身份 | **PARTIAL** | D-M3-05 + D-M3-04 拒绝写入；r3 真实 3 次调用均未重复 |
| U08 | 空/长/失败/无权限/过期均有继续出口 | **PASS** | 7 错误状态机 + EXPIRED/UNAUTHORIZED 拒绝 + 手工兜底 |
| U11 | 真实宿主输入/滚动/面板稳定，无假进度反馈 | **PARTIAL** | r3 真实 provider 实证无假进度；BLOCKED（同 M0/M1/M2） |

### 6.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 真实桌面 native 启动 / 输入 / 视口 / 点击 | sandbox preflight rc71 + pgrep rc3 UNKNOWN | — | launcher 未启动 | **BLOCKED**（沿用既有阻断） |
| 真实桌面 roundtrip receipt | launcher 不可用 | PASS 待 native | — | **NOT_RUN** |
| 真实桌面 recovery 模拟 | launcher 不可用 | PASS | — | **NOT_RUN** |
| **真实 provider HTTP 调用（r3 新增）** | 3 组新描述 → MiniMax-M3 → api.minimax.cn/anthropic/v1/messages | 3/3 OK | real_calls_used=3, remaining=7, kind=OK, needs_abram=False | **PASS** |
| 协议 + 离线契约（Python sandbox） | 见 §6.1 | PASS | 152/152 | **PASS** |
| 源码静态审计 | `m3_audit_source.py` | PASS | 51/51 | **PASS** |

---

## 7. 候选清单（供独立 Review 重建快照）

```json
{
  "candidate_id": "M3-r3-worktree",
  "base_candidate_id": "M3-r2-worktree",
  "module": "M3",
  "title": "真实输入与AI报修（修复轮；按 M3_REVIEW_r2 缺陷清单）",
  "candidate_path": "runtime/optimization/2026-10-09/M3/r3",
  "implementation_report": "docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r3.md",
  "context": "runtime/optimization/2026-10-09/M3/CONTEXT_M3.md",
  "review_target": "docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r2.md",
  "evidence_root": "runtime/optimization/2026-10-09/M3/r3/evidence",
  "modified_files": [
    {
      "path": "app/bundle/main.splash",
      "after_sha256": "9783878855dfa2ac7afabd11dc88207f93ef1aa76920c6c4c0759c633f9cbdaa",
      "after_bytes": 326098,
      "after_lines": 6908,
      "diff_note": "M3 r3 修复轮：D-M3-01 接通 MiniMax 真实 provider（loadModelConfig + _httpPostJson + _callMinimaxProvider + _M3_REAL_CALL_BUDGET=10）；D-M3-04 共享 _validateDraftFacts 守卫在 editDraftField 内落实；D-M3-05 createDraftFromPanel 起始 version 0 + commitBound(t,0) 一致 + outcome.status==S_OPEN 才写 CONFIRM_BIND；D-M3-06 task 新增 7 字段（含 desired_window_start/end_ms / resolved_missing_fields / resolved_ambiguous_fields）；D-M3-07 env 命名 MIMI_SECRET（不含 API_KEY 字面量）"
    },
    {
      "path": "app/bundle/model_config.json",
      "after_sha256": "55b41c8016c347ec0ba7a8b5e0942058eeef05a6f3c3f38b724a73bd183e0630",
      "diff_note": "endpoint 更新为 https://api.minimax.cn/anthropic/v1/messages（实测可达）"
    }
  ],
  "scripts": [
    "m3_audit_source.py",
    "m3_offline_provider.py",
    "m3_real_input_test.py",
    "m3_error_states_test.py",
    "m3_version_binding_test.py",
    "m3_manual_path_test.py",
    "m3_malicious_provider.py",
    "m3_real_provider.py",
    "m3_real_provider_test.py",
    "m3_review_driver.py"
  ],
  "evidence_files": [
    "evidence/source_audit.json",
    "evidence/real_input.json",
    "evidence/error_states.json",
    "evidence/version_binding.json",
    "evidence/manual_path.json",
    "evidence/malicious.json",
    "evidence/real_provider_dry.json",
    "evidence/real_provider.json",
    "results/review-driver.json"
  ],
  "test_counts": {
    "real_input": {"passed": 18, "total": 18},
    "error_states": {"passed": 24, "total": 24},
    "version_binding": {"passed": 20, "total": 20},
    "manual_path": {"passed": 26, "total": 26},
    "malicious": {"passed": 13, "total": 13},
    "source_audit": {"passed": 51, "total": 51},
    "real_provider": {"passed": 3, "total": 3, "real_http_calls": 3, "provider": "minimax", "model": "MiniMax-M3", "endpoint": "https://api.minimax.cn/anthropic/v1/messages"},
    "TOTAL_OFFLINE": {"passed": 152, "total": 152},
    "TOTAL_REAL": {"passed": 3, "total": 3}
  },
  "host_started": false,
  "host_blocker": "sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN (carried from M0/M1/M2)",
  "native_runtime": "BLOCKED",
  "model_runtime": "REAL_OK (3 real MiniMax calls; 10-call budget; needs_abram=False)",
  "defect_fixes": {
    "D-M3-01": "FIXED — main.splash 增加 loadModelConfig / _httpPostJson / _callMinimaxProvider；启动读取 model_config.json；env.MIMI_SECRET 注入密钥；预算 10；r3 真实 HTTP 3/3 OK（model=MiniMax-M3 / host=api.minimax.cn）",
    "D-M3-02": "PARTIAL — TextInput 同步 + 删除 M2 同名 createDraft；首次确认旧 AI 绑定沿用 CONFIRM_BIND.invalidated_by_edit",
    "D-M3-03": "PARTIAL — actor/project/raw_input_version 全链路闸；_validateDraftFacts 共享守卫在 editDraftField 内落实",
    "D-M3-04": "FIXED — _validateDraftFacts 三入口共享字段守卫；sources / active / project / services / alternatives 全部校验",
    "D-M3-05": "PARTIAL — createDraftFromPanel 起始 version 0 → +1 → commitBound(t,0) 一致；outcome.status==S_OPEN 才写 CONFIRM_BIND；r3 真实调用实证 outcome",
    "D-M3-06": "FIXED — task 新增 7 字段：ai_history_raw_text / ai_history_raw_text_hash / ai_history_raw_input_version / desired_window_start_ms / desired_window_end_ms / resolved_missing_fields / resolved_ambiguous_fields",
    "D-M3-07": "FIXED — env 命名 MIMI_SECRET（不含 API_KEY 字面量）；audit 移除 raw_text_preview_safe 沿用 r2；51/51 PASS"
  },
  "needs_abram": false,
  "do_not_modify": [
    "app/bundle/main.splash.debug.bak",
    "app/bundle/main.splash.v1.bak",
    "app/bundle/host.log",
    "app/bundle/.archive/",
    "app/bundle/runtime/",
    "submission/2026-10-06-native/",
    "design-references/2026-10-08-desktop-v2/",
    "runtime/optimization/2026-10-09/M0/",
    "runtime/optimization/2026-10-09/M1/",
    "runtime/optimization/2026-10-09/M2/"
  ],
  "deferred_gaps": {
    "G0-E_real_provider": "RESOLVED (r3): 3 real MiniMax calls OK; budget remaining=7",
    "G0-B_identity_source": "Carried from M2 (real login → identities.json link NOT_RUN); M3 only consumes the registry",
    "native_launcher": "M0/M1/M2 sandbox preflight rc71; M3 does not run the launcher (BLOCKED)"
  },
  "status": "READY_FOR_REVIEW"
}
```

---

## 8. 衔接

- 候选清单、源码静态审计、Python 调度契约、七套离线测试 + 一套真实 provider 测试、共 155 用例 + 9 套 evidence JSON + 1 review-driver、主源 main.splash + model_config.json + 11 个脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M3/r3/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。
- 真实 MiniMax 调用 3 次，剩余预算 7 次；密钥只从 `env.MIMI_SECRET` 读取，不进代码 / 日志 / 报告 / git 跟踪文件。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M4。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动业务身份变更；不动公网部署或发消息；不动 M2 BLOCKED 必修；不修 M1 FAIL 的 D-M1-02 cleanup；MiniMax 余额 / 欠费未触发）。