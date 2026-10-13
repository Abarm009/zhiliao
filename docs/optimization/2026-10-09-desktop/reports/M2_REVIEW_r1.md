# M2 独立 Review r1

最终结论：**FAIL**。候选 `M2-r1-worktree` 的可信执行主体、稳定重放、可靠提交/回执、竞争和历史恢复存在核心 P1。当前源码的本地 catalog / install_staged 路线可行；真实桌面运行在本轮环境 **BLOCKED**。没有修业务代码，没有执行 M3。

- 审查者 / 日期：Codex 唯一审查方；2026-10-10，Asia/Shanghai。无子代理、无 Kimi。置信度：源码确定分支与隔离复现 **高**；契约对真实宿主行为的等价程度 **中**；原生 UI / 登录会话运行 **未知**。
- candidate_id / base：`M2-r1-worktree` / `M1-r2-worktree`；HEAD `8d730569546cb57310944bb299695134df773b9d`。以报告及 GATES 的交接 ID 定位，未按修改时间选择。
- 主源：`app/bundle/main.splash`，100587 B，SHA-256 `2bef267a3bc3e1111eace38b039323ad9ee948b510ab53f3617ce55f4b1612f0`；新增 `identities.json`，1597 B，SHA-256 `ed00dcbcd7c8849838f7bc4b6de86b48669ca841af75c787f4b10ac171fc69b2`。
- 基线副本 SHA-256 `7dd8d89c4f37774c5d59535049f208251cddf0a51bff6ab656cb637bdfafb00d` 与作者 M1-r2 before 一致。已保存逐行增量 `results/base-to-candidate.diff`。审查输入开始/结束字节一致；见 start/end-snapshot 与最终 verification。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r1.md`。候选清单是该报告 §10 内嵌 JSON，没有独立 CANDIDATE.json；可用源码哈希与基线副本定位。作者五份证据共22个条目，未覆盖写它们。
- 前置核对：M1 独立结论实际为 **FAIL**，不存在已接受的 M1-r2 PASS。依 Abram 本次“前序挂账”裁决继续审 M2；不因 M1 的状态单独判本轮失败，不将该基线改写为已接受。M0/M1 字段及历史不改。
- 实际环境：macOS 项目隔离目录；主会话未能独立确认 Router / `gpt-6.1-sol` 路由，也没有切换或代称已切换。会话 createdAt / 标题设置工具在本轮不可用，未猜日期或修改会话其他状态。
- 宿主：官方 `desktop-v0.1.0-rc.1` 所交接路径；现场 SHA-256：octosense `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，octos-kernel `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。工具二进制哈希见 `results/environment.json`。
- 已阅读：AGENTS.md、CONTEXT_M2.md、00/01/02、M2、04模板、M2实施报告/清单/证据/脚本、M1 r2 Review及相关隔离证据、对应既有业务/UI/独立核验条款。依已有 CONTEXT 的效率要求，未重新通读全部历史文档。
- 已运行：现场快照与增量核对、隔离机制预检、独立契约失败/重放/重启/竞争、提交源码 finalizer 分支探针、当前源码本地签名安装正/负/恢复验证。测试只创建本轮 runtime 副本及合成数据。
- 未运行：真实 launcher/UI、原生失败点注入、真实授权主体和 grant 生命周期、完整业务/UI用例。预检 rc71；进程清点 rc3 UNKNOWN，禁止启动无法保证隔离/回收的宿主。未调用 launcher --help，未创建本轮窗口；不能声称已核验桌面上历史窗口是否消失。

证据根：`runtime/optimization/2026-10-09/M2/review-r1/`；下文 `results/…` 均相对此目录。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、宿主、增量|核对两源文件、基线副本、HEAD和二进制哈希；保存差异|与交接内容一致|两源哈希、基线哈希及宿主哈希一致；输入冻结|PASS，定位范围|environment/start/end-snapshot、base-to-candidate.diff|
|真实按钮到事实源|追踪 main_action_btn→runAction→acceptTask→runCommandBound→runCommand→recordReceipt→commit→commitBound→logEvent→STATE.status|主体/键/提交结果贯穿，失败不继续成功支路|点击生成新键；commit丢失返回值；调用方随后写成功事件/状态|FAIL，源码；原生BLOCKED|source-traces；main.splash:2074、1377、861、466、823、725、772、575|
|硬1：正常重试、跨状态重放、同键冲突、独立新动作|独立契约先接单提交；以原键原版本重试，再原键新版本重试；recordProgress同/异参数对照|均可查询原已完成动作，同键异参拒绝|接单提交final后：原版本version_mismatch，新版本source_state_invalid；同状态同参数hit，异参数idem_conflict|FAIL；部分子项成立不放行|independent-contract-probes：retry_original_version、retry_current_version、same_payload_newer_version、changed_payload|
|硬2：权限、撤权、版本、真正竞争|检查主体/角色读取路径；修改隔离注册表撤权；两个进程同目录，barrier保证都先读version0，再完成各提交|客户端不能切主体；撤权生效；仅一个成功|缓存身份仍放行；两个独立进程均gate ok、commit final；最终version1/承接者tech2，tech1成功回执被覆盖|FAIL，契约运行及源码；真实主体NOT_RUN|independent-contract-probes：cached_revocation、race；source-traces|
|硬3：写入中断、任务/回执/事件一致及UI|契约注入tasks写失败；任务成功而final前中断，重开检查盘；追踪生产调用方|无假成功、可恢复一致结果|写失败盘任务仍OPEN、回执needs_verify；任务成功后pending重开仅superseded，不能查询成功；生产调用方不处理提交失败|FAIL；完整原生逐写点/UI BLOCKED|write_failure_disk、crash_disk；source-traces commit/commitBound|
|硬4：读回失败及较新任务的原动作查询|注入契约独立读回None；新实例对账并原键查询；读取回执结果|待核验后查原action_id/result，不重复写；新版本不误拒旧成功|任务已ACCEPTED/version1、回执needs_verify；重开reconcile0，原版本重试version_mismatch；正常final结果仍写OPEN|FAIL|readback_failure_disk、readback_failure_restart_retry、initial_receipt_result|
|回执精确归属|抽取提交的_setReceiptStatusFinal，最小语法翻译执行；旧A、新B同command，不同task/actor；当前rid=B|只更新B，A保持不可变|A被写入B结果，B仍pending；探针落盘已独立读回|FAIL，源码函数探针，不是原生执行|receipt-source-probe.json、finalizer-translated.py|
|硬5：迁移、重启、重复点击、身份/输入|检查迁移helper和load/后续save路径；核对UI键保存|旧回执可恢复使用；未知结果跨重启可查|字符串长度helper固定0；迁移没有接入boot；旧日志返回nil后后续save覆盖活跃日志；稳定键不在STATE|FAIL，源码迁移；原生点击/输入BLOCKED|source-traces；main.splash:221、290、375、431、851|
|旧入口|检查addEvidence/quarantineEvidence/togglePin及commit公开路径|每个实际业务写都校验身份、版本、幂等|三入口直接mutate+commit，commit自身不校验上述条件、可无回执写成功|FAIL，当前脚本写入口；外部旧Web/MCP/runner NOT_RUN|main.splash:1117、1145、1293、772；source-traces|
|当前本地catalog/install_staged|仅在副本keygen/certify/stamp/sign-manifest；直接离线构造签名catalog，官方verify/install；重开may_run；篡改并恢复|当前内容准入、拒篡改、可重装|verify及安装重开rc0；篡改rc1；恢复rc0；两源安装字节匹配|PASS，Store层；不是launcher/UI|local-store-validation.json、local_store.py|
|隔离/清理|限制写入到本轮runtime并禁网络；true预检、pgrep清点|隔离可执行，退出可核验|sandbox_apply Operation not permitted rc71；pgrep rc3；host_started=false|BLOCKED，未冒险启动|preflight.json|
|离线密钥|finally删除本轮两私钥并读回key目录|不保留私钥|working.key / anchor.key已删除，remaining_key_files=[]|PASS，本轮生成范围|local-store-validation.json|

### 既有用例逐项状态（当前原生交付形态）

|用例|本轮结论|精确范围/未测项|
|---|---|---|
|G0-B|FAIL + 真实身份链BLOCKED|D-M2-01；注册表不是登录认证。延期在M2到期，作者无权自定“止于适配器”再次延期。真实业务身份来源需Abram裁决。|
|G0-C|FAIL|D-M2-03/04/05；部分写入/竞争契约反例；完整原生事务恢复BLOCKED。|
|T02|FAIL（源码）；原生BLOCKED|createDraft每次新task/key，不能带原创建key重发；D-M2-02/03。|
|T04|FAIL（独立竞争契约）；原生BLOCKED|同事实源两个独立进程双成功；D-M2-05。不能用源码/harness结果声称已执行原生T04。|
|T15|部分版本拒绝成立；完整NOT_RUN|独立旧版本拒绝成立；真实UI刷新、输入保留及阶段百分比完整流程未跑。|
|T16|FAIL|成功后同key重试被版本/状态拦截；D-M2-02。|
|T17|NOT_RUN|原生断线/全量回读完整流程未运行；未启动SSE或以旧后端结果替代。|
|T18|NOT_RUN；主体边界源码FAIL|真实列表/搜索/事件/附件权限探测未跑；D-M2-01。|
|T22|FAIL|提交/回执/事件恢复不闭合；契约写失败/中断已注入，完整原生逐写点仍BLOCKED。|
|T24|FAIL（当前脚本绕过）；其他入口NOT_RUN|D-M2-06；没有在本轮运行旧Web/MCP/runner，也未据未修改后端推断它们在bundle内激活。|
|T29|NOT_RUN|原生grant关闭/退出/到期、共享卡授权未跑；到期字段不等于完整grant生命周期。|
|T32|NOT_RUN|配对码、poll_secret、审批绑定及token隔离未跑；此交付无配对流程运行证据。|
|T37|FAIL|提交读回失败无法恢复查原动作；结果取提交前状态；D-M2-02/03/04。|
|U03|BLOCKED|三可信主体同任务事实一致/禁止自验的真实桌面流程不可运行；切演示角色不能算主体证据。|
|U07|FAIL（提交源码）；原生BLOCKED|提交失败状态被业务成功覆盖、键不稳定；实际重复点击/超时输入保留未跑。|
|U08|NOT_RUN|完整错误出口/长文/过期建议/附件失败UI未跑；没有用作者旧截图代替。|
|T28|BLOCKED|当前Store安装层PASS，当前launcher打开→操作→权威回读→重开未跑。|

G0-E：**延期缺口（Abram 已裁决，M3 到期）**。未配置/更换真实provider，不作为本轮FAIL/BLOCKED或NEEDS_ABRAM依据。

## 缺陷

以下七项均为 **P1 / 必修**，直接破坏本模块核心目标；没有因美化或扩功能列P1。文件行号适用于本轮冻结源码。

### D-M2-01：演示选择成为执行主体，身份注册表没有成为授权事实

- **文件/行**：`app/bundle/main.splash:95`、`:336`、`:358`、`:466`、`:656`、`:682`、`:1963`；`identities.json:5`。
- **触发**：报修人窗口点击“技工甲/经理丙”，随后调用该角色动作；保持窗口不重启，在隔离注册表撤销身份或项目角色再执行。真实UI触发本轮BLOCKED；调用链已静态定位。契约缓存撤权探针已运行。
- **实际/预期**：setActorM2直接写STATE.actor；命令以该字段为主体。getMe从固定USERS取角色/技能，注册表仅缓存检查id/撤权/到期，未按注册表核验项目成员资格；身份只启动加载。契约盘上撤权后cached gate仍ok。预期视角仅影响展示，写主体来自已核验的不可由视图切换的上下文；成员/撤权每次写有效。
- **根因/影响**：把“名单中存在”当成“操作者证明”，客户端可选择他人权限；独立验收主体没有可信来源。缓存撤权契约探针使用的是reporter，单独只证明缓存失效；它不是生产acceptTask完整权限测试。
- **证据**：source-traces.setActorM2、independent-contract-probes.disk_revoked_identity_cached_gate、cached_revocation_disk。真实身份链NOT_RUN，不能声称两个登录主体已验证。
- **具体改法**：分离展示actor和可信执行subject；角色/技能/成员资格统一读取权威授权投影，更新/revoke后写边界必须重新核验。没有可信subject时禁业务写，不能fallback USERS放行。Abram需明确允许的业务身份来源/建立主体的方式；不得自行部署认证服务或把演示id包装为登录。
- **验证**：真实A/B独立会话；A切视角后仍只能以A写；B撤权/去成员/到期后同窗口下一命令拒绝且事实不变；承接者不能借切换自验。仅更改demo标签不算闭合。

### D-M2-02：幂等查询太晚，UI每次重生键，缺少原动作恢复查询

- **文件/行**：`main.splash:479`、`:487`、`:711`、`:823`、`:851`、`:868`；createDraft `:788`、`:801`；其余业务入口同形。
- **触发**：OPEN/version0用key K接单成功；响应丢失后K+原参数重试，分别携带version0和当前version1；当前任务进一步升级后查询K。重复调用recordProgress/createDraft。
- **实际/预期**：独立契约首次final；原版本重试version_mismatch，当前版本source_state_invalid，尚未进入receipt lookup。源状态不变的recordProgress才hit/异参conflict。按钮每次newId覆盖LAST_KEY，键没有跨重启保存，createDraft不能复用创建键。预期授权完成后先按稳定键查历史final，返回相同action_id/原结果，再展示最新任务；新执行才做版本/源状态检查。
- **根因/影响**：把已成功重放当新写；键属于调用而非用户确认意图，响应丢失和跨状态重放无法对账，重复处置可重复追加。
- **证据**：independent-contract-probes的retry_original_version/retry_current_version/same_payload_newer_version/changed_payload；source-traces。
- **具体改法**：建立持久化不可变意图（task_id、规范化params、expected_version、action_key）；未知/重试不换key。先做当前授权及历史action查询：final返回原完整结果，pending/needs_verify走对账，异参冲突，miss才执行当前守卫。为创建和历史action提供同一恢复查询，不以当前task.version相等作为旧成功条件。
- **验证**：原键原版本、原键新版本、后续合法动作后的原键查询均返回同action_id及原结果，版本/事件不增；异参拒绝；独立新意图允许新键；关窗重开、超时重试仍沿用K。测试必须经真实按钮和权威落盘。

### D-M2-03：提交失败未传播，任务/事件/回执中断不能一致恢复

- **文件/行**：`main.splash:575`、`:597`、`:618`、`:772`、`:815`、`:855`、`:875`、`:209`–`:217`。
- **触发**：在tmp/任务主文件/清tmp/终结回执/事件写入处分别抛错；写任务成功后让读回失败；任务写成功而回执final前中断重开；创建草稿。
- **实际/预期**：commit忽略commitBound返回值，业务入口继续logEvent和成功STATE.status（例如acceptTask:875）；内存任务已修改且不回滚。任务、回执、事件独立整文件写；没有一致恢复协议。契约tasks失败盘仍OPEN，receipt needs_verify；任务已成功但读回None，重开不处理needs_verify（reconcile0），原动作查询失败；final前中断只改superseded。createDraft先saveTasks、仍version0即调用commitBound(t,0)，必然触发internal drift，落盘草稿却始终待核验。预期失败不能成功展示/事件，未知结果可证实原动作，任务/预约/事件/回执按一个提交协议恢复。
- **根因/影响**：持久化协议只顺序写文件，提交结果被薄壳吞掉；启动仅改receipt标签，不补全/回滚事实。可能“盘未接单而UI已接单”或“任务已写但永久查不清”；完整原生发生情况本轮未运行，源码控制流确定。
- **证据**：independent-contract-probes.write_failure/readback_failure/crash各项及盘读回；source-traces.commit/commitBound/createDraft；原生其余写点BLOCKED，未声称全点已测。
- **具体改法**：命令返回明确committed/needs_verify/rejected，调用方依返回更新UI，失败后禁止继续成功事件/状态；不让未提交内存污染下一命令。采用宿主实际可验证的一致提交/恢复协议（权威日志或可用事务），事件和回执必须和动作绑定；未知时只查询恢复。覆盖needs_verify及pending；判断实际action标识/提交证据，不能只比较版本大小。创建也进入同一提交流程，修正版本语义。不得仅把fs.write改名atomic或假设不存在的rename API。
- **验证**：每个真实写点中断，重开检查tasks/appointments/actions/events原始字节及UI；未提交不出现成功事件，已提交可查原动作，较新任务保留旧动作；写/读回/清tmp/receipt失败均有出口。createDraft正常路径获得核验成功并重开可读。

### D-M2-04：回执终结可能覆盖另一任务旧回执，缺少pending与原结果

- **文件/行**：`main.splash:543`–`:570`，尤其`:558`；`:725`–`:730`；`:494`、`:716`、`:623`。
- **触发**：旧A、新B回执同command，不同task/actor，当前_pending_receipt_id=B；终结B。普通动作recordReceipt后、提交前中断；成功后读取原结果。
- **实际/预期**：精确rid尚未扫描到B，循环已在旧A的command fallback处break；源码函数最小语法翻译探针落盘显示A收到task-B结果，B仍pending。生产recordReceipt根本不写status/expected_version，boot只查status==pending因而不能识别普通未完成回执。结果在mutation前取t.status；契约接单final.result.status仍OPEN。receiptFor也不区分pending/rejected/final。预期以唯一rid更新当前动作，历史回执不可变；pending字段完整，final结果反映真正提交结果，未知/拒绝不冒充成功hit。
- **根因/影响**：“按rid优先”实际是每次循环混合fallback；恢复元数据与提交前后语义缺失，直接破坏原动作对账和独立核验。
- **证据**：receipt-source-probe.json（保存原提交函数及输入/落盘输出）、finalizer-translated.py；independent-contract-probes.initial_receipt_result；source-traces.recordReceipt。翻译探针验证控制流，不冒称Splash运行。
- **具体改法**：第一遍只精确rid，未找到明确报待核验；取消跨task/actor/cmd宽泛终结，禁止改历史final。pending保存actor/key/fp/task/expected_version及确认参数；final保存before/after版本、action_id、实际已提交结果及可验证关联。receiptFor按状态分支，拒绝/未知不作为成功hit。
- **验证**：同cmd跨两个任务及主体连续执行，逐份旧回执字节不变、新回执唯一final；普通命令在recordReceipt后杀进程能识别pending；接单final.result为ACCEPTED及正确assignee/version；拒绝和未知键重放分别明确拒绝/对账。

### D-M2-05：读版本和写入无排他保证，真实竞争双成功

- **文件/行**：`main.splash:480`、`:575`–`:608`；作者测试 `m2_concurrency_test.py:57`–`:102`、`:141`–`:156`；契约 `m2_contract.py` 的run_command_bound/commit_bound。
- **触发**：两个独立进程指向一个隔离store，不同主体/键；barrier强制两者先读version0，再分别提交。提交阶段按A→B排序用于确定地暴露读取与提交之间的竞争窗口，生产边界没有测试锁。
- **实际/预期**：两gate都ok，两commit都final，进程exit0；最终任务只有version1，assignee=tech2；tech1成功信息被整文件覆盖。预期独立竞争只有一个成功、一个权威承接者、一条成功接单事件，另一方冲突且不能覆盖。
- **根因/影响**：只在写前读一次版本，无跨上下文的锁/CAS/单权威串行队列；整TASKS/RECEIPTS数组覆盖。作者第一例先复制赢家结果再执行输家，是顺序冲突；第二例测试自带threading.Lock串行化，不能证明生产竞争安全。
- **证据**：independent-contract-probes.race保存两进程结果及盘；audit.py/race_worker可复现；source-traces。此为交接契约反例，原生双实例竞争仍BLOCKED。
- **具体改法**：在唯一事实源内使“读版本→授权/状态→占用→任务/事件/回执提交”处于同一可验证竞争边界；共享锁/CAS或真正权威单写者须可跨实例，不能在测试外包锁模拟通过。动作和回执不能覆盖其他主体已提交事实。
- **验证**：真实两个独立上下文共用同一权威存储，两者读取旧版本后同步放行，多次竞争均仅一成功；核对任务、唯一成功回执/事件和失败方结果；注入赢家中断并重启，不留下双成功或锁永久阻塞。

### D-M2-06：仍有业务入口绕过命令边界

- **文件/行**：`main.splash:1117`（addEvidence）、`:1145`（quarantineEvidence）、`:1293`（togglePin）、`:772`（commit）、`:2122`（收藏按钮）。
- **触发**：直接调上述仍可调用的函数；失效主体/旧版本时执行，或没有_pending context时commit任务。
- **实际/预期**：入口只做各自部分角色判断后直接mutate+commit，没有runCommandBound、稳定key或当前授权检查；togglePin连活跃身份都不查。commit可把任务写盘且_setReceiptStatusFinal未匹配仍被commitBound视为成功。预期所有当前交付实际写入口走一个完整边界；旧无法迁移入口禁写。
- **根因/影响**：认为“commit转到commitBound”即可覆盖身份/幂等，但commitBound负责持久化，不负责这些守卫；撤权和旧版本可从遗留入口绕过。附件真实picker不是本轮修复范围，附件索引写边界是本轮责任。
- **证据**：source-traces上述四函数，真实按钮定位；作者audit把调用commit视为边界覆盖，不能证明授权成立。未运行外部Web/MCP/runner，不捏造其当前可利用性。
- **具体改法**：为三入口添加规范化命令/意图，身份、成员、源状态、版本、幂等均在唯一入口；commit仅能由已验证的当前命令上下文调用，无上下文拒绝写。清点该交付形态旧写入口，迁移或明确禁用。保留旧契约兼容，别全仓重写。
- **验证**：独立直调每个入口，撤权/旧版本/同键冲突均拒绝且盘不变；正常写唯一回执、事件、版本。测试旧可调用runner/Web/MCP时必须证明当前交付实际启用范围。

### D-M2-07：迁移函数为空实现，旧历史回执无法进入活跃对账

- **文件/行**：`main.splash:221`–`:258`、`:290`–`:327`、`:375`、`:413`–`:442`、`:211`–`:217`。
- **触发**：副本以合法多行旧JSONL动作/事件启动，再做一次会保存日志的正常动作；查旧动作。混入破损行测试恢复。
- **实际/预期**：loadJsonlLines备份后返回nil，内存历史为空；migrateJsonlLegacy没有启动调用，_textLenSafe无条件返回0/_charAtSafe返回空，无法迁移任何多行文本。下一saveReceipts/saveEvents覆盖活跃文件，只剩本次条目；备份仍在但无恢复查询通路。预期旧事件/回执保留可查询，未迁移时显式阻止覆盖，不能缺失历史仍成功运行。
- **根因/影响**：存在函数名称和backup被误当迁移实现；丢失活跃幂等历史，原成功无法查、旧key可能重复写。源码行为确定；真实宿主迁移本轮BLOCKED。Python脚本真实splitlines迁移与此源码不同，作者migration PASS不能转签。
- **证据**：source-traces.migrateJsonlLegacy/_textLenSafe及load路径；begin/end快照保留作者证据。
- **具体改法**：用已验证宿主原语实现可用迁移并在boot接入；先完整验证、可靠备份、读回新形态再切换。未完成或破损数据进入明确恢复模式，禁写原历史文件，提供从备份恢复的受控通路；不要静默跳过坏行或把空历史当成功。
- **验证**：在副本跑合法旧JSON/NDJSON、空数组、坏行、备份失败/写失败/中断重开；旧动作/事件仍能查询，恢复后字节/条数可追踪，新动作追加不抹旧条目。旧成功key重试不会第二次业务写。

### 建议挂账（不单独导致FAIL）

- **A-M2-01 / P2**：从当前产物生成交接清单，删除“源码与Python等价”“全部命令已覆盖”“不变更bundle digest”等超出证据的断言。改变main.splash/添加identities必改变内容digest；本轮当前隔离包digest为 `7673558730e5ce4c719a156b27bccb508ec623cab3ea518d55d49e4253a4b3bd`，与前序签名包不同。这是签名副本的digest，原manifest未重写；生产认证不因离线签名成立。
- **A-M2-02 / P2**：完整视口、中文输入、长文、键盘等仍按已有模块挂账，不新增皮肤/搜索范围，不为这些建议判FAIL。

## 判定

- 最终结论：**FAIL**，精确指 `M2-r1-worktree` 的上述核心源代码/提交契约失败；真实桌面检查另列BLOCKED。并非以M0/M1挂账、美化建议、真实provider延期判FAIL。
- 必修：D-M2-01至D-M2-07。复审只逐条核对这些编号及受影响回归，优先闭合正常创建/提交、未知结果对账、同键重放、单赢家竞争和可信主体，不扩后续模块。
- 解阻：提供可限制项目外写入、并能检查本次PID/子进程/窗口退出的运行通道后，后台启动既定launcher；禁止 --help；测试结束立即回收。本地catalog路线已可行，不需要公开发布授权，也不应转走AppHub。
- 需要Abram：**仅业务身份来源**。G0-B在本模块到期，真实登录/主体来源尚无已批准接入证明；需要明确用于独立A/B主体的可信身份来源/建立方式。现有隔离测试授权足够解决其余工程/环境项；离线签名无需新授权；G0-E不计本轮授权缺口。实现方可继续处理无需新增授权的各缺陷，不能以此停掉其他修复。
- 私钥删除证据：`local-store-validation.json` 的keys_deleted列出本轮两私钥，remaining_key_files为空；仅当前隔离包签名，无联网、上传、publish、公开listing、push、issue、消息、部署或真实provider修改。
- 受影响前序回归：当前源码在既有M0官方Store路径的安装/重开准入/篡改拒绝/恢复已复验PASS；M1 UI任务选择与清理代码未修改，原生交互受环境阻断；不重判前序模块。
- 更新：本报告及GATES.json的M2审查字段/状态/历史。原ACCEPTANCE.json保持此前来源，不用Store/契约部分结果覆盖历史后端或原生完整验收。
- 下一模块：**不允许；未执行**。留在M2修复以上编号，提交新candidate_id、对应差异、真实核心操作和失败恢复证据后复审。

STATUS=FAIL
NEEDS_ABRAM=yes
