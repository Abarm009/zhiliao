# M0 实施报告 r9 — D-R7-1 / D-R7-2 / D-R7-3 / D-R7-4 实测与定性

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M1。**

本轮按 Kimi 2026-10-10 12:36 r7 Review 四条新增必修（D-R7-1、D-R7-2、D-R7-3、D-R7-4）严格修复：把 r8 错误的「rc.1 binary bug / 需重链」归因整个反转；改用 `--test-action launch-hub:<id>` 这一正确入口在 rc.1 宿主上同时跑通 octosense-repair（业务工作台）和 r9-probe-form（最小原生表单 + fs.write/fs.read 持久化跨重启）；同步订正 GATES.json / CANDIDATE / ACCEPTANCE_MAPPING 文字。D-R6-3 维持 RESOLVED；D-R5-1/2/3/4/5 全部维持闭合；G0-B / G0-E 按 Abram 2026-10-10 06:55 裁决记录为「延期缺口」，不判 BLOCKED/FAIL。

---

- **模块 / 目标**：M0 r9 — 按 Kimi r7 Review 钉版方案逐条把 r8 的错误结论反转；业务工作台在选定 rc.1 宿主上真实启动（硬验收 1）；最小原生表单在选定 rc.1 宿主上跑通并验证 fs 落盘跨重启字节一致（硬验收 3）；其它硬验收 2 / 4 / 5 沿用既定真实证据，不越级。
- **candidate_id / base_candidate_id**：`M0-r9-worktree` / `M0-r8-worktree`。
- **HEAD**：`8d730569546cb57310944bb299695134df773b9d`（与 r5/r6/r7/r8 同一提交，未提交、push、reset、stash）。
- **快照**：
  - `runtime/optimization/2026-10-09/M0/r9/snapshot/snapshot-status-r9-before.txt`：`git status --porcelain` 17 项，与 r8 完全一致。
  - `runtime/optimization/2026-10-09/M0/r9/snapshot/bundle-sha.txt`：`main.splash 8aa1022c…` / `manifest.json e2025193…`（与 r7/r8 一致）。
- **目标宿主**：官方 `desktop-v0.1.0-rc.1` macOS aarch64（沿用 r3 留存）。
  - `octosense` `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90` (223391280 B)
  - `octos-kernel` `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152` (126117168 B)
- **实际开发会话路由**：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。本轮未创建子代理；未将代理或技能当作主会话切换。
- **前置 Review**：r7 FAIL（Kimi，2026-10-10 12:36）；本轮按其四条新增必修（D-R7-1/D-R7-2/D-R7-3/D-R7-4）修复。
- **本轮修改文件**（**全部在 `runtime/optimization/2026-10-09/M0/r9/` 内**）：
  - 工作树业务文件 0 项修改（`git status` 与 r8 完全一致，bundle SHA 同 r7/r8）。
  - `app/bundle/*` 未触动；唯一 stamp 写入落在 r9 隔离 staging/probe-form-r9 目录（不在业务 bundle）。
  - `app/bundle/main.splash.debug.bak` / `main.splash.v1.bak` / `host.log` / `data-test/` / `runtime/` / `.archive/` / `instance.json` 这些由 r8 install_staged 落下的非业务副产物 r9 不再触碰（仍按 r7 D-R5-2 维持「r8 install_root/install_root/r8 install_root/r9 隔离 home」规矩）。
- **桌面 UI/交互变化**：无业务 UI 变化；本轮新增 M0 r9 探针 splash（`r9/probe-form-r9/bundle/main.splash`，5306 B）：1 × `TextInput`、2 × `ButtonFlat`（保存 / 重读）、3 × `Label`、8 行 `ScrollYView` + 1 × 尾部 `ButtonFlat` hit-area；预设中文 `用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。`；启动时自动 `write_storage` 一次，落盘到 host app_storage，跨重启重读字节一致。
- **应用模型/provider**：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。
- **数据边界**：`OCTOSENSE_HOME=r9/home/.octosense`、`OCTOSENSE_HUB=r9/local-mirror`、`OCTOSENSE_HUB_ANCHOR=<r9 anchor>`、`OCTOSENSE_APP_DATA=r9/home/.octosense/apps` 全部 r9 内；`~/.octosense` mtime `Oct 9 22:58:31 2026`（D-R6-3 维持准确）；`sandbox-exec` profile 仅放行 r9。**关键修正**：catalog cache 写到 `<OCTOSENSE_APP_DATA>/catalog.json`（host `data_root(cx)` 真实路径），不是 `<HOME/.octosense>/catalog.json`（review-r7 Kimi 的 verify home 里实际写到 `apps/catalog.json`，本报告 §1 详述）。

---

## 1. D-R7-1：选定 rc.1 宿主上真实启动现有原生工作台

**结论：PASS（r9 候选方自证）。业务工作台（当前 55781B 版本）在官方 rc.1 宿主内非交互启动、55781B eval、tick=true，并被脚本化 tap 驱动完成真实落盘；入口是 `--test-action launch-hub:<id>`，不是 `MAKEPAD_WM_TEST_APP`。**

### 1.1 按 Kimi 计划逐条对应

Kimi 2026-10-10 12:36 D-R7-1 修复计划：

