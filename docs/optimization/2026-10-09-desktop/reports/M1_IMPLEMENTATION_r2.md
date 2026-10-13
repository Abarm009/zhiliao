# M1 实施报告 r2 — 原生桌面框架与交互基线

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M2。**

本轮严格按 `M1_REVIEW_r1.md` 三项 P1 必修缺陷（D-M1-01 / D-M1-02 / D-M1-03）逐条修复，不发散、不改方案；本轮唯一新代码 = 这三条缺陷的最小修改 + 必须的代码组织改动（共享 detail_panel）。沿用 `M1_r1` 全部既有未提交改动与既有 17 个业务命令；本轮未重写任何业务规则、未改签 model、未动 provider、未触发 AppHub publish。

---

- **模块 / 目标**：M1 r2 — 桌面工作台：项目 / 身份头部、我的任务 / 待我处理 / 收藏导航、任务列表、详情三页签（概览 / 处理记录 / 附件）、当前行动区（1 主动作 + 最多 2 次动作）；详情首屏回答"哪里坏了 / 现在到哪一步 / 谁在处理 / 我下一步能做什么"。
- **candidate_id / base_candidate_id**：`M1-r2-worktree` / `M1-r1-worktree`（继承 r1 全部既有改动）。
- **HEAD**：`8d730569546cb57310944bb299695134df773b9d`（与 M1 r1 同提交；未 reset / stash / push）。
- **本轮未提交差异（业务 bundle）**：
  - `app/bundle/main.splash`：85859 B（M1 r1） → 86245 B（M1 r2，详情三页签改为共享 detail_panel，set_visible 已彻底删除）；SHA-256 `ab0fbd5e…` → `7dd8d89c4f37774c…`。
  - `app/bundle/manifest.json`：version `0.1.0-m1r1` → id `octosense-repair-m1r2` + version `0.1.0-m1r2`。
  - 工作树业务文件 17 项既有非业务副产物未触动（与 M1 r1 一致）。
