# M0 实施报告 r7 — 官方钉版源码 + install_staged 端到端复核

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M1。**

本轮按 Kimi 2026-10-10 03:40 r5 Review 五条必修（D-R5-1/2/3/4/5）严格修复：

- D-R5-1：`install_probe` 与 `hub` CLI 改为 path 依赖 / 基于官方钉版 ba36df05 全量源码构建。install_staged 走官方 `&dyn SignatureVerifier` 接口，落点改为官方 `<install_root>/.bundles/<id>/bundle`；may_run 走官方 `verify_release_bundle`（按 catalog publisher_keys 重验字节）。
- D-R5-2：全新空 home；r7 内不预布景任何 bundle；host 60s 后探针自控终止，pgrep 验证无残留进程。
- D-R5-3：isolated_launcher.py 路径判据改为官方布局 `OCTOSENSE_HOME/apps` + `apps/.bundles/<id>/bundle`。
- D-R5-4：G0-D 退回 BLOCKED（probe std::fs 非 host app_storage 授权路径）；P02 改 PARTIAL。
- D-R5-5：重写 ACCEPTANCE_MAPPING.md 为 r7 版本；GATES.json 文字修正。

- 模块 / 目标：仅 M0 r7；按 Kimi r5 Review 五条必修逐条对齐固定官方契约 + 洁净 home + 路径判据 + 文档准确性。
- candidate_id / base_candidate_id：`M0-r7-worktree` / `M0-r6-worktree`；已提交 B 包另标 `B-candidate-8d73056`。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；未提交、push、reset、stash。
- 快照：`runtime/optimization/2026-10-09/M0/r7/snapshot-status-before.txt` 与 r5/r6 一致；`bundle-sha.txt` 同 r5/r6。
- 目标宿主：官方 `desktop-v0.1.0-rc.1` macOS aarch64；与 r3/r5/r6 同源复用 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`（SHA-256 与 r3 receipt 一致：`3e127963…` / `a3e46a45…`）。
- 实际开发会话路由：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。本轮未创建子代理；未将代理或技能当作主会话切换。
- 前置 Review：r5 FAIL（Kimi）；本轮按其五条必修修复。
- 修改文件：新增 r7/ 目录（probe、install_probe、keys 已销毁、staging、local-mirror、install-root、results、logs、source-pin）；修改工作树业务文件 0 项（git status 与 r5/r6 一致）。
- 桌面 UI/交互变化：无；r7 没有写新 splash、没有重打 bundle。
- 接口 / 数据迁移：无；没有重打正式 bundle stamp、没有动旧 B 包。
- 应用模型/provider：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。
- 覆盖范围：D-R5-1 install_staged 端到端实测（D-R5-1 闭合）、D-R5-2 洁净 home（D-R5-2 闭合）、D-R5-3 路径判据（D-R5-3 闭合）、D-R5-4 G0-D/P02 文字修正（D-R5-4 闭合）、D-R5-5 ACCEPTANCE_MAPPING 与 GATES 文字（D-R5-5 闭合）；其余 64 项 ACCEPTANCE 映射维持 r6 原状。
- 置信度：install_staged 端到端 **高**（官方钉版源 + 公开锚验签 + 重启 may_run ok + 字节级 SHA 一致）；洁净 home **高**（launcher 启动前为空，launcher.log L31 佐证 apps_root 写入 .host/.system，pgrep 验证 0 残留）；UI 自动化（osascript）**失败证据**：osascript 报 `execution error: 未获得授权将 Apple 事件发送给 System Events. (-1743)`，Automation 权限不在本环境 → **仍 BLOCKED**。

## 1. 官方钉版源码获取与构建

### 1.1 完整官方源码（与 r5/source 5 文件 SHA 一致）

r7 直接从 GitHub 拉取官方 ba36df0505e198f998201af312ff5184df98cae9 全量源码：

```sh
cd runtime/optimization/2026-10-09/M0/r7
mkdir source-pin
curl -sL --max-time 120 -o source-pin/apphub.tar.gz \
  https://github.com/OctoSense-org/OctoSense-App-Hub/archive/ba36df0505e198f998201af312ff5184df98cae9.tar.gz
