# 接力交接：下一轮要修什么、怎么复跑、别踩什么坑

日期：2026-10-02。上一轮：`docs/build-loop/REPAIR_RESULT_2026-10-02_ROUND2.md`（V01–V11 逐项证据）。

---

## A. 已改完并验证通过（不要重做）

### A1. 后端领域与 API（V02/V03/V04/V05/V06/V07/V08/V09/V10）

新增四个基础模块，**所有命令都走同一边界**：

| 文件 | 作用 |
|---|---|
| `backend/src/octosense_backend/paths.py` | `find_project_root()` 向上找工程标记；`default_db_path()`/`default_evidence_root()` 显式环境变量优先 |
| `backend/src/octosense_backend/authorization.py` | `task_visible()` / `narrow_role()` / `can_see_contact()` / `skill_matches()` / `technician_ok()` / `service_relation_ok()` |
| `backend/src/octosense_backend/idempotency.py` | `fingerprint(command,actor,project,task,expected_version,params)` / `check_replay()` / `record_receipt()` / `record_failure()` / `strict_positive_int()` |
| `backend/src/octosense_backend/jobs.py` | 持久化提醒作业；`run_due_jobs()` 只写站内通知，**不**自动验收/开工 |

命令边界模板在 `commands/__init__.py::CommandExecutor._run()`：
幂等 → 授权 → 源状态 → 写 → `repair_actions`（`result_json` 存完整原响应）；
失败另写 `repair_action_failures` 追加审计，不会把失败留成成功回执。

新增表：`repair_completions`、`repair_appointments`、`repair_evidence`、`repair_pins`、
`repair_advice`、`repair_asset_services`、`repair_jobs`、`repair_notifications`、
`repair_action_failures`；`repair_tasks.category`、`repair_actions.result_json`。
迁移在 `db/__init__.py::init_schema()`，幂等 ALTER。

### A2. 测试（假阳性已修）

- `backend/tests/octosense_backend/world.py`：`ok()/okd()/expect_error()/task_row()`，
  **每步铺垫都断言成功并回读数据库事实**；`World` 提供 draft/open/accepted/propose/confirm/
  start/evidence/complete/accept_finish/reject_finish 链。
- `test_commands.py`(37) / `test_appointments.py`(20) / `test_appointments_reassign.py`(9) /
  `test_extended.py`(53) / `test_http_api.py`(22) = **141 项新回归**。
- 全量 `backend/.venv/bin/python -m pytest backend/tests/ -q` → **375 passed**。
- 继承测试的 `from conftest import stream_of` 名称碰撞已修：helper 移到
  `backend/tests/_baseline_helpers.py`，`pyproject.toml` 加 `pythonpath = ["tests"]`；
  `test_mcp.py` 一处过期断言（“汇金广场”→“示范广场”）已按当前种子事实修正。

### A3. 验收脚本不再是假阳性

- `runtime/repair-round2-20261002/probe_round2.py`：**任一断言失败 exit 1**；11 项覆盖 V02–V11。
- `backend/scripts/e2e_full_chain.py`：读 `--base-url`/`OCTOSENSE_BASE_URL`，自带空闲端口 +
  临时库 + 明确时钟；HTTP 失败即终止；末段断言最终状态/回执/两轮完工/附件字节/预约/事件。
  **旧的 `e2e_full_chain.sh` 不要再跑**（固定 8713、curl 不以 HTTP 失败退出）。

### A4. 原生交付件 V01 的一半

`app/bundle/main.splash` 已重写：0 解析错误、`view=true`、`admitted`，
点击"新建草稿"后宿主隔离存储 `tasks.json / actions.jsonl / events.jsonl` 实测写入。
`app/docs/route-decision.md` 记录了路线裁决（路线 A：事实在应用自有存储；**不**把本机
Python 服务塞 Hub 包，**不**自行转公网）。

---

## B. 还剩什么（按优先级）

### B1.【阻断】固定版本 card-host 的 OctoScript 编译缺陷 → 原生动作按钮无法按角色隐藏

实测失败（日志在 `runtime/repair-round2-20261002/native-*/host.log`）：

1. `ui.x.set_visible(false)` **不触发重排**（隐藏控件仍占位，截图尺寸不变）；
2. `on_render` **不实例化子控件**（闭包里 emit 的 Label/Button 一个都不出现）；
3. `const X = "..."` 不产生可见绑定 → 必须用 `let`；
4. `ok` 是保留字（try/ok 块）→ 不能做变量名；
5. fn 内跨声明顺序调用另一个 fn → `call target is not a function (got nil)`；
6. 对象字面量里嵌套对象字面量（`{a: {b: 1}}`）→ 所在函数解析为 nil；
7. `c ? a : b` 三元**不支持**；`string` 没有 `.hash()`/`.substr()`；`fn` 不能当对象 key（写 `"fn"`）；
8. `ui.<handle>` **只在事件回调里可解析**，顶层 eval 里调用直接失败。

当前规避：动作按钮统一展示，**分发层守门**（`runCommand()`：可见性 + 源状态 + 身份矩阵 + 幂等）。
这满足"不允许未授权操作成功"，但**不满足**"按角色隐藏按钮"。

**下一步**（任选其一，然后重跑 B3 的 D）：
1. 在 `runtime/native-build/OctoSense-App-Hub` 换/升到修复 1/2 的构建；
2. 宿主侧修 `View::script_call` 的 `render` 路径与 `set_visible` 的重排；
3. 改用 `PortalList` 之类原生列表控件承载动作行。

### B2.【未接通】真实模型 / 宿主身份 / grant / pairing

