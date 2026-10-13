# M4 独立 Review r12

**最终结论：FAIL。受审候选：M4-r10-worktree。** 六场独立原生运行均 CLEAN，冷启动零业务解析/运行错误，合法盘加载、坏盘分类与备份保全、future/unknown/stale 锁启动处理均 PASS。**唯一继续必修：D-M4-03，原生命令原子边界尚未实现。** 本轮只增加方案与复现，业务脚本和宿主没有相应实现变化；真实 M3 创建→接单→设备→预约→开工、三角色和真正原生业务并发仍缺证。不能放行，不执行下一模块。

## 审查对象与范围

- 审查者/日期：当前主会话唯一独立审查者，2026-10-13，Asia/Shanghai；两段式 `review_r2_0002`，无子代理、不修业务/宿主代码。实际 Router/指定 gpt-6.1-sol 路由及线程 createdAt/改名接口无法核验，没有宣称切换或命名完成。
- candidate_id/base：**M4-r10-worktree / M4-r9-worktree**。由用户交接 `build_r2_0002_REQUEST_build_r10`、构建请求、`M4_IMPLEMENTATION_r10.md`、`M4/r10/CANDIDATE.json` 和 GATES 作者字段共同定位；没有按mtime选版本。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty。冻结main：**657584 B / SHA256 c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421**，与当前源码、r11审查冻结源、作者staged、审查seed/运行源一致；r11→本候选源码diff为空。保留他人改动。
- bundle digest：`77b95f2eb1ecc5c97cc109e46cda7ccbb3276ac52f99b4f840cad8150d1adf6b`；离线anchor：`966929104434039f8034ffccada5eae1ab020c05518dab24dbc695f9626c6a0b`。复用授权本地catalog/install_staged路线，运输manifest与工作树未签名manifest区分，不声称字节相同。
- 固定宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness `226df8dd61409cb0c82a7e70a931c2637362445d8a4a9e5232254da29188d11a`；profile模板 `80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7`。全部独立重算核对。
- 前置：**M3=FAIL / M3-r9-worktree / M3_REVIEW_r12.md**，没有已接受M3 PASS。按用户挂账裁决继续局部复核，不修/改判M3；同源码不代表前置已验收。
- 阅读范围：实际AGENTS、CONTEXT、00/01/02/M4/04、根基线相关段；r11旧缺陷、r10作者交接/证据/脚本、受影响源码/宿主fs注册、harness/schema、19项T/U定义。只核旧B01/D03/D04及直接回归，没有无关扩审。
- 驱动执行：**03:49:06–03:50:53 +08:00**，一个batch，6/6 CLEAN、quit_http/rc0、无ABORT，各场16.24–16.27秒。审查者未启动宿主/harness、未执行sandbox-exec/pgrep预检。
- 实际审计命令：`PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/optimization/2026-10-09/M4/native/review_r2_0002/audit_phase2.py`，rc0，**5403项证据一致性/盘面检查，0失败；不是5403个业务用例PASS**。
- 门禁写入前18项保护输入及132项seed/mirror文件与第1段快照一致。源码/原ACCEPTANCE不改，GATES原态归档再更新本模块审查字段，其他模块与作者交接字段保持。
- 第1段按上层记忆流程读取一次项目外记忆索引，已在阶段笔记披露，未用作候选/运行证据；本第2段读写均在项目内。没有读取真实明文凭据或provider密钥。needs_model全false，本轮真实模型调用0，没有实测402/欠费。无发布、push、issue/评论、消息或公网部署。

