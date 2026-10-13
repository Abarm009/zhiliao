# M1 独立 Review r1

- 最终结论：**FAIL**。候选：`M1-r1-worktree`；基线：`M0-r10-worktree`。仅三项 P1 必修，其余建议挂账。置信度：高（字节核对、官方 Store 正负测试、源码索引分析和驱动异常注入）；本轮原生交互结果：BLOCKED。
- 审查者 / 日期：Codex 主会话，唯一审查方；2026-10-10，Asia/Shanghai。未委派代理。环境没有可确认/切换主会话为 gpt-6.1-sol 或 Router 的接口，未声称已切换。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作树非干净。作者报告：`reports/M1_IMPLEMENTATION_r1.md`。无既往 M1 Review，本轮首审。
- 候选确定依据：GATES 的 candidate_id、implementation_report、实施报告内相同 candidate_id，以及 staging/catalog/安装目录内容交叉匹配；没有按文件时间挑版本。
- 前置：M0 独立 Review r10 仍为 FAIL，**没有已接受的 M0 PASS 候选**。按本次 Abram 前序挂账裁决继续审 M1，不把 M0 的表单缺陷搬入本轮必修；其清理缺陷在 M1 自己的测试驱动中再次出现，直接涉及本轮安全，故列 D-M1-02。未改写 M0 门禁。
- 已读：AGENTS、M1/CONTEXT_M1、00/01/02、M1 模块要求、04 Review 模板、M1 实施与原始证据、M0 Review r10 与基线源码、desktop v2 DESIGN_SPEC、T18/T28 和相关 U 用例原文，以及根文档入口。CONTEXT 中“复用 M0 catalog/不重签”等旧说明与实施报告不一致，以现场候选为准。
- 本轮证据目录：`runtime/optimization/2026-10-09/M1/review-r1/`；表格中 results 路径均相对此目录。原作者证据 `r1/` 只读取，不覆盖。

## 候选、宿主及审查边界

|对象|现场核对结果|
|---|---|
|工作树 / staging / artifact / 已安装 main.splash|均为 85859 B，SHA-256 `ab0fbd5e476a647cff6f27de3ce1caa7485f5ade159e377b8471b02d4dd908a0`|
|本轮签名 staging manifest|id `octosense-repair-m1r1`，version `0.1.0-m1r1`，manifest SHA `6629be1e5ed4a62cffc07b59bb9934c0895c97fdca63c24c7cea99831abd516e`|
|候选 bundle digest|`598c6dcfcda3fb682fefa45569e1cd5b8bb975d03f7ce4c5e9e43c7c2ab26e3e`；官方 Store 独立安装实际输出一致|
|catalog|sequence 1，SHA `e084f04fc95c96f99e49b9772cbb0a3d2c45346c07bc46c305f0e3570d26280d`|
|工作树 manifest|仍为原 `octosense-repair / 0.1.0-b`，249 B，SHA `e20251934523392768a4aa459297366e999470d0b71685c46c710bbb5d101031`；不能把它当作本轮已签名 manifest|
|M0 基线差异|对实际 r10 staging main 生成 `results/M0-to-M1-main.diff`；17 个既有业务命令函数体均保持一致，createDraft 仅新增 selected_task_id 同步赋值；UI 段确有重排，未见整份业务函数被覆盖|
|launcher|指定 M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense；223391280 B，SHA `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`|
|kernel|126117168 B，SHA `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`|
|冻结|开始/结束 238 个候选与业务输入文件 SHA 全部不变；`results/start-snapshot.json`、`end-verification.json`|

本轮真实执行：官方本地 Store 安装/重开准入、篡改拒绝与恢复重试；隔离预检；驱动原函数 AST 的 mock 异常注入。源码索引轨迹为 Python 逻辑复算，**不是原 OctoScript 或原生操作**。本轮目视检查的是作者原生截图，**没有本轮截图或亲自点击通过记录**。

本轮 HOME、CFFIXED_USER_HOME、TMPDIR、XDG cache/config/data、OctoSense home/app-data 和 Metal cache 均指向 review-r1；宿主必须使用仅允许该隔离目录写入的 profile。true 与 echo 均 rc71：`sandbox-exec: sandbox_apply: Operation not permitted`。pgrep rc3：`Cannot get process list`。因此没有启动 launcher，没有使用 --help，没有新增窗口，也没有全局杀掉他人进程。既有残留窗口/进程状态 UNKNOWN，不能声称桌面已无残留。具体记录见 `results/preflight.json`。

