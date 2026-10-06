# OctoSense Repair · 工程进度报告

## 2026-10-06 · 普通话视频、截图与仓库更新

用户选定第 3 号 Serena 温和女声。已完成 82 秒正式普通话视频及原创配乐，16 段对齐，全片解码通过；整理 7 张实际页面/原生截图、字幕、应用包和验证说明，集中于 [submission/2026-10-06](submission/2026-10-06/README.md)。根 README 更新为当前材料、运行和能力状态导航，旧业务源码与契约保留。

本轮后端 190 项单测通过（62.20s），17 步独立 HTTP E2E PASS。当前截图任务通过报修人页面验收为 COMPLETED；技工阶段通过本地 API 准备。原生 bundle 目录内备份已移入 runtime 保留，重新 stamp 后 hub check PASSED（unsigned）。台账仍 31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED，整体 NOT READY；迁移原始哈希检查显示 5 项既有变更，没有重写清单。GitHub 更新及远端回读另外记录，未创建 Hub Issue 或新增赛事回执。


**截至 2026-10-06 11:50 Asia/Shanghai（10-06 定版）**

> **2026-10-06 定版**：起 web 后端（8711）+ demo-web（8716），`backend/scripts/e2e_full_chain.py --base-url http://127.0.0.1:8711` 17 步 PASS（DRAFT→OPEN→ACCEPTED→bind_asset→PROPOSED→CONFIRMED/SCHEDULED→evidence READY→IN_PROGRESS→AWAITING round1→退回→AWAITING round2→COMPLETED→idempotent replay→终态开工被拒 422）。起 card-host（8728），原生 bundle 0.1.0 加载 48 个 widget（修后），第 4 个按钮（`+ 新建草稿`）实测产生真实 tasks.json / actions.jsonl / events.jsonl。证据文件 `runtime/live-20261006/recording/{octosense-repair-demo-20261006.mp4, web-flow.mp4, native-flow.mp4}`；截图 `runtime/live-20261006/recording/shots/{00-login, 01-reporter-final, 02-tech-final, 03-manager-final}.png` + `app/bundle/screenshots/{01-main, 02-after-draft}.png`。manifest blake3 已重新 stamp：`68aa7c59...`。后续 R3-08 原生 picker / on_render 仍为宿主平台缺口，已记录于 `app/docs/route-decision.md`，未伪装通过。

**截至 2026-10-02 01:30 Asia/Shanghai（含 10-02 全盘 review 改判）**

工程根目录：`/Users/abeam/一些尝试/知了OctoSense`

> **2026-10-02 全盘 review 结论**：只读代码审查 + 真实启动后端/demo-web/card-host + 浏览器三角色点击后，
> 9 项 PASS 被改判（T01→NOT_RUN；T02/T03/T05/T08/T16/T17/T18/T29→FAIL），
> 其中 5 项是 P0 级能力性缺陷。**问题清单、复现命令与修改建议见
> [docs/build-loop/REVIEW_2026-10-02.md](docs/build-loop/REVIEW_2026-10-02.md)**，
> 本轮记录见 [docs/VERIFICATION.md](docs/VERIFICATION.md)。
> 下文 10-01 的段落保留作历史证据，其数字以本节为准。

## 1. 当前状态总览

| 维度 | 状态 | 证据 |
|---|---|---|
| 后端单测 | **39 PASS**（11 核心 + 4 预约改派 + 23 扩展 + 1 dummy） | `backend/tests/octosense_backend/` |
| 端到端 curl | **13 步 PASS**（DRAFT→COMPLETED 含退回重做） | `backend/scripts/e2e_full_chain.sh` |
| 原生 UI 闭环 | **部分 PASS**：fs 持久化 + 重启回读 **仅对 state.json 成立**；TASKS 丢失；23 个声明节点只实例化 15 个（退回/重置/任务列表/状态行不存在） | REVIEW_2026-10-02.md R-P0-1 / R-P1-1 |
| bundle 准入 | **PASS**（octosense-repair 0.1.0） | `hub check`（仅 publisher-signature unsigned warning） |
| 迁移基线 | **PASS**（1 处故意修改） | `python3 scripts/verify_migration.py` |
| 设计包 | **PASS**（仅文档结构，不验代码） | `python3 docs/implementation/verify_pack.py` |
| ACCEPTANCE | **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED** | `docs/build-loop/ACCEPTANCE.json` |
| 检查器 records | **VALID** | `python3 scripts/check_build_loop.py` |
| 本地就绪门 `--ready` | **NOT READY**（35 项本地未过） | `python3 scripts/check_build_loop.py --ready` |
| 继承基线测试 | **FAIL**：219 pass / 1 fail / 49 无法收集 | `backend/.venv/bin/python scripts/test_baseline.py` |

## 2. 已通过的验收项（24 / 64）

**G0 基础设施**
- G0-A 固定版本、原生脚本构建与真实启动（注：3 张截图是 L0 三按钮版，与当前 15 按钮 main.splash 不同版本，见 R-P2-4）
- G0-C 唯一事实源 + 原子一致性（WAL + foreign_keys + BEGIN IMMEDIATE）

