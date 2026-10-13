# M4 独立 Review r3

最终结论：**FAIL**。正式候选 `M4-r3-worktree` 的 **D-M4-03、D-M4-04 仍为 P1 必修**；D-M4-02、D-M4-05 的对应源码子项已改善。只复核 r2 缺陷及受影响回归，不修业务代码、不执行下一模块。置信度：候选字节、锁算法反例、确认控制流高；发行宿主 UI 和权威业务结果未知。

- 审查者 / 日期：当前 Codex 主会话唯一独立审查方，无子代理；2026-10-11，Asia/Shanghai。精确结束时间见 GATES.reviewed_at。
- candidate_id / base：`M4-r3-worktree` / `M4-r2-worktree`，依据 GATES、r3 实施报告和 CANDIDATE 的三方一致指向；没有依据文件时间选版本。
- 被审 HEAD：实际 Git HEAD `8d730569546cb57310944bb299695134df773b9d`；清单为 `WORKTREE-UNCOMMITTED`。主源 SHA-256 `4c753154cf55fb5912a53a5f09425c54bcc5787ee5e54d5d1f82cd8096a50f13`，324049 字节、7131 splitlines 行。清单7130行误差承接 A-M4-01，不单独判 FAIL。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M4_IMPLEMENTATION_r3.md`；原缺陷来源 `reports/M4_REVIEW_r2.md`。
- 快照：`start-snapshot.json` / `end-snapshot.json` 一致；固定源码、manifest、配置、候选、实施报告、账号表/安装映射和宿主/VM 摘要。原账号表及安装映射未改；未读取明文凭据、模型密钥。
- 前置：M3 当前为 `M3-r4-worktree` / **FAIL**，报告 `M3_REVIEW_r4.md`，没有已接受 PASS 候选。按用户前序挂账裁决继续 M4 局部复审，不修 M3、不宣称满足原 PASS 前置。M4-r2 留存源 SHA 与 before_sha256 相同；M3-r4 留存源 SHA 与其独立报告相同，两组增量已保存。当前身份/模型实现包含 M3-r4 差异，不能沿用旧 CONTEXT 所称身份/provider 尚待裁决。
- 实际环境 / 路由 / 宿主：项目终端、本地 `runtime/identity/evidence/vm/target/release/identity-vm-probe`、官方 Hub/Store 安装探针。指定 launcher 为 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`；摘要已固定，但未启动。工具无法核实/切换主会话为指定 Router / gpt-6.1-sol，亦无本会话 createdAt/标题操作接口；未冒称已切换或已命名。
- 已阅读：先读 CONTEXT_M4、实际 AGENTS、00/01/02、M4 指令、04 模板、r2 Review、r3 实施/清单/证据及脚本、M3-r4 当前结论和缺陷涉及的源函数、相关原 T/U 定义；根基线资料仅作历史边界参考，没有展开无关模块或据旧文档验收。
- 已运行：源码与基线差异、重新隔离预检、两个独立进程的锁竞争/释放反例（3轮）、局部 Splash 日期/冲突/准入拒绝/开工守卫/确认控制流探针、当前源码隔离副本离线签名与官方 install_staged/重建/may_run、篡改拒绝和恢复安装。
- 未运行：真实桌面 M3 创建→接单→设备→预约→开工、三角色首屏/键鼠、业务接单与预约确认真正并发、实际权限/时钟注入、权威任务/事件/final 回执、失败和业务重启恢复。重新预检仍 rc71 / rc3，不能保证宿主隔离/回收，因此不启动 launcher、不用 `--help`；本轮无新增宿主窗口，前序残留窗口 UNKNOWN。
- 数据与副作用：本轮测试/日志/缓存/签名/合成状态在 `runtime/optimization/2026-10-09/M4/review-r3/`；子进程 HOME、CFFIXED_USER_HOME、TMPDIR、XDG目录、OctoSense app-data、Metal缓存均重定向。未原样运行会覆盖作者证据或使用系统临时目录的作者脚本。没有手改原业务数据推进成功链。真实模型请求0次，未观察余额/402错误；未联网、上传、公开签名、publish/listing、push、消息、Issue/评论或部署。
- 审查过程偏差：开场对项目外记忆索引做过一次只读搜索，违反用户本次读取边界；没有项目外写入，后续显式内容读取限项目内。此项如实披露为过程偏差，不编造为候选业务缺陷；结论依据本轮项目内证据。

