# M7 独立 Review r12

**最终结论：FAIL。唯一仍未闭合的核心必修为 R-M7-02。B-M7-01 的解析回归已关闭。** 新冻结候选的15场独立原生运行均CLEAN、完整host.log的[E]均为0，但两个“合法任务数组后接垃圾、末尾仍为`]`”场景被误接受，`tasks_pending_recovery=false`，原因空、任务恢复备份不存在。坏盘没有进入恢复保护，不能作为可复现的本地发布候选放行。

- 审查者 / 日期：当前Codex主会话唯一审查者，2026-10-13，Asia/Shanghai；无子代理。当前工具不能核验/切换主会话Router/gpt-6.1-sol，未声称切换；没有自身createdAt/标题接口，未用当前日期代替创建时间。
- candidate_id / base：**M7-r9-worktree / M7-r8-worktree / 0.1.0-h**。用户给出的build_r2_0002_REQUEST_build_r9、GATES候选、M7_IMPLEMENTATION_r9、r9/phase1-audit共同定位，不按mtime选候选。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r9.md`。上一轮独立报告M7_REVIEW_r11.md；本轮仅核原缺陷及受影响回归。
- 冻结包 **F**：`runtime/optimization/2026-10-09/M7/r9/release/octosense-repair-0.1.0-h/`，digest=`4c2bb0d3618afea78801ea2764fcc15918f0e88fb5860e3d3f2ca9225afca72f`；main.splash **702301 B**，SHA256=`f7afc63256f386633f2f03c0aa4a5f464175a9f43dd3ca4fe86f2b3798b7e429`。HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty差异、相关未跟踪包源摘要另存，不能只用HEAD定位。
- 前置：M6仍为 **FAIL / M6-r10-worktree / M6_REVIEW_r12.md**，没有已接受的M6 PASS。依本次挂账裁决继续局部审查，不代签、不修M6；本次FAIL来自当前M7自身核心反例，不由前序挂账/P2建议判FAIL。
- 宿主：项目内M0/r3提取OctoSense.app；octosense SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；octos-kernel SHA256=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。未外推未知上游可重建性。
- 原生执行：外部驱动 **08:24:18–08:29:27 +08:00**，15场、2批、15/15 CLEAN/quit_http/host rc0，无ABORT。审查者未自行启动launcher、harness、sandbox-exec、pgrep或系统自动化。
- 快照：第1段至第2段，**37个保护文件和159个生成输入文件无漂移**；当前工作树main与冻结main相同；冻结七文件、签名运输、新Store、各场唯一.running副本一致。模型配置是冻结的禁用配置，不能继承工作树或历史候选能力。
- 已读范围：第1段CONTEXT/AGENTS/00/01/02/M7/04、r9交接、r11原缺陷与相关源码/材料；第2段全部summary/result/profile/probes、MANIFEST、完整host.log/denials、实际包/seed/权威盘与PNG。原验收编号/定义由上一轮64项来源及原ACCEPTANCE校准，未删减。
- 实际执行：第1段独立hub stamp/check/verify及官方install_staged/Store重建/may_run；第2段独立只读审计脚本rc0，**12220项证据一致性检查、0不一致**，不是12220个业务用例。2124个MANIFEST文件全部重算；请求16张capture，实际15张，全部摘要/PNG CRC核对；7种不同摘要画面均已目视查看，同摘要图片逐字节等价。
- 未执行：可信非空登录、三角色正常/退回链、真实附件、权威业务回执、认证后任务恢复两分支、普通写实际拒绝、同Store原生业务进程重启、精确提交点故障、真实模型、完整键盘/150%/完整演示/官方scan。未执行完整项NOT_RUN，确实无法用当前许可动作表达的具体步骤另列BLOCKED。
- 模型：全部needs_model=false，无代理统计/代理文件/endpoint或MM_KEY注入，真实MiniMax调用 **0**。冻结enabled=false、storage-only；没有402/余额不足/欠费证据，不请求新的计费授权。
- 置信度：候选、隔离回收、解析清零、两坏盘被误接受、原文和备份状态、所见登录页 **高**；宽容解析接受前缀的内部机理 **中**；认证后恢复、完整业务和模型效果 **未知**。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M7/native-runs/review_r2_0002_REQUEST_review_r2_0002/`，驱动原始证据，只读。
- **E**：`runtime/optimization/2026-10-09/M7/native/review_r2_0002/`，独立离线安装、seed、fixture、dirty差异、phase1-audit、native-evidence-audit-r12、final-acceptance-64-r12及收尾检查。
- **R**：`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r2_0002.json`，SHA256=`9d5868438a2768097efb1594f694d93761f4c207bfff896ea481eb1df6c52c27`。
- **N**：`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r2_0002.md`，第1段笔记原文保留；本报告纠正其中提醒类型夹具和空输入点击计划的证据范围。
- 审计命令：`python3 -B runtime/optimization/2026-10-09/M7/native/review_r2_0002/audit_phase2_r12.py`；只有读取原始证据及写入E的新审计文件，不启动原生进程。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/源码/dirty/材料|交叉定位、重算清单/差异/包字节|冻结输入明确，差异可解释|37保护、159生成输入未变；非manifest运输字节相同、manifest仅签名扩展|PASS 定位子项|E/phase1-audit、dirty.diff、F/材料|
|本地准入/安装|新副本stamp/check、验签、新Store官方install_staged和may_run|本地路线可复现|均rc0，unsigned warning保留，storage-only/无agent/hosts空|PASS 离线子项；不代完整P03|E/phase1-audit commands|
|确实打开同一应用|核catalog、唯一.running、完整eval、实际图|业务脚本确已加载、字节一致|15场均702301 B eval/view=true；app_not_opened=false；原生登录页渲染|PASS 加载/登录页子项|H/.running/log/frames|
|隔离与回收|重算profile，核探针/环境/PGID/driver记录|限场内写、禁区拒读、无残留|15场probes=true，pre/post NONE，PGID_after=[]，CLEAN；无ABORT|PASS|H/result/profile/denials|
|冷启解析门槛|无tasks、合法/坏盘和窄窗参数冷启|0解析及脚本错误，不空白|15场[E]=0、panic=false、tick_exception_count=0；真实登录页持续可见|PASS B-M7-01精确子项|H全部完整host.log/state/PNG|
|合法任务加载门禁|空白[]、两完整任务含中文/转义/括号及数值、窄窗[]|不误报坏盘、不新建recover|合法场task pending=false/why空，原文不变、无任务recover|PASS R02合法子项|empty_whitespace/legal_quoted_two/empty_narrow|
|普通坏盘拒绝|对象、截断、id-only、尾随末字符非]、三非法数值类型|整份拒绝、pending保持、原文备份|7场pending=true、原因非空、recover与原文精确；原文未动|PASS R02部分保护子项|对应7场盘/state|
|完整输入消费|合法记录数组或[]前缀后接垃圾，最后仍]|仍属非JSON，必须整份拒绝|两场pending=false/why空；无recover；原文仍非法|**FAIL R-M7-02**|closed_junk_record/closed_junk_empty|
|旧备份保全|新坏盘+既有合法recover|旧备份不覆盖，本次另存latest|recover453 B保留、latest32 B与当前坏盘相同，pending=true|PASS 保全子项|preserve_old_recover|
|预置备份失败|recover路径预置为目录后冷启|原文保留、保持pending、不假成功|原文34 B不变、recover仍DIR、pending=true；可见任务备份失败说明未成立|保源/保护PASS；反馈NOT_RUN|backup_slots_are_dirs/盘/state/图|
|错误与实际恢复出口|查看坏盘实际图，对照任务banner/登录gate|错误同屏、可信主体可进行安全恢复|15张都在登录页，只有账号/口令提示；任务原因不显示，认证后的恢复按钮未测|R02可见反馈未闭合；实际恢复NOT_RUN/输入步骤BLOCKED|H/PNG；F:13761|
|空输入登录回归|许可内置tap及前/后截图核对|明确空输入拒绝，不建会话|actor=null、当前图显示输入提示，但before缺失、默认本就有同文本，无法证明点击命中反馈|NOT_RUN 点击反馈；R01历史关闭保留|empty_whitespace result/captures/log|
|提醒类型回归|核实际夹具形状与判定层|合法空/整数/小数加载，六非法due类型拒绝|审查夹具均错误写成顶层数组，全部在顶层对象门禁被拒，未测到成员due门禁|**NOT_RUN 字段矩阵；测试夹具责任在审查方**|E/fixtures/seed；H follow盘/state；F:2984|
|证据完整性|MANIFEST/结果/argv/seed/markers/denials/PNG重算|原始证据与实际文件一致|2124文件、12220检查0不一致；缺一张before被结果如实记录|PASS 一致性；capture覆盖不完整|E/native-evidence-audit-r12|
|完整链/业务重启/模型|核实际动作和权威结果|同候选实证，不能用诊断seed代替|未执行，模型禁用；Store重建不代原生进程重开|NOT_RUN，具体不可表达步骤BLOCKED|R/N、本报告|
|旧完成态与发布内容|复核listing/README/材料/图/演示|准确版本和能力、无旧完成态冒称|F说明本地/模型禁用/placeholder；README旧入口及闭合话术仍在；完整演示未交|A01/A02 P2挂账，完整材料NOT_RUN|app/README.md:5；F/listing/materials|
|四种交付状态|只核本候选回执，不继承历史候选|本地、发布、赛事、收录分别记录|本地准备FAIL；P06/P07/P08无本候选新回执、无外部动作|PASS 状态区分；外部NOT_RUN|本报告/GATES.M7审查字段|

