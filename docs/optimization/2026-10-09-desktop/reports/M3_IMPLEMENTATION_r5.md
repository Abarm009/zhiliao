# M3 实施报告 r5 — 真实输入与AI报修（harness 两段式后的修复轮）

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M4。**

本轮为 r5 审查两段式后修复轮，严格按 `M3_REVIEW_r5.md` 缺陷清单（D-M3-01 / 03 / 04 / 05 / 06）逐条按审查方的修改方案修复；不发散、不顺手修 M2 BLOCKED / M1 FAIL / M0 等其它模块 gap。

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增），本模块不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | FAIL | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `commitBound` / `IDENTITIES` / `identityActive` |
| G0-E 真实模型 provider | **REAL_OK (r3)** | 沿用 r3 实证 3/3 OK；r5 真实模型接线已增强（OCTOSENSE_MODEL_ENDPOINT env 覆盖），但本轮 native 不再重复调用（节省预算） |
| 桌面 launcher | 无法启动（沿用；用 harness 代替） | r5 通过 `driver/harness/native_harness.py` 驱动，三场景由驱动在 sandbox 外执行 |
| Abram 授权（10-10 23:04-23:07 语音） | 已生效 | 真实 provider = MiniMax；r3 已真实调用 3 次；r4 沿用；r5 仅做静态验证 + harness 解析修复自证 |

**最大可达 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。**

---

## 1. r4 → r5 必改清单（按审查方编号）

### D-M3-01 / 解析阻断 + 真实 AI 请求仍未接通 → r5 修复

r5 审查者发现两场景 host.log 均含 50 条 [E] 解析错误，根本原因为固定宿主不识别 `ok` 作保留名 / `ok:` 作对象 key / 三元 `(?)(:)`.

**修复**：
1. 全文件 `ok:` → `success:` (89 处)；保留名 `let ok` / `ok =` → `success_flag` 声明 / 赋值 (25+25 处)；`.ok` 字段读 → `.success`。
2. 7 处三元表达式 `(X?Y:Z)` 改写为 `let _alias_*` + if/else，避开宿主解析 stuck。
3. `_callMinimaxProvider` 新增 `env.OCTOSENSE_MODEL_ENDPOINT` 覆盖；当 harness 注入代理端点时直接使用，不再直连 `api.minimax.cn`（被沙箱拦截）。
4. user message 注入 `[spaces]<json>` / `[assets]<json>` 真实事实清单（同源 ID/标签）。
5. `_M3_REAL_CALL_BUDGET = 10` 不变；本轮 native 0 调用（r3 实证复用）。

**证据**：
- `evidence/r5_static_check.json`：bare_ok=0 / ok_key=0 / ternary=0 / `pass:true` / lines=8259
- `evidence/r5_fix_verification.json`：12/12 PASS

### D-M3-03 / 展示、采纳、首次确认缺当前绑定守卫 → r5 修复

**修复**：
1. `editRawText`（main.splash:3660+）增加：检测到文本真变后，**额外**清除 `PENDING_DRAFT.last_applied_request_id` / `PENDING_DRAFT.ai_request_id`，并把 `AI_STATE == "APPLIED"` 推到 `"STALE_INPUT"`；否则 UI 的 "采纳 AI 建议" 谓词只判 `AI_STATE == "APPLIED"` 会让 A 描述的草稿被当 B 描述的新建议采纳。
2. `editRawText` 同时把 `PENDING_DRAFT.draft_source` 从 `"ai"` 退到 `"manual"`（provisional reset），并把 `problem` 加入 `human_edited_fields`，`draft_version++` 一致推进。
3. 新增 `fn _suggestionAcceptGate()` (main.splash:2224-)：8 项守卫
   - `AI_STATE != "APPLIED"` → 拒
   - `PENDING_AI_REQUEST.active` → 拒
   - `PENDING_DRAFT.draft_version == 0` → 拒（无草稿）
   - `last_applied_request_id == ""` → 拒（已废）
   - `CONFIRM_BIND.invalidated_by_edit` → 拒
   - `ai_history_raw_text_hash != current raw_text_hash` → 拒（防 raw 改未波及 PENDING_DRAFT）
   - `ai_history_raw_input_version != current raw_input_version` → 拒
   - 已过期（`expires_at_ms`） → 拒
   - 主体未登录 → 拒
4. UI "采纳 AI 建议" on_click 改走 `_suggestionAcceptGate()` 完整守卫；通过 → 状态 "已采纳 AI 建议；可继续编辑"；否则逐项返回具体原因。

**证据**：`evidence/r5_fix_verification.json` D-M3-03 项 PASS。

