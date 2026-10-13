# M7 独立 Review r3

- 最终结论：**BLOCKED**。`M7-r3-worktree` 的 B-M7-01 未闭合；缺少符合项目内隔离要求的同候选原生业务与 UI 实证。不以建议项或前序 FAIL 单独拒收。
- 审查者 / 日期：本主会话唯一审查方，2026-10-11T10:48:55+08:00；无子代理。实际主模型 Astra；无法核验 Router 路由/切换到 gpt-6.1-sol，不声称已切换。置信度：字节、当前驱动及命令结果 **高**；模拟控制流 **中**；实际原生 UI/业务/模型 **未知**。
- candidate_id：`M7-r3-worktree`；base：`M7-r2-worktree`。由 GATES.candidate_id、implementation_report 与 r3/CANDIDATE.json 相互定位，未依据文件时间选择。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r3.md`。本报告编号取下一个 Review 编号 r3。
- HEAD / 分支：`8d730569546cb57310944bb299695134df773b9d` / `main`，dirty。候选包沿用 `runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/`，版本 0.1.0-c，bundle BLAKE3 `a7451d34d7aa808bc534df0350b5e501cc5fc83a9861f296e9ea4574c9b2ea10`。
- 源码定位：冻结主源 SHA-256 `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6` / 283933 字节；当前工作区主源 `1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2` / 369061 字节（M6 r4）。作者所写当前工作区 `5c12041e…` 是旧快照，不能解释今天的工作区。审查此已明确冻结的旧包，不自行改包吸收后续变更，也不把 M2–M6 r4 证据嫁接给它。
- 前置：M6 当前 `M6-r4-worktree` / `M6_REVIEW_r4.md` = FAIL，无独立接受的 PASS 候选。按本轮用户明确挂账裁决继续限定 M7 复审；保留前置缺口，不修前序、不改前序结论。
- 宿主：指定提取包 `M0/r3/host/app-extracted/OctoSense.app`；octosense SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，223391280 字节；kernel SHA-256 `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`，126117168 字节。本轮重新计算，均与 r2 宿主快照一致。
- 阅读范围：实际 AGENTS、现有 CONTEXT_M7、M7 模块和04模板、r2 Review、r3实施/候选/驱动/5次作者运行记录/发布材料，02规则及00/01相关门禁段；基线要点沿 CONTEXT。遵守修复轮要求，没有无关业务扩审。原64定义与当前 ACCEPTANCE.title 64/64相同，额外 L8-DV2 保留未改。
- 已独立执行：逐文件大小/SHA及历史快照比较；当前宿主哈希；项目内环境下 sandbox/进程预检与 hub check；对现存驱动做内存 mock 失败注入（没有启动宿主、没有写日志或覆盖作者证据）。
- 未执行：实际 launcher、中文输入/滚动/角色业务、正常/退回/重复/失败/业务重启、真实模型及同版本截图/演示。隔离施加和进程枚举失败，必须 BLOCKED/NOT_RUN。作者静态25/25、27/27本轮未重跑；它们不替代原64。
- 私钥：本轮未生成/读取任何私钥；仅枚举 r2/catalog 及 review-r2 下 `*.key` 文件名，结果均为空。r2删除记录按历史保留，不谎称本轮执行过删除。未读取 `CREDENTIALS_FOR_ABRAM.md` 或 provider 密钥，真实模型请求 **0**。
- 写入范围：只新增本 Review 报告及 GATES 的 M7审查字段/审查历史；候选、业务文件、运行证据和 ACCEPTANCE 不修改。上级要求的启动记忆查询有项目外只读访问，不属于宿主测试；其后项目审查限定项目内，未产生项目外写入。工具未提供自身 createdAt/改标题能力，本轮也仅获报告/门禁写授权，不声称实际改名。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|D-M7-01 准入回归|对精确最终目录运行本地 Hub check|rc0且当前包合规|rc0 PASSED，unsigned warning，仅storage/16MiB/agent none|CLOSED，准入子项 PASS|下方命令记录；manifest|
|D-M7-02 冻结回归|解析INTEGRITY表，16行逐文件比较；包与r2独立end-audit比较|包及材料指纹一致|12包全部正确且未变；INTAKE/LICENSE正确；两材料及自哈希失配|包核心子项保持；材料回归挂A03|INTEGRITY.txt:42–47；下方精确哈希|
|D-M7-03 编号回归|将原64逐一与当前ACCEPTANCE标题比较|含义保留且未测不变PASS|64/64一致；本轮逐项真实状态见表|CLOSED（定义/口径子项）|ACCEPTANCE、review-r2/acceptance-matrix、下表|
|B-M7-01 环境|先施加项目内写隔离，再枚举目标进程|隔离成功且清理可验证|sandbox_apply rc71；pgrep rc3；不启动|BLOCKED|命令记录|
|B-M7-01 驱动/同版本|读实际Popen命令、路径与作者日志；mock早退/异常|目标bundle安装/加载可证，失败不成功，必定清理|现存命令带sandbox；未传bundle/app-data；进程101仍main rc0；启动后异常未清理|OPEN，P1核心/隔离安全缺口|driver:61–84、86–119、144–154；mock记录|
|硬1 全必需门槛|逐项核64的证据适用性|同候选原生业务及UI实证|无本候选实操；旧未测未升级|BLOCKED|64表；B01|
|硬2 正常/退回/失败/重启/模型|核3/3作者日志是否证明业务加载/权威结果|同包目标宿主可回读业务|3次app-data大小全0；无动作/回执；包模型OFFLINE|BLOCKED；模型NOT_RUN|probe1/2/3/run.json；model_config|
|硬3 同版本材料|核源码/包/截图/模型/材料|对应同一冻结候选|包稳定；截图仍历史；工作区已MiniMax/新主源；包仍旧字节；材料摘要失配|BLOCKED；包摘要子项PASS|清单、哈希、A03|
|硬4 准入/安装/干净运行|check新跑；核同digest历史install_staged及私钥删除|本地安装与实际干净运行分别成立|check新PASS；包12/12未变，历史Store PASS可沿用；本轮安装/干净运行未跑|BLOCKED；本地catalog路线有效|review-r2/local-store-validation.json；命令记录|
|硬5 状态分离|核本候选外部回执及本地结论|分别记录、不冒称|本地BLOCKED；发布/赛事/商店皆NOT_RUN|PASS（状态区分）|判定表；清单、listing|

## 本轮独立命令与反例

实际CLI运行 cwd=`runtime/optimization/2026-10-09/M7/r3/sandbox/`。HOME/CFFIXED_USER_HOME/TMPDIR/XDG缓存/配置/数据/OCTOSENSE_HOME/Metal缓存均指向此目录；不启动launcher，不传`--help`，不联网。以下输出直接存于本报告，未新建运行证据文件。

1. `/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny file-write*)(allow file-write* (subpath "/Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09"))(deny network*)' /usr/bin/true`：rc **71**，stderr `sandbox-exec: sandbox_apply: Operation not permitted`。
2. `/usr/bin/pgrep -fl OctoSense.app/Contents/MacOS/octosense`：rc **3**，stderr `sysmon request failed with error: sysmond service not found` 与 `pgrep: Cannot get process list`。桌面已有窗口状态 UNKNOWN；本轮未创建窗口，也未盲杀他人进程。
3. `runtime/native-build/OctoSense-App-Hub/target/release/hub check <精确上述冻结包绝对路径> --allow-unsigned`：rc **0**，stdout `octosense-repair 0.1.0-c — PASSED`；warning unsigned；grants storage、hosts为空、storage 16777216、agent none。
4. 内存mock：从现存driver AST只抽出函数，Path.mkdir/write_text、open、Popen/run、sleep、killpg均模拟；未import其顶层mkdir、未产生真实进程或文件写入。模拟proc.returncode=101、pre/post pgrep=1，`main()`仍返回 **0**。模拟Popen成功后sleep抛 `INJECTED_AFTER_SPAWN`，异常外逸，killpg调用 **0** 次、终态record **0** 条。这是驱动控制流反例，不是原生运行证据。
5. 记录得到的真实spawn命令：`sandbox-exec -f <r3/scripts/launcher.sb> <指定launcher>`，没有bundle、app-data参数；driver SHA-256 `b7aa39f1efa700db0b04e48cbaba38c808ee44b92d42d0bfd7b9450535fc64b4`。