本轮无联网、上传、publish、listing、push、部署、provider 配置或消息发送；复用候选现有签链，没有生成私钥。现场 r1/keys 为空；作者 results 的 keys_deleted 含 anchor.json/publisher.json/anchor.cert.txt。本轮独立确认“当前无私钥”，不把作者删除记录冒充本轮执行删除。

边界偏差：首轮工具调用误读了项目外的 memory registry 做定位，随后停止；未将记忆作为本轮判断证据，所有审查产物与测试副本均在项目内。此偏差不能写成“整个会话绝无项目外读取”。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/证据一致|复算文件 SHA、核对原始 results 与各安装副本|审查对象可唯一定位|main/签名 manifest/catalog/宿主一致；工作树 manifest 与签名包不同，显式区分|PASS（定位）|candidate-audit.json、start-snapshot.json|
|本地 catalog 安装路线|将 catalog/artifact 复制到 review-r1/store-test；运行固定 r10_install_probe|install_staged、Store 重开 may_run 成功|rc0，实际 digest 相同，caps storage、hosts 空、agent false|PASS（Store 层）|local-store-validation.json；M0/r10/install_probe/src/main.rs:70–102|
|安装失败恢复|仅改测试副本 main 注释，再恢复原字节重试|篡改拒绝，恢复成功|rc1 digest mismatch；恢复 rc0|PASS（安装层）|local-store-validation.json|
|亲自操作原生窗口|先做安全启动预检和进程清点|隔离可用，后台启动、操作后回收并核验残留|预检 rc71、清点 rc3；未启动|BLOCKED|preflight.json|
|搜索/选中/导航/滚动|查实际入口、源函数，目视原图并核对日志|列表动态更新、选中可用、导航对应筛选结果|搜索为无输入/无回调按钮；列表原图仍“初始化”；set_visible 报错；筛选导航存在错误索引|FAIL（D-M1-01/03）；真实点击/滚动 BLOCKED|main:1581–1606,2042–2054；日志465/466；selection-source-traces.json|
|键盘/焦点/输入保留|核对控件、STATE 写入路径与原 U 用例|真实中文编辑、焦点、Esc/导航保留|无 TextInput/输入事件，pending_input/panel 仅初始占位；本轮无法操作|NOT_RUN；缺口挂账|main:52–55,1581–1585；建议 A-M1-01|
|desktop v2 与既有修改|对 r10 基线作 diff，检查头部/侧栏/详情/行动区与17命令|框架接纳既有规则，不制造第二事实库|保留业务函数；新增列表/页签；实际详情动态内容与行动区未获得有效操作证据|PARTIAL；核心 FAIL|M0-to-M1-main.diff、candidate-audit.json、D-M1-01|
|UI/命令边界|对比动作回调与旧命令；核查权威文件|界面不直接把最终业务状态改成成功|主/次动作调用 runAction→原命令；未见新 UI 最终状态绕过；仍用旧 currentTask 下标，稳定ID桥接有风险|PASS（新增源码边界子项）；运行 NOT_RUN|main:372–375,979–996,1662–1705；17函数比较；A-M1-03|
|实际命令/权威回读/重开|读取作者各运行 side_effects 和实际 home 文件；独立宿主烟测受预检约束|真实 task_id、回执和状态一致，重开仍一致|三轮均没有 tasks/actions/events，只有空选中 state；没有核心任务操作/恢复证据|NOT_RUN（完整）|r1/results/install-and-host-m1r1.json；D-M1-01|
|跨项目/迟到回包|查项目切换入口、异步请求与回包保护；计划原生重测|旧项目资料清空，旧回包不能覆盖|project 头部是 Label，无项目切换入口；无本轮迟到回包注入；tick 源注释承认旧 isolate 风险|NOT_RUN|main:999–1004,1533,1726–1728；A-M1-01/03|
|字体/长文/放大/错误区|目视原1280/980截图，读取PNG尺寸/SHA并查布局|实际3视口/150%文字可达，长文和错误可读|截图文字可辨；底部被dock遮挡，完整错误/新建区不可见；1440与980原图字节完全相同；无150%长文证据|NOT_RUN（完整）；核心操作见D-M1-01|candidate-audit.json；A-M1-02|
|测试失败清理|抽取驱动原 run_host AST，用假 Popen，log.open 注入 OSError|启动后任何异常都回收自己进程|只有 Popen(fake)，未调用 killpg/wait/terminate；真实进程创建为0|FAIL（安全）|driver-failure-injection.json；D-M1-02|

