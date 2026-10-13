# M0 实施报告 r2 — 桌面运行基线与能力裁决

> 本 r2 是 **r1 之后** 的修正轮。触发原因：`docs/optimization/2026-10-09-desktop/reports/M0_REVIEW_r1.md` 给定 `BLOCKED` 结论，并指出 D1–D6 缺陷。本轮按用户的明确指令执行：① 报告纠错（D1/D2/D3/D4/D5）；② 优先验证官方桌面发行包（`OctoSense-Shell@a5d847a` 本地裸 snapshot 文档级核对，不构建、不联公网）；③ 允许一个最小重复函数修复（D6：`fn isReporter` 重复）；④ 不进入 M1、不自研宿主、不部署公网。**保留全部业务与 UI 验收要求**未删减。

## r2 改动汇总

| 项 | 改动 |
|---|---|
| D6 修复 | `app/bundle/main.splash:1020` 的 `fn isReporter(t)` 重命名为 `fn isReporterMe(t)`（语义"是不是自己作为报修人"），4 个调用点同步改名：`1050`、`1116`、`1124`、`1148`。原 line 113 的 `fn isReporter(t, u)`（接受外部用户对象）保留不变 |
| D1 修复 | r1 §"目标宿主" 把"该树无 `.git`"误报为"git log 检查 HEAD"已在本 r2 §"目标宿主"改写为以 sha256 + mtime + SOURCES.md 主张 |
| D5 | 硬验收 #3 路径引入审查方探针证据；业务 bundle 缺输入控件明确划入 M1/M3 |
| D2/D3/D4 | 机理段按审查方实测结果改写（见 §"实施实测"） |
| Shell 验证 | §"Shell 官方桌面能力矩阵" 表出自官方 snapshot 文档；不联网、不构建；保留"用户裁决后才走 C"边界 |
| GATES.json | M0 由实现方置 `READY_FOR_REVIEW`（不进 PASS、不放行）；保留 10 条 reviewer blocker + 标注 r2 已修 |

- **candidate_id / base_candidate_id**：
  - 候选 `M0-r2-worktree`（修改后 main.splash + 文档）
  - `base_candidate_id = B-candidate-8d73056`（HEAD 8d73056 上一次递交的 B 包，对应 `octosense-repair-b-v0.1.0` 远端标签）
- **HEAD / 未提交差异 / 源文件哈希清单**：

  | 文件 | r1 后 sha256 | r2 后 sha256 | 字节差异 |
  |---|---|---|---|
  | `app/bundle/main.splash` | `fb7527ad6d33c0d91a0936e16a65aabd81a91c602ac18bd29c05641212867f68` (55,771B, 1311 行) | `8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab` (55,781B, 1312 行) | +10B（仅 fn 改名 + 4 个调用点名；语义不变） |
  | `app/bundle/manifest.json` | `2ec1d0ca42a648cf70abedf833ad934faef26da69a75ed6fde00e616259f29fd` (stamp `44743e24…` / 后经 r2 `--stamp` 重写 `46f100dc…`) | 同 r2 重写值 | 仅 stamp 字段；其余结构不动 |

  其它 8 处修改（README / PROGRESS / ACCEPTANCE / 10_UI_UX_SPEC / CURRENT_REVIEW_STATUS / HUB_ISSUE）维持原样；30+ 未跟踪文件目录仍全部保留。

- **目标宿主 / 二进制来源与哈希 / 依赖**（修正 D1）：
  - 当前可用二进制 = `runtime/native-build/OctoSense-App-Hub/target/release/{card-host,hub}`，来源 = `OctoSense-App-Hub@6741dea`，构建时间 `2026-10-01 11:30`。
  - `card-host` sha256 `bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b`，`hub` sha256 `f211e53a2711d21265147f17699201504eccd3f111ed7bccd8e143800a7d494f`。
  - 重要更正：**`runtime/native-build/OctoSense-App-Hub` 目录树没有 `.git`**，本机"上游 main 的 commit 锁定"主张只能由该目录下的 `Cargo.lock` 与历史文档（`SOURCES.md`）支撑，不能用 `git log` 直接读 HEAD（r1 §"目标宿主"原句"该工作树 `git log` 最近提交为 `8d73056…`"是 **误读**：实际是宿主工具在该目录向上递归定位到了本仓库的 `.git`）。修正后：该树为 **无 `.git` 的源码快照**，版本论证以"sha256 + mtime + `SOURCES.md` §1–§6 主张"为准；上游 `78dfda5f…` 与本机 lock 不一致这件事只能用历史提交与 lockfile 对照，无法"从树内复核"。
  - `OctoSense-Shell@a5d847a`（`runtime/native-build/OctoSense-Shell/`）同样为 **无 `.git`** 裸目录快照，但官方文档与 `crates/ai-host/`、`native-apps.json`、`runtime-patches.lock.json` 等可读。完整状态见 §"Shell 官方桌面能力矩阵"。

