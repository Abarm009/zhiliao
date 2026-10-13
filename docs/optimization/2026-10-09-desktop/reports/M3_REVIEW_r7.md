# M3 独立 Review r7

**最终结论：FAIL。** 受审候选 **M3-r6-worktree** 在独立 harness 的 **3/3 场景均未生成业务根视图**。登录、真实输入、报修草稿和失败恢复界面空白；完整日志有控件作用域错误、`script time budget exceeded` 和业务 `view=false`。隔离、回收与候选一致性 PASS，不能代替业务验收。D-M3-01/03/04/05/06 未完全闭合；不允许进入下一模块。

## 受审对象与实际范围

- 审查者 / 日期：本会话唯一 Codex 审查方，2026-10-11，Asia/Shanghai；未委派。无法用现有接口核验实际主会话 Router 路由、指定模型切换或 thread createdAt/标题设置，未声称这些动作完成。
- candidate_id / base：**M3-r6-worktree / M3-r5-worktree**。按用户指定的构建证据、GATES 交接字段、`M3_IMPLEMENTATION_r6.md` 和 `M3/r6/CANDIDATE.json` 定位，不按 mtime 选版。HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty；保留全部他人修改。
- 主源：462803 字节，SHA256 `abfc939139310463be3b04357cb73287a1455653228d8b50efca3e4f54f6ee9e`。作者冻结的四项对象均匹配；阶段1→阶段2定稿前 **11个保护文件、75项独立 seed/mirror 和 request 摘要一致**。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r6.md`。只复核上一轮 r6 的 D01–D07 及直接受影响回归，没有无关扩审。
- 前置：M2 **FAIL / M2-r7-worktree / M2_REVIEW_r8.md**；没有已接受的 M2 PASS 基线。按用户前序挂账裁决继续本模块局部审查，不伪造前置通过，不更改 M2 结论。
- 固定宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，实际三场 SHA256 均为 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 运行包 digest：`48a42cf03d8cff69a7dd9dee17ad5be31ef30c1b3c4e374f8d3792048a8d5ec9`。signed manifest 与原 manifest 的差异是 stamp/sign 摘要、签名及 canonical null 默认字段，能力/网络及其他业务语义一致，不误报为候选错配。每场镜像、`.bundles`、`.running` 三份业务 main/config/identities 与冻结对象相同，signed manifest 与冻结签名包相同。
- 模型：MiniMax / MiniMax-M3 / anthropic messages；本轮原生模型请求 **0**。三场 needs_model=false，没有代理或密钥占位符注入。历史作者 r3 Python 3次调用仅保留原范围，不算当前原生模型通过；未发生本轮402/欠费错误。
- 独立请求：`runtime/optimization/2026-10-09/M3/native/REQUEST_review_r1_2104.json`。驱动沙箱外实际执行窗口 **23:37:20–23:38:19 +08:00**。本审查方没有自行启动宿主、sandbox-exec/pgrep预检、--help、osascript、辅助功能或自动化。
- **H/**：`runtime/optimization/2026-10-09/M3/native-runs/review_r1_2104_REQUEST_review_r1_2104/`；**E/**：`runtime/optimization/2026-10-09/M3/native/review_r1_2104/`；**A**：E/native-evidence-audit.json，复核脚本 E/audit_phase2.py。阶段笔记保留于 `M3/native/REVIEW_NOTES_r1_2104.md`。
- 已读：阶段1 AGENTS/CONTEXT/00/01/02/M3/04、r6 Review/实施/清单/相关源码及差异、M2直接依赖；阶段2全部 summary/result/profile/denials/logs/MANIFEST、全部现存 PNG 内容、实际业务盘及相关源码分支。
- 已运行：阶段1独立离线 catalog verify、install_staged/重建/may_run；驱动运行本审查请求三场；本审查独立计算摘要、seed/运行盘/元数据/日志/源码核验。源码审查不等于 Splash 动态执行。
- 数据边界：仅隔离合成账号、业务盘与现有签名副本；没有预装 SESSION。未读取真实明文凭据、provider密钥或项目外memory，未修改原业务数据。没有生成新签名私钥；作者两把私钥已核不存在，删除历史证据在 build_r6/offline-store-evidence.json。
- 过程说明：阶段2辅助脚本首跑根目录索引错误，尝试打开不存在的父目录请求路径而报 FileNotFound，未读到文件或写项目外内容；改为正确项目根后核验成功。阶段1缺 jsonschema 依赖，已用 schema 关键字检查及仅抽取 harness 纯校验函数替代，未安装依赖。均不是产品缺陷或环境 BLOCKED 理由。
- 置信度：候选一致、隔离回收、空白UI/运行错误、盘对比及确定源码分支 **高**；真实模型效果、完整交错、提交故障/重开结果 **未知或未运行**；宿主作用域错误的最小技术根因需同宿主验证，**中**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/证据一致|核 request/summary、481项MANIFEST、75项seed、11保护文件及实际三份包|同候选且证据完整|全部摘要匹配；无遗漏；运行main/config/签名manifest一致|PASS，证据范围|A；E/snapshot-start、candidate-audit、seed-manifest；H/MANIFEST|
|内核隔离与回收|核三份profile、probes/env/files/denials/pgid/exit|受限写、禁读、无残留|三场probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN、host rc0、quit_http|PASS，隔离范围|H/*/result、profile.sb、sandbox-denials；A|
|本地catalog/install_staged|独立验签/安装/重建，核实际加载字节|不公开发布即可安装加载|verify/probe rc0；net/storage准入成立；运行复制相同|PASS安装/加载；业务运行FAIL|E/install-staged-audit、candidate-audit；A|
|原生空盘登录/输入|独立新描述A、空任务、保存未提交输入；launch/capture/type/capture|可见可操作真实业务根，保留未提交输入|51作用域错误+预算超限，view=false、空白；持久pending_input被清空|FAIL，D01；键入通道BLOCKED|H/cold_new_input_channel/logs:39–42、66–118；frames；A|
|原生越权/伪来源草稿|合成B项目DRAFT+A设备+恶意原文+saved actor，未认证；独立taps/capture|授权投影、拒绝出口，无自动提交|51作用域错误，空白；actor清为null；task/action/event未变|FAIL界面；动态来源/权限NOT_RUN|H/cross_project_forged_draft；A|
|坏事件失败恢复|合法行→坏行→合法行事件盘，空任务；独立taps/capture并查盘|保留历史、可见恢复/拒写，不假成功|原事件字节保留，无bad_lines/恢复输出；52作用域错误、空白无出口|FAIL界面/恢复出口；提交故障NOT_RUN|H/events_failure_recovery；A|
|硬1 三组新输入/真实模型|独立选A歧义/B未知位置/C无历史恶意原文，核实际适配路径|建议随症状位置变、不编造、缺项追问|A type不支持，三组原生模型0请求；业务界面不可用|FAIL核心可用性；真实效果NOT_RUN|阶段笔记三组新描述；H/cold日志；E/source-traces|
|硬2 AI确认与权威回读|追AI采纳→确认→M2，核task/receipt/event实际盘|确认前不OPEN，确认后精确final及事件读回、可重开|D05源码残留；无AI执行、新任务或确认回执|FAIL D05；AI全链NOT_RUN|main:5119–5166、5536–5601；A|
|硬2/4 手工确认与回读|独立空盘入口，追同M2路径，查盘|无模型可合法手工提交并权威回读|没有可操作表单，同D05；空盘未变不能证明合法成功|FAIL界面/D05；手工提交NOT_RUN|H/cold；A；E/source-traces|
|硬3 展示/采纳两层失效|核回包及采纳/确认的当前绑定；独立输入能力探针|迟到/编辑/撤权/任务事实证据变化失效，合法正例成立|回包改善；采纳未核task/facts/evidence；动态交错未执行|FAIL D03源码；完整交错通道BLOCKED|main:2746–2771、4102–4255；H/cold:41|
|硬4 非法返回/来源/歧义|追假设备/项目/status、quote校验、人工解歧义分支|不写身份/状态，来源可核，未解定位不确认|事实子守卫保留；伪quote可verified，设备选择可误消空间歧义|FAIL D04/D06源码；实际注入NOT_RUN|main:3842–3893、4312–4349；E/source-traces|
|硬5 桌面编辑/取消/重试/审计|查看实际帧/全日志/控制能力|可编辑、失败可继续、元数据无秘密|3场根视图空白；type unknown；取消重试/真实模型审计未执行|FAIL桌面；键入通道BLOCKED|H/frames、logs；A；D02/D07改善保留|
|M2直接受影响回归|同候选登录/任务加载、确认/事件/readback消费|可信主体和可靠确认作为M3基础|独立根UI再次失败，D05依赖未闭合；不改M2结论|FAIL直接依赖；业务动态NOT_RUN|M2_REVIEW_r8；本轮H/A；main确认分支|

### 独立原生证据核验

H/summary 请求与本审查 request 完全相同，harness/template摘要匹配；481项MANIFEST全匹配、遗漏0。三场summary与result一致，18.28/18.27/18.19秒退出，host_returncode均0，无ABORT/异常/残余进程。每场124项 files_written_in_run_dir全部存在、唯一且在run内，目录/环境路径和profile一致；这项是mtime清单，**不是124次业务写入**。Library scan无新增，真实home的记录mtime前后一致；未自行访问真实home复验。

profile明确限制写到场景目录（另有/dev/null例外），禁读五处受保护位置；记录的全部内核探针成功。网络仅本机控制口及profile已有Unix socket许可，没有模型代理。完整denials重新计算与result summary一致：443外联、外部Metal缓存写及部分/dev/dtracehelper写被拒，不能说成成功外联/越界写；duplicate reports不等于实际调用次数。appleeventsd拒读是系统日志，不代表本审查调用自动化。

captures逐项核 exists/sha256：三份initial请求截图均未生成，如实保留缺图；三张最终PNG实际存在并逐张目视，均为空白业务客户区。另三张.part.png分别与最终PNG字节相同，全部六个文件摘要核过；实际尺寸均2800×1716全屏，不能据此认定业务1280×800/980×760布局通过。前两张最终SHA为 `d44d11cda69ecd409e021390ef529dbb778a7479eaac5adcf0dad2df11c2ca82`，第三张为 `9f30f97d79a51453e7e74ee8b845e5747389145b3eef6acc06cfde60bca213fb`。缺initial截图不作唯一FAIL理由，三张最终图+view=false+全日志已独立证明核心失败。

host_log_bytes、listening/quit/launched/eval/panic各marker全部全文重新计算一致，无panic、每场[E]=0，但运行错误仍在：

|场景|作用域错误数|关键独立日志与结果|
|---|---|---|
|cold_new_input_channel|51|host.log:66起header_project/header_actor/login控件不在作用域；99行zh_input缺失；117预算超限（VM9221，源码9218）；118业务eval view=false；41 type unknown。|
|cross_project_forged_draft|51|同66起/99控件缺失；117预算超限；118业务view=false，跨项目DRAFT仍原样，无可信会话或模型校验执行证明。|
|events_failure_recovery|52|66起作用域错误；99缺输入控件；118预算超限（VM9248，源码9245）；119业务view=false；坏事件盘仍原样，无恢复出口。|

三场 `wait:4` 和 `wait:2` 均unknown；实际18秒存活由harness时间上限完成，**不能按wait序列声称精准交错发生**。cold的type也unknown；其他taps没有实际业务控件命中证据。809字节view=true是另一宿主脚本，不混作462803字节业务成功。

业务目录为 `home/.octosense/apps/octosense-repair/`。task/actions/events/隔离accounts与seed字节完全相同，无新增业务文件。唯一业务文件变化state.json：三场pending_input从已保存的新描述A/C变为空，panel从draft变none；越权场saved actor清空和selected_task_id清空。前者说明未提交输入恢复失败；**不是type已成功键入后丢失**。actor=null只证明不沿用saved actor，不证明完整可信授权链通过。坏事件原源保留，但没有bad_lines/业务恢复运行或可见出口；空盘仍空/没有OPEN只说明没有执行，不能判“确认前无OPEN的成功链”通过。

needs_model=false，model_proxy_stats缺席、无代理endpoint/MM_KEY注入；本轮0请求、无billing_error。被拒443无法直接归因于MiniMax。config、net准入或离线verify不证明http.fetch可用。完整审计细节见A。

### 相关既有用例逐项复核

|用例|本轮判定与精确范围|
|---|---|
|G0-E|**FAIL** 当前原生核心不可用/D01；配置与net准入改善保留；真实MiniMax与授权/服务失败动态NOT_RUN，0请求。|
|T01|**FAIL** D01/D06；三组独立新描述及同义句选定，A输入探针unknown；真实提取/追问/确认前业务NOT_RUN。|
|T03|**NOT_RUN** 实际缺空间/越权/缺联系人拒绝及合法对照；源码事实guard改善保留，跨项目seed原样不能代替实际拒绝。|
|T25|**FAIL** D04伪来源verified源码；缺失/矛盾工具数据、非法状态和恶意模型返回动态NOT_RUN；合成原文不能证明已拒注入。|
|T26|**FAIL** 人工兜底界面不可用及D05；真实模型失败→手工合法确认回读NOT_RUN。|
|T33|**NOT_RUN** 三新描述/同义/不同地点症状真实效果；不继承历史Python成功。|
|T34|**FAIL** D04可核来源/D06核心定位；未知空间/多候选/无历史实际追问、解决和确认NOT_RUN。|
|T35|**FAIL** D03采纳层源码；回包层改善保留；完整动态交错NOT_RUN、控制通道BLOCKED。|
|T36|**NOT_RUN** 真/假原生适配器白名单实际执行；net may_run准入PASS，HTTP可用性未实证，不假定octos实现。|
|T37|**FAIL** D05精确final/磁盘事件/重放；响应丢失、读回失败、原键恢复、较新版本动态NOT_RUN；精确注入/同盘重开通道BLOCKED。|
|T38|**NOT_RUN** 完整模型成功/失败复跑；候选/host/config/seed/运行字节及当前失败复现子项PASS。|
|U02|**FAIL** 空白业务界面、持久未提交原文被清空，D03/D06；键入通道BLOCKED，编辑→确认全链NOT_RUN。|
|U07|**FAIL** 输入恢复失败、没有可用操作/恢复出口及D05；实际重复点击/丢响应/版本冲突身份稳定NOT_RUN。|
|U08|**FAIL** 三场空白，没有可操作空态/坏历史/无权限/过期出口；业务状态恢复NOT_RUN。|
|U11|**FAIL** 原生业务根未渲染；输入/滚动/面板稳定NOT_RUN；正常退出及shell截图不能代验。|

## 缺陷

只保留阻断核心的原编号P1，其他已改善/建议挂账；下列D03–D06是确定源码分支审查，**未声称原生已执行越权、错误创建或假成功**。

### D-M3-01 — P1 / 必修 / 原生根视图仍失败，真实模型闭环未成立

- **文件与行**：`app/bundle/main.splash:8634–8638、8691–8695`控件声明，`:8850–8880`根引用，`:9218、9245`预算中止位置；`:252–258` HTTP接口；manifest网络许可已改善。
- **触发**：独立同包launch-hub，空盘/越权草稿/坏事件各冷启动，capture；无需登录或模型即可复现。
- **实际 / 预期**：3场51/51/52作用域错误、预算超限、业务view=false、空白；预期登录/任务/输入表单真实可操作、错误有出口。旧parser[E]清零改善认可，**不再称旧解析错误仍存在**。
- **根因 / 影响**：命名widget声明与root引用在固定宿主运行时不在同一可用作用域，根创建失败/启动预算超限；具体语法替代与预算消耗根因需同宿主最小验证。阻断M3全部用户路径和实际模型调用。
- **证据**：H/cold/logs:66–118、cross/logs:66–118、events/logs:66–119；三张最终frames；A。11保护文件与实际运行包一致，不能归咎审错版本或agent沙箱预检。
- **具体改法**：Kimi先修这一最小共有加载依赖，使用固定宿主实际支持的widget绑定/引用与根返回方式，检查运行时scope/预算/view和截图，不能只检查[E]。保留已经补好的net许可、绑定值与代理覆盖；根可用后实证HTTP API和三组新描述，不直连公网、不读真密钥到宿主。
- **验证方式**：同字节签名Store冷启动零作用域/预算错误，业务根/登录/输入实际渲染；真实合法登录后，新三描述经needs_model本机代理≤全模块剩余预算，分别核草稿来源/缺项/确认与权威回读。无模型可操作路径也须真实成功。

### D-M3-02 — 部分闭合保留；界面与未提交输入恢复回归未通过

- **文件行 / 证据**：main:4653–4662、4764起输入同步改善保留；main:493与启动9795–9805、H三场state前后及A。未提交pending_input实际被清空，zh_input运行缺失；没有真实键入/取消/重试。
- **改法 / 验证**：加载修复时把持久待编辑原文/草稿恢复到真实控件；未知type仅视作通道缺口，不能以“准备就绪”证明输入恢复。复验持久输入冷启动、同文no-op、编辑/取消/重试；不重复新增P1，归D01核心入口/恢复依赖处理。

### D-M3-03 — P1 / 必修 / 采纳层没有当前任务、事实、证据校验

- **文件行**：main:2746–2771 `_suggestionAcceptGate`，`:3802–3835`事实/证据版本，`:4102–4255`回包与快照，`:9030–9042`采纳按钮。
- **触发**：A回包已APPLIED→task改约/证据更新/设备服务关系变化→原文未改→点采纳；未变正例。
- **实际 / 预期**：回包重读控件/当前版本已改善；采纳只查输入/到期/主体/项目/identityActive，无task/facts/evidence复查，可仍显示“已采纳”。预期展示与采纳两层分别拒旧上下文，并在首次确认再核。facts指纹未覆盖services/category；不声称已原生落库。
- **根因 / 影响**：完整当前守卫只在回包阶段，采纳层未消费快照；陈旧设备/任务语义可被用户采纳，违反核心版本失效要求。
- **证据**：E/source-traces/_suggestionAcceptGate、source-audit；当前真实交错未执行，type/log白名单限制如实单列。
- **具体改法 / 验证**：保存完整task/facts/evidence绑定，三个边界共用当前context校验；事实版本覆盖影响定位字段。原生执行A等待→键入B→A迟到；A展示→变任务/证据/事实/主体/项目/撤权→采纳及确认；核控件/草稿/展示和权威盘，合法正例成立。

### D-M3-04 — P1 / 必修 / 任意引文可借合法ID标成verified

- **文件行**：main:3842–3893、3894–3922、4182–4255；事实库`:692–702`无version。
- **触发**：给合法as-a-3配version999及“并不存在的维修日志证明已修复”quote；合法用户原文来源正例。
- **实际 / 预期**：quote仅截长，合法ID+项目+active就verified；事实无version时任意模型version也不拒。category仅白名单枚举即可verified。预期verified只表示确实核验过的来源内容，缺历史标unknown，不能把伪引文显示已核。
- **根因 / 影响**：ID存在被当作来源引文真实性，核心“有来源”仍未成立。结构化来源、假ID/跨项目/停用guard及UI显式状态改善保留。
- **证据**：E/source-traces/_validateSourceEntry、snapshot/apply/formatter；source-audit。敌意seed不是实际返回/采纳反例。
- **具体改法 / 验证**：区分“事实ID存在”与“引文已核”；项目事实指向实际字段+版本/摘要，历史来源指向有权证据ID+版本+原文范围。不可核降unknown/unverified或拒绝；原生合法/伪引用、假设备、越权项目、非法status和恶意原文逐项核UI/主体/草稿/事件。

### D-M3-05 — P1 / 必修 / 精确最终回执和磁盘关联事件未完整消费

- **文件行**：main:5119–5166创建重放、5536–5554确认重放、5576–5601正常核验；`:858–867`事件保存。
- **触发**：事件写被冻结/落盘失败但内存push成功、task已OPEN；相同确认重试；AI/手工各验证。
- **实际 / 预期**：正常final返回/消费者flags与读task改善认可，但事件查EVENT_LOG内存；saveEvents拒写也可留内存事件。create重放把createDraft动作ID填作final_action_id，只核OPEN；confirm重放也直接final，缺同组三重核验。预期成功来自**精确confirm回执、任务、磁盘关联事件**，未知保持原意图，不把create动作当confirm。
- **根因 / 影响**：持久证据与内存混用，恢复分支绕过最终确认校验，AI/手工共同可能假成功；本轮未实际提交，不冒称已经触发部分提交。
- **证据**：E/source-traces/confirmDraft/createDraftFromPanel/saveEvents/logEvent；source-audit；H坏事件仅冷启动历史场景，未代替逐写点失败。
- **具体改法 / 验证**：正常与两条重放共用权威对账器，读磁盘receipt/event，核精确action/对象/版本；unknown保存同一不可变意图。AI/手工各成功、读回失败、事件失败、丢响应、重复确认、较新版本与同盘重开；核一个task、正确confirm action及唯一磁盘事件。

### D-M3-06 — P1 / 必修 / 选设备可误消除未解决的空间歧义

- **文件行**：main:4312–4349 `_computeResolvedAmbiguous`，`:4942–4989`确认拒歧义分支。
- **触发**：ambiguous_fields=[space,asset]；只人工选合法as-a-3，space还没澄清；各字段补齐对照。
- **实际 / 预期**：遍历每个a却不判断字段，只要asset_id被编辑且在alternatives中，就resolved.push(a)，可能同时消掉space歧义；预期每个核心定位字段只由对应人工选择解决。
- **根因 / 影响**：已增加确认拒未解歧义，但解决函数按设备选择统一放行所有字段，核心报修定位仍可能未确认。problem不吞定位缺项、空asset合法未知的改善保留。
- **证据**：E/source-traces/_computeResolvedAmbiguous及confirm；source-audit；原生未执行，不称实际已错误创建。
- **具体改法 / 验证**：白名单字段分别核human_edited和对应候选，重核空间/设备服务关系；未选/只选设备/只选空间/全部补齐四组，前3拒或继续补充，补齐后权威创建。

### D-M3-07 — 已闭合源码部分保留

模型审计字段白名单保留；本轮0真实请求，未执行真实审计，不用静态改善代签真实模型隐私验收。无新证据，不新增P1。

## 判定与本模块交接

- **最终结论：FAIL**，精确范围为M3-r6-worktree上一轮缺陷复核、3场独立原生冷启动/敌意盘/坏历史及直接M2依赖。不能称AI或手工核心全链跑通。
- **必修**：D-M3-01/03/04/05/06。先D01使原生业务根真正渲染并保留输入，再逐条最小修复，不扩审或优化后续模块。
- **BLOCKED仅限真实通道不足**：目标宿主unknown type/key输入（本轮type明确实证）；wait也unknown，不能精准安排交错。当前schema/白名单没有可用的延迟回包、运行途中上下文变更、精确提交写点失败及同盘跨进程重开动作。驱动需提供符合既有授权的输入/注入/重开能力；不得改用osascript、辅助功能或agent直接启动。**没有ABORT，也不以sandbox-exec rc71/pgrep rc3判BLOCKED。**
- **NOT_RUN**：三组原生MiniMax、AI及手工合法提交回读、实际恶意模型返回、完整版本交错、提交失败/重开恢复。未运行不等于新环境授权缺口；0模型请求，无余额错误。
- **受影响既有模块**：M2登录/根视图直接回归再次FAIL，确认/读回依赖源码未闭合。M2本身状态与报告不改；未动M0/M1/M4–M7。
- **门禁与台账**：仅更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M3 status及review_*，review_report指向本报告、review_candidate_id=M3-r6-worktree，保存旧review字段到review_history。作者build字段及原blockers保留为交接来源；当前审查结论见review_summary/review_blockers。ACCEPTANCE.json不改，历史后端PASS不转为本轮原生PASS。定稿校验见 E/report-verification.json。
- **不允许下一模块，不提供下一模块入口。** 本地catalog/install_staged路线已实证，不需要publish/公开签名/上架；身份/provider/离线签名已授权，技术修复和测试通道属于构建/驱动工作。`NEEDS_ABRAM=no`。

STATUS=FAIL
NEEDS_ABRAM=no
