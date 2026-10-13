# M6 独立 Review r7

**最终结论：FAIL。当前候选的原生解析和业务首屏已恢复，但坏提醒文件仍被误认为正常加载；D-M6-03 的历史/阶段建议闭环、D-M6-04 的拒写反馈也未闭合。8 场 CLEAN 证明隔离与回收通过，不证明核心业务通过。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无子代理。
- candidate_id / base：**M6-r6-worktree / M6-r5-worktree**。按用户指定交接、GATES、实施报告、清单和运行包联合定位，没有用文件时间选版。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`，加既有未提交变更；源码 SHA-256=`8dda17002accec8afa630742ae3c34753c1dad8e157941dbb178dd9725ed8ba2`，503532 B。bundle digest=`15397be72f20b08a51629c832af62372619eb4486f30b4ab6da6d89b503f4e3e`。
- 作者报告：`reports/M6_IMPLEMENTATION_r6.md`；候选清单：`runtime/optimization/2026-10-09/M6/r6/CANDIDATE.json`。作者 build_r1_2104_REQUEST_build_r6 仅参考，不代独立执行。
- 快照：第1段冻结源/配置/manifest/候选/实施报告/GATES/ACCEPTANCE/harness/profile/宿主与第2段审计时全部一致。写门禁前再核，写后验证仅 M6 status/审查字段/审查历史变化，详见 S/final-write-verification.json。
- 前置：**M5=FAIL，M5-r7-worktree / M5_REVIEW_r8.md**，没有已接受的 M5 PASS。按用户挂账裁决继续 M6 复核，不伪造前置、不修 M5、不因其历史缺陷单独新增 M6 P1。
- 差异：S/previous-reviewed-to-r6.diff 包含其他模块累积变化；S/m5-r7-reviewed-to-m6-r6.diff、changes-from-M5-reviewed.json 定位 M6 本轮恢复/偏好/AI caller/派发/UI变化，不能全部归为 M6 自改。函数抽取最后区段含后续 UI 声明，不能把全部当 `_makeRowClick` 函数体。
- 宿主：项目内 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 原生执行：**仅外部驱动**执行本审查请求，03:42:53–03:44:30 +08:00；8 场 CLEAN、quit_http、rc0，没有 ABORT。审查者未自行启动 launcher、sandbox-exec、pgrep、osascript、辅助功能或其他 UI 自动化。
- 路由/标题：当前主会话无可用 Router/指定主模型核验或切换接口、createdAt/改标题接口；不冒称已切换为指定型号或已实际命名。MiniMax 与真实身份来源已由 Abram 裁决，不再写 NEEDS_ABRAM。
- 已读：第1段 AGENTS/CONTEXT/00/01/02/M6/04、候选/实施/上轮缺陷与直接相关源码、原 T/U 定义；第2段本请求、全部 summary/result/profile/完整日志/denials/MANIFEST、实际运行包/盘中权威文件、8 张原生截图及受影响源码。
- 已运行：独立官方离线 hub verify（第1段 rc0）；驱动 8 场当前候选原生冷启动/异常加载；审查者完整摘要、隔离、回收、环境、日志、包副本、权威盘与截图对账。Python 只准备/审计证据，未移植 Splash 业务作为测试。
- 未运行：可信三角色完整操作、真实收藏/重登、显式恢复点击、实际通知去重、动态改约/撤权跳回、真实模型三链及失败人工继续、运行中故障/同盘跨进程重启、150%/键盘完整流程和演示。未执行的业务记 NOT_RUN；已证明白名单不能覆盖的指定步骤单列 BLOCKED。
- 范围偏差：第1段首批误读项目外记忆索引匹配结果，已在阶段笔记披露；随后和本第2段没有继续显式读取项目外文件、没有项目外写入。结论依据本项目实时源码和独立原生证据；未读明文凭据或模型密钥。
- 置信度：版本/隔离/回收/解析改善、坏 schema 与非法成员实际加载失败、确定源码控制流 **高**；完整可信业务/模型事实正确性/真实提示效果 **未知**。没有把未发生的模型虚构或磁盘覆盖写成事实。

## 证据索引与独立核验

- **H**=`runtime/optimization/2026-10-09/M6/native-runs/review_r1_2104_REQUEST_review_r1_2104/`，驱动原始证据，只读未改。
- **S**=`runtime/optimization/2026-10-09/M6/native/review_r1_2104/`，冻结快照、diff、函数全文/行号、独立夹具/Store/离线验签/审计。
- **R**=`M6/native/REQUEST_review_r1_2104.json`，SHA-256=`2ccb34b34ce3e9f8971f09e6dfd3c704765964b266393515e133eb0eaf184d35`。
- **N**=`M6/native/REVIEW_NOTES_r1_2104.md`，第1段原笔记，未以第2段结果回改。
- **A**=S/native-evidence-audit.json；实际执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M6/native/review_r1_2104/audit_phase2.py`，rc0，**5397 项证据一致性检查通过，不是5397项业务测试通过**。

