# M4 实施报告 r8

- 模块 / 目标：M4 接单设备与预约桌面流程 —— 修复轮，严格按 `M4_REVIEW_r9.md` 缺陷清单逐项修复，只修清单项：B-M4-01（坏任务盘恢复剩余子项）、D-M4-03（原子命令边界脚本侧 + 宿主原语最小复现/方案）。D-M4-04 已 SOURCE-CLOSED，仅保静态回归。
- candidate_id / base_candidate_id：`M4-r8-worktree` / `M4-current-M3-r8-cc193cf0-review-r9`（base = M4_REVIEW_r9 冻结诊断快照 `M4/native/review_r1_0937/source.main.splash`，即当前共享 M3-r8 工作树内容，已含 M4-r7 全部修复）。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=工作树未提交；`app/bundle/main.splash` SHA-256=`982b7c352da9a026a856faad75d0bf21f8b6ef36a9010ba1122acd45971c7267`（base `cc193cf0…` / 552591 B）；差异 `runtime/optimization/2026-10-09/M4/r8/evidence/r9frozen-to-r8.diff`（+271/-88 行，492 行 diff）。
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256=`3e1279635c…c2c90`，沿用 M4_REVIEW_r9 同一二进制）；harness 由驱动在沙箱外执行；本轮运输包 digest=`d9f2a769d26d09f0f9f333dc49fb78ec8b2e1f7acfd49f6af68f0ec6c91432d5`，anchor=`b38936f9e4d5439729077d86c79b2065d038b3a033bcf73cafd189789ac88e3c`。
- 实际模型路由检查结果（开发会话）：主会话为 Kimi-K3（Abram 2026-10-11 21:03 裁决构建方）；Router 细节不可由本会话核验，不冒称。
- 已检查的前置 PASS 报告：无已接受 PASS 的 M3（M3=BLOCKED / M3_REVIEW_r10，挂账沿用）；按用户前序挂账裁决继续本模块局部修复，不修前置。
- 本轮修改文件与原因（仅 `app/bundle/main.splash`，8 处 hunk）：
  1. **B-M4-01**：`m7_task_record_valid` 从"仅 id"升级为完整业务 schema 门禁——id/project/reporter 非空字符串、status 属 8 阶段白名单（新 helper `m7_known_task_status`）、version/createdAtMs/updatedAtMs 数字、appointments 数组；缺字段对象 TASKS 不再接纳。
  2. **B-M4-01**：`load()` 在宿主宽容 `parse_json` 之前先做独立首尾闭合校验（trim → to_chars → 首 `[` 尾 `]`），截断/未闭合直接 mark corrupt（why=「JSON 截断或顶层数组未闭合」），不再依赖宿主内部产物推断。
  3. **B-M4-01 关联回归（审查方 102 行备份细分）**：`m7_tasks_mark_corrupt` 检测路径不覆盖既有有效备份——`tasks.json.recover` 已存在且非空时保留原文，本次坏盘原文另存 `tasks.json.corrupt.latest` 并读回核实，status 明确说明。
  4. **B-M4-01**：`runCommandBound` 在授权之后、取锁之前新增 `tasks_pending_recovery` 显式拒绝（rejected 回执 + fail，事实与回执一致）。
  5. **B-M4-01**：创建路径 `createDraftFromPanel` 同步禁写（避免内存 push 后主写被拒的半提交）。
  6. **B-M4-01**：`m7_tasks_explicit_recover` 入口核 `identityActive(sessionActor())` 可信权限，未认证/撤权/到期拒绝；故障说明（banner + status）对未登录入口保持可见（UI 既有 `m7_tasks_banner_text`，未改 UI 结构）。
  7. **D-M4-03**：`_acquireTaskLock` 用 `fs.exists` 区分首次缺锁（合法首次获取，不再误报 read_failed）与真实读失败（fail-closed）；回应 r9「首次合法命令是否被拒仍 NOT_RUN，不能预置空锁掩盖」。
  8. **D-M4-03**：`commitBound` 提交点强制同 owner——token 空（未持锁）/锁文件不存在/锁内容与本进程 token 不全等（含被清空成 ""，r7 的空锁漏洞）一律 needs_verify 不写盘；写盘前最后一刻磁盘版本复核（创建 expected=0 豁免但盘不可解析 fail-closed）；跨任务冲突复核推进到提交点——新 helper `_m4_disk_tech_conflict` 与 runCommandBound 步骤 4 共用同一实现，spec 经 `_PENDING_CC` 传递、commitBound 进入即清零。
