# M2 独立审查 r18 — 本次 JSON 读取改动

结论：**本次 JSON 读取差异 PASS，无本范围内已证实的 P1。置信度：高。** 指定六类严格 JSON 负例继续被拒，常用正例及既有隔离冷启动场景恢复正常，没有发现新增解析错误、指令超限、越界源码修改或隔离违规。标准 JSON 正例的完整兼容性并未保持：四类合法转义被主动拒绝，深层数据也有限制，见下方建议挂账。

**本结论只适用于用户授权的 JSON 读取替换，不是整个 M2、全部历史缺陷或发布验收的 PASS。** 没有修改业务代码、GATES.json、请求、原始证据或测试材料；仅新增本报告。

## 1. 授权、规则与受审对象

- 授权：Abram 2026-10-13 16:45；本轮在 20 分钟时限内交付。仅访问本项目资料，不读取禁读凭据内容，不启动宿主或 harness，不 publish/push、不发外部消息。
- 规则：`runtime/optimization/2026-10-09/driver/run2.py:140` 的 SOL_REVIEW、`M2/CONTEXT_M2.md` 及当前用户指定范围。只有实际阻断核心功能或违反安全/隔离硬约束的才列 P1；建议不导致 FAIL。
- `D-M2-05`、`D-M4-03` 按最新裁决记 **BLOCKED-HOST**，不计 P1，不作为 FAIL 原因。此轮没有复验宿主原子替换或持锁能力。
- 主会话为 GPT-6 Astra；Router 路由不能在当前工具集核实，未声称已经切换。无子代理。没有可用的 createdAt/标题接口，未以当前日期猜测标题或改动其他对话状态。
- 正式源：`app/bundle/main.splash:560–672`，765252 bytes，SHA256 `ae25feb480ea443a0b3b7634b51b4077dc58095e48dbe58d0b2499d0c706889e`。
- 直接基线：`app/bundle/main.splash.bak-gptfix-1540:560–946`，774074 bytes，SHA256 `a3a013b283d15848e365216b60b6f2f6c1f8ee5db7534073f52942d226a28798`。没有把 r17 的另一份候选摘要当成本次直接基线。
- 作者说明、离线材料：`runtime/optimization/2026-10-09/hardfix-20261013/gptfix/`，以下简称 **E**；原生目录 `runtime/optimization/2026-10-09/M2/native-runs/`，以下简称 **R**。

## 2. 差异与实现核对

独立按保留换行的字节行比较：新文件第 1–559 行与基线全等；新第 673 行至结尾与基线第 947 行至结尾全等。所有差异均位于指定替换段。身份/密码派生、schema、动作执行、恢复调用点、布局段没有随本次改动变化。

| 核对项 | 文件/行号与证据 | 判断 |
|---|---|---|
| 全输入 token 检查 | `main.splash:569–579`；非法 token 留下 residue 即失败 | PASS；宽容原生 parser 前仍有独立门禁 |
| 完整结构检查 | `:581–601`；字符串/标量变为标记，合法容器逐层化简，最后只能是单一值 | PASS；截断、错括号、缺值、缺逗号、尾逗号、拼接值均不能通过 |
| 重复键 | `:624–664`；原文与解码序列化后的冒号、容器和标量数量分别核对 | PASS；同名键覆盖减少字段数，包含嵌套和转义后同名键 |
| 不返回部分值 | `:609、618–665、667–670`；失败出口保持 `value=nil`，全部门禁通过才赋值 | PASS |
| 语法与禁用写法 | 新段无 `(expr).method()` 匹配；独立解析正式源输出 `PARSE_PASS bytes=765252`，无 diagnostics 输出 | PASS |
| schema/业务边界 | 替换段后字节完全相同；E 的既有 21 项 schema 检查独立重跑 | PASS 本次保留性；不代表重新审过全部 schema |

数量回读是本读取器针对字段/容器丢失的门禁，**不是普遍的值等价证明**。因此本轮还对独立正例的实际解码结果做了 Python JSON 值比较，而没有只看 `success=true`。

## 3. 离线独立复核与严格 JSON

### 3.1 作者材料独立重跑

未运行会改写证据的 `check_json.py`；直接运行项目内既有、已阅读源码的离线 VM。它使用 vendored ScriptVm，不加载桌面宿主、账号或网络。

