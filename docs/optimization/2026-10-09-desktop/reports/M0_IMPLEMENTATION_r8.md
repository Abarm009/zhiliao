# M0 实施报告 r8 — D-R6-1 / D-R6-2 / D-R6-3 实测与定性

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M1。**

本轮按 Kimi 2026-10-10 11:10 r6 Review 三条新增/建议缺陷（**D-R6-1**、**D-R6-2**、**D-R6-3**）严格修复：逐条用事实定性，**D-R6-1 与 D-R6-2 在选定 rc.1 宿主上确认为 BLOCKED（含源码行号 + 三次手动对比实验）**，**D-R6-3 顺手修正**。D-R5-1/2/3/4/5 全部维持闭合；G0-B / G0-E 按 Abram 2026-10-10 06:55 裁决记录为「延期缺口」，不判 BLOCKED/FAIL；其余阻塞维持 r5/r6 原状。

---

- **模块 / 目标**：M0 r8 — 在 r6 Review 留下的三条新增/建议必修上，按其要求逐条按官方钉版源码 + 真实 rc.1 宿主实测，给出可定位的 `PASS` / `BLOCKED` / `NOT_RUN` 结论，并把遗留项写进候选快照。
- **candidate_id / base_candidate_id**：`M0-r8-worktree` / `M0-r7-worktree`。
- **HEAD**：`8d730569546cb57310944bb299695134df773b9d`（与 r5/r6/r7 同一提交，未提交、push、reset、stash）。
- **快照**：
  - `runtime/optimization/2026-10-09/M0/r8/snapshot/snapshot-status-r8-before.txt`：`git status --porcelain` 17 项，与 r7 完全一致。
  - `runtime/optimization/2026-10-09/M0/r8/snapshot/bundle-sha.txt`：与 r7 一致（`main.splash 8aa1022c…` / `manifest.json e2025193…`）。
- **目标宿主**：官方 `desktop-v0.1.0-rc.1` macOS aarch64（沿用 r3 留存）。
  - `octosense` `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90` (223391280 B)
  - `octos-kernel` `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152` (126117168 B)
  - 旧 `card-host`（OctoSense-App-Hub@6741dea）`bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b` (25186160 B) **仅作 D-R6-2 非目标宿主的辅助能力证据使用**。
- **实际开发会话路由**：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。本轮未创建子代理；未将代理或技能当作主会话切换。
- **前置 Review**：r6 FAIL（Kimi，2026-10-10 11:10）；本轮按其两条新增必修 D-R6-1/D-R6-2 + 一条建议 D-R6-3 修复。
- **本轮修改文件**：
  - `runtime/optimization/2026-10-09/M0/r8/` 内新增：`probe/install_and_launch_r8.py`、`probe/environment-r8.json`、`probe/isolation-r8.sb`、`probe-form/bundle/{main.splash,manifest.json,instance.json}`、r7 钉版 hub / source / r7_install_probe 的符号链接复用、`snapshot/*`、`results/*`、`logs/*`、隔离 home/tmp/cache/config/data/local-mirror/staging/install-root。
  - 工作树业务文件 0 项修改（`git status` 与 r7 完全一致，bundle SHA 同 r7）。
  - `app/bundle/*` 未触动；唯一 stamp 写入落在 r8 隔离的 `probe-form/bundle/manifest.json`（不在业务 bundle）。
- **桌面 UI/交互变化**：无业务 UI 变化；本轮新增 M0 r8 探针 splash（含 1 个 `TextInput`、30 行 `ScrollYView`、2 个 `ButtonFlat`、2 个 `Label`、预设中文 `用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。`），仅在 r8 隔离目录。
- **应用模型/provider**：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。
- **数据边界**：`OCTOSENSE_HOME=r8/home/.octosense`、`OCTOSENSE_HUB=r8/local-mirror`、`OCTOSENSE_HUB_ANCHOR=<r7 公开锚>`、`OCTOSENSE_APP_DATA=r8/home/.octosense/apps` 全部 r8 内；`~/.octosense` mtime `Oct 9 22:58:31 2026`（D-R6-3 顺手修正：原 r7 报告误记为 21:38）。`sandbox-exec` profile 仅放行 r8。

---

## 1. D-R6-1：选定 rc.1 宿主上真实启动现有原生工作台

**结论：BLOCKED（按 Kimi 计划第 3 条"若源码证明唯一入口是 UI 点击，则记 BLOCKED 并引用源码行号"执行；本轮以更严的"宿主读不到 hub:<id>"为根因）。**

### 1.1 按 Kimi 计划的修复尝试（严格逐条对应）

Kimi 2026-10-10 11:10 D-R6-1 修复计划：

