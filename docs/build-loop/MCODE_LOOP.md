# M3（MiniMax Code）适配循环：与 START_PROMPT 配套执行

**定位。**本文是 `START_PROMPT.md` 与 `15_BUILD_VERIFY_LOOP.md` 的**适配附录**，不是替代。原有 L0–L8、8 状态/14 命令/38 业务/12 UI 的范围、ACCEPTANCE.json 台账、ITERATION_TEMPLATE.md 记录模板、检查器 `scripts/check_build_loop.py` 全部沿用。本文件只补齐"由我（M3 在 MiniMax Code 环境下）执行"时需要的差异与纪律。

**执行入口与排期。**仍以 `15_BUILD_VERIFY_LOOP.md` 为主线；`docs/implementation/12_DELIVERY_PLAN_20261009.md` 决定日期，`14/13` 决定平台边界。本文件不重新定义范围。

## 1. 当前会话身份与模型路由

1. 我运行在 MiniMax Code 环境下，会话级模型在系统提示中已固定（当前为 MiniMax-M3）。启动每个新会话时，必须在首轮回复中写明"实际路由：minimax/MiniMax-M3 / MiniMax"，不得使用"启用技能""调用了某个 Router 子代理"等说法代替主会话路由已确认。
2. 不得自行切换到其他供应商或计费渠道。若当前主会话无法满足某项需要（例如某工具不可用或上下文受限），先报告实际限制并询问授权，不得绕过。
3. 子代理（`task` 工具）继承父会话的模型；明确告诉子代理它的模型身份与文件所有权边界，子代理不允许改父级已写文件。
4. 比赛 Token、产品系统助手、开发用模型是三件不同的事：本会话内的"思考与推理"≠产品运行模型，演示期间需要在文档中明确写出实际接入模型与失败路径（参考 `14_COURSE2_LATEST_GUIDE_REVIEW.md`）。

## 2. 工具映射（我实际有的）

| 原循环/START_PROMPT 概念 | 我实际使用的工具 | 注意事项 |
|---|---|---|
| 读代码、读文档 | `read`（路径相对工程根，支持 offset/limit） | 不要重复读已在上下文中的内容 |
| 文件名/路径搜索 | `glob`（ripgrep 后端） | 用于发现资产、模板、清单 |
| 文本/正则搜索 | `grep`（ripgrep） | 排除规则已默认；需要包含被忽略项时给窄路径 |
| 修改文件（部分） | `edit`（精确字符串替换） | `old_string` 必须唯一，否则改 `replace_all` |
| 新建/覆盖文件 | `write` | 整文件覆盖；写入前 `read` 现状 |
| 执行命令 | `bash`（非交互，无 TTY） | 需要长进程用 `run_in_background=true`，前台默认 120s、上限 300s |
| 任务列表 | `todowrite` | 多步推进/显著进度变化时同步；不要每轮都重写 |
| 子代理 | `task`，内置 `mavis` / `explore` / `verifier` / `worker` | 见第 5 节委派纪律 |
| 结构化问卷 | `ask_user`（≤4 步、每步 ≤4 选项） | 见第 6 节 |
| 单一延迟提醒 | `self_reminder` | 见第 7 节 |
| 等待子任务结果 | `task_output` + `task_append` | 见第 5 节 |
| 媒体/产物交付 | `<deliver-assets>` 包裹 `<media>` | 见第 8 节 |
| 浏览器原生操作 | `mcp_browser`（需先 `skill: browser-use:control-in-app-browser`） | 用于 Hub/App 真实页面验证 |
| 已配置 App/连接器 | `mcode-tools`（需先 `skill: mcode-tools-master`） | 普通 MCP/插件工具直接调，不需要 App 探查 |

> Bash 默认 120s，长任务主动 `run_in_background=true` 或加 `timeout`；不要通过反复重试掩盖卡死。子代理可用 `task_query` 查状态。

## 3. 每一轮的最小切片（我的执行版本）

把 `15_BUILD_VERIFY_LOOP.md` 第 6 节映射到我的工具链，单轮动作顺序：

