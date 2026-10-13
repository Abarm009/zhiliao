# M0 实施报告 r5 — D-R4-1 至 D-R4-5 修复与真实启动重出

**状态：BLOCKED；编码方交接，等待独立 Review，不进入 M1。**

本轮针对 r4 Review（Kimi，2026-10-09 22:35 CST）的五条缺陷逐项修复并重出证据。本环境允许隔离启动并能拉起宿主 5 服务/10 模块；本地 catalog / install_staged 受用户禁止 publish/签名约束阻塞；可信双主体、文件选择/原子恢复/提醒三类能力依赖 UI 交互与宿主账户授权未在本轮实测。**承认 r4 的"环境不允许隔离启动"判断是错的；当前环境实际可行；本轮在同一环境复跑 `--launch` 把 host_started=true 与 launcher.log 写入 §1。**

- 模块 / 目标：仅 M0 r5；修复 `M0_REVIEW_r4.md` D-R4-1、D-R4-2、D-R4-3、D-R4-4、D-R4-5。
- candidate_id / base_candidate_id：`M0-r5-worktree` / `M0-r4-worktree`；已提交 B 包另标 `B-candidate-8d73056`。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；未提交、push、reset、stash。
- 快照与差异：`runtime/optimization/2026-10-09/M0/r5/snapshot/`。`status-before.txt` 17 项与 r4 一致，未触动任何业务文件。
- 目标宿主：官方 `desktop-v0.1.0-rc.1` macOS aarch64；具体来源、固定 SHA 与哈希与 r4 一致；只读复用 r3 已校验的 `app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`。
- 实际开发会话路由：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。按本轮串行约束未创建子代理；未将代理或技能当作主会话切换。
- 前置 Review：M0 无前置模块；r4 BLOCKED；本轮修复其 5 条缺陷并保留历史 r1–r4 报告原文。
- 修改文件：新增本报告、r5 隔离证据/探针（隔离脚本、launcher.log、local-install-attempt.json、dev-apps.json）；只更新 `GATES.json` 的 M0。**未触动 `app/bundle/main.splash` 与 `app/bundle/manifest.json`**。
- 桌面 UI/交互变化：无；r5 只跑宿主 launch 与 apps.json 解析，没有改写业务 splash。
- 接口 / 数据迁移：无；没有重打正式 bundle stamp、没有动旧 B 包。
- 应用模型/provider：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。
- 覆盖范围：D-R4-1/2 同环境复跑 `--launch`、D-R4-3 本地 catalog 路径最小复现、D-R4-4 双主体阻塞证据、D-R4-5 文件/原子/提醒实测阻塞、64 项 ACCEPTANCE 映射保留、隔离数据边界全部落 r5。
- 置信度：D-R4-1/2 修复 **高**（host_started=true、launcher.log 关键行同 r4 复现）；D-R4-3 install_staged 阻塞 **高**（源码证据 + r5 本地 catalog 缺失）；D-R4-4/D-R4-5 阻塞 **高**（launcher.log 仅证服务/模块链接，未触 UI）。

## 1. D-R4-1 / D-R4-2 修复：同环境复跑 `--launch`

承认 r4 报告 "sandbox_apply: Operation not permitted (exit 71)" 在本环境不可复现；当前沙箱允许叠加宿主写隔离并能真实拉起宿主。

复现命令：

```sh
python3 -B runtime/optimization/2026-10-09/M0/r5/probe/isolated_launcher.py
```

执行器（`r5/probe/isolated_launcher.py`）相对 r4 调整：
- 默认 30 秒诊断窗口（`--short` 仍可用，回落到 15 秒）。
- 显式生成 `dev-apps.json`：合法 catalog（`id/label/manifest/package/bin/policy`），指向业务 bundle 当前未提交 v2 工作树。
- 把 launcher.log 与 local-install-attempt.json 同时落到 `logs/`。
- 提取关键行（kernel ready / llm profile / model service / Consent / modules linked / `[SPLASH] eval` / PingFang SC / apphub launch）写入 JSON，便于审查者无需打开日志即可核验。

