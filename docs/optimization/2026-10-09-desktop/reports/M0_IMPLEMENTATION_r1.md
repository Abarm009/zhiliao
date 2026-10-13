# M0 实施报告 r1 — 桌面运行基线与能力裁决

- **模块 / 目标**：M0 — 确认这份桌面应用准备在哪个宿主版本运行，以及模型、文件、身份和存储是否有可实施路径。
- **candidate_id / base_candidate_id**：
  - `B-candidate-8d73056` — 已递交 B 包的固定标签 `octosense-repair-b-v0.1.0`，指向本地 HEAD `8d730569546cb57310944bb299695134df773b9d`。仅存在于公开仓库 `https://github.com/Abarm009/zhiliao/releases/tag/octosense-repair-b-v0.1.0` 与远端标签回读；本地仓库无 `.git/refs/tags/octosense-repair-b-v0.1.0`，提交 `git rev-parse --verify` 失败，按 `[submission/2026-10-08-hub/RECEIPT.md]` 引用远端证据。
  - `M0-r1-worktree` — 当前未提交的修改后工作树：未提交 main.splash（+368 行）和 manifest.json（stamp 已重写又被按要求回滚）；其他修改文档（README/AGENTS 等）不动。
  - `M0-r1-start-manifest-stamp` = `44743e24cd6f2247c6e967a03e1ac4663f6f5bdc5081cc5dbe368c3eed80cf81`（M0 开始时的 manifest claim）。
  - `B-candidate-stamp` = `e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`（HEAD 8d73056 `git show` 给出的 manifest 摘要；与 [B 版提交回执](submission/2026-10-08-hub/RECEIPT.md) 一致）。
- **HEAD / 未提交差异 / 源文件哈希清单**：

  | 文件 | sha256 | 字节数 | 状态 |
  |---|---|---|---|
  | `app/bundle/main.splash` | `fb7527ad6d33c0d91a0936e16a65aabd81a91c602ac18bd29c05641212867f68` | 55,771 | 修改（1311 行，含桌面 v2 改写与 1 处重复 `fn isReporter`） |
  | `app/bundle/main.splash.v1.bak` | `9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72` | 46,640 | 未跟踪（保留）= B-candidate 对应文件 |
  | `app/bundle/main.splash.debug.bak` | `7e96c90c1b8bc6d8b73d5fc7b5737e65818514cebbb44585ba3af5c05c92dd48` | 97,787 | 未跟踪（保留，debug 变体） |
  | `app/bundle/manifest.json` | `2ec1d0ca42a648cf70abedf833ad934faef26da69a75ed6fde00e616259f29fd` | 249 | 修改（stamp 在 [M0-start, post-stamp] 之间来回）：当前已按要求还原为 M0-start 值 `44743e24…` |

  未跟踪保留（不删除、`M0` 不覆盖）：`app/bundle/.archive/{main-helpers,main-new-ui,main-v2-ui,main.splash.desktop-v2-failed}.splash`、`app/bundle/data-test/octosense-repair/state.json`、`app/bundle/{host.log,instance.json}`、新文件 `design-references/2026-10-08-desktop-v2/`、`docs/optimization/2026-10-09-desktop/`（M0–M7 指令包，含 `GATES.json` 与本报告）、`submission/2026-10-08-hub/{ISSUE_BODY,RECEIPT,SUBMITTED_ISSUE}.md`。

- **目标宿主 / 二进制来源与哈希 / 依赖**：
  - 现有 `runtime/native-build/OctoSense-App-Hub/` 是唯一已构建的本地 App Hub 仓库；其工作树 `git log` 最近提交为 `8d730569546cb57310944bb299695134df773b9d`（=本仓库 HEAD），但 **HEAD 中仓库根的 HEAD 与 Cargo.lock 对应的真实源代码提交不在本仓库保存的 OctoSense-App-Hub/target 二进制构建来源上**：本地 `runtime/native-build/OctoSense-App-Hub/target/release/{card-host,hub}` 的 `stat.mtime = 2026-10-01 11:30`，对应最早的 L0 切片 `[runtime/build-loop/iter-L0-toolchain-install.md]` 与 `[submission/2026-10-06-native/SOURCES.md] §6-8` 锁定的"固定旧宿主候选"。
  - 二进制来源（探针实测）：
    - `runtime/native-build/OctoSense-App-Hub/target/release/card-host` — `25,186,160` bytes，Mach-O arm64，`sha256 = bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b`
    - `runtime/native-build/OctoSense-App-Hub/target/release/hub` — `1,928,944` bytes，Mach-O arm64，`sha256 = f211e53a2711d21265147f17699201504eccd3f111ed7bccd8e143800a7d494f`
  - 选择的宿主版本与理由：**唯一可在 macOS Apple Silicon 本地启动、且已通过 L0-A/G0-A 复跑过的 `card-host` 二进制**（来源与 SHA 已在 SOURCES.md §1–§6 标注，且唯一卡点 main.splash 974 行版本仍为 B-candidate stamp）。理由：
    1. App Hub 仓库公开 main 实际为 `78dfda5f33638e1869c36bceef5713342aae861c`，与本机锁定的 `6741dea` 不同（SOURCES.md §6 已记录）。本仓库不具备按上游 main 重编 `card-host` 的 cargo 锁（上游 lockfile 与本机 lockfile 不一致）；当前任务范围不允许删除 OctoSense-App-Hub 重新拉取远端并就地构建（违反"`runtime/` 不被提交、不在 bundle 内" 与"不得擅自升级"）。
    2. 评测发射平台（桌面 Shell）= `OctoSense-Shell@a5d847a`，本地为 `runtime/native-build/OctoSense-Shell/` 裸目录；其 worktree 无 `.git`、无 `target/release/octosense-shell` 二进制。我们没有构建/启动 Shell 的产物证据，不能将它作为"目标桌面宿主"启动本应用。
    3. 仅 `card-host`（OctoSense-App-Hub@6741dea）实测能 admit bundle、绘制 splash、保留状态机；其它线路（rebuild from upstream `78dfda5f`, build shell from upstream `a5d847a`, build from a fresh app-hub clone）都属于"必须先有用户授权 + 网络拉取 + 离线构建产物"的外部动作，本轮不动。
  - 配置前提：本机 PATH 临时增加 `runtime/native-build/OctoSense-App-Hub/target/release` 才能调用 `card-host` / `hub`；card-host 启动需 `MAKEPAD_REMOTE=<port>` 以便外部驱动 `/snap`、`/click`、`/g`。每次 `--allow-unsigned` 才能 admit 未签 manifest。
