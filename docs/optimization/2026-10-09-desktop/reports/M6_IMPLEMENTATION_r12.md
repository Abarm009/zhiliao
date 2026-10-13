# M6 实施报告 r12（修复轮）

- 模块：M6 桌面体验收口与持续跟进
- 轮次：r12（修复轮，严格按 `M6_REVIEW_r13.md` 缺陷清单 D-M6-03-B2 人工恢复回归 + D-M6-03-C 诊断出处隔离；上一实施 r11 / 上一 Review r13=FAIL）
- 编码方：Kimi-K3（唯一实现方）；候选 **M6-r12-worktree**，base **M6-r11-worktree**
- 日期：2026-10-14，Asia/Shanghai；未进入 M7，未派子代理
- HEAD：`8d730569546cb57310944bb299695134df773b9d`（工作树含他人未提交改动，全部保留未动）
- 源：`app/bundle/main.splash` 809344 B / 15833 行，SHA256=`72dc9c8d634b84054b2fdb12d91c8e3b29bad6d6ec65349e198e442854170ed7`；运输 digest=`1a94e5cc5f571ec2ce76ab71fffb005754ec5c363618f057764387d7f72d53f1`

## 本轮范围（只修清单项）

r13 Review 判定 FAIL 的依据：D-M6-03 两处核心残余（B2 既有合法人工记录被 r11 新增的引用门禁整份拒复——原生反例 manual_writer_no_refs / mixed_manual_model；C diagnostic 未与成功出处消费隔离——源码硬边界）。本轮严格按审查方「具体最小改法」逐条修复，不动界面、布局、文案、其他模块代码，不新增功能/入口/页面/字段。

### D-M6-03-B2 — 加载器按条目 kind 分流，人工协议豁免模型引用门禁

- 位置：`m6_load_history_view`（`app/bundle/main.splash` 现 5660–5708 行区域；函数全文见 `M6/native/build_r12/source-traces/m6_load_history_view.splash`）。
- 修法（按清单「loader 先按既有 item.kind 分流；manual 兼容既有无 refs/空引用协议，保留人工正文与 manual 标记；suggestion 继续核合法数组/非空结构化 refs」）：取 `_ikind = (_ik or "suggestion")` 后分流——
  - `manual`：`_irefs` 缺失 → 按既有写入协议恢复（writer `m6_cmd_save_manual_entry` 从不落 refs），人工正文与 `kind:"manual"` 标记保留，`refs` 落显式空数组；`_irefs` 为数组 → 原值赋 `_kept_mrefs` 保留；`_irefs` 存在但**非数组** → 仍置 `_refs_invalid` 整份按未知拒（不默默丢弃畸形数据）。
  - `suggestion`：规则与 r11 完全相同——显式核 `m7_is_array_value(_irefs)` 后原值保留，缺失/非数组 → `_refs_invalid` 整份按明确未知拒复，`kind=none` + 可见文案，原盘字节不动。
- 保持 actor/project/task/expiry/facts/来源/可见性全部既定门禁（`m6_history_schema_class` / `m6_history_items_recheck` / `m6_history_sources_check` / 出处闸）零改动；人工条目的 `manual_ref_unexpected`、`manual_unexpected_request_id` 显式人工 schema 校验保留。

### D-M6-03-C — diagnostic 与成功出处消费双向隔离

- 位置：`m6_history_provenance_ok`（现 5436–5468 行区域）与 `m6_restore_ai_requests_log`（现 8770–8870 行区域）。
- 修法一（按清单「既有 provenance 消费端明确排除 diagnostic」）：出处闸逐条读 `entry_kind`，`_ek == "diagnostic"` 的条目**既不证明成功也不作废成功**（整个匹配体跳过）；成功枚举保持 `HISTORY_ISSUED`/`PHASE_ISSUED`/`OK`（不用泛泛 SUCCESS 替换），同 rid `STALE_RESPONSE` 作废语义不变，旧无 `entry_kind` 成功记录（恢复后标 `request_result`，内存新写无 `entry_kind`）不受影响。
- 修法二（按清单「恢复端按现有合法无请求失败诊断协议核 rid/result_kind 及数值/绑定，非法诊断仍保源拒，不充当成功」）：`m6_restore_ai_requests_log` 对每条 diagnostic（显式 `entry_kind:"diagnostic"` 或 legacy NO_SERVICE 空 rid 规范化而来）在并入前校验：`result_kind` 必须为 `NO_SERVICE`、`request_id` 必须缺失或空串、`at` 必须严格数值、`task_id`/`project_id`/`actor` 必须存在且为字符串（空串合法，草稿链本无任务）。任一不符即非法诊断 → `bad=true` → **整份保源拒复**（`AI_LOG_CORRUPT=true`，原文件字节不动，`_persistAiLog` 禁止覆盖），绝不充当成功出处。合法诊断并入时 `request_id`/`result_kind` 固定写 `""`/`NO_SERVICE`，不再透传原条目自称的 rid/result_kind。
- 严格 `request_result` 路径（旧无 `entry_kind` 成功/STALE）校验一字未动；`entry_kind` 非法值仍整份拒。