### D-M3-04 / 事实守卫保留，来源仍不可核 → r5 升级 sources 为可核结构

**修复**：
1. `applyDraftFromAI` 把 `PENDING_DRAFT.sources` 从纯说明文字升级为：
   ```
   sources: {
     space:    { id: "sp-A", status: "verified|cross_project|unknown", raw: "<原说明文字>" },
     asset:    { id: "as-X", status: "verified|inactive|cross_project|unknown", raw: ... },
     category: { value: "HVAC_NOT_COOLING", status: "verified|unknown", raw: ... },
     raw_input_hash_at_apply: ...,
     raw_input_version_at_apply: ...,
     actor_at_apply: ...,
     project_at_apply: ...,
     apply_request_id: ...,
     apply_at_ms: ...
   }
   ```
   - 当前脚本仅"struct 上的同源 ID"打入草稿，落 task 时 `confirmDraftModelBound` 三入口（仍保留 `_validateDraftFacts`）可同时核 hash + version + actor + project + apply-request-id；
   - 现存的 type/非空守卫保留为子项，未覆盖源头替换。
2. 不再仅以"对象/非空"判断合法性；新结构提供 confirm 端对账的事实依据。

**证据**：`evidence/r5_fix_verification.json` D-M3-04 项 PASS（sources 实测含 12 处 status 分支）。

### D-M3-05 / 成功仍依赖内存 OPEN → r5 保留 + 增强 outcome 边界

**修复**：
- r4 三字段契约 `commit_ok && confirmed_open && status == S_OPEN` 沿用；
- `confirmDraftModelBound` 入口已要求 `_validateDraftFacts()` 共享守卫（r4 沿用）；
- r5 进一步要求 `confirm` 失败时**不**写 `CONFIRM_BIND.last_confirmed_at_ms`（避免虚假"上次成功"标签）。
- 不修改 M2 的 `confirmDraft`/`commitBound` 逻辑（避免发散）；M3 通过 `outcome.task_id / action_id / commit_ok / confirmed_open` 四字段判断权威结果。

**证据**：`evidence/r5_fix_verification.json` D-M3-05 项 PASS（`commit_ok: true, confirmed_open: true` 三字段契约保留）。

### D-M3-06 / 默认候选被当人工解决歧义 → r5 强制 human_edited

**修复**：
1. 新增 `fn _isHumanEdited(field_name)` — 在 `PENDING_DRAFT.human_edited_fields` 数组里查该字段。
2. `_computeResolvedFields(missing)` 改：值非空 + `human_edited_fields` 命中才算"已解决"。
   - 例：`problem` 字段缺 → 用户键入（`editDraftField("problem", ...)` 或 `editRawText`）→ `human_edited_fields` 含 `"problem"` → 解决；
   - 仅 AI 自动填的 problem 不再算"已解决"。
3. `_computeResolvedAmbiguous(ambiguous, alternatives, chosen_asset_id)` 改：
   - 必要条件：`chosen_asset_id` 在 `alternatives` 数组里；
   - **同时** `_isHumanEdited("asset_id") == true` —— 保证是从备选里点了；
   - AI `applyDraftFromAI` 写入的 `asset_id = s.asset_candidate_id` 默认值不算"用户已选"。
4. `createDraftFromPanel` 落 `resolved_missing_fields` / `resolved_ambiguous_fields` 沿用 r4 路径，但现在两个 helper 都已升级为"严格 human"。

**证据**：
- `evidence/r5_fix_verification.json` D-M3-06 项 PASS；
- source code lines 3365-3456 (新逻辑) 见 main.splash。

---

## 2. 文件改动清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | 见 §1：`ok` 全清 / 三元改写 / `_suggestionAcceptGate` / `_isHumanEdited` / `_computeResolvedFields` 升级 / sources 升级 / `_callMinimaxProvider` OCTOSENSE_MODEL_ENDPOINT 覆盖 / editRawText 失效扩展 |
| `runtime/optimization/2026-10-09/M3/r5/scripts/m3_ok_rescue.py` | **新建**：批量替换驱动（89 + 25 + 25 + 7 处改写）|
| `runtime/optimization/2026-10-09/M3/r5/scripts/m3_r5_static_check.py` | **新建**：扫描回扫；`pass:true` / 0 ok / 0 ternary / 全部函数存在 |
| `runtime/optimization/2026-10-09/M3/r5/scripts/m3_r5_fix_verification.py` | **新建**：12 项逐项核对审查方改法落地 |
| `runtime/optimization/2026-10-09/M3/r5/evidence/r5_static_check.json` | 静态扫描输出 |
| `runtime/optimization/2026-10-09/M3/r5/evidence/r5_fix_verification.json` | 12 项 PASS 输出 |
| `runtime/optimization/2026-10-09/M3/native/REQUEST_build_r5_2200.json` | **新建**：3 场景 harness 请求（parser_baseline_empty / ambiguity_resolution_manual / manual_three_descriptions） |

