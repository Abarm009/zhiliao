# M2 独立 Review r9

**最终结论：FAIL。** 当前共享源码在固定原生宿主中已能渲染，8/8 场解析/运行错误为0，原空白根视图子项关闭。可靠执行核心仍未成立：独立盘面证明合法空历史被迁成嵌套数组、坏行被迁成字符串且未冻结、原合法备份被覆盖、未保存输入及持久意图丢失；D-M2-02/03/04/05 的核心源码反例仍在。CLEAN仅表示隔离与回收。本轮不修代码，不进入下一模块。

## 审查范围与候选

- 审查者/日期：本主会话唯一审查者，2026-10-12，Asia/Shanghai，无子代理。工具无法读回/切换指定 Router 主会话模型或取得当前thread createdAt/设置标题，未声称已用指定 gpt-6.1-sol 或已完成命名。
- 本次入口：Abram 0748“跳过构建，审当前代码”。`driver/state.json` 的 M2 rounds_done=0、skip_used=true，0748构建日志为空；用户没有交接新 M2 实施候选。最新M2作者报告仍为 `M2_IMPLEMENTATION_r7.md`，上轮 `M2_REVIEW_r8.md`；本轮未按mtime选版。
- **实际受审运输候选：M7-r7-worktree / 0.1.0-f**。由 `M7/r7/CANDIDATE.json`、冻结运输包及与工作树逐字节相等的main定位，审查范围仅M2及相关回归。原M2-r7-worktree是比较基线，不把当前字节冒名为旧M2候选，不新造构建方candidate_id。
- HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty；当前main **532303 B / SHA-256 `7b82c1313dcf14379942f01453784f44eb70321257d61a9214fc09d39173e23c`**；bundle digest **`9e1f7aec09785858c744272048afd786c02dee05c1a29aa3838cca8db05ed5cf`**。M2旧r7 main 440604 B / SHA `8d82606aaf22e7526a39108ed8c6021359db53ecb48f8ac58fb147a4c7c5a143`；累计差异已保存。
- 工作树manifest/listing/model_config与冻结运输包不同；本轮运行的是既有冻结运输包，storage-only、模型关闭。main相同不表示所有配置相同，**不验证M3模型或工作树整包**；差异见 E/source-audit.json。GATES作者candidate/base/implementation保持原历史，review_candidate/source/digest标记实际版本。
- 前置：**M1仍FAIL / M1-r2-worktree / M1_REVIEW_r2.md**，没有已接受M1 PASS。按Abram前序挂账与本轮先审裁决继续M2，未改写前置。原生根、未登录空态及恢复状态做针对性回归，不替M1全量放行。
- 固定宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；kernel SHA `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`；harness SHA `12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`。
- 已读：AGENTS、CONTEXT_M2、00/01/02/M2/04、M2 r7实施/候选/r8审查、五账号实施记录、M1 r2、当前既有验收原定义、原缺陷涉及源码及累计差异、harness/schema和本轮完整运行证据。只复核D01～07及受影响回归。
- 独立请求 `M2/native/REQUEST_review_r1_0748.json`，SHA `364320ac053b81d65c095e1077e354d446df9366b6897b28e752a9910ebdeef6`。8场新合成数据和独立离线安装Store，未预装SESSION，未取真实凭据。驱动沙箱外执行 **07:56:38–07:58:59 +08:00**；审查方未启动launcher/harness、未运行sandbox-exec/pgrep预检或外部自动化。
- 已运行：独立离线stamp/check/catalog verify/install_staged；驱动本轮8场；本审查完整证据、摘要/磁盘/PNG/源码复核。未运行：成功/错误口令登录、两可信主体矩阵、真实业务提交/重试、逐写点故障、原动作认证后查询、真正竞争、连续同Store重启、旧外部入口负例。原因与状态下文逐项列明。
- 置信度：候选/隔离/盘面动态失败及确定源码路径 **高**；未保存输入恢复的内部失败具体执行点 **未知**；认证后提交/竞争/恢复动态结果 **未知/未执行**。未把源码反例写成本轮已发生的业务事故。

