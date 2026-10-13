# M7 独立 Review r4

- 最终结论：**BLOCKED**。`M7-r4-worktree` 的原 B-M7-01 仍未闭合：项目内写隔离/进程清理预检不可执行，驱动仍绕开 launcher sandbox，实际加载候选及核心原生业务链没有证据。不是因 P2 建议或前序 FAIL 单独拒收。
- 审查者 / 日期：Codex 当前主会话，唯一独立审查方，无子代理；2026-10-11T11:12:14.365087+08:00。工具未提供可验证主会话 Router 路由/切换 gpt-6.1-sol 的能力，不声称已切换或满足指定模型身份。置信度：文件摘要、命令输出与驱动控制流反例 **高**；目标宿主实际业务/UI及模型效果 **未知**。
- candidate_id / base：`M7-r4-worktree` / `M7-r3-worktree`。由 GATES:3180 的候选字段、r4 实施报告:4–6、r4/CANDIDATE.json:2–3 相互定位，未按 mtime 选择。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r4.md`；本报告取下一个 Review 编号 r4。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作区 dirty。本轮 git 读回的已跟踪修改：PROGRESS.md、README.md、app/README.md、app/bundle/main.splash、app/bundle/manifest.json、docs/VERIFICATION.md、docs/build-loop/ACCEPTANCE.json、docs/implementation/10_UI_UX_SPEC.md、submission/2026-10-06-native/CURRENT_REVIEW_STATUS.md、submission/2026-10-06-native/HUB_ISSUE.md；不 reset/stash/删除这些改动。
- 被审包：`runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/`，0.1.0-c，manifest BLAKE3 `a7451d34d7aa808bc534df0350b5e501cc5fc83a9861f296e9ea4574c9b2ea10`。r4 是驱动/材料新候选，应用字节仍为 r2；不能称它已包含 M2–M6 r4 业务修复。
- 冻结主源：SHA-256 `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6` / 283933 字节；工作区主源 `1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2` / 369061 字节。r4 已披露差异，未把工作区证明嫁接给旧包。
- 前置：M6 `M6-r4-worktree` / `M6_REVIEW_r4.md:3,140–146` = **FAIL**，没有独立接受的 PASS 候选。按用户明确挂账裁决继续限定 M7 复审；不将前置改成 PASS，不要求本轮代修全部前序缺陷。
- 宿主：指定 M0/r3 提取的 OctoSense.app。octosense 223391280 字节，SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；octos-kernel 126117168 字节，SHA-256 `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`，本轮独立重算均一致。来源按项目历史记录 0.1.0-rc.1 / 20261008.091752；本轮未重新验证发行下载或源码可复构性。
- 阅读范围：先读现有 CONTEXT_M7，随后实际 AGENTS、00/01/02、M7 指令及04模板；r3缺陷、r4实施/清单/驱动/材料/作者日志、受影响r2准入/Store证据、最新M6结论及原64定义。只做原缺陷与受影响回归，未扩审无关业务代码。CONTEXT 的旧身份/provider“待授权”说法被当前用户裁决覆盖。
- 已运行：逐文件SHA/大小和原64定义对照；hub check；隔离/进程预检；现存驱动7个内存mock控制流场景。mock文件写、目录创建、删除、线程、Popen、signal均替换，不启动宿主，不覆盖作者证据。
- 未运行：真实launcher、中文键入/滚动/视口/三角色任务流程、权威回执、正常/退回/失败/重复/业务重启、真实附件、真实模型和新截图/演示；预检失败，不直接非隔离启动。真实模型请求 **0**，未访问原身份数据、`CREDENTIALS_FOR_ABRAM.md` 或 provider密钥。
- 写入范围：仅本报告与 GATES 的 M7 status/审查字段/历史；没有新增或改写运行证据、业务代码、候选、原验收台账、其他模块及 external_delivery。会话内存保存146个相关文件摘要，结束回读核验。工具未提供自身 createdAt/改标题接口，且本轮仅授权报告/门禁写入，未声称实际改名。
- 操作偏差：开始时按上级记忆要求只读访问了项目外 MEMORY.md，违反用户本轮项目内访问边界，已当场说明；随后不再主动访问项目外材料。此偏差不被描述为符合约束；本轮没有启动宿主或进行项目外文件写入。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|D-M7-01 准入回归|运行精确冻结目录 hub check|准入成功，区分独立scan|rc0 PASSED，unsigned警告，storage/16MiB、hosts空、agent none；scan未跑|原缺陷CLOSED；准入子项PASS|下方独立命令；冻结manifest|
|D-M7-02 / A-M7-03 指纹|独立解析表中16行、重算外存自哈希|12包+4材料+1自排除一致|16/16大小与SHA匹配；3189字节自哈希匹配；包未变|CLOSED，指纹子项PASS|INTEGRITY:33–54；r4/evidence/integrity-selfhash.txt|
|D-M7-03 编号口径|原64与ACCEPTANCE.title逐条对照|原定义不替换、未跑不冒PASS|64/64一致，额外L8-DV2保留；本轮整项状态见下表|CLOSED（定义/口径子项）|原ACCEPTANCE与本报告64表|
|B-M7-01 安全启动|先隔离写预检、再枚举进程|预检成功才可启动|sandbox rc71、pgrep rc3；未启动launcher|BLOCKED|下方独立命令|
|B-M7-01 驱动|读cmd/catalog，mock错误与异常|隔离先行、确证加载、不误PASS、清理|直接Popen未套sandbox；预检rc3仍spawn并PASS；spawn异常写PASS；部分收尾反例已改善|OPEN，P1必修|r4 driver:119–172,248–273；下方mock表|
|硬1 全必需门槛|核实际可用证据|同候选原生核心成立|没有同候选原生业务/全部UI实证，静态总数不能替代|BLOCKED|B01；64表|
|硬2 同版本链路|核启动日志、模型配置、实际回执|正常/退回/失败/重启/模型同包|作者3次启动仅launcher进程记录，未证明包加载或业务结果；包模型OFFLINE|BLOCKED，模型NOT_RUN|run.json、launcher.log、model_config:5–9|
|硬3 同版本材料|核17个文件、截图来源、主源/config|源码、包、图、演示、描述一致|字节指纹一致且旧主源差异披露；6张仍旧B图，未录当前演示；启动绑定描述仍不实|BLOCKED；指纹PASS|INTEGRITY、SOURCES、listing|
|硬4 本地路线/准入/干净启动|新check+回读相同摘要r2独立Store证据|安装/准入与实际运行分别成立|check新PASS；历史install_staged/恢复/may_run子项保留；当前原生运行与scan未跑|BLOCKED|review-r2/results/local-store-validation.json；B01|
|硬5 状态分离|核本候选实际外部回执|本地/发布/赛事/收录各自记录|本地BLOCKED，P06/P07/P08 NOT_RUN，不把旧B回执移植|PASS（状态区分）|判定表；candidate/listing|

## 独立命令、字节与控制流证据

所有CLI运行cwd=`runtime/optimization/2026-10-09/M7/r4/sandbox/`，HOME/CFFIXED_USER_HOME/TMPDIR/XDG缓存/配置/数据/OCTOSENSE_HOME/Metal缓存均设到该项目内隔离目录。不传`--help`、不联网、不执行作者的重建/篡改/签名脚本，以免改冻结包或覆盖证据。

1. `sandbox-exec -p '(version 1)(allow default)(deny file-write*)(allow file-write* (subpath "<项目>/runtime/optimization/2026-10-09/M7/r4/sandbox"))(deny network*)' /usr/bin/true`：rc **71**；`sandbox-exec: sandbox_apply: Operation not permitted`。这是当前审查环境不能施加隔离的证据，不能推导launcher所有项目内路线均不可行。
2. `/usr/bin/pgrep -fl OctoSense.app/Contents/MacOS/octosense`：rc **3**；`sysmon request failed with error: sysmond service not found`、`pgrep: Cannot get process list`。已有窗口/进程状态 **UNKNOWN**；本轮没有创建窗口，没有盲杀他人进程。
3. `<项目>/runtime/native-build/OctoSense-App-Hub/target/release/hub check <精确冻结包> --allow-unsigned`：rc **0**；`octosense-repair 0.1.0-c — PASSED`，警告 `publisher-signature: unsigned: accountability rests on the hub alone`，grants storage、hosts空、16777216 bytes、agent none。此命令不是scan独立审阅或业务测试。
4. r2历史官方Store证据的实际路径是 `M7/review-r2/results/local-store-validation.json`（修正r3漏掉results的引用）。其install_staged、Store重建/may_run、篡改拒绝、恢复重试及删除私钥结果仍为相同摘要历史子项。未声称本轮重新安装/签名。历史signed check中未注册测试publisher曾被REFUSED，与本地隔离Store通过须分开。
5. 本轮没有生成/读取私钥；仅枚举 r2/catalog、review-r2 的 `*.key` 文件名，均为空。沿用 `r2/evidence/key-deletion.json` 和上述独立历史删除证据，不伪称本轮删除。离线签名已获授权，不需要NEEDS_ABRAM。
6. 16文件摘要全一致；INTEGRITY自哈希 **efb06e03bd9fb366a7fe76084cf98348e14907469e6ef216e74a9512eed0716d** / **3189字节**。PRIVACY **bff2bdd9587186e26b17dc3038e8b4eac87bc1d83d1610daa2f837ea765dffa8** / 1445；SOURCES **f516843f13c36bf6d83c948fb1f44d3c1e5b4fb4e7672d218fffba6dc5b1ed93** / 4323。工作区model_config SHA **55b41c8016c347ec0ba7a8b5e0942058eeef05a6f3c3f38b724a73bd183e0630**；冻结包model_config SHA **b36ca0561b89cf05de37f49eb5cbb2dc46ef9c9cc1879feee7bfff586de52741**，未混记。
7. 现存r4 driver SHA **2e80fe046c9e9fa90a0858cf7644041bb7ab58f7eb14f827b77fe3657a5bbf5e**；profile SHA **999ad2bddc8f3f74b4840cffdc323c0e254acc95f49719004640cf8c52df2c14**。三个作者run.json记录同值，来源一致性比r3改善；但cmd_actual均只有launcher路径，记录摘要不是已加载证明。probe-clean/probe-r3base的原始run.json在r4所列路径不存在，Metal结论只能记作者汇总声称。

独立mock方法：`python3 -B` 内用importlib读取现存driver，替换Path.mkdir/write_text/unlink、subprocess.run/Popen、threading.Thread、time.sleep、getpgid/killpg；用`--label independent-memory-only --wall-cap 0`，不加skip-launch。hub和pgrep返回值、子进程与异常都在内存模拟，run.json写入被收集到内存。本表是控制流证据，不是实际宿主结果。

|场景|独立注入|rc / 保存verdict|spawn / signal次数|结论|
|---|---|---|---|---|
|clean|check0、pre/post1、正常TERM|0 / true|1 / 1|基线成立，仅mock|
|check-fails|hub check7、其余正常|2 / false|1 / 1|能判FAIL，但准入失败仍启动，需早停|
|pre-pgrep-error|pre3、post1|0 / true|1 / 1|预检未知仍启动并PASS，安全前置未失败关闭|
|post-pgrep-error|pre1、post3|2 / false|1 / 1|能判FAIL，但reason写residue，未区分未知|
|launcher-101|子进程提前101|2 / false|1 / 0|r3误PASS反例已关闭|
|after-spawn-exception|sleep抛INJECTED_AFTER_SPAWN|2 / false|1 / 1|r3启动后异常不清理反例已改善|
|spawn-exception|Popen抛INJECTED_SPAWN_ERROR|异常外逸 / **true**|1尝试 / 0|finally保存假PASS，异常记录缺失|

作者 `m7_driver_injection.py:54` 全部带`--skip-launch`；:98–105仅check-fails、residue、clean-baseline三例，结果JSON也只有三例。没有执行其注释声称的Popen异常、101或启动后异常；`4/4`不成立。本轮独立补测不改作者脚本和结果。

## 缺陷及上一轮逐条闭合

### B-M7-01 — OPEN / 核心BLOCKED；安全与证据判定子项P1必修

- 文件与行：`r4/scripts/m7_launcher_probe.py:119–172,175–178,248–273`；`r4/scripts/launcher.sb:15–25`；`r4/scripts/m7_driver_injection.py:54,98–105`；`r4/CANDIDATE.json:11,38–46`；`M7_IMPLEMENTATION_r4.md:14,138–151,200–204`；`r4/launch-logs/SUMMARY.md:23–30`。
- 触发：复制当前README的r4启动命令；或向现存driver注入pre-pgrep rc3、hub check失败、Popen抛异常。真实启动本轮因预检阻塞未执行，控制流反例如上。
- 实际/预期：launcher在:164–172直接Popen，不使用:90定义的SANDBOX；环境变量重定向及mtime不变不能保证所有写入受限。hub失败或pre3仍spawn；pre3后post1返回PASS。Popen异常进入外层finally时check0、residue_clean=None、exception=None，写verdict_pass=true，再把异常抛给shell；日志消费者会读到假PASS。实际catalog只是sequence/apps/bundle_path/main文件SHA，没有官方签名catalog、Store安装/选择或launcher确认读取证据；日志仅见系统apps/news服务，没有维修任务权威结果。期望隔离预检成功才启动、准确加载已冻结digest、任何异常均失败关闭并清理自己的进程/窗口。
- 已关闭子项：101不再误PASS；启动后sleep异常已触发signal与失败记录；作者driver/profile SHA与三次日志匹配。部分改善不构成整个B01关闭。
- 根因：把hub check/文件路径登记当作候选运行绑定；只对hub子命令套sandbox，launcher绕过；预检结果未作启动门槛；outer finally默认成功，未覆盖Popen异常；自测全用skip-launch漏测。
- 影响：核心可复现桌面发布候选未成立，并可能越界写入、重复开窗或生成假成功审查材料。不能依据“3/3启动”放行。
- 具体改法：继续已证明可行的本地catalog/install_staged路线，不做公开publish。使用合法离线签名catalog并安装到全新隔离Store，记录安装/选择/加载的同一bundle摘要；确认launcher实际使用该Store或受支持的应用打开动作，不发明参数。所有宿主HOME/app-data/日志/缓存都在项目 `runtime/optimization/2026-10-09/`；先找到能施加写隔离并正常初始化GUI的环境/profile，失败立刻退出，禁止直接绕过。profile不允许冻结候选目录或项目外写入；/dev/null特殊设备规则不能称全目录无写入证明。hub失败及pre-pgrep非1停止，不启动；outer except记录错误、默认失败，只有所有必需阶段成功才PASS；Popen及其后由finally可靠TERM/KILL/wait自己的进程组，并确认窗口归零。区分准备子项与实际launch verdict，skip-launch不得写“launch PASS”。
- 验证方式：7个本轮反例加入真实启动分支的内存隔离自测；确认check失败/pre3 spawn=0、Popen异常保存false、spawn后异常必清理。然后在可运行相同隔离且可枚举窗口/进程的环境从干净合成数据操作冻结包正常/退回/重复/失败/业务重启，回读任务ID/版本/状态/action_id/附件；补同包真实账号会话、少量已授权MiniMax请求和当前截图/演示。旧包缺能力时重冻新的candidate_id并有针对性复验，禁止嫁接工作区结果。MiniMax遇402/欠费立即停并保留原文错误，此轮未出现。
- 解阻所需条件：技术上可施加项目内写隔离、枚举并清理自己的进程/窗口；有效本地Store→launcher同摘要加载；同候选核心业务与材料证据。均属现有授权范围，**NEEDS_ABRAM=no**。没有证明本地安装路径不可行：相同摘要已有官方Store独立PASS。

### A-M7-01 — PARTIAL / P2建议挂账

- 文件与行：`app/README.md:5,38–65,88–119`；`CONTEXT_M7.md:43–52`。
- 触发/实际：读取当前入口。:5仍声称B01已闭合、可隔离重现，:92仍称所有写入重定向；:38代码围栏到:65标题前未闭合，:104–121旧/tmp链仍在当前段之后且未标历史不可执行；:5的../../runtime链接从app/解析越出项目层级。
- 预期/根因/影响：当前入口须明确BLOCKED、实际允许的隔离方式、正确相对链接；历史命令误导及代码块替换不完整。未执行旧命令，不据此独立判FAIL。
- 具体改法：本模块入口写未安全运行，删“B01已闭合/所有写入已保证”；正确关闭代码围栏、把/tmp整块标历史不可用；staging链接用项目内正确相对路径。以渲染后标题/命令/链接目的地回读验证。

### A-M7-02 — 原媒体/不存在脚本问题CLOSED；来源/能力措辞P2建议挂账

- 文件与行：`release-materials/SOURCES.md:4,8–18,40–51`；`PRIVACY.md:11–15`；`r4/launch-logs/SUMMARY.md:23–25`。
- 实际：不存在脚本引用和本候选原创配乐断言已清除，未知源码commit及binary定位范围明确，原修复成立。仍把:51实际命令说成显式绑定bundle/app-data（driver未传）；SUMMARY:25以“Per r3 review”引用不存在于r3原文的“launcher设计层面不可达”；“媒体从未公开”也无本轮外部证据。
- 根因/影响：把实现意图、推断和作者限制当已观察事实；本地草案未公开，列P2。B01的实际安全/运行问题仍按P1处理，不让文案代替证据。
- 具体改法/验证：引用r3确实存在的原句“该次配置失败未证明所有路径不可行”；删无证据的不可达/绑定/从未公开断言，只写本候选未取得回执；以实际cmd_actual、Store加载结果及已核媒体范围回读，无需扩做媒体。

### A-M7-03 — CLOSED / 指纹及自指纹回归PASS

- 文件行：`release-materials/INTEGRITY.txt:10–16,33–59`；`r4/evidence/integrity-selfhash.txt:1–6`。
- 原触发：材料编辑后摘要失配、把自指纹写回自身。现在独立重算16项全匹配，外存自哈希正确，未在自身内容写摘要；包12+材料5=17与计数相符。
- 根因已消除：材料先定稿再冻结，self hash外存。无需业务改动。篡改/恢复历史作者证据仅保留，未重新篡改冻结材料。
- 若再改上述P2文案：材料需最后重冻并复核16项与外存摘要；不能沿用此次哈希PASS。

D-M7-01/02/03的原准入、冻结包和原编号口径问题保持CLOSED；本轮对同版本实际运行、scan及媒体不额外赠予PASS。不修、不改M0–M6独立结论。

## 相关既有用例逐项复核

以下逐项使用原ACCEPTANCE定义，64/64对应，无删改；额外L8-DV2保留。原64整项本轮50 BLOCKED / 14 NOT_RUN / 0 PASS，子项准入/指纹/历史Store PASS单列。历史后端/源码PASS与本轮原生状态不同，不覆盖原台账。P03含独立scan，不能用check退出0把整个原用例标PASS。

|编号|权威定义|本轮状态|证据与适用范围|
|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|BLOCKED|本轮精确冻结包hub check rc0、12文件摘要一致；真实启动/加载仍BLOCKED。|
|G0-B|真实可信身份、授权与独立会话|BLOCKED|5账号来源已授权；冻结包仍演示身份材料，不是当前M2 r4登录会话。未访问原账号、安装或明文凭据；可信读写权限未实操。|
|G0-C|唯一事实源、原子一致性、并发与恢复|BLOCKED|同摘要历史Store安装/恢复子项保留；业务事实源原子性、并发和崩溃恢复未实操。|
|G0-D|真实附件写入、回读、归属及失败恢复|BLOCKED|真实附件字节、归属、读回及失败恢复未执行；离线签名不能替代。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|BLOCKED|提醒恢复、去重与官方意图视图未实操；不称后台常驻。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|BLOCKED|冻结包不含Python/Web服务，manifest仅storage且无network hosts；旧写入口绕过、关闭网络和完整本地验收未实操。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|BLOCKED|冻结包不含Python/Web服务，manifest仅storage且无network hosts；旧写入口绕过、关闭网络和完整本地验收未实操。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|BLOCKED|相同摘要的r2官方install_staged/重建/may_run历史子项仍适用；r4合成catalog不证明launcher加载，任务操作/回读/重开未执行。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|BLOCKED|B-M7-01：不能安全启动并确认本候选已加载；本轮未执行原生操作、业务权威回读与失败/重启恢复。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|冻结包 enabled=false、provider_id/model_id 为空；与工作区已授权 MiniMax 配置不是同一字节。本轮真实请求0，不需新授权。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U06|进度、完工、验收不同；退回后历史与附件保留|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|BLOCKED|B-M7-01：当前真实桌面UI未运行；六张截图沿用旧B素材，未据此升级为PASS。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|无本候选2–3分钟演示及独立人员复述；旧B图不能替代。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|BLOCKED|同候选正常链、退回重做、失败/重复提交/业务重启均未实操。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|BLOCKED|目录/主源/宿主二进制可定位，历史本地Store子项保留；完整工具链来源及干净原生启动未验证。|
|P03|最终包准入check及实际scan审阅通过|BLOCKED|本轮hub check --allow-unsigned rc0 PASSED；实际独立scan审阅NOT_RUN，故完整原用例BLOCKED。纠正r3仅check即整项PASS的范围错误并保留历史。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|BLOCKED|来源/隐私/许可草案及材料哈希核对；同版本真实截图、演示和独立复述未取得。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|BLOCKED|16文件摘要及外存自哈希一致，A03关闭；本地运行核心B01未关闭，同版本交付整体BLOCKED。|
|P06|固定公开源码与Hub Issue实际递交回执|NOT_RUN|本候选无对应外部回执；本轮禁止发布/收录/赛事动作。历史B版回执不移植。|
|P07|维护者商店收录结果|NOT_RUN|本候选无对应外部回执；本轮禁止发布/收录/赛事动作。历史B版回执不移植。|
|P08|赛事正式提交入口回执|NOT_RUN|本候选无对应外部回执；本轮禁止发布/收录/赛事动作。历史B版回执不移植。|

## 判定

|状态维度|结论|范围|
|---|---|---|
|本地M7发布准备|**BLOCKED**|原B01核心与安全条件未闭合；准入/材料摘要子项PASS不代替运行|
|本地catalog/install_staged路线|历史子项PASS|相同摘要r2独立Store证明保留；r4合成catalog未证明launcher加载|
|外部发布/实际递交 P06|NOT_RUN|本候选无对应回执，禁止本轮执行；external_delivery原UNASSESSED保留|
|商店收录 P07|NOT_RUN|无维护者收录回执；不以递交或签名代替|
|赛事回执 P08|NOT_RUN|无本候选正式提交回执，历史B版不移植|

- 精确范围：仅M7 r4原缺陷复审与受影响回归，不是全项目或最新工作区业务放行。
- 必修/解阻：原B-M7-01；先安全隔离与候选加载，再补同候选核心原生链、权威读回、必要模型/UI证据。P2不构成单独拒收条件；不用完成比完美降低安全/核心证据门槛。
- 受影响先前回归：D01准入、D02/A03指纹、D03原64语义及driver安全已定向复核；M0–M6挂账保留，不声称重新通过。包若重冻需再跑受影响项。
- 门禁：仅GATES.json的M7 status/审查字段与历史更新，review_report指向本报告；保留上一轮来源。其他模块、作者candidate/implementation/evidence/staging/needs字段及external_delivery不改。原ACCEPTANCE.json未改。
- 下一模块：不允许、不执行，不给入口。M7为此序列末模块；本地通过也不自动授权公开发布。
- NEEDS_ABRAM=no：5账号、MiniMax、隔离离线签名已获授权；本地安装路线并非不可行；本轮真实模型0请求、无欠费错误，不需要新增授权。剩余技术与证据问题交实施方继续修，本审查不写业务代码。
- 审查起止摘要：同一冻结包12文件、4材料及外存自哈希一致；结束写入前后保留146文件快照，回读核验结果在本轮输出记录，发现变化不沿用PASS。

STATUS=BLOCKED
NEEDS_ABRAM=no
