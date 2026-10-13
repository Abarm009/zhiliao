# M7 独立 Review r7

**最终结论：FAIL。旧 B-M7-01 的解析/全空白故障已关闭：新候选7场零解析错误、原生工作台真实渲染。但登录点击实际报 widget读取错误，坏任务恢复进入运行时错误循环，合法提醒也被判损坏；这三项直接回归阻断本地可操作、可恢复发布候选。隔离/回收7/7通过，没有ABORT。**

- 审查者 / 日期：当前Codex主会话唯一独立审查者，无子代理；2026-10-12，Asia/Shanghai。
- candidate_id / base：**M7-r6-worktree / M7-r5-worktree**，版本 **0.1.0-e**。按用户交接、请求、实施r6、候选清单及GATES定位，没有按文件mtime选版。
- HEAD=`8d730569546cb57310944bb299695134df773b9d`；dirty候选另由实际包、作者原diff与审查相关diff/内容摘要定位，HEAD单独不足以复构。
- 冻结包：`runtime/optimization/2026-10-09/M7/r6/release/octosense-repair-0.1.0-e/`；digest=`80d7b5c077979723e3a5cbaa1400701ea683968f6112f5224139608fdba13ef9`；main **519600 B**、SHA-256=`dd3f4a5e8d87cc45bbd6ac38d1bfa63d31a194b1474826173aef1b8e4023c22f`。与工作区和M6-r7主源同字节，M7配置/版本/digest独立核对。
- 作者报告路径：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r6.md`；清单：`runtime/optimization/2026-10-09/M7/r6/CANDIDATE.json`。
- 前置：**M6=FAIL，M6-r7-worktree / M6_REVIEW_r8.md**，没有已接受M6 PASS。按用户挂账裁决继续M7，未代修前序，也未把M6叫已接受；本轮FAIL依据是本候选独立原生失败，不是前序挂账本身。
- 快照：第1段至本段受保护源码、候选、材料、作者资料、harness/schema、工具/宿主、GATES/原台账及seed全部一致。最终只允许本报告、M7 status/审查字段/审查历史与审计材料变化，最终写后核验见S/final-review-verification.json。
- 实际宿主：项目内M0/r3提取OctoSense.app。octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，octos-kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`；只定位二进制，不承诺由未知上游源码复构。
- 原生执行：驱动沙箱外harness，**04:48:05–04:50:09 +08:00**，独立请求7场CLEAN/quit_http/rc0；审查者没有启动launcher、sandbox-exec/pgrep、--help、osascript、辅助功能或其他UI自动化。
- 模型/路由：冻结配置enabled=false、manifest仅storage，独立请求needs_model=false、真实调用0。主会话没有Router/指定模型核验或切换、自身createdAt/改标题接口；未冒称完成这些动作。
- 已阅读：第1段AGENTS/CONTEXT/00/01/02/M7/04、实施/候选/上轮缺陷和直接关联源码差异；本段完整summary/result/profile/MANIFEST/日志/denials、实际运行包、隔离盘、7张请求PNG及不同的input_reachability.part.png。
- 已运行：第1段独立离线stamp/check/验签/official install_staged、Store重建/may_run；驱动独立7场；本段只读审计。`PYTHONDONTWRITEBYTECODE=1 python3 -B runtime/optimization/2026-10-09/M7/native/review_r1_2104/audit_phase2.py` rc0，**4283项证据一致性检查，不是4283项业务测试**。
- 未运行：可信三角色成功/退回完整链、真实附件、权威业务动作回执/并发/响应丢失、同盘跨进程业务恢复、真实模型三链、实际官方scan、150%/完整键盘/2–3分钟演示。具体白名单不能表达的步骤单列BLOCKED；领域操作未发生记NOT_RUN。没有以agent沙箱rc71/rc3判BLOCKED。
- 访问/授权：两段显式文件访问仅项目内，未读原账号/安装/host-data、明文凭据、模型密钥或项目外记忆/技能；无联网、公开签名/publish/listing、push、Issue/评论、消息、部署、计费变更。离线签名输入只针对当前digest；本审查者本轮没有生成私钥。
- 置信度：同版本/隔离/解析修复、登录点击错误、任务错误循环与合法提醒误判 **高**；宿主parse_json/typeof具体根因、完整可信业务与真实模型效果 **未知**。

