# M3 独立 Review r4

- 最终结论：**FAIL**。只复核上一轮 D-M3-01～07 的闭合及受影响回归，不修业务、不进入下一模块。
- 审查者 / 日期：本会话唯一独立审查方 / 2026-10-11，Asia/Shanghai。置信度：候选字节、源码分支和本地安装结果高；发行宿主 UI、真实模型、权威提交与恢复未知。
- candidate_id：`M3-r4-worktree`；base：`M3-r3-worktree`。由 GATES、CANDIDATE、实施报告三处明确交接定位，未以文件时间选版本。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r4.md`。
- 当前主源 SHA-256：`1a2773cf446a13db70af1ac5f74f61ec0e171aadb939f775ee8195c40ab001b4`，320576 字节、7077 行；清单 SHA 与行数匹配，280760 字节声明错误。base 留存源 SHA 与 before_sha256 匹配，增量已保存。
- 被审 HEAD、主源/配置/manifest 和身份数据摘要：`runtime/optimization/2026-10-09/M3/review-r4/results/start-snapshot.json`；结束核对及材料自检见同目录 `end-snapshot.json`、`report-verification.json`。审查候选不是仅用 HEAD 描述的干净提交。
- 前置：M2 为 `M2-r4-worktree` / **FAIL**，见 `M2_REVIEW_r4.md`；没有已接受的 M2 PASS 候选。按本次前序挂账裁决继续局部复审，不修 M2、不把挂账解释为 PASS。实际创建可靠性仍直接阻断 M3。
- 阅读范围：AGENTS、CONTEXT_M3、00/01/02、M3 模块、04 模板、M3 r3 原缺陷、r4 交接/清单/证据及缺陷对应源文件、M2 r4 前置和受影响提交问题、相关 T/U 定义。CONTEXT 的未裁决 provider / M2 BLOCKED 为旧记载，以当前用户裁决和独立报告为准；没有重新通读所有历史实施文档或无关模块。
- 实际环境：项目内终端、本地 `runtime/identity/evidence/vm/target/release/identity-vm-probe`、项目内官方 Hub/Store 探针；该 VM 不是发行桌面。指定 launcher 为 `M0/r3/host/app-extracted/OctoSense.app`，本轮未启动。实际宿主二进制摘要另核于 `results/host-pin.json`（本轮末核，不伪称开始快照已含）。
- 模型路由 / 标题：工具没有提供主会话实际路由或 createdAt/标题读写能力，无法独立确认 Router / gpt-6.1-sol，也没有切换或冒称已设置标题；未委派子代理。
- 已运行：候选/base 摘要及差异；新隔离预检；局部 Splash 探针；独立新恶意返回 Python 契约探针；原 bundle check；当前源码副本离线签名 catalog、官方 install_staged、Store 重建/may_run、篡改拒绝及恢复安装。
- 未运行：发行 launcher、真实中文键盘/焦点/滚动/取消/重试、宿主 MiniMax 新描述、可信主体真实创建、final 回执/事件/任务回读、进程杀死重开及逐业务写点失败恢复。隔离预检 rc71，进程清点 rc3，不能安全启动/清理 launcher；没有用 `--help` 探测。
- 数据与秘密：所有本轮测试写入均在 `runtime/optimization/2026-10-09/M3/review-r4/`，HOME/app-data/log/cache/TMPDIR 显式重定向。账号表/映射/host-data 只核摘要，未改原业务数据；未读取明文凭据或模型密钥。真实模型请求 **0 次**，未观察付款错误；无联网、上传、公开签名/publish/listing、push、消息或公网部署。
- 程序偏差披露：开场误对项目外 `/Users/abeam/.codex/memories/MEMORY.md` 做一次只读 rg 搜索，违反本次“只允许读写项目内部”约束。此后停止项目外读取；没有项目外写入。不得将本轮表述为零越界读取。该偏差属于审查过程，不伪装成业务候选缺陷。

## 必需检查

以下证据短名均位于 `runtime/optimization/2026-10-09/M3/review-r4/results/`。

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选 / 前置|核三处 candidate、主源/base SHA、差异及 M2 门禁|对象固定、已接受基线可查|r4 对象明确，r3 增量可定位；M2 FAIL|候选定位成立；前置未 PASS|candidate-check、r3-to-r4.diff、gates-before|
|硬1 / D01|现场换排风停转、双空调滴水、位置未知/恶意原文三组，原 request 函数捕获适配参数；追 HTTP body/许可|当前事实和请求绑定随输入发送，发行模型处理三组|适配调用点已存在；事实参数传入后被真实适配函数忽略；manifest 只有 storage|FAIL 核心接线；真实模型 NOT_RUN|vm-probes.request_new_inputs、source-traces、local-store-validation|
|硬2 / D05|合法对照和 OPEN+失败 outcome 投影；追实际 create/confirm/final 路径|只由匹配 final、事件及权威 OPEN 回读成功|源码仅查 task_id/status；局部控制流投影失败 outcome 仍 true；返回 create 的 action_id|FAIL；真实回执/重开 BLOCKED|vm-probes.false_open_outcome、source-traces、M2_REVIEW_r4|
|硬3 / D02/03|回包前只改 TextInput；APPLIED 后改原文再采纳/首次确认；检查同文 no-op|展示/采纳/首次确认分别失效|回包门只读旧 TASK_INPUT；原采纳条件仍 true；首次确认局部投影仍 true。同文 no-op 已改善|FAIL；发行交错 BLOCKED|vm-probes.late_keyboard/adopt_after_edit/first_confirm_after_edit/same_text_noop|
|硬4 / D04|假设备、实际存在的 B 项目空间、非法状态、恶意原文、伪来源；追最终 guard|假事实/越权拒；来源可核；模型不执行|Python 负例拒假ID/跨项目/非法状态，恶意原文不改主体；伪来源仍接受；最终事实 guard 已接入|D04 部分闭合；来源 FAIL；原生 BLOCKED|malicious-contract、source-traces|
|硬4 / 手工|追 NO_SERVICE、设问题、编辑、确认到实际 M2|模型失败可人工合法创建并回读|源码手工入口存在；AI/手工共用 D05，未有权威成功链|BLOCKED 完整手工；D05 FAIL|source-traces、M2_REVIEW_r4|
|硬5 / D07|重新运行强制隔离与进程清点；核审计白名单|真实键盘/取消/重试，秘密不落审计|rc71 / rc3；未启动，无本轮新增窗口；已有残留 UNKNOWN；原文预览旧缺陷未复发|BLOCKED 桌面；D07 已关闭源码范围保留|preflight、source-traces.recordModelMeta|
|D06 时间/歧义|核时间编辑；原 resolved helper 测未选备选及缺设备；确认未解决歧义|只在真实人工解决后可确认并保留记录|时间保留分支已改；自动候选当已解决，space 也被错误解决；缺设备仅有问题文字仍算解决；确认不阻断|FAIL 核心歧义；时间实际宿主未证|vm-probes.ambiguous_resolution/missing_resolution/unresolved_ambiguity_confirm/time_edit|
|本地安装路线|仅 sandbox 打包当前源，离线 keygen/certify/stamp/sign/verify→install_staged→重建；篡改/恢复|只针对当前副本 digest，私钥删除|安装/恢复 rc0，篡改 rc1，三个源文件字节匹配；私钥剩余0|PASS 安装层；不代签运行|local-store-validation|
|受影响 M2 回归|追 create 提前写、confirm 回执和事件提交；对照现存缺陷|一次确认一个权威工单，可对账|提前 saveTasks/成功提示仍在；M2 D03/04/05 仍阻断本链；发行复验未跑|FAIL D05；原生 BLOCKED|source-traces、M2_REVIEW_r4|

### 运行证据的精确边界

1. 初始本地 VM 探针有夹具 `ok` 字段解析错误；随后原 `_g.ok` 访问下合法对照也 false，不能用这批“全拒绝”判守卫 PASS。原始不确定结果保留于 `vm-probes-initial-invalid`、`vm-probes-second-invalid`、`vm-probes-exact-guard-inconclusive`。最终确认控制流探针**仅在测试副本将 `_g.ok` 改为 `_g.good` 并合成 good 守卫结果**，业务源未改；其他确认分支保留。它是隔离的控制流投影，不能称发行原函数端到端反例。D03/D05 判定同时有确定源码分支依据。
2. `adopt_after_edit`、同文 no-op、resolved helper 为抽取的原逻辑；最终日志无错误。`late_keyboard` 的适配/回包均为合成桩，只证明请求入口回包门未读当前 TextInput，不证明真实异步 UI 已重现。三组 request 调用了适配桩，但假结果未形成合法回包，返回 false 不判模型效果 FAIL/PASS。
3. 原时间解析在本地 VM 报 `method index_of not found on string`；不据此推断指定发行 launcher 行为，也不计时间编辑运行 PASS。跨项目/停用 confirm 投影只是给守卫合成拒绝结果，不冒称真实字段守卫已在宿主实测。
4. 独立恶意数据测试运行的是作者 Python 契约，明确不替代 Splash。实际存在的 B 项目空间另在隔离内存中添加，返回 CROSS_PROJECT；不存在的 B ID 子例返回 FABRICATED_FACT。合法对照可解析，伪造来源仍可解析；无任何业务命令调用。
5. 原工作目录 bundle check rc1，未修改原目录。离线安装针对筛出允许文件并重盖 digest 的当前源码副本：digest=`34e91fede1d760bd75c6a510200424884a32aba7daa98bf16221a0517bd5d948`。不是原 manifest 旧 digest 的通过证明。`may_run` 仅 `caps={storage}, hosts={}`，不证明 HTTP 权限。两私钥在 finally 删除，`remaining_key_files=[]`；结束再次核为空。
6. 作者 r3 三次 HTTP 200 是历史独立 Python provider 记录，r4 未重复真实调用；上一轮已指出事实集与应用不同、没有 M2 创建/回读。本轮保留该证据来源，不将其升格为当前宿主 G0-E 或本轮三组真实模型 PASS。r4 Python 的三字段检查确实存在，实际 Splash 没有对应检查；170/170 不能证明实现等价。

### 相关既有验收逐项复核

|用例|本轮结果与范围|
|---|---|
|G0-E|FAIL D01 事实/绑定未发、当前包未授 HTTP；发行 MiniMax/关闭/拒绝/失败 NOT_RUN。|
|T01|FAIL D01/03/06；三组现场新描述仅适配桩；真实提取/追问/未确认到权威状态 BLOCKED。|
|T03|最终事实 guard 接线源码改善；跨项目/停用共享规则可见。真实缺位置/联系人保留与合法手工提交 BLOCKED，不用投影代签。|
|T25|NOT_RUN 完整；Python 假设备、非法状态拒绝，恶意原文不改 actor/no command；实际宿主权限与真实模型行为未测。|
|T26|BLOCKED 完整手工链；NO_SERVICE/设问题入口可见，D05 影响 AI 和人工成功判定。|
|T33|NOT_RUN 真实同义及不同症状效果；三组适配桩调用不算真实模型建议。|
|T34|FAIL D04 伪来源、D06 未解决多设备；真实追问/未知空间/无历史 BLOCKED。|
|T35|FAIL D03 展示/采纳/首次确认；仍只比较回包与旧请求任务版本，不读当前 task/事实/证据版本；发行交错 BLOCKED。|
|T36|NOT_RUN 完整真/假适配器权限；当前安装仅 storage/空 hosts；Python 禁状态/身份字段拒绝局部成立。|
|T37|FAIL D05 成功判定；丢回执/读回超时/原键重试/高版本恢复发行测试 BLOCKED。|
|T38|NOT_RUN 同候选全链复跑；base 差异和当前副本安装可查；历史真实调用不匹配当前 prompt/事实/运行形态。|
|U02|FAIL D03/06；同文 no-op 和时间保留源码改善；真实原话→追问→人工编辑→回读 BLOCKED。|
|U07|BLOCKED 桌面重复点击/丢响应/输入恢复；D05 每次 newId、创建回执与确认回执不匹配未闭合。|
|U08|BLOCKED 真实错误/无权限/过期继续出口；独立 Python 迟到编辑拒绝局部成立，不覆盖宿主失败恢复。|
|U11|BLOCKED 真实输入/滚动/面板稳定；没有本轮宿主截图或按钮证据。|

## 缺陷：沿用原编号，不做无关扩审

### D-M3-01 — P1 / 必修 / 部分闭合：调用点新增，真实请求仍缺事实与宿主许可

- 文件/行：`app/bundle/main.splash:228,245,272,285,296,3275,3319`；`app/bundle/manifest.json:2`；`model_config.json:50`。
- 触发：面板发起任一新描述；检查 `_callMinimaxProvider` 最终 HTTP body 及安装 grants。
- 实际/预期：request 已传 sps/asts，但适配函数完全未使用 spaces_json/assets_json；body 仅 system_text 和用户原话，没有事实列表、联系人白名单及实际 request_id/版本值。提示要求回声，模型没有收到可回声值。manifest/实际 may_run 仍只有 storage、hosts 为空。预期请求使用当前授权事实、绑定值、已验证 HTTP API 和最小目标 host 许可。
- 根因/影响：只接函数调用和另造 Python mock，没有接完整模型输入协议/选定宿主能力，不能证明从真实输入产生可核来源的建议。`env.MM_KEY` 与 secret_ref 的映射亦无实际宿主注入证据。
- 证据：source-traces._callMinimaxProvider/requestAiSuggestion/_modelInstructionText；vm-probes.request_new_inputs；local-store-validation.install_restart_may_run。
- 具体改法：复用 craftModelRequest 或同源结构，将当前授权事实和不可变请求绑定真正写入发送内容；按指定宿主已验证 API 接 HTTP，给当前 digest 最小 http.fetch/host 许可，核只读密钥注入映射。不要继续靠变量改名满足关键词审计。
- 验证：强制隔离的发行宿主内三组新描述真实 MiniMax 总计≤10次，含缺项/多设备；核实际请求、字段来源、回包与失败出口；付款错误立即停止并记录脱敏必要原文。当前授权足够，不需再次问 provider。

### D-M3-02 — 部分闭合；剩余核心并入 D03，真实手工 UI BLOCKED

- 文件/行：main.splash:3243、3262、6220～6262。相同文本 no-op 已实证；request/confirm 入口同步已接。
- 仍未闭合：回包到来、展示到采纳之间没有独立当前输入守卫；真实手工字段编辑和权威创建没有运行证据。无需新增另一个 P1，按 D03/D05 验证。

### D-M3-03 — P1 / 必修 / 未闭合：旧建议仍可采纳，首次确认仍漏失效

- 文件/行：main.splash:2832、2850、2891、3243、3338、3396、3524、3528、6244～6246。
- 触发：请求 A 时 provider 延迟，期间只键入 B；或已 APPLIED(A) 后编辑 B→采纳→第一次确认。
- 实际/预期：回包门 hash 仍取未同步 TASK_INPUT；deliver 自动 apply 改草稿；editRawText 只置 invalidated/active，不改 APPLIED。真实采纳谓词 `!active && APPLIED` 对 B 仍 true；首次确认只有 last_confirmed_at 非零才拒 invalidated。控制流投影中 A 来源/B 原文仍 confirmed=true。预期展示、采纳、执行均对当前输入和上下文重新核验，首次确认也不能把旧建议当新输入建议。
- 根因/影响：按钮前同步修了副作用，没有建立独立建议、显式采纳与具体确认绑定；任务版本仍比请求快照，设备事实/证据版本未接当前值。
- 证据：source-traces；原逻辑 vm-probes.adopt_after_edit；late_keyboard、first_confirm_after_edit 为明确标记的合成控制流投影。
- 具体改法：建议独立保存；展示/采纳/首次确认共用当前 TextInput、request/input/draft/task/project/actor/事实/证据版本与到期守卫。编辑废旧建议；允许用户明确转手工重新确认，不能永久把所有编辑拒掉。
- 验证：回包前、展示后采纳前、采纳后确认前三种交错，各核 UI/草稿/命令/回执；合法未改输入对照必须可继续，旧回包不能覆盖。真实宿主解阻前不声明闭合。

### D-M3-04 — P1 / 必修 / 部分闭合：最终事实 guard 已接，伪来源仍当依据

- 文件/行：main.splash:2714～2728、3089、3501、2910；Python m3_contract.py:386～393。
- 触发：合法候选 ID，sources 填不存在的维修日志/知识条目后解析、展示、确认。
- 实际/预期：来源只查 object/非空，独立 Python 新负例 accepted=true；实际源码相同分支。预期来源绑定存在的事实 ID/版本、可核原文片段或明确 unknown，不能把任意模型字符串当来源。
- 根因/影响：schema 校验替代来源校验，不能完成“有来源”核心目标。最终确认调用 `_validateDraftFacts` 是真实源码改善，不重复要求接线；跨项目/active/services 发行测试仍 BLOCKED。
- 证据：malicious-contract.untraceable_sources、existing_cross_project、fabricated_asset、illegal_status；source-traces.parseModelReturn/_validateDraftFacts/confirmDraftModelBound。
- 具体改法：来源结构用事实/版本引用和原文引用，校验存在性、权限及引用关系；未知明确标 unknown；三入口使用同源当前事实规则，不新增独立事实库。
- 验证：合法可核来源对照通过；不存在/越权/陈旧引用拒或标未知且不能作为确认依据；采纳后撤用/改关系时最终执行拒，无成功事件。

### D-M3-05 — P1 / 必修 / 未闭合：实际 Splash 没有作者声称的三字段检查，也无权威成功协议

- 文件/行：main.splash:3533～3552、3556、3597～3640；Python m3_contract.py:864～878；实施报告 r4:50～54。
- 触发：返回 task_id/OPEN，但 commit_ok=false、confirmed_open=false；确认回执/事件失败；丢响应后再次确认。
- 实际/预期：实际 confirm 仅查 task_id 和 status，随后写 CONFIRM_BIND/关面板；Python 才有 flags 检查。控制流投影 OPEN+双 false 仍 true。create 仍 newId/push/“草稿已创建”/saveTasks 后才 commit，最后按内存 t.status 包装 flags，action_id 是 create receipt，而非 confirm final。预期匹配最终确认动作 final、关联事件和权威 OPEN 回读，未知保持待核验。
- 根因/影响：作者自测实现与候选不等价；增加 outcome 标签不能解决 M2 提交/恢复缺口。AI 和人工路径共同受影响；本轮没有真实失败工单落库证明，报告不声称原生已复现。
- 证据：source-traces.confirmDraftModelBound/createDraftFromPanel/confirmDraft；vm-probes.false_open_outcome（guard 字段适配的控制流投影）；M2_REVIEW_r4 D03/04/05。
- 具体改法：修阻断 M3 的最小创建/确认依赖：持久稳定意图，无提前权威主写或成功；返回实际确认 action_id/final/rejected/needs_verify；网关按回执和权威读回判成功，重试对账原动作、不 newId 重建。仅补 flags 仍不足。
- 验证：AI/人工各跑真实成功与写失败/读回超时/丢响应/重复确认/重开；同意图一任务，未知不成功，任务/final/事件一致；对受影响 M2 依赖做定向复验，不扩修其他挂账。

### D-M3-06 — P1 / 必修 / 部分闭合：时间保留源码改善，歧义被自动当作人工解决

- 文件/行：main.splash:2934～2969、2976～2991、3161～3174、3487～3533、3592～3593。
- 触发：模型有 asset/space 歧义并默认一个备选，用户未选择；或设备定位缺项、asset 为空但 problem 非空，运行 resolved helper 后确认。
- 实际/预期：原 helper 对默认备选把 asset 和 space 都记 resolved，完全不检查人工选择；设备空仍因问题文字存在把“设备定位/具体哪组插座”记 resolved。确认不检查残余 missing/ambiguous，投影中未人工选择仍 confirmed=true。预期只记录真实人工选择/补充，未解决核心定位歧义不得静默提交。
- 根因/影响：自动填值等于已解决，helper 不按字段区分，未与确认守卫连接；报修对象和确认内容不可靠。时间非法保留旧值分支已修改，实际解析在本地 VM index_of 报错，发行可用性未知，不将时间子项作为新的独立 P1。
- 证据：原 helper vm-probes.ambiguous_resolution/missing_resolution；确认控制流投影 unresolved_ambiguity_confirm；source-traces；time_edit.log。
- 具体改法：逐字段维护缺项/歧义和明确用户选择记录，只有相应事实与用户确认成立才 resolved；确认前检查剩余核心歧义；保留合法时间编辑，用目标宿主支持的解析原语。设备尚未识别但空间合法的人工报修是否允许应沿用业务规则，不因作者新增“空 asset 必拒”声明误改旧规则。
- 验证：未选备选/选择有效备选/撤销选择/缺设备三组对照；仅真实解决后提交；重开 task/final/事件及时间/原文/来源一致。

### D-M3-07 — 原关闭源码范围保持；宿主审计 BLOCKED

- 文件/行：main.splash:3441 recordModelMeta、model_config.json audit_keys。
- 审计仍白名单长度/hash，不见旧原文 preview 回归；密钥变量命名不是安全证明。没有读取真实秘密来测试，发行日志/缓存审计未运行，不能扩大已关闭范围。

### 建议 / 挂账

- A-M3-01 / P2：更正 r4 的 flags 已实现、170/170 等价、真实回读 PASS 等证据混用；分别写作者历史 HTTP、Python 契约、源码和发行运行结论。
- A-M3-02 / P2：保留原有效期与失败转手工出口建议；不为美化/优化扩大范围。
- A-M3-03 / P2：更正主源字节数、缺失脚本清单条目及旧 CONTEXT/provider/M2 字段；base SHA 增量本轮已可定位。原包 check 挂账；本地隔离安装路线可行，不要求公开发布。

## 判定

- 最终结论：**FAIL**；精确范围为已交接 M3-r4 的原缺陷闭合与受影响回归。P1 为 D-M3-01、03、04、05、06 的上述剩余核心部分；不是因文档字节数、皮肤或其他建议判 FAIL。
- AI 路径：真实发行模型与人工确认回读未成立；源码有 D01/03/04/06，不能 PASS。人工路径：无模型入口存在，但 D05 阻断权威成功/恢复；未实际创建任何原业务工单。
- 解阻条件：可执行强制项目内写入限制、可靠后台启动/清点/立即关闭指定 launcher 的环境；同 digest 本地安装和最小 HTTP 许可；只读注入已授权 MiniMax；真实可信会话及最小 M2 创建/确认依赖可回读。身份/provider 已裁决，不再列 NEEDS_ABRAM；未观察余额/欠费。
- 本地 catalog/install_staged 已独立验证可行；无需 publish/公开签名/listing。离线私钥已删除。本轮残余修复和环境缺口无需新增 Abram 授权，**NEEDS_ABRAM=no**。
- 前序模块：M2 FAIL 保留，只分析/投影受影响创建链；M0/M1 和 M4–M7 均不修改、不代签 PASS。没有下模块执行。
- 门禁：仅更新 GATES.json M3 status、review_report 和本轮审查字段；旧审查字段归档到该模块 review_history，构建交接字段保留。既有 ACCEPTANCE.json 不改，以本报告/M3 review_acceptance 表达当前形态，保留历史来源。
- 留在本模块：按原编号修剩余核心问题并提供新候选/真实证据；不要重复修已接的 final facts 调用或已关闭的原文审计子项；不开始下一模块。

STATUS=FAIL
NEEDS_ABRAM=no
