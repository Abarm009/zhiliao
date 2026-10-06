# 2026-10-06 ROUND5：web 演示链路修复 / 原生首屏修复 / 提交前核对

**范围**：真机启动 + 浏览器全链路实测 + 原生宿主探针。不接真实模型，不递交外部。
**结论口径**：每条都附复现方式；未修的照实标 BLOCKED / FAIL，不假装通过。

---

## 一、本轮修复（4 项，均实测通过）

### R5-01 · web 演示永远进不了 IN_PROGRESS（原 R-P0-5 的残留）

`app/demo-web/static/workbench.html` 的 `proposeAppt()` 把窗口写死 `Date.now() + 2h`。
后端 `start_progress` 要求 `start_at_ms <= now < end_at_ms`
（`commands/__init__.py:621-625`），而 `appointments.py` 文件头规定提议有效期
`min(24h, 开始时间 - 现在)`。两者叠加：**web 端永远无法开工，也就永远无法到达
COMPLETED。**

改为 `now + 25s` / `+20min`：报修人有 25 秒完成确认（否则 410 APPOINTMENT_EXPIRED），
技工稍等即可开工。服务端时钟校验未改。

复现（浏览器三角色全链，ego-browser 实点）：
```
createDraft → confirm(OPEN) → tech accept(ACCEPTED) → bind asset
→ tech propose → reporter confirm(SCHEDULED) → 等 26s → tech start(IN_PROGRESS)
→ upload evidence → submit completion(AWAITING_ACCEPTANCE) → reporter accept(COMPLETED)
实测结果：COMPLETED，任务版本 v1→v9。
```

### R5-02 · web 端绑定设备永远候选为空

`fetchCandidates()` 用 `asset_id`（`as-a-1`）去查 `/assets/match?code=`，而该参数要的是
`repair_assets.asset_code`（`AC-001` / `PWR-001` / `EXH-001`），三次全
`ASSET_NOT_FOUND` → 绑定设备不可用 → 缺 `asset_id` → `start_progress` 被
`IllegalTransition` 拒绝。改为按 asset_code 查询后，候选正常返回。

### R5-03 · 原生首屏渲染 `[Error:WrongValue]`

`main.splash` 的状态行在未选中任务时执行
`contactLine(currentTask()) + readyCount(currentTask()).to_string() + currentTask().completions.len()`，
`currentTask()` 返 nil → 视图表达式求值失败，把错误串渲染到首屏。
新增 `detailLine()`（声明在视图之前，见下方 N2 的顺序约束）做 nil 短路。
修复后 `card-host` 日志 `[E]` 计数为 0。

### R5-04 · 原生动作按钮标签横向裁字 + 末行被压扁

`body` 高 821pt，可用宽 368pt。原 `Bar/Acc/Danger` padding 10~16、字号 12，
三按钮行的自然宽度超过 368，末个按钮被压到自然宽度以下：`经理分配` 只显示"经理"、
`开工（→ IN_PROGRESS）` 只显示"开工（→IN_PRO"；末行 `取消任务/改派` 被压到高 12pt。

修法：padding 收到 6/8、字号降到 10、`开工` 标签去掉目标态、该行 `spacing` 收到 2。
现在 `/snap` 报 26 个 Button 全部以自然宽度渲染，末行高 30pt（不再贴边裁切）。

---

## 二、本轮发现但**未修复**（两条都是 OctoScript 宿主持久缺口）

### N1 · 原生界面完全不重绘（新发现，影响全部 U 项与 T28）

宿主日志只有一行：
```
[SPLASH] eval: 40976 bytes preserve=false view=true animating=false tick=false epoch=0
```
`animating=false tick=false` → 视图只在加载时求值一次。**所有 `on_click` 的副作用
确实落盘了**（`state.json` / `tasks.json` / `actions.jsonl` / `events.jsonl` 都更新），
**但屏幕纹丝不动。**

复现：
```sh
curl -sS http://127.0.0.1:8728/g?raw=1 -o a.png      # 点"新建草稿"
curl -sS http://127.0.0.1:8728/click?x=86&y=384
sleep 2; curl -sS http://127.0.0.1:8728/g?raw=1 -o b.png
# a.png 与 b.png 的 sha256 不同但视觉完全相同；state.json 已写"草稿已创建 ..."
```

