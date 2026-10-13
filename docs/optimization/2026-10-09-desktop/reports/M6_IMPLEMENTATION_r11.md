# M6 实施报告 r11（修复轮）

- 模块：M6 桌面体验收口与持续跟进
- 轮次：r11（修复轮，严格按 `M6_REVIEW_r12.md` 缺陷清单 D-M6-03-B1/B2/C；上一实施 r10 / 上一 Review r12=FAIL）
- 编码方：Kimi-K3（唯一实现方）；候选 **M6-r11-worktree**，base **M6-r10-worktree**
- 日期：2026-10-14，Asia/Shanghai；未进入 M7，未派子代理
- HEAD：`8d730569546cb57310944bb299695134df773b9d`（工作树含他人未提交改动，全部保留未动）
- 源：`app/bundle/main.splash` SHA256=`cb4820f34008090f…`（完整值见 `M6/native/build_r11/offline-store-evidence.json` 与 `r11-fix-checks.json`）；运输 digest=`009e138f20d1f3c6a7891335d847d94285b23a403efde4b321a9c7a6416787dc`

## 本轮范围（只修清单项）

r12 Review 判定 FAIL 的依据：D-M6-03 三处核心残余（B1 阶段来源 schema 与消费者不一致 / B2 重开加载 refs 变空数组 / C 自产 NO_SERVICE 诊断毒化整份出处恢复）。本轮严格按审查方改法逐条修复，不动界面、布局、文案、其他模块代码，不新增功能/入口/字段。

### D-M6-03-B1 — 阶段自身来源与历史来源集合统一 schema

- 位置：`m6_cmd_request_phase`（`app/bundle/main.splash` 现 5317 行区域）。
- 修法（按清单「阶段自身来源保存 task_id/task_version/evidence_version，与历史来源集合统一」）：`source_versions: [m6_ref_snapshot("task", t.id)]`（产出 `ref_type/ref_id`、缺 `task_id`，来源闸必拒 `source_task_id_empty`）改为 `source_versions: [hf_source_version(t.id, t.version, _currentEvidenceVersion(t.id))]`，与设备历史链 `m6_history_source_snapshot` 产出的 `{task_id, task_version, evidence_version}` 完全同构；消费者 `m6_history_sources_check` / `m6_history_sources_drift` 不变。
- refs 继续使用 `ref_type/ref_id` 完整集合，全部引用门禁（存在/同项目/可见/版本/证据漂移）保留未动。

### D-M6-03-B2 — 重开加载显式保留全部 refs

- 位置：`m6_load_history_view`（`app/bundle/main.splash` 现 5646–5680 行区域）。
- 修法（按清单「显式核 _irefs 为数组后原值赋给独立变量，否则明确拒/未知；不要对数组使用 or []」）：删除 `refs: (_irefs or [])`（宿主 `or` 默认值不保留数组，r12 原生反例：种子双引用条目冷启动后 `refs=[]`）。现仅在 `_irefs != nil && m7_is_array_value(_irefs)` 时把原数组赋给独立变量 `_kept_refs` 随条目恢复；缺失/非数组 → 置 `_refs_invalid`，整份缓存按**明确未知**拒复：`kind=none` + 可见状态文案「历史建议缓存条目缺可核出处（refs 缺失或非法），整份视为未知；原盘未改，可重新请求或手工记录」，不默默丢引用、不改原盘字节。
- 下游全部版本/权限/出处重核（`m6_history_sources_check`、`m6_history_items_recheck` 等）保留。

### D-M6-03-C — 自产 NO_SERVICE 诊断与出处恢复分 schema

- 位置：`m6_restore_ai_requests_log`（`app/bundle/main.splash` 现 8760 行区域）。
- 修法（按清单「明确合法无请求失败诊断 schema，它不作为出处、但不毒化其他合法记录；成功/STALE 仍严格校验」）：每条记录先过 `hf_normalize_ai_log_entry(e, true)`（M2 hardfix 层既有函数，未改）：应用自产 `result_kind=NO_SERVICE` 且 `request_id` 为空的失败诊断规范化为 `entry_kind="diagnostic"` 恢复——**不作为出处**（出处闸仍要求 SUCCESS + 非空 rid + 同任务同主体同项目），也**不再毒化整份恢复**。
- 旧版无 `entry_kind` 的成功/STALE 记录（既有日志与未来 `recordModelMeta` 写入）仍走**原严格校验**（rid/result_kind 非空、task/project/actor 存在、at 严格数值）；`entry_kind` 非法值仍整份拒。
- 损坏保源不变：校验失败 → `AI_LOG_CORRUPT=true`，原文件字节不动，`_persistAiLog` 禁止覆盖。
- 无请求失败诊断三处写入点（`m6_request_device_history` / `m6_request_phase_meaning` / `requestAiSuggestion` 的 NO_SERVICE 分支）未改——新写入在下次恢复时经同一 legacy 规范化兼容，新旧记录均可用。

