# M4 独立 Review r7

**最终结论：FAIL。** `M4-r6-worktree` 在独立 harness 的三场原生运行中均未渲染业务界面，登录、设备、预约与开工流程没有成立。解析错误已消除，但 B-M4-01 的核心渲染阻断仍在。D-M4-03 部分修复，非过期他人锁在冷启动时被错误清空，真正互斥仍未闭合。D-M4-04 的旧累计编辑集反例在源码层已修，完整动态验收仍未执行。隔离回收与证据一致性通过，不允许进入下一模块。

- 审查者 / 日期：本会话唯一独立审查方，2026-10-12（Asia/Shanghai），两段式 `r1_2104`；无子代理、无业务源码修改。
- candidate_id：**M4-r6-worktree**；声明 base_candidate_id=M4-r5-worktree，实际修复 diff 基线为 M3-r7 源 `a6f55a21aa8ccd70e2bcc9a886dfdedab996b7811f6b447e62fd49a20d8cdee8` / 473410 字节。此基线变化由实施报告明示，不冒充所有累积修改都是本轮修复。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，存在未提交工作树；审查按内容清单冻结，不只按 HEAD。
- 当前主源：`app/bundle/main.splash` SHA-256=`37d1b1cabbea7d17e0b24ddb66aae4afe7ed5b54940df6b6b8d14a3c3d777b20`，477432 字节、9951 行。第1段冻结源、当前工作树、独立安装副本、三场实际 `.running` 副本一致，写门禁前再次核验。
- 作者报告：`reports/M4_IMPLEMENTATION_r6.md`；候选清单：`runtime/optimization/2026-10-09/M4/r6/CANDIDATE.json`。版本由用户交接证据、请求、报告、清单和 GATES 联合定位，未按 mtime 选版。
- 上一轮：M4_REVIEW_r6 / M4-r5-worktree。本轮仅复核 B-M4-01、D-M4-03、D-M4-04，以及直接受影响回归。D01/D02/D05 既有已闭合源码子范围保留。
- 前置：**M3=FAIL / M3-r7-worktree / M3_REVIEW_r8**，不存在已接受 PASS 的 M3 候选。按用户挂账裁决继续清单复核，未伪造前置满足；本轮独立复现其直接影响 M4 的渲染与输入恢复失败，不修改 M3 门禁。
- 固定宿主：M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense，SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。
- 实际运行：外部驱动执行审查方请求，2026-10-12 **01:05:52–01:06:57 +08:00**。三场 CLEAN / quit_http / rc0；审查方未启动宿主、sandbox-exec、pgrep、自动化或辅助功能。
- 路由 / 标题：工具未提供主会话 Router 路由、实际型号或当前会话 createdAt/标题接口；未冒称已切指定型号或实际命名。读取与写入限定项目内，未读取生产明文凭据/provider 密钥。
- 已读范围：第1段笔记列出的 AGENTS、CONTEXT、00/01/02/M4/04、上轮缺陷、候选/差异/作者证据及对应验收；第2段仅读这些缺陷关联源码、模板、GATES 和驱动证据。
- 已运行范围：第1段独立离线 catalog 验签、本地 install_staged/restart may_run；驱动三场冷启动；第2段完整证据摘要、参数/配置/加载副本、PNG、全部 host/denial 日志及权威盘对账。
- 未运行：真实可信登录、M3 创建到接单/设备/预约/开工、领域反例、同盘业务并发、模型交错、提交点故障和同盘进程重开。业务区空白导致命令 NOT_RUN；确实缺白名单通道的子项单列 BLOCKED。
- 置信度：候选与证据一致、空白 UI、锁清空、输入丢失、源码控制流及隔离回收 **高**；UI 根/句柄安装的完整修复根因 **中**；未运行的真实领域/模型/并发结果 **未知**。

## 证据索引与核验

- **H**：`runtime/optimization/2026-10-09/M4/native-runs/review_r1_2104_REQUEST_review_r1_2104/`。
- **S**：`runtime/optimization/2026-10-09/M4/native/review_r1_2104/`。
- **R**：`runtime/optimization/2026-10-09/M4/native/REQUEST_review_r1_2104.json`。
- **N**：`runtime/optimization/2026-10-09/M4/native/REVIEW_NOTES_r1_2104.md`。
- **A**：S/`native-evidence-audit.json`，S/`audit_phase2.py` 可重复只读核验。命令 `PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/native/review_r1_2104/audit_phase2.py`，rc0；其通过范围是证据一致性和隔离，不是业务 PASS。

