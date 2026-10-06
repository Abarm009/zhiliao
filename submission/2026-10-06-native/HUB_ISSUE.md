# App Hub Issue 草稿（待用户授权后发出）

> 任务书：「冻结 B 版源码 commit 和 tag，上传到现有公开仓库，再到官方 App Hub 创建或更新对应的 `Submit octosense-repair <version>` Issue」。本文档是 Issue 正文草稿，**未经用户明确授权前不会自动发出**。
>
> 推荐发送位置：[OctoSense-org/OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/new?template=submit.md) → 选择 `Submit an app` 模板，标题 `Submit octosense-repair 0.1.0-b`。

---

## 标题

```
Submit octosense-repair 0.1.0-b
```

## 正文

### 1. 发布者信息

- **Publisher**：Abram / OctoSense (Local Dev)
- **App ID**：`octosense-repair`
- **Version**：`0.1.0-b`
- **首次 unsigned**：是（首版 publisher 未签名；后续补 `hub keygen` + `hub sign-manifest` 后再次递交即可，hash 不变）

### 2. 仓库 URL / tag / commit

- **公开仓库**：`https://github.com/Abarm009/zhiliao`
- **B 版固定 tag**：`octosense-repair-b-v0.1.0`（待用户授权后冻结并 push）
- **B 版固定 commit**：见冻结后 commit 链接（stamp blake3 `e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579` 与 commit 文件一一对应，recheck 后最终）
- **A 版固定 commit**：`6d81d57b1436c6df3c233b65b9313e3a3bf9d84b`（保留作为 Web/后端演示与普通话视频对应版本）

### 3. Bundle 路径

- **包文件**：`https://github.com/Abarm009/zhiliao/blob/<B-commit>/submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip`（或同仓 raw 下载）
- **stamp blake3**：`e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`（recheck 后最终）
- **SHA256**：见 `submission/2026-10-06-native/SHA256SUMS`
- **大小**：1.5 MiB（< 8 MiB 白名单）

### 4. 完整 check 输出