```text
runtime/optimization/2026-10-09/hardfix-20261013/gptfix/offline-vm/target/debug/gptfix-offline-vm app/bundle/main.splash parse
runtime/optimization/2026-10-09/hardfix-20261013/gptfix/offline-vm/target/debug/gptfix-offline-vm runtime/optimization/2026-10-09/hardfix-20261013/gptfix/offline-json-tests.splash 180
```

输出：两次均 rc=0；180 callbacks，最高 **4667** 条指令，总计 207248。既有测试脚本的读取器文本与正式新段一致。作者记录的 116 份原 seed JSON/JSONL 文本或行、21 项 schema 检查，与本次实际重跑相符。50,000 字符含中文/emoji字段在这组中通过。

### 3.2 审查方独立输入检查

从正式源码精确抽取新第 560–672 行，在内存生成测试脚本，通过进程 stdin 交给同一离线 VM，没有新增或覆盖测试文件。实际完成 **241 callbacks，rc=0，最高 4653 条指令**。输入包含手选边界、180 项固定随机变异（`random.seed(18)`）、负数/小数/指数、中文/emoji、BMP 转义、控制字符、不同容器深度及长字段。成功值重新序列化后用 Python `json.loads` 与原值比较，成功 consumed 与原码点数比较。

最终输入脚本 SHA256：`9a71ea257cd67c4947d260b741aafabe97cd5611db84eb019a066df68a6d14cf`。这是 stdin 内容的追踪摘要，未声称项目中有同名落盘测试文件；本报告记录本轮 stdout 结果。

| 指定重点 | 实际输入例子 | 结果/门禁 |
|---|---|---|
| 截断 | `{"a":"x`、`{"a":1`、`[1` | 全部拒绝，未返回部分值 |
| 首尾不闭合/错配 | `}"a":1{`、`{"a":[1}` | 全部拒绝 |
| 重复键 | `{"a":1,"a":1}`、null 重复、嵌套重复、`a`/`\u0061` | 全部拒绝；不同 sibling 对象各自的 `a` 仍接受 |
| 尾逗号 | `[1,]`、`{"a":1,}` | 全部拒绝 |
| 非法转义 | `\q`、不满四位 `\u123`、非 hex `\u00xz`、未转义 NUL | 全部拒绝 |
| 尾随内容 | `{}[]`、`{}/*x*/`、关键字/数值拼接 | 全部拒绝；前置注释、BOM 也拒绝 |
| 常用正例和值保真 | 中文/emoji、引号/反斜杠、换行/回车/tab、负数/指数、普通 BMP 键 | 接受的值与 Python 解码值一致；未发现静默改写 |
| 双反斜杠字面量 | 实际内容为 `\b`、`\f`、`\/`、`\ud800` 的字符串 | 接受，未被当作实际转义误拒 |
| BMP 控制字符 | `{"s":"\u0000\u0001\u0008\u000c"}` | 接受且值一致 |
| 长字段 | 单字段 50,000 和 1,000,000 个中文字符 | 均接受，consumed=50009 / 1000009，无 VM 超限 |

没有发现非法 JSON 被接受，也没有发现已接受值的语义差异。但**不能称 241 项全部与完整标准 JSON 接受集合一致**：四个随机变异产生了合法的实际 `\b` 转义，被新读取器拒绝；这是作者已披露的限制，见 S1。最初补查中 Python 序列化控制字符产生 `\b/\f`，默认“合法即接受”的断言因此失败；本轮随后完成上述不提前终止的全量检查，区分标准合法性与已知拒绝策略，没有将这次测试设计偏差伪装成应用错误。

## 4. 两轮原生证据的独立核对

| 项目 | rc.1：R/gptfix_1625 | rc.6：R/gptfix_rc6_1633 |
|---|---|---|
| 实际运行时间 CST | 16:22:52–16:31:29 | 16:33:37–16:42:16 |
| result 数量 / verdict | 29 / 全 CLEAN | 29 / 全 CLEAN |
| profile_probes.ok、pre/post NONE、pgid 回收 | 各 29/29；回收后 [] | 各 29/29；回收后 [] |
| returncode / panic | 全 0 / 全 false | 全 0 / 全 false |
| 运行中的 main.splash SHA | 29/29 等于受审正式源 | 29/29 等于受审正式源 |
| captures 与 SHA 回核 | 29/29 | 29/29 |
| MANIFEST 逐文件 SHA 核对 | 4941 项，0 不符 | 6536 项，0 不符 |
| 敏感目录核验边界 | 跳过 29 项隔离 identity 文件 | 跳过 29 项隔离 identity 文件 |
| 原始 host.log | `[E]`、`splash: splash:`、instruction limit 均未发现 | 同左 |
| 原 HOME mtime / library_scan | 29/29 未变 / 全空 | 同左 |

