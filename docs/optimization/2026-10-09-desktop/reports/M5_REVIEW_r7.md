# M5 独立 Review r7

**最终结论：FAIL。B-M5-01 的原生解析/空白界面故障已关闭；D-M5-04 的附件恢复实测失败，D-M5-05 新恢复分支存在不可信重建基准的源码缺口。8 场 CLEAN 只证明隔离与回收，不证明完工或独立验收成立。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无子代理。
- candidate_id / base_candidate_id：`M5-r6-worktree` / `M5-r5-worktree`，根据用户交接、r6实施报告、候选清单及请求联合定位，不按mtime。HEAD=`8d730569546cb57310944bb299695134df773b9d` 加既有未提交改动。
- main SHA-256=`4da13507ec78218d627ba91cab8569c47a77d0dc4d5d195ab9fb9e10a8266492`，488510字节；bundle digest=`541349cc4addb06c9544ca9d5ad7a228d206b2cfc4cc1dfc093346fc50e2a7ac`。第1段冻结、第2段及写门禁前业务源/manifest/配置/身份配置/候选/宿主一致；8场安装与运行副本一致。
- 作者报告：`reports/M5_IMPLEMENTATION_r6.md`；清单：`runtime/optimization/2026-10-09/M5/r6/CANDIDATE.json`；作者原生证据：`M5/native-runs/build_r1_2104_REQUEST_build_r6/`，仅参考，未代独立复现。
- 前置：**M4=FAIL / M4-r7-worktree / M4_REVIEW_r8.md**，没有已接受M4 PASS候选；按用户前序挂账裁决继续本模块，不伪造前置、不修M4。
- 受影响差异：相对M4 r7冻结main，改变函数仅load、_strIndexOf、m5_reconcile_attach_index、submitCompletion、rejectCompletion；实际diff/行号保存在S。相对上一轮M5冻结的更多差异含前序已交接修复，不把它们全归本轮M5修复。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 原生运行：驱动在agent沙箱外执行本审查请求，02:33:26–02:35:16 +08:00，8场CLEAN、quit_http、rc0、无ABORT。审查者未自启launcher/sandbox-exec/pgrep，未使用osascript、辅助功能或其他自动化。
- 实际环境/模型：每场独立HOME/app-data/cache/tmp/logs及Seatbelt；全部needs_model=false、模型调用0、无model_proxy_stats、无欠费。当前工具未提供主会话Router路由/指定主审型号核验与createdAt/title接口，未声称切换或命名。
- 已读：第1段AGENTS/CONTEXT/00/01/02/M5/04、上一轮缺陷/交接/相关源码与用例；第2段本请求全部summary/result/profile/日志/denials/MANIFEST、8张请求PNG、1张不同的part及7张同字节part副本、权威盘及直接相关源码。不做无关扩审。
- 已运行范围：离线官方hub verify（第1段rc0）、驱动独立8场当前包加载/输入能力探针/恢复启动、证据一致性审计及真实盘读回。Python审计不执行Splash业务。
- 未运行范围：实际选文件上传→保存后注入→两个业务入口拒绝、可信独立登录/自验/经理理由、正常链/退回链、同盘重启及精确提交点故障；区分下文NOT_RUN与白名单确实无法表达的BLOCKED子项。
- 置信度：候选/隔离/解析关闭/实际索引不变与错误路径事实 **高**；字段缺失与错误值传播的具体VM细节 **中**；D05源码基准缺口 **高**、原生坏件放行 **未知**；未执行业务链 **未知**。

## 证据索引与独立核对

- **H**：`runtime/optimization/2026-10-09/M5/native-runs/review_r1_2104_REQUEST_review_r1_2104/`，驱动原证据，只读保留。
- **S**：`runtime/optimization/2026-10-09/M5/native/review_r1_2104/`，冻结、diff、fixture、seed、离线验签及审计。
- **R**：`M5/native/REQUEST_review_r1_2104.json`；**N**：`M5/native/REVIEW_NOTES_r1_2104.md`。
- **A**：S/`native-evidence-audit.json`；复核脚本S/`audit_phase2.py`。运行`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r1_2104/audit_phase2.py`，rc0。**4568项证据一致性检查通过，不是4568项业务测试通过。**