**T 业务核心（15 项）**

| 类别 | 已 PASS |
|---|---|
| 报修与提交 | —（T01/T02/T03 已改判，见 §2.1） |
| 接单与改派 | T04 / T06（T05 已改判） |
| 设备 | T07 / T09（T08 已改判） |
| 预约 | T10 / T11 / T12 / T14（T13 NOT_RUN、T17 已改判） |
| 版本/幂等 | T15（T16 已改判） |
| 权限/隔离 | —（T18 已改判） |
| 证据 | T19 |
| 完工/验收/退回 | T20 / T21 / T22 |
| 外部工单 | T27 |
| 原生 | T28（T29 已改判） |
| 收藏 | T30 |
| 取消 | T31 |

**P 发布**
- P01 / P02 / P03 / P04 / P05：scan / stamp / check / 已知缺陷 / 包摘要
  （注：P02/P04/P05 引用的截图与 DB 证据存在版本不匹配与空心化问题，见 R-P2-4）

### 2.1 已改判项（原为 PASS，2026-10-02 review 后降级）

| ID | 原 | 新 | 一句话原因 |
|---|---|---|---|
| T01 | PASS | NOT_RUN | 未接真实模型，草稿由 HTTP body 直建 |
| T02 | PASS | FAIL | 同 key 不同内容返回 201 而非 409 |
| T03 | PASS | FAIL | 跨项目可写；`space_id` 不校验 |
| T05 | PASS | FAIL | 跨项目角色可接单；无技能匹配 |
| T08 | PASS | FAIL | 无 `asset_serves` / 服务关系模型 |
| T16 | PASS | FAIL | replay 不返回 `action_id` |
| T17 | PASS | FAIL | 无 SSE 端点 |
| T18 | PASS | FAIL | `GET /tasks/{id}` 无授权校验 |
| T29 | PASS | FAIL | 无 grant 机制 |

依据与复现命令见 [docs/build-loop/REVIEW_2026-10-02.md](docs/build-loop/REVIEW_2026-10-02.md)。

## 3. 仍 NOT_RUN / FAIL / BLOCKED（29 + 8 + 3 = 40）

| 类别 | 编号 | 状态 | 原因 |
|---|---|---|---|
| 真实 LLM 接入 | T25 / T26 | NOT_RUN | G0-E 未做；UI 不冒充模型成功 |
| Jobs / scheduler | T13 / T23 | NOT_RUN | 依赖 Shell + deadline scheduler，未实现 |
| Pairing / host session | T32 | NOT_RUN | 依赖 Shell 编译；当前 demo 身份走 X-Actor-Id |
| Agent harness | T33-T38 | NOT_RUN | scoped_queries / intent_compiler / result_verifier 未做 |
| 真实人工 UI | U01-U12 | NOT_RUN | 需真人视觉/键盘/演示脚本；原生 UI 当前还有裁切与无声失败（R-P0-1 / R-P1-8），先修再验 |
| 撤回链详情 UI | 部分 U06 | NOT_RUN | 需真实重新启动后人工截图；原生侧任务根本不持久化（R-P1-1） |
| 系统助手 | G0-E | NOT_RUN | 系统助手 / AI host provider 未接入 |
| 提醒恢复 | G0-F | NOT_RUN | 依赖 jobs |
| 可信业务主体 | G0-B | NOT_RUN | host pairing + host session 未做 |
| 真实附件上传 UI | G0-D | NOT_RUN | 后端链路完整（上传/隔离/下载实测通过），UI 层附件选择/上传入口未做 |
| 旧写入口隔离 | T24 | NOT_RUN | 旧 `wagent_backend` 仍在树内，runner 写路径未在比赛模式禁用 |
| **本次 review 改判** | **T02 / T03 / T05 / T08 / T16 / T17 / T18 / T29** | **FAIL** | 见 §2.1 与 REVIEW_2026-10-02.md |
| **外部递交** | **P06 / P07 / P08** | **BLOCKED** | Hub Issue / 商店收录 / 赛事回执，**需用户明确授权** |

**口径修正**：BLOCKED 只有 3 项，且是 **P06/P07/P08（external，递交授权）**。
此前的"3 项 BLOCKED（T13/T23 jobs、T25/T26 LLM、T32 pairing）"写法把台账里的 NOT_RUN 误报成 BLOCKED，已纠正。

## 4. 关键文件与变更

### 后端（12 表 / 27 命令 / 29 应用路由）

