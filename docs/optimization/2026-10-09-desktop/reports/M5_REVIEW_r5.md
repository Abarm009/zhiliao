# M5 独立 Review r5

**结论：FAIL。D-M5-04、D-M5-05 两个核心P1未闭合；本轮原生隔离/回收PASS，业务程序未加载，业务验收NOT_RUN。**

本轮实际原生失败是审查方seed遗漏已接受catalog，不是M5业务代码运行后拒绝了坏附件，也不是本轮重现了程序解析失败。该审查准备错误如实单列，不转嫁为构建方业务缺陷。源码缺陷与未运行项各自记录，不能以CLEAN或本地安装成功放行。

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-11（Asia/Shanghai）；未委派子代理。
- 审查对象：`M5-harness-r1-1309-current`。这是用户“首轮跳过构建、用当前代码harness重审”的冻结快照标识，不是构建方新增了r5实现报告。旧作者交接为 `M5-r4-worktree / M5-r3-worktree`，实施报告 `reports/M5_IMPLEMENTATION_r4.md`、清单 `runtime/optimization/2026-10-09/M5/r4/CANDIDATE.json`；旧源与现工作树不同，未按mtime选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d` 加既有未提交差异。现main SHA-256=`dcf73555767c895ac04a8a5904246f9635b21481ac9f4e07b14cc13709e3d006`，388582字节、8330逻辑行；两段审查间及门禁写入前一致。
- 旧r4源SHA=`e7e0e713eb68303a0fc23a9d2e2fe5ef253817f5a6b65c9af11d5e0b94ac91a2`。完整累积差异已保存；56个相关函数中47个同内容，9个变更主要为 `ok→success` 及提示串。未把前序累积修改全部说成本轮M5修复。
- 前置：`M4-r5-worktree / M4_REVIEW_r6.md / FAIL`，没有已接受PASS前置。按用户前序挂账裁决继续复核M5，不代修M4、不冒称前置已满足。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。仅外部驱动通过harness启动；审查方未运行launcher、局部VM、sandbox-exec、pgrep、osascript或辅助功能。
- 原生实际窗口：2026-10-11 15:31:08–15:32:02 +08:00，4场均CLEAN、quit_http、rc0。主程序未加载；没有可信业务会话、实际完工/验收命令或成功回执。
- 置信度：候选摘要、源码缺陷、四场证据一致性/隔离、catalog缺失/启动错误 **高**；本轮实际附件命令、可信身份、正常/退回/重启链 **未知**。前序报告关联的具体解析token根因不作本轮结论。
- 阅读范围：第1段AGENTS、CONTEXT、00/01/02/M5/04、r4缺陷/实施/候选/证据、M4 r6、harness及相关T/U定义；第2段只核这些缺陷与其受影响运行，不作无关扩审。
- 路由/标题：工具未提供主会话Router/具体型号核验和当前会话createdAt/标题读写接口，未声称切换或命名。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M5/native-runs/review_r1_1309_REQUEST_review_r1_1309/`，驱动证据，未改。
- **S**：`runtime/optimization/2026-10-09/M5/native/review_r1_1309/`，源码快照、差异、函数、独立字节分析、离线安装、seed及审计结果。
- **R**：`runtime/optimization/2026-10-09/M5/native/REQUEST_review_r1_1309.json`。
- **N**：`runtime/optimization/2026-10-09/M5/native/REVIEW_NOTES_r1_1309.md`。
- **A**：S/`native-evidence-audit.json`，可用S/`audit_phase2.py`重复核对；A的一致性PASS不是业务PASS。

## 独立运行证据核对

|场景|隔离回收|安装副本/入口|PNG与实际业务|
|---|---|---|---|
|cold_new_intake|PASS指定全部判据|main安装副本匹配；apps/catalog.json缺失；无.running副本|宿主桌面+“Could not open app / no catalog has been accepted”；业务NOT_RUN|
|corrupt_submit_candidate|同上PASS|同上；两件固定负例未被应用读取|同上；提交反例NOT_RUN|
|corrupt_fixed_acceptance|同上PASS|同上；坏件/固定completion仅seed|同上；验收反例NOT_RUN|
|missing_foreign_fixed_set|同上PASS|同上；缺失/跨任务仅seed|同上；守卫NOT_RUN|

