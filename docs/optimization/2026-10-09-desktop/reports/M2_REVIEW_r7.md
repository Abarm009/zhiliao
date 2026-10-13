# M2 独立 Review r7

**最终结论：FAIL。** 本轮固定候选 `M2-r6-worktree` 已在独立 harness 中实际加载，6/6 场景业务区空白，每份日志 44 条 `[E]` 运行错误。隔离和进程回收 PASS，登录/任务核心入口 FAIL。D-M2-01/02/03/04/05/07 未闭合；D-M2-06 原白名单根因修复保留。未修业务代码，未执行下一模块。

## 受审范围与版本

- 审查者 / 日期：Codex 唯一审查方，2026-10-11，Asia/Shanghai；没有子代理。无法用当前工具核实指定主会话 Router 路由、取得 thread createdAt 或设置标题，未声称这些已经完成。
- candidate_id / base：**M2-r6-worktree / M2-r5-worktree**。依据用户明确交接的 build_r1_2104_REQUEST_build_r6、其请求、r6/native-prep/snapshot-start.json 和本地安装证据定位，不以 mtime 选版。
- HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty；main 439223 字节，SHA-256 **76f00c37740534b68ce66a8cc9d3c17a07f11aca8ebf8577071afa6113a911f4**。
- 阶段 1→2 保护文件全部一致。完整内容清单、源码冻结副本、上一轮实际受审 r5→r6 差异在 `runtime/optimization/2026-10-09/M2/native/review_r1_2104/`。运行 `.bundles` 与 `.running` 中业务 main 全部匹配该摘要；`.system` 宿主内置脚本单独排除。
- 宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**。日志记录 20000000 instructions、67108864 bytes heap、16777216 bytes storage；没有执行完整登录 KDF，不断言其超预算。
- bundle digest **209b46058e0a3228830f38519f6c7a294abd0ee75c85a4ac0e1d0c0b0d1a5637**。沿用该 digest 的本地隔离签名 catalog 副本；本轮未生成私钥。构建证据中两把私钥路径已核不存在、keys 目录为空；仅本地 install_staged 路线成立，不代表公开发布或完整 hub check 通过（作者 check 仍 REFUSED）。
- 作者报告：**M2_IMPLEMENTATION_r6.md 不存在**。GATES 作者字段仍指 r5；不将 M2_IMPLEMENTATION_r5.md 冒充 r6。以 review_candidate_id、review_summary 和本报告记录实际受审 r6，保留作者字段，材料缺口列建议。
- 前置：M1 仍 `FAIL / M1-r2-worktree / M1_REVIEW_r2.md`，没有已接受 M1 PASS。按 Abram 前序挂账裁决继续审查 M2，不伪造前置通过。针对基础界面做回归，结论 FAIL；未改 M0/M1 门禁或旧缺陷结论。
- 已读：AGENTS、CONTEXT_M2、00/01/02、M2文件、04模板、上轮 M2_REVIEW_r6、r6请求/准备脚本/快照/本地安装证据、原缺陷涉及源码、既有验收定义、harness schema/执行逻辑、本轮完整 summary/result/profile/log/denials/MANIFEST 和全部最终截图。
- 独立请求：`runtime/optimization/2026-10-09/M2/native/REQUEST_review_r1_2104.json`；驱动沙箱外运行窗口 **21:50:30–21:51:53 CST**。
- 下文 **H/** = `runtime/optimization/2026-10-09/M2/native-runs/review_r1_2104_REQUEST_review_r1_2104/`；**A** = `runtime/optimization/2026-10-09/M2/native/review_r1_2104/phase2/evidence-audit.json`，复核脚本 `review_r1_2104/audit_phase2.py`。阶段笔记 `M2/native/REVIEW_NOTES_r1_2104.md` 保留历史观察。
- 置信度：同版本加载、空白 UI、运行错误、权威文件比较、隔离回收和确定源码反例 **高**；真实凭据登录、真正竞争、逐写点故障及完整对账的动态结果 **未知/未执行**。

审查过程偏差：阶段 1 起始工具误读项目外记忆索引，违反本次路径限制；已在阶段笔记和当时输出披露，随后停止外部访问。该操作没有写外部文件或读原始业务凭据/provider密钥。本阶段仅访问项目内文件。此为审查过程违规，不能因 harness CLEAN 将其解释为全流程完全合规；不是由应用候选产生的新缺陷。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/请求一致|重算快照、全部 MANIFEST、seed、二进制、安装与运行 main|同一可定位候选，证据完整|963 项全部匹配，无未列文件；summary.request 与独立请求相同；保护文件及业务副本摘要匹配|PASS（证据范围）|A；H/MANIFEST.sha256；阶段快照|
|隔离/回收|逐场核 profile/probes/环境/进程/清单/denials|写入隔离目录，黑名单禁读，无残留|6场 probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN；无 library 新写，真实家目录 mtime 不变|PASS（harness范围）|H/各 result/profile/denials；A|
|真实登录/任务界面|独立 launch-hub 与 capture，逐张看图，读全文日志|登录、任务和错误恢复出口真实渲染|6张均空白；每场44条[E]，另有[I]中的函数/字段错误；任务界面不可操作|**FAIL，D01**|H/frames；cold/log:43–60、77–80、258起；A|
|硬1：重试/跨状态/冲突/新动作|追按钮→replay→stable key→boundary→权威存储|原动作不重复，异参拒绝，新意图可独立执行|D02源码反例未闭合；没有真实点击业务写/原动作查询|FAIL（源码）；业务动态 NOT_RUN；任意原key注入 BLOCKED于通道|main:4785–4890、5036–5129；A|
|硬2：主体/权限/版本/竞争|核登录及查写授权，锁有效交错|查写均核项目权限，同盘竞争一赢家|原生入口FAIL；replay/恢复授权不足；普通write/read锁仍可能双赢家；未执行可信登录/竞争|FAIL（D01/D05）；完整竞争动态 BLOCKED于通道|main:5061、3283、2869–2932；阶段笔记|
|硬3：逐写点恢复和关联一致性|核task/receipt/event顺序、pending恢复、脏历史失败行为；查盘|失败不制造假成功，可证明关联事实|D03/04仍缺；本轮未到业务提交点，权威业务文件未变|FAIL（源码）；提交故障动态 NOT_RUN；逐写点控制 BLOCKED于通道|main:843–853、3198–3379；A|
|硬4：未知结果原动作对账|独立原finalv1/needs_verify/pending/currentv6夹具；查盘|按原action核完整结果，不用最新版本代替事实|缺rid成功子项源码已改；needs_verify仍仅核version；本轮无授权恢复，夹具保持原样|FAIL（D04源码）；实际查询 NOT_RUN|main:3252–3258、3325–3364；H/unknown场景；A|
|硬5：重复/超时/重启/迁移|独立NDJSON、旧备份、坏回执、缺主文件、坏事件夹具；界面/磁盘核对|保留完整历史，明确失败禁写，重试身份稳定|迁移调用在load时尚未定义，实际未迁移；恢复/禁写源码残留；空白UI|FAIL（D01/D07）；连续同盘重启动态 BLOCKED于通道|cold/log:43–48；main:1033、1048；H/历史场景；A|
|D06/旧入口受影响回归|比上次sourceOk，核原命令入口|已修白名单不回退，旧写入口不可绕过|sourceOk函数体与上次完全一致；addEvidence/quarantine/togglePin原修复保留；外部旧入口未实际调用|原根因保留闭合；T24完整NOT_RUN|冻结源码/差异；上次r6报告|

### 原生证据逐项核对

全部 summary/result 结论、场景名称、wall_s/退出方式一致；均 quit_http 正常退出，12.18–12.90 秒，无 ABORT。profile 摘要、每张 capture 摘要及 seed 所有文件独立核对。6张最终PNG逐张目视；各 `.part.png` 与对应最终图同字节同摘要，因此视觉结论同时适用于全部12张PNG，不能把它们当12个独立业务步骤。

每场 `files_written_count=124`，124项清单路径均在该场新目录内，文件存在。主要为宿主资源/运行副本/缓存/news/截图及视图 state；**mtime 清单不证明业务提交**。正确事实目录为 `home/.octosense/apps/octosense-repair/`。任务、actions、events、测试账号和已有 bak 与 seed 全字节相同；state 的实际变化是 actor→null、selected_task_id→空、m6_last_loaded_ms新增。没有新增业务动作、迁移数组、bad_lines或恢复主文件。

|场景|实际盘面与图像|业务判定|
|---|---|---|
|cold_saved_actor_untrusted|空白；任务OPEN/v0、空回执/事件不变；持久actor清空|界面FAIL；未执行登录/权限矩阵，不能凭无业务变更证明拒绝正确|
|three_history_stale_backup|空白；三行NDJSON和一条旧bak不变，未转活跃数组|迁移核心未运行成功；不能称“旧bak不覆盖”已动态验证|
|mixed_bad_action_history|空白；有效→坏行→有效原文保留，无bad_lines输出|坏历史处理NOT_RUN；保留seed不是实际fail closed证据|
|missing_primary_ndjson_backup|空白；主actions仍缺失，两行NDJSON bak不变|实际恢复未成立；备份格式源码缺陷未闭合|
|corrupt_events_valid_backup|空白；坏主事件和旧合法bak均原样|没有发生实际覆盖/恢复；不虚报本轮已丢失坏源；源码风险保留|
|unknown_with_unrelated_newer_version|空白；current IN_PROGRESS/v6、原final/needs_verify/pending及后续事件不变|真实查询/恢复NOT_RUN；预装记录不是授权历史查询成功|

全文日志证实 launched hub client 1、439223字节 eval、remote listening/quit，无 panic；这些 marker 与 result 相符，但 eval 后 runtime 错误仍在。各日志 `[E]` 44条；`method ... not found on error` 25条，最早 :43–48 在 `[I]` 中明确 migrateJsonlLegacy 未定义。仅数 `[E]` 或 parser 错误会漏掉初始化失败。

全文 sandbox-denials 已读取并独立重算，统计与 result 相符：443 外联被拒，Metal缓存拒写，部分场景 /dev/dtracehelper 拒写；它们不是成功外联或成功项目外写入。profile仅允许场景目录写入和/dev/null，外联限本机控制口/Unix IPC，本轮无模型代理。所有 `needs_model=false`，model_proxy/model_proxy_stats 字段不存在，模型环境键不存在，实际模型请求 **0**，summary.billing_error均null。

result 还记录冷场景运行进程组中的 `osascript` 子进程；本审查没有自行调用 osascript/辅助功能/自动化，且最终该进程组全回收。该字段透明保留于A，不将“没有审查方自动化动作”写成“宿主绝无osascript子进程”。内核探针/清单没有证明任何成功逃逸。

G0-E：**延期缺口（Abram 已裁决，M3 到期）**。不用于本模块FAIL/BLOCKED，不请求新provider授权，不把零模型调用说成provider已通过。

### 相关既有用例逐条复核

|用例|结论|本轮精确范围|
|---|---|---|
|G0-B|FAIL|原生登录界面空白；查询/恢复项目授权源码残留。真实双主体登录动态未执行，受支持输入覆盖不足另列BLOCKED。|
|G0-C|FAIL|D03/04/05可靠执行源码未闭合；隔离CLEAN不替业务一致性。|
|T02|FAIL（源码）；动态NOT_RUN|创建内容代意图，同key未知可再创建；新来源同文本无法独立新建。|
|T04|FAIL（源码）；竞争动态BLOCKED|非原子锁有效交错双赢家；当前harness无同盘双可信竞争屏障。|
|T15|NOT_RUN|陈旧版本刷新、输入保留及错误提示没有执行；不是rc71/rc3阻塞。|
|T16|FAIL（源码）；动态NOT_RUN|稳定意图生命周期/unknown重试残留；完整原key响应丢失注入BLOCKED于通道。|
|T17|BLOCKED|schema没有受控断线/重连/响应丢失及连续同盘启动步骤。|
|T18|FAIL（源码）；动态BLOCKED|m2ReplayAtTop/恢复未逐task核权限；可信主体凭据输入与全部读面矩阵没有受支持通道。|
|T22|FAIL（源码）；动态NOT_RUN|pending与final/event关联恢复缺陷；精确写点故障控制BLOCKED于通道。|
|T24|NOT_RUN完整|D06原白名单修复保留；旧Web/MCP/runner实际禁用未调用。|
|T29|BLOCKED完整|宿主未验证可用凭据输入/grant/撤权/到期调度，不能用展示actor代替。|
|T32|NOT_RUN|配对码/poll_secret/Web绑定未执行；不将未测声称通过。|
|T37|FAIL（源码）；动态NOT_RUN|D04版本代事实、pending/unknown恢复不足；未执行授权原动作查询。|
|U03|FAIL|6张实际业务区空白，无角色事实动作界面。|
|U07|FAIL界面；完整恢复NOT_RUN|无真实输入/重试出口；同盘连续重启通道不覆盖。|
|U08|FAIL|错误/权限/待核验出口不可见；运行错误仅在host.log。|
|T28|FAIL|同版本本地安装及真实加载成立；真实业务操作/权威回读/重开主链不成立。|

## 缺陷与修复清单

仅复核上一轮编号及受影响回归。以下 P1 均直接影响登录、权限或可靠执行核心，不因建议项判FAIL。源码推导与本轮实际原生结果分开标明。

### D-M2-01 — P1 / 必修 / 未闭合：初始化失败和空白界面；查询权限不完整

- **文件行**：main:477–483、961/971、1014–1026、1033–1036、1048；:7450–7470、9248–9259；授权回归 :5061–5093、3463–3478、3283–3379。
- **触发/证据**：本请求任一场景新隔离目录加载；H/cold_saved_actor_untrusted/logs/host.log:43–60、77–80、258起及PNG，A。6/6实际空白。
- **实际/预期**：load()在迁移/表单初始化函数定义前执行，日志明确NotFound；loadViewState以旧偏好整体替换STATE，缺省字段未补齐；刷新/tick引用未建立的ui，持续报错。预期兼容旧视图状态、真正返回/挂载可交互根视图，再安全刷新。
- **根因/影响**：parser通过但执行顺序和UI绑定不成立，整个M2核心不能操作。此前保留名parser问题已有改善，不继续宣称旧50条parser错误。另 m2ReplayAtTop仅核身份、findReceiptByKey不核task权限；恢复扫描所有actor/project，移除项目角色但会话仍有效可读旧结果（**源码反例，动态未执行**）。
- **具体改法**：先集中初始化，确保调用时函数已定义；旧state仅加载允许偏好并补齐默认字段；按固定宿主支持方式建立返回根UI/控件引用，挂载后刷新，tick异常可见。replay和恢复逐task/command核当前项目权限，禁止会话身份活跃替代授权。
- **验证**：同候选harness冷启动无初始化/UI错误，登录/任务真实渲染；两个独立测试主体真实登录、退出与项目撤权，原结果/读写权限矩阵均实际核对。测试凭据不落盘到state/log/cache。

### D-M2-02 — P1 / 必修 / 未闭合：内容指纹仍代替确认意图，创建未知结果可重复执行

- **文件行**：main:4789–4828、4869–4889、5020–5044、5055–5129；确认结果消费 :4757。
- **触发**：同内容新报修；编辑同一确认后重试；创建已写task但final丢失/未知，再点确认；原task已到IN_PROGRESS后查原创建。
- **实际/预期**：键由actor+内容或fp选取；创建只查final，忽略pending/needs_verify，随后newId并再写新task。创建回放返回最新status，可能把原成功判失败。预期一次确认不可变、重试用原key，unknown先查询；独立新意图可同内容新建，原结果与当前task分开。
- **影响/证据**：直接违反T02/T16和一次执行目标。冻结源码与r5→r6差异；原生未操作，**本轮没有重复创建实测**。append即时持久化、部分状态前replay认可为改善，未整体闭合。
- **具体改法**：引入持久确认intent_id、不可变payload/key/phase；明确新确认与重试；创建统一进入边界并阻止unknown再建；原结果完整返回/UI呈现，当前状态另读。
- **验证**：正常重试、跨状态、同key异参、同payload新key、unknown重试、更高版本原创建逐条执行；同意图task/action/version/event不增，新独立意图可新建。

### D-M2-03 — P1 / 必修 / 未闭合：关联恢复未完成，脏历史写拒绝不能阻止假成功

- **文件行**：main:843–853、3198–3274、3289–3305、3347–3377、3441–3458、3518–3535。
- **触发**：task主写成功后final前中断；event写失败/历史脏；重启补事件。
- **实际/预期**：pending用version>expected标superseded，不能确定原action提交；saveEvents/saveReceipts脏时只return，任务/final仍可能返回成功；补齐统计未核真实event写。预期有关联动作日志和可证实完整事实，失败不显示成功。
- **根因/影响/证据**：多文件顺序写与恢复协议断裂，before/action_id字段不足以补齐主故障窗口。源码及阶段笔记；本轮坏历史没有执行到提交点，**无新原生部分提交实测**。新增before和event.action_id认可但P1未闭合。
- **具体改法**：统一before/after/action/receipt/event恢复记录；脏历史在整个命令边界fail closed；每次保存返回真实结果，独立核关联字段/唯一event后才成功；pending恢复不以版本大小替原动作事实。
- **验证**：harness精确逐写点失败/中断，查盘及UI，同盘重开收敛；原key不重复业务写，失败event不可只靠“recovered”计数放行。

### D-M2-04 — P1 / 必修 / 未闭合：version++仍能把未知动作误判成成功

- **文件行**：main:3252–3258、3283–3379、3421–3432、603–629。
- **触发**：needs_verify expected v0、另一动作把盘升到v1但after不符；pending原动作已提交；合法后续升到v6；pending_orphan重试。
- **实际/预期**：needs_verify仅凭expected+1标final_recovered，不核status/assignee/原action；pending标superseded；orphan在receiptFor仍unknown无继续出口。预期精确原动作证明及完整after，旧回执和最新状态分离，未提交可明确继续。
- **证据/影响**：冻结源码反例直接违反“不制造假成功”；H/unknown场景原记录和currentv6未变，**未执行登录恢复**，不把seed当恢复PASS。
- **已修子项**：缺rid不再committed=true；非final不再当hit；登录后触发恢复。仅源码子项认可，不关闭整体D04。
- **具体改法**：用关联action/提交标记/完整after核验，恢复所有未知状态但逐项授权；缺事实保持待核验；历史原结果完整返回，提供未提交继续和明确失败出口。
- **验证**：读回失败→同action完整结果，不增version/event；无关同版本不得final；v6仍可查询原v1；缺rid不成功，未提交原key可以按协议恢复。

### D-M2-05 — P1 / 必修 / 未闭合：普通文件锁无唯一赢家，创建绕过串行边界

- **文件行**：main:2869–2932、2937–3114、4785–4903。
- **触发/实际**：A/B同时读空；A写A读A获锁；B写B读B也获锁。同actor会话直接重入/可互释；创建直接pending+commitBound不获取锁。**为源码有效交错，不是本轮竞争实测**。
- **预期/影响**：真正同盘竞争只一个提交者，一承接者一成功event，创建不得覆盖别的写；当前会双提交/丢更新。
- **证据**：固定源码、差异、注释HOST_PRIMITIVE_BLOCKED；当前harness串行新目录不覆盖真竞争，不用CLEAN代签。
- **具体改法**：真实原子锁/CAS或唯一可信写者，session唯一owner和异常清理；包括创建在内所有写统一经过该边界。
- **验证**：两个独立可信上下文同事实盘同步竞争与同actor独立会话竞争，只有一个获执行权；异常不误释别人锁，创建/普通命令竞争不丢更新。

### D-M2-06 — 原白名单根因继续闭合；完整回归未运行

sourceOk:770与上一轮实际受审函数体相同，addEvidence/quarantineEvidence/togglePin已修准入保留。无需重新修白名单。不据此认定旧Web/MCP/runner真实禁用或当前原生按钮已运行；T24完整NOT_RUN。

### D-M2-07 — P1 / 必修 / 未闭合：迁移未执行，备份格式与恢复协议不一致

- **文件行**：main:961–984、1033、1048–1168、843–844。
- **触发**：缺主actions且bak为真实两行NDJSON；坏事件主文件+旧合法数组bak；有效历史中夹坏行。
- **实际/预期**：原生log:43–48证实迁移函数在load时尚未定义，全部历史未迁移。源码备份写原NDJSON，缺主恢复却只接受整体数组；完全坏主可被bak覆盖且未保存坏源；单文件冻结不能保证业务整体禁写。预期同格式可完整恢复、保留损坏原文、错误不变空可写。
- **影响/证据**：恢复可能丢原历史或隐去损坏依据，阻断可靠恢复。H/三历史场景及A；当前原文不变，**不宣称本轮已经覆盖丢失数据**。主有合法行优先主及DIRTY保存守卫是改善。
- **具体改法**：先修调用顺序；主/bak共同支持数组与NDJSON并保留完整字节；损坏源先备份，失败整体冻结且显示恢复路径；读回核全记录，不只长度。
- **验证**：独立三行/旧bak、两行NDJSON缺主、混坏行、全坏主+合法bak复跑；全字段历史保留、损坏源存在、错误不能写业务；同盘重开恢复可查询。

### 建议挂账（不据此单独判FAIL）

- 补 `M2_IMPLEMENTATION_r6.md`、候选清单及作者候选字段；当前审查定位已足够，不为材料过时单独设P1。
- 在驱动中补受控凭据输入、真正同盘屏障、逐写点/响应丢失及连续同盘重启能力；本审查不擅自改驱动或业务增加测试后门。它们是具体动态检查通道缺口，不是rc71/rc3问题，也不是NEEDS_ABRAM。
- 不因字体/视觉完善等建议降低核心修复优先级。先让同字节候选登录/任务真实渲染，再按原编号闭合核心。

## 判定与门禁

- **最终结论：FAIL**，精确适用于上述 M2-r6-worktree 内容摘要和固定发行宿主。本地安装加载/证据一致/隔离回收通过；可信身份与可靠执行核心未通过。
- 必修：D-M2-01/02/03/04/05/07；先D01实际界面与初始化，再统一动作/恢复/权限/竞争，不扩做下一模块。
- BLOCKED只用于明确白名单/harness无法覆盖的完整检查：受支持凭据输入、任意原key/payload、真正同盘竞争、逐写点故障、响应丢失/断线和连续同盘重启。实际空白UI为FAIL；没跑到业务路径为NOT_RUN。没有ABORT，不用Codex沙箱rc71/rc3解释。
- 门禁仅更新 `GATES.json` 的M2 status及review字段：review_report指本报告，review_candidate_id指r6，旧M2审查字段/旧status归档review_history。作者candidate/base/implementation及其他模块不改；既有验收台账不覆盖，在本报告和M2.review_acceptance记录本次17项范围并保留历史。
- **不允许下一模块，不执行下一模块。** 构建方按原编号修复并交接新同字节候选；驱动补受支持控制后独立重审。
- NEEDS_ABRAM=no：身份/provider与隔离签名已授权，本地路径已验证；无余额/欠费或必须公开发布条件。剩余技术修复和测试通道问题不要求Abram新授权。

STATUS=FAIL
NEEDS_ABRAM=no