- 桌面 UI/交互变化：无新 UI 结构；坏盘时既有 banner/状态栏现在会真实出现（此前 pending 永不置位），恢复入口两 Chip 不变但恢复动作新增可信身份校验。
- 接口 / 数据迁移 / 旧数据恢复方式：无接口/迁移变化；损坏 tasks.json 恢复路径 = 左侧「恢复任务·保留原文 / 用内存覆盖」，均先备份读回核实再解除阻断；新增 `tasks.json.corrupt.latest` 仅为备份保全，不影响既有 recover 语义。
- 已有别人修改的保留与适配：base 为共享 M3-r8 工作树（含 M2/M3/M5/M6/M7 各轮修复），本轮 diff 只动上述 8 处 hunk；未 reset/stash/删除任何他人改动；M5/M6/M7 代码路径未触碰（fix_verifier 回归项覆盖 tick/D-M4-04 等共享段）。
- 启动步骤 / 隔离数据位置：构建方不启动宿主（Abram 2026-10-11 12:12 裁决）；原生验证请求 `M4/native/REQUEST_build_r8.json`（4 场），证据待驱动落 `M4/native-runs/build_r8_*/`；离线签名 store 与 seeds 在 `M4/native/build_r8/`（私钥已删，证据 `offline-store-evidence.json`）。
- 应用运行模型/provider：needs_model=false，本轮 MiniMax 0 调用；未读任何真实密钥。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作（冷启动回归）|REQUEST_build_r8 场1：预存 pending_input 冷开+capture|零解析错误、工作台渲染、原文/意图恢复|待驱动执行|NOT_RUN（harness 排队）|M4/native/REQUEST_build_r8.json|
|B-M4-01 截断盘恢复|场2：截断 tasks.json + 既有 recover=[] 冷开|pending=true、why 可读、主盘与 recover 逐字节保持、corrupt.latest 落盘核实、零循环错误|待驱动执行|NOT_RUN|同上|
|B-M4-01 缺字段盘恢复|场3：仅 id 合法 JSON 成员冷开|schema 门禁拒收、pending=true、无既有 recover 时备份为 recover 并读回|待驱动执行|NOT_RUN|同上|
|D-M4-03 锁回归|场4：未来他人完整 token 锁冷开|锁逐字保留、本进程 token 清空、业务盘不变|待驱动执行|NOT_RUN|同上|
|权威状态与回执（普通命令禁写/提交点复核）|需可信登录+输入通道|pending 拒写回执一致；提交点 owner/版本/冲突复核|宿主 type/key 输入通道仍 unknown|NOT_RUN（通道 BLOCKED）|源码静态核验 fix_verifier.json|
|受影响先前模块回归|fix_verifier 35/35 含 r7 全部 26 项回归|全绿|35/35 PASS|PASS（静态）|M4/r8/evidence/fix_verifier.json|

## 尚未完成

- 原生 4 场均 NOT_RUN：请求已提交，等驱动沙箱外执行后回读（本报告不预断结果）。
- D-M4-03 真跨进程原子互斥仍 **HOST_PRIMITIVE_BLOCKED**：宿主 fs 无 O_EXCL/flock/原子 rename，脚本侧只能把授权/版本/冲突复核推进到写盘前最后一刻并强制同 owner，核验→写盘之间仍存在竞争窗口；双可信上下文同盘同步接单/重叠确认「唯一成功」仍需宿主原语（见附录最小复现与方案）。
- 事件落盘（logEvent）在锁释放后执行：事件为全文件覆盖写，锁外存在丢更新窗口；缓解 = boot 对账按 final 回执补齐缺失事件（既有代码 4284 段）。把事件提交并入原子边界同样依赖宿主原语，一并列入附录方案。
- 可信三角色真实主链（M3→接单→设备→预约→开工）NOT_RUN：宿主 type/key 输入通道 unknown（M4_REVIEW_r7/r9 实证），不可用合成 seed/注入 SESSION 代验。
- T04/T05/T06/T07/T08/T09/T10/T11/T12/T13/T14/T15/T31/T35、U01/U03/U04/U05/U07 业务动态子项沿用 NOT_RUN/BLOCKED（见 r9 审查表），本轮未冒充。

## 附录：D-M4-03 宿主原语最小复现与方案（交驱动）

**最小复现（现宿主即可运行）**：两个独立宿主进程 A、B 指向同一隔离 Store；同时执行接单。两者 `_acquireTaskLock` 均读到空锁→各自写 stamp→各自读回自己的 stamp（最后写者赢，先写者读回也可能是自己——窗口在写与读回之间）；双双进入 commit，后写覆盖先写，read-back 不匹配只能事后 needs_verify。**这不是互斥**：期望行为是唯一成功+另一明确 conflict 拒。

**所需宿主原语（任选其一即可闭合）**：
1. `fs.write_exclusive(path, content)` —— O_EXCL 语义：文件已存在则抛错/返回失败；或
2. `fs.compare_and_swap(path, expected, new)` —— 读-比-写原子；或
3. `fs.with_lock(path, fn)` / flock 语义句柄 —— 进程崩溃自动释放。

**脚本侧对接方案（原语到位后）**：`_acquireTaskLock` 改为 `write_exclusive("tasks.lock", stamp)` 一次调用（成功=唯一持有者）；`commitBound` 保持当前提交点复核作为纵深；`_releaseTaskLock` 保持 token 全等才清。事件/回执/任务/预约全部写纳入同一持锁区间（commit 成功后暂不释放，logEvent 完成后统一释放；失败路径照旧释放）。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M4/r8/CANDIDATE.json`（candidate_id=M4-r8-worktree）。
- 静态核验：`M4/r8/evidence/fix_verifier.json` 35/35（命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M4/r8/scripts/m4_r8_fix_verifier.py`）。
- 差异：`M4/r8/evidence/r9frozen-to-r8.diff`。
- 离线签名证据：`M4/native/build_r8/offline-store-evidence.json`（私钥已删，remaining_key_files=[]）。
- 原生请求：`M4/native/REQUEST_build_r8.json`（4 场；digest/anchor 见上）。原生截图/日志/回执证据待驱动落 `M4/native-runs/build_r8_*/`，交接时无法附 harness 冷启动结果（驱动尚未执行），如实标记 NOT_RUN。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。
