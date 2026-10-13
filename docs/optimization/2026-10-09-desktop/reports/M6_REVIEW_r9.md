# M6 独立 Review r9

**最终结论：FAIL。合法提醒的启动加载已修复，但布尔值和数字字符串仍被接受为时间；历史/阶段 AI 的事实、协议和请求/缓存绑定仍有缺口；收藏偏好的同动作键对账仍未接通。D-M6-02/03/04 为本模块核心 P1，未闭合。8/8 CLEAN 仅证明本轮隔离和回收成立。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无子代理，不修业务代码，不进入 M7。
- 交接 candidate_id=`M6-r7-worktree`，base=`M6-r6-worktree`；作者报告 `reports/M6_IMPLEMENTATION_r7.md`，清单 `runtime/optimization/2026-10-09/M6/r7/CANDIDATE.json`。上一轮独立报告 `reports/M6_REVIEW_r8.md`。没有新的 M6 构建交接，按本次“首轮先审当前代码”裁决复核这三个缺陷，不按文件时间选版。
- **实际被测组合来源是已登记 M5-r8-worktree**：当前 main.splash 与其构建快照逐字节一致，SHA256=`6a7176e84a6f3692690d1d566129a0c57ea747f0c3fc5b943b9039a8b298d4c4`，573476 B；运输 bundle digest=`08c64f5600244854a63df93eb76ce3a2d1ca46f74d8f9195e00a32b43f1fd441`。旧 M6-r7 的源码摘要 `dd3f4a5e…` / digest `3f17a209…` 不冒充本次运行版本；没有制造新的构建 candidate_id。完整差异、函数行号与摘要见第1段 provenance/source-regression 及本次重核证据。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树已有他人未提交修改，全部保留。运输 manifest 含离线签名 integrity，与工作树 manifest 不混称同一完整文件；实际 installed、hub-mirror、唯一 running 包所有文件均等于冻结运输件，业务源/config/identities 与工作树一致。
- 前置：M5=`FAIL / M5-r8-worktree / M5_REVIEW_r10.md`，不存在已接受的 M5 PASS。依本次前序缺陷挂账裁决继续局部审查；不修 M5，不把其真实附件缺陷重复登记为 M6 新 P1。
- 宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 原生实际执行：外部驱动经 harness 于 **12:58:42–13:00:31 +08:00** 执行独立请求的8个 `_v2` 场景，全部 quit_http/rc0/CLEAN；无 ABORT。审查者没有启动 launcher、sandbox-exec、pgrep、osascript 或辅助功能/自动化。
- 原生输入边界：请求无 ui_actions，仅内置 launch-hub/capture，没有造 SESSION。固定宿主 type/key 不实现的证据来自同宿主既有 Review 与当前 schema；本次禁止 System Events/辅助功能，不能用 schema 中另一授权说明绕过。角色夹具只是诊断目标，不是已完成可信登录的三角色流程。
- 模型：8场 needs_model=false，模型代理/stat字段及文件缺省，无 endpoint/MM_KEY 注入，真实 MiniMax 调用0；没有实际402/余额/欠费错误。身份/provider/本地离线签名已授权，不是新增授权缺口。
- 路由/标题：无主会话 Router 型号核验/切换、当前 thread createdAt/标题工具，不冒称已切换指定模型或已实际命名。
- 已阅读：第1段 AGENTS/CONTEXT、00/01/02/M6/04、作者交接/候选/上一轮缺陷/相关源码差异与用例；第2段本请求、阶段笔记、summary、8个result、profile/probes、完整日志/denials、全部MANIFEST、实际运行包与隔离盘、相关源码，以及16张PNG的3种独特画面。
- 已运行：第1段独立官方离线 hub verify；驱动8场冷启动；第2段只读证据审计，未把 Python 改写业务算法当应用测试。保护输入核验一致，最终写入前再次检查。
- 未运行：可信三角色/收藏隔离/真实重登、实际通知去重/旧约取消/动态撤权跳回、三条真实模型链及人工继续、同Store跨进程重启、提交点故障/迟到交错、完整键盘/150%/演示。领域动作未发生为 NOT_RUN；只对确实不能用本轮白名单表达的具体步骤标 BLOCKED。
- 置信度：候选/隔离回收/加载正反例及源码残留 **高**；布尔/字符串被数值运算隐式接受的具体内核实现 **未知**；真实模型事实正确性及完整可信流程 **未知**。