下文 **H/** = `runtime/optimization/2026-10-09/M2/native-runs/review_r1_0748_REQUEST_review_r1_0748/`；**E/** = `runtime/optimization/2026-10-09/M2/native/review_r1_0748/`；**A** = E/native-evidence-audit.json；**B** = E/business-observations.json。阶段笔记 `M2/native/REVIEW_NOTES_r1_0748.md` 保留。

## 必需检查

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本/证据一致|重算保护输入、请求/种子、全部MANIFEST、安装/.running/mirror字节|同固定候选且证据完整|22保护+130种子/mirror无变化；1143清单项全部匹配、无缺漏；各场实际运行资源一致|PASS，证据范围|A；E/protected-snapshot、seed-manifest；H/MANIFEST|
|隔离/回收|逐profile/env/probes/进程组/denials/写清单|写限场景目录，禁读生效，无残留|8场probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN；无ABORT|PASS，harness范围|A；H各result/profile/denials|
|原生根/空输入/退出|核全部16张PNG内容、全文日志和tap请求|业务根渲染，明确登录失败/退出出口|业务532303 B view=true；0解析/运行错误；未登录、空输入与退出提示可见|PASS子项，D01旧空白关闭|H/cold、synthetic/frames/log；A|
|可信登录/主体权限|合成5账号，只用内置tap/type/key输入|真实登录后逐查写核权|宿主明确拒4个输入动作；无可信会话/业务操作|BLOCKED，具体白名单通道；未做业务矩阵|synthetic/log:39–42；PNG；A|
|硬1：幂等/独立意图/新版本原查询|按钮→确认→创建/重放→磁盘调用，核冷开意图|同key原结果、异参拒、新意图可新建|unknown创建不拦、内容代意图仍在；保存意图冷开丢失；新确认要求当前OPEN|FAIL，源码+冷开动态；业务重试NOT_RUN|main:5938–6118、6253–6345、6404–6460；B/compact|
|硬2：授权/版本/竞争|核会话门控、锁交错与创建路径|越权拒；同权威盘竞争一赢家|门控/完整token子项改善；仍普通read/write/readback，创建绕过取锁；未真正竞争|FAIL，D05源码；竞争动态BLOCKED|main:3516–3610、3890–3920、6060–6097；schema/harness|
|硬3：逐写点恢复|核pending/task/final/event顺序和保存返回；坏历史冷开|业务无部分提交/假成功|保存脏历史可return，内存matched即committed、event后写；坏行实际被接受|FAIL，D03源码/D07动态；精确提交注入BLOCKED|main:886–900、3854–3996、4093–4137、6510–6513；B/mixed|
|硬4：未知结果查询|无关v1/原finalv1-currentv9夹具，核恢复代码|查原action完整事实，不重复写|未登录盘回执保持；认证后查询未执行；version-only恢复仍在，新确认当前OPEN依赖|FAIL，D04源码；认证后动态NOT_RUN|main:4013–4088、6404–6460；B/two_unknown|
|硬5：冷开输入/意图及历史恢复|新seed输入/意图、3行/混坏/缺主/坏event迁移，查盘/UI|输入及原key保留，旧历史严格可恢复|8场pending_input空；issued意图丢；[]→[[]]；坏行→字符串；合法bak被覆盖；缺主仍缺|FAIL，独立原生|B；H各业务jail/state/history/PNG|
|D06/旧入口回归|比sourceOk原修复和调用路径|准入不回退；旧入口不可绕过|sourceOk同码；原白名单根因保留；旧Web/MCP/runner真实负例未执行|原根因关闭保留；T24 NOT_RUN|E/source-audit；main:805|

### 原生证据逐项核对

1. A脚本复核 **5112项证据一致性检查，无摘要/字段失败**；这不是5112个业务测试PASS。summary/request逐字结构相同，场景次序/目的与各result一致；宿主/harness/profile模板摘要匹配。
2. 全部实际profile由仓库模板、场景路径、控制口重建后逐字一致；内核探针禁写/五禁读均成立。HOME/app-data/cache/tmp/env路径均限场景。8场 **16.18–16.42秒**，rc0、quit_http；pre/post NONE，最终无进程组成员，library_scan无新增、驱动记录真实home目录mtime前后一致。
3. 每场119或121个files_written项存在、唯一、有序且限场景；是驱动mtime文件清单，不是业务提交数。种子与seeded_files完整一致；实际 `.bundles`、唯一 `.running` 与mirror全资源逐字对应签名运输包。工作树其他配置差异单列。
4. 全部16张PNG摘要重算，**8种不同字节内容全部目视**，覆盖所有图像内容；全部2560×1260全屏图，root/login可见。`980x760`仅启动参数，不能由全屏尺寸认定紧凑布局已通过。part和正式capture可能不同，本报告不猜拍摄时间排序。
5. 逐个全文host.log复核marker/bytes/tail：8场业务eval `532303 bytes ... view=true`，与宿主809 B另一视图区分；无`[E] splash`、NotFound、作用域/属性或budget错误，tick_exception_count=0。synthetic场4项`unknown --test-action`明确证实入口不支持，不以harness接受请求等同宿主执行输入。
6. 全文denials已核；octos摘要与全文重算相同，443外联、Metal缓存、/dev/dtracehelper写被内核拒绝。拒绝尝试不是成功外联或项目外写；日志聚合重复报告不被当作精确系统调用次数。cold运行进程组曾含宿主派生osascript，审查方未调用osascript/辅助功能/自动化，最终无残留；不写“宿主无此子进程”。
7. model_proxy/model_proxy_stats在所有场均不存在，env没有代理/MM_KEY，needs_model=false、billing_error=null。真实模型请求0。**G0-E：延期缺口（Abram已裁决，M3到期）**，不作为M2 FAIL/BLOCKED或NEEDS_ABRAM理由。

### 权威盘面逐场结果

正确业务jail是 `H/<场景>/home/.octosense/apps/octosense-repair/`。所有tasks.json、tasks.lock和合成账号全字节保持seed，无业务接单/创建提交；以下是**加载/迁移实测**，不是已发生命令事务故障。

|场景|独立盘面事实|结论|
|---|---|---|
|cold_forged_actor_empty_login|actor=null；UI未登录/空输入/退出；tasks不变；actions/events均[]→[[]]；pending_input丢失|未冒用及登录提示PASS子项；D01/D07 FAIL|
|synthetic_login_input_capability|4项tap/type/key拒绝，输入框仍空；未建立可信主体；空历史同样被嵌套|登录通道BLOCKED；D07 FAIL|
|two_unknown_histories_no_session|4条回执各字段/status原样，当前v1/v9任务原样；没有新成功业务事件；events[]→[[]]|未登录对账保护PASS子项；认证后查询NOT_RUN；D07 FAIL|
|three_rows_newer_than_backup|3条全部字段及嵌套marker逐项匹配；bak精确改为三行原主NDJSON，未被旧1条压过；events空历史仍坏|三行迁移/备份子项PASS；模块迁移整体FAIL|
|mixed_bad_history_preserve|actions被改写为[对象,"THIS_IS_NOT_JSON_0748",对象]，好行保留；无bad_lines；bak为原主文本|坏行被接受、未冻结/可见恢复，D07动态FAIL|
|missing_actions_ndjson_backup|actions主仍缺失；两行NDJSON bak原样；state只“迁移1条events”，画面无对应恢复出口|备份无法恢复且无明确失败关闭，D07 FAIL|
|corrupt_events_preserve_old_backup|events变为["BROKEN_EVENT_PRIMARY_0748"]；原合法数组bak被坏主原文覆盖；合法旧备份字节在该业务jail任何文件均不存在|坏数据假迁移且覆盖合法备份，D07 FAIL；原合成旧事件来源丢失|
|compact_restart_intent_preferences|原issued记录→{}，非空pending_input→空；合法空任务不变；空历史被嵌套|D01/D02持久恢复FAIL；空态渲染PASS子项|

8场state均记“迁移 1 条 events（旧 NDJSON→array）”，未保存输入全丢。图片可见区域仅有登录/无可见任务说明，没有历史损坏/备份恢复的可继续出口；不声称不可见区域绝无控件。未登录时无权task选择清空可以是合法过滤，**不单因selected_task_id空判缺陷**。

## 缺陷及 Kimi-K3 修复清单

只复核原编号；以下P1均直接影响M2核心，非视觉建议。每项源码行对应本轮532303 B冻结main。动态范围与源码反例分开。

### D-M2-01 — P1 / 必修 / 部分关闭，输入恢复仍未闭合

- **文件/行**：`app/bundle/main.splash:500–519` loadViewState，`:876` saveState，`:1110–1112/:1187–1207` 启动加载/迁移保存，`:10991–10996` 初始化落盘；登录入口`:9854–9878`。
- **触发**：任一本轮隔离seed的state含非空pending_input，原生冷开；compact亦含已保存意图。
- **实际/预期**：8场pending_input全变空，启动落盘覆盖旧输入。预期冷开保留未保存内容；加载失败时明确状态并禁止默认空值覆盖。原空白/解析/控件句柄错误已关闭，空输入和退出提示实际可见；不要求重修渲染。
- **根因/影响**：当前加载不提供可验证恢复结果，启动会无条件saveState；不能用0错误说明偏好已经恢复。导致用户输入/恢复线索丢失。**具体是parse/字段读取哪个内部点导致本次input未恢复，未插探针，未知**；不能杜撰为某个UI事件已清空。
- **证据**：B全场input_before/after；H各seed对应state及运行state；PNG；A。源码白名单确有pending_input，动态仍失败，故不能仅再加同名字段交差。
- **具体改法**：在固定VM验证state完整parse/字段并入，读回非空输入；loadViewState返回明确结果，失败保护原文且不以默认STATE覆盖；成功后才保存。将意图恢复与D02共用严格安全白名单，actor/session永不恢复。
- **验证**：新同digest harness，非空中文输入/空输入/缺字段/损坏state分别冷开，核磁盘+UI；无法恢复保持原文并可继续，未登录不成为主体。可信登录完整仍受本轮输入白名单通道BLOCKED，不伪造已通过。

### D-M2-02 — P1 / 必修 / 未闭合：内容代意图，unknown创建仍可重复

- **文件/行**：main`:5938–6062/:6081–6118` 创建；`:6253–6301` 意图记录；`:500–519` 不恢复action_keys；`:6404–6460` 原确认重放；真实人工确认按钮`:10090–10099` → confirmDraftModelBound`:5700` → createDraftFromPanel → pending/task提交。
- **触发/实际**：创建回执pending/needs_verify时只筛final/final_recovered，随后仍newId/TASKS.push再提交；同内容独立新确认仍合并到内容key；cold保存的issued意图实际变{}。原确认后合法推进到ACCEPTED/v9，新增对账器因当前不是OPEN（6409）把原final重放判unknown（6456–6458）。创建/重放业务动态没有执行，这是明确源码路径，不虚称本轮重复工单已产生。
- **预期/影响**：一次确认稳定不可变意图，unknown先对账不重建；同内容新来源可新建；后续版本不抹掉原动作。当前可重复创建、误吞新意图、丢失重试key、合法历史误判。
- **根因/证据**：内容fp充当意图身份，创建未覆盖unknown状态，加载白名单漏意图，新对账器把历史结果绑到当前状态。E/source-audit/累计diff、B/compact及上述完整调用。
- **具体改法**：持久intent_id/actor/task/command/不可变payload/key/phase，显式区分新确认与重试；创建也走统一边界，所有unknown先查原动作；安全恢复已存意图；原回执完整返回，当前task另查。保留新确认磁盘事件核验的改善，移除“当前必须OPEN”作为历史成功前提。
- **验证**：正常重试、跨状态、同key异参拒绝、同内容新来源、unknown创建重试、currentv9查原v1。按task/action/version/event数及完整原result核对；原key不重生，独立新意图可新建。

### D-M2-03 — P1 / 必修 / 未闭合：关联提交可假成功

- **文件/行**：main`:886–900` 保存/事件；`:3854–3888` final状态；`:3890–3996` commitBound；`:4093–4137` 补事件；`:6497–6513` 接单入口。动作链为runAction/acceptTask→稳定key→runCommandBound→commit/commitBound→logEvent→成功提示。
- **触发/实际**：task落盘后final/event间失败；或actions/events脏历史保存只return。`_setReceiptStatusFinal`仍按内存matched=true返回，commitBound在event之前成功，接单再写event/成功提示；恢复补事件计数不核save成功。没有本轮认证提交，因此**这些是源码反例；本轮坏seed迁移失败另归D07**。
- **预期/影响**：任务/回执/事件业务一致、未知可收敛，错误不能显示成功。当前存在部分提交/假补齐路径。新增confirmDraft磁盘关联事件核验认可，只覆盖确认子路径，不代表全写命令一致。
- **根因/证据**：独立文件保存无明确持久成功结果和完整恢复协议，memory matched/计数代事实；源码/E diff。不能把tmp+主写称原子事务。
- **具体改法**：任何脏历史整体禁写；记录关联before/after/action/event可恢复协议；保存返回可验证结果、独立核权威磁盘完整回执/唯一事件才成功。每写点未知保留原key，不让模型/旧路径跳过。
- **验证**：pending/tmp/task/final/event各写点异常或中断，同盘重启核权威盘、回执、事件、UI。event保存失败不能成功或仅计数补齐。精确注入当前schema不能表达，动态BLOCKED于控制能力，不以环境rc71/rc3作理由。

### D-M2-04 — P1 / 必修 / 未闭合：version++仍代原动作提交证明

- **文件/行**：main`:4013–4088` 恢复，特别`:4060–4072`；`:3854–3996` final/readback；`:6404–6460` 历史确认。
- **触发/实际**：needs_verify期望0/afterACCEPTED，但另动作造成OPEN/v1/另一承接人，恢复仅disk.version==expected+1即final_recovered；pending较新版本改superseded。当前v9也不能从原确认接口查原v1成功。无认证seed中4回执保持原状是未登录保护子项PASS，**未运行该认证恢复，不虚报本轮已造final**。
- **预期/影响**：原action及完整after核验；事实不足保持未知，未提交可明确继续，后续版本独立展示。否则可能假成功或永远无恢复出口。
- **根因/证据**：bootReconcilePending与r7同码，按版本大小替代动作事实；B/two_unknown、E/source-audit、main。rid精确匹配、缺rid不按cmd回退等已修子项保留。
- **具体改法**：原action提交标识、关联before/after/事件证明；原final历史结果不依赖当前状态；orphan明确按原key继续或失败，不能只留人工核对文字。
- **验证**：写成功读回失败后查询不增version/event；无关同版本不能final；currentv9查原v1；缺rid保持未知；未提交原key能按协议继续。真实动态NOT_RUN，不代签。

### D-M2-05 — P1 / 必修 / 未闭合：无原子竞争边界，创建未统一

- **文件/行**：main`:3516–3580/:3582–3610` 锁；`:3616–3628` 命令取锁；`:3890–3920` 提交锁检查；`:6060–6097` 创建直接提交。
- **触发/实际**：两上下文先读空，A写A读A通过，B写B读B也通过；提交前再读只能缩小窗口，仍非原子互斥；创建不先取锁，commitBound空锁允许继续。**有效源码交错，不是本轮真正竞争实测**。完整token归属/失败关闭/同actor互释改善认可。
- **预期/影响**：同事实盘两个可信上下文同步接单只一赢家，创建与更新同一可信写边界。当前双提交/丢更新不能排除，源码自身声明HOST_PRIMITIVE_BLOCKED。
- **根因/证据**：普通fs.write/readback不是CAS，expected_version重读不能等价原子提交；E diff/main。harness当前串行run_scenario且fresh HOME，不会形成同盘竞争。
- **具体改法**：验证宿主真实原子锁/CAS或唯一可信写者；创建与所有写命令统一，session唯一owner和崩溃回收。无原语就给最小可运行复现和技术缺口，不继续假称互斥。
- **验证**：独立账号与同actor不同session均在同权威盘同步竞争；一成功action、一承接者、一成功事件，无互释/丢更新。现白名单无共享盘屏障/并发调度，完整动态BLOCKED，技术解阻无需新Abram授权。

### D-M2-06 — 原白名单根因关闭保留

sourceOk:805与r7同码；addEvidence/quarantineEvidence/togglePin准入未回退。不重新列P1、不重修。旧Web/MCP/runner及graph/reset真实负例未执行，T24仍NOT_RUN。

### D-M2-07 — P1 / 必修 / 独立原生失败：坏历史被假迁移，合法备份被覆盖

- **文件/行**：main`:901–939` loadJsonlLines；`:1187–1239` 启动迁移/保存；`:1277–1389` migrateJsonlLegacy，特别`:1284–1302/:1306–1327/:1361–1389`；`:1399–1410` 分行。
- **触发**：R的合法`[]`、valid→非法裸词→valid、缺主两行NDJSON bak、非法event裸词+合法旧数组bak；均使用本轮隔离Store。
- **实际/预期**：①空数组被当一条NDJSON记录迁为`[[]]`；②非法裸词被parse为字符串后当合法记录迁入，未生成bad_lines/冻结，覆盖式改写主历史；③缺主的实际NDJSON bak仍不恢复，无对应可见拒绝出口；④坏event主变字符串数组，合法旧bak被坏主文本覆盖，原合法事件备份在业务jail消失。预期严格合法数组/记录schema、坏行原文保留且整体禁写、备份恢复格式统一、覆盖前保护既有有效来源。三条合法NDJSON的全字段迁移及主优先子项已PASS，不能因此给整体PASS。
- **根因/影响**：宿主宽容parse_json，非nil及len不是合法历史schema；空合法数组走逐行兜底；bad裸词也被非nil接受；迁移无条件改写唯一legacy.bak，恢复仅整体parse/len。导致坏数据假成功、丢原合法恢复来源，直接违反可靠恢复。**本轮丢失的是合成旧备份，不是原业务数据**。
- **证据**：B/mixed坏字符串、good_rows_exact=true、bad_lines=false；B/corrupt旧备份全jail缺失、新bak等于坏主原文；B/cold空数组嵌套；B/missing主缺失；A/H各盘/PNG。state只显示“迁移1条events”，可见区域无历史恢复提示。
- **具体改法**：严格辨别数组与NDJSON、逐记录字段schema和完整JSON，合法空数组原样；裸词/字符串/嵌套数组拒绝；主/bak共用合法解析；已有合法bak不无条件覆盖，保留坏源及有效恢复来源；完整字段读回，失败整体冻结并提供实际可见恢复出口。
- **验证**：合法空/1条/3条、混坏行、全坏主+合法bak、缺主NDJSON bak及已有旧bak；核全字段/原文/各备份/冻结/UI。成功迁移后同Store再开不得[]→[[]]→更深嵌套或再覆盖恢复来源。存储写点失败继续查盘，不能以0错误或条数通过代替。

### 建议挂账（不单独导致 FAIL）

- 提供固定宿主支持的可信文本输入、共享盘竞争屏障、逐写点故障/响应丢失和连续同Store重开协议；本次不改业务/驱动或加后门，相关动态项如实BLOCKED/NOT_RUN。
- 交接机械生成与当前共享源码一致的M2候选清单、配置差异及冷启动证据；本轮review字段已定位实际运输候选，不把旧M2实施声明移给新字节。布局/字体/皮肤和无关后续模块问题不列必修。

## 相关既有验收逐项复核

保留 `docs/build-loop/ACCEPTANCE.json` 原定义。FAIL精确区分源码和动态失败；BLOCKED只用于本轮已证实或schema不能表达的控制能力。作者/旧后端PASS不转移到当前原生版本。

|项|结论|本轮证据和实际范围|
|---|---|---|
|G0-B|BLOCKED|原生根/空输入/退出/伪actor保护PASS子项；tap/type/key明确被拒，可信成功登录和两主体查写矩阵未执行。|
|G0-C|FAIL|D07假迁移/合法备份丢失和D01/D02持久恢复动态失败；D03/04/05源码反例未关。|
|T02|FAIL|D02内容代意图、unknown再创建源码反例；实际创建重发/冲突/新来源业务NOT_RUN。|
|T04|FAIL|D05非原子锁及创建绕过源码；真正同盘同步竞争BLOCKED于harness调度，不串行代签。|
|T15|NOT_RUN|未认证，未实际陈旧版本拒绝/刷新/保留输入或阶段百分比负例。|
|T16|FAIL|D02原key恢复丢失动态，unknown创建源码；提交响应丢失/原key实际重试未执行，精确控制缺口单列。|
|T17|BLOCKED|白名单不提供SSE/断线/响应丢失/重连控制，不能以fresh HOME冷开代全量回读。|
|T18|NOT_RUN|未登录不显示任务PASS子项；回放/恢复门控源码保留；独立主体列表/搜索/事件/附件防探测完整矩阵未执行。|
|T22|FAIL|D03保存/关联协议源码未关，D07迁移实测失败；逐业务提交写点异常和同盘恢复BLOCKED于精确注入通道。|
|T24|NOT_RUN|D06白名单原修复保留；旧Web/MCP/runner真实负例和graph/reset未执行，不声称无绕过。|
|T29|NOT_RUN|未登录点击退出有提示，不代宿主grant关闭/到期/共享卡生命周期和实际调用。|
|T32|NOT_RUN|未运行配对过期/重用/poll_secret、Web审批绑定或脚本token隔离；五账号哈希不等于配对机制。|
|T37|FAIL|D04版本代提交及历史必须当前OPEN源码反例；未发生模型/真实提交后的回读超时，不虚报动态假成功。|
|U03|BLOCKED|根和未登录权限空态可见；可信输入通道缺失，三真实主体同task事实/动作/自验禁止未执行。|
|U07|FAIL|8场未保存输入全丢；持久issued意图冷开变{}；真实重复提交/响应丢失/版本冲突/离线完整链NOT_RUN。|
|U08|FAIL|登录/空态出口PASS子项；坏历史假迁移、缺主拒恢复没有对应可见恢复出口，不能真实继续可靠恢复。|
|T28|FAIL|同候选安装/原生根PASS子项；冷开输入/意图恢复失败，原生操作→权威回读→同task重开完整链NOT_RUN。|

## 判定与门禁

- **最终结论：FAIL**，精确适用于上述实际运输版本中的M2共享源码及固定宿主。本地准入、独立安装、隔离/回收、根渲染、空输入/退出和三行合法迁移子项通过，不能代替可信身份与可靠执行核心。
- **必修仍为 D-M2-01/02/03/04/05/07**；D01旧空白/解析已关，只剩输入恢复及可信链所需验证；D06保持关闭。不重修已关子项、不开始后续模块。
- 修复优先：先严格历史解析/备份与安全恢复输入/意图，保持0解析和可见根；再按原编号统一意图/关联提交/原动作查询/竞争边界。每轮提交新固定候选和同字节harness冷启动结果/图，不以注释或自测PASS交差。
- 具体动态缺口：宿主已拒输入动作，现schema无同权威盘同步竞争、逐写点故障/响应丢失、连续同Store重开和任意原key/payload协议。无ABORT，未使用agent rc71/rc3为阻塞原因。这些是技术能力缺口，不需身份/provider新授权。
- 受影响前序回归：真实根与未登录空态子项PASS；输入/意图恢复FAIL；M1完整结论仍FAIL，不改其他模块。
- 门禁：仅改GATES的M2 status、review_report/reviewed_at及review_*；review_report指本r9，review_candidate_id指实际 **M7-r7-worktree**，review_base_candidate_id指M2旧r7比较基线，source/digest与运行一致。作者candidate/base/implementation、其他模块和顶层状态保持原值；旧M2审查字段追加review_history，整份修改前副本 **E/GATES.before-review-r9.json**。
- 原ACCEPTANCE.json不覆盖历史；17项当前原生精确状态见本报告、E/final-acceptance-17.json及M2.review_acceptance。最终门禁/保护文件验证 **E/final-review-verification.json**，确认原业务源码、宿主、真实账号/映射、seed/运行证据未改变。
- **NEEDS_ABRAM=no**：本地catalog/install_staged已实证可用，身份/provider/隔离离线签名均已授权，无余额不足/欠费或必须公开发布事项。没有读明文凭据/密钥，没有发布、上传、push、发消息或联网模型调用。
- **不允许进入下一模块。** 构建方Kimi-K3留在M2按本清单修复；没有由本报告授权执行后续模块。

STATUS=FAIL
NEEDS_ABRAM=no
