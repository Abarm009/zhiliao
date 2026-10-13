# M2 独立 Review r4

最终结论：**FAIL**。被审候选为 `M2-r4-worktree`。只复核上一轮 D-M2-01～07 和受影响回归；D-M2-06 白名单根因继续闭合，D-M2-04 正常 final 结果已改善，但 D01/02/03/04/05/07 仍有核心或凭据安全 P1。未修业务代码，未进入下一模块。

- 审查者 / 日期：Codex 唯一审查方，2026-10-11（Asia/Shanghai），无子代理。当前工具不能核实或切换主会话到指定 gpt-6.1-sol Router；不能声称该路由已满足。当前无本会话 createdAt / 改标题工具，未猜日期或宣称已改标题。
- 候选 / HEAD：GATES→`M2_IMPLEMENTATION_r4.md`→r4 candidate-manifest 明确交接 `M2-r4-worktree`，base=`M2-r3-worktree`。HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty。未按 mtime 选版。
- 精确审查字节：`app/bundle/main.splash` 303143 字节，**实际 SHA-256=`4796cfe454e97f5b9b01ae3b4229f33fb3161792e27c20e399c80ba84657ce79`**，与 r4/after-main.splash 完全相同。清单中所谓 after_sha256 的 `9f0daa10707d8932935a381e1b0a07d9` 实为 MD5。开始/结束摘要一致，详见 start/end-snapshot。
- 基线差异缺口：r4/before-main.splash 实际为 46640 字节、SHA-256=`9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72`，**不是**声明的 r3 298181 字节 / `6704362f…42358`；提交 source-main.diff 不能证明声称的 r3→r4 增量。当前候选可由保存副本锁定，此材料问题列 A-M2-01 建议，不单独制造 P1，也不声称基线增量已核实。
- 前置：M1 仍为 FAIL，候选 `M1-r2-worktree` / `M1_REVIEW_r2.md`；不存在已接受的 M1 PASS 基线。按 Abram 最新前序挂账裁决继续本模块复审，不修改 M0/M1 门禁、不把前置写为 PASS。
- 已阅读范围：项目 AGENTS、CONTEXT_M2、00/01/02、M2、04 模板、M2_REVIEW_r3 原编号缺陷、r4 实施报告/候选/作者 evidence，以及原缺陷涉及的源码。遵守修复轮精简阅读，不从头扩审全部模块。真实账号表、安装映射、host-data 只读核元数据；五主体存在，两份账号表摘要一致、权限 0400。未读取 `CREDENTIALS_FOR_ABRAM.md`；未读取 MiniMax 密钥、未请求模型。
- 环境 / 宿主：macOS；目标 launcher 为指定 M0/r3/host/app-extracted/OctoSense.app，二进制摘要见 start-snapshot。执行的是项目现成 `identity-vm-probe`（SHA-256=`204b5892fad7fcfc0cb634a638e8067e73760018bbcb014ced2f3547ea2cbede`）与原 Splash 函数、真实 jailed fs。**无窗口局部 VM 不等于发行 launcher / 桌面端到端**。
- 隔离：所有新脚本、HOME/TMP/XDG cache/data、合成凭据、磁盘事实及日志在 `runtime/optimization/2026-10-09/M2/review-r4/`。未改原业务数据/真实账号，未 reset/stash，未联网、发消息、push、issue、publish、listing、部署。未生成离线私钥，因此无本轮私钥需要删除。
- 原生条件：独立 sandbox-exec preflight rc71（`sandbox_apply: Operation not permitted`）；pgrep rc3（`Cannot get process list`）。不能强制保证 launcher 全部写入隔离及窗口/进程回收，**未启动 launcher、未使用 --help、未创建宿主窗口**。既有窗口残留 UNKNOWN，未杀他人进程。真实 UI、原生双主体业务竞争、杀宿主重开均 BLOCKED。
- 当前包：独立 hub check app/bundle --allow-unsigned rc1 / REFUSED，实际 digest=`dabbf172145491b3fccf19cfac21f6c0dfdef108dee6f73d6ff140f0438312ad`，manifest 仍声明旧 digest；还拒收 .DS_Store/log/bak 与资源扫描项。未签名拒收包、未安装拒收包。历史本地 catalog/install_staged 成功保留历史范围，不能转签本 digest。当前包准入及安装未完成；未证明本地路线不可行，NEEDS_ABRAM=no。
- 置信度：当前字节、确定调用顺序、实际 VM/磁盘反例与双进程锁反例 **高**；原生 UI、发行宿主指令预算/方法集、完整恢复 **未知**。

