# M2 独立 Review r3

最终结论：**FAIL**。正式候选 `M2-r3-worktree` 可定位，但原 D-M2-01～05、07 的核心问题未完整闭合；D-M2-06 的源状态白名单根因已修复，原生按钮回归仍 BLOCKED。本轮有独立的实际 Splash VM、权威磁盘及竞争失败证据，故不只报环境 BLOCKED，也不将作者的 17/17 扫描或 Python 契约结果签为 PASS。

- 审查者 / 日期：Codex 唯一审查方，2026-10-11，Asia/Shanghai；无子代理。现有接口不能确认主会话 Router/具体型号，不能声称已切换至 gpt-6.1-sol。没有可用的本会话 createdAt/改标题接口，未猜日期或宣称标题已设置。
- candidate_id / HEAD：`M2-r3-worktree`；实际 HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty worktree。通过 GATES→实施报告→candidate-manifest 的显式交接链定位，不按 mtime 选版。清单三项字节/哈希均匹配。
- 主源：298181 字节，SHA-256=`6704362fb6bbc91d0e634d7f6c5dce93629cddd32c519a0b8ec462dd4ab42358`。开始/结束输入快照核验及宿主/VM哈希见证据目录。候选清单只含 main、identities、账号安装表，不能当完整包/依赖清单。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r3.md`；账号子范围报告 `M2_ACCOUNTS_SOL_2026-10-10.md`；上一轮独立报告 `M2_REVIEW_r2.md`。
- 前置：M1 当前仍 **FAIL**、候选 `M1-r2-worktree`、报告 `M1_REVIEW_r2.md`，不存在已独立接受的 PASS 基线。本轮按 Abram 最新“前序挂账、仅阻断当前核心才必修”裁决继续审 M2；不修 M1、不把前置说成已通过。M2 的 base 在 GATES 为 accounts 候选、清单/报告为 r1，本轮通过 before-main 哈希和 source-main.diff 定位增量，见建议 A-M2-01。
- 已阅读：项目内 AGENTS、CONTEXT_M2、00/01/02、M2、04 模板、上一轮七项缺陷、r3交接/差异/作者证据和账号实施记录；仅追踪这些缺陷涉及的源码及受影响回归。未读取项目外记忆或技能，未读取/打印/改动 `runtime/identity/CREDENTIALS_FOR_ABRAM.md`；未读取 MiniMax 密钥，未调用模型。
- 实际环境：macOS；项目内现成 `runtime/identity/evidence/vm/target/release/identity-vm-probe`，执行从本候选提取的**原函数**和项目内宿主 jailed fs 实现。它是无窗口局部 VM，**不是发行 launcher，也不是桌面端到端**。
- 隔离：所有新探针、HOME/TMP/cache/data/日志/合成账号和事实盘在 `runtime/optimization/2026-10-09/M2/review-r3/`。只写报告、M2审查字段及测试证据；原业务数据与真实账号未修改。未 reset/stash、未发消息/联网/push/issue/publish/listing/部署。
- 宿主：独立 `sandbox-exec … true` rc71，`sandbox_apply: Operation not permitted`；`pgrep` rc3，`Cannot get process list`。无法确保 launcher 的所有写入和清理满足硬约束，**未启动 launcher、未调用 --help、没有新建宿主窗口**。既有窗口残留情况 UNKNOWN，未杀他人进程。真实 UI、launcher会话、真实双主体接单、杀宿主重开均 BLOCKED。
- 置信度：固定字节、确定调用顺序、实际 VM/磁盘结果与双进程文件锁反例 **高**；发行 launcher 的解析/预算/UI/授权和完整恢复 **未知**。不将本地 VM 方法错误直接等同发行二进制已复现同一错误。

证据根：`runtime/optimization/2026-10-09/M2/review-r3/`。下文 `results/…`、`sandbox/…` 均相对于此目录。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与前置|读显式交接链、逐文件 SHA、实际 HEAD、M1门禁|固定候选；如实定位前置|r3三文件匹配；M1 FAIL挂账；全包未准入|候选定位 PASS；前置未通过|candidate-check、start/end-snapshot、gates-before|
|按钮到事实源|追踪 main_action_btn→runAction→acceptTask→runCommandBound→runCommand→recordReceipt→mutation→commit→commitBound→logEvent|可靠统一边界|链存在，但键重算、回执旧结果、提交后独立事件写、未知恢复缺口仍在|FAIL源码/局部 VM；真实按钮 BLOCKED|main.splash:5850、4899、3330、1906、3288、2220、2293、2072、644|
|硬1 重试/冲突/新意图/历史查询|执行原 key/finder/bound；保持旧key查询 version5；复用按钮生成键方式|同 action_id 和原结果，跨状态/新版本可回查；同键异参拒绝|显式旧键命中、异参拒绝、version5历史命中成立；按钮版本变化重生key而拒绝；未返回完整原结果|局部改善；整体 FAIL D02/D04|focused_normal_replay、history_newer_version、focused_key_formula|
|硬2 身份和并发|两个独立VM进程用另造凭据登录、切视角、盘上撤权；两个独立OS进程同锁文件真实竞争|主体不借位；撤权拒绝；并发单赢家|合成登录/动态授权通过；原生登录未接入；竞争两个进程均 acquired=true|身份局部 PASS；核心 FAIL/BLOCKED D01/D05|focused_auth_r-A/r-B、race-lock、preflight|
|硬3 失败一致性|tmp目标设目录、事件目标设目录；实际原 commitBound/fs 写读；追踪 commit快照位置|无假成功及业务部分提交|tmp失败盘未提交；事件失败时任务 ACCEPTED/version1、final已落、无事件；commit快照在caller mutation之后|FAIL D03/D04|focused_tmp_write_failure、focused_event_write_failure、focused_rollback_snapshot|
|硬4 未知结果对账|原 commitBound 的读回依赖返回nil；独立查盘；原恢复函数处理 needs_verify/pending|待核验可恢复原动作；不重写|盘已提交且 needs_verify；恢复返回0不处理；pending按版本变成superseded；缺rid仍造final|FAIL D03/D04|focused_readback_reconcile、pending_and_orphan、pending_replay_lock|
|硬5 迁移和桌面恢复|合法2行NDJSON按真实load→migrate次序执行；实际split；核桌面条件|历史活跃可查且错误禁写；输入/身份重开稳定|先备份后迁移直接nil，未加载历史；本地VM index_of不存在；原生重开不可跑|FAIL D07；桌面 BLOCKED|boot_migration、split_actual、preflight|
|受影响旧入口/白名单|实际 sourceOk 六状态×三个原遗漏命令，核其边界接线|合法动作放行、非法状态拒绝|add/quarantine在ACCEPTED等允许、OPEN/COMPLETED拒绝；pin任意状态允许|白名单根因 PASS；完整回归 BLOCKED|source_ok_regression；main.splash:615、4789、4936|
|精确rid归属|旧A/新B只终结B|旧A不变、B final|原函数确实精确更新B；缺rid另造final仍不正确|匹配分支局部成立；D04未闭合|finalizer_rid_regression、pending_and_orphan|
|当前包/本地安装路线|项目内 hub check 当前完整 app/bundle，allow-unsigned|当前digest准入、再离线安装|rc1 REFUSED，实际digest不符manifest；含禁止扩展/资源引用项；不签拒收包|当前包/安装 BLOCKED；历史路线保留|current-bundle-check.log|

运行形态说明：可靠性探针使用原生产函数、真实 jailed fs、**明确的合成授权桩**；为模拟边界后的领域变更，测试脚本在 `runCommandBound` 允许后改夹具对象并调用原 `commitBound`。这不是假报按钮成功链。读回失败是对读回依赖的注入；原 `commit()` 失败探针另用失败返回桩。锁反例是原文件锁算法的 Python 分支翻译，两个实际 OS 进程同盘运行；它没有证明原生两个业务主体已接单。身份探针则使用实际 KDF、会话和授权函数，以两个独立新测试凭据进程验证，不读取真实凭据。

初轮完整局部探针因本地 VM 对 `catch _` / 保留名 `ok` 报错而失败，日志全部保留，**不能用其 rc0/输出文件宣称完整通过**。后续聚焦探针移除未执行的业务/commit函数，只运行未改写的实际边界原函数；normal、tmp、event、readback、key、历史、pending及两主体授权取得明确读回。精确rid旧探针带未执行commit的解析错误，只计确证的分支输出，不计整程序PASS。全源独立解析为16个错误，与账号实施记录数量一致；本轮不扩修全源其他模块。

### 相关既有用例逐项范围

|用例|本轮状态|具体范围|
|---|---|---|
|G0-B|BLOCKED原生；D01未闭合|五真实账号表已存在；两合成主体实际VM登录/撤权成立，正式桌面仍无可登录通道。|
|G0-C|FAIL局部存储/竞争；原生BLOCKED|D03/04/05：部分提交、原结果错、双赢家。|
|T02|NOT_RUN完整创建；源码FAIL|createDraftFromPanel每次先newId，先成功提示/直接saveTasks，再commitBound；D02/03。|
|T04|FAIL文件锁竞争；完整接单BLOCKED|两独立OS进程在同一锁文件竞争，非顺序两次调用；真实A/B业务接单未跑。|
|T15|NOT_RUN完整用例|源码有磁盘版本拒绝；原生冲突刷新/输入保留未跑，不以guard名称判PASS。|
|T16|FAIL按钮重试协议；显式原键局部成立|旧键命中不增版本，按钮重算v1键后拒绝；回执结果OPEN。|
|T17|NOT_RUN|断线/重连全量回读未运行，不修下一模块。|
|T18|BLOCKED完整读权限|动态会话授权合成探针成立；列表/搜索/事件/附件全通道独立核验未跑。|
|T22|FAIL局部注入；原生逐写点BLOCKED|实际事件写异常留下任务+final，无事件；完整逐写点/杀进程重开未跑。|
|T24|NOT_RUN完整旧入口；白名单根因修复|三按钮接入与sourceOk局部回归成立；旧Web/MCP/runner未运行，不能声称禁止绕过已验收。|
|T29|NOT_RUN原生授权周期|合成撤权下一次命令拒绝；宿主grant关闭/退出/到期/共享卡未跑。|
|T32|NOT_RUN|配对码/poll_secret/Web审批/token边界未跑。|
|T37|FAIL局部恢复|needs_verify恢复0、final原结果错、缺rid造final；显式旧键较新版本查询局部成立。|
|U03|BLOCKED|两合成VM非借位成立，真实三个主体桌面事实一致/自验禁止未跑。|
|U07|BLOCKED桌面；核心源码FAIL|键重算与失败内存污染仍在；真实重复点击/超时/重启输入未跑。|
|U08|NOT_RUN桌面|部分STATE拒绝/待核验文案可观察，完整错误出口没有UI实测。|
|T28|BLOCKED|当前完整包REFUSED；launcher操作→权威回读→重开未跑；旧Store PASS不替代。|

G0-E：**延期缺口（Abram 已裁决，M3 到期）**。身份来源与 MiniMax provider 的选择均已裁决，本轮不再列 NEEDS_ABRAM，不调用模型。本轮没有生成私钥，删除证据为“不适用：未生成”，不虚构删除操作。历史本地 catalog/install_staged 已证明路线在历史digest可行；当前包检查失败，不等于本地安装路线被证明不可行，也不需要公开发布授权。

## 缺陷：只复核上一轮编号

所有行号对应本轮固定的 `app/bundle/main.splash`；每项核心未闭合为 **P1 / 必修**，建议不影响判定。

### D-M2-01 — P1 / 必修 / 部分闭合：可信会话实现改善，原生登录仍无入口

- 文件/行：main.splash:388、406、430、5603、5604、6600；账号实施报告“防冒用和失败关闭”“尚未闭合”。
- 触发：正常打开候选后点击“登录待接入”；期望经五个已建立账号的安全登录获得业务主体并执行命令。
- 实际/预期：按钮只设置 `BLOCKED：宿主安全登录服务未接通`；源码没有UI调用authBegin，SESSION初始为空，业务写入关闭。账号注册表刷新、getMe无USERS兜底、切视角不改主体已实质改善，合成两进程登录/撤权成功；正式用户仍不能操作。
- 根因/影响：账号与认证函数没有接到选定宿主安全凭据/登录入口。五账号建立不是原生业务登录完成，直接阻断核心正常链。
- 证据：两个 focused_auth 的 observed.json；上述UI/call-site源码；preflight.json。真实桌面触发 BLOCKED，不能假报点击实测。
- 具体改法：在已裁决的账号来源上接入实际宿主安全登录/可信本地会话适配；保持每写/每查刷新权限，不在普通文本框收集秘密。按实际发行策略解决KDF预算/可运行性，不降低哈希配置掩盖问题。
- 验证：项目内隔离宿主中A/B独立登录、正常一次业务写/读；切视角不能冒用；撤权/到期/移项目/退出下一次写和旧动作查询拒绝。凭据只另造，不读真实凭据文件。

### D-M2-02 — P1 / 必修 / 部分闭合：键查询修复，但真实动作键仍随版本/编辑重算

- 文件/行：main.splash:1916、1917、1921、2238、3277、3278、3337、3338、3175。
- 触发：接单v0完成后响应丢失，再走同按钮的v1键生成；恢复旧键查询；同键改payload；创建重复确认。
- 实际/预期：显式保留原键的final查询、异参冲突、version5历史查询成立。按钮重新用version/payload拼键，变成新键；实际VM边界返回 `source_state_invalid：acceptTask 不允许从 ACCEPTED`，而非原结果。函数只有return拼串，无确认意图持久化；创建先newId让task/key均新生。重放分支只写STATE文本并return false，没有完整原结果返回。
- 根因/影响：查询索引修了，意图身份未持久化。响应丢失后的正常用户重试不能可靠对账；同意图编辑自动换键规避冲突，创建重试可能重复工单。
- 证据：focused_normal_replay、focused_key_formula、history_newer_version的磁盘observed及原函数；作者静态检查只检查fingerprint/函数名，不查持久意图。
- 具体改法：人工确认时生成并保存独立action_key及不可变确认内容；按钮重试/重开沿用，编辑时明确重新确认；边界授权后按actor+key查原回执、核指纹，miss才验新状态/版本；返回原action_id+原结果，最新任务另读。创建亦采用同协议。
- 验证：原键原版本、跨状态、后续version5、重启、同键异参、独立新键同payload；任务/回执/事件计数不重复，完整原结果一致。

### D-M2-03 — P1 / 必修 / 未闭合：所谓完整回滚快照仍在mutation之后，事件与创建仍部分提交

- 文件/行：main.splash:3340～3344（范围说明）、2299、2300、2313、2072、2094、2125、644、3186、3188、3189。精确触点为3340、2300、644、3188。
- 触发：caller已改assignee/status后commit失败；接单主文件和final落盘后令events.jsonl写失败；创建commitBound前中断。
- 实际/预期：commit里的snapshot在caller变更之后，恢复仍是ACCEPTED/技工，只恢复旧version；失败探针盘为OPEN/v0，内存ACCEPTED/v0。该探针还存在本地VM保留名ok解析错误，不能据此宣称原生完整执行，但源码顺序明确。更强实证：原commitBound成功后原logEvent因真实目录冲突异常，盘已ACCEPTED/v1且final已落，事件文件未形成。创建仍先“草稿已创建”+saveTasks，再进入commitBound。期望失败不制造假事实，已提交可恢复补齐关联事实。
- 根因/影响：把字段恢复当事务；跨任务/回执/事件未建立可恢复提交记录；创建仍绕开完整命令流程。
- 证据：focused_tmp_write_failure、focused_rollback_snapshot及日志、focused_event_write_failure实际盘和write failed日志；创建源码。
- 具体改法：在mutation前取权威完整快照或失败时重新读取权威事实；明确区分未提交与已提交未知。使用包含动作标识、before/after、事件/回执的可恢复提交协议，并覆盖异常资源释放；创建收敛同一边界，不提前成功提示或直接主文件写。
- 验证：每个任务/回执/事件写点异常和进程中断；查盘、回执、事件、UI；未提交无成功，已提交能对账补齐，重试不重做。

### D-M2-04 — P1 / 必修 / 部分闭合：pending元数据已补，final结果与未知恢复仍错

- 文件/行：main.splash:2220、2230、1987、1989、2303、2038、2059、2109、2114、2133、2139、2149、2179、2209。
- 触发：接单正常commit；提交成功后读回nil；pending中断后task.version变大；缺rid终结；needs_verify同key重试。
- 实际/预期：pending+expected_version、精确rid匹配是改善。但正常盘ACCEPTED/v1，final.result仍 `{status:OPEN,task_id:…}`，缺after版本/承接者；读回失败盘已ACCEPTED，needs_verify恢复返回0；pending不核动作而改superseded；缺rid产生新final；receiptFor不区分状态，将needs_verify当“幂等命中”文本。启动boot对账还在SESSION为空时直接退出，登录后无重新调用。期望终态结果来自核实after事实，未知不能当成功且能恢复。
- 根因/影响：生命周期数据补齐但结果仍取mutation前 `_PENDING_RESULT`，恢复只按版本贴标签，没有动作关联和提交证明。
- 证据：focused_normal_replay、focused_readback_reconcile、pending_and_orphan、pending_replay_lock；finalizer_rid_regression仅证明旧A未被改。
- 具体改法：final只存核验after对象及前后版本、actor/task/key/action关联；缺rid返回needs_verify而非新造final；显式处理pending/rejected/needs_verify/final，并从持久动作/提交记录恢复，不因较新版本覆盖原结论。有效会话恢复后执行对账，授权先行。
- 验证：正常接单final=ACCEPTED+正确actor/version；响应丢失/读回失败/较新版本恢复同action_id；缺rid和未知不报成功；旧final不变。

### D-M2-05 — P1 / 必修 / 未闭合：状态标签不是互斥，真实竞争双赢家，未知重放还漏释放

- 文件/行：main.splash:1874、1882、1889、1897、1900、1989、1990、3296、3300。
- 触发：A/B均读空锁；A先写并读回成功但不释放，B随后写并读回成功；needs_verify原键重放落runCommand的hit出口；持锁崩溃后重开。
- 实际/预期：两个OS进程同盘均 acquired=true、exit0，最终盘锁属于B，A尚未释放；作者顺序CAS测试无法覆盖该交错。原VM pending重放实际先取锁后return false，盘锁非空，第二次acquire=false；receiptFor将needs_verify提示幂等命中。非空锁也没有崩溃恢复。期望真正单赢家、所有hit/reject/异常路径释放、重开安全恢复。
- 根因/影响：read→write→read不是原子CAS；release不验owner；command_allowed=false出口漏释放。直接违反可靠执行/并发核心，不能降成建议或仅等待官方的说明。
- 证据：race-lock.json含不同pid/共享路径及实盘；last-vm-probes.json/pending_replay_lock。前者是锁算法分支翻译、后者实际VM；完整原生业务并发BLOCKED。
- 具体改法：使用已实证的宿主原子锁/CAS或一个权威命令执行队列；不可用则保持BLOCKED能力项并交接最小复现。绑定所有权、释放与恢复，所有返回/异常走清理；禁止仅加m2_lock_state声称解决并发。
- 验证：可信A/B同事实源并发接单仅一成功/一事件/一承接者；连续合法写、拒绝/hit/异常/杀进程重开均可继续且不误解锁。

### D-M2-06 — 原P1 / 根因已修复；闭环待测，不单独新增P1

- 文件/行：main.splash:615、623、631、4789、4803、4816、4936。
- 触发/实际：sourceOk六状态×addEvidence/quarantineEvidence/togglePin的实际VM矩阵符合显式白名单；三个旧入口仍经runCommandBound。上一轮“合法动作全部source_state_invalid”的具体根因已关闭。
- 尚未验证：真实按钮、真实附件及统一提交后的盘/事件，受D01/03/05及宿主隔离阻断。本轮不扩审M5、不独立重判收藏version规则；需要的跨模块回归保留挂账。
- 后续验证：核心边界修好后用合法/非法身份与状态真实点击、同键重发、读取任务/回执/事件；无须为本条再改白名单来刷测试。
- 证据：source_ok_regression.splash/.log/sandbox observed.json。

### D-M2-07 — P1 / 必修 / 未闭合：改split函数没有改变boot备份阻断迁移

- 文件/行：main.splash:652、667、688、729、733、749、811、813、855、865、833、843。
- 触发：副本含合法两条NDJSON，无旧备份；按loadJsonlLines→migrateJsonlLegacy的真实启动顺序；独立split。
- 实际/预期：实际VM load创建legacy.bak、loaded=nil，后续migrated=nil，活跃历史未加载，两条仍只在原文件/备份。本地VM原split报 `method index_of not found on string`；不能将Python的find/slice成功当宿主方法验证。遇坏行仍过滤再覆盖，历史写入未被全局禁用。期望合法历史全部保留可查询，坏格式/失败禁写恢复而非空成功。
- 根因/影响：旧备份兜底仍早于迁移，bak存在直接跳过；平台原语没有实证；会丢失活跃幂等历史，后续整数组保存可覆盖旧日志。
- 证据：boot_migration实际observed/原文件/备份、split_actual.log；作者test_6直接调用Python迁移而未跑生产boot顺序。boot probe带解析警告，明确只计磁盘分支结果，不计完整程序PASS。
- 具体改法：迁移先于旧格式备份兜底；已有备份核来源/恢复状态，不无条件跳过。采用实际目标宿主可用文本原语，全条核验、备份/读回成功才切换。任何坏行/失败进入禁止覆盖历史的恢复状态；不能把不支持的index_of/slice当已实测。
- 验证：数组、NDJSON、已有备份、空/坏行、备份写失败/主写失败/中断重开；逐条历史可查，旧key不重写，新动作不丢旧历史。

### 建议挂账

- A-M2-01 / P2 / 建议：统一GATES/报告/清单的base_candidate_id、提供完整包与依赖哈希；修正“持久化键”“caller mutate前快照”“六项闭合”等超过证据的措辞。当前主源码可定位，不因此额外判FAIL；包准入REFUSED作为运行条件缺口单列。
- A-M2-02 / P2 / 建议：继续保留既有布局/输入/键盘挂账；仅在M2真实提交/恢复可跑后做受影响回归，不做皮肤或下一模块。

## 判定

- 最终结论：**FAIL**，范围为已交接 `M2-r3-worktree` 的原七项缺陷复审及受影响回归。D01/02/03/04/05/07仍有真正阻断本模块核心的P1；D06白名单根因修复但端到端待测。核心尚未真实跑通，不能按“完成比完美重要”把核心缺口降为建议。
- 必修清单：接通可信原生登录；保存一次确认的稳定动作；用真实after生成不可变回执；提交/事件/未知结果能对账恢复；真实互斥且异常释放；修正启动迁移与失败禁写。按上述原编号修，不扩模块。
- 运行解阻：提供可后台启动并可强制限定HOME/app-data/cache/log到项目隔离目录的宿主通道，以及可确认立即关闭和无残留的进程/UI核验；当前sandbox rc71/pgrep rc3不允许绕过。交接当前可准入包与digest，离线catalog/install_staged后核安装字节，不复用历史digest的PASS。既有账号来源/离线签名授权足够，不要求Abram新增授权。
- 未测：原生真实按钮、全套逐写点/杀进程重开/独立三主体、旧Web/MCP/runner及grant/pairing周期、全UI恢复；逐项见上表。当前全源16解析错误/包REFUSED分别记录，不把局部VM当launcher。
- 受影响先前模块：核M1状态和命令/身份/选择/输入/清理依赖；原生回归BLOCKED。M0/M1仍保留挂账，本轮未改其字段或结论。
- 门禁/台账：只更新GATES.json的M2审查字段与status；先归档本轮开始的审查字段到review_history，保留来源。ACCEPTANCE.json未修改，历史后端/模块结论不转签原生PASS。
- 是否允许下一模块：**否**。留在M2修复/解阻；不提供下一模块入口，不执行M3。

STATUS=FAIL
NEEDS_ABRAM=no
