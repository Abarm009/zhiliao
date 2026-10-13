# M7 独立 Review r11

**最终结论：FAIL。必修仍为 B-M7-01、R-M7-02。** 本轮独立请求10场全部CLEAN、实际业务脚本已加载、工作台能渲染；但每场仍有17条解析诊断，合计170条。合法空任务/完整任务被误标损坏，7个坏任务场景最终 `tasks_pending_recovery=false`。这份冻结候选尚不能作为可复现的本地桌面发布候选。

- 审查者 / 日期：当前Codex主会话唯一审查者，2026-10-13，Asia/Shanghai，无子代理。现有工具不能核验/切换主会话Router/gpt-6.1-sol路由，未声称切换；没有可用的自身createdAt/改标题接口，未用当前日期代替创建时间，也未读项目外会话文件。
- candidate_id / base：**M7-r8-worktree / M7-r7-worktree**，**0.1.0-g**。GATES、最新M7实施r8、r8/phase1-audit.json一致定位，不按mtime选候选。r8未单独生成CANDIDATE.json，实施报告明确使用phase1-audit.json替代。
- 作者报告：docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r8.md。上一轮最终报告M7_REVIEW_r10.md；本轮只核其原缺陷及受影响回归，不扩审无关业务。
- 冻结包 **F**：runtime/optimization/2026-10-09/M7/r8/release/octosense-repair-0.1.0-g/，digest=`e0ee84d8463778bade271acc1a4798e0486bbd15a3c5fc21d6bc16e1cadf89a8`。F/main.splash **597814 B**，SHA256=`3b5001839fda8153d5adfeba04f11669ccd4e243af39c2dbd8c8e6d7a89d2852`。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`。当前app/bundle/main.splash已为**701133 B**，SHA256=`3bc555f2f0e4134120d7b8eb71d3a4e74f860cb6cc8ee64a3539fcc9203ef82b`，与M6-r10来源相符，**不是被审M7字节**。作者dirty.diff、E/scoped-dirty.diff/status、两个源码副本、frozen-to-current.diff可定位。未把新工作树的解析清零、登录或UI能力转移给旧冻结包。
- 前置：**M6 FAIL / M6-r10-worktree / M6_REVIEW_r12.md**，没有已接受M6 PASS。依用户前序挂账裁决继续局部审查，不代签前置，不修M6。本次FAIL依据当前M7的实际核心失败，未因挂账/P2建议额外判FAIL。
- 宿主：M0/r3项目内提取OctoSense.app；octosense SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，octos-kernel SHA256=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。固定二进制来源可定位，不外推未知上游可重建性。
- 原生运行由外部驱动执行：**07:46:01–07:49:17 +08:00**，10场、2批；10/10 quit_http、host rc0、CLEAN，无ABORT。审查者未启动launcher、harness、sandbox-exec、pgrep或osascript。
- 快照：第1段到第2段，**38个保护文件、116个生成输入文件全部未变**；harness执行摘要与当前/第1段一致，无并发漂移。请求/候选/宿主/材料/台账同一快照；GATES只在本轮最终审查落盘时更新。
- 已读范围：第1段CONTEXT、AGENTS、00/01/02/M7/04、r8交接、r10原缺陷及相关冻结源/材料；第2段全部summary/result/profile/probes、MANIFEST、完整host.log/denials、运行包、隔离事实盘与PNG。以05_IMPLEMENTATION_ACCEPTANCE、09_AGENT_HARNESS、10_UI_UX_SPEC和原ACCEPTANCE定义校准编号。
- 实际执行：第1段独立hub stamp/check/verify和官方install_staged/Store重建/may_run；第2段 `python3 -B runtime/optimization/2026-10-09/M7/native/review_r1_0002/audit_phase2_r11.py` rc0，**16911项证据一致性检查、0不一致**，不是16911个业务用例。1406个MANIFEST文件全部重算，20张PNG结构/摘要核对，7种不同摘要画面全部目视查看。
- 未运行：可信非空口令登录/每写每查核权、三角色完整正常/退回链、实际附件、成功业务回执、可信任务恢复两分支、同Store业务进程重启、精确备份/写/读回故障、真实模型、完整键盘/三客户区/150%/完整演示/官方scan。未执行项记NOT_RUN；确实不能由当前允许动作表达的具体步骤另记BLOCKED，见下文。
- 真实模型：10场needs_model=false，候选enabled=false/storage-only；真实MiniMax调用**0**，model_proxy_stats缺失与未启动代理一致，非成功调用证明；无endpoint/MM_KEY注入、无402/欠费记录。
- 安全：本次两阶段显式文件读写均限本项目；未读项目外memory、runtime/secrets、账号明文或原业务盘，未改业务源码/harness/原数据。无公开签名/publish/listing、push、Issue/评论、消息、公网部署或计费变更。本轮新私钥0；作者keys目录空、两条历史私钥删除路径仍不存在，不伪造本轮删除事件。
- 置信度：字节、隔离回收、所见UI、解析诊断、合法任务误拒、坏盘pending失效和提醒类型加载结果 **高**；`ok`语法冲突的内部机理、pending被哪条后续路径清掉、可信恢复/完整业务/模型效果 **未知**。

## 证据索引

- **H**：runtime/optimization/2026-10-09/M7/native-runs/review_r1_0002_REQUEST_review_r1_0002/，外部驱动原始证据，只读。
- **E**：runtime/optimization/2026-10-09/M7/native/review_r1_0002/，独立离线安装/seed/源码差异、phase1-audit.json、native-evidence-audit-r11.json、final-acceptance-64-r11.json和收尾检查。
- **R**：runtime/optimization/2026-10-09/M7/native/REQUEST_review_r1_0002.json，SHA256=`c30650a4dec21f32855ff8b91306353504017b85fe0fa99ea1eee4e2ef0aedd8`。
- **N**：runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r1_0002.md，第1段笔记保留原文。
- 历史：M7_REVIEW_r10.md及E/gates-before.json保留上一轮结论、证据根与逐项来源，未删除旧报告/原验收。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/源码/材料|三方定位、重算冻结/运输/运行字节和清单|同候选、差异可解释|11资源/材料指纹及自摘要匹配；当前工作树明确排除|PASS 定位子项|E/phase1-audit、源码diff；F材料|
|本地准入/安装|新副本stamp/check，verify签名，新Store install_staged与may_run|本地准入可重现|全部rc0；unsigned warning保留，声明storage、hosts空、agent none|PASS 离线子项；不是完整P03|E/phase1-audit commands|
|原生确实打开应用|核catalog、运行目录、完整log/eval、PNG|业务包加载且版本正确|10场app_not_opened=false；每场597814 B eval/view=true；唯一.running七文件等于运输|PASS 加载/渲染子项|H每场包/log/PNG|
|隔离与回收|重建profile，核探针、env、PGID、driver观察|限场内写、五禁区拒读、无残留|10场probes=true，pre/post NONE、PGID_after=[]、CLEAN；osascript exec被内核拒绝|PASS|H result/profile/denials|
|冷启动解析门槛|无tasks及合法/坏盘各新Store冷启|0解析诊断|每场10条Expected expression+7条Parser stuck，共170条[E]；工作台仍渲染|FAIL B-M7-01|H全部完整host.log|
|合法任务加载|空白包裹[]、完整DRAFT正例|不标坏、不新建recover|两场原文未变，却都生成recover、status误报任务文件异常且原因空|FAIL R-M7-02|legal_empty/legal_record事实盘/state|
|损坏任务保护|对象、截断、id-only、尾随、首尾[]垃圾、version=true|整份拒绝、pending保持、准确错误可见|六场均pending=false、why空；原文/recover精确保全|保护FAIL；保全PASS R02|六bad场state/盘/PNG|
|既有备份保护|新坏盘+既有合法recover|不覆盖旧备份，另存本次坏盘且pending保持|recover403 B保留，corrupt.latest41 B同坏盘；status有分类但pending=false/why空、UI任务banner空|保全PASS；保护FAIL R02|bad_preserve_backup|
|恢复入口与动作|看实际图，核两次内置tap尝试后状态/盘|错误与有效安全出口；未认证拒绝可见|两任务恢复按钮可见；无任务错误banner、无recover.bak或明确恢复/身份拒绝回执；pending已false|入口位置子项PASS；实际两分支NOT_RUN，R02未闭合|bad_object/bad_member PNG/state/log|
|空输入登录回归|legal_empty内置tap、看PNG/actor|空输入明确提示、不建会话|真实显示“请输入账号ID与口令”，actor=null|PASS 原R-M7-01子项|legal_empty PNG/state|
|提醒类型回归|空/整数/小数及true/false/string/object/array/null|合法加载、非法整份拒且原文备份|正例加载；六非法内存[]，pending/dirty=true，原文与recover精确|PASS 原R-M7-03类型子项|10场follow_ups/state|
|证据完整性|MANIFEST、request/result/argv/seed/captures/完整日志及denials重算|无遗漏/篡改/未解释差异|1406文件、16911检查、0不一致；单场单capture均存在，无unknown动作|PASS 完整性子项|H/MANIFEST、E/audit|
|完整链/重启/模型|核实际操作与权威回执|同候选真实成功/退回/恢复/重开/模型|未执行；Store对象重建不代业务进程重启，诊断seed不代业务完成|NOT_RUN；具体不可表达步骤BLOCKED|R/N及本报告|
|发布媒体/完成表述|检查最终listing/材料/README及真实PNG|同版本、无旧完成态冒称|listing明确禁模型/待复核；仍placeholder和README旧入口/闭环叙述，完整演示未交|A01/A02 P2挂账；完整媒体NOT_RUN|F/listing、app/README.md:5/:7|
|四种交付状态|只核本候选回执，不迁移历史Issue|本地、发布、赛事、收录分别记录|本地准备FAIL；本候选P06/P07/P08均无新回执，无外部动作|状态区分PASS；外部NOT_RUN|本报告、GATES.review_summary|

### 证据核对的具体边界

1. summary嵌入R全等；场景顺序、purpose、size、actions、result摘要、batch和命令逐项匹配。MANIFEST1406项无重复、越界、漏列或错hash。原始H未修改。
2. 当前harness摘要为`8141b4de36e8a248a1b7ed0b9d430fa3ee464ccbc65fc927ef1de40be5ef34c8`，与summary/第1段一致；模板摘要`76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`一致。根据记录run_dir/控制口和黑名单内原HOME字符串重建十份profile到同字节，未读取项目外路径。
3. 五禁读探针全部拒绝，场外写探针未创建文件；osascript执行探针被拒。本轮宿主实际多次尝试exec osascript，denials记录为`process-exec* /usr/bin/osascript`，**不是已执行系统自动化**；十个运行PGID快照只有宿主完整argv，最终无子进程残留。不能隐瞒尝试，也不把拒绝当成功越界。
4. HOME/app-data/log/cache/tmp和XDG/Metal路径均在本场内。driver记录原HOME mtime前后相同、Library扫描空；审查者未自行扫描项目外。files_written计数119–121，排序/唯一/存在/场内性及未截断均核对；这是mtime文件清单，不是系统调用审计或业务动作数。
5. denial摘要以同parser从完整日志重算一致；外443、系统Metal缓存、dtracehelper尝试被拒。宿主news七来源失败，不声称整个宿主没有尝试外联；未见被允许的非本机模型网络路径。
6. 冻结manifest249 B与离线签名运输manifest629 B摘要不同、原因明确；六非manifest资源完全相同。十场installed/mirror/唯一.running七文件逐字节等于签名运输输入。同version/digest字符串不足以代这个比对；本轮digest_seen_in_seed=true、in_host_log=false如实保留。
7. 完整host.log的字节/tail/markers重计一致。所有场app_not_opened=false、597814 B eval/view=true；809 B系统脚本不算业务成功证据。所有场17条解析诊断、tick_exception_count=0；panic=false/没有tick异常不证明parser无错。
8. 10张请求截图及10张part都存在；PNG签名、全部chunk CRC、完整长度及hash核对。尺寸为**2560×1232或2560×1236**，七种不同hash全部实看；part与对应final同hash。它们显示未登录三栏工作台及恢复按钮，任务恢复banner未显示。整张宿主截图和`--size 1280x800`参数不足以签客户区/窄窗/150%通过。
9. 两合法任务原文5/403 B全部未变但被备份为异常；六坏盘35/47/34/420/421/406 B原文及recover精确。额外既有备份场41 B坏盘与403 B旧recover分别保全。九个有tasks输入的场最终pending均false，七坏场why空；没有真实普通业务写或数据丢失的观察，不把保护失效推演写成已经破坏原文。
10. 空、整数、小数提醒加载成立；六非法类型原文/recover精确，内存列表空、pending/dirty=true。仅保持原R03 schema缺陷关闭，不代提醒发出、去重、跳回、恢复成功或后台常驻。

## 上轮缺陷闭合表

|编号|本轮状态|精确范围|
|---|---|---|
|B-M7-01|**OPEN / P1 / 必修**|同冻结候选每场17解析诊断，未新冻结修复|
|R-M7-02|**PARTIAL / OPEN / P1 / 必修**|原文、recover、旧备份和按钮位置子项通过；合法误拒、pending失效、准确错误/可信可执行恢复未闭合|
|R-M7-03|CLOSED保持|空/整数/小数与六类型反例本轮复验通过；完整跟进NOT_RUN|
|R-M7-01|CLOSED保持|空输入提示复验；可信非空登录/清空完整行为未跑|
|D-M7-01/02/03、A-M7-03|历史精确关闭范围保留|本地准入、资源清单、原编号语义和私钥历史状态核对；不代完整业务/媒体/外部完成|
|A-M7-01/02|P2建议继续挂账|README旧入口/旧完成表述、placeholder/完整演示欠交；不作为FAIL依据|

## 必修缺陷及具体修复指令

### B-M7-01 — P1 / 必修：被冻结候选仍有解析回归

- **文件与行**：runtime/optimization/2026-10-09/M7/r8/release/octosense-repair-0.1.0-g/main.splash:1197、1202、1207、1211 的`{ok:…}`，1285、1311、1389 的`.ok`比较；共同parser1184开始。**这些不是当前701133 B工作树行号**。宿主包装源码位置分别1200/1205/1210/1214/1288/1314/1392，比原文件相应语句大3行。
- **触发**：R的cold_absent、legal_empty、legal_record从新Store冷启；其余七场也复现，不依赖登录、原数据或模型。
- **实际 / 预期**：每場17条Expected expression/Parser stuck，栈含OkTestExpr，停在`ok:`冒号或`.ok`后的比较；真实工作台有渲染。预期固定宿主同字节解析诊断0并正常加载/恢复，不能只检查rc0/view=true。
- **根因**：新增`ok`协议与固定宿主语法冲突是源码/日志对应的强推断；未做独立语法微验证，不声称已证明一般保留字规则。当前新工作树改动未被交接为M7候选，不能关闭本缺陷。
- **影响**：核心加载/恢复分支不可依赖，违反冷启0诊断硬门槛，阻断本地发布准备；G0-A、硬1/2/4、P01/P05受影响。
- **证据**：H/legal_empty/logs/host.log:44–60、legal_record/logs/host.log:43–59；十场完整日志及E/audit各error_lines，共170条。
- **具体改法**：构建方先在候选责任范围内采用固定宿主实证可用的返回协议（如success），同步全部三调用点；不能删严格validator/保护。若修复已在当前累计源码，明确差异后**重冻结新M7 candidate/digest及清单/运输/材料**，不能递交旧0.1.0-g。只通过合规harness确认冷启0诊断/持续渲染，不自行启动宿主。
- **验证方式**：至少无tasks、合法[]、完整DRAFT三正例及本轮坏盘场在最终新冻结包上诊断0。合法两例不得误生成recover；空登录提示与提醒类型矩阵不回归。模型请求对此无帮助，可保持0。

### R-M7-02 — P1 / 必修：合法任务误拒，坏盘pending和可执行恢复不成立

- **文件与行**：同一冻结main.splash:1148–1175成员validator、1184–1211共同parser、1215–1241坏盘标记、1253–1320显式恢复、1388–1394加载、11035–11043 UI入口；普通写守卫932、4336、6941。行号以F/E源码副本为准。
- **触发**：legal_empty/record合法对照；bad_object/truncated/member/trailing四原反例；bad_closed_junk、bad_task_boolean直接回归；bad_preserve_backup既有合法备份保留。
- **实际 / 预期**：合法两场仍生成tasks.recover，status“任务文件异常（）”；七坏场最终pending=false、why空，UI任务banner空。八场新recover与原文精确，额外场旧recover未覆盖、corrupt.latest精确。bad_object/member的tap没有明确恢复/身份拒绝回执或recover.bak；不能说两分支已成功/已拒绝。预期合法事实源正常加载；坏盘保护持续、错误准确可见、普通写拒绝；可信恢复须核身份、验证备份、受控写后严格读回再解锁，失败保留pending。
- **根因**：B01源码解析回归使共同返回及分支结果不可靠；pending实际为何在后续变false仍未知，须在解析修复后查load→初始化→reconcile→refresh/save/tick。代码里有`STATE.tasks_pending_recovery=true`不能代最终保持。首尾[]完整性及旧任务数值探针仍属本缺陷受影响回归，本轮有解析错，无法单独裁决其内部消费/类型语义。
- **影响**：合法输入被误拒，坏盘普通写护栏前提消失，核心失败恢复没有成立，阻断同版本本地发布准备；G0-C、U08、硬1/2/4、P01/P05受影响。未观察真实业务写或丢数据，不夸大为已发生破坏。
- **证据**：H合法两场state/tasks/recover；七bad场state.tasks_pending_recovery=false；bad_preserve_backup旧recover403 B、坏盘/latest41 B；真实PNG；E/audit逐字节和状态核对。state与status矛盾可直接复现，不借作者声称补证据。
- **具体改法**：先闭合B01，再保证pending/reason不会被后续初始化或偏好加载重置；合法parser结果正常驱动加载；准确任务banner不被提醒状态或空态覆盖。load/keep/overwrite三处保留同一完整严格判据，任务version/createdAtMs/updatedAtMs用严格数值判定。仍非法原文keep不得解锁；overwrite必须有效可信主体、备份核实、受控写和严格读回；各失败点保持保护。保留本轮已通过的原文/旧备份策略与现有UI布局，不扩修前序业务。
- **验证方式**：最终新冻结包重跑本轮正反矩阵，合法不误备份、所有坏盘pending=true且原因可见、原文/旧recover/latest正确。再通过被允许的真实输入完成隔离合成账号登录，核非法keep持续保护、修复合法原文后keep加载、overwrite备份/读回后解锁、普通写在恢复前拒绝，以及备份/写/读回失败和同Store真实进程重开。当前不可表达步骤如实列BLOCKED，不伪session/回执、不手工改任务状态制造成功。

## 建议与未执行边界

- **A-M7-01 / P2**：app/README.md:5的旧入口/旧关闭叙述、:7的完整闭环表述仍无本候选全链依据。建议明确历史和当前冻结入口，按实际能力改描述；保留挂账，不单独判FAIL。
- **A-M7-02 / P2**：F/listing.json仍引用1×1 placeholder。H本轮真实图已经存在，但未纳入冻结listing，完整2–3分钟演示/独立理解核验未做。建议补媒体后重新冻结及复验受影响项；不代外部发布，不拿旧B完成截图填本候选完成态。
- **BLOCKED只限确实不可表达动作**：本轮用户只允许宿主内置test-action/capture、禁止系统自动化；固定宿主已有type/key不实现的独立历史记录，无法完成可信非空键入和完整键盘主流程。当前schema/内置动作也没有“同Store业务进程重开”或在指定提交点精确替换/拒写/读回的原语；150%文字设置未有可用动作。解阻需提供在同一隔离harness中可表达这些步骤的受控接口和对应证据，**无需因技术接口缺口重开身份/provider授权**。
- 可信业务/模型/实际附件/官方scan/完整演示等本轮没有执行，记NOT_RUN；不是因为agent内rc71/pgrep rc3而BLOCKED。当前harness没有ABORT，禁止把运行环境当失败替身。
- 本轮taps没有unknown，三个位置尝试不等于三个业务动作。只有legal_empty显示明确空输入提示；恢复tap没有确切回执，实际恢复NOT_RUN。

## 全部64项验收登记

原编号、定义及历史来源保留。表中的结果是**完整用例**或已观察到足以否定该要求的反例；离线/加载/类型/渲染PASS只列子项，不代全项。未执行完整业务不得继承作者或前序候选PASS。U11依原“滚动/输入/面板/动效”定义校准为NOT_RUN，r10的FAIL历史完整保存；这不关闭B01/R02。详细定义来源/旧状态/当前范围另见E/final-acceptance-64-r11.json。

|编号|原定义|本轮结果|实际范围与证据|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|FAIL|FAIL：最终同字节10场均17条解析诊断；实际打开及渲染子项PASS。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|NOT_RUN：未运行可信非空登录、每查每写核权及独立会话；空输入提示和actor=null仅子项PASS。|
|G0-C|唯一事实源、原子一致性、并发与恢复|FAIL|FAIL：合法任务误拒、七坏盘pending=false；原文/旧备份保全子项PASS；原子/并发完整流程未跑。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|NOT_RUN：未执行真实附件写入/读回/归属/故障；诊断I/O探针不代附件。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|NOT_RUN：最终provider禁用，10场needs_model=false，0真实模型/无代理stats；未验证系统助手能力。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|NOT_RUN：空/整数/小数及六类型提醒加载子项PASS；真实通知/恢复/去重/视图/常驻未跑。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|NOT_RUN|NOT_RUN：加载schema子项PASS；真实业务进程重开、通知去重、改约取消旧作业未执行，具体时序动作BLOCKED。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|NOT_RUN：同候选原生打开/渲染PASS子项；未执行可信业务操作/权威回执/同Store重开。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|NOT_RUN：未执行该原定义的可信完整业务流程；不由诊断seed、静态源码或前序/作者结果转移PASS。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|FAIL：任务损坏错误banner空、保护状态失效，实际安全恢复出口未成立；按钮位置子项PASS。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|NOT_RUN|NOT_RUN：PNG为2560×1232/1236宿主全屏；客户区、窄窗、150%完整实测未执行；文字设置动作BLOCKED。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|BLOCKED：用户仅允许内置test-action/capture；固定宿主type/key不实现，禁止系统自动化，无法用许可动作完成键盘主流程；对比/颜色完整要求也未跑。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|NOT_RUN|NOT_RUN：原定义的滚动/输入/面板/动效完整流程未执行；r10 FAIL历史保留，B01/R02仍OPEN，并非关闭缺陷。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|NOT_RUN：没有本候选2–3分钟完整演示及独立理解核验，不用10场加载截图替代。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|FAIL：同候选独立冷启加载/任务恢复失败；成功/退回链及真实业务进程重开NOT_RUN。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|NOT_RUN|NOT_RUN：冻结/dirty/工具/宿主定位和离线新Store安装子项PASS；完整干净构建与依赖说明未复现；A01 P2挂账。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|NOT_RUN：独立stamp/check/verify/install_staged子项PASS；官方实际scan审阅未执行，不将rc0代审阅通过。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|NOT_RUN：材料摘要一致、真实原生帧已核子项；冻结listing仍placeholder、完整演示未交，A02 P2挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|FAIL|FAIL：字节清单/运行副本子项PASS；B01/R02两个核心P1未关闭，完整交付未成立。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|NOT_RUN：无本候选公开源码/Hub递交新回执，无外部动作，不转移历史0.1.0-b记录。|
|P07|维护者商店收录结果|NOT_RUN|NOT_RUN：无本候选商店收录回执，未listing；全局历史台账不改。|
|P08|赛事正式提交入口回执|NOT_RUN|NOT_RUN：无本候选赛事正式入口新回执，未提交；全局历史台账不改。|

完整用例计数：FAIL 5、BLOCKED 1、NOT_RUN 58、PASS 0。多个真实PASS子项在上表之外单独报告，不用子项冒充全用例通过。

## 判定与交接

- **最终结论：FAIL**，精确范围为M7-r8-worktree/0.1.0-g、固定M0/r3宿主的本地发布准备。两个核心P1仍有独立原生反例，无“基本通过”或带条件放行。
- 硬验收1 **FAIL**：解析/任务恢复反例成立，其他完整门槛未执行，不冒充全量通过。
- 硬验收2 **FAIL**：同版本任务加载/恢复失败；完整正常/退回/真实业务重启/模型NOT_RUN。
- 硬验收3 **NOT_RUN（完整）**：候选/运输/清单/隔离秘密子项PASS；截图/演示欠交及A01/A02为P2挂账。
- 硬验收4 **FAIL**：本地离线准入/安装/隔离子项PASS，但独立冷启0解析与核心恢复失败，官方scan未执行。
- 硬验收5 **PASS（状态区分）**：本地准备FAIL；**P06公开源码/Hub递交、P07商店收录、P08赛事回执均NOT_RUN**，没有本候选实际新回执。未查询/操作外部平台，不迁移历史0.1.0-b递交记录，不改external_delivery历史状态。
- 受影响回归：空输入登录与R03提醒类型子项通过；合法/坏任务矩阵及旧recover保留真实复验，保护仍失败；M6持续建议/三角色全业务等不在本次扩审范围，挂账结论保留。
- 更新位置：本报告、GATES.json中M7的status/review_report及本轮审查字段。旧r10来源在E/gates-before.json和review_history/逐项previous_review保留；原docs/build-loop/ACCEPTANCE.json保持字节不变，不把历史后端结论覆盖成原生PASS。
- 是否允许下一模块：**否**，本次不执行下一模块。留在M7，构建方只修B-M7-01、R-M7-02并交新冻结候选及合规harness冷启日志/截图，不撤他人改动，不为修复发散新功能。
- **NEEDS_ABRAM=no**：本地catalog/install_staged可行，身份/provider/隔离离线签名已有授权；无欠费、无公开发布申请。剩余为技术/证据缺口，不把它们转成授权阻塞。

STATUS=FAIL
NEEDS_ABRAM=no
