# M3 实施报告 r6

修复轮（Kimi-K3 构建方）。严格按 `M3_REVIEW_r6.md` 缺陷清单 D-M3-01/03/04/05/06 逐条修复，只修清单项，未发散；D-M3-02/D-M3-07 已闭合部分保留未动。

- 模块 / 目标：M3「真实输入与AI报修」—— 从用户实际描述得到可编辑、有来源的报修草稿，经人确认后创建可回读工单。
- candidate_id / base_candidate_id：**M3-r6-worktree / M3-r5-worktree**。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD `8d730569546cb57310944bb299695134df773b9d`（dirty，含他人未提交改动，全部保留）；冻结对象清单与 SHA256 见 `runtime/optimization/2026-10-09/M3/r6/CANDIDATE.json`（主源 462803 字节，SHA256 `abfc9391…f6ee9e`）。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`（沿用审查方记录）。宿主/launcher 由驱动在沙箱外经 harness 运行；本构建方未自行启动。
- 实际模型路由检查结果（开发会话）：本会话为 Kimi-K3（Abram 2026-10-11 21:03 裁决构建方）。Codex Router 状态未在本会话核验，不声称已切换。
- 已检查的前置 PASS 报告：无已接受 M2 PASS 基线（M2_REVIEW_r6/r8 均 FAIL，挂账沿用）；本轮仅核阻断本模块的加载/权限/确认/回读依赖，不改变 M2 结论。
- 本轮修改文件与原因：见下表。
- 桌面 UI/交互变化：`ai_suggestion_label` 来源区改为结构化渲染（`id[status]“quote”` + 缺项追问/待澄清歧义两行）；`input_validation_label` 新增缺项/歧义补充出口；确认成功后状态机进入 `CONFIRMED`。
- 接口 / 数据迁移 / 旧数据恢复方式：`manifest.json` 增 `net` capability + `network.hosts`（schema 1 既有字段，旧 host 按 KNOWN_CAPABILITIES 校验，无迁移）；任务新增字段沿用 r1–r5（向后兼容读）。
- 已有别人修改的保留与适配：M2 r6/r7（runCommandBound/replay/意图持久化）、M4/M5/M6 在同 main.splash 的函数均未改语义；`confirmDraft` 仅加返回值（旧调用点 7943 忽略返回值，行为不变）。
- 启动步骤 / 隔离数据位置：驱动执行 `runtime/optimization/2026-10-09/M3/native/REQUEST_build_r6.json`；证据将落 `runtime/optimization/2026-10-09/M3/native-runs/build_r6_REQUEST_build_r6/`。
- 应用运行模型/provider（适用时；无秘密）：MiniMax / MiniMax-M3 / `https://api.minimax.cn/anthropic`（anthropic messages）；harness 内由 `OCTOSENSE_MODEL_ENDPOINT` 覆盖到 127.0.0.1 代理；宿主只持 `MM_KEY` 占位符；真密钥不进入代码/日志/报告。
- 覆盖的既有验收项与证据运行形态：协议层源码断言 + Python 仿真（本目录证据）；原生层由 harness 请求覆盖加载/渲染/权限投影/手工面板可达。

## 逐条修复（按审查方改法）

### D-M3-01（解析阻断 + 最小 HTTP 许可 + 请求绑定值）
- 解析阻断：`168...:5184` 指纹函数的位运算表达式已由前轮 parsefix 修复（当前 6077 行 `(b & 255)`；M2 r7/r8 两轮 harness 共 13 场景 `[E]=0`，见 `M2/native-runs/*_2104`）。本轮复核无回归（r6 静态扫描 0 ok / 0 三元 / 0 缺函数）。
- 最小 HTTP 许可：`app/bundle/manifest.json` 增 `"net"` + `network.hosts=["api.minimax.cn","127.0.0.1"]`（127.0.0.1 为 harness 本机代理）；`install_probe` may_run 实证 `caps={"net","storage"}, hosts={"127.0.0.1","api.minimax.cn"}`（`build_r6/offline-store-evidence.json` 最后一步）。
- 绑定值进提示词：`_modelInstructionText()` 现携带真实 `request_id / expires_at_ms / task_version / draft_version`（`main.splash:3825` 起），模型逐字回声，不再占位编造；`sources` 协议同步升级为 `unknown`/文字/`{fact_id,version,quote}`。
- 仍 NOT_RUN：`host.http_fetch` 真实原生放行（需宿主运行 + 输入通道，见"尚未完成"）。

