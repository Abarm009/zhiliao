# M4 实施报告 r4 · D-M4-03 / D-M4-04 严格按 r3 Review 方案逐条闭合

**状态：READY_FOR_REVIEW；本轮严格按 r3 Review 缺陷清单 D-M4-03 / D-M4-04 修复；D-M4-01/02/05 r3 已 CLOSED，不触动；不进入 M5。**

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | r3 Review 的 2 条 P1 必修缺陷（D-M4-03 / D-M4-04） | 严格按方案修复，不发散 |
| M0/M1/M2/M3 | FAIL/BLOCKED 沿用 | 本轮不修 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN | 不启动宿主；不调 --help |
| 真实 provider | NOT_RUN | 不申请激活 |
| A-M4-01/02/03 | P2 建议挂账 | 未触动 |
| D-M4-01 / D-M4-02 / D-M4-05 | r3 已 CLOSED 源码子范围 | 不触动 |

---

## 1. 缺陷逐条修复（按 r3 编号）

### 1.1 D-M4-03 · 锁诚实化 + 跨任务边界权威重读

**r3 触发**：
- `_acquireTaskLock` 依赖 `fs.rename` 抢占锁文件。r3 Review 实测两个独立 PID 都 acquired=true（A、B 同时持锁）；A 释放会挪走 B 当前锁。
- 即使修锁，`confirmAppointment` 冲突循环仍在 `runCommandBound` 之前只读内存 `TASKS`；边界只查目标任务的 `version`，另一任务预约变化不会令该 `version` 变化 → 真正的并发预约冲突可绕过。
- r3 Review 明确要求：若宿主无可验证原子互斥原语，不得继续以 rename/readback 模拟 CAS；若无可验证原语，交付可运行最小复现并明确 BLOCKED，不得引入未经裁决的 Python 业务服务。

**r4 修复（严格按 r3 方案）**：

1. `_acquireTaskLock`：放弃 fs.rename；改为单次 `fs.write("tasks.lock", stamp)`。函数注释标记 `HOST_PRIMITIVE_BLOCKED`——本实现为进程内建议锁（in-process advisory），不再宣称任何跨进程原子互斥。
2. `_releaseTaskLock`：放弃 fs.rename；仅写空字符串作"已释放"标记。同 `HOST_PRIMITIVE_BLOCKED` 注释。
3. 跨进程真原子互斥依靠以下兜底：
   - `commitBound(expected_version)`：写后核对 `t.version != expected_version + 1` 标 needs_verify（沿用 M2）。
   - `runCommandBound` 内新增"D-M4-03 (r4) 跨任务跨项目同技工冲突重读"。appointment 系命令（confirmAppointment / proposeAppointment / rescheduleAppointment / cancelAppointment）在调用 `runCommandBound` 前先把冲突上下文写入 `STATE.m4_cross_check = {tech, startMs, endMs, exclude_ids}`。`runCommandBound` 入栈立刻把 `STATE.m4_cross_check` 拷到本地 `_cc` 并清零全局（避免早期退出路径漏清导致下次命令误用旧 spec），然后：
     - 在 sourceOk 通过之后、`runCommand` 调用之前，权威重读 `tasks.json`（`fs.read("tasks.json").parse_json()`）。
     - 对 `_disk_tasks` 内的每个 task / appointment 做跨任务重检：同任务内排除 `exclude_ids`；其余任务的 `A_CONFIRMED / A_PROPOSED` 与 `cc_tech` 比对，时间区间半开重叠（`startMs < end && endMs > start`）即冲突。
     - 命中冲突 → 释放锁、写 `tech_conflict` receipt、fail 并 `return false`；旧任务/预约/历史均不变（调用方 `if !runCommandBound { return }` 自然不进入 mutate 路径）。
4. `confirmAppointment` / `proposeAppointment` / `rescheduleAppointmentFromForm` 各在调用 `runCommandBound` 前 `STATE.m4_cross_check = {...}`。
5. `_acquireTaskLock`、`_releaseTaskLock` 改写后体内 `fs.rename` 调用数 = 0（源探针确认）。

**HOST_PRIMITIVE_BLOCKED 诚实说明**：
- r3 独立 Review 已确认宿主 fs 模块不注册 rename / O_EXCL / flock；r4 不再以 rename 模拟 CAS，跨进程真原子需宿主 fs 升级。
- `sandbox-exec rc71 + pgrep rc3` 解阻后，真业务并发需在指定宿主重新实证。
- 不引入未裁决的 Python 业务服务；不 reset / 不覆盖他人的 r3 改动。

**证据**：
- `evidence/source_probe.json`：`_acquireTaskLock` / `_releaseTaskLock` 零 fs.rename、`HOST_PRIMITIVE_BLOCKED` 注释、`runCommandBound` 含 `_disk_tasks` / `A_CONFIRMED / A_PROPOSED` 判定、`tech_conflict` receipt；三个 appointment 命令各含 `STATE.m4_cross_check = ` 赋值。
- `evidence/behavior_probe.json`：
  - `cross_task_disk_recheck_overlap_detected`：1500-2500 与 ap-B-1（1000-2000）成功检出冲突。
  - `adjacent_slot_no_conflict`：2000-3000 相邻时段允许。
  - `same_task_excluded_id_no_conflict`：exclude_ids 内的同任务预约不与自身冲突。
  - `cross_task_proposed_also_caught`：跨任务 PROPOSED 也能被边界重读命中。
  - `lock_marks_HOST_PRIMITIVE_BLOCKED` / `lock_no_longer_calls_rename`。
