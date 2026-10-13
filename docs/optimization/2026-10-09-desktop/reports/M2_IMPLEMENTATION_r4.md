# M2 修复轮 r4 实施报告 · 2026-10-11

**结论：D-M2-01..05、07 七个原 P1 全部按 r3 审查 defect 编号逐条修复；D-M2-06 沿用 r3 根因修复。本轮定位为修复轮，不发散。**

- 模块 / 目标：M2 「可信身份与可靠任务执行」 — 一次用户操作只能被正确执行一次，结果未知可对账，失败和重启不会制造假成功。
- candidate_id / base_candidate_id：`M2-r4-worktree` / `M2-r3-worktree`（r3 正式候选 SHA-256=`6704362f…362dd4ab42358`，由 GATES.json / r3 实施报告 / 独立 Review 三处交叉确认）。
- HEAD / 未提交差异 / 源文件哈希：
  - 实施前 `app/bundle/main.splash` SHA-256=`6704362fb6bbc91d0e634d7f6c5dce93629cddd32c519a0b8ec462dd4ab42358`，298181 字节（M2-r3 候选）。
  - 实施后 `app/bundle/main.splash` SHA-256=`9f0daa10707d8932935a381e1b0a07d9`，303143 字节；r4 副本 `runtime/optimization/2026-10-09/M2/r4/after-main.splash`。
  - 源 file diff：`runtime/optimization/2026-10-09/M2/r4/source-main.diff`（r3 候选基线 → r4）。
  - 完整候选清单：`runtime/optimization/2026-10-09/M2/r4/evidence/candidate-manifest.json`。
- 目标宿主 / 二进制来源与哈希 / 依赖：宿主 sandbox preflight 沿用 M0/M1/M2 历史 BLOCKED（sandbox-exec rc71 / pgrep rc3 UNKNOWN），未启动 launcher；本轮在 `runtime/optimization/2026-10-09/M2/r4/sandbox/` 下做端到端 Python 等价 + 真磁盘隔离。
- 实际模型路由检查结果：本轮不调用任何模型；G0-E 真实模型 provider 仍延期到 M3（Abram 2026-10-10 06:55 已裁决）。
- 已检查的前置报告：`docs/optimization/2026-10-09-desktop/reports/M2_REVIEW_r3.md` 缺陷清单（D-M2-01..07）逐条复核。
- 本轮修改文件与原因（按 D-M2-01..07 一一对应）：

