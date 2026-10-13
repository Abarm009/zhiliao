# M6 实施报告 r5 · 桌面体验收口与持续跟进（修复轮 4）

**状态：READY_FOR_REVIEW。** 仅就 M6_REVIEW_r5 的 D-M6-02、D-M6-03、D-M6-04 三项 P1 缺陷逐条按审查方修改方案深化修复；不发散；不修 M0..M5 任何未闭合缺陷；不启动 native launcher；不修挂账建议 A-M6-01..03；不修复 R-M6-01（审查准备错误属审查方责任，本轮不迁就业务）；不重签为 PASS。

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | 按审查方案深化 r4 已 PARTIAL 的 3 项 P1：D-M6-02 恢复未决严格区分；D-M6-03 两既定 AI 链 + 引用校验；D-M6-04 偏好读回与精确收尾 |
| 审查方工具 | r5_review_probes.py（自建静态控制流探针） | 29/29 PASS |
| D-M6-02 (r5 PARTIAL → DEEPENED) | **本轮 FIXED** | 新增 `pending_recovery` 标志与 `m6_explicit_recover_follow_ups` 显式恢复接口；普通登记 / 失效 / dismiss 在 pending 期间一律拒绝；普通 save 不再以内存非空清恢复状态；登记 / 失效保存结果传到调用方 |
| D-M6-03 (r5 PARTIAL → DEEPENED) | **本轮 FIXED** | 新增 `m6_request_device_history` / `m6_request_phase_meaning` / `m6_validate_reference`；`recordModelMeta` 强制 caller 传 task/project/actor，不依赖 UI/PENDING_DRAFT 派生；消费端做三元组匹配 + 引用校验 + 缺项标"未知" + 人工出口 |
| D-M6-04 (r5 PARTIAL → DEEPENED) | **本轮 FIXED** | `m6_save_prefs` 加写后读回（核对 pinnedBy 一致）；返回 `{state: final|needs_verify|unexecuted, reason, saved, readback}` 三态；togglePin 按 state 三态分支；偏好已落盘但不通过时不盲目回滚；state / receipt 失败可见 |
| R-M6-01 | 不修 | 审查准备错误（seed 路径错放）属审查方；本轮不动业务迁就错误 |
| M0..M5 | FAIL/BLOCKED 沿用 | 仅消费 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN 沿用 | **本轮未启动；不用 --help** |
| 真实 provider | NOT_RUN | 不申请；D-M6-03 链②③仍按需走 model_config.enabled；新增入口复用 M3 适配层；缺绑定自动标 MISSING_BINDING |
| G0-F 后台常驻 | NOT_RUN | 按用户指令 |
| 隔离目录 | `runtime/optimization/2026-10-09/M6/r5/` | 不写 ~/.octosense 或外部 |

---

## 1. 改动文件清单

| 文件 | 净行 | 范围 |
|---|---|---|
| `app/bundle/main.splash` | +404 / -77 | D-M6-02/03/04 深化；不重写；保留 r4 既有差异 |
| `runtime/optimization/2026-10-09/M6/r5/scripts/r5_review_probes.py` | new | r5 静态控制流探针 29/29 PASS |
| `runtime/optimization/2026-10-09/M6/r5/scripts/results/r5_review_probes.json` | new | 探针结果 |
| `runtime/optimization/2026-10-09/M6/r5/CANDIDATE.json` | new | r5 候选清单 |
| `docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r5.md` | new | 本报告 |
| `docs/optimization/2026-10-09-desktop/GATES.json` | edit | M6 字段更新：status=READY_FOR_REVIEW；r5 candidate / evidence_root / modified_files_sha256 / test_counts |

主源 SHA-256：
- r4 后状态：`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2` (7955 行)
- r5 修复后：`9a1a8e274f4cd9b98d1fcdad4ac21d5dd6d391de8b3af30f07192d6c0822af34` (8885 行)

净 +404 行（深化 + 注释），保留 r4 / r3 / r2 / r1 全部差异不撤不改。

---

## 2. 三条 P1 缺陷逐条闭合

### 2.1 D-M6-02 · 提醒恢复未决严格区分（深化）

**审查方案要点**（r5）：仅 D02 路径区分"加载恢复未决"与"正常写待重试"；前者在普通写前一直阻写 / 保留原文及可核备份，显式恢复完成后解除；后者按同记录重试并去重。登记 / 失效保存结果传到现有 UI，不以再 save 或内存非空清恢复状态。

