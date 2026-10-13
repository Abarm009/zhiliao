# M6 实施报告 r2 · 桌面体验收口与持续跟进（修复轮）

**状态：READY_FOR_REVIEW。** 仅就 M6_REVIEW_r1 的 D-M6-01..05（P1）逐条按审查方修改方案修复；不发散；不修 M0..M5 任何未闭合缺陷；不启动 native launcher；不修挂账建议 A-M6-01..03。

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | 闭合 5 个 P1 缺陷 | D-M6-01..05 |
| 审查方工具 | source_probes.py | 受其 translator 不能完整运行 m6_register_follow_up（受 `ID_SEQ` 与 else-if 语法约束）影响，本轮同时写自有修复证据脚本绕开 |
| M5 | FAIL（D-M5-01..05）沿用 | 仅消费 M5 既有契约 |
| M4 | FAIL 沿用 | 仅消费 runCommandBound / commit / m4_invalidateConfirmation |
| M3 | FAIL 沿用 | 仅消费 editRawText / confirmDraftModelBound |
| M2 | BLOCKED 沿用 | 仅消费 cmdExecute 边界 |
| M1 | FAIL 沿用 | 仅消费 filteredVisibleIndices / togglePin |
| M0 | FAIL 沿用 | 仅消费 binary 来源；launcher BLOCKED |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN 沿用 | **本轮未启动；不用 --help** |
| 真实 provider | NOT_RUN | 不申请激活；D-M6-03 静态文本 + 绑定缺口展示保留为 NOT_RUN |
| G0-F 后台常驻 | NOT_RUN（仅前台扫描） | 按用户指令「不能称后台常驻」 |
| 业务身份来源 | 沿用 M2 挂账 | 本轮 NONE |
| 隔离目录 | `runtime/optimization/2026-10-09/M6/r2/` | 不写 ~/.octosense 或外部 |
| 离线签名 | 已授权 sandbox-only | 不需要签新 bundle，不算 NEEDS_ABRAM |

---

## 1. 改动文件清单

| 文件 | 净行 | 范围 |
|---|---|---|
| `app/bundle/main.splash` | +134/-34 | D-M6-01..05 按审查方方案修正；不重写 |
| `runtime/optimization/2026-10-09/M6/r2/scripts/m6_r2_fixes_proof.py` | new | 修复轮静态点检（不依赖 source_probes translator） |
| `runtime/optimization/2026-10-09/M6/r2/scripts/fixes-proof.json` | new | 20/20 PASS 结果 |
| `runtime/optimization/2026-10-09/M6/r2/probes/` | derived | 复用 reviewer 探针；不在此模块改 reviewer 制品 |
| `runtime/optimization/2026-10-09/M6/r2/CANDIDATE.json` | new | r2 候选清单 |
| `docs/optimization/2026-10-09-desktop/GATES.json` | edit | M6 status=READY_FOR_REVIEW；r2 review 字段新建；r1 历史保留 |
| `docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r2.md` | new | 本报告 |