- **实际模型路由检查结果（开发会话）**：本会话是 root session (`SESSION ROLE: root`)。Router activity 不在本 M0 范围内测量；M0 未调用任何 Router 路由，因此也没有"技能已启用 ≈ 主会话已切换"的风险。M0 只动了 Bash（PATH-extended）、HTTP `curl` 到 card-host 的 `MAKEPAD_REMOTE` 端口、文件系统读写真实文件。Token 未消耗。
- **已检查的前置 PASS 报告**：无前置模块（M0 为链首）。但需要承认前置 state：
  - 既有的 `[docs/build-loop/ACCEPTANCE.json]` 在 M0 开始时是 31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED 的口径（见 `[docs/VERIFICATION.md]` §"2026-10-02 全盘 Review"）。
  - `L0-A`（`G0-A`）的旧 `iteration` 报告位于 `runtime/build-loop/iter-L0-stage-report.md`、`runtime/build-loop/G0-A-iteration.md`、`runtime/build-loop/l0-shots/L0-A-{1,2,3}*.png`、`runtime/build-loop/l0-shots/snap-1-initial.json` 可重读；本轮用了与 L0-A 相同的最小路径，但本次测试 app-data 不在 `runtime/build-loop/`，而是隔离在 `runtime/optimization/2026-10-09/M0/r1/probes/host-stage/app-data/`，**没有动 `runtime/build-loop/` 内的 L0-A 证据**。
  - 本仓库旧 `[submission/2026-10-06-native/SOURCES.md]` §1 写明本机二进制 mtime `2026-10-01 11:30`，对应"固定旧宿主候选"语义；M0 工作树对齐该口径，未引入新的"最新 upstream"假设。
- **本轮修改文件与原因**：
  - `runtime/optimization/2026-10-09/M0/r1/` — 新建隔离证据目录，全部路径都在 `.gitignore` 覆盖范围内，不污染提交。
    - `snapshots/candidate_snapshot.txt` — 候选清单与桌面 v2 / manifest 现状。
    - `probes/host-stage/app-data/octosense-repair/{state.json,tasks.json,actions.jsonl,events.jsonl,test-direct-write.txt}` — 真实重启的隔离 app-data。
    - `probes/{host-stage,04-restart-refused,05-model-file-isolate,06-storage-recovery,07-clock-reminder}/` — 启动日志、截图、`/snap` JSON 副本、heartbeat 文件。
    - `evidence/01-initial-load/`、`evidence/02-click-test/`、`evidence/03-restart/`、`evidence/04-restart-refused/` — 真实原生截图与命名 Label 重算证据。
  - `app/bundle/manifest.json` — 在 M0 探针试验中：`--stamp` 改写为 `aa654664…`（实测 digest）→ 第二次启动因 `manifest.json.postM0boot.bak` 出现在 `digest_dir` 中导致 `refused: bundle digest 2821a9ca… ≠ manifest aa654664…` → 删除 `.postM0boot.bak` 后再 --stamp 重写 → 最后 **已按用户要求把 manifest 回滚到 M0-start 值 `44743e24…`**。这是 M0 启动阻断复现的副作用，未修改业务代码；原 B-candidate stamp `e5b477c7…` 仍在 HEAD 中可被 `git show` 取出。
  - 复制的 `runtime/optimization/2026-10-09/M0/r1/evidence/04-restart-refused/manifest.original-atM0start.json` 与 `manifest.after-first-boot.json` — 仅为探针期间 / 之后的差异留底，不入 bundle。
  - 没有删除别人任何未跟踪文件（`.archive/`, `.bak`, `data-test/`, `host.log`, `instance.json`, `runtime/`）。