**r5 修复（6 处）**：

A. **`m6_load_follow_ups`**：在 r4 已对"读失败 / 空文件 / schema 异常"置 dirty 的基础上，**新增 `STATE.m6_followups_pending_recovery = true`** 作为"加载恢复未决"标志，与 dirty 共存。普通写路径必须以 pending_recovery 为主要闸，不能仅看 dirty+empty。这样：
- `upsert_dedupe` 把新记录加入内存后 `m6_save_follow_ups` 仍被阻断
- 原文 `.recover`（损坏）+ `.recover.bak`（恢复前最后保险）保留可核
- 正常加载路径末尾 `pending_recovery = false`（仅当 schema 合法）

B. **`m6_save_follow_ups`**：重写首闸——`if pending_recovery == true → return false`。**不再以"内存非空"作为绕过恢复状态的条件**。dirty+empty 二次保护保留作冗余。

C. **新增 `m6_explicit_recover_follow_ups(keep_backup)`** 显式恢复接口：
- `keep_backup=true`：保留原文（复制为 `.recover.bak`），清 pending，**不写新内容**
- `keep_backup=false`：用内存覆盖原文件（先备份为 `.recover.bak`，再走 `m6_save_follow_ups`）
- 返回 `{success, reason, saved}` 让调用方能精确区分"无需恢复 / 保留原文 / 用内存覆盖 / 写盘失败"

D. **`m6_register_follow_up_ex`**：pending_recovery=true 时直接 `return ""`，不调 `upsert_dedupe`，让 confirmAppointment 等调用方拿到 "" 不得把"已登记"告诉用户。

E. **`m6_invalidate_for_task` / `m6_invalidate_for_appointment` / `m6_dismiss_follow_up`**：pending_recovery=true 时同样直接 return 0 / false，不修改内存，不让普通失效操作绕过恢复状态。

F. **`m6_init_forms`** 兜底：`STATE.m6_followups_pending_recovery` 默认 false；与 dirty 共存但语义不同。

**验证（r5_review_probes.py）**：
- d02_load_read_failure_pending：✓
- d02_load_empty_pending：✓
- d02_load_corrupt_pending：✓
- d02_save_pending_blocks：✓
- d02_register_blocks_on_pending：✓
- d02_invalidate_task_blocks_on_pending：✓
- d02_invalidate_appt_blocks_on_pending：✓
- d02_dismiss_blocks_on_pending：✓
- d02_explicit_recover_exists：✓

### 2.2 D-M6-03 · 两既定 AI 链 + 引用校验（深化）

**审查方案要点**（r5）：只补原 D03 两既定链（设备历史 / 事件阶段）；复用已授权 M3 适配 / 来源 / 校验 / 失效契约；发出时固定 task/project/actor/事实版本，不用回包时当前 UI 派生；补设备 / 历史 / 占用及事件依据、引用校验、缺项和人工出口；模型不得直接写业务。

**r5 修复（5 处）**：

A. **新增 `m6_request_device_history(task, references)`**：
- 入口先 `authorizeTask(task)` 闸（身份 / 项目）
- 复用 `_callMinimaxProvider` + `bindRequestVersions` + `recordModelMeta` + `AI_STATE` / `AI_LAST_ERROR`
- `MODEL_CONFIG.enabled == false` → 标 NO_SERVICE 返回 `{success: false, items: []}`，调用方走人工出口
- 成功路径：对 `call.payload.items[]` 做 `m6_validate_reference(it, task)`，不可见 / 跨项目 / 不存在 → 丢弃
- `recordModelMeta` 显式传 `task_id=task.id / project_id=task.project / actor=sessionActor()`（固定，不派生）

B. **新增 `m6_request_phase_meaning(task, event_seq)`**：
- 同上 authorizeTask + 复用 M3 适配层
- 固定 task_version / project_version 上下文（caller 显式传入即可）
- 校验 `call.payload.references[]` 的可见性
- 模型只给阶段字符串建议，不写业务字段

C. **新增 `m6_validate_reference(ref_item, task)`**：
- `ref_type` ∈ {space, asset, task} 分别核 SPACES / ASSETS 可见性 + 同项目
- 不可见 / 跨项目 / 不存在 → return false
- 缺 ref_id / ref_type → return false