### 明确未动

- D-M6-02 / D-M6-04：r13 裁决「补运行验证，勿无依据改代码」，本轮零改动；r9/r10/r11 已闭源码子项全部保留并回归断言。
- r13 保留的「同 D03 待调度边界」（`:8750` 读失败 nil return、飞行期 refs 快照时点）：审查方标注「未跑精确读失败/飞行交错，不另扩 P1，不要求无依据重写」，本轮不动。
- A-M6-01～03 建议项继续挂账；B1（r11 已闭）源码保持并回归断言；界面/布局/文案/样式一律未动。

## 证据

| 证据 | 位置 | 结果 |
|---|---|---|
| VM-compat 解析（宿主同源 vendored parser cargo test） | `M6/r12/results/r12-fix-checks.json` 第 1 项 | 实测 `1 passed; 0 failed`（真实 cargo 输出，非静态猜测） |
| 静态检查合计 | 同上 | **82/82 PASS**（含 r7–r11 已闭子项回归断言 + 本轮新断言：loader 按 `_ikind` 分流、manual 无 refs 恢复/数组保留/非数组整份拒、suggestion 严格规则不变；出处闸 `_ek != "diagnostic"` 排除 + 成功枚举保留；恢复端 `_drk != "NO_SERVICE"`/空 rid/严格 at/字符串绑定校验、非法诊断整份保源拒） |
| 函数级定位/行号 | `M6/native/build_r12/affected-functions.json` + `source-traces/` | 37 个函数（CONTEXT 旧行号已过期，以此为准） |
| 离线签名（Abram 03:02 授权 A，沙箱-only） | `M6/native/build_r12/offline-store-evidence.json` | PREPARED；新 anchor/verify rc0；install_probe 装后 main.splash 与源逐字节一致；**私钥已删 remaining=[]，2 枚私钥删除记录在案** |
| harness 构建请求 | `M6/native/REQUEST_build_r12.json`（15 场景，schema PASS） | 11 个 r11 回归场 + 新增 `history_manual_no_refs`（writer 同构无 refs 人工缓存冷启动后 state 保留 manual 正文）/ `history_manual_mixed`（人工+双 refs 模型条目混合缓存两者按序保留）/ `history_manual_bad_refs`（manual 的 refs 为布尔 → 整份明确未知、原盘不动）/ `ai_log_diagnostic_fake_success`（diagnostic 自称 PHASE_ISSUED 且 rid 匹配 → 整份保源拒复、字节保全、零解析；合法诊断正对照仍为 ai_log_no_service_mixed） |
| 构建校验 | `M6/native/build_r12/build-validation.json` | watched 文件前后不变；15/15 种子 main 与源一致；catalog 齐全；host_started=false；model_calls=0 |

原生执行证据：待驱动在沙箱外跑 `REQUEST_build_r12.json`，落 `M6/native-runs/build_r12_REQUEST_build_r12/`；本报告交付时该目录尚不存在，**原生结果未读回前不声称任何业务 PASS**。冷启动零 `[E]` 回归以驱动跑回的 host.log 为准（cold_fresh 场已含）。

## 尚未完成（如实标记）

- 宿主级冷启动零解析、人工缓存恢复反例复验、诊断伪成功整份拒复：以 harness 回读为准，本轮交付前未原生执行（构建方不自行启动宿主）。
- D02 实际恢复两分支、D04 收藏故障对账、提醒通知/去重/旧约失效/跳回、三角色可信登录流程、三条真实 AI 链、视口/150%/键盘：保持 r13 的 NOT_RUN/BLOCKED 状态，本轮白名单未变，不凭源码闭合冒充运行通过。
- 真实 MiniMax：本轮 0 调用（needs_model=false，预算留审查轮，模块合计 ≤10）。
- M2–M5/M7 挂账缺陷未碰（含 BLOCKED-HOST 的 D-M2-05/D-M4-03）。

## 交接

- candidate_id=`M6-r12-worktree`，base=`M6-r11-worktree`；清单 `runtime/optimization/2026-10-09/M6/r12/CANDIDATE.json`。
- GATES.json 仅 M6 置 READY_FOR_REVIEW，不给自己 PASS；等待独立 Review，不进入 M7。
- 审查建议：按 r13 必修清单逐项核 B2（manual 无 refs/[]/混合恢复 + 坏引用仍拒）与 C（diagnostic 伪成功整份拒 + 合法 NO_SERVICE 恢复 + 出处闸排除）闭合 + cold_fresh 零解析回归；审查 seed 须带 apps/catalog.json（harness 自动补齐已可用）。

## 合规

- 未启动 launcher / sandbox-exec / pgrep / osascript / 辅助功能；未读明文凭据与 `runtime/secrets`；未写 `~/.octosense` 或项目外。
- 无 publish/公开签名/listing/git push/issue/评论/部署/改计费/发消息；离线签名私钥已删并记录（remaining=[]）。
- 未 reset/stash/删除他人改动。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
