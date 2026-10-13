# M6 独立 Review r6

**最终结论：FAIL。当前候选在 8 场独立 harness 原生运行中均解析失败，应用业务区为空；原 D-M6-02、D-M6-03、D-M6-04 仍未闭合。CLEAN 只证明隔离与回收通过，不能放行产品。**

- 审查者 / 日期：当前主会话唯一审查者，2026-10-11，Asia/Shanghai；无子代理。
- candidate_id：`M6-r5-worktree`，base=`M6-r4-worktree`；以 GATES、实施报告及清单交叉定位，没有按文件时间选版。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r5.md`；清单：`runtime/optimization/2026-10-09/M6/r5/CANDIDATE.json`。
- 被审内容：main SHA-256=`9a1a8e274f4cd9b98d1fcdad4ac21d5dd6d391de8b3af30f07192d6c0822af34`，417088 B、8885 行；与作者 r5 清单一致。HEAD=`8d730569546cb57310944bb299695134df773b9d` 加既有未提交改动；不把 HEAD 单独当完整候选。
- 本次包 digest=`a12494c40081d55adefa6673ee1dc8be574a9114d815f46362e9a658ce8f8e9a`；原业务 main/config/identities、安装副本、实际 `.running` 副本逐场同摘要。隔离签名只改变测试包 manifest，不改变原包源文件。
- 开始/结束快照：第1段开始/结束、第2段核查时，候选源、配置、原 manifest、identity 配置、harness、宿主、清单、GATES 与 ACCEPTANCE 均一致；最终 GATES 仅变 M6 status/审查字段及审查历史，核验见 S/final-review-verification.json。
- 前置：M5=`M5-r5-worktree / M5_REVIEW_r6.md / FAIL`，没有接受的 M5 PASS 候选。按本次 Abram 前序挂账裁决继续审查，不宣称前置 PASS，不修前序，不单以挂账判新增 M6 缺陷。
- 实际环境：驱动在沙箱外于 **16:50:12–16:52:09 +08:00** 执行本审查请求；宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 模型路由 / 标题：当前主会话没有可用路由核验/切换及 createdAt/标题修改接口，不声称已切换到指定模型或已改标题。MiniMax provider 已由 Abram 授权；实际 model_config.enabled=true，但本轮真实请求0。
- 已阅读范围：第1段 AGENTS、CONTEXT、M6 硬验收、02 门禁相关规则、04 模板、环境方案、r5 实施/清单、上轮 r5 Review 及其冻结快照；按修复轮规则仅核 D02/D03/D04、D01/D05 受影响回归和准备文件。第2段读全部原始 summary/result/profile/日志/denial/manifest、实际运行包、输入/权威文件及8张原生截图。
- 已运行范围：第1段隔离离线 keygen/certify/stamp/sign/verify、官方 install_staged/Store 重建/may_run、8场 seed/apps 根核验；第2段独立证据摘要/环境/回收/日志标记/文件对账。真实宿主仅由驱动执行，审查方没有自行启动 launcher、sandbox-exec、pgrep、osascript、辅助功能或其他 UI 自动化。
- 未运行范围：可信三角色完整业务流程、实际收藏/提醒/跳回/撤权/AI建议、业务写后权威回读、运行中故障及同盘进程重启、产品布局/150%/键盘、同版本演示。产品解析失败造成的后续未执行记 NOT_RUN；白名单能力不足的具体步骤另记 BLOCKED。
- 范围偏差：第1段初始工具批次读过项目外记忆索引及技能说明，已披露；此后未继续显式读取项目外业务/记忆文件，也没有项目外写入。当前审查结论依据项目内实时证据。
- 置信度：候选定位、摘要一致、隔离/回收、原生解析失败及下述确定源码控制流 **高**；尚未执行的业务效果/模型事实正确性/产品布局 **未知**。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M6/native-runs/review_r2_1309_REQUEST_review_r2_1309/`。驱动原始证据，只读未改。
- **S**：`runtime/optimization/2026-10-09/M6/native/review_r2_1309/`。冻结快照、`previous-reviewed-to-r5.diff`、函数追踪、独立离线安装/seed、审查核验记录。
- **R**：`runtime/optimization/2026-10-09/M6/native/REQUEST_review_r2_1309.json`，SHA-256=`b87a1a65d42a2929b05a80e6d9cdf84c0938dd047702045e0299cbf5de7cca7e`。
- **N**：`runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r2_1309.md`。第1段原笔记，不因第2段结果重写。
- **A**：S/`native-evidence-audit.json`，由 S/`audit_phase2.py` 独立重算生成。A 的 evidence_integrity=PASS 不等于业务 PASS。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/前置/增量|交接三方、摘要、冻结差异、M5 Review|当前候选明确，运行同版本，前置真实保留|r5 main/配置/运行副本一致；M5 FAIL 保留|定位 PASS；前置未 PASS|S/start-snapshot、diff、A；M5 r6|
|证据完整性|全部 MANIFEST 重算、请求/summary/result 对账|无缺失/错摘要/重复/未列文件|1297项全部一致，错误0|PASS|H/MANIFEST.sha256；A|
|内核隔离/回收|profile逐场重建、探针、进程、外写及 denial 核对|指定CLEAN条件全部成立|8/8符合，正常quit，残留0|PASS|H/*/result、profile、denials；A|
|本地catalog安装与识别|独立离线Store检查，再核实际registry/.running|当前digest本地可安装/被识别|正确apps/.bundles；8场均launch并得到同摘要运行副本|PASS 安装/识别层|S/offline-store-evidence；H/*/logs、.running|
|原生解析及应用首屏|实际launch/capture；读parser日志并逐图看业务区|应用渲染登录/任务/下一步|4条parser错误/场；只有标题和空白业务区|**FAIL D03回归**|H/reporter_entry_input/logs/host.log:48；其余场:45；8 PNG|
|三角色首次使用|3种角色目标seed，launch/taps及输入诊断|可信登录后同task追踪/搜索/下一步|无业务登录UI；没有可信session|入口FAIL；后续NOT_RUN|H/reporter_entry_input、technician_entry、manager_narrow|
|收藏隔离/重登/恢复|D04读回/调用方源码；pending seed实际对账|固定task/actor读回，失败状态真实|源码读回目标被清空；原生没有收藏动作|FAIL源码D04；实际收藏NOT_RUN|S/source-traces；H/prefs_pending_history；A|
|提醒恢复/去重/旧作业|D02源码；重复/坏/空/旧预约4场独立输入|可恢复、保护原文、去重/旧提醒取消|源码恢复成功不可达；原生在parser前失败，未到load|FAIL源码D02；实际提醒NOT_RUN|S/source-traces；H四场；A|
|撤权与摘要跳回|授权过滤源码；预撤权/旧预约scene|动态撤权后拒绝跳回，无旧提醒|没有真实先登录后撤权/跳回；seed未变化|NOT_RUN；动态步骤能力BLOCKED|H/revoked_old_appt_summary；R/schema|
|历史/阶段/模型业务边界|函数调用图、事实/版本/引用/既有caller回归|两新增链可调用、真实事实/模型/人工出口|新增函数无caller且引发parser失败；只有静态/审计渲染|FAIL D03；真实模型NOT_RUN|S/affected-functions；main:1379、1492、8685、8709|
|原生视觉/交互|独立查看8原生PNG、尺寸与action日志|3视口/150%/中文/键盘可达|全部2800×1718、业务区为空；key/type被拒|入口FAIL；产品布局NOT_RUN；输入步骤BLOCKED|H/*/frames；reporter日志:39–41|
|受影响回归|上轮实际c683快照→当前r5差异；D01/D05与元数据caller|已关闭源码项不重开，协议caller同步|formatter/nav非注释源码不变；旧AI caller未同步绑定|D01/D05源码子项保持；D03回归FAIL|S/affected-closed-subitems-regression、diff、source-traces|

### 原生证据逐项核对

1. **完整性**：H/MANIFEST.sha256 **1297项**，摘要错误/缺失/重复/未列文件均0。summary.request与R相等；summary与8场result的scenario/verdict/exit_method/wall_s一致；harness/template摘要与当前文件一致。未修改H任何文件。
2. **profile_probes**：8场 apply rc0；写到场景外探针被拒且没有创建；5项秘密/配置黑名单探针均被拒；ok=true。逐场按模板与实际本机控制端口重建profile字节一致，所有HOME/app-data/tmp/log/cache环境路径均在该场景新目录；无模型代理放行规则。
3. **进程与回收**：8场pre/post_pgrep均rc1、class=NONE、out/err空；pgid_members_after=[]；verdict=CLEAN、quit_http=ok、host_returncode=0，wall_s 13.22–13.29。没有ABORT。原HOME .octosense mtime前后相同、library_scan_new_or_modified=[]。
4. **进程记录限定**：reporter、empty、revoked三场 `pgid_members_running` 含 `osascript`/`(osascript)`，退出后均为空。审查请求只使用获准宿主内置 --test-action，没有直接调用它；证据不能用来声称整个宿主运行中从未出现osascript。该进程的具体内部调用用途仅凭本记录未知，不据此捏造辅助功能/授权违规；保留原始进程记录，未新增相应产品P1。
5. **files_written_in_run_dir**：每场count=123、列表123项，无重复，文件存在且解析路径留在新根；包含宿主/appstore运行副本等，**不是123次业务动作**。每场7个业务输入文件（tasks/state/actions/events/accounts/提醒/附件索引）与seed逐字节相同，业务新文件0；坏提醒未出现.recover。因为源码未成功执行，不能认定损坏保护、提醒去重、pending对账或撤权已经成功。
6. **sandbox_denials**：全文读取并重算summary一致；remote:443、Metal缓存及个别/dev/dtracehelper写尝试被拒。没有把被拒尝试当成功外写/外联；CLEAN所要求的隔离/回收成立。不是用agent内rc71/rc3解释失败。
7. **host_log_markers**：全部完整日志重新计算bytes/tail/markers相同，无panic。8场均`wm: launched hub:octosense-repair as client 1 (in-process, card)`、`[SPLASH] eval: 417088 bytes ...`，随后还有宿主809 B eval。registry/appstore运行成功不代表业务解析成功。digest_seen_in_seed=true；digest_seen_in_host_log=false如实保留，另以catalog/.bundles/.running字节核候选，没有用日志未打印digest判错版。
8. **parser与截图**：每场4条同类错误；报修场host.log:48–51，其他场:45–48。保留VM源码位置1450/1522及原文；实际文件对应新增history `main.splash:1447–1448` 的保留标识符 `ok`、phase `:1519` 的条件表达式。8张captures均存在且sha256与result/MANIFEST相同，逐张视觉确认标题“OctoSense Repair”、业务区为空；全部2800×1718，不将request size当实际产品客户区测量，也不沿用HTML/包内旧截图。
9. **动作能力**：reporter日志:39、40、41分别明确拒绝 `tap:145,107`、`key:Tab`、`type:M6-R2-NONCREDENTIAL`；taps:744,108@8/@10被接受调度，但没有业务登录控件，不能称业务重复点击。未知输入用非凭据文字，不把测试口令放日志。
10. **模型与签名**：8场needs_model=false，result中的model_proxy/model_proxy_stats均缺省，故本轮无代理启动及真实请求，不称模型PASS；无billing_error。独立离线签名与当前digest安装可行；S/keys/working.key、anchor.key已删除，exists_after=false，剩余key文件0，复核后仍空。没有publish/公开签名/listing/上传/消息/公网部署。

|场景|隔离回收|当前包识别|原生应用解析/首屏|业务结果|
|---|---|---|---|---|
|reporter_entry_input|PASS|PASS|FAIL，4 parser错误/空白|NOT_RUN；输入动作能力BLOCKED|
|technician_entry|PASS|PASS|FAIL，同上|NOT_RUN|
|manager_narrow|PASS|PASS|FAIL，同上|NOT_RUN|
|duplicate_due_cold|PASS|PASS|FAIL，同上|NOT_RUN，不把两条seed当通知|
|corrupt_recovery_guard|PASS|PASS|FAIL，同上|NOT_RUN，不把坏文件没变当保护通过|
|empty_recovery_guard|PASS|PASS|FAIL，同上|NOT_RUN，不把空文件没变当恢复成功|
|revoked_old_appt_summary|PASS|PASS|FAIL，同上|NOT_RUN，预撤权不代动态撤权|
|prefs_pending_history|PASS|PASS|FAIL，同上|NOT_RUN，pending未产生实际对账|

## 缺陷

### D-M6-02 — P1 / 必修 / PARTIAL：恢复成功分支不可达，备份失败可错误解除保护

- **文件行**：`app/bundle/main.splash:1721`加载；`:1781`显式恢复；`:1788–1795`备份吞错/清pending；`:1804–1806`save后才清pending；`:1819`普通save闸；`:1922`、`:1950`失效保存结果；`:5157`登记调用方。
- **触发**：坏/空/schema/拒读提醒文件令pending=true后，选择`m6_explicit_recover_follow_ups(false)`；或保留备份遇读/写失败；再核普通登记、失效和关闭结果传播。
- **实际/预期**：源码use-memory分支先调save，save因pending=true返回false，所以成功清pending分支不可达。keep-backup分支即使读/备份失败仍清pending并提示已保留。函数没有非定义caller，用户没有可达恢复入口；失效save结果与登记返回仍未被既有调用方可靠消费。预期先核备份成功，再有可达受控恢复；失败保持保护/可见错误，恢复后可以持续使用。
- **已改善**：新的pending闸确实阻普通登记/失效/dismiss，不再以列表非空解锁。只认可该源码子项；当前原生解析失败，没有实际执行恢复路径，不声称本轮已经覆盖原文。
- **根因/影响**：恢复复用自身禁止的普通写，备份未核便解锁，UI/调用结果链未接通。原D02持续恢复与文件保护核心仍不成立，硬3/5、T23、U07/U08。
- **证据**：N与S/source-traces、affected-functions（恢复无caller）、diff；H两异常场日志/文件及A说明没有进入业务load。
- **具体改法**：只修D02，建立现有UI中明确确认的恢复入口；读/备份字节校验失败不能清pending；受控恢复写与普通save闸分开，或使用失败可回退的状态转换；失效/登记返回真实保存状态，并由现有预约/关闭调用方消费。
- **验证方式**：隔离坏/空/schema/拒读→普通登记/关闭/失效保持原文→备份失败保持pending→显式恢复成功→同记录重试仅一份→同Store进程重启；核原文/备份、提醒与UI结果，旧预约/撤权后不得复活。

### D-M6-03 — P1 / 必修 / OPEN：新增链引起原生解析失败，且仍没有桌面触发/事实版本闭环

- **文件行**：`main.splash:1447–1448`保留名ok；`:1519`phase条件表达式；`:1804–1805`新增恢复也用ok（parser后续覆盖须继续实跑）；`:1379`、`:1492`两链定义；`:1385`、`:1498`空task版本绑定；`:1435`、`:1540`回包actor；`:4278`等旧元数据caller；`:8685`静态阶段、`:8709`审计历史UI。
- **触发/最小复现**：用R正确预装当前digest，任意场仅`launch-hub:octosense-repair`并capture。8场真实日志报`'ok' is reserved and cannot be a variable name`，及`Expected )`/两条`Expected } not found`；窗口业务区为空。期望同版本原生包可解析并呈现登录/工作台，然后既定history/phase链可使用。
- **实际与未执行边界**：这是本轮新日志及同字节运行包的真实FAIL，不来自M5历史错误，也不是R01安装问题。parser位置1450/1522保留在证据；文件行按原始main确定为1447、1519，不机械把VM行号当原文件行号。未成功执行任何三角色业务命令，后续效果不能判PASS。
- **旧D03闭环仍缺**：新增函数均无非定义caller，UI只显示审计字段/静态说明，无实际两链触发或“阶段手工编辑”入口。空task绑定采用无任务sentinel，局部task/project版本未用于回包检查；回包重新取当前actor，缺发出时固定上下文/重核权/过期。输入缺维修历史、预约占用及事件事实，返回schema不明确，引用存在性不能保证任意事实陈述真实。
- **受影响回归**：recordModelMeta强制显式task/project/actor，旧requestAiSuggestion各meta调用未同步，写为空绑定后被历史消费排除；没有用UI默认值兜底的方向正确，但不能当调用方已兼容。实际config.enabled=true，作者enabled=false理由不成立；MiniMax并非缺授权。
- **根因/影响**：用字符串存在探针替宿主语法验证；函数声明替可达流程；复用草稿契约未固定task事实与完整版本。当前新增代码阻断整个本模块原生核心，硬1–5的入口；原history/phase目标仍不成立，T25/T26/T33/T34/T35/T38。
- **证据**：H/*/logs/host.log（reporter:48–51、其余:45–48），8张PNG，`.running`同摘要，A；S/affected-functions与source-traces；29/29作者词法探针不是语法/运行证明。
- **具体改法**：先仅纠正本轮新增路径的保留标识符及宿主不接受的表达式，使用现有Splash合法条件赋值写法；不能只移除两链换取白屏消失。再接既定桌面触发和人工出口；固定发出task/project/actor/事实版本，输入有权维修/占用/事件事实及明确JSON schema，回包核权/版本/请求/过期，存真正建议与引用；补旧caller明确绑定或明确未建任务种类。模型不得直接写业务。
- **验证方式**：新的同digest离线包经独立harness首先无parser错误、登录/任务UI实际出现；然后可信主体三链各新描述、无历史/矛盾/不存在引用及失败人工继续；切task/actor、撤权/事件改变/迟到不落错任务，核权威业务不被模型写。真实请求仅needs_model经本机代理，模块累计≤10，402/余额不足/欠费即停并记原文及NEEDS_ABRAM=yes。

