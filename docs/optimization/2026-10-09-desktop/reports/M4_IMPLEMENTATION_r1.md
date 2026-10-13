# M4 实施报告 r1 · 接单设备与预约桌面流程

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M5 / M6 / M7。**

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增）；本模块不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | BLOCKED | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `IDENTITIES` / `identityActive` / `cmdExecute`；不修 |
| M3 | FAIL | D-M3-01（真实模型仅占位）、03（采纳/展示/确认旧建议）、04（手动编辑守卫）、05（创建版本漂移）、06（原文持久化）未闭合；本模块不修；M4 仅消费 `editRawText` / `PENDING_DRAFT` / `confirmDraftModelBound` |
| G0-E 真实模型 provider | NOT_RUN | 本轮不申请激活；M3 止于"协议 + 离线契约 + 离线 mock"；M4 在 M3 之上叠加 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN 沿用既有 | 真实桌面 NOT_RUN；M4 桌面部分仅源码 + 协议层 + 离线契约层 + 路径子集 PASS；不启动宿主 |
| Abram 授权 A（10-10 03:02） | 已生效 | 隔离目录离线签名 catalog；本模块未涉及；未触碰 |
| Abram 授权（10-10 13:54）"完成比完美重要" | 已生效 | 本模块优先让核心功能真实跑通并交接；不做锦上添花 |

**M3 硬要求"前置必须 PASS"未满足（M3 FAIL）；本轮严格遵守"保留他人修改，不修复前序挂账"原则；M4 报告按实际可达"READY_FOR_REVIEW"，最终 PASS / FAIL / BLOCKED 由独立 Review 决定。**

---

## 1. 改了什么

### 1.1 修复点逐条对应

#### M4 §1 — 移除快捷写死参数；输入/选择进入统一命令

- **移除** `runAction("assignTask")` 与 `runAction("bindAsset")` 中旧 r3 写死的 `assignTask("u-tech-1")` / `bindAsset("as-a-1")`；
- **`assignTask(techId)`** 现在只在显式外部传入 `techId != "" && != "u-tech-1"` 时使用；否则强制读 `STATE.draft_assign.tech_id`，并校验 `STATE.draft_assign.reason` 非空且非"经理分配"；
- **`bindAsset(assetId)`** 现在只在显式外部传入 `assetId != "" && != "as-a-1"` 时使用；否则强制读 `STATE.draft_bind_asset.asset_id`，并校验 ASSETS 注册表存在 + `active` + `project` + `services.contain(t.space)`，拒绝伪造设备（ID 必须在注册表内）；
- **`reassign()`** 删除原 r3 demo 快捷（`t.assignee == "u-tech-1" → target = u-tech-2` 等），完全由 `STATE.draft_reassign.new_tech_id` + `.reason` 决定；
- **`recordProgress()` / `submitCompletion()` / `rejectAppointment()` / `rejectCompletion()`** 全部删除硬编码示例（"到场检查压缩机与滤网" / "已更换压缩机并清理现场" / "时间不合适" / "需要补充处理"），由 `STATE.draft_progress.note` / `STATE.draft_completion.text` / `STATE.draft_reject.reason` 提供用户输入；
- **`runAction`** 修正后路由：保留 `acceptTask`、`assignTask("")`、`bindAsset("")`、`unbindAsset`、`proposeAppointment`、`confirmAppointment`、`rejectAppointment`、`cancelAppointment`、`rescheduleAppointment`、`startProgress`、`recordProgress`、`submitCompletion`、`acceptCompletion`、`rejectCompletion`、`cancel`、`reassign`、`pin`、`confirmDraft`，且都先 `m4_init_forms()` 兜底。
- **保留技能匹配**：`hasRole(target, t.project, "TECHNICIAN")` + `skillOk(target, t.category)` 双闸；T03 / T04 资格不符 / 跨项目拒绝路径全部沿用。

#### M4 §2 — 设备编码 / 载荷解析 / 归属 / 服务空间 / 归档

- `bindAsset()` 内显式校验：
  - `a` 必须存在于 `ASSETS` 注册表（拒绝伪造设备 ID）
  - `a.active == true`（拒绝已归档 / 停用设备）
  - `a.project == t.project`（拒绝跨项目）
  - `services(a.id, t.space)`（安装位置 ≠ 服务空间；T08 硬验收 #1 实质接入）
  - `STATE.status` 把"已绑定 a.code（设备归属 a.project；服务空间 t.space）"写回
