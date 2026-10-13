# M3 独立 Review r14

**最终结论：BLOCKED。** 正式候选 **M3-r10-worktree** 的 D-M3-02「合法持久输入被误判损坏、原文和确认意图未恢复」冷恢复缺陷已关闭；本轮受审范围没有未闭合业务 P1。真实输入→AI建议→人工确认→M2权威回执与回读的核心链仍无独立运行证据，且受控迟到/恶意回包及同Store重开不在当前白名单测试机制覆盖内，不能据恢复子项或8场CLEAN判模块PASS。

置信度：候选绑定、冷恢复与保源、运行日志及隔离记录 **高**；登录后控件恢复、AI/手工合法建单与真实模型效果 **未知（未运行）**。本报告不因P2建议或BLOCKED-HOST判FAIL。

## 审查对象与边界

- 审查者：本主会话，2026-10-13（Asia/Shanghai）；未委派代理、未修业务代码、未进入下一模块。Router路由与指定模型无法从现有工具确认/切换；无本对话createdAt/标题读写接口，未声称完成切换或改名。
- 交接依据：GATES的candidate_id、`M3_IMPLEMENTATION_r10.md`、`M3/r10/CANDIDATE.json`，以及用户本次明确交回的独立请求运行。**M3-r10-worktree / base M3-r9-worktree**；HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty。没有按文件时间选版，没有把上一轮共享观察运输冒作本轮正式包。
- 正式源码：765252 B，SHA256 **ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e**。当前源、r10冻结源、上一轮共享观察源全等；四个frozen_objects均匹配清单。第1段与第2段写门禁前保护对象全等。
- 正式运输digest：**ddd0eb06ef6afda8cc36174c64e0c5519e84ac695854b94f6f502cf62d45ed6f**。curated包排除.bak，与r13含备份文件的共享运输digest不同；业务源码相同，运输证据分别定位。
- 第1段材料 **E/**：`runtime/optimization/2026-10-09/M3/native/review_r2_1659/`；阶段笔记为同级`REVIEW_NOTES_r2_1659.md`。请求同级`REQUEST_review_r2_1659.json`，SHA256 **2b18d81fe6038ec0a03a60a8190cd320f8eb1d7cf13f648c9234d485da938bdd**。
- 第2段独立原生证据 **H/**：`runtime/optimization/2026-10-09/M3/native-runs/review_r2_1659_REQUEST_review_r2_1659/`；实际执行记录 **19:30:43–19:33:04 +08:00**。本审查只读取H，不启动或重跑宿主，不覆盖原证据。
- 实际宿主rc.6：`host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 **2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a**。harness SHA256 **8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7**；profile模板 **76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f**。均重新对实际文件核算。
- 前置：M2 r18 **仅JSON读取差异PASS**，整体依Abram裁决carried结束；GATES的M2仍FAIL/r17。本轮不制造整体M2 PASS、不更新M2。D-M2-05/D-M4-03为BLOCKED-HOST，不计P1；没有用这两项阻断M3。
- 已读范围：第1段AGENTS/CONTEXT、00/01/02/M3/04、r10实施与清单、r13缺陷、M2 r18与相关源码；第2段重新核全部八场result、summary、profile、denials、log、frames、manifest及权威盘。只复核原D02及其直接影响，不扩审其他模块。
- 模型：源码MiniMax配置与本机endpoint覆盖保留；八场全部`needs_model=false`，本次真实请求0。没有读取provider密钥/真实明文凭据，没有余额错误。

## 必需检查与独立结果

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|正式候选/宿主/运行一致|重算请求、四源、seed、mirror/installed/.running及宿主SHA|运行确为M3-r10与rc.6|请求全等、资源全等，实际765252 B业务脚本加载|PASS|E清单/phase1-audit；H全部result/log/资源|
|隔离与回收|逐场核profile/probes/env/进程/退出/文件和denials|probes.ok、pre/post NONE、PGID空、CLEAN|8/8符合，quit_http/rc0；无ABORT|PASS（记录范围）|H各profile/result/denials|
|冷开渲染回归|空盘launch-hub→capture，核日志|零解析/运行错误、真实根可见|正常登录页，零[E]；没有登录后工作台操作|PASS冷根子项|H/review_cold_r10|
|D02中文原文恢复|新北楼插座异响描述，含引号/换行/emoji/路径；回读四字段|原文/意图/嵌套payload/原key全等，无损坏备份|71码点/202 UTF-8 B原文；1274 B seed→2986 B完整默认补齐state，四字段全等|PASS|H/review_new_unicode；E/expectations|
|D02字面转义恢复|新楼梯灯描述，字面反斜杠/Unicode拼写|不得误判实际非法转义，四字段全等|111码点原文；1137→2849 B，四字段全等，无坏备份|PASS|H/review_literal_backslashes|
|D02长输入恢复|2912码点/6936 UTF-8 B新原文，含嵌套序列化payload|四字段保真；运行错误另判|18687→20399 B，四字段全等、无坏备份；log:55一次预算[E]|恢复PASS；零运行错误FAIL，原P2挂账|H/review_long_input|
|转义同名重复键|pending_input与转义后同名键、无关旧boot-bak|整对象拒收，本次源独立精确保全，旧bak不动|1341 B坏源在corrupt-bak逐字相等；旧boot-bak不变；四恢复字段均未采纳|PASS|H/review_escaped_duplicate|
|尾随垃圾且槽满|合法前缀+垃圾、三个不同旧副本占满|原主/旧副本不动，视图冻结，人工出口可见|1326 B主及三副本全等；图有保源/冻结/人工修复说明|PASS|H/review_trailing_full_slots|
|精确旧备份复用|449 B截断源与已有boot-bak相等，另有旧corrupt-bak|只复用精确源，旧副本不动，不接受部分字段|两旧副本不变，无额外坏备份；四字段拒收，state写明精确复用|PASS|H/review_exact_backup_reuse|
|伪保存身份/恶意原文|保存伪经理/session、越权项目/假设备/CLOSED原话冷开|保存内容不构成身份，不写业务|actor/session为null；原文/意图恢复；三业务盘字节不变，仍登录页|PASS冷保存权限子项|H/review_forged_context|
|硬1：三组真实AI建议|现场输入，缺项追问、多设备歧义、不同地点症状|真实模型随输入变化且不编造|本次是预存恢复夹具，0模型请求；无实时键入/建议|NOT_RUN|H请求/代理字段；不能用恢复正例代签|
|硬2：AI与手工权威成功|分别明确确认→M2最终回执/关联事件→工单回读/重开|未确认不OPEN；成功有权威结果|8场tasks/actions/events都是原空数组；未确认无写子项PASS；两成功链未执行|AI NOT_RUN；手工 NOT_RUN|H各业务盘|
|硬3：展示与采纳双层失效|A请求后改B、迟到A；展示后再改上下文并采纳|两层旧建议均拒绝|没有实际交错；当前机制无受控模型返回/同Store中途重开场景字段|NOT_RUN；控制覆盖BLOCKED|B-M3-01，见下文|
|硬4：错误回包与失败兜底|恶意/格式错/自报完成回包；模型失败后手工继续|无非法副作用，手工仍受授权边界|只做恶意原文冷盘负例；未执行模型回包或合法手工兜底|NOT_RUN；受控回包覆盖BLOCKED|H/源码仅保留性证据|
|硬5：桌面编辑/取消/重试|可信登录后真实控件与键盘操作|原文可编辑，取消/重试可恢复|16图均登录页；持久原文PASS；实际编辑/取消/重试未执行|NOT_RUN；当前有效输入覆盖BLOCKED|H/frames；B-M3-01|

上述“PASS”只属于明确的冷恢复/安全/隔离子项，不是整个T/U项或本模块PASS。

## 运行证据逐项核验

1. **summary/result/命令**：summary.request与独立请求全等；summary的场景投影字段逐一等于各完整result。八场顺序、purpose、batch、1280×800请求及实际命令一致；实际只有launch-hub/capture。各场16.20–16.26秒，host_returncode=0、quit_http成功，无panic、无未加载应用提示。业务eval均765252 B、view=true；日志未直接打印运输digest，因此`digest_seen_in_host_log=false`如实保留，版本通过实际运行资源核对成立。
2. **MANIFEST/seed/资源**：重算 **1744条MANIFEST.sha256** 全部一致；**285条seed文件哈希**与准备材料完全一致；八场每场14个资源的mirror、installed、实际唯一.running三份，共 **336次资源SHA比较** 全等。catalog在seed中真实存在，不依赖自动补入；没有混入旧r9或r13运输。
3. **profile/probes/env**：八份profile重构文本与模板、场景目录、实际本机控制端口全等，profile SHA匹配result。apply rc0；外写probe refused/created=false；五类禁读probe ok；osascript exec probe refused/ok。HOME、app-data、cache/config/data/tmp等全部归本场目录。无模型代理放行。本轮只读探针证据，不访问其秘密目标。
4. **进程**：pre/post均rc1、NONE且无stderr；活动成员属于本场PGID，回收后数组为空；实际binary SHA匹配rc.6。驱动记录外部HOME的.octosense mtime前后不变，Library扫描空；不把这些观察扩大为机器全量写入审计。
5. **captures**：8/8请求capture存在且SHA与result匹配；包含part在内共 **16张有效PNG，物理尺寸2800×1696**，5种不同SHA内容已逐一目视，其余以同SHA映射。均为登录页；槽满图有完整失败保护提示。1280×800是命令请求尺寸，不能将2800×1696帧当作实测客户区或签完整工作台布局PASS。未出现业务脚本解析导致空白；登录后业务区未运行。
6. **files_written_in_run_dir**：共 **1448条**记录，各场180–182条；核排序、唯一、计数（均未触及400截断）、实际存在与路径归本场。此集合是驱动按mtime收集的记录，包含资源/日志/图等，不冒称全量系统副作用监测。三权威业务盘每场原字节不变。
7. **sandbox_denials**：逐场从原denials重算summary与result全等。合计明确拒绝：osascript执行66条、443外联27条、/dev/dtracehelper写16条、两类系统Metal缓存写39/32条。数字仅为harness正则计数，不含重复报告展开。**拒绝尝试确实存在**，不是“没有尝试”；没有成功执行/写入证据，不能把被内核拒绝的宿主尝试当已完成系统自动化或模型调用。未发现允许越界的profile变化；不擅自修改宿主。
8. **host_log_markers**：remote listening/quit、launched、eval、panic/app_not_opened、日志字节数与tail全部从完整log复算一致。解析诊断0；7场运行[E]为0，长输入1条预算[E]。没有用CLEAN抹去错误。
9. **model_proxy_stats**：八份result均无此字段，所有request.needs_model=false，场景无proxy产物，profile无proxy端口，符合本次未开启代理。不是“真实代理调用成功0错误”；原生真实建议未执行，计本轮0调用，无billing_error/402证据。
10. **保护与私钥**：第1段保护对象、全部准备seed/mirror字节到写门禁前仍一致。复用已有同digest离线签名catalog，本审查没有生成私钥；作者`build_r10/keys`为空、两key路径不存在。没有publish/listing/外部安装。

核验直接在内存运行，未另写审计文件或改H/E历史材料。本轮summary SHA256 `e3d4795681eb2bb387c9bdc0c1080f348d34102fe52d554c6cb042dcacb7082d`；MANIFEST SHA256 `e993231bc9d03759d58708ecb2065ce2321c008495a8e4bf446badd2192140de`。初次审计误把summary投影当完整result、假定旧帧尺寸；按实际结构/PNG头纠正后重新验证，最终没有证据不匹配，未将审计假设错误列为产品缺陷。

## 原缺陷闭合与建议挂账

### D-M3-02 — 原P1 / 必修：CLOSED（冷恢复缺陷）

- **文件与行号**：正式`M3/r10/source.main.splash:1951–1996`严格读取及四字段并入；`:990`保源helper；`:2364`视图拒写门禁；`:15179–15194`输入恢复接线。源码与当前main全等。
- **原触发/实际/预期**：r13正式r9的合法中文state被误判损坏，四字段清空。预期合法持久原文、确认意图/嵌套payload、原动作键完整恢复，坏源保护不退化。
- **本次证据/实际**：正式新包中独立中文、字面转义、2912码点长输入四字段全部全等；无坏源备份；重复键/槽满/精确复用负例全部保源成立，未认证业务盘无新增。
- **根因与改法落实**：按r13要求把已验证共享严格读取接线冻结成正式候选，解决“正式包仍用旧门禁”的版本缺口，没有继续重写读取逻辑或新增入口。当前不是仅换candidate标签。
- **影响/置信度**：已证明冷恢复不再丢失合法原文或稳定意图，置信度高；**没有证明登录后控件可编辑或恢复意图可合法重提**。这两项保留NOT_RUN，不倒签完整端到端通过。
- **后续**：本项不再要求业务修复；保持当前冻结字节。解阻后在既有界面核实际控件与同意图继续，不通过伪会话或手工制造OPEN证明成功。

### A-M3-R13-01 — P2 / 建议：长输入运行预算诊断继续挂账

- **文件/行号**：`main.splash:3297–3305` `_charAtSafe`、`:7325–7337` hash、`:15183–15185`恢复hash；本轮`H/review_long_input/logs/host.log:55`定位源码3303:11。
- **触发/实际/预期**：2912码点/6936 UTF-8 B原文冷开一次预算[E]；四字段全等、无坏备份、根可见。期望恢复链零预算错误。
- **根因/影响**：字符helper反复to_chars有重复扫描；日志没有完整栈，唯一调用链原因未知。未证实此次造成原文丢失/业务区空白，依用户裁决保持P2，不升级必修，不据此判FAIL。
- **具体建议/验证**：沿用r13在已有字符/hash路径复用字符数组的建议，保持指纹/版本守卫，不新增字段/入口、不跳过来源检查；同长输入及短中文/emoji复跑核零[E]与hash语义，动态失效另须真实操作。此次不改代码。

### A-M3-R12-01 — P2 / 建议：成功保源的可见诊断继续挂账

- **文件/行号**：`main.splash:1958–1962`备份成功只写STATE.status；当前登录页消费失败notice。
- **触发/实际/预期**：重复键已精确保源、精确旧副本已复用，磁盘status有依据/路径；对应真实登录图仍只显示账号提示。期望现有反馈出口说明已保源依据，不另建页面。
- **根因/影响/证据**：登录反馈与成功state.status未接通，属反馈缺口；H/review_escaped_duplicate、review_exact_backup_reuse的state与frames共同证明。未见核心丢失，建议，不据此判FAIL。
- **具体建议/验证**：仅在既有反馈出口显示保源说明；同场核同屏文字及副本字节。保持原建议，本轮不修。

|原编号|本轮精确状态|
|---|---|
|D-M3-01|冷根/解析0诊断PASS子项；长输入运行诊断为原P2；认证工作台NOT_RUN|
|D-M3-02|冷恢复原P1 CLOSED；登录后控件/意图继续NOT_RUN|
|D-M3-03|源码守卫保留；伪保存主体无写PASS子项；动态双层交错NOT_RUN|
|D-M3-04|来源/version_present保留；恶意原文冷保存无写PASS子项；来源→展示→采纳→确认NOT_RUN|
|D-M3-05|显式outcome/权威结果绑定保留；AI与手工权威成功及回读分别NOT_RUN|
|D-M3-06|逐字段解歧义保留；真实追问/多候选/无历史NOT_RUN|
|D-M3-07|MiniMax/config/本机endpoint保留；原生真实效果NOT_RUN|

没有本轮相关差异新增用户功能/入口的实证，没有新业务P1；没有把源码守卫保留写成动态闭合。

## BLOCKED原因与解阻条件

**B-M3-01：只针对实际白名单测试覆盖缺口，不针对普通cold harness。** 本次harness没有ABORT，8场原生确实执行；未使用agent sandbox-exec rc71/pgrep rc3判阻塞。

- **证据位置**：`driver/harness/request.schema.json:52–60`内置test_actions；其场景属性没有受控模型回包/迟到调度/同Store中途重开控制；`native_harness.py:39、242`的ui_actions桥接调用osascript/System Events。本次最高优先用户禁止osascript、辅助功能及自动化，故不调用该桥接。
- **实际/预期**：预期审查能在可信登录后改输入、控制回包到达/内容并分别检查展示与采纳，随后人工确认和同Store重开。现有本请求只有launch/capture，预存state不能替代上述动态；schema无受控回包动作。文档中旧宿主type/key不支持有历史证据，但本轮没有对rc.6执行type/key，**不声称新rc.6已验证缺此能力**。
- **影响**：双层失效、恶意回包、可信会话后输入/重试及恢复意图继续不能完成独立运行判定；这是真实核心验收缺口，不能用冷恢复PASS或作者模型自述代替。
- **解阻条件**：驱动在当前授权范围内提供并实证有效的内置输入/会话操作、受控迟到/恶意响应和同Store重开测试机制，交回同候选的真实操作记录/frames/log/权威结果。没有声称所有点击都不可行，普通尚未执行的AI/手工成功项仍记NOT_RUN。验证机制是BLOCKED；业务功能是否失败仍未知。
- **留在M3的验证清单**：可信登录后原文恢复/编辑；≤10模块总预算内三组新真实MiniMax建议；请求A/编辑B/迟到A和展示后变更再采纳；恶意回包/非法状态/权限失败及模型失败手工兜底；AI与手工分别确认→M2精确final回执/关联事件/工单回读→同Store重开与稳定意图重试。只使用既有功能，不新增业务字段/入口，不修改挂账其他模块。

身份来源、provider、离线签名及本地catalog路线已获授权且可定位；不要求再次授权、不公开publish、不更换计费渠道。剩余为技术测试覆盖和未执行证据，**NEEDS_ABRAM=no**。

## 既有验收台账的精确范围

|项|本轮状态|
|---|---|
|G0-E|NOT_RUN：0真实模型请求，配置不代调用|
|T01|原文持久恢复PASS子项；模型提取/追问/编辑NOT_RUN|
|T03|未认证/未确认无OPEN及草稿原文保留PASS子项；合法/缺项/越权实际提交NOT_RUN|
|T25|恶意原文/伪保存主体不能改角色或写任务PASS子项；恶意模型/非法状态动态NOT_RUN|
|T26|模型失败说明及合法手工兜底NOT_RUN|
|T33|NOT_RUN：三个恢复正例不等于真实意图泛化|
|T34|来源/设备候选相关源码保留；真实引用及歧义处置NOT_RUN|
|T35|双层动态失效NOT_RUN；受控交错覆盖BLOCKED|
|T36|错误/越权回包与实际白名单契约NOT_RUN；受控回包覆盖BLOCKED|
|T37|稳定意图/key冷恢复PASS子项；AI/手工M2权威确认、待核验/重试/重开分别NOT_RUN|
|T38|正式候选/请求/宿主/资源及恢复复跑可定位PASS子项；真实模型同条件复跑NOT_RUN|
|U02|持久原文与意图保留PASS子项；实际编辑/补缺/采纳NOT_RUN|
|U07|冷恢复及坏源保全/冻结PASS子项；实际取消/重试/重复点击NOT_RUN|
|U08|登录根、槽满失败说明/人工出口PASS子项；保源成功反馈原P2；业务待核验反馈NOT_RUN|
|U11|真实根/capture PASS子项；键盘/滚动/业务面板/完整工作台NOT_RUN|

没有新增完整既有T/U/G0用例PASS可登记，**ACCEPTANCE.json不改**；历史后端结果不覆盖解释为原生PASS。先前模块未扩审，M2仅继承用户r18/carried裁决及共享读取证据，不签整体PASS。

## 判定与门禁

- **最终结论：BLOCKED。** 精确范围：正式新候选D02冷恢复闭合及受影响安全回归已独立运行通过；原生核心链未证实，特定白名单控制缺口阻断剩余硬验收。
- 本轮未闭合业务P1：**0**；建议仅A-M3-R13-01/A-M3-R12-01挂账；不是“带条件PASS”。
- 只更新GATES的M3状态及review_*审查字段，review_report指本报告；原审查字段快照追加review_history，作者candidate/base/实施字段与其他模块保留。旧blockers为作者交接原文，当前审查结论以review_summary/review_blockers为准。
- 本第2段仅写本报告和GATES；未改业务源、准备材料、请求、harness或H证据。未启动宿主、未读秘密、未发消息/issue/评论、未push/publish/部署/换渠道。
- 第1段项目外记忆索引误读已如实写入阶段笔记；属于审查过程范围偏差，不能被原生CLEAN抵销。本第2段只访问项目内材料。它不是源码产品缺陷，本报告不掩盖该偏差或用其充当当前原生隔离通过证据。
- **不允许进入下一模块；不给下一模块入口。** 留在M3解决上述具体测试覆盖并交回核心链独立证据；不要求重写已关闭D02，不执行P2优化。

STATUS=BLOCKED
NEEDS_ABRAM=no
