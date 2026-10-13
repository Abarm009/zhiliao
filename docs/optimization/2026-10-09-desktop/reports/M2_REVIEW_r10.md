# M2 独立 Review r10

**最终结论：FAIL。** 独立原生8场均成功加载业务根，解析/运行错误为0，隔离与回收均CLEAN，原空白问题维持关闭。但可靠执行核心仍不成立：保存的输入/意图全部丢失，合法空历史被迁成嵌套数组，坏历史被当合法记录迁入并覆盖有效备份；幂等、关联提交、原动作证明和并发的原P1亦未完整关闭。本轮不修业务代码、不进入下一模块。

## 审查范围与候选

- 审查者/日期：本主会话唯一独立审查者，2026-10-12，Asia/Shanghai，无子代理。无法核验指定Router主会话模型或获取thread createdAt/设置标题，未声称已切换或完成命名。
- 两段式：第1段源码/差异/作者证据审查，笔记 `M2/native/REVIEW_NOTES_r2_0748.md`；独立请求 `M2/native/REQUEST_review_r2_0748.json`，SHA-256 **f4a703d278a9698e29f4765833a71bd22156ae93610e7a07d2c4590740d6a6bc**。驱动在agent沙箱外运行 **08:53:42–08:56:05 +08:00**，第2段核完整证据并最终判定。审查方未启动launcher/harness、未做sandbox-exec/pgrep预检或外部UI自动化。
- **实际受审运输候选：M2-r8-worktree**。用户本次明确提供build_r2_0748_REQUEST_build_r8，候选由其请求、`M2/r8/native-prep/snapshot-start.json`、已签名mirror和安装Store定位，不按mtime选版。HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty；实际比较基线为上一轮r9所审 **M7-r7-worktree**，与 `r8/main.splash.before-r8` 的7b82c131…字节一致。作者声明base=M2-r7-worktree单独保留。
- 冻结main **545982 B / SHA-256 a9acd344b16cb75b0e60e27ef7cfe86d6d9b69598f15d3b1838d31eef0347ceb**；签名包digest标识 **1cf1144dc990a644dea9801352c0c4b2b2ebda3c89c6ddc8fba6fbf9955284e7**。各场mirror、installed及唯一.running中的全部包资源与冻结运输包一致。
- 当前工作树main **551000 B / SHA-256 0fb141f92574e06581e92c08cc27d8d186c00783be0f1fc7f6b446b8766e0116**，与运行版本不同，审查起止未变化；其后续state/schema/历史确认改动**不在本次原生运行范围**。差异已保存，不把a9包结果冒充0fb版本结果。正式 `M2_IMPLEMENTATION_r8.md` 仍缺失，最新存在的作者报告为r7；r8运输版可定位但交接材料不完整。此项列建议，不单独造成FAIL。
- 前置：**M1仍FAIL / M1-r2-worktree / M1_REVIEW_r2.md**，没有已接受的M1 PASS。按Abram本次前序挂账裁决继续M2，未制造前置PASS。只做原生根、未登录空态、输入/意图与恢复回归，不代M1全量放行。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，独立重算SHA **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness SHA **12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9**，与记录一致。
- 阅读范围：AGENTS、CONTEXT_M2、00/01/02/M2/04、r7实施/五账号记录、r8/r9审查、M1 r2、原17项验收定义、上一轮缺陷涉及的冻结源码及差异、schema/harness与本轮完整运行证据。只复核原D01～07和受影响回归。
- 实际运行：驱动8场独立原生冷开/迁移/读取故障/空登录/退出，审查方核所有结果及磁盘和图像；审核脚本仅处理已有文件。未运行：成功/错口令登录与两可信主体完整授权矩阵、认证业务创建/重试/冲突/历史查询、真正同盘竞争、逐提交写点故障/响应丢失、连续同Store重启、旧外部入口真实负例。
- 置信度：候选字节、隔离/回收、动态盘面失败与明确源码分支 **高**；非空输入/confirm_intent恢复失败的具体内部执行点 **未知**；认证业务、竞争、精确提交中断动态结果 **未知/未执行**。不把静态反例写成本轮已经发生的双接单或假成功事故。