### 隔离、完整日志及截图的具体边界

summary内嵌请求与R全等，场景/动作/size/seed/env/digest与结果及argv对应，MANIFEST逐文件无越界、重复、遗漏或hash不符。harness SHA=`8141b4de36e8a248a1b7ed0b9d430fa3ee464ccbc65fc927ef1de40be5ef34c8`、profile模板SHA=`76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`与当前相同。十五份profile按场内目录/控制口和证据中的黑名单字符串重建到同字节；审查者未读取这些黑名单路径。

完整denials与摘要逐条核对，按本场宿主PID归属的文本记录包括290次`process-exec* /usr/bin/osascript`、59次443外联拒绝，以及/dev/dtracehelper和系统Metal缓存拒写。这些是**被内核拒绝的尝试记录**，含重复报告，不是成功执行/成功外联次数，也不是模型调用。PGID运行快照只有宿主，最终为空；无许可ui_actions。driver记录外部HOME mtime相同、Library扫描空；审查者未自行扫描项目外。未观察允许profile越界写入。

全部现存capture为2560×1236宿主画面，即使empty_narrow传980×760也不能据此声称实际窄客户区或150%验证。15图只有7种摘要，逐一目视确认是登录页；业务工作台、任务banner/恢复按钮没有出现在这些图中。empty_whitespace_before不存在、after存在且摘要匹配；host日志登记两个capture，实际仅末张落盘。固定宿主是否只保留最后capture可继续查实现，但本轮不编造前置图或点击回执。