## 证据索引与独立核验

路径以下均相对项目根：

- **H**=`runtime/optimization/2026-10-09/M6/native-runs/review_r1_0937_REQUEST_review_r1_0937/`，驱动本次原始证据，审查者未改。
- **E**=`runtime/optimization/2026-10-09/M6/native/recheck_20261012_125718/`，本次冻结源、旧请求/笔记保全、新seed摘要、源码重核、验签及审计。
- **P**=`runtime/optimization/2026-10-09/M6/native/review_r1_0937/`，原阶段 provenance、M6-r7→当前 diff 与逐函数源码。
- **R**=`runtime/optimization/2026-10-09/M6/native/REQUEST_review_r1_0937.json`；**N**=`runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r1_0937.md`。
- **A**=E/`native-evidence-audit.json`。实际命令 `python3 -B runtime/optimization/2026-10-09/M6/native/recheck_20261012_125718/audit_phase2.py`，rc0，**12703项证据一致性检查、0不一致，不是12703项业务测试通过**。

1. R与summary.request全等，且请求SHA等于第1段冻结值；harness/template SHA与冻结和当前一致。MANIFEST **2666项**全重算，无缺失/摘要不符/重复/漏列/越界路径或符号链接。目录还含上一批8个非v2场景，**它们只纳入文件完整性检查，不作为本次业务运行**。
2. 驱动没有采用第1段建议的新输出根，复用了旧根；本次场景名均为新增 `_v2`，8个旧场景目录仍在，旧根 summary/MANIFEST 已由驱动换为本次内容。报告使用用户交回的实际H及匹配R的8场，不宣称旧聚合元数据完整保留，也不把路径偏差归为业务失败。
3. 每场 profile_probes.ok=true，apply rc0，场外写探针拒绝且created=false；5个禁读探针满足限制；pre/post_pgrep均 rc1/class=NONE/out/err空，pgid_members_after=[]。按记录的场路径、原HOME字符串、控制端口及模板重建profile，字节和SHA一致。外联规则只允许Unix socket、本机控制口，本次无模型代理口。
4. HOME/app-data/cache/tmp/config/data/Metal/rinx/octos-home全在新场目录；原HOME mtime相等、library_scan空是驱动记录，审查者没有访问项目外原HOME。第1场运行组另记录短暂 `osascript` 子进程，脚本用途/参数未记录；本请求无ui_actions、harness没有进入该分支，不能把它说成审查者执行了登录自动化，也不凭名称猜其用途。退出组已全部回收。
5. 每场seeded_files全清单/SHA与独立seed和mirror一致；installed/mirror及唯一running包所有资源与冻结运输包一致。digest_seen_in_seed=true、digest_seen_in_host_log=false如实保留，以完整包字节定位版本。
6. 8场 files_written_count 为 **126/126/126/126/127/126/126/127**；所有列表排序、唯一、数量、存在及作用域一致，均未触400项截断。这是harness按mtime采集的文件记录，不是业务动作次数。完整denials重新计数等于result：外部443、系统Metal缓存、/dev/dtracehelper尝试被拒，没有据此宣称成功外联/外写。
7. 完整日志字节数、tail、markers重新计算一致。8场业务eval均573476 B/view=true，另有809 B系统视图；无parser、业务变量/widget缺失、panic、unknown-action或view=false诊断。最初两场有Metal/present的493/321 ms ui-hang信息，记录为启动观察，不因该信息单独新增P1。
8. 8张请求PNG和8张part PNG均核SHA/格式/尺寸；**共3种独特SHA画面，逐种实际查看**，其余同字节。boolean场part与final不同，二者已分别由独特画面覆盖。全部2560×1232：登录行可见，未登录/无可见任务，未展示异项目私有正文/旧缓存；null/截断错误及恢复Chip未出现在可见区域。三请求size不等于三个客户区已验收，150%未运行。
9. tasks/actions/events/隔离accounts及提醒原文8场全与seed同字节；actor=null、tasks_pending_recovery=false、tick_exception_count=0。manager原needs_verify回执、marker、旧主体缓存保留，内存history_view={kind:none}，没有无权正文显示；**不是登录后实际偏好对账或动态撤权测试**。
10. 合法空数组/四status/四条重复旧约/单条：pending=false，内存提醒与seed列表全等，不再错误备份。null第2成员/截断第1成员：整份拒、pending/dirty=true、内存空，原文与recover逐字节相同。布尔true/数字字符串"1"：pending=false、非法值原类型进入内存、没有recover——**D02原生FAIL**。通知没有实际发出，不声称重复通知或错误提醒已发生。
11. 第1段官方离线verify rc0、catalog sequence 1 verified, 1 entries；新私钥0，原build_r8两私钥再次确认不存在，见E/offline-verify.json。无publish/listing/上传/push/Issue/消息/公网部署。第1段项目外记忆索引读取偏差已在N披露；本段显式读写均限项目内，未读取明文凭据/模型密钥。

