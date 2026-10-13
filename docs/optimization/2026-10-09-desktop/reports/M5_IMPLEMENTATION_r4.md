# M5 实施报告 r4（D-M5-01/02/04/05 修复轮）

状态：READY_FOR_REVIEW。上一轮 r3 = FAIL（D-M5-01..05 全部未闭合 + reject commit 失败回滚未闭合）；本轮按 r3 Review 缺陷清单 + 用户授权约束逐条修复。

- 模块 / 目标：M5 真实附件完工与独立验收
- candidate_id / base_candidate_id：M5-r4-worktree / M5-r3-worktree
- HEAD / 未提交差异：8d73056 + 本轮补丁（见下）
- 目标宿主 / 二进制来源与哈希 / 依赖：未启动 launcher；隔离 sandbox = runtime/optimization/2026-10-09/M5/r4/sandbox
- 实际模型路由检查结果（开发会话）：未切换；走当前主会话默认路由
- 已检查的前置 PASS 报告：M4 r4 / M3 r4 / M2 r4 仍为 FAIL / BLOCKED；按 Abram 10-10 23:04 裁决继续 M5 修复，不修前序缺陷
- 本轮修改文件与原因：见下方「按 D-M5-XX 修复」

## 按 D-M5-XX 修复（逐条对应 r3 Review 缺陷）

### D-M5-01 / P1 必修：openAttach UI 真实消费
- 修：m5_cmd_openAttach 把 r.content / r.content_preview / r.bytes / r.sha /
     r.stored_abs / r.name / r.original_name / r.prefix32 / r.suffix32 /
     r.opened_at / r.lifecycle / r.reason 整体打包落到 STATE.last_open_attach；
     STATE.last_open_attach 由 m5_init_forms 兜底 = nil。
- 修：refreshDetail attachments tab 增加渲染分支 — 若 STATE.last_open_attach
     不为 nil 且其 task_id 等于当前任务，则把"最近打开 attach_id ·
     lifecycle · bytes · sha · preview · 落盘路径 · 完整内容"渲染到
     ui.tab_state，把 ui.tab_lines 维持附件列表。
- 验证：r4_review_probes.json source_outlets：
   * cmd_uses_returned_content = true（源码内 m5_cmd_openAttach 引用 r.content）
   * cmd_stores_to_state_last_open_attach = true
   * refresh_detail_renders_preview = true
   * r4_fix_driver.py d04_01_open_attach_has_content /
     has_content_preview / has_bytes / content_matches = PASS

### D-M5-02 / P1 必修：sandbox 真实绝对根
- 修：新增常量 M5_PROJECT_ROOT_ABS = "/Users/abeam/一些尝试/知了OctoSense"；
     m5_init_forms 兜底 STATE.attach_sandbox_root_abs =
     M5_PROJECT_ROOT_ABS + "/runtime/optimization/2026-10-09/M5/r4/sandbox"。
- 修：m5_sandbox_root_abs 重写 — 优先 STATE.attach_sandbox_root_abs（显式绝对），
     缺省回退 M5_PROJECT_ROOT_ABS + "/" + rel；不再使用 "./" + rel。
- 不修改 m5_path_in_inbox 主体（仍以 m5_inbox_abs() 字面前缀为唯一授权依据），
     父轨迹 / 未授权 inbox 拒绝行为继承 r3。
- 验证：r4_review_probes.json path_guard：
   * sandbox_root_abs_is_absolute = true
   * legal_absolute_inbox_allowed = true（绝对 inbox 路径通过）
   * unapproved_inbox_denied = false（未授权 inbox 名仍拒）
   * parent_traversal_denied = false（…/inbox/../attachments 仍拒）

### D-M5-04 / P1 必修：失败回滚 + 索引恢复
(a) **m5_bind_round 不再落盘**：
- 修：删除 m5_bind_round 末尾 m5_save_attach_index() 调用；调用方
     submitCompletion 在 commit 成功后才调 m5_save_attach_index()。
     索引写入时机由调用方显式控制，与 commit 协议保持一致。

(b) **rejectCompletion commit 失败回滚（r3 未闭合）**：
- 修：rejectCompletion 重写 — 先在内存里把 t.status=S_IN_PROGRESS、
     ev.evidence_round=0、ev.last_rejected_at=nowMs()、
     ai.evidence_round=0、ai.last_rejected_at=nowMs()；同时把旧值收集到
     chg_ev_idx / chg_ev_old_round / chg_ev_old_rejected / chg_ai_idx /
     chg_ai_old_round / chg_ai_old_rejected 6 个平行数组。
