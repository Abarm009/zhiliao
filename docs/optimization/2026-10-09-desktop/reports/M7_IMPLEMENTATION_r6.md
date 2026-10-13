# M7 实施报告 r6

- 模块 / 目标：M7 同版本总验收与发布准备 —— 修复轮，只处理 M7_REVIEW_r6 缺陷清单。
- candidate_id / base_candidate_id：`M7-r6-worktree` / `M7-r5-worktree`。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`；工作区 dirty 全部保留（本轮不改 `app/bundle/` 任何文件）；冻结主源 `app/bundle/main.splash` = 519600 B，SHA-256=`dd3f4a5e8d87cc45bbd6ac38d1bfa63d31a194b1474826173aef1b8e4023c22f`（与 M6-r7-worktree 同字节）；全量清单见 `runtime/optimization/2026-10-09/M7/r6/phase1-audit.json` 的 `workspace_bundle_sha256` / `staging_sha256` / `seed_manifest`，dirty diff 存 `r6/dirty.diff`。
- 目标宿主 / 二进制来源与哈希 / 依赖：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`；octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，octos-kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`；hub CLI 固定副本 `M0/r7/source-pin/.../hub`；安装探针 `M0/r10/install_probe/.../r10_install_probe`。
- 实际模型路由检查结果（开发会话）：主会话无 Router 切换/核验接口；本轮模型调用 0 次。
- 已检查的前置 PASS 报告：无。M6=`M6_REVIEW_r8.md` FAIL（挂账继续，不代修、不称已接受）；M7 上一轮=`M7_REVIEW_r6.md` FAIL。
- 本轮修改文件与原因：
  1. **B-M7-01（P1，唯一 FAIL 依据）**：审查方改法 = 把 seq 条件改显式 if/else 并重冻结。实际核实：当前工作区字节中根因已闭合——`main.splash:1734` 为显式 `if event_seq == nil { _evt_seq_str = _ev_count.to_string() } else { _evt_seq_str = event_seq.to_string() }`；全文件三元 `? "` 模式 0 处、`\bok\b` 保留字 0 处（r6/phase1-audit.json `parse_fix_evidence`）。且该字节与 M6-r7-worktree 相同，已在 M6 r8 独立 harness（2026-10-12 04:19–04:21，8 场）实测**零 Splash 解析错误、未登录工作台真实渲染**。本轮 0 行业务代码改动，只做 M7 职责内的重新冻结。
  2. **重冻结 0.1.0-e**：`r6/release/octosense-repair-0.1.0-e/`（7 文件）；manifest version 0.1.0-d→0.1.0-e、capabilities 保持 `["storage"]`；`bundle_blake3` 由 hub stamp 不动点写入 = `80d7b5c077979723e3a5cbaa1400701ea683968f6112f5224139608fdba13ef9`；`hub check --allow-unsigned` rc=0 PASSED（`r6/results/hub-check.txt`）。listing/model_config 口径沿 r5（模型 enabled=false、endpoint 清空、截图 placeholder），release_notes 改写为 r6 事实。
  3. **材料同版本重写**（A-M7-02 的事实部分）：SOURCES.md / PRIVACY.md / INTAKE.md 按 0.1.0-e 当前事实重写，移除旧 0.1.0-c 引用；INTEGRITY.txt 11 指纹重算、自指纹外存 `r6/evidence/integrity-selfhash.txt`。app/README.md 未改（A-M7-01 继续挂账，审查方明确不要求顺手修）。
  4. **离线签名 catalog + 隔离 Store seed**（Abram 授权 A）：`r6/keys/` keygen/certify/sign-manifest/verify + install_staged 全 rc=0；私钥 try/finally 删除，`private_key_files_remaining=[]`（phase1-audit.json）。
  5. **harness 复核请求**：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r6.json`（4 场：fresh_candidate / repeat_open / broken_tasks / broken_followups；needs_model=false；expect_bundle_digest=80d7b5c0…），白名单校验全过；由驱动在沙箱外执行，证据将落 `M7/native-runs/build_r6_REQUEST_build_r6/`。
- 桌面 UI/交互变化：无（本轮不改业务脚本）。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化；坏数据场景由 harness broken_* 两场复核。
- 已有别人修改的保留与适配：M2–M6 r6–r8 各轮对 main.splash 的累积修复全部保留（正是本次新基线）；未 reset/stash/覆盖任何改动。
- 启动步骤 / 隔离数据位置：构建方不启动宿主；驱动按 REQUEST_build_r6 在 `M7/native-runs/` 下新目录执行（HOME/app-data/缓存/tmp 全部隔离，Seatbelt 限制）。
- 应用运行模型/provider：冻结候选 enabled=false、storage-only；真实 MiniMax 仅 harness needs_model 代理路径，本轮 0 调用、无 402/欠费。
- 覆盖的既有验收项与证据运行形态：本轮只重跑准入/冻结类子项；业务/模型/完整 T/U 不冒充。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r6 四场|解析 0 错误、首屏渲染|待驱动执行（M6 r8 同字节 8 场零解析仅作交叉证据）|NOT_RUN（待 harness）|M7/native/REQUEST_build_r6.json；M6 r8 H 证据|
|权威状态与回执|离线 catalog/Store 重建|verify/install rc0|PASS|PASS（准入子项）|r6/phase1-audit.json steps|
|失败与重试|broken_tasks/broken_followups seed|原文保护、错误出口|待驱动执行|NOT_RUN|r6/seeds/|
|重启恢复|repeat_open（同场重复开启）|真实重开证据|待驱动执行；跨进程重启仍 BLOCKED（白名单缺口）|NOT_RUN / BLOCKED|REQUEST_build_r6.json|
|受影响先前模块回归|与 0.1.0-d 差异核对|差异可定位|基线 417104B→519600B 为 M2..M6 累积；4 场 harness 复核受影响首屏/恢复|NOT_RUN（待 harness）|r5/r6 staging、M6 r8 报告|

## 尚未完成

- **B-M7-01 闭合待 M7 自有 digest 的 harness 复核**：解析修复在源码与同字节 M6 证据上成立，但 0.1.0-e digest 的四场证据尚未产生（驱动本轮后执行）。不预先宣称 PASS。
- 核心业务链（正常/退回/失败恢复/重启）、真实模型、可信身份、完整 T01–T38/U01–U12：NOT_RUN；输入 key/type、并发主体、精确故障注入、同盘跨进程重启、窄窗/150%：BLOCKED（白名单能力缺口，沿 r6 review 挂账）。
- A-M7-01（app/README.md 旧入口/旧版本引用）：OPEN，P2 建议挂账保留。
- P06/P07/P08：NOT_RUN / UNASSESSED；未发布、未提交、未收录。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M7/r6/CANDIDATE.json`；冻结包：`r6/release/octosense-repair-0.1.0-e/`；材料：`r6/release/release-materials/`。
- 证据：`r6/phase1-audit.json`（含全部离线命令 rc、指纹、密钥删除）、`r6/results/hub-check.txt`、`r6/evidence/integrity-selfhash.txt`、`r6/dirty.diff`。
- harness 请求：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r6.json`（SHA-256 见 phase1-audit `request_sha256`）；待驱动执行后证据在 `M7/native-runs/build_r6_REQUEST_build_r6/`。
- 实际测试命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M7/r6/scripts/prepare_build_r6.py`（rc=0，输出 offline_preparation=PASS）。
- GATES.M7.status=READY_FOR_REVIEW；编码方不给自己 PASS；最终判定等独立 Review；不进入下一模块。