1. H/MANIFEST.sha256 **1285 项**逐项重算，缺失/错误/重复/未列入均0；summary.request 等于 R，harness/template 摘要与冻结及当前文件一致。8 场 summary 的 verdict/exit/wall/billing 与 result 一致。
2. 每场 profile_probes.ok=true、apply rc0；场外写被拒且 created=false，5 个禁读探针均拒；pre/post_pgrep 均 rc1/class=NONE/out/err 空，pgid_members_after=[]。均 quit_http=ok/rc0/CLEAN，无 exception/ABORT。
3. 按模板、实际新场目录、记录的原 HOME 字符串和控制端口重建 profile，字节/摘要全部一致；HOME/app-data/tmp/cache/config/data/Metal/rinx/octos/日志均在本场新目录。无模型代理放行。原 HOME .octosense mtime 前后相同、library_scan 空是驱动记录，审查者未访问项目外原 HOME。
4. 写入列表7场125项、prefs场123项，列表完整、排序/计数/唯一性一致、列项实际存在且均在本场；不把125项当125次业务动作。全部 denials 全文重算与 result 相同，remote:*:443、Metal系统缓存及部分/dev/dtracehelper尝试被拒，不当作成功外联/外写。
5. 8 场 seeded_files 清单与独立 seeds/mirror 的全文件 SHA 一致；installed、hub-mirror、唯一实际 `.running` 包的**全部文件**与 S 冻结签名包相同。seed/apps 的安装根正确；digest_seen_in_seed=true，digest_seen_in_host_log=false 如实保留，另以包字节定位，不因日志未打印 digest 判错版。
6. 完整 host.log 的 bytes/tail/markers 独立重算匹配。8 场实际业务 eval **503532 B / view=true**、hub launch 成功、零旧 parser/reserved/Expected 错误，无 panic。809 B 系统窗口 eval 单列，不与业务源混记。旧解析/业务全空白子项可以关闭。
7. 8 张请求 PNG 均存在、SHA 与 result/MANIFEST 相同，逐张实际查看，均 **2800×1716**；不存在额外 part 图。业务工作台已渲染，未显示种子任务正文/联系方式/异项目私有标记；登录输入/按钮下部仍裁切，所见截图的恢复/AI入口未可见。不同 request size 没有形成不同实际截图尺寸/可验证客户区，不能签三视口/150%通过。
8. reporter 场 host.log **:39–40** 明确拒 `key:Tab` 和 `type:M6-2104-NONCREDENTIAL`。这是固定宿主真实白名单能力缺口，不是 agent 内 rc71/rc3。没有可信登录或真实文字键入；role-labelled场仅预定角色入口，不能冒充三可信主体工作流。
9. tasks 与测试账号文件全部与 seed 同字节；四个提醒场原文也同字节。普通 actions 被既有迁移写为 `[[]]`；prefs pending 回执与 seed 同字节、仍 pending，AI审计夹具不是真实模型请求。所有场预存 pending_input 被清空，是前序共用恢复挂账观察，不是本轮实际键入后丢失，也不另扩编号。
10. 空文件场 pending/dirty=true，原文保留；scalar 场把 `{"follow_ups":17}` 当正常、pending=false、内存空；malformed 场把44 B非法JSON读为 **[null, null, -2104]**，pending=false、无备份，截图停留部分初始化显示。重复场内存保留两条同task/kind/current预约ACTIVE及旧约/其他主体记录。未登录没有实际通知，所以不能宣称发了重复通知或旧约误提醒。
11. 全部 needs_model=false，result 中 model_proxy/model_proxy_stats 缺省，无对应代理文件；真实请求0，无余额/402/欠费。新私钥0，作者两私钥复核不存在、keys目录空。没有公开签名/publish/listing/上传/push/Issue/消息/公网部署，也未造 SESSION。
12. 运行中进程记录 manager 场含 `(defaults)`，duplicate/empty 场含 `(pmset)`，结束全部回收为空；不据进程名猜测业务或未经授权的自动化。没有把运行列表只摘主进程来声称无子进程。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/前置/宿主|冻结、离线验签、8场全包/日志/seed核对|准确绑定当前候选，前置真实保留|M6-r6一致；M5仍FAIL|PASS定位子项，前置挂账|S/A/H|
|隔离及回收|profile重建、探针、pre/post、PGID/denials|用户规定隔离、完整回收|8场全符合，CLEAN无ABORT|PASS|8 result/profile/denials|
|原生解析/业务首屏|launch-hub、capture、完整日志|零parser、业务出现|8场均出现，零旧parser|PASS，关闭旧解析/白屏子项|8 log/PNG|
|三角色首次使用|新长中文同task，三入口/白名单探针|可信登录→有权任务→清楚下一步|未登录，key/type被拒，登录行裁切|实际角色流程NOT_RUN；可信键入步骤BLOCKED|reporter:39–40；3图|
|收藏隔离/拒写/重登|D04固定读回与saved消费；pending场|隔离/版本不增、保存状态准确|固定目标源码已修；saved=false仍称已落盘；未执行收藏|FAIL源码D04；实际操作NOT_RUN|main:2376/8558；pending盘|
|提醒异常恢复|空/数字schema/中文坏JSON独立冷启动|坏输入pending保护且有可达恢复|空文件保护成立；数字/非法成员被当正常解除保护|**原生FAIL D02**；显式恢复点击NOT_RUN|3场state/原文/图|
|提醒重复/旧约/跳回|2条重复+旧约+其他主体加载|按权去重/旧约失效、同task跳回|4条加载，未登录无通知/跳回|加载子观察成立；实际通知/跳回NOT_RUN|duplicate盘/图|
|撤权/重启/故障恢复|预撤权pending场+schema覆盖检查|动态撤权拒跳回、同盘重启去重、故障结果真实|预撤权未登录，不是假final；动态步骤未执行|实际命令NOT_RUN；指定步骤BLOCKED|R/schema/A|
|历史与阶段AI|输入/绑定/caller/渲染/元数据链|真实有权事实、版本拒旧、建议可读、人工继续|仍缺历史事件/版本网关/正文渲染；0真实调用|FAIL源码D03；真实模型NOT_RUN|S函数追踪/main|
|真实视觉与交互|8张PNG+actual action日志|登录/恢复入口可达、三视口/150%/键盘|原生渲染成立；登录裁切，恢复入口所见不可见|渲染PASS；入口可达未通过，完整布局/放大NOT_RUN；键盘步骤BLOCKED|8图/reporter日志|
|受影响回归|D01/D05、M3旧meta caller、M5基线差异|已修保持，新增变化定位|D01/D05非注释源一致；7处caller补绑定但D03总链未闭合|关闭子项保持，D03继续必修|S/diff/函数摘要|

