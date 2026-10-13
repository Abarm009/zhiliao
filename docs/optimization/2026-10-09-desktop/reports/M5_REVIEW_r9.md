# M5 独立 Review r9

**最终结论：FAIL。当前包能原生渲染，但七个合法任务盘都被误判为未闭合，M5 任务恢复分支未到达。D-M5-04 未闭合；真实上传、完工、独立验收和退回链没有运行证据。8/8 CLEAN 仅证明本轮隔离与回收成立。**

- 审查者 / 日期：本主会话唯一独立审查者，2026-10-12，Asia/Shanghai；无代理，未修改业务代码或进入下一模块。
- 被审快照：**M5-current-M4-r8-982b7c35-review-r9**，这是按用户首轮跳过构建、审当前代码要求冻结的组合快照标识，**不是新的构建方 M5 candidate_id**。最后正式 M5 交接仍是 `M5-r7-worktree / M5-r6-worktree`，实施报告 `M5_IMPLEMENTATION_r7.md`、清单 `M5/r7/CANDIDATE.json`；其源 a91f71f8/digest e6ddeed4 已不同于当前工作树，不能用旧报告描述当前包。
- 当前 HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树 dirty；源 `app/bundle/main.splash` **562062 B**，SHA256=`982b7c352da9a026a856faad75d0bf21f8b6ef36a9010ba1122acd45971c7267`。按旧 M5 冻结件、正式 M4-r8 清单、当前运输件和 M4 r10 交叉定位，未按 mtime 选版。第1段/第2段源、配置、宿主、seed 一致；结束核验见 E/final-write-verification.json。
- 当前运输件来自已授权隔离离线签名的 M4-r8；digest=`d9f2a769d26d09f0f9f333dc49fb78ec8b2e1f7acfd49f6af68f0ec6c91432d5`，anchor=`b38936f9e4d5439729077d86c79b2065d038b3a033bcf73cafd189789ac88e3c`。签名 manifest 与工作区 manifest 有 integrity/官方默认字段差异；main/model_config/identities 与当前源全字节一致，运行的完整运输包一致性另行核实。
- 前置：**M4=FAIL / M4-r8-worktree / M4_REVIEW_r10.md**，没有已接受的 M4 PASS 候选。按用户挂账裁决继续局部审查；其 B-M4-01 加载错误确实阻断本轮 M5 恢复，因此仅列最小依赖修复，不扩审或改动 M4 门禁。
- 实际宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`。
- 原生执行：外部驱动依 R 于 **11:35:35–11:37:25 +08:00** 执行，8场均 CLEAN、quit_http/rc0，无 ABORT。审查者未自启 launcher、sandbox-exec/pgrep，也未执行 osascript/辅助功能/额外 UI 自动化。
- 模型/路由：全部 needs_model=false，MiniMax 请求0，proxy/stats字段及文件缺省，无计费错误。当前主会话实际 Router/指定型号及 thread createdAt/标题工具不可核验，未冒称切换或命名。
- 阅读范围：第1段 AGENTS/CONTEXT/00/01/02/M5/04、r8缺陷/r7交接/候选、相关既有用例及源码差异；第2段 R/N、summary、全部 result/profile/完整 logs/denials/MANIFEST、运行包/业务盘/附件及截图，直接相关宿主原语源码。
- 已运行：第1段官方 hub 离线 verify；驱动本轮8场独立原生请求；第2段只读证据对账。Python 审计不执行 Splash 业务。
- 未运行：实际桌面新文件选择/保存后变更、完工与验收两个命令入口反例、可信三主体登录/多角色自验/经理理由、完整正常/退回链、同盘重开、精确提交点异常和模型迟到交错。命令未执行记 NOT_RUN；只有具体白名单通道缺口记 BLOCKED，后文给出证据。
- 边界：第1段曾误读项目外记忆索引，已在 N 披露，未作本轮判定依据。第2段显式读写均限本项目；没有读明文凭据或 provider 密钥、造 SESSION、改原业务数据、公开签名/publish/listing、push/issue/消息或部署公网。
- 置信度：候选/隔离/零parser/七个合法盘误拒/任务恢复未到达 **高**；类型根因 **高（源码及实证支持，未输出 VM 中间值）**；本轮 writer/resolver 的实际结果、可信业务链与坏件验收行为 **未知**。

## 证据与独立核验

- **H/**=`runtime/optimization/2026-10-09/M5/native-runs/review_r1_0937_REQUEST_review_r1_0937/`，驱动原证据，保留不改。
- **E/**=`runtime/optimization/2026-10-09/M5/native/review_r1_0937/`，本审查冻结件、diff、seed及审计。
- **R**=`M5/native/REQUEST_review_r1_0937.json`，SHA256=`b7951d99af3500e7576f2978f1e64f6b25caa41bf0502ed8bc64ec663a73f042`；**N**=`M5/native/REVIEW_NOTES_r1_0937.md`；短路径相对 `runtime/optimization/2026-10-09/`。
- **A**=E/native-evidence-audit-r9.json。执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r1_0937/audit_phase2.py`，rc0：**5963项证据一致性检查、0错误；不是5963项业务测试通过。**

