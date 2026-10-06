# 知了 · 维修任务协作

队伍名：**知了**。Agentic App 2026 初赛项目，围绕同一项维修任务组织报修人、技工与项目经理的协作：报修 → 接单 → 设备确认 → 预约 → 处置 → 完工 → 独立验收 / 退回重做。

## 演示与提交材料

**[2026-10-06 提交入口](submission/2026-10-06/README.md)**：82 秒正式普通话视频、7 张截图、字幕、应用包及本轮核验记录。

- [观看 / 下载视频](submission/2026-10-06/video/zhiliao-demo-putonghua.mp4)：用户选定 Serena 温和女声，正式普通话旁白，配原创器乐；沿用已录制的流程展示画面。
- [截图说明](submission/2026-10-06/screenshots/README.md)：真实本地演示页面与原生界面展示，使用合成数据。
- [原生脚本应用包](submission/2026-10-06/bundle/octosense-repair-0.1.0.zip)。
- [本轮验证与已知边界](submission/2026-10-06/VERIFICATION.md)。

![报修人独立验收完成](submission/2026-10-06/screenshots/05-completed.png)

## 当前验证状态

2026-10-06 本轮复跑：后端 **190 项单测通过**，**17 步 HTTP 业务链通过**（含退回、第二轮完工、幂等回放与终态拒绝）；本次截图任务在报修人页面完成验收，状态为 `COMPLETED`。`hub check --allow-unsigned` 通过，publisher 未签名。

**整体仍为 NOT READY**：验收台账 31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED。原生宿主重绘、部分动作 handler、grant 生命周期和真实模型接入尚未通过完整验收。Python/Web 业务验证、原生界面展示及包准入分别记录。AI 助手属于待接通范围；视频配音模型与应用 AI 能力无关。

本次更新源码仓库与展示材料；Hub 收录、商店上架和新的赛事回执尚未完成。此前仓库登记记录见 [源码提交回执](docs/build-loop/REPOSITORY_SUBMISSION_2026-10-02.md)。

## 本地运行

```sh
uv sync --frozen --directory backend
backend/.venv/bin/python scripts/run_local.py --port 8711 --web-port 8712 --runtime runtime/demo
```

浏览器打开 `http://127.0.0.1:8712/`，选择演示身份。服务只绑定本机，任务、证据及日志写入 `runtime/`。本轮验证了现有开发环境启动；未宣称全新机器依赖安装已验证。

原生应用入口为 `app/bundle/main.splash`，需安装匹配版本的 OctoSense/card-host；它不随包安装 Python 后端。参见 [应用运行说明](app/README.md) 与 [平台边界](app/docs/route-decision.md)。

## 项目文件导航

| 目录 | 内容 |
|---|---|
| `app/bundle/` | 原生 OctoScript 应用、manifest、listing、图标与原生截图 |
| `backend/src/octosense_backend/` | 独立维修任务领域后端 |
| `backend/tests/octosense_backend/` | 当前领域单元测试 |
| `app/demo-web/` | 本地浏览器演示与 API 代理，不进入原生包 |
| `submission/2026-10-06/` | 本次可直接查看、下载和上传的比赛材料 |
| `docs/implementation/` | 需求、架构、接口和构建计划；设计不等于实现 |
| `docs/build-loop/` | 验收台账、审查与修复记录；按记录时间阅读 |
| `runtime/` | 本地数据库、模型、虚拟环境、日志与备份；不提交 |

旧 `wagent_backend` 保留为独立迁移与回归资产，其 contracts 不在本轮重写。历史背景见 [架构](docs/ARCHITECTURE.md)、[迁移](docs/MIGRATION.md)、[核验记录](docs/VERIFICATION.md)。

许可：[Apache-2.0](LICENSE)。数据来源见 [仿真种子说明](backend/data/simseed/PROVENANCE.md) 和 [本地演示数据说明](docs/PRIVACY.md)。