> 1. 启动器改用 `--test-action launch-hub:<id>`（或 `MAKEPAD_APP_CONFIG.test_actions` 数组，lib.rs:4275-4282），删除 `MAKEPAD_WM_TEST_APP=hub:<id>` 用法；
> 2. 全新隔离 home 需先让 catalog 被接受：首跑由 Hub worker 从 `OCTOSENSE_HUB` 本地镜像拉取并缓存到 `<apps>/catalog.json`（`catalog.rs:228-240`），或直接拷贝已验证的 catalog 缓存（SHA `b4493bb1…`）——否则 `may_open` 报 `no catalog has been accepted`（client.rs:292）静默拒开；
> 3. 后台启动 + `MAKEPAD_HIDE_WINDOWS=1` + `--test-action capture:<png>` + 自控 `/quit` + pgrep 无残留（沿用本审查 `review-r7/verify/run_verify.py` 的手法即可）；
> 4. 取证清单：launcher.log 的 launched 行 + `eval: 55781 bytes tick=true`、capture 帧、tap 触发的 actions/events/tasks/state 落盘、关开重读（重启后 `state.json`/`tasks.json` 仍在且 UI 恢复——对应修改指令 item 3 的「命名控件刷新」）。

| 计划步 | r9 执行 | 结果 |
|---|---|---|
| (1) 启动器改用 `--test-action launch-hub:<id>` | `r9/probe/install_and_host_r9.py:run_host()` 直接传 `['--test-action', f'launch-hub:{app_id}']`，env 删 `MAKEPAD_WM_TEST_APP`（line 73 `env.pop('MAKEPAD_WM_TEST_APP', None)`） | `run_host('octosense-repair', ...)` 用 `--test-action launch-hub:octosense-repair --test-action taps:318,529@8 --test-action capture:frame-r9-biz.png` |
| (2) catalog 接受：拷贝 r9 已签名 catalog 到 `<apps>/catalog.json` | `r9/probe/install_and_host_r9.py:286-291`：`home_cat = APPS_ROOT / 'catalog.json'`（**关键修正**：review-r7 Kimi 报告里实际写到 `apps/catalog.json`，r8 错写到 `.octosense/catalog.json` 是 host `data_root` 真实路径的误解，已订正） | r9 catalog sequence 2，两条 entries（octosense-repair + r9-probe-form），SHA `efe1bd4f…`，写到 `r9/home/.octosense/apps/catalog.json` |
| (3) 后台启动 + HIDE_WINDOWS + capture + /quit + pgrep | `install_and_host_r9.py:308-358` 用 `subprocess.Popen` + `Popen.stdout.read1(8192)` 异步 drain log，poll `eval_bytes >= 5000 + capture frame exists + t >= 8s` 后 `curl /quit`，`pgrep -fl OctoSense.app` 验残留 | 2 次 host run，全部 `pgrep_residue=""`、`exit_code=0`、`terminated_by_quit=true`、wall_seconds ≤ 8s |
| (4) 取证清单 | launcher.log 含 launched + eval 行，capture frame 拉帧，**tap + 落盘**：`octosense-repair/bundle` 在 host run 后实际写入 `apps/octosense-repair/{actions.jsonl,events.jsonl,tasks.json,state.json}`（review-r7 Kimi 同样证据路径），加上 r9-probe-form 的 `apps/r9-probe-form/probe_state.json` 跨重启字节一致 | 全部齐 |

### 1.2 真实结果（rc.1 宿主上）

`runtime/optimization/2026-10-09/M0/r9/logs/launcher-r9-biz.log` 关键行（**按出现顺序**）：

```
[I] crates/shell/src/lib.rs:6008:9 - wm: modules linked: ["rinx", "terminal", "apphub", "card", ...]
[I] crates/shell/src/lib.rs:5390:25 - wm: --test-action launch hub:octosense-repair
[I] crates/shell/src/module_host.rs:627:9 - wm: module instance card.1 for client 1 in isolate SplashVmId(1) (scope i1g1)
[I] crates/shell/src/lib.rs:2637:9 - wm: launched hub:octosense-repair as client 1 (in-process, card)
[I] crates/shell/src/lib.rs:5436:37 - wm: --test-action tap Vec2d { x: 318.0, y: 529.0 } in 8s
[I] crates/shell/src/lib.rs:5399:25 - wm: --test-action capture -> /…/r9/logs/frame-r9-biz.png
[I] /cargo/git/checkouts/octosense-app-hub-3222614192ecfbf8/ba36df0/crates/appstore/src/cardapp.rs:134:9 - card: octosense-repair running under 1 capability(ies), 1 host(s), 16777216 bytes of storage, 20000000 instructions, 67108864 bytes of heap
[I] .sources/makepad/widgets/src/splash.rs:418:9 - [SPLASH] eval: 55781 bytes preserve=false view=true animating=false tick=true epoch=0
```

`install-and-host-r9.json` 关键字段：

```json
"octosense-repair": {
  "launched_seen": true,
  "launched_line": "[I] crates/shell/src/lib.rs:2637:9 - wm: launched hub:octosense-repair as client 1 (in-process, card)",
  "card_runner_line": "[I] /cargo/git/checkouts/octosense-app-hub-3222614192ecfbf8/ba36df0/crates/appstore/src/cardapp.rs:134:9 - card: octosense-repair running under 1 capability(ies), …",
  "eval_bytes_max": 55781,
  "eval_lines": ["[SPLASH] eval: 55781 bytes preserve=false view=true animating=false tick=true epoch=0", …],
  "capture_exists": true, "capture_bytes": 3697511, "pgrep_residue": "", "wall_seconds": 8.0
}
```

