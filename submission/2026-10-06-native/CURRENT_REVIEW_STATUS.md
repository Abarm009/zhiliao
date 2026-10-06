# 当前 GitHub 候选状态

本次上传的是待修复的 B 版原生候选，不是完整验收通过或 App Hub 已收录版本。

- manifest.version：`0.1.0-b`；bundle_blake3：`1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96`。
- 独立复验已确认：旧假 READY 被清理，完工被拒绝；旧9条事件有逐字节一致的备份；hub check PASS；ZIP与源码一致。
- 待第三轮收尾：旧事件未恢复到活动日志、备份失败覆盖保护、1024字节清理条件过宽、发布文档旧结论与摘要统一。
- 动态幂等、真实附件、真实模型、最新版宿主兼容以及全部38/12验收未通过或未验证。
- README、Issue草稿与旧截图中尚存历史/过时结论，以本文件和最新独立复验报告为准。旧 COMPLETED 截图不得作为当前完整闭环通过证据。
- 本次仅发布源码和材料；没有创建 App Hub Issue、取得官方审核回执或商店收录。

独立报告：[第三轮复验](../../docs/build-loop/RECHECK_NATIVE_B_FINAL_2026-10-06.md)。

公开证据：[旧假证据被阻断](screenshots/15-independent-legacy-blocked.png)、[独立点击结果](check/independent-final-results.json)、[旧9条事件原始快照](check/independent-original-events.jsonl)。