**BLOCKED的精确范围**：当前发行宿主实测拒 key/type，允许的动作不能建立可信文本登录/Tab流程；当前schema每场新目录，仅启动前seed，不能表达同Store跨进程重启、运行中writer/commit故障、登录后动态撤权/断线或受控迟到交错。仅这些指定步骤记BLOCKED。原生坏schema保护失败是FAIL；未点击恢复/收藏或未触发模型是NOT_RUN。没有以CLEAN或agent环境错误代判产品。解阻需驱动/宿主提供仍符合Seatbelt和秘密边界的可信控件输入及受控步骤，不需Abram新增授权，禁止伪造SESSION或UI自动化绕行。

## 缺陷与上轮闭合

|编号|本轮结论|
|---|---|
|D-M6-01|已关闭源码子项保持；formatApptLine非注释源码一致；完整原生预约显示未测|
|D-M6-02|**P1 / 必修 / PARTIAL，原生FAIL**：受控恢复/备份/入口定义改善，但非列表/非法成员仍解锁，失效保存结果未贯通|
|D-M6-03|**P1 / 必修 / PARTIAL，源码FAIL**：旧parser/全空白关闭，caller补齐；事实/版本/可见建议/人工出口仍欠，真实模型NOT_RUN|
|D-M6-04|**P1 / 必修 / PARTIAL，源码FAIL**：固定读回目标关闭；拒写假落盘反馈仍在，实际故障操作NOT_RUN|
|D-M6-05|已关闭源码子项保持；m6_due_count_for_identity非注释源码一致；真实数量/筛选未测|
|R-M6-01|已关闭保持：离线验签及真实同digest installed/.running加载成立|
|A-M6-01～03|建议挂账，不因美化/文档/演示建议独立判FAIL|

