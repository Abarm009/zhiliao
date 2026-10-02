# 2026-10-02 独立代码审查与旧报告对照

## 结论及范围

**当前实现不满足项目基线的本地交付要求，置信度高。** 既有 39 项测试通过，但定向反例证明权限、命令状态、幂等、预约恢复、验收和界面动作存在漏洞。旧报告主要结论成立，但覆盖不全，部分修复建议会引入回归；旧报告保留的 24 项 PASS 不能整体视为独立核验通过。

本轮先阅读 README、ARCHITECTURE、MIGRATION、VERIFICATION，核对实施 13/14/15、START_PROMPT、业务需求及验收条款，然后审查当前源码，再读取旧 REVIEW 逐项对照。README 和 VERIFICATION 已包含旧报告摘要，因此并非严格盲审。未重新核实上游平台现行政策，平台约束按本地冻结基线理解。

审查对象：`backend/src/octosense_backend` 的命令/API/数据库/预约/扩展/种子、`app/bundle/main.splash`、`app/demo-web`、相关测试、启动与验收记录。旧 wagent 仅检查迁移完整性和回归入口，未声称对旧 GraphRAG/runner 全部代码完成逐行审计。

仅新增本报告和 `runtime/review-independent-20261002/` 下的审查脚本、日志、源码哈希记录；未修改业务代码、现有测试、旧报告或 ACCEPTANCE.json。探针全部使用临时数据库及临时附件目录；数据库旧证据通过复制到临时目录后读取，未操作原运行库。未调用真实模型、发布、发送消息或重启宿主。

工作区根没有 Git 仓库，不能给出 Git diff 或候选 commit。`source-sha256.json` 固定了本轮审查的核心源码内容。Router activity 返回 unknown，无法确认主会话路由；未创建代理或宣称已切换模型。

## 1. 基线理解

- 正式方向是石墨 UI 下的报修、接单、设备、预约、开工、完工、独立验收/退回闭环。
- 单一任务事实源，原生入口与其他入口共用业务执行边界；不能另造一个不受约束的原生状态机。
- 权限必须同时考虑项目、角色、任务报修人/承接者、技能和当前阶段。演示身份不免除业务权限验证。
- 任一命令应有明确源状态、版本约束、请求幂等、持久回执和事件，不能只验证目标状态是否在通用状态图中。
- 首次预约确认后才 SCHEDULED；拒绝改约保留原确认预约及 SCHEDULED（01_REQUIREMENTS.md:103）。经理代验收必须有理由（T20），退回再完工必须有新 completion_id（T21）。
- 原生包准入、原生业务与重开、真实模型、发布回执必须分开证明。检查器只验证记录。

## 2. 本轮实际验证

|检查|实际结果|证据/边界|
|---|---|---|
|新后端现有测试|39 passed，0.15s|`pytest.log`；包含 dummy，不代表所有验收条款|
|临时库 HTTP/命令探针|复现下述缺陷及对照行为|`probe.py` / `probe.json`；FastAPI TestClient，非真实浏览器|
|前端函数执行|首次预约无确认入口；隔离动作传入 undefined 路径|`frontend-probe.cjs` / `frontend.log`；直接执行当前函数，非视觉验收|
|继承测试入口|退出 2，收集期 2 个 ImportError|`baseline.log`；本轮没有产生 219 passed / 1 failed 的执行结果|
|迁移检查|退出 1：Changed: backend/tests/conftest.py|`migration.log`；不能写成“通过，只是有差异”|
|设计包检查|通过，36 文件/158 链接/25 参考 SQL 表等|`pack.log`；验证参考设计，不验证运行业务|
|台账结构|通过，24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED|`ledger.log`；只是原台账状态|
|本地就绪检查|退出 2，NOT READY|`ready.log`|
|文档无参工厂调用|TypeError: missing db_path|`additional.log`|
|旧 DB 证据副本|1 task/7 actions/7 events/1 appointment，缺 evidence/pins/advice 表|`additional.log`|
|随包截图|与 L0 初始截图 SHA256 完全相同|两者摘要 `bba32be81acc0c5f9ea0f3f9ddf6821dfbdd8cc83342e62b56dce658f6a7380c`|

