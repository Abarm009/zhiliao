# M4 实施报告 r12

- 模块 / 目标：M4 接单设备与预约桌面流程 —— 修复轮，审查输入 **M4_REVIEW_r13**（结论 BLOCKED）。本轮只修 r13 缺陷清单中构建方可执行的唯一项 **A-M4-R13-01**（P2：任务坏盘恢复说明未到登录反馈出口）；其余清单项按裁决保持。
- candidate_id / base_candidate_id：**M4-r12-worktree / M4-r11-worktree**。
- HEAD / 未提交差异 / 源文件哈希：`8d730569546cb57310944bb299695134df773b9d`（dirty，共享工作树）。`app/bundle/main.splash` = **769874 B / SHA256 `07ecd2fddcfea116151378e8f1dd1e41cefd333f4c703d442bb1ae20cbb88b2a`**。与 r13 受审冻结源（765252 B / ae25feb4…）总差量 15 hunks +81/-32：其中本模块仅 1 hunk，其余为其他模块修复轮推进（全保留，未 reset/stash/删除）。
- 目标宿主 / 二进制来源与哈希：固定宿主 host-rc6 `runtime/optimization/2026-10-09/M0/r3/host-rc6/app-extracted/OctoSense.app`（Abram 16:45 批准切换；SHA 见 r13 审查 `2686e399…`）。本轮构建方不启动宿主。
- 实际模型路由检查结果：本会话为 Kimi-K3（Abram 2026-10-11 21:03 指定构建方）；无 Router 切换能力声明。
- 已检查的前置 PASS 报告：**无**。M3=BLOCKED（M3_REVIEW_r14）、M2 carried；沿用挂账裁决局部推进，不声称前置满足。
- 本轮修改文件与原因：
  - `app/bundle/main.splash`（1 hunk，`refreshDesktop`）：A-M4-R13-01 —— 任务盘恢复未决时，既有登录反馈出口 `ui.login_hint`（即 M2_RECOVERY_NOTICE 同一出口）前置任务盘恢复说明。文案**复用既有** `m7_tasks_mark_corrupt` 写入 `STATE.status` 的说明（含原因/备份路径 `tasks.json.recover`·`tasks.json.corrupt.latest`/副本读回核实摘要）；`STATE.status` 为空时回退既有 `m7_tasks_banner_text()`。**不新增页面/控件/字段**（13:14 硬规则合规；接线块内无 set_visible、无新 ui.* 成员，核验 WIRE-04）。
- 桌面 UI/交互变化：仅登录页提示文字在任务盘恢复未决时多一行 ⚠ 说明；布局/样式/控件命名不变。
- 接口 / 数据迁移 / 旧数据恢复方式：无接口变化；`m7_tasks_mark_corrupt` 保源备份逻辑（recover 不覆盖、corrupt.latest 另存读回核实）未动。
- 已有别人修改的保留与适配：共享工作树其他模块 diff 全保留；本 hunk 只追加在 `refreshDesktop` login_hint 段，不改他人逻辑。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。原生验证请求 `runtime/optimization/2026-10-09/M4/native/REQUEST_build_r12.json`（4 场）交驱动沙箱外执行；隔离数据 `M4/native/build_r12/` 与 `M4/native-runs/`。
- 应用运行模型/provider：needs_model=false，本轮 MiniMax 0 调用；无密钥入代码/日志/报告。
- 离线签名：digest 变化（`a6a5c30576a4432f2206013d2d903de9fef3eeed86d7d5b38201c49930ed9b97`），按授权 A 在隔离目录重新签名（`prepare_build_r12.py`，anchor `3321ee0c…`）；私钥已删，证据 `M4/native/build_r12/offline-store-evidence.json`（working.key/anchor.key exists_after=false，keys 目录空）。不联网、不上传、不 publish/listing。

## 缺陷清单逐条回写（按 r13 原编号）

