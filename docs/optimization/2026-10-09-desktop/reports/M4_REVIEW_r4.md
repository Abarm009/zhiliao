# M4 独立 Review r4

最终结论：**FAIL**。本轮为 r3 缺陷闭合复审，只保留两条核心必修 P1：D-M4-03、D-M4-04。真实桌面运行另为 BLOCKED；不进入 M5。

- 审查者 / 日期：本会话独立审查，2026-10-11（Asia/Shanghai）；未委派子代理。源码、局部控制流及安装层结论置信度高；发行宿主完整业务结果未知。
- candidate_id：`M4-r4-worktree`；base_candidate_id：`M4-r3-worktree`。由实施报告、`M4/r4/CANDIDATE.json`、GATES 三处交接一致定位，未按文件修改时间选版本。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；被审文件是未提交工作树，不能用 HEAD 替代内容摘要。
- 主源：`app/bundle/main.splash` SHA-256=`8b3c589a7c360a3a34e9a9d1f6c5e6c104357e3958e073769dbd03ed7ca6800c`，332548 字节，实际 `splitlines()` 7269 行；清单声明7268行，按 A-M4-01 建议挂账，不因该数字判 FAIL。
- 基线：r3 留存安装副本 SHA-256=`4c753154cf55fb5912a53a5f09425c54bcc5787ee5e54d5d1f82cd8096a50f13`；独立生成 `r3-to-r4.diff`。开始/结束主源、配置、账号表、安装映射、候选清单和宿主摘要一致，见 start/end-snapshot。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r4.md`。
- 前置：M3-r4 独立结论仍为 **FAIL**（`M3_REVIEW_r4.md`），不存在已接受的 PASS 前置。按本次前序挂账指令继续做 M4 缺陷复审，不修 M3，不将此记录升级为 M3 PASS。
- 实际环境 / 路由：本地受限执行环境；工具未提供主会话实际 Router 路由、切换或 gpt-6.1-sol 核验接口，也未提供本对话 createdAt/标题读写接口。未冒称已切换、已确认指定型号或已实际设置标题。
- 宿主：指定 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`，二进制 SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮没有启动 launcher，没有使用 `--help`，没有新增宿主窗口；历史残留窗口不可清点，状态 UNKNOWN。
- 已阅读：先 CONTEXT_M4、实际 AGENTS、00/01/02/M4/04 模板、r3 Review、r4 实施/候选/作者证据及缺陷相关源码；核 M3-r4 结论及相关 T/U 定义。依修复轮规则使用浓缩上下文，不展开无关模块和重新通读全部历史资料。
- 已运行：固定摘要/基线差异、全新隔离预检、局部 Splash 预约边界/确认/日期探针、两独立上下文执行实际锁函数的三轮受控交错、前导开工资格/时窗回归、本候选副本离线签名及官方 install_staged/Store 重建/may_run、篡改拒绝与恢复安装。
- 未运行：真实桌面从 M3 创建到开工、三角色首屏/键鼠、可信账号真实查询/写入权限、原生预约过期/服务关系反例、真正双接单/双预约确认、业务权威回执/事件回读、逐业务写点失败/重启恢复。不能用局部探针和作者模拟代签。
- 隔离与副作用：测试证据都在 `runtime/optimization/2026-10-09/M4/review-r4/`。子进程 HOME、CFFIXED_USER_HOME、TMPDIR、XDG缓存/配置/数据、OctoSense HOME/app-data、Metal缓存均重定向。未读取明文凭据文件或 provider 密钥；账号表/安装映射仅核摘要。没有修改原业务数据，没有手改任务跳过预约；未改业务代码、原验收台账或其他模块；未联网、上传、publish/listing、push、发消息、Issue/评论或部署。真实模型请求0次，未观察余额/402错误。