- T01/T25/T26/T33–T38、T29/T32：依赖用户授权 provider 与宿主 session，**保持 NOT_RUN，不要标 PASS**。
- Web/API 侧三独立会话的角色隔离**已完成**（不同 actor + 服务端授权矩阵 + 三条独立 DB 连接抢单只一人成功）。

### B3.【未接通】原生 SSE / 站内通知 / 关闭重开回读自测

- 后端已有：`GET /api/octosense/v1/events/stream`（SSE，游标续传，游标过旧全量刷新）、
  `GET /events?since_seq=`、`POST /jobs/tick`、`GET /notifications`。
- 原生侧未接。`runtime/repair-round2-20261002/native_verify.py` 已写好（真实点击 →
  回读宿主存储 → 关进程 → 同 app-data 重开 → 比对任务/版本/完工轮次），**只差 B1 修好即可跑通**。

### B4.【未做】U01–U12 真人 UI 验收、T24 旧入口统一边界、P06/P07/P08 外部递交

- U01–U12 需要真人，不由模型冒充。
- T24 依赖"比赛模式图怎么写 /reset 不可用"的定义，需先与用户确认再动 runner/MCP。
- P06/P07/P08 外部递交需用户授权；本地候选包材料已可生成。

---

## C. 复跑命令（原样可跑）

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# C1 全量测试（应 375 passed）
backend/.venv/bin/python -m pytest backend/tests/ -q

# C2 独立验收探针（应 11 pass / 0 fail，任一失败 exit 1）
backend/.venv/bin/python runtime/repair-round2-20261002/probe_round2.py \
    --json runtime/repair-round2-20261002/probe_round2.json

# C3 端到端（应 E2E PASS，17 步）
backend/.venv/bin/python backend/scripts/e2e_full_chain.py

# C4 原生（副本 bundle + 独立 app-data；当前卡在 B1）
backend/.venv/bin/python runtime/repair-round2-20261002/native_verify.py

# C5 记录检查器（只检查记录结构，不执行应用测试）
python3 scripts/check_build_loop.py
python3 scripts/verify_migration.py
python3 docs/implementation/verify_pack.py
```

零参启动与显式配置启动见 `REPAIR_RESULT_2026-10-02_ROUND2.md` §7。

---

## D. 下一轮的硬约束（沿用）

1. **不许改弱验收标准**。已发现旧基准错误：T12 断言 ACCEPTED 是错的（需求要求保留 SCHEDULED）；
   Q06 把 `asset:AC-001` 当正确载荷（正确是 `asset:<asset_id>`）。发现 T07/T09/T10/T12/T20/
   T21/T28 等旧 PASS 结论有误时，**先撤销错误结论再按真实修复逐项恢复**。
2. **不许伪造**：真实模型/宿主不可用时保持 NOT_RUN/FAIL/BLOCKED，不把假模型成功当真实通过；
   不用 mock 冒充；不删旧代码、旧验收项、他人修改。
3. **不改用户的模型配置**，不擅自换供应商或付费渠道，不公开发布/推送/发消息/提交赛事/买额度。
4. 每个稳定阶段更新 `docs/build-loop/REPAIR_RESULT_2026-10-02_ROUND2.md` 与本文件，
   并重新生成 `runtime/repair-round2-20261002/source-sha256-round2.json`。
5. 迁移只在旧库副本上验证，保留备份；`verify_migration.py` 退出 1 就如实记录差异，
   不写"通过"。

---

## E. 当前冻结状态

- 源码哈希：`runtime/repair-round2-20261002/source-sha256-round2.json`（24 个文件）。
- Hub 包：`app/bundle/` 未被 `--stamp` 改写（只在副本打戳）；原包 digest 与实际不符是 V01 的
  REFUSED 根因，重新生成后见 `runtime/repair-round2-20261002/native-check/*/host.log`。
- 进程/端口：本轮所有 uvicorn / card-host 均在脚本结束时自行关闭，无常驻进程。
- `check_build_loop.py`：`VALID RECORD STRUCTURE: 64 checks; PASS 24 / NOT_RUN 29 / FAIL 8 / BLOCKED 3`
  → 本地仍未 READY，**不把失败归因于外部递交项**。

---

## F. 本地就绪门实测（2026-10-02）

```
$ python3 scripts/check_build_loop.py
VALID RECORD STRUCTURE: 64 checks; {'PASS': 31, 'NOT_RUN': 28, 'FAIL': 2, 'BLOCKED': 3}

$ python3 scripts/check_build_loop.py --ready
NOT READY: candidate='octosense-backend@0.4.0 · 15 表/27 命令 · 统一命令边界 authorization+idempotency+jobs'
  unpassed:      G0-B G0-D G0-E G0-F | T01 T23 T24 T25 T26 T28 T29 T32 T33 T34 T35 T36 T37 T38 | U01–U12
  other_revision: G0-A G0-C | T04 T06 T07 T09 T10 T11 T12 T14 T15 T19 T20 T21 T22 T27 T30 T31 | P01–P05
  FAIL:          T28（旧 PASS 已撤销）、T29
```

`other_revision` 里的项是上一轮留的 PASS，本轮没有逐条重跑；不要当成本轮证据。
`unpassed` 与上面的 B2/B4 一一对应；`--ready` 失败**不**归因于外部递交项。

### 下一轮的最小关闭集（按投入产出排序）

1. **B1 原生按钮按角色隐藏** → 直接决定 T28 能否翻正，且是 `--ready` 的硬缺口之一。
2. **U01–U12 真人 UI 验收**（12 项一次拍完，需要人）。
3. **T33–T38 模型链**（需要 provider 授权；未授权前保持 NOT_RUN）。
4. **T24 旧入口统一边界**（需先与用户确认"比赛模式图谱"的定义）。