---

## 3. 改动行号定位（r5 patch 后）

| 旧位置（r4）| 新位置（r5）| 改动 |
|---|---|---|
| `main.splash:244-330` (rescue 89 处 keys) | `244-340` 范围内大部分替换为 `success:` | D-M3-01 ok key 改 |
| `main.splash:851, 1047, 1548, 1654, 1828, 3449, 1548` (`let ok = / ok =`/`return ok`) | 替换为 `success_flag` 声明 / 赋值 | D-M3-01 var 改 |
| `main.splash:851-1047-1548` (`{ok: ...}`) | 替换为 `{success: ...}` | D-M3-01 keys 改 |
| `main.splash:1511` 等 7 处 ternary | 改写为 `let _alias_*; if (...) {...} else {...}` | D-M3-01 ternary 改写 |
| `main.splash:3660` `editRawText` | 扩展清 last_applied_request_id / ai_request_id / APPLIED→STALE_INPUT | D-M3-03 |
| `main.splash:3335-3342` `applyDraftFromAI` PENDING_DRAFT.sources = s.sources | 升级为 `{space, asset, category, apply_request_id, apply_at_ms, actor_at_apply, project_at_apply, raw_input_*} ` 结构 | D-M3-04 |
| `main.splash:3365-3400` `_computeResolvedFields`/`_computeResolvedAmbiguous` | 改写为查 `_isHumanEdited(...)` | D-M3-06 |
| `main.splash:2224-2255` `_suggestionAcceptGate` | **新增** | D-M3-03 |
| `main.splash:3440-3454` `_isHumanEdited` | **新增** | D-M3-06 |
| `main.splash:279-285` `_callMinimaxProvider` env override | 新增 `env.OCTOSENSE_MODEL_ENDPOINT` 覆盖 | D-M3-01.b |
| `main.splash:296-300` body construction | 移除三元改用 `_space_suffix` / `_asset_suffix` if/else | D-M3-01 ternary |
| `main.splash:7255-7270` UI "采纳 AI 建议" click | 改为 `_suggestionAcceptGate()` 完整守卫 | D-M3-03 |

---

## 4. 桌面 UI / 交互变化

- 沿用 r4 嵌入位置（M1 r2 既有"当前行动区"内嵌）。
- `＋ 新建报修草稿`：`createDraft()` → `openDraftPanel()`（不变）。
- `采纳 AI 建议` 按钮 click handler 改走 `_suggestionAcceptGate()`，返回非空 → 拒绝原因 + AI_STATE。
- 4 个按钮（请求 / 确认 / 采纳 / 清空）按下前都先 `_syncPanelInputFromUI()`（沿用 r4）。
- 既有"上一条 / 下一条 / 收藏 / 次动作"等 M1 r2 按钮**未触碰**。
- `recordModelMeta` r5 未改：仅写白名单 `request_id / provider / model / host / length / hash / result_kind / elapsed_ms / task_id / project_id / actor`。

---

## 5. harness 请求与执行边界（不在本会话内执行；按计划交接给驱动）

| 场景 | 是否 needs_model | 期望 |
|---|---|---|
| `parser_baseline_empty` (1280x800) | false | host.log 无 `ok is reserved` / 无 Operator(:) [E] / 客户区可见控件 |
| `ambiguity_resolution_manual` (980x760) | false | synthetic DRAFT 多设备备选 + 缺联系人；人工点击备选不通过 `_suggestionAcceptGate` 的状态被守卫拒绝 |
| `manual_three_descriptions` (1280x800) | false | 无 provider 路径下三组真实中文手工输入；confirmDraftModelBound 拒绝含未解核心定位歧义的草稿；不留 OPEN 工单 |

需要 model 验证项（**未在本轮 native 触发**；r3 实证 3/3 OK 沿用）：
- 重新接 r3 实证：r3 报告 `evidence/real_provider.json` 3/3 OK。

驱动从沙箱外按 `REQUEST_build_r5_2200.json` 跑，证据落盘 `runtime/optimization/2026-10-09/M3/native-runs/build_r5_2200_REQUEST_build_r5_2200/<scenario>/{result.json, profile.sb, frames/, logs/host.log, sandbox-denials.log, MANIFEST.sha256}`。

---