## 证据索引

- **H**=`runtime/optimization/2026-10-09/M7/native-runs/review_r1_2104_REQUEST_review_r1_2104/`：本审查者独立请求的驱动证据，只读未改。
- **S**=`runtime/optimization/2026-10-09/M7/native/review_r1_2104/`：phase1-audit、scoped-dirty.diff、old-frozen-to-new-frozen.diff、独立Store/seed、native-evidence-audit、门禁原快照和写后核验。
- **R**=`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r1_2104.json`；SHA-256=`01fd1a345cebe84720dc343c8595cb84103a0da74fb493d4e32470f27b042f37`。
- **N**=`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r1_2104.md`：原阶段笔记保留，不回改为最终判定。
- 作者 `build_r1_2104_REQUEST_build_r6/`只作第1段参考，不代本轮独立复现。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/前置/差异|5方定位及冻结摘要、M6门禁、旧/新diff|明确审哪份和新增影响|M7-r6明确；M6 FAIL；换基线303差异块，非仅1行修复|定位PASS；前置未PASS|S/phase1-audit/diff；M6 r8|
|最终字节/运行包|对照seed、installed、mirror、实际.running全部文件|同digest实际运行|7场全部运输字节一致，6个非manifest资源与冻结源相同；manifest仅本地签名运输形式|PASS|S/native-evidence-audit；H实际包|
|证据完整性|全MANIFEST及summary/request/result重算|无漏项/错hash/重复|954项全匹配、请求一致，4283个一致性检查无失败|PASS证据完整性|H/MANIFEST；S/audit|
|隔离/进程回收|重建profile、核禁读探针/env/writes/PGID/denials|新run限制、禁读、无残留|7/7 probes true、pre/post NONE、PGID_after空、CLEAN、退出rc0|PASS|H各result/profile/denials|
|干净原生首屏|cold_clean从新独立Store launch/capture|正确解析、工作台渲染|519600 B实际eval，0parser/0runtime，未登录工作台可见|PASS启动/渲染子项；B01关闭|cold/log:43；PNG|
|登录入口|内置taps触发登录handler、核UI/日志/状态|空输入有明确提示，不抛异常|widget 'text' not found；仍未登录；输入行裁切|**FAIL R-M7-01**|input/log:62、PNG/part；源9624|
|真实文字/键盘|内置key:Tab/type新非凭据字符串|宿主支持并送入控件|两动作明确unknown；不形成文本输入|具体步骤BLOCKED|input/log:39–40|
|合法提醒恢复|真实loader路径合法18 B空数组/168 B单条|合法schema正常加载|两场均误判顶层损坏，pending/dirty true，内存[]|**FAIL R-M7-03，关联D-M6-02**|两场state/原文/.recover|
|坏提醒保护|真实路径follow_ups:false|准确拒绝、原文保护、可恢复|原文与备份逐字节保留；pending护写状态；但也在顶层拒，数组/member校验未到|保护子项PASS；准确分类/恢复操作NOT_RUN|bad_followup盘/PNG/audit|
|坏任务失败恢复|新非法顶层/截断数组冷启动|明确错误、保护原文、可继续恢复|各30条variable _ not found，原文未变但state仍准备就绪，UI停初始化/无恢复信息|**FAIL R-M7-02**|tasks场log:56–85、盘/PNG|
|全链/权威回读/重启|同候选三角色、成功/退回/失败、任务/回执/版本|可复跑桌面闭环|可信登录未完成，领域命令未执行；没有业务成功回执|NOT_RUN；入口实际FAIL；指定跨进程/故障步骤BLOCKED|R01/R02；64表|
|模型/身份|核实际config/caps/代理/SESSION入口|可信身份、真实模型有证据|无可信会话；enabled=false/storage；代理/统计缺省，0请求|身份入口FAIL；模型NOT_RUN|实际包/input/result|
|材料/媒体同版本|11指纹+selfhash、listing/README/当前PNG|无假完成、媒体属于当前字节|指纹/当前PNG同版本；旧完成截图不再引用；README旧入口、placeholder及演示不足建议挂账|字节PASS子项；A01/02 OPEN；媒体NOT_RUN|S/audit；材料/README|
|本地准入/实际独立审阅|独立check/catalog验签/install/may_run、审运行结果|准入且实际功能可用|准入通过；独立功能审查FAIL；官方scan未运行|准入PASS子项；本地准备FAIL；P03 NOT_RUN|S/phase1-audit；本报告|
|外部状态|只读本候选交接回执字段|本地/发布/赛事/收录分开|没有本候选实际外部回执；全局P06/07/08 UNASSESSED保留|状态分离PASS；外部NOT_RUN|GATES.external_delivery；判定|

