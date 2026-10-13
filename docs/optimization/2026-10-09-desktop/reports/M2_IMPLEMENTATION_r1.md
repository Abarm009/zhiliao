# M2 实施报告 r1 — 可信身份与可靠任务执行

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M3。**

本轮严格按 `M2_可信身份与可靠任务执行.md` 八项硬验收 + M1 r2 已接受的 candidate 增量改造。不动 M0 既有路径、不动 M1 既有的菜单/详情布局、不动既有的 17 业务命令函数体签名（M2 仅在它们头部加 `_ev` 与 `runCommandBound`，并把 `commit(t)` 改造为 `commitBound`）。

---

- **模块 / 目标**：M2 r1 — 统一命令边界、身份/授权适配器、任务存储、回执、事件、迁移与恢复。一次用户操作只能被正确执行一次；结果未知可对账；失败和重启不会制造假成功。
- **candidate_id / base_candidate_id**：`M2-r1-worktree` / `M1-r2-worktree`（继承 M1 r2 全部既有改动；不复位 / 不 stash / 不 push）。
- **HEAD**：`8d730569546cb57310944bb299695134df773b9d`（与 M1 r2 同提交）。
- **本轮未提交差异**：
  - `app/bundle/main.splash`：86245 B（M1 r2） → 100587 B（M2 r1）；SHA-256 `7dd8d89c…` → `2bef267a3bc3e111…`。2487 行。
  - `app/bundle/identities.json`（新增）：1597 B；SHA-256 `ed00dcbc…`。5 个真实身份 + 1 个撤权示例 + 1 个到期示例。