1. **恢复现场**：`read` 上轮 `runtime/build-loop/iter-Lx-<slice>.md`、ACCEPTANCE.json 中已 PASS 的 `revision`、`git status`（若已 init）。不重做已完成项。
2. **选取切片**：从最早依赖已满足的必需项中选一个；先写"可观察的验收条件（PASS/FAIL 判定）"，再写代码。
3. **确定所有权**：本轮修改文件清单。若与子代理的写入路径可能重叠，**先在任务描述中固定**，避免两个写者覆盖。
4. **实现**：UI 动作 → 命令守卫 → 权威写入 → 结果回读 → UI 反馈，**一次写齐**。`edit` 优先；新文件用 `write`。
5. **构建**：按已记录的命令在 `bash` 中执行；保存退出码与错误日志到 `runtime/build-loop/iter-Lx-<slice>/build.log`。
6. **相关测试 + 原生操作**：脚本测试用 `bash` 跑；UI 原生页面用 `mcp_browser` 跑（先 `inspect`，再 `query`，再 `screenshot`，最后 `read` 关键 DOM）。
7. **状态/事件/回执回读**：从持久层（DB / 事件日志 / 官方 store）直接读权威值，不依赖 UI 显示的成功状态。
8. **独立核验**：能用 `verifier` 子代理跑独立核验；不能让同一执行者自验业务关键路径。
9. **失败定位 → 最小修复 → 重跑失败项 + 受影响回归**。
10. **登记版本、实际结果、证据、核验者** 到 ACCEPTANCE.json 对应行 + `runtime/build-loop/iter-Lx-<slice>.md`。
11. **挑选下一必需切片**；更新 `todowrite` 反映 Lx 进度。

每一轮只做一个切片；UI 跨多个面板也要分轮实现并独立验证。

## 4. L0 的"真实可信"边界

`15_BUILD_VERIFY_LOOP.md` 第 4 节列了 G0-A 到 G0-F 六个最小裁决点。对我而言，下列"伪通过"必须主动报告：

- 用 HTML 截图冒充原生控件；
- 用 `agent:<name>` 子代理的输出冒充主会话路由已确认；
- 把 `agent:` 类型的 manifest 文件准入当后台 Agent 已运行；
- 关闭开关/未首次同意/工具审批被拒的"系统助手"，不得记为真实 AI 通路；
- 把 mock 模型的成功回执当真实模型接入成功；
- peer、device、客户端 cookie 切角色冒充业务账号；
- 一次 `fs.write` 成功就声称事务成立。

若 G0 任一项不通过，写明**最小复现 + 实际阻碍 + 是否 BLOCKED**；不为了进 L1 而降低标准。

## 5. 子代理委派纪律

- **必须委派**（默认使用）：
  - 大范围只读证据扫读（多文件搜索/统计）→ `explore`；
  - 独立验收（业务或代码 review）→ `verifier`；
  - 明确范围的批量实现（独立文件清单、独立测试集）→ `worker`；
  - 混合跨领域任务 → `mavis`。
- **不委派**：
  - 架构裁决、关键逻辑、最终核验 → 留在主会话；
  - 跨写者重叠的文件 → 拆开后再委派，避免两个 worker 改同一文件；
  - 需要外部授权（部署、发布、额度购买、密钥提供）的动作 → 不在子代理里做，回到主会话通过 `ask_user` 询问用户。
- **文件所有权**：子代理 prompt 中显式列出"你只能改这些文件"。父会话和子代理都不修改他人已写文件；如发现冲突，先停下来报告，不擅自覆盖。
- **等待子任务**：用 `task_output(task_id, wait_ms≤30000)`；不要高频轮询；不要在子任务还在跑时就新建"替补"任务。

## 6. 何时直接做，何时停下来询问

直接做（无需额外询问）：

- 单文件/多文件局部代码改动、本地测试、文档修订、check_build_loop.py / verify_pack.py / verify_migration.py 运行；
- 已记录模板内的台账填写、证据路径补全；
- 在 `runtime/build-loop/` 写日志、截图、回读记录。

必须用 `ask_user`（≤4 步结构化问卷）：

- 需要切换路由/供应商/付费渠道；
- 需要新增公网部署、对外开放端口、推送代码到公共仓库；
- 需要读取用户提供但未到手的资源（密钥、Token、第三方应用授权）；
- 需要在范围上做实质降级（例如不实现 G0-B 真实身份、退而依赖"切角色"）；
- 需要用户对日期/范围/取舍做最终裁决。

**禁止用大段文字问开放式问题来替代 `ask_user` 问卷**，也不要为了"礼貌询问"在每一步都打断。

## 7. 等待与轮询

- 子任务有完成通知：用 `task_output` 等通知，不主动轮询。
- 等待用户回复：不需要提醒。
- 等待外部不可中断事件（例如官方服务回归、审批返回）：用 `self_reminder(action="set", delay_seconds=N, prompt=...)`；同一会话只允许一个未完成提醒；再次设置会返回 `SELF_REMINDER_EXISTS`，需要时先 `cancel` 再 `set`。事件结束后立即 `cancel`。
- 永远不要"为了等待确认"而设置重复轮询；也不要新建"替换任务"来覆盖仍在跑的子代理（见第 5 节）。

## 8. 产物与交付

任何我创建/修改/删除的真实文件（不只读、不只在思考中讨论），必须在最终回复里用 `<deliver-assets>` 包裹：