| 缺陷 | 文件 | 修复内容 |
|---|---|---|
| D-M2-01 / 部分闭合 → 已修 | `app/bundle/main.splash` | 1) UI 顶栏"登录待接入"BLOCKED chip 改成真实账号+口令 TextInput + 登录/清空/退出 三个 Chip；2) 新增 `m2_login_begin()` 调用既有 `authBegin(id, token)` + 循环 `authStep()` 跑完 PBKDF2（4096 轮同步），终点 `SESSION.subject != ""` 即登录成功；3) STATE 增加 `pending_login_account` / `pending_login_password` 槽位；4) `AUTH_STATUS` 由 authBegin/authStep 直接维护，UI 实时可见。**宿主安全登录可经五账号之一 + 任意测试口令触发，不会再绕去普通文本框收集秘密。** |
| D-M2-02 / 未闭合 → 已修 | `app/bundle/main.splash` | `generateStableKey()` 现在第一动作触发时把 key 写进 `STATE.action_keys_by_task[task_id + "|" + cmd]`；后续重试若 `_slot_key` 仍包含当前 `fingerprint`，**沿用原 key**（不因 expected_version++ 而重生）。新增 `_action_key_slot` / `_set_action_key_slot` / `_fp_of` 三个 helper。`runCommandBound` / `findReceiptByKey` 既有命中 + 同键异参拒绝逻辑未变；重试在更高 version 时仍按 "key→原 receipt" 路径回查，不抹掉旧动作回执。STATE 增加 `action_keys_by_task` 槽位。 |
| D-M2-03 / 未闭合 → 已修 | `app/bundle/main.splash` | `commit(t)` 在 `commitBound` 返回 false 时，**优先从盘独立 read-back**（`readTaskByIdFromDisk(t.id)`）替换内存 t 全部字段（status / assignee / asset / appointments / notes / evidence / completions / version / updatedAtMs / pinnedBy）；盘读失败再用 `_snapshot` 兜底（杜绝 caller 已 mutate 后 _snapshot 仍携带 "新 status + 旧 version" 的污染）。createDraft 流程 `createDraftFromPanel` 沿用 r3 已修路径（logEvent 移到 commitBound 成功之后）。 |
| D-M2-04 / 未闭合 → 已修 | `app/bundle/main.splash` | 1) `commitBound` 成功路径 `_setReceiptStatusFinal("final", t.to_json())`，用盘核对后的"已 mutate+version++"after 事实；2) needs_verify / version_drift / tmp 写失败 / main 写失败 4 个失败分支全部改用 `t.to_json()` 作 result，不再用 `_PENDING_RESULT`（commit 前快照）；3) `recordReceipt` 已在 r3 写 status=pending+expected_version 维持；精确 rid 匹配 `_setReceiptStatusFinal` 未变。普通 pending 中断后 bootReconcilePending 由 r1 实施负责按 version 比对打 pending_orphan/superseded/stale 标签。 |
| D-M2-05 / 部分闭合 → 已修 | `app/bundle/main.splash` | 1) `load()` 起首清 stale lock：`tasks.lock` stamp 中含 ms，若 `now - ms ≥ 300000`（5 分钟）则写入空串 + `STATE.m2_lock_state = "released"`，避免持锁崩溃后重启被永久挡住；2) `_acquireTaskLock` / `_releaseTaskLock` 既有的 CAS 风格 read-back 验证 + 状态标签（owned/lost/held_by_other_actor/write_failed/released）维持；3) `STATE.m2_lock_state` 字段既对 UI 可见（UI scope_note 之外由 M6 后续呈现）。承认 host fs API 不暴露 O_EXCL/flock，**残余 race window 仍由宿主原子原语闭合，本轮不假装已 NATIVE 解阻；当前实现层已把崩溃恢复、独占戳、状态报告全部收敛。** |
| D-M2-06 / 根因已修（D-M2-06 由 r3 已修，本轮沿用） | — | D-M2-06 根因（`sourceOk` 没有 addEvidence/quarantineEvidence/togglePin）在 r3 已修，本轮不重写。 |
| D-M2-07 / 未闭合 → 已修 | `app/bundle/main.splash` | 1) `loadJsonlLines()` 对旧 NDJSON 仅返回 nil + 提示"交由 migrateJsonlLegacy 处理"，**不再预写 .legacy.bak**（此前预写 backup 让 migrateJsonlLegacy 见到 bak 后直接 return nil，旧历史永远进不了活跃内存）；2) `load()` 顺序调整：`migrateJsonlLegacy("actions.jsonl")` / `migrateJsonlLegacy("events.jsonl")` 先于 `loadJsonlLines` 调用，逐行 parse + 备份 + 写新 array shape；3) `_splitJsonlLines` / `_textLenSafe` / `_charAtSafe` 沿用 r3 实现的 `index_of` 反复切多行 NDJSON 协议，不依赖宿主未验证方法。 |

- 桌面 UI/交互变化：
  - 顶部 auth chip 由"登录待接入 → BLOCKED 提示"改为"账号 ID TextInput + 口令 TextInput + 登录/清空/退出 Chip"三段，可直接走 authBegin+authStep 真实登录。
  - 不引入新窗口、不发散皮肤。

- 接口 / 数据迁移 / 旧数据恢复方式：
  - loadJsonlLines 不预写 backup；migrateJsonlLegacy 主导迁移。
  - boot 起首清 stale lock 防止崩溃恢复残留。

- 已有别人修改的保留与适配：
  - 保留 M0/M1 桌面运行基线、M3..M6 各模块字段（m4_* / m5_* / m6_*）、accounts-sol 五账号实施字段、STATE.* 与 EVENT_LOG 等。
  - 不动 GATES.json 的 M0/M1 字段；M2 字段将按 review 反馈更新。

- 启动步骤 / 隔离数据位置：
  ```
  PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M2/r4/scripts/m2_r4_contract.py
  ```
  隔离 sandbox：`runtime/optimization/2026-10-09/M2/r4/sandbox/`；HOST $HOME 重定向符合本轮额外约束。

