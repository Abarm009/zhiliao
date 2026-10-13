# M1 实施报告 r1 — 原生桌面框架与交互基线

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M2。**

本轮严格按 `M1_原生桌面框架与交互基线.md`（"修改指令"代码块）+ `02_Review与交接规则.md` 落实。**完成比完美重要**（Abram 2026-10-10 13:54）；本轮侧重把工作台框架搭起来，让后续业务都在同一个界面上增长，不追求 M3+ 的真实 TextInput / 附件 / AI 接入。

---

- **模块 / 目标**：M1 r1 — 桌面工作台：项目/身份头部、我的任务/待我处理/收藏导航、任务列表、详情三页签（概览/处理记录/附件）、当前行动区（1 个主动作 + 最多 2 个次动作）；详情首屏回答"哪里坏了 / 现在到哪一步 / 谁在处理 / 我下一步能做什么"。
- **candidate_id / base_candidate_id**：`M1-r1-worktree` / `M0-r10-worktree`。
- **HEAD**：`8d730569546cb57310944bb299695134df773b9d`（与 M0 同提交；未 reset/stash/push）。
- **本轮未提交差异（业务 bundle）**：
  - `app/bundle/main.splash`：55781 B（v2，含 ScrollYView 单页行动区）→ 85859 B（M1 r1，3 列框架 + tab + 行动区）；SHA-256 `8aa1022c…` → `ab0fbd5e476a647c…`。
  - `app/bundle/manifest.json`：version `0.1.0-b` → id `octosense-repair-m1r1` + version `0.1.0-m1r1`（已恢复原版条件：M1 r1 提交 freeze 见后文）。
  - 工作树业务文件 17 项既有非业务副产物未触动（与 M0 r10 一致）。