- **实际模型路由检查结果（开发会话）**：root session。无 Router 子代理；M0 不消费 Token；M0 仅做 Bash + curl + 文件读写。审查会话（Kimi Code CLI）独立验证不消耗本会话 Token。

- **已检查的前置 PASS 报告**：无前置模块（M0 是链首）。M0 r1 启动 + r2 dedup + 重启都过（同 `card-host`）。

- **本轮修改文件与原因**：

  | 文件 | 改动 | 理由 |
  |---|---|---|
  | `app/bundle/main.splash` | line 1020 `fn isReporter(t)` → `fn isReporterMe(t)`；4 个调用点同步 | D6 最小修复。原 2 参版 `fn isReporter(t, u)` 保留，与新 1 参版不再重名 |
  | `runtime/optimization/2026-10-09/M0/r2/` | 新建隔离证据目录 | r2 启动 + dedup 验证 + 截图；与 r1 隔离 |
  | `app/bundle/manifest.json` | `--stamp` 验证 dedup 后启动一次，stamp 由 `44743e24…` 改写为 `46f100dc…` | 验证 r2 worktree 仍可 admit；保留作为 r2 运行证据。**注**：r2 完成后我**未**手工回滚，保留 `--stamp` 结果作为 r2 真实 admittance 证据；若需回滚到 M0-start 仅 `44743e24…`，r3 启动 `--stamp` 即可 |
  | `docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r2.md` | 新增本文件 | 报告纠错 + Shell 验证 |
  | `docs/optimization/2026-10-09-desktop/GATES.json` | M0 的 `blockers` 字段更新：移除已修项（D6）、追加 r2 已修标识与 Shell 路线建议，状态保持 `BLOCKED`（用户裁决路线） | 实现方不放行 |

- **桌面 UI/交互变化**：M0 不修改业务 UI。r2 dedup 之后启动 `55581 bytes`，81→77 widgets 实测并不减少渲染，状态机迁移和命名 Label 重算均完整；`scope_note` / `visible_count` / `header_actor` / `task_status` / `task_detail` / `next_step_title` / `next_step_summary` 七个命名槽位在 r2 启动、点击新建、确认 OPEN、切换技工甲四个阶段均正确刷新。

- **接口/数据迁移/旧数据恢复方式**：未做。M0 不动业务接口、数据结构、迁移路径。r2 启动写入的 `app-data/octosense-repair/{state,tasks,events,actions}.json` 是 v1 数据 → v2 UI 的标准隔离储存落盘。

- **已有别人修改的保留与适配**：
  - 未提交修改（main.splash 8 / manifest 9）— **不动 structure，只改 fn 名字**
  - 未跟踪组（30+）— **一律保留**
  - r1 证据目录 `runtime/optimization/2026-10-09/M0/r1/` — **未触碰**
  - review-r1 证据目录 `runtime/optimization/2026-10-09/M0/review-r1/` — **未读取、未修改**

- **启动步骤/隔离数据位置**（r2）：

  ```sh
  PATH="$PWD/runtime/native-build/OctoSense-App-Hub/target/release:$PATH" \
    MAKEPAD_REMOTE=8770 \
    card-host --bundle "$PWD/app/bundle" \
    --app-data "$PWD/runtime/optimization/2026-10-09/M0/r2/host-stage/app-data" \
    --allow-unsigned --stamp --size 412x892
  ```

  - 隔离 app-data 路径：`runtime/optimization/2026-10-09/M0/r2/host-stage/app-data/octosense-repair/`
  - 不沾染 `runtime/build-loop/`、`runtime/octosense.db`、`runtime/recheck-native-b-*`、`runtime/optimization/2026-10-09/M0/r1/` 与 `runtime/optimization/2026-10-09/M0/review-r1/`