证据根为 `runtime/optimization/2026-10-09/M4/review-r3/`，下文 JSON / diff / log 位于其 `results/`；独立脚本与 Splash 测试副本在证据根/`probes/`，没有修改业务源。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、前置、增量|核三方交接，计算r2留存/当前/M3-r4摘要并生成diff，结束再核|唯一候选、可定位差异、已接受M3|r3明确且无漂移，前置M3 FAIL；角色动作/命令边界继承M3-r4|定位成立；前置未PASS|start/end-snapshot、affected-regression、M4-r2-to-M4-r3.diff、M3-r4-to-M4-r3.diff|
|硬1 / D05资格和设备|抽取实际开工前导守卫，合成合法对照、撤角色/技能/身份到期、归档、旧技工等|合法可进边界，资格变化/无效设备拒|合法true；撤角色、技能、身份、归档、旧技工均拒；撤服务关系进入拒绝分支后局部VM join错误|资格子项关闭；完整原生BLOCKED|vm-probes.start_*、source-traces.startProgress|
|硬2 / D02改约|实际排除数组与改约准入前缀；仅CONFIRMED、双预约、跨项目、准入拒绝|同任务被替换预约不自冲突；拒绝前不改预约|仅旧确认可到准入；跨项目重叠拒；准入false后原CONFIRMED/PROPOSED及version均不变|r2源码缺陷子项关闭；完整T12 BLOCKED|appointment-probes、vm-probes.conflict_and_dates|
|硬3 / D03真并发|两个不同PID；A取得锁保持临界区，B再rename/readback；A释放时B仍持有|只有一个持有者；释放不清别人锁|3/3均A、B同时acquired=true；A释放移走B锁|FAIL算法；真实双业务命令BLOCKED|concurrency.json、probes/lock_worker.py|
|硬4 /有效预约开工|实际前导守卫：合法、未到时窗、end边界、旧承接者|缺合法时窗/旧承接者不可开工|合法通过前导；未到、end==now、旧承接者拒绝；未执行commit|守卫子项成立；完整原生BLOCKED|vm-probes.start_*|
|硬5 / D04旧AI及重新确认|旧未确认草稿失效；正常新输入、重复确认、关闭重开重填；追实际失效置位/复位|旧内容拒，新内容可核对后继续|旧内容现已拒；普通新输入首次/再次false；关闭重开重填仍false；未改输入对照true|FAIL核心恢复出口|vm-probes、source-traces.editRawText/confirmDraftModelBound/closeDraftPanel|
|D01时区回归|实际日期helper算上海00:00-01:00，对照独立Python datetime UTC+8；核原非法日guard|UTC毫秒准确，日期校验保留|2026-10-12得到1791734400000/1791738000000，与标准对照一致；helper与r2相同|关闭子范围保持；原生输入/星期显示BLOCKED|independent-date-reference、vm-probes.conflict_and_dates、affected-regression|
|三角色首屏与错误出口|对mainAction/secondaryActions及相关详情做受影响源码比对；新隔离预检|真实屏幕可说明阶段/下一处理人，有可继续错误出口|两个动作函数与r2相同；没有本候选屏幕、键盘/回执；D04错误出口循环|BLOCKED真实UI；D04 FAIL|affected-regression、preflight、vm-probes|
|权威结果及失败恢复|追runCommandBound、commitBound和预约冲突位置；拒绝前缀反例|同一边界重读所有相关任务并提交，失败可对账|只读目标task版本；冲突遍历TASKS发生在锁前；实际回执/事件/业务重启未跑|D03未闭合；其余BLOCKED|source-traces、appointment-probes|
|本地catalog/install_staged|当前源隔离打包→keygen/certify/stamp/sign/verify→官方install_staged→重建/may_run→篡改→恢复|本地路径可行、篡改拒绝、私钥删除|安装/恢复rc0；篡改rc1；安装三份源文件字节匹配；私钥剩余0|PASS安装层，仅该副本digest|local-store-validation、end-snapshot|

