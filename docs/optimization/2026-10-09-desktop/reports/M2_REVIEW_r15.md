# M2 独立 Review r15

**最终结论：NOT_RUN。** 本轮 r2_1054 未取得专修新候选，未生成可执行请求；驱动本次明确提供「无：未写请求或无新请求」。没有本轮原生运行证据，不能裁定原生 PASS 或运行 FAIL，也不能把它说成 harness ABORT。五项原 P1 不关闭，旧 `M2-r10-worktree` 的 r13 FAIL 保留历史适用范围。

## 审查范围、候选与环境

- 审查者/日期：本主会话唯一独立审查方，2026-10-13T12:30:49.957218+08:00；按 04 模板作修复复审，仅原 D01/02/03/05/07 及受影响回归，没有业务改动或下一模块执行。
- 本轮受审 candidate_id/base、包 digest：**未交接，均为 null**。登记候选仍 M2-r10-worktree/base M2-r9-worktree；作者报告仍 `reports/M2_IMPLEMENTATION_r10.md`，不能把旧登记或文件时间当新交接。
- HEAD：8d730569546cb57310944bb299695134df773b9d，存在未提交变化。已核旧快照/catalog 对应旧 r10；当前 main 757315 B / SHA256 `9869f8adfb4de00a48858851f47dfc87e51e29a54479999ad902026b356898db`。它是**未交接工作树观察源码**，不是正式新候选。
- 第1段笔记：`runtime/optimization/2026-10-09/M2/native/REVIEW_NOTES_r2_1054.md`。观察证据 E=`runtime/optimization/2026-10-09/M2/native/review_r2_1054/`，包含 source.main.splash、观察 diff、phase1-inputs、verification；新增 native-evidence-audit-r15.json 与 GATES.before-r15.json。
- 前后源码、manifest、ACCEPTANCE、harness/schema/profile、构建日志及更新前 GATES 全部与第1段摘要相同。具体摘要在 E/phase1-inputs.json 与 E/native-evidence-audit-r15.json。结束核验另写 E/final-verification-r15.json。
- M1：仍 FAIL/M1-r2-worktree/M1_REVIEW_r2.md，不满足原文 PASS 前置；依用户挂账裁决仅继续 M2 局部复审，不改前序结论。受影响 M1 原生回归 NOT_RUN。
- 运行环境：只做本项目文件/证据核查，未启动 launcher/harness，未做 sandbox-exec 或 pgrep 预检。固定宿主路径见 r10 报告；本轮宿主运行版本/摘要与新候选一致性 **NOT_RUN**，没有实际运行包可核。
- 主会话显示 Astra；未能确认/切换 Router/gpt-6.1-sol，不冒称满足指定路由。当前线程 createdAt/改标题能力未取得，不猜日期改标题。没有子代理。
- 已读范围：AGENTS、CONTEXT_M2、00/01/02/M2/04、r14/r13 原缺陷、r10 报告/清单/catalog、HARDFIX_PLAN、本次构建日志、相关源码、harness/schema；第2段重新核候选目录/摘要/控制字段/调用关系。项目外 memory/skills、明文凭据及 provider secret 未读取。
- 实际已运行：只读定位、SHA 核对及报告/门禁一致性核验；认证操作、原生场景、注入故障、真竞争、模型请求均无本轮执行证据。

## 必需检查

|检查|独立操作与期望|实际|结果|证据|
|---|---|---|---|---|
|版本定位|新 candidate/base、冻结清单/diff/digest、同签名 Store、冷开证据应齐全|r10 旧包与当前工作树不同；新交接仍缺|NOT_RUN 新候选验收|E/phase1-inputs、旧 r10 清单/catalog、构建日志|
|观察源码一致性|两段及写报告前源码同一摘要|757315 B/9869f8ad…，一致|PASS，仅观察证据关联|E/source.main.splash、native-evidence-audit-r15|
|真实 UI/业务加载|同新包冷开日志错误0并有 PNG|无本轮请求/log/PNG|NOT_RUN|驱动本次“无”；E/native-evidence-audit-r15|
|硬1|认证真实按钮正常/跨状态重放、异参拒绝、新意图、v9 查 v1，完整原 action/result|未运行，源码仍见 D02 caller 缺口|NOT_RUN|D02、阶段笔记|
|硬2|版本/越权/撤权/到期拒绝；同盘真正竞争唯一赢家|权限未运行；白名单无双上下文同步竞争|NOT_RUN 权限；BLOCKED 竞争|D05、harness:859–869 串行 fresh 场景、schema|
|硬3|逐写点失败、同盘重开，任务/回执/事件完整一次|未运行，现 schema 无这些控制；实际提交仍旧路径|BLOCKED 控制范围；不宣称动态 FAIL|D03、schema|
|硬4|成功但读回失败/丢响应后待核验，原动作查询不重做|无精确故障控制，无认证查询证据|BLOCKED 故障控制；NOT_RUN 查询|D02/03、schema|
|硬5|实际重复/超时/重开输入身份保持、严格迁移保源|冷恢复/迁移没有运行；fresh seed 不能代连续重开|NOT_RUN 冷恢复/UI；BLOCKED 连续重开|D01/07、schema|