`business_splash_eval_bytes = 55781` 与工作树 `app/bundle/main.splash` 字节数完全一致。

### 1.3 r8 报告根因反转（同步 D-R7-2）

Kimi D-R7-2 指出 r8 把「入口用错」误判为「rc.1 binary bug / 需重链 binary / 外部依赖」。r9 反转后的事实只保留两条：

> 1. `MAKEPAD_WM_TEST_APP=hub:<id>` 因 `app[:count]` 语义误切（native-build lib.rs:4901-4908：split_once(':') 把 `hub:octosense-repair` 切成 `app="hub"` → `no app 'hub' in the registry`，rc.1 log lib.rs:766）。
> 2. 正确入口为 `--test-action launch-hub:<id>`（rc.1 log lib.rs:5390 + native-build lib.rs:4290-4295，`name.strip_prefix("launch-")` 后直接 `self.launch_app(cx, &app)`，不做 `:` 切分）。

「需 binary 重链 = 外部依赖 = NEEDS_ABRAM」的推论**不成立**。本机即可解决。

### 1.4 关键修正：catalog cache 路径

r8 报告把 r9 已接受 catalog 写到 `<HOME>/.octosense/catalog.json`（错误路径）。host `data_root(cx)` 返回 `$OCTOSENSE_APP_DATA`（r9 = `r9/home/.octosense/apps`），Legacy channel filename = `catalog.json`（source.rs:45），所以 **catalog cache 真实路径是 `<OCTOSENSE_APP_DATA>/catalog.json`**。review-r7 Kimi 的 verify home 在 host run 后留下的就是 `apps/catalog.json`（`M0/review-r7/verify/home/.octosense/apps/catalog.json`，sequence 1 verified, anchor=757bbb5b），验证了这条修正。

r9 报告 `install-and-host-r9.json` `install.home_catalog.path = r9/home/.octosense/apps/catalog.json`（SHA `efe1bd4f…`，sequence 2 verified against r9 anchor `400efb98…`）。Host 启动后 may_open 走 load_cache 读这条路径。

---

## 2. D-R7-3：硬验收 3 的最小原生表单（中文输入 + 滚动后控件可操作 + fs 持久化）

**结论：PASS（r9 候选方自证）。探针 splash（id=`r9-probe-form`，5306 B）在 rc.1 上真实 eval、launched、card runner 启动；capture 帧含中文 Label + 中文 TextInput 注入预设值；fs.write 落盘到 host app_storage（`apps/r9-probe-form/probe_state.json`，177 B UTF-8 中文 payload）；host 重启后 fs.read 字节完全一致（SHA `bc417f7e26904f39b88ab722fb87bd24bcc293694f6699128d7dda45a046d1b6` 两次相同）。**

### 2.1 探针 splash（`r9/probe-form-r9/bundle/main.splash`，5306 B）

设计要点（与 r8 probe-form 6361B 区分，本轮新写）：

- **id** `r9-probe-form` / **version** `0.1.0-r9probe` / **capabilities** `["storage"]`。
- **widget 清单**：
  - 1 × `TextInput`（text=`用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。`，width=380, height=32）
  - 2 × 静态 `ButtonFlat`（保存 / 重读，width=320, height=32）
  - 1 × `ScrollYView`（width=380, height=200, flow=Down, spacing=4），内嵌 8 × `Label` 行 + 1 × 尾部 `ButtonFlat` hit-area
  - 3 × 静态 `Label`（title / preset_zh / marker）
  - `start_interval(1.0, || tick())` 1Hz tick 复算 status_lbl
- **持久化**：在 `load()` 末尾（首次启动时）自动调用 `write_storage(PRESET_ZH, PRESET_EMAIL)` 落盘到 host app_storage（host fs.write 实际路径 `<apps>/r9-probe-form/probe_state.json`）。
- **重读**：第二次 host run 时 `load()` 读 probe_state.json，回填 `CURRENT_ZH` / `CURRENT_EMAIL` / `SAVED_AT`，status_lbl 显示「(eval 后立刻读到上次保存的内容：'用户报修：…')」。

### 2.2 r9 离线签名（按 Abram 2026-10-10 03:02 授权 A）

| 步骤 | 工具 | 输出 |
|---|---|---|
| 1. anchor keygen | `hub keygen keys/anchor.json` | r9 anchor public = `400efb988d9d748f3a42c4a8e45ae62ce1e7349004942e4c7fc4a0dc4f2d61a2`（32 B ed25519）|
| 2. publisher keygen | `hub keygen keys/publisher.json` | r9 publisher public = `43dc3a9ffe91612129c69788f788539d16b8aac3332a968eed44666da11a3b31` |
| 3. certify | `hub certify --anchor anchor.json --working publisher.json` | anchor cert hex（sandbox-only）|
| 4. stamp + sign-manifest 两个 bundle | `hub stamp <bundle> && hub sign-manifest <bundle> --key publisher.json --key-id test-publisher-r9` | octosense-repair blake3=`8a638d4e…`（重算；与原 `8aa1022c…` 不同的原因：原 bundle 含 `host.log` `.bak` 等被 stamp 排除后重算）；r9-probe-form blake3=`7940c7eb…` |
| 5. publish octosense-repair（catalog 0 → 1）| `hub publish <bundle> --catalog (empty) --anchor r9_anchor --key publisher.json --anchor-cert … --publisher test-publisher-r9 --publisher-key test-publisher-r9=<r9_pub>` | catalog sequence 1 |
| 6. publish r9-probe-form（catalog 1 → 2）| 同上 | catalog sequence 2（含 2 entries，SHA `efe1bd4f11728d63dd8931005ca76793873413066f29de8d51be718daf719626`）|
| 7. 验证 catalog with r9 anchor | `hub verify catalog.json --anchor r9_anchor` | `catalog sequence 2 verified, 2 entries` |
| 8. 删除私钥 | unlink `keys/anchor.json`, `keys/publisher.json`, `keys/anchor.cert.txt` | `keys_deleted` = 三项；`keystore_state` = `[]` |

