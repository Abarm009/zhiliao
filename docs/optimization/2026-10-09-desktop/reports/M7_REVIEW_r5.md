# M7 独立 Review r5

**最终结论：FAIL。交接候选已在4场独立harness运行中实际加载，每场17条脚本解析错误，业务区全部空白。B-M7-01核心可用性仍未闭合。隔离与回收4/4 PASS，不再用agent沙箱rc71/rc3作为BLOCKED理由。**

- 审查者 / 日期：当前主会话唯一独立审查者，无子代理；2026-10-11，Asia/Shanghai。置信度：字节、隔离、原生解析失败与空白首屏高；未执行业务/模型效果未知。
- candidate_id=`M7-r4-worktree`，base=`M7-r3-worktree`。GATES、r4清单、实施报告三方定位，没有按mtime选版。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r4.md`；候选清单：`runtime/optimization/2026-10-09/M7/r4/CANDIDATE.json`。
- 被审包：`runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/`；0.1.0-c；digest=`a7451d34d7aa808bc534df0350b5e501cc5fc83a9861f296e9ea4574c9b2ea10`；main SHA=`ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6`，283933 B。r4候选仍复用r2包。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`，有未提交改动。当前工作区main SHA=`9a1a8e274f4cd9b98d1fcdad4ac21d5dd6d391de8b3af30f07192d6c0822af34`，417088 B；它是后续M6字节，不是本候选。完整dirty清单/内容摘要/差异见S，未reset/stash/删除他人修改。
- 前置：M6=`M6-r5-worktree / M6_REVIEW_r6.md / FAIL`，没有接受的M6 PASS候选。按用户挂账裁决继续M7；不单因前序FAIL拒收、不代修前序。当前FAIL依据本候选真实运行。
- 实际宿主：M0/r3提取OctoSense.app，octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；MacOS/octos-kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`，独立重算一致。来源二进制可定位，未知源码commit不冒充可复构。
- 实际运行：驱动沙箱外于17:15:02–17:16:05 +08:00执行本审查请求；审查者没有自行启动launcher/sandbox-exec/pgrep、没有--help、没有osascript/辅助功能操作或外部UI自动化。
- 主会话路由/标题：无可验证Router/切换指定gpt-6.1-sol或自身createdAt/改标题接口，未声称完成切换或改名。
- 开始/结束快照：第1段至本段候选/作者材料/源码配置/宿主/harness/ACCEPTANCE/GATES均一致；最终只改本报告、M7审查字段及本段核验记录。最终回读见S/final-review-verification.json。
- 阅读：先读CONTEXT与项目AGENTS，00/01/02、M7、04、r4 Review/实施/清单及原64定义；第2段读summary、4份result、全部日志/profile/denials/manifest和实际包，并独立看4张PNG。只核原缺陷与受影响回归。
- 已运行：第1段独立check/stamp/verify、官方install_staged及Store重建/may_run；第2段完整证据摘要、profile重建、seed/运行包/权威文件对账。真实宿主仅驱动运行。
- 未运行：真实可信三角色正常/退回/重做链、真实附件、业务动作与权威回执、真实模型、业务重启、完整视觉/键盘及演示。parser失败后的业务项NOT_RUN；真正白名单能力缺口在64表单列BLOCKED，不能伪称每项已操作。
- 第1段访问偏差保留：首批读过项目外记忆/技能说明，违反用户读取边界；随后停止。本段只显式读写项目内，没有读取secrets、账号原数据或明文凭据。未把过程偏差写成全程符合约束。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M7/native-runs/review_r1_1309_REQUEST_review_r1_1309/`，驱动原始证据，只读未修改。
- **S**：`runtime/optimization/2026-10-09/M7/native/review_r1_1309/`，phase1-audit、dirty diff、离线Store/seed、native-evidence-audit和最终回读。
- **R**：`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r1_1309.json`，SHA=`f9c00874625c670c2f84350f0ec87cbd5461547d5822e7a0a6364bfdcc5cb072`。
- **N**：`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r1_1309.md`，第1段笔记，不按第2段结果重写。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本/前置/dirty|三方定位候选、核源码/包/宿主摘要和M6结论|候选明确、前置真实|旧r2包明确，与当前M6不同；M6 FAIL保留|定位PASS；前置未PASS|S/phase1-audit及diff；M6 r6|
|证据完整性|MANIFEST全项独立重算、目录/summary/result/R对账|无错摘要/漏列/重复|599项全一致、错误0；请求与场景完全对应|PASS|S/native-evidence-audit；H/MANIFEST|
|内核隔离/进程回收|逐场重建profile、核探针/环境/进程/外写扫描/denials|5类禁读、限制写入/外联、无残留|4/4 profile ok、pre/post NONE、pgid_after空、CLEAN，正常quit|PASS|H/*/result/profile/denials|
|候选实际加载|核Store、registry/eval与.running全部12文件|目标包实际被宿主读入|4/4实际launch/eval；11非manifest字节与原包一致，manifest同离线签名副本|PASS加载子项|H/*/logs及home/.octosense/apps/.running|
|业务首屏/可操作入口|看全部PNG及parser日志|登录/任务/下一步可操作|4/4空白业务区，各17条parser错误|FAIL，B-M7-01|clean_wide/logs:43–59；repeated:45–61；4 PNG|
|重复触点诊断|独立2次内置taps、核实际业务回执/文件|只真实命中与权威结果算执行|触点已调度，应用空白；没有业务写/回执|业务NOT_RUN，不判幂等PASS|repeated_entry/logs:39–40；S/audit|
|损坏数据启动恢复|合成坏tasks/follow_ups，核错误出口/备份/原文|可恢复、原文保护|原文未变，无备份/恢复出口；业务parser前失败|入口FAIL；业务恢复NOT_RUN|corrupt_load_recovery/PNG/log/data|
|正常/退回/失败/重启同版本|核真实动作/权威结果与包版本|同一版本完整链可复现|没有业务动作；跨进程同盘重启缺白名单动作|FAIL核心入口；后续NOT_RUN/能力BLOCKED|B01、64表、R/schema|
|模型/身份同版本|读实际运行config/identity与UI/调用记录|可信会话、真实MiniMax及错误出口|冻结OFFLINE/旧演示身份，UI未渲染；无代理/请求/账单错误|NOT_RUN；不能用工作区替代|actual.running；model_config:6–9|
|冻结包/截图/演示/材料|核16指纹、自指纹、listing/旧catalog/文案|实证属于同候选，不含假完成|指纹一致；当前图空白；旧B图披露；README仍称闭合，旧catalog旧完成宣称|指纹PASS；材料建议挂账；演示NOT_RUN|INTEGRITY；A01/A02；H/PNG|
|本地check/scan|独立check、区分scan问题生成/自答和接受|最终包准入及独立审阅|check PASS；本轮scan独立审阅未执行|check PASS；完整P03 NOT_RUN|S/phase1-audit；64表|
|外部状态分离|核本候选回执及external_delivery|本地/发布/赛事/收录分别记录|本地FAIL；外部三项UNASSESSED，无本候选回执|PASS状态分离；外部NOT_RUN|下方判定及GATES|