- 本地文件：`<media src="/abs/path" type="file" caption="..." />`；`src` 必须真实存在；
- 删除文件：`<media src="/abs/path" deleted="true" />`；
- 图片/音频/视频：用 `type="image|audio|video"` 与扩展名推断；
- 公开发布的网站：用 `website_deploy`，并在 `<deliver-assets>` 中以 `<media type="website" src="<url>" node_id="..." name="..." />` 交付（需要用户事先确认公开发布）。

证据路径相对工程根，便于跨机器迁移；不接受 `latest`、不接受未截屏的"已完成"宣称。截图不是事务一致性证明；模型输出不是 UI 通过证明；`PASS` 字段不是已发布证明。

## 9. Token 与上下文纪律

- 同一根因连续三次失败必须重新定位或换方案，**不第四次跑**（沿用 15 第 6 节"三振防空转"规则）；M3 在 MiniMax Code 下 Token 是真实成本，循环失败消耗必须被看见。
- 长思考（`reasoningSummary=auto`）不替代证据；思考里说"应该是这样"不能写进 PASS。
- 大输出优先落在 `runtime/build-loop/` 与 `app/docs/`，不在聊天里堆长文。
- 当一轮涉及真实模型调用时，记录 provider / 模型 / 实际 `verified_at`；不得用估算值冒充真实值。
- 真实模型的 401 / 429 / 限流：先读 Retry-After，转离线兜底或人工入口并把该 AI 项记 FAIL，**不无限重试**消耗 Token。
- 不要"为了节省时间"在 production-like 路径上 mock 后再标 PASS；mock 只用于隔离单测，且必须在台账里写明。

## 10. 文档与"未接通"清单

每次修改业务或契约后，按以下顺序更新（沿用 AGENTS.md 第 23 行约定）：

1. 改 `01_REQUIREMENTS.md` / `04_DATA_API.md` / `openapi.json` / `schema.sql` / 业务脚本；
2. 同步 `02_ARCHITECTURE.md` 与 `ARCHITECTURE.html` 中的图（先改 Mermaid 源码，再同步 SVG，再同步 HTML 内嵌）；
3. 更新 `05_IMPLEMENTATION_ACCEPTANCE.md` 中相关验收项；
4. 在 `15_BUILD_VERIFY_LOOP.md` 或本文件中标注"实际跑通过 vs 仅设计"；
5. `ACCEPTANCE.json` 中把对应行的 `status` 从 `NOT_RUN` 改为 `PASS`，填齐 `revision/verified_at/procedure/expected/observed/verifier/evidence/defects`；
6. 在 `runtime/build-loop/iter-Lx-<slice>.md` 写完整记录；
8. 不要伪造测试结果；未接通项明确写"未接通 + 缺什么条件"，不为了看上去完整而改 PASS。

## 11. 每轮汇报格式（沿用 15 第 6 节末段，补齐我的最小字段）

每轮汇报**只列**：

1. 已完成且有证据的切片（含证据路径与核验者）；
2. 失败 / 阻断（具体根因、最小复现、是否影响 10 月 6 日晚目标）；
3. 下一切片（最早依赖已满足的必需项）；
4. 实际 Token 用量或明确写"未知"（不把估算当真值）；
5. 工期影响判断（不写主观"完成 80%"）。

完整主线、状态机命令、退回链、独立验收等业务范围不在本文件重述，详见 `15_BUILD_VERIFY_LOOP.md` 第 1、5 节与 `01_REQUIREMENTS.md`、`04_DATA_API.md`。

## 12. 我不适用的部分（明确说明）

- 不会把 Claude Code 专属的 `TodoWrite` / `Bash` / `Edit` 工具名写进本工程文档；统一使用本文件第 2 节映射。
- 不会写"启用了 Codex Router 子代理即代表主会话已切到 Claude"之类的话；主会话路由以系统提示与本文件第 1 节为准。
- 不会自行在 `mavis session update` 上替用户改项目名、归档状态、置顶、对话内容；本工程的对话标题按 AGENTS.md 第 17 行规范。
- 不会调用 `web_search` / 通用浏览器代替真实 Shell / 真实官方 SDK 的接入验证；当且仅当用户明确同意"用浏览器预览"或这是必要回退手段时才使用 `mcp_browser`，并在台账中说明为何采用替代路径。
- 不会以"演示模式"为由跳过身份、持久化、事务、附件、失败恢复等 P0 项；沿用 15 第 5 节"不删除 01 R01–R10、14 类命令、独立验收、预约冲突、证据、失败恢复"。

---

**执行起点（不重述 START_PROMPT）：**首轮必须 `read` README.md / AGENTS.md / docs/ARCHITECTURE.md / docs/MIGRATION.md / docs/VERIFICATION.md / docs/implementation/15_BUILD_VERIFY_LOOP.md / docs/implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md / docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md / docs/implementation/12_DELIVERY_PLAN_20261009.md，并在 `todowrite` 中登记 L0 待办。然后从 L0 第一个可执行最小切片开始，每轮按本文第 3 节执行。