# M6 独立 Review r11

**最终结论：FAIL。当前候选原生冷启动、合法提醒加载、非法提醒整份拒绝与原文保护已独立通过；D-M6-03 的完整依据与持久出处恢复仍有核心源码缺口，另发现原生进程组实际包含本次禁止的 osascript。D-M6-02/04 的针对性源码修补已核到，但恢复动作和收藏故障收敛没有可信原生执行证据，不签关闭。**

- 审查者 / 日期：当前主会话唯一审查者，2026-10-13，Asia/Shanghai；无子代理。实际 Router/gpt-6.1-sol 路由无可核验接口，未声称切换。未修业务代码、未修改 harness、未执行下一模块。
- candidate_id / base：**M6-r9-worktree / M6-r8-worktree**。作者报告 `reports/M6_IMPLEMENTATION_r9.md`；清单 `runtime/optimization/2026-10-09/M6/r9/CANDIDATE.json`。由用户交回的 build/review 请求和清单定位，不按文件时间择版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty工作树保留；本轮开始/结束源与第1段冻结源一致，684541 B，SHA256 `b2df2c0faf850875025321f317e6bf642ac4fef0b9d517f01bf8efad8a8fb1d1`。运输digest `e0cbb9c6b39b3924f24e237060a3438ce75406db76a220edf7ece3c3440d3502`；每场完整mirror/installed/running资源等于冻结运输件。工作树manifest与含integrity的运输manifest分别核验，不混称同一文件。
- 前置实际：**M5=FAIL / M5-r10-worktree / M5_REVIEW_r12.md**，没有已接受的M5 PASS。按Abram后续前序挂账裁决继续局部重审；只回归本候选两处M5解析探针适配的冷启动影响，不重新审附件业务。
- 上轮：`M6_REVIEW_r10.md`。本轮仅复核原D02/D03/D04、已关子项和直接回归；新增R-M6-02只因用户明确要求核原生隔离/禁用操作，属于硬约束检查，不是无关扩审。
- 宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 实际原生执行：外部驱动harness于 **06:01:13–06:03:59 +08:00** 跑审查者独立选择的12场，2批，12/12 quit_http/rc0/CLEAN，无ABORT。审查者未启动launcher或在自己的沙箱运行sandbox-exec/pgrep/osascript；但**驱动记录两场宿主进程组有osascript子进程，不能声称运行期间完全没有该程序**。
- 模型：全部needs_model=false；没有模型代理、endpoint/MM_KEY注入、model_proxy_stats或billing_error；真实MiniMax请求0。没有实际402/欠费；身份/provider/离线签名已授权，NEEDS_ABRAM=no。
- 已读：第1段材料、请求/笔记/候选/差异/源码；第2段summary、全部result/profile/probes、完整logs/denials、MANIFEST、实际运行包与隔离盘、24张PNG的结构/摘要及6种独特画面。
- 已运行：第1段官方离线verify rc0；外部驱动12场冷启动/内置tap/原生capture；第2段只读证据审计。Python审计不执行Splash业务，不生成认证SESSION、业务成功回执或模型效果。
- 未运行：三角色可信登录后的搜索/收藏/当前任务/下一步；实际提醒恢复/通知/去重/旧约取消/撤权跳回；同Store跨进程重开；精确写/读回/state/finalize/清marker失败；三AI真实链/人工输入；实际客户区尺寸/150%/键盘全流程。未执行领域动作记NOT_RUN，仅确切不能由当前合规白名单表达的步骤记BLOCKED。
- 范围记录：第1段项目外记忆索引读取已披露在阶段笔记，未用作判定证据；第2段显式文件读写均在项目内，未读取明文凭据/provider密钥、未改原始业务数据。
- 置信度：候选、证据一致性、加载保护、所见原生登录和源码控制流 **高**；osascript具体脚本/来源调用栈 **未知**；可信业务、真实模型事实正确性与故障恢复 **未知**。

## 证据和独立审计

相对项目根：

