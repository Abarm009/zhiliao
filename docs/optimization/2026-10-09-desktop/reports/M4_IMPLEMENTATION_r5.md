# M4 实施报告 r5 · D-M4-03 / D-M4-04 严格按 r4 Review 方案逐条闭合（修复轮）

**状态：READY_FOR_REVIEW；本轮严格按 r4 Review 缺陷清单 D-M4-03 / D-M4-04 修复；不触动 M3 FAIL/M2 BLOCKED；不进入 M5。**

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | r4 Review 的 2 条 P1 必修缺陷（D-M4-03 / D-M4-04） | 严格按方案修复，不发散 |
| M0/M1/M2/M3 | FAIL/BLOCKED 沿用 | 本轮不修 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN | 不启动宿主；不调 --help |
| 真实 provider | NOT_RUN | 不申请激活 |
| A-M4-01/02/03 | P2 建议挂账 | 未触动 |
| D-M4-01 / D-M4-02 / D-M4-05 | r4 已 CLOSED 源码子范围 | 不触动 |

---

## 1. 缺陷逐条修复（按 r4 编号）

### 1.1 D-M4-03 · 预约边界接线修复 + 锁诚实化保留

**r4 触发（精确范围）**：
1. `let _cc = STATE.m4_cross_check; STATE.m4_cross_check = nil; if _cc != nil { let cc = STATE.m4_cross_check ... }` — r4 把 spec 拷到本地并清零全局后，spec-handling 块却又从 STATE 读，STATE 已被清零，cc 必 nil，runCommandBound 整段被新代码阻断。
2. spec save+clear 放在 sourceOk 通过之后，idem_conflict / cross_project / version_mismatch / concurrency_lost / source_state_invalid 等早期退出路径仍把 spec 留在全局，污染下一次命令。
3. 锁 `fs.write(tasks.lock, stamp)` 无条件覆盖，release 无条件写空，连进程内重入保护也不存在；readback 后 read→write 竞争窗口内当前写的 stamp 已被他人覆盖。

**r5 修复（严格按 r4 方案）**：

1. **spec save+clear 前移到入栈入口**。在 `runCommandBound` 入口（authorizeCommand 之后、所有早期拒绝路径之前）执行：
   ```
   let _cc = STATE.m4_cross_check
   STATE.m4_cross_check = nil
   ```
   之后任何早期退出路径（idem_conflict / cross_project / version_mismatch / concurrency_lost / source_state_invalid）都会使 STATE.m4_cross_check = nil，spec 不再污染下一次命令。
2. **spec-handling 块使用本地 _cc，不再读 STATE**：
   ```
   if _cc != nil {
       let cc = _cc    // r4 bug 修复
       ...
   }
   ```
   r4 错误模式 `let cc = STATE.m4_cross_check` 已不存在。
3. **锁诚实化保留**。`_acquireTaskLock` / `_releaseTaskLock` 体内 `fs.rename` = 0（仍 HOST_PRIMITIVE_BLOCKED，跨进程原子需宿主 fs 升级）；函数体内显式标注 HOST_PRIMITIVE_BLOCKED 注释，便于静态扫描锁定诚实状态。

**证据**：
- `evidence/source_probe.json`：45 项源码契约检查，**45/45 PASS**。
  - `D-M4-03.r5.spec_clear_before_{idem_conflict,cross_project,version_mismatch,concurrency_lost,source_state_invalid}` —— 5 条早期退出路径都被覆盖。
  - `D-M4-03.r5.spec_block_uses_saved_local` —— `let cc = _cc` 存在。
  - `D-M4-03.r5.no_buggy_re_read` —— r4 bug 模式已消失。
  - `D-M4-03.r5.authorizeCommand_first` —— D-M2-01 不破。
  - `D-M4-03.acquire_documents_blocked` —— 函数体内显式 HOST_PRIMITIVE_BLOCKED 注释。
  - `D-M4-03.acquire_no_rename` / `release_no_rename` —— 0 个 fs.rename。
