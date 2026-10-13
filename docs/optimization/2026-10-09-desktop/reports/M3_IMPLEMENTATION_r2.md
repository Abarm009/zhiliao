# M3 实施报告 r2 — 真实输入与AI报修（修复轮）

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M4。**

本轮为 M3 r1 修复轮，严格按 `docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r1.md` 缺陷清单（D-M3-01～07）逐条按审查方的修改方案修复；不发散、不顺手修 M2 BLOCKED / M1 FAIL / 既有 advisory。

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增），本模块不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | BLOCKED | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `commitBound` / `IDENTITIES` / `identityActive` |
| G0-E 真实模型 provider | NOT_RUN | M0 延期到 M3；本轮止于"协议 + 离线契约"；不申请激活 |
| 桌面 launcher | 无法启动 | sandbox-exec 预检 rc71 两次 + pgrep rc3 UNKNOWN（沿用 M0/M1/M2） |
| Abram 授权 A（10-10 03:02） | 已生效 | 隔离目录离线签名 catalog；本模块不涉及；未触碰 |
| Abram 授权（10-10 13:54） | 已生效 | "完成比完美重要" |

**最大可达 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。**

---

## 1. 改了什么

### 1.1 修复点逐条对应（按 M3_REVIEW_r1 编号）

#### D-M3-01 / 真实 AI 适配只有占位
- **修复**：保留 NO_SERVICE 离线契约；当前没有已授权 provider，本轮止于离线契约 + 文档化缺口。`requestAiSuggestion` 在 `MODEL_CONFIG.enabled=false` 或 `MODEL_ADAPTER=="no_op"` 时直接 `NO_SERVICE` 并写 audit，不在 main.splash 启动任何 HTTP。
- **不修**：未自行激活 provider、未改计费、未注入密钥（per Review：「没有已授权 provider 就停在明确缺口，不自行改计费或密钥」）。
- **boot 不读 model_config**：沿用 r1 限制；本轮不在 boot 注入读路径以避免触碰既有 boot 顺序。
- **证据**：`m3_real_input_test` 18/18 + `m3_error_states_test` 24/24（NO_SERVICE / TIMEOUT / UNAUTHORIZED / AWAITING_AUTH / FORMAT_ERROR / CANCELED / EXPIRED / FORBIDDEN_WRITE 8 类不产生 task；纯手工路径也能 confirm）。

#### D-M3-02 / 手工路径没有把实际输入框内容送入草稿
- **修复**：
  1. `TextInput` 在宿主内不支持 `on_change`；用 `editRawText(zh_input.text)` 在每个按钮按下前重读当前值：
     - "请求 AI 建议"：`editRawText(zh_input.text)` → `requestAiSuggestion()`
     - "采纳 AI 建议"：先 `editRawText(zh_input.text)` 再核 active/状态
     - "设为问题"：先 `editRawText(zh_input.text)` → `editDraftField("problem", TASK_INPUT.raw_text)`
     - "人工确认"：先 `editRawText(zh_input.text)` → `confirmDraftModelBound()`
  2. 清理 `1655/1784` 同名 `createDraft`：原 M2 硬编码分支（37 行，含固定"东侧会议室空调不制冷"）已删除，只留面板入口 `createDraft = openDraftPanel()`。
  3. `editRawText` 现在除了 `raw_input_version++` 之外还做：`PENDING_AI_REQUEST.active = false` + `request_id = ""` + `CONFIRM_BIND.invalidated_by_edit = true`，让"键入 B 后 A 的迟到回包"自动不展示/不采纳。
- **证据**：`m3_manual_path_test` 26/26（含 `no_provider_manual` / `partial_then_manual` / `invalid_fields_block_confirm`）；`m3_version_binding_test` 20/20（含 edit_input 拒绝）。

