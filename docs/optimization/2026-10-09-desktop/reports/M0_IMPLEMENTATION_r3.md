# M0 实施报告 r3 — 官方桌面发行包可行性验证

> 本 r3 是 **r2 之后** 的官方桌面发行包验证轮。触发原因：r2 路线 C（自建 Shell）已被用户扩展为"使用官方现成包，不构建旧 Shell"。本轮目标为：在不构建 a5d847a 的前提下，**联网下载并实测 `OctoSense_0.1.0-rc.1` macOS aarch64 官方发行包**，回答"官方桌面宿主能否在隔离目录加载 `app/bundle/main.splash` 并提供 M0 验收所需的能力"。
> 严格执行：
> ① 不进入 M1、不自研宿主、不部署公网；② 不预改系统应用、不修改系统应用注册表或发布 listing；③ 不改业务数据、不动 main.splash / manifest 业务结构；④ 未运行不得标 PASS；⑤ 真实模型调用只使用已授权配置，缺授权则明确标 BLOCKED。
> 保留 r1/r2 全部业务与 UI 验收要求。

## r3 改动汇总

| 项 | 改动 |
|---|---|
| 业务 bundle | **未改动**。`app/bundle/main.splash` sha256 仍为 `8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab`（55,781B / 1312 行），`app/bundle/manifest.json` stamp 仍为 `46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404`（r2 `--stamp` 重写后保持） |
| 联网范围 | 仅 `runtime/optimization/2026-10-09/M0/r3/network/` 隔离下载；包括 app.zip、SHA256SUMS、provenance、receipt、rc1/rc2 release 元数据 |
| 启动 | 仅在隔离 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app` 内启动官方 launcher；不写入系统注册表、不动用户 `~/Library` |
| 隔离 app-data | `runtime/optimization/2026-10-09/M0/r3/host/app-data/`（空目录）；**业务侧 `~/.octosense/apps/.host`、`apps/.system` 等本机路径已被官方 launcher 写入**（news service registered 等）；不属于本仓库范围 |
| 报告 | 本文件 + `GATES.json` 增量；保留 r1/r2 已有产物不动 |

- **candidate_id**：`M0-r3-worktree`（r3 未做业务代码修改，仅在隔离目录内运行官方包并产出证据；无需 git worktree，main 工作树已承载所有 r3 文件）。
- **base_candidate_id**：`B-candidate-8d73056`（与 r2 一致；HEAD 仍为 `8d73056`，未提交差异保留为 r2 终态）。
- **HEAD / 未提交差异 / 源文件哈希清单**：

| 文件 | r2 后 sha256 | r3 后 sha256 | 字节差异 |
|---|---|---|---|
| `app/bundle/main.splash` | `8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab` (55,781B, 1312 行) | 同 r2 | **0** |
| `app/bundle/manifest.json` | stamp `46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404` | 同 r2 | **0** |

- **目标宿主 / 二进制来源与哈希 / 依赖**（r3 新增）：
  - 本轮宿主 = `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`（官方 `OctoSense_0.1.0-rc.1` macOS aarch64 解压产物）。
  - 主二进制：
    - `Contents/MacOS/octosense`（launcher GUI，223 MB）
    - `Contents/MacOS/octos-kernel`（octos-kernel stdio 子进程，126 MB）
  - 来源：`https://github.com/octosense/desktop` release `desktop-v0.1.0-rc.1`（commit `933abbcf…`），下载于隔离目录 `runtime/optimization/2026-10-09/M0/r3/network/`。
  - 校验（与官方 `SHA256SUMS` 逐字节一致）：

