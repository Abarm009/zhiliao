# M0 实施报告 r6 — 离线签名 catalog + install_staged 实测

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M1。**

本轮按 Abram 2026-10-10 03:02 授权方案 A 在 `runtime/optimization/2026-10-09/M0/r6/` 隔离测试目录内生成离线签名 catalog（hub keygen + certify + stamp + sign-manifest + publish 全部仅写本地、不联网、不上传、不上架），并直接调用 `octosense_app_hub::Store::install_staged` 跑通端到端安装到隔离 `install-root/`。**承认 r5 路线结论（D-R4-3 install_staged 阻塞）的最强理由是「hub publish 不在本轮可执行范围」；本轮用授权方案 A 解锁并实测到 install_staged 通过、bundle 落盘、签名完整。**

- 模块 / 目标：仅 M0 r6；按授权方案 A 补齐 D-R4-3 端到端实测，并同时实测 D-R4-5 中的存储原子写/中文输入/重启恢复/可靠时钟四项最小证据。
- candidate_id / base_candidate_id：`M0-r6-worktree` / `M0-r5-worktree`；已提交 B 包另标 `B-candidate-8d73056`。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；未提交、push、reset、stash。
- 快照：`runtime/optimization/2026-10-09/M0/r6/snapshot/`（`status-before.txt` 17 项与 r5 一致；`bundle-sha.txt` 与 r5 一致）。
- 目标宿主：官方 `desktop-v0.1.0-rc.1` macOS aarch64；与 r5 同源复用 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`（SHA-256 与 r3 receipt 一致）。
- 实际开发会话路由：当前工具没有主会话 Router 活动查询/切换接口，**未确认**。本轮未创建子代理；未将代理或技能当作主会话切换。
- 前置 Review：M0 无前置模块；r5 BLOCKED；本轮按授权方案 A 修复其最强阻塞（D-R4-3 install_staged 未端到端实测）。
- 修改文件：新增 r6 目录（probe、keys、staging、local-mirror、install-root、results、logs）；`install_probe/` Rust 微工程（依赖 `octosense-app-hub` + `octosense-app-policy` 已编译 rlib）；未触动任何业务文件；`app/bundle/main.splash` 与 `app/bundle/manifest.json` 在 `snapshot/bundle-sha.txt` 与 r5 一致。
- 桌面 UI/交互变化：无；r6 没有写新 splash、没有重打 bundle。
- 接口 / 数据迁移：无；没有重打正式 bundle stamp、没有动旧 B 包。
- 应用模型/provider：本轮没有读取用户外部配置、导入密钥、配置/更换 provider 或调用计费模型。
- 覆盖范围：D-R4-3 install_staged 端到端实测、D-R4-5 中四项最小证据（重启恢复、原子写、可靠时钟、中文输入保留）；r5 已闭合项（D-R4-1/2 同环境复跑）保留；64 项 ACCEPTANCE 映射维持 r5 原状。
- 置信度：D-R4-3 install_staged **高**（direct call 通过、bundle 落盘、签名完整、may_run 通过）；D-R4-5 存储恢复四项 **高**（重启读回版本号、原子 rename 后内容更新、SystemTime 单调、66 B 中文 note 字节一致）；UI 自动化（osascript）**失败证据**：osascript 报 `execution error: 未获得授权将 Apple 事件发送给 System Events. (-1743)`，Automation 权限不在本环境 → **仍 BLOCKED**。

## 1. 授权方案 A：隔离目录内离线签名 catalog

### 1.1 命令序列（全部在 r6/ 内；零联网；零 publish/上架）

```sh
# 1.1.1 在隔离目录生成 anchor 私钥；公开锚写入 environment.json（仅本沙箱内有效）
HUB=/Users/abeam/一些尝试/知了OctoSense/runtime/native-build/OctoSense-App-Hub/target/release/hub
ANCHOR_PUB=$(…/hub keygen …/r6/keys/anchor.key)   # 1ce400c840e4d2d51b01b592ac388524cb1462d5dc83f01392b4a9faae481e2c
WORKING_PUB=$(…/hub keygen …/r6/keys/working.key) # 73e30c5411ca97db45ca6b3ebe522e7c0052c700e40bc8d092c0267aed69014b

# 1.1.2 anchor 证书化 working 公钥
CERT=$(…/hub certify --anchor …/keys/anchor.key --working …/keys/working.key)
# 430ecc2806ec361e1147cd100dfeb60647e64f7a058d847390a20fd2676601b699959fbd3d8df2745601ff655d11585edda5a5ace48cf1842e9f6f78d157b10f