下文证据短名均位于 `runtime/optimization/2026-10-09/M4/review-r4/results/`，脚本/测试副本在证据根与 `probes/`。作者原证据未覆盖。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/前置/增量|核三方交接、r3留存和r4摘要，保存差异，末核|固定候选、可定位增量、M3已接受PASS|候选和增量可定位；M3仍FAIL|定位成立；前置未PASS|start/end-snapshot、r3-to-r4.diff、gates-before|
|硬1 / D05资格设备回归|在新隔离目录重跑源码未改的开工前导守卫：合法、撤角色/技能/身份、归档、旧技工|合法可到边界；资格/设备失效拒绝|合法true；撤角色/技能/身份、归档、旧技工拒；撤服务关系错误出口局部VM报join错误|已关闭源码子范围保留；原生BLOCKED|qualification-regression、affected-regression|
|硬2 / D03预约边界|实际runCommandBound，磁盘另一任务同技工预约；重叠、相邻、无spec对照|重叠拒；相邻允许；可到实际命令边界|重叠和相邻均rc1：`no getter for field tech on type nil`；无spec对照true|FAIL核心接线；原生BLOCKED|vm-probes.boundary_*、source-traces|
|硬2 / D02改约|比对hasTechConflict与改约原排除/准入顺序；追新边界|旧确认保留、待确认可提交、拒绝不误改|r3排除/准入修复保持；新边界nil错误阻断正常提议/确认/改约|D02源码子项保持；完整T12未通过，归D03|affected-regression、source-traces、boundary_*|
|硬3 / D03并发|两个不同PID的活跃控制进程，各独立VM执行原acquire；A不退出时B取得；A再执行原release|仅一取得；不能释放别人的锁|三轮均A/B acquired=true，A释放清空B stamp，B仍在测试临界区|FAIL锁算法；真正业务并发BLOCKED|concurrency、probes/lock_worker.py|
|硬4 /有效预约开工|重跑合法、未到开始、end==now、旧assignee前导守卫|非法时窗/旧技工不能开工|合法通过前导；其余拒；没有提交开工命令|守卫子项保持；完整原生BLOCKED|qualification-regression|
|硬5 / D04确认恢复与旧AI失效|普通新输入、旧草稿未编辑、改派失效后只改原文、关闭重填|新人工内容能继续；旧AI绑定不能靠任一版本++复活|普通输入/关闭重填true；未改旧内容false；改原文后旧AI问题/来源仍保留却confirmed=true|PARTIAL改善，旧绑定P1未闭合|vm-probes、source-traces|
|D01时区回归|实际日期helper与Python UTC+8独立标准比对；原validate比对|上海日期换UTC毫秒准确，非法日校验保留|2026-10-12 00:00/01:00为1791734400000/1791738000000，标准一致；helper/validate与r3同源|已关闭源码子项保持；原生输入/显示BLOCKED|vm-probes.conflict_and_dates、independent-date-reference|
|错误恢复|当前预约边界nil失败后核锁；旧expected_version拒绝后核spec|失败清理、spec不污染下一命令|失败后stamp保留；expected4/live5拒绝后spec仍在全局；不存在作者称“入栈立即清理”|D03未闭合；原生恢复BLOCKED|boundary-failure-cleanup、boundary-early-reject|
|三角色首屏|比较mainAction/secondaryActions与r3并新隔离预检|真实首屏可说明阶段/下一人、错误可继续|动作函数未改；无本候选原生界面证据；正常预约边界先中断|真实UI BLOCKED；不新增视觉P1|affected-regression、preflight|
|本地catalog/install_staged|当前源码筛选副本→离线keygen/certify/stamp/sign/verify→官方安装→Store重建/may_run→篡改→恢复|本地可安装、篡改拒、私钥删除|安装/恢复rc0；篡改rc1；主源/身份注册/模型配置安装字节匹配；私钥剩余0|PASS安装层，仅当前副本digest|local-store-validation、end-snapshot|

### 证据边界

1. 本地 `identity-vm-probe` SHA-256=`204b5892fad7fcfc0cb634a638e8067e73760018bbcb014ced2f3547ea2cbede`，使用项目已有受限文件系统。它不是指定发行 launcher。预约边界抽取原函数与实际读磁盘/锁函数，授权、源状态、receipt查询及最终runCommand用桩；nil错误发生在runCommand之前。不称其为原生业务端到端失败。
2. 确认探针仅在测试副本将 `_g.ok` 改为 `_g.good`，事实守卫、身份和创建outcome合成，以避开既知本地VM accessor冲突。未改候选源码；true表示控制流放行，不证明实际创建/权威回执。raw_edit反例日志干净，且有确定的源码分支支持旧内容复活判断。
3. `contact_edit_restores_old_ai` 虽rc0且写出了观察文件，但日志含parser错误，**不作为闭合或缺陷的运行证明**；保留原始记录。D04判定使用无该错误的raw_edit反例。服务关系错误分支仍因局部VM `.join` 不确定，不能由此判定发行宿主不支持该方法，也不新增P1。
4. 并发实验的两个活跃Python控制进程分别在独立VM执行抽取的实际Splash acquire/release，测试临界区由控制进程保持；取得锁的VM调用本身会返回退出。证据说明锁函数无排他/持有权保护，**不是两个原生业务命令都成功的证据**。三轮子进程均wait/必要时kill清理；真正T04/T11和任务/事件/回执提交仍BLOCKED。
5. r3 D01/D02/D05的“关闭”仅为先前明确源码子范围；本轮保存其改善，不升级完整原生用例。开工探针停止于业务突变前，以true表示通过前导；身份/角色/时间/任务都为隔离合成数据。r3→r4差异及守卫依赖未改，不是使用旧截图代验。
6. 新签名副本digest=`852fc80e3b52be42f393a68456f0a0bd197713d5a81bf762eb02874165ebb3cd`。原manifest未改，不能用副本安装证明原历史digest通过。`may_run`仅storage、空hosts，未证明登录/HTTP/业务运行。`store-test/keys/working.key`、`anchor.key`在finally删除，删除路径、剩余空列表及末核均有证据；未输出私钥。没有公开发布或请求新授权。
7. 作者43/43由26项源码关键词、13项Python重写算法和4项锁复现检查组成。其算法没有复现`_cc`保存后从nil全局读`cc`的接线；锁复现测试旧r3 rename，不是当前r4真互斥。部分pass条件直接写True，不能继承为本轮验收。