|独立场景|隔离 / 当前字节加载|原生日志与截图|权威结果|
|---|---|---|---|
|cold_empty_history_input|PASS；probes.ok=true，pre/post=NONE，pgid_after=[]，CLEAN；实际运行源与候选一致|业务 eval view=false；index_of 177行、slice 353行、ui作用域错误19行；末张空白；key/type/wait unknown|任务/回执/事件/测试账号未变；保存的新中文原文被清空，panel draft→none|
|corrupt_authority_manager_hint|同上 PASS|业务 view=false；index_of 180行、slice 356行、ui作用域错误19行；末张空白，无坏盘错误出口|截断 tasks.json 原样保留，回执/事件/测试账号未变；actor hint清空；没有实际提交命令|
|foreign_lock_expired_tech_hint|同上 PASS|业务 view=false；index_of 176行、slice 353行、ui作用域错误19行；to_int方法缺失1行；末张空白|任务/回执/事件/测试账号未变；**另一owner非过期锁由非空变空**；actor hint清空|

1. **MANIFEST.sha256 全482项核对，摘要错误0、缺文件0、重复0、未列入文件0**；summary.request 与 R 一致，harness/template 摘要匹配。各 result 的宿主/profile 摘要、命令与 env、seed 来源清单、截图存在性/摘要、write 列表、denial 摘要及 host markers/bytes/tail 均独立重算一致。
2. 请求6张截图，实际仅末张3张存在，initial3张缺失；result 如实记 exists=false / sha256=null。三张存在图全部已查看，均2800×1718、SHA `889f76b20e12fbb201c189ee3a69f15326759040726782ce54e270455e4263ec`，业务客户区空白。请求1280×800不等于实际客户区尺寸通过；缺 initial 不能伪造操作前后比较，也不因该证据建议项另判 FAIL。
3. 每场实际加载477432字节业务源，分别 host.log:**1142 / 1158 / 1145** 的业务 eval `view=false`；其后的809字节系统窗口 `view=true` 不属于业务。三场无 parser 行，解析子项 **PASS**；大量运行时方法/作用域错误及空白业务 UI **FAIL**。宿主 rc0 / 无panic / CLEAN 不能替代这一结果。
4. 按实际请求仅运行 launch/wait/capture/key/type。cold host.log:**39、41–43** 明确 unknown `wait:4`、`key:Tab`、中文 type、`wait:2`；另两场39/41为wait unknown。故真实键入/登录凭据输入与按动作等待调度通道 **BLOCKED**，不是从未尝试推断不支持。多次capture最终只生成末张，不声明成功等待四秒或两秒。
5. files_written_count 分别 **124 / 124 / 125**，与列表数量相等且未截断；全部列出路径在各场目录内且存在，主要是代码副本、系统应用/缓存、profile/log/PNG以及 state。业务 tasks/actions/events/隔离accounts 三场均与seed同字节。**业务盘不变只证明未执行主链，不证明权限/过期/冲突拒绝已成功。** foreign 场tasks.lock变空，不能说全部业务seed保持不变。
6. cold 的state.pending_input从新描述“A栋301空调断续异响，运行十分钟后停止，请核对设备与到场日期。”变空，panel draft→none；这是预存未提交输入恢复失败，**不是成功键入后丢失**，因为type已unknown。其余state丢弃saved actor/选中项；不能据此代签真实登录与查询授权。
7. Seatbelt profile 与模板/场景参数逐字节一致，HOME/app-data/cache/config/tmp等均在场景目录；只开放本机控制口及模板所列本地网络规则，无模型代理。禁止读秘密/明文凭据/用户配置/SSH的探针全部拒绝，外写探针拒绝；pre/post NONE、pgid_after空、library_scan空、真实HOME的 .octosense mtime前后一致。denial日志中远端443、系统Metal缓存与/dev/dtracehelper均为**被拒绝**尝试，不能当成功外联/外写。
8. cold 的运行中PGID快照另有短暂 `osascript`，回收后为空；请求和实际cmd中没有该动作，审查方没有调用。快照无子进程参数/用途，不能断言宿主内部没有此调用或推断它完成了业务操作。按用户指定隔离/回收判据通过；这项观察如实保留。
9. bundle digest=`d34b1073e4908130841606727416593a1e50dd31a965b97ddfbd473ff7275ba5`，seed marker=true、host digest marker=false。加载证明采用 launch-hub、实际 `.running` 源/config/identity/manifest/listing摘要和业务eval字节数，不拿seed包含digest冒称运行。
10. 独立本地 catalog verify / install_staged / restart may_run 第1段均rc0；运行副本再次一致，本地路径可行，不需要公开发布。审查方生成私钥0；作者两把隔离私钥路径已核不存在，未读取私钥字节。准备记录见S/preparation-evidence.json。
11. 三场 needs_model=false，model_proxy/model_proxy_stats、代理产物、MM_KEY及模型endpoint覆盖env均不存在，符合请求。本模块本审查真实调用 **0**，无402/欠费，不能声称真实 T35 通过。