- **H**=`runtime/optimization/2026-10-09/M6/native-runs/review_r1_0002_REQUEST_review_r1_0002/`，驱动原始证据，未修改。
- **E**=`runtime/optimization/2026-10-09/M6/native/review_r1_0002/`，冻结源、名义/实际前序差异、函数行号、seed、签名核验与审计。
- **R**=`runtime/optimization/2026-10-09/M6/native/REQUEST_review_r1_0002.json`，SHA256 `7f257a34e933a0dceded16d52b92af9f4cec7315d6c3e59fedb83930a0e4b1c9`。
- **N**=`runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r1_0002.md`。
- **A**=E/`native-evidence-audit-r11.json`；实际命令 `python3 -B runtime/optimization/2026-10-09/M6/native/review_r1_0002/audit_phase2_r11.py`，rc0，**20077项证据一致性检查、0不一致，不是20077项业务测试通过**。

1. summary.request与R全等，请求摘要等于第1段冻结值；场景顺序/批次/result摘要、harness/template/宿主/保护输入摘要均一致。MANIFEST **1978项**全重算，完整集合一致，无重复、缺失、符号链接或越界路径。
2. 12份profile按实际run目录、ROOT、原HOME字符串、记录控制端口和冻结模板重建到字节一致。全部profile_probes.ok=true；外写探针拒绝且created=false；5项禁读探针均拒。未在本轮审查访问那些敏感路径。
3. 所有HOME/app-data/cache/config/tmp/Metal/rinx/octos-home/mirror路径都在新场目录；网络profile仅控制口和Unix socket，无模型代理口。pre/post_pgrep均rc1/NONE/out与err空；pgid_members_after=[]，宿主rc0。原HOME mtime不变/Library scan空是驱动记录，审查者不访问原HOME。**隔离与回收子项PASS不覆盖禁用进程R02。**
4. files_written列表按请求顺序为 **127/127/128/128/128/128/128/127/127/127/127/127**，逐项核排序、唯一、存在及场内范围，count一致、未触400项截断。这是按mtime记录的文件集合，不能当成业务写次数。
5. 全量sandbox-denials按驱动相同规则重计与result一致，含443外联、Metal外部缓存和/dev/dtracehelper拒绝；拒绝不是成功外联/外写。日志中其他系统进程记录不自动归因业务。未放宽Seatbelt换成功。
6. seed清单与第1段冻结件全等，完整mirror/installed与唯一running作品包等于运输件。全部业务seed文件（state除外）原字节未变，tasks/actions/events/accounts/提醒/缓存/marker/诊断ai_requests均保全；没有新业务动作。每场state.boot-bak等于独立原state全文，state中actor=null、selected_task_id空，三caller字段没有形成可信登录。state完整性误判仍属前序挂账，不新增无关M6业务P1。
7. 完整log的bytes/tail/markers重算一致；12场684541 B作品eval view=true，无本轮匹配的parser/splash/type/scope/unknown-action/panic诊断，tick_exception_count=0。809 B系统view不充当作品证据。string_spaces_middle/object_due_bad_marker各有一条约260ms启动ui-hang，未观察到持续阻塞，不升级为P1。
8. **24张PNG**（12 final＋12 part）逐项核签名、CRC、完整长度与摘要，均2800×1696，共6种独特SHA，6种都目视。全部是原生登录页；三种size确实进入命令，但没有三种实际客户区读回，也没有150%。四个空登录tap场的part可见登录按钮按压色；仍未认证、文案“请输入账号和口令”。初始文案相同，不能把按压画面当可信输入/认证成功。
9. legal_four_status_numeric的0/1.5/大整数与四status全量载入、pending=false；reporter_old_cache的合法提醒同样载入。false/空白数字字符串/null中间项、中文截断、对象due五场整份拒、内存空、dirty/pending=true，原提醒与recover逐字节相同；没有因合法前项被先读就部分接纳。
10. 三缓存场未认证时载入诊断正文到内存，原生PNG没有显示该正文；只是未认证保护观察，不能证明登录后出处/期限/引用/事实门禁全部成立。坏marker、矛盾回执与空marker保全；boot因无认证跳过消费者，不能当收藏对账成功。
11. 全部没有model_proxy_stats、proxy-stats文件、模型endpoint/MM_KEY注入或billing_error，符合needs_model=false。离线签名第1段已独立验签且作者两私钥不存在，本轮没建私钥，无publish/公开签名/listing/上传。

## 必需检查

