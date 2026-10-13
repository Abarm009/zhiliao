# M4 独立 Review r10

**最终结论：FAIL。** 正式候选 M4-r8 的八场独立原生冷启动均渲染工作台，解析/运行错误为0，隔离回收记录符合要求，原文/确认意图/动作键保留，三种旧锁启动处理通过。但合法空数组及完整任务数组均被误判为“截断/未闭合”，进入恢复未决；B-M4-01 没有闭合。D-M4-03 仍无可验证原子命令边界；实际接单至开工、可信三角色及真正并发没有成功证据。不能 PASS，不执行下一模块。

## 审查对象、环境与实际范围

- 审查者/日期：本主会话唯一独立审查者，2026-10-12，Asia/Shanghai；两段式 r2_0937，无子代理、无业务代码修改。实际主会话 Router/model 与自身 createdAt/标题工具不可核验，未冒称已切指定型号或完成命名。
- **candidate_id=M4-r8-worktree**；base_candidate_id=**M4-current-M3-r8-cc193cf0-review-r9**。作者报告 `reports/M4_IMPLEMENTATION_r8.md`、清单 `runtime/optimization/2026-10-09/M4/r8/CANDIDATE.json`。由用户交接的 build-r8 证据关联清单/请求/运输件定位，未按mtime选版。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树dirty。冻结 main **562062 B**，SHA256=`982b7c352da9a026a856faad75d0bf21f8b6ef36a9010ba1122acd45971c7267`。独立差异 E/independent-r9-to-r8.diff，base=上一轮r9冻结cc193cf0/552591 B；没有把历史共享修改全部归属于本轮M4新增。
- 前置 **M3=BLOCKED / M3-r8-worktree / M3_REVIEW_r10.md**，没有已接受PASS；M2仍FAIL。按用户前序挂账裁决继续本模块局部复核，不把挂账等同前置通过，不改前序结论。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`。
- 运输包digest=`d9f2a769d26d09f0f9f333dc49fb78ec8b2e1f7acfd49f6af68f0ec6c91432d5`；本轮复用已授权隔离离线catalog/本地安装件，新私钥0。签名manifest有integrity及官方默认字段差异，业务id/version/capabilities/network对应源；不声称manifest全字节相同。
- 独立请求R SHA256=`32798115fd25e3ed57ccf16d6c2260d01b41123bc41620b6eccca8d3474a6385`；驱动沙箱外执行 **11:12:51–11:14:40 +08:00**，8/8 CLEAN、quit_http/rc0，无ABORT。审查方没有自行启动launcher/harness、sandbox-exec/pgrep预检、--help或额外UI自动化。
- 第1段读取实际AGENTS、CONTEXT、00/01/02/M4/04、上轮r9、r8交接/差异/作者证据、前置与19项T/U定义；第2段全读summary/result/profile、完整host.log/denials、MANIFEST及权威盘，全核16个PNG摘要并目视全部3种不同图像内容。范围仅旧B01/D03/D04及直接受影响回归。
- 实际审计命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/native/review_r2_0937/audit_phase2.py`，最终rc0，**5709项证据一致性检查、0失败，不是5709个业务用例PASS**。初次审计误设“运行中只能有宿主”，stale场实有同组osascript子进程；已改为核宿主存在/所有成员同PGID并保留建议，而非掩盖记录或误报业务失败。
- 全部needs_model=false，model proxy未启，本轮MiniMax请求**0**；没有402/余额不足/欠费。未读provider密钥或真实明文凭据，无公开发布/push/issue/消息/公网部署。
- 未运行：可信登录后实际输入、接单/设备/预约/开工、改派/改约/取消、提交点故障与同盘重开、双上下文并发、AI迟到交错。合成DRAFT仅测加载，不是M3创建成功工单；没有注入SESSION、预约或开工状态，没有手改运行盘跳过业务。
- 起止15项保护输入、179项seed/mirror相同；写门禁前再核。第1段一次项目外记忆索引读取已在N披露，没有作为本报告候选/事实/验收依据；第2段所有读取与写入限项目内。