本轮未重跑 card-host 的节点树和截图，也没有把旧报告的原生 UI 观察冒充本轮结果。

## 3. 独立问题清单与修改建议

以下 P1 表示应优先修复的业务正确性/主路径问题，P2 表示局部功能或工程可靠性问题。它与旧报告按交付阻断定义的 P0/P1/P2 不作直接数量比较。置信度除明确标明者外为高。

### N01 [P1] bind_asset 缺少常规授权，未知主体能修改已完成任务

位置：`backend/src/octosense_backend/extended.py:179–231`。

仅在 IN_PROGRESS 部分分支检查角色，其他状态直接更新；COMPLETED/CANCELLED 没有终态禁写。临时库中 ghost 对 DRAFT 绑定返回 200，任务完成后 ghost 改为另一设备仍返回 200。这不是旧报告 R-P0-2 的全局角色查询问题：仅修 core resolver 无法覆盖此入口。

建议：先统一验证可信主体、项目成员及任务对象授权，再按业务允许阶段/主体执行绑定；终态拒绝。同步检查 unbind_asset，不能仅防 IN_PROGRESS 承接者。验证 unknown actor、同项目无关报修人、跨项目、终态四组反例，断言任务、版本、事件均不改变。

### N02 [P1] 命令未绑定源状态，SCHEDULED 可被另一技工重新接单

位置：`commands/__init__.py:141–161,221–261`。

`accept_task`/`assign_task` 复用 `_transition(..., ACCEPTED)`，通用状态图允许 SCHEDULED→ACCEPTED（为改派/拒绝预留），却没有限制“接单只能 OPEN”。探针：u-tech-2 接受已由 u-tech-1 确认预约的任务返回 200；任务承接者变 tech-2、状态 ACCEPTED，CONFIRMED 预约仍归 tech-1。重复接受 ACCEPTED 返回 422 的现有行为并不能防住这条路径。

建议：每个命令声明允许的源状态；accept/assign 仅 OPEN，改派只走 reassign 并释放旧预约。补针对 SCHEDULED 的接单/分配测试，验证承接者、预约、事件的一致性。

### N03 [P1] 项目角色修复不够，缺少任务归属和代行边界

位置：`commands/__init__.py:92–99,205–261,326–451`；`appointments.py:35–62,119–145`；`extended.py:499–524`。

探针证实非承接技工可 `/start`（200）；经理可分配到不存在的 `missing-user`（200）。静态上 confirm_draft/cancel/验收没有校验原 reporter，经理被 `_check_actor_role` 全局代行放行；预约确认接受 MANAGER，与基线“P0 不代确认预约”冲突。列表只在调用者主动带 role_filter 时限制可见任务；省略 role 即返回项目所有任务，Web 恰好省略。

建议：把身份、项目角色、任务关系、命令阶段拆成统一授权规则；列表的最小可见范围由服务端主体推导，客户端筛选只能缩小范围。assign 必须验证目标账号同项目有效技工及技能。按需求权限矩阵补反例，不能只补两条跨项目测试。

### N04 [P1] 任意 asset_id 可穿透历史建议的项目隔离

位置：`extended.py:526–556`。

入口只校验当前 task 的项目，然后直接用查询参数 asset_id 查全库历史，不验证设备属于当前项目、当前任务或用户可见范围。探针在 B 项目建立设备及任务，A 项目报修人通过 A 任务的 history-advice?asset_id=b-asset 得到 B 任务历史，HTTP 200。

建议：设备先做项目/可见性验证，历史 SQL 再加 project 和任务可见性限制；不允许用一个可见 task 为任意资源授权。详情、列表、附件、历史建议使用同一对象可见规则。

### N05 [P1] API 字典输入允许绕过版本守卫，缺字段直接 500

位置：`api/__init__.py:100–124,135–180`；`commands/__init__.py:148`。

定义了 Pydantic 请求模型却实际使用 `body: dict`。`expected_version: null` 进入 `_transition` 后跳过版本比较，confirm 返回 200；缺 idempotency_key 返回 500，而非输入错误。错误类型也可流入 `.strip()`/比较表达式。