### D-M6-02 — P1 / 必修：异常提醒文件被当作正常，恢复保护未闭合

- **文件与行**：`app/bundle/main.splash:1887–1918` parse/load/schema/清pending，特别`:1903–1917`；`:1973–1981`显式恢复读回只查非nil；`:2101–2104`、`:2128–2131`忽略失效保存结果；`:2530–2532`直接显示已失效；`:9434–9438`恢复入口。
- **触发**：R 的 scalar_schema_recovery 用17 B `{"follow_ups":17}`，或 malformed_backup_recovery 用44 B `{"follow_ups":[独立坏文件原文-M6-2104`，当前同digest冷启动。所有输入只在本场隔离app-data。
- **实际/预期**：scalar 内存[]且pending=false；malformed内存[null,null,-2104]、pending=false、没有.recover/.recover.bak，截图部分初始化态。预期非数组/非法成员/坏JSON保持原文并进入明确待恢复，不能以非nil放行普通写。原文确未被覆盖，本轮没有运行后续写，**不声称已丢盘或发生崩溃**。
- **已改善**：空文件原生pending/dirty=true、原文保留；受控use-memory不再走普通pending闸、备份有逐字节读回、新UI/cmd caller真实存在。只关闭这些子项；显式点击/备份失败/成功重试与同盘重启未执行。
- **根因**：应用把parse_json结果非nil及follow_ups非nil当schema有效；实际宿主没有把此坏原文转成预期nil/异常，应用又不检查数组及成员对象类型/字段，随后清pending。不能推断底层parser的完整规范，当前反例和应用缺校验已经确证。恢复读回仍没有与预期内容比较，失效计数仍忽略保存返回。
- **影响**：核心可恢复跟进及损坏保护、硬3/5、G0-F/T23/U07/U08；空或非法内存可被后续普通写追认，恢复/去重无法可靠成立。
- **证据**：H两反例场的state.json、原follow_ups.json、logs/host.log/frames与A；S源全文/差异。empty场是对照；duplicate场仅证明加载4条，不以它宣称重复通知已发。
- **具体改法（Kimi-K3）**：保留已修受控写和备份。把load及受控读回共用严格schema门禁：顶层对象、follow_ups数组、每条非nil对象、合法id/task/主体/kind/时间/状态，不能接受宿主错误值/残缺解析结果。失败保持pending/原文/准确可见错误，备份必须真实读回一致；成功读回内容等价于本次预期，再解除保护。让失效/登记/关闭调用方消费saved/dirty，拒写不能显示完成。只修该编号，不扩业务。
- **验证方式**：harness先独立零parser/登录渲染，复跑空/17/中文坏JSON，补null、数字成员、缺字段/拒读；全都保护原文。驱动输入通道可用后真实点击两恢复分支、备份拒写/内容错读、写后schema正确但内容不一致；失败保护可重试，成功同key仅一份。实际改约/取消/撤权/同Store进程重启核旧提醒不复活，通知恰一份。静态词法或CLEAN不能代验。