没有读取被禁止的凭据文件。MANIFEST 的敏感项主动跳过，故不宣称“所有 manifest 文件均已核验”。profile 中的拒绝探针结果来自已存在证据，本审查没有执行其命令。sandbox_denials 的既有系统缓存、外部网络与自动化拒绝记录没有被误写成允许访问。

两轮 summary.request 均与 E/REQUEST.json 全等。相对原 review 请求，差异恰为 116 个字段：每场 seed 两路径、测试 anchor、预期 digest；29 场顺序/测试动作等未变。预期 bundle digest 为 `1bd2bfc2fb541066604638a4ae3a8c7acef409427c5845b72b396944e4833f03`。两种实际宿主文件也分别与 result.binary_sha256 一致，未把离线 VM 当作这两种发行二进制的新增运行。

直接查看 E/frames_check/contact_rc1.png、contact_rc6.png 的全部 58 格，并查看 rc.6 的 Unicode、缺主合法备份和备份槽占用原图：均有登录页，不再出现 r17 的九场空白；备份失败图有“原文保留未覆盖、视图写已冻结”提示。**这些是未登录冷启动图，不是登录后工作台或真实命令执行证据。** 无模型场景，不声称完成模型调用。

### 4.1 实际数据读回，而非仅依赖 CLEAN

两轮结果一致：

| 场景组 | 独立文件读回结果 | 本次判断 |
|---|---|---|
| rv_clean_ascii / rv_clean_unicode | pending_input、confirm_intent、confirm_intent_id、action_keys_by_task 与原 seed 值全等；tasks 字节不变 | 正例原文、稳定意图与键恢复通过 |
| rv_history_array / rv_history_ndjson | array 主源未改；NDJSON 转为 2 条数组，逐记录值与原两行相同 | 合法历史读取/迁移通过 |
| rv_primary_over_old_bak | 较新 2 条主源保持原字节 | 主源没有被旧备份替代 |
| rv_missing_primary_valid_bak | 生成 1 条数组，与合法 NDJSON 备份的单条记录值相同；备份字节不变，主文件非 null | 备份恢复通过 |
| rv_bad_main_old_bak / rv_history_duplicate_key | 从合法旧备份恢复；原坏主字节在 actions.jsonl.bad_lines 中完整保留 | 没有把重复键输入作为合法主源直接使用 |
| rv_view_missing_value / rv_view_duplicate_key / rv_view_old_backup | 原坏 view 在 boot-bak / corrupt-bak 中逐字节保留 | 坏输入保源通过 |
| rv_view_no_backup_slots / rv_bad_main_backup_blocked / rv_history_truncated / rv_history_unreadable | 坏源或目录保持；UI 可见且日志无 VM 故障 | 失败分支未回归为空白或部分解析结果 |
| 六类未决事务冷场 | missing_commit / no_applied / null / wrong_id / false_time / claimed_unprojected 均 hf_recovery_pending=true，投影未改 | 读取后的既有冷屏障没有回归 |
| rv_tx_complete_positive | pending=false，任务/动作/事件原投影不改，登录页正常 | 本次读取后完整投影冷启动可用 |

58 场 tasks.json 均与对应 seed 字节相同。clean 场景的 selected_task_id 最终为 `""`，**不能说 view 所有字段完全不变**；源码 `main.splash:7106–7118、13063–13073` 的既有启动选择/可见性兜底会在未登录时重新选取或清空，它位于本次未改的段落，本轮未将此行为归因于新解码器。

三项 wrong receipt/event/decision binding 场景虽已正常渲染，pending=false 和原投影未改并不能证明完整事务绑定正确。本次不关闭 `D-M2-03` 的整体事务协议缺口，也不借这些截图认定真实错误命令执行成功。`D-M2-02` 仅认可稳定意图恢复子项，不代签真实重试；`D-M2-01/07` 仅认可本次 JSON/合法恢复相关子项，不将段外 schema、主提交与历史结果绑定统统关闭。

## 5. 缺陷/建议挂账

本范围内必修 P1：**0**。以下均为建议，依 SOL_REVIEW 不导致 FAIL。

### D-M2-01-R18-S1 — 合法转义接受集合收缩（建议；置信度高）

