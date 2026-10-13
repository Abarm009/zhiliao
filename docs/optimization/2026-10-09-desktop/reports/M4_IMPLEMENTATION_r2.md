# M4 实施报告 r2 · 缺陷修复轮

**状态：READY_FOR_REVIEW；按 r1 Review 缺陷清单 D-M4-01..05 逐条修复；不进入 M5。**

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | r1 Review 的 5 条 P1 必修缺陷 | 严格按清单修改，不发散 |
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有）；本轮不修 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本轮不修 |
| M2 | BLOCKED | D-M2-01..07 未闭合；本轮仅消费 `runCommandBound` |
| M3 | FAIL | D-M3-01/03/04/06 未闭合；本轮仅消费 D-M3-05 的自增路径 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN | 不启动宿主；不调 --help |
| 真实 provider | NOT_RUN | 不申请激活 |
| A-M4-01/02/03 | P2 建议 | 不属本轮 P1，未触动 |

---

## 1. 缺陷逐条修复（按 r1 编号）

### 1.1 D-M4-01 · 预约年月日与上海时区

**根因**：`parseApptFormToMs` 只取"今日 00:00 + h * 3600000"，`y/m/d` 形同虚设；11/31 通过 `validateApptForm` 的 `<= 31` 检查；`formatApptLine` 提议日期读全局 `STATE.draft_appt`（串任务）。

**改动**：

- 复用既有 `_daysBeforeYear` / `_daysBeforeMonth` / `_isLeap`（M2 起已落地），新增 `_parseApptFormYmdh(y,m,d,h,mn)`：本地 → UTC = `days*86400000 + ms_in_day - 28800000`。
- `parseApptFormToMs` 改为两次调用 `_parseApptFormYmdh`；移除 `today_start / base % day_ms`。
- 新增 `_daysInMonth(y,m)`，按闰年规则返回 28/29/30/31；`validateApptForm` 用 `_daysInMonth(form.date_y, form.date_m)` 校验 `date_d` 区间。
- 新增 `_shanghaiYmdhFromMs(ms)`，UTC ms → 上海 y/m/d/h/mn；`formatApptLine` 改为读 `a.startMs / a.endMs` 转回显示完整日期 + 星期 + Asia/Shanghai；不再读 `STATE.draft_appt`。

**验证**：

- 独立 Python 模拟 `_parseApptFormYmdh`：`2026-10-11 14:00` Shanghai → `1791698400000` UTC ms（与 r1 期望一致）。
- `2026-12-31 14:00` Shanghai → `1798696800000` UTC ms（旧代码会把 12/31 当作"今日 + 14h"，给 `1791640800000`）。
- `daysInMonth(2026,11)=30`、`daysInMonth(2024,2)=29`、`daysInMonth(2027,2)=28`。
- 7/7 时间算术单元测试 PASS：`runtime/optimization/2026-10-09/M4/r2/evidence/d_m4_01_time_math.json`。
- 源码静态审计 5/5 PASS：`evidence/d_m4_01.json`。

### 1.2 D-M4-02 · 取消 / 改约边界 + 自冲突

**根因**：`sourceOk` 不识别 `cancelAppointment / rescheduleAppointment`，统一拒绝点 `:970` 直接拒；`hasTechConflict` 总是核对当前任务 PROPOSED，改约等于"今天不和今天自己冲突"。

**改动**：

- `sourceOk` 新增两条分支：
  ```fn
  if cmd == "cancelAppointment" { ... ACCEPTED / SCHEDULED }
  if cmd == "rescheduleAppointment" { ... ACCEPTED / SCHEDULED }
  ```
- `hasTechConflict` 新增第 5 形参 `same_proposal_id`，按 id 精确排除；旧版本"CONFIRMED 排除"改为可选 fallback。
- `proposeAppointment`：把当前 PROPOSED id 作为 `exclude_proposal_id` 传入；新提议入栈前 SUPERSEDE。
- `rescheduleAppointmentFromForm`：去掉"CONFIRMED 时必须先取消"的硬拒（`fail("当前为已确认预约；先『取消预约』再提议...")`）；新提议 SUPERSEDE 旧 PROPOSED，CONFIRMED 保留；调用 `hasTechConflict(..., previous_proposed_id)` 排除旧 PROPOSED。
- 事件行 `replaces: previous_proposed_id2` 仍写入 receipt 参数与 appointment 字段；旧预约 ID → 新 PROPOSED 链路保留。

**验证**：

- 6/6 源码契约 PASS：`evidence/d_m4_02.json`。
  - `sourceOk` 含 `cancelAppointment` / `rescheduleAppointment`
  - `hasTechConflict` 签名含 `same_proposal_id`
  - `rescheduleAppointmentFromForm` body 不含"必须先取消"硬拒；调用 `hasTechConflict(t, tech, start, end, previous_proposed_id)`
  - `proposeAppointment` 调用 `hasTechConflict(t, tech, start, end, exclude_proposal_id)`

### 1.3 D-M4-03 · 锁与创建版本