## 必需检查

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/前置|冻结/差异/完整运行包核对|版本一致，前置如实|组合源/M5-r8摘要一致；M5仍FAIL挂账|版本PASS子项；前置未满足|P/E/A，M5门禁|
|隔离/回收|profile重建、探针、PGID/写列表/denials|硬隔离、结束无遗留|8场均满足|PASS|8 result/profile/denials|
|解析/工作台|冷启动与全部PNG/完整日志|零parser、业务渲染|8场view=true，登录完整可见|PASS子项|8log/16PNG|
|合法提醒恢复|空数组/四status/重复旧约/单条|正常读入、不pending|全部内存等于seed，无错误备份|PASS限定启动加载子项，旧反例关闭|4正例state/followups|
|null/截断保护|中间null/未闭合中文|整份拒、保护原文|pending/dirty、内存空、recover全等|PASS此子项|2反例盘/state|
|严格时间schema|true与字符串"1"，对照数值1|非法值整份拒|两值均入内存、pending=false|**FAIL D02**|boolean/scalar场state及原文|
|恢复反馈/出口|坏盘冷启动原生图与渲染源|故障可见、能继续恢复|错误在盘，所见区域无故障/恢复入口，左栏下部裁切|可见反馈子项FAIL D02；点击/滚动恢复NOT_RUN|null/truncated PNG，main:2822/10625|
|通知/去重/旧约/跳回|启动重复/旧约/其他主体夹具|可信实际动作核验|没有登录/通知/改约/跳回命令|NOT_RUN，具体可信输入/同Store调度BLOCKED|R/空业务动作记录|
|三角色/收藏/重登|三个角色目标夹具＋偏好恢复源|可信操作、按主体隔离、版本不增|无真实会话；D04恢复源欠|NOT_RUN；D04源码FAIL|3入口图、相关源|
|历史/阶段AI与人工出口|协议、事实映射、回包/缓存/保存链核对|有据、拒旧回包、准确保存、人工继续|D03源码未闭合；真实调用0|源码FAIL，真实模型/人工继续NOT_RUN|源trace及manager缓存|
|真实视口/键盘|全PNG/SHA、size命令、能力边界|三客户区/150%/键盘可达|仅未登录图、同尺寸；恢复所见不可见|完整NOT_RUN；确切键入/放大通道BLOCKED|PNG/schema/同宿主拒动作证据|
|受影响回归|D01/D05、共用load/偏好路径及冷启动|已关子项保持，无回归|函数正文一致，合法加载改善|源码/启动子项保持；不签前序业务PASS|P/E/8场|

