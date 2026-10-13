# M2 独立 Review r16

**最终结论：FAIL。** 适用正式交接候选 **M2-r11-worktree**。驱动独立原生运行 CLEAN，但合法原文恢复、合法历史加载、事务恢复屏障存在实际失败。CLEAN 证明隔离与进程回收，不证明业务通过。只复核原 D-M2-01/02/03/05/07 及受影响回归，不修业务、不进入下一模块。

## 审查范围与候选

- 审查者：本主会话唯一独立审查方；日期 2026-10-13（Asia/Shanghai）。主会话 Router/gpt-6.1-sol 路由未能确认/切换，未冒称满足；无子代理。当前线程 createdAt 与改标题工具不可用，未猜日期操作。
- candidate_id/base：M2-r11-worktree / M2-r10-worktree。依据指定请求、实施报告、GATES 与冻结清单关联，不依据文件时间。
- 作者报告：[M2_IMPLEMENTATION_r11.md](M2_IMPLEMENTATION_r11.md)。HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty。
- main.splash 765739 B，SHA256 `f74813fb6945f2aaad3e7ef4d4f63f3c88017cff757967e10bc9a985d373e0c2`；bundle digest `70d795d179a9829d01cda4d5b34976baf42cb6029639f599410c047824386a73`。
- 冻结 E/source.main.splash；E=`runtime/optimization/2026-10-09/M2/native/review_r1_1238/`。清单 E/seed-manifest.json，原清单 M2/r11/native-prep/snapshot-start.json。差异 M2/r11/main.splash.diff-r10-to-r11.patch 独立重建成功，基于 r15 **未接受工作树观察** `9869f8ad…`，不是此前接受候选。关联证据 E/candidate-evidence-relation.json。
- 两段源码、manifest、harness/schema、ACCEPTANCE 与写报告前 GATES 均同第 1 段摘要。运行 Store 20/20 的 main 摘要与冻结源码一致；报告行号对应此冻结候选。
- M1 仍 FAIL/M1-r2-worktree/M1_REVIEW_r2.md，原 PASS 前置不成立；按 Abram 挂账裁决继续局部复审，不改变其结论。本次冷启动回归有两场业务空白，不能认框架回归通过。
- 固定宿主 M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense；运行 binary SHA256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 已读：第 1 段 AGENTS/CONTEXT/00/01/02/M2/04、r15 缺陷、r11 报告/清单/diff、HARDFIX_PLAN；本段重核阶段笔记、真实运行证据、涉及缺陷的源码与模板。未无关扩审。
- 实际运行：驱动沙箱外独立 harness，2026-10-13 13:16:15–13:23:28 CST。请求 `M2/native/REQUEST_review_r1_1238.json`，SHA256 `3cc153e635773e74f7c44b3b028be55d8fcb063953291d90ad42f5c36066b25a`。本主会话只查文件/截图/源码并写报告和审查记录，没有自行启动 launcher/harness/sandbox-exec/pgrep。
- 未运行：真实认证按钮链、正常/跨状态重放/同键冲突/较新版本查原动作、撤权/到期、两主体真竞争、精确写点故障/丢响应、同 Store 连续重开。原因与适用状态在下文列明；冷 seed 不当成成功链证明。
- 第 1 段首条检索误读项目外 memory 索引的过程偏差已在阶段笔记保留；随后停止项目外访问，本段未访问项目外资料。全部产品裁定来自项目内本轮直接证据。未读取明文凭据或 provider secret。

## 独立运行证据与隔离核验

R=`runtime/optimization/2026-10-09/M2/native-runs/review_r1_1238_REQUEST_review_r1_1238/`。以下简写 `R/<场景>/` 均包含 result.json、frames/<场景>.png、logs/host.log、profile.sb、运行后 home/.octosense/apps/octosense-repair/ 权威文件。