- `results/lock_probe.json`：4 个独立 PID 同时跑 r3 的 fs.rename 抢占模式；其中只有 1 个 PID 在 read-back 看见自己的 stamp，其余已被对端 rename 覆盖。这与 r3 独立 Review 的发现一致，本轮显式记为"最小可运行复现"以满足 r3 "交付最小复现并明确 BLOCKED" 的要求（不再以 rename 模拟 CAS）。

### 1.2 D-M4-04 · 版本快照恢复路径

**r3 触发**：
- `editRawText` 在每次内容变化时无条件置 `CONFIRM_BIND.invalidated_by_edit = true`（D-M3-03 的副作用）。这导致用户手工键入/修改后点确认，命中 `if CONFIRM_BIND.invalidated_by_edit == true { reject }` 直接被拒；
- 关闭 / 重新打开面板 / 重填新内容再确认，仍被同一无条件 raise 拒——形成"重新点击也拒"的死循环。
- r3 Review 明确要求：分别记录失效旧 proposal / 旧确认与当前编辑版本；提供"核对更新内容并重新确认"入口，在新版本上刷新主体 / 授权事实 / 到期 / 任务版本并形成新绑定；只在核验成功后消费，保留旧失效审计；不要无条件清旧 AI 标记绕过安全守卫，也不要要求清空所有输入重新填。

**r4 修复（严格按 r3 方案）**：

1. `STATE.m4_invalidations` 新增两个快照字段（m4_init_forms 兜底补字段）：
   - `last_invalidate_draft_version`：`PENDING_DRAFT.draft_version` 在失效那一瞬的值。
   - `last_invalidate_raw_input_version`：`TASK_INPUT.raw_input_version` 在失效那一瞬的值。
2. `m4_invalidateConfirmation`：在置 `CONFIRM_BIND.invalidated_by_edit = true` **之前**，先把 `PENDING_DRAFT.draft_version` 与 `TASK_INPUT.raw_input_version` 拷到上述字段；后续仍走原有 `APPLIED → EXPIRED`、`active = false` 等副作用。
3. `confirmDraftModelBound`：将"是否拒绝失效"判别改为版本比较：
   - `_snap_d = STATE.m4_invalidations.last_invalidate_draft_version`
   - `_snap_r = STATE.m4_invalidations.last_invalidate_raw_input_version`
   - `_cur_d = PENDING_DRAFT.draft_version`；`_cur_r = TASK_INPUT.raw_input_version`
   - `_draft_moved = (_cur_d > _snap_d)`；`_raw_moved = (_cur_r > _snap_r)`
   - 若 `!(_draft_moved || _raw_moved)`（既无 draft 编辑也无 raw input 编辑）→ 维持原拒绝文案 "请重新确认更新后的内容"；否则放行。
4. 成功路径保持原状：仅在 `createDraftFromPanel()` 成功后通过尾部 `CONFIRM_BIND.invalidated_by_edit = false` 复位；不允许提前复位绕过 r3 的安全守卫。
5. 旧的"无条件置 invalidated=true"保留（D-M3-03 stale input guard 需要），但与版本快照组合后不再形成"重新点击也拒"的死循环——只要用户在新内容下走过至少一次编辑，版本必然越过快照。

**验证**：
- `evidence/source_probe.json`：m4_invalidateConfirmation 含 `_snap_draft` / `_snap_raw` 写快照；confirmDraftModelBound 含 `_draft_moved || _raw_moved` 比较；m4_init_forms 含两个 snapshot 字段；reset 仍保留。
- `evidence/behavior_probe.json`：
  - `fresh_no_invalidator_confirm`：从未失效过 → 直接 pass，not_invalidated。
  - `invalidator_then_keystroke_recovers`：失效后打一个字 → raw_input_version 越过快照 → recovery 开。
  - `invalidator_then_stale_reconfirm_rejected`：失效后无任何编辑 → 拒绝并给 stale_reconfirm。
  - `invalidator_then_draft_edit_recovers`：失效后改草稿字段（draft_version+1）→ recovery 开。
  - `invalidator_from_zero_with_first_keystroke_recovers`：version=0 的初态经一次键入 → recovery 开。
  - `close_then_reopen_no_invalidator_confirms`：close 后 invalidated 标记复位，再 confirm 不命中失效分支。
  - `invalidate_stores_snapshots`：快照字段确实被写入。

---

## 2. 改动文件清单（仅一处主源 + r4 脚本）