### D-M6-04 — P1 / 必修 / PARTIAL：读回定位被提前清空，未落盘显示成已落盘

- **文件行**：`main.splash:2145`捕获rid/cmd/actor；`:2163`清_PENDING_RESULT；`:2194–2196`才取task_id；`:2288`final；`:2180`tasks写失败返回saved=false；`:7027–7031`统一“已落盘”；`:2271–2285`finalize异常；`:2148–2154`未激活清理。
- **触发**：收藏tasks写后读回空数组/错任务/旧pinnedBy；或tasks明确拒写；state/final回执拒写后重试/重启。
- **实际/预期**：源码清_PENDING_RESULT后取任务，task_id恒为空，pinnedBy比对分支跳过；只要JSON能parse便可能readback=true并final。tasks写失败返回saved=false却被togglePin needs_verify分支显示“已落盘”并保留新收藏内存；finalize失败只改内存needs_verify，持久结果仍需可恢复收尾。期望固定目标独立读回、执行状态/UI一致，已落盘不盲目回滚，明确未执行可回退且保留错误，不产生假成功/永久pending。
- **已改善**：三态结构、state/final异常可见及eager清锁的方向保留。原生本轮未执行收藏/故障路径，不能把pending夹具不变当已经证实永久pending。
- **根因/影响**：遗漏固定task/预期偏好，清理丢上下文；调用方不消费saved/readback；内存收尾不代持久对账。原D04收藏核验与失败后持续使用仍欠缺，硬1/5、T30、U07/U11。
- **证据**：S/source-traces/m6_save_prefs、togglePin、diff、N；H/prefs_pending_history及A明确没有业务变更。
- **具体改法**：只修偏好路径，写前固定task_id/actor/action_id/预期偏好，不从清理后的pending再取；缺目标/比对不一致即待核验，不把parse成功代比较。调用方按saved和执行态准确显示/恢复；明确拒写回退保留错误；finalize错误有持久对账/重启恢复并保留稳定键，所有退出清锁/收尾完整。
- **验证方式**：双可信主体收藏/取消、跨项目、重登/同key重试、version不增；拒写tasks/state/final receipt及读回空/错任务/错偏好，核UI、磁盘、回执及下一动作一致。

