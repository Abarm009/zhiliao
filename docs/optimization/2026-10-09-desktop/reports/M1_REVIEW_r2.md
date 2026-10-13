# M1 独立 Review r2

- 最终结论：**FAIL**。候选 `M1-r2-worktree`，基线 `M1-r1-worktree`。只保留 **D-M1-02（P1 / 必修）**；不是因建议项或 M0 挂账判 FAIL。置信度：高（清理函数原代码失败注入）；原生交互结果未知。
- 审查者 / 日期：Codex 主会话，唯一审查方；2026-10-10，Asia/Shanghai。未使用子代理。当前接口不能确认或切换主会话 Router / gpt-6.1-sol，不声称已切换；没有可调用的当前会话 createdAt / 改标题接口，未用当前日期猜标题。
- candidate_id / HEAD：`M1-r2-worktree` / `8d730569546cb57310944bb299695134df773b9d`；工作树非干净。以 GATES 的 candidate_id、implementation_report 与报告内交接 ID 定位，没有按文件时间挑选候选。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M1_IMPLEMENTATION_r2.md`。本轮为修复复审，仅核对上一轮 D-M1-01/02/03 和受影响回归，不开展其他业务模块扩审。
- 前置：M0 仍为 FAIL，报告 `reports/M0_REVIEW_r10.md`，**不存在已接受的 M0 PASS 候选**。按 Abram 本次“前序挂账”覆盖通常前置门禁，继续审 M1；不改写 M0、不要求本轮修其业务缺陷。
- 已读：项目 AGENTS、M1/CONTEXT_M1、00/01/02、M1 指令、04 模板、M1 r1 Review、r2 实施报告/候选清单/原证据；受影响的 main.splash 与驱动、desktop v2 DESIGN_SPEC、T18/T28 及 U 原文。CONTEXT 的 r1 自测说明没有当作当前结论。
- 已运行：独立隔离预检；官方 Store 当前包安装/重开准入、篡改拒绝、恢复重试；原 Python 驱动函数 AST 的假进程失败注入；筛选索引源码复算；候选哈希/差异/截图审计。
- 未运行：本轮 launcher、亲自原生点击/滚动/键盘/焦点/中文输入/150%放大、三角色命令回读及桌面重开。隔离预检失败，不能拿作者声称代替。
- 证据根：`runtime/optimization/2026-10-09/M1/review-r2/`；以下 `results/` 均相对该目录。保留 r1/r2 作者证据及既有报告。

## 候选与宿主一致性

|对象|本轮实物核对|
|---|---|
|工作树 / staging / artifact / install-root / apps镜像 main|均 86245 B；SHA-256 `7dd8d89c4f37774c5d59535049f208251cddf0a51bff6ab656cb637bdfafb00d`|
|签名 staging manifest|id `octosense-repair-m1r2`，version `0.1.0-m1r2`；SHA `8c47cc70f76c417f508b67f034d93173c342ac6997ded05675204fa02d771419`|
|当前 bundle digest|`b8af06de3721d8ba3febbae605bfc7b88f9525a211202e7bc4bedacd0ee643b7`；官方安装实际输出相同|
|当前 catalog|sequence 1；SHA `50a39465824bf5b8fe05aac50f98ec31d4df66af78e0460d67faaf7b33e973a5`|
|工作树 manifest|仍为 `octosense-repair / 0.1.0-b`；与签名 staging 不同，不能用工作树 manifest 代表已安装候选|
|指定 launcher / kernel|M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS；launcher SHA `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；kernel SHA `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`|
|差异与命令边界|保存 `results/r1-to-r2-main.diff`；17 个既有业务命令函数体逐一相同。新增页签刷新只写显示文字；未见本轮新增最终业务状态绕过命令路径|
|开始/结束冻结|575 个输入文件 SHA 均一致，含候选、作者数据/证据、宿主及更新前 GATES；见 start-snapshot / end-verification。最终只按本轮授权修改 M1 审查字段|

作者报告 §10 的 catalog `6ebd528f…` / digest `bbe54cfe…` 与现场、原 results 的当前值不同；§7 的部分 PNG 字节也不一致。当前签名包、catalog、Store 输出和 main 可以交叉唯一定位，故归入既有 **A-M1-02 建议挂账**，不另列 P1。后续交接应机械生成完整哈希清单。