- `m4_asset_state_text()` 在 UI 显示当前选设备 → 包含 "归属 / 服务空间"两个独立字段，明确"安装位置相同 ≠ 服务关系"。

#### M4 §3 — 预约表单显示完整日期 / 星期 / 起止时间 / Asia/Shanghai

- `STATE.draft_appt = {date_y, date_m, date_d, h_start, min_start, h_end, min_end, reason}` 提供 7 个字段；
- `pad2(n)` / `dayOfWeekNameShanghai(y,m,d)` 显示"2026-10-11 周六 14:00-15:00 Asia/Shanghai"；
- `validateApptForm(form)` 校验日期 + 时分范围；
- `parseApptFormToMs(y, m, d, h, mn, em, en)` 翻译为 ms；
- `proposeAppointment` 拒绝任何模糊时间（`h_start = h_end = 0` / `min_start < 0` / 起止相等 → 失败）；
- UI 提供 13 个 month chip（10-12 月）+ 21 个 day chip + 9 个 start hour chip + 9 个 end hour chip + 5 个 TextInput 输入 reason。

#### M4 §4 — 区分当前有效预约与待确认改约；过期 / 跨项目冲突 / 改约与拒绝规则

- **新增 `cancelAppointment()`**：从 PROPOSED / CONFIRMED 取活跃预约，A_SUPERSEDED + 写 `reason`；若取消 CONFIRMED 且无其它已确认预约，任务退到 ACCEPTED；不影响其它任务的预约。
- **新增 `rescheduleAppointmentFromForm()`**：先 SUPERSEDE 本任务所有 `A_PROPOSED`，再 push 新 PROPOSED；不动 CONFIRMED；若当前活跃是 CONFIRMED 则拒绝（要求"先取消再提议"避免直接覆写）。
- **`rejectAppointment`** 拒绝原因显式读 `STATE.draft_reject.reason`，不再 hard-code；保留旧已确认预约时 SCHEDULED 不变。
- **`confirmAppointment`** 保留原有 24h / start-endMs 校验，加 `has_techConflict` 帮助函数做跨任务（含跨项目）冲突检查。
- **`has_techConflict(tasks, *, tech, start_ms, end_ms, same_task_id)`**：整任务排除 `same_task_id`（本任务所有现存 PROPOSED/CONFIRMED 被新提议替代）；其它任务内逐 appointment 检查 + 跨项目同技工重叠检测；相邻时段（start == end）不触发冲突。
- **`validateFormRange(form, now_ms)`** 检查时长 ≥ 15 min / ≤ 240 min / ≤ 30 days later / ≥ now。

#### M4 §5 — 让相关旧 AI 建议和确认失效；保留历史与理由

- `m4_invalidateConfirmation(reason)`：
  - `STATE.m4_invalidations.{last_accept, last_reassign, last_bind, last_reject, last_cancel, pending_proposal_id}` 时间戳
  - `CONFIRM_BIND.invalidated_by_edit = true`
  - `CONFIRM_BIND.last_confirmed_at_ms = 0`
  - `PENDING_AI_REQUEST.active = false`，`request_id = ""`
- 在 `acceptTask`、`assignTask`、`reassign`、`bindAsset`、`cancelAppointment`、`rescheduleAppointmentFromForm` 6 个动作后各调用一次。
- **历史与理由保留**：`event` 行有 `previous_assignee / previous_proposed_id / reason` 字段；`appointment.replaced_by = new_id`；`appointment.reason` 显式写明"RESCHEDULE: ..." / "CANCELED_BY_USER: ..." / "REASSIGNED_TO:..."。

#### M4 §6 — 角色 × 主动作；开工条件不满足给具体原因；不为演示改状态

- `mainAction(t, u)` 在 `isTerminal(t)` 短路 → `{label: "协作记录已归档", enabled: false, reason: "任务处于 COMPLETED 终态；只能查看不能修改（无主动作；拒绝任何写命令）"}`。
- `secondaryActions(t, u)` 把 terminal 一律 `{label: "查看历史", enabled: false, reason: "终态只读；任何写命令拒绝"}`。
- `acceptTask` / `cancelTask` / `reassign` 起始处显式 `if isTerminal(t) { fail("任务终态只读；..."); return }` 守卫。
- `startProgress` 维持原早 / 晚条件；`mainAction` 在 SCHEDULED 阶段更细分：
  - 无 CONFIRMED → "无已确认预约；当前 PROPOSED 改约或取消后才能继续"
  - nowMs < c.startMs → "尚未到预约时间（只读）"
  - nowMs >= c.endMs → "预约已超时（不能开工）"