|检查|独立操作 / 预期|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/隔离回收|完整资源、profile/probes、PGID、清单核验|摘要/运行包一致，12/12正常退出，全部CLEAN|PASS这些子项；禁用进程另见R02|H全result/profile/MANIFEST；A|
|禁用操作|应不执行osascript/自动化|两场运行PGID确有osascript，无ui_actions请求|**FAIL R-M6-02**；具体脚本未知|H/fresh_login_only/result:253、object_due_bad_marker/result:259|
|冷启动解析回归|新盘/异常盘零解析、作品真实渲染|12场零本轮诊断，登录页可见，M5探针落盘|PASS启动子项|12log/frames；A|
|合法提醒恢复加载|合法数值/四status完整读取|内存等于seed，pending=false，原文不变|PASS加载子项|legal_four_status_numeric盘/state|
|坏盘保护|非法中间项整份拒、原文保全|五场均成立，recover字节相同|PASS保护子项|五场盘/state/A|
|D02恢复出口/真实恢复|认证后按钮可达、两分支权威读回|只有登录页，未点击恢复|NOT_RUN；可信文本/同Store调度步骤BLOCKED|R/schema；PNG；N|
|三角色/搜索/收藏|可信主体按权限追踪同task|只有caller负例，未认证，无领域操作|NOT_RUN；可信文本步骤BLOCKED|三caller场state/PNG|
|提醒通知/去重/旧约/跳回|真实注册、重启、取消/撤权|只发生启动加载，无通知/业务命令|NOT_RUN；重开/运行中注入步骤BLOCKED|R/H业务盘|
|AI历史/阶段/人工|完整出处、引用变化失效、真实模型不写业务|D03源码仍缺全依据/全refs/持久出处恢复；模型0|**FAIL源码D03**；真实链NOT_RUN|E源码与source-traces；3缓存场|
|D04收藏故障对账|固定key恢复、坏marker/矛盾/清理反馈准确|原缺口有源码修补；未认证消费者不运行|源码子项关闭；故障链NOT_RUN，精确注入/重开BLOCKED|E源；marker原盘/A|
|原生视口/150%/键盘|关键内容及操作可达|24图都是登录；非3客户区读回，无放大/键盘|NOT_RUN；合规文本/放大步骤BLOCKED|PNG/cmd/schema|
|已关子项回归|D01/D05、严格类型/保护不回归|函数原文保持；独立类型/加载保护通过|保持精确关闭范围，不签未测业务|E/closed-subitem-regression.json；A|

**BLOCKED仅用于确切无法表达的步骤**：固定同SHA宿主内置type/key不支持（当前schema明确记录，前序独立同宿主日志有unknown-action）；schema的真实ui_actions依赖本次明确禁止的System Events/osascript。现有每场新盘、启动前seed接口无法表达同Store跨进程重开、登录后动态撤权/迟到交错、精确提交点写/读回/state/finalize/清marker故障与150%设置。需要驱动/宿主提供当前授权内的内置通道和受控调度。没有ABORT，不把agent rc71/rc3列原因；未执行领域操作仍记NOT_RUN，不改称环境故障。

## 原缺陷闭合与必修清单

|编号|本轮裁决|
|---|---|
|D-M6-01 / D-M6-05|已关源码子项保持；实际预约/待处理完整业务仍NOT_RUN|
|D-M6-02|严格类型/合法加载/整份保护独立PASS；顶部可滚动恢复＋空banner收合源码已实现；**恢复可达/操作运行未关闭**，不沿用r10“裁切FAIL”当r9实图结论|
|D-M6-03|**P1 OPEN / FAIL**，完整输入依据变化、阶段全refs及持久出处恢复仍缺；其他新增门禁源码改善范围保留|
|D-M6-04|r10四分支/坏marker/绑定/清理反馈源码子项关闭；**真实故障对账运行未关闭**，不凭未认证marker保全宣布失败或成功|
|R-M6-01|当前离线验签/本地安装资源一致子项保持；不需要公开发布|
|R-M6-02|**P1 NEW / FAIL**，实际出现禁用osascript；只属原生验证路线约束，不要求重写业务|
|A-M6-01～03|旧建议继续挂账，不因皮肤/演示/文档建议判FAIL|

### D-M6-03 · P1 / 必修：完整引用依据仍未贯穿持久缓存消费

**A. 历史来源变化不在快照中。**