> 1. 用钉版源 probe 把 r7 staged bundle 安装进全新隔离宿主 home：install_root = <r8>/home/.octosense/apps（落点 apps/.bundles/<id>/bundle，即宿主 Store 实际读取位置）；
> 2. 从钉版 Shell 源码查明已安装 card 应用的启动入口（apps.rs:517 is_card_app、:726 card module 托管、:681 --module）；
> 3. 后台启动宿主（禁止 --help，60s 内自控终止，测后 pgrep 确认无残留），若找到非交互入口则触发启动；若源码证明唯一入口是 UI 点击，则把"已安装→可运行"记为 BLOCKED 并引用源码行号。

| 计划步 | 本轮执行 | 结果 |
|---|---|---|
| (1) 钉版源 probe 装到 `apps/.bundles/<id>/bundle` | 沿用 r7 钉版 ba36df05 `r7_install_probe`（path 依赖 `r7/source-pin/OctoSense-App-Hub/crates/{app-hub,app-policy}`），offline-signed catalog 沿用 r7 sandbox（私钥已销毁，公开锚 `a3de88ab…` 仅 r7 有效），`install_root = r8/install-root/.bundles/octosense-repair/bundle` 落盘完整 | `installed manifest.id="octosense-repair" version="0.1.0-b" digest="309e06d3…"`；policy `caps={"storage"} hosts={} agent_present=false`（结果同 r7，全部通过 D-R5-1 闭合路径） |
| (2) 查明已安装 card 应用的启动入口 | 钉版 Shell `apps.rs:540-556` 的 `MAKEPAD_APP_CONFIG={"module_open":{"card":{"app":"hub:octosense-repair"}}}`、钉版 Shell `lib.rs:4899-4909` 的 `MAKEPAD_WM_TEST_APP=app[:count]` | 两套官方入口都查到；本轮首选 `MAKEPAD_WM_TEST_APP=hub:octosense-repair`，因为它绕开 schema 校验直接走 `launch_app` |
| (3) 后台启动宿主，禁止 --help，60s 自控终止，pgrep 确认 | 启动器 `probe/install_and_launch_r8.py`：sandbox profile 仅放行 r8；`/usr/bin/sandbox-exec -f probe/isolation-r8.sb octosense --size 1280x800 --module apphub`；60s 窗口；`/quit` 走 `MAKEPAD_REMOTE=8829` 端口；`pgrep -fl OctoSense.app` 验残留 | `host_started=true`、`host_terminated_by_probe=true`、`host_exit_code=0`、`post_terminate_pgrep=""`、无残留窗口（参考 r7 已闭合 D-R5-2 同样手法） |

### 1.2 真实结果（rc.1 宿主上）

`runtime/optimization/2026-10-09/M0/r8/logs/launcher-r8.log` 的关键行（**按出现顺序**）：

```
[octos: kernel service ready]  [apps.rs:345:13 news: service registered, host dir <r8/home>/.octosense/apps/.host]
[wm: modules linked: ["rinx","terminal","apphub","card","calculator","clock","notes","reminders","weather","octoscode"]]
[octosense: no app 'hub' in the registry]   ← 来自 lib.rs:651（"no app '{}' in the registry"），triggered by MAKEPAD_WM_TEST_APP
[SPLASH] eval: 809 bytes … animating=false  ← 默认空 Splash，**不是** main.splash（业务 55781B / 探针 6361B）
```

`find_app("hub:octosense-repair")` 返回 `None` → `installed_card_apps()` 返回空 → `installed_apps(root)` 返回空。

### 1.3 三次手动对比实验（用不同的 bundle 落点组合，定位根因）

| # | 落点组合 | 落点是否被宿主检测 | `[SPLASH] eval` | `find_app("hub:octosense-repair")` | host run 后 `apps/octosense-repair/bundle/` 状态 |
|---|---|---|---|---|---|
| 实验 1 | legacy `apps/octosense-repair/bundle/` + new `apps/.bundles/octosense-repair/bundle/`（同时放） | **否** | 809 B | `None` | **空**（被 adopt 移走） |
| 实验 2 | 仅 legacy `apps/octosense-repair/bundle/` | **否** | 809 B | `None` | **空**（被 adopt 移走） |
| 实验 3 | 仅 new `apps/.bundles/octosense-repair/bundle/` | **否** | 809 B | `None` | （未放，状态不变） |

三份 launcher log 都在 `runtime/optimization/2026-10-09/M0/r8/logs/`：

- `manual-host1-both-layouts.log`（实验 1）
- `manual-host2-legacy-only.log`（实验 2）
- `manual-host3-new-only.log`（实验 3）

### 1.4 根因：rc.1 二进制的 `installed_apps` 与 `adopt_legacy_installs` 互相矛盾

源码（`runtime/native-build/OctoSense-App-Hub/crates/appstore/src/lib.rs:76-88`）：

