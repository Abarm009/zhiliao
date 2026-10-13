# M0 独立 Review r4 — D7/D8 修复与本地安装路线裁决复核

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-09 22:35 CST（Asia/Shanghai）
- candidate_id：`M0-r4-worktree`；base：`M0-r3-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`（已逐项核实，与 r4 CANDIDATE 一致）
- 审查开始/结束时快照：开始时 git status 17 项未提交/未跟踪改动（8 修改 + 9 未跟踪），结束后 r4 隔离脚本本身额外写了 `runtime/optimization/2026-10-09/M0/r4/logs/launcher.log`（9479 B）和 `local-install-attempt.json`（被审查方操作覆写为 exit 0/host_started=true 记录）。其余文件未触动。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r4.md`
- 已核对前置模块 PASS 与受影响回归：M0 无前置模块；r3 Review 维持 BLOCKED；r4 在 r3 基础上修复 D7/D8。
- 实际环境 / 模型路由 / 宿主：darwin（Darwin 25.6.0）、本机 sandbox-exec / r3 留存的官方 launcher 二进制（`r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense` 223,391,280 B，SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，与官方 receipt 一致）；octos-kernel 126,117,168 B，SHA-256 `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。当前工具不具备主会话 Router 活动查询/切换接口，**未确认**。
- 已阅读范围：AGENTS.md、`docs/optimization/2026-10-09-desktop/00–04`、`GATES.json`、`M0_桌面运行基线与能力裁决.md`；r1–r4 IMPLEMENTATION 报告、r1–r3 REVIEW 报告；r4 CANDIDATE.json 与全部 results/、source/、snapshot/、logs/、probe/；fixed GitHub source 抽样 3 项核实；当前 git 工作树与 snapshot 比对。
- 已运行范围：
  - `git rev-parse HEAD` 与 r4 CANDIDATE 一致；
  - `git status --porcelain` 与 `snapshot/status-before.txt` 一致（17 项）；
  - 重新复算 `app/bundle/main.splash`、`app/bundle/manifest.json` SHA-256，与 r4 snapshot 与 r4 CANDIDATE 逐字节一致；
  - 直接复算 `r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`，与 r4 binary-verification.json 一致；
  - 直接执行 `sandbox-exec -f r4/probe/isolation.sb /usr/bin/true`，exit 0、stderr 空；
  - 直接执行 `sandbox-exec -f r4/probe/isolation.sb /bin/echo hi`，exit 0、stdout `hi`；
  - 执行 `python3 -B r4/probe/isolated_launcher.py`（无 `--launch`），preflight exit 0；
  - 执行 `python3 -B r4/probe/isolated_launcher.py --launch`，preflight exit 0，host_started=true，host_exit_code=0，写出 `r4/logs/launcher.log`（9479 B，55 行）；
  - 抽样核实 GitHub blob：OctoSense `runtime-patches.lock.json`、`native-runtime.lock.json`、`crates/appstore/src/source.rs`（git_blob_sha `07a1221dbaacb1008045669efb0035f0a24a6a38`）逐项匹配 r4 INDEX.json。
- 未运行范围及原因：
  - install_staged 实测：r4 sandbox 启动脚本命令通过 `--apps` 指向 `probe/empty-dev-apps.json`（内容 `[]`），未注入 octosense-repair bundle，也未配置本地 catalog，所以 install_staged 未触发。`OCTOSENSE_HUB=runtime/optimization/2026-10-09/M0/r4/local-mirror`（空目录，无 catalog）。
  - 业务 bundle 原生操作、中文表单输入、滚动/控件、关闭重开：未执行；脚本仅 15 秒诊断性启动即被 terminate。
  - 真实模型调用：launcher.log 显示 llm profile 路径 `r4/home/.octosense/octos-home/.octos` 已读取但未配置；模型 service 仅"已注册"一行（`ai-host/src/lib.rs:429 - model: service registered (one-shot calls; granted apps only)`），未发起任何请求。
  - 可信双主体：未实测；launcher.log 仅含默认 Consent 注册。
  - 真实文件 picker、原子存储恢复、提醒/任务跳回：未执行。
  - 模型路由 → 切回应话：工具能力外，不在本轮。

## 必需检查