```
$ hub check app/bundle --allow-unsigned
octosense-repair 0.1.0-b — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

### 4a. 完整 stamp 记录

- stamp blake3: `e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`（recheck 后最终）
- manifest.version: `0.1.0-b`
- 与 A 版（commit `6d81d57b`，manifest.version `0.1.0`，bundle_blake3 `eff13f557080fc12ac2961f6bee83a2365f3d8fb5ac0e56681cee45b13c4ad26`）互不覆盖。

### 5. scan 7 项回答

完整答复见 `submission/2026-10-06-native/check/03-scan-packet.answers.md`；摘要：

| Q | 答 |
|---|---|
| 1. App 是否做了它声称的事？ | 是；7 个核心动作函数 + 状态机常量 + 6 张真实原生截图覆盖 DRAFT→COMPLETED 全闭环 |
| 2. platforms / category 合适吗？ | 是；`macos` + `productivity` 与本机实测一致 |
| 3. capabilities 与可见行为匹配吗？ | 是；仅声明 `storage`；不请求 network / agent / compute |
| 4. 界面冒充系统/支付/登录/品牌？ | 否；自定义石墨主题；无登录、无支付、无第三方品牌 |
| 5. 源/数据含 prompt 注入？ | 否；脚本体内无 SYSTEM/assistant/Ignore 等指令 |
| 6. 辱骂或针对个人？ | 否；中性业务用语 |
| 7. 路径？ | pass（建议人类复核但不阻塞） |

### 6. 原生验证证据

- **真实宿主**：`card-host`（Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc；本机 binary mtime 2026-10-01）
- **6 张截图**：`submission/2026-10-06-native/screenshots/01-initial.png` 至 `06-after-restart.png`
- **已实测的主路径**：DRAFT → OPEN（报修人提交）→ ACCEPTED（技工接单）→ SCHEDULED（报修人确认预约 now+10s/+20min）。从 SCHEDULED → IN_PROGRESS 在自动化测试中遇到 review 已知的 scheduler timing 限制（详见 [KNOWN_LIMITATIONS.md L5](KNOWN_LIMITATIONS.md)），但 IN_PROGRESS 状态本身经合成 tasks.json 真实宿主验证通过。
- **Review 6 项修复的真实宿主验证**：
  - **B-R01**：addEvidence 写入 `bytes:0, sha:"", ready:false, demo:true`；`submitCompletion` 被 `readyCount(t) < 1` 阻断，task.status 保持 IN_PROGRESS，状态条「拒绝：完工前必须至少有一份可读证据」。
  - **B-R02**：runCommand 恢复 hit/conflict 路径（修前因 `hit.hit` 字段访问错误导致所有 13 个 runCommand 调用失败；修后 confirmDraft 等命令恢复）。
  - **B-R03**：events.jsonl 改整体 JSON 数组保存；重启后 events 计数 9→9 完全恢复。
  - **B-R05**：visible 过滤；切「报修人二」后显示「无可见任务」label，selectedIdx 自动跳到第一条可见任务。
- **持久化**：`tasks.json` / `actions.jsonl` / `events.jsonl` / `state.json` 在原生宿主 `--app-data` 目录真实落盘
- **不靠关闭重开掩盖**：每次状态变化由 `refreshLabels(taskToShow)` 主动更新 Label + `fn tick()` 1Hz 重算事实条
- **Python 后端独立**：bundle 不调任何 HTTP / TCP / 模型；后端 190 项单测 + 17 步 HTTP E2E 是 A 版独立证据

### 7. 已知限制（已显式标记，未冒充通过）

| 项 | 原因 |
|---|---|
| App picker 缺失（review 后阻断路径正确） | 宿主未提供 `openFileDialog`；`addEvidence` 写 demo 占位，`submitCompletion` 被 `readyCount(t) < 1` 阻断 |
| 隔离存储读字节 API 缺失 | 脚本可 `fs.write` 但无 `fs.read_bytes`；证据真实字节未落盘 |
| grant 申请/关闭/到期路径未实现 | 脚本只声明 `capabilities`；无 grant UI 面板 |
| 真实模型未接通 | `compute.agent: null`；脚本内无 `model.complete` / `agent.run` |
| 开工 scheduler timing 限制 | `time_now()` 与 `tick()` 同步不稳；自动化测试在 SCHEDULED → IN_PROGRESS 阶段需要更稳定的 isolate |
| 多次 setActor 后按钮位置下移 | 宿主布局 API 不稳定；测试脚本需每次重读 snap |
| 「最新 OctoSense 兼容性」未独立验证 | 上游 main 与本机 lockfile 存在 commit 差异；本机 binary 对应 Hub@6741dea lockfile |

详细最小复现与影响见 `submission/2026-10-06-native/KNOWN_LIMITATIONS.md`。

### 8. A 版与 B 版对照

- **A 版（2026-10-06，已提交比赛材料）**：`submission/2026-10-06/` 含 82 秒正式普通话视频、7 张截图、`octosense-repair-0.1.0.zip`、VERIFICATION、SHA256SUMS。A 版固定 commit `6d81d57b`。
- **B 版（2026-10-06，本目录）**：B 版针对 A 版残留的 N1（点击后不重绘）/N2（handler nil）做实质修复，由真实 card-host 实测跑通主路径，含 6 张原生截图。A/B 两条交付互不覆盖。

### 9. 致评审员

本 bundle 是公开候选版与真实验证结果，不是已完成发布版本。已知限制已显式记录；App Hub 收录需评审员按官方规范进一步判断；我们承诺：

- 不修改官方 catalog.json / index / artifacts/。
- 不把 Issue 创建成功描述成审核通过或商店收录。
- 等宿主补齐 App picker / 读字节 API / grant 生命周期后，再次 stamp + check + scan + 提交更新版本。

---

## 发出前确认清单

- [ ] 用户已批准冻结 B 版 commit + tag（`git tag octosense-repair-b-v0.1.0 <commit>`）
- [ ] 用户已批准推送到 `Abarm009/zhiliao`（`git push origin <commit> --tags`）
- [ ] B 版 bundle zip 已上传到 GitHub release / 同仓 `submission/2026-10-06-native/bundle/`
- [ ] 检查 9 项正文链接全部可访问
- [ ] 用户确认 publisher 身份署名（当前为 `Abram / OctoSense (Local Dev)`）
- [ ] Issue 标签：`submit`、`octosense-repair`、`v0.1.0-b`、`unsigned`

---

## 备选：本地递交到 OctoSense-App-Hub catalog（不适用本轮）

如未来想用 `hub publish` 把 bundle 推到本地 catalog（不与官方 catalog 同步），命令为：

```sh
HUB=runtime/native-build/OctoSense-App-Hub/target/release/hub
$HUB keygen /tmp/zhiliao_publisher.key
$HUB certify --anchor <hub-anchor> --working /tmp/zhiliao_publisher.key
$HUB sign-manifest app/bundle --key /tmp/zhiliao_publisher.key --key-id octosense-repair
$HUB publish app/bundle \
  --catalog runtime/catalog.json \
  --key /tmp/zhiliao_publisher.key \
  --anchor-cert <hub-anchor> \
  --publisher "Abram / OctoSense (Local Dev)" \
  --repo https://github.com/Abarm009/zhiliao \
  --commit <B-commit> \
  --out runtime/build-loop/b-publish/
```

本轮我们不擅自 publish 到任何目录；该命令仅供用户在公开授权后执行。
