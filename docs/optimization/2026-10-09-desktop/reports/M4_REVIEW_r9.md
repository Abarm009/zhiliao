# M4 独立 Review r9

**最终结论：FAIL。** 七场独立原生运行均渲染工作台、零解析/运行错误，登录行完整，原文、确认意图及动作键保留；三种旧锁启动反例通过。旧空白/解析/裁切/原文丢失子项不再列为当前失败。两个坏任务盘仍未进入待恢复状态，旧原子互斥缺口仍在，B-M4-01、D-M4-03 未完整闭合。真实 M3 工单到预约确认/开工主链尚未执行，没有可信三角色业务证据；不能 PASS。不执行下一模块。

## 审查对象、环境和范围

- 审查者/日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；两段式 r1_0937，无子代理、无业务代码修改。主会话实际 Router/model 及 createdAt/标题工具不可核验，未冒称已切指定主审型号或完成命名。
- **最后正式 M4 candidate_id=M4-r7-worktree，base=M4-r6-worktree**；作者报告 `reports/M4_IMPLEMENTATION_r7.md`、清单 `M4/r7/CANDIDATE.json`；main=5430cc10…/480580 B。M4 上轮为 `M4_REVIEW_r8.md`。没有新的 M4 构建交接。
- 本轮按用户“首轮先审当前代码”授权，冻结并审查共享 **M3-r8-worktree** 内容；诊断快照标识 **M4-current-M3-r8-cc193cf0-review-r9**，**不是新建或接受的正式 M4 构建候选**。当前 main=552591 B、11344行、SHA256=`cc193cf0a5015d8475167403a125def3a183efb17dd13336453de47f4d0fe7e8`；四源对象均与M3-r8清单一致。HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty。
- 差异 E/M4-r7-to-current.diff，2824行，明确比较旧M4正式内容与当前共享内容；不将全部共享差异归属于本轮M4实现。候选依清单/内容/请求联合定位，不按mtime选版。
- 前置 **M3=BLOCKED / M3-r8-worktree / M3_REVIEW_r10**，M2=FAIL/M2_REVIEW_r10；不存在已接受PASS的M3。按用户前序挂账裁决继续局部复核，未修改前序门禁。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`。
- 本轮运输包digest=`fbcb68672e3c1fa85f48cce4667303c5df562c73dc8c27b00eaa4c8d8370e4f0`；复用已授权隔离离线catalog，本轮新私钥0。签名manifest仅integrity及官方null默认字段与工作树不同，业务id/version/capabilities/network一致；不声称manifest全字节相同。
- 驱动沙箱外原生执行 **10:19:40–10:21:16 +08:00**，7场CLEAN、quit_http/rc0，无ABORT。审查方没有自己启动launcher/harness、sandbox-exec/pgrep预检、--help、osascript/辅助功能或其它UI自动化。
- 第1段读取实际AGENTS/CONTEXT及00/01/02/M4/04、上轮缺陷/作者清单和证据、前置与19项T/U定义；第2段读全部summary/result/profile、完整host.log/denials、MANIFEST、权威盘，目视七张请求PNG及不同的future场part图。只查原B01/D03/D04及直接受影响回归；不扩审其它模块。
- 实际审计命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/native/review_r1_0937/audit_phase2.py`，rc0；**4958项证据一致性检查，0失败，不是4958个业务用例PASS**。
- 未运行：可信登录后实际填写/接单/服务设备绑定/预约/开工/改派/改约、提交点故障与同盘重开、双上下文业务并发及真实AI交错。全部needs_model=false，**本轮MiniMax请求0**，没有402/欠费。不得以合成seed或未认证hint代验。
- 审查起止15个保护输入、159个seed/mirror保持；写门禁前再核。只写报告、审查证据与M4审查字段，原ACCEPTANCE保持。第1段误读项目外记忆索引已在N披露，未作为本报告事实/版本/验收来源；第2段材料均来自项目内。