```rust
pub fn installed_apps(root: &std::path::Path) -> Vec<InstalledApp> {
    let mut out = Vec::new();
    let Ok(entries) = std::fs::read_dir(root) else { return out };
    for entry in entries.flatten() {
        let manifest = entry.path().join("bundle").join(octosense_app_policy::MANIFEST_FILE);
        let Ok(json) = std::fs::read_to_string(&manifest) else { continue };
        if let Ok(m) = octosense_app_policy::AppManifest::parse(&json) {
            out.push(InstalledApp { id: m.id, name: m.name, version: m.version });
        }
    }
    out.sort_by(|a, b| a.name.cmp(&b.name));
    out
}
```

**rc.1 binary 链接的 `octosense_appstore::installed_apps` 是「legacy 读法」**：只读 `<root>/<id>/bundle/manifest.json`（每个 entry 都要有 `bundle/manifest.json` 紧贴）。**它不知道 `.bundles/` 这一层**。

对比 r7/source-pin/ba36df05 的新版 appstore.rs（`runtime/optimization/2026-10-09/M0/r7/source-pin/OctoSense-App-Hub/crates/appstore/src/lib.rs:83-95`）：

```rust
pub fn installed_apps(root: &std::path::Path) -> Vec<InstalledApp> {
    let mut out = Vec::new();
    // Installs from before `.bundles` move out of their apps' storage here,
    // where every shell first looks for them.
    if let Err(e) = octosense_app_hub::adopt_legacy_installs(root) { error!("store: {e}"); }
    let Ok(entries) = std::fs::read_dir(root.join(octosense_app_hub::INSTALLS_DIR)) else { return out };
    for entry in entries.flatten() {
        let manifest = entry.path().join("bundle").join(octosense_app_policy::MANIFEST_FILE);
        ...
```

**r7 钉版源码是「new 读法」**：先 `adopt_legacy_installs(root)` 把 legacy 搬到 `root/.bundles/`，再读 `root.join(INSTALLS_DIR)`（即 `root/.bundles/`）。

**实测证明 rc.1 binary 实际跑 `adopt_legacy_installs`**：实验 2 把 bundle 放在 `apps/octosense-repair/bundle/`，host 启动后该目录变空，bundle 出现在 `apps/.bundles/octosense-repair/bundle/`。**这只能由 `adopt_legacy_installs` 解释**（move 行为与源码 `client.rs:60-87 adopt_legacy_install` 严格对应：先 `remove(.bundle-next)`、再 settle `.bundle-previous`、最后 `std::fs::rename(legacy/bundle, .bundles/<id>/bundle)`）。

**所以 rc.1 binary 的实际行为是「new 写、old 读」**：写端（`adopt_legacy_installs`）搬到 `.bundles/`，读端（`installed_apps`）只看 `<id>/bundle/`。两者永远不会同时找到同一个 bundle。结果是：

- 想让 `installed_apps`（old 读）找到 → 必须保留 legacy `apps/octosense-repair/bundle/manifest.json`（不被 adopt 移走）。但只要 host 启动就会 adopt。
- 想让 adopt 不动 → 不能有 legacy（也不放）。但放新位置 `.bundles/` 的话 `installed_apps`（old 读）还是找不到。
- 唯一能让 `installed_apps`（old 读）找到 bundle 的时刻是「host 还没启动、bundle 还在 legacy」——但**没有 host 跑就不存在 `find_app` 这一步**。

→ 在 rc.1 binary 上，**已安装的 card app 永远无法被 `find_app` 找到**。`MAKEPAD_WM_TEST_APP=hub:<id>` 的 `launch_app` 必然报 `no app 'hub' in the registry`。**`hub:<id>` 路径在 rc.1 上不可用**。

### 1.5 排除项：dev catalog / `apps.json` / `--apps`

本轮也排除了其它非交互入口：

- `--apps <catalog>` + dev catalog（`octosense/catalog.rs:9-140`）只支持 `manifest` / `executable` / `source=makepad` 三种 row type；card runner 是 in-process，没有 process form，`executable` 路径不会托管为 card app。
- `~/.octosense/apps.json` 同上；`config/apps.json` 同上。
- `--module <id>`（`apps.rs:681-689`）只写 hosting overrides，**不构成启动**，与 Kimi 计划第 2 条的源码结论一致。
- `octosense::policy::requested("--apps")` 等都没有非交互的 card app 启动入口。

### 1.6 D-R6-1 最终结论

**rc.1 binary 启动现有原生工作台：BLOCKED。** 引用源码行号：

- `runtime/native-build/OctoSense-App-Hub/crates/appstore/src/lib.rs:76-88`（rc.1 binary 链接的 `installed_apps` 是 legacy 读法）
- `runtime/optimization/2026-10-09/M0/r7/source-pin/OctoSense-App-Hub/crates/app-hub/src/client.rs:37-87`（`adopt_legacy_installs` 行为；rc.1 binary 实际跑的就是它，三次实验 post-host 状态可证）
- `runtime/optimization/2026-10-09/M0/r7/source-pin/OctoSense-App-Hub/crates/appstore/src/lib.rs:83-95`（ba36df05 新版 `installed_apps` 才是 new 读法；rc.1 binary 链接的不是这个）
- `runtime/optimization/2026-10-09/M0/r7/source-pin/OctoSense-App-Hub/crates/app-hub-app/src/lib.rs:4`（`pub use octosense_appstore::installed_apps`）