|核验|实际|结果与范围|证据|
|---|---|---|---|
|请求/候选一致|summary.request 与提交 JSON 全等，请求摘要同第1段；20实际 main 同冻结；digest 出现在 seed，非靠日志字符串推断|PASS 证据关联|E/native-evidence-audit-r16.json|
|MANIFEST|3273 文件逐项 SHA256 匹配，缺失/摘要不符/额外未列文件均0|PASS 文件完整性|R/MANIFEST.sha256；E/audit 的 manifest|
|宿主/harness/profile|20宿主摘要同上；harness SHA `8141b4de…` 同第1段；20 profile 摘要与 result 一致|PASS 版本/隔离配置关联|R/summary、各 result/profile；E/audit|
|隔离与回收|20 CLEAN；probes.ok=true；pre/post_pgrep.class=NONE；pgid_members_after=[]；capture 全存在且摘要一致|PASS 隔离回收；不等于业务PASS|各 result/PNG；E/audit|
|文件写入|逐个 files_written_in_run_dir 路径均在本场目录，列表指向文件存在；全部业务 tasks.json 同 seed 字节|PASS 未越界/未擅改任务；不证明事务|各 result；E/audit authority_files|
|sandbox_denials|已逐场检查日志与摘要。可见宿主 osascript、/dev/dtracehelper、系统 Metal cache、外部443等被拒；无允许越界写证据，library_scan 无新增|PASS 已拒越界尝试；不拿拒绝本身作业务BLOCKED|各 sandbox-denials.log/result|
|模型代理|20 needs_model=false；各 result 没有 model_proxy_stats 字段，无 proxy 产物，无模型场景|NOT_RUN 模型；0个模型场景/无代理启动，不伪造stats=0|请求与各 result；E/audit|
|可见业务/UI|20主PNG均人工查看；19个part与主图字节相同，另一个rv_final_empty_result.part也已查看、仍同冻结状态；18有登录界面，rv_valid_history 与 rv_primary_over_old_bak 空白|FAIL 两合法历史结构场业务加载|PNG、host.log|
|日志|全部 [E]=0；两场 `[I] splash:` 运行诊断分别41/36条，包括属性缺失/作用域/空栈；其余18无提取到同类诊断|FAIL 运行错误，不能零[E]放行|E/audit runtime_diagnostics|

私钥：作者离线签名报告记录 anchor.key/working.key 删除，本段再次核 keys 目录为空；审查未生成私钥。签名 Store 与本地安装可定位；作者 hub check 的 assets rc1 保留为包检查挂账，不冒称全准入 PASS，不因此升级本轮新P1。未 publish/listing/push/部署/发消息。

## 必需检查与逐场结果

下表 PASS 仅适用明确列出的子项。所有场共享 state 正例未恢复，不能以反例保源 PASS 推导整场或模块 PASS。

|场景|独立输入/期望|实际权威盘、UI、日志|结论|
|---|---|---|---|
|rv_clean_unicode|中文/emoji/引号/换行合法 view、空历史；原文精确保留且无自动登录|登录可见、无VM诊断；pending_input 由非空原文变为空，state 被重写，无来源副本|FAIL 原文恢复；PASS 登录冷开子项|
|rv_view_missing_value|闭合缺值 view 拒信，覆盖前精确备份|坏源全文在 state.json.boot-bak；默认视图保存；登录可见|PASS 拒信/保源子项|
|rv_view_old_backup|截断当前源+不同旧 boot-bak，不覆盖旧备份|旧 boot-bak 字节保留，当前坏源另存 corrupt-bak；登录可见|PASS 旧/新来源保全子项|
|rv_view_no_backup_slots|三备份槽为目录，唯一坏源不覆盖，冻结提示可见|state 原文未动；登录提示备份失败/视图写冻结|PASS 唯一来源保护子项|
|rv_valid_history|两条字段齐全 NDJSON 结构正例/嵌套中文结果；不冒称真实成功链；保全并加载|原 NDJSON在 legacy.bak，主文件迁成数组后又判坏；完整事件也被误拒；41条VM诊断、业务区空白|FAIL 结构解析/迁移加载|
|rv_missing_status|缺status/绑定反例拒信保源|主源未动、bad_lines精确副本，登录冻结提示|PASS 反例拒信/保源；不证明status专属判据正确|
|rv_final_boolean|字段齐全但result:false拒信|主源与精确诊断副本保留，登录冻结提示|PASS 反例拒信/保源；不证明result专属判据正确|
|rv_final_empty_result|空对象result不可作完整成功证明|拒信/冻结/保源可见，未动态误接受|PASS fail-closed子项；结构判据仍须排除共同解码误拒|
|rv_final_bad_result_text|非空非法结果字符串不可作成功证明|拒信/冻结/保源可见|PASS fail-closed子项；不把第1段源码风险称为已复现误接受|
|rv_event_boolean_after|after:false拒作可信结果|拒信/冻结/保源可见|PASS fail-closed子项；不证明after语义判据已成立|
|rv_history_duplicate_key|单条NDJSON重复status，严格拒绝，不先归一化主源|原文在legacy.bak；主源已被宽容迁移成仅status=pending的数组，随后冻结|FAIL 严格消费顺序；PASS 原文副本仍在|
|rv_history_tail_garbage|完整数组后垃圾尾仍以]结束，拒信保源|主源未动、精确bad_lines、可见冻结|PASS 此语法反例保源子项|
|rv_primary_over_old_bak|两条字段齐全主历史与一条旧bak，优先主且能解析|主与旧bak都未回退覆盖；主被误判坏、36条VM诊断、空白业务区|FAIL 加载；PASS 不以旧bak覆盖子项|
|rv_bad_source_no_diag|坏事件源+合法形状备份，诊断槽全为目录，保源失败禁止恢复覆盖|主源与旧bak未动，无假诊断文件；登录提示人工检查原文件|PASS 保源失败阻止覆盖子项|
|rv_tx_no_applied|commit/redo存在无applied，未登录应pending并提示|commit/index与投影未变，但state hf_recovery_pending=false、准备就绪，无提示|FAIL 冷恢复屏障|
|rv_tx_null|applied=null不可解屏障|同上，无未决提示|FAIL 冷恢复屏障|
|rv_tx_empty|applied={}不可解屏障|同上，无未决提示|FAIL 冷恢复屏障|
|rv_tx_wrong_id|applied为其它tx不可解屏障|同上，无未决提示|FAIL 冷恢复屏障|
|rv_tx_false_time|verified_at=false不可解屏障|同上，无未决提示|FAIL 冷恢复屏障|
|rv_tx_claimed_applied|字段形状正确marker但投影缺失，不可仅信标记|同上，task仍前序，无动作/事件投影，无未决提示|FAIL 屏障；尚不能归因于marker专属检查已执行|

