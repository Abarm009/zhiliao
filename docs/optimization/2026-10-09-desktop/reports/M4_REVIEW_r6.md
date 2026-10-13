# M4 独立 Review r6

**最终结论：FAIL。**当前候选真实加载后，三个原生场景均出现解析错误，业务客户区空白，核心流程没有成立。D-M4-03、D-M4-04 部分改善但未闭合；B-M4-01 仍是直接阻断 M4 的最小前序依赖。隔离与回收通过，不进入下一模块。

- 审查者 / 日期：本会话唯一独立审查方，2026-10-11（Asia/Shanghai），两段式 `r2_1309`；没有子代理，没有修业务代码。
- candidate_id：`M4-r5-worktree`，声明base=`M4-r4-worktree`；GATES、作者报告和源摘要共同定位，未按文件修改时间选版本。HEAD=`8d730569546cb57310944bb299695134df773b9d`，未提交工作树。
- 当前主源：SHA-256=`dcf73555767c895ac04a8a5904246f9635b21481ac9f4e07b14cc13709e3d006`，388582字节、8330逻辑行。与候选声明、安装副本及三场实际 `.running` 副本一致，审查开始至门禁写入前未变。
- 上一轮：`M4_REVIEW_r5.md`，审查对象 `M4-harness-r1-1309-current`；其源SHA=`3e30355262e2a06dcb0216e0847cdb6166e8420fbf6793bf2fbcf31fda4ae23f`。本轮差异4199字节、71行，四函数变化；另保存声明r4→r5的完整差异，不能把所有累积增量都称本轮修复。
- 作者报告：`reports/M4_IMPLEMENTATION_r5.md`；候选：`runtime/optimization/2026-10-09/M4/r5/CANDIDATE.json`。作者68/68不等于原生业务通过；独立重跑静态45/45、改写Python行为16/16，只证明这些脚本的有限范围。
- 前置：M3仍FAIL，候选 `M3-r5-worktree`、报告 `M3_REVIEW_r6.md`；没有已接受PASS前置。按用户挂账裁决继续审当前模块，不顺手修全部前序，不冒称串行前置满足。
- 宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。驱动在agent沙箱外执行审查方请求；审查方未启动宿主、VM、sandbox-exec或pgrep。
- 实际运行窗口：2026-10-11 15:14:37–15:15:18 +08:00。三场均CLEAN、quit_http、宿主rc0，但业务运行FAIL。
- 路由 / 标题：工具没有提供实际主会话Router路由、当前会话createdAt和标题读写接口，未冒称已切换指定型号或实际命名。
- 已读范围：第1段已读AGENTS、CONTEXT、00/01/02/M4/04、上一轮缺陷、实施/候选/证据、相关T/U定义及harness；第2段只核这些缺陷、受影响回归和驱动证据。
- 已执行范围：独立离线签名和官方Store本地安装/重开准入；独立请求；外部驱动三场原生加载；481项证据摘要核验、实际PNG查看、完整host/denial日志和结果字段重算、源/种子/加载副本/门禁一致核查。
- 未执行范围：可信登录后的M3创建→接单→设备→预约→开工、实际领域反例、三个真实角色、真正同盘业务并发、模型交错、失败/丢响应/同盘重开恢复。解析失败导致业务NOT_RUN；白名单请求结构无法覆盖的并发/受控故障子项单独BLOCKED。
- 置信度：候选一致、空白UI、解析失败、隔离回收及源码控制流 **高**；具体解析token根因 **中**；未执行领域/真并发/模型结果 **未知**。

## 证据索引与独立核验

- **H**：`runtime/optimization/2026-10-09/M4/native-runs/review_r2_1309_REQUEST_review_r2_1309/`。
- **S**：`runtime/optimization/2026-10-09/M4/native/review_r2_1309/`。
- **R**：`runtime/optimization/2026-10-09/M4/native/REQUEST_review_r2_1309.json`。
- **N**：`runtime/optimization/2026-10-09/M4/native/REVIEW_NOTES_r2_1309.md`。
- **A**：S/`native-evidence-audit.json`，由S/`audit_phase2.py`可重复核验，不启动原生进程。A的PASS仅指证据一致性，不是M4业务PASS。