### 全部 M1 硬验收

|编号|结论|明确边界|
|---|---|---|
|1 真桌面打开、3视口/放大、主要动作/错误/返回可达|FAIL（核心证据交付）；独立运行 BLOCKED|原图有框架，不能据参数或PNG存在认定可操作；D-M1-01；150% NOT_RUN|
|2 task_id稳定、无权限项目切换/迟到回包|FAIL（筛选导航源码）；其余 NOT_RUN|D-M1-03；不把 ID 字段存在写成恢复或项目保护PASS|
|3 中文输入、未保存、焦点、错误、对比|NOT_RUN（真实原生完整项）|真实表单未接；普通中文字目视可读不代表输入/焦点/对比测试通过；按本次核心裁决挂账|
|4 角色/状态动作、诚实说明不可用|PARTIAL|动作矩阵/禁用原因存在，附件与身份标明演示/未接；动态动作区未验证；不代签授权|
|5 空态/选中/错误/窄窗截图|NOT_RUN（完整集合）|现有三张命名PNG实为全桌面空态，缺选中任务及明确错误态；1440与980相同SHA|

### 相关既有用例（使用原文定义）

CONTEXT 对若干 U 编号的描述与原 UI 表不同。本表按 `docs/implementation/10_UI_UX_SPEC.md:173–183` 原文保留范围，不能缩减为编码方自定标签。

|用例|完整范围结果|本轮依据 / 未测边界|
|---|---|---|
|T18 可见任务事件与列表/搜索/附件防探测|NOT_RUN|源码可见投影仍存在，无真实权限/事件/搜索/附件负例；G0-B不因延期判FAIL|
|T28 同 task_id 原生操作/回读/重开保留|NOT_RUN|Store重开不是桌面工单重开；作者无tasks/回执落盘，本轮宿主BLOCKED|
|U01 三角色首屏待办/阶段/下一人|FAIL（框架核心）；三角色操作 BLOCKED|动态列表/详情故障D-M1-01，角色操作未独立执行|
|U03 三角色事实一致/权限动作/禁止自验|NOT_RUN|17领域命令体不变和显示矩阵不能代替三角色运行；可信身份M2到期|
|U07 重复点击/丢包/冲突/离线保留身份输入|NOT_RUN|没有这些原生失败注入；筛选身份混用D-M1-03仅为子项缺陷|
|U08 空态/长文/附件失败/无权限/过期建议出口|NOT_RUN（完整）|原图空态存在；其余未运行，不把占位文字计成可继续流程|
|U09 1280/窄窗/文字放大无裁切|NOT_RUN（完整）|同图重复和底部遮挡；150%未运行|
|U10 键盘完成主流程/清楚焦点/多状态线索/对比实测|NOT_RUN|原生键盘与对比实测均未执行|
|U11 真宿主滚动/输入/面板稳定、反馈真实|FAIL（框架刷新交付）；其余 BLOCKED/NOT_RUN|D-M1-01；没有实时中文编辑、滚动点击和恢复证据|

## 缺陷

### D-M1-01 — P1 / 必修：工作台动态刷新包含不存在的宿主调用，核心列表/详情/动作未交付运行证据