D. **修改 `recordModelMeta`**：强制 caller 提供 task_id / project_id / actor；不再从 `PENDING_DRAFT.expected_task_id` / `STATE.selected_task_id` / `STATE.project` / `sessionActor()` 派生。缺失时 `task_id=""` / `project_id=""` / `actor=""` + `_missing=true`，未指定 result_kind 时标 `MISSING_BINDING`，消费端可识别为待核验。

E. **修改 `m6_history_render`**：
- 缺绑定条目（task_id / project_id / actor 任一为空）独立计入 `unknown_count`
- 三元组精确匹配（`task_id == t.id && actor == sessionActor() && project_id == t.project`）才计入 items
- 未绑定条目不再写 provider/model 元信息到 items[]（已闭合）
- note 文本：缺项条目独立显示 + "人工出口：可在阶段说明面板手工编辑"

**验证（r5_review_probes.py）**：
- d03_request_device_history_exists：✓
- d03_request_phase_meaning_exists：✓
- d03_validate_reference_exists：✓
- d03_record_no_ui_derive_task_id / project_id / actor：✓（函数体非注释不含派生调用）
- d03_record_missing_binding_marker：✓（MISSING_BINDING 标记存在）
- d03_history_render_triple_check：✓（三元组匹配 + unknown_count 存在）
- d03_history_render_manual_exit：✓（人工出口文案存在）

### 2.3 D-M6-04 · 偏好读回与精确收尾（深化）

**审查方案要点**（r5）：仅偏好路径捕获固定 actor/action_id/原偏好；写后读回区分已执行 / 未执行 / 未知；精确收尾并核持久结果；state / receipt 失败走可见待核验 / 对账；稳定键保留，所有退出清理保持；已落盘不盲目回滚，未执行可回退；不要吞错误或恢复旧 status 遮掉提示。

**r5 修复（3 处）**：

A. **`m6_save_prefs` 重写为精确收尾**：
- 返回值改为 `{state: "final" | "needs_verify" | "unexecuted", reason, saved, readback}`
- 提前捕获 `_rid` / `_cmd` / `_act`（eager cleanup 前）
- 写后**读回 `tasks.json`**，重新 parse 后核对 `pinnedBy`（按 `_PENDING_RESULT.task_id` 定位任务）是否与内存一致；不一致 → `state="needs_verify"`，reason=`"readback_mismatch:<具体原因>"`
- `_pinnedByEqual(a, b)` 辅助函数逐元素比较（顺序敏感）
- `tasks.json` 写盘失败：`saved=false / state="needs_verify" / reason="tasks_write_failed"`
- `saveState` 抛异常：偏好已落盘（`saved=true`），不盲目回滚，仅 `state="needs_verify" / reason="state_write_failed"`
- `saveReceipts` finalize 失败：`state="needs_verify" / reason="receipt_finalize_failed"`
- `identityActive == false`：返回 `unexecuted`，调用方据此回退内存

B. **`togglePin` 改用三态分支**：
- `state="unexecuted"` → 真未执行，回退 pinnedBy + status
- `state="needs_verify"` → 已落盘但读回 / state / receipt 异常，**不回滚**（已落盘不盲目回滚），仅在 status 标"已落盘但待核验：<reason>"
- `state="final"` → 完整成功，走 logEvent / saveEvents

C. **`_pinnedByEqual`**：长度相等 + 逐元素相等（顺序敏感）。

**验证（r5_review_probes.py）**：
- d04_save_prefs_returns_struct：✓（三种返回结构均存在）
- d04_save_prefs_readback：✓（写后读回逻辑存在）
- d04_save_prefs_no_rollback：✓（"已落盘但不通过"文案存在）
- d04_save_prefs_tasks_needs_verify：✓（tasks_write_failed reason 存在）
- d04_save_prefs_readback_needs_verify：✓（readback_mismatch reason 存在）
- d04_save_prefs_state_needs_verify：✓（state_write_failed reason 存在）
- d04_save_prefs_receipt_needs_verify：✓（receipt_finalize_failed reason 存在）
- d04_pinned_by_equal_exists：✓
- d04_toggle_pin_three_states：✓

---

## 3. 验证结果汇总

