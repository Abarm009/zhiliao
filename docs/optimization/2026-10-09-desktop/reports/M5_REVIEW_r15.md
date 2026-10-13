# M5 独立 Review r15

**最终结论：FAIL。八场独立原生运行均 CLEAN，但四场索引写后核验返回失败，两场真实附件重建耗尽脚本指令预算、业务窗口空白。D-M5-04.B/C 未闭合，核心附件恢复能力不成立。不是 ABORT 或 agent 沙箱限制，不允许进入下一模块。**

- 审查者 / 日期：Codex 主会话唯一独立审查者，2026-10-14，Asia/Shanghai。无子代理，无业务/宿主/驱动代码修改。
- 候选 / base：**M5-r11-worktree / M5-r10-worktree**；按 M5_IMPLEMENTATION_r12、r11/CANDIDATE、GATES及本次请求定位，不按最新文件时间选版。r12 未改业务代码、沿用冻结件。HEAD 来源 `8d730569546cb57310944bb299695134df773b9d` 加共享未提交差异，不等于 HEAD 的纯提交内容。
- 冻结源 **771176 B / SHA-256 05c9ea2484eb3c2ee1dc5a97dde37e1f489501a42385dfd81b5803914dfe6365**；bundle digest **5bde47daba3ff19a98a9b0e079bbd9cd06eb16ae0d4b133dc45206395ab63544**，0.1.0-b。候选与实际 mirror/installed/.running 全资源同源；本次不审后来漂移工作树。
- 前置：**M4 BLOCKED / M4-r12-worktree / M4_REVIEW_r14.md**，没有已接受整体 PASS。按挂账裁决继续局部复核，不冒称前置满足。D-M2-05/D-M4-03 单列 BLOCKED-HOST，不列 P1、不据它们判 FAIL；本轮失败是 M5 自身附件运行/核验。
- 实际宿主 rc.6：`runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA **2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a**，本次重算与各 result 相同。harness SHA **8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7**，profile模板 SHA **76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f**，与第1段一致。
- 驱动运行时间：2026-10-13 **23:54:03–23:56:41 +08:00**；八场各18.26–18.30秒、quit_http退出、rc0、CLEAN，没有 ABORT。
- 作者报告：`reports/M5_IMPLEMENTATION_r12.md`；上轮独立 Review：`reports/M5_REVIEW_r14.md`。本轮只核原编号和直接影响回归，未扩审前序/下游。
- 阅读范围：第1段实际 AGENTS/CONTEXT、02/04/M5、实施/候选/r14、相关冻结源码与schema；本段全部独立 summary/result/profile/probes、日志、MANIFEST和盘面，实际目视全部5种不同摘要截图（其余3张同字节）。00/01及根基线通过既有 CONTEXT 浓缩承接，未声称重新全文通读。
- 实际主会话 Router路由/指定模型、createdAt与标题设置无可核验接口，未声称切换或命名成功。
- 所有场 needs_model=false，未启动 MiniMax代理，`model_proxy_stats`缺失不是“代理实测零请求”；实际模型请求 **0**，无余额/402错误。NEEDS_ABRAM=no。
- 快照：本段保护源/请求/harness/schema/台账准备前后摘要一致；未换入最新源码。GATES仅本模块 status和审查字段更新，历史快照保留；ACCEPTANCE.json及其他模块不动。
- 置信度：证据完整性、原生失败与冷保源观察 **高**；writer究竟主盘read抛出还是比较/返回语义异常 **未知**；真实认证主链、保存后双入口和同盘重启 **未知/未运行**。

短路径相对 `runtime/optimization/2026-10-09/`：**E/**=`M5/native/review_r2_1659/`；**H/**=`M5/native-runs/review_r2_1659_REQUEST_review_r2_1659/`；**R**=`M5/native/REQUEST_review_r2_1659.json`；**A**=E/native-evidence-audit-r15.json。下列源码行号均属于 E/source.main.splash 的冻结源。

## 必需检查

|检查|独立步骤 / 期望|实际|结果 / 证据|
|---|---|---|---|
|请求/候选/宿主/全证据|逐项核摘要、完整资源集合、实际命令与seed|1846条MANIFEST、380个seed记录、336个包资源比较均相符，八场确实加载相同候选|PASS，A；不是业务放行|
|隔离/回收|profile/probes、前后库存、环境目录、空进程组与CLEAN|八场满足全部条件，无外目录成功写入证据，库扫描空、真实HOME目录mtime未变化|PASS隔离/回收，A与各result|
|解析及实际渲染|零parser且实际业务窗能渲染|无parser错误；六场登录页可见，两场指令预算错误后窗口全空白|解析子项PASS；运行/渲染FAIL，D04-C，日志不能只查[E]|
|三成员轮次/两格式核验|legacy/v3轮37，整套核验成功、全成员保留|三件均修成37，旧孤儿6/外项8及其他全部字段保留；但两场save_return=false、后段unrun|字段修平/保留子项PASS；整体核验FAIL，D04-B|
|退回tmp恢复|截断主盘回退合法tmp，保留旧记录、三件退回标记，核验后清tmp|主盘重写完整v3、三标记正确、旧项保留；writer=false、tmp非空保留|保留/marker子项PASS；整体核验FAIL，D04-B|
|完整件与新件矩阵|新ASCII/中文完好READY；中损/缺件/无canonical不得信任|basename和六件矩阵在m5_xor8耗尽预算；索引未重建，probe/audit缺失，UI空白|FAIL执行能力，D04-C；具体坏件分类NOT_RUN，不写成“已拒绝”|
|外任务同id碰撞|不夺owner/round，旧孤儿/原字节保留|外项owner与round8保持，孤儿不删、全部附件字节不变；核验仍失败|归属/保留子项PASS；整体核验FAIL|
|坏任务保源|截断任务拒接部分事实、旧recover不覆盖、原文另存|pending=true，原tasks/recover/索引/附件保留，corrupt.latest逐字相等；登录页可见故障原因|PASS冷子项；可信修复操作NOT_RUN|
|真实保存后双入口反例|原生保存后损坏/缺失/跨任务，再submit/accept均拒|本请求无上传或业务命令，schema无运行期副本变更调度|NOT_RUN双入口；特定变更控制缺口BLOCKED|
|可信独立主体与经理理由|真实独立会话、承接者多角色禁自验、经理无理由拒|没有可信登录/业务命令，未以actor标签或预置completion代替|NOT_RUN，源码不代认证证据|
|正常/退回/同盘重启链|真实UI、字节、事实与回执一致，两条主链与重启打开|只有冷诊断，tasks/actions/events未变；fresh Store不能代连续重启|主链NOT_RUN；同Store重启/精确提交调度BLOCKED|

### result与MANIFEST逐项核对

1. summary.request与R全文相同；八场id/顺序/verdict相符。driver_not_sandboxed_check=rc0/空stderr；summary记录harness/template摘要与实物一致。
2. 每场profile.path/sha256与实物相同；按run目录、项目根、记录的HOME/control port重构profile后逐字全等。写入仅当前场目录和/dev/null；五类禁读、osascript禁执行、外联禁令保留；无model proxy规则。所有路径类env均落本场目录。没有重新执行probe或读取禁读目标。
3. profile_probes.apply.rc0，write_outside_denied.rc!=0且created=false，五项read_blacklist均ok=true/拒绝，osascript_exec_denied.rc71且ok=true，整体ok=true。此rc71是驱动证明禁止执行有效，**不是BLOCKED理由**。
4. 八场pre/post均rc1/空out/空err/class=NONE，pgid_members_after=[]、host_returncode=0、quit_http，耗时在max35+2内；library_scan_new_or_modified=[]，real HOME/.octosense mtime前后相同。
5. 每条cmd逐项核对：sandbox-exec参数、已固定宿主、1280x800、launch-hub和本场capture完全相符。审查方没有自行执行cmd、pgrep或sandbox-exec。
6. 8个captures存在、SHA全等；5种不同摘要全部实际目视：普通登录、空白、退回场登录、外来碰撞场登录、坏任务诊断登录。basename与matrix截图同字节；三成员两格式与cold同字节。seed内作品screenshots不是本批次captures。
7. **1462条files_written_in_run_dir记录**逐项核项目内场目录、实物存在、唯一性及count相等，无400条截断。该列表是按mtime收集的目录文件记录，包含宿主系统资源和预装文件，不能将其全部称业务新增写入。各文件字节由完整MANIFEST独立核对。
8. sandbox-denials.log原文全部核查，result.summary按harness正则重算相同：包含osascript执行、外联443、系统Metal缓存、/dev/dtracehelper的**拒绝**。八场按时间并行日志窗口可混入其他场/探针记录，不能将每条拒绝直接归属当前业务调用；拒绝不代表外联/外写成功，也不作为本轮BLOCKED。profile/probes与盘面未显示成功越界。
9. host_log_markers、bytes、tail全部从真实日志重算相同；app_not_opened=false、panic=false且已launch-hub。**该摘要不收集脚本指令超限**：两场host.log:49明确有`script instruction limit exceeded`，虽日志级别[I]、零[E]，业务eval view=false，不能因此写“零runtime错误”。另有缺property提示，未将与本次核心故障无关提示扩列P1。
10. 各场model_proxy/model_proxy_stats均不存在，needs_model=false、env无代理启动，由实际harness分支与命令核对未启动代理；没有余额错误、调用0次，不推导真实模型效果。
11. 1846条MANIFEST逐项重算，校验唯一性、项目内路径、无symlink及完整文件集合，0差异；380个seeded_files记录与冻结输入完整集合/摘要相符；mirror、installed和.running各14资源×8场×3副本共336个资源比较一致，包含真实源码，不仅查digest字符串出现。
12. 八场tasks/actions/events均与各自seed逐字相同：本批次没有执行用户完工/验收/退回、未生成相应用户业务回执。全部inbox/attachments/canonical原字节保持，缺stored和缺canonical未被偷偷补成可信基准；这证明冷保留，不证明成功主链。
13. 四场main/tmp全文同字节、解析后的items与state.attach_items完整对象相等。逐字段比较seed旧索引：legacy/v3仅本任务三件round0→37；reject仅三件last_rejected_at变化；foreign无owner/round夺用，孤儿/外项全保留。尽管盘面正确，writer=false、members=[]、audit.index_saved=false，未形成权威核验成功证据。
14. build_r11离线私钥删除证据沿用第1段实测：working.key/anchor.key不存在、keys为空；本段未生成新私钥、未签名/发布。原第1段误读项目外记忆索引的流程偏差已披露，本段仅项目内；native CLEAN不抹去该偏差。

实际审计命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r2_1659/audit_phase2_r15.py`，rc0；**5624条一致性断言、0差异**，不是5624项业务测试通过。R SHA **7b154a675bc051e8a89607c8ff9fe08820a5bbd47588af41bd303d7e48103175**；summary SHA **7f91a096b971a7e76690b0d40cb4ae41d1fc876a3af05011f06b1a893a63d1c3**；MANIFEST SHA **601e19dcccc4dc02d3548a8ec6759fe2efd884f0dbc6b40d55078ad0b82e474f**。