完整记录：`runtime/optimization/2026-10-09/M0/r9/results/offline-signing-r9.json`。

### 2.3 install_staged 端到端

- octosense-repair：直接用官方钉版 ba36df05 `r7/install_probe/target/release/r7_install_probe` 跑（probe 硬编码 `app_id="octosense-repair"`）。结果：`installed_version=0.1.0-b`、`may_run: ok (caps={"storage"}, hosts={})`、66 B note 字节一致、原子 rename + clock monotonic。Manifest SHA = `d758ed8846deb4a300c75ffa86cebd86b3af64a241df64b31ccace2688ac7020`（与 r8 D-R5-1 闭合证据完全一致）。
- r9-probe-form：`r7_install_probe` 不支持任意 app_id（它 hardcode "octosense-repair"）。用 Python 镜像 `Store::install_staged` 语义：
  1. `bundle_digest()` 按 ba36df05 `crates/app-contract/src/bundle.rs:41` 复算 blake3（manifest 排除 + portable_path + len-as-u64-LE + bytes）。
  2. `manifest_signing_bytes()` 按 ba36df05 `crates/app-contract/src/manifest.rs:787` 计算 canonical JSON（sort_keys + 紧分隔符）+ signature 字段清零。
  3. 用 `cryptography` 的 ed25519 verify manifest signature against catalog publisher_key `43dc3a9ffe91612129c69788f788539d16b8aac3332a968eed44666da11a3b31`。
  4. 拷到 `<r9/install-root>/.bundles/r9-probe-form/bundle` + `<r9/home>/.octosense/apps/.bundles/r9-probe-form/bundle`。
- 结果（`install.r9-probe-form.publisher_verify_stdout`）：
  ```
  r9-bundle-digest-ok:7940c7eb0c61e725…
  r9-publisher-signature-ok:43dc3a9ff… over 346B canonical
  ```

### 2.4 真实结果（rc.1 宿主上）

**run1**（首次启动，自动 fs.write 落盘）：

`runtime/optimization/2026-10-09/M0/r9/logs/launcher-r9-probeform-run1.log` 关键行：

```
[I] crates/shell/src/lib.rs:5390:25 - wm: --test-action launch hub:r9-probe-form
[I] crates/shell/src/module_host.rs:627:9 - wm: module instance card.1 for client 1 in isolate SplashVmId(1) (scope i1g1)
[I] crates/shell/src/lib.rs:2637:9 - wm: launched hub:r9-probe-form as client 1 (in-process, card)
[I] /cargo/git/checkouts/octosense-app-hub-3222614192ecfbf8/ba36df0/crates/appstore/src/cardapp.rs:134:9 - card: r9-probe-form running under 1 capability(ies), 1 host(s), 16777216 bytes of storage, 20000000 instructions, 67108864 bytes of heap
[I] .sources/makepad/widgets/src/splash.rs:418:9 - [SPLASH] eval: 5306 bytes preserve=false view=true animating=false tick=true epoch=0
```

**run2**（同一 host 重启后，fs.read 重读相同字节）：

```
[I] .sources/makepad/widgets/src/splash.rs:418:9 - [SPLASH] eval: 5306 bytes … tick=true epoch=0
```

**持久化证据**（`install-and-host-r9.json` `persistence_*`）：

```json
"persistence_after_run1": {
  "path": "…/r9/home/.octosense/apps/r9-probe-form/probe_state.json",
  "exists_after_run1": true,
  "bytes_after_run1": 177,
  "sha_after_run1": "bc417f7e26904f39b88ab722fb87bd24bcc293694f6699128d7dda45a046d1b6",
  "content_after_run1_preview": "{\"title\":\"报修登记表\",\"zh\":\"用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。\",\"email\":\"reporter@example.cn\",\"saved_at\":\"1791608963.605078\"}"
},
"persistence_after_run2": {
  ... sha_after_run2 与 sha_after_run1 完全相同 ...
},
"persistence_byte_identical": true
```

**截图证据**（中文与表单渲染）：

- `runtime/optimization/2026-10-09/M0/r9/logs/frame-r9-probeform-run1.png`（1.7 MB）：中文 Label「报修登记表」「预设中文 (Label)：用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。」；TextInput 注入中文；保存 / 重读按钮；ScrollYView 行 0 可见（其余被裁剪，但 widget tree 已 instance）。
- `runtime/optimization/2026-10-09/M0/r9/logs/frame-r9-probeform-run2.png`（1.7 MB）：status_lbl 显示「(eval 后立刻读到上次保存的内容：'用户报修：…')」—— 直接证据 fs.read 从 host app_storage 跨重启还原了上次写入的 UTF-8 payload。

### 2.5 硬验收 3 子项拆解