## 隔离与运行边界

本轮隔离预检 HOME、CFFIXED_USER_HOME、TMPDIR、XDG cache/config/data、OctoSense home/app-data、Metal cache 都指向 review-r2；profile 禁止隔离目录外写入及网络。`sandbox-exec true`、`sandbox-exec echo` 两次均 **rc71 / sandbox_apply: Operation not permitted**。`pgrep` **rc3 / Cannot get process list**。见 `results/preflight.json`。

因此没有启动 launcher，没有使用 --help，没有新增宿主窗口或真实宿主进程，没有全局 kill。已有桌面残留状态 **UNKNOWN**，不能声称“桌面无残留”。环境阻塞需要可用的隔离启动及进程/窗口核验通道；当前授权已经覆盖本地测试，**不需要 Abram 新授权**。

Store CLI 是已读源码、固定本地路径的非 GUI 工具；只对 review-r2/store-test 副本执行，无网络和宿主启动。隔离数据篡改后已恢复原字节。本轮无 keygen/certify/sign-manifest/publish/listing，复用当前签链；独立查看 r2/keys 为空，作者 keys_deleted 只作为作者记录，未冒充本轮删除操作。没有模型配置、push、上传、公开部署或消息发送。

边界偏差：首轮定位误读项目外 memory registry，随后停止，未作为本轮结论依据；最小复现脚本首跑根路径层级错一层，尝试读取不存在的项目外路径后失败，已修正并重跑。不能写成本轮绝无项目外读取。审查产物、测试数据和全部写入均在项目内。

## 必需检查与上一轮缺陷闭合

|检查|独立步骤与期望|实际|结果|证据|
|---|---|---|---|---|
|D-M1-01 刷新错误|检查可执行 set_visible、r1→r2 diff、日志和空/选中图；随后原生列表→页签→动作→回读|可执行调用为0；4份作者日志无[E]或该错误；预置选中图列表/概览已有动态内容。作者三份原结果无actions/events；当前home只有seed任务/state，无命令回执|源码报错根因已消除；**原生完整闭合 BLOCKED**|main:1660–1674,1915–2005,2071–2096；candidate-audit.json；作者选中图|
|D-M1-02 生命周期|抽取实际 run_host / _kill_proc_tree AST，以假进程分别注入日志、Popen、线程、getpgid失败；不启动真实进程|日志提前打开修复；线程失败且PGID可用时清理成功。getpgid失败时仅wait两次，未killpg/terminate/kill，仍alive；异常还被finally return抑制|**FAIL，P1未闭合**|driver-failure-injection.json；cleanup-minimal-reproduction.json；驱动:294–339,376–408,454–512|
|D-M1-03 筛选索引|核对helper使用filtered索引并同步ID/兼容下标；复算仅B收藏、B/C前后导航|4条索引轨迹全部符合预期；没有再交未筛选列表取np|源码根因已消除；原生导航 **BLOCKED**|main:1069–1083,1182–1193；selection-source-traces.json（Python逻辑复算，非OctoScript执行）|
|本地 catalog / install_staged|复制当前签名包/catalog，固定官方探针安装、重建Store may_run；篡改副本再恢复|rc0 / rc1 digest mismatch / rc0；当前digest一致|**PASS，Store层**|local-store-validation.json；M0/r10/install_probe/src/main.rs:70–102|
|亲自原生窗口交互|必须先通过隔离预检，后台启动后核验关闭|rc71 + rc3，未启动|**BLOCKED**|preflight.json|
|desktop v2 / 保留修改|只检查共享详情、任务选择及受影响布局；比较源码/作者图|头部、导航、列表、三页签、概览可见；17命令体保持。选中图行动区未显示；窄图底部被dock遮挡。截图不能证明可滚动到动作|源差异检查PASS；交互/完整视觉 **NOT_RUN**|r1-to-r2-main.diff；原选中/980图；A-M1-02继续挂账|
|UI / 命令边界|核对改变的显示/选择函数及原动作入口|本轮页签仅写显示，选择写ID与兼容下标；17命令不变。未实际执行命令或回读权威回执|新增源码子项PASS；运行 **NOT_RUN**|candidate-audit.json；main:1682–1707；保留A-M1-03|
|项目/迟到回包、输入与焦点|复核上一轮A-M1-01/03涉及路径，无无关扩审|本轮未改变这些路径；未独立运行；搜索仍诚实显示占位|**NOT_RUN**；建议挂账|r1 Review A-M1-01/03；r1→r2差异|
|字体、长文、放大、错误区|目视作者选中/980原图，核对PNG维度与SHA|概览中文可辨，列表长文裁切；1440/980 PNG完全相同，均2560×1268全桌面图；没有150%或错误态操作证据|**NOT_RUN，完整范围**；A-M1-02|candidate-audit.json；作者原图。目视作者图不等于本轮原生操作|

