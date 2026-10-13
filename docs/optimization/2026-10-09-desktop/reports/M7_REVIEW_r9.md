# M7 独立 Review r9

**最终结论：FAIL。必修仍为 R-M7-02、R-M7-03。** 独立原生运行确认：截断、id-only、尾随垃圾任务未进入恢复保护；布尔和数字字符串到期时间被加载为 ACTIVE 提醒。非法任务顶层虽然保护成功，实际截图中恢复说明和动作仍不在可见区域。解析/渲染、空输入登录、包运输、隔离与回收通过，不把 CLEAN 当作功能通过。

- 审查者 / 日期：当前 Codex 主会话唯一独立审查者，2026-10-12，Asia/Shanghai；没有子代理或 Kimi 参与审查。
- 候选 / base：`M7-r7-worktree / M7-r6-worktree`，版本 **0.1.0-f**；按明确交接的 GATES、实施 r7、CANDIDATE定位，不按mtime选版。首次跳过构建没有生成新M7候选。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；未提交源码由作者dirty.diff、E/scoped-dirty.diff、双源码副本及摘要定位，HEAD单独不能复构。
- 冻结包：`runtime/optimization/2026-10-09/M7/r7/release/octosense-repair-0.1.0-f/`；digest=`9e1f7aec09785858c744272048afd786c02dee05c1a29aa3838cca8db05ed5cf`；主源 **532303 B**、SHA256=`7b82c1313dcf14379942f01453784f44eb70321257d61a9214fc09d39173e23c`。
- **当前工作树不是被审发布包**：主源596445 B、SHA256=`d98a32720c1731fa3deb54495aec15609b545d0374c78eea8c51df3f9a084b77`，对应M6-r8；已保存2902行unified diff，不是2902行改动代码。该源码严格提醒门禁等改进未进入M7-r7，本轮不代签其发布准备。
- 作者报告：`reports/M7_IMPLEMENTATION_r7.md`；清单：`runtime/optimization/2026-10-09/M7/r7/CANDIDATE.json`；上一轮审查：`M7_REVIEW_r8.md`。
- 前置：**M6=FAIL / M6-r8-worktree / M6_REVIEW_r10.md**，无已接受M6 PASS。按用户前序挂账裁决继续本模块局部审查，不修M6、不代签前置。FAIL依据是本轮M7独立核心反例，不是建议或挂账本身。
- 快照：第1段保护42文件及76 seed文件全部未变；候选、工作树、材料、宿主、harness/schema/profile、门禁/原台账均一致。门禁写后另核非门禁快照及其他模块不变，见E/final-review-verification-r9.json。
- 实际宿主：项目内M0/r3提取OctoSense.app，octosense SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，kernel SHA256=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。固定二进制，不声称未知上游可重建。
- 原生执行：沙箱外驱动harness，**14:17:11–14:19:33 +08:00**；8场全部quit_http/host rc0/CLEAN，无ABORT。审查者没有自行启动launcher、sandbox-exec/pgrep、--help、系统UI自动化。
- 模型：候选enabled=false、caps storage；8场needs_model=false，模型请求 **0**，无代理/stat/endpoint/MM_KEY注入，无402/余额/欠费证据。provider来源已有授权，不另列NEEDS_ABRAM。
- 已阅读：第1段CONTEXT、实际AGENTS/00/01/02/M7/04、r8缺陷、r7交接/源码/证据；本段完整summary/result/profile/probes/MANIFEST、host.log/denials、实际运行包和隔离业务盘。16张PNG核摘要/CRC/长度；8种不同字节画面全部实际查看，其余同字节。
- 已运行：第1段独立离线stamp/check/catalog verify/official install_staged/Store rebuild/may_run；外部驱动8场；本段只读证据审计命令 `python3 -B runtime/optimization/2026-10-09/M7/native/review_r1_0937/audit_phase2_r9.py` rc0，**8456项证据一致性检查、0失败，不是8456个业务测试**。
- 未运行：可信成功/错误口令登录、三角色命令及查询核权、权威动作回执、正常/退回完整链、真实附件/模型、恢复按钮实际点击与故障注入、同Store业务重开、150%/完整键盘、官方scan及完整演示。NOT_RUN/BLOCKED边界如下表，不用作者声明代替。
- 安全：显式材料读写与产物仅在项目内；没有访问原账号/安装/host-data、明文凭据/模型密钥、外部memory，没有任何外部发布/签名/listing、push、Issue/评论、消息、部署或计费变更。本轮私钥生成0；作者keys目录仍空，沿历史删除证据，不伪造本轮删除事件。
- 置信度：版本/隔离/所见UI、损坏任务漏门禁、bool/string提醒误接受 **高**；宿主parse内部值和转换细节、完整业务/模型效果 **未知**。当前工具不能核验/切换主会话Router/指定模型，也不能取得自身createdAt设置标题；未冒称完成。

