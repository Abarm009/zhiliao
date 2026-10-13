# M3 独立 Review r3

最终结论：**FAIL**。`M3-r3-worktree` 的 D-M3-01、03、04、05、06 尚未完整闭合，涉及真实 AI 接线、旧输入失效、最终权限复核、权威成功判断及来源/时间意图。只复核上一轮编号与受影响回归；不因建议项或 M2 的历史 FAIL 单独拒收。未修业务代码，未执行下一模块。

- 审查者 / 日期：Codex 唯一主审，无子代理；2026-10-11，Asia/Shanghai。系统标识 GPT-6/Astra；当前工具不能独立确认 Codex Router 路由或切换至指定 gpt-6.1-sol，不能冒称已切换。无当前会话 createdAt/改标题接口，未猜日期修改标题。
- 置信度：固定候选字节、静态调用链、实际局部 VM 反例和离线安装结果 **高**；完整发行桌面行为、真实 M2 工单恢复 **未知**。Python 控制流翻译仅作为源码局部证据。
- candidate_id：`M3-r3-worktree`；base_candidate_id：`M3-r2-worktree`；HEAD：`8d730569546cb57310944bb299695134df773b9d`。依据正式实施报告、CANDIDATE.json 与 GATES 交接字段共同定位，不按文件时间选版本。
- 作者报告：[M3_IMPLEMENTATION_r3.md](M3_IMPLEMENTATION_r3.md)；清单：`runtime/optimization/2026-10-09/M3/r3/CANDIDATE.json`。
- 主源 SHA-256：`9783878855dfa2ac7afabd11dc88207f93ef1aa76920c6c4c0759c633f9cbdaa`；配置 SHA-256：`55b41c8016c347ec0ba7a8b5e0942058eeef05a6f3c3f38b724a73bd183e0630`，均匹配交接。实际主源 **312592 字节、6909 行**，清单的326098字节/6908行不准确，列建议，不据此判 FAIL。
- 前置：M2 最新独立结论为 **FAIL**，`M2-r4-worktree` / [M2_REVIEW_r4.md](M2_REVIEW_r4.md)，没有已接受的 M2 PASS 候选。按用户前序挂账裁决继续本模块复审，保留 M2 结论；r2 留存源→当前候选差异已保存，不能把该大幅增量都声称为 M3 修改或已通过 M2 回归。
- 阅读范围：实际 AGENTS.md、CONTEXT_M3、00/01/02、M3 模块与04模板、M3 r2缺陷/本轮交接及证据、M2 r4结论、缺陷涉及的 main.splash/config/manifest 和测试脚本。CONTEXT 的“provider未裁决、不启动launcher、原M2 BLOCKED”是旧记载，以本轮用户裁决与最新实证为准。
- 证据根：`runtime/optimization/2026-10-09/M3/review-r3/`，下文短文件名指其 `results/`。候选前后快照见 start/end-snapshot、report-verification；r2→r3增量见 r2-to-r3.diff。
- 宿主：指定 `M0/r3/host/app-extracted/OctoSense.app`；launcher SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，见 host-pin。另用项目内 `runtime/identity/evidence/vm/target/release/identity-vm-probe` 执行抽取原函数；它**不是发行 launcher 或真实桌面**。
- 已运行：候选/证据核对，隔离预检，当前包check，本地离线签名catalog、官方install_staged/Store重建/may_run、篡改与恢复，8组局部原函数VM探针，5组源码翻译交错，6组独立恶意返回Python契约测试。
- 未运行：launcher、实际中文键盘/展示/采纳/取消/重试，发行宿主MiniMax调用，真实M2创建/最终回执/事件/重开，以及原生逐写点失败注入。独立预检 sandbox-exec rc71=`sandbox_apply: Operation not permitted`；pgrep rc3=`Cannot get process list`，所以不启动、不用--help、不产生本轮宿主窗口。既有残留窗口 **UNKNOWN**，不能声称已清空。
- 隔离：测试HOME、CFFIXED_USER_HOME、app-data、XDG配置/缓存、TMPDIR和签名全部重定向至上述项目内 review-r3。未读取明文凭据文件，未读取/输出模型密钥；未修改真实账号/安装映射/host-data及原始业务数据。本轮真实模型请求 **0次**，无欠费错误观察。未联网、上传、publish/listing、push、部署、发消息或更换计费。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与前置|核三份交接ID、实际SHA、r2留存差异及M2结论|对象可定位，前置如实|主源/配置哈希匹配；M2 FAIL挂账，无接受基线；字节数误报|对象定位成立；前置未PASS|start-snapshot、r2-to-r3.diff、M2_REVIEW_r4|
|硬1 / D01|换成强电间报警、会议室两空调滴水、未知楼层焦味，执行实际request函数并计适配调用|实际模型处理新输入、缺项/歧义可继续|三次均issued=true/ASKING，适配调用0；新增适配函数未被UI请求调用|FAIL接线；真实模型/桌面NOT_RUN/BLOCKED|vm-probes.request_new_inputs、source-traces|
|硬2 / D05/06|分别投影失败OPEN outcome、追create与confirm命令/回执，核工单字段|仅匹配最终回执及权威回读成功，来源可重开|commit_ok=false/confirmed_open=false仍confirmed=true；返回创建action_id而非最终确认回执；字段新增但恢复未跑|FAIL局部；原生BLOCKED|vm-probes.false_open_outcome、source-traces|
|硬3 / D02/03|采纳后原文A→B→首次确认；只键入B；当前任务8而旧回包7|展示、采纳、执行分别失效|局部VM中adopted=true/confirmed=true；源码翻译仅键入/旧任务也true；显式edit拒回包|FAIL；发行交错BLOCKED|vm-probes.first_confirm_after_edit、translated-probes|
|硬4 / D04|确认阶段跨项目空间/停用设备；独立假ID、非法状态、恶意原文、假来源|各入口一致校验，模型无业务副作用|最终确认跨项目/停用均true；契约假ID/非法状态拒；恶意文字actor不变无任务；假来源接受|FAIL最终守卫；安全回包局部改善|vm-probes.cross_project_confirm/inactive_confirm、malicious-contract|
|硬5 / D07|重跑隔离/清点预检，核审计白名单及调用点|真实键盘恢复可用，审计无秘密|rc71/rc3，未启动；审计仍长度/hash，无原文预览|BLOCKED桌面；D07源码范围关闭|preflight、source-traces.recordModelMeta|
|本地catalog路线|新离线keygen/certify/stamp/sign/verify，官方安装、重建、篡改拒绝、恢复|只在隔离目录有效，删除私钥|安装/重建/恢复rc0，篡改rc1；三份安装源与当前一致，私钥0|PASS，仅安装层|local-store-validation|
|受影响M2回归|追确认入口及commit失败判断，对照M2 r4已知提交缺口|无假成功、授权和回执可靠|初始version0→1已改善；最终返回仍只依赖内存status，创建提前saveTasks；原生回归未跑|FAIL D05；原生BLOCKED|source-traces、M2_REVIEW_r4|