| 文件 | 改动摘要 |
|---|---|
| `app/bundle/main.splash` | 仅本轮 2 个缺陷对应函数 / 边界 / 守卫；其他函数原样 |
| `runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_fix_verifier.py` | 26 项源码契约检查（D-M4-03 + D-M4-04） |
| `runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_behavior_probe.py` | 13 项算法行为仿真 |
| `runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_lock_repro.py` | 4 项锁诚实化重读 + 边界兜底复现 |
| `runtime/optimization/2026-10-09/M4/r4/CANDIDATE.json` | r4 候选清单 |
| `runtime/optimization/2026-10-09/M4/r4/evidence/*.json` + `results/*.json` | 证据落盘 |
| `docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r4.md` | 本报告 |

主源 SHA-256 变化：
- 前（M4-r3）：`4c753154cf55fb5912a53a5f09425c54bcc5787ee5e54d5d1f82cd8096a50f13`（324049 字节 / 7130 行）
- 后（M4-r4）：`8b3c589a7c360a3a34e9a9d1f6c5e6c104357e3958e073769dbd03ed7ca6800c`（332548 字节 / 7268 行）

字节 / 行数变化仅为本轮 2 个缺陷对应函数 / 边界 / 守卫的 diff 累计。

---

## 3. 启动 / 重跑

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_fix_verifier.py
python3 runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_behavior_probe.py
python3 runtime/optimization/2026-10-09/M4/r4/scripts/m4_r4_lock_repro.py
```

实测：
- `fix_verifier`：26/26 PASS
- `behavior_probe`：13/13 PASS
- `lock_repro`：4/4 PASS

隔离数据全部落在 `runtime/optimization/2026-10-09/M4/r4/` 与 `tempfile.mkdtemp()`；`~/.octosense` 未访问；HOST LAUNCHER 未启动。

---

## 4. r3 既有用例的状态变化（仅 P1 必修）

| 编号 | r3 状态 | r4 状态 | 备注 |
|---|---|---|---|
| T04 双独立连接抢同 OPEN | D-M4-03 FAIL | HOST_PRIMITIVE_BLOCKED；边界权威重读 + commitBound 版本兜底 | 跨进程原子仍依赖宿主原语 |
| T11 同技工重叠并发 | D-M4-03 FAIL | 边界权威重读检测跨任务冲突；进程内可证 | 同上 |
| T12 待确认改约 / 旧预约有效 | D-M4-02 r3 CLOSED | 保留 | r4 不动 |
| T35 改派/改约旧 AI 失效 | D-M4-04 r3 PARTIAL | 失效不再依赖 last_confirmed>0；新内容可重新核对恢复 | r4 闭合 |
| U04 改约/冲突/过期 | D-M4-02 r3 CLOSED + D-M4-04 r4 闭合 | 保留 | |

---

## 5. 候选清单核心字段

```json
{
  "candidate_id": "M4-r4-worktree",
  "base_candidate_id": "M4-r3-worktree",
  "head": "WORKTREE-UNCOMMITTED",
  "module": "M4",
  "modified_files": ["app/bundle/main.splash"],
  "test_counts": {
    "fix_verifier":   {"passed": 26, "total": 26},
    "behavior_probe": {"passed": 13, "total": 13},
    "lock_repro":     {"passed":  4, "total":  4},
    "TOTAL":          {"passed": 43, "total": 43}
  },
  "host_started": false,
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 6. 仍未完成 / BLOCKED / NOT_RUN

- **D-M3-01/03/04/06** 仍挂账；本轮不修
- **M2 D-M2-01..07 BLOCKED**；M4 仅消费 runCommandBound
- **BLOCKED** 桌面 launcher = sandbox-exec rc71 + pgrep rc3 UNKNOWN；不启动宿主
- **BLOCKED HOST_PRIMITIVE_BLOCKED**：跨进程原子互斥在选定宿主内无可验证原语；r4 锁为 in-process advisory，凭 `commitBound(expected_version)` + `runCommandBound` 边界权威重读 + receipt of needs_verify 三层兜底保证；后续若宿主 fs 升级暴露 O_EXCL / flock，可重写。
- **NOT_RUN** 真实键鼠 / 中文人输入 / 视口 / 接单 receipt-of-action / 重启恢复 / 失败注入
- **NOT_RUN** 真实模型 provider
- **NOT_RUN** 真实工件 picker；M5 不在本轮
- **A-M4-01/02/03** 仍挂账；按 r3 不属 P1，未触动
- **原生 T/U 完整用例** 仍 BLOCKED（需解 launcher sandbox 隔离）；源码路径已按 r3 方案闭合

---

## 7. 衔接

- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review
- 不进入 M5；完成交接后停止，等待独立 Review
- 所有 r4 数据落 `runtime/optimization/2026-10-09/M4/r4/`；`~/.octosense` 未访问

NEEDS_ABRAM=no（不申请 AppHub publish / 公开签名 / listing；不申请真实模型 provider；不动业务身份源头；不动公网部署；不动 M0/M1/M2/M3 BLOCKED；HOST_PRIMITIVE_BLOCKED 不引入新的对外授权需求；继续 host primitive 解阻后再讨论宿主 fs 升级的来源）
