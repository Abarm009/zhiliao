# B 版已知限制（KNOWN LIMITATIONS · 不冒充通过）

> 任务书要求：「平台限制无法解决时给出最小复现和明确影响」「未接通时准确标记，禁止用视频配音或 manifest 声明代替真实 AI 验证」。
>
> review 后的本版（B-R01 修复后）：addEvidence 写入 demo 占位、submitCompletion 被 readyCount<1 阻断——L1「demo 数据满足完工门槛」一项由「写入 ready:true 假装成功」改为「写入 demo:true + ready:false + 阻断完工」。
>
> 本文件列出 B 版 `octosense-repair 0.1.0-b` 仍存在的全部已知限制，每条都有最小复现和影响范围。

## L1 · App picker（文件选择器）缺失（review 后行为变更）

**review 前现象**：`addEvidence`（旧版 main.splash:574-583）写 `bytes:1024, sha:"demo-sha", ready:true`——证据门槛被伪占位满足，submitCompletion 放行，整个 DRAFT→COMPLETED 闭环被伪造。

**review 后修复（B-R01）**：
- `addEvidence` 现在写 `bytes:0, sha:"", ready:false, demo:true`，附 `note:"演示条目：宿主 picker / 隔离存储读字节 API 缺失，未真实落盘"`（`main.splash:574-594`）
- `readyCount(t)` 只数 `ready:true` 的 evidence，demo 占位不计入
- `submitCompletion` 检查 `readyCount(t) < 1`，**直接拒绝**并提示「完工前必须至少有一份可读证据；请先上传或解除隔离」

**最小复现**（B-R01 验证脚本 `/tmp/probe_b_v6.py`）：
1. 启动 card-host，加载本 bundle。
2. 用 `u-tech-1` 身份走到 IN_PROGRESS 状态（合成 tasks.json 或经调度时序）。
3. 点击「上传证据」。
4. 期望：弹出宿主文件选择器；实测：无 picker，evidence 写入 demo 占位（`bytes=0, ready=false, demo=true`）。
5. 期望 readyCount=0；实测 0 ✓
6. 点击「提交完工」。
7. 期望：状态条「拒绝：完工前必须至少有一份可读证据」；实测：task.status 保持 IN_PROGRESS ✓

**当前实现**：`addEvidence` 写入 demo 占位、`submitCompletion` 在证据门槛未达标时被阻断。**没有伪造完整闭环**。

**影响**：
- 在宿主补 picker 之前，演示流程在 IN_PROGRESS → submitCompletion 步骤自然停下，不会到 AWAITING_ACCEPTANCE / COMPLETED。
- 报修人 / 经理无法在原生界面看到真实附件。
- 公开候选展示范围 = DRAFT → OPEN → ACCEPTED → SCHEDULED → IN_PROGRESS → 记录处置 → （演示）上传证据 → submitCompletion 被阻断。

**修复路径**：等宿主补 `openFileDialog` / `pickFile` host API；脚本侧把 picker 返回路径喂给 `fs.write`，并将 evidence 写入 `ready:true, demo:false`。

---

## L2 · 隔离存储读字节 API 缺失

**现象**：脚本可调用 `fs.write`（实际未用）但不能直接 `fs.read_bytes(path)` 读取原始字节；只能通过 `fs.read` 配合 `parse_json` 反序列化 JSON 数据。

**最小复现**：
1. 期望：在 AWAITING_ACCEPTANCE 状态，点「查看证据」按钮读取 `evidence/{id}.bin` 字节并显示大小/缩略。
2. 实测：脚本内 `load()` 只反序列化 `state.json` / `tasks.json` / `actions.jsonl` / `events.jsonl`，未尝试读 `evidence/*.bin`。

**当前实现**：证据元数据存在 `tasks.json`，真实字节流**未落盘**。

**影响**：
- 证据只在前端可见名字 + ready 标记，不能在原生界面预览/下载。
- 报修人/经理不能校验证据内容是否被篡改。