## 必需检查

|检查|独立步骤 / 期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/证据一致|冻结候选，对安装和运行副本、schema/request/摘要核验|当前候选、固定宿主、三场加载一致|PASS一致性子项；M3前置仍未满足|A、S/start-snapshot、GATES、M3_REVIEW_r8|
|真实UI主链|M3真实创建→接单→设备→预约确认→开工，权威回读|三场空白，无登录/工单表单，无法开始|**FAIL原生入口；业务主链NOT_RUN**|三张PNG、业务view=false日志|
|硬1资格/设备服务|合法绑定与技能/越权/伪造/仅安装位置无服务反例|保留守卫源码；未提交命令|NOT_RUN|N、A.business_files|
|硬2预约|提议不直升、合规确认、过期/改约/跨项目冲突规则|spec清理与坏盘拒绝源码已改；坏盘无可用错误出口；实际预约未操作|NOT_RUN命令；桌面错误出口FAIL|main:2982、3104；corrupt末图|
|硬3真并发|两独立同盘上下文接单/重叠确认仅一成功；相邻正常|锁恢复实际清空他人非过期锁；原子串行仍未实现，harness逐场新盘顺序运行|**D03 P1未闭合；真并发通道BLOCKED**|main:961、2921、3263；foreign log:67；A锁对账|
|硬4开工/旧技工拒|有效设备/预约/当前时窗/当前承接者|守卫源码保留，未实操|NOT_RUN|startProgress、reassign；A|
|硬5真实输入/角色/回执|三个可信角色可理解、填写、确认并看到一致事实|空白；预存原文清空；type/key不支持|**FAIL可用UI与恢复；角色命令NOT_RUN**|cold state对账、三张PNG、unknown日志|
|改派/改约撤销|旧授权/确认/AI不可执行，新绑定可恢复|D04本次字段集合已替代累计集合；实际改派/改约/回包未运行|源码反例修复；动态NOT_RUN，交错通道BLOCKED|main:2745、5191；N|
|隔离回收|用户指定profile/probe/pre/post/pgid/CLEAN|全部指定条件满足|PASS；无ABORT|三场result/profile/denials，A|

### 既有用例逐项结果

|用例|本轮结论与边界|
|---|---|
|T04|BLOCKED：schema没有两个可信独立上下文同盘同步接单调度；D03未闭合，实际未产生业务并发结果。|
|T05|NOT_RUN：技能/项目权限反例、经理分配身份事件未执行；空白入口不得继承旧后端PASS。|
|T06|NOT_RUN：真实改派、旧预约失效、ACCEPTED及新承接者/旧技工拒未操作；D04源码修复范围保留。|
|T07|NOT_RUN：编码/asset载荷等价、伪造/跨项目/归档设备实际绑定未执行。|
|T08|NOT_RUN：合法服务空间正例与安装位置相同但无服务关系负例未执行。|
|T09|NOT_RUN：无设备开工、IN_PROGRESS技工换设备拒、经理更正旧新值理由未执行。|
|T10|NOT_RUN：提议不直升、报修人确认、非报修人拒未执行；saved actor只是hint。|
|T11|BLOCKED真同盘并发调度；跨项目重叠/相邻的实际确认亦NOT_RUN，非原子owner检查不代验。|
|T12|NOT_RUN：真实改约保留旧预约、新确认替代、拒新保旧未执行；D02既有源码子范围保留。|
|T13|NOT_RUN：过期确认/410、无定时器仍拒、客户端伪时间未提交；预置已过期提议不是命令结果。|
|T14|NOT_RUN真实上海时区/UTC毫秒/完整日期与模糊时间确认/end<=start；键入步骤BLOCKED（实际type/key unknown）。|
|T15|NOT_RUN：旧version拒/刷新、保留表单与阶段百分比限制未执行；D03持锁恢复另有实际FAIL。|
|T31|NOT_RUN：实际取消释放预约/保留历史、终态拒/新关联任务未执行；不拿夹具代链。|
|T35|D04旧累计字段反例SOURCE-CLOSED；真实模型生成期间改派/改约/旧回包NOT_RUN；白名单没有受控交错步骤，该子项BLOCKED。|
|U01|FAIL首屏：三场无业务内容/当前动作；三可信角色待我处理/下一处理人未形成。|
|U03|NOT_RUN完整三角色同工单事实/动作权限/不能自验；可用桌面入口FAIL归B01，hint不证明真实角色授权。|
|U04|FAIL可用预约/错误投影：客户区空白；具体当前预约与待改约、冲突/过期命令NOT_RUN。|
|U05|FAIL可用设备/依据展示：客户区空白；真实选择/安装与服务关系绑定NOT_RUN。|
|U07|FAIL输入恢复与错误出口：cold预存原文被清空、坏盘/持锁场无出口；重复点击/旧版本/离线业务NOT_RUN，提交点故障/丢响应/同盘进程重开通道BLOCKED。|