所有 seed 是隔离合成数据。历史结构正例只是 decoder/loader 输入，不代表真实业务动作成功；六事务输入是冷恢复消费者测试，不代表本次实际业务写点故障。tasks.json 在20场均未变；六tx文件/index也未变，不能凭“没写”认定“没有未决事务”。

## 缺陷复审与修复清单

### D-M2-01 · P1 / 必修 / OPEN：合法原文被错误解码后以空偏好覆盖

**文件与行：** app/bundle/main.splash :614、:619、:709（字符串输出）；:847、:862（解码后对象键）；:2082–2149 loadViewState；:15354–15364 加载与saveState。

**触发：** 用 rv_clean_unicode 的 view seed 冷开。pending_input 是 `独立复审：厨房积水，原文🙂 "引号"\n第二行`（含实际换行），键和值均合法。无需登录、无需业务写。

**实际/预期：** 登录渲染正常，但运行后 state.pending_input=""，原唯一合法 view 被重写且没有本次原文副本。预期完整恢复原字符串/偏好，再允许保存；不是损坏数据，不该默认清空。复原摘要与副本列表见 E/audit/scenarios/rv_clean_unicode。

**根因（高置信度）：** `_hf_parse_string` 以普通 `[]` 收集数值码点再 `out.to_string()`；普通 ScriptValue 数组会串接数值文本，U32字符数组才转换字符。合法键值变成十进制串。rv_valid_history/host.log:44 直接显示 `actor` 被解码为 `9799116111114`、pending_input 为 `11210111010010511010395105110112117116`，分别精确等于原键每个码点的十进制拼接。loadViewState 无法取原键却继续 `_VIEW_STATE_OK=true`，默认空内容落盘。无需靠函数名猜测此根因。

**影响：** 用户原文与稳定动作意图无法可信恢复；有丢输入/换键重复执行风险，是本模块硬5核心缺陷。

**具体改法：** 修字符串解码输出的真实数组类型，保留 typed U32 码点后转字符串，或使用已核宿主字符转换；不能把普通数值数组 to_string 当字符转换。现源码 `_strSlice :3470–3496` 有保留原to_chars U32数组的实现，可据此核实；例如空字符buffer须由真实to_chars产生，不能以普通[]代替。同类 `_hf_parse_number :782–790` 也用普通 sub[]→to_string，应一并修其转换并独立验证数值（该数值返回未在本轮直接探针，标源码风险）。合法view必需输入/意图读取异常时停止保存默认值，不吞掉失败。

