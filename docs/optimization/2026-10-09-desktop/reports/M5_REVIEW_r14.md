# M5 独立 Review r14

**最终结论：BLOCKED。驱动在沙箱外运行本轮独立请求，但在第一场启动宿主之前发现已有 OctoSense 进程，触发 ABORT_PRE_PGREP_MATCH。八场业务均未执行，不能关闭 B-M5-01 或 D-M5-04 B/C，也不能签核心功能 PASS。不是 Codex 沙箱内 rc71/rc3 导致的阻塞。**

- 审查者 / 日期：Codex 主会话唯一独立审查者，2026-10-13，Asia/Shanghai；无子代理、业务代码修改或下一模块执行。
- candidate_id / base：**M5-r11-worktree / M5-r10-worktree**，HEAD 来源 `8d730569546cb57310944bb299695134df773b9d` 加共享未提交差异。冻结源 **771176 B / SHA-256 05c9ea2484eb3c2ee1dc5a97dde37e1f489501a42385dfd81b5803914dfe6365**，bundle digest **5bde47daba3ff19a98a9b0e079bbd9cd06eb16ae0d4b133dc45206395ab63544**。按用户交接、candidate、实施报告和实际请求定位，没有按 mtime 选版。
- 作者报告 / 上轮缺陷：`reports/M5_IMPLEMENTATION_r11.md`、`reports/M5_REVIEW_r13.md`；候选清单 `runtime/optimization/2026-10-09/M5/r11/CANDIDATE.json`。只复核 B-M5-01、D-M5-04 B/C 和受影响回归；不扩审其他模块。
- 前置：**M4=BLOCKED / M4-r12-worktree / M4_REVIEW_r14.md**，没有已接受的整体 PASS。按挂账裁决继续局部复核，不冒称前置满足。D-M2-05/D-M4-03 单列 BLOCKED-HOST，不作为本轮 FAIL/P1。
- 宿主：rc.6，`host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256 **2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a**。本批次核实了待运行二进制摘要，**没有实际启动这个宿主**。
- harness SHA `8115cb845fa69a5c312969c0829dd68c9d7467df6d597c536537e4923e3e28d7`；profile 模板 SHA `76b77eb7bb10d772769c442d16033f39bb94f38ae8540d18d3044b9ba049690f`，与第 1 段一致。
- 运行时间：summary 记录 **22:59:53–22:59:53 +08:00**；首场准备记录 wall_s=0.06，退出方式 null，summary=ABORT。请求八场，result 一份，启动宿主 **0 次**；其余七场连准备目录都未生成。
- 阅读范围：第 1 段 AGENTS/CONTEXT、00/01/02/M5/04、实施/候选/r13、相关源码与验收映射；本段独立 summary、唯一 result、profile/probes、完整 MANIFEST、全部运行文件与冻结夹具、harness 早退及结果记录代码。
- 实际模型：八场 needs_model=false，无代理启动或模型请求，模型 **0 次**，没有余额/402错误；NEEDS_ABRAM=no。没有读取秘密或明文凭据。
- 主会话 Router/指定模型、线程 createdAt 和标题设置仍无可核验接口，不声称切换或命名成功。
- 置信度：ABORT 原因、未启动/未执行范围、候选与准备盘一致性 **高**；本候选独立原生解析、恢复、指纹和可信业务链效果 **未知**。

短路径相对 `runtime/optimization/2026-10-09/`：**H/**=`M5/native-runs/review_r1_1659_REQUEST_review_r1_1659_recheck/`；**E/**=`M5/native/review_r1_1659/`；**R**=`M5/native/REQUEST_review_r1_1659_recheck.json`；**A**=E/native-evidence-audit-r14.json。源码行号均指 E/source.main.splash 的冻结源，不套用共享工作树。

## 必需检查

|检查|独立步骤与期望|实际|结果 / 证据|
|---|---|---|---|
|请求/候选/准备盘一致|核请求全文、固定资源、seed 和 MANIFEST|43 条 MANIFEST 及完整文件集合全等；40 个 seed 文件与冻结输入逐字全等|PASS **准备与证据完整性子项**，A；不是已安装运行 PASS|
|隔离/回收|profile/probes、前后进程、空进程组、CLEAN|profile/probes 合格；pre=MATCH；post/pgid_after 不存在；不是 CLEAN|BLOCKED 完整运行隔离/回收，不能从 probes 推导已回收|
|冷启动零解析与实际渲染|新候选零诊断且 UI 可见|Popen 前早退；本批次 logs/host.log、frames/*.png 全无|BLOCKED，B-M5-01 不能关闭；也不能判新候选解析 FAIL|
|写后权威核验与三成员/格式对照|legacy/v3 三成员 round23、读回成员完整及 index_saved=true|对应两场未启动；没有 save_verify/audit 或实际索引恢复|BLOCKED，D-M5-04.B 未验|
|新文件指纹/内容分类|新 ASCII/中文、同长同首尾中损、缺件/缺 canonical 独立对照|夹具字节已核；矩阵场未执行；无原生新实际值|BLOCKED，D-M5-04.C 未验；参考 hash 不代实际值|
|退回/旧证据/归属回归|tmp 回退、round9 退回、旧孤儿/他任务保留、跨任务碰撞拒信|对应场景均未执行|BLOCKED 冷恢复；没有历史保留或权限拒绝 PASS|
|坏任务安全加载|截断盘不接部分事实、保留源/旧 recover|对应场景未执行|BLOCKED；源码守卫不代运行|
|保存后双入口负例|真实保存后损坏/缺失/跨任务，submit 和 accept 都拒|无登录/上传/业务命令；当前 schema 无运行期副本变更调度|本批次 BLOCKED/ABORT；变更通道另列 BLOCKED，不冒充已拒绝|
|可信主体与经理理由|承接者多角色禁自验、经理空理由拒、独立验收仅到终态|无可信会话与实际命令；当前请求只 launch-hub/capture|本批次 BLOCKED/ABORT；业务操作 NOT_RUN，不以标签或预装 state 代认证|
|正常/退回/重启链及桌面操作|真实字节、事实状态、回执、UI 一致，终态只读|全部未执行；同 Store 跨进程/提交故障调度不在当前 schema|本批次 BLOCKED/ABORT；精确通道缺口 BLOCKED，其余业务步骤 NOT_RUN|

### result 字段逐项核对

1. summary.request 与 R 全等；八场顺序/batch 相符；唯一 summary 场景投影与 result 的字段全等，verdict 为 **ABORT_PRE_PGREP_MATCH**。driver_not_sandboxed_check 为 rc0/空 stderr。
2. result.profile.path/sha256 与实际 profile 全等；按 run 路径、项目根、记录的 HOME、控制端口 51842 及无代理规则重构 profile，逐字吻合。写入仅该场目录及 /dev/null，五类禁读和 osascript 禁执行规则保持，没有放宽。
3. profile_probes.ok=true：apply rc0、外写拒且 created=false、五条禁读均拒、osascript exec 拒。记录中的 probe rc71 是**驱动证明禁执行有效**，不是本轮阻塞原因。审查者未执行 probes 或再次访问禁读目标。
4. pre_pgrep 为 **rc0 / MATCH / 空 stderr**，记录 `35436 .../host-rc6/.../octosense --size 1280x880 --test-action launch-hub:octosense-repair --test-action capture:.../demo-video-20261013/run/frames/start.png`。这是运行当时库存，不证明该进程现在仍存活，也不裁决其归属、授权或隔离方式。
5. **post_pgrep、pgid_members_after、captures、files_written_in_run_dir、files_written_count、sandbox_denials、host_log_markers、model_proxy_stats 均缺失**；cmd/env/pid/pgid/host_returncode/finished 也缺。harness :662–664 在 Popen（:689）前 return，finally 只记录耗时/exit_method，跳过 :765 起的后置采集。因此这些字段是早退未采集，**不能当成 NONE、空数组、零错误或成功回收**。
6. frames 目录没有运行 PNG，logs/host.log 不存在；无法目视本批次 UI 或统计解析错误。seed 包里的 screenshots 是作品资源，不能冒充本轮 captures；未拿作者截图或旧独立输出代本轮截图。
7. MANIFEST **43 条**逐项重算 SHA-256，核唯一性、项目内路径、无文件 symlink 和完整文件集合，0 差异。运行目录文件集合严格等于 **40 个准备 seed 文件 + summary/result/profile 三文件**。40 个 seed 与请求两处输入目录及 result.seeded_files 全等，所有业务盘/附件字节保持；这是启动前未变化，**不是故障恢复或权限拒绝通过**。
8. 第一场 mirror/预装 bundle 完整资源与冻结源相符；digest_seen_in_seed=true。但没有实际运行的 .running 资源/宿主加载日志，不能称“运行候选已加载”。第二至第八场目录不存在。
9. needs_model 全 false，model_proxy/model_proxy_stats 缺失，早退前未调用代理路径，无模型请求；不是“启动代理并测得 0”。build_r11/keys 为空，作者删私钥证据保留；本段新私钥 0、未签名或发布。

实际审计命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/review_r1_1659/audit_phase2_r14.py`，rc0；**426 项证据一致性断言、0 差异**，不是 426 项业务测试通过。R SHA `b19569fa7483be88f97ce1da1c302d51f0b2aa0e4835f40f1c8e532a9d5d5475`；summary SHA `68ce0065c3624fdf5de36c24939a766dba0557dd85d3a2f1fd0b75bbabbd9331`；MANIFEST SHA `247b1ad009641119657c3c1e6a333c242c1f36fa7ba7e27414399c0a3b615294`。

