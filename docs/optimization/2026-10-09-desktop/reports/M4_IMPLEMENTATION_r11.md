# M4 实施报告 r11

- 模块 / 目标：M4 接单设备与预约桌面流程 · r12 修复轮（审查输入 M4_REVIEW_r12，FAIL，唯一必修 D-M4-03）。
- candidate_id / base_candidate_id：**M4-r11-worktree / M4-r10-worktree**。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD `8d730569546cb57310944bb299695134df773b9d`（dirty，含他人改动，全部保留）。`app/bundle/main.splash` = **765252 B / SHA-256 `ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e`**（r12 审查冻结源为 657584 B / `c37e31e6…`；差量为其他模块修复轮在共享工作树的推进，M4 本轮 hunks=0，按 10:45 规则从当前工作树重新冻结候选）。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主经 harness 默认 BIN（现为 host-rc6/app-extracted/OctoSense.app，Abram 16:45 批准切换）；构建方不启动宿主，原生验证由驱动沙箱外执行。
- 实际模型路由检查结果（开发会话）：当前构建方为 Kimi-K3（Abram 2026-10-11 21:03 指定）；无工具核验 Router 内部路由，不声称切换。
- 已检查的前置 PASS 报告：无新 PASS。M3 前置仍 FAIL（M3_REVIEW_r12/r14 挂账），M4 仅消费契约不修；本模块 r12 六场冷开子项 PASS 沿用，不代业务动态。
- 本轮修改文件与原因：
  1. `M4/r11/scripts/m4_r11_guard_verifier.py`（新增）——D-M4-03 BLOCKED-HOST 裁决下「安全拒写并保源」守卫盘点核验；
  2. `M4/r11/evidence/guard_verifier.json`（新增，已实际运行 rc=0，41/41）；
  3. `M4/native/prepare_build_r11.py` + `M4/native/build_r11/`（新增）——digest 变化后的授权离线签名 store，私钥已删；
  4. `M4/native/REQUEST_build_r11.json`（新增）——harness 原生验证请求，待驱动执行；
  5. `M4/r11/CANDIDATE.json`、本报告、GATES.json M4 作者字段、CONTEXT_M4.md r11 速记。
  **业务源码 / 宿主 / harness / 界面 0 改动。**
- 桌面 UI/交互变化：无。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化。
- 已有别人修改的保留与适配：共享工作树 main.splash 自 r12 冻结源推进了 107668 B（M2 hf_* 恢复事务、M5/M6/M7 修复等），全部保留；本轮守卫核验按函数名定位而非行号，确认 M4 相关守卫在他人改动后仍完好。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。离线签名与 seed 全部在 `runtime/optimization/2026-10-09/M4/native/build_r11/`（沙箱内隔离 HOME/TMP）；原生证据待驱动落 `M4/native-runs/build_r11_*/`。
- 应用运行模型/provider：needs_model=false，本轮 MiniMax 0 调用；无密钥接触。

## 本轮范围裁定（先于一切修复动作）

r12 唯一必修 **D-M4-03** 的审查方改法要求宿主原子替换/持有期锁/CAS 原语。**Abram 2026-10-13 BLOCKED-HOST 裁决**（依据 HARDFIX_PLAN.md §0 第 22–28 行）：固定宿主不提供这两项能力，D-M4-03 记 **BLOCKED-HOST** 单独挂账，不再算 FAIL、不再列为 P1，审查不得因此判 FAIL；**代码仍须保持安全拒写并保源**。叠加 13:14 硬规则（不扩展功能），本轮 M4 唯一可执行项 = 实证安全拒写/保源守卫在当前工作树未回归 + 重新冻结候选交接。

## D-M4-03 守卫盘点核验（41/41，evidence/guard_verifier.json）

按函数级模式核验当前 765252 B 工作树（行号已因他人改动漂移，不锁行号）：