## 缺陷及上一轮对账

### B-M7-01 — P1原必修 CLOSED：解析回归消除

F/main.splash:1391共同返回标志与三调用点统一success，15场同字节完整log零[E]、无panic、tick异常计数0、实际登录UI可见。原r11的17条/场解析诊断不再发生。**仅关闭原解析/空白回归，不代表认证后工作台或全业务通过。** 原r11失败来源保留于E/gates-before与review_history。

### R-M7-02 — P1 / 必修 / OPEN：宽容解析接受非完整JSON，恢复保护未成立

- **文件与行**：F/main.splash:1391–1418 `m7_tasks_strict_parse`（:1397–1403仅检查首尾；:1407调用parse_json；:1418直接返回success）；:1596–1601 load成功分支清pending；:1491–1500 keep复验、:1517–1520 overwrite读回复用此判据。普通写守卫:1014、:5172、:7998依赖pending。任务反馈:1450、恢复控件:12328、登录提示:13761–13767。
- **触发**：在独立新Store写入`tasks.json`为①完整合法任务数组+` ignored-review-tail ]\n`，或②`[ ] ignored-empty-tail ]\n`，使用本请求closed_junk_record/closed_junk_empty冷启。两场均无解析错误，应用实际加载本冻结包。它们是故障夹具，不是伪造业务成功链。
- **实际**：①原文475 B、②25 B均保持；两场`tasks_pending_recovery=false`、`tasks_recovery_why=""`，不存在tasks.json.recover；实际图只有登录页，无任务错误。其他7种坏任务被拒、原文与备份保全，合法3场不误恢复；修复已有进展，但上述两个反例足以否定整份严格判据。
- **预期**：完整消费原始JSON并校验整份schema；前缀合法而后缀非法必须失败、pending=true、错误可见、原文备份可核、普通写保持禁写；恢复keep/overwrite不得用同样的宽容判据解锁。
- **根因**：首尾方括号不是完整JSON语法证明。代码允许宽容parse结果通过数组/成员检查即返回success；load随后合法分支解除保护。本次运行排除了旧解析错误干扰，但宿主parser的内部消费实现未直接执行跟踪，具体内部机理置信度中，反例置信度高。
- **影响**：损坏事实盘被当作可用输入，普通写保护前提消失；相同validator用于恢复两分支，失败恢复核心目标未成立，影响G0-C/U08/P01/P05和硬1/2/4。**没有实际认证业务写、覆盖或数据丢失证据，不声称已经发生破坏。** 已检测坏盘的任务原因也未出现在当前可见登录页；认证后恢复出口不能凭源码/旧图补证。
- **证据**：H两closed_junk场的result.json、完整host.log、tasks.json、state.json、frames；E/fixtures.json存准确原文与预期；E/native-evidence-audit-r12各场门禁、备份和摘要。preserve_old_recover与backup_slots_are_dirs保源结果另列，不能代替完整判据。
- **具体改法**：只补共同严格parser的**完整语法/全部输入消费**，沿用固定宿主实际支持且经过正反例实证的接口，或用可靠的JSON完整校验；明确拒绝数组前缀后的任何非空白输入。load/keep/overwrite保持同一判据。不要只匹配首尾、删validator、清pending或以序列化长度相等冒充完整校验。保留success协议、严格数值门禁、原文/旧recover保全策略和现有UI布局。使任务恢复错误在当前可见页面可读，保持身份核验；不为展示恢复按钮绕过登录。
- **验证方式**：新冻结候选和digest经harness复验两closed_junk反例、合法空/两个转义中文记录、截断/id-only/尾随、三数值类型、旧recover保全和备份失败；全部解析0。坏盘pending持续、why准确、原文与备份正确。通过获准真实输入完成隔离合成账号认证后，再验证非法keep不解锁、合法修复后keep加载、overwrite备份+受控写+严格读回、普通写拒绝及各失败点/同Store原生重开。当前不可表达的步骤如实BLOCKED，不伪session或手工终态。