## 原生证据逐项核对

1. **MANIFEST 954/954**全部摘要匹配，无缺失/错hash/漏列/重复；summary.request=R，harness/template摘要=current；各result与summary场序、verdict、退出、时长一致。第1段保护和seed无漂移。
2. 7份profile按实际新目录、记录的原HOME字符串与控制端口重建，字节/SHA完全相同。profile_probes.ok=true、apply rc0、场外写探针拒且created=false；secrets、明文credentials、~/.codex、~/.cc-switch、~/.ssh五项禁读探针成立。审查者仅看记录，没有实际访问项目外HOME。
3. 7场pre/post均rc1、class=NONE、out/err空、PGID_after=[]；quit_http=ok、host_returncode=0、wall=16.22–16.34 s，无exception/ABORT。HOME/app-data/log/cache/tmp/config等全部在各场新run下；驱动Library扫描空，原HOME .octosense mtime前后相同。
4. profile含/dev/null写例外与unix-socket放行，按已授权harness口径记录，不夸大为所有IPC均禁用。valid_empty_followups运行中PGID记录含(pmset)，最终回收干净；审查者没调用该程序，不臆造其用途。
5. 所有denials完整重算与result一致：443外联、系统Metal缓存、/dev/dtracehelper尝试被拒。拒绝不是成功越界；宿主news为7源失败/0新数据，不声称宿主没有尝试网络。needs_model=false、无代理/统计/MM_KEY/endpoint注入，模型0请求，无欠费证据。
6. written_count与完整有序唯一列表匹配：4场117、3提醒场118，全部实际存在且在对应run目录，未达到400截断上限。这是mtime写入清单，包含宿主初始化/运行副本/截图/偏好，不是任务执行数。
7. seed全部与独立安装输入SHA一致；installed、mirror、唯一`.running`的所有7文件逐字节相同。expect_digest/seed可见；日志digest_seen=false如实记录，靠实际运行包与519600 B eval识别，不因日志未打印digest错判旧包。
8. 全部host.log bytes/markers/tail重算匹配；7场**0parser错误**，有809 B系统窗口eval，不能混成业务源。cold/三提醒0runtime；input1条widget错误；两tasks各30条`_`错误。panic=false/rc0不能抵消应用运行失败。
9. 7张请求PNG逐张查看；input不同part图也查看，其余part与各请求图同字节。全部 **2800×1716**，3种--size未形成3种可验证客户区。业务工作台已渲染，登录行下方裁切，所见提醒错误/恢复入口未展示；bad_tasks留“初始化”占位/“待选任务”，truncated又显示任务不可见。未登录不展示任务私有正文，不代表已登录权限验证。
10. input日志:39–40明确拒key/type，:41–43记录3次tap调度，:62实际进入登录handler发生widget错误；part登录chip变白与源位置支持点击已达，不把其他tap调度声称业务成功。state.nav/detail_tab仍all/overview，auth会话未形成。
11. 正例提醒18/168 B与反例50 B原文均保留、`.recover`完全相同，但**两正例也被误判**。状态为dirty/pending true/列表[]；反例在相同顶层分支拒绝，不能据此称成员validator或人工恢复通过。不是构建请求误放根follow_ups文件的旧场景。
12. 两tasks新原文34/24 B始终保留、无.recover，state“准备就绪”；没有合法业务写/动作回执。文件没变是有限保护观察，不能把错误循环/无恢复入口认作失败恢复成功，也不声称已丢数据。

