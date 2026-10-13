# M3 实施报告 r7

- 模块 / 目标：M3 真实输入与AI报修 —— 修复轮，按 `M3_REVIEW_r7.md` 缺陷清单逐条修复，原编号回写。
- candidate_id / base_candidate_id：**M3-r7-worktree / M3-r6-worktree**（冻结清单 `runtime/optimization/2026-10-09/M3/r7/CANDIDATE.json`）。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty（含全部他人改动，未 reset/stash/删除）。主源 `app/bundle/main.splash` 473410 字节，SHA256 `a6f55a21aa8ccd70e2bcc9a886dfdedab996b7811f6b447e62fd49a20d8cdee8`；manifest/model_config/identities 哈希见 CANDIDATE.json。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/.../octosense`，SHA256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`（沿用，未自行启动）。
- 实际模型路由检查结果（开发会话）：本会话为 Kimi-K3（Abram 2026-10-11 21:03 指定）；未声称 Router 切换。
- 已检查的前置 PASS 报告：无——M2 最新为 FAIL（M2_REVIEW_r8），按前序挂账裁决继续本模块局部修复，不伪造前置通过。
- 本轮修改文件与原因（全部按审查方清单改法）：

| 缺陷 | 改动 | 位置（改后行号以源为准） |
|---|---|---|
| D-M3-01 | 反转 M2 r7 的 widget 顶层提升（r7 Review 实证 51 条 variable-not-in-scope + budget exceeded + view=false）：91 个命名 widget 回到根树内联 `name := Type{}`，函数/处理器恢复 `ui.<name>`（splash.rs `inject_splash_ui_handle` + startup.splash/apps/maps 实证模式），根视图改为脚本末位裸 `root` 表达式，顶层 init 不再在视图安装前调 `refreshDesktop()`（首刷由 1Hz tick 承担） | `app/bundle/main.splash` 根树段；工具 `M3/r7/scripts/m3_r7_unhoist.py` |
| D-M3-02 | `editRawText` 持久化 `STATE.pending_input` + saveState；`tick()` 一次性恢复到 TASK_INPUT 与 `ui.zh_input`（冷启动不再丢未提交原文） | editRawText / tick |
| D-M3-03 | `_currentFactsVersion` 指纹覆盖 services/category；apply 落 `task_id/task_version/evidence_version_at_apply` 快照；新增 `_currentBindingStaleReason()`，采纳守卫 `_suggestionAcceptGate` 与首次确认 `confirmDraftModelBound` 共用 | 3802 附近 / 2746 附近 / confirmDraftModelBound |
| D-M3-04 | `_validateSourceEntry`：非空 quote 一律降 `unverified_text`（引文不可对照事实库核验）；事实无 version 字段时模型任意 version 降 `unverified_text`；category 白名单枚举不再直接 verified | _validateSourceEntry |
| D-M3-05 | 新增 `_authorityCheckConfirmedOpen()` 磁盘权威对账器（磁盘任务 OPEN + actions.jsonl 精确 confirmDraft final 回执 + events.jsonl 同 action_id confirm_draft 事件）；confirmDraft 正常与重放路径、createDraftFromPanel 创建重放三路径共用；创建重放不再把 create 动作 ID 当 final_action_id；任务已建未确认时恢复原意图（选中同任务走 confirmDraft，不 newId） | confirmDraft / createDraftFromPanel |
| D-M3-06 | `_computeResolvedAmbiguous` 逐字段判定：空间歧义只由人工选空间解决；设备歧义只由人工选备选设备解决且重核事实（存在/同项目/在用）；去掉"选设备消掉所有字段"的统一放行 | _computeResolvedAmbiguous |