### D-M6-03 — P1 / 必修：新增历史/阶段链缺事实与版本绑定，返回建议没有真正进入详情

- **文件与行**：`:1516–1591`history，`:1522`空task绑定、`:1548–1560`请求输入；`:1631–1700`phase，`:1637`空绑定、`:1657–1669`输入；`:2553–2584`caller；`:5186–5235`元数据持久化；`:10225–10267`详情渲染。
- **触发/实际**：源码可达caller发history时传nil refs；phase传nil seq→0。history仅task_id+空间设备白名单，没有维修历史；phase仅task_id/seq，没有真实阶段事件。局部task/project_version没有回包比对，两处bindRequestVersions仍传空串；回包重新取当前actor，没走M3版本/过期网关。history丢弃res.items，只存“已返回”固定文案；meta只存请求种类/provider等，详情history只读该审计，phase只用静态m6_phase_meaning，未消费m6_history_view。失败称手工编辑，但phase无对应编辑控件。
- **预期**：实际有权历史/事件事实+明确JSON schema；发出上下文固定、回包重核授权/版本/事实/到期；正文和合法依据可读可核，失败/无历史有实际人工出口；不能用静态说明或元数据代模型建议。
- **改善与动态边界**：**8场独立零parser、业务渲染，上一轮解析/全空白子项CLOSED**；新触发和7处旧meta绑定源改善成立。新caller未直接写业务源子项保持。本轮0真实模型，不断言“模型已虚构事实”，也不声称三链成功/安全动态PASS。
- **根因/影响**：复用草稿适配却绑定未建任务sentinel，接口没有该链真实事实/schema、建议存取渲染未对接；人工出口只有文案。核心AI能力/硬2、T25/T26/T33/T34/T35/T38仍不成立。
- **证据**：S/source-traces、冻结diff、当前上述文件行；H的8场解析/截图用于关闭parser，prefs审计为显式FIXTURE-NOT-MODEL，不能证明真实调用。
- **具体改法**：只补本编号：固定真实task_id/project/发出actor/版本/事件与证据上下文；以有权事实组成两链输入和明确返回schema；回包复核权限/请求/任务事实版本/过期；保存并渲染真实items/phase正文及合法依据，失败/无历史可实际手工继续。保留已修解析/caller，不能删除链或禁用模型换PASS。
- **验证方式**：输入通道补齐后，从三组新描述实际跑三条链；无历史/矛盾/不存在引用须未知/拒绝且人工可继续；切task/actor、撤权、改约、迟到不落错对象，权威业务不被模型写。仅needs_model经harness代理，模块合计≤10；402/余额/欠费立即停并记录原文/NEEDS_ABRAM=yes。未建立可信刺激入口前，接口裸调用不代端到端。

### D-M6-04 — P1 / 必修：明确拒写仍反馈“已落盘”

