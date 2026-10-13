# M5 独立 Review r13

**最终结论：FAIL。交接候选 M5-r10-worktree 在八场独立原生运行中均有四条解析错误，作品业务区全部空白；B-M5-01 未闭合。D-M5-04 B/C 的代码未实际执行，本轮运行验证 NOT_RUN，不能关闭，也不能声称再次出现写后核验失败或指纹恒零。八场 CLEAN 仅支持隔离与回收通过。**

- 审查者 / 日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai；没有子代理、业务代码修改或下一模块执行。
- candidate_id / base_candidate_id：`M5-r10-worktree` / `M5-r9-worktree`。按 GATES 构建字段、M5_IMPLEMENTATION_r10、CANDIDATE、冻结源、签名运输包及实际请求定位，未用 mtime 选版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作树 dirty。冻结候选源 **668712 B**，SHA-256 `5e8bc1a7224f1d9c5ef3175c6a592ef3d222a8e50d50c444a52fb65f4222b690`；bundle digest `1c5651b763df91ac70a60adbb51f7ff36f153f84286dda96f368479084420b19`，版本 `0.1.0-b`。
- 当前共享工作树源是 **702182 B / `805257a2b6a14834d9ab092e17cc10fb143710803812c4999d55abfadaed6ae9`**，不是该候选；其中有 M6 对解析表达式的最小适配及其他后续差异，没有被本请求安装或被算成新 M5 候选。本报告结论限定于冻结交接包，**没有判定当前工作树仍有同一解析故障**。
- 作者报告：`reports/M5_IMPLEMENTATION_r10.md`；候选：`runtime/optimization/2026-10-09/M5/r10/CANDIDATE.json`。唯一上一轮缺陷依据：`reports/M5_REVIEW_r12.md`。仅核 B-M5-01、D-M5-04 B/C 与直接影响回归。
- 前置：M4 仍为 **FAIL / M4-r10-worktree / M4_REVIEW_r12.md**，不存在已接受 M4 PASS；按用户前序挂账裁决继续局部复核，不修 M4、不冒称前置满足、不改其结论。
- 实际宿主：固定 launcher SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮 harness SHA-256 `8141b4de36e8a248a1b7ed0b9d430fa3ee464ccbc65fc927ef1de40be5ef34c8`；profile 模板 `76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`，与第1段保护清单一致。
- 驱动执行时间：**09:58:13–10:00:02 +08:00**，八场均正常 quit_http、宿主 rc0、CLEAN；没有 ABORT。审查者没有启动 launcher 或自行调用 sandbox-exec/pgrep。
- 实际模型：所有 needs_model=false，模型请求 **0**；model_proxy_stats 未生成，符合请求。未出现计费错误。主会话实际 Router/指定模型、线程 createdAt 和改标题接口不可核验，未声称切换或命名成功。
- 阅读范围：第1段 AGENTS/CONTEXT/00/01/02/M5/04、实施报告/候选/上一轮缺陷和相关验收；本段请求/笔记/summary、八份 result、全部日志/profile/denials、MANIFEST、真实业务盘与附件、三种独特截图、直接相关源码/差异。
- 实际运行范围：审查方隔离夹具与离线验签准备；驱动八场原生启动/截图；本段只读证据审计及报告/门禁写入。审计不运行 Splash 业务、不创建可信主体或业务回执。
- 快照一致性：15项保护输入、全部冻结 seed/镜像、运行 mirror/installed/.running 资源核对一致；本段写入时 GATES 是唯一获准改变的保护输入，其原审查字段归档，其他受保护文件保持摘要。第1段工作树与候选本就不同，未混记。
- 置信度：候选/宿主/隔离回收/32条解析诊断/空白截图/未变业务盘 **高**；具体 parser 内部规则、新 writer/fingerprint 在宿主执行的正确性及可信业务全链 **未知**。

## 证据与独立核验

下列短路径相对 `runtime/optimization/2026-10-09/`：

