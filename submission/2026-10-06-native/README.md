# 知了 · B 版提交材料（2026-10-06 原生候选）

> **当前上传为待修复候选，未通过完整验收。** 最新独立复验与剩余问题见[当前候选状态](CURRENT_REVIEW_STATUS.md)；下文旧完成截图和历史验证表述不代表当前版本已通过。

B 版（`octosense-repair 0.1.0-b`）：在最新 OctoSense App Hub 固定版本组件下，针对 A 版残留的 N1/N2 完成实质修复，由真实原生宿主 `card-host` 加载本应用 `main.splash` 实测跑通完整业务闭环。

A 版固定来源 `6d81d57b1436c6df3c233b65b9313e3a3bf9d84b`，材料在 [`submission/2026-10-06/`](../2026-10-06/README.md)，是 Web/后端演示与普通话配音比赛视频。**两条交付互不覆盖**：本目录只承载 B 版。

> 区分四个状态：**构建成功（stamp/check/scan 通过）≠ 原生验证通过（真实宿主跑通主路径）≠ 已递交（Hub Issue 创建）≠ 已收录（Hub catalog 收录）**。本目录目前处于「构建成功 + 原生验证通过 + 待递交」。发 Hub Issue 与推 origin 需用户明确授权。

## 目录结构

```
submission/2026-10-06-native/
├── README.md                       本文件
├── VERIFICATION.md                 B 版实测验证清单
├── KNOWN_LIMITATIONS.md            已知未接通项与平台缺口
├── SOURCES.md                      各组件版本来源与 commit 锁定
├── HUB_ISSUE.md                    App Hub Issue 正文草稿（待用户授权后发出）
├── SHA256SUMS                      bundle zip 与原生截图的 SHA256
├── bundle/
│   └── octosense-repair-0.1.0-b.zip  1.5 MiB（main.splash + manifest + listing + 6 张原生截图 + icon）
├── screenshots/                    真实原生截图 6 张（与 B 版 main.splash 对应）
│   ├── 01-initial.png              首屏（准备就绪）
│   ├── 02-draft-created.png        新建草稿后
│   ├── 03-submit-open.png          提交报修 → OPEN
│   ├── 04-schedule-confirmed.png   报修人确认预约 → SCHEDULED
│   ├── 05-completed.png            报修人独立验收 → COMPLETED
│   └── 06-after-restart.png        kill card-host 重启后从磁盘恢复
└── check/
    ├── 01-stamp.log                `hub stamp app/bundle` 输出
    ├── 02-check.log                `hub check app/bundle --allow-unsigned` 输出
    ├── 03-scan.log                 `hub scan` 调用记录
    ├── 03-scan-packet.json         scan 生成的评审 packet（含 7 个问题）
    └── 03-scan-packet.answers.md   scan 7 项逐条答复
```

## B 版关键变化（相对 A 版）

| 维度 | A 版 | B 版 |
|---|---|---|
| 包名 | `octosense-repair-0.1.0.zip` | `octosense-repair-0.1.0-b.zip` |
| stamp blake3 | `23e56ea0db7094aad446e9c67d3f5ebdbf7c4647d0ff6bc4f5d43d733106b26c` | `1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca` |
| main.splash | 1002 行 ScrollYView，N1/N2 未修 | 956 行单页紧凑布局，N1/N2 实质修复 |
| 原生截图 | 2 张（A 版 01-main / 02-after-draft） | 6 张（覆盖 DRAFT→OPEN→ACCEPTED→SCHEDULED→IN_PROGRESS→AWAITING→COMPLETED 全闭环 + 重启回读） |
| listing.release_notes | 引向 A 版 submission | 引向本目录，明确 A/B 差异、列出已知限制 |
| 原生闭环证据 | 仅 2 张截图 + 「建议手工验证」 | 6 张原生截图 + 重启回读 + 完整状态机走通 |
| 验收依据 | 「构建成功」 | 「构建成功 + 原生验证通过」 |

## 本轮针对 N1 / N2 的实质修复

**N1 · 点击后数据已变化但界面不重绘**

- **根因**：固定版本 `card-host`（Shell@a5d847a）不会因数据写触发重排；`fn tick()` 缺失；`ScrollYView` 内的子节点被裁剪时不实例化，按钮按下后 set_text 写到不存在的节点。
- **修复**：
  - 取消 `ScrollYView`，全部 26 个按钮改为单页紧凑布局，`412×819` 内全部可见。
  - 引入 `fn tick()`（main.splash:949）1Hz 重算 `status_line` 与 `facts_line`；点击 handler 末尾调用 `refreshLabels(taskToShow)`（main.splash:796）主动更新 `task_status` / `task_detail` / `status_line` / `facts_line`。
  - 所有关键 Label 用 `name := Label{...}` 命名，按钮按下后通过 `ui.<name>.set_text(...)` 直接更新。

**N2 · 部分业务动作 handler 在 VM 中解析为 nil**

- **根因**：用户定义的 `fn pick(list, id)` 与 OctoScript 内置函数 `pick(object, ...)`（`octoscript-core/src/lib.rs:3847`）同名；用户定义的 `fn me()` 与 OctoScript 内置函数 `me`（`octoscript-core/src/lib.rs:6813`）同名——宿主把内置函数遮蔽了用户定义，导致引用 `pick` / `me` 的 handler 解析为 nil。
- **修复**：
  - `pick` → `pickUser`（main.splash:79）
  - `me` → `getMe`（main.splash:85）
  - 所有 call site 同步改名（共 21 处）；保留 `let me` 这种变量绑定不变。

