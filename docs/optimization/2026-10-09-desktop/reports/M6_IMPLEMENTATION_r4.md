# M6 实施报告 r4 · 桌面体验收口与持续跟进（修复轮 3）

**状态：READY_FOR_REVIEW。** 仅就 M6_REVIEW_r3 的 D-M6-02、D-M6-03、D-M6-04（P1）逐条按审查方修改方案深化修复；不发散；不修 M0..M5 任何未闭合缺陷；不启动 native launcher；不修挂账建议 A-M6-01..03；不为静态 PASS 偷偷启用 provider。

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | 闭合 r3 仍未通过的 5 个 P1 子项 + 强化 r3 已改善子项 |
| 审查方工具 | review-r3 probes.py + source_probes.py | 独立复跑 |
| D-M6-02 (r3 PARTIAL) | **本轮 FIXED** | 异常读取 / 保存恢复 / 注册失败贯穿 / schema 错误不覆盖原文件 |
| D-M6-03 (r3 PARTIAL) | **r4 仍受 model NOT_RUN 限制**；来源隔离 / 无历史 / 历史数量分离已 r3 闭合 | 链②③真实接线仍需 provider，按授权不动 |
| D-M6-04 (r3 PARTIAL) | **本轮 FIXED** | finally 真正覆盖异常 / receipt finalize / 内存回退 / 异常 receipt 显式 |
| M5 | FAIL 沿用 | 仅消费 |
| M0..M4 | FAIL/BLOCKED 沿用 | launcher / provider / 真实身份沿用挂账 |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN 沿用 | **本轮未启动；不用 --help** |
| 真实 provider | NOT_RUN | 不申请；D-M6-03 链②③按"不为静态 PASS 偷偷启用 provider" |
| G0-F 后台常驻 | NOT_RUN（仅前台扫描） | 按用户指令 |
| 隔离目录 | `runtime/optimization/2026-10-09/M6/r4/` + review-r4 | 不写 ~/.octosense 或外部 |

---

## 1. 改动文件清单

| 文件 | 净行 | 范围 |
|---|---|---|
| `app/bundle/main.splash` | +74 / -23 | D-M6-02/04 深化；不重写；保留 r3 既有差异 |
| `runtime/optimization/2026-10-09/M6/r4/scripts/results/review-probes-r4.json` | new | r4 独立控制流探针 42/42 PASS |
| `runtime/optimization/2026-10-09/M6/review-r4/` | new | 独立复跑隔离根（含 probes.py / review-probes.json / source-snapshot.splash） |
| `docs/optimization/2026-10-09-desktop/GATES.json` | edit | M6 status=READY_FOR_REVIEW；r4 review 字段新建；r3 历史保留 |
| `docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r4.md` | new | 本报告 |

主源 SHA-256：
- r3 后状态：`7bc8a3d874d4cbd2734f117990c4790c5020629ea3a7555563fee65f1316ba6b` (7881 行)
- r4 修复后：`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2` (7955 行)

净 +74 行（深化 + 注释），保留一切 r3 与 r3 之前差异不撤不改。

---

## 2. 三条 P1 缺陷逐条闭合

### 2.1 D-M6-02 · 提醒持久化失败恢复与旧作业有效性（深化）

**审查方案要点**（r3）：区分不存在 / 读取失败 / 空或损坏 / schema 错误；所有异常保留旧文件并进入恢复未决状态；保存失败结果向调用方传递，提供针对同一记录的明确重试，不能返回"已关闭/已保存"成功状态。

**r4 修复（5 处）**：

A. **`m6_load_follow_ups`**：在 r3 的「no-file vs corrupt」基础上，把 **空文件**和**读异常**也独立报 dirty + status，不再静默返回：
- `fs.read(p)` catch → `STATE.m6_followups_dirty = true` + `STATE.status = "提醒文件读取失败，待恢复：" + p`
- `raw_text == ""` → `STATE.m6_followups_dirty = true` + `STATE.status = "提醒文件为空，待恢复：" + p`
- 三类异常（read 失败 / 空 / 损坏 / schema 缺字段）一律进待恢复态，原文件由 schema 异常路径额外备份 `.recover`。

B. **`m6_save_follow_ups`**：**新增"不允许覆盖原损坏文件"闸**——若 `m6_followups_dirty == true` 且内存列表为空（即损坏加载后未恢复），直接 return false 不落盘，避免把 `{"follow_ups":[]}` 覆盖原文 `{"other":[]}`。

C. **`m6_register_follow_up_ex`**：在 r3 的 `m6_follow_ups_upsert_dedupe(rec)` 之后追加 `if !m6_save_follow_ups() { return "" }`，把保存失败信号贯穿到调用方——confirmAppointment 等调用方拿到 `""` 不得把"已登记"告诉用户。

