# M2 实施报告 r9

**轮次性质**：修复轮，针对 `M2_REVIEW_r10.md`（FAIL）缺陷清单逐项修复，只修清单项。
**候选**：`M2-r9-worktree`；base=`M2-r8-worktree`（r10 实际受审运输候选，冻结 main SHA a9acd344…）。
**当前工作树 main.splash**：642733 B / SHA-256 `a5bca2f3e876535a8a418b032acc08f604cb8fe57c6f845f6cf3a8a07a5f27ac`。
**注意**：r10 审查时工作树为 0fb141f9…（551000 B），本轮开始时工作树已含其他模块/前序修订（现 642733 B）；他人改动全部保留、未 reset/stash/覆盖。差异工件 `runtime/optimization/2026-10-09/M2/r9/main.splash.diff-a9-to-r9.patch`（a9 冻结版 → 当前候选，5006 行，含他人改动）。
**新签名包 digest**：`ee14dbb9f3fd532c7b4cf2128249ca688bb6d5384f3427f93a4f7fecb078b562`（离线签名，授权 A 范围内；私钥已删除，证据 `r9/native-prep/offline-store-evidence.json`，private_keys_remaining=[]）。

## 逐条修复（按 r10 原缺陷编号）

### D-M2-01 输入/意图恢复（部分关闭 → 本轮补齐持久侧）

- r9 前工作树已有 `_VIEW_STATE_OK` 门控（loadViewState 失败不用默认 STATE 覆盖原文，saveState 拒写未恢复的 state.json）。本轮补齐其配套：意图记录持久化（见 D-M2-02），pending_input 白名单并入逻辑不变。
- 原生验证：REQUEST_build_r9 `cold_login_view` 场景 seed 预置非空中文 pending_input + confirm_intent + action_keys_by_task，冷开后核盘/UI（待驱动执行）。

### D-M2-02 原 key/不可变意图（本轮新修）

- `STATE.confirm_intent` 新增持久不可变意图记录 `{id, actor, project, command, key, payload, phase, at}`（main.splash STATE 默认声明 + `loadViewState` 白名单恢复，仅接受对象形态；actor 字段只用于归属比对，**不**作为授权来源/不恢复会话）。
- `createDraftFromPanel`：意图归属校验 —— 持久意图的 actor/project 与当前可信上下文不符即轮换为新独立意图（切账号/项目 = 新动作，不沿用旧 key）；首次操作即持久 payload 快照与稳定 key；冷开恢复后面板为空时按原不可变 payload 对账（重试路径），面板有内容时以当前内容为准（意图存续期间改内容 = 同 key 异 payload → 对已 final 原动作 conflict）。
- `confirmDraftModelBound` 尾部权威完成后同时清空 `confirm_intent_id` 与 `confirm_intent`（轮换）。

### D-M2-03 关联提交（本轮新修 pending 保存返回消费）

- `recordReceipt`：saveReceipts 返回 false 时内存也不留该 pending（截断 RECEIPTS），返回 false；唯一调用方（旧 runner 绑定路径）收到 false 即中止，不进入业务写。
- `createDraftFromPanel`：pending 回执先于 TASKS.push/落盘写入；`saveReceipts` 失败 → 截断内存回执、释放锁、fail() 拒绝、返回 nil —— 任务与磁盘均未变更，不再忽略保存返回继续提交。
- 既有保留：事件落盘失败降级 needs_verify、commitBound 锁/版本/冲突提交点复核、commit 失败盘读回替换内存。

### D-M2-04 原动作证明

- 本轮未改源码分支（r8 已有 version+1 + after 事实全等才 final_recovered、三字段不符保持未知、rid 精确匹配）。真实认证恢复动态链仍 NOT_RUN（可信输入通道缺口，见挂账）。

### D-M2-05 原子竞争边界

- 无宿主原子原语（HOST_PRIMITIVE_BLOCKED 依旧），本轮不改代码、不以串行测试代签；保持 BLOCKED 技术缺口如实记录：需要宿主原子锁/CAS 与 harness 同权威盘双上下文同步竞争能力。

