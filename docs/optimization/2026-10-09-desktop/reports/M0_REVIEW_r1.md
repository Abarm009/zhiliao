# M0 独立 Review r1 — 桌面运行基线与能力裁决

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI，主会话），2026-10-09 20:40 CST（Asia/Shanghai）
- candidate_id / 被审 HEAD 和内容清单：
  - 被审候选：`M0-r1-worktree`（GATES.json 中 M0 登记的交接候选；本地仅此一版实现报告 `M0_IMPLEMENTATION_r1.md`，无 r2+，版本明确）
  - HEAD：`8d730569546cb57310944bb299695134df773b9d`（本仓库 main）
  - 独立复测哈希（审查开始与结束各取一次，一致）：
    - `app/bundle/main.splash` sha256 `fb7527ad…67f68`（1311 行，55,771 字节）— 与报告一致
    - `app/bundle/manifest.json` sha256 `2ec1d0ca…f29fd`，内含 stamp `44743e24…`（M0-start 值）— 与报告一致
    - `card-host` sha256 `bebded3d…e17b`（25,186,160 字节，Mach-O arm64，mtime 2026-10-01 11:30）— 与报告一致
    - `hub` sha256 `f211e53a…494f` — 与报告一致
  - B 包基线：HEAD 中 manifest stamp `e5b477c7…`（`git show HEAD:app/bundle/manifest.json` 实测），与当前工作树 `44743e24…` 明确区分；`main.splash.v1.bak`（46,640 字节）为 B 版对应文件。**未发现 B 包与 v2 工作树混记**：报告与快照把两者分开陈述。
- 审查开始/结束时快照是否一致：一致（`git status --short` 前后均为 8 项修改 + 9 组未跟踪；bundle 两文件哈希不变；无 card-host 残留进程）
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r1.md`
- 已核对前置模块 PASS 与受影响回归：M0 为链首，无前置模块。既有 `docs/build-loop/ACCEPTANCE.json` 现状实测：G0-A PASS / G0-C PASS（后端形态）/ G0-B、G0-D、G0-E、G0-F、T32、U09、U11 NOT_RUN / T28、T29 FAIL / P02 PASS — 与报告 §映射 的引用一致。本轮不改动该台账（见"判定"）。
- 实际环境 / 模型路由 / 宿主：macOS Apple Silicon 本机；本审查会话未调用任何模型 provider；宿主 = `card-host`（上述哈希），`MAKEPAD_HIDE_WINDOWS=1 MAKEPAD_REMOTE=8790/8791` 驱动。
- 已阅读范围：AGENTS.md、00/01/02/M0 模块文件、04 模板、M0_IMPLEMENTATION_r1.md、candidate_snapshot.txt、r1 全部 probes/evidence 目录清单、boot.log、ACCEPTANCE.json 相关条目、SOURCES.md、宿主源码（card-host host.rs、app-policy manifest.rs/policy.rs、makepad splash_host.rs/splash_storage.rs/splash.rs/text_input.rs、octoscript-widgets design.rs、OctoSense-Shell crates/shell/src/apps.rs 与 AGENTS.md）。
- 已运行范围（全部为审查方独立重跑，隔离于 `runtime/optimization/2026-10-09/M0/review-r1/`；bundle 为 **副本**，原 `app/bundle/` 未动）：
  1. 失败注入：不带 `--stamp` 启动当前 worktree bundle 副本 → 实测拒绝：`refused: bundle digest aa654664… does not match the manifest's 44743e24…`（与报告吻合，且独立复现了"实测摘要 = aa654664…"）。
  2. `--stamp` 启动 → admit：`capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none`；`[SPLASH] eval: 55771 bytes`；`/g?raw=1` 抓取真实 PNG（`review-r1/evidence-initial.png`）。
  3. 点击 `＋ 新建报修草稿` → `提交 OPEN`：隔离 app-data 的 `tasks.json` 落盘中文 `东侧会议室空调不制冷，希望今天下午处理`、状态 OPEN（`review-r1/evidence-after-confirm.png`）。
  4. 身份探针：`header_actor` 实测为 chip 切换（报修人一/二、技工甲/乙、经理丙），头部自述 `演示身份 · 非登录认证`；切到 `u-reporter-2`（prj-B）后 `visible_count=0 项`、`task_status=无可见任务（u-reporter-2）` — **身份来源确为脚本内 `STATE.actor`，不是宿主注入**；脚本级可见性隔离成立。
  5. 重启恢复：`/quit` 后不带 `--stamp` 重启同一 app-data → admit 成功，`u-reporter-2` 身份与 0 条可见视图从 state.json 恢复。
  6. 模型探针（自建最小探针包 `probe-bundle`，仅 storage capability）：`host.request("model.complete", …)` **并非静默悬挂** — card-host 显式回 `is_ok=false, err=this app was not granted "model", which "model.complete" needs`；manifest 增加 `"model"` capability 后 admit 显示 `{"model","storage"}`，再调回 `is_ok=false, err=no service answers "model" on this device`。**两级授权门存在且工作**；该二进制无 model 服务，BLOCKED 结论成立但机理与报告描述不同（见缺陷 D2）。
  7. 存储错误探针：脚本写 4 MiB 文件 → 宿主侧 trap `file too large`（splash_storage.rs:301，MAX_FILE_BYTES=1 MiB），文件未产生，错误进入宿主日志 — **不是静默吞掉**（见缺陷 D4）。
  8. 中文原生表单探针：注册词汇表中存在 `DesignInput`（= TextInput，design.rs:240）；探针包中 `/k?t=` 键入中文 `审查探针：中文输入保留` → `fs.write` 落盘 → 重启 → `fs.read` 回读逐字一致（`review-r1/evidence-probe-input.png`）。
  9. 滚动探针：`/m?k=scroll` 路由存在且生效（dy 正号向下）；ScrollYView 内 15 行内容真实滚动，滚动后底部按钮可点击并触发回调（`review-r1/evidence-probe-scroll.png`）— 报告"滚动不可测"的说法不成立（见缺陷 D3）。
  10. 重复函数探针：`fn dup(a,b)` 后再定义 `fn dup(a)`，调用 `dup(1,2)` 实测返回 `one-arg`、无 trap — **后定义静默胜出、多余实参被静默忽略**。main.splash 中 line 113（2 参）被 line 1020（1 参）覆盖属实，且 433/496/503/529/592/632/698/724/770/778/797/822 等 14 处业务守卫调用点实际执行的是 1 参版本（当前语义恰好等价，因为调用点均传 `getMe()`，但这是地雷不是设计）。
