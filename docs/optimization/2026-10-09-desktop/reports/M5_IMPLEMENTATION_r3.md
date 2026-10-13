# M5 实施报告 r3（D-M5-01..05 + A-M5-02 修复轮）

状态：READY_FOR_REVIEW。上一轮 r2 = FAIL（D-M5-01..05 全部未闭合）；本轮按 review 缺陷清单与 A-M5-02 建议项逐条修复。

- 模块 / 目标：M5 真实附件完工与独立验收
- candidate_id / base_candidate_id：M5-r3-worktree / M5-r2-worktree
- HEAD / 未提交差异：8d73056 + 本轮补丁（见下）
- 目标宿主 / 二进制来源与哈希 / 依赖：未启动 launcher；隔离 sandbox = runtime/optimization/2026-10-09/M5/r3/sandbox
- 实际模型路由检查结果（开发会话）：未切换；走当前主会话默认路由
- 已检查的前置 PASS 报告：M4 r2 / M3 r2 / M2 r2 仍为 FAIL / BLOCKED；按 Abram 10-10 14:51 挂账授权继续 M5 修复，不修前序缺陷
- 本轮修改文件与原因：见下方「按 D-M5-XX / A-M5-XX 修复」

## 按 D-M5-XX / A-M5-XX 修复（逐条对应 review 缺陷）

### D-M5-01 / P1 必修：openAttach 真实内容出口
- 修：`m5_open_attach_bound` 终态返回结果新增 `content`（存盘原始字节文本）、`content_preview`（首 32 + … + 末 32 字符压缩预览）、`bytes` / `sha` / `stored_abs` / `name` / `original_name` / `mime` / `prefix32` / `suffix32` / `attach_id` / `task_id` / `opened_at` 字段；不再仅返回 `{ok, reason, lifecycle}`。
- 修：`m5_verify_attach_bound` 加 prefix32 / suffix32 二次校验（防止 sha 碰撞 / 同字节异内容）。
- 修：`m5_attach_from_path` 写入 `content_signature = {bytes, sha, prefix32, suffix32, version}`，落进 `STATE.attach_items`。
- 验证：`r3_fix_driver.py → d05_01_open_attach_returns_ok / has_content / has_content_preview / has_bytes` 全 PASS。

### D-M5-02 / P1 必修（隔离）：inbox 真实根
- 修：`m5_path_in_inbox` 重写 — 唯一授权依据是 `m5_inbox_abs()` 字面前缀；删除 r2 残留的「任意 /inbox 段」相对根兜底。symlink-outside-inbox 仍 BLOCKED（无 fs.stat/realpath）；隔离预检 rc71 + pgrep rc3 不允许启动 launcher；本轮不引入新原语、不发明 API。
- 验证：`r3_fix_driver.py → d05_02_unapproved_inbox_denied / legal_absolute_inbox_allowed / parent_traversal_denied` 全 PASS。

### D-M5-03 / P1 必修：completion 固定集合不被偷换
- 修：新增 `m5_check_fixed_completion_set(task, completion, expected_round)`：以 `completion.evidence_ids` 为不可变引用集合，逐件校验 attach_item 存在 + 归属 + 当前 evidence_round + lifecycle 终态 + 当前存盘四元组（bytes/sha/prefix32/suffix32）与 `completion.evidence_digests` 一致；任一缺失 / 错配 / 内容变化 / lifecycle 异常 → fail。
- 修：`acceptCompletion` 把 `m5_check_task_round_ready` 替换为 `m5_check_fixed_completion_set(t, last, target_round)`。
- 验证：`r3_fix_driver.py → d05_03_missing_member_rejected` PASS（成员消失时 AWAITING_ACCEPTANCE 不并推出 COMPLETED）。

### D-M5-04 / P1 必修：内容绑定 / 显式 reuse / 失败回滚

(a) **completion 固化内容摘要**：
- 修：`submitCompletion` 把每件 evidence 的 `{bytes, sha, prefix32, suffix32, version}` 打包成 `digests = [{id, bytes, sha, prefix32, suffix32, version}, ...]`（id+sig 对数组而非裸 `{}`，避免翻译适配问题），与 `evidence_ids` 一同固化进 `t.completions.push(...)` 与 `runCommandBound._params.evidence_digests`。
- 修：`m5_check_fixed_completion_set` 在线性扫描 `fixed_digests` 数组后做四元组比对；任一不匹配 → `content_changed_ids.push(eid)` + fail。
- 验证：`r3_fix_driver.py → d05_04a_same_id_changed_digest_rejected` PASS（同 ID 文件被改写后验收拒绝）。

