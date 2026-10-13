# M4 独立 Review r2

最终结论：**FAIL**。正式候选 `M4-r2-worktree` 的 D-M4-02、03、04、05 尚有核心流程或授权问题。本轮只复核 r1 缺陷及受影响回归，不因建议项或前序模块结论单独拒收，不修业务代码，不执行下一模块。置信度：候选字节、源码分支和双进程文件锁反例高；原生桌面行为未知。

- 审查者 / 日期：当前 Codex 主会话，唯一审查方，无子代理；2026-10-10，Asia/Shanghai，具体时间见 `review-metadata.json`。
- candidate_id：`M4-r2-worktree`；base_candidate_id：`M4-r1-worktree`；清单 HEAD 为 `WORKTREE-UNCOMMITTED`，实际 Git HEAD 为 `8d730569546cb57310944bb299695134df773b9d`。依据正式 r2 实施报告、CANDIDATE 和 GATES 交接字段定位，不依据文件时间。
- 被审主源 SHA-256：`c656536119ff0983394bc10f65578095508ca3643e9a538ba8e82b415beab545`；r1 留存主源 SHA-256：`02220afb7ea3ba66a9247f40694766955e8827c79dbb414142380fb22d065eee`，均匹配交接摘要。实测 **206814 字节、4619 splitlines 行**；清单的210162字节/4618行不准确，列入已有 A-M4-01 建议，不单独判 FAIL。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r2.md`；上一轮审查：`reports/M4_REVIEW_r1.md`。
- 快照：`candidate-check.json` 固定主源、manifest、身份/模型配置、宿主及作者脚本/证据摘要；`M4-r1-to-M4-r2.diff` 留存新增差异；结束核验见 `final-verification.json`。未覆盖作者 evidence。
- 前置：M3 独立 Review r2 为 FAIL，没有已接受 PASS 候选。遵照本次前序挂账裁决继续复审 M4，仅检查实际影响本模块的创建、确认、锁、资格守卫；M0–M3 门禁不改，不宣称满足原 M3 PASS 前置。
- 环境 / 路由 / 宿主：指定 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`，宿主二进制摘要见快照。工具无法确认或切换主会话 Router / gpt-6.1-sol，也没有当前会话 createdAt 和标题修改接口；未冒称模型切换或猜日期改标题。
- 已阅读：实际 AGENTS、既有 CONTEXT_M4、00/01/02、M4 指令、04模板、r1 Review、r2实施/清单/全部作者证据与3脚本、M3 r2 Review及相关当前源码、原业务/UI用例定义。未重复展开无关前序源码或后续模块。
- 证据根：`runtime/optimization/2026-10-09/M4/review-r2/`；下文 JSON、翻译文件、diff 均在其 `results/`。独立脚本放证据根，不属于业务实现修改。运行环境通过 `review_common.py` 将 HOME、CFFIXED_USER_HOME、TMPDIR、XDG缓存/配置/数据、OctoSense app-data 和 Metal缓存导向本轮隔离目录；合成文件和签名测试仅在此目录。
- 执行偏差：首条命令误读项目外记忆索引，违反本次读取边界，已在 commentary 明确披露。没有写项目外文件；后续显式文件内容读取限定项目内。本报告结论取自本轮项目证据，不能宣称整轮完全没有越界读取。
- 已运行：当前候选隔离离线签名/官方 Store安装与恢复/篡改拒绝；实际源码选定函数的独立翻译探针；两个独立OS子进程的文件锁反例；隔离/进程清点预检。无联网、上传、publish/listing、push、Issue/评论、消息、部署或真实provider配置。
- 未运行：原生M3创建到开工、三角色屏幕与键鼠输入、真正业务接单/确认并发、权威任务/事件/回执和失败/重启恢复。隔离预检rc71、进程清点rc3，不能保证宿主隔离与回收，故没有启动launcher，不调用 `--help`。本轮没有新增宿主窗口；前序残留窗口 **UNKNOWN**，不能声称桌面清空。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、宿主与差异|解析正式r2清单，计算源码/配置/宿主摘要，对r1留存源生成diff|审查唯一交接候选且无漂移|候选和base摘要匹配；数量错误列建议|定位通过|candidate-check、M4-r1-to-M4-r2.diff、final-verification|
|D-M4-01 时区与合法日期|翻译实际日期计算函数，与标准datetime UTC+8独立对照；非法年月日反例|日期真正进入UTC毫秒；非法日期拒绝|次日、年底、闰日、上海00:00一致；11/31、2/30、非闰年2/29拒绝|日期算术/校验子范围关闭；原生BLOCKED|source-probes、相应translated.py|
|D-M4-02 命令与改约|执行实际sourceOk/冲突函数；执行改约到命令准入前的原分支|新命令合法；旧确认待新决定；准入失败旧提议不变|新命令白名单、旧PROPOSED精确排除已修；旧CONFIRMED重叠仍自冲突；旧PROPOSED仍提前SUPERSEDED|FAIL核心子范围；原生BLOCKED|source-probes、rescheduleAppointmentFromForm-translated.py|
|D-M4-03 连续提交/真并发|两个独立PID先读空锁，A写入读回后保持临界区，B再写入读回；检查创建自增/冲突位置|互斥且正确释放；创建符合版本协议|两PID都acquired=true；A释放清掉B锁；释放后顺序再获锁已修；创建自增已修；预约冲突仍在锁前只读内存|FAIL锁算法；原生接单/确认BLOCKED|concurrency、concurrency_probe.py、affected-regression|
|D-M4-04 旧确认/AI|执行实际失效函数，分别设last_confirmed=0和非零；执行实际确认前导守卫|已采纳和未确认旧建议均拒绝；新内容可重新核对|APPLIED→EXPIRED与新增调用成立；last_confirmed=0时不标失效，确认前导守卫仍通过；非零时拒绝，但普通编辑仍无重新确认出口|FAIL安全子范围；原生BLOCKED|source-probes、m4_invalidateConfirmation-source.txt、confirmDraftModelBound-translated.py|
|D-M4-05 当前有效设备/资格|独立翻译开工前导守卫，新归档/跨项目/撤服务/撤技工角色/撤技能反例|执行时设备和当前承接者资格均有效|设备新增守卫正确拒绝；相同assignee id但撤角色/技能仍通过|设备部分关闭；资格部分FAIL；原生BLOCKED|guard-probes、startProgress-guards-translated.py|
|三角色首屏与错误出口|对mainAction/secondaryActions作r1→r2比较，追详情与确认入口；隔离预检|真实屏幕可理解，错误可恢复，回执与事实一致|两个角色动作函数与r1相同；预约详情仍走apptLine简短状态，formatApptLine无调用；没有本轮屏幕/键鼠/回执|BLOCKED原生；已有A02继续建议挂账|affected-regression、源码3065/3109/3888、preflight|
|本地catalog/install_staged|本候选隔离副本keygen/certify/stamp/sign/verify；官方Store安装→重建→may_run；篡改→恢复；finally删私钥|本地路线可行，篡改拒绝，无需公开发布|安装rc0；篡改rc1；恢复rc0；三份主源安装字节匹配；私钥0|PASS，仅Store层|local-store-validation、local_store.py|
|前序受影响回归|比对创建、确认、边界、锁、开工及角色动作函数|只修实际依赖，旧结论不冒充新验收|创建和锁改动可定位；runCommandBound/commitBound/confirmDraftModelBound/confirmDraft及两角色动作函数未改；相应问题仍存在|源码回归完成；原生BLOCKED|affected-regression|

