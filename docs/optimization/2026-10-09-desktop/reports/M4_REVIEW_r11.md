# M4 独立 Review r11

**最终结论：FAIL。候选 M4-r9-worktree。** 九场独立原生冷启动均 CLEAN，实际加载冻结候选，业务解析/运行错误为0；合法任务盘加载、坏盘分类与备份保全、三种旧锁启动处理通过。r10 的 B-M4-01 合法盘误拒子项已关闭。但 **D-M4-03 原子命令边界仍为 P1**；真实 M3 创建→接单→设备→预约→开工、三角色与真正业务并发没有成功证据。不能放行，不执行下一模块。

## 审查对象、环境与范围

- 审查者/日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai；两段式 review_r1_0002，无子代理，无业务代码修改。主会话 Router/指定 gpt-6.1-sol 与线程 createdAt/标题接口不可核验，未冒称切换或命名完成。
- candidate_id/base：**M4-r9-worktree / M4-r8-worktree**。作者报告 `M4_IMPLEMENTATION_r9.md`、候选清单 `runtime/optimization/2026-10-09/M4/r9/CANDIDATE.json`；由用户交接 build_r1_0002_REQUEST_build_r9、请求、报告及 GATES 作者字段相互定位，没有按 mtime 选版本。
- HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty；冻结 main **657584 B / SHA256 c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421**。源码、作者 staged 源与审查冻结源相同。r8→r9 包含其它模块及 UI 重设计共享变化；作者本轮自身 bundle hunks=0，不把共享修改全归为 M4 新增。
- bundle digest **77b95f2eb1ecc5c97cc109e46cda7ccbb3276ac52f99b4f840cad8150d1adf6b**；复用隔离 signed catalog/installed bundle，anchor **966929104434039f8034ffccada5eae1ab020c05518dab24dbc695f9626c6a0b**。运输 manifest 的 integrity/signature 与未签名工作树 manifest 区分，未声称两者字节相同。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness **226df8dd61409cb0c82a7e70a931c2637362445d8a4a9e5232254da29188d11a**；profile模板 **80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7**。
- 前置 **M3=FAIL / M3-r9-worktree / M3_REVIEW_r12.md**，与本轮同一源码摘要；M2仍FAIL。没有已接受的M3 PASS。按用户前序挂账裁决继续本模块局部复核，不把挂账等同前置通过，不改前序门禁。
- 请求 R SHA256 **a6f348487dd6f52111768f013f48a02920fc43fed9b17311c2ef3e6bebdbce6f**；驱动沙箱外执行 **03:15:54–03:18:33 +08:00**，两个batch，9/9 CLEAN、quit_http/rc0，无 ABORT；各场实际墙钟 **16.24–16.29秒**。审查方未自行启动宿主/harness，也未做 sandbox-exec/pgrep 预检。
- 开始/结束保护：门禁写入前14项保护输入及189项seed/mirror文件一致；门禁变更单列保存前态，保留历史。源码与原台账不改。
- 已读范围：第1段实际 AGENTS、CONTEXT、00/01/02/M4/04、根基线相关部分、r10缺陷、r9作者交接/差异/证据/复现、M3 r12及19项T/U；第2段全量summary/result/profile/probes/log/denials/MANIFEST、事实盘及18张PNG摘要，目视全部3种不同图像内容。只查旧B01/D03/D04与相关回归，没有无关扩审。
- 实际审计命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/native/review_r1_0002/audit_phase2.py`。最终rc0，**8068项证据/盘面一致性检查，0失败；不是8068个业务用例PASS**。
- 未运行：可信登录后现场输入与三角色首屏、接单/设备/预约/改派/改约/取消/开工命令，命令提交点故障与同盘重开，真正双原生上下文业务并发，AI迟到/撤销/新绑定动态。合成DRAFT仅用于加载，不当作M3创建工单；没有注入SESSION或手改运行数据跳预约。
- 模型：全部 needs_model=false；model_proxy/model_proxy_stats字段均不存在，宿主env无MM_KEY/OCTOSENSE_MODEL_ENDPOINT。本次真实MiniMax调用**0**，无实测402/余额不足/欠费；没有读密钥/真实明文凭据。公开发布、push、issue/评论、消息、公网部署均未执行。新离线私钥0，作者keys目录仍空，删除来源记录保留。
- 第1段一次项目外记忆索引读取已在阶段笔记披露，没有作为本轮候选/测试证据；本第2段读写均限项目内。

**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r1_0002_REQUEST_review_r1_0002/`；**E/**=`runtime/optimization/2026-10-09/M4/native/review_r1_0002/`；**A**=E/native-evidence-audit-r11.json；**V**=E/visual-observations-r11.json；**N**=`M4/native/REVIEW_NOTES_r1_0002.md`；**R**=`M4/native/REQUEST_review_r1_0002.json`。短路径相对 `runtime/optimization/2026-10-09/`。源码行号指E/source.main.splash，与本轮受审源相同。

置信度：冻结内容、盘面、日志、隔离回收记录、当前文件协议原子缺口 **高**；未执行真实业务/身份命令/模型/并发效果 **未知**。Python协议反例不冒称原生业务实证。

## 必需检查

|检查|独立步骤/期望|实际|判定及证据|
|---|---|---|---|
|候选/宿主/运输/运行一致|重算请求、保护输入、各场mirror/installed/.running资源|9场均唯一运行本包，14个运行资源逐场一致；657584 B eval view=true|PASS限定版本一致性，A|
|冷启动解析/渲染|零parser/业务运行错误，原生根可见|9场零[E]/panic，tick_exception_count=0；完整登录页可见|PASS冷开/登录页；登录后工作台NOT_RUN，A/V|
|合法任务盘加载|空白空盘/完整中文任务正常，不误pending|empty_crlf/unicode_task_load均pending=false，无新recover，原盘不动|PASS，B01的r10误拒子项关闭，A/H|
|坏盘分类/保全|第2成员缺字段/未知状态准确拒；截断保主与旧备份|why准确；tasks不动，recover/corrupt.latest逐字匹配|PASS冷开子项；实际普通命令拒写/显式恢复NOT_RUN|
|旧锁启动恢复|future/unknown保留、stale回收、进程token空|三锁均符合盘面期望，正常盘无误pending|PASS限boot；不代预约过期或原子提交|
|硬1权限/设备关系|资格/越权/伪造拒，合法服务关系可绑定|没有可信主体或实际绑定命令|NOT_RUN；登录输入通道BLOCKED|
|硬2预约规则|提议不直升、合规确认、跨项目冲突/时区/过期/改约拒绝|没有实际预约提议/确认命令|NOT_RUN；不拿stale锁代提议过期|
|硬3真正并发|同Store两上下文接单/重叠确认唯一成功，相邻正常|非原子read/write/read及检查→写窗口仍在；独立文件协议反例成立|FAIL源P1 D03；原生同步调度BLOCKED|
|硬4开工与旧授权|无设备/有效预约不足拒；改派旧技工拒|没有开工或改派命令|NOT_RUN|
|硬5三角色表单/事实/回执|真实输入、负责人/预约/阶段与权威一致|只有未认证登录页，actions/events仍空|NOT_RUN，不拿截图/状态码代主链|
|旧确认/AI撤销|改派/改约旧绑定失效、新编辑再绑定、迟到回复拒|五源码段未变，新增确认分支未回退epoch段|SOURCE-CLOSED限定反例保持；动态NOT_RUN/交错BLOCKED|
|隔离与回收|profile/probes、预后进程、退出组与外写记录|9/9符合指定隔离/回收字段|PASS记录范围，A；不等于业务PASS|

### 九场权威结果

|场景|独立权威结果|结论|
|---|---|---|
|cold_no_tasks|原无tasks，结束仍无tasks/lock/recover；pending=false；actions/events空|PASS冷开无任务子项；没有M3工单|
|empty_crlf|9 B CRLF/Tab空数组逐字保留；pending=false，无recover|PASS合法空盘加载|
|unicode_task_load|353 B中文/引号/换行完整DRAFT逐字保留；pending=false，无recover|PASS加载门禁；未认证看不到任务，不能独立证明登录后任务列表投影|
|invalid_second_member|370 B整盘保持；pending=true，why指第2条成员；recover=原文|PASS整份拒收及准确分类|
|truncated_old_backup|339 B截断主盘和353 B旧有效recover均保持；corrupt.latest=339 B原坏源|PASS截断检测及备份保全|
|unknown_stage_closed|363 B主盘保持；pending=true，why指第1条字段/类型/状态非法；recover=原文|PASS成员分类，未误报首尾截断|
|future_foreign_lock|37 B未来外来token原样，当前token空；pending=false|PASS未来锁保持；m2_lock_state为空，不编造owned/held状态|
|unknown_foreign_lock|34 B未知戳锁原样，unknown_kept，当前token空|PASS未知锁保持|
|stale_foreign_lock|stamp=1旧锁变空，released，当前token空；pending=false|PASSboot旧锁回收；不是存活持锁者回收安全性证明|

## 证据核对与限制

1. **MANIFEST.sha256 1474条**全部独立重算，文件集合精确、无遗漏/额外文件/重复项/symlink。summary内嵌请求与R相同，9场summary字段与result一致，host/harness/template摘要一致。
2. 各场profile按模板、run路径、control port逐字重建匹配；probes.apply rc0、write_outside_denied.created=false、五禁读探针拒绝、probes.ok=true。预后pgrep严格为rc1/NONE，无残留组；library_scan为空、驱动记录的真实HOME/.octosense mtime不变。审查者没有去真实HOME另作预检。
3. HOME/app-data/缓存/tmp等12项路径均在各新run内。命令严格匹配R及capture改写。全部seed清单与冻结seed/mirror精确匹配；9场mirror、installed和唯一.running资源一致，运行源确为候选。digest_seen_in_seed=true、digest_seen_in_host_log=false均如实核对；digest marker不是单独的加载证明。
4. 9个最终capture存在、SHA256与result及MANIFEST一致；另9个part PNG也全核，共18张 **2800×1696**，分为3种字节内容（03:16/03:17/03:18，各7/7/4张），已全部逐种目视。均显示完整登录页、账号/口令/登录/清空，未显示三角色任务首屏、预约表单或恢复按钮。不同size请求仍得到相同桌面截图尺寸，不能据`--size`声称多分辨率业务布局/文字放大通过。invalid_second_member的part/final只属两种时钟内容，保留各自摘要，不错误认定截图损坏。
5. `files_written_count`为127或128，均小于400截断阈值；列表唯一、有序、文件存在且在run内。它按mtime列文件，不是127次业务提交或完整内核写审计。tasks/actions/events/合成哈希账号按夹具原字节保持；变化仅所测坏盘备份/旧锁回收及运行状态/缓存等，业务成功事件0。
6. 全部完整host.log的bytes/tail/markers独立重算，业务eval 657584 B/view=true，0[E]/panic，业务tick异常0；809 B另一个系统视图没有混作业务候选。
7. **请求动作缺口已披露**：九份日志都记 `wm: unknown --test-action 'wait:5'`（日志为[I]）；launch-hub和capture实际执行，harness墙钟约16秒。不能宣称宿主内置等待5秒成功；本次冷开最终盘与截图证据仍存在，加载/分类子项不因此作BLOCKED。后续请求应删除未实现的wait，或经验证的内置调度后缀/驱动等待机制控制时机。
8. 首次审计把unknown action与业务错误混合，产生9项预期不匹配，保存在E/native-evidence-audit-r11-first.json。已分为“业务[E]为0”和“wait:5未实现”两个明确事实，最终审计0一致性失败，A仍记录每场request_action_coverage=PARTIAL、unsupported_requested_actions=[wait:5]，**没有隐藏动作未执行或把它写成完整PASS**。
9. 完整sandbox-denials逐份读取并以harness同一解析规则重算摘要匹配，包含被拒443外联、Metal系统缓存和/dev/dtracehelper尝试。被拒尝试不是成功外联/外写；duplicate reports不作精确网络请求次数。本轮没有已证成功违反隔离的行为。
10. needs_model全false，model_proxy_stats实际**不存在**，没有编造requests=0统计字段。真实模型效果未测、无余额错误，因此NEEDS_ABRAM=no。作者旧MiniMax实证不能代本轮原生模型验收。
11. future及stale场运行组各有一个同PGID osascript成员，最终全回收；只记录comm，没有参数/用途。延续r10 A-M4-R10-01来源追溯建议，不凭进程名认定成功额外自动化或安全P1；审查者没有调用osascript/辅助功能。
12. 本轮没有seed view/state；正常任务盘及future场的state.status另出现“state.json损坏/不完整”的恢复说明。这不等于任务盘坏，未当作新的M4缺陷或声称输入恢复通过；M3 r12的独立view恢复FAIL继续保留。冷开截图没有把这些盘内诊断显示为可核的任务恢复出口。

## 上轮缺陷闭合与修复清单

### B-M4-01 — r10合法加载/准确分类/坏盘保全子项 CLOSED；完整可信恢复 NOT_RUN

- 文件：`app/bundle/main.splash:1383–1411`同型首尾校验及成员门禁，`:1348`schema、`:1414`备份保全、`:1452`恢复核身份、`:1587`加载判据。
- 旧触发：合法空数组/完整任务被误判为截断，r10 pending=true。预期合法盘正常，闭合非法成员走准确原因，坏源与旧recover保全。
- 实际：本轮empty_crlf/unicode_task_load及三锁合法空盘均pending=false且无新recover；invalid_second_member准确指第2条、unknown_stage准确走成员门禁；截断原盘/旧备份保持。该旧失败已被独立原生证据推翻，不再要求重修括号比较。
- 根因修复与证据：码点元素改为同型`"[".to_chars()[0]`/`"]".to_chars()[0]`，A/H相应state/tasks/备份/log/PNG、E差异支持。
- 保留范围：冷开零错误/完整登录页子项PASS；认证后普通命令禁写、显式恢复确认及可见错误出口仍NOT_RUN（登录输入受限）。没有动态证据则不把整个恢复用户流程签为PASS。当前没有新增源码失败或数据丢失证据，不新增P1。
- 具体建议/验证：保留现有判据/备份/权限守卫；原生可信输入通道可用后补实际写拒与显式恢复、结果回读，不能清任务盘制造成功。

### D-M4-03 — P1 / 必修 / PARTIAL：真跨实例原子边界仍缺失

- **文件与行**：`app/bundle/main.splash:4446`获取，`:4500–4507`普通写后读回，`:4517`释放；`:4860`commitBound，`:4883–4909`owner核、`:4915–4965`版本/冲突核、`:4985`tmp写、`:4995`主盘写、`:5062`放锁；`acceptTask:7920`等事件追加在commit/放锁之后。宿主`runtime/native-build/makepad/widgets/src/splash_storage.rs:242–415`未公开原子获取/CAS/flock原语。
- **闭合子项**：future/unknown/stale的boot结果本轮独立PASS；首次缺锁与读失败区分、提交同owner/版本/冲突复核源码保持。作者r9已交付可执行最小复现，关闭“只有文字方案”的交付缺口；不把这些子项说成原子提交已闭合。
- **触发**：A/B两独立上下文先读空锁；A写owner并核owner/版本后暂停；B基于旧空锁判断覆盖owner并通过同样复核；A先写/readback成功，B随后写/readback成功。另一方案反例：O_EXCL获取A后，模拟TTL回收仍存活且已通过检查的A，B获取后两个迟到写仍可覆盖。
- **实际/预期**：E/independent-lock-counterexample.json的两个真实Python进程均prewrite_checks_passed=true/readback_matches=true，最终version=6/assignee=B，A被覆盖。预期接单与跨项目重叠确认唯一合法成功、相邻均成功，事实/预约/回执/事件无丢更新。**这里实际跑的是文件协议反例，不是原生业务命令；九场native冷开没有实测双成功。**
- **根因/影响**：read/write/read、owner/版本/冲突复核与主写存在检查后插入窗口；全局整盘写可能覆盖另一提交，事件与事实也未在同一原子边界。影响本模块硬验收3核心正确性，继续为旧P1；不是建议项或环境rc71/rc3。
- **方案误判**：作者`m4_r9_atomic_acquire_repro.py:135–149`的part_b只验证获取级A1，未检验其说明中声称关闭的A2；附录仍保留5min回收。独立实际O_EXCL+活持有者回收注入仍产生两次“读回成功”，说明单独create_new不足。没有改系统时间、没有声称真实等了5min或运行了宿主TTL代码。
- **证据**：E/source.main.splash、independent-r10-to-r9.diff、independent_lock_counterexample.py及JSON（原协议PID67184/67185，O_EXCL注入PID67186/67187，四个rc0）；作者复现/附录作为交付来源；H三锁场只支持boot限定子项。
- **具体改法**：构建方/驱动提供可靠原子命令边界及跨实例唯一owner；原子获取之外，保证仍可继续写的旧持有者不会仅靠TTL被剥夺后继续提交。可用宿主持有期OS锁，或宿主原子CAS/事务与fencing；把最新授权、expected_version、跨任务冲突、事实/预约/回执/事件纳入同一可恢复边界。保留现有拒绝守卫，不能用“再读一次owner”或仅O_EXCL成功替代完整证明。审查方不改业务/宿主、不擅自新增服务。
- **验证方式**：两个可信原生上下文同一隔离Store同步接单和重叠预约，各一成功；跨项目重叠拒、相邻均成功；核唯一承接者/预约/成功回执/同action事件及同盘重开。再注入获取读失败、提交丢锁/清空/覆盖、存活锁回收、提交中断；boot三锁不得回归。
- **动态解阻条件**：当前schema逐场复制新Store、每场单宿主顺序执行，无“两个原生上下文共享同盘+提交点同步/暂停”的可执行入口，不能表达上述真正并发与提交点故障。仅该动态部分记BLOCKED，提供调度入口后补独立实跑；现有源码P1仍为FAIL，不因BLOCKED降为建议。

### D-M4-04 — SOURCE-CLOSED限定epoch反例保持；完整动态NOT_RUN

E/source-regression.json：m4_invalidateConfirmation`:4240`、editDraftField`:6395`、editRawText`:6532`、reassign`:10503`、rescheduleAppointmentFromForm`:8317`五段与r10冻结源逐字一致；confirmDraftModelBound`:6852`新增M2/M3原意图对账/outcome消费，独立diff核旧epoch段未回退。失效清epoch`:4283`，重绑仅消费本epoch`:7076–7095`。

旧累计编辑集复活确认的源码反例保持关闭，不要求重写已修段；改派旧技工拒、改约旧确认撤销、迟到AI展示/采纳拒与新绑定恢复仍未执行。受控AI交错的白名单入口不足，动态BLOCKED/NOT_RUN，不能SOURCE-CLOSED代完整PASS。

### 建议与挂账（不据此判FAIL）

- 原A-M4-01/02/03沿用；M3输入恢复P1以M3_REVIEW_r12保留来源，本模块不修。
- **A-M4-R10-01 / P2 / 建议延续**：H/future_foreign_lock/result.json及stale_foreign_lock/result.json有同PGID osascript，无参数/用途记录，最终回收正常。驱动补宿主内置capture的调用来源/参数；不据进程名称推断未授权行为。
- **R-M4-TEST-01 / 审查请求修正，非业务必修**：R.scenarios[*].test_actions中的wait:5不被固定宿主实现，H每份log均有unknown。后续去掉该动作或使用已证实调度机制；本次不宣称五秒内置等待通过。原结果/初次审计记录保留，加载盘证据仍有效。

## 19项既有用例逐条结果

|用例|本轮精确状态与范围|
|---|---|
|T04|BLOCKED真正原生同Store双主体同步接单；D03源P1保持，文件协议反例不代业务验收|
|T05|NOT_RUN技能/项目拒绝、经理分配及经理事件主体；未认证actor=null不是完整权限测试|
|T06|NOT_RUN动态改派/旧预约取消/新承接者/ACCEPTED/旧技工拒；D04源码段保持|
|T07|NOT_RUN编码/asset载荷一致、伪造/跨项目/归档拒|
|T08|NOT_RUN合法服务空间与仅安装位置相同负例|
|T09|NOT_RUN无设备开工/处理中技工换设备拒、经理更正旧新值理由|
|T10|NOT_RUN提议不直升、报修人确认/非报修人拒|
|T11|BLOCKED同Store同步重叠确认；跨项目实际冲突/相邻确认NOT_RUN，D03源P1保持|
|T12|NOT_RUN待改约旧确认有效、新确认替代、拒新保旧；撤销源码保持|
|T13|NOT_RUN提议过期/无timer/假客户端时钟；stale锁boot通过不代此项|
|T14|NOT_RUN真实上海日期/UTC转换、模糊时间核对、end<=start拒；授权内文字输入通道BLOCKED|
|T15|NOT_RUN旧version拒/刷新/防覆盖/任意百分比拒；合法任务盘加载回归PASS仅子项|
|T31|NOT_RUN取消释放预约/保事件/终态只读/关联新任务|
|T35|SOURCE-CLOSED仅epoch反例保持；真实改派改约/迟到AI/新绑定NOT_RUN，交错入口BLOCKED|
|U01|NOT_RUN三可信角色待处理首屏；PASS仅完整未认证登录页|
|U03|NOT_RUN同任务跨三角色事实/动作、承接者不得自验|
|U04|NOT_RUN有效预约与待改约区分、冲突/过期不显示成功|
|U05|NOT_RUN设备安装位置/服务空间/来源选择依据可读|
|U07|NOT_RUN真实重复点击/响应丢失/版本冲突/离线输入恢复；M3 r12恢复FAIL不改判|

原生登录/文字输入缺口：固定宿主内置type/key已由前序实证与schema标明unknown；schema.ui_actions借助System Events，但本次用户仍明确禁止额外osascript/辅助功能/自动化。本次请求按更窄授权只用内置动作，不注入SESSION代成功。故授权白名单内登录键入、后续三角色主链无法完整覆盖，记该通道BLOCKED、相应业务NOT_RUN。没有把Codex沙箱rc71/rc3或普通已执行冷开项当BLOCKED。

## 判定与本模块修复/解阻指令

- **最终结论：FAIL**。唯一继续必修的源码核心缺陷为 **D-M4-03**。B-M4-01的r10合法加载/分类/保源失败已独立关闭，D-M4-04旧epoch源码反例保持；完整业务主链仍缺证，不以CLEAN或建议挂账条件放行。
- 先解决D03原子边界及可继续写的旧持有者回收安全性，提交新可定位候选和可执行原生双上下文/故障调度；保持已通过加载/坏盘/三锁boot回归。不得只补作者Python成功测试而不接入实际宿主边界。
- 补授权内可执行登录/真实输入通道后，从真实M3创建工单沿UI走到开工，核可信角色/服务设备/上海时间/到期/改派改约撤销、错误出口与权威回执；不得预改status/version/预约。M3前置仍FAIL，以原报告挂账，不由本轮替它修复/验收。
- 仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M4 status及审查字段，review_candidate_id=M4-r9-worktree，review_report指本报告；前态保存在E/gates-before-review-r11.json，并把原审查字段追加review_history。作者candidate/base/implementation/build/测试计数与其它模块/外部交付字段保持。
- `docs/build-loop/ACCEPTANCE.json`保持；没有完整19项原生PASS，不把历史后端/作者结果改称本次原生PASS。19项精确状态写GATES.review_acceptance并保留历史来源。
- 不允许下一模块，不提供下一模块入口、不执行下一模块。**NEEDS_ABRAM=no**：离线签名/本地路线/身份/provider已裁决；没有欠费或公开发布需求，剩余为技术实现/调度与受限输入缺口。

STATUS=FAIL
NEEDS_ABRAM=no