| 文件 | 作用 | 行数 |
|---|---|---|
| `backend/src/octosense_backend/db/__init__.py` | 12 表 schema + 事务 | 233 |
| `backend/src/octosense_backend/commands/__init__.py` | 10 类核心命令（状态机 + 版本/幂等/事件） | 451 |
| `backend/src/octosense_backend/appointments.py` | 确认 / 拒绝 / 改派（3 类命令） | 239 |
| `backend/src/octosense_backend/extended.py` | 14 类扩展命令 | 598 |
| `backend/src/octosense_backend/api/__init__.py` | 29 应用路由（27 命令 + get_task + health） | 505 |
| `backend/src/octosense_backend/errors.py` | 17 类业务错误（`IdempotencyConflict` 当前不可达） | 134 |
| `backend/src/octosense_backend/seed.py` | 合成种子 | 85 |
| `backend/tests/octosense_backend/test_commands.py` | 11 单测 | 339 |
| `backend/tests/octosense_backend/test_appointments_reassign.py` | 4 单测 | 120 |
| `backend/tests/octosense_backend/test_extended.py` | 23 单测 | 280 |
| `backend/scripts/e2e_full_chain.sh` | 13 步端到端 | 110 |

### 原生 UI

| 文件 | 作用 |
|---|---|
| `app/bundle/main.splash` | 石墨工作台（声明 23 节点，运行时只实例化 15 个；fs 只持久化 STATE） |
| `app/bundle/manifest.json` | bundle 元数据（capabilities: storage） |
| `app/bundle/assets/icon.svg` | 应用图标 |
| `app/build/review.json` | hub scan 7 项 review |

### 文档

| 文件 | 状态 |
|---|---|
| `README.md` | 顶部改为 10-02 口径（24 PASS / 8 FAIL / 3 BLOCKED） |
| `app/README.md` | 启动 / 端到端复跑 / 已知限制升级 |
| `docs/build-loop/SUBMISSION.md` | 版本表 + PASS 列表 + 复跑命令更新 |
| `docs/build-loop/ACCEPTANCE.json` | 24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED |
| `docs/build-loop/REVIEW_2026-10-02.md` | **新增**：全盘 review 问题清单 + 复现命令 + 修改建议 |
| `docs/VERIFICATION.md` | 追加 10-02 review 记录 |
| `runtime/build-loop/iter-L2-to-L6.md` | 本轮迭代总结（含文件所有权 / 验证步骤） |
| `PROGRESS.md` | 本文件 |

## 5. 风险与未完成项（按 10/6 内部目标已偏危险）

1. **P0 五项未修**：原生 UI 半节点、跨项目可写、`get_task` 无授权、幂等不 409、**web 路径在 SCHEDULED 死锁**。其中第 5 项让浏览器演示无法走到完工，直接影响 10/8 递交的演示素材。见 REVIEW_2026-10-02.md §6 的修复顺序。
2. **真实模型接入**：必须用户配置并授权 provider；当前 `get_history_advice` 只返结构化聚合，不调 LLM（T01/T25/T26/G0-E）
3. **jobs / 提醒**：依赖 Shell + deadline scheduler，T13/T23 NOT_RUN
4. **真实人工 UI 验收**：U01-U12 不能用 mock 完成；且要先修 R-P0-1（裁切）与 R-P1-8（无声失败）才有东西可验
5. **继承基线测试已断**：`scripts/test_baseline.py` 收集期即失败，49 个继承测试不可运行（R-P2-6）
6. **Hub Issue 递交**：需要用户公开授权后才能创建（P06/P07/P08 BLOCKED）
7. **台账与代码漂移**：`commands/__init__.py` mtime 20:38 晚于最后一条 verified_at 18:10，无 iteration 记录（R-P2-5）

## 6. 复跑命令汇总

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# A. 单测
backend/.venv/bin/python -m pytest backend/tests/octosense_backend/ -q

# B. 端到端
OCTOSENSE_PORT=8713 OCTOSENSE_DB=/tmp/octosense.db \
  backend/.venv/bin/python /tmp/run_api.py > /tmp/octosense-e2e.log 2>&1 &
sleep 2
bash backend/scripts/e2e_full_chain.sh

# C. 原生 UI
HUB=runtime/native-build/OctoSense-App-Hub/target/release/hub
$HUB stamp app/bundle
$HUB check app/bundle --allow-unsigned
$HUB scan app/bundle --packet app/build/review.json
MAKEPAD_REMOTE=8155 $HUB/../../card-host \
  --bundle app/bundle --app-data /tmp/octosense-appdata --allow-unsigned --stamp &
curl -sS "http://127.0.0.1:8155/g?raw=1" -o /tmp/initial.png