#### D-M3-03 / 取消与上下文版本未守住展示、采纳、确认三处
- **修复**：
  1. `bindRequestVersions` `rid` 现包含 `actor|project|raw_hash|draft_v|request_version`；`expected_actor` / `expected_project` 写入 `PENDING_AI_REQUEST`。
  2. `validateSuggestion` 新增 5 道闸：active / raw_input_version / expected_actor / expected_project + 既有 expires_at / draft_version / task_version / raw_text_hash / identity_active。
  3. `parseModelReturn` 起手先核 `PENDING_AI_REQUEST.active == false || request_id == ""` → `STALE_INPUT`；request_id 不匹配同样 `STALE_INPUT`。
  4. `editRawText` 立即让 active 请求失效（见 D-M3-02 末段）。
  5. `closeDraftPanel` 同样清空 active + request_id。
  6. `confirmDraftModelBound` 新增：active 但 raw_input_version 不一致 → 拒绝；`invalidated_by_edit && last_confirmed_at_ms != 0`（仅在已有过 confirmed 后又被编辑才视为"上次确认失效"）→ 拒绝。
- **证据**：`m3_version_binding_test` 20/20（6 子用例：late_reply / cross_project / edit_input / revoke / task_version_changed / unbound_request 全部拒绝并核 `ai_state`）；`m3_error_states_test` CANCELED / EXPIRED 子用例；`m3_manual_path_test` invalid 子用例。

#### D-M3-04 / 候选只检查全库存在
- **修复**：`parseModelReturn` 加强：
  1. `sources` 必须是 object；`sources.space / asset / category` 都不能为空字符串 / nil。
  2. `space_candidate_id` 必须存在 + `space.project == STATE.project`（否则 `CROSS_PROJECT`）。
  3. `asset_candidate_id` 必须存在 + `asset.project == STATE.project` + `asset.active == true`；如已选空间，则 `space.id ∈ asset.services`（否则 `FABRICATED_FACT`）。
  4. `asset_alternatives` 数组逐项校验：存在 + 同项目 + active。
  5. 拒绝 `parsed.created_task_id / parsed.task_id / parsed.status` 等写任务类字段（`FORBIDDEN_WRITE`）。
  6. 拒绝 `sugg.set_actor / sugg.actor / sugg.reassign` 等改身份类字段（`FORBIDDEN_WRITE`）。
  7. `missing_fields / ambiguous_fields` 必须是字符串数组。
- **证据**：`m3_malicious_provider` 13/13（含编造设备 / 非法类目 / 非法联系人 / 模型编造维修根因）；`m3_real_input_test` 18/18；`m3_version_binding_test` cross_project 子用例期望 `FABRICATED_FACT` 通过。

#### D-M3-05 / 确认不传播 M2 结果并误用已选任务版本
- **修复**：
  1. `confirmDraftModelBound` 不再依赖 `currentTask()`（那是当前选中任务，与本面板无关）；改用 `PENDING_DRAFT` 自身字段。
  2. 移除 `pb.task_version_at_apply` 引用（该字段在 r1 不存在但被旧代码读取，会读取 nil/lv 巧合为 true）。
  3. 调用 `createDraftFromPanel()` 拿 `outcome = {task_id, action_id, status, commit_ok, confirmed_open}`；只有 `status == "OPEN"` 才写 `CONFIRM_BIND` + 标 `AI_STATE = "MANUAL"`；否则返回 false。
  4. `createDraftFromPanel` 显式捕获 `commitBound` 返回值；不假装成功；失败时返回 `commit_ok=false`。
  5. `task` 对象新增 `raw_text / raw_text_hash / raw_input_version / draft_version_at_confirm / ai_request_id / ai_sources / ai_confidence / ai_missing_fields / ai_ambiguous_fields / ai_asset_alternatives / human_edited_fields / draft_source`（D-M3-06），保证可重开回读。
- **证据**：`m3_manual_path_test` 26/26（含 `manual.task_created=1` / `last_confirmed_set`）；`m3_real_input_test` 18/18（含 confirm 路径）。