### 原关闭项与P2挂账

- **R-M7-01**：原关闭记录保留；本轮仅actor为空与提示可见，点击反馈由于缺before且提示默认存在 **NOT_RUN**，没有反例足以重开，不迁移为当前点击PASS。
- **R-M7-03**：原关闭记录保留；本轮提醒夹具由审查方错写为顶层数组（prepare_review_r2_0002.py:166），产品要求对象`{"follow_ups":[...]}`（F:2931/2984）。因此观察只证明非法顶层拒绝/保源，无法验证空/整数/小数或六种due类型。**本轮字段矩阵NOT_RUN，不判产品FAIL。** 下轮审查只修夹具包装并保留原类型值；不得修改原证据、不得要求构建方修业务代码来接受错误夹具。也不能用作者矩阵代独立PASS。
- **A-M7-01 / P2建议挂账**：app/README.md:5仍旧r4/r2路径与已闭合话术，:7附近历史完整闭环表述没有本候选全链依据。建议明确历史/当前冻结入口与实际状态。本次不因它单独判FAIL。
- **A-M7-02 / P2建议挂账**：F/listing.json:12仍1×1 placeholder，完整2–3分钟演示欠交。建议取得最终字节的业务关键截图/真实演示后重新冻结并复验受影响项，不能使用旧B完成态。无外部发布动作，本次不因建议单独判FAIL。

