# M3 独立 Review r2

最终结论：**FAIL**。正式候选 `M3-r2-worktree` 的 D-M3-01、03、04、05、06 尚未闭合，均涉及本模块核心功能或权限/来源约束；不是因建议项或前序门禁状态单独拒收。D-M3-02 的手工按钮接线已改善，完整原生验证 BLOCKED；D-M3-07 的原文预览泄漏已在本轮复核范围内关闭。没有修业务代码，没有执行 M4。

- 审查者 / 日期：Codex 唯一主审，无子代理；2026-10-10，Asia/Shanghai。置信度：候选字节、源码分支、离线 Store 实际结果高；真实桌面交互及真实模型效果未知。
- candidate_id=`M3-r2-worktree`；base_candidate_id=`M3-r1-worktree`；HEAD=`8d730569546cb57310944bb299695134df773b9d`。依据正式 r2 实施报告、CANDIDATE.json 和 GATES 中交接字段定位，不按文件时间选版本。
- `app/bundle/main.splash` SHA-256=`6cc98e88f03b2ca413c2965baca27f4997aaecf68397182b6235b2fa9166de32`；`model_config.json` SHA-256=`b36ca0561b89cf05de37f49eb5cbb2dc46ef9c9cc1879feee7bfff586de52741`；均匹配清单。审查实际 main.splash 为 **159772 字节、3772 行**，不是清单写的124708字节/3771行；哈希明确，数量误差挂 A-M3-03，不据此判 FAIL。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M3_IMPLEMENTATION_r2.md`。证据根：`runtime/optimization/2026-10-09/M3/review-r2/`；下文简写文件均指该目录 `results/`。
- 开始/结束：`start-snapshot.json`、`end-snapshot.json`、`report-verification.json`记录候选、配置、交接和脚本内容是否一致。从 r1 留存包核对前一主源哈希，生成 `r1-to-r2.diff`；未 reset/stash 或清理他人文件。
- 前置：M2 当前 BLOCKED，`M2_REVIEW_r2.md`；无独立 PASS/已接受 M2 候选。按 Abram 最新前序挂账裁决继续复审 M3，不修改 M2，不假称满足原 PASS 前置。M3 r1 留存源可定位，叠加差异明确；其基础仍为上一轮记录的未接受 M2 修复快照。
- 阅读范围：项目实际 AGENTS.md、现有 CONTEXT_M3.md、r1 Review 缺陷/验收定义、r2 实施报告与候选/作者证据、04_REVIEW模板、M2 前置及被缺陷影响的源码。按用户修复轮效率要求使用 CONTEXT，不再次通读全部基线文档，不做无关扩审。
- 环境 / 路由：本地 macOS；系统提供 GPT-6/Astra 主会话，无法独立确认 Codex Router 路由或切为用户指定 gpt-6.1-sol，不冒称切换。可用工具无当前对话 createdAt/标题修改接口，未猜日期修改标题。主审工具限制不冒充业务运行结果。
- 宿主固定为 M0/r3/host/app-extracted/OctoSense.app；octosense SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，kernel=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`，见 `host-pin.json`。
- 已运行：候选核对/差异定位；独立隔离预检；当前候选离线签名 catalog、官方 Store `install_staged`/Store 重建/`may_run`、篡改拒绝/恢复重试；15 项源码控制流最小语法翻译探针；独立新输入及恶意/跨项目/来源/编辑反例的 Python 契约探针。翻译保存被审函数原分支，依赖显式 stub；**不是 Splash VM、M2 或桌面执行**。没有把重跑作者成功样例作为独立验收。
- 未运行：launcher、真实中文键盘/展示/采纳/取消/重试、真实 provider、实际创建工单与回执/事件/重开、M2 各写点原生失败注入。sandbox-exec true rc71，pgrep rc3，强制隔离与进程回收清点不可验证，所以未启动 launcher、未调用 --help。本轮未产生宿主窗口；既有残留 UNKNOWN，不能声称桌面已清空。
- 隔离：所有测试数据、HOME/app-data/cache/config/tmp、签名与结果都在项目 `runtime/optimization/2026-10-09/M3/review-r2/`；没有读取项目外业务/配置/记忆文件，没有修改原始业务数据。未联网、上传、publish/listing、push、发消息、配置真实 provider 或变更计费。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与前置|核交接ID/哈希、r1留存源、M2门禁|同一固定候选，差异可定位|哈希匹配且生成r1→r2差异；M2无PASS，按用户挂账继续|定位PASS；前置挂账|candidate-check、r1-to-r2.diff|
|硬1 / 更换描述 / D01|新用水泵间灯闪、茶水间两个插座发热、楼层不明焦味，分别提交|真实模型随输入变化，追问和歧义有事实依据|Python均NO_SERVICE、无任务；实际请求函数仍无模型服务调用/回调注册|适配源码FAIL；真实模型NOT_RUN；桌面BLOCKED|fresh-input-attempts、source-traces.requestAiSuggestion|
|硬2 / D05、06|追踪创建初始version0→commitBound(0)，投影nil/DRAFT/OPEN但commit失败三种outcome|只根据M2最终回执和权威回读成功，原文来源可重开|nil/DRAFT已拒；OPEN+commit_ok=false仍通过；正常创建版本不符合commitBound guard；原生未跑|源码FAIL；原生BLOCKED|exact-source-probes、affected-M2-regression、source-traces|
|硬3 / D02、03|取消/主体项目切换/编辑A-B-A；仅键入B未按按钮；当前任务8、回包旧7；AI采纳后改原文再确认|展示和采纳两层失效，确认再核当前内容|取消等六项已拒；仅键入、旧任务版本、编辑后采纳/首次确认仍接受；回包仍自动写草稿|FAIL控制流；原生BLOCKED|exact-source-probes、independent-contract-probes、provenance-ui-audit|
|硬4 / D04|假设备/他项目/停用/空来源/虚构备选/非法状态；手工他项目；恶意原文|所有入口统一校验；恶意原文只作数据；无模型手工合法提交|回包负例已拒；手工他项目仍通过，确认不复核设备有效性/关系；恶意文字可保留但无改身份/状态副作用|权限入口源码FAIL；原生手工BLOCKED|independent-contract-probes、exact-source-probes|
|硬5 / D07|独立launcher预检；合成秘密sentinel审计；核5个审计调用点|真实键盘恢复可用，审计不存秘密|rc71/rc3，未启动；审计白名单已移除preview，sentinel不在离线审计|桌面BLOCKED；D07本轮子范围关闭|preflight、provenance-ui-audit、independent-contract-probes|
|本地catalog/install_staged|隔离keygen/certify/stamp/sign、verify、官方安装/重建/may_run、篡改和重试|当前digest可安装，坏包拒绝，删私钥|安装/重建/恢复rc0，篡改rc1，安装三份源码字节匹配，私钥0|PASS，仅Store层|local-store-validation|
|受影响M2回归|比较7个边界函数并追新面板创建|无绕过、正确提交/失败恢复|7函数去注释后与r1一致；新创建仍直接commitBound且版本错误；真实回归未跑|源码比对PASS；创建FAIL；原生BLOCKED|affected-M2-regression|

