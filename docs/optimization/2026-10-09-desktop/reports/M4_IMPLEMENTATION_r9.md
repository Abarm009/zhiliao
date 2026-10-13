# M4 实施报告 r9

- 模块 / 目标：M4 接单设备与预约桌面流程 —— 修复轮，只修 M4_REVIEW_r10 缺陷清单两项必修（B-M4-01、D-M4-03），D-M4-04 SOURCE-CLOSED 保回归，不发散。
- candidate_id / base_candidate_id：M4-r9-worktree / M4-r8-worktree。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`（工作树 dirty，含他人改动）；`app/bundle/main.splash` SHA256=`c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421`，657584 B；r8→r9 差异 `M4/r9/evidence/r8-to-r9.diff`（含 M5/M6/M7/M2/M3 共享修复与 Apple HIG 重设计等他人改动，本轮 M4 对 bundle 自身新增 hunks=0）。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256=`3e127963…`，沿用 r10 审查记录）；jailed fs 方法表以 vendored `runtime/native-build/makepad/widgets/src/splash_storage.rs:242–415` 逐行核实：read/read_bytes/write/append/exists/remove/mkdir/list —— 无 O_EXCL/flock/原子 rename。
- 实际模型路由检查结果（开发会话）：本轮为修复轮，未核验主会话路由；不冒称已切指定型号。
- 已检查的前置 PASS 报告：无已接受 PASS（M3=BLOCKED 挂账、M2=FAIL 挂账）；按前序挂账裁决继续本模块局部修复，不把挂账等同前置通过。
- 本轮修改文件与原因：
  1. **bundle 0 hunks。** B-M4-01 的审查方改法（首尾括号与 `"[".to_chars()[0]` / `"]".to_chars()[0]` 同型比较）已在当前共享工作树 `m7_tasks_strict_parse`（main.splash:1383–1411）落地——与 D-M5-04 r9 同一教训由后续共享修复轮先行应用。本轮逐条核验保留：trim 先于闭包校验、成员 schema 门禁（`m7_task_record_valid`:1348–1376 + 8 阶段白名单）、pending 普通命令/创建拒写（:4633–4641、createDraftFromPanel）、既有非空 recover 不覆盖另存 corrupt.latest（:1414–1441）、恢复核 identityActive（:1452–1457）、闭合缺字段/非法 status 走成员门禁准确分类（:1403–1409）。不回退、不重复改写。
  2. `M4/r9/scripts/m4_r9_fix_verifier.py`（新）：r8 核验器 35 项全部保留；两处因后续重构（闭包校验上移 `m7_tasks_strict_parse`）过时的断言更新到现结构并加严（同型比较、无 `== "["` 残留、准确分类、load 走共用判据）；新增 D-M4-04 六函数段对 r10 冻结源回归。结果 **46/46 PASS**（`M4/r9/evidence/fix_verifier.json`）。
  3. `M4/r9/scripts/m4_r9_atomic_acquire_repro.py`（新，D-M4-03 必修交付）：可执行最小复现，已实际运行（见下）。
  4. `M4/native/prepare_build_r9.py` + `REQUEST_build_r9.json`（新）：离线签名 store（digest=`77b95f2e…`，anchor=`96692910…`；与 M3-r9 同共享工作树）+ 7 场原生验证请求。
- 桌面 UI/交互变化：无（本轮不碰 UI；Apple HIG 布局为他人成果，未改）。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化；恢复入口沿用 m7_tasks_explicit_recover 既有契约。
- 已有别人修改的保留与适配：confirmDraftModelBound 经 M2-r10/M3-r9 共享修复合法扩展（意图重试直通 + outcome 消费），D-M4-04 epoch 失效逻辑保留（`human_edited_epoch_fields` 仅消费本 epoch；`m4_invalidateConfirmation` 清 epoch 不变）；其余五函数段与 r10 冻结源逐字一致。全部保留不回退。
- 启动步骤 / 隔离数据位置：构建方不启动宿主；请求交驱动沙箱外执行，证据将落 `M4/native-runs/build_r9_*`。
- 应用运行模型/provider（适用时；无秘密）：needs_model=false，本轮 MiniMax 0 调用，未读任何密钥。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|B-M4-01 同型比较（静态）|fix_verifier 46 项含 r10 改法逐条|合法盘不再误判截断；闭合缺字段/非法 status 准确分类|46/46 PASS|PASS（静态）|M4/r9/evidence/fix_verifier.json|
|B-M4-01 五组盘夹具（原生）|REQUEST_build_r9 场2–6（与 r10 完全同夹具）|valid_empty/valid_task pending=false 无新 recover；truncated 主盘+旧 recover 保持、corrupt.latest 落盘；id_only/unknown_status pending=true 且 why 为成员门禁原因|待驱动执行|NOT_RUN|M4/native/REQUEST_build_r9.json；证据待 native-runs/build_r9_*|
|冷启动渲染回归（原生）|场1：新 Store 冷开+capture|零解析/运行错误、登录页渲染不回归|待驱动执行|NOT_RUN|同上|
|D-M4-03 脚本边界（静态）|fix_verifier 中 r7/r8 全部边界项|获取/提交/释放同 owner、提交点版本/冲突复核保持|PASS|PASS（静态）|M4/r9/evidence/fix_verifier.json|
|D-M4-03 可执行最小复现|m4_r9_atomic_acquire_repro.py 实际运行|A1 获取级双 owned 复现、A2 复核→写盘窗口 lost update 复现、B 提议原语唯一胜者、C 真实 8 进程×200 轮对抗|A1/A2/B 全复现；C：现行协议 2 轮多 owned、create_new 0 轮|PASS（复现缺口+原语有效性）|M4/r9/evidence/atomic_repro.json|
|D-M4-03 双可信上下文同盘并发（原生）|需宿主原语或双上下文调度通道|同盘接单/重叠确认唯一成功|宿主无 O_EXCL 原语；harness 无双上下文同盘调度|BLOCKED（HOST_PRIMITIVE_BLOCKED，方案已交驱动）|atomic_repro.json + 附录|
|D-M4-04 六函数段回归（静态）|对 r10 冻结源逐段比较|无回退|5 段逐字一致；confirmDraftModelBound 合法扩展且 epoch 逻辑保留|PASS（静态）|M4/r9/evidence/fix_verifier.json|
|受影响先前模块回归|r8 核验器 35 项全部沿用|无回退|35/35 含在 46/46 内|PASS（静态）|同上|
|真实桌面主链（登录→接单→设备→预约→开工）|可信账号+输入通道|真实处理流程|宿主 type:/key: 输入通道 unknown（r10 实证）；不可用 seed/注入代验|NOT_RUN（通道 BLOCKED）|—|

## 尚未完成

- 原生 7 场均 NOT_RUN：请求已提交，等驱动沙箱外执行后回读，本报告不预断结果；交接时无法附 harness 冷启动结果（构建方被禁止自启宿主，Abram 12:12 裁决）。
- D-M4-03 真跨进程原子互斥仍 **HOST_PRIMITIVE_BLOCKED**：宿主 jailed fs 无 O_EXCL/flock/原子 rename（splash_storage.rs:242–415 逐行核实）。本轮已把 r8 的文字说明升级为可执行最小复现（A1/A2 缺口复现 + B/C 原语有效性实证）与对接方案（附录），宿主路线裁决属驱动/Abram，构建方不自行改宿主、不新增服务。
- 硬验收 1/2/4/5 与 T04–T15/T31/T35、U01–U07 业务动态子项沿用 r10 审查表 NOT_RUN/BLOCKED，本轮未冒充；硬 3 的「同盘双上下文唯一成功」待原语/调度通道解阻后实测。
- 事件落盘在锁外的窗口沿用 r8 挂账（附录方案含「全部写纳入持锁区间」）。

## 附录：D-M4-03 宿主原语最小复现结论与对接方案（交驱动）

**复现结论（已实际运行，`M4/r9/evidence/atomic_repro.json`）**：
- A1（确定性轨迹）：现行 exists→write→read-back 获取协议存在获取级双 owned（W1,R1,W2,R2 交错）；r8 提交点同 owner 复核在该轨迹上兜住（先写者 needs_verify 拒）——复核是必要纵深但不够。
- A2（确定性轨迹）：持有者通过全部提交复核后、整盘写之前被抢占超过 stale TTL（5min），另一进程按回收规则合法取锁并提交，前者醒来完成写 → 版本回卷 lost update。**复核→写盘不是同一原子步，这是剩余 P1 缺口。**
- B（同一轨迹 + 提议原语）：`write_exclusive`（create_new）获取即唯一胜者，无交错可能。
- C（真实 8 进程 × 200 轮 barrier 对抗）：现行协议实测 2 轮多 owned；O_EXCL 语义 0 轮。

**所需宿主原语**：`fs.write_exclusive(path, data)` —— `OpenOptions::new().create_new(true)`；已存在返回失败（脚本 try/catch 得 false）。落点 `runtime/native-build/makepad/widgets/src/splash_storage.rs` script_mod，约 20 行，复用既有 target()/配额检查。

**脚本侧对接方案（原语到位后）**：`_acquireTaskLock` 改为 `write_exclusive("tasks.lock", stamp)` 一次调用（成功=唯一持有者，省去读回）；commitBound 保持同 owner/版本/冲突复核作纵深；任务/回执/事件/预约全部写纳入持锁区间后 `fs.remove("tasks.lock")` 释放；stale 回收维持 5min TTL + 回收前 token 复核（crash 残留）。获取/提交/释放守同一 owner token 不变。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M4/r9/CANDIDATE.json`（candidate_id=M4-r9-worktree）。
- 静态核验：`M4/r9/evidence/fix_verifier.json` 46/46（命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/r9/scripts/m4_r9_fix_verifier.py`）。
- 可执行复现：`M4/r9/evidence/atomic_repro.json`（命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/r9/scripts/m4_r9_atomic_acquire_repro.py`，rc0）。
- 差异：`M4/r9/evidence/r8-to-r9.diff`（含他人共享改动声明）。
- 离线签名证据：`M4/native/build_r9/offline-store-evidence.json`（私钥已删，remaining_key_files=[]；删除证据在文件内 private_keys_deleted）。
- 原生请求：`M4/native/REQUEST_build_r9.json`（7 场；digest=`77b95f2e…`，anchor=`96692910…`）。原生截图/日志/回执证据待驱动落 `M4/native-runs/build_r9_*/`，如实标记 NOT_RUN。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。
