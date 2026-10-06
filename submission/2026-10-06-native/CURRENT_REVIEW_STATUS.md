# 当前 GitHub 候选状态

本次上传的是待修复的 B 版原生候选，不是完整验收通过或 App Hub 已收录版本。

- manifest.version：`0.1.0-b`；bundle_blake3：`e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`。
- 上轮独立复验已确认：旧假 READY 被清理，完工被拒绝；旧9条事件有逐字节一致的备份；hub check PASS；ZIP与源码一致。
- 最新一轮修复已随源码与 ZIP 更新上传。包检查通过、ZIP逐字节匹配源码；本轮没有执行完整业务独立复验。此前报告中的缺陷属于上次审查快照，是否关闭以新一轮复验为准。
- 动态幂等、真实附件、真实模型、最新版宿主兼容以及全部38/12验收未通过或未验证。
- README、Issue草稿与旧截图中尚存历史/过时结论，以本文件和最新独立复验报告为准。旧 COMPLETED 截图不得作为当前完整闭环通过证据。
- 本次仅发布源码和材料；没有创建 App Hub Issue、取得官方审核回执或商店收录。

独立报告：[第三轮复验](../../docs/build-loop/RECHECK_NATIVE_B_FINAL_2026-10-06.md)。

公开证据：[旧假证据被阻断](screenshots/15-independent-legacy-blocked.png)、[独立点击结果](check/independent-final-results.json)、[旧9条事件原始快照](check/independent-original-events.jsonl)。
