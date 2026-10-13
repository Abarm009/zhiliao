# App Hub 首次提交回执 · 2026-10-08

- 官方 Issue：[Submit octosense-repair 0.1.0-b · #149](https://github.com/OctoSense-org/OctoSense-App-Hub/issues/149)
- 作者：Abarm009；网页回读状态：Open。
- 版本：octosense-repair 0.1.0-b；首次 unsigned；申请 human-review。
- 固定标签：[octosense-repair-b-v0.1.0](https://github.com/Abarm009/zhiliao/releases/tag/octosense-repair-b-v0.1.0)，公开标记 Pre-release。
- 标签完整提交：8d730569546cb57310944bb299695134df773b9d，已通过远端标签回读及全新标签克隆的 HEAD 确认。
- 应用包目录：app/bundle/；ZIP 根目录：bundle/。
- BLAKE3：e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579。
- ZIP SHA256：6a58e27ade7255760e19b6b7229d744eb92799958fd84c728bf0d46c4de1fa12；大小 1,544,808 字节。

## 本轮检查

1. 公开固定提交存在，manifest 与本地一致；源码包与该提交无差异。
2. ZIP 中 12 个文件逐字节匹配源码包。
3. 在 runtime/hub-submission-20261008/fresh-tag-clone/ 全新稀疏克隆上执行 hub check，退出码 0，PASSED，仅 unsigned warning。
4. 同一克隆重新生成 hub scan packet：7 项，未指定 reviewer；提交发布者更正答复，并申请 human-review。
5. 网页创建后回读 #149 的标题、作者、Open 状态、版本、固定 SHA、检查输出和缺口说明；GitHub API 再次读取确认正文存在。

## 实际操作与边界

命令行标签推送因没有 GitHub 凭据失败，随后通过已登录 GitHub 网页创建 Pre-release 和固定标签。GitHub 连接器创建官方 Issue 返回 403 Resource not accessible by integration，随后使用官方 submit-app.yml 网页表单成功递交一次。

没有修改应用包、重写业务代码或重新宣称业务通过。公开提交中的旧 listing/README/截图结论未改写；在官方 Issue 明确更正并列为待修问题。

旧工具构建版本只由历史 SOURCES.md 记录为 Hub@6741dea（官方完整 SHA 6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747），本地该工具目录已无 .git，不能通过当前目录 HEAD 证明二进制构建来源。此限制已在官方表单披露；未声称当前未修改官方 main 已验证。标签名称与当前表单建议 v<version> 格式不同，已显式披露并保留固定标签。

真实附件、真实模型、完整原生闭环、动态幂等、最新宿主兼容及全部38业务/12UI验收仍未通过或未验证。本次未执行完整业务独立复验。

**当前状态：官方 App Hub 已递交候选，待维护者反馈；未取得审核通过或商店收录证据。**

## 证据

- [实际已提交正文](SUBMITTED_ISSUE.md)
- [网页回执截图](issue-149.jpg)
- 全新标签克隆与扫描 packet 保存在 runtime/hub-submission-20261008/（不入库）。
- ISSUE_BODY.md 是连接器尝试前准备的草稿；连接器返回403，实际提交正文以 SUBMITTED_ISSUE.md 为准。

