# 迁移核验记录


## 2026-10-02 · 全盘 Review（只读检查 + 真机启动检查）

对当前候选版本做了一次完整 review：静态通读 `octosense_backend` 7 个模块、`app/bundle/main.splash`、`app/demo-web` 5 个文件；实跑单测/端到端/三个 check 脚本；真实启动 8821 后端、8822 demo-web、8823 card-host；用浏览器完成三角色真实点击；30+ 个定向 curl 探针。**未修改任何业务代码。**

| 实际执行 | 结果 |
|---|---|
| `pytest backend/tests/octosense_backend/ -q` | **39 passed**（11 核心 + 4 预约改派 + 23 扩展 + 1 dummy） |
| `bash backend/scripts/e2e_full_chain.sh`（13 步，独立端口 + 独立 DB） | **PASS**：status=COMPLETED, version=13, events=13, evidence=2, appointments=[CONFIRMED] |
| demo-web 代理跑同一条 13 步链 | **PASS**：同上，说明 HTTP 层与代理层无额外问题 |
| `python3 scripts/verify_migration.py` | 通过，仅 `backend/tests/conftest.py` 一处故意修改 |
| `python3 docs/implementation/verify_pack.py` | 通过：36 必需文件 / 158 本地链接 / 6 SVG / 24 操作 / 14 命令 / 43 schema / 84 引用 / 25 表 + 10 约束场景 |
| `python3 scripts/check_build_loop.py` | VALID RECORD STRUCTURE: 64 checks; **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED** |
| `python3 scripts/check_build_loop.py --ready` | **NOT READY**，35 项本地未过 |
| `backend/.venv/bin/python scripts/test_baseline.py` | **失败（收集期即崩）**：`test_ops_agent.py`(34) + `test_ops_api.py`(15) 的 `from conftest import stream_of` ImportError；另 220 项中 `test_mcp.py::test_stdio_server_list_and_call` 失败。现状 219 pass / 1 fail / 49 无法收集，9/21 记录的"234 passed"不可复现 |
| `hub check app/bundle --allow-unsigned` | `octosense-repair 0.1.0 — PASSED`，仅 publisher-signature unsigned warning |
| card-host 启动 + `/d` `/snap` `/click` `/g` | admitted；**splash 声明 23 节点，运行时只实例化 15 个**（末节点为"验收"按钮） |
| card-host kill + 同 app-data restart | `state.json` 恢复 actor/status；**TASKS 全部丢失**，重启后点"接单"为 silent no-op，再点"新建草稿"产生第二个 `tsk-0` |
| ego-browser 三角色真实点击 | 登录页 5 角色卡正常；报修人建档/确认/绑定、技工接单/提议预约均可用；**报修人在 SCHEDULED 无"确认预约"入口**，web 路径在 SCHEDULED 死锁 |

### 改判（9 项 PASS → FAIL / NOT_RUN）

| ID | 原 | 新 | 依据 |
|---|---|---|---|
| T01 | PASS | NOT_RUN | 未接真实模型；草稿由 HTTP body 直建，无模型抽取步骤 |
| T02 | PASS | FAIL | 同 key 不同内容返回 201 而非 409；幂等冲突为死代码 |
| T03 | PASS | FAIL | 跨项目可写；`space_id` 完全不校验 |
| T05 | PASS | FAIL | 跨项目角色可接单；无技能匹配 |
| T08 | PASS | FAIL | 无 `asset_serves`/服务关系数据模型 |
| T16 | PASS | FAIL | replay 不返回 `action_id` |
| T17 | PASS | FAIL | 无 SSE 端点 |
| T18 | PASS | FAIL | `GET /tasks/{id}` 无授权校验 |
| T29 | PASS | FAIL | 无 grant 机制 |

台账现为 **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**。3 项 BLOCKED 是 **P06/P07/P08（外部递交，需用户授权）**——此前 README / PROGRESS / SUBMISSION 写成"jobs/LLM"，与台账不符，已一并在本次修正。