复跑结果（直接抄自 `r5/logs/local-install-attempt.json`）：

| 项 | 值 |
|---|---|
| `preflight_command`（`/usr/bin/sandbox-exec -f isolation.sb /usr/bin/true`） | exit 0；stderr 空 |
| `preflight_echo_command`（`/bin/echo r5-preflight-ok`） | exit 0；stdout `r5-preflight-ok` |
| `host_started` | **true** |
| `host_exit_code` | 0 |
| `host_terminated_by_probe` | true（30 s 后主动回收） |
| `launcher_log_size` | 7287 B |
| `launcher_log_lines` | 44 |
| `install_staged_executed` | false（见 §3） |

launcher.log 关键行（同 r4 复现，r5 落 `r5/logs/launcher.log`）：

```text
[I] crates/shell/src/app_storage/lifecycle.rs:442:9 - app storage: Mail's secrets stay in its service folder: ...r5/home/.octosense/secrets/os.mail: Operation not permitted (os error 1)
[I] crates/ai-host/src/lib.rs:312:13 - octos: kernel service ready (starts on first use), core dir Some(".../r5/home/.octosense/octos-home/.octos")
[I] crates/ai-host/src/lib.rs:395:13 - llm: provider profile under .../r5/home/.octosense/octos-home/.octos
[I] crates/ai-host/src/lib.rs:429:5 - model: service registered (one-shot calls; granted apps only)
[I] crates/ai-host/src/lib.rs:366:9 - octos: contained apps' service registered (Consent)
[I] crates/shell/src/lib.rs:6008:9 - wm: modules linked: ["rinx", "terminal", "apphub", "card", "calculator", "clock", "notes", "reminders", "weather", "octoscode"]
[I] crates/shell/src/desktop_app.rs:207:9 - wm: desktop style octosense applied to 0 clients and 0 modules
[I] crates/shell/src/lib.rs:6040:13 - octosense: background app prewarming disabled
[I] crates/shell/src/apps.rs:345:13 - news: service registered, host dir .../r5/home/.octosense/apps/.host
[I] crates/shell/src/apps.rs:274:9 - glance: the notice service answers ["os.photos", "os.maps", "os.ai-providers", "os.youtube"] (no service of their own)
[I] /cargo/git/checkouts/rinx-cf0dcd4e7b4d3fa8/4b89097/crates/article-makepad/src/apple_fonts.rs:85:5 - Apple typography: PingFang SC Regular/Semibold for English and Chinese; bundled fallback retained
```

业务 bundle 解析：r5 把 `--apps` 指向合法 catalog。`octosense/src/octosense/catalog.rs:9-140` 的 `parse_catalog` 对每行做严格字段与必填校验；r5 dev-apps.json 通过 schema 校验（id `octosense-repair`、label `知了 · 维修协作`、manifest 指向 `app/bundle/manifest.json`、package/bin `octosense-repair`、policy `new`）。当前业务 bundle 是脚本包不是 Cargo crate，host 若按 manifest 路径去 `cargo run --manifest-path <manifest.json>` 会触发 r3 已记录的 `error: the manifest-path must be a path to a Cargo.toml file`；本轮 `--apps` 路径让 catalog 解析合法但未触发 dock click → 业务 splash bundle **未在本轮 launch**。这与 r3 同一代码路径、不重新判定 D8 路线。

按 launcher.log 重新确认能力范围：