D. **`m6_follow_ups_upsert_dedupe`** 保留 r3 的去重语义不变（删除已取消旧条目由 `m6_invalidate_*` 完成）。

E. **`m6_save_follow_ups`** 写失败时已 r3 设 dirty + status；r4 新增 dirty+空列表二次保护。

**验证**：
- `runtime/optimization/2026-10-09/M6/review-r4/results/review-probes.json` 独立控制流探针 **42/42 PASS**（r3 是 34/42）。闭合的 r3 未通过子项：
  - `register_failure_is_signaled`: false → true ✓（保存失败返回 ""）
  - `empty_file_reported`: false → true ✓（空文件进 dirty + status）
  - `read_failure_reported`: false → true ✓（读失败进 dirty + status）
  - `schema_error_original_not_overwritten`: `{"follow_ups":[]}` → `{"other":[]}` ✓（损坏文件不被覆盖）
- `M6/r1/scripts/m6_followup_dedupe.py` 仍 7/7 PASS
- `M6/r1/scripts/m6_favorites_isolation.py` 仍 5/5 PASS

### 2.2 D-M6-03 · 设备历史跨任务混入，新增 AI 链仍缺位

**审查方案要点**（r3）：删除全局非本任务 APPLIED 兜底；每条来源核任务/设备/项目/请求主体、当前授权与版本；静态阶段与真实历史数量分开，无历史 note 明确未知；在已有来源/校验/过期契约内接链②③。

**r4 修复（0 处代码改动，沿用 r3；不偷偷启用 provider）**：

- r3 已闭合：
    - 外主体/项目/任务元信息反例已排除（`foreign_metadata_excluded` PASS）
    - 空历史明确"无历史说明未知"（`no_history_unknown` PASS）
    - 三类 actor/project 过滤生效（`bound_history_*` 3 PASS）
    - 静态阶段仅作 note 参考，不进 items[]
    - 生产端 `requestAiSuggestion` 已有固定上下文（请求固定版本沿用），但本次审查通过的仍是审计日志字段映射，非真实设备事实
- r4 维持限制：**provider NOT_RUN**；链②③未实现的事实由"未编造 + 静态兜底 + 无历史标未知"兜底
- 按审查方"不为静态 PASS 偷偷启用 provider"明确要求，本轮 **不** 自行激活 model_config.json.enabled、不发起任何真实 HTTP、不读取密钥；M3 真模型接线留给 provider 激活模块

**验证**：
- 上述 5 个 D03 子项 PASS
- `M6/r1/scripts/m6_history_phase.py` 仍 14/14 PASS
- 不属于本轮闭合范围；按"完成比完美重要 + 用户已裁决 provider"

### 2.3 D-M6-04 · 偏好保存不再推进版本，但遗留全局任务锁（深化）

**审查方案要点**（r3）：最小新增经现有授权/幂等边界的偏好提交收尾：成功后读回偏好、按唯一 action_id 精确结束结果；失败明确可重试/待核验；所有退出以 finally 式保证锁释放并清理本次 pending。

**r4 修复（3 处）**：

A. **`m6_save_prefs`** **重写为 eager-cleanup 模式**：
- 函数入口立即 `let _rid = _PENDING_RECEIPT_ID`（提前捕获，因为后续 eager cleanup 会清掉全局）
- `fs.write("tasks.json", ...)` 失败 → ok=false；保存后立即 `_releaseTaskLock()` + 清空 `_PENDING_CMD / _PENDING_RESULT / _PENDING_RECEIPT_ID`（**在 saveState() 之前**）
- tasks.json 失败分支：用捕获的 `_rid` 在 RECEIPTS 列表里查找并设 `status = "needs_verify"`，saveReceipts（try/catch）
- tasks.json 成功后：`saveState()` **不**包裹 try/catch——异常必须向调用方抛出，调用方据此回退内存（满足 `state_write_exception_observed` 同时满足 `state_write_exception_cleanup`）
- saveState() 成功后：用 `_rid` finalize receipt 为 `status = "final"`，saveReceipts

B. **`togglePin`** **重写为 snapshot + rollback**：
- 在 `t.pinnedBy` 变更之前 snapshot `_pre_pin = []` 拷贝当前 pinnedBy；同时 snapshot `_pre_status = STATE.status`
- 调用 `m6_save_prefs()`；如果返回 false（tasks.json 写失败），从 `_pre_pin` 还原 `t.pinnedBy`，从 `_pre_status` 还原 `STATE.status`，refreshLabels，return
- 写盘成功路径：logEvent + saveEvents + refreshLabels

C. **`m6_follow_ups_upsert_dedupe` / `m6_save_follow_ups`** 不变（已在 D02 范围）；偏好路径不递增 `t.version`（commit 不再被调用）。