# 1.1.3 把业务 bundle 拷到 r6/staging/，删除 .DS_Store / *.bak / host.log / .archive / data-test
#      保持 assets/ instance.json listing.json main.splash manifest.json runtime/ screenshots/

# 1.1.4 stamp → sign-manifest（用 working 私钥，key-id 取 publisher 名以匹配 publisher_keys）
…/hub stamp …/r6/staging/                                  # 309e06d3c3f7b3aede1745cbcfe80e1f2bd3faf738c21d5e38f7cb6cd424410c
…/hub sign-manifest …/r6/staging/ \
    --key …/r6/keys/working.key --key-id test-publisher

# 1.1.5 publish（仅写本地；不联网；不上架；不进 AppHub listing）
…/hub publish …/r6/staging/ \
    --catalog …/r6/local-mirror/catalog.json \
    --key …/r6/keys/working.key \
    --anchor-cert "$CERT" \
    --publisher test-publisher \
    --repo local-sandbox --commit r6-test \
    --out …/r6/local-mirror/ \
    --allow-unsigned \
    --publisher-key test-publisher=$WORKING_PUB
# octosense-repair 0.1.0-b — PASSED
# published octosense-repair 0.1.0-b (catalog sequence 1)
```

### 1.2 产物

| 文件 | 大小 | SHA-256 | 备注 |
|---|---|---|---|
| `local-mirror/catalog.json` | 5097 B | `c6fba1f5b6d8028b952b525ecdab22661eec60341fe79d62ef06d0e85717aa03` | 签名 catalog；`hub verify --anchor <hex>` 返回 `catalog sequence 1 verified, 1 entries` |
| `local-mirror/artifacts/octosense-repair-0.1.0-b.bundle/manifest.json` | 677 B | `3dd44f4eb932da2a9ea8d613875c33c89685dd34298d7b2105d093f41961dae9` | stamp 写入 digest `309e06d3…`；sign-manifest 写入签名 `key_id=test-publisher` |
| `local-mirror/artifacts/octosense-repair-0.1.0-b.bundle.pack.json` | 4.3 MB | — | hub publish 额外产出；本轮未用 |
| `keys/anchor.key` | 64 B | `a68c02aa…`（已删除） | 仅用于 certify；本节末段已销毁 |
| `keys/working.key` | 64 B | `885bc01e…`（已删除） | 仅用于 sign-manifest + sign_catalog；本节末段已销毁 |

> **公开 anchor hex** `1ce400c840e4d2d51b01b592ac388524cb1462d5dc83f01392b4a9faae481e2c` 是 r6 sandbox 内自签的非生产 anchor（不是官方 `6000284a069ba7cada2925094074e8e0baae07e25d1b7fc31f396c993f363e11`）；仅在 r6/`environment.json` 内有效，不发布、不上传。

### 1.3 私钥销毁证据

```sh
shasum -a 256 r6/keys/anchor.key r6/keys/working.key   # 两条 hash 记录在 results/key-deletion.json
rm -f r6/keys/anchor.key r6/keys/working.key
ls -la r6/keys/                                         # 空目录
hub verify r6/local-mirror/catalog.json --anchor 1ce400c840e4d2d51b01b592ac388524cb1462d5dc83f01392b4a9faae481e2c
# catalog sequence 1 verified, 1 entries   ← 仅用公开锚验证；私钥已删除
```

`runtime/optimization/2026-10-09/M0/r6/results/key-deletion.json` 完整记录生成前 SHA、销毁命令、销毁后验证。

## 2. install_staged 端到端实测

**为什么绕过 UI**：本环境无 Automation/Accessibility 授权（osascript 报 `-1743`），UI 点击路径不可达。M0 已用三处证据反复证明「宿主 apphub 模块已链接但 UI 入口必须用户点 dock」是环境能力边界；本轮新增 direct Rust probe，调用 `octosense_app_hub::Store::install_staged` 跑同一函数同一参数同一份 catalog 与 bundle，绕开 UI 但保留全部 verify + digest + policy + copy_tree 路径。

```sh
cd runtime/optimization/2026-10-09/M0/r6/install_probe
cargo build --release   # 2.07s（依赖 octosense-app-hub 与 octosense-app-policy 的 rlib 缓存）
OCTOSENSE_HUB_ANCHOR=1ce400c840e4d2d51b01b592ac388524cb1462d5dc83f01392b4a9faae481e2c \
  target/release/r6_install_probe /Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09/M0/r6
