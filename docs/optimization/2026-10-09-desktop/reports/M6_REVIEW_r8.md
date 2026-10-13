# M6 独立 Review r8

**最终结论：FAIL。合法提醒文件在当前原生宿主上被误判损坏，跟进恢复未跑通；历史/阶段建议的事实、返回协议与绑定校验仍不完整，收藏待核验恢复也未闭合。8场CLEAN证明隔离与回收通过，不代表核心业务通过。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无子代理。
- candidate_id / base：**M6-r7-worktree / M6-r6-worktree**，由用户交接、请求、实施报告、清单和实际运行包定位，没有按文件时间选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，另有既有未提交变更，均保留。源码SHA-256=`dd3f4a5e8d87cc45bbd6ac38d1bfa63d31a194b1474826173aef1b8e4023c22f`，519600 B / 10747行；bundle digest=`3f17a209a6fb1b88a8aae401051527493833e1c713bde670943d91b53bb09a8f`。
- 作者报告：`reports/M6_IMPLEMENTATION_r7.md`；清单：`runtime/optimization/2026-10-09/M6/r7/CANDIDATE.json`。作者 `build_r2_2104_REQUEST_build_r7` 只作参考；本轮结论使用审查者独立请求的驱动证据。
- 前置：**M5=FAIL，M5-r7-worktree / M5_REVIEW_r8.md**。没有已接受的M5 PASS；按用户挂账裁决继续M6复核，前置如实保留，不修M5、不把历史缺陷重新扩成M6必修项。
- 范围：逐条复核上轮D-M6-02/03/04与直接受影响回归；D01/D05已关源码子项保持；不做无关扩审、不执行M7。
- 快照一致性：第1段冻结的业务源码、manifest/config、候选/报告、harness/schema/profile、宿主、GATES与ACCEPTANCE在本段审计时一致；写门禁前再核。写后仅M6 status/审查字段/审查历史允许变化，见S/final-write-verification.json。
- 宿主：项目内 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 原生执行：外部驱动仅经harness执行本请求，2026-10-12 **04:19:06–04:21:04 +08:00**；8场CLEAN、quit_http、rc0，无ABORT。审查者没有启动launcher、sandbox-exec、pgrep、osascript、辅助功能或其他UI自动化。
- 路由/标题：主会话没有可用Router/指定主模型核验或切换接口、createdAt/改标题接口；不冒称已切换或已实际命名。身份、MiniMax及隔离离线签名已由Abram授权，不是新增授权缺口。
- 已读：第1段AGENTS/CONTEXT/00/01/02/M6/04、实施/清单/上轮缺陷/相关源码差异及原T/U定义；第2段本请求、完整summary/result/profile/日志/denials/MANIFEST、实际运行包与隔离盘、全部请求截图及不同的part图、直接相关源码。
- 已运行：第1段独立官方离线hub verify；驱动8场独立冷启动/异常恢复/白名单能力探针；审查者逐项证据审计。Python用于准备和审计，不移植Splash业务代测试。
- 未运行：可信三角色完整流程、真实收藏/重登、点击恢复、实际通知去重/旧提醒取消/撤权跳回、真实模型三链及人工继续、运行中故障/同Store跨进程重启、150%/完整键盘/演示。领域操作未发生记NOT_RUN；已证明白名单不能表达的具体步骤单列BLOCKED。
- 范围偏差：第1段首批误读取项目外记忆索引，已披露并停止；审查事实全部来自本项目实时源码与证据。本第2段没有显式读取项目外文件，无项目外写入，未读明文凭据或模型密钥。
- 置信度：候选、隔离/回收、合法提醒恢复失败、源控制流 **高**；宿主具体类型原语致因 **未知**；可信完整业务与真实模型事实正确性 **未知**。

## 证据索引与独立核验