| 检查 | 独立操作步骤 | 期望 | 实际 | 结果 | 证据 |
|---|---|---|---|---|---|
| 候选定位 | git rev-parse HEAD + shasum 工作树 main.splash/manifest | 与 CANDIDATE 一致 | HEAD `8d73056…`、main.splash `8aa1022c…`（55781B）、manifest `e202519…`（249B）逐一匹配 | PASS | git rev-parse / shasum 输出 |
| B 包 vs 工作树分离 | snapshot/committed-B/main.splash 与工作树 main.splash 比对 | 不同 SHA | 提交版 `9551239ec9…`（46640B）vs 工作树 `8aa1022c…`（55781B） | PASS | snapshot/committed-B/app/bundle/main.splash / r4 CANDIDATE artifacts |
| 已提交 B ZIP 复算 | shasum -a 256 r4 CANDIDATE 标 1,544,808B / SHA-256 `6a58e27a…` | 一致 | 与 r4 binary-verification 报告交叉一致（r4 直接结果取自 r3 留存 receipt） | PASS（来源核验） | r4 results/binary-verification.json |
| 官方 launcher / kernel 哈希 | 复算 r3 路径 | 与 receipt 一致 | `3e127963…` / `a3e46a45…` 均匹配 receipt | PASS | 直接 shasum 输出 |
| 固定 GitHub source（抽样 3） | curl /repos/{org}/{repo}/git/blobs/{sha} → 解码 base64 → sha256 | 与 INDEX.json 字段匹配 | `df4b5d0…` → `83e3d3c6f9…`（9187B）、`9f35c44…` → `fef6fddb73…`（152B）、`07a1221d…` → `073cf9801a…`（8732B）三项一致 | PASS | source/INDEX.json / curl 响应 |
| D7 编号语义 | 比对 ACCEPTANCE_MAPPING.md 64 项 vs ACCEPTANCE.json title/05/10 原文 | 名称与定义对齐 | G0-A–F / T01–T38 / U01–U12 / P01–P08 64 项映射完整，r4 目标列全为 BLOCKED/NOT_RUN；旧台账原样保留 | PASS（文档自检） | r4 results/ACCEPTANCE_MAPPING.md、acceptance-mapping.json |
| D8 路线结论 | 比对 r4 §3 vs 官方 `catalog.rs`、`source.rs`、`client.rs`、`apps.rs`、`catalog.rs` | 区分 dev 注册表 / AppHub 安装 / card 进程内托管 | r4 报告 §3 逐项列举 `executable`、local directory `OCTOSENSE_HUB` 镜像、`install_staged`、`hub:octosense-repair`、`card` 模块进程内托管；撤回 r3 Cargo crate 结论 | PASS（路线结论） | r4 IMPLEMENTATION_r4.md §3 |
| 静态守卫回归 | r4 static-check.json | 无重复定义 / 守卫调用 arity 匹配 | 80 fn 无重复；18 处 isReporter(2)/isReporterMe(1) 词法 arity 匹配 | PASS（词法检查） | results/static-check.json |
| **隔离启动预检复现** | r4 isolation-preflight.json 写 exit 71 | 当前能否复现 | **不可复现**：直接 `sandbox-exec -f r4/probe/isolation.sb /usr/bin/true` exit 0 stderr 空；`/bin/echo hi` 正常输出 `hi`；isolated_launcher.py 预检 exit 0 | FAIL（r4 报告失真，见 D-R4-1） | 本次 sandbox 命令输出 |
| **隔离 --launch 启动宿主** | r4 声称 host_started=false | 当前能否真实启动 | **真实启动**：isolated_launcher.py --launch → host_started=true，host_exit_code=0，写 55 行 launcher.log，含 kernel ready / llm profile path / model service registered / contained apps Consent / modules linked 含 `card` / Splash eval 809B 渲染、PingFang SC 字体加载、apphub 进程内 client 1 启动 | FAIL（r4 报告失真，见 D-R4-1） | r4/logs/launcher.log（本次生成）、local-install-attempt.json |
| install_staged 实测 | 隔离环境下注入 octosense-repair bundle + catalog | 落点 `<id>/.bundles/<id>/bundle` | 未执行：`--apps` 指向空 `[]`，OCTOSENSE_HUB=`r4/local-mirror` 空目录无 catalog | BLOCKED（理由仍在，见 D-R4-3） | launcher.log L43 / r4/local-mirror 空目录 |
| 模型最小正向及不可用 | 隔离 host 调真模型 + 服务缺失响应 | 真实成功/真实拒绝 | 未发起任何调用；launcher.log L7 仅"llm: provider profile under ... .octos"路径读取，无 provider 配置（与 r3 `_main` 未配置同源） | BLOCKED | launcher.log L6–9 |
| 两个可信业务主体 | 隔离 host 启用两个真实 subject | 跨主体读拒 | 未实测 | BLOCKED | D-R4-4 |
| 真实文件选择/保存/重开/读字节 | 隔离 host 走真 picker | 字节一致 | 未实测 | BLOCKED | D-R4-5 |
| 任务一致性与恢复 | 隔离 host 写失败/部分写/原子替换/重启 | 恢复未在目标句未测 | 未实测 | BLOCKED | D-R4-5 |
| 可靠时钟/提醒/任务跳回 | 时钟回拨 / 退出后唤醒 | 拒绝过期 / 跨重启提醒 | 未实测；launcher.log L10 仅证 reminders 模块已链接 | BLOCKED | D-R4-5 |
| 失败与重试 | 隔离启动失败处理 | 失败立即停止 | r4 脚本"preflight failed → 不启动"分支实现到位；本次预检通过，脚本进入 `host_started=true` 并 15s 后正常回收 | PASS（失败处理实现到位） | isolated_launcher.py L34–52 |
| 重启恢复 | 隔离 host 关闭重开 | 任务/文件读回 | 未实测 | NOT_RUN | — |
| 受影响先前模块 | r3 BLOCKED → r4 D7/D8 修复 → 其它 | 不迁移旧 PASS | 仅静态调用 + 词法回归 + 文档映射修复，无后端 PASS 迁移；G0-C/T22 历史台账 PASS 未被改写为 r4 原生 PASS | PASS（受影响范围限定正确） | results/ACCEPTANCE_MAPPING.md / r4 §6 |
| 数据边界 | `--apps` / HOME / OCTOSENSE_HOME / TMPDIR / XDG 全部 r4 内 | 不写 `~/.octosense` 或项目外 | isolated_launcher.py 写入 `r4/home/.octosense` 内（受 sandbox 阻断仅 os error 1，未越界）；r4 期间未触项目外路径 | PASS | isolated_launcher.py / launcher.log L5、L35 |
| 业务文件零改动 | git diff / status | 工作树业务文件未改 | `app/bundle/main.splash`/`manifest.json` 未在本轮触；git status 17 项与 r4 status-before.txt 一致 | PASS | git status / snapshot/status-before.txt |

