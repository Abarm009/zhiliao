# M0 独立 Review r5 — r6 离线签名 catalog + install_staged 候选复核

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-10 03:40 CST（Asia/Shanghai）
- candidate_id：`M0-r6-worktree`；base：`M0-r5-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`（逐项核实，与 r6 CANDIDATE.json 一致）
- 审查开始/结束时快照是否一致：开始与结束 `git status --porcelain` 均为同一 17 项（8 修改 + 9 未跟踪），与 `r6/snapshot/status-before.txt` 逐行一致；业务文件零改动。审查产生的写操作全部在 `runtime/optimization/2026-10-09/M0/{r6/logs,review-r5}/` 内：复跑脚本覆写了 `r6/logs/{launcher.log,local-install-attempt.json,install-attempt.json}`（原件已备份至 `review-r5/r6-logs-backup/`，且与 `r6/results/` 留存件 diff 一致）；复跑中官方宿主把一份手工放置在 `apps/octosense-repair/bundle` 的旧布局 bundle 迁移到 `apps/.bundles/`（见 D-R5-2），审查后已移回原位。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r6.md`
- 已核对前置模块 PASS 与受影响回归：M0 无前置模块；r4 Review BLOCKED 的 D-R4-1/2（宿主可启动）本轮独立复跑确认闭合；D-R4-3（install_staged）候选声称闭合，本轮复核**不成立**（D-R5-1）。
- 实际环境 / 模型路由 / 宿主：darwin（Darwin 25.6.0）；宿主 = `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`（官方 `desktop-v0.1.0-rc.1` macOS aarch64），本轮直接复算 octosense `3e127963…` / octos-kernel `a3e46a45…`，与 r3 receipt 及 CANDIDATE 一致；固定官方源码 = `r5/source/`（Shell `933abbcf`、App-Hub `ba36df05`，INDEX.json match=true）。当前工具不具备主会话 Router 活动查询/切换接口，**未确认**。
- 已阅读范围：AGENTS.md；`docs/optimization/2026-10-09-desktop/00/02/04`、M0 模块文件、GATES.json；r4 REVIEW 与 r6 IMPLEMENTATION 全文；r6 CANDIDATE.json、probe 源码（isolated_launcher.py、isolation.sb、environment.json、install_probe/src/main.rs、Cargo.toml）、全部 results/ 与 logs/；r5 source/INDEX.json 及钉版源码；官方 `client.rs` 与 native-build 克隆同名文件全文比对；工作树 `app/bundle/main.splash` 身份相关行。
- 已运行范围：
  - `git rev-parse HEAD`、`git status --porcelain` 与快照比对（一致）；
  - 复算 `app/bundle/main.splash`（`8aa1022c…`）、`app/bundle/manifest.json`（`e2025193…`）、`r6/staging/main.splash`（与工作树逐字节一致）、宿主两二进制 SHA-256 —— 全部与 CANDIDATE 一致；
  - `hub verify r6/local-mirror/catalog.json --anchor 1ce400c8…` → `catalog sequence 1 verified, 1 entries`（仅用公开锚，私钥已删，`keys/` 为空目录）；
  - 复算 catalog.json SHA-256 `c6fba1f5…` 与 key-files-sha256.txt 一致；staging/artifact/install-root 三方 manifest SHA `3dd44f4e…` 一致；
  - 后台复跑 `r6/probe/isolated_launcher.py`（60s 窗口，脚本自控终止，非 --help）：preflight exit 0、`host_started=true`、`host_exit_code=0`、`host_terminated_by_probe=true`，新 launcher.log 44 行（6415 B）含 kernel ready / llm profile 路径 / model service registered / 单 Consent / 10 模块链接 / Splash eval 809B / PingFang SC；结束后 `pgrep -fl OctoSense.app` 无残留进程；
  - 在全新目录 `review-r5/probe-rerun/`（仅拷入 local-mirror）复跑 `r6_install_probe`：ALL OK，install 落 `install-root/octosense-repair/bundle`，manifest SHA 一致 —— probe 可复现，但见 D-R5-1；
  - 对比官方 ba36df05 钉版源码与 probe 实际依赖的 `runtime/native-build/OctoSense-App-Hub` 克隆：5 个钉版文件 SHA-256 全部不一致（详见 D-R5-1）；
  - 验证 `~/.octosense` mtime 仍为 2026-10-09 22:58（r6 期间及本轮复跑均未触动）；
  - launcher.log L40 `news: fetched 0 new, 0 kept, 7 sources (7 failed)` —— 佐证 sandbox `deny network-outbound` 实际生效。
- 未运行范围及原因：
  - 真实 UI 驱动（osascript 复现 `-1743`，Automation/Accessibility 未授权，与候选一致）；
  - 真实模型调用（无授权 provider；launcher.log 仅 profile 路径读取，未发起请求）；
  - 可信双主体（宿主仅注册单 Consent sheet；本环境不另起第二 subject，属候选未做项）；
  - picker / due_at 持久化 / 跨重启提醒恢复 / 时钟回拨注入（候选未做，本轮不代做）；
  - 用官方钉版源码重建 hub/probe（属修复方工作，Review 不代修）。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 候选定位与 B 包/工作树分离 | git HEAD/status + shasum 工作树与 staging bundle | 与 CANDIDATE 一致；B 包与 v2 工作树不混 | HEAD `8d73056…`、17 项 status、main.splash `8aa1022c…`、manifest `e2025193…` 全一致；staging 与工作树同源；已提交 B 包另标 `B-candidate-8d73056` 未混入 | PASS | 本轮 shasum/git 输出；r6 CANDIDATE.json |
| 宿主二进制来源 | 复算 r3 留存官方 rc.1 两二进制 | 与 receipt 一致 | `3e127963…`/`a3e46a45…` 一致；来源为官方 release + r3 receipt，非版本字符串 | PASS | 本轮 shasum |
| 亲自启动宿主 | 后台复跑 isolated_launcher.py，测后 pgrep | host_started=true 且无残留 | host_started=true、exit 0、探针自动终止、无残留进程；44 行 log 服务/模块/字体齐全 | PASS | 本轮 task 输出 JSON；r6/logs/launcher.log（本轮生成）；pgrep |
| 身份来源非下拉框 | launcher.log 主体注册行 + main.splash L55–90 | 不把 role/actor 下拉当身份证据 | log 仅单 `Consent` sheet（lib.rs:366）；main.splash `USERS`/`STATE.actor` 为脚本内演示选择；候选未冒认，G0-B 维持 BLOCKED | PASS（候选如实） | launcher.log L8；main.splash L55–90 |
| 离线 catalog 合规性 | hub verify 仅用公开锚；keys/ 检查 | 私钥已删且 catalog 仍验证 | `catalog sequence 1 verified, 1 entries`；keys/ 空；未联网/未 publish/未上架（catalog 仅在 local-mirror） | PASS | 本轮 hub verify；key-deletion.json；ls keys/ |
| install_staged 对照固定官方契约 | 比对 probe 依赖 crate 与官方 ba36df05 钉版 | 同一契约 | **不一致**：probe 经 Cargo.toml path 依赖 native-build 无 .git 旧快照（历史主张 6741dea），5 个钉版文件 SHA 全部不同；落点 `<root>/<id>/bundle` 为旧布局，官方为 `<root>/.bundles/<id>/bundle`（client.rs L23–32） | **FAIL（D-R5-1）** | 本轮 sha256 比对；官方 client.rs L18–88 vs native-build client.rs |
| 宿主 home 洁净度 | stat birth/mtime + 内容比对 | home 仅宿主自己写入 | `apps/octosense-repair/{bundle,data/notes}` birth 03:18:21，内容为 03:17:44 probe 产物的未记录手工副本；本轮复跑触发官方宿主 `adopt_legacy_install` 迁移 | **FAIL（D-R5-2）** | stat %SB；notes 内容与 install-root 逐字一致 |
| 安装判据脚本 | 审 isolated_launcher.py L123/L158 | 判据路径 = 官方布局 | 脚本查 `OCTOSENSE_HOME/.apps` 与 `OCTOSENSE_HOME/.bundles/…`，官方实际为 `OCTOSENSE_HOME/apps` 与 `apps/.bundles/…` → 假阴性 | **FAIL（D-R5-3）** | isolated_launcher.py；官方 client.rs L23–32；宿主实际写 apps/.host、apps/.system |
| 模型最小正向及不可用 | 对照官方契约查 launcher.log | 真实成功/真实拒绝 | service registered 但无 provider、零请求；候选记 BLOCKED 如实 | PASS（维持 BLOCKED） | launcher.log L6–7 |
| 真实文件 picker/宿主存储路径 | 查候选证据 | 经宿主 picker/存储服务 | 候选证据为 probe 进程内 std::fs 写读/rename，非宿主存储授权路径；picker NOT_RUN | **FAIL（D-R5-4，结论超出证据）** | install_probe/src/main.rs step 3/4 |
| 原子性/并发/权限/提醒能力 | 对照官方契约核路线声明 | 有证据或如实记边界 | 原子 rename 仅文件系统原语级；并发零证据；权限仅旧 crate `policy::resolve` 输出 caps={storage}（官方为 admit_and_resolve_dir 按 catalog 记录密钥）；提醒仅 "modules linked" 一行。候选对 G0-C/G0-F 维持 BLOCKED 如实 | PASS（如实）+ 未验证边界记录 | launcher.log L9；install-probe.log；官方 client.rs may_run/install_staged |
| 失败与重试 | 查脚本 preflight 失败分支 | 失败不启动 | preflight/catalog verify 失败则不启动分支在位；本轮 preflight 通过 | PASS | isolated_launcher.py L89–92 |
| 重启恢复 | probe step 2 复跑 | installed_version/may_run | 可复现，但语义为旧 crate（may_run 仅版本字符串比对；官方重验 bundle 字节） | 部分（见 D-R5-1） | review-r5/probe-rerun 输出 |
| 数据边界 | stat ~/.octosense + sandbox profile | 不写项目外 | `~/.octosense` mtime 2026-10-09 22:58 未动；isolation.sb 仅放行 r6；news 7 源全失败佐证断网 | PASS | stat；isolation.sb；launcher.log L40 |
| 业务文件零改动 | git status 始末比对 | 不增不减 | 同一 17 项；ACCEPTANCE.json 改动为既有未提交项，非本轮新增 | PASS | git status × 2 |
| 既有用例映射文件 | 读 r6/results/ACCEPTANCE_MAPPING.md | 与本论判定一致 | 仍为 r4 版本（标题/列名未更新），r6 §5 翻项未落入 | FAIL（D-R5-5，文档准确性） | ACCEPTANCE_MAPPING.md L1–4 |

## 缺陷

- **D-R5-1（P1，必需修复·install_staged 证据未对齐固定官方契约）**
  - 文件/行：`runtime/optimization/2026-10-09/M0/r6/install_probe/Cargo.toml` L9–10（path 依赖 `runtime/native-build/OctoSense-App-Hub/crates/{app-hub,app-policy}`）；`reports/M0_IMPLEMENTATION_r6.md` L96–101、L148、L151（G0-A/G0-D PASS 结论）；GATES.json M0 blockers 首条（"D-R4-3 已闭合"）。
  - 触发：`sha256` 比对 native-build 克隆 vs `r5/source/OctoSense-App-Hub`（官方 ba36df05 钉版，INDEX match=true）5 个文件全部不一致；`diff` 显示官方 `client.rs` 多出 `INSTALLS_DIR=".bundles"`（L23）与 `install_root/installed_bundle_dir`（L26–32）、`adopt_legacy_installs` 迁移（L37–88）、`check_reserved_id`、`same_manifest` 全量比对、`admit_and_resolve_dir(…, self.publisher_keys())`（按 catalog 记录密钥验签而非调用方传入）、`check_host_apis`，且官方 `may_run` 经 `verify_release_bundle`+`check_bounds` 重验 bundle 字节；native-build 旧快照均无（其 `install_dir` = `<root>/<id>/bundle`，may_run 仅版本字符串比对）。
  - 预期：r4 Review 必修项 2 要求落点 `<id>/.bundles/<id>/bundle`、按固定官方契约实测。
  - 实际：probe 落点 `install-root/octosense-repair/bundle`（旧布局）；`may_run: ok` 为旧语义；catalog 签名/验证全部用旧 hub 二进制（2026-10-01 11:30 构建）自证，未经官方 CLI 语义复核（官方 hub.rs 要求既有 catalog 先过 `--anchor` 历史校验、`--publisher-key` 不能替换已记录密钥，r6 的 publish 命令序列在官方 CLI 下是否成立未验证）。
  - 影响：D-R4-3「已闭合」与 G0-A「PASS」不成立；「本地 catalog / install_staged 路线可行」的裁决证据对的是旧 crate，不等于官方宿主契约可行；宿主真实安装路径（`.bundles`）端到端仍无证据。
  - 最小修复：r7 用 `r5/source/OctoSense-App-Hub`（已钉版）补齐 crate 全量文件并钉版构建 probe 与 hub CLI（或按官方 rev `ba36df0505e198f998201af312ff5184df98cae9` 重新获取），重跑 keygen→certify→stamp→sign-manifest→publish（确认官方 CLI 下命令序列与参数仍合法）→install_staged；验收落点必须为 `<install_root>/.bundles/octosense-repair/bundle`，并在报告引用官方 client.rs 行号说明语义差异已覆盖。
  - 改后验证：probe 输出 digest/签名/policy 与官方语义一致；`hub verify` 用官方构建的 CLI 通过；落点路径断言写进 probe（不存在 `.bundles` 落点即失败）。

- **D-R5-2（P2，必需修复·宿主 home 被未记录的手工复制污染）**
  - 文件/行：`runtime/optimization/2026-10-09/M0/r6/home/.octosense/apps/octosense-repair/{bundle,data/notes}`；报告与 CANDIDATE.json 全文无此记录（报告 L131 仅称 `home/.octosense/{apps,secrets,wm,themes}` 被宿主写入）。
  - 触发：`stat -f %SB` → bundle 与 data/notes birth 均为 2026-10-10 03:18:21，内容 = 03:17:44 probe 产物（notes 为 rename 后的"更新版"文本，与 `install-root/octosense-repair/data/notes` 逐字一致）；birth 早于其父目录 `.bundles` 的 birth（03:27:02）证明后来发生了 rename 迁移。
  - 预期：隔离 home 内一切状态要么由宿主/probe 产生并有记录，要么在报告中显式声明为手工布景。
  - 实际：候选在 03:18:21 把 probe 安装产物手工复制进宿主 home 的旧布局位置，未记录；本轮审查复跑时官方宿主启动即执行 `adopt_legacy_install` 把它迁移到 `apps/.bundles/octosense-repair/bundle`（审查后已移回原位）。
  - 影响：此后任何"宿主识别/未识别已安装应用"的观察都被污染；违反 02 规则"证据类型不能混用"；也使候选自己"UI 未触发即无安装"的结论建立在不洁净现场上。
  - 最小修复：r7 用全新空 home 重跑；任何手工布景必须写入报告与 CANDIDATE 的 environment 段；删除该未记录副本或将其转为显式测试步骤。
  - 改后验证：新 home 启动前后 `find apps/` 快照对比可解释每一个目录的来源。

- **D-R5-3（P2，必需修复·安装成功判据路径错误导致假阴性）**
  - 文件/行：`runtime/optimization/2026-10-09/M0/r6/probe/isolated_launcher.py` L123（`OCTOSENSE_HOME/.apps`）、L158（`OCTOSENSE_HOME/.bundles/octosense-repair/bundle`）。
  - 触发：对照官方 client.rs L23–32 与宿主实际写入（`apps/.host`、`apps/.system`）。
  - 预期：判据路径 = `OCTOSENSE_HOME/apps` 与 `OCTOSENSE_HOME/apps/.bundles/<id>/bundle`。
  - 实际：脚本查的是不存在的 `.apps`/`.bundles` 顶层路径，`pre/post_install_state` 恒为 false，"no install evidence" 为判据 bug 的假阴性（即使宿主真安装也检测不到）。
  - 影响：UI install NOT_RUN 的结论方向正确（osascript -1743 确实未触发），但判据代码错误使该证据链不完整；r7 修 D-R5-1 后若沿用此脚本会继续误判。
  - 最小修复：改两处路径为官方布局；补一条"启动前后 apps/ 树 diff"判据。
  - 改后验证：在干净 home 重跑，预期 post_install_state 准确反映 apps/.bundles 是否存在。

- **D-R5-4（P1，必需修复·G0-D / P02 / "存储恢复 PASS" 结论超出证据）**
  - 文件/行：`reports/M0_IMPLEMENTATION_r6.md` L98–99（step 3/4）、L151（G0-D PASS）、L159（P02 PASS）、L165（"中文输入保留部分 PASS"）；`install_probe/src/main.rs` step 3/4。
  - 触发：step 3/4 是 probe 进程内 `std::fs::write/read/rename`，不经过宿主 app_storage 授权路径；时钟证据为同秒 `delta=0`，未测回拨拒绝；G0-D 原定义是"真实附件写入、回读、归属及失败恢复"，P02 是"完整源码和依赖版本、干净环境启动/构建说明"。
  - 预期：PASS 必须由对应层级证据支撑；工具链/依赖版本未钉版（D-R5-1）时 P02 不成立。
  - 实际：文件系统原语级证据被记为 G0-D 原生 PASS；P02 在 probe/hub 工具链为无 .git 旧快照时记 PASS。
  - 影响：映射翻项误导后续模块（M5 附件、M7 发布准备会引用 M0 结论）。
  - 最小修复：G0-D、P02 退回 BLOCKED；如要保留部分证据，改写为"文件系统原语级（非宿主存储服务）证据"，并把宿主存储授权路径（grant→app_storage 写读）列为未测。
  - 改后验证：映射表、报告 §5、GATES.json 三处结论一致且无越级。

- **D-R5-5（P3，必需修复·验收映射与门禁文字失真）**
  - 文件/行：`runtime/optimization/2026-10-09/M0/r6/results/ACCEPTANCE_MAPPING.md` L1–4（标题仍为"M0 r4 验收责任映射"、列名"r4 目标原生"）；GATES.json M0 blockers 中"sandbox 阻 keychain 写（launcher.log L5 os error 1）"。
  - 触发：读文件与比对 r5/r6 launcher.log。
  - 实际：映射文件是 r4 副本，r6 §5 的三处翻项未落入；GATES 引用的 os error 1 出自 **r5** 的 log L5（Mail secrets 目录写 EPERM，非 keychain 字面），r6 自己的 log 已无该行（r6 写 secrets 成功）——描述张冠李戴。
  - 影响：后续模块按映射文件分工时拿到的是 r4 旧判定。
  - 最小修复：r7 重写映射文件头部与本轮判定列；GATES 文字改为"r5 环境 secrets 目录写 EPERM（app_storage/lifecycle.rs:442），r6 同环境写成功；可信双主体未实测"。
  - 改后验证：映射文件、报告、GATES 三处一致。

## 判定

- 最终结论：**FAIL**
- 本次结论的精确范围：M0 r6 候选（`M0-r6-worktree`，HEAD `8d73056…`）。硬验收 1（候选可定位、宿主真实启动、来源明确）与 4（隔离边界、现场完整）本轮独立复核 **PASS**；硬验收 2 中模型/身份维持如实 BLOCKED，但"真实文件/存储恢复 PASS"证据越级（D-R5-4）；硬验收 3（原生表单中文输入+滚动后操作）仍无原生证据（候选自报 NOT_RUN）；硬验收 5（路线足以支撑后续）因 D-R5-1 不成立——install_staged 端到端证据对的是过时 crate 快照，官方契约（`.bundles` 落点、catalog 密钥验签、may_run 重验字节）未实测。
- 必修项：D-R5-1、D-R5-2、D-R5-3、D-R5-4、D-R5-5（修复方向与验证方式见各条）。
- 阻塞与未测项（维持如实记录，非本轮候选缺陷）：真实 UI 驱动（osascript -1743，Automation/Accessibility 未授权）；真实模型 provider（未授权配置）；可信双主体（单 Consent sheet）；picker/due_at 持久化/跨重启提醒恢复/时钟回拨；宿主 UI 入口的真实 install 点击路径。
- 受影响先前模块是否已复验：r4 的 D-R4-1/2 本轮独立复跑确认闭合（host_started=true、无残留）；D-R4-3 复验**不闭合**（转 D-R5-1）；D-R4-4/5 维持未闭合。`docs/build-loop/ACCEPTANCE.json` 未触动；P06/P07/P08 UNASSESSED 未改写；G0-C/T22 等历史后端 PASS 未被冒充为原生 PASS。
- 门禁与原台账更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=FAIL，review_report 指向本文件，blockers 重写）；不动 ACCEPTANCE.json。
- 是否允许下一模块：**否**。
- 若 FAIL/BLOCKED，留在本模块的修复/解阻指令：
  1. r7 按 D-R5-1 用官方钉版源码（`r5/source/OctoSense-App-Hub` @ ba36df05，必要时按 rev 重新获取全量 crate）重建 hub CLI 与 install probe，重跑离线签名 catalog → install_staged，落点必须 `…/.bundles/octosense-repair/bundle`；注意官方 hub.rs 对既有 catalog 的 `--anchor` 历史校验与 `--publisher-key` 限制，先静态核对命令序列再执行。
  2. r7 按 D-R5-2 换全新空 home，一切手工布景显式记录。
  3. r7 按 D-R5-3 修判据路径后重跑宿主（后台启动、窗口自控终止、测后确认无残留进程；禁止 --help）。
  4. r7 按 D-R5-4/D-R5-5 把 G0-D/P02 退回 BLOCKED、重写映射文件与 GATES 文字；三处结论一致。
  5. 解阻条件不变：UI 自动化需机器级 Automation/Accessibility 授权；可信双主体与真实模型 provider 需 Abram 另行授权。以上均不需要本次 FAIL 修复等待授权——D-R5-1/2/3/4/5 全部为本机可完成的修复。
