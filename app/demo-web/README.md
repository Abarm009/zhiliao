# OctoSense Repair · HTML 演示站（本地开发用）

这是**只用于本地浏览器看效果**的演示站，**不进 Hub bundle**，不是比赛正式交付件。

比赛正式交付仍是 `app/bundle/main.splash`（Hub 脚本应用）。

## 启动

```sh
# 1. 后端（已在 8713 跑着则跳过）
OCTOSENSE_PORT=8713 OCTOSENSE_DB=/tmp/octosense-live.db \
  EVIDENCE_ROOT=/tmp/octosense-live-ev \
  backend/.venv/bin/python -c "
from octosense_backend.api import make_app
import uvicorn
app = make_app('/tmp/octosense-live.db', evidence_root='/tmp/octosense-live-ev')
uvicorn.run(app, host='127.0.0.1', port=8713, log_level='info')"

# 2. demo 站
OCTOSENSE_DEMO_PORT=8090 OCTOSENSE_BACKEND_BASE=http://127.0.0.1:8713 \
  backend/.venv/bin/python -m uvicorn app.demo-web.server:app \
  --host 127.0.0.1 --port 8090 --log-level info
```

打开 http://127.0.0.1:8090/

## 角色

| actor | role | 项目 | 演示动作 |
|---|---|---|---|
| u-reporter-1 | REPORTER | prj-A | 报修、确认预约、验收、退回、取消 |
| u-reporter-2 | REPORTER | prj-B | 同上 |
| u-tech-1 | TECHNICIAN | prj-A（HVAC） | 接单、提议预约、开工、记录处置、上传证据、完工 |
| u-tech-2 | TECHNICIAN | prj-A & prj-B（电气） | 同上 |
| u-manager | MANAGER | prj-A | 分配技工、改派、隔离证据、取消 |

身份存浏览器 localStorage（`octosense.actor`）；服务端只信 `X-Actor-Id` 头。
**生产环境应替换为 host session / 原生 Bearer 取得 actor**，此处仅本地演示。

## 端点

- `GET /` — 登录页（4 角色卡片）
- `GET /workbench` — 工作台（任务列表 + 详情）
- `GET /api/demo/health` — demo 层 + 后端层健康检查
- `/api/octosense/v1/*` — 反向代理到后端 8713

## 流程

```
报修人创建草稿 → confirm_draft → 接单 → 绑设备 → 提议预约 → 报修人确认预约 → 
开工 → 处置记录 → 上传证据 → 完工提交（需 READY 证据）→ 报修人验收 → COMPLETED
                       ↓                                          ↓
                   经理可改派/隔离                            报修人可退回 → 重做
```

每个角色看到的「可执行动作」不同；服务端强制权限，角色不对就返 403 PERMISSION_DENIED。