本轮 sandbox-only 包 digest=`e723ed4549897c6ff1c70686deecfd40a6db0b6346487299de270d358de962f0`，由当前候选的隔离副本 stamp 后得到，不冒充原 manifest 的旧摘要。`working.key`、`anchor.key`在 finally 中删除，`keys_deleted`记录两路径，`remaining_key_files=[]`，结束再次核对。Store 重建只证明安装恢复，**不证明工单重开**。本地路线可行，无需 AppHub 公开发布授权。

### 原既有验收逐项复核

完整原用例的状态如下；源码/契约子项单独说明，不把子项通过写成原生 PASS。

|用例|本轮范围、变化与证据|完整用例状态|
|---|---|---|
|G0-E|助手真实调用/关闭/拒绝/失败未执行；请求只有no_op或REQUEST_ISSUED|NOT_RUN；适配源码FAIL D01|
|T01|三组新描述离线无任务；原文/缺位置追问的真实模型链不存在|BLOCKED原生；D01/03/06未闭合|
|T03|回包他项目已拒；手工他项目+确认仍通过投影；空空间/缺联系人guard仍有|FAIL源码/契约子项；原生BLOCKED D04|
|T25|非法状态/身份字段回包已拒；恶意原文只存数据，actor不变、未创建任务；完整缺失/矛盾推断未测|NOT_RUN完整；安全子项改善|
|T26|NO_SERVICE明确；设问题按钮已取TextInput；最终手工真实工单仍被创建链阻断|BLOCKED完整；D05核心源码FAIL|
|T33|同义意图/症状地点变化的真实模型未跑；同名createDraft现仅一处|NOT_RUN；同名问题源码关闭|
|T34|虚构主ID/备选与空来源已拒；任意非空伪来源仍通过；歧义已存内存但无解决状态|NOT_RUN完整；D04/06子范围未闭合|
|T35|主体/项目快照拒绝已改善；只比较回包与请求旧task_version，不查当前任务；采纳/确认无完整绑定|FAIL源码 D03；原生BLOCKED|
|T36|非法写字段已拒，恶意文字无身份/任务副作用；真实工具适配/白名单执行未实现|NOT_RUN完整|
|T37|nil/DRAFT拒绝已改善；内存OPEN仍代替最终回执，创建版本漂移；未知恢复/重试未跑|FAIL源码 D05；原生BLOCKED|
|T38|本轮源/配置/脚本/宿主已固定；无真实模型/提示/数据版本可复跑链；Python disk_records是内存列表|NOT_RUN完整；审计子范围改善|
|U02|手工设问题按钮同步已改；键入期间未同步，来源链/时间意图丢失仍在|BLOCKED原生；D03/06源码FAIL|
|U07|实际重复点击/丢响应/重启未跑；创建每次newId；确认只查内存status|BLOCKED原生；D05源码FAIL|
|U08|取消/过期/撤权控制流拒绝有效；完整空/长输入、失败后继续出口未执行|BLOCKED原生；到期转手工仍A02|
|U11|真实宿主输入/滚动/布局稳定未跑；假成功控制流风险仍在|BLOCKED；D05源码FAIL|