## 缺陷与阻塞

### B-M5-TEST-R14-01 — BLOCKED / 环境前置，不计产品 P1

- **文件/行**：driver/harness/native_harness.py:657 采集库存，:662–664 匹配则安全早退；H/review_cold_empty/result.json 的 pre_pgrep/verdict。
- **触发/实际/预期**：驱动执行 R，已存在上述 demo-video 命令的宿主；首场 pre=MATCH，summary=ABORT，未启动作品。预期执行前库存 NONE，随后逐场启动、采集与回收。
- **根因/影响**：驱动的无既有宿主前置不满足；八场原生必需项全部不能裁决。不是业务解析故障，不是 agent 沙箱限制。
- **具体解阻**：由该已有运行的负责方完成并关闭其宿主；驱动在沙箱外通过既有 harness 核实库存 NONE，再将**同候选、同请求**运行到新的 native-runs 目录，交回全套证据。不绕过库存保护、不强杀来源未核实进程、不覆盖本次 ABORT 或旧 CLEAN 证据。审查者不改业务/驱动代码或启动宿主。
- **验证**：八场 summary/result 均实际生成；每场 profile_probes.ok=true、pre/post=NONE、pgid_members_after=[]、verdict=CLEAN；另核零解析与真实 UI、全部权威索引/附件/审计。CLEAN 本身仍不等于业务 PASS。

