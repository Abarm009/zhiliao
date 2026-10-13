# M2 实施报告 r12（修复轮，对 M2_REVIEW_r16）

- 模块 / 目标：M2「可信身份与可靠任务执行」——一次操作只正确执行一次；结果未知可对账；失败/重启不制造假成功。本轮只修 M2_REVIEW_r16 缺陷清单项（D-M2-01/02/03/05/07），不发散、不新增功能/入口/字段。
- candidate_id / base_candidate_id：**M2-r12-worktree** / base=**M2-r11-worktree**（r16 受审 f74813fb… 冻结版，差异以其为基）。
- HEAD / 未提交差异 / 源文件哈希：HEAD 8d730569546cb57310944bb299695134df773b9d（dirty，含他人改动，全部保留，未 reset/stash/覆盖）。本轮冻结 main.splash **773316 B / SHA-256 3af303e7090f6e69137d7d1d0bd5060cbc35c44583ebfb695f43e6dad3ffb3e9**；bundle digest **3d3d820748a19cc8ae13d07ecf1a14467a7410a11239183c2273bdc22289e7cc**。差异 `runtime/optimization/2026-10-09/M2/r12/main.splash.diff-r11-to-r12.patch`（以 r11 冻结 bundle 内 main.splash f74813fb… 为 base，可用 patch 独立重建）。完整清单 `M2/r12/native-prep/snapshot-start.json`。
- 目标宿主：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA 3e127963…，本轮未变）。
- 模型路由：本轮无模型调用（needs_model=false，0 请求）；G0-E 为 Abram 已裁决延期缺口（M3 到期）。
- 前置：M1 仍 FAIL（挂账，按 Abram 裁决继续）；本模块不制造前置 PASS。
- 验证环境：构建方不启动宿主；原生验证请求 `M2/native/REQUEST_build_r12.json`（25 场景：r11 全部 20 回归 + 5 个 r16 失败场精确重跑）待驱动沙箱外执行，证据将落 `M2/native-runs/build_*_REQUEST_build_r12/`。

## 本轮修改（全部在 app/bundle/main.splash，按 r16 缺陷编号）

**D-M2-01（根因：普通数组 to_string 把码点拼成十进制串）**
- `_hf_parse_string`：收集码点的 `out` 由 `[]` 改为 `"".to_chars()` 产出的 **U32 typed 数组**。钉版宿主源码实证（`runtime/native-build/makepad/platform/script/src/`）：`string_to_chars_array` 恒产 `ScriptArrayStorage::U32`（空串同）；U32 storage 的 `push` 保持 U32 并以 `as_f64()` 转换（读 U32 元素经 `From<u32>` 得 f64，数字字面量 parser 先按 f64 入栈，算术 `* +` 经 `as_number` 后 `from_f64_traced_nan` 产 f64——全部入口值均为 f64，无 u40 截零风险）；U32 数组 `to_string()` 按 `char::from_u32` 转回字符。r16 实测 `"pending_input"→"112101…"`、`actor→"9799…"` 的改键根因即普通 `[]`（ScriptValue storage）的 to_string 串接十进制。
- `_hf_parse_number`：`sub` 同样改 U32 typed 数组（r16 标注的同类源码风险，数值文法子串 `"454950…"` 化）。
- 效果：合法 view（中文/emoji/引号/换行）键值原样还原，loadViewState 不再「取不到原键却继续落默认值」；合法历史/tx 索引 id 原样还原，恢复屏障按真实 tx_id 找 commit/applied。

**D-M2-07（迁移/bak/读回统一严格判据，宽容归一化不再合法化）**
- `_m2_parseRecordsLoose(text, kind)`：函数体改为直接委托 `hf_parse_history(text, kind)`（完整消费解码 + 重复键拒绝 + 逐记录 schema 绑定校验）；原「宿主宽容 parse_json + 非空对象」判据整体删除。迁移、bak 恢复、原文判定、读回 5 个调用点全部带 `kind = hf_record_kind_for_path(path)`。
- `migrateJsonlLegacy`：主文件整体判据由宽容 `parse_json` 改 `hf_json_decode_complete`（严格失败才进逐行兜底评估）；当前格式数组的元素门禁由 `_m2_history_record_ok` 升 `_hf_history_record_ok_kind`（与 load 同一 schema）；NDJSON 逐行判据由 `_m2_ndjson_line_ok`+宽容 parse 改逐行 `hf_json_decode_complete` + `_hf_history_record_ok_kind`；末段读回也改经 `_m2_parseRecordsLoose`（严格）。任何记录在严格整份通过前不写主文件——r16 的 rv_history_duplicate_key（单条重复 status 键）现在在**任何主写前**整份拒绝并保当前全文，不再先被宽容迁移归一化。
- `_m2_ndjson_line_ok`/`_m2_history_record_ok` 不再是任何写入路径的合法性来源（无生产调用点，注释如实标注保留对照）。

