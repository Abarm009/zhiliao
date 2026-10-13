# M6 独立 Review r12

**最终结论：FAIL。独立原生冷启动、签名候选一致性、提醒合法加载/坏盘保护、隔离回收已通过；R-M6-02 已在当前候选关闭。D-M6-03 仍阻断核心持续建议：阶段来源 schema 不匹配、重开加载丢失全部 refs、应用自产 NO_SERVICE 日志与恢复 schema 不兼容。D-M6-02/04 的源码子项保持，但实际恢复/收藏故障收敛没有运行闭合，不签通过。**

- 审查者 / 日期：当前主会话唯一审查者，2026-10-13，Asia/Shanghai，无子代理。实际 Router/gpt-6.1-sol 路由无可核验接口，未声称切换；当前工具无本会话 createdAt/改标题接口，未用当前日期代替创建时间。
- candidate_id / base：**M6-r10-worktree / M6-r9-worktree**。用户交回的构建和独立请求、候选清单、实施报告、GATES均定位同一候选，不按文件时间择版。
- HEAD：8d730569546cb57310944bb299695134df773b9d，dirty工作树全部保留。源701133 B / 13848行，SHA256 **3bc555f2f0e4134120d7b8eb71d3a4e74f860cb6cc8ee64a3539fcc9203ef82b**；运输digest **7e968a23e43386e9eae57e11e4e68bdf494f933dbe28ec43f995d75ec94e1fec**。开始/第1段冻结/第2段源一致；GATES只在本轮审查落盘时改变。
- 作者报告：docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r10.md；清单：runtime/optimization/2026-10-09/M6/r10/CANDIDATE.json。
- 前置：**M5仍FAIL / M5-r10-worktree / M5_REVIEW_r12.md，未接受PASS候选**。依据用户后续前序挂账裁决继续局部重审，不改写前置结论。本轮只回归冷启动和D02/D03/D04相关行为，不重新审其他模块业务。
- 上轮：M6_REVIEW_r11.md。本轮仅逐项核D01～05/R01/R02已关及未关子项和受影响回归；本报告所列三处必修均归原D-M6-03，不扩新业务。
- 宿主：runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense，SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**。
- 实际原生执行：驱动在agent沙箱外于 **06:41:51–06:44:36 +08:00**执行独立请求12场、2批；12/12 quit_http、rc0、CLEAN，无ABORT。审查者没有自行启动宿主，没有运行sandbox-exec/pgrep/osascript。
- 已读：第1段材料/冻结源码/差异/笔记、04模板；本段全部summary/result/profile/probes/logs/denials/MANIFEST、完整运行包和隔离权威盘、24张PNG结构与摘要，并目视全部7种独特画面。为避免用例误标，本段按05_IMPLEMENTATION_ACCEPTANCE、09_AGENT_HARNESS、10_UI_UX_SPEC原文校准T/U编号；第1段个别简称不作为正式定义。
- 实际命令：第1段官方本地hub verify rc0；本段 python3 -B runtime/optimization/2026-10-09/M6/native/review_r2_0002/audit_phase2_r12.py，rc0，**20080项证据一致性检查、0不一致**。该数字不是业务测试数。
- 未运行：三角色可信登录后的首次流程、搜索/待处理/下一步、真实收藏/恢复动作、通知去重/同Store重开/撤权跳回/旧约取消、精确提交点故障、真实三AI链/人工输入、实际三客户区/150%和键盘完整流程。
- 模型：12场needs_model=false，真实MiniMax0次；无model_proxy_stats/代理文件/endpoint或MM_KEY注入，无实际402/欠费。NEEDS_ABRAM=no。
- 文件范围：第1段项目外记忆索引读取偏差已在阶段笔记披露，没有作为本轮判定证据；本段显式文件读写限项目内。未读明文凭据/secrets，未改原始业务数据、业务代码或harness，未publish/listing/git push/发消息/部署。独立验签后核作者两私钥不存在，本轮无新私钥。
- 置信度：候选/原生加载保护/引用丢失和源码契约 **高**；可信业务流程、真实模型事实正确性和动态故障恢复 **未知**。

## 证据及逐项审计

以下路径均相对项目根：