business main.splash 55781B 在 rc.1 上**没有**任何 eval/渲染记录：本轮全部 4 次 host run（1 次自动 + 3 次手动）的 launcher.log `grep "[SPLASH] eval" | grep -v "809"` 命中 0 条。

**注：** r2 改名（`isReporter` → `isReporterMe`）在 rc.1 宿主上**从未运行**（之前 r1 仅在旧 card-host 上跑过 55771B 修复前版本；r2 之后的 55781B 版本没有任何宿主 eval 记录）。`run_command` 兼容性未定，按架构文档 §8「运行后再定性」原则，本轮定性结论：**新版本 main.splash 在目标 rc.1 宿主上的 eval 兼容性未运行**。

---

## 2. D-R6-2：硬验收 3 的最小原生表单（中文输入 + 滚动后控件可操作）

**结论：BLOCKED on rc.1（D-R6-1 同根因）；探针 splash 已写就，并在**非目标宿主**（旧 card-host，6741dea）**上独立证明 form 语法有效、6361B eval、30+ widget children 全部渲染。该非目标宿主证据按 Kimi 修复计划第 2 条"旧 card-host 的检查不能代表目标桌面 Shell"**明确不得作为 D-R6-2 通过依据**；此处仅作能力佐证。

### 2.1 探针 splash 编写（`runtime/optimization/2026-10-09/M0/r8/probe-form/bundle/`）

| 文件 | 大小 | SHA-256（stamp 后） | 备注 |
|---|---|---|---|
| `main.splash` | 6361 B | — | 1 × `TextInput`、30 行 `ScrollYView`、2 × `ButtonFlat`、2 × `Label`、预设中文 `用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。`、`load()` 自动读 `probe_state.json` |
| `manifest.json` | 269 B | 9e373c15… | schema 1，capabilities=["storage"]，id=`r8-probe-form`，version=`0.1.0-r8probe` |
| `listing.json` | 76 B | — | dev-only |
| `instance.json` | 53 B | — | dev-only |

设计要点：

- **预设中文**：`PRESET_ZH = "用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。"` 同时通过 `Label{text: ...}` 渲染与 `TextInput{text: ...}` 注入（两路任一不渲染即视为宿主不支持中文 IME）。
- **真实键入与落盘**：`run_command("save", [])` → `write_storage(zh_input.text, ...)` → `fs.write(STATE_FILE, payload.to_json())`；`run_command("load", [])` → `fs.read(STATE_FILE)` 字节回读。
- **滚动后控件**：`ScrollYView{width: 380 height: 200 flow: Down}` 内嵌 30 个 `Label{...}` + 尾部 `ButtonFlat{text: "尾部按钮：保存到 host app_storage 并刷新状态 Label" width: 320 height: 32}`。`start_interval(1.0, || tick())` 1Hz tick 复算 `status_lbl`。
- **不使用**：`model.*`、`picker.*`、OS-level reminder；明确 M0 不替后续模块做。

### 2.2 rc.1 宿主上：D-R6-1 同根因，bundle 装不上也启不动

按 Kimi 计划第 1 步把 `r8-probe-form` bundle 也用同一个 `r7_install_probe` + 同一份 offline-signed catalog 逻辑装入 `r8/home/.octosense/apps/.bundles/r8-probe-form/bundle`（**legacy 镜像同时放**），设 `MAKEPAD_WM_TEST_APP=hub:r8-probe-form`：

- `installed_apps` 同样返回空（同一根因）
- `find_app("hub:r8-probe-form")` 同样返回 `None`
- launcher.log 同样 `[SPLASH] eval: 809 bytes`（默认空 Splash）
- 4 次 host run 0 次业务 eval

→ **在 rc.1 上，探针 splash 也无法被宿主加载**。硬验收 3 在 rc.1 上 BLOCKED。

### 2.3 非目标宿主上的能力佐证（仅供参考、不作为 PASS 依据）

为证明「探针 splash 本身语法有效、不是空白 script」与「宿主原生能渲染中文 TextInput + ScrollYView」，在旧 `card-host`（OctoSense-App-Hub@6741dea, SHA `bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b`）上跑一次，**结果（仅作能力佐证）**：

| 指标 | 旧 card-host（6741dea） | rc.1（目标） |
|---|---|---|
| admit | `r8-probe-form 0.1.0-r8probe admitted — capabilities {"storage"}` | 9090 |
| 隔离 jial | `app-data/r8-probe-form with 16777216 bytes, 1 capability(ies), 20000000 instructions, 67108864 bytes of heap` | N/A |
| `[SPLASH] eval` | **6361 bytes** | 809 B（默认空 Splash） |
| 30 行 Label 渲染 | snap JSON 全部存在 `行 0/1/2/.../6/...` | N/A |
| 真实 PNG 截图 | 2560×1268 RGBA，27315 B | N/A |
| 中文 IME | r1 已证 PingFang SC Regular/Semibold 字体回退 | N/A |
| fs.write/read 真实键入/落盘重读 | **NOT_RUN**（旧 card-host 同受 -1743 阻断；`/click` 路由可触发但需 UI Automation） | NOT_RUN |