- `results/behavior_probe.json`：16 项算法行为仿真，**16/16 PASS**。
  - `D-M4-03.r5.cross_task_overlap_detected` —— 跨任务重叠可检出。
  - `D-M4-03.r5.adjacent_slot_no_conflict` —— 相邻时段允许。
  - `D-M4-03.r5.same_task_excluded_id_no_conflict` —— exclude_ids 不自冲突。
  - `D-M4-03.r5.cross_task_proposed_caught` —— PROPOSED 也被命中。
  - `D-M4-03.r5.save_then_use_local` —— saved local 即使 STATE 被清仍可用。
  - `D-M4-03.r5.source_uses_local_cc` —— 源码使用 local _cc 而非 STATE 重读。
- `results/lock_probe.json`：7 项锁诚实化 + 边界重读复现，**7/7 PASS**。
  - 多进程 rename 复现：4 PID 各自看到不同 stamp，read-back 仍 racy。
  - `D-M4-03.r5.spec_cleared_on_every_early_exit` —— 6 条早期退出路径（authorizeCommand / idem_conflict / cross_project / version_mismatch / concurrency_lost / source_state_invalid）模拟：每条路径 spec 在全局都被清零。
  - `D-M4-03.r5.boundary_re_read_catches_race` —— 边界 disk 重读捕到跨任务冲突。
  - `D-M4-03.r5.no_buggy_re_read_of_state_cross_check` —— r4 bug 模式已不存在。

**HOST_PRIMITIVE_BLOCKED 诚实说明**：
- r4 独立 Review 已确认宿主 fs 模块不注册 rename / O_EXCL / flock；r5 不再以 rename 模拟 CAS，跨进程真原子需宿主 fs 升级。
- `sandbox-exec rc71 + pgrep rc3` 解阻后，真业务并发需在指定宿主重新实证。
- 不引入未裁决的 Python 业务服务；不 reset / 不覆盖他人的 r4 改动。

---

### 1.2 D-M4-04 · 失效拆 AI 绑定 + 显式 rebinding 守卫

**r4 触发（精确范围）**：
- AI 草稿问题 A / 来源 ai / 历史原文 A（输入版本1）已 APPLIED。
- `m4_invalidateConfirmation("reassign")` 仅把 PENDING_DRAFT 标记 EXPIRED + AI_STATE=EXPIRED + invalidated_by_edit=true；**PENDING_DRAFT 上的 AI 绑定（last_applied_request_id / ai_history_raw_text_hash / expires_at_ms 等）原样保留**。
- 用户仅把原文改为问题 B（版本2）再确认——`raw_input_version++`，越过 r4 snapshot，r4 路径放行。
- 实际：confirmed=true，**仍 problem=旧AI问题A、source=ai、history=A、history_version=1**，但 raw=新的问题B、raw_version=2。
- 预期：旧proposal/旧确认保持撤销；新人工或新AI内容经明确核对当前主体/授权事实/任务及输入版本后形成新绑定，再继续。

**r5 修复（严格按 r4 方案）**：

1. **`m4_invalidateConfirmation` 把 PENDING_DRAFT 上的 AI 绑定整体拆掉**：
   ```
   PENDING_DRAFT.last_applied_request_id = ""
   PENDING_DRAFT.ai_request_id = ""
   PENDING_DRAFT.expires_at_ms = 0
   PENDING_DRAFT.ai_history_raw_text = ""
   PENDING_DRAFT.ai_history_raw_text_hash = ""
   PENDING_DRAFT.ai_history_raw_input_version = 0
   PENDING_DRAFT.draft_source = "manual"
   ```
   把 draft_source 强制设为 "manual"，使 `editRawText` 的 auto-promote 分支（仅在 draft_source == "ai" 时把 "problem" 推入 human_edited_fields）也被堵死——后续真正修改只能走 `editDraftField` 路径。
2. **`confirmDraftModelBound` 在 snapshot 恢复之上叠加 rebinding 守卫**：
   - snapshot 恢复（r4 保留）：`_draft_moved || _raw_moved` 放行。
   - **新增 rebinding 守卫**：必须满足下列任一：
     - **(a) AI 重新生成并落地** —— `PENDING_DRAFT.last_applied_request_id != ""` **且** `PENDING_DRAFT.ai_history_raw_text_hash == TASK_INPUT.raw_text_hash`。
     - **(b) 关键字段已通过 `editDraftField` 显式重填** —— `human_edited_fields` 同时包含 `problem` / `space_id` / `category`。
   - 两条都不满足 → reject：AI_LAST_ERROR = "失效已被作废；请重新请求 AI 或手工填写 problem/space/category 后再确认"。