BLOCKED只用于**当前白名单实际不能覆盖**的步骤，没有以agent内rc71/rc3或宿主未启动为理由；本轮宿主已真实运行、无ABORT。核心UI失败明确记FAIL，后续尚未发生的领域动作记NOT_RUN。

## 缺陷与修复清单（沿用编号）

### B-M4-01 — P1 / 必修 / PARTIAL：解析子项关闭，完整业务界面仍无法渲染

- **文件与行**：`app/bundle/main.splash:1186`、`:1194`、`:1196` 不兼容字符串方法；`:8118`、`:8122` / `refreshDesktop:9892` 等依赖ui，初始化/根返回`:9937–9951`。host VM坐标不是源行号，源码行用实际文本定位；完整UI句柄失败根因尚未完成最小隔离。
- **触发**：R三场新隔离盘加载本轮固定候选，含空历史、坏任务盘、他人锁；均完整执行到业务eval与周期刷新。
- **实际 / 预期**：无parser错误但业务view=false、三张空白图，持续index_of/slice及ui作用域错误；cold预存未提交原文消失。预期真实登录/任务/表单渲染、输入可恢复、失败同屏可继续。
- **根因 / 影响**：当前选定发行宿主不提供运行中被调用的字符串方法；错误值继续参与循环。UI根/句柄在周期刷新作用域没有成立。核心处理流程与三角色首屏、坏盘错误恢复被直接阻断，属于本模块必须消费的最小前序依赖。不是要求M4顺手修完M3。
- **证据**：H/cold_empty_history_input/logs/host.log:69/71/73、1142、1155起；corrupt:67起/1158/1171起；foreign:69起/1145/1158起；三张PNG；A.state_changes与加载摘要。
- **具体改法**：构建方先在固定宿主经harness验证实际字符串/数组API，替换启动拆行的不可用方法，空串直接返回且异常不进入错误循环；保证业务根挂载与UI句柄供初始化/周期刷新使用。输入恢复应在成功挂载后发生，不能把未提交原文保存为空或以“准备就绪”掩盖失败。不要修改审查夹具/预置SCHEDULED绕过主链。
- **验证**：完整同候选冷启动三场零parser且业务view成立、有实际登录/任务/表单与错误出口，原文保持；再从真实M3创建同一工单，经接单、设备、预约确认到开工，核权威任务/回执/事件。系统窗口view=true不代验。

### D-M4-03 — P1 / 必修 / PARTIAL：他人非过期锁被清空，互斥边界仍不可靠

- **文件与行**：`main.splash:961` 字符串to_int；`:956–968` 默认stale和清锁；`:2918–2953` 普通抢锁、`:2921–2923` 同actor重入；`:3261–3270` 提交前只核actor前缀、空/读失败放行。授权清理`:2982–2985`、坏盘显式拒`:3095–3114`为本轮已改善源码子项。
- **触发**：R/foreign场预装 `review-other-owner@4102444800000@901`，即按既有规则不是5分钟过期锁，冷启动没有可信会话或业务命令。另源码反例为两个同actor独立上下文/不同actor先后读空锁并在检查与写之间竞争。
- **实际 / 预期**：实际host.log:67 `method to_int not found on string`，隔离tasks.lock非空→空，任务盘未变。预期非过期他人锁保留，未知时间解析不得判过期或释放别人的锁。源码仍允许同actor两个上下文重入且提交只看actor前缀，没有已验证原子临界区。**本轮没有实际双成功并发结果**。
- **根因 / 影响**：锁时间解析依赖不可用方法，失败仍保留 `_stale=true` 然后清锁；owner绑定业务actor而非独立持有实例，读/冲突/版本检查与写盘之间有竞争窗口。影响接单、重叠预约确认、失败后恢复，非建议项。将这个直接恢复反例并入原D03，不扩审新模块。
- **证据**：A.scenarios.foreign_lock_expired_tech_hint.business_files.tasks.lock记录原文和前后摘要；H/foreign.../logs/host.log:67；其最终tasks.lock为空；N原子边界源码反例；作者报告也承认HOST_PRIMITIVE_BLOCKED。
- **具体改法**：先用宿主支持的数字转换并对解析失败明确拒绝，不能默认stale；非过期锁及未知归属锁不清空。owner采用独立持有实例token，获取/提交/释放核完整token；提供可验证原子获取或等效单一串行命令边界，把权限、最新事实、冲突检查和任务/预约/事件/回执提交包住。锁读取失败不能按无锁继续。需宿主原语时交最小复现及方案，不擅自引入新服务。
- **验证**：非过期/过期/坏stamp三组冷启动，未知不误清，合法恢复可解释；授权拒后spec为空且下一命令正常；在实际提交点读坏盘明确拒并恢复；两可信独立原生上下文共享隔离盘同步接单、同技工跨项目重叠确认仅一成功，相邻都成功，核任务/事件/回执与同盘重开。普通文件/改写Python循环不代替原生业务并发。