### 证据范围与限制

1. 局部 VM 是项目现有 Makepad-script/受限文件系统测试器，**不是指定发行 launcher**。开工探针抽取原函数到业务突变前，以 `return true` 表示通过前导守卫；外部身份、时钟、选择对象均合成。true不代表实际开工，null表示函数提前返回。撤服务关系用例在错误字符串 `.join` 处 rc1，不能算完整错误出口通过，也不据此宣判发行宿主缺少该方法。
2. 确认探针依赖合成事实守卫和创建结果；为绕过既知本地VM `ok`属性冲突，**仅测试副本**将 `_g.ok` 改为 `_g.good`。合法未编辑对照true；其他同一对照只因失效标记false。它证明确认控制流与恢复断路，不能宣称真实M2成功/拒绝已经执行。业务源未改。
3. 改约探针运行原排除helper及原改约前缀到 `runCommandBound`，身份/时间解析/准入为桩；没有执行提交、回执或真实版本冲突。D02源码子项闭合不等于完整T12。
4. 双进程实验执行实际POSIX rename/readback/release步骤，两个进程同时保持临界区，足以否定互斥声明；**不是原生双接单/双确认**。抽取原锁函数在本地VM另报 `variable _ not found in scope`，该API运行探针不确定，不从中断言发行宿主支持/不支持rename。当前本地源码的文件系统模块也未注册rename；构建方仍须在指定宿主验证实际可用原语。
5. 离线签名副本 digest=`d2f6068ee09790a8264b98cbfdd0bda2c4208e4ed15917cdd88e72bd384c43ec`；不是原manifest历史digest。`may_run`仅有storage/空hosts，不证明身份登录、模型或业务运行。`store-test/keys/working.key`和`anchor.key`在finally删除，`keys_deleted`记录两路径，结束再次核为空。私钥未输出/入报告；没有公开发布。
6. 作者18/18为关键词位置检查，13/13为另写Python模拟。其 `behavior_probe.json` 已同时记录 `A_won_first_readback=true` 与 `B_won_after_overwrite=true`，却作为通过条件；不能继承为并发验收。没有覆盖作者原证据。日期和guard子范围改善也不升级完整T/U为PASS。

### 相关既有用例逐项复核

修复轮只查旧缺陷涉及范围及受影响回归；原定义保留。以下所有完整原生用例均 **BLOCKED**，附局部实际结论；没有用源码/探针代签完整验收。

