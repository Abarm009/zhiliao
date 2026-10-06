# B 版组件版本来源（SOURCES · 固定版本锁定）

> 任务书：「获取最新官方规范并固定构建版本」「按官方要求使用相互兼容的依赖；不要把各依赖随意更新到各自 main」。本文件列出 B 版构建所用的所有官方组件版本、commit SHA 与相互兼容关系。
>
> **本轮 review（B 版独立复审）后的口径修正**：B 版卡在固定旧宿主候选上——`card-host` / `hub` 二进制 mtime 仍为 `2026-10-01 11:30`，与 App Hub HEAD `6741dea` / Shell HEAD `a5d847a` 在本机 lockfile 锁定。**官方 OctoSense main 与本机二进制不是同一时间锚点**：本机 bin 不能证明已编入 OctoSense main 上游的最新提交，本版不声称「最新 OctoSense 已验证」。详见 [§6 兼容性矩阵与已知偏差](#6-兼容性矩阵与已知偏差)。

## 1. OctoSense App Hub（宿主 CLI 与运行时）

- **仓库**：`https://github.com/OctoSense-org/OctoSense-App-Hub`
- **HEAD（本地 `.git`）**：`6741dea`（`runtime/native-build/OctoSense-App-Hub` 内含 `.git`，HEAD 已 pin）
- **构建时间**：2026-10-01 11:30（`target/release/{hub,card-host}` mtime）
- **二进制**：
  - `runtime/native-build/OctoSense-App-Hub/target/release/hub` — 1.9 MB arm64 Mach-O
  - `runtime/native-build/OctoSense-App-Hub/target/release/card-host` — 25 MB arm64 Mach-O
- **作用**：`hub` CLI 提供 stamp / check / scan / sign-manifest / publish / withdraw / remove 等命令；`card-host` 是宿主进程，加载 bundle 并向浏览器/外部提供原生界面渲染与脚本执行。
- **已知偏差**：上游 App Hub main 当前 head 与本机 `6741dea` 不一致；本机二进制对应 `6741dea` 的 cargo 依赖锁，未重编入上游最新 commit。

## 2. OctoSense（card-host 渲染核心）

- **仓库**：`https://github.com/OctoSense-org/OctoSense`
- **HEAD（上游 main）**：`4081c30e432ad0c3d0260c90be804d5e8aa5a9a1`
- **本地**：通过 OctoSense-App-Hub 的 cargo dependency 引入（指向 Hub@6741dea 的 Cargo.lock）。
- **作用**：card-host 的 UI 与脚本调度核心。
- **已知偏差**：本机 card-host 二进制 Cargo.toml 锁定的 `OctoSense` 提交与 OctoSense main 上 `4081c30e` 是**不同 commit**——前者来自 Hub@6741dea 的 lockfile，后者是上游 main。本机二进制不包含 OctoSense main 最新代码。

## 3. OctoScript-App-Design-Flow（脚本语言参考与示例）

- **仓库**：`https://github.com/OctoSense-org/OctoScript-App-Design-Flow`
- **HEAD（上游 main）**：`a5a87d3c`
- **本地参考**：未直接嵌入构建；用于核对官方 `main.splash` 用法、UI 控件、`fn tick()` / `ui.<name>.set_text()` 模式。
- **特别说明**：仓库 README 中 9/27 的 AI 状态已落后——Shell 已合入 `model.complete`、contained octos 和 glance，但助手默认关闭、需内核与首次同意、工具审批仍拒绝；manifest agent 文件准入不等于后台 Agent 运行。本 B 版不依赖 AI 路径。

## 4. Octoscript / Octoscript-Makepad / Makepad（脚本编译 + Makepad 渲染）

- **Octoscript**：`octoscript-core/src/lib.rs:6813` 列出 `me` 为 builtin；`3847` 列出 `pick(object, ...)` 为 builtin。B 版重命名 `me` → `getMe`、`pick` → `pickUser` 即基于这两处定位。
- **HEAD（Octoscript）**：`68f6a9df`（与 Hub@6741dea Cargo.lock 锁定）
- **HEAD（Octoscript-Makepad）**：`b33f494b`
- **HEAD（Makepad）**：`4fdcfccc`
- **本地路径**：`runtime/native-build/octoscript/`、`runtime/native-build/octoscript-makepad/`、`runtime/native-build/makepad/`（**裸目录无 .git**，仅作源码只读快照；版本锁定由 OctoSense-App-Hub 的 Cargo.lock 保证）

## 5. OctoSense-Shell

- **HEAD**：`a5d847a`
- **本地路径**：`runtime/native-build/OctoSense-Shell/`（裸目录）
- **作用**：card-host 依赖的 Shell 组件，提供宿主基础（fs 隔离、tick 调度、widget 树渲染）。

## 6. 兼容性矩阵与已知偏差

| 组件 | 本机二进制锁定的版本 | 上游 main HEAD | 一致？ |
|---|---|---|---|
| OctoSense-App-Hub | `6741dea`（本仓含 `.git`） | `78dfda5f33638e1869c36bceef5713342aae861c` | ✗（上游更新，未重编） |
| OctoSense | 由 Hub@6741dea lockfile 锁定 | `4081c30e432ad0c3d0260c90be804d5e8aa5a9a1` | ✗（上游更新，未重编） |
| Shell | `a5d847a` | 取决于 Hub@6741dea 内部 Cargo.lock | △ |
| Octoscript | `68f6a9df` | 由上游 main 演进中 | △ |
| Octoscript-Makepad | `b33f494b` | 同上 | △ |
| Makepad | `4fdcfccc` | 同上 | △ |

**结论**：本机 `runtime/native-build/` 下的 `octoscript` / `octoscript-makepad` / `makepad` / `OctoSense-Shell` **均为裸目录无 `.git`**，其版本号仅可由 OctoSense-App-Hub@6741dea 的 `Cargo.lock` 反推。上游 main 当前与本机 lockfile 存在 commit 差异；**最新 OctoSense 兼容性的独立验证未做**。

要严格证明「最新 OctoSense 兼容性」，需要在独立目录按上游 main 的 lockfile 完整重编 `card-host` 与 `hub`，记录构建输出与二进制摘要，并重复本文档 [§8 时间线](#8-验证时间线) 的全部实测。本轮未做这一步。

**保留口径**：本 B 版是「固定旧宿主候选（Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc）」；不声称「最新 OctoSense 已验证」。

## 7. 本应用组件（本仓库）

| 文件 | 角色 |
|---|---|
| `app/bundle/main.splash` | 974 行 OctoScript 脚本；声明 widget 树、状态机、命令函数、tick；B-R01/B-R02/B-R03/B-R05 修复均在此 |
| `app/bundle/manifest.json` | bundle 元数据；version=`0.1.0-b`；capabilities=[storage]；integrity.bundle_blake3 见 [§8](#8-验证时间线) |
| `app/bundle/listing.json` | 商店页元数据；publisher、release_notes、screenshots |
| `app/bundle/assets/icon.svg` | 应用图标（371 字节） |
| `app/bundle/screenshots/*.png` | 8 张截图（A 版 2 张 + B 版 6 张） |

## 8. 验证时间线

| 时刻（Asia/Shanghai） | 动作 | 输出 |
|---|---|---|
| 2026-10-06 22:05 | 复制 6 张原生截图到 bundle | `app/bundle/screenshots/b0*.png` |
| 2026-10-06 22:08 | 更新 listing.json（B 版 release_notes） | `app/bundle/listing.json` 3.2 KB |
| 2026-10-06 22:09 | `hub stamp app/bundle` | `1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca` |
| 2026-10-06 22:09 | `hub check app/bundle --allow-unsigned` | PASSED（unsigned warning） |
| 2026-10-06 22:09 | `hub scan app/bundle --packet ...` | 7 项 packet（由发布者自答，route=pass） |
| 2026-10-06 22:10 | 写 7 项答复 | `check/03-scan-packet.answers.md` |
| 2026-10-06 22:11 | 打 zip | `bundle/octosense-repair-0.1.0-b.zip` 1.5 MiB |
| 2026-10-06 22:11 | 二次 stamp 验证幂等 | 同 `1ac7bb26...` ✓ |
| 2026-10-06 23:25 | review 反馈 → 修 B-R02 `runCommand`（hit/conflict 路径恢复；消除 `hit.hit` 字段访问错误） | stamp `ab69db47...` |
| 2026-10-06 23:35 | review 反馈 → 修 B-R03 events.jsonl 改数组格式 + B-R01 addEvidence 写 demo:true/ready:false + B-R05 visible 过滤 | stamp `5503136c95285db99b7ab95ef151073803ee26da424ccd589f34a9bc0c5e32a1` |
| 2026-10-06 23:38 | `manifest.json` version 改为 `0.1.0-b`；重新 stamp；check 显示 `octosense-repair 0.1.0-b — PASSED` | stamp `1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96` |
| 2026-10-06 23:50 | 真实宿主验证 B-R01（addEvidence → submitCompletion 阻断）、B-R03（重启 9→9 events 恢复）、B-R05（visible 过滤）、B-R02（runCommand 路径） | 见 `check/probe-results-b-r01.json` 与 `check/probe-results-b-r03.json` |
| 2026-10-07 00:30 | recheck 反馈 → 修 P0 旧版假 READY 证据：load 时 `scrubLegacyEvidence()` 检测 `sha=="demo-sha"` / `bytes==1024` / `name.starts_with("demo-")` 改为 `ready:false, demo:true, bytes:0, sha:""` 并 saveTasks 覆盖 | stamp `1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96` |
| 2026-10-07 00:35 | recheck 反馈 → 旧 JSONL 多行不兼容：`loadJsonlLines` 整体 parse 失败时（旧 JSONL 不是合法 JSON 数组），备份 `events.jsonl.legacy.<ts>.bak` 并写 `[]`（不假装解析 9 条事件） | 同上 stamp |
| 2026-10-07 00:40 | 旧 demo 数据实测：legacy tasks.json 含 `bytes=1024, sha=demo-sha, ready:true` → load 后被 scrub 为 `bytes:0, sha:'', demo:true, ready:false` | evidence 写入确认 ✓ |
| 2026-10-07 00:45 | 旧 JSONL 实测：手工 9 条 JSONL dict 写入 events.jsonl → load 后 events.jsonl 被备份 + 写空，旧 9 条完整保留在 `events.jsonl.legacy.*.bak` | 备份文件确认 ✓ |
| 2026-10-07 00:50 | 动态幂等验证（review 第 4 项）：UI 路径下每次 click 生成新 LAST_KEY，runCommand hit/conflict 分支代码已恢复但 UI 不可达——保留 review 备注 | 见 `check/probe-results-b-idempotent.json` |

## 9. 与 A 版的版本边界

A 版固定 commit `6d81d57b1436c6df3c233b65b9313e3a3bf9d84b`，材料在 `submission/2026-10-06/`。**两条交付互不覆盖**：

| 字段 | A 版（`6d81d57b`） | B 版（本仓工作树，commit 待冻结） |
|---|---|---|
| bundle 文件 | `octosense-repair-0.1.0.zip` | `octosense-repair-0.1.0-b.zip` |
| `manifest.version` | `0.1.0` | `0.1.0-b` |
| `integrity.bundle_blake3` | `eff13f557080fc12ac2961f6bee83a2365f3d8fb5ac0e56681cee45b13c4ad26` | `e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`（recheck 后最终） |
| ZIP sha256 | `3cb784dbc4fe2bb3a072621a1c6db7f62d718643b1b1992d33812b0980b6f49b` | 见 `SHA256SUMS` |
| main.splash 行数 | 1002（含 ScrollYView） | 974（单页紧凑布局 + review 修复） |
| 截图 | 7 张（A 版工作台） | 6 张原生 + 2 张 A 版占位 = 8 张 |

**注意**：本轮之前 SOURCES / README 中曾错误标注 A 版 blake3 为 `23e56ea0...`（那是上一轮重 stamp 前的旧值），实际 A 版 commit `6d81d57b:app/bundle/manifest.json` 上的真实值是 `eff13f55...`。**修正后的版本以上表为准**。