### 明确未动

- D-M6-02 / D-M6-04：r12 裁决「补验证，勿无依据重写」，本轮零改动；r9/r10 已闭源码子项全部保留并回归断言。
- r12「同 D03 待调度验证边界」段（读失败 nil return、飞行期 refs 快照时点）：审查方标注「需精确读失败/请求交错实证；本轮动态结果未知」，不在必修清单，本轮不动。
- A-M6-01～03 建议项继续挂账；界面/布局/文案/样式一律未动。

## 证据

| 证据 | 位置 | 结果 |
|---|---|---|
| VM-compat 解析（宿主同源 vendored parser cargo test） | `M6/r11/results/r11-fix-checks.json` 第 1 项 | 实测 `1 passed`（非静态猜测） |
| 静态检查合计 | 同上 | **75/75 PASS**（含 r7–r10 已闭子项回归断言 + 本轮 B1/B2/C 新断言：无 `(_irefs or [])`、有 `_kept_refs`/`_refs_invalid` 明确未知、phase 来源用 `hf_source_version` 且无残留 `source_versions: [m6_ref_snapshot`、恢复走 `hf_normalize_ai_log_entry` + diagnostic/request_result 双路径 + 严格校验保留） |
| 函数级定位/行号 | `M6/native/build_r11/affected-functions.json` + `source-traces/` | 37 个函数（CONTEXT 旧行号已过期，以此为准） |
| 离线签名（Abram 03:02 授权 A，沙箱-only） | `M6/native/build_r11/offline-store-evidence.json` | PREPARED；新 anchor/verify rc0；install_probe 装后 main.splash 与源逐字节一致；**私钥已删 remaining=[]** |
| harness 构建请求 | `M6/native/REQUEST_build_r11.json`（11 场景，schema PASS） | 8 个 r10 回归场 + 新增 `ai_log_no_service_mixed`（成功+空 rid NO_SERVICE 诊断+成功混合日志：不毒化恢复、字节保全、零解析）/ `history_refs_restore`（双 refs 阶段缓存冷启动后 state 逐字段等于原盘）/ `history_refs_bad_member`（refs 为字符串 → 明确未知、原盘不动） |
| 构建校验 | `M6/native/build_r11/build-validation.json` | watched 文件前后不变；11/11 种子 main 与源一致；catalog 齐全；host_started=false；model_calls=0 |

原生执行证据：待驱动在沙箱外跑 `REQUEST_build_r11.json`，落 `M6/native-runs/build_r11_REQUEST_build_r11/`；本报告交付时该目录尚不存在，**原生结果未读回前不声称任何业务 PASS**。冷启动零 `[E]` 回归以驱动跑回的 host.log 为准（cold_fresh 场已含）。

## 尚未完成（如实标记）

- 宿主级冷启动零解析、refs 保留反例复验、混合日志恢复：以 harness 回读为准，本轮交付前未原生执行（构建方不自行启动宿主）。
- D02 实际恢复两分支、D04 收藏故障对账、提醒通知/去重/旧约失效/跳回、三角色可信登录流程、三条真实 AI 链、视口/150%/键盘：保持 r12 的 NOT_RUN/BLOCKED 状态，本轮白名单未变，不凭源码闭合冒充运行通过。
- 真实 MiniMax：本轮 0 调用（needs_model=false，预算留审查轮，模块合计 ≤10）。
- M2–M5/M7 挂账缺陷未碰（含 BLOCKED-HOST 的 D-M2-05/D-M4-03）。

## 交接

- candidate_id=`M6-r11-worktree`，base=`M6-r10-worktree`；清单 `runtime/optimization/2026-10-09/M6/r11/CANDIDATE.json`。
- GATES.json 仅 M6 置 READY_FOR_REVIEW，不给自己 PASS；等待独立 Review，不进入 M7。
- 审查建议：按 r12 必修清单逐项核 B1/B2/C 闭合 + cold_fresh 零解析回归；审查 seed 须带 apps/catalog.json（harness 自动补齐已可用）。

## 合规

- 未启动 launcher / sandbox-exec / pgrep / osascript / 辅助功能；未读明文凭据与 `runtime/secrets`；未写 `~/.octosense` 或项目外。
- 无 publish/公开签名/listing/git push/issue/评论/部署/改计费/发消息；离线签名私钥已删并记录（remaining=[]）。
- 未 reset/stash/删除他人改动。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
