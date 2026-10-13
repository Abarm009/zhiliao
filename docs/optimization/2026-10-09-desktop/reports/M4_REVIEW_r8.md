# M4 独立 Review r8

**最终结论：FAIL。** `M4-r7-worktree` 已在审查方独立 harness 六场运行中渲染部分工作台，但每场仍有新增保留字解析错误、登录行裁切以及未提交原文被清空；坏任务盘场继续出现作用域错误，没有可用恢复出口。真正跨上下文互斥仍未成立。非过期他人锁保留、未知戳保留、明确过期锁回收三项启动反例已独立通过；它们不能代替业务主链与并发验收。不允许进入下一模块。

- 审查者 / 日期：本会话唯一独立审查方，2026-10-12（Asia/Shanghai），两段式 `r2_2104`。无子代理、无业务代码修改。
- candidate_id：**M4-r7-worktree**；base_candidate_id=M4-r6-worktree。源码 HEAD=`8d730569546cb57310944bb299695134df773b9d`，存在未提交修改，本报告按内容快照审查。
- 当前源 `app/bundle/main.splash`：SHA-256=`5430cc10579426429505dcc83db5d37cdc2b90ddf947755e05373d79167a6931`，480580 字节、10018 行；base SHA=`37d1b1cabbea7d17e0b24ddb66aae4afe7ed5b54940df6b6b8d14a3c3d777b20`，477432 字节。交接 diff 与独立系统 diff 正文一致；第1段冻结源、当前工作树、安装/运行副本一致，写门禁前再核。
- 作者报告：`reports/M4_IMPLEMENTATION_r7.md`；清单：`runtime/optimization/2026-10-09/M4/r7/CANDIDATE.json`；diff：`M4/r7/evidence/r6-to-r7.diff`。版本根据用户交接的 build 证据/request/report/candidate 联合定位，不按 mtime 选版。
- 上一轮：`M4_REVIEW_r7.md` / M4-r6-worktree。仅核 B-M4-01、D-M4-03、D-M4-04 闭合与直接受影响回归；D01/D02/D05 先前已闭合源码子范围保留，不冒充完整原生 PASS。
- 前置：**M3=FAIL / M3-r7-worktree / M3_REVIEW_r8**，不存在已接受 PASS 的 M3 候选。按用户挂账裁决继续本模块复核，不修改 M3 门禁；其实际输入/登录依赖直接影响本模块，未伪造前置满足。
- 固定宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- bundle digest=`7ca55c1f52f6327d89164ccb10c7fcbc9db09f83acb6a436858101f6e151c8d0`。启动模型配置随运行包逐字节核对；本轮 needs_model=false，**真实模型调用0**，无402/欠费。
- 原生执行：外部驱动运行审查方请求，**01:52:05–01:53:27 +08:00**；六场 CLEAN / quit_http / rc0，无 ABORT。审查方没有自行启动 launcher、sandbox-exec、pgrep、--help、osascript、辅助功能或未授权自动化。
- 已读：第1段笔记列出的 AGENTS/CONTEXT/00/01/02/M4/04、上一轮缺陷、候选/作者证据/diff 与相关 T/U；第2段本冻结范围、六场全部 summary/result/profile/denials/host.log/MANIFEST、权威盘、六张请求 PNG 及相关源码。没有扩审其他模块。
- 已运行：第1段独立离线 catalog 验签、本地 install_staged/restart may_run，均rc0；驱动六场独立原生启动；审查方独立完整证据/摘要/盘对账。Python审计只核证据，不执行 Splash 业务。
- 未运行：真实可信登录，M3创建同一工单到M4开工，领域命令正反例，双上下文同盘并发、模型交错、提交点故障与同盘重开。尚未执行的业务命令记 NOT_RUN；已证白名单通道不覆盖的输入/并发/交错子项记 BLOCKED，原因见下。
- 路由/标题：当前工具未提供本主会话实际 Router 型号/路由或 createdAt/标题修改接口，未冒称已切指定主审型号或实际命名。历史线索仅用来定位，报告事实均以本项目当前证据验证。
- 置信度：候选/隔离/日志/截图/输入丢失/锁恢复事实 **高**；保留字根因 **高**；完整输入丢失、登录裁切和catch错误修复根因 **中**；未执行的业务/模型/真正并发结果 **未知**。

