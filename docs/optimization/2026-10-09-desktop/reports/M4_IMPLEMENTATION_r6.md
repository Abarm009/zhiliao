# M4 实施报告 r6

- 模块 / 目标：M4 接单设备与预约桌面流程 —— 修复轮，只修 M4_REVIEW_r6 缺陷清单三项（B-M4-01 / D-M4-03 / D-M4-04），不发散。
- candidate_id / base_candidate_id：`M4-r6-worktree` / `M4-r5-worktree`（以 GATES + 冻结摘要定位，不按 mtime 选版）。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d`（未提交工作树，含他人 M2/M3/M5/M6/M7 改动，全部保留）。当前 `app/bundle/main.splash` SHA-256=`37d1b1cabbea7d17e0b24ddb66aae4afe7ed5b54940df6b6b8d14a3c3d777b20`，477432 字节、9951 行。base=M3-r7 冻结源 SHA-256=`a6f55a21aa8ccd70e2bcc9a886dfdedab996b7811f6b447e62fd49a20d8cdee8`（473410 字节）；本轮差异仅 110 行 diff，见 `runtime/optimization/2026-10-09/M4/r6/evidence/r5-to-r6.diff`。
- 目标宿主：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（固定宿主，SHA `3e127963…`，本轮未启动）。
- 实际模型路由：本会话为 Kimi-K3（Abram 21:03 裁决构建方）；无法接口验证主会话 Router 细节，不冒称。
- 已检查前置：M3 仍 FAIL（M3_REVIEW_r8，D-M3-01 渲染路径未闭合），按用户挂账裁决继续修本模块清单项，不冒称前置满足。

## 本轮修改文件与原因（严格按审查方修改方案）

仅改 `app/bundle/main.splash`，四处 hunks：

1. **D-M4-03（授权出口清理）** — `runCommandBound`：把 `let _cc = STATE.m4_cross_check; STATE.m4_cross_check = nil` 移到 `authorizeCommand` 之前。r5 注释声称在授权前、实际代码在授权后，授权失败 return 时 spec 残留全局。纯内存操作，授权前无业务持久写，顺序调整安全。
2. **D-M4-03（坏盘显式拒绝）** — `runCommandBound` 跨技工冲突权威重读段：`tasks.json` 存在但读取/解析失败时，新增 `authority_unreadable` 拒绝（写 rejected 回执 + 释放锁 + `return false`），不再把异常吞成"未发现冲突"放行。文件不存在=全新空盘，仍按无冲突处理。
3. **D-M4-03（提交边界 owner 复核）** — `commitBound`：写盘前复核 `tasks.lock` 归属；锁非空且非本 actor 持有 → 不写 `tasks.json`、记 `needs_verify`、释放锁返回 false（避免覆盖另一上下文在途提交）。锁为空（create 路径不持锁）或属本 actor 维持原流程。真跨进程原子互斥仍 HOST_PRIMITIVE_BLOCKED（宿主 fs 无 O_EXCL/flock/rename 原子），本轮只缩小窗口，不冒充解阻；如需真互斥，最小方案=宿主 fs 暴露 O_EXCL 创建语义后重写 `_acquireTaskLock`，复现脚本沿用 r5 `lock_repro`。
4. **D-M4-04（字段确认 epoch）** — 新增 `PENDING_DRAFT.human_edited_epoch_fields`：失效（`m4_invalidateConfirmation`）清空 epoch 集合并开启新 epoch，累计 `human_edited_fields` 保留作历史审计；`editDraftField`/`editRawText` 双写两集合；`applyDraftFromAI`/`closeDraftPanel` 同步重置；`confirmDraftModelBound` 恢复路径 (b) 只消费 epoch 集合——失效前旧编辑齐备 + 仅改原文/联系人不再能复活旧 proposal。

## B-M4-01（解析阻断）处置

当前源在固定宿主下已无解析错误：M3_REVIEW_r8 对同一 base digest（473410 字节）实证 host.log 无 parser 错误、进入 VM 运行阶段（错误为 index_of/slice 运行时问题，属 M3 D-M3-01 挂账范围）。本轮对修复后源做括号平衡粗扫（{}/{()/[] 全平衡）并通过 `runtime/optimization/2026-10-09/M4/native/REQUEST_build_r6.json` 请求三场冷启动复验零 parser 错误。"登录/任务界面真实渲染"验证子项仍被 M3 D-M3-01 阻断，如实 NOT_RUN，不由 M4 修。

## 桌面 UI/交互变化

无（本轮纯命令边界与确认守卫修复；UI 层未动）。

## 接口 / 数据迁移

`PENDING_DRAFT` 为源码内字面量全局，新增字段随加载生效；消费处均有 nil 兜底。无持久 schema 变更。

## 已有别人修改的保留与适配

base 取 M3-r7 冻结源（含 M2/M3 修复轮全部改动），只叠加 4 处 hunks；未 reset/stash/删除任何他人改动。diff 证据：`r6/evidence/r5-to-r6.diff`。

## 启动步骤 / 隔离数据位置

构建方不启动宿主。原生验证请求：`runtime/optimization/2026-10-09/M4/native/REQUEST_build_r6.json`（3 场景：r6_cold_reporter / r6_expired_tech_hint / r6_terminal_manager_hint，needs_model=false）。隔离 store 与种子：`M4/native/build_r6/`（离线签名，私钥已删，删除证据 `offline-store-evidence.json`）；驱动执行后证据将落 `M4/native-runs/build_r6_*/`。

## 应用运行模型/provider

needs_model=false，本轮模型 0 调用；无密钥进入代码/日志/报告。

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r6 三场冷启动|零 parser 错误、业务区渲染|待驱动执行|NOT_RUN（待 harness）|M4/native/REQUEST_build_r6.json|
|权威状态与回执|同上|——|待驱动执行|NOT_RUN|同上|
|失败与重试|静态：坏盘拒绝路径|authority_unreadable 显式拒|源码已接|源码 FIXED / 动态 NOT_RUN|r6/evidence/fix_verifier.json|
|重启恢复|——|——|未覆盖|NOT_RUN|——|
|受影响先前模块回归|括号平衡 + 静态核验 14 项|全过|14/14|PASS（静态范围）|r6/evidence/fix_verifier.json|

## 尚未完成

- **NOT_RUN**：全部原生场景（等待驱动沙箱外执行 harness）；T04–T15/T31/T35/U01/U03/U04/U05/U07 动态验证同。
- **BLOCKED（沿用）**：跨进程真原子互斥（HOST_PRIMITIVE_BLOCKED，需宿主 fs 原语）；type/key 输入通道（宿主 unknown action，M3_REVIEW_r8 实证）；真并发同盘双上下文通道（harness 逐场新盘顺序启动）。
- **前置挂账不修**：M3 D-M3-01 渲染路径（B-M4-01 的渲染验证子项因此 NOT_RUN）、M2 D-M2-01..07。
- 真并发"两独立上下文同盘仅一成功"动态证据无法在本 harness 结构下产生，源码层 owner 复核只缩小窗口。

## 交接

- 候选：`runtime/optimization/2026-10-09/M4/r6/CANDIDATE.json`（candidate_id=M4-r6-worktree，base=M4-r5-worktree，base 源 SHA 与 diff 可定位）。
- 静态证据：`M4/r6/evidence/fix_verifier.json`（14/14）、`r5-to-r6.diff`、base 快照、`GATES.before-build-r6.json`。
- 离线 store 证据：`M4/native/build_r6/offline-store-evidence.json`（digest=`d34b1073…`，anchor=`d3417e12…`，两把私钥已删）。
- 原生请求：`M4/native/REQUEST_build_r6.json`；驱动执行后审查方可回读 `M4/native-runs/build_r6_*/`。
- 实际测试命令：`python3 runtime/optimization/2026-10-09/M4/r6/scripts/m4_r6_fix_verifier.py`（退出码 0）。
- GATES.json M4 = **READY_FOR_REVIEW**（编码方不给自己 PASS）；最终判定等独立 Review。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