3. **旧失效审计保留**：`STATE.m4_invalidations.last_invalidate_*` 字段未触动；r4 的 `invalidate_snapshots_draft_version` / `invalidate_snapshots_raw_input_version` 守卫继续生效。
4. **不破坏合法场景**：
   - fresh confirm（未失效）→ 直接 pass（not_invalidated）。
   - close-then-reopen（CONFIRM_BIND.invalidated_by_edit 被重置为 false）→ 直接 pass。
   - 失效后真正走 AI 重新生成（applyDraftFromAI 设置新 last_applied_request_id 与 ai_history_raw_text_hash）→ pass。
   - 失效后用户主动在面板编辑 problem/space_id/category（editDraftField 推入 human_edited_fields）→ pass。

**证据**：
- `evidence/source_probe.json`：45/45 PASS，含 r5 新增 12 条 D-M4-04 守卫检查：
  - `D-M4-04.r5.invalidate_clears_last_applied_request_id` / `_clears_ai_request_id` / `_clears_expires_at` / `_clears_ai_history_raw_text` / `_clears_ai_history_raw_text_hash` / `_clears_ai_history_raw_input_version` / `_sets_draft_source_manual` —— 7 条 m4_invalidateConfirmation AI 绑定清除检查。
  - `D-M4-04.r5.confirm_has_rebinding_gate` —— 显式 `_rebound` 变量存在。
  - `D-M4-04.r5.confirm_rebinding_allows_new_ai_hash_match` —— 新 AI 哈希匹配路径。
  - `D-M4-04.r5.confirm_rebinding_requires_human_refill` —— 手工重填 problem+space_id+category 路径。
  - `D-M4-04.r5.confirm_rejects_when_not_rebound` —— 显式拒绝文案。
- `results/behavior_probe.json`：16/16 PASS，含 10 条 D-M4-04 行为仿真：
  - `D-M4-04.r5.fresh_no_invalidator_confirm` —— fresh 通过。
  - `D-M4-04.r5.keystroke_after_invalidation_rejected` —— 单 keystroke（**r4 bug 修复点**）：拒绝 needs_rebinding。
  - `D-M4-04.r5.stale_reconfirm_rejected` —— 无编辑 stale 拒绝（保留）。
  - `D-M4-04.r5.re_ai_applied_recovers` —— AI 重生成恢复。
  - `D-M4-04.r5.manual_refill_recovers` —— 三关键字段显式重填恢复。
  - `D-M4-04.r5.partial_refill_rejected` —— 仅 problem 拒绝。
  - `D-M4-04.r5.keystroke_from_zero_no_rebinding_rejected` —— 0→1 键入无 rebinding 拒绝。
  - `D-M4-04.r5.close_then_reopen_no_invalidator_confirms` —— close 重置放行。
  - `D-M4-04.r5.invalidate_stores_snapshots` —— 快照存储保留。
  - `D-M4-04.r5.invalidate_clears_ai_binding_on_pending_draft` —— PENDING_DRAFT AI 绑定清除。

---

## 2. 改动文件清单（仅一处主源 + r5 脚本）

| 文件 | 改动摘要 |
|---|---|
| `app/bundle/main.splash` | 仅本轮 2 个缺陷对应函数 / 边界 / 守卫；其他函数原样 |
| `runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_fix_verifier.py` | 45 项源码契约检查（D-M4-03 r5 + D-M4-04 r5） |
| `runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_behavior_probe.py` | 16 项算法行为仿真 |
| `runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_lock_repro.py` | 7 项锁诚实化重读 + 边界兜底复现 + spec save+clear 模拟 |
| `runtime/optimization/2026-10-09/M4/r5/CANDIDATE.json` | r5 候选清单 |
| `runtime/optimization/2026-10-09/M4/r5/evidence/source_probe.json` + `results/*.json` | 证据落盘 |
| `docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r5.md` | 本报告 |

