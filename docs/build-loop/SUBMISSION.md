# OctoSense Repair — 递交材料（Agentic App 2026 比赛）

**项目**：维修协作 Hub 脚本应用 + 后端业务核心
**截止**：2026-10-09
**更新时间**：2026-10-02
**状态**：**本地未就绪**。台账 **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**。
10-02 全盘 review 把 10-01 自评的 33 PASS 中 **9 项改判**（T01→NOT_RUN；T02/T03/T05/T08/T16/T17/T18/T29→FAIL），其中 5 项 P0。
**问题清单、复现命令与修改建议：[REVIEW_2026-10-02.md](REVIEW_2026-10-02.md)**；本轮执行记录：[../VERIFICATION.md](../VERIFICATION.md)。
3 项 BLOCKED 是 **P06/P07/P08（外部递交，需用户授权）**，不是 jobs/LLM。L8 递交需用户明确授权（开发与维护者收录/赛事回执分别记录）。

## 1. 简短需求

围绕同一项维修任务，让报修人、维修技工、项目经理完成"报修 → 接单 → 设备确认 → 预约 → 处理 → 完工 → 独立验收"。AI 助手参与理解与建议，但所有人接受/拒绝操作走统一任务命令边界，版本与幂等由服务端强制。本地维修任务是事实，外部工单系统按设计 NOT_CONFIGURED。

## 2. 固定源码版本

| 组件 | SHA / 备注 |
|---|---|
| OctoSense-App-Hub | `6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747`（固定 detached） |
| Octoscript-Makepad | `b33f494b963759088edf5785fc6266cb8593818ee` |
| Makepad | `4fdcfccc127b700f1fc01aa1a5488af938dd7f3d` |
| Octoscript | `68f6a9df55692b5d8ef8873a12721e279a3f40d6` |
| rustc / cargo | 1.98.1 |
| Python | 3.12.13 |
| 后端 | octosense_backend 0.2.0（12 表 / 27 命令 / 29 应用路由；`__init__.py` 仍写 0.1.0） |
| 单元测试 | **39 PASS**（11 核心 + 4 预约改派 + 23 扩展 + 1 dummy） |
| 端到端 | 13 步业务主链 PASS（`backend/scripts/e2e_full_chain.sh`） |

`hub stamp` 后 bundle digest：`c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`
（详情见 `app/bundle/manifest.json`）

## 3. 启动说明

参见 `app/README.md`。

简版：
```sh
cd backend && uv sync --frozen && cd ..
backend/.venv/bin/python -m uvicorn --app-dir backend/src \
  octosense_backend.api:make_app --factory --host 127.0.0.1 --port 8712 &
runtime/native-build/OctoSense-App-Hub/target/release/card-host \
  --bundle app/bundle --app-data /tmp/octosense-appdata --allow-unsigned --stamp
```

## 4. 演示

| 文件 | 内容 |
|---|---|
| `runtime/build-loop/l0-shots/L0-A-1-initial.png` | 首次启动（石墨主题，3 按钮，未开始） |
| `runtime/build-loop/l0-shots/L0-A-2-after-click.png` | 点击"开始处理"后（处理中 + 持久化事件 1 + [begin]） |
| `runtime/build-loop/l0-shots/L0-A-3-after-restart.png` | 重启 card-host 后从 fs jail 回读（处理中仍在） |
| `runtime/build-loop/l2-shots/L2-workbench-1-initial.png` | L2 工作台首次启动（9+ 业务按钮，actor=报修人一） |
| `runtime/build-loop/l2-shots/L2-workbench-2-after-flow.png` | L2 工作台多步操作后（actor=manager，state.status=已提交报修） |
| `runtime/build-loop/l2-shots/L2-workbench-3-after-restart.png` | L2 重启回读（state.json 内容与 before 一致） |

视频建议：3 张 L0 截屏 + 3 张 L2 截屏 + 后端 curl 13 步端到端串讲。

## 5. 数据来源与限制

- **来源**：合成数据（`backend/src/octosense_backend/seed.py`），2 项目 / 2 报修人 / 2 技工 / 1 经理 / 2 设备 / 1 空间。
- **真实素材**：状态持久化在 fs jail（card-host enforce 16 MB）和 SQLite WAL。
- **未迁移**：私有真实数据；旧 wagent_backend 的图谱与历史会话；任何未公开授权的源码。
- **第三方资源**：图标 SVG 为原创，使用石墨色 `#111A1B` 等。
- **许可**：Apache-2.0（与 Hub 一致）。

## 6. 隐私与许可

- bundle 仅声明 `capabilities: ["storage"]`；不发起网络请求（`hosts: {}`）。
- 后端 demo 身份通过 `X-Actor-Id` 请求头读取；生产环境必须替换为可信会话/原生 Bearer 取得。
- 端到端运行不写、未收集、未发送任何用户隐私；本工程运行在用户本机，仅 `runtime/`、`/tmp/octosense-appdata`、`runtime/octosense.db` 写入数据。

## 7. hub check / scan 输出

