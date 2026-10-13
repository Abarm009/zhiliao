# M3 独立 Review r13

**最终结论：FAIL。正式受审候选仍为 M3-r9-worktree；D-M3-02 保留 P1。** 正式包在 rc.6 上仍误判合法输入并清空恢复字段。当前共享修复的原文/意图恢复正例已有独立原生证据，但尚无新 M3 正式候选交接，不能把共享改善归给旧包。AI、手工合法确认链分别 NOT_RUN，不能给模块 PASS。

置信度：版本绑定、盘面恢复、隔离记录及正式包 D02 失败 **高**；长输入异常的完整调用栈/模型实际效果 **未知**。

## 审查对象与边界

- 唯一审查者：本主会话；日期 2026-10-13，Asia/Shanghai。未委派代理、未修业务代码、未启动下一模块。主会话 Router 路由和指定模型无法通过现有工具核实/切换；没有可用的当前线程 createdAt/标题写入接口，未声称完成这些操作。
- 第 1 段笔记：`runtime/optimization/2026-10-09/M3/native/REVIEW_NOTES_r1_1659.md`；请求：同目录 `REQUEST_review_r1_1659.json`，SHA256 `2a46092eaa2bc6314461b5b5271cadc8ffcffd3845b90020187527683fbc76d2`。本次第 2 段消息给出的证据路径为“无”，没有新执行证明；实际从项目内定位并核验了已存在、request 全等的运行，明确采用其记录的时间，不冒称刚执行。
- 实际证据 **H/**：`runtime/optimization/2026-10-09/M3/native-runs/review_r1_1659_REQUEST_review_r1_1659/`，运行记录为 **18:24:29–18:26:53 +08:00**。审查材料 **E/**：`runtime/optimization/2026-10-09/M3/native/review_r1_1659/`。H 为 review 请求运行，不是作者自测替代品。本审查只读取 H，不覆盖或重跑。
- 正式交接来自 GATES、`reports/M3_IMPLEMENTATION_r9.md`、`M3/r9/CANDIDATE.json`：**M3-r9-worktree / base M3-r8-worktree**，main **657584 B / c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421**，digest **77b95f2eb1ecc5c97cc109e46cda7ccbb3276ac52f99b4f840cad8150d1adf6b**。本轮一场正式包对照；正式源码行号指 E/formal-r9.source.main.splash。
- 另七场是独立冻结的**共享观察性对象**，不冒造 candidate_id：当前 main **765252 B / ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e**，运输 digest **1bd2bfc2fb541066604638a4ae3a8c7acef409427c5845b72b396944e4833f03**。当前源码与 E/shared.source.main.splash 全等。已提出正式 candidate_id 澄清但未收到新交接；未按文件时间选版。HEAD 两者均 `8d730569546cb57310944bb299695134df773b9d`，dirty，不能只用 HEAD 标版。
- 前置：M2 r18 **仅 JSON 读取差异 PASS**，整体按 Abram 最新裁决 carried 结束；GATES 仍为 M2 FAIL/r17。本轮不制造整个 M2 PASS、不重开 M2。D-M2-05/D-M4-03 按裁决为 BLOCKED-HOST，不计 P1、不作为 M3 FAIL 原因。
- 实际宿主 rc.6：`runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 **2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a**。harness SHA **8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7**，profile 模板 SHA **76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f**。均从实际文件重算，不启动宿主。
- 已阅读范围继承第 1 段的实际 AGENTS/CONTEXT、00/01/02/M3/04、r9 实施/清单、r12 缺陷、M2 r18、HARDFIX_PLAN 相关边界及相关源码；第 2 段完整读取八份结果、日志、denials、profile、manifest、权威盘，复核冻结差异。只复核 D02 及相关原编号/回归，不扩审。

## 必需检查与独立结果

|检查|独立操作 / 期望|实际|结果 / 证据|
|---|---|---|---|
|候选与运行一致|重算请求、seed、mirror/installed/.running 全资源；正式与共享分开|两种运输分别匹配冻结字节；业务根均实际加载|PASS 版本绑定；E/native-evidence-audit-r13.json、H各result/log|
|隔离与回收|逐场核 probes、pre/post、pgid、profile/env/denials|8场 probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN；quit_http/rc0|PASS 驱动记录范围；CLEAN不代表业务成功|
|正式 D02 合法中文恢复|新“西侧三层茶水间滴水”原文，中文/引号/换行/emoji/反斜杠；冷开恢复四字段|1236 B合法state被判坏，主变2207 B默认态，四字段均不匹配；精确boot-bak保源|**FAIL / P1**；H/formal_r9_unicode_control|
|共享正常冷开|空业务盘，加载新读取器，登录根可见|零解析/运行错误，正常登录页|PASS 冷开子项；H/shared_clean_cold；登录后工作台NOT_RUN|
|共享中文及ASCII恢复|中文原文与正式对照相同；ASCII含字面量\\ud800和\\n；核原文/意图/嵌套payload/原key|两场四字段全等、无坏源备份、零运行错误|PASS 共享恢复子项；H/shared_unicode_restore、shared_ascii_literal_restore|
|共享长输入恢复|2826码点 / 6728 UTF-8 B原文，含中文/emoji/换行/反斜杠|四字段恢复一致、无坏备份；log:56出现一次 equality/work/instruction/time limit [E]|数据恢复PASS；零运行错误检查FAIL，建议挂账；H/shared_long_input_restore|
|重复键+不同旧备份|重复pending_input必须整对象拒绝；保本次源、不覆旧bak|1287 B坏源在corrupt-bak精确保全；48 B旧boot-bak不变；不采纳伪恢复字段|PASS 此安全子项；H/shared_duplicate_old_backup|
|备份槽满|截断源+三个不同旧槽；拒写原主、旧副本不变、可见修复出口|434 B原主及三个28 B旧槽不变；截图可见冻结与人工修复提示|PASS 此失败恢复子项；H/shared_backup_slots_full|
|伪保存主体/恶意原文|保存经理/session、越权项目/虚构设备/要求CLOSED；不得取得可信会话或写业务|actor/session为空，原文/意图恢复；三业务盘字节不变，仍登录页|PASS 冷保存负例；H/shared_forged_saved_subject；不是恶意模型回包测试|
|硬1：三组真实模型建议|现场换描述，追问/多候选/无历史，不编造根因|预存恢复夹具，无真实键入/模型返回|NOT_RUN；G0-E/T33不签PASS|
|硬2：AI与手工成功|分别经人工确认→M2精确final→关联事件→任务回读/重开|三业务盘各场都是原空数组，没有新OPEN、final或确认事件|AI NOT_RUN；手工 NOT_RUN；未确认无新增工单子项PASS|
|硬3：双层失效|请求A后改B、迟到A展示；展示后改上下文再采纳|源码守卫保留，实际交错没有运行|NOT_RUN；受控输入/迟到回包动作覆盖BLOCKED，见下文|
|硬4：恶意返回/失败兜底|假设备、越权项目、非法状态、自报完成拒绝；模型失败手工可继续|仅冷保存负例；真实模型回包/错误恢复未执行|NOT_RUN；受控回包机制BLOCKED|
|硬5：桌面编辑/取消/重试|可信登录后真实控件操作、秘密不落盘|截图仅登录页；正式原文恢复FAIL；实际编辑/取消/重试未执行|恢复FAIL，其余NOT_RUN|

## 原生证据逐项复核

独立在内存重新执行已读审计逻辑，**不覆盖已有审计文件**；仅抽取 harness 的 render_profile 纯函数，不调用 run/preflight/pgrep/网络入口。重算输出与已有 E/native-evidence-audit-r13.json 全等：**5656 项证据检查，0 不匹配；MANIFEST 1792项；mirror对installed/.running资源比较252项**。这些是证据核对数，不是业务PASS数。

1. **summary/results**：请求全文及SHA、八场顺序、purpose、size、实际命令、batch、退出/时长与各result一致。八场16.20–16.30秒，无ABORT、无未打开应用提示；只有launch-hub/capture。没有把消息中的“无新请求”包装成新执行。
2. **profile/probes/env**：八份profile与当前模板/场景目录/控制口重构文本全等；apply rc0、外写探针created=false、五类禁读和osascript执行拒绝均为ok。HOME、app-data、tmp/cache等指向各场目录；无模型代理规则。禁读目标只核证据，不读取秘密内容。
3. **进程回收**：pre/post均rc1/class NONE，pgid_members_after=[]，运行成员归本场PGID，quit_http/rc0；驱动记录HOME目录mtime不变、Library扫描无新增。未自行调用sandbox-exec/pgrep；不拿agent rc71/rc3判BLOCKED。
4. **captures**：8/8请求图SHA匹配；另8张part图有效，共16张，均2560×1264。四种不同SHA内容已逐一目视，相同SHA映射其余图。都为登录界面；备份满一场有明确冻结提示，正式包/备份成功场没有恢复诊断。未见业务区空白，但没有登录后工作台/草稿/成功工单截图，不能扩大布局和交互验收。
5. **files_written_in_run_dir**：逐项核排序、唯一、计数、存在、路径归本场；各场182–184个记录。这是驱动记录的文件集合，包含资源/日志/图像，不当成业务写次数或全系统写审计。
6. **sandbox_denials**：全文读取并重算summary一致；包括外部443、Metal缓存、/dev/dtracehelper及/usr/bin/osascript拒绝。没有观察到越界写成功。process-exec拒绝与probe相容，不冒称执行了未授权自动化；news外联失败不算MiniMax调用。
7. **host_log_markers**：从八份完整日志重算listening/quit/launched/eval/panic/app_not_opened、bytes/tail均匹配。正式eval657584 B/shared765252 B，view=true；809 B是另一宿主视图。7场零[E]，长输入场1条运行预算[E]；**解析错误0与运行错误1分开记**，不宣称八场零错误。
8. **model_proxy_stats**：八场needs_model=false，无代理环境/统计字段，summary billing_error=null；本轮0真实请求。模型服务注册不等于MiniMax调用成功；历史作者r3调用不代当前原生效果，无402/欠费证据。
9. **权威结果**：八场tasks.json/actions.jsonl/events.jsonl与seed原字节一致，均为空数组；未伪造成功。共享合法state会补默认偏好，**主文件字节不是完全不变**，四个恢复字段值/嵌套payload才是正例比较依据。正式四字段丢失，精确源备份存在；不误称不可逆源字节丢失。
10. **运输/保护**：210个seed/mirror文件及写门禁前8个保护输入与阶段清单相同。每场唯一.running资源、installed、mirror全文件集全等。复用两份已有隔离签名catalog，无新签名/私钥；r9授权删除私钥路径仍不存在。公开发布不需要也未执行。

## 缺陷与原编号闭合

### D-M3-02 — P1 / 必修 / OPEN：正式交接包仍误判合法持久输入

- **文件与行号**：正式E/formal-r9.source.main.splash:560–568完整性门禁、594–600默认恢复分支、614–625字段并入、999–1003保存放行。共享修复对应当前main:1951–1996、2364、15179–15194。
- **触发**：H/formal_r9_unicode_control全新隔离Store；1236 B合法JSON，含非空pending_input/confirm_intent_id、完整confirm_intent及action_keys_by_task，launch-hub→capture→退出。与共享中文场输入完全相同，宿主同为rc.6。
- **实际/预期**：正式主文件变2207 B默认态，四字段全false；boot-bak逐字保留原1236 B。预期合法来源正常恢复四字段/嵌套payload及原动作键，不生成损坏备份，不建立会话。
- **根因**：正式包的旧完整性门禁仍将合法对象分入损坏路径，随后放行默认state保存；共享读取修复尚未成为正式M3交接。具体哪一个旧trim/字符/类型原语导致false仍未知，未捏造宿主返回类型。
- **影响/证据**：退出后不能正常继续未提交报修或沿原意图恢复；这是核心恢复阻断。H同名result/log/frame/主与boot-bak、E/expectations及重算audit四字段false共同支持，置信度高。
- **具体改法**：当前共享读取接线已有正例证据，**不要重写已修逻辑**。构建方把已验证共用读取及M3恢复接线冻结为新的正式M3候选，给candidate_id/base、清单/源码SHA/运输digest、与r9差异及实施报告；保持已通过保源/冻结分支和界面。旧r9不能只改候选标签冒充新字节。
- **验证**：对新正式候选运行同类中文/ASCII/长输入/重复键+旧bak/槽满/伪保存身份，逐字段/逐字节回读；登录后核输入控件与原意图继续，不用等价Python代签。真实模型/AI与手工成功链另须真实证据；不把冻结候选本身当修复通过。

### A-M3-R13-01 — P2 / 建议：共享长输入恢复出现运行预算错误

- **文件/证据**：当前main:3297–3305 _charAtSafe、7325–7337逐字符hash、15183–15185恢复hash；H/shared_long_input_restore/logs/host.log:56明确定位运行源码3303:11。
- **触发/实际/预期**：2826码点中文/emoji/转义原文冷开，出现一次“script equality work, instruction, or time limit exceeded”；四字段仍恢复全等、登录页可见、无坏备份。预期恢复链不触发预算错误。
- **根因/影响**：_charAtSafe每次重新to_chars，hash循环反复调用，静态存在重复扫描；日志没有完整调用栈，不能确定只有hash导致或断言之后全部交互失效。此轮未见恢复数据丢失/空白，按核心阻断裁决列建议，不另加P1。零运行错误检查实际为FAIL，不能抹去。
- **具体改法/验证**：在既有hash/字符路径复用一次字符数组，保持当前指纹/版本失效语义；不增字段/入口，不跳过来源或版本门禁。相同长输入以及短中文/emoji负正例在固定宿主复跑，核零[E]、输入hash一致性与两层旧建议失效。无完整栈时先做最小定位。

### A-M3-R12-01 — 原建议继续挂账

共享main:1958–1962备份成功写STATE.status，登录提示只消费恢复notice；H/shared_duplicate_old_backup盘面已保源，但截图无备份成功说明。预期已有反馈出口明确恢复依据与路径。根因及实际与r12相同；只影响反馈，无已证实核心阻断，仍P2。建议在既有出口显示保源说明，验证同屏文字与副本字节，不改布局、不单独导致FAIL。

|原编号|本轮复核结论|
|---|---|
|D-M3-01|正式rc.6冷根零错误/登录页PASS；共享7场解析0但长输入1运行[E]，不能写全场零错误；登录后工作台NOT_RUN|
|D-M3-02|正式OPEN P1；共享四字段恢复及保源/冻结子项PASS，长输入诊断建议；不把共享改善倒填正式包|
|D-M3-03|相关函数与r9冻结区段相同；伪保存身份无写PASS子项；实际迟到/改输入/切项目/撤权/task/facts/evidence交错NOT_RUN|
|D-M3-04|来源/version_present源码改善保留；恶意原文冷保存无写PASS；真实来源parse→展示→采纳→确认NOT_RUN|
|D-M3-05|r9显式outcome消费根因修复保持，共享历史创建/确认结果绑定变化已定位；实际final/关联事件/回读/重开NOT_RUN，不伪造动态闭合|
|D-M3-06|逐字段解歧义逻辑保留；实际追问/选择/无历史路径NOT_RUN|
|D-M3-07|MiniMax配置/本机endpoint覆盖源码保留；0请求，原生真实效果NOT_RUN|

没有发现相关M3差异新增用户入口、页面或功能的实证；共享底层可靠性helper不据数量认定功能扩展。没有新无关P1。

## 既有验收逐条记录

|项|本轮精确状态|
|---|---|
|G0-E|NOT_RUN：0真实模型请求，服务注册/config不代调用成功|
|T01|正式原文恢复FAIL；共享恢复子项PASS；实际提取/追问/编辑NOT_RUN|
|T03|未认证冷盘无新增工单PASS子项；合法/缺项/越权实际提交NOT_RUN|
|T25|恶意原文+伪保存主体冷开无写PASS子项；恶意模型返回/非法状态动态NOT_RUN|
|T26|模型失败状态与合法手工兜底NOT_RUN|
|T33|真实三组描述/同义表达效果NOT_RUN；三个恢复夹具不当泛化结果|
|T34|来源/候选相关源码保留；真实来源正负例/人工解歧义NOT_RUN|
|T35|实际双层交错NOT_RUN；受控有效输入/迟到回包动作机制BLOCKED|
|T36|实际错误/越权模型回包NOT_RUN；受控回包机制BLOCKED|
|T37|正式原intent/key恢复FAIL；共享恢复子项PASS；AI/手工M2权威确认和恢复分别NOT_RUN|
|T38|两种对象、请求、宿主、运行资源可定位PASS子项；正式新候选/模型同条件复跑未交接/NOT_RUN|
|U02|正式未提交原文恢复FAIL；共享持久原文子项PASS；实际编辑/补缺/采纳NOT_RUN|
|U07|正式输入/意图恢复FAIL；共享恢复与坏源保护PASS子项；真实取消/重复点击/重试NOT_RUN|
|U08|登录页/槽满冻结提示PASS子项；备份成功提示建议；实际提交失败/待核验反馈NOT_RUN|
|U11|原生根与capturePASS子项；键盘焦点/滚动/面板动作/完整工作台NOT_RUN|

## 判定与交接

**FAIL；必修仅 D-M3-02（正式 M3-r9 恢复失败）。** 不因两个建议或BLOCKED-HOST判FAIL；不将未测项降成已通过。共享对象改善明确认可为恢复子项证据，不自行宣布正式交接/整模块PASS。

**BLOCKED仅用于具体动作覆盖 B-M3-01**：本次禁止osascript/辅助功能/自动化，schema.ui_actions实现不可使用；原固定宿主type/key不支持的旧实证不能自动当新rc.6已复验。当前八场只有launch/capture，没有获准且已实证生效的现场输入、会话控制或受控迟到/恶意回包机制；schema也未提供这类受控回包/同Store中途重开操作。相应验证机制BLOCKED，普通尚未执行的AI/手工业务项NOT_RUN；本次harness无ABORT。解阻条件是驱动在当前授权范围提供有效输入与响应控制并交付结果，禁止通过新增业务入口或伪造登录/成功盘面绕过。不是agent rc71/rc3原因，不再请求身份/provider/离线签名授权。

构建方留在M3：将已修共享逻辑正式冻结交接，复核D02及其受影响恢复；附固定宿主冷启结果/截图；对核心AI、手工确认分别给M2精确回执、事件与回读证据。建议只挂账，不做新功能、不修挂账其他模块。

本轮只新增本报告并更新GATES的M3审查字段/status，review_report指本报告；保留旧review字段到history，保留作者candidate_id/实施信息、其他模块和原验收台账。未更改ACCEPTANCE，因没有新的完整既有用例PASS可登记。未改业务源、夹具、请求、H原证据或审计文件。

未publish/listing/push、未发issue/评论/消息、未部署、更换渠道或读取秘密；第1段项目外记忆索引误读已在阶段笔记记录，本第2段仅读取项目内资料，不能用原生隔离CLEAN覆盖该审查操作偏差。无需Abram新增授权，无余额错误。**不允许进入下一模块。**

STATUS=FAIL
NEEDS_ABRAM=no