探针是选定实际源码分支的Python翻译，角色、时钟、注册表及持久化依赖显式stub；前导守卫的“通过”仅表示到达提交前，**不表示业务命令成功**。双进程实验是真并发文件I/O与锁步骤反例，**不是原生双接单/双确认**；失败足以推翻锁算法互斥声明，不能据此代签完整T04/T11。未改系统时间，未手改业务状态推进成功链。

离线测试包digest=`f83b173f7ea577089cd90adfead81e6e02c1ea4a5b1c73808627a6ef9b74e9de`，来自当前源码隔离副本stamp，不冒充原manifest旧digest。`store-test/keys/working.key`、`anchor.key`在finally删除，`keys_deleted`和`remaining_key_files=[]`记录删除，结束再核验。Store重建只证明安装恢复，不证明工单恢复。本地路线成立，不需要公开签名/publish/listing授权。

### 既有验收：仅缺陷涉及的复核与回归

以下保留原定义和r1独立范围，**不沿用作者r2把源码改善记成完整PASS的表述**。无关项未重新扩审；完整原生范围均BLOCKED。

|用例|本轮复核或承接范围|完整用例状态|
|---|---|---|
|T04|双独立连接接同一OPEN，仅一承接者/成功事件；锁步骤两PID同时成功，真实接单未跑|BLOCKED；D03算法FAIL|
|T05|错技能/无项目权限接单前导守卫拒绝仍成立；经理分配权威事件未跑|BLOCKED|
|T06|经理改派SCHEDULED，取消旧预约、ACCEPTED、新技工有效、旧技工拒；改派原分支保留，旧技工ID开工守卫拒；旧建议作废仍D04|BLOCKED|
|T07|编码与asset:载荷相同设备、假/跨项目/归档拒；设备ID负例守卫复核，编码/载荷解析未测，不改为M5验收|BLOCKED；解析NOT_RUN|
|T08|合法服务关系通过、同安装位置无服务拒；服务守卫复核；真正提交未跑|BLOCKED|
|T09|缺设备拒、维修中技工不能换设备、经理更正旧/新/理由；新增当前设备守卫通过，撤资格遗漏D05|BLOCKED；安全子范围FAIL|
|T10|提议不直接SCHEDULED、非原报修人不能确认；相关状态/确认主体原分支保留，提交未跑|BLOCKED|
|T11|同技工重叠双确认只一成功、相邻与跨项目；冲突/相邻子探针成立，锁互斥失败且冲突在锁外|BLOCKED；D03算法FAIL|
|T12|待确认改约旧确认保留，新确认替换，拒绝保留；旧CONFIRMED重叠改约被自冲突拒，旧PROPOSED提前撤销|BLOCKED；D02源码FAIL|
|T13|过期410、停定时器仍拒、伪造时间无效；原nowMs/截止分支保留，完整时钟/协议反例无运行条件|BLOCKED|
|T14|上海输入换UTC、模糊日期核对、end<=start拒；日期算术/非法日改善成立；真实输入、星期显示与规范化读回未跑|BLOCKED；日期子范围关闭|
|T15|旧version409刷新、不自动覆盖、阶段不能写任意百分比；边界未改；拒绝前撤旧提议仍违反恢复要求|BLOCKED；D02/03|
|T31|取消释放预约保留事件、终态不能开工/验收、再次故障关联新任务；新cancelAppointment准入已修，取消/重开完整用例未跑|BLOCKED|
|T35|模型生成期间改派/改约使旧角色/版本建议不能执行；APPLIED按钮失效改善，未确认旧草稿仍越过确认前导守卫|BLOCKED；D04源码FAIL|
|U01|三角色首屏说明待办、阶段、下一处理人；角色动作源码未改，无当前屏幕|BLOCKED；已有A02建议|
|U03|同任务三角色事实一致、权限变化、承接者不自验；原分支保留，实际多会话读回未跑|BLOCKED|
|U04|当前预约和改约提议区分，冲突/过期无假成功；D02未闭合，详情仍用简短apptLine；原生未跑|BLOCKED；D02源码FAIL|
|U05|安装位置/服务空间/来源可读；绑定和开工关系守卫成立；真实屏幕及实际安装位置展示未测|BLOCKED；已有A02建议|
|U07|重复点击/丢响应/版本冲突/离线输入及任务身份稳定；锁顺序释放已修，但互斥仍错；权威失败恢复未跑|BLOCKED；D02/03|