本轮离线重打包digest=`4551e40acaf040d8219d38c6f2aa134b69c21f6629a300fa8413a7ae5ab9490c`。它是**筛出允许文件后、仅在本轮sandbox重签的副本**，不是原工作目录manifest旧digest。`may_run`仅授予storage、hosts为空，不能证明HTTP许可或应用可运行。复用了已审查的离线Store脚本，其publisher/source标签仍含r2，实际运行根、源码SHA及新digest见结果；不把标签当候选身份。`working.key`、`anchor.key`在finally删除，`remaining_key_files=[]`，结束再次核对为空。

原 `app/bundle` 的 hub check rc1：digest不匹配、备份/日志等文件违规、assets扫描拒绝；属于原包交付挂账，未修改原目录。隔离本地安装路线实际可行，因此不需要公开发布授权。

作者真实证据核对：`real_provider.json`记录3次200/OK，这是**作者Python适配层的记录**，本轮未独立复发。测试脚本没有调用M3Boundary、M2创建或权威读盘，其“3/3 processed”甚至只统计kind非空；不能支持实施报告中的“真实outcome OPEN/可重开”。测试输入事实另造了sp-a-4/5、as-a-4/5/6；当前main.splash只有sp-a-1..3/as-a-1..3。模型遵从这些测试事实，不等于捏造；问题是该证据不能证明候选当前事实。实际case1 confidence=medium，case3 space=null，也与报告中的high/sp-a-2不一致。见 author-evidence 与脚本行69–90、172起。