证据根：`runtime/optimization/2026-10-09/M2/review-r4/`。下文 results/probes/sandbox 均相对此目录；脚本和失败日志保留，不把退出码或 Python 等价的 PASS 当原生通过。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、前置与一致性|显式交接链、真实 SHA、保存副本、HEAD、前后快照|审查对象固定；如实核前置|当前 main=保存 r4；MD5冒充SHA、before不是r3；M1 FAIL挂账|对象定位成立；基线增量未证实|candidate-check、start/end-snapshot、gates-before|
|真实按钮到事实源|追踪 main_action_btn:5955→runAction:4987→acceptTask:3418→键:3355→bound:1945→runCommand:3376→receipt:2268→mutation→commit:2341→commitBound:2111→logEvent:677|一次确认、可靠提交、原结果与UI一致|键依赖未验证 index_of；任务/final提交后事件单独写；查询仅文本，不返回原结果|源码/局部FAIL；真实按钮BLOCKED|原函数、聚焦探针及磁盘|
|硬1 重放与冲突|显式原key正常重试、跨状态/版本、改payload、任务version5查询；另执行按钮键原函数|同action_id+原结果；异参拒绝；新意图可独立执行|显式key命中、冲突拒绝、v5历史命中成立；按钮key方法在本地VM报错；内容编辑换key、同内容新意图不能区分|整体FAIL D02；局部命中成立|retry_normal_replay、history_newer_version、retry_key_actual|
|硬2 身份/权限与竞争|两个独立VM进程用另造token登录，切视角，盘上撤权；两个OS进程竞争共享锁|可信会话不冒用，撤权拒绝；只一赢家|合成A/B真实KDF登录、切视角不换主体、撤权失效成立；共享锁双赢家；UI口令进STATE可落盘|身份局部成立；FAIL D01/D05；原生BLOCKED|auth-probes、focused_login_*、secret_persistence、race-lock|
|硬3 部分提交和写失败|tmp/events目标设目录，执行原commitBound、logEvent，独立查盘|无假成功/部分提交，恢复补齐或一致回滚|tmp失败盘OPEN/v0；事件失败盘ACCEPTED/v1+final，事件无文件；创建仍提前成功/saveTasks|FAIL D03/D04|retry_tmp_write_failure、retry_event_write_failure；创建源码|
|硬4 未知结果|原commitBound读回依赖返回nil，查实际tasks盘；原bootReconcilePending；needs_verify原key重放、缺rid终结|待核验能对账、不得重复或造final|盘已ACCEPTED/v1；needs_verify恢复0；重放“幂等命中”且锁未释放；缺rid生成新final|FAIL D04/D05|retry_readback_reconcile、pending_replay_lock、finalizer_orphan|
|硬5 迁移/重开|核启动迁移新顺序、实际split；核坏行/已有bak失败路径；桌面条件预检|历史完整、失败禁写、重开输入/身份稳定|迁移顺序已调整；已有bak直接跳过、坏行仍过滤；split原函数本地VM index_of报错；桌面不可安全启动|FAIL D07；真实桌面BLOCKED|migration_split_actual、源码850/875；preflight|
|原D06及旧入口回归|实际sourceOk六状态×三命令；追踪三个入口经bound|合法状态允许、非法状态拒绝、不可绕过|白名单矩阵继续成立；外部旧Web/MCP/runner本轮未执行|D06根因闭合；完整旧入口NOT_RUN|source_ok_regression、入口源码|
|包/本地安装|当前完整bundle独立check|当前digest准入后离线install_staged|REFUSED；未签/未安装|BLOCKED当前包|preflight、bundle.log|