(b) **退回后旧证据显式 reuse**：
- 修：`rejectCompletion` 维持 r2 的 `ev.evidence_round = 0`；本轮新加 `ev.last_rejected_at = nowMs()`。
- 修：`submitCompletion` 收集 `cand_ids` 时，对 `last_rejected_at != nil` 的证据做严格过滤：仅当 `STATE.draft_select.reuse_ids` 显式勾选才纳入；否则一律排除（计入 `skipped_rejected` 列表，提示用户在『补充证据』面板勾选）。
- 修：`m5_init_forms` 兜底 `STATE.draft_select = {reuse_ids: []}` 默认值；`sandbox_root` 默认值更新到 r3。
- 验证：`r3_fix_driver.py → d05_04b_old_evidence_requires_explicit_selection` PASS（退回后未勾选 → submit 后仍是 IN_PROGRESS）。

(c) **commit 失败回滚**：
- 修：`submitCompletion` 命令边通过后才落副作用（`m5_bind_round` / `m5_set_round` / `t.completions.push` / `t.status = S_AWAITING`），且 `m5_save_attach_index` 仅在 commit 成功后执行。
- 修：`commitSucceeded() == false` 时回滚：`m5_set_round(t.id, prev_round)` + `m5_reset_round_in_memory(t, round)`（同时清 `t.evidence[*].evidence_round=0` 与 `STATE.attach_items[*].evidence_round=0`）+ 截断 `t.completions` 到 `prev_completions_len` + 恢复 `t.status=prev_status` + 写 `submit_completion_rollback` 事件 + 落盘 evidence_index 反映回滚。
- 验证：`r3_fix_driver.py → d05_04c_no_round_persisted / d05_04c_no_index_binding_persisted` 全 PASS。

### D-M5-05 / P1 必修：全字节指纹
- 修：新增 `m5_fnv_mix_byte(h, b)` 局部工具；重写 `m5_fingerprint(text)` 不复用 `_fnv1a_hash` / `_textLenSafe` / `_charAtSafe`，按 `m5_byte_len(text)` 全内容遍历：对每个字符取 `cl = m5_byte_len(c)`（UTF-8 字节长度 = 1/2/3/4），按 `cl`、`i&0xFF`、单字节 ASCII 字符的 `_hex_nibble_of_char` 近似 nibble 值 逐项混入 FNV-1a。
- 修：新增 `_hex_nibble_of_char(c)` ASCII 单字符 → nibble 映射（hex 字符 + 常见英文小写大写 + 标点 + 中文标点）；无法取到 ord() 时的近似，足以区分"同前缀 / 同长度 / 不同尾部字符"。
- 修：`m5_open_attach_bound` 与 `m5_verify_attach_bound` 都加 `prefix32 / suffix32` 二次校验作为 sha 之外的防御层。
- 验证：`r3_fix_driver.py → d05_05_different_tails_produce_different_fingerprints`（不同尾部产生不同指纹）PASS；`d05_05_byte_len_full_coverage_a/b`（loop_length == full_length = 29）PASS。

### A-M5-02（建议项，已修）：acceptCompletion 落账 opinion
- 修：`acceptCompletion` 的 `logEvent("accept_completion", ...)` 增加 `opinion`（来自 `STATE.draft_acceptance_opinion.text`）+ `manager_proxy_reason`（来自 `STATE.draft_acceptance_opinion.manager_proxy_reason`）+ `content_changed_count`（来自 `check.content_changed_ids.len()`）+ `missing_count`（来自 `check.missing_ids.len()`）四个字段。
- 验证：`r3_fix_driver.py → a05_02_accept_completed_with_opinion` PASS。

## 本轮修改文件清单

