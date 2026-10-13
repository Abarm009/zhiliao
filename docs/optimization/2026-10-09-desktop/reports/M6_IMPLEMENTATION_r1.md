# M6 实施报告 r1 · 桌面体验收口与持续跟进

**状态：READY_FOR_REVIEW。** 按 Abram 2026-10-10 13:54「完成比完美重要」授权 + 模块指令完成本轮；只跑源码层 + sandbox 内静态点检，未启动 native launcher。

---

## 0. 范围与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| 本轮目标 | M6 硬验收五条 + 全部 26 个 T/U 责任归属 | 严格按模块指令，不发散 |
| M5 | FAIL（D-M5-01..05）沿用 | 仅消费 M5 既有契约 |
| M4 | FAIL（D-M4-01/02/03/04/05）沿用 | 仅消费 runCommandBound / commit / confirmDraft |
| M3 | FAIL（D-M3-01/03/04/05/06）沿用 | 仅消费 editRawText / confirmDraftModelBound |
| M2 | BLOCKED（D-M2-01..07）沿用 | 仅消费 cmd 边界 |
| M1 | FAIL 沿用 | 仅消费 filteredVisibleIndices / togglePin |
| M0 | FAIL 沿用 | 仅消费 binary 来源；launcher BLOCKED |
| 桌面 launcher | sandbox-exec rc71 + pgrep rc3 UNKNOWN | **本轮未启动；不用 --help** |
| 真实 provider | NOT_RUN | 不申请激活 |
| G0-F 后台常驻 | NOT_RUN（仅前台扫描） | 按用户指令「不能称后台常驻，原用例继续 BLOCKED」 |
| 业务身份来源 | 沿用 M2 挂账 | 本轮 NONE |
| AppHub publish / 公网 | 不发起 | |

---

## 1. 改动文件清单

| 文件 | 净行 | 范围 |
|---|---|---|
| `app/bundle/main.splash` | +569/-0 | STATE 追加 m6_*；新增 24 个 m6_* 函数；view 新增搜索 TextInput + 3 个 tab + 状态/提醒/诊断 label + Chip；refreshDetail 加 history/phase/summary 分支；refreshLabels 同步 m6_* label；load() 调 m6_init_forms + m6_load_follow_ups；command hook 7 处 |
| `runtime/optimization/2026-10-09/M6/CONTEXT_M6.md` | new | 浓缩必读 |
| `runtime/optimization/2026-10-09/M6/r1/CANDIDATE.json` | new | 候选清单 |
| `runtime/optimization/2026-10-09/M6/r1/scripts/m6_*.py` | 10 new | 测试脚本 |
| `runtime/optimization/2026-10-09/M6/r1/evidence/*.json` | 10 new | 证据落盘 |
| `runtime/optimization/2026-10-09/M6/r1/results/run-summary.json` | new | driver 汇总 |
| `docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r1.md` | new | 本报告 |

main.splash 主源 SHA-256（与 CANDIDATE 一致）：
- 前（M5 r2）：`20bf8800b3b6542f806f6e59a7a360a0df85cb2021fdd6321a65504b6ccfb113` (251677 字节 / 5584 行)
- 后（M6 r1）：`321c9298d73104302eb005487cd7727555266cdfdbc03d0898eab0e24931af1d` (277622 字节 / 6153 行)

---

## 2. 八项硬要求的逐条对位

### 2.1 复核三角色工作台（搜索/待我处理/收藏/数量/当前动作都来自可见真实数据；收藏不改变任务业务版本）

**实现**：
- `STATE.search` + `STATE.nav` 三类（all/todo/fav）经 `filteredVisibleIndices()` 真实过滤（既有 M1/M2 函数不动）。
- 收藏走 `togglePin` → `runCommandBound("togglePin", ...)`（既有 M2/D-M2-06 修复），M6 仅做静态点检。
- `m6_count_pinned_for_actor` / `m6_visible_count_for_role` / `m6_due_count_for_identity` 显式按 actor + 过滤层级动态计算。

**验证**（脚本）：
- `m6_favorites_isolation.py`（5/5 PASS）
- `m6_whitebox_three_role.py`（18/18 PASS）

### 2.2 既定设备历史建议和阶段说明，复用 M3 来源、校验、过期及错误契约；无历史说明未知，不把种子洞察当学习效果

**实现**：
- 新 `m6_history_render(task)`：仅读 `AI_REQUESTS_LOG`（M3 既有）；无记录返回 `kind=none`，固定文案 `"无历史说明未知"`。
- 新 `m6_phase_meaning(task)`：按 `t.status` 给阶段含义；不创造设备事实，不引入 `createDraft` / `submitCompletion` 等写命令。
- 新 detail tab「设备历史」「阶段说明」通过 `STATE.detail_tab` 切换；render 函数仅显示历史依据 + 来源。
- `m6_history_for_task_count` 辅助统计；`m6_match_search_v2` 已实现但用 `_strContains` 嵌入既有 `matchSearch`（用 `index_of` 替代 `starts_with`）。

