# 文件迁移说明

**9月27日：[Hub包边界](implementation/13_APP_HUB_SUBMISSION_REVIEW.md)**不允许随包安装Python/新增原生代码。旧Python文件保留为迁移与回归资产，具体复用到何种运行位置须G0决定；复制成功不等于可直接打包。

> 最新依据为[研讨课 #1 对照修订](implementation/11_COURSE1_BASELINE_REVIEW.md)。原生目标保留，但原robrix2不再被视为全部作品唯一宿主；Python复用和具体配对方式须重新过G0。迁移来源与领域业务规则不变。

2026-09-26补充：[代码复用与改造清单](implementation/08_REUSE_MIGRATION.md)给出逐模块继承、修改与新增责任。旧contracts继续保护，旧JSONL不替代业务事务库，模型自报根因不作学习真值。Rust移植仅在正式约束或实测理由成立时按[07方案](implementation/07_REVISION_20260926.md)定向执行。迁移来源与下方历史说明不变。

## 来源选择

迁移来源为原工程的 `wagent/agent/`，不是对 `评委演示_v1/` 整包复制。原仓库提交：`a9caf17e0f830b23e694f952e21e6c0dbefa34cc`。迁移时源仓库 `git status --short` 无变更。具体两版本差异及最终复制数量见 VERIFICATION.md。

新目录采用 `backend/` 包装原 `agent/` 的完整运行依赖闭包，包名仍为 `wagent_backend`。不复制虚拟环境、不保留旧工程软链接，也不依赖原目录作为 Python 导入路径。目录整体移动后重新安装依赖即可；现有种子路径均相对复制后的模块定位。

开发版与评委版依赖声明、锁文件和 GraphRAG 核心相同。评委版额外包含访问码中间件，限制图谱写操作和重置，并移除抽取路由，因此采用开发版作为继续开发的基线。两者并非单纯时间先后版本：开发版演示基准为 2026-08-23，评委版为 2026-09-13；此次保留开发版日期及工单编号，没有混入评委版种子。

## 文件去向

下表路径均相对原 `wagent/`；新路径相对本工程根目录。

| 原文件/目录 | 新位置 | 迁移方式与理由 |
|---|---|---|
| `agent/src/wagent_backend/ops/` | `backend/src/wagent_backend/ops/` | 原样保留运维契约、工具、数据仓储、runner 和记忆机制 |
| `agent/src/wagent_backend/llm/` | `backend/src/wagent_backend/llm/` | 原样保留模型客户端、流组装和嵌入 |
| `agent/src/wagent_backend/web/` | `backend/src/wagent_backend/web/` | 原样保留路由、页面及资源，作为回归基线，不是新卡片 UI |
| `agent/src/wagent_backend/graphRAG/`、`agent/`、`tools/` 及包初始化文件 | `backend/src/wagent_backend/` 对应位置 | 保留当前入口和测试依赖，不在复制时大规模删包 |
| `agent/tests/` | `backend/tests/` | 原样保留现有离线测试和真实模型脚本；后者本次不执行 |
| `agent/pyproject.toml`、`agent/uv.lock` | `backend/` | 保留依赖及打包约定，后续有意修改再单独记录 |
| `agent/README.md` | `backend/README.md` | 保留历史说明，仅作原后端参考；新项目状态以根 README 与 docs 为准 |
| `agent/data/simseed/l1_seed.json` | `backend/data/simseed/` | 仅搬迁声明过来源的仿真快照 |
| `agent/data/simseed/l2_events.jsonl`、`PROVENANCE.md` | `backend/data/simseed/` | 保留仿真事件与来源，不包含评测真值 |

每个复制文件的 SHA-256、字节数和来源见根 `migration-manifest.json`。新写的 docs、scripts、AGENTS.md、.gitignore 与 .env.example 不属于原样复制清单。

## 明确排除

- 原 `.env`、服务器私钥、部署凭据、历史运行数据库、`data/kg.json`、`data/sessions/`。
- `.git`、`.venv`、缓存、截图、视频、旧服务器安装和发布脚本。
- `评委演示_v1/` 整包、旧工作区辅助配置和旧项目 AGENTS.md。
- 根 `ontology/`、`simulator/`、`harness/`、`scripts/`：现有后端有内嵌契约，运行不需要这些目录。评测器当前尚未完成；以后另建隔离的评测模块，不能把真值迁入 Agent 数据目录。
- 原长篇方案文档不整包复制，以免把旧冻结日期、旧比赛规则和待办误当新要求；必要设计与迁移理由已经写入新文档。

`simseed/PROVENANCE.md` 中的旧 Git 再生成命令仅作为历史来源说明；新工程不包含那段 Git 历史，不能直接执行该命令重建数据。这不会影响随包仿真快照导入。后续正式评测需要再迁移经过审查的生成器及其版本，不应伪称当前包已具备完整评测可复现性。

## 迁移后如何继续改

2026-09-22更新：功能边界已确定，按[编码交付包](implementation/README.md)实施。下面是迁移时的原顺序记录；最新G0–G5及文件所有权以设计包为准。新流程写runtime/repair.db中的repair_*表，不直接复用旧工单为第二个事实源；旧ops/contracts保持兼容。当前只新增设计及校验文件，未改迁移源码或运行数据库。用户偏好与学习对照移到P1。

1. 在新空间确认功能边界，再验证平台最小接入；记录 SDK/宿主版本。
2. 在 `application/` 与 `task_contracts/` 建立新模块，旧契约先保持兼容。
3. 把 `web/routes_ops.py` 中任务级操作逐项抽到应用服务，把 runner 中写操作同步接到统一执行边界。一次迁移一个操作，并跑对应旧测试和新增的任务行为测试。
4. 再接卡片投影与持久化任务，验证重启、重复提交、过期确认和失败恢复；不能只验证页面可点击。
5. 最后接偏好与可信验收反馈，补对照结果；旧种子数据不能作为自动学习的实验结论。

原仓库的 FROZEN.lock 和钩子未复制。旧契约的兼容性由复制的测试保护；如果确需修改，不是删除测试了事，而是定义新版本、兼容迁移及验证。

## 移动与验证

复制或移动整个 `WAgent-OctoSense` 目录，不要只搬 `backend/`。随后照根 README 安装依赖并运行 `scripts/verify_migration.py`、`scripts/test_baseline.py` 和 `scripts/run_local.py`。

启动器把运行状态统一定位到新根目录 `runtime/`。建议使用启动器；若直接运行旧 `kg-web`，其默认数据目录仍沿用旧代码的相对路径规则（位于新 backend 内），也不是新卡片服务。已产生的旧业务数据库不自动升级到未来任务模型。

本包用于内部迁移。源码中的示例种子仍需审查来源与许可；未复制运行数据库并不意味着所有内嵌内容已经完成对外发布审查。