- 文件行：`app/bundle/main.splash:2361`起历史输入取EVENT_LOG.after；`:3835/3841`缓存快照；`:4013`重核；`:5889`facts指纹；`:5942`证据版本；`:2499`历史task引用仅存在/项目/可见性。
- 触发：合法设备历史建议引用另一个同设备任务H；其后H发生事件/事实/证据变化，当前任务版本、空间/设备事实不变，H仍可见。
- 预期/实际：应因来源变化失效；现快照只覆盖空间/设备字段与当前任务version/证据数量，不保存H或历史事件事实版本，所以源码缺少识别该变化的输入。动态反例本轮NOT_RUN，不冒称已发生事实泄漏。
- 根因/影响：复用了M3的当前对象快照，但设备历史已经扩大到其他任务来源；持续建议可能继续使用旧事实，原D03完整依据重核未闭合，硬2/5、T34/T35/U07。
- 具体改法：保存实际送入模型的来源集合及逐来源事实/证据版本或规范输入快照；回包、load与render重核同一集合。不要只补当前task.version。
- 验证：真请求引用H后只改变H的事实/证据；应失效且可重新请求/人工继续。对照无变化可重开保留；H撤权/跨项目也拒。必须用隔离数据，结果看真实UI和权威盘。

**B. 阶段正文的全部引用被压成第一个。**

- 文件行：`:2599`起返回验证过的refs；`:3880`只取`_res_refs[0]`；`:3884`整段正文只保存单ref；`:3931`load/render按保存条目重核。
- 触发：阶段正文包含refs=[A,B]且正文依赖B；之后B撤权/事实变化，A与当前任务保持。
- 预期/实际：全refs都应重核；持久结构丢掉B，消费闸只剩A。缺引用时还替代成本任务ID，这不构成模型正文有据证明。源码路径高置信，动态撤权本轮NOT_RUN。
- 根因/影响：引用校验结果在持久化时丢失；可能显示基于不可核第二来源的正文，原D03/T34/T35安全依据边界未闭合。
- 具体改法：每条阶段正文保留完整结构化refs与来源快照，逐条消费；缺/非法依据按未知，不制造合法来源。
- 验证：至少双引用正例及只撤第二引用的反例；同会话和重开都失效，无正文残留，不直接写TASKS。

**C. 新出处闸没有持久请求日志恢复路径。**

- 文件行：`:227`AI_REQUESTS_LOG初始化空；`:3992`出处闸要求同rid成功/非STALE内存记录；`:1533`load及`:778`登录重核；`:7082`push和`:7091`仅写ai_requests.jsonl，全源没有读该文件的恢复路径。
- 触发：真实生成并保存合法模型建议→退出→同Store重开→同主体登录，尚未重发请求。
- 预期/实际：合法持久出处可重核；空内存日志让原rid找不到，合法模型缓存也一律拒绝。当前诊断ai_requests文件在三场字节保全，但未认证且没有实际模型生成，不能把它当端到端复现。
- 根因/影响：持久消费新增强门禁，却未接其权威来源恢复；持续跟进的重开建议核心不可用。拒未知的安全方向应保留，不能删闸换PASS。
- 具体改法：在history消费之前安全恢复/校验落盘成功与STALE绑定记录；损坏/写失败保源并明确未知，日志不应因重开后第一次请求把旧出处全部覆盖。
- 验证：真生成→重开→真登录的保留正例，及缺rid/过期/STALE/坏日志/不同主体/项目反例；请求日志和建议权威盘、UI一致。三组新描述/三链真实MiniMax仍须≤10请求，经needs_model代理；402/余额不足立即停并原文记录NEEDS_ABRAM=yes。本轮0请求。

**上述A/B/C均属原D03的剩余修复，不扩新业务。** 证据：E冻结函数/两份diff，H三个缓存场的盘/state/PNG；后者只支持未认证保护与原盘保全。不得把源码推导写成已运行的泄漏、模型编造或真实失败注入。

### D-M6-02 / D-M6-04 · 原P1：源码针对性修补已核，运行闭合仍缺

- D02文件行`:11965/11972/11982/11985`、`:13306/13310/13314/13318`；源码布局改法成立。五坏盘触发时pending与备份独立PASS，但本轮全部真实PNG停在登录页，没有恢复点击。预期核心恢复可达且权威读回成功；实际运行未测。先补合规可信登录→按钮可见/操作→两恢复分支→保存失败/重开证据；不因本轮未登录重复重写布局，不移除严格schema/原文保护。
- D04文件行`:3373/3389/3471/3535/3567/3608/3634/3660/3675/5335`；四未知路径、坏marker、完整绑定和清理读回源码已补。坏marker/矛盾回执未被未认证boot消费，是保全子观察。预期原key偏好对账准确、他人隔离且version不增；实际真实收藏及写/读回/state/finalize/清理故障、同盘重开都未执行。优先补获准输入与故障调度，逐分支实际核，不用新key、伪final/SESSION或业务version变化绕过。
- 两项根因/影响：现有验证白名单缺可信输入与相应调度，尚不能证成核心恢复；不是已证明代码继续坏。证据R/schema/N、H的盘/回执/PNG和E源码。构建方不做无依据扩修，只补实际验证，失败后按具体根因最小修。