## 缺陷

沿用r1编号；仅核心或安全问题为P1必修，其余建议挂账。

### D-M4-01 / 日期解析子范围 CLOSED；展示与原生验证未完成

- 文件：`app/bundle/main.splash:730`、`:736`、`:743`、`:770`。实际年月日/上海UTC+8和非法日校验已修，独立标准时间对照通过。
- 证据：`source-probes.json`前7条及对应翻译文件。`formatApptLine:685`虽然改为读取appointment，但当前详情仍在`:3065`、`:3109`调用`apptLine`，没有调用新helper。展示接线承接A-M4-02建议，未因这项单独判FAIL；完整D01的原生验证仍BLOCKED，不写完整桌面PASS。

### D-M4-02 / P1 / 必修 / PARTIAL：旧确认仍自冲突，准入拒绝前旧提议已撤销

- 文件与行：`main.splash:788`、`:802`、`:2518`、`:2525`、`:2533`、`:2686`、`:2707`、`:2715`、`:2726`。
- 已闭合：`sourceOk:297/302`准入两个新命令；已有PROPOSED按ID排除；专门改约不再要求先取消。
- 触发1：当前CONFIRMED为100–200，改约150–250，只有旧确认无待提议。独立执行实际冲突函数。
- 实际/预期：previous_proposed_id为空，旧CONFIRMED仍被检查，返回冲突；应允许同任务替换旧确认的新提议，旧确认保持有效至新确认或拒绝。其他任务/跨项目同技工冲突仍拒绝。
- 触发2：已有PROPOSED，替换它并在统一边界注入旧version/撤权/锁拒绝。
- 实际/预期：执行原改约前缀到边界前，旧status已为SUPERSEDED；应在准入失败时仍为PROPOSED，任务/预约/历史不变。proposeAppointment的`:2525`有同样顺序。未宣称该内存污染已在原生落盘。
- 根因/影响：只排除旧PROPOSED，漏旧确认；先修改事实再授权/版本准入。正常重叠改约被阻断，失败会污染后续操作的内存事实。
- 证据：source-probes中的`confirmed_overlapping_reschedule_should_be_allowed`、`old_proposal_unchanged_before_rejected_command`，实际函数翻译和diff。
- 具体改法：显式排除本次改约可替换的同任务预约ID集合，保留其他任务/项目检查；只有边界准入、权威重读/校验成功后才同时撤旧提议并增新提议，失败不留下变更。新确认才撤旧确认，拒绝/过期保留旧确认。
- 验证：只有CONFIRMED时做重叠改约；已有PROPOSED时替换；确认新/拒绝新/过期；旧version、撤权、锁丢失注入，核旧预约字节、任务、事件、回执与桌面均无假成功。