### 主要问题（编号与修改建议见 [REVIEW_2026-10-02.md](build-loop/REVIEW_2026-10-02.md)）

- **P0**：原生 UI 只实例化一半节点（退回/重置/任务列表/状态行不存在）；core 命令跨项目可写；`GET /tasks/{id}` 无授权；同 key 不同内容不 409；**demo-web 无法确认预约、web 路径在 SCHEDULED 死锁**；无任何 grant 机制
- **P1**：原生任务不落盘（重启丢任务 + id 重复）；技工乙登录即 403；`record_advice` 重复 key 返 500；`/task/{id}` 500；6 处幂等键用 `Date.now()`；`currentVer()` 猜版本；证据根目录跟 CWD 绑定；原生 UI 零权限 + 无声失败
- **P2**：schema 25 表 vs 实现 12 表、openapi 23 路径与实现零重叠；测试数 37/39、命令数 25/27、表数 11/12、BLOCKED 归属三处矛盾；17 项 PASS 引用同一个只有 1 条任务的旧 DB 作证据、8 项 PASS 共用同一组 4 个证据文件；`runtime/` 被 gitignore 且本工程非 git 仓库；随包截图是 L0 三按钮版而 main.splash 已是 15 按钮版；`commands/__init__.py` mtime 20:38 晚于最后一条 verified_at 18:10 且无 iteration 记录

### 本次 review 的副作用（已清理）

- 跑 pytest 在 `backend/tests/__pycache__/` 生成 .pyc（已被 .gitignore 覆盖）
- 一次 live 证据上传落到 `runtime/evidence/<task_id>/…bin`（默认根目录为 CWD 相关，见 R-P1-7），已删除该测试产物
- `app/bundle/manifest.json` 被 card-host `--stamp` 重写（mtime 变化，digest 仍为 `c066a517…`，`hub check` 仍 PASSED）

**检查器只验证记录字段、文件和候选版本一致性，不检验日志事实或应用行为。本节的执行与结论可依 [REVIEW_2026-10-02.md](build-loop/REVIEW_2026-10-02.md) §5 的命令独立复跑。**

## 2026-10-01 · L0 真实原生 UI + L1 任务内核 + L7 hub check

本轮轮在本工程内真实完成：

- **环境**：`fastly CDN` 限速 2.7 KB/s 改走 USTC 镜像 1.68 MB/s；`rustup + stable toolchain 1.98.1` 通过 USTC 装好；4 个 native checkout 通过 `codeload.github.com` tarball 解压就位（`makepad / octoscript-makepad / octoscript / OctoSense-App-Hub / OctoSense-Shell`）。
- **构建**：`cargo build --release -p octosense-app-hub -p octosense-card-host` 用时 1m 11s，产出 `card-host` (25 MB) + `hub` (1.9 MB) Mach-O arm64。
- **L0-A 真实验证**：业务化最小 `main.splash`（石墨主题 + 3 个 ButtonFlat + fs 持久化）+ `card-host` admit → `/click` 触发 → fs 写入 83 字节 → 重启回读真实截图（824x1696 RGBA）。3 张截图：`runtime/build-loop/l0-shots/L0-A-{1,2,3}-*.png`。
- **L1 任务内核**：8 状态机 / 14 命令（11 命令已实现）/ 8 张表（精简）/ FastAPI HTTP API / 14 项 pytest 全 PASS / curl 7 步端到端 PASS。
- **L7 hub check + scan**：`octosense-repair 0.1.0 — PASSED`，warning 仅 publisher-signature unsigned；review packet 写入 `app/build/review.json`。

### 已知基线变更（按 MIGRATION.md "有意改基线文件需记录兼容与真实差异"原则）

