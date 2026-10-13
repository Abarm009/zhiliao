# M7 实施报告 r9

- 模块 / 目标：M7 同版本总验收与发布准备 —— 修复轮，只处理最新独立 Review **M7_REVIEW_r11**（与 r10 同一候选 0.1.0-g、同一组缺陷）的两项必修 **B-M7-01**（冷启解析回归）、**R-M7-02**（合法误拒/坏盘 pending 失效/恢复出口不成立）；R-M7-03 保持关闭不动；A-M7-01/02 P2 建议按规则继续挂账，不顺手改。
- candidate_id / base_candidate_id：`M7-r9-worktree` / `M7-r8-worktree`
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`；dirty.diff 与六文件 SHA-256 清单见 `runtime/optimization/2026-10-09/M7/r9/phase1-audit.json`；冻结主源 `app/bundle/main.splash` **702301 B**，SHA-256=`f7afc63256f386633f2f03c0aa4a5f464175a9f43dd3ca4fe86f2b3798b7e429`（含 M2–M6 r11 累计与本轮 M7 三处修复，不撤不改他人差异）。
- 目标宿主 / 二进制来源与哈希 / 依赖：M0/r3 提取 OctoSense.app；octosense SHA=`3e127963…`，octos-kernel SHA=`a3e46a45…`；本轮构建方不启动宿主（Abram 10-11 12:12 裁决：原生验证一律走 harness）。
- 实际模型路由检查结果（开发会话）：主会话无 Router 切换/核验接口，未冒称；候选 model_config enabled=false、storage-only。
- 已检查的前置 PASS 报告：无已接受 M6 PASS（M6_REVIEW_r12 FAIL 挂账沿用户裁决继续）；上轮 M7_REVIEW_r11 FAIL，两项必修为本轮唯一修复清单。
- 本轮修改文件与原因：仅 `app/bundle/main.splash`（R-M7-02 三处最小修复，见下）+ M7/r9 新增冻结/证据/seed + GATES/CONTEXT/本报告。B-M7-01 无需新改代码——审查方指定的 `success` 返回协议改名已存在于当前累计工作树（701133 B 基线），本轮按 r11 改法「明确差异后重冻结新 M7 candidate/digest 及清单/运输/材料」，不再递交旧 0.1.0-g。
- 桌面 UI/交互变化：仅聚合文案一处（任务+提醒同时待恢复时状态行同时点名两者出口）；布局/控件命名不变。
- 接口 / 数据迁移 / 旧数据恢复方式：load/保留复验/受控覆盖读回三处继续共用 `m7_tasks_strict_parse`；keep 仍须复验为合法事实源才解锁；overwrite 仍要求有效可信身份+备份核实+受控写+严格读回。无数据迁移变更。
- 已有别人修改的保留与适配：M0..M6 全部累积字节保留；未 reset/stash/覆盖他人改动；harness 源码本轮未触碰。
- 启动步骤 / 隔离数据位置：harness 每场在 `runtime/optimization/2026-10-09/M7/native-runs/` 下新目录；本轮构建方不启动 launcher。
- 应用运行模型/provider：enabled=false；密钥不经手；本轮 needs_model=false、真实调用 0。
- 覆盖的既有验收项与证据运行形态：本轮只做离线静态/准入证据；业务/UI 原生判定全部等驱动 harness，不预声明。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r9 十场（无 tasks 冷启/合法空/完整 DRAFT/六坏盘/既有备份保留；提醒类型矩阵随场嵌入；合法空场空输入登录回归 tap；bad_object/bad_member 未认证恢复 tap）|每场解析诊断 0、工作台渲染；合法两场不生成 tasks.recover；六坏盘 pending=true、原因准确可见、原文/备份逐字节保全；bad_task_boolean 的 version=true 被严格数值门禁整份拒；既有合法 recover 不被覆盖|构建方不能启动宿主；请求已交驱动|NOT_RUN（待驱动）|runtime/optimization/2026-10-09/M7/native/REQUEST_build_r9.json|
|权威状态与回执|可信登录后业务命令|—|本轮未涉及|NOT_RUN|—|
|失败与重试|坏任务/坏提醒预置 seed|pending 拒写、原文/备份可核|静态修复完成，宿主行为待复核|NOT_RUN（待驱动）|r9/seeds/（夹具逐字节镜像 review_r1_0002）|
|重启恢复|同 Store 跨进程重启|—|schema 无此动作|BLOCKED（能力缺口，沿前轮）|—|
|受影响先前模块回归|follow_ups 严格数值门禁（R-M7-03 已关闭项）|六非法类型整份拒、三正例加载|门禁字节保留随包冻结，待 harness 复核|NOT_RUN（待驱动）|r9/seeds/ 各场 follow_ups 夹具|
|离线准入|hub stamp 不动点 + check --allow-unsigned + 离线签名/verify/install_staged|rc=0|rc=0 PASSED（unsigned warning 保留如实记录）|PASS（离线子项）|r9/results/hub-check.txt；r9/phase1-audit.json|
|私钥处理|keygen/sign 后 finally 删除|keys 目录空|anchor.key/working.key 已删，目录空|PASS|r9/phase1-audit.json keys_deleted/private_key_files_remaining|

## 两项必修对账（按审查方改法逐条）

- **B-M7-01（冷启解析回归，REOPENED→本轮处理）**：r11 改法为「采用固定宿主实证可用的返回协议（如 success），同步全部三调用点；若修复已在当前累计源码，明确差异后重冻结新 M7 candidate/digest 及清单/运输/材料」。核对结果：当前工作树（701133 B 基线）中共同 parser `m7_tasks_strict_parse` 的 4 处 `{ok:…}` 返回已全部改为 `{success:…}`，load（`:1596`）、keep 复验（`:1492`）、overwrite 读回（`:1518`）三处 `.ok` 比较已全部改为 `.success`；全文件静态扫描无残留 `{ok:` / `.ok ==` / `.ok !=`（phase1-audit.json r9_fix_evidence 断言）。`success` 字段在模型适配层等多处长期使用且经宿主实证，符合审查方「已验证非冲突字段」要求。本轮将该源码冻结为新候选 **0.1.0-h**（digest 见交接），不递交旧 0.1.0-g。冷启 0 诊断的最终确认只能由合规 harness 完成（REQUEST_build_r9 第 1 场 cold_absent 及全部 10 场），构建方不自行启动宿主。
- **R-M7-02（合法误拒 / pending 失效 / 恢复出口，PARTIAL→本轮处理）**：
  1. pending/reason 重置路径审计（r11 要求「修解析后核 load→初始化→reconcile→refresh/save/tick」）：`STATE.tasks_pending_recovery` 全文件写点仅 5 处——STATE 默认声明、`m7_tasks_mark_corrupt` 置 true、keep/overwrite 两成功分支置 false、load 严格校验成功分支置 false（另 nil 兜底）——phase1-audit.json 以精确计数断言（`= true`×1、`= false`×4）；`loadViewState` 只并入偏好白名单字段，不恢复该 flag/reason；`loadModelConfig/m4_init_forms/bootReconcilePending/_m1_init_selection/saveState/tick` 均不触碰。解析修复后不存在把 flag 清掉的其他路径。
  2. 任务 version/createdAtMs/updatedAtMs 由宽容 `m7_is_number_value` 改为严格数值门禁 `m7_is_strict_number_value`（`m7_task_record_valid`，排除 bool/数字字符串/对象/数组后再做数值探针）——`bad_task_boolean`（version=true）整份拒由 REQUEST_build_r9 同名场复核。
  3. load() 内两处 migrateJsonlLegacy 成功提示增加 `STATE.tasks_pending_recovery != true` 守卫，任务损坏原因说明不被迁移成功提示覆盖（flag/reason 本身本就不被重置，此修可见文案）。
  4. `m6_status_label_text` 在任务+提醒同时 pending 时返回聚合文案同时点名两者及各自恢复入口，任务 banner 不被提醒状态整条覆盖；单 pending 时原文案不变。
  5. 三处共用严格判据、keep 复验解锁、overwrite 身份+备份+受控写+严格读回、原文/旧备份保全策略与现有 UI 布局全部保留未动。

## 尚未完成

- 0.1.0-h 的宿主行为（解析诊断 0、合法不误拒、坏盘 pending 保持、严格数值门禁、恢复入口可见）**未经实证**：最终判定权在驱动 harness 复核（REQUEST_build_r9，10 场）。本轮交接无冷启动截图——构建方不得自行启动宿主；上一轮（r8 冻结）驱动执行结果为 10/10 CLEAN 但 17 条/场解析诊断，本候选必须复测。
- bad_object/bad_member 的恢复 tap 坐标沿用审查方 r11 请求的既有画面坐标；未命中则状态证据不变，按证据如实记未验证，不伪造恢复/拒绝回执。可信登录后的 keep/overwrite 两分支、同 Store 业务进程重开、精确故障注入：NOT_RUN / 具体 BLOCKED（白名单缺口沿 r11，未改）。
- A-M7-01（app/README.md 旧入口/旧版本话术）、A-M7-02（listing placeholder/完整演示）：P2 建议挂账保留，本轮按修复轮规则未动。
- P06/P07/P08：UNASSESSED/NOT_RUN，本轮无发布、无递交、无收录动作。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M7/r9/CANDIDATE.json` 未单独生成——定位信息完整存于 `r9/phase1-audit.json`（HEAD/dirty.diff/六文件哈希/r9_fix_evidence 静态断言/冻结摘要/运输比对/seed 清单/request 哈希/私钥删除记录），与 r7 的 CANDIDATE.json 字段一一对应。
- 冻结包：`runtime/optimization/2026-10-09/M7/r9/release/octosense-repair-0.1.0-h/`，digest=`4c2bb0d3618afea78801ea2764fcc15918f0e88fb5860e3d3f2ca9225afca72f`，hub check rc=0 PASSED（r9/results/hub-check.txt）；主源 702301 B SHA-256=`f7afc632…` 与工作区逐字节一致。
- 离线 catalog/Store/seeds：`r9/store/`、`r9/seeds/`（10 场，夹具逐字节镜像 review_r1_0002，新 Store）；私钥已删（phase1-audit.json，keys 目录空）。
- harness 请求：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r9.json`（10 场，needs_model=false，白名单校验全过，SHA-256=`0348b26a…`）。
- 原生截图/日志：待驱动执行后存 `M7/native-runs/build_*_REQUEST_build_r9/`；冷启解析清零/渲染回归由该请求全部 10 场覆盖。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
