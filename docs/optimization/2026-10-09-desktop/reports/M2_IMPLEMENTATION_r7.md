# M2 实施报告 r7

- 模块 / 目标：M2 可信身份与可靠任务执行 · 修复轮（按 M2_REVIEW_r7.md 缺陷清单逐条，不发散）。
- candidate_id / base_candidate_id：**M2-r7-worktree / M2-r6-worktree**。
- HEAD / 未提交差异 / 源文件哈希清单：
  - HEAD `8d730569546cb57310944bb299695134df773b9d`（dirty，同前两轮）。
  - `app/bundle/main.splash` 440604 字节，SHA-256 **8d82606aaf22e7526a39108ed8c6021359db53ecb48f8ac58fb147a4c7c5a143**；r7 改前快照 `runtime/optimization/2026-10-09/M2/r7/main.splash.before-r7`（即 r6 受审版 76f00c37…）；摘要对照 `M2/r7/evidence/main_sha256.txt`。
  - 冻结清单（含 identities/manifest/model_config/GATES/身份表/harness）：`M2/r7/native-prep/snapshot-start.json`。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定发行宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，沿用 r6/r7 审查 pin，本轮未触碰）。
- 实际模型路由检查结果（开发会话）：本构建方为 Kimi-K3（Abram 2026-10-11 21:03/21:05 裁决）；无法读取主会话 Router 内部状态，不声称路由已核验。
- 已检查的前置 PASS 报告：M1 仍 FAIL（挂账，不伪造前置）；本轮遵守串行门禁，只做 M2。
- 本轮修改文件与原因（只修 Review r7 清单项）：
  1. **D-M2-01 界面空白根因** — `app/bundle/main.splash` UI 段整体重构为宿主已验证的 probe 模式（M0 r10 探针在同一二进制上实证）：91 个 `name := Widget{...}` 命名控件从 `SolidView` 体内**提升为脚本顶层全局**（原位留裸名引用），全文 94 处 `ui.<name>` 改为直接按名引用（注释除外）；脚本末尾以 `return root` 收尾（probe 末尾 `return body` 同款挂载方式）。原 `ui` 句柄在本宿主顶层 fn 中 "not found in scope"（review_r1_2104 cold host.log 全部 23 条 `[E] variable ui not found in scope` + 8 条 `set_text on NotFound` 均源于此）。变换脚本 `M2/r7/scripts/m2_r7_ui_hoist.py`（括号匹配跳过字符串/注释；名称唯一性与顶层冲突断言通过；全文 brace depth=0 复核）。
  2. **D-M2-01 控件属性错误** — 删除全部 21 处 `draw_text.text_style.font_weight`（本宿主 TextStyle 无该属性，host.log 逐条 "property font_weight not defined on type"）；移除 8193 行 `知` Logo Label 上不存在的 `draw_bg +:`（host.log "field draw_bg not found in type-check"）。
  3. **D-M2-01/D-M2-07 初始化顺序** — 顶层 `load()`/`loadModelConfig()`/`m4_init_forms()`（原 1046–1049）、`bootReconcilePending()`（原 3401）、`_m1_init_selection()`+`saveState()`（原 8139–8140）全部移到脚本末尾集中初始化块（`return root` 之前），消除 host.log:43–60 的 `migrateJsonlLegacy/m5_init_forms/m6_init_forms 等 not found in scope` 运行错误；迁移函数先于调用点定义，D-M2-07 的"迁移未执行"顺序根因闭合。
  4. **D-M2-01 视图状态** — `loadViewState` 改为白名单字段并入（selected_task_id/selectedIdx/nav/filter/search/detail_tab/panel/pending_input/page/status/demo_view_as），不再 `STATE=raw` 整体替换；旧 state.json 缺省的 draft_*/m6_*/last_idem_hit 等字段由默认声明补齐（消除 `property m6_follow_ups/draft_bind_asset not found in prototype chain` 级联错误）；actor/凭据/锁状态不从持久态恢复。
  5. **D-M2-01 空 catch 体** — 3 处 `catch _ { }`（loadModelConfig 等）补幂等语句，消除 host.log:232 `variable _ not found in scope` 类风险。
  6. **D-M2-01 授权子项** — `m2ReplayAtTop` 增加 `visible(t, getMe())` + 项目匹配检查；`bootReconcilePending` 三个循环（pending/needs_verify/补事件）逐 task 经新顶层 `_m2_reconcile_allowed`（findTaskById + 项目匹配 + visible）门控，会话活跃不再替代授权。