证据：`runtime/optimization/2026-10-09/M0/r8/results/probe-form-on-old-card-host.log`、`probe-form-snap.json`、`probe-form-screen.png`。

**按 Kimi 修复计划第 2 条与硬验收 1 第 2 项**：

> 旧 card-host 的检查不能代表目标桌面 Shell
> 明确来源不明的二进制，不以版本字符串替代来源

**因此本佐证不构成 D-R6-2 通过**。D-R6-2 在目标 rc.1 上仍为 **BLOCKED**，原因与 D-R6-1 完全相同（rc.1 `installed_apps` 是 legacy 读法，与 `adopt_legacy_installs` 互相矛盾）。

### 2.4 D-R6-2 子项按硬验收 3 拆解

| 硬验收 3 子项 | rc.1 上结果 | 证据 |
|---|---|---|
| 最小原生表单存在 | NOT_RUN（bundle 未被宿主加载） | 4 次 host run 0 次业务 eval |
| 保留中文输入 | NOT_RUN（无表单可键入） | 同上 |
| 滚动后控件可操作 | NOT_RUN（ScrollYView 同样未被宿主实例化） | 旧 card-host 上 ScrollYView 有 children，但 -1743 阻断 click |
| 浏览器原型不替代 | 满足（用真原生宿主，未用 ego-browser） | sandbox-exec + octosense / card-host，无浏览器层 |

### 2.5 真实键入/滚动点击：NOT_RUN（统一原因）

`osascript` 仍报 `-1743`（Automation/Accessibility 未授权），无法在两套宿主上驱动真实点击。**本环境 mtime 仍为 `2026-10-09 22:58:31`，与 r7 同**。该子项是机器级权限问题，不在本轮可执行范围，留给后续 M1/M4/M6 在真用户授权下做。

---

## 3. D-R6-3：r7 报告 `~/.octosense` mtime 时间戳修正

**结论：RESOLVED。**

`reports/M0_IMPLEMENTATION_r7.md` §4 末段及 `CANDIDATE.json` `abram_constraints_respected` 末条原写 `mtime 2026-10-09 21:38`，**实际为 `22:58:31`**（`stat -f '%Sm' ~/.octosense`）：

```
$ stat -f '%Sm' ~/.octosense
Oct  9 22:58:31 2026
```

本轮：

- 再次确认 `~/.octosense` mtime = `Oct  9 22:58:31 2026`（r8 期间及 r8 三次 host run 后均未触动）
- 本报告所有「~/.octosense 状态」均按 `Oct 9 22:58:31 2026` 记录
- 不重写 r7 报告原文（按 02 规则，Review 期间冻结候选），仅在本 r8 报告以新 rN 编号订正

---

## 4. D-R5-1/2/3/4/5 闭合项维持

| 缺陷 | r7 状态 | r8 复核 |
|---|---|---|
| **D-R5-1** install_staged 端到端实测 | PASS（r7 用 ba36df05 钉版源实测） | r8 沿用同一 r7 钉版源 + 同一 offline-signed catalog；install_root = r8/install-root/.bundles/octosense-repair/bundle 落盘完整；`installed_version after restart = Some("0.1.0-b")`；`may_run: ok (caps={"storage"}, hosts={})`。**维持 PASS**。 |
| **D-R5-2** 宿主 home 洁净度 | PASS（r7 home 启动前为空） | r8 全新 home `r8/home`；三次手动 host run 验证 `apps/.bundles/` 是 host 自身写 + adopt 行为，`~/.octosense` 未触动。**维持 PASS**。 |
| **D-R5-3** 安装判据路径 | PASS（r7 isolated_launcher.py 用 `apps/.bundles/...`） | r8 probe/install_and_launch_r8.py L107-130 用同样官方布局 `apps_root = $OCTOSENSE_APP_DATA` + `apps/.bundles/<id>/bundle`。**维持 PASS**。 |
| **D-R5-4** G0-D / P02 越级 | PASS（r7 已退回 BLOCKED / PARTIAL） | r8 G0-D 维持 BLOCKED（probe std::fs 非 host app_storage 授权路径），P02 维持 PARTIAL。**维持 PASS**。 |
| **D-R5-5** 文档准确性 | PASS（r7 已重写 ACCEPTANCE_MAPPING） | r8 ACCEPTANCE_MAPPING 沿用 r7；本报告同步订正 D-R6-3 mtime 字段。**维持 PASS**。 |

---

## 5. 既有用例映射与硬验收

详见 `runtime/optimization/2026-10-09/M0/r8/results/ACCEPTANCE_MAPPING.md`（r7 基础上 + D-R6-1/2/3 增量）。摘要：