- **文件/行号：** `app/bundle/main.splash:565–566、574、620–623`；E/CHANGES.md“明确限制”第 1 项。
- **证据：** `{"s":"\b"}`、`{"s":"\f"}`、`{"s":"\/"}`、`{"s":"\ud83d\ude42"}` 在新 VM 检查中均被明确拒绝；以指定旧第 560–946 行独立运行，前四个 callbacks 均 success=true，分别耗指令 1119、1124、1114、1744。另有四个随机变异的合法实际 `\b` 输入落入相同拒绝策略。
- **根因：** 原生 tokenizer 不可靠处理这些真实转义，新读取器采用全输入预拒绝。它避免静默丢字符，但没有保持旧读取器的全部合法正例。
- **影响/分级：** 可能影响采用 ASCII surrogate 编码 emoji 的外部 JSON、含上述转义的持久文档。本轮 116 份原 seed 文本/行及两种宿主常用正例未受阻断，也未见新增安全放行，列建议；不能声称“所有标准正例不变”。
- **具体改法：** 在现有原生读取路径中，对字符串 token 内的真实 `\b/\f/\/` 做转义感知规范化后再解码，例如前两者转 BMP `\u0008/\u000c`；保留对双反斜杠字面量和解码后重复键的区分。合法 surrogate pair 需采用能保真合成码点的受支持路径，未验证前继续明确拒绝并保源，不直接解除预拒绝开关。
- **验证：** 四类合法转义接受且值等于预期；孤立高/低 surrogate 仍拒绝；奇偶反斜杠、转义键重复与混合 Unicode 回归；然后重跑现有离线组和两种发行宿主对应场景。

### D-M2-01-R18-S2 — 实际深度与错误定位限制（建议；置信度高）

- **文件/行号：** `main.splash:589–601、609、629–665`；E/CHANGES.md“明确限制”第 2–3 项。
- **证据：** 1/12/24 层数组接受；25 层 `[...1...]` 拒绝，原因为数值丢失；48 层拒绝数组结构丢失，49 层报超过 48。失败 error_offset 保持 0。旧段的同一 25 层数组在离线 VM 中出现 `variable v not found in scope`，因此没有将其说成旧版已成功支持的实测正例。
- **根因：** 语法化简上限 48，不等于原生 serialization 的完整往返深度；parser API 没有回传准确错误 offset。
- **具体改法：** 对外文档分别写清语法上限与已验证往返深度，错误说明不要暗示精准位置；若真实存储出现受影响深度，再实现受支持的保真读取路径，仍须拒绝部分值。
- **验证：** 分别覆盖对象/数组混合深度、深层字符串/标量及空容器；保留 24/25/48/49 边界，核成功值一致、失败原源不被覆盖。

### D-M2-01-R18-S3 — 原生工作量仍需与帧预算区分（建议；置信度中）

- **文件/行号：** `main.splash:577–606、613–616、635–665`。
- **证据：** 唯一新 Splash 循环最多 48 次；180 项最高 4667 指令，独立 241 callbacks 最高 4653，100 万字符字段通过；58 份原生日志无超限。作者的 E/baseline-long-input.log 确有旧逐字符读取器的 instruction limit 错误。
- **根因/限制：** native regex/parse/to_json/match_all 的扫描和分配不会按每个字符计成 Splash 指令，但仍同步消耗时间和内存。长度检查前已调用 to_chars；多轮结构化简/多次数量统计也不是恒定 CPU 时间。未实测 400 万字符上界或最大对象字段数，不能写“任意合法输入都无单帧风险”。
- **具体改法：** 当前保留固定上限及完整拒绝；后续只在真实边界输入存在卡顿证据时优化原生扫描/分配，测量回调时间与峰值内存，不重新引入逐字符 VM 长循环，不为降低预算跳过完整性门禁。
- **验证：** 对最大长度字符串、宽对象/数组及深层结构分别测真实宿主帧时间/内存；确认失败保源、界面可恢复，原有六类负例不变。

## 6. 最终判定

本次差异严格局限于指定 JSON 读取段；指定负例仍拒绝，常用合法数据、原文/稳定意图和历史恢复已有离线及 rc.1/rc.6 的对应证据，过去的本组空白/预算错误未再出现。没有本范围内已证实的核心阻断或安全/隔离硬约束违反，因此按 SOL_REVIEW 判局部 PASS。合法转义/深度收缩及原生帧预算边界如实挂账，不以“29 CLEAN”冒充整个 M2 的验收。

VERDICT: PASS