路径约定：**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r2_0002_REQUEST_review_r2_0002/`；**E/**=`runtime/optimization/2026-10-09/M4/native/review_r2_0002/`；**A**=E/native-evidence-audit-r12.json；**R**=`M4/native/REQUEST_review_r2_0002.json`；**N**=`M4/native/REVIEW_NOTES_r2_0002.md`（R/N短路径相对runtime/optimization/2026-10-09）。R SHA256 `f693d2c386cb485b5713b88e75a0494979baa0946a1dec5977e031606e0550fd`。源码行号指E冻结源，与受审源码相同。

置信度：候选/证据/盘面/原子窗口与文件协议反例 **高**；未执行真实业务命令、可信身份交互、原生并发/模型效果 **未知**。

## 必需检查

|检查|独立步骤/期望|实际|结论/证据|
|---|---|---|---|
|候选/宿主/运行一致|重算冻结、镜像、installed/.running全资源与宿主|六场每场唯一running包，资源逐字一致，657584 B eval view=true|PASS版本一致性，A|
|冷启动解析/渲染|零业务错误，原生根可见|6/6零[E]/panic/unknown动作，tick异常0；完整登录页|PASS冷开/登录页；登录后工作台NOT_RUN，H/A/截图|
|合法盘加载|含中文/引号/换行完整任务不误pending、不改事实盘|三个锁组合均pending=false、无新recover、原盘不动|PASS B01加载回归|
|坏盘分类/保全|第二成员非法整盘拒；截断保主源与既有备份|原因准确，recover/corrupt.latest与原文摘要相符|PASS冷开子项；实际恢复确认NOT_RUN|
|旧锁启动恢复|future/unknown保留、stale回收、旧token不复活|三锁均符合权威盘预期，当前token空|PASS boot子项，不代存活持有者回收安全性|
|硬1权限/设备关系|实际不合格/越权/伪设备拒，合法服务空间可绑定|没有实际可信主体绑定命令|NOT_RUN；当前白名单登录文字通道BLOCKED|
|硬2预约规则|提议不直升、合规确认、跨项目冲突/过期/改约/拒绝/时区|没有实际预约命令|NOT_RUN；旧锁过期不是预约过期|
|硬3真正并发|同盘双原生上下文接单/重叠确认唯一成功，相邻正常|源原子边界仍缺；独立Python协议反例两方读回后丢更新|FAIL源P1 D03；真正原生同步调度BLOCKED|
|硬4开工/旧授权|无设备/有效预约不足拒；改派旧技工不能操作|没有实际改派/开工命令|NOT_RUN|
|硬5三角色信息与回执|真实填写、阶段/负责人/预约/动作事实一致|截图只有未认证登录页，成功动作/事件0|NOT_RUN|
|旧确认/AI撤销|改派/改约使旧绑定失效，新编辑再绑定、迟到回复拒|六源码段逐字保持，动态未执行|SOURCE-CLOSED限定旧epoch反例；动态NOT_RUN/交错BLOCKED|
|隔离与回收|核profile/probes、预后进程、退出组、外写记录|6/6满足指定隔离/回收字段|PASS证据记录范围，A|

### 六场权威结果

|场景|权威盘面与结果|判定范围|
|---|---|---|
|fresh_absent_store|结束仍无tasks/lock/recover，pending=false，actions/events空|PASS无任务冷开，不是M3创建|
|valid_unicode_future_lock|合法任务原字节保持，pending=false；future foreign token原样，进程token空|PASS加载/future保留；lock_state为空，不编造owned状态|
|valid_unicode_unknown_lock|同合法盘保持，unknown戳token不动，unknown_kept，token空|PASS加载/未知锁保留|
|valid_unicode_stale_lock|同合法盘保持；stamp=1锁清空、released、token空|PASS旧锁boot回收，不代活持有者TTL回收|
|mixed_invalid_second|整盘保持，pending=true；why指第2条必需字段/类型/状态，recover=原坏源|PASS整盘拒收/准确分类/原文备份|
|truncated_preserve_previous|截断主盘与旧有效recover逐字保持，corrupt.latest=本次坏源；why指首尾截断|PASS截断检测/旧备份保全|

## 证据核对与适用边界

1. **984条MANIFEST**摘要全部重算，文件集合精确，无重复、遗漏、额外文件或symlink。summary内嵌请求、场景/batch集合及逐场摘要与result匹配。
2. 各场profile按模板/run路径/control port逐字重建，SHA匹配；apply rc0、probes.ok=true、外写探针created=false、五禁读探针拒绝。pre/post严格rc1/NONE，pgid_members_after空，host rc0/quit_http；library_scan空，驱动记录的真实HOME/.octosense mtime不变。没有另去真实HOME预检。
3. HOME、app-data、cache/config/data/tmp、Metal cache等12项路径均在新run内，命令匹配仅launch-hub/capture；seed条目/摘要精确对应冻结种子，镜像、installed、唯一running全资源一致。digest_seen_in_seed=true、digest_seen_in_host_log=false如实核对；加载证明来自running资源与业务eval，不靠digest marker单项。
4. 六个final capture与result/MANIFEST摘要匹配，连同part共12张PNG，均2800×1696；两种字节内容已全部逐种目视（03:49/03:50）。均是完整账号/口令/登录/清空页，未显示任务列表、预约/恢复表单或三可信角色。相同截图尺寸不能以请求1280×800声称业务自适应/文字放大通过。
5. 全量读取六份host.log，bytes/tail/markers独立重算匹配；每场业务657584 B/view=true，另一个809 B系统视图未混作业务。0[E]/panic、0未知动作、tick异常0，**本轮已删除旧wait:N，launch/capture动作覆盖完整**，等待只依据harness墙钟。
6. files_written_in_run_dir唯一、有序、全部实际存在且在run内；files_written_count为127/128，与完整列表一致，未触及截断上限。它是mtime文件清单，不是业务动作数或内核完整写审计。actions/events及合成hash账号原字节未变；任务事实未变，只出现预期坏盘备份/旧锁回收及运行缓存状态。
7. 全部sandbox-denials完整读取，按harness规则独立重算summary一致。存在被拒remote:*:443、/dev/dtracehelper与系统Metal缓存写尝试；**被拒尝试不等于成功外联/外写**，重复拒绝日志不当作准确模型请求计数。本轮没有已证成功违反隔离的行为。
8. needs_model全false，**model_proxy/model_proxy_stats字段实际不存在**，env无MM_KEY/OCTOSENSE_MODEL_ENDPOINT。没有编造requests=0统计字段，模型效果NOT_RUN；没有欠费错误，因此NEEDS_ABRAM=no。复用签名store，新私钥0，作者keys目录仍空，先前删除证据保留。
9. future场运行PGID曾有一个osascript成员，参数/用途未记录，最终组空。延续A-M4-R10-01来源建议；不凭进程名判成功未授权自动化，审查方未调用osascript/辅助功能，请求无ui_actions。
10. 未seed view/state，fresh/future最终state.status出现state恢复说明；这是另一状态文件的诊断，不是任务盘坏，也不证明M3输入恢复通过。坏盘诊断虽落state，当前截图没有显示可信恢复出口；不能把盘内说明代用户可见错误流程。

## 上轮缺陷闭合与本模块修复清单

### D-M4-03 · P1 / 必修 / PARTIAL：原生原子边界未闭合

- **文件/行**：`app/bundle/main.splash:4446`获取、`:4500–4507`普通锁写/读回、`:4517`释放；`:4860`commitBound，`:4883–4909`owner核、`:4915–4965`版本/冲突核、`:4985`tmp写、`:4995`主盘写、`:5062`放锁；事件在调用方commit/放锁之后追加。宿主`runtime/native-build/makepad/widgets/src/splash_storage.rs:242–415`无已公开原子获取/CAS/持有期锁原语。
- **触发**：A/B两独立上下文先读空锁；A写owner、完成owner/版本/冲突检查后暂停；B用此前空锁判断覆盖owner并完成检查；A先写/读回成功，B随后写/读回成功。另一既有反例注入O_EXCL持有者复核后仍存活但被TTL回收，旧持有者可迟到写。
- **实际/预期**：第1段两个实际Python进程PID74428/74429及O_EXCL注入PID74430/74431均rc0，双方prewrite_checks_passed/readback_matches=true，最终version=6/assignee=B、A更新被覆盖。预期同盘接单/重叠确认唯一业务成功、跨项目冲突拒、相邻正常，任务/预约/回执/事件一致。**这里是文件协议反例，不是原生业务双成功实测。** 六场原生冷开只证明boot子项。
- **根因/影响**：read/write/read、owner/版本/冲突复核与主写分离；整盘写可能覆盖其它提交。影响本模块硬3/T04/T11核心正确性，旧P1保持。r10源码与宿主没有相关实施变化，CLEAN不能关闭此项。
- **进展/闭合范围**：已交付可执行方案、修正r9单独O_EXCL+TTL方案误判，关闭对应交付子缺口；本轮future/unknown/stale boot回归独立PASS，fail-closed/同owner/盘版本/冲突守卫保持。没有原生原子提交闭合证据。
- **证据**：E/source.main.splash、source-regression.json、空diff、independent_lock_counterexample.py/independent-lock-counterexample.json；作者r10脚本/方案交付与E/proposal-source-audit.json；H三锁场只支持boot限定子项。
- **具体改法**：提供并接入可靠原子命令边界，覆盖提交点最新主体/授权、expected_version、跨任务冲突、事实/预约/回执/事件及可恢复结果。持有期OS锁的TTL回收也必须先拿同一锁，不能剥夺仍可写的活持有者；或用真正原子CAS/事务与fencing拒旧持有者迟到提交。保留现有拒绝守卫，不能仅加一次owner读取、单独O_EXCL或作者Python成功方案替代实际接入。审查方不修改业务/宿主、不新增服务。
- **验证方式**：两个可信原生上下文共享一个新隔离Store，同步接单/重叠确认各唯一成功，跨项目重叠拒、相邻都成功；核唯一承接者/预约/成功回执/同action事件及同盘重开。注入获取读失败、提交丢锁/覆盖/清空、活持有者被抢占与回收、提交中断；已通过冷开/加载/坏盘/三锁boot不能回归。
- **动态解阻**：当前schema/harness逐场复制新Store、单宿主顺序执行（native_harness.py:580–588、:853–865），无双原生上下文共享同盘+提交点同步/暂停入口。仅该白名单无法覆盖的动态项记BLOCKED；源码P1仍FAIL，不因为动态BLOCKED降成建议。

### B-M4-01 · 已关闭加载/分类/保源子项保持；可信恢复NOT_RUN

文件：`main.splash:1383`同型首尾/成员门禁、`:1414`坏源备份、`:1452`恢复核身份、`:1587`加载。旧触发为合法盘误判截断；本轮三份中文合法任务均pending=false，无新recover、原文不动；第二成员非法准确整盘拒、截断主盘/旧备份保持。本轮H/A独立回归PASS，不重新列必修。完整认证后写拒与显式恢复/可见错误出口仍NOT_RUN；保留当前判据/权限/保源守卫，补实际恢复确认、权威回读，不清盘制造成功。

### D-M4-04 · SOURCE-CLOSED限定epoch反例保持；动态NOT_RUN

`m4_invalidateConfirmation:4240`、`editDraftField:6395`、`editRawText:6532`、`confirmDraftModelBound:6852`、`rescheduleAppointmentFromForm:8317`、`reassign:10503`六段与r11冻结源逐字一致（E/source-regression.json）。旧累计编辑集复活确认源码反例保持关闭，不要求重写已修段；实际改派旧技工拒、改约旧确认/旧AI撤销、迟到回复/新编辑再绑定仍NOT_RUN，受控交错入口BLOCKED。不能SOURCE-CLOSED代完整动态PASS。

### 建议与挂账（不据此判FAIL）

- 旧A-M4-01/02/03及A-M4-R10-01保留；future场osascript成员用途追溯建议继续，最终回收合格，不据名称认定安全P1。
- **A-M4-R12-01 / P2 / 证据文案建议**：作者`m4_r10_atomic_fencing_repro.py:166–214`的B2迟到提交实际因版本先变化返回needs_verify，报告写rejected_stale_fence；`:360`的C-preempt用两个thread，C2才是Python多进程。E/proposal-source-audit.json独立补“version不变、fence已换”和“复核后CAS处换owner”，分别拒绝stale fence/CAS。建议报告按实际返回/运行形态改文案，保留两个更有区分力的方案反例；它们仍是VFS/OS替身，不能说实际宿主原子边界已完成。此项不新增业务P1。
- GATES作者host_runs/deferred_gaps/test_counts仍含旧rc71/rc3、provider延期/r9证据计数等历史文字；本轮只改审查字段，明确审查依据为当前harness证据/已裁决身份/provider，不拿旧作者字段作BLOCKED理由。原始来源保留。
- M3 r12输入恢复FAIL沿用原报告，不由本模块修复；旧R-M4-TEST-01的wait动作问题本轮已在请求中修正，日志零unknown，历史证据不抹去。

## 19项既有用例逐条结果

|用例|本轮精确状态/范围|
|---|---|
|T04|BLOCKED真正双原生同Store同步接单；D03源P1保持，Python协议反例不是业务验收|
|T05|NOT_RUN技能/项目拒绝、经理分配及事件主体|
|T06|NOT_RUN实际改派/旧预约取消/新承接者/ACCEPTED/旧技工拒；撤销源码保持|
|T07|NOT_RUN编码/asset载荷一致与伪造/跨项目/归档拒|
|T08|NOT_RUN有效服务空间与仅同安装位置反例|
|T09|NOT_RUN无设备开工/处理中技工换设备拒/经理更正旧新值理由|
|T10|NOT_RUN提议不直升/非报修人确认拒/合规确认|
|T11|BLOCKED同Store同步重叠确认；跨项目冲突、相邻实际NOT_RUN；D03源P1|
|T12|NOT_RUN待改约旧确认有效/新确认替代/拒新保旧；撤销源码保持|
|T13|NOT_RUN提议到期/无timer/假客户端时钟；stale锁boot PASS不是预约过期|
|T14|NOT_RUN上海日期输入/UTC毫秒/模糊时间核对/end<=start拒|
|T15|NOT_RUN旧version拒/刷新/防覆盖/任意百分比拒；合法盘加载回归PASS仅子项|
|T31|NOT_RUN取消释放预约/保事件/终态只读/新关联任务|
|T35|NOT_RUN动态改派改约/迟到AI/新绑定；SOURCE-CLOSED仅epoch反例，交错调度BLOCKED|
|U01|NOT_RUN三可信角色待处理首屏；PASS仅完整未认证登录页|
|U03|NOT_RUN同任务跨角色事实/动作与承接者不可自验|
|U04|NOT_RUN有效预约/待改约区分与冲突/过期错误出口|
|U05|NOT_RUN实际设备安装位置/服务空间/来源选择依据UI|
|U07|NOT_RUN实时重击/响应丢失/版本冲突/离线输入恢复；M3 r12恢复FAIL不改判|

当前用户只授权本轮内置test-action/capture并明确禁额外osascript/辅助功能/自动化。schema虽描述ui_actions的历史授权，本轮更窄约束优先；固定宿主type/key已由前序实证与schema标明未实现，不能注入SESSION或运行状态绕登录。**登录文字/键盘与后续可信UI通道BLOCKED**，依赖它的业务动态未执行记NOT_RUN；受控回包/提交点故障/双上下文同盘调度BLOCKED。六个已执行冷开子项全部按结果PASS，不用agent环境rc71/rc3标BLOCKED，没有ABORT。

## 判定与门禁

- **最终结论：FAIL。** 唯一必修旧源码P1为D-M4-03；方案交付有进展，原生实现未变。没有真实核心主链/无P1证据，不能套用“完成优先”给PASS。建议项不构成FAIL理由。
- 本模块修复/解阻清单：①实现并接入可靠原子命令边界；②提供当前授权范围内可信输入、同盘双原生上下文同步及提交点/AI交错入口；③提交新可定位候选，独立从M3创建工单走到开工，核19项相关动态与权威回执/失败恢复；④保持本轮加载/保备份/三锁boot和旧epoch源码回归。不能手改status/version/预约跳主链，不能只补作者Python方案成功测试。
- 受影响前序：M3仍FAIL，同源加载回归不代M3验收；其余模块不扩审、不修改。原`docs/build-loop/ACCEPTANCE.json`保留，未把旧后端/作者结果改称本轮原生PASS。
- 更新`docs/optimization/2026-10-09-desktop/GATES.json`仅M4 status和review字段：review_candidate_id=M4-r10-worktree，review_report指本报告，精确记录六场与19项边界；原review字段追加review_history，完整前态另存E/gates-before-review-r12.json。作者candidate/base/implementation/test_counts/host_runs等与其他模块保持。
- 不允许下一模块，不提供/执行下一模块入口。NEEDS_ABRAM=no：身份/provider/离线签名/本地路线已裁决，没有余额错误或公开发布需求；剩余为实现/测试入口缺口。

STATUS=FAIL
NEEDS_ABRAM=no