- H=runtime/optimization/2026-10-09/M6/native-runs/review_r2_0002_REQUEST_review_r2_0002/，驱动原证据，未修改。
- E=runtime/optimization/2026-10-09/M6/native/review_r2_0002/，冻结源/差异/seed/签名核验/独立审计。
- R=runtime/optimization/2026-10-09/M6/native/REQUEST_review_r2_0002.json，SHA256 **a31170b7d08083320e6698c6d6e8e50e1a8ffd5aee875be8d0956317d805960e**。
- N=runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r2_0002.md；A=E/native-evidence-audit-r12.json；B=E/refs-load-observation-r12.json。

1. summary.request等于R；请求摘要等于第1段冻结值；场序/两批/result与summary字段全等。**MANIFEST 1974项**完整重算，文件集合一致，无重复、缺失、符号链接或越界路径；源/harness/template/宿主摘要匹配。
2. 每场profile按冻结模板、实际run目录/端口重建到字节相等，profile路径/sha256一致。全部probes.ok=true，apply rc0，外写探针拒且created=false，五项禁读均拒；不通过访问受保护文件来复验。HOME/app-data/日志/cache/tmp等记录路径在各自新场目录。
3. 全部pre/post_pgrep记录rc1/NONE、out/err空，pgid_members_after=[]、宿主rc0、quit_http；原HOME mtime前后不变、Library scan空仅使用驱动记录，审查者未访问项目外HOME。所有pgid_members_running含完整argv，未采到osascript。
4. **R02新增措施独立成立**：每场profile禁止/usr/bin/osascript执行；探针原文execvp Operation not permitted，rc71为驱动执行的预期拒执行；全量denials按原算法重计一致，总计记录105次process-exec* /usr/bin/osascript拒绝（窗口日志可能包含其他场/探针，不等于105次业务调用）。拒执行与采样共同支持当前路线已阻止该程序，不能把拒绝记录误称已执行。
5. seeded_files与冻结完整seed/mirror逐项一致；完整mirror、installed和唯一running作品资源全等。运输manifest含integrity，与工作树manifest分别核，不混称同一文件。每场apps/catalog.json齐全，无HOST_DID_NOT_OPEN_APP/no catalog；signed本地路径成立，无须公开发布。
6. files_written列表按请求顺序为 **127/127/127/127/127/127/127/128/127/127/127/128**，排序/唯一/数量/存在/场内范围一致，未触400项截断。它按mtime记录文件集合，不是业务写次数。全部业务seed非state文件原字节保持，tasks/actions/events/accounts/缓存/提醒/marker/ai_requests保全；actions/tasks没有新增业务写。
7. sandbox_denials.file/summary重算一致，除上述禁执行还含443外联、Metal外缓存、/dev/dtracehelper拒绝；拒绝不等于成功外联/外写。没有放宽Seatbelt换成功。完整host.log bytes/tail/host_log_markers/digest标记重算一致。
8. 12场均加载701133 B作品view=true，未见[E]、parser/type/scope/unknown-action/panic匹配诊断，tick_exception_count=0。809 B系统view不充当作品。log_truncated_cn/invalid_member_middle/history_source_cache分别有约310/269/268ms启动present日志；没有持续阻塞证据，不升级P1。
9. **24张PNG**（12 final+12 part）签名/CRC/完整长度/摘要均核；7种独特摘要全部目视，均2800×1696。全是原生登录页；cold/phase/manager的part见登录按钮按压色，仍未认证，提示输入账号和口令。三size进入实际命令，但无实际客户区读回、无150%。不能把原生登录图当三角色工作台或引用/恢复验证。
10. 所有state.actor=null、selected_task_id空；caller报修人/技工/经理字段没有形成可信登录。state.boot-bak等于各seed原state全文。当前state被判不完整回默认的行为沿用前序挂账，不新扩M6无关P1。未认证缓存正文没有出现在PNG中，仅支持此负例，不证明登录后的授权全链。
11. legal_reminder_statuses四status/合法数值完整载入、pending=false；history_source_cache合法一项提醒载入。invalid_member_middle与malformed_marker整份拒、内存空、dirty/pending=true；原提醒与recover逐字节相等。**PASS加载/保护子项，未执行恢复按钮、通知、去重或取消。**
12. phase/history两缓存在boot进入内存，但**输入items[0].refs有两项，运行后state同条refs=[]**，两原缓存盘均未变。来源集合保留。此为原生执行的加载丢引用反例，详见D03-B2；不是模型生成或授权泄漏实证。
13. 六日志场原ai_requests字节保全、启动渲染不坏；AI_REQUESTS_LOG/AI_LOG_CORRUPT未暴露在结果或state，不能证明合法出处已恢复、STALE已拦或NO_SERVICE动态毒化已观测。两者只作源码裁决与运行未测边界，绝不把文件未变当恢复通过。
14. 12场无model_proxy_stats、proxy-stats.json、模型注入或billing_error，符合needs_model=false；没有模型编造事实的实证，也没有模型正确性的证据。坏marker/矛盾回执保全，未认证boot未消费，不能当收藏对账成功。