## 缺陷

- **D-R4-1（P2，必需修复·环境证据失真）** — 文件：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r4.md` L88–95、`runtime/optimization/2026-10-09/M0/r4/logs/isolation-preflight.json`（exit_code=71）、`logs/local-install-attempt.json`（exit_code=71）、`logs/execution-notes.md` L4 / L8。触发：审查方独立执行 `sandbox-exec -f r4/probe/isolation.sb /usr/bin/true` 返回 exit 0 stderr 空；`/bin/echo hi` 返回 `hi`；`isolated_launcher.py --launch` 返回 preflight exit 0、host_started=true、host_exit_code=0，并写出 55 行 launcher.log（`kernel ready`、`model: service registered`、`contained apps' service registered (Consent)`、`wm: modules linked: ["rinx", "terminal", "apphub", "card", "calculator", "clock", "notes", "reminders", "weather", "octoscode"]`、`[SPLASH] eval: 809 bytes ... animating=false tick=false`、`PingFang SC Regular/Semibold for English and Chinese`）。预期：报告"环境不允许隔离启动、宿主无法启动"。实际：**当前环境允许隔离启动并能真实拉起宿主 5 项服务和 10 个模块**。影响：r4 报告 R4-B01 的最强理由（"严格隔离启动预检实测 sandbox_apply: Operation not permitted（exit 71）"）在本环境不可复现，宿主 5 项服务注册 + 模块链接 + Splash 渲染均能跑出来；但 r4 没有尝试 `--launch`，把"环境阻断"作为 M0 不可行的首要依据，导致硬验收 1（目标桌面宿主能真实启动）在当前实际条件下已具备重新放行的空间。最小修复：在同一环境重跑 `isolated_launcher.py --launch`，把 `host_started=true`、launcher.log、apphub 进程内 client 1 启动如实写入 r5；按 launcher.log 重新确认能力范围：模型 profile 未配（`_main` 路径同 r3）→ 仍 BLOCKED；consent / card 进程内目标存在 → M1/M3 落地路径具体化；不要把已能跑的 sandbox 启动继续报为环境阻断。
- **D-R4-2（P2，必需修复·R5 候选必须先于实现方重试）** — 文件：`M0_IMPLEMENTATION_r4.md` §4。触发：D-R4-1 已证 r4 的 sandbox 启动证据可重出。预期：r5 在同一环境以同一脚本先跑 `--launch`、记录 host_started、捕获 launcher.log，再按 launcher.log 的实际能力结论回填硬验收。实际：r4 报告仅写预检失败结论，未跑 `--launch` 也没有 launcher.log 备份。影响：报告与现场不一致会向下误导 R5 实施与 M1/M3 选型。最小修复：r5 报告 §1 必须包含 launcher.log 关键行（`wm: modules linked` 与 `[SPLASH] eval` 两段）+ 同环境复跑 `isolated_launcher.py --launch` 得到的本地安装路径结论。
- **D-R4-3（P1，必需修复·本地 catalog 仍未具备）** — 文件：`M0_IMPLEMENTATION_r4.md` §3、§4、§5。触发：`runtime/optimization/2026-10-09/M0/r4/local-mirror/` 为空目录；launcher.log L43 `[SPLASH] eval: 809 bytes` 与工作树 `app/bundle/main.splash`（55781B）不一致——说明 `--apps` 注入的并非业务 bundle 而是空注册表触发的内置 splash。预期：路线成立需"一份已签名/已证明且含当前候选 digest 的离线 catalog 与对应 artifact"，让 `install_staged` 在隔离环境真实落盘 `<id>/.bundles/<id>/bundle`。实际：本轮禁止 publish/签名/listing，`local-mirror` 为空；`OCTOSENSE_HUB_CATALOG=github-v2` 走的是官方 catalog 通道且 sandbox `deny network-outbound`。影响：r3 D8 修复路径"本地目录镜像"逻辑已查实（`source.rs:76–143`），但端到端 install_staged 实证未完成；后续 M0/M1 落地前提仍缺一份 v2 catalog 在隔离目录下的真值。最小修复：用户授权生成"仅测试目录、仅当前 digest、仅隔离 sandbox 内有效"的离线签名 catalog；或按用户路线裁决改走"AppHub 公开发布"；不能在没有 catalog 的前提下声称本地安装路径已可行。
- **D-R4-4（P1，必需修复·可信双主体未实测）** — 文件：`M0_IMPLEMENTATION_r4.md` §5 表格行"两个可信业务主体"。触发：launcher.log L9 仅出现单一 `Consent` 默认 sheet（`octos: contained apps' service registered (Consent)`），无第二个 subject 注册。预期：两个经宿主真实认证的不同 subject，服务端/宿主可信项目映射、伪造 actor 拒绝、退出撤权、跨主体读拒。实际：本轮未启用第二个 subject；`main.splash` 的 `STATE.actor` / `USERS` 是脚本内演示选择（已多次写明）；launcher.log L34 `ai-host: apphub (i1g1) did not take its assistant service` + L35 `app storage: apphub: storage: Operation not permitted` 仅证明服务已注册但未完成 grant 落地。影响：M2/M3/M5 都建立在"宿主真实认证 subject 投影到项目授权"之上，M0 必须先行验证。最小修复：在隔离 sandbox 内启用第二个 subject（独立 CFFIXED_USER_HOME / OCTOSENSE_HOME），用两个独立 session 跨读拒、退出撤权验证。
- **D-R4-5（P1，必需修复·文件/原子恢复/提醒三类能力未实测）** — 文件：`M0_IMPLEMENTATION_r4.md` §5。触发：launcher.log L10 `wm: modules linked` 列出 `card` / `notes` / `reminders` / `clock`，但脚本 15 秒后即被 terminate，未触发 picker、原子写、提醒调度。预期：真 picker 选写、字节读回、原子替换/持久化、重启恢复、退出后唤醒。实际：未实测；同 r3 BLOCKED。影响：M2/M5/M6 直接依赖这三类能力的实证。最小修复：r5 在 sandbox `--apps` 注入业务 bundle 后跑至少 30 秒诊断窗口，验证 picker 调用、字节一致、提醒 due_at 持久化与跨进程恢复。