- **文件与行**：`:2324–2342`固定目标/预期快照（已修）；`:2361–2376`拒写返回；`:2390–2411`读回目标（已修）；`:2466–2480`finalize恢复；`:8552–8559`togglePin结果消费。
- **触发**：可信收藏变更后tasks写异常，m6_save_prefs返回`needs_verify / saved=false / tasks_write_failed`；或读回/receipt失败后重试。本轮没有运行中writer注入，不伪称实际复现该命令。
- **确定源码实际/预期**：caller按needs_verify统一处理，不查saved，保留新收藏内存并显示“收藏添加/取消已落盘但待核验”。预期明确未执行与写结果未知/已写分开，准确保留失败，不能把saved=false说成已生效；已写/未知结果则不能盲目回滚。finalize catch仅内存改needs_verify，持久对账同key恢复仍须证明。
- **已改善**：清pending前固定task/预期pinnedBy；缺目标/错任务/错偏好进入待核验，parse成功不代匹配。这些源码子项CLOSED，不重复要求改。prefs原生夹具仍pending、没有假final，但因未登录不能签收藏实际恢复通过。
- **根因/影响**：调用方继续把needs_verify等同saved=true；仅修callee读回不等于端到端执行反馈可靠。硬1/5、T30/U07/U11核心持续收藏使用欠缺。
- **证据**：当前冻结main上述行、S/source-traces；H/prefs_pending_revoked_history/A仅支持未发生真实命令，不能作拒写实验结果。
- **具体改法**：保留固定目标修复，精确消费saved/readback/执行态；对确定未写回退并显示准确失败，未知/已写查权威回执与实际偏好再定状态；finalize失败有可定位的持久对账/稳定键。不能吞错后继续用“已落盘”统一文案。
- **验证方式**：双可信主体收藏/取消、跨项目、重登/version不增/同key重试；tasks/state/final拒写及空/错task/错pinnedBy读回，核UI/盘/回执/后续动作，确证不假成功、不盲目重做。需驱动受控输入/故障/同盘重启通道；未提供前动态NOT_RUN/指定步骤BLOCKED。

### 建议与前序依赖挂账

保留A01～03及旧文档/演示建议，不作为新增FAIL依据。登录行裁切、预存中文清空、prefs场初始化显示是原生实测可用性/前序依赖边界；不扩修前序或增加无关编号。构建方要完成M6可信流程时，需最小处理真正阻断入口的依赖或补合规驱动通道。M5附件索引FAIL及其他前序门禁保持原样；不把作者CONTEXT旧身份/provider/agent沙箱错误当当前授权/环境缺口。

## 全部硬验收与相关既有用例

|硬验收|本轮结论|
|---|---|
|1三角色追踪/搜索/收藏/重登/跨项目|FAIL D04源码执行反馈；可信完整流程NOT_RUN，文本输入步骤BLOCKED；未登录不显示seed正文子观察PASS|
|2三条真实AI、失败/无历史人工出口|FAIL D03源码闭环；真实模型/人工继续NOT_RUN，可信输入步骤BLOCKED；parser子项关闭|
|3提醒恢复/去重/旧作业/跳回|**原生FAIL D02**；空文件保护子项PASS；实际显式恢复/通知/跳回NOT_RUN，同盘/动态步骤BLOCKED；仅前台不称后台常驻|
|4三视口/150%/键盘可达|首屏渲染PASS，登录行裁切及新增入口所见不可达未通过；完整视口/放大/角色操作NOT_RUN，键盘步骤BLOCKED；无HTML替代|
|5统一输入/选择/滚动/恢复/责任台账|FAIL D02/D04；完整交互NOT_RUN；P0/38业务/12UI定义和历史保留|