1. H/MANIFEST **1327项**全部重新计算SHA，目录完整性/重复/作用域/摘要检查通过；R与summary.request全等，harness/template及16个保护输入、210个seed/mirror文件一致。无符号链接。
2. 每场 profile_probes.ok=true、apply rc0；外写探针被拒且created=false，5条禁读均拒；pre/post_pgrep均rc1/class=NONE/out空，pgid_members_after=[]，quit_http=ok/rc0/CLEAN。根据本场目录/控制端口/模板重建 profile，全字节及摘要一致；全部HOME/app-data/tmp/cache/config指向本场。没有agent rc71/rc3或harness ABORT阻塞。
3. written完整列表数量为 **124/126/126/125/125/125/126/126**，排序、唯一性、计数及每条真实文件/本场范围吻合，均未触400条截断。驱动记录原HOME `.octosense` mtime不变、library_scan为空；审查者仅读记录，不访问项目外目录。
4. 每场完整 sandbox-denials 按 harness 算法重算与 result 全等，包含被拒 remote:*:443、Metal缓存和/dev/dtracehelper。未从这些拒绝记录发现成功外联/越界写；拒绝并非业务运行失败本身。首场运行组额外记录 osascript，最终组为空，作为来源可追溯建议列于后文，不凭名称推定额外自动化。
5. 所有 actual installed、唯一 `.running/<ID>`、hub-mirror 的**全部包文件**逐项等于冻结运输包；catalog/seed与记录一致。main/model_config/identities对应当前源；日志业务eval为562062 B/view=true，809 B是另一系统视图。digest_seen_in_seed=true/log=false均按实际重算，不用marker代替运行副本检查。
6. 全部完整 host.log 的字节数/tail/markers独立重算一致，零[E]、parser、unknown-action、panic，正常launch-hub及remote quit。8张capture的SHA与result/MANIFEST一致，part均与对应final同字节；16个PNG均 **2560×1232**，共3种内容，已逐种目视并覆盖所有场景。差异为顶部时钟11:35/11:36/11:37；请求size不等于可操作尺寸验收。
7. 图片显示完整登录行、导航、搜索、附件标签、未登录/无可见任务空态；没有任务/附件内容或完工/验收表单。分页文字出现NaN/page[Error:NotFound]；本轮夹具未给page，归为建议/夹具边界，不据此新增安全或核心P1。未显示盘中恢复原因/入口，不能签附件错误恢复UI已通过。
8. 冷场没有tasks.json，pending=false；另外7场tasks为闭合、完整诊断数组，均主盘逐字节保留，recover逐字等于原文，却pending=true/why=“JSON截断或顶层数组未闭合（首尾字符校验失败）”。全部审计state的touched/tasks=[]、repaired_round=rounds_fixed=rebuilt_items=0，counter.by_task={}，证明任务级恢复未执行。
9. 8场index均与seed全字节相同，无index.tmp，index_saved=false/index_save_failed=false。四个非空index场只产生system:boot-reconcile审计，foreign数量2/2/1/1；任务没加载，所以这不是实际跨任务守卫运行成功。两成员仍round0，退回marker仍null；完整件缺索引项，坏/缺件内容分类未到达。**本轮不是旧r8“writer尝试后失败”的复现，不混用两轮现象。**
10. tasks历史、inbox、stored、canonical及缺件状态全部与seed一致；无新造canonical。新原/改件均220 B、首尾32 B相同、中间43 B不同，真实SHA256分别 `c8255dd58e8092e298546a52bfc1cde4c01ed32aae30493e74a5f34c78c1f8dc` / `d15f04221bdd751c3060f1d7e27fa3bf0623d93ee6b27a9f3d35b516530e828b`。参考应用指纹未原生确认，未到达内容分支也不以该值判字节校验失败或成功。
11. 8场未提交中文/intent/action-key均保留，actor清空、锁token空、tick_exception_count=0；不再把旧清空/登录裁切当当前故障。actions/events均空数组原文保持，没有真实业务final回执。proxy/stats/占位MM_KEY均不存在，符合needs_model=false。新增私钥0，离线验签rc0、原两私钥不存在证据保留。