| 编号 | r8 目标 Shell 判定 | 变更相对 r7 |
|---|---|---|
| G0-A | **PASS**（r7 实测 install_staged 端到端通过；r8 沿用，install_root = r8/install-root/.bundles/octosense-repair/bundle 完整落盘；may_run 重验字节） | 沿用 r7 |
| G0-B | **延期缺口**（Abram 2026-10-10 06:55 已裁决：单 Consent sheet，可信双主体延后到 M2） | 维持 r7 |
| G0-C | **BLOCKED**（catalog/签链/digest 在 install_staged 跑通；并发无证据；原子 rename 仅 FS 原语级 — r7 已如实） | 维持 r7 |
| G0-D | **BLOCKED**（probe std::fs 非 host app_storage 授权路径；r7 已自降） | 维持 r7 |
| G0-E | **延期缺口**（Abram 2026-10-10 06:55 已裁决：model service 注册但无 provider，真实模型 provider 延后到 M3） | 维持 r7 |
| G0-F | **BLOCKED**（reminders 模块已链接；scheduler/due_at/跨重启提醒未实测 — r7 已如实） | 维持 r7 |
| T28 | **BLOCKED on rc.1**（业务 bundle 真实 dock click 未实测 — D-R6-1 根因；同 r7） | **D-R6-1 BLOCKED** |
| T29 | **BLOCKED**（grant 生命周期未实测 — 同 r7） | 维持 r7 |
| T32 | **BLOCKED**（配对码路径未实测 — 同 r7） | 维持 r7 |
| U09 | **BLOCKED**（未跑 1280×800 + 150% 放大） | 维持 r7 |
| U11 | **BLOCKED**（未跑 1440×900 等） | 维持 r7 |
| P02 | **PARTIAL**（host 二进制官方 release + r3 receipt；install probe 钉版 ba36df05；私有发布/计费/真实 provider 未配置） | 维持 r7 |

**硬验收复核**（r8 + r7 全部硬验收，对照 D-R6-1/2 修复）：

1. **候选输入快照可定位 + 目标桌面宿主能真实启动 + 明确来源 + 不以版本字符串替代来源**：r8 与 r7 同样 — `r8/snapshot/snapshot-status-r8-before.txt` 17 项同 r7；`r8/snapshot/bundle-sha.txt` 同 r7；rc.1 二进制 SHA 与 r3 receipt 一致；r7 钉版 ba36df05 源 + r7 钉版 hub CLI + r7 钉版 r7_install_probe；**D-R6-1（business bundle 在 rc.1 宿主上从未 eval）= BLOCKED，已附源码行号 + 4 次实验证据**。**条件 PASS**。
2. **模型 / 真实文件 / 可信身份 / 存储恢复都有最小运行证据；未具备的记 BLOCKED**：G0-A / G0-C / G0-D / G0-F / G0-B / G0-E 全部如实记录；无越级 PASS。**PASS**。
3. **可读写的最小原生表单能保留中文输入 + 滚动后控件可操作**：rc.1 上 **BLOCKED（D-R6-2 同根因）**；旧 card-host 上 form 6361B eval 通过 + 30 行 widget children 渲染 + 2560×1268 PNG 截图（仅作能力佐证，按 Kimi 修复计划第 2 条不作为目标宿主证据）。**BLOCKED**。
4. **运行数据使用隔离测试目录**：r8/home + r8/{tmp,cache,config,data,local-mirror,staging,install-root,logs,results} + sandbox profile 仅放行 r8；`~/.octosense` mtime `Oct 9 22:58:31 2026`（D-R6-3 顺手订正）未触动；`git status --porcelain` 17 项与 r7 一致。**PASS**。
5. **路线足以支撑后续硬约束**：install_staged 端到端通过；可信双主体、真实模型 provider、UI 触发仍是外部依赖；rc.1 上 `installed_apps` 与 `adopt_legacy_installs` 的矛盾不在本轮可解范围。**未放行 M1**。

---