## 必需检查

|检查|独立操作/期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/本地安装|请求、资源、signature、running包一致|全资源与冻结候选一致，本地验签/加载成立|PASS该子项|R/H各包/MANIFEST；A；E/offline-verify.json|
|隔离/回收/禁用程序|profile/probes、NONE、空PGID、无允许执行禁程序|12场均成立，osascript内核拒执行|PASS；R-M6-02关闭|H各result/profile/denials；A|
|零解析/原生渲染|冷盘/异常盘真实作品渲染|12场零本轮诊断，登录可见|PASS启动子项|12logs/24PNG；A|
|D02合法/坏盘加载|四状态合法加载；非法中间项整份拒/原文备份|两类均成立|PASS加载保护子项|legal/invalid/malformed的state/盘|
|D02恢复出口与两分支|认证后可达/点击/失败保留/读回|未认证，没执行恢复|NOT_RUN；输入步骤BLOCKED|R/schema/PNG|
|三角色首次任务/下一步|可信角色搜索/项目/追踪同task|三caller负例，没有可信角色业务|NOT_RUN；可信文本通道BLOCKED|state/PNG|
|D04收藏隔离/故障对账|原key恢复、坏marker/矛盾反馈准确、version不增|源码子项保留，原盘保护，没执行收藏/消费者|NOT_RUN；精确故障/复开调度BLOCKED|E回归；H marker/actions/tasks|
|提醒通知/去重/旧约/跳回|真实注册→重开→去重→取消/撤权|只发生启动加载|NOT_RUN；复开/动态调度BLOCKED|R/H业务盘|
|D03完整阶段/出处|结构一致、重开不丢refs、合法失败诊断不毒化出处|来源字段源码不匹配；原生load丢refs；日志自产/恢复不兼容|FAIL原D03；真实模型链NOT_RUN|源码；B；phase/history盘/state|
|真实模型/人工继续|三链真请求、有据/失败可继续、不直接写业务|模型0次/真人输入0次|NOT_RUN；可信输入步骤BLOCKED|R/H全部无modelstats|
|原生视口/150%/键盘|实际客户区和主要操作可达|只登录图/外层尺寸，无放大键盘|NOT_RUN；输入/放大设置步骤BLOCKED|PNG/cmd/schema|
|直接回归|已关函数/加载/冷启动不回归|10函数段未变，零解析/保护成立；引用新加载回归失败|PASS精确旧子项，FAIL D03新回归|E源码回归；A/B|

**BLOCKED仅用于白名单确切无法覆盖的步骤**：固定宿主schema明确type/key未实现；可用ui_actions依赖本次明确禁止的osascript/自动化；每场仅新盘/启动前seed，无同Store跨进程重开、运行中撤权/迟到交错、精确提交点读/写/state/finalize/清marker故障或150%设置通道。需驱动/宿主在现有授权内提供受控内置输入/调度/观测。没有ABORT，agent沙箱rc71/pgrep rc3不是理由；未执行领域行为记NOT_RUN，不改称启动BLOCKED。

## 缺陷与修复清单

