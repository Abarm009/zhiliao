# M4 独立 Review r5

**最终结论：FAIL。**原生隔离/回收和当前字节加载通过；应用解析失败，三个场景的业务客户区均空白，核心流程未跑通。上一轮必修 **D-M4-03、D-M4-04 未闭合**。不进入下一模块。

- 审查者 / 日期：本会话唯一独立审查方，2026-10-11（Asia/Shanghai），两段式 r1_1309；未委派子代理、未修业务代码。置信度：摘要、运行日志、空白 UI、隔离回收和源码控制流 **高**；具体解析 token 根因 **中**；未运行业务/真并发结果 **未知**。
- candidate_id：构建交接仍为 `M4-r4-worktree`，base=`M4-r3-worktree`；本次驱动首轮跳过构建并明确重审当前代码，审查固定标识为 `M4-harness-r1-1309-current`。它不是作者新增候选，更不是已接受候选。不能把当前增量称作原 M4-r4 字节。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；未提交工作树。冻结主源 SHA-256=`3e30355262e2a06dcb0216e0847cdb6166e8420fbf6793bf2fbcf31fda4ae23f`，384383 字节、8259 行；M4-r4 原源 SHA-256=`8b3c589a7c360a3a34e9a9d1f6c5e6c104357e3958e073769dbd03ed7ca6800c`。完整差异留存，不按文件修改时间选版本。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r4.md`；清单 `runtime/optimization/2026-10-09/M4/r4/CANDIDATE.json`。作者 43/43 是静态/改写算法证据，不能替代本次独立原生检查。作者没有本轮 harness 请求/证据。
- 前置：M3=`FAIL`，候选 `M3-r5-worktree`，报告 `M3_REVIEW_r6.md`；无已接受 PASS 前置。按用户前序挂账/本次重审裁决继续收证，不修全部 M3，不冒称依赖已通过。只记录确实阻断 M4 的整体解析依赖。
- 宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。由驱动在 agent 沙箱外运行 harness；审查方没有自行启动宿主、VM、sandbox-exec 或 pgrep。
- 运行窗口：2026-10-11 14:48:39–14:49:32 +08:00。三场均 `CLEAN / quit_http / host rc0`，但均不具备业务成功结果。
- 路由/标题：本会话工具未提供实际 Router 路由或 createdAt/标题核验接口；未冒称切换指定型号或设置标题。驱动启动配置不等于实际服务路由证据。
- 已阅读：AGENTS、CONTEXT、00/01/02/M4/04、上一轮 M4 Review、实施/候选/作者证据、相关 T/U 定义、M3-r6、harness schema/实现；仅复核原缺陷及受影响回归。
- 已执行：独立请求准备与结构校验，审阅外部驱动原生结果，481 条证据摘要验证、运行副本/种子/配置核对、全部实际 PNG 查看、完整 host.log/denial 日志审阅、源码增量和门禁末核。
- 未执行：真实登录后的 M3 创建→接单→设备→预约→开工、三真实角色首屏、领域负例实际提交、同盘真正并发、真实模型异步交错、丢响应/逐写点/同盘重开恢复。解析失败导致流程 NOT_RUN；确实缺少白名单测试覆盖的子项另列 BLOCKED，不用旧 rc71/pgrep rc3 判阻塞。

## 证据索引与核验

下文短名：

- **H**=`runtime/optimization/2026-10-09/M4/native-runs/review_r1_1309_REQUEST_review_r1_1309/`。
- **S**=`runtime/optimization/2026-10-09/M4/native/review_r1_1309/`。
- **R**=`runtime/optimization/2026-10-09/M4/native/REQUEST_review_r1_1309.json`。
- **N**=`runtime/optimization/2026-10-09/M4/native/REVIEW_NOTES_r1_1309.md`。
- **A**=S/`native-evidence-audit.json`，由 `audit_phase2.py` 可重复核查，不启动原生进程。

|独立场景|隔离/回收|实际加载|真实业务画面/日志|业务种子|
|---|---|---|---|---|
|empty_intake_login（请求1280×800）|PASS；profile_probes.ok=true；pre/post NONE；pgid_after=[]；CLEAN|冻结主源/模型配置/身份注册与 `.running/*/` 字节一致|FAIL：空白客户区；host.log:46–50 五条 parser 错误|tasks/state/actions/events/accounts 全部未变|
|untrusted_tech_appointment（请求1280×800）|同上 PASS|同上|同上 FAIL|同上|
|untrusted_manager_narrow（请求980×760）|同上 PASS|同上|同上 FAIL；不能据此验窄窗业务布局|同上|

1. **MANIFEST.sha256：481 条，错误0、缺文件0、未列入文件0**；summary 内请求与 R 相同，harness/template 摘要核对一致。每场 profile 摘要、宿主摘要、原 seed 清单、实际 `.running` 副本、capture 记录、host_log_markers 与原文件独立核对。H 自哈希清单不含其自身。
2. 每场请求2张，**实际只存在第二个 `*_after_empty_login.png`**，其 SHA-256 与 result/manifest 均一致；3张初始图不存在且 result 明示 exists=false/sha256=null，未伪造或补图。不能进行初始/操作后两帧对比，也不能仅凭文件名证明空登录回执。
3. 3张实际 PNG 均已查看：只有宿主桌面与“OctoSense Repair”窗口，客户区空白，没有登录、任务、预约表单或错误恢复出口。原 PNG 均为 **2800×1718**；请求 size 是参数证据，不能把截图全屏尺寸当客户区布局实测。技工/经理两图摘要相同，不算两个真实角色首屏通过。
4. 每场 files_written_count=123，列表123项，路径全部限定运行目录且实际存在；主要是 `.running` 代码复制、系统应用、news 缓存、profile、日志和PNG。无 `/apps/octosense-repair/` 业务文件列为本次写入；业务五文件和原种子逐字节一致。**未写不等于权限拒绝通过：应用尚未执行业务。**
5. Seatbelt 明确限制写入场景目录、禁读指定秘密/配置、禁外联，仅本机控制口（本轮无模型代理），并实际探针通过。denial 摘要与日志独立重算匹配；出现远端443、Metal系统缓存及 `/dev/dtracehelper` 的**拒绝**，不是成功外写/外联证据。library_scan 空，原 HOME `.octosense` mtime 前后一致；原始业务盘未操作。
6. host_log_markers 的 launched/eval/remote_listening/remote_quit/panic 字段与原日志一致；没有 panic、rc0只说明宿主正常退出。**各场 host.log:46–50 都有 Expected ) ×3、Expected } not found ×2，内部坐标5187:26/28；eval=384383 bytes，整体源码解析没有成功。**前序 M3-r6 将该坐标关联到 main.splash:5184 的 bitwise 表达式；本轮不另跑修改语法的探针，保留“完整解析失败已实证、具体 token 修法待同宿主验证”的范围。
7. digest=`22d40f461bc44643fdddedfa3ddd532f438f0d16253de475ba4767972479c0f4`。digest_seen_in_seed=true、digest_seen_in_host_log=false；因此使用实际 `.running` 主源/配置/身份/派生manifest字节和 launch-hub 日志证明加载，未用 seed 含digest冒称加载。重用同字节已离线签名 Store；本轮没有重新执行 keygen/sign/install_staged。当前 launch-hub 本地运行路径可行，不需公开发布。
8. model_proxy/model_proxy_stats 均**不存在**，与 R needs_model=false 一致；本轮真实模型请求0，没取得真实模型成功证据，也没有402/余额/欠费错误。本轮未生成私钥；S/signed-store-provenance 保留之前签名私钥删除证据，本轮再核该 keys 目录无 `.key`。不声称本轮重新签名或删除他人密钥。
9. 开始至门禁更新前主源、配置、宿主、harness、GATES、ACCEPTANCE 摘要均未变化；业务测试没有手改运行数据跳过预约。预置 SCHEDULED/CONFIRMED/PROPOSED 仅是未认证反例/投影夹具，**不是由 M3 创建的成功任务**。

## 必需检查

|检查|独立步骤 / 期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/数据一致|冻结当前增量并核运行副本；同字节|current/seed/running/配置/宿主一致，旧r4身份与当前增量明确区分|PASS固定/加载子项；M3前置FAIL|A；S/start-snapshot；M4-r4-to-current.diff|
|原生入口/成功链|UI从真实M3创建到开工，不能预置状态代测|当前源码解析失败，业务客户区空白；不能进入实际创建/接单|**FAIL运行入口；成功链NOT_RUN**|三场图；host.log:38、46–54；A|
|硬1资格/设备服务|合法能绑定、越权/技能/伪造/仅安装位置无服务拒|源码守卫改善保留；没有当前实际提交|NOT_RUN|S/source-traces；UI失败|
|硬2预约|提议不直升、合规确认、过期/改约/跨项目冲突|D02子范围保持；D03仍消费nil spec；没有成功预约/回执|**FAIL源码必修D03；领域原生NOT_RUN**|main:2547–2560；source-traces|
|硬3真正并发|同盘双独立上下文仅一成功，重叠拒/相邻可行|普通读写锁仍有竞争；请求场景顺序独立盘，无法制造真业务竞争|D03源码未闭合；**BLOCKED仅同盘真并发通道**|main:2380–2442；harness run_scenario/seed隔离|
|硬4开工|有效设备+当前承接者+有效确认预约；旧技工拒|原守卫同源保留，未能实际开工|NOT_RUN|startProgress:4843；source-traces|
|硬5桌面真实输入/回执|用户能填写/理解/确认，三角色事实和动作回执一致|无表单、任务或错误出口；D04以版本增长恢复旧内容问题仍在|**FAIL可用UI/D04源码；角色/回执NOT_RUN**|三张图；main:3785、4050|
|改派/改约撤销|旧授权/确认/AI不能直接执行，新内容可正常恢复|清AI标识/改manual改善；确认仍未核完整新绑定|**D04 PARTIAL/未闭合**；真实交错NOT_RUN|main:2213、3785、4088–4105|
|失败恢复|拒绝后spec/锁清理，丢响应/同键/同盘重开可对账|spec清理在多条早退后；无业务命令/恢复实际执行|D03 OPEN；**BLOCKED仅故障/连续同盘重开通道**|main:2446–2620；request.schema|
|隔离/回收|禁外写/秘密/外联、无残留|三场全部符合条件，非ABORT|**PASS；旧B01环境阻塞关闭**|H/result/profile/denials；A|

### 既有用例逐项复核

以下结果严格区分整体入口失败、源码子项、未执行领域结果。NOT_RUN 不能继承作者或历史后端 PASS。

|用例|本次结果与范围|
|---|---|
|T04|BLOCKED：harness顺序独立目录不覆盖同盘双上下文接单；D03源码仍OPEN；本轮无“双业务成功”实测。|
|T05|NOT_RUN：真实技能/权限接单、经理分配身份事件因解析失败未提交；原授权/技能检查可定位。登录文字输入通道另见缺口。|
|T06|NOT_RUN：真实SCHEDULED改派、旧预约释放/ACCEPTED/新承接者/旧技工拒未执行；reassign同源，D04受影响。|
|T07|NOT_RUN：编码/asset载荷等价及伪造/跨项目/归档绑定未提交；原设备守卫保持。|
|T08|NOT_RUN：安装位置相同无服务与合法跨服务空间实际绑定未执行；services规则保持。|
|T09|NOT_RUN：无设备开工、技工处理中换设备拒、经理旧新值理由未实操；startProgress同源。|
|T10|NOT_RUN原生：技工提议不直升/合规确认/越权确认未实操；D03 nil引用仍是P1源码故障。|
|T11|BLOCKED真并发通道；重叠/相邻/跨项目原生提交NOT_RUN；hasTechConflict同源不代验命令边界，D03仍OPEN。|
|T12|NOT_RUN：新确认替代/拒绝新提议保留旧确认未实操；排除同任务和准入后突变的D02源码改善保持。|
|T13|NOT_RUN：预置已过期提议只是夹具，未执行确认，不判410/定时器未运行/伪时间反例通过。|
|T14|NOT_RUN当前原生日期换算/模糊时间核对/非法时窗反馈；D01同源子范围保持。支持中文/表单输入的动作通道BLOCKED。|
|T15|NOT_RUN：旧version实际拒/刷新/不覆盖未执行；spec早退污染源码仍D03，百分比既有规则未扩审。|
|T31|NOT_RUN：真实取消释放预约/留事件/终态拒操作/关联新任务未执行，不用预置夹具代链。|
|T35|D04源码PARTIAL/未闭合；真实生成期间改派/改约及旧回包执行NOT_RUN；受控异步回包通道BLOCKED。|
|U01|FAIL原生入口：首屏无业务信息/动作；三种真实会话“待我处理/下一人”NOT_RUN，磁盘actor不是可信角色。|
|U03|FAIL桌面可用性；同任务三角色事实/权限/不自验NOT_RUN，不以未写数据当授权拒绝通过。|
|U04|FAIL真实UI：当前确认/待改约/过期错误均不可见；具体预约操作NOT_RUN。|
|U05|FAIL真实UI：安装位置/服务空间/依据不可见；实际设备选择NOT_RUN。|
|U07|FAIL当前入口无错误恢复出口；D03/D04仍需修；重复提交/丢响应/离线/同盘重开NOT_RUN，故障通道BLOCKED。|

## 缺陷（沿用编号；不做无关扩审）

### D-M4-03 — P1 / 必修 / OPEN：预约边界丢弃spec，并发与失败清理尚未可靠

- **文件/行**：`app/bundle/main.splash:2547–2560`（spec保存后清空再读nil），`:2446–2533`（早退在清理前），`:2565–2573`（读失败当nil），`:2380–2442`（锁），`:2702`（commitBound）。
- **触发**：合法propose/confirm/reschedule设置非nil spec后进入边界；旧version/权限等早退后再发下一命令；两个上下文先各读空锁，再依次写/读回，各自进入临界区。
- **实际/预期**：当前源码保留 `_cc=STATE.m4_cross_check; STATE.m4_cross_check=nil; let cc=STATE.m4_cross_check`，然后访问cc.tech。预期消费保存的局部spec并拒绝重叠、允许相邻，所有退出清理；实际明确引用nil、早退留全局、读盘错误可走“无冲突”。**本轮真实宿主先整体解析失败，未实际到达此分支，不把旧VM nil日志当本轮原生复现。**
- **并发改善与残留**：相较旧r4增加非空锁检查、写后读回和按actor释放，不能再说当前无条件覆盖/释放。仍缺原子read/claim，且同actor不同上下文当重入、owner只有actor前缀；版本检查是各自本地对象，不构成事务。所列双取得是源码可达交错，不是已发生双业务成功。
- **根因/影响**：spec局部值未消费、清理不覆盖全出口；权威重读/冲突判断/提交间无已验证串行边界。阻断合法预约，不能证明唯一接单/重叠确认成功或失败恢复，属于核心必修。
- **证据**：S/source-traces.runCommandBound/_acquireTaskLock/_releaseTaskLock/commitBound；S/M4-r4-to-current.diff；N；本轮H只证明整体解析FAIL，不能补出预约动态结果。作者行为probe重写冲突循环未覆盖nil接线，锁旧复現不证明当前真事务。
- **具体改法**：入口保存且正确使用局部spec，覆盖授权/幂等/版本/源状态/异常退出清理；坏盘明确拒，不能吞错当无冲突。使用实际宿主可验证的串行事务/互斥边界把授权、读最新事实、跨项目同技工冲突、任务/预约/事件/回执提交包住；owner绑定独立持有实例。若需宿主能力修复，给最小harness复现及可审阅方案，不擅加业务服务。
- **验证**：同候选原生重叠拒/相邻允许/旧版本后下一合法命令、坏盘/写失败清理；两个独立原生上下文同盘同OPEN接单以及同技工跨项目重叠确认仅一个成功，相邻两个成功。权威回读 task/appointment/action/event，并同盘重开检查。不能靠Python改写循环或关键词检查闭合。

### D-M4-04 — P1 / 必修 / PARTIAL：撤销标识改善，版本增长仍代替重新核对内容

- **文件/行**：`main.splash:2213`（失效快照）、`:3785–3821`（编辑）、`:4050`确认、`:4096–4105`版本恢复；最终创建消费旧草稿见`:4139`。
- **触发**：AI问题A已采纳→改派/改约失效→仅将原文改成问题B，不编辑结构化problem、不重新生成或明确核对旧内容，再确认。
- **实际/预期**：current新增清AI请求ID、ai→manual、human_edited_fields.problem及版本++；但该函数未改PENDING_DRAFT.problem，仍可把旧A标为manual/人工已解决，以raw/draft任一版本增长越过失效分支。预期撤销旧建议/确认持续有效，新人工或AI内容经当前主体/项目/任务/输入/事实/到期核对形成新绑定。**未在本轮原生创建错误工单**；源码逻辑未闭合，与旧r4“来源仍ai”的运行观察严格区分。
- **根因/影响**：元数据改名和计数器增长被当成重新确认内容；采纳入口新增守卫没有被最终确认消费，旧结构化问题/来源历史仍可进入创建。撤销失效不可靠，影响核心M3→M4输入/确认安全。
- **证据**：S/source-traces.m4_invalidateConfirmation/editRawText/confirmDraftModelBound，固定主源与完整diff；H整体解析失败导致动态用例NOT_RUN。保留前序清ID与草稿恢复改善，不恢复永久禁人工编辑。
- **具体改法**：分别保存旧proposal失效与新可编辑人工草稿；提供明确转人工/重新请求/核对更新内容入口，重建并验证完整新绑定。只有实际编辑问题等对应字段或明确核对才写human_edited/resolved，不能只改原文自动把旧problem标为人工已解；保留未保存输入。
- **验证**：改派/改约/解绑/撤权后无编辑、只改原文、只改联系人均不能直接执行旧proposal；普通人工初次编辑、关闭重填、明确核对当前内容可继续。真实模型迟到回包与当前输入/任务版本交错实测，核最终任务内容、来源与回执/事件，不以标签变manual代验。

### B-M4-01 — 原隔离环境阻塞关闭；当前核心原生运行FAIL（前序D-M3-01直接依赖）

- **严重性/属性**：P1必修的最小前序依赖；非新增无关扩审。旧r4 sandbox rc71/pgrep rc3理由已被本轮沙箱外harness证据消除。
- **文件/行**：整体 `app/bundle/main.splash`；日志坐标5187:26/28，前序关联点`:5184`（m5_fnv_mix_byte表达式）。不要求顺带修M5其余业务。
- **触发/实际/预期**：R三种全新seed launch-hub同一冻结bundle；三场均五条解析错误和空白客户区。预期能显示登录/任务/表单/错误出口并进入M4；实际只有宿主窗口，无任何M4流程。
- **根因/影响**：当前单文件程序整体不被选定解析器接受；所关联表达式的具体兼容改法仍须最小probe验证。阻断本模块一切正常UI，不是未授权、不足余额或沙箱内预检失败。
- **证据**：三场H/logs/host.log:46–54及frames唯一实际PNG；A.running_copies与main摘要保证当前字节；M3_REVIEW_r6是前序来源，不替代本轮独立原生复现。
- **具体改法/验证**：构建方只修当前解析阻断的最小语法依赖，不扩展M5；在harness里提交同宿主最小语法probe和整体当前bundle复跑，先确认无parser错误且UI实际渲染，再做D03/D04和真实主链。整条主链不得手改状态越过预约。

### D-M4-01 / D-M4-02 / D-M4-05 — 已关闭源码子范围保持；完整原生NOT_RUN

D01日期、D02自身预约排除/准入后修改、D05开工资格/设备/时窗的先前改善保留；本轮同源函数比对不是新原生行为验收。D02受D03接线影响，不重复编缺陷。A-M4-01/02/03保持建议挂账，截图首帧缺失、请求尺寸未实证列为证据限制，不因这些建议单独判FAIL。

## 判定与修复交接

- **最终结论：FAIL**，范围为本次current冻结字节的D03/D04闭合及直接受影响回归。
- 必修：D-M4-03、D-M4-04；先解除B-M4-01当前解析失败这个真正阻断核心的最小前序依赖。无需修完全部前序或后续挂账才做本模块复跑。
- 隔离/回收 **PASS**、本地launch-hub确实加载当前字节 **PASS**、完整业务UI启动 **FAIL**；实际登录/领域命令/权威完成链/模型交错/恢复 **NOT_RUN**。没有本轮ABORT。
- **BLOCKED只用于确实缺少测试覆盖**：选定宿主此前拒绝 `type:`（M2_REVIEW_r5及M2第一轮原日志），没有已验证的中文/登录输入动作；当前schema/实现按序独立盘不覆盖双上下文同盘提交；没有受控延迟AI回包、逐写点/丢响应注入及连续同盘重开入口。解阻需构建/驱动提供合规实际支持动作/覆盖，不可预造SESSION或在agent环境另起launcher。当前解析FAIL不被这些能力缺口免责。
- 前序：M3-r6 FAIL保留；本轮在同摘要上独立重现整体解析问题，不更改M3门禁或扩审其余缺陷。
- 门禁：只改 `docs/optimization/2026-10-09-desktop/GATES.json` M4 status及审查字段，review_report指本报告，旧审查状态/字段完整追加review_history。作者candidate_id/base/implementation_report等原字段保留，review_candidate_id明确为current审查快照。ACCEPTANCE.json未修改，历史后端记录不改写为原生通过。
- **不允许执行下一模块**。修复顺序：最小解析兼容→D03正常预约/清理/真实并发→D04新内容与旧建议解绑→真实UI创建至开工、三角色权威读回和必要失败恢复。仅按清单修复并提交新可定位候选。
- NEEDS_ABRAM=no：身份/provider与离线签名已裁决；本地catalog路径可行，不需公开publish/listing；本轮0真实模型调用、无余额/402/欠费，剩余均为技术/代码/证据缺口。

STATUS=FAIL
NEEDS_ABRAM=no
