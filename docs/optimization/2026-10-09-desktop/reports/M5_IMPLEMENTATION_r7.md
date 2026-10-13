# M5 实施报告 r7（修复轮 · Kimi-K3）

- 模块 / 目标：M5 真实附件完工与独立验收 · 按 M5_REVIEW_r7 缺陷清单修复，只修清单项（D-M5-04、D-M5-05）。
- candidate_id / base_candidate_id：`M5-r7-worktree` / `M5-r6-worktree`（清单 `runtime/optimization/2026-10-09/M5/r7/CANDIDATE.json`）。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d` + 既有未提交改动（含 M4-r7、M5-r6 等他人/前序改动，全部保留）+ 本层 r7 修复。修复后 `app/bundle/main.splash` SHA-256=`a91f71f809183f243762a7a2595ef880929dde3dd727ec7a51cbc503aeb206a1`；bundle digest=`e6ddeed41a5fe2b21dbc38156ae3f7fe29d9cb741e4de01d39db18d683b6d478`。逐文件哈希见 `M5/native/build_r7/start-snapshot.json` 与 `fixtures.json` seed 清单。
- 目标宿主：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`（固定发行宿主，未变）。
- 实际模型路由：本模块不调模型；全部场景 needs_model=false，模型请求 0。
- 已检查的前置：M4=FAIL（M4_REVIEW_r8，按 Abram 挂账裁决不修、仅消费契约）；B-M5-01 已由 M5_REVIEW_r7 判定 CLOSED（8 场零 parser、业务区渲染），本轮不修解析；M5_REVIEW_r7 为本轮唯一修复依据。
- 本轮修改文件与原因（仅 `app/bundle/main.splash` 一个业务文件）：
  1. **D-M5-04**（必修）启动恢复未落权威索引、失败被对账计数掩盖：
     - 默认 STATE 显式声明全部 11 个 M5 字段（`main.splash` STATE 字面量内；draft_attach_path / draft_acceptance_opinion / draft_select / attach_proof_pick / attach_items / attach_sandbox_root / attach_sandbox_root_abs / m5_last_round / last_open_attach / m5_last_reconcile）。Review 实测发行宿主对缺失键的读取不保证 nil——错误值 `[Error:NotFound]` 直接进入路径并被拼成索引路径（`[Error:NotFound]/evidence_index.json.tmp` 空文件）；声明默认值后该路径不再出现。nil 兜底初始化保留为第二道防线。
     - 附件根改为相对路径 `m5-test`，由宿主 fs 原语解析进当前获准 app-data jail（与 tasks.json / state.json 同一边界），天然限制在本场。删除 `M5_PROJECT_ROOT_ABS` 与旧 r4/r1 硬编码绝对根（Review 指出的越界根因）；`attach_sandbox_root_abs` 仅在测试/配置显式注入绝对路径时生效，默认为 `""`。未放宽 Seatbelt profile。
     - `m5_reconcile_attach_index()` 新增 **(0) 权威轮次**：从已提交 `t.completions` 历史（commit 先落盘 = 权威）重建 `m5_last_round`——取末条 completion 的 `round`（退化为 `evidence_round` / 条数），与内存轮次不一致即修平并置 dirty；不从 UI 偏好/旧 state.json 认定轮次。
     - **统一 dirty 标记**：涵盖轮次修平 / 退回标记同步 / 索引项重建三类（旧代码 marker-only 修复只增 `t_repaired`，不进 `repaired_round>0 || rebuilt_items>0` 保存条件，reject_marker_only 场实测不落盘）。
     - **writer 失败上抛 + 成功读回**：dirty 时调 `m5_save_attach_index()`，返回 false → `index_save_failed=true`、状态串改为「保持拒绝态，可安全重启重试」，不以计数提示成功；返回 true 后必须 `fs.read` 读回实际目标并逐成员比对（attach_id / evidence_round / lifecycle 全等）才算持久化，读回不一致同样按失败处理。
     - **恢复审计持久化**：启动时无登录会话，`saveEvents` 身份闸拒写是既有设计（不绕过、不造用户会话）；对账审计改经受控系统来源文件 `m5-test/m5_reconcile_audit.json`（actor=`system:boot-reconcile`，含各计数/涉及任务/index_saved/index_save_failed），直接 `fs.write` + 读回核对，`audit_saved` 进 `STATE.m5_last_reconcile`。
     - 新增 `m5_resolve_existing()`：登记绝对路径失效（跨场目录 / 旧钉扎 / 含 `[Error` 错误值标记）时回退到本场相对根 + `stored_rel` / `attachments/<basename>`；不可读保持 MISSING。
     - 索引中同 id 项**属于其他任务**时隔离保留：不修平、不重建、不为本任务所用，计入 foreign_items（D-M5-03 归属守卫在对账路径的补齐）。
     - `m5_load_attach_index()` 只接受数组（标量/对象/错误值不覆盖内存索引）。
  2. **D-M5-05**（必修）丢 canonical 时的弱指纹重建基准：
     - 删除 reconcile 中 `canon_text == nil` 分支的弱指纹自动重建（`fs.write(canonical)` + `canon_text = cur_text` 内存赋值）；canonical 缺失 = 失去可信内容基准，直接保持 `CORRUPTED`（未可信，source=`rebuild_from_task_store:no_canonical`），补证出口 = 人工重传 / 显式复验。Review 的 0x03→0x04 同指纹反例不再可能被追认为原件。
     - 保存路径（`m5_attach_from_path`）canonical 写入后必须读回核对（`canon_back != src_text` 即拒存），不把「写入未抛错」当落盘成功。
