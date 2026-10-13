# M2 独立 Review r2

最终结论：**BLOCKED**。本轮无法把现场修复源码绑定到已交接候选，且原生隔离/清理条件不成立。上一轮正式候选 `M2-r1-worktree` 的 **FAIL** 保留；本轮没有把未交接的 r2 改动签成 PASS。现场修复差异存在已独立复现的核心 P1，见原缺陷编号 D-M2-01～07。没有改业务代码，没有执行下一模块。

- 审查者 / 日期：Codex 唯一审查方，2026-10-10，Asia/Shanghai。无子代理。置信度：字节定位、确定源码分支、隔离文件竞争探针 **高**；原生语义/真实主体/UI **未知**。
- candidate_id / HEAD：正式交接仍为 `M2-r1-worktree`，base=`M1-r2-worktree`，HEAD=`8d730569546cb57310944bb299695134df773b9d`。GATES、实施报告 §10 均定位 r1，不按修改时间选候选。
- 正式 r1 主源 SHA-256=`2bef267a3bc3e1111eace38b039323ad9ee948b510ab53f3617ce55f4b1612f0`；其副本仍可从 `review-r1/store-test/local-mirror/artifacts/octosense-repair-0.1.0-b.bundle/main.splash` 重建且哈希一致。现场 `app/bundle/main.splash` 为113025字节，SHA-256=`edba9dc9e335acc8577327c9ebc8f054d27b7bf7910c9caf33f73d0fa61d9500`，已经不是交接的 r1。
- r2交接缺口：没有 `M2_IMPLEMENTATION_r2.md`、没有 r2 固定 candidate_id/内容清单；GATES未更新为r2。存在 `M2/r2/evidence/source_audit.json` 的19/19名称/文本扫描；构建日志停在“现在写r2报告”，未发现完成记录。这不等于已交接。已向Abram请求候选定位，本报告生成前未收到答复。本轮仅对该字节快照作原缺陷修复诊断，不替代正式候选验收。
- 开始/结束：31个输入文件内容快照一致，包含完整bundle、正式报告和r2扫描证据。差异保存在 `results/r1-to-unhanded-r2.diff`；宿主二进制哈希在 `results/candidate-audit.json`，与r1 Review记载一致。报告输出后会再次核验。
- 作者报告：`reports/M2_IMPLEMENTATION_r1.md`。上一轮：`reports/M2_REVIEW_r1.md`。以 `M2/CONTEXT_M2.md` 为复审上下文；阅读实际AGENTS、00/01/02、M2、04模板，后续只追踪原七项缺陷涉及源码，不扩审其他模块。
- 前置：M0、M1实际仍FAIL，M1不存在独立PASS接受候选。依Abram“前序挂账”裁决继续本模块定位，不把前序FAIL单独作为本次拒收原因，也不伪造已接受基线。M0/M1字段不改。
- 实际环境/模型：macOS工具环境；主会话Router和具体模型路由无法通过现有接口独立确认，未声称切换。无可用会话createdAt/标题变更接口，未猜日期改标题。
- 隔离运行：所有本轮文件探针、合成数据、日志、HOME/cache/data/tmp目录在 `runtime/optimization/2026-10-09/M2/review-r2/`。宿主启动前 `sandbox-exec true` rc71：`sandbox_apply: Operation not permitted`；`pgrep` rc3：`Cannot get process list`。因无法验证强制写入限制及进程回收，**没有启动launcher**，没有调用launcher --help，没有创建本轮窗口，历史桌面窗口是否残留 **UNKNOWN**。仅设置HOME不能证明框架不写真实app-data/系统缓存。
- 审查操作偏差：开头记忆关键词检索曾只读项目外 `/Users/abeam/.codex/memories/MEMORY.md`，违反本轮读取范围；随后停止项目外资料检索。未使用该记忆作审查依据，未写项目外文件。记录偏差，不宣称本轮全程读取隔离完全合规。
- 已运行：内容核对、当前隔离预检、真实磁盘锁顺序/双独立进程竞争、旧日志boot分支磁盘投影、回执ID匹配分支、重放/失败内存恢复分支投影；这些是**源码控制流的Python翻译/投影探针**，不是Splash原生执行，也不是实际业务按钮端到端成功证据。
- 未运行：真实按钮、可信A/B会话、原生逐写点/读回失败/超时/关窗恢复、原生全套T/U案例。不能把源探针、静态19/19或作者r1 Python契约转签为原生PASS。

