# 维修协作应用：编码交付包 v1.1

**当前编码入口：[15石墨构建循环](15_BUILD_VERIFY_LOOP.md)** · [启动提示词](../build-loop/START_PROMPT.md) · [验收台账](../build-loop/ACCEPTANCE.json)。用户已确定石墨；L0–L8覆盖创建、原生操作、事实回读、失败修复、封包与提交状态，优先于旧默认主题和旧分工顺序。

**9月29日执行入口：[14课程 #2 与最新制作发布说明](14_COURSE2_LATEST_GUIDE_REVIEW.md) → 13 Hub边界 → 12排期。** 当前Shell已合入隔离应用助手/model/glance；Design-Flow的旧AI状态不能覆盖新源码。仍须实际环境与业务G0验收；原六图的旧部署结构仅作历史记录，当前接入图见14第5节。

**9月27日接入依据（AI状态由14增量修订）：[13官方Hub提交规范与架构差异](13_APP_HUB_SUBMISSION_REVIEW.md)**。固定仓库已读取；脚本应用、权限、存储、原生验证及Issue提交机制以13为准，12继续决定期限。已克隆不代表环境已运行。

> **当前执行排期（用户确认）**：10月9日初赛截止；内部目标10月6日晚主要功能完成、10月7日验收、10月8日优先提交。日期与范围控制以[项目排期与差异清单](12_DELIVERY_PLAN_20261009.md)为准，旧赛程仅作历史证据。

> **研讨课 #1 后续修订（设计v1.2）**：先读[逐字稿与基线差异](11_COURSE1_BASELINE_REVIEW.md)。原robrix2为唯一P0宿主的前提已撤回，改以OctoSense原生持久应用为主选，App Card为意图视图；旧宿主/配对实现仍属条件设计。以下领域规则继续保留，宿主专属细节须G0复核。

日期：2026-09-26（原v1为9/22）。交付性质：**已完成设计文档、架构图和参考契约；业务功能尚待编码。**

历史与领域设计入口：[13官方Hub核对](13_APP_HUB_SUBMISSION_REVIEW.md) → [12项目期限、差异点与改进方向](12_DELIVERY_PLAN_20261009.md) → [11课程逐字稿对照](11_COURSE1_BASELINE_REVIEW.md)。下列为领域设计与历史修订阅读顺序：[07会议证据与顶层架构修订](07_REVISION_20260926.md) → [08旧代码复用/改造清单](08_REUSE_MIGRATION.md) → [09 Agent运行与独立核验](09_AGENT_HARNESS.md) → 00–06及机器契约。此修订保留用户全部P0功能、现有任务状态和命令；补强旧业务价值与Agent执行证据，不做无依据的全量Rust重写。

本次实现报单、接单、设备身份、官方桌面宿主内展示、预约、进度、完工与验收。外部工单系统只预留写入能力，默认显示未接入。长期通过适配器接入现有业务系统；比赛版先以本地维修任务为事实源。

## 阅读入口

界面设计与原生实现必须同时阅读[10 UI与交互规范](10_UI_UX_SPEC.md)：角色化工作台、任务卡、预约/证据交互、视觉参数、键盘与异常状态，以及12项独立UI验收。该文件是待实现规范，不是已完成高保真稿。

先打开 [六张架构图册](ARCHITECTURE.html)，再将本目录完整交给编程模型。新增第六张置于图册首位；原五张业务图继续使用。图册是离线HTML，内嵌SVG，不依赖外部CDN。可打印，也可直接编辑同名Mermaid源文件。

|文件|编码时解决的问题|
|---|---|
|[00 决策](00_DECISIONS.md)|冻结范围、角色、状态、事实归属与未实现边界|
|[01 需求](01_REQUIREMENTS.md)|10类需求、角色权限、正常旅程与异常业务规则|
|[02 架构](02_ARCHITECTURE.md)|模块路径、统一执行、状态机、事务、后台恢复、旧入口迁移|
|[03 技术栈](03_TECH_STACK.md)|Rust/Makepad原生宿主、Python/FastAPI/SQLite、Web回归与配对|
|[04 数据与API](04_DATA_API.md)|24个HTTP操作、14类任务命令、投影、鉴权、错误、外部输出|
|[05 实施与验收](05_IMPLEMENTATION_ACCEPTANCE.md)|可复制的接手提示、6个实施门槛、分工及原32项待执行用例；09再补6项，总计38项|
|[06 官方要求映射](06_OFFICIAL_COMPLIANCE.md)|官方直接来源、规则对应、版本门槛、未验证事项|
|[10 UI与交互规范](10_UI_UX_SPEC.md)|页面结构、三角色操作、视觉token、反馈与恢复、U01–U12验收|
|[OpenAPI 3.1](openapi.json)|机器可读请求、响应、枚举与安全声明；不是运行中的服务|
|[参考SQL](schema.sql)|新repair.db结构与约束；须转换为版本迁移，不覆盖旧库|
|[交付包检查](verify_pack.py)|离线检查链接、接口引用与关键SQL约束，不替代应用测试|

## 六张图的使用方式

|主题|可查看图|可编辑源|
|---|---|---|
|Agent运行、开发双环与证据|[agentic-loop.svg](diagrams/agentic-loop.svg)|[agentic-loop.mmd](diagrams/agentic-loop.mmd)|
|整体分层与职责|[system.svg](diagrams/system.svg)|[system.mmd](diagrams/system.mmd)|
|任务与预约流转|[workflow.svg](diagrams/workflow.svg)|[workflow.mmd](diagrams/workflow.mmd)|
|并发接单、确认预约与失败回读|[execution.svg](diagrams/execution.svg)|[execution.mmd](diagrams/execution.mmd)|
|宿主、后端、存储与信任边界|[deployment.svg](diagrams/deployment.svg)|[deployment.mmd](diagrams/deployment.mmd)|
|核心实体与数据约束|[data.svg](diagrams/data.svg)|[data.mmd](diagrams/data.mmd)|

图是架构说明，详细守卫以需求和命令文档为准；SVG是手工排版版本，编辑Mermaid后须同步SVG与HTML，不会自动重新渲染。

## 如何修改与交接

1. 业务范围调整先改00/01；新规则同步02状态与事务、04/OpenAPI/SQL及05验收用例。
2. 官方发布版本变化先改06和G0记录，再更新03及宿主适配；自有API不可标成官方API。
3. 每次修改图同步三份：Mermaid源码、独立SVG、HTML内嵌图。检查通过后在项目[验证记录](../VERIFICATION.md)记下实际结果。
4. 发现文档与机器契约矛盾时先修正并统一版本，不能由不同编程模型各选一套。业务语义以00/01为依据；04/OpenAPI明确线协议；SQL只覆盖其中的存储约束。
5. 当前[迁移说明](../MIGRATION.md)和79文件快照仍是源码来源证据；本包不代表原后端已按新架构改造。

```sh
python3 docs/implementation/verify_pack.py
python3 scripts/verify_migration.py
```

先做G0原生宿主最小读写切片，同时可实现G1/G2本地业务。G0失败必须记录具体阻碍，不能把浏览器页面成功写成比赛原生交付通过。真实模型、原生宿主与业务闭环分别验收。

设计边界置信度高；原生桥接可行性置信度中，需实际构建验证；最终发布包能力与比赛最终评审结果未知。