1. H/MANIFEST.sha256 **1342项**逐一核SHA：缺失0、摘要错误0、重复0、未列入0。summary.request与R相同，harness/template摘要匹配，summary场景verdict/exit/wall_s与result相同。
2. 8场profile_probes.ok=true，apply rc0，外写探针被拒且created=false，5个禁读探针均被拒；pre/post_pgrep均rc1/class=NONE/out空，pgid_members_after=[]；quit_http=ok、host_returncode=0、CLEAN。没有以agent环境rc71/rc3作BLOCKED理由。
3. 8个profile逐字节按模板、当前场目录和控制端口重建并匹配SHA；环境路径均在本场。原HOME `.octosense` mtime前后一致、library_scan_new_or_modified=[]。隔离与回收 **PASS**。
4. 记录的写入清单首场128、其余各129项，逐项唯一、文件存在且留在本场目录。此数字包含宿主文件，不等于业务操作数。完整denials读取并按harness算法重算，全部相同；有remote:*:443、Metal系统缓存、/dev/dtracehelper被拒记录，未发现据此成功外联/外写。没有模型代理/统计文件。
5. 8张请求PNG均存在，SHA与result/MANIFEST一致，尺寸**2800×1716**；逐张查看，业务头部/任务列表/空态已渲染，全部未登录；登录输入行被裁切，未显示附件/完工/验收表单。7个part.png与相应主PNG同字节；reject_marker_only的part不同，另行查看仍为同一未登录业务空态，其自身摘要匹配MANIFEST，不要求中间帧与最终帧相同。不能把请求1280×800当布局验收通过。
6. 8场完整host.log已读取，字节数、tail、markers从原文重算一致；当前488510字节main实际eval、launch-hub成功，无上轮parser错误和panic。安装及.running main匹配冻结源；model_config/identities一致；accepted catalog与验签mirror一致，entry manifest与安装manifest一致、digest正确。digest_seen_in_seed=true、digest_seen_in_host_log=false符合实际。**B-M5-01解析/空白子项PASS，R-M5-01准备错误保持关闭。**
7. 8场tasks.json、全部本场m5-test原附件/索引/新源均与seed字节相同。7个恢复场虽然state报告“重建索引1”，实际目标index不变；均新增本场app目录下 **`[Error:NotFound]/evidence_index.json.tmp`（0字节）**，没有正确索引落盘。state不包含attach_sandbox_root_abs、attach_items、m5_last_round；events/actions为`[[]]`，没有m5_index_reconcile或业务final回执。恢复 **FAIL D-M5-04**，而不是BLOCKED。
8. 本次seed绝对根与实际run目录 **8/8完全匹配**，已经排除作者4场目录钉扎不一致的问题。本次恢复失败不能归因于审查夹具路径错误。
9. 原件205字节SHA=`7aeec0f07db331d5e6a18de6823b81d7cc0de0704b91b19103bf1073417899d1`，变更件SHA=`ea448a8389a3f520008b2b1d7775f68ec3b5f4d08bc7bbbae4881594e38a7265`；96个0x03变0x04，首尾保留，源码算法分析FNV均`e14280da`。collision场canonical仍缺失，索引仍空；**未发生实际READY或完工/验收放行，不把算法分析当原生漏洞利用成功**。
10. 本轮没有生成私钥；第1段复用当前digest的已签测试Store并独立hub verify。构建两把私钥删除记录本段复查exists=false，keys目录空。没有公开签名、发布、listing、push、Issue、消息或部署。没有读真实明文凭据/模型密钥、造SESSION或改原始业务数据。

## 必需检查

|检查|独立操作步骤/期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/运行包|冻结当前候选并核accepted/installed/.running|8场内容与digest一致|PASS|S快照/diff，A|
|原生解析/业务渲染|冷启动、日志零parser、真实客户区|8场零parser、业务列表/未登录区域出现|PASS，限B01子项|H各log/PNG，A|
|隔离与回收|内核探针、目录/profile/进程核对|全部满足，无ABORT|PASS|8个result/profile/denials|
|提交后旧索引恢复|task round3、index0、view1；恢复权威round|task仍round3，index仍0，round视图字段消失；错误路径空tmp|**FAIL D04**|submit_round3_stale_state运行盘|
|退回标记恢复|task/index同round0但marker缺失应修平|index缺marker保持；仅“重建1”提示，无事件|**FAIL D04**|reject_marker_only运行盘|
|缺项与旧证据保留|完整件应重建可读索引并保留孤儿/外来|原字节/旧项保留；新项没有落目标index，orphan/foreign计数0|保留原字节PASS；恢复**FAIL D04**|rebuild_intact_orphan盘/A|
|坏/缺/异任务恢复负例|正确索引记录失败状态/归属，不能元数据READY|目标index始终未修；未产生可核验新项|恢复FAIL；两个业务入口NOT_RUN|3场负例盘/A|
|真实新上传后双入口反例|自行新文件，经应用保存后注入，再完工/验收均拒|另造字节与冷启动夹具；未实际上传、提交或验收|NOT_RUN；运行中变更通道子项BLOCKED|S fixtures、R/schema|
|可信独立验收|多角色同ID不得自验，经理无理由拒/有理由成功|无可信登录；当前宿主拒type/key|可信文本输入通道BLOCKED；业务命令NOT_RUN|cold_input_probe/log:39–40，8张PNG|
|正常链/退回链/终态|同任务真实填写/上传/完工只待验，独立验收；退回补充再验|均未执行，没有权威业务回执|NOT_RUN；文本输入通道BLOCKED|8场actions/events/PNG|
|重启附件读取/失败恢复|同盘跨进程恢复再打开/重试，精确写点注入|冷启动恢复实际失败；本schema不表达同盘重启/写点注入|启动恢复FAIL；精确通道BLOCKED|D04盘、schema、R|