### D-M4-03 / P1 / 必修 / PARTIAL：读-写-读回不是原子CAS，两个进程同时进入

- 文件与行：`main.splash:933`、`:937`、`:942`、`:946`、`:949`、`:957`、`:2550`、`:2562`、`:2575`；作者脚本`r2/scripts/m4_d03_lock_cas.py:10`、`:49`。
- 已闭合：释放为空后可再次顺序获得；`:2189`创建自增满足commitBound版本要求。仅这两个子项关闭，完整创建/连续命令未原生验证。
- 触发：A、B先读空；A写A戳并读回成功，停在临界区；B写B戳并读回成功；A释放。
- 实际/预期：两个独立PID均acquired=true，同时持有临界区资格；A释放还清掉B锁，第三次获取可看见空。应只有一个进入，释放只属于实际持有者。
- 根因/影响：没有原子compare-and-swap，读回只能证明瞬间相等；注释“只有一个能读到自己的stamp”错误。跨进程stamp也没有保证唯一。同一task版本检查及同技工跨任务冲突不能因此获得互斥；冲突检查仍在runCommandBound前读内存TASKS，修锁后也必须移动到锁内权威重读。
- 证据：`concurrency.json`完整双PID时序、两成功、清掉对端锁、两个worker退出0；`concurrency_probe.py`；`affected-regression.json`显示边界未改。本反例不是原生业务双成功，不冒称T04/T11已实际跑完。
- 具体改法：使用选定宿主实有的原子互斥或唯一串行写入机制；同一边界重新读取当前任务、资格及该技工所有项目预约，校验并提交，所有异常正确释放。若无原语，交付可运行最小复现并明确BLOCKED，不能继续用文件读回模拟声称CAS通过；不自行引入未经裁决的Python业务服务。
- 验证：本轮确定性交错反例必须拒绝第二者；真正独立上下文抢同OPEN、确认跨任务/跨项目重叠只一成功；相邻成功；崩溃/写失败/丢响应/重启后可对账且无遗留锁阻断。
- 隔离要求：作者脚本使用`tempfile.gettempdir()`，报告列出的直接重跑命令没有重定向TMPDIR；本轮未原样运行，不推断旧运行实际写到了哪里。改为明确项目内路径或强制隔离env，并保证不覆盖作者证据。