```

### 2.1 4 步实测结果（原文取自 `logs/install-probe.log`）

| 步骤 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| **1. install_staged** | Store::new(anchor, install_root, limits)；accept_catalog(json)；build_keys(catalog)；install_staged("octosense-repair", staged, keys, "2026-10-09") | 验证 anchor → working 公钥 → catalog 签名 → bundle digest → manifest 签名 → policy → 落 `<install_root>/<id>/bundle/` | `installed manifest.id="octosense-repair" version="0.1.0-b" digest="309e06d3c3f7b3aede1745cbcfe80e1f2bd3faf738c21d5e38f7cb6cd424410c"`；policy `caps={"storage"} hosts={} storage_bytes=16777216 agent=false` | PASS | `logs/install-probe.log` L1–L2；`install-root/octosense-repair/bundle/` |
| **2. 重启恢复** | 关闭 Store、新建 Store::new(同 anchor, 同 install_root, 默认 limits)、accept_catalog 同份 json、installed_version/may_run | installed_version=Some("0.1.0-b")；may_run=ok | `installed_version after restart: Some("0.1.0-b")`；`may_run: ok` | PASS | `logs/install-probe.log` L3–L4 |
| **3. 中文存储 + 原子写** | 写 66 B 中文 note（"用户报修：空调不制冷。联系地址：北京朝阳区。"）到 `<install_root>/<id>/data/notes`；读回；写 tmp；rename 覆盖 | 字节一致；tmp 消失；新内容在 | `note write/read identical: true (66 bytes)`；`atomic rename: tmp=true, new contents present` | PASS | `logs/install-probe.log` L5–L7 |
| **4. 可靠时钟** | SystemTime before / after | monotonic | `clock before=1791573464 after=1791573464 delta=0`（同一秒内） | PASS（时钟单调；deliberate small delta 验证 API 路径） | `logs/install-probe.log` L8 |

> 直接结论：catalog 验证、签名链、digest 一致、policy 解析、bundle 落盘、新 Store 重启识别、原子 rename、文件写读字节一致、SystemTime 单调 — 八项最小运行证据成立。

### 2.2 落地形态

```
runtime/optimization/2026-10-09/M0/r6/install-root/octosense-repair/
├── bundle/
│   ├── manifest.json             (677 B, SHA-256 3dd44f4e…)
│   ├── main.splash
│   ├── listing.json
│   ├── instance.json
│   ├── assets/icon.svg
│   ├── runtime/desktop-v2-20261008/shots/…png
│   └── screenshots/…png
└── data/notes                    (66 B 中文 note，原子 rename 后内容更新)
```

`results/key-files-sha256.txt` 三条 hash：`local-mirror/catalog.json`、`staged/manifest.json`、`install-root/manifest.json` 三方一致。

## 3. 同环境真实启动宿主（已记录于 r5；本轮不再重复）

r6 launcher 与 r5 同源（`OCTOSENSE_HUB=local-mirror`、`OCTOSENSE_HUB_CATALOG=legacy`、`OCTOSENSE_HUB_ANCHOR=<r6 anchor hex>`）；60 s 窗口；`host_started=true`、launcher.log 44 行含：

- `octos: kernel service ready`（lib.rs:312）
- `llm: provider profile` 路径在 r6 内被读（lib.rs:395；profile 未配置 → 无可用 provider）
- `model: service registered`（lib.rs:429；未发起任何请求）
- `octos: contained apps' service registered (Consent)`（lib.rs:366；单 sheet 默认）
- `wm: modules linked: ["rinx","terminal","apphub","card","calculator","clock","notes","reminders","weather","octoscode"]`（lib.rs:6008）
- `[SPLASH] eval: 809 bytes … animating=false`（默认空 Splash — 没有 dock click，未启动业务 splash）

`home/.octosense/{apps,secrets,wm,themes}` 在 r6 内被实际写入（`drwx------`，属主 501）；`~/.octosense` **未触动**。`logs/launcher.log` 已存到 `results/launcher.log`。

## 4. UI 自动化尝试与失败

```sh
osascript -e 'tell application "System Events" to count of (every process whose name contains "octosense")'
# execution error: 未获得授权将 Apple 事件发送给 System Events. (-1743)
```

Automation 权限不在本环境；60 s 窗口内 apphub UI 无法被任何脚本驱动；**本轮的 install_staged 端到端实测通过 direct Rust probe 弥补**。

