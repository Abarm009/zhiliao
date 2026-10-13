# M5 独立 Review r10

**最终结论：FAIL。D-M5-04 未闭合：完整附件路径回退变成数字串；旧数组索引恢复及可读附件重建触发数值/字符串类型错误，两场业务区空白。新信封的轮次/退回标记持久化子项通过，但不能代替真实附件完工及可信独立验收。8/8 CLEAN 只证明本轮隔离与回收成立。**

- 审查者 / 日期：本主会话唯一独立审查者，2026-10-12，Asia/Shanghai；未委派代理、未修改业务代码、未进入下一模块。
- candidate_id=`M5-r8-worktree`；名义 base=`M5-r7-worktree`；实际修复比较基线是 r9 冻结的、含 M4-r8 运输件的 `982b7c352da9a026a856faad75d0bf21f8b6ef36a9010ba1122acd45971c7267`，不是原 r7 代码。按交接、候选清单、GATES 和用户指定构建证据定位，未按 mtime 选版。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树 dirty；`app/bundle/main.splash` 573476 B，SHA256=`6a7176e84a6f3692690d1d566129a0c57ea747f0c3fc5b943b9039a8b298d4c4`。
- bundle digest=`08c64f5600244854a63df93eb76ce3a2d1ca46f74d8f9195e00a32b43f1fd441`；anchor=`6b4c6bb9e3c13dca1cc2124abeeec0659aa8e533991ca4f851eba67e62908148`。当前完整运输包、installed/.running 包与冻结运输包逐项一致；源/model_config/identities 与工作树全字节一致。签名运输件 manifest 的 integrity/默认字段与工作树 manifest 有差异，未混称同一完整文件。
- 作者报告：`reports/M5_IMPLEMENTATION_r8.md`；候选清单：`runtime/optimization/2026-10-09/M5/r8/CANDIDATE.json`；上一轮依据：`reports/M5_REVIEW_r9.md`，唯一 OPEN P1 D-M5-04。
- 前置：M4=`FAIL / M4-r8-worktree / M4_REVIEW_r10.md`，没有已接受的 M4 PASS。依用户后续前序挂账裁决继续本模块局部重审；保留 M4 结论，仅复核合法任务加载这个直接依赖，没有改 M4 门禁或扩审其他流程。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`c46ba53a6d84b9a1cf288a06f2921990a3939a272d66f870d7a61932400b9dc9`；profile 模板 SHA256=`80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7`。
- 实际原生执行：外部驱动于 **12:25:08–12:26:57 +08:00** 执行本审查独立 R，8场 CLEAN，均 quit_http/rc0，无 ABORT。审查者未自己启动 launcher、sandbox-exec/pgrep、osascript 或辅助功能/自动化。
- 模型/路由：needs_model=false 全部成立，MiniMax 请求0，proxy/stat字段及文件缺省符合请求，无余额/402错误。本主会话 Router/型号与 thread createdAt/标题接口不可核验，未冒称切换或命名。
- 已阅读：第1段 AGENTS/CONTEXT/00/01/02/M5/04、r9缺陷/r8交接/候选/相关用例及差异；第2段阶段笔记、R/H全部 summary/result/profile/日志/denials/MANIFEST、业务盘/字节/截图及直接相关宿主源码。没有无关扩审。
- 已运行：第1段隔离离线验签与请求准备；驱动本轮8场独立原生冷启动；第2段只读证据审计。Python审计没有执行 Splash 业务，也未伪造 SESSION 或动作回执。
- 未运行：真实新文件上传、保存后变更、完工/验收双入口反例、可信三主体/多角色自验与经理理由、正常/退回完整链、同盘跨进程重开、精确提交点故障和 T35 实际失效。操作均记 NOT_RUN；仅有确切白名单通道缺口的能力记 BLOCKED，后文说明。不以agent rc71/rc3判阻塞。
- 快照：第1段冻结、第2段审计前的源码/配置/宿主/seed及保护输入一致；最终写入只变本轮报告与 GATES 的 M5审查字段，核验见 E/final-write-verification.json。
- 置信度：候选/隔离/路径数字化/两场原生空白/轮次与marker落盘 **高**；旧数组loader每步VM控制流和body最终返回错误的具体内核原因 **中/未知**；真实可信业务链 **未知**。

## 证据与独立核验

以下短路径相对 `runtime/optimization/2026-10-09/`：