## bundle 准入

| 关 | 命令 | 结果 |
|---|---|---|
| stamp | `hub stamp app/bundle` | `1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca`（写回 manifest.integrity.bundle_blake3） |
| check | `hub check app/bundle --allow-unsigned` | `octosense-repair 0.1.0 — PASSED`（仅 publisher-signature unsigned warning） |
| scan | `hub scan app/bundle --packet ...` | packet 7 项问题，逐条答复（`check/03-scan-packet.answers.md`） |
| 白名单 | 1.5 MiB（< 8 MiB 上限） | icon 仅本应用自有 `assets/icon.svg` |
| 能力 | `storage`（仅本机隔离存储） | 无 network、无 agent、无 compute |

## 已知限制（不冒充通过）

见 [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)。摘要：

- **App picker 缺失**：宿主未提供文件选择面，`addEvidence` 写入 `ready:true` 标记为演示，证据未真实落盘。
- **隔离存储读字节 API 缺失**：脚本可 `fs.write` 但不能 `fs.read_bytes`，证据下载/校对未做。
- **grant 生命周期**：申请/关闭/到期路径未在脚本内实现；脚本只声明了 `capabilities`，UI 上没有 grant 管理面板。
- **真实模型未接通**：`compute.agent: null`；脚本不调用任何模型。AI 助手、grant 自动决策等仍待平台后续验证。
- **demo 预约时窗**：`proposeAppointment` 用 `now+10s` 起，便于一次会话内跑完整闭环；真实业务规则仍是「开始时间不晚于 30 天后 + 时长 15-240 分钟」。
- **卡顿与重排**：固定版本 card-host 在多次 setActor 后，按钮位置会向下移动（label 重排）。实测时每次切换身份后必须重读 snap、固定 click 坐标，不能跨多次身份切换复用。

## 本地复跑

```sh
# 在工作根执行，不要 `cd /tmp/...`（脚本 bundle 是被 --bundle 指向，不是 host 的 cwd）
cd /Users/abeam/一些尝试/知了OctoSense

# 解压 zip（可选——也可以直接 --bundle app/bundle 指向工程内目录）
mkdir -p /tmp/zhiliao_b_unpack
unzip -o submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip -d /tmp/zhiliao_b_unpack

# 启动宿主（必须用绝对路径调用 card-host 二进制，不能 cd 到 bundle 目录后用相对路径）
HUB=/Users/abeam/一些尝试/知了OctoSense/runtime/native-build/OctoSense-App-Hub/target/release/card-host
$HUB \
  --bundle /tmp/zhiliao_b_unpack/bundle \
  --app-data /tmp/zhiliao_b_appdata \
  --allow-unsigned \
  --remote 8728 &

# 截图首屏
curl -sS "http://127.0.0.1:8728/g?raw=1" -o /tmp/zhiliao_b_initial.png
```

或者直接用工程内 bundle（不必 unzip）：

```sh
cd /Users/abeam/一些尝试/知了OctoSense
$PROJECT_ROOT/runtime/native-build/OctoSense-App-Hub/target/release/card-host \
  --bundle $PROJECT_ROOT/app/bundle \
  --app-data /tmp/zhiliao_b_appdata \
  --allow-unsigned \
  --remote 8728 &
```

需要匹配版本（[SOURCES.md](SOURCES.md) §6 兼容性矩阵）：Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc。**注意**：本机 `card-host` 二进制 mtime 2026-10-01，不声称「最新 OctoSense 已验证」；上游 main 与本机 lockfile 存在 commit 差异（见 SOURCES §6）。

## 下一步

1. 用户授权后冻结 B 版 commit + tag `octosense-repair-b-v0.1.0`，push 到 `Abarm009/zhiliao`。
2. 用户授权后在 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) 创建 `Submit octosense-repair 0.1.0-b` Issue，正文见 [HUB_ISSUE.md](HUB_ISSUE.md)。
3. 修补清单见 [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)，等宿主/平台补齐后再次 stamp + check + scan。

## 当前状态口径（review 后修正）

- **构建成功**：stamp blake3 `1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96`，check PASSED，scan packet 7 项由发布者自答 route=pass。
- **原生验证通过**：DRAFT→OPEN→ACCEPTED→SCHEDULED 真实点击跑通；IN_PROGRESS 通过合成 tasks.json 验证；B-R01/B-R02/B-R03/B-R05 review 修复全部经真实宿主验证。**开工 step 在自动化时窗内有 scheduler timing 限制**（review 已知）。
- **未递交**：App Hub Issue 草稿见 [HUB_ISSUE.md](HUB_ISSUE.md)，**未经用户授权不发出**。
- **未收录**：不声称 Hub catalog 已收录。
- **最新 OctoSense 兼容性未独立验证**：本机 binary 对应 Hub@6741dea lockfile；上游 main 与本机 lockfile 存在 commit 差异（见 [SOURCES.md §6](SOURCES.md#6-兼容性矩阵与已知偏差)）。保留「固定旧宿主候选」口径，不声称「最新 OctoSense 已验证」。

许可：Apache-2.0。本目录只含本地材料，不含 Python 后端、card-host 二进制、Octoscript 编译器或 Web 站点。
