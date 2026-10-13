# M0 独立 Review r7 — r8 候选复核：D-R6-1「rc.1 二进制 bug」结论被证伪，业务工作台可在 rc.1 真实运行

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-10 12:36 CST（Asia/Shanghai）
- candidate_id：`M0-r8-worktree`；base：`M0-r7-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`（本轮复算，与 r8 CANDIDATE.json 一致）
- 审查开始/结束时快照是否一致：开始与结束 `git status --porcelain` 均为同一 17 项，与 `r8/snapshot/snapshot-status-r8-before.txt` 逐行一致（diff 为空）；`app/bundle/main.splash` `8aa1022c…`（55781 B）/ `manifest.json` `e2025193…` 与 r8 `bundle-sha.txt` 一致；业务文件零改动。审查写操作全部在 `runtime/optimization/2026-10-09/M0/review-r7/` 内，未触碰 r8 候选任何文件。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r8.md`
- 已核对前置模块 PASS 与受影响回归：M0 无前置模块；r6 Review（Kimi，FAIL）三条缺陷 D-R6-1/D-R6-2/D-R6-3 本轮逐条独立复核；r5 五条必修（D-R5-1/2/3/4/5）沿用 r6 闭合结论并抽查 r8 证据一致。
- 实际环境 / 模型路由 / 宿主：darwin；宿主 = `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`（官方 `desktop-v0.1.0-rc.1` macOS aarch64），本轮复算 octosense `3e127963…` / octos-kernel `a3e46a45…`，与 r3 receipt 及 CANDIDATE 一致。当前工具不具备主会话 Router 活动查询/切换接口，**未确认**。
- 已阅读范围：AGENTS.md；`docs/optimization/2026-10-09-desktop/00/01/02/04`、M0 模块文件、GATES.json；r6 REVIEW 与 r8 IMPLEMENTATION 全文；r8 CANDIDATE.json、`r8/probe/install_and_launch_r8.py`、r8 全部 logs/results、r8 ACCEPTANCE_MAPPING.md；钉版 App-Hub（r7/source-pin，ba36df05）`appstore/src/lib.rs:83-95`、`app-hub/src/client.rs:37-87`、`app-hub-app/src/catalog.rs:98-130`；`runtime/native-build/OctoSense-Shell/crates/shell/src/lib.rs`（MAKEPAD_WM_TEST_APP 解析 4901-4908、run_test_actions 4272-4340、launch_app/find_app 643-666）；`runtime/native-build/OctoSense-App-Hub/crates/appstore/src/lib.rs:76-88`；本审查会话既有 review-r7 证据（11:55–12:14 生）。
- 已运行范围（全部在 `review-r7/verify/` 隔离目录；sandbox profile 仅放行 review-r7 写、deny network-outbound；`MAKEPAD_HIDE_WINDOWS=1`；`/quit` 自控终止；测后 `pgrep -fl OctoSense.app` 无残留）：
  - `git rev-parse HEAD`、`git status --porcelain` 始末比对（一致）；复算 main.splash / manifest.json / 宿主两二进制 / catalog `b4493bb1…` SHA —— 全部与 CANDIDATE 一致；
  - **独立复跑宿主（全新 verify home + 拷贝已接受 catalog）**：`octosense --size 1280x800 --test-action launch-hub:octosense-repair --test-action taps:318,529@8 --test-action capture:…/frame-biz.png` → `wm: launched hub:octosense-repair as client 1 (in-process, card)`（rc.1 二进制日志 `crates/shell/src/lib.rs:2637:9`）、card runner 行来自 `/cargo/git/checkouts/octosense-app-hub-3222614192ecfbf8/ba36df0/crates/appstore/src/cardapp.rs:134`、`[SPLASH] eval: 55781 bytes tick=true`（= 工作树 main.splash 字节数 55781）、捕获帧 2560×1264 PNG 显示「知了·维修协作」工作台、tap 命中「新建报修草稿」→ 隔离 home 落 `actions.jsonl`（createDraft）/ `events.jsonl` / `tasks.json`（DRAFT）/ `state.json`；13.2s 自控 /quit，exit 0，pgrep 无残留（`verify/results/host-run-biz.json`）；
  - **独立复跑探针表单**：`--test-action launch-hub:r8-probe-form`（bundle 已放入 `.bundles/r8-probe-form/bundle`）→ 60s 内仅默认 Splash `eval: 809 bytes`，无 launched 行，被静默拒开（`verify/results/host-run-probeform.json`）；
  - 复算并核对 r8 四次 host run log（均 `no app 'hub' in the registry` + 809B，与 r8 报告事实部分一致）；
  - 验证 `~/.octosense` mtime 仍 `Oct 9 22:58:31 2026`（本轮两次宿主运行均未触动）；
  - 终止一个并发残留宿主进程（见「并发活动记录」）。
- 未运行范围及原因：真实 UI 自动化（osascript -1743，Automation/Accessibility 未授权）——但注意 Shell 自带 `--test-action taps:` 注入，本轮已用其实现真实点击，-1743 不再是点击取证的阻断；真实模型调用（无授权 provider，G0-E 按 Abram 裁决延期 M3）；可信双主体（G0-B 延期 M2）；为探针表单重签含其条目的离线 catalog（属修复方 r9 工作，Review 不代做）。

## 并发活动记录（过程事实，非候选缺陷）

审查期间 12:29 检测到另一会话在 `review-r7/` 内启动宿主（pid 88992，tag `verifyA-reload`），已按用户规矩立即终止并确认 pgrep 无残留、桌面无残留窗口。本结论仅依据本审查会话自产或复算的证据（`review-r7/verify/`），并发会话写入的文件不作为依据。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 候选定位与 B 包/工作树分离 | git HEAD/status + shasum 对照 r8 snapshot | 与 CANDIDATE 一致；不混包 | HEAD `8d73056…`、17 项 status 逐行一致、main.splash `8aa1022c…`/manifest `e2025193…` 一致 | PASS | 本轮 git/shasum 输出 |
| 宿主二进制来源 | 复算 r3 留存官方 rc.1 两二进制 | 与 receipt 一致 | `3e127963…`/`a3e46a45…` 一致 | PASS | 本轮 shasum |
| 亲自启动目标宿主并重跑最小探针 | verify home + `--test-action launch-hub:octosense-repair` + taps + capture | 业务工作台在 rc.1 真实运行 | **成功**：launched as client 1、`eval: 55781 bytes tick=true`、工作台渲染 PNG、tap 触发 createDraft 落盘 | **PASS（审查方证据；候选未交付，见 D-R7-1）** | `verify/results/host-run-biz.json`、`verify/logs/launcher-biz.log`、`verify/logs/frame-biz.png`、`verify/home/.octosense/apps/octosense-repair/{actions.jsonl,events.jsonl,tasks.json,state.json}` |
| 身份来源非 role/actor 下拉框 | 捕获帧 + launcher.log 主体注册行 | 不把演示身份下拉当身份证据 | 帧内「切换演示身份：报修人一/二、技工甲/乙、经理丙」为脚本内演示选择；log 仅单 `Consent` 注册行（ai-host lib.rs:366）；G0-B 按 Abram 06:55 裁决记延期缺口（M2） | PASS（候选如实；延期缺口） | `verify/logs/launcher-biz.log:10`、frame-biz.png |
| 模型调用对照官方契约 | launcher.log 模型行 | 如实 | `model: service registered (one-shot calls; granted apps only)`、无 provider、零请求；G0-E 延期缺口（M3） | PASS（如实；延期缺口） | `verify/logs/launcher-biz.log:8-9` |
| install_staged 对照固定官方契约（D-R5-1 维持） | 抽查 r8 install-run-r8.json + 钉版源 | 同 r6 闭合 | probe exit 0、官方布局落盘、manifest SHA `d758ed88…`、may_run 字节重验；catalog `b4493bb1…` 一致 | PASS（维持闭合） | r8/results/install-run-r8.json |
| 准入权限机制正向证据 | 探针表单不在 catalog → 启动 | 拒开 | `launch-hub:r8-probe-form` 被静默拒开（may_open 不过），与钉版 `catalog.rs:108-120` + shell 拒开路径一致 | PASS（机制有效；同时是 D-R7-3 的触发） | `verify/results/host-run-probeform.json` |
| 原子性/并发/提醒边界 | 对照候选记录与 log | 如实 | G0-C 并发零证据、G0-D 宿主 app_storage 未测、G0-F 仅 modules linked 一行 —— 候选维持 BLOCKED 如实 | PASS（如实） | r8 ACCEPTANCE_MAPPING.md；launcher-biz.log:11 |
| 数据边界 | sandbox profile + stat ~/.octosense | 仅写 review-r7 | 两次宿主运行全部写 review-r7/verify；`~/.octosense` mtime 22:58:31 未动；news 7 源全失败佐证断网 | PASS | isolation.sb；stat；launcher-biz.log:35 |
| 业务文件零改动 | git status 始末比对 | 不增不减 | 同一 17 项 | PASS | 本轮 git 输出 |
| **D-R6-1 复核：rc.1 上真实启动业务工作台** | 审查方独立复跑 + 源码核对 | r8 声称 BLOCKED（binary bug 需重链） | **r8 结论被证伪**：正确入口 `--test-action launch-hub:<id>` 在 rc.1 上直接成功，55781B eval、tick、真实点击落盘全部成立 | **FAIL（D-R7-1/D-R7-2）** | 见缺陷节 |
| **D-R6-2 复核：硬验收 3 最小原生表单** | 审查方独立尝试探针表单 | rc.1 上表单证据 | 探针表单因未入 catalog 被准入层拒开；rc.1 上仍零表单证据（候选与审查方均未取得） | **FAIL（D-R7-3）** | `verify/results/host-run-probeform.json` |
| D-R6-3 复核：mtime 订正 | `stat -f %Sm ~/.octosense` | 22:58:31 | `Oct 9 22:58:31 2026`，r8 订正准确 | PASS（RESOLVED 维持） | 本轮 stat |

## 缺陷

### D-R7-1（P1，必需修复·D-R6-1 的「rc.1 BLOCKED / 需重链 binary」结论错误：启动入口用错，非宿主缺陷）

- 文件/行：
  - 误用点：`runtime/optimization/2026-10-09/M0/r8/probe/install_and_launch_r8.py:19` 及 `:187`（设 `MAKEPAD_WM_TEST_APP=hub:octosense-repair`）；
  - 误用机制：`runtime/native-build/OctoSense-Shell/crates/shell/src/lib.rs:4901-4908` —— `MAKEPAD_WM_TEST_APP` 语义是 `app[:count]`，`spec.split_once(':')` 把 `hub:octosense-repair` 切成 app=`"hub"`、count=`"octosense-repair".parse().unwrap_or(1)`，于是 `launch_app("hub")` → `no app 'hub' in the registry`（rc.1 日志自证 `crates/shell/src/lib.rs:766:13`）；
  - 正确入口：`--test-action launch-<app id>`（`launch-` 前缀后取完整 id，不做 `:` 切分）——native-build `lib.rs:4290-4295`（`name.strip_prefix("launch-")` → `self.launch_app(cx, &app)`）；rc.1 二进制内该路径日志位于 `crates/shell/src/lib.rs:5390:25`（`wm: --test-action launch hub:octosense-repair`）。
- 触发步骤：r8 四次 host run 均用 `MAKEPAD_WM_TEST_APP=hub:octosense-repair`；本审查用 `--test-action launch-hub:octosense-repair` 复跑同一二进制、同一 bundle（SHA `8aa1022c…`）。
- 预期：按 r6 Review D-R6-1 修复计划第 2 条「从钉版 Shell 源码查明已安装 card 应用的启动入口」应找到可用入口；r8 报告 §1.5 声称已排除全部非交互入口。
- 实际：`--test-action launch-` 入口一直存在且可用。本审查独立复跑：`wm: launched hub:octosense-repair as client 1 (in-process, card)`、`[SPLASH] eval: 55781 bytes tick=true`、捕获帧为真实业务工作台、`taps:318,529@8` 命中「新建报修草稿」并落盘 `actions.jsonl`（createDraft）/ `events.jsonl` / `tasks.json`（DRAFT）/ `state.json`。既有 review-r7 证据（11:57–12:14，both2/legacyonly/newonly/taps 四次 run）同样全部成功。
- 影响：r8 把「入口参数用错」误判为「rc.1 二进制 bug、需官方重链、外部依赖、本轮不可解」，导致 D-R6-1/D-R6-2/T28/U09 等全部阻塞结论失真，GATES.json blockers 与 NEEDS_ABRAM 推论随之失真；r2 改名后版本「从未在目标宿主 eval」的风险实际已被运行定性（本审查 run 即 55781B 当前版本的首次 rc.1 eval + 点击落盘，tick=true 正常）。
- 根因：r8 查到 `MAKEPAD_WM_TEST_APP` 的注释（`app[:count]`）却未意识到 `hub:<id>` 内含冒号会被误切；未继续检查 `run_test_actions`（`--test-action launch-`/`taps:`/`capture:`，lib.rs:4272-4340）这一组专为脚本化测试设计的入口。
- 具体修改方案（r9，全部本机可完成，无需新授权）：
  1. 启动器改用 `--test-action launch-hub:octosense-repair`（或 `MAKEPAD_APP_CONFIG.test_actions` 数组，lib.rs:4275-4282），删除 `MAKEPAD_WM_TEST_APP=hub:<id>` 用法；
  2. 全新隔离 home 需先让 catalog 被接受：首跑由 Hub worker 从 `OCTOSENSE_HUB` 本地镜像拉取并缓存到 `<apps>/catalog.json`（`catalog.rs:228-240`），或直接拷贝已验证的 catalog 缓存（SHA `b4493bb1…`）——否则 `may_open` 报 `no catalog has been accepted`（client.rs:292）静默拒开；
  3. 后台启动 + `MAKEPAD_HIDE_WINDOWS=1` + `--test-action capture:<png>` + 自控 `/quit` + pgrep 无残留（沿用本审查 `review-r7/verify/run_verify.py` 的手法即可）；
  4. 取证清单：launcher.log 的 launched 行 + `eval: 55781 bytes tick=true`、capture 帧、tap 触发的 actions/events/tasks/state 落盘、关开重读（重启后 `state.json`/`tasks.json` 仍在且 UI 恢复——对应修改指令 item 3 的「命名控件刷新」）。
- 改后验证：r9 报告附上述全部证据路径；Review 复跑同一脚本可重现。
- 证据：`review-r7/verify/results/host-run-biz.json`、`review-r7/verify/logs/launcher-biz.log`、`review-r7/verify/logs/frame-biz.png`、`review-r7/verify/home/.octosense/apps/octosense-repair/*`；对照 r8 `logs/launcher-r8.log` 等四份 809B log。

### D-R7-2（P1，必需修复·根因归因错误：rc.1 链接的是 ba36df0 新版 appstore，不是 legacy 读法）

- 文件/行：r8 报告 §1.4/§1.6 及 `r8/results/ACCEPTANCE_MAPPING.md` T28 行，引用 `runtime/native-build/OctoSense-App-Hub/crates/appstore/src/lib.rs:76-88`（legacy 读法）作为「rc.1 binary 实际链接」。
- 触发：核对 rc.1 二进制自身日志与三布局实验。
- 预期/实际：r8 称「rc.1 binary 链接 legacy `installed_apps`，不知道 `.bundles/`」。实际反证三条：
  1. rc.1 二进制 card runner 日志行自带构建路径 `/cargo/git/checkouts/octosense-app-hub-3222614192ecfbf8/ba36df0/crates/appstore/src/cardapp.rs:134` —— rc.1 链接的 app-hub 是 **ba36df0**（即 r7 钉版同系），其 `installed_apps` 是新版读法（r7/source-pin `appstore/src/lib.rs:83-95`：先 `adopt_legacy_installs` 再读 `INSTALLS_DIR=.bundles`）；
  2. 既有 review-r7 三次布局实验（both2 / legacyonly / newonly）用正确入口**全部启动成功**——与「新版 reader + adopt」行为完全一致；若真是 legacy 读法，newonly 布局不可能成功；
  3. `runtime/native-build/OctoSense-App-Hub/crates/` 全文 grep 无 `adopt_legacy_installs` —— r8 既称 binary 跑 adopt（此点对：post-host legacy 目录变空由 ba36df0 的 adopt 解释），又称 binary 链接 native-build 的 legacy reader，两者引用的源树自相矛盾；native-build 目录并非 rc.1 的构建源。
- 影响：「需 rc.1 binary 重链 = 外部依赖 = NEEDS_ABRAM」的推论不成立；真实结论是「入口用错」，本机即可解。
- 具体修改方案（r9）：重写报告根因段落——删除「rc.1 binary bug / 需重链」表述；保留的正确事实仅两条：(a) `MAKEPAD_WM_TEST_APP=hub:<id>` 因 `app[:count]` 语义误切（native-build lib.rs:4901-4908 + rc.1 log lib.rs:766）；(b) 正确入口为 `--test-action launch-hub:<id>`（rc.1 log lib.rs:5390 + native-build lib.rs:4290）。同步订正 ACCEPTANCE_MAPPING.md T28 行与 GATES.json blockers 文字。
- 改后验证：Review 对照本条三条反证逐条核对 r9 文本。
- 证据：`review-r7/verify/logs/launcher-biz.log`（card runner 行）、`review-r7/results/host-run-{both2,legacyonly,newonly}.json`、本轮 grep 输出。

### D-R7-3（P1，必需修复·硬验收 3 仍无目标宿主证据；探针表单被 catalog 准入层静默拒开）

- 文件/行：本审查 `launch-hub:r8-probe-form` 复跑 → 60s 仅 `eval: 809 bytes`、无 launched 行（`review-r7/verify/results/host-run-probeform.json`）；准入逻辑 `r7/source-pin/OctoSense-App-Hub/crates/app-hub-app/src/catalog.rs:108-120`（`try_may_open_from_environment` → `may_open`）；shell 拒开路径 `runtime/native-build/OctoSense-Shell/crates/shell/src/lib.rs:660-666`（catalog 不准入 → `notify("Could not open app", …)`，**仅 UI 通知、无 stdout 日志**，这是静默的原因）；已接受 catalog（sequence 1，SHA `b4493bb1…`）只含 `octosense-repair` 一个条目。
- 触发：把 `r8/probe-form/bundle` 放入隔离 home `.bundles/r8-probe-form/bundle` 后 `launch-hub:r8-probe-form`。
- 预期：r6 Review D-R6-2 修复计划要求探针表单在 rc.1 内完成渲染/落盘/重读取证。
- 实际：r8 未在 rc.1 尝试探针表单（仅在旧 card-host 佐证）；本审查尝试证明：准入机制有效拦截未收录应用，探针表单要跑必须先入离线 catalog。
- 影响：硬验收 3（最小原生表单中文输入 + 滚动后控件可操作）在目标宿主上仍零证据，必需检查未通过。
- 具体修改方案（r9，全部在本机 + Abram 已授权的隔离离线签名范围内）：
  1. 按授权 A 在 r9 sandbox 内重新 `hub keygen / certify / sign-manifest`，生成**含探针表单条目**（新 id 或沿用 `r8-probe-form`）的离线签名 catalog（sequence 递增；仅 sandbox 有效、不联网、不上传；测完删除私钥并在报告记录删除证据）；
  2. 用钉版源 probe 把探针表单 `install_staged` 进全新隔离 home（`.bundles/<id>/bundle`），catalog 缓存同 D-R7-1 第 2 条；
  3. `--test-action launch-hub:<probe-id>` + `capture:` + `taps:`：取证 6361B eval、表单渲染帧（预设中文 `用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。` 可见）、tap 尾部按钮触发 `run_command("save")` → `probe_state.json` 落盘 → `/quit` → 重启 → 重读字节一致；
  4. 真实逐字键入若 taps 无法表达，用 splash 内预设值 + run_command 写盘链路替代取证，并把「逐字 IME 键入」单列 NOT_RUN（所需授权：macOS Automation/Accessibility）；滚动后点击用 taps 直接命中尾部按钮坐标取证（capture 帧可定坐标）。
- 改后验证：rc.1 launcher.log 出现探针表单 eval 6361B + card 行；capture 帧显示表单与中文；`probe_state.json` 字节回读一致；逐字键入子项要么有 taps 证据要么单列 NOT_RUN。
- 证据：`review-r7/verify/results/host-run-probeform.json`、`review-r7/verify/logs/launcher-probeform.log`、r8 `probe-form/bundle/main.splash`（6361B）。

### D-R7-4（P2，必需修复·交接材料同步：错误根因已写入 GATES.json / CANDIDATE / ACCEPTANCE_MAPPING）

- 文件/行：`docs/optimization/2026-10-09-desktop/GATES.json` M0.blockers 第 1/2 条；`r8/CANDIDATE.json` `r6_review_resolutions.D-R6-1/D-R6-2` 与 `ui_install_failure_reason`；`r8/results/ACCEPTANCE_MAPPING.md` T28 行与「D-R6-1/2/3 增量」表。
- 预期/实际：上述位置均断言「rc.1 binary legacy reader + 需重链」，与 D-R7-1/D-R7-2 的复核证据矛盾。
- 影响：后续模块与人工裁决会读到错误的外部依赖结论。
- 具体修改方案（r9）：随 D-R7-1/D-R7-2 修复一并改写；T28 在 r9 取得候选方自己的运行证据后可从 BLOCKED 转为有证据状态；U09（1280×800 已在审查 run 中跑过，候选需自证）/U11（1440×900 等）可用同一入口低成本补测。
- 改后验证：三处文字与 r9 实测结论一致，无残留「binary bug」表述。

## 判定

- 最终结论：**FAIL**
- 本次结论的精确范围：M0 r8 候选（`M0-r8-worktree`，HEAD `8d73056…`）。硬验收 1（候选可定位、宿主真实启动、来源明确）与 4（隔离边界、现场完整）PASS；硬验收 2 各能力如实记录、无越级；D-R5-1/2/3/4/5 维持闭合；D-R6-3 维持 RESOLVED；G0-B/G0-E 按 Abram 2026-10-10 06:55 裁决维持「延期缺口」。但 r8 对 D-R6-1/D-R6-2 的 BLOCKED 结论与根因归因被本审查独立证伪（D-R7-1/D-R7-2），且硬验收 3 在目标宿主上仍零证据（D-R7-3），必需检查未通过，不得放行。
- 审查方新确立的事实（供 r9 直接引用，证据在 `review-r7/verify/`）：**(1) 业务工作台（当前 55781B 版本）可在官方 rc.1 宿主内非交互启动、渲染、tick、并被脚本化 tap 驱动完成真实 createDraft 落盘；(2) 入口是 `--test-action launch-hub:<id>`，不是 `MAKEPAD_WM_TEST_APP`；(3) rc.1 链接 ba36df0 系 app-hub（新 reader + adopt），不存在需重链的 binary bug；(4) catalog 准入层有效拦截未收录应用（探针表单被拒）。**
- 必修项：D-R7-1、D-R7-2、D-R7-3（D-R7-4 随修）。
- 延期缺口（Abram 已裁决，不判 BLOCKED/FAIL）：G0-B（M2 到期）、G0-E（M3 到期）。
- 其余阻塞与未测项（维持如实记录）：G0-C 并发零证据；G0-D 宿主 app_storage 授权路径未测；G0-F 提醒调度/due_at/跨重启恢复未实测；T29/T32 BLOCKED；U09/U11 候选方未自证（审查 run 已证 1280×800 可跑）；逐字 IME 键入（-1743）可用 taps + splash 写盘链路替代取证，剩余子项单列 NOT_RUN。
- 受影响先前模块是否已复验：M0 无前置模块；`docs/build-loop/ACCEPTANCE.json` 未触动；P06/P07/P08 UNASSESSED 未改写；历史后端 PASS 未被冒充为原生 PASS。
- 门禁与原台账更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=FAIL，review_report 指向本文件，blockers 按 D-R7 系列重写，previous_review 追加 r6→r7 链）。
- 是否允许下一模块：**否**。
- 若 FAIL/BLOCKED，留在本模块的修复/解阻指令：
  1. r9 按 D-R7-1：改用 `--test-action launch-hub:octosense-repair`（含 catalog 接受前提），交付业务工作台在 rc.1 的完整运行证据链（launched 行 + 55781B eval + capture 帧 + tap 落盘 + 关开重读）；
  2. r9 按 D-R7-2：重写根因段落，删除「binary bug/需重链」表述，同步订正 ACCEPTANCE_MAPPING 与 CANDIDATE；
  3. r9 按 D-R7-3：用授权 A 的离线签名把探针表单入 catalog，在 rc.1 完成表单渲染/中文/落盘/重读/滚动后点击取证；逐字键入不可为则单列 NOT_RUN；
  4. 全部为本机可完成工作（离线签名已授权、taps/capture 不依赖 -1743），**无需 Abram 新授权**；宿主启动遵守后台 + HIDE_WINDOWS + 自控 /quit + pgrep 无残留规矩。