- 未运行范围及原因：
  - OctoSense-Shell：`runtime/native-build/OctoSense-Shell/` 无 `.git`、无 `target/`、无二进制，本机不可启动（实测确认），不冒充。
  - 真实 LLM 响应：无 provider、无模型服务，且未获授权配置计费渠道 — NOT_RUN。
  - 后台/锁屏提醒：宿主无 scheduler/notification API，最小化窗口场景不可经远程面驱动 — NOT_RUN（前台 tick 已确认）。
  - 存储并发/崩溃中途恢复（写到一半 kill）：未做断电级注入，记录为未验证边界。
  - U09（1280×800/响应式）：仅 412×892 与 412×300 探针 — NOT_RUN。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 硬验收1 候选可定位/宿主真实启动/二进制来源明确 | 复算全部哈希；无 `--stamp` 启动（应拒）与 `--stamp` 启动（应 admit）各一次 | 拒绝路径与 admit 均可复现；来源不以版本字符串替代 | 全部复现；二进制以 sha256+mtime+SOURCES.md 锁定，但报告含一句伪造式验证（缺陷 D1） | PASS（附 D1 修复要求） | `review-r1/logs/refused-no-stamp.log`、`boot-stamped.log` |
| 硬验收2 模型/文件/身份/存储最小证据或 BLOCKED | 探针 6/4/7/3/5 | 具备的给证据，不具备的记 BLOCKED | 文件与存储恢复有证据；模型、宿主身份、文件 picker、OS 提醒实测不可达并记 BLOCKED；报告未把候选方案记为 PASS | PASS | `probe*-boot.log`、tasks.json、截图 |
| 硬验收3 可读写最小原生表单保留中文/滚动后可操作 | 探针 8/9（DesignInput 中文 round-trip + 滚动后点击） | 原生控件真实输入中文并回读；滚动后控件可点 | **审查方探针证明该能力成立**；但当前业务 bundle 未挂任何输入控件，报告自身未做此探针（缺陷 D5） | PASS（能力层面，由审查证据补足；业务表单落地属 M1/M3） | `evidence-probe-input.png`、`evidence-probe-scroll.png` |
| 硬验收4 隔离数据/原数据保留 | 审查全程只用 review-r1 副本与隔离 app-data；结束后复算 bundle 哈希与 git status | 原数据与未提交改动完整 | 一致；`runtime/build-loop/`、`runtime/octosense.db` 等未触碰 | PASS | 本报告哈希记录 |
| 硬验收5 路线支撑后续硬约束/用户架构选择未决不放行 | 对照报告 §路线建议 与实测能力矩阵 | 路线足以支撑 M2/M3/M5/M6 硬约束 | **不满足**：模型（M3）、宿主身份（M2）、OS 提醒（M6）在 card-host@6741dea 上无路径，路线 A/C/D 需用户裁决；实现方亦声明不放行 | **BLOCKED** | 探针 6、Shell apps.rs、报告 §路线建议 |
| G0-A 固定版本原生构建与真实启动 | 重跑启动 | PASS 沿用 | 复现 admit+渲染 | PASS（原生形态复核） | `boot-stamped.log` |
| G0-B 可信身份 | 探针 4 | 身份非下拉框 | 实测即下拉 chip（state.actor），宿主无注入；维持 NOT_RUN 语义 | 维持 BLOCKED/NOT_RUN，不升级 | snap `header_actor` |
| G0-C 唯一事实源/原子/并发/恢复 | 重启恢复 + 源码审读 splash_storage.rs | 恢复有证据；原子性如实记录 | 重启读回 PASS；`fs.write`=`std::fs::write` 单次覆盖、非事务；并发未测 | 部分证据，原子/并发为未验证边界 | splash_storage.rs:324 |
| G0-D 真实附件 | 查 picker/附件路径 | 不可冒充 | 81 控件词汇无 picker；`addEvidence` 仍为 demo 占位 | 维持 NOT_RUN/BLOCKED | main.splash 全文 grep |
| G0-E 系统助手/模型 | 探针 6 | 不得把缺失说成支持 | 两级显式拒绝实测；BLOCKED 成立 | 维持 BLOCKED（机理更正见 D2） | probe4 日志 |
| G0-F 提醒/跳回 | 源码审读 splash.rs:405 | 区分前台/后台 | `tick_timer=cx.start_interval(1.0)` 前台 UI 定时器；无 OS 级 API | 维持 BLOCKED（前台 only） | splash.rs、apps.rs |
| T28/T29 grant 关闭/全链路 | 探针 4/6 | 维持 FAIL 不升级 | 无 host tag/grant/pair 路径；维持 FAIL | 一致 | splash_host.rs:29 |
| T32 配对码/token | 查 manifest/host | 不冒充 | 无 pair 服务；维持 NOT_RUN | 一致 | policy.rs |
| U09/U11 布局与滚动 | 探针 9 | 滚动实测 | 滚动实际可用（更正报告保留意见）；U09 响应式未测 | U11 滚动子项有正向证据；U09 维持 NOT_RUN | evidence-probe-scroll.png |
| P02 完整源码+依赖+启动说明 | 复核 SOURCES.md 与可重复启动 | 可重复 | 启动可重复；但二进制源码树 `.git` 缺失（见 D1），"6741dea pin"当前不可从树内复核 | PASS 附条件（D1 修复） | SOURCES.md §6-8 |