1. H/MANIFEST.sha256 **592项**，摘要错误0、缺失0、未列入文件0、重复0。summary.request与R逐字段相同；harness/template摘要匹配。逐场result/summary摘要、命令、环境、seed清单、captures、profile、denial汇总、host_log_markers/bytes/tail均重新计算核对；A.errors为空。
2. 四场 `profile_probes.ok=true`；apply rc0，外写探针失败且未创建，秘密/明文凭据/用户配置/SSH禁读探针均成功拒绝；pre/post_pgrep均NONE，pgid_members_after=[]，verdict=CLEAN。profile与模板及场景参数逐字节匹配，HOME/app-data/cache/tmp等指向各场新目录。原HOME `.octosense` mtime前后一致，library_scan空，无进程组残留。**旧agent沙箱rc71/rc3理由关闭。**
3. 逐张查看了4张实际PNG，摘要均匹配，尺寸均为2800×1718。都显示原生宿主桌面和上述toast，没有M5窗口/登录/任务/附件/验收表单。请求1280×800/980×760不是实际业务布局已验证的证据。
4. 每场files_written_count=109，列表均109项、无重复、路径在场景目录且存在。主要是宿主系统应用/缓存、profile/log/PNG。业务目录与seed逐字节相同：冷场5个文件，损坏提交9个、损坏验收9个、缺失/异任务8个；包括tasks/state/actions/events/测试账号表/证据索引和存盘字节。**不变不是坏件被命令拒绝，只是业务没运行。**
5. 四场日志都有 `--test-action launch hub:octosense-repair`（cold的host.log:32）及两个tap调度；SPLASH eval仅 **809 bytes**，无 `wm: launched`、无main的388582字节eval、无业务 `.running/main.splash` 副本。本轮无主程序parser错误，不能因此声称当前主程序已解析成功，也不能沿M4 r6错误冒充本轮复现。
6. 各场安装位置的main字节与S/当前main一致；hub-mirror含已签名catalog及声明digest。但宿主读取的 `home/.octosense/apps/catalog.json` 在四个seed及运行目录均不存在，launch toast明确表示没有接受catalog。**候选在磁盘一致，候选加载不成立**；digest_seen_in_seed=true而digest_seen_in_host_log=false，不混用这两项。
7. denial完整日志已读，汇总重新核对一致：remote:443、Metal系统缓存、/dev/dtracehelper等是被拒绝尝试，不是成功外联/外写。仅授权本机控制口；四场needs_model=false，model_proxy_stats/model_proxy均不存在，和请求一致；真实模型调用0，无402/欠费证据。
8. 第1段实际offline hub verify、官方install_staged、Store重建/may_run均rc0，证据S/offline-store-evidence。此安装probe每次在内存中accept_catalog（`M0/r10/install_probe/src/main.rs:92`），不证明catalog已持久放到launcher读取位置。签名仅沿用精确同digest隔离副本，不修改原manifest、不公开发布；没有新签名私钥，旧两把私钥已复核不存在。
9. 凭据均在本次隔离目录另造，seed只放慢哈希账号表，没有预置SESSION或可信actor；没有读生产明文凭据/provider密钥、改生产数据。账号来源/provider已裁决，不列为NEEDS_ABRAM。
10. 第1段开头误读项目外记忆注册表的读取越界已在N披露；无项目外写入，记忆未作候选/验收依据。第2段显式读写均在项目内。不称两段全程满足读取目录约束。

## 必需检查

|检查|独立步骤 / 期望|实际|结果|证据|
|---|---|---|---|---|
|候选/前置/新增差异|作者r4定位，冻结当前增量，核安装/运行|固定当前/安装相同；M4仍FAIL；没有实际当前代码加载|快照PASS；前置未满足；加载检查FAIL（审查准备）|S/start-snapshot、diff、A|
|原生隔离/回收|全部指定探针/进程/profile/写入判据|四场全部满足，无ABORT|PASS|H/results/profile/denials、A|
|独立新文件及两入口坏/缺/跨任务|新二进制保存测试副本后损坏/删除/改归属；实际再次提交及验收应拒绝|反例字节已造；算法分析相同指纹；业务未加载，没有实际两入口|D05源码FAIL；原生NOT_RUN|S/independent-byte-analysis、fixtures、H|
|本轮固定集合/旧证据|两件固定成员必须全查；退回后保留历史/新轮/显式复用|源码守卫改善保留；seed好+坏两件没有被应用执行|源码子范围保持；完整NOT_RUN|source-traces、affected-functions、A|
|可信独立主体验收|真实凭据会话、同ID多角色禁止自验、经理无/有理由拒/成功|没有登录UI或会话；标签/seed actor不代验|NOT_RUN|4张PNG、日志、A|
|正常链/退回链|真实上传→完工仅待验→独立验收；退回补充新轮再验|主程序未加载；预置负例不代成功链|NOT_RUN|H、N|
|重启/附件读取|同盘应用重开，真实字节、固定集合、事实/回执一致|Store重建成功只安装层；四场新盘，不是业务同盘重启|业务NOT_RUN；同盘自动复跑通道BLOCKED|S/offline-store-evidence、schema/harness|
|失败恢复|submit/reject writer异常及commit中断，明确结果、重启对账重试|writer吞异常/覆盖成功源码未改；本请求无受控故障动作|D04源码FAIL；受控原生故障通道BLOCKED|source-traces、schema、N|
|实际内容打开/失败/重试/终态只读|应用控件及实际字节/权限/回执|没有业务窗口，未执行查看/重试/终态动作|NOT_RUN|4张PNG、A|