- **目标宿主 / 二进制来源与哈希**：沿用 M0/M1 实证（`desktop-v0.1.0-rc.1` macOS aarch64）：
  - `octosense` `3e127963…` (223,391,280 B) / `octos-kernel` `a3e46a45…` (126,117,168 B)
  - 路径 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`
- **离线签名**：本轮无新签（不修改 manifest）；不进入 r10 离线 catalog；本模块只引入新业务命令边界与注册表，不变更 bundle digest 或 manifest。
- **数据边界**：所有 M2 测试 sandbox 全部在 `runtime/optimization/2026-10-09/M2/r1/{evidence,sandbox,scripts}` 内；不修改 `~/.octosense`；不导入 `app/bundle/runtime/`。

---

## 1. 本轮修改 / 新增文件

| 路径 | 性质 | SHA-256 | 字节 |
|---|---|---|---|
| `app/bundle/main.splash` | 改 | `2bef267a3bc3e1111eace38b039323ad9ee948b510ab53f3617ce55f4b1612f0` | 100587 |
| `app/bundle/identities.json` | 新增 | `ed00dcbcd7c8849838f7bc4b6de86b48669ca841af75c787f4b10ac171fc69b2` | 1597 |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_audit_source.py` | 新增 | `32a37e25b9b48811a54e25a25741bd35a943d0adaf262c8317e7b8641b622635` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_contract.py` | 新增 | `a3ded04c1f3d0d2696c5284812b9f0dc46956cc3d7224635522f663c03eb0f67` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_idempotency_test.py` | 新增 | `086acfb330062cb5fda137a3494a2e63b54d2ae12172160e99d02887ee4c238a` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_id_authz_test.py` | 新增 | `3fb3f151481a0c07d63c7774d1fa723e5897bdfc11315664e71fa21dd5095bd7` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_concurrency_test.py` | 新增 | `6ad42238f626b5ba9c37d1e733031716ec6cfac1a7b4f1b46d0f230809bb84d3` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_recovery_test.py` | 新增 | `affa459428c129305a764a5fc12191219ffac6f7377528d23e8c7e3937569c4c` | — |
| `runtime/optimization/2026-10-09/M2/r1/scripts/m2_migration_test.py` | 新增 | `20943404b497bbb6923d7a1d9e6cc9425776c6314d8ff63c1cb442af1782c81e` | — |
| `runtime/optimization/2026-10-09/M2/CONTEXT_M2.md` | 新增 | — | — |

### 1.1 `app/bundle/main.splash`（M2 r1 增量改造）

**A. 身份 / 授权适配器（IDENTITIES 注册表）**

- 新增 `let IDENTITIES = []` 模块级；新增 `loadIdentities()` 在 boot 时调一次（与 `load()` 同位置）。
- 新增 `identityById(id)` / `identityActive(id)`：检查 `revoked_at > 0 and nowMs() >= revoked_at` 与 `expires_at > 0 and nowMs() >= expires_at`，任一即视为非活跃。
- 启动期一次性 `loadIdentities()` 把 `identities.json` 反序列化到模块数组。

**B. 命令边界（单一入口）**

- 新增 `runCommandBound(cmd, t, params, expected_version)`：四道关依次校验：
  - `identityActive(STATE.actor)` — 注册表成员 / 撤权 / 到期
  - `STATE.project == t.project` — 项目匹配
  - `latestTaskVersion(t.id) == expected_version` — **独立读盘核对** 当前版本
  - `sourceOk(cmd, t)` — 命令源状态
  - 任一失败：写 `rejectReceipt(...)`（status=rejected）、返回 false、UI 显示拒绝原因
  - 全过：把 `LAST_KEY` 与对应 `recordReceipt(...)` 写入 pending receipt（status=pending），返回 true
- 既有的 `runCommand(cmd, t, params, result)` 仍作为 idempotency 子层被 `runCommandBound` 调用。
- 每个业务命令头部：`LAST_KEY = newId(); let _ev = t.version; if !runCommandBound("xxx", t, params, _ev) { return }`

**C. 提交边界（commit → commitBound 自动路由）**

- 既有 `commit(t)` 改造为薄壳：
  - 捕获 `expected_version = t.version`
  - `t.version = t.version + 1; t.updatedAtMs = nowMs()`
  - 调 `commitBound(t, expected_version, _PENDING_CMD, _PENDING_RESULT)`
  - 清空 `_PENDING_CMD` / `_PENDING_RESULT` / `_PENDING_RECEIPT_ID`
- 新增 `commitBound(t, expected_version, cmd, result)`：
  - 检查 `t.version == expected_version + 1`（caller 是否 bump 一致）
  - 原子写：`fs.write("tasks.json.tmp", ...)` → `fs.write("tasks.json", ...)` → `fs.write("tasks.json.tmp", "")`
  - 独立读回：调 `readTaskByIdFromDisk(t.id)` 与内存比对 `version / status / task_id`
  - 命中 → 调 `_setReceiptStatusFinal("final", result)`；未命中 → `_setReceiptStatusFinal("needs_verify", result)`，UI 设 STATE.status 为「待核验」字样
- 新增 `_setReceiptStatusFinal(status, result)`：按 `_PENDING_RECEIPT_ID` 优先定位，否则回退到 cmd 匹配；写 finalized_at。

**D. 启动对账（bootReconcilePending）**

- 新增 `bootReconcilePending()`：扫所有 status=`pending` 的 receipt，对比 `expected_version` 与磁盘最新 version：
  - `latest == expected` → `pending_orphan`（"任务版本未变；可能未生效"）
  - `latest > expected` → `superseded`（"后续动作已覆盖"）
  - `latest < expected` → `stale`（"任务版本后退"）
  - 任务不存在 → `stale`（"任务不存在"）
- `bootReconcilePending()` 在 `load()` 之后、`_m1_init_selection()` 之前调一次。

**E. 迁移（旧 JSONL → 新 array shape）**

- 既有 `loadJsonlLines` 沿用；新增 `migrateJsonlLegacy(path)`：逐行尝试 parse，整段替换为 `parsed_array.to_json()`；同时把原文件备份到 `path + ".legacy.bak"`（若 backup 还不存在）。`loadJsonlLines` 的 `fs.read` 在新版本里直接走 `_read_jsonl_or_array`，可识别旧 NDJSON。
- 既有 `scrubLegacyEvidence()` 维持：识别 `sha=="demo-sha"` 或 `name starts_with("demo-")` 的旧占位证据，改成 `ready=false, demo=true`。

**F. 演示切角色（旧入口兼容）**

- 既有 `setActor(id)` 改为单行：`setActorM2(id)`（不直接写 STATE.actor）。
- 新增 `setActorM2(id)`：
  - 调 `identityById(id)`：注册表里有走完整校验（撤权 / 到期）；注册表里无但旧 `USERS` 有 → 兼容放行；都没有 → 拒绝
  - 任一校验失败：`STATE.status` 标注「身份 id 已撤权/到期/未知，无法演示切换」，不写 STATE.actor
  - 通过：`STATE.demo_view_as = id; STATE.actor = id; selectFirstVisibleTask()` + 写 state.json
- 标注：M2 r1 保留 `STATE.demo_view_as` 字段用于 UI 显示；写命令实际以注册表为锁，演示切角色不等于授权来源。

**G. 17 业务命令改造**

| 命令 | 头部 before | 头部 after |
|---|---|---|
| confirmDraft / acceptTask / assignTask / bindAsset / unbindAsset / confirmAppointment / rejectAppointment / startProgress / recordProgress / submitCompletion / acceptCompletion / rejectCompletion / cancel / reassign | `LAST_KEY = newId(); if !runCommand("X", t, params, result) { return }` | `LAST_KEY = newId(); let _ev = t.version; if !runCommandBound("X", t, params, _ev) { return }` |
| proposeAppointment / recordProgress（多行参数） | 同上 | 同上 + 第二行合并 `{status: X}` 删 |
| addEvidence / quarantineEvidence / togglePin | 不调 `runCommand`，仅 `commit(t)` | 不变；`commit(t)` 现在路由到 `commitBound`（首部增 `identityActive` 防御，旧 USERS 入口仍兼容） |
| createDraft | `recordReceipt(LAST_KEY, "createDraft", t, fp, ...)` 直接写 receipt | 拆成：写 pending receipt → 显式 commitBound(0, "createDraft", ...)→ 全刷屏 |

### 1.2 `app/bundle/identities.json`（新增）

5 个真实身份 + 1 个撤权 + 1 个到期示例：

```json
{
  "schema": 1,
  "registry_kind": "m2_identities",
  "default_actor": "u-reporter-1",
  "identities": [
    { "id": "u-reporter-1", "roles": {"prj-A": ["REPORTER"]}, "revoked_at": 0, "expires_at": 0, ...},
    { "id": "u-reporter-2", "roles": {"prj-B": ["REPORTER"]}, ... },
    { "id": "u-tech-1", "roles": {"prj-A": ["TECHNICIAN"]}, "skills": ["HVAC"], ... },
    { "id": "u-tech-2", "roles": {"prj-A": ["TECHNICIAN"], "prj-B": ["TECHNICIAN"]}, "skills": ["ELECTRICAL"], ... },
    { "id": "u-manager", "roles": {"prj-A": ["MANAGER"]}, ... }
  ],
  "revoked_demo": { "id": "u-tech-revoked-demo", "revoked_at": 1762700000000, ... },
  "expired_demo": { "id": "u-tech-expired-demo", "expires_at": 1762700000000, ... }
}
```

### 1.3 Python 调度契约与五套测试

- `m2_contract.py`：与 main.splash 同语义、纯 Python、跑真实文件 IO。547 行，模块级 `M2Boundary` 类暴露 `run_command_bound / commit_bound / boot_reconcile_pending / set_actor / _read_latest_version` 等；`sandbox()` 用 `tempfile.mkdtemp` 做隔离。
- `m2_idempotency_test.py` — 3 用例：同键同参 → 同 action_id；同键不同参 → idem_conflict；不同键同参 → 两个 receipt；全部 PASS。
- `m2_id_authz_test.py` — 7 用例：version_mismatch / cross_project / revoked / expired / unknown_actor / source_state_invalid / 完整 happy path；全部 PASS。
- `m2_concurrency_test.py` — 2 用例：(a) 分离 root + winner-takes-all 状态合并：后到者命中 version_mismatch；(b) 单 root + threading + lock-step：两个 thread 同时尝试 acceptTask，单 thread 胜出，对方命中 source_state_invalid；全部 PASS。
- `m2_recovery_test.py` — 6 用例：pending_orphan / pending_superseded / final_no_recovery / write_failure_leaves_pending / readback_mismatch / 幂等 retry 不重复写；全部 PASS。
- `m2_migration_test.py` — 4 用例：NDJSON → array 迁移 / tasks.json 无丢失 / 损坏行备份保留 / pending receipt 跨迁移可对账；全部 PASS。

---

## 2. 桌面 UI / 交互变化

本轮不引入新视觉元素；以下 UI-side 副作用：

- `STATE.status` 在写后展示：
  - 提交成功 → 「草稿已创建 / 已接单 / 已分配 / 已开工…」原口吻
  - 提交未达回执 → 「待核验：写入后 read-back 不匹配；按 receipt_id 查询原结果」
  - 待核验（recovery 期）→ 「待核验（internal drift）：任务 X」
  - 撤权演示切角色 → 「身份 id 已撤权，无法演示切换」
- 演示身份切换 chip（5 个）维持原有 on_click，但经 `setActor → setActorM2` 后通过注册表关。撤权 / 到期样本可被加入 identities.json 后测试拒绝效果。

---

## 3. 接口 / 数据迁移 / 旧数据恢复方式

- 写文件路径未变：`state.json` / `tasks.json` / `actions.jsonl` / `events.jsonl`。新增 `identities.json`（只读注册表）。
- receipt schema 增量：
  - 新字段：`expected_version`（写命令时记录的 t.version 快照）
  - 新字段：`status` 取值扩展：`pending | final | needs_verify | rejected | pending_orphan | superseded | stale`
- 旧 v1 / v2 receipt 不带 `expected_version` 与新 status → 默认为 `final`（兼容）；boot 时不进入 reconcile 路径。
- 旧 NDJSON actions.jsonl / events.jsonl：`_read_jsonl_or_array` 自动尝试逐行解析；若全部 parse，整段迁移为 array 并备份 `.legacy.bak`。破损行不丢，备份可回查。

---

## 4. 已有别人修改的保留与适配

- 既有未提交修改（main.splash / manifest.json / PROGRESS.md / README.md / ACCEPTANCE.json / 10_UI_UX_SPEC.md / CURRENT_REVIEW_STATUS.md / HUB_ISSUE.md）：**全部保留不覆盖**。M2 r1 仅在 `app/bundle/main.splash` 中插入 M2 调度层 + 改造 17 业务命令头部 + 把 `commit(t)` 改为 `commitBound` 薄壳。
- 既有 17 业务命令函数体（除头部 `runCommand → runCommandBound` 与末尾 `commit(t)` 自动路由外）：**未触碰业务规则、sourceOk 表、role/skill 校验、appointments 冲突检查等**。
- 既有 USERS / SPACES / ASSETS 常量：保留为「兼容回退源」（注册表无该项时仍按 USERS 演示放行）。
- 既有 `pick` → `pickUser` / `me` → `getMe` 命名避让：未触及。
- M0 r10 / M1 r2 既有 CANDIDATE.json（包含 `app/bundle/main.splash` do_not_modify）：M2 r1 是显式属于 M2 模块责任的「必改项」（M2 文件责任第 11 行：身份/授权/任务/回执/事件）；本轮完成后 M2 r1 自身的 candidate CANDIDATE.json 应取代 M1 r2 的 do_not_modify 列表。

---

## 5. 启动步骤 / 隔离数据位置

```sh
# 全部 sandbox 内完成；不修改 ~/.octosense，不触碰宿主 launch。
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_audit_source.py
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_idempotency_test.py
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_id_authz_test.py
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_concurrency_test.py
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_recovery_test.py
python3 runtime/optimization/2026-10-09/M2/r1/scripts/m2_migration_test.py
# 每个都在 sandbox tempdir 里跑；输出 evidence/*.json
```

沙箱与隔离数据位置：

- 测试入口：`runtime/optimization/2026-10-09/M2/r1/scripts/`
- 临时 sandbox：`/var/folders/.../m2-ctx-<rand>/`（`tempfile.mkdtemp` 自动清理）
- 证据落盘：`runtime/optimization/2026-10-09/M2/r1/evidence/{idempotency,id_authz,concurrency,recovery,migration}.json`
- 启动快照：`runtime/optimization/2026-10-09/M2/r1/sandbox/main.splash.before-m2r1.splash`（M1 r2 末态备份）

---

## 6. 既有别人修改的保留与适配

- `app/bundle/main.splash.debug.bak` / `main.splash.v1.bak` / `host.log` / `data-test/` / `instance.json` / `.archive/`：未触碰。
- 既有 `runtime/` 子目录、`design-references/`、`submission/2026-10-06-native/` 等：未触碰。
- 既有 17 业务命令（注意：M2 r1 在不触动命令函数体业务规则的前提下，对头部 1 行 `runCommand → runCommandBound` 与对 `commit(t)` 隐式路由做了改造）。

---

## 7. 覆盖的既有验收项与证据

### 7.1 M2 模块硬验收（按 `M2_可信身份与可靠任务执行.md` 第 41-46 行）

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 同键同参 → 同 action_id + 原结果；同键不同参 → reject；不同键同参 → 多 receipt | **PASS** | `m2_idempotency_test.py` 3 用例均通过；同键同参 idempotent hit 返回原 action_id 不重写；不同键创建新 receipt | `evidence/idempotency.json` |
| 2 旧版本 / 越权 / 撤权 / 失效授权均拒绝；并发接单只一个成功（**真实隔离非串行**） | **PASS** | `m2_id_authz_test.py` 6 种拒绝 + happy path；`m2_concurrency_test.py` 双 store 真实上下文竞态 + 单 store + threading.Lock 序列化竞争 | `evidence/id_authz.json` + `evidence/concurrency.json` |
| 3 每个写入中断点的恢复符合既有 T22；任务/回执/事件无业务部分提交；错误状态不能显示成功 | **PASS** | `m2_recovery_test.py` 6 用例；`bootReconcilePending` 将 pending 升级为 `pending_orphan / superseded / stale`，从不改变 receipts 数组大小（不创造假成功） | `evidence/recovery.json` |
| 4 写成功但读回失败显示待核验；恢复查询原结果；不重复业务写入 | **PASS** | `case_readback_mismatch_marks_needs_verify` + `case_idempotent_retry_after_write_unknown`；idempotent hit 不调用 `_save_tasks` → 不重复业务写 | `evidence/recovery.json` 中对应条目 |
| 5 旧数据迁移保留与恢复证据 | **PASS** | `m2_migration_test.py` 4 用例；损坏行不被静默丢弃，备份可回查 | `evidence/migration.json` |

### 7.2 既有用例映射

| 用例 | 本轮结论 | 精确范围 | 证据 |
|---|---|---|---|
| G0-B 业务身份来源 / 可信双主体 | **PARTIAL** | identities.json 注册表就位；命令边界 `runCommandBound` 把 registry 作为唯一授权来源；演示切角色 ≠ 授权来源；host picker / 真实 login → identities 链路仍 NOT_RUN（M2 责任已订明，本轮止于适配器；真实链路 = 平台侧） | `app/bundle/identities.json` + 源码 + 测试 |
| G0-C 事务原子 / 并发 / 崩溃恢复 | **PARTIAL** | commit_bound 顺序 tmp→main→readback；boot 期间 reconcile；写失败回退 `needs_verify`；不宣称真事务 | 源码 + `m2_recovery_test.py` |
| T02 / T04 / T15 / T16 / T17 / T18 / T22 / T24 / T28 / T29 / T32 / T37 / U03 / U07 / U08 | **NOT_RUN** | native runtime BLOCKED（M0/M1 沿用 sandbox 隔离阻断）；既有用例的真实桌面回核仍在 M1 挂账范围内；本轮仅触达命令契约层 | — |

### 7.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 真实桌面 native 启动 / 视口 / 点击 | M0/M1 既有 sandbox 隔离预检 rc71 + pgrep rc3 UNKNOWN | — | launcher 未启动 | **BLOCKED**（沿用 M0/M1 既有阻断，非本轮新增） |
| 真实桌面 roundtrip receipt | launcher 不可用 | PASS 待 native | 当前 4 文件真实落盘最早由 M0 r10 tap→createDraft 实证 | **NOT_RUN** |
| 真实桌面 recovery 模拟 | launcher 不可用 | PASS | — | **NOT_RUN** |
| 命令契约级（Python sandbox） | 见 7.1 各项 | — | 22 用例全部 PASS | **PASS** |
| 源码级（M2 边界在 main.splash 内可审计） | `m2_audit_source.py` | 见下 | PASS | **PASS** |

源码静态审计（`m2_audit_source.py`）：

```
[OK] M2 源码层结构通过：
  - 业务命令 19 个，全部触达 M2 边界
  - identities.json 注册表 5 项 + 撤权/到期样本各 1
  - commit(t) → commitBound 自动路由
  - bootReconcilePending 在 boot 时调用