## 判定

- 最终结论：**BLOCKED**
- 本次结论的精确范围：M0 r4 候选（`M0-r4-worktree`，HEAD `8d73056…`）的硬验收 1–5 在审查方环境下部分有条件满足（1：当前环境允许隔离启动并能拉起宿主 5 服务/10 模块；4：数据边界符合）；其余硬验收（2：模型/文件/身份/存储最小证据；3：中文原生表单与滚动后操作；5：路线足以支撑后续硬约束）仍缺本轮证据。
- 必修项：
  1. **D-R4-1 / D-R4-2**：在同一环境重跑 `isolated_launcher.py --launch`，把 `host_started=true`、launcher.log 关键行（`wm: modules linked` 含 `card`、`[SPLASH] eval` 渲染、PingFang SC 字体）写进 r5 报告 §1；不要再把"环境不允许隔离启动"作为 M0 主 BLOCKED 理由。
  2. **D-R4-3**：交付一份当前 digest 的离线签名 catalog 与对应 artifact（用户授权生成，或用户裁决改走 AppHub 公开发布），让 `install_staged` 在隔离环境真实落盘 `<id>/.bundles/<id>/bundle`；不做 catalog 即不能声称本地安装路径已具备。
  3. **D-R4-4**：在隔离 sandbox 内启用第二个 subject 并验证跨读拒、退出撤权；当前 demo `STATE.actor`/`USERS` 与"`Consent` 单 sheet"不构成可信双主体。
  4. **D-R4-5**：注入业务 bundle 后跑 ≥30 秒诊断窗口，验证 picker 选写、字节一致、原子替换/持久化提交、跨重启提醒恢复、退出后唤醒；不要把"模块已链接"等同于能力可用。