## 必需检查

|检查|独立操作与期望|实际|结果/证据|
|---|---|---|---|
|当前快照/宿主/加载包|冻结、查完整运行资源，要求同源同digest同宿主|8场一致，工作树未漂移|PASS此子项；E/A/H|
|原生解析/工作台|新盘launch-hub/capture，零parser可见工作台|全部零错误、登录及业务空态渲染|PASS B-M5-01子项；8log/16PNG|
|隔离/回收|内核探针/完整profile/env/denials/PGID|全部满足用户指定条件|PASS；8result/profile/A|
|合法任务加载|7个闭合完整任务诊断盘；应正常加载|全部错误pending，生成recover，TASKS未进入任务恢复|**FAIL D04的最小前置依赖**；7state/tasks/recover|
|两成员round恢复|两固定成员7/index0，应counter7和磁盘两成员7|counter空，index0，touched=[]；writer未执行|整体恢复目标FAIL；writer本轮NOT_RUN；round7场|
|退回marker-only|task退回marker、index缺marker，应持久化并保留history|marker仍null，history/字节保留；未遍历任务|恢复目标FAIL；reject场|
|完整件/旧孤儿恢复|真实完整相对路径原件/canonical、缺新索引；应字节核验重建，保留旧项|旧字节/索引保持，新成员未重建；未到达内容分支|保留PASS子项，恢复FAIL；relative场|
|损坏/缺件/canonical/异任务|恢复诊断应正确分类/归属且不追认坏件|原件/改件/缺件保持；未到达任务内容/同id守卫|保全PASS子观察；分类/命令拒NOT_RUN；对应4负例|
|真实新上传与双命令拒绝|实际保存后损坏/缺失/异任务，完工和验收均拒|只执行预启动诊断seed，没有真实上传或两个命令|NOT_RUN；指定输入/后保存注入通道BLOCKED|
|可信独立验收|可信承接者、多角色、独立报修人/经理；无自验、代验理由必填|无登录/验收命令|NOT_RUN；可信输入通道BLOCKED|
|正常/退回完整链|真实填写→上传→完工→验收/退回补证→新round；核事实/回执|未执行，无业务回执|NOT_RUN；不可拿seed completion代证|
|同盘重开/异常恢复|应用保存的同盘跨进程重启、精确提交点故障|每场新盘冷启动，未有重开/提交点调度|指定白名单通道BLOCKED；命令NOT_RUN|

## 缺陷与闭合

|上轮编号|本轮判定|
|---|---|
|B-M5-01|CLOSED保留：当前8场零解析、业务渲染；旧登录裁切已改善；不代表完整业务可用|
|D-M5-01|打开/复验源码改善保持；实际上传/打开/下载/失败重试NOT_RUN|
|D-M5-02|本轮内核隔离PASS；相对根/默认字段保持；未执行resolver动态，不声称完全验证路径|
|D-M5-03|固定completion集合守卫保持；外来归属/字节原样保留，但同id任务守卫未到达；实际双入口拒NOT_RUN|
|D-M5-04|**P1 / 必修 / OPEN**：当前合法任务加载实际FAIL，恢复未到达；旧writer/resolver失败未有修复交接，不闭合|
|D-M5-05|SOURCE-CLOSED保持：缺canonical自动追认分支仍删除；内容分支和实际双入口NOT_RUN，不重复要求重修已删分支|
|D-M5-06|8场用户指定内核隔离/回收PASS；本段显式操作项目内；第1段外部索引读取偏离已披露|
|R-M5-01|CLOSED保留：独立验签和当前完整installed/.running/candidate加载对应成立|

### D-M5-04 — P1 / 必修 / OPEN：合法任务不能加载，附件恢复未到达；旧落盘/解析问题尚未闭合