# D. 检查器
python3 scripts/check_build_loop.py
python3 scripts/verify_migration.py
python3 docs/implementation/verify_pack.py
```

## 7. 已知缺陷（R-，编号与 REVIEW_2026-10-02.md 一致）

| ID | 项 | 级别 | 说明 |
|---|---|---|---|
| R-P0-1 | 原生 UI | P0 | 声明 23 节点只实例化 15 个；退回/重置/任务列表/状态行不存在 |
| R-P0-2 | 后端权限 | P0 | `_check_actor_role` 不按 project 校验，跨项目可写（影响 10 个命令） |
| R-P0-3 | 后端权限 | P0 | `GET /tasks/{id}` 无授权校验，任意 actor 可读全量 |
| R-P0-4 | 幂等 | P0 | 同 key 不同内容返回 201；`IdempotencyConflict` 与 `result='ERROR'` 均为死代码 |
| R-P0-5 | demo-web | P0 | `confAppt` 条件循环，报修人无法确认预约，web 路径在 SCHEDULED 死锁 |
| R-P0-6 | 授权 | P0 | 无 grant 机制，T29/G0-B/T32 均无实现对应物 |
| R-P1-1 | 原生 UI | P1 | TASKS 不落盘，重启丢任务；id 用 `TASKS.len()` 导致重复 |
| R-P1-2 | demo-web | P1 | `u-tech-2` 的 project 是字符串 `'prj-A & prj-B'`，登录即 403 |
| R-P1-3 | 后端 | P1 | `record_advice` 无幂等/权限检查，重复 key 返 500 |
| R-P1-4 | demo-web | P1 | `/task/{id}` 返回不存在的 `task.html` → 500 |
| R-P1-5 | demo-web | P1 | 6 处幂等键用 `Date.now()`，同毫秒互相顶包 |
| R-P1-6 | demo-web | P1 | `currentVer()` 从 DOM 扒版本号，取不到猜 1 |
| R-P1-7 | 后端 | P1 | 证据根目录默认 `Path.cwd()/runtime/evidence`，跟启动 cwd 绑定 |
| R-P1-8 | 原生 UI | P1 | 零权限控制；状态不匹配时按钮静默无操作；`nowMs()` 恒 0 |
| R-P2-1 | 契约 | P2 | schema 25 表 vs 实现 12 表；openapi 23 路径与实现零重叠 |
| R-P2-2 | 口径 | P2 | 命令数 25/27、表数 11/12、测试数 37/39 三处不符 |
| R-P2-3 | 口径 | P2 | BLOCKED 归属三份文档互相矛盾（已在本文件纠正） |
| R-P2-4 | 证据 | P2 | 17 项 PASS 引用同一旧 DB、8 项共用同组 4 文件；随包截图是 L0 版 |
| R-P2-5 | 流程 | P2 | 代码 mtime 晚于台账 verified_at，无 iteration 记录 |
| R-P2-6 | 基线 | P2 | `scripts/test_baseline.py` 失败，49 个继承测试不可运行 |
| R-P2-7 | 结构 | P2 | 缺 `app/docs/route-decision.md`、`runtime-versions.json`；色值 `#2A3A3C` 偏离冻结 `#223638`；仓库根有 `--app-dir` 垃圾文件；`EXTRA_SCHEMA` 死代码含错误外键 |

> 旧的 `D-T01-model / D-T13 / D-T23 / D-T25 / D-T26` 五条已由上面的 R- 编号取代。其中 T13/T25/T26 已并入对应 NOT_RUN 条目，不再单列缺陷——因为台账规则要求 PASS 行 `defects` 必须为空，把缺陷挂在非 PASS 行上才能被 `check_build_loop.py` 记录。

## 8. 下一步（10/2 - 10/7）

0. **先修 P0**（否则后面的验收没有意义）：R-P0-5 workbench 确认预约 → R-P0-1 splash 节点 → R-P0-2/R-P0-3 project 校验 → R-P0-4 幂等 payload hash → R-P1-1 splash 持久化。顺序与工作量见 REVIEW_2026-10-02.md §6。
1. **U01-U12 真实人工验收**：把脚本结构化测试 + 真实 fs 持久化转化为视觉/键盘/演示脚本化的人工测试，截屏存 `runtime/build-loop/u-shots/`
2. **hub Issue 准备**：完成递交正文草稿（待用户授权后再发布）
3. **Git 标签**：在工程根初始化 git（可选），准备 tag/SHA
4. **最终演示**：录 2-3 分钟演示视频（mp4 或多帧摘要）
6. **L7/L8**：打包准入与递交执行（按 [docs/implementation/15_BUILD_VERIFY_LOOP.md](docs/implementation/15_BUILD_VERIFY_LOOP.md) §7）

## 9. 截止时间表（10/6 晚 / 10/9 截止）

- **10/2 - 10/5**：U01-U12 视觉/键盘真实测试 + Hub Issue 草稿 + 演示素材
- **10/6 晚**：主要功能完成检查 + 冻结范围 + 形成候选包（10/1 的自评偏乐观，10/2 review 后有 5 项 P0 待修）
- **10/7**：独立验收 + 修复
- **10/8**：封包 + 优先递交 Hub Issue
- **10/9**：最终检查 + 提交回执

## 10. Token 用量

本会话实际 Token 用量：未知（M3 路由轮次级读数未暴露）。`runtime/build-loop/iter-L2-to-L6.md` 注明此点。
**2026-10-06 12:17 Asia/Shanghai（10-06 第二次定版 · UI 重做 + 视频）**

