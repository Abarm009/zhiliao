# 2026-10-02 修复后独立验收

**结论：部分修复有效，整体修复验收不通过。置信度高。** 51 项单测和修复者的 22 项探针确实通过，但没有覆盖若干实际剩余缺陷；原生候选包不能通过当前 Hub 检查，临时副本打戳后仍出现脚本解析错误。本轮不修改业务代码或验收台账。

## 一、执行范围与证据

本轮读取当前修复报告与当前代码，运行现有测试、修复者探针、继承基线、设计/迁移/台账检查，并独立编写新探针，逐步断言业务前置步骤成功。新增探针使用独立临时DB/文件与注入时钟，不连接现有业务服务。构造同项目第二报修人的角色仅用于测试权限矩阵，不改运行数据库。

对原始 app/bundle 执行只读 hub check；复制 bundle 到本轮 runtime 后，单独启动已有 card-host，--stamp 只修改临时副本，运行结束关闭本轮进程，不改原 manifest。未做原生点击与视觉验收：脚本解析已经失败。未调用真实模型、外部发布或发消息。

证据目录：`runtime/repair-verification-20261002/`。

|检查|本轮结果|证据|
|---|---|---|
|新后端测试|51 passed in 0.25s|pytest.log|
|修复者 probe_after.py|22 pass / 0 fail|reported-probe.log；脚本自身也会重新生成 repair-20261002/probe-after.json|
|独立新增反例|24 条观察，包含已修复对照和剩余失败|independent_probe.py / independent.json|
|继承基线|退出2，两个测试模块因 stream_of 导入失败无法收集|baseline.log|
|迁移检查|退出1，Changed: backend/tests/conftest.py|migration.log|
|设计包检查|通过，证明设计与参考SQL检查，非运行应用正确|pack.log|
|本地就绪检查|退出2，NOT READY，24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED|ready.log|
|原包 hub check|REFUSED，bundle digest 与 manifest 不一致|hub-check.log|
|临时副本打戳后启动原生|admitted，但多处 parser error，最终 SPLASH eval view=false|native/host.log|

不运行修复报告所给的原 e2e shell 命令：它忽略传入 OCTOSENSE_BASE_URL，仍访问固定8713，可能打到其他现有实例，不能用于证明宣称的8722独立测试库。独立 API 探针使用临时库，避免此风险。

## 二、已核实有效的改进

- 跨项目 create 返回403；ghost 读取任务返回401。
- null expected_version 返回422，缺字段不再直接500（但严格类型仍不完整，见V10）。
- SCHEDULED 不能用 reject-finish 绕到 IN_PROGRESS，原状态保留。
- 首次预约提议保持 ACCEPTED；经理不能替报修人确认；报修人不能取消已承接阶段任务（现有探针的取消铺垫因而发生变化）。
- 提前开工被422拒绝，开工已有设备非空和确认预约时间窗口检查。
- 经理无理由代验收返回422。
- 完工文本、completion_id 和 round 已持久化；本轮核实两个轮次能回读不同ID/文本。
- 拒绝非重叠改约保持 SCHEDULED 的修复者探针通过；同请求预约重试可返回200（回执仍不完整）。
- 零参 make_app 可构造，但默认数据目录锚错一层，见V10。

以上改进不能推出“所有R/N/Q已修复”，也不能替代Web/原生/真实模型验收。

## 三、剩余可操作问题（按影响排序）

### V01 [P1] 原生交付件被拒绝，打戳后脚本仍无法正常求值

位置：`app/bundle/manifest.json`；`app/bundle/main.splash:87` 起；`main.splash:329`。

原包实际摘要 `61f795d8dcc75b3089485423b5ff7a12d34ee3b9e4f94053c7985b7dfdc324f3`，manifest 仍声明 `c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`，Hub REFUSED。临时副本重新打戳后准入，但当前 card-host 在87/89/92等行报 `Argument type expected in function` / `Parser stuck on character Operator(:)`；后续有330行 `pop_stack_resolved on empty stack`，最终 `view=false`。进程退出0不等于应用求值成功。

建议：使用固定宿主支持的语法修复，先让完整脚本无解析/求值错误，再实际点击、回读、重开；最终重新生成包摘要、check/scan、截图。优先核查动作对象中 `fn:` 与视图内表达式，而不是只改manifest摘要。