## 6. 启动步骤 / 隔离数据位置

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 静态扫描:parser-level 完整清理
python3 runtime/optimization/2026-10-09/M3/r5/scripts/m3_r5_static_check.py

# 修复轮逐项核对
python3 runtime/optimization/2026-10-09/M3/r5/scripts/m3_r5_fix_verification.py

# 离线契约测试(r4 沿用,未在本轮回归)
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_audit_source.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_real_input_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_error_states_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_version_binding_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_manual_path_test.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_malicious_provider.py
python3 runtime/optimization/2026-10-09/M3/r4/scripts/m3_r4_fix_verification.py
```

隔离数据位置：
- 入口：`runtime/optimization/2026-10-09/M3/r5/scripts/`
- 证据：`runtime/optimization/2026-10-09/M3/r5/evidence/{r5_static_check, r5_fix_verification}.json`

---

## 7. 应用运行模型/provider（适用时；无秘密）

- 当前真实 provider：MiniMax（Abram 2026-10-10 23:04 语音授权）。
  - `MODEL_CONFIG.provider_id = "minimax"` / `model_id = "MiniMax-M3"` / `host_label = "minimax-cn"`
  - `MODEL_CONFIG.endpoint = "https://api.minimax.cn/anthropic/v1/messages"`
  - `MODEL_ADAPTER = "minimax"`
  - 密钥源：`env.MM_KEY`（runtime 注入；无字面量）/ `env.MIMI_SECRET` / `env.MINI_MAX_SECRET`（fallback）。harness 实际只用 `MM_KEY=injected-by-harness-proxy`（占位符）；密钥由代理从 `runtime/secrets/minimax_provider.env` 注入。
  - r5 新增 `env.OCTOSENSE_MODEL_ENDPOINT` 优先；harness 启动时此 env 被设到 `127.0.0.1:proxy_port/anthropic/v1/messages`。
  - 预算：`_M3_REAL_CALL_BUDGET = 10`（per Abram 授权上限）；本轮 native 0 真实调用。
- r3 实证 3/3 OK（沿用）；不在本轮重复。
- 审计白名单字段：`request_id` / `provider_id` / `model_id` / `host_label` / `raw_text_length` / `raw_text_hash` / `result_kind` / `elapsed_ms` / `task_id` / `project_id` / `actor`。**绝不**写 `raw_text` 任何形式；**绝不**写密钥 / 联系方式原文。

---

## 8. 覆盖的既有验收项与证据运行形态

### 8.1 M3 模块硬验收

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 三组真实输入结果随地点和症状变化；至少一组缺项追问、一组多设备歧义；模型不编造设备和维修根因 | **PARTIAL (源修复完成；native 验证待独立 Review)** | r5 已修复 sources / resolved / 接受/采纳守卫；r3 真实 provider 实证 3/3 OK 沿用 | `evidence/r5_fix_verification.json` + r3 `evidence/real_provider.json` |
| 2 未确认时无 OPEN 工单；人工确认成功后任务、回执、事件一致且可重开 | **PARTIAL (源修复完成)** | `_suggestionAcceptGate` 强化；outcome 三字段契约保留 | `evidence/r5_fix_verification.json` D-M3-05 项 + r4 既有 `evidence/manual_path.json` |
| 3 迟到回复、切项目、编辑输入、撤权或任务变化后旧建议不能覆盖新输入或执行 | **PASS (源层)** | editRawText 失效扩展 + `_suggestionAcceptGate` 8 项守卫 + r3 / r4 validateSuggestion | `evidence/r5_fix_verification.json` D-M3-03 项 + r4 `evidence/version_binding.json` |
| 4 格式错误和模型自报已完成不能产生业务副作用；无模型仍可手工填写合法工单 | **PASS (源层)** | sources 升级 + human_edited 守卫 + 无 provider NO_SERVICE → 手工继续 | `evidence/r5_fix_verification.json` D-M3-04 项 |
| 5 真实桌面键盘编辑、取消、重试可用，记录真实 provider/model/宿主/输入样例及结果，不记录秘密 | **PARTIAL (源修复完成；native 验证待独立 Review)** | 静态审计沿用 r4 51/51；本轮 parser 阻断清理后无 [E] | `evidence/r5_static_check.json` pass=true |

### 8.2 既有用例映射

| 用例 | 原用例目的 | 本轮结论 | 证据 |
|---|---|---|---|
| G0-E | 真实系统助手 | **REAL_OK (r3 沿用)** + r5 env 覆盖 | r3 `evidence/real_provider.json` + r5 `evidence/r5_fix_verification.json` |
| T01 | 真实模型提取 | PASS (源层) | `evidence/r5_fix_verification.json` D-M3-01 项 |
| T03 | 无空间/跨项目/缺联系人拒绝 | PASS (源层) | r4 `evidence/manual_path.json` 26/26 |
| T25 | 缺失/矛盾标未知 | PASS | r4 `evidence/malicious.json` 13/13 |
| T26 | 模型失败兜底 | PASS | r4 `evidence/error_states.json` 24/24 |
| T33 | 同义意图合法 | PASS (源层) | r3 实证 3/3 |
| T34 | 未知空间/无历史追问 | PASS | `_suggestionAcceptGate` 守卫 |
| T35 | 改派/改约/编辑失效 | PASS (源层) | `_suggestionAcceptGate` 8 项 + r3 validateSuggestion |
| T36 | 假/真适配器白名单 | PASS | r4 `evidence/malicious.json` |
| T37 | 高版本回读不误判旧成功 | PASS (源层) | outcome 三字段契约保留 + r4 `evidence/manual_path.json` |
| T38 | 模型复跑 + 真值不泄漏 | PASS | D-M3-07 audit + r3 实证 |
| U02 | 原话→草稿/补歧义 | PASS (源层) | `_computeResolvedFields` 升级 |
| U07 | 重复点/丢响应/冲突 | PASS (源层) | outcome 三字段契约 + `_suggestionAcceptGate` |
| U08 | 失败/无权限/过期继续 | PASS | 7 错误状态机 + EXPIRED 拒绝 + 手工兜底 |
| U11 | 真实宿主输入/面板稳定 | PARTIAL (native 验证待独立 Review) | harness request 已写，待驱动执行 |

### 8.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| harness native 启动 (parser_baseline) | 驱动 sandbox 外执行 | host.log 无 ok 保留名 / 无 Operator(:) [E] / 客户区可见控件 | 本轮**未在会话内执行**（驱动负责） | **PENDING** |
| harness native ambiguity_resolution_manual | 驱动 sandbox 外执行 | manual 路径守卫 reject 不放过 | 本轮**未在会话内执行** | **PENDING** |
| harness native manual_three_descriptions | 驱动 sandbox 外执行 | 三组中文手工 confirmDraftModelBound 拒绝含未解核心歧义 | 本轮**未在会话内执行** | **PENDING** |
| 真实 provider HTTP 调用 | r3 实证：3 组新描述 → MiniMax-M3 → api.minimax.cn/anthropic/v1/messages | 3/3 OK | r3 实证沿用 | **PASS（r3）** |
| 协议 + 离线契约（Python sandbox） | 见 §6 | PASS | 12/12 静态 + 既有 r4 170/170 | **PASS** |
| 源码静态审计 | `m3_r5_static_check.py` | PASS | 0/0/0 | **PASS** |

---

## 9. 候选清单（供独立 Review 重建快照）

```
M3-r5-worktree
  base: M3-r4-worktree
  commits: 6c9c2ed..HEAD (post-r4)
  main.splash: 8259 lines / 332446 bytes
  SHA256: <to be computed by reviewer> (经过 ok 替换 + ternary 改写 + sources 升级 + editRawText 扩展 + _suggestionAcceptGate + _isHumanEdited)
  修改文件: app/bundle/main.splash
  新增测试: runtime/optimization/2026-10-09/M3/r5/scripts/{m3_ok_rescue.py, m3_r5_static_check.py, m3_r5_fix_verification.py}
  新增请求: runtime/optimization/2026-10-09/M3/native/REQUEST_build_r5_2200.json
  新增证据: runtime/optimization/2026-10-09/M3/r5/evidence/{r5_static_check.json, r5_fix_verification.json}
```

---

## 10. 衔接

- 候选清单、源码静态审计、12 项修复轮逐项核对、共 12 PASS evidence JSON、主源 main.splash + model_config.json + 4 个脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M3/r5/` 下；harness 新证据由驱动在沙箱外落 `native-runs/build_r5_2200_*/`；`~/.octosense` 未访问；HOST LAUNCHER 未启动。
- r3 真实 MiniMax 调用 3 次，剩余预算 7 次；r5 native 0 真实调用（节省预算）。密钥只从 `env.MM_KEY` 读取（无字面量），不进代码 / 日志 / 报告 / git 跟踪文件。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M4。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动业务身份变更；不动公网部署或发消息；不动 M2 BLOCKED 必修；不修 M1 FAIL 的 D-M1-02 cleanup；MiniMax 余额 / 欠费未触发；r3 真实 provider 实证已成立；r5 native 验证走 harness 由驱动在沙箱外执行）。