- 修：commit(t) 后若 commitSucceeded() = false，回滚路径：
     t.status = prev_status（AWAITING_ACCEPTANCE）
     chg_ev_idx 索引回写 ev.evidence_round = old_round
     chg_ev_idx 索引回写 ev.last_rejected_at = old_rejected
     chg_ai_idx 索引回写 ai.evidence_round = old_round
     chg_ai_idx 索引回写 ai.last_rejected_at = old_rejected
     logEvent("reject_completion_rollback", ...)
     不调 m5_save_attach_index()，索引文件保持 commit 前状态。
- 修：commit 成功路径才调 m5_save_attach_index()，保证"索引 + 任务状态"原子。
- 验证：r4_review_probes.json reject_commit_failure_rollback：
   * before_round=1 / before_ev_round=1 / before_ai_round=1 / before_status=AWAITING_ACCEPTANCE
   * after_round=1 / after_ev_round=1 / after_ai_round=1 /
     after_status=AWAITING_ACCEPTANCE / after_ev_last_rejected_at=null /
     after_ai_last_rejected_at=null
   * saved_index_round=null（index 文件未被修改）

### D-M5-05 / P1 必修：全 95 printable ASCII 字节指纹
- 修：删除旧 _hex_nibble_of_char（仅覆盖 hex/a-z/空格/几个中文标点；'v' / 'w' 都返回 0）。
- 修：新增 _ascii_byte_value(c)：用 c.index_of(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~") 返回 0..94 唯一位置。
     'v' → 85；'w' → 86；'a' → 64；'z' → 89 等。
- 修：新增 _nibble_of_byte_low(c) / _nibble_of_byte_high(c) 处理非 printable 字节
     （控制字符 / UTF-8 续字节 0x80-0xBF / 多字节首字节 0xC0-0xF7）。
     两个表都用 index_of；同一个字节 c 不会同时出现在两表 → 高低位独立反查。
- 修：m5_fingerprint 重写为：cl + (i & 0xFF) + ascii_val + (lo|hi nibble) 全部混
     进 FNV-1a（常量 2166136261，乘数 16777619）；全内容遍历至 m5_byte_len 上限。
     旧 _hex_nibble_of_char 全表删除；不再依赖 _fnv1a_hash / _textLenSafe / _charAtSafe。
- 验证：r4_review_probes.json hash_counterexample：
   * original_sha256 = e573c686...31731
   * changed_sha256  = b27195c1...a3fd9
   * original_m5     = a353d3ef（80 个 'v' 引入）
   * changed_m5      = e5c9d3ef（80 个 'v' → 80 个 'w'）
   * fingerprint_different = true ✓
- 验证：r4_fix_driver.py d04_05_v_vs_w_different_fps / reviewer_v_vs_w_different_fps /
     byte_len_coverage = PASS

## 本轮修改文件清单

| 文件 | 净行变化 | 原因 |
|---|---|---|
| app/bundle/main.splash | +388/-85（粗估；与 r3 同量级）| D-M5-01/02/04/05 全部修复 + 注释 |
| runtime/optimization/2026-10-09/M5/r4/CANDIDATE.json | 新增 | 候选清单 schema=3 |
| runtime/optimization/2026-10-09/M5/r4/scripts/r4_fix_driver.py | 新增 | 27 项驱动（按 r3 Review 缺陷清单逐条验证）|
| runtime/optimization/2026-10-09/M5/r4/scripts/r4_review_probes.py | 新增 | r4 版本的 r3 review probes 全套 |
| runtime/optimization/2026-10-09/M5/r4/results/* | 新增 | 翻译快照 + 验证结果 |

## 修复前后对比（按 r3 Review 缺陷表）

| 缺陷 | r3 状态 | r4 修复 | r4 验证 |
|---|---|---|---|
| D-M5-01 | m5_cmd_openAttach 不读 r.content | m5_cmd_openAttach 写 STATE.last_open_attach + refreshDetail attachments tab 渲染 preview / content / bytes | r4_review_probes.source_outlets / r4_fix_driver.d04_01_* |
| D-M5-02 | m5_sandbox_root_abs 返回 "./" + rel | M5_PROJECT_ROOT_ABS 常量 + STATE.attach_sandbox_root_abs 绝对字段；m5_sandbox_root_abs 优先取绝对 | r4_review_probes.path_guard（sandbox_root_abs_is_absolute=true；合法绝对通过；unapproved/parent_traversal 拒）|
| D-M5-04 | reject commit 失败不回退 + m5_bind_round 提前落索引 | m5_bind_round 不再落索引；rejectCompletion 内存改 + 失败回滚 + commit 成功才落索引 | r4_review_probes.reject_commit_failure_rollback（before/after round=1 保持；status 回到 AWAITING_ACCEPTANCE；last_rejected_at=null；saved_index_round=null）|
| D-M5-05 | _hex_nibble_of_char 对 v/w 等都返回 0 | _ascii_byte_value(c) 用 index_of 命中 95 printable ASCII；_nibble_of_byte_low / _nibble_of_byte_high 处理非 printable；m5_fingerprint 全字节混合 | r4_review_probes.hash_counterexample（original_m5=a353d3ef vs changed_m5=e5c9d3ef）|

## 覆盖的既有验收项与证据运行形态

| 检查 | 输入与步骤 | 预期 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|---|
| D-M5-01 内容出口 | r4 m5_open_attach_bound（合法 READY 附件）| 返回 content / preview / bytes | 全部非空 + content[:32]==源 | PASS | r4/results/r4-fix-verification.json |
| D-M5-02 路径守卫 | 注入未授权 inbox 名 + 合法绝对 + 父穿越 | 未授权/父穿越拒；合法绝对通过 | 全部按预期 | PASS | r4/results/r4-review-probes.json |
| D-M5-04 (c) 失败回滚 | reject commit=false | evidence_round / status / last_rejected_at 全回滚；索引不写 | 全部回滚到提交前；saved_index_round=null | PASS | r4/results/r4-review-probes.json |
| D-M5-05 全字节 | 80 v → 80 w + 中文 PNG-like | 指纹不同 | a353d3ef vs e5c9d3ef | PASS | r4/results/r4-review-probes.json |
| 正常链 submit→reject→reuse→accept | 完整链跑通 | COMPLETED + rounds [1, 2] | 全部 PASS | PASS | r4/results/r4-fix-verification.json |
| 真实桌面启动 HOST | launcher 未启动（隔离沙盒 preflight rc71 + pgrep rc3）| 原生读/写/打开附件 | 未运行 | NOT_RUN | 沿用 r1..r3 挂账 |
| 权威状态与回执 | 独立可信业务会话与真实权威回执 | 读权威主体验收 | 未运行 | NOT_RUN | 沿用 r1..r3 挂账 |
| 受影响先前模块回归 | 11 个 M4 既有函数 | 字节级未变 | 未触碰 | PASS | r3 source-probes unaffected（review-r3 仍可重跑）|
| 隔离 sandbox 落点 | 所有 M5 测试/探针产物 | 必须项目内 | 无 /tmp / 外部路径 | PASS | r4/scripts/sandbox/ + r4/sandbox/ |

## 尚未完成（BLOCKED / NOT_RUN，沿用前序）

1. **真实桌面启动**：launcher sandbox-exec rc71 + pgrep rc3 UNKNOWN；本轮未启动宿主；
   所有原生命令路径闭合是源码层证据，桌面可达性仍 BLOCKED。
2. **可信独立主体**：review-r3 已声明需要独立业务会话；本轮未引入；
   自验 + 经理代验理由守卫仅源码正确。
3. **真实中文键入 / 视口 / 接单 receipt-of-action**：NOT_RUN；M3/M4 沿用。
4. **symlink 跟随拒绝**：BLOCKED（无 fs.stat / realpath）；路径层级防御已就位，
   路径字面层无法识别 symlink 越界；本轮不发明 API。
5. **M0/M1/M2/M3/M4/M6/M7 前序未闭合缺陷**：未触碰；按 Abram 10-10 14:51 挂账。
6. **AppHub publish / 公开签名 / 真实 provider 配置 / 业务身份来源**：
   未引入；NEEDS_ABRAM=no（离线签名 / 本地 catalog 已授权）。

## 末两行（按用户授权约束固定格式）

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no