## 原生证据逐项核对

1. MANIFEST **599项**全部SHA一致；无缺失、重复、未列文件。summary.request=R；4份result的scenario/verdict/exit_method/wall_s与summary一致；harness/template摘要一致。完整核验记录在S/native-evidence-audit.json。
2. 四场profile_probes.ok=true，apply rc0；场景外写探针被拒且未创建；secrets、明文credentials、~/.codex、~/.cc-switch、~/.ssh五项禁读探针均失败。profile字节按模板与真实本机控制端口独立重建一致；HOME/app-data/tmp/log/cache路径均在场景目录。无模型代理放行。/dev/null设备及unix-socket规则如模板，不冒充绝对禁止所有设备写或本机IPC。
3. 四场pre/post_pgrep均rc1/class=NONE、out/err空；pgid_members_after=[]，host_returncode=0、quit_http=ok、exit_method=quit_http、verdict=CLEAN，wall 14.22–14.31s。无ABORT，外部Library扫描为空、原HOME .octosense mtime不变。
4. clean_wide的运行中PGID包含osascript，退出后为空；其余运行快照仅宿主。审查请求只用获准宿主内置action，审查方未调用osascript。该内部进程具体用途未独立确定，保留事实，不声称宿主全程从未出现osascript，也不凭名字捏造辅助功能使用。没有新增此项产品缺陷。
5. 各场sandbox-denials原日志与result.summary正则重算一致：被拒443外联、Metal系统cache写、部分/dev/dtracehelper写；是拒绝记录，不是成功越界。news日志显示7源失败/0新数据；不能声称整个宿主从未尝试网络。本包model关闭，无model_proxy_stats、proxy文件或账单错误，真实模型请求0。
6. 每场files_written_count=121，列表121项均存在并在该run目录，包含.running包、宿主系统应用素材、截图/日志；**业务路径写入0**。不能把宿主初始化文件数说成维修任务写成功。seeded_files逐项与本段预装源对应，总源seed54项；所有seed文件摘要未变。
7. installed/.running的main/config/identity/listing及其余资源逐文件与相同离线签名副本一致；11个非manifest包文件与交接原包一致。manifest只增加离线测试签名及官方空/default字段；权限没有改动。digest只在seed可见、host log不含digest；实际.running摘要与283933字节eval共同证明装载，未靠digest字符串推导。
8. 四张PNG均实际查看、哈希与result及MANIFEST一致，均 **2800×1718** 且哈希相同 `6667016462d14569ff5a5f76c627199883b58a3378524433d4425e59358bf4b2`：标题为OctoSense Repair，业务区完全空白，无登录/列表/按钮/错误恢复文字。三种--size未产生三个实测视口，不据此通过U09。
9. 每场17条[E] parser记录，三条明确 `ok is reserved`，还有赋值/else/括号连锁错误。宿主返回0、marker.panic=false、eval含tick=true均不能抵消parser错误，亦不能证明业务正常。合成tasks/follow_ups原文保留但没有恢复UI/备份；这是应用未执行，不是业务恢复PASS。