|用例|本轮复核及证据|
|---|---|
|T04|两个独立连接抢同OPEN只一承接者/事件：D03锁反例FAIL；真实接单/成功事件未跑。|
|T05|错技能/无项目权限拒、经理事件记经理：原角色/技能边界可定位；D05资格反例局部拒；真正接单/分配事件未跑。|
|T06|SCHEDULED改派取消旧预约、ACCEPTED、新技工、旧技工拒：旧技工开工前导拒；改派源码与M3-r4相同；实际改派/回读未跑；旧确认恢复D04。|
|T07|设备编码/asset载荷同对象、假/跨项目/归档拒：归档前导拒；编码/载荷解析NOT_RUN，不能代签。|
|T08|有效服务空间可绑定、仅安装相同不自动通过：services关系保留；撤服务关系拒绝分支在局部VM错误出口不确定；真实绑定/读回未跑。|
|T09|缺设备不准开工、维修中不能自换、经理更正旧新值/理由：原设备guard保留；当前角色/技能拒绝改善；实际写及经理更正未跑。|
|T10|提议不直接SCHEDULED、非原报修人不可确认：源码原提议/主体guard保留；真实命令/权限反例未跑。|
|T11|同技工重叠并发仅一、相邻可、跨项目仍冲突：实际helper跨项目true/相邻false；D03两PID持锁FAIL；真正双确认及权威预约读回未跑。|
|T12|改约待确认保留旧确认、新确认替换、拒绝保留：D02同任务排除/拒绝前不突变已改善；成功提交/确认/拒绝全链未跑。|
|T13|过期410、无定时器仍拒、伪当前时间无效：confirmAppointment原nowMs/截止分支保留；实际权限/时钟/协议注入NOT_RUN。|
|T14|上海换UTC、模糊时间具体核对、end<=start拒：实际日期helper与独立标准对照一致，原validate保持；真实输入/显示/规范化读回未跑。|
|T15|旧version409刷新不覆盖、不可任意百分比：目标version读回源码继承M3-r4，D03权威全量/并发缺口仍在；真实错误和刷新未跑。|
|T31|取消释放预约留事件、终态不开工/验收、新故障关联：取消/终态守卫未无故改动；实际取消/事件/重建未跑。|
|T35|生成中改派/改约，旧角色版本建议不能执行：旧未确认草稿已标失效并拒；D04更新后重新确认仍被锁死；完整异步/主体反例未跑。|
|U01|三角色首屏可找到待办并说明阶段/下一处理人：动作函数保持；真实首屏NOT_RUN，A02挂账。|
|U03|三角色事实一致、按权变化、承接者不自验：真实多会话查询/屏幕/回执NOT_RUN。|
|U04|旧确认与新改约区分、冲突/过期不假成功：D02前导改善；真实屏幕/提交/失败反馈NOT_RUN。|
|U05|安装位置与服务空间分开、来源可读：真实投影NOT_RUN，A02挂账。|
|U07|重复点/丢响应/version冲突/离线输入任务不乱：D03互斥FAIL、D04恢复FAIL；真实UI/丢响应/重启NOT_RUN。|

## 缺陷

### D-M4-01 — 日期算术/非法日源码子范围 CLOSED，原生 BLOCKED

- 原r2修复范围保持；helper与r2相同，新增上海00:00的实际Splash/独立标准对照通过。星期/完整日期屏幕属于A02及原生待测，未扩为本轮P1。

### D-M4-02 — r2两个源码子项 CLOSED，完整改约/恢复 BLOCKED

- 文件/行：`app/bundle/main.splash:1891,3987,4000,4173,4194,4206,4213`。
- 排除数组明确包含当前同任务CONFIRMED和PROPOSED；仅旧确认的重叠改约可到准入。旧PROPOSED的SUPERSEDED循环已移到准入通过后。
- 独立反例：准入false时两旧预约仍CONFIRMED/PROPOSED、version=5；跨项目另任务重叠拒，准入调用0次。证据 `appointment-probes.json` 和 `source-traces.json`。
- 关闭的是旧自冲突及准入拒绝前突变；提交/失败恢复沿D03和原生BLOCKED处理，不声称完整T12通过，不要求修无关预约功能。

### D-M4-03 — P1 / 必修 / OPEN：rename替换不能互斥，冲突仍在锁外