| 能力 | 现状 |
|---|---|
| kernel 服务 ready | ✓（lib.rs:312） |
| llm provider profile 路径已读 | ✓（lib.rs:395），profile 未配置 → 模型 service **注册成功但无可用 provider**（同 r3） |
| model service（one-shot） | ✓（lib.rs:429）；未发起任何模型请求 |
| contained apps Consent service | ✓（lib.rs:366），默认 subject 已注册；本环境无第二个真实认证 subject（见 §4） |
| modules linked | ✓：rinx / terminal / apphub / card / calculator / clock / notes / reminders / weather / octoscode |
| apphub 进程内 client 1 启动 | ✓（module_host.rs:627、lib.rs:2637） |
| Splash 渲染 | ✓：`[SPLASH] eval: 809 bytes preserve=false view=true animating=false tick=false epoch=0` |
| PingFang SC 字体 | ✓：`PingFang SC Regular/Semibold for English and Chinese`（rime 用于 CJK） |

**结论**：D-R4-1 / D-R4-2 已在同一环境复跑并验证为当前事实。R4-B01（"环境阻断"）解除；不再以此为由 BLOCKED。

## 2. 数据边界与现场保留

`r5/probe/isolation.sb` 沿用 r4 的写入白名单 + 网络外发拒绝，仅把根目录从 r4 改到 r5。`environment.json` 显式列出 `HOME / CFFIXED_USER_HOME / TMPDIR / XDG_CACHE_HOME / XDG_CONFIG_HOME / XDG_DATA_HOME / OCTOSENSE_HOME / OCTOS_HOME / RINX_DATA_DIR / MTL_SHADER_CACHE_DIR / OCTOSENSE_HUB`，全部限制在 `runtime/optimization/2026-10-09/M0/r5/**`；`isolated_launcher.py` 启动前断言每条路径解析后位于 r5 之内。

启动后产生的文件：
- `runtime/optimization/2026-10-09/M0/r5/home/.octosense/...`（OCTOSENSE_HOME，host 自身沙箱内）。
- `runtime/optimization/2026-10-09/M0/r5/home/octos-home/.octos`（OCTOS_HOME，kernel profile 路径）。
- `runtime/optimization/2026-10-09/M0/r5/cache/metal`（MTL_SHADER_CACHE_DIR）。
- `runtime/optimization/2026-10-09/M0/r5/logs/{launcher.log,local-install-attempt.json}`。

`~/.octosense`（宿主默认）**未触动**（launcher.log L5 显示 app_storage/lifecycle.rs:442 写入 `r5/home/.octosense` 而非 `~/.octosense`，与 r4 一致）。

`app/bundle/main.splash`、`app/bundle/manifest.json` 未改动；r5 目录也不写项目内业务路径。已提交 B ZIP（`submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip`）原样保留，未触动 stamp。

## 3. D-R4-3 修复：本地 catalog 路径最小复现 + install_staged 阻塞

用户授权路线为「查明并验证本地 catalog / app-hub install_staged 本地安装路径」，不走 AppHub 公开发布。源码证据（`OctoSense-App-Hub/crates/{appstore,app-hub,app-hub-app}/...`）确认本地安装路径如下：

| 入口 | 固定源码事实 |
|---|---|
| `OCTOSENSE_HUB` 解析 | `crates/appstore/src/source.rs:from_env()`：`http://...` 走 `Origin::Http`，其余按 `Origin::Directory(dir)` |
| 本地目录 catalog 读取 | `CatalogChannel::read_cache(root)`：读 `root/catalog-v2.json`（GitHub 通道）或 `root/catalog.json`（legacy） |
| `install_staged` 入口 | `crates/app-hub/src/client.rs:install_staged()`：要求 entry 存在 → 未 withdrawn → `digest_dir(staged) == entry.manifest.integrity.bundle_blake3` → staged manifest 与 entry manifest 一致 → **签名校验**（`if let Some(signature) = &entry.manifest.integrity.signature { verifier.verify(...) }`） → `admit_and_resolve_dir(&staged_json, &digest, &self.limits, &self.publisher_keys())` → `entry.manifest.check_host_apis(&self.host_api_versions)?` |
| publisher_keys | `client.rs:publisher_keys()`：从 `self.catalog.entries[*].publisher_key` 累加；空 catalog → 空 keys |
| UI 安装 | `crates/app-hub-app/src/catalog.rs:install()`：先 `self.origin.stage(artifact, workspace)` → `prepared_store.install_staged(...)` → `publish_bundle(install_root, install_dir, rename)`。`publish_bundle` 是本地原子切换函数，不是 `hub publish` |

