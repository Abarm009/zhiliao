# OctoSense Repair · 工程进度报告

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