# M3 独立 Review r6

最终结论：**FAIL**。当前 M3-r5-worktree 已经由独立请求加载，两个原生客户区均为空白，各有 **5 条解析错误**。核心输入、AI/人工确认、权威回读没有运行成立。harness **CLEAN 仅证明隔离与回收**。D-M3-01/03/04/05/06 未完全闭合；只要求修阻断本模块核心的部分，不修业务、不开始下一模块。

- 审查者 / 日期：本会话唯一独立 Codex 审查者，2026-10-11（Asia/Shanghai），未委派代理。
- candidate_id / base：**M3-r5-worktree / M3-r4-worktree**。GATES candidate_id 与作者 `reports/M3_IMPLEMENTATION_r5.md` 一致；不按文件时间选候选。作者缺 r5 独立 CANDIDATE.json，报告 SHA 为占位符且字节数不准，本审查者补充冻结对象清单，不冒称作者已交付完整清单。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty。主源 **384383 字节**、SHA256 **3e30355262e2a06dcb0216e0847cdb6166e8420fbf6793bf2fbcf31fda4ae23f**。
- 快照：`runtime/optimization/2026-10-09/M3/native/review_r2_1309/`（下称 **S/**）的 start-snapshot.json / main.splash.snapshot / tracked.diff / previous-review-to-r5.diff / source-traces.json。阶段1→阶段2定稿前包源、GATES、ACCEPTANCE摘要一致；最终仅报告、新审查证据和 GATES 的 M3 审查字段变化，记录于 S/report-verification.json。
- 前置：M2 **FAIL**，candidate **M2-r5-worktree**，报告 **M2_REVIEW_r6.md**；不存在已接受的 M2 PASS 基线。遵循本次前序挂账及局部重审裁决，继续 M3 原缺陷复核；只核阻断本模块的加载/权限/确认/回读依赖，不改变 M2 结论。
- 模型路由：本会话 Astra；无法核验 Router 底层转发或切换成 gpt-6.1-sol，未声称已切换。无可调用的本会话 createdAt/标题设置接口，未以当前日期猜标题，未改变任何其他对话状态。
- 原生宿主：驱动在 agent 沙箱外执行本审查者请求；`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**。
- 配置：MiniMax / MiniMax-M3；本次两段独立 Review 真实请求 **0**。历史 r3 Python 3次调用保留原范围，不能充当当前原生模型验收；无402/欠费事实。
- 原生证据：`runtime/optimization/2026-10-09/M3/native-runs/review_r2_1309_REQUEST_review_r2_1309/`（下称 **H/**），窗口 **14:33:12–14:33:51 CST**。请求 `M3/native/REQUEST_review_r2_1309.json`，阶段笔记 `M3/native/REVIEW_NOTES_r2_1309.md`；独立核验 **S/native-evidence-audit.json**（下称 **A**）。
- 已读范围：阶段1 AGENTS/CONTEXT/00/01/02/M3/04、上一轮 r5报告、作者r5报告/证据及原缺陷涉及源码；阶段2全部 summary/result/profile/frames/logs/denials/MANIFEST与实际业务盘、固定宿主输入能力既有证据。不扩大到后续模块业务。
- 已运行范围：阶段1离线签名/certify/verify/install_staged/Store重建/may_run；驱动运行本次两个原生场景；独立摘要、seed/运行复制、profile/写入/回收、日志与盘核对。未自己启动launcher，未做 sandbox-exec/pgrep预检，未用 --help/osascript/辅助功能/自动化。
- 数据与秘密：仅新隔离目录及合成业务/账号数据，未伪造已认证SESSION，未改原始业务数据，未读/打印/改真密钥或明文业务凭据。两份本轮离线签名私钥已删除，S/offline-store-evidence.json记录exists_after=false，本轮再核keys空；未删他人文件。
- 过程偏差：阶段1依上级memory指令只读搜索过项目外MEMORY.md，及审查辅助脚本首跑根路径索引错误导致FileNotFound（未复制源、未生成私钥），均已在阶段笔记披露。阶段2访问/输出在项目内；无项目外写入。此为审查过程说明，不伪装为业务缺陷。
- 置信度：摘要/隔离/回收/解析失败/空白UI及确定源码分支 **高**；真实模型效果、动态交错、业务写入和恢复 **未知或未运行**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/证据一致|重算request、harness/template、MANIFEST、seed与镜像/安装/.running的目标主源|同候选、证据完整|321项SHA全部匹配，遗漏0；两场景各三份目标main与冻结源一致；宿主SHA一致|PASS（对象/证据范围）|A；H/MANIFEST.sha256；S快照|
|原生隔离与回收|核profile及探针、env、写入清单、前后进程及退出|仅写新run、黑名单不可读、无残留|两场景probes.ok=true，pre/post=NONE、pgid_members_after=[]，CLEAN、quit_http、host rc0；每场景123项列出文件均在run内|PASS（隔离/回收）|H/*/result.json、profile.sb、denials；A|
|本地catalog/install_staged|核本轮离线Store与实际加载目标|无需公开发布，同字节安装/加载|verify/install_staged/重建/may_run rc0；同源运行复制实际存在；digest_seen_in_host_log=false但实际字节独立验证一致|PASS安装/加载；FAIL应用运行|S/offline-store-evidence；A；H/logs|
|原生空盘/手工入口|1280×800、空盘、未登录；独立导航taps/capture|可见可操作表单/登录/错误出口|空白客户区；5条[E]；没有业务控件命中证据|FAIL / D01|H/cold_candidate_ui/frames；host.log:45–49|
|原生不可信既存草稿|980×760、合成DRAFT、恶意原文/伪来源、未认证；导航taps/capture|权限投影、来源不误当权威、可操作拒绝|同样空白，5条[E]；盘与seed相同，无业务解析/权限执行证明|FAIL界面；权限/来源运行NOT_RUN|H/untrusted_existing_draft/frames；host.log:44–48；A|
|硬1 三组新真实描述|另选滴水歧义、未知空间插座、无历史通风+恶意原文；追实际适配body|真实建议随症状/位置变、缺项追问、不编造|三组只选定，未键入/调用；HTTP/绑定缺口静态仍在|FAIL D01源码；模型NOT_RUN|阶段笔记三组描述；S/source-traces；manifest|
|硬2 AI确认与回读|追apply→confirmDraftModelBound→createDraftFromPanel→M2确认；核盘|确认前不OPEN，确认后精确回执/任务/事件一致可重开|无AI执行；只检查task_id/status，仍以内存OPEN包装结果|FAIL D05源码；AI写入/回读NOT_RUN|S/source-traces；main:4105–4224、4381–4399；A|
|硬2/4 手工路径|独立空盘启动；追字段→同确认边界；核实际盘|无模型仍可合法提交并权威回读|UI空白、无输入，仍共享D05；空盘未变不证明合法手工成功|FAIL界面/D05；手工写入/回读NOT_RUN|H/cold_candidate_ui；A|
|硬3 展示/采纳/确认失效|复核三种输入交错、任务/事实/证据/主体绑定|旧建议不展示/覆盖/执行，合法未改可采纳|编辑失效改善认可；回包不重读控件，完整当前绑定与确认检查仍缺|FAIL D03源码；动态NOT_RUN；控制通道BLOCKED|S/source-traces；阶段笔记；输入能力证据|
|硬4 恶意返回/字段来源/歧义|追假ID、越权、非法状态、来源和未选默认值分支|拒非法事实/来源；核心歧义先解决|事实guard保留；verified只是候选存在，确认不消费来源快照、不拒剩余核心歧义|FAIL D04/D06源码；实际恶意返回NOT_RUN|S/source-traces；main:3164–3177、3359–3411、4050–4126|
|硬5 桌面编辑/取消/重试/审计|查看真实帧/日志及审计白名单|输入可用、失败可继续、模型审计不含秘密|当前应用空白；未到输入/取消/重试/模型审计路径；D07源码闭合保留|FAIL原生UI；动态NOT_RUN|两场景帧/logs；S/source-traces.recordModelMeta|
|M2受影响回归|同候选加载及精确确认依赖复核|可信主体与可靠最终提交作为M3基础|当前解析仍阻断整体UI；M2 final/readback依赖仍缺|FAIL直接依赖；不改M2结论|本轮H；M2_REVIEW_r6；main:4381–4399|