首次原64对照脚本遇到额外 `L8-DV2` KeyError，随后限定本模块明确64编号重跑，64/64定义一致；该附加项未删除。没有把失败的初次命令记PASS。

## 缺陷及上一轮闭合状态

### B-M7-01 — OPEN / 核心 BLOCKED，驱动安全子项 P1 必修

- 文件与行：`r3/scripts/m7_launcher_probe.py:61–84`、`:86–119`、`:144–154`；`r3/scripts/launcher.sb:12–15`；`M7_IMPLEMENTATION_r3.md:14`、`:26–28`；`r3/launch-logs/SUMMARY.md:32`。
- 触发：按README当前测试命令复跑；或在子进程启动后引入异常/使子进程提前以101退出。实际驱动未证明bundle安装/加载，只将bundle路径写进最终record；app_data用于cwd/环境，未传给宿主，也没有登记本候选的Store状态。三次作者记录中 app_data_root_size 均0，记录无实际动作回执。不能据此断言加载失败，但也不能断言已加载了此候选。
- 实际/预期：现存driver套sandbox，与作者直接启动3/3记录不对应；只用post_pgrep=1判成功，进程101也返回0。Popen后无finally，异常可能跳过进程清理。profile还允许项目外 `Library/Caches/TemporaryItems` 写入，并允许整个工程写入而非隔离测试目录。作者承认直接启动会写真实 `~/.octosense`，这不是获批的例外；“非用户数据”不能消除写越界。严格profile的Metal panic只证明该次配置失败，未证明所有项目内路径均不可行。
- 根因：测试驱动缺少实际候选绑定、启动成功断言和全路径清理；环境/缓存隔离只靠环境变量，profile与用户硬边界不一致；运行记录未冻结生成它的驱动版本。
- 影响：M7可复现同版本桌面候选核心未成立；可能误报启动成功/异常遗留进程/写项目外。当前工具环境隔离和枚举本身也受阻。
- 具体改法：保留指定launcher，本地catalog/install_staged路线不变；先明确并实证安装到隔离Store并被launcher实际加载的目标digest。所有宿主数据/缓存/日志仅在 `runtime/optimization/2026-10-09/` 新隔离根，删除项目外写allow；不得用直接非隔离启动绕开要求。Popen及其后全部路径包在finally，优雅退出→TERM/KILL自己PGID→wait，pgrep三态，异常/非零退出必失败；记录实际cmd、env非秘密路径、driver/profile SHA及digest。
- 验证方式：在可施加同样写隔离且可枚举进程/窗口的环境先预检，失败不启动；做启动早退/异常/清理失败注入，核不误PASS且不会遗留。再从干净合成数据实操同候选正常/退回/重复/失败/重启、保存权威结果及当前截图；测完立即关闭并核本轮窗口归零。前序只修确实阻断本模块核心者，不拉回所有挂账。
- 是否需Abram：**no**。身份来源、MiniMax与隔离离线签名已授权；本地catalog路线有相同digest独立历史实证。无402/欠费，未要求公开发布。当前环境不足与代码修复不是新授权项。