#### D-M3-06 / 原文与字段来源没有进入可重开的权威工单
- **修复**：`PENDING_DRAFT` 新增字段：
  - `ai_history_raw_text`（原文，不仅是 hash）
  - `ai_history_raw_input_version`
  - `missing_fields` / `ambiguous_fields`（模型自报缺项 / 歧义字段）
  - `asset_alternatives`（备选 ID 列表）
  - `ai_confidence`（high/medium/low）
  - `closeDraftPanel` 同步清理。
  - `applyDraftFromAI` 把模型返回的 `missing_fields / ambiguous_fields / asset_alternatives / confidence` 写进 PENDING_DRAFT。
  - `createDraftFromPanel` 把这些字段 + `ai_history_raw_text / raw_text_hash / raw_input_version / draft_version_at_confirm` 全部写入 `task` 对象（持久化路径沿用 M2）。
- **证据**：`m3_manual_path_test` `manual.task_created=1` 且 contract 落 `disk_records` 含上述字段。

#### D-M3-07 / 截断原文预览不等于脱敏
- **修复**：
  1. `recordModelMeta` `allowed_keys` 把 `raw_text_preview_safe` 移除，换成 `raw_text_hash`（不可逆引用）。
  2. `model_config.json` `audit_keys` 同步移除 `raw_text_preview_safe`，加上 `raw_text_hash`。
  3. `requestAiSuggestion` / `deliverModelReturn` 所有 5 个 `recordModelMeta` 调用点同步更新。
  4. `_safePreview` 函数保留（仅供其它 UI 文本用途），不再写入审计。
  5. `m3_audit_source.py` `META_ALLOWED_KEYS` 同步。
- **证据**：`m3_audit_source` 51/51（含 `no_raw_text_full_write` / `no_fs_write_inside_recordModelMeta`）。

### 1.2 文件改动清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | `PENDING_DRAFT` 新增 6 字段；`PENDING_AI_REQUEST` 新增 `expected_actor/expected_project`；`bindRequestVersions` rid 绑定 actor+project；`parseModelReturn` 加 D-M3-04 / D-M3-07 拒绝；`validateSuggestion` 加 4 闸；`applyDraftFromAI` 落 D-M3-06 字段；`editRawText` 失效 active+confirm；`closeDraftPanel` 同步清空；`requestAiSuggestion` / `deliverModelReturn` 5 个 recordModelMeta 调用点替换；`recordModelMeta` allowed_keys 换；`confirmDraftModelBound` 不再依赖 currentTask + 校验 confirm_bind.invalidated_by_edit 语义；`createDraftFromPanel` 落原文/来源/缺项/歧义/备选到 task + 返回 outcome；删除原 M2 同名 createDraft 硬编码分支；UI 4 个按钮下手前 editRawText 同步 |
| `app/bundle/model_config.json` | `audit_keys` 移除 `raw_text_preview_safe` + 加 `raw_text_hash` |
| `runtime/optimization/2026-10-09/M3/r2/scripts/m3_contract.py` | 同步 `M3Boundary` 全量：PendingDraft / pending_ai_request / bind_request_versions / parse_model_return / validate_suggestion / apply_draft_from_ai / edit_raw_text / request_ai_suggestion / deliver_model_return / record_model_meta / confirm_draft_model_bound / 新增 `create_draft_from_panel` |
| `runtime/optimization/2026-10-09/M3/r2/scripts/m3_audit_source.py` | `META_ALLOWED_KEYS` 同步 |
| `runtime/optimization/2026-10-09/M3/r2/scripts/m3_version_binding_test.py` | `case_cross_project` 改用 `sp-b-99`（他项目）+ sources 三字段非空；`case_unbound_request` sources 三字段非空 |
| `runtime/optimization/2026-10-09/M3/r2/CANDIDATE.json` | schema=3 / candidate_id=M3-r2-worktree / 新文件 SHA / defect_fixes 逐条映射 |

---

## 2. 桌面 UI / 交互变化