### D-M3-03（当前绑定完整性）
- `deliverModelReturn` 回包先 `_syncPanelInputFromUI()` 重读真实控件（不再只信 TASK_INPUT 缓存）。
- `bindRequestVersions` 新增 `expected_facts_version`（`_currentFactsVersion()`：当前项目空间/设备 id+active+名称指纹）与 `expected_evidence_version`（任务 version×1000+evidence 数，磁盘权威）。
- `validateSuggestion` 新增：与**当前磁盘任务版本**比对（不只请求快照）、事实版本比对、证据版本比对；切主体/切项目/撤权检查沿用。
- `_suggestionAcceptGate`：删除"invalidated_by_edit 一刀切"（它会拒掉合法采纳）；新增原主体/原项目快照比对 + `identityActive` 当前权限核验。
- `applyDraftFromAI`：不再把合法采纳标为编辑失效（旧确认的陈旧性由 draft_version/hash 绑定在确认入口独立判定）。
- `confirmDraftModelBound`：AI 来源草稿核 `ai_history_raw_text_hash == 当前输入 hash`、`actor_at_apply`、`project_at_apply`。

### D-M3-04（可核来源）
- 新增 `_validateSourceEntry(kind, entry)`：`unknown`/描述文字（unverified_text，不作确认依据）/`{fact_id,version,quote}` 对象；不存在/跨项目/停用/版本陈旧分别 `unknown_fact/cross_project/inactive/stale`。
- `parseModelReturn`：三项 sources 全部结构化校验，硬失败状态整包拒绝（FABRICATED_FACT/CROSS_PROJECT/STALE_INPUT）。
- `applyDraftFromAI`：来源快照来自校验结果；`verified` 要求 fact_id 与采纳候选 id 一致，否则降级 unverified_text。
- `confirmDraftModelBound`：`_validateSourcesSnapshot()` 消费快照——verified 来源此刻须仍通过同一校验，失效/不可核即拒。
- UI：`aiSuggestionLabelText` 改 `_fmtSourceEntry` 显式读结构，unknown 与 verified 界面可区分。

### D-M3-05（权威最终回执）
- `confirmDraft()` 返回结构化 `{result: final|rejected|unknown, task_id, action_id, status, reason}`；final 前做磁盘读回 OPEN + `findReceiptByKey` final 回执 + `confirm_draft` 事件关联同一 action_id 三重核验；replay 路径同样读回。
- `createDraftFromPanel()` 只认 `_cf.result=="final"`，消费端再独立 `readTaskByIdFromDisk` 读回；outcome 增 `final_action_id`；原键恢复分支（内容指纹 `_cd_key` 查 RECEIPTS，不 newId 重建）同步补齐 confirmed_open/final_action_id。
- `confirmDraftModelBound()` 严格消费 `commit_ok && confirmed_open && final_action_id`，任一缺失即拒并保留草稿；成功才 `AI_STATE="CONFIRMED"`（修正原误写的 `MANUAL`）。

### D-M3-06（核心歧义阻断确认）
- `_computeResolvedFields`：`problem` 分支不再吞"空间定位/设备定位/具体是哪一组插座"；各字段由对应字段的人工编辑痕迹判定。
- `confirmDraftModelBound`：确认前计算未解缺项/歧义；未解核心歧义（多候选未人工选择）直接拒绝并给出补充出口文案；空间缺项未解拒绝；**空 asset 不一律拒绝**（沿用合法空间下设备可未知的手工规则）。
- `inputValidationLabelText`：逐条列出未解缺项/歧义及补充出口。

