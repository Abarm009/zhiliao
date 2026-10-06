# 2026-10-06 材料与源码核验

本文件区分本轮实际检查和未完成能力。文件与命令结果置信度：高；整片听感由用户播放判断。

| 检查 | 本轮实际结果 |
|---|---|
| `pytest backend/tests/octosense_backend/ -q` | 190 passed in 62.20s |
| `backend/scripts/e2e_full_chain.py` | 17 步 HTTP E2E PASS；独立端口、临时 DB；含退回重做、二次完工、READY 附件字节核对、幂等回放与终态拒绝 |
| 本次截图任务 | 页面创建草稿 / 确认报修 / 报修人验收，其他阶段由本地 API 准备；页面最终 COMPLETED v9 |
| `hub check app/bundle --allow-unsigned` | PASSED；publisher 未签名；移出本地 `.bak` 备份后重新 stamp |
| `hub scan` | 已生成 7 问人工评审包，未接 reviewer；不是自动评审通过或发布回执 |
| `docs/implementation/verify_pack.py` | 36 文件 / 158 本地链接 / 6 SVG；参考契约与 SQL 检查通过，仅为设计结构检查 |
| `scripts/check_build_loop.py` | 64 项台账结构 VALID：31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED |
| `scripts/check_build_loop.py --ready` | NOT READY，退出 2；历史 revision 项仍提示与 candidate 不同 |
| `scripts/verify_migration.py` | 退出 1；5 个已在此前修复中变更的迁移基线文件与原始快照不同；本轮不重写清单掩盖差异 |

迁移差异为 `backend/pyproject.toml`、`backend/tests/conftest.py`、`backend/tests/test_mcp.py`、`backend/tests/test_ops_agent.py`、`backend/tests/test_ops_api.py`；本轮未修改这些文件。未声称旧基线全测或全新机器依赖安装已验证。

## 视频与声音

- MP4 82.000 秒，H.264 1280×900，AAC 48 kHz 双声道；2,636,409 字节。
- 原始压缩视频数据包与源片一致；ffmpeg 全片解码通过。
- 16 段旁白非空，全部在对应画面时段内结束；过长句子缩短重录，保留自然停顿。
- 综合响度 -16.67 LUFS，真峰值 -4.50 dBTP，无削波。
- Qwen3-TTS 1.7B CustomVoice / MLX 4bit，中文 Serena，第 3 号音色由用户选择；风格明确为正式、自然、克制的标准普通话。视频配音不代表应用已接通真实 AI 模型。
- 配乐为本次本机制作的原创器乐，旁白期间压低音乐，首尾淡入淡出。
- [机器核验结果](verification/media.json)、[音色参数](verification/voice.json)、[16 段时间对齐](video/alignment.json)。

## 原生应用与交付状态

bundle digest：`eff13f557080fc12ac2961f6bee83a2365f3d8fb5ac0e56681cee45b13c4ad26`。

原生重绘、部分动作 handler、grant 生命周期、真实模型与 UI 独立验收仍有缺口，见 [ROUND5 报告](../../docs/build-loop/REPAIR_RESULT_2026-10-06_ROUND5.md) 及 [验收台账](../../docs/build-loop/ACCEPTANCE.json)。本轮没有擅自改变台账结果，也不把媒体文件生成当成业务能力验收。

公开提交仅包含经过筛选的源码、文档、展示材料及应用包。数据库、密钥、日志、模型权重、语音环境、官方参考克隆和旧配音候选留在本机。此次用户授权更新既有 GitHub 源码仓库；未另行创建 Hub Issue、递交赛事消息或宣称上架。