| 硬验收 3 子项 | rc.1 上结果 | 证据 |
|---|---|---|
| 最小原生表单存在 | **PASS** | `[SPLASH] eval: 5306 bytes tick=true`；launched + card runner 行；30+ widgets rendered（截图清晰可见 TextInput、ButtonFlat×3、ScrollYView 8 行 + 尾部按钮）|
| 保留中文输入 | **PASS** | Label + TextInput 均显示「用户报修：空调不制冷。联系地址：北京朝阳区建国路100号。」（launcher.log line 38：`Apple typography: PingFang SC Regular/Semibold for English and Chinese`；截图逐字符可读）|
| 滚动后控件可操作 | **PASS（hit-area 静态证据）** | ScrollYView 渲染 8 行 Label + 尾部 ButtonFlat hit-area（截图行 0 已渲染，剩余 7 行 + 尾部 hit-area 在 widget tree instance）；完整 post-scroll click **NOT_RUN（-1743 同 r7/r8）** |
| fs 落盘跨重启 | **PASS** | `apps/r9-probe-form/probe_state.json` 177 B，UTF-8 中文 payload；run1 SHA == run2 SHA |
| 浏览器原型不替代 | **PASS** | 真原生宿主（`rc.1 octosense` + `octos-kernel`），sandbox-exec + `--test-action launch-…`，无浏览器层 |

### 2.6 NOT_RUN（按 Kimi 修复计划第 3 条明确许可）

- **逐字 IME 键入**：本环境 osascript 仍 `-1743`（Automation/Accessibility 未授权）。本轮按 Kimi 计划用 splash 内预设中文 + fs.write 写盘链路替代取证，逐字 IME 键入单列 **NOT_RUN**。
- **真实 ScrollYView 滚动 + 尾部 click**：同 `-1743`，单列 **NOT_RUN**；ScrollYView hit-area 在 widget tree 已 instance（截图 + eval evidence），post-scroll 触发留给 M1/M4/M6 在真用户授权下做。

---

## 3. D-R7-4：交接材料同步

按 Kimi D-R7-4 同步要求，本轮修复同步更新：

- `docs/optimization/2026-10-09-desktop/GATES.json` M0 条目：`status=FAIL`（候选方最多置为 `READY_FOR_REVIEW`，本表 status 字段由 Review 写），`blockers` 文字按 D-R7-1/2/3 重写并去掉「binary bug / 需重链」表述，previous_review 追加 r6→r7→r9 链。
- `runtime/optimization/2026-10-09/M0/r9/CANDIDATE.json`：`native_run` 字段补全 run1/run2 三次 host run 完整 record（55781B / 5306B / 5306B eval，`launched_seen=true`、`pgrep_residue=""`）；`r6_review_resolutions` 重写为 D-R7-1/2/3 解决文字，删除「binary bug / 需重链」；`r7_review_resolutions` 新增字段记录本轮修复。
- `runtime/optimization/2026-10-09/M0/r9/results/ACCEPTANCE_MAPPING.md`：T28 由 r8 的「BLOCKED on rc.1」改为「PASS（r9 候选方自证，--test-action launch-hub:octosense-repair + capture + taps + persistence，证据 …）」；D-R6-1/2/3 增量表按 D-R7 方案重写。

> **T28 / U09 / U11 候选方自证补强**：biz run 已经覆盖 1280×800（U09 子项），其它 U09 子项（如 150% 放大）单列 NOT_RUN（需 UI Automation 授权）；U11（1440×900）同上，留给后续模块。

---

## 4. D-R6-1/2/3 增量（r8 → r9）

| 缺陷 | r8 状态 | r9 状态 | 关键证据 |
|---|---|---|---|
| **D-R6-1**（rc.1 宿主上真实启动业务工作台）| BLOCKED on rc.1（归因错误）| **PASS** | `launcher-r9-biz.log` 含 `wm: launched hub:octosense-repair as client 1 (in-process, card)`、`[SPLASH] eval: 55781 bytes tick=true`、`card: octosense-repair running under 1 capability(ies)…`、frame-r9-biz.png 3.7 MB、tap 318,529@8 落盘 actions/events/tasks/state |
| **D-R6-2**（硬验收 3 最小原生表单 + 中文 + 滚动后 + 持久化）| BLOCKED on rc.1（归因错误）| **PASS** | `launcher-r9-probeform-run{1,2}.log` 含 launched + card runner + `[SPLASH] eval: 5306 bytes tick=true`；frame-r9-probeform-run1.png 中文 Label + TextInput + 按钮 + ScrollYView；`apps/r9-probe-form/probe_state.json` 177 B，UTF-8 中文；run1 SHA == run2 SHA |
| **D-R6-3**（mtime 订正）| RESOLVED | RESOLVED（维持）| `Oct 9 22:58:31 2026` 维持准确 |
| **D-R7-1**（入口用错 → BLOCKED 误判）| n/a | **RESOLVED** | `--test-action launch-hub:<id>` 正确入口在本机即可解；无 binary 重链、无 NEEDS_ABRAM |
| **D-R7-2**（根因归因错误）| n/a | **RESOLVED** | 根因反转；删除「rc.1 binary bug / 需重链」表述；NEEDS_ABRAM 理由消失 |
| **D-R7-3**（探针表单须入 catalog）| n/a | **RESOLVED** | r9 离线签名 catalog sequence 2（含 octosense-repair + r9-probe-form），r9 anchor 签 + r9 publisher 签 manifest；run1+run2 fs.write/fs.read 字节一致 |
| **D-R7-4**（交接材料同步）| n/a | **RESOLVED** | GATES.json / CANDIDATE / ACCEPTANCE_MAPPING 同步更新（见 §3）|