- **文件行**：`app/bundle/main.splash:1310–1318`前置首尾类型校验；`:1435`恢复调用；`:8099–8109`遍历任务起点；旧必修仍在`:8024–8048`索引writer、`:8066–8082`resolver、`:7643–7654`basename、`:8184–8219`字节恢复及`:8276–8301`读回。以E冻结件为准。
- **触发**：R的round7_two_index_members或relative_intact_rebuild，以及其余5个完整诊断task场；当前签名digest/固定宿主、本场真实字节/路径正确，白名单只launch-hub/capture，不改运行盘。
- **实际**：7个合法闭合任务全部pending=true，主盘保留且被复制recover；why均首尾未闭合。任务级reconcile计数0/touched=[]、counter为空；index不变且无tmp，writer未运行。两成员不能同步到7、marker-only不能持久化、完整件不能进入可读索引。系统foreign-only审计与旧字节保存真实成立，但不代表恢复成功。
- **预期**：合法任务进入唯一事实源，恢复按已提交completion/evidence逐任务进行；固定成员/轮次/marker实际持久化，完整文件经原生字节核验可读，缺/坏/外来安全拒。成功必须读回目标，失败给可继续恢复入口。
- **根因**：当前`:1310`取to_chars码点数组，`:1313–1314`与字符串括号比较；项目内原语源码 `runtime/native-build/makepad/platform/script/src/string.rs:80–84` / `string_heap.rs:580–618`显示U32码点，合法盘及前序M4 r10同样误拒，高度支持类型不匹配。未记录VM中间值，不冒称本轮实测其具体数值。basename`:7649`同类比较仍在，旧resolver风险保持。writer/resolver/reconcile与旧M5-r7冻结件逐字相同，r8已验证失败但本轮因加载前置没重跑到；**具体writer原语原因仍未知，不宣称本轮fs.rename失败或坏件放行。**
- **影响**：核心附件/轮次/退回恢复目标无法成立，阻断硬1/4/5、G0-D/T21/T22/T28/U06/U07。这是实际核心加载失败，不是普通建议或agent沙箱限制。
- **证据**：H各7场 `home/.octosense/apps/octosense-repair/{tasks.json,tasks.json.recover,state.json,m5-test/evidence_index.json}`；四个system audit；实际附件/canonical；A逐场加载/计数/索引及真实SHA；E/source-traces、source-regression、r7-to-current.diff；旧 `M5_REVIEW_r8.md` D04的候选范围历史实证。
- **具体改法给Kimi-K3**：只修D04及确实阻断它的最小依赖，不重做M4其它流程。先将合法数组首尾判定按宿主真实类型比较，例如与 `"[".to_chars()[0]` / `"]".to_chars()[0]`，或经小probe验证的91/93；保留trim/schema/pending拒写和备份，不能清盘或移除守卫造通过。随后用固定宿主harness小probe核路径/字符串/fs.exists/read/write/rename真实行为；修basename类型及必要字符串转换，统一获准app-data相对路径；采用实证可用保存/恢复协议并逐成员/轮次/marker读回。保留旧目标与字节、系统审计和外来归属；禁止新造canonical追认坏件、改门槛或放宽profile。
- **验证方式**：冷启动零parser/渲染；合法 `[]` 和完整任务pending=false，截断/非法成员正确拒、原文和旧备份保全。然后复跑本请求7任务场，必须实际touched/task计数、counter7、两成员磁盘round7、退回marker落盘，完整件可读、旧/孤儿保留、坏件CORRUPTED/缺件MISSING/无canonical不被重建/外来不修平；应用摘要必须由原生实证，不能只沿用本审查参考指纹。最后补真正新上传→保存后变更→完工及验收均拒、正常链/退回新completion/同盘重开和失败恢复，核任务/字节/事件/回执一致。先修加载不意味着已关闭旧writer缺陷。

### 建议与受限范围

- **A-M5-R9-01 / P2 / 建议**：H/cold_no_tasks_file/result.json 的运行组出现 `osascript` 子进程，只有名称/PGID，没有参数或调用来源。用户授权内置capture，禁止额外自动化；现有记录不能区分内部capture机制与额外动作。驱动应补来源/参数及权限机制，保持现有隔离/回收，不用该名字单独推定越权P1。延续前序M4同类取证建议。
- 分页NaN/page错误字样与未认证画面中的恢复提示可见性，均列建议/未验范围；本轮夹具缺page，未实际操作面板或滚动，不凭其新增核心P1。
- 新增事件保存返回值闸只改善成功提示；权威回执/任务事件一致提交仍需真实命令，不能静态检查代签。旧输入清空/登录裁切本轮已改善，不继续要求重修。

## 硬验收与既有用例

|硬验收|本轮精确结果|
|---|---|
|1真实选择、保存、重启打开|合法任务恢复FAIL D04最小依赖；实际选择上传/保存打开NOT_RUN，可信输入/同盘重开通道BLOCKED|
|2坏/缺/隔离/异任务/无权/旧轮拒|旧D05源码关闭保持；诊断字节保全PASS，内容/同id守卫未到达，真实两个命令拒NOT_RUN；后保存变更通道BLOCKED|
|3仅待验、可信独立终验|自验/经理理由源码保持；真实主体与命令NOT_RUN，可信输入通道BLOCKED|
|4退回保留、新completion/轮次/引用|历史字节保全PASS；round/marker恢复目标FAIL D04前置；真实退回补证/再验收NOT_RUN|
|5打开/失败重试/表单/终态/全链|解析/渲染PASS子项；合法任务加载/恢复目标FAIL；真实操作/正常退回链NOT_RUN，指定通道BLOCKED|