## 缺陷与上轮闭合

只处理上轮编号及换基线直接影响，不扩审无关前序业务。新R编号用于可复现的直接回归，保留旧根因已修的事实。

|编号|本轮结论|
|---|---|
|B-M7-01|**CLOSED：旧三元解析/业务全空白根因已修**；7场0parser、真实工作台；这不等于核心动作或M7整体PASS|
|D-M7-01/02/03|已关准入/指纹/原编号保留子项保持；同版本独立回归通过，不转移旧业务PASS|
|A-M7-01|OPEN/P2建议：README仍旧入口/旧版本/旧完成结论，继续挂账|
|A-M7-02|PARTIAL/P2建议：当前版本/旧完成图移除子项改善，身份/入口/统计/媒体事实仍欠|
|A-M7-03|CLOSED：当前11指纹+selfhash、作者本轮keys为空；审查者无新私钥|
|R-M7-01|**OPEN/P1必修，独立原生FAIL：登录handler读取widget错误**|
|R-M7-02|**OPEN/P1必修，独立原生FAIL：坏任务恢复错误循环、假就绪**|
|R-M7-03|**OPEN/P1必修，独立原生FAIL：合法提醒误判损坏**；原来源D-M6-02，不另扩修M6 AI/收藏|

### R-M7-01 — P1 / 必修：登录点击即异常，无法进入核心流程

- **文件与行**：冻结包及同字节`app/bundle/main.splash:9623–9635`，读取`:9624–9625`，清空`:9628–9629/:9633–9634`；登录行布局`:9613–9618`。
- **触发**：R/input_reachability，全新独立Store、无真实凭据；内置taps:794,198@6点击登录区域。无需成功打字或真实账号即可触发handler。
- **实际/预期**：H/input/log:62 VM9627:50报`widget 'text' not found in tree`，仍未登录、无“请输入账号ID与口令”反馈；预期空输入准确提示，真实输入能交给凭据核验，失败不抛widget异常、口令不落盘。登录行裁切使核心入口难操作，非纯美化。
- **根因**：源用`ui.login_account_input.text`/password.text当普通字段；实测UI句柄把`text`当子widget查找失败。把写`.text=""`当清空也须实测，不能只修读而留下同种写路径。项目本地参考TextInput实现提供script-call `text`与`set_text`（`runtime/native-build/makepad/widgets/src/text_input.rs:2390/2394`），**参考源码不是本固定发行宿主已验方法**。
- **影响**：登录是所有可信三角色命令/查询入口，发布候选只渲染未登录壳；硬1/2/4、G0-B、U01/U11、P01/P05阻断。无真实账号失败或凭据泄露断言。
- **证据**：H/input/log:39–43、62；PNG及不同part；实际.running/S/audit；源9624与VM+3对照。
- **具体改法（Kimi-K3）**：只修入口依赖。先在固定宿主通过驱动harness验证TextInput读/写方法，候选方向为`text()`/`set_text("")`；替换登录/清空handler的错误字段访问，保留私有SESSION与凭据不持久化边界。给登录行足够实际空间，使输入/提交/错误可见，不新增客户端/认证绕过。
- **验证方式**：新冻结digest原生空输入点击得到明确提示、无widget错误；隔离自造5账号慢哈希，可信输入通道下正确/错误口令、清空、退出、重登，凭据不出现在state/log/包，任务查询/写前核权。key/type不支持需驱动/固定宿主提供已授权内置输入通道，不用伪造seed.actor或项目外自动化。