- 文件行：`app/bundle/main.splash:2042–2054`；列表占位 `1599–1606`；原 `r1/logs/launcher-m1r1-1280x800.log:465–466`，其余两日志也有同错。
- 触发：启动已交接 M1 包→初次 refreshDesktop，之后每秒 tick；切换页签再次走同路径。
- 预期：列表从真实可见任务更新，详情随稳定ID显示事实，一个主动作随角色/阶段更新；空态可新建；页签可切换。
- 实际：三日志分别18/20/20条 `[E] widget 'set_visible' not found in tree`；原图 list_summary 为“—”、task_row_0 为“初始化”、详情未出现动态内容。三次作者运行无 tasks/actions/events。不能用 `eval_bytes=85859` 证明完成执行或可操作。
- 根因：把 `ui.tab_overview.set_visible != nil` 当作方法可用性探测，在该实际宿主上它本身未形成可靠能力检查。此调用位于所有新列表/详情/行动区刷新之前。结合原图判断刷新交付失败；具体异常传播与每个控件更新时序尚待原生复现，置信度中。
- 影响：本模块核心“可操作工作台”不能成立；不是颜色、边距等美化问题。
- 具体改法：先在相同宿主用最小控件实证可用的页签切换方法。若无可靠隐藏API，改为一个共享详情内容区，以已验证的命名控件更新方法展示所选页签；不要再猜API。让一次命令点击结束后同步刷新列表、详情、动作和状态，不仅刷新旧两个Label；不能靠另一 isolate 的tick覆盖来宣称成功。保留原命令校验/事实源。
- 验证方式：项目内新隔离 home，通过真实新建按钮生成task_id，列表选中→三页签→主动作→权威回执/状态回读→关闭重开；日志无该错误，截图包含选中/错误态；任务按钮与文字真实响应。本轮这些原生操作 BLOCKED，未以作者自述代签。

### D-M1-02 — P1 / 必修：M1 驱动启动后的日志失败绕过回收，且隔离路径声明不足

- 文件行：`runtime/optimization/2026-10-09/M1/r1/probe/install_and_host_m1r1.py:299–308,325–332`；环境 `213–217,272–281`。
- 触发：Popen成功后 log_path.open 抛出异常；getpgid、线程初始化等前置步骤也在保护之外。
- 预期：任何启动后失败均进入finally，回收本次进程组并等待退出，始终记录结果；宿主HOME/app-data/临时/日志/缓存全部隔离，检查残留不可用时写UNKNOWN。
- 实际：执行**原run_host AST**、假Popen、日志打开失败注入，调用序列只有 `Popen(fake)`，没有killpg/wait/terminate；没有创建真实进程。原驱动只设置部分环境、无写入约束预检，不能证明所有宿主缓存/app-data都在本项目。没有据此推断已发生外部写入。
- 根因：资源生命周期的try/finally晚于子进程创建与资源初始化；从M0继承相同漏洞。M1现在实际使用该驱动，不能作为不影响M1的前序挂账放过。
- 影响：异常时可留下窗口/进程，直接违反用户测试后立即关闭及隔离硬约束。
- 证据：`results/driver-failure-injection.json`；原M0 Review D-R9-2仅作历史来源，本轮自行注入复证。
- 具体改法：先准备日志及隔离环境，或从创建子进程起就进入完整保护；用可为空的资源句柄清理，避免异常遮蔽原错误；kill只针对本次已知PID/进程组。补齐CFFIXED_USER_HOME和XDG目录等实际路径，并使用限制外部写入的隔离机制；预检失败不得启动。结果落盘涵盖整个流程。
- 验证方式：分别注入getpgid/log.open/线程启动失败，断言自己进程被回收且结果保存；之后真实后台启动一次，正常与异常退出均确认无本次残留。无需公开发布、模型配置或Abram新授权。

### D-M1-03 — P1 / 必修：筛选后上下条导航使用未筛选索引，选中错误任务

- 文件行：`app/bundle/main.splash:1052–1058,1159–1168`。
- 触发：可见任务按顺序 A/B，仅收藏B；选中B→点击上一条或下一条。另例：可见A/B/C，筛选后B/C，从B下一条。
- 预期：第一例仍选B；第二例选C；选中 task_id 和命令目标一致。
- 实际源码逻辑：stepFiltered 在 filteredVisibleIndices 内算 np，却交给从 visibleIndices 取位置的 selectTaskAtVisiblePos；第一例改选未收藏A，第二例仍选B。三个源逻辑复算均FAIL；这不是本轮原生点击结果。
- 根因：同一个位置整数来自两个不同列表；稳定ID字段没有消除列表坐标混用。
- 影响：我的任务/收藏/处理中视角的核心任务导航失效，用户可能对意料之外的任务发起动作；不是授权绕过已证明。
- 证据：`results/selection-source-traces.json`，明确为检查源码后的Python索引轨迹；原生运行待解阻。
- 具体改法：stepFiltered直接用本次filtered idxs[np]解析目标task_id，经同一个按ID选中助手同步selected_task_id和命令兼容下标；不要再次从未筛选列表取np。筛选/导航/换项目后校正分页和选中；勿改领域授权规则。
- 验证方式：两组隔离任务跑收藏/处理中/搜索过滤、前后边界和分页后上下条；逐次比对所显示ID、selected_task_id及回执task_id；刷新/重开仍指同一对象。