## 证据索引

- **H**=`runtime/optimization/2026-10-09/M7/native-runs/review_r1_0937_REQUEST_review_r1_0937/`，审查独立请求的驱动原始证据，未修改。
- **E**=`runtime/optimization/2026-10-09/M7/native/review_r1_0937/`，双源/差异/离线准入、seed、审计、64项表及门禁历史快照。
- **R**=`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r1_0937.json`，SHA256=`eb172639b7c8dd5020b71e8d9e6f8f052d622f620a5ae75a1133e5a967faf52c`。
- **N**=`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r1_0937.md`，第1段原笔记不回改成最终结论。
- **A**=E/`native-evidence-audit.json`；当前64项=E/`final-acceptance-64-r9.json`。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本/差异/前置|交接交叉定位，重算冻结/工作树/宿主摘要|明确候选，前置如实|冻结r7明确，工作树M6-r8另存；M6 FAIL挂账|定位PASS；前置未PASS|N/E差异与phase1-audit|
|真实加载同包|逐比installed/mirror/唯一.running及manifest|实际跑冻结候选|每场7运输文件精确同字节，6非manifest资源同冻结|PASS|H实际副本、A|
|证据完整|重算MANIFEST、request/summary/result/capture|无漏列/篡改|1094/1094完整匹配，8456检查0失败|PASS证据子项|H/MANIFEST、A|
|隔离与回收|重建profile、禁读/写probe、PGID/writes/denials|全部场内写、无残留|8/8 probes true、pre/post NONE、PGID_after=[]、CLEAN|PASS|H各result/profile/denials|
|冷启/空输入|新空盘，内置tap登录/清空/再登录|0解析、可见界面/明确空输入提示|8场532303 B view=true；空输入PNG提示“请输入账号ID与口令”|PASS子项；R01保持CLOSED|cold_empty_login PNG/log|
|合法空任务/提醒|[]及空follow_ups冷启|不误拒|pending=false，无备份、无错误|PASS加载子项|cold_empty_login盘/state|
|完整结构/合法数字控制|合成DRAFT、未来due_ms数值|不误判损坏|完整任务盘保全、UI有当前任务不可见分支；数值提醒恢复精确、pending=false|PASS有限加载子项；可信业务NOT_RUN|valid_load_controls|
|非法任务顶层|新顶层对象冷启|保护/待恢复及可见出口|原文/recover精确、pending=true；截图无恢复说明/动作|保护PASS；可见恢复FAIL R02|bad_top_visible|
|任务截断/残缺/尾随|3个独立坏盘|整份拒绝保护，不能假就绪|pending=false、status准备就绪、无备份；截断/id-only保留初始化|FAIL R02|cut/id_only/trailing盘/PNG|
|提醒strict类型|同numeric控制比bool true及数字字符串|非数值整份拒|bool/string均载入ACTIVE，pending=false，无备份|FAIL R03|boolean_due_true/string_due_digits|
|真实恢复操作/失败|核请求/实际数据与UI|两分支读回、失败不解锁|没有实际点击/注入/重开|NOT_RUN；精确故障/重开步骤BLOCKED|R/schema/盘|
|完整命令/权限/模型|可信三角色/模型/权威回执|真实闭环|均未执行，actor=null、无新业务回执、模型0|NOT_RUN；获准文本入口BLOCKED|全部state/模型字段|
|媒体/过期完成态|指纹、listing/README、当前PNG|同版本、无冒称能力|11指纹一致；placeholder/旧入口/旧话术建议挂账，完整演示欠|子项PASS；完整媒体NOT_RUN|N、E/phase1-audit；A01/02|
|本地发布准备|准入、安装及独立核心复验|可靠候选|离线路线PASS；原生核心R02/R03失败|FAIL|本报告|
|外部状态|只读该候选回执材料|状态分开，无回执不完成|没有本候选发布/赛事/收录回执，无外部动作|状态分离PASS；P06/07/08 NOT_RUN|review_summary|