此外 allowedActions 仅被定义，视图仍硬编码显示所有动作；原生 propose 仍直接 SCHEDULED，没有 confirmAppointment 实现；仍是独立TASKS而非统一权威。保存tasks.json并不等于完成原生业务接入。

### V02 [P1] 列表权限可由 role=MANAGER 绕过，详情仍泄露他人联系方式

位置：`backend/src/octosense_backend/extended.py:596–616`；`api/__init__.py:544–562`。

同项目另一 REPORTER 默认列表看不到某任务，加 role=MANAGER 后返回该任务（200）。详情只验证项目成员，第二报修人可直接读取任务及 `private-contact`。客户端过滤值仍在决定服务端授权范围，N03/T18没有完整修复。

建议：由已认证主体推导可见集合，再与客户端筛选取交集；详情/事件/附件/收藏/历史保持同一对象可见性与字段脱敏策略。默认 X-Actor-Id 仍可伪造注册用户，不是身份认证完成。

### V03 [P1] 新列表过滤让技工看不到 OPEN 待接单，Web主链卡在接单前

位置：`extended.py:601–614`；Web loadList 调用默认列表。

技工默认被限制 `assignee_id=actor`，所有未分配 OPEN 任务均不返回。本轮创建可见项目的 OPEN 任务后，用本项目技工列任务返回200但任务缺失。原来“能看到太多”变成“待接单消失”，技术上有接单API也不能证明用户入口可用。

建议：允许本人承接任务及本项目技能匹配 OPEN 的并集；接单前脱敏。补真实浏览器报修人提交→技工刷新发现→接单验证。

### V04 [P1] 维修中换设备的角色守卫被削弱

位置：`extended.py:106–115,219–221`。

`bind_asset(IN_PROGRESS)` 调 `_check_role(..., {'MANAGER'})`，但该 helper 只判断项目成员存在，完全不检查 allowed。无关技工乙对技工甲维修中的任务换绑另一设备返回200，asset_id实际改变。经理换设备理由也未被参数/接口接收验证。

建议：统一角色/对象/阶段校验，IN_PROGRESS必须同项目经理、理由非空且旧/新值留痕；当前承接者和其他项目成员都应拒绝。不能只测 ghost 被拒绝就判 N01 完成。

### V05 [P1] 幂等仍串命令，冲突分支出现 NameError/500，原响应不完整

位置：`extended.py:76–92,476–510`；`appointments.py:60–77`；`commands/__init__.py:160–187`。

- pin 和 unpin 的指纹都仅 `{task_id}`。同key先pin后unpin，两次200，第二次返回 add_pin 回放，收藏仍在。
- extended 与 appointments 使用 IdempotencyConflict 却未导入。同key改变 advice payload，或预约确认时改 expected_version，实测返回500，未达应有409。
- 首次确认响应有 appointment_id/status/task_version，但没有 action_id；重放仅返回task_id/command/action_id，丢失原结果。还未实现完整一致回执。
- 回放发生在对象授权前，NULL历史hash继续跳过比较，仍需迁移和撤销授权语义。

建议：公共执行边界统一认证、对象访问、命令级指纹及原结果存储；指纹必须包含command，补异常导入；原请求回放返回原action_id和完整结果，其他请求同key一律冲突。

### V06 [P1] 改约仍与自己的旧预约冲突；过期预约仍可确认

位置：`commands/__init__.py:402–409`；`appointments.py:130–140`。

原确认预约平移1秒的新提议被409拒绝，因为没有排除本任务将被替换的旧预约。确认路径虽有“排除将被替换”注释，实际排除的是新proposal ID，旧确认预约仍参与冲突。已结束一小时的预约可提议且可确认200，缺有效期/时间窗口规则。

建议：提议与确认分别遵循基线；确认事务排除同任务被替换的预约，仅与其他任务竞争；预约生命周期统一可注入时钟，过期确认410，客户端不能伪造当前时间。修复者只测不重叠改约，不能证明完整T12。

### V07 [P1] Q06没有修复：合法 asset:<asset_id> 依然404

位置：`extended.py:140–151`；`runtime/build-loop/repair-20261002/probe_after.py:373–382`。

实际：AC-001→200；asset:as-a-1→404；asset:AC-001→200。修复者探针把最后一种错误载荷当成正确验收，因此“Q06已通过”不成立。

