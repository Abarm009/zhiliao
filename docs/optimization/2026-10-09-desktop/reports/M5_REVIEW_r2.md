# M5 独立 Review r2

**结论：FAIL。候选：M5-r2-worktree。置信度：高（候选、源码控制流、离线 Store 安装）；未知（原生 UI、可信独立业务会话、权威业务回执）。**

- 审查者 / 日期：本会话 Codex 唯一独立主审，2026-10-10，Asia/Shanghai；未委派其他审查者。只做上一轮 D-M5-01～06 的闭合核对与受影响回归，不修业务代码、不执行 M6/M7。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M5_IMPLEMENTATION_r2.md`；候选清单：`runtime/optimization/2026-10-09/M5/r2/CANDIDATE.json`。r2 报告明确按 r1 缺陷修复、交接此 candidate_id；GATES 的候选和报告也一致，不依据文件时间挑版本。
- 被审 HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作区原有未提交及未跟踪改动保留。当前 `app/bundle/main.splash` SHA-256：`20bf8800b3b6542f806f6e59a7a360a0df85cb2021fdd6321a65504b6ccfb113`，251677 B，Python splitlines=5585；SHA 与 r2 清单一致。
- 基线：M5-r1-worktree SHA-256=`f2b50b67337303965565c90472a610d250fb01bd968a2568709bda9cf823613e`，从 r1 已安装 bundle 找回，与候选 before_sha256 相符。r1 的 `results/source-snapshot.splash` 已被后续重跑覆盖为 r2，不能作 r1 基线。本轮不改旧记录，另存实际基线与差异。
- 前置：M4_REVIEW_r2=FAIL，未有 PASS 候选；按 Abram 本次明确挂账授权继续 M5 复审，不仅因前置 FAIL 判退，不修改 M4 或其他模块状态。
- 阅读范围：先读项目 AGENTS 与 CONTEXT_M5；核对 M5 r1 Review、r2 报告/清单/证据、04 模板、00/01/02 和本模块硬验收；代码只检查上一轮缺陷涉及的路径、附件、提交/验收/退回、三个隔离脚本及相关旧函数。既有用例沿用原定义，不混用历史同名 G0-D。
- 模型 / 对话元数据：当前接口不能确认或切换主会话实际 Router 路由，不能声称已切换为指定模型；没有可用 createdAt/改标题接口，未猜日期或写外部会话数据库。未读取项目外技能/记忆文件，遵守本次项目范围约束。
- 宿主：用户指定 M0/r3 提取的 OctoSense.app，二进制 SHA-256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。本轮 launcher **未启动**，未用 `--help`，未新增桌面窗口；既有窗口残留状态 UNKNOWN。
- 证据根：`runtime/optimization/2026-10-09/M5/review-r2/`；下文相对证据路径均相对此目录。所有新增脚本、文件、HOME、app-data、tmp、缓存、日志及离线签名密钥均在此隔离目录。
- 实际运行：重新隔离预检；当前源码 32 项翻译控制流探针；6 项针对剩余缺口的控制流反例与1项哈希覆盖源码推导；新的中文文件与存盘副本及新进程读回；作者脚本另复制到本轮隔离目录复跑；当前 digest 离线签名、catalog 校验、官方 install_staged、Store 重建/may_run、包篡改拒绝及还原重试。
- 证据边界：翻译探针的 fs/hash/identity/command/commit/clock 为 adapter，不能称为 Splash VM、真实业务身份、实际业务命令、权威任务事实或回执。完整 hash adapter 比当前源码 helper 更有利；32 项中31项符合预期仅说明这些控制流子项，不能证明实际文件摘要或桌面链路。
- 未运行：真实桌面选择/展示/中文输入/点击、正常链与退回链、实际命令失败恢复、可信独立会话、权威回执、应用重启与终态只读。新的隔离预检 rc71、进程枚举 rc3 阻止安全启动，不沿用作者报错代替本轮检查。
- 开始/结束快照一致性与只改 M5 审查字段的核对见 `results/final-verification.json`。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选、基线与新增差异|核 SHA/HEAD，从已安装 r1 包找回基线，保存 r1→r2 diff|交接版本可定位|r2 SHA、r1 before SHA 都匹配；旧 review snapshot 被覆盖已识别|PASS（定位范围）|results/candidate-check.json、base-M5-r1.splash、M5-r1-to-M5-r2.diff|
|当前候选本地安装|新建隔离 anchor/working keys，stamp/sign-manifest/catalog verify，实际 install_staged，重建 Store/may_run|当前 digest 可离线安装并重建|digest=`99f179049229d31a65da8d8b7146b72a30e3c2892f572aa42e36b961d7facc02`；安装的 main/model_config/identities 与当前源逐字节一致|PASS（Store 层）|results/local-store-validation.json、local-store-venv-run.log、local_store.py|
|篡改拒绝及清钥|改测试包内容再装，还原后重试；finally 删除私钥|篡改拒绝、还原成功、无私钥留存|篡改 rc1、还原 rc0；anchor.key/working.key 删除，剩余列表为空|PASS（Store 层）|local-store-validation.json：tamper_rejection/restored_retry/keys_deleted/remaining_key_files|
|安全启动条件|项目内写白名单、禁网络 sandbox-exec true；枚举指定 launcher 进程|可隔离启动并清理窗口|本轮 rc71 `sandbox_apply: Operation not permitted`；pgrep rc3，无法枚举；未启动|BLOCKED|results/preflight.json、isolation.sb|
|新文件及损坏/缺失/跨任务|新建55 B中文文件，保存测试副本；分别注入等长损坏、缺失、task-B 归属，执行提交/验收翻译本体|两个入口拒绝，事实不推进|adapter 下均拒绝；DENIED 亦拒绝；不是原生命令结果|PASS（源码子项）；原生 BLOCKED|sandbox/inbox/reviewer-new-evidence.txt、results/source-probes.json|
|完整本轮集合|正常翻译提交两件，移除任务列表中一件并删其保存副本，再验收|按 completion 原引用两件核验并拒绝|仍 COMPLETED；只核当前列表剩余一件|FAIL（源码）|results/followup-probes.json：missing_member_from_fixed_completion_set_rejected|
|固定摘要与旧引用|提交后修改同 ID 文件及可变索引摘要；另跑提交→退回→不选择旧证据再提交|固定引用可检测变化；复用须显式选择|更换同 ID 内容后仍 COMPLETED；旧证据自动再绑新轮|FAIL（源码）|followup-probes.json：same_id_changed_digest_after_submit_rejected、old_evidence_reuse_requires_explicit_selection|
|轮次与失败恢复|拒绝 runCommandBound 后重试；提交通过但 commitSucceeded=false|拒绝不消费轮次；提交失败不留已提交附件绑定|准入拒绝轮次/绑定不变已修；commit失败时 round/index binding=1仍保留|部分修复；FAIL（M5 索引源码）|source-probes.json、followup-probes.json；D-M5-04|
|可信独立验收|多角色同 ID自验、经理空理由守卫；核实际会话证据|独立可信会话、无自验、代验需理由|adapter 守卫子项符合预期；没有可信会话运行证明|BLOCKED（完整检查）|source-probes.json；r2 报告明确未提供|
|正常/退回/重启链|翻译提交/验收、退回/再提交；新进程读索引/字节|界面、字节、权威状态和回执一致|翻译正常链、退回状态、新 ID与轮次[1,2]成立；新进程实读55 B；并非真实应用链或应用重启|BLOCKED（完整链）；D04反例 FAIL|source-probes.json、fresh_process_file_read|
|打开及失败重试|核 dispatcher→函数→内容出口|合法附件可看/打开/下载|上传/隔离分发已接；打开只写 lifecycle/reason，未交付文件内容|FAIL（源码）；原生 BLOCKED|main.splash:4037、3235；D-M5-01|
|项目内脚本复跑|静态核移除外部写；复制同内容脚本到本轮隔离目录运行|全部产物在项目内，历史证据不覆盖|8脚本/122断言通过，当前三个问题脚本未再写 /tmp/default tempfile|PASS（D06隔离及作者断言）；非应用验收|author-copy/scripts、results/author-copy-summary.json、author-copy-run.log|
|受影响前序回归|比较11个旧函数与 M4 r2基线|既有实现未被本轮改写|11项同内容；不是前序真实运行通过|PASS（内容比较）；运行 BLOCKED|source-probes.json：affected_predecessor_functions|

运行异常也保留：第一次系统 python 缺 cryptography（`local_store.py` 导入即失败，没有生成私钥），改用项目现有 `backend/.venv/bin/python` 后离线 Store 检查通过；首轮附加探针对源码多行字符串的翻译器报 SyntaxError，随后仅将 hash 循环长度改为明确标识的源码推导。两次失败日志保留，不作为业务运行失败，也不伪造原生执行。

### 上一轮缺陷闭合核对

|编号|r2 独立结论|已成立子项|剩余必修/阻塞|
|---|---|---|---|
|D-M5-01|未闭合 / P1|上传/隔离分发、item字段接口已修|打开/展示/下载内容出口没有接通；原生操作 BLOCKED|
|D-M5-02|未闭合 / P1（隔离）|字面 `..` 拒绝、合法绝对路径子例成立|任意 `/inbox/` 路径被接受、symlink越界仍放行；可信根/真实目标校验未成立|
|D-M5-03|部分修复，未闭合 / P1|跨任务、DENIED、索引轮次、一好一缺失提交的原反例已拒|验收仍未逐项检查 completion 固定引用集合，成员消失被跳过|
|D-M5-04|部分修复，未闭合 / P1|准入拒绝不增轮次、不改绑定；退回后新轮次[1,2]、新 completion ID、旧字节保留；新增 evidence_ids|只固定ID未固定摘要/版本，验收未消费集合；旧证据自动复用；提交失败M5索引/轮次未恢复|
|D-M5-05|未闭合 / P1|adapter 下16 MiB+1准确测量，旧65536上限问题子项已修|全量指纹助手仍止于首换行，保存初判仍仅比较大小；二进制原语/VM语义未实测|
|D-M5-06|已闭合（本条隔离范围）|三个脚本外部写已移除；本轮副本实际复跑、产物落点项目内|原生文件能力仍未验，但不是本条修复责任；不重新打开本条|

### 全部硬验收

1. **FAIL / 原生 BLOCKED**：内容出口 D01、路径 D02、字节 D05仍未闭合；新进程读文件不等于宿主选择/重启打开。
2. **FAIL / 原生 BLOCKED**：跨任务等原子反例修复成立，但固定集合成员丢失可漏检（D03），全量内容和绑定仍不可靠（D04/D05）。可信撤权会话未运行。
3. **BLOCKED**：adapter 下仅到待验收、自验与经理理由守卫成立；未从可信独立业务会话核权威事实与回执。
4. **FAIL / 原生 BLOCKED**：新轮次、新ID、旧字节保留子项成立；显式复用、不可变内容引用及失败恢复仍缺（D04）。
5. **FAIL / 原生 BLOCKED**：附件可视内容出口仍缺（D01）；真实正常/退回/重启/终态只读与失败重试未运行。

### 既有用例逐项复核

定义：G0-D=`docs/build-loop/ACCEPTANCE.json:69`（真实附件写入、回读、归属及失败恢复）；T18–T22/T28/T31=`docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md:72` 起；T35=`docs/implementation/09_AGENT_HARNESS.md:99`；U03/U06/U07/U08/U11=`docs/implementation/10_UI_UX_SPEC.md:175` 起。此表为 r1 缺陷涉及项与受影响回归，没有另做无关扩审。

|用例|结论与精确范围|
|---|---|
|G0-D|FAIL D01/D02/D03/D04/D05剩余源码缺口；真实副本与新进程读回子项成立；原生运行 BLOCKED|
|T18|跨任务ID核验已补且源码子项拒绝；可信当前访问主体、列表/搜索/事件/附件数据探测完整用例 BLOCKED；M2身份挂账不扩修|
|T19|FAIL：单项坏/缺失/他人任务/DENIED源码子项拒绝，但固定集合漏件、全量摘要、实际合法下载未闭合；原生 BLOCKED|
|T20|BLOCKED：翻译正常提交只到待验收、多角色同ID禁止自验、经理空理由拒绝成立；可信独立会话/权威状态回执未运行|
|T21|FAIL D04：退回 IN_PROGRESS、旧字节/旧completion、新ID/轮次递增成立；未显式选择即旧证据自动复用；真实补充/再次验收 BLOCKED|
|T22|FAIL M5索引/轮次在 commit 失败后未恢复；真正写入异常/回执一致恢复 BLOCKED，前序事务缺口继续挂账|
|T28|BLOCKED：本轮 Store重建/may_run PASS不等于桌面同task_id操作/重开|
|T31|BLOCKED：sourceOk与基线同内容；取消、终态再次操作、新关联任务原生未运行|
|T35|BLOCKED：confirmDraftModelBound与基线同内容；前序旧确认/AI建议失效继续挂账，实际迟到建议/证据变化回归未运行|
|U03|BLOCKED：独立会话、三角色权威事实一致未证明；adapter不替代|
|U06|FAIL D04引用复用/内容绑定；轮次与历史字节源码子项已修；实际UI历史未运行|
|U07|FAIL M5索引/绑定恢复 D04；准入拒绝重试子项已修；真实重复点击/响应丢失/离线/重启 BLOCKED|
|U08|FAIL D01附件内容出口；可达分发源码子项已修；实际失败、权限、过期等出口 BLOCKED|
|U11|BLOCKED：宿主滚动、输入、面板切换和真实进度未运行|

## 缺陷

只保留阻断 M5 核心或隔离硬约束的 P1，沿用原编号。下列“实际”明确指当前源码/翻译adapter；没有原生运行时不编造UI结果。

### D-M5-01 / P1 / 必修：打开仍没有真实内容出口（分发子项已修）

- 文件与行：`app/bundle/main.splash:3235`、`:3278`、`:4037`；分发修复位置 `:4010`、`:4011`。
- 触发：上传合法附件后执行“打开/重读”；沿函数查看实际返回与UI更新。
- 实际 / 预期：open读文件仅用于校验，返回 `{ok, reason, lifecycle}`，命令仅更新状态文本；没有内容/预览引用/下载或宿主打开调用。预期独立验收者能查看该保存附件的实际内容。原生点击 BLOCKED。
- 根因 / 影响：把“再次校验”当作“打开”；即使证据存在，业务人员无法检查其维修事实，T19合法下载/硬验收1、5未成立。
- 证据：`results/source-snapshot.splash`上述函数；source-probes UI dispatch无错只能关闭分发子项。
- 具体改法：在当前宿主实有能力中接出同一附件内容；可采用经验证的文本展示或文件预览/打开能力。展示必须经过任务与当前可信主体授权，不新增独立壳或包外服务。无法实现实有原语则明确最小复现/BLOCKED。
- 验证：独立新文件上传后实际展示其内容，校对存盘字节；重启再打开；缺失/隔离/无权时不给内容且能恢复。不能以状态“已重新打开”作证明。

### D-M5-02 / P1 / 必修（隔离）：绝对路径修复扩大为任意 inbox，链接越界仍未拒

- 文件与行：`main.splash:704`、`:3009`、`:3025`、`:3048`、`:3077`；STATE根默认 `:680`。
- 触发：用本轮 `sandbox/unapproved/inbox/foreign.txt`（与获准 inbox不同）传入路径守卫；另用获准inbox中的symlink指向同项目sandbox/attachments副本。均不读项目外文件。
- 实际 / 预期：两个路径都返回 true；预期仅获准根中的真实目标允许。合法绝对路径及字面 `..` 拒绝已修，但不能由任意目录名/inbox取得授权。
- 根因 / 影响：相对根分支只找任意 `/inbox` 段，完全不核此前实际目录；依然是字面前缀和可变STATE根，没有真实目标授权。链接真实路径硬约束不能降为建议；可能授权未获准文件读入。
- 证据：source-probes 的 inbox_symlink_outside_inbox_denied实际true；followup-probes 的 unapproved_inbox_named_directory_denied实际true；新反例实际文件只在本项目隔离目录。
- 具体改法：使用实测可信固定根/获准文件引用，校验源/保存目标/索引实际路径；删掉“任意/inbox”兜底；拒绝越界链接与篡改根。没有realpath/stat时可选择平台原生获准引用或已验证的无链接隔离机制，交最小复现与 BLOCKED；不能发明API或把限制认定已修。
- 验证：合法绝对路径成功；另一inbox、同项目越界链接、穿越和篡改根均拒；不同cwd及安装app-data启动仍落本项目隔离目录。原生安全条件满足前不启动launcher。

### D-M5-03 / P1 / 必修：验收仍可跳过 completion 固定集合中丢失的成员

- 文件与行：`main.splash:3368`、`:3373`、`:3376`、`:3646`、`:3679`。
- 触发：正常翻译提交两件，completion.evidence_ids保存两个ID；从任务evidence列表移走第二件并删除其保存副本，再验收。这是隔离反例，不是正常链手工造状态。
- 实际 / 预期：actual=COMPLETED；期望仍AWAITING_ACCEPTANCE并指明原引用附件丢失。将原引用项改为其他轮次也会被过滤，而非作为缺失成员核验。
- 根因 / 影响：虽然r2存了 evidence_ids，accept仍只遍历当前task.evidence中round匹配的条目；没有读last.evidence_ids。原集合可被缩小后仅凭剩余件数通过，违反完整证据验收。跨任务、DENIED、混合提交守卫的已修子项不被否定。
- 证据：followup-probes.json 的 original_completion_ids与 missing_member_from_fixed_completion_set_rejected；相关翻译函数。
- 具体改法：验收遍历待验 completion不可变引用集合，逐件核ID唯一、task/round、摘要/版本、访问权、真实bytes；不存在的成员直接拒。task和全局索引必须对应原集合，不能用当前筛选总数代替。
- 验证：两件提交后移走/缺失/换轮/隔离/跨任务其中一件，全部拒且任务/回执不推进；只明确更改本轮集合并重新完工确认后才能验收。

### D-M5-04 / P1 / 必修：ID列表未绑定内容，旧证据自动复用，提交失败索引仍留绑定

- 文件与行：`main.splash:3433`、`:3469`、`:3640`、`:3646`、`:3649`、`:3679`、`:3793`、`:3803`、`:3809`。
- 触发：A）提交后同ID文件与可变登记摘要一起更改，验收；B）提交→退回→没有新证据/显式选择即再提交；C）准入通过但commitSucceeded=false。
- 实际 / 预期：A仍COMPLETED，completion只有ID无法比对原内容；B自动将原ID再绑轮次2；Cround及索引evidence_round仍=1。期望固定ID+内容摘要/尺寸/版本，复用旧证据须新轮明确选择并核验，失败不留下已提交轮次绑定。
- 根因 / 影响：固定集合不含内容版本；退回将全部本轮条目清0，下次遍历所有条目自动收录；M5索引在commit前单独fs.write，失败分支只return。单调轮次及准入拒绝修复成立，但不足以完成可审计退回链/恢复。
- 证据：followup-probes.json 的 same_id_changed_digest_after_submit_rejected、return_ids、old_evidence_reuse_requires_explicit_selection、failed_commit_*；source-probes 原轮次[1,2]与准入拒绝修复子项。
- 具体改法：completion固化引用ID/全量摘要/尺寸/版本，由最终验收实际消费；历史绑定保留，用单独候选选择表达新轮，不将旧证据自动清0复用；M5附件绑定/索引纳入现有提交恢复协议，失败恢复本模块写入。前序M2通用事务缺口继续挂账，不要求顺手重写M2。
- 验证：正常退回→显式补充/复用→轮次2成立且轮次1引用仍可审计；内容/索引换版使旧确认无效；准入拒绝、commit失败/索引写失败及重启后不留错轮或半绑定，回执与附件集合一致。

### D-M5-05 / P1 / 必修：扩展长度扫描没有修复全文件指纹和保存初判

- 文件与行：`main.splash:589`、`:600`、`:1509`、`:3112`、`:3119`、`:3126`、`:3151`、`:3158`、`:3330`。
- 触发：两份相同首行、等长不同尾部文件；查实际fingerprint调用；保存读回字节相同长度但内容不同；原生测试应另含UTF-8、PNG/PDF、0及非UTF8字节。
- 实际 / 预期：_fnv1a_hash继续用_textLenSafe；有换行只循环到首个换行。本轮ASCII例全长29，循环界16，不同尾部消费相同前缀。READY初判仍仅比源/存盘size，不比内容。m5_byte_len确实移除了64KiB截断子项，但未证明fs.read字符串就是完整二进制bytes。
- 根因 / 影响：修复只增扫描上限；借用的文本助手与实际全文件摘要不等价。原生 `h ^ c` 的字符串数值语义未知，未假定VM会出现Python错误；无论该语义如何，首行后的字节没有进入循环，损坏检测核心没有成立。
- 证据：followup-probes hash_coverage（明确源码推导）；实际helper源码；source-probes的16MiB+1仅使用latin1 bytes adapter，不能证明Splash二进制原语。
- 具体改法：采用目标宿主实测全量byte读取/写入/长度/内容指纹原语或可靠组合，保存读回后比较全量内容再READY；hash遍历真实全内容并核实际数值转换。M5自身不要继续复用首行助手；不因此重写M3。原语不可用则提供最小复现/BLOCKED。
- 验证：真实中文UTF-8、可打开PNG/PDF、0/非UTF8、>64KiB及16MiB边界；等长首行后/尾部损坏在提交与验收均拒，保存初判及重启摘要与独立全量字节一致。

### 建议挂账（P2，不据此判 FAIL）

- A-M5-01延续：数字与来源修正。r2报告行数称5402，应修正；清单5584与实际换行符计数一致，本轮splitlines5585属于不同计数口径。实际SHA已明确，不阻断候选。r2声明31/32来自已覆盖r1 evidence；r1 snapshot也已覆盖。今后重跑另存目录并保留原来源，补r2真正run-summary路径（交接指向r2/results，实际汇总在r1/r2/results）。当前作者122项仍为关键词/Python模型，不是原生验收。本轮独立结果另存，不改历史来制造闭合。
- A-M5-02延续：`main.splash:3662` accept未读取/persist `draft_acceptance_opinion.text`，意见输入仍丢失；建议将意见与completion/固定证据集/主体写入既有事件/回执。不据此判FAIL。
- A-M5-03延续：证据变化相关旧确认/AI建议失效继续按原报告挂账；在D04固定集合最小修复时核对受影响确认，不发散修前序模块。

## 判定

- 最终结论：**FAIL**。D-M5-01～05剩余项直接阻断实际附件查看、隔离、完整证据集验收或退回恢复；D-M5-06闭合。不是因建议项、数字偏差或M4前置FAIL判退。
- 精确范围：当前r2候选源码与本地Store路线已独立核验；原生正常链、退回链、重启、可信独立验收及权威业务结果仍BLOCKED/NOT_RUN。31/32控制流、122/122作者断言、本地Store PASS都不等于M5 PASS。
- 本地路线裁决：本轮当前digest的catalog/install_staged **可行**，无需AppHub publish/公开签名/listing。隔离目录离线签名已按授权执行并删除私钥，删除证据在local-store-validation.json与final-verification.json。没有上传、push、issue/评论、消息、公网部署或模型/provider配置。
- 解阻条件：执行环境须允许项目内写、禁止项目外写/网络并通过隔离预检；能够枚举、关闭本轮宿主进程且核残留窗口。之后用已核digest的安装副本后台启动指定launcher，完成真实UI动作/状态/字节/权威回执读回，测完立即关闭；不使用--help。可信独立会话应复用已验证的现有身份来源，标签切换无效；未证明前不可签PASS。
- 修复清单：只按D01接内容出口；D02固定可信根和真实目标隔离；D03验收逐项核固定集合；D04绑定内容/显式复用/本模块索引恢复；D05全字节读回和指纹。提供新candidate_id、上述差异与真实运行证据，再逐条复审；D06不重复修。
- NEEDS_ABRAM=no：当前待办是本模块修复、安全运行条件及既有可信会话验证；没有必须Abram另授权的当前动作。若之后证实必须新增业务身份来源，另明确提出该具体依赖；本轮不预先将其当既成阻塞，也不擅自配置。
- 门禁：仅更新GATES.json的M5 status及review相关字段，留存旧审查字段历史；作者候选/报告/测试声明与其他模块不改。ACCEPTANCE.json不改，不把历史后端记录改写为原生结果。
- 下一模块：**不允许，未执行。** 留在M5完成上述必修及必需运行证据后再审。