**验证：** 原样复跑 rv_clean_unicode 与r11冷开长view；核中文/emoji/转义/换行、actor/project/key原字符与数字类型精确还原。最终view和UI原文相同、无自动登录、无误建坏源备份。已通过的不同旧bak/槽目录保源子项必须保留，不回退。

### D-M2-07 · P1 / 必修 / OPEN：严格与宽容消费者并存，合法历史加载失败且重复键源先被改写

**文件与行：** :611–715 字符串decoder；:936–1020 schema；:1147–1195 history；:2657 loader；:3061/:3085 在load中先迁移；:3181 _m2_parseRecordsLoose；:3217–3423 migrateJsonlLegacy（:3403 主写）。

**触发/实际：** rv_valid_history/rv_primary_over_old_bak 的字段齐全结构输入被严格decoder改键后误拒，分别41/36条VM错误，PNG业务空白；主历史/事件冻结。rv_history_duplicate_key 使用一条NDJSON中重复status，迁移先走宽容parse，主记录从重复 final/pending 归一化为仅pending，再由严格loader拒绝。原源确在legacy.bak，不能说源已完全丢失；但原主文件被提前改写是直接失败。

**预期：** 语法/结构合法数据正常加载，原键和值不改；非法重复键在任何主写前整份拒绝并保当前全文；主/备份/迁移/恢复共用严格decoder/schema，不能宽容parse清洗后再验证。

**根因/影响（高）：** D01字符buffer错误造成合法记录误拒；迁移函数仍用parse_json、非空对象判据，实际执行先于严格loader，故“有严格函数”不等于所有消费者严格。原合法历史不可用，非法历史被重解释，影响原动作对账与失败恢复。

**具体改法：** 先修D01的typed字符/数字转换；将迁移、bak恢复、原文判定和读回全部接入同一 `hf_parse_history(text,kind)`，在严格整份通过及精确保源前不得write；删除宽容归一化作为合法性来源。保留失败冻结与来源副本，不通过接受半条记录消除VM错误。

**关于上一段schema风险的修正：** result={}、非法字符串和after=false本轮均被拒/保源，**没有复现“坏结果被接受”**，因此不把源码风险当动态事实；然而共同改键会让正常/异常记录都被拒，这些反例不能关闭结果语义缺口。:979–987仍只核非空字符串/对象、:1012–1015仍只非nil；修decoder后按版本校验完整结果与动作/任务/版本绑定，旧未知历史可保留但不可升级成功。

**证据/验证：** R/rv_valid_history/logs/host.log:44、PNG与actions/events/bad_lines；R/rv_primary_over_old_bak 同类；R/rv_history_duplicate_key 的主源及legacy.bak。复跑全部正反例，检查原源字节、主源变化、字段和值、两个action IDs与事件、业务渲染；真实成功链另验，不用这些手造记录替代。

### D-M2-03 · P1 / 必修 / OPEN：已提交redo被漏查，恢复屏障实际未建立；主提交协议仍未接

**文件与行：** :1473–1489 tx索引；:1724–1863恢复（:1752按tx_id拼路径）；:6614–6650命令前屏障；:6874–7090实际commitBound；:2560 logEvent；:15362启动调用；:1469绑定函数仅定义。

**触发：** 六rv_tx场：tx_index=["rv1238-tx"]，对应commit/prepare存在，task仍前序，actions/events为空；applied分别不存在/null/{}/异tx/错误时间/形状正确却缺投影。均未预装可信session。

**实际/预期：** 全部运行后commit/index/投影原字节未变，但hf_recovery_pending=false、status准备就绪；PNG只有普通登录，无未决提示。预期未登录保pending、阻断后续业务写、可见恢复提示，授权后再对账补投影，不能把未恢复事务当不存在。这里实际**FAIL**，不是ABORT或环境BLOCKED。

**根因（高的共同转换原因，具体分支为源码推断）：** tx索引string也被D01错误解码为数字串，恢复函数据转换后的id拼路径，找不到实际commit/applied后走“无提交决定安全跳过”，最终清屏障。本轮直接观察到了原文件存在且屏障false；尚未观察某个marker专属检查实际被命中，不能声称本轮已证明applied正确校验。

**另一个已确认源码缺口：** commitBound仍分别写tmp/任务主文件/清tmp/读回/final，调用者后写事件；hf_bind_commit_spec无生产caller；作者明确完整H4未接。启动恢复接线改善认可，但无法为旧writer生成可靠的持久共同提交决定。

**影响：** 失败/重启后未决业务不受屏障，任务/回执/事件仍可能不完整；无法证明一次正确提交/对账，违反硬3/4。

