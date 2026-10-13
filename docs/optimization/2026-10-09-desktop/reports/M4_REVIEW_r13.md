# M4 独立 Review r13

**最终结论：BLOCKED。受审候选：M4-r11-worktree。** 八场独立原生冷加载/失败夹具均 CLEAN，零业务解析/运行错误；合法任务加载、严格数值拒收、坏盘保源、三种旧锁 boot 和伪保存会话无认证均 PASS 对应子项。本轮没有新增业务 P1，D-M4-03 按 Abram 裁决单独 **BLOCKED-HOST**，不计 P1、不作为 FAIL 理由。

真实 M3 建单→接单→设备→预约→开工、三角色与业务命令仍 NOT_RUN；当前白名单没有同 Store 双原生上下文同步、提交点故障或受控 AI 交错入口，剩余必需验证有明确覆盖阻塞，不能凭八场 CLEAN 放行。不执行下一模块。

置信度：候选/资源绑定、冷加载与保源、日志和隔离记录 **高**；可信登录后的业务/预约/权限/模型效果 **未知（未运行）**。

## 审查对象与边界

- 审查者/日期：本主会话唯一审查者，2026-10-13，Asia/Shanghai；两段式 `review_r1_1659`，无子代理、不修业务/宿主/harness。无法用现有工具确认或切换 Router/gpt-6.1-sol，亦无本线程 createdAt/标题读写接口；未声称完成切换或改名。
- candidate_id/base：**M4-r11-worktree / M4-r10-worktree**；用户交接、`M4_IMPLEMENTATION_r11.md`、`M4/r11/CANDIDATE.json`、构建请求/证据与 GATES 作者字段联合定位，不按 mtime 选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty；受审 main **765252 B / SHA256 ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e**。
- 运输 digest：`ddd0eb06ef6afda8cc36174c64e0c5519e84ac695854b94f6f502cf62d45ed6f`；离线 anchor：`8d7c22db627105c78cf604aabcccdaede817263f0078a4ac90ec669406016ac7`。复用已授权本地 catalog/install_staged 运输，不发布、不新签名；运输 manifest 与工作树 manifest 不冒称逐字相同。
- 实际宿主 rc.6：`host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`；harness `8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7`；profile 模板 `76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`。实际文件摘要与驱动记录全等。
- 前置：**M3=BLOCKED / M3-r10-worktree / M3_REVIEW_r14.md**。D-M3-02 冷恢复已闭合，但没有整体 PASS 或已接受候选；用户挂账允许局部复核，不等于满足前置。不修、不改判 M3。
- 已读范围：第1段 AGENTS/CONTEXT、00/01/02/M4/04、r11实施/清单、r12缺陷、M3 r14、HARDFIX_PLAN边界、缺陷函数与旧冻结源、harness/schema/profile和相关T/U。第2段核全部8场 result/summary/profile/probes/denials/log/frames/权威盘/资源/MANIFEST。仅旧缺陷及直接差异回归，没有无关扩审。
- 驱动执行：**20:10:21–20:12:51 +08:00**，1 batch、8/8 CLEAN，quit_http/host rc0，各场17.25–17.32秒，无 ABORT。审查者未启动宿主或执行 sandbox-exec/pgrep 预检。
- 实际审计命令：`PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/optimization/2026-10-09/M4/native/review_r1_1659/audit_phase2.py`，rc0，**9360项证据一致性/权威盘检查，0不匹配**；这不是9360个业务用例PASS。
- 全部读写在项目内，未读取真实明文凭据/账号哈希或provider密钥、项目外记忆/配置。测试账号为隔离新造 salted PBKDF2；没有用伪SESSION绕登录。真实MiniMax调用0、未出现余额错误；无消息、公网部署、push、issue/评论、公开签名或上架。