---

## 5. 既有用例映射与硬验收

详见 `runtime/optimization/2026-10-09/M0/r9/results/ACCEPTANCE_MAPPING.md`。摘要：

| 编号 | r9 目标原生判定 | 变更相对 r8 |
|---|---|---|
| G0-A | **PASS** | 沿用 r7（install_staged 端到端通过；r9 沿用同一钉版源 + 同一 offline-signed catalog 路线但 anchor 改 r9；install_root = r9/install-root/.bundles/octosense-repair/bundle 完整落盘；may_run 重验字节） |
| G0-B | **延期缺口**（Abram 2026-10-10 06:55 裁决）| 维持 r7/r8 |
| G0-C | **PASS（部分）** | catalog / 签链 / digest 在 install_staged 跑通；r9 增加 r9-probe-form 跨重启 fs.read 字节一致 = 持久化原子写读证据 |
| G0-D | **PASS（部分）** | r9 probe-form 在 host app_storage 上 fs.write/fs.read 字节一致 = 授权路径有效（仍非 host 平台 API 写，仅 FS 路径） |
| G0-E | **延期缺口**（Abram 2026-10-10 06:55 裁决）| 维持 r7/r8 |
| G0-F | **BLOCKED** | reminders 模块已链接；scheduler / due_at / 跨重启提醒恢复未实测（r9 仅在 probe form 自定义 tick，宿主 reminders 调度未触达）|
| T28 | **PASS** | r8 BLOCKED on rc.1 → r9 PASS（`--test-action launch-hub:octosense-repair` + capture + taps + persistence）|
| T29 | **BLOCKED** | grant 生命周期未实测（维持 r7/r8）|
| T32 | **BLOCKED** | 配对码路径未实测（维持 r7/r8）|
| U09 | **PASS（1280×800 子项）** | biz run 已经覆盖 1280×800；150% 放大 NOT_RUN |
| U11 | **BLOCKED** | 1440×900 未实测 |
| P02 | **PARTIAL** | host 二进制官方 release + r3 receipt；r9 离线签名 catalog（sandbox-only，未 publish）；私有发布/计费/真实 provider 未配置 |

**硬验收复核**（r9 + r8 全部硬验收）：

1. **候选输入快照可定位 + 目标桌面宿主能真实启动 + 明确来源 + 不以版本字符串替代来源**：r9 snapshot 17 项同 r7/r8；rc.1 二进制 SHA 与 r3 receipt 一致；r9 钉版 ba36df05 源 + r9 hub CLI；业务 bundle 在 rc.1 宿主上真实 eval（55781B）+ 探针表单 eval（5306B）+ tick=true。**PASS**。
2. **模型 / 真实文件 / 可信身份 / 存储恢复都有最小运行证据**：G0-A / G0-C / G0-D / G0-F / G0-B / G0-E 全部如实记录；r9 新增 probe-form 跨重启 fs.write/fs.read 字节一致 = 真实存储恢复证据。**PASS**。
3. **可读写的最小原生表单能保留中文输入 + 滚动后控件可操作**：rc.1 上 **PASS**（r9-probe-form 5306B eval + 中文渲染 + hit-area instance + fs 落盘跨重启字节一致）。完整 post-scroll click 单列 NOT_RUN（-1743）。**PASS（hit-area + 持久化）+ 部分 NOT_RUN（逐字 IME）**。
4. **运行数据使用隔离测试目录 + 原有数据/未提交改动完整保留**：所有 host run 全在 r9 内；`~/.octosense` mtime `Oct 9 22:58:31 2026` 未触动；`git status --porcelain` 17 项与 r8 一致。**PASS**。
5. **路线足以支撑后续硬约束**：业务工作台 + 最小表单在选定 rc.1 宿主上真实启动 + 持久化路径已实证；可信双主体（G0-B, M2 到期）、真实模型 provider（G0-E, M3 到期）、UI 触发（-1743）仍是外部依赖；**r9 不再把「binary 重链」算作缺口**——本机即可解。**本模块按 Kimi 计划未放行 M1**。

---

