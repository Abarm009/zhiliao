# M6 实施报告 r8

- 模块 / 目标：M6 桌面体验收口与持续跟进 · 修复轮 r8 —— 严格按 M6_REVIEW_r9 缺陷清单修 D-M6-02 / D-M6-03 / D-M6-04 的剩余子项；已关闭子项（合法加载、null/截断整份保护、saved=false 回退、数量函数、formatApptLine）不重做。
- candidate_id / base_candidate_id：`M6-r8-worktree` / `M6-r7-worktree`。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d`；工作树含他人未提交改动，全部保留未动。修改后 `app/bundle/main.splash` SHA256=`d98a32720c17…`（完整值见 `runtime/optimization/2026-10-09/M6/r8/CANDIDATE.json` 与 `native/build_r8/start-snapshot.json`）；bundle digest=`561c535132bf…`。
- 目标宿主 / 二进制：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（沿用，未改动；哈希在 start-snapshot.json）。本机未启动宿主；原生验证交驱动 harness（REQUEST_build_r8.json）。
- 实际模型路由检查：本轮无模型调用（needs_model=false，预算留审查轮 ≤10）。
- 已检查的前置 PASS 报告：无新前置；M5 仍 FAIL 挂账（按 Abram 裁决继续局部修复）。
- 本轮修改文件与原因：仅 `app/bundle/main.splash`（外科式修补，见下）+ 新增 r8 准备脚本/请求/候选/证据文件。

## D-M6-02 剩余项修复（严格时间 schema / 可见恢复反馈 / 写后核验）

1. `m7_is_strict_number_value(v)`（新增，紧邻 m7_is_number_value）：先排除 bool（`== true`/`== false` 走结构化相等 deep_eq，无数值强转——已在 vendored makepad `equality.rs`/`numeric.rs` 核实：`as_number` 只认 f64，算术中 bool/字符串走 `cast_to_f64` 兜底才被隐式接受）、再排除字符串（trim 探针）、对象/数组（既有行为探针），最后才用 `v-v==0` 排 NaN。数值 1 通过；`true`/`false`/`"1"`/null/对象/数组均拒。`m6_follow_up_record_valid` 的 due_ms 改用此门禁（load 与受控恢复共用 `m7_followups_schema_ok` 随之生效）。M7 自用的 `m7_is_number_value`（行 1135/1141/1144）不动，不越权改 M7 语义。
2. `m6_save_follow_ups` 普通写：写成功后读回逐字节比对 `_rb == body` 且过 `m7_followups_schema_ok`，全过才清 dirty；否则 dirty=true + 可见失败文案 + 返回 false。与受控恢复同一标准。
3. `m6_status_label_text`：故障优先于空态 —— pending_recovery / dirty / 失败·待恢复·待核验状态的检查移到空态分支之前（r9 实测坏盘画面只显示空态）。
4. 左栏布局：状态聚合 / 提醒 banner / 任务 banner / 数量 / 关闭与 4 个恢复 Chip 整块上移到左栏顶部固定可见区（导航 Bar 之前）；旧位置在两个 `height: Fill` 弹簧之后，非滚动 Down 容器把它们裁到视口外（r9 U09 子项 FAIL）。

## D-M6-03 剩余项修复（协议 / 事实 / 完整绑定 / 缓存恢复 / 人工保存结果）

1. 两链 system 改为明确 JSON 协议（说明返回结构 `{"items":[{text,ref_type,ref_id}]}` / `{"phase":..., "references":[...]}`、来源约束、无历史返回空、不编造、不写业务），替代 `history_only_no_write` / `phase_only_no_write` 标记串（provider 强制 content[0].text 为 JSON）。
2. history 输入 = 有出处的真实设备历史：EVENT_LOG 中同项目、同设备（asset 相同非空）、当前身份可见任务的事件，最新优先限 6 条，每条带 task_id / kind / at_ms / after 事实（截断 120）；未绑设备退化为本任务自身事件。phase 输入 = 本任务最新 6 条事件（不再是最早 6 条），事实读标准字段 `after`（不再读不存在的 `summary`）。
3. `m6_response_binding_check(task, task_version, rid)`：新增核发出时捕获的 rid（`request_id_mismatch`，堵住 A 回包 / B 改写 pending 反例）、`expected_task_id`、当前选择 `STATE.selected_task_id`、facts 版本、evidence 版本；保留 actor/project/到期/任务版本检查。两个调用点同步传入 rid。
4. `m6_validate_reference`：非对象条目拒、缺键 try 读取；task 引用允许同项目且当前身份可见的其他任务（设备历史出处），跨项目/不可见/不存在仍拒。
5. 建议视图持久化带上下文：actor / project / task_version / request_id / expires_at_ms。`m6_save_history_view` 写后读回逐字节核实并返回真实 bool；`m6_load_history_view` 重开重核主体/项目/任务版本/到期/出处（request_id 须在 AI_REQUESTS_LOG 有同任务同主体记录），任一不符 → kind=none + 可见原因；boot 未登录仅载入，登录成功后由 `m2_login_begin` 重核。渲染两侧（phase/history 页签）经新 `m6_history_view_usable(hv, t)` 重核，失效缓存显式提示「已过期或主体/任务已变化」，不混同无建议。
6. 人工出口：`m6_cmd_save_manual_entry` 改用实证接口 `.text()`（与登录控件一致；读取失败如实反馈），消费 `m6_save_history_view()` 返回值 —— 失败显示「保存失败（待重试；输入仍保留在输入框）」，不再无条件「已保存」。两模型链 caller 同样消费保存结果，保存失败覆盖成功文案。
7. typeof 未证实语义清除：本模块新增/触碰处一律用 m7_is_* 探针（含 items/phase/references 读取）。

## D-M6-04 剩余项修复（同 key 偏好对账 / 保存结果消费）

1. `saveState()` 显式返回 true/false（跳过路径返回 false）；既有调用方忽略返回值，行为不变。
2. `m6_save_prefs`：4 处 `saveReceipts()` 全部消费 bool（`_sr1.._sr4`，false 与抛异常同属失败）；`saveState` 跳过（`saveState_skipped`）与抛异常同样算失败。
3. 对账标记增强：`m6_reconcile_needed.json` 携带 receipt_id + task_id + actor + expected_pinned，写后读回逐字节核实。
4. 新增 `m6_pin_marker_read` / `m6_pin_marker_pending_for` / `m6_reconcile_marker_boot`：boot/登录（bootReconcilePending 末尾）按固定 key 核权威盘 pinnedBy —— 一致 → 回执补 final 并清标记（宿主无 fs.remove，空串=无标记，沿用既有约定）；相反 → pending_orphan「确定未提交，可按原 key 安全重试」并清标记；未知（无回执/预撤权/盘不可读/任务缺失/标记非法）→ 保留标记。saveReceipts 失败不清标记。
5. `bootReconcilePending`：pending 与 needs_verify 两个循环对 `togglePin` 回执跳过版本判据（收藏不递增业务 version，版本不变 ≠ 未提交），pending 转 needs_verify 注明未知，交标记对账。
6. `togglePin` 入口闸：同任务存在未清标记时拒绝新 key 盲重做，提示重登/重启让对账收敛。

## 桌面 UI/交互变化

- 左栏顶部固定可见区现在承载：状态聚合、提醒/任务 banner、提醒数量、「我已知悉」、4 个恢复 Chip；导航与筛选顺序不变；AI 触发与人工出口控件仍在左栏下部。
- 详情页签 phase/history 对失效缓存显示显式过期提示。

## 接口 / 数据迁移 / 旧数据恢复方式

- `saveState` 增加返回值（兼容）；`m6_response_binding_check` 加第三参（模块内两个调用点已同步）；`m6_history_view.json` 旧格式（无上下文字段）重开时判未知不恢复正文 —— 有意为之（缺出处不可信）。
- follow_ups.json 契约不变，门禁更严；损坏原文保护与 .recover/.recover.bak 流程不变。

## 已有别人修改的保留与适配

- 未动 M2/M3/M4/M5/M7 任何既有差异；`m7_is_number_value`（M7 使用）保持原语义；左栏 M7 恢复 Chip 仅随整块上移（可见性改善，行为不变）；`saveState` 仅加返回值。git 工作树他人未提交改动未 reset/stash/删除。

## 启动步骤 / 隔离数据位置

- 构建方不启动宿主。harness 请求：`runtime/optimization/2026-10-09/M6/native/REQUEST_build_r8.json`（6 场景，needs_model=false），驱动输出 `M6/native-runs/build_r8_REQUEST_build_r8/`。种子与离线签名 Store 在 `M6/native/build_r8/`（私钥已删，证据 `offline-store-evidence.json`）。

## 应用运行模型/provider

- 本轮 0 次真实调用；model_config 未改；密钥不出现。

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|VM 兼容解析|cargo test -p octoscript-core --test m2_r7_bundle_parse|解析通过|1 passed|PASS|r8/results/r8-fix-checks.json|
|静态断言 41 项|prepare_build_r8.py|全过|41/41|PASS|同上|
|离线签名/安装探针|hub keygen/certify/stamp/sign-manifest/verify + install_probe|当前 digest 沙箱内可装|PREPARED，私钥已删|PASS（沙箱限定）|native/build_r8/offline-store-evidence.json|
|真实桌面操作|harness 6 场景（含 bool/字符串时间反例、恢复入口顶部可见）|整份拒/合法恢复/零解析|待驱动执行|NOT_RUN（交驱动）|native/REQUEST_build_r8.json|
|权威状态与回执|marker 对账/saveReceipts 消费|源码级实现|静态 PASS，动态未跑|NOT_RUN|同上|
|失败与重试|写后读回/保存失败文案/人工出口|源码级实现|静态 PASS，动态未跑|NOT_RUN|同上|
|重启恢复|load 重核 + 登录重核 + marker boot|源码级实现|静态 PASS，动态未跑|NOT_RUN|同上|
|受影响先前模块回归|watched 文件哈希 + 冷启动零解析|不变|watched 全等；冷启动待驱动|部分 PASS|native/build_r8/build-validation.json|

## 尚未完成

- 原生 6 场景（含 r9 的 bool/字符串时间反例与恢复入口可见性）：已交驱动，结果未回 —— NOT_RUN。
- 真实 MiniMax 三链调用、可信登录后交互（点击恢复/收藏/改约/跳回）、150% 放大与键盘：宿主输入通道 BLOCKED（沿用 r9 审查的精确范围），本轮 0 次模型调用。
- G0-F 后台常驻仍 NOT_RUN（仅前台扫描，不宣称后台常驻）；T17/T29/T33/T34/T35/T36 等真实交互项保持 NOT_RUN/BLOCKED，未伪造。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M6/r8/CANDIDATE.json`；证据：`M6/native/build_r8/`、`M6/r8/results/r8-fix-checks.json`、harness 请求 `M6/native/REQUEST_build_r8.json`。
- 实际测试命令：`python3 -B runtime/optimization/2026-10-09/M6/native/prepare_build_r8.py`（rc0，41/41）；`cargo test -p octoscript-core --test m2_r7_bundle_parse`（1 passed）。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