- **H/**：`M5/native-runs/review_r2_0949_REQUEST_review_r2_0949/`，外部驱动原证据，只读。
- **E/**：`M5/native/review_r2_0949/`，冻结源、完整差异、seed、独立夹具与审计。
- **R**：`M5/native/REQUEST_review_r2_0949.json`，SHA-256 `b5c15f94110b5c8ad4fe2da4d795b01f6d84c5fcb5bd3b02a4fd0d06d7c20d2c`。
- **N**：`M5/native/REVIEW_NOTES_r2_0949.md`，第1段范围和各场期望。
- **A**：E/`native-evidence-audit-r13.json`。实际命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r2_0949/audit_phase2.py`，rc0，**4421项证据一致性检查、0差异**；这不是4421项业务测试通过。

核验结果：

1. **1370个 MANIFEST 条目**逐项重算 SHA-256、核路径/唯一性/完整文件集合，无符号链接。summary.request 与 R 全等，场景顺序/批次/各 result 摘要一致，外部驱动检查 rc0。
2. 每场 profile 按本次 run、项目根、记录的敏感目录及控制端口重建后逐字一致；profile 摘要匹配。全部 HOME/app-data/cache/config/tmp/镜像路径在各自新 run；profile_probes.ok=true，外写探针 created=false，五条禁读探针全部拒绝，禁执行 osascript 探针亦拒绝。这是驱动的隔离探针，不是审查者在自身沙箱做预检。
3. pre_pgrep/post_pgrep 均 rc1、NONE、输出空；pgid_members_after=[]，host_returncode=0，quit_http=ok。驱动记录原 HOME mtime 未变、library_scan 无新增修改。只读取记录，没有访问项目外目录。运行组采样不能证明完整生命周期从无瞬时子进程。
4. 每场 files_written_in_run_dir **123项**，逐项核存在/作用域/唯一性/顺序/count，未达400项截断。该列表按mtime采集，包含复制的seed，不能称123次业务写入。
5. sandbox-denials.log 全文重新聚合后与 result.summary 一致，含443外联、Metal外部缓存、/dev/dtracehelper和osascript执行被拒记录。**拒绝记录不是成功越界**；聚合可能包含其他系统进程日志，不能自动将所有记录归因本应用。没有发现成功越界证据。
6. seeded_files 与冻结输入全等；每场明确有 apps/catalog.json，无 catalog 自动补齐或拒打开告警。运行 mirror、installed、.running 的作品包全部资源集合和字节与签名运输包相同；实际命令仅 launch-hub/capture，与 R 一致，没有 ui_actions/type/key/--help。
7. host_log_bytes/tail/markers/digest标记均由全文重算一致。日志显示加载 **668712 B** 作品，但每场随后有四条 parser 错误。host_log_markers 的 panic=false、app_not_opened=false 及 eval/view=true **没有零解析含义**。
8. **16张PNG**，尺寸为2560×1232或2560×1606，capture摘要与MANIFEST一致；共三种独特摘要，逐种实际查看：作品业务区全空，无登录/工作台/附件表单。其余图按摘要相同核验；不能凭整屏截图及1280×800请求签尺寸/完整UI验收。
9. 每场整个业务 app-data 文件集合/全部字节与seed全等：tasks/state/actions/events/隔离账号/索引/tmp/附件/canonical未变。无新增探针、恢复审计、recover、可信session或业务回执。**未执行时字节保全不等于恢复、权限拒绝或历史业务保全通过**。
10. 独立新原件/坏件均640 B，首尾32 B一致；在217–307区间置换91字节，实际有**90个字节不同**。原 SHA-256 `54788d1eeb68c314e7730a0a9ca0ce5804b2b6d5b802f84ff53aaec8a6144ca3`，坏件 `ccec12123cb6ace2b8688b8cd2052a5a8603d3e44d6a14c3d58e22ee867cecee`。登记参考 `c86d1b9a` 是审查诊断参考，不是原生上传生成摘要。
11. 所有场无 model_proxy_stats/代理统计/MM_KEY/OCTOSENSE_MODEL_ENDPOINT，符合 needs_model=false；模型服务注册日志不等于模型请求。无 billing_error、无真实 MiniMax 调用。本轮未生成私钥，第1段离线verify rc0、作者两把私钥删除来源和当前不存在状态已核验；没有公开发布或联网签名。

## 必需检查

|检查|独立操作与期望|实际|结果|证据|
|---|---|---|---|---|
|候选/宿主/隔离回收|完整资源/实际命令/profile/probes/退出及摘要一致|八场同源包、CLEAN、NONE、空进程组，0摘要差异|PASS子项|R/H/result/profile/MANIFEST/A|
|冷启动零解析/真实渲染|八场零错误、登录可见、boot执行|每场四条错误，16截图全空白；无probe|FAIL B-M5-01|全部log/frames/A|
|D04-B旧数组/v3两成员|两round0→17，四旧项/owner/round保留；落盘与核验一致|两成员仍round0，盘为原文，无save_verify/audit|NOT_RUN，被B01阻断；旧项未闭合|legacy_round17/envelope_round17业务盘/A|
|D04-B退回marker/tmp|退回round6标记/counter修平，整体成功才清tmp|主索引仍截断，tmp仍3683 B，未执行恢复|NOT_RUN，不把副本未变签作成功|marker_tmp_recovery业务盘/A|
|D04-A basename回归|从过期路径定位当前真实件、正确basename及登记|索引缺项未重建，无resolver执行结果|NOT_RUN，历史精确关闭不扩展|basename_only_rebuild/A|
|D04-C指纹/好坏分类|literal正确，新完整件READY，中损/缺件/无canonical拒信|无fingerprint探针或分类；坏件/缺件原样|NOT_RUN，不声称指纹再次恒零|content_rebuild_matrix/A|
|跨任务归属/坏任务保源|外来不夺归属，截断拒采纳并生成可读恢复来源|旧记录/字节未变，无业务拒绝或recover|NOT_RUN；只观察到字节未变|foreign_collision_v3/truncated_tasks_preserve/A|
|保存后故障双入口拒绝|实际上传后坏/缺/跨任务，完工及验收均拒|无上传、登录或业务命令|NOT_RUN；实时变更调度通道BLOCKED|R/schema/盘/frames|
|可信独立验收|真实三主体、多角色禁自验、经理理由实际校验|空白，无SESSION/回执或验收执行|NOT_RUN；允许的真实文本输入通道缺口|R/schema/log/frames|
|正常/退回/重启链|真实命令到终态/退回新轮次，字节/事实/回执/UI一致|业务全链未执行；seed不是成功链|NOT_RUN；same-Store重开调度BLOCKED|R/schema/业务盘|

## 缺陷

### B-M5-01 · P1 / 必修 / OPEN（沿用r12 REOPENED）：冻结交接包解析失败、业务区空白

- **文件与行**：`app/bundle/main.splash` 的 M5-r10冻结内容，E/source.main.splash:**9223、9226**，m5_fs_probe 两个括号位运算后直接 to_string 的探针表达式。固定宿主首报`:9227:34`，与冻结文本约1行偏差；不套用当前工作树的偏移行号。
- **触发**：按R任意场，用本地签名catalog在fresh Store启动固定宿主，只执行launch-hub/capture。无需登录或选择附件。**八场独立重复成立**。
- **预期**：零parser/type/scope诊断、真实登录渲染，load/reconcile/probe执行，随后附件与验收可操作。
- **实际**：每场`Expected )`、`Expected expression … found CloseRound`、两条`Expected } not found`；共32条，16截图业务区空白，三类M5探针/审计都不存在，整个业务盘未变。
- **根因**：冻结交接包仍含r12已定位的不兼容探针表达式，解析期失败阻断全主脚本；try/catch不能保护解析错误。具体parser内部组合规则未通过本轮最小运行实验唯一裁决，不把推断写成实测。
- **影响**：真实附件保存/核验、完工及独立可信验收全部不可用，直接阻断模块核心和硬验收1–5。不是环境BLOCKED，也不是可挂账建议。
- **证据**：H/cold_empty/logs/host.log:45–48、frames/cold_empty.png；其他七场同源错误和空白；A全部diagnostics/probe缺失及盘字节核对；E/source.main.splash与冻结摘要。
- **具体改法**：当前共享工作树已有M6适配（来源见M6_IMPLEMENTATION_r9:11–18），构建方先把该最小修复纳入**明确的新M5候选交接**：列出相对M5-r10的实际差异、完整资源摘要、匹配的本地签名安装包及零解析冷启动证据；不能只引用工作树修好、却继续交付旧签名包。保留权限、canonical、轮次/固定集合和他人修改，不改布局、不由审查方修业务代码。
- **验证方式**：驱动harness同候选冷开零错误且登录真实可见，再复跑本请求覆盖的启动恢复场景；若候选改变，更新请求/摘要/运输包并明确哪些前序差异需回归。仅移植测试、静态语法检查、CLEAN或宿主rc0不足关闭。

### D-M5-04 · P1 / 必修 / OPEN：B/C在本轮仍未实际运行

保留原编号和历史失败来源；不把未执行编造成新的writer或指纹失败。

|子项|文件/行与触发|实际/预期、根因及影响|具体改法与验证|
|---|---|---|---|
|B 写后权威核验|冻结源:9005 writer、:9056 tmp clear、:9062 commit、:9072 field-eq、:9492起核验；旧r11正确落盘却报告失败|新核验源码仍在；本轮无save_verify/audit，成员/round未变，实际正确性未知。应逐成员及真实盘一致、整体成功才清tmp。当前直接阻断B01；可靠恢复核心未证明|先闭合B01；按原生save_return/read/parse/extract/len/成员actual定位最小失败点，保完整失败副本，不硬改成功旗标。复跑旧数组/v3两成员、退回tmp、外来/孤儿；字节、完整字段、状态和审计一起核对。|
|C 指纹与完整件|冻结源:8803 xor8、:8821 mix、:8833 hex、:8847 fingerprint、:9121 probe；旧r11恒零/完整件CORRUPTED|新算法源码仍在，但本轮没执行probe或内容分类；不声称仍恒零或再次误分类。应实际literal符合算法、完整新件自洽且坏件拒信；当前B01使核心真实证据正确性无法判定|先闭合B01；核分步原语与literal，再实际新文件上传/读回，保存副本中损/缺失/跨任务，两入口拒绝。不追认现存坏件为基准、不批改sha，保canonical全内容闸。|

证据：r11独立实际值为历史来源；r12缺陷清单为本轮范围；本轮H/E/A只证明解析失败和业务未执行。D04-A、D-M5-01/02/03/05历史精确关闭保留，当前没有可扩展的原生业务PASS。

## 全部硬验收与相关既有用例

|硬验收|本轮结论与范围|
|---|---|
|1 真实选择/重启打开|FAIL核心入口解析/空白；真实选择/保存/打开/同Store重启NOT_RUN；签名同源/隔离PASS子项。|
|2 异常证据完工/验收拒绝|NOT_RUN；中损/缺失/foreign诊断盘未变不能代两个入口拒绝，隔离/越权/过期轮次实际拒绝未跑。|
|3 待验与可信独立终验|NOT_RUN；无可信登录/多角色验收/经理理由/真实状态迁移，不以界面标签代身份。|
|4 旧证据保留与新轮次引用|NOT_RUN；旧盘字节保全观察成立，恢复/实际退回/新completion引用未执行。|
|5 桌面附件与全链|FAIL空白且不可操作；真实预览打开、重试、验收表单、终态只读、正常和退回链NOT_RUN。|

|用例|本轮判定及精确边界|
|---|---|
|G0-D|FAIL原生解析/桌面入口；PASS签名包/隔离子项；真实文件选择/保存/打开NOT_RUN。|
|T18|NOT_RUN可信列表/搜索/事件/附件访问控制；外来字节未变不等于拒访问。|
|T19|NOT_RUN完整/坏/隔离/他人件核验、下载和完工/验收拒绝；分类未执行。|
|T20|NOT_RUN待验、可信独立验收、承接者多角色禁自验、经理理由。|
|T21|NOT_RUN退回历史/新completion_id/新轮次/再验收；seed记录不代业务链。|
|T22|NOT_RUN索引/tasks恢复、精确提交点故障/回滚/回执；未生成recover/audit；精确故障调度BLOCKED。|
|T28|FAIL同候选真实入口空白；PASS完整installed/.running同源包子项；同Store重开附件NOT_RUN，重开调度BLOCKED。|
|T31|NOT_RUN终态只读、重复验收、取消与关联新故障；旧源码闸不代实际操作。|
|T35|NOT_RUN证据变化使旧确认/AI建议失效；0模型调用不代表通过。|
|U03|NOT_RUN三可信主体一致事实/按权限动作/禁止自验。|
|U06|NOT_RUN进度/完工/验收/退回历史真实区别与保留。|
|U07|NOT_RUN重复、丢响应、冲突、离线/恢复与输入保全；原盘未变不是恢复成功。|
|U08|FAIL空白界面无可继续操作出口；真实附件失败、重试、无权限/过期出口NOT_RUN。|
|U11|FAIL真实宿主解析/渲染；实际滚动、输入、面板稳定性NOT_RUN。|

## 判定与修复交接

- **最终结论：FAIL。** 必修仅B-M5-01和D-M5-04 B/C，没有因建议或锦上添花项判FAIL。
- 通过范围：候选/完整安装资源/宿主一致、八场隔离与进程回收、1370条证据摘要及记录一致。它们不构成真实附件完工与独立验收成功。
- 无ABORT。解析故障已原生实际执行并发现，判产品FAIL。被其挡住的恢复/指纹及业务项NOT_RUN，不能改称环境BLOCKED。
- **仅以下白名单无法覆盖的具体通道记BLOCKED**：本次禁用系统自动化而固定宿主内置type/key无支持的既有证据（M3_REVIEW_r10）；schema无上传后运行中副本变更、同Store跨进程串联重开、精确提交点中断/屏障字段。需驱动提供符合当前用户约束的真实输入/故障变更/重开调度或人工操作的可核验证据。不得由审查者绕过禁令、造SESSION或改成功状态。这些技术缺口 **NEEDS_ABRAM=no**；不使用agent沙箱rc71/rc3当阻断。
- 当前共享工作树的M6适配与本候选分离；本轮结论不自动否定适配后的工作树，但也不替它作原生验收。需新M5候选/同源证据才能关闭交接缺陷。
- 受影响前序：冷启动回归八场实测FAIL，业务初始化未执行，不能宣布M2/M3/M4旧业务运行结果在本冻结包仍成立。各前序挂账不改、不扩修。
- 修复顺序：①新M5候选包含解析修复并交接匹配包；②harness冷启动零诊断且真实渲染；③逐成员/全字节验证D04-B/C actual；④补齐真实可信主体正常/退回/重启链与上传后双入口负例。只按清单修，保留原权限、固定引用、轮次、canonical、旧来源和他人改动。
- 门禁：GATES.json只更新M5 status与审查字段，review_report指向本报告；旧r12审查字段归档review_history，构建字段/其他模块保留。原ACCEPTANCE.json未改，本轮精确映射写M5.review_acceptance，历史来源保留。
- 不允许进入下一模块；未执行M6。没有业务代码改动、读取明文凭据/密钥、联网/上传/公开签名/publish/listing/push/issue/评论/消息/公网部署或更换计费渠道。

STATUS=FAIL
NEEDS_ABRAM=no