**根因**：`_acquireTaskLock` 是 TOCTOU `exists + write`，两进程同读同写都 `return true`；`_releaseTaskLock` 写空但锁文件仍在，下一次 acquire 永远 `false`；`createDraftFromPanel` 把 `t.version=0` 直接交给 `commitBound(expected_version=0)`，要求 `t.version == expected_version+1` 失败。

**改动**：

- `_acquireTaskLock` 改 CAS：先 `read` 现有内容（非空 → 直接放弃）→ 写 `actor@ms@seq` 独占戳 → 立即 `read-back`，与刚写的戳不一致即被对端抢走。
- `_releaseTaskLock` 写空字符串作"已释放"标记；下个 acquire 仍可 CAS。
- `createDraftFromPanel`：在 `commitBound(t, 0, "createDraft", ...)` 之前 `t.version = t.version + 1`（t.updatedAtMs 也刷新）。`_PENDING_CMD = ""` 保留恢复。

**验证**：

- 4/4 源码契约 PASS：`evidence/d_m4_03.json`（CAS 模式三要素 + 无 `fs.exists` + release 写空 + 自增在 commitBound 前）。
- 5/5 独立并发模拟 PASS：`evidence/d_m4_03_lock_cas.json`（A 持锁时 B 抢占失败；释放后 C 抢占成功；5 线程并发仅 1 胜；连续 10 轮 A→释放→B 循环无卡死）。
- 旧版 `_acquireTaskLock` / `commitBound` 7 函数相同部分未触动；本轮只补 createDraftFromPanel 的自增路径，符合 r1 备注"继承创建版本协议未闭合"为"确实阻断 M4 的最小依赖"。

### 1.4 D-M4-04 · 旧确认 / AI 采纳失效

**根因**：`m4_invalidateConfirmation` 把 `CONFIRM_BIND.last_confirmed_at_ms` 清零，导致 `confirmDraftModelBound` 的拒绝条件 `invalidated_by_edit && last_confirmed_at_ms != 0` 反向成立（旧 → 失效仍可通过）；不重置 `AI_STATE`，采纳按钮的 `!active && AI_STATE==APPLIED` 继续成立；`unbindAsset / proposeAppointment / confirmAppointment / rejectAppointment` 不调用失效函数。

**改动**：

- `m4_invalidateConfirmation(reason)`：
  - **不再清零** `last_confirmed_at_ms`；只置 `invalidated_by_edit = true`，让拒绝条件真成立。
  - `if AI_STATE == "APPLIED"` → `AI_STATE = "EXPIRED"`，采纳按钮条件自动拒绝。
  - `STATE.m4_invalidations.last_invalidate_reason = reason` 留审计。
  - 注释标明"用户可经由 `confirmDraftModelBound` 重新走恢复路径"。
- `unbindAsset` / `proposeAppointment` / `confirmAppointment` / `rejectAppointment` 各自在 commit 成功、logEvent 之后追加 `m4_invalidateConfirmation("<cmd>")`。

**验证**：

- 6/6 源码契约 PASS：`evidence/d_m4_04.json`（去注释后无 `last_confirmed_at_ms = 0`；`AI_STATE = "EXPIRED"`；4 个新增调用点齐全）。
- `confirmDraftModelBound` 拒绝条件（`:2052` `invalidated_by_edit && last_confirmed_at_ms != 0`）的语义保留：失效后仍能识别 → 强制用户重新确认。

### 1.5 D-M4-05 · 开工核当前有效设备

**根因**：`startProgress` 仅 `t.asset != ""` 即放行；绑定后归档 / 服务关系撤销 / 跨项目变更都不再核。

**改动**：

```fn
let cur_a = pickUser(ASSETS, t.asset)
if cur_a == nil { fail("开工时设备不存在（已被删除/伪造）"); return }
if !cur_a.active { fail("开工时设备已归档（active=false）；请重新选择设备"); return }
if cur_a.project != t.project { fail("开工时设备归属项目已变更..."); return }
if !services(t.asset, t.space) { fail("开工时设备不再服务当前空间..."); return }
```

**验证**：

- 4/4 源码契约 PASS：`evidence/d_m4_05.json`（`pickUser(ASSETS, t.asset)` + `!cur_a.active` + `cur_a.project != t.project` + `services(t.asset, t.space)` 全部出现）。

---

## 2. 改动文件清单（仅一处主源 + r2 脚本）

| 文件 | 改动摘要 |
|---|---|
| `app/bundle/main.splash` | 仅本模块 5 个缺陷对应函数 / 边界 / 守卫；其他函数原样 |
| `runtime/optimization/2026-10-09/M4/r2/scripts/m4_fix_verifier.py` | 25 项源码契约检查（5 个 D-M4-XX） |
| `runtime/optimization/2026-10-09/M4/r2/scripts/m4_d01_time_math.py` | 7 项时间算术单元测试 |
| `runtime/optimization/2026-10-09/M4/r2/scripts/m4_d03_lock_cas.py` | 5 项并发锁 CAS 模拟 |
| `runtime/optimization/2026-10-09/M4/r2/CANDIDATE.json` | r2 候选清单 |
| `runtime/optimization/2026-10-09/M4/r2/evidence/*.json` + `results/fixes.json` | 证据落盘 |
| `docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r2.md` | 本报告 |