BLOCKED仅用于当前白名单schema/harness确实不提供的运行中保存副本变更、writer故障/中断和共享盘重启/受控模型交错子项；没有ABORT。不用“环境限制”遮盖seed准备错误，也不把普通登录/输入白名单可执行项未经尝试便判BLOCKED。

## 上轮缺陷闭合表

|编号|本轮状态|证据与边界|
|---|---|---|
|D-M5-01|内容出口源码子项保持；完整原生NOT_RUN|STATE.last_open_attach及UI消费者存在；当前ok→success接线改善，实际查看/下载/错误/重试未执行|
|D-M5-02|绝对根源码子项保持；目标运行访问约束NOT_RUN；harness内核隔离PASS|默认/STATE根与字面路径逻辑未修；测试根在新目录，未测试真实读取/链接/根篡改，不杜撰越界事故|
|D-M5-03|固定集合源码闭合范围保持；实际两入口NOT_RUN|固定completion ID/digest检查和全成员拒绝逻辑保持，不能按readyCount签收|
|D-M5-04|PARTIAL / **P1 OPEN**|bind不主动落索引、reject布尔失败回滚保持；writer吞异常、commit与索引分裂、重启恢复未修|
|D-M5-05|PARTIAL / **P1 OPEN**|printable v/w区分改善保持；保存只核大小、控制字节fallback内容值缺失未修；新反例分析复现|
|D-M5-06|此前构建方约束子范围闭合保持|本轮无作者外写重现；审查方读取偏差单独归责|

## 缺陷

### D-M5-05 — P1 / 必修 / OPEN：保存只核尺寸；非printable字节变化不能可靠影响内容指纹

- **文件行**：`app/bundle/main.splash:5170`（back_size）、`:5172`（大小判断）、`:5175`（READY）、`:5257`（fingerprint）、`:5285`（仅位置fallback）、`:5319`和`:5326`（两个ASCII表）。相关函数与旧r4同内容，见S/affected-functions。
- **触发**：审查方新206 B二进制证据，ASCII首尾，中段96个0x01。先写入隔离保存副本，再同位置改为0x02；长度和前后32字节不变。分别为提交候选、固定待验收记录准备好件+坏件负例。初次保存同大小不同内容也进入相同READY判定分支。
- **实际 / 预期**：原/坏SHA=`07731e728f98c853bb465d82456cda55192fed73c6904c43011bb7bcf31b8d3d` / `663aa58c5227b27cc5363b068ae25956c48c120b51b67bd5b07276db51f57438`；按当前源码的一字节slice/index_of语义计算均为 `1d2f705b`。预期保存全量一致才READY，提交/验收重查任一内容变化即拒。实际源码缺失这条可靠区分；本轮原生程序没有加载，**没有观察到真实错误终态，也没有独立跑通两个入口**。
- **根因**：两张所谓nibble表只含ASCII，所有不在printable表内且不在这两表的字节走仅依赖位置i的fallback，内容值完全不参与。它是确定性算法缺口，不是偶发摘要碰撞；保存另只比back_size。
- **影响**：核心硬1/2、T19/G0-D真实字节绑定未闭合。中文/高字节/二进制不是可降为建议的附件范围。
- **证据**：当前冻结函数、S/independent-byte-analysis.json、prepare脚本:108–110、seed/inbox和attachments及fixtures；H只证明本轮未加载，不证明错误命令放行。分析适配不是发行宿主原语验证。
- **具体改法**：仅由构建方修该编号：在指定宿主证明可用的完整二进制读写/摘要或完整内容比对；保存后全量读回一致才READY；两个入口以固定内容再核，不能用printable表冒充任意字节，也不能用Python测试指纹替换待测实现。宿主原语确实不可行时交最小harness复现，不缩验收。
- **验证方式**：修复审查seed并真实加载后，用实际上传保存的新文件，对0x01/0x02、NUL、0x80/0x81、UTF-8、PNG/PDF、>64KiB边界分别坏/缺/跨任务注入，两个入口均拒；正常文件可完工仅待验，独立验收通过。核实际全字节、状态、固定证据集合和权威回执。