### 建议挂账（均不单独导致 FAIL）

|编号 / 严重性|文件行、证据、根因与影响|具体改法 / 验证|
|---|---|---|
|A-M1-01 / P2 搜索、输入、项目切换未接|main:52–55,999–1004,1533,1581–1585；按钮无输入回调，pending_input/panel占位，项目仅Label；CONTEXT把输入延期M3属于作者计划，非本次身份/模型延期裁决|保留原硬验收挂账；后续在同工作台接真实中文输入/项目选择，按当前范围逐步验焦点、Esc/导航保留、旧回包丢弃；不要把未测项写PASS|
|A-M1-02 / P2 视口/截图与PASS断言超出证据|driver:458–463；三个PNG都是约2560×1266/1268整桌面；1440/980均SHA f58e8db0…且字节相同；原图底部被dock遮挡。驱动只断言启动/eval/PNG存在/pgrep NONE，无业务或日志错误断言|结果改成分层“启动烟测”与核心交互；核对实际客户区尺寸/缩放，不只参数名；原生补980窄窗、150%、长文/错误/选中截图，发现错误不得总PASS|
|A-M1-03 / P2 稳定ID桥接/旧数据/迟到刷新风险|load:290整对象替换，init:331仅判断空字符串；currentTask:372–375仍取下标，ensureSelectionVisible:1061–1064对有效ID不重同步下标；tick:1726–1728/2060–2066承认可能旧isolate；导航/filter/tab/page修改多未saveState|补明确可选字段默认值并按ID同步旧命令目标；持久化实际视图变化；原生重开旧state、任务顺序改变、切换身份后等待tick，验证旧项目/联系人不返回；本轮不声称已经发生泄露|
|A-M1-04 / P2 动作与信息不完整|main:1210–1212将已有bindAsset入口禁用；1254–1261拒绝提议放在isMine分支内，报修人通常进不到；终态/阶段/选中样式及地点/联系人摘要仍需核对|后续对应业务模块接通入口和字段；M1只确认诚实不可用、命令没有被删。对实际合法角色/阶段作可见与禁用原因回归，不降附件/独立验收标准|

## 判定

- 最终结论：**FAIL**，仅依据 D-M1-01、D-M1-02、D-M1-03 三项真正影响核心框架或安全的 P1。其余建议和后续业务缺口不单独判FAIL。
- 本轮不是“独立原生测试PASS”。必需原生操作 BLOCKED/NOT_RUN，无法用作者启动日志、截图或模型报告替代；缺口逐条保留。
- 解阻条件：本机审查执行通道能在项目隔离路径约束下运行宿主（隔离预检成功），并能清点/回收本次进程和确认窗口关闭。当前授权已覆盖本地catalog安装、隔离离线签名和launcher测试，不需要Abram公开发布/新计费授权。本地安装路线已独立PASS，不能以预检失败归因为“本地安装不可行”。
- G0-B：**延期缺口（Abram 已裁决，M2 到期）**；G0-E：**延期缺口（Abram 已裁决，M3 到期）**。均不计本轮FAIL/BLOCKED或NEEDS_ABRAM。
- 受影响既有模块：只做M0同一Store路线/当前M1包的正负恢复与继承清理缺陷回归；未重写M0结论，不扩审附件、提醒、模型或完整事务。
- 门禁：仅更新GATES中M1的status/Review字段和needs_abram；保留作者旧review_summary来源及所有其他模块/实现字段。原ACCEPTANCE.json、业务代码、候选、旧报告均不改；原后端历史PASS不转签原生PASS。
- 是否允许下一模块：**否**。修复交接仅限D-M1-01/02/03，并重跑受影响框架/安全回归；提交新候选与M1_IMPLEMENTATION_rN后按相同缺陷编号复审。不执行下一模块。
- 会话标题：可用工具未提供本对话createdAt及改名/回读接口，未以当前日期代替创建日期，也未声称已实际改名。

STATUS=FAIL
NEEDS_ABRAM=no
