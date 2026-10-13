# M6 实施报告 r10（修复轮）

- 模块：M6 桌面体验收口与持续跟进
- 轮次：r10（修复轮，严格按 `M6_REVIEW_r11.md` 缺陷清单；上一实施 r9 / 上一 Review r11=FAIL）
- 编码方：Kimi-K3（唯一实现方）；候选 **M6-r10-worktree**，base **M6-r9-worktree**
- 日期：2026-10-13，Asia/Shanghai；未进入 M7，未派子代理
- HEAD：`8d730569546cb57310944bb299695134df773b9d`（工作树含他人未提交改动，全部保留未动）
- 源：`app/bundle/main.splash` 701133 B / 13848 行，SHA256=`3bc555f2f0e4134120d7b8eb71d3a4e74f860cb6cc8ee64a3539fcc9203ef82b`；运输 digest=`7e968a23e43386e9eae57e11e4e68bdf494f933dbe28ec43f995d75ec94e1fec`

## 本轮范围（只修清单项）

r11 Review 判定 FAIL 的依据：D-M6-03 三处剩余源码缺口（A/B/C）+ R-M6-02（原生路线出现禁用 osascript）。D-M6-02/04 源码子项 r9 已闭合，本轮按要求不做无依据重写，全部保持。本轮改动：

### D-M6-03 A — 历史来源快照贯穿持久缓存消费（`app/bundle/main.splash`）

- `m6_request_device_history`：构建 `[repair_history]` 时同步生成**实际送入模型的来源集合快照** `m6_history_source_snapshot(_harr)`（按 task_id 去重，逐来源记录 `task_version` + `evidence_version`），成功结果带 `sources` 返回。
- 回包时新增同一集合漂移闸 `m6_history_sources_drift(_src_snap)`：请求飞行期间来源任务 H 的版本/证据变化 → `STALE_RESPONSE` 作废不落；引用条目同样过 `m6_history_refs_drift`。
- `m6_cmd_request_history`：视图缓存持久化 `source_versions` + 每条建议的 `refs` 快照。
- 新增 `m6_history_sources_check(hv, t)`：含模型建议的缓存必须带 `source_versions`（缺=旧格式=未知），逐来源核存在/同项目/当前身份可见/版本/证据，并核每条建议全部 refs 快照；`m6_load_history_view` 与 `m6_history_view_usable` 双闸同标准接入。

### D-M6-03 B — 阶段正文全部 refs 持久与逐条消费

- `m6_request_phase_meaning`：`_vrefs` 每条改为 `m6_ref_snapshot`（task 引用带任务版本/证据版本），回包时全部 refs 过漂移闸（不再只核第一个）。
- `m6_cmd_request_phase`：条目持久化完整 `refs: _res_refs` + 自身来源快照；**模型缺引用时不再替代成本任务 ID 制造合法来源**——按未知处理（kind=none + 人工出口「存为手工阶段说明」）。
- `m6_history_items_recheck`：条目带 `refs` 数组时逐条按当前身份/项目/权限重核（撤权/跨项目/不存在即拒）。

### D-M6-03 C — 持久请求日志恢复路径

- 新增 `m6_restore_ai_requests_log()`：在 `m6_load_history_view` 消费历史缓存**之前**从 `ai_requests.jsonl` 恢复出处记录到 `AI_REQUESTS_LOG`（load 与登录重核两条路径都覆盖）；严格逐条目 schema（request_id/result_kind 非空字符串、at 严格数值、task/project/actor 字段存在）。
- 顶层非数组或任一条目非法 → `AI_LOG_CORRUPT=true`：**保留原文件字节、禁止 `_persistAiLog` 覆盖**，出处一律按未知（provenance 闸保留不删）。
- 恢复只执行一次（`AI_LOG_RESTORED`），重开后第一次新请求 push 在恢复之后，不会把旧出处全部覆盖。