**验证**（脚本）：
- `m6_history_phase.py`（14/14 PASS）—— 检测 `kind=none` 固定文案、M3 来源、phase 不写业务、不调用禁用动词。
- `m6_search_real.py`（6/6 PASS）—— `_strContains` 用 `index_of`、`m6_search_input` 真实 TextInput、占位「🔍 搜索（占位；M3 接 TextInput）」已移除。

### 2.3 可恢复、去重的预约跟进；改约/取消后旧提醒失效；若只支持重开或前台检查，不能称后台常驻，原用例继续 BLOCKED

**实现**：
- `m6_register_follow_up(task_id, kind, due_ms, summary)`：ACT 写入；同 task_id + 同 kind 旧 ACTIVE 自动 SUPERSEDED。
- `m6_invalidate_for_task(task_id, reason)`：命令边界 hook。`m6_dismiss_follow_up(fu_id)`：人工关闭。
- 跨重启 `m6_save_follow_ups` → `runtime/optimization/2026-10-09/M6/r1/sandbox/follow_ups.json`；`m6_load_follow_ups()` 在 `load()` 调用。
- **不启动后台定时器**（脚本静态检查 `setInterval/setTimeout/backgroundTask/schedule_timer` 均不存在；通过）。
- `G0-F 后台常驻 = NOT_RUN`（按用户授权约束）；原用例 G0-F 仍 PARTIAL（仅前台 reopen 扫描）。

**验证**（脚本）：
- `m6_followup_dedupe.py`（7/7 PASS）：dedupe / invalidate / 跨重启 / 不启动后台 / sandbox 内不写 ~/.octosense。

**命令边界 hook（全部在 `runCommandBound` 已通过 + `commitSucceeded` 之后追加）**：
- `confirmAppointment` → 注册 `kickoff_checkin` 提醒（at=appt.startMs − 30min，落后则改为 +5min）
- `rescheduleAppointmentFromForm` → `m6_invalidate_for_task(t.id, "reschedule")`
- `cancelAppointment` → `m6_invalidate_for_task(t.id, "cancel_appointment")`
- `submitCompletion` → `m6_invalidate_for_task(t.id, "submit_completion")`
- `acceptCompletion` → `m6_invalidate_for_task(t.id, "accept_completion")`
- `rejectCompletion` → `m6_invalidate_for_task(t.id, "reject_completion")`
- `reassign` → `m6_invalidate_for_task(t.id, "reassign")`

### 2.4 同一 task_id 的任务摘要/跳回入口；外部摘要不是第二事实库，不带出无权资料或继承他人 grant

**实现**：
- `m6_jump_summary(task_id)`：先 `findTaskById(task_id)` → `visible(t, getMe())` 不通过则拒（不显示明细）；不写任何业务字段；只切 `STATE.detail_tab = "summary"` + `STATE.selected_task_id = task_id`。
- `m6_summary_lines(t)`：仅返回当前身份可见字段；`contact` 用 `canSeeContact` 闸；不读 `t.pinnedBy` / 不写 `t.version` / 不调 `runCommandBound` / `createDraft`。
- 新 detail tab「摘要」：事件按 `EVENT_LOG` 真实时间排序；不继承 cross-project 的他人 grant。

**验证**（脚本）：
- `m6_jump_summary.py`（13/13 PASS）：visible 校验、不带 grant、`canSeeContact` 控制 contact 暴露、不写业务字段、不调禁用动词。

### 2.5 统一加载 / 空态 / 断线 / 权限变化 / 保存失败 / 待核验 / 过期建议 / 附件失效的反馈和恢复；全流程键盘与未保存输入检查

**实现**：
- 新 `m6_status_label_text(role)` 聚合 8 类反馈（空列表 / 离线占位 / 保存失败 / 待核验 / 过期 AI 建议 / 附件失效 / fav 空 / todo 空）→ 单 Label `m6_status_label`。
- 新 `m6_unsaved_set(panel_open, has_input)` + `m6_unsaved_check_close(panel_open)` → 含未保存输入时 `block=true` + 中文提示「面板含未保存输入；确认关闭？」。
- 调试噪音移出主 UI：list_footer `"M1 框架 · 列表 ≤ 8 · 选中以 task_id 维持"` → 占位 `"—"`；头部 `"演示身份 · 非登录认证"` Label 删；调试文集中到 `m6_diag_text()` + `m6_cmd_dev_diag_toggle`，按 `STATE.m6_dev_diag_open` 控制 `m6_diag_label.set_text("")`。
- 主要交互控件 22+（`Chip{`/`Bar{`/`TextInput{`/`ButtonFlat{`）；不引入 `setTabIndex` 手动索引。