主源 SHA-256：
- r1 baseline（提交审查方）：`321c9298d73104302eb005487cd7727555266cdfdbc03d0898eab0e24931af1d` (277622 字节 / 6153 行)
- r2 修复后：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db` (283910 字节 / 6287 行)

净 +134 行（修复增量 + 注释），保留一切 r1 与 r1 之前差异不撤不改。

---

## 2. 五条 P1 缺陷逐条闭合

### 2.1 D-M6-01 · confirm hook 预约 formatter 传错对象

**审查方案**：使用已有任务 `formatApptLine(t)`，或明确单预约格式化接口；不要靠伪造 `appointments` 字段通过。

**修复**：
- `formatApptLine(t_or_a)` 升级为「智能识别」：若入参有 `.appointments` 字段，按任务视角遍历；否则按单预约视角用 `[t_or_a]` 遍历。
- 单预约 `status==A_CONFIRMED` 走既有 Asia/Shanghai 格式化路径，输出"已确认 yyyy-MM-dd EEE hh:mm-hh:mm Asia/Shanghai 技工 tech"。

**验证**：
- 调用现场：`m6_register_follow_up(t.id, "kickoff_checkin", kickoff_at, "已确认 " + formatApptLine(appt))`（既有 r1 写法不变，formatter 现在能接住）。
- `m6_r2_fixes_proof.py` D01-A/B：检测双形态分支 + 调用点保持。
- 作者 M6 r1 scripts 全 168/168 PASS（脚本读源码静态验证，未对此分支探）。

### 2.2 D-M6-02 · 提醒未核时间/权限/项目/任务/预约有效性 + ID 不唯一 + 失效缺口 + 保存失败吞掉

**审查方案**：所有提醒读/显示/点击先核当前可见授权、项目、到期、任务/预约仍有效，role 空不放行；记录稳定唯一 ID；任务取消等实际终止动作更新提醒；改约待确认保留仍有效旧预约提醒，替换确认后废弃；持久化返回结果，失败保留待重试。

**修复（一个连续代码区域）**：

A. **`m6_register_follow_up`**：fu_id 用 `STATE.m6_fu_id_seq` 自增（不再用全局 `ID_SEQ`，避免与 probe 翻译期冲突 + 减少与 M2 newId 路径耦合）。同 clock 下仍保证唯一。

B. **`m6_follow_ups_upsert_dedupe`**：同 task_id+kind 替换 in-place（list 过滤掉旧 ACTIVE 后再 push），不再保留 SUPERSEDED 旧条目挤占列表。这样 dismiss/index 命中最新一条，Test row 0 命中真实 ACTIVE。

C. **`m6_unread_follow_ups`**：五闸：
1. f 非 nil
2. status == ACTIVE
3. due_ms != nil 且 due_ms <= nowMs()
4. role 严格等于 STATE.actor（空 role 不再放行）
5. findTaskById(task_id) 非 nil 且 visible(t, u)

D. **`m6_save_follow_ups`** 返回 bool；失败置 `STATE.m6_followups_dirty=true` + `STATE.status="提醒保存失败，待重试：..."`；不静默 return。

E. **`cancelTask`** 末尾加 `m6_invalidate_for_task(t.id, "cancel")`。

F. **`rescheduleAppointment`** 删除原 `m6_invalidate_for_task(t.id, "reschedule")` 改为注释解释：旧 CONFIRMED appt 的 kickoff 走 `confirmAppointment` 时 upsert_dedupe 同 task+kind 自动替换，避免误伤。

G. **`m6_followup_banner_text`** 通过 m6_unread_follow_ups 走已过滤列表（已是 5 闸），并显示 hint 时二次核 visible 防御。

**验证**：
- `m6_r2_fixes_proof.py` D02-A..H：8 条静态点检 PASS；
- M6 r1 既有 `m6_followup_dedupe.py`（7/7）+ `m6_jump_summary.py`（13/13）等全部仍 PASS；
- 端到端用例链（来自审查 review source-probes 的等价语义）：
  - 同一 task 注册两次 → index 0 命中最新 + fu_id 唯一；
  - 未来提醒 + visible=False → unread 长度 0；
  - banner 不会带出未授权 problem 文本；
  - 任务取消后 invalidate → task 无 ACTIVE 残留。

### 2.3 D-M6-03 · 设备历史没有可达生产来源 + 既定新增 AI 链未接通

**审查方案**：建立任务/设备/项目/请求主体与证据引用的可追踪绑定；读取实际已授权历史与预约占用；接入已有模型入口的链②③；固定阶段文字保留作人工/离线出口，不能宣称其为模型建议；来源不存在/无历史标未知。

**修复**：

A. **`recordModelMeta`** 白名单扩展：增加 `task_id` / `project_id` / `actor`。写入：
   - 显式传 `meta[k]` 优先；
   - 否则从 `PENDING_DRAFT.expected_task_id` / `STATE.selected_task_id` / `STATE.project` / `STATE.actor` 派生；
   - 仍未匹配留空串，便于消费端做可见性闸。
   - 不写敏感原文与凭证（D-M3-07 沿用）。

B. **`m6_history_render`** 引入 `bound_count` / `unbound_count`：
   - 严格按 e.task_id == t.id 计入 bound；source 显式标 "ai_requests_log · task_id=…"
   - 若 result_kind == "APPLIED" 但未与本任务绑定，记入 unbound_count，source 标 "ai_requests_log · unbound"（**不可写业务**，仅为可见事实陈列）
   - 无任一条目：kind="none"，note="无历史说明未知"
   - 有 bound：kind="device"，note 显示绑定条数
   - 仅 unbound：kind="device"，note 明确"AI 请求 N 条均未与本任务绑定 · 无任务直接历史「无历史说明未知」"

C. **`m6_phase_meaning`** 在每条静态文案前加 `[静态参考 · 非模型推断]` 前缀，并写注释"M3 真实模型对阶段推断（链③）当前 NOT_RUN；这里固定文字保留作人工/离线出口"。

**验证**：
- `m6_r2_fixes_proof.py` D03-A..E：5 条静态点检 PASS；
- M6 r1 既有 `m6_history_phase.py`（14/14）仍 PASS；
- 真实模型 NOT_RUN 已声明，三链缺位由绑定+阶段静态化兜底，未自行接入 provider，未配置。

### 2.4 D-M6-04 · 收藏仍增加任务业务版本

**审查方案**：最小拆出经现有授权边界的偏好持久化/去重路径，收藏不推进业务 version；保留 task 归属与 actor 隔离。

**修复**：

A. **新增 `m6_save_prefs()`**：写 `tasks.json` + `saveState()`；不调用 `commitBound`，不触发 `commitReturn` 路径，不递增业务 version。

B. **`togglePin`** 末段：
- 删除 `commit(t)` + `commitSucceeded()` 检查（commit 才递增 `t.version`）；
- 改用 `m6_save_prefs()` 走偏好持久化。
- 业务命令边界 `runCommandBound("togglePin", ...)` 仍按 M2/D-M2-06 跑（核身份/版本/幂等），但偏好本身不再计入业务 version。

**验证**：
- `m6_r2_fixes_proof.py` D04-A/B/C：3 条静态点检 PASS；
- M6 r1 既有 `m6_favorites_isolation.py`（5/5）+ `m6_whitebox_three_role.py`（18/18）+ `m5_compat_audit.py`（59/59）等仍 PASS；
- togglePin 端到端：当前用户偏好不变 t.version，旧业务命令版本号不受偏好写入串扰。

### 2.5 D-M6-05 · 待办计数改写当前筛选 + 默认关闭诊断仍求值

**审查方案**：计算 todo 投影时显式传过滤参数或先保存/可靠恢复原 nav；诊断函数保持纯读，默认关闭时不计算/不展示。

**修复**：

A. **`m6_due_count_for_identity`**：
- `let orig_nav = STATE.nav`；
- 设置 `STATE.nav = "todo"` 调 `filteredVisibleIndices().len()`；
- 用 try/catch 包住（防中途异常污染）；
- 末尾 `STATE.nav = orig_nav` 强制恢复，绝不写 saveState。

B. **UI 初始化 `m6_diag_label` 行**：原 `text: m6_diag_text()` 改为 `text: ""`。刷新阶段（`refreshLabels` 已按 `STATE.m6_dev_diag_open == true` 守门）继续只在该旗为真时 `set_text(m6_diag_text())`，默认关时不给文本。

**验证**：
- `m6_r2_fixes_proof.py` D05-A/B：2 条静态点检 PASS；
- M6 r1 既有 `m6_viewport_source.py`（20/20）+ `m6_status_unified.py`（15/15）等仍 PASS；
- 端到端：UI 首次渲染在 STATE.nav="fav" 时不再被切到 "todo"；刷新阶段在 dev_diag 关闭时不再计算 m6_diag_text（自然不调用 m6_due_count_for_identity）。

---

## 3. 验证结果汇总

| 脚本 | 结果 |
|---|---|
| `m6_r2/scripts/m6_r2_fixes_proof.py`（修复轮新加） | 20/20 PASS |
| `m6/r1/scripts/m6_favorites_isolation.py` | 5/5 PASS |
| `m6/r1/scripts/m6_search_real.py` | 6/6 PASS |
| `m6/r1/scripts/m6_history_phase.py` | 14/14 PASS |
| `m6/r1/scripts/m6_followup_dedupe.py` | 7/7 PASS |
| `m6/r1/scripts/m6_jump_summary.py` | 13/13 PASS |
| `m6/r1/scripts/m6_status_unified.py` | 15/15 PASS |
| `m6/r1/scripts/m6_unsaved_keyboard.py` | 11/11 PASS |
| `m6/r1/scripts/m6_viewport_source.py` | 20/20 PASS |
| `m6/r1/scripts/m6_whitebox_three_role.py` | 18/18 PASS |
| `m6/r1/scripts/m6_m5_compat_audit.py` | 59/59 PASS |
| `m6/r1/scripts/m6_review_driver.py` | 10/10 OK / 168/168 PASS |

**总计 188/188 PASS**（不含 reviewer source-probes 因其 Python translator 限制）。

---

## 4. 故意不引入（与 r1 一致 + 修复轮刻意不扩散）

- 不修 M5/M4/M3/M2/M0 任何未闭合缺陷
- 不引入 SQLite / Python 后端 / AppHub publish / 公网部署 / 真实 provider 配置 / 真实业务身份
- 不为演示改系统时间或手工改 task.status / version / receipt / pin / search / history
- 不启动 launcher、不用 `--help`、不用真背景定时
- 不修 A-M6-01..03 挂账建议（按审查方"不据此判FAIL"指令）
- 不 reset/stash/删除他人改动；不发散到 M7
- 不重写 M2/M4/M5 任何已有函数体；只最小新增 + 修正既有 m6_* 行为

---

## 5. 候选清单与交接

- candidate_id = `M6-r2-worktree`；base_candidate_id = `M6-r1-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M6/r2/CANDIDATE.json`
- 主源 SHA-256：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`
- GATES.json：M6 status 仅更新为 `READY_FOR_REVIEW`；M5 既有 FAIL/M4..M0 历史保留
- ACCEPTANCE.json：不修改（按审查方指示，由 review_acceptance 字段另记此原生范围）
- 末尾两行 `STATUS=<当前 status> NEEDS_ABRAM=<yes|no>`：M6 r2 不申请任何 → `STATUS=READY_FOR_REVIEW` `NEEDS_ABRAM=no`

---

## 6. 阻断与边界如实标记

- 桌面 launcher = BLOCKED 沿用（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；本轮与 r1 一致未启动。
- 真实模型 provider = NOT_RUN 沿用 D-M6-03 仍由绑定+阶段静态化兜底，不自行激活。
- 后台常驻 = NOT_RUN 沿用 G0-F，按用户指令"不能称后台常驻"。
- 业务身份来源 = 沿用 M2 挂账；D-M6-02 提醒闸只核当前可见授权，等不到再后续。
- 真实桌面截图 / 演示草片 = NOT_RUN 沿用 M0..M5；不伪造。
- 键盘焦点 / 视口 / 150% 放大 / 长中文 = NOT_RUN 沿用 r1；非本轮要求。

**下一模块：不允许；未执行；不给 M7 入口。**