### 未测与解阻

本轮无ABORT。**BLOCKED只用于白名单确实不能覆盖的具体步骤**：固定宿主type/key未实现，当前用户禁止系统自动化/ui_actions，因此可信非空键入、完整键盘流程及认证后恢复不能由许可动作完成；当前schema没有同Store原生业务进程重开、精确提交点拒写/读回调度或150%设置接口。需要同一隔离harness中的受控接口和新证据；不是Codex沙箱rc71/pgrep rc3阻塞，也不重新申请已授权的身份/provider。提醒字段矩阵因审查夹具错误是NOT_RUN，缺截图也是证据缺口，不写BLOCKED。

## 全部64项验收登记

以下保留原编号/定义。完整用例与已验证子项分开；历史后端PASS、前序候选PASS及作者结果不迁移到本候选。逐项定义来源及原r11状态保存在E/final-acceptance-64-r12.json，正式原ACCEPTANCE保持不变。

|编号|原定义|完整项结果|当前范围与证据|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|NOT_RUN|固定版本/准入/安装/实际原生启动/0解析子项PASS；可信操作写回和同Store原生重开未跑，完整项NOT_RUN。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|actor=null/登录页子项已核；可信非空登录、每查每写核权及独立会话未跑，许可输入步骤BLOCKED。|
|G0-C|唯一事实源、原子一致性、并发与恢复|FAIL|两closed_junk非完整任务数组被接受、pending=false/why空/无recover；合法加载与其余坏盘/旧备份保源子项PASS；完整原子/并发未跑。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|未执行真实附件写入/回读/归属/失败恢复；诊断I/O不代附件。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|冻结enabled=false/storage-only；needs_model全false、0真实调用，无代理统计；未验证系统助手/真实模型链。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|审查提醒夹具错误顶层数组，仅非法顶层拒绝/保源子项PASS；due字段类型、恢复/去重/真实通知未跑。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|NOT_RUN|提醒夹具顶层错误，字段/作业未测；同Store原生业务进程重开与通知去重未执行，具体重开调度BLOCKED。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|同候选原生脚本加载/登录页渲染子项PASS；可信业务动作/权威回执/同Store原生重开未执行。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|未执行该完整业务/UI用例；诊断加载、源码、作者与前序结果不代本候选PASS。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|两坏任务未进入恢复保护；已检测的任务损坏原因也未显示在实际登录页；认证后安全恢复NOT_RUN。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|NOT_RUN|size参数1280x800/980x760均输出2560x1236宿主画面；实际客户区和150%/全部主要动作未实测。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|固定宿主内置type/key未实现；本次禁止ui_actions/系统自动化，白名单不能完成键盘主流程；不以agent rc71/pgrep rc3判阻塞。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|NOT_RUN|实际登录页渲染PASS子项；滚动/输入/业务面板/动效完整流程未跑。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|本候选完整2–3分钟演示及独立理解核验欠交，15登录帧不能代完整演示。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|同候选失败恢复冷启矩阵有两坏盘被误接受；完整成功/退回/重开链NOT_RUN。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|NOT_RUN|冻结/dirty/宿主/工具定位与离线新Store安装子项PASS；完整干净构建/依赖说明未复现；A01 P2挂账。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|独立stamp/check/verify/install_staged子项PASS；官方实际scan审阅未执行，不以rc0代审阅通过。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|同字节材料/15真实原生登录帧子项已核；listing仍placeholder、完整演示未交、before缺失；A02 P2挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|FAIL|源码/冻结/运输/实际运行字节一致子项PASS；R-M7-02核心P1未闭合。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|无本候选公开源码/Hub递交新回执，无外部动作，不继承历史0.1.0-b。|
|P07|维护者商店收录结果|NOT_RUN|无本候选商店收录回执，未listing；外部历史台账不改。|
|P08|赛事正式提交入口回执|NOT_RUN|无本候选赛事正式入口新回执，未提交；外部历史台账不改。|

