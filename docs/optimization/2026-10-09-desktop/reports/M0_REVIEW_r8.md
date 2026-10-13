# M0 独立 Review r8 — r9 候选复核：启动/持久化全链路由审查方独立复现；探针表单「滚动后控件可操作」越级判 PASS，业务 tap 落盘证据不存在

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-10 13:34 CST（Asia/Shanghai）
- candidate_id：`M0-r9-worktree`；base：`M0-r8-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`（本轮复算，与 r9 CANDIDATE.json 一致）
- 审查开始/结束时快照是否一致：开始与结束 `git status --porcelain` 均为同一 17 项，与 `r9/snapshot/snapshot-status-r9-before.txt` 逐行 diff 为空；`app/bundle/main.splash` `8aa1022c…`（55781 B）/ `manifest.json` `e2025193…` 与 r9 `bundle-sha.txt` 一致；业务文件零改动。审查写操作全部在 `runtime/optimization/2026-10-09/M0/review-r8/` 内，未触碰 r9 候选任何文件；旧 B 包（8d73056 提交内容）与当前 v2 工作树未混记——55781B main.splash 是未提交工作树文件，review 证据均以其 SHA 锚定。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r9.md`
- 已核对前置模块 PASS 与受影响回归：M0 无前置模块；r7 Review（Kimi，FAIL）四条必修 D-R7-1/2/3/4 本轮逐条独立复核；D-R5-1/2/3/4/5、D-R6-3 抽查维持闭合（见必需检查表）。
- 实际环境 / 模型路由 / 宿主：darwin；宿主 = `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`（官方 `desktop-v0.1.0-rc.1` macOS aarch64），本轮复算 octosense `3e127963…` / octos-kernel `a3e46a45…`，与 r3 receipt、r9 CANDIDATE 一致。当前工具不具备主会话 Router 活动查询/切换接口，**未确认**。
- 已阅读范围：AGENTS.md；`docs/optimization/2026-10-09-desktop/00/02/04`、M0 模块文件、GATES.json；`M0/CONTEXT_M0.md`；r9 IMPLEMENTATION 全文；r9 CANDIDATE.json、`r9/results/install-and-host-r9.json`、`r9/results/offline-signing-r9.json`、`r9/results/ACCEPTANCE_MAPPING.md`、r9 全部 logs、`r9/probe-form-r9/bundle/main.splash`、`r9/probe/install_and_host_r9.py`；r7 Review；`runtime/native-build/OctoSense-Shell/crates/shell/src/lib.rs`（run_test_actions 4272-4400）；钉版 `r7/source-pin/octoscript-makepad/crates/octoscript-widgets/src/tap.rs:55-95`（on_click ScriptFnRef 分发）；rc.1 二进制 strings（test-action 集合）。
- 已运行范围（全部在 `review-r8/verify/` 隔离目录；sandbox profile 仅放行 review-r8 写 + r3/host 读、deny network-outbound；`MAKEPAD_HIDE_WINDOWS=1`；curl `/quit` 自控终止；每次测后 `pgrep -fl OctoSense.app` 无残留；未用 `--help`）：
  - `git rev-parse HEAD`、`git status --porcelain` 始末比对（一致）；复算 main.splash / manifest.json / 宿主两二进制 / r9 catalog `efe1bd4f…` / r9 probe_state.json SHA —— 与 r9 记录一致；
  - 从 r9 `local-mirror/artifacts/*.bundle`（已验签的 staged 产物）独立装出三个全新隔离 home（home-biz / home-probe / home-tap），catalog 拷至 `<apps>/catalog.json`（复核 r9 的「关键修正」：host `data_root` = `$OCTOSENSE_APP_DATA`，路径正确），bundle main.splash SHA 与工作树/r9 源逐字节一致；
  - **run biz1**（home-biz 全新）：`--test-action launch-hub:octosense-repair --test-action taps:318,529@8 --test-action capture:…`，16.6s 自控退出 → launched + card runner + `eval: 55781 bytes tick=true`；**tap 真实命中「＋新建报修草稿」**：`apps/octosense-repair/` 落 `actions.jsonl`（createDraft 回执，含幂等 key/fp）/ `events.jsonl` / `tasks.json`（DRAFT `1791609929728-1-u-reporter-1`）/ `state.json`（"草稿已创建"）；
  - **run biz2**（同 home 重启）：10.7s 退出 → 55781B eval；`tasks.json` SHA 跨重启字节一致（`4e26f973…` == `4e26f973…`）；capture 帧显示 DRAFT 任务「1791609929728-1-u-reporter-1 · DRAFT · 承接 未指派」——命名控件刷新 + 关开重读成立；
  - **run probe1/probe2**（home-probe 全新 → 重启）：5306B eval + launched + card runner；run1 自动 `fs.write` 落 `probe_state.json` 177B UTF-8 中文（SHA `086f7b59…`，审查方自己的 saved_at `1791609939.281985`）；run2 字节完全一致，capture 帧 status_lbl 显示「(eval 后立刻读到上次保存的内容：'用户报修：…')」；
  - **run probetap**（home-tap 全新，taps:218,404@8 命中「保存按钮」）：30.4s 退出 → `probe_state.json` saved_at 仍为 eval 时刻 `1791610051.596662` 未变 —— **按钮无任何效果**（见 D-R8-2）；
  - **run biz1440**（U11 抽查，`--size 1440x900`）：launched + 55781B eval + 渲染正常 + DRAFT 恢复；但 capture 帧仍为 2560×1260（与 1280×800 各 run 同尺寸，疑为屏幕/capture 上限），有效窗口尺寸证据弱，不据此改判 U11；
  - 复算 r9 三份 log 与 install-and-host-r9.json 内部一致性（发现 D-R8-1/D-R8-3 不符）；
  - rc.1 二进制 strings 复核 test-action 全集：`launch / capture / taps / page / shade / perf / ask-appcard / group / split / phone / island` 等，**无 scroll 注入**。
- 未运行范围及原因：逐字 IME 中文键入与真实滚动（osascript -1743，Automation/Accessibility 未授权；且 rc.1 test-action 无 scroll 注入）；真实模型调用（G0-E 按 Abram 裁决延期 M3）；可信双主体（G0-B 延期 M2）；grant 生命周期 / 配对码（T29/T32，候选维持 BLOCKED）；宿主 reminders 调度（G0-F，候选维持 BLOCKED）。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 候选定位与 B 包/工作树分离 | git HEAD/status + shasum 对照 r9 snapshot | 与 CANDIDATE 一致；不混包 | HEAD `8d73056…`、17 项逐行一致、main.splash `8aa1022c…`/manifest `e2025193…` 一致 | PASS | 本轮 git/shasum 输出 |
| 宿主二进制来源 | 复算 r3 留存官方 rc.1 两二进制 | 与 receipt 一致 | `3e127963…`/`a3e46a45…` 一致 | PASS | 本轮 shasum |
| 亲自启动目标宿主重跑最小探针（业务工作台） | 全新 home-biz + launch-hub + taps + capture + 重启重读 | launched + 55781B eval + tap 落盘 + 跨重启恢复 | **全部成立（审查方证据）**：createDraft 落盘四文件、tasks.json 跨重启字节一致、UI 恢复 DRAFT | PASS（审查方证据；候选方 tap 证据缺失，见 D-R8-1） | `review-r8/verify/results/host-r8v-biz-run{1,2}.json`、`logs/frame-r8v-biz-run2.png`、`verify/home-biz/.octosense/apps/octosense-repair/{actions.jsonl,events.jsonl,tasks.json,state.json}` |
| 亲自重跑探针表单 + 持久化 | 全新 home-probe run1→run2 | eval + 中文渲染 + fs.write + 跨重启字节一致 | **全部成立（审查方证据）**：5306B eval、probe_state.json 177B、SHA `086f7b59…` run1==run2、run2 帧显示重读成功 | PASS | `host-r8v-probe-run{1,2}.json`、`logs/frame-r8v-probe-run2.png` |
| 身份来源非 role/actor 下拉框 | 捕获帧 + launcher.log 主体注册行 | 不把演示身份下拉当身份证据 | 帧内「切换演示身份」五枚 Chip + 页首「演示身份 · 非登录认证」如实标注为脚本内演示选择；log 仅单 `Consent` 注册行（ai-host lib.rs:366）；G0-B 按 Abram 06:55 裁决记延期缺口（M2） | PASS（如实；延期缺口） | `logs/launcher-r8v-biz-run1.log`、`frame-r8v-biz-run2.png` |
| 模型调用对照固定官方契约 | launcher.log 模型行 + 零请求核对 | 如实，不按注释断言 | `llm: provider profile under <隔离home>`、`model: service registered (one-shot calls; granted apps only)`、全 log 零模型请求；G0-E 延期缺口（M3） | PASS（如实；延期缺口） | `logs/launcher-r8v-biz-run1.log` |
| install_staged 对照固定官方契约（D-R5-1 维持） | 抽查 r9 install JSON + 钉版源 + 复核离线签名记录 | 同 r7 闭合 | probe exit 0、官方布局 `.bundles/<id>/bundle`、manifest SHA `d758ed88…` 同 r8、may_run ok；r9 离线签名 sequence 2 verified、私钥三项已删（`r9/keys/` 实测为空） | PASS（维持闭合） | `r9/results/install-and-host-r9.json`、`offline-signing-r9.json`、`ls r9/keys/` |
| 准入权限机制正向/反向 | r7 已证未收录拒开；本轮复核 catalog 准入生效 | 一致 | 三个审查 home 均凭 sequence 2 catalog 准入成功；未收录拒开结论沿用 r7（本轮未重复反向用例） | PASS | r7 `verify/results/host-run-probeform.json` + 本轮三 home 启动成功 |
| 原子性/并发/权限/提醒边界 | 对照候选记录与实测 | 如实，不越级 | G0-C 并发/崩溃恢复零证据（候选如实）；原子 rename 仅 FS 原语级（如实）；G0-D 候选升为「PASS（部分）」有实测依据（probe fs 写读跨重启，审查方复现）；G0-F 维持 BLOCKED（reminders 仅 modules linked 一行） | PASS（如实） | 本轮 probe run1/run2；`logs/launcher-r8v-biz-run1.log` modules 行 |
| 数据边界 | sandbox profile + stat ~/.octosense + pgrep | 仅写 review-r8 | 6 次宿主运行全部写 review-r8/verify；`~/.octosense` mtime `Oct 9 22:58:31 2026` 未动；pgrep 每次无残留 | PASS | `verify/isolation.sb`；stat；各 run `pgrep_residue=""` |
| 业务文件零改动 | git status 始末比对 | 不增不减 | 同一 17 项（END_SNAPSHOT_MATCH） | PASS | 本轮 git 输出 |
| **D-R7-1 复核：业务工作台 rc.1 真实启动** | 审查方独立复跑（biz1/biz2） | r9 声称 PASS | 结论方向正确：启动/eval/tick/渲染/点击落盘/重启恢复全部真实成立。但 **r9 自己的 tap 落盘证据不存在**：r9 home 无 actions.jsonl/events.jsonl/tasks.json，state.json 为 83B 初始态（quit 8.5s 与 tap@8s 赛跑）；报告/CANDIDATE/MAPPING 的「tap 落盘 createDraft」声称无候选方证据支撑 | **部分成立（能力由审查方证实；候选证据缺失 → D-R8-1）** | 见缺陷节 |
| **D-R7-2 复核：根因归因反转** | 对照 r9 报告 §1.3 与 CANDIDATE | 删除「binary bug/需重链」 | 已删除，保留两条正确事实（app[:count] 误切 + 正确入口），与 r7 Review 一致 | PASS（RESOLVED） | r9 报告 §1.3；CANDIDATE `host_entry_used` |
| **D-R7-3 复核：硬验收 3 最小原生表单** | 审查方 probe run1/run2 + probetap 失败注入 + 源码核对 | 表单中文 + 滚动后控件可操作 | eval/中文/落盘/重读成立；但**探针三个按钮全部无 `on_click`，`run_command` 无调用方（死代码），tap 命中保存按钮后 saved_at 未变**；「滚动后控件可操作 PASS（hit-area 静态证据）」为越级判定；尾部按钮在 1280×800 帧中完全不可见（ScrollYView 仅「行 0」露出）且 rc.1 无 scroll 注入 | **FAIL（D-R8-2）** | 见缺陷节 |
| D-R7-4 复核：交接材料同步 | 对照三处文字 | 无残留「binary bug」 | 「binary bug/需重链」已清除；但同步引入了新失真（tap 落盘声称、blake3/capture_bytes 陈旧值），见 D-R8-1/D-R8-3 | 部分（D-R8-3） | 见缺陷节 |
| D-R6-3 复核：mtime 订正 | `stat -f %Sm ~/.octosense` | 22:58:31 | `Oct 9 22:58:31 2026` | PASS（RESOLVED 维持） | 本轮 stat |

## 缺陷

### D-R8-1（P1，必需修复·r9 声称的业务 tap 落盘证据在候选 artifacts 中不存在）

- 文件/行：
  - 声称点：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r9.md` §1.1 表 row (4)「tap + 落盘：apps/octosense-repair/{actions.jsonl,events.jsonl,tasks.json,state.json}」、§4 D-R6-1 行「tap 318,529@8 落盘 actions/events/tasks/state」、§6 测试表「启动 rc.1 宿主（业务工作台）」行；
  - `runtime/optimization/2026-10-09/M0/r9/results/ACCEPTANCE_MAPPING.md:16`（T28 行「tap 触发 actions.jsonl createDraft」）、`:41`（D-R6-1 行同）；
  - `runtime/optimization/2026-10-09/M0/r9/CANDIDATE.json` `r7_review_resolutions.D-R7-1`（"tap 318,529@8 fires actions.jsonl createDr…"）。
- 触发步骤：`find r9/home -name actions.jsonl -o -name events.jsonl -o -name tasks.json` → 零命中；`cat r9/home/.octosense/apps/octosense-repair/state.json` → `{"actor":"u-reporter-1",…,"selectedIdx":-1,"status":"准备就绪"}`（83 B 初始态）。
- 预期：按 r7 Review D-R7-1 修复计划第 4 条，r9 应交付「tap 触发的 actions/events/tasks/state 落盘 + 关开重读」候选方证据。
- 实际：r9 唯一记录的 biz run（`install-and-host-r9.json` wall 8.5s）在 tap@8s 触发后 ~0.5s 即 curl /quit，与 tap 赛跑；`frame-r9-biz.png` 显示「无可见任务 / 共 0 条可见」，r9 home 无任何落盘文件。「tap 落盘」实为把 review-r7 审查方证据路径当作 r9 自己的证据引用。
- 影响：候选、宿主与证据不一致——「确认候选、宿主与证据一致」这条 Review 必需检查对 tap 落盘子项不成立；T28「PASS」行的关键依据之一是虚构的候选方证据。能力本身真实（本审查 biz1 run 复现 createDraft 落盘四文件、biz2 跨重启恢复），故不定性为能力缺失，但候选方必须交付自己的证据或如实改引审查方证据。
- 根因：`install_and_host_r9.py` 退出判据 `t >= 8s` 与 `taps:…@8` 同刻，quit 先于/紧贴 tap 生效；写报告时把 r7 Review 的证据描述直接继承为 r9 结果。
- 具体修改方案（r10）：
  1. 重跑 biz host run：`taps:318,529@8` 保留，退出判据改为「tap 后 ≥5s」（如 min_wall ≥ 15s），使 tap 完整生效；
  2. 交付 r10 自己的证据：`r10/home…/apps/octosense-repair/{actions.jsonl,events.jsonl,tasks.json,state.json}` 四文件内容摘录（含 createDraft 回执）+ tap 后 capture 帧（任务列表出现 DRAFT）+ 重启 run2 的 tasks.json SHA 一致记录（可参照本审查 `review-r8/verify/results/host-r8v-biz-run{1,2}.json` 的字段）；
  3. 若不重跑，则把三处声称改为「审查方证据（review-r7/review-r8），候选方未自证 tap 落盘」——但这会留候选证据空洞，优先选 1+2；
  4. 同步订正 ACCEPTANCE_MAPPING T28/D-R6-1 行与 CANDIDATE `r7_review_resolutions.D-R7-1`。
- 改后验证：Review 对 r10 home 跑 `find` + `cat actions.jsonl`，并对 capture 帧确认 DRAFT 可见。
- 证据：`r9/home/.octosense/apps/octosense-repair/state.json`（83B 初始态）；`r9/logs/frame-r9-biz.png`（0 条可见）；对照 `review-r8/verify/home-biz/.octosense/apps/octosense-repair/actions.jsonl`（createDraft，`"status":"DRAFT"`）与 `frame-r8v-biz-run2.png`（DRAFT 任务行）。

### D-R8-2（P1，必需修复·硬验收 3「滚动后控件可操作」越级判 PASS：探针按钮无 on_click 全部失效，run_command 为死代码）

- 文件/行：
  - `runtime/optimization/2026-10-09/M0/r9/probe-form-r9/bundle/main.splash:91`（尾部 `ButtonFlat` 无 `on_click`）、`:94-95`（保存/重读按钮无 `on_click`）、`:116-129`（`fn run_command(cmd)` 定义但全工程无调用方）；
  - 机制证据：钉版 `r7/source-pin/octoscript-makepad/crates/octoscript-widgets/src/tap.rs:64,83` —— `on_click: ScriptFnRef` 是唯一 tap 分发通道，未绑定时 `widget_to_script_call(NIL)` 为空操作；`grep -rn "run_command" r7/source-pin`（Rust 源）零命中，宿主/卡片运行时不存在对 splash `run_command` 的隐式调用；
  - 越级判定：`M0_IMPLEMENTATION_r9.md` §2.5 表「滚动后控件可操作 PASS（hit-area 静态证据）」、§5 硬验收 3「PASS（hit-area + 持久化）」；`r9/results/ACCEPTANCE_MAPPING.md:51` 同。
- 触发步骤（本审查失败注入，隔离 home-tap）：`launch-hub:r9-probe-form` + `taps:218,404@8`（坐标按 frame-r9-probeform-run1.png 实测命中「保存按钮：触发 run_command('save')」按钮中心）→ 14s 后退出。
- 预期：若按钮有效，`run_command("save")` 应以 tap 时刻（≈启动+8s）重写 `probe_state.json` 的 `saved_at`。
- 实际：`home-tap/.../probe_state.json` 的 `saved_at` 保持 eval 时刻 `1791610051.596662` 不变，SHA 不变 —— tap 无任何效果。三个按钮全部失效。此外尾部按钮在 1280×800 下根本不可见：capture 帧中 ScrollYView 仅露出「行 0 (静态)」，行 1-7 与尾部按钮被窗口下缘裁掉；rc.1 二进制 test-action 全集（strings 实测：`launch/capture/taps/page/shade/perf/ask-appcard/group/split/phone/island`）**无 scroll 注入**，taps 只能命中可视坐标。
- 影响：硬验收 3 的「滚动后的控件可操作」在目标宿主上仍为零有效证据，候选却以「hit-area 静态证据」判 PASS——正是 Review 指令禁止的「按注释/静态迹象认定已支持」。必需检查未通过。
- 根因：探针 splash 把 r7 Review 方案中的 `run_command("save")` 当作宿主会自动调用的入口（实际不存在该机制），按钮未绑 `on_click`；同时把「widget tree 里存在 hit-area」误等同「控件可操作」。
- 具体修改方案（r10，全部本机可完成，无需新授权）：
  1. 给三个按钮绑定 `on_click:` 闭包：保存 → 调写盘函数（把 `run_command` 的 save/load 分支重构为普通函数供 `on_click` 调用，或直接在闭包内写盘），删除或实装 `run_command`；尾部按钮同样绑定（如写盘并更新 status_lbl）；
  2. 让可点击证据可达：二选一——
     a. 若 octoscript-makepad 的 ScrollYView 暴露脚本可设置的滚动偏移（查 `r7/source-pin/octoscript-makepad/crates/octoscript-widgets/src/` 的 scroll 组件 API），eval 时把滚动偏移设为非零，再用 `taps:` 命中偏移后可视的尾部按钮 → 这是真正的「滚动后控件可操作」证据；
     b. 若无脚本滚动 API：缩小 ScrollYView 行数/行高使尾部按钮在 1280×800 窗口内**不滚动即可视**，`taps:` 命中并产生状态变化（`probe_state.json` saved_at 更新或新落盘字节）→ 证明「滚动容器内控件可操作」；真·post-scroll click 改记 NOT_RUN，原因写实测事实：「rc.1 test-action 无 scroll 注入（strings 证据）+ UI Automation -1743 未授权」，不得再写「PASS（hit-area）」；
  3. 保留现有 run1 自动写盘 + run2 重读字节一致链路（该证据有效，不要破坏）；
  4. 探针 bundle 变更后 blake3 改变，需按 Abram 授权 A 在 r10 sandbox 内重新 keygen/certify/sign-manifest/publish（sequence 3），测完删除私钥并记录删除证据——与 r9 同类操作，授权 A 范围内；
  5. 报告与 ACCEPTANCE_MAPPING 的硬验收 3 行按实际证据重写：中文渲染 PASS、落盘跨重启 PASS、按钮可操作（按 2a/2b 结果）、真·post-scroll 与逐字 IME 视情况 NOT_RUN。
- 改后验证：Review 复跑 tap 注入，检查 `probe_state.json` saved_at 随 tap 更新（或 2b 的等价状态变化），并核对 ACCEPTANCE_MAPPING 无「hit-area PASS」残留。
- 证据：`review-r8/verify/results/host-r8v-probe-tap.json`、`review-r8/verify/home-tap/.octosense/apps/r9-probe-form/probe_state.json`（saved_at 未变）、`review-r8/verify/logs/frame-r8v-probe-tap.png`（按钮位置）、`r9/logs/frame-r9-probeform-run1.png`（ScrollYView 仅行 0 可见）、tap.rs:64/83、rc.1 strings 输出。

### D-R8-3（P3，建议·报告/CANDIDATE 数值与自家 JSON 证据不一致）

- 文件/行：
  - r9-probe-form blake3：`M0_IMPLEMENTATION_r9.md:122` 与 `:140` 写 `7940c7eb…`、`r9/CANDIDATE.json` `install_staged_r9_probe_form_blake3` 同；但 `r9/results/offline-signing-r9.json:35`、`install-and-host-r9.json:30` 及实测 `r9/local-mirror/artifacts/r9-probe-form-0.1.0-r9probe.bundle/manifest.json` 均为 `84be777702522afe…`（`offline-signing-r9.json` pipeline 名自证为 rev2，报告引用的是 rev1 旧值）；
  - biz capture 大小：报告 §1.2 引用 `capture_bytes: 3697511`、CANDIDATE `host_runs.octosense-repair` 写 3697511、§8 与 MAPPING 写「3.7 MB」；实际 `install-and-host-r9.json:96` 与 `ls` 均为 1754961 B（1.7 MB）；
  - `offline-signing-r9.json:64` `home_catalog.path` 仍记 `r9/home/.octosense/catalog.json`（r9 自己已订正的错误路径；实际写入并生效的是 `apps/catalog.json`，本审查复核 SHA `efe1bd4f…` 一致）。
- 影响：交接材料内部自相矛盾，后续模块引用会拿到错误 digest/路径。
- 具体修改方案（r10）：三处数值以 `install-and-host-r9.json` / `offline-signing-r9.json`（rev2）/ manifest.json 实测为准统一订正；`offline-signing-r9.json` 的 `home_catalog.path` 字段若重跑签名则修正，否则在报告注明该字段为 rev1 残留。
- 改后验证：grep 7940c7eb / 3697511 在 r10 交接材料中零残留（除历史引用说明）。
- 证据：本轮 shasum/cat 输出；上述 JSON 行。

### D-R8-4（P3，建议·探针 splash  cosmetic 缺陷与规格偏差未声明）

- 文件/行：`r9/probe-form-r9/bundle/main.splash:120,140` —— `PRESET_ZH.length` 对字符串不支持（rc.1 strings 实测 `len called on non-string value`），status_lbl 实际渲染「bytes=[Error:NotFound]」（frame-r9-probeform-run1.png 可见）；探针 ScrollYView 为 8 行，与 r6 Review 钉版的「30 行」规格不符且报告未声明偏差。
- 影响：低；但状态行显示 Error 会污染「表单正常」的观感证据。
- 具体修改方案（r10）：改用宿主支持的取长度方式或直接去掉 bytes= 拼接；行数偏差在报告 §2.1 声明（或补足行数，配合 D-R8-2 的 2a/2b 布局一并处理）。
- 证据：`frame-r9-probeform-run1.png` status 行；`review-r8/verify/logs/frame-r8v-probe-tap.png` 同。

## 判定

- 最终结论：**FAIL**
- 本次结论的精确范围：M0 r9 候选（`M0-r9-worktree`，HEAD `8d73056…`）。硬验收 1（候选可定位、宿主真实启动、来源明确）PASS；硬验收 2 PASS（各能力如实记录，G0-B/G0-E 按 Abram 2026-10-10 06:55 裁决维持延期缺口）；硬验收 4 PASS（隔离边界与现场完整，审查方 6 次宿主运行亦全程在 review-r8 内）；D-R7-2 根因反转 RESOLVED；D-R5-1/2/3/4/5 与 D-R6-3 维持闭合。**审查方独立复现了 r9 的核心能力声称**（业务工作台 55781B eval + tap createDraft 落盘 + 跨重启恢复；探针表单 5306B eval + 中文渲染 + fs 落盘跨重启字节一致），能力本身成立。但硬验收 3 的「滚动后控件可操作」被候选以「hit-area 静态证据」越级判 PASS（实测按钮无 on_click 全部失效，D-R8-2），且候选声称的 tap 落盘证据在其 artifacts 中不存在（D-R8-1）——必需检查未通过，不得放行。
- 审查方新确立的事实（供 r10 直接引用，证据在 `review-r8/verify/`）：**(1) 候选方 biz run 的 quit 判据与 tap@8s 赛跑，r9 artifacts 中无 tap 落盘证据；能力由审查方 biz1/biz2 复现（四文件落盘 + tasks.json SHA `4e26f973…` 跨重启一致 + UI 恢复 DRAFT）；(2) 探针持久化链路真实有效（审查方 run1/run2 SHA `086f7b59…` 字节一致）；(3) 探针三个按钮无 on_click、run_command 无调用方，tap 命中无效果；(4) rc.1 二进制 test-action 全集无 scroll 注入（strings 实测），post-scroll 脚本化点击需探针内脚本滚动或授权 UI Automation；(5) r9 报告 blake3/capture_bytes/catalog 路径三处数值为 rev1 残留。**
- 必修项：D-R8-1、D-R8-2（D-R8-3/D-R8-4 随修）。
- 延期缺口（Abram 已裁决，不判 BLOCKED/FAIL）：G0-B（M2 到期）、G0-E（M3 到期）。
- 其余阻塞与未测项（维持如实记录）：G0-C 并发/崩溃恢复零证据；G0-F 提醒调度/due_at/跨重启恢复未实测（reminders 仅 modules linked）；T29/T32 BLOCKED；U09 1280×800 有候选+审查双方证据，其它子项 NOT_RUN；U11 审查方抽查 1440×900 可启动可渲染但 capture 分辨率未随 --size 变化，证据弱，维持候选 BLOCKED 判定；逐字 IME 键入 NOT_RUN（-1743）；真·post-scroll click 按 D-R8-2 方案 2a/2b 定性。
- 受影响先前模块是否已复验：M0 无前置模块；`docs/build-loop/ACCEPTANCE.json` 未触动；P06/P07/P08 UNASSESSED 未改写；历史后端 PASS 未被冒充为原生 PASS。
- 门禁与原台账更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=FAIL，review_report 指向本文件，blockers 按 D-R8 系列重写，previous_review 追加 r7→r8 链）。
- 是否允许下一模块：**否**。
- 若 FAIL/BLOCKED，留在本模块的修复/解阻指令：
  1. r10 按 D-R8-1：biz host run 退出判据改为 tap 后 ≥5s，交付候选方自己的 actions/events/tasks/state 落盘 + tap 后 DRAFT 帧 + 重启 SHA 一致证据，同步订正报告/MAPPING/CANDIDATE 三处；
  2. r10 按 D-R8-2：探针按钮绑 on_click（删除或实装 run_command），按 2a（脚本滚动偏移）或 2b（可视布局 + taps 状态变化证据）交付「滚动容器内控件可操作」真实证据，真·post-scroll 不可为则按实测原因记 NOT_RUN；探针重签走授权 A sandbox 流程并删除私钥；
  3. r10 按 D-R8-3/D-R8-4：订正 blake3 `84be7777…`、capture 1754961 B、catalog 路径字段、status 行 [Error:NotFound]；
  4. 全部为本机可完成工作（离线签名已授权、taps/capture 不依赖 -1743），**无需 Abram 新授权**；宿主启动继续遵守后台 + HIDE_WINDOWS + 自控 /quit + pgrep 无残留规矩。
