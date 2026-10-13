# M5 实施报告 r6（修复轮 · Kimi-K3）

- 模块 / 目标：M5 真实附件完工与独立验收 · 按 M5_REVIEW_r6 缺陷清单修复，只修清单项。
- candidate_id / base_candidate_id：`M5-r6-worktree` / `M5-r5-worktree`（清单 `runtime/optimization/2026-10-09/M5/r6/CANDIDATE.json`）。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d` + 既有未提交改动（含 M4-r7 等他人改动，全部保留）+ 本层 r6 修复。修复后 `app/bundle/main.splash` SHA-256=`4da13507ec78218d627ba91cab8569c47a77d0dc4d5d195ab9fb9e10a8266492`；bundle digest=`541349cc4addb06c9544ca9d5ad7a228d206b2cfc4cc1dfc093346fc50e2a7ac`。逐文件哈希见 `M5/native/build_r6/start-snapshot.json` 与 `fixtures.json` seed 清单。
- 目标宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`（固定发行宿主，未变）。
- 实际模型路由：本模块不调模型；全部场景 needs_model=false，模型请求 0。
- 已检查的前置：M4=FAIL（M4_REVIEW_r8，按 Abram 挂账裁决不修、仅消费契约）；M5_REVIEW_r6 为本轮唯一修复依据。
- 本轮修改文件与原因：
  1. `app/bundle/main.splash` — 仅此一个业务文件：
     - **B-M5-01**（必修）：`_strIndexOf` 新增局部变量 `ok` 是宿主保留字（M4_REVIEW_r8 高置信度根因：每场 3 条 parser 错误首条 ok reserved，宿主.log 43–45）。改为 `matched`，三处引用（`let ok = true` / `ok = false` / `if ok`）同步改名；不改任何其他标识符、不改逻辑。全文件正则扫描确认无其他保留字（err/type/match/fn/if/for/while/in/return/true/false/nil/catch/try/await/break/continue）被用作 let 变量。
     - **D-M5-04**（必修）：新增 `m5_reconcile_attach_index()` 启动对账（`main.splash` m5_load_attach_index 之后定义），并在 `load()` 中于索引加载 + demo 清退之后、开放操作之前调用。协议：任务库（`commit(t)` 先落盘）是权威事实，`evidence_index.json` 是派生索引；对账做四件事——(1) 以 `t.evidence`（随任务同一 commit 落盘）修平索引 `evidence_round` 与 `last_rejected_at`；(2) 索引缺项从 `t.evidence` 重建，并立刻重读真实字节（canonical 全字节比对 + 登记指纹 + 尺寸 + 内容签名回填）才置 READY——READY 仍只能由字节校验得出，不从登记值继承；canonical 快照缺失时须 sha+尺寸一致才允许从存盘重建快照，否则 CORRUPTED；(3) 索引孤儿（任务库无此证据）保留不删、仅计数记录，submit 候选遍历 `t.evidence` 天然不引用孤儿；(4) 任务不存在的外来项保留并计数。所有修复按任务落 `m5_index_reconcile` 事件、重写索引，并写 `STATE.m5_last_reconcile` 对账记录（at/修轮次/重建/孤儿/外来/涉及任务）供 UI 与回读核验。
     - 注释/提示清扫：submit（commit 成功索引落盘失败分支）与 reject 同类分支的过期注释与状态串更新为「重启时启动对账将从任务事实自动修平索引」，删除「旧版本覆盖」「重新上传」的旧说法（M5_REVIEW_r6 指出的 submit 注释与 loader 行为相反问题）。
