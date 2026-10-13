# M2 独立 Review r13

**最终结论：FAIL。受审候选 M2-r10-worktree，不允许进入下一模块。** 本轮独立原生运行已经加载正确业务包，18场均 CLEAN、业务解析/运行错误0、登录页渲染成立；但独立复现了 **D-M2-01 的损坏视图保源失败**及 **D-M2-07 的错误历史被当作合法记录迁移**。D-M2-02/03/05 的原核心源码缺口仍在，不能由冷启动或 CLEAN 放行。只保留阻断可靠执行的 P1；无关建议不作为 FAIL 原因。

## 审查范围、候选与前置

- 审查者/日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai；无子代理，没有修改业务代码。实际 Router/model 路由及线程 createdAt 无当前工具可核验，未声称切换为指定模型或完成标题设置。
- 两段式来源：`M2/native/REVIEW_NOTES_r2_0924.md`；独立请求 `runtime/optimization/2026-10-09/M2/native/REQUEST_review_r2_0924.json`，SHA-256 **c219406c6ba29aac6a0cdd64ba772ffa675164b4c1a66fe4b38e764dde58fdc5**。
- 驱动在 agent 沙箱外执行：**2026-10-13 09:32:02–09:37:56 +08:00**，18场/3批，CLEAN、没有 ABORT。本段只读运行证据、核源码、写审查产物与 M2 门禁；没有自行启动 launcher/harness 或 sandbox-exec/pgrep 预检。
- candidate_id/base：**M2-r10-worktree / M2-r9-worktree**。按 M2 GATES、r10 实施报告/快照、冻结运输 catalog 定位，用户第2段交回的是本候选的独立请求证据，未按 mtime 选版。
- HEAD：**8d730569546cb57310944bb299695134df773b9d**，dirty；作者报告 `reports/M2_IMPLEMENTATION_r10.md`，候选清单 `runtime/optimization/2026-10-09/M2/r10/native-prep/snapshot-start.json`，差异 `M2/r10/main.splash.diff-a5-to-r10.patch`。
- 受审 main：**653536 B / SHA-256 244a180c4605f85e3fd2a5d7f6b9d4987704080ac017c7182ec09f6d2ee4dc83**；bundle **0.1.0-b / digest 04492599e88fd37807778d172a2e397e0edafb55a4fa2d4d31c51a0cd38167a3**。每场 mirror、预装 bundle、实际 `.running` 的全部14个包文件都与冻结运输包相同。
- 当前工作树 main 为 **702182 B / SHA-256 805257a2b6a14834d9ab092e17cc10fb143710803812c4999d55abfadaed6ae9**，属于后续变化，**没有被代入本候选**。第1段至本段门禁写入前，11项保护输入均未变；冻结源与382项 seed/mirror 内容未变。结论仅适用冻结 r10，不能直接套用于后续工作树。
- M1 前置实际：**FAIL / M1-r2-worktree / M1_REVIEW_r2.md**，没有已接受 M1 PASS。按前序挂账裁决继续 M2 局部审查，保留事实、不制造前置 PASS、不修 M1。本轮受影响冷启动/登录页/输入冷恢复有针对性证据；完整 M1、认证后工作台和三视口/150%没有重新验收。
- 阅读范围：第1段已读 AGENTS、CONTEXT_M2、00/01/02/M2/04、r10交接/清单/作者证据、r12原缺陷及验收定义；第2段读完整 summary、18份 result/profile/host.log/denials、2931项 MANIFEST、所有业务盘文件并目视全部11种不同PNG内容。仅复核 D-M2-01～07 和受影响回归。
- 实际运行：驱动18场内置 launch-hub/capture/退出；审查方 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M2/native/review_r2_0924/audit_phase2.py`，rc0，以及全运行包/盘面/图像补充比对。**认证业务动作0、独立主体竞争0、精确提交点注入0**；不把历史夹具中已有 final 当成本轮命令执行成功。
- 未运行：认证重试/同键冲突/权限矩阵/撤权到期/较新版本原动作查询、旧入口绕过完整负例、真实输入双击/超时、同 Store 连续重开、真实竞争和逐提交点中断。细分 NOT_RUN 与白名单控制 BLOCKED 见下文，未使用 agent rc71/rc3 作为理由。
- 模型请求 **0**，代理未启用；G0-E 如实记为 **延期缺口（Abram 已裁决，M3 到期）**，不计 M2 FAIL/BLOCKED。没有计费错误，没有公开发布需求，**NEEDS_ABRAM=no**。
- 置信度：候选/隔离/完整性/原生保源与迁移失败、明确源码分支 **高**；未执行的认证结果、真竞争与精确提交恢复 **未知**。

下文 **H/**=`runtime/optimization/2026-10-09/M2/native-runs/review_r2_0924_REQUEST_review_r2_0924/`；**E/**=`runtime/optimization/2026-10-09/M2/native/review_r2_0924/`。

**A**=E/native-evidence-audit-r13.json，**B**=E/business-detail-r13.json，**C**=E/business-supplement-r13.json，**V**=E/visual-observations-r13.json。所有源码行号指 **E/source.main.splash**（同 r10 冻结包），不能套当前工作树行号。

## 必需检查

|检查|独立步骤与期望|实际结果|判定/证据|
|---|---|---|---|
|候选、宿主、请求与证据一致|重算请求/全部清单/seed/包/控制器，核 summary/result|10135项一致性检查0失败，2931清单完整，18场运行包同 r10|PASS，仅一致性；A/C/phase1-snapshot|
|隔离与回收|核 profile/probes、HOME等、pre/post、进程组、退出、denials|18场probes.ok=true，pre/post NONE，最终组空，CLEAN，18.23–18.34秒|PASS，仅harness范围；A、逐result/profile/log|
|真实业务冷开与 UI|业务653536B eval、启动记录、运行资源、截图|18场正确加载、0[E]/panic，登录页可见；没有认证后工作台交互证据|PASS冷开/登录页子项；A/V；工作台NOT_RUN|
|硬1：幂等/跨状态原结果|追按钮到事实源，同时核正常/冲突/历史/未知|持久意图保持；D02外层仍非nil判成功/当前OPEN误拒历史；认证动态未跑|FAIL源码 D02；动态NOT_RUN；source:6827等、B|
|硬2：独立身份/权限/真竞争|可信主体、撤权/到期、同盘竞争一赢家|伪持久主体没有自动登录；完整权限未跑；D05普通读写锁无原子边界|FAIL源码 D05；权限NOT_RUN/竞争控制BLOCKED；source:4421、schema|
|硬3：失败与关联提交|逐写点/中断/恢复核完整事实，不假成功|启动保源有正负例；D03关联恢复仍不足，精确提交点未注入|FAIL原D03，动态控制BLOCKED；A/B、source:4796等|
|硬4：读回失败与查询旧动作|完整after比对，原结果和当前任务分离|D04完整比较根因已修；无登录不补回执/事件通过；D02实际外层结果仍不闭合|FAIL D02相关；D04动态认证NOT_RUN；source:4993、5140、B/C|
|硬5：输入/旧数据/重开|输入与来源保留、失败出口、旧记录字段恢复|正常输入/意图保持、合法1/4记录及3记录bak恢复通过；损坏view丢源、错误JSON被迁移|FAIL原生 D01/D07；B/C/V；双击/同Store重开NOT_RUN|
|旧状态守卫/旧入口|核原sourceOk修复及受影响绕过|D06原源状态白名单根因保持关闭；完整旧入口负例未运行|根因修复保持；T24完整项NOT_RUN|

## 独立原生结果：18场逐项收口

下表 PASS 均指写明的**子项**，不代完整 M2 硬验收。每场都有同候选业务加载、登录帧和权威盘证据。

|场景|独立盘面与 UI 实际|结果|
|---|---|---|
|restore_input_intent|中文两行输入、不可变意图、键映射保持；伪actor/session未恢复，actor为空，登录页；未授权选择被清空|PASS冷恢复/伪会话负例；不代认证后任务身份验收|
|typed_view_fields|非法对象输入等被安全兜底，不进入UI造成运行错误；意图/键仍保持|PASS类型兜底子项|
|corrupt_view_backup_directory|坏state原主字节未变，bak仍目录；登录页明确备份失败/写冻结/人工出口|PASS失败保源子项|
|corrupt_view_stale_readable_backup|坏主被默认state覆盖；旧bak仍不同内容；jail没有任何文件含本次完整原字节；状态却称已备份，登录页无告警|**FAIL，D01**|
|corrupt_view_new_backup|新boot-bak逐字等于原坏state，默认主可溯源；登录页无恢复告警|PASS保源子项；告警可改进|
|truncated_nonempty_view|未闭合非空对象被宽容parse恢复并覆主；没有boot-bak或其它完整原字节来源，状态“准备就绪”|**FAIL，D01**；部分pending_input保留不代完整保源|
|one_record_full_ndjson|迁为1记录数组，全字段/嵌套结果等于独立原行；legacy.bak等于原文|PASS迁移子项|
|four_records_old_backup|主迁4记录全部字段相等；旧1记录bak字节未变；legacy2.bak等于本次4行原文|PASS新旧来源共存子项|
|truncated_middle_record|主与旧bak未变，bad_lines逐字等于整个原主；登录页真实告警/冻结出口|PASS坏行否定子项|
|braced_invalid_nonempty_record|`{"action_id":"rv-invalid", "result":}`变成`{"action_id":"rv-invalid"}`进入主数组；记“迁移3条receipts”，登录页无异常|**FAIL，D07**；非法来源未被拒绝|
|empty_object_middle_record|主/旧bak保留，完整原文另存真实bad_lines，登录页告警|PASS空对象否定子项|
|bad_source_diag_directory|诊断目标为目录，坏events原主及合法旧bak原样保留，停恢复覆盖；UI指向人工检查原文件|PASS保源失败否定子项|
|migration_backup_directory|bak为目录，合法NDJSON主字节未动；磁盘state记备份失败，登录页没有该告警|PASS保源子项；FAIL告警子项，按A-M2-r13-01建议挂账，不单独判模块FAIL|
|missing_primary_full_backup|缺主恢复三条完整记录数组，所有嵌套字段一致，bak原字节不变|PASS缺主恢复子项|
|read_failure_events_directory|events仍目录，旧bak原样；UI告警写冻结/人工检查原文件，没有命名不存在diag|PASS读失败否定子项|
|unknown_history_no_session|未登录v9任务/原回执/needs_verify/事件均不自动修改，登录页；未补造final|PASS未登录负例；不代认证后对账|
|empty_history_control|合法空历史保持[]，正常输入保持，任务未变，未自动登录|PASS正常冷开子项|
|corrupt_view_equal_readable_backup|本次坏源在既有相同boot-bak完整保留，主变默认、状态准备就绪，登录页无告警|PASS完整来源留存子项；此输入未证明严格损坏识别|

所有18场 tasks.json 的结构化业务事实未变，隔离测试账号字节未变；这符合无认证业务操作的运行范围，**不等于一次命令只执行一次已经实证**。伪会话负例也不能证明全权限矩阵。

## 证据审核与隔离事实

1. summary.request 与独立请求逐字段相同，请求摘要未变，18场及3批顺序、verdict/时长/退出/批次/可选字段均与 result 一致；driver_not_sandboxed_check.rc=0。
2. MANIFEST **2931项**逐项核文件存在/哈希/唯一性/运行树内路径；清单与完整实际文件集合相等。A的 **10135** 是一致性检查数，不是应用业务测试数。
3. 每场 profile 摘要正确，按本轮模板、真实记录的run目录/控制端口/禁读home路径重建逐字相等。禁止写场景外、禁止读取5个指定敏感目标、禁止宿主执行osascript的探针均记录为拒绝；只读探针记录，没有读取禁读目标。
4. 12个路径环境变量均指向各自新场景；仅本机控制端口网络规则，没有模型proxy规则/MM_KEY/endpoint。pre/post pgrep均rc1/NONE，pgid_members_after为空；host rc0、quit_http正常退出；真实HOME根mtime前后相等，library_scan=[]。没有ABORT或残留。
5. files_written_in_run_dir 每场**125–128项**，全部唯一、有序、存在且限该场景，count一致且未截断。这是驱动mtime文件清单，含包、缓存、图片等，**不是业务写调用次数或全系统I/O审计**。
6. seeded_files 完整集合与新seed/mirror逐项对应；apps/catalog.json确实存在且等于同签名mirror。每场catalog_autofilled字段缺省，没有依赖驱动自动补齐。每场实际运行包全部14文件与运输包一致。digest_seen_in_host_log均false，日志未直接打印digest；身份由catalog/签名manifest、全包字节和运行路径共同核对，未谎称日志含digest。
7. 全文重算18份 host.log 的bytes/tail/markers；都有653536 B业务view=true eval和实际launch记录；809 B是宿主其它视图。无[E]、panic、catalog拒开。此前“解析清零”在本轮业务层确有执行；认证后工作台仍未操作，不称完整桌面闭环PASS。
8. **36张PNG / 11种完整字节内容**：全部摘要与PNG头核实，11个不同图像已实际目视，重复帧按完整哈希等价对应。尺寸为2560×1238或2560×1606；启动参数只1280×800，**不称三视口/150%验收**。V记录代表帧与全部路径、可见提示。每种图都是业务登录页，无凭据输入或认证业务截图。
9. 全文读sandbox-denials，用harness相同正则独立重算summary一致。包含443外联、Metal缓存、/dev/dtracehelper及osascript执行**被拒**；后者有隔离探针来源，不能当成功自动化或宿主已越界。系统日志时间窗可交叠，不将计数当互斥系统调用数。
10. model_proxy_stats在18份result中**缺省**，needs_model=false、无proxy文件或代理环境；不是伪造“零统计对象”。本轮未启proxy或发真实模型请求，无billing_error，provider延期不影响判定。
11. 本轮未生成新签名私钥，复用当前digest隔离签名包；只读核实r10 native-prep/keys仍空，原生成/删除依据在offline-store-evidence.json，A记录0残留。没有联网/public签名/publish/listing/push/消息/部署。

本轮宿主 SHA **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness SHA **8141b4de36e8a248a1b7ed0b9d430fa3ee464ccbc65fc927ef1de40be5ef34c8**；profile.sb.tmpl SHA **76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f**，均与第1段钉版一致。旧r12 `R-M2-TEST-01` 审查准备错误在新请求已纠正，旧失败证据仍保留，不作为本候选业务缺陷。

## 原缺陷复核与本模块修复清单

### D-M2-01 — P1 / 必修 / 原生仍 FAIL：不同旧备份与宽容解析仍会覆唯一来源

- **文件/行**：source:539–607，特别 :549–556、558–571；启动saveState :12957。
- **触发A**：H/corrupt_view_stale_readable_backup；坏state完整原文为`[BROKEN_VIEW_REVIEW_R2_0002\n独立原文必须保留`，已有bak为`OLDER_UNRELATED_BACKUP_REVIEW_R2_0002\n`。
- **实际/预期**：实际主被默认偏好覆写，bak仍旧文，jail所有文件未找到本次完整原字节；磁盘status却称“原文已备份”，可见登录页无异常。预期新旧来源都留存、本次备份写/读回成立后才允许覆主，否则冻结并告警。
- **触发B**：H/truncated_nonempty_view，原文`{"pending_input":"独立非空截断原文", "search":"原搜索"`缺闭合大括号。
- **实际/预期**：实际partial对象被接受，主改为完整默认state，没有任何boot-bak或其它完整原字节来源，status准备就绪。预期首先识别完整合法JSON；部分字段恢复不能代原文保源，也不能静默认正常。原pending_input部分保留不抵消丢失整个来源与异常事实。
- **根因/影响**：对象类型门禁不等于严格JSON完整性；可读旧bak不等于本次备份。失败恢复会丢原输入/意图来源，直接阻断硬5/U07/G0-C。
- **证据**：B对应场所有前后文件摘要/原字节搜索、state_fields；H两场seed对照/最终state/bak；V同哈希帧；source上述分支。置信度高，原生已独立复现。
- **具体改法**：先严格验证完整输入对象；损坏/截断一律保原全文。已有bak与本次原文全等才认可；不同则保旧另存新原文并独立读回，失败冻结。可见提示必须对应真实来源保护，不让普通准备就绪覆盖异常。
- **验证方式**：重跑两失败场及新bak/目录bak/相同bak/正常中文意图；逐文件核两来源、动作键与字段，验证0运行错误和真实可见恢复出口。不修已通过的目录bak保源/字段类型兜底。

### D-M2-02 — P1 / 必修 / 实际按钮的未知与历史结果仍未闭合（源码FAIL，动态NOT_RUN）

- **文件/行**：source:6827–6850、7049–7063、7197–7217、7274–7276、7744–7804、12109–12120。
- **完整链**：draft_submit_btn→editRawText→confirmDraftModelBound→createDraftFromPanel/confirmDraft→任务/回执/事件/历史核验→外层布尔值→成功/失败UI。
- **触发A/实际**：空面板有当前主体原意图，内层给非nil unknown；外层只判nil即true，按钮显示已确认/OPEN。预期 unknown保输入/原键并对账，绝不能成功。
- **触发B/实际**：有内容重试且原确认已成功、任务合法到ACCEPTED/v9；内层历史成立但confirmed_open=false，外层仍要求OPEN而拒。预期返回原action/完整原result，另显当前状态，不重做。
- **根因/影响**：下层新增历史/未知协议没被上层消费；历史helper还只返回action_id，完整original_result没有贯通。这是核心假成功/错误重试缺口，不是文本建议。
- **证据边界**：source明确分支；B/C仅证明输入意图冷恢复和未登录不自动执行。本轮没有通过认证按钮制造假成功，**不虚报原生重复工单或历史误拒已经动态发生**。
- **具体改法**：统一结构化outcome=new_commit/historical/unknown/rejected；完整权威原action/result与当前task分开；空面板也核outcome，历史成功不要求当前OPEN。成功提示只能来自完整权威成立结果。
- **验证方式**：真实按钮有/无内容两条路径，正常重试/跨状态/同键异参（所有占用状态）/v9查旧v1/新独立意图；核task、action、event写次数、原键/结果与UI。不可用伪SESSION绕过合成账号认证。
- **认可修复**：创建任何占用状态同key异参拒绝、原意图持久、历史helper实际接入，保留改善，不重复原“无消费点”指控。

### D-M2-03 — P1 / 必修 / 完整关联提交恢复仍不足（源码FAIL，精确动态控制BLOCKED）

- **文件/行**：source:4796–5041、1024–1056、5059–5209，特别 :5018、:1044。
- **触发**：任务主写后/final前终止；事件失败且降级回执保存也失败；清tmp失败note保存失败。
- **预期/实际源码**：预期T22完整关联事实无业务部分提交，故障恢复能查原action而不重做；实际普通tmp/主覆盖/final/释放锁后另存事件，持久pending没有完整after，boot只能记未知；后续保存结果仍有未消费出口。没有可实证的共同恢复提交协议。
- **根因/影响**：局部读回和try/catch不能代跨文件关联一致性；可能留下任务/回执/事件不齐，无法充分对账。**本轮启动夹具未注入这些认证提交点，不声称已实测部分业务提交或假成功**。
- **证据**：source完整链；r10作者也没有精确点运行；本请求只launch/capture、schema不含中途故障控制。A/B中的冷迁移不是事务中断测试。
- **具体改法**：持久可恢复的action/before/after/event关联信息，所有写/降级/读回结果必须消费；完整事实未齐不报成功，失败要能收敛或明确未知并有原动作查询路径。
- **验证方式**：pending/tmp/main/clear-tmp/final/event/降级写逐点失败，读回失败/丢响应，同Store重开原key核完整事实且不重复写。只在harness控制边界表达故障，不让审查方自启/kill宿主。已有pending保存截断/释放锁、清tmp/读回catch、完整比较改善保留。

### D-M2-04 — 原源码根因修复认可；认证完整对账尚未通过

- source:4993、5140–5152实际完整after.to_json比较，历史helper已被真实函数消费；原三字段相似判成功根因不再成立，**无需重修这些比较**。
- 本轮unknown_history_no_session的回执/事件/任务没有自动改变，未登录负例PASS。认证后三字段相同而完整after不同、完整匹配、缺rid、读回丢失、较新版本查询仍NOT_RUN。
- 外层及完整原结果不足归D02，避免把同一根因重复算新P1。此条不宣称完整动态闭合。

### D-M2-05 — P1 / 必修 / 非原子竞争边界仍未改（源码FAIL，真竞争控制BLOCKED）

- **文件/行**：source:4421–4505获取锁、4835起提交前复查至主写。
- **触发交错**：A/B同权威盘先读空；A写核自己token及旧版本后暂停；B写核自己token/旧版本；随后双方继续主写。
- **预期/实际源码**：预期真实一赢家、一承接者/一成功action/event；实际普通读→写→读回及提交前复查到主写之间无原子线性化点，HOST_PRIMITIVE_BLOCKED仍在。**不是本轮真实双赢家实测**。
- **根因/影响**：同owner token/版本复核缩小窗口却不实现跨上下文互斥，核心T04/硬2保证不成立；version++/读取stamp不能代实证。
- **证据**：source边界；harness:581–610每场fresh独立Store；schema seed只允许复制路径，没有共享Store双上下文/屏障。18串行CLEAN不代竞争。
- **具体改法**：固定宿主实证原子锁/CAS或唯一可信写者，所有旧/新写入口归同线性化边界。
- **验证方式/解阻条件**：在受限harness提供真正独立认证上下文同权威Store同步竞争、崩溃回收；核一承接者、一条成功action/event与双方UI，不能两Store副本或串行。无需Abram重新决定身份/provider授权。

### D-M2-06 — 原根因保持关闭；旧入口完整项未代签

source:898状态白名单原修复保持，没有新P1。本轮未实际调用旧Web/MCP/runner/graph/reset，T24完整项NOT_RUN。后续只补相关绕过验证，不扩改旧契约或下一模块。

### D-M2-07 — P1 / 必修 / 错误非空JSON仍被接受为权威历史（原生FAIL）

- **文件/行**：source:1075–1088逐行门禁、1691–1725主/bak解析、1727–1935迁移；错误行从两次宽容parse进入parsed/主写。
- **触发**：H/braced_invalid_nonempty_record，两条合法历史之间夹`{"action_id":"rv-invalid", "result":}`，有合法旧bak。
- **实际/预期**：实际迁入三条数组，其中中间项成`{"action_id":"rv-invalid"}`，result被丢弃；state显示“迁移3条receipts（旧NDJSON→array）”，无bad_lines/登录告警。预期拒绝整个非法来源，主/旧bak保留、诊断真实、业务历史写冻结；不能把修剪字段后的对象当合法记录。
- **根因/影响**：大括号首尾+宽容parse非空对象不等完整合法JSON；记录门禁也没有阻止这条残缺对象。权威历史被污染且迁移假成功，破坏回执/恢复可靠性，属于原D07未闭合，非新模块扩审。
- **证据**：B.actions_parsed[1]、H该场主/原seed/旧bak/legacy2.bak/state/log/frame；V正常无警告图；A确认同候选/加载真实。非法完整原文在legacy2.bak保留，不夸大成原文全部丢失；失败在于它被接受为主事实。
- **具体改法**：主/备份/整体数组/NDJSON统一使用能完整消费文本并拒绝缺值/截断/尾随垃圾的严格JSON校验，再按兼容的历史记录schema核必要字段；不能靠首尾括号、非空对象或宽容解析成功。拒绝后保原文并给真实诊断/冻结出口。
- **验证方式**：精确重跑该错误行，补缺值/截断/尾随垃圾，保持合法空/单/多记录、旧bak共存与缺主恢复正例。字段及嵌套结果必须逐项相同，非法行不能被缩成新对象。
- **认可改善**：本轮普通截断/空对象拒绝、diag不可写停恢复覆盖、读失败保源/真实可见出口都PASS子项，不要求重修已成立部分。

### A-M2-r13-01 — P2 / 建议挂账 / 某些恢复状态未进入可见登录页

- 文件/行：source:1908–1910备份失败只返回状态，refreshDesktop:12872–12874只消费M2_RECOVERY_NOTICE。
- migration_backup_directory的主原文已保留，盘state如实记失败，登录页仅“请输入账号和口令”，没有迁移失败出口；新bak恢复提示也只在盘status而不显示。
- 建议在所有恢复/备份失败出口统一设置可见notice，并保留原输入。核截图与真实文件名，不能只看state.status。此项没有本轮业务丢源/假成功证据，**按用户完成优先裁决列建议，不单独导致FAIL**。D01/D07的实际丢源/非法迁移仍是P1。

## BLOCKED / NOT_RUN 的具体边界

本轮 **没有ABORT**，正常冷开/迁移/保源场景均已执行，按实际PASS/FAIL判定，没有记环境BLOCKED。

仅以下动态控制无法由当前允许的白名单动作覆盖：

1. **认证输入控制**：固定宿主 SHA同本轮的历史实证 `M3/native-runs/review_r2_0937_REQUEST_review_r2_0937/restore_unknown_empty_arrays/logs/host.log:40–41` 明确拒识`type:`/`key:`；当前schema也注明这一限制。原用户本次指令禁osascript/辅助功能/自动化，本请求没有ui_actions；tap/capture不能输入独立测试账号口令。认证动态检查是NOT_RUN；其输入控制缺口可记BLOCKED，**不是登录产品已坏的证明**。解阻需要在同harness边界提供当前授权可用的真实输入控制，不能预装伪SESSION。
2. **精确提交故障/丢响应/连续同Store重开**：schema无写点屏障、故意中断或复用同Store生命周期操作，内置动作只有UI/launch/capture等。相应动态控制BLOCKED；源码D03仍单列FAIL。解阻是受限控制能力及完整恢复协议，不能拿fresh冷seed当真实中断恢复。
3. **真正同盘竞争**：harness每场复制独立Store，没有两个独立主体对同盘同步屏障的请求机制。此动态控制BLOCKED；源码D05仍单列FAIL。解阻需要共享权威Store双上下文控制和原子写者边界。

其它没有执行的业务项如SSE、配对/grant、旧入口完整负例如实NOT_RUN，不因未选择场景就笼统称BLOCKED。没有重新拿Codex沙箱内rc71/rc3作理由；上述技术缺口均不是NEEDS_ABRAM授权阻塞。

## 相关既有验收：保留17项映射

|用例|本轮准确状态与覆盖|
|---|---|
|G0-B|NOT_RUN完整可信主体/授权与原课程助手项；伪持久会话不自动登录PASS子项；provider延期M3|
|G0-C|FAIL D01/D03/D05/D07；部分坏源/读失败冻结出口PASS，其它否定路径NOT_RUN|
|T02|FAIL源码D02；认证同键创建/异参冲突/独立动作NOT_RUN|
|T04|FAIL源码D05；实际同盘独立连接同步竞争控制BLOCKED|
|T15|NOT_RUN旧版本拒绝/刷新/输入保留/任意百分比负例|
|T16|FAIL源码D02/D03相关；实际丢响应同key返原action/不加版本NOT_RUN|
|T17|NOT_RUN断线重连/全量事实回读，不用fresh冷开代SSE恢复|
|T18|NOT_RUN可信权限的列表/搜索/事件/附件完整矩阵|
|T22|FAIL D03及本轮D01/D07恢复；合法迁移/部分保源PASS子项，逐提交点故障控制BLOCKED|
|T24|NOT_RUN完整旧入口/graph/reset负例，D06原状态守卫根因保持关闭|
|T29|NOT_RUN grant关闭/退出/到期/共享卡授权生命周期|
|T32|NOT_RUN配对过期/重复消费/poll_secret/审批/token边界|
|T37|FAIL源码D02外层未知/历史；D04完整after比较认可，认证对账NOT_RUN|
|U03|NOT_RUN同任务三独立主体事实/权限/自验拒绝|
|U07|FAIL原生D01、源码D02；正常输入/意图/key冷恢复PASS子项，实际双击/超时/冲突/离线NOT_RUN|
|U08|PASS部分state/events/actions失败告警子项；备份失败告警FAIL建议挂账；完整其它UI项NOT_RUN|
|T28|PASS同候选原生打开/登录页子项；FAIL本轮失败恢复；认证操作回读/同Store重开NOT_RUN|

不删除原38业务/12UI/P0，不把历史后端测试覆盖成当前原生PASS。ACCEPTANCE.json保持原样，本轮范围在GATES.review_acceptance分项记录；既有来源留在review_history与旧报告。

## 判定与交接

- **最终结论：FAIL**，精确适用 **M2-r10-worktree / 244a180c… / 04492599…**。
- **必修**：D-M2-01、D-M2-02、D-M2-03、D-M2-05、D-M2-07。前两项源码/动态范围分别标清，D01/D07已有独立原生失败；D04/06认可原根因修复，完整动态验证不冒称通过。
- **建议**：A-M2-r13-01，不用于FAIL。单纯UI完善/更全面呈现建议不扩成其它模块工作。
- **修复顺序**：先修并原生复验已独立失败的D01/D07，保持冷开0错误；再贯通D02结果协议；以D03恢复协议和D05原子边界补上真正执行保证，并准备受限harness所需控制。严格按上述原编号，不重做已通过子项，不改布局或下一模块。
- **前置回归**：冷开/登录渲染/正常输入恢复子项有实证，完整M1仍FAIL、未代签其它模块。当前后续工作树未被本候选验收。
- **门禁位置**：`docs/optimization/2026-10-09-desktop/GATES.json` 的 **M2 status=FAIL、review_report=本报告**，保存旧r12审查字段历史；候选及作者字段保持不变。E/GATES.before-r13.json保存更新前态，门禁局部变更另核。
- **是否允许下一模块：否**。不提供下一模块入口、不执行下一模块。
- **NEEDS_ABRAM=no**：身份/provider/离线签名已有裁决，剩余是技术修复与控制能力；无公开发布需求或MiniMax计费失败。

STATUS=FAIL
NEEDS_ABRAM=no