**BLOCKED精确范围**：固定发行宿主不实现内置type/key；本轮禁用基于System Events的ui_actions，无法形成可信文本登录、实际中文人工出口或Tab流程。当前schema每场新盘、只启动前seed，不能表达同Store跨进程重启、运行中精确writer/finalize故障、登录后撤权/断线/迟到交错及150%设置。解阻需驱动/宿主提供本轮获准的内置输入及受控重启/注入接口，保持现有Seatbelt和秘密边界。未执行的领域动作/模型调用仍记NOT_RUN；本次没有ABORT，已实测业务反例必须记FAIL。agent rc71/rc3没有被用作理由。

## 缺陷及上轮闭合

|编号|本轮闭合情况|
|---|---|
|D-M6-01|已关闭源码子项保持：formatApptLine一致；真实预约完整交互仍未测|
|D-M6-02|P1/必修/部分关闭：合法加载、null/截断整份保护PASS；非法时间接受和可见恢复反馈未闭合|
|D-M6-03|P1/必修/OPEN：上一轮剩余协议/事实/完整请求与缓存绑定/失败反馈源码保持；模型0次|
|D-M6-04|P1/必修/部分关闭：saved=false准确回退保持；同key偏好恢复仍缺消费者和正确判据|
|D-M6-05|已关闭源码子项保持：数量函数一致；可信实际筛选数量未测|
|R-M6-01|本地离线验签/当前digest实际installed/running子项保持，不需公开发布|
|A-M6-01～03|建议继续挂账，不因美化/演示/文档建议单独判FAIL|

### D-M6-02 — P1 / 必修：严格时间校验仍接受非法类型，恢复错误/出口未在可见区呈现

- **文件行**：`app/bundle/main.splash:1092` m7_is_number_value，`:2394`成员门禁（due调用在`:2416`附近）、`:2450`loader、`:2581`普通保存；`:2822`统一反馈与`:10625`状态/恢复控件区。
- **触发**：R/boolean_time_member_v2 seed due_ms=true；R/scalar_list_83_v2 **实际已更新为due_ms字符串"1"，不是旧场景名所暗示的标量83**；对照合法数值1。另null/截断坏盘启动查看PNG。
- **实际/预期**：两非法时间均完整进入STATE.m6_follow_ups，pending=false、无recover，原类型保留。预期整份拒、原文/备份保护、pending/dirty及清晰恢复入口。坏盘两场盘状态准确，但可见画面仍是无任务/未选任务，没有故障文案/恢复Chip；没有运行点击/滚动，不能宣称所有方式均不可达。
- **根因**：以`v-v==0`作为严格数值类型判断，在固定宿主实证中不能区分数值、布尔和可转数字字符串；具体内核转换路径未知。反馈函数先检查空列表而优先返回空态，左栏非滚动Down容器在导航/筛选后堆放状态/恢复/AI控件，错误及出口处于可见区外。普通保存仍仅按异常判断成功，没有写后字节/schema读回。
- **影响**：核心持续跟进的输入契约和失败恢复不成立；非法时刻可被采纳，不能据此声称已错误通知。涉及硬3/5、G0-F/T23/U07/U08/U09/U11。
- **证据**：H/boolean_time_member_v2与scalar_list_83_v2的state及原followups、A的due_ms原类型；H/null/truncated state/recover/PNG；冻结源码上述行。
- **具体改法**：只修剩余D02，保留已通过的合法加载和整份备份保护。经harness实证严格类型判断，数值1可用、true/false/"1"/null/对象/数组均拒；不要用数值运算能成立代类型判断。load/显式恢复共用门禁，普通写和受控恢复核读回再清dirty/pending。故障状态优先于空态，恢复提示与动作放可见区域或可验证的滚动区域；失败保留输入/原文，不靠清空提醒换通过。
- **验证方式**：独立复跑上述正反例，核内存、pending、原文和backup；合法冷启动仍零parser。经获准内置动作实际点击恢复、读回、同Store重开，再跑同通知只一份、旧约取消、撤权跳回及写/读失败不解锁。源码检查和CLEAN不代这些动作。