tar -xzf source-pin/apphub.tar.gz -C source-pin
mv source-pin/OctoSense-App-Hub-ba36df0505e198f998201af312ff5184df98cae9 \
   source-pin/OctoSense-App-Hub
# 兄弟 crates 软链到 native-build 已存在的 makepad/octoscript/octoscript-makepad
ln -s .../runtime/native-build/makepad source-pin/makepad
ln -s .../runtime/native-build/octoscript-makepad source-pin/octoscript-makepad
ln -s .../runtime/native-build/octoscript source-pin/octoscript
rm source-pin/apphub.tar.gz
```

### 1.2 SHA 钉版校验（与 r5/source 5 文件 1:1 一致）

| 文件                                                       | SHA-256                                                            |
| ---------------------------------------------------------- | ------------------------------------------------------------------ |
| `r7/source-pin/OctoSense-App-Hub/crates/app-hub/src/client.rs` | `27701be87130900ee6981243569f135f0f1d3042ccd73649ead58407548cc54e` |
| `r7/source-pin/OctoSense-App-Hub/crates/app-hub/src/bin/hub.rs` | `bc21e988dccd9fe1bfe8894eaf38f572736f7a132c8ff8ce3aa129b51df0039f` |
| 与 r5/source 同名文件 SHA 一致 ✓                           | 与 r5/source INDEX.json 14 项 match=true ✓                         |

### 1.3 hub CLI 构建产物

```sh
cd r7/source-pin/OctoSense-App-Hub
cargo build --release -p octosense-app-hub --bin hub  # 1m 25s
# target/release/hub  SHA-256 = c233094faf94ebf277be36c8d7e0559b07691064df670778c360eb26432038a9
# ./target/release/hub --help 输出含 keygen / certify / stamp / sign-manifest /
# publish / check / scan / verify / catalog-prepare / catalog-envelope /
# catalog-verify 共 16 个子命令（与官方 ba36df05 一致）。
```

## 2. 授权方案 A：隔离目录内离线签名 catalog

### 2.1 命令序列（全部在 r7/ 内；零联网；零 publish/上架）

```sh
HUB=r7/source-pin/OctoSense-App-Hub/target/release/hub
ANCHOR_PUB=$(…/hub keygen keys/anchor.key)   # a3de88ab126a88006480790425770619c7e903b83b7645d28d989079d8c5d34d
WORKING_PUB=$(…/hub keygen keys/working.key) # 757bbb5bd8ffd1d1be7e667c5c374166ad2fcd6e56f630cde330ebc8fac0bb3d
CERT=$(…/hub certify --anchor keys/anchor.key --working keys/working.key)
# 419c2eb764f7d9d58ed3da56a1c4c5fdce613fea5f58dccc55d7211c503e9275faa5d8d986a0d9e8956af55993279dfde39a659a0f60d0883470468c6087500d

cp -R app/bundle/. staging/   # 删除 .DS_Store / *.bak / host.log / .archive / data-test

…/hub stamp staging/                                  # 309e06d3…
…/hub sign-manifest staging/ --key keys/working.key --key-id test-publisher
…/hub publish staging/ \
    --catalog local-mirror/catalog.json \
    --key keys/working.key \
    --anchor-cert "$CERT" \
    --publisher test-publisher \
    --repo local-sandbox --commit r7-test \
    --out local-mirror \
    --allow-unsigned \
    --publisher-key test-publisher=$WORKING_PUB