### A-M7-01 — PARTIAL / P2 建议挂账

- 文件行：`app/README.md:48–63`、`:65–99`、`:103–119`；`CONTEXT_M7.md:45–51`。
- 实际：旧card-host段已降历史，后台启动禁令已删除；但当前段称“所有写入”均隔离，与作者自述真实HOME写冲突。旧/tmp端到端脚本仍在，外层从:38开始的代码块未在:65标题前关闭，导致当前入口渲染混乱。
- 根因/影响：文档替换不完整；复制命令误导。没有执行这些旧命令，不据此判FAIL。
- 改法/验证：当前段明确未通过隔离预检，不宣称可安全复现；旧/tmp链整体标历史不可用于本轮，修代码围栏；逐个检查可执行输出路径，渲染回读。

### A-M7-02 — 原问题 CLOSED；来源完整性 P2 挂账

- 文件行：`release-materials/SOURCES.md:8–19`、`:29–30`、`:43–45`；`PRIVACY.md:8`。
- 触发/实际：不存在的脚本名已删除；固定commit写未知；旁白/配乐不再断言本候选原创，原修复成立。仍有未核媒体渠道描述，以及“3/3解阻”沿旧记录。
- 预期/根因/影响：只陈述可核媒体/宿主来源，不把二进制hash等同可复构源码；剩余为文稿复制/来源不完整，未公开，仅建议。
- 改法/验证：删除无法定位的渠道说法；保留发行标识/二进制SHA/未知源码标记；以现有媒体路径及本候选实际记录回读，无需新做媒体。

