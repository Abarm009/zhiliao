# M7 实施报告 r10

- 模块 / 目标：M7 同版本总验收与发布准备 · 修复轮——只修 M7_REVIEW_r12 唯一未闭合必修 **R-M7-02**（恢复/加载时仍接受不完整 JSON：合法前缀+尾随垃圾、末尾仍 `]` 的 tasks.json 被宽容 parse 误接受）。B-M7-01 解析回归已在 r11/r12 关闭，本轮不得回归。A-M7-01/A-M7-02 为 P2 建议挂账，不在本轮范围。
- candidate_id / base_candidate_id：**M7-r10-worktree / M7-r9-worktree**，staging 版本 **0.1.0-i**，bundle_blake3 = `958f2875b7a5151bb8bcf086f1b34bbafcadd6a7355cac4ba75f431fb3d23b03`。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD=`8d730569546cb57310944bb299695134df773b9d`（工作区有大量未提交差异，不只凭 HEAD 定位）；dirty.diff 与全量 SHA-256 清单存 `runtime/optimization/2026-10-09/M7/r10/phase1-audit.json` + `r10/dirty.diff`。冻结主源 = 工作区 `app/bundle/main.splash` **809714 B**，SHA-256=`ee8f541468304b710d87fbf0cda8416939c57c7f762b32f624fde8637f5b6a44`（staging 内逐字节相同）。
- 目标宿主 / 二进制来源与哈希：项目内 M0/r3 提取 OctoSense.app（octosense SHA-256=`3e1279635cc7…`，octos-kernel=`a3e46a45…`，沿 r12 记录）；本轮构建方不启动宿主，原生复核走 harness 请求 `runtime/optimization/2026-10-09/M7/native/REQUEST_build_r10.json`（SHA-256 见 phase1-audit.json），待驱动沙箱外执行。
- 实际模型路由检查结果（开发会话）：未切换/未声称；模型配置保持 enabled=false、storage-only；本模块 needs_model=false、真实 MiniMax 调用 0 次。
- 已检查的前置 PASS 报告：无新前置 PASS——M6 仍 FAIL（M6_REVIEW_r12/r14 挂账），按挂账裁决继续局部构建；本轮 FAIL 风险只来自 M7 自身 R-M7-02。

## 本轮修改文件与原因

| 文件 | 修改 | 原因（按 r12 审查改法） |
|---|---|---|
| `app/bundle/main.splash`（`fn m7_tasks_strict_parse`，唯一业务代码改动） | 完整消费证明改由共用底层 `hf_json_decode_complete` 承担：先全文 token/shape 完整闭合校验（非法 token、尾随内容、未闭合一律整份拒绝），再 parse→to_json 回读结构计数对账（防重复键/结构丢失），随后才核顶层数组与逐成员必需字段/类型/状态。删除"首 `[` 尾 `]` 即闭合"的证明与直接 `raw_text.parse_json()` 宽容消费；保留首字符 `[` 快速门禁（仅用于报准确原因） | r12 改法原文："只补共同严格 parser 的完整语法/全部输入消费，沿用固定宿主实际支持且经过正反例实证的接口……明确拒绝数组前缀后的任何非空白输入。load/keep/overwrite 保持同一判据。不要只匹配首尾、删 validator、清 pending 或以序列化长度相等冒充完整校验。保留 success 协议、严格数值门禁、原文/旧 recover 保全策略和现有 UI 布局。" |

调用点（load:strict_parse、保留复验 keep、受控覆盖写后读回）未改——三处本就共用 `m7_tasks_strict_parse`，判据升级后自动获得完整消费证明；success 返回协议、`m7_is_strict_number_value` 严格数值门禁、`m7_tasks_mark_corrupt` 原文/旧 recover 保全、登录页 login_hint 恢复原因可见（15731–15735，A-M4-R13-01 已接）、恢复控件与身份核验全部不变。**无新页面/新字段/新入口/新文案布局。**

