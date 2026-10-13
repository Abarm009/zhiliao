# M4 实施报告 r10

- 模块 / 目标：M4 接单设备与预约桌面流程 —— 修复轮，只修 M4_REVIEW_r11 缺陷清单唯一必修（D-M4-03），D-M4-04 SOURCE-CLOSED 保回归，B-M4-01 已由 r11 独立关闭不回退，不发散。
- candidate_id / base_candidate_id：M4-r10-worktree / M4-r9-worktree。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`（工作树 dirty，含他人改动）；`app/bundle/main.splash` SHA256=`c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421`，657584 B，与 r9 候选完全相同（本轮 bundle hunks=0）。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256=`3e127963…`，沿用 r11 审查记录）；jailed fs 方法表以 vendored `runtime/native-build/makepad/widgets/src/splash_storage.rs:242–415` 逐行核实：read/read_bytes/write/append/exists/remove/mkdir/list —— 无 O_EXCL/flock/原子 rename/CAS。
- 实际模型路由检查结果（开发会话）：本轮为修复轮，未核验主会话路由；不冒称已切指定型号。
- 已检查的前置 PASS 报告：无已接受 PASS（M3=BLOCKED→FAIL 挂账、M2=FAIL 挂账）；按前序挂账裁决继续本模块局部修复，不把挂账等同前置通过。
- 本轮修改文件与原因：
  1. **bundle 0 hunks。** r11 已独立关闭 B-M4-01 的合法盘加载/准确分类/坏盘保全子项（empty_crlf/unicode_task_load pending=false 无新 recover；invalid_second_member/unknown_stage 准确分类；截断主盘与旧 recover 保持），D-M4-04 五函数段回归保持。本轮无任何源码改动，不回退、不重写已修子项。
  2. `M4/r10/scripts/m4_r10_atomic_fencing_repro.py`（新，D-M4-03 必修交付）：按 r11「方案误判」与「具体改法」逐条修正 r9 复现，已实际运行 rc=0（见下）。
  3. `M4/native/REQUEST_build_r10.json`（新）：2 场原生回归请求。按 R-M4-TEST-01 删除全部 `wait:N`（固定宿主未实现，r9/r11 全部 host.log 记 `unknown --test-action`）；时机由 min/max_seconds 与驱动控制。digest/anchor 与 r9 相同，复用 build_r9 已授权隔离签名 store（seeds/store 只读引用），无新私钥。
  4. r9 静态核验器原样重跑作回归：`m4_r9_fix_verifier.py` **46/46 PASS**（含 D-M4-04 六函数段对 r10 冻结源回归；源码未变，结果复制到 `M4/r10/evidence/fix_verifier.json`）。
- 桌面 UI/交互变化：无。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化。
- 已有别人修改的保留与适配：源码零改动，全部保留。
- 启动步骤 / 隔离数据位置：构建方不启动宿主；请求交驱动沙箱外执行，证据将落 `M4/native-runs/build_r10_*`（REQUEST_build_r10）。
- 应用运行模型/provider（适用时；无秘密）：needs_model=false，本轮 MiniMax 0 调用，未读任何密钥。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|D-M4-03 方案误判修正（B1）|O_EXCL 获取 + 现行 5min TTL 回收，注入存活持有者被抢占的 A2 调度|按 r11：单独 create_new 不足，lost update 仍在|P1 O_EXCL 唯一获取、复核通过；P2 TTL 回收后获取并提交 version=6；P1 迟到写覆盖 → p2_commit_lost=true|PASS（缺口实证，与审查方 independent_lock_counterexample 一致）|M4/r10/evidence/atomic_fencing_repro.json|
|D-M4-03 fencing 方案（B2）|同一 A2 调度 + fencing token 随获取单调推进、与事实同处一个原子 CAS 边界|旧持有者迟到提交被拒，A1/A2 双关闭|P1 迟到提交 rejected_stale_fence；final=P2 无 lost update；A1 轨迹唯一胜者|PASS（方案语义实证）|同上|
|D-M4-03 持有期 OS 锁（C2 真实多进程）|8 进程 × 200 轮 barrier 对抗，flock 覆盖 获取→复核→事实写→释放 整个命令边界|0 轮多 owned、每轮恰好一次提交、版本严格单调|0 轮多 owned；200/200 轮恰好一次提交；final version=200 无回卷|PASS（真实 OS 原语替身实证）|同上|
|D-M4-03 存活持有者回收注入（C-preempt）|持有者存活被抢占、锁戳远旧于 TTL；回收方按 TTL 规则尝试|回收方拿不到 flock = 持有者存活不可回收；持有者醒来提交成功|reclaimer_got_lock=false；final=P1-holder version=6 无 lost update|PASS|同上|
|D-M4-03 现行协议缺口回归（A1/A2/C1）|r9 复现原样保持|缺口仍可复现（不被新方案掩盖）|A1 双 owned、A2 lost update、C1 本轮 3 轮多 owned|PASS（缺口保持可复现）|同上|
|D-M4-03 双可信上下文同盘业务并发（原生）|需宿主原语 + 双上下文同盘调度入口|同盘接单/重叠确认唯一成功|harness 逐场新 Store、单宿主顺序执行，无该调度入口|BLOCKED（动态解阻条件见 r11 §D-M4-03；源码 P1 不靠 Python 替身冒充关闭）|—|
|冷启动渲染 + future 锁回归（原生）|REQUEST_build_r10 场1/2|零解析/运行错误、登录页渲染、future 锁逐字保留不回归|待驱动执行|NOT_RUN|M4/native/REQUEST_build_r10.json；证据待 native-runs/build_r10_*|
|B-M4-01 / D-M4-04 回归（静态）|r9 核验器 46 项原样重跑|无回退|46/46 PASS|PASS（静态）|M4/r10/evidence/fix_verifier.json|

## 尚未完成

- 原生 2 场 NOT_RUN：请求已提交，等驱动沙箱外执行后回读，本报告不预断结果；交接时无法附 harness 冷启动结果（构建方被禁止自启宿主，Abram 12:12 裁决）。bundle 与 r9 逐字节相同，r11 九场冷启动/加载/锁 boot 结论对该 digest 仍然成立，本轮两场仅为防回归。
- D-M4-03 真跨进程原子互斥仍 **HOST_PRIMITIVE_BLOCKED**：宿主 jailed fs 无 O_EXCL/flock/原子 rename/CAS。本轮已按 r11 修正方案误判（B1）并把「具体改法」落成可执行 fencing/持有期 OS 锁方案与实证（B2/C2/C-preempt），宿主路线裁决属驱动/Abram，构建方不自行改宿主、不新增服务。Python 侧 flock/CAS 是宿主应提供原语的语义替身，不冒称原生业务已实证。
- 硬验收 1/2/4/5 与 T04–T15/T31/T35、U01–U07 业务动态子项沿用 r11 审查表 NOT_RUN/BLOCKED；硬 3 的「同盘双上下文唯一成功」待宿主原语与调度通道解阻后实测。
- 事件落盘在锁外的窗口沿用挂账（附录方案含「宿主原语落地后事件写一并移入持锁区间」；当前由 bootReconcilePending 按 receipt 对账补齐，属既有可恢复边界）。

## 附录：D-M4-03 宿主原语对接方案（交驱动，按 r11 具体改法）

**r11 方案误判修正**：r9 附录的「write_exclusive + 5min TTL 回收」不足 —— B1 实证存活持有者在复核→写盘窗口内被 TTL 回收后仍能完成迟到写（lost update）。回收不感知持有者是否存活是根因。

**首选原语 `fs.lock_exclusive(path)`（持有期 OS 锁）**：splash_storage.rs 暴露 fd + flock/Rust fd-lock 等效持有期锁。
- `_acquireTaskLock`（main.splash:4446）：先拿持有期锁（拿不到=他人持有，含 TTL 回收路径也必须先拿锁 —— 存活持有者绝不可被回收），再写 stamp。
- `commitBound`（:4860）：授权/expected_version/跨任务冲突复核 + tasks.json/receipts/events 全部写在同一持锁区间完成。
- `_releaseTaskLock`（:4517）= 命令边界结束 unlock。crash 残留由宿主在进程退出时由内核自动释放（OS 锁天然随 fd 关闭释放，不再只靠 TTL）。
- C2/C-preempt 已实证：0 双主、200/200 恰好一次提交、存活持有者不可被 TTL 剥夺。

**备选 `fs.cas(path, expected, new)` + fencing**：权威记录携带单调 fencing token；每次获取把 fence 原子推进，提交以 cas 单步完成，fence 过期即拒（B2 实证 A1/A2 双关闭）。

**保留为纵深**：read_failed fail-closed、提交同 owner token 全等、盘版本/跨任务冲突复核、needs_verify 拒绝守卫全部保留；不以「再读一次 owner」或仅 O_EXCL 成功替代完整证明。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M4/r10/CANDIDATE.json`（candidate_id=M4-r10-worktree）。
- 可执行复现：`M4/r10/evidence/atomic_fencing_repro.json`（命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/r10/scripts/m4_r10_atomic_fencing_repro.py`，rc0）。
- 静态回归：`M4/r10/evidence/fix_verifier.json` 46/46（r9 核验器原样重跑，源码未变）。
- 原生请求：`M4/native/REQUEST_build_r10.json`（2 场，无 wait 动作；digest=`77b95f2e…`，anchor=`96692910…`，复用 build_r9 隔离签名 store，无新私钥）。原生证据待驱动落 `M4/native-runs/build_r10_*/`，如实标记 NOT_RUN。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。
