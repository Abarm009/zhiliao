# M7 实施报告 r11（修复轮）

- 模块 / 目标：M7 同版本总验收与发布准备 —— 按 M7_REVIEW_r13（2026-10-14，结论 BLOCKED，未闭合业务 P1=0）的缺陷清单逐条回写，不发散。
- candidate_id / base_candidate_id：**M7-r10-worktree / M7-r9-worktree**（不变）。本轮无业务代码改动，冻结包不重新冻结：工作树 `app/bundle/main.splash` SHA-256 `ee8f541468304b710d87fbf0cda8416939c57c7f762b32f624fde8637f5b6a44` 与冻结包 `M7/r10/release/octosense-repair-0.1.0-i/main.splash` 逐字节一致（本轮重算核对），bundle digest 仍 `958f2875b7a5151bb8bcf086f1b34bbafcadd6a7355cac4ba75f431fb3d23b03`。
- HEAD / 未提交差异：HEAD=`8d730569546cb57310944bb299695134df773b9d`；未提交差异沿 r10 dirty.diff，本轮新增改动仅为下表 3 个文档/台账文件。
- 目标宿主：**rc.6** `runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app`，octosense SHA-256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`，kernel `3bb242ac295493cf17ab61458e5cc76328cd3ec8e77aa7f2d22da08ceefe9980`（与 host-rc6/sha256.txt 及 r13 实测一致）。
- 已检查的前置 Review：M7_REVIEW_r13（最新）；M6 仍 BLOCKED（M6_REVIEW_r14），按挂账裁决不代修。
- 本轮修改文件与原因：
  | 文件 | 对应清单项 | 改动 |
  |---|---|---|
  | `app/README.md:5` | A-M7-01 | 旧「M7 r4 staging / r2 路径」入口更正为当前候选 0.1.0-i（r10 staging）+ 当前宿主 rc.6 + 最新 Review 状态（BLOCKED，R-M7-02 语法反例已闭合） |
  | `app/README.md:7` | A-M7-01 | 「走完整闭环」补充为设计目标/历史 Web 后端实证；明示当前原生候选完整业务链 NOT_RUN，不作当前状态依据 |
  | `M7/r10/release/release-materials/SOURCES.md` §2 + 顶部校正注记 | A-M7-01 | 宿主条目由历史 rc.1 哈希更正为当前 rc.6 哈希（rc.1 保留为历史定位）；bundle 字节/digest 未变 |
  | `M7/r11/evidence/BLOCKED_CONTROL_GAP_r11.md` | R-M7-02 残余 / B-M7-R13-CONTROL | 控制能力缺口最小复现与定位（见下） |
- 桌面 UI/交互变化：无。接口/数据迁移：无。他人改动：全部保留，未 reset/stash/覆盖。

## 清单逐条回写

| 原编号 | 审查方方案 | 本轮处理 | 状态 |
|---|---|---|---|
| R-M7-02（语法/加载反例） | 已由 r13 独立实测 CLOSED；不继续重写已通过的 JSON 判据 | 不改代码；工作树与冻结字节一致性本轮重算复核 | CLOSED 保持 |
| R-M7-02 残余恢复证据 / B-M7-R13-CONTROL | 交付同 Store 原生重开、恢复写点故障、认证后两分支的可运行证据；缺控制能力时维持 BLOCKED，不制造终态或伪会话 | 静态核对 request.schema.json（SHA `d5d79a63…`，`additionalProperties:false`，scenario 仅 13 个允许键）：无同 Store 重开控制、无写点故障调度；type/key 在 rc.6 未实现；ui_actions 授权状态记录冲突（CONTEXT 载 10-12 23:50 授权，r13 载当前禁止），本轮按审查方口径不使用。最小复现与解阻条件已写 `M7/r11/evidence/BLOCKED_CONTROL_GAP_r11.md`；不提交重复登录截图请求 | **BLOCKED 维持**（非业务 P1） |
| R-M7-02-FEEDBACK / A-M4-R13-01（双坏盘任务说明被覆盖） | P2 建议挂账；「如构建方处理建议」仅改 login_hint 取值 | 本轮不处理（P2 建议项，非必修；避免在 BLOCKED 主导结论下触发无必要的重冻结/回归风险） | P2 挂账保留 |
| A-M7-01（旧入口/宿主来源过时） | 校正已有入口、宿主定位及历史/当前状态 | 已修（上表 3 文件）；请审查方按最终材料重新核摘要 | 已修复，待复核 |
| A-M7-02（listing placeholder / 完整演示欠交） | 保留 NOT_RUN，最终业务截图/演示到位后更新 | 无认证链与业务运行证据，无法产出真实业务演示；不造假 | P2 挂账 / NOT_RUN |
| P06 / P07 / P08 | 无本候选外部动作 | 无 publish / listing / push / issue / 消息 | NOT_RUN |

## 验收运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|—|—|本轮无代码改动，未请求新 harness 运行（避免重复登录截图）|NOT_RUN|r13 H 已覆盖可表达范围|
|权威状态与回执|—|—|认证后恢复/普通写拒绝缺 harness 控制|BLOCKED|M7/r11/evidence/BLOCKED_CONTROL_GAP_r11.md|
|失败与重试|schema 静态核对|确认控制是否可表达|同 Store 重开/写点故障不可表达|BLOCKED|同上|
|重启恢复|schema 静态核对|同上|不可表达|BLOCKED|同上|
|受影响先前模块回归|main.splash 未动；digest/字节重算|不回归|工作树==冻结包（ee8f5414…）|PASS（静态子项）|本报告上文|

冷启动解析清零：本轮无代码改动，沿用 r13 实测 24 场 [E]=0；未回归风险。

## 尚未完成

- R-M7-02 残余恢复链证据：**BLOCKED**（harness 控制缺口，见证据文档；需驱动侧受控接口，构建方不可单方面解决，不造伪证据）。
- R-M7-02-FEEDBACK / A-M4-R13-01：P2 挂账（双坏盘任务说明被提醒错误覆盖）。
- A-M7-02：P2 挂账 / NOT_RUN（真实业务截图与 2–3 分钟演示欠交）。
- 正常/退回/真实模型完整链、认证后恢复、U 系列完整项：NOT_RUN（沿 r13 台账，不冒充）。
- ui_actions 授权冲突（CONTEXT 10-12 授权 vs r13「当前禁止」）：提请澄清；非本轮唯一阻塞理由。
- P06/P07/P08：NOT_RUN，无外部动作。

## 交接

- 候选：`M7/r10/release/octosense-repair-0.1.0-i/`（digest `958f2875…`；本轮未重冻结，字节未变）。
- 本轮证据：`runtime/optimization/2026-10-09/M7/r11/evidence/BLOCKED_CONTROL_GAP_r11.md`；文档改动 diff 见 git 工作树。
- GATES.json M7 → READY_FOR_REVIEW；最终判定等独立 Review。