## 验证证据

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|静态解析风险扫描|r6_static_check.py|0 ok / 0 三元 / 函数齐|0 / 0 / 齐|PASS|runtime/optimization/2026-10-09/M3/r6/evidence/r6_static_check.json|
|缺陷修复源码断言+守卫仿真|r6_fix_verification.py|32 项全过|32/32|PASS|runtime/optimization/2026-10-09/M3/r6/evidence/r6_fix_verification.json|
|离线签名 catalog + install_staged|prepare_build_r6.py（授权 A 范围内）|verify rc0 + may_run ok + 私钥删除|全 rc0；caps={net,storage}；keys 删除 exists_after=false|PASS|runtime/optimization/2026-10-09/M3/native/build_r6/offline-store-evidence.json|
|真实桌面操作（加载/渲染/导航/截图）|REQUEST_build_r6.json 三场景|零 [E]、客户区渲染、手工面板可达|待驱动执行|NOT_RUN（构建方不得自启宿主）|runtime/optimization/2026-10-09/M3/native/REQUEST_build_r6.json → native-runs/build_r6_REQUEST_build_r6/|
|权威状态与回执（原生）|同上|确认前无 OPEN；确认后 task/回执/事件一致|待驱动执行|NOT_RUN|同上|
|失败与重试 / 重启恢复（原生）|同上|草稿保留、原键恢复|待驱动执行|NOT_RUN|同上|
|受影响先前模块回归|M2 runCommandBound/confirmDraft 消费面|返回值新增不改旧调用|M2 r8 FAIL 挂账沿用，结论不变|NOT_RUN（由审查方核）|M2_REVIEW_r8.md|
|真实 MiniMax 调用|needs_model 场景|≤10 次、遇 402 即停|未发起（见下）|NOT_RUN|r3 Python 3/3 证据沿用：runtime/optimization/2026-10-09/M3/r3/|

## 尚未完成

- **真实桌面键盘输入通道 BLOCKED（通道缺口，非本模块代码）**：固定宿主不支持 `--test-action type:`（M2_REVIEW_r5 已实证 unknown action；M3_REVIEW_r6 §判定同样记录）。因此"原话→追问→编辑→确认"的原生键入驱动、以及由 UI 触发的真实 MiniMax 原生调用本轮无法驱动；本请求不含 needs_model 场景以守住 ≤10 预算（r3 Python 真实调用 3/3 沿用，累计真实调用 3 次）。需构建/驱动提供合规输入通道后复验。
- 动态交错（等待中键入 B / APPLIED 后切项目撤权）原生 NOT_RUN；源码守卫与 Python 仿真已覆盖。
- M2 FAIL（r6/r8）挂账未修（按用户指示只做本模块）；M3 经 M2 既有边界消费。
- harness 执行结果（frames/host.log/summary）由驱动在沙箱外产出后补充；本报告先交接源码与离线证据。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M3/r6/CANDIDATE.json`（含冻结对象 SHA256/字节数）。
- 离线 Store：`runtime/optimization/2026-10-09/M3/native/build_r6/store/`（catalog.json + artifacts + install-root）；anchor `4f82d3d8…553e`；bundle digest `48a42cf0…5ec9`；私钥已删（evidence 内 exists_after=false）。
- harness 请求：`runtime/optimization/2026-10-09/M3/native/REQUEST_build_r6.json`（3 场景，needs_model=false，expect_bundle_digest 已填）。
- 证据脚本：`runtime/optimization/2026-10-09/M3/r6/scripts/{m3_r6_static_check.py, m3_r6_fix_verification.py}`；复跑命令：`python3 <script>`。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。