## 缺陷与上轮闭合

### B-M7-01 — OPEN / P1必修；本轮判FAIL

- **文件与行**：`M7/r4/CANDIDATE.json:19–25`仍绑定r2冻结包；`M7/r2/release/octosense-repair-0.1.0-c/main.splash:574,577–579,968–977,1178–1182,1404–1405`；`model_config.json:5–9`。原r4 launcher脚本:151–172、248–273仅作历史方案，不运行、不要求修已被新裁决替代的驱动。
- **触发**：从无业务数据的新隔离Store，通过本轮R的launch-hub+capture实际加载该包。四场均复现；损坏数据/重复触点没有改变解析结果。
- **实际/预期**：目标宿主明确拒绝变量名ok，报告三处reserved及后续语法错误；四场业务区空白。预期是交接包能真实解析渲染、用户进入可信身份/任务流程，核心正常/退回/失败恢复/重启及真实模型证据属于同一候选。当前只证明安装/加载，核心入口不可用。
- **证据**：H/clean_wide/logs/host.log:43–59、clean_narrow与corrupt:43–59；repeated:45–61。日志源定位整体比物理包行号多3（根据三个保留字锚点推断）：日志577/971/1181对应包574/968/1178；日志1407附近对应包1404的三元表达式。正式修复以实际包文件物理行定位。S/audit、4 PNG、实际.running SHA共同固定候选与症状。
- **根因**：最终冻结包未在目标宿主做真实解析/业务验收，却一直用旧r2字节；该字节含目标语法不接受的保留字标识符，以及在1404附近触发Expected ')'的表达式。静态/译码通过、check、Popen退出0不能证明目标解析成功。三元表达式具体语法不兼容由日志与源码相邻定位支持；更深的后续handler故障未执行，不预先断言全部问题已知。
- **影响**：维修桌面核心功能完全不可达；任何旧业务/模型/截图成功均不能证明此候选可发布。违反硬验收1/2/4。不是因为建议项或全部前序挂账而FAIL。
- **具体改法**：构建方在本模块只修阻断最终候选运行的语法/封包差异；把所选基线中ok局部变量及全部引用改为非保留字（已报错574/968/1178，另需检查1701/2018/2470等同名声明，不宣称这些后续错误已经运行）；把1404/1405条件计算写成目标宿主支持的显式if/else，再由harness验证。不能只改工作区而继续交付旧包。以新candidate_id重新冻结最终字节/dirty清单/manifest/catalog/配置，记录对原候选增量；若选择后续基线，先明确新增差异及受影响回归，不能直接把M6 r5称已接受基线。
- **验证方式**：仅驱动harness从干净隔离Store加载新包，parser错误0且真实应用首屏可操作；随后以隔离新造凭据检验可信三角色核心流程、正常/退回/失败重试与权威task/action/版本/附件回读。模型依照既有MiniMax授权走needs_model代理与OCTOSENSE_MODEL_ENDPOINT、总≤10次；不能改包后沿用旧digest/UI/model证据。重启/故障/并发动作缺口必须用授权范围内可复现驱动能力实现或如实保留BLOCKED，不能用源码probe通过代替。重新产生同字节截图/演示并复核材料和必需门槛。本审查方未修业务。
- **已闭合子项**：本地catalog/install_staged路线、实际识别/加载、写隔离/禁读/外联限制/自己的PGID回收已获独立实证。旧rc71/rc3不再阻塞。旧r4直接Popen方案退役，不能拿历史假PASS当新harness产品PASS。
- **NEEDS_ABRAM=no**：本地路径已可行，技术修复与MiniMax已授权；没有公开发布需求、没有402/欠费证据。