|上轮编号|本轮闭合裁决|
|---|---|
|D-M6-01 / D-M6-05|保持已关精确子项；完整业务未测，不倒推通过|
|D-M6-02|严格类型/完整加载/整份拒/备份保护PASS；恢复入口源码保持；实际恢复仍NOT_RUN|
|D-M6-03 A|实际送模历史来源集合与版本重核源码补齐；实际漂移/撤权NOT_RUN|
|D-M6-03 B/C|**P1 OPEN**：下述三处核心残余；不因作者72断言关闭|
|D-M6-04|四未知分支/坏marker/绑定/清理读回源码保持；真实故障对账NOT_RUN|
|R-M6-01|本地签名/安装/运行资源一致子项PASS；不要求公开发布|
|R-M6-02|**CLOSED于本候选**：独立内核拒执行、全argv/denials/回收与零解析证据成立|
|A-M6-01～03|建议继续挂账，不作为本轮FAIL原因|

### D-M6-03-B1 · P1 / 必修：阶段自身来源 schema 与消费者不一致

- **文件行**：app/bundle/main.splash:3993使用source_versions=[m6_ref_snapshot("task",t.id)]；:4148/:4155返回ref_type/ref_id；:4254/:4255消费task_id、缺即source_task_id_empty；:4423/:4452接load/render。
- **触发**：阶段请求成功、有合法非空references、其余上下文/期限/出处/事实均通过，保存并渲染或重开。
- **预期/实际**：应显示可核阶段正文；生成项没有task_id，来源闸必拒。高置信源码契约反例；本轮未发真模型，未冒称真实模型UI失败。phase_producer_cache原盘/内存确实保留这种来源结构，但未认证未执行该消费者。
- **根因/影响**：引用schema被当成来源集合schema；阻断阶段说明核心（硬2/5，T34/T35/U08）。
- **改法**：阶段自身来源保存task_id/task_version/evidence_version，与历史来源集合统一；refs继续使用ref_type/ref_id完整集合，保留门禁。
- **验证**：真实阶段双引用正常显示→同Store重开正常显示；仅改变或撤权第二引用即失效；原盘/UI一致。不能删除来源校验换通过。
- **证据**：E/main.splash.snapshot、M6-r9-to-r10.diff、source-contract-observations.json；H/phase_producer_cache原盘/state；B。

### D-M6-03-B2 · P1 / 必修：重开加载将全部 refs 变成空数组（独立原生反例）

- **文件行**：app/bundle/main.splash:4327读取it.refs，:4330以refs=(_irefs or [])组装；:4054起全refs重核，:4272缺/空refs拒item_refs_missing。
- **触发/实际**：独立phase_producer_cache、history_source_cache种子items[0].refs均有两条结构化引用；原缓存盘未变，boot后state.m6_history_view.items[0].refs均为[]。源码加载表达式是丢失点；不把数组的or默认写法假定为保值操作。
- **预期**：合法数组逐项保留；缺/坏引用应明确未知，不能默默丢弃依赖集合。
- **根因/影响**：refs加载采用宿主不保留该数组的默认表达式。已有空refs门禁会拒绝缓存，持续设备/阶段建议重开不可用；没有观察到授权泄漏，不能将“安全拒绝”解释成核心功能成立。
- **改法**：显式核_irefs为数组后原值赋给独立变量，否则明确拒/未知；不要对数组使用or []。保留全部refs和版本/权限检查。
- **验证**：隔离双refs缓存冷启动state数组逐字段等于原盘；真模型生成→退出→同Store复开→可信登录后正文/出处可核；仅第二引用变化或撤权后拒，无残留正文。
- **证据**：B的seed_refs/loaded_refs/原盘摘要；H两场home/.octosense/apps/octosense-repair/state.json和runtime/optimization/2026-10-09/M6/r1/sandbox/m6_history_view.json。phase原盘SHA=c546b37ec7288017a57fb67a2d31144065b56d4c4ee75c99e2ad41120eb53ce1，history原盘SHA=bf294c1d89f0f0c20403747fec8db89d5c71374c66419c712f9d302b230a5f06。

### D-M6-03-C · P1 / 必修：自产 NO_SERVICE 诊断与整份出处恢复不兼容