证据根：`runtime/optimization/2026-10-09/M2/review-r2/`；下文 `results/…` 相对此目录。复现：在项目内执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M2/review-r2/probes.py`；使用新空隔离目录复现，勿覆盖已保存历史证据。

## 必需检查

|检查|独立步骤|期望|实际|结果/范围|证据|
|---|---|---|---|---|---|
|候选一致|比较正式清单/保留副本/当前源码|明确交接id且字节一致|正式r1副本匹配；现场已变更，无r2交接|BLOCKED|candidate-audit、start/end-snapshot、r1-to-unhanded-r2.diff|
|按钮到事实源|main_action_btn→runAction→acceptTask→runCommandBound→runCommand→recordReceipt→commit→commitBound→logEvent|单边界、提交与事件/回执一致|接线存在；锁、回执、恢复仍有下述核心问题|源码诊断；原生BLOCKED|source-traces；main.splash:2294、1597、1050、534、1011、890、937、710、213|
|硬1 重放/冲突/新意图|核对新键公式、历史匹配条件及较新版本；投影不同key同payload|原键复用、同键异参拒绝、独立新动作可提交|key随版本变；早查final忽略key，新独立同payload被旧回执吞掉；未返回原result|FAIL源码分支；原生NOT_RUN|replay-recovery-source-probes；D-M2-02|
|硬2 权限/竞争|检查主体/撤权读取；双独立进程共用目录，屏障只控制exists时点|授权不可选择/过期；竞争仅一赢家|身份来自可持久化STATE与启动缓存；两个独立进程均取锁true；释放后第二次取锁false|FAIL锁分支；真正业务主体/完整接单BLOCKED|lock-source-probes；D-M2-01/05|
|硬3 中断/假成功|追踪commit返回及创建路径；注入commit失败分支并查内存/盘|失败状态不成功、事实一致恢复|多数调用方新增失败guard有改善；仅回滚version，status/assignee仍污染；创建先成功事件和主文件后核验；事件仍在final之后独立写|FAIL源码/投影；原生写点BLOCKED|replay-recovery-source-probes、source-traces；D-M2-03|
|硬4 未知结果对账|检查recordReceipt、boot对账、历史查询与final结果|pending/needs_verify可恢复原动作正确结果|普通pending元数据仍缺；boot不处理needs_verify，按版本标签改写；final仍存提交前结果|FAIL源码；原生读回/重启BLOCKED|source-traces；D-M2-03/04|
|硬5 迁移/重启/输入|合法两行JSONL副本按boot顺序，查备份guard；核对split上界|旧历史活跃可查且禁止未迁移覆盖|load先备份，migrate因备份存在退出；split仅遍历首行；后续整数组保存覆盖活跃历史|FAIL分支/磁盘投影；真实桌面NOT_RUN|migration-source-probe；D-M2-07|
|旧入口回归|addEvidence/quarantineEvidence/togglePin→sourceOk|接入统一边界且合法动作仍可执行|新增边界调用，但sourceOk无这三命令，全部走默认false|FAIL源码；旧Web/MCP/runner运行NOT_RUN|source-traces；D-M2-06|
|回执归属回归|旧A、新B，以rid B更新|A不变、B唯一终结|投影A不变，B匹配；缺rid仍新建final兜底问题未闭合|局部PASS，D-M2-04未闭合|finalizer-source-probe|
|本地catalog/install_staged|核对r1 Store证据和源码变化|当前交接digest对应离线签名与安装|r1 Store验证是历史PASS；现场digest已变，无本轮固定候选，不沿用r1安装作为r2证明|本轮NOT_RUN；历史保留|review-r1/results/local-store-validation.json、candidate-audit|
|隔离/宿主回收|独立预检再决定启动|可强制隔离且核验无残留|rc71/rc3；host_started=false|BLOCKED|preflight.json|

本轮未生成私钥、未签名、未联网、未上传、未publish/listing。r1私钥删除证据仅保留历史来源，本轮不伪造新的删除记录。宿主路线仍按本地catalog/install_staged；r1证明Store层可行，不需要公开发布授权。当前问题不是本地路线已被证明不可行。

### 相关既有用例逐项范围

|用例|本轮状态|范围|
|---|---|---|
|G0-B|BLOCKED；源码D-M2-01未闭合|可信业务身份来源和真正独立主体缺失；不是G0-E延期。|
|G0-C|BLOCKED原生；源码/锁投影FAIL|D-M2-03/04/05，未用顺序竞争代替真实并发。|
|T02|NOT_RUN原生；源码FAIL|创建先save/事件后核验且version0漂移；D-M2-02/03。|
|T04|BLOCKED完整接单；锁探针FAIL|真实两个OS进程同盘双取锁，不宣称已跑原生双主体接单。|
|T15|NOT_RUN完整案例|旧版本守卫仍存在，不等于UI输入保留/刷新通过。|
|T16|NOT_RUN原生；源码FAIL|较新版本key变、新意图被fp归并；D-M2-02。|
|T17|NOT_RUN|断线全量回读/重连未执行。|
|T18|NOT_RUN|列表/搜索/事件/附件权限完整范围未执行；仅追踪主体。|
|T22|BLOCKED原生；源码/分支FAIL|只有失败分支内存/盘投影；未执行原生每个写点。|
|T24|NOT_RUN完整旧入口；源码FAIL|当前三入口sourceOk阻断合法动作；外部Web/MCP/runner没跑。|
|T29|NOT_RUN|完整grant关闭/退出/到期/共享卡授权未执行。|
|T32|NOT_RUN|配对码/poll_secret/审批绑定/token隔离未执行。|
|T37|BLOCKED原生；源码FAIL|needs_verify无恢复、final结果仍是提交前状态。|
|U03|BLOCKED|真实三个可信主体桌面事实一致/不可自验未执行。|
|U07|BLOCKED|重复点击/超时/输入保留/重启未执行；源码失败分支仍污染任务。|
|U08|NOT_RUN|完整中文错误/恢复出口未执行。|
|T28|BLOCKED|当前候选launcher打开→动作→权威回读→重开未执行；r1 Store历史PASS不冒充。|

G0-E：**延期缺口（Abram 已裁决，M3 到期）**，不算本轮FAIL/BLOCKED或NEEDS_ABRAM依据。M1清理/布局挂账不扩修，当前启动预检仍不允许启动；没有推翻或改写前序门禁。

## 缺陷：仅复核上一轮编号

以下源码行号对应上述113025字节现场快照。它不是已交接r2候选；结论是修复诊断，必须冻结交接后再原生复验。七项原P1均未完整闭合，没有扩到下一模块或为建议判FAIL。

### D-M2-01 / P1 / 必修：主体信任与授权生命周期未闭合（部分修复）

- 文件/行：`app/bundle/main.splash:96`、`:290`、`:368`、`:404`、`:534`、`:564`、`:811`；`identities.json`默认身份数据。
- 触发：复用state.json的actor；运行后撤权/删除项目角色；持旧final回执再查询。原生触发BLOCKED。
- 实际/预期：setActorM2已不改actor、getMe优先注册表，是局部改善；但actor仍从可写STATE读取，未找到宿主已核验主体接入，注释声称default_actor派生而源码无该派生赋值。注册表只启动读取；历史final查询位于identityActive之前。预期可信主体、项目授权和撤权在每次写/查时核验，失败关闭。
- 根因/影响：注册表名单替代主体证明，启动缓存替代权威授权；无法证明不同操作者不能借位、自验或撤权后继续使用历史入口。
- 证据：source-traces（loadIdentities/identityActive/getMe/setActorM2/runCommandBound），replay-recovery-source-probes的授权顺序。
- 具体改法：先明确Abram认可的业务身份来源；建立不可由state/视角选取的会话subject。每次边界刷新/核验授权并在历史查询之前执行；身份不可用禁写，去掉业务路径的USERS兜底。勿将演示注册表标为认证完成。
- 验证：真实A/B独立会话；A切展示视角仍不能以B写；在线撤权/到期/移出项目下一次命令及旧动作查询均按权限拒绝；盘事实不变。

### D-M2-02 / P1 / 必修：按payload误吞新意图，稳定键未真正持久化（未闭合）

- 文件/行：`main.splash:534`、`:544`、`:557`、`:879`、`:967`、`:974`、`:1058`。
- 触发：同任务recordProgress完成后，用独立新意图/新key提交相同内容；原意图响应丢失后任务版本升级再重试；同key改内容。
- 实际/预期：早查final只匹配actor/task/cmd/fp，根本不看key；投影不同新key也返回旧action，合法第二次相同记录被吞。generateStableKey包含version/payload，改版本/参数自动改变key，没有保存确认意图供重启重试；只给STATE文本，不返回原result。预期原键恢复查询、同键异参拒绝、独立新键可执行，新版本不抹原动作。
- 根因/影响：把内容相等当意图相同；所谓稳定键是当前参数公式，不是一次确认的持久身份。创建每次先newId亦不能原意图重发。
- 证据：replay-recovery-source-probes.json、source-traces；正常跨状态/冲突/较新版本完整原生操作NOT_RUN，不能宣称均已测。
- 具体改法：持久化确认内容和独立action_key，重试不重算；授权后按actor+key查不可变回执、核payload冲突，再miss时做版本/状态守卫；返回同action_id和完整原结果，并单独读取最新任务。创建也走该协议。
- 验证：原键原版本、原键较新版本、后续动作后的旧查询不增事实/事件；同键异参拒绝；不同新键同内容形成两次合法动作；重启保留原键。

### D-M2-03 / P1 / 必修：失败仅回滚版本，创建和事件仍不一致（部分修复）

- 文件/行：`main.splash:213`、`:710`、`:735`、`:742`、`:770`、`:937`、`:949`、`:974`、`:1000`、`:1064`。
- 触发：接单mutation后令tmp写失败/主文件写失败；主文件成功后清tmp/读回/终结回执/事件写失败；创建正常路径；重启对账。
- 实际/预期：commit捕获返回、18处guard是改善；false时只恢复version，status/assignee/notes/evidence仍变。失败分支投影盘OPEN/无承接者，内存ACCEPTED/承接者A/version0。创建先成功事件、提示、saveTasks再commitBound(t,0)，t.version仍0，固定进入漂移；commitBound未被调用方判定。final之后才写事件，事件失败留下部分提交。boot只处理pending并按版本改标签，不恢复needs_verify。预期未提交回到权威事实、未知保持待核验并查询恢复，不显示虚假事实/成功。
- 根因/影响：部分内存回滚且多文件顺序写未形成恢复协议；已提交/未提交/未知仍混淆。
- 证据：replay-recovery-source-probes、source-traces。原生各写点注入BLOCKED，未假报其UI结果。
- 具体改法：统一创建与更新的提交协议；提交失败恢复完整任务快照或重新读取权威事实，不在unknown时盲回滚已提交版本。把动作标识、事件、回执和任务纳入可恢复的提交记录；pending/needs_verify按动作证据补全/确认，不只比较版本大小；所有抛错出口释放资源并保留输入。
- 验证：真实逐写点注入+杀进程重开，核任务/预约/回执/事件及UI；未提交无成功，已提交可查同原动作，合法后续版本不误判；创建获得正确final后重开可读。

### D-M2-04 / P1 / 必修：精确rid改善，但普通pending和原结果仍缺失（部分修复）

- 文件/行：`main.splash:625`、`:676`、`:695`、`:751`、`:770`、`:879`、`:890`。
- 触发：普通命令recordReceipt后中断；接单成功看final.result；rid缺失时终结；旧A/新B同command精确rid回归。
- 实际/预期：精确rid探针旧A不变、新B正确匹配，原“跨任务cmd覆盖”分支已消除。但recordReceipt仍不写status=pending和expected_version，boot看不到普通中断动作；_PENDING_RESULT在mutation前记录，接单final仍可能是OPEN；receiptFor仍把非final同key当hit；找不到rid竟新增标为final的orphan而非拒绝核验。预期不可变、可证明归属、完整pending元数据、真实after结果；未知不能当成功。
- 根因/影响：只修匹配算法，没修回执生命周期和结果语义，无法可靠对账。
- 证据：finalizer-source-probe、source-traces、replay-recovery-source-probes。
- 具体改法：精确rid找不到返回needs_verify，不生成成功兜底；pending记录稳定键、actor/task/参数/预期版本；final只存验证后的after事实和版本/action关联；查询按pending/rejected/final分支。
- 验证：两个任务/主体同cmd旧final字节不变；普通pending中断可恢复；final接单为ACCEPTED+正确承接者/版本；缺rid/拒绝/未知不显示已成功。

### D-M2-05 / P1 / 必修：假文件锁既双赢家又阻断后续动作（未闭合，修复回归）

- 文件/行：`main.splash:521`、`:527`、`:536`、`:600`、`:760`；r2静态审计的file_lock_helpers检查。
- 触发：第一次获取→释放→第二次获取；两个独立进程同隔离目录，屏障让两者exists均false后各写锁。
- 实际/预期：顺序结果true→释放写空→第二次false。两进程均acquired=true，exit0，最后写覆盖前者；这仅验证锁，不声称完整业务双提交已运行。预期后续合法动作可继续、竞争只有一持有者，崩溃后可安全恢复。
- 根因/影响：exists+write是TOCTOU，不是flock/原子排他创建；释放保留文件与获取exists逻辑矛盾。第一次成功或拒绝后即可永久挡住新命令，又无法保护实际竞争。
- 证据：lock-source-probes.json、probes.py，独立OS进程与实际盘字节；测试未添加生产mutex。
- 具体改法：使用宿主已经实证的原子CAS/排他锁或单权威执行队列；如果平台原语不可用应BLOCKED，不能继续模拟“flock风格”。覆盖所有返回/异常释放、所有权、防误释放、崩溃恢复。修掉空文件exists问题仍不足以解决双赢家。
- 验证：真实两个可信主体同事实源并发接单恰好一成功、一承接者、一成功事件；顺序第二次合法写正常；拒绝/hit/异常/杀进程后可恢复，无锁残留阻断。

### D-M2-06 / P1 / 必修：接入边界后遗漏命令白名单，旧合法按钮失效（部分修复）

- 文件/行：`main.splash:174`、`:209`、`:612`、`:1329`、`:1360`、togglePin见source-traces精确行号。
- 触发：授权任务上点击登记证据/隔离证据/置顶。在解决D-M2-05锁后仍可复现。
- 实际/预期：三入口已调用runCommandBound，但sourceOk没有addEvidence/quarantineEvidence/togglePin，最终return false，均source_state_invalid；原生按钮未运行。预期保留既有合法动作，经统一授权/版本/幂等提交。
- 根因/影响：只按文本检出“调用了边界”，未把新命令纳入状态协议，核心统一入口回归使原功能不可用。
- 证据：source-traces.sourceOk/addEvidence/quarantineEvidence/togglePin；作者静态19/19不查该可执行语义。
- 具体改法：按既有规则补齐显式命令schema和合法状态，非法状态仍拒绝；创建同样收敛。交付未激活的旧入口注明禁用，仍可调用者必须实际迁移。
- 验证：合法/非法身份×状态分别真实按钮执行，检查盘/回执/事件；同键重发不重复，不依赖绕过guard。外部旧Web/MCP/runner本轮NOT_RUN，不凭静态猜其已激活。

### D-M2-07 / P1 / 必修：boot备份阻断迁移，首换行冒充文本长度（未闭合）

- 文件/行：`main.splash:241`、`:290`、`:321`、`:406`、`:408`、`:425`、`:445`、`:466`。
- 触发：合法两条NDJSON无备份启动；已有备份重开；单测split多行；后续正常保存；带坏行输入。
- 实际/预期：loadJsonlLines首先备份并返回nil，migrateJsonlLegacy因bak已存在直接nil；磁盘探针证明历史未进入活跃内存，随后整数组保存只剩新条目。绕过备份时_textLenSafe只返回首换行位置+1，split最多首行；无换行返回1048576不是实际长度。parse坏行被跳过仍覆盖，违背注释“每行均有效”。预期旧历史全部保留可查、异常进入禁写恢复模式、备份可用于恢复。
- 根因/影响：helper存在/调用存在被当迁移成功，控制流互相挡路且长度算法错误；丢失活跃幂等历史，可重复旧成功动作。
- 证据：migration-source-probe.json（两行夹具、备份、后续保存读回、helper可达首行）、source快照。
- 具体改法：迁移在旧格式兜底前按完整合法输入执行；已有备份不应无条件禁迁移，应核来源/恢复状态。使用真实宿主已验证的完整文本原语，验证全条数/读回后才切换；坏行或任一步失败禁写历史并提供受控备份恢复。不要用index_of存在作为完成标准。
- 验证：旧数组/多行NDJSON/空/坏行/已有备份/备份与写入失败/中断重开；逐条旧回执和事件可查询，旧成功key重试不再写业务，新动作保留全部历史。

### 建议挂账

- **A-M2-01 / P2 / 建议**：提交真实r2清单/报告后修正“19/19即闭合”“宿主实测”“稳定键”“flock风格”等超过证据的声明；当前缺交接作为审查条件缺口，不另造业务P1。不因文风判FAIL。
- **A-M2-02 / P2 / 建议**：布局、全视口/中文输入/键盘继续保留既有挂账；只重验影响M2提交/输入恢复的部分，不做皮肤或下一模块功能。

## 判定

- 最终结论：**BLOCKED**，精确范围为本轮复审交接及原生运行条件。正式r1历史仍FAIL；现场未交接修复快照的七项原P1均未完整闭合，**不得据此PASS**。若按该快照正式交接，必须解决这些核心问题再原生复审。
- 必修：D-M2-01～07；按上文原编号修复，不扩模块。优先打通可信subject→正常创建/提交→下一次写→稳定键查询→未知恢复→真实单赢家竞争；只有名称、返回值或扫描通过不能关闭编号。
- 解阻：①交接冻结candidate_id、报告、完整内容哈希/差异和对应bundle digest；明确此次究竟r1还是r2。②提供可执行强制隔离、可清点回收宿主的本地测试环境，HOME/app-data/cache/log全部在项目runtime；不得为赶进度绕过隔离。③Abram确定业务身份来源/独立主体建立方式。身份来源是授权缺口，其余是实现/环境/交接问题无需新增Abram授权。
- G0-E延期不变；隔离离线签名已获授权，公开发布不是解阻前提，不请求公网/provider/计费变更。
- 先前模块：只定位M1基线和受影响命令/选择/输入/清理范围；真实回归BLOCKED，不修前序挂账、不把旧FAIL转PASS。
- 门禁：只更新GATES.json的M2审查字段和status，保存上一轮独立字段到review_history；candidate_id/base/实施字段及其他模块不改。ACCEPTANCE.json不改，本轮原生未跑不能覆盖历史后端结论。
- 是否允许下一模块：**否**。本轮不给下一模块入口，不执行M3。

STATUS=BLOCKED
NEEDS_ABRAM=yes
