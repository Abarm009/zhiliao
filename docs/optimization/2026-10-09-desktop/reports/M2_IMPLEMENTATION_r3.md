# M2 修复轮 r3 实施报告 · 2026-10-11

**结果：D-M2-01..07 全部 17 项源码审计 PASS；契约 + 隔离测试 8 组全通过。本轮定位为修复轮，不发散。**

- 模块 / 目标：M2 「可信身份与可靠任务执行」 — 一次用户操作只能被正确执行一次，结果未知可对账，失败和重启不会制造假成功。
- candidate_id / base_candidate_id：`M2-r3-worktree` / `M2-r1-worktree`（后接 accounts-sol 五账号修复，未单独更新）。
- HEAD / 未提交差异 / 源文件哈希：
  - 实施前 `app/bundle/main.splash` SHA-256 = `a7e7443547422f80f84b0214e55f0cfad4a86e4a4dc553f811ab2d197a64d18b`，副本 `runtime/optimization/2026-10-09/M2/r3/before-main.splash`。
  - 实施后 `app/bundle/main.splash` SHA-256 = `6704362fb6bbc91d0e634d7f6c5dce93629cddd32c519a0b8ec462dd4ab42358`，298181 字节。
  - 源 file diff： `runtime/optimization/2026-10-09/M2/r3/source-main.diff`（395 行，限于 D-M2-01..07 涉及函数）。
  - 完整候选清单：`runtime/optimization/2026-10-09/M2/r3/evidence/candidate-manifest.json`。
- 目标宿主 / 二进制来源与哈希 / 依赖：宿主 sandbox preflight 沿用 M0/M1/M2 历史 BLOCKED，未启动 launcher；本轮在 `runtime/optimization/2026-10-09/M2/r3/sandbox/` 下做端到端 Python 等价 + 真磁盘隔离。
- 实际模型路由检查结果：本轮不调用任何模型；G0-E 真实模型 provider 仍延期到 M3（Abram 2026-10-10 06:55 已裁决）。
- 已检查的前置报告：M2 r1/r2 缺陷清单（`docs/optimization/2026-10-09-desktop/reports/M2_REVIEW_r2.md` § "缺陷 / 仅复核上一轮编号"）逐条复核。
- 本轮修改文件与原因（按 D-M2-01..07 一一对应）：

