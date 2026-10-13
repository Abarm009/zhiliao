# M6 实施报告 r7 · 桌面体验收口与持续跟进（修复轮，Kimi-K3）

- 日期：2026-10-12，Asia/Shanghai；构建方：Kimi-K3（Abram 2026-10-11 21:03 裁决）；无子代理。
- candidate_id：`M6-r7-worktree`；base：`M6-r6-worktree`；清单：`runtime/optimization/2026-10-09/M6/r7/CANDIDATE.json`。
- 依据审查方缺陷清单：`docs/optimization/2026-10-09-desktop/reports/M6_REVIEW_r7.md`（必修仅 D-M6-02 / D-M6-03 / D-M6-04）。
- 本轮性质：修复轮。只修清单项，严格按审查方「具体改法」，不发散、不修前序挂账模块、不进入 M7、不覆盖他人改动。
- main.splash 后态：SHA-256=`dd3f4a5e8d87cc45bbd6ac38d1bfa63d31a194b1474826173aef1b8e4023c22f`，10747 行 / 519600 B。当前 digest=`3f17a209a6fb1b88a8aae401051527493833e1c713bde670943d91b53bb09a8f`。HEAD=`8d730569546cb57310944bb299695134df773b9d`（工作树另有他人未提交改动，全部保留）。
- 前置如实：M5=FAIL（M5-r7-worktree / M5_REVIEW_r8.md）挂账延续，本轮不伪造前置、不修 M5。
- 目标宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（沿用审查冻结；本轮未启动，harness 请求交驱动）。
- 模型/provider：本轮 needs_model=false，真实 MiniMax 调用 0 次（≤10 预算留给审查轮三组新描述实证）；无密钥入码/日志/报告。
- 实际模型路由检查（开发会话）：当前会话无 Router 切换/核验接口，不冒称已切换；按裁决构建方=Kimi-K3。

## 逐条修复（按原缺陷编号回写）

### D-M6-02 — 异常提醒文件被当作正常，恢复保护未闭合 → 已按审查方案修复（源码级）

- 位置：`m6_load_follow_ups` / 新增 `m6_follow_up_record_valid` / `m6_followups_mark_corrupt`（约 :1864–1940）、`m6_explicit_recover_follow_ups` 读回段（约 :2050）、`m6_invalidate_for_task` / `m6_invalidate_for_appointment`（约 :2190/:2220）、`m6_cmd_invalidate`（约 :2640）、「我已知悉」Chip（约 :9540）。
- 修复内容（严格按审查方改法「load 及受控读回共用严格 schema 门禁」）：
  1. **严格 schema 门禁**：顶层必须为对象；`follow_ups` 必须为数组（`{"follow_ups":17}` 标量拒绝）；逐条校验——非 nil 对象、`fu_id/task_id/role/kind` 非空字符串、`due_ms` 非 nil 且非字符串/对象/数组、`status` 在四值白名单（ACTIVE/SUPERSEDED/CANCELED/FIRED）。任一失败 → 整份按损坏处理。这直接覆盖审查方两反例：标量 schema 与宿主宽容 parse 产生的 `[null, null, -2104]`。
  2. **损坏统一处理** `m6_followups_mark_corrupt`：保留原文、写 `.recover` 并**读回逐字节核实**（不一致标备份失败）、置 dirty + pending_recovery + 可见 status；不推进内存、不解锁普通写。
  3. **恢复读回与预期内容比较**：受控写后读回改为 `_rb == body` 逐字节比对，不再「parse 非 nil 即放行」；不一致保持 pending、可见错误、可重试。r6 已修的备份核实前置 / 受控写绕闸 / 两个恢复 Chip 全部保留未动。
  4. **失效/登记/关闭调用方消费保存结果**：两个 invalidate 把 `m6_save_follow_ups()` 结果记入 `STATE.m6_followups_last_save_ok`，拒写时置「已记录到内存但保存失败，待重试（未落盘）」；`m6_cmd_invalidate` 拒写时不再显示「已失效 n 条」完成文案；「我已知悉」Chip 消费 `m6_dismiss_follow_up` 返回值，失败显示「提醒关闭未落盘」。
