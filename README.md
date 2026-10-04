# 知了 · 维修任务协作与 AI 助手

队伍名：**知了**。本仓库用于 Agentic App 2026 初赛源码提交，基于 WAgent × OctoSense 独立迁移工程持续开发。

**2026-10-02 提交说明**：本次登记源码仓库地址，不代表应用已通过全部验收。最近一次独立复核见 [修复核验报告](docs/build-loop/REPAIR_VERIFICATION_2026-10-02.md)；下方历史状态、测试数字和版本需按记录时间解读。运行数据、密钥、虚拟环境及官方参考克隆不提交。发布准备与范围见 [仓库提交记录](docs/build-loop/REPOSITORY_SUBMISSION_2026-10-02.md)。

**OctoSense App Flow 摘要**：本项目作为脚本应用（Script App / octoscript 应用）提交，按官方 [`app-hub-submission.md`](https://raw.githubusercontent.com/gosimfoundation/hackathon-agenticapp26/main/docs/app-hub-submission.md) §"所有作品需要的材料"六项 + [`PUBLISHING.md`](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md) 规范整理。详细见 [`docs/PROJECT.md`](docs/PROJECT.md)；Hub gate 等价自检见该文件 §十。

| OctoSense 场景 | 落点 | 接入 |
|---|---|---|
| 写作 / 创作（writing/creation） | 报修原话 / 处置记录 / 完工说明 / 备注 / 钉选 | ✅ 核心 |
| 系统 / 设备（system/devices） | 设备身份 / 空间服务关系 / 隔离存储 | ✅ 核心 |
| 生产力（productivity） | 工作台 + 命令边界 + 状态机 | ✅ 核心 |
| 日历（calendar） | `repair_appointments` 预约窗口 | ⚠ 内部实现 |
| 邮件 / 即时消息（mail / messaging） | 站内通知 + 撤权失效；不连 Rinx Matrix | ⚠ 仅站内 |
| 购物 / 物流（shopping / logistics） | 设备服务关系 (`repair_asset_services`) | ⚠ 预留接口 |
| 天气 / 新闻 / 音乐 / 视频 / 行情 / 导航 | — | ❌ 不在范围 |

**bundle 入口**：`app/bundle/`（`manifest.json` schema 1 / `listing.json` / `main.splash` / `assets/icon.svg` / `screenshots/01-main.png`）；宿主 `card-host --bundle app/bundle --allow-unsigned`（独立 sandbox，详见 `docs/PROJECT.md` §三）。**Agent 任务演示**（input → execute → verify → human confirm 全链）见 `docs/PROJECT.md` §五。

**10月2日（当前）：全盘 review 后本地**未就绪**。台账 **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**（合计 64）；3 项 BLOCKED 是 **P06/P07/P08 外部递交授权**，不是 jobs/LLM。10-01 自评的 33 PASS 中有 **9 项被改判**（T01→NOT_RUN，T02/T03/T05/T08/T16/T17/T18/T29→FAIL），其中 5 项为 P0。问题清单、复现命令与修改建议见 [docs/build-loop/REVIEW_2026-10-02.md](docs/build-loop/REVIEW_2026-10-02.md)，本轮执行记录见 [docs/VERIFICATION.md](docs/VERIFICATION.md)。`check_build_loop.py --ready` 返回 NOT READY。**

**10月1日（历史）：L0-L6 主切片本地 ready，33/64 项 PASS、3 项 BLOCKED。该自评偏乐观，已被 10-02 review 修正，仅作历史证据保留。**

**9月30日构建入口：[石墨版完整构建—验证循环](docs/implementation/15_BUILD_VERIFY_LOOP.md)** · [可复制启动提示词](docs/build-loop/START_PROMPT.md)。用户已选择石墨、确认比赛Token到账；按L0–L8创建、验证、修复与交付。64项台账初始均NOT_RUN，不代表应用已实现或Token已接通。

**9月29日最新依据：[课程 #2 与制作发布指南核对](docs/implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md)**。已读99段完整可见转写，并核对最新Shell源码：系统助手、一次性模型调用、glance支持已有实现，开发指南AI状态部分过时。应用运行仍未验证；身份/存储/协作须G0裁决，业务与UI方向、10月9日期限不变。

**9月27日官方仓库核对：[Hub提交规则与架构差异](docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md)**。Hub和官方开发指南已克隆至references，版本见[快照索引](references/README.md)。保留维修业务与UI视觉；交付改为验证脚本应用，旧本机Python桥接不可直接随包发布。宿主、身份、持久化及真实模型仍待G0。

**当前交付期限：[项目排期与差异清单](docs/implementation/12_DELIVERY_PLAN_20261009.md)**。按用户要求10月9日初赛截止，内部目标10月6日晚主要功能完成、10月7日验收、10月8日优先提交。维修协作方向不变；日期均为目标，功能尚待实施。

**9月26日历史设计v1.2：[研讨课 #1 逐字稿核对与基线修订](docs/implementation/11_COURSE1_BASELINE_REVIEW.md)**。已读完整可见逐字稿212段；修正唯一robrix2宿主假设，补应用生产过程、原生持久应用/App Card分工和主动跟进方向。尚未接通课程环境，以下v1.1内容涉及宿主时以v1.2为准。

这是独立迁移基线与**比赛版编码设计交付包**，不是已完成的 OctoSense 应用。现有运维后端复制到 `backend/`，原工程不变。2026-09-22已将本地报单、接单、设备身份、原生桌面展示、预约、进度及验收写成详细设计；外部工单只预留接口。

**9月26日设计v1.1：[会议证据与架构修订](docs/implementation/07_REVISION_20260926.md) · [旧代码复用清单](docs/implementation/08_REUSE_MIGRATION.md) · [Agent运行与独立核验](docs/implementation/09_AGENT_HARNESS.md)。** 保留原业务逻辑与任务协议；区分官方Rust技术栈与初赛语言门槛，补充意图建议、执行和证据机制。

**完整入口：[编码交付包](docs/implementation/README.md) · [六张架构图册](docs/implementation/ARCHITECTURE.html) · [官方要求映射](docs/implementation/06_OFFICIAL_COMPLIANCE.md)。** 可以把本目录整体移动到任意位置，再作为独立项目打开。

**UI设计要求：[原生界面与交互规范](docs/implementation/10_UI_UX_SPEC.md)**，包含页面结构、角色操作、视觉参数、异常恢复及12项待执行UI专项验收。

**四版可点击 UI 参考：[风格总览](design-references/2026-09-26-ui-variants/index.html) · [使用说明](design-references/2026-09-26-ui-variants/README.md)**。青绿、钴蓝、赭橙、石墨四个方向，包含配色、按钮及报单/预约/验收示例交互；独立存放，仅使用固定示例数据。

## 从这里开始

本项目全程使用 Codex Router；每个新增对话按 `createdAt` 的北京时间命名为 `MMDD｜TYPE｜Topic`。实际路由核对、标题设置与回读规则见 [AGENTS.md](AGENTS.md)。这些约定不会自动切换当前会话模型。

1. 阅读 [架构设计](docs/ARCHITECTURE.md)：哪些保留、哪些调整、哪些尚未实现。
2. 阅读 [迁移说明](docs/MIGRATION.md)：文件来源、排除项、迁移和验证方法。
3. `migration-manifest.json` 记录每个原样复制文件的相对来源、大小和 SHA-256；`docs/VERIFICATION.md` 记录本次实际验证。

## 当前交付范围

- 已复制：现有 Python 后端、旧 Web 页面、测试及指定仿真种子；不是生产环境数据库的复制。
- 已实现（10月1日实现，10月2日复核）：
  - **业务后端 `octosense_backend 0.2.0`**：12 张 SQLite 表、27 类业务命令、29 个应用路由（27 命令 + get_task + health）；**39 项单测全过**；端到端 13 步完整业务链路（DRAFT→COMPLETED，含退回重做）真实通过 curl 验证（10-02 独立端口 + 独立 DB 复跑仍 PASS）。
  - **原生 UI `octosense-repair 0.1.0`**：main.splash 石墨工作台；fs jail 内 state.json + events.jsonl 写入；card-host kill + restart 后 **state.json 回读成功但任务本体丢失**。10-02 实测：splash 声明 23 个节点，运行时只实例化 15 个，"退回 / 重置演示 / 任务列表 / 状态行"不存在（REVIEW_2026-10-02.md R-P0-1 / R-P1-1）。
  - **边界 E2E**：T04 双技工抢单只一人、T15 旧 version 409、T18 缺 actor 返 401、T30 收藏不互相影响、T31 取消释放预约 均通过；**T02 同 key 幂等只覆盖『同 key 同内容』，『同 key 不同内容返 409』未实现**；T05/T18 已在 10-02 改判为 FAIL（跨项目可写、`get_task` 无授权）。
  - **ACCEPTANCE.json 24/64 PASS**；29 NOT_RUN；**8 FAIL（T02/T03/T05/T08/T16/T17/T18/T29）**；3 BLOCKED（P06/P07/P08 外部递交）。原 33 PASS 中 9 项经 10-02 review 改判。
- 已设计但未实现：生产认证（X-Actor-Id 仍是 demo，且**未按 project 隔离**，见 R-P0-2 / R-P0-3）、真实 LLM 接入（明确标记为离线演示，原话保留）、jobs/scheduler/notification 后台、原生 App Card / glance 视图、Hub Issue 与赛事回执（待 L8 授权后递交）。
- **10-02 待修**：见 [docs/build-loop/REVIEW_2026-10-02.md](docs/build-loop/REVIEW_2026-10-02.md) §6——5 项 P0（原生半节点 / 跨项目可写 / 读无授权 / 幂等不 409 / web 路径死锁）+ 8 项 P1 + 7 类 P2。
- 没有复制密钥、`.env`、虚拟环境、运行数据库、历史会话或 Git 历史。
- bundle digest（最新 hub stamp）：`c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`

## 移动后运行

需要 Python 3.11+ 和 uv。在**本工程根目录**执行：

```sh
cd backend
uv sync --frozen
cd ..
python3 scripts/verify_migration.py
backend/.venv/bin/python scripts/run_local.py
```

Windows 最后一行改为 `backend\.venv\Scripts\python.exe scripts\run_local.py`。默认只监听 `127.0.0.1:8711`，避免与旧工程的 8700 端口混淆。未配置模型时可检查健康接口与旧页面，不能完成真实 AI 对话。

如需模型调用，把 `backend/.env.example` 复制为 `backend/.env`，自行填入兼容服务的配置。启动器将数据库、图谱和会话位置固定到**新工程的 `runtime/`**，不会沿用旧工程路径。首次启动仍使用原有演示种子，部分种子源自人工示例或历史资料，不能当成 Agent 自动学到的实验结果。

离线基线测试（假模型，不调用真实模型）：

```sh
backend/.venv/bin/python scripts/test_baseline.py
```

`verify_migration.py` 验证的是迁移时的基线快照。以后有意修改复制文件，哈希变化属预期，应保留原清单作来源证据，在变更记录中解释，不要为让检查通过而覆盖原清单。

## 下一步编码入口

> 请先读 AGENTS.md、docs/ARCHITECTURE.md、docs/MIGRATION.md、docs/VERIFICATION.md，**以及 docs/build-loop/REVIEW_2026-10-02.md（当前问题清单与修复顺序）**，再按 docs/implementation/README.md 阅读设计包。以05_IMPLEMENTATION_ACCEPTANCE.md的完整接手提示和G0–G5实施；不要把旧演示页面或预留目录当成OctoSense已接入，不将设计检查通过写成业务功能已实现，**也不要把 ACCEPTANCE.json 里的 PASS 当成已独立复核的结论**。

## 迁移阶段发布说明（历史）

以下为迁移阶段的历史说明，实际仓库登记以文首及[提交记录](docs/build-loop/REPOSITORY_SUBMISSION_2026-10-02.md)为准：本目录当时是内部开发交接包，没有自动为原代码及数据重新授予开源许可。赛方要求 Apache 2.0 开源；当时尚未发布仓库。本次仓库登记未另外变更已有代码及第三方资源的许可声明。