|独立场景|隔离回收|当前字节加载|原生UI与日志|权威业务数据|
|---|---|---|---|---|
|r5_cold_reporter /请求1280×800|PASS；probes.ok=true，pre/post NONE，pgid_after=[]，CLEAN|PASS；source/config/identities/manifest/listing与已安装副本一致|FAIL：空白客户区；host.log:45–49五条parser错误|五业务文件均与原seed相同|
|r5_expired_tech_hint /请求1280×800|同上PASS|同上PASS|FAIL：空白客户区；host.log:43–47相同错误|同上；过期夹具未实际确认|
|r5_terminal_manager_hint /请求980×760|同上PASS|同上PASS|FAIL：空白客户区；host.log:43–47相同错误|同上；终态夹具未执行取消|

1. H/MANIFEST.sha256共 **481项，摘要错误0、缺文件0、未列入文件0、重复0**。summary.request与R逐字段相同；harness/template摘要匹配。各result的宿主/profile摘要、实际命令与请求、seed来源清单、capture摘要、write列表、denial摘要、host_log_markers/bytes/tail均独立核对。
2. 每场1张请求图，3张全部存在且摘要匹配，已逐张查看。全部是2800×1718的宿主画面，应用标题“OctoSense Repair”下客户区空白，没有登录/任务/表单/业务错误出口。前两张SHA相同，第三张主要时间显示不同；**不能据此称三个真实角色首屏通过**。请求尺寸不等于客户区布局实测，缺操作前后对比不单独判FAIL。
3. 每场files_written_count=123，列表123项，路径均在场景目录且存在；主要为运行代码副本、系统应用/缓存、profile/log/PNG。`state.json/tasks.json/actions.jsonl/events.jsonl/identity/accounts.json`全部逐字节不变。**零业务变化只是流程未执行，不是权限拒绝/过期校验已通过。**
4. Seatbelt profile与模板/场景参数逐字节一致；HOME、app-data、tmp、配置、缓存均指向本次运行目录；禁读秘密/明文凭据/用户配置及SSH，拒绝外写，仅允许声明的本机控制网络路径。探针通过，library_scan空，原HOME `.octosense` mtime前后一致，无进程组残留。denials中的远端443、Metal系统缓存、`/dev/dtracehelper`均是**被拒绝**的尝试，不是成功外联/外写。
5. r5_cold_reporter的pgid_members_running额外记录过一个短暂`osascript`同组进程，退出后为空。审查请求和实际cmd仅有授权launch-hub/taps/capture，审查方没有调用osascript；现有快照无该子进程参数，不能声称宿主内部绝无此调用或认定其用途。按用户指定probes/pre/post/pgid_after/CLEAN判据，隔离回收通过；此观察如实保留，不拿它证明业务操作成功。
6. 三场均实际eval **388582 bytes**，随后五条parser错误：`Expected )`×3，`Expected } not found`×2，内部坐标 **5258:26/28**。host rc0、无panic只说明正常退出。当前业务程序整体未被解析成功；不能把日志的5258直接当源文本5258行，见B-M4-01。
7. 新离线bundle digest=`c4c614f86f17784e8be31d087efc40bcf731fd2d288dc62302dbaaf595e392d7`。digest_seen_in_seed=true、digest_seen_in_host_log=false；本轮用实际 `.running` 副本摘要和launch-hub日志证明加载，不用seed含digest冒称加载。
8. 第1段实际离线keygen/certify/stamp/sign-manifest/verify和现有官方接口install_staged/may_run均rc0；两把隔离私钥已删除，本段再核keys目录为空。证据S/offline-store-evidence；本地路径可行，无需公开发布/公开签名/listing。派生manifest签名只在测试副本，业务源未改。
9. 三场均needs_model=false；model_proxy_stats字段和模型代理文件均不存在，与请求一致。本轮真实调用0，无402/欠费记录，不能称真实T35通过。
10. 作者候选文件46行相邻字符串不符合JSON语法；原文件未改，仅审查副本连接相邻字符串后读取身份/摘要。来源可定位，属建议，不单独判FAIL。作者lock_probe使用默认项目外tempfile/Manager且不是原生业务并发，未重跑；保留读取作者7/7的来源，不继承其结论。
11. 第1段首次检索误读项目外记忆/技能文件的目录约束偏差已在N公开记录；没有项目外写入。第2段显式读取和写入均在项目内，没有读取生产明文凭据或provider秘密。不能将第1段执行过程描述为全程严格符合只读目录约束。