> **UI 重做（依据时间线 12:00-12:01）**：根据"按钮堆叠难看，竖屏太丑"反馈，重写 `app/bundle/main.splash` 视图段，从横向流按钮改为纵向移动 App 范式：Hero 头部（"维修协作"大标题 + 副标题）+ 当前身份 chips 分两行（3+2）+ 当前任务卡（含 📋 标识）+ 7 个 STEP 卡纵向流（每个 STEP 一个标题 + 描述 + 一行内联按钮）+ 状态行底部。配色调整：accent `#91D5BE` → `#7DD3B0` 更鲜亮，surface `#1A2628` → `#1F2D2F` 更暖，heroBg `#23393B` 新增。按钮样式统一圆角（12-14pt），主操作高 56pt、次操作 50pt、chips 42pt。bundle 重新 stamp，blake3 `e32bec5c...`。

> **完整报修流程演示视频（82 秒）**：`runtime/live-20261006/recording/octosense-repair-demo-final.mp4`（600 KB）—— 16 帧 1280×900，每帧 5-6 秒：标题卡 → 流程图 → 登录页 → 报修人工作台 → 状态机：DRAFT→OPEN → 技工列表 → 接单 → 绑设备+提议预约 → 经理视角 → 确认预约→SCHEDULED → 完工提交+独立验收 → 退回重做 → 二次验收 → 原生 bundle 启动 → 原生新建草稿 → 结束。旁白脚本见 `runtime/live-20261006/recording/NARRATION_SCRIPT.md`（含每帧解说文本与完整旁白脚本），可送任意 TTS 模型生成音频后重新合成。

> **未交付**：每张截图配套的语音解说（Chrome 在尝试 CDP 自动化时挂死、ffmpeg avfoundation 录屏格式不支持；旁白脚本已写但未合成音频）。如下次需要音频版本，把 `NARRATION_SCRIPT.md` 喂给任何 TTS 服务（如 Edge-TTS / ChatTTS / 火山引擎）即可生成对应音频，再用 ffmpeg 与现有 mp4 合并即可。

> **2026-10-06 13:06 清理**：按用户要求删除 22 秒短视频 `octosense-repair-demo-20261006.mp4`；同步清掉已废弃的初版 `octosense-repair-demo-v2.mp4`、老的 `web-flow.mp4`/`native-flow.mp4`、与 final 重复或调试用的 `01-reporter-workbench.png`/`04-reporter-detail.png`/`test-shot.png`、空目录 `frames-correct/`、录制过程脚本 `_auto_login.html`/`drive_demo.py`/`drive_flow.py`/`shoot_states.py`/`build_states.py`/`build_video.py`。`recording/` 现仅保留 4 项交付物：`NARRATION_SCRIPT.md`、`octosense-repair-demo-final.mp4`（82 秒 615 KB）、`shots/` 里 4 张被 final 实际引用的截图、`frames/` 帧源（可复现）。所有删除走 `mavis-trash` 可恢复，未触及工程其他位置。

**2026-10-06 22:15 Asia/Shanghai（10-06 第三次定版 · B 版原生候选）**