### 原生证据审计细节

1. embedded request与R全等，summary场景顺序/用途/命令/时间/result逐项匹配；harness/template与第1段摘要一致；MANIFEST1094项无重复、漏列、错hash或越界路径。
2. 8 profile按记录run目录、控制口、原HOME字符串和冻结template重建到同字节。probes apply rc0；场外写被拒、created=false；secrets/明文credentials及~/.codex/~/.cc-switch/~/.ssh五禁读均拒。审查者只读这些拒绝记录，不访问禁区。
3. HOME/app-data/log/cache/tmp/XDG/Metal等env全部位于本场新目录；pre/post均rc1/class NONE/out err空；quit_http=ok、host rc0、PGID_after空；wall16.24–16.33秒。原HOME mtime前后相同、Library扫描空是驱动观察，不是审查者自己扫描项目外。
4. writes每项唯一、排序、存在且在本场内；bad_top118项、其余117项，未达400截断上限。这是mtime文件清单，不是领域命令数。denials重计吻合：外443、系统Metal缓存、/dev/dtracehelper尝试被拒；拒绝不等于实际越界。宿主news七来源失败，不声称没有尝试网络。
5. 运行PGID快照中cold_empty_login、id_only_task各有一条osascript子进程，没有参数/用途证据；审查者请求无系统自动化，不能据此断言它进行了UI自动化，也不隐瞒该记录。最终这两场PGID全部回收，符合本次指定回收判据。
6. seed manifest与76文件及mirror完全一致；installed/mirror/.running包文件清单和字节同运输包。digest_seen_in_seed=true、digest_seen_in_host_log=false如实保留；版本由实际运行副本精确比对，不靠字符串marker。
7. 完整host.log字节数/tail/markers重计一致。每场532303 B业务脚本view=true，另809 B系统窗口不充当业务证明；0解析、0日志runtime诊断/unknown-action/panic。tick_exception_count=0不能证明坏任务已恢复。
8. 16 PNG均2560×1238，签名/CRC/完整长度及captures摘要全核。8种独特hash全部查看，id_only与cut相同、bool与string相同；bad_top和cold的part/final不同，额外实际查看。三种size只是命令参数，不能由相同整屏像素签三个客户区/150%通过。
9. 空控制3/18 B、完整任务388 B、数值提醒166 B均保全；坏顶层36 B精确备份；中文截断52 B、id-only27 B、尾随405 B无备份；bool156 B和数字字符串169 B无备份且进入内存ACTIVE。所有原文未变，不声称数据已经丢失或错误通知已发送。
10. model_proxy/model_proxy_stats均不存在，endpoint/MM_KEY未注入，billing_error无，matches needs_model=false。不存在字段不当代理成功；空输入提示在PNG可见，state.status准备就绪不用于否认auth提示的独立UI事实。

## 上轮缺陷对账