### 原关闭项、建议与技术缺口

- **D-M6-01 / D-M6-05**：formatApptLine与m6_due_count_for_identity非注释源码与上轮实际快照一致，保持原源码子项关闭，不重新扩审；原生时间/数量/筛选仍未验证。
- **R-M6-01（审查准备）**：本轮已纠正seed安装根，并由真实registry/运行副本证实。旧轮记录保留；不计产品P1，不再用作本轮BLOCKED。
- **A-M6-01～03**：建议挂账保留；文档旧环境/授权描述、精简调试/补演示等不另判P1。不修前序或经营大屏/客户端等范围。
- **BLOCKED仅限确定能力缺口**：本轮宿主明确拒绝tap/key/type，无法用允许动作完成可信文本输入/Tab步骤；schema各场新目录，不能表达同Store进程重启、运行中writer/commit故障、登录后动态撤权/受控迟到交错、断线恢复注入。需要驱动提供仍在同隔离目录、可定位命令/回收/权威变化的受控步骤或支持相应白名单输入；审查不改驱动或绕过SESSION。原生应用parser失败是FAIL，其余未执行不泛记BLOCKED；本轮没有ABORT，也不引用agent内rc71/rc3。

## 全部硬验收与相关用例

|硬验收|本轮结论|
|---|---|
|1 三角色追踪/搜索/收藏/重登/跨项目|**FAIL**：原生入口parser失败、D04源码未闭合；可信全流程NOT_RUN，输入子步骤BLOCKED|
|2 三条真实AI链及失败/无历史人工出口|**FAIL**：D03新增链parser/入口/依据/版本未闭合；真实模型NOT_RUN|
|3 提醒恢复/去重/旧作业/跳回|**FAIL**：D02源码恢复未闭合；原生提醒NOT_RUN；同盘重启/动态撤权子步骤BLOCKED；不称后台常驻|
|4 三视口/150%/键盘|**FAIL 应用可用入口**；实际产品布局/放大/对比NOT_RUN，key/type输入子步骤BLOCKED；不凭2800×1718宿主截图放行三视口|
|5 跨模块输入/选择/滚动/恢复/台账|**FAIL**：D02/D04源码缺口、D03解析阻断；完整操作NOT_RUN；原P0/38业务/12UI定义/历史不变|