### 证据核验边界

1. 两个最终PNG均逐张目视，为空白客户区；尺寸 **2800×1718**，两张SHA256都为 **376a7e2296bf4a6ff40cad2df13748e512baff188f007c94b51b9550d2b2c0b4**。对应.part.png与最终PNG相同，核字节后不重复作为额外交互。不能据相同画面证明两个请求尺寸的响应式UI通过。
2. 两场景实际加载 **384383字节**源，各5条解析错误，日志内部坐标5187对照冻结源码 **5184**。`eval`及`launched`只说明加载尝试，不证明脚本执行成功。旧`ok`保留名错误未再出现，认可对应修复子项；不将当前5条错误冒称旧50条仍未修。
3. 两场景seed清单逐项回核，运行副本的目标export/install/.running三处main均一致；系统应用的main不混入业务源相等断言。profile SHA及template SHA均匹配，env的HOME/app-data/cache/tmp/config/data路径在各run内。每份123项列出文件存在且路径不越界；家目录mtime前后相同、Library扫描新增0。
4. 拒绝日志完整读取并重算summary，与result相符：443外联、Metal外部缓存写及第二场景/dev/dtracehelper写被拒。duplicate-report行不等于实际尝试次数；appleeventsd的拒读是系统日志条目，不是本审查使用自动化。未把拒绝行为写成成功外联/越界写。原profile含本地Unix socket许可，如实保留，未声称仅有TCP许可。
5. 实际业务jail为各场景 `home/.octosense/apps/octosense-repair/`。tasks/actions/events/state/隔离accounts与seed逐字节相同。空盘仍空；另一盘仅原synthetic DRAFT，空间`sp-A-101`本就不是当前白名单事实。这不是实际生成的合法AI建议，不证明来源、歧义或权限守卫已执行。
6. needs_model=false，result中model_proxy/model_proxy_stats缺席、MM_KEY/代理endpoint未注入；实际模型请求0、无billing_error。宿主被拒443外联不能据此归因于MiniMax调用。配置中的MiniMax、host日志“1 capability/1 host”均不证明http.fetch已经工作。
7. 作者本次构建证据三场景仍加载旧主源`8b7d84…`，每份50条[E]；其481项MANIFEST完整，但不能代验当前r5。见S/author-native-audit.json。本轮独立请求已纠正Store对象，无需公开发布。