### D-M5-04 — P1 / 必修 / OPEN：commit后索引写失败被吞，成功提示覆盖错误；没有共同恢复结果

- **文件行**：`main.splash:5387`（writer）、`:5391`（catch）、`:5395`/`:5402`（load读取旧索引并替换）；`:6106`/`:6115`（submit索引写与成功提示）；`:6344`/`:6349`（reject同模式）。writer/load/reject与旧r4同内容，submit只有结果字段改名。
- **触发**：submit或reject的task commit成功后，evidence_index.json写失败；或在commit与index写之间中断再重启。
- **实际 / 预期**：源码writer没有可核成功返回，catch仅修改STATE.status，随后成功路径改成“完工已提交/已退回”；load用旧盘索引替换内存。预期任务/固定集合/轮次/索引/事件回执能按同一已提交结果恢复，失败或未知不能报完整成功。**本轮未运行真实writer异常/权威commit，不重称上轮适配结果为原生实证。**
- **根因**：两个独立持久写没有本模块提交/恢复协议；把writer挪到commit之后只移动故障窗口，不构成原子提交。
- **影响**：核心硬4/5、T22/U07的失败恢复与重启一致性未闭合。布尔commit=false的既有回滚改善仍认可；不要求修完M2所有历史挂账。
- **证据**：S/source-traces的writer/load/submit/reject、r4→当前差异与函数摘要；旧M5_REVIEW_r4的反例只保留来源，不冒充本轮运行。本轮H业务NOT_RUN。
- **具体改法**：建立M5可核验提交/恢复记录，关联task版本、completion固定集合/轮次、索引快照和动作回执；索引异常传播，启动先按权威提交恢复再开放业务操作。只修本模块所需恢复，不静默引入新服务或把两个写叫原子。
- **验证方式**：通过驱动受控故障/共享隔离盘，submit/reject两链各测writer异常、commit失败、commit后中断；同盘重启比task/state/index/completion/字节/事件/回执，再重试无重复、旧证据不丢、UI无错误成功提示。

### R-M5-01 — 审查准备错误 / 必需补证据；不是构建方业务P1

- **文件行**：`M5/native/prepare_review_r1_1309.py:116`复制install-root后未放catalog；`:145`请求launch-hub。`M0/r10/install_probe/src/main.rs:92`仅给重建Store重新accept内存catalog。
- **触发 / 实际 / 预期**：四个新HOME加载launch-hub；实际apps/catalog.json不存在，PNG均“no catalog has been accepted”，日志仅809字节eval、无业务运行；预期当前bundle真正加载且可开始独立操作。
- **根因 / 影响**：审查方把官方安装probe成功当成launcher接受catalog所需seed已齐；这使原生证据不能评业务。不归咎作者，不增加业务修复范围。
- **证据**：A.accepted_catalog_in_seed=false×4、running_main_copies=[]×4；四PNG；H日志；原seed与运行目录实际清单。第1段校验检查了安装main和请求schema，却没检查该入口前置。
- **具体改法 / 验证**：下一次原生审查准备新seed时，把**已验证同digest的隔离catalog**放到宿主已验证读取位置apps/catalog.json，再核同anchor、安装bundle及expected digest；通过驱动harness重跑，必须出现实际业务main eval/加载副本和UI。不得用旧H补写文件后说原运行成功，不需要公开发布或Abram另授权。

### 保留改善及建议（不作为FAIL依据）

- D01内容出口、D03固定集合、D04布尔失败回滚、显式复用/递增轮次、D05 printable区分的既有源码改善保留。完整运行结论未签收。
- A-M5-01作者证据路径/汇总准确性仍建议挂账；author r4摘要可定位，不因清单路径缺口单独判FAIL。
- A-M5-02验收意见/经理理由读取落事件的源码改善保留；没有权威事件回读，不用作者布尔值放行。
- A-M5-03附件长内容/格式预览及显式复用UI可读性建议保持，不扩M6；真正打开/失败重试属于未执行核心检查。

## 五条硬验收及既有用例

