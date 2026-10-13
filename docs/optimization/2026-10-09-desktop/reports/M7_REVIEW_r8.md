# M7 独立 Review r8

**最终结论：FAIL。** 本候选同版本运输、原生解析/渲染、隔离与回收通过；R-M7-01 的登录控件读取报错已关闭。R-M7-02 部分修复但截断/残缺任务仍漏过恢复门禁，真实恢复提示与入口未在截图可见区域展示；R-M7-03 的合法提醒误判已修，但布尔 due_ms 被当作合法到期时间加载。这两项 P1 直接阻断可靠的本地发布候选。没有 harness ABORT，不把 CLEAN 当作业务 PASS。

- 审查者 / 日期：当前 Codex 主会话唯一独立审查者，无子代理；2026-10-12，Asia/Shanghai。
- candidate_id / base：`M7-r7-worktree / M7-r6-worktree`，版本 **0.1.0-f**。以用户交接请求、实施 r7、CANDIDATE、CONTEXT、GATES 定位，未按 mtime 选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；dirty 内容由作者 dirty.diff、本审查 scoped-dirty.diff 和冻结字节定位。HEAD 单独不能复构本候选。
- 包：`runtime/optimization/2026-10-09/M7/r7/release/octosense-repair-0.1.0-f/`；digest=`9e1f7aec09785858c744272048afd786c02dee05c1a29aa3838cca8db05ed5cf`；main **532303 B**，SHA-256=`7b82c1313dcf14379942f01453784f44eb70321257d61a9214fc09d39173e23c`，与工作区主源一致。
- 作者报告 / 清单：`reports/M7_IMPLEMENTATION_r7.md`；`runtime/optimization/2026-10-09/M7/r7/CANDIDATE.json`。
- 前置：**M6=FAIL / M6-r7-worktree / M6_REVIEW_r8.md**，没有已接受的 M6 PASS。按用户挂账裁决继续 M7；不修改 M6，不代签前置通过。本轮 FAIL 来自独立原生核心反例。
- 快照：第 1 段保护的 **1085 文件全部一致**。候选、源码、材料、作者证据、宿主、工具、harness/schema、seed、原门禁/台账无漂移。报告与门禁写后再核，见 S/final-review-verification.json。
- 实际宿主：项目内 M0/r3 提取 OctoSense.app；octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；octos-kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。核的是固定二进制，不声称可由未知上游源码重新构建。
- 原生执行：驱动沙箱外 harness，**05:35:22–05:37:44 +08:00**；8 场 CLEAN、quit_http、host rc0。审查者没有自行启动 launcher、sandbox-exec/pgrep、--help、osascript、辅助功能或其他 UI 自动化。
- 模型/路由：固定候选 enabled=false、capabilities=storage，8 场 needs_model=false，真实调用 **0**。当前工具不能核验/切换主会话 Router 或指定模型，也不能取得自身 createdAt/修改标题；未声称完成这些动作。
- 已阅读：第 1 段基线浓缩材料、实际 AGENTS/00/01/02/M7/04、上轮缺陷及相关差异；本段完整 summary/result/profile/MANIFEST、日志/denials、运行包及隔离数据。逐张查看 8 张请求 PNG，以及登录场不同的 part PNG；其余 part 与对应 PNG 同字节。
- 已运行：第 1 段独立离线 stamp/check/catalog verify/official install_staged/Store rebuild/may_run；驱动独立 8 场；本段只读证据审计。`PYTHONDONTWRITEBYTECODE=1 python3 -B runtime/optimization/2026-10-09/M7/native/review_r2_2104/audit_phase2.py` rc0，**5935 个证据一致性检查，非 5935 个业务测试**。
- 未运行：可信账号成功/错误口令、非空凭据清空、三角色命令与查询核权、完整成功/退回链、权威动作回执、真实附件、模型三链、通知去重、同 Store 跨进程恢复、精确运行中故障、完整键盘/文字放大、官方 scan、完整演示。具体白名单无法表达的步骤单列 BLOCKED；没有实际操作的领域/模型项 NOT_RUN。
- 安全：本段文件访问与所有审查产物均在项目内；未访问原账号/安装/host-data、明文凭据、模型密钥，无外部发布、联网调查、push、Issue/评论、消息、部署或计费变更。本轮未生成私钥；作者 keys 目录为空，删除记录与当前残留检查保留。
- 置信度：同版本/隔离/原生空输入提示、损坏任务未标恢复、bool 提醒误接受 **高**；完整可信业务/模型效果、宿主内部 parse 返回值与隐式类型转换细节 **未知**。