**验证**（脚本）：
- `m6_status_unified.py`（15/15 PASS）：8 类反馈分支存在；正式 UI（去除注释后）不含 `M1 框架 · 列表 ≤ 8` / `演示身份 · 非登录认证` / `选中以 task_id 维持`；色彩调色板含 `ink/secondary/accent/danger/heroBg/border`。
- `m6_unsaved_keyboard.py`（11/11 PASS）：`m6_unsaved_check_close` 返回 `block=true`、含中文提示、`max_lines: 2` / `max_lines: 4` / `max_lines: 8` 兜底、长中文 `index_of` 子串命中（模拟）。

### 2.6 真实测 1440×900、1280×800、980×760、150% 文字放大及长中文

**实现**：
- launch BLOCKED 沿用（M0..M5）：`sandbox-exec rc71` + `pgrep rc3` UNKNOWN；本轮未启动 launcher；**未用 --help**。
- 源码层静态点检：调色板 / 字号梯度 / 高度 / `max_lines` / `ScrollYView` / 列表 ≤ 8 / 列宽 280 / 侧栏 170。
- 长中文兜底：所有主 Label 设 `max_lines`；_strContains 用 `index_of` 子串包含（不再 starts_with）。
- 真实桌面截图 + 演示草片：**NOT_RUN**（launcher BLOCKED）；按用户授权约束不伪造。

**验证**（脚本）：
- `m6_viewport_source.py`（20/20 PASS）：6 类调色板全部存在；字号 16/14/11/9 累计出现 ≥ 30 次；主交互控件（chip/bar/textinput）height ≥ 22；`ScrollYView` 存在；`task_row_*` ≥ 8；列宽 280 / 侧栏 170；`max_lines: 2/4/8` 全设。

### 2.7 保存同版本桌面正常/异常截图及演示草片；清除正式界面调试噪音，开发诊断保留在合适位置

**实现**：
- 真实桌面截图：**NOT_RUN**；不伪造（在 0.6 / 2.7 表内如实标记）。
- 调试噪音剥离：见 §2.5。
- 开发诊断保留：`STATE.m6_dev_diag_open` 收起的 chip「开发诊断」在左侧栏底部；点开后写一行诊断信息到 `m6_diag_label`（默认隐藏）。

### 2.8 核对全部 T/U 映射，遗漏硬要求不能移到未来以换取 PASS

下表汇总在 §5。

---

## 3. 主要测试结果（10 脚本 / 168 用例 / 全部 PASS）

| 脚本 | 范围 | cases | 结论 |
|---|---|---|---|
| m6_favorites_isolation.py | 收藏走 runCommandBound + 跨角色/项目隔断 | 5/5 | PASS |
| m6_search_real.py | TextInput 真实化 + index_of 子串 + 同步 | 6/6 | PASS |
| m6_history_phase.py | m6_history_render + m6_phase_meaning + tab 声明 | 14/14 | PASS |
| m6_followup_dedupe.py | dedupe + invalidate + 跨重启 + 不后台 + 不写 ~/. | 7/7 | PASS |
| m6_jump_summary.py | visible 闸 + 不带 grant + canSeeContact + 不写业务 | 13/13 | PASS |
| m6_status_unified.py | 8 类反馈聚合 + 调试剥离 | 15/15 | PASS |
| m6_unsaved_keyboard.py | unsaved + max_lines + 长中文 | 11/11 | PASS |
| m6_viewport_source.py | 调色板 + 字号 + 控件高度 + 尺寸 | 20/20 | PASS |
| m6_whitebox_three_role.py | 三角色搜索 / 收藏 / 重登 / 跨项目过滤 | 18/18 | PASS |
| m6_m5_compat_audit.py | M0..M5 既有契约 / 函数 / 数据结构全部保留 | 59/59 | PASS |

`m6_review_driver.py` → `runtime/optimization/2026-10-09/M6/r1/results/run-summary.json`：`scripts_passed=10/10`、`cases_passed=168/168`。

---