|用例|本轮状态与范围|
|---|---|
|G0-D|PASS当前catalog/完整运行包加载/隔离/解析子项；合法任务附件恢复FAIL D04前置；实际选择保存打开NOT_RUN|
|T18|PASS未登录截图未展示seed任务正文子观察；可信列表/搜索/事件/附件越权命令NOT_RUN，输入通道BLOCKED|
|T19|固定集合源码保持，诊断字节保全；内容/归属检查未到达，真实无证据/QUARANTINED/两个入口拒及下载NOT_RUN|
|T20|NOT_RUN可信仅待验、自验/多角色、经理无理由拒/有理由成功；可信输入通道BLOCKED|
|T21|PASS旧history/bytes保全；合法任务恢复目标FAIL，round/marker未执行到；真实第二completion/新round/验收NOT_RUN|
|T22|FAIL诊断加载/恢复前置；writer本轮NOT_RUN；精确commit故障/同盘恢复调度BLOCKED，真实回滚/回执NOT_RUN|
|T28|PASSinstalled/.running同当前快照；合法任务恢复FAIL；真实操作回读/同盘重开NOT_RUN，重开通道BLOCKED|
|T31|终态源码守卫保持；真实终态只读/再次验收拒/新关联故障NOT_RUN，不扩前序取消预约|
|T35|证据变化旧确认/建议实际失效NOT_RUN；迟到模型交错通道BLOCKED，真实调用0|
|U03|NOT_RUN三可信主体同task事实/动作权限/禁自验，输入通道BLOCKED|
|U06|PASS旧history/bytes保全；恢复目标FAIL D04前置；真实进度/完工/验收/退回区别NOT_RUN|
|U07|PASS预存中文/intent/action-key保留；合法加载恢复FAIL；重复/丢回包/冲突/离线真实命令NOT_RUN，故障/重开通道BLOCKED|
|U08|PASS未登录/空态渲染子项；合法任务误入恢复FAIL，恢复原因/入口未在capture可见区域出现；真实附件失败重试/无权/过期出口NOT_RUN|
|U11|PASS业务渲染/capture子项；真实可信输入/滚动/面板稳定性NOT_RUN，可信文本输入通道BLOCKED|

**BLOCKED只限具体通道**：同SHA固定宿主前序独立 `M3/native-runs/review_r2_0937_REQUEST_review_r2_0937/restore_unknown_empty_arrays/logs/host.log:40–41` 实际拒识type/key；当前schema/harness只有启动前seed、每场新盘，无法表达实际上传后改副本、精确writer/commit中断、同盘跨进程重开或受控模型交错。需驱动/宿主提供已授权内置动作的可信键入/登录和这些调度通道，保持Seatbelt及密钥边界；不造SESSION或另用未经授权自动化。**本轮无ABORT；已运行的合法盘误拒判FAIL，未运行的业务命令判NOT_RUN，不将源码故障/前序FAIL/agent rc71或rc3笼统改成BLOCKED。**

## 判定与交接

- **最终结论：FAIL**；范围为当前组合快照及上述独立原生诊断、上轮编号/直接受影响回归，不是旧M5-r7整包再次验收，也不表示赛事/平台接入完成。
- 必修：**D-M5-04**，先修阻断M5的合法任务加载最小依赖，再关闭原有writer/resolver/实际恢复缺口。仅上述核心问题决定FAIL，建议不参与否决。
- 解阻：驱动补已验证白名单内可信输入、独立会话、保存后变更、精确故障及同盘重开，然后补真实上传、双入口反例和正常/退回验收链。不需要Abram新授权；身份/provider/离线签名已裁决，本轮模型0次、无余额/公开发布需求。
- 前序回归：确认当前共享加载错误影响M5，输入/意图保留、事件成功提示及零解析检查均在直接范围；不重审M4完整业务、不改变任何其它模块结论。
- 门禁：只更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M5审查字段，review_report指本报告，reviewed_candidate_id记录组合快照；旧r8字段追加review_history，旧构建candidate/base/实施/自测信息原样保留。`docs/build-loop/ACCEPTANCE.json` 不改，当前14项结果登记M5.review_acceptance，历史后端/旧包来源不被覆盖。结束证据 E/final-write-verification.json。
- 不允许以本结论放行下一模块；不提供或执行下一模块入口。停在M5修复交接。

STATUS=FAIL
NEEDS_ABRAM=no