- `backend/tests/conftest.py`（原 2730 字节 / sha256 61b8940cab270337557cdaba1e1c4fdbe220a3fc95655f1f2716ea91c19c143c）已改为 614 字节的占位文件。原仓库不可访问以重建精确字节；octosense_backend 测试 fixture 全部移入 `backend/tests/octosense_backend/conftest.py`。verify_migration.py 仍能正确识别此差异。

### 未完成（NOT_RUN / BLOCKED）

- G0-B / G0-D / G0-E / G0-F：依赖 Shell 编译 + host services + AI provider；本轮未做。
- T07-T09 设备身份业务子集、T13-T14 时区 / 过期校验、T17 SSE 流、T19 附件上传、T23 提醒作业、T24-T26 AI 链路、T28-T32 原生联调 / 收藏 / 配对、T33-T38 内部机制、U01-U12 UI 视觉专项、P01-P08 发布材料：均 NOT_RUN（依赖未在本轮完成的工程量）。
- L8 递交与回执：本地材料已就绪（`app/README.md` + `docs/build-loop/SUBMISSION.md` + `app/build/review.json`），Hub Issue / 公开发布 / 赛事提交均未发出——需用户授权。

## 2026-09-30 · 石墨版构建循环交接

用户确认比赛Token已到并选择石墨。本轮新增[15构建—验证循环](implementation/15_BUILD_VERIFY_LOOP.md)、[执行交接包](build-loop/README.md)、可复制启动提示、每轮记录模板、64项初始NOT_RUN台账及scripts/check_build_loop.py。L0–L8覆盖平台裁决、业务内核、原生报单/接单/设备/预约/处理/独立验收、AI/提醒/意图视图、恢复/视觉、封包与外部提交状态。仍保留原38业务/12UI验收，不把“简单”解释成角色切换或动画闭环。

同步README、AGENTS、架构入口、实施入口、05、10、12和UI参考说明；10的视觉参数同步石墨，原HTML稿未改。旧业务源码、机器契约、SQL和运行数据库未改。未创建业务app或运行L0，未配置/读取密钥、调用赞助模型、部署或公开提交。Router活动读取返回unknown，不能确认主会话路由；本轮无子代理或新任务。

|实际验证|结果与范围|
|---|---|
|设计包检查|通过：36必需文件、156本地链接、6张SVG及内嵌图；24操作/14命令/43schema/84引用；25表及10参考SQL约束场景；业务用例仅检查声明|
|迁移基线检查|79文件、3,591,754字节匹配，无需旧工作区|
|台账结构|64项均NOT_RUN，结构合法；--ready退出2，明确未达到本地交付门槛|
|检查器负向验证|正确拒绝缺项、将本地项改为外部项、SKIP、无证据PASS及工程外证据路径，共5项；这些是检查器验证，不是业务验收|
|入口与视觉参数|56个相关本地链接存在；15中全部六位石墨色值与原参考CSS相符；未执行原生视觉或对比度验收|

检查器只验证记录字段、文件和候选版本一致性，不检验日志事实或应用行为。后续编码方逐项提供真实证据，冻结同一候选版本后独立复跑；外部Hub递交/收录/赛事回执单列。未重跑234项旧后端测试或构建原生应用，64项初值不代表任何实际通过。


## 2026-09-29 · 课程 #2与最新制作发布指南核对

新增[14课程与最新源码裁决](implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md)。课程页面显示2026/09/28 19:44，读取AI纪要及段号0–98共99段可见自动转写，补齐虚拟列表后缺段数0；最后一段01:29:44，播放器约01:31:22。没有逐秒听校或下载录像，没有保存完整转写到交付包。浏览器核对结束后已关闭本任务创建的浏览器空间。

官方参考克隆刷新到固定提交，旧本地main保留，两份当前detached工作树均干净；当前及历史版本见[快照索引](../references/README.md)。额外读取Shell固定版本10个公开文件及相关PR状态，未完整克隆Shell；[源码索引](../references/course2-source-evidence.json)记录URL、SHA和字节数。Design-Flow中旧AI状态与当前源码有时间差：model、contained octos、首次同意及glance已合并，但默认开关、内核和权限等条件仍存在；工具审批仍被拒绝，事件驱动应用Agent未据此实现。

