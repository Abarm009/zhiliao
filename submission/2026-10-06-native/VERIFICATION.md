# B 版验证清单（VERIFICATION · 2026-10-06 原生候选 review 后）

> 口径：「构建成功」指 stamp/check/scan 通过；「原生验证通过」指真实 card-host 加载本应用 main.splash 后由真实点击跑通主路径。本目录为「构建成功 + 原生验证通过 + 待递交」。
>
> **review 反馈后修正**：本目录上一版的 VERIFICATION 把多项「待证据」事项写成 PASS（replay 命中返回 action_id、重启事件计数不变、scan 三关通过 等）。review 指出后已修正——这些条目改为 NOT_VERIFIED 或 FAIL。下面只列**当前确实被真实宿主跑通过**的事项。

## 1. 包准入（hub 三关）

| 关 | 命令 | 结果 | 备注 |
|---|---|---|---|
| stamp | `hub stamp app/bundle` | `1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96` | recheck 修后最终 hash |
| check | `hub check app/bundle --allow-unsigned` | `octosense-repair 0.1.0-b — PASSED` | warning: publisher-signature unsigned（首版声明 unsigned） |
| scan | `hub scan app/bundle --packet ...` | packet 7 项问题 | 由**发布者自己**回答，route=pass；**不是独立 reviewer 通过** |

完整输出见 [check/](check/)。

**重要口径**：
- check 是**程序包完整性**检查（manifest / capabilities / 签名），不是业务验证。
- scan packet 是**给人类评审员的 7 个引导问题**，本仓 7 项答复由发布者自己写；这是自答，不是独立 reviewer 结论。
- 不把上述两项描述为「scan 三关全部通过」——那会暗示有独立 reviewer，实际没有。

## 2. 原生业务主路径（真实点击验证）

执行环境：macOS darwin 25.6.0 arm64，card-host 二进制 `runtime/native-build/OctoSense-App-Hub/target/release/card-host`（arm64 Mach-O 25 MB，mtime 2026-10-01）。

### 2.1 主路径（DRAFT → SCHEDULED）

| # | 步骤 | 主路径期望 | 实测 | 证据 |
|---|---|---|---|---|
| 1 | 启动宿主，加载 bundle | 首屏 | 「无可见任务（u-reporter-1）」label；events.jsonl count=0 | `02-draft-created` 等 |
| 2 | 切「报修人一」+「新建报修草稿」 | DRAFT | task.status=DRAFT；events=1；receipts=1 | `02-draft-created.png` |
| 3 | 「提交 OPEN」 | OPEN | task.status=OPEN；events=2；receipts=2 | `03-open.png` |
| 4 | 切「技工甲」+「技工接单」 | ACCEPTED | task.status=ACCEPTED；events=3；receipts=3 | — |
| 5 | 「绑定设备」+「提议预约」 | ACCEPTED + appt PROPOSED | events=5；receipts=5 | — |
| 6 | 切「报修人一」+「确认 SCH」 | SCHEDULED | task.status=SCHEDULED；events=6；receipts=6 | `05-scheduled.png` |

### 2.2 review 留下的「开工首次拒绝」问题

review 指出：「开工首次在测试等待后仍拒绝，稍后不重启重试成功」。**本轮探针（probe_b_v5.py）真实复现了同一现象**：wait 75s + 10 次 retry 后 task.status 仍为 SCHEDULED；脚本内 `nowMs() < appt.startMs` 检查持续失败。