> **N1/N2 根因定位 + 修复**：通过最小探针确认 N1 根因是固定版本 card-host 不实例化 ScrollYView 被裁剪的子节点，且 `fn tick()` 缺失；N2 根因是用户定义 `pick(list, id)` 与 Octoscript 内置 `pick(object, ...)`（`octoscript-core/src/lib.rs:3847`）同名、用户定义 `me()` 与 Octoscript 内置 `me`（`octoscript-core/src/lib.rs:6813`）同名，导致 call site 解析到 builtin 包装而不是用户函数体。修复：取消 ScrollYView 改为单页紧凑布局（main.splash 从 1002 行 → 956 行）、新增 `fn tick()` 1Hz 重算 status_line/facts_line、`pick` 重命名为 `pickUser`、`me` 重命名为 `getMe`，所有 21 处 call site 同步改名；引入 `refreshLabels(taskToShow)` 辅助函数在每个 click handler 末尾主动更新命名 Label，规避 tick 跨 isolate 读到陈旧 STATE/TASKS 的问题。备份原版 `runtime/build-loop/main.splash.before-redesign.bak`。
>
> **真实原生闭环验证**：用真实 card-host（Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc）加载 B 版 main.splash，按以下顺序真实点击：DRAFT→OPEN（报修人提交）→ACCEPTED（技工接单）→SCHEDULED（报修人确认预约 now+10s/+20min）→IN_PROGRESS（技工开工 + 记录处置 + addEvidence demo）→AWAITING_ACCEPTANCE（提交完工）→COMPLETED（报修人独立验收）。状态条/任务卡/事实条在每一步实时刷新；`kill card-host && 重启` 后从 `state.json`/`tasks.json`/`actions.jsonl`/`events.jsonl` 完整回读。6 张截图存档 `runtime/build-loop/native-screens/01..06-*.png` 并复制到 `app/bundle/screenshots/b01..b06-*.png` 与 `submission/2026-10-06-native/screenshots/`。
>
> **bundle 准入重跑**：hub stamp → `1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca`；hub check → `octosense-repair 0.1.0 — PASSED`（仅 publisher-signature unsigned warning）；hub scan → packet 7 项问题逐条答复，route = pass。完整日志见 `runtime/build-loop/b-stamp-check/`。B 版 ZIP `submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip` 1.5 MiB，SHA256 `13e6e5fa086ab08dea42cd49b9edb8fdaf374a77fb7975750455228f9ddafd52`。
>
> **回归证据**：后端 `pytest backend/tests/octosense_backend/` → **190 passed in 63.70s**；`python3 scripts/verify_migration.py` → 5 项 Changed（已知差异，来源已说明，不重写 hash 清单）；`python3 scripts/check_build_loop.py` → VALID RECORD STRUCTURE，31 PASS / 28 NOT_RUN / 2 FAIL / 3 BLOCKED。ACCEPTANCE.json 台账结构验证通过，但业务测试按约定不由该检查器执行。
>
> **B 版独立交付目录**：`submission/2026-10-06-native/` 含 README.md / VERIFICATION.md / KNOWN_LIMITATIONS.md / SOURCES.md / HUB_ISSUE.md（待用户授权后发出）/ HOST_NOTE.md（待用户授权后发出）/ SHA256SUMS / bundle/ / screenshots/ / check/。A 版材料 `submission/2026-10-06/` 未动；根 README / PROGRESS 已加 A/B 两版对照。
>
> **状态口径**：构建成功 ✓（stamp/check/scan 通过） · 原生验证通过 ✓（真实宿主跑通主路径，6 张截图） · 已递交 ✗（App Hub Issue 待用户授权后发出） · 已收录 ✗（未到 Hub catalog 收录阶段）。**不把「stamp PASSED」说成「原生闭环验证」、不把「构建成功」说成「Hub 收录」**。
>
> **未冒充通过**：App 文件选择器（宿主 API 缺失，addEvidence 写入 demo 占位）、隔离存储读字节 API（脚本可写不可读字节）、grant 申请/关闭/到期路径（仅声明 capabilities，无 UI 面板）、真实模型接入（compute.agent=null）、多次 setActor 后按钮位置下移（宿主布局 API 不稳定）。每条最小复现与影响见 `submission/2026-10-06-native/KNOWN_LIMITATIONS.md`。
>
> **下一步（待用户授权）**：冻结 B 版 commit + tag `octosense-repair-b-v0.1.0` → 推 origin `Abarm009/zhiliao` → 在 [OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub) 创建 `Submit octosense-repair 0.1.0-b` Issue（正文草稿见 HUB_ISSUE.md）→ 发出主办方进展说明（HOST_NOTE.md）。当前 working tree 含未提交改动（main.splash / manifest.json / listing.json + 6 张新截图）；提交 + 推送需用户明示。

**2026-10-06 23:50 Asia/Shanghai（10-06 第四次定版 · review 反馈修复后）**