### 相关既有用例逐项复核

|用例|本轮结论与精确范围|
|---|---|
|G0-E|FAIL D01原生UI/接线缺口；当前原生真实MiniMax、关闭/拒绝/失败路径NOT_RUN，0请求。|
|T01|FAIL D01/D03/D06；三组新描述已独立选定但未键入，实际提取/追问/确认前不OPEN业务NOT_RUN。|
|T03|NOT_RUN实际无空间/越权/缺联系人拒绝及合法对照；最终事实guard源码改善保留。|
|T25|NOT_RUN实际缺失/矛盾/恶意provider及主体/状态行为；恶意原文仅留在synthetic seed，不能写拒绝已测。|
|T26|FAIL原生手工界面不可用及D05共享缺口；实际模型失败→手工合法成功/回读NOT_RUN。|
|T33|NOT_RUN真实同义/不同地点症状效果，不继承Python3次为native效果。|
|T34|FAIL D04不可核来源、D06未解核心定位；实际未知空间/无历史追问及可核来源正例NOT_RUN。|
|T35|FAIL D03源码；动态迟到/编辑/撤权/切项目/任务事实变更NOT_RUN，控制通道BLOCKED。|
|T36|NOT_RUN真实/假适配器白名单执行，storage-only manifest与HTTP API/许可未实证，不假定octos实现。|
|T37|FAIL D05精确最终回执/回读源码；实际丢响应/读回失败/原键恢复/高版本恢复NOT_RUN，精确控制及连续同盘重开通道BLOCKED。|
|T38|候选/宿主/配置/数据/运行字节已核；同候选真实成功与失败全链NOT_RUN。|
|U02|FAIL原生空白、D03/D06；原话→补歧义→编辑→确认→回读NOT_RUN。|
|U07|FAIL无可用表单/恢复出口及D05；重复点击/响应丢失/冲突/任务身份稳定实际业务NOT_RUN。|
|U08|FAIL空白应用无可见可操作失败/无权限/过期出口；状态恢复未运行。|
|U11|FAIL真实客户区空白；应用内输入/滚动/面板切换未运行，shell截图/正常退出不能代签。|

