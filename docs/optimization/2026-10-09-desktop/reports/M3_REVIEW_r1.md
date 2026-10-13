# M3 独立 Review r1

最终结论：**FAIL**。当前候选存在阻断真实输入、旧建议失效、项目事实校验和确认结果可信性的 P1；AI 与手工路径均没有当前原生端到端成功证据。桌面运行条件另为 BLOCKED，真实模型为 NOT_RUN。未修业务代码，未执行 M4。

- 审查者 / 日期：Codex 唯一主审，2026-10-10，Asia/Shanghai；无子代理。置信度：候选字节、源码控制流及 Store 实际运行结果高；原生运行语义/UI/真实模型效果未知。
- candidate_id=`M3-r1-worktree`；base_candidate_id=`M2-r1-worktree`；HEAD=`8d730569546cb57310944bb299695134df773b9d`。按 GATES 和唯一正式实施报告定位，未按文件时间选择。
- `main.splash` SHA-256=`f49768274816cdc2b1bf451a8e35af87e9fda9bb0a28c981e562467996c1f035`；`model_config.json` SHA-256=`2ebc087f6703af7be1c0c0cc12a484bf717b5e1fa58073c12f32ab23ca5b11f2`；均与 CANDIDATE.json 一致。开始/结束完整文件清单见 start/end-snapshot；最终核对见 report-verification.json。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r1.md`；上下文：`runtime/optimization/2026-10-09/M3/CONTEXT_M3.md`。本轮为首审，没有上一轮 M3 缺陷需要复审。
- 前置核对：M2 的独立结论为 BLOCKED（M2_REVIEW_r2），正式 r1 历史为 FAIL，无接受的 PASS 候选。按 Abram 前序挂账裁决继续诊断 M3，不以形式上的前置未 PASS 单独判本轮 FAIL。实际叠加基线是未交接 M2 修复快照 `edba9dc9…`，不是正式 M2-r1 主源 `2bef267a…`。本轮从保留的 r1 副本及 r2 unified diff 重建出该基线，SHA 完整匹配；已生成 base-to-m3.diff。能够定位差异不等于接受 M2。
- 实际环境 / 模型路由 / 宿主：macOS 本地命令；系统提供 GPT-6/Astra 主会话，无法独立确认 Codex Router 或切换至用户指定 gpt-6.1-sol，不冒充已切换。工具中没有本会话 createdAt/标题变更接口，未猜创建日期改标题。选定 launcher 为 M0/r3/host/app-extracted/OctoSense.app；octosense SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；kernel SHA-256=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。
- 阅读范围：实际 AGENTS、M3 CONTEXT、00/01/02/M3/04 模板、正式实施报告/候选/证据、M2 r2 Review 与相关源证据；根架构/迁移/核验入口及 13/14/15、旧 T/U 验收和桌面 v2 相关要求。本轮不把作者重新解释的用例名称替代原验收定义。
- 已运行：候选哈希、隔离预检、当前候选离线签名与官方 Store install_staged/restart/may_run、篡改拒绝及恢复重试；独立新合成输入/恶意回包的 Python 契约反例；逐函数源码控制流最小语法翻译探针。翻译保留原分支，依赖用明确 stub；不声称 Splash VM、实际 M2 或桌面运行通过。
- 未运行：launcher、真实中文键盘输入/展示/采纳/取消/重试、真实 provider、实际工单提交/回执/事件/重开、真实 M2 写点失败注入。当前 sandbox-exec true rc71（Operation not permitted），pgrep rc3（Cannot get process list）；强制写入隔离及回收清点不可验证，故未启动 launcher、未调用 --help、未产生本轮窗口。既有窗口残留 UNKNOWN，不能报告“桌面已清空”。
- 隔离：本轮测试数据、HOME、app-data、tmp/cache/config、签名和证据均在 `runtime/optimization/2026-10-09/M3/review-r1/`。没有访问真实业务数据库，没有改作者的 evidence 文件。审查方执行偏差：开头为遵循系统记忆查阅要求，曾只读项目外 `/Users/abeam/.codex/memories/MEMORY.md`；随后停止项目外检索。未写项目外文件，不把该记忆中的旧状态作为本轮事实证据；本轮读取范围并非全程符合额外约束。

证据根：`runtime/optimization/2026-10-09/M3/review-r1/`。下文 `results/…` 均相对此目录。复现脚本 `independent_probes.py`、`local_store.py` 仅是审查测试资产，不进入应用包。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与基线|核对两个文件 SHA；从 M2 保存副本+diff 重建基线|同一固定候选，可定位叠加|源 SHA 全匹配；基线重建匹配；没有 M2 PASS|候选定位 PASS；前置挂账|candidate-check、base-resolution、base-to-m3.diff|
|硬1 / 换描述|使用水泵间灯闪、茶水间插座故障、未知区域多风机三组新描述|真实模型因地点/症状变化，追问与歧义有依据|离线 NO_SERVICE 三组均保留输入、不创建任务；应用没有模型调用实现|真实模型 NOT_RUN；适配实现 FAIL|fresh-input-attempts、source-traces.requestAiSuggestion|
|硬2 / 确认与回读|追踪输入→确认→createDraftFromPanel→M2；令创建依赖返回 false|无确认无 OPEN；成功必须有一致权威回执/事件且重开可读|源码确认入口仍返回 true；UI无条件显示 OPEN；Python 测试只追加内存 stub|FAIL；原生读回 BLOCKED|exact-source-probes、源码1660/3142、契约563–612|
|硬3 / 迟到与交错|取消后回包；切项目/活动主体；任务7→8但回包7；输入A→B→A；AI已采纳后改原文|展示和采纳两层拒绝旧建议，确认再次检查|上述旧校验返回 true；单纯A→B、撤权、到期子项返回 false；回包直接写草稿，采纳按钮仅改提示|FAIL|exact-source-probes、post-apply-input-edit-confirm、ui-wiring|
|硬4 / 恶意与手工|虚构ID、跨项目/停用设备、虚构备选、空来源、非法状态/角色、恶意原文；输入后直接设为问题|拒绝越权/虚假事实；模型不写任务；无模型可合法手工继续|虚构主ID被拒；跨项目/停用设备/空来源/虚构备选被接受；额外status/actor未变成任务/身份，任务数0；手工按钮未读输入框|FAIL核心校验/输入；原生手工 BLOCKED|independent-contract-probes、ui-wiring|
|硬5 / 真桌面与审计|launcher隔离预检；合成短token串经过实际_safePreview控制流|真键盘取消重试可用；不记录秘密|rc71/rc3未启动；短token串被原样作为审计preview保留|桌面 BLOCKED；审计源码 FAIL|preflight、audit-preview-source-probe|
|本地 catalog 路线|隔离生成离线密钥/证书、stamp/sign、验证catalog、官方install_staged、重建Store/may_run、篡改与恢复|当前源摘要可安装，坏包拒绝，私钥删除|安装/重建/恢复均rc0；篡改rc1；installed三份源字节一致；私钥文件0|PASS（仅Store层）|local-store-validation|
|受影响回归|比较 M2 runCommandBound/commitBound/commit/confirmDraft/identityActive/recordReceipt/generateStableKey；核新创建接线|不绕过边界，不误继承旧失败|七函数与重建基线相同；新创建接线复制了未闭合M2创建路径|源码比对 PASS；核心确认 FAIL；运行回归 BLOCKED|affected-M2-regression、D-M3-05|

本轮离线签名只服务该隔离测试包 digest=`67d9e0bb2e179b2122ed8b796e9728664bb9159fecd6bdac1096c83a81327341`；这是测试副本 stamp 后摘要，不冒充原工作树 manifest 的旧摘要。没有联网、上传、publish、listing 操作。working.key、anchor.key 已在 finally 删除，`remaining_key_files=[]`；报告结束时再核验目录为空。本地路线可行，不需要 AppHub 公开发布授权。

### 既有验收逐项核对

状态指完整原用例；括号内给出已执行子范围。不能用源码存在、Python通过或历史后端PASS替代本轮原生PASS。

|用例|原用例目的与本轮实际|结论|
|---|---|---|
|G0-E|真实系统助手及关闭/拒绝/失败。应用仅no_op、没有模型调用，未配置provider|NOT_RUN真实调用；适配实现FAIL D-M3-01|
|T01|真实模型提取、保留原文、缺位置追问、未确认不OPEN。新输入仅离线NO_SERVICE；采纳来源不落任务|BLOCKED完整桌面；源码FAIL D-M3-01/02/06|
|T03|无空间/跨项目空间/缺联系人拒绝且保留草稿。缺字段guard存在；跨项目仅查全库存在性|FAIL源码/契约反例 D-M3-04；原生BLOCKED|
|T25|缺失/矛盾标未知，伪造状态不写任务，恶意原文不改角色。非法status/actor及恶意原文在离线反例中无任务/角色副作用；缺失/矛盾真实模型未跑|NOT_RUN完整；安全子项仅契约验证，来源校验FAIL|
|T26|模型失败明确且人工兜底；不以假模型代真。NO_SERVICE分支存在；纯手工“设为问题”读旧输入|FAIL源码 D-M3-02；真实兜底BLOCKED|
|T33|同义意图合法、不同症状地点不强归模板。没有真实模型；两个createDraft同名，旧函数仍含固定会议室文本|NOT_RUN；同名运行解析未知，不凭它单独判FAIL|
|T34|未知空间、多设备、无历史主动补充，不存在引用拒绝。主候选假ID拒绝；虚构备选及空来源通过，missing/ambiguous未保留到草稿|FAIL子范围 D-M3-04/06；真实追问NOT_RUN|
|T35|生成时改派/改约，旧角色/版本不可执行。源码只比回复与请求旧版本，不读当前版本；主体/项目不绑定|FAIL源码分支 D-M3-03|
|T36|假/真适配器工具白名单。禁止动词数组仅供参考，schema放过未知status/actor但未执行；真实工具调用未实现|NOT_RUN完整；不声称恶意字段已修改身份|
|T37|无回执失败、读回超时待核验、重试不重复、高版本不误判旧成功。创建失败stub仍确认true，UI直接宣称OPEN|FAIL源码 D-M3-05；真实回执/恢复BLOCKED|
|T38|模型/提示/数据/宿主版本可复跑且真值不泄漏。离线脚本和源有快照；真实模型/提示/数据版本链未建立，Python确认不是M2读回|NOT_RUN完整；证据范围见A-M3-01|
|U02|原话→可编辑草稿/补歧义/保留原文/人工兜底。TextInput没有编辑同步，歧义及来源未持久保留|FAIL源码 D-M3-02/06；原生BLOCKED|
|U07|重复点、丢响应、冲突、离线不乱输入/任务身份。创建每次新ID，确认不传播执行结果；实际连续点击未跑|FAIL源码 D-M3-05；原生BLOCKED|
|U08|空/长/失败/无权限/过期均有继续出口。过期/撤权分支局部拒绝；取消后回包可通过；过期AI草稿改字段仍保留11秒deadline|FAIL取消子项 D-M3-03；完整UI出口BLOCKED，手工到期恢复见建议|
|U11|真实宿主输入/滚动/面板稳定，无假进度反馈。未启动；源码“OPEN已确认”无权威结果依据|BLOCKED完整UI；假成功源码FAIL D-M3-05|

## 缺陷

### D-M3-01 / P1 / 必修：真实AI适配只有占位，没有请求和回调链

- 文件与行：`app/bundle/main.splash:128`、`:139`、`:1503`、`:1519`；`model_config.json:6`。
- 触发：输入任一新描述点击请求AI；即使假设enabled为true且adapter字符串改值，再追踪请求路径。
- 实际/预期：默认恒走NO_SERVICE；另一个分支只绑定版本并写REQUEST_ISSUED，没有调用craftModelRequest、宿主模型服务、超时/授权处理或注册deliverModelReturn回调；boot也不加载配置。预期通过已授权能力返回真实结构化草稿，失败可解释。
- 根因与影响：把离线协议当模型适配完成；模块核心AI路径不能跑通，152/152不能证明模型贡献。
- 证据：source-traces.requestAiSuggestion、fresh-input-attempts；作者报告§6/8也承认TODO。真实模型NOT_RUN。
- 具体改法：实现选定宿主版本实际可用的单模型适配、配置读取、请求/回调/取消/超时/授权错误；没有已授权provider就停在明确缺口，不自行改计费或密钥。
- 验证：隔离真实桌面运行三组本轮新描述及同义表达；至少一组追问、一组多设备确认；记录真实provider/model/宿主与结果。离线反例另列，不能顶替真模型。

### D-M3-02 / P1 / 必修：手工路径没有把实际输入框内容送入草稿

- 文件与行：`main.splash:1494`、`:3106`、`:3109`、`:3138`。
- 触发：全新面板，在TextInput输入“水泵间西侧灯闪烁”，不点击AI，直接点击“设为问题”并补空间/联系人后确认；或AI请求发出后只键盘修改文字。
- 实际/预期：TextInput没有on-change接线；只有请求AI和清空按钮调用editRawText。“设为问题”读取TASK_INPUT.raw_text而非zh_input.text，得到旧/空原文；键盘编辑也不增加输入版本，迟到回复无法看见编辑。预期真实键盘输入即成为当前原文，手工路径无需先请求AI。
- 根因与影响：两个输入状态不同步，阻断手工报修与失效判定。置信度：源码接线高；具体宿主键盘表现未知。
- 证据：ui-wiring.json、源码上述行；原生重现BLOCKED，不把静态分析写成截图观察。
- 具体改法：用宿主实际支持的编辑事件同步并递增版本；在设问题/确认等入口再次取当前TextInput，保留失败输入。并清理1655/1784同名createDraft，只留明确面板入口；当前同名解析结果NOT_RUN，不单独断言后者已覆盖前者。
- 验证：NO_SERVICE下输入→设问题→确认实际OPEN回读；键入B后A的迟到回包不得展示/采纳；无需点击AI也必须成功。

### D-M3-03 / P1 / 必修：取消与上下文版本未守住展示、采纳、确认三处

- 文件与行：`main.splash:83`、`:1091`、`:1257`、`:1292`、`:1455`、`:1494`、`:1536`、`:1616`、`:3128`。
- 触发：请求A→取消→A回包；请求后切项目/切到另一个活动主体；任务7→8，回包仍7；A→B→A；回包已采纳后改原文，再确认。
- 实际/预期：逐函数原控制流翻译中，前五项validate均true；已采纳后改原文，confirm仍true。validate不检查active/input_version、不绑定请求主体/项目/事实/证据版本；任务校验只与旧请求比较。deliver直接apply，采纳按钮仅写“已采纳”提示，不做第二次校验。预期所有上下文变化使旧建议不可展示覆盖、不可采纳/执行。
- 根因与影响：单处、不完整的旧快照校验；取消只是改标签，输入版本虽存却未使用，确认也不核AI原文hash。单纯A→B、撤权和过期反例被拒是有效子项，但不足以放行。
- 证据：exact-source-probes.json、post-apply-input-edit-confirm.json、ui-wiring.json。
- 具体改法：生成不可复用请求ID及完整上下文快照；回包只建立独立suggestion；展示前和用户采纳时对当前active/request/input/draft/task/actor/project/fact/evidence/expiry重验。取消/关面板使请求失效；关键编辑清旧确认；确认必须绑定当前内容和AI来源，不能仅检查expires。
- 验证：逐项跑上述交错及关面板后回包；检查旧文本不显示覆盖、草稿版本/任务/回执不变；采纳前与确认前分别改输入或事实版本，再测拒绝。

### D-M3-04 / P1 / 必修：候选只检查全库存在，跨项目/停用设备和虚构备选可被采纳

- 文件与行：`main.splash:1171`、`:1179`、`:1197`、`:1224`、`:1418`、`:1624`。
- 触发：项目A回包引用库内项目B空间/设备、停用A设备；主候选合法但asset_alternatives含不存在ID，sources={}；手工调用字段修改到同样值。
- 实际/预期：独立合成Python反例跨项目/停用/虚构备选/空来源均APPLIED，虚构主ID被拒；主源同样全库查找、不检查project/active/服务空间/备选/来源schema，确认也只查存在。预期当前授权项目中的有效事实及可核查来源；歧义不自动定案。
- 根因与影响：给模型的事实列表过滤了项目，但返回侧不实施同样约束；请求prompt不能承担授权。可能把错误项目/设备带入真实工单。没有宣称本轮已发生原生越权提交。
- 证据：independent-contract-probes.json、source-traces.parseModelReturn、源查找和确认函数。
- 具体改法：统一草稿字段守卫：当前可信project、space.project、asset.project/active/services关系、全部备选ID和来源引用、有限schema/类型、缺项/歧义明确确认；回包、手工编辑和确认都使用。未知status/actor字段拒绝或明确忽略，不允许写身份/状态。
- 验证：上述负例三入口全部拒绝且无任务/事件成功记录；合法候选通过；恶意原文仅保留为数据、不得更改身份或任务状态。

### D-M3-05 / P1 / 必修：确认不传播M2结果并误用已选任务版本，产生假成功与重复创建风险

- 文件与行：`main.splash:97`、`:1640`、`:1651`、`:1660`、`:1675`、`:1691`、`:1695`、`:1701`、`:3142`；`M3/r1/scripts/m3_contract.py:592`。
- 触发：已选已有任务时新建；无选中任务但createDraftFromPanel失败；create/confirm提交或读回失败；重复点击确认。
- 实际/预期：草稿没有task_version_at_apply字段且未赋值，确认却将currentTask最新版本与它比较，与正在新建的草稿无关。无选中任务的失败依赖探针中，create返回false，确认仍true；UI因此写“✓ 已确认；OPEN工单”。新创建先push任务、写成功事件/save，再忽略commitBound返回；confirmDraft也无结果返回；确认标记照样写。每次创建新task_id/action_key，没有一次意图的创建重放约束。预期仅权威final回执/读回一致才成功；失败保留草稿，未知待核验，重试不新建。
- 根因与影响：面板协议与M2执行结果断开，复制了M2未闭合创建路径；即使M2返回拒绝，上层仍报告成功。Python“manual_path”只是内存created_task_ids/disk_records追加，不调用M2、不读真实磁盘、无回执/事件/重启，不能作硬2证据。
- 证据：exact-source-probes两项确认反例、源码、契约563–612、M2 r2 D-M2-02/03/04/05；affected-M2-regression表明M2核心函数未变。本轮未扩修这些前序缺陷。
- 具体改法：新建使用草稿对象与稳定意图键，不受无关选中任务版本影响；create/confirm返回结构化执行状态及action_id/task_id，传播失败/unknown；只在权威回读确认OPEN及匹配回执/事件后显示成功和落确认绑定。不要在核验前写成功事件；若M2现有接口达不到此要求，明确依赖并先做最小阻断修复，不在M3复制绕行。
- 验证：空列表和已有选中任务都可新建；每个创建/确认/回执/事件/读回失败点注入；UI不假成功且保留内容；相同意图连点/丢响应/重启重试只有同一个任务/动作，查回执和权威盘。

### D-M3-06 / P1 / 必修：原文与字段来源没有进入可重开的权威工单

- 文件与行：`main.splash:1292`、`:1308`、`:1467`、`:1661`、`:1691`、`:1740`。
- 触发：模型把原文整理为摘要，用户改空间/问题并确认；关闭应用后重开同一工单；回包含歧义、缺项、希望时间。
- 实际/预期：AI仅存输入hash，未保存所对应原文；missing_fields/ambiguous_fields/asset_alternatives未进入PENDING_DRAFT；工单t不含原文、sources、ai_request_id、人改字段/来源或desired_window。create_draft事件只保存source总标签；关闭面板清来源，重开无法从权威任务恢复。预期工单能回读原话、AI/人工字段来源与已确认内容，歧义不会消失。
- 根因与影响：可编辑有来源只存在临时内存，保存时丢掉核心审计链。此项不要求新增复杂历史产品，只补本模块最小必需字段。
- 证据：source-traces.createDraftFromPanel、applyDraftFromAI、源码97–115/1467/1661；契约disk_records也没有原文与完整来源。
- 具体改法：在版本化任务/命令schema中保留最小原文及输入版本、请求来源/事实引用、逐字段人工编辑和时间意图；歧义/缺项在确认前可见且有明确解决状态，经M2同一提交落盘。保留旧数据兼容，不新增第二事实源。
- 验证：长中文原文与AI摘要不同；用户改字段；确认→权威回读→重启，原话、当前字段和来源相符，无秘密泄漏；未解决必要缺项不得OPEN。

### D-M3-07 / P1 / 必修：截断原文预览不等于脱敏，审计可保存用户输入的秘密

- 文件与行：`main.splash:1513`、`:1580`、`:1591`、`:1604`。
- 触发：用纯合成短串`token=TEST_SECRET_ONLY_9`输入并请求AI（不使用真实凭据）。
- 实际/预期：原_safePreview控制流翻译保留完整该串并追加省略号（按现有_textLenSafe无换行返回1048576的分支）；recordModelMeta白名单含raw_text_preview_safe，_persistAiLog写到ai_requests.jsonl。Python契约也保存同样preview。预期审计不记录秘密；字段名“safe”不能代替脱敏。
- 根因与影响：只限制字段名和长度，不限制字段值；短描述甚至完整入日志。违反本模块“不记录秘密”的硬约束。
- 证据：audit-preview-source-probe.json、independent-contract-probes.json的secret_preview、源码。没有采集或公开真实秘密。
- 具体改法：审计删除原文preview，仅保留长度/不可逆引用和provider/model/状态；业务原文按任务权限保留，不混入通用模型日志。不要靠少数token前缀正则声称全面脱敏。
- 验证：合成密钥/电话/授权头样本及普通短/长中文；在审计文件确认无原文/秘密值，正常长度/结果仍可查。

### 建议挂账（不因建议项判FAIL）

- **A-M3-01 / P2 / 建议**：`M3_IMPLEMENTATION_r1.md:177`附近验收映射与原T/U定义不一致，例如把T33当禁止写、T35当手工兜底、T38当重开；152/152来自独立Python实现且确认用stub。按本文原定义重写交接映射并标明源码/离线/真实桌面/真实模型层次；不重跑作者样例为独立验收。上述具体核心缺陷仍按D编号修复。
- **A-M3-02 / P2 / 建议**：AI草稿只有约11秒有效期，转人工编辑仍保留deadline；到期后允许明确“转手工重新确认”并保留输入。按钮即时禁用、排版/所有视口/字号/focus等既有挂账按影响范围后续补，不本轮发散做皮肤。
- **A-M3-03 / P2 / 建议**：候选记录应明确实际基线是未接受的M2修复快照，补齐全部bundle/配置/脚本哈希与真实provider/提示版本。当前两份主源匹配及重建diff已足以进行本轮源码定位；不能宣称M2已被接受。

## 判定

- 最终结论：**FAIL**，精确范围为正式`M3-r1-worktree`首审。已有上述核心/安全P1，不是因建议、文风或前序状态单独拒收。
- 必修：D-M3-01～07。优先D-M3-02/05让纯手工输入→一次确认→权威OPEN回读成立，再接D-M3-01真实AI及03/04/06校验和来源；D-M3-07移除审计原文preview。不要顺手修无关前序或下一模块。
- 阻塞与未测：真实桌面隔离执行/进程回收条件；真实provider授权配置；M2确认回执/恢复能力及可信业务主体来源。作者离线成功不能替代必需运行证据。
- 解阻条件：①提供可执行的项目内强制隔离、可清点回收launcher的环境，后台启动并在finally终止/核验无残留；②接通已有授权宿主模型，若无授权配置，由Abram裁定真实provider配置；③由Abram裁定可信业务身份来源（继承M2），构建方只解决实际阻断本模块确认/回读的M2缺陷；④提交冻结M3新候选与逐D编号关闭证据，再原生复审。隔离离线签名已经授权且本地安装路径已PASS，不请求公开发布。
- 受影响先前模块：七个M2核心函数源码与重建基线相同；新创建/UI路径有本轮P1，原生回归BLOCKED；M0/M1/M2原结论不改。
- 门禁/台账：仅更新`docs/optimization/2026-10-09-desktop/GATES.json`的M3 status/审查字段，并把作者预填review字段存入review_history。ACCEPTANCE.json保持历史来源，不把本轮原生未运行结果覆盖历史后端验证；本轮逐项结论写入M3 review_acceptance。
- 是否允许下一模块：**否**；不执行M4，不给下一模块入口。
- NEEDS_ABRAM=yes仅对应剩余的真实provider授权配置与可信业务身份来源。源码修复、执行环境和离线签名不需新增Abram授权；本轮没有请求或执行被禁止的provider更换/计费配置。

STATUS=FAIL
NEEDS_ABRAM=yes
