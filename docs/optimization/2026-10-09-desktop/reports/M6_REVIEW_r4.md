# M6 独立 Review r4

**最终结论：FAIL。** 候选 `M6-r4-worktree` 对上一轮 D-M6-02/04 有实际改善，但异常恢复仍存在反例；D-M6-03 两条新增 AI 链明确未实现。三条原 P1 均未完全闭合。没有因挂账建议、M5 前置 FAIL 或视觉未测单独新增 P1。

- 审查者 / 日期：Codex 当前 Astra 主会话，2026-10-11（Asia/Shanghai）；唯一审查方，无子代理。不能声明主会话为 gpt-6.1-sol 或已经切换到 Router。
- candidate_id / base：`M6-r4-worktree` / `M6-r3-worktree`；由 GATES、r4 实施报告、`M6/r4/CANDIDATE.json` 三方定位，不用文件时间确定交接。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作区未提交；主源 SHA-256：`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`，与交接匹配。候选把文件摘要写作 head_sha 的字段仅是文件摘要，不是 Git commit。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r4.md`。
- 前置：M5 r4 独立 Review 为 **FAIL**，候选 `M5-r4-worktree`；没有已接受 PASS 候选。按本次明确挂账授权继续本模块复审，保留 M5 结论，不修前序模块。
- 宿主：指定 M0/r3 `host/app-extracted/OctoSense.app`；0.1.0-rc.1 / 20261008.091752；可执行文件 SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮没有启动宿主。
- 已阅读：先读现有 CONTEXT_M6；实际 AGENTS、00/01/02、M6 指令和 04 模板；r3 缺陷、r4 实施报告/清单/证据；D02/03/04 函数及命令、回执、预约调用端；M5 前置、相关既有验收定义沿用 r3 已列精确映射。没有无关扩审。
- CONTEXT 的身份/provider 未授权、禁止后台启动说法已过时，由当前用户裁决覆盖。5 账号和 MiniMax 来源已获授权；没有读取明文凭据或密钥，没有修改原身份数据，没有真实模型调用。
- 证据根：`runtime/optimization/2026-10-09/M6/review-r4-independent/`。作者已经使用 `review-r4/` 写自测，本轮另建目录保留原证据；作者复跑旧审查脚本不自动成为独立审查。
- 开始保存 GATES、源码快照及主源/manifest/model_config/候选/原台账摘要；结束核同一快照，见 `results/final-verification.json`。r3→r4 精确差异见 `results/M6-r3-to-r4.diff`；业务变化集中在提醒加载/保存/登记、偏好保存与 togglePin。函数文本比对另含前置注释变化，不将其误报为新增业务改动。
- 实际运行：隔离预检；旧 42 条控制流探针独立复跑；原缺陷相关 10 条补充探针；当前 digest 离线 catalog / 官方 Store::install_staged / Store 重建及 may_run / 篡改拒绝 / 恢复重试。
- 未运行：真实原生三个可信角色首次使用/重登、宿主进程重启、grant 生命周期、业务权威回读、真实模型三条链、当前原生视觉/键盘/放大/滚动及演示。分别标 BLOCKED/NOT_RUN，未用作者声称、HTML 原型或旧截图替代。
- 写入：本报告、GATES 的 M6 status/审查字段/审查历史、本轮隔离证据。业务代码、其他模块、原 ACCEPTANCE.json 和原始业务数据均未修改；没有进入 M7。
- 标题：当前可用工具没有当前会话 createdAt 和改名接口；没有猜日期或声称已实际改名。受项目内访问限制，没有读取项目外记忆/技能。
- 置信度：版本定位、源码分支/调用次序和本地安装 **高**；Splash→Python 控制流适配 **中**；原生 UI/会话/权威业务和真实模型 **未知**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据（相对证据根）|
|---|---|---|---|---|---|
|候选/宿主/前置|核三方交接、主源摘要、宿主 plist/二进制、r3差异|版本明确且前置如实|当前摘要匹配；M5 r4 FAIL 保留；增量定位|定位 PASS；前置未 PASS|results/start-hashes.json、candidate-and-regression.json、M6-r3-to-r4.diff|
|外写隔离与测试退出条件|新建 HOME/CFFIXED_USER_HOME/TMPDIR/XDG/app-data/Metal缓存根；deny外写/网络预检；进程枚举|保证项目外零写入及测后关闭/无窗口残留|sandbox rc71；pgrep rc3；未启动 launcher|BLOCKED B01|isolation.sb、results/preflight.json|
|首次使用三角色|需真实登录后的原生首屏、当前任务/下一步及跨项目追踪|可信身份下信息明确、事实一致|无安全原生运行条件；合成主体不能替代登录|BLOCKED|preflight；作者未运行|
|收藏隔离与失败恢复|两合成主体收藏/取消；version检查；拒写tasks/state；finalize写失败；写后读回不一致|偏好隔离、版本不变、失败可继续且结果可核|正常隔离/version/清锁成立；state失败pending、finalize失败假成功、读回缺失仍存在|FAIL D04；原生重登BLOCKED|results/review-probes.json、residual-probes.json|
|提醒恢复/去重/旧作业|登记重复提醒、清内存load、终态/改约/撤权过滤；异常文件→登记新提醒|有权且有效才提醒；异常原文不覆盖，恢复未决不假成功|正常子项保持；新增登记绕过dirty+空保护、覆盖异常原文并清dirty|FAIL D02；进程重启BLOCKED|两个probe JSON、residual_probes.py|
|撤权跳回与旧提醒|显式授权adapter撤权后调jump/unread，核预约失效调用|无权拒绝、旧预约不显示、不继承grant|适配控制流符合；真实grant退出/到期及官方卡未运行|源码子项符合；完整BLOCKED|review-probes.json、源快照|
|历史依据/阶段/模型边界|核history/phase/model日志生产端及r3差异；外任务/主体/项目、空历史|真实有权事实、固定请求上下文、无历史未知、模型建议不直写业务|隔离/未知子项保持；history为审计字段、phase静态；新增链未实现且context兜底仍取当前UI|FAIL D03；真实模型NOT_RUN|candidate-and-regression、源:1286/1348/3725；作者r4§2.2|
|真实原生视觉与交互|需三视口、150%、长中文、键盘/焦点、正常异常截图|当前原生关键内容可达、主动作可用|无当前原生执行；不继承HTML或旧截图结论|BLOCKED；演示NOT_RUN|preflight、r4报告明确未运行|
|当前digest本地安装|离线keygen/certify/stamp/sign-manifest/verify；install_staged、Store重建/may_run；篡改、恢复|当前包可安装；篡改拒绝；恢复成功|当前包安装/重建rc0、篡改rc1、恢复rc0；源码/配置/identities安装字节一致|PASS安装层|results/local-store-validation.json、store-output-venv.txt|
|私钥删除|签名finally删除两key；结束检查|仅sandbox签名、无残留私钥|working.key与anchor.key删除，remaining_key_files=[]|PASS|local-store-validation、final-verification|
|受影响回归|r3差异；D01双形态formatter、D05正常/异常nav恢复；D02过滤；D03来源；D04version/双主体|保留已成立子项；不替前序签PASS|旧探针42/42匹配；补充探针发现原缺陷剩余反例|局部回归符合；异常恢复FAIL|两个probe JSON、diff|

旧探针本轮独立复跑 **42/42 匹配预期**。补充 **10 条：8 条不符合恢复/核验要求，2 条仅确认清理已发生和异常仍向外抛出**，不能将后两条叫完整功能成功。所有探针从冻结 Splash 函数体转译，保留分支与调用次序；文件写入本轮隔离数据，时钟、身份/授权、命令 admission 为显式 adapter。它们不是发行 VM、可信人员、真实宿主重启或权威业务回执。

本轮离线 bundle digest：`8c103ab21fa27914a1ab4e5af450871d8ac5dfbf4a08ab7dff2347cf7d591d22`。没有继承 r3 旧 digest 当本轮证据。系统 Python 缺 cryptography 的首次尝试在生成 key 前退出；使用项目既有 `backend/.venv/bin/python` 复跑成功，没有安装依赖或联网。只改本轮包副本；没有公开发布、listing操作、上传、push、消息或计费变更。Store重建证明安装恢复，不证明 launcher 已加载该包或任务运行。

### 上轮缺陷逐条闭合

|原编号|本轮状态|已成立改善|仍未闭合|
|---|---|---|---|
|D-M6-01|维持源码子项关闭|task与单预约formatter一致|原生时间UI仍BLOCKED|
|D-M6-02|PARTIAL，P1 OPEN|空/读失败可见；dirty+空直接save不覆盖；登记持续写失败返回空；正常有效性/去重保持|恢复未决时登记新记录仍覆盖原文；调用端未完整处理登记/失效保存失败|
|D-M6-03|PARTIAL，P1 OPEN|来源主体/项目/任务过滤、无历史未知、静态阶段标识保持|两条新增模型链未实现；请求日志不等于业务历史建议；固定上下文兜底仍未补齐|
|D-M6-04|PARTIAL，P1 OPEN|正常final状态、tasks失败内存回退、state异常时清锁/pending改善|state异常回执pending；final写失败被吞而UI成功；无写后读回；失败提示被旧状态覆盖|
|D-M6-05|维持源码子项关闭|正常/异常nav计数恢复保持|真实滚动/筛选/视口仍BLOCKED|

## 缺陷

### D-M6-02 — P1 / 必修 / PARTIAL：新增登记绕过恢复保护，仍会覆盖未恢复的提醒原文件

- 文件与行：`app/bundle/main.splash:1453`（schema异常置dirty）；`:1471`（只在列表为空时阻写）；`:1492`（写成功清dirty）；`:1510`～`:1513`（upsert先填非空列表并save）；`:1534`～`:1537`（登记二次save）；`:1554`/`:1583`（失效保存结果未贯穿）；`:4368`（预约调用端丢弃登记返回）。
- 触发：隔离文件写 `{"other":["preserve-original"]}`→清提醒内存→load→register新提醒；另复跑空文件同路径。没有更改原业务文件。
- 实际：load报待恢复；register令列表非空，save保护失效，原schema文档被新 `follow_ups` 文档覆盖，dirty变false，登记返回ID。空文件同样被未经恢复确认的登记写覆盖。原42条只测“异常load后列表仍空→直接save”，漏测了正常登记会改列表的后续步骤。schema分支也没有作者所称额外 `.recover` 备份。
- 预期：恢复未决独立于列表是否为空；新增登记不能覆盖尚未恢复的源文件或把恢复状态清掉。失败/重试结果贯穿调用端；预约已提交与提醒未保存分别说明。
- 根因：同一个dirty混用了读损坏恢复与写失败重试；“内存非空”被当作原文件已经恢复，没有恢复协议。upsert/失效忽略save结果，登记新增返回值也未被预约调用方消费。
- 影响：原挂账D02要求的提醒异常恢复和不丢数据仍不成立，阻断硬3/5、T23/U07/U08；不是新增后台服务要求。
- 证据：`results/residual-probes.json` 的schema/empty注册保护四项反例；`residual_probes.py`；冻结函数及 diff；旧42条中登记写拒绝/正常load/过滤通过结果保留。
- 具体改法：在本路径区分“加载恢复未决”与“正常写待重试”；前者在任何普通upsert/dismiss/invalidate/save前保持阻写，保留原文件/备份，经过可核恢复才解除。后者针对同一记录重试并保持去重。将登记/失效保存结果传到现有UI调用端，不以填入一条新记录清除恢复未决。不要用只检查空列表或再加一次save作为修复。
- 验证方式：隔离空/损坏/schema/读拒绝→加载→登记、关闭、失效；核原文/备份仍可恢复，错误仍可见；明确恢复→同动作重试→恰一条→重开；改约确认/取消/撤权不复活旧通知。原生步骤待B01解阻。

### D-M6-03 — P1 / 必修 / PARTIAL：既定设备历史与事件阶段 AI 链仍未实现

- 文件与行：`main.splash:1286`/`:1316`（history只陈列请求审计）；`:1348`（静态阶段）；`:3569`（现有报修AI入口）；`:3725`/`:3739`～`:3758`（日志缺绑定时依当前选中任务/项目/主体）；作者r4§2.2、§4明确零代码修改且链②③未实现。
- 触发：接单后请求设备/维修历史/预约占用建议，或事件变化后请求最新阶段说明；核模型调用生产端与history/phase消费端；外任务/主体/项目和空历史探针保持。
- 实际：只有provider/model/result_kind元信息及固定状态解释；没有新增两条链的事实输入、引用、请求版本、过期拒绝、人工采纳和真实请求证据。与r3的history/phase/recordModelMeta函数完全相同。未观察真实模型输出，不能断言模型已不虚构。
- 预期：既定三链实际存在，新增链基于有权设备/任务/事件/占用事实，缺失标未知、不存在引用拒绝、回包与采纳检查固定请求上下文/版本、有人工出口、不直接写业务。
- 根因：把“未编造+静态未知出口”当作缺失核心功能的替代，并误称provider未授权。实际 `model_config.json` 为enabled=true、MiniMax-M3；用户已经裁决provider和账号来源，当前审查没有“等重新选provider”的授权缺口。
- 影响：本模块明确新增AI核心场景仍缺失，硬2/T25/T26/T33/T34/T35/T38不能成立。前序M3一般模型问题保留，不能用其挂账豁免本模块原D03。
- 证据：`results/candidate-and-regression.json`、源快照、42条的历史隔离/未知子项、作者r4§2.2。本轮0真实请求，没有读取密钥；绕过应用直接调用API也不能关闭该缺陷。
- 具体改法：只接原D03两条既定链，复用M3已授权适配及来源/版本/过期/错误契约；以请求发出时固定task/project/actor/事实版本为依据，不能回包时由当前UI派生。补有权设备/历史/占用与事件引用、缺项和人工采纳；模型仅读事实、只出建议。宿主接口不可行则给最小复现和BLOCKED，不虚报已实现，也不重新申请provider/身份选择授权。
- 验证方式：原生三链各新描述，空历史、矛盾/不存在引用、切任务/切主体/撤权/事件变化/迟到回包；记录模型/提示/数据/宿主及请求版本，检查无业务直写和人工出口。少量真实请求总数≤10；遇402/余额/欠费立即停止并原文报告NEEDS_ABRAM=yes。

### D-M6-04 — P1 / 必修 / PARTIAL：清理改善，偏好结果仍不能可靠收尾与读回

- 文件与行：`main.splash:1775`（tasks直写，无读回）；`:1778`～`:1780`（提前清上下文）；`:1798`（state异常跳过回执收尾）；`:1804`/`:1809`（只改status，吞final写异常）；`:6096`（调用无异常处理）；`:6106`（恢复旧status掩盖错误）。
- 触发①：隔离收藏时拒写state.json。②：允许初始pending落盘，第二次actions.jsonl写入，即finalize写入，拒绝。③：tasks写适配返回但读回保留旧值。④：tasks明确拒写后观察UI状态。
- 实际①：锁/pending上下文确已释放，但异常向外抛，原回执内存/磁盘仍pending，tasks已经收藏，未给可核恢复结果；源码调用端没有报告声称的异常回退。②：内存final、磁盘pending，UI仍“已收藏”。③：磁盘未收藏、内存已收藏却final，证明没有独立读回。④：pinnedBy回退改善，但“保存失败”被旧status覆盖。正常final状态并没有补result/finalized_at作为完整偏好核验事实。
- 预期：成功以当前主体偏好落盘读回和本次唯一action_id的持久结果为准；结果不明显示待核验、保留稳定键可对账；state/receipt异常不会永久pending或假成功；错误可见且能继续，业务version不增。已落盘的偏好不应盲目回滚冒充没执行。
- 根因：eager cleanup解决部分清理顺序，未覆盖偏好生命周期；saveState在收尾之前无保护，receipt失败被吞；把内存status改成final当作核验；失败路径恢复旧显示状态。
- 影响：本模块原D04的连续使用、收藏失败恢复与幂等结果仍不成立，影响硬1/5、T30/U07/U11。未把M4建议锁误称为强锁，也不扩修前序事务系统。
- 证据：`results/residual-probes.json` 的state_exception/ finalize_failure详情及读回/错误可见反例；`residual_probes.py`；源快照。旧42条的双主体收藏/取消、version=4、清锁、tasks拒写内存回退结果保留。
- 具体改法：仅补偏好提交收尾：捕获固定actor/action_id/原偏好，以写后读回区分已执行、未执行、未知；精确保存本动作结果和终结字段并核落盘。state/receipt失败走可见待核验/对账路径；所有退出清理仍保持；tasks未执行可回退，已执行则按读回恢复一致UI；不要吞receipt错误或覆盖错误状态，不能只改status字符串。
- 验证方式：收藏/取消/双主体/跨项目/重登及同key重试；拒写tasks、state、final回执，写后读回不一致；核原action持久结果、偏好和下一动作一致，无假成功、永久pending或业务version变化。原生重开待B01解阻。

### B-M6-01 — 必需运行 BLOCKED：无法保证项目内隔离与宿主关闭核验

本轮全新预检：sandbox-exec rc71，`sandbox-exec: sandbox_apply: Operation not permitted`；pgrep rc3，`sysmon request failed with error: sysmond service not found` / `pgrep: Cannot get process list`，原文保留在preflight.json。

仅重定向HOME不能证明发行宿主所有app-data/log/cache零外写，且无法可靠枚举/终止和核窗口残留。因此没有后台启动launcher、没有调用--help、没有新增宿主测试窗口；已有窗口状态未知，没有关闭或声称清理他人窗口。解阻需要能强制项目内写入约束、可靠管理测试进程并确认无残留窗口的运行环境；全部HOME/app-data/log/cache仍指向本轮隔离根。解阻后只运行本模块受影响原生流程，后台启动并finally立即关闭。当前catalog路径已实证可行，无需公开发布；此运行条件缺口不需要Abram新增授权。

### 建议挂账（P2，不作为FAIL依据）

A-M6-01～03保留，不做无关扩审。建议纠正CONTEXT/实施报告中已过时的授权与“作者复跑=独立通过”表述；静态测试总数不得重复累计或宣称功能闭合。这些文档建议本身不构成新P1。

## 全部硬验收与相关既有用例

|硬验收|本轮结果|
|---|---|
|1 三角色追踪/搜索/收藏/重登/项目|FAIL D04结果恢复；双主体/version源码子项符合；原生可信角色/重登/跨项目BLOCKED|
|2 三条真实AI链及人工出口|FAIL D03两新增链缺失；来源隔离/未知出口子项保持；真实模型NOT_RUN|
|3 提醒恢复/去重/旧作业/跳回|FAIL D02恢复保护；正常过滤/去重/磁盘load子项保持；目标宿主重启/grant BLOCKED；不称后台常驻|
|4 视口/放大/键盘|BLOCKED；未借源码尺寸、HTML或旧图放行；本轮未新增视觉P1|
|5 跨模块一致性与原台账|FAIL D02/D04错误恢复；D01/D05回归保持；原生BLOCKED；P0/38业务/12UI原定义和历史保留|

|用例|本轮状态与精确范围|
|---|---|
|G0-F|BLOCKED后台/官方任务卡；前台有效性子项保持，恢复FAIL D02|
|T17|BLOCKED真实断线/全量回读/不重复写；磁盘load不替SSE|
|T18|来源task/actor/project及适配撤权隐藏子项符合；可信搜索/事件/附件全投影BLOCKED|
|T23|FAIL D02；去重/预约/终态子项符合；实际进程重启和一份站内通知BLOCKED|
|T25|NOT_RUN真实模型缺失/矛盾/恶意原文；D03未闭合，不声明模型无虚构|
|T26|NOT_RUN真实模型失败/人工继续；静态未知不代真实失败测试|
|T28|BLOCKED原生同task操作/权威回读/重开；本轮Store安装层PASS|
|T29|BLOCKED真实grant关闭/退出/到期及共享卡；适配撤权跳回拒绝符合|
|T30|FAIL D04；version不变、双主体收藏/取消子项符合；真实重登BLOCKED|
|T33|NOT_RUN真实意图泛化；D03缺失，M3原挂账保留|
|T34|FAIL D03新增依据/引用链缺失；空历史出口保持；真实不存在引用拒绝NOT_RUN|
|T35|BLOCKED真实迟到建议/改派/改约；固定请求上下文兜底问题仍在D03|
|T36|NOT_RUN真/假内核白名单契约；只读history不代完整模型工具安全|
|T38|当前源码/配置/宿主/digest固定；真实模型/提示/数据成功失败复跑NOT_RUN，D03未闭合|
|U01|BLOCKED三角色真实首屏/当前任务/下一步；nav计数回归符合|
|U02|BLOCKED实际草稿/歧义/人工失败出口；M3挂账保留|
|U03|BLOCKED可信三角色事实/权限和独立验收；合成主体不代登录，M5挂账保留|
|U04|BLOCKED真实预约/改约冲突/过期；D01 formatter和旧预约过滤保持|
|U05|BLOCKED实际安装/服务空间/来源可读；D03新增依据缺失|
|U06|BLOCKED实际进度/完工/验收/退回历史附件；M5 FAIL保留|
|U07|FAIL D02/D04恢复；真实重复/响应丢失/离线/重启BLOCKED|
|U08|FAIL D02恢复保护；无历史未知保持；真实空态/附件/无权出口BLOCKED|
|U09|BLOCKED原生三视口/150%/长中文|
|U10|BLOCKED原生键盘/焦点/对比及非颜色线索|
|U11|FAIL D04偏好异常收尾；D05计数保持；原生滚动/输入/面板BLOCKED|
|U12|NOT_RUN同版本2–3分钟实际结果与失败/空态演示|

## 判定

- 最终结论：**FAIL**，仅针对已定位 `M6-r4-worktree` 的原缺陷复审与受影响回归；未运行项没有伪装成通过。
- 必修项：原 D-M6-02、D-M6-03、D-M6-04；按上文最小改法修复，不要求关闭P2或代修前序模块。
- 阻塞：B-M6-01运行隔离/进程清理条件；解阻后补本模块核心真实角色、提醒重启/撤权、收藏恢复、模型及原生交互证据。
- 前序回归：仅D01/D05与受影响预约/提醒/偏好/source子项；不改变M0～M5任何独立结论。
- 门禁：只更新GATES M6 status和审查字段，review_report指向本报告；审查历史保存旧来源。原ACCEPTANCE.json未改，未用本轮探针冒签全量台账。
- 下一模块：**不允许；未执行；不给M7入口。**
- NEEDS_ABRAM=no：账号、MiniMax、隔离离线签名已授权；本地安装路线成功；无模型请求/计费错误。本轮剩余代码/环境/验证问题不需要新增用户授权。

STATUS=FAIL
NEEDS_ABRAM=no
