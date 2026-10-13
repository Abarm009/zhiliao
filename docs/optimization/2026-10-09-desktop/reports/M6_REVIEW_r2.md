# M6 独立 Review r2

**最终结论：FAIL。** 上轮 D-M6-02、D-M6-03、D-M6-04 仍有直接阻断核心功能或授权隔离的 P1；D-M6-01、D-M6-05 原源码问题已修正，原生端到端验证仍 BLOCKED。没有因建议项或前序模块挂账判 FAIL。

- 审查者 / 日期：Codex 当前主会话，2026-10-10 Asia/Shanghai；唯一审查方，无子代理。
- 候选：`M6-r2-worktree`；基线：`M6-r1-worktree`。以 GATES、`reports/M6_IMPLEMENTATION_r2.md` 和 `M6/r2/CANDIDATE.json` 的同一交接定位，不按修改时间选版本。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；候选为未提交工作区，不能只凭 HEAD 定位。主源 SHA-256：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`，283910 字节；r1 独立快照 SHA-256：`321c9298d73104302eb005487cd7727555266cdfdbc03d0898eab0e24931af1d`。已保存完整快照、增量差异，开始/结束哈希须一致，见 final-verification。
- 前置：M5 r2 = FAIL，没有已接受 PASS 候选；按 Abram 本次前序挂账授权继续本模块复审。保留 M5 及 M0～M4 原结论，不修其缺陷，不将其算本轮新增 P1。
- 宿主：指定 `M0/r3/host/app-extracted/OctoSense.app`，0.1.0-rc.1 / build 20261008.091752；launcher SHA-256：`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮未启动 launcher，未调用 `--help`。
- 路由 / 标题：当前工具无法核验或切换主会话 Router/provider，也无当前对话 createdAt/标题写入接口；未声称已经切换或实际改名。受本次“只读写项目内”约束，未读取项目外记忆或技能文件。
- 已读范围：AGENTS.md、先读 CONTEXT_M6.md、上轮 M6_REVIEW_r1、r2 实施交接/候选/修复脚本、04_REVIEW模板、M6 本轮硬验收；其余基线按 CONTEXT 与上轮报告定位，仅读 D01～05 涉及的函数、模型配置、相关 UI 消费端和官方本地 Store 探针。未重新通读全部基线，未无关扩审。
- 写入范围：本报告、GATES.json 的 M6 status/审查字段/审查历史，以及本轮隔离审查证据。没有修改业务代码、原业务数据或其他模块，没有启动 M7。
- 证据根：`runtime/optimization/2026-10-09/M6/review-r2/`。下文证据路径均相对此根。
- 置信度：候选匹配、官方 Store 实际命令结果、源码调用关系 **高**；Splash 控制流译码与 VM 等价性 **中**；真实原生交互、可信角色会话、权威业务结果、真实模型行为 **未知**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与新增差异|逐项实读主源、manifest、身份及模型配置哈希；对比 r1 独立快照|交接一致、增量可定位|主源与 r2 清单一致；r1 基线一致；保留增量与快照|PASS（定位）|results/candidate-check.json、source-snapshot.splash、M6-r1-to-r2.diff|
|隔离预检与清理能力|本轮 HOME/CFFIXED_USER_HOME/TMPDIR/XDG/OctoSense 数据/Metal 缓存重定向；deny 外写和网络的 sandbox 执行 true；枚举指定宿主|可确保隔离，后台启动后能杀进程并确认无窗口|新执行 sandbox-exec rc71，sandbox_apply: Operation not permitted；pgrep rc3，Cannot get process list|BLOCKED；不启动 launcher|results/preflight.json、runtime-metadata.json、isolation.sb|
|当前包本地安装|离线生成本轮 key/catalog、stamp、签 manifest；官方 Store::install_staged → 重建 Store → may_run；篡改后拒绝、恢复再试|当前包离线安装和完整性验证成立|安装及 Store 重建 rc0，篡改 rc1，恢复 rc0；三份安装源内容与候选一致|PASS（本地 Store，非原生应用运行）|results/local-store-validation.json；store-test/|
|私钥销毁|签名脚本 finally 删除，结束再列 keys 目录|无私钥遗留|anchor.key、working.key 已删除，remaining_key_files=[]|PASS|local-store-validation、final-verification|
|首次使用三角色与收藏|真实桌面首屏、搜索/待办/收藏/跨项目/重登；另译码实际 togglePin/命令/存储/锁函数|任务与下一步清楚；收藏不污染业务版本、不妨碍下一操作|原生不可安全启动；version 4→4 已修，收藏后 tasks.lock 非空，下个命令返回 false|FAIL D04 源码/adapter；原生 BLOCKED|source-probes 的 favorite_*、next_bound_command_allowed；D04|
|提醒恢复/去重/撤权/旧作业|固定时钟、同秒多任务、重复登记、关闭准确条目、角色/可见性切换、落盘清空再加载、终态旧记录及损坏文件注入|有权且到期有效才展示；准确恢复，损坏明确可恢复|到期/撤权闸、同秒唯一ID、去重、准确关闭和保存失败标记成立；终态 ACTIVE 仍展示，损坏读取无错误状态|FAIL D02；真实宿主重启 BLOCKED|source-probes；D02|
|历史依据和阶段|向实际 history 函数注入另一任务/项目/主体的 APPLIED 日志；清空日志；检查来源生产端、模型入口和 UI|不带出无权资料，无历史明确未知；设备/事件建议有真实依据链|外任务 provider/model 被展示；空历史仍“已读1条历史依据”；静态阶段已标非模型，但链②③仍没有模型接线|FAIL D03；真实模型 NOT_RUN|source-probes；main.splash:811、2713、6139；D03|
|真实原生视觉和交互|本候选三尺寸、150%、长中文、焦点、键盘、正常/异常截图和权威结果|真实可达且流程可恢复|launcher 未运行，没有当前候选原生操作证据；未采用 HTML 测量或旧截图判原生通过|BLOCKED / NOT_RUN|preflight；runtime-metadata|
|受影响回归|比对15个相关函数；运行 task/单预约 formatter、all/fav/todo 计数及异常恢复；核取消/改约 hooks|修复不破坏相关旧契约|10个函数内容相同，5个变化可定位；formatter 双形态一致且含实际时段，nav 正常/异常均恢复；新增收藏存储遗漏命令收尾|D01/D05 原源码问题修正；D02/D04 仍 FAIL|results/affected-regression.json、source-probes.json|