### 本模块全部硬验收

按 Abram 最新“只把核心或安全问题列P1”的裁决保留范围，不把未测项涂成PASS；本轮已存在P1，不满足核心放行条件。

|编号|本轮结论与范围|
|---|---|
|1 真宿主打开、三个视口/放大、动作/错误/返回可达|**BLOCKED（独立运行）**。作者启动/截图仅作交付证据；实际视口、滚动后动作、错误/返回与150%未核验|
|2 稳定task_id、无权限项目切换、迟到回包|筛选索引根因已修；**NOT_RUN（完整）**。没有真实前后导航、项目切换、重开或迟到回包记录|
|3 中文输入、未保存、焦点、可理解错误/对比实测|**NOT_RUN**。中文Label可读不能代替输入/焦点。作者“留M3”是计划，未据此宣称本硬验收已通过|
|4 角色/状态动作、诚实不可用|**NOT_RUN（完整）**；显示/命令边界未新增绕过，附件不可用说明保留；真实角色动作与拒绝恢复未独立操作|
|5 空态/选中/错误/窄窗原图|已有作者空态/预置选中截图；**NOT_RUN（完整）**，没有真实错误态，窄窗大小不由文件名证明|

### 相关既有用例

使用 `docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md:72,82` 与 `10_UI_UX_SPEC.md:173–183` 原定义；不采用CONTEXT/作者报告里将U07/U08重命名为中文输入的缩减解释。

|用例|完整范围结果|本轮复核 / 缺口|
|---|---|---|
|T18 可见任务事件/列表/搜索/附件防探测|NOT_RUN|筛选索引源码已修；未跑权限负例；可信身份按M2延期|
|T28 同task_id原生操作、回读、重开保留|BLOCKED|Store重开准入通过，不能代替工单命令回读；seed预置不是命令产生事实|
|U01 三角色首屏待办、阶段、下一处理人|NOT_RUN|预置概览图可读；未运行三角色首屏/操作|
|U03 三角色事实一致、按权限动作、禁止自验|NOT_RUN|17命令体保留；真实角色/授权回读未跑|
|U07 重复点击、丢包、冲突、离线输入/身份保留|NOT_RUN|本轮仅测试驱动生命周期失败，不冒充业务失败恢复|
|U08 空态、长文、附件失败、无权限、过期建议出口|NOT_RUN|作者空态图可读；后续真实出口/恢复未跑|
|U09 1280/窄窗/放大动作与错误无裁切|NOT_RUN|两个不同视口命名为相同PNG；150%缺证，不沿用作者PASS|
|U10 键盘主流程、焦点、多状态线索、对比实测|NOT_RUN|没有本轮原生键盘/焦点/对比证据|
|U11 真宿主滚动、输入、面板稳定、真实反馈|BLOCKED|set_visible源码根因消除；页签/滚动后点击与输入运行仍被环境阻断|

## 缺陷与具体修复清单

### D-M1-02 — P1 / 必修 / 未闭合：PGID查询失败后不发终止信号，隔离启动未作有效检查