|编号|本轮闭合情况|
|---|---|
|B-M7-01|CLOSED保持：8场原生解析清零、工作台可见|
|D-M7-01/02/03、A-M7-03|原关闭准入/指纹子项保持；无新私钥，作者keys仍空|
|R-M7-01|CLOSED保持原控件读取异常：实际空输入提示成立；可信成功登录/非空清空未执行|
|R-M7-02|**PARTIAL / OPEN / P1**：非法顶层保护通过；中文截断/id-only/尾随垃圾漏恢复，可见出口失败|
|R-M7-03|**PARTIAL / OPEN / P1**：合法空/数字加载通过；bool及数字字符串误接受|
|A-M7-01/02|建议继续挂账：README旧入口/历史完成态、placeholder/演示欠交付；不作为FAIL依据|

### R-M7-02 — P1 / 必修：坏任务漏过恢复门禁，核心恢复出口不可见

- **文件与行**：准确行号属于冻结0.1.0-f `main.splash`（E/source.frozen.splash），当前工作树行号不同。成员`:1017–1021`只核id；load`:1163–1180`；recover`:1047–1098`，特别keep`:1068–1073`无条件解锁且仍不加载；UI`:9885–9906/:9932–9937`；普通写保护`:877–884/:2713/:3946`。
- **触发**：新Store放52 B未闭合中文任务、27 B只有id成员、405 B合法结构后TRAILING_M7_0937；另36 B顶层对象对照。全为隔离诊断seed，无可信会话/原业务数据操作。
- **实际/预期**：前三场status准备就绪、pending=false、无recover；截断/id-only图列表“初始化”及详情待选，尾随图有不可见任务分支但没有非法JSON保护。顶层对照pending=true、原文/recover相同，但两张PNG可见区域没有恢复说明或按钮。预期坏JSON/缺运行字段整份拒绝、原文/备份/pending护写、准确可见错误和至少一个安全可继续出口；合法控制不误拒。
- **根因**：宽容parse结果加id最低验证无法保证JSON完整性和运行字段；非滚动左栏把恢复放两个Fill和长控件后。宿主parse实际内部内容/刷新停留执行点未知，不编造；keep分支源码直接解除门禁而不加载合法事实源，实际点击未跑，作为原R02最小修复依赖指出。
- **影响**：核心加载/失败恢复不可靠，界面不能按真实故障继续；硬1/2/4、G0-C、U08/09/11、P01/05受影响。原文保全不等于恢复成功，未发生实际丢数据。
- **证据**：H/cut_unicode_tasks、id_only_task、trailing_task_junk的tasks/state/无recover/PNG/log，bad_top_visible原文/recover及两PNG；A fixtures/state，N与E固定源。日志业务eval532303 B，无解析/runtime诊断，不能以0错误掩盖漏分类。
- **具体改法**：只修原R02。采用固定宿主验证过的严格完整JSON/数组/运行必需字段检查，load和受控覆盖共用，不能只加首尾括号/标记特判。原文+备份读回+普通三写门禁保留；keep若不产生可用合法事实源则不能无条件解锁，或明确备份后新工作副本并核事实源。把错误和至少一个安全恢复动作放真实可见区或可实测滚动容器，不增加美化范围。修当前累计源码后**交接新的M7冻结包和材料**，不能继续递交旧532303 B包。
- **验证方式**：新M7 candidate/digest，harness合法空/完整任务及四坏JSON正反例；核准确保护/pending、0循环、真实可见可点击出口；保留/覆盖两分支写后权威读回。备份/写盘/读回失败保持未决，同Store重开核恢复。现白名单不能表达者列具体缺口，不伪造成功回执或业务状态。

### R-M7-03 — P1 / 必修：宽容数值探针接受bool和数字字符串

