# M5 独立 Review r12

**最终结论：FAIL。B-M5-01 解析/空白回归重新打开：独立 11 场各有 4 条解析错误，业务区全部空白。D-M5-04 B/C 的核验代码与探针本轮未实际执行，不能关闭旧缺陷，也不能声称旧写后核验或全零指纹现象在本轮再次复现。11/11 CLEAN 仅支持隔离与回收通过。**

- 审查者 / 日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai；未委派代理、未修业务代码、未进入下一模块。
- candidate_id / base_candidate_id：`M5-r10-worktree` / `M5-r9-worktree`。按用户交接证据、summary.request、r10实施报告、CANDIDATE和GATES构建字段一致定位，未按mtime选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；工作树dirty，保留他人修改。源码668712 B，SHA256=`5e8bc1a7224f1d9c5ef3175c6a592ef3d222a8e50d50c444a52fb65f4222b690`；bundle digest=`1c5651b763df91ac70a60adbb51f7ff36f153f84286dda96f368479084420b19`。
- 作者报告：`reports/M5_IMPLEMENTATION_r10.md`；候选：`runtime/optimization/2026-10-09/M5/r10/CANDIDATE.json`；上一轮缺陷依据：`reports/M5_REVIEW_r11.md`，唯一旧OPEN P1 D-M5-04 B/C。仅检查旧项及直接受影响回归。
- 前置：M4仍为`FAIL / M4-r10-worktree / M4_REVIEW_r12.md`，无已接受M4 PASS。按用户前序挂账裁决继续局部重审，不修改M4，也不宣称串行前置通过。
- 宿主SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；harness SHA256=`226df8dd61409cb0c82a7e70a931c2637362445d8a4a9e5232254da29188d11a`；profile模板SHA256=`80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7`。
- 原生执行：外部驱动于**05:09:34–05:12:06 +08:00**执行本审查请求，11场均CLEAN、quit_http、宿主rc0，无ABORT。审查者没有在agent环境启动宿主或调用sandbox-exec/pgrep。
- 模型：全部needs_model=false；model_proxy_stats及模型代理环境缺省符合请求，MiniMax请求0，无402/欠费。主会话实际Router/型号、当前线程createdAt/标题接口无法核验，未冒称切换或命名。
- 阅读范围：第1段AGENTS/CONTEXT/00/01/02/M5/模板/r11缺陷/r10交接与差异；第2段阶段笔记、独立请求、全部summary/result/profile/日志/denials/MANIFEST、业务盘与真实附件、截图和相关源码。
- 实际运行范围：第1段隔离夹具准备和独立离线验签；驱动11场原生启动/截图；第2段只读证据审计。审计脚本不执行Splash业务，不产生可信SESSION或业务回执。
- 未运行：真实上传、保存后注入及双入口拒绝、可信独立验收/禁自验/经理理由、正常/退回完整链、同Store跨进程重开和精确提交点中断，T35实际失效。解析回归导致的未执行记NOT_RUN；只有明确的白名单能力缺口单列BLOCKED，不将解析失败归咎运行环境。
- 快照：第1段15项保护输入及339项冻结seed/镜像摘要核对未变；当前源、冻结源、每场镜像/installed/.running全部资源一致。签名运输manifest与工作树manifest不混称同一文件。写后保护核验见E/final-write-verification.json。
- 置信度：候选、隔离与回收、44条解析诊断、空白截图和业务盘未变**高**；具体parser内部规则及新writer/fingerprint运行正确性**未知**；可信业务全链**未知**。

## 证据与核验

以下短路径相对`runtime/optimization/2026-10-09/`：