- 文件/行：`main.splash:2062,2066,2077,2087,2094,2100,2115,2153,4035,4047`；作者 `runtime/optimization/2026-10-09/M4/r3/scripts/m4_r3_behavior_probe.py:137,170,179` 附近的顺序测试及其通过条件。
- 触发：A写tmp→rename→读回自己→保持临界区；B写自己的tmp→rename同目标→读回自己→也保持临界区；随后A释放，B尚未退出。两个不同PID，连续三轮，分别A/B为38215/38216、38217/38218、38219/38220。
- 实际：每轮A、B均acquired=true，B原子替换A的锁；A随后将B当前锁rename走，lock不存在而B仍在临界区。预期第二者在第一者释放前必须失败，释放只影响自己的持有权。
- 根因：rename是可覆盖目标的原子替换，不是create-if-absent/CAS。rename与后续read不是一个原子操作，已读成功的A不会因B后来替换而自动退出。同账号tmp/stamp也非跨进程唯一。释放不核持有者。作者自己的两者成功日志被错误当作PASS。
- 影响：无法保证一次接单/确认只一成功；过期快照可并行提交/覆盖他任务，释放可破坏别人锁。即使修锁，confirmAppointment冲突循环仍在runCommandBound之前只读内存TASKS；边界只查目标任务version，另一任务预约变化不会令该version变化。
- 证据：`concurrency.json`（3/3双持有、误释放）、`probes/lock_worker.py`、`source-traces.runCommandBound/confirmAppointment`、作者behavior_probe.json。原生T04/T11未运行；不把文件算法实验写成真实业务双成功。
- 具体改法：在选定宿主实际可用的互斥/串行事务原语中，覆盖授权→读取全部相关权威任务/该技工跨项目预约→校验→任务/事件/回执提交；释放校验持有权且finally覆盖异常。不要继续用rename或write/readback声称CAS，也不要仅加预读exists。若宿主无可验证原语，交付最小复现并记BLOCKED，不能未裁决自行加业务服务。
- 验证：先使本轮确定性交错只一持有、旧持有者不清别人锁；再在两个实际独立上下文接同OPEN/确认同技工跨任务及跨项目重叠只一成功，相邻都成功；逐写点失败/崩溃/响应丢失/重启核权威回执和无残留锁。仅目标version检查不够。

### D-M4-04 — P1 / 必修 / PARTIAL：旧内容已拒，但新内容无法重新确认

- 文件/行：`main.splash:1941,1945,3136,3207,3217,3223,3254,3265,3279,3509,3512,3543,3565`。
- 已改善：m4_invalidateConfirmation现在不依赖last_confirmed_at_ms；未确认旧草稿也被标失效，APPLIED→EXPIRED，后续confirm拒绝。此安全子项保留，不要求恢复旧漏洞。
- 触发：普通手工新描述或合法编辑；confirm入口同步TextInput→editRawText置invalidated=true；随后点击确认两次。另一对照：关闭/打开面板、重填新内容再确认。
- 实际：两次均false，关闭重开重填也false，错误都要求“重新确认新内容后再点确认”；未编辑合法对照true。预期保留新输入、重新核权威主体/事实/版本后生成新的具体确认绑定并能继续。
- 根因：把所有编辑/旧上下文失效放在同一永久拦截位。唯一成功复位位于该位拒绝之后，无法到达；closeDraftPanel虽清位却清掉草稿，重填再次置位。不存在作者所称“close→open→重填可通过”的恢复路径。
- 影响：M3新输入到工单的核心前置及M4改派/改约后继续处理受阻；错误提示形成重复点击死循环。该问题属于r2 D04已经要求的“新内容可重新核对”及受影响M3回归，不是无关扩审。
- 证据：`vm-probes.fresh_untouched_confirm/fresh_manual_edit_confirm/close_reopen_edit_confirm/unconfirmed_stale_invalidated`；原失效/编辑/确认源码。控制流探针守卫和创建依赖合成、_g属性适配已披露，未执行原生创建。
- 具体改法：分别记录失效旧proposal/旧确认与当前编辑版本；明确提供转手工/核对更新内容并重新确认入口，在新版本上刷新主体/授权事实/到期/任务版本并形成新绑定。只在新绑定核验成功后消费，保留旧失效审计；不要无条件清旧AI标记绕过安全守卫，也不要要求清空所有输入重新填。
- 验证：原文初次输入、字段编辑、AI采纳后编辑、改派/改约/解绑/撤权的旧建议均不得执行；新人工内容能经真实UI重新核对继续，不手工改运行数据。检查保留输入、命令/权威task/action/event一致及失败后可恢复。