- 验证：静态控制流检查 15 项全过（r7-fix-checks.json）；原生验证走 harness `REQUEST_build_r7.json` 场景 `followup_scalar_schema`（17 B 标量必须被拒、原文保留、pending 置位、.recover 落盘）、`followup_malformed_members`（44 B 坏 JSON 同上，内存不得接受 [null,null,-2104]）、`followup_valid_restore`（合法 ACTIVE 提醒跨冷启动恢复、原文不变），由驱动在沙箱外执行。

### D-M6-03 — 历史/阶段链缺事实与版本绑定，返回建议没有真正进入详情 → 已按审查方案修复（源码级）

- 位置：`m6_request_device_history`（约 :1560）、`m6_request_phase_meaning`（约 :1720）、新增 `m6_response_binding_check`（约 :1545）、`m6_cmd_request_history` / `m6_cmd_request_phase`（约 :2670）、新增 `m6_save_history_view` / `m6_load_history_view` / `m6_cmd_save_manual_entry`（约 :2740）、详情渲染 phase/history 页签（约 :10370/:10400）、左栏人工出口控件（约 :9560）、boot 加载（:1063）。
- 修复内容（严格按审查方改法）：
  1. **固定真实绑定**：两链 `bindRequestVersions(task.id)`（不再传未建任务 sentinel 空串）；history 输入携带真实有权维修历史事实（`[repair_history]` = 本任务 task.notes，限 6 条、截断 60 字）+ `task_version`；phase 输入携带真实事件事实（`[events]` = EVENT_LOG 中本任务事件，限 6 条）且 `event_seq=nil` 时派生本任务真实事件数（不再落 0）。
  2. **回包复核**：新增 `m6_response_binding_check(task, task_version)` —— 重核授权 / actor / project / 到期（expires_at_ms）/ 任务事实版本（latestTaskVersion 与发出时比对）；任一不符 → `STALE_RESPONSE` 审计落盘、建议不落、返回人工可继续文案。两链均接入。
  3. **明确返回 schema**：history 条目必须带非空字符串 `text` 且引用可见；phase 正文必须非空字符串（不再只查非 nil）；结果携带 `request_id`。
  4. **保存并渲染真实建议**：cmd 成功分支把真实 items 正文 / phase 正文（截断 200）+ `request_id` 依据写入 `m6_history_view` 并持久化到 `m6_history_view.json`（严格 schema 恢复）；零有效条目按「无历史说明未知」处理。详情「设备历史」页签现在先渲染 `m6_history_view` 建议正文（[建议·待人工采纳] / [手工历史备注]）再列 AI_REQUESTS_LOG 审计（[审计]）；「阶段说明」页签渲染模型/手工阶段正文 + 显式标注的静态参考。
  5. **真实人工出口**：新增 `m6_manual_entry_input` TextInput + 「存为手工阶段说明」「存为手工历史备注」两个 Chip → `m6_cmd_save_manual_entry(kind)`，人工内容标 `kind=manual`、来源 `manual · <actor>`，仅入建议视图，不写业务字段。模型不直接写业务的边界不变。
- 边界如实声明：真实模型请求本轮 0 次（needs_model=false）；三链真实模型证据、无历史/矛盾/迟到回包的原生行为记 NOT_RUN，交审查轮 harness needs_model 场景实证（预算 ≤10 次，遇 402/欠费立即停并 NEEDS_ABRAM=yes）。解析回归闸保留：VM-compat parser 实测 1 passed，无保留字标识符。

### D-M6-04 — 明确拒写仍反馈「已落盘」→ 已按审查方案修复（源码级）

- 位置：`togglePin` needs_verify 分支（约 :8720）、`m6_save_prefs` finalize catch（约 :2560）。
- 修复内容（严格按审查方改法「精确消费 saved/readback/执行态」）：
  1. **saved=false（确定未写盘，如 tasks_write_failed）**：回退内存 `pinnedBy` 到变更前快照，显示「收藏未保存：<reason>（已回退，未落盘；可重试）」——不再把 saved=false 说成已生效。
  2. **saved=true（已写或结果未知）**：不盲目回滚，维持「已落盘但待核验：<reason>」；version 不递增边界不变。
  3. **finalize 失败的持久对账**：receipt finalize 失败时除标 `needs_verify` 外，另把稳定键（receipt action_id + 写前固定 task_id + 原因 + 时间）落盘到 `m6_reconcile_needed.json`（sandbox 内），后续对账/重试按同 key 恢复；标记写失败也在状态栏可见。
  4. r6 已修的固定读回目标 / 预期 pinnedBy 快照 / missing_target 全部保留未动。