- **H/**=`M5/native-runs/review_r2_0002_REQUEST_review_r2_0002/`，驱动原证据，未修改。
- **E/**=`M5/native/review_r2_0002/`，冻结源、差异、seed、夹具及审计。
- **R**=`M5/native/REQUEST_review_r2_0002.json`，SHA256=`177a0b6dd337ae9671ba2e99a646331bfab0a0ad1cb575331977b6adbc9adaf8`。
- **N**=`M5/native/REVIEW_NOTES_r2_0002.md`，第1段边界与预期。
- **A**=E/native-evidence-audit-r12.json；实际命令`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r2_0002/audit_phase2.py`，rc0，**5997项证据一致性检查，0不一致；不是5997项业务测试通过**。审计初版误将系统应用包纳入作品包比较，已按manifest.id限定octosense-repair后重跑；该脚本范围错误不列业务缺陷。

1. MANIFEST的**1865项**逐项重算摘要、路径作用域、唯一性及完整文件集合一致，无符号链接；summary.request与R全等，场景顺序/批次/result摘要一致。
2. 每场profile按实际run目录、控制口及无模型代理重建后逐字一致；profile_probes.ok=true，外写探针拒绝、created=false；五条敏感路径禁读探针均拒。全部HOME/app-data/cache/config/tmp及镜像环境路径位于本场run。
3. pre/post_pgrep均rc1、NONE、stdout/stderr空；pgid_members_after=[]，11场正常退出。驱动记录原HOME目录mtime未变、library_scan为空；审查者只读这些记录，不访问项目外目录。运行组采样均只记录宿主；采样不能证明完整生命周期从无其他瞬时子进程。
4. 每场files_written_in_run_dir均**123项**，排序、唯一性、存在与作用域、count逐项一致，无400项截断。它是按mtime采集的文件列表，包含seed副本，不能当作123次业务写入或推断执行了完工。
5. 全量sandbox-denials日志重新聚合与result.summary一致，含443外联、Metal外部缓存和/dev/dtracehelper写入拒绝；拒绝记录不是成功越界。日志范围可含其他系统进程记录，按harness相同规则重算，不将每条日志自动归因业务代码。
6. seeded_files与冻结输入逐项对应；每场hub镜像、installed和.running作品包完整资源集合与运输包全等。真实命令与R仅launch-hub/capture一致。日志确实加载668712 B作品源，但每场随后有4条parser诊断；`eval ... view=true`及宿主rc0不代表业务成功。
7. host_log_bytes、tail、markers、digest出现标记从完整原文重算一致。remote/listen/quit正常，无panic或no-catalog拒打开。**host_log_markers没有parser错误计数**，其panic=false不能代替零解析检查。
8. **22张PNG**（11 final+11 part），均2800×1696，capture与MANIFEST摘要一致；4种独特摘要逐种实际查看，全部作品区空白，无登录/工作台/附件表单。不能据整屏PNG和1280×800请求签完整尺寸验收。
9. 每场整个业务app-data文件集合/真实bytes与seed全等，tasks/state/actions/events/隔离accounts/索引/tmp/附件/canonical全部未变。缺失件未补、坏件未修、旧证据未丢，但**这属于未执行时的字节保全，不是权限拒绝、恢复成功或业务历史验收**。无新m5探针、系统恢复审计、recover或回执。
10. 独立原件384 B，中损67 B、首尾32 B及尺寸一致，SHA256=`4b80338376fef6b11467e07467f1a8bb3765fa5617df5fa4bf016200e6e8e61e` / `0714f10ed1a121578b5a3e917189aa4ec5fa9c219b2f1f311bebb3556c6b0737`。登记参考`9bbeadce`为诊断算法参考，不是原生上传生成摘要。
11. 全部无model_proxy_stats/代理统计文件/MM_KEY/OCTOSENSE_MODEL_ENDPOINT，符合needs_model=false；无ui_actions请求/日志。本轮未生成私钥，第1段作者两把离线私钥删除已核验，独立验签rc0。未publish/listing/公开签名或上传。

## 必需检查

|检查|独立操作/期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/隔离/回收|核完整包、实际命令、profile/probes/env/退出与摘要|同源同digest同宿主，11/11 CLEAN、无ABORT|PASS子项|R/H/result/profile/MANIFEST/A|
|零解析与冷启动渲染|11场应无解析错误且登录/业务区可见|各4条解析错误，22截图对应4种全为空白|FAIL B-M5-01|全部log/frames/A|
|D04-B旧数组/v3两成员恢复|legacy/envelope：4旧项保留，两个round0→13，counter13、v3落盘及核验成功|两场索引原文仍为输入，两个成员仍round0；无save-verify/audit|NOT_RUN，被B01阻断；旧缺陷未闭合|两场真实索引/state/tasks/A|
|D04-Btmp与退回marker|主盘截断、有效tmp：轮4/marker修平、成功后清tmp|主盘仍截断，tmp保持原内容，未生成恢复审计|NOT_RUN，不能当成功保留副本测试|marker_tmp_recovery/A|
|D04-A路径回归/新原件重建|basename导出当前路径，字节/canonical/摘要正确后READY|缺索引成员未重建，无新探针|NOT_RUN；A历史精确关闭不扩成当前运行PASS|basename_only_rebuild/A|
|D04-C摘要与异常分类|literal探针正确；新原件READY、中损/缺件/缺canonical正确拒信任|无fingerprint探针，分类没有执行；原盘原字节未变|NOT_RUN；不得声称本轮指纹仍全零|content_rebuild_matrix/log/A|
|外来归属/非法索引/截断任务|不夺归属，拒非法形状、保护原文、正确pending/recover|盘原文均保全，但业务初始化未运行，recover未生成|保全观察成立；各业务断言NOT_RUN|相关6场app-data/A|
|保存后故障双入口拒绝|UI保存后坏/缺/跨任务，重新完工/验收均拒|没有上传或命令执行，actions/events仍[]|NOT_RUN；实时注入调度通道BLOCKED|R/schema/A|
|可信独立验收与禁自验/经理理由|真实登录多主体，按主体权限实际提交|登录区空白，无可信SESSION或命令回执|NOT_RUN；获准文本输入通道缺口另列|frames/R/A|
|正常链、退回链、重启打开|真实命令到终态/退回再提交，UI/字节/事实/回执一致|全部业务链未执行，seed状态不作成功链|NOT_RUN；同Store重开调度BLOCKED|schema/frames/app-data|

## 缺陷

### B-M5-01 · P1 / 必修 / REOPENED：新增探针使主脚本解析回归，作品区空白

- **文件与行**：`app/bundle/main.splash:9226`，`m5_fs_probe`新增移位探针`try { _sh = (32 >> 4).to_string() } ...`附近；紧邻`:9223`掩码探针也应在最小修复中核对。宿主诊断首报`:9227:34`（与冻结文本行约1行偏差），不是任意文件时间定位。
- **触发**：按R任意场，干净隔离Store启动固定宿主，仅执行`launch-hub:octosense-repair`、`capture`；无需登录或业务操作即可触发。11场都复现。
- **预期**：零parser/type/scope诊断，登录视图可见，load/reconcile/probe初始化执行，然后才检查附件和验收行为。
- **实际**：每场4条错误：`Expected )`、`Expected expression ... found CloseRound`、两条`Expected } not found`；22张截图业务区空白；m5_fs_probe/m5_save_verify/m5_reconcile_audit均不存在，业务盘全等输入。
- **根因**：r10新增诊断表达式引入固定宿主解析不兼容，阻断整份脚本初始化。差异和定位把问题缩到新增探针附近；**具体是移位原语、括号表达式后方法调用还是parser组合规则，未通过最小运行实验唯一裁决**。try/catch只能处理运行异常，不能保护解析期失败；宿主rc0/view=true/CLEAN无零解析含义。
- **影响**：真实附件选择、保存、核验、完工和可信独立验收均不可用，直接阻断模块核心与硬验收1–5；属于本模块修复引入的回归，不能按前序挂账或建议放行。
- **证据**：H/cold_empty/logs/host.log及frames/cold_empty.png；其余10场同类日志/截图；A/scenarios中44条原始诊断及全部probe缺失；E/r9-to-r10-candidate.diff与冻结源。作者5场同类现象只作交叉参考，不作为独立复现依据。
- **具体改法**：先局部拆解新增移位/掩码探针为宿主已能解析的变量赋值，再对变量做to_string；必须逐个经固定宿主冷启动确认。若该原语本身不受支持，诊断明确记unsupported，避免把不能解析的语法放进主业务脚本；保留可执行的指纹和save-verify探针、canonical与权限/轮次守卫。不要直接硬改成功旗标、不要重写布局或其他模块。
- **验证方式**：harness冷启动零解析且登录真实渲染；同源包复跑本请求11场，确认探针真的落盘，随后按D04-B/C核实际值和对应业务链。仅静态平衡/移植测试/CLEAN不足关闭。

### D-M5-04 · P1 / 必修 / OPEN：B/C修复尚无有效原生验证，本轮NOT_RUN

沿用原编号，不将未执行编造成两个新业务失败。

|子项|文件行/原触发|本轮实际与预期|根因与影响|具体改法和验证|
|---|---|---|---|---|
|B 写后权威核验|`:9005` writer、`:9056` tmp clear、`:9062` commit包装、`:9072` field-eq、`:9492`起reconcile核验；原r11恢复写盘正确却index_saved=false|源码修复在位；本轮无save-verify/audit，索引/轮次未变。应在实际恢复后逐成员读回通过，整体成功才清tmp|当前阻断B01；r11实际失败来源保留，**新field-eq是否正确未知**；可靠恢复核心仍未证明|先修B01，只按分步原生actual值修B。配对旧数组/v3、两成员、orphan/foreign、退回marker/tmp全部核对，失败副本保留；不能补写假rb_ok或只比readyCount|
|C 原生摘要与完整件恢复|`:8803` xor8、`:8821` mix、`:8833` hex、`:8847` fingerprint、`:9121` probe；原r11literal全零且完整诊断件CORRUPTED|新指纹未执行、无探针；本轮不声称全零或完整件分类失败。应literal与所选算法一致、登记可解释、完整件读回有效|当前阻断B01；新整数运算/兼容性未知；真实证据恢复与登记仍未证明|先修B01，核literal及分步probe；再独立新文件上传登记/重读/同尺寸中损/缺件/缺canonical及完工、验收两入口。保留canonical全内容比对，不追认现存字节、不批改旧sha|

证据：上一轮`M5_REVIEW_r11.md`及其独立证据是原缺陷来源；本轮H/E/A只证明新候选解析失败及运行项未执行。D04-A、D-M5-01/02/03/05的旧精确关闭范围保留，**没有当前原生运行PASS可扩展**。

## 硬验收与既有用例

|硬验收|本轮状态与范围|
|---|---|
|1 真实选择/重启打开|NOT_RUN；解析/空白核心入口FAIL；本地包与隔离子项PASS|
|2 异常证据完工/验收拒绝|NOT_RUN；诊断坏件/缺件原字节保全不能代替两个入口拒绝|
|3 待验与可信独立终验|NOT_RUN；没有SESSION/登录/验收执行，不用标签或seed状态代验|
|4 旧证据/新轮次引用|NOT_RUN；原盘字节保全观察成立，恢复和新业务轮次未执行|
|5 桌面全链/失败恢复|FAIL B01空白；实际表单/打开/重试/终态/正常退回链NOT_RUN|

|用例|本轮判定及边界|
|---|---|
|G0-D|FAIL原生脚本/桌面入口；包/隔离PASS子项；真实文件选择/保存/打开NOT_RUN|
|T18|NOT_RUN可信列表/搜索/事件/附件权限；外来盘未变不等于拒访问|
|T19|NOT_RUN完整/异常件核验、双入口拒绝与下载；分类代码未执行|
|T20|NOT_RUN待验/独立终验/禁自验/多角色/经理理由|
|T21|NOT_RUN退回历史/新轮次/再完工验收；盘字节保全观察不代执行|
|T22|NOT_RUN索引/截断恢复、精确提交点故障/回滚/回执；未生成recover/audit|
|T28|FAIL真实宿主入口空白；installed/.running同包PASS子项；同Store附件重开NOT_RUN|
|T31|NOT_RUN终态只读/重复验收拒绝/关联新故障，既有源码守卫不代执行|
|T35|NOT_RUN证据变化使旧确认/建议失效，0模型调用不代表通过|
|U03|NOT_RUN三可信主体事实与禁自验|
|U06|NOT_RUN进度/完工/验收/退回历史区分|
|U07|NOT_RUN重复/响应丢失/冲突/离线/恢复；原盘没变不签恢复或输入保全通过|
|U08|FAIL桌面入口空白、没有可继续操作的出口；真实附件失败/重试/无权限出口NOT_RUN|
|U11|FAIL原生解析/渲染回归；真实滚动输入面板交互NOT_RUN|

## 判定

- **最终结论：FAIL**。必修：B-M5-01 REOPENED，D-M5-04 B/C仍OPEN且本轮运行NOT_RUN；没有因建议项判FAIL。
- 精确通过范围：固定候选完整资源与宿主一致、离线本地安装运输来源可追溯、11场隔离与回收、完整证据摘要/记录一致。它们不能替核心业务真实成立。
- 没有ABORT。解析错误是已运行后发现的产品缺陷，判FAIL，不写环境BLOCKED。源码修复正确性被此缺陷挡住的运行项记NOT_RUN。
- **仅具体白名单能力项BLOCKED**：本次允许的内置真实文本/键盘输入（固定宿主type/key不支持的既有证据见M3_REVIEW_r10；schema.ui_actions依赖本次禁止的System Events）、上传后隔离副本变更、同Store跨进程重开、精确提交点中断。当前schema没有后三项调度字段；不可伪造SESSION/回执或把prelaunch成功状态当实际链。需驱动提供符合本次约束的可执行输入/变更/重开/故障通道；不由审查方绕过禁令或修改harness。**NEEDS_ABRAM=no**，这些是技术缺口，身份/provider/离线签名已裁决；无计费错误或需公开发布事项。
- 受影响前序：冷启动回归已独立11场FAIL；因业务初始化未运行，不宣布M2/M3/M4旧运行结论在本候选有效。各前序挂账状态不改，不扩修。
- 修复顺序：构建方Kimi-K3先修B01并附固定宿主零解析/真实渲染截图，再复核D04-B/C actual值及本请求的受影响回归，补齐核心真实链证据；仅清单项，保留权限、canonical、轮次、旧记录和他人修改。
- 门禁：GATES.json仅M5审查字段及status更新为FAIL，review_report指向本报告；旧r11字段归档到review_history，构建字段和其他模块保留。原ACCEPTANCE.json未改，本轮精确范围记录在M5.review_acceptance，历史来源保留。
- 不允许进入下一模块，未执行M6。无业务代码修改、未读取明文凭据/provider密钥、无联网/上传/公开签名/publish/listing/push/issue/评论/消息/部署/更换计费渠道。

STATUS=FAIL
NEEDS_ABRAM=no