- 桌面 UI/交互变化：无新增控件；对账结果落 `STATE.status` 与事件，验收/完工表单不变。
- 接口 / 数据迁移 / 旧数据恢复：无格式迁移；旧 evidence_index.json 在启动时被对账修平（不删除任何条目）。
- 已有别人修改的保留与适配：M4-r7（`_strIndexOf` 等 helper、登录/锁恢复）与 M6/M7 改动全部保留；仅在 `_strIndexOf` 内部改保留字变量名。未 reset/stash/删除任何他人改动。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。原生验证请求 `M5/native/REQUEST_build_r6.json`（4 场），由驱动在沙箱外经 `driver/harness/native_harness.py` 执行，证据输出固定为 `M5/native-runs/build_r6_REQUEST_build_r6/`（fixture 绝对根已按此钉扎）。
- 应用运行模型/provider：不调用；无秘密入代码/日志/报告。
- 覆盖的既有验收项与证据运行形态：G0-D/T19/T22/U07 的「重启恢复/索引分裂」子项由对账协议覆盖，原生实证待驱动执行；其余 T/U 项本轮未扩。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|B-M5-01 保留字清零|全文件正则扫描 + 引用计数|无 ok 等保留字变量|24 项静态检查全过|PASS（源码级）|M5/r6/results/r6-fix-checks.json|
|本地 canonical 探针|octoscript-cli check 新函数与已知良构函数|—|canonical profile 连已知良构 `m5_save_attach_index` 也拒（单行 if 块/#颜色/位运算），不具宿主代表性；仅作负向校准记录|校准记录| M5/r6/parse-check/|
|D-M5-04 对账算法|Python 移植算法跑 3 类分裂夹具|submit 分裂修回 round1；reject 分裂修回 round0+退回标记；索引缺项重建 READY 且孤儿保留|3/3 符合|PASS（逻辑移植，非原生）|M5/r6/results/r6-fix-checks.json|
|真实桌面冷启动（零解析错误/登录任务界面渲染）|harness cold_fresh 场|零 parser 错误、真实 UI|NOT_RUN（驱动执行后见 native-runs）|NOT_RUN|M5/native/REQUEST_build_r6.json|
|原生对账恢复（3 场分裂负例）|harness reconcile_* 场启动即对账|运行副本 evidence_index.json 被修平 + events.jsonl 有 m5_index_reconcile|NOT_RUN|NOT_RUN|同上|
|权威状态与回执|可信会话业务命令|—|NOT_RUN（输入白名单通道缺口沿用 r6 Review BLOCKED 子项）|NOT_RUN|—|
|失败与重试 / 完整正常链与退回链|真实上传→完工→验收|—|NOT_RUN|NOT_RUN|—|
|受影响先前模块回归|M4-r7 helper 改名影响面|仅 `_strIndexOf` 内部局部名|其调用方不感知局部改名；无签名变化|PASS（源码级）|M5/native/build_r6/affected-functions.json|

## 尚未完成
- 原生冷启动与 3 场对账负例：请求已就绪并钉扎路径，**NOT_RUN**（驱动在本阶段结束后沙箱外执行；证据将落 `M5/native-runs/build_r6_REQUEST_build_r6/`）。
- D-M5-05 完整实证、可信独立验收、正常/退回链、同盘重启、受控写失败注入：沿用 M5_REVIEW_r6 的 NOT_RUN/BLOCKED 子项划分，本轮未扩范围。
- 本地 canonical 解析器与发行宿主语法 profile 不一致（连已知良构代码也拒），不能替代宿主验证；B-M5-01 的最终判定以 harness 冷启动 host.log 零解析错误 + 真实 UI 截图为准。

## 交接
- 候选清单：`runtime/optimization/2026-10-09/M5/r6/CANDIDATE.json`（含源 SHA 与 bundle digest）。
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r6.json`；准备脚本 `prepare_build_r6.py`；离线签名证据 `build_r6/offline-store-evidence.json`（私钥 2 把已删，删除记录逐项 exists_after=false，keys 目录为空）；seed 清单 `build_r6/fixtures.json`。
- 源码切片：`build_r6/source-traces/`（_strIndexOf / m5_reconcile_attach_index / load 等）。
- 静态证据：`M5/r6/results/r6-fix-checks.json`（24/24）；canonical 探针校准 `M5/r6/parse-check/`。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
