# M2 实施报告 r11（修复轮，对 M2_REVIEW_r15）

- 模块 / 目标：M2「可信身份与可靠任务执行」——一次操作只正确执行一次；结果未知可对账；失败/重启不制造假成功。本轮只修 M2_REVIEW_r15 缺陷清单项（D-M2-01/02/03/05/07），不发散。
- candidate_id / base_candidate_id：**M2-r11-worktree** / base=**M2-r10-worktree**（r15 审查观察的工作树源码 9869f8ad… 冻结版，差异以其为基）。
- HEAD / 未提交差异 / 源文件哈希：HEAD 8d730569546cb57310944bb299695134df773b9d（dirty，含他人改动，全部保留，未 reset/stash/覆盖）。本轮冻结 main.splash **765739 B / SHA-256 f74813fb6945f2aaad3e7ef4d4f63f3c88017cff757967e10bc9a985d373e0c2**；bundle digest **70d795d179a9829d01cda4d5b34976baf42cb6029639f599410c047824386a73**。差异 `runtime/optimization/2026-10-09/M2/r11/main.splash.diff-r10-to-r11.patch`（以 r15 审查留存的 r10 观察源码 9869f8ad… 为 base）。完整清单 `M2/r11/native-prep/snapshot-start.json`。
- 目标宿主：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA 3e127963…，本轮未变）。
- 模型路由：本轮无模型调用（needs_model=false，0 请求）；G0-E 为 Abram 已裁决延期缺口（M3 到期）。
- 前置：M1 仍 FAIL（挂账，按 Abram 裁决继续）；本模块不制造前置 PASS。
- 验证环境：构建方不启动宿主；原生验证请求 `M2/native/REQUEST_build_r11.json`（20 场景：r10 全部 16 回归 + 4 个 r15 指名正反例）待驱动沙箱外执行，证据将落 `M2/native-runs/build_*_REQUEST_build_r11/`。

## 本轮修改（全部在 app/bundle/main.splash，按 r15 缺陷编号）

**D-M2-07（schema/迁移消费者：半条记录不得充当可信历史）**
- `_hf_action_record_ok`：status 从「可缺」改为**必需且在已知集合**；按状态定义必需字段——final/final_recovered 必须有完整绑定 actor/key/command/task_id/fp/expected_version 与完整 result（非空字符串或对象；布尔/数值/nil 不构成完整结果）；pending/needs_verify/superseded/pending_orphan 必须有 actor/key/command/task_id/fp/expected_version；rejected 必须有 actor/command/task_id。r15 点名的 `{"action_id":"review-incomplete"}`（缺 status/绑定）与 `{"action_id":"review-final","status":"final","result":false}`（result 类型不成立）现在都整份拒信并保源。
- `_hf_event_record_ok`：事件必需 at（严格数值）/kind/actor/task_id/task_version/after（非 nil）；action_id 可选但若存在必须非空字符串——历史无 action_id 的合法旧事件保留，但不充当新事务关联成功证据。
- 判据统一由 `hf_parse_history` / `_hf_validate_history` 消费，主/备份/迁移/恢复同规则；任一行失败整份拒绝、报告行号、保留全文，不返回可写部分记录。

**D-M2-03（新协议未接实际提交；恢复标记校验不足）**
- 恢复屏障真实接线：启动集中初始化块在 `bootReconcilePending()` 后调用 `hf_recover_commits()`；`runCommandBound` 在授权后、取锁前消费屏障——`STATE.hf_recovery_pending==true` 时先尝试收敛（登录授权后幂等补投影），仍 pending 则写 rejected 回执并 fail-closed 禁写，绝不绕过屏障写业务。`STATE.hf_recovery_pending` 在默认 STATE 显式声明（宿主对缺失键读取不保证 nil）。
- applied 标记强化（r15 点名 `:1706–1711`）：applied 文件必须严格解码为对象且 `tx_id==本事务`、`schema_version==1`、`verified_at` 为正的严格数值；`{}`/`null`/别的 tx_id 的合法 JSON 不再解除恢复屏障；applied 存在但不可读/不绑定/缺字段 = 权威未知，保持未决并阻断（不重做投影）。
- applied 写返回消费（r15 点名 `:1760–1764`）：`published` 而未 `verified` 不再计入 done——保持 unknown、pending_left+1、如实写 M2_RECOVERY_NOTICE；只有 `success && verified` 才收敛。
- commitBound 任务主写路径本轮未改为 tx 协议（仍 tmp→write→读回→final，见「尚未完成」）；恢复侧屏障与标记校验已闭环，业务写在恢复未决时整体阻断。