宿主支持的重算路径在 `runtime/native-build/makepad/widgets/src/splash.rs:387-415`：
只有 **(a) 数据抓取 epoch 变化**、**(b) `fn tick()`（自动起 1Hz 定时器）**、
**(c) animating（绑 live data）** 三种。`octoscript/examples/` 内没有 `fn tick` 用例，
`ui.<id>.set_*` 的可用方法在本地源码里没有文档。**需先做最小探针确认 tick 内如何
更新已声明控件的 text，才能把"点了有反应"做出来。** 本轮未做，不宣称修复。

### N2 · 10 个业务动作 handler 在 VM 里解析成 nil（新发现）

`card-host` 日志反复出现：
```
[E] splash:...:324:16 - call target is not a function (got nil)
[E] splash:...:118:24 - no getter for field id on type nil
```
实测 26 个按钮中，**只有** `setActor` / `createDraft` / `prevTask` / `nextTask`
可用；`confirmDraft` / `acceptTask` / `assignTask` / `bindAsset` / `unbindAsset` /
`proposeAppointment` / `confirmAppointment` / `rejectAppointment` / `acceptCompletion` /
`cancelTask` / `togglePin` 点击后**无任何反馈、不写任何文件**（连 `fail()` 的拒绝
状态行都不出现）。

`main.splash` 文件尾的注释记录了三条已知触发条件：跨声明顺序的 fn 调用、嵌套对象
字面量、`ok` 变量名。上面 10 个函数的失败行号（324/366/397/420/631/680/733）与
这三条的对应关系**尚未定位**，需要逐函数最小化复现，不能靠猜。本轮未修。

---

## 三、提交前核对（10-06 实测）

| 项 | 命令 | 结果 |
|---|---|---|
| 单元测试 | `pytest backend/tests/octosense_backend/ -q` | **190 passed**（62s） |
| 端到端链路 | `backend/scripts/e2e_full_chain.py` | **PASS**（13 步 DRAFT→COMPLETED，含退回重做） |
| 浏览器全链 | ego-browser 三角色实点 | **PASS**（见 R5-01，到达 COMPLETED） |
| 包准入 | `hub stamp` + `hub check --allow-unsigned` | **PASSED**，digest `cd72ded4…`（仅警告未签 publisher 名） |
| 人工评审包 | `hub scan --packet` | 生成 7 问评审包，**未接 reviewer、未发布** |
| 结构自检 | `verify_migration.py` / `verify_pack.py` / `check_build_loop.py` | 通过（只查记录与结构，不执行应用） |
| 入口脚本 | `python3 scripts/run_local.py --port 8731 --web-port 8732` | **通过**（后端 200 / demo 200 / proxy 200，状态落 `runtime/<dir>/`） |

### 入口脚本指错（R5-05，已修）

`scripts/run_local.py` 原先启动 `wagent_backend.web.app`——迁移来的旧 WAgent 后端，
**不是本比赛的 OctoSense 应用**。README「移动后运行」因此把评审引到错误入口。
已改为启动 `octosense_backend.api:make_app` + `app/demo-web`，并新增
`--port / --web-port / --runtime / --no-web`。

### 随包截图注水（R5-06，已修）

`app/bundle/screenshots/01-main.png` 的 sha256 与 `runtime/build-loop/l0-shots/` 的
L0 三按钮版完全相同；`listing.json` 的 description/release_notes 仍写"L0 最小切片：
三按钮"。现在 `main.splash` 是 26 按钮版。已用当前宿主实渲染重截 01/02 两张，
并改写 listing 文案；digest 已重新 `hub stamp`。

---

## 四、仍然 BLOCKED / FAIL

- **T28 FAIL**：依赖 N1（不重绘）+ N2（handler 为 nil）。web 端不能替代此项。
- **T29 FAIL**：无 grant 申请/关闭/退出/到期路径；bundle 只声明 `storage`。
  需宿主 host pairing / session（14 号文档 §5 路径）。
- **P06/P07/P08 BLOCKED**：Hub Issue、商店收录、赛事回执——需用户显式授权后才递交。
- **T01/T25/T26/T33-T38 NOT_RUN**：未接真实模型，本机无可用凭据。
- **U01-U12 NOT_RUN**：UI 可用性未做独立人员实测；`U12`（2-3 分钟演示）依赖 N1 修好。