### D-M2-07 历史迁移/备份/恢复（本轮主修）

- 新增 `_m2_history_record_ok`（记录=≥1 字段对象）、`_m2_write_diag_file`（诊断文件写入+读回核实后才可命名）、`_m2_mark_dirty`（置脏同步记录真实诊断出口）。
- `loadJsonlLines`：读取失败（目录/权限）→ 冻结写 + 真实人工出口，不命名不存在的 bad_lines；真数组逐项过门禁，含非法元素（字符串/null/嵌套数组/空对象）→ 原文件保留 + 诊断文件核实 + 写冻结 + 合法项仍可供查询；合法 `[]` 原样不动。
- `_m2_parseRecordsLoose`：数组逐项门禁，主/bak 共用同一判据。
- `migrateJsonlLegacy`：主/bak 读取失败不抛穿 boot；含非法元素的数组不当当前格式接受（冻结+诊断）；skipped>0 与 bak 兜底恢复路径的诊断文件均写入+读回核实；**已有合法非空 .legacy.bak 不盲覆** —— 本次迁移原文另存 `.legacy2.bak` 并读回核实后才继续；备份写+读回任一步失败回滚保留原文件。
- `saveReceipts`/`saveEvents` 冻结提示只命名真实存在的诊断文件（DIAG=="NONE" 时给人工检查出口）。
- `load()`：迁移错误优先显示 —— 有任一历史冻结时不用后续无关成功提示覆盖错误状态。

### D-M2-06

- 白名单根因保持关闭，未动。

## 验证（本轮已执行）

- vendored parser：`cd octoscript && cargo test -p octoscript-core --test m2_r7_bundle_parse` → **PASS**（全部改动后重跑，2026-10-13 00:1x +08:00）。
- 离线候选准备：`runtime/optimization/2026-10-09/M2/r9/prepare_build_r9.py` 已执行 —— snapshot-start.json、签名 mirror、install_staged 本地安装核验（LOCAL_INSTALL_VERIFIED，main 同字节断言通过）、13 个场景 seed、seed-manifest.json；私钥已删除（证据内 private_keys_remaining=[]）。
- harness 冷启动请求：`runtime/optimization/2026-10-09/M2/native/REQUEST_build_r9.json`（13 场景：r8 七场景回归 + r10 六个新回归场景 empty_array_stays / invalid_array_elements / mixed_bareword_with_bak / missing_primary_ndjson_bak / corrupt_primary_valid_bak_events / unreadable_events_directory）。**由驱动在沙箱外执行**，证据将落 `M2/native-runs/build_*_REQUEST_build_r9/`；本报告提交时原生结果尚未产生，不预判。

## 尚未完成 / 如实标记

- 原生 13 场结果：待驱动执行，未执行不标 PASS。
- D-M2-05 真原子竞争：BLOCKED（宿主原语 + harness 同盘双上下文能力缺口）。
- 认证业务创建/重试/冲突/权限矩阵、逐提交写点故障注入、连续同 Store 重开：NOT_RUN（可信输入通道/写点注入控制缺口，harness 白名单不覆盖）。
- 真实模型 provider：延期缺口（Abram 已裁决，M3 到期），本模块 0 次真实模型请求。
- G0-B 双主体：登录链路已可由 ui_actions 驱动，本轮未请求（范围限定 r10 清单）。

## 交接

- 候选：M2-r9-worktree（main SHA a5bca2f3…，包 digest ee14dbb9…）。
- 差异：`M2/r9/main.splash.diff-a9-to-r9.patch`；快照 `M2/r9/native-prep/snapshot-start.json`；seed 清单 `seed-manifest.json`。
- 请求：`M2/native/REQUEST_build_r9.json`（expect_bundle_digest=ee14dbb9…）。
- GATES：M2 → READY_FOR_REVIEW。