**D-M2-02（原结果与真实按钮链接线）**
- `hf_action_outcome` / `hf_query_original_action` 从「只有定义」变为真实消费：
  - `confirmDraft` 重放分支：按意图查出原 key/fp，`_authorityHistoricalConfirm(t.id, key, fp)` 精确绑定 + `hf_query_original_action` 取完整原结果，返回携带 `original_result` 与统一 `outcome`（kind=historical，retry_key=原键）；当前任务状态从权威盘独立另读。
  - `_m2_emit_replay`：`STATE.last_idem_hit` 携带 `outcome`（historical + 完整原结果）。
  - `createDraftFromPanel` 两个历史分支（confirmed_open / historical_confirmed）返回 `original_result` + `outcome`；historical 分支的 `original_result` 取精确绑定确认回执的完整 result，不是同 task 任意一条 final。
- `_authorityHistoricalConfirm` 签名升级为 `(task_id, key, fp)`：增加 `actor==sessionActor()` 绑定，key/fp 非空时必须逐字匹配原回执；返回新增 `original_result` 字段（final 回执 result 原文）。

**D-M2-01**：沿用 r10 已接线的严格解码 + `hf_preserve_source` 保源（r15 已认可源码改善）；本轮原生关闭证据随 REQUEST_build_r11.json 的 cold_login_view / corrupt_view_backup_unwritable / older_backup_newer_history 等场景补测。

**D-M2-05**：仍 HOST_PRIMITIVE_BLOCKED。固定宿主无原子替换/持有期锁/CAS 原语（`hf_storage_caps()` 如实声明 false），harness 白名单/schema 无同盘双独立认证上下文同步竞争控制；不以串行测试、write-verify 或线程模拟代签。

**未动**：D-M2-04/D-M2-06（保持原轮根因认可/关闭，未回退）；UI 布局/样式/控件命名未动；未读凭据文件，未改真实账号哈希，未 publish/push。

## 覆盖的既有验收项与证据形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|源码语法（vendored parser）|`cd octoscript && ~/.cargo/bin/cargo test -p octoscript-core --test m2_r7_bundle_parse`|PASS|1 passed（本轮改动后实测）|PASS|本报告；octoscript 测试输出|
|离线签名+本地安装|prepare_build_r11.py|rc0，私钥删除|LOCAL_INSTALL_VERIFIED，keys 目录空|PASS|M2/r11/native-prep/offline-store-evidence.json|
|真实桌面 20 场景（r10 十六回归 + action_record_missing_status / action_final_result_false / tx_commit_no_applied / tx_applied_unbound）|REQUEST_build_r11.json|见请求 note（解析 [E]=0；两个 schema 反例整份拒信+保源+冻结；两个 tx 屏障场登录页显示恢复提示、投影未动）|待驱动执行|NOT_RUN（待 harness）|M2/native/REQUEST_build_r11.json → M2/native-runs/|
|认证业务/同盘竞争/写点注入|—|—|白名单/schema 能力缺口|BLOCKED|同 r15 挂账（D-M2-05）|

## 尚未完成

- D-M2-05 原子竞争边界：BLOCKED（宿主无原语 + harness 无同盘双上下文同步竞争能力）。
- commitBound 主写路径迁移到完整 H4 prepare→commit→投影协议：未做（本轮先闭恢复屏障与 applied 校验）；业务写在恢复未决时已整体阻断，但「主写后 final 前中断」的逐写点注入验证仍依赖 harness 控制缺口，NOT_RUN。
- 认证业务创建/重试/冲突/权限矩阵、连续同 Store 重开：NOT_RUN（可信输入/写点注入控制缺口）。
- 本轮全部原生结果待驱动执行 REQUEST_build_r11.json 后核验。
- G0-E 真实模型 provider：延期缺口（Abram 已裁决，M3 到期），本模块 0 次真实调用。

## 交接

- 候选：M2-r11-worktree；main SHA-256 f74813fb…；bundle digest 70d795d1…；差异补丁与快照在 `runtime/optimization/2026-10-09/M2/r11/`。
- 签名/安装证据：`M2/r11/native-prep/offline-store-evidence.json`（私钥已删，目录为空）；seed 清单 `seed-manifest.json`（20 场景 seed 含 apps/catalog.json）。
- 原生请求：`M2/native/REQUEST_build_r11.json`（20 场景；无 ui_actions、无会话预装、无模型）。
- 测试命令：`cd octoscript && ~/.cargo/bin/cargo test -p octoscript-core --test m2_r7_bundle_parse`；`python3 runtime/optimization/2026-10-09/M2/r11/prepare_build_r11.py`（只能跑一次，OUT 已存在会拒）。