### 相关既有用例逐项复核

本轮只查r3缺陷及受影响回归；所有完整原生用例均未执行成功链，标BLOCKED，不以源码或局部探针代签。

|用例|本轮结果与精确范围|
|---|---|
|T04|FAIL D03锁函数非排他；真实双接同OPEN、承接者/成功事件一致性BLOCKED。|
|T05|资格/技能前导负例拒绝保持；真实接单权限、经理分配身份和事件BLOCKED。|
|T06|reassign与r3同源；旧assignee开工前导拒绝；真实改派取消旧预约、ACCEPTED/新承接者读回BLOCKED；旧AI恢复仍D04。|
|T07|设备原函数同源、归档前导拒；编码/asset载荷等价、伪造/跨项目真实绑定BLOCKED。|
|T08|原services规则保持；撤服务关系局部错误出口不确定；安装位置与服务空间真实绑定BLOCKED。|
|T09|设备与开工守卫保持；真实缺设备拒、自换限制、经理更正旧新值/理由BLOCKED。|
|T10|提议/确认权限与状态原规则可定位；合法appointment spec现在触发D03nil错误；真实主体/提议不直升SCHEDULED BLOCKED。|
|T11|局部冲突helper跨项目true、相邻false；实际边界两者均nil错误；锁反例FAIL D03；真双确认及权威预约结果BLOCKED。|
|T12|r3 D02排除/准入前不突变源码保持；新边界D03阻断正常改约；真实新确认替换/拒绝保留BLOCKED。|
|T13|原确认到期分支保持；实际410/未跑定时器/伪客户端时间及恢复BLOCKED，没有把预约end边界前导探针当410测试。|
|T14|实际helper上海换UTC与独立标准一致，原非法日期guard保持；真实模糊时间核对/显示/end<=start反馈BLOCKED。|
|T15|actual boundary旧version拒绝并留下spec；commitBound仍只查本地t.version；原生409刷新/不覆盖/百分比限制BLOCKED，受D03影响。|
|T31|取消/终态源码未改；实际释放预约留事件、终态操作拒、新建关联任务BLOCKED。|
|T35|未编辑失效旧草稿拒；改派后只改原文会放行旧AI草稿，FAIL D04；真实异步/主体/任务版本交错BLOCKED。|
|U01|mainAction/secondaryActions未改；三角色真实首屏、阶段和下一处理人BLOCKED，A02挂账。|
|U03|同任务三角色事实/权限/不自验真实画面及查询BLOCKED；不以按钮隐藏替代权限核验。|
|U04|旧确认与待改约原投影未改；新边界D03阻断正常预约/错误恢复，真实同屏状态/不假成功BLOCKED。|
|U05|安装位置/服务空间来源投影未变；真实选择/展示BLOCKED，继续A02建议。|
|U07|D03失败清理/并发、D04旧AI恢复仍FAIL；真实重复点击/丢响应/离线/重启输入及任务身份恢复BLOCKED。|

## 缺陷：沿用编号，不做无关扩审

### D-M4-03 — P1 / 必修 / OPEN：预约边界接线中断，互斥未实现