**D-M2-03（恢复屏障补强）**
- 索引登记但 commit 决定缺失：不再一律「决策前中断安全跳过」——fail-closed：`_pending_left+1` + `M2_RECOVERY_NOTICE` 可见提示（权威未知，业务写阻断，人工核对 tx/ 后重启），不自动抹掉登记项。
- applied 标记除 r11 的 schema/tx_id/verified_at 形状绑定外，新增 `_hf_projections_complete(_prep, tx_id)`：marker 形状绑定成立后还必须与提交决定及**全量权威投影**核对（盘任务与 after 全等 + 同 action_id final 回执且 result 一致 + 关联事件 kind 一致）；形状正确但投影缺失（r16 rv_tx_claimed_applied）按未应用进入幂等恢复路径，不直接解屏障；commit 缺失/损坏则权威未知 fail-closed。
- commitBound 任务主写路径本轮仍未迁完整 H4 tx 协议（见「尚未完成」，如实记录）；恢复侧屏障/标记/投影核验已闭环。

**D-M2-02（精确原动作绑定）**
- OPEN 重放分支（createDraftFromPanel）：outcome 的 `action_id` 与 `original_result` 同属**创建回执**（`_cd_prior.action_id` + `_cd_prior.result`）；确认 action_id 只作独立字段 `final_action_id`，不再拿确认 ID 搭配创建 result 混绑。
- 历史分支：废除 `_authorityHistoricalConfirm(_rp_task_id, "", "")` 空调用——先用盘任务 + 固定 params 重建真实 fp（fingerprint 不含版本/状态，跨状态稳定），再从持久意图记录取原 key，按真实 key/fp 精确绑定。
- `_authorityHistoricalConfirm`：空 key/fp 直接不确认（reason 如实说明），删除「退成同 task 同 actor 最后一条 final」的回退——较新状态下不再用别的确认动作结果冒充原操作结果。
- `confirmDraft` 重放：`hf_query_original_action` 返回 conflict（同键异参）时按 unknown 出口返回（不构 historical outcome、不返回成功）；仅 historical 才覆盖 original_result。

**D-M2-05**：仍 HOST_PRIMITIVE_BLOCKED。固定宿主无原子替换/持有期锁/CAS 原语（`hf_storage_caps()` 如实声明 false），harness 白名单/schema 无同盘双独立认证上下文同步竞争控制；不以串行测试、write-verify 或线程模拟代签。

**未动**：D-M2-04/D-M2-06（保持原轮结论，未回退）；UI 布局/样式/控件命名未动；未读凭据文件，未改真实账号哈希，未 publish/push。

## 覆盖的既有验收项与证据形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|源码语法（vendored parser）|`cd octoscript && ~/.cargo/bin/cargo test -p octoscript-core --test m2_r7_bundle_parse`|PASS|1 passed（本轮全部改动后实测）|PASS|本报告；octoscript 测试输出|
|离线签名+本地安装|prepare_build_r12.py|rc0，私钥删除|LOCAL_INSTALL_VERIFIED，keys 目录空|PASS|M2/r12/native-prep/offline-store-evidence.json|
|真实桌面 25 场景（r11 二十回归 + history_duplicate_key / tx_applied_null / tx_applied_wrong_id / tx_applied_false_time / tx_applied_claimed；cold_login_view 换 unicode 原文 seed、clean_ndjson 换嵌套中文 result seed）|REQUEST_build_r12.json|见请求 note（全部 [E]=0 且无 [I] splash 运行诊断；unicode 原文精确保留；中文嵌套历史迁移并加载、业务区渲染；重复键主文件字节不动+冻结；六个 tx 屏障场 pending=true+提示+投影未动）|待驱动执行|NOT_RUN（待 harness）|M2/native/REQUEST_build_r12.json → M2/native-runs/|
|认证业务/同盘竞争/写点注入|—|—|白名单/schema 能力缺口|BLOCKED|同 r16 挂账（D-M2-05）|

## 尚未完成

- D-M2-05 原子竞争边界：BLOCKED（宿主无原语 + harness 无同盘双上下文同步竞争能力）。
- commitBound 主写路径迁移到完整 H4 prepare→commit→投影协议：未做；业务写在恢复未决时已整体阻断，逐写点注入验证仍依赖 harness 控制缺口，NOT_RUN。
- D02 真实按钮链（认证登录下正常/跨状态重放、占键异参、v9 查原 v1）：本轮只完成源码侧精确绑定收口；动态验证需要可信输入通道，NOT_RUN。
- 本轮全部原生结果待驱动执行 REQUEST_build_r12.json 后核验。
- G0-E 真实模型 provider：延期缺口（Abram 已裁决，M3 到期），本模块 0 次真实调用。

## 交接

- 候选：M2-r12-worktree；main SHA-256 3af303e7…；bundle digest 3d3d8207…；差异补丁与快照在 `runtime/optimization/2026-10-09/M2/r12/`。
- 签名/安装证据：`M2/r12/native-prep/offline-store-evidence.json`（私钥已删，目录为空）；seed 清单 `seed-manifest.json`（25 场景 seed 含 apps/catalog.json）。
- 原生请求：`M2/native/REQUEST_build_r12.json`（25 场景；无 ui_actions、无会话预装、无模型）。
- 测试命令：`cd octoscript && ~/.cargo/bin/cargo test -p octoscript-core --test m2_r7_bundle_parse`；`python3 runtime/optimization/2026-10-09/M2/r12/prepare_build_r12.py`（只能跑一次，OUT 已存在会拒）。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
