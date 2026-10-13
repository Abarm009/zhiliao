# M6 实施报告 r9

- 模块 / 目标：M6 桌面体验收口与持续跟进 · 修复轮 r9 —— 严格按 M6_REVIEW_r10 缺陷清单修 D-M6-02 / D-M6-03 / D-M6-04 的剩余子项；已关闭子项（严格类型门禁、合法加载、整份原文保护、写后读回、回包 rid 闸、saved=false 回退等）不重做、不回归。
- candidate_id / base_candidate_id：`M6-r9-worktree` / `M6-r8-worktree`。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d`；工作树含他人（ui-redesign、M2/M4/M5/M7 各轮）未提交改动，全部保留未动。修改后 `app/bundle/main.splash` SHA256=`b2df2c0faf850875025321f317e6bf642ac4fef0b9d517f01bf8efad8a8fb1d1`，684541 B / 13504 行；bundle digest=`e0cbb9c6b39b3924f24e237060a3438ce75406db76a220edf7ece3c3440d3502`。
- 目标宿主 / 二进制：`runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（沿用，未改动；哈希在 `native/build_r9/start-snapshot.json`）。本机未启动宿主；原生验证交驱动 harness（`M6/native/REQUEST_build_r9.json`，6 场景，needs_model=false）。
- 实际模型路由检查：本轮无模型调用（needs_model=false，预算留审查轮 ≤10）。
- 已检查的前置 PASS 报告：无新前置；M5 仍 FAIL 挂账（按 Abram 裁决继续局部修复）。
- 本轮修改文件与原因：`app/bundle/main.splash`（外科式修补，见下）+ 新增 `M6/native/prepare_build_r9.py`、`M6/native/REQUEST_build_r9.json`、`M6/native/build_r9/`（快照/追踪/离线签名证据/seeds/store）、`M6/r9/`（CANDIDATE + results）。

## 0. 阻断适配：B-M5-01（M5 r12 重开的解析回归，确实阻断本模块）

- 现象：r9 首轮 VM-compat parse 回归失败，定位 `app/bundle/main.splash:9466` `m5_fs_probe` 内 `(2166136261 & 0xFFFFFFFF).to_string()`（及紧邻 `:9469` `(32 >> 4).to_string()`）。这两行是 M5 r12 修复轮新增探针（注释自标 D-M5-04 r12 修复轮 C），不属于 M6 改动；M5_REVIEW_r12 的 B-M5-01 已记录同一宿主解析失败（其 host.log 报 `:9227:34 Expected )`，业务区全空白）。
- 实证：vendored parser 与固定宿主均首报该处 `Expected )`；单行/最小组合探针在 octoscript 测试内复现；try/catch 不能保护解析期失败。M5 自己 r12 Review 的 11 场 host.log 每场 4 条同源解析诊断为佐证。
- 处置（最小语法适配，不撤销 M5 探针语义，不碰其他 M5 代码）：
  - `:9466` → `let _bbn = 2166136261` + `try { _bbn = (_bbn ^ 0) & 0xFFFFFFFF } catch { _bb = "__throw__" }` + `if _bb == "" { _bb = _bbn.to_string() }`（同构对照已实证零解析的 `:5132 h = (h ^ c) & 0xFFFFFFFF`；`^ 0` 恒等，仍探测大数 `& 0xFFFFFFFF` 宿主行为）；
  - `:9469` → `let _shn = 32` + `try { _shn = _shn >> 4 } catch { _sh = "__throw__" }` + `if _sh == "" { _sh = _shn.to_string() }`（同构对照 `:5147 v = v >> 4`，仍探测 `>>` 宿主行为）。
- 结果：VM-compat parse（vendored makepad parser，与宿主同源）恢复 `1 passed`；探针输出键 `band_big_probe` / `shift_probe` 保留。此行修复同时在源码注释中标记为 M6 r9 阻断适配，供 M5 下一轮核对（B-M5-01 的责任仍在 M5，本模块不代领）。

## D-M6-02 剩余项修复（恢复动作进入实测客户区 / 空 banner 不占高）

1. 左栏布局：`recovery_tools`（数据恢复 4 个动作：任务保留原文/内存覆盖、提醒保留原文/内存覆盖）移到左栏 `ScrollYView` 滚动内容的最顶部，先于所有 banner 与提醒槽——pending 时首屏客户区内即达，不再被后续块高度推挤出可见区（r10 实图裁切根因）。
2. 空 banner 收合：`tasks_banner` / `m6_status_label` / `fu_banner` 三个 `max_lines: 0` Label 在文本为空时 `set_visible(false)`（appleRefreshPresentation 内先取文案再 set_text + set_visible），空块不再占显著高度。
3. r7/r8 已关子项保持不动并由静态检查复核：严格数值门禁、整份拒/原文备份、写后读回、故障优先空态、恢复入口命令。

## D-M6-03 剩余项修复（结构化出处 / 完整消费门禁）