## 证据索引与独立核验

- **H**：`runtime/optimization/2026-10-09/M4/native-runs/review_r2_2104_REQUEST_review_r2_2104/`。
- **S**：`runtime/optimization/2026-10-09/M4/native/review_r2_2104/`。
- **R**：`M4/native/REQUEST_review_r2_2104.json`；**N**：`M4/native/REVIEW_NOTES_r2_2104.md`。
- **A**：S/`native-evidence-audit.json`，S/`audit_phase2.py`。复核命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/native/review_r2_2104/audit_phase2.py`，rc0；**127项证据一致性检查通过，不是127项业务测试通过**。
- S/`preparation-evidence.json`、`phase1-final-check.json`、`GATES.before-phase1.json`、`GATES.before-final.json` 保留准备与门禁历史；最终限定变更读回见 S/`final-write-verification.json`。

|独立场景|实际运行/日志|权威盘结果|判定|
|---|---|---|---|
|fresh_reporter_draft|业务480580字节view=true；parser错误host.log:43–45；登录行裁切|预存中文原文→空，panel draft→none；未出现锁；任务/回执/事件/测试账号不变|B01/U07 FAIL；新盘首次业务获取 NOT_RUN|
|wide_reporter_draft|同上错误43–45；请求1440×900但截图客户端仍相同裁切|原文清空；空锁保持；业务事实不变|B01/U07 FAIL；不声明宽布局通过|
|foreign_tech_lock|同上错误43–45；无to_int方法错误|`independent-foreign@4102444800000@947`逐字节保留；旧saved token清空；原文清空|D03非过期锁启动子项 PASS；入口恢复FAIL|
|unknown_manager_lock|同上错误43–45|`independent-foreign@not-a-number@948`逐字节保留；state.lock_state=unknown_kept并有解释；原文清空|D03未知戳保留启动子项 PASS；入口恢复FAIL|
|stale_reporter_lock|同上错误43–45|`independent-crashed@1@949`→空；state.lock_state=released、有原stamp解释；原文清空|D03明确过期回收启动子项 PASS；入口恢复FAIL|
|corrupt_manager_authority|parser错误43–45；另22条`variable _ not found in scope`（59–81区间）；初始化占位、登录裁切|截断tasks.json保持原字节；原文清空、status准备就绪；回执/事件/账号不变|B01/U07恢复出口FAIL；实际authority_unreadable命令拒绝NOT_RUN|

1. **MANIFEST.sha256 966项全部独立重算**：摘要错误0、缺文件0、重复0、未列入文件0；summary.request等于R；harness/template摘要与当前文件一致。初次审计对`.running`目录名作了错误假设，已改为枚举实际唯一内容目录，最终审计全通过，不将审计路径假设错误列业务缺陷。
2. 六场result的binary/profile摘要、模板渲染、cmd、env、完整seed清单、captures及摘要、write列表/数量、denial摘要、host_log_bytes/markers/tail逐项匹配。三份实际包（.bundles、实际`.running/<内容ID>`、hub-mirror artifact）**全部文件**与冻结签名包一致，480580字节业务eval不与809字节系统窗口混记。digest_seen_in_seed=true/host_log=false，仅seed marker不是加载证明。
3. 六张请求PNG存在且全部查看，均**2800×1716**；六张`.part.png`与各对应完整PNG逐字节相同。四场PNG摘要相同，stale场时钟不同，corrupt场保留初始化占位；均有部分工作台、登录输入/提交行裁切。`--size`1280×800/1440×900写入命令并不证明业务窗口响应了这些尺寸，故不宣称两个业务客户端尺寸通过。
4. 每场profile_probes.ok=true，应用profile探针rc0、外写和五类禁读探针均拒；pre/post_pgrep均NONE，pgid_members_after空，quit_http/rc0/CLEAN；library_scan为空，真实HOME的.octosense mtime前后不变。wide场运行中PGID快照另有短暂`(pmset)`，请求/cmd没有该动作、未记录子进程参数/用途，不能推断它做了业务操作；其余快照只列宿主，全部无回收残留。审查方仅读取这些外部执行结果，没有自己预检。
5. HOME、app-data、cache、config、tmp等路径均在各场新run目录，profile与模板/本地控制口一致；所有场景无模型代理。完整denial日志包含被拒的remote:*:443、系统Metal缓存、部分/dev/dtracehelper尝试；摘要独立重算一致。**这些是拒绝记录，不是成功外联/外写**。指定隔离/回收范围PASS。
6. files_written_count依次**124/124/124/124/125/124**，全列表无截断、全部路径在run内且存在。主要为包/系统应用/缓存、截图/日志/state；六场tasks/actions/events/隔离accounts均与seed同摘要。事实盘不变说明主链未执行，不证明权限/过期拒绝命令已成功。唯一有意业务锁变化是stale回收。
7. 六场预存未提交新原文均被清空，保存的actor均null、旧token空；这是启动恢复失败，**不是成功键入后丢失**。未装SESSION、未做可信登录，不能用三种角色hint代替三角色业务验收。
8. needs_model=false；model_proxy_stats字段均未产生（读取值None）、无proxy文件/模型endpoint覆盖env/MM_KEY，模型调用0，无账单错误。真实T35继续未执行。
9. 独立本地catalog/official install_staged/restart may_run及运行字节加载成立；不需公开发布。审查方生成私钥0，作者隔离anchor.key/working.key路径再次确认不存在；删除历史证据保留，不读私钥。没有读取/打印生产明文账号或provider密钥。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/证据一致|冻结候选、核所有运行副本/请求/seed/摘要|同候选同宿主|全部一致|PASS证据子项；M3前置未满足|A、S、GATES/M3_REVIEW_r8|
|真实UI主链|新隔离空盘从M3创建到接单/设备/预约确认/开工|真实填写确认、同任务/回执/事件|部分UI有，但parser错、登录裁切、输入恢复失败；主链未发生|**FAIL可用入口；主链NOT_RUN**|六图、host.log43–45、A.state|
|硬1权限/设备/服务|可信主体、技能/项目、伪造设备与服务空间正反例|合法成功，非法拒绝|无实际业务命令；保留源码守卫子范围|NOT_RUN|N、A任务/事件/回执不变|
|硬2预约|合法提议/确认，时区、过期、跨项目、改约拒绝|提议不直升，当前与待改约区分，错误可恢复|坏盘启动出口失败；预约命令未执行|NOT_RUN命令；错误出口FAIL归B01|corrupt图/log、D03源码|
|硬3真并发|两可信独立上下文同盘同步接单/重叠确认，相邻正例|唯一成功/无丢更新，相邻都成功|仍普通文件read-write-read；六场顺序新盘不具备双上下文调度|**D03 P1未闭合；并发通道BLOCKED**|main:2968/3006/3013/3342；R/schema|
|硬4开工与旧授权|合法设备/有效预约/时窗，改派后旧技工拒|守卫有效且UI明确缺口|未实际提交或开工|NOT_RUN|旧源码子范围、A|
|硬5首屏/真实输入/权威回读|三个可信角色可理解、可填可确认，事实/回执一致|各角色当前主动作/错误出口可用|hint不成会话，登录行裁切，原文清空；无角色操作|**FAIL入口/恢复；三角色命令NOT_RUN**|全部PNG、A.state|
|改派/改约撤销旧确认/AI|旧累计编辑集反例与当前epoch回归|旧绑定拒，重新绑定恢复，迟到回包拒|源码关闭子范围保留；无实际建议/改派/改约|SOURCE-CLOSED子范围；动态NOT_RUN/交错BLOCKED|main:2794/5272；N|
|D03锁启动恢复|future/NaN/stale三独立夹具，不更改运行盘|非过期/未知保留，过期可解释回收|三组各自符合；token启动重置|PASS限定启动子范围|A三组锁/state对账|
|隔离/回收|逐场profile/探针/env/denials/PGID核对|用户指定限制与回收|全部满足|PASS|A、六场result/profile/denials|

### 既有用例逐项结果

|用例|本轮结果与边界|
|---|---|
|T04|BLOCKED：当前白名单/新盘逐场harness没有两可信独立上下文共享隔离盘的同步接单调度；D03源缺口仍在，未实测双成功。|
|T05|NOT_RUN：技能/项目反例、经理分配事件未执行；actor hint不代验。|
|T06|NOT_RUN：改派旧预约取消、新承接者/ACCEPTED、旧技工拒未操作；D04源码子范围保留。|
|T07|NOT_RUN：编码/载荷等价、伪造/跨项目/归档设备命令；字符串helper已变且解析回归，需真实回归。|
|T08|NOT_RUN：合法服务空间与仅安装位置相同负例命令。|
|T09|NOT_RUN：无设备开工、IN_PROGRESS技工换设备拒、经理更正旧新值理由。|
|T10|NOT_RUN：提议不直升、合规报修人确认与非报修人拒。|
|T11|BLOCKED真正同盘同步调度；实际跨项目重叠/相邻预约确认NOT_RUN，顺序冷启动不代验。|
|T12|NOT_RUN：真实改约保留旧预约、新确认替代、拒新保旧；先前D02源码子范围保留。|
|T13|NOT_RUN：过期410/无定时器仍拒/客户端伪时间；锁时间测试不代替预约过期。|
|T14|NOT_RUN真实上海时区/UTC毫秒/具体日期/end<=start；已证type/key输入白名单通道不支持该宿主，子步骤BLOCKED。|
|T15|NOT_RUN版本409/刷新/保存表单/任意百分比拒；独立锁启动恢复子项PASS，不能代完整版本/失败恢复验收。|
|T31|NOT_RUN：取消释放预约/保历史/终态拒/新关联任务。|
|T35|旧累计编辑集源码反例SOURCE-CLOSED保留；真实建议生成期间改派/改约及迟到回包NOT_RUN；受控交错白名单通道BLOCKED。|
|U01|FAIL可用首屏入口：登录行裁切；三可信角色待我处理/下一处理人未形成（NOT_RUN角色链），不是本候选全部空白。|
|U03|NOT_RUN：三可信角色同工单事实/动作差异与不能自验；登录入口FAIL归B01，hint不证明权限。|
|U04|NOT_RUN实际预约/改约投影与冲突/过期命令；坏盘可恢复错误出口FAIL归B01。|
|U05|NOT_RUN真实设备选择、安装/服务与依据展示；不把当前无任务图称作规则FAIL。|
|U07|FAIL启动未提交输入恢复与坏盘出口；重复点击/响应丢失/版本冲突/离线命令NOT_RUN，提交点故障/同盘重开通道BLOCKED。|

BLOCKED仅用于**白名单动作确实不能覆盖**的输入、双上下文同步、受控故障/模型交错步骤。上一轮独立H/r1_2104/cold日志明确type/key/wait unknown；当前固定宿主与声明的test-action实现未变，本轮只用已支持launch-hub/capture，没有假装再次键入。没有以agent内rc71/rc3或“宿主无法启动”判BLOCKED；本轮宿主已经真实执行，无ABORT。可执行原生入口/恢复项实际失败明确记FAIL，尚未发生的业务动作记NOT_RUN。

## 缺陷与本模块修复清单

### B-M4-01 — P1 / 必修 / PARTIAL：部分工作台已渲染，但解析、登录入口与输入恢复仍失败

- **文件与行**：`app/bundle/main.splash:1257`、`:1259`、`:1262` 新helper使用保留字ok；`:8935`/`:8940` 登录固定高度布局；`:483–501` loadViewState、`:9974–9997` tick恢复/刷新、`:10004–10009` 初始化落盘。bad盘新增catch作用域关联`:9997`；VM坐标不等于源码行。
- **触发**：R六场新盘加载当前候选；仅launch/capture，没有点击清空、退出或手改运行盘。所有种子有新中文pending_input；corrupt场独立截断tasks.json。
- **实际 / 预期**：每场3条parser错误（首条ok reserved），业务view=true并出现部分UI；登录行下部裁切，保存原文清空，panel→none。corrupt另22条未绑定`_`作用域错，无清楚坏盘恢复出口。预期零解析错误、完整可操作登录/表单、原文恢复且保留、失败同屏可继续；真实M3→M4主链权威回读成立。
- **根因**：保留字ok作为变量导致解析恢复（高置信度）。其余恢复/裁切/刷新根因需要最小定位（中置信度），不能仅凭日志把整个输入丢失归因于ok。`catch _`未绑定错误使作者“异常隔离即不循环”主张未成立；坏任务盘初读`:986`也未提供受控错误状态。恢复读取、状态清理、首次保存需逐步证明。
- **影响**：核心登录/真实输入/处理入口与失败恢复被直接阻断；这是本模块必需的最小前序依赖，不要求修完M3全部挂账。
- **证据**：H六场host.log:43–45；corrupt:59–81区间22条作用域错；六张PNG；A各场state前后摘要/投影。旧r7“全空白”子范围已改善，本报告不沿用过时描述。
- **具体改法**：将新增局部名及引用改成非保留名并用固定宿主验证；按真实支持catch语法处理异常，不引用未绑定`_`；坏盘初始化明确禁写/保盘并可恢复；让登录输入及提交可见可点击；核loadViewState→恢复→选中兜底→saveState顺序，未提交原文不要被默认空值覆盖，恢复成功后才标记完成。
- **验证方式**：同候选六场零parser/新增作用域错、完整登录/错误出口、state原文保持；再真实填写M3工单，经接单、服务设备、提议/合规确认预约到开工，核同一task/版本/预约/回执/事件。禁止预置SCHEDULED/IN_PROGRESS或改系统时间补链。

### D-M4-03 — P1 / 必修 / PARTIAL：锁误清启动反例已闭合，原子命令边界仍缺

- **文件与行**：`main.splash:955`/`:969–981` boot恢复；`:2965–3019` token与普通读写获取；`:3034–3051`释放；`:3342–3358`提交前owner复核，`:3374`起实际写盘。spec授权前清理`:3063–3066`和坏盘拒`:3187–3195`改善保留。
- **本轮关闭子项**：future他人锁与NaN未知锁均原文保留；stamp=1旧锁合法回收并保存解释；旧持有token重置。三项动态**PASS限定boot范围**，旧to_int错误没有再出现。坏盘文件保持也是实际结果，但没有执行提交命令，不能说authority_unreadable返回已通过。
- **尚未闭合 / 触发反例**：两个独立上下文读取空锁后，A写并读回、检查并准备提交，B覆盖锁并读回，再各自写任务/预约，仍有可能双方执行。`:2965`采用actor@毫秒@本地ID_SEQ，未证明跨实例唯一；`:3342`核锁和任务写之间有竞争窗口。**本轮没有实际双成功业务并发证据**，这是对上一轮源缺口的确认，作者也明示HOST_PRIMITIVE_BLOCKED。
- **预期 / 影响**：同盘并发接单/重叠预约只一成功，相邻正常，最新授权/版本/冲突/提交一体串行，owner可靠。当前不能满足硬验收3，属于核心P1；token化只改善owner识别，没有变成原子互斥。
- **受影响回归**：`:2968`/`:3342`既有锁读取失败显式拒已加强，但没有区分文件首次不存在；新空Store首次合法命令是否被误挡必须核验。pinned std fs open失败会I/O trap；实际app适配/命令未执行，该子问题保留为待验证分支，**不伪装已实测必失败**。不能为过此回归固定预装锁掩盖新安装行为。
- **证据**：A三组lock/state前后字节；R逐场新盘；源码read/write/read与提交顺序；实施报告承认非原子边界；当前schema无双上下文同盘同步调度。
- **具体改法**：给出可核验原子获取或等效单一串行边界，覆盖权限/最新事实/版本/冲突及任务、预约、回执、事件提交；owner需跨实例唯一，获取/提交/释放核完整token。区分首次不存在与读取失败而守住fail-closed，不把存在性预检称原子。需宿主原语时提交最小复现及方案给驱动，不擅增服务。
- **验证方式**：保留future/NaN/stale冷启动回归，再真实新盘首次命令、权限拒后spec清空与下一命令、坏盘提交拒与恢复；两可信独立原生上下文同盘同步接单/跨项目同技工重叠确认仅一成功，相邻均成功，核唯一承接者/预约/成功事件回执、重开。普通Python文件并发或本六场顺序冷启动不能代验。

### D-M4-04 — SOURCE-CLOSED子范围保留 / 完整动态NOT_RUN

- **文件与行**：`:2794`失效开新epoch，`:4845–4857`显式编辑记录，`:5272–5286`恢复只消费本次集合。
- **原触发/预期**：失效前累计problem/space/category齐备，改派/改约后仅原文/联系人编辑，不得恢复旧proposal。当前代码仍不消费旧累计集合，原源码反例保持关闭；公共helper变化与parser回归使完整动态仍不可代签。
- **证据/根因修复**：N、冻结diff/源码；累计审计与本次编辑集合分离，旧绑定清理保留。没有新增可信证据要求再改该业务分支，因此不列为本轮剩余P1。
- **后续验证**：B01修复后实际旧编辑集空/部分/齐全×改派/改约，核无编辑/只原文/只联系人拒绝，当前三字段重填/新AI绑定可恢复，迟到回包拒；完整T35继续NOT_RUN/交错通道BLOCKED。

### 建议挂账

先前A-M4-01/02/03继续保留，不用来判FAIL。捕获尺寸与业务窗口尺寸关系、补可执行输入/受控交错通道和更精确取证由驱动/宿主侧明确；建议不掩盖当前实际P1。无需无关样式优化或下一模块改动。

## 判定与交接

- **最终结论：FAIL**，范围为冻结M4-r7-worktree在固定发行宿主及六场独立运行的旧缺陷复核；隔离/证据/本地安装PASS，部分工作台渲染改善，核心处理流尚未成立。
- **必修：B-M4-01、D-M4-03**，按上述具体改法与验证方式逐条修。D03三个boot子项不重复要求重写；D04源码关闭子范围保留。
- **阻塞/未测**：合法真实UI登录与填表通道、双上下文同盘同步、受控提交故障与模型交错缺已验证白名单能力；领域业务命令及主链NOT_RUN。需要驱动/宿主提供合规通道，不能绕过权限、注入SESSION或手改运行数据。没有等待Abram的新授权项。
- **前序回归**：本轮直接复测M2/M3共用锁/登录/输入入口，改善与失败如实记录；其他前序结论不改，M3仍FAIL，不能提升整条历史门禁。
- **门禁**：只更新`docs/optimization/2026-10-09-desktop/GATES.json`的M4审查字段与status=FAIL，review_report指本报告、review_candidate_id=M4-r7-worktree，保存此前审查字段/history，不动构建字段和其他模块。
- **原验收台账**：不改`docs/build-loop/ACCEPTANCE.json`；未继承旧后端PASS为原生PASS，本轮精确T/U结果写M4 review_acceptance并保留历史。
- **下一模块：不允许、不执行。** 留在M4修核心入口、保持输入与错误恢复、可靠命令串行边界，再以新候选独立复审。先跑harness冷启动看真实parser/log/图，不能仅提交静态26/26。

STATUS=FAIL
NEEDS_ABRAM=no