## 缺陷

- **D1（P2，必需修复·报告准确性）** — 文件：`reports/M0_IMPLEMENTATION_r1.md` §"目标宿主"（"其工作树 `git log` 最近提交为 `8d73056…`（=本仓库 HEAD）"）。触发：`cd runtime/native-build/OctoSense-App-Hub && git log`。预期：该树自身版本证据。实际：该树**没有 `.git`**（`ls -d .git` 不存在，`ls -la` 仅有 `.gitignore`），git 命令向上走进了本仓库，把 zhiliao 的 8d73056 误读为 App-Hub 的提交。SOURCES.md §1 声称"内含 .git，HEAD 已 pin 6741dea"当前亦不可从树内复核。影响：恰是 Review 指令第 1 条要防的"混版本"错误的变体；二进制来源实际只能由 sha256+mtime+历史文档主张支撑。最小修复：删除/更正该句，改写为"该树为无 .git 的源码快照，版本仅可由 Cargo.lock 与历史 SOURCES.md 主张，二进制 sha256 为准"。
- **D2（P3，建议·报告机理更正）** — 报告 §"应用运行模型"称未识别请求"静默无响应（simply never resolves）"。实测：card-host 显式回 `is_ok=false`，且区分"未授权"与"无服务"两级错误（证据：probe2/probe4）。影响：机理更正对 M2 有利（显式失败可对账），报告表述会误导路线设计。最小修复：更正为实测的两级错误语义。
- **D3（P3，建议·报告机理更正）** — 报告测试表/U11 行称滚动因"无 /scroll 路由"不可测。实测：`/m?k=scroll` 存在，ScrollYView 真实滚动且滚动后控件可点击。影响：U11 的滚动子项其实已有正向证据，报告的保留意见过度保守；同时报告 §"桌面 UI"称"当前 bundle 改用 detail_block := ScrollYView"与脚本头注释"取消 ScrollYView"并存（两者分别指详情区与按钮区，需写清）。最小修复：更正表述并纳入本次滚动证据。
- **D4（P3，建议·报告机理更正）** — 报告称"fs.write 错误返回被脚本吞掉"。实测：超配额/超限写入在宿主侧 trap（`file too large` 进日志，handler 中止），并非静默；真正的风险是 main.splash 的 `save*` 不检查返回值且 trap 会中止命令处理器的剩余步骤（可能留下部分写入）。最小修复：按"trap 中止 + 部分写入风险"重写该段，并把失败注入测试留给 M2/M5。
- **D5（P2，必需修复·证据缺口已补但需入册）** — 硬验收 3 的最小原生表单探针，实现方未做（只测了业务 bundle 并据此记 PARTIAL）。审查方已用独立探针补足（DesignInput 中文 round-trip + 滚动后点击均 PASS）。最小修复：r2 报告将审查探针证据并入实施证据链，并把"业务 bundle 无输入控件"明确划入 M1/M3 范围而非 M0 缺口。
- **D6（P1，必需·转入 M1 前置）** — `app/bundle/main.splash:113` 与 `:1020` 重复定义 `fn isReporter`；实测后定义胜出、2 参调用的多余实参被静默忽略，14 处业务守卫实际执行 1 参版本。当前语义巧合等价（调用点均传 `getMe()`），但任何未来以第三方为主体的调用都会静默错判。M0 文件责任不允许本次修业务代码；**M1 启动前必须消除重复定义**，此项已登记为 M0→M1 的携带 blocker。