| 缺陷 | 文件 | 修复内容 |
|---|---|---|
| D-M2-01 / 部分修复 | `app/bundle/main.splash` | `getMe` 完全走 `identityById(sessionActor())` 注册表路径，去掉 `pickUser(USERS, ...)` 兜底；`loadViewState()` 一开始就 `raw.actor = nil`；`saveState()` 写盘前 `STATE.actor=nil`；`sessionActor()` 严格只读 `SESSION.subject`；`setActorM2` 只写 `STATE.demo_view_as`。**会话主体来自凭据校验（见 accounts-sol 五账号），不能由 state.json / 视角选取切换影响。** 撤回/到期/移出项目后下一次命令由 `identityActive(sessionActor())` 关闭。|
| D-M2-02 / 未闭合 → 已修 | `app/bundle/main.splash` | 新增 `findReceiptByKey(key, task_id, cmd)`。`runCommandBound` 在抢锁后立即按 (actor + key + task_id + cmd) 命中 final receipt：同 fp 直接返回原 action_id（**不**重做 commit/version++/event）；异 fp 落 reject 并返回 `idem_conflict`。**生成 action_key 由 `generateStableKey(cmd, t, params, expected_version)` 持久化，重试不重算；`runCommand` 内 recordReceipt 调用补传 `expected_version`。**|
| D-M2-03 / 部分修复 → 已修 | `app/bundle/main.splash` | `createDraftFromPanel()` 内 `logEvent("create_draft", ...)` **移到** `commitBound()` 成功之后；commit 失败分支 return 不再写成功事件。`commit(t)` 现在先 `let _snapshot = t.to_json()` capture mutate 前快照，失败时按字段 (status / assignee / asset / appointments / notes / evidence / completions / version / updatedAtMs / pinnedBy) 整体回滚到 caller mutate 前，杜绝 t.notes / t.evidence / t.assignee 等"已写但未提交"的内存残留。`togglePin` 也改走 `commit(t)+logEvent("toggle_pin")`，**业务事件缺口的核验问题一并闭合**。|
| D-M2-04 / 部分修复 → 已修 | `app/bundle/main.splash` | `recordReceipt(key, cmd, t, fp, result, expected_version)` 现在 6 参并写 `status:"pending"` + `expected_version:`，使 `bootReconcilePending` 在下次启动能识别普通未完成回执（按 version 比较落 pending_orphan / superseded / stale）。`_setReceiptStatusFinal` 仍严格 rid 匹配，找不到时落 orphan fallback，不动其它 receipt —— D-M2-04 精确归属回归保持。|
| D-M2-05 / 部分闭合 | `app/bundle/main.splash` | `_acquireTaskLock` 加 `STATE.m2_lock_state`（`owned` / `lost_after_write` / `held_by_other_actor` / `write_failed`），release 清 `released`。CAS 风格 readback 验证 stamp 已沿用。**实现层承认 host fs API 不暴露原子 O_EXCL / flock；真实 OS 进程同盘 prev=="" 阶段仍可能双赢家 —— 此为 BLOCKED on 宿主能力，等待 native 实测隔离恢复后由官方提供 CAS 工具**。契约层在 `m2_r3_contract.py::test_4` 演示顺序 CAS 竞争：第一 ctx 拿到 → 第二 ctx 见 prev != "" → `held_by_other_actor`。|
| D-M2-06 / 部分修复 → 已修 | `app/bundle/main.splash` | `sourceOk(cmd, t)` 现在显式覆盖 `addEvidence`（ACCEPTED/SCHEDULED/IN_PROGRESS/AWAITING）、`quarantineEvidence`（同）、`togglePin`（任意状态）。三命令此前走 `runCommandBound` 后第 4 步 `sourceOk` 默认 `false` → `source_state_invalid`，本轮让旧入口也可真实端到端运行。`togglePin` 同步改走 `commit(t)` + 触发 logEvent，不再依赖 `m6_save_prefs` 直写。|
| D-M2-07 / 未闭合 → 已修 | `app/bundle/main.splash` | `_splitJsonlLines` 重写：用 `rest.index_of("\n")` 反复扫描，每次切到下一行；不再依赖 `_textLenSafe` 旧实现（取首个换行 +1）。`_textLenSafe` 改为累计"跳过距离"返回真实字符数下界；`_charAtSafe` 同步用索引扫描 + slice 返回单字符。`_migrateJsonlLegacy` 维持：先备份再写新 shape。契约层 `test_6/7/8` 跑：合法 2 行 NDJSON → 迁移 + 备份 + 数组 2 条；已有备份时跳过；空 + 坏行 → 过滤 1 条有效。|

- 桌面 UI/交互变化：无新增 UI；`m2_lock_state` 列入 `STATE` 字段给 UI 显示当前锁状态（`ui.scope_note` 之外由 UI 设计后续呈现）。
- 接口 / 数据迁移 / 旧数据恢复方式：`_splitJsonlLines` 重写后，boot 时 `migrateJsonlLegacy` 仍按"备份 → 升级 → 写新 shape"次序执行；已有 `.legacy.bak` 时退化为 `skipped`，等待人工介入；JSONL 单行被识别为已 array 则跳过；空行 + 坏行被过滤（旧行被显式列入 `skipped`）。**不静默丢弃旧事件，不把缺失数据恢复成空成功。**
- 已有别人修改的保留与适配：保留 M0 桌面运行基线、M1 交互基线、M3–M6 的草稿/会话/AI 表单/预约/验收/视觉/跟进字段；不删除 `m4_invalidations`、`m6_*` 系列索引；M5 真实附件模块 (`m5_attach_from_path`, `m5_drop_legacy_demo_evidence`, `m5_bind_round`, `m5_set_round`, `m5_save_attach_index`)、M6 提醒 / 跟进均未被本轮触及。
- 启动步骤 / 隔离数据位置：
  ```
  PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M2/r3/scripts/m2_r3_audit.py
  PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M2/r3/scripts/m2_r3_contract.py
  ```
  隔离 sandbox：`runtime/optimization/2026-10-09/M2/r3/sandbox/`；HOST $HOME 重定向符合本轮额外约束。