## 证据索引

- **H**=`runtime/optimization/2026-10-09/M7/native-runs/review_r2_2104_REQUEST_review_r2_2104/`，本审查者独立请求的驱动证据，只读未改。
- **S**=`runtime/optimization/2026-10-09/M7/native/review_r2_2104/`，包含 phase1-audit、protected snapshot、源码差异、独立 Store/seed、native-evidence-audit、64 项逐项表与最终写后校验。
- **R**=`runtime/optimization/2026-10-09/M7/native/REQUEST_review_r2_2104.json`；SHA-256=`b704467f1f7bfcef1296f5ccec270560bb5754fb7369252e083bd3a6637ab556`。
- **N**=`runtime/optimization/2026-10-09/M7/native/REVIEW_NOTES_r2_2104.md`，第 1 段笔记保持历史原文，不回改为最终结论。
- 作者 build_r2_2104_REQUEST_build_r7 只供参考，不代本次独立结果。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、前置、差异|交叉定位、源摘要、旧新 diff、M6 门禁|审明确候选，前置如实|r7 明确，25 个差异块；M6 FAIL 挂账|定位 PASS；前置未 PASS|S/phase1-audit、diff；M6 r8|
|最终字节与宿主|对照 frozen/transport/installed/mirror/.running|实际运行同候选同宿主|8 场全部 7 个运输文件同字节；6 个非 manifest 资源与冻结相同|PASS|S/native-evidence-audit；H 运行包|
|证据完整性|重算 MANIFEST、request/result/summary|无错 hash、漏项、重复|1091/1091 匹配；5935 检查无失败|PASS（证据）|H/MANIFEST；S/audit|
|隔离与回收|重建 profile、禁读/禁写探针、PGID/writes/denials|新 run 内写，禁读，无残留|8/8 probes true、pre/post NONE、PGID_after=[]、CLEAN、退出 rc0|PASS|H 各 result/profile/denials|
|合法空任务/空提醒冷启|新 Store tasks=[] 与真实路径 follow_ups=[]|合法数据不误拒，工作台渲染|0 parser/0 runtime，pending=false，无备份|PASS 子项|clean_empty state/原文/PNG/log|
|空输入登录/清空入口|内置 taps:695,209→748,209→695,209|读取无异常、空输入明确提示|PNG/part 显示“请输入账号 ID 与口令”；0 runtime|PASS 子项；R01 CLOSED|login_empty_clear PNG/log；源9861|
|可信输入/成功登录|核固定宿主白名单与前轮 unknown 实证|真实口令输入、会话核验|本轮未形成非空输入；key/type 固定宿主不支持|具体步骤 BLOCKED；成功链 NOT_RUN|N；受保护前轮日志|
|合法提醒加载|新空/单条正例真实 loader 路径|不误损坏，单条完整恢复|正例 pending=false，单条各字段准确；false 反例拒且备份一致|PASS 子项|clean/valid_one/bad_false state/盘|
|提醒成员负例|新单条 due_ms=true|整份拒绝、保护并 pending|bool 成员进入 m6_follow_ups，ACTIVE、pending=false、无备份|**FAIL R03**|bad_followup_bool_due state/原文|
|坏任务保护|新非法顶层/截断/残缺成员冷启|准确分类、保护原文、可见恢复|顶层拒绝备份；另两场准备就绪、pending=false、无备份，列表留初始化|**FAIL R02**|三 tasks state/原文/PNG|
|人工恢复出口|看真实错误与恢复入口|用户可见且可继续|bad_top 盘有错误，PNG 可见区未展示 banner/恢复按钮；恢复操作未执行|可见出口 FAIL；操作 NOT_RUN|PNG；源9885/9906/9932|
|完整业务/权威回读|同候选可信三角色、正常/退回/重开/故障|实际闭环有权威结果|没有领域命令/成功回执；仅加载/空输入子项|NOT_RUN；核心加载 FAIL|64 表与 R02/R03|
|真实模型|核固定 config/caps、proxy/stats/env|真实调用证据|enabled=false/storage；proxy/stats 缺省；0 请求，无欠费|NOT_RUN|实际包与各 result|
|材料媒体一致|11 指纹+selfhash、listing/当前截图|不挪用旧完成态|字节指纹/外置当前 PNG 一致；placeholder 与完整演示欠缺，旧 README 建议挂账|一致性子项 PASS；媒体 NOT_RUN|S/phase1-audit；A01/02|
|本地准入和独立审阅|独立 check/verify/install/may_run、功能复验|可安装且可靠使用|准入通过，实际恢复/schema FAIL；官方 scan 未执行|本地准备 FAIL|S/phase1-audit；本报告|
|外部发布/赛事/收录|只读本候选交接回执|各状态独立|无本候选实际回执、无外部动作|状态分离 PASS；外部 NOT_RUN|review_summary.external_statuses|