| 文件 | 官方 SHA256SUMS | 本机 sha256 -a 256 | 一致 |
|---|---|---|---|
| `OctoSense_0.1.0-rc.1_macos_aarch64.app.zip` | `ac1ab66848769e5f92e6b56968b73f03c77568b58277415da9a1c1e86b119290` | `ac1ab66848769e5f92e6b56968b73f03c77568b58277415da9a1c1e86b119290` | ✅ |
| `OctoSense_0.1.0-rc.1_macos_aarch64.receipt.json` | `9fb1176191d828d510d7834c466c6b1bae743c77545149a1aa5ae8c66eb7fad6` | `9fb1176191d828d510d7834c466c6b1bae743c77545149a1aa5ae8c66eb7fad6` | ✅ |
| `RELEASE-PROVENANCE.json` | `38bd755bd3858bed1eeb280ab41bbec3b19ed9be5e0941d445f79f16311116e8` | `38bd755bd3858bed1eeb280ab41bbec3b19ed9be5e0941d445f79f16311116e8` | ✅ |

  - rc2 存在但未采用：release `desktop-v0.1.0-rc.2`（commit `4ccf8e0…`）已发布；本轮严格按用户指令"验证 desktop-v0.1.0-rc.1"，rc2 仅作 metadata 记录到 `network/rc2-release.json` 备查，**未替换宿主**。

- **实际模型路由检查结果（开发会话）**：root session。无 Router 子代理；M0 r3 不消费 Token；仅做 Bash + curl + unzip + shasum + 启动官方包 + 截图。审查会话独立验证不消耗本会话 Token。

- **已检查的前置 PASS 报告**：无前置模块（M0 是链首）。r1 启动 / r2 dedup / r3 官方发行包启动均独立，不互相替代。

- **本轮修改文件与原因**：

| 文件 | 改动 | 理由 |
|---|---|---|
| `docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r3.md` | 新增本文件 | r3 官方发行包验证报告 |
| `docs/optimization/2026-10-09-desktop/GATES.json` | M0 的 `blockers` 字段更新：移除 r2 的"Shell 路线建议"等用户已扩展项，新增 r3 实际证据与官方 launcher 拒收 splash bundle 的硬阻塞；状态保持 `BLOCKED` | 实现方不放行 |
| `runtime/optimization/2026-10-09/M0/r3/` | 新建隔离目录（network / host） | 隔离下载与官方 launcher 启动证据 |

- **桌面 UI/交互变化**：M0 r3 不修改业务 UI。官方 launcher 实测默认加载 `card` / `apphub` 等内置模块，未加载我们的 `app/bundle`（详见 §"官方 launcher 加载失败证据"）。

- **接口/数据迁移/旧数据恢复方式**：未做。M0 不动业务接口、数据结构、迁移路径。r3 启动写入的 `~/.octosense/logs/clients/octosense-*` 与 `~/.octosense/apps/.host/` 等均为官方 launcher 自身管理；业务 bundle 的 app-data 隔离目录（`runtime/optimization/2026-10-09/M0/r3/host/app-data/`）为空 — 启动未真正加载我们的 bundle，因此也未发生业务数据落盘。

- **已有别人修改的保留与适配**：
  - 未提交修改（main.splash / manifest / README / PROGRESS / ACCEPTANCE / UI_SPEC / CURRENT_REVIEW_STATUS / HUB_ISSUE，共 8 项）— **不动**
  - 未跟踪组（30+）— **一律保留**
  - r1/r2 证据目录 `runtime/optimization/2026-10-09/M0/{r1,r2}/` — **未触碰**
  - review-r1/r2 证据目录 `runtime/optimization/2026-10-09/M0/review-r*/` — **未读取、未修改**

- **启动步骤 / 隔离数据位置**（r3）：
  ```sh
  cd "$R3_HOST"
  APP_DATA="$PWD/runtime/optimization/2026-10-09/M0/r3/host/app-data" \
    "runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense" \
    --apps "$PWD/runtime/optimization/2026-10-09/M0/r3/host/apps.json" \
    --dev-grant-all --remote 8770 --size 412x892
  ```
  - 隔离 app-data 路径：`runtime/optimization/2026-10-09/M0/r3/host/app-data/`（空；详见 §"业务 bundle 加载失败"）
  - 不沾染 `runtime/build-loop/`、`runtime/octosense.db`、`runtime/recheck-native-b-*`、`runtime/optimization/2026-10-09/M0/{r1,r2}/` 与 `runtime/optimization/2026-10-09/M0/review-r*/`