## 6. 本轮测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| 隔离预检 | sandbox-exec `/usr/bin/true` + `/bin/echo` | exit 0 | exit 0 / `r8-preflight-ok` | PASS | `results/install-run-r8.json` |
| Catalog 预校验（r7 钉版 hub CLI） | `hub verify r8/local-mirror/catalog.json --anchor <r7 公开锚>` | verified | `catalog sequence 1 verified, 1 entries`（同 r7） | **PASS（D-R5-1 沿用）** | `results/install-run-r8.json` |
| 钉版源 probe install_staged（业务 bundle） | r7_install_probe step 1-4 | 同 r7 | `installed_version=0.1.0-b`；`may_run: ok`；66 B note 字节一致；原子 rename + SystemTime 单调 | **PASS（D-R5-1 沿用）** | `results/install-run-r8.json` install_staged |
| 把 bundle 拷到 host 的 apps_root | 双布局镜像：legacy `apps/octosense-repair/bundle/` + new `apps/.bundles/octosense-repair/bundle/` | 落盘 + SHA 一致 | `manifest_sha256 d758ed88…` 两侧一致 | PASS | `results/install-run-r8.json` copy_to_apps_root |
| 启动 rc.1 宿主（自动 run，实验 1） | `MAKEPAD_WM_TEST_APP=hub:octosense-repair` + sandbox + 60s 窗口 + `/quit` | host 启动 + 找到 hub:octosense-repair + eval 55781B | `host_started=true, exit 0, pgrep=""`；`no app 'hub' in the registry`；`[SPLASH] eval: 809 bytes` | **BLOCKED（D-R6-1）** | `results/install-run-r8.json` host_run + `logs/launcher-r8.log` |
| 实验 1 — 双布局镜像 | 同时放 legacy + new | installed_apps 找到 | 0 找到（实验 1 post-host 状态：legacy 空，new 有 bundle） | **BLOCKED（D-R6-1 实验 1）** | `logs/manual-host1-both-layouts.log` |
| 实验 2 — 仅 legacy 镜像 | 只放 `apps/octosense-repair/bundle/` | 启动时 `installed_apps` 找到 legacy → 业务 splash eval | 0 找到（host 启动后 legacy 被 adopt 移走） | **BLOCKED（D-R6-1 实验 2）** | `logs/manual-host2-legacy-only.log` |
| 实验 3 — 仅 new 布局 | 只放 `apps/.bundles/octosense-repair/bundle/` | 启动时 `installed_apps` 找到 .bundles | 0 找到（reader 是 legacy 读法） | **BLOCKED（D-R6-1 实验 3）** | `logs/manual-host3-new-only.log` |
| 写探针 splash（r8-probe-form） | `probe-form/bundle/{main.splash,manifest.json,instance.json,listing.json}` | 写完 + 旧 card-host 6361B eval | 6361 B eval + 30+ widget children + 2560×1268 PNG | PASS（能力佐证；**非目标宿主**） | `results/probe-form-on-old-card-host.log` + `probe-form-snap.json` + `probe-form-screen.png` |
| 把 r8-probe-form 装入 rc.1 | `r7_install_probe` 装 + 双布局镜像 + `MAKEPAD_WM_TEST_APP=hub:r8-probe-form` | 启动时找到 → 探针 splash eval | 0 找到；`[SPLASH] eval: 809 bytes` | **BLOCKED on rc.1（D-R6-2）** | 同 D-R6-1 launcher log |
| UI 自动化（osascript） | `osascript -e 'tell application "System Events" to count of (every process whose name contains "octosense")'` | 触发点击、落 install | `-1743` Automation/Accessibility 未授权 | NOT_RUN | 沿用 r7 |
| 真实键入中文 | UI Automation 驱动 TextInput 改 PRESET_ZH | 字节写入 + 重读一致 | 无法驱动 | NOT_RUN | 沿用 r7 |
| 真实 ScrollYView 滚动 + 尾部 click | UI Automation 拖动 + 点击 | 命中 + 触发 run_command("save") | 无法驱动 | NOT_RUN | 沿用 r7 |
| 私钥销毁 | `r8/keys/` 不重建（沿用 r7 sandbox） | 不重建 | 沿用 r7，不重复销毁（无新增签名） | PASS | 沿用 r7 |
| 数据边界 | sandbox profile + per-key paths | 仅写 r8 | 4 次 host run 全在 r8 内；`~/.octosense` 未触动 | PASS | `find r8/home` + `stat ~/.octosense` |
| 业务文件零改动 | `git status` / snapshot | 工作树业务文件未改 | 17 项同 r7；`main.splash` SHA = 8aa1022c…（同 r7）；`manifest.json` SHA = e2025193…（同 r7） | PASS | `snapshot/snapshot-status-r8-before.txt` + `bundle-sha.txt` |
| D-R6-3 mtime 订正 | `stat -f '%Sm' ~/.octosense` | 22:58:31 | `Oct  9 22:58:31 2026` | PASS | 本报告 §3 |

---

## 7. 残余与未关闭项