## 缺陷

只复核上一轮 D-M3-01～07，未新增无关扩审缺陷。以下行号对应本轮匹配哈希的 `app/bundle/main.splash`。

### D-M3-01 / P1 / 必修 / 未闭合：真实AI请求仍为占位

- 文件/行：`main.splash:1133`、`:1635`、`:1653`、`:1670`；`model_config.json:6`（enabled=false）。
- 触发：任意新描述请求AI；即使绕过disabled分支追后续函数。
- 实际/预期：默认NO_SERVICE；另一分支只绑定请求、标ASKING、写REQUEST_ISSUED并返回，无服务调用/回调注册/超时授权处理，boot未读取配置。预期通过已授权宿主能力得到真实、可追溯建议。
- 根因/影响：离线协议未接真实适配；文档说明缺口并不关闭原P1，本模块AI核心未跑通。不能从本轮证据推断用户实际账户是否已有可用provider。
- 证据：`source-traces.json`、`fresh-input-attempts.json`；作者r2报告§3.1也明确未修。
- 具体改法：实现实际宿主版本支持的单模型请求/回调/取消/超时及配置读取；优先使用现有已授权能力，不自行更换provider或计费。缺授权配置时由Abram裁定，只给清晰缺口。
- 验证方式：隔离原生三组本轮新描述，含缺项追问与多设备歧义；记录实际provider/model/宿主、输入和结果。离线输出另列，不冒充真实模型。

### D-M3-02 / 原P1 / 部分闭合，完整运行BLOCKED：按钮读取已修，键入期间同步未实证