### D-M7-01 / D-M7-02 / D-M7-03 — 原子项保持CLOSED

精确冻结包check仍PASS；16项+外存自哈希一致；原64定义一一保留。不追加业务PASS，不把scan自答升级独立接受。新包变化后须重验。

### A-M7-01 — P2建议挂账，OPEN

- 文件：app/README.md:5,88–100,104–121。实际仍称B01闭合并给直接subprocess、错层级staging链接和旧/tmp链。触发是按当前入口找候选/启动；预期指向用户授权harness与真实FAIL状态。
- 根因：历史命令/结论未同步新路线；影响是误导复现，但本轮没有运行它，也不单因此FAIL。
- 改法/验证：链接改为../runtime；当前步骤使用harness请求；旧命令明确标不可执行历史；删无证据“已闭合”。按实际链接解析/渲染及当前报告读回，材料最后重冻。

### A-M7-02 — 原媒体脚本问题CLOSED；来源与能力措辞P2建议挂账

- 文件：release-materials/SOURCES.md:4,44,51；PRIVACY.md:11–15；测试transport catalog.json.entries[0].listing（S/store/local-mirror/catalog.json）。
- 实际/预期：旧显式bundle/app-data绑定、从未公开断言，以及旧catalog的B闭环完成/scan PASSED不能说明当前候选能力。包listing.json:4,28正确披露旧图与未通过；旧catalog仅隔离运输未发布，材料不能把它当最终当前发布catalog。
- 根因/影响：旧草案与运行方式不同，推断混成事实；当前发布草案仍未定稿。按用户裁决列建议，不因其独立判FAIL。
- 改法/验证：仅保留已核命令和此候选回执范围；如最终交付catalog则listing与包材料统一重新签名冻结。核实际文件与命令/hash，不需公网/媒体扩审。

### A-M7-03 — CLOSED