以下 **H/** = `runtime/optimization/2026-10-09/M2/native-runs/review_r2_0748_REQUEST_review_r2_0748/`，**E/** = `runtime/optimization/2026-10-09/M2/native/review_r2_0748/`；**A** = E/native-evidence-audit-r10.json；**B** = E/business-observations-r10.json；**C** = E/business-detail-r10.json。

源码行号全指 **E/source.main.splash**（a9acd344…冻结副本，对应本轮包内main.splash），不是当前工作树main的行号。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|同版本与证据完整性|重算请求/seed/包资源/宿主/harness/profile/捕获图与整个MANIFEST；比较起止保护输入|证据同候选且完整|1293项清单全部匹配，178个seed/mirror不变，10保护输入不变；所有运行资源逐字节对应冻结候选|PASS，仅版本/证据范围|A、protected-inputs、seed-manifest、final-review-verification|
|隔离与回收|逐result的probes/pre/post/进程组/env/profile/denials/files_written核查|只写场景目录，禁读生效，无残留|8场probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN；无ABORT|PASS，harness范围|A；H各result/profile/denials|
|原生根/登录空态/退出|目视16图的全部7种不同内容；全文host.log与taps记录|业务根持续可见，空输入/退出提示明确|8场545982 B业务eval view=true，0解析/运行错误、tick_exception_count=0；cold分别可见空登录和退出提示|PASS子项，D01旧空白仍关闭|A；H/cold*/frames/log|
|硬1：原key、冲突、独立新意图、跨状态查询|独立seed保存issued/confirm意图；追按钮→创建/确认→回执/盘；复核unknown/后续状态分支|重试同key/action/result，异参拒，新意图可新建，原历史不依赖当前状态|8场issued和confirm意图丢；unknown异参只final冲突；历史确认仍要求当前OPEN。真实认证重试未执行|FAIL，动态持久恢复+源码|B/C；source:505–524、6112–6275、6519–6527、6631–6687|
|硬2：权限、旧版本和真正竞争|伪saved actor/session负例、账号/会话授权源码、原锁交错核查|不冒用；撤权/到期/跨项目拒；同盘接单一赢家|伪会话未认证、task不变PASS子项；非原子read/write/readback锁仍存在。两可信主体/真正竞争未运行|FAIL，D05源码；动态能力缺口BLOCKED|B；source:3620–3721、4028–4074；schema/harness|
|硬3：逐写点一致提交|独立events目录读取失败；审pending/task/final/event流程|失败关闭、无业务部分提交/假成功|读取故障保住根/原backup且冻结事件写；但指向不存在bad_lines；pending保存忽略返回、task/final/event间无完整关联提交恢复协议|FAIL，D03源码与D07动态；逐提交点注入BLOCKED|B/C；source:896–942、3970–4119、4339–4361、6313–6335|
|硬4：未知结果对账|原finalv1/currentv9与三字段相同却完整after不符夹具；核恢复与历史查询|原action完整事实，不重复写，较新状态独立展示|未登录4回执逐字保持PASS子项；认证恢复只比version/status/assignee，历史确认受OPEN前提。认证查询未执行|FAIL，D04源码；认证动态NOT_RUN|B/C；source:4179–4213、6631–6687|
|硬5：输入/身份/历史恢复|冷开8种独立历史夹具，核state/主/bak/bad_lines与图|保留输入/意图，严格迁移、可恢复、错误可继续|8场输入与意图丢；[]→[[]]；坏行→字符串、有效bak被坏主覆盖；缺主NDJSON bak仍不恢复；读取错误指向不存在文件|FAIL，独立原生|B/C；H各业务jail/PNG|
|原D06与受影响前序回归|冻结sourceOk与r9逐字比较；根/未登录空态回归|已关根因不回退|sourceOk相同，根/空态维持；旧Web/MCP/runner真实负例未执行|D06保持关闭；T24 NOT_RUN|E/phase1-verification；A/B|