### D-M6-03 — P1 / 必修：历史/阶段依据及请求/缓存绑定仍欠，人工保存失败能被覆盖成成功

- **文件行**：`:315`provider强制JSON；`:1945`回包helper；`:1958`history输入，`:1991`system；`:2112`phase，`:2139`system、`:2150`首6事件summary；`:950`实际logEvent.after；`:3170/3202`caller、`:3225/3231/3259`建议保存/恢复/人工出口；`:11457/11499`消费视图。
- **触发/实际**：两system仍只`history_only_no_write`/`phase_only_no_write`，没有明确JSON返回结构，provider却强制content[0].text为JSON。history只当前任务前6条notes，未形成有出处的设备历史；phase只前6事件且读summary，标准事实在after。helper仍读全局PENDING，没有核本次rid/request_version/expected_task_id/当前选择/facts/evidence完整快照。持久view只有task/kind/ts/items，未保留并重核主体/项目/事实版本/到期/合法出处。m6_save_history_view不返回保存成功；人工caller随后无条件显示“已保存”。人工输入仍读`.text`而登录同宿主采用`.text()`，实际人工键入未测。
- **预期**：两链明确协议和有权真实来源，最新事件事实正确，无历史未知，矛盾不编造；发出/回包/消费/重开都核固定请求/对象/权限/事实/到期；保存失败准确且可人工继续。实体ID存在不等于生成正文有事实支持。
- **根因**：输入事实映射与返回协议不完整；用易被后请求替换的全局pending校验先请求回包；缓存丢安全/版本上下文；保存失败未贯通caller。A回包/B改写pending、同主体同项目且A版本不变的源码反例仍存在，动态交错未运行。
- **影响**：核心AI历史/阶段依据、过期与撤权安全、失败人工出口，硬2/5、T25/T26/T34/T35/T38/U02/U07/U08。不声称模型实际生成过虚构事实，本轮真实调用0。
- **证据**：E/P逐函数冻结源与行号；H/manager原缓存保全、内存kind:none、未登录PNG。该夹具仅证明未显示外来正文，不能当合法缓存恢复或真实AI成功。
- **具体改法**：按原D03补两链JSON协议、真实有权设备历史及最新事件after和来源ID；固定rid/version/task/actor/project/facts/evidence/expiry快照传入校验；回包/渲染/重开都重核，拒错对象/过期。保存结构化出处与上下文，采用实证宿主schema；保存/读回返回真实结果，caller不覆盖失败，保留输入。人工控件用实证文本接口。保留模型仅建议、不直接写业务的边界，不通过关闭模型换PASS。
- **验证方式**：获准可信入口后三组新描述及三链真实MiniMax，经needs_model本机代理模块≤10请求；未知/矛盾/不存在引用拒、人工继续、切主体/任务/撤权/迟到/事实或证据变化不串。核权威TASKS不由模型直接写；保存拒写/重开核主体版本出处。遇402/余额/欠费立即停止并记录原文/NEEDS_ABRAM=yes。裸代理调用和夹具不能替代业务链。

### D-M6-04 — P1 / 必修：收藏不增版本，但通用恢复仍按版本不变判未提交；稳定标记无恢复消费者