- 文件与行：`app/bundle/main.splash:2112`（acquire）、`:2129`（release）、`:2138`（命令边界）、`:2229`～`:2237`（spec）、`:2386`（本地version检查）；调用点在`:4085`、`:4150`、`:4290`函数内。
- 触发：隔离task-A版本5、同技工另一task-B预约100–200；设置当前spec150–250或合法相邻200–300，再走原命令边界；另外A取得锁未结束时B取得，再让A释放。
- 实际 / 预期：两预约探针均rc1，`no getter for field tech on type nil`，runCommand未到达，stamp仍留；无spec对照成功进入桩命令。预期重叠明确拒绝、相邻正常继续，异常有可对账结果并释放自身资源。锁三轮均双方acquired=true、A释放清空B的stamp；预期排他和持有者限定释放。
- 根因1：保存`_cc`后清全局，再令`cc=STATE.m4_cross_check`，必然读nil；新增权威重读根本不能正常执行。清理位置也在多条早退之后，expected4/live5拒绝时spec未清，可能污染后续非预约命令。
- 根因2：`fs.write(tasks.lock,stamp)`无条件覆盖，release无条件写空，连进程内重入保护也不存在；注释诚实写BLOCKED不能让命令边界获得互斥。`commitBound`的` t.version == expected+1`检查的是各自内存对象，两者各自加1都可满足；不是磁盘CAS，更不是全量预约事务。修复读nil后仍有重读→另一上下文写→当前写的竞争窗口。
- 影响：普通预约提议/确认/改约核心出口被新代码阻断；同任务接单和跨任务同技工并发预约没有唯一成功保证；错误后spec/锁无可靠清理。不是视觉建议或只因前序模块FAIL而挂P1。
- 证据：`vm-probes.boundary_overlap/boundary_adjacent/boundary_no_spec`、对应`.log`、`boundary-failure-cleanup.json`、`boundary-early-reject.json`、`concurrency.json`、`source-traces.runCommandBound/commitBound`。本地VM失败及锁反例不冒称发行宿主真业务双成功。
- 具体改法：在入口将spec保存到局部并正确使用保存值，覆盖所有退出清理；失败不得将读盘失败当无冲突。把授权、读取最新任务及跨项目预约、冲突判定、任务/事件/回执提交收敛于实际可验证的串行事务/互斥边界；释放验证持有者且异常清理覆盖全过程。不要将普通write、预读exists或本地version检查称作互斥兜底。若指定宿主没有可验证原语，交付该宿主最小复现并保持BLOCKED，不暗加未经裁决的业务服务。
- 验证方式：先重叠拒/相邻允许、旧版本拒后下一合法非预约命令正常、坏磁盘与失败清理；再在发行宿主两个独立上下文同OPEN接单及跨任务/跨项目同技工重叠确认仅一成功，相邻均成功，核权威task/action/event与失败/重启恢复。不能用旧rename复现或Python重写冲突循环判已修。

### D-M4-04 — P1 / 必修 / PARTIAL：恢复出口改善，但任一版本增长复活旧AI

- 文件与行：`main.splash:1967`（失效快照）、`:3372`（原文编辑）、`:3616`（确认入口）、`:3653`～`:3674`（恢复判别）；`:3705`的`createDraftFromPanel`继续使用旧PENDING_DRAFT字段并记录新TASK_INPUT。
- 已改善：新人工描述与关闭/重开重填的控制流均可继续；失效后完全未编辑的旧草稿仍拒。保留这两个改善，不要求恢复r3永久拦截。
- 触发：AI草稿问题A/来源ai/历史原文A（输入版本1）已APPLIED；执行原`m4_invalidateConfirmation("reassign")`，使EXPIRED；仅把原文改为问题B（版本2）再确认，没有重新生成/明确转手工核对旧建议。
- 实际 / 预期：局部确认投影`confirmed=true`，仍`problem=旧AI问题A`、`source=ai`、`history=A`、`history_version=1`，但`raw=新的问题B`、`raw_version=2`。预期旧proposal/旧确认保持撤销；新人工或新AI内容经明确核对当前主体/授权事实/任务及输入版本后形成新绑定，再继续。
- 根因：把`raw_input_version > snapshot || draft_version > snapshot`直接等同“新绑定有效”。editRawText只废请求/置invalidated，不更新旧PENDING_DRAFT问题、来源和AI历史；失效将active置false，确认入口的active请求版本守卫随之不再检查旧绑定。确认恢复也不核旧proposal/task绑定是否已更新，最后成功才清invalidated不能补回缺失的验证。
- 影响：改派/改约后的旧AI建议撤销不可靠，旧AI问题可与新原文一起进入创建路径；M3→M4核心输入/确认链无法认定安全闭合。属于r3 D04已要求的旧内容拒绝与新版本重新核对，未扩审其他M3欠账。
- 证据：无parser错误的`vm-probes.raw_edit_restores_old_ai`与`stale_unchanged_rejected/fresh_manual_edit_confirm/close_reopen_confirm`、相应日志和原源码。创建/事实/身份依赖为合成桩，**不是已在发行宿主写入错误工单**；contact编辑探针有parser错误，不用于定案。
- 具体改法：将旧proposal失效与可编辑人工草稿分开。编辑后的原文不能自动恢复旧AI来源/版本；提供明确转人工或重新请求/核对入口，保存输入，重建当前输入/草稿/主体/项目/任务/事实/到期绑定。确认核该新绑定，而非任一计数器++；旧失效记录保留。不要重新永久禁掉正常人工编辑，也不要靠无条件清invalidated绕过旧AI检查。
- 验证方式：普通人工初次输入、编辑与关闭重填可继续；改派/改约/解绑/撤权后，无编辑、只改原文、只改联系人等都不能直接执行旧proposal；明确核对的新人工内容可从真实UI继续。核输入保留、来源和实际task/action/event一致，旧绑定无执行记录。