### 证据逐项核对

1. 审核脚本 **5745项证据一致性检查，0失败**，不是5745个业务测试PASS。MANIFEST的 **1293项** 摘要、唯一性、范围和完整文件清单均重算；summary.request与独立请求结构精确一致，所有场次/目的/时长/结论相符。
2. 各profile从模板、场景路径和控制端口重建后逐字相同，摘要匹配；五禁读和场景外禁写探针通过。所有HOME/app-data/cache/tmp等路径均限对应场景；MAKEPAD_HIDE_WINDOWS是值1开关，MAKEPAD_REMOTE是对应端口，未把这些非路径值误判为越界。
3. 每场 **16.23–16.37秒**，rc0、quit_http、pre/post NONE、最终进程组为空；真实home目录mtime前后一致，library_scan无新增。files_written清单为 **126或128项**，逐个存在、唯一、有序、路径在场景内；这是驱动按mtime记录的文件清单，不是业务提交次数。实际运行期间进程组成员亦核对，不据最终清理反推绝无派生进程。
4. 178个审查seed/mirror文件不变，seeded_files与准备文件摘要精确一致。各场唯一.running、.bundles和mirror全部运输资源逐字对应a9冻结包；current工作树0fb不混入原生结果。
5. 16张PNG均重算摘要，全部 **7种不同字节图像已目视**，覆盖所有capture内容。尺寸实际为2560×1260/1262/1264全屏图；`980x760`仅启动参数，不能由此称紧凑布局通过。cold两个capture分别显示“请输入账号 ID 与口令”和“已退出；请重新登录”，配合内置taps日志证明相应按钮路径触达；不猜capture文件名的拍摄先后。
6. 全文读取8份host.log，重算host_log_bytes、tail和所有host_log_markers。业务eval **545982 B view=true**，与809 B宿主其它视图区分；无[E]、预算/作用域错误或未知test-action；tick_exception_count均0。Metal/ui-hang信息不当作业务解析失败，也不因无日志错误认定偏好/历史成功恢复。
7. 全文sandbox-denials与汇总重算一致：443外联尝试、Metal缓存及/dev/dtracehelper写被内核拒绝。拒绝尝试不是已成功外联/项目外写；聚合日志有重叠，汇总不当作精确系统调用次数。审查方没有自己启动宿主、做预检、调用osascript/辅助功能或其它未授权自动化。
8. needs_model均false，所有result没有model_proxy_stats字段、env无代理endpoint/MM_KEY，summary.billing_error=null。**本轮真实模型请求0**；字段缺失是该运行模式未启代理，不臆造统计对象。G0-E为 **“延期缺口（Abram 已裁决，M3 到期）”**，不导致M2 FAIL/BLOCKED或NEEDS_ABRAM。
9. 本轮没有新私钥生成，复用已签运输包；作者离线keys目录为空及删除记录在第1段核验。作者hub verify/install_staged路线rc0且本轮实际原生加载，**完整hub check仍REFUSED**（model_config URL的assets扫描），不能将本地安装成功写成公开准入/发布通过。没有上传/publish/listing/push/消息或部署。

审核脚本初版将MAKEPAD的开关/端口误归为路径，随后又使用了错误预期值；已依据实际harness源码修正并重跑全部检查，最终0失败。错误属于审查脚本，不是产品失败，不隐去或计入业务缺陷。

### 权威盘面逐场结果