主源 SHA-256 变化：
- 前（M4-r1）：`02220afb7ea3ba66a9247f40694766955e8827c79dbb414142380fb22d065eee`（201458 字节 / 4526 行）
- 后（M4-r2）：`c656536119ff0983394bc10f65578095508ca3643e9a538ba8e82b415beab545`（210162 字节 / 4618 行）

---

## 3. 启动 / 重跑

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M4/r2/scripts/m4_fix_verifier.py
python3 runtime/optimization/2026-10-09/M4/r2/scripts/m4_d01_time_math.py
python3 runtime/optimization/2026-10-09/M4/r2/scripts/m4_d03_lock_cas.py
```

隔离数据全部落在 `runtime/optimization/2026-10-09/M4/r2/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。

---

## 4. 覆盖 r1 既有用例的状态变化

| 编号 | r1 状态 | r2 状态 | 备注 |
|---|---|---|---|
| T04 双独立连接抢同 OPEN | NOT_RUN 原生 | BLOCKED 原生 / 源码依赖 PASS（D-03 CAS + 自增） | 真并发需重审 launcher |
| T06 经理改派 SCHEDULED → 取消旧预约 + 新技工有效 | NOT_RUN 原生 | 源码 PASS；旧 CONFIRMED 保留路径保持（reschedule 不动 CONFIRMED） | 原生运行仍 BLOCKED |
| T07 设备编码 / 载荷解析 | BLOCKED | 未触动（属 M5 / picker） | 不属本轮 |
| T08 安装位置 / 服务空间分离 | PASS（contract） | 保留 | bindAsset + startProgress 双层核 |
| T09 缺项 / 时窗 / 旧技工 | 部分 FAIL D-M4-05 | 修复（D-05） | 经理理由拼接保留为 A-M4-03 |
| T10 提议不直接 SCHEDULED | PASS | 保留 | sourceOk 路径未变 |
| T11 并发确认重叠仅一成功 | FAIL D-M4-03 | 修复（D-03） | CAS 模式 + hasTechConflict 跨任务跨项目 |
| T12 待确认改约 / 旧预约有效 | FAIL D-M4-02 | 修复（D-02） | reschedule 不再硬拒 CONFIRMED |
| T13 过期 / 伪造时钟 | 协议保留 | confirmAppointment 24h + start-endMs 校验未变 | 原生运行未跑 |
| T14 上海日期换算 UTC | FAIL D-M4-01 | 修复（D-01） | `_parseApptFormYmdh` |
| T15 旧 version 409 | 部分 | runCommandBound 未改 | 原生冲突未跑 |
| T31 取消 / 终态只读 / 重开 | 保留 | 保留 | cancelAppointment 已接 sourceOk |
| T35 改派 / 改约旧 AI 失效 | FAIL D-M4-04 | 修复（D-04） | APPLIED → EXPIRED；4 个新调用点 |
| U01 角色 × 主动作 | PASS | 保留 | mainAction / secondaryActions 未触动 |
| U03 承接者不自验 | PASS | 保留 | |
| U04 改约 / 冲突 / 过期 | FAIL D-M4-01/02 | 修复（D-01 + D-02） | |
| U05 安装位置 / 服务空间 | PASS | 保留 + 起点路径 D-05 加强 |
| U07 重复点击 / 离线输入 | NOT_RUN 原生 | 保留 | 命令边界 + 锁修复有利恢复 |

---

## 5. 候选清单核心字段

```json
{
  "candidate_id": "M4-r2-worktree",
  "base_candidate_id": "M4-r1-worktree",
  "head": "WORKTREE-UNCOMMITTED",
  "module": "M4",
  "modified_files": ["app/bundle/main.splash"],
  "test_counts": {
    "fix_verifier":  {"passed": 25, "total": 25},
    "d01_time_math": {"passed": 7,  "total": 7},
    "d03_lock_cas":  {"passed": 5,  "total": 5},
    "TOTAL":         {"passed": 37, "total": 37}
  },
  "host_started": false,
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 6. 仍未完成 / BLOCKED / NOT_RUN

- **FAIL** D-M3-01/03/04/06 仍挂账；本轮不修
- **BLOCKED** 桌面 launcher = sandbox-exec rc71 + pgrep rc3 UNKNOWN；不启动宿主
- **NOT_RUN** 真实键鼠 / 中文人输入 / 视口 / 接单 receipt-of-action / 重启恢复 / 失败注入
- **NOT_RUN** 真实模型 provider；G0-E 沿用 M0/M3 延期
- **NOT_RUN** 真实工件 picker；M5 不在本轮
- **A-M4-01/02/03** 仍挂账；按 r1 不属本轮 P1，未触动

---

## 7. 衔接

- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review
- 不进入 M5；完成交接后停止，等待独立 Review
- 所有 r2 数据落 `runtime/optimization/2026-10-09/M4/r2/`；`~/.octosense` 未访问

NEEDS_ABRAM=no（不申请 AppHub publish / 公开签名 / listing；不申请真实模型 provider；不动业务身份源头；不动公网部署；不动 M0/M1/M2/M3 BLOCKED）