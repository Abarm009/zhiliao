# M5 独立 Review r8

**最终结论：FAIL。D-M5-04 的真实附件恢复仍失败：7 个独立恢复场景的目标索引未保存，完整原件也未恢复为可读附件。解析/隔离/回收通过，D-M5-05 的危险源码分支已删除；这些子项不能代替真实完工与独立验收。**

- 审查者 / 日期：当前主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无子代理。
- candidate_id / base_candidate_id：`M5-r7-worktree` / `M5-r6-worktree`；HEAD=`8d730569546cb57310944bb299695134df773b9d`，加既有未提交修改。按用户交接的 build_r2_2104 证据、请求、候选清单及实施报告联合定位，不按mtime。
- 源 SHA-256=`a91f71f809183f243762a7a2595ef880929dde3dd727ec7a51cbc503aeb206a1`，495772字节；bundle digest=`e6ddeed41a5fe2b21dbc38156ae3f7fe29d9cb741e4de01d39db18d683b6d478`。第1段快照与第2段开始一致；写门禁前再核源/配置/候选/宿主，结果见 S/final-write-verification.json。
- 作者报告：`reports/M5_IMPLEMENTATION_r7.md`；清单：`runtime/optimization/2026-10-09/M5/r7/CANDIDATE.json`。作者 harness 路径 `M5/native-runs/build_r2_2104_REQUEST_build_r7/` 仅参考，不代独立运行。
- 前置：**M4=FAIL，M4-r7-worktree / M4_REVIEW_r8.md**，没有已接受M4 PASS候选。按用户前序挂账裁决继续M5复核，不修M4，不伪造前置。其他模块结论不改。
- 实际差异：相对上轮冻结M5-r6，默认STATE声明M5字段；8个变化函数为m4_init_forms、m6_init_forms（只统一M5根）、m5_sandbox_root_abs、m5_init_forms、m5_attach_from_path、m5_load_attach_index、新增m5_resolve_existing、m5_reconcile_attach_index。S/diff与changed-functions可定位，不扩审其他业务。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 原生执行：外部驱动经审查方请求运行，03:07:31–03:09:21 +08:00；8场CLEAN、quit_http、rc0，没有ABORT。审查者未自启launcher/sandbox-exec/pgrep，没有osascript、辅助功能或其他UI自动化。
- 环境/模型：每场新HOME/app-data/cache/tmp/logs，Seatbelt隔离；全部needs_model=false，模型调用0，无proxy/stats或欠费。主会话Router路由、指定型号和createdAt/标题接口不可核验，未冒称切换或实际命名。
- 已读：第1段AGENTS/CONTEXT/00/01/02/M5/04、上一轮缺陷/候选/交接/相关源码与用例；第2段R、全部summary/result/profile/完整host.log/denials/MANIFEST、权威盘、8张最终截图及1张不同的part图、直接相关函数。7张part与最终图同字节，不重复当新交互证据。
- 已运行：独立离线官方hub verify（第1段rc0）、驱动独立8场原生冷启动/恢复、审查方摘要/证据/真实盘对账。Python审计只核证据，不执行Splash业务。
- 未运行：实际选文件上传后变更、完工与验收双入口拒绝、可信独立登录/多角色自验/经理理由、正常链、退回链、同盘重启打开、精确提交点故障及模型交错。未执行命令记NOT_RUN；已证白名单通道缺口记BLOCKED，见后文。
- 置信度：候选/隔离/零parser/索引不变/完整件MISSING/系统审计及轮次改善 **高**；具体writer原语失败原因 **未知**；路径解析不能到达字节校验的判断 **高**，具体宿主fs/字符串原语原因 **未知**；完整业务链和坏件通过验收 **未知**。

## 证据索引与独立核验

