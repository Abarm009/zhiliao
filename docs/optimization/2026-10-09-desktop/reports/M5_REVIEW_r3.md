# M5 独立 Review r3

**结论：FAIL。候选：M5-r3-worktree。置信度：高（锁定源码、隔离字节反例与官方 Store 安装）；未知（发行宿主 UI、可信独立业务会话、权威任务/回执）。**

- 审查者 / 日期：当前 Codex 会话唯一独立审查者，2026-10-11，Asia/Shanghai；未委派代理。当前工具没有可核验的主会话 Router 路由 / gpt-6.1-sol 切换证据，不能声称已按指定模型切换。
- candidate_id / HEAD：`M5-r3-worktree` / `8d730569546cb57310944bb299695134df773b9d` 加未提交改动。以 GATES `r3_handoff_summary`、r3 实施报告、r3 CANDIDATE 三者的交接记录定位，不以 mtime 选版。
- 内容：`main.splash` SHA-256=`ef4299405caeb5c68bea0dd615ad6df7c555191db5d65ae28c4ad307fbd5c872`，352311 B；实际换行符数7650，清单7645属于建议修正，不据此FAIL。开始/结束清单见 `results/start-snapshot.json` / `final-verification.json`。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M5_IMPLEMENTATION_r3.md`；清单：`runtime/optimization/2026-10-09/M5/r3/CANDIDATE.json`。
- 前置：M4-r4 的独立 Review 仍 FAIL（D-M4-03/04），没有已接受 PASS 候选。按本次用户前序挂账裁决继续 M5 缺陷复核，不修 M4，也不把 M4 FAIL 改称 PASS。当前候选与 M4-r4 的11个受影响既有函数内容一致；本轮FAIL有独立的M5核心反例，非因建议或挂账项判退。
- 已阅读：项目 AGENTS、CONTEXT_M5（其r1内容不当作当前事实）、00/01/02及04模板、本模块要求、M5 r2 Review与r3交接材料；只查D01～05及受影响相关函数/既有验收定义，没有无关扩审。旧D06保持闭合。
- 实际环境：指定 launcher 文件SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；本轮未启动 launcher、未用--help。本地 ScriptVm 探针仅是测试工具，不是该发行 launcher。
- 证据根：`runtime/optimization/2026-10-09/M5/review-r3/`。下文 `results/…` 均相对于此目录。
- 范围偏离：初始检查误读项目外 `/Users/abeam/.codex/memories/MEMORY.md` 与技能说明，违反本次“仅项目内部读写”。未在项目外写入；发现后后续显式文件操作限定项目内。不能把本轮描述为“全程无项目外读取”。旧记忆没有替代本轮验收结果。对话createdAt/标题及实际Router路由未核验、未设置，不能用当前日期或委派假冒完成。
- 未读/打印/修改 `runtime/identity/CREDENTIALS_FOR_ABRAM.md`；未读取MiniMax密钥、未调用模型（0次）。身份来源与provider已经裁决，不再是NEEDS_ABRAM。

## 必需检查

|检查|独立操作|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选及差异|核交接三处ID、哈希，冻结当前源；比r2及M4-r4|同一候选可定位|当前源匹配交接SHA；r2→r3差异已保存；11个前序函数同内容|PASS（内容）|start-snapshot.json、M5-r2-to-r3.diff、followup.json|
|安全启动条件|新隔离目录环境重定向，sandbox-exec true及进程枚举|可禁止外写并核清理|sandbox rc71 `sandbox_apply: Operation not permitted`；pgrep rc3 `Cannot get process list`|BLOCKED；未启动|preflight.json、isolation.sb|
|本轮离线安装|当前源复制打包、sandbox-only签名/catalog，官方Store install/rebuild/may_run|当前digest安装、篡改拒绝、恢复成功|digest=`e3d220e26c44b751ca9989a0ee2f765892d05c34e69624cb2cf196ffa13d3395`；main/config/identities安装副本逐字节一致；篡改rc1/恢复rc0|PASS（Store层）|local-store-validation.json、local-store-run.log|
|私钥删除|finally删两私钥，检查目录|无私钥遗留|working.key、anchor.key删除；remaining_key_files=[]|PASS|local-store-validation.json；final-verification.json|
|新文件损坏/缺失/跨任务|本轮新造148 B文件，保存测试副本；两个入口分别注入坏件/缺失/异任务/隔离/拒绝/错轮|提交及验收均拒|一般损坏、缺失、跨任务、DENIED/QUARANTINED/错轮在源码适配探针均拒；中段等长损坏两个入口均放行|FAIL D05；原生BLOCKED|review-probes.json、review_probes.py、sandbox/inbox/reviewer-new-evidence.txt|
|固定集合/旧证据|两件提交后移除并删除一件；提交→退回→显式复用|不跳过缺件；旧引用保留、新轮次|丢失固定成员拒；未选旧证据拒，显式选择后轮次[1,2]、旧ID/字节保留（适配探针）|D03源码子项闭合；完整运行BLOCKED|review-probes.json|
|保存初判|注入同尺寸异内容写盘|READY前全量内容一致|源与存盘不等，仍返回READY|FAIL D05|followup.json：save_readback_counterexample|
|内容出口|查open返回→按钮命令→UI消费|实际内容可查看|返回content已补；按钮仍丢弃content，只写状态|FAIL D01|main.splash:4953、6004|
|可信独立会话|多角色同ID、经理无/有理由源守卫；核实际会话运行材料|可信独立主体、权威事实一致|仅synthetic会话探针；守卫符合源码预期；没有真实会话及回执运行|BLOCKED|review-probes.json、preflight.json|
|正常/退回/重启|适配正常与退回链；另开Python进程读真实保存文件与索引|实际UI/字节/任务事实/回执一致|适配正常/显式复用链成立；新进程实读148 B及SHA一致；均不是实际应用链/重启|BLOCKED（完整检查）|review-probes.json：new_process_byte_read|
|失败恢复|submit commit=false；reject commit=false|任务/轮次/索引一致恢复|submit回退子项成立；reject在commit=false后索引已写轮次0|D04部分修复/FAIL|review-probes.json、main.splash:5732|
|实际ScriptVm|运行未改动摘出的hash/path函数|实际运行结果可读|hash探针解析错误、无observed；path探针`method slice not found on string` rc1|NOT_RUN成功语义；不能按退出码0称PASS|vm-hash-path.json、followup.json|

源码适配探针明确替换了身份、command、commit、fs及十六进制格式化依赖；采用真实隔离文件，并执行当前M5指纹混合/映射控制流。它证明指定控制流反例，不能证明可信会话、发行宿主命令、事务或权威回执。ScriptVm本身与发行宿主兼容性未证实，两个VM失败保留，不外推为该launcher的确定运行结果。

### 上轮缺陷闭合

|编号|本轮结论|成立子项|剩余|
|---|---|---|---|
|D-M5-01|未闭合，P1|open函数返回内容/元数据|UI丢弃返回内容，没有用户可见内容出口|
|D-M5-02|部分修复，P1 / 原生隔离BLOCKED|删除任意inbox兜底|绝对路径与实际相对根不匹配；根仍可变/依赖cwd；链接拒绝没有目标宿主证明|
|D-M5-03|固定集合缺件反例的源码子项已闭合|验收消费completion固定ID/摘要；缺成员、错任务、错轮均拒|完整可信主体及原生链BLOCKED；摘要可靠性归D05，不重新另立同一缺陷|
|D-M5-04|部分修复，P1|固定摘要结构、旧证据不自动复用、显式选后新轮/旧字节、submit失败内存回退|指纹内容绑定归D05；绑定/退回索引仍先写，失败/崩溃一致恢复未闭合|
|D-M5-05|未闭合，P1|脱离首换行上界，遍历范围扩大|字符近似映射忽略内容、首尾不能覆盖中段；READY仍只按大小；二进制未实证|
|D-M5-06|维持上一轮闭合|原作者脚本外部写整改|本轮审查开头外读偏离另行披露，不伪造其为构建方D06复发|

## 缺陷

### D-M5-01 / P1 / 必修：返回内容仍未接到桌面展示

- 文件行：`app/bundle/main.splash:4953`、`:6004`（按钮命令）、`:7197`（点击入口）。
- 触发：合法附件“打开/重读”→m5_cmd_openAttach→m5_open_attach_bound。
- 实际/预期：底层r.content/content_preview已存在，但命令只读r.lifecycle/r.reason、更新STATE.status；全源仅在返回对象处出现content_preview，没有展示/下载/OS打开消费者。预期验收人能实际查看同一保存证据内容。
- 根因/影响：修了返回值，未完成产品链；“READY/重新打开”状态不能代替维修事实可见。阻断硬验收1/5、T19合法附件实际下载。
- 证据：review-probes.json/source_outlets、冻结源码、r2→r3.diff；原生点击BLOCKED。
- 具体改法：在既有桌面附件区域消费经过当前可信主体授权的内容/预览或实有宿主打开能力；不能只把内容返回给无人读取的局部变量。
- 验证：本轮新文件实际显示/打开并与保存字节比对，重启再打开；坏件/无权不出内容、重试可恢复；提交截图、task_id和权威回执一致证据。

### D-M5-02 / P1 / 必修：实际根/路径契约未闭合，链接隔离仍BLOCKED

- 文件行：`main.splash:1182`、`:1209`、`:1718`、`:4478`、`:4550`、`:4589`。
- 触发：真实绝对inbox文件路径传入上传；更换cwd/宿主app-data；inbox链接指向非inbox测试副本。
- 实际/预期：m5_sandbox_root_abs实为`"./"+STATE.attach_sandbox_root`；m4默认先写r1相对路径，使m5的nil兜底r3通常不生效。收紧后的字面前缀无法匹配绝对路径；作者和本轮适配正常例均注入了绝对m5_inbox_abs，不能证明实际源根。适配根下链接守卫返回true，但本地测试fs会跟随，目标发行host是否拒绝没有证明。预期可信固定根、部署cwd无关、合法文件可入且实际链接越界拒绝。
- 根因/影响：名称叫abs但仍相对/可变；路径测试替换了待测依赖；已有链接隔离硬缺口未闭合，影响附件入口和隔离安全。
- 证据：源码上述行、review-probes.json/symlink_and_paths_adapter、default-root-probe.json（实际根函数配置到本轮新文件inbox后绝对路径仍false）、作者报告D02仍BLOCKED；VM路径探针失败不作为成功路径证据。测试只指向项目内副本，没有读取外部目标。不能据此声称发行宿主已发生越界读。
- 具体改法：明确目标host文件路径语义，以可信宿主分配的项目内隔离根/获准引用完成导入；统一输入和保存路径，不再依赖app-data cwd。利用已实测宿主链接防护并交证据；若确实不可实施，给最小复现并保留BLOCKED，不能把相对根拼接叫真实绝对根。
- 验证：未替换实际根函数的正常输入、另一inbox、同项目越界链接、父穿越及根篡改；不同cwd/安装app-data仍只在本项目授权目录读写。

### D-M5-04 / P1 / 必修：本模块索引仍可先于提交/退回提交完成，失败恢复未闭合

- 文件行：`main.splash:4833`、`:5159`、`:5516`、`:5524`、`:5539`、`:5732`。
- 触发：完工绑定后、commit前注入异常；成功提交后退回时commit失败；索引写入失败或此窗口重启。
- 实际/预期：m5_bind_round内部仍m5_save_attach_index（5159），因此作者“仅commit成功后落索引”不成立；本轮submit commit=false的内存/索引回退子项已修。reject先清轮次/标退回并写索引，后commit；失败仅refreshLabels/return，适配注入后保存索引round=0。实际权威业务回滚尚未实测。预期失败/重启恢复同一已接受状态、轮次、证据集合，不留提前绑定或提前退回索引。
- 根因/影响：附件索引仍是提交协议外的单独副作用，不能由成功末尾再写一次替代原子性/恢复。m5_save_attach_index吞掉异常仅拼状态，调用者还可继续成功状态。直接关联旧D04失败恢复、T22/U07；不要求重写前序M2通用事务。
- 证据：review-probes.json：failed_submit_commit / failed_reject_commit；冻结源码上述行。
- 具体改法：仅对M5建立统一提交/恢复记录及任务、轮次、索引快照；移除绑定阶段独立提前持久化，索引错误可传播并恢复；补退回失败恢复，而不是只处理submit的布尔失败。保留旧记录/旧字节。
- 验证：提交/退回的索引写入异常、commit失败及中途退出重启；读回任务、两轮固定引用、真实字节和回执一致；失败后可重试。

### D-M5-05 / P1 / 必修：中段损坏被摘要忽略，两个入口都可通过

- 文件行：`main.splash:4627`、`:4698`、`:4730`、`:4794`、`:5244`；作者驱动 `runtime/optimization/2026-10-09/M5/r3/scripts/r3_fix_driver.py:145`。
- 触发：新148 B文件，中段80个`v`改为80个`w`，首尾32字符不变；分别在提交前/提交后改变保存副本。额外在复制写盘阶段注入同尺寸损坏。
- 实际/预期：两份独立SHA-256分别`99ff465b5a7fcc529b8b519cbc56fba3e87515e3c747a3cb2a161b476b44db0e` / `50373e6f8a441bc86f5e12f58ec7280f548b180d10ea6b241a4b7b10449815e1`，当前M5指纹同为`71cc362b`；prefix/suffix同。源码适配提交到AWAITING_ACCEPTANCE、验收到COMPLETED，预期两者拒绝。保存阶段同尺寸异内容仍READY。
- 根因：_hex_nibble_of_char对v/w等都返回0，大小写/多个字符也同映射；cl和位置无法编码字符真实内容。prefix/suffix只防边缘变化；READY仍只比大小。作者17项驱动把m5_fingerprint替换为Python fp，因此“不同尾指纹”验证的并不是本次新实现。
- 影响：真实损坏检测与不可变证据内容绑定失效，核心硬验收2直接失败。不是偶然碰撞概率或美观问题，能确定构造大量被完全忽略的中段差异。
- 证据：review-probes.json/hash_counterexample及submit_middle_collision/accept_middle_collision，followup.json/save_readback_counterexample；保留源与新测试文件。本轮实执行的是源码适配控制流；实际本地ScriptVm hash解析失败、没有observed，发行host不可运行，不能声称原生已推进事实。
- 具体改法：使用目标宿主实测可用的完整字节摘要/编码方案，逐真实字节区分所有值；不要近似nibble常量或仅用首尾。保存后全量比对再READY；测试调用实际实现，保留Python独立SHA仅作交叉核验。不可用则交最小原语复现并BLOCKED。
- 验证：中段v/w、大小写、等尺寸尾改、UTF-8、真实PNG/PDF、NUL/非UTF8、>64KiB及边界；保存、submit、accept和重启均核真实全量字节，损坏全部拒。

### 建议挂账（P2，不据此FAIL）

- A-M5-01：纠正清单行数；r3证据清单包含不存在或拼错的translated路径、测试范围表仍称11函数未触碰且引用旧r2。本轮已经比当前M4-r4确认11函数同内容；不要让这些表述替代真实运行。
- A-M5-02：accept事件已读取opinion与proxy reason，源码写入子项成立；作者断言只检查COMPLETED，并未捕获事件意见。最终真实事件/回执还需在可信会话中读回，不另据此FAIL。
- A-M5-03：旧确认/AI失效按前序挂账；源码与M4-r4同内容。D04本轮新增reuse_ids仅有初始化/读取，没有UI赋值；可补明确选择入口，但新附件链及核心修复优先，勿扩修下一模块。

## 全部硬验收与相关既有用例

|硬验收|本轮结论|
|---|---|
|1 真实选择、保存、重启打开|FAIL D01/D02/D05；原生选择/重启BLOCKED，新Python进程字节读取只属子项|
|2 坏/缺失/隔离/他人/无权/过期证据拒|FAIL D05中段反例；其他负例源码子项成立；真实撤权会话BLOCKED|
|3 完工仅待验收、可信独立验收|BLOCKED；synthetic自验/经理理由守卫成立，不能代可信会话|
|4 退回历史、新轮、明确引用|D03固定集合子项闭合，D04部分修复；FAIL恢复/内容完整性；原生完整退回链BLOCKED|
|5 桌面附件/失败恢复/终态只读、正常退回链|FAIL D01；完整发行桌面/权威结果BLOCKED|

|用例|结论与范围|
|---|---|
|G0-D|FAIL D01/D02/D04/D05；当前Store层PASS；真实附件原生链BLOCKED|
|T18|BLOCKED可信访问主体、列表/搜索/事件/附件探测；跨任务源码子项拒绝；前序身份缺陷挂账|
|T19|FAIL中段损坏、实际内容出口；缺失/隔离/异任务源码拒绝、固定缺件修复；合法下载原生BLOCKED|
|T20|BLOCKED可信主体/权威状态；适配仅待验、自验禁令、经理理由子项成立|
|T21|适配退回/显式reuse/新ID/轮次[1,2]/旧字节子项成立；完整原生BLOCKED，D04/D05剩余关联|
|T22|FAIL本模块索引恢复D04；真实任务/事件/回执事务运行BLOCKED；不扩修M2|
|T28|BLOCKED指定launcher同task操作/回读/重开；Store安装/重建PASS不代替|
|T31|BLOCKED取消/终态再次操作/新关联任务原生；sourceOk与M4-r4内容一致|
|T35|BLOCKED实际迟到建议/版本失效；前序D-M4-04挂账，confirm函数未改|
|U03|BLOCKED三可信角色事实/权限一致；synthetic切换不作验收|
|U06|旧记录/字节及固定ID源码子项成立；D04/D05剩余影响；实际UI历史BLOCKED|
|U07|FAIL本模块索引恢复D04；submit布尔失败回退已修；真实重复/丢响应/离线/重启BLOCKED|
|U08|FAIL D01无附件内容出口；真实失败/权限/建议恢复BLOCKED|
|U11|BLOCKED真实host滚动/输入/面板及真实进度；没有拿截图或旧日志代替|

定义来源：`docs/build-loop/ACCEPTANCE.json:69`、`docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md:72`、`docs/implementation/09_AGENT_HARNESS.md:99`、`docs/implementation/10_UI_UX_SPEC.md:175`。没有改变旧后端/旧桌面验收历史，也没有因该历史自动继承PASS。

## 判定

- 最终结论：**FAIL**。必修D-M5-01/02/04/05；D-M5-03固定集合缺件源码子项闭合，D06保持闭合。建议、行数偏差或挂账前序不是本次FAIL依据。
- 精确范围：当前r3冻结源、真实隔离字节及适配控制流、官方离线Store路线已独立检查；完整桌面、可信独立会话、实际业务command和权威回执仍BLOCKED/NOT_RUN。不能用17/17作者断言或Store PASS替代M5核心成立。
- 本地路线：当前digest可走本地catalog/install_staged，无需公开publish/listing。隔离离线签名已执行，两私钥已删除并留证；没有网络、上传、push、issue/评论、消息或公网部署动作。
- 解阻：允许强制项目内写/禁止外写的隔离运行及进程枚举/关闭/窗口残留核对；确认指定发行host可用文件/字符串/摘要原语；复用已裁决5账号来源接通现有可信会话，独立造隔离测试账号（不读原明文凭据）。之后后台启动指定launcher、用相同digest跑新文件负例/正常链/退回链/重启/终态/真实回执，测完立即关闭并读回无残留。本轮未启动，无新增窗口；已有窗口未知，不能伪称已清空。
- 修复交接：仅修D01内容消费者、D02实际根与host隔离证据、D04本模块索引恢复、D05真实完整字节实现；保留D03/D06已成立子项。提供新candidate_id/哈希/差异与本轮真实运行证据，按原编号复审，不进入后续模块。
- 门禁：仅改GATES.json中M5的status及审查字段，保存先前审查状态历史；不改作者交接字段/其他模块。不改ACCEPTANCE.json，以本报告范围表及M5门禁记录当前原生验收，保留原台账历史来源。
- 下一模块：不允许；未执行。
- NEEDS_ABRAM=no：身份/provider及离线签名已有授权；本地Store可行，未遇计费错误。当前代码和安全运行/能力验证缺口不需要新Abram授权。

STATUS=FAIL
NEEDS_ABRAM=no