主源 SHA-256 变化：
- 前（M4-r4）：`8b3c589a7c360a3a34e9a9d1f6c5e6c104357e3958e073769dbd03ed7ca6800c`（332548 字节 / 7268 行）
- 后（M4-r5）：`dcf73555767c895ac04a8a5904246f9635b21481ac9f4e07b14cc13709e3d006`（388582 字节 / 8330 行）

字节 / 行数变化仅为本轮 2 个缺陷对应函数 / 边界 / 守卫的 diff 累计。

---

## 3. 启动 / 重跑

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_fix_verifier.py
python3 runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_behavior_probe.py
python3 runtime/optimization/2026-10-09/M4/r5/scripts/m4_r5_lock_repro.py
```

实测：
- `fix_verifier`：45/45 PASS
- `behavior_probe`：16/16 PASS
- `lock_repro`：7/7 PASS
- 合计：68/68 PASS

隔离数据全部落在 `runtime/optimization/2026-10-09/M4/r5/` 与 `tempfile.mkdtemp()`；`~/.octosense` 未访问；HOST LAUNCHER 未启动。

---

## 4. r4 既有用例的状态变化（仅 P1 必修）

| 编号 | r4 状态 | r5 状态 | 备注 |
|---|---|---|---|
| T04 双独立连接抢同 OPEN | D-M4-03 FAIL | HOST_PRIMITIVE_BLOCKED 保留；spec save+clear 前移到入栈；spec-handling 用 local _cc | 跨进程原子仍依赖宿主原语 |
| T11 同技工重叠并发 | D-M4-03 FAIL | 边界权威重读检测跨任务冲突；进程内可证 | 同上 |
| T12 待确认改约 / 旧预约有效 | D-M4-02 r4 CLOSED | 保留 | r5 不动 |
| T35 改派/改约旧 AI 失效 | D-M4-04 r4 PARTIAL | PENDING_DRAFT AI 绑定清除 + rebinding 守卫；单 keystroke 复活旧 AI 已不可达 | r5 闭合 |
| U04 改约/冲突/过期 | D-M4-02 r4 CLOSED + D-M4-04 r5 闭合 | 保留 | |

---

## 5. 候选清单核心字段

```json
{
  "candidate_id": "M4-r5-worktree",
  "base_candidate_id": "M4-r4-worktree",
  "head": "WORKTREE-UNCOMMITTED",
  "module": "M4",
  "modified_files": ["app/bundle/main.splash"],
  "test_counts": {
    "fix_verifier":   {"passed": 45, "total": 45},
    "behavior_probe": {"passed": 16, "total": 16},
    "lock_repro":     {"passed":  7, "total":  7},
    "TOTAL":          {"passed": 68, "total": 68}
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
- **BLOCKED HOST_PRIMITIVE_BLOCKED**：跨进程原子互斥在选定宿主内无可验证原语；r5 锁为 in-process advisory，凭 `commitBound(expected_version)` + `runCommandBound` 入口 spec save+clear + 边界权威重读 + receipt of needs_verify 三层兜底保证；后续若宿主 fs 升级暴露 O_EXCL / flock，可重写。
- **NOT_RUN** 真实键鼠 / 中文人输入 / 视口 / 接单 receipt-of-action / 重启恢复 / 失败注入
- **NOT_RUN** 真实模型 provider
- **NOT_RUN** 真实工件 picker；M5 不在本轮
- **A-M4-01/02/03** 仍挂账；按 r4 不属 P1，未触动
- **原生 T/U 完整用例** 仍 BLOCKED（需解 launcher sandbox 隔离）；源码路径已按 r4 方案闭合

---

## 7. 衔接

- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review
- 不进入 M5；完成交接后停止，等待独立 Review
- 所有 r5 数据落 `runtime/optimization/2026-10-09/M4/r5/`；`~/.octosense` 未访问

NEEDS_ABRAM=no（不申请 AppHub publish / 公开签名 / listing；不申请真实模型 provider；不动业务身份源头；不动公网部署；不动 M0/M1/M2/M3 BLOCKED；HOST_PRIMITIVE_BLOCKED 不引入新的对外授权需求；继续 host primitive 解阻后再讨论宿主 fs 升级的来源）