探针边界：可靠性测试明确使用合成授权桩，只执行原边界/提交/回执/事件函数；允许后由夹具模拟领域 mutation，故不是按钮成功链。读回失败对依赖注入，真实磁盘写入未伪造。锁竞争是**原 read→write→read 分支的 Python 翻译**，两个真实独立 OS 进程同路径合法交错，不是两个原生用户接单证明。登录探针是实际原 crypto/auth/m2_login_begin 与两个合成token、真实账号表格式；其动态回归最终聚焦 identityActive、切视角和盘上撤权，不将它说成完整命令授权矩阵。

首批探针因夹具未提供新STATE字段失败，日志保留；后续补齐合成夹具字段、可靠性探针使用显式key后获得上述事实。按钮key和迁移split的真实方法错误仍保留。前两轮登录探针登录后因依赖捕获缺失报错，不计PASS；最终 focused_login_r-A/r-B rc0，各约3.8秒，才计局部登录/撤权成立。200000指令限制探针超限，仅证明该预算下不可运行，**不推断发行 launcher 本轮实际预算**。

### 相关既有用例逐项复核

|用例|本轮状态|实际范围与限制|
|---|---|---|
|G0-B|BLOCKED原生；FAIL D01安全|五真实账号及映射已建立；两合成登录成立；原生登录与安全凭据处理未通过。|
|G0-C|FAIL|D03/04/05磁盘部分提交、未知不恢复、竞争双赢家。|
|T02|NOT_RUN完整；源码FAIL|创建仍先newId、提前成功提示/saveTasks，不能保证一次确认仅一任务。|
|T04|FAIL锁算法；原生BLOCKED|两个OS进程同盘双赢家；不是顺序测试。|
|T15|NOT_RUN完整|磁盘版本guard仍在；旧版本UI刷新/输入保留未实际运行。|
|T16|FAIL完整按钮路径|显式旧key重放不增version成立；按钮稳定key原语/确认协议未闭合。|
|T17|NOT_RUN|断线、重连、全量回读未运行。|
|T18|BLOCKED完整|原权限刷新局部撤权成立；列表/搜索/事件/附件跨主体防探测未全面运行。|
|T22|FAIL|事件真实写失败后任务及final已提交，无可恢复事件提交记录。|
|T24|NOT_RUN完整|D06三个入口经bound/sourceOk；旧Web/MCP/runner、reset真实禁用未跑。|
|T29|NOT_RUN完整|合成会话撤权检查成立；原生grant关闭/退出/到期/共享卡周期未跑。|
|T32|NOT_RUN|配对码/poll_secret/Web审批未跑；不拿账号KDF代签。|
|T37|FAIL可靠性；模型NOT_RUN|写成功读回失败→needs_verify，但恢复0/未知重放误报命中；较新版本final索引局部成立。|
|U03|BLOCKED|三角色实际桌面事实/动作未跑。|
|U07|BLOCKED桌面；D02/04/05 FAIL|重试/未知/锁的局部反例；真实输入与任务身份恢复未跑。|
|U08|NOT_RUN完整|错误/无权限/过期等真实UI出口未跑。|
|T28|BLOCKED|当前候选launcher打开→操作→权威回读→重开未跑；本地VM不代签。|

G0-E：**延期缺口（Abram 已裁决，M3 到期）**，本模块不调用MiniMax、不因provider缺口判FAIL/BLOCKED；账号来源和provider裁决都已生效，不再列NEEDS_ABRAM。

## 缺陷：只复核上一轮编号

下列行号对应本轮固定 `app/bundle/main.splash`。P1仅用于核心可靠性或安全问题，不因建议项判FAIL。

### D-M2-01 — P1 / 必修 / 部分闭合：登录已接线，但凭据进入持久视图状态

