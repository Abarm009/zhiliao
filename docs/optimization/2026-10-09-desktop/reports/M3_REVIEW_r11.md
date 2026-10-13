# M3 独立 Review r11

**最终结论：FAIL。** 本轮5场独立原生运行均 CLEAN，当前共享源码加载成功、解析/运行错误0、登录页正常渲染；四场计划中的冷开/权限/事件保全子项通过，截断 view 来源保全场失败。另有原 D-M3-05 的核心回归：恢复确认分支以非空对象判成功，真实按钮可把未知结果或历史成功包装为当前 OPEN。AI与手工合法确认完整链均未运行，没有真实模型成功证据；不能放行。

## 审查对象与范围

- 审查者/日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai，无子代理，未修业务代码。主会话 Router 实际路由和指定 gpt-6.1-sol 无可用工具核实/切换；未冒称切换。无会话 createdAt/标题写入工具，未冒称已完成标题设置。
- 正式交接 candidate_id/base：**M3-r8-worktree / M3-r7-worktree**；实施报告 `reports/M3_IMPLEMENTATION_r8.md`，清单 `runtime/optimization/2026-10-09/M3/r8/CANDIDATE.json`。按 GATES/报告/清单关系定位，没有用mtime选版。
- **实际受审运行对象是当前共享源码诊断快照，不是原r8逐字节候选**：main **653536 B / SHA256 244a180c4605f85e3fd2a5d7f6b9d4987704080ac017c7182ec09f6d2ee4dc83**，与M2-r10交接相同；原M3-r8为552591 B/cc193cf0a5015d8475167403a125def3a183efb17dd13336453de47f4d0fe7e8。诊断对象标识 `diagnostic-current-shared-244a180c`，不伪称构建方交接了新M3候选。manifest/model_config/identities与r8清单相同。
- HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty。E/candidate-audit.json、E/r8-to-current.diff及冻结E/source.main.splash定位共享差异；不是仅凭HEAD审查。17个相关函数逐段比较：回包/采纳/来源守卫保持；确认/创建/confirmDraft/tick有变化。
- 前置 M2 **FAIL / M2-r10-worktree / reports/M2_REVIEW_r12.md**，无已接受PASS候选。用户挂账要求允许本模块局部重审，不免除放行前置，不修改M2结论。当前M3新增实施交接仍缺失，记候选验收NOT_RUN，不能归为harness ABORT。
- 运输bundle digest **04492599e88fd37807778d172a2e397e0edafb55a4fa2d4d31c51a0cd38167a3**。signed mirror、installed和实际唯一.running的14个资源/场逐字节相同（70项核对）。导出manifest的变化限原integrity/signature运输字段，与app/bundle未签名manifest区别保留，不把两个manifest SHA混写。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense` SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness SHA256 **d597d24ae0a14989f58b022786390916fac2b8fe0a24b11499db2a0d5c4895da**。配置MiniMax/MiniMax-M3/anthropic messages、net声明存在；本轮代理未启，模型请求 **0次**。
- 请求 `M3/native/REQUEST_review_r1_0002.json` 与summary内对象、实际cmd一致。驱动沙箱外执行 **01:49:13–01:50:36 +08:00**，5场CLEAN，无ABORT，逐场15.19～15.24秒、quit_http/rc0。
- 已阅读范围：实际AGENTS/CONTEXT、00/01/02/M3/04、r8实施和候选、上一轮r10缺陷、M2 r12直接依赖、相关G0/T/U定义；只核D01～07、B01及受影响恢复回归，没有无关扩审。
- 实际执行：第1段隔离seed/request准备与离线 `hub verify` rc0；驱动本请求5场原生；第2段审查 `python3 runtime/optimization/2026-10-09/M3/native/review_r1_0002/audit_phase2.py` rc0、资源及PNG逐项核验。审查方未自行启动launcher/harness、sandbox-exec/pgrep预检或额外UI自动化。
- 快照一致：准备后校验快照及本段审计中13个保护输入、117个seed/mirror未变化。准备后才建立phase1-start记录，已在该记录说明，不冒称未做的最初工具调用前快照。门禁写前原态及写后保护检查另存。
- 未运行：可信登录后实际中文输入、三组真实模型、迟到/恶意返回、来源确认、AI及手工合法提交/回执/回读/重开、精确提交点故障。预存原文/来源和伪会话只用于冷开负例，不能代这些路径。

**H/** = `runtime/optimization/2026-10-09/M3/native-runs/review_r1_0002_REQUEST_review_r1_0002/`；**E/** = `runtime/optimization/2026-10-09/M3/native/review_r1_0002/`；**A** = E/native-evidence-audit-r11.json。下文源码行号均指E/source.main.splash，与当前main一致。

置信度：运行对象/摘要/隔离记录/盘面与两项源码根因，**高**；未执行的可信交互、模型效果与完整业务链，**未知**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/运输一致|重算冻结源码、签名运输件、seed及唯一.running|明确运行版本，逐资源相同|当前诊断244a/044925一致；正式r8有差异且未新交接|运行一致PASS；新候选交接NOT_RUN|A、candidate-audit、running-resource-check|
|隔离与回收|核profile/probes/环境、进程组、退出、denials|探针拒越界，pre/post NONE，pgid空|5场probes.ok=true、NONE/空/CLEAN、rc0|PASS（驱动记录范围）|H每场result/profile/denials|
|D01冷启动|5种隔离盘原生冷开、读全日志、目视PNG|零解析/运行错误，业务根渲染|5场653536 B view=true，[E]/panic 0；均见登录页|PASS冷开根/登录页；登录后工作台NOT_RUN|H各log:43、5张final图|
|D02原文/键恢复|三组新原文、[]与空串历史、伪saved主体|内容/意图/key保留，业务不假写|4场有效view原文/intent/key保留，task/action/event不变|PASS盘面子项；控件恢复NOT_RUN|A各view_compare|
|坏events保全/恢复提示|独立好坏好主文件+不同旧bak|全源与备份保全，冻结，真实提示|主353 B/bak208 B保留，bad_lines=353 B完整原主；登录页警告可见|PASS该失败保护及可见提示；人工修复/重开NOT_RUN|H/broken_event_preserve盘/PNG|
|坏view保全/恢复提示|含原文的截断view+不同旧bak|不覆唯一坏源；备份须对应本次原文；有警告|主210 B被覆为2261 B，无原坏源副本；旧bak843 B不变；无警告；**描述文字仍保留**|FAIL来源保全/诊断，D02；不宣称描述丢失|H/broken_view_preserve_input、A|
|未认证权限负例|伪saved经理/token+跨项目DRAFT/假设备/恶意原文|不产生可信身份，业务盘不写|actor/session清空，图仍登录页，task/actions/events字节不变|PASS该冷盘负例；模型回包攻击NOT_RUN|H/forged_saved_context|
|硬1真实三组建议|现场A/B/C及同义句、追问/多候选/无历史|建议随描述变化且有来源|仅准备/预存原文；0模型请求|NOT_RUN，实际输入动作覆盖BLOCKED|独立描述文件、B01|
|硬2 AI确认权威链|真实建议→可编辑草稿→人确认→M2回执/事件/回读/重开|只能权威一致后成功|没有执行；D05外层源码仍误消费未知结果|动态NOT_RUN；结果消费源码FAIL|D05|
|硬2/4手工路径|无模型真实补齐并独立创建/回读|合法手工可提交，未确认无OPEN|无可信登录/填写/确认，0新增OPEN|手工动态NOT_RUN；未认证无OPEN子项PASS|权威盘/A|
|硬3迟到展示/采纳失效|A请求中改B、迟到A；显示后改主体/项目/task/facts/evidence再采纳|展示与采纳分别失效，盘不写|原守卫源码保持，未执行真实交错|BLOCKED于当前允许动作无受控输入/返回通道|B01、原D03|
|硬4恶意/格式/错误模型及兜底|假设备、越权、非法status、恶意原文、格式/自报完成/错误恢复|拒绝业务副作用，手工合法继续|冷盘权限负例已测，真实回包/错误路径未测|NOT_RUN；受控回包注入BLOCKED|D04/D06/D07/B01|
|硬5键盘/取消/重试/元信息|真实中文编辑、取消、重试与provider结果记录|交互可用、秘密不落盘|只冷开；无输入、无请求、无取消/重试|NOT_RUN；有效文本键入覆盖BLOCKED|B01|

5场场景的精确结果：**cold_multidevice_input / cold_unknown_location / forged_saved_context / broken_event_preserve 的计划子项PASS；broken_view_preserve_input 来源保全FAIL**。五場共同的零错误冷开及隔离PASS不代表完整报修模块PASS。

## 原生证据核验

审计 **3575项证据一致性检查、0不匹配**；另外70项实际.running资源比较匹配。它们是记录核对数，不是3575或70个业务用例PASS。

1. **MANIFEST**：814项重算SHA256、唯一性、目录范围与实际文件集合完整性全匹配。未改驱动原证据。117项seed/mirror也与准备清单相同。
2. **summary/result/实际命令**：5场ID/目的/size/动作/seed/digest、时长/退出/batch/结论一致；实际仅launch-hub与单capture，不含ui_actions、type/key、--help或额外自动化。无ABORT。
3. **profile/probes**：按模板与每场路径/控制口重建后逐字相同，摘要一致。写场景外拒绝、5类禁读探针全部拒绝；HOME/app-data/tmp/缓存/日志限每场新目录。profile允许必要的/dev/null及本机unix/control；本轮无模型代理端口授权规则。
4. **进程及隔离范围**：pre/post NONE、pgid_members_after=[]、运行成员均本场组、quit_http/rc0、library_scan无新增、驱动记录真实home目录mtime未变。仅采纳驱动已有记录，未重跑预检/读取项目外真实HOME。
5. **captures**：5/5请求final PNG存在，摘要全匹配；另5个part均与对应final逐字节相同。原图 **2800×1696**，3种不同内容全部目视：正常登录页、坏events带冻结/修复警告登录页、坏view无警告登录页。normal/unknown/forged同图。启动size1280×800不能代签紧凑布局验收；未见登录后工作台/草稿。
6. **files_written_in_run_dir**：各场126/126/126/127/126，逐项存在、唯一、有序、限场景，count与清单相同。它是驱动mtime清单，含运行资源和图像，不是业务写次数。
7. **sandbox_denials**：读全部五份原文并核摘要，按harness规则重新汇总，全部匹配。包含443外联、项目外Metal缓存和/dev/dtracehelper写被拒；重复报告是日志汇总，不当系统调用次数。宿主news日志记7来源失败，不能把其外联拒绝当MiniMax调用或成功越界。没有记录证明成功违反隔离。
8. **host_log_markers/完整log**：字节数/tail/markers重算一致，全部日志读取；业务653536 B view=true、另809 B为宿主其它视图；[E]/panic/unknown test-action均0。cold_multidevice有一次286 ms ui-hang日志，未执行交互，不能据此判核心输入故障，也未把它新增P1。
9. **model_proxy_stats**：5场needs_model=false，result均没有model_proxy_stats/model_proxy，env无代理endpoint/MM_KEY；summary billing_error=null。这是未启代理的合法缺字段，**0请求**，不虚构统计对象或余额信息。
10. **权威结果**：5场tasks/actions/events及合成账号表均与seed原字节相同；只有原预装DRAFT，无新增OPEN、成功confirm final回执或成功关联事件。4場有效view原文/intent/key保留；坏events保全并显示出口；坏view原源丢失而描述保留。预置字段并未执行parseModelReturn/确认函数。
11. **运输与私钥**：每场mirror/installed/.running资源与签名运输件相同，digest在seed，host.log不打印digest，已明确区分“不打印”与“不一致”。本轮不生成私钥；复用M2 r10 keys空，原删除证据可定位。离线hub verify rc0，不替作者hub check rc1或更广准入；本地路径本轮实际加载成立，不要求公开发布。

## 原缺陷复核与修复清单

### D-M3-02 — P1 / 必修：坏view被部分恢复后静默覆写，原来源未保全（独立原生FAIL）

- **文件行**：source:548–556 `loadViewState`以宽容parse结果的对象类型判完整性；590–606并入/置_VIEW_STATE_OK；969–979 `saveState`允许覆盖。相关备份判断558–570也仅认可读旧bak，不核它是否为本次原文。
- **触发**：本轮broken_view_preserve_input新隔离seed，state.json为含原文B的截断对象，210 B；另有843 B可读但不同来源旧boot-bak。用launch-hub冷开，capture后退出。seed/result/主/bak/PNG均在H同名场与E/seeds同名场。
- **实际**：原210 B主被重写2261 B，没有任何同内容的场内源副本；旧bak未变且不含本次坏源；磁盘status=准备就绪，截图无损坏/冻结警告。**可恢复的pending_input描述文字仍在，未观察到描述文字丢失，也没有声称已丢某个原合法intent/key。**
- **预期**：不能把截断解析成部分对象当完整来源；覆盖前保存本次全部源字节并读回核相等，或保持原主不写/冻结，明确恢复状态。已有其它来源bak不能冒充本次备份。
- **根因**：对象类型门禁不证明完整JSON；宽容解析路径绕过坏源分支，_VIEW_STATE_OK被提前置true，saveState将部分恢复与默认值正式落盘。本轮原生盘面与源码结合确定该路径，非无运行条件。
- **影响/严重性**：报修输入/确认意图的持久恢复来源被不可逆覆盖，无法在应用数据中核对原来源完整性或继续修复，违背核心失败恢复边界；沿D02保留 **P1**，不是因视觉建议FAIL。原文文本本场保留，只能关闭该文本保留子项，不能关闭来源/恢复完整性。
- **具体改法建议**：在loadViewState加入完整JSON验证，不只判对象类型或头尾括号；损坏/不能完整恢复时冻结写并显示notice。若允许恢复后继续，先把本次原始字节写独立诊断副本并读回逐字相等，不覆盖旧bak、不把旧可读bak当本次保源成功；只有此证据成立才解除_VIEW_STATE_OK门禁。这是M2共享恢复函数对M3的直接阻断，仅改该问题所需范围。
- **验证**：复跑本场及“坏view无bak / 不同旧bak / bak目录 / 非空截断对象 / 括号闭合但值非法”边界；每场核原主或精确副本、旧bak原字节、警告与输入/intent/key；正常有效view恢复回归不丢原文。按规则交新的冷启动零错误结果与截图，不改布局。

### D-M3-05 — P1 / 必修：恢复确认结果绕过权威消费，未知/历史成功可被包装为当前OPEN（源码FAIL，动态NOT_RUN）

- **文件行**：source:6831–6850恢复分支，createDraftFromPanel返回未确认对象:7236–7242/7274–7276，历史结果:7210–7212；真实按钮12109–12118。正常路径7049–7070有commit_ok/confirmed_open/final_action_id及状态检查，本分支提前return绕过。
- **触发条件**：可信会话中原intent payload属当前主体、当前原文和problem为空；恢复原动作返回non-nil unknown（confirmed_open=false，final_action_id空），或原动作已成功且任务推进为ACCEPTED等。点“确认提交报修”。**本轮5场均未认证，未动态触发本分支**。
- **源码实际**：只看_rr非nil就return true；按钮将status改“✓ 已确认；OPEN 工单 = currentTask().id”。未消费M2未知/历史结果，也不使用返回task_id核显示。历史helper当前已在创建恢复路径调用，其历史事实改善成立，但被外层成功文本覆盖。
- **预期**：unknown/needs_verify保留待核验与原key、不能宣称OPEN；原final历史成功与任务当前阶段/版本分开显示，真实task_id来自权威结果。人工新确认只在本次回执/事件/回读条件成立后显示本次成功。
- **根因/影响**：新增空面板恢复直通分支把“有对象”误作“最终成功”，然后UI固定OPEN文案覆盖M2细分outcome。违反M3核心权威结果要求；该回归已在M2_REVIEW_r12 D-M2-02指出，本轮只沿M3-D05查它的真实按钮消费，不扩审其它M2问题。
- **证据**：E冻结源码、candidate-audit与diff；A确认本轮没有成功回执，**源码确定不等于已经截图到假成功**。置信度：源码根因高，具体原生触达未知。
- **具体改法建议**：恢复分支与正常确认共用显式outcome消费；unknown返回待核验，保持intent/key，不能return true；合法历史成功只显示原action结果及另读当前状态。按钮从经核验结果的task_id/实际阶段渲染，不凭currentTask/固定OPEN文案或模型文字。
- **验证**：可信真实按钮下，同原intent/key覆盖nil、unknown、缺事件、完整final、historical_confirmed但任务已推进；核屏幕、AI_STATE、原task_id、权威盘/同action事件、同键重试，无新增重复任务。AI与手工两路分别验证；现行输入/故障通道缺口见B01。

### 其余原编号与阻断项

|编号|本轮结论|剩余验证/建议|
|---|---|---|
|D-M3-01|原空白/解析诊断关闭；当前5场零错误业务root和登录页独立PASS|没有登录后工作台实证，不把登录页PASS扩大。|
|D-M3-02其它子项|4场有效view原文/意图/key盘面PASS；旧恢复catch错误未复现|控件实际恢复、编辑/取消/重试NOT_RUN；上述坏view问题仍必修。|
|D-M3-03|展示/采纳/首次确认守卫源码保持，未实证动态闭合|受控迟到A、改B、展示后主体/项目/撤权/task/facts/evidence变化，两层分别核。|
|D-M3-04|version_present旧自拒根因源码修复保持；冷盘无会话负例PASS|真实合法无version/quote及恶意来源/假设备/跨项目/status返回parse→apply→confirm NOT_RUN。|
|D-M3-06|缺项/歧义逐字段守卫保持，未现场补齐|追问、多设备显式选择、未知地点/无历史三组真实路径NOT_RUN。|
|D-M3-07|provider配置/代理覆盖/net准入源码保持；0请求|真实MiniMax请求/结果/元信息NOT_RUN；不以配置或作者Python效果代签。|

**B-M3-01 / 具体白名单覆盖BLOCKED**：当前schema包含ui_actions；本次用户明确禁止osascript/辅助功能/自动化，不能使用该实现。固定宿主type/key拒识已由上一轮M3 r10原host.log:40–41实证，当前请求未重复已知无效动作。当前允许的内置launch/tap/capture动作无法完成有效账号/中文文本键入，也没有受控迟到/恶意回包、精确业务提交失败/同Store中途重开通道。**仅这些操作的验证机制BLOCKED**；其它未执行业务项记NOT_RUN，本轮已执行恢复失败记FAIL。无ABORT，不以rc71/rc3解释任何结果，不声称schema绝无键鼠能力。

解阻需驱动/宿主提供**当前授权范围内**实际有效的可信登录/文本输入/响应控制，先证明动作生效，再在新正式M3候选验证核心流程。无需重新裁决身份/provider或公开发布；未知余额不构成NEEDS_ABRAM。

建议挂账：旧A-M3-R10-01缺图在本轮5次capture/5次final范围关闭；旧进程用途参数缺口本轮运行组只有宿主、最终回收成立，不作为新P1。尺寸/286 ms hang只保留范围说明，不做无关扩审或用建议单独FAIL。

## 既有验收逐项复核

|项|本轮精确结果|
|---|---|
|G0-E|NOT_RUN：0原生MiniMax请求；配置/net/离线验签不代真实调用。|
|T01|NOT_RUN真实提取/追问/编辑；有效view原文盘面保留与未认证不OPEN子项PASS。|
|T03|NOT_RUN合法/缺空间/缺联系人/越权提交；冷开未认证业务不写子项PASS。|
|T25|NOT_RUN真实恶意模型返回/未知事实；伪saved经理+跨项目/假设备冷盘保护PASS子项。|
|T26|NOT_RUN真实模型错误与合法手工兜底；手工创建链单独NOT_RUN。|
|T33|NOT_RUN真实三描述/同义表达泛化；只保存独立计划与预存原文。|
|T34|D04旧版本默认自拒根因源码修复保持；来源合法/恶意动态和人工解歧义NOT_RUN。|
|T35|BLOCKED：允许内置动作无法完成真实键入/受控返回交错；双层源码守卫不代动态。|
|T36|NOT_RUN适配器/协议与错误返回真实调用；受控恶意回包注入通道BLOCKED。|
|T37|FAIL（D05权威结果消费源码）；AI/手工final/事件/回读/未知恢复动态NOT_RUN。|
|T38|当前诊断快照、同digest运输/宿主/seed可复核子项PASS；新正式M3交接及完整核心复跑NOT_RUN。|
|U02|有效view原文盘面PASS子项；真实可编辑/解歧义/手工继续NOT_RUN；坏view来源保全FAIL。|
|U07|有效view意图/key保留PASS子项；坏view恢复保全动态FAIL、D05源码FAIL；重复点击/丢响应/冲突完整链NOT_RUN。|
|U08|登录空态与坏events可见冻结/修复说明PASS子项；坏view无准确恢复诊断FAIL；其它错误恢复交互NOT_RUN。|
|U11|原生root/登录页零错误冷开PASS子项；输入、滚动、面板/取消/重试NOT_RUN，实际文本输入动作覆盖BLOCKED。|

## 判定、门禁与后续

- **最终结论：FAIL**。精确范围：M3-r8正式交接之后、实际244a当前共享源码诊断的D01～07复核与直接回归。**不是追溯宣称原r8本体出现本轮新增故障，也不是五场全业务PASS**。
- 必修：**D-M3-02坏view来源保全及准确恢复诊断；D-M3-05未知/历史结果消费与真实按钮文案**。只改直接阻断M3输入恢复/权威结果的共享部分；保持布局与冷开零解析/可渲染，不开始下一模块。
- 实施方补定位清单/差异/哈希与当前M3正式交接；门禁前置M2仍FAIL。补当前允许范围内测试控制后分别实证AI和手工成功/失败链，三组真实模型总预算≤10次，余额不足/402立停并记录原错误。身份账号和provider已授权，无需重开其NEEDS_ABRAM。
- 受影响前序回归只认本轮有效view输入/intent/key、未认证权限、空历史、坏events、坏view的上述精确结果；不代签M2整模块。其它模块字段保持。
- GATES仅改M3的status、review_report/reviewed_at及review_*字段，review_report指本r11；`review_candidate_id=diagnostic-current-shared-244a180c`与`review_handoff_candidate_id=M3-r8-worktree`分开，旧审查字段及原状态追加review_history，门禁写前完整副本E/GATES.before-review-r11.json。作者candidate/base/implementation/build字段与其他模块不动。
- 原ACCEPTANCE.json保持：没有新完整业务PASS，不覆盖38业务/12UI/P0历史；本轮逐项结果写报告及M3.review_acceptance，保留历史来源。最后核验E/final-verification-r11.json。
- 不允许进入下一模块，不提供下一模块入口。
- 本段仅项目内读写；第1段一次项目外memory注册表读取已在阶段笔记明确记录，之后未再读取。未读取/打印明文业务凭据和provider密钥、未改原始业务数据，无网络调用/公开签名/上传/push/消息/公网部署。**NEEDS_ABRAM=no**：没有观察到余额/欠费错误或公开发布需求。

STATUS=FAIL
NEEDS_ABRAM=no