## 缺陷

仅复核上一轮编号及直接受影响回归。以下P1均阻断当前核心，不以视觉建议判FAIL。

### D-M3-01 — P1 / 必修 / 部分改善，仍未闭合

- **文件与行**：`app/bundle/main.splash:5184`（整体解析阻断）、`:244–340、3838–3927`（模型调用/绑定），`manifest.json:2–4`。
- **触发**：本轮两独立场景按当前签名catalog launch-hub→导航taps→capture。无需登录或模型即可复现。
- **实际 / 预期**：两窗口均空白，每份5条Expected ) / Expected }；对照源码表达式 `return ((h ^ (b & 0xFF)) * 16777619) & 0xFFFFFFFF` 在固定宿主解析失败。预期整体应用可加载并出现真实可操作表单。没有将单个运算符的原因未经验证写死；错误位置与表达式对应，需在同宿主验证支持语法。
- **改善保留**：旧ok保留名/三元错误未再出现；代理endpoint覆盖、spaces/assets注入已新增。
- **仍缺**：host.http_fetch/最小HTTP许可未原生证明，manifest仍仅storage；实际model request没有发送request_id/expires/draft/task绑定值，提示“回声”不提供这些值。真实三描述0请求。
- **根因 / 影响**：全文件只做字符串检查未过固定宿主解析；后续M5函数虽非本模块业务范围，但在同main中解析失败，直接阻断M3全部UI。仅修该语法加载依赖，不展开M5业务。
- **证据**：H/cold_candidate_ui/logs/host.log:45–49；H/untrusted_existing_draft/logs/host.log:44–48；两帧；A；S/source-traces。
- **具体改法**：以固定宿主支持的表达式/位运算方式重写这一最小函数，保持原fingerprint语义；经harness证明整个main可加载。随后只补授权事实/绑定和实际HTTP适配/最小许可，继续走本机代理，不放开公网直连、不将真密钥给宿主。
- **验证**：新同字节Store零parser错误且表单可操作；再现场输入阶段笔记三组新描述真实请求≤剩余预算7，核返回/来源/追问及错误出口。旧Python证据不替代。

### D-M3-02 — 部分闭合保留；余项归D03/D05，不新增重复P1

- **文件行**：main:3785–3836、7373–7428。相同文本no-op/按按钮同步改善保留。
- **实际 / 证据**：当前UI空白，真实中文键入、清空、取消、重试尚未执行；H帧/logs、S/source-traces。
- **验证**：加载成功且输入通道可用后，真实编辑/取消/重试与同文no-op，再分别核AI/手工权威确认。不会因本轮NOT_RUN回退已成立源码子项。

### D-M3-03 — P1 / 必修 / 部分改善，当前绑定仍不完整

