# M0 实施报告 r4 — D7/D8 修复与本地安装路线裁决

**状态：BLOCKED；编码方交接，等待独立 Review，不进入 M1。**

本轮已纠正 D7 的编号语义和 D8 的 Cargo 重写结论，并查明 rc.1 的本地目录安装实现。**未完成目标 Shell 的本轮启动和业务包安装**：隔离启动预检返回 `sandbox_apply: Operation not permitted`，因此没有撤去写入限制继续运行。不能把这个执行环境阻断解释成平台不支持本地安装。真实模型、文件选择、可信双主体、存储恢复及原生交互仍未获本轮运行证据。

- 模块 / 目标：仅 M0 r4；修复 `M0_REVIEW_r3.md` D7、D8，验证用户选定的本地 catalog / `install_staged` 路线。
- candidate_id / base_candidate_id：`M0-r4-worktree` / `M0-r3-worktree`；已提交 B 包另标 `B-candidate-8d73056`。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；没有提交、push、reset、stash。
- 快照、差异与哈希：`runtime/optimization/2026-10-09/M0/r4/snapshot/`。输入清单 `files-before.json` 覆盖 320 个 Git 已跟踪及未忽略文件；保存 59 个已修改/未跟踪路径的内容副本，另有完整 `worktree.diff`、`status-before.txt`、`worktrees.txt`。不只以 HEAD 定位候选。
- 目标宿主：官方 `desktop-v0.1.0-rc.1` macOS aarch64；具体来源、固定 SHA 和哈希见下文。
- 实际开发会话路由：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。按本轮串行约束未创建子代理；未将代理或技能当作主会话切换。当前工具也没有读取当前会话 `createdAt` 并设置标题的接口，标题设置未执行。
- 前置 Review：M0 无前置模块；已读 r1/r2/r3 Review 和 r3 候选报告。r3 是 BLOCKED，不存在前置 PASS。
- 修改文件：新增本报告、r4 隔离证据/探针；仅更新 `GATES.json` 的 M0。r1/r2/r3 报告和 Review 保留原文，本报告明确撤回其中被指出的错误结论。
- 桌面 UI/交互变化：无；没有修改 `app/bundle/main.splash` 或 manifest。
- 接口 / 数据迁移：无。没有启动旧后端、迁移旧数据或重打正式 bundle stamp。
- 应用模型/provider：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。r3 的 `_main` 缺失仅作为历史记录，本轮未启动内核，不能冒称重现。
- 覆盖范围：D7/D8、现场快照、固定源码校验、来源校验、静态守卫调用检查、64 项验收责任映射、隔离启动失败复现。详见测试表。
- 置信度：D7 定义、固定源码安装分支和本轮失败记录 **高**；该业务包在 rc.1 的安装、原生操作和完整能力 **未知**。

## 1. 现场、B 包与数据边界

输入时已有 8 个修改的已跟踪文件：`PROGRESS.md`、`README.md`、`app/bundle/main.splash`、`app/bundle/manifest.json`、`docs/build-loop/ACCEPTANCE.json`、`docs/implementation/10_UI_UX_SPEC.md`、`submission/2026-10-06-native/CURRENT_REVIEW_STATUS.md`、`submission/2026-10-06-native/HUB_ISSUE.md`。另有 51 个未跟踪文件，逐文件见 `snapshot/status-before.txt`，包括桌面 v2、旧备份、bundle 内历史测试数据、M0 报告和门禁；均保留。

|对象|本轮读取结果|适用边界|
|---|---|---|
|已提交 B ZIP|1,544,808 字节；SHA-256 `6a58e27ade7255760e19b6b7229d744eb92799958fd84c728bf0d46c4de1fa12`；12 个文件逐字节匹配 HEAD 对应路径|本地固定提交/归档比对；不是本轮远端递交回读|
|工作树 main.splash|55,781 字节；SHA-256 `8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab`|当前未提交 v2 候选，不冒充已递交 B 字节|
|工作树 manifest|249 字节；SHA-256 `e20251934523392768a4aa459297366e999470d0b71685c46c710bbb5d101031`；stamp `46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404`|本轮未改写、未重新运行摘要准入工具；D9 的历史修复不重新列为 blocker|
|当前权限|仅 `storage`，版本 `0.1.0-b`，ID `octosense-repair`|没有声明 model、octos、认证等能力；宿主服务存在也不等于此包获授权|
|桌面 v2|完整读取 DESIGN_SPEC，相关未跟踪资料保存副本/哈希|HTML/旧 PNG 为设计及历史材料，不是 r4 原生运行证据|
|旧运行数据|没有运行会写旧数据的宿主/后端；没有删除/改写旧 r1/r2/r3、review-r* 和业务数据|320 文件快照不覆盖全部 ignored runtime，不能夸大为全盘历史数据库字节审计|

