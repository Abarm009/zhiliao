# M0 独立 Review r10 — r10 候选缺陷闭合复核

- 审查者 / 日期：Codex 主会话唯一审查；2026-10-10T14:33:19+08:00（Asia/Shanghai）。未创建子代理。工具不能查询实际主模型/Router 路由，不能确认 gpt-6.1-sol，也未宣称已经切换。
- candidate_id：`M0-r10-worktree`；base：`M0-r9-worktree`。定位依据为 GATES、CONTEXT、实施 r10 和 CANDI2026-10-10T14:33:19+08:00 的一致指向，不按文件修改时间选择。
- 被审 HEAD：`8d730569546cb57310944bb299695134df773b9d`；工作树仍有 17 项既有修改/未跟踪项，内容清单与 HEAD 分开核对。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M0_IMPLEMENTATION_r10.md`。
- 前置：M0 无前置模块；M1–M7 均 NOT_STARTED，无已通过模块需要跨模块回归。本轮只复核上一轮 D-R8-1/2/3/4、D-R9-1/2/3/4 及直接受影响的安装、表单、清理和验收映射。
- 阅读：AGENTS、CONTEXT_M0、优化 00/01/02/M0/04、Review r9、实施 r10、候选及相关脚本/源码/证据。遵守后续轮效率约束，没有从头重读全部历史实施文件；未读取项目外记忆或技能文件。
- 环境：macOS，zsh；使用项目内保留的离线官方 App Hub 契约与工具，不联网、不上传、不发消息、不配置 provider、不部署、不 push、不执行 publish/listing。
- 宿主：选定 `desktop-v0.1.0-rc.1` macOS aarch64；实际为官方源码在本地打包、linker ad-hoc 签名，非已核验 CI/notarization 成品。路径为用户指定 r3/host/app-extracted/OctoSense.app。字节已独立复算。
- 快照：`review-r10/results/start-snapshot.json` 共 314 个文件；结束核验 `end-verification.json`。审查证据均在项目 `runtime/optimization/2026-10-09/M0/review-r10/` 内。
- 已运行：现场哈希；隔离 true/echo 预检；catalog 正/负验签；两包官方 install_staged、Store 重开 may_run、脚本篡改拒绝、manifest 失配拒绝、恢复重试；启动驱动日志打开失败的源代码 mock 注入。
- 未运行：本轮 launcher、真实桌面输入/滚动/保存/重开、宿主文件选择/权限、提醒、业务事务并发/崩溃。隔离预检均 exit 71，`sandbox_apply: Operation not permitted`；不绕过隔离启动。身份和模型按用户已裁决延期。
- 进程/窗口：本轮 `host_started=false`，未新增窗口；pgrep exit 3，`Cannot get process list`，现存残留状态 UNKNOWN，不能宣称桌面没有他人残留窗口，也未擅自全局杀进程。
- 对话标题：工具没有本对话 createdAt、改名和回读接口，未以当前日期代替创建日期，未执行重命名。

## 必需检查

下表 runtime 路径以 `runtime/optimization/2026-10-09/M0/` 为基准。**本轮独立运行、读取候选原始证据、源码模拟**严格分开。

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与旧 B 分离|git show HEAD、当前业务文件 SHA/尺寸与候选比对|B 与 v2 可区分|B main 46640 B / 9551239e…；v2 main 55781 B / 8aa1022c…；同为 0.1.0-b 不代表同内容|PASS|start-snapshot.json、candidate-audit.json|
|包/宿主现场哈希|复算工作树、两安装目录、catalog、launcher/kernel|当前清单对应实物|所检查 SHA/尺寸均匹配；来源源码 ID 有抄写错误，列建议 D-R8-3|PASS（字节定位）|candidate-audit.json|
|目标宿主安全运行条件|只在 review-r10 放行写入的 sandbox profile 下执行 true/echo；检查进程清点|隔离可用、可安全启动和清理|true/echo 均 rc71；pgrep rc3 UNKNOWN；没有启动 launcher|BLOCKED|preflight.json|
|离线 catalog 正/负|hub verify 当前 catalog；全零错误 anchor|正确通过、错误拒绝|rc0：sequence2、2 entries；错误 anchor rc1|PASS|cli-store-validation.json|
|官方两包安装/准入|复制 catalog/artifacts 到独立 store-test；r10_install_probe 两个 app_id|固定 Store::install_staged 与重开 may_run 成功|两个包均 rc0、caps storage、hosts空、agent false；digest 为 514b21b7… / dc844840…|PASS（Store 层）|同上；src/main.rs:70–102|
|安装失败恢复|仅修改测试副本 main 注释和 manifest name；恢复后重试|篡改/失配拒绝，恢复成功|两个包各两次 rc1；恢复各 rc0；总计10次 CLI 命令，未生成私钥或执行 publish|PASS（安装拒绝/重试）|同上；不是任务崩溃恢复|
|D-R8-1 业务权威文件|核对 r10 候选四文件、日志与 UI 原图|createDraft 同 task_id 落盘；同 home 重开无重复|四文件存在、同 task_id=1791613206528-1-u-reporter-1、DRAFT；重开未执行，作者也明确未测|NOT_RUN（独立桌面重开）|候选 home/.octosense/apps/octosense-repair；实施r10:§5|
|D-R8-2 最小表单|逐行查绑定/取值/启动恢复，目视两张候选 PNG，检查驱动动作|编辑非预设中文→保存→重开恢复输入框；滚动后可点击|回调字段已补；仍仅启动自动写 PRESET；两张图字节完全相同，顶部横排、操作区不可见、status仍“初始：未保存”；启动读取未给输入框恢复值|FAIL（核心交互交付）|D-R8-2；candidate-audit.json；候选原截图，非本轮截图|
|D-R9-2 清理失败恢复|抽取原函数 AST，用 mock Popen、mock getpgid、对日志 open 注入 OSError|创建子进程后的任何错误都进入清理|错误发生在 try 之前，killpg 未调用，模拟 child 未回收；没有真实进程/窗口被创建|FAIL（源代码失败路径）|driver-failure-injection.json|
|固定模型/附件契约|对照 ba36df05 PUBLISHING/HOST-API、install_staged、业务 manifest/附件分支|区分契约、准入、实际可调用及运行结果|model.complete 契约要求 fast/strong 与 JSON Schema；storage-only 包不证明 model grant；附件仍 bytes0/sha空/ready=false 占位|NOT_RUN（宿主调用）|PUBLISHING.md:287；main.splash:705–715；模型延期|
|原子/并发/权限/提醒|核对真正执行路径，区分 Store、普通fs、业务事务|路线声明不超出证据|未有目标宿主事务/崩溃恢复、撤权、due_at/任务跳回证据；fs普通写读和Store重开不能替代|NOT_RUN（完整范围）|实施r10:§6/§8；D-R9-1建议|
|私钥与数据隔离|检查 r10 keys 与本轮输入哈希；测试只改 review-r10 副本|不留私钥、不动原业务和候选|r10 keys 空；本轮未 keygen；结束所有314个输入文件字节不变|PASS（本轮范围）|candidate-audit.json、end-verification.json|

### 上一轮缺陷闭合表

严重性按 Abram 13:54 最新要求重判：仅核心/安全阻断为 P1；其余建议挂账，不因建议判 FAIL。

|旧编号|本轮复核|判定/属性|
|---|---|---|
|D-R8-1|四个权威文件已补齐、task_id一致；尚无同 home 桌面重开恢复；不沿用作者 PASS|落盘证据问题已补；独立运行/恢复 BLOCKED，继续核对，不新加业务范围|
|D-R8-2|按钮字段补齐；实时编辑保存、启动恢复和可操作表单仍未证实；原图反映核心布局/状态未成立|未闭合，P1 必修|
|D-R8-3|包/digest/catalog/截图实物数字已匹配；host source ID 仍错，r10 mapping 文件未交付|大部闭合；剩余 P2 建议|
|D-R8-4|恢复30行；PRESET_ZH.length仍存在（160行），没有按声明删除|未全闭合，P3 建议；错误是否实际触发未知|
|D-R9-1|实施仍称普通fs“原子写读”，硬验收3部分项PASS超过实际操作；driver末尾无条件PASS|P2 建议，门禁由本Review纠正；不单凭文案判FAIL|
|D-R9-2|后台drain、独立session、rc严格分类已修；Popen后的日志open/部分设置仍在finally外|未闭合，P1安全必修|
|D-R9-3|两个包均官方Store安装，独立正负测试通过|闭合，PASS（Store层）|
|D-R9-4|旧“binary bug/必须公开发布”根因已降级；Remote仅字符串、未运行|上下文主要订正；Remote运行NOT_RUN，P2建议，受本轮隔离阻断|

### 全部硬验收

|硬验收|本轮结论|精确范围|
|---|---|---|
|1 候选输入、目标桌面启动与来源|BLOCKED（桌面独立运行）；字节/Store子测试PASS|候选/宿主已定位；本轮未启动，不能拿作者eval替代|
|2 模型、文件、可信身份、存储恢复|BLOCKED（宿主最小运行）|G0-B/M2、G0-E/M3已裁决延期，不计阻断；普通文件写读候选存在，真实附件/错误恢复未运行；完整业务能力不强推到M0修|
|3 中文可读写最小原生表单、滚动后操作|FAIL|D-R8-2核心可操作表单未成立；真实输入/滚动独立运行BLOCKED；预设自动写盘不等于编辑保存|
|4 隔离数据、未提交修改保留|PASS（本轮范围）|未启动宿主；仅项目内副本测试，冻结输入结束一致；不读取项目外mtime来证明旧轮隔离|
|5 路线支撑后续硬约束|BLOCKED（运行证据）；本地安装路线PASS|官方catalog/Store安装可行，不需要公开发布；宿主运行环境与最小表单/清理仍须闭合|

### 全部相关既有用例

不改原后端 ACCEPTANCE.json；以下为目标桌面形态范围，历史后端 PASS 不转签。

|编号|完整范围判定|证据/未验证边界|
|---|---|---|
|G0-A|BLOCKED（独立桌面运行）|离线签链、两包Store准入/拒绝/恢复PASS；本轮launcher没启动|
|G0-B|延期缺口（Abram 已裁决，M2 到期）|STATE.actor/u-reporter-1及身份按钮均是演示选择，非可信身份；不判FAIL/BLOCKED，不记NEEDS_ABRAM|
|G0-C|NOT_RUN（完整事务）|候选普通fs字节持久化；无事务原子/并发/部分写/宿主崩溃恢复；不称“原子写读PASS”|
|G0-D|NOT_RUN（真实附件）|占位附件不是picker、真实bytes/hash或权限；JSON探针普通写读不是附件；不据源码注释裁定宿主永久缺失|
|G0-E|延期缺口（Abram 已裁决，M3 到期）|固定契约model.complete存在；本轮零provider配置/零模型请求；不判FAIL/BLOCKED，不记NEEDS_ABRAM|
|G0-F|NOT_RUN|reminders资源/链接不证明due_at、重启、唤醒、前台提醒和任务跳回|
|T28|NOT_RUN（完整）|候选createDraft同task_id四文件成立；其余动作及重开恢复未独立执行|
|T29|NOT_RUN|关闭/到期/撤权与授权不残留未运行|
|T32|NOT_RUN|配对过期、重复消费、poll_secret主体绑定/token隔离未运行；不把身份延期写成用例PASS|
|U09|NOT_RUN（完整）|biz原PNG2560×1262；--size参数不是尺寸/150%覆盖证明；不扩审业务布局|
|U11|FAIL（最小表单核心）；完整业务NOT_RUN|D-R8-2；真实编辑/保存/读回/滚动点击未建立|
|P02|NOT_RUN（完整发布）|本地源码打包receipt、字节、sandbox catalog签链可定位；非市场接收、官方签名/上架/计费证明；不要求本轮公开发布|

## 缺陷

### D-R8-2 — P1 / 必修：表单交互、中文编辑保存与启动恢复没有闭合

- 文件行：`r10/probe-form-r10/bundle/main.splash:72–75,81–97,119–160`；`r10/probe/install_and_host_r10.py:369–405`；实施r10:133–152,214–217。
- 触发：按候选启动流程首次/再次启动；检查原run1/run2图及动作配置；重开前使隔离测试保存值与PRESET不同。
- 实际：两张原图SHA均 `ef3f3e5205943448af10be93ea0d6e7561ca093cb105fc7ca7bdf10b5acf2d7e`；顶部从左到右排status/title/长Label/marker，TextInput在窗口右缘截断，保存/读取/滚动区不可见。驱动两轮没有编辑、save、load或tail动作；首次由155行自动写PRESET。启动149–151行只load到CURRENT_ZH和status，输入初始仍是PRESET，没有调用doLoad或给输入框恢复已保存值。
- 预期：最小原生表单可见、可点击；保存非预设中文；关闭重开显示同一值；读回不改文件；滚动到尾部后独立计数变化。
- 根因：把构造脚本对象字段和on_click声明当运行时Widget交互证据；重复读不变的预设文件无法覆盖编辑/恢复。布局具体为何未生效本轮未知，不编造VM解析根因。固定本地Makepad `text_input.rs:2390–2410`提供运行时text()/set_text()，候选却读/写构造对象`.text`；这是需要实测纠正的接口路径。
- 影响：M0最小可操作原生表单核心目标未成立，D-R8-2不能关闭。不是锦上添花视觉问题。
- 证据：本轮candidate-audit.json、对候选原PNG的目视审查、上述源行；本轮桌面复现受隔离BLOCKED，未冒充实际点击。
- 具体改法：仅修M0探针；参照已运行业务bundle的具名控件 `ui.<name>` 路径，以目标宿主可用方法取实时文本/回填；让表单控件在真实窗口内可见；启动时回填已读值；用FIXTURE_ZH或另一非PRESET值做实际编辑保存。去掉自动写PRESET充当成功操作的判据；保持30行与真实尾部操作，不扩写业务模块。
- 验证方式：严格隔离launcher后台启动→Remote或现有可用输入接口改中文→实际保存按钮→读磁盘确认fixture及计数→关闭→同home重开→输入框读回相同fixture；再真实scroll→tail计数改变。保存每阶段截图、动作响应、文件hash及清理结果；不可运行明确BLOCKED，不编PASS。

### D-R9-2 — P1 / 必修：启动后的设置失败仍绕过清理

- 文件行：`r10/probe/install_and_host_r10.py:188–199,201–235,292–361`（try位于子进程创建和日志open之后）。
- 触发：Popen成功后日志open失败（权限/I/O错误），或getpgid/线程设置失败。
- 实际：抽取本候选原run_host函数，mock child/getpgid并让Path.open抛OSError；函数直接传播异常，没有调用killpg；模拟child.returncode仍None。**这是源代码模拟，不是本轮真实launcher失败记录。**
- 预期：一旦创建自己的子进程，后续全部设置/等待/读取失败都进入finally，回收自己的进程组，并保存失败记录。
- 根因：try保护起点晚于Popen和日志初始化；结果也只在全部run结束后写，错误路径不会保证完整落盘。
- 影响：违反测完立即关闭、不能残留窗口的硬约束；已修drain/正常quit不足以覆盖该失败路径。
- 证据：`review-r10/results/driver-failure-injection.json`，cleanup_called=false。原图/日志没有代替本轮失败注入。
- 具体改法：所有可能失败的日志/路径准备尽量在创建进程前完成；从创建子进程起置于try/finally，资源设None并分别清理；保存原始PGID，仅清理自己组；等待/信号失败也保证落盘；保留MATCH/NONE/UNKNOWN分类，不全局pkill。
- 验证方式：不启动真实宿主先复跑日志open/getpgid/drain初始化失败与quit失效的模拟测试，断言每种已创建child均进入有限回收；随后在可隔离环境跑真实launcher正常/失败退出，确认无自己进程/窗口残留。

### D-R8-3 — P2 / 建议：来源ID与映射交付仍有失配

- 文件行：`r10/CANDI2026-10-10T14:33:19+08:00.json:38,52`；`CONTEXT_M0.md:61`；实施r10中引用ACCEPTANCE_MAPPING的声明。
- 触发/实际：CANDI2026-10-10T14:33:19+08:00宿主源码ID为`933abbcf2737eda652acd9cae2a4c9ffc16bfdaec6`（42字符），receipt为`933abbcf2737e652acd9cae2a4c9ffc16bfdaec6`（40字符）；r10/results/ACCEPTANCE_MAPPING.md不存在。`abc 1.26 rust stable`也无当前复核依据。
- 预期：来源字段从receipt和真实构建记录生成；映射若只在实施报告内，明确路径。
- 根因/影响：手填摘要残留；当前字节SHA和独立安装可定位，故不因此判FAIL。
- 证据/改法/验证：candidate-audit.json；按receipt订正ID，引用实际映射或生成它，工具链只写真实记录；再自动核对。

### D-R8-4 — P3 / 建议：声称删除的长度表达式仍存在

- 文件行：探针main.splash:160；CONTEXT_M0:48；实施r10相关删除声明。
- 实际/预期：仍为PRESET_ZH.length.to_string()；删除未验证表达式的声明不准确。当前原图status仍初始，不能据此断言此表达式实际抛错。
- 根因/影响：修复未完整同步，影响说明准确性，非新增核心阻断。
- 改法/验证：删除该表达式或提供目标binary成功证据；字节数由驱动读取UTF-8文件统计。随下一修复轮处理。

### D-R9-1 / D-R9-4 — P2 / 建议：缩减过宽通过声明，Remote能力仍待运行

- 文件行：实施r10:214–218及§6/§8；driver:400–408；CONTEXT_M0:45–53。
- 实际：probe日志eval是tick=false，但报告声称tick=true/1Hz tick；脚本没有该start_interval。普通fs写读仍称“原子写读”；driver在persistence=false或UNKNOWN等结果后仍无条件status=PASS。Remote未实际尝试。
- 预期：子结果与最终诊断一致；失败不能自动成功；普通fs持久化不能证明事务/原子性；字符串接口仅是调查入口。
- 根因/影响：摘要沿用计划；本Review已纠正门禁，不把建议本身升级P1。
- 证据：原launcher日志的5452B eval tick=false；driver源；preflight.json。
- 改法/验证：按实际断言计算结果、写全量失败记录；订正tick/原子措辞。在隔离可用后尝试Remote文本/scroll/snap；失败保留响应与当前binary SHA，不要求公开发布或更换provider。

## 判定

- 最终结论：**FAIL**。置信度：高（源码缺陷、候选原图/文件、官方CLI正负结果）；本轮独立桌面运行能力：未知/BLOCKED。
- 精确范围：M0-r10-worktree 的最小表单与launcher测试清理交付。官方本地catalog/Store路径已独立证明可行，不能把环境sandbox失败写成“本地安装不可行”。
- 必修：仅 **D-R8-2、D-R9-2** 两项P1。P2/P3全部建议挂账，不为它们阻断。
- 解阻：需可执行sandbox-exec（true/echo成功）的本机审查环境、自己进程回收与残留核验条件；之后后台启动用户指定launcher，不使用--help。不得以简单HOME重定向替代系统级写隔离。无需公开publish/listing、provider配置或新业务身份授权。
- 延期：G0-B「延期缺口（Abram 已裁决，M2 到期）」；G0-E「延期缺口（Abram 已裁决，M3 到期）」。不再列NEEDS_ABRAM。
- 后续完整事务/并发/撤权、真实附件、提醒、尺寸/缩放及发布验收挂账；本轮不实现它们，后续模块到期仍需真实验证。本报告不以建议项判FAIL。
- 门禁：只更新GATES.json中M0审查字段、当前结论及审查历史；其他模块/实现字段保留。原ACCEPTANCE.json、业务文件、候选和旧报告不改。
- 是否允许下一模块：**否**。留在M0逐条修上述两项，修后同候选来源提交新编号实施报告/候选，再独立复审。不执行M1。
- 隔离/销钥：本轮无新私钥；r10 keys目录当前为空，历史删除记录保留。没有读取或写入~/.octosense，没有启动宿主，不宣称能确认旧轮全部外部写入/残留。

STATUS=FAIL
NEEDS_ABRAM=no