**修复路径**：等宿主补 `fs.read_bytes(path) -> bytes` 与附件管理面。

---

## L3 · grant 申请/关闭/到期路径未实现

**现象**：manifest 声明 `capabilities: ["storage"]`，但脚本内没有 grant 申请、关闭、到期提示 UI；用户既看不到已获得的 grant，也不能在界面上撤销。

**最小复现**：
1. 启动宿主后切到任意任务。
2. 期望：右上角或底部有「Grant 设置」入口。
3. 实测：无入口。

**当前实现**：脚本只声明 `capabilities`，没有 UI 面板反映运行时 grant 状态。

**影响**：
- 用户无法看到 storage 已用多少、是否接近 16 MiB 上限。
- grant 申请/关闭/到期路径仅在 manifest 层静态声明，无脚本层运行时逻辑。

**修复路径**：等宿主补 `grant.list` / `grant.revoke` / `grant.expire_at` 等 API。

---

## L4 · 真实模型未接通

**现象**：脚本不调用任何模型；`compute.agent: null`；UI 上没有 AI 助手对话面板。

**最小复现**：
1. 期望：报修人点击「AI 帮我写报修描述」可调用本地 OctoScript Agent 模型生成草稿。
2. 实测：无按钮，无 agent provider 配置。

**当前实现**：`createDraft` 直接用硬编码模板 `problem: "东侧会议室空调不制冷，希望今天下午处理"`，不调用模型。

**影响**：
- 报修描述是固定模板，没有个性化。
- 后端 `record_advice` 等基于 LLM 的业务功能在原生侧无法触发。
- Hub Issue P03 等依赖 AI 助手的 PASS 项保持 NOT_RUN。

**修复路径**：等宿主补 `model.complete` / `agent.run` host API；脚本侧申请 agent capability 并实现 prompt 模板。

---

## L5 · 开工 scheduler timing 卡点（review 已知）

**现象**：固定版本 card-host 的 `time_now()` 在事件循环中更新频率与 `tick()` 不直接同步；从 SCHEDULED 状态「开工」时，脚本内 `nowMs() < appt.startMs` 检查在 click 后短时间内持续失败；review probe 指出「开工首次在测试等待后仍拒绝，稍后不重启重试成功」。

**最小复现**（probe_b_v5.py 实测）：
1. 走到 SCHEDULED 状态（appt.startMs = now+10000ms）。
2. wait 75s + retry click「开工」10 次，每次 1.5-2s 间隔。
3. 实测：task.status 仍为 SCHEDULED；STATE「拒绝：还没到预约开始时间」。

**当前实现**：`startProgress` 检查 `nowMs() < appt.startMs` 直接 fail。

**影响**：
- 自动化测试必须在更稳定的 isolate 下推进时间（如本目录 B-R01 验证采用合成 tasks.json 直接进入 IN_PROGRESS）。
- 真实用户用鼠标点击不受影响（人手点击间隔通常超过 scheduler 推进周期）。

**修复路径**：等宿主补 `time_now()` 与 tick 的稳定同步，或脚本侧用 wall-clock 与 nowMs 取大值。

---

## L6 · 多次 setActor 后按钮位置下移

**现象**：实测时，切身份（`setActor`）后，状态条与按钮组会重排，按钮 Y 坐标变化。固定版本 card-host 没有「点击后给元素快照」机制；脚本侧无法控制 widget 几何。

**最小复现**：
1. 启动宿主，初始 actor = `u-reporter-1`。
2. 点击「切换身份 → 技工甲」→ 状态条更新，按钮组重排。
3. 再点「切换身份 → 经理丙」→ 再次下移。

**当前实现**：脚本侧无法处理；测试侧只能每次 setActor 后重新读 snap，固定 click 坐标。

**影响**：
- 自动化测试脚本必须按身份切换次数重新读取 snap。
- 真实用户不会感受到（用鼠标点击而不是坐标）。

