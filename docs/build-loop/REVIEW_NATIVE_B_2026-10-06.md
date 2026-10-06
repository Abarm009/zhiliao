# B 版原生独立 Review · 2026-10-06

结论：**能够启动并演示状态流；完整原生验收 FAIL，最新宿主兼容性未验证。** 置信度高。只新增独立测试副本、运行证据和本报告；未改业务代码、原始 bundle、A 版材料、验收台账，未提交/推送 GitHub 或创建 Hub Issue。

## 实际复跑

- 审查对象：当前未提交的 B 版 `app/bundle`；digest `1ac7bb265b66e9ff2a049aacd67fd9de1e30b2a29449fc1f61482e2ec5b477ca`。
- 将完整 bundle 复制到 `runtime/review-native-b-20261006/bundle`，使用全新独立 app-data，全部业务动作经官方 `/snap` 定位控件及 `/click` 真正调用按钮；未用手工数据改写推进状态。
- B 版 ZIP 内 12 个文件与当前 bundle 逐字节一致；旧版本 `hub check --allow-unsigned` 本次 PASS。
- 真正加载原生窗口，无 `[E]` 日志；新建、提交、接单、绑定、提议、确认、开工、处置、完工、退回、第二轮完工、独立验收可操作。流程经过两轮完工到 COMPLETED。
- 开工首次在测试等待后仍拒绝，稍后不重启重试成功；不能据此前一次拒绝判定时钟永久冻结或主链卡死。预约等待/时间刷新尚需专门定位，未列为确定阻断项。
- 无证据时提交完工被拒；点击“上传证据”写入伪 READY 后则成功完工及验收。**这不是有效的真实证据闭环。**
- 不同角色错误接单、自验及 COMPLETED 再开工被拒；错误显示依赖 tick，约 1 秒后出现，不是所有失败立即刷新。
- 独立实例关闭再启动：任务和 12 条回执完全恢复；事件文件 13 行保持，但界面事件计数变 0。未执行故障断电、kill -9、并发写入或全部 38/12 项验收。
- 本轮未改后端，未重复跑 190 项后端测试；历史测试结果不能写作本轮结果。

## 问题与修复建议（按优先级）

### B-R01 · P0：伪 READY 绕过真实附件门槛（运行复现）

`app/bundle/main.splash:574-580`：没有 picker、没有文件字节，却写 `bytes:1024`、`sha:"demo-sha"`、`ready:true`。同一操作的事件 `ready:false`，状态文案写“未 READY”，但 `readyCount()` 将其算为可读证据，`submitCompletion()` 放行。

本次隔离目录只存在 state/tasks/actions/events 四个文件，没有附件文件；真实点击仍成功到 COMPLETED。禁止把演示说明或 note 字段当作证据完整性的替代。

建议：未真实持久化并验证字节及摘要时保持非 READY，演示数据不得满足正式完工门槛。若平台尚不支持文件能力，公开候选可以展示到该步骤，但说明阻断；不要强行声称完整闭环。

### B-R02 · P1：幂等冲突和回放分支被删（代码确认）

`app/bundle/main.splash:287-295` 计算 `let hit = receiptFor(...)` 后完全不使用结果，无条件新增回执；相对父版本的 diff 删除了 conflict 拒绝和 hit 回放分支。提交说明却把“重复 key 返回原 action_id”打勾。

建议：恢复统一命令边界中的 key/fingerprint 冲突校验和原回执返回；重放不得再执行写入或增加 version/event/receipt。补真实相同 key 同参数、同 key 不同参数的定向验证。此项未通过真实 UI 重用 key 来动态复现，结论依据代码与 diff。

### B-R03 · P1：事件恢复解析格式错误（运行复现）

`app/bundle/main.splash:200-206` 逐条 append JSONL；`load():221-223` 却将整个 JSONL 当单个 JSON parse，无法恢复多行 EVENT_LOG。

本次重启后磁盘 13 条事件仍在，界面显示“事件 0 条”。任务与回执恢复正常，不能把“所有事件与计数恢复不变”写 PASS。