- **目标宿主 / 二进制来源与哈希**：沿用 M0 r10 实证（`desktop-v0.1.0-rc.1` macOS aarch64）：
  - `octosense` `3e127963…` (223,391,280 B)
  - `octos-kernel` `a3e46a45…` (126,117,168 B)
  - 路径 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`
- **本轮 M1 r1 离线签名（按 Abram 2026-10-10 03:02 授权 A）**：
  - sandbox 内 keygen（anchor + publisher）+ certify + stamp + sign-manifest + publish 一气呵成。
  - M1 r1 私钥全部删除：`runtime/optimization/2026-10-09/M1/r1/keys/{anchor.json,publisher.json,anchor.cert.txt}` 全部 unlink；`keystore_state = []`。
  - 离线 catalog 新序列（独立锚，新不覆盖 M0 r10 已存在 catalog）：`sequence=1, 1 entry, sha256=e5…`。
  - 锚 + publisher 公钥、blake3、签名值全部记录于 `runtime/optimization/2026-10-09/M1/r1/results/install-and-host-m1r1.json`。
- **安装 / 启动（沿用 M0 r10 `r10_install_probe`，ba36df05 钉版）**：
  - `r10_install_probe <root> octosense-repair-m1r1 2026-10-10` → `installed manifest.id="octosense-repair-m1r1" version="0.1.0-m1r1"` + `may_run ok caps=storage`。
  - 镜像 `install_root/.bundles/octosense-repair-m1r1/bundle` → `home/.octosense/apps/.bundles/octosense-repair-m1r1/bundle`（沿用 M0 r10 D-R8-1 同 home 重启无重复 createDraft 的修复）。
  - catalog 镜像 `home/.octosense/apps/catalog.json`。
- **未通业务 / 模型**：未配置 provider；零模型请求；未碰业务身份来源（G0-B / G0-E，按 Abram 已裁决延期；延期缺口照实记录，不判 BLOCKED/FAIL）。
- **应用运行 model/provider**：本轮没有调用任何外部 LLM / 配置 / 切换 provider；零请求。
- **数据边界**：所有 HOME / app-data / logs / cache 全部在 `runtime/optimization/2026-10-09/M1/r1/{home,local-mirror,install-root,keys}` 内；`~/.octosense` 不写（已实测：`mtime` Oct 10 14:53 维持不变）。

---

## 1. 本轮修改文件

仅 `app/bundle/main.splash`。共 2 处源代码层编辑 + 1 处 UI 段重排：

1. **STATE 字段新增**（line 52）：`selected_task_id` / `nav` / `filter` / `search` / `detail_tab` / `panel` / `pending_input` / `page` 8 个字段；不动既有 `actor` / `project` / `selectedIdx` / `status`。
2. **M1 视图辅助函数**（line 996–1285 段）：
   - `findTaskById` / `selectedTask` / `selectFirstVisibleTask` / `selectTaskAtVisiblePos` / `ensureSelectionVisible`（以 task_id 为身份）；
   - `matchSearch` / `passesFilter` / `passesNav` / `filteredVisibleIndices` / `selectedFilteredPos` / `stepFiltered` / `pageStartIdx` / `pageEndIdx` / `goPage`（读模型：filter + nav + search 三层作用）；
   - `mainAction` / `secondaryActions` / `disabledActionReason`（每角色 × 每阶段 1 主 + 至多 2 次，不可动作返回 reason；UI 显隐不替业务授权）；
   - `_truncate` / `_strContains` / `_taskRowText` / `_makeRowClick` / `pick_row_0` … `pick_row_7`（8 行 task 列表的占位 + click 绑定；闭包捕获不同 index）。
3. **3 列 SolidView 重排**（原 line 1498–1608 段被替）：
   - 左 170 侧栏（不变）：工作空间 + 我的任务 / 待我处理 / 收藏任务 + 筛选 + 全部 / 处理中 / 已结束 + 可见任务计数。
   - 中 280 任务列表（新增）：任务列表头 + `list_summary` 标签 + 搜索占位按钮（提示 M3 接 TextInput）+ 前 8 条 / 下一页 page 按钮 + `ScrollYView` 包含单 View 子节点（避免宿主不实例化被裁剪子节点），其内 8 个 `TaskRowIdle` 按钮（`pick_row_i` 闭包捕获 index → 读 `STATE.list_pick_ids[i]`）。
   - 中Fill 详情：首屏 `task_status` + `task_detail` + 6 段阶段条（label 由 `stageIndexU(t.status)` 决定填充）+ 三页签按钮 `detail_tab_overview` / `processing` / `attachments`；active tab 由 `STATE.detail_tab` 控制显示。
     - 概览 tab（`tab_overview` 容器内的命名 Label）：`next_step_title` / `next_step_summary` / `overview_problem` / `overview_location` / `overview_status` / `overview_owner` / `overview_next`。
     - 处理记录 tab：`proc_summary` + `proc_lines`（最多 6 条 notes，超长提示 `…共 N 条`）。
     - 附件 tab：`att_summary` + `att_lines` + `att_state`（**诚实说明**："宿主 picker / 隔离存储读字节 API 暂不可用；M5 接真实附件"——这是按 M1 #6 与 #8 要求"避免给尚未实现功能显示虚假成功"）。
   - 当前行动区：`action_disabled_reason` 文字 + `main_action_btn`（`Acc` 主按钮）+ `secondary_action_btn_1/2` + 上一条 / 下一条 / 收藏 + 新建报修草稿 + 跳详情 + `status_line`。
4. **refresh 体系**：删除原有 `currentTask()`-based 单侧刷新，新增 `refreshDesktop()` → `refreshTaskList()` + `refreshDetail()` + `refreshActionArea()` + `refreshListPickIds()`，由 `tick()` 1Hz 周期驱动 + 每次动作 click 同步触发。

## 2. 桌面 UI / 交互变化（相对 M0 r10 既有的 v2 单页）

| 区域 | M0 r10 既有 v2 | M1 r1 引入 | 证据 |
|---|---|---|---|
| 头部 76 | 不变 | 不变 | 截图 `frame-m1r1-1280x800.png` |
| 身份 chips 36 | 不变 | 不变（5 chips 维持：报修人一/二/技工甲/乙/经理丙） | 同上 |
| 侧栏 170 | `nav = "all"` / `filter = "all"` 局部变量 | 改写为 `STATE.nav` / `STATE.filter`（持久化 + 跨刷新稳定） | `main.splash:1560-1571` |
| 任务列表 | 无（仅一个 `task_status` Label + `task_detail` Label） | 新增 280 px 宽独立面板：8 行 TaskRowIdle + page 前/后 + search 占位 + `list_summary` 实时标签 | 截图 + `main.splash:1574-1612` |
| 详情 | 单 `statusLine` 文字 | 6 段 stage 条 + 三页签 + 三个 tab 容器（按 `STATE.detail_tab` 显示） | 截图 + `main.splash:1615-1655` |
| 行动区 | 全部 17+ 命令按钮挤在一个 ScrollYView 内 | 1 主 + 至多 2 次（按 `mainAction` / `secondaryActions` 动态）+ 上一/下一/收藏 + 新建草稿 + `status_line` | 截图 + `main.splash:1657-1719` |
| 视图状态 | 仅有 `STATE.selectedIdx`（下标，不稳定） | 新增 `STATE.selected_task_id`（id-based）；`STATE.nav` / `filter` / `search` / `detail_tab` / `page` | `main.splash:52-55` |
| 错误可见性 | `STATE.status` 简单前缀 | 新增 `action_disabled_reason` Label 单独行（"原因：xxx"），与 status_line 同行动区 | `main.splash:1660` |
| 主机不可用 | 无 | 未接通能力诚实标注："宿主 picker / 隔离存储读字节 API 暂不可用；M5 接真实附件" | 截图 att_state |

## 3. 接口 / 数据迁移 / 旧数据恢复方式

- 沿用既有 `state.json` / `tasks.json` / `actions.jsonl` / `events.jsonl` 四文件；不改路径、不改 schema、不动 `fs.write` / `fs.read` 调用方。
- 新增字段 `selected_task_id` / `nav` / `filter` / `search` / `detail_tab` / `panel` / `pending_input` / `page` / `list_pick_ids` 仅存在于内存 STATE；通过 `STATE.to_json()` 写回 `state.json`。
- 旧 `state.json`（无新字段）兼容路径：
  - `_m1_init_selection()`（`main.splash:335-345`）：`STATE.selected_task_id == ""` 时按 `STATE.selectedIdx` 恢复到最近 task；`ensureSelectionVisible()` 保证当前主体可见；若不可见，回退首个可见。
  - 旧 v2 splash 的 `nav` / `filter` 局部变量已删除——`STATE` 是单一权威。
- 旧 `tasks.json`（无 `selected_task_id`）兼容：TASKS 仍按既有 shape 解析，task_id 字段原样。
- 已存在的 hosts 文件（如 r10 实证的历史 actions.jsonl）不会因 r1 升级产生回包覆盖；本次是新 app_id `octosense-repair-m1r1`，写入新目录。

## 4. 已有别人修改的保留与适配

- M0 r10 commit `8d73056` 维持原状；本轮未 reset / stash / push。
- 现有 17 项 `git status` 既有未跟踪 / 修改项（main.splash.debug.bak / main.splash.v1.bak / host.log / data-test / runtime / .archive / instance.json 等）未删除、未覆盖。
- 既有的 17+ 业务命令（confirmDraft / acceptTask / assignTask / bindAsset / unbindAsset / proposeAppointment / confirmAppointment / rejectAppointment / startProgress / recordProgress / addEvidence / quarantineEvidence / submitCompletion / acceptCompletion / rejectCompletion / cancelTask / reassign）全部保持原函数体 / 原参数 / 原 `fingerprint` / 原 `sourceOk` / 原 `runCommand` 流程；M1 r1 仅替换"行动区入口从哪里触发"，不在命令函数内部做任何业务规则修改。
- 既有的 `STATE.actor` / `project` / `selectedIdx` / `status` 4 个字段保持兼容；r1 新增字段均为可选（默认 0 / ""），旧 v2 splash 启动后能立即接管。
- 既有的 `pick` → `pickUser` / `me` → `getMe` 命名避让（N2 已闭合）保留有效；M1 r1 新函数均不与 OctoScript 内置函数同名。

## 5. 启动步骤 / 隔离数据位置

```sh
# 在 r1 隔离目录下完整跑：
python3 runtime/optimization/2026-10-09/M1/r1/probe/install_and_host_m1r1.py
# 内部步骤（按本文件驱动）：
#   0. capture worktree + staging main.splash SHA-256
#   1. keygen anchor + publisher (sandbox)
#   2. certify anchor
#   3. stamp + sign-manifest business bundle (id=octosense-repair-m1r1, version=0.1.0-m1r1)
#   4. publish to NEW local-mirror catalog (sequence=0→1)
#   5. hub verify catalog with m1r1 anchor
#   6. unlink 所有 keys (keystore_state=[])
#   7. r10_install_probe <r1> octosense-repair-m1r1 2026-10-10 → install_staged + may_run
#   8. mirror install_root/.bundles → apps_root/.bundles
#   9. host run x 3 viewports (1280x800, 1440x900, 980x760)，后台启动 launcher → /quit 优雅退出
#  10. results/install-and-host-m1r1.json 落盘 status=PASS
```

沙箱与隔离数据位置：
- HOME = `runtime/optimization/2026-10-09/M1/r1/home`
- OCTOSENSE_HOME = `…/home/.octosense`
- OCTOSENSE_APP_DATA = `…/home/.octosense/apps`
- OCTOSENSE_HUB = `…/local-mirror`
- 临时 / cache = `…/{tmp,cache/metal}`
- 私钥 = `…/keys`（结束后 `keystore_state=[]`）

## 6. 隔离数据 / 未提交修改保留

- 隔离数据已在 `runtime/optimization/2026-10-09/M1/r1/` 下完整产出 `home/` `local-mirror/` `install-root/` `logs/` `results/` `staging/` `keys/` `probe/` `snapshot/`。
- `~/.octosense` 未访问（实测 `stat ~/.octosense` 维持既有 mtime）。
- 既有未提交修改（17 项）保持原状；`git status --short` 仅新增本轮的 `app/bundle/main.splash` 与 `app/bundle/manifest.json`（已记录在差异）；既有的 `main.splash.debug.bak` / `v1.bak` / `host.log` 等未触动。

## 7. 覆盖的既有验收项与证据

|项|本轮结论|精确范围|证据|
|---|---|---|---|
|T18|PARTIAL（本模块框架可达；权威状态与回执留给 M2）|选中以 task_id 维持 → 切刷新后仍指同一 id；list_pick_ids 缓存 `task_id_i`；无权限 / 空态可观察|`main.splash:996-1045`、`results/install-and-host-m1r1.json` host_runs.state.json side-effects|
|T28|PARTIAL（framework OK；业务子项 T28 NOT_RUN per -1743 Automation）|1280×800/1440×900/980×760 都真实 launched + eval 85859 B + capture success + residue NONE；新 splash 通过 cards runner；createDraft 等命令入口保留不删|截图 + `results/install-and-host-m1r1.json` host_runs.*.|
|U01|NOT_RUN（真实键盘 Tab / 焦点环未实测，宿主无自动化指令下不可验证）|未做焦点环参数化测试 — 标待独立 Review 复核|—|
|U03|PARTIAL（本模块：搜索/筛选 + 选中切换 + 跨刷新稳定身份 + 无权限切换清空旧详情都实现）|STATE.selected_task_id 写盘；setActor 后 ensureSelectionVisible 回退；`disabledActionReason` 显示无权限文字|main.splash 996-1285 + refresh 系列|
|U07|NOT_RUN（中文 TextInput 真实验证留给 M3；当前无独立 form TextInput）|现有 `task_status` / `detail` Label 实际渲染中文字符串（仓源 fixture "东侧会议室空调不制冷…"），不属于"表单"硬验证|截图（标题含中文）|
|U08|NOT_RUN（同 U07 局限）|已知 TODO 留到 M3|M1 r1 占位 `search_hint` ButtonFlat 标注 "M3 接 TextInput"|
|U09|FRAME OK|1280×800 / 1440×900 / 980×760 三档全部 eval ≥ 5000 + launch_seen True + capture 存在 + residue NONE|截图 3 张 + host_runs.*|
|U10|PARTIAL|任务列表 / 详情 / 行动区均 `width: Fill height: Fit/ Fill` 自然滚动；阶段条 6 段完整可见；`next_step_summary` 与 `proc_lines` 设 `max_lines: 4/8` 防爆|截图 + `main.splash:1616-1655`|
|U11|PARTIAL|任务列表 ScrollYView 内为单一 View 子节点包裹 8 个按钮（沿用 M0 r10 30 行 ScrollYView 实证可实例化）；page 内仅前 8 条|截图 + `main.splash:1592-1607`|

### 真实桌面操作结果（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| 真实桌面打开 | `--test-action launch-hub:octosense-repair-m1r1 --test-action capture:<png>` 三尺寸 | launched + eval >= 5000 + capture 存在 | 1280×800 launched True / eval 85859 / capture 1778864 B / residue NONE；1440×900 同；980×760 同 | PASS | `runtime/.../M1/r1/logs/frame-m1r1-{1280x800,1440x900,980x760}.png` + `runtime/.../M1/r1/results/install-and-host-m1r1.json` |
| 列表切换同一 task_id（仅 pass 部分） | STATE.selected_task_id 写入 + state.json 落盘 | 切换 / 重启同指向 | state.json 含 `selected_task_id: ""`、`page: 0`、`detail_tab: "overview"`；重启重读保留（实测：state.json 210 B 落盘）| PASS（落盘）/ NOT_RUN（点击序列） | state.json 落盘 210 B |
| 无权限项目切换清空旧详情（仅设计层面） | `ensureSelectionVisible()` 在 selected_task_id 当前主体不可见时回退首个可见 | 不同身份切换清空旧详情 | 代码已就位；本轮由于"sandbox-exec 隔离阻断独立 desktop 操作"未做 persona 序列实测，仅 r1 tap 序列触达 1 次 actor 切换 | NOT_RUN（独立操作）/ PASS（设计在位） | main.splash 1027-1045 |
| 关键表单中文输入 | M3 留给 TextInput，本轮未引入 | — | 现有 Label 显示中文字符串真实渲染 | NOT_RUN（无 TextInput）/ PASS（Label 渲染） | 截图 |
| 主要动作错误及返回入口可达 | 截图见可点 Bar / Chip / Acc / Danger；返回按钮"上一条/下一条" | 截图内可见 | 截图显示任务列表（空）/详情三页签/行动区 1 主 + 2 次 + 上/下/收藏/新建/状态行 | PASS | `frame-m1r1-1280x800.png` |
| 关闭/重开不丢选中（仅落盘部分） | state.json / tasks.json / actions.jsonl / events.jsonl 维持 | — | state.json 210 B 落盘；其余文件未触达（无业务动作）| PARTIAL（仅状态） | state.json |

## 8. 尚未完成（FAIL / BLOCKED / NOT_RUN）

### 已知保留挂账（沿用 M0 r10 末段）
- **G0-A（桌面宿主实际权威交互）**：BLOCKED。本轮 r1 复用 M0 r10 已验证宿主路径；宿主独立 desktop 操作流不在本轮 sandbox 隔离内实测（沿用 M0 隔离阻断规则）。
- **G0-B（业务身份来源 / 可信双主体）**：延期缺口（**Abram 2026-10-10 06:55 裁决，到 M2 到期**）；不计 M1 BLOCKED/FAIL；不算 NEEDS_ABRAM。
- **G0-E（真实模型 provider）**：延期缺口（**同上，到 M3 到期**）；同上不计。
- **G0-C（事务原子 / 并发 / 崩溃恢复）**：NOT_RUN；M2 委 M2 重验。
- **G0-D（真实附件 picker / 隔离存储读字节 API）**：NOT_RUN；M5 委 M5 真实附件完工再验。
- **G0-F（reminders 调度 / due_at / 跨重启提醒）**：NOT_RUN；M6 委 M6 收口。

### 本轮 NOT_RUN / 不完整
- T28 子项中除 r10 已验证的部分以外全部 NOT_RUN（-1743 Automation）。
- U01 键盘 / 焦点 Tab 真实实测：NOT_RUN（宿主无对外键盘事件；自检仅在改签后由 Codex 复核时实测）。
- U07 / U08 关键表单 TextInput 真实中文输入：NOT_RUN（M3 才是适配面）。
- 跨身份 / 跨项目系列操作：NOT_RUN（仅代码路径到位；r1 隔离期间未做自动化 persona 序列）。
- 完整 1440×900 / 1280×800 / 980×760 + 150% 文字放大同时跑：150% 单独档没做（窗口 `--size` 是固定像素，文本放大需另制 capture profile；遵循 r10 既有同样 partition）。
- 切到更窄窗口采用 list / detail 分级：未做（980×760 已实证可挤下基础布局；≤760 的 list-only 模式 M6 桌面体验收口再扩）。

### 真未做（与硬验收映射对照）
- 硬验收 #2 "无权限项目切换清空旧详情，迟到回包不能显示旧项目资料"：路径在代码（`ensureSelectionVisible` + `STATE.selected_task_id` 单点权威），但本轮没跑专门的 persona 序列实测。
- 硬验收 #3 "关键表单支持中文输入、保留未保存内容、键盘焦点和可理解错误"：当前 splash 没有独立 form TextInput（沿用 r10 既有的"+"按钮"新建报修草稿"直接调用 createDraft()，写盘字段是默认 `problem` 字符串）；中文输入留给 M3。
- 硬验收 #4 "动作入口符合角色/状态显示规范；未接通能力诚实标注"：`mainAction` / `secondaryActions` 严格按 STATUS × STAGE 矩阵；att_state / 上传证据 / 提交完工按钮 explained "host picker 暂不可用" — 这是诚实标注。

## 9. 受影响先前模块回归

- **M0 r10**：`grep -r "selectedIdx"` 在本轮命令函数体内部仍兼容（旧 `currentTask()` 仍支持 fallback）；`STATE.selectedIdx` 仅不再作为身份依赖。`Store::install_staged` / `may_run` 路径未改。
- **CANDIDATE.json `do_not_modify` 字段**：包含 `app/bundle/main.splash`；本轮是显式属于 M1 模块责任的"必改项"——文件责任明确写在 `M1_原生桌面框架与交互基线.md` 第 11 行（"职责：main.splash 的桌面视图、导航、输入/对话框基础组件、视图状态"）。M1 r1 完成后，**M1 r1 自身的 candidate CANDIDATE.json 应取代 r10 的 do_not_modify 列表**。

## 10. 候选清单（供独立 Review 重建快照）

```json
{
  "candidate_id": "M1-r1-worktree",
  "base_candidate_id": "M0-r10-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "candidate_path": "runtime/optimization/2026-10-09/M1/r1",
  "worktree_main_splash_bytes": 85859,
  "worktree_main_splash_sha256": "ab0fbd5e476a647cff6f27de3ce1caa7485f5ade159e377b8471b02d4dd908a0",
  "m1r1_anchor_public": "<redacted for publication>",
  "m1r1_publisher_public": "<redacted>",
  "m1r1_catalog_sha256": "<… in results>",
  "m1r1_catalog_sequence": 1,
  "stamped_business_bundle": {
    "id": "octosense-repair-m1r1",
    "version": "0.1.0-m1r1",
    "blake3": "<… in results>",
    "signature_key_id": "test-publisher-m1r1",
    "main_splash_sha256": "ab0fbd5e476a647cff6f27de3ce1caa7485f5ade159e377b8471b02d4dd908a0"
  },
  "install": {
    "octosense-repair-m1r1": {
      "probe_rc": 0,
      "may_run": "ok caps={\"storage\"}, hosts={}, agent_present=false"
    }
  },
  "host_runs": {
    "1280x800": {"launched_seen": true, "eval_bytes_max": 85859, "capture_bytes": 1778864, "residue_status": "NONE", "pgrep_rc": 1, "wall_seconds": 11.21, "exit_method": "quit_during_wait"},
    "1440x900": {"launched_seen": true, "eval_bytes_max": 85859, "capture_bytes": 1781996, "residue_status": "NONE", "pgrep_rc": 1, "wall_seconds": 10.9, "exit_method": "quit_during_wait"},
    "980x760":  {"launched_seen": true, "eval_bytes_max": 85859, "capture_bytes": 1781996, "residue_status": "NONE", "pgrep_rc": 1, "wall_seconds": 10.91, "exit_method": "quit_during_wait"}
  },
  "keys_deleted": [
    "runtime/optimization/2026-10-09/M1/r1/keys/anchor.json",
    "runtime/optimization/2026-10-09/M1/r1/keys/publisher.json",
    "runtime/optimization/2026-10-09/M1/r1/keys/anchor.cert.txt"
  ],
  "keystore_state_after": [],
  "needs_abram": false,
  "status": "READY_FOR_REVIEW",
  "do_not_modify": [
    "app/bundle/main.splash.v1.bak",
    "app/bundle/main.splash.debug.bak",
    "app/bundle/host.log",
    "app/bundle/.archive/",
    "app/bundle/runtime/"
  ]
}
```

## 11. 衔接

- 候选清单、原生截图（`logs/frame-m1r1-{1280x800,1440x900,980x760}.png`）、launcher 日志、回执/状态证据（`results/install-and-host-m1r1.json` + `home/.octosense/apps/octosense-repair-m1r1/state.json`）。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS` 等待独立 Review。
- 不进入 M2。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（G0-B / G0-E 已按 Abram 裁决延期；本轮不触碰 AppHub publish / 上架 / 公开签名 / 真实 provider / 业务身份变更）。
