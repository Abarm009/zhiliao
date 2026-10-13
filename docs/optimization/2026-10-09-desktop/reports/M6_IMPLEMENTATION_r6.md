# M6 实施报告 r6 · 桌面体验收口与持续跟进（修复轮，Kimi-K3）

- 日期：2026-10-12，Asia/Shanghai；构建方：Kimi-K3（Abram 2026-10-11 21:03 裁决）；无子代理。
- candidate_id：`M6-r6-worktree`；base：`M6-r5-worktree`；清单：`runtime/optimization/2026-10-09/M6/r6/CANDIDATE.json`。
- 依据审查方缺陷清单：`docs/optimization/2026-10-09-desktop/reports/M6_REVIEW_r6.md`（必修 D-M6-02 / D-M6-03 / D-M6-04）。
- 本轮性质：修复轮。只修清单项，严格按审查方「具体改法」，不发散、不修前序挂账模块、不进入 M7。
- main.splash 后态：SHA-256=`8dda17002accec8afa630742ae3c34753c1dad8e157941dbb178dd9725ed8ba2`，10464 行 / 503532 B。当前 digest=`15397be72f20b08a51629c832af62372619eb4486f30b4ab6da6d89b503f4e3e`。
- 注意：r6 审查基线（8885 行）之后，其他模块构建方（M2–M5 Kimi-K3 r8）已在同一工作树叠加各自的 append patch（文件增至 10317 行）；本轮保留全部他人改动，只做 M6 清单项的外科修复。

## 逐条修复（按原缺陷编号回写）

### D-M6-02 — 恢复成功分支不可达、备份未核便解除保护 → 已按审查方案修复（源码级）

- 位置：`app/bundle/main.splash` `m6_explicit_recover_follow_ups`（约 :1924）、`m6_save_follow_ups`（约 :2008）、UI 左栏（约 :9389）、runAction 派发（约 :8657）、cmd 层 `m6_cmd_recover_keep / m6_cmd_recover_overwrite`（约 :2540）。
- 修复内容（严格按审查方改法）：
  1. 两分支共用前置：先读原文（失败→保持 pending+可见错误并返回），写 `.recover.bak` 后**读回逐字节比对**（不一致→保持 pending、状态栏可见错误、可重试）。
  2. keep_backup 分支：备份核实后才清 `pending_recovery`/`dirty`。
  3. use_memory 分支：**受控写不走普通 save 闸**（旧实现复用被闸拒绝的 `m6_save_follow_ups`，成功路径不可达），直接构造 body 写盘，写后读回 `parse_json` + `follow_ups` 字段校验，全部通过才解除阻断；任一失败保持 pending。
  4. 既有 UI 中可达的恢复入口：左栏新增两个 Chip「恢复提醒·保留原文」「恢复提醒·用内存覆盖」（仅 `pending_recovery=true` 时生效），并经 runAction 白名单命令 `m6_recoverKeep` / `m6_recoverOverwrite` 派发。
  5. 普通闸不变：`m6_save_follow_ups` / register / invalidate / dismiss 在 pending 下仍一律拒绝。
- 验证：静态控制流检查 7 项全过（r6-fix-checks.json）；原生验证走 harness `REQUEST_build_r6.json` 场景 `followup_corrupt_guard`（坏文件不得被覆盖、pending 置位）与 `followup_valid_restore`（合法 ACTIVE 提醒跨冷启动恢复、原文不变），由驱动在沙箱外执行。

### D-M6-03 — 新增链解析失败、无桌面触发/事实版本闭环 → 解析已清零（源码级实证），触发与绑定已补

- **解析回归**：当前工作树 `main.splash` 在宿主同源 vendored VM-compat parser 下解析通过：`octoscript/crates/octoscript-core/tests/m2_r7_bundle_parse.rs`（`check_vm_compatibility_named`，2 MiB 限制）1 passed；保留标识符 `ok` 与被拒条件表达式在当前树已不存在（`let (ok|err|type|match)` 扫描为零）。两条链函数保留，未以删链换白屏消失。该解析清零发生在本轮之前（同树其他模块构建叠加后），本轮以真实 parser 复核确认并列入回归闸。
- **桌面触发**（审查方改法第 2 步）：新增 `m6_cmd_request_history` / `m6_cmd_request_phase`（当前选中任务 → `m6_request_device_history` / `m6_request_phase_meaning`），runAction 派发 `m6_requestHistory` / `m6_requestPhase`，左栏 Chip「请求设备历史建议」「请求阶段建议」。成功：建议进 `STATE.m6_history_view`（人工采纳位，模型不写业务）并切到对应页签；失败：`STATE.status` 给出 kind + msg + 「人工出口」文案。请求元数据经 `recordModelMeta` 带 task_id/project_id/actor 落 AI_REQUESTS_LOG，「设备历史」页签由 `m6_history_render` 三元组匹配读回——触发→记录→可见闭环接通。
- **旧 caller 绑定**（审查方改法「补旧 caller 明确绑定或明确未建任务种类」）：新增 `_m6_draft_binding_task_id()`；`requestAiSuggestion`（4 处）与 `deliverModelReturn`（3 处）共 7 个 `recordModelMeta` 调用点全部显式传 `task_id`（草稿期未建任务时显式为空串）/ `project_id` / `actor`。
- **边界如实声明**：真实模型请求本轮 0 次（needs_model=false，模块 ≤10 次预算留给审查轮）；`MODEL_CONFIG.enabled` 实际值与无历史/矛盾/迟到回包的原生行为未在本轮执行，记 NOT_RUN，交由 harness 复跑核验。