- **文件行**：`:2921`m6_save_prefs，`:3052`finalize附近、`:3083`marker写；`:4374`bootReconcilePending、`:4440`版本不变分支附近；`:9666`togglePin、`:9730`saved=false分支。
- **触发**：收藏tasks已落盘而receipt finalize/state/readback失败后，重启/重试按原action_id恢复。实际提交点故障未运行；本项基于仍可达的源码控制流。
- **实际/预期**：saved=false准确回退/未保存的旧问题保持关闭；恢复未决tasks拒偏好写也已补。marker全源仍只有写和提示，无读/对账/清理消费者；generic看到disk.version==expected就判pending_orphan/未提交，而收藏设计不递增业务version，也没有按固定主体/任务/预期pinnedBy核原动作。预期按稳定key及权威偏好事实恢复，准确final或保持未知，不能把已写偏好当未执行盲重做。
- **根因**：不增版本偏好复用增版本业务对账协议；持久marker未接恢复边界。另saveReceipts返回bool失败不会抛异常，但finalize处仅try/catch、未消费返回值，因此该明确失败路径可漏出needs_verify/marker；与原“准确消费保存结果”剩余缺口相同，动态故障未运行。
- **影响**：核心收藏结果未知后的持续使用与可靠重登/重试，硬1/5、T30/U07/U11；不是美化建议。
- **证据**：冻结源码全源marker检索、generic判据及saveReceipts返回协议；H/manager旧回执/marker/tasks仍原字节。预撤权/未登录时保持标记是安全行为，不以此声称实际对账已发生或误恢复已发生。
- **具体改法**：只为togglePin补固定key、主体/任务/预期偏好读回协议；marker可靠写/读回、启动消费，成功清理，未知保留并禁止新key盲做。让保存接口显式表达实际保存/跳过结果，准确消费saveReceipts的bool及saveState的保存状态；不要仅捕获throw。不得递增业务version来迁就通用恢复，保留已关闭的saved=false回退子项。
- **验证方式**：可信两主体pin/unpin、他人隔离、业务version不变、重登保留；精准tasks拒写与已写后finalize返回false/抛错、state失败/读回失败；同Store重开按原key核偏好/回执/marker，不制造第二操作。未能运行时保留NOT_RUN，不以预填回执代业务成功。

## 全部硬验收与既有映射

|硬验收|本轮精确判定|
|---|---|
|1 三角色/搜索/收藏/重登/跨项目|D04源码FAIL；完整可信流程NOT_RUN，未登录不展示私有正文子观察PASS|
|2 三条真实AI/失败与无历史人工出口|D03源码FAIL；模型/人工继续NOT_RUN，0真实请求|
|3 提醒恢复/去重/旧作业/跳回|合法启动加载及null/截断保护PASS子项；非法时间FAIL D02；真实通知/取消/跳回NOT_RUN；不宣称后台常驻|
|4 视口/放大/键盘|原生登录渲染改善；故障/恢复所见不可见；三客户区/150%/完整键盘NOT_RUN，具体通道BLOCKED|
|5 输入/选择/滚动/恢复/P0责任|D02/D03/D04核心FAIL；其他真实交互NOT_RUN；P0/38业务/12UI要求与历史来源保留|