- **文件与行号**：`runtime/optimization/2026-10-09/M1/r2/probe/install_and_host_m1r2.py:294–339`，重点304–330；隔离预检220–238、真实Popen381–383；结果采集454–512。
- **最小触发**：执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M1/review-r2/reproduce_cleanup.py`。它仅抽取提交的 `_kill_proc_tree`，假Popen保持运行，getpgid抛PermissionError，wait抛TimeoutExpired；无真实进程或信号。
- **实际/预期**：实际调用 `[getpgid(fake), wait, wait, stdout.close]`，`sent_any_termination=false`，`still_alive_after_kill=true`。预期：即使PGID获取失败也尝试终止本次已知进程，等待并按需升级终止，明确报告清理失败，不能仅等待后返回。
- **根因**：pgid=None时两处killpg均被跳过，缺少Popen terminate/kill后备；忽略已知 `start_new_session=True` 的组信息。finally末尾return又抑制日志/Popen/线程启动异常，注入结果中原异常为null，缺错误来源。仅设置环境变量、运行无sandbox的true/echo不能证明宿主任意缓存写入被限制；r2没有兑现r1要求的隔离预检失败禁止启动。
- **影响**：测试异常路径可能保留本轮launcher窗口/进程，直接违反用户立即回收的硬约束。没有据mock或作者mtime断言已经发生项目外写入/真实残留。
- **证据**：`results/cleanup-minimal-reproduction.json`；`driver-failure-injection.json` 的thread_start_and_getpgid_failure；其余4项无fake残留。真实后台清理验证仍BLOCKED。
- **具体改法（仅此缺陷范围）**：保存本次进程/进程组身份；PGID查不到或killpg失败时，调用本次Popen的terminate→wait→必要时kill→wait，保留对其自建子进程组的回收检查；不得全局pkill。完整捕获初始化异常并保存error，不在finally中return抑制原错误。启动前验证能限制项目外写入的实际隔离机制，失败即BLOCKED且不创建launcher；不能把普通true成功改写成隔离成功。汇总必须同时检查`still_alive_after_kill`/cleanup_errors/本次PID存活/残留UNKNOWN，而非只看全局pgrep。
- **验证方式**：复跑现有5项注入及单独getpgid失败、TERM失败/KILL升级；所有创建的假进程被终止或明确FAIL，错误来源可读；再在可用隔离运行环境后台启动真实launcher一次，正常/异常两条回收均验证本次PID、子进程和窗口消失。测试全部用本模块隔离路径。

### 其他编号的处置

- **D-M1-01**：不存在的set_visible调用已删除，共享详情根因修复确认；不重开新的业务修复项。原生列表→选择→三个页签→动作→权威回读→重开证据仍待独立复验。
- **D-M1-03**：filtered索引混用根因修复确认，4条源码逻辑复算PASS；真实筛选/边界/分页前后导航与回执目标一致尚未运行。
- **A-M1-01/02/03/04**：均保留上一轮建议挂账，不单独导致FAIL。本轮A-M1-02补充现场哈希/PNG与报告清单不符、完整硬验收PASS超出证据；应从实际产物生成清单并分清启动烟测/核心交互。其余建议未扩审。

## 判定与交接

- 最终结论：**FAIL**。仅D-M1-02清理/隔离安全必修未闭合；没有因美化、搜索建议、M0挂账、可信身份或模型延期单独判FAIL。
- 精确范围：源码、当前包本地Store安装和驱动异常注入已独立检查；**没有本轮原生交互PASS**。解决P1后仍需在可隔离的执行通道闭合核心任务点击、页签、命令回读与重开，不能只交启动PNG。
- 解阻条件：隔离profile或等效限制可执行，进程清点/本次PID与窗口退出可核验；不要求公开发布。本地catalog/install_staged路线已独立可行，无需改走AppHub。
- 延期缺口：G0-B **延期缺口（Abram 已裁决，M2 到期）**；G0-E **延期缺口（Abram 已裁决，M3 到期）**。均不算NEEDS_ABRAM或本轮失败依据。
- 先前模块回归：仅当前签名包在M0既有官方Store路径的正/负/恢复回归与继承清理路径；保留M0原FAIL及来源，不执行后续模块。
- 更新位置：本报告与GATES的M1状态/审查字段/审查历史；原ACCEPTANCE.json不改，不将后端旧PASS转签为原生PASS。原业务代码、作者候选与原始业务数据不改。
- 下一模块：**不允许，不执行**。留在M1，仅修D-M1-02并补核心真实交互闭合证据。

STATUS=FAIL
NEEDS_ABRAM=no