### R-M7-02 — P1 / 必修：坏任务启动后不断异常，却仍称准备就绪

- **文件与行**：同字节main`:997–999`任务加载；`:10720–10726`tick刷新及`catch _ {}`，特别`:10726`；源状态默认与当前刷新路径。
- **触发**：R/bad_tasks_top用合法JSON非法顶层`{"review_tasks_invalid_top":true}`34 B；R/truncated_tasks用新截断数组24 B。各自新Store同最终digest冷启动，没有业务写/模型/真实数据。
- **实际/预期**：两场log:56–85各**30条**VM10729:16`variable _ not found in scope`；截图列表留初始化占位/待选任务；state.status仍“准备就绪”。原文保留、无备份，不声称已丢失。预期坏schema/截断数据明确标恢复未决、保护原文、拒业务写且给合法恢复出口；周期刷新不陷错误循环/假就绪。
- **根因**：load把任意非nil parse结果赋TASKS，没有此处数组/成员门禁；异常流最终到tick的`catch _`又报变量未定义。准确是哪一个refresh调用先触发原异常还**未知**，不能用吞错或改“准备就绪”文案代替修复；宽容parse和异常语法必须按固定宿主实测。
- **影响**：用户现有任务损坏/升级恢复时无法可靠继续，M7失败恢复/重开可复现目标失败；硬1/2/4、G0-C、T28、U07/U08/U11、P01/P05。不是无关故障注入扩审，正是上轮B01要求的坏数据受影响回归。
- **证据**：H两tasks的log:56–85、tasks.json、state.json和PNG；S/audit原文与源/S.diff。未把原文未变认作完整恢复PASS。
- **具体改法**：只修这条加载/异常出口。用固定宿主实际支持的parse/type/schema验证任务数组与必需成员；不把非nil当合法，不删除旧数据。原文/备份可核，持久恢复未决和拒写，显示真实错误与恢复/重试。把tick异常处理改成实测可用形式并保留诊断/状态，不继续循环报`_`。继续保留原正常命令边界与幂等，不重写其他模块。
- **验证方式**：合法空/合法任务正例正常；本两负例准确拒、原文不丢，0重复runtime错误，有可操作恢复；恢复失败保持未决、成功读回权威任务，补同Store跨进程重启。预损坏不是运行中写故障；未跑的精确故障继续NOT_RUN/具体BLOCKED。

### R-M7-03 — P1 / 必修：最终候选合法提醒不能恢复（来源D-M6-02）

- **文件与行**：main`:1940–1944`实际路径、`:2000–2053`loader，特别`:2024–2028`parse/顶层门禁、`:2033–2048`数组与成员门禁；`:1967–1983`成员validator；`:1990–1999`备份/保护态。
- **触发**：R/valid_empty_followups完整18 B合法对象/空数组；valid_one_followup完整168 B合法成员、status=ACTIVE、数值远期due。文件放真实嵌套读取路径，不是作者未触达loader的根follow_ups文件。不存在task的单条夹具仅检验schema，**空列表正例已独立排除任务存在性因素**。
- **实际/预期**：两正例都状态“JSON解析失败或顶层非对象”、dirty/pending=true、内存[]，被当损坏逐字节备份；预期合法schema正常恢复，真实坏schema拒绝/保护且可恢复。反例false也在顶层拒，成员validator正确性未实证。
- **根因**：当前固定宿主的parse_json/typeof实际结果未满足源码`typeof(raw)=="object"`假设。具体是parse结果、typeof表示或调用语义未知；不能凭源码编造真实返回类型。该前序D-M6-02挂账已在**本M7最终digest**独立复现，现直接阻断发布候选恢复，所以只要求最小loader依赖修复，不拉入M6 AI/收藏未闭合项。
- **影响**：合法数据启动就锁在损坏恢复态，连续使用/重开恢复失效；硬1/2、G0-F、T23、U07/U08、P01/P05不能通过。原文与backup正确保护子项已通过，不能因此放行正例失败。
- **证据**：H两个valid与bad_followup的state/原文/.recover、PNG；S/audit分别18/168/50 B及逐字节核验；同字节M6 r8/D-M6-02仅作来源记录。
- **具体改法**：固定宿主经harness做最小parse/typeof/读写结果探针，采用实证schema判断；load与受控恢复共用验证，合法空/单条通过，非法顶层/成员整份拒。保留已有pending写保护、原文备份读回及失败结果传播，不放宽安全边界。恢复状态/入口须在真实界面可见。
- **验证方式**：先复跑本两正例及false反例；正例不进入损坏态、合法内容恢复，反例精准分类且原文/备份不变。补null/boolean due/残缺成员、恢复拒写/错读，再实际点击恢复、同Store重启；提醒去重/旧作业取消/权限跳回未跑仍NOT_RUN，不能以后台常驻名义放行前台seed。