- `_acquireTaskLock`（当前 :6288）：fs.exists 区分首次缺锁与真实读失败（read_failed fail-closed）；重入仅完整 token 全等；未知/不可解析锁戳拒且不清锁（held_by_other_unknown）；非过期他人锁拒；仅 ≥300000ms stale 回收；写后读回校验丢锁显式 lost；token 绑定本进程持有实例。
- `_releaseTaskLock`（:6359）：无 token / 读失败 / 内容不全等一律不动他人锁。
- `_m4_disk_tech_conflict`（:6396）：盘存在但读/解析失败 = error（fail-closed）；重叠严格 `start < other.end && end > other.start`（相邻不算）；仅 A_CONFIRMED/A_PROPOSED 同技工。
- `runCommandBound`（:6455）：`_cc` 拷清在 authorizeCommand 之前（r6 修复保持）；M2_ACTIONS_DIRTY/EVENTS_DIRTY 脏历史冻结；hf_recovery_pending 与 tasks_pending_recovery 双恢复屏障；先抢锁。
- `commitBound`（:6715）：_PENDING_CC 进入即清零；提交点本进程未持锁/锁缺失/锁读失败/锁非本 token 一律 needs_verify 不写盘；盘版本漂移复核；创建前盘不可解析 fail-closed；跨任务冲突复核推进到写盘前最后一刻；tmp 写失败/主写失败/读回非全等（`rb.to_json()==t.to_json()`）均 needs_verify；恢复未决拒主写（R-M7-02 保持）；final 回执须精确命中 action_id；出口统一放锁。
- `m7_tasks_strict_parse` / `m7_tasks_mark_corrupt`（B-M4-01 保源门禁保持）；`m4_invalidateConfirmation`（D-M4-04 epoch 失效保持）。

## A-M4-R12-01 文案更正（建议项，仅报告层面落实）

审查方指出 r10 报告两处文案与实际运行形态不符，本报告如实更正（不改业务代码、不回改 r10 历史证据）：
1. r10 复现 Part B2 的 B 方迟到提交，实际返回是**版本先变化导致的 needs_verify**，不是 r10 报告所写的 rejected_stale_fence；
2. r10 Part C-preempt 用的是**同进程两个 thread**，多进程实证是 Part C2（8 进程×200 轮 flock）。
r10 证据文件（atomic_fencing_repro.json）保持原样不改；以上更正仅影响文字描述，方案结论（O_EXCL+TTL 单独不足、需 fencing 或持有期 OS 锁）不变，且该路线已由 BLOCKED-HOST 裁决挂账。

## 验收项覆盖表

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r11 场 1：digest ddd0eb06 冷启动|零解析/运行错误、登录页真实渲染、tick 异常 0|待驱动沙箱外执行|**NOT_RUN（已提交请求）**|M4/native/REQUEST_build_r11.json；证据待落 M4/native-runs/build_r11_*/|
|权威状态与回执|守卫盘点核验（当前工作树）|D-M4-03 安全拒写/保源守卫完好|41/41 PASS|PASS（静态，源码级）|M4/r11/evidence/guard_verifier.json|
|失败与重试|commitBound/acquire 拒写路径|needs_verify 不写盘、fail-closed|源码核验在案（CB-03..15、ACQ-02..07）|PASS（静态）；动态 NOT_RUN|同上|
|重启恢复|REQUEST_build_r11 场 2：future 他人锁 boot|锁逐字保留、token 空、pending=false|待驱动执行|**NOT_RUN（已提交请求）**|同上|
|受影响先前模块回归|冷启动渲染回归场|解析错误 0 不回归|待驱动执行|**NOT_RUN（已提交请求）**|同上|

## 尚未完成

- **D-M4-03 = BLOCKED-HOST**（Abram 2026-10-13 裁决）：真原子命令边界需宿主原子替换 + 持有期锁，固定宿主不提供；脚本侧安全拒写/保源守卫保持（本轮 41/41 实证），真互斥与原生双上下文并发验证挂账。
- 原生业务主链（M3 创建→接单→设备→预约→开工）、可信登录后三角色动态、真正同盘双上下文并发：仍 NOT_RUN/BLOCKED（harness 无同盘双上下文+提交点同步入口；固定宿主 type/key 未实现），沿用 r12 挂账边界，本轮无变化。
- REQUEST_build_r11 两场原生结果：待驱动执行后回读，本报告不预判。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M4/r11/CANDIDATE.json`（candidate_id=M4-r11-worktree，digest `ddd0eb06…`，anchor `8d7c22db…`）。
- 证据：`M4/r11/evidence/guard_verifier.json`（41/41）、`M4/native/build_r11/offline-store-evidence.json`（私钥 working.key/anchor.key 已删 exists_after=false，keys 目录空）。
- 原生请求：`M4/native/REQUEST_build_r11.json`（2 场，needs_model=false，无 wait:N）。
- 实际测试命令：`PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/optimization/2026-10-09/M4/r11/scripts/m4_r11_guard_verifier.py`（rc=0）；`…/M4/native/prepare_build_r11.py`（rc=0，PREPARED）。
- 编码方标 READY_FOR_REVIEW；最终 PASS 等待独立审查。本轮无 AppHub publish、无 push、无公网、无真实凭据/密钥接触。