本轮独立控制流探针 **28项，20项符合预期、8项不符合**；不是原生应用测试通过率。以当前函数体译码，固定时钟和隔离文件系统；身份、权限、版本读取、源状态、指纹和 receipt 查找为明确 adapter。收藏复现使用实际译码 `runCommandBound / runCommand / _acquireTaskLock / togglePin / m6_save_prefs`，不是凭 stub 返回成功推断锁状态。没有把译码结果写成原生 VM 已观察到的崩溃或可信业务回执。

译码 harness 的 JSON 字符串花括号处理、nil 属性、try/catch、Python 作用域作等价适配，详见 runtime-metadata；早期 harness 错误修正仅在本轮审查脚本。作者修复脚本复制到本轮目录独立复跑仍 **20/20 PASS**；它只查字符串和分支存在，未覆盖上述失败。未覆盖作者原证据、未重跑会删除 r1 sandbox 的全套 driver，也不把作者沿用的168项算本轮独立验证。

本轮独立离线安装 digest 为 `883f5b1d763efeadbb9cf820cddcf06b492a4ccac0ff8098f26aca2d12767ed0`，以本轮隔离包实测为准；不复用作者或前轮 digest。包中既有 screenshots 只作为原素材随包复制，不是本轮原生截图。未联网、上传、publish、listing、push、发消息或配置模型。

### 上轮缺陷闭合表

|编号|本轮状态|精确边界|
|---|---|---|
|D-M6-01|原源码缺陷 FIXED；目标宿主验证 BLOCKED|formatter 兼容真实单预约与任务形状，适配探针输出一致且包含确认时段；真实确认→提醒→重启仍未运行|
|D-M6-02|PARTIAL / OPEN / P1|时间/visible/actor闸、ID递增、取消hook、提议改约保留旧提醒、保存失败标记已补；任务终态/旧预约有效性、损坏与持久化失败恢复仍不完整|
|D-M6-03|PARTIAL / OPEN / P1|日志字段扩展与静态标注已补；全局 APPLIED 兜底跨任务展示，无历史文案仍错；新增AI链②③仍未接通|
|D-M6-04|PARTIAL / OPEN / P1|不增加version已修；拆出偏好写入后遗漏释放锁、命令结果收尾与失败恢复，阻断下一操作|
|D-M6-05|原源码缺陷 FIXED；目标宿主验证 BLOCKED|nav正常和异常路径均恢复，诊断label初始空文本；原生首屏/刷新/筛选保持未验证|
|A-M6-01～03|原建议继续挂账|不因建议项判FAIL，不扩成必修；原编号和来源保留于r1报告|