## 缺陷与上轮闭合

### D-M5-04.B — P1 / 必修 / OPEN：实际写盘后核验持续失败，成员核验未运行

- **文件行**：冻结`main.splash:11003` writer，主盘write/read最终守卫`:11038–11047`；`:11513–11518`读取返回值/进入成员链；`:11585`诊断文件。证据：H/{r2_legacy_three37,r2_v3_three37,r2_reject_tmp14,r2_foreign_collision}/home/.octosense/apps/octosense-repair/m5-test/{evidence_index.json,.tmp,m5_save_verify.json,m5_reconcile_audit.json}，A.scenarios.member_comparison。
- **触发**：用R中任一上述seed原生冷启；合法task已提交而派生轮次或退回标记落后，要求恢复、读回并全成员核验。两种格式三成员对照均实际复现。
- **实际/预期**：四场`save_return="false"`、read/parse/extract/rb_ok全unrun、members=[]；audit.index_saved=false/index_save_failed=true，state.status写落盘/读回失败。main/tmp却为同字节完整v3，items与内存完整相等，三个round37/退回标记正确，旧项保留。预期writer真实确认写后读回成功，随后完整长度/逐成员/字段核验实际执行，audit与state成功一致，整体成功才清tmp。
- **根因界定**：失败已定位在writer返回/最终主盘读回守卫这一段，逐成员比较`:11070`和`:11552`尚未到达，继续只改成员相等函数无效。根据主盘已实际写为本次新内容可排除“根本没有写入”；read抛出、运行期比较与bool返回哪一项异常，现诊断未分辨，**未知，不杜撰具体宿主类型根因**。
- **影响**：核心附件索引恢复不能以权威成功结束，重启/重试仍处于失败；源码存在和盘面相等不足以关闭原缺陷。不声称本轮已丢证据，也不把D-M4-03原子能力挂账当免责。
- **具体改法**：Kimi只在既有writer/既有测试诊断中分清最终read是否成功、返回长度/内容与body比较、实际返回结果；根据原生失败分支修对应调用/比较，**不扩字段/入口，不硬改saved=true，不跳过全文核对，不删除恢复tmp**。两侧确一致时正确返回成功，再让现有成员核验到达；失败路径继续保源和拒信。
- **验证**：同四种种子原生复跑，save_return/rb_ok真实true、members覆盖全部5/2项、全字段和旧证据不变、index_saved=true、tmp在核验后清空；另做真实提交/验收读取回归与同盘重启。只改计数或Python仿真不算闭合。

