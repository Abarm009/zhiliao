# B 版第三轮独立复验 · 2026-10-06

审查摘要：`1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96`；version `0.1.0-b`。结论：旧假 READY 阻断通过；旧事件完整备份但未迁移恢复；发布文档仍不一致，不能标完整原生验收 PASS。置信度高。

本轮使用初次独立 review 的真实 IN_PROGRESS 旧快照，在新隔离目录运行当前 bundle。未改业务代码、原运行数据或 A 版材料，未提交/推送。

## 实测通过

- hub check --allow-unsigned PASS（unsigned warning）；ZIP 12 个文件逐字节对应当前 bundle；git diff --check PASS；宿主日志未见 [E]。
- 旧 bytes=1024、sha=demo-sha、ready=true 的演示证据加载后 scrub 为 bytes=0、sha为空、ready=false、demo=true。
- 真实点击提交完工，任务保持 IN_PROGRESS，状态条拒绝：完工前必须至少有一份可读证据。此前旧假证据绕过的复现已关闭。
- 旧9条 JSONL 已备份至 events.jsonl.legacy.<ts>.bak；备份字节与输入原文件完全相等。

## 尚需收尾

1. **P1 发布文档未统一**：根 README:18/23/36/38/41 仍有“最新”、旧 B 摘要 1ac7bb...、“幂等验证通过”、完整闭环；B 提交 README:3/41/70/80 仍有完整闭环、错误 A/B 摘要和 ready:true。HUB_ISSUE:28/34 用旧摘要，49 用新摘要；scan Q1 仍宣称截图覆盖全闭环。VERIFICATION:150 残留5503136c。新增末尾更正不替代删除前文错误。必须全文统一，旧完成截图标明修前演示版本，不作为当前验收证据。
2. **P1 旧事件只有备份，未迁移恢复**：加载后 EVENT_LOG=0，events.jsonl=[]；不是9→9恢复。main.splash:230 忽略备份写失败，296-297 无条件覆盖原事件/回执，失败时仍可能丢原文件。应在备份确认成功后才允许转换，或解析失败保留原文件并阻止覆盖。main.splash:286 又将明确备份提示改为 DEBUG: events raw is nil；用户看到 DEBUG，没看到需要恢复的提示。不得标旧格式恢复 PASS。
3. **P1 清理条件过宽（代码确认）**：main.splash:249 将所有 bytes==1024 的证据当演示并清空 bytes/sha，即使名称和摘要不是 demo。应按明确演示标识识别，不能仅凭1024字节判假。
4. 幂等稳定 key 的动态验证、真实附件与模型、最新宿主兼容及全部38/12验收仍未完成。只承认恢复分支和已实测动作。

## 最快收尾范围

保持当前已通过的假证据阻断；收窄清理识别；备份失败不覆盖原文件，去除 DEBUG 并保留清晰迁移提示；统一 README/Issue/VERIFICATION 摘要和候选进展口径，重新 stamp/check/打包并核对 ZIP。无需为提交候选进展声称完整闭环通过。

运行证据：runtime/recheck-native-b-final-20261006/final-results.json；02-completion-blocked.png；original-events.jsonl；data/octosense-repair/events.jsonl.legacy.*.bak。测试窗口保留。