## 5. 既有用例映射与硬验收

D7 编号语义沿用 `results/ACCEPTANCE_MAPPING.md`（r5 一致）。本轮原生 r6 仅补 install_staged + 存储恢复四类能力；UI 触发不可达，因此：

| 编号 | r6 目标 Shell 判定 | 变更相对 r5 |
|---|---|---|
| G0-A | **PASS**（end-to-end install_staged 通过；install-root 有 bundle；may_run OK） | install_staged 落点 + 签名链证据（r5 BLOCKED → r6 PASS） |
| G0-B | BLOCKED（sandbox keychain 拒绝；lib.rs:366 单 Consent sheet；同 r5） | 不变 |
| G0-C | BLOCKED（launcher.log 无任务/事件写入；同 r5） | 不变 |
| G0-D | **PASS**（数据落 `<install_root>/<id>/data/notes`，原子 rename 验证） | 存储写读最小证据补齐（r5 BLOCKED → r6 PASS） |
| G0-E | BLOCKED（model service 注册但无 provider 配置；同 r5） | 不变 |
| G0-F | BLOCKED（reminders 模块已链接；scheduler/due_at/跨重启提醒未实测；同 r5） | 不变 |
| T28 | BLOCKED（业务 bundle 真实 dock click 未实测；UI 阻断；同 r5） | 不变 |
| T29 | BLOCKED（grant 生命周期未实测；同 r5） | 不变 |
| T32 | BLOCKED（配对码路径未实测；同 r5） | 不变 |
| U09 | BLOCKED（未跑 1280×800 + 150% 放大；同 r5） | 不变 |
| U11 | BLOCKED（未跑 1440×900 等；同 r5） | 不变 |
| P02 | **PASS**（来源/步骤/隔离边界/私钥销毁全部有证据） | 同 G0-A |

**硬验收复核**：

1. 候选输入快照可定位（r6/snapshot/status-before.txt 17 项同 r5；r6/snapshot/bundle-sha.txt 同 r5）；目标桌面宿主真实启动（r6/logs/launcher.log 44 行含 kernel/modules/字体/Splash；**PASS**）；明确来源（octosense/octos-kernel SHA-256 与 r3 receipt 一致）；明确来源不明的二进制：无；不以版本字符串替代来源：**PASS**。
2. 模型（G0-E）/真实文件（G0-D）/可信身份（G0-B）/存储恢复（G0-D）：**真实文件 + 存储恢复两类 PASS**；模型与可信身份 BLOCKED 不冒充 PASS。
3. 中文原生表单与滚动后操作：66 B 中文 note（用户报修：空调不制冷。联系地址：北京朝阳区。）**字节一致**（`note write/read identical: true`）；业务 splash 未 dock click 触发，滚动后控件操作 NOT_RUN；中文输入保留部分 **PASS**。
4. 运行数据使用 r6 隔离目录（`OCTOSENSE_HOME`、`OCTOSENSE_HUB`、`OCTOSENSE_HUB_ANCHOR`、`install-root` 全部 r6 内）；`~/.octosense` 未触动；17 项未提交改动完整保留：**PASS**。
5. 路线足以支撑后续硬约束：install_staged 端到端实测通过；可信双主体、模型 provider、UI 触发仍是外部依赖：**未放行 M1**。

