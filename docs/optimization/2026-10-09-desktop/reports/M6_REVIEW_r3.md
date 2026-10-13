# M6 独立 Review r3

**最终结论：FAIL。** `M6-r3-worktree` 对上轮 D-M6-02、03、04 有明确改善，但三项均未完全闭合，仍阻断提醒恢复、既定 AI 场景或收藏失败后持续使用。建议项、M5 前置挂账和未运行视觉检查不是本次新增 P1 的理由。

- 审查者 / 日期：Codex 当前主会话，2026-10-11 Asia/Shanghai；唯一审查方，无子代理。
- candidate_id：`M6-r3-worktree`；交接基线：`M6-r2-worktree`。由 GATES、M6_IMPLEMENTATION_r3.md、M6/r3/CANDIDATE.json 三方交接定位，不按文件时间选版本。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r3.md`。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作区未提交；主源 SHA-256：`7bc8a3d874d4cbd2734f117990c4790c5020629ea3a7555563fee65f1316ba6b`，366104 字节，与候选交接一致。开始冻结完整源及配置哈希，结束重新核验，见 final-verification.json。
- 前置：M5 最新独立 Review r4 为 **FAIL**，候选 `M5-r4-worktree`，没有已接受 PASS 候选。按本次前序挂账授权继续 M6 复审；没有宣称前置通过，没有修 M5 或改变其结论。
- 增量：r2 至当前包含中间 M2～M5 重跑变化，不能把全部差异叫“仅新增99行”。另保存 M5-r4 独立冻结快照至 M6-r3 的差异；23 个相关函数中 17 个忽略纯注释行后相同，6 个变化为本轮 M6 提醒、历史、偏好及其预约 hooks，详见 affected-regression.json。前序新增差异可定位，不代表已接受。
- 宿主：指定 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`，0.1.0-rc.1 / 20261008.091752；可执行文件 SHA-256：`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 实际路由 / 标题：当前工具不能核实或切换主会话 Router 路由、没有当前对话 createdAt 与标题写入接口；未声称主会话已切换或已实际改名。受项目内读写限制，未读取项目外记忆或技能文件。
- 已阅读：先读 CONTEXT_M6.md，再核 AGENTS、00/01/02、M6、04 模板、上一轮 r2 缺陷、r3 交接/作者证据、相关函数及其 UI 消费端、既有 T/U 定义、M5 r4 前置。CONTEXT 的“禁止后台启动”“身份/provider未授权”已过时，由本次授权覆盖；没有沿用这些说法作为阻塞理由。
- 实际运行：新隔离预检；当前冻结函数的控制流探针与文件故障注入；作者静态脚本复制复跑；离线 catalog / 官方 Store::install_staged、Store 重建 / may_run、篡改拒绝及恢复重试。没有运行真实桌面流程或真实模型。
- 未运行：三可信角色首次使用、真实登录/重登、宿主重启/撤权/grant、业务权威结果与回执、原生视觉/键盘/放大及三条真实模型链。原因与边界见下文。
- 写入范围：本报告、GATES.json 的 M6 status/审查字段/审查历史，以及本轮项目内隔离证据。未修改业务代码、原业务数据、其他模块或原 ACCEPTANCE.json；未进入 M7。
- 证据根：`runtime/optimization/2026-10-09/M6/review-r3/`，以下相对证据路径均从此根起。
- 置信度：候选、源码调用关系、离线安装实测 **高**；Splash 到 Python 控制流适配 **中**；真实原生会话、UI、权威业务结果及模型行为 **未知**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/增量|核交接主源哈希；冻结配置；对比 r2 与 M5-r4 快照；读取宿主版本与二进制摘要|交接一致，前置与变化明确|当前主源匹配；M5-r4仍FAIL；增量已定位|定位 PASS，前置未PASS|results/candidate-check.json、两个 diff、affected-regression.json|
|隔离与退出条件|本轮全新 HOME/CFFIXED_USER_HOME/TMPDIR/XDG/app-data/Metal 缓存重定向；deny外写及网络预检；pgrep核进程枚举|可约束全部外写并确保关闭/无窗口残留|sandbox-exec rc71：`sandbox_apply: Operation not permitted`；pgrep rc3：`Cannot get process list`|BLOCKED；未启动launcher|results/preflight.json、isolation.sb|
|首次使用三角色|需真实原生首屏、当前任务/下一步、搜索/待办/收藏/重登/跨项目|事实一致、操作明确、有权限依据|无法安全启动发行宿主；没有用角色标签或夹具充当可信人员|BLOCKED|preflight；作者明确未运行|
|收藏与连续使用|执行实际 togglePin/m6_save_prefs/saveState/release 控制流；两主体收藏/取消；注入tasks/state写失败|version不变、偏好隔离、命令精确结束、失败可继续|正常锁/上下文释放、双主体互不取消、version=4成立；state异常跳过清理；pending回执不结束；tasks失败内存仍收藏|FAIL D04；原生重登BLOCKED|results/review-probes.json、生成的 translated.py|
|提醒恢复/去重/旧作业|绑定预约、重复登记、磁盘清空内存后load；撤权/换主体/终态/改约/取消；写拒绝、空文件、读异常、异常schema|有效到期且有权才展示；恢复不丢失、不假成功|终态/预约闸、精确失效、到期/撤权、去重、load、dismiss失败返回成立；登记忽略保存失败；空/读失败静默；schema异常后save覆盖原文|FAIL D02；真实宿主重启BLOCKED|review-probes.json、data/followups/、源快照|
|撤权跳回|对实际 m6_jump_summary 与提醒显示调用注入撤权；核UI与授权生产端|撤权无摘要/提醒，不继承grant|适配撤权返回false/零提醒；真实grant生命周期不可运行|源码子项符合；完整BLOCKED|review-probes.json、preflight|
|历史与阶段|外任务/项目/主体、空历史、本任务记录；读模型入口及history/phase消费|真实来源、不虚构、无历史未知、模型只出建议|外主体元信息已排除，空历史明确未知；内容仍是调用审计元信息与静态阶段，链②③未实现|FAIL D03；真实模型NOT_RUN|review-probes.json、source-evidence-audit.json、源码:1286/1348/3515/7705|
|真实原生视觉/交互|需1440×900、1280×800、980×760、150%、长中文、键盘/焦点、正常异常截图|关键内容可达、当前主要操作明确|未启动宿主；无当前候选原生截图/交互；未借HTML测量或旧图放行|BLOCKED / NOT_RUN|preflight、作者报告|
|当前digest本地安装|离线keygen/certify/stamp/sign-manifest/verify；官方install_staged及Store重建；改包、恢复|安装当前候选；篡改拒；恢复可运行准入|安装/Store重建rc0；篡改rc1；恢复rc0；三份源码/配置安装字节一致|PASS安装层，非原生执行|results/local-store-validation.json、store-test/|
|私钥删除|签名finally删除两key；结束核keys目录|仅本轮sandbox签名，私钥不残留|working.key、anchor.key已删除，remaining_key_files=[]|PASS|local-store-validation、final-verification|
|受影响回归|比对23函数；task/单预约formatter；nav保存/异常恢复；终态/改约hooks及偏好隔离|保留D01/D05修正，前序结论不冒签|formatter双形态一致；all/fav/todo及异常均恢复nav；17函数相同；D02/D04仍有失败|局部回归符合，完整原生BLOCKED|affected-regression、review-probes、两个diff|

独立控制流探针 **42项，34项符合预期、8项不符合**。作者静态脚本独立复跑仍 **29/29**；只检查代码片段/分支存在，不等于失败恢复或应用通过。没有用作者沿用的195项总数代替本轮独立结果。

本轮离线安装 bundle digest：`9ad0c9273b9c4de04dbf73f5ebd67e9d865651754f44fec1a87e73044f0a8c13`。仅签本轮项目内包副本，不改原manifest；没有联网、publish、公开签名或listing发布。包内旧截图是历史素材，不是当前原生视觉证据。官方 Store 层成功不能证明 launcher 已加载该包或业务 UI 可用。

### 证据边界与原缺陷闭合

探针从冻结 Splash 函数体译码，保留原分支/调用次序，实际写本轮隔离文件。翻译仅适配Python对象、三目、跨行表达式、全局变量作用域和字符串/数组方法；全部生成函数保留。时钟、身份、授权、任务查找及命令 admission/receipt 查询为显式 adapter。runCommand、recordReceipt、saveReceipts、togglePin、m6_save_prefs、saveState 和释放函数使用实际源码控制流；runCommandBound admission 适配只建立其已核源码中的持锁/pending上下文。没有称为发行VM、可信会话、真实权威回执或已发生的原生故障。早期探针全局LAST_KEY适配错误已在审查脚本内纠正后复跑，不改业务。

|原编号|本轮闭合状态|已成立改善|剩余|
|---|---|---|---|
|D-M6-01|保持源码子项关闭|formatter接受task/单预约，两者相同|原生确认/实际时间UI仍BLOCKED|
|D-M6-02|PARTIAL / P1 OPEN|终态/appointment_id过滤、精确取消、invalid JSON错误/.recover、dismiss返回保存结果|空/读失败、schema保护、登记/失效保存返回与重试未闭合|
|D-M6-03|PARTIAL / P1 OPEN|task/actor/project过滤、空历史明确未知、静态阶段不算历史条数|链②③仍缺；审计元信息不是设备/事件事实建议；请求固定上下文/引用版本契约未补齐|
|D-M6-04|PARTIAL / P1 OPEN|正常路径锁与pending清理；version不变；双主体收藏隔离控制流符合|state异常跳过清理；回执永远pending；失败内存不回退/不核对|
|D-M6-05|保持源码子项关闭|正常/异常nav恢复、诊断默认不即时计算保持|真实原生筛选/滚动/交互仍BLOCKED|

## 缺陷

### D-M6-02 — P1 / 必修 / PARTIAL：提醒异常读取与持久化恢复仍不完整

- 文件与行：`app/bundle/main.splash:1427`（read失败转空）、`:1428`（空文件直接返回）、`:1443`（缺字段只置dirty）、`:1467`（写入不检查恢复标记）、`:1494`（upsert忽略save结果）、`:1515`/`:1516`（登记仍返回fu_id）、`:1558`（失效忽略save结果）。
- 触发：只在新隔离follow_ups.json分别造空文件、读异常、有效JSON但缺follow_ups；调用load，再在后两步清空内存并save；对登记注入该文件写拒绝。
- 实际：空文件/读失败均没有错误或dirty；缺字段时报错但后续save写成`{"follow_ups": []}`，原文覆盖；登记保存失败仍返回非空fu_id，错误没有向登记调用方贯穿。合法JSON缺字段分支没有.recover，dirty也不是防覆盖/恢复协议。invalid JSON备份与dismiss返回false已改善，保留。
- 预期：首次不存在可正常空态；已存在却读取失败/截断/schema异常必须可见且保留原数据；恢复未决时不能用空内存覆盖；登记/关闭/失效明确区分保存成功与待重试，最小重试不重建重复记录。
- 根因：把“读失败/空内容”合并为正常返回；dirty只用于提示且save立即清掉；登记/upsert/失效忽略持久化结果。
- 影响：重开或保存失败可丢失跟进，无法实现核心可恢复持续使用；直接影响硬3、T23/U07/U08。不是要求新增后台服务。
- 证据：review-probes的register_failure_is_signaled、empty_file_reported、read_failure_reported、schema_error_original_not_overwritten，当前源快照及对应translated.py。真实宿主重启未运行，未声称原业务已丢数据。
- 具体改法：只修此提醒路径：区分不存在/读取失败/空或损坏/schema错误；所有异常保留旧文件并进入恢复未决状态，后续普通save不得覆盖；把save结果贯穿登记/upsert/失效并提供针对同一记录的明确重试。保留已经通过的appointment/终态/撤权过滤。
- 验证方式：隔离空/损坏/schema/读拒绝/写拒绝→关闭→宿主重开；检查原文件或可恢复备份仍在、错误可见、重试后恰一条，改约确认/取消/撤权不复活旧通知。

### D-M6-03 — P1 / 必修 / PARTIAL：来源隔离改善，但既定新增 AI 链仍未实现

- 文件与行：`main.splash:1286`（history只读AI_REQUESTS_LOG）、`:1318`（只陈列result_kind/provider/model）、`:1348`（phase静态状态映射）、`:3515`（现有模型入口为报修草稿）、`:3683`（缺绑定时取当前UI上下文）、`:7681`/`:7705`（UI消费）。作者报告r3 §2.2B明确“链②③未实现”。
- 触发：接单后查看设备/历史/预约占用建议及事件变化后的阶段建议；对空历史、外任务/项目/主体注入日志并读history；核模型来源生产端与调用图。
- 实际：外主体provider/model元信息反例已消失，空历史note精确为“无历史说明未知”；本任务记录仍只有AI调用审计字段，phase只有静态参考。不存在新增链②③真实请求、事实引用、版本/过期及人工采纳路径。生产缺绑定兜底仍取当时selected_task_id/project/主体，未改为请求发出时的固定上下文。
- 预期：三条既定链均有真实模型证据；新增设备/历史/占用与事件阶段建议读有权事实，引用不存在拒绝，无历史说明未知，失败可人工继续，建议不直接写业务。
- 根因：将“删除泄漏+静态未知出口”当作功能闭合；AI请求元信息陈列代替业务历史建议。实施报告仍把真实provider/身份当未授权，已与本次裁决冲突。当前model_config.json实际为enabled=true、MiniMax-M3；缺的是M6新增接线与运行证明，不是等待选provider。
- 影响：本模块核心AI场景缺失，硬2/T25/T26/T33/T34/T35/T38不能完成。未观察真实模型虚构输出，不能声明“模型已无虚构”；仅读函数没有直接业务写，但也没有已运行新增模型链。
- 证据：review-probes的foreign_metadata_excluded、no_history_unknown及三条actor/project过滤；source-evidence-audit；冻结函数和作者r3 §2.2B。M3一般模型/HTTP挂账保留，不扩修前序模块。
- 具体改法：在已有来源、过期/版本、授权与人工确认契约内补原缺陷要求的链②③；使用请求固定上下文绑定，读取可核真实设备/任务历史/占用和事件，返回事实引用及缺项，不能把种子或日志元信息当设备事实。复用已授权MiniMax及5账号来源，不重新申请选择provider/身份；若目标宿主能力阻断，给最小复现并标BLOCKED。
- 验证方式：原生各链新描述、空历史、矛盾/不存在引用、切任务/换主体/撤权/事件变化、迟到回包；保存模型/提示/数据/宿主和固定请求版本及引用；确认建议不直接写业务、有人工出口。按本次授权≤10真实请求，余额/402/欠费立即停并原文报告。本审0次请求，未读取密钥或明文凭据；绕开应用直接调API不能闭合本缺陷。

### D-M6-04 — P1 / 必修 / PARTIAL：所谓finally不覆盖异常，偏好回执与失败结果仍悬空

- 文件与行：`main.splash:1737`（偏好保存）、`:1740`（身份失败早退）、`:1745`（tasks写失败只记ok）、`:1746`（saveState未包异常）、`:1753`～`:1756`（清理放在正常尾部）、`:814`（state直接写）、`:2650`（recordReceipt建pending）、`:6034`（调用偏好路径）。
- 触发：合法收藏后注入state.json写异常；另注入tasks.json写异常。正常收藏后读同一action回执，再按相同key/fp查询/重试。仅新造本轮tasks/state/actions/lock，不碰原数据。
- 实际：正常路径锁清空、_PENDING_CMD清空且version 4→4；但state写异常时仍有`review-owner`和`togglePin`，尾部清理根本不执行。回执正常成功后仍pending；清空_PENDING_RECEIPT_ID前没有精确finalize或权威读回。tasks写失败后内存pinnedBy仍[actor-A]，回执仍pending，没有显式失败/待核验。相同key命中该悬空记录，runCommand返回false。没有把这叫已观察真实权威回执。
- 预期：成功先核偏好落盘并按唯一action_id结束该动作；失败保持可恢复一致状态、不把未落盘收藏留作成功事实；所有退出/异常释放本次锁和上下文，重试能对账、不永久悬空，业务version不增。
- 根因：注释写“finally”，实际仅顺序执行正常尾部；身份早退与saveState异常都绕过清理。删除commit后只补_releaseTaskLock和清变量，漏了原缺陷明确要求的幂等/读回/失败结果；不是要求重写前序M2事务。
- 影响：失败后持续使用与收藏重试不能保证；UI内存/磁盘偏好分裂，原动作没有可核终态；影响硬1/5、T30/U07/U11。当前M4锁是建议锁，不能机械复用r2“下一命令必因抢锁失败”的结论；本轮证明的是异常跳过清理和偏好生命周期未闭合。
- 证据：review-probes的favorite_receipt_finalized、state_write_exception_cleanup、tasks_write_failure_memory_rolled_back、tasks_write_failure_receipt_explicit；实际生成m6_save_prefs/togglePin/saveState/runCommand/recordReceipt；source-evidence-audit的无finalizer/无读回。
- 具体改法：仅为偏好建立完整收尾：固定本次actor/action_id/原偏好，写入与读回一致后精确finalize；失败回退或明确待核验/可重试；身份早退和tasks/state/receipt异常均走实际受保护的清理，不能仅加注释或正常尾部调用，不更新其他回执，不递增业务version。
- 验证方式：正常收藏→另一动作；收藏/取消/双主体/跨项目/重登；同key重试；分别拒写tasks/state/actions/释放锁与读回不一致，重开核偏好、原action及清理一致，无假成功和永久pending。

### B-M6-01 — 必需运行 BLOCKED：原生隔离与清理预检失败

本轮全新预检rc71/rc3原文在preflight.json。仅设HOME不能证明全部宿主外写受限，且不能枚举/结束并核无残留窗口，因此没有启动launcher、没有调用--help、没有新增测试宿主窗口；已有窗口状态未知，不冒称已清理其他人的窗口。

解阻条件：能执行项目内写入约束、可靠枚举/终止测试进程及确认窗口清理的环境；所有HOME/app-data/log/cache定向本次runtime隔离根。通过后后台启动指定launcher，真实登录隔离测试主体，逐操作回读任务/事件/动作/提醒，finally立即关闭。本地catalog路径本轮已证明可行，无需公开发布或Abram再次授权。仅环境解阻不能代替D02/03/04修复。

### 建议挂账（P2，不作为FAIL依据）

- A-M6-01～03维持上一轮挂账，未无关扩审；未保存输入、视觉/文本收口等建议不因本轮未修新增P1。
- 修正CONTEXT/实施报告中的旧身份/provider/launcher授权说法，明确“静态点检通过”和“实际功能通过”。当前候选已可定位，不因报告措辞单独判FAIL。

## 全部硬验收与相关既有用例

|硬验收|本轮结果|
|---|---|
|1 三角色持续追踪、搜索/收藏/重登/项目|FAIL D04失败结果与收尾；双主体/version源码子项符合；可信原生角色/重登/项目检查BLOCKED|
|2 三条真实AI链、失败/空历史出口|FAIL D03新增链②③缺失；空历史/外主体隔离子项符合；真实模型NOT_RUN|
|3 提醒恢复/去重/旧作业/跳回|FAIL D02恢复；终态/预约/撤权/去重/跳回控制流子项符合；目标宿主重启/grant BLOCKED；仅前台扫描，不称后台常驻|
|4 视口/放大/键盘|BLOCKED；无当前候选真实截图/交互，不用源码尺寸或HTML结论冒签|
|5 输入/选择/滚动/错误恢复与原台账|FAIL D02/D04恢复；D01/D05回归保持；真实原生BLOCKED；原P0/38业务/12UI及历史完整保留|

|用例|本轮状态与实际范围|
|---|---|
|G0-F|BLOCKED后台/官方任务卡；本轮前台提醒去重/有效性子项符合，恢复FAIL D02|
|T17|BLOCKED真实断线/全量回读/不重复写；未把磁盘load等同SSE回连|
|T18|历史task/actor/project过滤、适配撤权隐藏子项符合；可信搜索/事件/附件全投影BLOCKED|
|T23|FAIL D02异常读取/保存恢复；去重/终态/预约子项符合；实际进程重启与一份站内通知BLOCKED|
|T25|NOT_RUN真实模型缺失/矛盾/恶意原文；D03新增链缺失，不声明模型无虚构|
|T26|NOT_RUN真实模型失败/人工继续；D03待补，静态未知不代真实失败测试|
|T28|BLOCKED原生同task操作/权威回读/重开；本轮Store安装及重建仅安装子项PASS|
|T29|BLOCKED真实grant关闭/退出/到期及共享卡；适配撤权跳回拒绝子项符合|
|T30|FAIL D04偏好失败/回执；version不变、双主体收藏/取消子项符合；真实重登BLOCKED|
|T33|NOT_RUN真实意图泛化；D03新增AI场景缺失，M3原挂账保留|
|T34|FAIL D03新增事实引用/依据链缺失；空历史出口符合；真实不存在引用拒绝NOT_RUN|
|T35|BLOCKED真实迟到建议、改派/改约、固定请求上下文；recordModelMeta现有兜底未修，前序结论不冒签|
|T36|NOT_RUN真/假内核白名单契约；只读history不代完整模型工具安全|
|T38|当前源码/配置/宿主/digest已固定；真实模型/提示/数据成功失败复跑BLOCKED/NOT_RUN，D03未闭合|
|U01|BLOCKED三角色真实首屏/当前任务与下一步；nav计数无副作用回归符合|
|U02|BLOCKED真实草稿/歧义/人工失败出口；M3挂账，本轮未扩修|
|U03|BLOCKED可信三角色事实/权限及独立验收；合成主体不代登录，M5挂账|
|U04|BLOCKED真实预约/改约冲突与过期；D01formatter保持、D02预约旧提醒子项符合|
|U05|BLOCKED真实安装/服务空间/设备来源可读；D03新增依据建议缺失|
|U06|BLOCKED实际进度/完工/验收/退回历史附件；前序M5 FAIL保持|
|U07|FAIL D02/D04恢复；真实重复/响应丢失/离线/重启BLOCKED|
|U08|FAIL D02空/读失败及异常覆盖；无历史未知出口符合；真实空态/附件/无权限出口BLOCKED|
|U09|BLOCKED三个原生视口、150%及长中文|
|U10|BLOCKED原生全键盘/焦点/对比与非颜色线索|
|U11|FAIL D04偏好异常收尾影响连续使用；D05计数保持；原生滚动/输入/面板BLOCKED|
|U12|NOT_RUN同版本2–3分钟实际结果与失败/空态演示|

定义来源：05_IMPLEMENTATION_ACCEPTANCE.md的T17/18/23/25/26/28/29/30，09_AGENT_HARNESS.md的T33～38，10_UI_UX_SPEC.md的U01～12及M6硬验收。没有沿用CONTEXT中将T30误写成改约的映射，未删减或重写原验收。

## 判定

- 最终结论：**FAIL**。精确范围为M6-r3相对上一轮D01～05闭合及受影响回归；不做无关扩审。
- 本模块必修：D02异常读取与不覆盖恢复/保存结果贯穿；D03既定新增链②③的事实来源、固定请求绑定与真实接线；D04偏好实际异常收尾、读回/回执与失败恢复。建议不作为拒收原因。
- 解阻及未测：B01安全原生环境；随后用已裁决身份/provider完成真实三角色、重启/撤权、模型/UI/权威结果复验。本轮没有满足原生或模型必需检查，不能用“核心静态有改善”给PASS。
- 受影响前序：23函数差异与局部回归已核；M0～M5真实运行结论未重签，M5-r4仍FAIL，不修其原缺陷。
- 门禁：仅更新GATES M6 status和审查字段并保留来源历史，review_report指向本报告；原ACCEPTANCE.json、其他模块保持原状。末核候选/非M6字段一致，证据见final-verification。
- 下一模块：**不允许；未执行；不给M7入口。** 构建方仅按本轮D02/03/04修复并交新候选，保留D01/D05改善，再独立复审。
- NEEDS_ABRAM=no：本地离线签名/安装可行且两私钥已删；身份/provider已经裁决；本审0次真实模型请求，没有余额/402/欠费错误。剩余是代码、原生隔离环境和运行证据，不是新的Abram授权。

STATUS=FAIL
NEEDS_ABRAM=no