**关键阻塞点**：
1. `install_staged` 第 423 行 `verifier.verify(&signature.key_id, &signature.value, &entry.manifest.signing_bytes())` — 当 catalog entry 带 signature 时，校验失败则拒绝；空 publisher keys 无法验签。
2. 即使把 bundle manifest 的 `integrity.signature` 字段置空（绕过 `if let Some`），`admit_and_resolve_dir` 仍会读 `self.publisher_keys()` 做策略解析，空 keys → 任何依赖 publisher 身份的策略条目都会失败。
3. 用户路线约束「禁止 AppHub publish/签名/listing」 = 不能走 `hub keygen / hub certify / hub sign-manifest / hub publish / hub verify <catalog> --anchor ...`；任何生成 catalog 签名或 anchor certificate 的命令都不在本轮可执行范围。

`r5/local-mirror/` 为空目录（`OCTOSENSE_HUB=runtime/optimization/2026-10-09/M0/r5/local-mirror`）。`OCTOSENSE_HUB_CATALOG=github-v2` 让 host 期待 `catalog-v2.json`，空目录 → host 不读 catalog；但 launcher.log L6–L9 显示 LLM profile 路径在 `OCTOSENSE_HOME/.octos` 下被读，未因此抛错（profile 缺失不阻断启动）。

**端到端 install_staged 在本轮无法实证**：写一份离线签名 catalog 需 `hub keygen + hub certify + hub sign-manifest`，三步都在用户禁止清单内；写一份无签名的 catalog 让 `if let Some(signature)` 短路 → 后续 `admit_and_resolve_dir` 用空 keys 解析策略的结果未实测到；启动器也未在 30 s 窗口内通过 dock click 触发 `install_staged`。

**最小复现**（用于未来解除阻塞时跑）：

```sh
# 三步生成离线测试 catalog（需要用户授权，本轮禁止）
hub keygen runtime/optimization/2026-10-09/M0/r5/local-mirror/test-anchor.key
hub certify --anchor runtime/.../test-anchor.key --working runtime/.../test-anchor.key > runtime/.../local-mirror/anchor.cert
# 用 working key 给我们的 bundle 签名
hub stamp runtime/.../local-mirror/artifacts/octosense-repair
hub sign-manifest runtime/.../local-mirror/artifacts/octosense-repair --key runtime/.../test-anchor.key --key-id test-anchor
# 用 working key 签 catalog（含 publisher_key=test-anchor 公钥）
hub publish ... --anchor-cert <hex> --publisher test-anchor --repo <url> --commit <sha>
```

然后 `isolated_launcher.py` 启动后经 dock 点开 apphub-app，调 `install_staged` 落 `<id>/.bundles/<id>/bundle`。本轮上述步骤均未执行；D-R4-3 维持 BLOCKED。

**保留 D8 路线结论**：install_staged 在 `app-hub-app` 的 `install()` 里被 UI 入口触发；该入口存在，但本环境无认证主体同意 consent（见 §4）。**最小可审阅方案**：建议由用户授权生成"仅测试目录、仅当前 digest、仅隔离 sandbox 内有效"的离线签名 catalog（`hub keygen / hub certify / hub sign-manifest / hub publish` 全套），并在测试结束后丢弃私钥与 anchor；或由用户裁决改走 AppHub 公开发布（拒绝项，本轮不重提）。两条路都不在本轮可执行范围。

## 4. D-R4-4 修复：可信双主体阻塞证据

launcher.log 仅出现单一 Consent sheet（`octos: contained apps' service registered (Consent)`，lib.rs:366）。Consent service 是单 sheet 默认注册，没有第二个 subject 在本轮加入。