更新根README/AGENTS、架构入口、设计包入口、03/05/06/09/10/12/13与参考版本说明，新增接入Mermaid图；原六张SVG/HTML仍是有历史标记的旧部署图，G0裁决后再统一重绘。此次未更改业务源码、OpenAPI、SQL、UI参考或运行数据库。排期不变，9月28日G0未见通过记录明确列为当前风险。

|实际检查|结果与证明范围|
|---|---|
|设计包离线校验|通过：31个必需文件、141处本地链接、6张SVG及内嵌图；24操作、14命令、43schema、84引用；25表及10个参考SQL约束场景；T01–T38只检查声明|
|迁移清单校验|通过：79文件、3,591,754字节，原迁移基线未改，不访问旧WAgent|
|源码注册与拒绝路径阅读|核对ai-host注册、contained的device/peer与审批拒绝、model.complete、glance及Hub scan追加问题；只证明已读版本代码，不是运行通过|
|Router活动|本任务activity返回unknown / Router activity could not be read；不能确认或宣称主会话路由已切换，本轮无子代理或新任务|

未执行：上游安装或构建、真实模型调用、原生UI/业务/并发验收、234项旧后端测试、hub check/scan、签名、公开仓库发布、Issue提交或部署。没有消耗赞助模型Token。文档结构/SQL参考检查与源码存在性均不能作为G0完成证据。

后续修改：先按14第6节跑实际环境和业务底座切片，保存固定版本、授权/拒绝与回读证据；依据通过项选择身份/存储路线，再同步契约、适配和图册。发布时回答实际scan packet，不硬编码问题数；Hub状态与赛事回执分开保存。

## 2026-09-27 · 官方App Hub仓库与交付边界核对

已克隆用户指定的OctoSense-App-Hub及其直接链接的OctoScript-App-Design-Flow，均为main浅克隆；完整SHA、来源和目录见[参考快照](../references/README.md)。两份工作树检查均无修改。读取发布/开发/首次应用/图标规范、清单模板、准入与扫描源码、服务名契约及脚本API；新增[13 Hub规范与架构差异](implementation/13_APP_HUB_SUBMISSION_REVIEW.md)。未将上游文档里的verified当本项目实测。

结论落实到文档：脚本应用为Hub交付候选；本机Python桥接不再是默认路线；身份、事务、助手和证据在G0裁决；UI视觉和业务规则继续保留。同步根README/AGENTS、架构/迁移入口、00–11修订提示、03路线标记、05门槛、06规则、12排期、集成目录说明、图册历史提示及检查清单。新增参考目录忽略规则，避免参考克隆进入作品；原业务代码、OpenAPI、SQL与运行数据未改。

|实际检查|结果与范围|
|---|---|
|设计包校验|通过：30必需文件、130本地链接、6 SVG及内嵌图；24操作、14命令、43schema、84引用；25表、10个参考SQL约束场景|
|迁移清单校验|通过：79文件、3,591,754字节，无需旧工作区|
|官方仓库工作树|两份干净；Hub未检出.github工作流，发布文档明确当前无发布Action|
|路由核对|本任务Router activity返回unknown（Router activity could not be read）；不能确认或声称主会话已切换|

**未执行**：运行时依赖安装、Rust构建、hub check/scan、原生UI、真实模型、38项业务/12项UI验收、原234项后端测试、签名、部署、公开发布或Hub Issue提交。克隆不等于G0通过，设计校验不等于产品通过。当前PATH中未找到cargo，标准~/.cargo/bin位置亦未找到；未做全机Rust安装探测，不据此断言系统绝无工具链。

后续修改方式：先以固定版本准备环境，执行13的G0切片并记录真实结果；再选定任务权威/身份/存储路径，同步03/04、全部图源和适配实现。包内文件变更后重新stamp/check，已签名版本重新签名。10月9日截止目标保留；精确关门时间和赛事采用递交还是收录的口径仍待主办方明确。