`hf_json_decode_complete` 来源：M2 硬修轮写入的共用底层（main.splash:612），M2_REVIEW_r18 已对其 JSON 读取改动判 PASS（P1=0），属"固定宿主实际支持且经过正反例实证的接口"。注意：r9 冻结的 0.1.0-h 主源（702301 B）尚不含 hf 族；本候选冻结的是当前累计工作树（809714 B），包含 M2/M4/M5/M6 后续硬修轮的 hf_* 家族与调用点改动——**他人改动全部保留、未撤销未覆盖**；r9→r10 主源 diff 共 2840 行，其中本模块改动仅 `m7_tasks_strict_parse` 一处（±约 20 行），其余为他人模块累计硬修。

## 桌面 UI/交互变化

无。界面、布局、文案、样式一律未动（Abram 2026-10-13 硬规则）。任务损坏原因在登录页 login_hint 的既有展示路径（refreshDesktop:login_hint）未改；R-M7-02 修复后两个 closed_junk 坏盘将进入 pending=true 并沿用该既有可见出口。

## 接口 / 数据迁移 / 旧数据恢复方式

无协议/迁移变化。恢复两分支判据收紧后与 load 完全一致：非法原文 keep 不解锁（保持 pending、备份已核、身份核验在先）；overwrite 仍要求有效可信身份+备份核实+受控写+严格读回。旧 tasks.json.recover 非空时绝不覆盖（另存 corrupt.latest 并读回核实）。

## 已有别人修改的保留与适配

保留 M2/M3/M4/M5/M6 在累计工作树上的全部硬修（hf_* 家族、m4 状态文案、登录 KDF 等），未 reset/stash/删除任何他人改动；`git status` 里的他人未跟踪文件（.archive/、data-test/、host.log、.bak 等）一律未动且不进入 staging。前序模块未闭合缺陷（M2/M3/M4/M5/M6 挂账清单）不在本模块范围。

## 启动步骤 / 隔离数据位置

构建方不启动宿主。harness 请求 15 场全新隔离官方 Store seed：`runtime/optimization/2026-10-09/M7/r10/seeds/<场景>/`（逐字节镜像 review_r2_0002 夹具，含 closed_junk_record / closed_junk_empty 两反例；fixture 镜像一致性已核 0 不符），hub mirror=`r10/store/local-mirror`（离线签名 catalog，私钥已删并记录），expect_bundle_digest=`958f2875…`，全部 needs_model=false。证据将由驱动写入 `M7/native-runs/build_r10_*/`。

## 应用运行模型/provider

model_config.json：enabled=false、endpoint/api_style 为空（hub check 要求），密钥引用仅指向 runtime/secrets/minimax_provider.env 供 harness needs_model 路径注入；本轮不消费。

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|冻结一致性|工作树快照+staging 7 文件+材料 5 文件重算 SHA|字节一致、版本 0.1.0-i、digest 不动点|staging/材料/运输包非 manifest 字节全同，hub stamp 三次不动点|PASS（静态）|r10/phase1-audit.json、INTEGRITY.txt|
|本地准入|hub check --allow-unsigned、离线 keygen/certify/sign-manifest/verify、install_staged 探针|全部 rc0、私钥删除|rc0；anchor/working 私钥 finally 删除、目录空|PASS（离线子项，不代官方 scan）|r10/results/hub-check.txt、phase1-audit.json|
|R-M7-02 完整消费门禁静态自检|等价 Python 正则模拟 hf 判定跑 15 夹具|两 closed_junk 拒绝；4 合法场不误拒；7 坏盘+2 特殊场拒绝；旧 recover/目录备份保源|15/15 与预期一致（simulate_hf_gate.py，模式串与 main.splash:577 逐字节核对一致）|PASS（静态预测，不替代原生证据）|r10/scripts/simulate_hf_gate.py 输出（见下文）|
|真实桌面操作（15 场冷启）|REQUEST_build_r10 待驱动执行|每场解析诊断 0；合法场 pending=false 无 recover；9 坏盘 pending=true 原因准确、原文/备份逐字节保全；两 closed_junk 必须 pending=true|驱动未执行|NOT_RUN|M7/native/REQUEST_build_r10.json|
|权威状态与回执|可信登录后业务链|r12 已记不可表达步骤|未执行|NOT_RUN|—|
|失败与重试（认证后恢复两分支）|r12 验证方式要求可信登录后 keep/overwrite|非法 keep 不解锁、合法 keep 加载、overwrite 备份+受控写+严格读回|固定宿主 type/key 未实现、本轮许可动作不可表达|BLOCKED（具体步骤）|—|
|重启恢复（同 Store 原生业务进程重开）|r12 验证方式|同候选重开状态保留|schema 无此接口|BLOCKED（具体步骤）|—|
|受影响先前模块回归|解析清零门槛（B-M7-01 不得回归）、合法任务/提醒数值门禁/旧 recover 保全|0 解析错误、正例不误拒|静态证据+模拟通过；原生待 harness|NOT_RUN（原生）|phase1-audit r10_fix_evidence|