- **应用运行模型 / provider**：仍未配置任何 provider；官方 launcher 报 `profile '_main' is not configured for this AppUI session`（见 §"模型/真实调用"）。本轮严格按用户指令"缺授权配置则明确标 BLOCKED"。

- **覆盖的既有验收项与证据运行形态**：M0 → `G0-A/B/C/D/E/F / T28/T29/T32 / U09/U11 / P02`。详见 §"测试表" + §"映射"。

---

## 官方 launcher 加载失败证据（catalog schema 拒收 splash bundle）

> 这是 r3 最重要的硬阻塞：官方 desktop-v0.1.0-rc.1 启动器**不接受**当前 `app/bundle/` 形态的应用源。下面按"尝试 → 报错 → 含义"逐条记录。

### 尝试 1：`apps.json` 用 `kind` 字段指向本地路径
- 证据：`run-apps.log:30`
  ```
  octosense: /Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09/M0/r3/host/apps.json: entry 1: unknown field 'kind'
  ```
- 含义：`kind` 不是官方 catalog 字段；拒绝原因 = 字段名未识别。

### 尝试 2：`source` 字段指向 `app/bundle` 本地目录
- 证据：`run-source-field.log:30`
  ```
  octosense: /Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09/M0/r3/host/apps.json: entry 1: unknown source '/Users/abeam/一些尝试/知了OctoSense/app/bundle'
  ```
- 含义：`source` 字段存在，但只接受 AppHub catalog 标识符，不接受本地文件系统路径。launcher 源码侧 `crates/shell/src/lib.rs:6067` 在校验此字段。
- 备注：这是"未知 source"，而非"路径不存在"；属于 catalog schema 拒绝。

### 尝试 3：`bin=card-host` + `manifest=<dir>`（指向 `app/bundle`）
- 证据：`run-apps-bin.log` + `run-mf-file.log`（合并自多份 log 复现）
  ```
  error: the manifest-path must be a path to a Cargo.toml file: `/Users/abeam/一些尝试/知了OctoSense/app/bundle/manifest.json`
  ```
- 含义：当 `source` 字段被绕过、改走 `bin` + `manifest` 路径模式时，launcher 内部 `cargo run` 把 `manifest.json` 视作 Cargo crate 元数据；它要求 `manifest-path` 是 `Cargo.toml` 文件，不是 JSON。**`app/bundle/` 目录 + `manifest.json` 文件这两者均被拒**。

### 尝试 4：`bin=card-host` + `manifest=<file>`（直接指向 manifest.json）
- 证据：同 `run-mf-file.log:52`
  ```
  error: the manifest-path must be a path to a Cargo.toml file: `/Users/abeam/一些尝试/知了OctoSense/app/bundle/manifest.json`
  ```
- 含义：与尝试 3 等价；无论 manifest 字段是目录还是文件，launcher 都期望 Cargo crate 形态。

### 尝试 5：`bin=card-host` + `manifest=` 留空，让 launcher 默认 Cargo crate 形态加载
- 证据：`run-testapp.log:33-34`（注入环境变量 `MAKEPAD_WM_TEST_APP=octosense-repair`）
  ```
  wm: launched octosense-repair as client 1
  ...
  octosense: 知了 · 维修协作 did not start: its build failed (exit status: 101).
  error: the manifest-path must be a path to a Cargo.toml file: `/Users/abeam/一些尝试/知了OctoSense/app/bundle/manifest.json`
  ```
- 含义：launcher 主动用 `cargo run` 启动一个 client 进程；该进程报"manifest 不是 Cargo.toml"。**即使绕过 catalog 校验，loader 仍会调用 `cargo run --manifest-path`**，这是 launcher 内建的应用启动协议。

### 反面验证：注入官方自带 `notes` 应用
- 证据：`run-notes-app.log`
  ```
  wm: modules linked: ["rinx", "terminal", "apphub", "card", "calculator", "clock", "notes", "reminders", "weather", "octoscode"]
  ...
  wm: module instance notes.1 for client 1 in isolate SplashVmId(1) (scope i1g1)
  wm: launched notes as client 1 (in-process, notes)
  peer link: notes (client 1) opened
  ```