- **文件行**：main:2244–2254、3282–3340、3419–3421、3785–3823、3899–3916、4050–4126。
- **触发**：A请求等待期间仅键入B；APPLIED(A)后改输入/主体/项目；合法未改正例。
- **实际 / 预期**：editRawText清引用/APPLIED→STALE_INPUT改善认可，但回包只查TASK_INPUT不重读控件；task_version比请求快照，不比当前任务；事实/证据版本仍缺。采纳gate只查有session，未核原主体/项目/当前权限；apply设置invalidated_by_edit=true，gate直接拒该标记，合法采纳也需验证。确认仍凭版本超过M4快照放行，未核AI历史绑定。预期展示、采纳、首次确认三处分别核当前完整上下文，合法未改正例可继续。
- **根因 / 影响**：逻辑快照与输入控件不一致，自动apply与显式采纳混用，可能展示/确认旧内容或拒合法采纳。**本轮未运行动态交错，不声称已落库。**
- **证据**：S/source-traces / previous-review-to-r5.diff；本轮H无法运行表单。
- **具体改法**：共用当前输入/请求/草稿/任务/主体/项目/事实/证据/到期守卫；回包读实际控件，区分待采纳建议与草稿，显式转人工重新确认。
- **验证**：三输入交错及切项目/撤权/任务事实变化；截图、草稿、动作与事件分别核，不以一个STALE标签代替展示与执行两层证明。

### D-M3-04 — P1 / 必修 / 事实子项保留，来源仍不可核

- **文件行**：main:3164–3177、3359–3411、3631–3654、4060–4067、4275–4276。
- **触发**：合法设备ID配不存在的巡检/维修日志来源，合法引用正例对照。
- **实际 / 预期**：sources仍只查对象/非空；候选存在/同项目被标verified，任意模型来源文字保留raw；确认不消费新增来源快照、更无证据ID/版本/原文范围验证。来源UI仍按字符串拼接新对象，需定向渲染回归。预期来源可定位、权限有效，unknown与已核事实区分。
- **根因 / 影响**：候选存在不证明模型声称的来源，阻断“有来源”核心目标。假ID/跨项目/停用/服务关系最终guard改善保留。预装synthetic伪来源不是动态接受反例。
- **证据**：S/source-traces.parseModelReturn/applyDraftFromAI/_validateDraftFacts；H次场景盘未变、UI空白。
- **具体改法**：结构化白名单事实/证据ID、版本、原文范围；校验存在/权限/关联，陈旧/不存在/越权来源拒绝或标未知；UI显式读来源结构。
- **验证**：合法/伪来源、假设备、存在但无权项目、非法状态、恶意原文及采纳后撤权；核UI/草稿/主体/事件。当前facts仅prj-A，不捏造已测真实B事实。

### D-M3-05 — P1 / 必修 / AI与手工仍无权威最终成功协议

- **文件行**：main:4105–4126、4139–4224、4381–4399。createDraftFromPanel/confirmDraft与上一轮相同。
- **触发**：确认先变内存OPEN后提交失败/待核、事件失败、丢响应重试；AI和手工分别做。
- **实际 / 预期**：确认入口只验task_id/status，不验commit_ok/confirmed_open/精确final；create返回创建action_id，confirmDraft不返回最终确认结果，按内存OPEN包装成功。每次newId创建新意图，未证明原键恢复。预期精确最终确认回执、任务、关联事件权威读回成立才成功，未知保留草稿/原意图。
- **根因 / 影响**：内存状态被当作提交证明，AI/手工共同受影响。作者字符串找到“三字段”不证明消费检查。**本轮业务未运行，没有新增实际部分提交反例。**
- **证据**：S/source-traces.confirmDraftModelBound/createDraftFromPanel/confirmDraft；M2_REVIEW_r6；A盘与seed一致。
- **具体改法**：持久不可变确认意图；返回实际final/unknown/rejected及精确确认action；消费端核回执/关联事实后成功，原键对账不newId重建；只修最小M2依赖。
- **验证**：AI/手工各成功+读回失败+丢响应+重复确认+关联事件失败+同盘重开，核一个task/匹配final/唯一事件，不用内存flags替代权威查询。

