# M3 实施报告 r10（修复轮）

- 模块：M3「真实输入与AI报修」；构建方 Kimi-K3；日期 2026-10-13（Asia/Shanghai）。
- 依据审查：`docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r13.md`（FAIL，必修仅 D-M3-02）。严格按审查方交接方案执行，只修清单项，未发散、未新增功能/入口/字段。
- 候选：**M3-r10-worktree**（base M3-r9-worktree）；HEAD 8d730569546cb57310944bb299695134df773b9d（dirty，含他人共享改动，未覆盖/未撤销）。
- 运行对象源码：app/bundle/main.splash **765252 B / SHA256 ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e**——与 r13 独立审查已原生验证 D02 恢复正例 PASS 的「共享对象」逐字相同。
- 清单：`runtime/optimization/2026-10-09/M3/r10/CANDIDATE.json`；冻结源副本 `M3/r10/source.main.splash`。

## 修复项（按原缺陷编号回写）

### D-M3-02（P1，必修）正式交接包仍误判合法持久输入

r13 审查方「具体改法」原文：**当前共享读取接线已有正例证据，不要重写已修逻辑。构建方把已验证共用读取及 M3 恢复接线冻结为新的正式 M3 候选**……保持已通过保源/冻结分支和界面。旧 r9 不能只改候选标签冒充新字节。

按此执行，**本轮业务代码改动数 = 0**：

1. 根因（r13 已定位）：正式包 M3-r9 的旧完整性门禁（trim/首尾字符/对象探针组合）把合法 JSON 误判为损坏，随后放行默认 state 保存覆写原文。共享工作树在 M2 硬修复轮已把 `loadViewState` 接到严格底层 `hf_parse_json(text, "view_state")`（当前 main:1951–1996），r13 用全新隔离 Store 在固定宿主 rc.6 上独立实证：中文（1236 B 原文/引号/换行/emoji/反斜杠）、ASCII 字面 `\ud800`/`\n`、2826 码点长输入三组正例四字段（pending_input / confirm_intent_id / confirm_intent 嵌套 payload / action_keys_by_task）恢复全等、无坏源备份；重复键整对象拒绝+旧 bak 不动、备份槽满冻结+人工出口、伪保存主体无业务写三个负例子项 PASS。
2. 本轮动作：把该共享源码正式冻结为 M3 候选 M3-r10-worktree——冻结四个 bundle 对象 SHA、重新离线签名打包、重建七场 D02 场景 seed（业务 seed 原字节沿用 r13 审查种子，仅换包）、写新 harness 请求。不改 `loadViewState`、不改保源/冻结分支、不改界面/布局/文案。
3. 与 r9 的差异：全部来自 M2 硬修复共用底层（H1 严格 JSON 读取接线及关联 helper），非本模块新写代码；差异详情见 r13 审查材料 `M3/native/review_r1_1659/formal-r9-to-shared.diff`。

### 运输 digest 说明（诚实记录）

本候选 digest `ddd0eb06…` 与 r13 审查自建 mirror-shared（`1bd2bfc2…`）不同：该 mirror 打包时误含 `main.splash.bak-gptfix-1540` 与 `manifest.json.bak-gptfix-1540` 两个 .bak 文件；本候选沿用 curated 打包清单（main/manifest/model_config/identities/listing/assets/screenshots），不含 .bak，业务 main.splash 字节与 r13 验证对象逐字相同（ae25feb4）。

## 验证证据（本沙箱内实际执行）

| 项 | 结果 | 证据 |
|---|---|---|
| vendored 解析（octoscript-core m2_r7_bundle_parse） | PASS（1 passed，0 诊断） | 本轮实际运行输出；`M3/r10/evidence/r10_static_check.json` |
| 冻结字节与 r13 验证对象一致 | PASS（逐字相等） | `shasum` 重算 765252 B / ae25feb4；`M3/r10/source.main.splash` |
| 离线签名 store（授权 A） | PREPARED；hub verify rc0；install_probe（install_staged 本地安装路径）rc0；私钥已删（evidence 内 `exists_after=false`，keys 目录空） | `M3/native/build_r10/offline-store-evidence.json`；anchor=1a32d39cfd3238db761564aa434ff85f60e96139e904f9c4b6873dbfb2e49bbe；digest=ddd0eb06ef6afda8cc36174c64e0c5519e84ac695854b94f6f502cf62d45ed6f |
| r13 独立原生恢复证据（对本源码） | 正例三场 PASS / 负例三场 PASS（审查方证据，本轮不重跑冒充） | `M3/native-runs/review_r1_1659_REQUEST_review_r1_1659/`；M3_REVIEW_r13 必需检查表 |

## 原生验证（驱动沙箱外执行）

- 请求：`M3/native/REQUEST_build_r10.json`（7 场，全部 needs_model=false，仅 launch-hub/capture，无 ui_actions/osascript/自动化）：
  1. `shared_clean_cold` 冷启动回归（零解析/运行错误、登录页渲染不回归）；
  2. `shared_unicode_restore` D02 中文正例逐字段恢复；
  3. `shared_ascii_literal_restore` D02 ASCII 字面转义正例；
  4. `shared_long_input_restore` D02 长输入回归（已知 A-M3-R13-01：r13 本场出现一次运行预算 [E]，恢复数据仍全等；P2 建议挂账，本轮不修代码，如实记录 actual）；
  5. `shared_duplicate_old_backup` 重复键拒收+保源负例；
  6. `shared_backup_slots_full` 备份槽满冻结+人工出口负例；
  7. `shared_forged_saved_subject` 伪保存主体无业务写负例。
- 结果：**PENDING_DRIVER**（待写入 `M3/native-runs/build_r10_REQUEST_build_r10/`）。冷启动零解析错误结论以驱动回写证据为准，本轮不预先声称。

## 未执行 / 阻塞 / 挂账（如实标记）

- **A-M3-R13-01（P2 建议，挂账不修）**：长输入恢复链一次运行预算 [E]（_charAtSafe 重复 to_chars）。按 r13「建议挂账」与 10:45「其他缺陷和建议项一律不动」裁决，本轮不动代码。
- **A-M3-R12-01（P2 建议，挂账不修）**：备份成功缺可见诊断说明。
- 固定宿主无 type:/key: 输入通道，ui_actions 本轮不可用：可信登录后真实中文键入、三组真实 MiniMax 建议、受控迟到/恶意回包、AI/手工合法确认完整链、取消/重试动态 = **NOT_RUN / BLOCKED（通道缺口 B-M3-01）**。
- 真实 MiniMax 调用本轮 0 次（历史累计 r3 Python 3 次 ≤10）；无 402/欠费。
- 前置与挂账沿用：M2 按 Abram 裁决 carried 结束（D-M2-05/D-M4-03 BLOCKED-HOST）；M4–M7 缺陷挂账不修。
- D-M3-03/04/05/06/07 动态闭合依赖上述通道，本轮源码守卫保持，不伪造动态闭合。

## 交接

- GATES：M3 status 置 READY_FOR_REVIEW（编码方不给自己 PASS）；candidate_id=M3-r10-worktree，base=M3-r9-worktree，implementation_report 指本报告。review_* 字段（指 r13）与其他模块未动；写前备份 GATES。
- ACCEPTANCE.json 未改。
- 无 publish/listing/push/issue/消息/公网部署；未读取明文凭据/provider 密钥；未改他人改动。
- 完成后停止，等待独立 Review，不进入下一模块。

NEEDS_ABRAM=no
