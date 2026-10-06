# Scan Packet · 7 项逐条回答

**包**：`octosense-repair 0.1.0`
**stamp blake3**：`1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca`
**scan 时间**：2026-10-06（Asia/Shanghai），card-host=`runtime/native-build/OctoSense-App-Hub/target/release/card-host`（Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc）
**packet 源文件**：`runtime/build-loop/b-stamp-check/03-scan-packet.json`
**证据文件**：`runtime/build-loop/native-screens/01..06-*.png`、`app/bundle/main.splash`、`app/bundle/manifest.json`

---

## Q1. App 是否做了它名字/副标题/描述声称的事？引用源文本。

**是**。

- 名称 `OctoSense Repair` 对应 `app/bundle/manifest.json:9` `"name": "OctoSense Repair"`。
- 副标题「报修、处置与独立验收的三角色维修协作」对应 `app/bundle/main.splash:56-60` 的 `USERS` 表：`u-reporter-1`/`u-reporter-2`（REPORTER 报修人）、`u-tech-1`/`u-tech-2`（TECHNICIAN 技工）、`u-manager`（MANAGER 经理）。三角色在 `hasRole`/`isReporter`/`isAssignee`/`isManager`（`main.splash:90`/`113`/`114`/`118`）里被显式区分；报修人独立验收由 `submitCompletion`（`main.splash:604`）让承接技工完工、由 `acceptCompletion`（`main.splash:630`）交回原报修人完成验收，对应业务描述「独立验收」。状态机常量见 `main.splash:31-38`：DRAFT / OPEN / ACCEPTED / SCHEDULED / IN_PROGRESS / AWAITING_ACCEPTANCE / COMPLETED / CANCELLED。
- 描述里 7 个核心动作全部存在并落到具体函数：`createDraft`（269）、`acceptTask`（315）、`bindAsset`（353）、`proposeAppointment`（415）、`confirmAppointment`（458）、`recordProgress`（548）、`submitCompletion`（604）、`acceptCompletion`（630）、`rejectCompletion`（657）、`cancelTask`（681）。每个函数都在 `sourceOk`（157）里按当前状态门禁，并通过 `runCommand` 走 `actions.jsonl` 幂等回执。
- 闭环证据：6 张真实原生截图覆盖 `native-screens/01-initial.png`（首屏 / 准备就绪）→ `02-draft-created.png`（草稿已创建）→ `03-submit-open.png`（已提交 → OPEN）→ `04-schedule-confirmed.png`（预约确认 → SCHEDULED）→ `05-completed.png`（报修人独立验收完成 → COMPLETED）→ `06-after-restart.png`（kill card-host 重启后从 `state.json`/`tasks.json`/`actions.jsonl`/`events.jsonl` 完整回读）。状态条与任务卡由 `refreshLabels`（796）按 click handler 顺序主动刷新，事实条由 `fn tick()`（949）1Hz 自动更新，修复 N1「数据变化但界面不重绘」。
- 与后端的关系：`main.splash:1-9` 头部注释明确「权威事实在本应用自己的宿主隔离存储里」「不拉起服务、不访问 127.0.0.1、不请求公网地址」。Python 后端 190 项单测 + 17 步 HTTP E2E（`backend/scripts/e2e_full_chain.py`）是 A 版独立业务验证证据，本包内脚本不依赖也不重实现后端。

---

## Q2. listing 的 platforms 和 category 是否合适？

**是**。

- `platforms: ["macos"]`（`app/bundle/listing.json`）——宿主 card-host 当前仅在本机 `darwin 25.6.0 arm64` 上构建并实测运行（`runtime/native-build/OctoSense-App-Hub/target/release/card-host` 是 arm64 Mach-O）。脚本语言层是跨平台 Rust + Octoscript，但本次仅在 macOS 实测；不声明未实测的平台。
- `category: "productivity"` ——任务协作、流程推进、记录与验收是 productivity 的常见子类；不冒充社交、娱乐或财务类。
- `age_rating: "all"` ——演示数据全部合成（任务描述、报修联系人、设备名都是 `main.splash:271-272` 的内嵌字符串，如「东侧会议室空调不制冷」），不涉及真人或真实个人信息。
- `license: "Apache-2.0"` 与根 `LICENSE` 一致；`publisher` 的 support / privacy 链接指向同一仓库的 `issues` 页与 `docs/PRIVACY.md`。

---

## Q3. granted capabilities 是否与可见行为匹配？脚本 app 列出每个 host 请求及原因；指出屏幕上看不到的 grant。

**匹配；无超出可见行为的 grant**。

