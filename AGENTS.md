# 新工程协作约定

2026-09-30用户选定石墨UI（04-graphite），覆盖此前青绿默认候选；比赛Token已到不等于配置/真实调用已通过。执行入口docs/implementation/15_BUILD_VERIFY_LOOP.md与docs/build-loop/START_PROMPT.md；按L0–L8闭环构建，不删除既有P0/38业务/12UI验收。ACCEPTANCE.json记录真实证据，check_build_loop.py仅检查记录，不执行应用测试。

2026-09-29新增优先依据docs/implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md（课程 #2 与当前源码）。Design-Flow README的9/27 AI状态已落后：Shell已合入model.complete、contained octos和glance，但助手默认关闭、需内核与首次同意、工具审批仍拒绝；manifest agent文件准入不等于后台Agent运行。保留13的包/身份/存储边界、12的期限，G0仍未通过。

先读 README.md、docs/ARCHITECTURE.md、docs/MIGRATION.md、docs/VERIFICATION.md。

2026-09-27先读docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md（Hub实证约束）；Hub优先脚本应用，不把本机Python服务或新增Rust代码装入bundle。保留旧代码与业务规则，G0先裁决存储/身份/模型/协作；不擅自部署公网或降低验收。官方参考克隆仅作资料，不进入作品包。

排期执行入口为docs/implementation/12_DELIVERY_PLAN_20261009.md（排期）与11_COURSE1_BASELINE_REVIEW.md（课程修订），再读00–10。用户明确本项目10月9日初赛截止、10月7日前基本完成；内部目标10月6日晚主要功能完成，10月7日验收、10月8日优先提交。旧10月3/4日赛程仅作历史证据，不覆盖当前用户排期。业务方向与P0功能保留；日期是目标，不是已完成。官方包、真实模型和业务完成分别验收。

- 这是独立迁移副本；不得依赖或修改旧 WAgent 工作区。不要把旧项目的过期赛程、固定开发截止日或“永远只能 11 个工具”自动当作新产品要求。
- `backend/src/wagent_backend/ops/contracts` 保持迁移基线兼容。新任务协议单独版本化；如确需改旧契约，明确记录调用方、测试、数据迁移和兼容方式，不静默重写。
- 用户希望先确定架构与迁移，具体功能在新空间讨论。架构文档中的目标模块不是已实现功能。
- 本项目全程使用 Codex Router。新增对话启动时核对实际模型路由；若当前主会话无法切换或无法确认路由，明确说明，不能把启用技能或调用一个 Router 子代理说成主会话已切换。可委派工作使用 Router 代理；简单机械工作使用 DeepSeek，架构、关键逻辑与最终核验由主模型负责。每个代理有明确文件所有权，不覆盖他人改动。
- 每个新增对话都必须按 `MMDD｜TYPE｜Topic` 实际设置标题，不能只提出标题建议。日期取该对话的 `createdAt` 并转换为 Asia/Shanghai，不使用 `updatedAt` 或当前日期代替。TYPE 默认统一使用英文代码 `FEA / DES / FIX / OPT / REL / EXP / DOC / RES`，仅用户要求中文时使用对应中文标签，同一次运行不混用语言。Topic 简短具体，概括实际内容，不重复项目名称；主题无法辨别时保留原标题。取得创建时间及明确主题后设置标题，并回读核验；只改标题，不改项目名称、对话内容、项目分配、顺序、置顶或归档状态。
- 运行数据统一放 `runtime/`，密钥放本地环境或未入库的 `backend/.env`。模型调用、写数据库、上传/发消息与部署须符合当前用户授权。
- 仿真真值与 Agent 输入隔离。旧演示洞察和仿真聚合洞察不能作为自动学习效果的证明。真实模型效果、官方平台接入和任务最终完成，必须分别验证。
- 未来所有业务副作用均收敛到任务执行边界，旧 runner 也必须经过该边界；不能只在新卡片按钮上加校验，而保留模型绕过路径。
- 先沿用单进程模块化后端和 SQLite。没有实测理由，不拆微服务，不重写全部 Python，不另做独立桌面壳。
- 当前无生产认证与租户隔离保证，默认仅本机开发。身份标识可以为偏好预留，但不等于认证授权已经实现。
- 文件修改后更新相关文档，解释改哪里、怎么改、如何验证以及哪些还没接通。不伪造测试结果。