源码路径：
- `app-storage/lifecycle.rs` 存在账户绑定 / 登出 / 存储分区代码（r4 source 已核验），但启动时未触发；host 默认 subject 与 `~/.octosense/...` 关联。
- 双主体需要宿主账户系统层面接受第二个认证（OS keychain / system account）。本环境隔离 sandbox 阻断了 `app storage: Mail's secrets stay in its service folder: ... Operation not permitted (os error 1)`（launcher.log L5）—— 这正是 host 试图在 keychain 写入第二个 subject 的拒绝路径。

`STATE.actor` / `USERS` 是 `app/bundle/main.splash` 的脚本内演示选择（r3/r4 已多轮记录），与宿主认证解耦；D-R4-4 修复 ≠ 把 STATE.actor 改成两个数组。

**最小复现**：
- 启动宿主 → 触发账户切换 / 新增 subject → 验证隔离 sandbox 允许 keychain 写入 → 切换后再读 → 跨读拒。
- 本轮 sandbox profile 允许 r5 文件写入，**不允许 keychain 写入**（lifecycle.rs:442 L5 即证）。第二个 subject 不可能在当前 sandbox 内注册；D-R4-4 维持 BLOCKED。

替代方案（仅审阅）：
- 在 r5 sandbox 放宽 `(allow file-write* (subpath "~/Library/Keychains"))` —— 用户授权后可行；本轮禁止改动 sandbox profile。
- 跳过 keychain 走 host 的 dev-only mock subject —— 等同绕开"可信"，不解决 BLOCKED。

## 5. D-R4-5 修复：文件/原子恢复/提醒三类能力实测阻塞

launcher.log L10 显示 `wm: modules linked` 含 `card` / `notes` / `reminders` / `clock`，与 r4 同；但 30 s 诊断窗口未触发：
- 真实文件选择（picker）：apphub / notes 的 file dialog 在 makepad 库内（`makepad_platform::file_dialogs::VirtualFile`）；需 UI click 触发，headless 启动器无法模拟；D-R4-5 picker 维持 BLOCKED。
- 原子替换/持久化提交：业务脚本 `addEvidence` 仍含 `demo:true, ready:false, sha:""`（未改业务文件）；host 自身的 `std::fs::rename(path.with_extension("part.png"), path)`（lib.rs:5242）是原子切换示例，但跑业务任务需要 dock click。
- 提醒/任务跳回：`wm: modules linked` 仅证模块链接；`reminders` 模块的实际调度、due_at 持久化、跨重启恢复都需要 UI 触发。

**最小复现**：
- 启动宿主 → dock 点击 `notes` 或 `card` → 在 notes 内写文件 → 关闭 → 重启 → 读回 → 验证原子替换 + 持久化。
- 启动宿主 → 注册 reminders → 设置 due_at → 退出 → 重启 → 验证提醒恢复。
- 本轮 30 s 窗口内 headless 无法触发 dock click；M0 不假装 D-R4-5 已具备证据，D-R4-5 维持 BLOCKED。

## 6. 既有验收映射与硬验收

D7 编号语义按 `docs/build-loop/ACCEPTANCE.json` title 与 `15_BUILD_VERIFY_LOOP.md` L0 现行台账为准。映射文件：`results/ACCEPTANCE_MAPPING.md`（64 项 G0-A–F / T01–T38 / U01–U12 / P01–P08，原生 r5 全部维持 BLOCKED）。旧 `L8-DV2` 额外条目保留在 `additional-ledger-entries.json`。