建议：为每个命令实际挂接强类型请求模型，版本为必填正整数且不可 null；幂等键非空、限制长度；领域层也不接受 None 绕过写命令版本检查。补 null、缺字段、错误类型、旧版本测试；错误输入不得产生业务副作用。

### N06 [P1] 改约拒绝破坏旧预约可执行性，测试把错误写成标准

位置：`appointments.py:149–176`；`commands/__init__.py:285–291`；`tests/octosense_backend/test_appointments_reassign.py:63–76`。

拒绝新提议无条件将 SCHEDULED 改 ACCEPTED，保留旧 CONFIRMED 后仍不能 start（422 ACCEPTED→IN_PROGRESS）。与基线“任务保持 SCHEDULED”冲突。测试却断言 ACCEPTED，台账 T12 expected 也照抄该错误。另外改约冲突查询未排除当前任务，和自己旧预约重叠的新提议直接 409，不能平移/微调已有时段。

建议：有旧确认预约时拒绝新提议保留 SCHEDULED，无旧确认时才回待预约状态；无提议时应拒绝拒绝命令，不能虚构成功事件。改约碰撞查询排除当前任务的被替换预约，并在确认事务中再次检查其他任务冲突。测试必须验证“拒绝改约后仍可按旧预约开工”，不能只查旧行状态。

### N07 [P1] 幂等机制不统一，预约成功后原请求重试 409

位置：`commands/__init__.py:101–112`；`extended.py:106–116,569–590`；`appointments.py:35–239`。

旧报告指出同 key 不同内容被回放，探针确认。补充：预约三个命令没有幂等回放；首次 confirm 200，完全相同 key/version 请求重试 409。record_advice 首次 ghost 写入 200、重试 500。回放缺原 action_id/完整响应，跨命令同 key 也可能被当成成功。

建议：统一命令执行入口，幂等指纹至少含 actor、project、command、task、规范化业务参数；保存原 action_id 和完整结果；合法完全重放在版本检查前返回原结果，不重放业务。不同请求复用 key 必须冲突。审计失败不能写进随后回滚的同一事务；区分尝试审计与成功幂等回执。客户端为一个逻辑动作保留同一 key 至结果确定，单纯每次点击生成随机 key 不能解决丢响应重试。

### N08 [P1] 经理代验收不需要理由，T20 PASS 不成立

位置：`commands/__init__.py:385–403`；`api/__init__.py` accept-finish 路由。

探针以经理调用 accept-finish，不提供理由仍 200/COMPLETED。函数签名没有 reason，无法满足 T20。当前保护“承接者不能自验”是必要条件，但不是完整验收权限。

建议：按当前承接者、原报修人、同项目经理分支检查；经理代验收必须有非空理由并持久化。补多角色自验、非任务报修人、经理缺理由/有理由测试。

### N09 [P1] 完工说明/退回理由只回响应，缺完工轮次身份

位置：`commands/__init__.py:353–425`；`db/__init__.py`；T21。

`completion_text` 只出现在响应，未写入 task/action/event；探针跨这些表检索唯一完工文本，结果为 false。退回 reason 和取消/分配 reason 也没有通过这些命令落入事件/回执，重开详情无法复原业务依据。没有 completion_id 或完工轮次模型，二次完工无法关联一次具体完工与一次验收。

建议：每次完工建立可持久引用的 completion_id，保存文本、提交主体、证据集合和轮次；验收/退回引用对应轮次并保存理由。可采用明确版本化事件模型，不必仅为对齐旧表数照搬所有表。验证重开回读及两轮完工的独立身份，T21 不应仅凭状态退回成功判 PASS。

### N10 [P1] 原生业务与后端是两套事实，修 TASKS 落盘仍不足交付

位置：`app/bundle/main.splash:15–150`；`app/bundle/manifest.json`。

原生对内存 TASKS 直接改状态；没有调用后端，也无版本/幂等/主体/预约确认守卫。save/load 只处理 STATE/EVENT_LOG，任务未持久化；事件 at 恒为 0 且无 task_id。原生能在无确认事实时开工、无附件时完工、无独立主体检查时验收。

