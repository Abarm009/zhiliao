# M2 独立 Review r8

**最终结论：FAIL。** 受审候选 **M2-r7-worktree** 在独立 harness 的 **8/8 场景仍无业务根视图**。登录/任务界面空白，业务 eval 为 `view=false`；全文日志有作用域/属性错误和 `script time budget exceeded`，即使 `[E]` 为零也不能放行。隔离与回收 PASS。D-M2-01/02/03/04/05/07 未闭合，D-M2-06 原白名单根因修复保留。不允许进入下一模块。

## 受审范围与版本

- 审查者 / 日期：Codex 唯一审查方，2026-10-11，Asia/Shanghai；没有子代理。当前工具不能读回指定主会话 Router 路由、thread createdAt 或设置标题，未声称这些操作完成。
- candidate_id / base：**M2-r7-worktree / M2-r6-worktree**。按用户交接的 `build_r2_2104_REQUEST_build_r7`、请求、`M2_IMPLEMENTATION_r7.md`、候选清单定位，不按 mtime 选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty。main **440604 字节**，SHA-256 **8d82606aaf22e7526a39108ed8c6021359db53ecb48f8ac58fb147a4c7c5a143**。上轮实际受审 r6 main 为 `76f00c37740534b68ce66a8cc9d3c17a07f11aca8ebf8577071afa6113a911f4`。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**。harness SHA-256 `12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`。
- bundle digest：**ea2b64afe2dae5ef053c68a2bc3d1324a936a102e5c0d5cc01470ff31d753436**。本轮沿用该 digest 的隔离本地签名 catalog/mirror 副本，不生成私钥、不联网签名、不 publish/listing。构建两把私钥路径已核不存在，keys 目录为空。本地 Store/实际加载路径成立，不能代替业务验收或公开发布。
- 阶段一致性：14 个保护文件在第一段→第二段完全一致，177 项独立 seed/mirror 摘要全部一致，请求摘要 `e4d054c63794a54028543ad8feb42eeb80e0ea5de7e53d59335e63835ce93427` 一致；独立运行的每场 `.bundles`、`.running` 业务 main 均匹配受审 main。宿主内置 `.system` 脚本单列，不混作业务候选。
- 前置：M1 仍 **FAIL / M1-r2-worktree / M1_REVIEW_r2.md**，没有已接受 M1 PASS 候选。按 Abram 前序挂账裁决继续复核 M2；不修 M1、不改其门禁、不伪造前置通过。受影响根 UI/空态回归失败，紧凑窗口只核请求参数，未宣称实际尺寸验收通过。
- 读取范围：AGENTS、CONTEXT_M2、00/01/02/M2/04、上轮 M2_REVIEW_r7、r7 实施/候选/本地安装证据、缺陷涉及源码、r6→r7 差异、既有 T/G0/U 定义、harness schema/执行边界及本轮完整运行证据。修复轮仅核原编号及受影响回归，没有无关扩审。
- 独立请求：`runtime/optimization/2026-10-09/M2/native/REQUEST_review_r2_2104.json`，8 个自行选择的合成数据场景；全部 `needs_model=false`，没有预装认证会话。驱动沙箱外执行窗口 **22:40:23–22:42:13 +08:00**。审查方未自行启动宿主、未做 sandbox-exec/pgrep 预检或自动化。
- 下文 **H/** = `runtime/optimization/2026-10-09/M2/native-runs/review_r2_2104_REQUEST_review_r2_2104/`；**E/** = `runtime/optimization/2026-10-09/M2/native/review_r2_2104/`；**A** = E/evidence-audit.json，复核脚本 E/audit_phase2.py。第一段笔记 `M2/native/REVIEW_NOTES_r2_2104.md` 保留。
- 置信度：候选一致、1283 项文件清单、运行错误、空白 UI、磁盘比对和确定源码反例 **高**；可信登录、真正竞争和逐写点完整恢复动态结果 **未知/未执行**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/请求一致|重算保护文件、seed、MANIFEST、安装/运行 main；比 summary/request/result|同一固定候选且证据完整|1283 项全匹配，无未列文件；14 保护文件一致；每场两份业务 main 一致|PASS，证据范围|A；E/snapshot-start.json；H/MANIFEST.sha256|
|隔离与回收|全文 profile、probes、env、files、denials、pgid和退出记录|写入受限，禁读生效，无残留|8场 probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN、quit_http退出|PASS，harness范围|H/各 result/profile/denials；A|
|真实登录/任务 UI|每场 launch-hub/capture，核完整日志和全部 PNG 内容|登录和任务根真实渲染，可继续操作|8场业务 view=false；作用域/属性错误和超时；全部业务区空白|**FAIL，D01**|H/frames、logs；A|
|硬1：重试/跨状态/同键冲突/新动作|追确认按钮→意图→边界→权威存储，核旧缺陷差异|同key同action/原结果，异参拒绝，独立新意图可新建|D02核心函数体未变，仍有unknown再创建/内容代意图反例；原生业务操作未发生|FAIL，源码；业务动态NOT_RUN|main:4813–4855、4903–4935、5039–5072；E/source-audit.json|
|硬2：主体/授权/版本/竞争|核登录、回放/恢复门控及锁交错，查盘|每次查写核权；同盘真正竞争只一赢家|门控源码已加；根UI失败；非原子锁/创建绕过未改；真实登录/竞争未执行|FAIL，D01/D05；真正竞争BLOCKED于通道|main:5090–5096、3296–3301、2880–2946、4813–4921；A|
|硬3：逐写点失败与关联恢复|核task/pending/final/event调用；独立坏历史启动查盘/UI|失败不部分成功；关联事实完整可恢复|D03未改；本轮没有到业务提交点，无新增业务写；错误无可见出口|FAIL，源码；提交故障动态NOT_RUN；精确注入BLOCKED于通道|main:855–867、3173–3288、3303–3410；H/坏历史；A|
|硬4：未知结果/较新版本原动作查询|独立无关v1、原finalv1/当前v8夹具；查盘及门控|按原action和完整after核验；不重写|回执/任务保留seed，未执行可信登录后查询；version-only恢复反例未改|FAIL，D04源码；认证后动态NOT_RUN|main:3320–3363、3442–3464；H/两个unknown场景；A|
|硬5：迁移/重复点击/超时/重启|独立三行旧bak、混坏行、缺主NDJSON bak、坏事件bak及旧state|保留完整历史，失败禁写可继续，输入和task_id稳定|迁移/恢复实际未成立；state.pending_input/selected_task_id丢失；空白UI|FAIL，D01/D07；点击/连续重启动作NOT_RUN|main:1059–1180、8434–8887、9383；H/历史场景；A|
|D06/旧入口回归|完整函数体摘要比对，核按钮到边界|原白名单修复保留，旧入口不能绕过|sourceOk与r6相同；未实际调用旧Web/MCP/runner|原根因闭合保留；T24完整NOT_RUN|main:782；E/source-audit.json|

### 原生证据逐项核对

summary 的请求与独立请求完全相同，场景、verdict/exit_method/wall_s 与各 result 一致。8 场 **12.18–12.75 秒**、宿主 rc0、quit_http 正常退出，无 ABORT。逐个核 profile 摘要、内核禁写与五处禁读探针、环境 HOME/app-data/cache/tmp 路径、控制口规则；模型代理关闭。每场 files_written_count=124、124项清单存在且均在场景目录内，library_scan 无新增，真实家目录 mtime 前后一致。清单是 mtime 收集，**不是124次业务提交**。

每张 captures 的 exists/sha256 与磁盘一致，全部16张 frames PNG 均重算摘要，只有3种不同字节内容，3种均已目视，业务区全白。因此覆盖全部 PNG 内容，但不声称16个业务步骤。`three_ndjson_stale_backup.part.png` 与该场最终PNG不同，分别属于已检查的22:41和22:40空白图组，不能套用其他场“part==final”。PNG为2800×1706全屏内容；`--size 980x760`仅命令参数可核，并不能由该全屏图证明业务窗口尺寸已通过。

host_log_markers 的 listening/quit/launch/eval/panic 与全文独立重算一致，无panic；业务 `440604 bytes ... view=false` 与另一份宿主 `809 bytes ... view=true` 区分，后者不是业务根通过。每场 `[E]=0`，但 `[I]` 有 NotFound 和一次 script time budget exceeded，不能只检查 parser 或 `[E]`。

|场景|NotFound数 / 超时日志行|权威业务盘面与界面结论|
|---|---|---|
|cold_untrusted_saved_actor|70 / 113（main:8800）|OPEN/v0任务及空回执/事件不变；登录/任务空白，FAIL。|
|compact_empty_root|71 / 114（main:8820）|空任务不变；根空态和登录入口不渲染，FAIL。|
|three_ndjson_stale_backup|71 / 114（main:8820）|三行主actions及旧一条数组bak均原样，未迁移；没有错误出口，FAIL。|
|mixed_bad_actions_freeze|88 / 131（main:8887）|valid→bad→valid原文保留，无bad_lines；未执行整体业务禁写，动态NOT_RUN；根界面FAIL。|
|missing_primary_ndjson_backup|88 / 131（main:8887）|主actions仍缺失，两行NDJSON bak不变；没有完成恢复或可见拒绝出口，FAIL。|
|corrupt_events_old_array_backup|71 / 114（main:8820）|坏事件主文件及旧合法数组bak原样；恢复/保存坏源处理未执行，不虚报已覆盖丢失；根界面FAIL。|
|unrelated_v1_unknown_no_session|88 / 131（main:8887）|当前OPEN/v1/assignee2与原ACCEPTED结果、unknown/pending不变；认证后对账NOT_RUN。|
|original_v1_current_v8|88 / 131（main:8887）|当前IN_PROGRESS/v8、原finalv1、unknown/pending及无关事件原样；历史授权查询NOT_RUN。|

正确业务目录为 `home/.octosense/apps/octosense-repair/`。tasks/actions/events、合成账号、已有bak全字节保持seed，无新增动作/成功事件/迁移记录/bad_lines。唯一变化是 state.json：actor清为null、last_idem_hit清空，**pending_input从隔离输入变为空、selected_task_id变空、status改“准备就绪”**。有视图状态写入不表示 load/迁移/认证执行成功，也不证明权限拒绝正确；实际丢失输入/选择是启动失败的受影响回归，纳入D01。

全部 sandbox-denials 全文已读取，摘要与记录独立重算相符：443外联、Metal缓存、部分 /dev/dtracehelper 写被拒；另有 appleeventsd 的禁读记录，harness摘要本来只统计octos系，不隐去全文其他拒绝。不将拒绝尝试写成成功外联/项目外写。冷场景进程组记录宿主派生的 osascript，审查方未调用该工具/辅助功能/自动化，最终全部回收；该观察保留于A，不写“宿主绝无此子进程”。

`model_proxy_stats` 在8场均**不存在**，与 needs_model=false、无模型环境键/代理一致；summary.billing_error均null，真实模型请求 **0**。**G0-E：延期缺口（Abram 已裁决，M3 到期）**，不用于M2 FAIL/BLOCKED，不申请新provider授权。

### 相关既有用例

|项|结论|本轮精确范围|
|---|---|---|
|G0-B|FAIL|可信登录核心原生UI失败；新增逐task门控源码认可；两主体真实查写/撤权矩阵NOT_RUN。|
|G0-C|FAIL|D03/04/05核心源码反例未闭合；隔离PASS不证明可靠提交。|
|T02|FAIL，源码；动态NOT_RUN|内容代意图、unknown再创建、新来源同内容仍未闭合。|
|T04|FAIL，源码；竞争动态BLOCKED|普通锁有效交错双赢家；harness串行新HOME，没有同盘双主体屏障/同步竞争动作。|
|T15|NOT_RUN|没有真实执行陈旧版本拒绝/刷新/保留输入的操作；不是沙箱rc71/rc3。|
|T16|FAIL，源码；动态NOT_RUN|D02/D04未闭合，未执行响应丢失后原key重试；任意原key/payload注入不在测试动作协议内。|
|T17|BLOCKED，完整动态|白名单无断线/响应丢失/重连控制，不能以8个全新目录冷启动替代连接恢复。|
|T18|NOT_RUN，完整动态|回放/恢复权限门控新增已核源码；未实际执行列表/搜索/事件/附件读权限矩阵。|
|T22|FAIL，源码；精确动态BLOCKED|D03未闭合；白名单不提供提交写点异常/进程中断位置/连续同盘恢复调度。|
|T24|NOT_RUN，完整|D06白名单原根因保留；旧Web/MCP/runner和graph/reset实际调用未测。|
|T29|NOT_RUN|grant/退出/到期/共享卡实际生命周期未执行，预装actor不算授权。|
|T32|NOT_RUN|配对过期/重用/poll_secret/Web审批绑定/token隔离未执行。|
|T37|FAIL，源码；动态NOT_RUN|version代原动作事实未闭合；两个新夹具未执行可信登录后原动作查询。|
|U03|FAIL|独立8场业务区空白，无真实三主体事实和动作界面。|
|U07|FAIL，启动回归；完整NOT_RUN|启动后输入/选择清空；完整重复点击/超时/响应丢失/同盘重开操作未执行。|
|U08|FAIL|初始化错误/无权限/待核验恢复出口不可见。|
|T28|FAIL|同版安装/加载成立；原生任务操作→权威回读→重开主链不成立。|

## 缺陷与本模块修复清单

以下仅复核上轮原编号及相关回归；六个未闭合项均为 **P1 / 必修**，直接阻断核心功能。没有把字体、视觉完善或材料建议作为FAIL原因。

### D-M2-01 — P1 / 必修 / 未闭合：根视图仍失败，启动清空输入与选中

- **文件行**：main:52–90、1306–1330、5803–5820，8222–8226、8434–8468、8800/8820/8887、9383–9396；权限改动5090–5096、3296–3301/恢复循环。
- **触发**：本独立请求任一场景加载当前本地signed bundle。
- **实际/预期**：cold日志:43–63缺STATE属性，:64–68等为控件名称NotFound，:113出现脚本时间预算超出，:114业务view=false；其余场亦同。真实登录/任务界面空白，state输入和task_id被空默认值覆盖。预期同宿主可挂载、可登录、任务身份/输入可恢复，启动失败须可见且不能覆盖未恢复偏好。
- **根因/影响**：91个控件提升为顶层`:=`并不使其成为root/普通函数可解析的VM变量；默认STATE仍缺初始化字段，根树求值未在宿主预算内完成。末尾return root不能救回失败表达式。当前单次操作根本不能进入可信执行链。
- **认可的源码子项**：白名单并入、load后移、回放/恢复visible+项目门控确有改变，不凭源码关闭整体D01；真实认证/动态授权未测。
- **具体改法**：先在同固定宿主+harness验证“一控件+一根+一次刷新”的变量/挂载模式，再按得到的可引用句柄组织现有UI；补齐启动所需默认属性，缩减同步启动求值到预算内。恢复成功前禁止用空STATE覆盖旧偏好；失败显示可继续出口。不要仅统计`[E]`。
- **验证/证据**：H/全部frames/logs/result，A的错误与state_diff；同候选冷启动全文无作用域/属性/预算错误，业务view=true、登录/任务截图真实可用；旧输入/task_id保留；两个合成独立主体登录/退出/撤权后逐读写验证。

### D-M2-02 — P1 / 必修 / 未闭合：内容指纹代意图，unknown创建可重复

- **文件行**：main:4813–4855、4903–4935、5039–5072、5097–5125，确认回调4677/4780、操作入口7522/5190。
- **触发/实际**：确认→confirmDraftModelBound→createDraftFromPanel→内容key→只找final→newId/pending/commitBound。主任务已写但回执pending/needs_verify时仍可再newId；同内容新独立确认被折叠；编辑一次确认换fp/键。创建回放还读取最新status代原创建结果。**源码反例；本轮没有原生重复创建实测**。
- **预期/影响**：一次确认不可变intent/key/payload，unknown先对账，独立同内容新意图可新建，原action原结果与当前状态分离；否则重复工单或阻止合法新操作。
- **根因/证据**：createDraftFromPanel、意图查找/追加、generateStableKey、receiptFor完整函数体与r6相同，E/source-audit.json、冻结源码/差异。
- **具体改法**：持久intent_id+不可变payload/key+执行phase，显式区分新确认/重试；创建也统一边界并拦unknown；按原回执返回完整结果，最新任务另读。
- **验证**：正常重试、跨状态、同key异参、同内容新intent、unknown重试、较新版本原创建逐条实际运行；同意图task/action/version/event不增加，真正新意图可新建。

### D-M2-03 — P1 / 必修 / 未闭合：关联提交/恢复仍可假成功

- **文件行**：main:855–867、3173–3288、3303–3410、3469–3490、4914–4935、5180–5186。
- **触发/实际**：task主写后final前中断；actions/events坏历史或event落盘失败。saveReceipts/saveEvents脏时只return，_setReceiptStatusFinal仍按内存命中返回true，commitBound可在event写前committed，调用方随后成功；恢复“已补齐”计数不验证事件保存成功。
- **预期/影响**：关联task/action/receipt/event完整后才核验成功，中断可证明原动作并收敛；当前可能部分提交或伪补齐。
- **根因/证据**：独立文件写未形成可恢复一致协议，保存无明确成功结果；函数体未变。A证明本轮坏历史未到业务提交点，**不将坏seed当本轮部分提交实测**。
- **具体改法**：整个命令在脏历史时禁写；持久关联before/after/action/event恢复记录，保存返回结果且独立核完整事实/唯一event；pending不得按version大小猜提交。
- **验证**：精确每写点失败/中断，同盘恢复核磁盘、回执、事件和UI；原key不重复业务写；保存事件失败不能仅计数后显示成功。

### D-M2-04 — P1 / 必修 / 未闭合：version++仍代原动作成功事实

- **文件行**：main:3320–3363、3442–3464、3209–3288、637–640。
- **触发/实际**：needs_verify expected0/resultACCEPTED，但无关动作造成盘OPEN/v1/另一assignee，恢复仅`expected+1`就final_recovered；pending升版本改superseded；orphan仍unknown无可继续出口。真实v8不能用当前状态抹掉原v1结果。
- **预期/影响**：原action提交标识和完整after证明，事实不足保持未知，未提交可明确继续；当前可能制造假成功或长期无法恢复。
- **根因/证据**：核心恢复规则未改，仅加权限门控；源码/A。H两个unknown场盘面原样，**未登录恢复，不称此为真实对账成功或本轮动态假成功**。
- **具体改法**：以关联action/完整after核验未知状态，历史原结果完整返回，提供未提交原key继续/明确失败路径；保留缺rid不成功的已修子项。
- **验证**：读回失败同action查询不增version/event；无关同版本不能final；当前v8可查原v1；缺rid保持未知；orphan按协议可恢复。

### D-M2-05 — P1 / 必修 / 未闭合：非原子锁与创建绕过

- **文件行**：main:2880–2946、2948–3125、4813–4921。
- **触发/实际**：A/B先读空，A写A读A成功，再B写B读B也成功；同actor不同会话可重入和互释；创建未先取锁直接commitBound。**源码有效交错，不是本轮真正竞争实测**。
- **预期/影响**：同盘两个可信上下文真正竞争唯一赢家，创建和已有任务写均串行；否则双提交/丢更新。
- **根因/证据**：普通write/read不具CAS互斥，owner只用actor；两个锁函数和创建函数未变，E/source-audit.json。harness串行新HOME不能代签竞争PASS。
- **具体改法**：真实原子锁/CAS或唯一可信写者，session唯一owner和异常回收；创建统一进入同一写边界。
- **验证**：独立主体同事实盘同步竞争，同actor独立会话竞争，只有一个接单结果、承接者和成功事件；异常不互释、创建/普通写不丢更新。无需新Abram授权。

### D-M2-06 — 原白名单根因闭合保留

sourceOk:782完整函数体与r6相同；addEvidence/quarantineEvidence/togglePin原修复保留。无需重修；旧入口完整T24动态NOT_RUN。

### D-M2-07 — P1 / 必修 / 未闭合：实际迁移未成立，备份/恢复格式仍断裂

- **文件行**：main:971–1005、1059–1180、855–856、9383；启动根失败8434–8887。
- **触发/实际**：本独立三条NDJSON+旧bak仍不迁移，缺主+两行NDJSON bak未恢复且无可见错误出口。源码迁移备份写原NDJSON，恢复却只整体数组；全坏主可直接被旧数组bak覆盖未先保存坏源；读回只核长度。坏主+bak本轮原样，**不虚报本轮已覆写坏源**。
- **预期/影响**：主/bak格式一致且历史全字段可恢复；损坏源保留，失败整体禁写有出口，否则丢历史或空可写假成功。
- **认可/根因/证据**：定义→load调用位置已修，但核心migrateJsonlLegacy未变；本轮根求值超时阻断初始化，不能关闭“实际迁移未成立”。H历史四场/A/E/source-audit。
- **具体改法**：先闭合D01；主与bak共用数组/NDJSON合法解析，全记录读回，覆盖前保留坏源，失败整体禁写且显示恢复路径。
- **验证**：本轮独立三行旧bak、混坏行、缺主两行bak、坏主合法bak真实复跑，全字段/坏源/错误出口查盘；连续同盘重开可查询，不把启动无写等同整体禁写通过。

### 建议挂账（不因这些建议单独FAIL）

- 通过驱动提供受支持的同盘竞争屏障、逐写点/响应丢失/连续同盘重开及原key输入协议；本审查不改业务或驱动加后门，不预装认证SESSION。仅白名单实际不能覆盖的完整动态项记BLOCKED；UI本身失败及未执行登录操作记FAIL/NOT_RUN。
- 先使同候选业务UI真正渲染，再跑原编号核心故障链；不扩做字体/皮肤或下一模块。M1等历史门禁及过时作者blockers保留来源，当前有效结论以M2.review字段和本报告为准。

## 判定与门禁

- **最终结论：FAIL**，精确适用于上述M2-r7-worktree/固定宿主。独立安装加载/证据一致/隔离回收通过，可信身份与可靠任务执行核心未通过。
- 必修：**D-M2-01/02/03/04/05/07**；先D01登录/任务真实渲染和启动状态保护，再按原编号闭合意图、关联提交、未知恢复、竞争和迁移。
- 未测/阻塞：真实认证后的权限/重试/对账没有执行；真正同盘竞争、精确写点故障、连接/响应丢失、连续同盘重开和任意key/payload注入缺白名单协议。没有ABORT，不以agent沙箱rc71/rc3作BLOCKED原因。
- 受影响先前模块：根UI/空态/输入选择做针对性回归，FAIL；不改变M0/M1历史状态，不重裁其他模块。
- 门禁：仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M2 status/审查字段，review_report指本r8、review_candidate_id指r7；修改前M2状态/旧审查字段保存在review_history，整份原门禁副本E/GATES.before-review-r8.json。作者candidate/base/implementation及其他模块保持原数据。
- 写入后读回验证：E/gate-update-verification.json；M2为FAIL、r7候选、r8报告，旧审查历史已追加。其他模块/顶层数据/作者字段未变；业务源码、宿主、原身份表/安装映射和既有验收台账摘要不变。
- 既有台账：保留ACCEPTANCE.json不覆盖历史后端/作者结果；本报告与M2.review_acceptance逐条记录17项当前原生范围。
- 审查过程偏差：第一段误读项目外记忆索引，已披露并停止；未写项目外文件、未读明文凭据/provider密钥。第二段仅访问项目内证据。该偏差保留历史，不能用harness CLEAN声称整次审查完全合规；不是应用新增缺陷。
- **不允许进入下一模块，不执行下一模块。** 构建方Kimi-K3按原编号修复，交接新固定候选和同字节冷启动日志/截图，独立重审。
- **NEEDS_ABRAM=no**：身份、provider和离线签名已裁决，本地路径成立；无余额不足/欠费或必须公开发布事项。剩余是技术修复和受支持测试控制。

STATUS=FAIL
NEEDS_ABRAM=no