INTEGRITY.txt:33–54的16项和外存3189 B自哈希全部匹配。没有本轮篡改/重新删除私钥；复用既有离线签名，不生成/读取私钥，原keys/*.key为空。删除证据仅沿用历史，不伪称本轮执行keygen或删除。

## 相关既有用例逐项复核

以下是完整用例状态，不是局部子项；保留原64定义与原历史状态，额外L8-DV2不删。BLOCKED只用于本表具体白名单能力缺口；解析失败本身是FAIL，后续未执行是NOT_RUN，不以缺少旧环境权限笼统BLOCKED。

|编号|原定义|本轮状态|证据与适用范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|5个真实账号来源已获授权；本候选仍旧演示身份配置，无可操作登录首屏；未创建/核对可信独立会话，未访问原账号或凭据。|
|G0-C|唯一事实源、原子一致性、并发与恢复|NOT_RUN|官方Store重建/may_run子项PASS；业务任务/事件/回执原子性、并发及崩溃恢复未运行，不混用Store恢复和业务恢复。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|没有真实附件上传/读回/归属/失败恢复操作；两份合成损坏业务文件不是附件证据。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|提醒实际恢复/去重/跳回未运行；合成follow_ups保持原文，但应用parser前失败，无恢复业务证明。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|两个内置触点被调度，但业务区空白、没有创建key/task/action回执；不把无变化判幂等PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|BLOCKED|白名单无两个独立可信连接的并发调度接口；未执行竞争接单。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|BLOCKED|白名单无两个独立主体并发确认预约的调度接口；未执行并发/跨项目冲突。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|BLOCKED|白名单无断线/重连或SSE/选定平台替代路线的注入接口；未执行恢复。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|BLOCKED|白名单不能在任务/预约/事件精确写入间注入异常；未执行事务回滚。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|BLOCKED|请求只支持每场新目录，没有复用同盘业务数据重启进程/调度提醒作业的动作；未执行去重/旧作业恢复。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|本包被识别/复制到.running子项PASS；未打开或操作同一真实task_id、未回读业务结果；同盘重启没有白名单动作。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|未进行grant关闭/退出/到期/共享卡授权测试；现场景没有相应动作。不把退出进程或Seatbelt当业务撤权通过。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|未执行旧配对码/审批/poll_secret，亦无经独立验证的原生可信登录替代链；目标不删减、不默认N/A PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|冻结包enabled=false、provider/model为空，无MiniMax/http.fetch代理适配；真实请求0。相应模型业务未执行，不用工作区配置或静态探针替代。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|包/宿主/harness/请求/配置摘要已记录并可重跑；业务成功与失败模型场景未跑，不以源/hash记录判完整用例PASS。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|BLOCKED|三种--size请求得到相同2800×1718截图，当前内置动作未实现可验证的窄窗/150%文字设置；业务区另因parser失败不可测。 仅能力缺口，不引用agent沙箱rc71/rc3。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|NOT_RUN|本候选解析失败，未进入可操作业务UI；相应命令、权威回执/事实、失败恢复未执行。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|没有本候选2–3分钟演示及独立人员复述；实际空白截图和旧B媒体均不替代。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|FAIL|4/4实际加载后各17条parser错误，业务区空白；干净运行/可用首屏及继续操作入口失败。完整后续业务未执行。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|精确冻结包check rc0 PASSED；已有scan资料不等于本轮实际独立scan审阅通过，此子项NOT_RUN。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|来源/隐私/许可与指纹核对；本轮四张当前原生截图是空白业务区，没有成功关键图或2–3分钟完整演示。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|NOT_RUN|候选listing已披露旧图/未通过；旧离线catalog仍有旧B完成/scan宣称，app README仍称B01闭合。当前发布材料尚未定稿、未作最终提交内容实证；建议挂账不单据此判FAIL。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|没有本候选实际外部回执；保持GATES.external_delivery原UNASSESSED，未执行公开发布、收录或赛事提交，不能转移旧B回执。|
|P07|维护者商店收录结果|NOT_RUN|没有本候选实际外部回执；保持GATES.external_delivery原UNASSESSED，未执行公开发布、收录或赛事提交，不能转移旧B回执。|
|P08|赛事正式提交入口回执|NOT_RUN|没有本候选实际外部回执；保持GATES.external_delivery原UNASSESSED，未执行公开发布、收录或赛事提交，不能转移旧B回执。|

共64项：0 PASS / 6 FAIL / 6 BLOCKED / 52 NOT_RUN。准入、指纹、安装/加载、隔离/回收PASS子项已单列，不能借此升级整个业务/UI用例。

## 判定

- **最终结论：FAIL**，精确范围为M7-r4-worktree / r2冻结0.1.0-c的本地同版本发布准备。
- **本地准备**：FAIL；本地安装、加载、隔离/回收子项PASS；业务首屏解析失败。
- **外部发布（P06）**：NOT_RUN；原UNASSESSED保留，无本候选实际回执。
- **商店收录（P07）**：NOT_RUN；原UNASSESSED保留，无本候选实际收录结果。
- **赛事回执（P08）**：NOT_RUN；原UNASSESSED保留，无本候选实际赛事回执。旧B回执不转移。
- 必修：仅B-M7-01核心运行/同字节实证缺口；A01/A02建议挂账。对前序已挂账业务不无关扩修。
- 阻塞/未测：只用表中具体白名单能力不足记BLOCKED；其余真实业务/model/演示未运行为NOT_RUN，不能替代必需通过。没有harness ABORT，无rc71/rc3阻塞。
- 受影响回归：原D01准入、D02指纹、D03编号、A03自哈希保持CLOSED；实际宿主/running子项新增独立PASS；M0–M6历史独立结论不改、不借其静态总数放行M7。
- 门禁：GATES仅M7 status/审查字段/审查历史更新，review_report指向本报告；作者host_started/host_runs/blockers/test_counts等历史字段不覆写，以review_summary区分当前结果。原ACCEPTANCE.json保持原历史来源，本报告与M7.review_acceptance提供当前原生64项结果。
- 不允许进入下一模块；本模块是最终阶段，也不执行发布、赛事或上架。
- 留在本模块：构建方按B01具体清单修最终候选解析并重新冻结；提交受影响业务/模型/材料同版本harness请求，驱动执行后再独立复审。无发布授权申请，无账单阻塞。

STATUS=FAIL
NEEDS_ABRAM=no