- **桌面 UI / 交互变化**：M0 不修改业务 UI；它只测现有 main.splash 的真实启动状态。经实测的工作桌面 v2 布局（`412x892` 容器）发现的事实（**仅为观察、不是修复**）：
  - 顶部栏 `header_actor` 右侧的"演示身份 · 非登录认证"在 412 宽度下被裁切（仅右侧可见 21 像素）；侧栏 `切换演示身份` 行的 5 个 chip 同样被裁，最后一个"经理丙"只露出 11 像素宽。
  - 详情区右上角的 5 个 step 占位 `View{... height:4}` 被渲染为 4×15 的细条且挤占在 ◀ 上一条 / 下一条 ▶ / ☆ 收藏 / ⚙ 设置/身份 这行按钮的左侧，并未作为阶段进度条生效。
  - `ScrollYView` 在固定版本宿主下被 `route-decision.md §4` 标注为"被裁剪内容置 0×0"；当前 bundle 改用 `detail_block := ScrollYView`，需要后续模块用真旋转测试印证滚动是否生效（本轮没拿到 `/scroll` route，回执走单帧 `/g?raw=1`）。
- **接口 / 数据迁移 / 旧数据恢复方式**：M0 不修改业务接口或数据结构。仅运行真实 host，重启 `/g` 与 `/snap` 触发 `main.splash` 的 `load()` 函数从 `<app-data>/octosense-repair/{tasks,actions,events,state}.json` 重新装载，**未观察到 `leg scrubLegacyEvidence` 等迁移分支触发**（probe 阶段写入的事件为 `create_draft` / `confirm_draft` 两个，action 为 `createDraft` / `confirmDraft` 两个，写入顺序 = `[{"at":..., "kind":"create_draft"}, {"at":..., "kind":"confirm_draft"}]` 数组，actions 是 `[]` 数组包裹对象 — 都是脚本 `saveEvents()` / `saveReceipts()` 的统一形态：`{Array}.to_json()` 覆盖写）。重打开确认业务规则不动。
- **已有别人修改的保留与适配**：M0 启动只读 `git status --short`、仅在隔离测试 app-data 目录做写入；未触碰 `backend/`；未触碰 `app/demo-web/`、`submission/`；未更改 `PROGRESS.md`/`README.md`/`AGENTS.md`/`app/bundle/main.splash` 等已有别人修改的文件本身。`docs/implementation/10_UI_UX_SPEC.md` / `docs/build-loop/ACCEPTANCE.json` 等别人未提交改动也保持原样。**M0 仅写隔离目录 + 一处 manifest 回滚**。
- **启动步骤 / 隔离数据位置**：
  - 启动：`PATH="$PWD/runtime/native-build/OctoSense-App-Hub/target/release:$PATH" MAKEPAD_REMOTE=8766 card-host --bundle "$PWD/app/bundle" --app-data "$PWD/runtime/optimization/2026-10-09/M0/r1/probes/host-stage/app-data" --allow-unsigned --stamp --size 412x892`
  - 端口：每个 stage 用了不同端口 8765/8766/8767/8768 区分候选，便于 review。
  - 停机：`pkill -f "card-host --bundle $PWD/app/bundle"` + 等 1 秒。
  - 隔离数据：所有 task/event/state/action 写入都在 `runtime/optimization/2026-10-09/M0/r1/probes/{host-stage,05-,06-}/app-data/octosense-repair/`；不沾染 `runtime/build-loop/`、`runtime/recheck-native-b-*`、`runtime/octosense.db` 等既有数据。
  - 启动阻断与定向修复：`M0` 探针发现当前工作树在 `--stamp` 改写 manifest 之后又被新出现的 `manifest.json.postM0boot.bak` 阻断二次启动；修复 = 删除该 `.bak` 文件（我的测试备品），并把 `app/bundle/manifest.json` 回滚到 M0-start 状态，未涉及 `main.splash` 业务。
- **应用运行模型/provider（适用时；无秘密）**：本轮**未配置模型 provider**。`hub check` 与 card-host admit 都报告 `agent none` / `hosts {}` / `capabilities={"storage"}` / `prompts false`；这表示 `model.complete` / `ai.complete` / `agent.*` 等宿主服务在当前二进制中**没有被绑定**。任何对这些名字的 `host.request` 调用会静默无响应（per `splash_host.rs`："undrained or unrecognized request simply never resolves"）。详见 §"MODEL PROBE"。
- **覆盖的既有验收项与证据运行形态**：覆盖项 = `G0-A / G0-B / G0-C / G0-D / G0-E / G0-F / T28 / T29 / T32 / U09 / U11 / P02`（`M0` 模块的 `acceptance_mapping`）。每一项的状态汇总见 §"测试表"。

## 本轮实施快照（实测，不是声称）