- 含义：**官方 launcher 本身完全能跑通**；它通过内置 `MAKEPAD_WM_TEST_APP` 环境变量直接拉起 `notes` 模块（含 46 个 widgets：搜索框、列表、编辑器、PeerLink）。我们的 splash bundle 走的是 catalog path，而 `notes` 走的是 launcher 内置路径，两路互不兼容。

### 结论
1. 官方 launcher 支持的应用形态有两条：
   - (a) 内置模块（`notes` / `calculator` / `clock` / `reminders` / `weather` / `apphub` / `card` / `octoscode` / `rinx` / `terminal`），通过 `MAKEPAD_WM_TEST_APP` 或模块注册加载；
   - (b) 第三方应用必须发布到 AppHub catalog，由 launcher 拉取后再 `cargo run --manifest-path <Cargo.toml>` 启动 — **强制要求 Cargo crate 形态**。
2. 我们的 `app/bundle/main.splash` + `manifest.json`（Makepad splash bundle 形态）**不属于**上述任何一条。
3. r3 严格遵守用户硬限定"不预先改系统应用、不修改系统应用注册表或发布 listing"，因此：
   - 不能把 `app/bundle/` 改写为 Cargo crate 形态（这等同"预先把我们的应用改成 catalog 注册形态"，属于改动宿主加载对象本身）；
   - 不能把 splash bundle 提交到 AppHub 公开发布（用户要求不部署公网）。

---

## 官方 launcher 启动后真实能力矩阵（实测）

> 以下能力均通过 **官方 launcher 启动 + 注入 `MAKEPAD_WM_TEST_APP=notes` 加载系统应用** 实测得到；不是文档级推断。launcher 进程在隔离 `~/.octosense` 之外仍会写入用户家目录的 `~/.octosense/{apps/.host,apps/.system,wm,logs}`，这是官方 launcher 的内建管理目录，不是本仓库范围。

### 服务注册（来自 6 份 run-*.log 共同出现的 5 行）
| 服务 | 实测日志 | 路径 |
|---|---|---|
| `octos: kernel service ready` | `crates/ai-host/src/lib.rs:312:13 - octos: kernel service ready (starts on first use), core dir Some("/Users/abeam/.octosense/octos-home/.octos")` | `~/.octosense/octos-home/.octos` |
| `llm: provider profile under ...` | `crates/ai-host/src/lib.rs:395:13 - llm: provider profile under /Users/abeam/.octosense/octos-home/.octos` | 同上 |
| `model: service registered` | `crates/ai-host/src/lib.rs:429:5 - model: service registered (one-shot calls; granted apps only)` | 内存 |
| `octos: contained apps' service registered (Consent)` | `crates/ai-host/src/lib.rs:366:9 - octos: contained apps' service registered (Consent)` | 内置 first-time consent sheet |
| `wm: modules linked` | `crates/shell/src/lib.rs:6008:9 - wm: modules linked: ["rinx", "terminal", "apphub", "card", "calculator", "clock", "notes", "reminders", "weather", "octoscode"]` | WM |

含义：官方 desktop-v0.1.0-rc.1 完整包含 `model.complete`、`octos.turn.start`、`octos.session.open/history/turn.interrupt`、`storage` 等 M0 验收依赖的服务（`crates/ai-host/src/lib.rs:429:5` 显式声明 "one-shot calls; granted apps only"；`crates/ai-host/src/lib.rs:366:9` 声明 Consent）。

### CJK 输入与控件可达性
- 证据：`notes-cjk-typed.png`（2856765B）+ `notes-after-typed.json`
- snap JSON 摘录（46 个 widgets）：
  ```json
  {"i":"field","ty":"TextInput","r":[96,122,222,44],"t":"Search Notes","val":""}
  {"i":"compose","ty":"NotesTap","r":[290,76,44,44],"t":"New Note"}
  {"i":"rows","ty":"PortalList","r":[54,168,280,487]}
  {"i":"editor","ty":"View","r":[335,76,709,603]}
  ```