### A-M7-03 — PARTIAL / P2 建议；D-M7-02材料子项发生回归

- 文件行：`release-materials/INTEGRITY.txt:42–47`；`r3/evidence/integrity-hash-after-stamp.txt:3–4`；`M7_IMPLEMENTATION_r3.md:35–40`。
- 触发：对表中16文件及另存摘要重新计算size/SHA；与作者“已闭合”比较。
- 实际/预期：计数12+5=17、16项排除自身已修；但PRIVACY实际 **1290字节** / SHA `0544948ac4256c97bda55ea8000ea19a1fba1cd0c2eb3b4218bb51a8c82cbb3c`，表仍1069/旧hash；SOURCES实际 **3641字节** / SHA `070f4e6e806efd714116b0d15d8d4b9af3d893211d674d0462bfb1f4180a4a9e`，表仍2927/旧hash。INTEGRITY实际 **2670字节** / SHA `0ab8eab50d28be1f99178eec5348430ff0b3dcc52f52384dd189219c61bd706e`，另存文件仍2709/`77a752af…`，并在自身末行写自身摘要造成不可成立的自指纹。
- 根因：编辑材料后未重新冻结，且把自排除指纹又写回待摘要文件。当前worktree已新主源/MiniMax，但报告仍称旧worktree字节；新候选来源范围需明确。
- 影响：材料校验无法通过，不称全部指纹一致。包内12/12仍匹配上一轮，核心准入/安装并未因此作废。按“完成比完美”裁决作为建议挂账，不用此项单独判FAIL。
- 改法/验证：定稿材料后重算4材料指纹；INTEGRITY内部只说明自身排除，不放自身hash；最终对它计算一次摘要写到包外另存文件，不再改它。报告明确冻结旧源码快照与今天工作区不同。逐个比对16项及外存摘要全部正确，冻结起止无变。

## 相关既有用例逐项复核

原始定义逐项保留；以下状态仅适用于本候选、本轮独立范围。T/U未实际运行的原因如实记录，不以历史PASS、静态总数、旧B图或作者3/3代替。没有改变原ACCEPTANCE及L8-DV2历史。

|编号|权威定义|本轮|证据及实际范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|BLOCKED|hub check rc0、12/12 包字节与上一轮独立快照相同；实际原生启动 BLOCKED。|
|G0-B|真实可信身份、授权与独立会话|BLOCKED|账号来源已经裁决，非授权缺口；冻结包仍旧演示身份。独立会话/每次读写权限未运行；不访问真实账号或凭据。|
|G0-C|唯一事实源、原子一致性、并发与恢复|BLOCKED|本地 Store 安装恢复历史子项保留；业务事务/并发/崩溃恢复未运行。|
|G0-D|真实附件写入、回读、归属及失败恢复|BLOCKED|未执行真实附件写入、权威回读、归属及失败恢复；离线签名不替代附件。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|BLOCKED|提醒恢复/去重/官方意图视图未运行；不称后台常驻。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|BLOCKED|包字节未变，旧静态入口子项保留；边界绕过/网络关闭/完整本地验收未实操。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|BLOCKED|包字节未变，旧静态入口子项保留；边界绕过/网络关闭/完整本地验收未实操。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|BLOCKED|相同 digest 的上一轮官方 install_staged/may_run 子项保留；本轮未重新安装或操作任务/回读/重开。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|BLOCKED|B-M7-01：未安全启动本候选；原生实操、权威结果与恢复无本轮证据。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|冻结包仍 enabled=false / provider_id 空；实际模型请求 0。工作区 MiniMax 配置已授权且不同于此包，不能移植证据。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U06|进度、完工、验收不同；退回后历史与附件保留|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|BLOCKED|六张截图均逐字节沿用 r2/B 历史；当前桌面 UI 未运行，旧图不证明当前包。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|无本候选 2–3 分钟演示及独立复述；未运行。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|BLOCKED|正常链、退回重做链、失败/重复/业务重启未运行；不能以启动器进程存在证明。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|BLOCKED|同 digest 的官方本地 catalog/install_staged 历史 PASS 子项仍适用；目标宿主能力/UI整体 BLOCKED。|
|P03|最终包准入check及实际scan审阅通过|PASS|本轮对精确最终目录独立运行 hub check --allow-unsigned：rc0 PASSED；只覆盖准入，不证明正式 scan 审阅或运行。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|BLOCKED|本候选截图/演示无实证，旧媒体已披露；不能判同版本材料 PASS。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|BLOCKED|包 12/12 摘要一致；两项包外材料摘要及自哈希失配 A-M7-03；核心 B01 仍 BLOCKED。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|本候选无实际对应回执，本轮禁止外部动作；历史 0.1.0-b 不升级为新候选完成。|
|P07|维护者商店收录结果|NOT_RUN|本候选无实际对应回执，本轮禁止外部动作；历史 0.1.0-b 不升级为新候选完成。|
|P08|赛事正式提交入口回执|NOT_RUN|本候选无实际对应回执，本轮禁止外部动作；历史 0.1.0-b 不升级为新候选完成。|