**BLOCKED只限已证明的通道缺口**：cold_input_probe host.log:39–40明确`unknown --test-action 'type:reviewer-noncredential-probe'`、`'key:Tab'`；schema允许名字不等于当前发行宿主实现。当前schema仅场景启动前seed，每场新目录，没有运行中对应用刚保存副本变更、精确writer/commit中断、共享同盘跨进程重启或迟到模型交错调度。上述动作子项不能用当前白名单表达。没有harness ABORT；解析/恢复等已执行项按PASS/FAIL，未执行命令按NOT_RUN。解阻需要驱动/宿主提供已支持的可信控件输入与受控注入/同盘重启，维持现有Seatbelt与秘密边界，不需Abram新增授权。

## 缺陷与闭合

|编号|本轮闭合状态|
|---|---|
|B-M5-01|CLOSED：当前固定宿主8场零parser，业务区不再全空白；不签收可信登录或完整流程|
|D-M5-01|内容出口/canonical源码子项保持；真正打开/下载/失败重试NOT_RUN|
|D-M5-02|本轮内核隔离PASS；M5根/初始化错误影响核心，并入D04；没有发现成功越界访问|
|D-M5-03|completion固定集合逐成员检查保持；双入口实际拒绝NOT_RUN，跨任务恢复没有可核验新项|
|D-M5-04|**P1 OPEN / FAIL**，新增对账未使正确索引/轮次/审计恢复成立|
|D-M5-05|**P1源码缺口OPEN**，新增丢canonical分支弱指纹重建基准；原生放行NOT_RUN，已有全文保护改善保留|
|D-M5-06|作者约束子范围保持；本轮内核隔离/回收PASS；第1段审查读取偏差另披露|
|R-M5-01|CLOSED，正确accepted catalog、本候选实际进入解析与运行|

### D-M5-04 — P1 / 必修 / OPEN：附件恢复未落权威索引，失败被“对账”结果覆盖

- **文件行**：`app/bundle/main.splash:52`默认STATE未声明M5字段；`:483–501`只加载偏好；`:1368–1387`、`:6515–6535`依赖缺字段==nil初始化；`:2489–2504`根返回；`:6915–6942`writer；`:6964–7104`reconcile；`:7401–7409`轮次；`:862–870`启动审计的身份闸。
- **触发**：R/submit_round3_stale_state与reject_marker_only任一冷启动。seed与run根本轮匹配，current bundle由同发行宿主实际执行；不需要可信用户操作即可进入load对账。
- **实际**：task round3/index round0仍分裂；退回标记仍缺；所有7场恢复目标index不变，却报告“重建索引1”。输出出现`[Error:NotFound]/evidence_index.json.tmp`空文件；state无附件根/索引/轮次，事件没有m5_index_reconcile。完整件+孤儿/外来场也没有恢复新项。这是原生读回失败，不是仅作者声称或静态怀疑。
- **预期**：启动对账读当前获准app-data，依据已提交task/completion恢复固定集合与单调轮次、保留旧证据并持久审计；失败留明确可对账状态，不能以计数提示成功。
- **根因**：M5字段未在默认STATE显式建立，loadViewState不恢复它们；缺字段被当nil的假设没有产生预期结果，实际错误值进入路径（事实高置信，具体VM缺字段比较语义中置信）。reconcile也忽略writer返回值而覆盖状态，未重建m5_last_round；marker-only改动只增加t_repaired，保存条件仅看repaired_round/rebuilt_items，单独标记变化可能不保存；启动未登录时saveEvents拒持久化。
- **影响**：核心硬1/4/5、G0-D/T21/T22/T28/U06/U07失败，退回后不能可靠复用、新完工轮次不可恢复；状态提示与盘事实分离。
- **证据**：H/submit_round3_stale_state/.../tasks.json、state.json、m5-test/evidence_index.json、`[Error:NotFound]/evidence_index.json.tmp`；reject_marker_only同盘；其余5场恢复盘；A/scenes与S/冻结源。原bytes全部保留，不能将“不变”称为正确拒绝。
- **具体改法**：只修M5恢复依赖：在STATE声明M5所需字段，使用当前发行宿主实测的缺字段/类型检查；附件根从可信host app-data确定且限制到本场，采用正确fs路径语义，不使用旧r4硬编码根、不放宽profile。以已提交completions历史重建last_round，不从UI偏好认定权威轮次。统一dirty标记涵盖round/marker/索引项；writer返回失败须上抛，成功须读回实际目标后才提示。恢复审计用受控系统来源持久记录，不造用户会话、不绕过一般业务写权限。
- **验证方式**：先同宿主harness小probe证明M5字段/根/fs读写/rename原语；再复跑本R的round3、marker-only、完整件+孤儿/外来输入，回读正确index及审计、错误目录不再出现。经驱动受控注入submit/reject各自index写失败、commit失败、commit后中断与同盘重启；重试无重复/无旧证据丢失/新round递增。禁止用Python移植替代这些证据。