- **文件行**：app/bundle/main.splash:2330/:2342、:2573/:2577模型禁用时rid空写NO_SERVICE；:7358/:7360追加并持久；:7403要求每条rid非空；:7417/:7419整份损坏；:7431禁止后续持久。
- **触发**：隔离盘曾有合法绑定成功记录，再出现应用自身NO_SERVICE空rid诊断，随后重开；或失败诊断先于成功记录。
- **预期/实际**：失败诊断不应成为成功出处，也不应使其他合法出处全部失去恢复能力；源码只要一条自产空rid就整份拒并阻止后续日志持久。**源码FAIL；动态内存恢复结果NOT_RUN。** log_no_service_mixed仅证明格式夹具实际加载未破坏原盘，不证明AI_LOG_CORRUPT已观测。
- **根因/影响**：恢复schema不兼容写入协议，未区分诊断和可核出处；持续建议失败恢复被阻断（硬2/5、T26/T34/U08）。
- **改法**：明确合法无请求失败诊断schema，它不作为出处、但不毒化其他合法记录；成功/STALE仍严格校验身份/项目/task/rid。或统一自产诊断rid并兼容已有记录。损坏保源和出处闸保留，不能改夹具/删除闸替代。
- **验证**：应用实际生成成功＋NO_SERVICE＋成功后重开，成功记录可恢复，失败不能验证缓存；补STALE/坏at/非法中间项/截断反例及原文保全，可观测内存与权威盘一致。
- **证据**：冻结源、E/source-contract-observations.json；H/log_no_service_mixed/ai_requests原盘、所有日志场state/PNG、A。当前AI日志全局状态没有既有观测口，磁盘没变不是恢复成功证据。

### D-M6-02 / D-M6-04 · 原未闭运行项：补验证，勿无依据重写

D02 app/bundle/main.splash:3012/:3081及左栏恢复控件；D04 :3453/:3469/:3714/:3755/:11354。源码修补与r9相同，D02非法提醒整份保护本轮独立PASS，D04坏marker/矛盾回执本轮保全；但未认证没有实际恢复/收藏消费者执行。根因是本次合规输入与复开/故障调度缺口，**不是本轮证明这些函数仍坏**。保留原编号与运行未闭状态，优先提供合法可信登录→恢复两分支/保存失败→收藏固定key对账→同盘重开证据；实际失败后按根因最小修，不改业务版本/造SESSION/final或用新key绕过。证据R/schema、H盘/state/PNG、E/closed-subitem-source-regression.json。影响硬1/3/5、T23/T28/T30、U07/U08。

同D03待调度验证边界，不扩新编号：:7373先置restored，:7377读取失败nil直接return而未设corrupt，后续persist可能覆盖旧出处；:2677阶段refs版本在provider返回后才快照，不能据此宣称飞行中第二引用漂移已核。需精确读失败/请求交错实证；本轮动态结果未知。

## 全部硬验收及相关既有用例

以下采用原文用例定义；PASS只列精确子项，未用历史Python/HTML结果签原生PASS，不改原台账。

|硬验收|本轮结果|
|---|---|
|1 三角色持续追踪/搜索/收藏/重登/项目|NOT_RUN完整可信流程；未认证负例与资源保护PASS子项；D04运行未闭|
|2 三AI真链/失败与无历史人工出口|FAIL D03核心源码及实际refs加载；三条真模型/人工输入NOT_RUN|
|3 提醒恢复/去重/旧作业/跳回|PASS合法加载/坏盘保护子项；实际通知/去重/取消/跳回NOT_RUN；后台常驻未验证|
|4 视口/放大/键盘|PASS原生登录渲染子项；真实工作台三客户区/150%/全键盘NOT_RUN|
|5 一致输入/选择/恢复与P0/38/12归属|FAIL D03持久消费；其余直接源码/加载回归按范围保留；既有标准/未通过来源保留|