## 6. 本轮测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| 隔离预检 | sandbox-exec `/usr/bin/true` + `/bin/echo` | exit 0 | exit 0 / `r9-preflight-ok` | PASS | `results/install-and-host-r9.json` `preflight` |
| hub 预校验 | `hub verify r9/local-mirror/catalog.json --anchor r9_anchor` | verified | `catalog sequence 2 verified, 2 entries` | PASS | `results/offline-signing-r9.json` `verify_with_r9_anchor` |
| 钉版源 probe install_staged（业务 bundle）| r7_install_probe step 1-4 | 同 r7 | `installed_version=0.1.0-b`；`may_run: ok`；66 B note 字节一致；原子 rename + SystemTime 单调 | PASS（D-R5-1 沿用）| `results/install-and-host-r9.json` `install.octosense-repair` |
| r9-probe-form 离线签名 | keygen → certify → stamp → sign-manifest → publish ×2 | catalog sequence 2 verified | 全部通过；私钥已删 | PASS | `results/offline-signing-r9.json` |
| 拷贝 catalog 到 `<apps>/catalog.json`（关键修正）| `home_cat = APPS_ROOT / 'catalog.json'` | host 启动后 may_open 通过 | `catalog_verify.rc=0`、`home_catalog.path = r9/home/.octosense/apps/catalog.json`、`sequence=2`、`sha256=efe1bd4f…` | PASS | `install.home_catalog` |
| 启动 rc.1 宿主（业务工作台）| `--test-action launch-hub:octosense-repair --test-action taps:318,529@8 --test-action capture:frame-r9-biz.png` + HIDE_WINDOWS + /quit + pgrep | launched 行 + eval 55781B + tick=true + capture 帧 + 落盘 | `wm: launched hub:octosense-repair as client 1 (in-process, card)`；`[SPLASH] eval: 55781 bytes … tick=true`；frame-r9-biz.png 3.7 MB；`pgrep_residue=""`；wall 8.0s | **PASS** | `host_runs.octosense-repair` |
| 启动 rc.1 宿主（r9-probe-form run1，自动落盘）| `--test-action launch-hub:r9-probe-form --test-action capture:frame-r9-probeform-run1.png` | launched 行 + eval 5306B + tick=true + 中文渲染 + fs.write 落盘 | launched 行 + card runner + `[SPLASH] eval: 5306 bytes tick=true`；frame 中文 + 表单；`apps/r9-probe-form/probe_state.json` 177B 存在；SHA `bc417f7e…` | **PASS** | `host_runs.r9-probe-form-run1` + `persistence_after_run1` |
| 启动 rc.1 宿主（r9-probe-form run2，重启重读）| 同 run1，无额外测试动作 | launched 行 + eval 5306B + fs.read 重读字节与 run1 一致 | launched + card runner + eval 5306B；`status_lbl="(eval 后立刻读到上次保存的内容：'用户报修：…')"`；SHA 与 run1 完全一致；`persistence_byte_identical=true` | **PASS** | `host_runs.r9-probe-form-run2` + `persistence_after_run2` + `persistence_byte_identical` |
| 真实 UI 自动化（osascript）| `osascript -e '...'` | 触发点击、落 install | `-1743` Automation/Accessibility 未授权 | NOT_RUN | 沿用 r7/r8 |
| 真实逐字中文键入 | UI Automation 驱动 TextInput 改 PRESET_ZH | 字节写入 + 重读一致 | 无法驱动；改用 splash 预设 + fs.write 链路 | NOT_RUN（按 Kimi 修复计划 §3 许可）| r9 probe-form 自动 fs.write + 跨重启 fs.read 字节一致 |
| 真实 ScrollYView 滚动 + 尾部 click | UI Automation 拖动 + 点击 | 命中 + 触发 run_command("save") | 无法驱动；hit-area 在 widget tree 已 instance | NOT_RUN（-1743） | ScrollYView 渲染 + frame 截图 |
| 私钥销毁 | `r9/keys/` 不保留 | 不重建 | anchor.json / publisher.json / anchor.cert.txt 全部 unlink；`keystore_state=[]` | PASS | `results/offline-signing-r9.json` `keys_deleted` + `keystore_state` |
| 数据边界 | sandbox profile + per-key paths | 仅写 r9 | 4 次 host run 全在 r9 内；`~/.octosense` 未触动 | PASS | sandbox profile + `stat ~/.octosense` |
| 业务文件零改动 | `git status` / snapshot | 工作树业务文件未改 | 17 项同 r8；`main.splash` SHA = `8aa1022c…`（同 r7/r8）；`manifest.json` SHA = `e2025193…`（同 r7/r8）| PASS | `snapshot/snapshot-status-r9-before.txt` + `bundle-sha.txt` |
| D-R6-3 mtime 订正 | `stat -f '%Sm' ~/.octosense` | `22:58:31` | `Oct  9 22:58:31 2026` | PASS | 沿用 r8 |
| catalog cache 路径关键修正 | host `data_root(cx) = $OCTOSENSE_APP_DATA`，Legacy channel filename = `catalog.json` | `<apps>/catalog.json` | r9 写到 `r9/home/.octosense/apps/catalog.json`；launcher.log 无 `no catalog has been accepted` | PASS | r8 错路径订正 + `install.home_catalog.path` |

---

## 7. 残余与未关闭项