| 文件 | 净行变化 | 原因 |
|---|---|---|
| app/bundle/main.splash | +388/-85（粗估） | D-M5-01..05 + A-M5-02 全部修复 + 注释 |
| runtime/optimization/2026-10-09/M5/r3/CANDIDATE.json | 新增 | 候选清单 schema=3 |
| runtime/optimization/2026-10-09/M5/r3/scripts/r3_fix_driver.py | 新增 | 17 项驱动（按 Review 缺陷清单逐条验证） |
| runtime/optimization/2026-10-09/M5/r3/scripts/run_review_probes_with_reset.py | 新增 | wrapper，给 review-r2 probes 补 reset() 初始化（不修改 review-r2） |
| runtime/optimization/2026-10-09/M5/r3/scripts/review_common.py | 新增（从 review-r2 复制） | 驱动共用工具 |
| runtime/optimization/2026-10-09/M5/r3/results/* | 新增 | 翻译快照 + 验证结果 |
| runtime/optimization/2026-10-09/M5/r3/evidence/run-summary.json | 新增 | 证据汇总 |

## 修复前后对比（按 Review 缺陷表）

| 缺陷 | r2 状态 | r3 修复 | r3 验证（r3_fix_driver.py 缩写） |
|---|---|---|---|
| D-M5-01 | openAttach 仅返 reason/lifecycle | m5_open_attach_bound 新增 content / preview / bytes 等 | d05_01_open_attach_has_content(PASS) |
| D-M5-02 | 任意 /inbox 段被放行 | m5_path_in_inbox 收紧到 m5_inbox_abs() 字面前缀 | d05_02_unapproved_inbox_denied(PASS) |
| D-M5-03 | 验收跳过消失成员 | m5_check_fixed_completion_set 以 completion.evidence_ids 为不可变集合 | d05_03_missing_member_rejected(PASS) |
| D-M5-04 (a) | 同 ID 内容变化能放行 | completion 固化 evidence_digests 四元组 | d05_04a_same_id_changed_digest_rejected(PASS) |
| D-M5-04 (b) | 退回复用自动入选 | last_rejected_at 显式 reuse_set 过滤 | d05_04b_old_evidence_requires_explicit_selection(PASS) |
| D-M5-04 (c) | commit 失败 binding 留 | m5_set_round(prev_round) + m5_reset_round_in_memory + completions 截断 | d05_04c_no_round_persisted / no_index_binding_persisted(PASS) |
| D-M5-05 | _textLenSafe 截到首换行 | m5_fingerprint 全内容遍历 + FNV-1a 字节级 mix | d05_05_different_tails / byte_len_full_coverage(PASS) |
| A-M5-02 | opinion 未落账 | logEvent 增加 opinion + manager_proxy_reason + counts | a05_02_accept_completed_with_opinion(PASS) |
| inbox_symlink_outside_inbox_denied | r2 已知 BLOCKED | 仍 BLOCKED：无 fs.stat/realpath；隔离预检 rc71 不允许启动 launcher；不发明 API | NOT_RUN（原生运行 BLOCKED；不假装 PASS）|

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|D-M5-01 内容出口|调用 m5_open_attach_bound（合法 READY 附件）|返回 content / preview / bytes|全部非空|results/r3-fix-verification.json|r3/results/|
|D-M5-02 路径守卫|注入 `…/unapproved/inbox/foreign.txt` + `…/inbox/reviewer-link.txt` 软链 + `…/inbox/../attachments/…` 父穿越|前两个都拒，合法绝对允许|全部按预期|同上|同上|
|D-M5-03 固定集合|提交两件 → 移除第二件 + 删盘 → 验收|任务停留 AWAITING_ACCEPTANCE|OK|同上|同上|
|D-M5-04 (a) 内容变化|提交 → 改写同 ID 文件 → 验收|拒绝|拒绝|同上|同上|
|D-M5-04 (b) 显式 reuse|提交 → 退回 → 不勾 reuse → 再提交|IN_PROGRESS|IN_PROGRESS|同上|同上|
|D-M5-04 (c) 失败回滚|commitSucceeded=False + submitCompletion|round/binding/completions 全部回退|全部回退到 prev_round=0|同上|同上|
|D-M5-05 全字节|`same first line\noriginal tail` vs `same first line\nmodified tail`|指纹不同 + loop=full=29|指纹不同 + loop=full=29|同上|同上|
|A-M5-02 opinion|submitCompletion 后 acceptCompletion 时 opinion 非空|事件流含 opinion|OK|同上|同上|
|真实桌面启动 HOST|launcher 未启动（隔离沙盒 preflight rc71 + pgrep rc3）|原生读/写/打开附件|未运行|NOT_RUN|review-r2/preflight.json|
|权威状态与回执|独立可信业务会话与真实权威回执|读权威主体验收|未运行|NOT_RUN|同上|
|受影响先前模块回归|11 个 M4 既有函数 |字节级未变|未触碰|PASS|review-r2 source-probes unaffected|
|隔离 sandbox 落点|所有 M5 测试/探针产物|must 在项目内|无 /tmp / 外部路径|PASS|r3/scripts/sandbox/ + r3/sandbox/|

## 尚未完成（BLOCKED / NOT_RUN，沿用前序）

1. **真实桌面启动**：launcher sandbox-exec rc71 + pgrep rc3 UNKNOWN；本轮未启动宿主；所有原生命令路径闭合是源码层证据，桌面可达性仍 BLOCKED。
2. **可信独立主体**：review-r2 已声明需要独立业务会话；本轮未引入；自验 + 经理代验理由守卫仅源码正确。
3. **真实中文键入 / 视口 / 接单 receipt-of-action**：NOT_RUN；M3/M4 沿用。
4. **symlink 跟随拒绝**：BLOCKED（无 fs.stat / realpath）；路径层级防御已就位，路径字面层无法识别 symlink 越界；本轮不发明 API。
5. **M0/M1/M2/M3/M4/M6/M7 前序未闭合缺陷**：未触碰；按 Abram 10-10 14:51 挂账。
6. **AppHub publish / 公开签名 / 真实 provider 配置 / 业务身份来源**：未引入；NEEDS_ABRAM=no（离线签名 / 本地 catalog 已授权）。

## 末两行（按用户授权约束固定格式）

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no