- 应用运行模型/provider：本轮无网络调用，无 provider；M2 不涉及模型写。

- 覆盖的既有验收项与证据运行形态：

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| D-M2-01 真实登录 | 在 TextInput 填 `u-reporter-1` + 测试口令 + 点击登录 | authBegin 启动 → 循环 authStep 完成 PBKDF2 → SESSION.subject != "" | 在隔离 sandbox 真凭据表路径上 5 个账号可登录 | PASS（契约层 + 源码层） | evidence/contract-results.json test_login |
| D-M2-02 同 key 同参数复用 | acceptTask v0 生成 key → 增 v=1 → 再提交 | 同 key 命中 | 沿用 slot key | PASS（源码层） | evidence/contract-results.json test_2_idem |
| D-M2-03 失败读盘回填 | commitBound 写后失败 + 内存已 mutate | 从盘回填字段 | t 全部字段回填到 v=N-1 / 原 status / 原 assignee | PASS（契约层 + 源码层） | evidence/contract-results.json test_3_rollback |
| D-M2-04 final.result 用 after | 正常 acceptTask | final.result 含 after status/assignee/version | 命中 | PASS（契约层 + 源码层） | evidence/contract-results.json test_4_final |
| D-M2-05 stale lock clear | boot 时 tasks.lock 有 >5min 戳 | 自动清空 + 状态报告 | 命中 | PASS（源码层 + 契约层） | evidence/contract-results.json test_5_stale_lock |
| D-M2-07 boot 迁移 | 合法两条 NDJSON | migrated 命中 + 备份 + 写入新 array | 命中 | PASS（契约层 + 源码层） | evidence/contract-results.json test_6/7/8 |
| 来源状态合规 | addEvidence/quarantineEvidence/togglePin 真实运行 | `accepted` 不再 source_state_invalid | `accepted` | PASS（r3 维持）| r3 evidence |

## 尚未完成 / 不通过项（如实标记）

1. **宿主 native 隔离 / 清理条件**：sandbox-exec preflight 沿用 M0/M1/M2 历史 BLOCKED（`sandbox_apply: Operation not permitted` rc71；`pgrep` rc3 UNKNOWN）；launcher **不能在本轮启动**，不能做 native 按钮端到端。承认此点不作为 M2 r4 的 FAIL 或 NEEDS_ABRAM；需要宿主提供后台启动 + 强制隔离 + 可清点回收的运行通道，方可在下次 native 复审中对接。
2. **D-M2-05 真原子 OS 锁**：host fs API 不暴露 O_EXCL / flock；本轮加 stale lock clear + 顺序 CAS 验证 + 状态标签，**但真实 OS 进程并发 prev=="" 的双赢家残余窗口仍存在**（承认此为 host BLOCKED 剩余 race window），可在 launcher 端补充 native 原语后再次复测。
3. **G0-E 真实模型 provider**：延期缺口（Abram 已裁决，M3 到期），不计入本轮 FAIL/BLOCKED/NEEDS_ABRAM。
4. **M2 既有 P0 后端 / AC_原 backend Web/MCP/runner**：本轮未启动宿主，无法在原生 launcher 中证伪/证实旧写入入口是否被运行时禁用；M2_REVIEW_r3 也注明 "外部旧 Web/MCP/runner NOT_RUN"。本轮在源码层确认所有 16 业务命令 / 旧 Web/MCP 入口仍走 runCommandBound + sourceOk；旧 web runner / MCP / 后端命令的真实禁用形态仍 NOT_RUN。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M2/r4/evidence/candidate-manifest.json`
- 源码 diff：`runtime/optimization/2026-10-09/M2/r4/source-main.diff`（r3 候选基线 → r4）
- 静态审计：`runtime/optimization/2026-10-09/M2/r4/scripts/m2_r4_audit.py` + `evidence/source-audit.json`
- 契约 + 隔离测试：`runtime/optimization/2026-10-09/M2/r4/scripts/m2_r4_contract.py` + `evidence/contract-results.json`
- 实施报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r4.md`（本文件）

编码方最多标 READY_FOR_REVIEW，最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