局部VM限制：最终确认/采纳反例均rc0且无错误日志；validSuggestion三组（含合法对照）全部false、错误串为空，无法据此认定迟到逻辑已修。保留实际输出，**不计迟到拒绝PASS**；对此只用明确标记的当前源码分支翻译（合法true、仅键入/旧任务true、显式编辑false）。最初夹具缺_textLenSafe及inline对象解析错误已修正夹具后重跑，没有改业务代码。

### 相关既有验收逐项复核

|用例|本轮结论与范围|
|---|---|
|G0-E|FAIL接线D01；真实发行宿主模型/关闭/拒绝/失败 NOT_RUN；作者Python三次200另列。|
|T01|FAIL D01/03/06；三组新描述只到ASKING，不证明真实模型/缺位置追问；原生BLOCKED。|
|T03|FAIL D04最终确认；手工编辑入口跨项目/停用已有guard，最终确认未刷新事实。原生BLOCKED。|
|T25|NOT_RUN完整；契约假ID/状态/身份字段拒绝、恶意文字不改actor/无任务成立；假来源接受归D04。|
|T26|BLOCKED完整手工链；NO_SERVICE分支可见，AI启用请求只ASKING；AI与手工共同受D05影响。|
|T33|NOT_RUN真实同义/症状变化；换输入请求探针不冒充模型提取效果。|
|T34|FAIL来源复核D04/缺项歧义处理D06；作者多设备样例使用不同事实集，完整模型NOT_RUN。|
|T35|FAIL D03首次确认失效；当前任务版本只与旧请求比较的源码翻译仍接受；原生改派/改约交错BLOCKED。|
|T36|NOT_RUN真实权限/白名单执行；manifest仅storage，未开HTTP权限；非法状态/身份契约负例已拒。|
|T37|FAIL D05；原函数接受OPEN+commit失败，没有最终确认action关联；真实读回超时/重试/高版本恢复BLOCKED。|
|T38|NOT_RUN完整；候选、配置、宿主及证据已固定，但真实测试prompt/事实不同，无同版本复跑链；审计源码改善。|
|U02|FAIL D03/06局部；旧AI与新原文可混配，时间编辑清零；实际桌面编辑/追问/兜底BLOCKED。|
|U07|BLOCKED桌面；D05仍每次newId、返回创建回执而非确认回执，不能据内存OPEN判断恢复成功。|
|U08|BLOCKED完整错误出口；取消/显式编辑源码分支有拒绝，合法手工闭环未证明。|
|U11|BLOCKED真实输入/滚动/切面板；D05假成功风险独立确认。|

## 缺陷

只沿用上一轮 D-M3-01～07；以下行号对应本轮匹配SHA的 main.splash。

### D-M3-01 — P1 / 必修 / 未闭合：适配函数存在，实际请求仍未接通

- 文件/行：main.splash:203、227、241、268、3176、6060；manifest.json:2；m3_real_provider_test.py:69、85、172。
- 触发：已启用MiniMax的情况下，在面板请求任一新描述。
- 实际/预期：原request函数仅bind→ASKING→audit→return，三组新描述适配调用0；_callMinimaxProvider仅定义，无调用点。预期当前宿主内真实调用、回包校验与编辑继续可用。
- 根因/影响：新增独立函数及Python调用没有接入实际应用链；manifest只有storage，host.http_fetch及env注入未在选定宿主验证。secret_ref指MINIMAX_API_KEY，但读取MIMI_SECRET/MINI_MAX_SECRET，无已验证映射。模型provider/身份授权早已给出，不能再以未授权拖延。
- 证据：vm-probes.request_new_inputs、source-traces、author-evidence、local-store-validation的grants。作者真实200不等于桌面已接；测试事实集不匹配当前应用。
- 具体改法：按选定宿主已验证API接UI→适配→回包/失败/取消；开最小http.fetch与目标host许可，只读注入已授权env文件并核变量映射。请求事实从当前授权项目实际数据生成；复用同一提示/解析/版本协议，不另造测试事实冒充应用。
- 验证：隔离发行桌面三组新的描述真实MiniMax ≤10次，包含缺项/多设备/不同症状，记录provider/model/宿主/请求版本和结果；失败退出保留输入。余额不足立即停止并写原文错误/NEEDS_ABRAM=yes。

### D-M3-02 — 部分闭合；真实手工UI BLOCKED，剩余必修并入D03