|编号/原要求|本轮精确复核|
|---|---|
|G0-F 提醒/后台作业/跳回能力|加载/保护PASS子项；真实后台/通知/跳回NOT_RUN，不签后台支持|
|T17 断线重连/全量回读不二次写|NOT_RUN；没有断线期间业务命令，不以新盘冷启动代替|
|T18 可见任务/事件及无权探测|未认证诊断正文未显示PASS子项；可信列表/搜索/事件/附件探测NOT_RUN|
|T23 重启恢复/通知去重/旧约失效|合法加载/整份保护PASS子项；同Store复开/通知/改约取消NOT_RUN，调度BLOCKED|
|T25 缺失矛盾未知/模型不得写任务或改角色|真模型NOT_RUN；仅caller无认证和业务盘未改，不代签模型安全|
|T26 模型失败/人工兜底|NOT_RUN真实链；D03-C自产失败诊断兼容FAIL源码|
|T28 原生同task操作/回读/重开|启动PASS子项；同task领域操作/复开NOT_RUN，复开调度BLOCKED|
|T29 grant关闭/退出/到期及不继承授权|NOT_RUN；运行中撤权/跳回调度BLOCKED|
|T30 收藏重登/他人隔离/version不变|NOT_RUN完整；D04源码回归及marker保全成立，不能当实际收藏通过|
|T33 多种维修说法泛化|NOT_RUN，模型0次，不把缓存诊断当新描述实证|
|T34 依据缺失/不存在拒建议|FAIL D03阶段source/refs持久核心；模型无历史/引用事实正确性NOT_RUN|
|T35 飞行期间改派改约/旧建议失效|源码补集合/全refs重核；实际交错NOT_RUN，动态调度BLOCKED|
|T36 适配器白名单/内核替换边界|未更换内核；真实适配器/工具链NOT_RUN，不扩大历史结论|
|T38 固定模型/提示/数据/宿主复跑与真值隔离|当前候选/宿主/请求/数据已冻结且复核PASS证据子项；真模型成功失败固定组NOT_RUN|
|U01 三角色首屏当前阶段/下一人|NOT_RUN，全部PNG登录页|
|U02 原话草稿可编辑/补歧义/人工继续|NOT_RUN，前序挂账保留|
|U03 三角色事实/权限/承接者不自验|NOT_RUN，未可信登录，不扩M5业务|
|U04 当前预约/改约提议及冲突过期|NOT_RUN业务；旧子项保持，不扩大重审|
|U05 设备位置/服务空间/来源|NOT_RUN可信详情；D03来源源码核查非此UI验收|
|U06 进度/完工/验收与退回历史附件|NOT_RUN，前序挂账保留|
|U07 重复点击/丢响应/冲突/离线输入身份稳定|NOT_RUN；D04固定key源码保持，真实故障调度BLOCKED|
|U08 空态/长文/附件/无权/过期建议恢复出口|FAIL D03持续建议来源/refs/失败日志；D02实际恢复出口NOT_RUN|
|U09 1280/窄窗/文字放大主动作与错误可达|NOT_RUN工作台/150%；只有三size命令和固定外层PNG|
|U10 键盘焦点/非单色状态/对比实测|NOT_RUN，输入与设置通道BLOCKED|
|U11 真宿主滚动输入面板稳定/真实反馈|登录渲染PASS子项；工作台输入滚动/面板NOT_RUN；短present延迟未作为P1|
|U12 独立完整演示与同版本结果/失败|同版本PNG/权威加载证据PASS子项；完整2–3分钟业务演示NOT_RUN|

## 判定与交接

- **最终结论：FAIL**，原因是原D-M6-03的三处核心残余，不因视觉/文档建议判FAIL。冷启动可用和CLEAN不能抵销阶段/出处持久消费失败。
- 必修清单：D03-B1统一阶段source_versions schema；D03-B2显式保留全部refs；D03-C统一自产诊断/出处恢复schema。保持原编号、权限/过期/出处/坏盘保护门禁，不扩业务。之后补D02/D04原运行未闭及真实模型/恢复相关证据。
- 解阻条件：驱动/宿主提供当前禁止条件内可信内置输入、同Store复开、动态撤权/精确故障调度和结果观测；不用UI自动化/伪SESSION绕过，不要求公开发布或更换计费。真实模型只在needs_model经本机代理、模块总量≤10；真实402/余额不足立即停止并原文记录。本轮0请求，没有该类阻塞。
- 已复验的先前影响：当前候选冷启动/M5解析探针回归零错误；未审M5附件业务，M5 FAIL挂账保留。
- 门禁：仅更新docs/optimization/2026-10-09-desktop/GATES.json中M6 status与审查字段，review_report指本报告；旧r11字段追加到review_history，备份E/GATES.before-r12.json。作者candidate/base/implementation/evidence/test_counts等不替换；其他模块/外部递交/原ACCEPTANCE.json保持。
- **不允许进入下一模块。本轮留在M6修复与补证，不执行M7。**

STATUS=FAIL
NEEDS_ABRAM=no
