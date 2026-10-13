# M2 独立 Review r5 · harness 两段式重审

最终结论：**FAIL**。选定发行宿主真实加载当前源码后，8 个场景均出现脚本解析错误和空白应用窗口，M2 登录、任务动作、查询与恢复界面未运行成立。harness 的 **CLEAN 是隔离与回收通过**，不是业务通过。D-M2-01/02/03/04/05/07 的核心或安全问题未闭合；D-M2-06 白名单根因保留闭合。只审本模块，不修业务代码，不执行下一模块。

- 审查者 / 日期：Codex 唯一审查方，2026-10-11（Asia/Shanghai），无子代理。工具不能核实/切换用户指定的主会话 Router 模型，不能获取本会话 createdAt 或原生修改标题；未猜日期、未声称路由或标题已设置。
- 作者明确交接 candidate_id：`M2-r4-worktree`，base=`M2-r3-worktree`；实施报告 `M2_IMPLEMENTATION_r4.md`。本轮按用户 `SKIP_FIRST_BUILD_ALL=1` 对**当前代码**审查，不按 mtime 选择候选。
- 精确被审快照：`M2-harness-r1-1309-current`（审查快照标识，不冒充作者新交接 candidate_id）；HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty。当前 main 369061 字节，SHA-256 **`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`**。旧 r4 副本为303143字节 / `4796cfe4…657ce79`，不可将两者混用。
- 内容清单、r4→当前差异与函数级核对：`runtime/optimization/2026-10-09/M2/native/review_r1_1309/snapshot-start.json`、`r4-to-current.diff`、`function-delta-audit.json`。阶段1至阶段2当前 main 摘要未变化；8份 `.running/*/main.splash` 摘要也与本快照一致。
- 前置：M1 仍为 FAIL，`M1-r2-worktree` / `M1_REVIEW_r2.md`，不存在已接受的 M1 PASS 候选。遵守 Abram 前序挂账裁决继续本模块重审；不写成前置PASS、不改M1门禁。此前rc71/rc3不是本轮BLOCKED理由。
- 环境 / 宿主：macOS；驱动在agent沙箱外执行本审查者请求。二进制 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense` SHA-256 **`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`**。日志实际策略为20000000 instructions、67108864 bytes heap、16777216 bytes storage；本轮没有证明KDF超预算，不沿用旧局部VM的200000指令限制推断本宿主。
- 已读范围：AGENTS、CONTEXT_M2、00/01/02、M2模块、04模板、r4 Review/实施/候选/作者证据、原缺陷涉及源码、harness schema/执行与回收实现、阶段1笔记；阶段2全部summary/result/profile/denials/logs、8张最终帧及MANIFEST，及与夹具路径相关的固定宿主源码。未扩审后续模块业务。
- 运行证据根：`runtime/optimization/2026-10-09/M2/native-runs/review_r1_1309_REQUEST_review_r1_1309/`（下称 **H/**）。运行窗口13:19:36–13:24:56 CST。阶段2独立核对结果：`runtime/optimization/2026-10-09/M2/native/review_r1_1309/phase2/evidence-audit.json`（下称 **A**）。独立请求为 `M2/native/REQUEST_review_r1_1309.json`。
- 安全范围：账号测试表是按已建立五账号的角色结构另造凭据；未读明文凭据文件、MiniMax密钥或家目录私有配置，未改原账号、原业务数据或原包。真实模型请求0；无publish/listing/push/issue/消息/部署。阶段1临时离线私钥已删除，阶段2再次确认keys目录为空。
- 置信度：哈希、隔离回收、原生解析错误/空白窗口、源码确定逻辑 **高**；真实业务提交、独立主体竞争与完整故障恢复 **未知/未执行**。不将源码或历史局部VM结果冒充本轮按钮实证。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|证据完整性与版本|逐行重算MANIFEST，核请求/summary、seed及运行副本摘要|同请求、同候选、证据未被改写|1281项全部匹配；无遗漏文件；请求相同；8份安装/运行源码与冻结main相同|PASS（此范围）|H/MANIFEST.sha256；A|
|隔离与回收|逐场景核profile及其SHA、写禁令/读黑名单探针、前后进程与退出|内核限制有效，前后NONE，无残留|8场景profile_probes.ok=true；pre/post rc1 NONE；pgid_members_after=[]；CLEAN；quit_http；38.21–38.41秒；Library新写0，家目录mtime不变|PASS（本harness运行）|H/*/profile.sb、result.json、sandbox-denials.log；A|
|本地catalog/install_staged|阶段1仅离线导出/签名/verify/官方安装/Store重开；阶段2核真实运行副本|本地路线可运行同字节候选，无公开发布|verify/install_staged/may_run rc0；宿主实际launch hub:octosense-repair并eval369061字节；运行复制摘要一致|PASS（安装与加载）；业务启动FAIL|阶段1offline-store-evidence.json；H/*/logs/host.log及.running源码|
|真实原生M2界面|驱动加载本候选、capture，逐张查看|可见登录/任务/动作/错误恢复出口|8张均为标题OctoSense Repair的空白客户区；每份host.log有45条[E]解析错误|FAIL / D01、D07受影响原生回归|全部最终frames；H/auth_tech_duplicate/logs/host.log:51–95|
|硬1 重试/跨状态/冲突/新动作|正常重复点击与历史v5场景；核稳定键与确认调用顺序|同key返回原action/result、异参拒绝、新确认可独立执行|业务未执行；key函数仍同r4，确认生命周期和原结果接口未闭合；未获得重放/冲突动态结果|FAIL（源码缺陷）；运行NOT_RUN；原键注入BLOCKED（白名单覆盖限制）|D02；H/auth_tech_duplicate、history_newer_version；A|
|硬2 身份/权限/真正竞争|技工与跨项目报修主体场景；核每查写授权及锁源码|可信登录、越权/撤权/到期拒绝，共享事实源竞争一赢家|type动作不受支持，且应用解析失败；两主体均未登录。当前锁无条件写戳return true，无原子互斥|FAIL（D01/D05源码及原生UI）；真实主体/竞争BLOCKED（动作能力）|H/*/host.log:40/42；D01/D05|
|硬3 各写点失败与一致恢复|预置tmp/event目录；逐场景查原始事实/回执/事件和UI|错误点到达，失败无部分提交或可确定补齐|所有业务文件与seed字节相同，tmp/event目录保留；不是错误点被业务执行到的证据。提交源码仍final后另写event、创建提前主写|FAIL（D03/D04源码）；注入NOT_RUN；精确杀进程覆盖BLOCKED|H/tmp_write_failure、event_write_failure；A业务文件对比|
|硬4 写成功读回失败→原动作查询|needs_verify+已变更任务、历史finalv1/currentv5夹具重开，查盘/源码|恢复精确原action完整结果，后续版本不抹掉历史、不重写|needs_verify、v5和历史final原样保留；应用未建立查询/恢复界面。恢复函数仅pending，登录后不重跑，缺rid能造final|FAIL（D04源码）；本轮业务对账NOT_RUN|H/unknown_restart、history_newer_version；A；D04|
|硬5 重复/超时/重开输入与迁移|旧NDJSON+bak、有效+坏行两夹具加载/截图/查原字节|历史完整活跃可查询，失败关闭、重开输入/身份稳定|夹具原字节仍在但未被活跃业务加载；迁移let ok被原生解析器拒绝；原备份/坏行语义亦未修复|FAIL / D07；连续业务重开/超时NOT_RUN，白名单故障控制BLOCKED|H/legacy_existing_backup、legacy_malformed；D07|
|原D06与旧入口|sourceOk、附件/隔离/pin到runCommandBound追踪；核变化|已修白名单保持，旧入口不能绕过|sourceOk/相关dispatch与r4函数相同；白名单根因继续闭合；原生按钮未运行，外部旧Web/MCP/runner运行禁用未测|根因闭合；完整运行NOT_RUN|function-delta-audit.json；main:743、6192、6216、6222–6223|

### 8 个原生场景的实际结果

每场景：隔离CLEAN、profile/capture SHA核对通过；2个type动作均unknown；45条脚本解析错误；宿主启动/退出成功、无panic；所有预置业务文件保持原seed字节。`host_log_markers` 的 launched/eval/remote_quit只证明宿主加载与退出；eval之后还有错误，不能作为应用成功标记。

|场景|最终帧|事实源实际读回|业务检查|
|---|---|---|---|
|auth_tech_duplicate|空白|OPEN/v0、无新增动作/事件；state为seed|登录/重复接单未执行|
|auth_reporter_scope|空白|OPEN/v0、无新增动作/事件|跨主体权限未执行，不能称拒绝通过|
|tmp_write_failure|空白|OPEN/v0；tasks.json.tmp仍目录|没有到达tmp写点，不能称回滚通过|
|event_write_failure|空白|OPEN/v0；events.jsonl仍目录|没有到达提交/event写点，不能称一致性通过|
|unknown_restart|空白|ACCEPTED/v1与needs_verify原样保留|不是实际对账/恢复成功|
|legacy_existing_backup|空白|NDJSON及既有bak原样保留|不是历史已载入活跃回执|
|legacy_malformed|空白|有效行+坏行原样保留|不是已失败关闭迁移/恢复成功|
|history_newer_version|空白|IN_PROGRESS/v5与原final原样保留|不是原action完整结果查询通过|

所有captures存在且哈希正确，最终8帧均已目视核对；`.part.png`也在MANIFEST覆盖内，不作为第二时间点流程帧。每场景`files_written_count=123`且列出的123文件都存在；主要是宿主运行副本、系统资源、news、截图与缓存等。该按mtime记录的列表不是业务写入证据，不能说“写了123文件所以任务执行成功”。

全部denials原文已读取并列入A：有2–3次被拒的443外联、Metal列表缓存拒写及部分/dev/dtracehelper拒写；未将被拒请求认作成功外联或模型调用。各场景无model_proxy/model_proxy_stats，needs_model=false，代理未启用，真实模型请求0。读黑名单5项探针rc1且ok=true；无需要Abram处理的计费错误。

### 审查请求自身的限制与纠正

1. **输入能力确实不覆盖**：全部host.log:40、42报告 `unknown --test-action type:<隔离测试值>`。schema允许不等于选定launcher实现；登录依赖动作记BLOCKED（测试通道缺能力），不归咎于账号口令。即使加入键入能力，当前解析失败也必须先修。
2. **夹具目录是审查方准备错误**：请求把账号及事实写在 `apps/octosense-repair/data/`，固定ba36df0宿主的`containers.rs:44,95`定义storage_root为`apps/octosense-repair/`本身，cardapp.rs:119将该策略应用到Splash。因此本轮不能证明这些夹具被应用fs读到。原文件不变仅证明seed保留；不能作为业务安全、迁移、失败恢复证据。后续请求应把 `identity/accounts.json`、`tasks.json`、回执/事件、state及故障目录直接放在jail根，先用实际写回定位核验。已完成的证据和seed不倒改。
3. **竞争/精确中断能力不覆盖**：harness全局单宿主锁、场景新目录、串行运行，不支持双独立主体同盘屏障竞争、逐写点中断/读回故障/响应丢失、运行后以同盘连续重开；也没有任意原action_key/payload注入接口。相应动态必需项BLOCKED，所需为受控harness测试能力，不需要新增Abram授权。审查方不绕过harness运行或修改业务造证据。
4. **本候选界面启动是确定FAIL**：解析错误发生于候选本身，空白帧已独立取得；不受上述输入/夹具限制影响。不是ABORT，也不是旧agent环境rc71/rc3，不能把启动失败藏进BLOCKED。

### 相关既有用例逐项复核

|用例|本轮结论|证据范围与未执行部分|
|---|---|---|
|G0-B|FAIL|真实账号来源已裁决；实际界面解析失败D01。登录/两独立主体/撤权到期动态矩阵BLOCKED于键入能力，不声称原账号已登录。|
|G0-C|FAIL|D03/04/05核心源码仍未闭合；动态业务未执行。隔离宿主与事实提交分别判。|
|T02|FAIL源码；原生NOT_RUN|创建newId及提前saveTasks仍在；本轮没有原生确认建单。|
|T04|FAIL源码；竞争BLOCKED|建议锁不互斥；串行8场景不代表真正竞争通过。|
|T15|NOT_RUN|陈旧版本UI刷新/输入保留未执行；不是环境BLOCKED。|
|T16|FAIL源码；运行NOT_RUN|D02无确认生命周期；同键跨状态/异参/新意图注入受白名单限制。|
|T17|BLOCKED|白名单/harness无受控断线/响应丢失/同盘连续重开能力。|
|T18|BLOCKED|跨主体登录键入不支持且夹具位置需纠正；盘不变不等于权限拒绝。|
|T22|FAIL源码；错误注入NOT_RUN|final与event分开无恢复记录；目录失败点未被执行业务到达。全部写点中断BLOCKED于harness控制能力。|
|T24|NOT_RUN完整|当前原生入口源码追踪；旧Web/MCP/runner真实禁用未执行，不改旧契约。|
|T29|BLOCKED完整|登录/退出/到期/撤权完整流程及宿主grant事件不能由现有动作白名单覆盖。|
|T32|NOT_RUN|配对码/poll_secret/Web审批非本轮登录证据，未运行。|
|T37|FAIL源码；运行NOT_RUN|D04未知恢复/完整原结果不足；needs_verify和历史记录仅预置未变。G0-E不因此判FAIL。|
|U03|FAIL|8帧没有角色/事实/动作界面；三角色实际投影未执行。|
|U07|FAIL界面；恢复NOT_RUN|真实表单/输入/重试出口未渲染；seed输入保留不等于应用保留。|
|U08|FAIL|空白UI没有可见错误/无权限/恢复出口。|
|T28|FAIL|安装/宿主加载同字节成功，但真实应用打开为空白，操作→权威回读→重开未成立。|

G0-E：**延期缺口（Abram 已裁决，M3 到期）**。本模块不因provider延期FAIL/BLOCKED，不请求真实模型，不要求更换渠道或公开发布。

## 缺陷：原编号闭合复核与受影响原生回归

以下行号对应固定当前main。**P1仅列阻断核心功能/凭据安全的问题**；源码判定和本轮运行事实明确区分。每项均须由构建方修复，审查方未改代码。

### D-M2-01 — P1 / 必修 / 未闭合：原生登录界面不能运行，凭据持久化路径未修

- 文件/行：`app/bundle/main.splash:252`（及249–331含`ok`字段的结果对象）、`1012`（迁移局部`ok`）、`1448`（未验证的三元表达式）；认证/保存`530、580、597、814、6920–6934`。
- 触发：用本次独立签名catalog和同字节候选执行 `launch-hub:octosense-repair`、capture；不需要成功键入即可复现启动问题。
- 实际/预期：8个场景均空白窗口、45条[E]。host.log:51起`Expected expression ... Operator(:)`，:87明确`'ok' is reserved and cannot be a variable name`，:92–95为`Expected )/}`。预期先渲染可使用的登录/任务界面，真实登录后再核每次查写权限。
- 根因/影响：当前合并源码使用选定Splash解析器不接受的保留符号/表达式，阻断整个M2；这是关联原生基线回归，非扩做M3/M6功能。日志内部源码坐标有包装偏移，修复位置须结合实际main内容，不能机械替换日志行号。
- 另有未闭合源码安全问题：登录口令进入STATE，saveState仅清actor而整体序列化，authLogout不清该字段；这三个函数字节与r4相同，r4的真实局部磁盘反例仍是历史来源。本轮未成功键入，**不声称这次原生已再次泄露真实口令**。同步KDF预算尚未实测，不能以旧VM预算制造故障。
- 证据：H/所有最终帧；H/auth_tech_duplicate/logs/host.log:51–95；A；function-delta-audit；M2_REVIEW_r4/D01。
- 具体改法：先以固定发行宿主支持的语法修正保留名/对象结果字段与相关调用方、未支持表达式；不要改变延期模型的业务范围。认证秘密只放不可持久暂态，安全输入、所有结束/退出路径清理，saveState保存白名单偏好；KDF按真实预算决定是否分步，不能降低强度。
- 验证：正确jail夹具+受支持输入通道，原生界面渲染、两个独立测试主体登录/退出/重新登录/查写，盘上撤权到期拒绝；扫描state/log/cache没有测试口令；无parser错误、UI显示真实结果。

### D-M2-02 — P1 / 必修 / 未闭合：稳定槽位不等于不可变确认与原结果返回

- 文件/行：`main.splash:4026–4051、2314–2331、3873、3922、4067–4075`。
- 触发：同任务同命令新独立确认、原确认编辑参数、重开后重试、同key原动作查询及创建重复确认。
- 实际/预期：槽仅task|cmd、不即时持久；异参自动生新key，同参独立新意图没有生命周期；创建先newId，final命中仅false+文本。期望一次确认绑定持久原key/不可变payload，重试完整返回原action_id/result，异参拒绝，新确认独立。
- 根因/影响：内容派生键和槽位不能表达用户意图；新任务ID规避创建重放。函数与r4相同，源码根因未修；本轮原生重放/冲突未执行。
- 证据：当前函数、function-delta-audit；H/auth_tech_duplicate/history_newer_version及A（只证明未执行）；历史r4/D02范围保留。
- 具体改法：持久确认意图含actor/task/command/不可变参数/key/状态，明确新确认与重试；授权后历史查询返回完整原结果、另读最新任务，不依赖当前来源状态。创建前建立稳定意图，不先newId绕开。
- 验证：正常重试、跨状态、更高版本、重开同key不增任务/版本/事件；同key异参拒绝；同payload新意图可独立执行。不得用重复主按钮进入下一命令冒充同命令重试。

### D-M2-03 — P1 / 必修 / 未闭合：任务/final/event未形成关联恢复协议，创建仍提前写

- 文件/行：`main.splash:818–822、2547–2612、2597、3933–3945、4114–4117`。
- 触发：task/final成功后event写失败；新建时saveTasks与commit之间中断；清tmp或final写异常。
- 实际/预期：commitBound先final，调用者后写event，无关联提交日志补齐；创建仍提前成功提示/saveTasks。预期任务/回执/事件作为一个可恢复业务动作，失败不能假成功。**本轮目录故障未进入执行点**，未宣称新原生部分提交反例。
- 根因/影响：分文件顺序写和一次version/status读回不能证明关联一致性。commitBound/logEvent与r4相同；历史r4事件失败的局部原函数磁盘反例仍保留，不当成此次原生实证。
- 证据：当前调用链、function-delta-audit；M2_REVIEW_r4/D03；H/tmp_write_failure/event_write_failure+ A的seed未变。
- 具体改法：统一可恢复动作记录关联before/after/action/receipt/event；每写点异常后确定未提交或补齐已提交，成功显示在核验后；创建走同边界，禁止提前主写/成功；兜底快照必须来自mutation前权威事实。
- 验证：正确jail下每个写点真实故障/中断，核盘/UI与重开补齐，原key不重复。非原子平台必须给可验证恢复协议，不称“四次写”为事务。

### D-M2-04 — P1 / 必修 / 未闭合：needs_verify不恢复、缺rid仍造final

- 文件/行：`main.splash:2513–2542、2597–2598、2617–2663、2687–2695、580–602`。
- 触发：业务已写后读回未知；登录后恢复；缺_PENDING_RECEIPT_ID终结；原finalv1/任务v5查询。
- 实际/预期：恢复只处理pending，needs_verify忽略；boot未登录退出，登录不再对账；版本增大即superseded；缺rid创建新的指定final_status回执；commitBound忽略是否匹配rid。期望从关联事实确认原动作，未知不能hit作成功、不能造final，更高任务版本不能抹掉原结果。
- 根因/影响：没有动作关联恢复状态机，任务版本不是某动作提交证据。核心函数均同r4，未修；本轮unknown/history盘不变只因业务未执行，不是恢复正确。
- 证据：当前函数、function-delta-audit；历史r4/D04；H/unknown_restart、history_newer_version；A。
- 具体改法：final必须关联已核验rid及持久提交事实；缺rid保持未知并返回明确错误；登录后按权限恢复pending/needs_verify等，补齐相关event/receipt，历史结果和最新状态分开。
- 验证：读回故障→恢复同action完整结果，不增version；缺rid/未知不造成功；合法后续version不会污染历史；未提交原动作可按明确协议继续。

### D-M2-05 — P1 / 必修 / 未闭合：建议锁仍不能保证竞争一赢家

- 文件/行：`main.splash:2277–2298、2307、2347、2464–2465、4072`。
- 触发：A/B对同盘并发读v0，分别acquire，然后写任务；未知回执hit/reject/异常返回。
- 实际/预期：当前acquire写stamp后无条件return true，release无owner校验清空；两个上下文都可进入，版本重读/覆盖文件不是CAS；runCommand早退无统一释放。预期共享事实源真正竞争仅一提交且清理安全。
- 根因/影响：后续M4改为建议锁而没有权威单执行或原子互斥；文档自称限制不能关闭M2核心P1。**本轮未执行双主体竞争，不复制旧r4双赢家结果当成新实现实测**。
- 证据：本轮锁函数及r4→当前差异；request/harness串行边界；A。源码可确定互斥保证缺失，实际业务竞争BLOCKED于测试能力。
- 具体改法：用已验证原子原语/权威单执行队列，owner绑定和全部早退/异常清理；不以建议锁、TTL、两次版本检查替代互斥。确无平台原语则交付最小复现和技术能力缺口，不要求公开发布或另建未授权服务。
- 验证：受控harness支持双可信独立会话、同事实源、真实重叠竞争；唯一承接者/业务event/final回执；失败/未知/杀进程/重开不误释他人锁、不制造重复执行。

### D-M2-06 — 原P1白名单根因继续闭合；完整原生回归NOT_RUN

- 文件/行：`main.splash:743、6192、6216、6222–6223`。
- sourceOk与r4完全相同；addEvidence/quarantineEvidence/togglePin允许/拒绝白名单及边界dispatch保留。无需再修改这项白名单。此次没有成功运行这些按钮，根因闭合不扩大为附件/原生用例整体PASS。
- 证据/验证：function-delta-audit及r4历史矩阵；解开D01后回归原三命令合法/非法来源状态、权限、幂等与关联事实，不扩做M5/M6。

### D-M2-07 — P1 / 必修 / 未闭合：迁移语法被发行宿主拒绝，备份/坏行恢复仍缺失

- 文件/行：`main.splash:826–843、992–1027、1012–1017、1036、1046、909–959`。
- 触发：加载当前源码；随后在正确jail中测试已有bak且主文件仍NDJSON、有效+坏行、备份成功后主写失败重开。
- 实际/预期：本轮parser明确拒绝迁移局部变量`ok`（源码1012；内部诊断1015），足以阻断原生加载；源码仍有bak即return nil、有坏行仍写有效子集、失败无全局禁写/恢复。期望历史完整可查并恢复，错误不空覆盖。
- 根因/影响：语法适配和迁移状态协议都未解决。migration函数字节与r4相同；本轮旧夹具位置错误且业务未执行，不将原字节保留称迁移成功/拒绝正确。
- 证据：H/*/logs/host.log:87–91；当前函数/差异；H/legacy_*及A；r4/D07历史来源。
- 具体改法：采用发行宿主支持的命名/分割原语；建立备份来源/迁移状态/目标完整读回协议，已有bak可继续恢复，坏行不截断活跃历史，失败禁业务写且给恢复出口。
- 验证：正确jail中的完整NDJSON、已有bak、坏行、备份/主写失败各场景，查原备份/活跃历史/UI，重开恢复、不覆盖成空；index_of/slice须实际宿主实证。

### 建议挂账（不据此判FAIL）

- A-M2-01材料：r4清单MD5误标SHA、旧before并非所称r3；本轮当前快照已精确定位。建议构建方提供新完整候选/正确增量/文件哈希，不再把旧r4报告当当前合并版本。
- 当前原包hub check拒收、隔离导出签名包也因model_config资源扫描拒收；但独立catalog/install_staged及实际宿主加载已证明本地路线可行。保留分层结果与下一轮包清单建议，不为M2加入公开发布/计费审批，不仅因CLI扫描建议判FAIL。
- 宿主测试动作的schema/实际实现差异和本审查夹具路径纠正属于验证工具/准备问题，不冒充新增业务缺陷。后续请求先核运行动作、jail与截图，不再重复8场景无业务执行的运行。

## 判定

- **最终结论：FAIL**。确定原生界面解析失败；D01/02/03/04/05/07核心/安全P1未闭合。不是“基本通过”，不以CLEAN放行。
- 精确范围：当前快照`M2-harness-r1-1309-current`及其明确派生的隔离签名包；原handoff为`M2-r4-worktree`。不是原始完整bundle准入PASS，不证明真实五账号登录、完整任务可靠性或后续模块验收。
- 修复优先级：**先修D01/D07导致的发行宿主解析失败，让M2界面可运行；再按原编号修凭据、确认意图、提交一致性、未知恢复、真互斥、迁移。** D06白名单不再重复修。修复后交接新候选/差异及受控原生证据。
- 阻塞/未测：受支持输入、同盘双主体竞争、逐写点中断/响应丢失/读回故障控制缺少白名单测试能力，记BLOCKED；其余由于本候选解析失败未执行项记NOT_RUN，不能泛写环境BLOCKED。夹具路径错误已明确纠正，不改变完成的证据。
- 受影响前序回归：本次harness隔离/回收PASS，只覆盖本运行通道；不关闭旧M1 cleanup实现缺陷、不改变M0/M1 FAIL。候选桌面基线实际空白已记录在本M2报告。
- 门禁：只更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M2状态及审查字段，原candidate/base/实施报告/构建字段保留；r4审查字段整体追加进review_history。review_report指向本r5。既有38业务/12UI/P0台账不覆盖、不删减，逐项本轮范围在本报告与M2 review_acceptance记录。
- **不允许下一模块**，不提供下一模块入口、不执行它。留在M2交给构建方按上面原编号修复和重新交接。
- NEEDS_ABRAM=no：账号/provider及隔离离线签名均已授权；无MiniMax请求/余额错误，本地安装路线可行，无公开发布需求。剩余是实现及测试通道技术问题，不是新授权问题。

STATUS=FAIL
NEEDS_ABRAM=no