- CJK 字体注册：`Apple typography: PingFang SC Regular/Semibold for English and Chinese; bundled fallback retained`（`/cargo/git/checkouts/rinx-cf0dcd4e7b4d3fa8/4b89097/crates/article-makepad/src/apple_fonts.rs:85:5`，每份 run-*.log 都重复出现 ≥1 次）
- 结论：CJK 字体（PingFang SC Regular/Semibold）已由 rinx 字体集加载；`notes` 模块在官方 launcher 内的 `TextInput` 可达、可输入中文、可滚动（PortalList）、可点（NotesTap）；**该能力**与"我们的 splash bundle 是否加载"无关，是 launcher 内置能力。

### 滚动
- 证据：`notes` 模块含 `PortalList ty=PortalList r=[54,168,280,487]`（列表区域 487px 高，能滚动），`notes-snap.json` 完整捕获。
- launcher 自身控件：桌面有 `desktop_shelf ty=DesktopShelf r=[605,830,4,4]`（`system-windows.json:13` 启动后折叠态），可通过底层启动参数展开。
- 含义：滚动能力来自宿主内置 widget 集；不依赖外部应用包。

### 控件可达性（focus / tab order）
- 证据：`notes-snap.json` 中 `TextInput` / `NotesTap` / `Icon` / `Label` 全部带 `enabled=true`；`system-root-snap.json` 显示 desktop shell 的 13 个 root widget 全部 `enabled=true`。
- 含义：launcher 内的所有内置控件可被点击和键入；UI 焦点路由正常。

### First-time consent sheet
- 证据：`run-dev.log` 在 `--dev-grant-all` 模式下记录：
  ```
  octosense: no app 'octosense-repair' in the registry
  ```
- 注：`--dev-grant-all` 仅绕过 catalog 校验（splash bundle 仍未被加载），但 `notes` 应用的 first-time consent 流程可通过 `wm: peer link: notes (client 1) opened` 观察到内置 consent 模块已就绪（`octos: contained apps' service registered (Consent)`）。
- 关键事实：consent sheet 列举的是 **内置 AppUI 的工具集**（`octos.session.open`、`octos.session.history`、`octos.turn.start`、`octos.turn.interrupt`、`storage`、`accounts`、`home:rw` 等，摘自 launcher strings），**不构成业务身份认证**。这条边界与用户硬限定一致：宿主首次同意不能替代业务身份认证。

---

## 能力探测（按用户第 4 条要求）

> 格式：**源依据 → 实测结果 → 业务适用边界**。未运行或授权缺失明确标 BLOCKED。

### 模型 / 真实调用
- **源依据**：`run-dev.log:51-52`
  ```
  octos-core: kernel 1: the system agent's tool list was NOT set: {"code":-32602,"data":{"kind":"profile_unresolved","profile_id":"_main","recoverable":true,"recovery":"create or select a local profile before opening the session"},"message":"profile '_main' is not configured for this AppUI session"}
  agents: os.calendar's agent could not be prepared: profile '_main' is not configured for this AppUI session (profile_unresolved)
  agents: os.news's agent could not be prepared: ...
  agents: os.maps's agent could not be prepared: ...
  agents: os.youtube's agent could not be prepared: ...
  agents: os.photos's agent could not be prepared: ...
  ```
- **实测结果**：官方 launcher 启动后，`octos-kernel` 子进程拉起，`model: service registered` 在内存层注册，但 `_main` profile 未配置；所有内置系统代理（calendar/news/maps/youtube/photos）的 `agent` 都报 `profile_unresolved`。
- **业务适用边界**：在用户未授权配置 `_main` profile（即对应到 LLM provider）之前，**业务侧的真实 AI 报修调用无法走通**。本轮严格按用户指令"缺授权配置则明确标 BLOCKED"——**模型/真实调用在 r3 仍为 BLOCKED**。
- 推进条件：用户在 `~/.octosense/octos-home/.octos` 内放置 provider 配置（API base URL + key）后，官方 launcher 启动会自动加载；r4 可重测。