# octosense-repair 0.1.0-b — PASSED
# published octosense-repair 0.1.0-b (catalog sequence 1)
```

### 2.2 产物

| 文件 | 大小 | SHA-256 | 备注 |
|---|---|---|---|
| `local-mirror/catalog.json` | 5097 B | `b4493bb14a1f83f76ddcc191146937629e76b5c51c84ad8d4fecc1f7a2f0f880` | 签名 catalog；`hub verify --anchor <hex>` → `catalog sequence 1 verified, 1 entries` |
| `local-mirror/artifacts/octosense-repair-0.1.0-b.bundle/manifest.json` | 677 B | `d758ed8846deb4a300c75ffa86cebd86b3af64a241df64b31ccace2688ac7020` | stamp 写入 digest `309e06d3…`；sign-manifest 写入签名 key_id=test-publisher |
| `keys/anchor.key` | 64 B | `44194e832754c4855c0fde3edd7ae427e7350d3f32694597ebf8ce9f2182ea1b` | 已删除 |
| `keys/working.key` | 64 B | `71cec44b9d3d618bf03b6beac29aa47e079878cbd6707bcfd350db236b168cec` | 已删除 |

> **公开 anchor hex** `a3de88ab126a88006480790425770619c7e903b83b7645d28d989079d8c5d34d` 是 r7 sandbox 内自签的非生产 anchor；仅在 r7 内有效，不发布、不上传。

### 2.3 私钥销毁证据

```sh
shasum -a 256 keys/anchor.key keys/working.key   # 两条 hash 记录在 results/key-pre-delete.txt
rm -f keys/anchor.key keys/working.key
ls -la keys/                                       # 空目录
hub verify local-mirror/catalog.json --anchor a3de88ab126a88006480790425770619c7e903b83b7645d28d989079d8c5d34d
# catalog sequence 1 verified, 1 entries   ← 仅用公开锚验证；私钥已删除
```

`results/key-deletion.json` 完整记录生成前后 SHA、销毁命令、销毁后公开锚验证。

## 3. install_staged 端到端实测（官方钉版源码）

**为什么用 direct Rust probe**：本环境无 Automation/Accessibility 授权（osascript 报 `-1743`），UI 点击路径不可达。M0 已用三处证据反复证明「宿主 apphub 模块已链接但 UI 入口必须用户点 dock」是环境能力边界；r7 probe 基于官方 ba36df05 全量源码重建，调用 `octosense_app_hub::Store::install_staged` 走与官方宿主同一函数同一参数同一份 catalog 与 bundle，绕开 UI 但保留全部 verify + digest + policy + copy_tree 路径。

```sh
cd runtime/optimization/2026-10-09/M0/r7/install_probe
cargo build --release   # 3s（依赖 octosense-app-hub 与 octosense-app-policy 钉版源码）
OCTOSENSE_HUB_ANCHOR=a3de88ab126a88006480790425770619c7e903b83b7645d28d989079d8c5d34d \
  target/release/r7_install_probe /Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09/M0/r7