### 建议及历史来源

- **A-M7-01 / P2 / OPEN**：`app/README.md:5、88–100、104–121、134`仍旧0.1.0-c入口/直接subprocess/项目外tmp命令/旧bundle摘要及B01完成话术。触发为照文档复现选错候选；根因入口未随版本同步；建议指当前候选+harness、修相对链接，旧步骤标历史不可执行。验证链接/步骤/版本读回。本轮未执行旧命令，不单因建议FAIL。
- **A-M7-02 / P2 / PARTIAL**：旧材料版本与B完成图移除子项改善；当前INTEGRITY事实匹配。`listing.json:4/:23`仍称card-host与待执行作者请求；`PRIVACY.md:5`演示默认身份说法和实际退役fixture不合；清单正则问号3命中与报告/GATES构建字段0不同（源1932/2721是字符串，不是三元），placeholder不算关键图/演示。根因是统计和事实scope未同步；建议按launcher/真实身份入口、作者已运行但独立功能FAIL的范围写事实，保留disabled模型/媒体未完成。替换媒体变化digest后重新冻结。网络配置禁用说明不等于证明宿主无外联尝试；注释或未启用适配器也不证明成功外联。
- **A-M7-03 / CLOSED**：当前11项指纹及外存selfhash匹配，作者r6 keys目录实际空，与当前finally删除记录相符；审查者未生成私钥。没有拿旧r2证据替代本轮，也没有公开签名。
- M6 AI/偏好对账、其他模块挂账不在本轮顺手修；原台账旧PASS保留其版本和运行形态。缺媒体/对比/美化等建议不单独判FAIL。

## 相关既有用例逐项复核

下面64项保持原编号/含义；完整项结论按当前运行范围。局部子项PASS不能冒充整个用例PASS；具体能力缺口只记在相应步骤，不泛称原生环境BLOCKED。