### 上轮编号闭合核对（保留历史来源，不新造产品故障）

|编号 / 严重性|文件与行、上一轮触发与影响|本候选实际 / 预期|根因、具体处理与验证|
|---|---|---|---|
|B-M5-01 / 历史 P1，当前未关闭|冻结源:11201–11210；r13 旧包探针两处括号位运算接方法解析失败，业务空白，阻断核心|新候选已纳入具名中间值适配；本批次启动前 ABORT。预期新候选零 parser/runtime 诊断且真正渲染|最小语法适配及新签名交接已定位；当前运行正确性未知，不能再断言新包仍有旧 parser 错误。先解阻重跑，不凭本批次盲改代码。核实际日志/截图和安装资源一致后关闭|
|D-M5-04.B / 历史 P1，当前未关闭|:11003 writer、:11070 字段比较、:11505 起权威核验；r13 未执行修复链，历史写后核验不能成立|本批次无 writer/save_verify/audit；预期三成员/全部保留项、主索引/tmp/内存/审计一致，整体核验后才清 tmp|作者参考三场 save_return=false、rb_ok=unrun 已在第1段登记；不能代独立运行或猜具体分支。重跑后按 writer 返回/读回/解析/成员比较实际失败点作**原编号内最小修复**，不硬改成功旗标、不削弱内容/归属/轮次闸|
|D-M5-04.C / 历史 P1，当前未关闭|:10801 xor8、:10819 mix、:10831 hex32、:10845 fingerprint，:11427–11445 全内容重建闸；r13 原生实际值未跑|本批次无 probe/新件分类；预期新内容参考与原生值一致，完整件 READY，坏/缺件拒信|源码算法与 canonical 主闸保留，作者 literal 探针不是独立新件/上传证据；解阻后运行矩阵，核真实完整字节及归属/轮次，不能只 readyCount 或只看固定 probe|

D04-A、D-M5-01/02/03/05 的历史限定关闭保持原范围；本轮相关原生回归全部被 ABORT 阻断，不能扩大为已验证全链。**本轮新增经实测确认的产品 P1=0，不代表历史两条 P1 已关闭，也不能据此 PASS。**

## 全部硬验收及既有映射