## 4. 启动 / 重跑

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M6/r1/scripts/m6_review_driver.py
```

隔离数据全部落 `runtime/optimization/2026-10-09/M6/r1/sandbox/`（attachments / quarantine / lost+found 与 M5 共享根目录 root 不动；M6 新建 `follow_ups.json`）；`~/.octosense` 与宿主 HOME **未访问**；HOST LAUNCHER **未启动**；`--help` 未调用。

---

## 5. 覆盖 T / U 项与状态

| T/U 编号 | 责任 | 本轮状态 |
|---|---|---|
| G0-F | 后台常驻提醒调度 | PARTIAL → 仅前台 reopen 扫描；显式声明原用例 BLOCKED |
| T17 | 单一身份切换 reopen | PASS（identityById + USERS fallback） |
| T18 | 跨任务 / 跨项目 readback | PASS（runCommandBound 单一事实库） |
| T23 | 三角色持续追踪同一 task | PASS（selected_task_id 稳定 + nav=todo） |
| T25 | 跨项目合法身份写 | NOT_RUN（M3 FAIL 沿用，不补 provider） |
| T26 | 纯手工 confirm | NOT_RUN（M3 OFFLINE） |
| T28 | 真实桌面 reopen | BLOCKED（launcher BLOCKED） |
| T29 | shared grant 销权 | NOT_RUN（M2 BLOCKED） |
| T30 | 改约/取消旧 ACTIVE 失效 | PASS（m6_invalidate_for_task） |
| T33 | 真实模型 | BLOCKED（M3 FAIL） |
| T34 | 完整 AI 链路 | NOT_RUN（M3 FAIL） |
| T35 | 旧建议 stale | PARTIAL（m6 复用 m4 失效） |
| T36 | 真工具调用 | NOT_RUN（M3 FAIL） |
| T38 | audit + 历史依据 | PARTIAL（m6_history_render 仅读 ai_requests_log） |
| U01 | 5 区可达 | PARTIAL（BLOCKED launch） |
| U02 | PENDING_DRAFT 持久化 | PASS（D-M3-02 已落） |
| U03 | 三角色真实读 | PARTIAL（adapter 不立 trusted） |
| U04 | 改约 / 冲突 / 过期 | PASS（M4 + m6_invalidate_for_task） |
| U05 | 安装 / 服务空间 | PASS（既有 M4 契约） |
| U06 | UI 历史证据 | PASS（m6_history_render） |
| U07 | 重复点击 / 离线输入 | PASS（M2/M5 已落；m6 不改动） |
| U08 | 错误出口 | PASS（m6_status_label_text） |
| U09 | 1440/1280/980 视口 | NOT_RUN（launcher BLOCKED） |
| U10 | 操作区可达 | PARTIAL（m6_status_label_text 已兜底） |
| U11 | 滚动 / 输入 / 面板 | PARTIAL（launcher BLOCKED） |
| U12 | 摘要跳回 | PASS（m6_jump_summary 唯一入口） |
| P02 | 本地 catalog / 私有发布 | PARTIAL（沿用 M0..M5） |

**未通过项真实保留**：T25 / T26 / T28 / T29 / T33 / T34 / T36 / U01 / U03 / U09 / U11 等 NOT_RUN/BLOCKED 项以原状留在台账，未用「基本通过」伪装放行。

---

## 6. 尚未完成 / BLOCKED / NOT_RUN

1. **native desktop runtime = BLOCKED**：sandbox-exec rc71 + pgrep rc3 UNKNOWN；launcher 未启动；不连 `--help`。
2. **真实中文键入 / 视口 / 接单/确认 receipt-of-action = NOT_RUN**（沿用 M3/M4/M5）。
3. **同版本桌面截图 + 演示草片 = NOT_RUN**（沿用 launcher 阻断，不伪造）。
4. **G0-F 后台常驻 = NOT_RUN**：仅前台 reopen 扫描。原用例继续 BLOCKED。
5. **真实 model provider = NOT_RUN**（沿用 M3 延期）。
6. **可信业务身份来源 = 沿用 M2 挂账**。
7. **symlink 跟随拒绝 / host picker = 沿用 M5 BLOCKED**。
8. **M0/M1/M2/M3/M4/M5 前序未闭合缺陷**：未触碰；按 Abram 13:54 挂账。
9. **AppHub publish / 公开签名 / 公网上架 / listing**：本轮一律不发起；本地 catalog 沿用；离线签名已授权不算 NEEDS_ABRAM。
10. **业务写 6 个动作（reassign / cancel / accept / reject / reschedule / submit）的 follow-up 失效**：已 hook；权威测试需独立 Review。

---

## 7. 候选清单核心字段

```json
{
  "candidate_id": "M6-r1-worktree",
  "base_candidate_id": "M5-r2-worktree",
  "module": "M6",
  "modified_files": ["app/bundle/main.splash"],
  "scripts_total": 10,
  "scripts_passed": 10,
  "cases_total": 168,
  "cases_passed": 168,
  "host_started": false,
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 8. 末两行（按用户授权约束固定格式）

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
