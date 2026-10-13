# M2 实施报告 r10（修复轮，对 M2_REVIEW_r11）

- 模块 / 目标：M2「可信身份与可靠任务执行」——一次操作只正确执行一次；结果未知可对账；失败/重启不制造假成功。本轮只修 M2_REVIEW_r11 缺陷清单项，不发散。
- candidate_id / base_candidate_id：**M2-r10-worktree** / base=**M2-r9-worktree**（r11 受审 a5bca2f3… 冻结版）。
- HEAD / 未提交差异 / 源文件哈希：HEAD 8d730569546cb57310944bb299695134df773b9d（dirty，含他人改动，全部保留，未 reset/stash/覆盖）。本轮冻结 main.splash **653536 B / SHA-256 244a180c4605f85e3fd2a5d7f6b9d4987704080ac017c7182ec09f6d2ee4dc83**；bundle digest **04492599e88fd37807778d172a2e397e0edafb55a4fa2d4d31c51a0cd38167a3**。差异 `runtime/optimization/2026-10-09/M2/r10/main.splash.diff-a5-to-r10.patch`（227+/68-）。完整清单 `M2/r10/native-prep/snapshot-start.json`。
- 目标宿主：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA 3e127963…，本轮未变）。
- 模型路由：本轮无模型调用（needs_model=false，0 请求）；G0-E 为 Abram 已裁决延期缺口（M3 到期）。
- 前置：M1 仍 FAIL（挂账，按 Abram 裁决继续）；本模块不制造前置 PASS。
- 验证环境：构建方不启动宿主；原生验证请求 `M2/native/REQUEST_build_r10.json`（16 场景）待驱动沙箱外执行，证据将落 `M2/native-runs/build_*_REQUEST_build_r10/`。

## 本轮修改（全部在 app/bundle/main.splash，按 r11 缺陷编号）

**D-M2-01（损坏视图恢复覆原源 + to_chars 运行错误）**
- `loadViewState`：parse 结果必须过 `m7_is_object_value` 严格对象门禁——宽容 parse 对截断/错误值返回的非 nil 非对象（含 error 值）一律按损坏处理，不再进入字段并入（r11 实测 `splash:1891 to_chars not found on error` 的来源）。
- 损坏分支：备份写+独立读回逐字节核实后才算备份成立；已有 boot-bak 必须可读（目录/不可读不算成功备份）；备份不成立 → `_VIEW_STATE_OK` 保持 false（saveState 拒写，原文绝不被默认值覆盖），状态如实报「备份失败、原文保留、视图写冻结、人工出口」。
- 字段并入加逐字段类型门禁（新增 `m7_is_string_value`；数值字段用既有 `m7_is_number_value`），非法类型不并入。
- `_textLenSafe` / `_charAtSafe` / `_strSlice` 对非字符串值（含 error 值）try/catch 兜底，消除该运行错误类。

**D-M2-02（unknown 异参与历史重放）**
- `createDraftFromPanel`：同 key 异 payload 在**任何占用状态**（含 pending/needs_verify/unknown）一律 `idem_conflict` 拒绝，不再只对 final/final_recovered。
- `_authorityHistoricalConfirm` 接入真实链：`createDraftFromPanel` 重放在 `_ra.open==false` 后先查历史（磁盘 confirmDraft final 回执 + 关联事件，不要求当前 OPEN），命中返回完整原结果、当前状态另读；`confirmDraft` 重放路径改走 `_authorityHistoricalConfirm`，当前任务状态从权威盘独立另读（v9 可查原 v1）。
- `confirmDraftModelBound`：面板为空但存在归属当前主体的持久不可变意图（payload 完整）时直通 `createDraftFromPanel` 对账/重放链，不被新内容前置守卫阻断；`createDraftFromPanel` 增加「空面板 + 无原意图回执 → 拒创建空草稿」。

**D-M2-03（关联提交逐写点消费）**
- `commitBound` 清 tmp 写显式 try/catch 消费；失败时提交事实（主写+读回全等）已成立不假报，但如实写入 final 回执 note（tmp 残留待人工清理），不静默。
- 提交读回 `readTaskByIdFromDisk` 包 try/catch，读回异常按不匹配 → needs_verify。

