# M4 独立 Review r14

**最终结论：BLOCKED。** M4-r12-worktree 的冷启动加载、分类、保源与旧锁子项通过，8/8 隔离回收 CLEAN，新增业务 P1=0。上轮任务坏盘告警接线在单故障场景通过，但双故障场景仍有 P2 残留。真实 M3 建单到开工的核心链没有运行证据；同 Store 真并发及提交点故障/AI 交错不在当前 harness 白名单控制能力内，不能签整体 PASS。D-M4-03 依 Abram 裁决单独记 BLOCKED-HOST，不计 P1、不作为 FAIL 理由。

- 审查者 / 日期：Codex 主会话，2026-10-13 Asia/Shanghai；独立审查，无子代理。
- candidate_id / base：**M4-r12-worktree / M4-r11-worktree**。HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty；冻结 main **769874 B / SHA256 07ecd2fddcfea116151378e8f1dd1e41cefd333f4c703d442bb1ae20cbb88b2a**。按用户交接请求及证据链定位，未按文件时间选版。
- 包 digest=`a6a5c30576a4432f2206013d2d903de9fef3eeed86d7d5b38201c49930ed9b97`；anchor=`3321ee0cca1fa528c548f30a9c9c21e89756c1a21ff2912102995e5bb016e7b0`。复用授权隔离离线签名及本地 install_staged Store，没有公开发布/重新签名。
- 宿主：实际 BIN=`runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`。作者实施报告写 M0/r3/host-rc6 是路径表述差异；本轮按实际 BIN 与 result 核验。
- harness SHA=`8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7`；profile.sb.tmpl SHA=`76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`。
- 前置：**M3=BLOCKED / M3-r10-worktree / M3_REVIEW_r14.md**，没有已接受整体 PASS；M2 按用户 carried 裁决。本轮挂账允许局部核对，不等于 M3 前置通过，不改前序门禁。
- 作者报告：`reports/M4_IMPLEMENTATION_r12.md`；上轮独立输入：`reports/M4_REVIEW_r13.md`。仅检查旧编号及直接差异回归，不做无关扩审或修业务。
- 已阅读范围：第 1 段 AGENTS/CONTEXT、00/01/02/M4/04、候选/实施/r13 缺陷、HARDFIX_PLAN 能力边界及相关源码/请求；第 2 段全部 8 场 summary/result/profile/probes/完整 log/denials/权威盘/frames/MANIFEST。
- 运行范围：**驱动**在沙箱外执行独立请求，21:06:21–21:08:50 +08:00，1 batch、8场、每场17.21–17.28秒，全部 quit_http、host rc0、无 ABORT。审查者没有启动宿主、执行 sandbox-exec/pgrep 预检或调用系统自动化。
- 主会话路由/指定模型和标题：未取得可验证的路由切换证明、线程 createdAt/设置工具，不声称主会话已切 Router/gpt-6.1-sol 或实际命名成功。
- 置信度：候选绑定、冷恢复/保源和告警残留的事实 **高**；真实业务主链、三角色、业务并发/撤销效果 **未知**。

