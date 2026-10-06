# 知了 · 2026-10-06 提交材料

本目录集中保存本次源码更新对应的比赛展示材料。GitHub 仓库：[Abarm009/zhiliao](https://github.com/Abarm009/zhiliao)。

| 材料 | 文件 |
|---|---|
| 正式普通话视频 | [zhiliao-demo-putonghua.mp4](video/zhiliao-demo-putonghua.mp4)，82 秒，1280×900 |
| 展示截图 | [7 张截图及来源说明](screenshots/README.md) |
| 字幕 / 旁白稿 | [narration.srt](video/narration.srt) / [narration.json](video/narration.json) |
| 原生脚本应用 | [octosense-repair-0.1.0.zip](bundle/octosense-repair-0.1.0.zip) |
| 本轮检查及能力边界 | [VERIFICATION.md](VERIFICATION.md) |
| 文件校验和 | [SHA256SUMS](SHA256SUMS) |

建议上传时优先使用视频、`02-reporter-draft.png`、`04-awaiting-acceptance.png`、`05-completed.png`、`06-event-history.png`，并附 `07-native-workbench.png` 展示原生界面。若页面允许，另附角色选择与预约确认截图。

视频使用已有 82 秒流程展示画面，补正式普通话旁白与原创器乐；包含静态截图、文字卡与原生界面片段。本轮未把它描述为重新录制的连续真实点击录像。旁白声音由用户从三段试听中选定第 3 号 Serena，在本机 Qwen3-TTS / MLX 生成，文案与视频没有发送到外部配音服务。

截图中的任务、角色、联系人和附件均为合成演示。原生界面展示与本地 Web/后端业务验证分别说明，当前整体验收仍 NOT READY。源码地址更新不等于 Hub 收录、商店上架或新增赛事回执。

解压应用包后，入口在 `octosense-repair/main.splash`；运行需要匹配版本的官方宿主。依赖和启动方式见 [根 README](../../README.md)。