正确业务jail为 **H/<场景>/home/.octosense/apps/octosense-repair/**。所有场tasks.json及合成账号表前后逐字节相同，没有创建/接单业务提交；下表是加载/迁移实测，不冒充业务事务注入。

|场景|独立实际结果|判定|
|---|---|---|
|cold_persisted_intent|非空中文pending_input→空；confirm_intent→空；issued key map→{}；actor=null、saved session不恢复；actions/events各[]→[[]]；两登录/退出提示可见|D01/D02/D07 FAIL；防冒用/根/提示PASS子项|
|three_rows_stale_backup|3条完整NDJSON含嵌套marker及result全字段正确迁成数组；bak为原主NDJSON；events空仍嵌套|三行主优先/全字段子项PASS；D07整体FAIL|
|mixed_bareword_history|actions变[合法对象,"NOT_JSON_RV2_0748",合法对象]，好行字段保留；bak覆为混坏主原文，无bad_lines；state只显示events迁移|坏行被假接受、未进入对应损坏恢复，D07 FAIL|
|missing_primary_ndjson_bak|actions主仍缺失；3行合法NDJSON bak原字节不变；无对应可见恢复出口；events[]→[[]]|恢复仍未接通，D07 FAIL|
|corrupt_event_valid_backup|events变["INVALID_EVENT_RAW_RV2_0748"]；旧2条合法bak被坏主原文覆盖；原合法备份精确字节在整个该业务jail均未找到|合成恢复来源被毁，D07 FAIL|
|invalid_array_elements|含string/null/[]的actions数组原字节保持，无bad_lines/对应损坏提示；源码按len当有效并不设脏标志；events嵌套|非法记录schema未被拒，D07 FAIL；未登录，未虚称认证写已绕过冻结|
|no_session_unknown_v1_v9|4条unknown/final/pending回执及v1/v9任务原字节保持；没有业务事件对账；events[]→[[]]|未登录保护PASS子项；认证恢复/原历史查询NOT_RUN；D07 FAIL|
|unreadable_events_directory|events仍目录，旧合法backup字节保留；state写“events写已冻结；请按events.jsonl.bad_lines修复”，但该文件不存在；业务根无错误；全部输入/意图丢|冻结/保护旧backup/根PASS子项；错误恢复出口D07 FAIL|

所有场pending_input、confirm_intent_id与action_keys_by_task都丢失。选中无权任务被清空可能是合法权限过滤，**不因selected_task_id为空单列缺陷**。图中可见区域均为登录/无可见任务，坏历史/读取失败没有对应可继续恢复提示；不声称未显示区域绝无控件。状态落盘文字本身不等于用户已看见和能够继续恢复。

## 缺陷与逐条修复建议

仅保留原编号。以下P1直接阻断M2核心或恢复安全，不把皮肤、布局或完整交接形式问题列为必修。

### D-M2-01 — P1 / 必修 / 部分关闭：输入恢复仍失败

- **文件/行**：冻结main:505–524 loadViewState、:882 saveState、:1157–1160加载调用、:1235–1283迁移保存、:11221–11226初始化。
- **触发**：任一本轮seed带非空中文pending_input，固定宿主冷开；cold additionally点击空登录/退出，其它7场不点此类按钮。
- **实际/预期**：8场磁盘pending_input全为空；预期保留输入，读/parse失败保护原来源并可继续。原空白/解析错误已关闭，不能要求重修渲染。
- **根因**：loadViewState不提供可核验的成功恢复门控，启动无条件saveState会覆盖旧来源。白名单虽然包含pending_input，本轮仍未恢复；**具体是parse/字段并入哪个内部点导致清空，未插探针，未知**，不杜撰是某按钮清空。
- **影响/证据**：丢未提交内容与重试线索；B全场input_before/after，H各seed/业务state/图；source与diff。
- **具体改法**：在固定VM实证完整state读取、字段并入和输入投影；明确load结果，失败不以默认STATE覆盖原文，保留可恢复来源；安全恢复偏好/意图而永不恢复actor/session。
- **验证**：同新候选harness分别非空中文/空输入/缺字段/损坏state冷开，核盘和UI；失败保持原文，未登录不成为主体。可信成功登录动态仍缺控制通道。

### D-M2-02 — P1 / 必修 / 部分改善：原key丢失、unknown异参与历史重放未闭合

- **文件/行**：main:505–524、:6090–6095、:6109–6275、:6481–6527、:6631–6687；人工确认控件:10320–10330→confirmDraftModelBound(:5867)→createDraftFromPanel→commitBound；confirmDraft(:6672)为确认子链。
- **触发**：冷开保存issued key和confirm_intent；或createDraft pending/needs_verify同key改payload；或原确认final后任务合法到ACCEPTED/v9，再查询原动作。
- **实际/预期**：8场issued map→{}、confirm_intent→空；源码unknown只在final/final_recovered异参时conflict，原任务DRAFT则继续确认；历史核验因当前非OPEN返回unknown。预期持久原意图/不可变payload、所有占用状态同键异参拒绝、历史原result与当前状态分开。
- **根因/影响**：既有意图仍以fp匹配，加载漏issued且confirm意图动态失效；unknown冲突未覆盖；历史结果绑定当前OPEN。可能重生key、误执行未确认内容或误判合法历史。**本轮未发生认证创建/重放，不声称已产生重复工单**。
- **证据**：B全场intent/issued；source:6146–6149异参分支、:6179–6214 DRAFT恢复、:6636/:6682 OPEN条件；E两份diff和冻结源码。
- **具体改法**：持久intent_id/actor/task/command/不可变payload/key/phase；区分同操作重试与独立新确认；所有unknown先同payload核验并查询原action，不能确认已改内容；按精确原action回执/事件返回完整原result，最新task另读。
- **验证**：正常重试、跨状态、同key异参（含unknown）、同内容不同源新意图、unknown创建、currentv9查原v1；task/version/action/event次数及完整result核验。新创建先取锁改善保留，不重新按内容直接生成意图。

### D-M2-03 — P1 / 必修 / 部分改善：关联提交与中断恢复不足

- **文件/行**：main:896–942保存/事件、:3970–4119 finalize/commitBound、:4254–4273补事件保存、:4339–4361 recordReceipt、:6313–6335创建。
- **触发**：pending写失败但caller继续；或task主写后clear-tmp/final/event间失败或进程中断。读取故障场另证保存冻结可见状态指向不存在文件，但不是提交写点注入。
- **实际/预期**：源码recordReceipt/创建忽略pending保存返回；task直接覆盖，清tmp写未catch；final先落、锁释放后事件才写。保存boolean和事件失败needs_verify有所改善，但不证明每写点无部分提交/最终可恢复。预期关联task/receipt/event一致、失败未知不能成功、原key可收敛。
- **根因/影响**：跨文件顺序保存缺可靠关联提交标识及完整before/after/event恢复；局部write返回和version/status读回代完整事实。事件失败降级若再写回执失败，仍可能盘上final/event不齐。**认证提交中断本轮未执行，这是确定源码路径，不虚称动态已假成功**。
- **证据**：source :4064/:4074/:4083/:4098/:4118；:4359、:6313 pending保存返回未消费；:6334事件在提交后；B/unreadable仅boot读失败。
- **具体改法**：统一关联可恢复提交协议，持久before/after/action/event并核每步结果；失败保护原key/来源，完整磁盘回执与唯一关联事件核验后成功。处理清tmp/读回异常与进程中断，不以再次写状态文字当恢复。保留已加boolean/脏历史整体禁写/精确rid的改善。
- **验证**：pending/tmp/task/clear-tmp/final/event各写点失败+中断，同Store重启核权威任务/回执/事件/UI；event失败不成功、补事件真实落盘且不重复。当前白名单/schema无精确业务提交点控制，动态BLOCKED具体于此。

### D-M2-04 — P1 / 必修 / 部分改善：三字段仍代原动作证明

- **文件/行**：main:4140–4218，尤其:4179–4204；历史确认:6631–6687；commit读回:4085–4098。
- **触发**：needs_verify的expected=0，另一个动作也造成v1/同status/同assignee，却problem/asset/appointments与原after不同；或原finalv1后当前v9。
- **实际/预期**：恢复只比version/status/assignee就final_recovered并补事件；原confirm仍要求当前OPEN。预期核精确原action提交标识及完整结果，事实不足保持未知，合法后续状态不抹掉原历史。
- **根因/影响**：三字段相似性替代动作归属/完整after，能把无关变化误认原成功。r8取消pending按新版猜superseded、after状态不符保持unknown的改善认可。独立no_session场4回执原样是未登录保护PASS子项，**未认证执行上述恢复，未虚报本轮产生final_recovered**。
- **证据**：冻结source完整分支；B/C/no_session；H任务v1/v9及4回执；source历史OPEN前提。
- **具体改法**：原action持久提交标识/完整before-after/唯一关联事件证明；历史final原result与当前task分别查；orphan按原key明确安全继续或失败，不只有人工核对文字。
- **验证**：写成功读回失败不增业务次数；同三字段但异完整after不能成功；缺rid未知；currentv9查原v1；未提交原key可按协议继续。真实认证恢复NOT_RUN。

### D-M2-05 — P1 / 必修 / 部分改善：仍无原子竞争边界

- **文件/行**：main:3620–3689获取锁、:3691–3721释放、:3725–3745命令取锁、:4028–4074提交、:6285–6320创建。
- **触发**：A/B两个可信上下文同盘同步接单：均先读空；A写/验证A并完成提交前锁核对后暂停；B写/验证B并核对；双方随后写任务/回执。
- **实际/预期**：write-then-readback和单独锁复读不能提供CAS；最后锁检查到task写之间仍可交错，回执/事件各自覆盖更无原子排他。预期仅一承接者、一成功动作/事件。**这是源码可成立交错，不是本轮真正竞争实测**。
- **根因/影响**：普通read/write无原子线性化点；expected_version复读不能替代原子提交。存在双赢家/丢更新/历史覆盖风险。r8创建进入同锁、完整token归属/失败关闭改善认可，不再指控创建完全绕过获取锁。
- **证据**：source :3674–3689/:4028–4074；HOST_PRIMITIVE_BLOCKED注释仍在；schema/harness逐场串行、fresh HOME。
- **具体改法**：核验实际宿主原子锁/CAS或唯一可信写者；创建/更新/完整关联提交统一边界，独立session所有权和崩溃回收；无原语给可运行最小复现与技术缺口，不继续将write-verify称互斥完成。
- **验证**：两个实际可信上下文、同权威盘、同步屏障竞争，核task/receipt/event/双方UI单赢家。当前白名单/schema无法表达共享Store同步竞争，动态BLOCKED，不以串行或双Store测试代签。

### D-M2-06 — 原白名单根因保持关闭

sourceOk与r9实际受审版逐字相同；原准入修复无回退，不列新的P1或要求重复修复。旧Web/MCP/runner/graph/reset完整真实负例本轮未运行，T24仍NOT_RUN。

### D-M2-07 — P1 / 必修 / 独立原生失败：坏历史假迁移、备份覆盖与恢复无出口

- **文件/行**：main:948–991 loadJsonlLines、:1231–1290启动迁移/保存、:1342–1500共同解析/迁移；尤其:1397–1417非nil/len、:1469–1470写唯一bak；保存冻结:897/:905。
- **触发**：合法[]、混裸词坏行、有合法bak的坏主、缺主NDJSON bak、含无效元素数组、events为目录。全部独立隔离数据。
- **实际/预期**：[]→[[]]；裸词→字符串记录，无bad_lines；合法旧bak被坏主覆写；缺主仍缺；无效数组项原样被接受；目录读失败虽冻结但指向不存在bad_lines，图中没有可继续出口。预期严格JSON/数组/逐记录schema，原文与有效恢复来源保护，格式统一、可验证恢复，失败冻结并真实可继续。
- **根因**：宿主parse_json宽容，非nil/len不是合法记录证明；空数组走逐行；备份覆盖未保护现有有效来源；主/bak共同parser仍宽容，写失败诊断文件未核可读性，恢复状态可能被后续events迁移提示覆盖。
- **影响**：坏历史假成功，原合成备份来源丢失，unknown动作无法可靠恢复。丢失的是**本轮合成恢复来源，不是原业务数据**。
- **证据**：B/C逐场完整原文；corrupt旧bak在整个业务jail无精确字节；mixed的middle_record为NOT_JSON_RV2_0748；missing.primary_missing=true；H各盘/PNG；source。三行合法全字段迁移/主优先PASS子项保留。
- **具体改法**：整体真数组且逐项严格对象/字段/完整JSON；合法[]原样；裸词/字符串/null/嵌套数组拒；主/bak共用同规则；已有有效bak不盲覆，保存坏源及有效backup；所有写/读回及诊断文件结果核验，失败不默认空历史。错误优先显示，不被后续无关成功提示覆盖，给真实可用恢复操作。
- **验证**：空/1行/3行、混坏/全坏/无效数组、缺主NDJSON bak、已有有效bak、读取及写失败；核完整字段/原文/全部来源/冻结/UI；同Store再开不继续嵌套。不能仅再加注释或用0解析/迁移条数交差。

### 建议挂账（不单独导致FAIL）

- 补齐r8正式实施报告、准确base及全部配置/源码清单；当前0fb工作树后续修订交新固定候选和独立冷启动证据，不覆盖旧运输包/请求。未交接修订是否关闭问题当前未知。
- 固定宿主的可信输入、任意原key/payload、同盘同步竞争、逐提交写点/响应丢失、连续同Store重开等测试能力，作为技术解阻条件；本轮不修改harness或新增业务测试后门。
- 完整Hub check拒绝如实挂账；本地已安装运输路径可用，不转向公开发布、更换渠道或要求新授权。无关视觉/下一模块问题不扩审。

## 相关既有验收逐项复核

原 `docs/build-loop/ACCEPTANCE.json` 定义与历史来源保留。下表是本轮冻结原生候选范围，源码FAIL和动态FAIL明确分开。

|项|结论|实际范围与证据|
|---|---|---|
|G0-B|BLOCKED|根/空登录/退出/伪actor-session保护PASS子项；固定宿主上一轮明确拒type/key，当前同二进制无可信文本输入通道，成功登录与两主体矩阵未执行。身份来源已裁决，不需新授权。|
|G0-C|FAIL|D01/D02持久恢复、D07历史/backup独立原生失败；D03/04/05源码未闭合。|
|T02|FAIL|D02原意图恢复动态失败，unknown异参及较新状态原查询源码；实际创建重发/冲突/新来源NOT_RUN。|
|T04|FAIL|D05非原子锁源码；创建同锁子项改善；同权威盘同步竞争BLOCKED于schema/白名单能力，不拿8场串行代签。|
|T15|NOT_RUN|未实际认证陈旧版本拒绝/刷新/保留输入/阶段百分比负例。|
|T16|FAIL|原key/confirm意图冷开丢失实测；同key跨状态源码未闭合；响应丢失控制无法覆盖，动态未执行。|
|T17|BLOCKED|白名单/schema无SSE断线/重连或全量回读控制；fresh HOME不代断线恢复。|
|T18|NOT_RUN|未登录空态/伪身份不授予权限PASS子项；授权门控源码保留；独立主体列表/搜索/事件/附件矩阵未执行。|
|T22|FAIL|D03关联提交源码、D07迁移恢复动态FAIL；逐业务提交写点故障/连续同Store恢复BLOCKED于控制能力。目录样本仅boot读失败。|
|T24|NOT_RUN|D06原已关白名单无回退；旧Web/MCP/runner及graph/reset真实负例未执行。|
|T29|NOT_RUN|空会话退出提示子项，不代grant关闭/到期/共享卡实际调用生命周期。|
|T32|NOT_RUN|配对码过期/重用/poll_secret/Web审批/token隔离未测，5账号不是配对机制验证。|
|T37|FAIL|D04三字段代原action证明、历史必须当前OPEN源码反例；未执行模型声称成功/真实提交后回读超时完整动态链。|
|U03|BLOCKED|根和未登录权限空态PASS子项；固定宿主可信输入缺口阻断三真实主体同task事实/动作/自验禁止动态。|
|U07|FAIL|8场输入和issued/confirm意图丢失；真实重复提交/响应丢失/版本冲突/离线完整链NOT_RUN。|
|U08|FAIL|空输入/退出PASS子项；坏历史/缺主/读失败没有对应可继续恢复出口，目录故障指向不存在bad_lines。|
|T28|FAIL|安装/业务根/同字节PASS子项；冷开输入/意图恢复FAIL；实际操作→权威读回→同task重开完整链NOT_RUN。|

BLOCKED仅用于白名单/schema确实不能覆盖的上述控制能力。**harness无ABORT；没有用agent内sandbox-exec rc71或pgrep rc3作BLOCKED理由。** 成功登录/认证业务未运行是实际范围，不由作者claim代替。

## 判定与门禁

- **最终结论：FAIL**，适用于M2-r8-worktree的a9冻结运输包在固定宿主中的M2范围。输入/意图和历史恢复已有独立动态失败，核心P1未关闭；不是因建议、provider延期或缺完整形式报告判FAIL。
- 必修：**D-M2-01/02/03/04/05/07**的上述剩余核心；D01根/0解析、D06白名单、D07合法三行迁移、D05创建进入同锁及D03局部保存结果改善保留。
- Kimi-K3留在M2按原编号逐项修：先严格历史/backup与输入/意图恢复并守住可渲染根，再收敛不可变意图、关联提交、原action证明、真实竞争边界；每次交新固定候选/差异/同字节原生冷启动证据。已有0fb未交接修改先核对再适配，不reset/stash/覆盖他人修改。
- 阻塞技术条件：可信输入通道、原key/payload调用、同权威盘同步竞争、提交写点/响应丢失及连续同Store重开。无需重新裁决身份/provider；不改harness/业务加后门来伪造通过。
- 前序受影响回归：根和未登录空态维持PASS子项，输入/意图恢复FAIL；M1仍FAIL，其他模块不改。
- 门禁：仅写GATES的M2 status、review_report/reviewed_at及review_*，报告指向本r10；review_candidate_id=M2-r8-worktree，review_base_candidate_id=M7-r7-worktree（r9实际比较基线），源码/digest与本轮运行一致。作者candidate/base/implementation等保留历史，旧review字段存入review_history；写前完整副本 **E/GATES.before-review-r10.json**，写后核其它模块及非审查字段不变。
- 原全局ACCEPTANCE历史不覆盖；17项本轮精确范围写本报告、E/final-acceptance-17-r10.json和M2.review_acceptance。保护输入、候选/运行/seed清单与门禁范围核验见 **E/final-review-verification-r10.json**。
- 没有读真实明文凭据或密钥、没有启动宿主或项目外写入；第1段误读项目外记忆索引已说明并留在阶段笔记，第2段只用项目内材料。模型0请求、新私钥0生成；作者已删除离线私钥记录和空目录核验保留。
- **NEEDS_ABRAM=no**：本地catalog/install_staged原生加载可用，身份/provider/离线签名已授权；无402/欠费，也无必须公开发布事项。
- **不允许进入下一模块。** 本报告仅提供M2修复清单。

STATUS=FAIL
NEEDS_ABRAM=no