|编号|本轮范围及结果|
|---|---|
|G0-F|前台合法加载PASS子项，严格schema FAIL D02；实际通知/后台常驻NOT_RUN|
|T17|断线期间动作/重连权威重读不重写NOT_RUN；受控断线通道BLOCKED|
|T18|未登录未显示跨项目/联系人/私有任务子观察PASS；可信搜索/列表/事件/附件查询NOT_RUN|
|T23|合法启动恢复PASS，时间schema FAIL；同Store重启/一份通知/旧约失效NOT_RUN，具体调度通道BLOCKED|
|T25|真实缺失/矛盾/恶意原文不编造不改业务NOT_RUN；D03源码FAIL，无实际虚构断言|
|T26|真实模型失败人工继续NOT_RUN；人工保存失败反馈D03源码FAIL|
|T28|离线安装/实际运行包/隔离/解析PASS子项；提醒schema FAIL，可信业务/重开NOT_RUN|
|T29|共享grant关闭/到期/退出/动态撤权不继承NOT_RUN；预撤权未登录仅有限观察|
|T30|真实收藏隔离/重登/version不变NOT_RUN；准确拒写源码保持，偏好对账D04 FAIL|
|T33|三组新描述真实意图泛化NOT_RUN，0模型|
|T34|未知/多候选/无历史/不存在引用真实拒NOT_RUN；D03依据/协议FAIL|
|T35|动态改派改约/撤权迟到回包NOT_RUN，受控交错BLOCKED；完整请求绑定D03 FAIL|
|T36|真/假工具同组白名单契约NOT_RUN；harness隔离不是工具替换验收|
|T38|版本/源提示/宿主/seed摘要固定PASS子项；真实模型同组成功失败复跑NOT_RUN|
|U01|三可信角色当前阶段/下一人/动作NOT_RUN；三个预定角色不是三个真实会话|
|U02|原话编辑/歧义/失败人工继续NOT_RUN；D03出口/保存反馈FAIL|
|U03|同task多主体事实/权限动作/承接者禁自验NOT_RUN，不代签M5|
|U04|真实当前约/改约/冲突/过期NOT_RUN；D01已关源码保持|
|U05|设备安装与服务空间来源/实际选择NOT_RUN|
|U06|进度/完工/验收/退回历史真实链NOT_RUN；M5 FAIL保持|
|U07|坏原文保全PASS子项，提醒schema D02和偏好恢复D04 FAIL；重复/冲突/丢回包/断线领域动作NOT_RUN|
|U08|未登录空态渲染PASS子项；坏盘错误/恢复未在可见区、人工保存反馈FAIL；真实重试/附件/过期出口NOT_RUN|
|U09|真实图逐种核查，登录行完整可见；恢复所见区域裁切FAIL子项；三客户区/150% NOT_RUN，不沿用HTML|
|U10|完整键盘/焦点/实测对比NOT_RUN；固定宿主拒type/key、本轮禁自动化的具体步骤BLOCKED|
|U11|原生launch/capture渲染PASS子项；实际输入/滚动/面板/命令反馈NOT_RUN；恢复反馈D02 FAIL|
|U12|同版本2–3分钟独立人员演示NOT_RUN；继续作为建议挂账，不因演示美化独立判FAIL|

## 判定

- 最终结论：**FAIL**，精确适用于本次冻结M5-r8组合代码中的M6功能及8场独立原生诊断；不将旧M6运输件或历史后端测试当本次原生结论。
- 必修：D-M6-02 严格时间schema/可见恢复反馈及写后核验；D-M6-03 事实/协议/完整绑定/缓存恢复/人工保存结果；D-M6-04 不增版本偏好的同key对账及保存结果消费。
- 原先合法提醒全拒问题已实测关闭；D01/D05与saved=false回退的已关源码子项保持。仅核心/安全P1决定FAIL，建议不独立否决。
- M5依赖未PASS挂账，不改变前序结论；本轮回归仅合法任务加载、共用恢复、偏好路径及原生冷启动，未声称真实附件完工/验收通过。
- 更新：仅新增本报告及 `docs/optimization/2026-10-09-desktop/GATES.json` 的M6审查字段/历史；原candidate/作者字段、其他模块、全局外部交付及ACCEPTANCE.json保持。审计/核验附属证据在E，不改驱动H。保留上一轮Review来源和审查字段快照。
- 不允许进入下一模块。本模块修复方Kimi-K3只按D02/03/04剩余清单修；先经驱动harness确认冷启动零解析/业务区渲染不回归，提交可定位新候选及正反例权威证据，再独立复审。不要求重复修已关子项，不扩展功能。
- 具体白名单/受控调度缺口需要驱动或宿主实现，不是Abram新增身份/provider授权问题；本次无计费错误或公开发布需求。

STATUS=FAIL
NEEDS_ABRAM=no