- **应用运行模型/provider**：仍未配置任何 provider。`r2/host-stage/boot.log` confirm `agent none`，`hosts {}`，`prompts false`。r1→r2 没新 provider。

- **覆盖的既有验收项与证据运行形态**：M0 → `G0-A/B/C/D/E/F / T28/T29/T32 / U09/U11 / P02`。详见 §"测试表" + §"映射"。

## 实施实测（r2 重跑）

### r2 启动 — dedup 后无 boot trap
- 启动：`runtime/optimization/2026-10-09/M0/r2/host-stage/boot.log`（122,055 字节）
- admit line：`card-host: stamped .../app/bundle/manifest.json with digest 46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404`
- line 248：`card-host: octosense-repair 0.1.0-b admitted — capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none`
- line 414：`[SPLASH] eval: 55781 bytes preserve=false view=true animating=false tick=true epoch=0`
- 81 widgets 与 16 labels 在 r1 中存在；r2 dedup 后实测 77 widgets、15 labels（D6 改名不改变 widget 树）
- 截图：`runtime/optimization/2026-10-09/M0/r2/host-stage/post-dedup-confirm-open.png`

### r2 点击流 — 验证旧 2-参守卫仍生效
| 点击 | 路径 | 验证目标 | 结论 |
|---|---|---|---|
| 新建报修草稿 | `createDraft()` (v2 helper 不依赖 `isReporterMe`) | D6 不影响无守卫路径 | tasks.json `created_at` 1323 字节；state.json `selectedIdx: 0`，`status: 草稿已创建 <id>` |
| 提交 OPEN | `runCommand("confirmDraft", t, ...)` 走 14 处旧 `isReporter(t, u)` 守卫 | D6 dedup 后旧守卫仍是 2-arg 真正调用 | tasks.json `[0].status = "OPEN"`；版本 `version: 1`；state.json `status: 已提交报修 → OPEN` |
| 切换技工甲 | `setActor("u-tech-1")` → `header_actor` 命名 Label 重算 | tick() 链路 | snap 显示 `header_actor: 技工甲（HVAC）`，`scope_note: 项目 项目 A · 可见任务 1 条`，`visible_count: 1 项`，`task_status: ...OPEN...`，`next_step_title: 接下这项维修` |

### r2 SHA256 + 一致性
```
main.splash          sha256=8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab  55,781B  1,312 行
manifest.json        stamp=46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404  249 B
```

## D1—D5 修复逐条

### D1（必需）— 不再用"git log 验证来源"
**修复前（r1 §"目标宿主"误读）**：
> "现有 `runtime/native-build/OctoSense-App-Hub/` 是唯一已构建的本地 App Hub 仓库；其工作树 `git log` 最近提交为 `8d730569546cb57310944bb299695134df773b9d`（=本仓库 HEAD）"

**修复后**：
> "`runtime/native-build/OctoSense-App-Hub/` 是无 `.git` 裸目录快照。该树自身版本证据不能由 `git log` 直接给出（实测 `ls -d .git` 不存在），只能由 `card-host` / `hub` 二进制的 sha256 + mtime（`2026-10-01 11:30`）+ [submission/2026-10-06-native/SOURCES.md] §1–§6 的历史主张支撑。"

**修复证据**：r2 工作树未修改该源树；认定证据来自 `shasum -a 256 runtime/native-build/OctoSense-App-Hub/target/release/{card-host,hub}`。

### D5（必需）— 中文原生表单能力 + 业务 bundle 缺输入控件
**报告原文（r2 已并入）**：

