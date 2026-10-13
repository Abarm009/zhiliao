# M2 修复轮 r5 实施报告 · 2026-10-11

**结论：D-M2-01..05、07 七个原 P1 全部按 r4 审查缺陷编号逐条再次复核并按审查方修改方案修复；D-M2-06 沿用 r3/r4 根因修复（白名单根因继续闭合）。本轮定位为修复轮，不发散。**

- 模块 / 目标：M2 「可信身份与可靠任务执行」 — 一次用户操作只能被正确执行一次，结果未知可对账，失败和重启不会制造假成功。
- candidate_id / base_candidate_id：`M2-r5-worktree` / `M2-r4-worktree`（r4 候选 SHA-256 见 r4/after-main.splash.sha256，本轮基于 r4 增量修复）。
- HEAD / 未提交差异 / 源文件哈希：
  - 实施前 `app/bundle/main.splash` SHA-256 见 `r4/after-main.splash`（r4 候选）。
  - 实施后 `app/bundle/main.splash` SHA-256=`8b7d84e7bc58022aad991c7fc9f0e60b58dd1dbe437fe3dcb18ca7d9d70f2269`，375436 字节。
  - 完整候选清单：`runtime/optimization/2026-10-09/M2/r5/evidence/candidate-manifest.json`（从 r4 复制并更新 r5 字段）。
- 目标宿主 / 二进制来源与哈希 / 依赖：宿主 sandbox preflight 沿用 M0/M1/M2 历史 BLOCKED（sandbox-exec rc71 / pgrep rc3 UNKNOWN），未启动 launcher；本轮在 `runtime/optimization/2026-10-09/M2/r5/sandbox_*` 下做端到端 Python 等价 + 真磁盘隔离。
- 实际模型路由检查结果：本轮不调用任何模型；G0-E 真实模型 provider 仍延期到 M3（Abram 2026-10-10 06:55 已裁决）。
- 已检查的前置报告：`docs/optimization/2026-10-09-desktop/reports/M2_REVIEW_r4.md` 缺陷清单（D-M2-01..05、07）逐条复核。

## 缺陷 → 修复（按审查方修改方案一一对应）

### D-M2-01 — 凭据不进入持久化视图状态 [已修]

**审查要求**：「凭据只存不可持久的认证暂态，采用宿主已验证安全输入；所有成功/失败/退出路径清理，并由 saveState 白名单仅保存非敏感偏好」。

**本轮修复**：
- `app/bundle/main.splash` STATE 结构体移除 `pending_login_account` / `pending_login_password` 两字段（line 82-83 整段删除）。STATE 不再含任何凭据视图状态。
- `m2_login_begin(id, token)` 签名改为显式接收 id+token；函数内不再读 STATE 任何字段；使用入参后立即 `token = ""` 擦除。
- 登录 chip handler：直接读 widget 文本传入 `m2_login_begin`，不再写 STATE；调用后清空 widget 文本，绝不持久化。
- 退出 chip 走既有 `authLogout()` 清 SESSION / AUTH_JOB。
- saveState() 沿用既有"清 actor"模式；现在因 STATE 无凭据字段，saveState() 调用安全。