### D-M5-05 — P1 / 必修 / OPEN（源码）：canonical缺失时用弱指纹认可现存字节为新原件

- **文件行**：`main.splash:7022–7028`补canonical，`:7031–7038`置READY；弱指纹`:6774–6809`，尤其`:6802–6804`非ASCII/控制字符仅按位置fallback。
- **触发**：task登记原件，但index/canonical缺失，stored中段控制字符变更，尺寸/首尾不变；进入新增reconcile的丢canonical分支。
- **实际源码**：只有尺寸与m5_fingerprint相同就把当前stored写成canonical，并在内存中立刻令canon_text=cur_text；既未证明当前内容等于原件，也未读回成功写出的canonical。96个0x03→0x04在两个字符表均不命中，按当前算法同指纹`e14280da`，真实SHA不同。此分析是明确源码反例，不是Native READY结果。
- **本轮原生实际**：collision场旧坏件保留、canonical未创建、目标index空；先受D04入口/存盘故障影响。**未观察到坏件通过验收，攻击/双入口运行NOT_RUN**。没有把首尾/尺寸相同或Python分析升级为宿主全字节实证。
- **预期/影响**：失去可信内容基准时应拒绝/未可信态，不能用不区分这些字节的指纹把现在的文件重认作原件。该分支削弱上一轮已加的完整canonical比对，直接影响核心硬2“损坏证据不得通过”及READY来源；属于本轮新增恢复逻辑的必要回归，非扩审新功能。
- **根因**：将“现存文件自洽”当“与已提交原件一致”；使用位置型fallback的弱摘要恢复完整性基准，且吞掉canonical写失败。
- **证据**：S/independent-byte-analysis.json、fixtures/reviewer-original.bin与reviewer-changed.bin真实205字节、H/rebuild_no_canonical_collision的stored/canonical缺失/index/state、冻结函数。原生字节读取语义最终仍需同宿主验证。
- **具体改法**：丢失canonical时仅从可信不可变原件或已提交的可靠全字节摘要验证恢复；无充分证据直接保持CORRUPTED/未可信并提供补证出口。最小安全修法可取消弱指纹自动重建分支。任何canonical写入必须检查并读回，不以cur_text赋值替代落盘。
- **验证方式**：D04修复后，同宿主先实际上传保存本轮新文件，分别造同尺寸控制字节/NUL/UTF-8/二进制损坏、canonical缺失/写失败；核目标字节与固定completion集合，再从可信独立主体复跑完工/验收两个入口，均拒绝。完整件缺index的合法恢复应仍能运行。

### 建议挂账 / 证据限制（不新增FAIL依据）

- 登录行裁切属于前序B-M4-01相关可操作性，8图中仍出现；不代修M4。可信登录若确被它阻断，下一修复只处理必要依赖并实测，不把它当普通视觉美化。
- 作者请求钉扎build_r6而驱动输出build_r1_2104，作者静态/移植通过不能补原生恢复。建议更新交接证据适用范围；本次独立已纠正路径，不增产品缺陷编号。
- boot把空JSON数组迁为`[[]]`是已有M2路径的本轮观测；保留证据，不扩修M2或据此伪造原final动作。M5审计确实未持久化已计入D04。
- 第1段初批读取项目外memory/skill文件偏差在N披露；发现后停止，无外写。第2段显式读取/写入仅在本项目，不以该记忆认定当前事实。