`app/bundle/data-test/`、`host.log`、`instance.json` 和备份文件是已有现场，已记录而未清理；本轮不把它们作为新运行数据或正式安装路线的一部分。r4 新增文件只在项目内。宿主 HOME、临时目录、缓存和 app-data 的拟定路径均落在 r4；日志记录具体环境。宿主实际未启动，因而没有 r4 宿主写入 `~/.octosense` 的问题；不沿用 r3 “宿主管理数据不算隔离范围”的说法。

## 2. 目标宿主与来源

选择继续验证 rc.1，是为了对同一已校验发行候选修复 D8，避免混入 rc.2 或旧 `a5d847a` 构建的差异；**不声称 rc.1 是最新版本**。本轮通过官方发行页面重新核对版本与来源，并从固定 GitHub SHA 取得 15 个相关源码/锁文件，逐一复算 Git blob SHA 与官方树匹配。

- 官方发行页：[desktop-v0.1.0-rc.1](https://github.com/OctoSense-org/OctoSense/releases/tag/desktop-v0.1.0-rc.1)。macOS 是官方账号发布的本地装配包，不称其为 CI 构建；未 Developer ID 签名/公证。
- Shell：`933abbcf2737e652acd9cae2a4c9ffc16bfdaec6`。
- 随发行锁定 App Hub：`ba36df0505e198f998201af312ff5184df98cae9`，不是旧参考 `6741dea`。
- Makepad base：`32d6415fb7476345ad36ee4f98d6f844d1f07fd2`；combined tree：`6c080f31adb899611e6ebe132ccfa2eead06cf9b`（官方 receipt 记录）。
- Octoscript-Makepad：`33dea2f1f3ad3f1346a219aa8cf6e91b31361e23`，见固定 `native-runtime.lock.json`；额外补丁清单见 `runtime-patches.lock.json`。本轮未构建，不声称验证了本机编译工具链。
- 内核：receipt 记录 `b0759a57719fd35b3a2da1c5d969bc67538ed516` / `2.0.3-rc.13`；二进制单独校验。
- 实际入口：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，只读复用；不是旧 card-host。

|对象|本轮 SHA-256|核对|
|---|---|---|
|官方 app.zip|`ac1ab66848769e5f92e6b56968b73f03c77568b58277415da9a1c1e86b119290`|与现存官方 receipt 一致|
|解压 launcher|`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`|与 receipt validation 一致|
|解压 kernel|`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`|与 receipt kernel 一致|

证据：`results/binary-verification.json`、`source/INDEX.json`、`source/{shell,hub}-tree.json`。本轮没有重新下载发行 ZIP；其哈希链基于 r3 留存的官方 receipt 和本轮读取的官方页面。旧 `runtime/native-build/.../card-host` 的来源仍限历史主张，不能据项目 HEAD 或版本字符串认证，更不能代替目标 Shell。

## 3. D8 更正：本地安装确有实现，不要求 Cargo 重写

**撤回 r3 “第三方 Splash bundle 不可加载”“AppHub 最终转成 Cargo crate”“需补 Cargo.toml”以及“重写为 Cargo crate”的路线结论。** 用户已经选择本地安装方向，不再要求用户重复选择公开发布或重写。

下列路径均相对 `runtime/optimization/2026-10-09/M0/r4/source/`，可由 `INDEX.json` 跳到固定官方 URL：

|入口|固定源码事实|本轮运行判定|
|---|---|---|
|dev `--apps` 注册表|Shell `crates/shell/src/octosense/catalog.rs`：`manifest`、`executable`、`source` 三选一；`source` 是名为 `makepad` 的源码源，不是 AppHub ID 或任意目录|源码已核对；r3 对该入口的拒绝不能推广到 AppHub|
|`executable`|同文件：直接二进制路径，可带 args，不允许同时指定 package/bin。它注册进程应用，不会把路径变成 `hub:<id>` 的安装授权|已查字段；r4 实际启动 BLOCKED。将旧 card-host 写入这里也不能证明同进程 model 服务已接通|
|本地目录镜像|Hub `crates/appstore/src/source.rs:76–143`：`Origin::Directory`；`OCTOSENSE_HUB` 不以 `http` 开头时解释为目录；`catalog_for` 读目录文件，`stage` 复制 `<dir>/<artifact>`|本地来源实现已证实；`file://` 不是此接口要求，使用绝对目录路径|
|catalog 信任|同文件 `CatalogChannel`：默认 `github-v2`，读 `catalog-v2.json`；显式 legacy 读 `catalog.json`，已经有 v2 的 library 禁止降级。`client.rs:218` 对 v2 验证证明、legacy 验证签名|本地目录不免验签、不自动接纳 unsigned catalog；本轮没有签名、改 anchor 或制造证明|
|`install_staged`|`app-hub/src/client.rs:421–473`：已接纳且新鲜 catalog → app/version/撤回状态 → bundle digest → 完整 manifest 一致 → 签名/策略/host API → 复制安装|不是 CLI 任意路径直装，也不是 Cargo 构建；本轮未执行到该函数|
|安装落点|`client.rs:19–32`：`<app-data-root>/.bundles/<id>/bundle`；应用可写区另在 `<root>/<id>`|更正旧版本 `<root>/<id>/bundle`，不能混用旧源码行号|
|UI 安装与恢复|`app-hub-app/src/catalog.rs:388–432`：真实 consent、复核 catalog、stage、对安装专用 root 调 `install_staged`、再 `publish_bundle`；后者是本地目录切换函数，不是公开 `hub publish` 命令|本轮未调用；这种安装更新恢复不等于业务任务四文件事务|
|业务运行|Shell `crates/shell/src/apps.rs` 的 `installed_card_apps`、`card_row`、`card_manifest_id`：`hub:<manifest-id>` 由已链接 `card` 模块托管，Splash 包保持原形态|同进程服务是运行前提；不自动授予身份、模型和文件权限|

唯一继续路线为：**官方 rc.1 → 隔离 HOME/app-data → 已验证的本地 catalog 镜像 → App Hub 原生安装 → `hub:octosense-repair` → 进程内 card 模块。** 不改交付形态，不启用公网服务，不转成独立壳。

本轮未取得包含**当前工作树 digest**且可由此宿主验证的 catalog。B 包的旧 digest 即便存在于其他目录，也不能授权安装不同的 v2 工作树。只把 bundle 复制到 `.bundles`、编辑缓存、使用 `--dev-grant-all` 或拿 unsigned `hub check` 当安装成功，都不能满足这条路线。本轮均未如此处理。

## 4. 隔离启动与安装实测尝试

可复现命令（从项目根执行）：

```sh
python3 -B runtime/optimization/2026-10-09/M0/r4/probe/isolated_launcher.py --launch
```

执行器生成纯净子进程环境，排除继承凭据；设置 HOME、CFFIXED_USER_HOME、OCTOSENSE_HOME、OCTOS_HOME、RINX_DATA_DIR、TMPDIR、XDG 目录、Metal 缓存、内核路径和本地镜像目录。只读复用发行二进制。先用 `sandbox-exec` 验证“仅允许 r4 文件写入、禁止外发网络”限制，再尝试启动；预检不通过立即停止，**没有无约束回退**。严格文件写边界是本轮实现选择的保护手段，不冒称用户指定必须使用 sandbox-exec。

实际返回：

```text
sandbox-exec: sandbox_apply: Operation not permitted
preflight exit_code = 71
wrapper exit_code = 2
host_started = false
install_staged_executed = false
```

证据：`logs/isolation-preflight.json`、`logs/local-install-attempt.json`、`probe/isolation.sb`、`probe/environment.json`。第一次隔离预检和写成可交接脚本后的复现均停在同一环境限制，不再重复。**这不是 catalog 解析失败、包不兼容或本地路径不可行的最小复现；这是无法在本执行环境执行严格隔离启动的最小复现。** 本地安装的成功/拒绝运行证据仍缺，不能写为已验证可安装或永久不可安装。

本轮没有 r4 原生截图、控件树、模型响应、安装回执、保存文件或重开读回。没有拿旧截图、浏览器、夹具模型或后端测试填补。

## 5. 能力与唯一任务事实源裁决

|能力|当前依据与风险|r4 状态 / 下一项具体核验|
|---|---|---|
|原生工作台、中文、列表、详情、滚动、命名刷新|业务脚本未改；r1/r2 的 DesignInput 和 r3 的 Notes 是不同宿主/应用的历史证据|BLOCKED；业务包安装后用真实表单输入中文，滚动后操作、选中任务与命名控件回读，关闭重开|
|重复函数/调用兼容|去掉注释/字符串后 80 个 fn 无同名重复；18 处 isReporter/isReporterMe 调用的词法参数数目匹配。tick 注释不能当第二个定义|静态检查 PASS，启动兼容 NOT_RUN；没有据此改正式业务文件|
|模型成功及不可用|manifest 只有 storage；本轮无获授权的隔离 provider 配置；r3 profile_unresolved 不是 r4 证据|BLOCKED；先安装独立权限探针，再验证真实模型响应及拒绝/服务缺失；不配置计费、不用假模型|
|两个可信业务主体|main.splash 的 `STATE.actor`、USERS 为本地演示选择。rc.1 app_storage/lifecycle.rs 存在账户绑定/登出/存储分区代码，但不是维修项目认证|BLOCKED；需要两个经宿主真实认证的不同 subject，服务端/宿主可信项目映射、伪造 actor 拒绝、退出撤权与跨主体读取拒绝。两份 HOME、两个 peer 或 consent 不算两个人|
|真实文件选择/保存/重开/读字节|当前 addEvidence 仍含 `demo:true, ready:false, sha:""`。所读 platform_services 文档的设备授权不提供文件 picker；此文档不覆盖所有潜在文件 API|BLOCKED；安装探针后先查询真实 runtime API，再完成 picker 成功/取消、字节摘要、权限与重开，不能宣称整个 rc.1 永远无 picker|
|任务一致性及恢复|当前四个 save 函数分别覆盖文件；安装器的原子发布是另一层。一次 fs.write 或旧 card-host 重开不能证明任务/预约/回执/事件一致|BLOCKED；必须在目标沙箱核验写失败、配额、部分写、原子替换/持久化提交、重启恢复、单写者及跨实例竞争原语|
|时钟|业务 `nowMs()` 用 `time_now()`；Hub catalog freshness 用 SystemTime（remote.rs），Glance route TTL 用 Instant|BLOCKED；这些是不同用途，不能据 catalog 时钟判定业务 epoch/可信时间。需运行采样、重启、时钟回拨和过期确认拒绝|
|提醒/任务跳回|r3 只证明内置 reminders 注册。固定 glance_routes.rs 有按 app 绑定、一次性、120 秒 TTL 的内存路由|BLOCKED；需 due_at 持久化、重复触发去重、改约撤旧提醒、重启恢复与打开同 task_id。前台检查不等于宿主退出后唤醒；后台能力未测，不从验收中删除|

任务事实源继续优先考虑**宿主本地隔离存储的一个版本化任务库**，UI 缓存、模型对话和 Glance 只读投影；旧 Python/SQLite 不与它双主写入。当前四文件实现不获可靠性背书，路线仍是候选，不能据此放行 M2。

本地存储最小可审阅方案：命令边界单写者，任务/预约/事件/回执同一提交记录，稳定动作键，明确成功/失败/结果未知；若宿主确有原子替换与持久化原语，可验证写新快照→持久化→原子切换→回读及崩溃恢复。**原语尚未实测，以上不是已实现方案**。若目标沙箱只提供非原子覆盖且无锁/事务，需提交宿主原子存储服务的最小扩展方案（含接口、并发和恢复测试）供用户审阅；本轮不修改宿主、不部署包外服务、不降低验收。

## 6. D7 重标及完整映射

编号以 `docs/build-loop/ACCEPTANCE.json` 的 title 和 `15_BUILD_VERIFY_LOOP.md` 的 L0 定义为当前台账语义；T/U 按 05/10 原文。`14_COURSE2_LATEST_GUIDE_REVIEW.md` 同名 G0 编号有另一组描述，只作为补充要求，不能覆盖 15/台账的 G0-B/C/E。r3 错挂编号的 PASS/PARTIAL/n/a 全部撤回；旧 Notes 能力事实保留为历史材料，不能成为这些条目的 PASS。

|编号|原定义（摘要）|r4 目标 Shell 判定|
|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|BLOCKED：来源校验完成，目标启动未完成|
|G0-B|真实可信身份、授权与独立会话|BLOCKED|
|G0-C|唯一事实源、原子一致性、并发与恢复|BLOCKED；历史后端证据不继承|
|G0-D|真实附件写入、回读、归属及失败恢复|BLOCKED|
|G0-E|系统助手实际调用与关闭/拒绝/失败|BLOCKED|
|G0-F|提醒恢复、去重与官方任务意图视图路线|BLOCKED；不是 n/a|
|T28|原生打开同 task_id、操作并回读、重开状态保留|BLOCKED；撤回“中文表单 PASS”|
|T29|grant 关闭/退出/到期后不能调用，共享卡不继承发送者授权|BLOCKED；不是“多端一致”|
|T32|配对码过期/重复消费/poll_secret 拒绝，审批绑定用户，脚本拿不到 token|BLOCKED；不是“共享任务”。以后替换技术步骤须保留语义并显式版本化|
|U09|1280×800及窄窗/放大后动作和错误不裁切覆盖|BLOCKED；未测这组尺寸，撤回“滚动 PASS”|
|U11|真实宿主滚动、输入、面板稳定，动效不阻塞，无假进度|BLOCKED；不是“AI 报修”|
|P02|完整源码和依赖版本、干净环境启动/构建说明|BLOCKED；来源/步骤部分已补，干净启动未完成，不是“提醒恢复”|

完整 G0-A–F / T01–T38 / U01–U12 / P01–P08 共 **64 项**逐项映射见 `results/ACCEPTANCE_MAPPING.md` 与 `acceptance-mapping.json`，包含原始 title、责任模块、历史 revision/evidence、r4 状态；已检查集合完整且每项有模块。当前旧台账实际有 **65 条**，额外 `L8-DV2` 已单独保留到 `additional-ledger-entries.json`，不删掉也不混入 64 项范围。历史台账状态全部保留原样，**未重写 ACCEPTANCE.json**。非本轮范围均 NOT_RUN；外部 P06/P07/P08 没有新发布或回执判定。

## 7. 本轮测试表与硬验收

|检查|输入与步骤|预期|实际|结论|证据（相对 r4）|
|---|---|---|---|---|---|
|候选现场保留|快照→最终逐文件复算|只发生授权的本轮元数据变化|见 preservation.json，正式业务字节未改|PASS（文件保留检查）|snapshot/、results/preservation.json|
|B 包定位|ZIP 12 文件对照 git show HEAD|旧包与工作树分离|12 文件匹配提交版本|PASS（归档比对）|results/B-package.json|
|官方二进制|复算 ZIP、launcher、kernel|匹配 receipt|三者一致|PASS（来源校验）|results/binary-verification.json|
|固定源码|GitHub 15 文件与官方 Git tree 对照|相同 blob SHA|15/15 匹配|PASS（源码校验）|source/INDEX.json|
|D7 语义及覆盖|原定义比对、64 ID 集合、责任模块|无错挂/漏项|64 项映射完整，原生无新 PASS|PASS（文档自检，待 Review）|results/acceptance-mapping.json|
|D8 路线|核对 directory、install_staged、card、executable|纠正 Cargo 推论|本地目录实现存在，信任前提仍在|PASS（源码结论更正）；安装 BLOCKED|source/INDEX.json、本报告 §3|
|静态守卫回归|去注释后重复定义及两个守卫调用参数|无重复/错参|80 fn、18 处目标调用匹配|PASS（词法检查）|results/static-check.json|
|真实桌面操作|隔离预检→目标启动|原生窗口可操作|预检 exit 71，目标未启动|BLOCKED|logs/local-install-attempt.json|
|本地 install_staged|本地可信 catalog→原生安装→回读|原形态包安装并运行|未执行，缺隔离执行条件及当前包可信 catalog|BLOCKED|logs/local-install-attempt.json|
|权威状态与回执|原生动作后回读|同一任务/回执真实落盘|未执行|BLOCKED|logs/local-install-attempt.json|
|模型/文件/可信身份/存储错误|目标宿主最小探针|正向及失败证据|未执行；不挪用旧证据|BLOCKED|本报告 §5|
|失败与重试|隔离设置失败复现|失败立即停止，不启动无约束宿主|host_started=false|PASS（启动器失败处理）；应用恢复未测|logs/isolation-preflight.json、local-install-attempt.json|
|重启恢复|原生关闭重开、中文与文件读回|本轮真实回读|未执行|BLOCKED|本报告 §5|
|受影响先前模块|M0 无前置；正式业务未改|不迁移旧 PASS|仅静态调用与文件回归，无后端重跑|NOT_RUN（原生回归）|results/static-check.json|

硬验收 1：候选可定位、来源明确，但目标真实启动 **BLOCKED**。硬验收 2：四类最小运行证据 **BLOCKED**。硬验收 3：中文表单与滚动后操作 **BLOCKED**。硬验收 4：r4 写入范围与现场保留检查完成，旧数据不改写。硬验收 5：安装、可信身份和可靠存储未实证，**BLOCKED**。实现方不自行写 PASS 或“带条件通过”。

## 尚未完成

1. **R4-B01 / 环境**：当前执行沙箱不允许叠加宿主写隔离；不能保证无约束启动满足用户文件边界，因此停止。解阻需要能执行相同限制的本地执行环境，或另有经验证且不写项目外的宿主运行手段；不是要求放宽数据边界。
2. **R4-B02 / 本地可信 catalog**：需要一份已签名/已证明且含当前候选 digest 的离线 catalog 与对应 artifact。默认 v2 或显式 legacy 必须使用与之匹配的可信材料。本轮禁止 publish/签名/listing，故没有创建目录发布项、密钥或证明。若只有旧 B 包被接纳，需明确只测旧 B 安装，不冒充 v2；若无现成可信材料，下一轮只能先审阅离线测试 catalog 的授权方案，不能本轮执行。
3. **R4-B03 / 模型**：没有本轮获授权的隔离 provider 配置/真实请求，包也只申请 storage；不从个人 HOME 复制配置，不能把模型服务注册当成功。
4. **R4-B04 / 业务身份**：现有 role/actor 不是可信双主体；需明确宿主账户如何形成可信 subject 和项目授权。宿主 consent 不能解除该阻断。
5. **R4-B05 / 文件、恢复、提醒**：真实 picker、字节回读、业务原子性/锁/失败恢复、可靠时钟及退出后唤醒仍未执行；不删除 T22/T23/T28/T29/T32/U09/U11 等要求。

替代方案只停留在可审阅设计：优先取得现成可信本地镜像并恢复严格隔离执行；必要时提出只作用于测试目录的离线签名 catalog 方案，但本轮禁止事项保持；若账户/事务原语仍不满足，再分别提出最小宿主适配服务及验证合同。没有部署公网、改宿主或重写业务包。

## 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r4/CANDIDATE.json`。
- 快照：`snapshot/`；固定官方源码及出处：`source/INDEX.json`；启动阻断：`logs/local-install-attempt.json`；真实桌面截图/安装回执/业务回读：**本轮没有**。
- 可复算审计：`python3 -B runtime/optimization/2026-10-09/M0/r4/probe/audit.py`；只检查清单/静态源码/映射/保留，不执行应用测试。运行过的脚本开发错误与纠正记录见 `logs/execution-notes.md`。
- `GATES.json` 的 M0 更新为候选 r4、状态 BLOCKED；r3 Review 保留为该旧候选历史，不把它挂成 r4 已审查结论。M1–M7 与 external_delivery 不变。
- D7 文档修复、D8 结论撤回和源码查证完成；D8 要求的本地安装运行验证尚未完成，提交独立 Review 时不得整体声称已关闭。

**编码方交接完成，待独立 Review；不进入后续模块。**