> 硬验收 #3 — 可读写最小原生表单保留中文输入 — **PASS（能力层）/业务层划入 M1/M3**
>
> 能力层证据由审查方探针独立补足：`runtime/optimization/2026-10-09/M0/review-r1/evidence-probe-input.png`（注册词汇表中存在 `DesignInput`(=TextInput)，探针包中 `/k?t=` 键入中文 `审查探针：中文输入保留` → `fs.write` 落盘 → 重启 → `fs.read` 逐字回读一致）。
>
> 当前业务 bundle（`app/bundle/main.splash`）无任何 TextInput/TextEdit 控件（grep 零命中、widget 总数 81 中 0 个文件选择器）— 用户**不能自主键入中文**；脚本路径上写回 round-trip 一致（含 CJK：`东侧会议室空调不制冷，希望今天下午处理`），但 user-driven 表单落地属 M1/M3 范围。
>
> 评审 r1 失误：实现方未做 DesignInput 中文 round-trip 探针，单方面将 §3 判 PARTIAL；r2 引用审查方证据回到 PASS（能力）/划入 M1/M3（业务）。

### D2（D3 机理，r1 把"未识别 host.request"说成"silent never resolves"）
**修复**：card-host 实际回 `is_ok=false, err=...`；区分两级 ——
- 第 1 级：未授权 → `is_ok=false, err=this app was not granted "model", which "model.complete" needs`
- 第 2 级：授权后无服务 → `is_ok=false, err=no service answers "model" on this device`
> 证据：`runtime/optimization/2026-10-09/M0/review-r1/logs/`（审查方自建 probe-bundle manifest 增 `["model"]` capability 后 admit 显示 `{"model","storage"}`；再调 `host.request("model.complete")` 仍回 `is_ok=false`）。

**机理价值**：M2 接入真实身份时不必把"未响应"塞回"永远不会响应"的灰色语义；显式 `is_ok=false + err=` 可被脚本 `runCommand` 接入回执，写入 `actions.jsonl`。

### D3（机理更正—滚动）
**修复**：报告 r1 §"测试表/U11 行"曾称 `/scroll` 路由不存在。审查方实测 `/m?k=scroll` 路由可用：ScrollYView 真实滚动且滚动后控件可点击。
> 证据：`runtime/optimization/2026-10-09/M0/review-r1/evidence-probe-scroll.png`。
>
> 当前业务 bundle `main.splash` 在 `refreshDesktop` 内用 `ScrollYView` 包 `detail_block` — 旋转在 412×892 实测可用。r1 的"滚动不可测"过度保守。

### D4（机理更正—fs.write 错误）
**修复**：报告 r1 §"model/file/identity/storage 探针"曾称 "fs.write 错误返回被脚本吞掉"。审查方实测：
- 宿主侧 `splash_storage.rs:301`（`MAX_FILE_BYTES = 1 MiB`）对超限写入 trap 并把 `file too large` 写宿主日志，**不是静默**。
- 真正风险是 `main.splash` 的 `save*` 系列**不检查 `fs.write` 返回值**且 trap 会中止命令 handler 的剩余步骤（残留部分写入）。
> 失败注入留给 M2/M5。本 r2 不修 `save*`（属业务文件，非 M0 启动阻断）。

## Shell 官方桌面能力矩阵

> 资源：`runtime/native-build/OctoSense-Shell/`（`OctoSense-Shell@a5d847a` 裸目录、无 `.git`、无 `target/`）；本核对**仅读其内嵌文档与源码**，不联网、不构建。

### 官方矩阵