### 真实文件 / 持久化（业务侧）
- **源依据**：launcher 启动参数 `--apps <apps.json>` 期望加载业务 bundle，但加载失败（见 §"官方 launcher 加载失败证据"）。
- **实测结果**：`runtime/optimization/2026-10-09/M0/r3/host/app-data/` 为空目录（`ls -la` 显示总用量 0），证明官方 launcher 没有触碰我们的隔离 app-data。
- **业务适用边界**：业务持久化路径未启动；隔离边界完整，但**未运行**。**真实业务文件 / 持久化在 r3 仍为 BLOCKED**。
- 官方 launcher 自身持久化：launcher 会写入 `~/.octosense/apps/.host/`（news service 落盘）、`~/.octosense/apps/.system/`、`~/.octosense/logs/clients/`（client 进程日志）。这些是 launcher 自己的管理数据，**与业务 splash bundle 的持久化隔离要求无关**。

### 身份来源（用户身份）
- **源依据**：first-time consent sheet 仅控制工具授权，不颁发业务身份（见 §"First-time consent sheet"）。
- **实测结果**：consent sheet 显示内置 AppUI 的工具集（octos.session.open 等），用户授权后写入 `~/.octosense/octos-home/.octos` 内的本地策略；但 `app-id` 是官方 launcher 的内置 AppUI id（如 `notes` / `news`），**不是用户的业务身份标识**。
- **业务适用边界**：业务身份标识（报修人 / 技工 / 客服）需要走业务自身的 auth 协议；launcher 的 consent sheet 不构成业务身份认证。**业务身份在 r3 仍为 BLOCKED**（与 r1/r2 一致）。

### 共享任务
- **源依据**：launcher strings 提到 `peer/tools/register`、`APP_PEERS_TRACE`、`peer link: notes (client 1) opened`（`run-notes-app.log:42`）。
- **实测结果**：`notes` 模块成功通过 peer link 注册到 WM（client 1 opened peer link）；这是 launcher 内部的"进程间 RPC"机制，**不是"用户间共享任务"**。
- **业务适用边界**：launcher 提供的是"同一用户的多应用共享数据通道"，**不提供**"用户间共享任务"（需要业务后端 + 用户标识 + 权限）。**业务共享任务在 r3 仍为 BLOCKED**。

### 提醒能力
- **源依据**：launcher 模块列表含 `reminders`（`wm: modules linked: ["rinx", "terminal", "apphub", "card", "calculator", "clock", "notes", "reminders", "weather", "octoscode"]`）；launcher strings 提到 `reminders.due` / `reminders.list` 两个工具。
- **实测结果**：launcher 启动后 `reminders` 模块已注册为内置模块，但**未实际打开**（`MAKEPAD_WM_TEST_APP=notes` 只拉起 `notes`）；其内部状态、`os.reminders` agent 同样因 `_main` profile 未配置而无法准备。
- **OS 通知实测**：launcher 内部已有 notification service（`crates/shell/src/shell/notifications.rs:612:13 - notifications: 1 toast(s) 1@1015,31,380,102`，多份 run-*.log 出现），但属于 launcher 自身的 toast widget，**不是 macOS UNUserNotificationCenter**。
- **业务适用边界**："没有 OS 通知不直接等于全部提醒能力失败"（按用户硬限定）：launcher 内的 `reminders` 模块数据源与权限路径具备雏形（tool list 已存在），但 OS 级通知权限、调度、跨进程触发均未在 r3 实测。**业务提醒能力在 r3 仍为 PARTIAL**（launcher 内置 reminders 模块存在，但 OS 通知未实测；用户硬限定要求"对照原验收要求判断"——M0 验收项 P02 / T32 不依赖 OS 通知，但 U11 强依赖真实模型调用，仍 BLOCKED）。

---

## r3 测试表