`hub check --allow-unsigned`:
```
octosense-repair 0.1.0 — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

`hub scan --packet app/build/review.json`：已生成 7 项 review questions 的 packet（默认无 reviewer，hub 默认配置）。

## 8. 已通过的 ACCEPTANCE 项（24 / 64）

详情见 [ACCEPTANCE.json](ACCEPTANCE.json)，候选版本 `octosense-backend@0.2.0`。**10-02 review 后为 24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED。**

- **G0**：G0-A（固定版本 + 原生构建 + admit + 截屏；截图与当前 splash 不同版本，见 R-P2-4）、G0-C（唯一事实源 + 原子一致性）
- **T 业务**：T04 / T06 / T07 / T09 / T10 / T11 / T12 / T14 / T15 / T19 / T20 / T21 / T22 / T27 / T28 / T30 / T31
- **P 发布**：P01-P05（scan / stamp / check / 已知缺陷 / 包摘要；其中 P02/P04/P05 的截图与 DB 证据存在版本不匹配，见 R-P2-4）
- **FAIL（10-02 改判）**：T02 / T03 / T05 / T08 / T16 / T17 / T18 / T29 —— 逐条依据见 [REVIEW_2026-10-02.md](REVIEW_2026-10-02.md) §4
- **NOT_RUN（原 PASS 降级）**：T01（未接真实模型）

`check_build_loop.py` records 验证：`VALID RECORD STRUCTURE (64 checks; PASS=24, NOT_RUN=29, FAIL=8, BLOCKED=3)`；
`check_build_loop.py --ready` 返回 **NOT READY**（35 项本地未过）。

## 9. 已知缺陷与边界（R- 编号，详见 REVIEW_2026-10-02.md）

- **P0（阻断交付，5 项）**
  - R-P0-1 原生 UI 声明 23 节点只实例化 15 个，"退回 / 重置演示 / 任务列表 / 状态行"不存在
  - R-P0-2 core 命令不按 project 校验角色，跨项目可写（影响 10 个命令）
  - R-P0-3 `GET /tasks/{id}` 无授权校验，任意 actor 可读全量
  - R-P0-4 同 key 不同内容返回 201 而非 409；`IdempotencyConflict` 与 `result='ERROR'` 为死代码
  - R-P0-5 demo-web `confAppt` 条件循环，报修人无法确认预约，**web 路径在 SCHEDULED 死锁，走不到 COMPLETED**
- **P1（8 项）**：R-P1-1 原生任务不落盘（重启丢任务 + id 重复）；R-P1-2 `u-tech-2` 登录即 403；R-P1-3 `record_advice` 重复 key 返 500；R-P1-4 `/task/{id}` 500；R-P1-5 6 处幂等键用 `Date.now()`；R-P1-6 `currentVer()` 猜版本；R-P1-7 证据根目录跟 CWD 绑定；R-P1-8 原生 UI 零权限 + 无声失败
- **NOT_RUN**：
  - T13 / T23：jobs / scheduler / 提醒后台未实现
  - T25 / T26：未接入真实 LLM（UI 明确标记"离线演示，原话保留"；不作为模型成功）
  - T32：pairing code / host session（依赖 Shell）
  - T33-T38：agent harness（scoped_queries / intent_compiler / result_verifier）未实现
  - U01-U12：窄窗、文字放大、键盘焦点、长中文、滚动稳定性、2–3 分钟演示脚本；**且要先修 R-P0-1 / R-P1-8 才有东西可验**
- **P2（7 类）**：契约脱节（schema 25→12、openapi 与实现零重叠）、数字口径、BLOCKED 归属、证据空心化、代码/台账漂移、`test_baseline.py` 失败（49 个继承测试不可运行）、结构与色值
- **BLOCKED**：P06 / P07 / P08 —— Hub Issue / 商店收录 / 赛事回执，**需用户明确授权**
- **设计说明**：后端 demo 身份通过 `X-Actor-Id` 请求头读取，且未按 project 隔离；真实模型能力（G0-E）未通过：UI 不冒充模型建议，不写任务状态

## 10. 递交与回执

按 START_PROMPT §"L8 递交与回执"：

> 准备公开源码固定 tag/SHA、Hub Issue 完整正文及赛事提交材料；有明确发布授权再实际提交。

本轮状态：
- 本地 candidate ready（`octosense-backend@0.2.0 + Hub@6741dea + octosense-repair@0.1.0` + 6 张截图）
- `hub check` + `hub scan` PASS；台账 24 PASS / 8 FAIL / 35 项本地未过
- 待用户给出公开发布授权后再创建 Issue / tag / PR

未发出 Hub Issue 与赛事提交回执；维护者收录状态等待记录。

## 11. 复跑命令

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 1. 迁移基线
python3 scripts/verify_migration.py
# 2. 设计包结构
python3 docs/implementation/verify_pack.py
# 3. 后端单测（39 项）
backend/.venv/bin/python -m pytest backend/tests/octosense_backend/ -q
# 4. 启动后端 + 端到端 curl 13 步全链
OCTOSENSE_PORT=8713 OCTOSENSE_DB=/tmp/octosense.db \
  backend/.venv/bin/python /tmp/run_api.py > /tmp/octosense-e2e.log 2>&1 &
bash backend/scripts/e2e_full_chain.sh
# 5. hub stamp / check / scan
runtime/native-build/OctoSense-App-Hub/target/release/hub stamp app/bundle \
  && runtime/native-build/OctoSense-App-Hub/target/release/hub \
     check app/bundle --allow-unsigned \
  && runtime/native-build/OctoSense-App-Hub/target/release/hub \
     scan app/bundle --packet app/build/review.json
# 6. 启动原生 UI（card-host）
MAKEPAD_REMOTE=8155 runtime/native-build/OctoSense-App-Hub/target/release/card-host \
  --bundle app/bundle --app-data /tmp/octosense-appdata --allow-unsigned --stamp \
  &
# 7. 截屏（首屏/重启回读）
curl -sS "http://127.0.0.1:8155/g?raw=1" -o /tmp/initial.png
# 8. 台账
python3 scripts/check_build_loop.py
python3 scripts/check_build_loop.py --ready  # NOT READY：35 项本地未过
python3 docs/../build-loop/REVIEW_2026-10-02.md  # 人工阅读问题清单
```

