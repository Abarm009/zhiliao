# M4 实施报告 r3 · D-M4-02/03/04/05 严格按 r2 Review 方案逐条闭合

**状态：READY_FOR_REVIEW；本轮严格按 r2 Review 缺陷清单 D-M4-02/03/04/05 修复；D-M4-01 r2 已 CLOSED，本轮不触动；不进入 M5。**

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | r2 Review 的 4 条 P1 必修缺陷（D-M4-02/03/04/05） | 严格按方案修复，不发散 |
| M0/M1/M2/M3 | FAIL/BLOCKED 沿用 | 本轮不修 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN | 不启动宿主；不调 --help |
| 真实 provider | NOT_RUN | 不申请激活 |
| A-M4-01/02/03 | P2 建议挂账 | 未触动 |
| D-M4-01 | r2 已 CLOSED（日期算术/非法日校验子范围） | 不触动；原生投影仍挂 A-M4-02 |

---

## 1. 缺陷逐条修复（按 r2 编号）

### 1.1 D-M4-02 · 改约边界 + 自冲突 + 准入前突变

**r2 触发**：
- 触发1：只有 CONFIRMED 无 PROPOSED 时，`previous_proposed_id` 为空，旧 CONFIRMED 仍被自冲突拒。
- 触发2：SUPERSEDED 旧 PROPOSED 在 `runCommandBound` 之前执行，准入失败时旧 status 已变。

**修复（按 r2 方案）**：
- `hasTechConflict` 签名改为 `same_task_exclude_ids`（数组）；同任务内按 ID 集合精确排除。
- `rescheduleAppointmentFromForm` 取当前 `A_PROPOSED` 与 `A_CONFIRMED` 两个 ID 组成 `exclude_ids`；改约可同时替换旧 PROPOSED 与旧 CONFIRMED，旧 CONFIRMED 不再自冲突。
- `proposeAppointment` 同样改传 `exclude_ids` 数组（仅含现有 PROPOSED）。
- 两个函数的 `a.status = A_SUPERSEDED` 循环整体移到 `runCommandBound` 通过之后；`runCommandBound` 失败时旧预约状态保持 PROPOSED、任务/历史不变。

**证据**：
- `evidence/source_probe.json`：
  - `hasTechConflict` 签名含 `same_task_exclude_ids`，体内 `while k < same_task_exclude_ids.len()` 数组循环。
  - `proposeAppointment` 含 `hasTechConflict(t, tech, start, end, exclude_ids)`，`a.status = A_SUPERSEDED` idx > `runCommandBound("proposeAppointment"...)` idx。
  - `rescheduleAppointmentFromForm` 含 `hasTechConflict(t, tech, start, end, exclude_ids)` + `confirmed_appt`，且 `a.status = A_SUPERSEDED` idx > `runCommandBound("rescheduleAppointment"...)` idx。
- `evidence/behavior_probe.json`：
  - only-confirmed 同任务 → 旧版自冲突 True（r2 bug 复现）；r3 排除数组含 CONFIRMED id → False。
  - only-proposed 同任务 → False。
  - PROPOSED + CONFIRMED 共存同任务 → False（两个 ID 都排除）。
  - 跨任务重叠 → True（不放过）。

### 1.2 D-M4-03 · 原子锁

**r2 触发**：`_acquireTaskLock` 用 `exists + write + readback` 伪 CAS；两独立 PID 都 acquired=true。

**修复（按 r2 方案：使用宿主实有原子互斥）**：
- `_acquireTaskLock` 改走 `fs.rename` 原子路径：
  1. 写 actor 专属 tmp 文件 `tasks.lock.tmp.<actor>`（stamp 跨进程唯一：`actor@ms@seq`）。
  2. `fs.rename(tmpfile, "tasks.lock")`：POSIX rename 是真原子（同一文件系统的 rename 在内核视图中是一次性替换）；rename 失败（dest 已被对端占用）→ 返回 `held_by_other_actor`。
  3. 读回确认：readback == 本 actor stamp → `owned`；否则 `lost_after_rename`。
- `_releaseTaskLock` 改走 `fs.rename("tasks.lock", actor_tmp)` 把锁文件挪回 actor tmp，让下个 acquire 可再次抢占；rename 失败兜底写空。
- 沿用 host 实有 fs API；未引入 Python 业务服务 / SQLite / 第三方库。