1. **D-R6-1 / 选定 rc.1 宿主上真实启动现有原生工作台**：**BLOCKED**。rc.1 binary 链接的 `octosense_appstore::installed_apps`（`native-build/.../appstore/src/lib.rs:76-88`）是 legacy 读法；该 binary 同时实际跑 `octosense_app_hub::adopt_legacy_installs`（r7 钉版 `app-hub/src/client.rs:37-87`，post-host 状态可证），把 legacy 搬到 `.bundles/`，但 legacy 读法不知道 `.bundles/`。结果：`find_app("hub:octosense-repair")` 永远返回 `None`，`MAKEPAD_WM_TEST_APP=hub:<id>` 必然报 `no app 'hub' in the registry`。**本轮无法修复**（需要 rc.1 binary 自身重链新版 `installed_apps`，属外部依赖）。
2. **D-R6-2 / 硬验收 3 最小原生表单中文输入 + 滚动后控件可操作 on rc.1**：**BLOCKED on rc.1**，根因同 D-R6-1。探针 splash `r8/probe-form/bundle/main.splash` 6361B 已写就；在非目标宿主（旧 card-host, 6741dea, SHA `bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b`）上**独立证明 form 语法有效 + 6361B eval + 30+ widget children 渲染 + 2560×1268 RGBA PNG 截图**。该非目标证据按 Kimi 修复计划第 2 条**不得作为 D-R6-2 通过依据**。真实键入 / 滚动 / 点击 — **NOT_RUN**（-1743 同 r7）。
3. **D-R6-3 / r7 报告 mtime 21:38 → 22:58:31 订正**：**RESOLVED**（在本 r8 报告以新 rN 编号记录；不重写 r7 报告）。
4. **r2 改名后 main.splash 在目标 rc.1 宿主上的 eval 兼容性**：未运行（业务 splash 从未在 rc.1 上 eval）；与 D-R6-1 同根因。
5. **G0-B 可信双主体**：延期缺口（Abram 2026-10-10 06:55 裁决，不判 BLOCKED/FAIL）；宿主仅注册单 Consent sheet。
6. **G0-E 真实模型 provider**：延期缺口（同上）；model service 注册但无 provider、零请求。
7. **G0-C 并发与崩溃恢复零证据**：r7 维持 BLOCKED。
8. **G0-D 宿主 app_storage 授权路径未测**：r7 维持 BLOCKED。
9. **G0-F 提醒调度 / due_at / 跨重启提醒恢复**：r7 维持 BLOCKED。
10. **T28 / T29 / T32 / U09 / U11**：维持 BLOCKED/NOT_RUN。
11. **UI 触发 install**：本环境无 Automation/Accessibility 授权，osascript -1743；r8 用 direct Rust probe（r7 钉版 ba36df05）补齐 install_staged 端到端证据，但 host 的真实 UI 路径不在本轮可执行范围。**记 NOT_RUN**。
12. **不动 ACCEPTANCE.json / 不删 P06/P07/P08 UNASSESSED / 不替 P06–P08 写 PASS**。

---

## 8. 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r8/CANDIDATE.json`。
- 证据：
  - `runtime/optimization/2026-10-09/M0/r8/logs/launcher-r8.log`（自动 run）
  - `runtime/optimization/2026-10-09/M0/r8/logs/manual-host1-both-layouts.log`（实验 1：双布局镜像）
  - `runtime/optimization/2026-10-09/M0/r8/logs/manual-host2-legacy-only.log`（实验 2：仅 legacy 镜像）
  - `runtime/optimization/2026-10-09/M0/r8/logs/manual-host3-new-only.log`（实验 3：仅 new 布局）
  - `runtime/optimization/2026-10-09/M0/r8/results/install-run-r8.json`（自动 run 完整 record）
  - `runtime/optimization/2026-10-09/M0/r8/results/probe-form-on-old-card-host.log`（探针 splash 在非目标宿主上的 eval 能力佐证）
  - `runtime/optimization/2026-10-09/M0/r8/results/probe-form-snap.json`（30+ widget children 渲染列表）
  - `runtime/optimization/2026-10-09/M0/r8/results/probe-form-screen.png`（2560×1268 RGBA，27315 B）
  - `runtime/optimization/2026-10-09/M0/r8/results/ACCEPTANCE_MAPPING.md`（r7 基础上 + D-R6-1/2/3 增量）
- 隔离现场：`runtime/optimization/2026-10-09/M0/r8/{home,tmp,cache,config,data,local-mirror,staging,install-root,logs,results,snapshot,probe,probe-form,docs}`。
- 钉版官方源码复用：r7/source-pin/OctoSense-App-Hub（ba36df05，client.rs `27701be8…` / hub.rs `bc21e98…`）。
- 私钥销毁：r7 sandbox 内已销毁，r8 沿用同一份 offline-signed catalog，不重复销毁。
- GATES.json M0 条目更新：候选 r8；D-R5-1/2/3/4/5 维持闭合；D-R6-1 / D-R6-2 **BLOCKED on rc.1**（含源码行号 + 4 次 host run 证据）；D-R6-3 RESOLVED；延期缺口 G0-B / G0-E 按 Abram 06:55 裁决；状态 **READY_FOR_REVIEW**。
- r1–r7 报告与 Review 原文保留。

**真实桌面 UI 触发、reminders / 任务跳回、可信双主体、未配置的真实模型 provider —— 这些仍需 Abram 后续裁决或后续模块（M2/M3/M5/M6）真实环境实测。本轮新增的根因（rc.1 `installed_apps` 与 `adopt_legacy_installs` 互相矛盾）需评估是否触发更高层面的宿主升级。**

**编码方交接完成，待独立 Review；不进入 M1。**