## 硬验收与既有用例

|硬验收|最终精确状态|
|---|---|
|1 真实选择/重启重新打开|恢复子项FAIL D04；真实上传保存打开NOT_RUN，输入通道BLOCKED|
|2 坏/缺/隔离/异任务/无权/旧轮双入口拒|D05源码完整性基准FAIL；实际两个业务入口NOT_RUN；保存后变更通道BLOCKED|
|3 只待验/可信独立最终验收|可信文本输入通道BLOCKED；业务动作NOT_RUN，守卫源码保持|
|4 退回历史/新轮/明确引用|恢复子项FAIL D04；原旧字节/历史保存子项PASS；实际退回链NOT_RUN|
|5 打开/失败重试/表单/终态/正常与退回链|渲染入口子项PASS B01；恢复FAIL D04；完整业务NOT_RUN，特定驱动通道BLOCKED|

|用例|本轮结论/适用范围|
|---|---|
|G0-D|同digest本地安装/隔离/解析PASS；实际附件恢复FAIL D04，真实选择/保存/打开NOT_RUN|
|T18|未登录UI未暴露seed任务事实的子项PASS；可信列表/搜索/事件/附件授权NOT_RUN，输入通道BLOCKED|
|T19|固定集合守卫源码保持；D05源码基准FAIL，损坏/缺失/异任务/隔离双入口及实际下载NOT_RUN|
|T20|可信自验/多角色/经理理由/只待验业务NOT_RUN；文本输入通道BLOCKED|
|T21|启动恢复FAIL D04；旧文件保留PASS；完整退回→新completion/round→验收NOT_RUN|
|T22|独立冷启动对账FAIL D04；精确writer/commit间注入与同盘重启通道BLOCKED，实际提交点异常NOT_RUN|
|T28|当前包实际原生加载PASS；同task恢复FAIL D04；业务操作/同盘再开附件NOT_RUN|
|T31|终态守卫源码保持；真实终态只读/再验/关联新故障NOT_RUN，不扩前序取消/预约|
|T35|证据改变导致旧确认/建议失效NOT_RUN；迟到模型/交错调度通道BLOCKED；模型调用0|
|U03|同task三可信角色事实/按权操作/禁止自验NOT_RUN；可信输入通道BLOCKED|
|U06|旧盘字节保留PASS；进度/完工/验收/退回真实区分NOT_RUN；恢复FAIL D04|
|U07|启动恢复FAIL D04；重复/丢回包/冲突/离线业务NOT_RUN；精确故障/同盘恢复通道BLOCKED|
|U08|原生未登录/无可见任务空态出现PASS；附件失败/重试/无权出口NOT_RUN；错误恢复提示FAIL D04|
|U11|真实业务客户区渲染PASS；type/key确被宿主拒；登录后滚动/输入/面板稳定性NOT_RUN，输入能力子项BLOCKED|

## 判定

- 最终结论：**FAIL**，非“基本通过”。范围为交接的M5-r6-worktree、本固定宿主、8场独立请求及明确源码回归。
- 必修：**D-M5-04**恢复初始化/真实存储/失败传播/轮次与审计；**D-M5-05**新增丢canonical时的弱基准分支。B-M5-01解析/空白子项已独立关闭，不再要求重修同一保留字问题。
- 阻塞/未测：仅白名单确实不能表达的可信文本输入、保存后变更、提交点故障、同盘重启/模型交错标BLOCKED；业务命令未执行记NOT_RUN。CLEAN且索引错误不标环境BLOCKED。
- 前序回归：当前M4 helper的解析依赖已针对性验证零parser；M4整体PASS没有成立，其余前序账保留。
- 门禁更新：仅GATES.json中M5 status及review_* / reviewed_* / review_history字段；review_report指向本报告，保存上一轮及完整before-final快照。实现候选/报告/自测/他模块和external_delivery保持。历史ACCEPTANCE.json未覆盖，本轮原生各项记录在GATES.M5.review_acceptance。
- 不允许进入下一模块。由Kimi-K3只按上述两编号修M5必要依赖；驱动补齐受控通道并回交同候选真实正常链、退回链、两个入口反例及失败恢复，重新独立Review。
- NEEDS_ABRAM=no：身份/provider/离线签名已经授权，本轮0模型调用，无公开发布或欠费阻塞。

STATUS=FAIL
NEEDS_ABRAM=no