### R-M6-02 · P1 / 必修：运行记录中出现本次禁止的 osascript

- 文件与行：`runtime/optimization/2026-10-09/driver/harness/profile.sb.tmpl:4`允许默认操作且未禁此进程；`native_harness.py:618`仅根据ui_actions选择外部输入，`:695`采集进程组。实际证据H/`fresh_login_only/result.json:253`=`2341 2322 osascript`；H/`object_due_bad_marker/result.json:259`=`2741 2725 osascript`。
- 触发：按本轮R，仅内置launch-hub/taps/capture启动固定宿主；采样出现osascript，无ui_actions请求/日志。
- 预期/实际：用户本次明确“不使用osascript、辅助功能、自动化”。实际存在该可执行进程；CLEAN只核回收/外写等，不含“禁用程序未执行”的判据，两进程均被回收不消除该约束违反。
- 根因边界：profile没有阻止宿主/子进程调用该程序，进程采样只记录comm、没有完整argv或调用栈，不能断言它做了System Events输入。只读检查二进制可见`osascript`与volume-settings字符串，**仅提示宿主状态查询的可能性，不是这两个PID实际脚本的证明**；不以推测的“只读无害”豁免明确禁令。
- 影响：当前运行路线的禁用操作硬约束未满足，不签“全程没有osascript”；这是原生验证/宿主约束问题，不据此捏造业务泄密或成功越界写。
- 具体改法：交驱动查两PID的来源，记录完整受控子进程argv，按本次约束阻止osascript执行（不能放宽禁读/写目录/网络限制或另走UI自动化）。审查者不修改harness或宿主；构建/驱动在当前授权内修验证路线，保留原日志。
- 验证：harness新目录重跑冷启动/独立核心场景，业务零解析/渲染和隔离回收不回归，同时有禁用进程未执行/拒执行的真实证据；不得仅凭no ui_actions、某次采样没出现或CLEAN关闭。技术解决，不需要公开发布/新计费授权，NEEDS_ABRAM=no。

## 全部硬验收与既有用例

|硬验收|本轮精确结果|
|---|---|
|1 三角色持续追踪、搜索/收藏/重登/项目过滤|完整NOT_RUN；D04源码子项关闭，真实故障收敛未测；可信文本步骤BLOCKED；不冒称M5前置PASS|
|2 三AI真实链、失败/无历史人工出口|FAIL D03源码残余；真实三链与人工继续NOT_RUN，合规输入步骤BLOCKED|
|3 提醒恢复/去重/旧作业/跳回与后台边界|PASS启动加载/保护子项；实际恢复/通知去重/旧约取消/跳回NOT_RUN，相应合规输入/重开/调度BLOCKED；后台常驻未签支持|
|4 视口/放大/键盘|原生登录渲染子项PASS；三客户区/150%/主要流程完整NOT_RUN，相应白名单设置/输入BLOCKED；本轮没有“裁切FAIL”实图可沿用|
|5 跨模块一致恢复/全要求责任|已关源码及加载回归保持；FAIL D03/R02；实际跨模块流程NOT_RUN；既有台账与前序历史保留|