### D-M3-06 — P1 / 必修 / human_edited改善，确认仍不阻断未解核心歧义

- **文件行**：main:3429–3531、4050–4126、4175–4176。
- **触发**：建议含合法默认设备及多候选，用户未选直接确认；显式选择正例。
- **实际 / 预期**：helpers已要求human_edited，认可默认值不直接记人工已解；确认不核剩余missing/ambiguous，创建只持久化resolved数组不作拒绝条件。预期核心定位歧义未解不执行、补充后合法可继续。
- **根因 / 影响**：台账与执行守卫脱节，报修对象未可靠确认；无当前原生执行反例。
- **证据**：S/source-traces helpers/confirmDraftModelBound/createDraftFromPanel；上一轮D06；本轮H。
- **具体改法**：按对应字段维护人工解决痕迹，确认前计算并拒未解核心定位，给补充出口。沿用合法空间下设备可未知的手工规则，**不要扩大为空asset一律拒绝**。当前helper仍可能将“空间定位/设备定位”因problem人工非空标resolved，应改为对应字段解决。
- **验证**：默认未选拒、有效选择可继续、撤销再失效、未知空间追问、合法人工无设备正例与合法时间编辑；读回原文/resolved一致。

### D-M3-07 — 源码范围闭合保留，实际模型审计NOT_RUN

- recordModelMeta未变，白名单不含raw_text/preview/key；本轮未执行真实provider日志路径，不扩大闭合范围，不重复修已闭合根因。

## 判定

- **最终结论：FAIL**。
- 精确范围：M3-r5-worktree原缺陷与直接受影响回归。当前字节安装/加载、证据完整性及原生隔离回收PASS；当前应用UI解析/渲染FAIL；真实模型、输入、AI/人工提交和权威回读NOT_RUN。
- **必修：D-M3-01、D-M3-03、D-M3-04、D-M3-05、D-M3-06**。D02/D07已改善部分保留。无锦上添花建议导致FAIL。
- **BLOCKED仅用于白名单能力缺口**：固定宿主既有M2_REVIEW_r5:52及对应日志拒`type:`，没有已验证的中文/登录输入替代；request.schema没有受控延迟/恶意回包、逐写点/读回故障/丢响应和连续同盘重开入口。这些技术通道需构建/驱动提供合规且可复现的支持，不能预造SESSION或修改业务来代测。无ABORT；解析失败记FAIL，不以sandbox rc71/pgrep rc3为理由。
- 未执行的新输入/恶意返回/交错/恢复，均明确NOT_RUN；本轮启动可用性不受输入通道缺口免责。
- M2直接依赖未通过，报告保留M2 FAIL，不修改其门禁，不开展后续模块。
- 门禁：更新 `docs/optimization/2026-10-09-desktop/GATES.json` **仅M3 status/审查字段**，review_report指本报告；旧审查字段追加入review_history。构建方原字段（含旧rc71/BLOCKED/REAL_OK声称）保留为历史来源，不能覆盖本轮review_summary。原ACCEPTANCE.json不改；相关T/U/G0逐项结论在本报告及M3 review_acceptance保存，不改写历史后端验收为原生验收。
- **不允许执行下一模块**。本模块修复顺序：当前整体main最小语法修复→支持输入通道/真实MiniMax代理事实与绑定→展示/采纳/确认当前守卫→可核来源与核心歧义→AI/人工精确最终回执/回读恢复。严格按原编号复验，不扩审。
- NEEDS_ABRAM=no：身份/provider/隔离离线签名均已授权；本地路径可行，无公开发布需求，0真实模型调用、无余额/欠费错误。剩余为技术/证据缺口。

STATUS=FAIL
NEEDS_ABRAM=no