- **H**=`runtime/optimization/2026-10-09/M6/native-runs/review_r2_2104_REQUEST_review_r2_2104/`：驱动原始证据，只读未改。
- **S**=`runtime/optimization/2026-10-09/M6/native/review_r2_2104/`：冻结源/配置/门禁/宿主、diff、函数行号、独立Store/seed/验签、审计。
- **R**=`M6/native/REQUEST_review_r2_2104.json`，SHA-256=`cd4c0ed8a8f25d5f5bc8db3d14b2932ef0d70ba75c7cc849f307e776aed0858d`。
- **N**=`M6/native/REVIEW_NOTES_r2_2104.md`：第1段原笔记，没有回改为最终结论。
- **A**=S/native-evidence-audit.json；实际命令 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M6/native/review_r2_2104/audit_phase2.py`，rc0，**3994项证据一致性检查通过，不是3994项业务测试通过**。

1. **MANIFEST 1306项**逐项重算，缺失/不符/重复/漏列均0；summary.request与R一致，harness/template SHA与冻结/当前一致；8个result与summary场序、verdict、退出、时长、计费字段一致。
2. 每场profile_probes.ok=true、apply rc0、场外写探针拒绝且created=false，5个禁读探针全部符合；pre/post_pgrep均rc1/class=NONE/out/err空、pgid_members_after=[]，均CLEAN/quit_http/rc0、无exception/ABORT。
3. 用模板、实际新场目录、记录的原HOME字符串与控制端口重建profile，字节/SHA完全一致；模型代理未放行。HOME/app-data/日志/cache/tmp/config/data/Metal/rinx/octos-home均在各自新场目录。原HOME mtime相等和library_scan空是驱动记录，审查者没有访问项目外原HOME。
4. 写入列表7场127项、manager场125项，排序/唯一性/计数/实际存在/目录约束一致，均少于400而未截断；这是harness按mtime记录的文件列表，不是业务动作数。完整denials重新计数与result一致；remote:*:443、系统Metal缓存及/dev/dtracehelper尝试被拒，不能归为成功外联/外写，也不猜由哪个业务发起。
5. 全部seeded_files与独立seed/mirror全文件SHA一致；installed、hub-mirror及唯一实际`.running`包**所有文件**与S验签包一致。digest_seen_in_seed=true、digest_seen_in_host_log=false如实保留，另以实际包字节定位，不因日志未打印digest错判版本。
6. 每场完整host.log字节数/markers/tail独立重算一致，业务eval **519600 B / view=true**、launch-hub成功，无旧parser诊断或panic。809 B系统窗口eval单列；旧解析/业务全空白子项保持关闭。
7. 8张请求PNG全部实际查看并核SHA；另查看valid_empty_control中不同的part图，其他7张part与各自请求图同字节。全部 **2800×1716**，画面是未登录工作台，登录行下方裁切，所见恢复/AI控件不可见；未展示种子任务正文、联系标记、异项目私有标记或旧建议正文。请求1440/1280/980没有形成不同实际可验证客户区，不签三视口/150%通过。
8. reporter场日志 **:41–42**实测拒绝 `key:Tab` / `type:M6-R2-NONCREDENTIAL`。没有可信登录或真实文字输入。角色夹具仅预定入口，不是三角色可信工作流。
9. 8场tasks与测试账号都与seed逐字节相同，8场事件文件保留同一显式fixture事实。7场空actions被既有迁移变为`[[]]`；manager回执保留needs_verify与原字节，不是假final。8场预存pending_input清空，仍属前序共用恢复挂账观察，不是本轮实际键入后丢失，不新增无关缺陷。
10. **8场原提醒文件与seed同字节，8个.recover与原文同字节**；内存均空、pending/dirty=true、统一“JSON解析失败或顶层非对象”。合法空数组2场、完整四条1场、合法单条1场都失败；坏输入保护原文子项成立，但标量/null/布尔时间成员校验分支没有真正到达。没有运行后续普通写，不声称原文已丢失或重复通知已发。
11. manager的稳定键标记与旧主体建议文件保持原字节，回执仍needs_verify，内存history_view={kind:none}。没有实际模型建议或无权正文展示。该主体预撤权/未登录，不能以“标记未消费”本身证明动态对账失败；D04的剩余必修基于源码缺偏好恢复协议。
12. 全部needs_model=false，proxy/stats字段及文件缺省符合预期；真实调用0，无402/余额/欠费。新私钥0，作者两私钥不存在。没有公开签名/publish/listing/push/Issue/消息/公网部署，没有造SESSION或改原始业务数据。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/前置|冻结、验签、全包与实际running核对|候选与证据一致，前置真实|M6-r7一致；M5仍FAIL挂账|PASS版本定位；前置未满足|S/A/H|
|内核隔离/回收|profile重建、5禁读/外写探针、pre/post/PGID|用户指定限制、结束无进程|8场全部符合|PASS|8 result/profile/denials|
|解析/首屏|launch-hub/capture/完整日志|零parser、业务区可见|8场零parser、未登录工作台渲染|PASS此子项|8 log/PNG|
|合法提醒恢复|合法空列表/四条/单条冷启动|schema合法正常恢复|合法输入也全部报顶层异常，列表空|**FAIL D02**|4正例state/原文/backup|
|坏提醒保护|71/null/布尔due/坏中文原文|原文保留、准确拒绝、可恢复|原文/backup保留，但均在顶层拒；成员校验未到|保护子项PASS；严格schema/点击恢复NOT_RUN|4反例盘/图/A|
|去重/旧约/撤权跳回|合法重复+旧约+其他主体；预撤权|有权主体一份通知，旧作业拒，同task跳回|合法列表未加载，无通知/跳回|加载FAIL D02；实际通知/跳回NOT_RUN|tech/manager场|
|三角色持续使用/收藏|三个预定角色入口、收藏待核验源/盘|可信操作、隔离、重登保留、版本不增|未登录，不能真实输入；无业务命令|业务NOT_RUN；可信键入BLOCKED|3图，reporter:41–42|
|历史/阶段AI与人工出口|源/输入/schema/回包/缓存/保存链|事实有依据、拒迟到/无权、可人工继续|正文/人工控件源已补；协议/事实/绑定/失败反馈仍欠；0模型|源码FAIL D03；真实模型/人工继续NOT_RUN|S traces/main/manager缓存|
|收藏失败与恢复|saved分支、标记读写、既有boot协议|明确拒写准确、同key偏好可对账|假落盘源码反例已修；新标记无消费、generic仅按version|D04 SOURCE-PARTIAL/FAIL；动态拒写NOT_RUN|main:2621/8780/3830|
|真实视觉/键盘|8张原生请求图+1不同part、动作日志|登录/错误/恢复可达、三视口/150%/键盘|登录裁切、恢复所见不可见，实际图同尺寸，key/type拒|渲染PASS；可达未通过；完整视觉/键盘NOT_RUN，键入BLOCKED|9实际查图/report日志|
|受影响回归|D01/D05非注释源、M5→M6 diff与冷启动|已关子项保持、新增影响定位|D01/D05保持；M5字段及共用load实际启动|已关源/解析子项保持；不签前序业务通过|S diff/supplemental/A|

**BLOCKED仅限已证明的白名单能力缺口**：固定发行宿主本轮拒key/type，不能完成可信文本登录/Tab流程；当前请求schema每场新目录、只启动前seed，不能表达同Store跨进程重启、运行中精确writer/commit故障、登录后动态撤权/断线和受控迟到交错。具体通道步骤BLOCKED；尚未执行的领域命令NOT_RUN。8场没有ABORT，已实测合法提醒失败必须记FAIL。解阻需驱动/宿主提供合规可信控件输入、受控注入/重启通道，保持Seatbelt与秘密边界；不需Abram新授权，不用伪造会话或UI自动化绕过。

## 缺陷与上轮闭合

|编号|本轮结论|
|---|---|
|D-M6-01|已关源码子项保持：formatApptLine非注释源一致；真实预约显示未测|
|D-M6-02|**P1 / 必修 / OPEN，原生FAIL**：合法文件也拒绝；损坏备份与保护成立，严格成员/受控恢复未动态证明|
|D-M6-03|**P1 / 必修 / PARTIAL，源码FAIL**：task绑定/正文渲染/人工控件改善；格式、事实、回包/消费/恢复绑定与保存反馈欠|
|D-M6-04|**P1 / 必修 / PARTIAL，源码FAIL**：saved=false准确回退子项关闭；同key偏好对账仍未闭合|
|D-M6-05|已关源码子项保持：数量函数非注释源一致；真实数量/筛选未测|
|R-M6-01|CLOSED保持：独立官方离线verify及实际installed/running当前digest成立|
|A-M6-01～03|建议继续挂账，不因美化/文档/演示建议独立判FAIL|

### D-M6-02 — P1 / 必修：合法提醒文件被误判损坏，恢复核心失败

- **文件与行**：`app/bundle/main.splash:2000–2055`，特别`:2026–2028`顶层门禁、`:2033–2048`数组/成员门禁；`:1969–1983`成员时间类型；`:2060–2119`显式恢复；`:2122–2156`普通保存。
- **触发**：R的valid_empty_control以23 B完整JSON `{follow_ups:[]}`（实际文件有规范引号）启动；或tech_valid_dupes完整1189 B、4个合法对象；manager合法325 B单对象。固定同digest/宿主/隔离app-data，无真实业务或会话。
- **实际/预期**：8场都pending/dirty=true、内存[]、“JSON解析失败或顶层非对象”；合法空数组、四条和单条都无法恢复。预期合法schema正常加载，坏schema整份拒并保护原文、可实际恢复。原文和backup都真实保留，未执行后续写，不称已丢数据。boolean/null场也在顶层拒，不能称其成员validator已经通过。
- **根因**：新门禁假设固定宿主parse_json/typeof结果使用`object/array`字符串，但合法实证不能满足该顶层判断；**具体是parse返回值、typeof表示或调用语义的哪一处尚未知**。不能仅凭源码断言宿主具体返回类型。恢复覆盖仅比字节、不共用schema；普通save不读回，仍须验证宿主错误值/异常语义。
- **影响**：核心可恢复持续跟进停在错误态，硬3/5、G0-F/T23/U07/U08不能成立；重复/旧作业/跳回流程无法继续证明。
- **证据**：H上述场state.json、隔离`runtime/optimization/2026-10-09/M6/r1/sandbox/follow_ups.json`及.recover、完整日志/PNG；A全场对账，S冻结源。作者正例失败现已由独立请求复现。
- **具体改法（Kimi-K3）**：保留已经修好的pending写保护、逐字节备份及失败caller消费。先在固定宿主经驱动harness做最小parse/typeof/fs读写返回值探针，采用实证类型判断，确保合法正例恢复、非法成员整份拒。load/受控恢复共用schema，due_ms明确数值而非排除法；普通写及恢复完成须读回核预期内容/schema再清保护。保留原文/备份、可见错误和可重试出口，不删功能/放宽隔离。
- **验证方式**：冷启动零parser/真实登录界面；独立空数组/合法四条/单条全部能恢复；71/null/布尔due/坏中文均准确拒，字节不丢。补备份拒写/错读和恢复内容不一致，失败保持pending、成功读回一致；可信通道可用后实际点两恢复入口、同Store进程重启、改约取消/撤权/通知只一份/旧作业不活。静态41/41、CLEAN或非法顶层全拒不能代验证。

### D-M6-03 — P1 / 必修：历史/阶段建议未闭合事实与协议，回包/缓存安全缺完整绑定

- **文件与行**：`:1523–1534`回包helper；`:1568–1597`history输入；`:1690–1781`phase输入/引用/回包，特别`:1729–1736`首6事件/summary；`:297–392`provider强制JSON；`:2708–2811`caller/持久恢复/人工保存；`:10479–10565`正文渲染；`:875–881`标准事件结构。
- **触发/实际**：两链system仅`history_only_no_write`/`phase_only_no_write`，未定义返回JSON及items/text/ref/phase schema，适配却强制content[0].text解析JSON。history仅本任务前6条notes、未形成设备历史出处；phase只取前6事件，读summary，而标准logEvent事实在after，没有summary字段。新helper未校验本次rid/request_version/expected_task_id/当前选择及已绑定facts/evidence版本。持久view只存task/kind/ts/items，不存主体/项目/事实版本/到期/合法引用用于恢复消费重核。save_history_view失败仅设dirty，人工caller`:2810`覆盖为“已保存”。
- **预期**：明确两链输入/返回schema，有权历史/最新阶段事件和可核出处；发出固定上下文、回包及渲染/重开都重核请求/对象/权限/事实版本/到期；失败准确并实际人工继续。ID存在/可见不是正文事实证据。
- **改善/动态边界**：真实task_id、部分事实输入与actor/project/task-version/expiry复核、正文渲染与人工控件均已补，关闭这些源码子项；模型不直接写业务的源边界保持。manager旧缓存盘保留、内存kind=none，未泄露，**不把这个无权夹具解释为缓存正常恢复**；其loader同样有object门禁。真实调用0，不断言模型实际虚构、实际格式失败或迟到串任务已发生。
- **根因**：用草稿适配接了两种业务语义，却未定义完整协议/事实映射；读取当前全局pending代替固定本次请求快照；持久视图丢失安全/版本上下文；保存失败没有贯通caller。若A回包时B改写pending而actor/project和A版本未变，helper缺少辨别A/B的校验，这是源控制流反例，受控交错NOT_RUN。
- **影响**：核心历史/阶段AI依据、过期/撤权和失败人工出口，硬2/5、T25/T26/T34/T35/T38/U02/U07/U08。
- **证据**：S/source-traces及冻结main上述行、R的新事实事件after、H/manager文件/STATE与A。无真实模型请求，fixture不算模型建议。
- **具体改法**：只修D03。两链各定义JSON协议，输入提供有权设备历史及最新事件after、明确来源ID；无历史未知、矛盾不编造。固定rid/version/task/actor/project/facts/evidence/expiry传入校验，回包拒错请求，消费/重开重核，保存合法正文和出处而非仅字符串来源。持久层使用实证schema；caller消费保存结果，不覆盖失败为成功。保留已修正文/人工控件及禁止直接业务写，不通过禁用模型换PASS。
- **验证方式**：合规可信入口可用后，三组新描述跑三链；未知/矛盾/不存在引用拒、人工可继续；切主体/任务、撤权、事实或证据变化、迟到不落错对象；权威TASKS不因模型直接改变。真实调用仅needs_model场经harness代理，模块≤10；402/余额/欠费立即停并记录原文/NEEDS_ABRAM=yes。保存失败/重开需核同主体正文、版本与来源。当前不能刺激成功链时仍NOT_RUN，不以代理裸调用代验收。

### D-M6-04 — P1 / 必修：拒写反馈已修，但同key收藏偏好恢复没有接通

- **文件与行**：`:2604–2634`finalize与标记，特别`:2621`唯一标记写路径；`:8780–8808`saved消费；`:3790–3859`bootReconcilePending通用版本对账。
- **触发**：真实收藏已写tasks、receipt finalize失败后重启/重试；标记按receipt_id/task_id固定原动作。动态writer/finalize注入未运行，源码检查真实可达分支。
- **实际/预期**：saved=false现在回退并准确称未保存，此旧反例**SOURCE-CLOSED**；saved=true保持待核验。新marker全源只有写和提示，无读取/恢复消费者；既有generic对账按task.version=expected或expected+1判未提交/已提交，**收藏按设计不增version**，未比较固定偏好预期，不能证明原收藏是否已写。预期同key偏好/回执/标记能读回对账，准确完成或继续needs_verify，不因版本不变误当未执行/制造再次操作。
- **根因**：新写标记没有接入恢复边界，既有增版本业务恢复协议不适用于不增版本偏好。写marker也无读回证明。manager预撤权、没有可信会话，原needs_verify和marker保持是安全保留，**不凭这个原生场断言已经误恢复**。
- **影响**：收藏持续使用、结果未知后重登与可靠重试，硬1/5、T30/U07/U11；核心可靠性，非美化建议。
- **证据**：冻结main上述行、全源marker仅写检索、H/manager回执/marker/tasks原字节、A。没有实际收藏final或动态拒写成功证据。
- **具体改法**：保留已修saved分支与固定目标。沿既有可信命令/回执恢复边界，为togglePin按稳定key、任务/主体、预期pinnedBy结果对账，处理已写/未写/未知；接marker读取及验证/持久保留/成功清理，不能通用只看version。标记写入读回；不要新key盲重做，不要求重写其他模块。
- **验证方式**：可信两主体真实pin/unpin、重登隔离及version不变；tasks拒写准确回退，tasks已写且finalize失败保持偏好/原key/待核验，同Store重启后核偏好与回执准确恢复；无法确认保持needs_verify而不称未执行。预撤权不能消费他人标记；正常输入和故障通道可用后补动态，本轮不伪签。

### 建议与挂账

- 登录行裁切/恢复入口不可见继续关联前序入口与本模块可达缺口，不另增无关美化编号；阻断可信使用时需最小依赖修复。原生截图同尺寸不能代表三视口，150%/对比/完整键盘及演示保留未测。
- 预存pending_input清空、空actions迁移为`[[]]`是前序共用挂账；本轮不顺手修，不把它算实际输入丢失。
- CONTEXT和GATES构建字段中的旧rc71/rc3、身份/provider未裁决文字不是当前阻塞理由；构建历史按只改审查字段保留，本报告给当前证据结论。

## 硬验收与相关既有用例

|硬验收|本轮精确结论|
|---|---|
|1三角色/搜索/收藏/重登/跨项目|真实领域操作NOT_RUN；可信输入通道BLOCKED；D04恢复源码FAIL；未登录不展示fixture私有内容子观察PASS|
|2三链真实模型/无历史/失败人工|D03源码FAIL，真实模型/人工继续NOT_RUN；provider已授权，不写授权阻塞|
|3提醒恢复/去重/旧作业/跳回|合法加载原生FAIL D02；保护原文及backup PASS；实际通知/取消/跳回NOT_RUN，同Store/动态操作通道BLOCKED；后台未证明|
|4视口/放大/键盘|原生渲染PASS子项；登录裁切、入口可达未通过；三客户区/150%/完整流程NOT_RUN，key/type通道BLOCKED|
|5输入/选择/滚动/错误与全量归属|D02/D03/D04核心FAIL；实际其他恢复/交互NOT_RUN；全部既有映射保留、不降标准|

|原用例|本轮结论|
|---|---|
|G0-F|前台合法恢复FAIL D02；后台常驻未验证；实际通知NOT_RUN，不以seed冷启动代后台恢复|
|T17|断线期间动作/重连全量权威回读不重写NOT_RUN；受控断线通道BLOCKED|
|T18|未登录截图不展示异项目/联系人/任务原文子观察PASS；可信列表/搜索/事件/附件查询NOT_RUN，输入通道BLOCKED|
|T23|合法提醒加载FAIL D02；一份通知/已改约旧作业实际NOT_RUN，同Store跨进程重启/运行中改变通道BLOCKED|
|T25|模型缺失/矛盾未知、恶意原文不改角色/不写任务NOT_RUN；D03源问题保留，无实际虚构断言|
|T26|明确真实模型失败与人工继续NOT_RUN；人工控件源改善、保存失败反馈D03仍欠|
|T28|当前同digest安装/running/隔离/解析PASS子项；提醒恢复FAIL D02；真实操作/重开NOT_RUN，同Store通道BLOCKED|
|T29|动态grant关闭/退出/到期及共享卡不继承授权NOT_RUN；预撤权未登录只有限边界观察，动态通道BLOCKED|
|T30|收藏自己的重登/他人隔离/version不变实际NOT_RUN；saved=false源码反例关闭，偏好对账D04源码FAIL|
|T33|新描述真实意图泛化NOT_RUN，0模型|
|T34|未知空间/多候选/无历史及不存在引用真实拒NOT_RUN；D03事实/协议源仍欠|
|T35|实际改派改约/撤权期间迟到回包NOT_RUN，受控交错通道BLOCKED；固定rid/facts/evidence复核D03源码FAIL|
|T36|真实/假适配白名单同组契约NOT_RUN；只实证harness隔离，不声称内核替换通过|
|T38|候选/提示源/数据/宿主固定及证据SHA PASS子项；同组真实模型成功失败复跑NOT_RUN，fixture不代真值/模型效果|
|U01|可信三角色首屏当前阶段/下一人/动作NOT_RUN，文本输入通道BLOCKED；三标签不算三会话|
|U02|原话修改/补歧义/模型失败人工实际NOT_RUN，D03新增人工控件源改善、保存反馈欠|
|U03|同task三主体事实/按权动作/承接者禁自验实际NOT_RUN，不代签M5|
|U04|当前约/改约/冲突/过期真实操作NOT_RUN；D01已关源码保持|
|U05|设备安装/服务空间来源与真实选择NOT_RUN|
|U06|进度/完工/验收/退回历史真实交互NOT_RUN，前序M5 FAIL保留|
|U07|提醒恢复FAIL D02、偏好恢复源码FAIL D04；重复/丢回包/离线/冲突实际NOT_RUN，指定故障/重启通道BLOCKED；预存输入清空挂账|
|U08|原生未登录空态渲染PASS子项；恢复FAIL D02、人工保存反馈D03源欠；实际重试/无权/过期/附件出口NOT_RUN|
|U09|真实PNG检查完成，登录裁切；客户区尺寸未证明、150% NOT_RUN；不拿HTML或--size当视觉通过|
|U10|key/type实测拒，可信键盘步骤BLOCKED；完整键盘/焦点/颜色非唯一区分及实测对比NOT_RUN|
|U11|launch/capture真实渲染PASS子项；输入/滚动/切面板及动作反馈实际NOT_RUN，文本输入通道BLOCKED|
|U12|同版本2–3分钟独立人员演示NOT_RUN，不以截图或CLEAN代签|

## 判定与交接

- **最终结论：FAIL**。精确范围为冻结M6-r7在固定发行宿主的上轮缺陷复核及8场独立直接回归。
- **必修：D-M6-02、D-M6-03、D-M6-04**。优先使合法提醒在原生恢复，再闭合两链协议/事实/绑定及偏好对账。已经关闭的解析/全空白、正文/人工控件、saved=false反馈、固定目标等子项不要求重写。
- **阻塞与未测**：可信key/type、同Store跨进程重启、运行中精确故障/动态撤权/断线/模型交错缺已验证白名单通道；实际领域流程和真实模型记NOT_RUN。需要驱动/宿主能力，非Abram新增授权。
- **前序回归**：当前共用load/业务渲染、M5→M6差异、D01/D05已关源码直接回归完成；不签前序可信业务通过，M5及其他模块门禁不改。
- **门禁**：仅更新 `docs/optimization/2026-10-09-desktop/GATES.json`中M6 status与审查字段，review_report指本报告、候选指M6-r7；旧审查字段追加history，构建字段/其他模块保持。写后验证见S/final-write-verification.json。
- **台账**：不修改 `docs/build-loop/ACCEPTANCE.json`，本轮逐项结果登记M6 review_acceptance/review_hard_acceptance，保留原P0/38业务/12UI及历史来源，不把后端旧PASS/作者静态PASS改解释为原生PASS。
- **不允许、不执行下一模块。** 留在M6按上述编号最小修复并补合规验证通道。新授权待办0、真实模型计费错误0。

STATUS=FAIL
NEEDS_ABRAM=no