### D-M4-05 — 当前技工资格源码/局部守卫子范围 CLOSED，完整开工 BLOCKED

- 文件/行：`main.splash:4240,4256,4258,4259,4263`。
- 资格校验已补；合法对照通过前导，撤角色、撤技能、身份无效、旧assignee都提前拒。原设备有效性守卫保留。证据 `vm-probes.start_*`。
- 身份/时钟为合成依赖；原5账号的真实登录和每次权威权限刷新未在发行宿主运行。撤服务关系错误出口局部VM不确定，完整结果未知，不将本项宣称真实授权PASS，也不新增P1扩审。

### B-M4-01 — 必需运行 BLOCKED：强制隔离和进程清点不可用

- 证据：`preflight.json`；`sandbox-exec -f review-r3/isolation.sb /usr/bin/true` rc71，原文 `sandbox-exec: sandbox_apply: Operation not permitted`；pgrep rc3，原文 `pgrep: Cannot get process list`。
- 期望：可验证强制写入限项目隔离目录、禁网络，且能盘点/关闭测试自身进程和窗口。实际条件不成立；只设HOME不足以证明宿主所有写入遵守边界，所以不启动。
- 解阻：提供满足该隔离与回收条件的本地执行环境，后台运行指定launcher，try/finally关闭自身进程并确认无残留窗口，再执行本轮必需业务/三角色/恢复反例。无需新的Abram授权；不能用旧截图或作者模拟代签。

### 建议继续挂账，不以建议判 FAIL

- A-M4-01：清单行数误差、证据路径与模拟PASS含义应按真实文件重新生成；本轮已固定实际字节/摘要，未把建议升为P1。
- A-M4-02：三角色首屏、日期/当前预约与新提议显示、安装空间及错误出口的真实投影未测；不做视觉锦上添花，不以建议单独FAIL。核心原生验证仍是必需BLOCKED。
- A-M4-03：previous_assignee历史建议保留，不扩修历史系统。

## 判定

- 最终结论：**FAIL**；精确范围为M4-r3固定候选、r2缺陷闭合及受影响回归。D03/D04为剩余P1；核心原生链另为BLOCKED。不是“基本通过”。
- 必修清单：D03真正互斥及同边界权威跨任务冲突核验；D04保留失效旧内容同时允许新版本重新核对/确认。D01/D02/D05局部改善保留，完整原生项尚未通过。
- 受影响先前模块：已定位M3-r4→本候选差异，正常新输入确认回归发现D04；原生权限/创建/权威回执回归BLOCKED。M0～M3及其他模块结论保持，未为它们改账。
- 门禁位置：只更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的M4 status与审查字段，review_report指本报告，替换前审查字段归档。作者构建字段保留为作者声明；`docs/build-loop/ACCEPTANCE.json` 不改，历史后端/旧版本来源保留，不能被本轮局部探针覆盖。
- 是否允许下一模块：**否**；不执行下一模块。
- 留在M4的修复/解阻指令：仅修D03/D04及对应回归；提供安全宿主运行环境后，重跑真实M3工单→开工、跨主体权限/时区/过期/真业务并发、改派改约失效、三角色首屏和失败恢复。冻结新candidate_id/清单/宿主配置再交接。
- NEEDS_ABRAM=no：身份来源/MiniMax已裁决；本地catalog/install_staged成立，离线签名已授权且私钥已删除；剩余为代码与执行环境，未有付款错误或需公开发布的缺口。

STATUS=FAIL
NEEDS_ABRAM=no
