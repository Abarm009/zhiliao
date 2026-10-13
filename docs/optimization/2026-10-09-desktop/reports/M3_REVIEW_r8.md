# M3 独立 Review r8

**最终结论：FAIL。** 受审候选 **M3-r7-worktree** 在本审查独立 harness 的 **3/3 场景均为业务 `view=false`、客户区空白**；未提交原文被清空。隔离与回收、候选和证据一致性通过，不能替代业务成功。D-M3-01 未闭合；D-M3-04 的伪来源收紧保留，但合法来源重核出现源码反例。AI与手工的真实确认/回读均未跑通，不能进入下一模块。

## 受审对象与范围

- 审查者 / 日期：本会话唯一 Codex 审查方，2026-10-12，Asia/Shanghai；未委派。当前接口不能验证主会话实际 Router 路由、指定模型切换、thread.createdAt/标题设置，未声称已切换或设置。
- candidate_id / base：**M3-r7-worktree / M3-r6-worktree**。依据用户交接的 build_r2_2104_REQUEST_build_r7、实施报告、CANDIDATE、GATES及请求定位，没有按mtime选版。作者报告 `reports/M3_IMPLEMENTATION_r7.md`；冻结清单 `runtime/optimization/2026-10-09/M3/r7/CANDIDATE.json`。
- HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty；主源 **473410字节 / SHA256 a6f55a21aa8ccd70e2bcc9a886dfdedab996b7811f6b447e62fd49a20d8cdee8**。四项冻结对象均匹配。第一段→第二段定稿前14个保护文件、75项独立seed/mirror及request摘要全部一致；没有覆盖他人改动。
- 前置：M2 **FAIL / M2-r7-worktree / M2_REVIEW_r8.md**，无已接受PASS候选。按用户前序挂账裁决继续M3原缺陷及直接依赖复核，不伪造前置满足、不修改M2结论。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`；本审查三场实际binary SHA均为 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**。
- 运行digest **b81fedb29f9c11e3cdcc42684f92d658c1a5663c21051a1df50b5373d9e7e362**。每场mirror、`.bundles`、`.running`三份main/config/identities与冻结对象一致；签名manifest与独立冻结artifact一致。原manifest与签名manifest能力/网络等业务语义一致，签名及canonical默认字段不列为错配。
- 模型配置：MiniMax / MiniMax-M3 / anthropic messages。当前三场needs_model=false，实际模型请求 **0次**；没有代理endpoint/MM_KEY注入、model_proxy_stats或billing_error。历史r3作者Python三次仅保留历史范围，不算当前原生通过。
- 独立请求 `M3/native/REQUEST_review_r2_2104.json`，SHA256 **2f6dbc228be5572a2b7ac859b92f7c4f399ed7a800581250a429adf01277c3aa**。驱动沙箱外执行窗口 **00:31:42–00:32:44 +08:00**。
- 本报告 **H/** = `runtime/optimization/2026-10-09/M3/native-runs/review_r2_2104_REQUEST_review_r2_2104/`；**E/** = `runtime/optimization/2026-10-09/M3/native/review_r2_2104/`；**A** = E/native-evidence-audit.json，脚本 E/audit_phase2.py。阶段笔记 `M3/native/REVIEW_NOTES_r2_2104.md`、请求与原始驱动证据保留。
- 已读：第一段AGENTS/CONTEXT/00/01/02/M3/04、上一轮r7缺陷、交接r7实现/清单/作者证据、r6→r7差异及相关函数、M2直接依赖和原T/U定义；第二段全部summary/result/profile/denials/full host.log/MANIFEST与运行盘、全部现存PNG内容、相关来源和确认分支。仅原D01–D07及受影响回归，无其他模块扩审。
- 已运行：第一段独立离线catalog验签、official install_staged/重建/may_run，rc0；驱动执行三场独立请求；本审查独立摘要、数据/元信息/完整日志/源码审计。未运行会覆盖作者结果的静态测试，Python审计不等于Splash业务执行。
- 数据/执行边界：仅项目内隔离合成数据。没有预装可信SESSION、读取真实账号明文或provider密钥；未改原业务数据，未自行启动宿主、sandbox-exec/pgrep、--help或任何未授权自动化。未读项目外memory。沿用已签名artifact副本，没有生成新私钥；作者anchor/working两把私钥再次核不存在，删除历史证据见build_r7/offline-store-evidence.json及E/candidate-audit.json。
- 置信度：候选一致、隔离回收、空白UI、运行错误、磁盘差异及来源源码反例 **高**；完整根返回/ui注入根因 **中**；真实模型/合法提交/交错/来源反例在固定宿主的动态表现 **未知或未运行**。

## 必需检查

|检查|独立操作|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/证据一致|比request/summary/result、14保护文件、75 seed、481 MANIFEST及运行三份包|同候选、无错配|全部匹配，遗漏0|PASS，证据范围|A；E/snapshot-start、seed-manifest、candidate-audit|
|隔离与回收|三场profile/probes/env/denials/pgid/退出核对|限制写、禁读、无残余|probes.ok=true，pre/post NONE，pgid_members_after=[]，CLEAN，host rc0，quit_http|PASS，隔离范围|H/*/result/profile/sandbox-denials；A|
|本地catalog/install_staged|独立验签/安装/重建，与实际包读回|本地路径可安装|两命令rc0；net/storage准入成立；实际加载相同包|PASS安装；业务运行FAIL|E/install-staged-audit；A|
|原生空盘/输入恢复|真正空字符串动作/事件盘+持久新原文A，launch/capture/type A/key Tab/type B/capture|登录/输入可操作，A恢复、输入能力可用|业务view=false/空白，pending_input被清空；type/key unknown|FAIL入口/恢复；键入通道BLOCKED|H/cold_empty_logs_input_restore；D01/D02|
|敌意盘权限/来源出口|B项目DRAFT+A空间+虚构设备/伪verified来源/恶意原文+saved actor；独立taps/capture|可信登录或拒绝出口，不能自动越权确认|空白；saved actor清为null，任务/回执/事件未变|FAIL可见出口；实际返回/确认NOT_RUN|H/forged_cross_project_saved_actor；A|
|坏历史恢复|合法→坏行→合法NDJSON事件盘，空任务；taps/capture/查盘|完整保留历史，可见禁写/恢复，不假成功|原历史保留，无bad_lines/恢复输出；空白；无业务提交|FAIL恢复出口；精确提交故障NOT_RUN|H/damaged_events_recovery；A|
|硬1三组真实模型输入|独立A歧义/B未知空间/C无历史恶意原文，核适配入口|新建议随地点/症状变，不造事实|三组原生请求0；输入不支持，业务根不可用|FAIL核心入口；模型效果NOT_RUN，输入通道BLOCKED|E/independent-inputs；H/cold日志40–42|
|硬2AI确认/权威回读|追来源guard→确认→M2，核实际盘|人工确认后精确task/receipt/event并可重开|D04合法来源重核源码反例；没有AI提交或确认回执|FAIL源码/入口；AI全链NOT_RUN|main:3881/3917/3955/4988；A|
|硬2/4手工路径|追面板→M2共同确认，核空盘|无模型可合法填齐、确认并回读|没有可操作表单，空盘未变|FAIL核心入口；手工提交NOT_RUN|H/cold；D01；main:5202/5709|
|硬3展示/采纳两层失效|源码两边界复核、独立输入能力探针|A迟到/B编辑、上下文漂移拒绝；合法正例成立|当前绑定守卫补齐源码；type/key明确不支持，未发生AI交错|源码改善保留；完整交错BLOCKED，动态NOT_RUN|main:2746/3830/4149/4840/5017；H/cold:40–42|
|硬4字段/恶意返回/错误恢复|核白名单/权限/来源/歧义，敌意冷盘|不改变身份/状态，不造设备，失败可人工继续|伪quote降级等改善；D04重核自拒；真实返回注入及人工成功未执行|FAIL D04；动态NOT_RUN|main:3880–3966/4364/4967；E/source-traces|
|硬5真实桌面编辑/取消/重试|全部PNG/完整日志/实际控制能力|输入与错误出口可用、无秘密审计|3/3空白，预存原文丢失；编辑/取消/重试/模型审计未执行|FAIL桌面；键盘通道BLOCKED|H/frames/logs；A|
|直接M2回归|同候选登录/任务共有加载、确认回读消费|可信主体与可靠执行作为基础|登录/业务根再次失败；共同提交未执行|FAIL入口；动态NOT_RUN，不改M2结论|M2_REVIEW_r8；本轮H/A|

### 原生证据逐项核验

summary.request与本审查request完全相同，harness/template摘要匹配；**481项MANIFEST全部匹配，无遗漏**。三场summary/result一致，19.26/19.39/19.37秒退出，host_returncode均0、quit_http，无ABORT/异常/残余PGID。

三份profile全文核过：默认禁写，允许写场景目录及/dev/null；五处禁读声明与kernel probes一致；网络仅本机控制TCP口及profile已有Unix socket许可，无模型代理。HOME/app-data/cache/config/data/tmp都位于场景目录。每场124项files_written_in_run_dir全部存在、唯一且在run内，与count一致；这项是mtime收集清单，**不是124次业务写入**。library_scan无新增，记录的真实home mtime前后一致；审查方未访问真实home复验。

全部sandbox_denials重算summary一致，出现443外联、项目外Metal缓存和部分/dev/dtracehelper写**被拒**，没有证据表明成功外联/越界写。443不能直接归因于MiniMax；重复deny行也不等于模型调用次数。

captures逐项核exists/sha256：三份initial截图均未生成，如实保留；三张final存在并逐张目视，均为空白业务客户区。全部六个PNG摘要/尺寸核过，三个part各与对应final同字节，共两种内容，内容均已目视；PNG为2800×1716全屏，不能由请求size证明业务窗口尺寸验收通过。cold final SHA `4880fff7a9a41ab18882969efebb832752861f0c9124c93a8b1dfcdf75593746`，另两场final SHA均 `7e52bba6c63c4d344efbc74bc5e7f8e7f2df47cbc458f1a4ee1403171572b00f`。缺initial不是唯一FAIL理由，final+view=false+完整运行错误已证明核心失败。

host_log_bytes、listening/quit/launched/eval/panic markers独立全文重算一致，无panic。业务473410字节view=false与另一809字节宿主view=true分开；后者不算业务通过。

|场景|[E] / ui作用域错误行数|index_of / slice错误行数|关键日志|
|---|---:|---:|---|
|cold_empty_logs_input_restore|36 / 18|177 / 356|68起字符串方法失败；1149预算超限；1150业务view=false；1163起ui不在作用域。40–42 type/key unknown。|
|forged_cross_project_saved_actor|36 / 18|177 / 354|66起方法失败；1149业务view=false；1162起ui不在作用域。无预算超限。|
|damaged_events_recovery|36 / 18|175 / 344|66起方法失败；1119业务view=false；1132起ui不在作用域。无预算超限。|

这些是日志行数，不是独立业务动作。第一处VM1185/1193/1195对应拆行相关源码1175–1195；运行注入造成行号偏移，报告修复引用实际文件行。tick相关VM8062/8066与源refreshLabels:8053起ui引用对应。只筛[E]/只跑parser不能证明真实执行通过。

业务盘 `home/.octosense/apps/octosense-repair/` 的tasks/actions/events/隔离accounts三场均与seed同字节，无新增业务文件。state.json三场pending_input从新描述A/C/B变空、panel从draft变none；敌意场saved actor变null、selected_task_id清空。**这证明预存输入恢复失败，不是已成功键入后丢失。** type/key日志明确unknown；盘未变和actor清空不能证明完整可信登录/权限/模型拒绝已通过。坏事件源保持原样，但无bad_lines及可见恢复出口；没有在业务提交点制造写失败，不能代签事务恢复。

model_proxy_stats缺席，needs_model=false，无endpoint/MM_KEY注入。本轮0请求、无billing_error；net准入/config与被拒443都不能证明真实MiniMax调用。未来真实调用仍须经needs_model代理并先核全模块≤10预算，遇402/欠费立即停止记录脱密原错误。本轮没有需要Abram补余额的证据。

### 相关既有用例逐项判定

|用例|本轮判定与范围|
|---|---|
|G0-E|**FAIL核心入口**；provider配置/net准入改善；真实MiniMax原生效果NOT_RUN，0请求。|
|T01|**FAIL入口/D04源码**；真实原话→结构化可编辑草稿未发生，三描述模型NOT_RUN。|
|T03|事实/联系人guard源码保留；越权冷盘无确认；合法/缺项提交动态NOT_RUN，保留内容入口FAIL。|
|T25|状态/身份/假设备白名单源码保留；敌意seed不是实际模型返回，动态NOT_RUN。|
|T26|**FAIL可见失败/人工出口**；模型错误状态源码保留，真实失败及手工合法提交NOT_RUN。|
|T33|独立新描述和同义句冻结；意图泛化模型效果NOT_RUN，键入通道BLOCKED。|
|T34|伪quote降级保留；**FAIL D04合法来源自拒源码**；缺项/多候选/无历史动态NOT_RUN。|
|T35|当前task/facts/evidence/主体绑定源码改善；完整展示/采纳交错BLOCKED于白名单能力，未执行。|
|T36|当前provider/config/白名单及本地准入可定位；实际适配器调用/敌意返回动态NOT_RUN，不声称未来octos适配已实现。|
|T37|磁盘三重对账改善；AI/手工最终回执、读回失败、重复确认和较新版本恢复NOT_RUN；精确注入/连续重开通道BLOCKED。|
|T38|同候选/宿主/配置/输入/seed可重跑，摘要核验通过；成功与失败业务固定条件复跑NOT_RUN，不以版本可定位代签全项。|
|U02|**FAIL真实可编辑草稿/人工出口**，无表单；未完成原话到确认链。|
|U07|**FAIL预存输入恢复**；稳定动作/响应丢失/版本冲突源码改善或挂账，动态NOT_RUN，精确故障能力BLOCKED。|
|U08|**FAIL空态/无权限/恢复出口**，3/3业务空白；不声称附件等非本模块场景已重验。|
|U11|**FAIL真实宿主面板/输入可用性**；type/key确实不支持，键盘项BLOCKED，真实滚动/取消/重试NOT_RUN。|

## 缺陷及原编号闭合情况

### D-M3-01 — P1 / 必修 / 当前宿主核心仍不能渲染

- **文件行**：app/bundle/main.splash:1175–1195 `_splitJsonlLines`，1061/1099迁移、872/886读取、943起load；8791起root，8053–8063 refreshLabels、9851–9891 tick/初始化/root返回。
- **触发**：使用本次任一独立seed从本地catalog冷启动；其中cold将动作/事件日志置为真正空字符串，仍出错。array与坏NDJSON场同样失败。
- **实际/预期**：实际3/3业务view=false，全部final截图空白，反复index_of/slice方法缺失、tick的ui作用域错误；cold另预算超限。预期当前固定宿主显示可操作登录/任务/报修输入，不阻断初始化或周期刷新。
- **根因**：拆行仍调用固定发行宿主实证不提供的String.index_of/slice，空字符串也先进入该循环，迁移空数组也可能落入拆行；在错误值上继续循环放大启动错误。ui句柄/根安装在当前启动路径没有成立，完整注入根因需同宿主进一步定位。反转widget提升、裸root、延后首刷只作源码改善，不能当已跑通。
- **影响**：同时阻断AI/手工核心入口和失败恢复，属于本模块真正P1；不是sandbox预检BLOCKED，也不是建议性布局优化。
- **证据**：H三场full host.log及frames；A runtime_error_lines、business_eval_lines、method_error_firsts/counts；E/source-traces与r6→r7 diff。
- **具体改法**：Kimi先处理这条直接加载依赖。对空字符串/已解析数组提前返回；其余NDJSON采用该**固定宿主实际验证支持**的拆行原语，错误时立即退出并保存完整原文，不能在error上循环。root/widget句柄/刷新改成该宿主实证模式，在根可用前不调用ui；不能靠提升预算或只查parser掩盖。保留net和代理覆盖，不加新壳、不修无关模块。
- **验证**：同digest新Store的空字符串/空数组/合法NDJSON/夹坏行冷启动，零阻断运行错误，业务根真实渲染，合法/错误登录出口可见，真实输入与恢复可操作；随后AI和手工各确认至权威回读。本轮空白原生失败已经独立成立。

### D-M3-02 — 写入/恢复源码部分保留；动态输入恢复FAIL，归D01共同必修

- **文件行/证据**：main:479–497 loadViewState、4684–4725 editRawText、9851–9866 tick；A三场state_changes，H实际state.json与独立seed。
- **触发/实际/预期/影响**：冷启动带未提交新原文A/B/C；实际被清空、panel变none、无控件；预期原文保留并恢复真实输入。阻断可编辑草稿和失败后继续。
- **根因范围/改法**：新增STATE.pending_input写入/首tick set_text保留，但当前load/root/ui路径未成功恢复。先闭合D01，检查load到持久state与首tick的实际读取/写回次序，不能以“准备就绪”覆盖丢失的草稿。没有证据证明type成功，不误报“键入后丢失”。
- **验证**：预存A冷启动仍在控件/盘，同文同步no-op；真实编辑B、取消/重试、重开不丢。与D01合并处理，不重复新增P1。

### D-M3-03 — 原缺失守卫源码已补；动态闭合未完成

- main:2746–2780、3807–3858、4149起、4229起、4840起、5017、8998–9002。事实指纹加services/category，apply保存task/evidence快照，采纳/首次确认共用当前guard；展示回包同步输入。原“采纳不核当前task/facts/evidence”源码原因已针对性修改。
- 当前完整交错未执行，不能宣布硬3通过。修改后与未修改正例的真实回包/采纳/首次确认仍需验证；不据未运行再新增同根因P1。
- **验证/解阻**：驱动/宿主提供合规白名单输入、延迟回包、途中更新上下文能力，执行A等待→B编辑→A迟到、A展示→task/事实/证据/主体/项目/撤权→采纳；分别查展示/草稿/盘，合法正例也通过。禁止转用未授权自动化。

### D-M3-04 — P1 / 必修 / 合法来源重核被缺省version自拒（源码反例）

- **文件行**：main:693–704无version事实库，3881归一化version=0、3899声明读取、3917/3930无版本事实降级、3955–3957二次校验、4988–4992确认消费。
- **触发**：合法当前项目来源 `{fact_id:"sp-a-1"}`，不声明version/quote，正常parse/apply后用户确认；合法asset无version同理。
- **实际/预期**：首次_validateSourceEntry得到verified并保存version=0；确认无条件重建含version:0的entry，因事实无version而降unverified_text，随后以“来源已失效”拒绝。预期不变的合法来源重新校验仍成立，伪造version/quote继续拒核。**这是精确源码分支推导，原生正例因D01未运行；不冒称本轮已经在UI触发拒绝。**
- **根因/影响**：归一化把“未声明version”变成“声明0”，重核语义不幂等；阻断有来源AI草稿的合法确认，属于核心P1。原“任意quote/版本可verified”的负例收紧保留，不撤回安全改动。
- **证据**：E/source-traces `_validateSourceEntry`、`_validateSourcesSnapshot`、confirmDraftModelBound；当前冻结源上述行，阶段笔记同反例。
- **具体改法**：保留version是否存在的元信息，重核省略未声明的版本；或为来源绑定真实可核的事实摘要/版本并前后一致。不要把任意version当正确、不要一律verified。新增正例覆盖归一化→落草稿→重新校验，不只检查伪引文被降级的字符串存在。
- **验证**：合法space/asset无version/quote两组正例可采纳并确认；version999、非空伪quote、假ID/跨项目/停用负例仍降级/拒绝；原生确认后查M2精确回执/事件/任务，不用Python等价对象当最终通过。

### D-M3-05 — 原磁盘消费/重放源码改善保留；真实提交恢复待验

- main:5202–5288、5668–5758：三路径共用磁盘task+confirm final+同action事件对账，create回放不再冒用create ID，DRAFT恢复沿用task_id。原内存事件假成功与create ID误消费的源码原因已针对性修改。
- 没有本轮AI/手工实际确认、事件写故障、读回超时、响应丢失或重开。坏历史盘冷启动未到commit，不代签逐写点恢复。
- **原范围残留建议**：对账仅接task_id并挑某条confirm final，宜绑定原意图的精确action/内容/前后版本，避免较新任务或另一个旧确认混用；本轮没有动态触发假成功，不据此新增必修P1。
- **验证**：AI/手工各真实成功与回读，再缺事件/缺回执/丢响应/重复确认/同盘重开/更高版本；一task、正确confirm action及唯一关联磁盘事件。先解D01，精确故障/重开超出白名单能力则BLOCKED并提供控制缺口。

### D-M3-06 — 原逐字段解歧义源码已补；动态闭合未完成

- main:4364–4418及5040–5057；asset/space分别核对应人工选择，设备重核存在/同项目/active/alternatives，确认拒未解项。原“选设备同时消空间歧义”分支已改，不重复列同原因必修。
- **验证**：无选、只选设备、只选空间、全部补齐四组；逐字段查未解项，只有完整合法定位可经M2权威确认。当前表单不可用，动态NOT_RUN。

### D-M3-07 — 原源码白名单闭合保留，真实审计未运行

没有新增秘密输出证据，不新增P1。本轮0模型请求；静态字段白名单不代签真实模型审计或G0-E。

## 判定与本模块交接

- **最终结论：FAIL**；精确范围为M3-r7-worktree原D01–D07复核、三场独立原生冷启动/输入恢复/敌意盘/坏历史以及M2直接依赖。
- **必修**：D-M3-01（含D02共同输入恢复）、D-M3-04合法来源重核。其余源码改善保留，待必要动态验证；非核心建议挂账，不用建议项判FAIL。
- **BLOCKED仅限白名单能力不足**：cold host.log:40–42明确unknown type/key；中文键入/登录凭据输入及依赖它的完整AI交错无法覆盖。schema没有延迟回包、途中上下文变更、精准提交故障、同盘连续重开控制。由驱动/宿主提供符合已有授权的通道即可解阻，不能用自动化绕过。没有ABORT，不用rc71/rc3判阻塞。
- **NOT_RUN**：三组原生MiniMax、真实非法模型回包、AI/手工合法确认回读、全部精确提交故障/重开/动态歧义正负例。原因分别为已复现D01或白名单能力不足；不存在可用运行条件时不拿作者声称代替。
- **受影响先前模块**：M2登录/共有根入口复验FAIL，可信业务提交未执行；M2结论保持，M0/M1/M4–M7不改、不执行下一模块。
- **门禁/台账**：仅修改 `docs/optimization/2026-10-09-desktop/GATES.json` 的M3 status及review_*，review_report指向本报告，review_candidate_id=M3-r7-worktree；旧审查字段归档review_history。作者candidate/base/implementation_report/build_summary/blockers及其他模块保持原样。ACCEPTANCE.json不改，历史后端PASS不转成原生PASS。读回校验见E/report-verification.json。
- 本地catalog/install_staged路线已成立，不需要publish/公开签名/上架。身份/provider/隔离签名授权均已有；技术修复与输入通道不是新授权缺口，未出现余额/欠费错误，**NEEDS_ABRAM=no**。
- 留在M3：Kimi先以harness证明D01零阻断错误并渲染登录/真实输入，再最小修D04，逐项完成以上动态正负回归。完成新候选/证据交接后独立重审；不提供下一模块入口。

STATUS=FAIL
NEEDS_ABRAM=no