- 文件/行：main.splash:6053–6100。按钮前读取TextInput保留；没有新增独立P1。
- 剩余：键入期间尚未同步，editRawText在文本相同时也递增/失效；真实无模型→设问题→补字段→确认→回读仍未执行。
- 证据：UI源码与vm-probes/translated-probes。改法/验证：按D03实现当前输入同步；恢复条件后跑真实手工链，不能只凭按钮取值关闭整条缺陷。

### D-M3-03 — P1 / 必修 / 未闭合：采纳与首次确认仍沿用旧AI输入

- 文件/行：main.splash:2829、2887、3162、3211、3325、3353、6074。
- 触发：回包自动APPLIED后A改B→采纳→首次确认；或请求A后只键入B不点按钮；当前任务8而回声7。
- 实际/预期：原函数VM中adopted=true、confirmed=true，AI原文A而当前B。deliver仍直接apply改草稿；采纳只是`!active && APPLIED`；首次确认仅在last_confirmed_at非零时拒invalidated。任务只比请求快照，不读当前版本；事实/证据版本未绑定。预期展示和采纳独立复核，旧建议不覆盖、不采纳、不执行。
- 根因/影响：建议与草稿没有分开；状态标签当采纳依据；首次确认漏检。显式编辑失效已有改善，不能覆盖该反例。
- 证据：vm-probes.first_confirm_after_edit；translated-probes的合法对照/仅键入/旧任务；source-traces。
- 具体改法：未采纳建议独立保存；展示、采纳、确认共用当前输入/主体/项目/草稿/任务/设备事实及证据版本守卫；读当前TextInput，内容未变不递增。编辑后废旧绑定并允许合法人工重新确认。
- 验证：回包前、展示后采纳前、采纳后确认前三处交错，分别检查展示/草稿/命令/回执；另测无变化合法采纳，防止把全部拒绝当PASS。

### D-M3-04 — P1 / 必修 / 部分闭合：编辑守卫改善，最终确认仍只查存在

- 文件/行：main.splash:2696（parseModelReturn）、3024、3049、3333、3337；sources仅非空校验。
- 触发：合法采纳/编辑后撤用设备、变更服务关系或空间归属，再确认；来源填不存在记录。
- 实际/预期：最终确认VM中B项目空间、active=false设备均confirmed=true；_validateDraftFacts未被confirm调用。新手工编辑project/active/services guard是改善；假来源在Python契约仍接受。期望确认前按当前权限/事实复核并核引用，不将非空模型字符串当事实来源。
- 根因/影响：共享守卫只接编辑，未覆盖最终执行；来源没有可核引用。原生越权落单未运行，本轮证明的是确认入口放行，不能宣称真实工单已跨项目落库。
- 证据：vm-probes.cross_project_confirm/inactive_confirm，malicious-contract.untraceable_sources、source-traces。非法模型状态/身份负例拒绝、恶意原文作为数据无副作用是正确子项。
- 具体改法：回包/编辑/最终确认统一当前project、active、服务关系及全部备选校验；确认刷新权限和事实；来源改为事实ID/版本或原文片段，未知明确标未知；缺项/歧义需解决。
- 验证：三入口同样负例都拒，无成功事件；合法同项目通过，采纳后撤用/改关系再次拒；不存在引用拒绝。

### D-M3-05 — P1 / 必修 / 部分闭合：创建版本已修，成功仍依赖内存OPEN

- 文件/行：main.splash:3325–3378、3391、3435–3480、3601、2249；UI:6095。
- 触发：确认返回OPEN但commit_ok=false/confirmed_open=false；确认回执未落/事件失败；响应丢失后重复确认。
- 实际/预期：原confirm网关VM仍confirmed=true；只查task_id/status，不核commit标志或匹配最终回执/独立读盘。创建version0→1已修，但仍先newId/push/saveTasks和“草稿已创建”提示，再commit；返回的是create的action_id，confirmDraft不返回完整最终结果。期望只能来自M2确认动作final回执+事件+OPEN权威回读，未知保持待核验。
- 根因/影响：新增outcome只是内存包装；AI/手工共用同一缺口。M2 r4可靠性缺陷影响该链，不能以Python real_provider记录替代；测试脚本根本没有创建调用。
- 证据：vm-probes.false_open_outcome，source-traces.createDraftFromPanel/confirmDraftModelBound/confirmDraft，M2_REVIEW_r4 D03/04/05。原生写点失败注入BLOCKED，不伪造失败工单。
- 具体改法：仅修阻断M3的最小创建/确认依赖：稳定确认意图，统一授权/提交边界，无提前权威主写/成功；返回final/rejected/needs_verify及实际确认action_id/task/version，失败后对账原动作。网关核匹配final、事件与权威读回，重试不newId重建。
- 验证：AI和手工各跑真实成功及逐写点失败、读回超时、丢响应、重开/重复确认；同意图一个任务，未知不成功，成功三份证据一致。