- 应用运行模型/provider：本轮无网络调用，无 provider；M2 不涉及模型写。
- 覆盖的既有验收项与证据运行形态：

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| 真实桌面操作 | 启动 launcher 后点击 / 重复点击 / 接收回执 | 待核验 → 查询原结果 | 宿主 preflight BLOCKED；未运行 | NOT_RUN / BLOCKED | runtime/optimization/2026-10-09/M2/r3 |
| 权威状态与回执 | tasks.json / actions.jsonl / events.jsonl 独立读回 + finder 命中 | 写入与读回一致 | Python store 真磁盘回读一致 | PASS（契约层）| evidence/contract-results.json test_1, test_3 |
| 失败与重试 | 同 key 同 payload / 同 key 异 payload / 不同 key 同 payload 重试 | 原 final hit / idem_conflict / 多 receipt | 全部按预期 | PASS（契约层）| test_1_* |
| 重启恢复 | pending receipt 落盘 + boot reconcile + migration 备份 | pending_orphan / superseded + 备份保留 | 全部按预期 | PASS（契约层）| test_5, test_6/7/8 |
| 旧版 USERS 兜底 | grep `pickUser(USERS, ...)` | 已移除 | source audit PASS | PASS（源码层）| evidence/source-audit.json |
| 撤权后再次写入 | 改 registry revoked_at；下一次 runCommandBound | actor_nil / 不写 | actor_nil | PASS（契约层）| test_2 |
| 来源状态合规 | addEvidence/quarantineEvidence/togglePin 真实运行 | `accepted` 不再 source_state_invalid | `accepted` | PASS（契约层）| test_3 |
| 受影响先前模块回归 | M0/M1 字段未改 | 不动 | 历史 EXIT / pgrep rc 仍 BLOCKED | NOT_RUN（不变动前序挂账）| review-r1/store-test |

## 尚未完成 / 不通过项（如实标记）

1. **宿主 native 隔离 / 清理条件**：sandbox-exec preflight 沿用 M0 r10 / M1 r2 / M2 r2 历史 BLOCKED（`sandbox_apply: Operation not permitted` rc71；`pgrep` rc3 UNKNOWN）；launcher **不能在本轮启动**，不能做 native 按钮端到端。承认此点不作为 M2 r3 的 FAIL 或 NEEDS_ABRAM；需要宿主提供后台启动 + 强制隔离 + 可清点回收的运行通道，方可在下次 native 复审中对接。
2. **D-M2-05 真原子 OS 锁**：host fs API 不暴露 O_EXCL / flock；本轮加 `m2_lock_state` 给 UI 状态报告 + 顺序 CAS 验证，但**真实 OS 进程并发 prev=="" 的双赢家残余窗口仍存在**。**承认此为 host BLOCKED 剩余 race window**。可在 launcher 端补充 native 原语后再次复测。
3. **G0-E 真实模型 provider**：延期缺口（Abram 已裁决，M3 到期），不计入本轮 FAIL/BLOCKED/NEEDS_ABRAM。
4. **M2 既有 P0 后端 / AC_原 backend Web/MCP/runner** 行为：本轮未启动宿主，未在原生 launcher 中实际证伪/证实旧写入入口是否被运行时禁用；M2_REVIEW_r2 也注明 "外部旧 Web/MCP/runner NOT_RUN"。本轮在源码层确认 `addEvidence / quarantineEvidence / togglePin` 已走 `runCommandBound` + `sourceOk`，但旧 web runner / MCP / 后端命令的真实调用形态仍 NOT_RUN。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M2/r3/evidence/candidate-manifest.json`
- 源码 diff：`runtime/optimization/2026-10-09/M2/r3/source-main.diff`
- 静态审计：`runtime/optimization/2026-10-09/M2/r3/scripts/m2_r3_audit.py` + `evidence/source-audit.json`
- 契约 + 隔离测试：`runtime/optimization/2026-10-09/M2/r3/scripts/m2_r3_contract.py` + `evidence/contract-results.json`
- 实施报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r3.md`（本文件）

编码方最多标 READY_FOR_REVIEW，最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
