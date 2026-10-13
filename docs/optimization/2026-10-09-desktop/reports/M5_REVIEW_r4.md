# M5 独立 Review r4

**结论：FAIL。候选：M5-r4-worktree。置信度：高（固定源码、隔离字节反例、Store 安装层）；未知（发行宿主真实 UI、可信业务会话、权威事实与回执）。**

- 审查者 / 日期：当前 Codex 主会话唯一独立审查者，2026-10-11，Asia/Shanghai；没有委派代理。
- candidate_id / base_candidate_id：`M5-r4-worktree` / `M5-r3-worktree`。按 GATES 当前交接字段、r4 实施报告和 CANDIDATE 三方一致定位，不按修改时间选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d` 加既有未提交差异；不是干净提交。冻结 `main.splash` SHA-256=`e7e0e713eb68303a0fc23a9d2e2fe5ef253817f5a6b65c9af11d5e0b94ac91a2`，360796 B、7782 个换行；匹配交接清单和作者 r4 快照。开始/结束核对见证据。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M5_IMPLEMENTATION_r4.md`。候选清单：`runtime/optimization/2026-10-09/M5/r4/CANDIDATE.json`。
- 前置：M4-r4 独立 Review 仍 FAIL（D-M4-03/04），没有已接受 PASS 候选。按本次用户前序挂账裁决继续本模块修复复核；不修 M4，不改其结论，不把前置写成 PASS。r4 与 M4-r4 的11个受影响既有函数内容一致。
- 阅读范围：实际 AGENTS、CONTEXT_M5（r1浓缩内容只作索引）、00/01/02/04模板、M5模块要求、M5_REVIEW_r3、当前实施报告/清单/证据及上轮缺陷涉及函数、相关既有验收定义。只复核 D01～06及受影响回归，没有展开下一模块。
- 宿主：指定 launcher `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`；二进制 SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮**没有启动 launcher，没有使用 --help，没有新增宿主窗口**；已有窗口无法枚举，状态 UNKNOWN。
- 模型路由/标题：当前工具没有可验证的 Router / gpt-6.1-sol 切换或对话 createdAt/标题能力；未声称已切换或已命名。未调用真实模型（0次）。
- 证据根：`runtime/optimization/2026-10-09/M5/review-r4/`；下文 `results/…` 均相对该目录。测试副本、HOME、app-data、缓存、日志、临时目录全部放本目录，未在项目外写入，未修改原业务数据、业务代码或其他模块门禁。
- 范围偏离：开头误读项目外记忆注册表和技能说明，违反本次“仅项目内读写”；后续显式文件操作限定项目内。不能称全程满足读取边界。记忆没有作为本轮候选/验收依据。
- 未读取、打印或修改 `runtime/identity/CREDENTIALS_FOR_ABRAM.md`；账号表/安装映射仅核内容摘要，未改原账号或原宿主数据；未读取 provider 密钥。身份来源和 MiniMax 已裁决，不是待授权事项。没有联网、上传、publish、公开签名/listing、push、Issue/评论、消息或公网部署。