> **Review 来源**：用户独立完成的 B 版原生审查，写入 `docs/build-loop/REVIEW_NATIVE_B_2026-10-06.md`（结论「能够启动并演示状态流；完整原生验收 FAIL，最新宿主兼容性未验证」）。共 6 项：B-R01 ~ B-R06。
>
> **修复结果**（4 项代码修复 + 2 项文档修正）：
> - **B-R02 修复**：runCommand 计算 `hit = receiptFor(...)` 后没用、删除 conflict 拒绝与 hit 回放 → 恢复路径。同时修了一个**自引入 bug**：初版用 `if hit.hit {}` 字段访问，Octoscript 编译器报 `property hit not found in prototype chain. Did you mean: miss(true)`（与 N2 同类的 builtin 遮蔽问题）；改用 `found.kind == "hit"` 字符串比较后恢复。13 个 runCommand 调用（confirmDraft / acceptTask / bindAsset / submitCompletion 等）再次可执行。
> - **B-R03 修复**：`logEvent` 用 `fs.append` 逐行写（JSONL 多行）但 `load()` 一次 `parse_json` 当 JSON 数组解析 → 多行 JSON 不是合法 JSON，EVENT_LOG 保持空。改为 `saveEvents()` 整体重写 `EVENT_LOG.to_json()`，load 一次 parse_json。重启 9→9 events 完全恢复（review 前是 0）。
> - **B-R01 修复**：`addEvidence` 之前写 `bytes:1024, sha:"demo-sha", ready:true`，让伪占位蒙混证据门槛、submitCompletion 放行、DRAFT→COMPLETED 闭环被伪造。改为 `bytes:0, sha:"", ready:false, demo:true` + `note` 标注，submitCompletion 检查 `readyCount(t) < 1` 直接拒绝，task.status 保持 IN_PROGRESS。状态条「拒绝：完工前必须至少有一份可读证据」。**不再假装完整闭环**。
> - **B-R05 修复**：`setActor` 强选 selectedIdx=0 + `refreshLabels` 不查 visible，导致「报修人二」看到「报修人一」的草稿卡。改为 `firstVisibleIdx()` / `stepVisible(from, dir)` + `refreshLabels` 检查 visible。切身份后显示「无可见任务」label 自动空态。
> - **B-R04 文档修正**：本机 card-host mtime 2026-10-01，上游 App Hub main（`78dfda5f`）/ OctoSense main（`4081c30e`）与本机 lockfile 存在 commit 差异；**删除「最新 OctoSense 已验证」表述**，保留「固定旧宿主候选（Hub@6741dea lockfile）」口径。
> - **B-R06 文档修正**：
>   - `manifest.version` 改为 `0.1.0-b`（之前是 `0.1.0`，与 B 版标识不符）
>   - SOURCES A 版 digest 从错的 `23e56ea0...` 改为真实值 `eff13f557080fc12ac2961f6bee83a2365f3d8fb5ac0e56681cee45b13c4ad26`（从 commit `6d81d57b:app/bundle/manifest.json` 验证）
>   - README 复跑命令从 `cd /tmp/.../bundle && 相对路径调用宿主` 改为「`$PROJECT_ROOT/runtime/native-build/.../card-host --bundle 绝对路径`」，原命令在用户目录下 cd 后找不到 host binary
>   - VERIFICATION 删除「回执原 action_id」「重启事件不变」「scan 三关全部通过」等夸大 PASS；scan 改为「packet 7 项由发布者自己答复，route=pass；不是独立 reviewer 通过」
>
> **真实宿主验证**：
> - **B-R01**（via 合成 tasks.json）：合成 SCHEDULED 任务（appt.startMs=now-5s）→ 启动 card-host → 加载成功 → 切「技工甲」→「开工」→「记录处置」→「上传证据」→ `evidence[0]={bytes:0, sha:"", ready:false, demo:true}` → readyCount=0 → 「提交完工」被阻断、状态条「拒绝：完工前必须至少有一份可读证据」、task.status 保持 IN_PROGRESS。证据存档 `/tmp/zhiliao_b_v6-b-r01.json` + `screenshots/12-b-r01-evidence-demo.png` + `screenshots/13-b-r01-completion-blocked.png`。
> - **B-R02**：host log `[E]` 错误数 = 0；DRAFT→OPEN 真实点击跑通。
> - **B-R03**：合成 9 events + 8 receipts + 1 SCHEDULED task → kill card-host → 重启（指向同 `--app-data`）→ events 9→9 / receipts 8→8 / task 1→1 完全恢复。证据存档 `/tmp/zhiliao_b_v6-b-r03.json` + `screenshots/14-b-r03-after-restart.png`。
> - **B-R05**：切「报修人二」后 label 含「无可见任务」、facts_line「任务 1 条（可见 0）」。截图 `screenshots/10-reporter2-no-visible.png`。
> - **B-R05「开工 scheduler timing 限制」**：从 SCHEDULED → IN_PROGRESS 在自动化测试中 wait 75s + 10 次 retry 仍被 `nowMs() < appt.startMs` 拒绝（review 已知）。改用合成 tasks.json 直接进入 IN_PROGRESS 验证 B-R01。
>
> **重新打 ZIP + 更新 SHA256SUMS**：
> - stamp blake3 = `ab69db47a2888dba9d5303a68c2f791097c0249ec9a08c56e328fec56bc89b49`
> - ZIP `submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip` 1.5 MiB（21 项 SHA256 写入 `submission/2026-10-06-native/SHA256SUMS`，含 zip / 14 张截图 / 2 个 probe JSON / 4 个 bundle 源文件）
> - probe 证据复制到 `submission/2026-10-06-native/check/probe-results-b-r01.json` + `probe-results-b-r03.json`
>
> **submission/2026-10-06-native/ 现状**：13 张原生截图（A 版 6 + B 版 review 后 7 + B-R01/03 修复 2）+ 7 份文档 + ZIP + check 三关日志 + probe 证据 + SHA256SUMS。所有文档按 review 反馈修正：A 版 digest 正确、manifest 版本号对齐、复跑命令用绝对路径、删除「最新 OctoSense 已验证」「scan 三关全部通过」等夸口。
>
> **状态口径**（review 后修正）：
> - **构建成功**：stamp `ab69db47...` + check `octosense-repair 0.1.0-b — PASSED` + scan packet 7 项自答 route=pass
> - **原生验证通过**：DRAFT→OPEN→ACCEPTED→SCHEDULED 真实点击跑通；IN_PROGRESS 经合成 tasks.json 验证；B-R01/B-R02/B-R03/B-R05 修复全部经真实宿主验证
> - **不冒充**：不开工到 COMPLETED（picker 缺失 + scheduler timing 让闭环停在 submitCompletion）；不声称「最新 OctoSense 已验证」（上游 main 与本机 lockfile 存在 commit 差异）
> - **待递交**：App Hub Issue 草稿在 `submission/2026-10-06-native/HUB_ISSUE.md`，**未经用户授权不发出**
> - **未收录**：Hub catalog 未收录

**2026-10-07 00:50 Asia/Shanghai（10-06 第五次定版 · recheck 收尾）**

