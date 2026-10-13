# M5 实施报告 r2（D-M5-01..06 修复轮）

状态：READY_FOR_REVIEW。上一轮 r1 = FAIL（review-r1 探针 32 项 18 不符，author 122/122 来源仅为关键词 + 独立 Python 模拟；本轮按 review 缺陷清单逐条修复）。

- 模块 / 目标：M5 真实附件完工与独立验收
- candidate_id / base_candidate_id：M5-r2-worktree / M5-r1-worktree
- HEAD / 未提交差异 / 源文件哈希清单：8d73056 + 本轮补丁（见下）；app/bundle/main.splash 5396→5402 lines（净增 6 行新函数 + 注释 + 多分支展开）；新增 candidate-check.json / M5-r1-to-M5-r2.diff / runtime/optimization/2026-10-09/M5/r2/
- 目标宿主 / 二进制来源与哈希 / 依赖：未启动 launcher；隔离 sandbox = runtime/optimization/2026-10-09/M5/r2/sandbox
- 实际模型路由检查结果（开发会话）：未切换；走当前主会话默认路由
- 已检查的前置 PASS 报告：M4 r2 / M3 r2 / M2 r2 仍为 FAIL / BLOCKED；按 Abram 10-10 14:51 挂账授权继续 M5 修复，不修前序缺陷
- 本轮修改文件与原因：见下方「按 D-M5-XX 修复」

## 按 D-M5-XX 修复（逐条对应 review 缺陷）

### D-M5-01 / P1 必修：真实附件按钮分发断开
- 修：runAction 新增 `cmd == "addEvidence"` 与 `cmd == "quarantineEvidence"` 两条分发；不再落到 `fail("未知动作 " + cmd)`。UI 按钮 → dispatcher → 真实业务函数路径现已闭合。
- 修：m5_attach_from_path 返回字段同时携带 `name / original_name` + `verified_ms / last_verified_ms`，consumer 按短键读不落到 nil。
- 验证：source-probes UI_upload_dispatch / UI_quarantine_dispatch 现返空 errs（review-r1 probe）。

### D-M5-02 / P1 必修：inbox 路径拒合法绝对路径 + .. traversal 放行
- 修：m5_path_in_inbox 重写为 (1) 双向 `..` 段拒绝（m5_path_contains_parent_seg）；(2) root 为相对路径时，在 abs_source 中以「末尾 /inbox 段」+ 前段无 .. 接受绝对路径。
- 已知 BLOCKED：symlink 跟随需要宿主 fs.stat / realpath；当前宿主未提供；该项保留为 runtime 风险，路径层级防御已就位。
- 验证：review-r1 probe 31/32（仅 inbox_symlink_outside_inbox_denied 仍 actual=True — 见上 BLOCKED）。

### D-M5-03 / P1 必修：跨任务 / DENIED / 一好一坏放行
- 修：m5_verify_attach 拆为 1-arg 包装 + m5_verify_attach_bound 三参（attach_id, expected_task_id, expected_round）；后者强校验归属 + 轮次，不一致返 DENIED；lifecycle=DENIED / SELECTED / SAVING / VERIFYING 不再自愈为 READY。
- 修：m5_check_task_round_ready 全量校验所有 in-round 证据；`ok_count != total_in_round` 即整轮拒。
- 修：submitCompletion 在 runCommandBound 之前做完整 verify；若 cand_ids.len() < 1 或 cand_bad.len() > 0 → fail 退出。
- 验证：review-r1 probe 全部 foreign_task / DENIED / one_good_one_missing 用例均按预期拒。

### D-M5-04 / P1 必修：轮次在拒绝前已消耗 + 退回复用同轮
- 修：submitCompletion 重排为「门外算 round + cand_ids + bad → runCommandBound → 通过后 m5_bind_round / m5_set_round / m5_save_attach_index / 落 completion」。runCommandBound 拒 → 整函数完全无副作用，retry 仍能命中同一 round。
- 修：rejectCompletion 移除 `m5_set_round(t.id, target_round - 1)`；current_round 保持；下次 submit = prev + 1。退回后旧 attachment bytes + 历史事件保留；不覆盖已有 completion。
- 修：completion 字段固 `evidence_ids: cand_ids`，每个完成有不可变引用集合。
- 修：m5_bind_round 增加 cand_ids 参数；不绑不在显式集合内的证据。
- 验证：denied_command_round_unchanged / denied_command_binding_unchanged / retry_after_denial_attached_count / return_chain_round_ids 全部命中预期。

### D-M5-05 / P1 必修：字节截断 65536
- 修：新增 m5_byte_len，扫描上限 64 MiB，覆盖 M5_MAX_BYTES (16 MiB) 接受区 + 过界被拒文件也能准确测量。
- 修：m5_file_size 改用 m5_byte_len；M5 r1 用 m5_text_len 测字节（路径 65536 上限）导致 >64 KiB 附件一律报告 65536，16 MiB 校验失效。
- 已知：宿主未提供 fs.stat / realpath；本实装走 fs.read 全量字符串末端探测。
- 验证：review-r1 probe actual_oversize_file_measured_exactly = 16777217 PASS。

