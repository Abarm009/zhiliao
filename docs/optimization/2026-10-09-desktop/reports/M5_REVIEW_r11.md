# M5 独立 Review r11

**最终结论：FAIL。D-M5-04 仍未闭合：六场需要修复索引的原生启动均将已写入、与内存成员一致的索引判为读回失败；指纹原生探针仍为全零，完整诊断附件被标为 CORRUPTED。路径字符转换、旧数组加载及业务区空白问题的对应子项已闭合。11/11 CLEAN 证明本轮隔离与回收成立，不证明真实完工与独立验收成立。**

- 审查者 / 日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai；未委派代理、未修业务代码、未进入下一模块。
- candidate_id / base_candidate_id：`M5-r9-worktree` / `M5-r8-worktree`。按用户指定构建证据、r9实施报告、CANDIDATE、GATES一致指向定位，没有按mtime选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作树dirty；源码659343 B，SHA256=`f0ba6a3f9972527cc35b8d3294fff9123f8601359848b06b29518b1405ce4983`；bundle digest=`d4e702380e758e329fa7c64997732c2ac668f6aa34b140332e7880f075011b5f`。
- 作者报告：`reports/M5_IMPLEMENTATION_r9.md`；候选清单：`runtime/optimization/2026-10-09/M5/r9/CANDIDATE.json`；唯一旧OPEN P1依据：`reports/M5_REVIEW_r10.md`的D-M5-04 A/B/C。本轮只复核这些项与直接回归。
- 前置：M4仍为`FAIL / M4-r10-worktree / M4_REVIEW_r12.md`，无已接受M4 PASS。依据用户后续前序挂账裁决继续局部重审，未改M4结论，未假称串行前置通过。
- 宿主SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`226df8dd61409cb0c82a7e70a931c2637362445d8a4a9e5232254da29188d11a`；profile模板SHA256=`80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7`。
- 实际原生执行：外部驱动于**04:27:40–04:30:12 +08:00**执行本审查独立请求，共11场，均CLEAN、quit_http、rc0，无ABORT。审查者没有在agent环境启动宿主或调用sandbox-exec/pgrep。
- 模型：全部needs_model=false，代理及model_proxy_stats缺省符合请求，MiniMax请求0，没有402/欠费。主会话实际Router/型号、线程createdAt/标题接口无法核验，未冒称切换或命名。
- 阅读范围：第1段AGENTS/CONTEXT/相关规则与模板/r10缺陷/r9交接/候选/相关用例/差异；第2段阶段笔记、独立请求、全部summary/result/profile/日志/denials/MANIFEST、业务盘/真实字节/截图及缺陷直接相关源码。
- 实际运行范围：第1段隔离夹具准备和离线验签；外部驱动11场原生启动/截图；第2段只读证据审计。Python审计不是Splash业务执行，不产生SESSION、完工或验收回执。
- 未运行：真实选择与上传、保存后的变更及两个命令入口拒绝、可信三主体/多角色/经理理由、正常/退回完整链、同盘跨进程附件重开、精确提交点中断、T35实际失效。业务动作记NOT_RUN；具体白名单能力缺口另记BLOCKED，未用rc71/rc3作理由。
- 快照：第1段保护输入到本段审计前一致；当前源与冻结源、每场installed/.running/运输包资源一致。签名运输manifest与工作树manifest不混称同一文件。最终只写本报告、M5审查字段和隔离审计证据，写后核验见E/final-write-verification.json。
- 置信度：候选一致性、隔离回收、路径修正、旧成员保全、六场失败标记及指纹全零输出**高**；导致读回失败和全零的具体宿主内部原因**未知**；可信业务全链**未知**。

## 证据与核验

以下短路径相对`runtime/optimization/2026-10-09/`：