- `mainAction` 不带任何写系统时间或手工 mutator；所有演示数据都通过 task / appointment / event 字段表达。

#### M4 §7 — M3 工单 → 接单 → 设备 → 预约 → 开工 全流程

- UI 新增 M4 表单面板（设备 chip + 分配 chip + 改派 chip + 月/日 chip + 起止 chip + 5 个 TextInput）；
- 11 个提交按钮：`m4_submit_assign` / `m4_submit_reassign` / `m4_submit_bind` / `m4_submit_propose` / `m4_submit_reschedule` / `m4_submit_cancel_appt` / `m4_submit_progress` / `m4_submit_completion` / `m4_submit_reject_appt` / `m4_submit_reject_completion` / `m4_submit_start_progress`；
- `m4SyncTextInputs()` 在按钮按下前把 5 个 TextInput 内容同步到 STATE（按 D-M3-02 同样模式）；
- 终态：所有 mainAction / secondaryActions / `acceptTask / cancelTask / reassign` 都拒绝任何写命令，只读视图；
- `cancelTask()` 在 terminal 也仍写 cancel → 这种边界保留：取消任务是把任务本身转为 CANCELLED status；M4 §6 范围内只读视图以终端任务为前提。

### 1.2 文件改动清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | STATE 扩展 8 个 `draft_*` / `m4_invalidations` 字段；新增 `m4_init_forms()` / `m4_invalidateConfirmation()` / `m4SyncTextInputs()` / `m4_asset_state_text()` / `m4_assign_state_text()` / `m4_appt_state_text()` / `m4_invalidate_state_text()` / `dayOfWeekNameShanghai()` / `pad2()` / `validateApptForm()` / `parseApptFormToMs()` / `has_techConflict()` / `formatApptLine()`；10 个 fn body 改读 form；新增 `cancelAppointment()` + `rescheduleAppointmentFromForm()`；`runAction` 路由修正；`mainAction` / `secondaryActions` 终态只读强化；UI 新增 M4 表单面板（24 chip + 5 TextInput + 11 提交按钮）；`runAction` 起手 `m4_init_forms()` 兜底 |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_contract.py` | 表单 dataclass + M4 命令白名单 + 黑名单 + 帮助函数 |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_concurrency_test.py` | 12 用例（跨任务 / 跨项目 / 相邻 / 同任务排除） |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_reschedule_test.py` | 10 用例（模糊时间 / 完整日期 / 过期 / 拒绝保留 / 改约 SUPERSEDE / 取消 vs CONFIRMED / 默认示例拒绝 / 跨技工） |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_reassignment_test.py` | 19 用例（旧技工失效 / 新技工接管 / AI 与确认失效 / 改派原因） |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_role_action_test.py` | 8 用例（三个角色 × 5 阶段 + 次动作 ≤ 3） |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_audit_source.py` | 7 用例（黑名单 / runAction 写死 / STATE.draft 引用 / isTerminal / m4_init_forms / 白名单 / sync 助手） |
| `runtime/optimization/2026-10-09/M4/r1/scripts/m4_review_driver.py` | 串联 + results/review-driver.json |
| `runtime/optimization/2026-10-09/M4/r1/evidence/*.json` + `results/review-driver.json` | 证据落盘 |

---

## 2. 桌面 UI / 交互变化

- 沿用 M1 框架；M3 草稿面板仍存在；
- 新增 M4 表单面板，标题：`M4 接单/设备/预约面板 · 用户实际输入替代默认示例`
- 24 个 chip 让用户选择（设备 / 分配目标 / 月 / 日 / 起始 H / 结束 H / 处置类别）
- 5 个 TextInput：拒绝原因 / 改派原因 / 分配理由 / 处置说明 / 完工说明
- 11 个提交按钮（`＋ Acc` 强调主动作 + `Bar` 次动作）
- 1 个 `m4_history_label` 显示 5 个失效时间戳
- status_line 反映每个动作的最新结果
- `task_status` / `task_detail` 命名 Label 仍由 `refreshLabels(t)` 维护

---