完整项计数：PASS 0、FAIL 4、BLOCKED 1、NOT_RUN 59。PASS子项单独登记，不冒充完整用例通过。

## 判定与交接

- **最终结论：FAIL**。范围是M7-r9-worktree/0.1.0-h、固定M0/r3宿主的本地发布准备。唯一未闭合的核心P1为R-M7-02；B01关闭，A01/A02建议挂账，无“基本通过”或带条件放行。
- 硬1 **FAIL**：两坏盘被误接受，其他完整门槛未执行，不能全量PASS。
- 硬2 **FAIL**：同候选失败恢复门禁反例成立；完整正常/退回/认证恢复/真实业务重启/模型NOT_RUN。
- 硬3 **NOT_RUN（完整）**：字节/清单/运输/秘密隔离子项PASS；真实业务图/演示仍缺，P2挂账保留。
- 硬4 **FAIL**：离线准入、安装、解析清零、隔离子项PASS；独立核心恢复失败，官方scan未执行。
- 硬5 **PASS（状态区分）**：本地准备FAIL；**P06公开源码/Hub递交、P07商店收录、P08赛事正式回执均NOT_RUN**，没有本候选新回执。本轮不查询/操作外部平台，不继承0.1.0-b历史提交/评分状态。
- 受影响回归：合法任务不误拒、三个任务数值类型、七种坏盘、旧recover/备份失败已实测；完整消费仍失败。提醒字段矩阵和点击反馈未完成，不补编通过；认证后桌面与业务未测，不作无关扩审。
- 更新：本报告与GATES.json的M7本轮审查字段/结论；旧r11源状态在E/gates-before.json和review_history保留。原docs/build-loop/ACCEPTANCE.json、其他模块、业务源码/原数据及原始H不改。
- 下一模块：**不允许，本次不执行**。构建方留在M7，只修R-M7-02并交新冻结候选与harness解析清零/完整拒坏/恢复证据。审查方下轮修正提醒夹具，避免重复同一测试错误。
- **NEEDS_ABRAM=no**：本地catalog/install_staged可行，身份/provider/离线签名已授权；0模型调用，无欠费或公开发布申请，剩余是技术/证据缺口。

## 审查过程约束偏差

第1段启动时曾误读一次项目外MEMORY.md索引，已在N记录；没有用其内容形成候选、源码或验收结论，没有项目外写入。第2段显式文件读写全部在本项目；未读取secrets、明文凭据、原业务数据或用户会话库。不能将整个两段过程写成“零项目外读取”。本段提醒夹具形状错误和before截图缺失亦如实降级，不隐瞒、不计产品缺陷、不改原始证据。

STATUS=FAIL
NEEDS_ABRAM=no
