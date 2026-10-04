# 运行路线裁决（G0.6）与实测边界

日期：2026-10-02。工程：`/Users/abeam/一些尝试/知了OctoSense`。

## 1. 路线选择：A（应用自有本地事实）

依据 `docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md` §4 的两条候选路线：

- **路线 A（已选）**：任务权威在本应用自己的宿主隔离存储里，`main.splash` 实现与
  后端 Python 领域核心**同一套命令规则**。
- 路线 B（包外 HTTPS 业务服务）：**未启用**。它需要新增公网部署与身份信任，
  本工程未获授权，13 号文档也明确"官方网络允许不等于本赛事已接受该部署形式"。

因此：**不把本机 Python 服务塞进 Hub 包，也不自行转公网部署。**
后端 `backend/src/octosense_backend/` 保留为规则参考实现、API 契约与回归基线；
Hub 包内只有 `bundle/`（manifest / listing / main.splash / assets / screenshots）。

## 2. 唯一事实源

| 事实 | 存放 | 说明 |
|---|---|---|
| 任务、状态、版本 | `tasks.json` | 宿主隔离存储 jail 内 |
| 命令回执（幂等键 + 指纹） | `actions.jsonl` | 同一 (actor,key) 同指纹才回放 |
| 事件流（task_id + 真实时间 ms） | `events.jsonl` | 追加式 NDJSON |
| 身份 / 选中 / 状态行 | `state.json` | `ui.<handle>` 不在宿主事件回调外可解析，故顶层不同步 |

## 3. 已实测

- 固定版本 card-host 准入：`octosense-repair 0.1.0 admitted`，capabilities `{"storage"}`，隔离 16 MiB。
- 脚本解析/求值：**0 个 `[E]` 错误**，`[SPLASH] eval: ... view=true`。
- 真实点击（MAKEPAD_REMOTE `/snap` + `/click`）→ `tasks.json` / `actions.jsonl` / `events.jsonl` 实际写入。
- 崩溃一致性：**未证明**。`fs.write` 单文件成功不等于掉电安全，13 号文档已要求另证。

## 4. 平台缺口（阻断项，未绕过）

固定版本 card-host 上实测失败，需要宿主侧修复或换构建版本：

1. `set_visible(false)` 不触发重排：隐藏控件仍占位（截图字节数不变、`/snap` 尺寸仍为实值）。
2. `on_render` 不实例化子控件：无法按白名单动态生成动作按钮。
3. OctoScript 解析/编译边界：
   - `const X = ...` 不产生可见绑定（必须用 `let`）；
   - `ok` 是保留字（try/ok 块），不能做变量名；
   - fn 内跨声明顺序调用另一个 fn → "call target is not a function (got nil)"；
   - 对象字面量嵌套对象字面量会让所在函数解析为 nil；
   - 三元表达式 `c ? a : b` 不支持；
   - `string` 没有 `.hash()` / `.substr()`；
   - `fn` 是保留字，不能做对象 key（要写 `"fn"`）。

## 5. 因此的动作白名单实现方式

渲染层做不到按角色隐藏按钮，所以白名单改为**分发层强制**：

- 每个动作按钮点击 → `runAction(cmd)` → 对应命令 → `runCommand()`；
- `runCommand()` 依次校验：主体可见性（`visible`）→ 命令源状态（`sourceOk`）→
  幂等键与指纹（`receiptFor`/`recordReceipt`）；
- 任一不过即 `fail(...)`：写 `state.json` 的拒绝原因，且**不产生成功回执**。

规则内容与 `docs/implementation/01_REQUIREMENTS.md` §3 权限矩阵逐条对应
（经理无技工角色不得自主接单、接单前联系方式脱敏、IN_PROGRESS 换设备需同项目经理与理由、
提议仅当前承接者或代行经理、确认/拒绝仅原报修人、开工需 CONFIRMED 窗口内且已绑定设备、
完工需可读证据、承接者不能自验…）。

## 6. 未接通 / 待补

- 原生 UI 按角色隐藏动作按钮（依赖平台缺口 1/2 修复）。
- 宿主身份 / session / grant / 配对（T29/T32）：依赖宿主能力，当前 `X-Actor-Id` /
  界面切身份仅开发调试，不等于身份校验通过。
- octos 助手 / 真实模型（T25/T26/T33–T38）：未授权未配置。
- SSE / 持久化提醒作业：Web 后端已实现（`octosense_backend.jobs` + `/events/stream`），
  原生宿主侧未接。