1. 结构化引用：设备历史 items 与阶段建议 item 新增 `ref_type` / `ref_id` 字段（不再只拼进 source 字符串）；`m6_request_phase_meaning` 成功结果新增 `refs`（通过校验的引用列表），阶段缓存取首个合法引用，缺引用显式绑定本任务自身。人工记录显式人工 schema：`kind:"manual"` + 空 ref + `request_id:""` + `expires_at_ms:0`。
2. 事实/证据快照：所有缓存构造（成功/失败/人工）携带 `facts_version: _currentFactsVersion()` 与 `evidence_version: _currentEvidenceVersion(t.id)`。
3. 新增四个共享重核辅助（load 与 render 双闸同标准）：
   - `m6_history_items_recheck(items, t)`：kind 仅允许 suggestion|manual；suggestion 必须带非空结构化 ref 且按当前身份/项目/权限逐条过 `m6_validate_reference`（撤权/跨项目/不存在即拒）；manual 必须空引用。
   - `m6_history_schema_class(hv)`：含模型建议的缓存必须有非空 request_id 且 expires_at_ms 为严格正数（`m7_is_strict_number_value` 且 >0）——缺出处/缺期限一律拒，不再以空值跳过校验；纯人工缓存必须 request_id 为空（显式人工 schema）。
   - `m6_history_provenance_ok(hv)`：AI_REQUESTS_LOG 须存在同 request_id + 同任务 + 同主体 + 同项目的成功记录（HISTORY_ISSUED / PHASE_ISSUED / OK），且无同 request_id 的 STALE_RESPONSE 作废记录。
   - `m6_history_facts_check(hv)`：缺快照（旧格式）或 facts/evidence 与当前不一致即失效。
4. `m6_load_history_view`：恢复时按 主体/项目 → 任务事实版本 → schema 分流 → 到期 → 出处 → 事实/证据快照 → 目标任务存在 → 引用当前权限 全链重核，任一不符 → kind=none + 各自可见原因文案；解析侧保留 ref/facts/evidence 字段。boot 未登录仅载入，登录后 `m2_login_begin` 重核不变。
5. `m6_history_view_usable`：渲染闸同步补 schema 分流 / 出处 / 快照 / 引用重核，与 load 完全同标准（防会话内切主体/切任务/撤权后继续显示）。

## D-M6-04 剩余项修复（全分支固定 key / absent-corrupt 区分 / 完整绑定 / 清理核实）

1. `m6_pin_marker_write(rid, task_id, act, exp_pinned, reason)`（新）：统一落盘对账标记，写后读回逐字节核实，返回真实 bool。`_exp_pinned` 在写盘前即固定，供所有分支共用。
2. `m6_save_prefs` 四个「已写但未知」分支全部落同 key 标记（不再只有 finalize 分支）：tasks_write_failed / readback_mismatch / state_write_failed / receipt_finalize_failed；标记落盘未核实时如实覆盖状态文案（「对账标记落盘未核实（待人工核对）」），不吞错。
3. `m6_pin_marker_read` 区分 absent / corrupt / ok：坏标记（读失败/parse 失败/字段非法）不再与无标记同返回；`m6_pin_marker_pending_for` 对 corrupt 保守返回 true（未知闸保持，禁盲重做）；`m6_reconcile_marker_boot` 对 corrupt 不消费不清理，置可见状态「收藏对账标记损坏…请人工核对」。
4. boot 消费者完整绑定重核：找回执后核 `command == "togglePin"` 且 receipt 的 task_id/actor 与标记一致；矛盾则不改任何回执、保留标记、可见反馈（「绑定矛盾…未改任何回执」）。
5. `m6_pin_marker_clear()`（新）：清标记写空串后读回逐字节核实；两处清理点（回执已 final / 对账完成）只有核实通过才报「标记已清」，否则报「标记清理未核实（写/读回失败），保留标记待重试」。
6. r7/r8 已关子项保持：固定目标先于 eager cleanup、读回比对固定预期快照、saveReceipts/saveState 返回值消费、boot 对 togglePin 跳过版本判据、未清标记禁盲重做、收藏不递增业务 version。

## 证据与验证

- `M6/r9/results/r9-fix-checks.json`：**56/56 PASS**（含 VM-compat parse cargo test 实测 `1 passed`、B-M5-01 适配检查、D02/D03/D04 全部新旧静态断言）。
- `M6/native/REQUEST_build_r9.json`：6 场景（cold_fresh / followup_valid_restore / followup_bool_time / followup_string_time / followup_null_member / followup_truncated），needs_model=false，schema 校验 PASS，交驱动在沙箱外执行；预期落 `M6/native-runs/build_r9_REQUEST_build_r9/`。冷启动零解析 + 工作台渲染为本轮硬性回归项；六坏盘/合法盘核严格门禁、原文保护与恢复入口在左栏顶部可见。
- `M6/native/build_r9/`：start-snapshot / main.splash.snapshot / affected-functions.json（30 个函数）/ source-traces / offline-store-evidence.json（新 anchor `8878ed96f175…`；hub verify rc0；install_probe ALL OK；**两私钥已删，remaining=[]**）/ fixtures.json / build-validation.json（watched files unchanged, model_calls=0）。
- 真实模型调用：0 次（预算留审查轮 ≤10；无 402/欠费）。
- 未执行（如实标记）：可信三角色实际收藏/搜索/重登、真实提醒通知去重/改约取消/跳回撤权、三条真实模型链、同 Store 跨进程重启、150%/键盘全流程 —— 均需驱动 harness 与审查轮可信入口；本轮无任何 NOT_RUN 项被记为通过。

## 交接

- GATES.json：M6 status → `READY_FOR_REVIEW`，candidate=`M6-r9-worktree`，base=`M6-r8-worktree`，implementation_report 指向本报告，evidence_root=`runtime/optimization/2026-10-09/M6/r9`；review_report 保留指向 M6_REVIEW_r10；其他模块与构建字段未动。
- 不进入下一模块；等待独立 Review。