- **文件与行**：冻结`main.splash:1007–1014`，特别`:1011–1012`；字段`:2175–2176`；共用schema`:2185–2195`；load`:2211–2265`；recover`:2273–2335`。
- **触发**：相同合法字段下仅due_ms分别为true、字符串"4102444800000"，与数字4102444800000对照。task_id为DIAGNOSTIC-NO-SUCH-TASK，仅schema测试，不发送实际通知。
- **实际/预期**：bool/string两场m6_follow_ups保留原类型完整进入ACTIVE、pending=false/status准备就绪，无recover。预期非严格数值整份拒绝，原文/recover一致且pending=true；空/合法数字正常加载。
- **根因**：`v-v==0`不是该固定宿主的严格类型检测；两种误接受已独立实证。VM内部转换细节未知，不借其他语言规则解释。load/recover共用错误探针并不证明validator正确。
- **影响**：非法到期时间进入提醒状态，恢复前提不可靠；硬1/2、G0-F、T23、P01/05。未实际触发发送，不把潜在错误提醒说成已发送。
- **证据**：H/boolean_due_true及string_due_digits原文/state/无recover、合法控制盘/state，A。bool/string同图不能区分内存类型，采用真实盘/state。
- **具体改法**：只修R03。把当前累计源码已存在且M6-r8实测过的严格数值门禁纳入**新M7候选**并复验；不以算术探针为唯一判据，不退回未经验证typeof假设；load/recover共用严格校验，原文/备份/pending护写保持。新包/清单/材料与新digest同步，不将M6候选PASS子项转移给旧M7包。
- **验证方式**：空/整数/小数数值正例和true/false/数字字符串/对象/数组/null反例整份加载对照；核权威原文/备份/内存pending；恢复与写后schema读回。用户授权的MiniMax不用于替代本类型实证。

## 全部既有验收逐项表

64项原定义/历史来源保留。PASS仅已执行明确范围，FAIL来自本轮核心前提反例；无可信领域操作的完整用例记NOT_RUN，不从旧后端/作者/其他候选转移通过。

|编号|既有定义|本候选结论|实际范围/证据|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|PASS|同digest离线准入/安装/Store重建及8场固定宿主运行字节一致，0解析、真实工作台渲染；仅启动与包子项。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|真实空输入提示PASS，R01原异常关闭；可信成功/错误口令、会话与每写/查询核权未执行。|
|G0-C|唯一事实源、原子一致性、并发与恢复|FAIL|R02中文截断/id-only/尾随垃圾漏保护，pending=false、无备份；坏顶层保护PASS。并发/领域原子提交未测。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|真实附件选择/写入/回读/轮次归属与失败恢复未执行；隔离PASS不能替代此项。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|enabled=false/storage-only；8场needs_model=false，模型0，无代理stat/endpoint/MM_KEY，实际助手/模型门槛未执行。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|FAIL|R03bool及数字字符串due_ms被接受为ACTIVE；合法空/数值加载PASS子项，通知/去重/跳回未测。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|FAIL|提醒恢复strict schema前提R03实测FAIL；合法数值加载子项PASS。同Store业务重启/通知去重/旧约失效未运行。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|同候选原生冷启/加载/空输入实际执行；没有可信主体业务操作、权威回读和业务重开，不签完整用例。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|本候选模型禁用/storage-only，needs_model=false，模型0；对应真实模型/失败/迟到/依据/白名单或可重复链未执行。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|未登录空态可见；真实三角色待办/阶段/下一处理人未执行。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|本轮仅核R02/R03及直接回归；该定义要求的可信领域操作/权威回执或完整UI链未独立执行，不转移历史或其他候选PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|原文保留子项PASS，R02准确恢复前提FAIL；重复点击业务提交/响应丢失/版本冲突/离线未执行。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|R02坏JSON漏恢复，正确pending的顶层反例也没有可见错误/安全出口；其他附件/过期建议场景未执行。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|FAIL|真实PNG恢复说明/动作在可见区外；3种size均整屏2560x1238，不能签三客户区/150%通过。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|固定宿主内置type/key实际unknown；当前禁止系统UI自动化，schema的ui_actions依赖禁止路径，完整键盘/焦点未覆盖；需合规内置输入。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|FAIL|登录空输入子项PASS；坏任务初始化/假就绪和不可见恢复R02实际FAIL；完整滚动/文字输入/切面板未测。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|没有本候选2-3分钟真实全链演示和独立理解核验；本轮PNG不可代完整演示。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|同digest独立失败恢复R02/R03实际FAIL；正常/退回可信业务链及业务同Store重开未测。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|NOT_RUN|双源/dirty/固定工具与宿主、独立准入及干净原生启动子项PASS；完整干净构建/说明复跑未执行，旧README建议挂账。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|独立stamp/check/verify/install_staged/may_run PASS子项；官方scan未执行，独立功能审阅FAIL，不以check rc0代签。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|16张独立PNG同候选且摘要/CRC/长度合格，8种实看；完整演示和全部媒体/来源/隐私/许可验收未执行，placeholder建议挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|FAIL|运行包/11材料指纹子项PASS，工作树另候选已定位；R02/R03必修未关闭。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|本候选无固定公开源码/Hub递交回执；未执行外部动作，不迁移历史0.1.0-b结果。|
|P07|维护者商店收录结果|NOT_RUN|本候选无维护者商店收录回执，未listing；原全局历史状态不改。|
|P08|赛事正式提交入口回执|NOT_RUN|本候选无赛事正式入口回执，未提交；原全局历史状态不改。|