- 文件/行：`main.splash:1621`、`:3253`、`:3256`、`:3289`、`:3295`。
- 实际改善：设为问题/请求/确认/采纳均读取TextInput，旧“必须先请求AI才能设问题”的接线问题关闭；`createDraft`现仅一个定义，固定成功文本分支删除。
- 剩余触发/实际：请求A后只键入B、不点击按钮时TASK_INPUT仍A；旧回复校验可接受。`editRawText`还会在文本相同时无条件递增/失效，不能把按按钮等价于真实编辑。
- 根因/影响：按钮前同步代替编辑同步；剩余必修归入D-M3-03，**不重复增加一条P1**。实际NO_SERVICE→设问题→确认→权威回读因桌面/创建链仍未通过，不能整条标FIXED。
- 证据：`provenance-ui-audit.json`、`exact-source-probes.json`。具体改法/验证：按D03实现展示/采纳前当前TextInput校验；再在NO_SERVICE下完成无需先点AI的真实手工闭环。

### D-M3-03 / P1 / 必修 / 未闭合：展示、采纳、首次确认仍可使用旧输入/旧版本

- 文件/行：`main.splash:1343`、`:1362`、`:1401`、`:1621`、`:1687`、`:1778`、`:3275`。
- 触发：请求A→只键入B→A迟到；回包自动APPLIED后改原文B→采纳/首次确认；任务已8但回复仍回声7。
- 实际/预期：当前任务8的投影仍validate=true；仅键入B的投影亦true。deliver仍直接apply修改草稿。采纳按钮先editRawText（active=false）再只看`!active && AI_STATE==APPLIED`，改B仍“已采纳”；确认在inactive且从未确认过时不核AI原文绑定，也通过。预期展示和采纳分别核当前输入/草稿/主体/项目/事实/任务，旧建议不覆盖、不采纳、不执行。
- 已闭合子项：取消、显式editRawText后的A-B-A、切主体/项目、撤权、到期六项源码投影均拒绝；保留这些修复。
- 根因/影响：回包与草稿仍混在一起；采纳检查的是状态标签；任务只比旧请求快照；确认只防“已有过确认”的编辑，漏首次确认旧AI。事实/证据版本也没有绑定。
- 证据：`exact-source-probes.json`的live_task/keyboard/adopt/confirm_AI四类反例；Python `apply_then_input_edit`也confirmed=true，均不是原生运行。
- 具体改法：将未采纳suggestion与PENDING_DRAFT分开；回包展示前读取当前输入框并按内容变化更新版本；采纳按钮再执行同一完整当前上下文守卫后才改草稿。文本未变不递增/失效。取消/关面板清请求；当前任务版本读取权威当前值。确认核草稿当前版本、AI输入及事实引用，编辑后的首次确认不能沿用旧AI绑定；合法人工重新确认要有出口。
- 验证方式：逐项原生交错，分别在回包前、展示后采纳前、采纳后确认前改输入/事实/主体；检查旧展示不覆盖、草稿/任务/回执不变。再证明未修改输入的合法采纳可用。

### D-M3-04 / P1 / 必修 / 部分闭合：回包守卫改善，手工及最终确认仍只查存在

- 文件/行：`main.splash:1226`、`:1259`、`:1288`、`:1535`、`:1763`、`:1822`。
- 触发：手工edit空间为库内项目B，设备为项目B/停用设备；或合法回包解析后设备撤用/关系变更，再确认；模型用不存在记录名充当sources。
- 实际/预期：新回包主空间/设备项目、active/services、备选存在、空来源、非法status/actor负例已拒。手工编辑和confirm仍只_find存在，Python手工他项目confirmed=true，源码confirm他项目/停用设备投影也true。任意非空`FAKE-EVIDENCE-991`来源仍被接受。预期所有入口使用同一当前项目/有效设备/服务关系及可核来源校验。
- 根因/影响：只加parse守卫；人工入口、最终执行前漏守卫，prompt或UI筛选无法代替授权。非法字段“能进草稿”已被证明，原生跨项目落单未运行，不宣称已发生。
- 证据：`independent-contract-probes.json`的manual_cross_project/untraceable_sources及源码confirm负例。
- 具体改法：抽取共享字段守卫，在回包、编辑、确认三个入口调用；核可信project、空间/设备project、active、服务关系和全部备选；来源用事实ID/原文片段等可核引用，未知标未知，不把非空模型字符串当证据。确认时刷新事实并检查缺项/歧义已解决。保留现有恶意写字段拒绝。
- 验证方式：三入口同样负例都拒、无成功事件；合法同项目通过；撤用后旧草稿拒。恶意原文可保留为数据，本轮接受其文字但actor不变/无任务是正确子项，不列为缺陷。