| 脚本 | 结果 |
|---|---|
| `M6/r5/scripts/r5_review_probes.py`（本轮 r5 静态控制流探针） | **29/29 PASS** |
| `M6/r1/scripts/m6_favorites_isolation.py` | 5/5 PASS（沿用 r1） |
| `M6/r1/scripts/m6_search_real.py` | 6/6 PASS |
| `M6/r1/scripts/m6_history_phase.py` | 14/14 PASS |
| `M6/r1/scripts/m6_followup_dedupe.py` | 7/7 PASS |
| `M6/r1/scripts/m6_jump_summary.py` | 13/13 PASS |
| `M6/r1/scripts/m6_status_unified.py` | 15/15 PASS |
| `M6/r1/scripts/m6_unsaved_keyboard.py` | 11/11 PASS |
| `M6/r1/scripts/m6_viewport_source.py` | 20/20 PASS |
| `M6/r1/scripts/m6_whitebox_three_role.py` | 16/18 PASS（r1 既知 2 失败） |
| `M6/r1/scripts/m6_m5_compat_audit.py` | 59/59 PASS |

**r5 自身修复点检 29/29 PASS**（自建 r5 静态控制流探针）。

---

## 4. 故意不引入（与 r4 一致 + 修复轮刻意不扩散）

- 不修 M5/M4/M3/M2/M0 任何未闭合缺陷
- 不引入 SQLite / Python 后端 / AppHub publish / 公网部署 / 真实 provider 配置 / 真实业务身份
- 不为演示改系统时间或手工改 task.status / version / receipt / pin / search / history
- 不启动 launcher、不用 `--help`、不用真背景定时
- 不修 A-M6-01..03 挂账建议
- 不修 R-M6-01 审查准备错误（属审查方；本轮不迁就业务）
- 不 reset/stash/删除他人改动；不发散到 M7
- 不重写 M2/M4/M5 任何已有函数体；只最小新增 + 修正既有 m6_* 行为
- 不自行配置真实 model provider；新增入口按 `MODEL_CONFIG.enabled` 走，未激活时走 NO_SERVICE 路径
- 不为 D-M6-03 链②③硬接入 provider；新增入口复用 M3 适配层；provider 未激活时 NO_SERVICE 退场

---

## 5. 候选清单与交接

- candidate_id = `M6-r5-worktree`；base_candidate_id = `M6-r4-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M6/r5/CANDIDATE.json`
- 主源 SHA-256：`9a1a8e274f4cd9b98d1fcdad4ac21d5dd6d391de8b3af30f07192d6c0822af34`
- GATES.json：M6 status 仅更新为 `READY_FOR_REVIEW`；r5 review 字段新建；r4..r1 历史保留
- ACCEPTANCE.json：不修改
- 末尾两行 `STATUS=<当前 status> NEEDS_ABRAM=<yes|no>`：M6 r5 不申请任何 → `STATUS=READY_FOR_REVIEW` `NEEDS_ABRAM=no`

---

## 6. 阻断与边界如实标记

- 桌面 launcher = BLOCKED 沿用（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；本轮与 r4..r1 一致未启动。
- 真实模型 provider = NOT_RUN 沿用；本轮 D-M6-03 新增入口按 `MODEL_CONFIG.enabled` 走，未激活走 NO_SERVICE 退场，不偷偷启用 provider。
- 后台常驻 = NOT_RUN 沿用 G0-F，按用户指令"不能称后台常驻"。
- 业务身份来源 = 沿用 M2 挂账；D-M6-02 闸只核当前可见授权。
- 真实桌面截图 / 演示草片 = NOT_RUN 沿用 M0..M5；不伪造。
- 键盘焦点 / 视口 / 150% 放大 / 长中文 = NOT_RUN 沿用 r1；非本轮要求。
- D-M6-02 / D-M6-04 静态点检 100% PASS；D-M6-03 来源隔离 / 无历史 / 三元组匹配 / 引用校验 / 人工出口静态点检 PASS，真实链②③仍 NOT_RUN。

**下一模块：不允许；未执行；不给 M7 入口。**

---

## 7. 受前序模块挂账影响

- M0..M2 沿用既有挂账条目，不修。
- M5 r6 FAIL：D-M5-01..05 未闭合；M6 仅消费既有 attach 契约，未触及 M5 任何业务。
- M6 r5 审查 R-M6-01：审查准备错误属审查方；本轮不迁就业务，未修。
- 累计快照（c683c7a0...）审查报告中所列 main SHA-256；本轮 SHA-256 在 r4 之上变化到 `9a1a8e27...`，对应累计工作区。