### D-M4-04 / P1 / 必修 / PARTIAL：尚未确认的旧AI草稿仍越过确认守卫

- 文件与行：`main.splash:830`、`:833`、`:842`、`:2089`、`:2113`、`:2117`、`:2122`；编辑`:1955`，清空草稿`:1946`。
- 已闭合：APPLIED变EXPIRED、active请求关闭、解绑/提议/确认/拒绝的新调用点成立，不能再用旧APPLIED按钮条件声称全部完成。
- 触发：旧AI内容已经采纳入PENDING_DRAFT但尚未确认，last_confirmed_at_ms=0；改派或改约调用失效函数，再确认旧草稿。隔离探针使用合成字段和有效身份stub。
- 实际/预期：失效函数因时间戳为0不设置invalidated_by_edit；AI_STATE虽EXPIRED，confirmDraftModelBound不检查它或旧建议的当前任务/角色/事实版本。原确认前导守卫仍通过，能到createDraftFromPanel入口；预期拒绝旧建议，必须核对新主体/任务和事实版本。本轮未执行真实创建，不能写成已产生原生越权工单。
- 根因/影响：将“是否有上次成功确认”当作“本次旧草稿是否失效”；禁止采纳按钮没有封住确认消费端。非零时间戳确实拒绝了，但editRawText仍置失效，再点同一确认入口继续拒；只有closeDraftPanel全清空，不是报告声称的普通编辑后重新确认。
- 证据：source-probes中的`unconfirmed_old_draft_marked_invalid`和`stale_unconfirmed_draft_confirmation_blocked`，失效函数源片段、实际确认前缀翻译；confirmed_recovery_note。
- 具体改法：失效针对相关proposal/草稿/确认的具体绑定和版本，不能依赖last_confirmed>0；显示、采纳、最终确认三处统一检查当前actor/project/task与事实版本。保留审计但将旧内容标不可执行；提供明确的“核对更新后的内容并重新确认”出口，成功后只清除当前新版本的失效状态。
- 验证：回包前/采纳后确认前/已确认后分别改派、改约、解绑、撤权；旧建议无法采纳或确认，任务/回执不变；重新核对新内容可继续，不靠手工清字段。

### D-M4-05 / P1 / 必修 / PARTIAL：设备检查已补，但当前承接者撤角色/技能后仍可通过开工守卫