### D-M4-04 — SOURCE-CLOSED / 原生NOT_RUN：旧累计编辑集反例已修，不再列为本轮剩余P1

- **文件与行**：`main.splash:2745` 失效清空本次字段集合，`:4669–4675` 显式编辑记录，`:5191–5208` manual恢复只消费本次集合；新AI apply/关闭面板同步重置。
- **原触发 / 实际源码 / 预期**：失效前累计problem/space/category齐备，改派/改约后只改原文或联系人，旧集合不应使旧proposal重新有效。本轮累计审计集合不再被恢复守卫消费，失效后来源manual，单改原文不自动凑齐本次三字段；原源码反例关闭。该结论没有运行旧AI创建错误工单的证据，也没有完整新AI恢复的证据。
- **根因修复**：累计历史与本次失效后的明确编辑记录分离，保留审计；不因尚未运行再要求无依据的业务改写。
- **证据 / 后续验证**：N与独立base diff/冻结源；待B01和白名单通道修复后，按旧编辑集空/部分/齐全×改派/改约，核无编辑/只原文/只联系人拒绝，当前明确核对/当前AI可恢复，并验证迟到回包。完整T35继续NOT_RUN/交错子项BLOCKED。

### 建议挂账

A-M4-01/02/03保留，不用于判FAIL。请求initial3张缺失、wait/type/key支持与schema不一致需要驱动/宿主明确可执行动作及调度能力，末张空白足以支持本轮入口FAIL，但不足以代签前后交互。构建字段 `host_runs/deferred_gaps/blockers` 尚含旧rc71/rc3和provider未裁决文字；本轮只在审查字段给出当前事实，保留作者历史来源，不顺手改实施记录。宿主内部短暂osascript用途未知，不伪造其行为。身份/provider及离线签名已有授权，均不再作为NEEDS_ABRAM。

## 判定

- **最终结论：FAIL**；精确范围为M4-r6-worktree上轮三项闭合与受影响核心原生回归。
- **必修清单**：B-M4-01解除完整业务UI/输入恢复阻断；D-M4-03修复未知/非过期锁误清及可靠实例互斥/串行提交边界。D04源码改善保留，完成相关动态回归；不新增无关业务开发。
- **阻塞与未测**：type/key/wait真实unknown；schema缺双上下文同盘同步、受控写点/丢响应/迟到回包及同盘跨进程重开。由驱动/宿主提供符合现有授权的通道解阻。其余命令因核心入口失败NOT_RUN，不以作者声称、夹具状态或旧后端PASS替代。
- **先前模块回归**：M3共同渲染与输入恢复失败由本轮再次实证，M3仍FAIL；M2锁恢复的直接消费问题在D03记录，不修其它挂账或改其他模块结论。
- **门禁 / 台账**：仅更新GATES的M4 status、review_*及reviewed_at；review_report指向本文件、review_candidate_id=M4-r6-worktree。写前保存原样GATES，旧审查字段追加review_history，作者candidate/base/implementation/build字段及其他模块保持不变。ACCEPTANCE.json保持历史原样，不把旧PASS移植为本轮原生PASS。
- **不允许下一模块，不执行M5**。留在本模块按上述两项必修和已有动态检查清单修复/重审。
- **NEEDS_ABRAM=no**：本地离线catalog/install路径实际成立，身份/provider已裁决，模型0次且无欠费；没有公开发布/公开签名/上架授权缺口，剩余都是技术修复与测试通道问题。

STATUS=FAIL
NEEDS_ABRAM=no