| # | 步骤 | 命令 / 资源 | 输出 |
|---|---|---|---|
| 1 | 启动 card-host（含 `--stamp` 重写 manifest） | 见快照 `probes/host-stage/boot.log` | admit line: `octosense-repair 0.1.0-b admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none` |
| 2 | 隔离 app-data 启动后 `tasks.json` 初始 = `[]` | `cat .../tasks.json` | `[]`，state 默认 `actor=u-reporter-1` |
| 3 | 触发 `tick()` 与 `setActor`、`createDraft`、`confirmDraft`、`setActor(u-tech-1)`、`setActor(u-reporter-2)` | `curl /click?x=...&y=...` 多次 | `evidence/02-click-test/{after-create-draft-task1,after-confirm-open,as-technician}.png` 显示命名 Label 重算 + 状态机迁移 + 切换身份 |
| 4 | 重启同一 app-data，重新 admit | `probes/{03-restart,04-restart-refused,06-storage-recovery}/restart.log` | `04` 因新增 `manifest.json.postM0boot.bak` 出现 `refused: bundle digest 2821a9ca… ≠ manifest aa654664…`；删除 `.bak` 之后再 `--stamp` 重启成功（截图 `06-storage-recovery/after-restart.png`） |
| 5 | 探针：模型调用 | `grep "agent none" boot.log` | confirm `agent none`, `hosts {}`；脚本本体亦无 `model.*` 调用 ⇒ BLOCKED |
| 6 | 探针：真实文件 | `actions.jsonl/tasks.json/events.jsonl/state.json` 写入与重读 | 在隔离路径下恢复完整 |
| 7 | 探针：两个主体来源 | click `报修人二` chip → snap filter 计算 `visibleCount()` = 0 | `evidence/as-reporter-2.png` 显示 0 条可见（隔离原则在脚本层成立，但身份仅是 state.json+USERS 切换，**非宿主注入**） |
| 8 | 探针：clok 与 reminder | `grep -n start_interval .../splash.rs` | tick 是 1Hz UI timer，**window 不在前台就不跑**，且 card-host 无 OS-level reminder/wake API ⇒ BLOCKED（仅前台） |

### 测试表（依据硬验收逐条）

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| 1. 候选输入快照可定位 / 目标桌面宿主能真实启动 | 输入：`candidate_snapshot.txt`、`host.log`、`card-host --bundle app/bundle --app-data r1/...`。 | admit + `[SPLASH] eval: 55771 bytes preserve=false view=true animating=false tick=true epoch=0` 在 boot.log 中出现。 | admit 出现，screen 渲染并被 `/g?raw=1` 抓回 PNG（`evidence/01-initial-load/initial.png`）。 | **PASS for current-worktree** | `runtime/optimization/2026-10-09/M0/r1/probes/host-stage/boot.log`、`evidence/01-initial-load/initial.png`、`snapshots/candidate_snapshot.txt` |
| 2. 模型 / 真实文件 / 可信身份 / 存储恢复 — 最小运行证据 | 见 §"测试表 #5/6/7/8" | 见下 | 见下 | 见下 | 见下 |
| 3. 真实可读写的最小原生表单能保留中文输入 | 412x892 容器下点击 `确认并提交报修` 路径 `confirmDraft` → `task.problem = "东侧会议室空调不制冷，希望今天下午处理"` 落盘 | 重启后从 `tasks.json` 读回的中文一致 | 中文被 `saveTasks()` 落盘、重启后 `evidence/04-restart-refused/after-restart.png` 渲染 "OPEN" 列表能看到中文标题 | **PASS for 持久化路径**（脚本层写回 round-trip 一致）。但 `main.splash` **没有任何 TextInput/TextEdit 控件**：用户**无法自行键入**中文，只能由脚本 `createDraft()` 内置常量生成。 | `app/bundle/main.splash`（全文 grep 无 `TextInput`/`TextEdit`）、`grep "TextInput\|TextEdit" /snap output` = 0、`evidence/02-click-test/as-technician.png` |
| 4. 运行数据使用隔离测试目录 | 全部 app-data 写到 `runtime/optimization/2026-10-09/M0/r1/probes/**/app-data/octosense-repair/` | 与既有 L0 / 业务数据库不交叉 | `runtime/build-loop/`、`runtime/recheck-native-b-*`、`runtime/octosense.db`、`runtime/ops.db` 未被写入 | **PASS** | `runtime/optimization/2026-10-09/M0/r1/probes/host-stage/app-data/` |
| 5. 路线足以支撑后续硬约束 (M2/M3/M5) | 见下文"路线建议" | M2/M3/M5 各自必需要求可被同一路线继续支撑 | 当前 `card-host` 无法支撑 model 与 OS 级身份、提醒；M2/M3/M5 路线需先决定 shell+kernel+messages 路线 | **PARTIAL**（路线可指明，宿主尚不能完全支撑） | 见 §"路线建议" |

### 实测记录（按 M0 修改指令的"需要完成"清单）