| 编号 | r13 状态 | 本轮处理 | 证据 |
|---|---|---|---|
| D-M4-03 | BLOCKED-HOST（不计 P1） | 按裁决不修宿主、不加服务；安全拒写/保源守卫盘点 **41/41 保持** | r12/evidence/guard_verifier.json（ACQ/REL/CC/RCB/CB/PARSE 全过） |
| B-M4-01 | CLOSED 子项保持 | 未动；PARSE-01/02 核验保持 | 同上 |
| D-M4-04 | SOURCE-CLOSED 保持 | 未动；INV-01 核验保持 | 同上 |
| A-M4-R12-01 | CLOSED（r11 文案） | 无需再处理 | M4_IMPLEMENTATION_r11.md |
| **A-M4-R13-01** | **P2 建议（唯一可执行项）** | **已按审查方方案接线**：既有任务恢复说明 → 既有登录反馈出口；新增 WIRE-01..06 静态核验 **6/6** | r12/evidence/guard_verifier.json；原生同屏验证待 REQUEST_build_r12 场景 3/4 |
| B-M4-TEST-R13-01 | 覆盖缺口 | **仍 BLOCKED**：同 Store 双原生上下文同步/提交点故障/受控 AI 交错入口属 harness/驱动侧，构建方不可修；不新增功能 | r13 报告 §白名单覆盖阻塞 |

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r12 4 场（launch-hub+capture）|冷开零错误、登录页渲染、坏盘场同屏恢复说明|待驱动执行|**NOT_RUN（待回读）**|M4/native/REQUEST_build_r12.json|
|权威状态与回执|—|—|—|NOT_RUN（可信登录通道 BLOCKED 沿用）|—|
|失败与重试|场景 3/4（bool version / 截断盘）|整盘拒+保源+同屏说明|静态接线核验过；原生待回读|NOT_RUN|同上|
|重启恢复|场景 2（future 锁）|锁逐字保留、token 空|原生待回读|NOT_RUN|同上|
|受影响先前模块回归|场景 1 冷启动渲染回归|零解析/运行错误、不回归|原生待回读|NOT_RUN|同上|
|静态守卫盘点|m4_r12_guard_verifier.py|47/47|**47/47 rc=0**|**PASS（静态）**|M4/r12/evidence/guard_verifier.json|

## 尚未完成

- D-M4-03：BLOCKED-HOST 挂账（宿主无原子替换/持有期锁原语）；代码保持安全拒写并保源，不宣称闭合。
- B-M4-TEST-R13-01：同盘双原生上下文同步/提交点故障/AI 交错控制入口缺，BLOCKED（驱动/harness 覆盖缺口）。
- 可信登录后业务主链（M3 建单→接单→设备→预约→开工）、三角色、硬1/2/4/5 及 T04–T35/U01–U07 动态项：NOT_RUN（输入/登录通道与 M3 前置 BLOCKED 沿用）。
- REQUEST_build_r12 原生结果：待驱动沙箱外执行后回读，本报告不构成原生 PASS 自述。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M4/r12/CANDIDATE.json`（digest `a6a5c305…`，anchor `3321ee0c…`）。
- 脚本/证据：`M4/r12/scripts/m4_r12_guard_verifier.py`（47/47）、`M4/r12/evidence/guard_verifier.json`、`M4/native/prepare_build_r12.py`、`M4/native/build_r12/offline-store-evidence.json`（私钥已删）。
- 原生请求：`M4/native/REQUEST_build_r12.json`（4 场：冷启动渲染回归 / future 锁回归 / 两个坏盘场 A-M4-R13-01 同屏验证；needs_model=false；无 wait:N）。
- 实际测试命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/r12/scripts/m4_r12_guard_verifier.py`（rc=0）；`PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python runtime/optimization/2026-10-09/M4/native/prepare_build_r12.py`（rc=0，PREPARED）。
- GATES 前态快照：`M4/r12/evidence/gates-before-build-r12.json`。
- 编码方仅标 READY_FOR_REVIEW；最终判定等待独立审查。无 git push / 发布 / 消息 / 公网部署。
