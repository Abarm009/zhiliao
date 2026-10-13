# M5 独立 Review r6

**最终结论：FAIL。当前候选在选定原生宿主解析失败、业务窗口空白；D-M5-04 共同提交与重启恢复未闭合。8 场 CLEAN 证明隔离/回收通过，不证明附件或独立验收通过。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-11，Asia/Shanghai；没有子代理。
- candidate_id：`M5-r5-worktree`；base_candidate_id：`M5-r4-worktree`。依据 GATES 与 r5 作者交接定位，不按 mtime 选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d` 加既有未提交改动。冻结 main SHA-256=`c683c7a034c8dbdd8c82560332418933482a01b953b0fabea9afeead1663f1d2`，395510 B、8450 行。作者未提供内容 SHA，由本审查独立冻结；没有把 HEAD 当全部未提交差异摘要。
- 审查快照：第1段开始、结束、第2段核查时源码/配置/manifest/宿主/清单/台账一致；8 场 `.bundles` 安装副本及 `.running` 运行副本 main 均与冻结摘要一致。
- 作者报告：`reports/M5_IMPLEMENTATION_r5.md`；清单：`runtime/optimization/2026-10-09/M5/r5/CANDIDATE.json`；作者证据：`M5/r5/results/r5-source-checks.json`、`r5-probes.json`。
- 前置：`M4-r5-worktree / M4_REVIEW_r6.md / FAIL`，没有接受的 M4 PASS 候选。本次用户明确前序挂账，因此继续审 M5；不把原文 M4 PASS 前置说成满足，不代修前序。受影响的原生解析入口已针对性复验，故障仍存在。
- 真实运行：驱动于 16:01:24–16:03:22 +08:00 在 agent 沙箱外执行本审查请求；8 场均 quit_http、宿主 rc0、CLEAN。审查者未启动 launcher、sandbox-exec、pgrep，不用辅助功能/osascript/自动化。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 环境 / 路由：每场独立 HOME/app-data/cache/tmp/日志，Seatbelt。当前主会话 Router、指定 gpt-6.1-sol 和 createdAt/title 无可用核验/修改接口，未声称切换或改名。
- 阅读范围：沿第1段 CONTEXT/AGENTS/00/01/02/M5/04、上一轮 M5 r5 Review、r5 实施与清单、D01–D06 受影响源码、相关 T/U 定义；第2段只核该请求、证据与上述缺陷，不做无关扩审。
- 已运行范围：独立离线签名/verify/install_staged/Store 重建，8 场原生加载/点击探测/capture/回收；证据摘要、profile、日志、实际字节与状态核对。没有原生业务提交、验收、退回、可信登录或模型调用。
- 置信度：候选一致性、原生解析失败/空白窗口、隔离回收、D04 源码恢复缺口 **高**；具体解析 token 根因 **中**；实际附件/可信验收/正常与退回链效果 **未知**。

## 证据索引

- **H**：`runtime/optimization/2026-10-09/M5/native-runs/review_r2_1309_REQUEST_review_r2_1309/`，驱动原证据，只读未改。
- **S**：`runtime/optimization/2026-10-09/M5/native/review_r2_1309/`，独立快照、diff、函数、seed、离线 Store 与审计记录。
- **R**：`runtime/optimization/2026-10-09/M5/native/REQUEST_review_r2_1309.json`。
- **N**：`runtime/optimization/2026-10-09/M5/native/REVIEW_NOTES_r2_1309.md`。
- **A**：S/`native-evidence-audit.json`；主体核查可用 S/`audit_phase2.py`复算；追加核查包括运行副本/accepted catalog/退出/无代理/手工看图记录。A 的一致性 PASS 不等于业务 PASS。

## 原生证据逐项核对

|场景|隔离/回收|实际入口|业务数据/命令|
|---|---|---|---|
|fresh_intake|PASS|FAIL，5 条 parser 错误，空白窗口|8 个业务 seed 文件不变；真实新上传 NOT_RUN|
|corrupt_submit|PASS|同上 FAIL|12 个文件不变；完工坏件拒绝 NOT_RUN|
|corrupt_accept|PASS|同上 FAIL|12 个文件不变；验收坏件拒绝 NOT_RUN|
|missing_submit|PASS|同上 FAIL|11 个文件不变；完工缺件拒绝 NOT_RUN|
|missing_accept|PASS|同上 FAIL|11 个文件不变；验收缺件拒绝 NOT_RUN|
|foreign_submit|PASS|同上 FAIL|12 个文件不变；完工跨任务拒绝 NOT_RUN|
|foreign_accept|PASS|同上 FAIL|12 个文件不变；验收跨任务拒绝 NOT_RUN|
|stale_index_recovery|PASS|同上 FAIL|12 个文件不变；启动对账/恢复未运行|

1. H/MANIFEST.sha256 共 **1331 项**，逐文件重算，摘要错误0、缺失0、未列入0、重复0。summary.request 与 R 完全相同，summary.harness/template SHA 与当前文件一致，各 summary 场景记录与 result 的 verdict/exit_method/wall_s 一致。全部 result/log/profile/captures/denials 都包含在核查范围。
2. 每场 `profile_probes.ok=true`、apply rc0、外写探针被拒且未创建；5 个黑名单读探针均被拒。pre/post_pgrep 均 rc1、class=NONE、out为空，pgid_members_after=[]；CLEAN、quit_http、quit_http=ok、host_returncode=0。没有 ABORT；没有使用 agent 沙箱 rc71/rc3 作 BLOCKED 理由。
3. profile SHA 重算匹配，按模板及实际场景/控制端口重建后逐字节一致。HOME/CFFIXED_USER_HOME/app-data/cache/config/data/tmp/Metal 缓存/hub-mirror 等路径都在各场新目录。原 HOME `.octosense` mtime 前后一致，library_scan_new_or_modified=[]。内核隔离及回收本轮 **PASS**。
4. 每场 files_written_count=123，实际列表123项、无重复、文件存在且路径留在各场目录。该数字是 harness 记录的写入清单，不是123次业务操作。业务 task/state/index/events/actions/账号表及附件均与各自 seed 摘要相同；原 bytes/坏件/canonical/缺件及跨任务归属负例仍是预置输入，**不变不证明拒绝命令**。
5. 8 张 PNG 全部存在、SHA 与 captures 和 manifest 匹配，尺寸均 **2800×1718**；逐张查看，均有 “OctoSense Repair” 窗口标题，但业务客户区为空白。没有登录、任务、附件、验收/退回表单。请求1280×800/980×760不等于这些业务布局已经验收。
6. 全部 host.log 已读取；host_log_bytes/tail/markers 从原文重算一致。每场有 `wm: launched hub:octosense-repair`、395510 B 的 main eval、两次 tap 调度和随后809 B 的 eval，无宿主 panic。但每场同时有 **Expected )×3、Expected } not found×2，内部位置5285:26/28**。宿主 rc0/无panic是退出证据，不是脚本解析通过。
7. 每场 accepted `apps/catalog.json` 存在，与本轮 verified mirror 相同；catalog entry manifest 与已安装 manifest 一致，digest=`b43787bd4f7f7e4cf3ff699059aabdef230da4be0f704cf74157cd3b4e657936`。安装及 `.running` main 全部匹配冻结源码。digest_seen_in_seed=true、digest_seen_in_host_log=false 与实际一致。**上轮 R-M5-01 catalog 缺失错误关闭；本轮候选确实进入原生解析器，业务程序没有解析成功。**
8. sandbox_denials 完整文本已读，逐条汇总重新计算与 result 一致；包含 remote:*:443、Metal 系统缓存、/dev/dtracehelper 被拒尝试，没有据此声称成功外联/外写。profile 仅允许本机控制口；全部 needs_model=false，没有 model_proxy/model_proxy_stats 或代理文件；真实模型请求 **0**，billing_error=null。
9. 离线 verify/install_staged/Store 重建/may_run 本段证据继续有效，源/config摘要不变。只针对测试副本 digest 生成签名，不公开发布/上传/上架；两把测试私钥删除记录逐项 exists_after=false，本段复核 keys 目录为空。原始业务 manifest 未改。
10. 隔离账号另造口令与慢哈希，5 个 ID/角色/技能与只读真实账号表契约一致，`identity-contract-check.json`。没有读明文凭据/provider密钥、伪造 SESSION 或把 state.actor 当认证；没有操作原始业务数据。真实账号/provider来源已裁决，不是新授权阻塞。

## 必需检查

|检查|独立操作/期望|实际|结果|证据|
|---|---|---|---|---|
|候选/新增差异/宿主一致|冻结 r5，核签名安装/实际运行副本|全部一致；7个相关函数改动可定位；M4仍FAIL|候选一致性 PASS；前置不满足但按用户挂账|S/start-snapshot、diff、A|
|隔离与回收|指定探针/进程/profile/路径全部满足|8场全部满足，无ABORT|PASS|H各result/profile/denials、A|
|原生当前入口|加载业务程序并渲染登录/任务/UI|8场实际解析错误与空白客户区|**FAIL B-M5-01**|8张PNG、日志、实际运行副本|
|独立文件保存及坏/缺/异任务双入口|新上传保存后注入，完工与验收均拒绝|另造241 B文件并在保存测试副本造6组反例；程序解析失败，没有真实上传或双入口命令|NOT_RUN；源码改善不代运行|S/fixtures/independent-bytes、H|
|固定集合与旧证据/新轮|查每个引用而非readyCount；退回显式复用与新轮|固定集合守卫源码保持；真实链未执行|NOT_RUN；D04恢复源码FAIL|traces/seed、H|
|可信独立验收|可信会话禁止自验，经理无理由拒/有理由可验|无可信登录，无业务控件；标签/actor/预置完工不是会话|本轮 NOT_RUN；输入白名单能力子项 BLOCKED|PNG/log；下文通道说明|
|正常链与退回链|真实填写/上传/提交只待验/独立验收；退回补充再验|主程序解析失败，未发生业务动作/权威回执|NOT_RUN，入口FAIL|H、A|
|重启读取/失败恢复|同盘重启校附件字节/固定集合/任务/回执，并重试|8场都是新盘；stale仅启动负例未运行业务；源码共同恢复未闭合|D04源码FAIL；实操NOT_RUN；受控通道BLOCKED|traces/schema/fixture、H|
|实际打开/失败/重试/终态只读|真实控件和实际内容出口可用|8场均无业务UI，tap只有宿主调度|NOT_RUN；入口FAIL|8张PNG/log|

**BLOCKED 精确范围**：没有 harness ABORT。只将当前 schema/固定宿主白名单确实无法表达的可信文本输入、运行中对“应用刚保存的副本”变更、writer/commit中断点、共享同盘重启和受控迟到模型交错列为 BLOCKED 子项。固定宿主此前 `M2/native-runs/review_r1_1309_REQUEST_review_r1_1309/tmp_write_failure/logs/host.log:40,42` 明确报 unknown `type:`；schema 收录 type 不等于实现它。本次普通 launch/taps/capture 已执行，入口故障是 **FAIL**，依赖的业务检查是 **NOT_RUN**。技术解阻须由驱动提供已支持的可信控件输入、同盘重启/注入机制，仍在原隔离与白名单授权下运行；不能改用 osascript/辅助功能或预装会话。无需 Abram 新授权。

## 上轮缺陷闭合

|编号|本轮判定|精确范围|
|---|---|---|
|D-M5-01|既有内容出口源码子项保持；完整原生NOT_RUN|open新增canonical检查；未签收实际打开/下载/错误/重试|
|D-M5-02|绝对根源码子项保持；本轮内核隔离PASS|访问/链接/根篡改实际业务未跑；没有发现成功越界读写|
|D-M5-03|固定集合源码闭合子范围保持；实际两入口NOT_RUN|completion固定ID/摘要与逐成员守卫，不因readyCount放行；6负例未实际调用|
|D-M5-04|PARTIAL，**P1 OPEN**|tmp+rename、bool传播/提示已改善；启动旧索引覆盖与共同恢复未闭合|
|D-M5-05|PARTIAL，真实附件验证未闭合|全文保存/canonical比对源码改善认可；不再指称仍size-only；发行宿主尚无法运行到两个入口。相关M5解析依赖见B-M5-01|
|D-M5-06|既有作者约束子范围保持；本轮隔离/回收PASS|没有本轮外写/读禁区成功证据；原生只由驱动执行|
|R-M5-01|CLOSED|本轮补accepted catalog，实际main进入解析；不追认上轮成功|

## 缺陷与具体修复要求

### B-M5-01 — P1 / 必修 / OPEN：当前程序原生解析失败，阻断核心桌面链

- **文件行**：`app/bundle/main.splash:5281–5283` 的 `m5_fnv_mix_byte` 是相关疑点，函数与前序故障候选同内容；实际日志坐标 **5285:26/28**，不是直接把它当源文本5285行。完整 main 的解析失败是实测事实。
- **触发**：用 R 任一场新隔离 Store（同digest、accepted catalog、安装/运行副本匹配），经指定宿主 launch-hub/capture。
- **实际/预期**：本轮8/8场五条parser错误、空白客户区。预期能显示登录/任务/附件/完工/验收，实际无法进入任何M5业务步骤。
- **根因**：当前完整脚本不被固定发行宿主解析器接受；精确 token/坐标映射仍需同宿主最小probe。不能从日志直接断言“XOR不支持”或“改某一hex常量必好”：资料parser有bitwise语法，源码与实际发行版本须核实。入口失败置信度高，具体语法根因中。
- **影响**：硬1–5与G0-D/T28/U11等核心入口受阻。这是前序 B-M4-01 关联的 M5 函数依赖，本次只复验确实阻断核心的项，非无关扩审。
- **证据**：H/fresh_intake/logs/host.log:45–49；其余场各5条同坐标错误，见A/parser_error_lines；8张真实PNG；8个`.running`同摘要副本；S/source-traces/m5_fnv_mix_byte.splash。
- **具体改法**：构建方仅定位并修最小解析依赖；以同宿主harness最小语法probe验证数字/bitwise表达式及报错映射，再重签当前digest隔离副本复跑完整bundle。不能用Python翻译、别的VM或删验收代替。
- **验证**：harness日志无parser错误，真实客户区显示登录/任务/附件；然后运行可信人员完整正常/退回链和两入口负例，回读权威状态与回执。只修解析后见到窗口不算M5验收完成。

### D-M5-04 — P1 / 必修 / PARTIAL：单索引原子写与错误提示改善，任务/索引重启恢复仍分裂

- **文件行**：`main.splash:5426` writer、`:5452–5460` loader及直接替换；`:6199–6213` submit成功commit后索引写/失败提示；`:6454–6467` reject同类路径；`:997–998`启动加载。
- **触发**：submit或reject任务commit成功后索引tmp/rename失败，或两次持久写之间中断，再重启。
- **实际/预期**：writer返回bool、调用方失败不再显示旧成功串，这是已闭合子项。但loader仍无条件以旧 `evidence_index.json` 覆盖state.attach_items；没有task/completion/version/动作结果选择或共同恢复记录。预期恢复一致的固定集合、轮次、task与回执，无法恢复时可明确对账并安全重试。
- **根因**：把索引换成tmp+rename只使单文件切换更可靠，没有解决任务与索引的提交/恢复关联。submit注释声称“不会覆盖”与loader代码相反；reject注释承认覆盖并让用户重传。
- **影响**：task已待验收round1但索引round0，会被验收轮次守卫拒绝；退回任务round0但索引仍round1，显式复用也被候选轮次守卫拒绝。仅重新打开重查字节不能修轮次。核心硬4/5、T22/U07失败恢复未闭合。
- **证据**：本轮冻结writer/load/submit/reject、diff、作者r5报告；S/seeds/stale_index_recovery里task/state round1、index round0的独立负例。本次该seed业务未解析，**不声称原生已经触发故障或看到错误终态**；本缺陷结论为源码确定的恢复缺口。
- **具体改法**：由构建方为M5补可核验提交/恢复记录或从权威已提交事实重建协议，关联task版本/completion固定集合/轮次/索引与动作回执，启动先对账再开放操作。写失败传播保持，不把提示重新上传称为共同恢复，不扩服务架构。
- **验证**：驱动受控同盘测试submit/reject各自index写失败、commit失败、commit后中断；重启比task/state/index/completion/字节/events/actions后重试，确认无重复、无旧证据丢失、无错误成功提示。

### D-M5-05 — 修复子项认可；核心实证仍需完成，不另造放行事故

- **文件行**：`:5207–5220`保存全文比对；`:5536–5553`open、`:5639–5656`verify canonical比对；`:5281`内容指纹依赖。
- **实际**：本轮新增stored vs src_text及stored vs canonical等值保护，不能照抄上轮“只核尺寸”和“坏控制字节一定被放行”。审查新文件精确 **241 B**（更正N中的240 B），原SHA=`bebb344effb148706ea9b7ba5a274ddb81b1145bdf7f2d16d0ff3d8389bbdddd`，坏SHA=`8041e075cb57883a0462fa7b30b94a9f658f1e925305337628172e8369adea39`，FNV均`bb97a1a2`，canonical原件不变；源码新全文条件可区分它们。
- **证据限制/预期**：另造字节及6负例已核，但真实上传、fs.read二进制/中文语义、保存读回与实际两个入口未运行。作者静态11/11仅字符串命中；动态6case中4项 propagated_exception，不能当byte-perfect运行通过。预期源/存盘/canonical全字节一致，保存后坏/缺/异任务两入口均拒绝。
- **交接验证**：先修B01使当前代码可运行，再由驱动用真实上传生成记录；在其保存副本变更，覆盖控制字节/NUL/高字节/UTF-8/PNG或PDF/>64KiB，核完整字节、固定引用集合、权限、UI与权威回执。若实际原语不足，给同宿主最小复现，不宣称Python适配等同原生。当前不增加未经运行证明的新算法事故。

### 建议挂账（不作为 FAIL 依据）

- A-M5-01：r5清单无源hash、source_bytes=341209与实际UTF-8字节数395510不一致；独立快照已定位，建议补准确内容清单。作者旧evidence_root/host_runs字段有历史rc71/rc3说明；保留来源，本轮只更新审查字段，当前事实以本报告为准。
- A-M5-02：验收意见/经理理由落事件的源码改善保持，权威事件未跑，不重复列业务修复。
- A-M5-03：格式/长内容预览和复用UI可读性建议保留，不扩M6。本轮真正打开/错误/重试是未测核心项，不能靠建议描述放行。

## 硬验收与既有用例结论

|硬验收|本轮结论|
|---|---|
|1 真实选择/保存/重启再开|入口FAIL；完整附件链NOT_RUN，离线安装子项PASS|
|2 坏/缺/隔离/异任务/无权/旧轮双入口拒|NOT_RUN；固定集合和全文比对源码改善保留，预置坏件不代实际拒|
|3 仅待验/可信独立主体最终验收|NOT_RUN；自验/角色/理由守卫保留；可信文本输入通道子项BLOCKED|
|4 退回保留历史/新轮/明确引用|D04恢复源码FAIL；真实退回链NOT_RUN|
|5 原生打开/失败重试/表单/终态只读/完整两链|入口FAIL、D04恢复源码FAIL；完整业务NOT_RUN|

|用例|本轮结论与范围|
|---|---|
|G0-D|离线安装与Seatbelt隔离PASS；原生附件入口FAIL B01；真实附件保存/打开/重启NOT_RUN|
|T18|真实列表/搜索/事件/附件权限NOT_RUN，归属源码守卫保持|
|T19|真实坏/缺/隔离/异任务双入口拒及下载NOT_RUN；D05源码子项改善认可|
|T20|可信自验禁止/多角色同ID/经理理由/完工仅待验NOT_RUN；输入通道子项BLOCKED|
|T21|正常→退回→补充→新completion/新轮再验NOT_RUN；D04恢复源码FAIL|
|T22|D04共同恢复源码FAIL；本次实际异常NOT_RUN；受控writer/commit中断/同盘恢复通道BLOCKED|
|T28|真实候选加载一致PASS，业务程序解析/入口FAIL；同task命令/回读/业务重开NOT_RUN|
|T31|终态禁止再开工/再验、取消释放/事件、再次故障关联任务NOT_RUN；仅受影响回归，前序挂账不修|
|T35|证据变更后旧确认/AI建议失效实际NOT_RUN；受控迟到回包/交错通道BLOCKED；模型0次，不签真实效果|
|U03|可信三角色同task事实/权限/自验NOT_RUN，输入通道子项BLOCKED|
|U06|进度/完工/验收、退回历史/附件真实UI NOT_RUN；D04恢复源码FAIL|
|U07|两次宿主tap调度已执行，无业务重复点击/版本冲突/回执；实际恢复NOT_RUN，D04源码FAIL，受控故障/同盘通道BLOCKED|
|U08|业务客户区空白，入口FAIL；附件失败/无权/重试出口NOT_RUN|
|U11|宿主启动/截图PASS；应用UI解析FAIL，业务滚动/输入/面板稳定性NOT_RUN|

## 判定与交接

- **最终结论：FAIL**，不是BLOCKED整体，不以“基本通过”放行。必修P1为 **B-M5-01 原生解析入口** 和 **D-M5-04 共同提交/恢复**；D-M5-05全文比对源码改善保留，完整实证仍未闭合。建议不参与FAIL判定。
- 当前范围：候选/实际运行副本/离线安装/证据一致性/原生隔离回收PASS；原生业务入口FAIL；其余完整业务与验收未运行。固定宿主/白名单不足的子项另列BLOCKED，不把程序解析失败归咎沙箱环境。
- 修复顺序：只定位并修B01最小解析依赖；再闭合D04共同恢复；提供可信控件输入、同盘重启与受控注入的驱动通道，复跑D05和完整正常/退回链。保留旧证据/建议/前序挂账，不顺手修其他模块。
- 前序回归：M4关联解析依赖本轮重现，M4现有FAIL不改；M2/M3可信身份/输入限制作为本模块运行缺口如实记录，不重写其结论。
- 门禁：仅更新GATES中M5当前审查字段/status，review_report指向本报告；旧审查状态、作者READY交接与历史来源归档保留。其他模块/原 ACCEPTANCE.json 不改，没有取得新的业务PASS可升级台账。
- **不允许据本报告进入下一模块**；本会话不执行下一模块，也不给M6入口。
- NEEDS_ABRAM=no：身份/provider/隔离离线签名已授权；无发布/公开签名/上架、0模型调用、无402或欠费。剩余解析、恢复与驱动通道均为技术修复/验证条件。

STATUS=FAIL
NEEDS_ABRAM=no