### D-M3-05 / P1 / 必修 / 未闭合：正常创建版本不匹配，确认仍以内存OPEN代替权威结果

- 文件/行：`main.splash:799`、`:1038`、`:1788`、`:1797`、`:1829`、`:1849`、`:1854`、`:1865`、`:1869`、`:1879`、`:1986`、`:3296`；Python契约`:722`。
- 触发：正常手工/AI确认；创建提交失败；假设创建成功后令确认写盘/读回失败；丢响应/重试。
- 实际/预期：t初始version=0，直接commitBound(t,0)却要求version=1，正常创建进入needs_verify；此前任务已push/save且写create_draft事件。r2确已拒nil/DRAFT且删除无关currentTask版本检查，但confirmDraft先把t.status改OPEN，commit失败只恢复version，外层仍读t.status OPEN返回confirmed_open=true。confirmDraftModelBound只查task_id/status，OPEN+commit_ok=false/confirmed_open=false探针仍true。无最终action匹配/回读检查，create回执ID还被当作确认结果；每次newId/key重新生成。
- 根因/影响：新增outcome包装没有形成执行结果协议，M3直接复制未闭合M2创建路径，未通过runCommandBound创建；AI/手工共用此核心阻断。失败可留下DRAFT/事件、重试再建，或展示假成功。Python disk_records只是内存列表并直接返回OPEN，不是M2回执/磁盘/重启证据。
- 证据：`source-traces.json`、`affected-M2-regression.json`版本guard；`exact-source-probes.json`；作者契约源码。原生各写点注入BLOCKED，未伪造实际工单成功/失败截图。
- 具体改法：只修实际阻断M3的最小M2依赖：创建统一授权/版本/稳定意图边界；初始版本与提交协议一致；创建前不写成功事实。create/confirm均返回final/rejected/needs_verify结构及实际action/task/version；commit失败恢复完整权威事实或进入待核验。外层只凭匹配final回执、确认事件及OPEN权威回读成功；保留草稿/意图键，重试查询原动作。不要仅检查内存status或再加模拟stub。
- 验证方式：空列表/已有选中任务正常创建；真实逐写点失败、丢响应、重启与重复确认；未提交无成功，未知待核验，成功任务/事件/回执一致且重开可读；同意图一个任务/动作。仅回归影响M3的M2路径，不修无关挂账。

### D-M3-06 / P1 / 必修 / 部分闭合：来源字段已新增，原AI输入与时间意图仍未可靠落任务

- 文件/行：`main.splash:1419`、`:1424`、`:1755`、`:1833`、`:1844`、`:1887`；Python契约`:737`。
- 触发：AI基于原文A生成问题，原文改B后首次确认；原文含希望上门时间；工单重开查原话/来源/歧义解决结果。
- 实际/预期：task现在有当前raw_text、ai_sources/请求ID/人工编辑字段，这是改善；但create只存当前TASK_INPUT，**未落草稿保留的ai_history_raw_text/hash/version**，A来源可能与B原文混配；desired_window_start/end未入task；缺项/歧义虽保存数组，但展示/确认无已解决状态。预期重开的工单能核对该AI建议依据的原话及人最终确认的内容和时间意图。
- 根因/影响：内存新增字段未完整接入同一提交与回读；D03交错反例可把来源和当前原文割裂。原生重开未跑；不把字段存在当持久化已通过。
- 证据：`provenance-ui-audit.json`字段表、`source-traces.createDraftFromPanel`、`independent-contract-probes.apply_then_input_edit`。
- 具体改法：在同一版本化任务/命令schema保存最小AI输入快照及最终人工原文/字段来源、时间意图；明确缺项/歧义被人解决的字段。引用已有草稿保留原文，不建第二事实库；与D03/D05一起经权威提交，保留旧数据兼容。
- 验证方式：A→建议→人工修改B→明确重新确认，来源仍能追A且最终内容是B；时间意图重开一致；缺项/歧义未解决不能默默消失；核权威任务而非内存disk_records。