- **H/**=`M5/native-runs/review_r2_0937_REQUEST_review_r2_0937/`，驱动原证据，保留不改。
- **E/**=`M5/native/review_r2_0937/`，本审查冻结源、diff、seed、fixtures及审计。
- **R**=`M5/native/REQUEST_review_r2_0937.json`，SHA256=`fae6fdd6906ebad27fe1d8df6e83188b0a2f5ee0b1a18077ed17c2011d609183`。
- **N**=`M5/native/REVIEW_NOTES_r2_0937.md`，第1段范围/预期/缺口。
- **A**=E/native-evidence-audit-r10.json。实际执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r2_0937/audit_phase2.py`，rc0：**6198项证据一致性核对、0不一致；不是6198项业务测试通过。**

1. MANIFEST **1391**项逐一重算SHA、作用域、重复、完整目录清单及符号链接检查均通过；R与summary.request全等，保护输入、全部seed/mirror哈希一致。
2. 全部 profile 与按本场路径/控制端口重建的模板逐字相等；profile_probes.ok=true，apply rc0；外写探针拒绝且created=false；5条敏感路径禁读均拒。HOME/app-data/tmp/cache/config均位于本场目录。pre/post_pgrep均rc1、NONE、out/err空，pgid_members_after=[]，宿主正常退出/CLEAN。驱动记录原HOME目录mtime未变、library_scan为空；审查者只读记录，不访问项目外目录。
3. 完整 written列表各场数量按请求顺序 **126/124/129/129/124/129/129/128**，排序、唯一性、真实存在和本场作用域吻合，均未触400项截断。全量denials重算与result一致：外部443、Metal缓存、/dev/dtracehelper被拒；未发现成功越界写/外联证据。8场运行组仅有本场宿主，退出组为空。
4. 每场 hub-mirror、installed以及唯一 `.running/<id>` 的完整文件清单/摘要均等于冻结运输包；日志确实eval 573476 B业务脚本。另一个809 B系统视图不是业务成功证据。digest_seen_in_seed/log按真实内容重算，不凭 marker 代替完整运行副本核验。
5. host_log_bytes/tail/markers全部从完整日志重算一致。8场无 parser/[E]/panic/unknown-action；**但legacy/content的脚本错误记录为[I]，分别1069/1072条，而且573476 B业务eval均view=false**。其他6场view=true、没有该类诊断。不能把“零[E]”“panic=false”当作零业务错误。
6. 8张capture及8张part PNG的SHA、实际格式/尺寸和result/MANIFEST一致；均 **2560×1232**，part与final同字节。共有6种独特截图，已逐种目视，覆盖其余2张同SHA截图：两场legacy/content业务区确实空白，另6场显示登录/导航/空态或无可见范围。未认证，不展示诊断工单正文；未执行表单/滚动/上传/验收操作。请求size不是完整桌面尺寸验收。
7. 8场原始 tasks/actions/events/隔离accounts原文不变；actions/events仍为[]，没有业务final回执。inbox/attachments/quarantine/lost+found真实文件及canonical缺失状态全与seed一致，新造canonical为0。新原件/中损件均256 B、首尾32 B相同，中间49 B不同，SHA256分别 `39f21955899ad70332972dd2a81381bbb2cc198cfd8b8d020ff186274aa7d54d` / `1f9f16b8bb661418db80464751406db73463f86f6135adbd8329331ad973fb10`。
8. 未提交中文、intent、action-key、panel/detail_tab保留，actor=null，m2_lock_token空，tick_exception_count=0。**tick异常为0仍不证明初始化成功：两个失败场在根视图形成前已经失败。**
9. 模型环境/代理/stat不存在，模型调用0。未新增私钥；第1段已重新核验 build_r8 私钥删除与keys空的证据，未读取私钥内容。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/包|冻结并核完整installed/running/运输件|同源同digest同宿主|8场全部一致|PASS子项|E/A/H全包、日志|
|隔离与回收|8场profile/probes/env/denials/PGID对账|用户指定条件全部成立|8/8 CLEAN，无ABORT|PASS|8result/profile/denials、A|
|冷启动/合法空数组|cold_empty seed为[]|零解析、工作台渲染、pending=false|正确|PASS|cold_empty state/log/frame|
|合法/截断加载回归|合法空数组及6个完整任务/1个截断副本|合法进入事实源，截断保全并拒写|完整pending=false；截断pending=true且recover全字节等原文|PASS限定加载子项|8tasks/state/recover；完整恢复两场仍失败|
|旧数组round9|legacy_round9四旧成员，两固定成员0→9|保留全部旧项并修两成员/counter9|主盘旧4项原样，但恢复未完成、counter空、无audit/probe；业务空白|**FAIL D04-B/C**|legacy result/log/frame/index/state|
|v3 round9|与旧数组同结构/字节，诊断task_id不同|2成员9、counter9、旧orphan/foreign保留并读回|全部成立；repaired_round=2、rebuilt=0、orphan=1、foreign=1|PASS持久化子项|envelope index/tmp/audit/state|
|basename-only重建|只旧absolute登记；当前完整原件/canonical真实存在|正确相对回退并进入字节检查|stored_rel数字化，完整件MISSING；新索引落盘不代表可读|**FAIL D04-A**|basename index/probe/bytes/audit|
|显式相对路径字节重建|content矩阵：完整/中损/缺件/缺canonical|正确分类并保留orphan、无追认基准|首个完整件进入指纹类型错误，业务view=false；4新项未落盘，后续分支未证实|**FAIL D04-C整体恢复**；后续坏件分类NOT_RUN|content全log/frame/index/state|
|同id外来索引|foreign_collision_v3|不改foreign所有权/round2，保留orphan/字节|正确；foreign计数2包括碰撞及不存在任务计数，不当两个独立附件|PASS归属保全子项|foreign index/audit/tasks/bytes|
|退回marker/tmp|主索引截断、完整v3 tmp，退回round4|保留4旧项/旧completion，2marker落盘，counter4，tmp成功后清空|全部成立，目标4项，两个marker=1791786000999，tmp0 B|PASS启动恢复子项|marker index/tmp/state/audit/history|
|真实新文件上传后双入口拒|真实上传后改实际保存副本，再提交完工/验收|两个入口对坏/缺/跨任务均拒|本轮只跑预启动诊断seed，没有真实上传或两命令|NOT_RUN；具体通道BLOCKED|R/N/schema/固定宿主既有type/key实证|
|可信自验/经理理由|可信独立会话、多角色、无理由/有理由|禁承接者自验，理由真实有效|无登录/验收命令，无可信会话|NOT_RUN；获准输入通道BLOCKED|8frame/空actions/events|
|正常/退回链/同盘重开|真实命令形成新completion、轮次、终验、重启打开|UI/字节/任务/回执一致|8个新盘冷启动，未跑全链或同盘重开|NOT_RUN；指定调度通道BLOCKED|R/schema/空actions/events|

已有索引的 READY 值在启动对账中保持，不是本轮重新验字节所得；v3/marker的PASS只限权威轮次、标记、保全和落盘，不签文件完整性或业务验收通过。

## 缺陷与上轮闭合

|上轮编号|本轮判定|
|---|---|
|B-M5-01|解析/冷启动子项CLOSED保留；旧数组/字节重建空白记入D04，不能声称所有初始化场景均可渲染|
|D-M5-01|内容出口和重解析源码保留；真实上传/打开/下载/重试NOT_RUN；路径失效另见D04|
|D-M5-02|本轮内核隔离PASS，合法相对路径可用于已登记索引子观察；真实路径输入/权限/上传仍NOT_RUN|
|D-M5-03|固定集合源码保持；同id外来索引恢复保全PASS子项；实际完工/验收双入口拒NOT_RUN|
|D-M5-04|**P1 / 必修 / OPEN**；加载依赖及v3/tmp持久化部分闭合，A路径/B旧数组/C字节指纹类型链仍失败|
|D-M5-05|危险自动canonical追认分支SOURCE-CLOSED保持；没有新canonical。content失败后未跑到后续缺canonical分类，不能以字节保全冒称动态拒绝已通过|
|D-M5-06|8场用户指定隔离/回收PASS；第2段显式读写均在项目内；第1段外部索引范围偏离已在N记录|
|R-M5-01|CLOSED保留，同digest验签、完整installed/running包一致成立|

### D-M5-04 — P1 / 必修 / OPEN：路径仍误判缺件，旧数组与真实字节恢复不能完成

以下A/B/C是同一旧缺陷的具体修复清单，不引入无关模块整改。每项都直接阻断核心附件恢复/可读性。

**A. 路径字符切片把码点拼成十进制。**

- 文件/行：`app/bundle/main.splash:1664–1681`（`:1678`字符串+U32），`:7659–7675`basename，`:8228–8245`resolver，`:8351–8374`重建相对路径。
- 触发：R/basename_only_rebuild，当前app-data有真实256 B完整文件与canonical，任务只有失效旧absolute登记，无stored_rel。
- 实际：probe `a/b.txt→9846116120116`、`abcdef[1:3]→9899`；磁盘新成员stored_rel为十进制码点串，lifecycle=MISSING；counter9/index_saved=true仍无法读文件。
- 预期：basename=b.txt，slice=bc，派生登记真实字符相对路径，完整件进入真实字节核验；旧orphan/字节保留。
- 根因：to_chars返回U32，比较类型已修，但 `_strSlice`没有码点→字符转换；根因置信度高。
- 影响：重启后按任务重建的合法附件无法重新打开，阻断硬1/4/5、G0-D/T21/T28/U06/U08。
- 证据：H/basename_only_rebuild 的 `m5-test/{evidence_index.json,m5_fs_probe.json,m5_reconcile_audit.json}`、实际attachments/canonical；A对应场，frame/log。
- 最小改法：用当前固定宿主经probe证实的字符串/码点转换实现必要切片和basename；不得把码点 `.to_string()` 当字符转换，不得造数字文件名或放宽profile迁就错误。只改D04直接依赖。
- 验证：harness真实probe应得到上述字符结果，中文路径不损坏；复跑basename场，新登记路径必须等于真实文件路径、可读，不能再因数字路径报MISSING。随后跑真正保存/重开入口。

**B. 旧顶层数组索引不能完成兼容加载与恢复。**

- 文件/行：`:8057–8071` m5_index_items_from_raw，`:8120–8137` loader（`:8124/:8131` catch `_`路径）；`:8307–8343`已有成员修平。
- 触发：R/legacy_round9四成员旧数组，两个task固定成员round9、index0；配对v3 envelope_round9使用等价结构/同字节、独立诊断标识。
- 实际：legacy业务view=false；完整日志第47行报 `variable _ not found in scope`（VM定位8127:83，源位置以冻结清单为准），后续进入C的类型错误；磁盘旧4项仍原样、counter空、无恢复audit/probe。v3控制则两成员round9、counter9、4旧项保留、tmp清空、目标读回成功。
- 预期：旧数组与v3均被正确加载，修平相同旧成员，保全旧orphan/foreign，不能退化成空索引重建后失败。
- 根因：数组/信封形状识别依赖 `raw.items` / 非nil / len；数组缺字段和宿主错误值/catch语法没有按真实VM适配。配对控制与错误位置支持loader问题，具体VM每步返回值未记录，根因细节置信度中。不是本轮writer已执行失败。
- 影响：既有附件索引升级无法恢复，实际业务工作台空白；阻断硬1/4/5、T21/T22/T28/U06/U07。
- 证据：H/legacy_round9的完整log第47行起、frame/index/state；H/envelope_round9完整控制结果；A。**第1段作者证据曾观察孤儿项被覆盖丢失，本轮独立legacy因初始化失败尚未覆盖磁盘，不混称本轮已删除旧项。**
- 最小改法：先用固定宿主probe确认旧数组与v3识别、无items/错误值和catch行为，明确检查数组/对象形状，避免访问旧数组的不存在items；只采用宿主实证的catch写法。可参考本工程已实际用于合法task加载的数组判定，但仍需独立验证。加载失败保全原盘并显示安全恢复，不能默默转空数组。
- 验证：复跑legacy/v3等价控制，两场业务view=true；两成员round9、counter9、旧4项/归属/marker全保留，无scope/type错误。再测截断/无items信封/非法items，正确拒绝并保全，不能只凭len接受任意对象。

**C. 真正读取完整附件后，指纹函数把U32传入字符串方法，初始化失败。**

- 文件/行：`:7907–7942` m5_fingerprint（`:7917/:7921`码点传入反查）；`:7959–7982`反查；`:1683–1704` _strIndexOf（`:1689` needle.to_chars）；`:8380–8405`实际恢复读取/指纹比较。文件行来自E/source-traces，与宿主VM日志定位1692/1694略有偏移，不把VM跨度号当源精确行号。
- 触发：R/content_rebuild_matrix首个文件使用明确正确stored_rel，完整bytes==canonical；缺新索引使恢复必须真读256 B内容。legacy旧数组退化重建也进入该链。
- 实际：content完整日志第51行起反复报 `method to_chars not found on number`、`method len not found on error`、`call target is not a function`；合计1072条脚本诊断（含少量前序缺字段），业务eval=view=false，截图业务区空白。index仍只有原orphan，m5_last_reconcile=null、counter空、无probe/新tmp；后续中损/缺件/无canonical分类没有运行证据。
- 预期：合法字符串/字节指纹计算结束，不调用数值不存在的方法；实际完整件/坏件/缺件逐件安全分类、落盘，失败可继续恢复，工作台可渲染。
- 根因：chars[i]为U32，反查仍当字符串传给 _strIndexOf；这次已由原生日志实证，超出第1段仅“可能区分度退化”的判断。body最终错误返回的内核细节未直接输出，不断言确切指令预算原因。
- 影响：一条正常可读附件就阻断启动重建和业务视图；不能完成核心附件/完工核验，影响硬1/2/4/5、G0-D/T19/T21/T22/T28/U06/U07/U08。
- 证据：H/content_rebuild_matrix完整log第51–1127行、末尾573476 B view=false、frame、index/state/真实文件与canonical；legacy对应log；A的逐错误计数与位置。
- 最小改法：直接消费实测数值码点，或通过宿主确有的字符转换后再进行字符串反查；字节摘要需真实字节语义，不能把码点循环说成UTF-8字节循环。保留canonical全内容比对；若摘要语义变更，显式版本化并处理旧登记，不静默把现存文件追认为基准。保持安全失败，不能删除指纹/内容闸或只看readyCount。
- 验证：用固定宿主对本轮原件、中损件、中文/控制字节小probe取得实际摘要，不能沿用Python参考值当原生证明；两种指纹计算应结束且无type/scope错误。再复跑content矩阵，坏件CORRUPTED、stored缺件MISSING、无canonical拒绝且不新造基准，完整件与原生保存摘要一致后可读；最后补真实上传→保存后变更→完工/验收两入口拒绝。

本轮登记指纹是独立诊断参考算法值，未由真实上传生成。因此不以参考摘要不匹配本身判“合法上传坏件”；C在比较登记摘要前已经调用了数值不存在的字符串方法，类型错误、恢复失败和空白是直接实测。未发生坏件验收放行，不编造该结论。

### 建议与挂账

- **A-M5-R10-01 / P2 / 建议**：harness/result的panic/[E]/tick计数与CLEAN容易被误读为业务成功。完整log还需提取 `[I] splash:` 类型/scope错误和业务脚本view=false；本轮已独立审计，不改harness。建议构建方自测加入这一判据。
- legacy/content日志中的m4/m6缺字段多数与部分STATE诊断seed有关，v3控制可渲染；不扩这些前序挂账为新P1。只处理确实阻断D04的字符/loader/指纹链。
- 6场未登录工作台截图未显示盘中对账/恢复详细原因，不证明已提供附件错误恢复UI。作为建议/未验范围记录；本轮FAIL依据是明确核心D04，不因显示建议或未认证夹具要求扩修皮肤。

## 硬验收及既有用例

|硬验收|本轮结果|
|---|---|
|1真实选择/保存/重启打开|FAIL D04-A/C启动附件恢复；实际选择上传/保存后重开NOT_RUN，获准输入/同盘重开通道BLOCKED|
|2坏/缺/隔离/异任务/无权/旧轮双入口拒|PASS外来归属保全子项；D05源码关闭保持；FAIL content整体恢复，后续分类未到达；实际双入口拒NOT_RUN|
|3只待验、可信独立终验|源码守卫保持；真实三主体/多角色/经理理由和命令NOT_RUN，获准输入通道BLOCKED|
|4旧证据保留、新completion/轮次/引用|PASS v3两成员round9、counter、marker/tmp及旧字节保全；FAIL旧数组恢复；真实退回/新completion/再验收NOT_RUN|
|5打开/失败重试/表单/终态/全链|PASS6场渲染及隔离子项；FAIL两场原生空白、完整件MISSING；实际正常/退回/打开/重试/终态操作NOT_RUN|

|用例|本轮状态及范围|
|---|---|
|G0-D|PASS同digest完整本地包加载/隔离/冷启动；FAIL路径/旧数组/字节重建；真实选择/上传/打开NOT_RUN|
|T18|PASS未登录截图没有seed正文子观察；可信列表/搜索/事件/附件探测权限命令NOT_RUN，获准输入通道BLOCKED|
|T19|PASS同id外来索引归属保全、固定集合源码保持；FAIL字节恢复；真实无证据/QUARANTINED/双入口拒/下载NOT_RUN|
|T20|可信只待验、自验/多角色、经理无理由拒/有理由成功NOT_RUN，获准输入通道BLOCKED|
|T21|PASSv3两成员round9、退回marker/counter4/旧completion与字节保留；FAIL旧数组恢复；真实第二completion/再验收NOT_RUN|
|T22|PASSv3/tmp启动恢复子项；FAIL旧数组/字节恢复；精确提交点故障及真实回滚/回执NOT_RUN，调度通道BLOCKED|
|T28|PASS当前installed/running全资源一致；FAIL路径/旧数组/字节恢复；实际操作回读/同盘重开NOT_RUN，重开通道BLOCKED|
|T31|终态源码守卫保留；真实只读/重复验收拒/关联新故障NOT_RUN；不扩前序取消预约|
|T35|真实证据变化后的确认/建议失效NOT_RUN；0模型调用，未声称交错通过|
|U03|三可信角色同task事实/按权动作/禁自验NOT_RUN，获准输入通道BLOCKED|
|U06|PASS旧completion/附件字节保全、v3轮次/marker恢复子项；FAIL旧数组/字节恢复；真实进度/完工/验收/退回区分NOT_RUN|
|U07|PASS预存中文/intent/key保留；FAIL两场初始化恢复/业务空白；重复/丢响应/冲突/离线命令NOT_RUN，精确调度/重开通道BLOCKED|
|U08|PASS6场登录/空态、截断盘保全子项；FAIL两场业务空白/完整件误报缺失；实际失败重试/无权/过期出口NOT_RUN|
|U11|PASS6场原生渲染/capture子项；FAIL2场初始化空白；真实输入/滚动/面板稳定性NOT_RUN|

## 判定与修复交接

- **最终结论：FAIL**，不是“基本通过”；唯一旧P1 D-M5-04仍OPEN，A/B/C为直接修复清单。其他建议不作为FAIL依据。
- 已闭合的精确范围：合法任务括号加载最小依赖、v3多成员轮次落盘/读回、tmp退回marker恢复、外来索引归属保全、所有旧文件字节保全、隔离回收、当前包一致。
- 原生失败均记FAIL，没有ABORT，也没有以agent沙箱限制降格BLOCKED。只对以下实际不能由当前获准白名单表达的能力记BLOCKED：可信登录/文本表单输入、真实保存后变更、同盘跨进程重开、精确提交点中断。未执行业务动作本身记NOT_RUN。
- 本轮schema虽有ui_actions，但其执行是osascript/System Events；当前用户仍明确禁用。schema内部写另一次授权不覆盖本轮指令。固定宿主已知type/key不支持（同SHA `M3/native-runs/review_r2_0937_REQUEST_review_r2_0937/restore_unknown_empty_arrays/logs/host.log:40–41`），不是所有UI输入在技术上永久不可行。现schema仍只支持预启动seed/每场新盘，不能把诊断种子当真实上传后变更/同盘重开。需驱动/宿主提供符合本轮授权的内置测试输入与副本注入/重开/中断调度；这些是技术缺口，NEEDS_ABRAM=no。
- 构建方Kimi-K3只修D04-A/B/C和必要依赖；先harness冷启动零parser/业务渲染，修完复跑本轮8场及上述真实命令链。不得清盘、放宽profile、删除canonical/摘要/权限门槛或造回执。
- 权威结果必须实际读取目标索引/任务/旧历史/字节/动作回执。真正正常链和退回链必须由可信会话发出实际命令，不能手工seed成功状态；经理理由/禁自验必须真实主体核验。
- 既有模块回归：仅当前合法/截断任务加载和冷启动做了针对性复验；M4 FAIL及其他前序挂账不改。没有宣布整条历史自动PASS。
- 更新位置：`docs/optimization/2026-10-09-desktop/GATES.json`仅M5的审查字段和status，指向本报告、记录本候选、审计和FAIL，归档此前r9审查来源；构建候选/报告字段及其他模块不动。原 `docs/build-loop/ACCEPTANCE.json` 保持不变，本轮适用结果写入M5.review_acceptance，保留历史来源，不用此局部重审覆盖既有台账。
- 不允许下一模块，未执行M6。
- 第2段读写仅限项目；不读明文凭据/provider密钥，不公开签名/publish/listing、push、issue/评论、发消息、部署公网或更换计费渠道。第1段项目外索引检索偏离见N，未作为本判定依据。

STATUS=FAIL
NEEDS_ABRAM=no