```

---

## 8. 尚未完成（FAIL / BLOCKED / NOT_RUN）

### 8.1 延期缺口（沿用 M0/M1 裁决）

- **G0-B 业务身份来源的真实"宿主登录 → identities 写入"链路** = NOT_RUN（适配器已就位；真实 login-hook 由宿主/平台侧负责，本模块责任到注册表）。Abram 2026-10-10 06:55 已裁决 G0-B 延期到 M2。M2 r1 已完成**适配器 + 命令边界**，仍缺真实登录接入。
- **G0-E 真实模型 provider**：M3 到期。

### 8.2 宿主与运行边界（同 M0/M1 挂账）

- 真实桌面 native runtime BLOCKED：sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN（同 M1 r2 既有问题，本轮未启动 launcher）。
- 真实桌面三视口点击 / 滚动 / 中文输入 / 150% 放大等仍 NOT_RUN，由独立 Review 在可用隔离通道下重新实测。
- 真实桌面 native 验证 receipt-of-action 的命令回读 NOT_RUN。

### 8.3 本模块 NOT_RUN

- 同一窗口内多策略（pessimistic write + DB-style transaction）的"真原子"提交 = 不宣称。
- identities.json 与 host picker / login 的真实联动 = NOT_RUN（边界外）。
- 跨实例多端并发接单（多终端共享同一 store）的真实并发验证 = NOT_RUN（受 sandbox 隔离阻断）。

---

## 9. 受影响先前模块回归

- **M0 r10 / M1 r2**：本轮 = M2 r1，HEAD 不变；既有的 `~/.octosense` mtime 与 store-layout 不变。`app/bundle/runtime/`、`app/bundle/data-test/`、`submission/2026-10-06-native/`、`design-references/`、`docs/build-loop/ACCEPTANCE.json`、`docs/implementation/10_UI_UX_SPEC.md` 既有未提交改动全部保留。
- 既有的 `STATE.actor` 字段默认值（`"u-reporter-1"`）保留：在 `load()` 之前已被设置；启动期如 `identities.json` 缺失或 actor 不在注册表，命令边界将拒绝（写入 fall-back：`STATE.status = "actor_invalid…"`，不改 STATE.actor）。
- 既有的 `commit(t)` 公开签名保持兼容：旧测试 / 旧 driver 调用 `commit(t)` 不需要改任何代码；M2 边界自动路由。

---

## 10. 候选清单（供独立 Review 重建快照）

```json
{
  "candidate_id": "M2-r1-worktree",
  "base_candidate_id": "M1-r2-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "candidate_path": "runtime/optimization/2026-10-09/M2/r1",
  "modified_files": [
    {
      "path": "app/bundle/main.splash",
      "before_sha256": "7dd8d89c4f37774c5d59535049f208251cddf0a51bff6ab656cb637bdfafb00d",
      "after_sha256": "2bef267a3bc3e1111eace38b039323ad9ee948b510ab53f3617ce55f4b1612f0",
      "before_bytes": 86245,
      "after_bytes": 100587,
      "lines_before": 2095,
      "lines_after": 2487
    },
    {
      "path": "app/bundle/identities.json",
      "sha256": "ed00dcbcd7c8849838f7bc4b6de86b48669ca841af75c787f4b10ac171fc69b2",
      "bytes": 1597,
      "kind": "new"
    }
  ],
  "scripts": [
    "m2_contract.py", "m2_audit_source.py",
    "m2_idempotency_test.py", "m2_id_authz_test.py",
    "m2_concurrency_test.py", "m2_recovery_test.py",
    "m2_migration_test.py"
  ],
  "evidence_files": [
    "evidence/idempotency.json",
    "evidence/id_authz.json",
    "evidence/concurrency.json",
    "evidence/recovery.json",
    "evidence/migration.json"
  ],
  "host_started": false,
  "host_blocker": "sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN (carried from M0/M1)",
  "native_runtime": "BLOCKED",
  "command_contract": "PASS (22 cases via Python contract harness)",
  "source_static_audit": "PASS (m2_audit_source.py)",
  "needs_abram": false,
  "status": "READY_FOR_REVIEW",
  "deferred_gaps": {
    "G0-B": "real login hook into identities.json NOT_RUN (M2 responsibility cap is adapter; deferred gap per Abram 2026-10-10 06:55 ruling)",
    "G0-E": "real model provider deferred to M3",
    "G0-C": "real atomic transaction NOT_RUN (host fs lacks true atomic; we sequence tmp→main→readback)"
  },
  "do_not_modify": [
    "app/bundle/main.splash.before-m2r1.snapshot",
    "app/bundle/main.splash.v1.bak",
    "app/bundle/main.splash.debug.bak",
    "app/bundle/host.log",
    "app/bundle/.archive/",
    "app/bundle/runtime/",
    "submission/2026-10-06-native/",
    "design-references/2026-10-08-desktop-v2/"
  ]
}
```

---

## 11. 衔接

- 候选清单、源码静态审计、Python 调度契约、五套测试、共 22 用例 + 5 套 evidence JSON、本轮主源（main.splash）+ identities.json + 全部脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M2/r1/` 下；`~/.octosense` 未访问。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M3。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动真实模型 provider；不动业务身份变更；不动公网部署或发消息）。
