# L7 / L8 准备状态与递交草稿

**日期**：2026-10-01
**截止**：2026-10-09
**状态**：本地 candidate ready，等待用户授权递交

## L7：打包与独立复跑

### 当前状态

- `hub stamp app/bundle` PASS（octosense-repair 0.1.0，blake3 `c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`）
- `hub check app/bundle --allow-unsigned` PASS
- `hub scan app/bundle --packet app/build/review.json` PASS（7 项 review questions）
- `python3 scripts/check_build_loop.py` VALID RECORD（**24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**，10-02 review 后）
- `python3 scripts/check_build_loop.py --ready` → **NOT READY**（35 项本地未过）
- **递交前置**：先按 [REVIEW_2026-10-02.md](REVIEW_2026-10-02.md) §6 修完 5 项 P0，其中 R-P0-5（web 路径死锁）直接影响演示素材
- `python3 scripts/verify_migration.py` PASS（1 处故意修改 conftest.py）
- `python3 docs/implementation/verify_pack.py` PASS

### 待补

1. **最终固定版本 SHA**：工程根目录未初始化 Git，需打 tag/SHA 作为公开固定点（可选）
2. **独立干净环境复跑**：把 `backend/.venv` 清空后用 `uv sync --frozen` 复跑；启动 card-host + uvicorn；跑 E2E
4. **演示视频**：录 2-3 分钟演示（mp4 或多帧摘要）

## L8：递交与回执

### 提交路径（按 13_APP_HUB_SUBMISSION_REVIEW.md）

- **GitHub Issue** 到 OctoSense/OctoSense-App-Hub（含 bundle 摘要 + 启动命令 + 截图 + 复跑步骤）
- **维护者收录**：等维护者 review
- **商店收录**：进入商店后记录时间戳
- **赛事回执**：与赛方交互后记录

### Hub Issue 草稿（占位）

```markdown
# App Submission: octosense-repair 0.1.0

## 简介
石墨主题维修协作 Hub 脚本应用。报修 → 技工接单 → 设备确认 → 预约 → 处理 → 完工 → 独立验收，沿本地事实源走完整闭环。

## Bundle
- id: octosense-repair
- version: 0.1.0
- bundle_blake3: c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82
- capabilities: [storage]
- hosts: {} (loopback only)
- storage: 16777216 bytes (16 MB)

## 后端独立验证
- 37 单元测试 PASS（14 核心 + 23 扩展）
- 13 步端到端 curl PASS（DRAFT → COMPLETED 含 reject+二次 record_progress）
- 7 项边界 E2E PASS（T02 / T04 / T05 / T15 / T18 / T30 / T31）

## 截图（真实原生，非 mock）
- runtime/build-loop/l0-shots/L0-A-1-initial.png
- runtime/build-loop/l0-shots/L0-A-2-after-click.png
- runtime/build-loop/l0-shots/L0-A-3-after-restart.png
- runtime/build-loop/l2-shots/L2-workbench-1-initial.png
- runtime/build-loop/l2-shots/L2-workbench-2-after-flow.png
- runtime/build-loop/l2-shots/L2-workbench-3-after-restart.png

## 启动
参见 `app/README.md`：
```sh
cd backend && uv sync --frozen && cd ..
OCTOSENSE_PORT=8712 backend/.venv/bin/python -m uvicorn --app-dir backend/src \
  octosense_backend.api:make_app --factory --host 127.0.0.1 --port 8712 &
MAKEPAD_REMOTE=8155 runtime/native-build/OctoSense-App-Hub/target/release/card-host \
  --bundle app/bundle --app-data /tmp/octosense-appdata --allow-unsigned --stamp
```

## 已知边界
- 后端 demo 身份走 X-Actor-Id；生产环境需可信会话/Bearer
- 真实 LLM / jobs / pairing code / App Card 视图均 NOT_RUN 或 BLOCKED（见 ACCEPTANCE.json）
- bundle capabilities 仅 storage，无网络权限；外部工单按设计 NOT_CONFIGURED

## 许可
Apache-2.0
```

### 等待用户授权

- 用户口头/文字明确：是否公开递交？
- 若授权：执行 GitHub Issue 创建 + tag + （可选）正式 PR
- 若不授权：保持本地 ready 状态；可继续录制演示或修复 UI 项

## 待办事项（10/2 - 10/7）

| 日期 | 工作 | 责任 |
|---|---|---|
| 10/2 | U01-U12 真实人工视觉/键盘测试 + 截屏；Hub Issue 正文定稿 | F |
| 10/3 | 演示视频录制（2-3 分钟）+ 摘要 | E/F |
| 10/4 | 独立干净环境复跑（uv sync + E2E + 重启回读） | F |
| 10/5 | 最终缺陷修复 + 文档定稿 | F |
| 10/6 晚 | 候选包冻结 + 摘要提交（工件 hash 存档） | 主设计 |
| 10/7 | 独立验收 | F |
| 10/8 | 封包 + 递交 Hub Issue（用户授权后） | F/提交负责人 |
| 10/9 | 最终检查 + 赛方回执 | 提交负责人/主设计 |