建议：先冻结 G0 唯一事实源和受支持宿主调用路线，再让原生动作经统一命令边界；无合法路线应记录阻断。修 TASKS 保存、UUID、布局只能改善演示，不能证明 T28 原生操作与权威任务一致。纯读源码可确认上述事实；旧报告精确节点缺失原因本轮未复跑。

### N11 [P1] Web 确认预约缺入口；旧报告“一行替换”会破坏开工按钮

位置：`app/demo-web/static/workbench.html:192–205,223`。

本轮执行实际 renderActions：只有 PROPOSED 时 reporter 只有取消；CONFIRMED 时却显示再次确认。confAppt 同时被技工开工按钮使用，不能整体改成查 PROPOSED。

建议：明确分开 proposedAppt 和 confirmedAppt；确认/拒绝提议绑定 proposed ID，开工判断 confirmed ID。测试首次提议、确认后、改约两条预约并存、拒绝改约四态三角色动作。完成 UI 修复仍需修 N06 等后端问题，不等于完整 T12 通过。

### N12 [P2] Web 隔离证据按钮没有对应分发分支

位置：`workbench.html:244–247,306–319`。

按钮生成 kind=quarantine，但 act switch 无此分支；函数探针记录 API path=null（实际变量 undefined），并非发往证据隔离接口。

建议：补完整 `/tasks/{tid}/evidence/{eid}/quarantine` 路由映射和请求字段；未知 kind 显式报错，不能继续 fetch(undefined)。验证隔离后服务端状态、下载拒绝和完工守卫。

### N13 [P2] 隔离不存在的证据仍报告成功

位置：`extended.py:371–397`。

UPDATE 后没有检查目标存在或 rowcount，missing evidence ID 返回 200/QUARANTINED，并生成成功 action。任务不变但回执声称成功。

建议：先验证证据归属于目标任务，再更新并检查受影响行数；不存在返回 404，跨任务目标不泄漏信息。状态变动应有可回读事件，定义是否提升 task version。

### N14 [P2] 代理异常处理和文件传输不保真

位置：`app/demo-web/server.py:51–60`。

使用不存在的 `httpx.ConnectRefused`；注入真实 httpx.ConnectError 后返回 500，设计的 BACKEND_DOWN/503 不会按预期执行。非 JSON 返回统一包装 `{_raw:r.text}`，附件字节、Content-Type/Disposition 丢失（静态确定，未跑二进制下载探针）。

建议：捕获 httpx.ConnectError/TimeoutException 并映射稳定错误；附件透传原始 bytes、状态和允许的响应头，必要时流式传输。分别验证后端停机、超时、JSON 错误、二进制附件摘要一致。

### N15 [P1] 文档启动命令不成立，旧报告复跑命令也有同样问题

位置：`api/__init__.py:77`；`app/README.md` 启动段；`REVIEW_2026-10-02.md:322–324`；SUBMISSION 启动段。

文档让 uvicorn 调 `make_app --factory` 并设置 OCTOSENSE_DB，但工厂必须传 db_path，且没有读取该环境变量。无参调用实测 TypeError。`OCTOSENSE_PORT` 也不能自动改写写死在 CLI 中的端口。

建议：提供实际存在的零参配置工厂或显式启动器，配置经统一入口解析；用临时 DB 验证文档原样命令启动、health、建任务、退出、重启回读。不可用“我以前起过服务”代替当前说明可复现。

### N16 [P2] 死代码安装器真正失败方式与旧报告不同

位置：`extended.py:595–599`；`db/__init__.py:215–229`。

install_extended_schema 在 tx 中 executescript，实测退出时 cannot rollback - no transaction is active（提交错误被回滚错误覆盖）。旧报告说“调用即 foreign key mismatch”不准确：函数先 init_schema，repair_pins 已由正确当前表定义创建，EXTRA_SCHEMA 的 CREATE IF NOT EXISTS 不会覆盖它；探针随后可插 pin。错误 FK 文本仍是潜在维护隐患。