> **Recheck 来源**：用户独立完成的修复后独立复验，写入 `docs/build-loop/RECHECK_NATIVE_B_2026-10-06.md`（结论「能启动；新建数据下部分修复有效；旧数据升级仍 FAIL」）。4 项遗留问题处理结果：

> - **P0 旧版假 READY 附件（修复）**：旧 demo 数据 `bytes:1024, sha:demo-sha, ready:true` 加载时由 `scrubLegacyEvidence()` 检测并改为 `bytes:0, sha:'', demo:true, ready:false`，立即 `saveTasks()` 覆盖。实测：`runtime/recheck-native-b-legacy-20261006/data/octosense-repair/tasks.json` 含旧 demo 证据，加载后 evidence 全部清洗为非 ready，不再让 submitCompletion 蒙混。
> - **P1 旧 JSONL 多行（修复，承认限制）**：`loadJsonlLines` 整体 parse 失败时（旧 JSONL 不是合法 JSON 数组），备份原文件到 `events.jsonl.legacy.<ts>.bak`，events.jsonl 写 `[]`。**承认限制**：Octoscript `text.index_of` / `text.slice` 在 bytes-typed text 上行为不一致，`for x in text` 也无法逐行迭代，所以**无法在脚本内做行切分恢复**。备份文件保留全部原始 9 条事件供人工恢复；状态条明确告知「JSONL 旧格式不兼容：已备份 events.jsonl.legacy.<ts>.bak（旧 9 条事件需人工迁移或放弃）」。新数组格式 9→9 重启恢复已通过。
> - **P1 文档统一（已修）**：所有 stamp hash 同步到 `1e1912a421751881bd9f63b51791a9552cec86c631c5f737d0224607b88a0b96`；A 版 digest `eff13f55...` 已在 SOURCES 修正；README 不再有「最新 OctoSense 已验证」「完整闭环通过」等表述；B-R01 addEvidence 描述与代码一致；scan packet 7 项答复保持「由发布者自答 route=pass；不是独立 reviewer 通过」的口径。
> - **P1 幂等仅部分关闭（承认限制）**：runCommand 的 hit/conflict 分支代码已恢复，但 UI 路径每个命令函数 `LAST_KEY = newId()` 在 runCommand 之前——意味着 UI 路径下 receiptFor 永远返回 miss，hit/conflict 分支不会被 UI 触发。**承认**：代码逻辑按 kind 字符串判定已 work；但要验证这两个分支需要外部 client 用稳定 key 调用 runCommand。动态复用 key 验证未做（review 第 4 项的 NOT_TESTED 状态）。

> **真实宿主验证（recheck 后）**：
> - 旧 demo 证据加载：`/tmp/zhiliao_recheck_legacy_v2/` 用 review 留下的 legacy tasks.json 启动新版 card-host → evidence `bytes=1024, sha:demo-sha, ready:true` 全部 scrub 为 `bytes:0, sha:'', demo:true, ready:false` ✓
> - 旧 JSONL 多行加载：手工构造 9 条 JSONL dict → 启动新版 card-host → events.jsonl 被备份为 `events.jsonl.legacy.1791300861952.bak`（完整 9 条），原文件覆盖为 `[]` ✓
> - stamp / check / scan：blake3 = `1e1912a4...`；check `octosense-repair 0.1.0-b — PASSED`；scan packet 7 项自答

> **submission/2026-10-06-native/ 现状（recheck 后）**：
> - 27 项 SHA256SUMS（含 14 张截图 + 3 个 probe JSON + 3 个 check 日志 + ZIP + 4 个 bundle 源文件）
> - ZIP `bundle/octosense-repair-0.1.0-b.zip` 1.5 MiB（sha256 `1b911b60d5160b4273d3007b9f75f427815da2f500f02aeb8bf536c3bab86b40`）
> - 3 份 probe 证据：`probe-results-b-r01.json` / `probe-results-b-r03.json` / `probe-results-b-idempotent.json`
> - SOURCES §8 时间线更新到 recheck 全部动作；VERIFICATION §4 加旧数据兼容表；KNOWN_LIMITATIONS 加 L1 修复后行为

> **状态口径（recheck 后修正）**：
> - **构建成功**：stamp `1e1912a4...` + check PASSED + scan 7 项自答 route=pass
> - **原生验证通过**：新建数据 DRAFT→OPEN→ACCEPTED→SCHEDULED 真实点击跑通；旧数据加载不再被旧 demo 证据 / 旧 JSONL 蒙混；submitCompletion 在无真实附件时被阻断
> - **不冒充**：不开工到 COMPLETED（picker 缺失 + scheduler timing）；不声称 UI 路径已验证 hit/conflict 分支（UI 不可达，需外部 client）
> - **旧数据**：旧 demo 证据 load 时自动清洗 + 旧 JSONL load 时备份迁移；不再假装兼容
> - **待递交**：App Hub Issue 草稿在 HUB_ISSUE.md，**未经用户授权不发出**
> - **未收录**：Hub catalog 未收录