- 桌面 UI/交互变化：视觉布局不变（同字节控件树，仅挂载方式与非法属性修正）；`知` Logo 去底色块保留文字。登录/任务界面是否能真实渲染**待 harness 冷启动证实**（见交接）。
- 接口 / 数据迁移 / 旧数据恢复方式：迁移/备份/恢复协议源码本轮未改（D-M2-07 备份格式子项见"尚未完成"）；仅修复迁移调用顺序。
- 已有别人修改的保留与适配：未改动 M3/M4/M5/M6 业务函数体；hoist 变换对它们是纯结构搬迁（控件构造参数与闭包原文保留）。
- 启动步骤 / 隔离数据位置：harness 请求 `M2/native/REQUEST_build_r7.json`（5 场景，沿用 r6 seeds 结构 + 新 digest）；离线签名 Store/种子 `M2/r7/native-prep/`（Abram 授权 A 范围内；私钥已删除，`offline-store-evidence.json` 记录 `private_keys_deleted`，keys 目录复核为空）。
- 应用运行模型/provider：全部场景 `needs_model=false`，0 次真实模型调用；G0-E 延期缺口（Abram 已裁决，M3 到期），本模块不算阻塞。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|语法/解析|vendored makepad parser（octoscript-core check_vm_compatibility_named，max_source_bytes=2MiB、max_syntax_tokens=4Mi 以匹配宿主预算）|无诊断|PASS（test ok）|PASS（静态）|`M2/r7/evidence/vendored_parser_check.txt`；测试 `octoscript/crates/octoscript-core/tests/m2_r7_bundle_parse.rs`|
|本地 catalog 安装|hub keygen/certify/stamp/sign-manifest + install_probe（沙箱隔离 HOME，离线）|本地安装同字节|LOCAL_INSTALL_VERIFIED，digest `ea2b64af…`，installed==bundle main sha|PASS（本地路线）|`M2/r7/native-prep/offline-store-evidence.json`、`seed-manifest.json`、`snapshot-start.json`|
|真实桌面操作|REQUEST_build_r7.json 已写，驱动沙箱外执行|**NOT_RUN（等驱动执行）**— 本轮构建方按裁决不自行启动宿主|NOT_RUN|`M2/native/REQUEST_build_r7.json`；结果将落 `M2/native-runs/build_*_REQUEST_build_r7/`|
|权威状态与回执|源码层：回放/恢复现逐 task 核权限|—|源码已改；动态未执行|NOT_RUN（动态）|main.splash `m2ReplayAtTop`/`_m2_reconcile_allowed`|
|失败与重试|D-M2-02/03/04/05 核心|—|本轮未改（见尚未完成）|NOT_RUN|—|
|重启恢复|初始化顺序修复后 boot 对账可真正执行|—|动态未执行|NOT_RUN|—|
|受影响先前模块回归|未改其他模块文件|—|—|NOT_RUN|—|

## 尚未完成

- **D-M2-02（确认意图/不可变 payload/创建 unknown 可重复执行）**：未修，FAIL 维持。本轮时间盒内优先 D-M2-01 界面渲染（Abram 21:03 最高优先）。
- **D-M2-03（task/final/event 关联恢复协议）**：未修，FAIL 维持。
- **D-M2-04（version++ 误判未知动作、needs_verify 仅核版本）**：未修，FAIL 维持。
- **D-M2-05（锁非原子双赢家、创建绕过串行边界）**：未修，FAIL 维持。
- **D-M2-07 备份格式/恢复协议一致性子项**：源码未改；仅"迁移未执行"的调用顺序根因已闭合。FAIL 维持。
- **D-M2-06**：白名单根因保持闭合，本轮未触碰；完整回归 NOT_RUN。
- harness 冷启动证据：请求已交接驱动，本轮构建方未取得原生截图/host.log（裁决禁止自建宿主）；cold 结果与 frames 路径将在驱动执行后于 `M2/native-runs/build_*_REQUEST_build_r7/` 可查。

## 交接

- 候选：`M2-r7-worktree`（工作树当前 main.splash，SHA-256 8d82606a…）；候选清单/快照 `M2/r7/native-prep/snapshot-start.json` + `seed-manifest.json`。
- 变换与验证脚本：`M2/r7/scripts/m2_r7_ui_hoist.py`、`octoscript/crates/octoscript-core/tests/m2_r7_bundle_parse.rs`（`cargo test -p octoscript-core --test m2_r7_bundle_parse`）。
- 原生验证请求：`runtime/optimization/2026-10-09/M2/native/REQUEST_build_r7.json`（5 场景：cold_login_view 含两次 taps、capture；clean_ndjson / older_backup_newer_history / bad_event_history / unknown_and_higher_version；needs_model=false）。
- 证据：`M2/r7/evidence/vendored_parser_check.txt`、`main_sha256.txt`、`prep_summary.json`。
- 编码方自评：**READY_FOR_REVIEW**（等独立 Review 与驱动 harness 执行；不给自己 PASS）。
