# M5 实施报告 r12

- 模块 / 目标：M5 真实附件完工与独立验收 —— 本轮为修复轮，唯一修复依据 = **M5_REVIEW_r14** 缺陷清单，只含一项 **B-M5-TEST-R14-01**（BLOCKED / 环境前置，非产品缺陷）：驱动在沙箱外执行独立请求时，首场 pre_pgrep 命中一个既有 OctoSense 宿主进程（demo-video 录制残留），触发 ABORT_PRE_PGREP_MATCH，八场均未启动，B-M5-01 与 D-M5-04 B/C 无法裁决。
- candidate_id / base_candidate_id：**M5-r11-worktree / M5-r10-worktree**（与 r14 审查的候选完全相同；审查方明确要求「同候选、同请求」重跑，本轮不重新冻结）。
- HEAD / 未提交差异 / 源文件哈希清单：冻结源 SHA-256 `05c9ea2484eb3c2ee1dc5a97dde37e1f489501a42385dfd81b5803914dfe6365`（771176 B），bundle digest `5bde47daba3ff19a98a9b0e079bbd9cd06eb16ae0d4b133dc45206395ab63544`；候选清单 `runtime/optimization/2026-10-09/M5/r11/CANDIDATE.json` 不变。**本轮 0 行业务代码改动**（清单项是环境前置，不是代码缺陷；r14 明示「先解阻重跑，不凭本批次盲改代码」）。
- 目标宿主 / 二进制来源与哈希 / 依赖：host-rc6 `host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`（沿用 r14 核实值）。
- 实际模型路由检查结果（开发会话）：本模块 needs_model=false，模型 0 次；无 provider 配置变更。
- 已检查的前置 PASS 报告：无（M4=BLOCKED 挂账沿用，按裁决继续局部交接，不冒称前置满足）。
- 本轮修改文件与原因：
  1. `runtime/optimization/2026-10-09/M5/native/REQUEST_build_r12.json`（新增）：与 REQUEST_build_r11.json 场景/种子/锚点/期望 digest 完全一致，仅 note 更新为 r14 解阻语义，输出钉扎 `runtime/optimization/2026-10-09/M5/native-runs/build_r12_REQUEST_build_r12/`。
  2. 本报告 + `runtime/optimization/2026-10-09/M5/CONTEXT_M5.md`（追加 r12 要点）+ `docs/optimization/2026-10-09-desktop/GATES.json`（仅 M5 构建字段）。
- 桌面 UI/交互变化：无（0 代码改动；界面/布局/文案/样式一律未动）。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化；种子与签名镜像复用 `M5/native/build_r11/`（r14 审查已逐项核验 40 个 seed 文件与冻结输入逐字全等，本轮复查目录完好）。
- 已有别人修改的保留与适配：全部保留。**未杀、未停任何他人进程**：2026-10-13 23:17 实测仍存在一个**活跃中**的 demo-video-20261013 录制运行（宿主 PID 47460 + minimax_proxy PID 47449，23:16:36 启动，属于另一工作流，正在写 frames），不是可安全清理的残留；按 r14「不强杀来源未核实进程」与「不覆盖他人改动」，构建方不动它。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。驱动在沙箱外、**pre_pgrep=NONE 后**执行 REQUEST_build_r12.json；证据落 `runtime/optimization/2026-10-09/M5/native-runs/build_r12_REQUEST_build_r12/`。
- 应用运行模型/provider：无（needs_model=false）。
- 覆盖的既有验收项与证据运行形态：G0-D、T18–T22、T28、T31、T35、U03、U06–U08、U11 —— 本轮全部 **NOT_RUN**（依赖驱动重跑后的原生证据，不由本报告预断）。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|harness 5 场（同 r11）|驱动执行|构建方未执行|NOT_RUN|REQUEST_build_r12.json|
|权威状态与回执|submit 分裂 / reject marker-only 场|save_verify rb_ok=true、audit index_saved=true|待驱动|NOT_RUN|同上|
|失败与重试|索引缺项+孤儿 / 丢 canonical 坏件场|坏件拒信、孤儿保留|待驱动|NOT_RUN|同上|
|重启恢复|evidence_index.json v3 持久化|待驱动|NOT_RUN|同上|
|受影响先前模块回归|cold_fresh 零解析+登录 UI 渲染（B-M5-01 回归闸）|0 解析错误|待驱动|NOT_RUN|同上|

## 尚未完成
- **B-M5-TEST-R14-01（唯一清单项）**：解阻动作 = 既有 demo-video 运行的负责方完成并关闭其宿主 → 驱动核实库存 NONE → 用 REQUEST_build_r12.json 重跑。构建方侧可做的（同候选请求、种子核验、交接）已全部完成；**宿主进程清退与重跑执行不在构建方权限内**（构建方不得自启/强杀宿主，harness 由驱动在沙箱外执行）。本轮交接时（23:17）该录制运行仍活跃，属环境时序问题，不需 Abram 新授权。
- B-M5-01、D-M5-04 B/C：保持 r14「历史未关闭 / 本轮运行 BLOCKED」原状，待重跑证据裁决；不以静态检查或源码存在代原生 PASS。
- 可信输入 / 保存后变更 / 同盘重开 / 精确中断通道：沿用既有 BLOCKED（驱动补通道，不需 Abram 新授权）。

## 交接
- 候选清单：`runtime/optimization/2026-10-09/M5/r11/CANDIDATE.json`（不变）；冻结源/签名镜像：`M5/native/build_r11/`（私钥早已删除，见 build_r11/offline-store-evidence.json）。
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r12.json`（5 场，needs_model=false，判定标准在 note）。
- 静态证据：`runtime/optimization/2026-10-09/M5/r11/results/r11-fix-checks.json`（85/85，本轮代码未变，继续有效）。
- 实际测试命令：无（构建方 0 执行原生；仅 ps/文件核验，未触宿主）。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。