### 全部硬验收

|硬验收|本轮结论|
|---|---|
|1 三角色持续追踪、搜索/收藏/重登/跨项目|FAIL D04阻断收藏后的连续使用；三角色真实流程与重登BLOCKED；D05源码子项修正|
|2 三条真实AI链、失败和无历史人工出口|FAIL D03：新增链②③未接通、来源隔离/无历史仍错误；真实模型全部NOT_RUN，静态阶段非模型标注成立|
|3 提醒恢复/去重/旧作业/跳回|FAIL D02剩余恢复与有效性；到期/撤权/去重子项改善；真实宿主重启BLOCKED；G0-F后台常驻仍BLOCKED|
|4 视口/放大/键盘|BLOCKED：三尺寸、150%、长中文、焦点、实际对比和键盘均NOT_RUN；不编造视觉缺陷|
|5 跨模块一致输入/选择/滚动/恢复及原台账责任|FAIL D02/D04恢复/命令生命周期；D05源码修正，原生输入/滚动BLOCKED；既有P0/38业务/12UI定义及历史不改|

### 相关既有用例逐项复核

沿用r1对原编号含义的核对，仅更新本轮修复涉及结论；未扩审其他模块。

|编号|本轮结论与范围|
|---|---|
|G0-F|BLOCKED：后台常驻未证明；仅前台扫描，提醒源码有效性/恢复D02仍FAIL|
|T17|BLOCKED：实际SSE断线重连/全量回读/不重复写未运行；身份标签切换不代替|
|T18|FAIL D03外任务历史元信息混入；提醒visible=false/banner拒绝子项已修；全面可信授权/原生出口BLOCKED|
|T23|FAIL D02终态旧提醒/损坏恢复；去重、ID、显式取消及文件加载子项成立；真实宿主重启和一份通知BLOCKED|
|T25|NOT_RUN：真实模型矛盾/缺失/恶意输入与未知处理；不直接业务写仅历史函数源码子项成立|
|T26|NOT_RUN：真实模型失败与人工继续未运行|
|T28|BLOCKED：同task_id原生操作/权威回读/重开；当前digest本地Store重建安装子项PASS|
|T29|BLOCKED：可信grant退出/到期/关闭未运行；跳回拒绝和提醒撤权adapter子项成立，历史隔离D03仍FAIL|
|T30|FAIL D04：version不增子项成立，锁/命令收尾阻断后续；真实双用户收藏/取消/重登BLOCKED|
|T33|NOT_RUN：真实模型多自然表达意图泛化|
|T34|FAIL新增历史来源/链②③D03；真实无历史/追问/不存在引用模型行为NOT_RUN|
|T35|BLOCKED：真实迟到建议与受影响确认未运行，M3/M4挂账；提议改约不提前清旧提醒源码子项已修|
|T36|NOT_RUN：真实/假适配器白名单及内核替换契约；未更换provider|
|T38|BLOCKED：未形成同真实模型/提示/数据/宿主固定场景复跑；源码/宿主/digest可定位，不把adapter算完整用例|
|U01|BLOCKED：三角色真实首屏/下一步；D05nav源码子项修正|
|U02|BLOCKED：真实原话→可改草稿/歧义/模型失败人工继续；M3挂账|
|U03|BLOCKED：可信三角色同任务事实/权限/独立验收；M5挂账|
|U04|BLOCKED：预约/改约/冲突/过期真实UI；D01formatter已修，D02旧提醒有效性仍FAIL|
|U05|BLOCKED：安装/服务空间与依据实际可读|
|U06|BLOCKED：进度/完工/验收/退回历史和附件原生UI；M5挂账|
|U07|FAIL D02损坏恢复、D04锁/命令收尾；实际响应丢失/离线/重启恢复BLOCKED|
|U08|FAIL D02损坏读取静默；实际错误/空态出口BLOCKED，A02未保存提示仅建议挂账|
|U09|BLOCKED：1440×900、1280×800、980×760、150%实际交互NOT_RUN|
|U10|BLOCKED：键盘全流程/焦点/对比/非颜色线索NOT_RUN|
|U11|BLOCKED：原生滚动/输入/面板；D05筛选副作用源码子项修正，D04连续使用仍FAIL|
|U12|NOT_RUN：本候选2–3分钟实际结果及失败/空态演示未交付；摘要入口不代替演示|

## 缺陷

以下均沿用上一轮编号，只列仍阻断核心或违反授权隔离的问题为P1。文件行以本轮哈希快照为准。

### D-M6-02 / P1 / 必修 / 未闭合：提醒持久化失败恢复与旧作业有效性不完整