**具体改法：** 修D01保证tx_id原字符还原；索引指向缺失/矛盾来源须fail-closed并提示，不一律认决策前中断；实际M2 caller绑定完整before/after/action/event、共同commit决定与受保护投影，返回unknown/拒绝必须被UI消费。applied还须绑定决定及全量权威投影，不只是schema/tx_id/时间形状。主writer与启动/每次命令恢复必须共用协议。

**验证：** 六冷恢复场必须pending=true且可见正确提示；再用受限驱动验证可信登录恢复、逐写点中断/读回失败/响应丢失/同Store连续重开，各action/task/event完整一次。后一组现白名单控制未覆盖，单列BLOCKED技术控制缺口；不影响已执行冷恢复FAIL。

### D-M2-02 · P1 / 必修 / OPEN：精确原动作绑定仍不完整，真实重试未验证

**文件链：** :14509–14522真实确认按钮→:8934 confirmDraftModelBound→:9237 createDraftFromPanel→:9955 confirmDraft→runCommandBound/commitBound/logEvent/权威核对。:9337–9368两重放分支；:9903–9953历史helper；:9983 query消费。

**改善：** query/outcome有实际caller；helper按actor/key/fp过滤并返回原result，不再只有定义。不得继续照抄r15“只有定义”。

**残余/触发（源码证据，动态NOT_RUN）：** OPEN重放outcome以确认action_id搭配创建回执result；历史分支仍 `_authorityHistoricalConfirm(task_id,"","")`，退成该任务同actor最后一条确认。较新状态下原键查询可能取非原意图结果；query非historical时caller仍构historical outcome的风险待实际分支核验。没有本轮可信按钮运行，不宣称已复现假成功。

**预期/影响：** 原创建和原确认的action_id/result各自精确绑定；当前较新状态另读，正常/跨状态/空面板重试同原键不重做，同键异参拒绝，结果未知不包装成功。当前源码两动作结果混用、任务级最后确认替代精确关联，仍无法完成核心原结果承诺。

**具体改法：** 持久保存创建动作与确认动作的明确关联，按actor/key/fp/action_id与权威盘精确查询，不允许空绑定回退；统一outcome返回原动作完整结果，非成功query保持unknown/conflict。顺带保留D01修复后的稳定key/intent恢复。

**验证：** 真实独立登录下正常重试、全部占键状态异参、跨状态重放、v9查原v1、空/有内容两分支与独立新意图，核任务/回执/事件写次数和UI结果。目前请求只有冷开capture，该组NOT_RUN；不以合成回执代测，不用用户禁止的自动化偷偷补测。

### D-M2-05 · P1 / 必修 / OPEN：仍缺同盘原子竞争边界

**文件：** :1294 storage caps；:1301 hf_atomic_write_text；:6447 lock；:6874 commitBound。

**源码实际：** atomic_replace/durable_sync/held_lock=false；exists/read→stamp write→read verify及提交前复核后才普通write。没有原子持锁/CAS线性化点；作者仍记录HOST_PRIMITIVE_BLOCKED。本段未独立探测宿主全原语，严格区分源码/能力记录与运行验证。

**触发/预期/影响：** 两真实独立认证上下文共享同Store/version同时抢单，应唯一赢家且完整事实不被迟到writer覆盖。读回校验与普通token复核不能排除校验后竞争，存在覆盖风险；并发硬要求未完成。

**具体改法：** 提供可核的受限宿主原子guard/CAS/替换边界，或交付形态可独立证明彻底排除第二writer；命令与恢复统一使用。不要把函数名atomic或单线程模拟当保证。

**验证/控制缺口：** 现harness场景串行fresh Store，schema没有共享Store双认证上下文/同步屏障。真正竞争动态 **BLOCKED（白名单无法覆盖）**，不是Codex rc71/pgrep rc3；无同盘竞争结果，不称动态FAIL，也不关闭P1。不用串行/不同Store/线程模拟代签。

D-M2-04/06保留旧根因认可，不宣称本轮动态重新通过。没有新增无关P1。旧建议及hub assets检查挂账，不因建议判FAIL。

## 五项硬验收与既有用例