无需变更的发现不编造缺陷：候选清单、哈希、B/v2 区分、隔离边界、agent none、16 MiB 配额、prompts false、Shell 裸目录不可启动等报告主张，经独立复测均属实。

## 判定

- 最终结论：**BLOCKED**
- 本次结论的精确范围：仅 M0「桌面运行基线与能力裁决」，候选 `M0-r1-worktree` + `card-host`@sha256 `bebded3d…`；不构成对 B 包、后端台账或任何后续模块的判定。
- 必修项：
  1. （用户裁决）宿主路线三选一：A 固定 card-host 并书面处理 model/身份/提醒类既有验收缺口（注意 02 规则禁止删缺口，A 实际不满足 M2/M3/M6 硬约束）；C 授权联网拉取并离线构建 OctoSense-Shell@a5d847a（唯一自带 ai-host/`model.complete`/kernel 身份服务的路径）；D 扩展 card-host 的 mini 模型/身份服务（须先书面提案并评估 Hub 收录风险）。裁决前 M0 不放行。
  2. r2 报告修复 D1（必需）、D5 证据入册（必需）；D2/D3/D4 表述更正（建议同轮完成）。
  3. D6 作为 M1 的入场前置条件登记，不属 M0 修复范围。
- 阻塞与未测项：模型服务（宿主无）、宿主身份注入（无）、OS 级提醒/跳回（无 API）、文件 picker（无该 widget）、存储并发与崩溃中途恢复（未做断电注入）、U09 响应式（未测）、Shell 启动（无二进制）。
- 受影响先前模块是否已复验：无前置模块。既有 ACCEPTANCE.json 的 G0/T/U/P 条目状态与报告引用一致，**本轮不改动**；本审查的新证据（model 授权门、DesignInput、滚动）均为原生形态正向/负向事实，不改变历史后端结论的适用形态，故无需重写台账。
- 门禁与原台账更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=BLOCKED、review_report、reviewed_at、blockers 更新）；`docs/build-loop/ACCEPTANCE.json` 不动，历史来源保留。
- 是否允许进入下一模块：**否**。M1 依赖 M0 的宿主路线裁决。
- 若 BLOCKED，留在本模块的解阻指令：
  1. 请用户就宿主路线 A/C/D 作出书面裁决（涉及网络授权、构建时间、交付形态变化，按 02 §1 须用户决定）。
  2. 实现方出 r2：修复 D1、并入审查探针证据（`runtime/optimization/2026-10-09/M0/review-r1/` 可整体引用）、更正 D2–D4 表述；探针仍只放隔离目录，不动业务代码。
  3. 若用户选 C：补 Shell 构建记录（源码 SHA、lockfile、二进制哈希、启动方法）后重交 M0 审查；若选 A：需用户同时书面确认 M2/M3/M6 相关既有验收项的处置方式（降级须明示，不得静默）。
