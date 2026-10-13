# M0 独立 Review r9 — 候选证据与能力判据复审

- 审查者 / 日期：Codex 主会话独立审查；2026-10-10T13:53:21+08:00（Asia/Shanghai）。本次按用户要求介入复审；工具无法查询实际主模型路由，未确认 gpt-6.1-sol / Codex Router，不以报告文件名证明模型身份。
- candidate_id：`M0-r9-worktree`；base：`M0-r8-worktree`。定位依据是 GATES 的明确 candidate_id 与 implementation_report，不是文件时间。另有 r9/probe-form 与 probe-form-r9，审查的是 CANDIDATE 指向、5306 B 的后者及对应 catalog artifact。
- 被审 HEAD：`8d730569546cb57310944bb299695134df773b9d`。当前工作树含既有 17 项修改/未跟踪项，HEAD 不代表工作树全部内容。
- 作者报告：`reports/M0_IMPLEMENTATION_r9.md`。
- 本轮修复方案：`reports/M0_SOL_r4_1219.md`。文件名按用户指定；不是 r4 候选，也不是对审查时刻 12:19 的宣称。
- 快照：开始记录 `runtime/optimization/2026-10-09/M0/review-r9/results/start-snapshot.json`；结束核验见同目录 `end-verification.json`。业务文件、候选、原验收台账及历史报告均要求逐字节不变。
- 前置：M0 无前置模块。M1–M7 没有已放行模块需要回归，本轮只复验 M0 已声明能力。
- 环境：macOS / zsh；仅使用项目内已有官方源、二进制和证据，离线审查。未读取项目外记忆/技能文件，未联网，未配置 provider，未发送消息，未发布、上传或 push。
- 已阅读：项目 AGENTS、CONTEXT_M0；README / ARCHITECTURE / MIGRATION / VERIFICATION；优化 00、01、02、M0、04 模板；实施 r1–r9、Review r1–r8；r9 清单、签名、安装、日志、截图与映射；固定 App Hub 契约及相关宿主/Makepad 本地源码。
- 已运行：工作区与候选哈希复算；隔离预检两次；官方 hub verify 正/负；官方 Rust Store install_staged、重开 Store may_run；脚本篡改与 manifest 不匹配拒绝；恢复测试副本后重试成功；目标宿主二进制 strings；候选文件存在性、PNG 尺寸、源码调用与清单交叉检查。
- 未运行：本轮 launcher、真实输入/滚动/点击、宿主模型/文件选择、可信身份、任务 UI 重开、权限撤销、配对、提醒与崩溃并发。预检 `sandbox-exec` 均 exit 71，`sandbox_apply: Operation not permitted`。遵守用户限制，不无隔离启动。不得把既有作者日志或 r8 Review 运行冒充本轮运行。
- 进程检查：`pgrep` exit 3，stderr `Cannot get process list`；空 stdout 不是无残留证据。本轮 host_started=false，未创建宿主窗口；现有桌面是否有他人遗留窗口无法核验，没有擅自杀其他进程。
- 对话标题：当前工具缺少本对话 createdAt / 标题设置与回读接口，未执行重命名，也不以当前时间猜测日期。

## 必需检查