```

### 3.1 4 步实测结果（原文取自 `results/install-probe.log`）

| 步骤 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| **1. install_staged** | Store::new(anchor, install_root, limits)；accept_catalog(json)；PublisherKeys 从 catalog entries 收集；install_staged("octosense-repair", staged, &keys, "2026-10-09") | 验证 anchor → working 公钥 → catalog 签名 → bundle digest → manifest 签名 → policy → 落 `<install_root>/.bundles/<id>/bundle/` | `installed manifest.id="octosense-repair" version="0.1.0-b" digest="309e06d3…"`；policy `caps={"storage"} hosts={} agent_present=false`；落点 `<install_root>/.bundles/octosense-repair/bundle/` | **PASS** | `results/install-probe.log` Step 1；`install-root/.bundles/octosense-repair/bundle/` |
| **2. 重启恢复 + may_run** | 关闭 Store、新建 Store::new(同 anchor, 同 install_root, 默认 limits)、accept_catalog 同份 json、installed_version/may_run | installed_version=Some("0.1.0-b")；may_run=ok（按官方 verify_release_bundle 重验字节 + admit_and_resolve_dir） | `installed_version after restart: Some("0.1.0-b")`；`may_run: ok (caps={"storage"}, hosts={}, agent_present=false)` | **PASS** | `results/install-probe.log` Step 2 |
| **3. 中文存储 + 原子写** | 写 66 B 中文 note（"用户报修：空调不制冷。联系地址：北京朝阳区。"）到 `<install_root>/.bundles/<id>/data/notes`；read_back | 字节一致 | `note write/read identical: true (66 bytes)` | **PASS**（FS 原语级，非 host app_storage 授权路径 — G0-D 维持 BLOCKED） | `results/install-probe.log` Step 3 |
| **4. 可靠时钟 + atomic rename** | SystemTime before / after；写 tmp；rename 覆盖 | 时钟单调；tmp 消失；新内容在 | `clock before=1791575149 after=1791575149 delta=0`（同一秒内）；`atomic rename: tmp=true, new contents present` | **PASS** | `results/install-probe.log` Step 4 |

> 直接结论（官方源码语义下）：catalog 验证、签名链、digest 一致、policy 解析、bundle 落 `<install_root>/.bundles/<id>/bundle/`、新 Store 重启识别、原子 rename、文件写读字节一致、SystemTime 单调 — 八项最小运行证据成立。

### 3.2 落地形态（按官方 client.rs INSTALLS_DIR=".bundles"）

```
runtime/optimization/2026-10-09/M0/r7/install-root/.bundles/octosense-repair/
├── bundle/
│   ├── manifest.json             (677 B, SHA-256 d758ed88…)
│   ├── main.splash
│   ├── listing.json
│   ├── instance.json
│   ├── assets/icon.svg
│   ├── runtime/desktop-v2-20261008/shots/…png
│   └── screenshots/…png
└── data/notes                    (66 B 中文 note，原子 rename 后内容更新)
```

`results/key-files-sha256.txt` 4 条 hash：`local-mirror/catalog.json`、`staged/manifest.json`、`local-mirror artifact/manifest.json`、`install-root/.bundles/.../manifest.json`（三方一致）。

## 4. 同环境真实启动宿主

r7 launcher 与 r6 同源（`OCTOSENSE_HUB=local-mirror`、`OCTOSENSE_HUB_CATALOG=legacy`、`OCTOSENSE_HUB_ANCHOR=<r7 anchor hex>`）；**洁净 home 启动**；60s 窗口；`host_started=true` + `host_terminated_by_probe=true` + `host_exit_code=0` + `post_terminate_pgrep=""`（无残留进程）。

launcher.log 关键行：

- `octos: kernel service ready`（lib.rs:312）
- `llm: provider profile under /Users/abeam/.../r7/home/.octosense/octos-home/.octos`（lib.rs:395；profile 未配置 → 无可用 provider）
- `model: service registered`（lib.rs:429；未发起任何请求）
- `octos: contained apps' service registered (Consent)`（lib.rs:366；单 sheet 默认）
- `wm: modules linked: ["rinx","terminal","apphub","card","calculator","clock","notes","reminders","weather","octoscode"]`（lib.rs:6008）
- `[SPLASH] eval: 809 bytes … animating=false`（默认空 Splash — 没有 dock click，未启动业务 splash）
- `news: service registered, host dir /Users/abeam/.../r7/home/.octosense/apps/.host`（apps.rs:345）

`home/.octosense/{apps,secrets,wm,themes}` 在 r7 内被实际写入（`drwx------`，属主 501）；host 仅写入自身状态（`apps/.host`、`apps/.system`、`secrets/os.mail`、`wm/themes/...`），**未写入 `apps/octosense-repair`**（因 UI install 被 osascript `-1743` 阻断）。`~/.octosense` **未触动**（mtime 2026-10-09 21:38）。

## 5. UI 自动化尝试与失败

```sh
osascript -e 'tell application "System Events" to count of (every process whose name contains "octosense")'
# execution error: 未获得授权将 Apple 事件发送给 System Events. (-1743)
```

Automation 权限不在本环境；60 s 窗口内 apphub UI 无法被任何脚本驱动；**r7 的 install_staged 端到端实测通过 direct Rust probe（基于官方钉版源码）弥补**。

## 6. 既有用例映射与硬验收

详见 `results/ACCEPTANCE_MAPPING.md`（重写为 r7 版本）。摘要：