- 文件/行：439、456、673、5696、5698、5699、5711；authLogout:389。
- 触发：UI登录将口令写到STATE.pending_login_password；随后任一saveState（切视角、业务动作、拒绝等）。本轮另造测试字符串赋同字段，执行原saveState，查实际state.json。
- 实际/预期：测试明文完整落盘；TextInput未见密码遮罩，登录结束/退出不清该字段。期望秘密不进入可保存/恢复的视图状态，不写日志/事实盘；真实凭据文件不参与测试。
- 根因/影响：把凭据放进序列化STATE，saveState仅清actor。违反可信身份安全要求。真实UI未点击，源码确定路径+实际序列化反例足以要求修复。
- 证据：sandbox/secret_persistence/state.json；probes/secret_persistence.splash。实际合成A/B登录已成立，原“无入口”子问题源码已改善；发行预算/安全UI仍BLOCKED。
- 具体改法：凭据只存不可持久的认证暂态，采用宿主已验证安全输入；所有成功/失败/退出路径清理，并由saveState白名单仅保存非敏感偏好。按实际宿主预算分步完成KDF，禁止降低哈希轮数。
- 验证：两个独立合成主体原生登录/读写，随后切视角、失败、退出、重开；扫描隔离state/log/cache不含测试秘密，每查/写撤权/到期/移项目拒绝。

### D-M2-02 — P1 / 必修 / 部分闭合：STATE槽位未形成不可变确认协议

- 文件/行：3345、3350、3361、3365、3367、1962、1964、3201、3238。
- 触发：新任务第一次按钮key生成、同任务第二次/重开、同意图编辑内容、同内容独立新动作、重复创建确认。
- 实际/预期：槽位仅task|cmd，写槽函数未立即saveState；payload不同直接换key，同内容新意图永远复用旧槽，无明确确认生命周期。生产默认槽{}的动态缺键在本地VM报错；夹具预建槽后第二次调用仍报index_of不存在。显式保留旧key正常/跨状态/v5/冲突成立，但返回false+STATE文本，不返回完整原结果。
- 根因/影响：内容派生键+单槽不能区分“重试”和“新的独立确认”；重开和创建稳定性不足。平台方法未在目标宿主实证，局部VM错误不能说成发行按钮已复现。
- 证据：results/retry_key_actual.log、首批key_retry_actual.log；retry_normal_replay、history_newer_version；上述源码。期望每次明确确认生成独立意图，重试持久沿用原key与规范化内容，修改需重新确认。
- 具体改法：建立含actor/task/command/不可变payload/key/状态的持久意图记录；明确新确认和重试入口；验证目标宿主原语。授权后返回历史action_id和完整原结果，最新事实另读；创建不能先newId规避重放。
- 验证：第一次按钮、同key跨状态/新版本/重开、同key异参拒绝、同payload新key新意图；盘上task/version/事件/回执不重复。

### D-M2-03 — P1 / 必修 / 部分闭合：读盘回填改善，事件和创建仍部分提交

- 文件/行：677、2111、2138、2146、2164、2348、2359、3249、3251、3252、3432。
- 触发：任务/final落盘后events.jsonl设目录致事件写失败；创建commitBound前中断；失败后权威读也失败。
- 实际/预期：原commitBound+logEvent实际写失败，任务ACCEPTED/v1、final已落，events仍为目录，无持久事件；恢复无补事件协议。createDraftFromPanel仍提前“草稿已创建”+saveTasks。commit失败读盘回填是改善，但兜底_snapshot仍在caller mutation后。
- 根因/影响：任务、回执、事件分开保存，无动作提交记录把它们关联恢复；读盘回填不能解决已提交缺事件，创建亦未收敛可靠边界。T22核心不成立。
- 证据：sandbox/retry_event_write_failure/tasks.json及actions.jsonl、results同名log；retry_tmp_write_failure真实盘OPEN/v0；创建源码。未将手工领域mutation探针说成真实按钮成功。
- 具体改法：统一可恢复提交记录包含before/after/action/event/receipt；写点失败/进程中断后确定未提交或补齐已提交，最后才显示成功。创建同协议，无提前主写/成功；兜底快照取mutation前权威事实。
- 验证：每个关联写点、清tmp、final、event异常/中断重开，独立查盘/UI；无部分业务提交或能确定补齐，同key不重做。