1. **清点 B 包与当前未提交修改** — 见 §"本轮修改文件与原因"。未 reset / 未 stash / 未删未跟踪 / 未覆盖别人修改。
2. **从官方资料核对并选定宿主版本 / 依赖 / 启动入口** — 选定 `card-host` 来自 `OctoSense-App-Hub@6741dea`（依据 `[submission/2026-10-06-native/SOURCES.md]`）。本仓库没有上游 main lockfile 对应的新二进制，无法在不联网的前提下重编最新 host（违反"不擅自升级"与"运行数据边界"）。详见 §"目标宿主"。
3. **真实启动现有原生工作台，检查输入、列表选择、详情、滚动、命名控件刷新；先静态查重复函数名 / 调用方兼容** — 见测试表 + 静态报告：
   - 重复函数：`fn isReporter` 在 `app/bundle/main.splash` 中被两次定义：line 113 (`fn isReporter(t, u){ u.id == t.reporter }`) 与 line 1020 (`fn isReporter(t){ if t == nil { return false } return t.reporter == STATE.actor }`)。OctoScript 解释器在本次 `[SPLASH] eval: 55771 bytes view=true animating=false tick=true epoch=0` 中**没有**因重复 fn 终止 eval，但在调用栈里只有后定义的 1-arg 版本被解析（v1.bak 只有 63 fns，无重复）。这是 main.splash 当前改动的潜在隐患：旧 1-arg 与 2-arg 混编时，旧路径被静默重定义覆盖。本次业务键值未走旧 2-arg 路径，没有显式失败，但建议 M1 启动前消除重复。
   - 命名 Label 刷新：通过 `tick()` 与 `refreshDesktop()` 实测可见 `scope_note` / `visible_count` / `header_actor` / `task_status` / `task_detail` / `next_step_title` / `next_step_summary` 都按业务修改而变化 ⇒ **PASS**。
   - 列表选择：selectedIdx 在 `click "下一条 ▶"` 后从 0 切换。但 `next` 按钮被裁切；412 宽度下，列表视图没有可用的 `ScrollYView` 真实滚动过（route-decision.md §4 已记录）。
   - 中文输入：脚本字符串常量 `"东侧会议室空调不制冷，希望今天下午处理"` 与 `"报修人一"` 路径实测全程通过；用户 UI 输入路径被 `main.splash` 不挂任何 TextInput 控件挡住 ⇒ 用户**不能自主输入中文**。
4. **隔离探针中验证**：
   - **真实宿主模型响应** — 不可能：card-host 不注册 `model.*` 处理器；manifest 没有 `["ai","model","research"]` capability；agent profile `none` ⇒ **BLOCKED**（不冒充 PASS）。
   - **真实文件 select / save / close-reopen / read** — `fs.write(filename, bytes)` 在脚本中以 `TASKS.to_json()` 等覆盖写；`fs.read(path)` 在脚本启动 reload 已工作；重启后回读任务与事件全部一致 ⇒ **PASS for 隔离存储路径**。**`pick_file` widget 不存在**于本 bundle 的 81 个 widget 中（widget 清单见 §3），用户不能"选择本地文件"。`addEvidence()` 在脚本中固定 `bytes=1024` 是 `demo:true` 占位，本轮不冒充真实附件。
   - **两个可信主体的来源及授权隔离** — 隔离逻辑（`visibleToMe`, `isReporter`, `isTechU`, `isMgrU`）在脚本层生效（u-reporter-2 与 prj-A 任务交叉看到 0 条）。但 **身份源头只是脚本内部 `STATE.actor`，不是宿主身份注入**——`Splash::set_host_tag` 路径未被使用；`agent: none`；不可信来源 ⇒ **BLOCKED for true principal proof**（按 M0 修改指令要求不冒充）。
   - **存储错误返回及恢复所需原语** — `splash_storage.rs` 配额 16 MiB 已强制（`storage 16777216 bytes`），但 `fs.write` 错误返回被脚本吞掉（`runCommand()` 内 `save*` 不抛错、不汇报 override 失败）。重启备份恢复路径（`loadJsonlLines` split fallback、`scrubLegacyEvidence`）在 boot log 中没有显式触发，但代码路径仍在 ⇒ 缺错误注入测试；当前 M0 不冒充"已证"。
5. **可靠时钟 / 可恢复提醒 / 任务跳回** — `tick()` 是 1Hz `start_interval(1.0, ...)` UI Timer，**仅在窗口处于前台时被驱动**。`card-host` 不暴露 OS-level reminder / wake / schedule API；`octosense-shell` 注册的 host services（`register_host_services`）只覆盖 `glance/mail/news/llm/model`，**没有 scheduler / notification service**。**结论：M0 时钟只在 UI 前台跑；系统级提醒与跳回不可用 ⇒ BLOCKED**。
6. **提出唯一任务事实源路线** — 见 §"唯一任务事实源路线"。
7. **映射既有 G0/T01-T38/U01-U12/P01-P08 到新模块** — 见 §"映射"。

## 尚未完成（NOT_RUN / BLOCKED / FAIL 列表）

按硬验收逐条对应：

- **硬验收 #1**（候选输入快照可定位 / 目标桌面宿主能真实启动）— **PASS for 当前 worktree，BLOCKED for "目标桌面宿主" 整体语义**：
  - 当前 worktree ⇒ real launch + admit + PNG capture ⇒ 真实证据。
  - "目标桌面宿主"是 `OctoSense-Shell@a5d847a` 的语义：本仓库 `runtime/native-build/OctoSense-Shell/` 仅是裸目录、无 `.git`、无 `target/release/octosense-shell`；构建它要求回连 `github.com/OctoSense-org/OctoSense-Shell` 拉取 main、cargo 解析 lockfile、产出 Mach-O 二进制；当前未做。