| 编号 | r7 目标 Shell 判定 | 变更相对 r6 |
|---|---|---|
| G0-A | **PASS**（基于官方 ba36df05 install_staged 端到端实测；落点 `.bundles/<id>/bundle`；may_run 重验字节） | D-R5-1 修复 |
| G0-B | BLOCKED（host 仅注册单 Consent sheet；sandbox keychain 拒绝；同 r5/r6） | 不变 |
| G0-C | BLOCKED（catalog/签链/digest 在 install_staged 跑通；并发无证据；原子 rename 仅 FS 原语级） | 不变 |
| G0-D | **BLOCKED**（probe 用 std::fs 非 host app_storage 授权路径；中文 66B write/read identical 仅 FS 原语级证据） | **D-R5-4 修复**：r6 误记 PASS → r7 BLOCKED |
| G0-E | BLOCKED（model service 注册但无 provider 配置；同 r6） | 不变 |
| G0-F | BLOCKED（reminders 模块已链接；scheduler/due_at/跨重启提醒未实测；同 r6） | 不变 |
| T28 | BLOCKED（业务 bundle 真实 dock click 未实测；UI 阻断；同 r6） | 不变 |
| T29 | BLOCKED（grant 生命周期未实测；同 r6） | 不变 |
| T32 | BLOCKED（配对码路径未实测；同 r6） | 不变 |
| U09 | BLOCKED（未跑 1280×800 + 150% 放大；同 r6） | 不变 |
| U11 | BLOCKED（未跑 1440×900 等；同 r6） | 不变 |
| P02 | **PARTIAL**（host 二进制有官方 release + r3 receipt；install probe 源码钉版 ba36df05；私有发布/计费/真实 provider 未配置） | **D-R5-4 修复**：r6 误记 PASS → r7 PARTIAL |

**硬验收复核**：

1. 候选输入快照可定位（`r7/snapshot-status-before.txt` 17 项同 r5/r6；`r7/bundle-sha.txt` 同 r5/r6）；目标桌面宿主真实启动（`r7/results/launcher.log` 含 kernel/modules/字体/Splash；`r7/results/local-install-attempt.json` 含 `host_started=true`、`host_exit_code=0`、`post_terminate_pgrep=""`）；明确来源（octosense/octos-kernel SHA-256 与 r3 receipt 一致；install probe 与 hub CLI 从官方 ba36df05 全量源码钉版构建）；明确来源不明的二进制：无；不以版本字符串替代来源：**PASS**。
2. 模型（G0-E BLOCKED）/真实文件（G0-D BLOCKED）/可信身份（G0-B BLOCKED）/存储恢复（G0-C BLOCKED）：四项如实 BLOCKED，**未冒充 PASS**。G0-A（install_staged 端到端实测 + 重启 may_run + 字节 SHA 一致）**PASS**。
3. 中文原生表单与滚动后操作：66 B 中文 note（用户报修：空调不制冷。联系地址：北京朝阳区。）**字节一致**（probe step 3）；原生 UI 中文 IME 输入与滚动后控件操作 **NOT_RUN**（UI 触发不可达；同 r6）。
4. 运行数据使用 r7 隔离目录（`OCTOSENSE_HOME`、`OCTOSENSE_HUB`、`OCTOSENSE_HUB_ANCHOR`、`install-root` 全部 r7 内）；`~/.octosense` 未触动；17 项未提交改动完整保留：`git status --porcelain` 与 r7/snapshot-status-before.txt 一致：**PASS**。
5. 路线足以支撑后续硬约束：install_staged 端到端基于官方钉版源实测通过；可信双主体、模型 provider、UI 触发仍是外部依赖：**未放行 M1**。