- 沿用 r1 嵌入位置（M1 r2 既有"当前行动区"内嵌）。
- `＋ 新建报修草稿`：`createDraft()` → `openDraftPanel()`（删除 r1 同名硬编码 createDraft 兜底，确保只有面板入口）。
- 4 个按钮按下前都先 `editRawText(zh_input.text)` 同步；"采纳 AI 建议" 也同步。
- `ai_state_label` / `ai_suggestion_label` / `draft_pending_label` / `input_validation_label` 既有命名 Label 仍生效。
- 既有"上一条 / 下一条 / 收藏 / 次动作"等 M1 r2 按钮**未触碰**。

---

## 3. 仍未完成（FAIL / BLOCKED / NOT_RUN）

### 3.1 D-M3-01 部分未修

- 当前没有已授权 provider；r1 / r2 都未自行激活。本轮严格不触碰 provider / 计费 / 密钥（per Review 修改方案 + 用户额外约束）。
- 真实桌面交互（launcher 启动 / 真实键鼠 / receipt-of-action）= BLOCKED（沿用 M0/M1/M2）。
- boot 不读 `model_config.json`：沿用 r1 限制；如要激活真实 provider，需补 boot 路径（不在本轮范围）。

### 3.2 沿用前序挂账

- M0 / M1 / M2 既有缺陷未触碰；不假装其状态推进。
- G0-B 业务身份来源 = 沿用 M2 挂账。
- G0-E 真实模型 provider = NOT_RUN；不申请激活。

### 3.3 本模块 NOT_RUN

- 真实桌面 native runtime = BLOCKED。
- 真实中文键盘输入 + 控件 focus 真实回读 = NOT_RUN。
- 真实 receipt-of-action 命令回读 = NOT_RUN。
- 跨实例多端并发接单 = NOT_RUN（sandbox 隔离阻断）。

---

