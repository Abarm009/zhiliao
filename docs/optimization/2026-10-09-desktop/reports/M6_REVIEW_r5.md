# M6 独立 Review r5

**最终结论：FAIL。原 D-M6-02、D-M6-03、D-M6-04 的核心源码缺口仍未闭合。8 场 harness CLEAN 证明隔离/回收通过；本轮审查 seed 安装目录放错，应用未注册，原生业务没有运行。该准备错误属于审查方，不作为产品新增 P1，不用它证明产品解析或业务失败。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-11，Asia/Shanghai；无子代理。
- 交接 candidate_id：`M6-r4-worktree`，base=`M6-r3-worktree`，由 GATES、r4实施报告和r4清单定位，不按mtime选版。
- **实际审查快照**：用户授权跳过首轮构建后使用的累计工作区，main SHA-256=`c683c7a034c8dbdd8c82560332418933482a01b953b0fabea9afeead1663f1d2`，395510 B、8450行；HEAD=`8d730569546cb57310944bb299695134df773b9d` 加既有未提交改动。不是原r4清单的main摘要`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`。不擅自创建已接受新候选；累计差异和冻结文件在S，结论只适用于本快照。
- 作者报告：`reports/M6_IMPLEMENTATION_r4.md`；清单：`runtime/optimization/2026-10-09/M6/r4/CANDIDATE.json`。
- 快照一致：第1段开始/结束、第2段审查时main、配置、manifest、identities、宿主、候选清单一致。GATES写入前与第1段一致；写入后只变M6 status/审查字段/审查历史。原ACCEPTANCE未变。
- 前置：`M5-r5-worktree / reports/M5_REVIEW_r6.md / FAIL`，没有接受的M5 PASS候选。按本次用户前序挂账裁决继续审查，不称前置满足，不修前序。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`；实际8场binary SHA-256均为`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 运行：驱动在沙箱外于16:20:43–16:22:32 +08:00执行本请求；8场CLEAN、quit_http、宿主rc0。审查方未自行启动launcher、sandbox-exec或pgrep，不使用辅助功能/osascript/额外自动化。
- 路由：当前主会话指定模型/Router路由无可用核验/切换接口；不声称已切换为gpt-6.1-sol。createdAt/标题修改接口亦不可用，未猜日期或声称已改名。
- 阅读范围：沿第1段CONTEXT/AGENTS/00/01/02/M6/04、r4 Review/实施/清单和D01–D05相关源码；第2段核请求、全部summary/result/log/profile/denial/PNG、manifest及权威文件，另定位审查seed错误，不做无关扩审。
- 已运行范围：第1段隔离副本catalog verify、官方install_staged/Store重建；第2段证据摘要重算、运行环境/回收/seed内容/日志标记/截图逐项核对。8场只执行宿主启动、launch尝试、两个坐标点击及capture，没有可信登录或业务命令。
- 未运行：真实三角色工作台、收藏/提醒/撤权/跳回/历史建议、业务回读和失败恢复、同盘业务重启、真实模型三链、应用视口/键盘/150%/演示。应用未注册的检查记NOT_RUN，另有白名单能力缺口单列BLOCKED，不沿用agent内rc71/rc3。
- 置信度：摘要/隔离/回收、审查准备目录错误及原缺陷源码控制流 **高**；本轮产品原生业务/视觉/模型效果 **未知**。本轮没有业务解析结果，不能引用M5历史parser错误充当本轮实证。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M6/native-runs/review_r1_1309_REQUEST_review_r1_1309/`，驱动原始证据，只读未改。
- **S**：`runtime/optimization/2026-10-09/M6/native/review_r1_1309/`，冻结源码、diff、函数、seed、离线Store及核查记录。
- **R**：`runtime/optimization/2026-10-09/M6/native/REQUEST_review_r1_1309.json`。
- **N**：`runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r1_1309.md`，保留第1段原笔记；其中“将验证加载”是计划，不是已完成加载。
- **A**：S/`native-evidence-audit.json`，可用S/`audit_phase2.py`重算。A的evidence_integrity=PASS不等于业务PASS。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本、前置、增量|交接三方/HEAD/摘要、r4冻结diff、M5最新Review|明确候选、未提交变化及前置|累计快照可定位；原r4清单不同；M5 FAIL保留|定位PASS；前置未PASS|S/start-snapshot、snapshots、diff；M5 r6|
|harness证据完整性|逐文件重算MANIFEST；summary/request/result对账|原始证据完整且对应独立请求|1186项全部一致，无缺失/重复/未列文件；请求与summary一致|PASS|H/MANIFEST.sha256；A|
|内核隔离与回收|核profile规则/摘要/探针/env/进程/写入/denial|只写新目录、禁读秘密、仅本机外联、无残留|8场全部满足用户规定CLEAN条件；外写尝试被内核拒绝|PASS|各result/profile/denial；A|
|本地catalog/安装|第1段verify/install_staged/Store重建，核当前包摘要与catalog|当前digest隔离安装可行|CLI rc0、源码配置一致；本轮seed安装位置错误，launcher未识别|PASS安装层；本轮launch尝试FAIL R01|S/offline-store-evidence；H/*/logs/host.log:35|
|首次使用三角色|三场launch/taps/capture；看真实图/日志|可信主体登录后可识别当前任务/下一步|只有宿主桌面及App unavailable；没有业务客户区|NOT_RUN；请求入口失败|H/reporter_fresh、technician_fresh、manager_fresh|
|收藏隔离/重登/失败恢复|源码D04+pending夹具、核实际tasks/actions/state|偏好隔离、version不增、异常可对账|D04仍无读回/可靠收尾；原生文件是原seed，未触发收藏|FAIL源码D04；原生NOT_RUN|S/source-traces；H/preference_pending_recovery；A|
|提醒恢复/去重/取消|D02路径+重复/schema/旧预约seed；核运行变化|有效提醒一份、损坏不丢原文、旧作业失效|D02登记可绕过恢复闸；原生提醒未加载/未登记|FAIL源码D02；原生NOT_RUN|S/source-traces；H/reminder_*、revoked_old_reminder|
|撤权/跳回/旧提醒|源码授权过滤与summary入口；真实会话/调用证据|撤权即时拒绝、旧grant不继承|过滤源码子项保持；无登录/撤权/跳回动作，不把预撤权seed当测试|NOT_RUN；动态撤权/同盘复跑能力BLOCKED|S/source-traces；A；R/schema|
|历史依据/阶段/模型边界|比history/phase/recordModelMeta及入口；核代理记录|三链真实事实/引用/未知出口、不直接写业务|两新增链未实现；静态阶段和审计元信息保持；模型0次|FAIL源码D03；真实效果NOT_RUN|S/affected-functions、source-traces；作者r4§2.2|
|原生视觉/交互|逐张看8 PNG，核尺寸/日志/实际客户区|三个应用视口、放大/中文/键盘/异常出口可达|全部PNG2800×1718，只有宿主桌面和错误toast；没有应用布局|NOT_RUN；可信type通道BLOCKED|H/*/frames；A；原宿主type未知日志|
|受影响回归|r4→当前diff、D01/05与D02/03/04函数核对|保留闭合子项，不篡改前序结论|37个m6函数中33全文一致；其余为等价变量/条件改写，未补三P1|源码局部保留；完整原生NOT_RUN|S/affected-functions、diff；本报告缺陷|

### 原生证据逐场结果

|场景|隔离/回收|launch实际结果|业务运行|
|---|---|---|---|
|reporter_fresh|PASS|FAIL：no app in registry|NOT_RUN|
|technician_fresh|PASS|同上|NOT_RUN|
|manager_fresh|PASS|同上|NOT_RUN|
|reminder_duplicate_load|PASS|同上|NOT_RUN|
|reminder_schema_recovery|PASS|同上|NOT_RUN|
|revoked_old_reminder|PASS|同上|NOT_RUN|
|preference_pending_recovery|PASS|同上|NOT_RUN|
|history_no_fact|PASS|同上|NOT_RUN|

1. H/MANIFEST.sha256共**1186项**，逐文件重算：摘要错误0、缺失0、重复0、未列文件0。summary.request与R一致，harness/template SHA与当前文件相同，各summary场景与result的verdict/exit_method/wall_s一致。开始/结束watched文件无变化。
2. 每场profile_probes.ok=true、apply rc0、外写探针被拒且未创建、5个黑名单读探针全部被拒；pre/post_pgrep均rc1、class=NONE、out/err空，pgid_members_after=[]，CLEAN、quit_http=ok、host_returncode=0。无ABORT。profile逐场按模板和实际控制端口重建字节一致，env路径均在本场目录，无模型代理放行规则。
3. 每场files_written_count=109、列表109项、无重复，文件存在且路径留在新目录；这是宿主写入记录，**不是109次业务动作**。原HOME .octosense mtime前后一致，library_scan_new_or_modified=[]。denial全文读取并重算summary一致：宿主remote:443、Metal缓存及部分/dev/dtracehelper写尝试被拒，不能说发生了成功外写/出网。这些宿主拒绝记录不新增产品P1。
4. 全部captured PNG存在且SHA与result/manifest相同，8张逐张视觉检查，均2800×1718，只见宿主桌面和“App unavailable / Register 'hub:octosense-repair'…”提示。请求1440×900、1280×800、980×760不能代应用客户区布局/长中文/150%结论；未沿用HTML测量或旧bundle截图。
5. 8场完整host.log均核：第35行`no app 'hub:octosense-repair' in the registry`；launch/tap/capture参数已被宿主接受，但launched_lines=[]，只有809 B的宿主SPLASH eval，没有395510 B业务main eval，没有业务parser结果、运行副本或panic。日志bytes/tail/markers及digest_seen_in_host_log=false均独立重算相同。
6. 每场`.bundles`中的包字节和当前冻结main/model_config/identities一致，catalog entry manifest/digest一致且预放apps/catalog.json不变；**这仅证明输入一致，不证明宿主接受或运行包**。实际错误位置为home/.octosense/.bundles；应为home/.octosense/apps/.bundles。各场无正确目录、无.running，见R-M6-01。
7. 7个场景各7个业务seed文件、history_no_fact场8个，tasks/state/actions/events/accounts/提醒/索引全部与seed逐字节相同。不能把schema原文没变当恢复保护通过、把重复提醒没变当去重成功、把撤权seed当真实撤权、把pending没变当恢复失败。都没有进入业务程序。
8. 8场needs_model=false，result未提供model_proxy_stats/model_proxy，视为未启动代理而非“模型通过”；无billing_error，真实请求0。没有读取密钥/生产明文凭据，没有欠费/余额或新增授权问题。模型不足的源码缺口仍按D03判定。
9. 第1段未生成新私钥，复用同digest离线签名；前次working.key、anchor.key删除状态已复核。没有publish/公开签名/listing/上传/消息等外部动作。

## 缺陷

### D-M6-02 — P1 / 必修 / PARTIAL：提醒恢复未决仍可被普通登记覆盖

- **文件行**：`app/bundle/main.splash:1496`加载；`:1533`结构异常置dirty；`:1550–1553`仅dirty+空列表阻写；`:1574`成功写清dirty；`:1579–1597`upsert先填非空列表再save；`:1601–1620`register再save；`:1636`/`:1659`失效丢弃保存结果；`:4737`预约调用未消费登记返回。
- **触发**：空/损坏/schema异常或读失败后load进入恢复未决，再正常登记新提醒；另检查关闭/改约失效保存失败传播。
- **实际/预期**：源码register先让列表非空，save仅拒dirty+空，因此可覆盖未恢复源文件并清dirty；预期恢复未决与列表是否非空无关，普通登记/关闭/失效不得绕过，失败必须保持可见并能对账重试。当前原生**未执行该路径**，没有冒称本轮已覆盖文件。
- **根因**：加载损坏恢复与正常写重试共用dirty；内存有新记录被当作恢复完成，保存信号没有贯穿调用方。
- **影响**：原缺陷的提醒数据保护、失败后持续使用仍不成立，阻断硬3/5、T23/U07/U08；不是要求新增后台服务。
- **证据**：S/source-traces中load/save/upsert/register/invalidate、diff；r4旧反例仅为历史辅助定位。本轮schema seed原文保留属于未运行，不能用作该缺陷原生复现。
- **具体改法**：仅D02路径区分“加载恢复未决”与“正常写待重试”；前者在普通写前一直阻写/保留原文及可核备份，显式恢复完成后解除；后者按同记录重试并去重。登记/失效保存结果传到现有UI，不以再save或内存非空清恢复状态。
- **验证**：隔离空/坏/schema/拒读→load→register/dismiss/invalidate，核原文/备份和错误仍在；显式恢复→同动作重试恰一条→同盘重启；改约/取消/撤权不复活旧提醒。发行宿主证据才关闭完整项。

### D-M6-03 — P1 / 必修 / PARTIAL：既定设备历史与事件阶段AI链仍未实现

- **文件行**：`main.splash:1363`history、`:1425`phase、`:4018–4055`请求元信息和当前UI上下文兜底；`:8248`/`:8272`消费端。作者r4§2.2明确两新增链未实现。
- **触发**：接单后请求设备/维修历史/预约占用建议，或事件变化后请求最新阶段；核事实输入、引用、版本、调用和人工采纳。
- **实际/预期**：当前仅有请求审计元字段与静态状态解释，三函数与r4全文一致；没有链②③生产端、事实引用、固定请求版本/过期拒绝、人工采纳和真实请求证据。预期三链真实基于有权事实，缺失标未知、不存在引用拒绝、模型只出建议。真实模型未调用，不能断言模型已经不虚构。
- **根因**：把审计日志和静态兜底当缺失核心功能的替代，旧报告还误称provider未授权。MiniMax/身份选择已经由用户裁决；`:279–310`代理endpoint支持是已有改善，不能替新增链。
- **影响**：硬2明确新增场景缺位，原D03继续OPEN；T25/T26/T33/T34/T35/T38没有完整效果证据。不是因M3一般问题或建议项单独FAIL。
- **证据**：S/affected-functions、source-traces、diff；作者r4§2.2。history seed中的ai_requests.jsonl并未hydrate进内存且应用没加载，不能用它声称过滤已测。
- **具体改法**：只补原D03两既定链，复用已授权M3适配/来源/校验/失效契约；发出时固定task/project/actor/事实版本，不用回包时当前UI派生。补设备/历史/占用及事件依据、引用校验、缺项和人工出口；模型不得直接写业务。
- **验证**：原生三链各新描述、无历史/矛盾/不存在引用、切任务/主体/撤权/事件变化/迟到回包；保留模型/提示/数据/宿主版本，核人工确认与权威结果。仅needs_model经harness本机代理，模块合计≤10，402/欠费立即停止并NEEDS_ABRAM=yes。

### D-M6-04 — P1 / 必修 / PARTIAL：偏好保存仍无可靠读回和异常收尾

- **文件行**：`main.splash:1840`m6_save_prefs、`:1854`tasks直写、`:1857–1860`eager清理、`:1877`saveState无捕获、`:1883`内存final、`:1888`吞回执写错；`:6587`togglePin调用无捕获、`:6597`回旧status。
- **触发**：偏好tasks写后state写失败；final回执写失败；写返回但读回不一致；tasks明确写失败后观察错误UI与下一动作。
- **实际/预期**：源码state异常跳过回执收尾；final写失败吞掉却返回true；没有读回，不能核当前主体偏好与持久动作结果；tasks失败后旧status覆盖错误。预期固定actor/action_id的独立读回和持久结果，未知可见待核验/对账，无假成功或永久pending，version不变，下一动作可继续。
- **根因**：eager cleanup仅解决清锁顺序，未覆盖偏好执行生命周期。累计改动是等价变量/条件改写，没有补收尾协议。
- **影响**：原D04收藏失败恢复与结果核验未闭合，阻断硬1/5、T30/U07/U11；不扩修前序事务系统。
- **证据**：S/source-traces/m6_save_prefs.splash、togglePin.splash与diff。当前pending fixture只作输入，**本轮没有原生故障注入或实际收藏回执**；不拿旧Python适配结论升级原生通过。
- **具体改法**：仅偏好路径捕获固定actor/action_id/原偏好，写后读回区分已执行/未执行/未知，精确收尾并核持久结果；state/receipt失败走可见待核验/对账，稳定键保留，所有退出清理保持。已落盘不盲目回滚，未执行可回退；不要吞错误或恢复旧status遮掉提示。
- **验证**：收藏/取消/双主体/跨项目/重登与同key重试；拒写tasks/state/final回执、读回不一致，核持久动作、偏好、UI和下一命令一致，无版本推进/假成功/永久pending。

### R-M6-01 — 审查准备错误 / 原生证据必需重跑 / 不计产品P1

- **文件行**：`runtime/optimization/2026-10-09/M6/native/prepare_review_r1_1309.py:100`；harness复制规则`driver/harness/native_harness.py:237–239`；宿主参考`M0/r5/source/OctoSense/crates/shell/src/apps.rs:474–482`、`:778–779`。
- **触发/实际/预期**：审查脚本把`.bundles`复制到seed根，harness再复制为home/.octosense/.bundles；宿主app-data根为home/.octosense/apps，要求apps/.bundles。8场均registry缺app、无业务窗口。预期seed与实际OCTOSENSE_APP_DATA契约一致并被registry列出。
- **根因/责任**：审查准备将CLI install-root误当HOME根布局，目录存在/离线may_run/源码hash检查不足以验证launcher寻址。此错误由审查方承担；本轮不改业务来迁就错误测试。
- **影响/证据**：本轮全部原生业务NOT_RUN，launch尝试FAIL；H/*/logs/host.log:35、8张PNG、实际目录和A。本轮无业务parser错误不能称产品解析通过，更不能移植M5旧parser错误称本轮失败。
- **具体纠正/验证**：下一次审查准备把安装副本放seed/apps/.bundles，并先以该apps根做官方Store核验；独立harness复跑，必须看到registry launch、395510 B（或新冻结字节数）业务eval及.running同摘要，之后才做可信流程和结果回读。保留本轮原seed/请求/证据，不能事后移动目录后声称旧场已通过。修正后若当前代码仍解析失败，只依新日志给最小复现。

### 白名单能力缺口（技术BLOCKED子项，不是新产品缺陷）

- 可信文本输入：固定宿主历史`M2/native-runs/review_r1_1309_REQUEST_review_r1_1309/tmp_write_failure/logs/host.log:40`明确`type:u-tech-1`为未知动作。本轮不传凭据、不预装SESSION、不用state.actor/标签冒充登录。需要固定宿主支持并由harness白名单验证输入，才能完成实际三角色/双主体流程；键盘和放大本轮NOT_RUN，不凭未测试`key:`猜其支持。
- 同盘进程重启、运行中写点失败/授权变更：当前request.schema每场新根且没有此类步骤，现有动作不能直接调用业务writer/控制commit边界。相关受控故障/同盘重启/先登录后撤权子项BLOCKED，需要驱动提供隔离且可定位执行/回收/文件变化的扩展证据。静态重启seed不能替实际重启。
- 8场没有ABORT；这些BLOCKED只用于确实未覆盖的步骤。其余当前业务因R01没有执行，记NOT_RUN。agent内rc71/rc3全部不作为本轮BLOCKED理由。

### 建议挂账（不作为FAIL依据）

A-M6-01～03原建议保留，不扩审。建议修正CONTEXT/实施报告旧授权、旧环境阻塞及自测“独立通过”说法，补累计快照准确候选清单。版本已通过冻结差异定位，此清单建议本身不另列P1。M5前置FAIL也未单独作为本模块新增P1。

## 全部硬验收与相关用例

|硬验收|本轮结论|
|---|---|
|1 三角色追踪/搜索/收藏/重登/项目|FAIL D04源码恢复；原生完整项NOT_RUN；可信输入子项BLOCKED|
|2 三条真实AI链与人工出口|FAIL D03新增链缺位；真实输出/失败人工继续NOT_RUN|
|3 提醒恢复/去重/旧作业/跳回|FAIL D02源码恢复；原生NOT_RUN；同盘重启/动态撤权子项BLOCKED；不称后台常驻|
|4 三视口/150%/键盘|NOT_RUN；PNG是宿主全屏图，没有应用客户区，不能放行；不新增未经运行证明的视觉P1|
|5 跨模块输入/滚动/错误恢复及台账|FAIL D02/D04源码恢复；完整交互NOT_RUN；原P0/38业务/12UI定义与历史保留|

|用例|本轮状态与精确范围|
|---|---|
|G0-F|NOT_RUN后台/官方提醒；同盘恢复步骤BLOCKED；前台恢复源码FAIL D02，不能称后台常驻|
|T17|NOT_RUN实际断线/全量回读；断线/重连注入步骤BLOCKED；未变seed不是第二次写被阻证据|
|T18|NOT_RUN可信列表/搜索/事件/附件权限；源码task/actor/project过滤子项保留|
|T23|FAIL D02源码保护；实际提醒/通知恰一份NOT_RUN，同盘进程重启子项BLOCKED|
|T25|NOT_RUN真实模型缺/矛盾/恶意原文；D03仍OPEN，不能断言模型无虚构|
|T26|NOT_RUN真实模型失败与人工继续；静态未知不替代实际错误出口|
|T28|离线安装与宿主隔离PASS；本轮launch尝试FAIL R01；同task原生操作/回读NOT_RUN，同盘重开子项BLOCKED|
|T29|NOT_RUN grant关闭/退出/到期/共享卡与跳回；受控动态授权变更步骤BLOCKED|
|T30|FAIL D04源码核验/恢复；可信收藏隔离/重登/version完整运行NOT_RUN；可信type子项BLOCKED|
|T33|NOT_RUN真实新描述泛化；没有以元数据/夹具替模型证据|
|T34|NOT_RUN真实无历史/歧义/不存在引用拒绝；静态未知子项保留，D03缺链|
|T35|NOT_RUN真实迟到回包/改约改派后的失效；受控交错步骤BLOCKED；当前UI兜底源码缺口保留D03|
|T36|NOT_RUN真实配置/工具白名单；manifest或源码守卫不代实际工具结果|
|T38|当前source/host/data/request版本定位PASS子项；模型/提示版本及真实成功失败复跑NOT_RUN，D03缺链|
|U01|NOT_RUN三角色当前任务/下一步；目标角色fixture不等于已登录角色|
|U02|NOT_RUN真实描述/草稿修改/失败人工继续|
|U03|NOT_RUN三可信主体同task事实/动作/自验；type输入子项BLOCKED|
|U04|NOT_RUN原生预约/改约/冲突/过期；D01源码formatter闭合子项保持|
|U05|NOT_RUN原生设备位置/服务空间/依据可读；D03事实建议缺链|
|U06|NOT_RUN原生进度/完工/独立验收/退回历史；前序挂账不代修|
|U07|FAIL D02/D04源码异常恢复；实际点击只调度到宿主、无业务重复点击；受控故障子项BLOCKED|
|U08|NOT_RUN应用空/错误/权限/附件/过期出口；App unavailable为宿主入口错误，不是应用恢复出口|
|U09|NOT_RUN应用布局/长中文/150%；8张2800×1718不等于三个应用视口已测|
|U10|NOT_RUN键盘/焦点/对比/颜色冗余，未凭源码或HTML放行|
|U11|宿主截图/回收PASS；应用滚动/输入/面板NOT_RUN；D04错误恢复源码FAIL|
|U12|NOT_RUN同版本2–3分钟演示与独立人员复述|

## 判定

- **最终结论：FAIL**，依据原D02/D03/D04未闭合核心源码缺口，不因建议、M5前置或审查R01单独惩罚产品，不以“基本通过”放行。
- 精确范围：证据完整性、内核隔离/回收、离线安装层PASS；本轮请求launch失败；产品原生业务/视觉/模型NOT_RUN，不能签完整独立验收。原生未执行与源码确定缺口分开。
- 必修清单仅 **D-M6-02 恢复保护与结果传播、D-M6-03 两既定真实AI链、D-M6-04 偏好读回/异常收尾**。D01/D05源码已闭合子项保持，原生仍待测。
- 审查重跑准备：先纠正R01路径，然后由驱动复跑当前冻结/新交接包；取得可信输入、同盘重启/故障/撤权步骤证据。不改业务迁就seed，不直接启动宿主，不公开发布。所有步骤仍用隔离测试数据。
- 受影响前序：只核当前累计源及M5状态/同摘要输入关系，没有将M5历史parser结果代成本轮实跑；前序结论不更新。
- 写入位置：本报告和GATES的M6 status/审查字段/历史；原ACCEPTANCE.json、业务源码、原业务数据和其他模块均不变。H原证据未改。
- **不允许下一模块，不给M7入口，不执行下一模块。** 留在M6按原编号修复/复审。身份/provider/离线签名已授权、模型请求0无计费错误，本轮NEEDS_ABRAM=no。