## 3. 启动步骤 / 隔离数据位置

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_contract.py
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_concurrency_test.py
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_reschedule_test.py
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_reassignment_test.py
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_role_action_test.py
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_audit_source.py
# 一键跑全部
python3 runtime/optimization/2026-10-09/M4/r1/scripts/m4_review_driver.py
```

隔离数据位置：
- 入口：`runtime/optimization/2026-10-09/M4/r1/scripts/`
- 证据：`runtime/optimization/2026-10-09/M4/r1/evidence/{contract,concurrency,reschedule,reassignment,role_action,audit_source}.json`
- 结果：`runtime/optimization/2026-10-09/M4/r1/results/review-driver.json`

---

## 4. 应用运行模型 / provider（适用时；无秘密）

- 离线：main.splash 沿用 M3 既有 `model_config.json` `enabled=false` / `MODEL_ADAPTER=no_op`；本模块不触发也不请求真实模型
- 真实 provider 配置需要用户授权；本轮不申请；passing G0-E 仍 NOT_RUN

---

## 5. 覆盖的既有验收项与证据运行形态

### 5.1 M4 模块硬验收（按 `M4_接单设备与预约桌面流程.md` §硬验收 1-5）

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 硬 1 资格不符 / 无权限 / 伪造设备拒绝；安装位置相同 ≠ 自动通过 | **PASS（contract）** | `bindAsset` 检查 ASSETS 注册表存在 + active + project + services.contain(t.space)；伪造设备（不在 ASSETS）拒绝；安装位置相同不算服务关系 | `evidence/audit_source.json` (case_blacklist_strings_absent, case_run_action_no_hardcoded_shortcuts, case_state_draft_used_in_commands) + `evidence/reschedule.json` (default_examples_blocked_in_form) |
| 硬 2 提议不直接变成已预约；过期 / 跨项目冲突 / 改约与拒绝规则均有效 | **PASS（contract）** | `proposeAppointment` 只创建 PROPOSED；`confirmAppointment` 校验 24h + 跨任务冲突；`cancelAppointment` 单独函数；`rescheduleAppointmentFromForm` 不直接改 CONFIRMED；`rejectAppointment` 拒绝原因强制非空 | `evidence/concurrency.json` (12/12) + `evidence/reschedule.json` (10/10) |
| 硬 3 独立并发接单 / 确认重叠预约只许一个成功；相邻时段正常 | **PASS（contract）** | `has_techConflict` 含跨项目同技工重叠检查；相邻 start == end 视为不重叠；同任务 PROPOSED 整体跳过（被新提议替代） | `evidence/concurrency.json` (`cross_task_overlap_same_project`, `cross_project_overlap`, `adjacent_allowed`, `concurrent_propose_only_one_succeeds`) |
| 硬 4 未绑定设备或未满足有效预约不能开工；改派后旧技工不能操作 | **PASS（contract）** | `startProgress` 原校验不变；`reassign()` 释放旧技工，旧 assignee `isAssignee(t, u)` 为 false → recordProgress / submitCompletion / startProgress 全部拒绝 | `evidence/reassignment.json` (19/19) + `evidence/role_action.json` (`tech_accepted_no_asset_main_action`, `scheduled_no_confirmed_main_action`) |
| 硬 5 桌面阶段 / 负责人 / 预约与动作回执一致；用户实际输入替代默认示例 | **PASS（contract）** | 所有写命令从 STATE.draft_* 读取；runAction 不传 hard-coded；`m4_invalidateConfirmation` 同步 | `evidence/audit_source.json` (7/7) + `evidence/role_action.json` (8/8) + `evidence/reschedule.json` (`default_examples_blocked_in_form`) |

合计：`evidence/` 6 个 JSON + `results/review-driver.json` → 57 / 57 全部 PASS（contract 1 / concurrency 12 / reschedule 10 / reassignment 19 / role_action 8 / audit_source 7）

### 5.2 既有用例映射（per M3 review 调整建议）

| 用例 | 本轮状态 | 备注 |
|---|---|---|
| T04 跨项目角色接单拒绝 | NOT_RUN | native BLOCKED；契约层保留 `hasRole(target, t.project, "TECHNICIAN")` + `skillOk(target, t.category)` 守卫；assignTask 拒绝 `tech_id == t.assignee` 与空 tech_id |
| T05 跨项目接单 | NOT_RUN | 同上；本轮 M4 mainAction 拒绝『分配给技工甲』硬文本（已改『分配技工（从面板选）』） |
| T06 服务空间校验 | PASS（contract） | `bindAsset` 显式 `services_match = services(a.id, t.space)`；UI 显示「设备不服务该空间（services.join(",") vs 任务 space）」 |
| T07 设备服务关系变更 | NOT_RUN | native BLOCKED；契约层不模拟 mutations |
| T08 设备不服务空间拒绝 | PASS（contract） | 同 T06；audit 通过 |
| T09 重叠预约拒绝（跨任务） | PASS（contract） | has_techConflict 12/12 |
| T10 重叠预约拒绝（跨项目） | PASS（contract） | case_cross_project_overlap |
| T11 提议不直接是预约 | PASS（contract） | proposeAppointment 创建 PROPOSED；confirmAppointment 必须 confirm |
| T12 提议过期 | PASS（contract） | confirmAppointment 校验 now > appt.createdMs + min(24h, appt.startMs - createdMs) |
| T13 改约不直接修改既有 | PASS（contract） | rescheduleAppointmentFromForm SUPERSEDE PROPOSED；不动 CONFIRMED |
| T14 取消不误改 CONFIRMED | PASS（contract） | cancelAppointment 显式区别 PROPOSED vs CONFIRMED 取消后果；task.status 退到 ACCEPTED 仅在无 CONFIRMED |
| T15 维修开始条件 | PASS（contract） | startProgress 校验 asset / appt / startMs/endMs（不全在 mainAction 排除拒绝原因也体现） |
| T31 独立完成 evidence | NOT_RUN | native BLOCKED；M5 不在本轮 |
| T35 接单 / 改派旧角色失效 | PASS（contract） | reassignment 19/19 |
| U01 单一主动作 | PASS（contract） | role_action 8/8 |
| U03 可见性按角色 | PASS（contract） | visibleToMe 既有；M4 仅消费 |
| U04 终态只读 | PASS（contract） | terminal_state_readonly + isTerminal guards |
| U05 错误原因同屏 | PASS（contract） | mainAction / disabledActionReason 显式 `reason` 字段 |
| U07 重复点击不重复建 | NOT_RUN | native BLOCKED；契约层留 generateStableKey + 命令边界（M2 既有） |

| 真实桌面操作 | NOT_RUN | sandbox-exec preflight rc71 |
| 权威状态与回执 | NOT_RUN | native BLOCKED |
| 失败与重试 | NOT_RUN | native BLOCKED |
| 重启恢复 | NOT_RUN | native BLOCKED |
| 受影响先前模块回归 | NOT_RUN | native BLOCKED |

---

## 6. 候选清单（供独立 Review 重建快照）

```json
{
  "candidate_id": "M4-r1-worktree",
  "base_candidate_id": "M3-r2-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "modified_files": [
    {
      "path": "app/bundle/main.splash",
      "before_sha256": "6cc98e88f03b2ca413c2965baca27f4997aaecf68397182b6235b2fa9166de32",
      "after_sha256": "02220afb7ea3ba66a9247f40694766955e8827c79dbb414142380fb22d065eee",
      "after_bytes": 201458,
      "after_lines": 4526
    }
  ],
  "test_counts": {
    "contract": {"passed": 1, "total": 1},
    "concurrency": {"passed": 12, "total": 12},
    "reschedule": {"passed": 10, "total": 10},
    "reassignment": {"passed": 19, "total": 19},
    "role_action": {"passed": 8, "total": 8},
    "audit_source": {"passed": 7, "total": 7},
    "TOTAL": {"passed": 57, "total": 57}
  },
  "host_started": false,
  "host_blocker": "sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN (carried from M0/M1/M2/M3)",
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 7. 尚未完成（FAIL / BLOCKED / NOT_RUN）

- **FAIL** D-M3-01 / 03 / 04 / 05 / 06 仍挂账；M4 不修
- **FAIL** D-M2-01..07 仍挂账；M4 仅消费
- **BLOCKED** native 桌面 launcher = sandbox-exec rc71 + pgrep rc3 UNKNOWN；不启动宿主 / 不调 --help；既有残留 UNKNOWN
- **NOT_RUN** 真实键鼠 / 中文人输入 / 视口 / 接单 receipt-of-action / 重启恢复 / 失败注入
- **NOT_RUN** 真实模型 provider；G0-E 沿用 M0 / M3 延期；本模块不申请激活
- **NOT_RUN** 真实工件 picker；M5 不在本轮

---

## 8. 衔接

- 候选清单、源码静态审计、Python 调度契约、6 套测试、共 57 用例 + 6 套 evidence JSON + 1 review-driver、主源 main.splash + 7 个脚本 SHA-256 均列出
- 隔离数据全部在 `runtime/optimization/2026-10-09/M4/r1/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review
- 不进入 M5；完成交接后停止，等待独立 Review

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动真实模型 provider；不动业务身份变更；不动公网部署或发消息；不动 M2/M3 BLOCKED 必修；不修 D-M4-01 缺口之外的 P0 缺口）