|用例|本轮结果与范围|
|---|---|
|G0-F|PASS提醒加载/坏盘保护子项；后台作业/通知/任务意图跳回NOT_RUN；原生路线FAIL R02|
|T17|真实断线重连/全量回读不二次写NOT_RUN|
|T18|PASS未认证不显示诊断缓存正文子项；可信列表/搜索/事件/附件无权探测NOT_RUN；未认证负例不代动态撤权|
|T23|PASS整份合法启动加载与坏盘保护；真实提醒前重启/通知去重/旧约失效NOT_RUN；同Store/动态调度BLOCKED|
|T25|FAIL D03依据覆盖源码；真实缺失/矛盾/恶意原文模型测试NOT_RUN；没有模型业务写证据|
|T26|真实provider失败与人工兜底NOT_RUN|
|T28|PASS同候选原生启动子项；同task真实操作/回读/重开完整NOT_RUN，合规输入/重开步骤BLOCKED|
|T29|grant关闭/退出/到期/共享卡授权不继承真实操作NOT_RUN|
|T30|D04源码修补成立；自己收藏重登/他人隔离/version不变真实操作NOT_RUN|
|T33|三组新描述泛化真实模型NOT_RUN，诊断seed不能替代|
|T34|FAIL D03完整引用与出处源码；未知空间/多设备/无历史/不存在引用真实链NOT_RUN|
|T35|FAIL D03历史来源变化/全refs缺口；真实改派改约/撤权/迟到失效NOT_RUN，交错调度BLOCKED|
|T36|真实/假适配器白名单与替换同组回归NOT_RUN，前序挂账保留|
|T38|PASS源码/配置/宿主/请求/seed冻结子项；真实模型成功失败同条件复跑NOT_RUN；R02路线硬约束FAIL|
|U01|三个可信角色首屏任务/下一步NOT_RUN；只有原生登录页与caller负例|
|U02|真实原话/编辑/模型失败人工继续NOT_RUN；D03持续缓存核心FAIL|
|U03|同任务三主体一致、承接者禁自验NOT_RUN，不代M5签PASS|
|U04|D01预约格式源码保持；实际预约/改约/冲突/到期NOT_RUN|
|U05|设备/服务空间及来源真实选择展示NOT_RUN|
|U06|真实进度/完工/独立验收/退回历史与附件NOT_RUN，M5挂账保留|
|U07|PASS坏盘全文/备份保全子项；FAIL D03持续依据源码；重复操作/丢响应/冲突/离线完整NOT_RUN|
|U08|PASS登录空输入文案/未认证缓存不展示子项；损坏提醒故障在盘中有状态但登录画面没有恢复出口，认证后恢复/人工/无权/附件/过期完整NOT_RUN|
|U09|24张真实PNG均登录页；三客户区/150%/业务主要动作与错误布局完整NOT_RUN；不用HTML或整屏尺寸代验|
|U10|完整键盘/焦点/颜色对比NOT_RUN；合规键盘输入步骤BLOCKED|
|U11|PASS12场零解析/原生登录、空按钮按压子项；完整滚动/输入/面板错误恢复NOT_RUN；R02禁用路线FAIL|
|U12|同版本独立人员2–3分钟完整演示NOT_RUN，不因演示建议单独判FAIL|

## 判定与交接

- **最终结论：FAIL**。依据是原D03三处核心源码缺口和实际禁用进程R02，不因皮肤/建议/演示不完美放大FAIL，也不把全部NOT_RUN冒签PASS。
- **构建方必修**：D03-A保存/重核真实历史来源快照；D03-B保存/重核阶段全部refs；D03-C接通可信持久请求日志恢复。继续保留所有已通过严格门禁与业务不直写边界。
- **驱动必修**：R02查明并阻止osascript路径、补子进程实际证据；保持当前隔离目录/禁读/网络/回收限制，不能用外部自动化绕过。每轮先证明零解析且原生工作台仍渲染。
- **D02/D04剩余交接**：优先取得当前授权内的可信内置输入、同Store重开和精确故障调度；补真正恢复/收藏全分支运行证据。源码针对性子项已闭合，不要求无依据重写。技术缺口不记NEEDS_ABRAM=yes。
- 建议挂账：旧A项、实际客户区/150%和演示证据改进、两条短启动ui-hang，不据此单独判FAIL。M5其他挂账不扩修。
- 门禁仅写GATES.M6.status和审查字段，指向本报告、本候选、本请求及A，追加保存r10历史。构建字段/其他模块保持；`docs/build-loop/ACCEPTANCE.json`未改，相关精确结果写M6.review_acceptance，既有T/U/P0标准和历史来源不删。
- 保护核验：报告与GATES写入后源/manifest/model_config/原台账及其他模块/构建字段一致，证据见E/final-write-verification-r11.json。审计和报告不修改驱动原证据。
- **不允许进入下一模块；未执行M7。** 无公開发布、余额不足或其他剩余Abram专属授权缺口。

STATUS=FAIL
NEEDS_ABRAM=no