### 原生证据审计细节

1. MANIFEST 1091 项完整覆盖全部证据文件（MANIFEST 自身除外），无重复/漏列/错摘要；嵌入 R 完全一致；harness/template、各场 purpose/命令/时间/退出与 summary 对齐。8 场均 16.23–16.33 秒，无 ABORT。
2. 全部 profile 按真实新目录、控制口、记录的原 HOME 字符串重建相同；禁读 secrets、明文 credentials、~/.codex、~/.cc-switch、~/.ssh，场外写探针拒且 created=false。仅核驱动记录，审查者未实际读禁区。HOME/app-data/cache/tmp/logs/config 路径全部在对应新 run。
3. pre/post 均 `{rc:1,out:"",err:"",class:"NONE"}`，最终 PGID 全空；quit_http=ok、host_returncode=0，外部 Library 扫描空、原 HOME .octosense mtime 前后相同。模板含 /dev/null 与 unix-socket 例外，按已授权 harness 口径记录，不夸大为全 IPC 禁止。
4. denials 逐行重算与 result 一致：443 外联、系统 Metal 缓存、/dev/dtracehelper 被拒。拒绝不表示成功越界；host news=7 sources failed，不声称宿主没尝试网络。运行期 PGID 还记录 pmset 与一场 osascript，记录无参数/用途，不能据此断言发生 UI 自动化；最终均回收。审查者请求和命令中没有这些自动化调用。
5. writes 有序、唯一、每项真实存在并在 run 内，6 场117项、两个保护反例118项，未达到400项截断上限。这是驱动 mtime 文件清单，不是领域命令数。源/安装/mirror/唯一 .running 均逐字节对应本候选运输包；日志未打印 digest 不构成错包证据。
6. 全量 host.log 字节、markers、tail 与 result 相同；8 场0 parser、0 `[E] splash`，532303 B 为本业务脚本，809 B 为另一次系统窗口 eval。tick_exception_count 都为0，不能以此反推损坏任务已准确恢复。
7. 8 张请求 PNG 为2800×1716；登录 part 与最终图不同，已额外查看；其余 part 各与请求 PNG 相同。合法提醒/false/bool 三类图同 hash，只说明未登录首屏相同，**无法凭截图区别 loader 成功与失败**，判定须靠盘与 state。
8. clean 空提醒18 B、空任务3 B；合法单提醒171 B恢复准确；false反例42 B逐字节原文/.recover保留；bool反例161 B被接受、无.recover；顶层坏任务31 B原文/备份一致；截断24 B和残缺29 B均原文保留但未标 pending/未备份。没有发生领域写，不声称已丢数据或消息误发。
9. 8 场 model_proxy/model_proxy_stats 均缺省，MM_KEY/OCTOSENSE_MODEL_ENDPOINT 未注入，matches needs_model=false；没有把缺省字段当代理成功，也没有402/欠费证据。

## 缺陷与上轮对账

只对上轮编号与直接回归作结论，不新增无关扩审。

|编号|本轮结论|
|---|---|
|B-M7-01|CLOSED 保持：8 场解析清零、业务工作台渲染|
|D-M7-01/02/03|原关闭准入/指纹子项保持，不挪用旧业务结论|
|A-M7-01|OPEN/P2 建议：README 旧入口/旧版本/旧完成话术沿上轮挂账|
|A-M7-02|PARTIAL/P2 建议：版本与旧图结论分离改善，placeholder/完整媒体仍欠|
|A-M7-03|CLOSED 保持：11 指纹+selfhash、作者 keys 当前为空；审查者无新私钥|
|R-M7-01|**CLOSED（原控件读取报错）**：空输入 handler 正确提示；成功登录/非空清空未验证|
|R-M7-02|**PARTIAL，仍 OPEN/P1**：`_`循环消失、坏顶层保护通过；截断/残缺漏过门禁、假就绪及不可见恢复仍失败|
|R-M7-03|**PARTIAL，仍 OPEN/P1**：合法空/单条和false拒绝通过；新数值探针接受bool，非法schema恢复失败|