建议：普通码按asset_code，asset:载荷按稳定asset_id，再做项目/归档/授权检查。先纠正用例，不能把错误协议改写成基线。

### V08 [P1] 完工只看READY数据库行，附件实际缺失也能提交

位置：`commands/__init__.py:511–523`。

本轮在临时目录上传附件成功后删除对应临时文件，任务仍能完工提交200。文件缺失时READY元数据不能充当合法可下载证据。当前返回的完工轮次记录有所改善，但未覆盖附件完整性守卫。

建议：定义证据已提交/可读/完整性的验证与失效状态，完工前确认本任务附件实际存在且摘要正确；缺失/损坏拒绝并给恢复入口，验证不会留半条完工记录。

### V09 [P1] 业务权限和提交条件尚有漏洞

位置：`commands/__init__.py:309–351`；权限需求矩阵。

经理没有 TECHNICIAN 角色仍能自主 accept，200后assignee=u-manager（默认allow_manager=True）。无服务空间的草稿仍能确认到OPEN。技能匹配和有效服务关系尚未实现，不能由项目角色或设备同项目代替。

建议：自主接单禁止经理角色隐式代行；各命令分别声明代行规则。确认草稿前补足位置/空间/联系人校验；不通过时保留草稿；设备服务关系与技能独立落地。

### V10 [P2] 类型与默认路径修复不完整

位置：`api/__init__.py:72,111`。

expected_version=true 被Pydantic转换为1，提交返回200；领域 `isinstance(True,int)` 也通过。`_PROJECT_ROOT=parents[3]` 对 api/__init__.py 实际是工程/backend，默认数据库与附件落 backend/runtime，与文档 root/runtime 不符。

建议：StrictInt/严格字段验证并在领域拒绝bool；统一从明确项目根或配置解析所有运行目录，补无环境变量/不同cwd启动测试。不要直接迁移未知旧库，先确定实际路径与备份。

### V11 [P1] 测试及交付记录有假阳性，不能支持“覆盖全部”

位置：`probe_after.py:357–382,408–419`；`backend/scripts/e2e_full_chain.sh:7–12`；`REPAIR_RESULT_2026-10-02.md`。

- Q05试图由报修人取消ACCEPTED任务，但修复后该动作应403；脚本没有断言取消成功，继续用错误version拒绝预约，只要409/422就标“CANCELLED测试通过”。实际未制造CANCELLED。
- Q06用错误载荷，详见V07。
- probe_after 即使存在 failed 记录也不设置失败退出码，只打印统计，不适合作为自动验收门。
- 原E2E仍固定8713、固定幂等键，未读取修复报告传入的8722 BASE_URL；curl未以HTTP失败退出，关键步骤缺最终断言。按照脚本所提一小时后预约立即开工也会被新时间守卫拒绝。
- 继承测试仍2个收集错误；迁移检查退出1却写“通过，仅旧差异”。
- 报告说T17/T29已NOT_RUN，实际台账两项仍FAIL；candidate仍0.2.0/11表25命令，API已0.3.0。
- 报告把--ready失败部分归因P06/P07/P08外部递交，检查器实际本地未过清单不含这些外部项。SSE、提醒作业等本地工作仍未做，不能统一归因等用户授权。

建议：先纠正验收脚本，逐步断言铺垫与目标状态；失败必须非零。端到端独立端口/库和合法时间，断言完成轮次、回执、附件、预约与失败分支；修复导入后重跑继承测试；台账与冻结内容版本同步，不能用旧PASS或源码diff代替运行证据。

## 四、未完成范围的裁决

真实模型、宿主会话/grant、配对、SSE、持久化提醒、设备服务关系、技能、旧入口统一边界及完整UI验收并未完成。真实账号/首次同意可能是外部阻断；SSE、jobs、测试修复和本地业务守卫则有独立可执行工作，不需要全部等用户回来才能推进。

51/51与22/22是这些特定脚本的实际结果，不是完整T01–T38/U01–U12覆盖率。建议下一轮首先修V01–V05及V11（交付件、权限、主路径、幂等、假阳性），再按原修复指令补齐其余范围。

本轮只新增验收报告、诊断程序和运行证据；没有修复产品代码。现有probe执行会更新它自己指定的probe-after.json，本轮完整输出另存reported-probe.log，避免与历史结果混淆。所有临时故障注入仅在临时数据库/临时附件。
