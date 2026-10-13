# M5 实施报告 r1 · 真实附件完工与独立验收

- 模块 / 目标：M5 / 让真实证据支持完工，并由独立可信主体完成验收或退回重做
- candidate_id / base_candidate_id：M5-r1-worktree / M4-r2-worktree
- HEAD / 未提交差异 / 源文件哈希清单：
  - HEAD = 8d730569546cb57310944bb299695134df773b9d
  - 本轮候选相对 WORKTREE-UNCOMMITTED（M4 r2 review 之后），不动 git tree
  - `app/bundle/main.splash` after_sha256：`f2b50b67337303965565c90472a610d250fb01bd968a2568709bda9cf823613e`（5396 行）
  - base（M4 r2）after_sha256：`c656536119ff0983394bc10f65578095508ca3643e9a538ba8e82b415beab545`（4618 行）
- 目标宿主 / 二进制来源与哈希 / 依赖：原生 launcher 沿用 M4 r2（sandbox-exec rc71 + pgrep rc3 UNKNOWN；不启动）
- 实际模型路由检查结果（开发会话）：Router 未切；M5 不要求联网，纯静态 + sandbox-isolated 测试
- 已检查的前置 PASS 报告：**M4 未通过独立 Review（M4_REVIEW_r2 FAIL）**；本模块按 Abram 2026-10-10 13:54「完成比完美重要」授权挂账推进，不假装 M4 PASS
- 本轮修改文件与原因：
  - `app/bundle/main.splash` 追加 778 行（含 m5_init_forms + 13 个 M5 函数 + 4 个 runAction 分支 + 3 个 TextInput + 4 个行为按钮 + load boot 钩子）
  - 删除 demo 占位 push：`addEvidence` 不再 push `demo-xxx.bin / bytes=0 / sha="" / ready=false`；改为真实 lifecycle
  - `quarantineEvidence` 改为移动 attachments/ → quarantine/ + lifecycle=QUARANTINED
  - `submitCompletion / acceptCompletion / rejectCompletion` 加入 M5 校验 + round binding + evidence 重置
- 桌面 UI/交互变化：
  - 新增 4 个行为按钮：上传真实附件（按 inbox 路径）/ 打开重读附件 / 重试验证 / 隔离证据
  - 新增 3 个 TextInput：m5_attach_path_input / m5_acceptance_opinion_input / m5_manager_proxy_reason_input
  - 附件 tab 渲染切到 M5 READY/异常/当前轮次视图；hint 提示 inbox 路径边界
  - inbox hint 实时渲染 m5_inbox_hint_text()
- 接口 / 数据迁移 / 旧数据恢复方式：
  - `STATE.attach_items[]` 与 `evidence_index.json` 跨重启恢复
  - 旧 demo 占位 t.evidence 条目（bytes=0 / sha=""）由 `m5_drop_legacy_demo_evidence` 在 boot 阶段清退
  - 旧 `STATE.draft_*` 字段在 m5_init_forms() 兜底；不破坏 M4 既有契约
- 已有别人修改的保留与适配：
  - M4 r2 的 STATE.draft_appt / draft_assign / draft_reschedule / draft_progress / draft_completion / draft_reject / draft_reassign / draft_bind_asset 全部保留
  - submitCompletion / acceptCompletion / rejectCompletion / addEvidence / quarantineEvidence 函数签名与控制流不变；仅在内部叠加 M5 校验
  - runAction dispatch 表追加 4 个 cmd（m5_openAttach / m5_retryVerify / m5_syncAttachPath / m5_syncAcceptOpinion）；不破坏既有 21 个 cmd
  - 不删 / 不动 M3 source_audit 51 项；不撤 M2 cmdExecute 边界
- 启动步骤 / 隔离数据位置：
  - sandbox root：`runtime/optimization/2026-10-09/M5/r1/sandbox/`
  - 子目录：`inbox/`（用户源文件）/ `attachments/`（存盘字节）/ `quarantine/`（隔离）/ `lost+found/`（missing 模拟）
  - 跨重启：`evidence_index.json` 在 sandbox root 下
  - 不写 `~/.octosense`；不写宿主 HOME