- **硬验收 #2**（模型 / 真实文件 / 可信身份 / 存储恢复都要最小运行证据；未具备的能力记 BLOCKED，禁止把候选记为 PASS）— 一部分是证据，一部分是 BLOCKED，已**禁止**把任何候选方案记为 PASS：
  - 模型：**BLOCKED**（无 provider、无 capability、无 agent）。
  - 真实文件：**PASS for 隔离存储路径**；**BLOCKED for 用户真实选择**（无 picker widget）。
  - 可信身份：**PASS for 脚本级隔离逻辑**；**BLOCKED for 宿主身份**（无 host tag、无 grant、无 pair）。
  - 存储恢复：**PASS for 关闭重开读回**；**BLOCKED for 错误注入路径**（缺失败注入测试，fs.write 错误未在脚本层上报）。

- **硬验收 #3**（可读写的最小原生表单能保留中文输入；不需浏览器原型）— **PARTIAL：写回 round-trip 一致**，**用户 UI 不挂 TextInput 控件**，需要 M1 调整（不冒充通过）。

- **硬验收 #4**（运行数据使用隔离测试目录；原有数据及未提交改动完整保留）— **PASS**（详见 §"运行数据使用隔离测试目录"测试表）。

- **硬验收 #5**（路线足以支撑后续硬约束；需要用户作出的架构选择尚未解决时，本模块不放行）— **PARTIAL**：
  - 后续 M1–M7 的硬约束要求：模型 / 真实附件 / 真实身份 / OS 提醒 / 脚本配额恢复 / UI 阶段进度等。当前 route 的 `card-host` 实体路线已贯通关键写回与重启恢复，但模型/身份/提醒/附件上链这四条必须先由用户给出"目标宿主再上一层"的裁决：是继续走 `card-host` + 补 `Splash::set_host_tag` + 私接 kernel，还是切到 `OctoSense-Shell@a5d847a` 重编、或者在 `Hub@6741dea` 的基础上扩展一个不含 llm kernel 的简化通道。**本模块不放行**：详见 §"路线建议"。

### 残留问题（不是 PASS 也不是 FAIL，BLOCKED 或 NOT_RUN）

- 模型 `model.complete` —— **BLOCKED**（capability、agent、宿主服务均不存在）。
- 文件选择 UI（picker） —— **BLOCKED**（无该 widget）。
- 宿主身份注入（pair / grant / shared-card protocol） —— **BLOCKED**（host log `agent none`，`Splash::set_host_tag` 未被调）。
- 任务完成后跨窗口或关窗 OS 级提醒 / 跳回 —— **BLOCKED**（host 不暴露此 API）。
- 1-arg `isReporter` 静默覆盖 2-arg `isReporter` 的潜在隐患 —— **NOT_RUN / 待 M1 解决**。
- 当前工作树 `manifest.json` 的 stamp（无论 `44743e24…` 还是实测 `aa654664…`）对应的 `bundle_blake3` 包含 `/app/bundle/.DS_Store`、`.archive/`、`runtime/`、`*.bak`、`host.log`、`instance.json` 与本次新增的 `manifest.json.postM0boot.bak`。Hub submitted stamp `e5b477c7…` 是 B-candidate 在干净 bundle 目录下的产物。M0 只指出现状，不替代：任何最终发布的 stamp 必须基于一个**只含正式 bundle 内容**的目录；当前不在本模块范围。
- `data-test/octosense-repair/` 出现在 `app/bundle/` 下，污染 `digest_dir`。它本应是 host lock / app-data staging；正确位置应当在 `runtime/`，但用户明确"保留其他人的改动"，所以只标记不挪。

## 唯一任务事实源路线

**当前（已实测）可行的"路线 A"：**

1. 任务权威 —— `app/bundle/main.splash` 的 `<jail>/{tasks.json,actions.jsonl,events.jsonl,state.json}`，与既有 `[app/docs/route-decision.md]` §2 一致。
2. 命令边界 —— `runCommand()` 中 `sourceOk → visible → receiptFor/recordReceipt` 三段；同 key 重放、提交流转 + 失败回执均落到 `actions.jsonl`。
3. UI 由同一脚本驱动 —— `refreshLabels` + `refreshDesktop` + `tick()` 1Hz Label 自动重算。
4. 隔离 —— 16 MiB / 20M instructions / 64 MiB heap；启动阻断由 `digest_dir + admit_and_resolve_dir` 强制；prompt = false。
5. 重启恢复 —— `--stamp` 触发 manifest 重写和 admit；同一 app-data 重启读到同一任务列表 / actor / selectedIdx。

**这一路线足以落地"任务权威唯一"与"业务回执可重读"。不满足（需后续模块解决）的部分：**

- 真实附件：仅 `addEvidence()` 仍写 demo 数据；隔离原语 `fs.write` 是有的，缺 picker 与 trust 路径（M5 解决）。
- 真实身份：`setActor` 仅切换 state.actor，没有任何 host tag；M2 解决。
- 真实模型：`model.complete` 等价物不存在；M3 解决。
- OS 级提醒：`tick()` 前台-only；scheduler / notification API 不可用；M6 解决。
- 配额原子化与崩溃恢复：`fs.write` 单次覆盖为非事务；M5/M7 解决。

**最小复现（针对关键能力不成立）：**