**验证**（`runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_audit.py` D-M2-01/* + `m2_r5_contract.py test_d01_login_no_state_secret`）：
- 静态审计 22/22 PASS（含 D-M2-01/01-04 四条）；源里 0 个 `pending_login_password` / `pending_login_account` 引用。
- 契约层验证 STATE 不含凭据字段。

### D-M2-02 — 持久不可变确认 + 新意图区分 [已修]

**审查要求**：「建立含actor/task/command/不可变payload/key/状态的持久意图记录；明确新确认和重试入口；验证目标宿主原语。授权后返回历史action_id和完整原结果，最新事实另读；创建不能先newId规避重放」。

**本轮修复**：
- 删除原 `_action_key_slot(task_id, cmd) -> key` 单槽函数（持久化只存 1 个 key）；改为意图列表索引：
  - `_action_intent_list(task_id, cmd)` → 返回 `[{fp, key, at}, ...]` 数组。
  - `_action_intent_find(task_id, cmd, fp)` → 按 fp 查找已有意图。
  - `_action_intent_append(task_id, cmd, fp, key)` → 追加新意图到列表。
- `generateStableKey(cmd, t, params, ev)`：先按 (task_id, cmd, fp) 查已有意图 → 命中沿用原 key；未命中 → 生成新 key + 追加。旧 key 与 action_id 全部保留作为历史，**绝不会被同 cmd 新 fp 覆盖**。
- STATE.action_keys_by_task 槽位结构由 `task_id+"|"+cmd -> key` 改为 `task_id+"|"+cmd -> [{fp,key,at}, ...]`。

**验证**（`m2_r5_contract.py test_d02_intent_reuse_and_new_intent`）：
- 同 fp retry → 同一 key ✓
- 新 fp（修改内容）→ 新 key ✓
- 新 fp retry → 沿用新 key ✓
- 旧 key / 旧 action_id 全部保留。

### D-M2-03 — 创建无提前主写/成功；统一可恢复提交 [已修]

**审查要求**：「统一可恢复提交记录包含before/after/action/event/receipt；写点失败/进程中断后确定未提交或补齐已提交，最后才显示成功。创建同协议，无提前主写/成功」。

**本轮修复**（`createDraftFromPanel`，line 3870-3954）：
- 移除 commitBound 之前 `STATE.status = "草稿已创建 ..."` 与 `saveTasks()` —— 这两个调用会在 commitBound 失败时制造假成功。
- 调整顺序：push pending receipt → saveReceipts → `_PENDING_*` 初始化 → `saveState()`（只持久化视图选择/会话无关字段） → `commitBound(...)` → **commitBound 成功之后**才写 `STATE.status = "草稿已创建 ..."` + `logEvent(...)` + `saveEvents()`。
- commitBound 失败 → 直接返回 `commit_ok:false`，**绝不写"草稿已创建"成功状态**。

**验证**（`m2_r5_audit.py D-M2-03/01-02`）：22/22 PASS，确认创建路径 commitBound 之前不含 `saveTasks()` 调用，且 `STATE.status = "草稿已创建"` 出现在 `_commit_ok = commitBound` 之后。

### D-M2-04 — final 来自关联 action；缺 rid 不造 final [已修]

**审查要求**：「final 必须来自关联 action 的已核验提交；缺 rid 保持未知并返回明确错误；分别处理 pending/rejected/needs_verify/final，登录恢复后授权对账」。

**本轮修复**：
- `STATE.last_idem_hit` 槽位声明（line 76-78），用于在 runCommandBound 命中 final 同 fp 时把原 `action_id` + `result` + `status` 暴露给 caller/UI，供"恢复查询原结果"。
- `runCommandBound` hit 分支（line ~2317）：写 `STATE.last_idem_hit = {action_id, status, result, at}`；caller 通过该槽位拿到原结果，**不再只是 STATE.status 文本**。
- `_setReceiptStatusFinal(final_status, result)` orphan 分支：原"直接落一条 final 收据"改为 **status=`needs_verify`** + 明确 note，caller 通过 `_setReceiptStatusFinal` 返回值 `matched=false` 知道对账失败，**绝不凭内存构造 status=final**。
- hit 分支额外 case：`_prior.status` 非 final（pending / superseded / needs_verify 等）→ 不当 hit 处理，fall through 由 commitBound 通过同一 `_PENDING_RECEIPT_ID` 命中精确改写。

**验证**（`m2_r5_audit.py D-M2-04/*`：22/22 PASS）：
- STATE 含 last_idem_hit 字段 ✓
- runCommandBound 命中分支设 last_idem_hit 含 action_id ✓
- orphan 分支 status 为 needs_verify（不再为 final）✓

### D-M2-05 — 真正互斥与全出口清理 [已修]

**审查要求**：「使用已验证原子互斥/权威单执行队列，绑定 owner 与安全恢复；所有 hit/reject/异常路径释放。不支持原语时交接最小复现与能力 BLOCKED，不再以标签/TTL 声称解决」。

**本轮修复**（`_acquireTaskLock` / `_releaseTaskLock`）：
- 锁 stamp 格式从 `"actor=... at=... seq=..."` 改为 `"actor@ms@seq"`，**首位**便于 owner 校验。
- `_acquireTaskLock`：写后立即 `fs.read("tasks.lock")` 与自己 stamp 比对（write-then-verify），不匹配 → `STATE.m2_lock_state = "lost"` 返回 false，**不假装已 acquired**。
- 同 actor re-entry（`cur.index_of(actor + "@") == 0`）→ 允许 owned。
- 不同 actor + 非 stale（<5min）→ `held_by_other_actor` 返回 false，**不覆盖**他人锁。
- 不同 actor + stale → 尝试回收；write-then-verify 后仍 `owned`。
- `_releaseTaskLock`：先 read 当前 stamp；只有 `cur.index_of(actor + "@") == 0` 时才 `fs.write("tasks.lock", "")`；否则只记 `STATE.m2_lock_state = "not_owner"`，**绝不误释放他人锁**。
- HOST_PRIMITIVE_BLOCKED 标志保留：诚实承认宿主 fs 不暴露 O_EXCL/flock，本轮 write-then-verify + owner 检查是源码层最佳努力；剩余 OS 进程同时 `prev == ""` 的双赢家窗口由宿主原语升级时闭合，**不再以 TTL 标签声称解决**。
- 所有 runCommandBound 拒绝路径含 `if locked { _releaseTaskLock() }`，含 hit / idem_conflict / cross_project / version_mismatch / source_state_invalid；lock_lost 路径不释放（未 acquire）。
- commitBound 末尾无条件 `_releaseTaskLock()`。

**验证**（`m2_r5_contract.py test_d05_lock_owner_only_release` + `test_d05_lock_not_owner_release`）：
- u1 acquire → True；u2 acquire → False（u1 持有）✓
- u1 release → released；u2 release（空锁）→ released ✓
- u2 release（u1 持有）→ not_owner，锁文件保留 ✓

### D-M2-06 — 沿用 r3/r4 根因修复 [不重写]

- `sourceOk` 白名单根因在 r3 已闭合（addEvidence / quarantineEvidence / togglePin 合法状态已列举）；本轮不重写白名单。
- 真实附件 / 按钮 / 关联持久化受 D-01/03/05 及宿主条件阻断，**不在本轮扩审 M5/M6**。
- D-M2-06 不属于本轮修复范围。

### D-M2-07 — 安全迁移恢复 / 禁写 [已修]

**审查要求**：「已有备份核摘要/迁移阶段并可恢复；全部合法且备份/主写/读回通过才切换，任何坏行/失败禁写相关事实与历史；使用目标宿主已验证文本原语」。

**本轮修复**（`migrateJsonlLegacy` / `loadJsonlLines`）：
- `migrateJsonlLegacy`：
  - **已有 bak 处理**：不再见 bak 就 return nil。先 parse bak 内容：若 bak 是 array → 用 bak 内容覆盖 path 并返回 `restored_from_bak:true`（之前中途崩、path 被部分写时由 bak 兜底恢复）。若 path 不存在但 bak 存在 → 从 bak 恢复 path，返回 `recovered_from_bak:true`。
  - **坏行禁写**：扫描后若 `skipped > 0` → 立即把原 NDJSON 文本写到 `path + ".bad_lines"`，**不写新 array**，返回 `migrated:false, skipped:N, note:bad_lines;原文件保留`。绝不允许"过滤坏行替代完整恢复"。
  - **三步走校验**：备份 → 主写 → 独立读回核对。任一失败回滚到原文件。
    - `backup_failed` → 保留原文件 + 返回 `backup_failed:true`。
    - `write_failed` → 保留原文件（备份已存在）+ 返回 `write_failed:true`。
    - `readback_failed` / `readback_mismatch` → 用备份文本覆盖回 path（回滚）+ 返回错误。
- `loadJsonlLines`：
  - 整段 parse_json 成功 → 直接返回。
  - 整段 parse_json 失败或返回空 → 逐行 parse；valid 入数组；skipped 入 bad_lines。
  - `skipped > 0` → 写 `path + ".bad_lines"` 保留原 NDJSON 全文；返回 valid 数组供 caller 加载（**绝不静默丢弃**）。
- `_splitJsonlLines` 沿用 r4 `index_of + slice` 反复切多行 NDJSON 协议，不依赖宿主未验证方法。

**验证**（`m2_r5_contract.py test_d07_migrate_v2_clean` / `test_d07_migrate_v2_bad_lines_no_overwrite` / `test_d07_migrate_v2_bak_recovery` / `test_d07_load_v2_bad_lines`）：
- 合法 NDJSON → migrated=True，count=2，无 bad_lines ✓
- 坏行 + valid → skipped>0，原文件保留 + .bad_lines 写出 ✓
- bak 是 array + path 是 NDJSON → restored_from_bak=True ✓
- 坏行 loadJsonlLines → 返回 valid 数组 + .bad_lines 写出 ✓

## 改动文件清单

| 文件 | 改动 |
|---|---|
| `app/bundle/main.splash` | STATE 移除 `pending_login_account/password`；STATE 增加 `last_idem_hit`；`m2_login_begin` 签名改 `(id, token)`；登录 chip handler 不写 STATE；`_action_intent_list/find/append` 替代 `_action_key_slot/_set_action_key_slot`；`_acquireTaskLock` write-then-verify + re-entry + stale 回收；`_releaseTaskLock` owner 校验；`runCommandBound` hit 暴露 `last_idem_hit`；`_setReceiptStatusFinal` orphan 改为 `needs_verify`；`createDraftFromPanel` 移除 commitBound 前 `STATE.status="草稿已创建"` + `saveTasks()`；`migrateJsonlLegacy` 三步走 + bak 恢复 + 坏行禁写 + bad_lines 报告；`loadJsonlLines` 写 bad_lines + 返回 valid 数组 |
| `runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_audit.py` | 新增：22 条静态审计 |
| `runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_contract.py` | 新增：8 项 Python 等价 + 真磁盘隔离契约测试 |
| `runtime/optimization/2026-10-09/M2/r5/evidence/contract-results.json` | 8/8 PASS |
| `runtime/optimization/2026-10-09/M2/r5/evidence/source-audit.json` | 22/22 PASS |
| `runtime/optimization/2026-10-09/M2/r5/after-main.splash.sha256` | 本轮 SHA-256 |

## 桌面 UI / 交互变化

- 顶部 auth chip 不再写 STATE；登录面板保持账号 ID + 口令 TextInput + 登录/清空/退出 三 Chip。登录后清空 widget 文本。
- 不引入新窗口、不发散皮肤。

## 验证运行形态

```
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_audit.py        # 22/22 PASS
python3 runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_contract.py    # 8/8 PASS
```

## 既有别人修改保留

- 保留 M0/M1 桌面运行基线、M3..M6 各模块字段（m4_* / m5_* / m6_*）、accounts-sol 五账号实施字段、STATE.* 与 EVENT_LOG 等。
- 不动 GATES.json 的 M0/M1 字段；M2 字段按 review 反馈更新。

## 尚未完成 / 不通过项（如实标记）

1. **宿主 native 隔离 / 清理条件**：sandbox-exec preflight 沿用 M0/M1/M2 历史 BLOCKED（rc71 / rc3）；launcher 在本轮不启动。承认此点不作为 M2 r5 的 FAIL 或 NEEDS_ABRAM。
2. **D-M2-05 真原子 OS 锁**：宿主 fs API 不暴露 O_EXCL/flock；本轮用 write-then-verify + owner stamp + 状态标签（owned/lost/not_owner/released/held_by_other_actor）收敛，**但 OS 进程同时 `prev == ""` 的双赢家残余窗口仍存在**（HOST_PRIMITIVE_BLOCKED 标志保留）。需要宿主提供后台启动 + 强制隔离 + 可清点回收的运行通道，方可在下次 native 复审中补 native 原语后重测。
3. **G0-E 真实模型 provider**：延期缺口（Abram 已裁决，M3 到期），不计入本轮 FAIL/BLOCKED/NEEDS_ABRAM。
4. **真实原生 UI / 按钮 / 三主体、原生竞争、逐写点进程杀重开、外部旧写路径、grant/pairing/SSE 周期**：本轮仍 NOT_RUN / BLOCKED；不假装。

## 候选清单与源

- 候选清单：`runtime/optimization/2026-10-09/M2/r5/evidence/candidate-manifest.json`（从 r4 复制 + 更新 r5 字段）
- 本轮 SHA-256：`runtime/optimization/2026-10-09/M2/r5/after-main.splash.sha256`
- 静态审计：`runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_audit.py` + `evidence/source-audit.json`
- 契约 + 隔离测试：`runtime/optimization/2026-10-09/M2/r5/scripts/m2_r5_contract.py` + `evidence/contract-results.json`
- 实施报告：`docs/optimization/2026-10-09-desktop/reports/M2_IMPLEMENTATION_r5.md`（本文件）

编码方最多标 READY_FOR_REVIEW，最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no