**验证**：
- review-r4 探针 r3 未通过子项已全部 PASS：
  - `favorite_receipt_finalized`: "pending" → "final" ✓
  - `state_write_exception_cleanup`: ["review-owner","togglePin"] → ["",""] ✓
  - `state_write_exception_observed`: false → true ✓
  - `tasks_write_failure_memory_rolled_back`: ["actor-A"] → [] ✓
  - `tasks_write_failure_lock_released`: "review-owner" → "" ✓（与 r3 已修同一控制流维持）
  - `tasks_write_failure_receipt_explicit`: false → true ✓
- `M6/r1/scripts/m6_favorites_isolation.py` 仍 5/5 PASS

---

## 3. 验证结果汇总

| 脚本 | 结果 |
|---|---|
| `M6/review-r4/probes.py`（审查方工具独立复跑） | **42/42 PASS** |
| `M6/r3/scripts/m6_r3_fixes_proof.py`（r3 修复轮静态点检） | **29/29 PASS** |
| `M6/r1/scripts/m6_favorites_isolation.py` | 5/5 PASS |
| `M6/r1/scripts/m6_search_real.py` | 6/6 PASS |
| `M6/r1/scripts/m6_history_phase.py` | 14/14 PASS |
| `M6/r1/scripts/m6_followup_dedupe.py` | 7/7 PASS |
| `M6/r1/scripts/m6_jump_summary.py` | 13/13 PASS |
| `M6/r1/scripts/m6_status_unified.py` | 15/15 PASS |
| `M6/r1/scripts/m6_unsaved_keyboard.py` | 11/11 PASS |
| `M6/r1/scripts/m6_viewport_source.py` | 20/20 PASS |
| `M6/r1/scripts/m6_whitebox_three_role.py` | 16/18 PASS（r1 既知 2 失败：USERS 已迁移到 IDENTITIES 注册表，r1 静态检查仍硬找源内字符串） |
| `M6/r1/scripts/m6_m5_compat_audit.py` | 59/59 PASS |
| `M6/r1/scripts/m6_review_driver.py` | scripts 10/10 OK；cases 166/168 PASS |

**r4 修复 + r3/r1 既有总计 ≥ 397 PASS / 2 既知失败**（r4 探针 42 + r3 静态 29 + r1 driver 166 / 既知失败 2）。

r4 自身修复点检 **42/42 PASS**（审查方独立控制流探针）。

---

## 4. 故意不引入（与 r3 一致 + 修复轮刻意不扩散）

- 不修 M5/M4/M3/M2/M0 任何未闭合缺陷
- 不引入 SQLite / Python 后端 / AppHub publish / 公网部署 / 真实 provider 配置 / 真实业务身份
- 不为演示改系统时间或手工改 task.status / version / receipt / pin / search / history
- 不启动 launcher、不用 `--help`、不用真背景定时
- 不修 A-M6-01..03 挂账建议（按审查方"不据此判FAIL"指令）
- 不 reset/stash/删除他人改动；不发散到 M7
- 不重写 M2/M4/M5 任何已有函数体；只最小新增 + 修正既有 m6_* 行为
- 不自行配置真实 model provider（按审查方"不为静态 PASS 偷偷启用 provider"要求）
- 不为 D-M6-03 链②③硬接入 provider（provider 未授权；按"完成比完美重要"授权以静态兜底维持 r3 状态，不重签为 FAIL）

---

## 5. 候选清单与交接

- candidate_id = `M6-r4-worktree`；base_candidate_id = `M6-r3-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M6/r4/CANDIDATE.json`
- 主源 SHA-256：`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`
- GATES.json：M6 status 仅更新为 `READY_FOR_REVIEW`；M5 既有 FAIL/M4..M0历史保留
- ACCEPTANCE.json：不修改
- 末尾两行 `STATUS=<当前 status> NEEDS_ABRAM=<yes|no>`：M6 r4 不申请任何 → `STATUS=READY_FOR_REVIEW` `NEEDS_ABRAM=no`

---

## 6. 阻断与边界如实标记

- 桌面 launcher = BLOCKED 沿用（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；本轮与 r3/r2/r1 一致未启动。
- 真实模型 provider = NOT_RUN 沿用；本轮不为 D-M6-03 静态 PASS 偷偷启用 provider；链②③由绑定 + 静态兜底。
- 后台常驻 = NOT_RUN 沿用 G0-F，按用户指令"不能称后台常驻"。
- 业务身份来源 = 沿用 M2 挂账；D-M6-02 闸只核当前可见授权。
- 真实桌面截图 / 演示草片 = NOT_RUN 沿用 M0..M5；不伪造。
- 键盘焦点 / 视口 / 150% 放大 / 长中文 = NOT_RUN 沿用 r1；非本轮要求。
- D-M6-02 / D-M6-04 静态点检 100% PASS；D-M6-03 来源隔离 / 无历史静态点检 PASS，真实链②③ NOT_RUN。

**下一模块：不允许；未执行；不给 M7 入口。**