## 必需检查

|检查|独立步骤 / 期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/证据一致|冻结r5，核安装与运行副本、summary和摘要|当前候选加载一致；M3前置仍FAIL|PASS加载子项；前置未满足|A、S/start-snapshot、R、GATES|
|真实UI主链|M3真实创建→接单→设备→预约→开工，不手改状态|三个业务客户区空白，无法开始主链|**FAIL原生入口；主链NOT_RUN**|三张PNG；三场parser日志|
|硬1资格/设备服务|合法绑定与越权/技能/伪造/仅安装位置无服务拒|原守卫同源；没有实际命令|NOT_RUN|S/source-traces；运行解析失败|
|硬2预约|提议不直升，合规确认，过期/改约/冲突拒绝|nil重读已修，授权早退spec残留/读坏盘继续仍存；预约未提交|D03 PARTIAL未闭合；原生NOT_RUN|main:2467、2591；A|
|硬3真正并发|同盘两个独立上下文仅一成功；相邻可行|源码普通锁仍可竞争；harness按场景顺序新盘|D03未闭合；**BLOCKED仅真并发通道**|main:2397；harness:224、439；schema|
|硬4开工与旧技工拒|有效设备+有效预约+当前授权承接者|开工守卫同源，未实操|NOT_RUN|startProgress/reassign traces；A|
|硬5真实输入/角色/回执|三角色能理解填写确认，同工单事实一致|客户区空白，无表单/当前动作/错误出口|**FAIL可用桌面入口；领域NOT_RUN**|三张PNG；A|
|改派/改约撤销|旧授权/确认/AI不可执行，新绑定可恢复|清AI字段改善，历史字段编辑集仍可复用|D04 PARTIAL/P1；原生NOT_RUN|main:2213、4154；S独立静态审计|
|失败与恢复|拒绝清理、未知结果对账、重试重开不重复|授权早退未清理，业务未运行；schema无受控故障/同盘重开|D03未闭合；**BLOCKED仅故障通道**|main:2467；schema；A|
|隔离与回收|指定探针/进程/写入/网络判据成立|三场CLEAN且全部指定条件满足|**PASS；旧rc71/rc3环境理由关闭**|H/result/profile/denials；A|

### 既有用例逐项复核

NOT_RUN由当前解析失败导致，不用作者、旧后端PASS或预置状态替代。BLOCKED只用于白名单实际结构无法覆盖的子项。

|用例|本轮结果与精确范围|
|---|---|
|T04|BLOCKED：当前请求/harness逐场新盘顺序启动，没有两个原生上下文同盘同步接单通道；D03源码仍未闭合，无真实双成功结论。|
|T05|NOT_RUN：技能/无项目权限接单、经理分配身份事件因解析失败未提交；原守卫同源。|
|T06|NOT_RUN：SCHEDULED改派、旧预约取消/ACCEPTED/新承接者/旧技工拒未执行；D04受影响。|
|T07|NOT_RUN：编码与asset载荷等价、伪造/跨项目/归档设备实际绑定未执行。|
|T08|NOT_RUN：合法服务空间和仅安装位置无服务关系实际绑定未执行；服务关系源码子范围保留。|
|T09|NOT_RUN：无设备开工、IN_PROGRESS技工换设备拒及经理更正旧/新值理由未执行。|
|T10|NOT_RUN：提议不直升、报修人确认、非报修人拒未执行；spec局部值接线已修但D03其余范围仍P1。|
|T11|BLOCKED真并发通道；跨项目重叠拒和相邻正例原生提交NOT_RUN；权威重读不代替原子边界。|
|T12|NOT_RUN：改约待确认保留旧预约、新确认替代、拒新保旧未实操；D02源码改善保持。|
|T13|NOT_RUN：410、无定时器仍拒、客户端伪时间反例未执行；预置已过期提议不算校验通过。|
|T14|NOT_RUN：当前真实上海时间输入/UTC毫秒、模糊时间核对、end<=start错误反馈；D01源码子范围保持。不因未尝试type而新增输入BLOCKED结论。|
|T15|NOT_RUN：旧version拒绝/刷新/保留输入和阶段百分比控制未执行；D03授权早退/坏盘风险保留。|
|T31|NOT_RUN：真实取消释放预约/留历史、终态拒操作、再次故障关联新任务；预置CANCELLED只作负例。|
|T35|D04源码PARTIAL未闭合；真实生成期间改派/改约和旧回包执行NOT_RUN；schema无受控延迟回包/交错动作，该子项BLOCKED。|
|U01|FAIL当前原生入口：没有业务首屏信息或主动作；三可信角色“待我处理/下一人”NOT_RUN。|
|U03|FAIL当前可用桌面；同工单三可信角色事实/权限/不能自验NOT_RUN；磁盘actor hint不是可信会话。|
|U04|FAIL当前桌面无预约/错误投影；具体当前预约/待改约区分、冲突/过期命令NOT_RUN。|
|U05|FAIL当前桌面无设备安装/服务/依据展示；实际设备选择与绑定NOT_RUN。|
|U07|FAIL当前入口无可用错误恢复出口；重复点击被调度但没有业务按钮，不能算拒绝通过；丢响应/受控写点/连续同盘重开子项BLOCKED，业务恢复NOT_RUN。|