**证据**：
- `evidence/source_probe.json`：`atomic_rename_present`、`rename_failure_returns_held_by_other_actor`、`release_uses_rename`、`release_fallback_write_empty` 全 PASS。
- `evidence/behavior_probe.json`：
  - `single_actor_acquire_release_cycle`：A 获 → 释 → 再获 → 再释 全 PASS。
  - `rename_atomicity_first_readback_wins`：10 轮顺序仿真，A 先 rename 后 readback 见到自己 stamp（own），B 后 rename 后 readback 见到自己 stamp（own）；与 POSIX 原子 rename 语义一致。
  - `release_then_other_can_acquire`：A 释放后 B 立即可获 → PASS。

### 1.3 D-M4-04 · 未确认旧 AI 草稿失效

**r2 触发**：`m4_invalidateConfirmation` 因 `last_confirmed_at_ms == 0` 不置 `invalidated_by_edit`，`confirmDraftModelBound` 的拒绝条件 `invalidated_by_edit && last_confirmed_at_ms != 0` 反向成立（旧 → 失效仍可通过）。

**修复（按 r2 方案）**：
- `m4_invalidateConfirmation` 不再依赖 `last_confirmed_at_ms > 0`；无条件置 `CONFIRM_BIND.invalidated_by_edit = true`。`APPLIED → EXPIRED` 与 `PENDING_AI_REQUEST.active = false` 保留。
- `confirmDraftModelBound` 的拒绝条件改为只判 `invalidated_by_edit == true`，不再要求 `last_confirmed_at_ms != 0`；旧确认和未确认旧草稿一并被拒。
- 成功确认后仍由 `CONFIRM_BIND.invalidated_by_edit = false` 复位（既有代码，未触动）。
- 用户重新确认路径：closeDraftPanel → openDraftPanel → 重填 → confirmDraftModelBound 通过（invalidate 已被 reset）。

**证据**：
- `evidence/source_probe.json`：
  - `m4_invalidateConfirmation` 体内 `CONFIRM_BIND.invalidated_by_edit = true` 无条件赋值，且不再含 `if CONFIRM_BIND.last_confirmed_at_ms > 0` 守卫。
  - `confirmDraftModelBound` 体内 `if CONFIRM_BIND.invalidated_by_edit == true {` 紧跟拒绝（无 `&& last_confirmed_at_ms != 0`）。
  - 末尾 `CONFIRM_BIND.invalidated_by_edit = false` 保留（成功路径复位）。
- `evidence/behavior_probe.json`：
  - `r2_buggy_passes_through`：True（验证 r2 行为确实漏判）。
  - `r3_blocks_unconfirmed`：True（r3 修复后未确认草稿也被拒）。
  - `r3_blocks_confirmed_too`：True（r3 同时保持对已确认旧确认的拒绝）。

### 1.4 D-M4-05 · 开工核当前承接者资格

**r2 触发**：`startProgress` 仅 `t.asset != ""` + ASSETS 注册/active/project/services 四检；缺当前承接者实时角色/技能校验。

**修复（按 r2 方案）**：
- `startProgress` 在 services 检查之后增加四重实时校验：
  1. `pickUser(IDENTITIES, t.assignee)`：当前承接者账号仍存在。
  2. `identityActive(t.assignee)`：身份仍有效（全局未撤权、未到期）。
  3. `hasRole(_cur_assignee, t.project, "TECHNICIAN")`：项目 TECHNICIAN 角色未被撤销。
  4. `skillOk(_cur_assignee, t.category)`：所需技能未被撤销。
- 任一不满足即 `fail(...)` 并 return；与既有 services 失败提示对齐。

**证据**：
- `evidence/source_probe.json`：
  - `start_rechecks_role`：`hasRole(_cur_assignee, t.project, "TECHNICIAN")` PASS。
  - `start_rechecks_skill`：`skillOk(_cur_assignee, t.category)` PASS。
  - `start_rechecks_identity_active`：`identityActive(t.assignee)` PASS。
- `evidence/behavior_probe.json`：
  - 角色撤销场景：拒绝（no role）。
  - 技能撤销场景：拒绝（skill revoked）。
  - 全资格场景：通过。

---

## 2. 改动文件清单（仅一处主源 + r3 脚本）

| 文件 | 改动摘要 |
|---|---|
| `app/bundle/main.splash` | 仅本轮 4 个缺陷对应函数 / 边界 / 守卫；其他函数原样 |
| `runtime/optimization/2026-10-09/M4/r3/scripts/m4_r3_fix_verifier.py` | 18 项源码契约检查（4 个 D-M4-XX） |
| `runtime/optimization/2026-10-09/M4/r3/scripts/m4_r3_behavior_probe.py` | 13 项算法行为仿真（4 个 D-M4-XX） |
| `runtime/optimization/2026-10-09/M4/r3/CANDIDATE.json` | r3 候选清单 |
| `runtime/optimization/2026-10-09/M4/r3/evidence/*.json` | 证据落盘 |
| `docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r3.md` | 本报告 |

