# M0 独立 Review r6 — r7 官方钉版源码 + install_staged 端到端候选复核

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-10 11:10 CST（Asia/Shanghai）
- candidate_id：`M0-r7-worktree`；base：`M0-r6-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`（逐项核实，与 r7 CANDIDATE.json 一致）
- 审查开始/结束时快照是否一致：开始与结束 `git status --porcelain` 均为同一 17 项（8 修改 + 9 未跟踪），与 `r7/snapshot-status-before.txt` 逐行一致；业务文件零改动。审查写操作全部在 `runtime/optimization/2026-10-09/M0/review-r6/` 内（独立 home/tmp/cache/config/data、local-mirror 副本、probe、logs、install-root），未触碰 r7 候选任何文件。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r7.md`
- 已核对前置模块 PASS 与受影响回归：M0 无前置模块；r5 Review（Kimi，FAIL）五条必修 D-R5-1/2/3/4/5 本轮全部独立复核**闭合**（逐条见必需检查表）。
- 实际环境 / 模型路由 / 宿主：darwin（Darwin 25.6.0）；宿主 = `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`（官方 `desktop-v0.1.0-rc.1` macOS aarch64），本轮直接复算 octosense `3e127963…` / octos-kernel `a3e46a45…`，与 r3 receipt 及 CANDIDATE 一致；钉版源码 = `r7/source-pin/OctoSense-App-Hub`（App-Hub `ba36df05`，client.rs `27701be8…` / hub.rs `bc21e988…` 复算一致）+ `r5/source/OctoSense`（Shell `933abbcf`）。当前工具不具备主会话 Router 活动查询/切换接口，**未确认**。
- 已阅读范围：AGENTS.md；`docs/optimization/2026-10-09-desktop/00/01/02/04`、M0 模块文件、GATES.json；r5 REVIEW 与 r7 IMPLEMENTATION 全文；r7 CANDIDATE.json、probe 源码（isolated_launcher.py、isolation.sb、environment.json、install_probe/src/main.rs、Cargo.toml）、全部 results/ 与 logs/；钉版官方 `client.rs`（INSTALLS_DIR/install_staged/may_run/verify_release_bundle/admit_and_resolve_dir/same_manifest 段落）、钉版 Shell `apps.rs`（AppRegistry/--module/is_card_app/installed_bundle 段落）与 `octosense/catalog.rs`（--apps 目录）；工作树 `app/bundle/main.splash` 身份与控件相关行；r1/r2/r4 IMPLEMENTATION 相关段落。
- 已运行范围（全部在 `review-r6/` 隔离目录、sandbox profile 仅放行该目录、deny network-outbound）：
  - `git rev-parse HEAD`、`git status --porcelain` 始末比对（一致）；
  - 复算 12 项 SHA-256：main.splash `8aa1022c…`（工作树=staging）、manifest `e2025193…`、catalog `b4493bb1…`、三方 manifest `d758ed88…`、client.rs/hub.rs 钉版值、hub CLI `c233094f…`、宿主两二进制 —— 全部与 CANDIDATE 一致；
  - 钉版 hub CLI `hub verify review-r6/local-mirror/catalog.json --anchor a3de88ab…` → `catalog sequence 1 verified, 1 entries`（仅用公开锚；`r7/keys/` 确认为空目录）；
  - 在 `review-r6/`（仅拷入 local-mirror 副本）复跑 `r7_install_probe`：`r7_install_probe: ALL OK`，install 落 `review-r6/install-root/.bundles/octosense-repair/bundle`（官方布局），重启 `installed_version=Some("0.1.0-b")`、`may_run: ok`，中文 66B note 字节一致，原子 rename 成立，安装 manifest SHA `d758ed88…` 一致 —— probe 可复现；
  - 后台复跑隔离启动器（复制脚本 + 重写 environment.json 指向 review-r6 + 改写 isolation.sb 放行 review-r6；60s 窗口、脚本自控终止、非 --help）：preflight exit 0、catalog 预校验通过、`host_started=true`、`host_exit_code=0`、`host_terminated_by_probe=true`、`post_terminate_pgrep=""`；新 launcher.log 45 行含 kernel ready / llm profile 路径 / model service registered / 单 Consent / 10 模块链接 / Splash eval 809B / news 7 源全失败（断网佐证）；结束后 `pgrep -fl OctoSense.app` 无残留（exit 1），桌面无残留窗口；
  - 验证 `~/.octosense` mtime 仍为 2026-10-09 22:58:31（r7 期间及本轮复跑均未触动；注意候选文本误记为 21:38，见 D-R6-3）；
  - 对照钉版 Shell 源码确认已安装应用的托管与启动路径（apps.rs:517 `is_card_app`、:726 card module 托管、:774–781 官方 `.bundles` 落点），并确认 `--module` 仅切换托管形态、不构成非交互启动入口（apps.rs:681 仅写 overrides）；
  - 全文 grep 确认当前 `app/bundle/main.splash`（1312 行）**没有任何 `TextInput`/`TextEdit` 控件**（0 处），`ScrollYView` 仅 L1256 一处。
- 未运行范围及原因：
  - 真实 UI 驱动（osascript 复现 `-1743`，Automation/Accessibility 未授权，与候选一致）；
  - 真实模型调用（无授权 provider；launcher.log 仅 profile 路径读取，未发起请求）——按 Abram 2026-10-10 06:55 裁决记「延期缺口」，见判定节；
  - 可信双主体（宿主仅注册单 Consent sheet）——同上，延期缺口；
  - picker / due_at 持久化 / 跨重启提醒恢复 / 时钟回拨注入（候选未做，本轮不代做）；
  - 把业务 bundle 装入隔离宿主 home 并尝试非交互启动（属修复方工作，Review 不代修，见 D-R6-1）。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 候选定位与 B 包/工作树分离 | git HEAD/status + shasum 工作树与 staging bundle | 与 CANDIDATE 一致；B 包与 v2 工作树不混 | HEAD `8d73056…`、17 项 status、main.splash `8aa1022c…`（工作树=staging 逐字节同源）、manifest `e2025193…` 全一致；已提交 B 包另标 `B-candidate-8d73056` 未混入 | PASS | 本轮 shasum/git 输出；r7 CANDIDATE.json |
| 宿主二进制来源 | 复算 r3 留存官方 rc.1 两二进制 | 与 receipt 一致 | `3e127963…`/`a3e46a45…` 一致；来源为官方 release + r3 receipt，非版本字符串 | PASS | 本轮 shasum |
| 亲自启动宿主 | 后台复跑隔离启动器（review-r6 独立 home），测后 pgrep | host_started=true 且无残留 | host_started=true、exit 0、探针自动终止、无残留进程/窗口；45 行 log 服务/模块/字体齐全 | PASS | review-r6/logs/local-install-attempt.json、launcher.log；pgrep exit 1 |
| 身份来源非下拉框 | launcher.log 主体注册行 + main.splash L55–90 | 不把 role/actor 下拉当身份证据 | log 仅单 `Consent` sheet（lib.rs:366）；main.splash `USERS`（L55）/`STATE.actor`（L77/86/204/323/328/338/393/454/458）为脚本内演示选择；候选未冒认，G0-B 如实记 BLOCKED（现按 Abram 裁决记延期缺口） | PASS（候选如实） | review-r6 launcher.log L8；main.splash L55–90 |
| 离线 catalog 合规性 | 钉版 hub CLI verify 仅用公开锚；keys/ 检查 | 私钥已删且 catalog 仍验证 | `catalog sequence 1 verified, 1 entries`；keys/ 空；未联网/未 publish/未上架（catalog 仅在 local-mirror 与 review-r6 副本） | PASS | 本轮 hub verify；key-deletion.json；ls keys/ |
| install_staged 对照固定官方契约（D-R5-1 复核） | 比对 probe 依赖与钉版源；复跑 probe | 同一契约；落点 `.bundles/<id>/bundle` | probe Cargo.toml path 依赖 = `r7/source-pin/.../crates/{app-hub,app-policy}`；钉版 client.rs 含 `INSTALLS_DIR=".bundles"`（L23）、`adopt_legacy_installs`（L37）、`admit_and_resolve_dir(…, self.publisher_keys())`（L460）、`check_host_apis`（L463/532）、`may_run`→`verify_release_bundle` 重验字节（L490–541）；本轮复跑落点 `review-r6/install-root/.bundles/octosense-repair/bundle`、may_run ok、三方 manifest SHA 一致 | **PASS（D-R5-1 闭合）** | 本轮 probe 复跑输出；client.rs L23–541 |
| 宿主 home 洁净度（D-R5-2 复核） | 全新 review-r6 home 启动前后对比 + r7 home 检查 | home 仅宿主自己写入 | review-r6 home 启动前为空，启动后仅 `apps/.host`、`apps/.system`、`secrets/os.mail`、`wm/themes/…`；r7 home 同样只含宿主自写目录，无 octosense-repair 污染 | **PASS（D-R5-2 闭合）** | find home（两侧）；stat birth 03:46（r7 运行窗口内） |
| 安装判据脚本（D-R5-3 复核） | 审 isolated_launcher.py L134–174 | 判据路径 = 官方布局 | `apps_root = OCTOSENSE_HOME/apps`、`installed_bundle_dir_exists` 查 `apps/.bundles/octosense-repair/bundle`，与官方 client.rs L23–32 及宿主实际写入一致 | **PASS（D-R5-3 闭合）** | isolated_launcher.py L134–174 |
| G0-D/P02 结论回退（D-R5-4 复核） | 读 r7 报告 §6 与 ACCEPTANCE_MAPPING.md | G0-D BLOCKED、P02 PARTIAL | 三处（报告、映射、GATES）一致：G0-D BLOCKED（std::fs 非宿主 app_storage 授权路径）、P02 PARTIAL | **PASS（D-R5-4 闭合）** | ACCEPTANCE_MAPPING.md L11/L56；报告 L191/L199 |
| 映射与门禁文字（D-R5-5 复核） | 读 ACCEPTANCE_MAPPING.md 头部与 G0 段 | r7 版本、判定一致 | 标题「M0 r7 验收责任映射」、列名「r7 目标原生」，G0-A–F 与 r7 报告一致 | **PASS（D-R5-5 闭合）** | ACCEPTANCE_MAPPING.md L1–13 |
| 模型最小正向及不可用 | 对照官方契约查 launcher.log | 真实成功/真实拒绝 | service registered 但无 provider、零请求；候选记 BLOCKED 如实。按 Abram 2026-10-10 06:55 裁决，G0-E 记「延期缺口（Abram 已裁决）」，不判 BLOCKED/FAIL | PASS（如实；延期缺口） | review-r6 launcher.log L6–7 |
| 真实文件 picker/宿主存储路径 | 查候选证据 | 经宿主 picker/存储服务 | 候选证据为 probe 进程内 std::fs 写读/rename，候选已自降为 FS 原语级、G0-D 维持 BLOCKED；picker NOT_RUN 如实 | PASS（如实） | install_probe/src/main.rs step 3/4；映射 L11 |
| 原子性/并发/权限/提醒能力 | 对照官方契约核路线声明 | 有证据或如实记边界 | 原子 rename 仅 FS 原语级（如实）；并发零证据（如实）；权限经官方 `admit_and_resolve_dir` 按 catalog 记录密钥验签（本轮 probe 实测 caps={"storage"} hosts={}）；提醒仅 "modules linked" 一行，G0-F 维持 BLOCKED 如实 | PASS（如实）+ 未验证边界记录 | 本轮 probe 复跑；launcher.log L9 |
| 失败与重试 | 查脚本 preflight/catalog 失败分支 | 失败不启动 | preflight/catalog verify 失败则不启动分支在位；本轮两关均通过后才启动宿主 | PASS | isolated_launcher.py L96–100 |
| 重启恢复 | probe step 2 复跑 | installed_version/may_run | 可复现，语义为官方钉版 crate（may_run 重验 bundle 字节 + admit_and_resolve_dir） | PASS | 本轮 probe 复跑输出 |
| 数据边界 | stat ~/.octosense + sandbox profile | 不写项目外 | `~/.octosense` mtime 2026-10-09 22:58:31 未动；isolation.sb 仅放行 r7（候选）/ review-r6（本轮）；news 7 源全失败佐证断网 | PASS | stat；isolation.sb；launcher.log |
| 业务文件零改动 | git status 始末比对 | 不增不减 | 同一 17 项；ACCEPTANCE.json 改动为既有未提交项，非本轮新增 | PASS | git status × 2 |
| **目标宿主上真实启动现有原生工作台**（修改指令 item 3） | 查全部轮次 launcher.log 的 SPLASH eval 字节数 + 报告记录 | 业务 main.splash（55781B）在选定宿主 rc.1 内 eval/渲染 | r3/r4/r5/r6/r7 及本轮复跑全部只有默认空 Splash `eval: 809 bytes`；唯一业务工作台运行证据是 r1 在**旧 card-host** 上的 55771B（且为 r2 改名修复前版本） | **FAIL（D-R6-1）** | 各轮 launcher.log；r1 报告测试表 #1；main.splash 55781B |
| **硬验收 3：最小原生表单中文输入 + 滚动后控件可操作** | grep 当前 bundle 控件；查候选证据 | 原生表单保留中文输入、滚动后控件可操作 | 当前 main.splash 无 TextInput/TextEdit（0 处），用户根本无法键入；候选自报 NOT_RUN 并推给 M1；无探针表单证据 | **FAIL（D-R6-2）** | grep 结果；r1 报告测试表 #3；r7 报告 L205 |

## 缺陷

- **D-R6-1（P1，必需修复·选定宿主上从未运行过现有原生工作台，修改指令 item 3 未达成）**
  - 文件/行：`runtime/optimization/2026-10-09/M0/{r3,r4,r5,r6,r7}/**/launcher.log`（SPLASH 行均 `eval: 809 bytes`，默认空 Splash）；对照 `docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r1.md` 测试表 #1（`eval: 55771 bytes`，**旧 card-host**）；`reports/M0_IMPLEMENTATION_r7.md` §4（仅默认 Splash）与 §6 硬验收 1 结论。
  - 触发：对 r3–r7 及本轮 review-r6 的 launcher.log 逐一轮 grep `[SPLASH] eval`；对比 main.splash 字节数（当前 55781；r1 运行的是 r2 修复 `isReporter`→`isReporterMe` 之前的 55771 版）。
  - 预期：修改指令 item 2 明确「旧 card-host 的检查不能代表目标桌面 Shell」；item 3 要求「真实启动现有原生工作台，检查输入、列表选择、详情、滚动和命名控件刷新……运行后再定性」。在选定宿主（官方 rc.1）上应有业务 bundle 的真实 eval/渲染记录，或精确到源码行号的阻断点记录。
  - 实际：r3 起选定 rc.1 为目标宿主后，业务 bundle 只经历了「签名 → publish → install_staged → may_run」的库级路径，**从未在宿主进程内被加载执行**（809B 是宿主默认空 Splash，不是 main.splash）；r1 的工作台运行证据属于被明确排除的旧 card-host；r2 改名后的当前 55781B 版本从未在任何宿主内原生 eval 过（r4 仅有静态检查）。候选既未尝试把 staged bundle 装入隔离宿主 home（probe install_root 指向 `OCTOSENSE_HOME/apps` 即可，工具链现成），也未从钉版 Shell 源码论证「已安装应用的唯一启动入口是 dock/UI 点击」。
  - 影响：硬验收 1 的「目标桌面宿主能真实启动」只覆盖了宿主外壳，没覆盖「这份桌面应用」本体；M0 目标「确认这份桌面应用准备在哪个宿主版本运行」缺最关键一环——应用在目标宿主里能不能跑起来尚无证据；r2 改名引入的 eval 兼容性风险未被运行定性（架构文档 §8 要求「运行后再定性」）。G0-A 的 PASS 目前只覆盖安装链路，不覆盖运行链路。
  - 根因：r3 切换宿主后，各轮聚焦安装/签名链路修正（D-R4/D-R5 系列），把「宿主可启动」与「工作台在宿主内运行」混为一谈；UI 自动化受阻（-1743）后未再从钉版源码寻找非交互启动路径。
  - 具体修改方案（r8，全部本机可完成，无需新授权）：
    1. 用钉版源 probe 把 r7 staged bundle 安装进全新隔离宿主 home：`install_root = <r8>/home/.octosense/apps`（官方布局落点 `apps/.bundles/octosense-repair/bundle`，即宿主 Store 实际读取位置，钉版 client.rs L23–32 + apps.rs:774–781）；
    2. 从钉版 Shell 源码（`r5/source/OctoSense`）查明已安装 card 应用的启动入口：`apps.rs:517 is_card_app`、:726 card module 托管、:681 `--module` 仅写 hosting overrides（不构成启动）；继续查 dock 点击处理、`MAKEPAD_APP_CONFIG`（apps.rs:194/546）、`--apps` dev catalog（octosense/catalog.rs:143）等是否存在可脚本化的启动/打开路径；
    3. 后台启动宿主（禁止 --help，60s 内自控终止，测后 pgrep 确认无残留），若找到非交互入口则触发启动并在 launcher.log 中捕获业务 splash 的 `eval: ~55781 bytes` 行；若源码证明唯一入口是 UI 点击，则把「已安装→可运行」记为 BLOCKED 并引用源码行号，不得再留作未探索项；
    4. 若业务 splash 成功 eval，记录 tick/Label 刷新与 r2 改名后版本的首个原生运行定性。
  - 改后验证：launcher.log 出现 55781B（±改名差）eval 行，或报告中附源码行号证明不存在非交互入口并记 BLOCKED；安装-识别-启动的每一步都有 log/路径证据。

- **D-R6-2（P1，必需修复·硬验收 3 无任何原生证据，且当前 bundle 无文本输入控件）**
  - 文件/行：`app/bundle/main.splash`（全文 0 处 `TextInput`/`TextEdit`；`ScrollYView` 仅 L1256）；`docs/optimization/2026-10-09-desktop/M0_桌面运行基线与能力裁决.md` 硬验收 3；`reports/M0_IMPLEMENTATION_r7.md` L205（自报 NOT_RUN）；`reports/M0_IMPLEMENTATION_r1.md` 测试表 #3（r1 已发现无输入控件）。
  - 触发：grep 当前 bundle；对照硬验收 3 原文「一个可读写的最小原生表单能保留中文输入，滚动后的控件可操作；浏览器原型不替代」。
  - 预期：M0 交付最小原生表单证据；M0 文件责任允许「探针只放 runtime/optimization 或独立测试目录」——即允许写一个一次性探针 splash 表单，不需要改业务 bundle。
  - 实际：候选把该项整体推给 M1，未做探针表单；中文证据停留在 probe 进程内 std::fs 66B 字节一致（FS 原语级，r7 已如实降级）；「滚动后控件可操作」零证据。
  - 影响：IME/原生文本输入是 M1 框架与 M3 报修表单的前置风险，M0 不定性就把风险带进后续所有模块；硬验收 3 属必需检查，NOT_RUN 不得放行。
  - 根因：候选把「业务 bundle 没有输入控件」（产品形态问题，M1 范围）与「宿主原生文本输入能力未验证」（宿主能力问题，M0 范围）混为一谈，以后者无人执行为由整体留空。
  - 具体修改方案（r8）：
    1. 在 `runtime/optimization/2026-10-09/M0/r8/` 内写一个最小探针 splash（含一个真实文本输入控件、一段预设中文「用户报修：空调不制冷。联系地址：北京朝阳区。」、一个 ScrollYView 长列表和列表尾部按钮），按 D-R6-1 的装载与启动路径在 rc.1 宿主内运行；
    2. 不依赖 UI 自动化即可取证的子项先做：脚本预设中文值 → 渲染 eval 成功 → 经 splash 存储 API 落盘 → 关开重读字节一致（对应 r1 已证明的 saveTasks 路径，但要在 rc.1 上重做）；同时实测 `screencapture` 在本环境是否可用，可用则留存原生渲染截图；
    3. 真实键入中文与滚动后点击若仍被 -1743 阻断，把这两个子项单独记 NOT_RUN，写明所需授权（macOS Automation/Accessibility）与已排除的替代路径，不得以整体 NOT_RUN 掩盖已可验证的子项。
  - 改后验证：探针表单在 rc.1 的 eval/渲染/落盘/重读证据链完整；剩余未测子项逐条列出阻断原因。

- **D-R6-3（P3，建议修复·交接材料中 ~/.octosense mtime 记录失真）**
  - 文件/行：`reports/M0_IMPLEMENTATION_r7.md` §4 末（"mtime 2026-10-09 21:38"）；`runtime/optimization/2026-10-09/M0/r7/CANDIDATE.json` `abram_constraints_respected` 末条。
  - 触发：`stat -f %Sm ~/.octosense` → `Oct 9 22:58:31 2026`；r5 Review L18 亦记录 22:58。
  - 预期/实际：实质结论（r7 期间未触动）成立且有证据，但记录的时间戳与实际不符（21:38 vs 22:58）。
  - 影响：不影响判定；属交接材料准确性瑕疵，r5 曾以同类问题判 D-R5-5。
  - 最小修复：r8 报告中更正为 22:58:31 并保留 stat 输出；顺手即可，不单独要求一轮。

## 判定

- 最终结论：**FAIL**
- 本次结论的精确范围：M0 r7 候选（`M0-r7-worktree`，HEAD `8d73056…`）。r5 五条必修（D-R5-1/2/3/4/5）本轮独立复核**全部闭合**；硬验收 1（候选可定位、宿主真实启动、来源明确）与 4（隔离边界、现场完整）**PASS**；硬验收 2 各能力如实记录、无越级 PASS；硬验收 5 中用户架构选择已全部落地或经 Abram 裁决延期（宿主路线 = 本地 catalog / install_staged，本轮基于官方钉版源码复核成立）。但修改指令 item 3（选定宿主上真实启动现有原生工作台）与硬验收 3（最小原生表单中文输入 + 滚动后控件可操作）仍无目标宿主证据（D-R6-1/D-R6-2），必需检查未通过，不得放行。
- 必修项：D-R6-1、D-R6-2（修复方向与验证方式见各条）；D-R6-3 建议随修。
- 延期缺口（Abram 2026-10-10 06:55 已裁决，不判 BLOCKED/FAIL，照实记录）：**G0-B 可信双主体 / 业务身份来源**（宿主仅单 Consent sheet；延期到 M2 再定）；**G0-E 真实模型 provider**（model service 已注册、无 provider 配置、零请求；延期到 M3 再定）。
- 其余阻塞与未测项（维持如实记录，非本轮候选缺陷）：真实 UI 驱动（osascript -1743，Automation/Accessibility 未授权）；G0-C 并发与崩溃恢复零证据；G0-D 宿主 app_storage 授权路径未测；G0-F 提醒调度/due_at/跨重启恢复未实测；T28/T29/T32、U09/U11 维持 BLOCKED/NOT_RUN；UI 触发 install 路径 NOT_RUN（已由钉版源 probe 在库级补齐 install_staged 证据）。
- 受影响先前模块是否已复验：M0 无前置模块；r5 FAIL 的五条必修全部复验闭合（见必需检查表 6–10 行）。`docs/build-loop/ACCEPTANCE.json` 未触动；P06/P07/P08 UNASSESSED 未改写；G0-C/T02 等历史后端 PASS 未被冒充为原生 PASS。
- 门禁与原台账更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=FAIL，review_report 指向本文件，blockers 更新）；不动 ACCEPTANCE.json。
- 是否允许下一模块：**否**。
- 若 FAIL/BLOCKED，留在本模块的修复/解阻指令：
  1. r8 按 D-R6-1：probe 装载 staged bundle 到全新隔离宿主 home 的 `apps/.bundles`，从钉版 Shell 源码查明非交互启动路径，后台启动宿主取证（禁止 --help、自控终止、测后 pgrep 无残留）；成功则捕获 55781B eval 行，失败则附源码行号记 BLOCKED。
  2. r8 按 D-R6-2：在 r8/ 内做最小探针表单（文本输入 + 预设中文 + ScrollYView 尾按钮），在 rc.1 内完成渲染/落盘/重读取证；真实键入与滚动点击若仍 -1743 则单独记 NOT_RUN 并写明所需授权。
  3. r8 顺手修正 D-R6-3 时间戳。
  4. 以上全部为本机可完成工作，无需 Abram 新授权；UI 自动化的机器级授权仅影响「真实键入/点击」子项的记录方式，不构成等待理由。
