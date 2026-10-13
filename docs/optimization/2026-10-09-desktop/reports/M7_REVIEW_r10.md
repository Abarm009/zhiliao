# M7 独立 Review r10

**最终结论：FAIL。必修：B-M7-01（解析错误回归，重新打开）、R-M7-02（合法加载误拒、损坏任务恢复保护不成立）。R-M7-03 的提醒到期时间类型缺陷关闭。** 8 场都 CLEAN，但每场有17条解析诊断；合法空任务也生成损坏备份，全部6个坏任务场景最终 `tasks_pending_recovery=false`。真实工作台能渲染，不能据此称解析错误清零或恢复成功。

- 审查者 / 日期：当前 Codex 主会话唯一独立审查者，2026-10-12，Asia/Shanghai；没有子代理或 Kimi 参与审查。实际主模型/Router 路由不能通过当前工具确认或切换，不冒称已执行指定路由。自身 createdAt/改标题接口不可用，未以当前日期代替创建时间。
- candidate_id / base：**M7-r8-worktree / M7-r7-worktree**；版本 **0.1.0-g**。由 GATES、实施r8及作者 phase1-audit 三方定位，不按mtime选版。
- 作者报告：`reports/M7_IMPLEMENTATION_r8.md`；清单替代文件：`runtime/optimization/2026-10-09/M7/r8/phase1-audit.json`（作者明确未单独生成 CANDIDATE.json）；前次审查：`M7_REVIEW_r9.md`。
- 冻结目录：`runtime/optimization/2026-10-09/M7/r8/release/octosense-repair-0.1.0-g/`；digest=`e0ee84d8463778bade271acc1a4798e0486bbd15a3c5fc21d6bc16e1cadf89a8`。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`；冻结/当前工作树 main.splash **均597814 B**，SHA256=`3b5001839fda8153d5adfeba04f11669ccd4e243af39c2dbd8c8e6d7a89d2852`。未提交差异由作者dirty.diff、E/scoped-dirty.diff、E/r7-to-r8-source.diff、E/source.frozen.splash和资源指纹定位，不能只凭HEAD复构。
- 前置：**M6 FAIL / M6-r8-worktree / M6_REVIEW_r10.md**；无已接受M6 PASS。依据用户前序挂账裁决继续局部M7审查，不修M6、不代签前置；本次FAIL来自当前候选的真实核心反例，不是建议项或前序挂账。
- 宿主：项目内 M0/r3 提取 OctoSense.app；octosense SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；kernel SHA256=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。来源说明与固定二进制摘要已核，不声称未知上游完全可重建。
- 快照：两阶段之间候选、业务源、宿主、材料、schema/profile、GATES/台账均未变。**48个保护文件中仅harness源码发生并发变化**：第1段/本次实际执行SHA=`c46ba53a…`；当前SHA=`d597d24a…`。项目内 `driver/harness/native_harness.py.bak-quote-batch-20261012` 与实际执行摘要完整匹配；本轮按这个确切旧源重建profile/命令/记录。新源改为32场分批及代理profile拼接，不冒称本轮用了新版，未回滚他人修改。
- 原生执行：外部驱动独立请求，**20:08:30–20:12:45 +08:00**，8/8场 CLEAN、quit_http、host rc0，无ABORT。审查者未自行启动launcher、sandbox-exec/pgrep、--help或系统UI自动化。
- 模型：候选 enabled=false / storage-only，8场 needs_model=false，真实MiniMax请求 **0**；无model_proxy/stats、endpoint/MM_KEY注入或欠费证据，不把缺失stats说成成功调用。
- 已读与运行范围：第1段按CONTEXT读取AGENTS/00/01/02/M7/04、r9原缺陷和r8交接；本段全部summary/result/profile/probes、MANIFEST、完整host.log/denials、运行包/业务盘、16张PNG；6种不同摘要画面全部实际查看。已执行第1段独立离线stamp/check/verify/install_staged/Store重建/may_run，本段执行只读证据审计命令 `python3 -B runtime/optimization/2026-10-09/M7/native/review_r2_1957/audit_phase2_r10.py` rc0，**11438项证据一致性检查、0未解释失败，不是11438个业务测试**。harness变更单独记录，不隐瞒初次审计发现的两项摘要差异。
- 未运行：可信成功/错误口令登录、每写/查询核权、完整正常/退回链及权威业务回执、真实附件/模型、合法keep/overwrite两分支、精确备份/写盘/读回故障、同Store业务进程重启、150%/完整键盘、官方scan、完整演示。具体不可表达动作列BLOCKED；其他未执行事项列NOT_RUN，不由作者声称代替。
- 安全审计：第1段初始误读一次项目外memory索引，已在原笔记披露并停止，未用作验收证据；不能声称整个两阶段从未读项目外。本第2段显式读写和产物全部在项目内，未访问原账号明文凭据、secrets、原业务数据或其他项目；未执行公开签名/publish/listing、push、Issue/评论、消息、部署或计费变更。本段无新私钥，作者keys仍空，保留其历史删除记录而不伪造本段删除事件。
- 置信度：候选、隔离、所见UI、解析回归、保护状态失效及提醒类型结果 **高**；解析器内部错误恢复、究竟哪条执行路径使pending回落、合法恢复/完整业务/模型效果 **未知**。`ok`语法冲突的具体机理是日志与源码对应的推断，须用固定宿主微验证确认。

## 证据索引

- **H**=`runtime/optimization/2026-10-09/M7/native-runs/review_r2_1957_REQUEST_review_r2_1957/`：外部驱动原始证据，未修改。
- **E**=`runtime/optimization/2026-10-09/M7/native/review_r2_1957/`：独立离线Store/seed/源码/差异、phase1审计及本段 `native-evidence-audit.json`、`final-acceptance-64-r10.json`、收尾验证。
- **R**=`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r2_1957.json`，SHA256=`c0171c1fcb139ae1c026017e2ce312e3988817f911e737fd9d43135260bc87a5`。
- **N**=`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r2_1957.md`，原第1段笔记保持不回改。
- 作者自测 H/build 同级 `build_r2_0937_REQUEST_build_r8/summary.json` 为18场超旧harness上限导致 ABORT_INVALID_REQUEST；不能当作本候选冷启动已通过。当前驱动上限已由他人调整，该历史ABORT不代表当前独立8场ABORT。

## 必需检查

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本/材料/运行包|交接三方定位，重算冻结/运输/运行副本|同候选同字节|11材料指纹匹配；每场installed/mirror/唯一.running七文件同运输，六非manifest文件同冻结|PASS子项|E/phase1、H副本及审计|
|完整证据|重算MANIFEST、request/result/命令/seed/capture/完整日志|无未解释漏列/篡改|1127/1127摘要匹配，11438检查0未解释失败；harness漂移有确切备份定位|PASS完整性子项|H/MANIFEST、E/audit|
|隔离与回收|核profile及探针、env/writes、PGID和driver观察|场内写、禁读、无残留|8/8 probes true、pre/post NONE、PGID_after=[]、CLEAN|PASS|H各result/profile/denials|
|冷启动/渲染|新空数据及全部诊断seed启动最终包|解析清零、真实工作台|每场17条解析诊断，597814 B view=true，真实工作台仍渲染|解析FAIL B01；渲染PASS|全部host.log，cold_empty PNG|
|空输入登录回归|内置tap登录，查看实际PNG|明确空输入提示、无会话|cold_empty提示“请输入账号ID与口令”；actor=null|PASS子项，R01保持关闭|cold_empty_after.png/state|
|合法空/完整任务|[]及完整DRAFT正例冷启|正常加载，不生成损坏备份|两场都生成精确tasks.recover，空原因错误status；pending=false，界面恢复说明空|FAIL R02|cold_empty/valid_controls盘/state/PNG|
|四个原坏任务|顶层对象、中文截断、id-only、尾随垃圾|原文/备份/pending护写与准确可见错误|四场原文/备份精确保全，但pending=false、reason空；错误未显示|备份PASS；保护/恢复FAIL R02|bad_top_bool/cut_false/id_only_string/trailing_object|
|严格JSON/任务类型回归|首尾[]内部垃圾、version=true|准确拒整份并保持保护|两场同样备份精确但pending=false、reason空；解析回归使细分判据无法单独认定|保护FAIL；细分能力NOT_RUN|closed_junk_array/task_bool_null|
|提醒类型矩阵|空/整数/小数与true/false/数字字符串/对象/数组/null|合法加载、六非法整份拒|空/两数值正常；六非法内存[]、pending/dirty=true、原文/recover精确|PASS原类型缺陷，R03关闭|8场follow_ups原文/备份/state|
|恢复入口/点击|看真实PNG，核tap后state/盘|可见错误及安全出口，点击有明确结果|两任务恢复按钮可见；任务banner空；无恢复回执/拒绝提示、pending早已false；未生成recover.bak|位置子项PASS；实际恢复NOT_RUN，R02未闭合|bad_top_bool/各PNG及state|
|时间线/截图|核两capture及wait动作记录|前后图及延时实际成立|8张before缺失且result如实写false/null；16张after/part存在、有效；7场wait:2实际unknown|缺失前态NOT_RUN；延时动作BLOCKED|captures/完整host.log|
|全链/模型/重启|核操作/授权与回执证据|真实同版本闭环|可信全链、模型、应用重启未执行；Store重建不是业务进程重启|NOT_RUN；仅不可表达步骤BLOCKED|N/R/schema及本报告|
|媒体/历史完成态|核最终listing/旁置材料/README与PNG|材料一致、无旧能力冒称|候选材料明确禁模型/待复核；placeholder1×1，README旧入口/闭环结论继续挂账|指纹PASS；完整媒体NOT_RUN，A01/02建议|冻结材料、app/README.md:5/7|
|本地与外部状态|分别读取该候选实际证据|本地结果不代外部回执|本地准备FAIL；无本候选P06/07/08实际回执，无外部动作|状态区分PASS；外部NOT_RUN|本报告及GATES.review_summary|

### 原始证据核对细节

1. summary嵌入R全等，8场顺序、purpose、size/actions、result和摘要吻合；MANIFEST1127项无重复、漏列、越界或错hash。原始H未改。
2. 使用匹配执行hash的harness备份、固定模板、记录run_dir/控制口和原HOME字符串重建全部profile到同字节；probes apply rc0、场外写拒且created=false、五禁读均拒。审查者只读拒绝记录，不读取禁区。
3. 8场HOME/app-data/log/cache/tmp/XDG/Metal路径都在本场目录；pre/post均rc1/class NONE/out err空；quit_http=ok/host rc0、PGID_after=[]，wall30.20–30.28秒。driver记录原HOME mtime前后相同、Library扫描空；不是审查者自己扫描项目外。
4. writes记录排序、唯一、数量等于实际列长、均在场内且存在、未达到400截断；这是mtime文件清单，不是业务命令数。deny日志全量重计匹配：外443、系统Metal缓存、/dev/dtracehelper尝试被拒；不把拒绝当实际越界，也不说宿主没尝试网络，news七来源实际失败。
5. cold_empty/id_only_string的运行PGID快照各有一条osascript子进程，未记录参数/用途；请求没有系统自动化，不据此推断进行了UI自动化。两场最终均完全回收，该观察不隐瞒。
6. 每场seed与独立原文/Store完全一致，唯一.running与运输七资源完全匹配。digest_seen_in_seed=true、digest_seen_in_host_log=false均如实保留，以实际副本字节确认候选。
7. 完整日志的字节数/markers/tail重计一致；每场597814 B业务脚本view=true，另809 B系统窗口不当业务证明。每场**10条Expected诊断+7条Parser stuck=17条解析诊断**（共136条）；七场另有1条unknown wait。`panic=false`/`tick_exception_count=0`不证明parser无错。
8. 8张before确实不存在，captures的false/null记录正确；16张after与part均2800×1696，PNG签名/全部chunk CRC/完整长度、摘要已核。6种独特摘要全实际看过；part与final不同时也已查看。三种size只是命令参数，不能凭同尺寸整屏图签不同客户区或150%通过。
9. 8份任务原文都未变，tasks.recover逐字节同seed，**连合法3 B空数组与394 B完整任务也被备份为异常**；六坏例26/52/27/411/413/397 B均pending=false。没有实际业务写，没有数据丢失/后续破坏的观察；只能认定保护前提失效。
10. 提醒空18 B、合法两数值317 B正常加载；true/false/string/object/array/null六原文及recover精确，内存列表[]、pending/dirty=true。图中部分状态仍停在初始化或空态，不以PNG代内存类型判断。R03关闭仅限schema误接受，不代通知/去重/跳回或恢复成功。
11. 无model_proxy/stat/endpoint/MM_KEY，和needs_model=false一致。未访问或打印任何实际模型密钥；无402/余额/欠费记录。

## 上轮缺陷对账与本轮必修

|编号|状态|精确范围|
|---|---|---|
|B-M7-01|**REOPENED / P1**|已关解析清零门槛被R02新parser返回/字段语法引入回归；工作台有渲染，不是旧空白症状完全复现|
|D-M7-01/02/03、A-M7-03|关闭子项保持|准入/完整指纹/定义/私钥历史处理一致，不代功能或外部完成|
|R-M7-01|CLOSED保持|空输入提示实际成立；可信登录与非空清空未跑|
|R-M7-02|**PARTIAL / OPEN / P1**|原文/recover保全与按钮可见已有改善；合法任务误拒、坏盘pending失效、准确错误/可执行恢复未成立|
|R-M7-03|**CLOSED原类型缺陷**|新M7冻结包空/整数/小数正例、六非法类型全拒，原bool/string误接关闭；完整跟进门槛NOT_RUN|
|A-M7-01/02|P2建议挂账|README旧入口/完成态、placeholder/完整演示欠交付，不作为本次FAIL理由|

### B-M7-01 — P1 / 必修 / 重新打开：冷启解析清零回归

- **文件/行**：冻结且与工作树同字节 `app/bundle/main.splash:1197/:1202/:1207/:1211` 的 `{ok:…}`返回，及 `:1285/:1311/:1389` 的 `.ok`比较。宿主报源码位置分别1200/1205/1210/1214/1288/1314/1392，比原文件同语句大3行；报告不把宿主包装行号写作原文件行号。实际完整日志从cold_empty/logs/host.log:45开始；其他场也逐条对应。
- **触发**：最终0.1.0-g在新Store仅预置合法 `[]\n`、空提醒后冷启，不依赖登录/原数据/网络。
- **实际/预期**：每场17条Expected/Parser stuck，栈含`OkTestExpr`，分别停在`ok:`冒号和`.ok`后的相等/不等运算。view=true、工作台有渲染，但不能满足0解析门槛；预期固定宿主同字节冷启解析0、合法load和原恢复判据可执行。
- **根因**：新增共同parser对象字段`ok`与实际语法解析冲突的推断有强日志对应；这不是坏JSON内容触发的源解析错。固定宿主对`ok`内部保留/表达式规则尚未独立微验证，不把推断说成已确认通用语言规则。
- **影响**：最终候选加载/恢复判定不可依赖，合法空数据都误报损坏，阻断本地可复现发布准备；G0-A、硬1/2/4、P01/P05受影响。
- **证据**：H全部8个完整host.log（各17诊断）；cold_empty实际PNG、tasks/recover/state；E/audit runtime_errors及源码副本。
- **具体改法**：仅修本次新增函数和三个调用点，优先把返回标志及读取统一改用已存在/已验证的`success`等非冲突字段，或用经固定宿主微验证的其他返回协议；不要只删调用/保护、退回旧宽容parser。先用合规harness确认这种字段语法可执行，再冷启动最终新冻结包到0解析；不要在审查方环境直接启动宿主。
- **验证方式**：新candidate/digest、合法空任务/完整DRAFT正例必须0解析且不标坏、不生成新tasks.recover；8个本轮场景解析清零回归，工作台继续渲染、R01空登录不回归。模型调用无助于此项，保持0请求。

### R-M7-02 — P1 / 必修 / 原编号继续：合法误拒，坏任务恢复保护与准确出口不成立

- **文件/行**：`main.splash:1184–1211`共同parser，`:1388–1394`load分支；`:1234–1247`损坏pending/reason/banner；`:1253–1329`两恢复分支；`:11035–11043`UI依据pending启用。普通写依赖该flag，见`:932/:4336/:6941`。当前冻结源码、工作树及E副本行号相同。
- **触发**：cold_empty合法空任务、valid_controls完整合法DRAFT；原四反例顶层对象/中文截断/id-only/尾随垃圾，再加首尾[]内部垃圾与version=true的直接回归，全为独立新诊断seed。
- **实际/预期**：所有8份原文与recover完全一致；合法两场status却是“任务文件异常（），恢复未决、已拒写”，原因空；所有6坏场最终tasks_pending_recovery=false、reason空。PNG任务banner空，两个任务恢复Chip可见但没有准确任务错误；bad_top_bool两tap未产生recover.bak、明确身份拒绝或恢复回执。预期合法任务正常加载且不误备份；坏盘准确分类、pending持续true、原文/备份保全、普通写守卫成立，错误与可执行安全出口可见，恢复有明确结果。
- **根因**：共同parser的源码解析回归已证实，不能把返回对象及分支执行看作可靠；只生成备份不能证明pending最终保持。**究竟哪条实际路径把flag变false仍未知**，需构建方在修解析后核load→model/forms→bootReconcile→选中→saveState→tick初始化顺序，不能无证据归咎其他模块。首尾检查/旧数值探针风险仍在，但本轮解析失败导致无法单独证明它们的正确性或内部消费语义。
- **影响**：合法事实源误拒；坏盘普通写门禁的前提消失、UI恢复动作在pending=false时只刷新；核心失败恢复未成立。未观察到实际业务写/原文丢失，不把潜在影响说成已破坏数据。G0-C、U08/U11、硬1/2/4、P01/P05受影响。
- **证据**：H八个tasks.json/recover/state与真实PNG；E/audit fixtures逐字节检查；cold_empty/valid_controls status；bad_top_bool没有recover.bak/权威回执。.before不存在，不能虚构点击前后转换；静态UI入口依赖pending的事实已定位。
- **具体改法**：先闭合B01；保留共同严格validator、原文/recover备份读回与三写保护。保证合法返回能驱动TASKS加载，损坏flag/reason不会被初始化/后续刷新或持久偏好覆盖；持久flag与内存/UI需一致。恢复说明不得因空态覆盖；keep对仍非法原文不能解锁，overwrite只有在有效可信身份、备份验证、受控写与严格读回后解除。恢复按原缺陷清单修，不改前序无关功能。共同parser修好后，再核严格完整JSON消费与任务version/createdAtMs/updatedAtMs用严格数值门禁，不能用首尾[]或算术探针代完整性/类型证明。
- **验证方式**：本轮8场原文可直接复用但要新Store/新候选。合法两场不得生成损坏备份；四坏例及首尾[]垃圾/boolean任务字段整份拒绝，pending=true、原因准确可见、无tick循环；普通写在恢复前拒绝。独立合成账号通过真实合规输入登录后，keep非法原文保持保护、修复合法原文后keep加载，overwrite先精确保留备份再写后读回；备份/写/读回失败保持pending，同Store真实业务重开复核。不能表达的具体动作如实BLOCKED，不能用伪session或手改任务状态制造成功。

## 建议挂账与具体未测边界

- **A-M7-01 / P2**：`app/README.md:5`仍指r2/0.1.0-c旧路径与旧关闭叙述，`:7`全闭环表述没有本候选证据。建议交付时明确区分历史/当前入口及实际能力；不据此额外判FAIL。
- **A-M7-02 / P2**：最终listing仍1×1 placeholder；真实截图保存在H但未入冻结listing，2–3分钟完整演示/独立理解核验欠交。候选SOURCES/PRIVACY已披露，不把旧B完成截图或历史模型结论转移。建议准备媒体后重新冻结并复验受影响项，不在本轮顺手美化或发布。
- **请求执行建议**：固定宿主7场将`wait:2`记为unknown，只有最后capture存在；以后单场单capture或采用经实证的内置时序动作，不宣称before/after证据。schema白名单只是批准传参，不保证固定宿主实现。
- **BLOCKED仅具体不可表达步骤**：wait:2延时本轮有实际unknown；非空可信文本/完整键盘的内置type/key上轮已有unknown证据，当前用户禁止System Events；schema没有same-Store业务restart与精确运行中写盘/读回失败调度/150%动作。需要合规驱动/宿主输入、重启和故障调度能力；不是agent沙箱rc71/rc3。未命中tap是NOT_RUN，不能据此判harness ABORT或整个原生环境BLOCKED。
- **NOT_RUN**：成功可信登录/完整业务命令、正常与退回链/权威回执、附件、实际模型、合法恢复两分支、精确故障、业务重启、完整演示/scan及其他完整G0/T/U/P定义。已授权身份来源/provider/离线签名不再列NEEDS_ABRAM；本候选disabled/storage-only也不能借本次0请求代签模型通过。

## 判定

- **最终结论：FAIL**，精确范围为M7-r8-worktree/0.1.0-g本地发布准备；不是旧0.1.0-b送审结果、商店/赛事接纳结论。
- 必修仅B-M7-01解析回归与R-M7-02核心加载/恢复；R-M7-03关闭，A01/02保持建议。不修业务代码、不进入下一模块。
- 本地离线准入/安装/实际包字节/隔离回收PASS子项；原生核心加载/恢复FAIL。发布/Hub递交P06、商店收录P07、赛事回执P08全部NOT_RUN，无本候选实际回执，不迁移旧候选外部状态。
- 受影响回归：冷启动/工作台/R01空输入及R02/R03原反例已在同digest独立运行；完整前序领域能力没有新验收，M6/M5等原结论保持挂账。
- GATES仅更新M7.status与审查字段，review_report指向本报告、review_candidate_id指向r8；r9审查内容追加history，不改其他模块/构建字段/全局external_delivery。原全局ACCEPTANCE不覆写：本轮64项及历史来源保留在本报告/E与M7审查字段，防止用局部schema测试替换完整定义。
- 修复留在M7：先合规harness证明parser字段协议可执行且冷启0错误，再闭合合法/损坏/恢复保护，重冻结新candidate及同步材料后独立复审。无下一模块入口。
- **NEEDS_ABRAM=no**：本地catalog/install_staged可行，身份/provider/离线签名已授权，模型0次无欠费；剩余是源码与验证技术问题，无本轮公开发布请求。

## 全部既有验收逐项表

下面64项保留原定义和r9历史来源。原定义完整用例未执行者不签PASS；局部schema/准入/隔离通过在证据列限定范围，实际核心反例记FAIL。最终整体FAIL由本轮两项P1决定，不因P2建议或前序挂账另扩必修范围。


|编号|既有定义|本候选结论|实际范围/证据|
|---|---|---|---|
| G0-A | 固定版本、原生脚本构建与真实启动 | FAIL | 同digest本地准入/安装和8场.running字节PASS；每场17条解析诊断，0解析运行门槛回归B01；工作台有渲染。 |
| G0-B | 真实可信身份、授权与独立会话 | NOT_RUN | R01空输入登录提示PASS子项；可信成功/错误口令、独立会话和每写/查询核权未执行。 |
| G0-C | 唯一事实源、原子一致性、并发与恢复 | FAIL | R02：合法空/完整任务误标损坏，六坏任务pending=false/reason空；原文/recover保全PASS；并发/领域原子提交未测。 |
| G0-D | 真实附件写入、回读、归属及失败恢复 | NOT_RUN | 真实附件选择/写入/回读/归属及失败恢复未执行；隔离PASS不能代替附件。 |
| G0-E | 系统助手实际调用与能力关闭/拒绝/失败路径 | NOT_RUN | enabled=false/storage-only，needs_model=false、0模型请求，无代理stats或endpoint；真实助手/模型与拒绝路径未执行。 |
| G0-F | 提醒恢复、去重与官方任务意图视图路线 | NOT_RUN | R03严格schema子项PASS并关闭原类型缺陷；空/整数/小数正常、六非法类型整份拒。通知/去重/跳回/跟进恢复未跑。 |
| T01 | 真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T02 | 同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T03 | 无空间/跨项目空间/缺联系人提交失败，草稿内容不丢 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T04 | 两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T05 | 技能不匹配或无项目权限拒绝；经理分配事件记录经理身份 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T06 | 经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T07 | 编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T08 | 机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T09 | 未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T10 | 技工提议不会直接SCHEDULED；非报修人不能确认预约 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T11 | 同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T12 | 改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T13 | 过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T14 | Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T15 | 旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T16 | 提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T17 | SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T18 | 用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T19 | 无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T20 | 技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T21 | 验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T22 | 在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T23 | 进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发 | NOT_RUN | R03 schema门槛关闭；业务进程重启、实际提醒通知、重复作业/改约去重均未执行。 |
| T24 | 直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T25 | 工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T26 | 模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T27 | 未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T28 | 原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T29 | 原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T30 | 自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T31 | 取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T32 | 配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T33 | 同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T34 | 未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T35 | 模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T36 | 假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T37 | 模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| T38 | 保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U01 | 三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U02 | 从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U03 | 同一任务在三角色中事实一致，动作按权限变化，承接者不能自验 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U04 | 当前预约与改约提议清楚区分；冲突、过期不显示成功 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U05 | 设备安装位置与服务空间分开展示，来源和选择依据可读 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U06 | 进度、完工、验收不同；退回后历史与附件保留 | NOT_RUN | 本轮仅核r9原缺陷与直接回归；该完整定义要求的可信领域操作/权威回执或UI全链未执行，不迁移其他候选或作者PASS。 |
| U07 | 重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱 | NOT_RUN | 原文/recover保全子项PASS，但R02 pending失效；重复业务提交、响应丢失、版本冲突/离线完整定义未执行。 |
| U08 | 空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口 | FAIL | R02任务错误banner空、损坏pending=false；按钮位置可见子项PASS，但准确错误和安全可执行恢复不成立。其他附件/过期建议未测。 |
| U09 | 1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖 | NOT_RUN | 任务恢复两按钮本轮真实可见；三种size的PNG均2800x1696整屏，不能据此签不同客户区/150%完整布局通过。 |
| U10 | 键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测 | BLOCKED | 固定宿主内置可信type/key上轮实际unknown，本轮禁止System Events；白名单无法覆盖完整真实键盘/输入/焦点步骤。 |
| U11 | 真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈 | FAIL | R01空输入提示PASS；新包17条解析诊断与R02合法任务误拒/pending失效为真实初始化/恢复反例，完整滚动/输入/面板链未测。 |
| U12 | 独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本 | NOT_RUN | 16张有效PNG/6种摘要实看不能代本候选2–3分钟完整演示与独立理解验收。 |
| P01 | 同一候选版本成功链、退回链及重开恢复独立复跑 | FAIL | 同digest独立加载/恢复R02失败，解析B01回归；可信正常/退回全链、同Store业务重启未跑。 |
| P02 | 完整源码和依赖版本、干净环境启动/构建说明 | NOT_RUN | 完整资源/dirty/固定宿主工具及离线安装定位子项PASS；完整干净构建/说明复现未跑，README建议挂账。 |
| P03 | 最终包准入check及实际scan审阅通过 | NOT_RUN | 独立stamp/check/verify/install_staged/may_run子项PASS；官方scan未执行，独立功能审阅FAIL。 |
| P04 | 真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料 | NOT_RUN | 11材料指纹子项PASS、8张after+8part有效同候选且6种实际查看；before缺失，listing仍placeholder，完整演示未交。 |
| P05 | 源码与包摘要一致，全部必需缺陷关闭，交付清单齐全 | FAIL | 源码/冻结/实际运行资源及指纹PASS子项；B01/R02必修未关闭，不能完整发布准备放行。 |
| P06 | 固定公开源码与Hub Issue实际递交回执 | NOT_RUN | 本候选无固定公开源码/Hub递交新回执；没有外部动作，不迁移历史0.1.0-b回执。 |
| P07 | 维护者商店收录结果 | NOT_RUN | 本候选无维护者商店收录回执，无listing；全局历史状态不改。 |
| P08 | 赛事正式提交入口回执 | NOT_RUN | 本候选无赛事正式入口新回执，无提交；全局历史状态不改。 |

STATUS=FAIL
NEEDS_ABRAM=no
