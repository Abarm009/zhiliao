# M6 独立 Review r1

**最终结论：FAIL。** 当前候选有阻断提醒、授权隔离、收藏版本及历史建议的 P1；真实桌面和模型检查另为 BLOCKED/NOT_RUN。没有以建议项或前置模块 FAIL 判退。

- 审查者 / 日期：Codex 主会话，2026-10-10 Asia/Shanghai；唯一审查方，无子代理。
- candidate_id：`M6-r1-worktree`；base：`M5-r2-worktree`。唯一实施交接为 `reports/M6_IMPLEMENTATION_r1.md` + `M6/r1/CANDIDATE.json`，不按文件修改时间猜版本。
- Git HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作区非干净；不是仅凭 HEAD 审查。
- 主源 SHA-256：`321c9298d73104302eb005487cd7727555266cdfdbc03d0898eab0e24931af1d`，277622 字节；M5 基线 `20bf8800b3b6542f806f6e59a7a360a0df85cb2021fdd6321a65504b6ccfb113`。清单与实读一致；完整差异和快照已保存。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r1.md`。
- 前置：M5 独立 r2 = FAIL，未存在已接受 PASS 候选；按 Abram 本次前序挂账授权继续 M6 首审，保留 M5 原结论，不扩修 D-M5-01～05。
- 宿主：指定 `M0/r3/host/app-extracted/OctoSense.app`，0.1.0-rc.1 / build 20261008.091752；可执行文件 SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮未启动。Store 探针与真实 launcher 分开验收。
- 路由：可确认本轮使用当前 Codex 主会话；工具不能确认实际 Router/provider，也没有可用 createdAt/标题接口，未声称切换模型或完成改名。
- 已读：先读 AGENTS.md、CONTEXT_M6.md，再核本轮 00/01/02、M6、04 模板、唯一实施报告/候选/十份证据及汇总、M5 r2 Review/快照；定向查 README/ARCHITECTURE/MIGRATION/VERIFICATION、01_REQUIREMENTS:136、05_IMPLEMENTATION_ACCEPTANCE、09_AGENT_HARNESS、10_UI_UX_SPEC、DESIGN_SPEC 和受影响函数。已有摘要使用后，没有重跑全套历史基线文档或扩审其他模块。
- 运行证据根：`runtime/optimization/2026-10-09/M6/review-r1/`。只新增审查报告/证据，修改 GATES 的 M6 审查字段与 status；没有业务代码改动。
- 置信度：候选/本地 Store/源码反例 **高**；Python 控制流与真实 VM 的等价性 **中**；真实桌面、业务权威回执、模型及可信会话 **未知**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据（相对本轮证据根）|
|---|---|---|---|---|---|
|候选/基线定位|实读四个包文件哈希；比对 M5 快照；保留差异|与交接一致、差异可定位|main.splash 和 M5 基线吻合；快照/差异已存|PASS（定位）|results/candidate-check.json、source-snapshot.splash、M5-r2-to-M6-r1.diff|
|安全运行预检|隔离 HOME、app-data、TMPDIR、缓存；禁止项目隔离根外写和网络；sandbox-exec 执行 true；枚举指定 launcher|隔离有效、能可靠清理本轮进程/窗口|sandbox-exec rc71，sandbox_apply: Operation not permitted；pgrep rc3，Cannot get process list|BLOCKED|results/preflight.json、runtime-metadata.json、isolation.sb|
|当前 digest 本地安装|复制当前包到本轮；离线 keygen/certify/stamp/sign-manifest/catalog；官方 Store::install_staged；重建 Store 后 may_run；篡改/恢复复跑|当前包可安装，篡改拒绝，无公网发布|安装/重建/may_run rc0；篡改 rc1；恢复 rc0；三份安装源码与当前包一致|PASS（Store 路线，不是原生 UI）|results/local-store-validation.json、store-test/|
|私钥删除|签名流程 finally 删除私钥，结束再次列目录|无私钥遗留|anchor.key、working.key 已删除；remaining_key_files=[]|PASS|local-store-validation.json；结束 final-verification.json|
|首次使用三角色|准备原生三角色任务、搜索/收藏/重登/跨项目操作核权威结果|首屏任务、阶段、下一处理人和动作清楚|不能安全启动；没有本候选原生截图或操作证据；不采信作者18项静态断言为三角色运行|BLOCKED|preflight；D-M6-04/05；r1/evidence/whitebox_three_role.json 为作者静态材料|
|提醒到期、去重、撤权|运行当前函数译码，固定时钟，注入撤权可见性；重复及同时间不同任务登记，关闭第一条|到期且有权才展示、ID唯一、关闭准确|未来提醒立即入列；撤权后 banner 含问题全文；同时间三条同ID、关闭第一条实际作用到另一条|FAIL（源码/adapter）；原生 BLOCKED|results/source-probes.json；D-M6-02|
|重启/取消/恢复|核 load/save/取消/改约调用链；检查真实宿主重启条件|正确恢复、不重复触发、已取消旧作业无效，写失败可恢复|load读取数组子项存在，显式失效有效；任务取消无hook；保存异常吞掉。没有真实应用重启证明|FAIL（源码）；重启 BLOCKED|D-M6-01/02；source-probes.json；源码 snapshot|
|撤权后跳回|同 task_id 跳回函数，以 visible=false 测拒绝，再查提醒摘要出口|所有出口都核当前权限|跳回返回false成立；提醒banner不核visible，另一出口仍泄漏|FAIL（隔离）；可信grant运行 BLOCKED|revoked_jump_denied / revoked_banner_no_task_problem|
|历史建议/阶段|比对生产端日志字段与消费端；运行该字段形状；查三条模型链|有设备/历史/占用来源的建议、最新阶段说明；未知/失败人工出口；不直接写业务|日志不产task_id，history永远无法匹配正常记录；阶段是固定状态文字；没有链②③模型调用与依据。无直接业务写的源码子项成立|FAIL（历史核心）；真实模型 NOT_RUN|D-M6-03；source-probes.json；01_REQUIREMENTS:136|
|真实视觉/键盘/失败恢复|本候选三尺寸、150%、长中文、正常/异常截图及交互检查|关键内容可达、主要流程可键盘完成|launcher BLOCKED，全部未运行；未使用 HTML 测量、字号或max_lines推断原生通过|BLOCKED / NOT_RUN|preflight；r1/CANDIDATE host_started=false|
|受影响回归|对比12个函数；当前 confirm/accept新增hook定向查；收藏实际走commit|先前契约不被误改，新hook不破坏核心|10项内容相同；confirmAppointment/acceptCompletion因新增hook变化；confirm formatter错参；收藏继承版本错误|FAIL 新hook/消费契约；其余仅内容比较|results/affected-regression.json、source-probes.json|

独立控制流探针共12项，3项符合预期、9项不符合；不是原生测试通过率。时钟、身份、文件保存和 commitBound 使用明确 adapter，未伪造可信会话或权威回执。译码仅修正审查 harness 的语法/作用域转换，早期 harness 失败及修正说明留于 `results/probe-development.log`，未改 Splash。作者168/168是报告/证据读回，**本轮未复跑作者driver**；其中收藏断言实际检查的是helper存在，提醒脚本模拟函数、还会删除自己的 sandbox，不能用来代替目标运行，也没有覆盖作者历史文件。

### 全部硬验收

|硬验收|本轮结论与边界|
|---|---|
|1 三角色、搜索、收藏、重登、跨项目|FAIL：收藏版本 D04、筛选副作用 D05；三个角色真实流程/重登/搜索 UI BLOCKED，静态可见过滤不能签完整 PASS|
|2 三条真实 AI 链及人工出口|FAIL：新增历史/阶段仅日志元信息与固定文字，D03；三条真实模型链 NOT_RUN，不以离线脚本替代|
|3 提醒恢复/去重/旧作业/跳回|FAIL：D01/02；显式失效及跳回visible拒绝子项成立；原生重启/作业/授权 BLOCKED。仅前台扫描边界已声明，后台 G0-F仍BLOCKED|
|4 桌面视口/放大/键盘|BLOCKED：1440×900、1280×800、980×760、150%及长中文/焦点/实际对比均NOT_RUN；不因未测编造视觉缺陷|
|5 一致输入/选择/滚动/恢复，保留P0/38/12|FAIL 核心筛选/提醒恢复 D02/05；实际UI BLOCKED。原编号和历史台账保留；作者映射错位见A01，不沿用其PASS|

### 既有用例逐项复核

按原用例含义核对。作者 r1 把 T17 当身份重开、T23当三角色、T30当改约、U12当跳回，与原定义不符；本表纠正审查范围，未修改原台账或继承其错误 PASS。

|编号|本轮结论（完整用例与子项分别说明）|
|---|---|
|G0-F|BLOCKED：后台常驻没有运行/实现证明；仅前台扫描亦有D01/02 FAIL。不要求擅自增加后台宿主能力|
|T17|BLOCKED：原定义是SSE断线重连/全量回读且无第二次写；身份标签切换不能代替；实际断线恢复未运行|
|T18|FAIL D02：撤权提醒带出无权任务问题；原生列表/搜索/事件/附件全面授权与可信身份 BLOCKED，M2挂账保留|
|T23|FAIL D01/02：提醒确认hook、ID、时间、任务取消；真实进程重启作业恢复/一份通知/旧作业不误触发BLOCKED|
|T25|NOT_RUN：模型对矛盾/缺失工具数据标未知、恶意原文不改角色、伪造状态不写业务；历史函数不写业务仅源码子项|
|T26|NOT_RUN：真实模型失败与人工继续未运行，不用假模型成功代替|
|T28|BLOCKED：同task_id原生操作/权威读回/重开未运行；Store重建仅安装子项PASS|
|T29|BLOCKED：真实grant退出/到期/关闭及共享授权未运行；跳回visible=false子项拒绝成立，提醒隔离D02仍FAIL|
|T30|FAIL D04：收藏使业务version 4→5；真实重登、跨用户收藏隔离BLOCKED；原可见过滤源码保留|
|T33|NOT_RUN：多自然表达意图泛化未跑真实模型|
|T34|FAIL新增历史接线D03；真实模型缺依据追问、无历史补充、拒绝不存在引用NOT_RUN|
|T35|BLOCKED：真实迟到建议/改派/改约后旧版本拒绝未运行，M3/M4挂账不扩修；M6旧提醒D02另列|
|T36|NOT_RUN：真实/假适配器白名单和内核替换同契约回归未运行；没有新增provider|
|T38|BLOCKED：未形成同模型/提示/数据/宿主固定场景复跑；当前源码/宿主/digest已固定，原合成真值未传给模型|
|U01|BLOCKED三角色首屏/下一处理人；D05筛选副作用源码FAIL|
|U02|BLOCKED真实原话→可改草稿/歧义/模型失败人工继续；保留M3挂账|
|U03|BLOCKED可信三角色同一任务事实/权限/独立验收；M5原P1不修不宣称通过|
|U04|BLOCKED预约/改约/冲突/过期真实UI；D01确认后的提醒hook错参，D02旧预约提醒过早失效|
|U05|BLOCKED安装/服务空间及依据实际可读；既有设备字段不能替代UI证据|
|U06|BLOCKED进度/完工/验收/退回历史及附件真实UI；M5 D01～05保留|
|U07|FAIL D02提醒ID/持久化恢复；真实重复点击/响应丢失/版本冲突/离线输入BLOCKED；不扩修M2/M5|
|U08|BLOCKED各类实际错误/空态出口；D02保存异常静默子项FAIL，A02未保存提示仅声明|
|U09|BLOCKED三个尺寸/窄窗/150%文字放大，全部实际测量NOT_RUN|
|U10|BLOCKED全流程键盘、焦点、非颜色线索、实际对比；不能由ButtonFlat声明推断键盘支持|
|U11|BLOCKED真实滚动/输入/面板稳定性；D05状态副作用FAIL|
|U12|NOT_RUN：未交同候选2–3分钟演示供独立人员说明实际结果和失败/空态；摘要入口不代替演示|

## 缺陷

仅下列直接阻断 M6 核心或授权隔离的问题列 P1。实际指源码及译码 adapter；**没有把 Python 异常描述成已经观察到的原生异常**。

### D-M6-01 / P1 / 必修：预约确认成功后，新增提醒格式化传错对象

- 文件与行：`app/bundle/main.splash:3145`、`:3146`；被调用定义`:1223`、`:1228`。
- 触发：走confirmAppointment，commitSucceeded=true后执行新增m6_register_follow_up参数求值；传入 `{id,startMs,endMs,status}` 预约对象。
- 实际/预期：`formatApptLine(appt)` 的函数体读取 `t.appointments.len()`，但appt无appointments；adapter返回AttributeError。预期确认后使用该真实预约时间登记提醒并保存状态，不能因展示字符串接错类型中断后续。原生异常形态未知。
- 根因/影响：复用任务格式化函数时误把任务形状当预约形状；发生在commit/logEvent后、saveState/refreshLabels前，核心确认后提醒流程无法闭合。
- 证据：source-probes `confirm_hook_appointment_object_accepted_by_formatter`；snapshot；M5差异显示此调用为M6新增。
- 具体改法：使用已有任务参数 `formatApptLine(t)`，或明确单预约格式化接口，核输出确为刚确认对象；不要靠给appt伪造appointments来通过。
- 验证：隔离实际预约确认→提醒落盘→界面回读→重启读回；新旧预约并存时摘要引用新确认时段；失败不显示成功或留下半登记。

### D-M6-02 / P1 / 必修（隔离及核心）：提醒未核时间/权限/终态，ID和恢复不可靠

- 文件与行：`main.splash:938`、`:941`、`:968`、`:976`、`:982`、`:1055`、`:1066`；失效缺口`:4278` cancelTask、`:3301`改约；静默保存`:913`、`:922`。
- 触发：A）登记due=100000、now=1000；同actor已撤任务访问权后刷新banner。B）固定时钟与ID_SEQ，连续登记同任务两次、另一任务一次，点击关闭第一条。C）确认预约后经理取消任务；或仅提议改约后拒绝改约；或提醒存储写失败后重启。
- 实际/预期：A未来提醒立即展示；unread只核ACTIVE/actor，banner又直接findTaskById读取problem，撤权仍带出 `REVOKED SECRET`。跳回函数visible拒绝成立也堵不住另一出口。B三条同fu_id、index覆盖到最后条，关第一条后第一任务ACTIVE仍在。C任务取消没有失效hook；仅改约提议即失效旧提醒，旧CONFIRMED仍有效时失去其跟进；写失败被catch return吞掉。预期到期/当前授权/项目/有效任务和预约才能显示，ID唯一，取消与实际替换后的旧作业失效，保存失败明确并可恢复。
- 根因/影响：提醒投影没有任务授权和到期闸；ID_SEQ不递增；失效绑定UI命令名字而非有效预约事实；持久化没有失败结果。直接违反安全隔离和T23可持续跟进。
- 证据：source-probes 的 future/reminder/revoked_banner/unique_ids/first_task_dismissed；`cancelTask_has_invalidation=false`、`save_followups_swallows_failure=true`；确认/改约/取消源码。不同任务同时间的记录是失败注入，并非声称真实VM已撞ID。
- 具体改法：所有提醒读/显示/点击先核当前可见授权、项目、到期、任务/预约仍有效，role空不作无限放行；记录稳定唯一ID及预约/接收主体引用；任务取消等实际终止动作更新提醒。改约待确认保留仍有效旧预约提醒，替换确认后废弃；持久化返回结果，失败保留待重试状态，读损坏不能默默认成功。采用现有可验证存储，不扩做后台调度。
- 验证：实际确认、到期前/后、同秒多任务、重复登记、关闭准确条目、进程重启、一份通知；改约提议/拒绝/确认、取消任务/预约、撤权/跨项目后展示与跳回都不泄漏。写入拒绝/损坏恢复只在本项目隔离数据中测试。

### D-M6-03 / P1 / 必修：设备历史没有可达生产来源，既定新增AI链未接通

- 文件与行：`main.splash:802`、`:813`、`:817`、`:830`；生产端`:2609`、`:2611`、`:2619`；UI`:6006`。要求源：`docs/implementation/01_REQUIREMENTS.md:136`。
- 触发：以实际recordModelMeta白名单产出一条APPLIED日志，选择同一真实任务的“设备历史”；再查接单后设备/历史/预约占用及处理事件变化的AI入口。
- 实际/预期：日志只有request/provider/model/输入hash/result/elapsed等，没有task_id；消费者只按e.task_id匹配，adapter结果kind=phase。就算人为加task_id，显示仍只是结果种类/provider/model，无设备历史事实与引用。阶段只是status固定文字，无链②“接单后读取设备/历史/占用→有来源建议”、链③“事件变化→最新阶段/下一步建议”的调用/版本来源。预期真实已核依据可达，未知明确，无虚构事实，建议不直接写业务且过期可拒。
- 根因/影响：把请求审计元信息当业务历史依据，生产/消费契约断开；M6核心新增AI场景没有实现。不要求顺手修M3旧报修链。
- 证据：source-probes 的 recordModelMeta_fields / real_producer_metadata_reachable_as_device_history；函数与UI源码；作者真实模型NOT_RUN声明。静态历史/阶段函数无写业务子项成立，但不是“模型不虚构”的运行证明。
- 具体改法：在既有来源/版本契约内建立任务/设备/项目/请求主体与证据引用的可追踪绑定，读取实际已授权历史与预约占用，接入已有模型入口的链②③；固定阶段文字可保留作人工/离线出口，但不能宣称其为模型建议。来源不存在/无历史必须标未知，沿用过期与错误契约，日志不可新增敏感原文。
- 验证：有历史/无历史/矛盾/引用不存在、事件变化/迟到响应、跨任务/项目/主体；同版本固定输入、真实模型元信息与依据、用户确认和权威回读分别存证。只能复用已授权配置；若确证必须新增provider配置或业务身份来源，先明确具体依赖，本轮不配置。

### D-M6-04 / P1 / 必修：收藏仍增加任务业务版本

- 文件与行：`main.splash:4350`、`:4374`（commit）、`:1916`（version+1）；作者断言 `M6/r1/scripts/m6_favorites_isolation.py:31`、`:34`。
- 触发：任务version=4，授权收藏togglePin，command/commitBound成功；检查真实调用的commit。
- 实际/预期：adapter version=5，期望保持4；作者“版本不变”用例仅断言m6_count_pinned_for_actor存在。应改变当前主体偏好、保留授权/去重与持久化，不污染业务版本。
- 根因/影响：M6沿用通用业务commit且没有验证消费契约；偏好变化会使其他业务确认/建议版本失效。togglePin/commit与M5基线同内容，明确为继承问题，但已直接阻断本模块明确收藏核心要求，不能以静态PASS掩盖。
- 证据：source-probes `favorites_do_not_increment_task_version`=5；affected-regression两个函数same_content=true。
- 具体改法：最小拆出经现有授权边界的偏好持久化/去重路径，收藏不推进业务version；保留task归属与actor隔离。不重写M2全部事务或身份系统。
- 验证：实际双用户收藏/取消收藏/重登、跨项目过滤，业务version和非偏好字段不变；同key重复操作不重复写；业务确认不因收藏失效。

### D-M6-05 / P1 / 必修：待办计数改写当前筛选，且默认关闭诊断仍求值

- 文件与行：`main.splash:791`、`:794`、`:796`、`:797`；调用`:996`，原生label初始化`:5203`的 `text: m6_diag_text()`。
- 触发：STATE.nav=fav，调用计数/诊断；初次构建UI时诊断默认关闭仍计算m6_diag_text。
- 实际/预期：adapter从fav变todo；`STATE.nav=STATE.nav`没有恢复，orig在覆盖后才赋且未用。预期计数/诊断纯读，不更换用户当前列表。
- 根因/影响：通过更改全局视图计算待办数；label初始化无条件执行有副作用的诊断函数，默认关闭标志未挡住。直接破坏收藏/全部任务筛选及三角色持续定位。
- 证据：source-probes `due_count_preserves_nav`=todo；源码对应初始化与refreshLabels已关闭分支对比。
- 具体改法：计算todo投影时显式传过滤参数或先保存/可靠恢复原nav；诊断函数保持纯读，默认关闭时不计算/不展示。不为计数写saveState。
- 验证：all/fav/todo、搜索和跨项目分别在首次渲染、刷新、诊断开关后保持原筛选/选中task_id，正确待办数且不写业务。

### 建议挂账（P2；不据此判FAIL）

- **A-M6-01 证据与映射修正**：`M6_IMPLEMENTATION_r1.md:170`起T/U错位；`:136`“全部PASS”只表示作者源码/模拟断言。真实用例按本报告表保留，新增证据不要覆盖r1。CONTEXT把后台启动launcher误写成禁止（环境约束段），本次用户已允许安全后台启动，应纠正文档。仅有前序catalog不等于当前digest通过，本轮已补当前Store子项。
- **A-M6-02 未保存/反馈接线**：`main.splash:1036`、`:1039`两个函数全源各仅出现一次（声明），未接输入/关闭handler；`:1004`统一反馈主要是空态/字符串匹配，未实现声明的全部加载/撤权/过期等恢复。只声明helper不能称键盘或未保存输入通过。建议接真实输入dirty与关闭确认、保留失败输入，随后核U07/08；本轮不凭未运行假定实际丢失。
- **A-M6-03 视觉与外部摘要边界**：正式主屏仍有开发诊断入口、9/10号字、30高Chip；仅作为源码设计偏差挂账，未虚构真实裁切/对比结论。当前“摘要”是内部detail tab与EVENT_LOG视图，不证明官方外部任务摘要入口/深链/grant生命周期接入；在可安全运行宿主后补同版本截图、交互与演示。没有原生数据不签视觉PASS。

## 判定

- **FAIL**：D-M6-01～05是当前M6核心/授权隔离P1；A01～03不构成判退理由。前序M0～M5结论原样保留，未开始M7。
- 精确范围：当前候选内容定位、本地离线签名和Store路径独立成立；12项源码译码探针以及函数差异检查完成；真实桌面、可信角色/撤权、权威业务命令/回执、运行重启和真实模型未完成。
- 安全解阻：本轮新预检sandbox rc71、pgrep rc3，需要一个能**只在项目隔离目录写、禁止网络、可枚举并关闭本轮launcher且核残留窗口**的运行环境。条件满足后用当前digest后台启动指定launcher，测完finally立即终止并核窗口；不用--help。不通过预检不能为了截图裸启动。未增加窗口，原先已有窗口状态未知，未全局杀用户进程。
- 本地路线裁决：**可行**。当前bundle digest `f721904d2bb4a7ac39f03abc2df7c17118a165d288a3b3fea9b66e8692d8ade8` 已离线安装验证；不需AppHub publish/公开签名/listing。签名仅本轮sandbox anchor有效，两把私钥已删，无上传/联网/消息/provider配置。
- 修复交接：只按D01对象契约、D02提醒授权/时间/ID/事实失效/保存恢复、D03新增历史建议链、D04偏好版本、D05筛选副作用逐条修。保留缺陷编号，提交新candidate_id、差异和独立可复验结果，再做缺陷闭合及受影响回归；不修挂账建议或扩到下一模块。
- 门禁/台账：仅GATES.json的M6 status及review字段更新，报告指向本文件，作者原候选/计数/证据字段保留。ACCEPTANCE.json不修改，以review_acceptance另记此原生范围，保留原历史后端/Web证据。
- 下一模块：**不允许，未执行；不给M7入口。**
- NEEDS_ABRAM=no：当前必修、安全运行条件与现有配置验证不需新增授权。真实模型NOT_RUN不自动等于必须换provider；本轮未证实必须新配provider/身份来源，且本地路线已可行。
- 过程偏差：开头按系统记忆流程读了一次项目外MEMORY.md索引，与本次用户只读项目约束冲突；已即时告知并停止进一步显式项目外资料读取，未写项目外文件。没有将该历史内容当本轮运行证据。

STATUS=FAIL
NEEDS_ABRAM=no