### D-M2-04 — P1 / 必修 / 部分闭合：after结果已修，未知仍无法恢复且能造final

- 文件/行：2096、2101、2111、2155、2164、2170、2182、2187、2195、2227、2258。
- 触发：正常提交；提交成功后读回nil再对账；needs_verify重放；缺_PENDING_RECEIPT_ID终结。
- 实际/预期：正常final.result现在为after JSON字符串、含ACCEPTED/承接者/version1，原旧结果子问题闭合。但盘已写ACCEPTED/v1的needs_verify对账返回0，前后回执相同；扫描只认pending，版本更大就贴superseded；boot在空SESSION时退出，登录后不重跑。缺rid实际生成status=final新回执；未知receiptFor仍hit。期望未知可查原动作，不凭版本/内存造成功。
- 根因/影响：改结果字段未实现动作关联的恢复状态机；任务本身无该action提交标识，无法证明较新事实属于哪个原动作。
- 证据：retry_normal_replay、retry_readback_reconcile、finalizer_orphan、pending_replay_lock实际磁盘；history_newer_version仅证明final索引改善。
- 具体改法：final必须来自关联action的已核验提交；缺rid保持未知并返回明确错误；分别处理pending/rejected/needs_verify/final，登录恢复后授权对账，从提交日志确认或补齐关联事实/事件，历史final不被更高version改写。
- 验证：读回失败→恢复同action_id及完整原结果；缺rid/未知不报成功；已提交重试不增version；未提交可按明确恢复协议继续。

### D-M2-05 — P1 / 必修 / 未闭合：仍双赢家，未知重放仍漏释放

- 文件/行：1909、1913、1921、1927、1936、1951、2030、2031、2258、3384；stale清理:746。
- 触发：A/B均读空锁；A写/读回成功且未释放，B随后写/读回成功；needs_verify同key重放。
- 实际/预期：两个实际OS进程（pid见race-lock）共享同盘，均acquired=true、exit0；A仍持有时B覆盖。原VM未知重放先抢锁，runCommand hit返回false，盘锁非空，下一acquire=false。release无owner核对；仅5分钟TTL不能证明持有者死亡，也未覆盖所有异常清理。
- 根因/影响：read→write→read不是原子CAS；缺finally式清理/所有权协议，直接阻断并发唯一执行和后续合法动作。作者承认窗口，不能作为延期建议放行。
- 证据：results/race-lock.json、sandbox/race/tasks.lock；pending_replay_lock观察/锁文件。完整原生双账号业务竞争BLOCKED。
- 具体改法：使用已验证原子互斥/权威单执行队列，绑定owner与安全恢复；所有hit/reject/异常路径释放。不支持原语时交接最小复现与能力BLOCKED，不再以标签/TTL声称解决。
- 验证：可信A/B同事实源真正并发接单仅一承接者/一业务事件；未知hit、拒绝、写失败、杀进程重开能继续且不误释放他人锁。

### D-M2-06 — 原P1根因继续闭合；完整按钮回归BLOCKED

- 文件/行：652、659、666、4448、4513、4877；addEvidence/quarantineEvidence/togglePin入口仍经runCommandBound。
- 实际：原sourceOk六状态×三命令矩阵再次运行rc0，合法ACCEPTED等允许、OPEN/COMPLETED附件拒绝，pin按既有规则允许。无须再改白名单。真实附件/按钮/关联持久化受D01/03/05及宿主条件阻断，不扩审M5/M6。
- 证据：sandbox/source_ok_regression/observed.json；results/source_ok_regression.log。
- 验证：待核心/宿主解阻后，只回归这些入口合法/非法状态与身份、同key和事实/回执/事件；不为此新增皮肤或模块工作。