## 原生证据逐项核查

本轮 `REQUEST_review_r2_1054.json` 不存在；预期关联目录 `M2/native-runs/review_r2_1054_REQUEST_review_r2_1054/` 不存在。目录中仅有上一轮 r1_1054 的历史 ABORT 记录，**不作为本轮证据**。这不是本轮 harness 返回 ABORT，harness_verdict=null、harness_aborted=false。

|用户指定字段/文件|本轮实际核查|判定|
|---|---|---|
|summary.json、各 result.json|没有本轮文件或场景|NOT_RUN|
|profile_probes.ok、pre_pgrep/post_pgrep、pgid_members_after、verdict|无 result；实际值未知，不能填 true/NONE/空数组/CLEAN|NOT_RUN|
|captures 及 SHA256、frames/*.png|无本轮截图可查看或核摘要；没有“业务区可渲染”结论|NOT_RUN|
|files_written_in_run_dir、sandbox_denials|无本轮字段/盘面/拒绝日志，不宣称没有越界或全部盘写成功|NOT_RUN|
|host_log_markers、logs/host.log|无本轮日志，错误数未知，不写“解析0”|NOT_RUN|
|model_proxy_stats|无代理统计；本审查未请求模型，不能代填驱动代理成功/0请求统计|NOT_RUN|
|MANIFEST.sha256|无本轮 manifest，不宣称全文件核验通过|NOT_RUN|

没有证据本身按 NOT_RUN 记录；仅真正超出现有白名单/schema 的同盘竞争、精确失败/丢响应和连续同盘重开记 BLOCKED。未引用 Codex 沙箱 rc71/rc3 作为原因。隔离/回收五指标和 CLEAN 尚未验证；旧截图、作者 PASS、冷夹具历史均不代签业务执行。

## 缺陷

下列均沿用原 P1/必需编号，不是新增无关扩审。行号指 E/source.main.splash；当前 app/bundle/main.splash 摘要相同。源码改善与残余根因如实区分，没有新候选动态 FAIL 或关闭结论。


### D-M2-01：源码有实质改善；原生关闭证据 NOT_RUN

- 文件/行：`source.main.splash:894–925` 严格全消费解码；`:982–1025` view schema；`:1207–1250` 保源；`:2006–2070` 真实 loadViewState 接线。
- 实际：loadViewState 已使用 `hf_parse_json(text, "view_state")`；损坏时走 `hf_preserve_source`，旧副本逐字相等才复用，不同副本不覆写，写后独立读回，保源失败保持冻结。此前“仅宽容 parse 加首尾括号”的根因已在这个消费点改动，不能继续照抄 r14 说这里仍未接严格 decoder。
- 未验证：严格 decoder 在固定宿主的真实语义、合法中文/转义/emoji 及持久意图恢复、坏源/旧副本保全、槽满/目录失败、UI 提示。新增 confirm_intent schema 不得误拒合法已保存意图。
- 原缺陷影响：恢复可能丢用户唯一来源和原意图；仅源码改善不能关闭。
- 具体改法/验证：保留已接线改善；冻结候选后跑下表独立正反例，逐字核主源及每个旧副本、原输入/意图/key、冻结状态与截图。若有效输入被新 schema 拒绝，修兼容映射，不能清空意图规避。

### D-M2-02：原结果和真实按钮接线仍未收口

- 文件/行及链：`:14379–14397` 确认按钮 → editRawText → `confirmDraftModelBound :8845` → `createDraftFromPanel :9148` → `confirmDraft :9840` → `commitBound :6785` / 外层 logEvent → 权威核对与 UI。
- 实际：`:9091–9118` 有内容路径仍要求 confirmed_open 和当前 OPEN；`:9802–9837` 历史 helper 返回 confirmed/action_id/reason，按 task_id 找 final，未返回完整 original_result，也未用原 actor/key/fp/action_id 精确绑定选择回执。`:1833–1862` 新 outcome/query helper 已定义，但全文件搜索只见定义，没有接入这条按钮链。
- 触发/预期：原操作已成功、任务推进到 ACCEPTED/v9 后，原键有内容/空内容重试应返回同 action_id 和完整原结果；最新状态另读。任何占键状态同键异参须拒绝；unknown 保键且不成功。
- 根因/影响：新 helper 尚未消费；历史与当前状态仍混在旧协议中，不能证明原操作一次性结果。
- 具体改法：M2 的创建/确认/原动作查询统一返回结构化 outcome，精确匹配原动作；正常及空内容按钮消费同一成功/未知判据，最新状态独立显示。只做必要数据/反馈接线，不改布局。
- 验证：真实可信登录后的两分支正常重试、跨状态重放、全部占键状态异参、v9 查原 v1、新独立意图；核任务/回执/事件写次数、完整原结果、UI。动态 NOT_RUN，不能称本段已复现假成功。

### D-M2-03：新增协议未接实际提交；恢复标记校验不足

- 文件/行：`:1429–1789` 新事务/投影恢复 helper；`:6785–6997` 真实 commitBound；`:7009` 起旧 boot 对账；`:9840–9895` 确认及外层事件。
- 实际：commitBound 仍普通 tmp → 主文件 write → 清 tmp → readback → final；确认后另写 logEvent。全文件搜索中 hf_bind_commit_spec、hf_recover_commits 只有定义；没有真实生产 caller 或启动恢复调用。新增索引/prepare/commit 相关代码存在，不等于已有共同提交决定。
- 同编号内需核对的新增恢复风险：`:1706–1711` 只要 applied 文件能严格解码，就 `_applied=true`；`{}`、`null` 或别的 tx_id 的合法 JSON 不能证明投影完整。`:1760–1764` applied 写返回 published 而未 verified 时仍可计入 done。此处是源码风险，尚无原生失败复现。
- 触发/预期：主写后 final 前、事件/降级回执/清理/读回/响应失败及同盘重开；完整原 action/task/event 恢复为一套，不重做、不假成功。applied 必须与本事务及完整权威投影核对，不能仅因语法合法跳过恢复。
- 根因/影响：新恢复协议与旧业务 writer 并存，仍有部分提交窗口；弱 applied 判据可能错误解除恢复屏障。
- 具体改法：先接完整 before/after/action/event 和持久提交决定，命令/恢复共用 guard；实际 M2 caller 和启动/每次命令前屏障必须消费返回。applied 校验 schema、tx_id、决定绑定及投影完整性；未 verified 保持 unknown。发布失败不能直接声称磁盘未改变。
- 验证：真正逐写点故障、读回失败、丢响应、同 Store 连续重开；另测 applied={}、null、错 tx_id 和投影缺失。当前 schema 无精确控制，动态 BLOCKED；冷 seed 仅可验证恢复输入拒信，不能代中途失败。

### D-M2-05：仍无真实原子竞争边界

- 文件/行：`:1254–1259` capabilities；`:1261–1347` 单文件 writer；`:6371` 起锁；`:6785` 起实际提交。
- 实际：HF_CAPS 明写 atomic_replace=false、durable_sync=false、held_lock=false；单文件发布仍 fs.write。旧锁仍 read → write stamp → read verify，再提交前核 token/版本。此能力记录是当前源码声明，不是本段独立宿主原语探测。
- 触发/预期：两个独立认证上下文同时读取无锁、竞争同一 Store/version；应有持有期原子 guard/CAS/发布边界，唯一赢家且其它提交不丢。
- 根因/影响：两个 writer 可在各自读回后继续，提交前普通复核不构成原子线性化点。新增函数名不能改善这个保证。
- 具体改法/验证：提供真实受限宿主原子能力或在交付形态上确实排除所有第二 writer 的可核验机制；提交/恢复统一使用。驱动提供同盘双认证上下文及同步屏障，证明一个提交、一个拒绝、完整事实，无迟到覆盖。不得用线程模拟、不同 Store 或串行重复关账。原生 BLOCKED。

### D-M2-07：严格语法读取已接；schema/迁移其它消费者尚待复核

- 文件/行：`:894–925` 严格解码；`:932–962` action schema；`:1107–1157` history；`:2535` 旧判据及迁移消费者；`:2581–2608` loadJsonlLines。
- 实际：loadJsonlLines 已整份严格 parse/schema，失败不返回可写的部分记录，保源诊断复用 hf_preserve_source。认可该改动；不继续说这个入口只查括号。
- 仍见源码缺口：action schema 只必需非空 action_id；status 可缺，final 的 result 仅要求非 nil，actor/key/command/task/fp/version 和完整 result 类型尚未成立。合法语法的 `{"action_id":"review-incomplete"}`、`{"action_id":"review-final","status":"final","result":false}` 会走到 schema 的 true 路径，不能因此成为可信业务完成历史。合法旧事件/回执需要明确兼容映射，不能一律拒旧数据或允许半条成功事实。
- 触发/预期：闭合缺值、尾随垃圾、重复键、合法语法但缺身份/动作/结果绑定；整份拒信并保来源，不归一化为可写权威历史。完整旧历史正常迁移且字段不丢。
- 根因/影响：语法闸已增强，业务记录 schema 尚不足；旧迁移/备份路径必须使用同一判据。动态 NOT_RUN。
- 具体改法/验证：统一主/备份/迁移/恢复的严格 decoder 和版本化记录 schema；区分兼容读取与可作为成功证明的记录，成功证明需精确完整绑定；跑下面正反例核来源和 UI，不用手造历史证明真实执行成功。

D-M2-04/06 保持原轮根因认可，本段无新动态结论。建议 A-M2-r13-01 不升级为 P1。本段只复核五个原缺陷及其受影响路径，不扩审其它模块。


## 既有验收映射

|验收|本轮实际范围/状态|
|---|---|
|G0-B|NOT_RUN：无本轮可信认证及权限操作证据；身份来源已裁决|
|G0-C|NOT_RUN：无本轮新候选权威盘/迁移/保源运行；逐点恢复另有控制 BLOCKED|
|T02|NOT_RUN：创建、重试、同键冲突、新独立意图未运行|
|T04|BLOCKED：白名单/schema 无同 Store 双独立认证上下文及同步竞争控制；非串行替代|
|T15|NOT_RUN：旧版本拒绝、刷新、原输入与 task_id 保持未运行|
|T16|BLOCKED：白名单/schema 无精确响应丢失控制；原动作查询未运行|
|T17|NOT_RUN：断连/重连后的权威回读未运行|
|T18|NOT_RUN：受影响查询/列表/事件/附件权限回归未运行|
|T22|BLOCKED：白名单/schema 无逐业务写点故障及同盘连续重开控制|
|T24|NOT_RUN：旧入口绕过及新旧 writer 边界未动态回归；D06 旧根因认可保留|
|T29|NOT_RUN：撤权/到期/退出/共享卡片生命周期未运行|
|T32|NOT_RUN：配对/一次消费/poll_secret/approval/token 边界未运行|
|T37|NOT_RUN：精确原 action/result、跨状态及较新版本查询未运行|
|U03|NOT_RUN：独立主体同任务事实/权限与自验收拒绝未运行|
|U07|NOT_RUN：真实重复按钮/未知/输入保持未运行；连续同盘重开控制 BLOCKED|
|U08|NOT_RUN：没有本轮真实失败/恢复截图|
|T28|NOT_RUN：没有本轮新候选原生打开/操作/回读证据；同盘重开控制 BLOCKED|

## 判定与交接

- **最终结论：NOT_RUN**，仅适用本次未交接新候选、没有独立运行的 r2_1054 审查。本次不把未交接观察源码当正式候选判 PASS/FAIL。源码残余问题详列供构建方逐项收口。
- 必修原编号仍开放：D-M2-01/02/03/05/07；D01 与 D07 的严格语法/保源接线改善认可，但缺独立原生关闭证据；D02/03/05 的实际调用/原子能力仍未闭合。D04/06 旧根因认可保留，建议不升级 P1。
- 补测先交新 candidate/base、报告、冻结源码/资源清单和 diff/digest、同签名本地 install_staged Store（必须 apps/catalog.json）、离线私钥删除证据、新候选 harness 冷开 log 和截图。第一段审查没有把缺 seed 的假请求交驱动；这也意味着本轮指定 REQUEST 未完成，不能归咎为本轮 harness ABORT。
- 再由审查方准备阶段笔记中的独立正反例、真实 seed/mirror，验证后交可执行 REQUEST。D02 需符合本轮输入限制的可信真实操作记录；D03/05 需驱动受限精确失败/丢响应/连续同盘重开/双独立主体竞争控制。不能靠所有冷场通过来替代这些核心检查。
- GATES.json **仅更新 M2 status 与 review_* 字段**，本轮 status=NOT_RUN、review_report 指向本报告、review_candidate_id=null；登记的作者 candidate/base/report/build 字段保持。更新前审查字段/状态保存在 review_history，完整前态 E/GATES.before-r15.json。旧 M2-r10/r13 FAIL 仍可定位，r14 ABORT 保留历史且本轮字段不再继承。
- ACCEPTANCE.json 未改：没有新运行结果可更新原验收；不删改原 P0/38业务/12UI。
- **不允许下一模块**，不提供或执行下一模块入口。
- G0-E：**延期缺口（Abram 已裁决，M3 到期）**，不作为 M2 未执行/阻断原因。身份/provider/隔离离线签名已授权；无余额/402/欠费错误，无公开发布需求。NEEDS_ABRAM=no。
- 置信度：版本/证据缺失、源码观察与控制边界高；新候选原生/UI/权限/恢复/竞争未知。

STATUS=NOT_RUN
NEEDS_ABRAM=no
