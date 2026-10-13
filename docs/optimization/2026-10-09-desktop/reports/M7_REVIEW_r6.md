# M7 独立 Review r6

**最终结论：FAIL。M7-r5-worktree / 0.1.0-d 已在六场独立harness中实际加载，每场3条解析错误，六张截图业务区均空白。B-M7-01仍OPEN / P1必修。隔离与进程回收6/6 PASS；没有harness ABORT，不使用agent沙箱rc71/rc3作BLOCKED理由。**

- 审查者 / 日期：当前主会话唯一独立主审，无子代理；2026-10-11 Asia/Shanghai。置信度：候选字节、隔离、解析故障、空白UI高；未执行业务/模型效果未知。
- candidate_id=`M7-r5-worktree`，base=`M7-r4-worktree`；GATES、实施r5和r5/CANDIDATE三方一致，非按文件mtime选版。被审HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty清单/内容摘要及binary diff见S；HEAD单独不能重建候选。
- 冻结包：`runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/`；main SHA=`a1293738da6d0eacba648487c14aa02aa083dfe9773c40222afa2a90d3f17c11`，417104 B；digest=`b3d10ba769a004e6fc244ec0af803d9be19869b63f3592e236e1d2fe1996bb17`。主源与当前工作区相同，版本不沿用旧0.1.0-c成功/失败统计。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r5.md`；候选清单：`runtime/optimization/2026-10-09/M7/r5/CANDIDATE.json`。
- 前置核对：M6=`M6-r5-worktree / M6_REVIEW_r6.md / FAIL`，无独立接受的M6 PASS候选。按用户前序挂账裁决继续本模块，不代修前序；本轮FAIL有当前候选的独立原生证据，不以旧挂账或建议拒收。
- 实际宿主：M0/r3提取OctoSense.app；MacOS/octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，MacOS/octos-kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`，本段重算和记录一致。二进制可定位，不声称未知上游源码可复构。主会话Router/指定gpt-6.1-sol无验证或切换接口；自身createdAt/标题接口未提供，未声称完成路由切换/改名。
- 审查开始/结束快照：第1段至本段所有受保护候选、作者资料、配置、宿主、harness及原验收台账一致；最终只改本报告、M7审查字段及S核验材料。其他模块/GATES全局字段不变，核验见S/final-review-verification.json。
- 已阅读：第1段AGENTS/CONTEXT、00/01/02/M7/04及上一轮缺陷涉及材料；第2段六份result、summary、完整MANIFEST、全部日志/profile/denials、实际.running包与六张PNG；只核上轮编号及基线变化受影响回归。
- 已运行：第1段独立check/stamp/keygen/certify/sign-manifest、catalog验签及官方install_staged/Store重建/may_run；第2段只读证据/字节/日志/隔离审计。原生运行仅驱动沙箱外harness（17:39:01–17:40:41 +08:00），审查方未启动launcher/sandbox-exec/pgrep、--help或osascript/辅助功能/外部UI自动化。
- 未运行：可信三角色正常/退回/失败重试链、真实附件/业务回执、模型、同盘跨进程业务恢复、实际scan独立审阅及完整演示。源码/作者静态计数不替代这些结果。只在具体白名单能力缺口记BLOCKED，解析故障是FAIL，后续未操作是NOT_RUN。
- 访问与授权：两段本轮均只显式读写项目内；没有读取secrets、真实账号数据/安装数据/host-data、明文凭据或项目外记忆/技能。无联网/publish/listing/push/issue/消息/部署/计费变更。模型调用0，无402/欠费，NEEDS_ABRAM=no。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M7/native-runs/review_r2_1309_REQUEST_review_r2_1309/`，驱动原始证据，只读保留。
- **S**：`runtime/optimization/2026-10-09/M7/native/review_r2_1309/`，phase1-audit、dirty.diff、old-frozen-to-new-frozen.diff、离线Store/seed、native-evidence-audit、门禁原快照与最终验证。
- **R**：`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r2_1309.json`；**N**：同目录`REVIEW_NOTES_r2_1309.md`，阶段笔记保留原文。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本/dirty/前置|GATES、实施、清单定位；核主源/旧冻结差异与M6|来源明确、不挪用旧通过|新包可定位；与M6 r5只差4处保留字替换/+16 B；M6 FAIL保留|定位PASS；前置未PASS|S/phase1-audit；M6 r6|
|证据完整性|所有MANIFEST项重算，summary/request/result、marker/denial重新生成|无漏项/错hash/重复|807项全匹配，无漏列/重复；日志摘要一致|PASS|H/MANIFEST；S/native-evidence-audit|
|隔离/回收|重建六profile，核禁读探针、环境/写目录、PGID及外写扫描|限制项目内新run写；禁读5项；无进程残留|6/6 probes ok；pre/post NONE；PGID_after空；CLEAN|PASS|H/*/result/profile/denials|
|实际包加载|seed/installed/.running七文件逐字节对账，核launch/eval|新候选真正加载|6/6实际417104 B eval；六非manifest文件与原包相同，manifest只离线签名归一化|PASS加载子项|H/*/.running；S/audit|
|干净首屏/核心入口|全新Store launch/capture，逐张看PNG与parser日志|登录/任务/下一步可操作|6场各3 parser错误，业务区全部空白|FAIL B-M7-01|fresh/logs:43–45；六PNG|
|输入/焦点诊断|新无效字符串、Tab与内置触点，核宿主实际支持|输入可操作、拒绝可见|tap/type/key均有unknown日志；taps调度但空白业务区|输入子项BLOCKED；业务NOT_RUN|auth/logs:39–43；narrow:39|
|重复开启|同场2次launch核client/eval、权威变化|只凭真实业务结果判幂等/恢复|请求2次，日志实际1 client/1业务eval；无任务/回执|开启子项；业务幂等/重启NOT_RUN|repeat/logs:32–50；S/audit|
|坏数据恢复|隔离预置坏tasks与follow_ups，核原文/备份/恢复出口|原文保护、可解释恢复|原文未变，无备份；UI解析失败、无恢复入口；业务写0|可操作入口FAIL；业务恢复NOT_RUN|broken_* data/PNG/log|
|正常/退回/失败/重启同版本|核动作/主体/回执/事实及运行包|同一候选可复跑核心闭环|没有可操作业务或回执；精确故障/并发/跨进程恢复缺白名单动作|核心入口FAIL；后续NOT_RUN/具体BLOCKED|B01；原64表|
|模型/可信身份|核实际config/identity/代码入口/UI/代理记录|可信会话与真实MiniMax有实证|退役空identity fixture，业务账号路径存在但未登录；enabled=false，无代理/请求|NOT_RUN；不改包制造成功|实际.running配置；G0-B/E|
|材料/媒体同版本|11指纹、自hash、listing、SOURCES/PRIVACY/README对照|当前版本、无假完成|字节可定位；placeholder不是关键图；材料仍旧0.1.0-c，README称B01闭合|指纹PASS；建议挂账；媒体NOT_RUN|A01/A02/A03；S/audit|
|本地准入/scan|独立check、离线验签及Store安装|check和真实独立审阅均有证据|check/验签/install/rebuild/may_run PASS；scan未跑|准入子项PASS；P03 NOT_RUN|S/phase1-audit|
|外部状态分离|只核本候选回执与外部字段|本地/公开/赛事/收录分别记录|本地FAIL；外部本候选无回执，UNASSESSED保留|PASS状态分离；外部NOT_RUN|判定与GATES.external_delivery|

## 原生证据逐项核对

1. **MANIFEST 807/807**全部SHA一致，无缺失/漏列/重复；summary.request与R完整相同，六份result identity/verdict/exit/wall与summary一致。harness/template/请求/宿主摘要一致。
2. 六份Seatbelt profile按实际run/control端口独立重建相同；probes.apply rc0，场景外写拒绝且未创建；五项secrets/明文credentials/~.codex/~.cc-switch/~.ssh禁读均成立。HOME/app-data/cache/config/tmp全部在各run目录。模板含/dev/null写例外与unix-socket放行，按获准harness口径记录，不夸大成所有设备/IPC完全禁用。
3. 六场pre/post均rc1、class=NONE、out/err空，pgid_members_after=[]；host_returncode=0、quit_http=ok、exit_method=quit_http，wall=15.17–15.84 s。外部Library扫描空、原HOME .octosense mtime未变。无ABORT。
4. 运行中fresh PGID见osascript，broken_tasks见(pmset)，repeat_open见<defunct>；最终全部回收。审查方只发获准宿主内置动作，未调用这些程序；其内部具体用途未独立确认，不臆造辅助功能行为或声称宿主全程没有子进程。
5. denials全文正则重算与result一致：443外联、系统Metal缓存与部分/dev/dtracehelper写被拒。拒绝记录不等于越界成功。宿主news显示7源失败/0新数据；不据此宣称宿主未尝试网络。模型关闭、代理统计缺省、无proxy/欠费记录，本轮真实请求0。
6. 每场files_written_count=116，列表116唯一文件均存在且在run目录；**业务jail写入0**。这些是宿主初始化/.running/截图等，不能记为任务提交成功。seeded_files逐项与本段seed/mirror源一致，原文与摘要全部保留。
7. 每场installed与实际`.running/<随机目录>/`七文件与本段离线签名运输副本一致；六非manifest资源与交接原包一致。manifest只加签名/官方默认字段，无扩大权限；catalog.listing与新包相同，没有旧B完成宣称。digest在seed可见、host log未包含digest，靠实际运行副本及417104 B eval证明装载。
8. 六张PNG逐张视觉确认标题OctoSense Repair、业务区完全空白，无登录/任务/按钮/错误恢复。原图均2800×1718；前四张hash相同，后两张hash相同（顶部时间变为17:40）。三种size请求未给出三个实际业务客户区，U09不能通过。
9. 每场3条[E] splash解析错误，VM位置1522:84/110；fresh/broken日志:43–45，auth:48–50，repeat/narrow:44–46。包物理1519的括号条件表达式与前序M6解析失败定位一致，VM偏移+3由前序定位及实际字节对照支持。没有本轮ok reserved错误，保留字子项改善成立；parser仍失败。panic=false、tick=true、进程rc0不能抵消解析故障。
10. auth明确unknown四动作（单tap、两次type、key:Tab），narrow拒绝key:Tab。taps接受调度不证明命中登录。坏tasks/follow_ups仅各原文文件保留，无备份/业务变化；没有恢复UI。这证明未进入业务，不是失败恢复PASS。

## 缺陷与上轮闭合

### B-M7-01 — OPEN / P1必修；本轮FAIL依据

- **文件与行**：最终包`M7/r5/release/octosense-repair-0.1.0-d/main.splash:1519`（工作区同1519）；作者`M7_IMPLEMENTATION_r5.md:14`选择新基线，却依据旧冻结1404行已变化认为条件表达式问题消失。候选`M7/r5/CANDIDATE.json:17、21–22`记录新基线及保留字替换。
- **触发**：用R fresh_candidate，从无业务数据新Store安装0.1.0-d，harness内置launch-hub后capture。无需模型、账号或附件操作即复现。其余五场相同。
- **实际/预期**：VM1522:84报Expected )、1522:110两条Expected } not found；六张业务区空白。预期是新冻结包在目标宿主能解析、展示真实登录/任务/下一步入口并进入核心流程。
- **证据**：H/fresh_candidate/logs/host.log:43–46；六场日志/PNG；S/native-evidence-audit实际.running全字节匹配。不是旧M6故障推测，也不是安装错误、镜像旧字节或隔离ABORT。
- **根因**：新包从旧M7主源283933 B切至M6累积417104 B；独立比较与M6 r5只差4处ok→passed（16 B），1519已知不可解析的`((event_seq == nil) ? "0" : event_seq.to_string())`原样保留。只查旧1404物理行及ok词命中，漏掉新基线已有解析缺陷；hub check验证准入不验证宿主脚本解析。
- **影响**：维修核心UI完全不可达，本模块可复现桌面发布候选目标未成立；硬验收1/2/4、G0-A及核心U/P失败。安全隔离已成立仍不能放行空白产品。
- **具体改法**：构建方在所选主源1519先把seq条件计算改为明确if/else临时字符串，再拼user_text；不是继续追旧1404行号。检查受影响表达式1431/1536/7031，但以实际parser日志定位，不宣称每个问号都已证实错误。保留两处passed修复，重新冻结新candidate/version/主源/配置/digest/catalog/材料；不能只修工作区而运行旧包。新基线的新增差异与影响列清，不把M6 FAIL叫已接受。
- **验证方式**：仅驱动harness，以同一新digest干净Store实际加载；检查parser错误0、登录/工作台可操作，并核实际.running和日志/PNG。再用隔离新造测试凭据完成受影响核心动作，权威task/action/version/附件读回、正常/退回/失败恢复及必要重启回归；白名单缺口需驱动在获准隔离范围内提供明确可复现动作，不以静态模拟代签。真实模型若交付启用新候选，走needs_model代理、OCTOSENSE_MODEL_ENDPOINT和≤10预算；不可修改本候选配置后挪用新证据。阶段截图/演示属于冻结字节，替换媒体改变digest时重新核受影响项。
- **已闭合子项**：保留字替换、当前本地catalog/install_staged路线、实际新包识别/加载、隔离/禁读/网络限制/PGID回收通过；未把局部子项升级完整B01闭合。
- **NEEDS_ABRAM=no**：本地路径可行，技术修复、驱动、身份/MiniMax已有授权；没有public发布需求或账单错误。

### D-M7-01 / D-M7-02 / D-M7-03 — CLOSED子项保持，已做新候选回归

独立check/验签/Store安装通过；11表项+外存selfhash一致，原64编号/定义保留。不追加业务PASS，也不把旧scan自答、r4测试总数迁移成新包验收。

### A-M7-01 — OPEN / P2建议挂账

- 文件：app/README.md:5、88–100、104–121。仍指0.1.0-c旧候选/错误../../runtime链接，声称B01闭合，保留禁止直接Popen和项目外/tmp命令。
- 触发/实际/预期：按入口复现会选旧包/旧驱动；应明确0.1.0-d、harness与当前FAIL。根因是入口未随交付更新；影响复现准确性，本轮没有执行这些历史命令，不单独因此FAIL。
- 改法/验证：当前步骤指向独立harness，新候选链接用../runtime；旧命令标历史不可执行，完成措辞按真实报告；逐链接解析/入口读回及文档指纹核验。

### A-M7-02 — OPEN / P2材料建议挂账；旧图移除子项改善

- 文件：r5 release-materials/SOURCES.md:1、22–29、38、48–51；PRIVACY.md:11、14；bundle/listing.json:4、12–14、28。
- 实际/预期：listing移除旧B完成宣称/截图，仅1×1 placeholder且有未验证说明；材料仍称r4/0.1.0-c、旧main/digest/provider/6截图与旧启动法。应对应当前0.1.0-d的真实字节、harness、退役identity与关闭MiniMax配置；placeholder不能当关键业务图。
- 根因/影响：新材料目录复制旧稿而未同步；材料尚未形成同版本发布准备。按用户核心优先裁决只列建议挂账，不单因文案/媒体缺口判FAIL。
- 改法/验证：只改当前事实及未知范围，移除无证据外部绝对断言；补当前真实图/演示后重新冻结摘要；对catalog/包/材料/截图逐项版本读回。无需联网公开发布。

### A-M7-03 — CLOSED，新selfhash与本段离线私钥销毁有独立证据

INTEGRITY.txt:33–51共11指纹项匹配；外存SHA=`e50208c29031ad60d7a4578f2f56ca3aa0e37c4d81b56bedc9a156d187cf30e1`。本段sandbox-only仅当前digest签名，anchor.key/working.key在try/finally删除，keys目录为空（S/phase1-audit的keys_deleted/remaining及最终验证）。没有用历史r2删除证据替代本轮，没有公开签名/publish。

## 相关既有用例逐项复核

保留ACCEPTANCE原64定义和历史状态，额外L8-DV2未删除；这里是本候选的完整用例结论，子项通过不会升级全项。能力BLOCKED只用于下列具体动作缺口，无ABORT，旧rc71/rc3不再适用。

|编号|原定义|本轮状态|证据与范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|源码有私有SESSION/账号表路径，identities为退役空fixture；原真实账号未访问，可信登录/会话/权限未执行。auth场tap/type/key明确不支持，输入子项BLOCKED。|
|G0-C|唯一事实源、原子一致性、并发与恢复|NOT_RUN|官方Store安装/重建/may_run子项PASS；业务事实源、原子提交、并发/崩溃恢复未执行；业务写0。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|没有实际上传/回读/归属验证或失败重试；不以placeholder PNG及坏文件当真实附件。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|坏follow_ups原文保留但应用解析前失败；没有提醒恢复/去重/跳回业务结果。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|repeat_open两次launch实际一client，无create key/task/action回执，不能用无写入证明幂等。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|BLOCKED|白名单不能建立两个独立可信连接并发接单；重复launch-hub实际只一client，不是并发主体。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|BLOCKED|白名单缺两个可信主体并发预约确认调度；实际key/type也不受宿主支持。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|BLOCKED|schema只有预装seed/固定内置动作，无断线/重连注入接口，未执行该步骤。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|BLOCKED|白名单没有任务/预约/事件具体写入之间的精确异常注入步骤，坏文件冷启动不能替代。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|BLOCKED|每场新目录，schema没有同盘跨进程重启/提醒调度步骤，重复launch未重启进程。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|同包实际.running/加载子项PASS；无可操作task_id、业务命令或权威回读，同盘跨进程恢复未执行。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|没有grant关闭/退出/到期/共享卡授权业务操作，进程回收和Seatbelt不能代替业务撤权。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|未运行旧配对审批/poll_secret，也未实际验证原生可信会话替代链；不默认N/A或PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|运行副本model_config enabled=false、manifest仅storage；无代理/请求，本轮0次。存在代理endpoint覆盖代码不代表已调用。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|当前源码/config/宿主/digest/request/data及成功安装/失败解析可复现；真实模型成功/失败场景未运行，完整用例NOT_RUN。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|应用parser前失败，未形成可编辑草稿/人工继续；type/key输入子项因宿主unknown而BLOCKED。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|应用parser失败，未进入可操作业务界面；对应命令、权威回执/事实及失败恢复未执行，不继承旧包/后端PASS。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|BLOCKED|三种size仍得到相同2800×1718画面/业务窗，没有可验证的窄客户区或150%文字调整动作。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|目标宿主明确unknown --test-action key:Tab及type，白名单无法完成键盘主要流程。 能力边界仅作用于该完整用例；parser失败另记B01 FAIL。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|6张实际PNG只有空白业务区；包内1×1占位图，无同版本关键业务图、2–3分钟演示或独立复述。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|FAIL|6/6实际加载新包后各3条parser错误、业务区空白；核心可操作入口失败，后续完整业务未执行。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|独立check/验签子项PASS；本候选scan实际独立审阅NOT_RUN，不用旧scan自答替代。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|6张实际PNG只有空白业务区；包内1×1占位图，无同版本关键业务图、2–3分钟演示或独立复述。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|NOT_RUN|11项指纹+外存selfhash及源/实际运行包对账子项PASS；B01 P1未关闭，材料旧版本建议挂账；完整交付条件未成立。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|没有本候选实际外部回执；GATES.external_delivery保持原UNASSESSED；未发布/提交/收录，不挪用旧B回执。|
|P07|维护者商店收录结果|NOT_RUN|没有本候选实际外部回执；GATES.external_delivery保持原UNASSESSED；未发布/提交/收录，不挪用旧B回执。|
|P08|赛事正式提交入口回执|NOT_RUN|没有本候选实际外部回执；GATES.external_delivery保持原UNASSESSED；未发布/提交/收录，不挪用旧B回执。|

## 五项硬验收

|硬验收|本轮结论|依据|
|---|---|---|
|1 同一候选必需业务/UI/运行实证|FAIL|真实加载6/6，但parser/可操作首屏FAIL；业务/模型/T/U未执行不冒充PASS|
|2 正常/退回/失败恢复/重启/模型同版本|FAIL|核心入口未可用；业务全链/真实模型NOT_RUN，具体并发/重启动作BLOCKED|
|3 包/源码/媒体/描述一致|NOT_RUN|源与实际运行字节、指纹子项PASS；当前可用关键图/演示缺，旧材料版本建议挂账|
|4 本地准入/独立审阅/干净启动|FAIL|check/catalog/Store子项PASS；干净业务首屏FAIL；独立scan未跑|
|5 本地与外部状态分离|PASS|本地FAIL；当前候选公开发布/P06、收录/P07、赛事/P08无回执，NOT_RUN/UNASSESSED明确保留|

## 判定

- **最终结论：FAIL。** 精确范围是本地桌面发布准备候选M7-r5-worktree/0.1.0-d；不是外部评审或收录结论。失败依据只有仍开放的核心P1 B-M7-01，不因P2建议或前序挂账单独拒收。
- **本模块修复清单**：修1519实际parser阻断→重新冻结候选/摘要→harness核无解析错误及真实首屏→补受影响核心流程/权威回读和失败恢复。A-M7-01/02继续建议挂账；不要求顺手修前序无关业务或美化。
- **阻塞与未测**：输入/Tab确实不受宿主白名单实现支持；并发主体、精确写故障、断线重连、同盘跨进程提醒恢复及实测窄窗/放大缺动作，具体见64表。其余因parser未到业务为NOT_RUN；身份/MiniMax来源已经确定，不是待授权。
- **受影响先前模块复验**：当前同字节基础首屏与M6新增phase/恢复区域解析已独立复验失败；没有修改或重新给M6其他功能结论。旧原生/后端PASS保持原版本范围，不转移到此包。
- **状态分开**：本地准备FAIL；本候选外部发布/Hub递交NOT_RUN；赛事正式递交NOT_RUN；商店收录NOT_RUN。GATES.external_delivery原P06/P07/P08 UNASSESSED不变；历史0.1.0-b回执不代表0.1.0-d已提交。
- **门禁/台账**：仅GATES.M7.status与review_*及review_history记录本轮，review_report指向本报告；历史审查快照保留于review_history与S/gates-before-review.json。原ACCEPTANCE.json不改，原64结果在本报告/GATES.M7.review_acceptance按候选单列。
- **是否允许下一模块：否。** 留在M7修复/重审；不执行下一模块或发布动作。
- **NEEDS_ABRAM=no。** 没有公开发布或MiniMax余额/欠费阻塞；已授权技术工作即可继续。