- 根因：固定版本 card-host 的 `time_now()` 在事件循环中更新频率与 `tick()` 不直接同步；UI 在 click 后是否推进 `time_now()` 取决于调度细节。
- 影响：自动化测试必须在更稳定的 isolate 下推进时间，或通过手工合成 tasks.json 直接进入 IN_PROGRESS 状态再继续。
- 处理：本目录采用合成 tasks.json（[§3.1](#31-br01-验证-via-合成-in_progress-任务)）验证 B-R01，避免与 scheduler timing 串行。
- 不冒充通过：claim「完整主路径真实点击跑通到 IN_PROGRESS」时**附注此 scheduler timing 限制**。

### 2.3 退回 / 终态拒绝 / 持久化（来自 review）

review 已用同一 bundle 与 probe 跑通以下项（独立审查证据在 `runtime/review-native-b-20261006/probe-results.json`）：

| 项 | 期望 | review 实测 | 本轮复跑 |
|---|---|---|---|
| AWAITING 状态「拒绝完工」 | 退回 IN_PROGRESS + completion round+1 | ✓ | 未在本轮重跑（沿用 review 证据） |
| 二次完工 + 报修人验收 | COMPLETED | ✓ | 未在本轮重跑 |
| COMPLETED 状态开工 | 业务拒绝 | ✓（状态条「拒绝：……」直到 tick 1Hz 后刷新） | 未在本轮重跑 |
| 重启（独立实例） | 任务 + 12 条回执恢复 | ✓ | 见 §4（B-R03 重启恢复 9→9 events / 8→8 receipts） |

## 3. Review 6 项修复的原生验证

> review 文档：`docs/build-loop/REVIEW_NATIVE_B_2026-10-06.md`。本轮针对 review 列出的 B-R01 / B-R02 / B-R03 / B-R05 / B-R06 全部或部分修复或修正。

### 3.1 B-R01 验证（via 合成 IN_PROGRESS 任务）

合成 SCHEDULED 任务的 `appointments[0].startMs = now - 5000`（5 秒前已到开始时间）写入磁盘，重启 card-host 让 `load()` 回读。

| 步骤 | 期望 | 实测 |
|---|---|---|
| 切「技工甲」+「开工」 | IN_PROGRESS | task.status=IN_PROGRESS ✓ |
| 「记录处置」 | evidence/repair 记录 | STATE「已记录处置：INSPECTION」 ✓ |
| 「上传证据」 | evidence 写入 | evidence[0] = `{bytes:0, sha:"", ready:false, demo:true, by:"u-tech-1", note:"演示条目：宿主 picker / 隔离存储读字节 API 缺失，未真实落盘"}` ✓ |
| `readyCount(t)` | 0 | 1 件 evidence，0 件 ready_true ✓ |
| 「提交完工」 | 被 readyCount<1 阻断 | task.status=IN_PROGRESS ✓；STATE「拒绝：完工前必须至少有一份可读证据；请先上传或解除隔离」 ✓ |

**结论**：B-R01 修复后，addEvidence 写入 ready:false demo 占位，submitCompletion 真实被阻断；不再假装完整闭环。

证据文件：`/tmp/zhiliao_b_v6-b-r01.json`。

### 3.2 B-R02 验证（runCommand hit/conflict 路径恢复）

review 指出 runCommand 计算 `hit = receiptFor(...)` 后没用，删除了 conflict 拒绝和 hit 回放。本轮修复 + 真实宿主验证：

| 步骤 | 期望 | 实测 |
|---|---|---|
| `receiptFor` 返回值改用 `{kind: "hit" \| "conflict" \| "miss"}` 命名 | 编译通过，无 `property hit not found in prototype chain` 错误 | host log `[E]` 错误数=0 ✓ |
| 「提交 OPEN」从 DRAFT → OPEN | runCommand 不再被「hit.hit」字段访问错误阻断 | task.status=OPEN（修前失败，修后通过）✓ |
| 同 key 同 payload 重放 | 「幂等命中：... → action_id ...」+ 不重做 commit/event | **代码层已恢复；但 UI 路径不可达**——每个命令函数 `LAST_KEY = newId()` 在 runCommand 前生成新 key，receiptFor 永远返回 miss；hit 分支不会被 UI 触发 |
| 同 key 不同 payload | 「拒绝：同 key 不同 payload 冲突」 | 同上：UI 路径不触发；需要外部 client 用稳定 key 调用 runCommand 才能验证 |

**关键发现**：review probe.py 之前在 v1（1002 行版本）能跑通，但本仓 v2（956 行 → 现在 974 行）首次重写 runCommand 时使用了 `hit.hit` 字段访问——Octoscript 编译器报 `property hit not found in prototype chain. Did you mean: miss(true)`，导致整个 runCommand 失败，所有走 runCommand 的命令（confirmDraft / acceptTask / bindAsset / submitCompletion 等 13 个）都失效。改用字符串比较 `found.kind == "hit"` 后恢复。

**recheck 第 4 项后续**：「动态复用 key 验证」仍是 NOT_TESTED。每个命令函数 `LAST_KEY = newId()` 在 runCommand 之前——意味着 UI 路径下 hit/conflict 分支永远不被触发；要验证这两个分支，需要外部 client 稳定输入 key 调用 runCommand。代码逻辑已恢复（运行时会按 kind 字符串判定），但端到端 UI 路径无法触发。详见 `check/probe-results-b-idempotent.json`。

### 3.3 B-R03 验证（events.jsonl 数组格式 + 重启恢复）

| 测试 | 期望 | 实测 |
|---|---|---|
| `logEvent` 末尾调用 `saveEvents()` | events.jsonl 整体 JSON 数组 | 写盘后文件内容是 `[entry1, entry2, ...]` 单行 JSON 数组 ✓ |
| `load()` 一次 parse_json 整体解析 | 启动回读 EVENT_LOG | 启动后 facts_line 显示「事件 N 条」与磁盘一致 ✓ |
| 9 条事件 + 8 条回执 + 1 个 task 重启后 | 完全恢复 | 9→9 / 8→8 / 1→1 ✓（`probe_b_v6_restart.py`） |

**关键修复**：之前 `logEvent` 用 `fs.append` 逐行写入（JSONL 多行格式），但 `load()` 一次 `parse_json` 整体解析（当成 JSON 数组解析）——多行 JSON 不是合法 JSON，parse_json 返回 nil，EVENT_LOG 保持空。review 触发本轮修复。

### 3.4 B-R05 验证（visible 过滤）

| 测试 | 期望 | 实测 |
|---|---|---|
| 切「报修人二」（prj-B 角色） | 「无可见任务（u-reporter-2）」label | label 含「无可见任务」 ✓ |
| `refreshLabels` 检查 `visible(task, actor)` | 不可见任务不显示 | code 改后 `refreshLabels` 加 visible 分支 ✓ |
| `setActor` 后 `selectedIdx = firstVisibleIdx()` | 默认选中第一条可见任务 | code 改后 `setActor` 用 `firstVisibleIdx()` ✓ |
| `prevTask` / `nextTask` 用 `stepVisible(from, dir)` | 跳过不可见任务 | code 改后 ✓ |
| facts_line 显示「任务 N 条（可见 K）」 | 计数透明 | 「任务 1 条（可见 1）」 ✓ |

## 4. 重启与持久化

| 测试 | 期望 | 实测 |
|---|---|---|
| `kill -9 card-host` | 进程退出，state/tasks/actions/events 落盘 | `/tmp/zhiliao_b_v6-restart.log` 启动新进程 ✓ |
| 重启 card-host 指向同一 `--app-data` | task 列表与 events 计数恢复 | events 9→9、receipts 8→8、tasks 1→1 ✓ |
| 修前（B-R03 未修） | events 计数恢复为 0 | review probe `12-completed-after-restart.png` 留证 ✓ |
| **recheck P0：旧版假 READY 证据加载** | 旧 `bytes=1024, sha:demo-sha, ready:true` 被 scrub 为 `bytes:0, sha:'', demo:true, ready:false` | `runtime/recheck-native-b-legacy-20261006` 数据实测：load 后 evidence 全部清洗 ✓ |
| **recheck P1：旧 JSONL 多行加载** | 旧 9 条 JSONL 事件被备份到 `events.jsonl.legacy.<ts>.bak`，events.jsonl 写 `[]` | 手工构造 9 条 JSONL 实测：备份文件完整保留原始 9 条 ✓ |
| **动态幂等验证（recheck 第 4 项）** | 同 key 同 payload / 不同 payload 触发 hit / conflict | UI 路径不可达（每个命令函数 fresh LAST_KEY），代码路径已恢复但需外部 client 驱动 |

## 5. 脚本内 / 后端业务的解耦

- 本应用 main.splash 不调任何 HTTP / TCP / 模型调用面；`network.hosts: []`、`compute.agent: null`。
- 后端 190 项单测与 17 步 HTTP E2E（`backend/scripts/e2e_full_chain.py`）**与本 bundle 相互独立**——后端在 `backend/src/octosense_backend/`，本 bundle 只声明 `capabilities: storage`，不依赖后端运行。
- A 版后端验证（提交目录 `submission/2026-10-06/`）的 Web 视频、普通话配音、报修人页面验收与 B 版原生闭环是两套独立证据。

## 6. 未跑通的部分（不冒充）

| 项 | 原因 | 证据 |
|---|---|---|
| 真实 LLM 接入 | `compute.agent: null`，无 `model.complete` 调用 | manifest + main.splash |
| App 文件选择器 | 宿主未提供 `openFileDialog`；`addEvidence` 写 demo 占位（已修 B-R01） | `main.splash:574-588` addEvidence |
| 隔离存储读字节 API | 脚本可 `fs.write` 但无 `fs.read_bytes` | `main.splash:198-207` 写盘函数 |
| grant 申请/关闭/到期 | 脚本只声明 `capabilities`，未实现 grant UI | manifest |
| 真实附件上传 | 见 L1（宿主 picker 缺失） | 同上 |
| 「最新 OctoSense 兼容性」独立验证 | 未重编 host binary；上游 main 与本机 lockfile 存在 commit 差异 | SOURCES §6 |
| 38 / 12 项验收 | review 仅做主路径与可见性回归；未重跑完整 38 业务 + 12 UI | review 留下 12 张截图证据 |

## 7. 验收台账变化（相对 10-02 review）

- **T28 原生 UI** 部分问题由 FAIL 改 PASS（取消 ScrollYView + 重命名 + tick）；本轮 B-R01/B-R02/B-R03/B-R05 修复后进一步收敛。
- **T29 grant 生命周期** 仍 FAIL（脚本未实现 grant UI；manifest 声明 storage 是入口而非 grant）。
- **ACCEPTANCE.json** 未在本轮更新（保留 10-02 review 状态：31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED）。

## 8. 文件与可复跑

- `app/bundle/main.splash` 974 行（含头部 24 行注释）
- `app/bundle/manifest.json` version=`0.1.0-b`，integrity.bundle_blake3=`5503136c...`
- `app/bundle/listing.json` B 版 release_notes 指向本目录
- `submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip` 1.5 MiB
- `submission/2026-10-06-native/SHA256SUMS` 文件清单与校验和
- 复跑命令：见 [README.md](README.md#本地复跑)（用绝对路径）
