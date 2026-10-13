# M7 实施报告 r7

- 模块 / 目标：M7 同版本总验收与发布准备 —— 修复轮，只处理 M7_REVIEW_r7 的三项 P1 必修（R-M7-01/02/03）；A-M7-01/02 P2 建议按规则继续挂账，不顺手改。
- candidate_id / base_candidate_id：`M7-r7-worktree` / `M7-r6-worktree`
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`；dirty.diff 与六文件 SHA-256 清单见 `runtime/optimization/2026-10-09/M7/r7/phase1-audit.json`；主源 `app/bundle/main.splash` 532303 B，SHA-256=`7b82c1313dcf14379942f01453784f44eb70321257d61a9214fc09d39173e23c`。
- 目标宿主 / 二进制来源与哈希 / 依赖：M0/r3 提取 OctoSense.app；octosense SHA=`3e127963…`，octos-kernel SHA=`a3e46a45…`；本轮构建方不启动宿主。
- 实际模型路由检查结果（开发会话）：主会话无 Router 切换/核验接口，未冒称；候选 model_config enabled=false、storage-only。
- 已检查的前置 PASS 报告：无已接受 M6 PASS（M6_REVIEW_r8 FAIL 挂账沿用户裁决继续）；上轮 M7_REVIEW_r7 FAIL，三项 P1 为本轮唯一修复清单。
- 本轮修改文件与原因：仅 `app/bundle/main.splash`（三处缺陷最小修复）+ M7/r7 新增冻结/证据 + GATES/CONTEXT/本报告。
- 桌面 UI/交互变化：登录行加高（50/28→70/34）修裁切；登录/清空按钮改 text()/set_text() 控件方法；左栏新增任务恢复 banner 与两个恢复 Chip（仅 pending 可用）。
- 接口 / 数据迁移 / 旧数据恢复方式：tasks.json 损坏→原文保留 + tasks.json.recover 备份读回核实 + pending 拒写 + 显式恢复（保留原文 / 用内存覆盖，均先备份 .recover.bak 并读回校验）；follow_ups 恢复读回新增共用 schema 校验。
- 已有别人修改的保留与适配：M0..M6 全部累积字节保留，仅叠加本模块三处修复；未 reset/stash/覆盖他人改动。
- 启动步骤 / 隔离数据位置：harness 每场在 `runtime/optimization/2026-10-09/M7/native-runs/` 下新目录；本轮构建方不启动 launcher。
- 应用运行模型/provider：enabled=false；密钥不经手；本轮 needs_model=false、真实调用 0。
- 覆盖的既有验收项与证据运行形态：本轮只做离线静态/准入证据；业务/UI 原生判定全部等驱动 harness，不预声明。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r7 七场（冷启/登录点击/合法与坏提醒/坏任务）|解析 0 错误、登录空输入可见提示、坏任务 0 循环+恢复入口、合法提醒加载、反例精准拒绝|构建方不能启动宿主；请求已交驱动|NOT_RUN（待驱动）|runtime/optimization/2026-10-09/M7/native/REQUEST_build_r7.json|
|权威状态与回执|可信登录后业务命令|—|登录入口修复未经宿主实证|NOT_RUN|—|
|失败与重试|坏任务/坏提醒预置 seed|pending 拒写、原文/备份可核|静态修复完成，宿主行为待复核|NOT_RUN（待驱动）|r7/seeds/|
|重启恢复|同 Store 跨进程重启|—|schema 无此动作|BLOCKED（能力缺口，沿前轮）|—|
|受影响先前模块回归|follow_ups loader（源 D-M6-02）|合法空/单条通过、非法整份拒|探针化重写完成，待 harness|M7 内修复；M6 门禁不动|r7/phase1-audit.json|
|离线准入|hub stamp 不动点 + check --allow-unsigned + 离线签名/verify/install_staged|rc=0|PASS|PASS（离线子项）|r7/results/hub-check.txt；r7/phase1-audit.json|
|私钥处理|keygen/sign 后 finally 删除|keys 目录空|PASS|PASS|r7/phase1-audit.json keys_deleted/private_key_files_remaining|

## 三项 P1 修复对账（按审查方改法逐条）

- **R-M7-01（登录 widget 读取错误）**：`main.splash` 登录/清空 handler 的 `ui.login_*_input.text` 字段访问（宿主实测当子 widget 查找失败）改为 `text()` 方法读取、`set_text("")` 清空；两处读写均加 bare-catch 兜底（控件接口不支持时给可见 status 而非 VM 异常）；登录行 50/28→70/34、标签 110→70/50 修下方裁切。凭据仍只经 handler 局部变量进 m2_login_begin，不写 STATE/日志。
- **R-M7-02（坏任务错误循环+假就绪）**：load() 的 tasks.json 加载从「非 nil 即赋 TASKS」改为数组+成员（对象且非空字符串 id）门禁；损坏时原文保留、写 tasks.json.recover 并读回逐字节核实、STATE.tasks_pending_recovery=true 阻断 saveTasks/偏好写/原子写三条写路径、status 显示真实异常而非「准备就绪」；tick 的 `catch _`（宿主实测异常真实发生时报 `variable _ not found in scope`，30 条/场来源）改无绑定 bare catch + 累计计数可见诊断；左栏新增 banner 与两个显式恢复 Chip（保留原文/用内存覆盖，均先备份校验）。
- **R-M7-03（合法提醒误判损坏）**：宿主 typeof 语义未证实（review 实测合法对象也不满足 `typeof(x)=="object"`），按改法不再猜 typeof 表示，loader 顶层/数组门禁、成员 validator、受控恢复读回校验统一改行为探针：`map_len()` 仅对象注册（数组/标量调用抛异常被 bare catch 捕获）判对象；`len()`+排除对象+`to_string` 相等性排除字符串判数组；`trim()` 判非空字符串；`v - v == 0` 判数值（NaN/bool/字符串/对象/数组均拒）。load 与恢复共用 `m7_followups_schema_ok`。pending 写保护、原文备份读回、失败传播全部保留，安全边界未放宽。

## 尚未完成

- 探针与控件方法（text()/set_text()/map_len/trim/减法和 bare catch）在固定发行宿主上的行为**未经实证**：依据是宿主实测反例（.text 字段访问失败、catch _ 失败、typeof 假设失败）+ 项目内参考源码（text_input.rs:2390/2394 script-call；object.rs/array.rs 方法注册表），最终判定权在驱动 harness 复核（REQUEST_build_r7）。
- 可信登录成功/失败链、三角色业务全链、真实模型三链、同 Store 跨进程重启、精确故障注入：NOT_RUN / 具体 BLOCKED（白名单缺口沿前轮，未改）。
- A-M7-01（app/README.md 旧入口/旧版本话术）、A-M7-02（材料历史表述/媒体）：P2 建议挂账保留，本轮按修复轮规则未动。
- P06/P07/P08：UNASSESSED/NOT_RUN，本轮无发布、无递交、无收录动作。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M7/r7/CANDIDATE.json`
- 冻结包：`runtime/optimization/2026-10-09/M7/r7/release/octosense-repair-0.1.0-f/`，digest=`9e1f7aec09785858c744272048afd786c02dee05c1a29aa3838cca8db05ed5cf`，hub check rc=0（r7/results/hub-check.txt）
- 离线 catalog/Store/seeds：`r7/store/`、`r7/seeds/`（7 场，fixture 与 review_r1_2104 同口径、独立新造标记）；私钥已删（phase1-audit.json）
- harness 请求：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r7.json`（7 场，needs_model=false，白名单校验全过）
- 原生截图/日志：待驱动执行后存 `M7/native-runs/build_*_REQUEST_build_r7/`
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
