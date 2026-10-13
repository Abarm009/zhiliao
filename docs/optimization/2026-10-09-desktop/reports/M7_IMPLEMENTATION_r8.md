# M7 实施报告 r8

- 模块 / 目标：M7 同版本总验收与发布准备 —— 修复轮，只处理 M7_REVIEW_r9 的两项必修（R-M7-02、R-M7-03）；A-M7-01/02 P2 建议按规则继续挂账，不顺手改。
- candidate_id / base_candidate_id：`M7-r8-worktree` / `M7-r7-worktree`
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`；dirty.diff 与六文件 SHA-256 清单见 `runtime/optimization/2026-10-09/M7/r8/phase1-audit.json`；主源 `app/bundle/main.splash` 597814 B，SHA-256=`3b5001839fda8153d5adfeba04f11669ccd4e243af39c2dbd8c8e6d7a89d2852`。
- 目标宿主 / 二进制来源与哈希 / 依赖：M0/r3 提取 OctoSense.app；octosense SHA=`3e127963…`，octos-kernel SHA=`a3e46a45…`；本轮构建方不启动宿主。
- 实际模型路由检查结果（开发会话）：主会话无 Router 切换/核验接口，未冒称；候选 model_config enabled=false、storage-only。
- 已检查的前置 PASS 报告：无已接受 M6 PASS（M6_REVIEW_r10 FAIL 挂账沿用户裁决继续）；上轮 M7_REVIEW_r9 FAIL，两项必修为本轮唯一修复清单。
- 本轮修改文件与原因：仅 `app/bundle/main.splash`（R-M7-02 三处最小修复）+ M7/r8 新增冻结/证据 + GATES/CONTEXT/本报告。R-M7-03 无需改代码——严格数值门禁已存在于当前累计工作树且经 M6-r8 原生实测，本轮把它随新 M7 候选冻结入包。
- 桌面 UI/交互变化：任务恢复 banner 与两个恢复 Chip 从状态块之后移到左栏顶部固定可见区（scope_note/visible_count 之后、其余状态块之前）；其余不变。
- 接口 / 数据迁移 / 旧数据恢复方式：tasks.json 严格整份校验抽公共函数 `m7_tasks_strict_parse`（首尾闭合 + parse + 顶层数组 + 逐成员必需字段/类型/已知状态），load、保留复验、受控覆盖写后读回三处共用；「保留原文」分支不再无条件解锁——原文复验为合法事实源才加载并解除 pending，仍非法则保持 pending 并给出可见下一步；原文+备份读回+普通三写门禁全部保留。
- 已有别人修改的保留与适配：M0..M6 全部累积字节保留，仅叠加本模块修复；未 reset/stash/覆盖他人改动。
- 启动步骤 / 隔离数据位置：harness 每场在 `runtime/optimization/2026-10-09/M7/native-runs/` 下新目录；本轮构建方不启动 launcher。
- 应用运行模型/provider：enabled=false；密钥不经手；本轮 needs_model=false、真实调用 0。
- 覆盖的既有验收项与证据运行形态：本轮只做离线静态/准入证据；业务/UI 原生判定全部等驱动 harness，不预声明。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r8 十八场（冷启渲染回归/提醒类型矩阵/合法完整任务/四种坏任务/恢复两分支点击）|解析 0、工作台渲染；合法加载不误拒；坏盘整份拒+原文/备份+pending；恢复 banner+Chip 可见；keep 对非法原文不解锁、overwrite 核实备份后写空副本解除|构建方不能启动宿主；请求已交驱动|NOT_RUN（待驱动）|runtime/optimization/2026-10-09/M7/native/REQUEST_build_r8.json|
|权威状态与回执|可信登录后业务命令|—|本轮未涉及|NOT_RUN|—|
|失败与重试|坏任务/坏提醒预置 seed|pending 拒写、原文/备份可核|静态修复完成，宿主行为待复核|NOT_RUN（待驱动）|r8/seeds/|
|重启恢复|同 Store 跨进程重启|—|schema 无此动作|BLOCKED（能力缺口，沿前轮）|—|
|受影响先前模块回归|follow_ups loader（D-M6-02 严格数值门禁源）|合法空/整数/小数通过，true/false/字符串/对象/数组/null 整份拒|门禁随包冻结，待 harness 复核|r8/seeds/ 类型矩阵|
|离线准入|hub stamp 不动点 + check --allow-unsigned + 离线签名/verify/install_staged|rc=0|PASS|PASS（离线子项）|r8/results/hub-check.txt；r8/phase1-audit.json|
|私钥处理|keygen/sign 后 finally 删除|keys 目录空|PASS|PASS|r8/phase1-audit.json keys_deleted/private_key_files_remaining|

## 两项必修对账（按审查方改法逐条）

- **R-M7-02（坏任务漏恢复门禁 + 恢复出口不可见）**：
  1. 严格完整 JSON/数组/运行必需字段检查抽为 `m7_tasks_strict_parse`（`app/bundle/main.splash:1184`），load（`:1386`）、保留复验（`:1282`）、受控覆盖写后读回（`:1308`）三处共用同一份判据；不是只加首尾括号特判（闭合只是第一层，后有 parse+数组+逐成员门禁）。
  2. keep 分支不再无条件解锁：原文经共用严格校验复验为合法事实源才加载进 TASKS 并解除 pending；仍非法保持 pending，status 给出「修复后重试或用内存覆盖」可见出口。备份核实（.recover.bak 逐字节读回）在两分支之前，保持不变。
  3. 任务恢复 banner + 两个 Chip 移到左栏顶部固定可见区（`:11033–11045`），先于 m6_status_label/fu_banner/fu_count/提醒恢复 Chip；依据 M6_REVIEW_r10 实测「空 banner 占高把按钮推出客户区」。
  4. 交接新 M7 冻结包 0.1.0-g 与同步材料（见下），不再递交旧 532303 B 包。
- **R-M7-03（bool/数字字符串误接受）**：当前累计源码的严格数值门禁 `m7_is_strict_number_value`（先排除 true/false/字符串/对象/数组，再做数值探针；M6_REVIEW_r10 原生实测六反例全拒、四正例全过）随 0.1.0-g 冻结入包；load 与受控恢复读回继续共用 `m7_followups_schema_ok`。新包/清单/材料与新 digest 同步，未把 M6 候选 PASS 子项转移给旧 M7 包。

## 尚未完成

- 共用严格校验/keep 复验/恢复入口置顶在本候选字节上的宿主行为**未经实证**：判据组件（to_chars 码点比较、trim、parse 宽容度、严格数值探针）以 M6-r8 原生实测为依据，最终判定权在驱动 harness 复核（REQUEST_build_r8，18 场）。
- 恢复 Chip 点击坐标为布局估算（顶栏 76 + 登录行 70 + 左栏顶起）；若 tap 未命中，状态证据不变，按证据如实记未验证，不伪造成功回执。
- 可信登录成功/失败链、三角色业务全链、真实模型三链、同 Store 跨进程重启、精确故障注入：NOT_RUN / 具体 BLOCKED（白名单缺口沿前轮，未改）。
- A-M7-01（app/README.md 旧入口/旧版本话术）、A-M7-02（材料历史表述/媒体）：P2 建议挂账保留，本轮按修复轮规则未动。
- P06/P07/P08：UNASSESSED/NOT_RUN，本轮无发布、无递交、无收录动作。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M7/r8/CANDIDATE.json` 未单独生成——定位信息完整存于 `r8/phase1-audit.json`（HEAD/dirty.diff/六文件哈希/冻结摘要/运输比对/seed 清单/request 哈希），与 r7 的 CANDIDATE.json 字段一一对应。
- 冻结包：`runtime/optimization/2026-10-09/M7/r8/release/octosense-repair-0.1.0-g/`，digest=`e0ee84d8463778bade271acc1a4798e0486bbd15a3c5fc21d6bc16e1cadf89a8`，hub check rc=0 PASSED（r8/results/hub-check.txt）；主源 597814 B SHA-256=`3b500183…` 与工作区逐字节一致。
- 离线 catalog/Store/seeds：`r8/store/`、`r8/seeds/`（18 场，夹具与 review_r1_0937 同口径、独立新造标记 M7-BUILD-R8）；私钥已删（phase1-audit.json，keys 目录空）。
- harness 请求：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r8.json`（18 场，needs_model=false，白名单校验全过）。
- 原生截图/日志：待驱动执行后存 `M7/native-runs/build_*_REQUEST_build_r8/`；交接时本轮无冷启动截图（构建方不得自行启动宿主），冷启解析清零/渲染回归由该请求第 1 场 cold_clean 覆盖。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