### R-M6-02 — harness 路线禁 osascript（构建/驱动侧，按 r11 改法）

- `driver/harness/profile.sb.tmpl`：新增 `(deny process-exec (literal "/usr/bin/osascript"))`，沙箱内宿主无法派生 osascript；禁读/写目录/网络限制不变；驱动侧 ui_actions 在沙箱外执行不受影响。
- `driver/harness/native_harness.py`：`pgid_members` 采样改为 `pid/pgid/args`（完整 argv 可归因，不再只有 comm）；`profile_probes` 新增 `osascript_exec_denied` 探针（`sandbox-exec -f sb /usr/bin/osascript -e 'return 0'` 必须失败）并纳入 `profile_probes.ok` 判据。

## 证据

| 证据 | 位置 | 结果 |
|---|---|---|
| VM-compat 解析（宿主同源 vendored parser cargo test） | `M6/r10/results/r10-fix-checks.json` 第 1 项 | 实测 `1 passed`（非静态猜测） |
| 静态检查合计 | 同上 | **72/72 PASS**（含 r7–r9 已闭子项回归断言 + 本轮 D03-A/B/C、R-M6-02 新断言） |
| 函数级定位/行号 | `M6/native/build_r10/affected-functions.json` + `source-traces/` | 37 个函数（CONTEXT 旧行号已过期，以此为准） |
| 离线签名（Abram 03:02 授权 A，沙箱-only） | `M6/native/build_r10/offline-store-evidence.json` | PREPARED；新 anchor/verify rc0；install_probe 装后 main.splash 与源逐字节一致；**私钥已删 remaining=[]** |
| harness 构建请求 | `M6/native/REQUEST_build_r10.json`（8 场景，schema PASS） | cold_fresh 零解析回归闸 + 6 个 followup 场 + 新增 `ai_log_valid_restore`（日志恢复且文件字节不变）/ `ai_log_corrupt`（损坏保源、零解析、UI 渲染） |
| 构建校验 | `M6/native/build_r10/build-validation.json` | watched 文件（含 harness 两件）前后不变；8/8 种子 main 与源一致；host_started=false；model_calls=0 |

原生执行证据：待驱动在沙箱外跑 `REQUEST_build_r10.json`，落 `M6/native-runs/build_r10_REQUEST_build_r10/`；本报告交付时该目录尚不存在，**原生结果未读回前不声称任何业务 PASS**。

## 如实标记（未执行/阻塞）

- 冷启动零解析门禁：本轮源码经 VM-compat cargo 解析实测通过；宿主级冷启动零 `[E]` 以驱动跑回的 host.log 为准（harness 请求已含 cold_fresh 场，结果待回读）。
- D-M6-02/D-M6-04 的**运行闭合**（真实恢复点击、收藏故障注入、同 Store 重开）：仍依赖 r11 所述「当前授权内的可信内置输入与受控调度」，本轮白名单未变，保持 NOT_RUN，不凭源码闭合冒充运行通过。
- R-M6-02 的两 PID 来源归因：进程采样已改为完整 argv，下一次 harness 运行即可归因；profile 拒绝执行有探针实证（随每场 profile_probes 输出）。
- 真实 MiniMax：本轮 0 调用（needs_model=false，预算留审查轮，模块合计 ≤10）；三链真实模型证据仍 NOT_RUN。
- D02 恢复出口原生可见性：r11 明确「不因本轮未登录重复重写布局」，本轮未动布局；待可信登录通道后实测。

## 合规

- 未启动 launcher / sandbox-exec / pgrep / osascript / 辅助功能；未读明文凭据与密钥；未写 `~/.octosense` 或项目外。
- 无 publish/公开签名/listing/git push/issue/评论/部署/改计费/发消息；离线签名私钥已删并记录。
- 未 reset/stash/删除他人改动；M2–M5/M7 挂账缺陷未碰。
- GATES.json 仅 M6 置 READY_FOR_REVIEW，不给自己 PASS。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