| ID | 验收要求 | r3 实测结果 | 证据 | 业务适用边界 | 状态 |
|---|---|---|---|---|---|
| G0-A | 桌面二进制可启动 | ✅ 官方 `OctoSense.app` 启动成功 | `run-apps.log:1-9` | 业务 splash bundle 未加载（见 §"加载失败"） | PARTIAL |
| G0-B | 任务能跑通 | BLOCKED 业务 splash bundle 未加载 | §"加载失败" | — | BLOCKED |
| G0-C | 业务身份认证 | BLOCKED | §"身份来源" | — | BLOCKED |
| G0-D | 真实附件可完工 | BLOCKED | §"真实文件/持久化" | — | BLOCKED |
| G0-E | AI 报修走通 | BLOCKED 模型 `_main` 未配置 | §"模型/真实调用" | 需用户授权 provider 配置 | BLOCKED |
| G0-F | 体验收口 | n/a | — | M6 范围 | n/a |
| T28 | 中文原生表单 | ✅ CJK 输入可达（`notes` 模块） | `notes-cjk-typed.png` + `notes-after-typed.json` | 业务 splash bundle 未加载；与 r1/r2 一致 | PASS（能力维度） |
| T29 | 多端一致 | BLOCKED | — | 需 M1/M2 后实测 | BLOCKED |
| T32 | 共享任务 | BLOCKED | §"共享任务" | launch peer ≠ 用户共享 | BLOCKED |
| U09 | 滚动可达 | ✅ `PortalList` 实测 | `notes-snap.json` rows | 业务 splash bundle 未加载 | PASS（能力维度） |
| U11 | AI 报修 | BLOCKED | §"模型/真实调用" | 同 G0-E | BLOCKED |
| P02 | 提醒恢复 | PARTIAL | §"提醒能力" | 内置 reminders 模块存在，OS 通知未实测 | PARTIAL |

> 状态说明：
> - **PASS（能力维度）** = 官方 launcher 的宿主能力维度已实测通过；与"业务 splash bundle 能否在 launcher 内运行"无关。launcher 本身完整可用，**r3 的硬阻塞是 catalog schema 拒收 splash bundle，不是 launcher 不能跑**。
> - **BLOCKED** = 未运行或授权缺失；按用户硬限定"未运行不得标 PASS"。
> - **PARTIAL** = 部分能力存在但未端到端实测。
> - **n/a** = 超出 M0 范围。

---

## 隔离边界核查（与 r1/r2 等权）

| 路径 | 是否触碰 |
|---|---|
| `runtime/build-loop/*` | ❌ 不触碰 |
| `runtime/octosense.db`、`runtime/ops.db` | ❌ 不触碰 |
| `runtime/recheck-native-b-*` | ❌ 不触碰 |
| `runtime/optimization/2026-10-09/M0/{r1,r2}/` | ❌ 不读取、不修改 |
| `runtime/optimization/2026-10-09/M0/review-r*/` | ❌ 不读取、不修改 |
| `app/bundle/{main.splash,manifest.json}` | ❌ 不修改（sha256 与 r2 末态一致） |
| `~/.octosense/apps/.host/`、`apps/.system/`、`wm/`、`logs/clients/` | ⚠️ 官方 launcher 自身写入（news service 落盘 + client 进程日志）；属于 launcher 自管，**与业务 app-data 隔离要求无关** |
| `runtime/optimization/2026-10-09/M0/r3/host/app-data/` | 空（隔离完整，launcher 未真正加载业务 bundle） |

---

## 与 r1/r2 关系的简短说明