- `model.complete` 不存在 —— 复现：尝试在 main.splash 中写 `host.request("model.complete", {prompt: "x"})` 并刷新，会观察到无响应（`host.request` 的 undrained request "simply never resolves"）。本次未写此分支，原因是 `app/bundle/main.splash` 没有该调用且 `agent none`；意思是 M3 一上来就要替换路线，不能用 card-host 现状"假装接入"。
- `pick_file` 不存在 —— 复现：脚本本体记录 81 个 widget，没有 `FilePicker / TextInput / FileDialog / AiArea`；任何"用户选择一张照片"的步骤需要 M5 直接走 host 服务桥或自造下载器。
- 跨窗口提醒不存在 —— 复现：将窗口最小化（测试不可达，因为 `/minimize` route 不存在），splah 渲染线程暂停；`tick_timer` 不再触发 ⇒ 任何依赖 1Hz 重算的"等待到点提醒"都会失准。
- 二次启动被 manifest `bundle_blake3` 不匹配阻断 —— 复现：见 §"测试表 #1"中的第二次 admit，错误信息原文已记录。

**具体替代方案（涉及新公网 / 宿主扩展 / 改变交付形态时，必须先给可审阅方案 —— 本模块不放行）：**

- 路线 B（包外 HTTPS 业务服务）：文档 13 已经声明**未授权**且本模块维持该结论。M2 后用户授权才走。
- 路线 C（重编 OctoSense-Shell@a5d847a 并切到 Shell）：是评估"目标桌面宿主"完整语义的唯一办法；需网络拉取 + 离线 cargo 构建 + 重新 stamp + 重新交付。需要用户授权与新的里程碑。
- 路线 D（hub@6741dea 的受限扩展：在 card-host 内追加一个 mini 模型/身份服务而不带 kernel）：部分可行，把"插入 Anthropic 直连"绑死在 card-host 二进制内，**不**经过任何 grant/kernel 路径。代价：评测与官方发布的"是否被官方包目录接受"取决于 Hub 维护者是否会接受 publisher-key 升级过的新二进制。**先书面提案再实施，本轮不部署。**

## 映射（M0 vs 既有的 64 项）

| Module | 既有 | 本模块承担 / 不承担 / 与本模块冲突 | 历史后端证据 vs 当前原生证据 |
|---|---|---|---|
| M0 | G0-A/B/C/D/E/F, T28, T29, T32, U09, U11, P02 | M0 全权 | 见下 |
| G0-A 固定版本、原生脚本构建与真实启动 | 既定 = PASS（[docs/build-loop/ACCEPTANCE.json]） | M0 本轮验证 PASS 沿用 | 后端证据 = G0-A PASS 注解；当前证据 = `probes/host-stage/boot.log` 与 `evidence/01-initial-load/initial.png` |
| G0-B 真实可信身份、授权与独立会话 | 既定 = NOT_RUN | M0 不修；记录宿主缺位 = BLOCKED for true principal | 后端证据 = 9-2 review 后改判 T18/T29 = FAIL；当前证据 = `agent none` + `prompts false` |
| G0-C 唯一事实源、原子一致性、并发与恢复 | 既定 = PASS（仅后端） | M0 验证隔离存储 + 重启走 `card-host`；不验证并发 | 后端证据 = T04/T15/T22 单测；当前证据 = `probes/host-stage/boot.log` 的 isolate jail |
| G0-D 真实附件 | 既定 = NOT_RUN | M0 不修；脚本 addEvidence 写 demo：true | 后端证据 = T19 单测；当前证据 = addEvidence 路径占位 |
| G0-E 系统助手 | 既定 = NOT_RUN | M0 不修；`model.*` 与 `agent.*` 均 BLOCKED | 后端证据 = T25/T26 NOT_RUN；当前证据 = boot.log `agent none` |
| G0-F 提醒 / 任务意图视图 | 既定 = NOT_RUN | M0 不修；tick 仅前台 ⇒ BLOCKED for foreground-only | 后端证据 = T23 NOT_RUN；当前证据 = tick_timer 是 `cx.start_interval(1.0)` |
| T28 原生 grant 关闭/退出/到期 | 既定 = FAIL（[docs/build-loop/ACCEPTANCE.json] `T28` 维持 FAIL） | M0 不修；记录路径未接通 | 后端证据 = T28 原改判 FAIL；当前证据 = 没有 host tag 接口 |
| T29 原生 grant 全链路 | 既定 = FAIL | M0 不修 | 历史 = 9-2 改判 FAIL；当前 = `agent none` |
| T32 配对码 / Web 审批 / 应用脚本取 token | 既定 = NOT_RUN | M0 不修；脚本未拉 token ⇒ BLOCKED | 后端证据 = T32 NOT_RUN；当前证据 = `host.request("pair.*")` 在该二进制无处理器 |
| U09 1280×800 / 窄窗布局 | 既定 = NOT_RUN | M0 仅 412x892 探针；不做响应式断言 | 后端证据 = U09 NOT_RUN；当前证据 = `evidence/01-initial-load/initial.png` 412 width overflow 右侧 |
| U11 真实宿主中滚动 / 输入 / 面板切换稳定 | 既定 = NOT_RUN | M0 不替代理一个 `/scroll` route；记录脚本 + ScrollYView 仍未真旋转测试 | 后端证据 = U11 NOT_RUN；当前证据 = `/scroll` route `{"err":"no route"}` |
| P02 完整源码 + 依赖 + 干净启动说明 | 既定 = PASS | M0 验证 `card-host` 启动可重复，但写明本机脚本依赖固化为 `cargo build` 的旧二进制（OctoSense-App-Hub@6741dea 上的 `Cargo.lock`，与上游 main 不一致） | 后端证据 = P02 PASS 注解；当前证据 = `SOURCES.md §6` 与本报告 §"目标宿主" |