## 缺陷（沿用编号，不做无关扩审）

### B-M4-01 — P1 / 必修 / OPEN：当前完整程序解析失败，阻断M4所有桌面流程

- **文件与行**：`app/bundle/main.splash:5254–5256` 的 `m5_fnv_mix_byte` 是前序报告关联的疑点；本轮日志内部坐标为5258:26/28，**并非直接等于源文本5258行**。实际故障范围为完整main.splash。
- **触发**：三个全新隔离seed通过R加载同一r5签名bundle；宿主参数和实际运行副本都核对一致。
- **实际 / 预期**：每场五条parser错误、空白业务客户区；预期能显示登录/任务/表单/错误出口并进入M4，实际无法进入任何M4命令。是真实原生FAIL，不是sandbox rc71/pgrep rc3或未授权。
- **根因 / 影响**：当前单文件程序不被选定宿主解析器接受。bitwise表达式与上轮相同，具体token兼容修法未做本轮最小probe，置信度中；整体解析失败/入口阻断置信度高。
- **证据**：H/r5_cold_reporter/logs/host.log:45–49；另两场:43–47；三张实际PNG；A.running_copies、parser_errors；S/m5_fnv_mix_byte同源记录。
- **具体改法**：只修确实阻断M4的最小解析依赖，不扩展M5业务。在harness提交同宿主最小语法probe及整体当前bundle复跑，确认无parser错误且业务客户区实际渲染。不得在审查方修改源码绕过。
- **验证**：当前完整候选三场能真实显示入口；再从真实M3创建到接单/设备/预约/开工，回读权威任务和回执，不能预置状态代链。

### D-M4-03 — P1 / 必修 / PARTIAL：spec接线已修，授权拒绝清理/坏盘处理/真互斥未闭合

- **文件与行**：`main.splash:2467` 授权早退；`:2475–2476` 保存/清空；`:2574` 局部spec消费；`:2591–2593` 异常nil跳过冲突；`:2397–2439` 普通抢锁、`:2443–2459` 按actor释放，`:2528`版本检查、`:2726`提交。
- **触发**：预约命令设置spec后授权撤销；任务盘读取/解析失败；两个独立上下文同盘，均先读空锁并各自在竞争写前完成读检查。
- **实际 / 预期**：已正确使用局部 `_cc`，且大部分版本/回执早退会清理；但授权失败在清理之前return，读坏盘被当成未发现冲突。普通读→写→读回与同actor重入没有证明临界区唯一。预期所有退出清理、未知权威盘明确拒绝、真实双接单/重叠确认仅一成功。
- **根因 / 影响**：瞬态spec生命周期不覆盖授权出口；异常被吞；权威重读与提交之间无已验证原子串行边界。影响硬2/3及失败恢复，属于核心必修。**本轮原生先解析失败，没有实际走到这些分支或产生双成功。**
- **证据**：S/source-traces、independent-static-audit及两份diff；作者lock_probe把清理模拟在authorizeCommand之前，而真实源码顺序相反。其45/45关键词检查、改写行为16/16和旧rename模拟7/7不能闭合真实命令。
- **具体改法**：保存/清空纯内存spec覆盖授权出口，同时保持授权前没有业务持久写；权威读失败显式拒绝。使用可验证的单一串行提交边界，owner绑定独立持有实例，把权限/最新事实/冲突/任务预约及事件回执提交包住；需要宿主能力时给具体最小复现和方案，不擅增服务。
- **验证**：授权失败后spec为空且下一正常命令不被污染；坏盘明确拒/正常恢复；两独立原生上下文同盘接单与跨项目同技工重叠确认仅一成功，相邻均成功，核任务/预约/事件/回执及同盘重开。Python改写循环/普通文件模拟不代验。