|编号|既有用例含义|本轮结论|证据/范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|PASS|本digest准入/实际.running及7场原生启动已独立证明，0parser、真实工作台；不含可信业务操作通过。|
|G0-B|真实可信身份、授权与独立会话|FAIL|R01登录点击widget读取异常；实际正确/错误凭据、三会话未执行；文字输入子项BLOCKED（key/type unknown）。|
|G0-C|唯一事实源、原子一致性、并发与恢复|FAIL|R02坏任务恢复错误循环/假就绪；原文保持子项PASS；正常原子命令/并发/崩溃对账NOT_RUN。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|真实附件上传/回读/归属/失败恢复均未操作；placeholder不是附件，未以受控坏文件代真实成功。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|FAIL|R03合法提醒恢复在最终digest失败；坏文件原文/备份保护PASS；实际通知/去重/跳回/后台NOT_RUN。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|NOT_RUN|断线期间真实动作/重连权威回读未跑；当前schema无运行中断线/重连动作，指定步骤BLOCKED，不以进程回收代回读。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|未登录PNG无任务私有正文仅有限观察；可信列表/搜索/事件/附件访问查询未执行，输入步骤BLOCKED。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|FAIL|前台合法提醒恢复FAIL R03；实际appointment作业触发/单份通知/旧作业取消NOT_RUN，指定运行中改变/同Store重启步骤BLOCKED。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|冻结无连接器实际执行证据；NOT_CONFIGURED口径不代真实本地完工/验收、external_id及SUCCEEDED验证。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|同digest实际native加载子项PASS；R02恢复直接回归FAIL，但同task_id正常操作/权威回读/跨进程重开这个完整用例未执行。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|真实grant关闭/退出/到期/共享卡撤权未执行；schema无运行中撤权动作，指定步骤BLOCKED；Seatbelt不能代业务授权。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|可信收藏/重登/他人隔离/version不变未执行；前序D-M6-04挂账保留，不本轮扩审或代签。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|旧配对/Web审批及原生可信会话替代链均未执行；不默认N/A/PASS，不伪造seed会话。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|真实模型生成期间改派/改约交错未操作；schema无精确运行中交错动作，指定步骤BLOCKED；0模型请求。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|当前运行包enabled=false、storage-only，无代理/统计/请求；真实模型或系统助手实际调用及相关失败/白名单业务未跑，0调用。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|模型假成功/回执丢失/后续版本等实际链未操作；schema无精确提交后读回超时注入，指定步骤BLOCKED。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|源码/config/宿主/digest/request/seed/运行包/成功启动及实际失败可定位；真实模型同组成功失败复跑NOT_RUN，真值/Agent隔离效果未实证。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|FAIL|工作台渲染子项PASS；R01可信登录入口实际失败，三角色待办/下一人未能独立操作，不以三标签代三会话。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|原话编辑/补歧义/真实模型失败人工继续未操作；key/type输入步骤BLOCKED，未以未登录空态代草稿。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|可信业务命令未独立执行，无权威任务/动作/版本结果及失败重试；不挪用旧包/后端PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|持久化加载直接回归R02/R03 FAIL；原用例重复点击/响应丢失/版本冲突/离线实际命令未执行，指定故障步骤BLOCKED。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|未登录空态渲染PASS子项；R02坏任务无准确恢复出口、R03合法恢复失败；长文本/真实附件/过期建议完整流程NOT_RUN。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|BLOCKED|3种size均同2800×1716画面，无可验证3种业务客户区；无150%文字调整白名单动作；登录行裁切关联R01，不单因美化FAIL。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|input/log:39–40实测unknown key:Tab/type；当前白名单无法完成主要键盘流程；焦点/颜色/对比完整实测NOT_RUN。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|FAIL|真实渲染PASS子项；登录widget异常和坏数据tick错误循环R01/R02影响输入/稳定反馈；滚动/完整面板业务操作NOT_RUN。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|7张当前digest实际PNG只有未登录/恢复失败工作台；包仍1×1placeholder，无可信全链2–3分钟演示/独立复述；媒体建议挂账。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|同候选核心入口/失败恢复R01/R02/R03实际FAIL；完整成功/退回/同task重启恢复NOT_RUN。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|NOT_RUN|源码/dirty/包/宿主/工具及干净原生启动子项PASS；README旧启动入口A01建议挂账，完整干净构建/运行说明条件未独立复跑。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|独立check/catalog验签/install_staged/may_run子项PASS；本候选实际官方scan独立审阅NOT_RUN，不挪用旧scan自答。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|7张当前digest实际PNG只有未登录/恢复失败工作台；包仍1×1placeholder，无可信全链2–3分钟演示/独立复述；媒体建议挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|FAIL|11指纹+selfhash及运行源字节子项PASS；三个核心P1未关，完整发布准备交付条件未成立；A01/02仅建议。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|当前交接无本候选实际外部回执；本轮不执行发布/递交/收录，未联网核外部状态；保持全局UNASSESSED，历史B回执不转移。|
|P07|维护者商店收录结果|NOT_RUN|当前交接无本候选实际外部回执；本轮不执行发布/递交/收录，未联网核外部状态；保持全局UNASSESSED，历史B回执不转移。|
|P08|赛事正式提交入口回执|NOT_RUN|当前交接无本候选实际外部回执；本轮不执行发布/递交/收录，未联网核外部状态；保持全局UNASSESSED，历史B回执不转移。|