- 验证：静态控制流检查 6 项全过；原生收藏拒写/双主体/重登场景依赖 harness 白名单输入能力（key/type 在 r7 审查中被宿主拒绝），如实记 NOT_RUN/BLOCKED（能力缺口属驱动侧，见 M6_REVIEW_r7 BLOCKED 段）。

## 证据与运行记录

- 静态+语法证据：`runtime/optimization/2026-10-09/M6/r7/results/r7-fix-checks.json`（41/41 PASS，含 VM-compat parser cargo test 实测输出）。
- 函数追踪：`runtime/optimization/2026-10-09/M6/native/build_r7/affected-functions.json`、`source-traces/`（18 个触及函数的行号+SHA-256+全文）。
- 开始快照：`native/build_r7/start-snapshot.json`（main/manifest/model_config/identities/harness/宿主摘要；head=`8d73056`）。
- 离线签名：`native/build_r7/offline-store-evidence.json`（Abram 授权 A；当前 digest 专属；私钥已删除，`remaining_key_files=[]`；无 publish/listing/联网/push）。
- harness 请求：`runtime/optimization/2026-10-09/M6/native/REQUEST_build_r7.json`（schema 校验 PASS；4 场景；needs_model=false；请求驱动输出到 `M6/native-runs/build_r7_REQUEST_build_r7/`）。
- **冷启动交接**：按 2026-10-11 21:03 裁决，本轮构建的 harness 冷启动请求已随交接提交（`cold_fresh` 场景期望：host.log 零解析错误、登录/任务界面真实渲染、`capture:cold_fresh_final.png`）。原生执行结果由驱动在本阶段结束后产生，本报告不预判其结果。
- 本轮未执行：真实模型调用（0 次）、原生 UI 交互（构建方不启动宿主）、同盘进程重启/动态撤权/运行中故障注入（harness 白名单能力缺口，沿用审查方 BLOCKED 定性）。

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|VM 兼容解析|cargo test m2_r7_bundle_parse|零诊断|1 passed|PASS（源码级）|r7-fix-checks.json|
|D-M6-02 schema 门禁|静态控制流 + harness 3 场景请求|坏输入保护原文|静态 15/15；原生待驱动|源码 PASS / 原生 PENDING|build_r7/ + REQUEST_build_r7.json|
|D-M6-03 事实/版本/渲染闭环|静态控制流|绑定+复核+真实渲染+人工出口|静态 17/17；真实模型 0 次|源码 PASS / 模型 NOT_RUN|同上|
|D-M6-04 拒写反馈|静态控制流|saved=false 回退+准确文案|静态 6/6；原生注入不可达|源码 PASS / 动态 NOT_RUN|同上|
|真实桌面操作|harness cold_fresh 等|零解析、登录/任务渲染|待驱动执行|PENDING|REQUEST_build_r7.json|

## 尚未完成（如实保留，不用「基本完成」）

- G0-F 后台常驻：仍仅前台 reopen/tick 扫描，不称后台常驻；原用例继续 BLOCKED/NOT_RUN。
- T25/T26/T33/T34/T35/T36 真实模型链路：NOT_RUN（本轮 0 请求；预算留给审查轮）。
- T28/T29/T30/U01–U12 的原生交互部分：可信键入/Tab 被宿主白名单拒绝（M6_REVIEW_r7 实测 :39–40），指定步骤 BLOCKED；不以静态检查或旧截图替代。
- M5/M4/M3/M2/M0 前序挂账缺陷不修不碰；M6 仅消费既有契约。
- 三视口/150% 放大/长中文/演示草片：等 harness 复跑；本轮未伪造截图。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M6/r7/CANDIDATE.json`。
- 原生截图/日志：待驱动执行 REQUEST_build_r7 后落 `M6/native-runs/build_r7_REQUEST_build_r7/`。
- 实际测试命令：`PATH="$HOME/.cargo/bin:$PATH" cargo test -p octoscript-core --test m2_r7_bundle_parse`（于 `octoscript/`）；`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M6/native/prepare_build_r7.py`。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入 M7。