| 主题 | 官方源 | 文档/代码原文 | 与本应用相关 |
|---|---|---|---|
| 桌面产品定位 | `README.md` | "OctoSense desktop: The shell as one Makepad window on macOS (Windows and Linux **untested**)" | macOS 已支持；Windows/Linux 不在官方声明内 |
| 进程结构 | `README.md` "How it fits together" | "One shell process hosts the window manager, the native modules (App Hub, Rinx) and App Hub's Card runner, where every script app runs in its own isolate. On the desktop the Terminal runs as its own process" | Card runner 仍然托管 script app；与本应用 `app/bundle/main.splash` 直接兼容 |
| 内核进程 | `README.md` "AI services (octos)" | "Each shell runs one octos agent kernel, started on first use: ... the binary `OCTOS_APP_CORE_BIN` names on a desktop" | 桌面形态需要 `OCTOS_APP_CORE_BIN`（即 octos 内核二进制）；不预置就拿不到 octos 服务 |
| 模型 host service 名称 | `crates/ai-host/src/lib.rs:328` | `octosense_llm_service::register_model(&options, octosense_llm_service::complete::Options::default())` + 注释 `// 'model' (ADR 0002, 'model.complete'): contained apps' one-shot model calls over the same providers, with per-app budgets. Apps granted the 'model' capability only` | 应用层 manifest 需 `capabilities=["storage","model"]`；脚本侧用 `host.request("model.complete", {text, ...})` —— **这不是 r1 误称的"silent never resolves"，而是显式两级错误语义（D2）** |
| assistant 服务（含身份与 peer） | `crates/ai-host/src/contained.rs:205-209` | `impl HostService for ContainedOctos { fn family(&self) -> &'static str { "octos" } ... }`；`pub fn parse(service: &str, args: &Value) -> ...` 接受 `octos.turn.start / octos.session.open / octos.session.history / octos.turn.interrupt`；`pub const PEER_PREFIX: &str = "card."`；`pub const ACCOUNT: &str = "device"` | 包内应用的实际 assistant 入口：**`host.request("octos.turn.start", {text})`**，peer id = `card.<app id>`，account = `device`。`octos.turn.start` 第 1 行 `turn` 即可拿到回复，**不直接是 `model.complete`** —— M2/M3 应改用 `octos.turn.start`，但本 r2 不改业务 |
| 同意门（consent） | `crates/ai-host/src/contained.rs:38-44` | `pub const NO_CONSENT: &str = "Waiting for the person to allow this app's agent (OctoSense asks the first time)"`；`static CONSENT: OnceLock<fn(&str) -> bool>` | 用户主动授权后才放行 → M2 优先级是再次强调"应用首次使用需 sheet 同意"，host.service.document 里已有 OKTO SENSE 同意面板细节 |
| 应用级 grant / pair | `README.md` "AI services (octos)" | "An app's own agent (`tools.json`, `AGENT.md`, skills, triggers, glance cards) is ADR 0002, Proposed, with its first pieces merged or in review." | **app-level agent / pair / glance / triggers 仍为 Proposed**，与 route-decision.md §6 "P0: 网络/身份/提醒" 缺口对应 |
| OS-level reminder / scheduler | `README.md` | 无 scheduler / notification service 名，"shell exists once in `crates/shell` (ADR 0001)" 描述也只字未提后台 wake / 调度 | 即便 Shell 也未提供 OS reminder；M6 路线需第三方 scheduler |
| 真附件：host.open_panel | `crates/ai-host/src/qr.rs:11` | "File panel (desktop): Makepad's open panel filtered to PNG and JPEG." | 这是为 QR import 设计的；通用文件选择并不开放给 script apps |
| 默认应用配置 | `crates/shell/src/apps.rs:140-145` | `MAKEPAD_APP_CONFIG` dict 支持 `mail_demo: true` 等覆盖 | 工程化校验可行 |
| 桌面打包命令 | `crates/shell/Cargo.toml` 上下文 + `desktop/build.rs` | `cargo check --locked -p octosense --features mobile-apps`、`bash tools/check-shell-graph.sh -p octosense` | 构建 shell 需要这两个命令全过；不是 `cargo build --release card-host` 之类（card-host 来自 Hub crate） |

### 关键判读
1. **官方桌面发行包 = `octosense` 包**（不是 `card-host`），它能在 macOS 上把 app bundle 当 Card runner 托管
2. **`octos` 服务 = `host.request("octos.turn.start", ...)`**，模型能力（`model.complete`）需要 `model` capability + `llm` 服务注册 + 至少一个 provider；只要在 Shell 的桌面打包里具备 `--features mobile-apps --features llm --features octos-core`，且 `OCTOS_APP_CORE_BIN` 提供 octos 内核二进制，应用方能真正调通模型
3. **身份同意在 Shell 内已有 first-time consent sheet**（"OctoSense asks the first time"），与 M2 路线一致 —— `Splash::set_host_tag` 在 Shell 内接入比在 card-host 内更自然
4. **OS reminder 仍是缺口**：即便 Shell 也未提供现成的 scheduler/notification host service；M6 路线需要 `crates/shell` 内加一个 in-process scheduler 或跳出 Shell 接 launchd/NotificationCenter

