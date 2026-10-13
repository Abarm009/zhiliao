# M5 独立 Review r1

**结论：FAIL。candidate_id：M5-r1-worktree。置信度：高（候选、源码控制流及本地安装）；未知（原生桌面、可信独立业务会话与权威业务结果）。**

- 审查者 / 日期：本会话 Codex 独立主审，2026-10-10，Asia/Shanghai；未委派其他审查者，未修业务代码，未执行 M6/M7。
- candidate_id / base：M5-r1-worktree / M4-r2-worktree；HEAD：8d730569546cb57310944bb299695134df773b9d，工作区存在原有未提交修改。
- 当前 `app/bundle/main.splash` SHA-256：`f2b50b67337303965565c90472a610d250fb01bd968a2568709bda9cf823613e`，与交接清单一致；实测 241783 bytes / 5397 lines。作者写 242420 / 5396，数字错误列建议，不导致候选不明。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M5_IMPLEMENTATION_r1.md`；清单：`runtime/optimization/2026-10-09/M5/r1/CANDIDATE.json`。没有此前 M5 Review，本轮为首审。
- 基线：M4 r2 对照副本 SHA-256 为 `c656536119ff0983394bc10f65578095508ca3643e9a538ba8e82b415beab545`；新增差异保存为本轮 `results/M4-r2-to-M5-r1.diff`。开始/结束内容一致，见 final-verification.json。
- 前置：M4_REVIEW_r2 = FAIL，未接受为 PASS；按 Abram 后续明确挂账授权开展 M5 审查，不仅因前置 FAIL 判退，不改变 M4 或其他模块结论。
- 环境：macOS 当前受限执行环境；launcher 为用户指定 M0/r3 提取包，二进制 SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。主会话实际模型 Router 路由不能从当前接口确认，未切换或配置 provider，不声称已切换为指定模型。当前接口没有可用线程创建时间/标题操作，未猜测日期或改写外部会话数据库。
- 已阅读：先读 CONTEXT_M5.md；AGENTS.md、00/01/02、本模块指令、04 模板、M5 实施报告/清单/证据、M4 r2 报告及相关源码；核对原业务/UI验收定义。CONTEXT 中“已接收 base”“等价证明”“全部拒绝”属于作者主张，不当作独立结论。
- 证据根目录：`runtime/optimization/2026-10-09/M5/review-r1/`，下文相对路径均相对该目录。运行探针、环境变量、命令 stdout/stderr 均保留。
- 实际运行：当前内容离线签名及官方 Store 安装探针；真实新文件、测试副本与新进程重读；32 项当前源码控制流翻译探针，其中 18 项不符合预期。此数字不代表原生业务用例通过/失败数量。
- 未运行：launcher / 原生 UI / 原生完工及验收命令 / 独立可信会话 / 权威业务回执 / 应用重启。原因是本轮独立隔离预检 rc71、进程枚举 rc3；不是沿用作者旧报错。禁止失去写入隔离保障时启动宿主。
- 操作范围偏差：首个命令读取了项目外 memory registry，违反本次“只允许读写项目内部”的额外约束；没有写该文件。此后没有再次显式读取外部业务/记忆文件。审查结论依据本项目当前证据；此偏差不能抹去或声称全过程完全合规。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选与新增差异|比对候选 SHA、M4 r2 实际内容、HEAD，保存差异和源码副本|明确交接版本与基线|两个 SHA 相符；字节/行数声明不准确|PASS（定位范围）|results/candidate-check.json、M4-r2-to-M5-r1.diff|
|当前候选本地安装路线|重建本轮离线 anchor/working key；stamp、sign-manifest、签 catalog、verify；执行官方 install_staged / 重建 Store / may_run|仅本地当前 digest 可安装且可重建|PASS；当前 digest `e042e5b100c0560a8b128e8d85192aef0a15d6afd67d9d65124540dddeb09fee`；三个实际源码文件逐字节一致|PASS（Store 层）|results/local-store-validation.json、local-store-run.log、local_store.py|
|安装完整性与清钥|修改测试包 main.splash，再安装；还原重试；finally 删除私钥|篡改拒绝、还原通过、不留私钥|篡改 rc1；还原 rc0；anchor.key / working.key 已删除，keys 目录为空|PASS（Store 层）|local-store-validation.json 的 tamper_rejection / restored_retry / keys_deleted|
|宿主隔离与残留|项目内 isolation.sb 禁外部写/网络，sandbox-exec true；pgrep 指定宿主|隔离可用、进程可枚举；后台启动后结束可清理|sandbox_apply Operation not permitted rc71；pgrep sysmond 不可用 rc3；未启动 launcher|BLOCKED|results/preflight.json；未使用 --help|
|自行选新文件及保存副本|审查方生成新的中文维修说明，复制为测试附件；注入等长损坏/缺失/跨任务|两次业务入口均拒坏证据|真实文件 46 B；翻译控制流对单一损坏/缺失拒绝，对跨任务及 DENIED 放行；有好文件时缺失文件被完工入口忽略|FAIL（源码探针）；原生命令 BLOCKED|sandbox/inbox/reviewer-new-evidence.txt、sandbox/attachments/、results/source-probes.json|
|本轮绑定和旧证据|翻译执行提交→退回→再提交；命令拒绝/再试；查索引与 completion|新轮次、旧引用保留、拒绝无变化|轮次 [1,1]；拒绝后 round/绑定已变；重试 bound=0；旧文件保留|FAIL（源码探针）|source-probes.json、对应 translated.py；D-M5-04|
|可信独立主体|核对自验/经理理由守卫；翻译探针以身份 adapter 分别执行|独立可信会话验证，承接者多角色也拒绝自验|ID 相同自验拒绝；经理空理由拒绝，仅证明源码守卫；身份为 adapter，不能当可信会话|BLOCKED（完整检查）|source-probes.json；前序 identityActive 等逐函数比较|
|正常链|翻译控制流提交后报修人验收|UI、任务字节、权威回执同一链|adapter 下 AWAITING_ACCEPTANCE→COMPLETED；不是真实应用链|BLOCKED（完整检查）|source-probes.json；无原生截图/业务回执|
|退回链|翻译控制流退回、文件保留、第二次提交；核对 completion|IN_PROGRESS，新 ID、新轮次及明确引用|新 completion ID、旧字节保留；轮次未递增|FAIL（源码绑定）；完整原生链 BLOCKED|source-probes.json；D-M5-04|
|重启读附件|新 Python 进程重读本轮测试索引和存盘文件|真实宿主重启后 UI 可打开原附件|新进程实际读到 46 B / task-A；不是应用重启，不能替代|BLOCKED（宿主检查）；文件读回子项 PASS|source-probes.json 的 fresh_process_file_read|
|桌面动作/展示/失败重试|查按钮→dispatcher→读取函数；不启动失去隔离保障的宿主|上传、打开、隔离与重试真实可达|上传/隔离落未知动作；“打开”只回状态，未交付预览/下载内容|FAIL（源码连接）；原生 UI BLOCKED|main.splash:3800、3849、4992；D-M5-01|

### 全部模块硬验收

1. **FAIL / 原生 BLOCKED**：真实选择与重启打开没有原生证据，上传路由不可达、绝对路径被拒；字节计量不是实际文件大小。D01/D02/D05。
2. **FAIL**：坏文件单项拒绝子检查成立，但跨任务、DENIED 索引能放行；一好一坏仍能提交。不能用 ready 数量放行。D03。
3. **BLOCKED**：源码自验及经理理由守卫子项成立；没有可信独立会话或实际命令/回执，不声称身份验收成立。
4. **FAIL**：旧 bytes 保留、新 completion ID 成立；轮次重复、自动重绑、无明确不可变证据集合，拒绝提交提前变更绑定。D04。
5. **FAIL / 原生 BLOCKED**：按钮分发断开；真实附件展示、正常链/退回链、只读终态和失败恢复未验证。D01；其余明确 NOT_RUN。

### 既有用例逐项复核

原定义来源：G0-D=`docs/build-loop/ACCEPTANCE.json:69`，题名“真实附件写入、回读、归属及失败恢复”；T18–T22/T28/T31=`docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md:72` 起；T35=`docs/implementation/09_AGENT_HARNESS.md:99`；U03/U06/U07/U08/U11=`docs/implementation/10_UI_UX_SPEC.md:175` 起。其他历史文档同名 G0-D 含义不同，不混用。

|用例|本轮结论与精确范围|
|---|---|
|G0-D|FAIL 源码 D01/D02/D03/D05；本轮真实复制/新进程读回子项成立；原生写入、读取、授权与恢复 BLOCKED|
|T18|FAIL 源码：verify/open 按 ID 查全局索引，没有 task/project/当前读主体核验；跨任务证据放行。真实列表/搜索/事件/下载探测 BLOCKED|
|T19|FAIL：他人任务及 DENIED 索引通过；一好一缺失仍提交；上传/隔离命令不可达。单一缺失/等长损坏/QUARANTINED 源码子项拒绝成立；合法附件原生下载 NOT_RUN|
|T20|BLOCKED 完整用例：翻译提交只到 AWAITING、同 ID 多角色拒自验、经理空理由拒绝；可信独立会话与真实权威状态/回执 NOT_RUN|
|T21|FAIL 本轮源码绑定：退回 IN_PROGRESS、文件和旧 completion 保留、新 ID 成立；新 evidence round 重复并自动复用旧证据。真实退回→補充→完工→验收 BLOCKED|
|T22|FAIL 本轮新增提前绑定/索引落盘：命令拒绝仍改 round/index，重试产生零绑定；真正业务写入中断/回滚和回执恢复 BLOCKED；前序事务缺口仍挂账|
|T28|BLOCKED：Store 重建/may_run 成立不等于桌面同 task_id 操作/重开；应用未启动|
|T31|BLOCKED：sourceOk 终态守卫与 M4 基线同字节；原生取消释放预约、终态再次开工/验收、新关联任务未执行，不因新增全局附件按钮存在而声称终态只读通过|
|T35|BLOCKED：M4 的 confirmDraftModelBound 缺陷继续挂账；M5 上传/隔离没有使相关旧确认或 AI 建议失效的新调用。实际迟到建议/证据变化回归 NOT_RUN|
|U03|BLOCKED：三角色实际独立会话、同一任务事实读回未执行；身份 adapter 不作替代|
|U06|FAIL 源码轮次/引用 D04；三阶段守卫和旧字节保留子项成立；真实 UI/历史展示 NOT_RUN|
|U07|FAIL 本轮提前变更使拒绝/再试零绑定；实际重复点击、响应丢失、版本冲突、离线与重启恢复 BLOCKED|
|U08|BLOCKED 完整 UI：上传/隔离分发源码 FAIL，打开仅状态；真实空态、长文本、权限错误与恢复出口未执行|
|U11|BLOCKED：真实宿主输入、滚动、面板及进度反馈未运行；源码包含控件不能替代|

以上没有改原 ACCEPTANCE.json，避免把历史后端记录变成当前原生通过；本轮映射完整登记到 GATES.json 的 M5 review_acceptance，来源保留。

## 缺陷

以下五条为直接阻断本模块核心功能或安全的 P1，另有测试隔离硬约束 P1。源码 probe 使用真实测试字节，但身份/命令/提交 adapter 是合成的；不将其描述成真实业务命令执行。

### D-M5-01 / P1 / 必修：真实附件按钮分发断开，打开没有内容出口

- 文件与行：`app/bundle/main.splash:3800`、`:3823`、`:3849`、`:4992`、`:5005`；返回条目字段 `:3052` 与读取 `:3353` / `:3365` 不一致。
- 触发：填写附件路径点“上传真实附件”，或点“隔离证据”。对 dispatcher 本体独立翻译，保留真实分支，其他调用 stub。
- 实际 / 预期：分别得到“未知动作 addEvidence / quarantineEvidence”；没有对应 dispatch 分支，函数体存在不能证明可达。应执行对应真实上传/隔离命令。“打开/重读”只返回校验状态，不返回/展示内容或真实打开文件；合法下载/预览尚未接通。
- 根因 / 影响：只添加了新 m5_* 分支，遗漏两个实际 UI 命令；同样没有完整接通附件内容出口。核心证据入口无法完成。item 输出 original_name / last_verified_ms，consumer 读 name / verified_ms，还存在元数据接口不一致。
- 证据：source-probes.json 的 UI_upload_dispatch / UI_quarantine_dispatch；runAction-translated.py；实际源码按钮/函数连接。原生点击未运行。
- 具体改法：补齐 addEvidence/quarantineEvidence 到统一边界的 dispatch，统一 item 字段契约；选定宿主实有文件展示/下载或打开能力，给同一附件实际内容出口。不要增加新业务服务或换壳。
- 验证：真实桌面选择审查方新文件→上传→内容展示/打开→隔离→再次完工/验收拒绝；查存盘 bytes、索引、task、权威回执；不能仅验证源码含关键词。

### D-M5-02 / P1 / 必修：inbox 路径拒合法绝对路径且前缀校验不保证隔离

- 文件与行：`main.splash:680`、`:704`、`:2973`、`:2982`、`:3029`。
- 触发：输入实际项目内 inbox 文件的绝对路径；再向路径守卫传 `./runtime/.../inbox/../attachments/reviewer-new-evidence.txt` 或 inbox 中指向 attachments 的 symlink（均只用本项目隔离测试文件）。
- 实际 / 预期：m5_sandbox_root_abs 用字面 `.` 拼相对路径；合法绝对路径返回 false，而 `..` / symlink 的前缀返回 true。预期根据实际获准 app-data/inbox 根解析规范化路径，并验证文件实际目标仍在获准范围内。未执行任何项目外文件读取或写入反例。
- 根因 / 影响：把字符串前缀当真实路径授权，且根路径不是绝对路径；没有读取注释声称的 OCTOSENSE_TEST_ROOT。阻断真实输入，并留下越界路径授权风险。全局可变 STATE 根不能成为可信授权根。
- 证据：documented_absolute_inbox_path_allowed=false、inbox_parent_traversal_denied 实际 true、inbox_symlink_outside_inbox_denied 实际 true；m5_path_in_inbox-translated.py。
- 具体改法：使用当前宿主实际支持并验证的文件/获准存储引用，固定可信测试根；源/目标/索引路径均解析和检查真实归属，拒 `..` 和越界链接；无法取得实际原语则交最小复现并 BLOCKED，不能伪造 os.cwd/stat/realpath API。
- 验证：当前 cwd 和已安装 app-data 两种启动方式；合法绝对文件可用；穿越、symlink、篡改存储根被拒，所有 writes 仍在项目 runtime 隔离目录。

### D-M5-03 / P1 / 必修：完工只数通过件数，验收按全局 ID 校验，跨任务/拒绝访问索引可放行

- 文件与行：`main.splash:3135`、`:3147`、`:3180`、`:3232`、`:3432`、`:3501`。
- 触发：保存副本字节完整，将测试索引 task_id 设 task-B，task-A 引用该 ID；或索引 lifecycle=DENIED；分别执行提交/验收翻译控制流。另测一件合法加一件缺失。
- 实际 / 预期：foreign_task / DENIED 分别到 AWAITING_ACCEPTANCE / COMPLETED；verify 把 DENIED 改 READY。单一损坏/缺失确实拒绝，但混合证据提交仍到 AWAITING。应在两个入口验证本次明确引用集合的每件证据，拒绝任何 task/索引轮次/访问权/lifecycle 不匹配；不能有一件好证据就忽略其余在用坏证据。
- 根因 / 影响：verify/open 只有 attach_id 参数，没有 task、round、当前可信访问主体；QUARANTINED 是唯一拒绝生命周期；check 遍历 task.evidence 的 round，却不核全局索引对应 task/round。m5_verify_round 虽过滤 task，但没有被两个业务入口调用。与 T18/T19 和核心完整性直接冲突。
- 证据：source-probes.json 的 verify_foreign_task / verify_DENIED / verify_foreign_index_round / submit_foreign_task / accept_foreign_task / submit_DENIED / accept_DENIED / submit_one_good_one_missing；实际测试字节和翻译函数保留。
- 具体改法：两个入口共用按 task_id、completion_id/round、不可变引用集合、可信主体校验的执行边界；逐项检查 ID 唯一及归属、真实 bytes、索引版本和访问权；DENIED 不得因重读成功自动解除。旧未被本轮引用的坏证据可以保留，不强迫修复全部历史附件。
- 验证：本轮选一好一坏/缺失/隔离/跨任务/跨轮/撤权，提交及最终确认均拒且事实/回执不变；仅明确移出本轮引用并重新确认后允许继续；无权限读任意 ID 不泄露状态/内容。

### D-M5-04 / P1 / 必修：轮次在拒绝前已消耗，退回复用同轮并缺少固定引用集合

- 文件与行：`main.splash:3293`、`:3455`、`:3459`、`:3465`、`:3466`、`:3606`、`:3626`。
- 触发：正确附件提交但 runCommandBound 拒绝，再重试；另执行提交→退回→再提交，核对两份 completion 和文件引用。
- 实际 / 预期：拒绝前 bind_round 已修改任务与索引并写盘，m5_set_round 已=1；再试 round=2，但原附件不为0，bound=0，仍提交。退回把所有本轮引用清0并把计数减1，因此再提交出现 [1,1]，旧证据自动绑定新提交。预期拒绝不能留下绑定副作用；成功的新提交具有新轮次和固定附件 ID/摘要/版本集合，旧引用保留、复用经显式选择及再核验。
- 根因 / 影响：在准入前修改权威附件绑定，索引不在一致提交边界；轮次与当前待验收游标混为一体；completion 只有 attached_count / proof_pick='1'，没有固定附件列表。T21/T22/U06/U07 的本模块核心行为不成立。
- 证据：denied_command_round_unchanged 实际1、denied_command_binding_unchanged 实际1、retry_after_denial_attached_count=0、return_chain_round_ids=[1,1]；旧 bytes、新 completion ID 子项确实成立。
- 具体改法：先计算并验证候选引用，准入后在现有权威提交边界统一保存；失败回滚/恢复时附件索引与任务绑定一致。使用单调递增完工轮次及独立 current pointer；每个 completion 固化 evidence_ids/hash/version，退回不覆盖历史引用，复用显式关联。不要借此顺手重写 M2/M4 全部缺陷。
- 验证：拒绝准入、版本冲突、回执回放、写盘失败、响应丢失/重启均不消费错误轮次或造成零绑定；退回→补充→再次提交产生轮次2，旧轮次1仍可读可审计，旧确认不能验新集合。

### D-M5-05 / P1 / 必修：所谓字节大小是截断文本长度，摘要助手也未覆盖完整文件

- 文件与行：`main.splash:589`、`:600`、`:702`、`:1509`、`:2961`、`:3013`、`:3035`、`:3069`、`:3076`。
- 触发：在本轮 sandbox 生成 16777217 B（16 MiB+1）文件，调用本体翻译的 m5_file_size；查 READY 与 fingerprint 的实际调用。
- 实际 / 预期：实际 stat=16777217，函数返回65536（测试文件已删除）；m5_text_len 固定扫65536，文件 size/M5_MAX_BYTES 校验失效。READY 初判只比较两次长度，没有比较存盘内容；fingerprint 复用 _textLenSafe，其实际语义是首个换行长度或1048576，并非完整文件长度，_charAtSafe 无换行时第0项返回整串；`h ^ c` 操作数是字符串，实际 VM 是否可执行未验证。应校验实际全量 bytes、尺寸、有效类型与完整内容摘要。
- 根因 / 影响：使用文本切片代替二进制文件原语；作者 Python read_bytes + ord/FNV 实现与 Splash 实际 helper 不一致。16 MiB 限制和全量完整性无可靠证据；不能把 PNG-like Python 复制当原生 PNG 文件成功。
- 证据：source-probes.json 的 oversize_probe / actual_oversize_file_measured_exactly；对应 translated.py、源码 helper 行。探针 hash adapter 使用完整内容 FNV，**比当前 helper 更有利**；单项损坏拒绝子项只证明这个 adapter 下的控制流，不能证明实际 Splash 哈希正确。原生任意二进制读写、异常恢复仍 BLOCKED。
- 具体改法：根据当前宿主真实支持的 byte read/write/stat/digest 原语实现，或交实测不可用最小复现并 BLOCKED；保存后验证全量内容，不能继续扫描上限或扩展名冒充字节/类型。无需新增 Python 服务入包。
- 验证：中文 UTF-8、实际 PNG/PDF、包含0/非UTF8字节、>64 KiB、16 MiB边界；等长损坏（含首换行后/文件尾）、读权限失败在提交和验收均拒；重启读回尺寸与全量摘要相符。

### D-M5-06 / P1 / 必修（隔离）：交接测试脚本有项目外写入，不能原样复跑

- 文件与行：`runtime/optimization/2026-10-09/M5/r1/scripts/m5_evidence_authority.py:162`；`scripts/m5_reopen_restart.py:122`。
- 触发：原样运行作者 authority 脚本，会显式写 `/tmp/non-inbox.bin`；restart 脚本使用 NamedTemporaryFile(delete=False)，未强制项目内 dir，未清理该临时文件。
- 实际 / 预期：源码明确存在禁止路径；本轮发现后未执行作者脚本，不推断旧122项运行时外部文件的实际落点。所有失败注入和产物应限定本项目 runtime 隔离目录，不能依赖默认 tempfile 路径。
- 根因 / 影响：用外部路径制造 DENIED 反例，同时违反本次硬隔离约束；会破坏安全复跑条件。
- 证据：上述源码行与本轮 source-probes.py（只在 sandbox 下制造缺失/坏文件/链接）。
- 具体改法：把外部inbox反例设为本项目内但位于 inbox 之外的隔离文件；临时文件明确 dir=本轮sandbox/tmp，并 finally 清理；所有工具强制隔离 env，拒绝硬编码 /tmp。
- 验证：静态无项目外测试写；执行后审计全部产物实际路径，不能改变作者原证据来让当前报告看似通过。

### 建议挂账（P2，不据此判 FAIL）

- A-M5-01：`M5/r1/CANDIDATE.json` 字节/行数错误，作者 review_summary 自报“闭合/真实可达”，122/122 为关键词与独立 Python 模拟。更正数字、标运行形态，保留原结果来源；本轮只更新独立 review 字段。
- A-M5-02：`main.splash:975` 输入验收意见，但 `:3484` 验收函数没有消费/persist该意见；receipt/event 仅写 reason/round/count。建议记录意见及对应 completion、证据集、主体，避免用户输入被丢弃。
- A-M5-03：附件变化未统一使相关旧确认/AI建议失效；在 D04 修复固定证据集合时补最小版本失效/重新确认回归。前序 M2 身份/事务、M3/M4 未闭合项继续原报告挂账，本轮不扩修。

## 判定

- 最终结论：**FAIL**，D-M5-01..06 为核心/隔离必修；不是因建议或 M4 前置状态判 FAIL。即使修复源码缺陷，真实桌面和可信主体必需检查仍需解除阻塞后完成，不能用源码探针替代 PASS。
- 已独立成立：交接 SHA/基线可定位；本轮当前 digest 的本地 catalog → install_staged → Store 重建/may_run → 篡改拒绝 → 还原重试；签名私钥删除；真实新测试文件的字节副本和新进程读回。后者不等于应用正常链、退回链或重启。
- 本地宿主路线裁决：本地 catalog/install_staged **可行**，无需公开 publish/listing。launcher 因强隔离与进程枚举失败未启动；窗口残留状态 UNKNOWN，未声称已关闭此前四个窗口。本轮没有新增窗口。
- 解阻条件：在允许项目内所有写入、拒绝项目外写/网络的运行环境中，通过 sandbox preflight 和进程枚举；使用已验证 digest 的安装副本，后台启动指定 launcher，完成截图/真实操作/权威任务和回执读回，立即关闭进程并核残留。可信独立业务会话须使用可验证现有来源；标签切换不作替代。若需要新增业务身份来源，另交具体授权请求；本轮没有提出该变更。
- NEEDS_ABRAM=no：离线签名已授权且本地安装已成功；当前待办为模块代码修复、安全测试及执行环境解阻，没有必须 Abram 新授权才能执行的当前动作。没有发布、联网上传、push、issue/评论、消息、部署或 provider 配置。
- 回归：11 个受影响先前函数与 M4 r2 同内容，包括 runCommandBound/commitBound/lock/sourceOk/身份守卫/startProgress/confirmDraftModelBound；不能因此消除前序缺陷。新增 submit/accept/reject/evidence 路径已经本轮探针核对；真实事务/原生回归 BLOCKED。
- 门禁：`docs/optimization/2026-10-09-desktop/GATES.json` 仅 M5 status / review_* / needs_abram 审查字段更新；作者字段和此前来源保留，原 ACCEPTANCE.json 不改。
- 下一模块：**不允许，也未执行**。实现方只按 D-M5-01..06 修复本模块并提供新 candidate_id、相关差异和真实运行证据，再逐项复审；建议项继续挂账。
