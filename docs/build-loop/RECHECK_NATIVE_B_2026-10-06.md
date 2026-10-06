# B 版修复后独立复验 · 2026-10-06

结论：能启动；新建数据下部分修复有效；旧数据升级仍 FAIL，完整原生证据闭环及最新版兼容未通过。置信度高。审查 bundle digest `ab69db47a2888dba9d5303a68c2f791097c0249ec9a08c56e328fec56bc89b49`，版本 `0.1.0-b`。只新增隔离运行证据和本报告，未改业务代码或推送。

## 已实际复验

- hub check --allow-unsigned PASS；ZIP 12 个文件逐字节等于当前 app/bundle；git diff --check PASS，宿主日志未见 [E]。
- 全新隔离目录真实点击 DRAFT→OPEN→ACCEPTED→SCHEDULED。报修人二显示无可见任务，tick 后仍保持空态。
- 关闭后使用同一数据目录重启：任务、6 条事件、6 条回执与重启前完全相同，UI 显示事件 6 条。
- 预约开工首次连续等待/重试未成功，重启后第一次仍拒绝，稍后重试成功到 IN_PROGRESS。没有手工修改此新建数据；原因未定位，不可把时间调度推测写成确定根因。
- 真实点击记录处置、上传证据：写入 bytes=0、sha为空、ready=false、demo=true；提交完工被拒，任务仍 IN_PROGRESS。新数据上的 B-R01 修复有效。
- 未重新跑全部 38/12 验收，未证明最新宿主兼容，未调用真实模型。

## 尚未关闭的问题

### 1. P0：旧版假 READY 附件仍被正式完工接受（运行复现）

main.splash:144 的 readyCount 只检查 e.ready；load 没有清理旧版演示证据。

使用上轮独立 review 的实际“上传证据”快照，在第二个隔离目录启动修复版（未改证据字段）：原证据 bytes=1024、sha=demo-sha、ready=true，没有实际文件。界面仍显示证据 1 件；真实点击提交完工，任务 IN_PROGRESS→AWAITING_ACCEPTANCE。新 addEvidence 的修复不会修正已经持久化的伪证据。

建议：加载时将旧版 demo-sha/演示占位标记为非 READY，并在 readyCount/正式提交边界排除演示附件，校验真实可读文件与摘要。不得把修前旧数据直接作为修后完成证据。

### 2. P1：旧 JSONL 不兼容，新事件会覆盖旧事件（运行复现）

main.splash:202-207 改为整体数组覆盖写，但 load:225-228 仍整文件 parse_json，不兼容旧版逐行 JSONL。

同一旧快照有 9 条事件。加载修复版后 UI 显示事件 0；提交完工新增事件后，events.jsonl 被覆盖为仅 1 条数组，旧 9 条不再保留在该文件中。此问题仅发生于升级旧格式；全新数组格式的重启恢复通过。

建议：兼容逐行 JSONL 的加载或显式迁移；解析失败时保留原文件并阻止覆盖，迁移前备份。验证 9 条旧事件加载和新增后达到 10 条。

### 3. P1：发布文档仍保留互相矛盾的旧结论

- 根 README:23/38 与 submission/2026-10-06-native/README:41/70 仍写旧 B digest 1ac7bb...，实际 ab69db...。
- 两份 README 仍有“最新”“完整闭环通过”；修后真实附件上传未接通，不能走正式完工。
- B README:80 仍称 addEvidence 写 ready:true，与当前源码矛盾；前面写全闭环，末尾又限定仅到 SCHEDULED/合成任务验证。
- HUB_ISSUE:28/34 使用旧摘要，49 使用新摘要，同一草稿不一致。
- VERIFICATION:85-86 称幂等 UI 验证沿用 review；上轮报告明确没有动态复用 key 验证，因此不能引用为通过证据。VERIFICATION:145 另残留 5503136c 摘要。
- 打包的 b05/b06 完成截图源于修前允许假证据的版本，不能用作修后完整闭环通过证据。

建议：统一以 manifest 当前摘要为准；发布口径写“固定旧宿主原生候选；已验证报修/接单/预约/处置及非 READY 完工阻断；真实附件、模型和最新版宿主兼容待完成”。

### 4. 幂等仅部分关闭（代码确认，未动态复用 key）

hit/conflict 分支恢复，但 runCommand 在查回执前先做 sourceOk，状态变化后重放可能先被源状态拒绝；各业务 handler 每次重建 LAST_KEY，没有稳定输入 key 的重复请求接口。不能把分支恢复等同于端到端幂等验收通过。建议用同 key 同参数、同 key 不同参数定向验证，重放查询应先于变化后的源状态判断。

## 证据目录

- runtime/recheck-native-b-20261006：全新数据真实点击、重启及证据阻断；06-completion-blocked.png。
- runtime/recheck-native-b-legacy-20261006：使用上轮真实数据快照验证升级；legacy-results.json、02-old-demo-completion.png。
- 原始 bundle、A 版材料和其他会话运行数据未改。全新数据测试窗口保留；旧数据负向测试实例已退出。

优先补旧假证据隔离和事件格式迁移，再统一提交文档。可以展示候选进展，不能标完整原生验收 PASS。