|硬验收|本轮结果|
|---|---|
|1 真实选择/保存/重启打开|BLOCKED（本批次 ABORT）；实际上传/同 Store 重开 NOT_RUN，预装夹具不代真实保存|
|2 六类异常在完工/验收双入口拒绝|BLOCKED（ABORT）；运行期保存副本变更通道另有具体缺口，双入口命令 NOT_RUN|
|3 待验/可信独立验收/禁自验|BLOCKED（ABORT）；三主体真实认证及理由实操 NOT_RUN|
|4 旧记录/旧证据/新轮次明确引用|BLOCKED（ABORT）；round23/退回round9冷子项和真实退回主链均未跑|
|5 附件UI/失败重试/验收/终态/全链|BLOCKED（ABORT）；本批次无截图、无业务命令，不借其他批次 UI 放行|

|用例|精确范围与未执行项|
|---|---|
|G0-D|准备盘同源子项 PASS；原生文件选择/保存/打开 BLOCKED/ABORT，业务 NOT_RUN|
|T18|跨任务碰撞冷回归 BLOCKED；可信列表/搜索/事件/附件权限 NOT_RUN|
|T19|新件/坏件/缺件/缺 canonical 分类及完工/验收拒绝 BLOCKED；隔离/下载/越权实际操作 NOT_RUN|
|T20|可信待验→终态、多角色禁自验、经理理由 BLOCKED；实际命令 NOT_RUN|
|T21|退回marker/tmp/旧证据保留冷回归 BLOCKED；新completion_id及真实再验收 NOT_RUN|
|T22|坏tasks/索引回读回归 BLOCKED；精确提交点注入/回滚/回执调度通道 BLOCKED|
|T28|候选准备摘要 PASS；真实操作/同Store重开 BLOCKED，未建立原生同版本运行证据|
|T31|终态只读、重复验收/取消/关联故障 BLOCKED；业务 NOT_RUN|
|T35|证据变化使旧确认/AI建议失效 BLOCKED；动态交错 NOT_RUN，模型0次不代验收|
|U03|三可信主体事实一致、权限动作和禁自验 BLOCKED；未登录|
|U06|进度/完工/验收及真实退回历史保留 BLOCKED；夹具非执行事实|
|U07|重复/丢响应/版本冲突/离线/重试输入保全 BLOCKED；实际操作 NOT_RUN|
|U08|附件失败/重试/无权/过期可继续出口 BLOCKED；本批次无UI|
|U11|原生零诊断/渲染/滚动/输入/切换 BLOCKED；没有日志或capture可裁决|

仅 ABORT 与明确白名单覆盖缺口记 BLOCKED。当前 schema 的每场 fresh Store 不表达同 Store 跨进程顺序重开、运行期附件副本修改或精确提交屏障；这些通道需驱动在授权内补可核验调度。当前用户禁止系统自动化，故不能用 ui_actions 的 osascript 实现补真实输入；本批次也未探测 rc.6 的内置 type/key，不能把旧版本记录直接当 rc.6 的实际不支持结论。普通未执行步骤标 NOT_RUN，均不因源码存在判 PASS。身份/provider/离线签名已授权，不是 NEEDS_ABRAM。

## 判定、门禁与复核边界

- **最终结论：BLOCKED**；精确范围为 M5-r11-worktree 本次独立请求未能启动。不是 PASS，不以建议项或历史 BLOCKED-HOST 判 FAIL，不将 r13 旧包 FAIL 自动改判新候选 FAIL。
- 必需解阻是 B-M5-TEST-R14-01；B-M5-01 与 D-M5-04 B/C 保留“历史未关闭/本轮运行 BLOCKED”，没有新产品修复清单，先获得可执行的独立证据再按实际失败点处理。
- 第1段保护输入与第2段审计开始全等；共享工作树本就不同于冻结候选，没有换审。报告/门禁写入后仅 GATES 为获准改变的保护输入；其他模块、M5 构建字段和原台账保持。旧 M5 审查字段完整备份 E/GATES.before-review-r14.json，并按既有 review_history 结构归档，旧报告不覆盖。
- 更新 `docs/optimization/2026-10-09-desktop/GATES.json` 的 M5 状态/审查字段：BLOCKED、当前候选、r14报告及真实 ABORT/未测范围；`docs/build-loop/ACCEPTANCE.json` 不变。本轮无新的业务 PASS/FAIL 数据，不用 ABORT 污染历史验收。
- 第1段误读项目外记忆索引已披露，未用于候选/裁决；不能声称整轮全程项目内读。本第2段只访问项目内证据，未启动宿主、执行 sandbox-exec/pgrep、读取秘密/真实明文凭据、发消息、联网发布或终止其他进程。原生 ABORT 不抹掉审查者第1段偏差。
- **不允许进入下一模块。** 解阻后只补本模块同候选的独立运行和白名单缺口证据，保留本次 ABORT 来源。

STATUS=BLOCKED
NEEDS_ABRAM=no