- 文件与行：`main.splash:192`、`:226`、`:499`、`:986`、`:2744`、`:2747`、`:2752`。
- 已闭合：设备不存在/归档/跨项目/撤服务关系均被新开工前导守卫拒绝；缺设备、缺预约、旧assignee、时窗负例亦拒绝。
- 触发：任务assignee仍为同一ID，账号未全局revoked且未过期，但项目TECHNICIAN角色或所需技能被撤销；设备和确认时窗仍有效。
- 实际/预期：开工只比较assignee ID，未调用hasRole/skillOk；identityActive只查存在/全局revoked/expiry。撤项目角色或技能后前导守卫仍通过。应重新核当前项目有效技工资格及技能，拒绝旧资格继续开工。原生实际授权/开工未执行。
- 根因/影响：执行时校验设备事实，但承接者资格只继承接单时快照。此项属于r1 D05已要求的“当前承接者资格”及撤角色/技能验证，不新增无关扩审。
- 证据：guard-probes中`start_after_technician_role_revoked`、`start_after_skill_revoked`均passes_leading_guards=true；真实isAssignee/getMe/identityActive源码确认无后续资格补查。
- 具体改法：在开工的同一权威执行边界重查当前项目TECHNICIAN角色、技能、当前assignee及有效身份，与设备服务关系、任务版本和有效确认预约一起校验。拒绝明确说明资格变化，保留任务与预约，提供重新分配/确认出口。
- 验证：分别撤角色、撤技能、全局撤权、身份到期、改派旧技工，再查无成功开工事件/回执；合法资格恢复后的真实开工与权威读回成立。

### 建议挂账，不因建议判 FAIL

- A-M4-01：r2清单JSON有效，但字节/行数错误；37/37只覆盖源码关键词和Python模拟，不能记原生T/U为PASS。使用实际文件和独立证据生成数字，保持完整用例BLOCKED。旧错误映射不扩成必修。
- A-M4-02：角色首屏/全量表单、安装空间实际字段、动作/错误出口承接r1；新formatApptLine未接详情，改好helper不等于屏幕已显示完整预约。只在核心动作可运行后修必要接线，真实三角色截图/输入验证，不追求视觉完美。
- A-M4-03：历史previous_assignee仍取未赋值字段；失效reason现在已保存，属部分改善。继续挂账，不扩展历史系统。

## 判定

- 最终结论：**FAIL**；精确范围为M4-r2固定候选、r1 D01–05闭合复核和受影响回归。D02/03/04/05仍P1；完整原生必需项另为BLOCKED，不能以作者37/37替代。
- 必修清单：D03真实互斥与边界内权威重读；D02排除同任务被替换旧确认且失败不变更预约；D04尚未确认旧草稿失效与可用重新确认；D05开工时当前技工资格。仅修这些及受影响回归；已改善子项保留，不要求修无关前序挂账和建议。
- 环境解阻：需要可实际应用项目内写入/禁网络隔离策略、可查询并回收自身进程及窗口的测试执行环境。本轮`sandbox-exec -f review-r2/isolation.sb /usr/bin/true`返回71，`pgrep`返回3。具备条件后，后台启动指定launcher，try/finally回收自身进程并核无残留；禁止`--help`。不能从HOME变量设置或作者旧日志推断环境已解阻。
- 本地安装路线已通过，**不需要**公开签名、publish或listing。签名仅隔离本地catalog，私钥已删除。本轮没有配置真实provider、决定业务身份来源或申请上述授权。
- 前序回归：源码差异及依赖核查完成；原生回归BLOCKED，M0/M1/M2/M3结论保持不变。创建自增子项不等于M3整个模块PASS。
- 门禁：只更新GATES的M4状态及审查字段，review_report指本报告；保留原作者构建字段，归档替换前审查字段。ACCEPTANCE.json不改，历史来源和后端结论不覆盖。
- 是否允许下一模块：**否**。留在M4修复/解阻，不执行下一模块，不给下一模块实施任务。
- NEEDS_ABRAM=no：剩余为本模块代码与执行环境；本地安装可行，离线签名已授权，未出现必须由Abram授权的公开发布/provider/业务身份来源决策。

STATUS=FAIL
NEEDS_ABRAM=no