- **H**=`runtime/optimization/2026-10-09/M5/native-runs/review_r2_2104_REQUEST_review_r2_2104/`，驱动原证据，只读保留。
- **S**=`runtime/optimization/2026-10-09/M5/native/review_r2_2104/`，快照、diff、夹具、seed、离线验签与审计。
- **R**=`M5/native/REQUEST_review_r2_2104.json`；**N**=`M5/native/REVIEW_NOTES_r2_2104.md`。
- **A**=S/native-evidence-audit.json。独立运行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r2_2104/audit_phase2.py`，rc0；**4147项证据一致性检查通过，不是4147项业务测试通过。**

1. H/MANIFEST.sha256 **1353项**逐项重算SHA：缺失/摘要错误/重复/未列入均0。summary.request等于R；harness/template摘要相同，8场summary的verdict/exit/wall/billing与各result一致。
2. 每场profile_probes.ok=true，apply rc0，外写探针被拒且created=false，5个禁读探针均拒；pre/post_pgrep均rc1/class=NONE/out空，pgid_members_after=[]；quit_http=ok/rc0/CLEAN，无异常或ABORT。没有用agent沙箱rc71/rc3判BLOCKED。
3. 逐场按模板、真实场目录、黑名单中的原HOME字符串和控制端口重建profile，文本/摘要全部匹配；记录的所有HOME/app-data/tmp/cache路径在本场。原HOME `.octosense` mtime前后一致，library_scan为空；审查者仅读驱动记录，没有读取项目外原HOME。
4. 写入列表首场128、其余各130项，数量与完整唯一列表一致，列项均存在且在本场，不截断。完整denials按harness算法重算匹配，包含被拒remote:*:443、Metal系统缓存、部分/dev/dtracehelper；没有据此发现成功外联或越界写。该数量包含宿主文件，不是业务操作数。
5. 8张请求最终PNG摘要与result/MANIFEST一致，均**2800×1716**，逐张查看。7张part同字节；no_canonical_control_mutation.part不同，另行查看仍为同一未登录空态/无可见任务。业务列表/导航/未登录说明已渲染，登录输入及按钮下部仍裁切；附件/完工/验收表单没有出现。请求1280×800不等于业务布局验收通过。
6. 每场完整host.log字节数、markers及tail独立重算相同；实际业务eval **495772字节、view=true**，launch-hub成功，零parser/reserved/unknown-action/panic。809字节系统窗口不与业务eval混记。B-M5-01解析/全空白子项保持关闭。
7. 所有场的installed、实际唯一`.running/<内容ID>`及hub-mirror bundle **全部文件**与S签名候选同SHA；accepted catalog与seed同SHA，manifest digest正确，当前main与交接一致。digest_seen_in_seed=true、digest_seen_in_host_log=false与实际一致。fixture登记根与实际运行盘 **8/8匹配**，不归因于作者钉扎偏差。
8. tasks.json均与seed逐字节相同；本场所有原附件/canonical/inbox字节保留，没有新造canonical。7个恢复场正确路径index均与seed同SHA，均出现0字节 `m5-test/evidence_index.json.tmp`；state与系统audit均明确index_saved=false/index_save_failed=true、audit_saved=true。旧 `[Error:NotFound]` 错误目录问题本轮未出现，但正确路径落盘仍失败。
9. round5两成员在state内存索引改到5，磁盘仍0；marker-only内存有退回时间，磁盘仍null；完整新件真实stored/canonical全等且都存在，state新项却MISSING，目标index缺该项。两坏件场也在state停MISSING/source=rebuild_from_task_store，未到CORRUPTED/no_canonical分支；没有坏件READY或验收放行证据。外来同id保持other-task/round2，未被修成当前任务；foreign_items=2不等于两件外来附件，源码两阶段重复计数，本轮不为计数新增P1。
10. 8场预存未提交中文pending_input均被清空；属于已挂账共用启动输入恢复问题，不是本轮成功键入后丢失。actions/events均为`[[]]`，源为既有空数组迁移；没有可信业务final回执，不当成功链。系统审计受控actor=system:boot-reconcile且真实写出，改善成立。
11. 本轮新生成私钥0；第1段独立官方verify，作者两私钥再次检查不存在、keys目录空。没有读明文凭据/模型密钥、造SESSION、改原始业务数据、公开签名/publish/listing/push/Issue/消息/公网部署。模型proxy/stats字段及文件均不存在，符合全部needs_model=false；请求0，无计费阻塞。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/运行包|冻结候选、核全部运行副本/日志/manifest|当前同digest同宿主|8场全部一致|PASS此子项|S快照/A/H|
|原生解析与渲染|新盘launch-hub、capture、读完整日志|零parser、业务区域出现|8场零parser，未登录业务区出现|PASS B01子项；完整可操作登录未成立|8张图/log/A|
|隔离/回收|内核探针、profile/env/denials/PGID|用户指定隔离与回收|全部符合，无ABORT|PASS|8个result/profile/denials|
|提交分裂恢复|历史round2/5，两任务成员5/index0|counter5与两index成员5持久化|counter5/内存5；磁盘0，tmp空，audit记录失败|**FAIL D04**|round5_two_members盘|
|marker-only恢复|task/index均0，仅task退回marker|只marker变化也应落盘|内存marker已同步，磁盘仍null|**FAIL D04**|reject_marker_only_r5盘|
|完整件索引重建|原件/canonical全等，缺新项，旧/孤儿/外来保留|完整新件可读且READY持久化，旧项不删|旧项/字节保留；新件内存MISSING，目标缺项|保留PASS；恢复**FAIL D04**|intact_rebuild_old_foreign盘|
|缺/坏件恢复|新字节、缺stored、等尺寸控制字节变更、丢canonical|MISSING/CORRUPTED真实持久化，无假READY|全部新项内存MISSING、磁盘仍空；丢canonical未被重造|不假READY子观察成立；分类/恢复FAIL归D04；D05动态未到达|三负例盘/A|
|跨任务恢复|同id外来index/round2，自己task round5|保留归属，不修成本任务附件|外来归属/round2保持、audit记录|PASS限定归属恢复子项；命令拒NOT_RUN|foreign_same_id_round5盘|
|真实上传后双入口反例|实际上传→保存后损坏/缺失/异任务→完工与验收|均拒绝且回执/事实一致|只运行恢复夹具，无实际上传或两个命令|NOT_RUN；保存后注入通道BLOCKED|R/schema/N|
|可信独立验收|实际可信承接者/独立报修人/经理会话|禁止自验；经理理由必填；只待验再独立完成|没有可信登录与命令|NOT_RUN；可信文本输入通道BLOCKED|当前8图、同宿主旧unknown-action日志|
|正常链/退回链|同task真实填写、保存、完工、验收/退回补证|事实、界面、字节及回执一致|未执行，tasks不变、无业务final回执|NOT_RUN|8场盘/图|
|同盘重启/提交点异常|应用保存后的同盘跨进程重启、精确中断再开/重试|可读、一致、无丢失或重复|仅每场新盘冷启动；启动恢复实测失败|启动恢复FAIL；指定调度通道BLOCKED，真实异常命令NOT_RUN|D04、R/schema|

**BLOCKED的限定原因**：同摘要发行宿主上一轮独立 `review_r1_2104.../cold_input_probe/logs/host.log:39–40` 明确拒绝type/key，当前宿主未变；不是schema有名字就可可信键入。当前schema仅启动前seed、每场新目录，不表达运行中改应用刚保存副本、精确commit/writer中断、同盘跨进程重启或受控模型迟到交错。这些指定子步骤无法由现有已验证白名单完成。没有harness ABORT；已运行的启动恢复按FAIL，未执行领域命令按NOT_RUN。需驱动/宿主提供支持的可信控件输入与受控注入/重启通道，维持既有Seatbelt和秘密边界，不需Abram新增授权，不用UI自动化或伪造SESSION补验收。

## 缺陷与上轮闭合

|编号|本轮结论|
|---|---|
|B-M5-01|CLOSED保留：8场零parser、业务区非全空白；完整可信操作未签收|
|D-M5-01|内容出口/canonical守卫源码子项保持；真实打开/下载/重试NOT_RUN|
|D-M5-02|内核隔离PASS；新默认根/字段改善，恢复路径失败并入D04；无成功越界访问证据|
|D-M5-03|固定completion集合逐件守卫保持；跨任务恢复不修平子项PASS；真实双入口拒NOT_RUN|
|D-M5-04|**P1 / 必修 / OPEN，原生FAIL**；字段/轮次/marker/审计改善，不等于字节可读或索引持久化|
|D-M5-05|**SOURCE-CLOSED**：不可信canonical自动重建分支删除；保存读回已加。危险源码反例关闭，Native内容分支未到达/双入口NOT_RUN；不要求重写已修分支，也不宣称完整动态PASS|
|D-M5-06|本轮8场用户指定内核隔离及回收PASS；显式读写仅本项目|
|R-M5-01|CLOSED保留：官方离线verify及本地已安装当前digest真实加载成立|

### D-M5-04 — P1 / 必修 / OPEN：索引写入始终失败，恢复路径将完整附件误判为MISSING

- **文件与行**：`app/bundle/main.splash:6930–6955`索引writer，尤其`:6940`写tmp、`:6948`fs.rename与`:6950`清tmp；`:6972–6987`m5_resolve_existing；`:7090`调用resolver、`:7099–7126`读取/分类；`:7181–7207`writer与读回；`:7227–7246`结果/失败提示。可对照S/main.splash.snapshot，不以VM坐标冒充源码行。
- **触发**：按R用当前候选及同发行宿主冷启动round5_two_members、reject_marker_only_r5、intact_rebuild_old_foreign任一场。fixture绝对根与实际run完全匹配，真实字节在获准本场app-data，profile未放宽。
- **实际**：7个恢复场正确index均未改、tmp均0字节，系统audit/STATE均index_saved=false、index_save_failed=true。两成员task round5，内存index5而盘0；marker-only内存有时间而盘null。完整新件stored/canonical均存在且同SHA、220字节，内存新项MISSING/content_signature=null，磁盘缺项。坏件也停在同MISSING状态，无法实测新完整性分支。旧字段错误值目录已消失、counter5和系统audit已落state/文件，这是**部分修复**。
- **预期**：启动恢复把已提交任务的固定成员/轮次/退回标记同步并持久化到正确index；合法完整件可读且验证READY。坏/缺/外来按真实内容/归属拒，旧记录/字节保留；失败保留明确可重试出口，成功必须真正读回，不只更新内存/提示。
- **根因**：原writer协议在固定宿主上仍不能完成目标保存；新增读取检查正确暴露了失败，却没有修复writer原语。resolver未让完整文件进入成功内容校验，绝对/相对回退链在当前宿主不成立。**具体fs.rename支持/返回/异常、字符串basename或fs路径语义的哪一处致因尚未知**；无日志细分原语结果，不能仅凭0字节tmp武断认定“宿主没有rename”。它不是agent运行限制，也不是本轮fixture钉扎错误。失败事实与受影响代码位置高置信，底层致因需小probe定位。
- **影响**：本模块核心硬1/4/5和G0-D/T21/T22/T28/U06/U07不能成立；合法附件无法可靠从任务事实恢复，索引/任务分裂持续，坏件分类验证也被阻断。不是美化或可挂账建议。
- **证据**：H/round5_two_members和reject_marker_only_r5下`home/.octosense/apps/octosense-repair/{tasks.json,state.json,m5-test/evidence_index.json,m5-test/evidence_index.json.tmp,m5-test/m5_reconcile_audit.json}`；intact场同路径及attachments原件/canonical；全部其他恢复盘；A逐场state/index/真实SHA及S/fixtures.json。没有拿作者结果代替这些独立原生结果。
- **具体改法（构建方Kimi-K3）**：只修此编号。先用固定宿主、驱动harness的小范围受控原语探针记录fs.exists/read/write/rename结果和真实盘，而非Python移植。对当前app-data统一采用已验证路径语义；从可信任务登记的相对路径解析，不靠尚未实证的字符串/绝对路径回退。使用宿主实证可用的保存/恢复协议，准确处理错误值与异常；保留旧目标，读回核完整成员/轮次/marker/归属，再宣布保存成功。不得改业务门槛、扩权限、放宽profile或新造canonical追认坏件。保留已修STATE、单调轮次、系统审计及外来隔离守卫，不重写无关模块。
- **验证方式**：先harness冷启动零parser/业务渲染；复跑R的round5两成员、marker-only、完整件+旧/孤儿/外来，核真正index全部字段/真实原字节/审计，正确tmp处理，无错误目录。坏件+canonical、坏件无canonical应CORRUPTED并拒，缺件MISSING，外来保持归属；完整件READY，旧completion固定集合不偷换。驱动通道补齐后实际新上传保存→损坏/缺失/跨任务→两个命令均拒，并跑正常链、退回补证新round、精确index写失败/commit后中断/同盘重启/重试，核回执与权威结果。静态30/30、Python仿真4/4或CLEAN不能代验。

### D-M5-05 — 源码反例关闭，动态NOT_RUN

- **文件行**：`:7107–7113`丢canonical保持CORRUPTED、不写新canonical；`:6679–6685`保存后canonical读回；`:7430–7444`缺canonical/全文不等拒。根因修复符合上轮最小取消危险分支的建议。
- **独立输入**：新原件与改件各220字节，87个0x05→0x06；真实SHA分别`e5348a7d5f8029d4f58f7bdcaa7459c7175201d1890c2462f32eb1a3b64060f5`、`7d8ee2edc4a836e2c204f254e7a8bf56ad69cbba83f872093126423a80dddab8`；源码算法分析FNV都`582bb92b`，仅分析，不当原生hash证明。
- **原生实际**：两改件内容原样保留、未新造canonical；内存新项均MISSING、source仍rebuild_from_task_store，index空，先被D04解析/保存路径挡住，没有实际CORRUPTED内容验证或READY/验收放行。**不再保留旧危险源码分支为OPEN P1**；后续重点是D04修好后的内容分支及实际双入口回归，无新证据不要照旧报告重复修改已关闭分支。

### 建议与前序挂账

- 共用登录行裁切、预存中文输入清空仍实测存在，关联前序M4/M3入口与恢复缺口；本轮不新建无关编号，不修前序。若它们阻断M5可信实际流程，应作为必要最小依赖由构建方/驱动处理；不能用标签代验。
- raw.len数组判断、foreign重复计数、截图尺寸与请求尺寸关系是建议/证据边界，不新增FAIL依据。audit写出和state失败提示是真实改善，但截图未显示附件失败可操作出口，不签U08完整通过。
- 作者/CONTEXT历史中的agent rc71/rc3或身份/provider未裁决条目不能作本轮阻塞理由；GATES构建字段含旧文字，按只改审查字段的用户边界保留其历史，当前审查字段给出真实结论。

## 硬验收与相关既有用例

|硬验收|本轮结论/范围|
|---|---|
|1真实选择与重启打开|恢复FAIL D04；实际上传保存打开NOT_RUN；指定输入/同盘重启通道BLOCKED|
|2缺/坏/隔离/异任务/无权/旧轮拒|D05危险源码反例关闭；恢复分类/持久化FAIL D04；真实双入口NOT_RUN，保存后变更通道BLOCKED|
|3只待验、可信独立终验|实际业务NOT_RUN，可信文本输入通道BLOCKED；自验/代验理由守卫保持|
|4退回保留、新轮与引用|旧字节/历史保留PASS，counter5恢复子项PASS；marker/index恢复FAIL D04；完整退回链NOT_RUN|
|5打开/失败重试/表单/终态/完整链|解析/渲染子项PASS；恢复FAIL D04；完整操作/正常退回链NOT_RUN，指定通道BLOCKED|

|用例|本轮精确结果|
|---|---|
|G0-D|本地同digest验签/安装加载/隔离/解析PASS；附件恢复FAIL D04；真实选择/保存/打开NOT_RUN|
|T18|未登录UI未展示seed事实子项PASS；可信列表/搜索/事件/附件越权命令NOT_RUN，文本输入通道BLOCKED|
|T19|固定集合源码保持/跨任务恢复归属PASS子项；附件恢复FAIL D04；无证据/QUARANTINED/双入口拒及下载NOT_RUN|
|T20|可信只待验、自验/多角色、经理无理由拒/有理由成功NOT_RUN；输入通道BLOCKED|
|T21|旧bytes/completions保留与counter5子项PASS；marker/index恢复FAIL D04；真实退回第二completion/新round/最终验收NOT_RUN|
|T22|独立启动分裂恢复FAIL D04；精确writer/commit间注入/同盘重启通道BLOCKED，真实提交点回滚NOT_RUN|
|T28|实际installed/.running同候选加载PASS；同task附件恢复FAIL D04；操作回读/同盘再开NOT_RUN|
|T31|终态守卫源码保持；真实终态只读/再次验收拒/新关联故障NOT_RUN，不扩前序取消预约|
|T35|证据变化导致旧确认/建议失效NOT_RUN；模型迟到/交错通道BLOCKED，真实调用0|
|U03|三可信角色同task事实/按权动作/禁自验NOT_RUN；输入通道BLOCKED|
|U06|旧历史/字节保留PASS；进度/完工/验收/退回真实交互区分NOT_RUN；恢复FAIL D04|
|U07|index恢复FAIL D04；预存未提交中文清空仍观测，前序挂账；重复/丢回包/冲突/离线业务NOT_RUN，指定故障/重启通道BLOCKED|
|U08|真实未登录/空态渲染PASS子项；盘中准确失败记录改善，索引/完整件恢复FAIL D04；实际附件失败重试/无权/过期出口NOT_RUN|
|U11|真实渲染/当前已支持launch/capture运行PASS子项；可信输入/滚动/面板稳定性NOT_RUN，文本输入通道BLOCKED|

## 判定与交接

- **最终结论：FAIL**，精确范围为冻结M5-r7在固定发行宿主上的上一轮缺陷复核及8场独立直接回归。
- **剩余核心必修：D-M5-04**。优先修真实索引保存和完整文件可读恢复，遵循上文最小建议及真实验证步骤。D05危险源码分支不重复要求改，补受D04影响的动态回归。
- **阻塞/未测**：可信输入、保存后变更、精确写点、同盘重启/模型交错缺已验证白名单通道；正常/退回/独立验收与两个入口反例NOT_RUN。需要驱动/宿主能力，不需要Abram新授权。
- **前序回归**：M5字段/相对根与共用m4/m6初始化的直接冷启动回归已跑，解析/字段/轮次/审计改善及输入清空如实记；其余前序缺陷不扩修，M4继续FAIL，其他模块门禁保持原样。
- **门禁**：仅更新`docs/optimization/2026-10-09-desktop/GATES.json`中M5 status与审查字段，review_report指本报告、reviewed_candidate_id=M5-r7-worktree；此前审查字段追加history，构建字段/其他模块不改，写后结构与文件哈希核验见S/final-write-verification.json。
- **原台账**：不改`docs/build-loop/ACCEPTANCE.json`；本轮T/U结果登记M5 review_acceptance，保留旧记录/来源，未把历史后端PASS或作者自测解释为原生PASS。
- **不允许、不执行下一模块。** 留在M5修D04和补合规验证通道；没有公开发布、模型余额或其他新增授权待办。

STATUS=FAIL
NEEDS_ABRAM=no