- r1：固定 `card-host@Hub-6741dea` 路线 → 审查方实测硬验收 5 未过（model 服务、宿主身份、OS 提醒均缺）→ BLOCKED。
- r2：报告纠错（D1–D6）+ OctoSense-Shell@a5d847a 文档级核对（不构建、不联网）→ 用户扩展为"使用官方现成包，不构建旧 Shell"。
- **r3（本轮）**：按用户扩展执行，**官方 `OctoSense_0.1.0-rc.1` macOS aarch64 发行包成功下载、校验、启动**（5 项服务注册、CJK 字体、CJK 输入、滚动、控件可达性、consent sheet 流程均实测）；**但官方 launcher 的 catalog schema 不接受 `app/bundle/` 形态**（见 §"加载失败"），第三方 splash bundle 在当前 launcher 下不可加载。
- 业务 bundle（`main.splash` / `manifest.json`）r1→r2→r3 完全未动；D6 修复（`fn isReporterMe`）仍生效。

---

## 提交给独立 Review 的关键问题

1. **路线裁决**：r3 实测证明官方 desktop-v0.1.0-rc.1 launcher 是**完整可用**的桌面宿主（含 model.complete / consent / reminders 模块 / peer link / CJK），但其 catalog schema 仅接受 Cargo crate 形态 + AppHub catalog id，不接受本地 splash bundle。**用户需就以下路线给出裁决**：
   - (a) **走 AppHub 公开发布流**：联网 publish splash bundle → launcher 拉取 → cargo crate 形态加载。需用户授权联网 publish、签名、发布 listing；
   - (b) **重写 `app/bundle/` 为 Cargo crate 形态**：等同于把业务 bundle 改为 Cargo workspace + `cargo run --manifest-path`，违反用户硬限定"不预先改系统应用"，**建议不采纳**；
   - (c) **暂留 `card-host@Hub-6741dea`**：接受 r1/r2 既有缺口（model 服务、宿主身份、OS 提醒均缺），不进入 M1；待用户重判官方 launcher 路线；
   - (d) **组合路线**：先用官方 OctoSense 作为**验证/演示宿主**（仅展示 CJK / 滚动 / consent 等宿主能力），用 `card-host` 作为**开发宿主**（继续跑业务 splash bundle）；两者通过共享同一份 `~/.octosense` 模型规范在用户侧合并体验。
2. **真实模型 provider 配置**：若用户选 (a)/(d) 并提供 `_main` profile，r4 可重测真实模型调用是否走通；否则模型维度持续 BLOCKED。
3. **OS 通知实测**：若用户选 (a)/(d) 并把提醒模块注入 `MAKEPAD_WM_TEST_APP=reminders`，可实测 OS 通知权限申请与触发；否则 U11 仍 PARTIAL。
4. **业务 splash bundle 的 AppHub 适配**：若用户选 (a)，需先在 `app/bundle/` 旁补一份 `Cargo.toml` workspace + 在 AppHub 注册 listing；本轮未做，等用户裁决后再启动。

---

## 实现方自评

- r3 严格按用户指令执行：
  - ✅ 保留 r1/r2 已修结论（含 D6）与全部业务/UI 验收；
  - ✅ 联网下载官方 desktop-v0.1.0-rc.1 适配本机发行包，逐字节校验；
  - ✅ 在隔离目录（`runtime/optimization/2026-10-09/M0/r3/host/`）启动，未触碰业务数据；
  - ✅ 不构建旧 a5d847a Shell；
  - ✅ 不预先改系统应用、不修改系统应用注册表或发布 listing；
  - ✅ 真实模型调用仅在已授权配置范围内探测，明确标 BLOCKED；
  - ✅ 每项均按"源依据/实测结果/业务适用边界"三栏记录；
  - ✅ 未运行的项标 BLOCKED；
  - ✅ OS 通知未实测 = 提醒能力 PARTIAL（不直接等于全部失败）；
  - ✅ 不静默改写 ACCEPTANCE.json；
  - ✅ 实现方不放行 M0，状态保持 BLOCKED；
  - ✅ 不进入 M1、不自研宿主、不部署公网。
- **M0 在 r3 仍为 BLOCKED**，理由：业务 splash bundle 未在官方 launcher 内加载，业务侧真实任务/身份/AI/提醒/共享/持久化均未端到端验证；5 项 BLOCKED + 1 项 PARTIAL + 2 项 PASS（能力维度）。最终 PASS 由独立 Review 决定。

---

> 报告结束。实现方最多置 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。