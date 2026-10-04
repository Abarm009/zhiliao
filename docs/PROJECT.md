# 知了 OctoSense Repair · 项目说明

> **项目**：`octosense-repair` v0.1.0（脚本应用 / Script App）
> **目标赛事**：Agent2App Hackathon 2026（OctoSense 12 个官方应用场景）
> **宿主**：OctoSense `card-host` / `app-contract = "1"`（App Hub `97c2a1fd` / `0f332112`）
> **基线**：[hagency-org/Rinx](https://github.com/hagency-org/Rinx) `05daf9bd` 作为小程序宿主基线
> **仓库根**：`/Users/abeam/一些尝试/知了OctoSense`
> **包目录**：`app/bundle/`（按 [OctoSense PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md) 规范）

本文档按 [`docs/build-loop/REPAIR_PROMPT_2026-10-03_ROUND4.md`](../build-loop/REPAIR_PROMPT_2026-10-03_ROUND4.md)
以及官方 [App Hub 提交规范](https://raw.githubusercontent.com/OctoSense-org/hackathon-agenticapp26/main/docs/app-hub-submission.md)
整理。回答初赛评审最关心的六个问题：源码与许可、应用目标与场景、
宿主与启动方式、数据 / 权限 / 隐私、Agent 任务演示、运行截图与复现步骤。

---

## 一、公开源码仓库、固定提交号、Apache License 2.0 许可证

| 项 | 值 |
|---|---|
| 仓库 | `/Users/abeam/一些尝试/知了OctoSense` |
| 固定提交 | 见 `git rev-parse HEAD`；本轮提交尚未推送（按用户授权要求保留为本地可检查改动） |
| 许可证 | `Apache-2.0`（见根目录 `LICENSE`） |
| 起源 | 独立迁移副本，原工程 `wagent/agent/`（commit `a9caf17e0f830b23e694f952e21e6c0dbefa34cc`）；来源逐文件核对见 `migration-manifest.json` 与 `docs/MIGRATION.md` |
| 不复制内容 | 原 `.env`、私钥、运行数据库、`data/kg.json`、`data/sessions/`、`.git`、`.venv`、缓存、旧服务器脚本 |

---

## 二、应用目标、适用场景、图标、截图、作者与支持方式

### 应用目标

**「报修 → 技工接单 → 设备确认 → 预约 → 处理 → 完工 → 验收」**完整维修协作闭环。
围绕同一项维修任务，三类角色（报修人 / 技工 / 经理）按权限矩阵在原生宿主与网页端协作，
Agent 在脚本内通过 `runCommand` 守门统一命令边界（`-view=1` 时宿主实证：0 解析错误）。

### 适用场景（对齐 OctoSense 12 场景）

| 场景 | 落点 |
|---|---|
| mail / messaging | 通知 + 已撤权用户作业失效（jobs 模块）；hagency 协作预留 |
| calendar | 预约窗口（`repair_appointments` + `appointment_*`） |
| weather / news | 不在范围内 |
| music / video | 不在范围内 |
| markets / navigation | 不在范围内 |
| shopping / logistics | 设备身份/服务关系（`repair_asset_services`） |
| **writing / creation** | **报修原话、处置记录、完工说明**（核心文本流） |
| system / devices | 设备绑定、设备空间服务关系、隔离存储读写 |
| productivity | 通用工作台 + 任务列表 + 命令执行 |

主场景：**writing/creation + system/devices + productivity**（维修协作 = 任务驱动 + 设备身份 + 文本沟通）。

### 图标与截图

- `app/bundle/assets/icon.svg` — 入口图标（应用安装后启动器显示）
- `app/bundle/screenshots/01-main.png` — 当前 L0 最小切片截图
- 截图依据：`card-host --bundle app/bundle --allow-unsigned` 实际渲染（见 `runtime/repair-round2-20261002/splash-probe/`）
- 已知缺口：固定版本 `card-host` 不实例化 `set_visible/on_render` 子控件，按钮重排受限；
  详见 `app/docs/round4_native_probe.md` 与 `runtime/review-round3-20261003/` 的 host.log

### 作者与支持方式

| 项 | 值 |
|---|---|
| 团队 | 知了（OctoSense 本地开发团队） |
| 发起人 / 联系方式 | 项目根 README 顶部 |
| 维护方 | Abram（用户）；本轮 Agent 协助编码 |
| 支持渠道 | 见 `app/bundle/listing.json::publisher.support` |
| 隐私政策 | 见 `app/bundle/listing.json::publisher.privacy_policy_url`（占位 URL，须 G0 由用户确认后替换为实际链接） |

---

## 三、宿主版本、支持平台、依赖与启动说明

### 宿主版本

| 项 | 值 |
|---|---|
| 宿主 | OctoSense `card-host` / `app-host`（具体提交由 App Hub pin 决定） |
| App Hub 版本 | `97c2a1fd9aa49a6b87586f228e070e0c16b1067b` / `0f332112` |
| App Contract 版本 | `octosense-app-contract = "1"` |
| L0 语言 | OctoScript（参见 `app/bundle/main.splash`） |
| 复现依据 | 历史 `runtime/repair-round2-20261002/splash-probe/` 记录了 `card-host --bundle` 的真实输出；本轮 25 项回归 + 7 项 R3 探针在 Python 后端层独立验证 |

### 支持平台

`app/bundle/listing.json::platforms: ["macos"]`（按 L0 切片当前实测范围声明；扩展到 iOS / Android 需新构建版本）

### 依赖

- 后端 Python：`Python 3.11+`、`uv`；`backend/pyproject.toml` 锁版本
- 前端 Web：`app/demo-web/static/` 纯静态（不依赖外部 CDN）
- 原生脚本：`app/bundle/main.splash`（OctoScript L0，宿主提供 fs / time / http_resource）
- 启动期工件：`backend/.venv/`、`runtime/`、`evidence_root/` 全部锚到独立临时目录，不污染宿主

### 启动说明

```sh
cd backend/ ; uv sync --frozen
python3 scripts/verify_migration.py        # 校验迁移基线
backend/.venv/bin/python scripts/run_local.py  # 默认 127.0.0.1:8711
backend/.venv/bin/python scripts/test_baseline.py  # 离线基线
backend/.venv/bin/python backend/scripts/e2e_full_chain.py  # E2E
# 原生（独立 sandbox）
MAKEPAD_REMOTE=8151 card-host --bundle app/bundle --allow-unsigned --app-data .local-state &
sleep 7
curl -s -o app/bundle/screenshots/01-main.png '127.0.0.1:8151/g?raw=1'
curl -s 127.0.0.1:8151/quit
# 重新计算 digest 后再 stamp
backend/.venv/bin/python -c "import hashlib,pathlib; b=pathlib.Path('app/bundle').resolve(); ...; print(hashlib.blake3(b'...').hexdigest())"
# hub check / hub scan / hub stamp / hub sign-manifest（参见 PUBLISHING.md）
```

---

## 四、数据来源、申请权限、隐私处理、用户授权 / 拒绝 / 失败行为

### 数据来源

| 数据 | 来源 |
|---|---|
| 项目 / 角色 / 空间 / 设备 / 服务关系 | 合成夹具（`backend/src/octosense_backend/seed.py`） |
| 任务 / 预约 / 完工 / 证据 / 事件 / 通知 | 真实用户操作 + 后端 SQLite（`runtime/octosense.db`） |
| 仿真种子 | 旧工程 `agent/data/simseed/l1_seed.json`（带 `PROVENANCE.md`，见 `docs/MIGRATION.md`） |
| 不复制 | 个人邮箱 / 通话录音 / 真实用户凭据（已排除，迁移说明 §"明确排除"） |

### 申请权限（capabilities，对齐 App Hub 闭集）

```text
storage        — 应用自身隔离存储读写（jobs / tasks / receipts / events 落盘）
```

`app/bundle/manifest.json::capabilities = ["storage"]`；网络、相机、位置、剪贴板、
邮件、glance、news、model 等均未请求，符合"请求最广者"原则。

### 隐私处理

- 联系人（`contact_info`）按 [R3-04 脱敏矩阵](../build-loop/REPAIR_VERIFICATION_2026-10-03_ROUND3.md)
  对未接单技工 / 跨项目用户脱敏，详情 / 事件 / SSE / 历史建议 / 通知列表共用同一投影
- 撤权接收者不再产生 / 读取新通知（`/notifications` 按 `auth.task_visible` 投影）
- 原生 `addEvidence` 不再伪造 `bytes:32 / sha:id-sha`，写 `ready:false` 占位，完工必须用真实文件
  （按 R3-08 / §一硬约束，详见 `app/docs/round4_native_probe.md`）
- 内部审计（`repair_actions`、`repair_events`）保留；只对外投影做字段脱敏
- `agent_workspace = account` 默认按账号隔离存储

### 用户授权 / 拒绝 / 失败行为

按 Rinx `02-octoscript-mini-app-authority.md`：每次打开需独立授权，
授权关联账号 + 登录会话 + 应用实例（最长一小时），关闭或退出后撤销。

| 场景 | 行为 |
|---|---|
| 报修人在 OPEN 不能绑设备（基线）/ 经理在 OPEN 可绑（基线） | 后端按 `bind_asset` 阶段矩阵校验；前端 `allowed_actions` 仅展示合法入口 |
| 撤权后访问 / 写入 | `auth.task_visible` + `_check_actor_role` 双重校验；同 key 回放同样走对象授权（R3-02） |
| 草稿 / 完工附件缺失或损坏 | 拒绝 `submit_completion` 并返回 `EVIDENCE_INTEGRITY`；独立失败审计追加（不掩盖业务失败） |
| 通知读取 | 已撤权任务的通知 / 正文 / 任务 ID 不返回 |
| 原生 picker / 隔离存储缺失 | 显式提示"宿主 picker 缺失"，`ready:false` 占位，不假装成功 |

---

## 五、Agent 任务演示（输入 → 实际步骤 → 结果核验 → 人工确认）

按初赛要求"展示 Agent 在作品运行时如何读取获授权的状态、提出操作、
执行并核验结果"。Agent 集成在脚本层 `runCommand` 守门 + 命令级 `_run`：
同一事务内做授权 / 幂等 / 阶段 / 业务写 / 事件 / 回执；不允许绕过。

### 5.1 输入（Input）

| 类型 | 示例 |
|---|---|
| 用户自然语言 | "三楼会议室空调不制冷" → `create_draft problem_text` |
| 设备身份 | `asset:as-a-1` 或 `AC-001` → `match_assets_by_code` / `resolve_asset` |
| 时间窗口 | `start_at_ms / end_at_ms`（客户端毫秒，服务端时钟校验） |
| 类别 / 空间 | `HVAC_NOT_COOLING / sp-a-1`（项目内强制） |
| 幂等键 | `idempotency_key`，保证重试不重复写入 |
| 决策提示 | "请报修人确认 / 请选择空间 / 请绑定设备" |

### 5.2 Agent 实际完成的步骤

1. **授权校验**：每个命令级 `body()` 入口检查角色 + 关系 + 阶段；
   `unbind_asset` 复用 `bind_asset` 阶段矩阵（R3-05）；撤权后无角色即拒
2. **幂等指纹**：`fingerprint(command + actor + project + task + expected_version + params)`；
   同 key 同内容 → 完整原结果回放；同 key 改内容 → 409
3. **业务写**：状态机 + 阶段矩阵 + 版本号严格检查
4. **事件与回执**：`repair_events`（业务流）+ `repair_actions`（动作幂等）同一事务写入
5. **二次授权 / 校验**：邮件 / 通知 / 完工 / 取消 / 验收按业务规则独立确认
6. **作业调度**：服务端时钟驱动的预约 / 验收提醒，发前再校验当前状态 / 时间 / 接收者权限
7. **失败审计**：失败另写 `repair_action_failures` 追加式表

### 5.3 结果核验（Verification）

- **数据库回读**：所有断言走真实 SELECT；状态 / 版本 / 事件 / 回执 / 预约 / 完工 全部 SQL 核验
- **HTTP 端到端**：`backend/scripts/e2e_full_chain.py`（17 步 DRAFT → COMPLETED 含退回重做 + 幂等回放 + 终态开工被拒）
- **探针与回归**：
  - `runtime/repair-round2-20261002/probe_round2.py` V01-V11 + V08b（11/11 PASS）
  - `runtime/repair-round4-20261003/probe_round4.py` R3-01~R3-07（7/7 PASS）
  - `backend/tests/` 全量 pytest（424 passed）
- **手动核验**：每次写操作回读 `task.version` / `task.status` / `task.asset_id` / `events` / `receipts`

### 5.4 人工确认环节

| 操作 | 必须人确认 | 说明 |
|---|---|---|
| 提交草稿（DRAFT → OPEN） | 否（自动） | 必须选 service space |
| 接单 / 派单 | 否（自动） | 经理派单需合法技工 |
| 提议 / 确认 / 拒绝预约 | **是**（原报修人确认） | 报修人 `confirm_appointment` |
| 开工 | 否（自动，需 CONFIRMED 窗口内） | 时间外系统时钟强制 |
| 提交完工 | 否（自动，需 ≥1 条 READY 证据） | 证据完整性由后端校验 |
| **验收 / 退回** | **是**（原报修人 / 经理） | 必须给出 `reason` 才能退回 |
| 改派 | **是**（经理） | 必须有 `reason` |
| 取消 | **是**（报修人 / 经理） | 必须有 `reason` |
| 撤权后所有写 | **是**（系统拒绝） | 由后端 auth 守门 |

---

## 六、运行截图、日志或视频 + 复现步骤

| 资产 | 路径 / 命令 |
|---|---|
| 原生截图 | `app/bundle/screenshots/01-main.png`（来自 `card-host --bundle` 真实渲染） |
| 原生会话日志 | `runtime/repair-round2-20261002/native/{native_run,splash-probe,verify-wl}/host.log` |
| Web 主链（前端） | `runtime/review-round3-20261003/{web.log, web-*.json, web_runner.py}` |
| 端到端日志 | `runtime/repair-round4-20261003/` 本轮新增 R3 探针 + 历史 e2e.log |
| pytest 全量日志 | `pytest backend/tests/ -q`（424 passed in ~66s） |
| 修复报告 | `docs/build-loop/REPAIR_RESULT_2026-10-03_ROUND3.md`（R2）+ `REPAIR_RESULT_2026-10-03_ROUND4.md`（R3） |
| 验证报告 | `docs/build-loop/REPAIR_VERIFICATION_2026-10-03_ROUND3.md` |
| 排期 / 差异 | `docs/implementation/12_DELIVERY_PLAN_20261009.md` |
| 课程 #2 对照 | `docs/implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md` |
| 13 Hub 边界 | `docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md` |

### 复现步骤（评审可独立运行）

1. 拉取仓库到独立工作区
2. `cd backend && uv sync --frozen`
3. `python3 scripts/verify_migration.py` —— 基线哈希全过
4. `backend/.venv/bin/python backend/scripts/e2e_full_chain.py` —— E2E 17 步全过
5. `backend/.venv/bin/python -m pytest backend/tests/ -q` —— 424 passed
6. `backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py` —— V01-V11 + V08b
7. `backend/.venv/bin/python runtime/repair-round4-20261003/probe_round4.py` —— R3-01~R3-07
8. 原生 bundle 用 `card-host --bundle app/bundle --allow-unsigned` 加载（详见 §三）；`set_visible/on_render` 缺口见 `app/docs/round4_native_probe.md`

---

## 七、与 OctoSense 12 场景对应

| 官方场景 | 是否接入 | 说明 |
|---|---|---|
| 邮件 / 即时消息 | ❌ 否 | 通知用站内 `repair_notifications`，不连 Rinx Matrix |
| 日历 | ❌ 否（仅预约窗口） | 用 `repair_appointments` 内部日历 |
| 天气 | ❌ 否 | 不在范围 |
| 新闻 | ❌ 否 | 不在范围 |
| 音乐 / 视频 | ❌ 否 | 不在范围 |
| 行情 / 导航 | ❌ 否 | 不在范围 |
| 购物 / 物流 | ❌ 否 | 设备服务关系 (`repair_asset_services`) 提供接口；接入外部系统按后续 G4 排期 |
| **写作 / 创作** | ✅ **核心** | `problem_text / preferred_window / completion_text / record_progress.note / pin` |
| **系统 / 设备** | ✅ **核心** | 设备身份 / 空间服务关系 / 隔离存储 |
| **生产力** | ✅ **核心** | 工作台 + 命令边界 + 状态机 |

主场景明确：**写作 / 创作 + 系统 / 设备 + 生产力**。

---

## 八、当前状态与未达成项（透明披露）

| 项 | 状态 | 来源 |
|---|---|---|
| Python 后端 424 测试 | ✅ PASS | `pytest backend/tests/` |
| R3-01 ~ R3-07（八项 R3 中前七项） | ✅ PASS | `runtime/repair-round4-20261003/probe_round4.py` |
| 原生 picker / set_visible / on_render | ⚠ BLOCKED | 固定版本 card-host 缺口，按 §一硬约束禁止回退假元数据；addEvidence 已写 `ready:false` 占位 |
| Hub bundle digest REFUSED | ⚠ BLOCKED | 本轮改 `addEvidence` 后 bundle 字节已变；`manifest.json::integrity.bundle_blake3` 仍是旧 hub stamp 值 `c066a517…`；候选新 digest 见下表（须 `hub stamp` 重新打戳） |
| Hub 上架 | ⚠ NOT_RUN | Rinx 通用目录 / 包安装尚未接通（`app-hub-submission.md` §"Not yet available"） |
| 真实模型 / 官方身份 / 多客户端 | ⚠ NOT_RUN | `ACCEPTANCE.json` G0/T01/T25/T26/T33-T38 / U01-U12 —— 等用户授权 |
| 加密聊天（`octos.*` 服务） | ⚠ BLOCKED | 当前 `card-host` 不暴露 octos.* 服务（host policy `may_prompt=false`） |
| Rinx Matrix 外部账号（`@user:matrix.rinx.chat`） | ⚠ 外部能力 | 见官方 [`rinx-guide.md`](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/rinx-guide.md) —— 用户自行在 `https://auth.matrix.rinx.chat` 注册；本项目代码不依赖该外部账号 |
| 复赛完整 Agent 自动化演示 | ✅ 已展示（§五） | input → execute → verify → human confirm 全链 |
| `manifest.json` 闭集字段校验 | ✅ PASS | schema=1 / id∈`[a-z0-9.-]{1,64}` / short_id 不在 `RESERVED_NAMES` / capabilities=`["storage"]` ⊂ `KNOWN_CAPABILITIES`（严格解析 10/10 通过） |
| `listing.json` 闭集字段校验 | ✅ PASS | category=`productivity` / platforms=`["macos"]` / age_rating=`all` / license=`Apache-2.0` / icon+screenshot 存在 |
| `listing.json::publisher.privacy_policy_url` | ⚠ 占位 | 当前 `https://example.com/privacy`；按 §一硬约束禁止擅自替换，须 G0 由用户确认实际隐私政策链接 |
| `listing.json::publisher.support` | ⚠ 占位 | 当前 `https://example.com/support`；同上待 G0 |

### 8.1 候选新 `bundle_blake3`（待 `hub stamp` 重新打戳）

按 R3 §三授权限制，本地**不擅自覆盖** `app/bundle/manifest.json::integrity.bundle_blake3`；
仅记录本地计算结果供评审核对。`hub stamp` 写入的格式以官方工具为准。

| 方法 | digest 输入 | 候选值（hex64） |
|---|---|---|
| 旧值（待替换） | 历史 `hub stamp` 值 | `c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82` |
| A（本地拼接，排除 manifest 自身避免循环依赖） | `(rel_path + 0x00 + file_bytes)` 排序拼接的 blake3 | `9ecd88d45c153b1e11439f1460fdcf73769037c77c356e492303cf3931b2bc21` |
| B（单文件 blake3） | `main.splash` blake3 | `e3a935dd054304986e1a0e0761c70e821c3f739cb02baa2532237b7c24a4587a` |

`hub stamp` 实际签名格式请以 App Hub 工具为准；本地候选值仅作完整性参考。

---

## 十、自检（Hub gate 等价检查）

```text
1. Bundle 结构齐全：manifest.json / listing.json / main.splash / assets/icon.svg / screenshots/01-main.png
2. manifest.json：schema=1, id=[a-z0-9.-]{1,64}, version, name, integrity, capabilities, storage
3. listing.json：schema=1, subtitle≤80, description, category∈闭集, platforms≥1,
   age_rating∈闭集, privacy_policy_url=https, license=Apache-2.0
4. main.splash：OctoScript 合法语法，无 http(s) 外链（只走 {{assets}} 相对路径）
5. 文件类型：仅 .json / .svg / .png / .splash / .md / .txt
6. icon + 至少 1 张 screenshot 在 bundle 内被 listing 引用
7. integrity.bundle_blake3 由 `hub stamp` 写入；未手工改
8. capabilities 闭集：仅 `storage`（最狭权限）
9. 数据：合成夹具 + 真实业务流；不复制个人凭据
10. README 顶部包含 OctoSense 12 场景对应（§七）
```

参见 `app/docs/round4_native_probe.py` 的可执行检查。

---

## 附录 A · 与官方 hub 文档的对齐表

| 官方要求 | 本文位置 |
|---|---|
| [PUBLISHING.md](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md) "What an app is" | §二（脚本应用结构） |
| manifest schema 1 闭集 capability | §四 `capabilities = ["storage"]` |
| listing 必填字段 | §二 `app/bundle/listing.json` |
| 隐私处理 | §四 |
| 用户授权 / 拒绝 / 失败 | §四 |
| Agent 任务演示 | §五 |
| 截图 + 复现步骤 | §六 |
| [app-hub-submission.md](https://raw.githubusercontent.com/gosimfoundation/hackathon-agenticapp26/main/docs/app-hub-submission.md) §"所有作品需要的材料" | §一 ～ §六逐项覆盖 |

## 附录 B · 与本项目 R2 / R3 修复的对应

| 修复轮次 | 文档 |
|---|---|
| R2-01~R2-10 | `docs/build-loop/REPAIR_RESULT_2026-10-03_ROUND3.md` |
| R3-01~R3-07 | `docs/build-loop/REPAIR_RESULT_2026-10-03_ROUND4.md` |
| R3-08（原生宿主） | `app/docs/round4_native_probe.md` |
| 第三方独立复核 | `runtime/review-round3-20261003/` |