## 2026-09-26 · 用户确认的10月9日交付排期

新增[12交付排期与差异清单](implementation/12_DELIVERY_PLAN_20261009.md)，按用户要求将10月9日设为本项目初赛截止日期，内部以10月6日晚功能基本完成、10月7日独立验收、10月8日优先提交安排。官方具体关门时刻未补造；旧10月3/4日与9日不同阶段仅保留为历史证据。业务方向及用户P0功能保持。

同步根README、AGENTS、架构入口、设计包README、00决策、05实施验收、06规则、07历史修订、11课程对照及必需文件检查清单。明确待改的宿主适配、UI落地、生成过程证据、主动跟进、意图视图、原生验收与官方回执；这些后续任务未标成已实现。

实际运行`python3 docs/implementation/verify_pack.py`通过：29必需文件、112本地链接、6张SVG；24操作、14命令、43schema、84引用；25表及10个参考SQL约束场景。只修改文档与设计包清单，不修改业务代码、OpenAPI、SQL或运行数据库。本轮未重跑后端/原生/模型/业务验收，未设置自动提醒、提交作品或公开发布。

## 2026-09-26 · 研讨课 #1 逐字稿与设计v1.2

来源：[会议录制](https://meeting.tencent.com/crm/2kAd7Z94bd)。读取页面AI纪要并切换逐字稿；因虚拟列表首遍有缺段，使用小步正向及反向滚动补齐，最终段号0–211共212段连续，覆盖00:00至最后一段03:29:44，播放器时长约03:30:14。阅读的是自动转写，未逐秒听校音频、未逐帧核对屏幕资料。页面不允许下载/转存，本轮没有下载录像或在工程交付完整转写。

新增[11课程对照](implementation/11_COURSE1_BASELINE_REVIEW.md)，同步设计包00–10的修订提示、图册历史路线提示、根README/架构/迁移及文档检查清单。原生应用为主选、App Card分工及主动跟进是本项目据课程作出的设计响应，不是假称已运行的官方SDK能力。旧源码、OpenAPI与SQL未改，旧图保留为明确标注的v1.1历史路线。

实际检查：`python3 scripts/verify_migration.py`通过，79文件/3,591,754字节；`python3 docs/implementation/verify_pack.py`通过，28必需文件/100本地链接/6张SVG、24操作/14命令/43schema/84引用、25表及10个参考SQL约束场景。未重跑234项后端测试或真实业务验收，未构建原生宿主、调用产品模型、接通总线、部署或提交比赛作品。

外部web读取工具网络失败；本次会议证据来自成功打开的腾讯会议浏览器页面。Router活动检查返回unknown，不能确认主会话路由，未以其他模型调用冒充切换。本轮没有新建用户任务。课程资料包、正式更名/仓库、最终赛程、提交workflow和混合后端支持仍待具体资料核对。

## 2026-09-26 UI设计要求补充

新增10_UI_UX_SPEC.md，定义角色化工作台、持续任务卡、Agent建议/事实/动作分层、预约与证据交互、视觉token、反馈恢复、窗口/键盘和U01–U12专项验收；同步根README、设计包入口、01需求、05实施验收和交付文件检查清单。

实际运行`python3 docs/implementation/verify_pack.py`通过：27个必需文件、86处本地链接、6张SVG、24个操作、14类命令、43个schema、84处引用、25张SQL表及10个参考约束场景。未修改业务代码。本轮没有制作高保真稿、运行原生UI、进行视觉截图验收、测量颜色对比或开展可用性测试；38项业务用例和12项UI用例均仍待执行。

后续修改视觉和交互需同步10及组件设计；动作或权限变化须同步01/04和T/U用例。文档检查不能代替交互、美观和原生运行验收。

## 2026-09-26 会议材料与架构v1.1修订

新增07会议证据/架构、08代码复用、09 Agent运行与独立核验，第六张SVG/Mermaid及HTML图册入口；同步00–06、根README/架构/迁移、宿主说明和AGENTS。机器接口和参考SQL未改；本轮没有实施新业务代码。

|实际执行|结果与范围|
|---|---|
|Router DeepSeek只读代码盘点|定位设备/历史/经验/模型流式处理与旧写路径；确认新任务/预约/验收/原生宿主缺口；代理未写文件，未跑真实模型|
|官方资料刷新|直接取得官网HTML和完整JS、robrix2 README、octoscode README及OctoLoop指南。官网JS为224,514字节，SHA与9/22相同；课程包未取得/运行|
|资料读取失败处理|web工具本地服务连接失败；首次JS下载超时且文件不完整，未把部分文件当完整证据。后续curl完整读取并核对字节数/SHA|
|`python3 docs/implementation/verify_pack.py`|通过：26必需文件、82本地链接、6张SVG及HTML内嵌图；T01–T38编号唯一完整，仅检查声明未执行用例|
|参考契约/SQL检查|通过：24操作、14命令、43schema、84引用；25表、10个SQL约束场景，仍是单连接离线设计检查|
|`python3 scripts/verify_migration.py`|通过：79文件、3,591,754字节；没有改旧源码或访问旧WAgent|
|可视图限制|第六图完成SVG结构/内嵌一致性检查，本轮未做浏览器截图或完整视觉验收；9/22的浏览器限制见下方历史记录|

主会话Router活动读取返回unknown，不能确认切换；Router子代理参与不作为主会话路由证据。当前任务沿用原有0921日期标题，没有新建用户任务。未重新跑234项后端测试，未构建宿主、未调用真实模型、未发消息/推送/部署。38项业务验收均待实现后执行。

验证记录描述本轮实际行为，不把代码存在性、资料可访问性或设计脚本通过提升为应用运行成功。

## 2026-09-22 编码设计交付检查

本轮交付[设计包](implementation/README.md)，未实现新业务、未改迁移源码、未写运行数据库。官方复核方法与来源见[合规矩阵](implementation/06_OFFICIAL_COMPLIANCE.md)。开发辅助使用Codex Router代理；原生图稿代理发生上游400错误后停止，已由主会话补齐文件。不能据此声称主会话已切换到Router模型。

|实际执行检查|结果与证明范围|
|---|---|
|`python3 docs/implementation/verify_pack.py`|通过：21个必需交付文件、57处本地链接、5张SVG及HTML内嵌图；无重复HTML/SVG ID|
|参考OpenAPI引用检查|24个操作、14类命令、43个schema、84处引用可解析；不是实际FastAPI服务契约测试，也不是完整OpenAPI标准验证器|
|参考SQL内存执行|25张repair_*表创建成功；10个约束场景通过，包括同技工跨项目重叠、相邻区间、单任务有效预约、更新重叠、跨项目设备、幂等键、跨任务证据和经理验收理由|
|`python3 scripts/verify_migration.py`|通过：79文件，3,591,754字节；不访问旧工作区；迁移基线未变|
|浏览器加载图册|ego-browser实际加载HTML并识别5张SVG；读取渲染文字边界，修正长标题、样式隔离和左侧旋转标签边缘越界|
|浏览器能力限制|两次截图调用均超时，未取得截图；缩放按钮自动点击因视口可见性失败，交互未完成验证；最后一次标签位置微调仅静态复查，不声称完整视觉验收通过|

SQL约束场景使用单个内存连接，不是并发业务测试。T01–T32全部仍为待执行用例。未安装依赖、未构建robrix2、未调用真实模型、未连接外部工单。本轮没有重跑原234项后端测试，下面是2026-09-21的历史结果。

修改方式：需求变更同步设计包00/01、02/04、OpenAPI/SQL、图册及05验收；重新运行上述两条命令，补记真实结果。详细业务守卫仍须编码实现，不能把这些文档检查当作应用通过验收。

## 2026-09-21 迁移历史

日期：2026-09-21。执行分工：Codex Router 的 DeepSeek 代理负责文件清点、版本比较和机械复制；主模型负责架构文档、运行脚本及独立核验。

## 已完成

| 检查 | 本次结果 | 证明范围 |
|---|---|---|
| 来源版本 | `a9caf17e0f830b23e694f952e21e6c0dbefa34cc`，源工作树干净 | 复制来源可定位 |
| 字节一致性 | 79 文件，3,591,754 字节，SHA-256 全部匹配 | 源码、原测试和指定资源未被复制操作改写 |
| 独立清单校验 | `python3 scripts/verify_migration.py` 通过 | 不访问原工程即可检查复制快照 |
| 离线基线测试 | **234 passed in 7.29s** | 使用复制后的源码及原测试，未执行真实模型脚本 |
| 搬移验证 | 临时复制到另一个目录后清单校验通过 | 根目录变化不会破坏文件布局与来源校验 |
| 搬移后路由冒烟 | `/api/health`、`/`、`/graph`、`/api/ops/spaces` 均 200；健康响应符合预期 | 复制后的入口、静态页面和种子查询可加载，不等于真实模型任务成功 |
| 路径隔离 | Python 导入路径断言指向新副本；测试数据指向临时目录 | 未把旧源码的测试结果冒充新副本结果 |
| 排除项 | 未带入 `.env`、私钥、运行 DB、kg.json、会话、虚拟环境和软链接 | 运行状态与凭据未随文件迁移；不是全面开源审计 |

## 环境与限制

- 主模型测试借用了原开发环境的 Python 3.12 解释器及第三方依赖，但以 `PYTHONPATH` 显式导入新副本，并断言实际导入路径。移动测试也如此；新包本身没有包含或链接该虚拟环境。
- 本次未在全新机器执行 `uv sync --frozen`；移动后需按 README 重建环境。锁文件已原样保留，不把现有环境下通过测试称为全新安装通过。
- 路由冒烟通过 FastAPI TestClient 执行，不是浏览器视觉验收，也不是官方宿主或真实服务联调。
- 没有调用真实模型、发送通知、创建外部工单、连接用户邮箱/日历或访问真实设备。
- OctoSense SDK、任务卡、任务应用服务、偏好与新的纠错机制均未实现或验证。
- 原 `.env.example` 不在复制清单；新工程的 `backend/.env.example` 由主模型另建且不含凭据。
- 种子保持开发版的 2026-08-23 场景时间；没有迁移评委演示版的 2026-09-13 场景。

## 复查命令

在新工程根目录、完成依赖安装后：

```sh
python3 scripts/verify_migration.py
backend/.venv/bin/python scripts/test_baseline.py
backend/.venv/bin/python scripts/run_local.py
```

真实模型冒烟、任务级对照、平台接入及干净环境安装需要分别验收，不能用以上 234 项离线测试替代。


## 2026-09-26 · 四版 UI 参考

新增独立 [UI参考文件夹](../design-references/2026-09-26-ui-variants/README.md)，包含四版配色、布局、按钮与本地示例交互。已核验脚本语法、四版加载、1440px文档溢出以及13项页面状态；完整范围和截图超时限制见 [参考包核验记录](../design-references/2026-09-26-ui-variants/VERIFICATION.md)。未修改业务后端，未接通正式宿主或真实服务。


## 2026-10-06 · 比赛展示材料与源码更新

本轮实际检查、视频参数、截图来源和未通过项集中记录于 [提交核验](../submission/2026-10-06/VERIFICATION.md)。190 项领域单测与 17 步独立 HTTP E2E 通过；hub check 通过（unsigned），整体 --ready 仍 NOT READY。迁移哈希检查退出 1，列出 5 个既有修复文件；没有将原始清单更新为假通过。媒体制作与项目整理不构成原生、模型或赛事收录验收。