- 文件与行：`app/bundle/main.splash:942`（损坏读catch→nil）、`:945`、`:946`、`:959`（写失败标记）、`:996`（忽略保存结果）、`:1037`、`:1038`（关闭失败仍返回true）、`:1064`～`:1068`（存在/visible后直接保留，无终态/预约闸）；取消任务hook`:4434`已补。
- 触发：仅在本轮隔离数据注入“任务已CANCELLED，但旧kickoff_checkin仍ACTIVE且到期”的恢复记录；再将隔离follow_ups.json损坏为非法JSON，清空内存重新调用load。该终态/旧记录组合是持久化局部失败的恢复反例，不是对原业务数据改状态。另对save注入写拒绝。
- 实际/预期：到期旧记录仍显示1条；损坏读取返回且既不报错也不设待恢复，后续保存可覆盖剩余历史。写失败本身已返回false/dirty，调用方仍不处理成功与持久化失败的区别。应以当前有效任务/预约决定旧作业，损坏或失败明确保留待恢复，不把读失败默当无提醒。
- 根因：仅增加到期/可见性闸，没有预约/终态有效性；持久化返回值未贯穿登记/关闭/失效；load依旧吞异常。dirty只在save中设置/清除，没有完整恢复路径。
- 影响：重开丢提醒或重新显示已失效提醒，核心T23跟进恢复不成立。取消hook、同秒ID及撤权显示修正不能替代故障恢复。
- 证据：results/source-probes.json 的 `terminal_task_active_not_shown`（1≠0）、`corrupt_load_reported`（false≠true）、`write_failure_reported/dirty`成立；当前快照与diff。
- 具体改法：保留现有前台路线；存稳定appointment_id/接收主体并在读/展示/跳回时核有效状态，明确取消/完成终态及预约替换规则；load区分首次无文件与损坏，保留可恢复旧文件/错误状态；保存失败结果向调用方传递，提供最小可验证重试，不能返回“已关闭/已保存”成功状态。不扩做后台服务。
- 验证：本候选原生确认→到期→关闭→重启，恰一份；改约提议/拒绝/确认、任务/预约取消、撤权无旧通知；只在隔离目录做写拒绝/损坏/退出后重开，验证错误可见、恢复不覆盖原数据、重试不重复。

### D-M6-03 / P1 / 必修 / 未闭合：设备历史跨任务混入，新增AI链仍缺位

- 文件与行：`main.splash:811`、`:823`～`:840`（只按task_id，无项目/主体来源核验）、`:842`～`:851`（所有非本任务APPLIED进入本页）、`:857`、`:872`（固定阶段）、`:2713`、`:2734`～`:2749`（绑定当前选中项/主体）、`:6139`～`:6152`（UI消费）。
- 触发：当前查看task-A/project-A/actor-A，在全局日志放task-B/project-B/actor-B的APPLIED记录，provider标识为PRIVATE-PROVIDER-B；读取task-A设备历史。再清空日志读取；查既定接单后设备/历史/预约占用建议及事件变化阶段建议入口。
- 实际/预期：外任务provider/model元信息进入task-A历史，kind=device；没有日志时也显示“已读1条历史依据”，实际只有静态阶段，UI不进入无历史出口。链②③仍没有调用/版本/事实引用接线。日志字段已扩、阶段已标非模型，但不等于设备历史与AI链实现。应排除未获本任务授权的记录，无业务历史明确未知，并提供真实有引用的既定AI场景。
- 根因：把“非本任务”当作unbound而全局兜底展示；元信息陈列替代设备历史事实；静态阶段塞入history计数；生产绑定兜底取实时UI上下文而非请求固定上下文。未补上轮要求的设备/历史/占用读取与新增链②③。
- 影响：跨任务/项目/主体审计元信息混入，无历史与事实来源误导；M6核心AI场景未实现。未声称泄漏问题全文或已观察真实模型虚构输出。
- 证据：source-probes 的 `foreign_task_history_excluded`（实际含外任务元信息）、`no_history_unknown`（实际“已读1条历史依据”）；source_checks.real_AI_call_in_history_or_phase=false；当前requestAiSuggestion只报修草稿流程，model_config.enabled=false，作者明确链未运行。
- 具体改法：删除全局非本任务APPLIED兜底；每条来源核任务/设备/项目/请求主体、当前授权与版本，绑定采用请求发出时的固定上下文，缺绑定标未知而非挂到当前选中任务；静态阶段与真实历史数量分开，无历史note明确未知；在已有来源/校验/过期契约内接链②③，来源不存在不得编造。复用已有授权配置；不为静态PASS偷偷启用provider。
- 验证：本任务有历史/空历史、其他任务/项目/主体、显式无绑定、矛盾与不存在引用、事件变化/迟到响应分别独立存证；记录模型、请求固定版本、实际引用及人工出口；建议不直接写业务。若后续确证必须新增真实provider配置或业务身份来源，再记录具体NEEDS_ABRAM依赖，本轮未配置。