**修复路径**：等宿主补 widget 几何稳定 API，或脚本侧通过相对布局消除重排依赖。

---

## L7 · listing 引用截图含 A 版占位

**现象**：`app/bundle/listing.json` 引用 `screenshots/01-main.png` 与 `screenshots/02-after-draft.png`（A 版 2 张占位图）以及 `screenshots/b01..b06.png`（B 版 6 张原生截图）。

**当前实现**：保留 A 版 2 张作为对照，listing release_notes 明确说明本版核心是 B 版 6 张。

**影响**：
- 商店页展示按数组顺序，前 2 张是 Web 演示页面截图。
- bundle 大小 1.5 MiB（< 8 MiB 上限，离 6.5 MiB 仍有空间）。

**修复路径**：把 A 版 2 张从 listing 数组移出，或重命名为 `legacy-*.png`。

---

## L8 · 「最新 OctoSense 兼容性」未独立验证

**现象**：本机 `card-host` / `hub` 二进制 mtime 2026-10-01，HEAD 锁 Hub@6741dea / Shell@a5d847a；上游 OctoSense main 当前 head 与本机 lockfile 存在 commit 差异。

**最小复现**：读本机 Cargo.lock 与上游 `OctoSense-App-Hub` Cargo.lock 对比，commit 字段不一致。

**当前实现**：B 版只验证了本机固定版本宿主；上游 main 上的 card-host 二进制未本地编译与实测。

**影响**：
- 不能声称「最新 OctoSense 已验证」。
- 上游 main 演进到不兼容接口时，本 bundle 可能失效。

**修复路径**：在独立目录按上游 main lockfile 完整重编 card-host + hub，记录构建输出与二进制摘要，并重复本目录所有实测。

---

## 总览：哪些已修 / 哪些待修

| ID | 项 | 状态 | 来源 |
|---|---|---|---|
| **N1** | 点击后界面不重绘 | ✅ 已修 | main.splash refreshLabels + tick |
| **N2** | handler nil（pick/me 遮蔽） | ✅ 已修 | pickUser / getMe 重命名 |
| **B-R01** | 伪 READY 绕过真实附件门槛 | ✅ 已修 | addEvidence 写 demo 占位、submitCompletion 阻断 |
| **B-R02** | 幂等 hit/conflict 分支被删 | ✅ 代码已修，⚠️ UI 不可达 | runCommand 恢复 hit/conflict 路径，字段访问改字符串；UI 路径每个 click 用新 LAST_KEY，hit/conflict 分支不被触发 |
| **B-R03** | events.jsonl 重启解析失败 | ✅ 已修 | logEvent 末尾 saveEvents 整体重写，load parse_json 整体解析 |
| **B-R04** | 最新宿主兼容性未独立验证 | ⚠️ 文档已修正 | 不再声称「最新」；保留「固定旧宿主候选」口径 |
| **B-R05** | 身份切换显示不可见任务 | ✅ 已修 | visibleIndices / firstVisibleIdx / stepVisible + refreshLabels 检查 |
| **B-R06** | 文档版本号 / digest / 路径不一致 | ✅ 已修 | manifest.version=`0.1.0-b`；SOURCES A 版 digest=`eff13f55...`；README 复跑用绝对路径 |
| L1 | App picker | ❌ 未修（review 后阻断路径已正确） | 等宿主 API |
| L2 | 读字节 API | ❌ 未修 | 等宿主 API |
| L3 | grant 生命周期 | ❌ 未修 | 等宿主 API + 脚本面板 |
| L4 | 真实模型 | ❌ 未修 | 等宿主 agent API |
| L5 | 开工 scheduler | ❌ 未修（review 已知） | 等宿主时间 API |
| L6 | 按钮重排 | ❌ 未修 | 等宿主布局稳定 |
| L7 | listing 截图混合 | ⚠️ 业务可读，商店展示略弱 | 改 listing |
| L8 | 「最新」兼容 | ⚠️ 文档已诚实标注 | 重编 host binary |