以下路径如未加前缀，runtime 路径以 `runtime/optimization/2026-10-09/M0/` 为基准；文档以本优化目录为基准。证据分为本轮独立命令、候选原始材料、历史 Review，三者不得混用。

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|版本定位 / B 与 v2 分离|git HEAD、git show B、工作树 SHA、r9 staging 与安装 manifest 比对|不把 B 内容当 v2|B main 46640 B、SHA 9551239e…；v2 main 55781 B、SHA 8aa1022c…；版本号均可为 0.1.0-b，内容不同|PASS|review-r9/results/start-snapshot.json、candidate-audit.json|
|现场清单准确性|逐项对照 CANDIDATE 和实际文件|digest/字节/路径一致|探针 digest、业务签名 manifest SHA、capture 字节、截图目录、catalog 路径有旧值|FAIL|D-R8-3|
|目标宿主来源|复算 launcher/kernel 与 receipt|源码来源与字节固定|OctoSense 源 933abbcf…；App Hub ba36df05…；二进制 SHA 与 receipt 一致；官方源码本地打包、adhoc 签名，不是已核验 CI/notarization|PASS（来源范围）|r3/network/*.receipt.json、start-snapshot.json|
|目标宿主亲自启动|隔离预检 true / echo 后才启动|预检成功、后台运行、关闭无残留|两次 exit 71；host_started=false；pgrep exit 3|BLOCKED|review-r9/results/preflight.json、start-snapshot.json|
|catalog 签链|hub verify 正确 anchor / 全零 anchor|正确通过、错误拒绝|exit 0：sequence 2 / 2 entries；错误 anchor exit 1|PASS|review-r9/results/cli-store-validation.json|
|官方本地安装业务包|固定 Rust probe 接收 r9 catalog/artifact 副本，重开 Store may_run|digest/manifest/签名校验、固定落点|exit 0，digest 8a638d4e…；.bundles/octosense-repair/bundle；caps storage、hosts 空、agent false|PASS（Store 层）|同上；不是 launcher/UI 重开|
|失败拒绝与恢复|隔离副本追加 main 注释 / 改 manifest name，再恢复各副本|失败不准入；恢复有效副本可重试|两次 exit 1，digest mismatch / manifest not admitted；恢复各副本后两次 exit 0|PASS（安装拒绝/重试）|同上；不证明任务事务崩溃恢复|
|业务 UI 与权威结果|读 r9 原日志、截图、app-data；检查四文件|点击→任务创建→文件落盘→重启同任务恢复|55781 B eval 原日志存在；截图零任务；仅 83 B 初始 state，actions/events/tasks 不存在|FAIL|D-R8-1、candidate-audit.json；r8 Review 正向结果仅是历史佐证|
|最小表单编辑/操作|查 TextInput 取值、按钮绑定、恢复；视觉审查原图|真实编辑被保存，按钮有副作用，重开恢复输入框|三个按钮均未绑 on_click；run_command 无调用；初次自动写 PRESET；load 不回填 TextInput|FAIL|D-R8-2；本轮无实际 tap 注入|
|真实滚动后点击|对照截屏、scroll 源与目标 binary strings|尾部滚动前不可见、滚动后可见并点击改变状态|候选无 scroll / tail-click 成功证据；binary 包含 Remote scroll/text/snap 文档；尚未运行接口|NOT_RUN|D-R9-4、candidate-audit.json；不能以 hit-area 判 PASS|
|模型/附件固定契约|查固定 PUBLISHING/HOST-API/manifest、业务实现|可用性、准入、grant、调用、结果各自取证|storage-only manifest；model.complete 官方契约存在；业务附件是占位条目；不能按注释推断永远无 picker|BLOCKED（文件）；模型依裁决延期|下文验收矩阵|
|原子/并发/恢复/权限/提醒|区分 Rust FS、Splash fs、宿主服务与业务层|路线声明对应真实证据|Rust rename 成功只是 FS 原语；Splash 写读不证明事务；SystemTime 同秒采样不证明可靠时钟；无 reminders 调度/撤权证据|BLOCKED|D-R9-1；r7 probe:102–131、Splash storage:324|
|隔离与既有数据|本轮仅项目内 review-r9 副本；业务/候选/旧报告 SHA 回读|不写项目外，不修改原数据|没有启动 launcher，不产生宿主副作用；测试只改副本；原材料结束哈希核验|PASS（本轮范围）|end-verification.json；不沿用旧报告项目外 mtime 宣称|

补充独立校验：官方 `hub check` 携当前publisher公钥检查探针，exit0、digest `84be7777…`；业务/探针artifact manifest与catalog完整字段一致。带相同catalog检查相同已收录版本时exit1（版本已存在的发布连续性检查），不是Store安装拒绝，也没有执行publish。见 `review-r9/results/probe-contract-check.json`。这不补足探针官方Store安装或按钮运行证据。

### 硬验收逐项结论

|硬验收|本轮判定|精确范围 / 缺口|
|---|---|---|
|1 候选定位、目标桌面启动与来源|BLOCKED|候选定位、宿主 SHA/来源通过；亲自 launcher 启动被隔离预检阻断。既有 eval 日志不代替本轮运行|
|2 模型、文件、可信身份、存储恢复运行证据|BLOCKED|G0-B 延期至 M2、G0-E 延期至 M3，不计失败；真实文件选择/重开、目标应用存储错误恢复仍无必需证据。“如实记录缺口”本身不等于能力通过|
|3 中文原生可读写表单、滚动后操作|FAIL|预设显示和自动写盘不能证明输入操作；三个无回调按钮是确定缺陷；真实滚动点击 NOT_RUN|
|4 隔离运行、既有数据与修改保留|PASS（本轮范围）|所有测试副本在 review-r9；无业务修改；不能确认旧轮所有进程是否已退出|
|5 路线支撑后续硬约束|BLOCKED|本地安装路线独立验证可行，无公开发布授权缺口；原子提交、并发、权限撤销与可恢复提醒路径尚无充分宿主证据，不启动后续模块补做|

### 相关既有用例逐项复核

这是本候选在目标桌面上的 Review 结论，不改写既有后端 ACCEPTANCE.json 的历史状态。

|编号|目标桌面完整用例判定|已证实范围 / 仍缺什么|
|---|---|---|
|G0-A|BLOCKED（运行闭环）|catalog/Store 安装/准入正负与恢复 PASS；本轮 launcher/UI 部分 BLOCKED；不能把 Store 实例重开说成桌面重开|
|G0-B|延期缺口（Abram 已裁决，M2 到期）|UI 明示“演示身份·非登录认证”，STATE.actor 是脚本选择，不是可信主体；没有以 role/actor 下拉框认证。未知真实来源，不判 BLOCKED/FAIL，不记 NEEDS_ABRAM|
|G0-C|BLOCKED|Rust rename 及普通读写仅原语级 PASS；任务事务、并发提交、部分写/崩溃/恢复/错误返回无目标宿主证据；历史 SQLite PASS 不迁移|
|G0-D|BLOCKED|真实 picker、文件来源、真实 bytes/hash、保存/关闭重开、取消/拒绝/错误恢复未测；probe_state JSON 写读不等于附件。main.splash:705–715 仍产生占位证据|
|G0-E|延期缺口（Abram 已裁决，M3 到期）|固定契约 model.complete 要 class fast/strong 与 JSON Schema；storage-only manifest 不能证明模型调用 grant；不配置或更换 provider，不进行计费请求，不判 BLOCKED/FAIL|
|G0-F|BLOCKED|链接 reminders 或脚本 interval 不证明 due_at、跨重启提醒、任务跳回、退出唤醒；同秒 SystemTime 不证明单调/可靠时钟|
|T28|FAIL（候选证据） / 本轮桌面复验 BLOCKED|要求同 task_id 操作并重开恢复；r9 缺 tasks/actions/events、初始 state；r8 Review 能力佐证不可冒充候选交付|
|T29|NOT_RUN|关闭/退出/到期后共享授权撤销与发送者授权不残留未运行；能力阻断明确记录|
|T32|NOT_RUN|配对过期、重复消费、poll_secret 主体绑定、token 不流入脚本未运行；G0-B 延期不自动让 T32 PASS，本轮也不强行实现 M2|
|U09|NOT_RUN（完整）|--size 1280x800 只是 argv；原 PNG 2560×1264，不是 DPR=2 的 1280×800；下方 shelf 遮住草稿按钮；150%/窄窗无证据。观察为测量/遮挡发现，不在本轮修业务布局|
|U11|FAIL（最小探针交互） / 完整业务 NOT_RUN|无回调/错误状态证明探针不满足交互基线；真实输入、滚动、面板切换完整用例尚未执行|
|P02|NOT_RUN（完整发布/展示验收）|receipt 与测试签链已核对；只证明本地 sandbox 包准入，不证明市场展示/官方接收/计费/公开发布。禁用事项保持禁用，不要求公开发布来解 M0|

## 缺陷

严重性以本模块证据/能力门禁影响计：P1 必修；P2 必修同步/可靠性；P3 随修。旧缺陷编号保留便于追踪。所有改法只供下一构建轮执行，本 Review 没有修代码。

### D-R8-1 / P1 / 必需：候选业务操作与恢复证据不存在

- 文件行：`reports/M0_IMPLEMENTATION_r9.md:218,240,266`；`r9/results/ACCEPTANCE_MAPPING.md:16,41`；`r9/CANDIDATE.json:27,92`；`r9/probe/install_and_host_r9.py:355–365,409–410`。
- 触发：检查候选 home 的 actions/events/tasks 与 state；对照 taps@8、退出≥8的条件。
- 实际：三个文件不存在；state 83 B，selectedIdx=-1，准备就绪；截图 0 任务。队列 tap 日志不是执行确认。
- 预期：真实 createDraft 发生，有可解析 task_id、对应事件/动作与状态；重开同候选数据后任务恢复。
- 根因 / 影响：退出条件只看 eval+截图+8s，与 tap@8赛跑；没有结果断言，又把计划点击写成已落盘。T28 和交接不可复现。
- 证据：本轮 candidate-audit.json；历史 r8 Review 已成功操作只证明能力可能成立。
- 最小改法：r10 新 home，点击后等待权威文件/记录/UI 断言；最长等待上限失败即 FAIL，不能固定睡5秒代替断言；独立重启检查同 task_id、状态与文件 SHA。

### D-R8-2 / P1 / 必需：表单按钮无绑定，输入持久化并未接通

- 文件行：`r9/probe-form-r9/bundle/main.splash:54–71,91,94–95,116–129,132–143`。
- 触发：检查三个 ButtonFlat 的事件字段及 run_command 调用；检查 load 后输入框取值。
- 实际：没有 on_click，run_command 只定义未调用；初次 eval 自动写 PRESET；load 仅写 CURRENT_ZH，TextInput 仍 PRESET。`.text` 是脚本对象字段，尚无证据为当前编辑值。
- 预期：用户编辑非预设中文→按保存→保存实时值→重开恢复输入框；滚动后尾部按钮触发可独立辨认动作；读取不写盘。
- 根因 / 影响：将按钮文案当事件绑定，将启动副作用当用户保存，将读出的 Label 当输入恢复。硬验收3确定 FAIL。
- 证据：静态源码和原截图；本轮未执行 tap。Makepad snapshot button.rs:527,570–573 / text_input.rs:675,689–699,2394–2419 显示事件/运行时方法路径；不能据此免除目标二进制实测。
- 改法：新探针显式回调、当前 WidgetRef/事件值取读与回填、save/load/tail 分立计数；去掉自动保存，用不同中文 fixture 验证。

### D-R8-3 / P2（原 P3，本轮发现签名 manifest 错值） / 必需：清单与实物不一致

- 文件行：`r9/CANDIDATE.json:23,25,27,42,92`；`r9/results/offline-signing-r9.json:63–65`；实施报告 r9:218；映射:16,41。
- 实际：清单 manifest SHA d758ed88…，实际 r9 stage/安装均 466b9ca5…；probe digest 写7940c7…而签名结果/当前 manifest 为84be7777…；biz图声称3697511/3.7MB，实际1754961 B；results/frame 路径不存在，实物在logs；catalog旧路径漏apps。
- 预期：唯一机器清单完整 SHA/digest/路径/字节与每一份安装/证据对应，所有被引用文件存在。
- 根因 / 影响：手写摘要沿用旧轮结果。当前实物并非因此被证明混包，但审查者无法依清单还原。
- 证据：candidate-audit.json；catalog manifest 与实际已独立校验。
- 改法：r10 全量从结果生成 manifest，不复制 r9 的旧数值；冻结后再次复算，报告只引用机读记录。

### D-R8-4 / P3 / 随修：状态错误和探针规格偏离

- 文件行：probe main:120,140；CONTEXT_M0:33 对照 probe:74–92。
- 实际：截图 bytes=[Error:NotFound]；String.length 未可用；30行规格缩成8行，没有变更/覆盖说明。
- 预期：没有运行错误；滚动前尾部不可见，有足够内容测试真实滚动。
- 改法：删除未验证长度表达式或用已运行验证方法；字节长度由测试驱动实际读取；恢复30行或提交明确等效覆盖证明，不靠缩短/搬出按钮绕过滚动。

### D-R9-1 / P1 / 必需：硬验收与能力范围仍被“部分通过”掩盖

- 文件行：实施r9:190–198,236–237,250–251；映射:12–13,50–51；审查前 GATES:39–43；r7/install_probe/src/main.rs:102–131。
- 触发：比较验收定义与证据实际层级。
- 实际：普通fs跨重启被称原子写读；JSON写盘被称文件授权路径；未scroll却硬验收3 PASS；G0-C/D写PASS部分。SystemTime同秒前后采样标可靠时钟，没有回拨/持久期限测试。
- 预期：子测试通过可列明，完整必需项有缺口必须 BLOCKED/NOT_RUN；延期仅适用于 G0-B/E。
- 影响：继续文字修复仍可能越级放行。旧 Review 的过宽接受也要纠正。
- 改法：映射逐项记录 route/primitive/runtime/full；补目标宿主最小真实文件和错误恢复证据，否则保留阻断；不要在M0扩写全部M2/M5/M6业务。

### D-R9-2 / P1 / 必需：启动驱动没有真实硬超时和可靠清理

- 文件行：`r9/probe/install_and_host_r9.py:320–321,332–337,357–386,398–400`。
- 触发：子进程不输出、/quit返回HTTP错误或收到请求但不退出、pgrep被拒绝。
- 实际：read1可阻塞使60s条件不被重查；quit_sent无论HTTP/进程退出是否成功都可为true，communicate超时异常被吞后跳过kill；pgrep只取stdout忽略错误。本轮pgrep exit3独立证明空stdout不能判无残留。
- 预期：所有失败路径finally回收自己启动的完整进程组，有限等待、记录退出码；无进程列表权限必须UNKNOWN/BLOCKED。
- 影响：残留窗口和进程可能持续占桌面；这是用户已经报告的实际问题的可成立代码路径，不声称本轮复现四个窗口。
- 改法：日志直接文件/非阻塞读取，monotonic deadline，独立session/进程组；/quit仅优雅退出尝试，随后wait→TERM→KILL始终执行；记录PGID/退出/残留检查完整结果，不全局pkill。

### D-R9-3 / P2 / 必需：探针手工安装不是官方 install_staged

- 文件行：`r9/probe/install_and_host_r9.py:170–178,228–268,278`；probe main注释:5–6；CANDIDATE:94。
- 实际：Python只做部分digest/签名检查后直接copy，未执行官方全部目录/manifest/withdrawn/host-api/OS等准入条件。业务包确实走Rust官方接口，探针包没有。
- 预期：两个包都用同一固定官方Store路径准入，或如实承认探针是手工fixture而不等同安装。
- 影响：探针运行环境与声明路线不完全一致，不能用它证明所有安装/权限语义。
- 证据：官方client.rs:421–473；本轮Store正负成功仅覆盖业务包。
- 改法：r10泛化现有Rust probe，显式app_id/artifact/apps_root/today，正式调用Store；不再复制算法模拟准入。

### D-R9-4 / P2 / 必需：未调查现有 Remote，且 CONTEXT 继续携带被推翻根因

- 文件行：CONTEXT_M0:57–68,74–79；实施r9:197–198；旧Review_r8对应D-R8-2；目标binary字符串；native-build/makepad/platform/src/remote.rs:1791–1793,1979–1983,2174,2180–2188。
- 实际：上下文仍把legacy reader说成rc.1链接事实、要求保留binary bug与NEEDS_ABRAM=yes，已被r7/r9入口证据反转；旧Review仅由test-action无scroll外推没有输入路线。
- 预期：源码快照归属不能由目录名猜测；优先测试实际二进制已经包含的Remote文本/滚动/坐标接口。
- 新证据：目标binary有 `/m?k=…scroll`、`/k?t=TEXT`、`/snap` 说明；这是可尝试入口，不是运行PASS；文本事件注入也不是逐字系统IME证明。
- 影响：后续代理按失效上下文继续追错源/要求不必要授权。用户要求后续只读CONTEXT，更使其失效内容成为重复失败来源。
- 改法：构建方下一轮首先按此Review校正CONTEXT当前结论，保留旧历史出处；隔离宿主内仅loopback尝试Remote，成功后测真实滚动/编辑；不可用附HTTP/超时/响应与当前二进制SHA，记NOT_RUN，不再泛化。

## 判定

- 最终结论：**FAIL**。置信度：高（候选文件缺失、按钮死代码、清单失配、驱动缺陷均直接核对）；本轮新增桌面运行能力结论：未知，因隔离预检失败而 BLOCKED。确定缺陷足以 FAIL，无需把运行缺口伪装通过。
- 精确范围：M0-r9-worktree 的候选交付、最小表单与证据门禁；不裁定本产品永久不能运行。本地catalog/官方Store路径已独立证明可行。
- 必修：D-R8-1/2/3、D-R9-1/2/3/4；D-R8-4随修，全部留在M0。
- 解阻条件：同项目内可执行的严格写隔离环境、后台launcher可启动、自己进程组可回收并可核验残留；真实文件/恢复/提醒等能力的最小证据或明确不可行复现。不能移除sandbox、写项目外、公开发布来绕过。
- 延期缺口：G0-B 到M2、G0-E 到M3，Abram已裁决，不计本模块FAIL/BLOCKED，不再索要授权。
- NEEDS_ABRAM：**no**。剩余问题是实现/证据/执行环境，不是用户未授权公开发布/provider/身份；本地路径并未证实不可行。
- 门禁：仅更新GATES的M0审查字段；review_report指向本报告，附详细方案和证据。保留旧Review完整记录，不改其他模块。
- 原台账：ACCEPTANCE.json保持原样，历史后端/旧原生来源不删除；本报告与M0门禁明确新候选状态，避免旧PASS被移植。
- 是否允许下一模块：**否**。没有执行下一模块、业务代码修复或系统授权变更。
- 修复/解阻执行顺序与逐项可交付标准：见 `M0_SOL_r4_1219.md`。构建方最多READY_FOR_REVIEW，独立Review前不得自置PASS。