后端证据 vs 原生证据的边界：
- 所有 `T2x` / `Uxx` 的"既 PASS / NOT_RUN / FAIL"都是后端 8821 / 8822 上的判断，**与原生 `card-host` 是否能在 macOS Apple Silicon 上绘制本应用是两件事**。
- `L8-DV2 PASS` 在 [docs/build-loop/ACCEPTANCE.json] 是"桌面 v2 工作台"自评（720h 自检），M0 重新独立跑出 81 widget 的同布局并发现 412 width 裁切的客观证据，不替代 L8-DV2 PASS 的可信度，但**不冲突**。
- `T28 FAIL`：`app/bundle/main.splash` 在 `card-host` 上可以 admit、绘制与重启恢复任务（"同一 task_id + 状态 + 操作 + 重开" = 部分满足），但 grant 关闭/退出/到期机制 = BLOCKED，所以 T28 仍为 FAIL，未升级。

## 路线建议（仅候选，未实施）

1. **不重编上游 main，不引入 last-commit 漂移**。当前 `card-host` 来自 `OctoSense-App-Hub@6741dea`，对应 `[submission/2026-10-06-native/SOURCES.md]` 锁定的固定版本。如果 M1/M2 之后走到了"必须用最新 host"的位置，请先把"是否值得花 1 个里程碑重编"作为用户决策（涉及网络 + 重交付路径）。
2. **身份与隔离可在本路线上递进**：用户偏好 = 通过 `setActor` 演示扩展；脚本层 `visibleToMe` 已经截断；M2 引入 `Splash::set_host_tag(<granted-token>)` + 把 token 落地 `<jail>/identity.json`，把"主权受托"硬约束在 host 提供方。
3. **模型可走最小化路径**：在 `card-host` 不变的前提下，要么（a）新写一个"写入 `<jail>/proposals.json`" 的提案器让外部 LLM 客户端（开发者本机）来推；要么（b）说服用户用 OctoSense-Shell@a5d847a 提供的 `model.complete`（需重编 Shell）。两条路线都不在 M0 范围。
4. **OS 级提醒需要第三方 scheduler**（NotificationCenter / launchd / systemd），card-host 不暴露此 API —— M6 才能讨论，且需要先有"提醒接收方"。

## 交接

- 候选清单：
  - 本仓库 HEAD `8d730569546cb57310944bb299695134df773b9d`
  - 已递交 B 包的固定标签：`octosense-repair-b-v0.1.0`（远端）
  - 修改工作树：`M0-r1-worktree`（未提交，仅文档与桌面 v2 改写）
  - 二进制：`card-host` 来自 `OctoSense-App-Hub@6741dea`（mtime 2026-10-01 11:30，sha256 `bebded3d…`），`hub` 来自同源（sha256 `f211e53a…`）
- 原生截图、boot log、snap JSON 全部在 `runtime/optimization/2026-10-09/M0/r1/{evidence,probes}/`（gitignore 路径）。
- 实际测试命令：
  - 启动：`PATH=...:$PATH MAKEPAD_REMOTE=N card-host --bundle app/bundle --app-data runtime/optimization/2026-10-09/M0/r1/probes/host-stage/app-data --allow-unsigned --stamp --size 412x892`
  - 探针：`curl -s -m 5 'http://127.0.0.1:N/snap?q=&w=0'`、`curl -s -m 5 'http://127.0.0.1:N/click?x=X&y=Y'`、`curl -s -m 5 'http://127.0.0.1:N/g?w=0&scale=1'`、`curl -s -m 5 'http://127.0.0.1:N/'`（路由字典）
  - 验证：`shasum -a 256 runtime/native-build/OctoSense-App-Hub/target/release/{card-host,hub}`、`hub stamp app/bundle --allow-unsigned`、`hub check app/bundle --allow-unsigned`
- **编码方状态：READY_FOR_REVIEW**。
- 残留：见 §"尚未完成"。
- **最终 PASS 等待独立审查**。

## 自我判定

- 既有的 64 项维持原状（M0 不改 ACCEPTANCE.json 的 `T/U/P` 项；改写 P-类与 G0-类可能误传"已通过"）。L8-DV2 / L0-A / G0-A 的 PASS 注解保留，但凡由 M0 重新验证的，本模块都用 `runtime/optimization/2026-10-09/M0/r1/` 的证据；**不**重新声明它们 PASS。
- 没有声称脚本已经全部原生闭环；本轮范围内硬验收 #3 (中文表单输入保留) 是 PARTIAL：写回 round-trip 一致，但用户输入控件不存在。
- 模型 / 文件选择器 / 宿主身份 / OS 提醒四项**没有**伪装成 PASS。
- 本模块不进入 M1。