## 硬验收与最终判定

|硬验收|结论|说明|
|---|---|---|
|1 同候选必需门槛实证，不冒充PASS|FAIL|R02/R03核心反例失败；完整T/U/业务/模型未测逐项保留|
|2 正常/退回/失败恢复/重启/真实模型同候选|FAIL|失败恢复/非法提醒加载未通过；完整链、业务重启/模型未执行|
|3 根包/秘密排除、源码包媒体描述一致|NOT_RUN|实际运输字节/11指纹/当前外置PNG子项PASS；工作树另版本，完整媒体/描述建议挂账|
|4 本地准入、独立审阅、干净启动|FAIL|准入/本地install_staged/冷启PASS；独立核心功能FAIL；官方scan未执行|
|5 本地与发布/赛事/收录分别记实|PASS|本地FAIL；本候选P06/07/08 NOT_RUN，无实际回执不称完成|

- **最终结论：FAIL，必修只有R-M7-02、R-M7-03。** 原编号延续，不新增无关扩审；建议不作为FAIL依据。
- **具体BLOCKED**：本次禁System Events/osascript/辅助功能，固定宿主内置type/key前序实际日志为unknown，schema新增ui_actions需要本次禁止的路径，因此完整可信文本/键盘输入不能覆盖；当前每场新盘和启动前seed不能表达同Store跨进程业务重开、精确提交点故障/迟到交错、150%设置。需要合规宿主内置输入和驱动受控调度。这些步骤单列BLOCKED，未执行的可信业务/模型链NOT_RUN。8场无ABORT，不以agent rc71/rc3阻塞已可执行项。
- **受影响回归**：只核上轮R02/R03、已关冷启/登录和合法数据加载；未签M6/其他前序PASS。旧M7包同字节仍有两核心失败，累计工作树变更已定位，下一次须新M7冻结交接。
- **状态分离**：本地发布准备FAIL；外部发布/Hub递交P06、商店收录P07、赛事正式回执P08均本候选NOT_RUN。无网络查外部或发出材料，不挪用旧0.1.0-b回执；GATES全局external_delivery历史保留。
- **门禁/原台账**：仅更新GATES.M7的status/review_*及reviewed_at；review_report指本r9、review_candidate_id=M7-r7-worktree。旧审查字段追加review_history并保存E/gates-before-review-r9.json。构建字段、其他模块、原ACCEPTANCE.json及全局状态不变，64项本候选明细另存E和M7审查字段。
- **不允许、未执行下一模块。** 由Kimi-K3按两项最小改法修复，保留已关项；先用harness确认冷启0解析/渲染不回归，重新冻结可定位M7包，再交独立Review。
- **NEEDS_ABRAM=no**：本地catalog/install_staged路线可行；身份/provider/隔离离线签名已有授权；本轮0模型请求，无402/欠费，无公开发布需要。剩余是技术修复/合规验证条件。

STATUS=FAIL
NEEDS_ABRAM=no