路径约定：**E/**=`runtime/optimization/2026-10-09/M4/native/review_r2_1659/`；**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r2_1659_REQUEST_review_r2_1659/`；**A**=E/native-evidence-audit-r14.json。所有业务行号指 **E/source.main.splash**。

## 必需检查

|检查|独立步骤与期望|实际|结论 / 证据|
|---|---|---|---|
|候选/宿主/运行一致|核 frozen/seed/mirror/installed/running/日志/宿主摘要|证据审计时197项第1段快照无漂移；每场唯一运行包，业务eval=769874 B/view=true；写门禁前仅共享main发生漂移，未改审新源|PASS受审冻结包绑定，A/phase1-snapshot；新共享源不在结论内|
|冷启动解析与可见根|冷开实际作品，零错误、真实UI|8场零[E]/panic/未知动作、tick异常0、可见登录页|PASS冷根；认证工作台NOT_RUN，H/log/frames|
|合法数据正例|中文、转义、空白、非空合法DRAFT不误拒|402 B盘原样，pending=false，未装有效预约|PASS加载子项，三个valid场|
|错误类型、尾随、截断|整盘拒收、准确分类、主源/备份保全|第二成员bool时间拒；尾随/截断拒；主源、旧recover与本次副本字节吻合|PASS，三个单任务坏盘场及双故障盘面|
|任务恢复说明同屏|准确原因、恢复未决和备份事实可见|单故障3场完整显示；双故障仅历史说明，任务原因被覆盖|单故障PASS；双故障FAIL/P2建议，A-M4-R13-01 PARTIAL|
|旧锁/伪保存身份|未来/未知锁不清、旧锁回收、保存token不能复活|future39 B/unknown37 B不动；stale清空；actor/session=null、token空|PASS冷安全子项；不是并发/实际撤权验证|
|硬1权限与设备关系|可信角色/技能/项目拒绝、服务绑定、伪设备拒|没有实际接单/分配/绑定命令|NOT_RUN|
|硬2预约规则|提议、合规确认、过期、时区、跨项目冲突/改约拒绝|没有实际预约命令或时间表单输入|NOT_RUN|
|硬3真业务并发|同Store双上下文接单/重叠确认唯一赢家，相邻合法|当前schema/runner不表达共享双上下文和同步；相邻普通命令未跑|BLOCKED控制覆盖；相邻NOT_RUN；D03单独BLOCKED-HOST|
|硬4开工与旧授权|设备/有效预约不足拒，改派旧技工拒|没有实际改派/开工|NOT_RUN|
|硬5三角色与权威回执|真实输入、首屏、阶段/负责人/预约/动作回执一致|全部未认证；业务成功动作0；合成任务仅冷反例|NOT_RUN|
|旧确认/AI撤销与失败恢复|改派改约撤旧绑定，提交点失锁/中断/重试回读|源码守卫保持；没有实际交错或提交点失败注入|动态NOT_RUN；受控交错/写点注入BLOCKED|
|隔离与回收|profile/probes、预后进程、组回收、路径清单|8/8指定字段合格，无ABORT，无已证成功越界写|PASS证据范围，A|

### 八场独立原生结果

|场景|权威结果与精确通过范围|
|---|---|
|review_cold_no_tasks|tasks/lock/recover仍不存在，pending=false、历史原样、登录根完整、无假告警。PASS首次无任务冷开，不是M3创建|
|review_valid_future_unicode|402 B合法任务原样；39 B未来他人锁原样；pending=false/token空，正常登录页。PASS加载/保锁|
|review_second_bool_time_notice|792 B混合盘第二成员updatedAtMs=true整盘拒；recover逐字=坏原文；同屏精确第2条、拒写与备份读回。PASS分类/保源/告警|
|review_closed_junk_keep_backup|412 B数组后尾随垃圾原样、403 B合法旧recover原样、corrupt.latest=412 B坏源；同屏完整说明。PASS尾随拒收/旧备份保全|
|review_truncated_new_backup|377 B不同截断源不动，新recover逐字377 B；同屏原因、拒写、备份读回。PASS截断与无旧备份分支|
|review_tasks_and_history_notice|792 B坏任务与坏历史均原样、task recover与actions.bad_lines精确；pending=true/原因仍存。保源PASS；登录图只显示两段历史提示，任务恢复说明遗漏，告警子项FAIL/P2|
|review_valid_unknown_forged|402 B合法盘原样、37 B未知锁不动；unknown_kept；伪保存actor/session清为null，token空，无业务提交。PASS冷加载/身份不复活|
|review_valid_stale_no_notice|402 B合法盘原样，stamp=1锁清为0 B、released、token空；登录无任务告警。PASS崩溃旧锁boot回收，不代存活持有者互斥|

因此是 **8场冷权威/隔离子项通过，7场告警/对照预期完整、1场P2告警子项失败**，不是8个完整业务用例通过。

## 完整证据核验

实际命令：`PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/optimization/2026-10-09/M4/native/review_r2_1659/audit_phase2.py`，rc0。**7747项证据一致性及冷权威断言，0不匹配**；该数字不是业务用例数量，双故障视觉缺陷单独登记，未藏在一致性计数里。

1. **1745条 MANIFEST**逐条核摘要、唯一相对路径/归属、无symlink、精确文件集合；summary.request与独立请求全等，batch顺序与8份result投影字段全等。
2. **283项seed文件比较**与原独立准备完全一致；每场14资源×mirror/installed/唯一.running，共**336次资源比较**全等。digest_seen_in_seed=true；digest_seen_in_host_log=false，如实保留，不以marker未出现推定没加载；真实运行资源/业务eval构成加载证据。
3. 全部profile逐字重构并核摘要；12项HOME/app-data/tmp/cache等路径各自落run目录，网络只放本机控制口，无模型代理。profile_probes apply rc0，外写拒且created=false，五类禁读probe合格，osascript exec拒。只读这些记录，未再次访问禁读目标或真实HOME。
4. 八场pre/post严格rc1/NONE/空stdout和stderr；pid/pgid及活动成员对应、回收后空组、quit_http/rc0/预算均符合。library扫描记录为空，真实HOME/.octosense mtime前后相等；没有把有限扫描解释为机器全量副作用审计。
5. **16张PNG（含part）、6种内容SHA**，全部物理尺寸2800×1696。六种不同内容全部目视，其余按相同SHA映射；8个请求capture路径、exists和摘要逐项吻合。全部是登录页。请求1280×800参数不代完整业务尺寸/缩放/三角色UI验收。
6. 八份完整host.log逐字读取；host_log_bytes/tail/markers重新计算吻合；769874 B业务view不与809 B宿主系统视图混淆；无[E]/panic/未打开应用/未知test-action。tick_exception_count=0。未执行登录或业务命令。
7. **1454项 files_written_in_run_dir**逐条核路径、存在、唯一有序及计数；每场清单未到400截断上限。它是驱动mtime文件列表，不是业务提交数，也非内核全量审计。primary、actions、events、旧recover逐字核对；唯一相关持久变化是新坏源副本、旧锁回收、state/宿主运行数据。
8. 八份完整sandbox-denials按harness正则独立重算：osascript执行拒89、443外联拒27、dtracehelper写拒16、两种系统Metal缓存写拒37/34，与result精确相同。**拒绝尝试存在，未发现成功越界证据**；计数是日志匹配，不是模型请求数量；未放宽profile。
9. 全部needs_model=false，**model_proxy/model_proxy_stats字段均不存在**，没有模型endpoint/MM_KEY环境。不是“代理运行且返回0”；本轮实际MiniMax调用0，真实模型建议NOT_RUN，无余额/402错误证据，NEEDS_ABRAM=no。
10. 作者build_r12/keys仍空，working.key/anchor.key删除证据保留；审查复用运输，新私钥0，未新签名。第1段独立catalog签名验算和作者install_staged只作为相应运输证据，不代本轮业务成功。原H证据全部只读。

请求SHA=`2c2695ea6a459589c3643f3716e3f008a8eba6465876bfa50fa4098deb73b046`；summary SHA=`ea5cb776f35785ef3b500d6ea1cb902df941d6fa5dd69337013b5c6dcf6a3af3`；MANIFEST SHA=`4ee39bc990ca7379e3273f352aeabc2211339c7dc4d5940a0978770ed7c32c9e`。完整结果见A。

## 缺陷闭合与建议挂账

### A-M4-R13-01 — P2 / 建议，PARTIAL：双故障仍丢任务恢复说明

- **文件/行**：冻结main:15187–15192，任务告警读取通用STATE.status；main:2535历史非法写STATE.status；main:2730–2756任务坏盘写pending/独立why/备份说明；main:2510独立历史notice。
- **触发**：独立review_tasks_and_history_notice，同时seed第二任务updatedAtMs=true与非法actions行；launch-hub/capture。全程无认证/业务写，未修改运行状态。
- **实际 / 预期**：pending=true，tasks_recovery_why精确第2条，主盘/两类副本全保；但STATE.status最终是actions非法诊断，登录图重复展示历史错误，无任务原因/recover路径。预期同一既有反馈出口展示两类准确诊断及核实的备份事实，不遗漏任务恢复未决。
- **根因**：接线把“非空STATE.status”当任务诊断；任务load之后历史load覆写这个通用字段，fallback只在空时触发，所以不会使用仍存在的tasks_recovery_why。
- **影响 / 严重性**：用户修复历史后可能才发现另有任务盘未决；本轮未发现数据丢失、越权或放行业务写，按完成优先裁决仅P2建议，**不因它判FAIL**。单故障三场接线子项已独立PASS，整体编号不能写CLOSED。
- **证据**：H/review_tasks_and_history_notice/frames/review_tasks_and_history_notice.png、state.json、tasks.json/recover、actions.jsonl/bad_lines、A；单故障三场对照。
- **具体改法**：只改既有反馈消费逻辑：pending时优先根据已有tasks_recovery_why生成任务原因，沿用现有恢复/备份核实事实；不能无条件信任泛用status属于任务告警。可复用m7_tasks_banner_text的独立原因分支；需要备份细节时仅消费/复核现有文件事实，不新增字段、页面、控件或入口，不改保源算法，不把文件存在说成已核实成功。
- **验证**：同一候选重新跑双故障，截图必须同时有任务原因/recover和历史冻结说明，盘面原文/副本全等；单坏盘、旧recover、合法盘及坏历史对照保持。本项挂账，不是本轮必修清单。

### D-M4-03 — BLOCKED-HOST，保源守卫保持，不计P1

- **文件/行**：main:6292获取/:6363释放/:6400盘冲突/:6459命令/:6719提交；宿主边界见HARDFIX_PLAN:22–28。
- **触发 / 实际 / 预期**：旧两上下文在复核到写盘间交错，普通文件token/版本重读不能确保唯一提交；预期原子替换与持有期锁。旧反例来源保持，本轮不伪称原生双进程协议已重跑或关闭。
- **根因 / 影响**：固定宿主缺少所需原语，依Abram裁决单独挂账，不作为FAIL。相同源码守卫保持，未知/未来锁与坏盘/坏历史/伪保存身份冷安全子项本轮已PASS，提交点失锁/故障仍无控制证据。
- **要求 / 验证**：保留安全拒写与保源，不清盘造成功；本轮不要求构建方改宿主、加服务或新功能。真正业务并发及写点失败属于下面的验证覆盖缺口。

### B-M4-01 — CLOSED加载/分类/保源子项保持；认证恢复NOT_RUN

main:2661成员/:2699解析/:2730保源/:2768恢复。合法Unicode/转义/非空盘不误拒；新bool时间/尾随/截断整盘拒收，旧备份和本次原文全保，独立PASS。根因修复与函数均保持。未执行可信主体显式恢复、恢复中故障/重试，不把这些签PASS，不新增必修源码改法。

### D-M4-04 — SOURCE-CLOSED限定epoch反例保持；真实撤销NOT_RUN

字段编辑:8254、原文:8391、改约:10310、改派:12704及原绑定失效守卫保持；确认:8779共享差异仅把来源对象判断改为既有helper，原文/actor/epoch校验仍在。旧累计字段复活确认的源码反例保持关闭；实际旧技工拒、旧确认/AI撤销、迟到回复/新绑定均未执行。无本轮必修改法，不将SOURCE-CLOSED提升为业务PASS。

### A-M4-R12-01 — CLOSED历史表述保持

r11实施已按真实证据更正B2为needs_verify、C-preempt为threads；未改历史证据或以Python替代模型证明原生原子性。旧A-M4-01/02/03及A-M4-R10-01继续保留原出处，不扩大成P1。

## 白名单覆盖阻塞与解阻条件

**B-M4-TEST-R13-01 — BLOCKED验证控制能力，非已证业务P1。** 本次8场全部实际运行，无ABORT；只对下列确实无法由当前控制表达的必需项记BLOCKED，不把普通未跑步骤泛称环境阻塞。

- **证据/根因**：request.schema.json:52–60及scenario属性没有共享双宿主/业务同步屏障、提交点暂停/失败注入、受控AI回包交错；harness:580–595每场复制到新的Store，:868–871逐场单宿主串行。两场相同seed复制不是同Store真竞争或连续重开。ui_actions桥接依赖osascript/System Events，本次用户明确禁止，故本轮未使用。
- **实际/预期/影响**：没有任何同步接单/重叠确认或写点故障控制执行；期望硬3/T04/T11及失败恢复/T35能在可信原生上下文中交错并核权威结果。该机制缺口阻断必需验证，不能根据冷回归签整个M4通过。
- **解阻**：驱动在现有授权内提供并实证可用的内置可信输入/登录通道，以及同Store双上下文同步、提交点失败/丢响应和受控AI交错机制；冻结相同候选与宿主，交回完整实际命令、回执/任务/预约/事件和截图。不得伪SESSION、手造成功回执、预装有效预约、手改task状态或在当前schema偷偷加入不支持字段。
- **普通未运行**：本请求只有launch/capture，没有可信登录或业务命令，真实主链、权限/服务关系/时区/预约过期/三角色仍NOT_RUN。旧资料记type/key不支持，但本轮未对rc.6作输入探针，**不声称已证明它缺少所有内置输入能力**。M3整体无PASS另行记录，不由M4代修。
- **授权边界**：没有余额不足或公开发布需求；身份/provider/离线签名/本地安装已裁决。剩余属于技术控制与证据交付，NEEDS_ABRAM=no。agent内rc71/rc3不是本报告BLOCKED依据。

## 19项既有用例逐条结果

|用例|本轮精确状态与范围|
|---|---|
|T04|BLOCKED同Store双上下文同步接单；无真实唯一成功/事件，D03不计P1|
|T05|NOT_RUN可信技能/项目/经理分配及主体事件|
|T06|NOT_RUN实际改派旧预约取消/新负责人/旧技工拒；撤销源码保持|
|T07|NOT_RUN真实编码/载荷、伪造/跨项目/归档拒|
|T08|NOT_RUN合法服务空间绑定及仅同安装位置反例|
|T09|NOT_RUN无设备拒开工、处理中换设备、经理更正理由|
|T10|NOT_RUN提议不直升、合规主体确认与错误主体拒|
|T11|BLOCKED同Store重叠同步确认；跨项目冲突/相邻普通动态NOT_RUN|
|T12|NOT_RUN待改约保旧确认、新确认替代、拒新保旧|
|T13|NOT_RUN预约过期/无timer/客户端伪时间；stale锁PASS不代预约过期|
|T14|NOT_RUN真实上海日期输入/UTC毫秒、模糊时间、end<=start|
|T15|NOT_RUN真实旧version拒、刷新/阶段限制；合法冷盘PASS仅子项|
|T31|NOT_RUN取消释放预约/保事件、终态只读与关联任务|
|T35|NOT_RUN真实旧授权/确认/AI撤销及新绑定；旧epoch SOURCE-CLOSED；受控交错BLOCKED|
|U01|NOT_RUN三可信角色首屏；PASS仅未认证登录根|
|U03|NOT_RUN同任务跨角色事实/动作和承接者不能自验；伪保存无认证PASS仅冷子项|
|U04|NOT_RUN有效预约/待改约/冲突/过期错误出口|
|U05|NOT_RUN安装位置/服务空间/来源选择依据真实UI|
|U07|NOT_RUN重复点击/丢响应/版本冲突/离线输入与同Store重开；冷保源PASS仅子项，双告警P2挂账|

没有新增完整T/U/P0/G0通过项，**docs/build-loop/ACCEPTANCE.json不改**。前序共享输入/来源/具名槽位差异已定位，零解析冷回归通过，认证工作台及M3建单仍未跑，故不签M3或其他模块整体PASS。

## 判定与门禁

- **最终结论：BLOCKED**；不是“带条件PASS”。已运行的冷权威/隔离检查均有真实证据，单故障反馈通过；建议P2不导致FAIL。核心链NOT_RUN和必需真并发/注入/交错控制BLOCKED使整体不能放行。
- **必修业务P1：0**。D-M4-03单独BLOCKED-HOST挂账；A-M4-R13-01仅P2 PARTIAL，保留建议，构建方不扩展功能，不反复修已挂账户主原子缺口。
- **留在本模块的解阻指令**：交付上述既有流程的可信输入/登录及同步/写点/回包控制证据；从M3实际创建工单沿UI到开工，保留权限/服务关系/时间/改派改约旧绑定反例。不得手改运行数据跳预约。M3整体前置继续挂账，不代修。
- **门禁**：仅更新GATES M4的status和review字段，review_candidate_id=M4-r12-worktree、review_report指本报告；写前完整GATES保存E/gates-before-review-r14.json，旧review字段追加review_history，并链接实际上一轮r13报告，避免作者残留r12字段覆盖历史。candidate/base/实施报告及其他作者字段、所有其他模块不改。
- **版本保护**：第2段开始及证据审计时197项快照均一致；写门禁前再次核对发现**仅共享app/bundle/main.splash变为769696 B / SHA256 2b532105383be89a9d9f568f01c39ef78f0c080c19fbb1f2ad910364087118fb**。冻结源、候选/seed/mirror/宿主/harness/profile及原GATES不变，漂移记E/post-audit-worktree-drift.json。没有撤销或覆盖并行改动，也未改审新源；结论仅适用于07ecd2fd/a6a5c305候选，不能沿用到2b532105新工作树。
- **审查过程偏差**：第1段误读项目外memory索引已在阶段笔记与用户输出披露，未用于候选/结论；第2段全部读写在项目内。CLEAN不抹掉该第1段偏差。没有读取真实明文凭据/provider密钥或真实账号哈希，无项目外写入、消息/push/issue/评论/部署/发布。
- **是否允许下一模块：否**。本报告不提供或执行下一模块入口。

STATUS=BLOCKED
NEEDS_ABRAM=no