### D-M3-06 — P1 / 必修 / 部分闭合：来源字段已接任务，时间/歧义仍未形成可确认事实

- 文件/行：main.splash:2887–2922、3096–3098、3325、3419–3425。
- 触发：AI建议含希望时间，人工修改时间或解决多设备歧义后确认；A来源/B最终原文，重开查依据。
- 实际/预期：新增ai_history三字段与desired_window两字段已进入task对象，这部分源码关闭；但时间编辑把start/end都置0，resolved_missing_fields/resolved_ambiguous_fields恒为空，确认不核未解决歧义。权威提交/重开仍无实证。期望保留可编辑的最终时间及真实人工解决记录，来源与最终输入关系可核。
- 根因/影响：增加schema字段尚未接真实编辑/解决状态；时间意图可能被清掉，未解决多设备可静默继续。不是缺一个漂亮展示，而是确认内容和来源不可靠。
- 证据：source-traces.editDraftField/applyDraftFromAI/createDraftFromPanel及D03首次确认反例；作者real_provider无权威回读。
- 具体改法：合法时间编辑解析并保留校验后值；缺项/歧义按实际人工选择更新解决记录，未解决拒确认；AI输入快照/最终人工原文经同一D05提交保留。
- 验证：A→建议→改B并明确重新确认；改时间与选备选后重开字段一致，未解决不能提交；核真实tasks/事件/回执，不查Python内存disk_records。

### D-M3-07 — 上轮关闭范围保持：审计不再存原文预览

- 文件/行：main.splash:3274起recordModelMeta，model_config.json audit_keys。
- 审计白名单和调用仍为长度/hash，无raw_text_preview_safe；密钥变量改名并不能单独证明安全，但本轮未发现该审计旧缺陷复发。源码范围继续关闭，发行宿主实际日志审计BLOCKED。不读取真实密钥来做测试。

### 建议 / 挂账，不据此判FAIL

- A-M3-01：修正文档中REAL_OK→原生PASS及“真实outcome”的证据混用，按真实记录改置信度/候选空间；作者152项离线通过不是本轮独立通过。
- A-M3-02：11秒有效期及失败转手工出口沿用建议，不因优化期限判FAIL。
- A-M3-03：清单字节/行数错误、base指r2但主源含后续M2等大量增量、CONTEXT过时；补可重建基线/增量归属。当前哈希明确，本轮对象未混淆。原目录包check与Store测试标签另行记录，未顺手改manifest或删他人文件。

## 判定

- 最终结论：**FAIL**；精确范围：固定M3-r3候选，上轮缺陷闭合和受影响回归。真实发行桌面与权威恢复仍BLOCKED，不代表模块整体通过。
- 必修：D-M3-01、D-M3-03、D-M3-04、D-M3-05、D-M3-06，按上述具体改法修本模块；D02剩余并入D03；D07已关闭范围保留。
- 解阻条件：能强制宿主写入仅项目隔离目录，能可靠清点/后台启动/回收launcher并核无残留；固定同候选本地安装；在原生接通已授权MiniMax与可信会话；再跑真实UI、M2回执/读回/失败恢复。不是要求Abram再次裁定身份/provider。
- 本地catalog/install_staged路线可行；无需AppHub publish、公开签名或listing。离线私钥已删除。本轮无欠费观察，无必须用户授权的残余阻塞：**NEEDS_ABRAM=no**。
- 先前门禁：M2维持FAIL，本轮仅受影响路径分析/局部反例，未给其PASS；M0/M1和M4–M7不修改。
- 门禁：仅更新GATES.json的M3审查字段、状态及review_report；保存此前作者审查字段到M3 review_history。不修改既有ACCEPTANCE.json历史记录。
- 不允许进入下一模块；留在M3按原编号修复后交新候选再审。本轮未修业务、未reset/stash/删他人改动。

STATUS=FAIL
NEEDS_ABRAM=no