| 编号 | r5 目标 Shell 判定 | 变更相对 r4 |
|---|---|---|
| G0-A | BLOCKED；host_started=true，但完整 bundle 安装未实证；launcher 来源/字节一致 | launcher 来源同 r4 复现；install_staged 未触；不重写为 PASS |
| G0-B | BLOCKED；单 Consent subject 已注册，第二个未实测 | 同 r4 |
| G0-C | BLOCKED；launcher.log 无任务/事件写入 | 同 r4 |
| G0-D | BLOCKED；picker 未触发；业务 addEvidence 未改 | 同 r4 |
| G0-E | BLOCKED；model service 注册但无 provider 配置 | 同 r4 |
| G0-F | BLOCKED；reminders 模块已链接；due_at 持久化与跨重启恢复未实测 | 同 r4 |
| T28 | BLOCKED；业务 bundle 未 launch | 同 r4 |
| T29 | BLOCKED；grant 生命周期未实测 | 同 r4 |
| T32 | BLOCKED；配对码路径未实测 | 同 r4 |
| U09 | BLOCKED；未跑 1280×800 + 150% 放大 | 同 r4 |
| U11 | BLOCKED；未跑 1440×900 等 | 同 r4 |
| P02 | BLOCKED；来源/步骤部分已补，干净启动未完成 | 同 r4 |

**硬验收复核**：
1. 候选输入快照可定位（`r5/snapshot/status-before.txt`、CANDIDATE.json）；目标桌面宿主能真实启动（host_started=true、launcher.log 关键行）；来源明确（octosense / octos-kernel SHA-256 与 r3 receipt 一致）；明确来源不明的二进制：以版本字符串替代来源的不存在。**部分满足**：1.1（来源）PASS、1.2（启动）PASS、1.3（install_staged 落点）BLOCKED。
2. 模型/真实文件/可信身份/存储恢复：四类最小运行证据未具备；本轮按要求记 BLOCKED，不冒充 PASS。
3. 中文原生表单与滚动后操作：业务 bundle 未 launch；BLOCKED。
4. 运行数据使用 r5 隔离目录，原有数据及未提交改动完整保留（git status 17 项未触动；~/.octosense 未触动）；PASS。
5. 路线足以支撑后续硬约束：install_staged 需要签名 catalog，本轮禁止；双主体、picker/原子/提醒均需 UI 触发；**未放行 M1**。

## 7. 本轮测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| 候选现场保留 | r5/snapshot/status-before.txt | 17 项与 r4 一致 | 一致 | PASS（文件保留） | snapshot/status-before.txt |
| B 包定位 | r4 results/B-package.json | 与 HEAD 一致 | 一致 | PASS（归档比对） | results/B-package.json |
| 官方二进制 | r3 receipt | 三个 SHA-256 一致 | 一致 | PASS（来源校验） | results/binary-verification.json |
| 固定源码 | r4 INDEX.json | 15/15 一致 | 一致 | PASS（源码校验） | source/INDEX.json |
| D7 语义与映射 | 64 项 ID 集合 | 完整且原生 r5 全 BLOCKED | 一致 | PASS（文档自检） | results/ACCEPTANCE_MAPPING.md |
| D8 路线结论 | r4 source 持续 | install_staged + Directory 路线 | 不变 | PASS（路线结论） | source/OctoSense-App-Hub/.../client.rs |
| 静态守卫 | results/static-check.json | 80 fn / 18 处调用 arity 匹配 | 一致 | PASS（词法检查） | results/static-check.json |
| **隔离预检** | sandbox-exec /usr/bin/true + /bin/echo | exit 0 | exit 0 / stdout `r5-preflight-ok` | PASS（环境允许） | r5/logs/local-install-attempt.json |
| **隔离 --launch** | isolated_launcher.py 默认 30 s | host 真实拉起 | host_started=true，exit 0，55 行 launcher.log 含 kernel / model / Consent / 10 模块 / Splash 渲染 / PingFang SC / apphub 进程内 client 1 | PASS（D-R4-1/2 修复） | r5/logs/launcher.log |
| **业务 bundle 解析** | dev-apps.json 合法 catalog | parse_catalog 通过 | schema 通过；未触 dock click → 未 launch | PASS（解析）/ NOT_RUN（业务 launch） | r5/probe/dev-apps.json |
| **本地 install_staged** | local-mirror + 离线 catalog | 落 `<id>/.bundles/<id>/bundle` | 未执行；缺签名 catalog | BLOCKED（D-R4-3） | §3 最小复现 |
| **可信双主体** | sandbox 内注册 2 个 subject | 跨读拒、撤权 | 单 Consent sheet；keychain 拒绝（os error 1） | BLOCKED（D-R4-4） | §4 launcher.log L5、L9 |
| **文件选择/原子/提醒** | UI 触发 + 30 s 窗口 | 字节一致、原子恢复、跨重启提醒 | 未触 UI；模块已链接 ≠ 可用 | BLOCKED（D-R4-5） | §5 launcher.log L10 |
| 重启恢复 | 关闭重开 | 任务/文件读回 | 未执行 | NOT_RUN | — |
| 数据边界 | sandbox profile + per-key paths | 仅写 r5 | 仅写 r5；未触 `~/.octosense` | PASS | r5/logs/launcher.log L5、L35 |
| 业务文件零改动 | git diff/status | 工作树业务文件未改 | 17 项与 r4 status-before 一致 | PASS | snapshot/status-before.txt |