建议：统一 schema 定义并显式版本迁移；不要在当前 tx 包装中执行会结束事务的脚本；回滚不能覆盖原始错误。此函数当前未接入应用，不把它计为正常请求路径必现故障。

## 4. 对旧报告全部 21 项的逐项裁决

|旧编号|当前裁决|补充/修改建议|
|---|---|---|
|R-P0-1 原生节点缺失|历史运行现象待本轮复跑，静态可见布局风险|`/d` 未列出不能单凭此证明“节点被丢弃而非裁剪”；查布局/节点枚举机制再定根因。修布局仍需 N10|
|R-P0-2 跨项目写|复现成立|修 project resolver 只是第一步，还需 N01/N03/N04|
|R-P0-3 详情无权限|ghost 读取 200，成立|统一详情/列表/事件/附件/历史可见性；不能只验证账号存在|
|R-P0-4 幂等内容冲突|复现成立|补 N07；旧行 NULL hash 不能静默放行无法确认的重试，需迁移/过渡策略|
|R-P0-5 Web 预约死锁|函数级复现成立|不能一行替换共享 confAppt；见 N11|
|R-P0-6 grant 缺失|静态成立，为未实现能力|本地调试身份是已知边界，不等于达到正式身份验收；不得为了消除 FAIL 改成没有依据的 PASS|
|R-P1-1 原生任务不落盘|静态成立|events.jsonl 当前全局事件没有 task_id，旧报告“日志两条记录指向同 task_id”表述不准确；ID 重用风险仍成立|
|R-P1-2 技工乙项目字符串|静态成立|用明确项目选择/项目数组及 URLSearchParams；同时修列表授权，不能靠拼接字符串|
|R-P1-3 advice 权限/幂等|ghost 首次 200、重试 500，成立|与 N07 一起放入统一命令边界|
|R-P1-4 task 页面不存在|HTTP 500 复现成立|补页面或改到确实存在的任务入口|
|R-P1-5 毫秒幂等键|风险成立，未观察真实人工同毫秒撞键|更重要的是同一逻辑重试保留 key；每次随机新建仍不满足响应丢失语义|
|R-P1-6 DOM 取版本|静态成立，旧报告情景非全都实测|版本与 task_id 放同一状态对象，异步响应校验任务是否仍选中；缺失禁止动作|
|R-P1-7 CWD 附件根|路径依赖成立，但原因描述需修正|uvicorn `--app-dir` 添加导入路径，不改变 cwd；不能将参数本身说成改目录。统一运行数据配置，避免静默猜路径|
|R-P1-8 原生权限/反馈|静态成立|仅隐藏按钮不足，执行边界必须拒绝；见 N10|
|R-P2-1 契约与实现脱节|成立|本地 schema/OpenAPI 是项目设计参考，不应称“官方 schema”。版本差异需记录；不能以回写当前弱实现取消原验收要求|
|R-P2-2 数字口径|部分已在旧报告后同步|README 已写 12表/27命令/29路由；`__version__` 仍 0.1.0、candidate 仍 11表/25命令。读接口不宜全部称业务命令|
|R-P2-3 BLOCKED 归属|当前顶层摘要已同步为 P06/P07/P08|不能把旧矛盾全部作为当前未修复项；历史条目需保留时间标签|
|R-P2-4 证据空心|旧 DB 缺表/截图一致实核成立|更严重的是 T12/T20 的错误期望及 T21/T28 证据不覆盖；见下节|
|R-P2-5 版本漂移|源码未绑定不可变候选问题成立，历史 mtime 结论不重新背书|mtime 可被复制改动，不能替代内容版本；应绑定源码 hash/包 digest/测试运行身份|
|R-P2-6 继承测试失败|收集期两错复现成立|本轮未证明旧报告 219/1 分项结果；避免 `from conftest import`，显式测试 helper 模块优于简单移动到另一个 conftest|
|R-P2-7 结构/色值/死schema|多项独立问题，不应混为一个缺陷|缺交付结构、颜色不符、对比度未测需分别验证；安装器真实错误见 N16。用户要求保留来源，不建议直接删历史产物|

此外，VERIFICATION 写迁移检查“通过，仅一处修改”，本轮实测退出码为 1；应明确“检测到已记录差异”，不能写 PASS。设计包 25 表约束测试通过不能证明当前 12 表执行器正确。