### R-M7-02 — P1 / 必修：损坏任务仍被当作就绪，可靠恢复未闭合

- **文件/行**：同字节 `app/bundle/main.splash:1163–1180` load；`:1017–1021` 只核 id 的成员门禁；`:950–951` 启动消费 evidence；`:1047–1098` 恢复；`:9885–9906/:9932–9937` 左栏固定布局/入口；`:10977–10984` tick。
- **触发**：R/truncated_tasks 全新 Store 放 `[{"id":"REVIEW_R2_CUT",\n`；incomplete_task_member 放 `[{"id":"REVIEW_R2_ONLY_ID"}]\n`；bad_tasks_top 正交反例放 `{"review_r2_invalid_top":true}\n`。不登录、不改原业务数据。
- **实际/预期**：前两场 state 均 `tasks_pending_recovery=false`、`status=准备就绪`、`tick_exception_count=0`，无.recover；PNG 列表仍“初始化”、详情待选任务。顶层反例正确 pending=true且备份精确，但其 PNG 可见区域没有恢复错误/入口。预期截断文本与缺必需字段的记录在加载前准确拒绝、保护并阻断普通写，明确展示可继续恢复的出口；合法空数组和真实合法任务应正常加载。
- **根因/置信度**：当前门禁依赖宽容 parse 后结果和 id 最低检查，缺原 JSON 完整性及运行必需字段验证（源码事实高）；宿主实际 parse 返回的内部数组内容与初始化停留具体执行点未知，未注入探针，不编造。左栏把新增错误/恢复放两个 Fill 占位及已有长控件之后，当前真实视口下不可见（高）。不再把旧 `_`循环列为未修，也不声称新的 tick 错误已发生。
- **影响**：加载/失败恢复核心不能可靠识别坏数据，界面假就绪但不能正常继续；既有原文未变不能代替恢复成功。硬1/2/4、G0-C、U08/U09/U11、P01/P05 受影响。未证明实际丢数据，不把潜在事故当已发生。
- **证据**：H 两场 tasks.json/state.json、无.recover、PNG，log :43 eval532303 B且无 `[E]`；bad_top 原文/备份/state/PNG。S/native-evidence-audit 中 fixtures 和状态；25块 diff。本结论来自独立原生数据，不依赖作者自述。
- **具体改法（Kimi-K3）**：仅修 R02。用固定宿主实证可用的严格 JSON 完整性/数组/运行字段校验；至少保证截断、尾随垃圾、缺证据数组等不进入 TASKS，不能只加首尾括号或只对这两标记特判。加载和覆盖恢复共用该校验；保留原文+备份读回、pending三写闸。保留原文分支若仍不能加载，不应声称完全恢复/无条件解锁，或采用明确的备份后新工作副本并读回有效事实源。将错误和安全恢复入口放实际可见区域，必要时紧凑排列/采用已支持滚动，先解决核心可操作，勿新增美化范围。
- **验证**：新冻结 digest，经 harness 复跑合法空、合法完整任务、非法顶层、截断、id-only；负例准确保护、pending/备份，0循环且截图真实可见。用内置可达动作分别验证保留/覆盖、备份失败/读回失败保持未决，成功读回权威合法任务。精确故障/同盘重启若现白名单不能表达，给具体能力缺口，未执行继续 NOT_RUN/BLOCKED，不能伪造盘内完成状态。

### R-M7-03 — P1 / 必修：新的“数值”探针接受布尔值，放宽提醒恢复门禁