### D-M5-04.C — P1 / 必修 / OPEN：1KiB完整附件指纹计算耗尽预算，启动空白

- **文件行**：冻结`main.splash:10801–10817` m5_xor8、`:10819–10829` m5_fnv_mix_byte、`:10845–10872`完整文件fingerprint；重建调用`:11433`及内容签名再次计算`:10935`；启动调用`:3041`。H/r2_basename_intact/logs/host.log:49报脚本`:10814:25`，H/r2_new_file_matrix/logs/host.log:49报`:10816:20`；对应frames/*.png及view=false、缺probe/audit，A两场记录。
- **触发**：合法任务登记新1024B完整ASCII附件及canonical，缺索引项；basename场仅一完整件+旧孤儿，matrix另含中文/损坏/缺失等对照；冷启需要恢复。参考原字节SHA **a7a92ba1874723b6354928068a9c7b8b495174ecbe0742abffe231354fc3c36f**，与输入、运行存盘、canonical全等。
- **实际/预期**：两场真实日志`script instruction limit exceeded`，eval771176B view=false，实际窗口空白、m5_last_reconcile=null、fs_probe/save_verify/audit缺失，索引不完成重建。宿主仍响应/quit，CLEAN、rc0，**不是环境BLOCKED**。预期完整件恢复READY并正确渲染；所有坏/缺件安全拒信且UI留有出口。
- **根因**：每个码点两次mix，每次展开8轮xor，多层脚本调用在启动同步执行，实际耗尽manifest已准入的**20,000,000 instructions**（host.log:41能力行），定位在xor循环。固定短literal探针正确不能证明真实文件规模可用。原子文件替换能力与此问题无关。
- **影响**：1KiB真实附件即可阻断启动、读取和验收前证据校验，完整件及异常恢复核心不可用；坏件分类因执行中止仍未验证，不能说坏件已被正确拒绝。
- **具体改法**：仅修现有指纹计算/调用链：在固定宿主已证实可用的原语范围降低逐码点函数/循环成本，复用一次核验得到的内容签名避免同启动重复计算；必要时沿现有tick机制分帧完成既有完整校验，期间保持VERIFYING/拒信并允许UI渲染。**不得截取首尾替代全文、改成元数据READY、删canonical闸、改宿主或只抬预算掩盖；不增功能/页面/公开字段。**若算法变化，旧登记兼容须按既有迁移规则保留，不静默重认坏件为原件。
- **验证**：先同1024B完好件+canonical、basename与matrix原生复跑，零instruction-limit/parser诊断、UI可见、完整件READY、损坏CORRUPTED、缺stored MISSING、缺canonical CORRUPTED且不制造基准。中文“机房→厨房”同长变更的声明指纹都531f702a，必须由canonical完整内容比对拒绝；随后真实保存、重启、双入口拒绝回归。不能仅看literal 50ce396a或缩小测试文件放行。

|上轮编号|本轮闭合范围|
|---|---|
|B-M5-TEST-R14-01|**CLOSED**：本次八场均已启动、NONE/CLEAN/回收合格；原已有宿主库存阻塞未复现。|
|B-M5-01|**PARTIAL**：原两处表达式parser根因已关闭，本候选没有该parser错误；“业务区可渲染”未整体关闭，两场指令超限空白由原D04-C承接，避免重复P1。不得写本候选仍是旧parser错误。|
|D-M5-04.B|**OPEN/P1**：四场独立复现writer=false/成员核验未运行。|
|D-M5-04.C|**OPEN/P1**：短literal实际正确；新文件规模核验两场因预算失败，未证明新件正确分类。|
|D04-A、D01/02/03/05|历史限定关闭保留；本轮旧索引/foreign保留PASS子项，不扩大为保存后双入口、可信主链或basename字节核验通过。|

必修为**原D-M5-04的两个子项**，不另造无关功能建议；B01运行空白在C中处理。既有无关提示仅保留日志来源，不因此判FAIL。

## 硬验收与既有映射

|硬验收|结论与边界|
|---|---|
|1 真实选择/保存/重启打开|**FAIL相关冷恢复**（完整件触发超限空白）；真实UI保存/同Store重启打开NOT_RUN，特定重启调度BLOCKED。|
|2 六类异常双入口拒绝|**FAIL相关冷核验执行**（矩阵中止）；全部真实保存后双入口拒绝NOT_RUN，运行期副本修改调度BLOCKED。|
|3 待验/可信独立验收/禁自验|**NOT_RUN**：未认证、未发命令；源码不得代可信身份实证。|
|4 旧记录/证据保留及本轮引用|冷保留/轮次/marker子项PASS，**整体恢复核验FAIL**；真实退回补证再验收NOT_RUN。|
|5 附件UI/失败重试/终态/正常退回全链|**FAIL渲染回归**（两场空白），其他主链与UI操作NOT_RUN。|

|用例|本次结果（完整项无PASS放行）|
|---|---|
|G0-D|同源运输PASS子项；真实件冷恢复FAIL；选择/保存/打开NOT_RUN。|
|T18|foreign owner/round及旧孤儿冷保留PASS子项；可信列表/搜索/事件/附件访问授权NOT_RUN。|
|T19|真实件分类执行FAIL；保存后submit/accept拒绝、隔离/下载/无权访问NOT_RUN，副本变更控制BLOCKED。|
|T20|NOT_RUN：真实待验→完成、可信独立登录、多角色禁自验、经理理由。|
|T21|旧记录/轮次/marker保留PASS子项，整体核验FAIL；真实completion_id/退回补证再验收NOT_RUN。|
|T22|截断任务保源、原recover保留PASS子项；索引核验FAIL；精确提交点中断/回执恢复控制BLOCKED。|
|T28|同候选/宿主/资源一致PASS子项；完整件冷恢复FAIL；真实保存→同Store重开NOT_RUN/调度BLOCKED。|
|T31|NOT_RUN：终态只读、重复验收/取消/关联故障。|
|T35|NOT_RUN：真实补证使旧确认/建议失效、迟到AI交错；模型0次不代该项。|
|U03|冷归属保留PASS子项；三可信主体同事实/权限动作/自验禁令NOT_RUN。|
|U06|冷历史/证据保留PASS子项、恢复核验FAIL；真实进度/完工/验收和退回链NOT_RUN。|
|U07|坏盘保源PASS子项；重复/丢响应/冲突/离线/重试输入保全NOT_RUN。|
|U08|坏tasks登录诊断可见PASS子项；真实完整件恢复空白FAIL；其余附件错误/无权/过期继续出口NOT_RUN。|
|U11|无parser PASS子项，冷渲染两场FAIL；登录后滚动/输入/切换NOT_RUN。|

唯一具体BLOCKED控制项：当前schema/runner每场fresh Store，不表达同Store顺序重开、运行期保存副本变更、精确提交点屏障/故障调度。当前明确禁止osascript/辅助功能/自动化，未使用ui_actions；rc.6内置可信非空输入未实测，不从旧宿主历史推出一切输入不能运行。驱动须在当前授权内提供宿主内置或人工既有流程的可信输入及上述调度，全证据保持同候选/宿主；身份/provider已裁决，不需新授权。**无ABORT；普通未执行操作标NOT_RUN，业务故障标FAIL，不能泛称环境BLOCKED。**

## 判定及交接

- **最终结论：FAIL。**范围为交接M5-r11冻结件、原缺陷及直接回归；不是整个当前共享源码的判定。
- 必修：**D-M5-04.B**修writer返回/实际主盘读回并让成员核验到达；**D-M5-04.C**修1024B真实附件指纹预算与空白，保持全内容/归属/轮次闸。按上述各自验证方式交新候选复审，优先这两项，不扩功能。
- 受影响前序：只做同候选坏tasks/保源/旧归属冷回归，结果写明子项；不代M2/M3/M4整体复验。BLOCKED-HOST挂账保持。
- 台账：`docs/optimization/2026-10-09-desktop/GATES.json`仅M5.status=FAIL与review_* / reviewed_*字段更新，review_report指本报告；r14当前审查字段完整归档至review_history，快照E/GATES.before-review-r15.json。旧作者字段含过时rc71/身份/provider等描述不静默改写，以本轮审查字段为当前判定。ACCEPTANCE.json保持原内容，避免把冷子项覆盖成完整原生验收。
- 没有下一模块入口或执行；未发消息、联网发布、公开签名/listing、push/部署。剩余为产品修复与控制覆盖，NEEDS_ABRAM=no。

STATUS=FAIL
NEEDS_ABRAM=no