|用例|本轮结论与精确范围|
|---|---|
|G0-F|FAIL D02源码恢复；原生前台提醒NOT_RUN；后台/官方任务卡NOT_RUN，同盘重启步骤BLOCKED，不称后台常驻|
|T17|NOT_RUN真实断线/权威全量回读/不重复写；schema断线故障/重连注入步骤BLOCKED；磁盘seed未变不替该结果|
|T18|NOT_RUN可信搜索/列表/事件/附件授权投影；D03消费三元组源码子项改善保留，不称完整通过|
|T23|FAIL D02源码恢复；原生通知恰一份NOT_RUN；实际同盘进程重启步骤BLOCKED|
|T25|NOT_RUN真实模型缺/矛盾/恶意原文；D03 OPEN，不断言模型无虚构|
|T26|NOT_RUN真实模型失败与人工继续；人工出口文案不代可达操作|
|T28|FAIL当前原生应用解析/首屏；离线安装/识别PASS；同task实际业务与回读NOT_RUN，同Store重启步骤BLOCKED|
|T29|NOT_RUN grant退出/到期/撤权/共享卡/跳回；登录后动态撤权步骤BLOCKED，不把预撤权seed代真实撤权|
|T30|FAIL D04源码读回/真实执行状态；实际收藏隔离/重登/版本NOT_RUN，可信输入步骤BLOCKED|
|T33|NOT_RUN真实新描述泛化；未以元数据、静态函数或夹具替代|
|T34|FAIL D03两新增依据/引用链不可达；真实无历史/歧义/不存在引用拒绝NOT_RUN|
|T35|NOT_RUN真实迟到/改派/改约失效；D03请求绑定源码缺口保留，受控运行中交错步骤BLOCKED|
|T36|NOT_RUN实际工具白名单及模型写边界；manifest/源码不代真实结果|
|T38|当前source/config/宿主/digest/request/data版本定位PASS子项；真实模型/提示/成功失败复跑NOT_RUN；当前parser失败可复现|
|U01|FAIL原生首屏业务为空、无当前任务/下一步；三角色完整操作NOT_RUN|
|U02|NOT_RUN真实描述/草稿修改/失败人工继续|
|U03|NOT_RUN三可信角色同task事实/动作/独立验收；输入步骤BLOCKED|
|U04|NOT_RUN原生预约/改约/冲突/过期；D01源码formatter子项保持关闭|
|U05|NOT_RUN设备位置/服务空间/依据真实可读；D03建议链OPEN|
|U06|NOT_RUN原生进度/完工/独立验收/退回历史；前序挂账不代修|
|U07|FAIL D02/D04源码恢复；业务重复点击/故障实际NOT_RUN，运行中writer/commit故障步骤BLOCKED|
|U08|FAIL应用业务/异常出口无法呈现；业务空态/附件/无权/过期出口NOT_RUN，不能把空白客户区当正确空态|
|U09|NOT_RUN应用三视口/长中文/150%；实际只有空白业务区，不沿用HTML/旧图|
|U10|NOT_RUN焦点/对比/颜色冗余；key/type已被拒的键盘步骤BLOCKED|
|U11|FAIL D04源码收尾；宿主截图/回收PASS子项；应用滚动/输入/面板NOT_RUN|
|U12|NOT_RUN同版本2–3分钟实际结果/失败空态演示及独立人员复述|