### D-M3-07 / 原P1 / 本轮复核范围关闭：审计不再保存原文预览

- 文件/行：`main.splash:1641`、`:1656`、`:1675`、`:1688`、`:1701`、`:1726`；`model_config.json:27`起audit_keys。
- 实际：审计白名单与5调用点均换为raw_text_hash，无raw_text_preview_safe；_safePreview不再从审计调用；合成`TEST_SENTINEL_ONLY_991`不出现在离线审计。预期原文不进审计已满足本轮源码/契约复核，不再列必修。
- 证据：`provenance-ui-audit.json`、`source-traces.recordModelMeta`、`independent-contract-probes.manual_secret_audit`。真实宿主落盘审计仍BLOCKED，已明确范围；8位FNV hash不声称密码学不可逆或匿名化证明。

### 建议挂账（不因建议判FAIL）

- **A-M3-01 / P2 / 保留**：r2映射已按原T/U定义改善，但仍将Python内存确认等同M2成功并标完整PASS；按本报告分层修正。作者证据逐文件哈希见author-evidence-inventory，不以作者声称代替运行。
- **A-M3-02 / P2 / 保留**：约11秒草稿deadline/到期转手工出口、焦点/滚动/视口后续补；不做皮肤扩审。
- **A-M3-03 / P2 / 保留**：实际基线仍未接受M2；清单字节/行数不准确，补完整bundle/宿主/脚本与模型提示版本。两源码哈希匹配，足够定位本轮，数量/文风不单独判FAIL。

## 判定

- 最终结论：**FAIL**；精确范围为正式M3-r2-worktree对上一轮D01～07的独立复审。已有核心/安全P1，因此不能PASS；原生运行条件另为BLOCKED，真实模型NOT_RUN。
- 必修项：D-M3-01、03、04、05、06。优先D05打通纯手工一次确认→M2 final→权威OPEN回读；D03/04/06守住输入、权限和来源；再以已授权真实模型闭合D01。D02键入失效余项合并D03；D07本轮关闭，不重复修。
- 解阻条件：提供项目内可强制隔离且可清点回收launcher的执行环境，后台启动、finally终止并核无残留；接通已授权模型能力，确需真实provider配置由Abram裁定；明确可信业务身份来源（M2继承授权缺口）。只处理实际阻断本模块的M2创建/结果问题，不扩修前序全部缺陷。
- 本地catalog/install_staged本轮PASS，仅安装Store层。无需公开签名/publish/listing授权；本轮两份离线私钥已删。执行环境、源码修复、离线签名不算NEEDS_ABRAM。
- 受影响前序模块：7个M2边界函数去注释后同r1，原生回归BLOCKED；本轮创建接线仍失败。M0/M1/M2门禁与历史不改。
- 门禁/台账：只改GATES.json的M3 status及审查字段；更新前的M3审查状态存review_history，原candidate/base/实施字段保留。ACCEPTANCE.json不改，本轮不以未跑原生覆盖历史来源。逐硬验收/T/U结论写入M3 review字段。
- 是否允许下一模块：**否**；不执行M4，不给下一模块入口。
- NEEDS_ABRAM=yes仅指尚待裁定的真实provider配置和可信业务身份来源。若已有授权能力，构建方应在隔离宿主接通并给证据；当前报告不配置/更换它。其余修复和环境问题不需新增Abram授权。

STATUS=FAIL
NEEDS_ABRAM=yes