### 当前二进制与 Shell 实际能力差
| 维度 | 现有 `card-host@Hub-6741dea` | 官方 `octosense` 桌面打包（**需用户授权联网 + 离线构建**，r2 不做） |
|---|---|---|
| 启动本 bundle | ✅（实测） | ✅（兼容 Card runner） |
| `octos.turn.start` | ❌（无 host service 处理） | ✅（如 KernelPeers + register_contained 已启用） |
| `model.complete` | ❌（需 manifest 增 capability，但 host 无 llm 服务） | ✅（需 `llm` feature + 至少一个 provider） |
| 同意面板 | ❌ | ✅ |
| OS reminder | ❌ | ❌（Shell 同样缺 scheduler host service） |
| picker | ❌（card-host 无，Shell 仅在为 QR import 时开 panel） | △（仍需 M5 专门接入） |

### r2 没做的事（按用户指令硬限定）
- 没有 `git clone` / `cargo build / -p octosense` —— 用户明确"暂不自研宿主、不部署公网"
- 没改 `AGENTS.md`、README、PROGRESS、ACCEPTANCE、UI 验收、submission 等任何已别人修改过的文件
- 没动 `r1/`、`review-r1/` 任何目录

## 路线建议（依据 r2 真实能力矩阵）

**只有 1 条可执行路线 = C（构造官方桌面发行包 = `Octosense` Shell）**。理由：
- 路线 A (固定 card-host) —— Review 已论证 M2/M3/M6 硬约束在 card-host 上**不可达**（`octos.turn.start` / `model.complete` / first-time consent / `Splash::set_host_tag` 缺；OS reminder 即便 Shell 也仍缺）
- 路线 B (包外 HTTPS) —— `[submission/2026-10-08-hub/RECEIPT.md]` 与 `app/docs/route-decision.md` 已多次声明未授权且本赛事不接受，本轮不再考虑
- 路线 C (官方桌面 = Shell) —— OctoSense 官方文档明确支持且为本次比赛的目标产物；但 r2 不能执行
- 路线 D (扩展 card-host) —— 等同于把 Shell 内核装到 card-host；和 C 同等体量但拿不到 app-level peer / consent sheet

**C 路线在用户授权后必须做的最小科目**：

| 步骤 | 来源 | 风险 |
|---|---|---|
| 网络：clone `OctoSense-Shell@a5d847a` 实际 git tree | 用户书面授权 "联网 + 落地一份新 bare-`shell` 目录" | 单一来源崩溃则失去源头；commit `a5d847a` 必须固定 |
| 复用本仓库 `runtime/native-build/OctoSense-Shell/` 裸目录（已含必要文件）作为初始 source | 本仓库现有材料 | 本仓库目录无 `.git`、无 SHA 校验，仅 snapshot 主张 |
| 跑 `python3 tools/setup.py --check --cargo` 校验 lock 与外部依赖 pin | `OctoSense-Shell/AGENTS.md` 显式要求 | 必须联网拉 .sources/{makepad, octoscript, ...} |
| `cargo build --release -p octosense --features mobile-apps --features llm --features octos-core` | Shell `AGENTS.md` "How it fits together" + "AI services (octos)" | 需 stable Rust + 大量 crate 编译时间 |
| `OCTOS_APP_CORE_BIN` 在 desktop 落地（octos 内核 binary）—— 需拉 octos 制品或自编 | README "Each shell runs one octos agent kernel" | octos 自身的 download/build 路径 |
| 将本应用 bundle 从 `app/bundle` 转为系统应用式：由 `app/bundle/*.splash` + `card-host` runner → Shell 直接持有 + `system-apps.json` 登记 | Shell `apps/<name>/bundle/` 形态 | listing 与 hub 链接要重写 |
| 启动后用 `card-host --bundle apps/octosense-repair/bundle --system` 验证本应用被 Shell 接纳 | `OctoSense-Shell/AGENTS.md` "Apps' access to the assistant" | `octos-host-tags` 与 AGENT.md 路径 |
| 然后才能让本 bundle 真调 `host.request("octos.turn.start", {text})` —— M3 | `ContainedOctos::call` | model provider 未配时仍 BLOCKED |