## 判定

- **最终结论：FAIL**。依据本轮同版本原生parser/白屏失败及原D02/D03/D04核心缺口，不因建议、美化、M5历史前置或能力不足单独惩罚产品，不给“基本通过”。
- 本次精确范围：证据完整性、内核隔离/回收、当前digest离线安装/识别/运行副本一致PASS；**应用原生解析/首屏FAIL**；业务命令/真实模型/完整产品布局NOT_RUN，明确白名单/受控步骤能力缺口BLOCKED。
- 必修清单只保留 **D-M6-02、D-M6-03、D-M6-04**。D03中的当前新增代码语法回归先修，必须随后补两链可达与既定事实/版本闭环；不能把删链/禁用模型当核心完成。
- 留在M6：按上述编号及具体改法最小修复→交接新的候选摘要与差异→独立harness复跑原生解析/登录及核心业务→提供缺失受控步骤/真实结果。无需新的Abram授权；余额/欠费尚未出现。
- 受影响前序：只检查当前累计源与已有M5状态、M3元数据caller回归；没有改写M0–M5结论或把旧测试代本轮。
- 更新位置：本报告与GATES **M6 status/审查字段/审查历史**。作者candidate/base/实施/证据/test_counts等保留；前次Review完整来源归档。ACCEPTANCE.json与其他模块不变，原P0/38业务/12UI未删未改。
- **不允许下一模块；不给M7入口；未执行下一模块。**
- STATUS=FAIL；NEEDS_ABRAM=no（身份/provider/隔离离线签名已授权、本地安装可行，实际模型0，无计费错误）。