### D-M2-07 — P1 / 必修 / 部分闭合：顺序已改，旧备份/坏行与失败恢复未修

- 文件/行：768、778、852、875、878、880、882、894、904、701。
- 触发：已有legacy.bak且原主文件仍NDJSON（上一轮/迁移中断遗留）；有效+坏行；备份成功主写失败重开；原split两行NDJSON。
- 实际/预期：boot迁移已在loadJsonlLines之前，原“预写备份阻断首次迁移”顺序子问题修复。但函数仍见bak就return nil；loadJsonlLines亦nil；坏行计数后仍覆盖有效子集，无全局禁写/恢复状态。备份成功主写失败后再次启动同样跳过。原split本地VM index_of不存在；未运行目标launcher证明方法可用。期望完整历史活跃可查、失败不允许以空内存覆盖旧记录。
- 根因/影响：迁移缺状态/来源核对与成功读回；过滤坏行替代完整恢复；幂等历史丢失仍可能再次执行或覆盖历史。
- 证据：results/migration_split_actual.log；原函数分支；作者test_8亦仅保留一条但称迁移成功，test_7无条件backup_exists。坏行/中断本轮为源码确定路径，未伪称原生运行。
- 具体改法：已有备份核摘要/迁移阶段并可恢复；全部合法且备份/主写/读回通过才切换，任何坏行/失败禁写相关事实与历史；使用目标宿主已验证文本原语。
- 验证：数组/NDJSON/已有bak/坏行/备份失败/主写失败/中断重开，每条旧事件/回执及旧key可查，后续写不丢历史。

### 建议挂账

- A-M2-01 / P2：更正MD5/SHA-256、恢复真正r3基线与增量diff；补完整包/宿主/依赖/配置摘要。修正作者“全部已修”“真凭据登录PASS”超出证据的表述（作者test_login实际引用静态审计，final测试只检查字段存在）。不因材料建议单独判FAIL。
- A-M2-02 / P2：保留M1布局/键盘及M0历史缺陷，原生解阻后仅做本模块受影响输入/选择/错误出口回归；不扩皮肤或下一模块。

## 判定

- 最终结论：**FAIL**，范围为固定 `M2-r4-worktree` 原七项复审。存在独立实际磁盘/原函数失败及安全反例，故不只记环境BLOCKED；核心无P1且有真实证据成立的PASS条件尚不满足。
- 必修：按D01清除凭据持久化；D02持久不可变确认/稳定重试/新意图区分；D03统一可恢复提交并移除创建提前写成功；D04真正对账未知/缺rid失败关闭；D05真正互斥与全出口清理；D07安全迁移恢复/禁写。D06不重复修白名单。
- 具体解阻条件：提供强制限定所有HOME/app-data/cache/log到项目runtime隔离目录、可后台启动且可立即关闭并清点窗口/进程的宿主通道；交接本digest可准入的隔离包、在授权sandbox离线catalog/install_staged并读回字节。本轮preflight失败不允许绕过；本地路线尚未被证伪，不需要公开发布。
- 未测：目标launcher真实UI/按钮/三主体、原生竞争、逐写点进程杀重开、外部旧写路径、grant/pairing/SSE周期。表中分别BLOCKED/NOT_RUN；不以作者自测、历史安装或局部VM代签。
- 受影响前序模块：核M1门禁与登录/动作/输入/选择依赖，原生回归BLOCKED；M0/M1原结论保留。未修改其他模块字段或ACCEPTANCE.json。
- 最终自检：results/review-output-verification.json确认审查输入/宿主摘要、真实账号输入、其他模块及GATES其他顶层字段未变；M2构建交接字段与历史条目保留；17项相关用例完整列出，报告位置与门禁一致。
- 门禁：仅更新GATES.json的M2 status和审查字段，将开始时审查字段归档review_history；candidate_id保持r4、review_report指向本报告，历史来源保留。
- 是否允许下一模块：**否**。留在M2修复/解阻；不提供或执行M3入口。

STATUS=FAIL
NEEDS_ABRAM=no