### D-M4-04 — P1 / 必修 / PARTIAL：累计旧编辑记录仍可通过“新填写”守卫

- **文件与行**：`main.splash:2213–2255` 失效；`:3744–3749` 累计human_edited_fields；`:3814`原文编辑；`:4154–4167`最终确认读取累计字段集合，`:4180`后调用创建。
- **触发**：失效前同一草稿human_edited_fields已包含problem/space_id/category；改派/改约使其失效；之后仅改原文A→B或联系人，不重新核对三个关键字段，再确认。
- **实际 / 预期**：清AI字段/转manual和非空新AI hash守卫确有改善；空旧编辑数组时仅改原文会被拒。**但失效不清空或分代隔离历史human_edited_fields**，最终只查三项存在；新版本增长加历史集合即可越过manual恢复。manual原文编辑又不更新旧problem。预期只有本次失效之后在当前主体/项目/任务/输入/事实上的明确新核对才能执行，实际源码仍可消费旧内容。
- **根因 / 影响**：累计字段名被当作本轮核对，没有字段编辑/核对epoch/version绑定。撤销与重新确认不可靠，影响核心T35/改派改约确认安全。**本轮未在原生创建错误工单，源码可达与动态结果严格区分。**
- **证据**：S/source-traces.m4_invalidateConfirmation/editDraftField/editRawText/confirmDraftModelBound、independent-static-audit；作者behavior_probe只覆盖失效前空集合等有限反例，没有历史三项齐备后仅改原文。
- **具体改法**：保留历史审计，单独维护本次失效后的字段确认epoch/version；最终确认消费完整当前绑定。可明确核对当前值，不强迫无意义改值；只有实际编辑对应字段或显式核对才记本轮完成。保留首次人工/关闭重填/重新AI的正常恢复。
- **验证**：旧编辑集空/部分/齐全三组，改派与改约后无编辑/只改原文/只改联系人均不能直接执行旧proposal；当前明确核对关键字段、新AI当前绑定可继续。迟到真实模型回包和撤权/版本交错需独立原生证据。

### 已闭合源码子范围与建议

D-M4-01日期、D-M4-02自身预约排除/准入后修改、D-M4-05开工资格/设备/时窗与上轮同源，保持其已关闭源码子范围；本轮完整原生仍NOT_RUN，不重复编必修。A-M4-01/02/03保持建议挂账。候选JSON格式与累积差异描述建议修正，不因这些建议单独判FAIL。

## 判定

- **最终结论：FAIL**。精确范围为 `M4-r5-worktree` 的D03/D04闭合、直接解析依赖和受影响桌面/命令回归。已经实际复现核心入口失败，不能把本轮整体记BLOCKED或“基本通过”。
- 必修：先解除B-M4-01最小解析阻断；修D-M4-03残留清理/坏盘/串行边界；修D-M4-04本次失效后的新绑定。无需修完所有前后序挂账才复跑，但不能放过本模块核心P1。
- 未测 / 阻塞：领域业务因解析失败NOT_RUN；同盘真并发和受控故障/模型交错等白名单通道子项BLOCKED，需要harness支持独立上下文共享隔离盘及同步动作、受控写点/回包/响应和重开。不以本机沙箱rc71/rc3作理由；未尝试输入动作不自动判不支持。
- 受影响前序：M3的整体解析依赖已由本轮独立原生重现，M3门禁仍FAIL；不替其补PASS，不修其他模块。
- 门禁：仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M4审查字段及status；保存更新前快照并追加history，review_report指向本文件。原 ACCEPTANCE.json 未改，旧后端/历史证据不冒充当前原生PASS。
- **不允许进入下一模块**；不执行M5。
- NEEDS_ABRAM=no：本地离线安装路径成立、身份/provider/离线签名已授权；本轮模型0调用无欠费/402，没有公开发布要求。剩余均是代码和测试通道缺口。

STATUS=FAIL
NEEDS_ABRAM=no