|硬验收|本轮结果|
|---|---|
|1 真选择/保存/重启再开|D05保存仅大小，源码FAIL；真实上传/业务重启/重新打开NOT_RUN|
|2 坏/缺/隔离/异任务/无权/旧轮两个入口拒|D05内容绑定源码FAIL；负例已独立造，但实际提交/验收NOT_RUN|
|3 仅待验/可信独立人员最终验收|NOT_RUN；源码自验/角色/理由守卫保留，未建立可信会话|
|4 退回旧证据/新轮/明确引用|固定集合/显式复用源码改善保持；D04恢复源码FAIL；真实退回链NOT_RUN|
|5 桌面打开/失败重试/表单/终态只读/完整两链|本轮launch检查FAIL（审查seed）；M5业务NOT_RUN；D04恢复源码FAIL|

|用例|本轮结论与精确范围|
|---|---|
|G0-D|离线安装层PASS、内核隔离PASS；附件真实读写/打开NOT_RUN；D04/D05源码FAIL。|
|T18|真实列表/搜索/事件/附件查询权限NOT_RUN；归属源码子范围保持，不以未加载/盘不变证明拒绝。|
|T19|D05源码FAIL；无证据/异任务/隔离/缺件守卫源码保持；两入口及实际下载NOT_RUN。|
|T20|真实独立会话、同ID多角色自验拒、经理理由、完工仅待验NOT_RUN；守卫源码保持。|
|T21|实际退回IN_PROGRESS、旧字节历史、新completion_id/新轮再验NOT_RUN；D04源码FAIL。|
|T22|D04源码FAIL；真实异常/事务回执NOT_RUN；受控写点/中断/同盘恢复通道BLOCKED。|
|T28|本轮请求launch失败（审查seed），同task操作/回读/应用重开NOT_RUN；安装Store重建PASS不代业务。|
|T31|终态禁止再开工/验收、取消释放/事件、故障关联新任务NOT_RUN；只要求受影响回归，不顺手修前序。|
|T35|证据变更的确认/AI绑定源码范围保留；实际运行NOT_RUN；受控迟到模型回包/交错通道BLOCKED，真实调用0。|
|U03|三可信角色同task事实/权限及禁止自验NOT_RUN。|
|U06|进度/完工/验收区分、退回历史与附件NOT_RUN。|
|U07|重复点击只有宿主tap调度，无业务确认；业务版本冲突/丢响应/恢复NOT_RUN，D04源码FAIL；受控故障/同盘重开通道BLOCKED。|
|U08|宿主launch错误toast已观察；M5附件坏/缺/无权/重试出口NOT_RUN，不能以宿主toast签收业务错误恢复。|
|U11|实际宿主启动/截图成立；M5输入/滚动/面板稳定性NOT_RUN，无业务客户区。|

## 判定与交接

- **最终结论：FAIL**。依据是本轮固定源码D04/D05核心问题未闭合及必需真实业务证据缺失；不是建议项、旧沙箱限制或M4未PASS单独决定。原生启动测试失败已归责审查准备，不能充当作者业务运行反例。
- 精确范围：当前 `M5-harness-r1-1309-current` 对旧M5 r4缺陷的复核及受影响原生验证。旧r4作者候选字段保留；门禁的reviewed_candidate_id/review_summary标清实际当前摘要，不把旧r4当作本轮加载版本。
- 构建方必修仅 **D-M5-05完整内容校验**、**D-M5-04索引失败传播/共同恢复**。保留此前改善与其他模块改动；若正确catalog下整体仍解析失败，再按前序证据修真正阻断本模块的最小解析依赖，不能由本轮809字节日志认定那个parser错误已重现。
- 原生补验必须先纠正R-M5-01，再从实际UI登录、真实上传、正常/退回两链和独立主体回读；负例在应用保存后的副本进行，不能只预置READY/completion。运行中的受控字节/归属/索引异常和同盘重开需驱动支持白名单通道，不由审查方启动宿主。
- 不要求修完所有M0–M4挂账，不发布、不发送消息、不部署、更换渠道或调用模型。原生硬要求不会因“完成优先”改成建议。
- 受影响前序：M4仍FAIL；同main安装字节保持，但本轮未加载，不能更新前序解析/身份/模型结论。没有删除或覆盖历史验收；ACCEPTANCE.json不改。
- 门禁：只更新GATES的M5审查字段和status；更新前快照保存于S/gates-before-phase2.json，review_history保留r4来源，review_report指向本文件，其他模块/作者实施字段不改。
- **不允许进入下一模块，不执行M6。**
- NEEDS_ABRAM=no：本地离线签名/账号/provider均已授权，当前本地安装路径可行；没有公开发布需求或模型欠费。剩余为代码、审查准备与测试通道缺口。

STATUS=FAIL
NEEDS_ABRAM=no