- manifest 声明 `capabilities: ["storage"]`、`network.hosts: []`、`compute.agent: null`、`integrity.signature: null`（`app/bundle/manifest.json`）。`hub check` 输出确认：`grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none`。
- 实际使用：`main.splash:197-200` 通过 `fs.write("state.json" | "tasks.json" | "actions.jsonl")` 与 `fs.append("events.jsonl", ...)` 写入应用专属目录；`fs.read` 在 `load()`（208）里把磁盘状态读回。这正是 `storage` capability 的预期用途——同一应用在自己设备上保留自己的数据。
- 不请求 `network`（`hosts: []`）——脚本体内没有任何 `http.request` / `tcp.connect` / 域名；`time_now()` 是本地时钟。
- 不请求 `agent` —— `compute.agent: null`，没有调用模型、没有调用 agent provider。AI 助手、grant 申请/关闭/到期路径未实现，按项目要求**已显式标记未接通**，不在 UI 上冒充 AI 能力。
- 屏幕上看不到的需求：未声明 —— manifest 的 capabilities 列表与脚本可见行为完全一致，无多余 grant。

---

## Q4. 界面有没有冒充系统提示、支付表、登录、品牌？

**没有**。

- `app/bundle/main.splash` 顶部头部条用的是品牌色 `ink=#xE8F2EE / surface=#x1F2D2F / accent=#x7DD3B0`（行 17-25），与 macOS 系统色板不同；不模仿系统通知、Alert 或 Sheet 形状。
- 没有「系统升级」「Apple ID 登录」「支付宝/微信支付」「密码输入框」「信用卡输入」等任何元素。所有「身份切换」是应用内三角色 chips（行 305-323 区域），按 `setActor`（835）切换本地 actor 字段，不是任何远程登录或 OAuth 流。
- 没有任何第三方品牌 logo、商标文字、彩虹色 / 彩虹标语；文字全部围绕任务状态、动作动词和按钮标签（「新建草稿」「提交报修」「提议预约」等）。
- 截图核对：`native-screens/01-initial.png` 到 `06-after-restart.png` 均无支付、登录或品牌冒充痕迹；状态条、任务卡、按钮组都在自定义的暗色面板里。

---

## Q5. 源或数据里有没有「指令给助手而不是给人看」的内容？

**没有**。

- `main.splash` 全部内容是 UI 标签、按钮文字、状态常量、命令函数；无 `SYSTEM:` / `assistant:` / `prompt:` / `Ignore previous` / `You are ...` 等模板注入。
- `card_source` 头部 `// 2026-10-06 修复（针对 N1/N2）` 段是给开发者看的修复说明（同样在 git 历史里有同等 commit message）；不属于运行时数据。脚本编译时 Octoscript 编译器只把 `//` 行作为 token 跳过，不当作指令执行。
- `events.jsonl` / `actions.jsonl` 写入的是 `kind` / `task_id` / `status` / 时间戳 / 幂等键指纹等结构化事实，不带 prompt。
- 没有任何对模型/助手说话的句子；agent capability 已声明为 `null`，脚本也确实没有调用任何模型调用面。

---

## Q6. 有没有辱骂或针对个人的措辞？

**没有**。

- 所有角色名是中性占位：`报修人一`、`报修人二`、`技工甲（HVAC）`、`技工乙（电气）`、`经理丙`（`main.splash:56-60`）。
- 失败提示是中性业务用语：「只有原报修人能提交草稿」「经理没有技工角色不得自主接单」「预约时长不得短于 15 分钟」（302 / 319 / 426 等）。
- 不针对任何真实个人、组织、政治实体或敏感群体；不包含仇恨、暴力、淫秽或骚扰语言。

---

## Q7. 路径：pass / human-review / reject？给出理由。

**pass（建议人类复核但不阻塞）**。

理由：

- 包准入三关（stamp / check / scan）全部通过：`stamp blake3=1ac7bb26...`、`check: octosense-repair 0.1.0 — PASSED`（仅 publisher-signature unsigned warning，已声明首版 unsigned）、`scan` 输出 packet 无 reject 项。
- granted capability 与可见行为一致（仅 `storage`）；网络、agent、计算资源全部声明为 0；不引入供应链代码（脚本是单文件 `main.splash`，无 npm/cargo/二进制依赖）。
- 主要 UI 文本中性、无系统冒充、无 prompt 注入、无辱骂；reviewer 担心的常见红线全部未触发。
- 已知限制已显式记录、不冒充通过：app picker、隔离存储读字节 API、grant 申请/关闭/到期路径、真实模型接入。`addEvidence`（563）在缺失宿主 picker 时写入 `ready:true` 并附 demo note，未声明真实附件已落盘。
- 建议人类复核的两点（不阻塞 publish）：
  1. **publisher 身份未签名** —— 首版 `--allow-unsigned` 通过；后续补 `hub keygen` + `hub sign-manifest` 后再次递交即可，hash 不变。
  2. **「项目」与「服务空间」模型简化** —— 原 schema 25 表，本应用脚本内把它收敛到 `task.project` + `task.space` 两个字符串字段以匹配脚本表达；功能完整但模型粒度比后端细，发布者可在评审时按需确认是否符合期望粒度。