## 判定

|对象|结论|精确范围|
|---|---|---|
|M7本地发布准备|**BLOCKED**|B-M7-01仍未闭合；仅准入/冻结包字节及相同digest本地安装子项有证据|
|外部发布/Hub递交|**NOT_RUN**|本候选无对应回执；未执行，不借历史Issue证明新候选|
|赛事正式提交|**NOT_RUN**|本候选无赛事回执|
|维护者商店收录|**NOT_RUN**|本候选无收录回执；本地catalog不是收录|

- 必修：B-M7-01中候选绑定、隔离、退出/清理真实性；环境恢复后取得真实核心链与权威回读。A01/A02/A03仅建议挂账；不因为建议项FAIL。
- 前序回归：确认今天M6 r4与冻结包不同；不改变M0–M6结论，不把新工作区成功假设给旧包。受影响同digest准入已新跑，r2本地Store/篡改/恢复证据因包12/12未变可保留为历史有效子项；本轮未重新签名/安装/冷重建/正式scan。旧已关闭D01/D03保持，D02包字节子项保持，材料回归归A03。
- 门禁：只更新M7 status/review_report/reviewed_at/review_candidate_id及review_*与审查历史；作者实施字段、其他模块、external_delivery及原台账不改。
- 是否允许下一模块：**否**。不给下一模块入口，不执行发布。解阻只需满足已有授权的项目内隔离运行条件与本模块核心实证；不要公开publish、换provider或申请已关闭身份授权。

## 审查快照

本轮git diff（二进制格式，包含既有未提交内容）的SHA-256：`63dbdb1f9063c8761fcc42014f20ddbd214318f5362dc4cec355c3b076bd2b9b`。这只是本轮定位，不是源码提交；既有状态如下。完整本轮内容清单保存在本报告，避免另写runtime文件。

```text
 M PROGRESS.md
 M README.md
 M app/README.md
 M app/bundle/main.splash
 M app/bundle/manifest.json
 M docs/VERIFICATION.md
 M docs/build-loop/ACCEPTANCE.json
 M docs/implementation/10_UI_UX_SPEC.md
 M submission/2026-10-06-native/CURRENT_REVIEW_STATUS.md
 M submission/2026-10-06-native/HUB_ISSUE.md
?? app/bundle/.archive/
?? app/bundle/data-test/
?? app/bundle/host.log
?? app/bundle/identities.json
?? app/bundle/instance.json
?? app/bundle/main.splash.debug.bak
?? app/bundle/main.splash.v1.bak
?? app/bundle/model_config.json
?? design-references/2026-10-08-desktop-v2/
?? docs/optimization/
?? scripts/identity_auth.splash
?? scripts/identity_crypto.splash
?? scripts/manage_identity.py
?? scripts/test_identity.py
?? submission/2026-10-08-hub/
```