路径约定：**H/**=`runtime/optimization/2026-10-09/M4/native-runs/review_r1_1659_REQUEST_review_r1_1659/`；**E/**=`runtime/optimization/2026-10-09/M4/native/review_r1_1659/`；**A**=E/native-evidence-audit-r13.json。请求为 `M4/native/REQUEST_review_r1_1659.json`，SHA256 **014b62a7d1fe5253ea6ed5338b4d806532a8423c0aa660f1ec5f8cb531520b43**；阶段笔记为同级 `REVIEW_NOTES_r1_1659.md`。源码行号均指 E/source.main.splash。

### 快照与共享工作树漂移

第1段后共享 `app/bundle/main.splash` 已为 SHA256 **c3e0477b26a2f20dcf7da4f73c27ac596d7b58800d88bcadbbdb12d186f457b0**；第2段仍是该已知漂移。审查没有修改或撤销它，也未改选候选。**原候选清单、冻结源、171项seed/mirror资源、manifest/config、harness/宿主及原GATES/ACCEPTANCE到写门禁前保持快照一致**，仅共享main与初始值不同。八场实际running资源均为受审 ae25feb4 源；本结论不适用于 c3e0477b 新工作树。

## 必需检查与独立结果

|检查|独立步骤/期望|实际|结论/证据|
|---|---|---|---|
|候选/宿主/证据绑定|重算请求、seed、mirror/installed/running与宿主|唯一running包，每场全资源吻合；765252 B业务eval/view=true|PASS，A/H|
|冷启动解析与真实根|零解析/运行错误、UI可见|8场无[E]/panic/未知动作、tick异常0，完整登录页|PASS冷根；认证工作台NOT_RUN|
|合法盘与严格数值|中文/引号/换行/路径/emoji合法数字可载；第二成员bool-version拒|合法395 B任务盘不动，pending=false；765 B混合盘整盘拒、准确第2条原因|PASS B01直接回归|
|坏盘保源|截断主源/旧recover不覆盖，本次坏源另存核实|372 B主及395 B旧recover不动，corrupt.latest=本次372 B坏源|PASS保源子项；显式恢复命令NOT_RUN|
|旧锁boot|future/unknown保留、stale回收、保存token不得复活|锁逐字符合预期；所有进程token空|PASS启动子项，不代活持有者并发安全|
|坏历史/伪保存身份|非法记录保源冻结；state中的主体不认证、不写任务|坏action原文与.bad_lines全等，图有冻结出口；伪actor/session均null，业务盘无写|PASS冷安全子项；登录后命令拒写NOT_RUN|
|硬1：权限与设备关系|可信主体技能/项目/伪设备拒，合法服务绑定|无真实绑定/分配命令|NOT_RUN|
|硬2：预约规则|提议/主体确认/过期/时区/跨项目/改约拒绝|无实际预约命令|NOT_RUN；锁到期不代预约到期|
|硬3：真正业务并发|同Store双原生上下文接单/重叠确认唯一成功；相邻正常|无共享双上下文+同步入口，实际命令未执行|BLOCKED控制覆盖；D03独立BLOCKED-HOST，不计P1；相邻/跨项目NOT_RUN|
|硬4：开工与旧授权|设备/有效预约不足拒开工，改派旧技工拒|无改派/开工命令|NOT_RUN|
|硬5：三角色与事实回执|真实输入、首屏/阶段/负责人/预约/回执一致|全部登录页，成功动作0；无预约或开工|NOT_RUN|
|旧确认/AI撤销|改派改约撤销、新编辑绑定、迟到拒|六相关源码段不变；无实际交错|SOURCE-CLOSED仅旧epoch反例；动态NOT_RUN，交错控制BLOCKED|
|隔离与回收|profile/probes、预后进程、组回收、成功外写记录|8/8指定字段合格，无ABORT|PASS证据记录范围|

### 八场权威结果

|场景|实际事实与精确PASS范围|
|---|---|
|review_cold_absent|无tasks/lock/recover新建；actions/events仍空数组；pending=false、零错误。PASS无任务冷根，不是M3创建|
|review_valid_future|395 B合法任务原样，pending=false；33 B future foreign token原样、进程token空。PASS加载/保锁；lock_state实际为空，不编造owned|
|review_valid_unknown|395 B合法任务不动；32 B未知锁原样，unknown_kept、token空。PASS加载/未知锁保留|
|review_valid_stale|395 B任务不动，pending=false；stamp=1旧锁清为0 B，released、token空。PASS旧锁boot回收|
|review_bool_version_second|765 B混合盘原样，pending=true；原因指第2条必需字段/类型/状态非法；recover=原坏源。PASS整盘拒与保源|
|review_truncated_keep_backup|372 B截断源、395 B既有合法recover全等保持；corrupt.latest逐字=截断源，pending=true，原因指首尾。PASS截断/旧备份保全|
|review_bad_history_no_write|51 B非法action原样保留，.bad_lines逐字相等，state写准确第1条原因/冻结；图显示修复文件后重启提示。PASS冷历史拒收/可见错误；未实际提交命令|
|review_forged_view_no_session|伪保存actor/session最终均null、token空，任务与空历史无写，仍登录页。PASS保存内容不能建立认证，不是实际撤权/越权命令测试|

## 完整证据核对与边界

1. **1743条 MANIFEST**逐项重算摘要、路径归属、无重复/无symlink及精确文件集合，全部匹配。summary.request与独立请求全等；场景集合/batch顺序及summary投影字段逐项匹配result。
2. 第1段171项seed/mirror摘要保持；八场seed列表及摘要与独立准备内容全等，无重复，catalog真实预装。每场14资源在mirror/installed/唯一.running三份，共**336次资源比较**全等。digest_seen_in_seed=true，digest_seen_in_host_log=false如实记录；实际运行资源/eval构成加载证据，不靠digest marker单项。
3. 八个profile按模板、ROOT/真实HOME占位、实际run路径/control port逐字重构，文本/摘要全等；apply rc0、外写probe拒且created=false、五类禁读probe合格、osascript执行probe被拒。12项HOME/app-data/cache/config/data/tmp等路径均在新场景目录。只读记录，不再次访问禁读目标或探测真实HOME。
4. pre/post严格为rc1/NONE、无stderr；pid/pgid与活动组匹配，回收后成员全空、host rc0/quit_http，运行窗口合规。library扫描为空，驱动记录真实HOME/.octosense mtime不变；没有把这些有限观察当机器全量审计。本次没有额外同PGID成员。
5. 含part共**16张PNG、4种SHA内容**，物理尺寸均2800×1696；逐种全部目视，其余通过相同SHA映射。8个请求capture与result/MANIFEST全等。所有图为未认证登录页，坏历史场有冻结/修复说明；任务坏盘两场没有同屏任务恢复原因，见建议。没有业务脚本解析空白；认证后的工作台/三角色未运行。1280×800是请求参数，不签完整业务自适应PASS。
6. 全量读取八份host.log，bytes/tail/markers重算匹配；每场业务eval=765252 B/view=true，809 B系统视图不混作业务；无[E]/panic/app_not_opened/未知动作。内置launch/capture完整执行，等待依据harness墙钟。
7. **1452项 files_written_in_run_dir**记录逐项核唯一、有序、实际文件存在且路径归run内，各场181–182，未触及400截断上限。它是mtime文件清单，不是业务动作数或内核完整副作用日志。任务/预约/历史没有成功业务提交，只有预期坏源备份、锁回收与运行缓存/state写入。
8. 完整读取八份sandbox-denials，依harness正则独立重算与result全等：osascript执行拒89、443外联拒32、/dev/dtracehelper写拒16、两类Metal系统缓存写拒39/32。**被拒尝试存在，不等于成功越界**；计数是日志匹配数，不代模型请求计数。profile未放宽，没有已证成功违反隔离的行为。
9. 八场needs_model=false，result均**不存在model_proxy/model_proxy_stats字段**，env无真实key/模型endpoint；不是代理已运行并返回requests=0。本轮真实模型0调用，真实建议NOT_RUN；无billing_error/402证据，NEEDS_ABRAM=no。
10. 作者build_r11删除记录保留，keys目录仍空、两key路径不存在。审查复用签名store，新私钥0；不publish/listing，不触及外部安装。原始H证据只读、不覆盖。

summary SHA256 `5d090d26cec72f26b084fb0c3245905d3b9eb041d4dbf8dc06e957ccac5e2e8f`；MANIFEST SHA256 `a568fc31ce5f1617eb9cd7cc70ce15837ac39b0960629f94bc22de134f6a3ed0`。完整机读审计见A；统计只支持上述精确范围。

## 上轮缺陷闭合与挂账

### D-M4-03 — BLOCKED-HOST，保留守卫，不计P1

- **文件/行**：冻结 `main.splash:6288`获取、`:6359`释放、`:6396`盘冲突、`:6455`边界、`:6715`提交；宿主能力边界见HARDFIX_PLAN:22–28。
- **旧触发/实际/预期**：两个上下文在检查到主写之间交错，普通锁文件读写与整盘写无法保证唯一成功/不丢更新；期望原子替换与持有期锁。该旧协议反例来源保留，本轮没有伪称重新执行原生双成功。
- **根因/影响**：固定宿主无所需原语，脚本中的token/版本/冲突重读不能替代原子性。**依Abram裁决单独挂账，不是本轮P1/FAIL理由，不宣称闭合。**
- **本轮进展/证据**：上述获取/释放/冲突/提交函数与r12冻结全等；runCommandBound新增恢复屏障在授权后/获取锁前。E/source-regression.json、affected-functions.diff及16项独立源码检查；H三锁与合法/坏盘/历史/伪身份冷回归均PASS限定子项。
- **保留要求/验证**：继续保持未知锁/坏盘/未决恢复/无身份安全拒写并保源，不删除守卫或用清盘制造成功。本轮不要求构建方改宿主、加服务或再修被裁决挂账的原子缺口。提交点失锁/读失败/中断与真正并发尚无原生控制验证，见覆盖缺口，不以作者41/41模式核验代动态。

### B-M4-01 — CLOSED加载/分类/保源子项保持；可信恢复NOT_RUN

- **文件/行**：`:2657`成员校验、`:2695`解析、`:2726`保源、`:2764`恢复身份校验、`:2843`boot。
- **旧触发/实际/预期**：合法闭合盘曾被码点/字符串类型不匹配误拒；期望合法数字盘加载，非法类型整盘拒并保护来源。本轮三个锁组合及其它合法395 B盘均pending=false，bool第二成员准确拒，截断主盘和既有recover保全。
- **根因与落实**：同型首尾门禁保持；共享修复将version/createdAtMs/updatedAtMs改strict-number。H/A独立回归证实合法值未误拒，坏值未采纳。旧闭合子项不重列必修。
- **影响/后续验证**：没有任务来源丢失证据，置信度高。登录后的显式恢复、恢复中失败/重试及操作后权威回读NOT_RUN；保持现有权限/备份门禁，验证既有恢复流程，不新增入口。

### D-M4-04 — SOURCE-CLOSED限定epoch反例保持；动态NOT_RUN

`:6073`失效、`:8250`字段编辑、`:8387`原文编辑、`:8775`确认、`:10306`改约、`:12700`改派六段与r12逐字一致。旧累计编辑集复活确认的源码反例继续关闭，epoch清空、旧AI绑定撤销守卫保留。实际改派旧技工拒、改约旧确认/AI撤销、新编辑绑定和迟到回复没有执行；SOURCE-CLOSED不代业务PASS。无本轮相关必修源码改法，保留修复并在既有动作中补动态验证。

### A-M4-R12-01 — 建议文案CLOSED

r11实施报告已准确更正B2迟到提交为版本变化导致needs_verify、C-preempt为同进程threads而C2才是Python多进程。历史证据不改，没有因此宣称原生原子能力完成。

### A-M4-R13-01 — P2 / 建议：任务坏盘说明未到登录反馈

- **文件/行**：冻结 `main.splash:2745–2752`将恢复原因写STATE.status；`:15143`登录反馈消费M2_RECOVERY_NOTICE，未包含该任务坏盘说明。
- **触发/实际/预期**：独立第二成员bool-version或截断盘冷开。state有准确恢复未决/备份路径，两个登录图仅“请输入账号和口令”；坏历史图则能显示冻结及修复说明。期望既有反馈出口显示该任务盘原因与保源信息。
- **根因/影响/证据**：任务恢复diagnostic与当前登录反馈未接通；H两个坏盘state/frames及坏历史对照。未证来源丢失或因此阻断合法核心写，按完成优先裁决仅建议，不据此FAIL；认证后的恢复出口仍NOT_RUN。
- **具体建议/验证**：仅将已有任务恢复说明接到已有反馈出口，不加页面/控件/字段；同两场核同屏原因/路径与副本摘要，保持合法盘/坏历史不回归。审查方不修改代码。

旧A-M4-01/02/03及A-M4-R10-01历史来源保留，不扩大为本轮P1。作者host_runs/deferred_gaps/test_counts中的旧rc71/rc3/provider延期/旧轮次数保留为历史自述，不作为本轮阻塞依据。

## 白名单覆盖阻塞与解阻条件

**B-M4-TEST-R13-01 — 必需验证覆盖缺口，非已证业务P1。** 本轮没有ABORT，普通冷开已真实运行；只有下述机制无法覆盖的项标BLOCKED。

- **文件/行与根因**：`driver/harness/request.schema.json:52–60`为内置动作列表；场景属性没有共享双宿主/提交点暂停或失败注入/受控模型回包到达控制。`native_harness.py:580–596`逐场复制到新run Store、`:868–871`每次仅run一个scenario；不是两个可信原生上下文共享一事实盘。`:39、242`及ui_actions实现依赖osascript/System Events，而本次最高优先用户约束禁止该桥接。
- **实际/预期/影响**：八场只有launch/capture，未登录、无业务命令或预约。期望硬3/T04/T11真实并发、提交点失败恢复与T35交错能被独立控制且回读一致。它们不在当前白名单可执行机制覆盖内，标BLOCKED；普通尚未执行的主链/权限/时区/三角色仍NOT_RUN，不推定业务失败。
- **输入能力精确边界**：旧schema/报告标type/key未实现，但本轮未对rc.6执行输入探针，**不声称已独立证明rc.6缺少所有点击/输入能力**。禁止桥接不等于整个harness不能运行，更不把agent沙箱rc71/rc3列阻塞。
- **解阻所需条件**：驱动在当前授权范围内实证有效的宿主内置真实输入/可信登录通道，并为现有命令提供同Store双原生上下文同步、提交点故障及AI交错控制。随后独立从M3实际创建工单，沿既有UI完成接单/设备/预约/开工，交回同候选的frames、完整log、权威任务/预约/回执/事件和失败恢复证据。不得伪造SESSION、预装有效预约/修改运行状态跳链，不新增业务功能/入口/字段，不公开发布。需闭合M3原生建单验收前置，本模块不代修M3。

身份/provider/离线签名/本地安装已裁决，没有余额或公开发布需求；剩余是技术验证机制和未执行证据，**NEEDS_ABRAM=no**。

## 19项既有用例逐条结果

|用例|本轮精确状态/范围|
|---|---|
|T04|BLOCKED：同Store双原生上下文同步接单入口缺；没有原生唯一接单者/成功事件实测，D03只BLOCKED-HOST|
|T05|NOT_RUN：可信技能/项目拒绝、经理分配及事件主体|
|T06|NOT_RUN：真实改派旧预约取消/新负责人/ACCEPTED/旧技工拒；撤销源码保持|
|T07|NOT_RUN：设备编码与asset载荷、伪造/跨项目/归档实际拒绝|
|T08|NOT_RUN：合法服务房间绑定与仅同安装位置反例|
|T09|NOT_RUN：无设备开工拒、处理中技工换设备拒、经理更正旧新值/理由|
|T10|NOT_RUN：提议不直升SCHEDULED、非报修人确认拒、合规确认|
|T11|BLOCKED：同Store同步重叠确认；跨项目冲突/相邻实际NOT_RUN；D03不计P1|
|T12|NOT_RUN：待改约保旧确认、新确认SUPERSEDE、拒新保旧；撤销源码保持|
|T13|NOT_RUN：提议到期/无timer/伪客户端时间；stale锁boot PASS不是预约到期|
|T14|NOT_RUN：上海真实日期输入/UTC毫秒/模糊时间核对/end<=start拒|
|T15|NOT_RUN：真实旧version拒/刷新不覆盖/阶段限制；合法盘冷加载PASS仅子项|
|T31|NOT_RUN：取消释放预约/保事件、终态只读、再故障关联任务|
|T35|NOT_RUN：实际改派改约/旧确认旧AI撤销/新绑定；SOURCE-CLOSED限旧epoch，受控交错覆盖BLOCKED|
|U01|NOT_RUN：三可信角色待处理首屏；PASS仅完整未认证登录页|
|U03|NOT_RUN：同任务跨角色事实/动作、承接者不能自验；伪保存无认证PASS仅冷安全子项|
|U04|NOT_RUN：有效预约/待改约与冲突/过期错误出口|
|U05|NOT_RUN：安装位置/服务空间/来源选择依据实际UI|
|U07|NOT_RUN：重复点击/响应丢失/版本冲突/离线输入与同Store重开；坏盘保全PASS仅冷子项，M3 r14结论不改|

没有新增完整T/U/P0/G0用例PASS可登记，**原ACCEPTANCE.json不改**。历史后端/作者/旧宿主通过记录不解释为本轮原生通过；相关共享读取的冷回归已做，不签前序模块整体PASS。

## 判定与门禁

- **最终结论：BLOCKED。** 已运行8个冷启动/失败子项均PASS，隔离回收8/8 CLEAN，新增业务P1=0；D03按裁决BLOCKED-HOST挂账，旧epoch SOURCE-CLOSED保持。真实核心流程没有独立证据、特定白名单控制无法覆盖剩余必需项，不能满足“核心功能真实成立且无P1”的PASS条件。建议项不构成FAIL理由。
- 不要求Kimi扩展功能或继续修已挂账宿主原子能力；留在本模块补上述现有流程/验证机制/证据，保持已通过守卫与冷回归。M3前置仍BLOCKED，不由本模块修复。
- `GATES.json`仅更新M4 status及review字段，review_candidate_id=M4-r11-worktree、review_report指本报告；完整前态归档 E/gates-before-review-r13.json，旧review字段追加review_history。作者交接字段和其他模块不变；原ACCEPTANCE/业务源码不改。
- 不允许进入下一模块，不提供或执行下一模块入口。

STATUS=BLOCKED
NEEDS_ABRAM=no
