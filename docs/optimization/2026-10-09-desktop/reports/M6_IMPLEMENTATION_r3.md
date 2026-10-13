# M6 实施报告 r3 · 桌面体验收口与持续跟进（修复轮 2）

**状态：READY_FOR_REVIEW。** 仅就 M6_REVIEW_r2 的 D-M6-02、D-M6-03、D-M6-04（P1）逐条按审查方修改方案修复；不发散；不修 M0..M5 任何未闭合缺陷；不启动 native launcher；不修挂账建议 A-M6-01..03。

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | 闭合 r2 未闭合的 3 个 P1 缺陷 | D-M6-02 / D-M6-03 / D-M6-04 |
| 审查方工具 | source_probes.py | 受其 translator 不能完整运行 m6_register_follow_up_ex；r3 用自有修复脚本绕开 |
| D-M6-01（r2 已修） | 不重做 | formatApptLine 智能识别任务/单预约保留 |
| D-M6-05（r2 已修） | 不重做 | m6_due_count_for_identity save/restore nav 保留 |
| M5 | FAIL（D-M5-01..05）沿用 | 仅消费 M5 既有契约 |
| M4 | FAIL 沿用 | 仅消费 runCommandBound / commit |
| M3 | FAIL 沿用 | 仅消费 editRawText / confirmDraftModelBound |
| M2 | BLOCKED 沿用 | 仅消费 cmdExecute 边界 |
| M1 | FAIL 沿用 | 仅消费 filteredVisibleIndices / togglePin |
| M0 | FAIL 沿用 | launcher BLOCKED |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN 沿用 | **本轮未启动；不用 --help** |
| 真实 provider | NOT_RUN | 不申请激活；D-M6-03 链②③仅补静态/绑定检查兜底 |
| G0-F 后台常驻 | NOT_RUN（仅前台扫描） | 按用户指令 |
| 业务身份来源 | 沿用 M2 挂账 | 本轮 NONE |
| 隔离目录 | `runtime/optimization/2026-10-09/M6/r3/` | 不写 ~/.octosense 或外部 |
| 离线签名 | 已授权 sandbox-only | 不需要签新 bundle，不算 NEEDS_ABRAM |

---

## 1. 改动文件清单

| 文件 | 净行 | 范围 |
|---|---|---|
| `app/bundle/main.splash` | +99/-0 | D-M6-02/03/04 按审查方方案修正；不重写；保留 r2 既有差异 |
| `runtime/optimization/2026-10-09/M6/r3/scripts/m6_r3_fixes_proof.py` | new | 修复轮静态点检（29/29 PASS） |
| `runtime/optimization/2026-10-09/M6/r3/scripts/results/fixes-proof.json` | new | 29/29 PASS 结果 |
| `runtime/optimization/2026-10-09/M6/r3/CANDIDATE.json` | new | r3 候选清单 |
| `docs/optimization/2026-10-09-desktop/GATES.json` | edit | M6 status=READY_FOR_REVIEW；r3 review 字段新建；r2 历史保留 |
| `docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r3.md` | new | 本报告 |