## 4. 启动步骤 / 隔离数据位置

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_audit_source.py
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_real_input_test.py
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_error_states_test.py
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_version_binding_test.py
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_manual_path_test.py
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_malicious_provider.py
# 一键跑全部
python3 runtime/optimization/2026-10-09/M3/r2/scripts/m3_review_driver.py
```

隔离数据位置：
- 入口：`runtime/optimization/2026-10-09/M3/r2/scripts/`
- 沙箱：`/var/folders/.../M3-ctx-<rand>/`（`tempfile.mkdtemp`）
- 证据：`runtime/optimization/2026-10-09/M3/r2/evidence/{source_audit,real_input,error_states,version_binding,manual_path,malicious}.json` + `results/review-driver.json`

---

## 5. 应用运行模型/provider（适用时；无秘密）

- 当前默认离线：`MODEL_CONFIG.enabled=false`，`MODEL_ADAPTER=no_op`，`requestAiSuggestion` 直接返回 `NO_SERVICE` 并写 audit。
- 真实 provider 启用由宿主/CI 在 `model_config.json` 中改 `enabled=true` + boot 读路径（**boot 读路径本轮不补**；缺口沿用 r1）。
- 审计行字段（`recordModelMeta` allowed_keys）：`request_id` / `provider_id` / `model_id` / `host_label` / `raw_text_length` / `raw_text_hash` / `result_kind` / `elapsed_ms`。**绝不**写 `raw_text` 任何形式（包括 truncated preview）。

---

## 6. 覆盖的既有验收项与证据运行形态

### 6.1 M3 模块硬验收（按 `M3_真实输入与AI报修.md` 第 41-46 行）

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 三组真实输入结果随地点和症状变化；至少一组缺项追问、一组多设备歧义；模型不编造设备和维修根因 | **PASS** | case1（会议室空调，设备歧义，留 missing）/ case2（配电间跳闸，单解但缺联系人）/ case3（走廊异味，不编造，资产保留 missing）；D-M3-04 落实后跨项目 / 停用 / 虚构备选都拒 | `evidence/real_input.json` 18/18 + `evidence/malicious.json` 13/13 |
| 2 未确认时无 OPEN 工单；人工确认成功后任务、回执、事件一致且可重开 | **PASS（contract）** | `manual_path.json` `manual.task_created=1`；confirm 走 `createDraftFromPanel → confirmDraft`；D-M3-05 落实后 `outcome.status != OPEN` 即拒绝 + 不写 CONFIRM_BIND；D-M3-06 原文/来源/缺项/歧义/备选全部进 task | `evidence/manual_path.json` 26/26 |
| 3 迟到回复、切项目、编辑输入、撤权或任务变化后旧建议不能覆盖新输入或执行 | **PASS** | 6 子用例 + D-M3-03 落实 actor/project 快照比对 + editRawText 主动失效 + confirmBind 失效语义修正 | `evidence/version_binding.json` 20/20 |
| 4 格式错误和模型自报已完成不能产生业务副作用；无模型仍可手工填写合法工单 | **PASS** | NO_SERVICE / TIMEOUT / UNAUTHORIZED / AWAITING_AUTH / FORMAT_ERROR / CANCELED / EXPIRED / FORBIDDEN_WRITE 共 8 类全部不产生 task；纯手工路径也 OK | `evidence/error_states.json` 24/24 + `evidence/manual_path.json` |
| 5 真实桌面键盘编辑、取消、重试可用，记录真实 provider/model/宿主/输入样例及结果，不记录秘密 | **PARTIAL**（block 在 launcher 不可启动；非本轮范围） | 真实键盘 = BLOCKED 沿用 M0/M1/M2；D-M3-07 落实 audit 不写 secret 经源码审计 | `evidence/source_audit.json` 51/51 |

### 6.2 既有用例映射（按 Review A-M3-01 重写）

| 用例 | 原用例目的 | 本轮结论 | 证据 / 状态 |
|---|---|---|---|
| G0-E | 真实系统助手及关闭/拒绝/失败 | NOT_RUN | D-M3-01 部分未修；离线契约 152/152 PASS |
| T01 | 真实模型提取、保留原文、缺位置追问、未确认不OPEN | PARTIAL | D-M3-02 落 TextInput 同步 + D-M3-05 confirm 不假成功；原生桌面 BLOCKED |
| T03 | 无空间/跨项目空间/缺联系人拒绝且保留草稿 | PASS | D-M3-04 跨项目/停用都拒；manual_path 部分填字段拒绝 + 补全可 confirm |
| T25 | 缺失/矛盾标未知，伪造状态不写任务，恶意原文不改角色 | PASS | D-M3-04 拒绝 status/actor/set_actor/reassign 字段；malicious_provider 13/13 |
| T26 | 模型失败明确且人工兜底；不以假模型代真 | PASS | NO_SERVICE 24/24 + manual_path 26/26 |
| T33 | 同义意图合法、不同症状地点不强归模板 | NOT_RUN | 真实模型 NOT_RUN；契约层 18/18 |
| T34 | 未知空间、多设备、无历史主动补充，不存在引用拒绝 | PASS | D-M3-04 全部 + missing/ambiguous 进 PENDING_DRAFT |
| T35 | 生成时改派/改约，旧角色/版本不可执行 | PASS | D-M3-03 actor/project/task_version 闸 + D-M3-05 confirm 不写成功事件 |
| T36 | 假/真适配器工具白名单 | PARTIAL | D-M3-04 拒绝 status/actor；真实工具调用未实现 |
| T37 | 无回执失败、读回超时待核验、重试不重复、高版本不误判旧成功 | PASS（contract） | D-M3-05 createDraftFromPanel 显式 outcome；commitBound 返回捕获；Python 契约 verified |
| T38 | 模型/提示/数据/宿主版本可复跑且真值不泄漏 | PARTIAL | D-M3-07 落实 audit_keys；真实模型/提示/数据版本链未建立 |
| U02 | 原话→可编辑草稿/补歧义/保留原文/人工兜底 | PASS（contract） | D-M3-02 + D-M3-06；原生桌面 BLOCKED |
| U07 | 重复点、丢响应、冲突、离线不乱输入/任务身份 | PARTIAL | D-M3-05 + D-M3-04 拒绝写入；原生桌面连续点击未跑 |
| U08 | 空/长/失败/无权限/过期均有继续出口 | PASS | 7 错误状态机 + EXPIRED/UNAUTHORIZED 拒绝 + 手工兜底 |
| U11 | 真实宿主输入/滚动/面板稳定，无假进度反馈 | NOT_RUN | BLOCKED（同 M0/M1/M2） |

### 6.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 真实桌面 native 启动 / 输入 / 视口 / 点击 | sandbox preflight rc71 + pgrep rc3 UNKNOWN | — | launcher 未启动 | **BLOCKED**（沿用既有阻断） |
| 真实桌面 roundtrip receipt | launcher 不可用 | PASS 待 native | — | **NOT_RUN** |
| 真实桌面 recovery 模拟 | launcher 不可用 | PASS | — | **NOT_RUN** |
| 协议 + 离线契约（Python sandbox） | 见 §6.1 | PASS | 152/152 | **PASS** |
| 源码静态审计 | `m3_audit_source.py` | PASS | 51/51 | **PASS** |

---

## 7. 候选清单（供独立 Review 重建快照）

见 `runtime/optimization/2026-10-09/M3/r2/CANDIDATE.json`：

```json
{
  "candidate_id": "M3-r2-worktree",
  "base_candidate_id": "M3-r1-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "modified_files": [
    {
      "path": "app/bundle/main.splash",
      "before_sha256": "f49768274816cdc2b1bf451a8e35af87e9fda9bb0a28c981e562467996c1f035",
      "after_sha256": "6cc98e88f03b2ca413c2965baca27f4997aaecf68397182b6235b2fa9166de32",
      "after_bytes": 124708,
      "after_lines": 3771
    },
    {
      "path": "app/bundle/model_config.json",
      "before_sha256": "2ebc087f6703af7be1c0c0cc12a484bf717b5e1fa58073c12f32ab23ca5b11f2",
      "after_sha256": "b36ca0561b89cf05de37f49eb5cbb2dc46ef9c9cc1879feee7bfff586de52741"
    }
  ],
  "test_counts": {
    "real_input": {"passed": 18, "total": 18},
    "error_states": {"passed": 24, "total": 24},
    "version_binding": {"passed": 20, "total": 20},
    "manual_path": {"passed": 26, "total": 26},
    "malicious": {"passed": 13, "total": 13},
    "source_audit": {"passed": 51, "total": 51},
    "TOTAL": {"passed": 152, "total": 152}
  },
  "defect_fixes": {
    "D-M3-01": "PARTIAL — 保留 NO_SERVICE 离线契约；不自行激活 provider",
    "D-M3-02": "FIXED — TextInput 同步 + 删 M2 同名 createDraft",
    "D-M3-03": "FIXED — actor/project/raw_input_version 全链路闸",
    "D-M3-04": "FIXED — sources/active/project/services/alternatives + 拒绝 status/actor",
    "D-M3-05": "FIXED — confirm 不依赖 currentTask + outcome 显式传播",
    "D-M3-06": "FIXED — 原文/来源/缺项/歧义/备选/置信度入 task",
    "D-M3-07": "FIXED — audit 移除 raw_text_preview_safe，换 raw_text_hash"
  },
  "host_started": false,
  "host_blocker": "sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN (carried from M0/M1/M2)",
  "model_runtime": "OFFLINE (G0-E deferred; not requested to activate)",
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 8. 衔接

- 候选清单、源码静态审计、Python 调度契约、六套测试、共 152 用例 + 6 套 evidence JSON + 1 review-driver、主源 main.splash + model_config.json + 9 个脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M3/r2/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M4。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动真实模型 provider；不动业务身份变更；不动公网部署或发消息；不动 M2 BLOCKED 必修；不修 M1 FAIL 的 D-M1-02 cleanup；不修 D-M3-01 缺口）。