- 桌面 UI/交互变化：根视图应恢复真实渲染（待 harness 实证）；未提交原文在重启后恢复到输入框。
- 接口 / 数据迁移 / 旧数据恢复方式：无协议变更；state.json 的 pending_input 字段沿用既有声明（r7 前已恢复读取，本轮补上写入与控件恢复）。
- 已有别人修改的保留与适配：未触碰 M2/M4/M5/M6 业务逻辑；M4/M5/M6 的 widget 一并按同一宿主模式内联（它们与 M3 共享同一 main.splash，不内联则整个根视图无法构建——这是 D-M3-01 明确要求的"最小共有加载依赖"修复，未改其业务行为）。
- 启动步骤 / 隔离数据位置：harness 请求 `M3/native/REQUEST_build_r7.json`（3 场景，needs_model=false）；离线签名 store `M3/native/build_r7/`（anchor `0a6b06b8…`，digest `b81fedb2…`，私钥已删，证据 `offline-store-evidence.json`）；证据目录 `M3/r7/`。
- 应用运行模型/provider：MiniMax / MiniMax-M3 / anthropic messages，配置 `app/bundle/model_config.json`；本轮 0 次真实调用（输入通道缺口，见下）。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|vendored 解析|octoscript-core m2_r7_bundle_parse|无诊断|PASS|PASS|cargo test 输出（本轮运行 ok）|
|静态扫描|ok 保留名/三元/函数完整性 + r7 结构断言|pass:true|pass:true|PASS|`M3/r7/evidence/r7_static_check.json`|
|修复验证 26 项|r7 清单逐条源码断言|26/26|26/26|PASS|`M3/r7/evidence/r7_fix_verification.json`|
|离线 store|keygen/certify/sign/verify/install_staged/may_run|rc0|rc0|PASS|`M3/native/build_r7/offline-store-evidence.json`（私钥已删并记录）|
|真实桌面操作|harness 3 场景冷启动/导航/capture|零作用域错误、view=true、表单渲染|待驱动执行|NOT_RUN（已提交 REQUEST_build_r7.json）|`M3/native-runs/build_r7_REQUEST_build_r7/`（待产出）|
|权威状态与回执|AI/手工确认全链|精确 final 回执+任务+事件一致|NOT_RUN|NOT_RUN（键入通道 BLOCKED）|—|
|失败与重试|丢响应/重复确认/恢复|unknown 保原意图、原键恢复|NOT_RUN|NOT_RUN|—|
|重启恢复|pending_input 恢复|原文回控件|NOT_RUN|NOT_RUN|—|
|受影响先前模块回归|M2 登录/根视图|根视图渲染|NOT_RUN|NOT_RUN|—|

## 尚未完成

- **原生运行证据 NOT_RUN**：我不启动宿主（Abram 12:12 裁决）；REQUEST_build_r7.json 已就位，等驱动沙箱外执行。冷启动零作用域错误 / view=true / 表单可操作需以该证据为准，本报告不预声称。
- **键入通道 BLOCKED（沿用）**：固定宿主无 `--test-action type:`（M2_REVIEW_r5 / M3_REVIEW_r7 实证 unknown action），真实中文键入、UI 触发真实 MiniMax、动态交错不可执行；需驱动/宿主侧提供合规输入通道。真实 MiniMax 累计 3 次（r3 Python），未超 10 预算。
- **needs_model 场景本轮未请求**：键入通道缺失时 UI 触发模型不可达，守住预算；配置/net 准入与提示词绑定值沿用 r6 改善。
- M0/M1/M2/M4–M7 挂账缺陷不修（用户指示）；M2 确认/读回依赖的 M3 侧消费已按 D-M3-05 收紧。
- 说明：`M3/r6/evidence/r6_static_check.json` 被 r6 静态脚本原地刷新（内容等价，仍 pass:true）；r7 独立证据在 `M3/r7/evidence/`。

## 交接

- 候选清单：`M3/r7/CANDIDATE.json`（四项冻结对象哈希 + anchor/digest）。
- 原生截图/日志：待 `M3/native-runs/build_r7_REQUEST_build_r7/` 产出。
- 证据：`M3/r7/evidence/r7_static_check.json`、`r7_fix_verification.json`（26/26）、`M3/native/build_r7/offline-store-evidence.json`。
- 测试命令：`cd octoscript && cargo test -p octoscript-core --test m2_r7_bundle_parse`；`python3 runtime/optimization/2026-10-09/M3/r7/scripts/m3_r7_fix_verification.py`。
- 编码方自标 **READY_FOR_REVIEW**；最终 PASS 等待独立审查。