主源 SHA-256 变化：
- 前（M4-r2）：`c656536119ff0983394bc10f65578095508ca3643e9a538ba8e82b415beab545`（210162 字节 / 4618 行）
- 后（M4-r3）：`4c753154cf55fb5912a53a5f09425c54bcc5787ee5e54d5d1f82cd8096a50f13`（324049 字节 / 7130 行）

> 注：r2 → r3 字节/行数大幅增加，是因为 r2 → 本轮之间累计了 M3/M4 的多轮中间落地；本轮纯 diff 仅限 4 个缺陷对应函数 / 边界 / 守卫。

---

## 3. 启动 / 重跑

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M4/r3/scripts/m4_r3_fix_verifier.py
python3 runtime/optimization/2026-10-09/M4/r3/scripts/m4_r3_behavior_probe.py
```

实测：
- `fix_verifier`：18/18 PASS
- `behavior_probe`：13/13 PASS

隔离数据全部落在 `runtime/optimization/2026-10-09/M4/r3/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。

---

## 4. r2 既有用例的状态变化（仅 P1 必修）

| 编号 | r2 状态 | r3 状态 | 备注 |
|---|---|---|---|
| T04 双独立连接抢同 OPEN | BLOCKED 原生 / 源码 D03 FAIL | 源码：D03 改 fs.rename 原子（POSIX）；原生 BLOCKED 沿用 |
| T05 错技能/无项目权限接单 | sourceOk 守卫未改 | 保留 BLOCKED |
| T06 经理改派 SCHEDULED → 旧技工拒 | D05 补 role/skill 实时校验 | 旧 assignee 开工被拒 |
| T08 安装位置/服务空间分离 | sourceOk 守卫未改 | 保留 |
| T09 缺项/时窗/旧技工 | D05 修复 | 当前承接者撤角色/技能拒 |
| T11 并发确认重叠 | D03 修复 + hasTechConflict 数组排除 | 锁内重读（runCommandBound 顺序） |
| T12 待确认改约/旧 CONFIRMED | D02 修复 | CONFIRMED + PROPOSED 同任务可一并被替换 |
| T14 上海日期换算 UTC | D01 r2 CLOSED | 保留 |
| T15 旧 version 409 | runCommandBound 未改 | 保留；D03 改原语不影响 |
| T35 改派/改约旧 AI 失效 | D04 修复 | 失效不再依赖 last_confirmed>0 |
| U04 改约/冲突/过期 | D02 修复 | 旧 CONFIRMED 改约不再自冲突 |
| U05 安装位置/服务空间 | sourceOk 守卫未改 | 保留 + 起点路径 D05 加强 |

---

## 5. 候选清单核心字段

```json
{
  "candidate_id": "M4-r3-worktree",
  "base_candidate_id": "M4-r2-worktree",
  "head": "WORKTREE-UNCOMMITTED",
  "module": "M4",
  "modified_files": ["app/bundle/main.splash"],
  "test_counts": {
    "fix_verifier":   {"passed": 18, "total": 18},
    "behavior_probe": {"passed": 13, "total": 13},
    "TOTAL":          {"passed": 31, "total": 31}
  },
  "host_started": false,
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 6. 仍未完成 / BLOCKED / NOT_RUN

- **D-M3-01/03/04/06 仍挂账**；本轮不修
- **M2 D-M2-01..07 BLOCKED**；M4 仅消费 runCommandBound
- **BLOCKED** 桌面 launcher = sandbox-exec rc71 + pgrep rc3 UNKNOWN；不启动宿主
- **NOT_RUN** 真实键鼠 / 中文人输入 / 视口 / 接单 receipt-of-action / 重启恢复 / 失败注入
- **NOT_RUN** 真实模型 provider；G0-E 沿用延期
- **NOT_RUN** 真实工件 picker；M5 不在本轮
- **A-M4-01/02/03** 仍挂账；按 r2 不属 P1，未触动
- **原生 T/U 完整用例** 仍 BLOCKED（需解 launcher sandbox 隔离）；源码路径已按 r2 方案闭合

---

## 7. 衔接

- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review
- 不进入 M5；完成交接后停止，等待独立 Review
- 所有 r3 数据落 `runtime/optimization/2026-10-09/M4/r3/`；`~/.octosense` 未访问

NEEDS_ABRAM=no（不申请 AppHub publish / 公开签名 / listing；不申请真实模型 provider；不动业务身份源头；不动公网部署；不动 M0/M1/M2/M3 BLOCKED；本轮修复不引入新授权需求）