**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r1_0937_REQUEST_review_r1_0937/`；**E/**=`M4/native/review_r1_0937/`；**A**=E/native-evidence-audit-r9.json；**N**=`M4/native/REVIEW_NOTES_r1_0937.md`；**R**=`M4/native/REQUEST_review_r1_0937.json`。短路径均相对 `runtime/optimization/2026-10-09/`；报告短路径相对本桌面文档目录。以下源码行指E/source.main.splash，当前工作树与其相同。

置信度：版本/摘要、盘面、日志、截图可见内容、锁恢复及非原子源码路径，高；截断JSON被宿主宽容解析的具体内部产物，中（本轮没有输出解析中间值）；未执行的可信业务、真实并发/模型结果，未知。

## 独立原生结果与证据核对

|场景|日志/截图|权威结果|本轮判定|
|---|---|---|---|
|fresh_no_lock|552591 B业务view=true，零错误，完整登录行|新原文/确认意图/key保留，actor=null/token空；tasks.lock仍不存在；任务/事件/回执不变|冷开及盘面保留PASS；真实首次命令NOT_RUN|
|future_foreign_tech_lock|同上；final/part时钟不同|未来他人锁逐字不变，伪持有token清空，业务盘不变|D03 future启动子项PASS；实际同actor重入命令NOT_RUN|
|unknown_manager_lock|同上，仍未认证|NOT_A_TIMESTAMP锁保持，state=unknown_kept且有说明|D03 unknown启动子项PASS；说明可见全流程NOT_RUN|
|stale_reporter_lock|同上，仍未认证|stamp=1→空，state=released及原stamp说明，业务盘不变|D03 stale启动子项PASS；不是预约过期验收|
|truncated_tasks_manager|零错误、部分列表仍“初始化”、详情普通待选/权限提示；未见对应恢复说明|截断tasks主盘及有效recover=[]均保持；**tasks_pending_recovery=false、why空**|B01恢复入口/检测FAIL；未观察到备份覆盖；实际拒写命令NOT_RUN|
|incomplete_task_reporter|同截断场可见内容，零错误|仅id任务保持，无recover；**tasks_pending_recovery=false、why空**|B01不完整记录恢复FAIL；实际提交命令NOT_RUN|
|forged_manager_cross_project|完整登录行，当前任务不在可见范围，没有展示伪设备/业务动作|saved伪经理清actor=null；跨项目OPEN、账号/事件/回执全部原样|未认证伪主体冷开负例PASS；不代三可信角色/设备拒绝|

1. **MANIFEST.sha256 1125条**全部独立重算；无重复、缺项、额外文件或摘要差异。summary完整request与R一致，全部7个摘要结果与各result一致；harness/template/binary摘要匹配冻结输入。
2. 每场profile重建后与模板逐字一致；probes.ok=true，apply rc0，场景外写探针拒绝且created=false，五禁读探针均拒；pre/post_pgrep均NONE、最终PGID成员空。运行中7份快照均只列对应宿主，library_scan为空，驱动记的真实HOME/.octosense mtime前后不变。审查方只核记录，没有访问真实HOME复测。
3. 命令、尺寸参数、动作、env、完整seed清单与摘要逐项一致；HOME/app-data/cache/config/tmp均在对应新run内。本次仅launch-hub/capture；全部完整运输资源的mirror/installed/唯一.running副本与冻结签名包逐字一致，业务eval均在各host.log:43，不把另一个809 B系统视图当业务根。digest_seen_in_seed=true/log=false符合实际；marker不是加载证明。
4. 七个请求capture均存在，sha256与记录相符，七张全部目视；共14个PNG，6组part与final同字节，future组不同。初次审计错误假设part必等于final，已改为核各自PNG/摘要并另看part：同一未认证业务界面、时钟10:19/10:20不同，不是capture记录不一致；不将该审计假设记为业务缺陷。
5. 前6场PNG=2560×1230，forged=2560×1606，均为屏幕截图。--size 1280×800/1440×900/980×760只证明启动参数，不能证明业务客户区布局或150%验收。登录行完整可见是本图实际事实，不意味着已登录、已填写或控件恢复已验证。底部部分区域不在捕获可见范围，不能推断其绝无控件。
6. files_written_count按R顺序为**124/124/124/125/124/124/124**，完整列表未达400截断上限；逐项存在、唯一、有序且在run内。该列表按mtime生成，含包/缓存/截图/状态等，不是124次业务提交或完整系统调用追踪。七场任务/动作/事件/合成账号原字节均保持；唯一预期锁变化为stale回收。
7. 完整host.log字节数/tail/markers独立重算一致，七场0[E]/panic/unknown-action，tick_exception_count=0。新原文、confirm_intent_id、action_keys及panel逐场与seed一致；这是磁盘保留与冷开恢复子项，未认证图不能证明登录后zh_input可编辑控件恢复成功。
8. 全部sandbox-denials日志读取并按harness同一规则重算summary一致。记录包含被拒的443外联、系统Metal缓存、/dev/dtracehelper尝试及appleeventsd读取宿主文件拒绝；这是拒绝记录，**不是成功外联/外写**。duplicate reports及时间窗口汇总不能当精确网络请求数。指定隔离回收证据范围PASS；没有已证成功违反隔离的原生行为。
9. 全部needs_model=false；result没有model_proxy/model_proxy_stats字段，env无代理地址/MM_KEY，summary各billing_error=null。这是未启用代理模式，不捏造统计对象；0新增真实MiniMax调用/欠费错误，T35未运行。
10. 新私钥0；复用授权离线catalog/本地安装件，build_r8隔离working.key/anchor.key仍不存在，原删除证据保留。未读取明文真实账号/provider密钥，没有公开签名/publish/listing/push/Issue/消息/公网部署。本轮原生证据不能代替尚缺的业务链。

## 必需检查

|检查|独立操作/期望|实际|结果/证据|
|---|---|---|---|
|版本与前置|按清单冻结、核包/宿主/运行资源；前序已接受PASS|当前M3-r8字节一致，旧M4正式候选不同；M3仍BLOCKED|内容证据PASS；前置未满足并挂账，A/N|
|真实UI主链|M3同任务创建→接单→服务设备→具体预约提议/合法确认→开工|只有冷开，无可信输入/业务动作、无新增事实|NOT_RUN；输入控制具体BLOCKED，R/A|
|硬1权限/设备服务|合法关系成功；无资格/越权/假设备/仅安装相同拒|伪saved主体冷开清除、不可见；实际业务命令未执行|限定未认证负例PASS；完整硬1 NOT_RUN|
|硬2预约规则|提议不直升、合规确认、过期/跨项目/改约拒绝|源码守卫保留，无提议或确认|NOT_RUN，A业务盘不变|
|硬3真并发|两可信同盘同步接单/重叠确认唯一成功，相邻均可|仍普通read/write/read；逐场新盘顺序运行不覆盖调度|D03源P1未闭合；动态BLOCKED|
|硬4开工/旧授权|无设备/无有效预约不能开工，改派旧技工拒|没有真实开工或改派|NOT_RUN，旧守卫子范围保留|
|硬5首屏/填写/回执|三个可信角色可理解可填可确认、与权威一致|未认证首屏渲染/登录行PASS；坏盘恢复检测FAIL，无可信角色/提交|B01恢复子项FAIL；三角色主链NOT_RUN|
|改派/改约旧确认/AI撤销|旧累计编辑不得复活，新绑定可恢复，迟到建议拒|D04源码精确反例保持关闭；未发生实际交错|SOURCE-CLOSED限定范围；动态NOT_RUN/交错BLOCKED|
|锁启动恢复|future/未知/stale及旧token|future/未知原文保留，stale回收，token清空|PASS限boot子项，A|
|失败恢复|截断/不完整tasks保盘、pending禁写、可用出口|盘面保全但pending=false，未给相应恢复证据|FAIL检测/恢复子项，B01；实际拒写命令NOT_RUN|
|隔离与回收|profile/probes、env/denials、PGID/退出|全部满足记录范围|PASS，A/各result/profile|

### 既有用例逐条结论

|用例|本轮结果及精确边界|
|---|---|
|T04|BLOCKED：白名单/harness没有两可信上下文共享隔离Store同步接单；D03源缺口仍在，未实测双成功|
|T05|NOT_RUN：技能/项目拒绝与经理分配事件；伪saved主体不代验|
|T06|NOT_RUN：改派旧预约取消、ACCEPTED/新技工、旧技工拒；D04守卫保留|
|T07|NOT_RUN：编码/载荷等价，伪/跨项目/归档设备实际绑定|
|T08|NOT_RUN：合法服务空间正例、仅安装位置相同负例|
|T09|NOT_RUN：无设备开工、处理中技工禁换、经理更正旧新值理由|
|T10|NOT_RUN：提议不直升及报修人/非报修人确认|
|T11|BLOCKED真正同盘同步确认；实际跨项目重叠及相邻确认NOT_RUN|
|T12|NOT_RUN：待改约保旧、新确认替代、拒新保旧；旧SOURCE-CLOSED子范围不冒充动态PASS|
|T13|NOT_RUN：提议过期410、无timer仍拒、客户端假时钟；锁stale不代验|
|T14|NOT_RUN：实际具体上海日期/UTC换算/歧义/end<=start；真实输入通道BLOCKED|
|T15|NOT_RUN：旧version409/刷新/防覆盖/百分比拒；冷开原文/意图/锁保留仅子项PASS|
|T31|NOT_RUN：取消释放预约/保历史、终态拒开工/验收、再次故障新关联任务|
|T35|D04旧epoch反例SOURCE-CLOSED保持；真实生成期间改派/改约、迟到回包/新绑定动态NOT_RUN，受控交错BLOCKED|
|U01|未认证首屏/完整登录行子项PASS；三可信角色待处理/下一处理人NOT_RUN，不再沿用旧裁切FAIL|
|U03|NOT_RUN：三可信角色同任务事实/动作权限/不能自验|
|U04|NOT_RUN：实际当前预约/待改约/冲突/过期投影；坏盘恢复错误出口FAIL归B01|
|U05|NOT_RUN：真实设备选择、安装/服务/来源分开展示|
|U07|冷开原文/意图/动作键保留PASS；坏任务盘恢复检测FAIL；重复提交/丢响应/旧版本/离线命令NOT_RUN；受控提交故障/同Store重开通道BLOCKED|

BLOCKED仅用于**白名单确实不能覆盖的步骤**：同SHA固定宿主在M3独立H/restore_unknown_empty_arrays/logs/host.log:40–41明确unknown type/key；本harness源码:224–241逐场新目录/Store，request.schema没有双上下文共享同步、同盘重开、精确故障或模型回包交错调度。本次没有ABORT，不以agent内rc71/rc3或“宿主无法启动”判BLOCKED。尚未发生的业务命令记NOT_RUN，可运行且实际失败的坏盘子项记FAIL。

## 旧缺陷闭合与本模块修复清单

### B-M4-01 — P1 / 必修 / PARTIAL：入口已改善，坏任务盘仍不能进入恢复

- **关闭子项**：七场零parser/运行错误、工作台渲染、登录行完整、持久原文/意图/key保留；旧r8的ok保留字、裁切、清空和catch作用域错误均未再出现。不要求再次重写这些已验子项。
- **文件与行**：`app/bundle/main.splash:1099–1103`成员schema、`:1246–1264`load解析/判定、`:1107–1125`恢复标记/banner；相关UI恢复入口`:10252`起、tick`:11316`起。精确冻结副本E/source.main.splash。
- **触发**：独立R的truncated_tasks_manager新盘装`[{"id":"review0937-truncated","appointments":[`及既有有效recover=[]；incomplete_task_reporter新盘装`[{"id":"review0937-missing-required-fields"}]`。仅launch/capture，未点击修复、未登录或改运行盘。
- **实际/预期**：两场主盘保持，第一场有效备份也保持，但tasks_pending_recovery=false、tasks_recovery_why空，无相应恢复status；图列表仍“初始化”、详情普通权限/待选出口，未见对应坏盘恢复说明。预期拒不完整/截断权威记录，明确pending/禁普通写，保盘且给有权限主体可用恢复入口；缺少业务字段不能当可用任务。
- **根因**：`:1099–1103`只验证id，合法JSON缺必要业务字段被接受（源码与本轮盘面一致，高）；`:1246`依赖宿主宽容parse_json产物，没有严格截断/完整结构校验（内部产物推断中）。这使后续pending/banner未进入。未认证不可见本身是正确权限行为，不用它单独证明schema失败；pending=false和缺字段是直接证据。
- **影响**：本模块错误/恢复出口硬要求未成立，损坏盘不能恢复到可靠处理入口；tasks恢复未决门禁未置。**实际写命令未执行，未证明坏盘已被业务覆盖或实际越权写成功。** 本旧缺陷直接恢复回归属于P1，不是样式建议。
- **证据**：H两场result、host.log:43及全部零错误；两PNG、home/.octosense/apps/octosense-repair/state.json（pending=false/why空）、原tasks与recover；A.scenarios对应盘摘要及状态，seed可精确重建触发。
- **具体改法**：在当前业务任务schema下核必需字段/类型/状态/预约数组等，独立识别截断/不完整内容；异常明确mark pending，不让TASKS接纳缺字段对象，普通命令禁写并保留主盘和有效旧备份；在未登录入口显示故障说明，恢复操作仍核可信权限。保留已修的零解析/原文/登录路径。
- **验证方式**：同两夹具冷开pending=true且可读故障说明，业务盘/有效备份保持、零循环错误；合规登录后普通命令明确拒且事实/回执一致，恢复经确认与读回完成；再正常盘真实M3→M4主链。不得改任务状态或清盘制造通过。
- **备份细分**：第1段指出mark_corrupt会直接写recover的源码风险，本次没有触发该分支，已有有效recover保持；**不把未发生的备份覆盖写成实测事故/独立P1**。修改检测路径时顺带保有效备份，作为关联回归。

### D-M4-03 — P1 / 必修 / PARTIAL：启动锁反例通过，原子命令边界仍未闭合

- **文件与行**：`main.splash:3666–3730`获取、`:3732–3760`释放、`:3766`命令入口、`:3890`起权威冲突重查、`:4065–4086`owner核验与`:4100`起实际任务盘写；token构造`:3674`。
- **已闭合启动子项**：future完整他人锁逐字保留、NaN未知戳保留并说明、stamp=1回收并说明、saved伪token清空；七场源/盘证据一致，三项本轮独立PASS。获取/释放函数段与旧M4-r7冻结源一致，不再将旧误清写成当前失败。
- **触发/实际/预期**：两独立上下文读空锁后可按A写/核owner→B写/核owner→各写业务盘交错；获取read/write/read、owner核验到写盘之间没有原子边界。预期同盘接单/重叠确认唯一成功且无丢更新，相邻均可。**本轮无实际双成功，当前实际是源码缺口和动态通道不足，不是已观测并发事故。** 作者也承认HOST_PRIMITIVE_BLOCKED。
- **根因/影响**：事后读回不是互斥；actor@毫秒@本地ID_SEQ未证明实例唯一，完整token核验也无法关闭核验到写盘竞争窗口。硬验收3是本模块核心要求，旧P1继续未闭合。
- **证据**：E/source.main.splash上述行、E/M4-r7-to-current.diff、上轮报告与作者r7说明；A三锁实际盘面；R逐场新隔离Store不提供真正同步调度。
- **具体改法**：提供可靠跨实例owner与可核验原子获取或等效单一串行边界，覆盖最新授权/版本/跨任务冲突及任务/预约/回执/事件提交；获取/提交/释放守同owner。区分首次缺锁与真实读失败而保持fail-closed；需宿主原语时向驱动交最小复现及方案，不擅增服务或改运行路线。
- **验证方式**：两可信独立原生上下文共享同一隔离Store同步接单/跨项目重叠确认各一成功，相邻都成功，核唯一承接者/预约/成功回执与事件及重开；保本轮future/unknown/stale回归。fresh_no_lock本次锁仍缺且没有业务命令，首次合法命令是否被拒仍NOT_RUN，不能预置空锁掩盖。

### D-M4-04 — SOURCE-CLOSED限定子项保持；完整原生撤销/恢复仍待验

`m4_invalidateConfirmation:3460`函数段与旧冻结相同；`:3503`清epoch、`:5533–5539`记录本次编辑、`:6086–6101`只消费本次epoch关键字段。改派`:9222`及预约变化仍撤销旧AI/确认；共享来源核验有差异但旧累计编辑集合反例未重新打开。根因修复保留，不新增P1或要求无依据重写。

旧技工实际拒、旧确认实际拒、迟到建议不得展示/采纳及新AI/手工重新绑定恢复仍NOT_RUN/受控交错BLOCKED；后续按T06/T12/T35真实操作核同任务/版本/回执，不把源码关闭代完整PASS。

### 建议与挂账

保留旧A-M4-01/02/03及尺寸取证建议，不据其判FAIL。future场part/final时钟差异、首次fresh启动日志一次320ms ui-hang诊断不证明核心失败，均不列新必修。没有扩展样式、附件、后续模块功能或要求重做已改善入口。

## 判定与交接

- **最终结论FAIL**，精确范围为当前冻结共享源码在固定宿主的7场独立冷开/恢复/锁/未认证负例，以及旧缺陷源码复核。版本/隔离/回收、零错误渲染、输入/意图盘面及三锁启动PASS；B01坏盘恢复、D03原子边界未闭合。
- **必修只有B-M4-01剩余恢复子项、D-M4-03原子边界**。先维持当前零解析/可渲染，再按两项最小改法修；D04旧精确SOURCE-CLOSED子项保留。
- 核心真实主链/可信三角色/预约/设备及权威业务回读尚未成立。构建/驱动需提供固定二进制支持的内置白名单输入、可信合成登录、同Store多上下文同步/重开及受控交错通道，继续独立验证；不允许注入SESSION、手改运行盘、Python复刻或作者声明代验。没有需要Abram新授权的剩余项。
- 前序只做共享登录/输入/锁/坏盘的针对性回归；M2/M3整模块状态不改，M3没有已接受PASS，不让历史挂账阻止局部核验，也不把它写成已满足前置。
- 门禁仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M4审查字段/status、review_report指本报告；review_candidate_id登记本轮诊断快照并在review_snapshot明示正式旧M4候选/M3运输件/摘要/差异。作者candidate_id/base/implementation等保持，旧r8审查字段归档到review_history。其它模块及全局状态不改。
- 原 `docs/build-loop/ACCEPTANCE.json`保持，本轮19项原生精确状态写M4 review_acceptance并保留历史来源；没有把后端历史PASS改称原生PASS。
- **不允许进入下一模块，不执行下一模块。** 留在M4闭合两项必修与真实核心证据，再用可定位新候选独立复审。

STATUS=FAIL
NEEDS_ABRAM=no