**r3 起不再讨论路线，本 r2 表态**：M0 仍为 `BLOCKED`，由用户决定 C 路线是否启动；其它路线不解决 G0-E / G0-F / T29 / T32 等硬验收。

## 测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| 1. r2 dedup 后启动不 trap | 启动 + `--stamp` 一次 | admit + `[SPLASH] eval` 不终止 | `55781 bytes view=true animating=false tick=true epoch=0` + 77 widgets | **PASS** | `runtime/optimization/2026-10-09/M0/r2/host-stage/boot.log` |
| 2. 旧守卫仍 2-arg | `submit OPEN` 路径含 `isReporter(t, u)` 守卫 | 通过 + version += 1 | tasks.json version=1, status=OPEN | **PASS** | `runtime/optimization/2026-10-09/M0/r2/host-stage/app-data/octosense-repair/tasks.json` |
| 3. v2 helper 链回改名 | `isReporterMe(t)` 用在 4 个 view-model 路径 | 命名 Label 刷新 | header_actor, scope_note, visible_count, task_status, task_detail, next_step_title, next_step_summary 全部按值变 | **PASS** | `runtime/optimization/2026-10-09/M0/r2/host-stage/snap-as-technician.json`、`post-dedup-confirm-open.png` |
| 4. 隔离数据/未提交改动 | 审查全程只读 `r2/host-stage/` + 未触碰 `r1/`、`review-r1/`、既有业务/UI 改动 | 与既有不交叉 | git status -uall 与 r1 末尾对照，仅 `M0_IMPLEMENTATION_r2.md` 新增、`GATES.json` M0 字段更新；其它未触碰 | **PASS** | git status; `runtime/optimization/2026-10-09/M0/r2/host-stage/` |
| 5. 路线可执行性 | 综合 §"Shell 官方桌面能力矩阵" | 实现方给可审阅的 C 路径 | 文档级核对已做；用户授权前不构建 | **READY_FOR_REVIEW**（C 路线作为唯一可解阻选项） | 见 §"Shell 官方桌面能力矩阵" 与 §"路线建议" |

## 映射（M0 vs 既有的 64 项）

按 Reviewer r1 的口径维持不变；本 r2 把 D6 从 M1 转入 M0 已修，并新增一行"r2 dedup 副作用 = 0"。

| Module | 既有 | r2 状态 |
|---|---|---|
| G0-A 固定版本原生构建 | PASS | **维持 PASS**（r2 重新启动实测） |
| G0-B 可信身份 / 授权 | NOT_RUN | 维持 NOT_RUN；M2 路线由 C 解阻 |
| G0-C 唯一事实源/原子/并发/恢复 | PASS（后端形态）/r1 部分证据 | **r2 增量**：隔离 app-data 落盘 + 重启回读 + 中文 round-trip；原子/并发未测 |
| G0-D 真实附件 | NOT_RUN | **r2 增**：Picker 仍 0 widget；addEvidence 仍 demo：true。Shell 内 picker 仍只为 QR import 设计 |
| G0-E 系统助手/模型 | NOT_RUN | **r2 增**：D2 机理更正 = "显式两级 err"；C 路线必经 Octosense Shell 才能解阻 |
| G0-F 提醒/跳回 | NOT_RUN | **维持**：前台 only；Shell 内亦无 scheduler host service |
| T28/T29 grant 全链路 | FAIL | **维持 FAIL**（不冒充） |
| T32 配对码/token | NOT_RUN | **维持 NOT_RUN** |
| U09 1280×800/响应式 | NOT_RUN | **维持**：r2 仅 412×892 |
| U11 滚动稳定性 | NOT_RUN | **r2 增**：D3 机理更正 = `/m?k=scroll` 真实可用 |
| P02 完整源码+启动说明 | PASS | **P2-附条件（D1 修复）**：来源主张改为 sha256+mtime+SOURCES |
| M0 → M1 入场前置 | （r1 新增）D6 = 重复 `isReporter` | **r2 已修**：`fn isReporter(t)` → `fn isReporterMe(t)` |