建议：统一事件持久化和读取格式；支持已有 JSONL 的逐行加载，或明确迁移到 JSON 数组。重启检查真实内容和计数，不能只检查文件存在。

### B-R04 · P1：最新宿主没有完成构建/兼容性验证（证据确认）

本次使用的 `card-host` mtime 为 2026-10-01 11:30。SOURCES 声称 Hub@6741dea、Shell@a5d847a，并声称本地 Hub 含 .git；实际上 runtime/native-build 的 Hub/Shell 均无自己的 .git，不能使用父项目 HEAD 证明上游来源。

只读查询官方 main：OctoSense `4081c30e432ad0c3d0260c90be804d5e8aa5a9a1`；App Hub `78dfda5f33638e1869c36bceef5713342aae861c`。读取一个最新 SHA 不等于该 SHA 已编入旧二进制。现有 card-host Cargo.toml 指向 Makepad/Octoscript 等固定依赖，未证明其把最新 OctoSense Shell 编入。

建议：固定有完整来源的兼容组件快照，按当前官方锁文件在独立目录重新构建并记录二进制摘要和完整构建输出；在最新版宿主重复以上实际交互。完成前删除“最新 OctoSense 已验证”的表述，保留“固定旧宿主候选”的准确口径。

### B-R05 · P1：身份切换仍显示不可见任务（运行复现）

`app/bundle/main.splash:835-840` 切身份后强选第 0 条任务；`refreshLabels():803-808` 不检查 visible 即显示 ID、状态、承接者、设备和预约。原生“报修人二”可看到“报修人一”的任务卡，虽然 contact 被隐藏、接单动作被拒。

建议：currentTask/上一条/下一条和任务统计按当前主体可见性过滤；换身份时选择第一条可见任务，无可见任务时显示空态。演示身份不是生产认证，此修复也不能代替宿主身份授权。

### B-R06 · P1：发布版本和验证文档有矛盾（文件确认）

- manifest/check 的 version 为 `0.1.0`；Issue 标题、README 的 version 却为 `0.1.0-b`。ZIP 文件名后缀不改变 manifest 版本。
- SOURCES/README 的 A 版 digest 写 `23e56ea0...`，实际 A 版已发布材料记录为 `eff13f557080fc12ac2961f6bee83a2365f3d8fb5ac0e56681cee45b13c4ad26`。
- VERIFICATION 的“回执原 action_id”“重启事件不变”等 PASS，与本次代码/实测不符。
- 已知限制文档声称 evidence size=0、demo:true，代码实际 bytes=1024、sha=demo-sha，且没有 demo:true。
- B 版 README 先 cd 到 `/tmp/zhiliao_b_unpack/bundle`，随后用项目相对路径调用宿主，命令找不到二进制。
- scan 生成问题包、发布者自己回答 route=pass，不是独立 reviewer 通过。不要标为“scan 三关全部通过”。

建议：修正源码后统一 manifest/Issue/tag/ZIP/报告版本，再 stamp、check、打包；文档只写当前实际验证结果。复跑命令使用宿主绝对路径。

## 交付判断

A 版公开 GitHub 素材保持不变。本轮 B 版尚是未提交的本地候选，不建议按“已验证完整原生应用、最新宿主兼容、正式证据闭环”递交。可以如实展示原生候选进展；需先修 B-R01/B-R02/B-R03，校正 B-R04/B-R06，再做独立复验。真实模型、grant 生命周期仍未接通。

## 本轮证据

- `runtime/review-native-b-20261006/source-sha256.json`：审查源文件快照，结束时与原 bundle 一致。
- `hub-check.log`：本次准入检查。
- `probe-results.json`：逐点击控件标签和持久化事实。
- `review-summary.json`：重启、最新远端 SHA 与结果。
- `host.log`：本次真实宿主日志。
- `02-created.png`：创建后真实刷新。
- `04-scheduled.png`：预约确认。
- `05-fake-evidence.png`：未 READY 提示与证据计数 1 同屏。
- `06-completed.png`：第二轮验收完成。
- `12-completed-after-restart.png`：任务回执恢复，但事件计数归零。

本次独立测试窗口保留，使用本轮自己的隔离数据；其他会话和原始运行数据未改。