## 7. 本轮测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| 隔离预检 | sandbox-exec `/usr/bin/true` + `/bin/echo` | exit 0 | exit 0 / `r7-preflight-ok` | PASS | `logs/local-install-attempt.json` |
| Catalog 预校验（官方 hub CLI） | `hub verify <catalog> --anchor <hex>`（基于 ba36df05） | verified | `catalog sequence 1 verified, 1 entries` | **PASS（D-R5-1 修复）** | `results/catalog-summary.txt` |
| hub CLI SHA 钉版 | shasum hub 二进制 | 与 r3 receipt 不一致（harness 自带不同） | `c233094faf94ebf277be36c8d7e0559b07691064df670778c360eb26432038a9`（基于 ba36df05 源码） | PASS | `results/key-files-sha256.txt` |
| 源码钉版一致 | shasum r7/source-pin 与 r5/source 5 文件 | 一致 | client.rs `27701be…` / hub.rs `bc21e98…` 与 r5/source 一致 | PASS | `results/key-files-sha256.txt` |
| host 真实启动（洁净 home） | isolated_launcher.py 60s 窗口 | host_started=true | host_started=true, launcher.log 44+ 行 | PASS | `results/launcher.log` |
| host 无残留进程 | probe 后 pgrep | 空 | `post_terminate_pgrep: ""` | PASS | `results/local-install-attempt.json` |
| home 洁净度 | launch 前 `find home/` | 空 | home 为空目录（仅 . 与 ..） | **PASS（D-R5-2 修复）** | `r7/snapshot-status-before.txt` + `find home` |
| host 写入来源 | launcher.log + `find home/` | 仅 host 自写 | `apps/.host`、`apps/.system`、`secrets/os.mail`、`wm/themes/...`；无 `apps/octosense-repair` | PASS | `results/launcher.log` + `find home` |
| UI 触发 install | osascript `count of (every process whose name contains "octosense")` | 触发 UI、落 install_root | `-1743` 权限拒绝；UI 未触发 | NOT_RUN | `results/install-attempt.json` |
| install_staged 直跑（官方源码） | r7_install_probe step 1 | 落 `<install_root>/.bundles/<id>/bundle/`、签名完整 | `installed manifest.id=octosense-repair version=0.1.0-b digest=309e06d3…`；policy `caps={"storage"} hosts={}` | **PASS（D-R5-1 修复）** | `results/install-probe.log` Step 1 |
| 重启恢复（官方源码） | step 2 同 anchor 同 install_root 新建 Store | installed_version=Some；may_run=ok（重验字节） | `installed_version after restart: Some("0.1.0-b")`；`may_run: ok (caps={"storage"}, hosts={}, agent_present=false)` | **PASS（D-R5-1 修复）** | `results/install-probe.log` Step 2 |
| 真实文件字节一致 | step 3 写 66 B 中文 note | 字节一致 | `note write/read identical: true (66 bytes)` | **PASS（FS 原语级；G0-D 维持 BLOCKED）** | `results/install-probe.log` Step 3 |
| 原子写 | step 4 tmp + rename | tmp 消失；新内容在 | `atomic rename: tmp=true, new contents present` | PASS | `results/install-probe.log` Step 4 |
| 可靠时钟 | step 4 SystemTime before/after | 单调 | `clock before=1791575149 after=1791575149 delta=0` | PASS | `results/install-probe.log` Step 4 |
| 私钥销毁 | `rm -f keys/*.key` + `hub verify <catalog> --anchor <hex>` | 私钥消失；catalog 仍可用公开锚验证 | 两键已删；`catalog sequence 1 verified, 1 entries` | PASS | `results/key-deletion.json` |
| 数据边界 | 沙箱 profile + per-key paths | 仅写 r7 | r7/home/.octosense 已实际写入；`~/.octosense` 未触动；r5/r6 历史 home 未变 | PASS | `find home` + `stat ~/.octosense` |
| 业务文件零改动 | git status / snapshot | 工作树业务文件未改 | 17 项与 r5/r6 status-before 一致；bundle_sha 同 r5/r6 | PASS | `snapshot-status-before.txt` + `bundle-sha.txt` |
| 路径判据正确 | isolated_launcher.py L122 / L132 | 官方布局 `apps` + `apps/.bundles/<id>/bundle` | `apps_root = $OCTOSENSE_HOME/apps`；`installed_bundle_dir_exists` 检查 `$OCTOSENSE_HOME/apps/.bundles/octosense-repair/bundle` | **PASS（D-R5-3 修复）** | `probe/isolated_launcher.py` L122-132 |
| 文档准确性 | ACCEPTANCE_MAPPING.md + GATES.json 文字 | 与本论判定一致 | ACCEPTANCE_MAPPING.md 重写为 r7；GATES.json blockers 文字按 r5 Review 修正（r6 secrets EPERM、r7 secrets 写成功） | **PASS（D-R5-5 修复）** | `results/ACCEPTANCE_MAPPING.md` + `GATES.json` |