**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r2_0937_REQUEST_review_r2_0937/`；**E/**=`M4/native/review_r2_0937/`；**A**=E/native-evidence-audit-r10.json；**N**=`M4/native/REVIEW_NOTES_r2_0937.md`；**R**=`M4/native/REQUEST_review_r2_0937.json`。短路径均相对 `runtime/optimization/2026-10-09/`；报告路径相对本桌面文档目录。以下源码行指E/source.main.splash，与本轮工作树相同。

置信度：候选/摘要/盘面/日志/截图可见内容/锁处理，高；括号数值与字符串类型不匹配根因，高（本地宿主源码及独立正负盘结果支持，未输出VM中间值）；未执行真实业务/并发/模型效果，未知。

## 必需检查与原生结果

|检查|独立步骤与期望|实际|判定/证据|
|---|---|---|---|
|候选/宿主/运输件|核冻结清单、请求及全部运行资源|本轮main、配置、身份资源及包与候选相符|PASS内容一致性，A；M3前置未满足并挂账|
|冷启动/旧空白回归|八场新Store启动/capture；零parser/运行错误、业务根渲染|562062 B/view=true，0错误，登录行完整|PASS限定子项，H各log/PNG|
|合法权威盘加载|合法空盘、字段完整DRAFT，pending=false|两者pending=true，why=截断/未闭合；合法盘另生成recover|**FAIL，B01**，A/H两场state与tasks|
|坏盘检测/保全|截断+旧有效recover；闭合缺字段/非法status|截断pending且旧备份保持；后二者虽拒收但错报截断，成员schema没得到动态证明|截断检测/保全子项PASS；分类与完整恢复FAIL/NOT_RUN，B01|
|锁启动恢复|future/unknown保持、stale回收、saved token清空|三锁符合盘面预期；正常tasks仍误pending|锁boot子项PASS；合法盘回归FAIL，A|
|真实UI核心链|同一M3工单→接单→服务设备→提议/合法确认→开工|只有冷开，无可信登录或业务写命令|NOT_RUN；实际输入控制BLOCKED，正常盘加载已FAIL|
|硬1权限/设备关系|资格/越权/假设备拒，合法服务关系成功|保存actor清null；实际分配/设备命令未执行|未认证不提权子项PASS；完整硬1 NOT_RUN|
|硬2预约规则|提议不直升、合规确认、过期/时区/改约与拒绝|未发生实际预约命令|NOT_RUN，历史源码/作者声明不代验|
|硬3真正并发|两可信上下文同Store同步接单/重叠确认唯一成功，相邻均可|普通read/write/read仍非原子；逐场新Store不提供该调度|D03源P1未闭合；动态BLOCKED，无实测双成功|
|硬4开工/旧技工授权|无设备/无有效预约拒，改派旧技工拒|未开工/改派，未执行拒绝命令|NOT_RUN|
|硬5三角色首屏/输入/回执|阶段/负责人/预约/动作与权威一致，实际可填|只有未认证首屏；完整DRAFT被误拒；无可信三角色/回执|加载恢复FAIL；完整三角色NOT_RUN|
|旧确认/旧AI撤销|改派/改约旧绑定失效，新编辑可重新绑定，迟到回复拒|六相关函数段未变，旧epoch精确反例保持SOURCE-CLOSED|完整动态NOT_RUN，受控交错BLOCKED|
|隔离与回收|profile/probes、env/denials、退出/PGID及摘要|8/8记录符合指定要求|PASS限隔离回收记录范围，A|

|原生场景|权威结果|本轮精确结论|
|---|---|---|
|valid_empty_no_lock|` \n[]\t\n`原盘保持，pending=true/why截断；recover=原文；锁仍不存在|合法加载FAIL；原文/意图/key保留PASS；首次合法命令NOT_RUN|
|valid_task_whitespace|完整DRAFT/数值版本时间/appointments数组原盘保持，却pending=true/why截断|合法加载FAIL；不能拿未认证无可见任务单独证明schema失败|
|truncated_existing_backup|截断主盘保持、旧有效recover=`[ ]\n`保持；corrupt.latest=原坏文；pending=true|截断检测和备份保全子项PASS；实际禁写/显式恢复/可见完整错误出口NOT_RUN|
|id_only_closed|闭合仅id数组被拒但why=截断，recover=原文|准确分类FAIL；成员缺字段守卫动态未证明，不重用旧pending=false结论|
|unknown_status_closed|字段齐、status=NOT_A_STAGE的闭合数组被拒但why=截断|准确分类FAIL；status成员门禁动态未证明|
|future_lock_clean_empty|未来他token原样、进程token空；合法`[]`仍pending|future启动锁PASS；正常盘加载FAIL；命令重入/提交丢锁NOT_RUN|
|unknown_lock_clean_empty|未知戳锁原样、unknown_kept；合法数组仍pending|unknown启动锁PASS；说明被随后坏盘status覆盖，可见完整出口NOT_RUN|
|stale_lock_clean_empty|stamp=1变空、released；合法`[ ]`仍pending|stale启动回收PASS；正常盘加载FAIL；不是预约过期验收|

## 独立证据逐项核对

1. **MANIFEST.sha256 1293条**全部独立重算，无重复、漏项、额外文件或摘要差异，无symlink。summary的完整request与R一致，全部八场摘要字段与对应result一致；harness/template/binary摘要匹配保护快照。
2. profile逐场按模板/对应run/control port重建后逐字一致；probes.ok=true、apply rc0、场景外写探针拒绝且created=false，五禁读路径探针均拒。pre/post_pgrep=NONE，最终pgid_members_after=[]；library_scan为空，驱动记录的真实HOME/.octosense mtime前后不变。审查者核记录，没有读取真实HOME另作预检。
3. HOME/app-data/cache/config/tmp全部指向各新run；启动cmd/size/两个动作与R一致。每场完整seed清单与179项冻结源对应；mirror/installed/唯一.running全部资源逐字节对应冻结签名包。业务eval是562062 B，809 B是另一系统视图；digest_seen_in_seed=true/log=false与实际一致，marker不等于加载证明。
4. 八个请求capture都存在且SHA256匹配，共16个PNG均为**2560×1236**。全量摘要归为3种字节内容，已逐种目视；同一未认证首屏，时钟11:12/11:13/11:14不同。valid_empty的part/final不相同，其余7组相同；差异各自有摘要并被内容检查覆盖，不凭part不等同final报事故。
5. 登录行可见，图未完成登录；底部被Dock/截图可见边界遮挡，未显示任务恢复说明的可核证据。不能据裁出区域断言绝无恢复控件，也不能把state有status解释成可见恢复出口已通过。size参数不是业务客户区尺寸/150%文字验收。
6. files_written_count按R顺序为**125/125/125/125/125/125/125/126**；所有列表存在、唯一、有序、在run内，低于400截断阈值。它是mtime文件清单，含包/缓存/PNG/状态等，不是125次业务提交或完整系统调用审计。八场tasks/actions/events/合成账号原字节全部保持；stale回收是唯一锁变化；新recover/corrupt.latest均与原文逐字一致。
7. 每份完整host.log字节数/tail/markers独立重算匹配，八场0[E]/panic/unknown action、业务view=true；state tick_exception_count=0。pending_input/confirm_intent_id/action_keys/panel与seed精确相同，actor清null/token空；这是盘面及冷开子项，不代登录后可编辑控件恢复。
8. 完整sandbox-denials逐份读取，以harness同一规则重算summary全匹配。记录包括被拒443外联、系统Metal缓存和/dev/dtracehelper尝试；**被拒尝试不是成功外联/外写**，duplicate reports不当精确请求次数。没有已证成功违反隔离的原生行为。
9. needs_model全false，result中model_proxy/model_proxy_stats字段均**不存在**，env没有OCTOSENSE_MODEL_ENDPOINT/MM_KEY，summary各billing_error=null；这是未启代理模式，不捏造“stats.requests=0”字段。新增真实MiniMax调用0，无实测欠费，T35真实模型交错未运行。
10. 七场运行PGID快照仅宿主，stale场多一条同PGID `22979 22963 osascript`，最后已回收。没有参数/用途证据，不据名称认定成功额外自动化或安全P1；保留材料建议。审查者未调用osascript。新签名私钥0，复用作者隔离件；两旧私钥路径仍不存在、keys目录空，删除来源记录保留。

## 上轮缺陷闭合与本模块修复清单

### B-M4-01 — P1 / 必修 / PARTIAL：合法任务盘被误拒，恢复仍不能可靠区分好坏

- **保留关闭子项**：本轮零解析/运行错误、工作台渲染、完整登录行、原文/意图/key保留；不再要求重修旧空白/裁切/清空问题。
- **本轮改善**：截断盘能够pending，旧有效recover保持、本次坏文另存corrupt.latest且字节核实；原r9“坏盘pending=false”不继续作为当前实际。
- **文件与行**：`app/bundle/main.splash:1308–1318`首尾校验；成员schema`:1118–1145`；恢复备份`:1149–1175`；pending普通命令拒`:3930–3938`、创建拒`:6518–6521`。冻结副本E/source.main.splash。
- **触发**：R的valid_empty_no_lock预装合法空数组带空白；valid_task_whitespace预装完整DRAFT、有id/project/reporter/已知status/数值version/appointments数组/数值创建更新时间；只冷开与capture，不改运行盘或调用恢复。future/unknown/stale三场其它合法空白变体同样复现。
- **实际/预期**：五个正常任务盘全部pending=true、why=“JSON截断或顶层数组未闭合（首尾字符校验失败）”，生成recover，主盘保持；应pending=false，正常加载且不产生坏盘备份。闭合id-only及非法status也错报首尾截断，应走对应成员门禁、给准确原因。
- **根因**：`:1310`to_chars后`:1313–1314`把元素与字符串`"["`/`"]"`比较。本地宿主`runtime/native-build/makepad/platform/script/src/string.rs:80–84`、`string_heap.rs:580–618`显示返回U32码点数组，`array.rs:270–272`/`array_heap.rs:121–122`显示索引/转换为数值；字符串与数值类型不一致。独立合法/坏盘全部走相同失败分支，根因高度支持；未输出VM中间值，不冒称已取到中间类型实测。
- **影响**：可靠加载与后续处理入口被阻断，已有任务不能进入正常内存事实；pending守卫源码会拒创建/普通命令。**本轮没有实际登录后写命令，未观察实际命令回执或坏盘覆盖，不编造越权写/数据损失事故。** 这是旧恢复P1的核心关联回归，不是错误文案建议。
- **证据**：H上述五个正常盘场的state.json（pending/why/status）、tasks.json/recover、result、完整host.log及PNG；A.scenarios的load_check与盘摘要；E冻结源码/独立diff。id_only_closed/unknown_status_closed提供成员分类反例。
- **具体改法**：用宿主真实类型比较括号，例如与`"[".to_chars()[0]`和`"]".to_chars()[0]`比较，或经证实的码点91/93；保留trim、成员schema、pending禁写与有效备份保全。不要移除门禁、清盘或伪造正常状态。正常加载通过后，确认成员门禁确实走到，并验证真正登录后的可读恢复入口。
- **验证方式**：独立合法`[]`/带空白空盘/完整任务均pending=false且无新recover；截断保持主盘和旧备份；闭合缺字段/非法status准确拒收；零错误渲染与原文/意图/key不回退。可信登录后普通命令拒写且事实/回执一致，显式恢复经确认/读回，最后真实M3→接单→设备→预约→开工，不手改状态。

### D-M4-03 — P1 / 必修 / PARTIAL：启动锁子项通过，原子命令边界仍未成立

- **文件与行**：获取`:3743–3812`、token构造`:3751`、释放`:3814–3843`；commit owner核`:4180–4206`、版本核`:4212–4242`、冲突核`:4246–4261`，主写`:4282–4292`；共享冲突helper`:3851`及spec清/传/消费`:3918/4064/4160–4161`。
- **已闭合/改善**：future完整他token逐字保留、unknown戳原样/unknown_kept、stale清空/released、saved token清空，本轮独立PASS限boot。源码新增首次缺锁exists区分、提交必须同owner（空/缺/他token拒）、写前版本及冲突重核；这些没有实际命令动态证据，不将其写成已验原子事务。
- **触发/实际/预期**：两独立上下文读空锁后可交错各写/读owner，owner/version/conflict核验到整盘写之间仍有窗口；预期同盘接单/跨项目重叠确认唯一成功，邻接都成功且无丢更新。**实际本轮是源码原子缺口与调度通道不足，没有实测双成功。**
- **根因/影响**：重复read/write/read与写前复核不能把获取—授权—检查—事实/回执/事件提交变成原子边界；actor@毫秒@本地ID_SEQ不证明跨实例唯一。硬验收3属于本模块核心要求，旧P1继续未闭合。
- **证据**：E/source.main.splash及independent-r9-to-r8.diff；A三锁盘面；作者M4_IMPLEMENTATION_r8`:37–51`明确HOST_PRIMITIVE_BLOCKED并给双进程文字调度/三种宿主原语建议，但没有当前白名单可执行调度请求/脚本与实际唯一成功结果。文字说明不代可运行最小复现。
- **具体改法/解阻**：提供可靠跨实例owner和原子获取/等效串行事务边界，覆盖最新授权、版本、跨任务冲突及任务/预约/回执/事件提交；获取/提交/释放守同owner。需宿主原语时交驱动可执行最小复现和对接方案；不自行改宿主路线、新增服务或重写别的模块。
- **验证方式**：两可信原生上下文同一隔离Store同步接单/跨项目重叠确认各一成功，相邻时段均成功；核唯一承接者/预约/成功回执/同action事件及同盘重开。补缺锁首次合法命令、锁读失败、提交时锁丢失/清空/覆盖反例，保future/unknown/stale启动回归。不能预置空锁掩盖首次获取问题。

### D-M4-04 — SOURCE-CLOSED限定epoch反例保持，完整动态仍未验

E/source-regression.json记录六函数段与r9逐字一致：m4_invalidateConfirmation、editDraftField、editRawText、confirmDraftModelBound、reassign、rescheduleAppointmentFromForm。当前清epoch`:3580`、记录本轮编辑`:5710/5810`、只消费本epoch`:6263–6264`；改派`:9446`及预约变化`:7250/7308/7359/7406/7514`保留撤销调用。

无本轮源码回退证据，不新增P1或要求重写已修子项。旧技工/旧确认实际拒、迟到AI展示/采纳拒及新绑定恢复仍NOT_RUN；受控交错通道BLOCKED，不能SOURCE-CLOSED代完整PASS。

### 建议与挂账

- 保留历史A-M4-01/02/03及尺寸/首屏取证建议，不据建议项FAIL。正常盘误拒和原子边界是本轮仅两项必修。
- **A-M4-R10-01 / P2 / 建议**：H/stale_lock_clean_empty/result.json的运行组多osascript子进程，参数/用途未记录；最终组空。期望内置capture来源可追溯，实际缺该细节；影响授权边界审计清晰度。驱动补宿主内置capture的调用来源/参数，区分内置机制与额外自动化，复核隔离/回收；不凭进程名称认定安全P1。延续前序同类建议，不扩修业务。

## 19项既有用例逐条结果

|用例|本轮状态与精确边界|
|---|---|
|T04|BLOCKED：当前白名单/harness无双可信上下文同Store同步接单；D03源P1仍在，无实测双成功|
|T05|NOT_RUN：资格/项目拒绝、经理分配事件；saved actor清空只证明未提权|
|T06|NOT_RUN：实际改派旧预约取消/任务ACCEPTED/新负责人/旧技工拒；D04源码保持|
|T07|NOT_RUN：编码/载荷一致及伪造/跨项目/归档设备实际拒绝|
|T08|NOT_RUN：合法服务空间正例、仅安装位置相同负例|
|T09|NOT_RUN：无设备开工、处理中技工换设备拒、经理更正旧新值理由|
|T10|NOT_RUN：提议不直升、报修人确认与非报修人拒|
|T11|BLOCKED真正同盘同步确认；实际跨项目冲突和相邻确认NOT_RUN|
|T12|NOT_RUN：待改约旧确认有效、新确认替代、拒新保旧；失效源码保持|
|T13|NOT_RUN：提议过期410、无timer仍拒/客户端假时钟；stale锁不代验|
|T14|NOT_RUN：真实上海日期/UTC换算、歧义确认/end<=start；实际键入通道BLOCKED|
|T15|NOT_RUN：旧version409/刷新/防覆盖/百分比拒；关联合法盘加载FAIL、原文/意图/key保留PASS仅子项|
|T31|NOT_RUN：取消释放预约/留事件、终态拒再次开工/验收、再次故障关联新任务|
|T35|旧epoch反例SOURCE-CLOSED保持；真实改派/改约/迟到建议NOT_RUN，受控交错BLOCKED|
|U01|未认证工作台/完整登录行子项PASS；三个可信角色待处理/下一处理人NOT_RUN|
|U03|NOT_RUN：三可信角色同任务事实/权限动作/不得自验|
|U04|NOT_RUN：实际当前预约/待改约/冲突/过期投影；坏盘准确分类关联FAIL，可见完整恢复出口未证|
|U05|NOT_RUN：真实设备选择/安装位置与服务空间分开/来源依据|
|U07|关联合法盘恢复FAIL；原文/意图/key冷开保持、截断旧备份保全子项PASS；重复提交/丢响应/旧版本/离线NOT_RUN，同盘重开/提交故障通道BLOCKED|

**BLOCKED的具体依据**：同SHA固定宿主前序独立 `M3/native-runs/review_r2_0937_REQUEST_review_r2_0937/restore_unknown_empty_arrays/logs/host.log:40–41`明确unknown type/key；harness源码`:224–241`逐场新目录Store、request.schema没有同盘双上下文同步、重开、精确提交故障/模型回包交错控制。本次请求没有ABORT，不以agent内rc71/rc3或“宿主不能启动”作理由。尚未执行的业务命令NOT_RUN，已原生运行且失败的正常盘/分类检查FAIL。

## 判定、门禁与交接

- **最终结论：FAIL**，范围为正式M4-r8候选旧B01/D03/D04复核及直接关联回归。八场CLEAN/零错误渲染不抵消正常盘误拒；没有完整真实核心业务证据，不放行。
- **必修两项**：B-M4-01修正常/坏盘类型比较及准确恢复；D-M4-03提供原子命令边界与可执行独立并发验证。先维持零解析/可渲染、输入/意图/锁/备份保全，再按原编号修；D04已修精确子项保持。建议挂账不作FAIL理由。
- 解阻后补可信合成账号UI登录、M3真实创建→M4接单/合法服务设备/具体预约→合规确认→开工，核权限/时区/过期/改派改约及旧AI撤销；同Store真实并发/失败恢复。不能注入SESSION、手改任务状态或用作者Python等价脚本代原生业务。
- M3前置仍BLOCKED，M2仍FAIL。本轮共享身份/原文/意图/锁/任务加载为针对性回归；正常盘加载回归失败可影响M3创建，未修改前序门禁或替它们整模块验收。
- 仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M4 status及审查字段，review_report指本报告、review_candidate_id=M4-r8-worktree；旧r9审查字段完整追加review_history，保存门禁前态。作者candidate/base/implementation/build相关字段、其他模块和external_delivery保持。
- `docs/build-loop/ACCEPTANCE.json`保持；没有新的完整T/U原生PASS，19项精确状态写GATES.review_acceptance并保留历史来源，不把旧后端PASS改称原生PASS。
- 不允许进入下一模块，不提供下一模块入口，不执行下一模块。
- **NEEDS_ABRAM=no**：身份/provider/隔离离线签名/本地安装已授权，没有实测欠费或公开发布需求；剩余是技术修复与验证缺口。

STATUS=FAIL
NEEDS_ABRAM=no