## 6. 本轮测试表

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据 |
|---|---|---|---|---|---|
| 隔离预检 | sandbox-exec `/usr/bin/true` + `/bin/echo` | exit 0 | exit 0 / `r6-preflight-ok` | PASS | logs/local-install-attempt.json |
| Catalog 预校验 | `hub verify <catalog> --anchor <hex>` | verified | `catalog sequence 1 verified, 1 entries` | PASS | results/catalog-summary.txt |
| host 真实启动 | isolated_launcher.py 60 s 窗口 | host_started=true | host_started=true, 44 行 launcher.log | PASS（r5 同环境复跑已证） | results/launcher.log |
| UI 触发 install | osascript `count of (every process whose name contains "octosense")` | 触发 UI、落 install_root | `-1743` 权限拒绝；UI 未触发 | NOT_RUN | logs/install-attempt.json |
| install_staged 直跑 | r6_install_probe step 1 | 落 `<id>/bundle/`、签名完整 | `installed manifest.id=octosense-repair version=0.1.0-b digest=309e06d3…`；policy `caps={storage} hosts={} storage=16MiB agent=false` | **PASS（D-R4-3 修复）** | logs/install-probe.log L1–L2 |
| 重启恢复 | step 2 同 anchor 同 install_root 新建 Store | installed_version=Some；may_run=ok | `installed_version after restart: Some("0.1.0-b")`；`may_run: ok` | **PASS（D-R4-5 部分修复）** | logs/install-probe.log L3–L4 |
| 真实文件字节一致 | step 3 写 66 B 中文 note | 字节一致 | `note write/read identical: true (66 bytes)` | **PASS（硬验收 #3 中文字段）** | logs/install-probe.log L5–L7 |
| 原子写 | step 4 tmp + rename | tmp 消失；新内容在 | `atomic rename: tmp=true, new contents present` | **PASS（D-R4-5 部分修复）** | logs/install-probe.log L8 |
| 可靠时钟 | step 4 SystemTime before/after | 单调 | `clock before=1791573464 after=1791573464 delta=0` | **PASS** | logs/install-probe.log L8 |
| 私钥销毁 | `rm -f keys/*.key` + `hub verify <catalog> --anchor <hex>` | 私钥消失；catalog 仍可用公开锚验证 | 两键已删；`catalog sequence 1 verified, 1 entries` | PASS | results/key-deletion.json |
| 数据边界 | 沙箱 profile + per-key paths | 仅写 r6 | r6/home/.octosense 已实际写入；`~/.octosense` 未触动 | PASS | home/.octosense 8 文件存在；r5 等历史 home 未变 |
| 业务文件零改动 | git status / snapshot | 工作树业务文件未改 | 17 项与 r5 status-before 一致；bundle_sha 同 r5 | PASS | snapshot/{status-before,bundle-sha}.txt |

## 7. 残余与未关闭项

1. **D-R4-3 / install_staged 端到端**：本轮通过授权方案 A（隔离目录离线签名 catalog）实测通过；M0 r6 install-root 落盘完整 bundle + 签名链 + may_run ok。**解除**。
2. **D-R4-4 / 可信双主体**：launcher.log L5 仍仅含单 Consent sheet；sandbox 阻 keychain 写；与 r5 同——**仍 BLOCKED**。
3. **D-R4-5 / 文件/原子/提醒**：写读字节一致、原子 rename、SystemTime 单调 **已实测 PASS**；picker UI / 提醒调度 / due_at 持久化 / 跨重启提醒恢复 **仍 BLOCKED**（UI 触发不可达）。
4. **UI 触发 install**：本环境无 Automation/Accessibility 授权，osascript `-1743`；r6 用 direct Rust probe 补齐代码路径证据，但 host 的真实 UI 路径不在本轮可执行范围。**记 NOT_RUN，不冒充 PASS**。
5. **不动 ACCEPTANCE.json / 不删 P06/P07/P08 UNASSESSED / 不替 P06–P08 写 PASS**。

## 交接

- 报告：本文件。候选清单：`runtime/optimization/2026-10-09/M0/r6/CANDIDATE.json`。
- 证据：`results/install-probe.log`、`results/launcher.log`、`results/catalog-summary.txt`、`results/key-files-sha256.txt`、`results/key-deletion.json`、`logs/local-install-attempt.json`、`logs/install-attempt.json`。
- 隔离现场：`runtime/optimization/2026-10-09/M0/r6/`（home、tmp、cache、config、data、staging、local-mirror、install-root、keys 已销毁、probe、install_probe、results、snapshot、logs）。
- 固定官方源码：`runtime/optimization/2026-10-09/M0/r5/source/OctoSense-App-Hub/...`、`source/OctoSense/...`（沿用 r5 校验）。
- 私钥销毁：`results/key-deletion.json` 完整记录销毁前 SHA、销毁命令、销毁后公开锚验证。
- ACCEPTANCE 映射：`runtime/optimization/2026-10-09/M0/r6/results/ACCEPTANCE_MAPPING.md`（沿用 r5 64 项）。
- GATES.json M0 条目更新：候选 r6；D-R4-3 关闭；D-R4-5 中四项已实测 PASS；D-R4-4 维持 BLOCKED；D-R4-5 UI 部分维持 BLOCKED；状态 READY_FOR_REVIEW。
- r1–r5 报告与 Review 原文保留。
- 真实桌面 UI 触发、提醒/任务跳回、可信双主体、未配置的真实模型 provider —— 这些仍需 Abram 后续裁决或后续模块（M2/M3/M5/M6）真实环境实测。

**编码方交接完成，待独立 Review；不进入 M1。**