### D-M6-04 — 读回定位被提前清空、未落盘显示成已落盘 → 已按审查方案修复（源码级）

- 位置：`m6_save_prefs`（约 :2286）。
- 修复内容：函数入口在 eager cleanup 清空 `_PENDING_RESULT` **之前**固定 `_fixed_task_id`（来自 `_PENDING_RESULT.task_id`，runCommandBound 在 :3254 设置）与 `_expected_pin`（内存任务 pinnedBy 快照拷贝）。读回段改为：缺固定目标→`readback_mismatch="missing_target"`→`needs_verify`（不再把 parse 成功当比对通过）；找到任务后磁盘 `pinnedBy` 与**固定预期快照**比对，不再读清理后的 pending 或活内存。togglePin 三态消费（unexecuted 回退内存 / needs_verify 不盲目回滚仅标待核验 / final 记事件）保持不变并已静态核对。
- 验证：静态控制流检查 4 项全过；原生收藏/拒写/读回不一致场景依赖 harness 白名单输入能力（tap/key/type 在 r6 审查中被宿主拒绝），如实记 NOT_RUN/BLOCKED（能力缺口属驱动侧，见审查报告 BLOCKED 段）。

## 证据与运行记录

- 静态+语法证据：`runtime/optimization/2026-10-09/M6/r6/results/r6-fix-checks.json`（17/17 PASS，含 VM-compat parser 实测输出）。
- 函数追踪：`runtime/optimization/2026-10-09/M6/native/build_r6/affected-functions.json`、`source-traces/`（12 个触及函数的行号+SHA-256+全文）。
- 开始快照：`native/build_r6/start-snapshot.json`（main/manifest/model_config/identities/harness/宿主摘要，head=`git rev-parse HEAD` 记录在内）。
- 离线签名：`native/build_r6/offline-store-evidence.json`（Abram 授权 A；当前 digest 专属；私钥已删除，`remaining_key_files=[]`；无 publish/listing/联网）。
- harness 请求：`runtime/optimization/2026-10-09/M6/native/REQUEST_build_r6.json`（schema 校验 PASS；3 场景；needs_model=false；请求驱动输出到 `M6/native-runs/build_r6_REQUEST_build_r6/`）。
- **冷启动交接**：按 2026-10-11 21:03 裁决，本轮构建的 harness 冷启动请求已随交接提交（`cold_fresh` 场景期望：host.log 零解析错误、登录/任务界面真实渲染、`capture:cold_fresh_final.png`）。原生执行结果由驱动在本阶段结束后产生，本报告不预判其结果。
- 本轮未执行：真实模型调用（0 次）、原生 UI 交互（构建方不启动宿主）、同盘进程重启/动态撤权/运行中故障注入（harness 白名单能力缺口，沿用审查方 BLOCKED 定性）。

## 未通过 / 未执行如实保留

- G0-F 后台常驻：仍仅前台扫描，不称后台常驻，原用例继续 BLOCKED/NOT_RUN。
- T25/T26/T33/T34/T35/T36 真实模型链路：NOT_RUN（0 请求；预算保留）。
- T28/U01–U12 原生业务/视口/键盘/演示：等 harness 复跑；不以静态检查或旧截图替代。
- 前序模块（M0–M5）挂账缺陷不修、不改判；他人未提交改动全部保留。
- D-M6-01 / D-M6-05 源码子项保持原关闭状态，本轮未触碰。

## 交接

- GATES.json：M6 `status=READY_FOR_REVIEW`，candidate/base/implementation_report/evidence_root 更新为 r6，`test_counts.r6_fix_checks` 与 `modified_files_sha256` 增补；r6 审查字段与全部历史保留；ACCEPTANCE.json 未改。
- 编码方不自评 PASS；停止在本模块，等待独立 Review；不进入 M7。
- 审查建议入口：先核 `r6-fix-checks.json` 与 driver 的 `build_r6_REQUEST_build_r6/` 冷启动证据（host.log 解析错误数、`cold_fresh_final.png` 业务区），再按 D-M6-02/03/04 验证方式逐项复核。