- **H/**=`M5/native-runs/review_r1_0002_REQUEST_review_r1_0002/`，驱动原证据，保留未改。
- **E/**=`M5/native/review_r1_0002/`，冻结源、diff、seed、fixtures和审计。
- **R**=`M5/native/REQUEST_review_r1_0002.json`，SHA256=`4b6e3e947431ab2700cdcb28a428c200897024b51439d59aa9ea0ddbb3af18c1`。
- **N**=`M5/native/REVIEW_NOTES_r1_0002.md`，第1段边界与预期。
- **A**=E/native-evidence-audit-r11.json；实际命令`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r1_0002/audit_phase2.py`，rc0，**8299项证据一致性检查，0不一致；不是8299项业务测试通过**。

1. MANIFEST的**1911项**逐项重算摘要、路径作用域、唯一性及完整目录清单一致，无符号链接；summary.request与R全等。第1段339项冻结seed/镜像摘要仍一致。
2. 每场profile按实际run目录、控制口和无模型代理重建后逐字相等；profile_probes.ok=true，外写探针拒绝且created=false，5条敏感路径禁读探针均拒。全部HOME/app-data/cache/config/tmp路径位于各自run目录。
3. pre/post_pgrep均rc1、NONE、stdout/stderr空；pgid_members_after均[]，11场正常退出CLEAN。驱动记录原HOME目录mtime未变、library_scan为空；审查者只读取这些记录，不访问项目外目录。
4. 全量写入列表排序、唯一性、计数、逐文件真实存在与作用域一致，未达到400项截断；按请求顺序数量为**127/130/130/130/130/130/130/129/127/127/127**。完整denials重新计数与result一致，包含被拒443外联、Metal缓存和/dev/dtracehelper写入；拒绝记录不是成功越界证据。
5. 每场seeded_files与冻结输入对应；hub-mirror、installed和唯一.running包完整文件/摘要清单均等于冻结运输件。完整日志确实eval659343 B业务源码、view=true；host_log_bytes/tail/markers均从原文重算一致。11场无parser/type/scope诊断、panic或unknown-action，也无HOST_DID_NOT_OPEN_APP。
6. 11张最终capture加11张part，共22张PNG，实际尺寸全部**2800×1696**；result/MANIFEST摘要均正确。4种独特摘要逐种目视：均为未认证登录页，未出现业务区空白。legacy的part与final不是同摘要，分别被核验并查看所属摘要组。不能凭1280×800请求或整屏PNG签完整尺寸/工作台/表单交互通过。
7. 11场tasks/actions/events/隔离accounts原字节均保全，actions/events仍为[]；未发生真实完工/验收命令，没有新业务final回执。所有inbox/attachments/canonical/quarantine/lost+found文件集合和摘要与输入一致，新增canonical为0。
8. 本轮384 B原件与中损件首尾各32 B和尺寸相同、中段67 B不同；SHA256分别`b2c5a6da50eb11ebf78a4951839ca9f5a85325f97d43f6aa5ec3afd1a2685809`与`5454c14ff1946a8eddc472714e078ea4f653e24af57c8502e6da2af4f7beaf1e`。这些是审查者选择的预启动诊断副本，不是UI保存后的注入。
9. 模型代理字段/统计文件和MM_KEY/模型代理地址均未设置，模型0次。第1段复核作者r9两把离线私钥路径不存在、keys目录为空；本审查未生成私钥、未公开签名、未publish/listing。

运行组记录需保留的边界：basename/content/foreign三场瞬时除宿主外还记录了`osascript`进程，退出组为空。请求没有ui_actions、结果没有ui_actions_log；记录没有该进程参数，**来源与具体用途未证实**，不能据此宣称存在System Events输入，也不能宣称整个宿主进程树从未运行osascript。审查者未调用自动化；固定宿主子进程的来源追踪作为建议挂账，不凭进程名称编造越权操作。完整profile及回收判据仍符合用户指定隔离条件。

## 必需检查

|检查|独立步骤/期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/包/隔离|11场完整源包、profile/probes/env/回收对账|同源同digest同宿主，11/11CLEAN，无ABORT|PASS子项|R/H/result/profile/MANIFEST/A|
|解析与视图回归|冷空盘及旧数组/内容恢复均应零诊断且渲染|11场零parser/type/scope，业务eval=view=true，登录页可见|PASS子项，登录后工作台NOT_RUN|全部完整log/22PNG|
|D04-A字符与路径|英文/中文探针；旧abs登记回退当前文件|b.txt/bc/中文附件.txt/文ab/hi正确；新stored_rel指向真实文件，已读至内容检查|PASS路径子项；最终READY未过C|basename/probe/index/真实文件|
|D04-B旧数组/v3|各4旧项，两成员0→9/counter9、旧归属保留、读回成功|两场4项全保留、round/counter9已落盘，state索引成员与磁盘全等；两场却index_saved=false/save_failed=true|FAIL恢复核验，加载/保全子项PASS|legacy/envelope index/state/audit/tmp|
|D04-Btmp退回恢复|截断主盘+完整tmp，round4/marker落盘、确认成功|4项保留、counter4、两marker1791786000999、目标已写、tmp0B；仍save_failed=true|FAIL恢复核验；标记/保全子项PASS|marker index/tmp/audit/history|
|D04-B非法形状|无items对象、items字符串、标量23，不采纳/不覆盖|3场原主盘字节不变、内存索引[]、无诊断/假恢复成功|PASS拒识别与保全子项|3场seed/index/state/log|
|D04-C完整/异常分类|正确路径，原件==canonical、登记摘要可核；中损/缺stored/缺canonical拒信任|完整件CORRUPTED且无签名；中损CORRUPTED、缺stored MISSING、缺canonical CORRUPTED，未造基准|FAIL完整件/摘要核验；异常分类子项PASS|content/basename/probe/bytes/index|
|D03/D04外来归属|同id外来索引不能重绑本任务|外来task/round2和旧orphan保全；foreign计数2含碰撞及不存在任务计数|PASS归属子项，恢复核验仍FAIL|foreign index/audit/tasks/bytes|
|直接任务加载回归|完整合法任务加载；截断任务安全保全|合法pending=false；截断pending=true，tasks/recover全字节一致|PASS限定加载子项|11tasks/state、truncated recover/log|
|保存后反例/双入口|真实上传后改副本，再提交完工/验收均拒|只执行预启动诊断seed，没有这两个命令|NOT_RUN；具体通道BLOCKED|R/schema、空actions/events|
|可信独立验收|可信登录，多角色禁自验，经理无理由拒/有理由实收|没有可信登录或验收动作，截图停在登录页|NOT_RUN；输入通道BLOCKED|R/frames/actions/events|
|正常/退回链/重开|实际命令产生新completion/终验，真实同盘重开附件|11场各新盘冷启动，不是成功链/退回链/同盘重开|NOT_RUN；调度通道BLOCKED|R/schema/事实盘|

## 缺陷与上轮闭合

保留唯一旧P1编号**D-M5-04**，以下是该编号的修复子项，不发散新业务范围。

### D-M5-04 A：CLOSED（精确限路径字符转换与回退）

`app/bundle/main.splash:2002`的U32数组切片转换已实测正确，`:8552`basename和`:9130`resolver生成`attachments/review0002r1-new-basename.txt`，当前stored/canonical均能被读取，未再发生十进制文件名或误报MISSING。英文/中文探针通过。后续CORRUPTED及读回失败分别归入C/B；实际UI打开与同盘重开仍NOT_RUN，不能扩大关闭范围。

### D-M5-04 B：OPEN / P1 / 必修——写入成功后的权威核验仍报告失败

- **文件/行**：`app/bundle/main.splash:8939`索引extractor、`:8959–9004`writer、`:9006`loader、`:9363–9389`reconcile写后成员核验，尤其`:9368`读取/抽取及`:9387`失败分支。
- **触发**：执行R的legacy_round9/envelope_round9，两个权威成员round9、索引round0，附旧orphan和foreign；以及marker_tmp_recovery、basename/content/foreign直接恢复场。
- **实际/预期**：六场目标索引已写成有效v3，磁盘items与最终state.attach_items结构全等、tmp已清空，audit/state却均`index_saved=false,index_save_failed=true`，状态文案称“保持拒绝态，可安全重启重试”。预期正确载入和逐成员读回后承认恢复成功；失败时准确指明失败点，保全恢复副本。
- **根因**：旧catch绑定和旧数组丢失问题已消失；当前异常集中在writer返回之后的核验结果链。tmp清空且目标正确支持writer完成到末尾的推断；究竟是返回值、extractor形状/成员类型、比较还是宿主VM控制流，**尚无分步原生probe，不作定论**。不能沿用r10“writer未到达”解释本轮。
- **影响**：恢复结果与真实存储事实矛盾，本模块无法取得可信“附件索引已恢复并核验”的结果。界面状态声称拒绝不等于本轮已验证所有业务命令真的拒绝；这些命令未执行。违反硬1/4/5的恢复结果要求，影响T21/T22/T28/U06/U07/U08。
- **证据**：H上述六场的`m5-test/evidence_index.json`、tmp、audit和state；A中的state_index_items_equal=true与六个失败标记、旧成员及真实字节清单。旧数组/v3两场均4项，不再混称旧项丢失。
- **具体改法**：构建方先在固定宿主记录`m5_save_attach_index`实际返回值、读回raw/extractor成功与否、两侧长度、每个attach_id/round/lifecycle的实际比较结果及失败原因；用已实证原语修正这一最小链。失败副本保留到**整个核验成功**，不能只把失败旗标硬改为成功、清空历史或移除读回闸。
- **验证方式**：复跑六场；两种格式两成员round9、counter9、marker/counter4、旧归属/字节全保留，state和audit均index_saved=true/save_failed=false；正常完成核验后才清tmp，故障时须保留有效副本。随后由可信实际完工/退回命令及同盘重开确认此恢复协议，不以Python结构相等代替原生成功。

### D-M5-04 C：OPEN / P1验收未闭合——数值类型报错已消失，指纹结果与内容恢复仍未通过

- **文件/行**：`app/bundle/main.splash:8793–8824`数值mix/fingerprint，`:5494–5505`_hex32；`:9098–9103`固定指纹probe；`:9281–9308`canonical/大小/登记指纹重建闸。
- **触发**：11场启动内置`m5_fingerprint("M5 probe ABC xyz 123")`探针；basename和content场对当前真实完整384B、与canonical相同的诊断文件执行内容恢复。
- **实际/预期**：11场probe均`00000000`；声明的兼容整数算法独立参考为`50ce396a`。完整诊断件登记参考sha=`7bedec07`、字节/canonical/尺寸均一致，却为CORRUPTED、content_signature=null。预期原生摘要实际可用且旧登记兼容可解释，完整件完成内容核验；异常件保持拒绝。
- **根因**：原r10的数值调用字符串方法错误已关闭，工作台不再因此空白；新路径的mix/整数范围/转换/_hex32具体哪一步失真**未知**。Python等价65/65不能证明固定宿主整数运算等价。
- **证据限制**：本轮任务sha为独立诊断参考，不是真实UI上传生成摘要。因此不把参考值不匹配单独说成“合法新上传被误拒”，也未观察坏件被验收放行。P1未闭合指上一轮要求的**真实摘要/登记兼容与完整附件恢复验证**仍不成立，不把每个指纹碰撞扩成新安全缺陷。
- **影响**：不能证明真实登记摘要有效或既有登记可恢复，固定集合内容核验及附件重开仍没有通过证据；涉及硬1/2/4/5、G0-D/T19/T21/T28/U06/U08。
- **证据**：H全部probe；content/basename的原文件/canonical/index/state；A逐成员分类。异常件分类正确，不编造“损坏检测已绕过”。
- **具体改法**：构建方先用固定宿主分步probe核`_hex32(1)`、初始值、一次mix、乘法/掩码/移位和实际ASCII/中文/控制字符摘要，确定原语后仅修此直接依赖；保留canonical全内容比对和固定集合核验。若摘要语义必须变更，显式版本化/兼容，不能把现存坏文件追认为原基准或批量改sha为全零。
- **验证方式**：固定literal probe结束且结果符合所选算法定义；真实新文件上传生成登记摘要，再重读同文件应通过，保存后同尺寸中损应拒，缺stored/缺canonical保持拒绝且不造基准；分别执行完工及验收入口。对已存在登记明确证明兼容策略，诊断参考测试与真实上传测试分开记录。

### 其他原缺陷与建议

- **B-M5-01**：零解析错误及本轮11场业务eval/登录视图CLOSED保留；不替登录后工作台交互签验收。
- **D-M5-01/02/03/05**：原关闭结论按其精确源码/历史范围保留，本轮不扩大到真实业务动作。外来归属保全、异常件分类、缺canonical不制造基准、内核隔离已做针对性回归；真实打开/下载/重试、权限命令和双入口拒绝仍未测。
- **A-M5-R11-01 / P2建议**：固定宿主子进程记录出现osascript而没有参数/来源；建议驱动下轮记录完整argv及父链，区分宿主内部行为与被禁的UI自动化。无证据不认定具体越权，不因该建议判FAIL。
- 本轮偏好诊断seed被loadViewState判为不完整并保留recover/default；任务事实加载及M5索引对账仍已实际执行。此为审查seed范围限制，不扩M2偏好校验为新P1；未提交输入保全不得沿用上一轮PASS。

## 硬验收与既有用例

|硬验收|本轮判定及边界|
|---|---|
|1 真实选择/重启打开|FAIL D04恢复核验/摘要未闭合；路径子项PASS，实际UI选择/保存/同盘重开NOT_RUN|
|2 异常证据双入口拒绝|异常件分类/外来归属/不造canonical子项PASS；完整件及恢复核验未过；实际两个入口拒绝NOT_RUN|
|3 待验与可信独立终验|NOT_RUN；源码禁自验/经理理由守卫仍在，不能替可信会话实证|
|4 旧证据保留/新轮次引用|旧4项/字节、round9/marker/counter4落盘子项PASS；应用核验FAIL；真实退回、新completion/再验收NOT_RUN|
|5 桌面全链/失败恢复|11场登录页/零解析子项PASS；恢复核验FAIL；表单/终态/打开/重试/正常退回链NOT_RUN|

|用例|本轮状态与范围|
|---|---|
|G0-D|FAIL D04核心恢复；完整本地包/隔离/路径子项PASS，真实文件选择/上传/打开NOT_RUN|
|T18|NOT_RUN可信列表/搜索/事件/附件探测权限；未登录截图未展示seed正文仅为子观察|
|T19|FAIL完整附件内容恢复未过；坏/缺/无canonical分类、外来归属PASS子项；无证据/QUARANTINED/双入口拒/下载NOT_RUN|
|T20|NOT_RUN可信AWAITING/禁止自验/多角色/经理理由执行|
|T21|FAIL应用恢复核验；旧记录/字节、轮次/marker落盘PASS子项；真实新completion与再验收NOT_RUN|
|T22|FAIL恢复结果；tmp内容恢复及截断原文保全PASS子项，精确提交点异常/全部回滚/真实回执NOT_RUN|
|T28|FAIL恢复/完整件未可读；installed/.running同包PASS子项；实际操作回读/同盘重开NOT_RUN|
|T31|NOT_RUN终态只读/重复验收拒绝/关联新故障，源码守卫保留；不扩取消预约前序挂账|
|T35|NOT_RUN真实证据变化后确认/建议失效；0模型调用不代表此项通过|
|U03|NOT_RUN三可信角色同task事实/按权动作/禁自验|
|U06|FAIL应用恢复核验；旧completion/字节和轮次marker保全PASS子项；真实进度/完工/验收/退回区分NOT_RUN|
|U07|FAIL恢复结果；截断tasks/recover保全PASS子项；偏好seed走默认，不迁移旧输入保全PASS；重复/丢响应/冲突/离线命令NOT_RUN|
|U08|FAIL恢复核验/完整件CORRUPTED；登录/异常分类子项PASS；真实重试/无权/过期出口NOT_RUN|
|U11|NOT_RUN真实滚动/输入/面板稳定性；本轮11场零解析及登录渲染PASS子项，无新增空白|

## 判定与本模块修复交接

- **最终结论：FAIL**；唯一旧P1 D-M5-04仍OPEN，A精确关闭，B/C按上述清单修复及补验证。建议项不作为FAIL依据。
- 精确通过范围：零解析/11场登录视图、英文中文切片与basename回退、旧数组/v3加载、旧索引/真实字节保全、轮次/退回marker实际写入、外来归属、异常分类、截断任务保全、完整运行包一致、隔离与回收。**写入发生不等于应用权威核验成功，也不等于业务验收成功。**
- 本轮没有ABORT。只对当前白名单不能覆盖的具体能力记BLOCKED：符合本轮授权的可信文本/键盘输入，上传后的隔离副本变更，同Store跨进程重开，精确提交点中断。实际未执行业务动作仍记NOT_RUN；不以agent rc71/rc3解释。
- schema的ui_actions依赖osascript/System Events，本轮原始指令仍禁用；固定同SHA宿主type/key不支持的既有原生实证见M3_REVIEW_r10和M5_REVIEW_r10。本schema只支持预启动seed及每场新目录，没有运行中注入/同Store重开调度字段。需驱动提供获准内置输入与副本/重开/故障步骤；不得伪造SESSION、回执或把预启动成功状态当实际命令链。这些是技术缺口，**NEEDS_ABRAM=no**。
- 构建方Kimi-K3先harness冷启动零解析，严格只修D04-B/C及直接依赖，再复跑本轮11场及真实上传/双入口拒绝、可信独立验收、正常/退回/同盘重开链；保留canonical、固定集合、权限与历史。
- 受影响前序仅合法/截断任务加载和初始化做针对性回归；M4 FAIL与其他模块挂账不动，不宣布历史自动PASS。
- 门禁：仅更新GATES.json的M5审查字段及status=FAIL，review_report指向本报告、记录本候选/独立证据，并归档r10审查来源。构建字段与其他模块保持一致；原ACCEPTANCE.json不改，适用结果在M5.review_acceptance保留历史来源。
- 不允许下一模块，未执行M6。
- 第2段仅在项目内读写，不读取明文凭据或provider密钥，不执行发布/上传/公开签名/listing/push/issue/评论/消息/部署或更换计费渠道。第1段一次项目外记忆检索偏离已在N记录，未作为本判定证据。

STATUS=FAIL
NEEDS_ABRAM=no