**D-M2-04（三字段代原动作证明）**
- `commitBound` 读回核对从 version/status 两字段升级为**完整 after 规范 JSON 逐字节全等**（`rb.to_json() == t.to_json()`）。
- `bootReconcilePending` 的 needs_verify 恢复同样改为完整 after 全等；同 version/status/assignee 但完整 after 不同 = 无关动作，保持 unknown。version==expected+1 前置保留。

**D-M2-07（坏历史假迁移 / 诊断失败丢坏源 / 恢复无可见出口）**
- 新增 `_m2_ndjson_line_ok`：NDJSON 逐行「完整 JSON」判据——去空白后 `{` 开头、`}` 结尾、解析为非空对象；截断对象被宽容 parse 成的 `{}` 不再算合法记录。`loadJsonlLines` / `_m2_parseRecordsLoose` / `migrateJsonlLegacy` 三处逐行解析共用（主/bak 同规则，先判后写主）。
- `migrateJsonlLegacy` bak 恢复分支：坏源另存（诊断文件写+读回核实）失败 → **停止覆盖**，原文保留未动、冻结、如实记 `corrupt_source_preserved:false` 与保源失败原因；不再覆主后谎称 preserved。
- 恢复/冻结错误接入当前可见界面：新增全局 `M2_RECOVERY_NOTICE`，`_m2_mark_dirty` 与 loadViewState 损坏备份失败路径置位；`refreshDesktop` 在未登录可见的登录页 `login_hint` 顶部展示。

**未动**：D-M2-05（HOST_PRIMITIVE_BLOCKED，宿主无原子锁/CAS 原语，仍 BLOCKED，不以 write-verify 冒充互斥）；D-M2-06（sourceOk 白名单，保持关闭，未回退）；UI 布局/样式/控件命名未动。

## 覆盖的既有验收项与证据形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|源码语法（vendored parser）|`cargo test -p octoscript-core --test m2_r7_bundle_parse`|PASS|1 passed|PASS|本报告命令输出；octoscript 测试|
|离线签名+本地安装|prepare_build_r10.py|rc0，私钥删除|LOCAL_INSTALL_VERIFIED，keys 目录空|PASS|M2/r10/native-prep/offline-store-evidence.json|
|真实桌面 16 场景（含 r11 两失败场精确重跑 + corrupt_view）|REQUEST_build_r10.json|见请求 note|待驱动执行|NOT_RUN（待 harness）|M2/native/REQUEST_build_r10.json → M2/native-runs/|
|认证业务/竞争/写点注入|—|—|白名单/schema 能力缺口|BLOCKED|同 r11 挂账|

## 尚未完成

- D-M2-05 原子竞争边界：BLOCKED（宿主无原语 + harness 无同盘双上下文同步竞争能力），源码层已守同锁/token/提交点复核，不以串行代签。
- 认证业务创建/重试/冲突/权限矩阵、逐提交写点故障、连续同 Store 重开：NOT_RUN（可信输入/写点注入控制缺口）。
- 本轮全部原生结果待驱动执行 REQUEST_build_r10.json 后核验；若 r11 两失败场仍未通过，按实际状态交接。
- G0-E 真实模型 provider：延期缺口（Abram 已裁决，M3 到期），本模块 0 次真实调用。

## 交接

- 候选：M2-r10-worktree；main SHA-256 244a180c…；bundle digest 04492599…；差异补丁与快照在 `runtime/optimization/2026-10-09/M2/r10/`。
- 签名/安装证据：`M2/r10/native-prep/offline-store-evidence.json`（私钥已删，目录为空）；seed 清单 `seed-manifest.json`。
- 原生请求：`M2/native/REQUEST_build_r10.json`（16 场景；无 ui_actions、无会话预装、无模型）。
- 测试命令：`cd octoscript && ~/.cargo/bin/cargo test -p octoscript-core --test m2_r7_bundle_parse`；`python3 runtime/optimization/2026-10-09/M2/r10/prepare_build_r10.py`（只能跑一次，OUT 已存在会拒）。
- 编码方已将 GATES.json 的 M2 置为 READY_FOR_REVIEW；最终 PASS 等待独立审查。