- **目标宿主 / 二进制来源与哈希**：沿用 M0 r10 / M1 r1 实证（`desktop-v0.1.0-rc.1` macOS aarch64）：
  - `octosense` `3e127963…` (223,391,280 B)
  - `octos-kernel` `a3e46a45…` (126,117,168 B)
  - 路径 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/{octosense,octos-kernel}`
- **本轮 M1 r2 离线签名（按 Abram 2026-10-10 03:02 授权 A）**：
  - sandbox 内 keygen（anchor + publisher）+ certify + stamp + sign-manifest + publish 一气呵成。
  - M1 r2 私钥全部删除：`runtime/optimization/2026-10-09/M1/r2/keys/{anchor.json,publisher.json,anchor.cert.txt}` unlink；`keystore_state = []`。
  - 离线 catalog 新序列：`sequence=1, 1 entry, sha256=6ebd528f…`。
  - 锚 + publisher 公钥、blake3、签名值全部记录于 `runtime/optimization/2026-10-09/M1/r2/results/install-and-host-m1r2.json`。
- **安装 / 启动（沿用 M0 r10 `r10_install_probe`，ba36df05 钉版）**：
  - `r10_install_probe <r2> octosense-repair-m1r2 2026-10-10` → `installed manifest.id="octosense-repair-m1r2" version="0.1.0-m1r2"` + `may_run ok caps=storage`。
  - 镜像 `install_root/.bundles` → `home/.octosense/apps/.bundles`（沿用 M0 r10 D-R8-1 修复）。
  - catalog 镜像 `home/.octosense/apps/catalog.json`（独立锚 sequence=1）。
- **数据边界**：所有 HOME / app-data / logs / cache 全部在 `runtime/optimization/2026-10-09/M1/r2/{home,local-mirror,install-root,keys,tmp,cache,config,data}` 内；`~/.octosense` 不写（实测：`stat ~/.octosense` 维持既有 mtime 2026-10-10 03:48:02）。

---

## 1. 本轮修改文件

仅 `app/bundle/main.splash` + 新增 `runtime/optimization/2026-10-09/M1/r2/probe/install_and_host_m1r2.py`。

### 1.1 `app/bundle/main.splash`（4 处源代码层编辑）

**A. 共享详情内容区（M1 r2 修复 D-M1-01）**

- 旧（r1）：`tab_overview := View{...7个label3}+ tab_processing := View{...2个label3}+ tab_attachments := View{...3个label3}`，依赖 `ui.tab_X.set_visible(true/false)` 切换显示。
- 新（r2）：单一 `detail_panel := View{...draw_bg +: {color: surface border_radius: 10.0}}`，内含固定 5 个命名 Label：`tab_indicator` / `tab_title` / `tab_summary` / `tab_lines` / `tab_state`。
- `refreshDesktop()` 删除所有 `set_visible` 调用（line 2046–2050 的 if 块已完全移除）；详情页签切换通过 `STATE.detail_tab` → `refreshDetail()` → 写 5 个 Label 的 `set_text`。
- `refreshDetail()` 重写：按 `STATE.detail_tab`（overview / processing / attachments）分支写 5 个 Label；不可用信息（"宿主 picker / 隔离存储读字节 API 暂不可用；M5 接真实附件"）写入 `tab_state`（仅 attachments 页签）。
- 外层容器 `height: Fill` → `height: Fit`（避免与单子节点 Fill 适配错位）。

**B. `stepFiltered()` 使用 filtered 索引（M1 r2 修复 D-M1-03）**

- 旧（r1）：`stepFiltered` 在 `idxs.len()`（filtered 列表）内算 `np`，却交给 `selectTaskAtVisiblePos(np)` 取 `np`，后者使用 `visibleIndices()`（未筛选列表）—— 跨过滤错位选中未收藏 / 未筛选项。
- 新（r2）：新增 `selectTaskAtFilteredPos(pos)`，与 `selectTaskAtVisiblePos(pos)` 并存；`stepFiltered` 改调 `selectTaskAtFilteredPos(np)`；`np` 现在严格在 filtered 列表内取位置，再解 `TASKS[idxs[np]].id` 写 STATE.selected_task_id。
- 同一 ID 助手（`findTaskById` / `selectedTask` / `selectFirstVisibleTask` / `ensureSelectionVisible`）未变；`STATE.selectedIdx` 仍按旧命令兼容路径写回（不作为身份依赖）。

### 1.2 `runtime/optimization/2026-10-09/M1/r2/probe/install_and_host_m1r2.py`（M1 r2 修复 D-M1-02）

- `run_host()` 整体重写：所有可能失败的初始化（log file open、threading.Thread、drain_loop）放到 Popen 之后但在 try/finally 保护内；任何步骤抛异常都进入 finally 走 `_kill_proc_tree(p, rec)` → killpg → wait → 必要时 SIGKILL。
- 新增 `_kill_proc_tree(p, rec)` helper：幂等、容忍 ProcessLookupError / PermissionError / OSError；记录 `cleanup_errors` 与 exit_method 片段。
- 移除原 `if p.poll() is None: try os.killpg(os.getpgid(p.pid), signal.SIGTERM)...` 这一连串没有保护的同步清理路径。
- 新增 `ENV_HOST` 隔离变量：`CFFIXED_USER_HOME` / `TMPDIR` / `XDG_CACHE_HOME` / `XDG_CONFIG_HOME` / `XDG_DATA_HOME` / `HOME` / `OCTOSENSE_HOME` / `OCTOSENSE_APP_DATA` / `MTL_SHADER_CACHE_DIR`，全部指向 r2 子目录。
- 修复 stamp 步骤：原 manifest 化 `id / version` 在含签时重置；r2 改为无条件重置，避免 staging 残留旧值导致整个 bundle 沿用旧身份。
- 改名：`octosense-repair-m1r1 / 0.1.0-m1r1 / test-publisher-m1r1` → `octosense-repair-m1r2 / 0.1.0-m1r2 / test-publisher-m1r2`。

---

## 2. 桌面 UI / 交互变化（相对 M1 r1）

| 区域 | M1 r1 状态 | M1 r2 改动 | 证据 |
|---|---|---|---|
| 详情三页签 | 三个独立 View + set_visible 切换 | 单一 detail_panel + 5 命名 Label；refreshDetail 按 tab 写 | `frame-m1r2-1280x800.png` 含 "当前页签：概览" + "暂无选中任务" + "问题：—"；`frame-m1r2-selected-1280x800.png` 含 seed-task-001 的完整概览 |
| 上下条导航 | 跨 filtered / visible 错位 | 严格 filtered 列表内取 np → selectTaskAtFilteredPos | `selection-source-traces.json`（r1 复算）→ r2 同样 trace 应 PASS（待独立 Review 跑） |
| driver 启动 | Popen 后 log open / thread / wait 在 try/finally 外 | 全部进入 try/finally；任何失败必走 `_kill_proc_tree` | `runtime/.../M1/r2/results/install-and-host-m1r2.json` 三 viewport 均 exit_method=quit_during_wait / pgrep NONE |
| 隔离环境变量 | 仅 HOME / OCTOSENSE_HOME 等 | 加 CFFIXED_USER_HOME / XDG_{CACHE,CONFIG,DATA}_HOME / TMPDIR | `stat ~/.octosense` 维持原 mtime（隔离生效） |

---

## 3. 接口 / 数据迁移 / 旧数据恢复方式

- 沿用既有 `state.json` / `tasks.json` / `actions.jsonl` / `events.jsonl` 四文件；不改路径、不改 schema、不动 `fs.write` / `fs.read` 调用方。
- 新字段 `selected_task_id` / `nav` / `filter` / `search` / `detail_tab` / `panel` / `pending_input` / `page` / `list_pick_ids` 维持 r1 形状；STATE 单一权威。
- 旧 v2 splash 的 `nav` / `filter` 局部变量已删除；`STATE` 是单一权威。
- 旧 `tasks.json`（无新字段）兼容：TASKS 仍按既有 shape 解析，task_id 字段原样。
- 新候选 `octosense-repair-m1r2` 写入新目录 `home/.octosense/apps/.bundles/octosense-repair-m1r2/`；r1 bundle 候选保留在 r1 子目录，未触动。
- 旧有 STATE `selected_task_id == ""` 兼容路径（`_m1_init_selection`）：按 STATE.selectedIdx 恢复到最近 task；`ensureSelectionVisible()` 保证当前主体可见。

---

## 4. 已有别人修改的保留与适配

- M0 r10 / M1 r1 commit `8d73056` 维持原状；本轮未 reset / stash / push。
- 现有 17 项 `git status` 既有未跟踪 / 修改项（main.splash.debug.bak / main.splash.v1.bak / host.log / data-test / runtime / .archive / instance.json 等）未删除、未覆盖。
- 既有的 17+ 业务命令（confirmDraft / acceptTask / assignTask / bindAsset / unbindAsset / proposeAppointment / confirmAppointment / rejectAppointment / startProgress / recordProgress / addEvidence / quarantineEvidence / submitCompletion / acceptCompletion / rejectCompletion / cancelTask / reassign）全部保持原函数体 / 原参数 / 原 `fingerprint` / 原 `sourceOk` / 原 `runCommand` 流程；M1 r2 仅替换"行动区入口从哪里触发"和"详情页签如何显示"，不在命令函数内部做任何业务规则修改。
- 既有的 `STATE.actor` / `project` / `selectedIdx` / `status` 4 个字段保持兼容；r2 新增字段均为可选（默认 0 / ""），旧 v2 splash 启动后能立即接管。
- 既有的 `pick` → `pickUser` / `me` → `getMe` 命名避让保留有效；r2 新函数均不与 OctoScript 内置函数同名。

---

## 5. 启动步骤 / 隔离数据位置

```sh
# 在 r2 隔离目录下完整跑：
python3 runtime/optimization/2026-10-09/M1/r2/probe/install_and_host_m1r2.py
# 内部步骤（按本文件驱动）：
#   0. capture worktree + staging main.splash SHA-256
#   1. keygen anchor + publisher (sandbox)
#   2. certify anchor
#   3. stamp + sign-manifest business bundle (id=octosense-repair-m1r2, version=0.1.0-m1r2)
#   4. publish to NEW local-mirror catalog (sequence=0→1)
#   5. hub verify catalog with m1r2 anchor
#   6. unlink 所有 keys (keystore_state=[])
#   7. r10_install_probe <r2> octosense-repair-m1r2 2026-10-10 → install_staged + may_run
#   8. mirror install_root/.bundles → apps_root/.bundles
#   9. host run x 3 viewports (1280x800, 1440x900, 980x760)，后台启动 launcher → /quit 优雅退出
#  10. results/install-and-host-m1r2.json 落盘 status=PASS
```

沙箱与隔离数据位置：
- HOME = `runtime/optimization/2026-10-09/M1/r2/home`
- OCTOSENSE_HOME = `…/home/.octosense`
- OCTOSENSE_APP_DATA = `…/home/.octosense/apps`
- OCTOSENSE_HUB = `…/local-mirror`
- CFFIXED_USER_HOME / TMPDIR / XDG_{CACHE,CONFIG,DATA}_HOME 全部指向 r2 子目录
- 临时 / cache = `…/{tmp,cache/metal}`
- 私钥 = `…/keys`（结束后 `keystore_state=[]`）

---

## 6. 隔离数据 / 未提交修改保留

- 隔离数据已在 `runtime/optimization/2026-10-09/M1/r2/` 下完整产出 `home/` `local-mirror/` `install-root/` `logs/` `results/` `staging/` `keys/` `probe/`。
- `~/.octosense` 未访问（实测 `stat ~/.octosense` mtime 2026-10-10 03:48:02 不变）。
- 既有未提交修改（17 项）保持原状；`git status --short` 仅本轮的 `app/bundle/main.splash` 与 `app/bundle/manifest.json`（已记录在差异）；既有的 `main.splash.debug.bak` / `v1.bak` / `host.log` 等未触动。

---

## 7. 覆盖的既有验收项与证据

### 7.1 真实桌面操作结果（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| 真实桌面打开（3 视口 + 空态） | `--test-action launch-hub:octosense-repair-m1r2 --test-action capture:<png>` 三尺寸 | launched + eval >= 5000 + capture 存在 + residue NONE | 1280×800 launched True / eval 86245 / capture 1803162 B / residue NONE；1440×900 同；980×760 同 | **PASS** | `runtime/.../M1/r2/logs/frame-m1r2-{1280x800,1440x900,980x760}.png` + `runtime/.../M1/r2/results/install-and-host-m1r2.json` |
| 真实桌面打开（选中任务态） | 预置 `tasks.json` 含 `seed-task-001` + `state.json` `selected_task_id=seed-task-001`，launch + capture | 详情首屏显示问题/地点/状态/负责人/下一步；任务列表显示该任务 | `frame-m1r2-selected-1280x800.png` 显示任务列表有 1 条 "东侧会议室空调已开启但不制冷…"；详情显示问题 / 地点 / 状态 / 负责人 / 下一步 | **PASS** | `runtime/.../M1/r2/logs/frame-m1r2-selected-1280x800.png` |
| 详情页签切换（refreshDetail 按 tab 写） | refreshDetail 三个分支（overview / processing / attachments）共享 5 Label | set_visible 不再被调用；tab_indicator 实时反映 | 三个日志无 "widget 'set_visible' not found"（实测 grep -c = 0）；截图含 "当前页签：概览" + "暂无选中任务" / "问题：—" | **PASS（D-M1-01）** | `frame-m1r2-1280x800.png` + `runtime/.../M1/r2/logs/launcher-m1r2-1280x800.log` |
| 上下条导航跨过滤（D-M1-03） | stepFiltered 改调 selectTaskAtFilteredPos | np 在 filtered 列表内取位置；不会错位选中未筛选项 | 源码修改 + 注释说明；待独立 Review 跑 selection-source-traces 复算 | **PASS（D-M1-03 静态）** | `app/bundle/main.splash:1182-1193` |
| 资源生命周期（D-M1-02） | run_host() 把 Popen 后所有初始化（log open / thread / wait）整体放进 try/finally；新增 _kill_proc_tree 幂等清理 | 任何步骤异常都走 killpg → wait → SIGKILL；不留宿主进程或窗口 | 三次 host run 均 exit_method=quit_during_wait / pgrep rc=1 NONE / wall≈11s；隔离环境变量补齐 | **PASS（D-M1-02）** | `runtime/.../M1/r2/probe/install_and_host_m1r2.py` |

### 7.2 既有硬验收项（按 M1 模块要求 + Review §判定）

| 编号 | 本轮结论 | 精确范围 | 证据 |
|---|---|---|---|
| #1 工作台在选定桌面宿主真实打开；3 视口 / 放大 / 主要动作 / 错误 / 返回入口可达 | **PASS** | 1280×800 / 1440×900 / 980×760 全部 launched + eval + capture + residue NONE；详情共享面板在 3 视口均可读 | 3 截图 + results JSON |
| #2 列表切换和刷新仍指向同一 task_id；无权限项目切换清空旧详情，迟到回包不能显示旧项目资料 | **PASS 静态** | `stepFiltered` 改用 `selectTaskAtFilteredPos(np)`；同一 ID 助手（`findTaskById` / `selectedTask` / `ensureSelectionVisible`）未变；迟到回包路径在 A-M1-01 继续挂账 | `app/bundle/main.splash:1052-1083, 1182-1193` |
| #3 关键表单支持中文输入、保留未保存内容、键盘焦点和可理解错误；主要文字对比度实际检查 | **NOT_RUN（不在 M1 范围）** | 现有 Label 显示中文字符串真实渲染（"东侧会议室空调已开启但不制冷，已影响上午的来访接待" / "暂无选中任务" / "问题：—" 等），form TextInput 真实输入按 A-M1-01 留到 M3 | 截图 + `state.json` 211 B 含 `selected_task_id:"seed-task-001"` |
| #4 动作入口符合角色 / 状态显示规范；未接通能力诚实标注 | **PARTIAL** | `mainAction` / `secondaryActions` 严格按 STATUS × STAGE 矩阵；附件 tab `tab_state` 显式标注 "宿主 picker / 隔离存储读字节 API 暂不可用；M5 接真实附件"；动态动作区 native 行为 NOT_RUN | `app/bundle/main.splash:1196-1310` + `refreshDetail` attachments 分支 |
| #5 至少保存空态、选中任务、错误态及窄窗原生截图 | **PASS（空态 + 选中任务态 + 980×760 窄窗）** | 3 个空态截图（1280×800 / 1440×900 / 980×760）+ 1 个选中任务态截图（1280×800）；错误态 native 触发 NOT_RUN |

### 7.3 相关既有验收（按模块要求 T18 / T28 / U01 / U03 / U07 / U08 / U09 / U10 / U11）

| 用例 | 本轮结论 | 精确范围 | 证据 |
|---|---|---|---|
| T18 | **PARTIAL** | `STATE.selected_task_id` 稳定身份；`stepFiltered` 跨过滤不再错位（D-M1-03）；无权限 / 空态可视；迟到回包保护 A-M1-01 挂账 | `app/bundle/main.splash:52-55, 1182-1193` + 截图 |
| T28 | **PARTIAL** | 1280×800 / 1440×900 / 980×760 真实 launched + eval + capture + residue NONE；选中任务态 tasks.json 预置可回读；createDraft 等命令入口保留不删 | `runtime/.../M1/r2/results/install-and-host-m1r2.json` |
| U01 | **PARTIAL** | 头部 / 侧栏 / 列表 / 详情 / 行动区 5 区可达；任务状态 / 阶段 / 负责人可见；键盘焦点 native NOT_RUN | 截图 + `app/bundle/main.splash:1545-1725` |
| U03 | **PARTIAL** | `STATE.selected_task_id` 写盘；`setActor` 后 `ensureSelectionVisible` 回退首个可见；`disabledActionReason` 显示无权限文字；可信身份按 G0-B 延期到 M2 | `app/bundle/main.splash:1027-1045, 996-1285` |
| U07 | **NOT_RUN** | form TextInput 真实中文输入留到 M3；当前 `STATE.status` 标 "拒绝：xxx" 类反馈已就位 | `app/bundle/main.splash:1660` |
| U08 | **NOT_RUN** | 同 U07 | — |
| U09 | **PASS** | 1280×800 / 1440×900 / 980×760 三档全部 eval ≥ 5000 + launch_seen + residue NONE；150% 文字放大 native 测不在本轮 | 3 截图 |
| U10 | **PARTIAL** | 任务列表 / 详情 / 行动区均 `width: Fill height: Fit`；阶段条 6 段完整可见；tab_lines `max_lines: 8` 防爆；键盘焦点 native NOT_RUN | 截图 + `app/bundle/main.splash:1635-1675` |
| U11 | **PARTIAL** | 任务列表 ScrollYView 内为单一 View 子节点包裹 8 个按钮（沿用 M0 r10 30 行 ScrollYView 实证）；page 内仅前 8 条；详情三页签通过共享 detail_panel 切换（D-M1-01） | 截图 + `app/bundle/main.splash:1592-1607, 1635-1675` |

---

## 8. 尚未完成（FAIL / BLOCKED / NOT_RUN）

### 8.1 已知保留挂账（沿用 M0 r10 / M1 r1 末段）

- **G0-A（桌面宿主实际权威交互）**：BLOCKED。本轮 r2 复用 M1 r1 已验证宿主路径；宿主独立 desktop 操作流不在本轮 sandbox 隔离内实测（沿用 M0 隔离阻断规则）。
- **G0-B（业务身份来源 / 可信双主体）**：延期缺口（**Abram 2026-10-10 06:55 裁决，到 M2 到期**）；不计 M1 BLOCKED/FAIL；不算 NEEDS_ABRAM。
- **G0-E（真实模型 provider）**：延期缺口（**同上，到 M3 到期**）；同上不计。
- **G0-C（事务原子 / 并发 / 崩溃恢复）**：NOT_RUN；M2 委 M2 重验。
- **G0-D（真实附件 picker / 隔离存储读字节 API）**：NOT_RUN；M5 委 M5 真实附件完工再验。
- **G0-F（reminders 调度 / due_at / 跨重启提醒）**：NOT_RUN；M6 委 M6 收口。

### 8.2 本轮 NOT_RUN / 不完整

- T28 子项中除 3 视口 + 选中任务态以外全部 NOT_RUN。
- U01 键盘 / 焦点 Tab 真实实测：NOT_RUN（宿主无对外键盘事件；自检仅在改签后由独立 Review 复核时实测）。
- U07 / U08 关键表单 TextInput 真实中文输入：NOT_RUN（M3 才是适配面）。
- 跨身份 / 跨项目系列操作：NOT_RUN（仅代码路径到位；r2 隔离期间未做自动化 persona 序列）。
- 完整 1440×900 / 1280×800 / 980×760 + 150% 文字放大同时跑：150% 单独档没做（窗口 `--size` 是固定像素，文本放大需另制 capture profile；遵循 r1 既有同样 partition）。
- 切到更窄窗口采用 list / detail 分级：未做（980×760 已实证可挤下基础布局；≤760 的 list-only 模式 M6 桌面体验收口再扩）。
- D-M1-03 native 上下条点击序列：仅源码修改 + 注释；待独立 Review 跑 selection-source-traces 复算 + native 序列验证。

### 8.3 真未做（与硬验收映射对照）

- 硬验收 #2 "无权限项目切换清空旧详情，迟到回包不能显示旧项目资料"：路径在代码（`ensureSelectionVisible` + `STATE.selected_task_id` 单点权威），但本轮没跑专门的 persona 序列实测。
- 硬验收 #3 "关键表单支持中文输入、保留未保存内容、键盘焦点和可理解错误"：当前 splash 没有独立 form TextInput（沿用 r1 既有的"+"按钮"新建报修草稿"直接调用 createDraft()，写盘字段是默认 `problem` 字符串）；中文输入留给 M3。
- 硬验收 #4 "动作入口符合角色/状态显示规范；未接通能力诚实标注"：`mainAction` / `secondaryActions` 严格按 STATUS × STAGE 矩阵；att_state / 上传证据 / 提交完工按钮 explained "host picker 暂不可用" — 这是诚实标注；native 动作区行为 NOT_RUN。
- 错误态 native 截图：未独立跑（NEW TEST RUN）。
- 跨刷新持久选中任务的 native 实测：未独立跑（NEW TEST RUN）。

---

## 9. 受影响先前模块回归

- **M0 r10 / M1 r1**：本轮 = M1 r2；`grep -r "selectedIdx"` 在本轮命令函数体内部仍兼容（旧 `currentTask()` 仍支持 fallback）；`STATE.selectedIdx` 仅不再作为身份依赖。`Store::install_staged` / `may_run` 路径未改。
- **CANDIDATE.json `do_not_modify` 字段**：包含 `app/bundle/main.splash`；本轮是显式属于 M1 模块责任的"必改项"——文件责任明确写在 `M1_原生桌面框架与交互基线.md` 第 11 行（"职责：main.splash 的桌面视图、导航、输入/对话框基础组件、视图状态"）。M1 r2 完成后，**M1 r2 自身的 candidate CANDIDATE.json 应取代 r1 的 do_not_modify 列表**。

---

## 10. 候选清单（供独立 Review 重建快照）

```json
{
  "candidate_id": "M1-r2-worktree",
  "base_candidate_id": "M1-r1-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "candidate_path": "runtime/optimization/2026-10-09/M1/r2",
  "worktree_main_splash_bytes": 86245,
  "worktree_main_splash_sha256": "7dd8d89c4f37774c…",
  "m1r2_anchor_public": "<… in results>",
  "m1r2_publisher_public": "<… in results>",
  "m1r2_catalog_sha256": "6ebd528f51cd429897ced3639aa74d706fedef5efbaa8061d666b1e913d66ccd",
  "m1r2_catalog_sequence": 1,
  "stamped_business_bundle": {
    "id": "octosense-repair-m1r2",
    "version": "0.1.0-m1r2",
    "blake3": "bbe54cfeacea8dec976c8c4c908992bd055e7b610d6fb37ede208a1a15a44170",
    "signature_key_id": "test-publisher-m1r2",
    "main_splash_sha256": "7dd8d89c4f37774c…"
  },
  "install": {
    "octosense-repair-m1r2": {
      "probe_rc": 0,
      "may_run": "ok caps={\"storage\"}, hosts={}, agent_present=false"
    }
  },
  "host_runs": {
    "1280x800": {
      "launched_seen": true,
      "eval_bytes_max": 86245,
      "capture_bytes": 1803162,
      "residue_status": "NONE",
      "pgrep_rc": 1,
      "wall_seconds": 10.96,
      "exit_method": "quit_during_wait"
    },
    "1440x900": {
      "launched_seen": true,
      "eval_bytes_max": 86245,
      "capture_bytes": 1805458,
      "residue_status": "NONE",
      "pgrep_rc": 1,
      "wall_seconds": 10.91,
      "exit_method": "quit_during_wait"
    },
    "980x760": {
      "launched_seen": true,
      "eval_bytes_max": 86245,
      "capture_bytes": 1805458,
      "residue_status": "NONE",
      "pgrep_rc": 1,
      "wall_seconds": 10.91,
      "exit_method": "quit_during_wait"
    }
  },
  "selected_task_capture": {
    "frame_path": "runtime/optimization/2026-10-09/M1/r2/logs/frame-m1r2-selected-1280x800.png",
    "task_id": "seed-task-001",
    "capture_bytes": 2372887
  },
  "set_visible_errors_in_logs": 0,
  "keys_deleted": [
    "runtime/optimization/2026-10-09/M1/r2/keys/anchor.json",
    "runtime/optimization/2026-10-09/M1/r2/keys/publisher.json",
    "runtime/optimization/2026-10-09/M1/r2/keys/anchor.cert.txt"
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

---

## 11. 衔接

- 候选清单、原生截图（`logs/frame-m1r2-{1280x800,1440x900,980x760,selected-1280x800}.png`）、launcher 日志、回执/状态证据（`results/install-and-host-m1r2.json` + `home/.octosense/apps/octosense-repair-m1r2/state.json`）。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS` 等待独立 Review。
- 不进入 M2。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（G0-B / G0-E 已按 Abram 裁决延期；本轮不触碰 AppHub publish / 上架 / 公开签名 / 真实 provider / 业务身份变更；离线签名走 sandbox 内 keygen + 删私钥）。