```json
{
  "app/bundle/main.splash": {
    "bytes": 369061,
    "sha256": "1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2"
  },
  "app/bundle/model_config.json": {
    "bytes": 1460,
    "sha256": "55b41c8016c347ec0ba7a8b5e0942058eeef05a6f3c3f38b724a73bd183e0630"
  },
  "app/README.md": {
    "bytes": 10160,
    "sha256": "2a566ff7c1a41da71c3d9936867930ad4ee2b39b9f6c071165efb6e5fd202517"
  },
  "runtime/optimization/2026-10-09/M7/r3/CANDIDATE.json": {
    "bytes": 3066,
    "sha256": "04a0370678bba84c02483d8ca998cfe41365b5053f2437f122c056970f214fed"
  },
  "runtime/optimization/2026-10-09/M7/r3/scripts/m7_launcher_probe.py": {
    "bytes": 5616,
    "sha256": "b7aa39f1efa700db0b04e48cbaba38c808ee44b92d42d0bfd7b9450535fc64b4"
  },
  "runtime/optimization/2026-10-09/M7/r3/scripts/launcher.sb": {
    "bytes": 700,
    "sha256": "7bfe2f8063dc5a89478a38dd80b7f7997dd2d11b1c94851bb537a845bb02d78b"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/assets/icon.svg": {
    "bytes": 371,
    "sha256": "48b598636650b91e23357e2f4a926025ab1c5e77032382c764bcc75c64076eb0"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/identities.json": {
    "bytes": 1597,
    "sha256": "ed00dcbcd7c8849838f7bc4b6de86b48669ca841af75c787f4b10ac171fc69b2"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/listing.json": {
    "bytes": 3426,
    "sha256": "1938eda9d538fcf0a2adc99fecd7a575f04450409bc470aabf528431e2b485d9"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/main.splash": {
    "bytes": 283933,
    "sha256": "ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/manifest.json": {
    "bytes": 249,
    "sha256": "7512238ec5a2cacddc48002f1e8b15049c0db01c1a5ecbbed1b99cc6f1b666dc"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/model_config.json": {
    "bytes": 1240,
    "sha256": "b36ca0561b89cf05de37f49eb5cbb2dc46ef9c9cc1879feee7bfff586de52741"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b01-initial.png": {
    "bytes": 188667,
    "sha256": "749c9e7dd84a90092c0080cfec51f749dcaf3cd3521acfa7abd53bf3f89bf440"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b02-draft-created.png": {
    "bytes": 212642,
    "sha256": "f0d11c03daa8f011ab2045ce54a2d0ecc16181ccc7c60e2e8d96d64b1a872de3"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b03-submit-open.png": {
    "bytes": 208293,
    "sha256": "9961a4a97623da6dd1be5102611aaa822982c3f838e98e7914e24fd260e8d322"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b04-schedule-confirmed.png": {
    "bytes": 208836,
    "sha256": "16c10ffc0d01afcfd52dda890da4309ad19d04923b74779fc601484688e31728"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b05-completed.png": {
    "bytes": 207682,
    "sha256": "0c0a798963eac8d3954c131e0b87d64c5bf39b9da2dce57908c90cce85d14217"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/screenshots/b06-after-restart.png": {
    "bytes": 207062,
    "sha256": "c5ad6c37e6c884d45be7d146d66480a629e4fe90bfc8c5164770a7cda1ad97b7"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/release-materials/INTAKE.md": {
    "bytes": 691,
    "sha256": "8ea7c9b7421c1479e6921bfbd4e51abf0f50e94fa9ed9ff15b5845f48b8fc91b"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/release-materials/INTEGRITY.txt": {
    "bytes": 2670,
    "sha256": "0ab8eab50d28be1f99178eec5348430ff0b3dcc52f52384dd189219c61bd706e"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/release-materials/LICENSE.txt": {
    "bytes": 1107,
    "sha256": "4285bd4c48ce4e9fbdfd4d0072ed5e54318a98deaa21b832b0e952ce57a448d0"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/release-materials/PRIVACY.md": {
    "bytes": 1290,
    "sha256": "0544948ac4256c97bda55ea8000ea19a1fba1cd0c2eb3b4218bb51a8c82cbb3c"
  },
  "runtime/optimization/2026-10-09/M7/r2/release/release-materials/SOURCES.md": {
    "bytes": 3641,
    "sha256": "070f4e6e806efd714116b0d15d8d4b9af3d893211d674d0462bfb1f4180a4a9e"
  }
}
```

审查起止：报告写入前再次确认上述候选/材料/工作区/驱动SHA完全一致；写入后回读核验另记本轮报告验证。未覆写任何原始运行证据。

STATUS=BLOCKED
NEEDS_ABRAM=no