### D-M4-01 / D-M4-02 / D-M4-05 — 先前关闭源码子范围保持，完整原生BLOCKED

- D01：日期helper/validate与r3相同，本轮UTC+8独立对照一致；屏幕日期/星期未测。
- D02：排除当前任务被替换预约及准入通过后再SUPERSEDE的改善保留；新边界中断归D03，不额外编重复缺陷。
- D05：startProgress及原角色/技能/身份/设备/时窗前导规则未变；合法及撤角色/技能/身份、归档、旧技工、时窗反例重跑。服务关系错误出口局部不确定；没有可信5账号原生登录/查询/写入实证。

### B-M4-01 — 必需运行BLOCKED：隔离与宿主回收条件仍不成立

- 本轮重新执行`sandbox-exec -f review-r4/isolation.sb /usr/bin/true` rc71，原文` sandbox-exec: sandbox_apply: Operation not permitted`；pgrep rc3，`pgrep: Cannot get process list`（另有sysmond不可用信息）。证据`preflight.json`。
- 仅设HOME不能证明launcher所有写入都限定项目；当前也不能清点历史进程/窗口。按用户硬约束不启动launcher，不以作者“不启动”的声明代独立检查。
- 解阻条件：在具备可验证项目内强制隔离、禁网络/受授权模型访问控制及可靠本次进程/窗口回收的环境，后台启动指定launcher，finally关闭并确认无残留；从实际M3创建工单跑到开工，完成真权限/服务/时区/过期/并发及三角色错误恢复。前序M3未PASS记录保持，需有可定位的真实创建/权威结果才能证明该链；本轮不代修前序。
- 不需要Abram新增授权；没有付款错误，也无需公开上架来解本地安装路径。

### 建议继续挂账，不因建议判FAIL

- A-M4-01：清单7268行与实际7269行、自测PASS表述、GATES作者改写的review_summary与独立r3报告不一致；应按实际产物和证据层级生成交接。当前候选内容SHA匹配，不升P1。
- A-M4-02：三角色首屏、日期/当前预约与待改约、设备安装/服务来源未有本候选真实画面；沿原建议挂账，不新增视觉锦上添花要求。核心真实UI链本来就是必需运行BLOCKED。
- A-M4-03：previous_assignee历史建议保留，不扩修历史系统。

## 判定

- 最终结论：**FAIL**。精确范围是固定M4-r4候选相对r3缺陷闭合及受影响回归；只因D03/D04核心P1未闭合判FAIL，不因建议、历史欠账或“还可更漂亮”判FAIL。
- 必修：D03正确接入预约边界并建立真实可验证互斥/事务（能力不足明确BLOCKED）；D04允许新人工内容重新核对，同时禁止计数器增长复活旧AI绑定。
- 阻塞/未测：发行宿主强制隔离与进程/窗口回收、真实M3工单→开工、真正业务并发、可信权限、权威回执/事件及失败重启恢复。M3前置仍FAIL；无原生成功链，不能PASS或“基本通过”。
- 受影响先前模块：命令边界影响M2及M3；确认恢复影响M3旧建议/新人工内容。已做受影响源码差异与局部回归；原生复验BLOCKED，不修改M0～M3或其他模块结论。
- 门禁：仅写GATES中M4 status及审查字段，`review_report`指本报告；保留既有构建字段与审查历史，替换前审查字段另归档，标注含作者自述而非独立验收。`docs/build-loop/ACCEPTANCE.json`不改，不把局部探针覆盖原有来源/验收。
- 是否允许下一模块：**否**。只留本模块D03/D04修复及解阻条件；不执行下一模块，不给下一模块入口。
- NEEDS_ABRAM=no：身份/MiniMax已裁决；本地catalog/install_staged可行，离线签名已授权且私钥删除；剩余是代码/执行环境问题，不是需新增公开发布授权或付款的问题。

STATUS=FAIL
NEEDS_ABRAM=no