## 5. 台账建议（本轮未修改）

|项|当前|建议|依据|
|---|---|---|---|
|T12|PASS|FAIL|拒绝改约后原预约无法开工；测试/expected 写错|
|T20|PASS|FAIL|经理代验收无理由仍成功|
|T21|PASS|FAIL|无新 completion_id；完工文本、退回原因未形成可回读轮次记录|
|T28|PASS|撤销 PASS，按实现缺陷记 FAIL|原生未接同一事实源，TASKS 未保存；已有证据是 Python 文件/DB，不覆盖原生重开|
|T15|PASS|补负向验证并撤销无条件 PASS|写版本可通过 null 跳过；UI 恢复规则也未完整验证|
|T14|PASS|NOT_RUN 或按覆盖拆子项|现有证据不足证明时区换算及自然语言具体日期确认；不能以 end>start 单项代替|
|T07/T09/T10/T19/T30/T31|PASS|逐条重新核验完整范围|设备授权、预约主体、附件对象可见性、取消状态/主体规则均存在缺口；不以本报告直接猜全部改判结果|
|G0-A/G0-C/P01–P05|PASS|检查冻结候选与证据是否同版|未复跑原生和 Hub，不在本轮直接改判，但旧截图与当前代码不一致|

即使只撤销 T12/T20/T21/T28 四条 PASS，24 项也只剩 **最多 20 项待继续复核的原 PASS**；这不是宣布“20 项已经可信”。不要在没有逐项证据时生成一张新的总通过率。

## 6. 修复顺序和验收方法

1. **先锁定事实源和授权边界。** 写 route-decision 明确后端/宿主职责、真实主体来源及原生接入条件；做 N01–N05/N08 的权限矩阵与命令源状态修复。先用反例阻止未知主体写、SCHEDULED 抢单、非承接者开工、null 绕版本。
2. **统一幂等、回执、审计和完工轮次。** 同一逻辑动作重试回原 action_id；不同请求同 key 拒绝；理由/文本/证据关联重开可读；任何失败不能留下部分任务事实。schema 迁移保留旧数据并明确版本。
3. **修预约领域规则。** 首次确认、改约重叠、拒绝改约、确认重试、取消与改派释放预约一起验证，不能只修 Web 按钮。
4. **修 Web 主路径与失败路径。** proposed/confirmed 分离、隔离 dispatch、技工乙项目选择、请求状态/版本、代理停机和二进制下载、缺失页面。实际三角色完整成功链和退回链分别跑。
5. **原生接统一执行边界后再做布局和重开。** 使用同一 task_id 从原生操作后回读权威库，再关开验证；不能只检 STATE 中的成功提示。
6. **恢复测试/冻结交付。** 修公共 helper 导入、按文档从临时环境启动；用源码哈希、bundle digest、对应日志/截图绑定候选。最后重核 T01–T38/U01–U12；真实模型、宿主和发布回执保持独立门槛。

不认可旧报告“补两个权限测试”“一行修好 Web 即解锁完整链”“按小时估计即可交付”的确定性。这些属于跨模块边界修复，完成时间取决于 G0 接入和领域规则收敛；当前没有足够证据给出可靠小时数。

## 7. 复现入口

在项目根运行（不启动对外服务、不使用运行 DB）：

```sh
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/review-independent-20261002/probe.py
node runtime/review-independent-20261002/frontend-probe.cjs
PYTHONDONTWRITEBYTECODE=1 OCTOSENSE_EVIDENCE_ROOT=/tmp/octosense-review-evidence backend/.venv/bin/python -m pytest backend/tests/octosense_backend -q -p no:cacheprovider
python3 scripts/check_build_loop.py --ready
python3 scripts/verify_migration.py
backend/.venv/bin/python scripts/test_baseline.py
```

probe 是记录反例的诊断程序，不是把错误行为作为期望的产品测试。修复后应将预期改为基线要求，并建立正式回归断言。Frontend 探针对网络做替身，仅验证渲染/分发逻辑；不把它算浏览器 E2E。