## 12. L2-L6 主切片（2026-10-01 记录，2026-10-02 复核修订）

业务核心完整实现并通过验证：
- **后端 29 应用路由**：27 命令 + get_task + health（设备绑定、证据附件、列表、历史建议、收藏、记录处置等）
- **12 张表**：projects/users/roles/spaces/assets/tasks/actions/events/appointments + repair_evidence + repair_pins + repair_advice
- **39 项单元测试 PASS**（11 核心 + 4 预约改派 + 23 扩展 + 1 dummy）
- **HTTP 端到端 13 步全链 PASS**：create_draft → confirm_draft → accept_task → bind_asset → propose_appointment → confirm_appointment → start_progress → record_progress → submit_completion → reject_completion → record_progress → submit_completion → accept_completion，13 events，COMPLETED
- **HTTP 边界 E2E**：T04 双技工抢单只一人、T15 旧 version 409、T18 缺 actor 401、T30 收藏隔离、T31 取消释放预约 均通过；T02 只覆盖「同 key 同内容」，「同 key 不同内容返 409」未实现（10-02 改判 FAIL）；T05/T18 跨项目问题 10-02 改判 FAIL
- **原生 UI**：main.splash 石墨工作台，声明 11 业务按钮 + 4 角色按钮；**运行时只实例化 13 个按钮**，"退回 / 重置演示"与任务列表、状态行在 412×816 视口外被整体丢弃（10-02 实测 `/d` 只返回 W3 23 个节点）；fs jail 内 state.json + events.jsonl 写入
- **重启回读（部分）**：card-host kill + restart → state.json 的 actor/status 恢复，**但 TASKS 全部丢失**；重启后点"接单"为 silent no-op，再点"新建草稿"会产生第二个 `tsk-0`
- **ACCEPTANCE.json 24 项 PASS**：G0-A/G0-C + T04/T06/T07/T09/T10/T11/T12/T14/T15/T19/T20/T21/T22/T27/T28/T30/T31 + P01-P05
- **NOT_RUN**：T13/T23（jobs/scheduler）、T01/T25/T26（LLM 接入）、T32（pairing）、T33-T38（agent harness）、U01-U12（真实人工视觉/键盘）
- **FAIL（10-02 新增）**：T02/T03/T05/T08/T16/T17/T18/T29
- **BLOCKED**：仅 P06/P07/P08（外部递交授权）

固定版本：
- 后端：octosense_backend 0.2.0（独立新空间 + L1+L2-L7 扩展）
- Bundle：octosense-repair 0.1.0（Hub@6741dea）
- bundle_blake3：`c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`（以最新 hub stamp 为准）

启动命令保持 `app/README.md` 一致。

### 文件所有权（本轮新增 / 修改）

- `backend/src/octosense_backend/extended.py`           新增（14 类扩展命令）
- `backend/src/octosense_backend/api/__init__.py`       改写（29 应用路由）
- `backend/src/octosense_backend/db/__init__.py`        加 3 张表 schema
- `backend/src/octosense_backend/errors.py`             加 7 类业务错误
- `backend/src/octosense_backend/commands/__init__.py`  cancel 释放预约
- `backend/tests/octosense_backend/test_extended.py`    新增 23 项扩展单测
- `backend/scripts/e2e_full_chain.sh`                   新增 13 步 E2E
- `app/bundle/main.splash`                              改写为石墨工作台
- `docs/build-loop/SUBMISSION.md`                       更新版本 + 进度
- `docs/build-loop/ACCEPTANCE.json`                     33 项 PASS / 28 NOT_RUN / 3 BLOCKED
- `runtime/build-loop/iter-L2-to-L6.md`                 新增 L2-L6 总结