|硬验收|结论与证据范围|
|---|---|
|1 同键/原结果/独立新动作|NOT_RUN真实按钮；D02源码必修未闭，稳定输入恢复另FAIL|
|2 权限/旧版本/撤权/到期/真竞争|NOT_RUN认证权限；BLOCKED仅真正竞争控制；D05未闭|
|3 逐中断点完整提交与恢复|FAIL已执行冷恢复屏障/D03；BLOCKED仅精确写点/同Store重开；非总BLOCKED|
|4 已写但读回失败未知与原结果对账|NOT_RUN真实查询；BLOCKED精确读回/丢响应控制；D02/03未闭|
|5 重复/重启输入与任务身份、迁移|FAIL合法原文/历史迁移加载；PASS所列精确保源子项；真实重复/超时NOT_RUN|

|既有用例|本轮状态与边界|
|---|---|
|G0-B|NOT_RUN真实认证/权限；真实身份来源已裁决，不记NEEDS_ABRAM|
|G0-C|FAIL解码、历史加载、tx屏障；精确保源子项PASS，不是整项PASS|
|T02|NOT_RUN创建/重试/冲突/独立意图；缺真实按钮证据|
|T04|BLOCKED白名单缺同Store双独立认证上下文同步竞争；无串行替代|
|T15|FAIL原输入恢复子项；旧版本拒绝/刷新NOT_RUN|
|T16|BLOCKED精确响应丢失控制；原动作真实查询NOT_RUN|
|T17|NOT_RUN断连重连权威回读；不把冷开称重连|
|T18|NOT_RUN逐主体列表/事件/附件查询权限|
|T22|FAIL冷恢复屏障/历史解析；保源子项PASS；逐写点/连续同Store重开BLOCKED|
|T24|NOT_RUN旧入口动态绕过回归；D06旧根因认可保留|
|T29|NOT_RUN撤权/到期/退出/共享卡片生命周期|
|T32|NOT_RUN配对/一次消费/poll_secret/approval/token|
|T37|NOT_RUN精确原action/result正常/跨状态/较新版本查询；D02未闭|
|U03|NOT_RUN双可信主体同任务事实与独立验收拒绝|
|U07|FAIL原输入冷恢复；重复点击/超时NOT_RUN，同Store连续重开BLOCKED|
|U08|FAIL合法历史业务空白、tx无未决提示；坏源冻结提示子项PASS|
|T28|FAIL两历史场业务加载；18登录冷开子项PASS，实际认证/操作/重开NOT_RUN|

NOT_RUN表示此请求未执行的实业务检查，不伪造白名单不能覆盖的确定性；仅真竞争/精确写点与丢响应/连续同Store重开有明确schema缺口，列BLOCKED。本次无ABORT；未引用agent沙箱rc71或pgrep rc3作为任何阻断。

## 判定、门禁与本模块修复顺序

- **最终结论 FAIL**，适用M2-r11-worktree。D01、D03、D07有本轮独立原生失败；D02、D05仍P1未闭且动态未充分执行。建议项不构成判FAIL依据。
- 先修D01共用typed字符/数值转换与view保存门禁，以最小原生正例证实键和值原样还原；再修D07全部实际迁移消费者与语法门禁，复跑正反例；随后修D03实际提交/恢复屏障、D02精确原动作关联与真实重试、D05原子竞争边界。不要仅改断言或把所有历史拒绝当安全完成，不改布局、不扩其它模块。
- 受影响前序：M1冷加载回归不通过，M1旧FAIL保留；共用解析对M3/M7有影响风险，注明来源，不执行或改这些模块结论。不是新增无关扩审。
- GATES.json仅更新M2 status=FAIL、review_*与reviewed_at；review_report指向本报告，review_candidate_id=M2-r11-worktree。更新前完整文件E/GATES.before-r16.json，上一轮status/review字段保留进review_history，不改作者candidate/base/build/implementation或其它模块。
- 本轮用例结果写入GATES.M2.review_acceptance，保留上轮来源；ACCEPTANCE.json不改，旧P0/38业务/12UI历史没有被删改或冒充本候选原生PASS。
- 不允许下一模块，不给下一模块入口。无需Abram额外授权：身份/provider已裁决，本地catalog/install路径可定位；本轮0模型场景，无余额/402/欠费；离线私钥已删。G0-E为“延期缺口（Abram已裁决，M3到期）”。
- 置信度：候选/完整性/隔离、原文丢失、历史加载失败、屏障false与共同字符转换根因 **高**；D02可达风险为源码证据，实际重试/并发/逐写点恢复结果 **未知**，没有宣称已执行。

STATUS=FAIL
NEEDS_ABRAM=no
