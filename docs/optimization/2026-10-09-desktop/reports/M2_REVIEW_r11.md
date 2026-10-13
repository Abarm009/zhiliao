# M2 独立 Review r11

**最终结论：FAIL。** 对明确交接的 **M2-r9-worktree** 独立运行11场，隔离/回收全部CLEAN，正常冷开的原生登录页可渲染，中文输入、原意图及合法历史恢复已有实证改善。但截断历史仍被先改写再冻结，诊断失败仍丢坏源，损坏视图原文被覆盖且产生运行错误；幂等冲突、关联提交、原动作证明和原子竞争的原核心缺陷也未全部关闭。本轮只审M2，不修业务，不进入下一模块。

## 审查范围与候选

- 审查者/日期：本主会话唯一审查者，无子代理，2026-10-13，Asia/Shanghai。无法核验指定Router主会话实际模型，未声称已切换；缺少自身createdAt/线程标题工具，未声称已完成命名。
- 两段式：第1段笔记 `runtime/optimization/2026-10-09/M2/native/REVIEW_NOTES_r1_0002.md`；独立请求 `M2/native/REQUEST_review_r1_0002.json`，SHA-256 **08f75214087cfd5773b19225dbdedf879571b631577a999279aefec371de75b5**。驱动在agent沙箱外执行 **00:32:59–00:35:51 +08:00**；第2段核证据并判定。审查者没有启动launcher/harness或进行sandbox-exec/pgrep预检。
- **受审候选：M2-r9-worktree，声明base=M2-r8-worktree**。由用户明确交接的build_r1_0002_REQUEST_build_r9、r9实施报告、snapshot、请求与运输包定位，不按mtime选版本。
- HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty；main **642733 B / SHA-256 a5bca2f3e876535a8a418b032acc08f604cb8fe57c6f845f6cf3a8a07a5f27ac**；签名bundle digest **ee14dbb9f3fd532c7b4cf2128249ca688bb6d5384f3427f93a4f7fecb078b562**。当前工作树main、冻结mirror、installed和各场唯一.running全部资源一致。签名manifest与工作树未签manifest分别核，不混用二者摘要。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r9.md`。作者补丁 `M2/r9/main.splash.diff-a9-to-r9.patch`，5006行，SHA **0a93e3f0066d04616a7d5ab5a964b9edb980b47bb1cfd7082e57d15b981f2eee**；含他人/其他模块变化，未把全部差异说成M2本轮自有修改。上一轮r10受审main为a9acd344…；同HEAD不等于同内容。
- 前置：**M1仍FAIL / M1-r2-worktree / M1_REVIEW_r2.md，没有已接受的M1 PASS**。按本轮前序挂账与完成优先约束继续M2，未修M1、未制造前置PASS；针对原生根、未登录保护、偏好/恢复做回归。
- 固定宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness SHA **d597d24ae0a14989f58b022786390916fac2b8fe0a24b11499db2a0d5c4895da**，template SHA **80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7**。
- 阅读：AGENTS、CONTEXT_M2、00/01/02/M2/04、r9实施报告、r10缺陷清单、固定源码/交接差异、原17项定义、schema/harness及本轮完整运行证据。修复轮只核原D01～07与受影响回归，不无关扩审。
- 实际运行：驱动11场独立冷开、历史迁移/读取和诊断失败、伪保存主体负例、原生截图/退出。审查脚本只处理既有证据文件；运行夹具均为自造隔离数据，五主体账号KDF全部重新随机生成。
- 未运行：成功/错误口令登录、可信双主体权限矩阵与撤权/到期、认证创建/重试/跨状态/同键冲突/历史查询、真正同盘同步竞争、每个业务提交写点中断/响应丢失、持续同Store重开、旧外部写入口实际负例。
- 置信度：候选/证据一致性、实测源丢失和明确源码分支**高**；错误值从parse到具体视图字段的内部传播路径**未知**；认证命令、真正竞争与逐提交点故障的动态结果**未知/未运行**。

下文 **H/**=`runtime/optimization/2026-10-09/M2/native-runs/review_r1_0002_REQUEST_review_r1_0002/`，**E/**=`runtime/optimization/2026-10-09/M2/native/review_r1_0002/`。**A**=E/native-evidence-audit-r11.json，**B**=E/business-observations-r11.json，**C**=E/business-detail-r11.json。

源码行号指 **E/source.main.splash**（a5bca2f3…冻结副本，与本轮app/bundle/main.splash同字节）。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/证据完整性|重算请求、236个seed文件、宿主、harness、profile、包全部资源与MANIFEST|同候选且完整|1806项清单完整匹配；各场mirror/installed/唯一.running同冻结包；保护输入一致|PASS，证据范围|A、phase1-start、seed-manifest、final-verification|
|隔离/回收|逐result核probes/pre/post/进程组/env/profile/denials/files_written|写限新场景、禁读生效、无残留|11场probes.ok=true，pre/post NONE，pgid_members_after=[]，CLEAN；无ABORT|PASS，harness范围|A；H各result/profile/denials|
|原生根与受影响回归|目视所有不同PNG，全文日志，核业务eval与tick|正常冷开可渲染，失败不抛运行错误|11场view=true、登录页可见；10场0[E]，损坏state场1条to_chars错误；tick异常计数均0|正常根PASS；失败恢复FAIL|A、B；H/corrupt_view*/logs/frames|
|硬1：原key、异参、独立意图、跨状态|新夹具冷开保留输入/意图；追真实提交按钮至事实源；核unknown/历史源码|原action完整结果，不重复执行；任何占用同键异参拒|正常输入/意图冷开保留；unknown异参仅final冲突，真实历史链仍要求当前OPEN；认证重试未跑|FAIL，D02源码；持久子项PASS|B/C；source:6963–7108、7548–7652|
|硬2：权限/旧版本/真正竞争|伪actor/session+unknownv1/currentv9负例；核会话/同盘锁交错|伪主体无权限，陈旧/撤权拒，同盘竞争一赢家|11场任务/合成账号未变、登录态未冒用；普通写后读回锁仍无原子边界；真实主体矩阵/竞争未跑|FAIL，D05源码；未登录保护PASS|A/B；source:4337–4407、4751–4864|
|硬3：中断一致提交|注入events目录、diag目录、截断历史；核pending/主/final/event代码|坏源保留、失败关闭、无部分成功|pending返回消费改善；独立坏源仍丢、坏历史先改后冻；完整关联提交未关，精确业务写点未跑|FAIL，D03源码/D07实测|B/C；source:1752–1794、4751–4934、999–1030|
|硬4：未知结果对账|未登录原final/unknown/currentv9负例；追认证恢复和历史调用|核原动作完整事实，保持原key，不重复写|未登录回执原样PASS子项；恢复仍只比三字段，历史helper无消费；认证对账未跑|FAIL，D04源码|B/C；source:5010–5034、7596–7652|
|硬5：输入/任务/历史恢复|11个新场景比较完整主/bak/diag/state和PNG|保留输入/历史来源，严格迁移，真实可继续|正常中文/意图和合法迁移PASS；坏历史被改、diag失败丢坏源、坏state被覆并运行错误|FAIL，独立原生|B/C；H对应jail/log/PNG|
|D06与旧入口回归|逐字比较sourceOk和r10冻结函数|原白名单根因不回退|函数相同；旧Web/MCP/runner/reset真实负例未执行|D06保持关闭；完整T24 NOT_RUN|E/phase1-checks；source:873|

### 证据审计范围

1. 审核 **7661项证据一致性检查，0失败**；不是7661个业务测试。MANIFEST **1806项** 摘要、路径范围、唯一性及完整文件集合均匹配；summary.request与独立请求精确一致，逐场summary/result字段对应。
2. 11个profile按模板、各场路径、记录中的真实HOME和控制端口重建后逐字一致；profile摘要匹配。只核驱动记录中的禁读探针，不在审查环境读取禁读目标。HOME/app-data/cache/tmp等12个路径环境变量都限各自场景。MAKEPAD_HIDE_WINDOWS=1、MAKEPAD_REMOTE为控制端口，未误判为路径。
3. 每场 **14.17–14.42秒**，host rc0、quit_http；pre/post NONE、最终进程组空、real home mtime前后一致、library_scan_new_or_modified=[]。files_written为 **126–129项/场**，数量、唯一性、排序、每项存在及范围核实；它是驱动按mtime形成的清单，不能称业务提交次数或全系统写调用审计。
4. 所有seeded_files与原独立seed/mirror摘要匹配；236个源seed文件未变。各场mirror、installed及唯一.running的完整文件集合/字节均等于冻结运输包。tasks.json与合成账号表全部原字节未变，没有本轮认证业务提交。
5. **22张PNG、3种不同字节图像**，摘要与尺寸核实，3种内容全部目视（每组字节相同的其余图映射见A）。均为 **2800×1696** 全屏图中的原生登录页。1280×800是启动参数，不将PNG全屏尺寸称为完整尺寸验收。图中只见登录提示，未见历史/备份/损坏state恢复错误；不能用这些图证明已认证工作台或可靠业务流。
6. 全文11份host.log，host_log_bytes/tail/markers重新计算一致，业务eval均 **642733 B view=true**；809 B为其它宿主视图，不混算。**损坏state场实际有1条[E]**：`splash:50129993728:1891:23 - method to_chars not found on error`；其余10场0条[E]。无panic/未知test-action。tick_exception_count=0不能抹掉这条日志错误。
7. 全文sandbox-denials与汇总按harness相同正则重算一致；包含443外联、Metal缓存、/dev/dtracehelper被拒。拒绝尝试不是成功外联/越界写；各时间窗口日志可能重叠，未把汇总当独立精确系统调用总数。
8. needs_model全false，env无MM_KEY/代理endpoint，**model_proxy_stats在result中缺省**，不是虚造一个零请求对象。未启动模型代理、真实模型调用0、无billing_error。G0-E为**延期缺口（Abram已裁决，M3到期）**，不计本轮FAIL/BLOCKED或NEEDS_ABRAM。
9. 本轮复用已签同digest本地Store；新私钥0生成。作者私钥删除记录及keys目录为空已核；本地安装/运行可用，完整hub check资产扫描拒绝仍挂账，不宣称公开准入/发布通过。

审核脚本第一次把“业务不得有[E]”混入证据一致性断言，因此在真实损坏state错误处失败。已将“日志记录是否一致”与“业务是否无错误”分开重新执行：最终证据一致性0失败，**实际产品错误仍保留并列D01**，未通过删异常来取得业务PASS。

## 权威盘面：逐场实测

正确业务jail为 **H/<场景>/home/.octosense/apps/octosense-repair/**。所有场tasks/合成账号原字节不变。以下迁移/加载结果不代认证业务事务故障注入。

|场景|独立实际结果|判定范围|
|---|---|---|
|restore_intent_and_empty|中文换行、confirm_intent_id/完整意图/key map保留；actions/events均原[]；actor/session不恢复|D01/D02正常持久与D07空数组PASS子项|
|single_ndjson_valid_backup|完整1条迁成数组，全部嵌套/result字段等价；旧bak原字节不变，legacy2精确等于原主|D07单条/备份PASS子项|
|four_ndjson_stale_backup|完整4条迁成数组；旧bak不压主且不变；legacy2精确保留本次原文|D07多行/主优先/备份PASS子项|
|malformed_object_ndjson|截断对象→{}，主变为[完整头,{},完整尾]；bad_lines等于修改后的主，legacy2保留原坏文；随后冻结|D07 FAIL：先假迁移再冻；本场原文另存存在，不能误称本场已丢唯一原文|
|invalid_array_error_priority|非法actions原字节及bak保留；diag与原文相同；合法events正确迁移，state仍显示actions冻结|D07非法数组/错误优先PASS子项；登录页未显示该恢复错误|
|missing_main_full_ndjson_bak|主正确恢复为完整4条数组，与原NDJSON所有字段等价；bak字节保留|D07缺主恢复PASS子项，不再沿用r10“缺主仍缺”|
|event_read_and_diag_failure|events与bad_lines均仍为目录；backup不变；盘state明确读取失败、冻结、人工检查|D07读取故障盘面PASS子项；恢复提示在未登录截图不可见|
|bad_source_diag_write_failure|坏events被合法bak规范数组覆盖，bak不变；bad_lines仍目录；原坏源字节在整个该业务jail无匹配；state仍为旧sentinel|D07 FAIL：诊断失败仍丢坏源且错误无真实反馈|
|corrupt_view_backup_unwritable|损坏state被普通JSON覆写，boot-bak仍目录；原state字节在业务jail无匹配；status等字段null；日志1条to_chars错误|D01 FAIL：失败源未保护，运行错误；未虚称日志显示“备份成功”|
|unknown_v1_newer_v9_no_session|任务v9/6条原回执精确不变，未登录没有补事件/认证恢复|未登录保护PASS子项；认证D04与历史查询NOT_RUN|
|minimal_view_preferences|中文输入保留、actor不恢复、根可见、0[E]；部分缺省偏好/意图字段保存为null|正常输入PASS子项；缺字段默认完整性列建议，不单独判FAIL|

所有有saved task_id的场最终selected_task_id变为空。未登录视图没有可见任务，**不将此直接列为丢任务/权限缺陷**；任务盘本身原字节完整。登录后同ID选择恢复尚未测。

## 缺陷：按上一轮编号，只有核心问题列P1必修

### D-M2-01 — P1 / 必修 / 部分关闭：损坏视图恢复仍覆原源并报运行错误

- **文件/行**：main:535–582 loadViewState；:944–955 saveState；:1891 _textLenSafe；:1446/:12744加载与重试。
- **触发**：隔离state原文`[BROKEN_VIEW_RV_0002`，state.json.boot-bak预置为目录，固定宿主冷开，不点击业务按钮。
- **实际/预期**：原文被覆，业务jail找不到原字节，可读备份不存在，状态字段null，真实日志出现to_chars not found on error；预期严格确认视图对象/字段类型，失败保原源、备份写读回真实成立后才继续，错误有可用出口。
- **根因**：源码仅把parse==nil当失败，不验证对象/字段；损坏分支吞备份写失败且未核已有bak可读性。固定宿主具体错误值内部传播点未注入探针，未知，不把猜测当实测。
- **影响**：恢复失败覆唯一来源、错误值进入UI辅助函数，违反“失败/重启不制造假成功和输入来源可靠恢复”。旧空白/正常解析问题与正常中文/原意图持久已改善，本轮不要求重修布局。
- **证据**：B/C/corrupt_view_backup_unwritable；H同场原state、最终state/bak目录、全文log/PNG；source。
- **具体改法**：严格可恢复对象/字段门禁；读/parse/备份写/备份读回结果显式消费，失败不放开默认值覆盖；已有目录/坏bak不得视为成功备份。UI只命名实际可读来源。
- **验证**：正常中文/原意图仍保留；缺字段安全默认；错误值、截断state、bak目录及备份写失败均原文保留或可验证另存，0运行错误；认证后同任务选择/输入恢复另实测。

### D-M2-02 — P1 / 必修 / 部分关闭：unknown异参与真实历史重放仍未贯通

- **文件/行**：main:6963–7108，重点:7033–7040异参；:7434–7498；:7548–7652；外层:6720–6737与按钮:11958。
- **触发**：原createDraft为pending/needs_verify，同key改payload；或原confirm final之后任务合法到ACCEPTED/v9，再由真实按钮/确认重放查原动作。
- **实际/预期**：异参只在final/final_recovered冲突，unknown继续恢复/确认；盘无task可orphan后同键使用已改内容。`_authorityHistoricalConfirm`存在但无实际消费，真实调用仍要求当前OPEN。预期任何占用同键异参拒，原action完整结果独立于当前合法状态。
- **根因/影响**：状态特判漏unknown；未使用的helper代替真实调用收敛；外层原文/草稿前置可能阻断冷开内层意图重试。可误确认未确认内容/误判旧成功；**本轮未发生认证重复工单，不写成实测事故**。
- **证据**：source完整分支/按钮链；B正常持久已PASS，unknown无会话保护不代认证重放。
- **具体改法**：unknown先核不可变payload并拒异参；把按精确原action查询接入实际按钮/重试链，返回完整原result，另读当前task；新独立意图与原动作重试明确区分。
- **验证**：正常重试、跨状态、final/unknown同键异参、同内容独立新意图、v9查原v1；核原key/action_id/result及任务/事件写次数。持久意图本轮已证子项不重复改。

### D-M2-03 — P1 / 必修 / 部分关闭：完整关联提交与逐写点恢复未成立

- **文件/行**：main:4751–4934 commitBound（清tmp:4890附近）；:999–1030 logEvent；:5077–5111补事件；pending:5171–5204/:7197–7224及caller:7536。
- **触发**：task主写后清tmp/final/event间异常或中断；事件保存失败后的降级回执再失败；读回异常。
- **实际/预期**：tmp→普通主覆盖→未catch清tmp→仅version/status读回→final→释放锁，事件后置另存。局部保存返回不构成共同提交/恢复点。预期task/action/event完整可恢复关联、原key不丢、事实不足未知而不成功。
- **根因/影响**：缺完整持久提交协议/动作归属事实，各文件和降级路径可部分提交。认证写点故障本轮未跑；启动历史/diag失败不冒充事务中断。
- **已关子项**：recordReceipt保存返回已消费，失败截断内存；创建pending失败不push TASKS、释放锁。认可，不继续沿用“忽略pending返回”指控。
- **证据**：冻结source；第1段完整追踪。动态关联提交结果未知，不用函数命名或作者Python契约测试补PASS。
- **具体改法**：统一持久before/after/action/event关联协议，消费每个写/清理/读回结果，崩溃后依原action收敛；完整事件与回执真实落盘才显示成功。
- **验证**：pending/tmp/task/clear-tmp/final/event各点异常与中断、丢响应、同Store重开；核盘/回执/事件/双方UI，不重复业务写。精确控制缺口见下文BLOCKED范围。

### D-M2-04 — P1 / 必修 / 未关闭：三字段仍代完整原动作证明

- **文件/行**：main:5010–5034恢复after比较；:4894–4905提交读回；:7596–7652历史函数/真实消费。
- **触发**：另一动作也使expected+1且同status/assignee，但problem/asset/appointments等完整after不同；或原final v1后当前v9。
- **实际/预期**：只比version/status/assignee就final_recovered；历史真实链要求当前OPEN。预期证明精确原action和完整结果，不能证实就未知；合法后续状态不抹原历史。
- **根因/影响**：字段相似性替代提交归属与完整事实，可能把无关动作当原成功。注释“after全等”不等于实际全等。
- **证据**：source；B/C/unknown_v1_newer_v9_no_session的6回执原样仅证明未登录保护，**未触发认证恢复，不称动态已误判final_recovered**。
- **具体改法**：持久唯一提交标识、完整before/after与关联事件；历史action精确查询与当前task独立返回。
- **验证**：同三字段异完整after保持unknown、真实相符收敛、缺rid不假成功、v9查原v1、写成功读回失败再查不增业务次数，必须经可信认证执行。

### D-M2-05 — P1 / 必修 / 技术缺口未关闭：普通写后读回没有原子竞争边界

- **文件/行**：main:4337–4407获取锁，:4408起释放；:4751–4864提交复查；:7182起创建同锁。
- **触发**：A/B同盘均先读空；A写/读回自身stamp并完成最后锁/版本核对后暂停；B写/读回并核对，随后双方写相同旧版本派生的任务与历史。
- **实际/预期**：普通read/write/readback与最后复查之间没有原子线性化点；预期仅一承接者、一成功接单action/event，不丢历史。
- **根因/影响**：缺实际原子锁/CAS或唯一可信写者，仍标HOST_PRIMITIVE_BLOCKED。存在双赢家/覆盖风险；**这是可成立的源码交错，不是本轮真正竞争实测**。
- **已关子项**：创建已入同锁、完整token所有权、提交点盘版本复核保留，不要求重复修这些项。
- **证据**：source及schema/harness逐场fresh Store串行循环。11场CLEAN不代双上下文同盘竞争。
- **具体改法/解阻**：在固定宿主验证原子原语或唯一可信写者，所有入口用同边界；补真正独立会话同权威盘同步竞争及崩溃回收能力。不能继续把write-verify称互斥完成。
- **验证**：实际同步屏障双上下文接同OPEN任务、核一个赢家/承接者/成功事件及完整回执、双方UI。当前白名单/schema无法表达同Store双上下文同步，动态BLOCKED仅限此能力。

### D-M2-06 — 保持原根因关闭

sourceOk与r10冻结函数逐字相同，原源状态白名单修复无回退；无新P1。不把它扩大为旧Web/MCP/runner/reset完整负例通过。

### D-M2-07 — P1 / 必修 / 部分关闭：先假迁移再冻，诊断失败仍丢唯一坏源

- **文件/行**：main:1037–1044记录门禁；:1072–1146加载；:1629–1661主/bakparser；:1740–1794恢复坏源；:1808–1842备份/主写；加载:1504起。错误投影:12669–12681登录页切换、:12715认证提示。
- **触发一**：完整NDJSON头尾夹`{BROKEN_REVIEW_R1_0002`，已有有效bak。**实际**：主改为[头,{},尾]，bad_lines保存的是修改后的主，之后才冻结；legacy2保原文。**预期**：严格拒截断行后保护原主，不先按假对象迁入权威历史。
- **触发二**：坏events=`BAD_EVENT_SOURCE_RV_0002\n`，有效bak，bad_lines为目录。**实际**：diag失败仍用bak覆主，原坏源在整个业务jail无字节匹配、无可读diag；state维持旧sentinel，截图无错误。**预期**：唯一坏源保护成功前不覆盖，失败明确反馈，不谎称preserved。
- **根因**：数组用非空对象门禁，NDJSON仍只看对象形态，宽容parser的{}可进入迁移；坏源diag返回空不阻止恢复覆盖，分支仍返回corrupt_source_preserved:true。
- **影响**：权威历史含假记录；失败恢复破坏唯一原来源，无法可靠对账。丢失的是本轮合成坏源，**未改原业务数据**。未登录UI也没有展示相应恢复错误，不能据盘status认定可继续UI已接通。
- **证据**：B/C/malformed_object_ndjson、bad_source_diag_write_failure；H对应主/bak/legacy2/diag目录/state/log/PNG；source。盘文件和字节对照独立于应用输出。
- **已关子项**：合法[]、一行/四行全字段迁移、主优先/有效bak保护、缺主NDJSON bak恢复、非法数组冻结/错误优先、读取故障不指假diag均已有独立实证，保留结果，不让构建方重修。
- **具体改法**：数组/NDJSON/主/bak共用完整JSON与逐记录判据，先判后写主；diag/backup写+读回失败必须停止覆盖，真实记录保源失败；恢复错误接入当前可见原生界面。
- **验证**：本轮两失败场精确重跑；补NDJSON空对象/截断非空对象、diag/bak写读回失败，核原字节/全部来源/严格主记录和可见恢复出口；正常六个已通过子项定向回归。

### 建议挂账（不单独导致FAIL）

- 缺字段state的部分偏好被持久化为null，默认合并与字段类型门禁宜一并核验；当前minimal场无运行错误、输入保留，不单独列P1。
- 完整Hub check资产扫描拒绝继续保留已知来源；本地路径已成功运行，不转公开发布或新计费渠道。
- 身份来源/真实provider不需重裁决；认证输入、原key/payload、精确提交点、共享Store竞争及持续重开是实现/测试能力工作，不因它们主动请求新授权。

## 相关既有验收逐项复核

原38业务/12UI/P0及ACCEPTANCE.json历史不改。本轮以下结论只适用于a5候选在固定宿主的M2范围；源码FAIL与动态FAIL分开。

|项|结论|实际范围|
|---|---|---|
|G0-B|NOT_RUN|登录页/伪保存主体保护PASS子项；成功登录、双可信主体权限/撤权/到期矩阵未做；五账号来源已裁决。当前schema有ui_actions，不再声称绝无输入能力|
|G0-C|FAIL|D01/D07恢复实际FAIL；D03/04/05完整可靠提交/竞争未关|
|T02|FAIL|原意图冷开持久PASS子项；unknown异参、历史重放源码未关；真实创建重发与独立新意图未跑|
|T04|FAIL|非原子边界源码未关；真正同盘同步竞争BLOCKED于白名单/schema，未以串行代签|
|T15|NOT_RUN|可信主体陈旧version拒绝/刷新/保留输入、任意百分比负例未实际执行|
|T16|FAIL|正常原key持久PASS子项；未知/历史重放源码未关；提交成功丢响应动态未跑|
|T17|NOT_RUN|SSE断线/重连/全量回读未执行；白名单没有相应断线控制，不用fresh Store冷开替代|
|T18|NOT_RUN|未登录可见空态/伪主体保护PASS子项；独立可信主体列表/搜索/事件/附件矩阵未跑|
|T22|FAIL|历史/保源恢复独立动态失败；关联提交源码未关；精确提交写点中断/持续重开BLOCKED于现行控制|
|T24|NOT_RUN|D06原白名单无回退；旧Web/MCP/runner/graph/reset真实负例未跑|
|T29|NOT_RUN|grant关闭/退出/到期及共享卡实际授权生命周期未跑|
|T32|NOT_RUN|配对码过期/重复/poll_secret/审批/token边界未跑；账号表不代配对验证|
|T37|FAIL|三字段代完整原action证明、真实历史仍要求OPEN源码未关；模型声称成功与提交后读回超时动态未跑|
|U03|NOT_RUN|未登录保护PASS子项；同task三主体事实/动作/自验禁止未实测|
|U07|FAIL|正常中文/原意图持久改善PASS；损坏state来源保护FAIL；认证重复点击/版本冲突/响应丢失/离线完整链未跑|
|U08|FAIL|正常登录空态可见；恢复失败没有对应原生可继续反馈、损坏state运行错误；完整附件/建议等子项未跑|
|T28|FAIL|同字节安装/根可见PASS子项；失败恢复动态FAIL；真实操作→权威回读→同task持续重开未跑|

本轮 **harness无ABORT**。BLOCKED仅限现行白名单/schema无法表达的**共享权威盘同步竞争、精确业务提交点/响应丢失、连续同Store重开**。认证链未运行记NOT_RUN：不把本段选用launch/capture而没有认证输入，伪装成宿主绝无能力；亦不因agent内rc71/rc3作BLOCKED。当前明确禁自动化的约束保留，没有请求ui_actions。

## 判定与门禁

- **最终结论：FAIL，candidate=M2-r9-worktree。** 核心实测恢复失败和原P1尚未关闭；不因建议、模型延期、缺前序PASS或Hub完整形式检查单独判FAIL。
- **必修保留D-M2-01/02/03/04/05/07的剩余项**。闭合子项明确保留：正常输入/意图持久、pending失败关闭、合法空/1/4行历史与backup/缺主恢复、原白名单、创建同锁/完整token等。按原编号最小修，不改界面布局、不修他人模块。
- 构建方留在M2：先修两种保源失败与严格历史判据，守住正常可渲染根；再闭合unknown同键冲突、实际历史查询、完整关联提交与真实竞争边界。附新固定候选/差异和harness冷启动证据，认证成功与每个恢复结果分开验证。
- 技术解阻条件：原key/payload可控的真实认证操作、精确提交写点/响应丢失、同权威盘双上下文同步竞争、持续同Store重开。不要手工填SESSION或改业务状态制造成功链；未解决不PASS。
- 受影响前序：正常根/未登录保护保持可用；损坏state恢复失败；M1仍FAIL，未动其他模块。
- GATES只更新M2 status、review_report/reviewed_at及review_*，作者candidate/base/implementation字段不变；旧审查字段存入review_history。新报告指向本r11、review_candidate_id=r9，完整写前副本 **E/GATES.before-review-r11.json**。原ACCEPTANCE历史不覆盖，17项当前范围写本报告及M2.review_acceptance。
- 回读核验：其他模块/顶层/非审查字段不变；业务源码、账号/映射、原验收、宿主/harness、seed/mirror保护输入不变，见 **E/final-verification-r11.json**。
- 第1段误读项目外记忆索引已如实留在阶段笔记；第2段只用项目内资料，没有读明文凭据/provider密钥，没有项目外写入、原生自启动或网络/发布/消息操作。
- **NEEDS_ABRAM=no**：本地路径可用，身份/provider/离线签名已裁决，无402/欠费或公开发布必须事项。
- **不允许进入下一模块，只交本模块修复清单。**

STATUS=FAIL
NEEDS_ABRAM=no