- 阻塞与未测项：
  - 业务 splash bundle 在官方 launcher 内未由本轮 `--launch` 加载（脚本仅 15 秒诊断窗口 + `--apps` 指向空注册表）。
  - 真实模型调用未发起（`_main` profile 未配置；本环境未授权任何 provider）。
  - 可信双主体未实测。
  - picker、字节一致性、原子恢复、提醒持久化、退出后唤醒未实测。
  - 模型路由切回主会话：工具能力外，未执行。
- 受影响先前模块复验：
  - r3 BLOCKED 维持（r3 D8 路线结论错误已由 r4 §3 撤回；r3 D7 编号语义错误已由 r4 ACCEPTANCE_MAPPING.md 重写）。
  - `docs/build-loop/ACCEPTANCE.json` 未触动；P06/P07/P08 UNASSESSED 未重写。
  - G0-C 历史台账 PASS 未被冒充为 r4 原生 PASS。
- 门禁与原台账更新位置：
  - `docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（`review_report` 指向本文件、`reviewed_at` 更新、`status` 维持 BLOCKED、blockers 列表追加 D-R4-1–5 与 D-R4-2 的"必须先于 r5 实现重跑 --launch"）。
  - 不改动 ACCEPTANCE.json，不删 P06/P07/P08 UNASSESSED。
- 是否允许下一模块：**否**。
- 若 BLOCKED 留在本模块的修复/解阻指令：
  - r5 必须由实现方在同一环境按 D-R4-1 / D-R4-3 / D-R4-4 / D-R4-5 重出证据，并显式记录 launcher.log、install_staged 落点、可信双主体路径、原子恢复与提醒跨重启实证；
  - 解阻 R4-B01 的"环境阻断"通过"再跑 `--launch`"即可，无需放宽数据边界；
  - 解阻 R4-B02 需用户裁决"生成离线签名 catalog"或"改走 AppHub 公开发布"；本轮禁止事项不变。
  - 在任何必修项关闭前，M1 不得启动。