- **文件/行**：`app/bundle/main.splash:1007–1014`，特别 `:1011–1012`；成员 `:2175–2176`；loader `:2255–2265`；共用schema `:2185–2195` 和恢复 `:2325–2335`。
- **触发**：R/bad_followup_bool_due，真实 loader 嵌套路径合法对象内单条 `{fu_id:"review-r2-bool",task_id:"REVIEW-R2-NONEXISTENT",role:"reporter",kind:"appointment",due_ms:true,status:"ACTIVE"}`；其余必需字段合法，与远期数值正例对照。
- **实际/预期**：state.m6_follow_ups 完整含该成员且 due_ms仍true，pending=false、status准备就绪，161 B原文保留但无.recover。预期按修复自身明示“bool 一律拒”整份拒绝，pending保护/备份；171 B合法数值正例正常恢复。
- **根因/置信度**：`v-v==0` 不是在本宿主上已经成立的严格数值类型判定；当前实际路径接受bool已实证（高）。内部转换细节未知，不能用其他语言规则当宿主证明。load与恢复共用这条错误探针，静态统一不能证明正确。
- **影响**：损坏的到期时间进入 ACTIVE 提醒状态，提醒恢复前提失效；这是原 R03 schema 修复的直接回归，非无关扩审。硬1/2、G0-F、T23、P01/P05 不能放行。虚构task不存在，本轮未触发发送，不声称已发错误通知。原合法误拒根因已修的子项保留。
- **证据**：H/bad_followup_bool_due 的原文/state/无.recover、result及实际包；valid_one_followup 数值正例、bad_followup_false 保护反例；S/native-evidence-audit。截图同hash无法证明正反例状态，采用权威盘读回。
- **具体改法**：仅修现 schema 数值判定。先用固定宿主 harness 验证实际支持的类型判定/严格JSON数值解析原语，对 true/false 显式拒绝并覆盖字符串、对象、数组、nil、非有限值（输入能表达者）。不要靠宽容减法作为唯一条件，也不恢复未经验证的 typeof字面假设。load与受控恢复继续共用同一严格validator、原文/备份/pending护写保持。
- **验证**：新冻结候选合法空/合法数值单条保持通过，bool true/false及其他非法成员整份拒绝、备份精确、pending=true、0运行错误；真实恢复入口与写后 schema读回也复核，不能只运行静态字符串检索。

## 全量既有验收逐项表

以下64项保留原定义；PASS仅当前已执行范围，FAIL是对应核心前提实际失败，不冒充未执行的完整业务链已跑。NOT_RUN保留未执行事实，BLOCKED仅具体白名单能力缺口。逐项历史来源、candidate、运行形态见 S/final-acceptance-64.json 和 GATES.M7.review_acceptance。测试数量不作为放行理由。

|编号|既有定义|本候选结果|证据与范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|PASS|本digest独立准入、本地install_staged/Store和8场真实.running与冻结字节一致，0解析/运行错误，工作台可见；不含可信业务完成。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|空输入登录正确提示，旧R01读取错误关闭；成功/错误口令、5账号会话核验及写/查询核权未执行，不以空输入代签。|
|G0-C|唯一事实源、原子一致性、并发与恢复|FAIL|R02截断及只有id成员漏过恢复门禁，pending=false/status准备就绪、无备份；坏顶层保护子项PASS。并发/原子命令/权威回执未执行。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|未进行真实附件选择、上传/回读、归属/轮次与失败恢复；隔离/回收PASS单列，不能替代真实附件门槛。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|FAIL|R03合法空/单条加载和false类型拒绝已PASS；due_ms=true非法提醒被接受为ACTIVE且pending=false。去重/通知/任务意图实际运行未执行。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|FAIL|提醒schema直接回归R03 FAIL：bool due被接受。合法加载子项PASS；同Store进程重启、通知去重/改约旧作业未执行，不能由loader正例代签。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|NOT_RUN|原生启动/空输入登录与加载正反例已执行；没有可信主体对合法业务任务操作及权威回读/重开，R02坏数据恢复FAIL另列。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|本候选enabled=false、storage-only，needs_model=false；模型proxy/stats缺省、真实调用0，实际模型/助手及失败/白名单行为未执行。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|真实未登录工作台和空输入提示可见；可信三角色待办、阶段/下一处理人未执行，旧登录报错已关闭。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|损坏原文保留子项PASS/R02准确分类FAIL；重复提交、响应丢失/版本冲突/离线领域操作没有发生。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|FAIL|R02坏顶层已落pending/备份，但恢复错误与入口在真实截图可见区域未展示；截断/残缺任务仍初始化/待选而假就绪，无可见恢复提示。其他附件/过期场景未执行。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|FAIL|当前实际画面恢复banner/主要恢复按钮在左栏下部裁切，R02核心恢复受阻；登录行加高已改善。3种请求size均2800x1716屏幕图，150%调整无白名单动作属具体能力缺口，不代签。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|固定宿主前轮实际拒key:Tab/type（已保护日志）；当前白名单无法形成已授权可信文字输入/完整键盘流程，未使用外部自动化。不是agent rc71/rc3。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|FAIL|空输入登录读写入口子项PASS；坏数据恢复可见出口/准确加载R02 FAIL，完整滚动/文字输入/面板流程未执行。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|本轮仅复核R01/R02/R03直接回归；本定义所需可信领域操作、权威回执/权限或完整UI链未独立执行，不转移旧包/后端PASS。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|FAIL|独立同digest坏数据恢复R02/R03 FAIL；成功/退回业务链及同Store跨进程重开未执行。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|NOT_RUN|源码/dirty/包/宿主/工具及干净原生启动子项PASS；README旧入口A01为建议挂账，完整干净构建/说明未独立复跑。|
|P03|最终包准入check及实际scan审阅通过|NOT_RUN|独立stamp/check/catalog verify/install_staged与运行发现PASS子项；官方scan未执行，独立核心审阅本轮FAIL，不能以check rc0代签实际scan。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|NOT_RUN|8张独立PNG与本digest一致、材料指纹PASS子项；包内仍placeholder，无完整真实演示，A02媒体建议挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|FAIL|全部资源字节/11指纹/外部selfhash一致；必需R02/R03未关。本地交付一致性子项PASS不等于缺陷关闭。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|本候选没有实际公开源码/Hub递交回执；未执行外部动作，不挪用历史0.1.0-b回执；全局UNASSESSED原状保留。|
|P07|维护者商店收录结果|NOT_RUN|本候选没有维护者收录回执，未listing；全局历史状态不改。|
|P08|赛事正式提交入口回执|NOT_RUN|本候选没有赛事正式提交回执，未提交；全局历史状态不改。|