## 必需检查

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、前置、增量|三方交接定位、冻结摘要、r3→r4差异、末核|同一候选可定位，前置已接受|当前候选匹配；M4仍FAIL，11函数同内容|候选定位成立；前置未PASS|start-snapshot、r3-to-r4.diff、gates-before、source-evidence-audit、final-verification|
|隔离启动条件|新隔离目录重定向环境，sandbox-exec true及pgrep|强制外写禁止，可核进程/窗口清理|rc71 `sandbox_apply: Operation not permitted`；pgrep rc3 `Cannot get process list`|BLOCKED；不启动launcher|preflight.json、isolation.sb|
|新文件及两个入口反例|新造160 B文件、保存副本；提交前/提交后分别损坏、删除、改task_id、隔离、拒绝、错轮|均拒绝|一般坏件/缺失/异任务/隔离/拒绝/错轮均拒；中段0x01→0x02两个入口均放行|FAIL D05；完整原生BLOCKED|review-probes.json、review_probes.py、sandbox/inbox/reviewer-new-binary.bin|
|保存初判|写盘适配器注入同尺寸异内容，执行本轮保存控制流|全量读回相同才READY|saved_equals_source=false、same_size=true，仍READY|FAIL D05|review-probes.json：save_equal_size_corruption|
|固定集合、旧证据|两件提交后删除/移除一件；退回未选择/显式复用再提交|不能跳过缺件；旧记录字节保留、新轮次|固定成员缺失拒；未选旧证据拒，显式选择后[1,2]、旧ID/字节保留|D03源码子项保持；完整原生BLOCKED|review-probes.json：fixed_member_missing、return_explicit_reuse|
|禁止自验、经理理由|合成多角色同ID及经理无/有理由控制流；核可信会话证据|可信独立主体，权限/回执真实|同ID自验拒、经理无理由拒、有理由允许；全部synthetic主体，没有可信运行|BLOCKED；不把标签/桩当会话|review-probes.json、preflight.json|
|正常链、退回链、重启|适配正常/显式复用链；新Python进程读取真实文件/索引|UI、字节、权威任务/回执一致|适配链可到COMPLETED；新进程读160 B及SHA一致；不是应用重启、实际命令或权威回执|完整检查BLOCKED|review-probes.json：normal_adapter、return_explicit_reuse、new_process_read|
|失败恢复|submit/reject布尔提交失败；成功提交后索引写失败适配注入|失败可对账、索引/任务轮次一致|布尔失败内存回退成立，reject索引保持；索引错误被吞后仍显示成功，磁盘/内存轮次不同|PARTIAL / FAIL D04|review-probes.json：failed_*、index_failure_*|
|实际局部VM|不改函数源码执行根、字符查找、路径、索引写失败|目标原语与观察结果明确|root_only rc0且观察绝对根；index_of/slice不存在，索引catch报`variable _ not found`，均无observed|根子项成立；其余成功语义NOT_RUN，发行宿主BLOCKED|followup.json、probes/*.splash|
|本轮本地安装|当前源码筛选副本，离线keygen/certify/stamp/sign/verify，官方install_staged、Store重建/may_run，篡改及恢复|同digest可安装，篡改拒，恢复成功|当前副本digest=`2cbdfaa3d5e1910e6b254ba99cfc015cb03f559597e996f5f2523658f0a0361d`，三文件安装字节一致，篡改rc1、安装/恢复rc0|PASS安装层|local-store-validation.json、local-store-run.log|
|私钥删除|finally删除两key并末核目录|私钥不残留|working.key、anchor.key已删，remaining_key_files=[]|PASS|local-store-validation.json、final-verification.json|

### 证据边界

1. 字节反例执行冻结 r4 函数的 Python 语法适配控制流：身份、command、commit、时钟和部分索引/文件系统依赖是桩。字符串 `slice` 按 latin1一字节切片，三张映射表从当前源码字符串字面量解析，查找用Python find，FNV混合/分支/循环由源函数翻译执行。它证明算法在字节切片假设下的确定反例，**不称为发行宿主已经写入错误终态**。若发行宿主不提供这些原语，则运行能力本身未闭合。
2. 保存阶段 fs.write 的同尺寸损坏是显式测试注入。注入后真正保存字节和源字节不同；源码READY只比较尺寸，这是独立的源码缺陷，不依赖指纹碰撞。
3. 索引写失败探针把索引函数替换为“错误被吞、设置状态”的分支适配，精确对应当前 `m5_save_attach_index` catch。任务事实文件由合成commit写，不是应用权威任务或回执。实际局部VM未成功运行该catch，不能把适配探针称作宿主异常恢复验证。
4. 局部 `identity-vm-probe` SHA-256=`204b5892fad7fcfc0cb634a638e8067e73760018bbcb014ced2f3547ea2cbede`，不是发行launcher。index_of、slice、catch错误均保留，不外推成发行宿主确定不支持；不得把rc0或作者Python实现当真实平台能力。真实UI/可信主体/终态只读/失败重启均BLOCKED。
5. 离线包仅复制main、manifest、公开身份配置、模型配置、listing和资源，排除原业务data/log/backup，签的是sandbox副本。原manifest不改；安装层PASS不代原manifest历史digest或业务运行。私钥仅当前测试、无公开发布；两文件删除路径及空目录已留证。
6. 作者27/27不继承为独立验收。r4_fix_driver使用Python字符串/映射适配；r4_review_probes:43/75直接用自写fp覆盖指纹，且:222以注入根startswith判断“绝对根”。本轮另用未改根函数在局部VM观察结果。清单引用的 `results/r4-review-probes.json` 实际缺失，不能把汇总布尔值当该文件运行证据。

### 上轮缺陷闭合表

|编号|本轮状态|已成立改善|剩余|
|---|---|---|---|
|D-M5-01|PARTIAL：内容出口源码子项关闭；完整桌面BLOCKED|command写last_open_attach、refreshDetail消费content/preview|真实查看/下载/重启/失败出口未运行；Label最多4行，无实际可读性证据|
|D-M5-02|PARTIAL / 安全运行BLOCKED|默认绝对根、cwd无关根函数局部VM成立|STATE根仍直接信任，链接目标未约束；实际路径原语及launcher强制隔离无证明|
|D-M5-03|维持关闭的固定集合源码子项|固定completion ID集合缺成员不能靠readyCount绕过|完整可信链BLOCKED；内容可靠性归D05|
|D-M5-04|PARTIAL / P1 OPEN|bind不再主动落索引；reject布尔失败回退；旧证据/新轮/显式复用保持|索引失败被吞、commit后索引不一致、崩溃重启恢复未闭合|
|D-M5-05|PARTIAL / P1 OPEN|旧v/w中段损坏两个入口现在拒|非printable内容被忽略；同尺寸保存仍READY；真实二进制/UTF-8原语未证实|
|D-M5-06|维持上一轮闭合|不复发构建方外写问题|本审开头项目外读取偏离单独披露，不归咎构建方|

## 缺陷

### D-M5-05 — P1 / 必修 / PARTIAL：只修printable ASCII，非printable损坏仍放行；保存仍只核大小

- 文件与行：`app/bundle/main.splash:4646`（READY尺寸判断）、`:4735`（指纹）、`:4761`（fallback）、`:4797`与`:4804`（两张所谓nibble表）。
- 触发：审查方新造160 B二进制证据，ASCII首尾各不少于32字节，中段80个0x01；存盘后同位置改为80个0x02。分别在再次提交完工前和待验收后操作保存副本；另对初次写盘注入等尺寸损坏。
- 实际：源SHA-256=`6a3b99eea8f7d5ab609ecdf2a361e8d656f50fe47db50d95714d41b608fe69d8`，坏件SHA-256=`7024be78ff0e933b9829ed44f7c2d11cfdfe5f6bf73dc84ffc56d02ad3377272`；当前算法两者均`f1da7803`，尺寸/首尾相同。适配submit推进AWAITING_ACCEPTANCE、accept推进COMPLETED，无拒绝错误。初次保存源/盘字节不同仍READY。旧v/w负例已拒绝，保留改善。
- 预期：真实全量字节发生变化，保存、完工和验收均拒，不能靠长度/首尾或READY元数据放行。
- 根因：low_table=`0123456789abcdef`、high_table=`ABCDEFGHIJKLMNOP`均仅ASCII字符，不能从控制/高字节反查nibble。所有不在printable表的字节都进同一仅依赖位置i的fallback，内容值完全不参与。不是小概率哈希碰撞。保存阶段另仍只比较back_size与bytes_size，未比完整内容。
- 影响：核心硬验收2与真实附件完工/验收内容绑定直接失效；附件并不限printable文本。阻断硬1/2、T19、U08，不是建议或前序挂账。
- 证据：`results/review-probes.json`的hash_counterexample、submit_control_middle、accept_control_middle、save_equal_size_corruption；冻结源、独立新文件及本轮探针。发行宿主实际推进事实仍未知。
- 具体改法：先确认目标宿主实际可用的二进制读写、逐字节编码/摘要能力，使用完整内容值参与可靠摘要或完整比对；不得用ASCII查表假冒任意字节nibble。保存后完整读回一致才READY；submit/accept重新核固定内容。能力不可用交最小复现并BLOCKED，不偷偷缩成仅ASCII附件。
- 验证方式：实际实现处理0x01/0x02、NUL、0x80/0x81、UTF-8、真实PNG/PDF及>64KiB边界，逐保存/提交/验收/重启检查全量内容；新文件保存后坏/缺/跨任务均拒。独立SHA作为对照，测试不能替换待测算法成Python fp。

### D-M5-04 — P1 / 必修 / PARTIAL：commit后写索引不等于原子，错误被吞后成功提示掩盖分裂状态

- 文件与行：`main.splash:4865`（索引writer吞异常）、`:4873`（重启load直接替换索引）、`:5584`/`:5593`（提交后索引与成功状态）、`:5822`/`:5827`（退回后索引与成功状态）、`:963`（启动加载）。
- 触发：合法待提交或待验收任务；task commit成功后evidence_index.json写入失败，或在commit与索引写间中断/重启。本轮适配注入检查提交、退回两条。
- 实际：submit显示“完工已提交”，内存round=1，原磁盘索引round=0；reject显示“已退回”，内存round=0，磁盘索引round=1。错误信息先写STATE.status，随后成功串覆盖。布尔commit=false的reject回退与索引保持已修；submit布尔失败轮次回0，索引内容变化含校验时间等，不将其单独定为任务损坏。
- 预期：索引错误能传播，UI不得报完全成功；任务、固定证据集合、轮次、历史与回执有同一个可对账提交/恢复结果，重启恢复并允许重试。
- 根因：m5_save_attach_index没有返回可核成功结果；commit与索引仍两个独立写入，无M5恢复协议。仅把索引挪到commit后，解决了一个提前写窗口，但产生/保留另一个窗口；load会用旧索引覆盖STATE.attach_items。作者报告“保证原子”没有依据。
- 影响：本模块提交/退回与重启证据轮次不一致，错误被成功提示掩盖，核心硬4/5、T22/U07未闭合。不要求重写前序M2通用事务。
- 证据：`results/review-probes.json`的index_failure_submit/index_failure_reject、步骤commit→index_write_failed_swallowed；上述冻结源。真实权威事务、崩溃重启及回执BLOCKED，未称原应用已发生该故障。
- 具体改法：仅在M5建立可核验的共同提交/恢复记录（任务版本、completion固定集合、轮次、索引快照与回执关联）；索引错误上报，启动先按权威已提交版本恢复再提供操作，不直接覆盖旧索引。确保提交/退回全过程失败处理，而非只处理布尔false。
- 验证方式：两条链分别注入writer异常、commit失败、commit后立即中断；重启核task/STATE/index/completion/真实字节/事件/回执一致，失败后重试不重复、不丢旧证据，无错误成功提示。

### D-M5-02 — 原编号安全缺口 / 必需BLOCKED：链接与固定根可信性尚无目标宿主证明

- 文件与行：`main.splash:1718`（直接返回STATE绝对根）、`:4495`（仅空时默认）、`:4572`（m5_path_in_inbox）（字面前缀）、`:4611`（导入读源）。
- 已改善：默认绝对根函数在未改源码局部VM实际返回预期；不再把相对根叫abs，不依赖cwd。
- 未闭合：用户/持久STATE非空根被直接采用，未核允许目录；字面前缀无法判断inbox链接的实际目标。项目内构造inbox链接→attachments测试文件，OS解析目标不在inbox，但未在发行宿主验证其是否拒绝。**没有访问项目外目标，没有声称真实宿主已越界。**
- 根因/影响：边界约束依赖未验证的宿主能力；本轮强制隔离又不能启用。涉及本次安全/隔离硬约束，不能因“优先完成”降成建议，也不能新增公开上架授权来解决。
- 证据：followup.json的root_only、project_local_symlink、source_root；preflight.json；作者报告明确symlink BLOCKED。
- 解阻/改法：用目标宿主已验证的受限引用或解析目标检查，根由可信宿主上下文固定并核允许范围；验证根篡改、链接、父穿越、另一inbox及更换cwd。能力不可行保留最小复现与BLOCKED，不引入未裁决服务。本轮FAIL主要由D04/D05已证源码反例决定，不将未发生的越界臆造为P1事故。

### D-M5-01 / 运行BLOCKED：消费路径已补，桌面查看与失败出口尚未成立

`main.splash:6101`写content到STATE、`:7666`消费内容成立，关闭“无人消费返回内容”的源码子项。实际Label `:6887`最多4行；失败返回的bytes/sha等是否完整、坏件→重试→重新打开、长文本/图片/PDF实际可看都未运行。只保留对应硬1/5、U08/U11的必需运行BLOCKED，不因视觉建议新增P1。

### B-M5-01 — 必需BLOCKED：隔离launcher、可信独立主体及真实命令链无法运行

本轮全新sandbox预检rc71、进程枚举rc3，原文见preflight。仅设HOME不能保证所有外写被禁止，当前不能确认宿主进程/桌面窗口回收，按用户硬约束不启动。正常链/退回链/重新打开附件、三可信主体的查询/写权限、自验/经理理由、终态只读、真实动作/回执和重启一致性均未运行成功。

解阻需可执行项目内强制读写隔离与可靠进程/窗口核验环境，后台启动指定launcher，finally关闭并读回无残留；消费已裁决真实账号来源，用项目内另造测试凭据和隔离会话，从真实任务到完工/独立验收，读取权威task/event/receipt，不切角色标签冒充身份。无需Abram再次授权身份/provider或离线签名。前序M4 FAIL保留，不由本轮代修。

### 建议挂账（P2，不作为FAIL依据）

- A-M5-01：CANDIDATE/evidence汇总引用不存在的r4-review-probes.json；修正证据路径、明确作者脚本与目标宿主运行边界。当前source SHA和快照可定位，不因该清单问题判FAIL。
- A-M5-02：验收意见/经理理由源码读取与写事件保持；本轮没有实际权威事件回读，不能沿作者布尔值签收。可信会话核心证据仍归B01，不扩大其他业务。
- A-M5-03：显式复用UI入口、长文本/二进制预览可读性继续挂账；补新附件核心链优先，不扩M6。闭合源码不等于完整UI通过。

## 全部硬验收与相关既有用例

|硬验收|本轮结论|
|---|---|
|1 真实选择、保存、重启重新打开|FAIL D05初次保存仅尺寸；D01消费/绝对根子项改善；原生选择/应用重启/真实内容查看BLOCKED|
|2 坏/缺/隔离/异任务/无权/旧轮不能通过|FAIL D05非printable中段反例；其他负例控制流拒；可信权限及目标宿主BLOCKED|
|3 完工仅待验、独立主体终验|BLOCKED；合成守卫和仅待验控制流成立，未验证真实可信会话/回执|
|4 退回历史、旧证据、新轮次/引用|PARTIAL固定集合/旧字节/轮次[1,2]/显式复用保持；FAIL D04恢复及D05内容绑定；原生BLOCKED|
|5 实际桌面/失败重试/终态只读/正常退回链|FAIL D04错误成功与恢复；D01消费源码改善；完整原生BLOCKED|

|用例|本轮结果与范围|
|---|---|
|G0-D|FAIL D04/D05；D02隔离BLOCKED；本轮Store层PASS不能代真实附件链|
|T18|BLOCKED可信查询/列表/搜索/事件/附件权限；跨任务源码反例拒，前序身份挂账|
|T19|FAIL D05中段损坏及保存初判；缺失/隔离/跨任务、固定集合缺件拒；合法下载原生BLOCKED|
|T20|BLOCKED真实会话/权威状态；合成自验禁令/经理理由/仅待验符合预期|
|T21|PARTIAL适配退回/新ID/两轮/旧字节/显式reuse保持；D04/D05未闭合；完整原生BLOCKED|
|T22|FAIL本模块索引D04；真正task/event/receipt失败事务与重启BLOCKED，不扩修M2|
|T28|BLOCKED指定launcher实际同task操作/回读/重开；当前digest安装/Store重建仅安装子项PASS|
|T31|BLOCKED真实取消释放、终态再次操作、新关联任务；sourceOk与M4同内容，不签完整PASS|
|T35|BLOCKED迟到建议/当前版本实际交错；confirm与M4同内容，前序D-M4-04挂账|
|U03|BLOCKED三可信角色事实与权限；合成角色不是可信独立会话|
|U06|PARTIAL旧记录ID/字节/新轮适配保持，D04/D05影响；实际历史UI BLOCKED|
|U07|FAIL D04索引错误成功；布尔失败回退改善；真实重复/丢响应/离线/重启BLOCKED|
|U08|D01内容消费者源码改善；FAIL D05假READY与D04错误成功；实际失败/无权/重试出口BLOCKED|
|U11|BLOCKED发行宿主实际滚动、输入、面板及进度；没有使用旧截图代验|

定义来源：`docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md:72`、`docs/implementation/09_AGENT_HARNESS.md:99`、`docs/implementation/10_UI_UX_SPEC.md:175`及模块硬验收。保留既有38业务/12UI/P0，未改变原验收台账或历史来源。

## 判定

- 最终结论：**FAIL**；精确范围是M5-r4相对r3原缺陷闭合及受影响回归。D04/D05是阻断真实附件核心功能的P1，建议与前序挂账不是FAIL理由。
- 必修清单：D05完整真实字节校验与保存全量读回；D04索引错误传播和提交/退回/重启一致恢复。D02安全隔离及B01可信原生运行解阻仍是必需条件，不得带条件PASS。
- 保留改善：D01消费出口、D02绝对根、D03固定集合、D04绑定不主动持久化/退回布尔失败回滚、D05旧v/w反例均有明确源码或局部证据；不要求撤销改善。
- 前序回归：11个相关M4函数逐内容比对相同；本轮重跑M5固定集合、旧证据、轮次、自验/经理理由控制流。原生先前结论复验BLOCKED，不改变M0～M4/M6/M7结论。
- 门禁：仅更新GATES M5 status和审查字段、归档前审查字段，review_report指本轮报告；candidate_id沿用已交接M5-r4-worktree。原ACCEPTANCE.json不改，不用适配探针覆盖旧历史或签原生通过。
- 下一模块：**不允许进入**；本轮只给M5修复及解阻清单，没有执行下一模块。
- NEEDS_ABRAM=no：身份/provider/离线签名已经授权；本地catalog路线可行，两私钥已删除；本轮0次真实模型请求，无余额/402错误。剩余是M5代码、隔离环境和运行证据问题。

STATUS=FAIL
NEEDS_ABRAM=no