静态自检模拟输出（`python3 -B runtime/optimization/2026-10-09/M7/r10/scripts/simulate_hf_gate.py`，仅为构建方静态预测，host 行为以 harness 为准）：fresh_login 无文件 pending=false；empty_whitespace/legal_quoted_two/empty_narrow hf 通过→成员门禁通过 pending=false；object_dual_pending 首字符拒；truncated_dual_pending 未闭合拒；member_missing 成员门禁拒；trailing_outside/closed_junk_record/closed_junk_empty 非法 token/尾随拒；boolean_version/string_created/object_updated 严格数值门禁拒；preserve_old_recover/backup_slots_are_dirs 拒绝且保源。**15/15 与 review_r2_0002 期望一致。**（排错记录：模拟初版把容器重复组误写为 `(?:,[@#TFN])*` 漏了 `@:`，导致 legal_quoted_two 被误报拒绝；按 main.splash:577 真实模式串修正后通过。真实代码从未含该笔误。）

## 尚未完成

- **NOT_RUN（原生）**：15 场 harness 复核（含两 closed_junk 反例、解析清零回归、登录页渲染）——请求已递交，待驱动沙箱外执行；本轮无任何原生 PASS 自称。
- **BLOCKED（具体步骤，沿 r12）**：可信非空键入/认证后恢复两分支/同 Store 原生业务进程重开/精确提交点故障/150%——固定宿主接口与许可动作不可表达。
- **NOT_RUN（挂账）**：提醒字段矩阵（r12 审查夹具顶层包装错误，审查方下轮自修，不判产品 FAIL）；真实模型链（G0-E/P03 模型子项）；完整 2–3 分钟演示与真实业务截图（A-M7-02 P2）；app/README 历史话术（A-M7-01 P2）。
- **P06/P07/P08 = NOT_RUN**：未发布、未收录、未提交赛事；本轮无 tag/Release/Issue/上架/联网动作。
- 前序模块挂账缺陷（M2 D-M2-01/02/03/07、M3 D-M3-02、M5 D-M5-04、M6 D-M6-03 系列、BLOCKED-HOST D-M2-05/D-M4-03）不在本模块范围。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M7/r10/phase1-audit.json`（HEAD、dirty 清单、工作树/staging/种子 SHA-256、运输一致性、白名单校验、私钥删除证据）。
- 冻结包：`runtime/optimization/2026-10-09/M7/r10/release/octosense-repair-0.1.0-i/`（7 文件）+ `release-materials/`（5 文件，INTEGRITY 自指纹外存 r10/evidence/integrity-selfhash.txt）。
- harness 复核请求：`runtime/optimization/2026-10-09/M7/native/REQUEST_build_r10.json`（15 场，逐字节镜像 review_r2_0002 夹具，needs_model=false，白名单校验全空）。
- 原生截图/日志：待驱动执行后位于 `M7/native-runs/`；本轮构建方无原生截图（不伪造）。
- 审查建议入口：先核 `m7_tasks_strict_parse`（main.splash，grep `fn m7_tasks_strict_parse`）与 r10_fix_evidence，再审新候选，勿审旧包。
- GATES.json：M7 status=READY_FOR_REVIEW、candidate_id=M7-r10-worktree；编码方不给自己 PASS，最终判定等独立 Review。