## 五项硬验收

|硬验收|本轮结论|依据|
|---|---|---|
|1最终同候选必需业务/UI/运行实证|FAIL|启动/解析/隔离通过；登录与数据恢复核心R01/R02/R03真实失败；未跑业务不冒充PASS|
|2正常/退回/失败恢复/重启/真实模型同版本|FAIL|同候选失败恢复已复现失败；成功/退回/业务重启/真实模型NOT_RUN，指定白名单步骤BLOCKED|
|3根包/运行数据/源码媒体描述一致|NOT_RUN|冻结源/实际包/11指纹子项PASS，无运行数据/秘密入包；材料媒体完整项未成立，A01/02建议挂账|
|4本地准入/独立审阅/干净启动|FAIL|check/验签/install与干净首屏PASS子项；本独立功能审查FAIL；官方scan NOT_RUN|
|5本地与外部状态分开|PASS|本地准备FAIL；P06/P07/P08当前候选无回执，NOT_RUN/UNASSESSED，不挪用历史B回执|

## 判定

- **最终结论：FAIL**，精确范围为M7-r6-worktree/0.1.0-e在固定发行宿主的本地桌面发布准备。置信度高；不是外部评审/赛事/收录结论。
- **必修清单：R-M7-01、R-M7-02、R-M7-03**。优先修可信登录控件读写和可见入口，再修坏任务与合法提醒的加载/恢复依赖；不要求重写已关闭的parser修复或顺手修M6 AI/收藏/无关视觉。
- 复验要求：新候选明确旧/新差异、重新冻结digest/catalog/seed；仅驱动harness运行，先空/合法/坏数据正反对照，再可信正常/退回与权威回读、失败恢复/重启。完成核心路径需要合规内置文本/故障/重启通道；不能用作者静态总数、伪会话、修改冻结模型开关或裸代理调用代签。
- **BLOCKED精确范围**：当前宿主实际拒key/type的可信文字输入/键盘；当前schema无法表达同Store跨进程重启、运行中精确故障/撤权/断线/迟到交错和150%调整。无ABORT，不用agent沙箱rc71/rc3解释功能失败。没有发生的领域操作和模型调用NOT_RUN。
- **先前模块回归**：本轮已对换入303差异块的新主源完成同digest解析/首屏、登录入口及合法/损坏加载直接回归；M6 D02失败来源明确。本报告不签M6其他功能或其他模块通过，不改其门禁。
- **状态分开**：本地准备FAIL；外部发布/Hub递交P06 NOT_RUN；商店收录P07 NOT_RUN；赛事正式回执P08 NOT_RUN。当前交接没有本候选实际外部回执，未联网核外部状态，保留全局UNASSESSED；历史0.1.0-b回执不表示0.1.0-e已完成。
- **门禁与台账**：仅更新`GATES.json`的M7 status和review_*/reviewed_at/审查history，review_report指本报告、review_candidate_id指M7-r6；构建字段、其他模块和external_delivery保持。旧审查字段保存在review_history与S/gates-before-final-review.json。原`docs/build-loop/ACCEPTANCE.json`不改；当前64结果单列GATES.M7.review_acceptance，保留历史来源/运行形态。
- **是否允许下一模块：否。** 留在M7按上述三项最小修复并补合规通道；不执行发布或下一模块。
- **NEEDS_ABRAM=no**：本地catalog安装路径成立；身份、MiniMax、隔离签名已授权；无402/余额/欠费或公开发布需求。剩余是已授权技术修复与驱动能力。

STATUS=FAIL
NEEDS_ABRAM=no