## 8. 残余与未关闭项

1. **R4-B02 / D-R4-3**：本地可信 catalog 需要用户授权生成 `hub keygen / certify / sign-manifest / publish`；本轮禁止 publish/签名/listing。若只生成 anchor 不发布，`hub verify <catalog> --anchor ...` 仍然需要 `anchor-cert`。建议用户裁断：
   - 路线 A：授权生成「仅测试目录、仅当前 digest、仅隔离 sandbox 内有效」的离线签名 catalog，r6 再实测 install_staged；结束后丢弃私钥与 anchor。
   - 路线 B：放弃本地 catalog，承认 install_staged 仅在 AppHub 公开发布后成立；本项目 M0/M1 路线改为只跑 `card` 进程内托管 + 已提交 bundle。
   两条路都不在本轮可执行范围 → **NEEDS_ABRAM=yes**（必须用户授权才能解锁）。
2. **R4-B03 / R4-B04 / R4-B05**：模型 provider、双主体、picker/原子/提醒在本轮仍未具备运行证据；D-R4-4/D-R4-5 维持 BLOCKED。解除需在 r6 起把窗口拉到 ≥ 60 s 并接 UI 自动化或允许 keychain 写入；M1/M2/M5 落地的"可信身份/可靠执行/真实附件"硬约束也因此无法在 M0 单轮内关闭。
3. **业务 bundle 真实启动**：dock click → `launch_app_with_args` 需要 UI。本轮 headless 启动器不冒充该路径；r5 launcher.log 显式无 `wm: launched octosense-repair as client 1`。
4. **不动 ACCEPTANCE.json / 不删 P06/P07/P08 UNASSESSED / 不替 P06–P08 写 PASS**。

## 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r5/CANDIDATE.json`。
- 证据：`runtime/optimization/2026-10-09/M0/r5/logs/launcher.log`（7287 B / 44 行）、`logs/local-install-attempt.json`（host_started=true + 关键行）、`probe/dev-apps.json`、`probe/isolated_launcher.py`、`probe/isolation.sb`、`probe/environment.json`。
- 快照：`runtime/optimization/2026-10-09/M0/r5/snapshot/status-before.txt`（17 项）、`bundle-sha.txt`、`head-sha.txt`。
- 固定官方源码：`runtime/optimization/2026-10-09/M0/r5/source/INDEX.json`（15 项，沿用 r4 校验）+ 完整 OctoSense / OctoSense-App-Hub 源码树。
- ACCEPTANCE 映射：`runtime/optimization/2026-10-09/M0/r5/results/ACCEPTANCE_MAPPING.md`、`results/acceptance-mapping.json`。
- GATES.json M0 条目：候选 r5；D-R4-1/2 关闭；D-R4-3 维持 BLOCKED + NEEDS_ABRAM=yes；D-R4-4/5 维持 BLOCKED；状态 READY_FOR_REVIEW。
- r1–r4 报告与 Review 原文保留。

**编码方交接完成，待独立 Review；不进入 M1。**