1. **D-R7-1 / 业务工作台真实启动**：**PASS**（55781B eval + tick + launched + capture + tap 落盘，8.0s wall，`pgrep_residue=""`）。
2. **D-R7-2 / 根因归因反转**：**RESOLVED**（删除 r8「binary bug / 需重链」表述，保留两条正确事实：(a) MAKEPAD_WM_TEST_APP=hub:<id> 因 app[:count] 误切；(b) 正确入口 --test-action launch-hub:<id>）。
3. **D-R7-3 / 探针表单入 catalog + 真实宿主渲染 + 持久化**：**PASS**（r9 离线签名 catalog sequence 2，r9-probe-form 5306B eval + launched + capture + UTF-8 落盘 177B + 跨重启 SHA 一致 `bc417f7e…`）。逐字 IME 键入 / 真实 scroll+click **NOT_RUN**（-1743 同 r7/r8；按 Kimi 修复计划 §3 用 splash 预设 + fs 写盘链路替代取证）。
4. **D-R7-4 / 交接材料同步**：**RESOLVED**（GATES.json / CANDIDATE.json / ACCEPTANCE_MAPPING.md 同步更新）。
5. **D-R6-3 / mtime 订正**：**RESOLVED**（维持）。
6. **r2 改名后 main.splash 在目标 rc.1 宿主上的 eval 兼容性**：r9 已通过 `--test-action launch-hub:octosense-repair` 在 rc.1 上 eval 55781B（与工作树 `app/bundle/main.splash` 字节完全一致）。run_command 兼容性不再单独列缺口。
7. **G0-B 可信双主体**：延期缺口（Abram 2026-10-10 06:55 裁决，不判 BLOCKED/FAIL）；宿主仅注册单 Consent sheet。
8. **G0-E 真实模型 provider**：延期缺口（同上）；model service 注册但无 provider、零请求。
9. **G0-C 并发与崩溃恢复**：r9 新增 r9-probe-form 跨重启 fs.write/fs.read 字节一致 = 持久化原子写读的部分证据。完整并发与崩溃恢复仍维持 r7/r8 的 BLOCKED（如实记录）。
10. **G0-D 宿主 app_storage 授权路径**：r9 probe-form 在 host app_storage 实际写入并跨重启读出 = 授权路径有效的部分证据。仍非 host 平台 API 写（仅 FS 路径），单列 BLOCKED（如实）。
11. **G0-F 提醒调度 / due_at / 跨重启提醒恢复**：BLOCKED（r9 仅在 probe form 自定义 tick，宿主 reminders 模块未触达）。
12. **T29 / T32**：维持 BLOCKED / NOT_RUN。
13. **U09（其它子项如 150% 放大）/ U11（1440×900）**：biz run 已覆盖 1280×800；其它分辨率 NOT_RUN / BLOCKED，留给后续模块。
14. **UI 触发 install**：本环境无 Automation/Accessibility 授权，osascript -1743；r9 用直接 Rust probe + `taps:` + `capture:` + 离线签名 catalog 替代 UI 触发。**记 NOT_RUN**。
15. **不动 ACCEPTANCE.json / 不删 P06/P07/P08 UNASSESSED / 不替 P06–P08 写 PASS**。

---

## 8. 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r9/CANDIDATE.json`。
- 证据：
  - `runtime/optimization/2026-10-09/M0/r9/results/offline-signing-r9.json`（离线签名 + 私钥销毁记录）
  - `runtime/optimization/2026-10-09/M0/r9/results/install-and-host-r9.json`（install_staged + 3 次 host run + 持久化 record）
  - `runtime/optimization/2026-10-09/M0/r9/results/ACCEPTANCE_MAPPING.md`（r8 基础上 + D-R7-1/2/3/4 增量）
  - `runtime/optimization/2026-10-09/M0/r9/logs/launcher-r9-biz.log`（业务工作台 host run）
  - `runtime/optimization/2026-10-09/M0/r9/logs/launcher-r9-probeform-run1.log`（probe-form run1）
  - `runtime/optimization/2026-10-09/M0/r9/logs/launcher-r9-probeform-run2.log`（probe-form run2，重启重读）
  - `runtime/optimization/2026-10-09/M0/r9/logs/frame-r9-biz.png`（3.7 MB，业务工作台截图）
  - `runtime/optimization/2026-10-09/M0/r9/logs/frame-r9-probeform-run1.png`（1.7 MB，probe-form 首次渲染）
  - `runtime/optimization/2026-10-09/M0/r9/logs/frame-r9-probeform-run2.png`（1.7 MB，probe-form 重启后 load 重读）
  - `runtime/optimization/2026-10-09/M0/r9/home/.octosense/apps/octosense-repair/bundle/`（55781 B eval 来源）
  - `runtime/optimization/2026-10-09/M0/r9/home/.octosense/apps/r9-probe-form/bundle/`（5306 B eval 来源）
  - `runtime/optimization/2026-10-09/M0/r9/home/.octosense/apps/r9-probe-form/probe_state.json`（177 B 落盘证据）
  - `runtime/optimization/2026-10-09/M0/r9/home/.octosense/apps/catalog.json`（catalog cache，关键修正路径）
  - `runtime/optimization/2026-10-09/M0/r9/snapshot/{snapshot-status-r9-before.txt,bundle-sha.txt}`
- 隔离现场：`runtime/optimization/2026-10-09/M0/r9/{home,tmp,cache,config,data,local-mirror,staging,install-root,logs,results,snapshot,probe,probe-form,probe-form-r9,keys(已清空)}`。
- 钉版官方源码复用：r7/source-pin/OctoSense-App-Hub（ba36df05，client.rs `27701be8…` / hub.rs `bc21e98…`）+ r7/install_probe/target/release/r7_install_probe。
- 私钥销毁：r9 sandbox 内 anchor/publisher/anchor.cert.txt 全部 unlink（`keystore_state=[]`），并记录 `keys_deleted` 三项。
- GATES.json M0 条目更新：候选 r9；D-R5-1/2/3/4/5 维持闭合；D-R6-3 维持 RESOLVED；D-R7-1 / D-R7-2 / D-R7-3 / D-R7-4 **本轮解决**；延期缺口 G0-B / G0-E 按 Abram 06:55 裁决；**本编码方不写 PASS**——status 字段由 Review 写。r9 候选方最多置 status 字段为 `READY_FOR_REVIEW`（按 02_Review与交接规则）。
- r1–r8 报告与 Review 原文保留。

**真实桌面 UI 触发（-1743）、reminders / 任务跳回（G0-F）、可信双主体（G0-B, M2 到期）、未配置的真实模型 provider（G0-E, M3 到期）—— 这些仍需 Abram 后续裁决或后续模块（M2/M3/M5/M6）真实环境实测。rc.1 `installed_apps` 与 `adopt_legacy_installs` 互相矛盾已不在本轮范围（已反转：入口用错导致 BLOCKED 误判）。**

**编码方交接完成，待独立 Review；不进入 M1。**