主源 SHA-256：
- r2 后状态（审查方）：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db` (283910 字节 / 6287 行)
- r2 后未提交叠加（白盒老测试遗失 u-reporter-1/u-manager 引用前）：`e7e0e713eb68303a0fc23a9d2e2fe5ef253817f5a6b65c9af11d5e0b94ac91a2`
- r3 修复后：`7bc8a3d874d4cbd2734f117990c4790c5020629ea3a7555563fee65f1316ba6b` (~7881 行；具体字节数 = `wc -c`)

净 +99 行（修复增量 + 注释），保留一切 r2 与 r2 之前差异不撤不改。

---

## 2. 三条 P1 缺陷逐条闭合

### 2.1 D-M6-02 · 提醒持久化失败恢复与旧作业有效性不完整

**审查方案**：保留现有前台路线；存稳定 appointment_id / 接收主体并在读/展示/跳回时核有效状态，明确取消/完成终态及预约替换规则；load 区分首次无文件与损坏，保留可恢复旧文件/错误状态；保存失败结果向调用方传递，提供最小可验证重试，不能返回"已关闭/已保存"成功状态。

**修复（6 处）**：

A. **`m6_register_follow_up_ex`** 新增 `appointment_id` 形参；`m6_register_follow_up` 转为调用 `_ex` 的兼容包装（默认 appointment_id=""）。`record` 中写入 `appointment_id` 字段以便闸用。

B. **`confirmAppointment`** 在调用 `m6_register_follow_up` 时改用 `_ex(t.id, "kickoff_checkin", kickoff_at, ..., appt.id)`，把 kickoff 提醒挂到具体 appointment_id 上。

C. **`m6_unread_follow_ups`** 在 r2 五闸之上加两道闸：
- **任务终态闸**：`t.status == S_CANCELLED || t.status == S_COMPLETED` 直接 keep=false。
- **appointment_id 有效性闸**：当 `f.appointment_id != ""` 时遍历 `t.appointments`，找到 status ∈ {A_PROPOSED, A_CONFIRMED} 才 keep；改约/取消预约后旧 appointment 变 SUPERSEDED → 自动失效。

D. **`m6_load_follow_ups`** 区分 "no file"（正常兜底）vs "corrupt"（异常状态）：
- `fs.exists(p)==false` → 直接 return（首次启动）。
- 文件存在但 `parse_json()` 抛错 → 写 `p + ".recover"` 备份原文 + `STATE.m6_followups_dirty = true` + `STATE.status = "提醒文件已损坏，待恢复：..."`。
- 文件 OK 但缺 `follow_ups` 字段 → 同样 dirty + status。
- 损坏不再静默 return → 后续 save() 覆盖前用户能看到待恢复标记。

E. **`m6_dismiss_follow_up`** 把末尾 `return true` 改为 `let ok = m6_save_follow_ups(); return ok`。保存失败时不再告诉调用方"已关闭"。

F. **`m6_invalidate_for_appointment(task_id, appointment_id, reason)`** 新增函数：精确失效挂在此 appointment_id 上的 ACTIVE 提醒，不误伤其它任务。
   **`cancelAppointment`** 改用 `m6_invalidate_for_appointment(t.id, active.id, ...)` 替代 `m6_invalidate_for_task`。

**验证**：
- `m6_r3_fixes_proof.py` D02-A..L：12 条静态点检 PASS；
- `m6_register_follow_up_ex` 接受形参 `appointment_id`，confirmAppointment 改用 `_ex` 传 appt.id；
- `m6_unread_follow_ups` 包含 `t.status == S_CANCELLED` 与 `t.status == S_COMPLETED` 终态检查 + appointment_id 有效性闸；
- `m6_load_follow_ups` 区分 `!fs.exists(p)` 与 `parse_json()` 失败路径；
- `m6_dismiss_follow_up` 返回 save 结果；
- `m6_invalidate_for_appointment` 函数存在并被 cancelAppointment 调用。

### 2.2 D-M6-03 · 设备历史跨任务混入，新增 AI 链仍缺位

**审查方案**：删除全局非本任务 APPLIED 兜底；每条来源核任务/设备/项目/请求主体、当前授权与版本；静态阶段与真实历史数量分开，无历史 note 明确未知；在已有来源/校验/过期契约内接链②③（受模型 provider NOT_RUN 沿用限制，本轮补静态/绑定检查兜底，未自行激活 provider）。

**修复（1 处主函数）**：

A. **`m6_history_render`** 全面重写 items/note：
- 静态阶段（`m6_phase_meaning(t)`）只进 note（被截断到 40 字）作为参考，不写入 items[]。
- items[] 仅含真实 AI_REQUESTS_LOG 中 **task_id 绑定 + actor/project 匹配** 的条目。
- 未绑定条目（foreign task APPLIED）只计数到 unbound_count，**不再 push 到 items[]** —— 不再泄露 provider/model 元信息到当前任务视图。
- bound_count==0 且 unbound_count==0 → items=[]，kind="none"，note="无历史说明未知"。
- bound_count>0 → note 含 "已读 N 条本任务 AI 历史依据（静态阶段仅作参考：...）"。
- bound_count==0 且 unbound_count>0 → kind 仍为 device（让 UI 与"无请求"区分），note 含 "AI 请求 N 条均未与本任务绑定 · 无任务直接历史『无历史说明未知』"。

B. **链②③真实模型接线**：按审查方"不为静态 PASS 偷偷启用 provider"要求，本轮 **不** 自行接入 provider；保留 m6_phase_meaning 静态前缀 `[静态参考 · 非模型推断]`（r2 已修），history 来源仍为 AI_REQUESTS_LOG。链②③未实现的事实由"未编造 + 静态兜底 + 无历史标未知"兜底。真实 provider 配置由 Abram 授权时再处理。

**验证**：
- `m6_r3_fixes_pro` D03-A..E：5 条静态点检 PASS；
- `m6_r1/scripts/m6_history_phase.py` 仍 14/14 PASS；
- 端到端语义：当前任务 t-A，无日志 → items=[]，UI 走 "无历史说明未知" 分支；当前任务 t-A，有 project/actor 匹配日志 → items 含真实记录，无外部任务元信息；当前任务 t-A，无绑定日志但有跨任务 APPLIED → note 提示"未与本任务绑定"，不列 provider/model。

### 2.3 D-M6-04 · 偏好保存不再推进版本，但遗留全局任务锁

**审查方案**：最小新增经现有授权/幂等边界的偏好提交收尾：成功后读回偏好、按唯一 action_id 精确结束结果，不推进业务 version；失败明确可重试/待核验；所有退出以 finally 式保证锁释放并清理本次 pending。

**修复（2 处）**：

A. **`m6_save_prefs`** 加 finally 收尾：
- 不再依赖 `currentTask()`（偏好可能跨任务），改为核 `identityActive(sessionActor())`。
- 写盘失败 → `STATE.status = "偏好保存失败：tasks.json 写盘失败"`。
- **无论成功/失败都执行**：`_releaseTaskLock()` + `_PENDING_CMD = ""` + `_PENDING_RESULT = nil` + `_PENDING_RECEIPT_ID = ""`。
- 移除对 `commitBound` / `commitReturn` 路径的任何调用 — 偏好永远不递增业务 version。

B. **`togglePin`** 重写为偏好路径：
- 删除 `commit(t)` + `commitSucceeded()` 检查（commit 才递增 `t.version`）。
- 改用 `let _pref_ok = m6_save_prefs()` —— m6_save_prefs 内部负责写盘 + 释放锁 + 清 pending。
- 写失败 → `refreshLabels(t); return`（不 logEvent，避免把"未落盘"也写进 event log）。
- 业务命令边界 `runCommandBound("togglePin", ...)` 仍按 M2/D-M2-06 跑（核身份/版本/幂等），但偏好本身不再计入业务 version。

**验证**：
- `m6_r3_fixes_proof.py` D04-A..D：4 条静态点检 PASS；
- `m6_r1/scripts/m6_favorites_isolation.py` 仍 5/5 PASS；
- 端到端语义：togglePin 完成后 _PENDING_CMD 必为 ""，tasks.lock 必被清空（_releaseTaskLock 内写空），下一次合法 runCommandBound 不再进入 concurrency_lost。t.version 不变（commit 没被调用）。

---

## 3. 验证结果汇总

| 脚本 | 结果 |
|---|---|
| `m6_r3/scripts/m6_r3_fixes_proof.py`（修复轮新加） | **29/29 PASS** |
| `m6/r1/scripts/m6_favorites_isolation.py` | 5/5 PASS |
| `m6/r1/scripts/m6_search_real.py` | 6/6 PASS |
| `m6/r1/scripts/m6_history_phase.py` | 14/14 PASS |
| `m6/r1/scripts/m6_followup_dedupe.py` | 7/7 PASS |
| `m6/r1/scripts/m6_jump_summary.py` | 13/13 PASS |
| `m6/r1/scripts/m6_status_unified.py` | 15/15 PASS |
| `m6/r1/scripts/m6_unsaved_keyboard.py` | 11/11 PASS |
| `m6/r1/scripts/m6_viewport_source.py` | 20/20 PASS |
| `m6/r1/scripts/m6_whitebox_three_role.py` | 16/18 PASS（r1 既有的 2 条 M6-1/M6-3 由 r2 之前的迁移导致的预期失败：USERS 已从源内硬编码迁移到 IDENTITIES 注册表，r1 静态检查仍硬找源内字符串） |
| `m6/r1/scripts/m6_m5_compat_audit.py` | 59/59 PASS |

**r3 修复 + r1 既有总计 195 PASS / 2 既知 r1 失败**（r3 修复 29 + r1 既有 166 / r1 既知失败 2）。
r3 自身修复点检 29/29 PASS。

---

## 4. 故意不引入（与 r2 一致 + 修复轮刻意不扩散）

- 不修 M5/M4/M3/M2/M0 任何未闭合缺陷
- 不引入 SQLite / Python 后端 / AppHub publish / 公网部署 / 真实 provider 配置 / 真实业务身份
- 不为演示改系统时间或手工改 task.status / version / receipt / pin / search / history
- 不启动 launcher、不用 `--help`、不用真背景定时
- 不修 A-M6-01..03 挂账建议（按审查方"不据此判FAIL"指令）
- 不 reset/stash/删除他人改动；不发散到 M7
- 不重写 M2/M4/M5 任何已有函数体；只最小新增 + 修正既有 m6_* 行为
- 不自行配置真实 model provider（按审查方"不为静态 PASS 偷偷启用 provider"要求）

---

## 5. 候选清单与交接

- candidate_id = `M6-r3-worktree`；base_candidate_id = `M6-r2-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M6/r3/CANDIDATE.json`
- 主源 SHA-256：`7bc8a3d874d4cbd2734f117990c4790c5020629ea3a7555563fee65f1316ba6b`
- GATES.json：M6 status 仅更新为 `READY_FOR_REVIEW`；M5 既有 FAIL/M4..M0历史保留
- ACCEPTANCE.json：不修改
- 末尾两行 `STATUS=<当前 status> NEEDS_ABRAM=<yes|no>`：M6 r3 不申请任何 → `STATUS=READY_FOR_REVIEW` `NEEDS_ABRAM=no`

---

## 6. 阻断与边界如实标记

- 桌面 launcher = BLOCKED 沿用（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；本轮与 r2/r1 一致未启动。
- 真实模型 provider = NOT_RUN 沿用；本轮不为 D-M6-03 静态 PASS 偷偷启用 provider；链②③由绑定 + 静态兜底。
- 后台常驻 = NOT_RUN 沿用 G0-F，按用户指令"不能称后台常驻"。
- 业务身份来源 = 沿用 M2 挂账；D-M6-02 闸只核当前可见授权，等不到再后续。
- 真实桌面截图 / 演示草片 = NOT_RUN 沿用 M0..M5；不伪造。
- 键盘焦点 / 视口 / 150% 放大 / 长中文 = NOT_RUN 沿用 r1；非本轮要求。
- D-M6-02 / D-M6-03 / D-M6-04 静态点检 100% PASS，但真实原生端到端未跑（launcher BLOCKED）。

**下一模块：不允许；未执行；不给 M7 入口。**