- 应用运行模型/provider（适用时；无秘密）：OFFLINE；M5 不调用任何模型；no_op adapter 沿用
- 覆盖的既有验收项与证据运行形态：
  - G0-D：本地 fs 路径证据 + 字节一致 fingerprint（host picker / native import = BLOCKED，标记 NOT_RUN）
  - T18 / T19 / T20 / T21 / T22 / T28 / T31 / T35 / U03 / U06 / U07 / U08 / U11：源码契约 + sandbox 字节真实比对；native desktop runtime = NOT_RUN

## 测试表

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|启动原生 launcher|窗口截图 + 真实交互|rc71 BLOCKED 沿用|NOT_RUN|docs/optimization/.../M0..M4 既有报告|
|权威状态与回执|真实 ops log|events / actions 落四文件 + receipt|sandbox 内 evidence_index.json 一致 + reopen 字节 PASS|源码契约 PASS|native runtime BLOCKED；契约 / OS 路径 PASS|
|失败与重试|故障注入：corrupt / missing / quarantine / DENIED|submitCompletion / acceptCompletion 拒绝|全部拒|native BLOCKED；契约 / OS 路径 PASS|evidence/{reopen_restart,failure_injection}.json|
|重启恢复|写 evidence_index.json + bytes；重读|attach 仍 READY，bytes 一致|PASS|native BLOCKED；契约 / OS 路径 PASS|evidence/reopen_restart.json|
|受影响先前模块回归|M4 既有 5 项契约|保留|保留；M4 r2 提交后未触及|native BLOCKED；契约 / OS 路径 PASS|M4_REVIEW_r2 + 既有 scripts|

## 测试细节（scripts/ 8 项全过 · 122/122 PASS）

|脚本|范围|cases|结论|
|---|---|---|---|
|m5_lifecycle.py|8 个 lifecycle 常量 + 13 个 M5 函数 + READY 由字节一致推导|35/35|PASS|
|m5_real_attach.py|真实字节入库 + fingerprint + reopen|8/8|PASS|
|m5_round_binding.py|round 增量 / 重置 / 行为模拟|17/17|PASS|
|m5_self_accept_block.py|自验阻止 + 经理代验理由|14/14|PASS|
|m5_reopen_restart.py|重启 reopen + 4 类故障注入|8/8|PASS|
|m5_input_no_hardcoded.py|无 demo / 默认串 / 接入 STATE 输入|13/13|PASS|
|m5_evidence_authority.py|真实字节 + UI 真实可达 + boot load|24/24|PASS|
|m5_whitebox_attachments.py|真实中文文本 + PNG-like + 跨重启|3/3|PASS|

review_driver 汇总 → `results/run-summary.json`：scripts 8/8 OK；cases 122/122 PASS

## 尚未完成（环境 BLOCKED 沿用）

- **native desktop runtime = BLOCKED**：sandbox-exec preflight rc71（沿用 M0/M1/M2/M3/M4）；pgrep rc3 UNKNOWN；本轮不启动 launcher，不连 `--help`。
- **host picker / native import API = BLOCKED**：原生宿主 picker 不可达，真实附件通过 TextInput 输入 sandbox 内 inbox 路径；等同于"用户把文件放进 sandbox 后告诉 UI"。仅 M5 内部校验该路径必须在 inbox 内；外部路径一律 DENIED。原生 picker 等同 BELAF 还需要宿主补齐 → 标记 BLOCKED（G0-D 沿用）。
- **真实模型 provider**：G0-E 仍延期缺口，本轮不申请。
- **可信业务身份来源**：M2 挂账缺口，本轮不申请。
- **AppHub publish / 公网上架 / listing**：本轮一律不发起；离线签名沿用 M0/M1/M2/M3/M4 既有路径（sandbox-only）。
- **既有 M4 未闭合缺陷**：D-M4-02/03/04/05 不在本模块修复。
- **既有 M3 D-M3-01/03/04/05/06 / M2 D-M2-01..07**：仅消费不修。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M5/r1/CANDIDATE.json`（schema=3 沿用 M3 r2）
- 实际运行证据：`runtime/optimization/2026-10-09/M5/r1/evidence/`（8 个 JSON）+ `results/run-summary.json`
- 测试命令：`python3 /Users/abeam/一些尝试/知了OctoSense/runtime/optimization/2026-10-09/M5/r1/scripts/m5_review_driver.py`
- 真实可用：当前 main.splash `f2b50b67…`（5396 行）已叠加 M5，不破坏 M4 r2 既有差异
- 编码方最多标本模块 status = `READY_FOR_REVIEW`；最终 PASS 等待独立审查