|用例|本轮精确结果|
|---|---|
|G0-F|原生schema恢复FAIL D02；空文件保护PASS子项；真实前台通知/官方卡/后台NOT_RUN，同盘重启步骤BLOCKED|
|T17|实际断线/重连全量回读/不重复写NOT_RUN；断线注入步骤BLOCKED|
|T18|未登录种子正文/联系方式/外项目标记不显示子观察PASS；可信搜索/事件/附件授权操作NOT_RUN|
|T23|原生异常提醒加载FAIL D02；重复/旧约加载4条为事实，不代通知去重；实际通知/进程重启NOT_RUN，同盘调度BLOCKED|
|T25|D03真实事实输入/返回校验欠缺；模型缺失/矛盾/恶意原文NOT_RUN，不断言已经虚构|
|T26|FAIL D03实际人工出口源码闭环；真实模型失败/人工继续NOT_RUN|
|T28|离线verify、installed/.running同包、独立launch/渲染PASS子项；可信操作/回读/同盘再开NOT_RUN，输入/重启步骤BLOCKED|
|T29|预撤权未登录没有seed正文显示子观察；动态撤权/退出/到期/共享卡/跳回NOT_RUN，指定注入步骤BLOCKED|
|T30|FAIL D04源码拒写反馈；固定读回目标子项CLOSED；双主体收藏/重登/version不增NOT_RUN|
|T33|真实新描述泛化NOT_RUN，不能以长中文fixture或审计代真实模型|
|T34|FAIL D03历史/阶段事实依据与可见建议源码闭环；真实无历史/歧义/不存在引用拒NOT_RUN|
|T35|D03task sentinel/回包版本仍欠；真实改派/改约/迟到NOT_RUN，交错步骤BLOCKED|
|T36|新增caller未直接写业务源码子观察保留；实际工具白名单/模型写边界NOT_RUN|
|T38|source/config/宿主/数据/request固定、原生parser及异常加载可复现PASS子项；真实模型/提示/成功失败复跑NOT_RUN|
|U01|原生首屏渲染PASS子项；登录行裁切未通过入口可达；三可信角色当前事项/下一处理人NOT_RUN|
|U02|真实原话草稿修改/歧义/模型失败人工继续NOT_RUN|
|U03|同任务三可信主体事实/按权动作/禁自验NOT_RUN，输入步骤BLOCKED|
|U04|D01formatter源码关闭保持；预约/冲突/过期/改约真实交互NOT_RUN|
|U05|D03历史依据未闭环；设备位置/服务空间/选择依据真实操作NOT_RUN|
|U06|进度/完工/独立验收/退回保留真实流程NOT_RUN，M5FAIL挂账保留|
|U07|原生异常加载FAIL D02、源码拒写反馈FAIL D04；动态重复/丢回包/故障实际NOT_RUN，指定步骤BLOCKED|
|U08|未登录/空态渲染子项PASS；schema异常恢复FAIL D02，显式恢复/附件/过期可继续出口NOT_RUN|
|U09|8张原生图登录行裁切；请求三size未证明客户区变化；完整视口/150%/长中文主要动作NOT_RUN|
|U10|真实key/type拒绝，键盘指定步骤BLOCKED；完整焦点/对比/颜色冗余NOT_RUN|
|U11|host运行/capture/回收PASS子项；D04假落盘反馈源码FAIL；实际滚动/输入/面板稳定性NOT_RUN|
|U12|同版本2–3分钟实际结果/异常演示及独立人员复述NOT_RUN，演示建议保留挂账|

## 判定与交接

- **最终结论：FAIL**，适用于冻结M6-r6在固定发行宿主的上一轮缺陷复核及本轮8场独立直接回归。不是因建议项、M5历史前置或agent沙箱限制判FAIL。
- 必修仅 **D-M6-02、D-M6-03、D-M6-04**。先修D02实测schema/成员校验与保存反馈，再补D03既定事实/版本/实际渲染/人工出口、D04保存结果准确消费。保留已关闭解析/备份/读回快照子项，不重复无关修复。
- 阻塞仅已确认的白名单文本/键盘以及schema无法表达的指定受控步骤；无ABORT。实际业务/模型未执行按NOT_RUN，不能用CLEAN、源词法检查或夹具审计代PASS。
- GATES仅M6 status/审查字段/审查历史更新：review_report指本报告，review_candidate_id=M6-r6-worktree；旧Review完整来源追加history，作者候选/实施/test_counts等不改，其他模块不改。
- 原 `docs/build-loop/ACCEPTANCE.json` 未改；本轮逐项结果写入M6 review_acceptance，保留历史后端/旧原生来源，不借旧PASS改判当前原生。
- **不允许、不执行下一模块，不给M7入口。** 留在M6按原编号修复并补合规原生验证通道/核心实际结果，再交接新可定位候选独立复审。
- 无公开发布或模型余额新授权缺口；真实请求0，不存在402/欠费证据，NEEDS_ABRAM=no。

STATUS=FAIL
NEEDS_ABRAM=no