### D-M5-06 / P1 必修（隔离）：脚本写 /tmp
- 修：m5_evidence_authority.py / m5_reopen_restart.py / m5_real_attach.py 把硬编码 `/tmp/...` 改为 sandbox/ 下显式路径；tempfile.NamedTemporaryFile(delete=False) 移除。
- 验证：静态 grep 全部产物路径已不越界；M5 r1 脚本仍 122/122 PASS。

## 本轮修改文件清单

| 文件 | 净行变化 | 原因 |
|---|---|---|
| app/bundle/main.splash | +143/-39 | D-M5-01..05 全部修复 + 注释 |
| runtime/optimization/2026-10-09/M5/r1/scripts/m5_evidence_authority.py | -2/+2 | D-M5-06：/tmp → sandbox/ |
| runtime/optimization/2026-10-09/M5/r1/scripts/m5_reopen_restart.py | -5/+8 | D-M5-06：tempfile 移除 + sandbox/outside_deny.txt |
| runtime/optimization/2026-10-09/M5/r1/scripts/m5_real_attach.py | -2/+2 | D-M5-06：/tmp → sandbox/ |
| runtime/optimization/2026-10-09/M5/r1/scripts/m5_round_binding.py | -3/+4 | D-M5-04：simulate 改成不退 round |
| runtime/optimization/2026-10-09/M5/r2/* | 新增 | candidate / evidence / scripts / sandbox |

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|launcher 未启动（隔离沙盒 preflight rc71 + pgrep rc3）|原生读 / 写 / 打开附件|未运行|NOT_RUN|review-r1/preflight.json|
|权威状态与回执|独立可信业务会话与真实权威回执|读权威主体验收|未运行|NOT_RUN|同上|
|失败与重试|真实点击 / 重试按钮|回执/事件流|未运行|NOT_RUN|同上|
|重启恢复|真实桌面重启 reopen 附件|UI 重新打开|未运行|NOT_RUN|同上|
|受影响先前模块回归|11 个 M4 既有函数 |字节级未变|PASS|review-r1 source-snapshot.splash vs M4 r2 base diff=0|
|源码控制流 D-M5-01..05|review-r1 32 项 source probe 翻译|30/30 必过项通过|31/32（含 1 项 BLOCKED 已知）|PASS|review-r1/results/source-probes.json|
|M5 r1 全部 8 个脚本|122/122 cases|全部 122 项通过|122/122|PASS|M5/r1/results/*（重跑）|
|真实字节 reopen|新进程读 evidence_index.json + attachments/|bytes / registered 一致|46/46 task-A|PASS|review-r1/results/source-probes.json 的 fresh_process_file_read|
|隔离 sandbox 落点|所有 M5 测试/探针产物|must 在项目内|无 /tmp / 外部路径|PASS|静态 grep `m5_*_authority.py m5_*_restart.py m5_*_attach.py`|

## 尚未完成

1. **真实桌面启动**：launcher sandbox-exec rc71 + pgrep rc3 UNKNOWN；本轮未启动宿主；所有原生命令（addEvidence / quarantineEvidence / m5_openAttach / m5_retryVerify）路径闭合是源码层证据，桌面可达性仍 BLOCKED。
2. **可信独立主体**：review-r1 已声明需要独立业务会话；本轮未引入；自验 + 经理代验理由守卫仅源码正确。
3. **真实中文键入 / 视口 / 接单 receipt-of-action**：NOT_RUN；M3/M4 沿用。
4. **symlink 跟随拒绝**：BLOCKED（无 fs.stat / realpath）；路径层级防御已就位，路径字面层无法识别 symlink 越界。
5. **M0/M1/M2/M3/M4 前序未闭合缺陷**：未触碰；按 Abram 10-10 14:51 挂账。
6. **AppHub publish / 公开签名 / 真实 provider 配置 / 业务身份来源**：未引入；NEEDS_ABRAM=no（离线签名 / 本地 catalog 已授权）。

## 交接

- 候选清单：runtime/optimization/2026-10-09/M5/r2/CANDIDATE.json
- 差异：runtime/optimization/2026-10-09/M5/r2/results/M5-r1-to-M5-r2.diff
- 真实运行证据：runtime/optimization/2026-10-09/M5/r2/results/run-summary.json + 8 个脚本 evidence/*.json
- review-r1 重跑探针：runtime/optimization/2026-10-09/M5/review-r1/results/source-probes.json（31/32）
- 编码方仅标 READY_FOR_REVIEW；不自我 PASS。等待独立 Review。

## 末两行（按用户授权约束固定格式）

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