### D-M6-04 / P1 / 必修 / 未闭合：偏好保存不再推进版本，但遗留全局任务锁

- 文件与行：`main.splash:4483`、`:4495`（进入runCommandBound）、`:4508`（偏好写入）、`:1177`～`:1183`（没有结果收尾/锁释放）；锁`:1584`、`:1589`、`:1600`；命令持锁上下文`:1608`、`:1703`；原释放位置`:1838`，原pending清理`:2021`～`:2023`。
- 触发：隔离tasks.lock初始为空，任务version=4、当前actor获准收藏；运行当前togglePin，随后再通过当前runCommandBound执行下一合法命令。
- 实际/预期：version保持4，已修；偏好写入返回后锁仍为`actor-A@1000@0`，_PENDING_CMD仍togglePin；下个命令返回false，进入concurrency_lost。应收藏成功后释放命令锁、精确收尾自己的回执/上下文，下一命令可用，偏好不影响业务version。
- 根因：去掉commit/commitBound同时去掉其finalize、释放锁及清理pending责任，m6_save_prefs只写tasks/state；失败也无finally收尾。结果是M6新增偏好路径的生命周期断裂，不要求重写M2。
- 影响：一次收藏阻断同目录后续业务操作，无法持续使用。还留下未完成回执/上下文；当前recordReceipt的status语义沿用前序，不能声称已独立证明完整回执final。
- 证据：source-probes 的 favorite_version_unchanged=4、favorite_lock_released为非空、favorite_pending_context_cleared=togglePin、next_bound_command_allowed=false、next_command_can_acquire=false；实际译码命令/锁/存储函数与隔离tasks.lock，source_checks显示无释放/精确finalize调用。
- 具体改法：最小新增经现有授权/幂等边界的偏好提交收尾：成功后读回偏好、按唯一action_id精确结束结果，不推进业务version；失败明确可重试/待核验；所有退出以finally式保证锁释放并清理本次pending，不改别的回执。不要仅加_releaseTaskLock而漏掉幂等/失败结果。
- 验证：收藏→另一业务动作真实成功；收藏/取消/重登、同key重试和双主体隔离；version和其他业务字段不变；写拒绝/state保存异常/读回不一致后仍可继续安全操作、没有残锁或错误final。

## 判定

- 最终结论：**FAIL**；候选`M6-r2-worktree`。必须修D-M6-02、03、04；D01/D05源码反例已消除，不要求重复改动。建议A01～03继续挂账，不因其拒收。
- 结论范围：当前候选源码/独立控制流和当前digest官方本地安装已审；真实原生流程、重启、可信权限、模型和UI验收均不能由这些替代。核心尚有P1，不能按“完成比完美重要”放行。
- 原生解阻条件：在能执行隔离策略、枚举/结束进程并核无残留窗口的环境重跑最小预检；通过后后台启动指定launcher，所有HOME/app-data/log/cache在本项目隔离根，测完立即关闭。用户已经授权该测试动作，CONTEXT里“禁止后台启动”是过时解释，不沿用；本轮仅因隔离/清理能力预检失败而不启动。无须新发布授权。
- 本地catalog/install_staged路径可行，不能把它写成NEEDS_ABRAM或要求公开发布。两份离线私钥已经删除，有删除及结束目录证据。
- 真实模型：当前enabled=false，既定新增链尚未实现；先修来源/接线/人工出口，禁止擅自配置/更换provider。尚未确证修这些代码必须新增模型provider或身份来源，本轮不申请这些动作，**NEEDS_ABRAM=no**；这是当前修复依赖判定，不是宣称真实模型已可运行。
- 门禁：GATES.json仅更新M6本轮status、候选审查字段、report、证据与历史；前轮/作者状态保留来源。ACCEPTANCE.json与其他模块不修改，原业务/UI定义不降级、不删除。
- 下一模块：**不允许；未执行；不给M7入口。** 构建方只按本报告D02/03/04定向修复并交新候选，保留D01/D05修正及建议挂账，再独立复核受影响回归。

STATUS=FAIL
NEEDS_ABRAM=no