## 硬验收与判定

|硬验收|结论|理由|
|---|---|---|
|1 全部必需门槛有同候选实证，不冒充通过|FAIL|R02/R03独立核心反例失败；完整业务/模型/T/U未执行如实列明|
|2 正常、退回、失败恢复、重启及真实模型同候选|FAIL|失败恢复实际未通过；正常/退回/模型未运行，同盘跨进程重启白名单缺口|
|3 根包/秘密排除、源码包媒体描述一致|NOT_RUN|字节/指纹/当前外置PNG子项PASS；完整媒体未交付，A01/02建议挂账|
|4 本地准入和实际独立审阅、干净启动|FAIL|准入/冷启动PASS，实际独立功能审查FAIL；官方scan未运行|
|5 本地与发布/赛事/收录状态分开|PASS|本地FAIL；本候选P06/P07/P08 NOT_RUN；历史全局状态原样保留|

- **最终结论：FAIL；必修只剩 R-M7-02、R-M7-03（P1）**。R01原异常关闭；A01/02建议不是FAIL依据。不增加新模块或无关前序修复。
- **具体 BLOCKED**：固定宿主不支持已授权 key/type 文字/键盘输入（前轮真实unknown日志保留）；当前请求/schema无法表达同Store跨进程重启、运行中精确故障/交错、150%调整。这些是具体步骤限制，8场本身无ABORT。原生正常冷启、坏数据分类、bool探针、登录空输入均有执行条件，按实际PASS/FAIL判；不以agent rc71/rc3阻塞。
- **NOT_RUN**：可信成功登录和查询/写权限、三角色领域命令/回执与完整链、真实附件/模型、恢复按钮实际操作、官方scan、演示等。输入缺口不等于身份来源待授权；enabled=false不等于provider待授权。
- **前序回归**：只做现25差异块的解析/冷启、登录、合法与非法任务/提醒加载；来源D-M6-02合法加载已改善，非法成员依赖仍FAIL。不签M6或其他前序PASS、不改其门禁。
- **发布状态**：本地发布准备FAIL；外部发布/Hub递交P06、商店收录P07、赛事正式回执P08均NOT_RUN。没有本候选实际回执，未联网调查外部状态，不将历史0.1.0-b递交迁移到0.1.0-f。
- **门禁/原台账**：仅更新 GATES.json 的M7 status、review_*、reviewed_at与审查history。review_report 指本r8、review_candidate_id指M7-r7。旧审查字段保留history及S/gates-before-final-review.json，其他模块、构建字段、external_delivery和原ACCEPTANCE.json不改。
- **下一模块：不允许，不执行。** 留在M7由Kimi-K3按上述两项最小修复、重新冻结并交独立harness。缺合规输入/重启能力需明确宿主/驱动技术条件，不能用自造会话或业务完成夹具跳过。
- **NEEDS_ABRAM=no**：本地catalog/install_staged路线成立；身份、MiniMax、隔离签名已有授权；无402/余额/欠费或公开发布需求。剩余均为已授权技术修复/验证能力。

STATUS=FAIL
NEEDS_ABRAM=no