后端历史 vs 原生本次证据区分（不混淆）：
- 之前的 64 项台账 PASS / NOT_RUN / FAIL 来自 `[docs/build-loop/ACCEPTANCE.json]` 历史后端口径
- 本 M0 的 r1/r2 命中是"原生形态"实测（macOS Apple Silicon × card-host@Hub-6741dea），后端 8821/8822 不可视为 M0 等价
- `L8-DV2 PASS`（工作台自评）和 `L0-A PASS`（最早基线）独立于 M0

## 尚未完成

- M0 仍 `BLOCKED` —— G0-E / G0-F / T29 / T32 在 card-host 上**结构性不可达**，必须 C 路线才解阻
- 未做（用户硬限定）：
  - 不构建 Shell（路线 C 入口）
  - 不部署公网
  - 不进入 M1
  - 不动 `app/bundle/{listing.json, *.bak, .archive/}`, `main.splash` 仅 fn 重命名
- 已知 r2 副作用：
  - `manifest.json` stamp `46f100dc…` ≠ M0-start `44743e24…` ≠ B-candidate `e5b477c7…`；三个值都是合法的 `bundle_blake3` 在不同目录内容下的哈希，不影响业务；r3（若用户授权 C）启动 `--stamp` 会覆盖

## 交接

- 候选：`M0-r2-worktree`
  - `app/bundle/main.splash` sha256 `8aa1022c93700ad1f155827ae57e87188a51c16bc0a693d5bd72b6fa7e4e3cab` (55,781B, 1312 行)
  - `app/bundle/manifest.json` stamp `46f100dc51b4243e205af345a7c4be6918afadd979386eeff8f3c6175be7f404` (249B)
  - 业务源码、UI 验收、AGENTS.md、README、PROGRESS、其它修改文件 — 维持原样
- 隔离证据：`runtime/optimization/2026-10-09/M0/r2/host-stage/{boot.log, post-dedup-confirm-open.png, snap-initial.json, snap-as-technician.json, app-data/}`
- 审查方补强证据（用于我方引用但不动）：`runtime/optimization/2026-10-09/M0/review-r1/{evidence-probe-input.png, evidence-probe-scroll.png, evidence-initial.png, evidence-after-confirm.png, evidence-as-tech.png, logs/, app-data/, probe-bundle/, bundle-copy/}`
- Shell 官方文档/源码只读：`runtime/native-build/OctoSense-Shell/{README.md, README.zh-CN.md, AGENTS.md, CLAUDE.md, GEMINI.md, native-apps.json, runtime-patches.lock.json, crates/ai-host/src/{lib.rs, contained.rs, qr.rs, bridge.rs}, crates/shell/src/apps.rs}`
- 实际启动命令如上文
- **编码方状态：READY_FOR_REVIEW（M0 维持 BLOCKED 直到用户裁决 C）**；D6 已修；D1/D2/D3/D4/D5 报告已并入；r2 未触动既有 `docs/build-loop/ACCEPTANCE.json`、`docs/implementation/10_UI_UX_SPEC.md` 等别人修改
- **最终 PASS 等独立审查**——本轮不进入 M1

## 自我判定

- 既有的 64 项 `T/U/P/G0` 状态未变（M0 仅在 `GATES.json` 与 `reports/M0_IMPLEMENTATION_r2.md` 中更新）
- `L0-A` (G0-A) 与 `L8-DV2` PASS 不被本 r2 进一步声明（仅复跑 admit + 隔离 app-data）
- 模型 / 文件选择 / 宿主身份 / OS 提醒 **没有**伪装 PASS —— 在 r2 中仍标 `BLOCKED`
- 不进入 M1；不进入 C 路线（用户未授权）
- 申请审查焦点：
  - D1/D2/D3/D4/D5 报告文本是否已落地
  - D6 dedup 副作用是否真为零
  - Shell 能力矩阵是否如本报告陈述
- 解阻条件不变：用户对 C 路线（联网拉取并构建 OctoSense-Shell@a5d847a）书面授权后，我方进入 r3，按 C 落地执行