## 8. 残余与未关闭项

1. **D-R5-1 / install_staged 端到端**：本轮通过官方 ba36df05 钉版源码 + 隔离目录离线签名 catalog 实测通过；落点官方布局 `<install_root>/.bundles/<id>/bundle`；may_run 重验字节 + admit_and_resolve_dir。**解除**。
2. **D-R5-2 / 洁净 home**：r7 内 home 启动前为空；host 启动后仅由 host 自己写入；pgrep 验证 0 残留。**解除**。
3. **D-R5-3 / 路径判据**：isolated_launcher.py 改用官方布局。**解除**。
4. **D-R5-4 / G0-D 与 P02 越级**：G0-D 退回 BLOCKED（probe std::fs 非 host app_storage 授权路径）；P02 改 PARTIAL。**解除**。
5. **D-R5-5 / 文档准确性**：ACCEPTANCE_MAPPING.md 重写；GATES.json blockers 文字修正。**解除**。
6. **D-R4-4 / 可信双主体**：launcher.log 仍仅含单 Consent sheet；sandbox 阻 keychain 写；与 r5/r6 同——**仍 BLOCKED**。
7. **D-R4-5 / 文件 picker / 提醒调度 / due_at 持久化 / 跨重启提醒恢复**：写读字节一致、原子 rename、SystemTime 单调 **已实测 PASS（FS 原语级）**；picker UI / 提醒调度 / due_at 持久化 / 跨重启提醒恢复 **仍 BLOCKED**（UI 触发不可达）。
8. **UI 触发 install**：本环境无 Automation/Accessibility 授权，osascript `-1743`；r7 用 direct Rust probe（基于官方钉版源码）补齐代码路径证据，但 host 的真实 UI 路径不在本轮可执行范围。**记 NOT_RUN，不冒充 PASS**。
9. **不动 ACCEPTANCE.json / 不删 P06/P07/P08 UNASSESSED / 不替 P06–P08 写 PASS**。

## 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r7/CANDIDATE.json`（待生成）。
- 证据：`results/install-probe.log`、`results/launcher.log`、`results/catalog-summary.txt`、`results/key-files-sha256.txt`、`results/key-deletion.json`、`results/key-pre-delete.txt`、`results/local-install-attempt.json`、`results/install-attempt.json`、`results/ACCEPTANCE_MAPPING.md`。
- 隔离现场：`runtime/optimization/2026-10-09/M0/r7/`（home、tmp、cache、config、data、staging、local-mirror、install-root、keys 已销毁、probe、install_probe、results、snapshot、source-pin）。
- 钉版官方源码：`runtime/optimization/2026-10-09/M0/r7/source-pin/OctoSense-App-Hub/`（含完整 crate；SHA 与 r5/source 5 文件 1:1 一致）。
- 私钥销毁：`results/key-deletion.json` 完整记录销毁前 SHA、销毁命令、销毁后公开锚验证。
- GATES.json M0 条目更新：候选 r7；D-R5-1/2/3/4/5 全闭合；D-R4-4 维持 BLOCKED；D-R4-5 UI 部分维持 BLOCKED；状态 READY_FOR_REVIEW。
- r1–r6 报告与 Review 原文保留。

**真实桌面 UI 触发、提醒/任务跳回、可信双主体、未配置的真实模型 provider —— 这些仍需 Abram 后续裁决或后续模块（M2/M3/M5/M6）真实环境实测。**

**编码方交接完成，待独立 Review；不进入 M1。**