- 桌面 UI/交互变化：无新增控件；对账结果落 `STATE.status` / `STATE.m5_last_reconcile` / 审计文件，验收/完工表单不变。
- 接口 / 数据迁移 / 旧数据恢复：无格式迁移；旧 evidence_index.json 与旧任务字节在启动对账中修平/保留（孤儿、外来项不删除）。
- 已有别人修改的保留与适配：M4-r7、M6、M7 及 M5-r6 改动全部保留；未 reset/stash/删除任何他人改动。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。原生验证请求 `M5/native/REQUEST_build_r7.json`（5 场），由驱动在沙箱外经 `driver/harness/native_harness.py` 执行，证据输出固定为 `M5/native-runs/build_r7_REQUEST_build_r7/`（fixture 绝对根已按此钉扎；相对根回退使钉扎偏差可自愈）。
- 应用运行模型/provider：不调用；无秘密入代码/日志/报告。
- 覆盖的既有验收项与证据运行形态：G0-D/T19/T21/T22/T28/U06/U07 的「重启恢复/索引分裂/丢 canonical」子项由本协议覆盖，原生实证待驱动执行；其余 T/U 项本轮未扩。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|D-M5-04 静态：STATE 声明/相对根/权威轮次/dirty/读回/审计/隔离守卫|全文件断言 24 项|全部命中|30/30（含 B-M5-01 回归守卫与 D-M5-05 项）|PASS（源码级）|M5/r7/results/r7-fix-checks.json|
|D-M5-04 仿真：submit 分裂|Python 移植对账跑夹具副本|权威轮次 1 重建 + 索引 2 项修 round1 + 落盘读回 + 审计|符合|PASS（逻辑移植，非原生）|同上 sim 段|
|D-M5-04 仿真：reject marker-only|同上|round0+退回标记同步并落盘|符合|PASS（移植）|同上|
|D-M5-04 仿真：索引缺项+孤儿|同上|字节校验 READY 重建 + 孤儿保留|符合|PASS（移植）|同上|
|D-M5-05 仿真：丢 canonical 坏件|同尺寸首尾不变、中段 0x01→0x02|保持 CORRUPTED，不生成 canonical|符合（canonical_files_after 为空）|PASS（移植）|同上|
|真实桌面冷启动（零解析错误/登录任务界面渲染）|harness cold_fresh 场|零 parser 错误、真实 UI|NOT_RUN（驱动执行后见 native-runs）|NOT_RUN|M5/native/REQUEST_build_r7.json|
|原生对账恢复（4 场负例）|harness 各场启动即对账|运行副本 evidence_index.json 修平 + m5_reconcile_audit.json + state.json m5_last_reconcile index_saved=true|NOT_RUN|NOT_RUN|同上|
|权威状态与回执 / 可信独立验收 / 完整正常链与退回链 / 同盘重启|可信会话业务命令|—|NOT_RUN（可信文本输入/受控注入/同盘重启通道缺口沿用 r7 Review BLOCKED 子项，需驱动补齐，不需 Abram 新授权）|NOT_RUN|—|
|受影响先前模块回归|受影响函数切片比对|仅 M5 恢复依赖变化|M4 helper 无改动；10 个受影响函数哈希已存|PASS（源码级）|M5/native/build_r7/affected-functions.json|

## 尚未完成
- 原生冷启动与 4 场对账/丢 canonical 负例：请求已就绪并钉扎路径，**NOT_RUN**（驱动在本阶段结束后沙箱外执行；证据将落 `M5/native-runs/build_r7_REQUEST_build_r7/`）。
- 可信文本输入、保存后变更、精确 writer/commit 中断注入、同盘重启、迟到模型交错：沿用 M5_REVIEW_r7 的 BLOCKED 子项（当前宿主白名单/schema 不表达，需驱动/宿主补通道）；业务命令链 NOT_RUN，本轮未扩范围。
- D-M5-05 的原生坏件放行实证（真实上传→保存后注入→双入口拒绝）依赖上述通道，NOT_RUN。

## 交接
- 候选清单：`runtime/optimization/2026-10-09/M5/r7/CANDIDATE.json`（含源 SHA 与 bundle digest）。
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r7.json`；准备脚本 `prepare_build_r7.py`；离线签名证据 `build_r7/offline-store-evidence.json`（私钥 2 把已删，删除记录逐项 exists_after=false，keys 目录为空）；seed 清单 `build_r7/fixtures.json`。
- 源码切片：`build_r7/source-traces/`（m5_reconcile_attach_index / m5_resolve_existing / m5_load_attach_index / m5_save_attach_index / m5_sandbox_root_abs / m5_init_forms / m5_attach_from_path / submitCompletion / rejectCompletion / load）。
- 静态+仿真证据：`M5/r7/results/r7-fix-checks.json`（30/30，含 4 场对账仿真明细）。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。不进入下一模块。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
