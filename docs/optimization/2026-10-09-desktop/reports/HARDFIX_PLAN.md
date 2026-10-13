# 硬缺陷共用底层与逐模块接入计划

日期：2026-10-13。性质：只读架构审查后的实施计划，**未实施、未运行宿主、未关闭缺陷、未改门禁**。

## 0. 适用范围、依据与裁决

本轮只新增本文件。输入为 `runtime/optimization/2026-10-09/driver/CARRYOVER.md` 末尾「2026-10-13 10:40 汇总」、本目录 M2_REVIEW_r13、M3_REVIEW_r12、M4_REVIEW_r12、M5_REVIEW_r13、M6_REVIEW_r12、M7_REVIEW_r12，以及当前 `app/bundle/main.splash`。另只读核对项目基线、harness 的 schema/控制实现、宿主存储注册表。未读 `runtime/identity/CREDENTIALS_FOR_ABRAM.md` 或 `runtime/secrets`，未改业务、宿主、harness、原始证据及其他报告，未 push/publish。

当前 HEAD：`8d730569546cb57310944bb299695134df773b9d`，工作树已有他人修改。**下文所有 main.splash 行号指本轮读取的当前工作树：702182 字节，SHA-256 `805257a2b6a14834d9ab092e17cc10fb143710803812c4999d55abfadaed6ae9`**，不是各报告冻结包的行号。后续改动必须按函数名重新定位。CARRYOVER SHA-256：`57c3e648bfe7ed7d41fbe48d9ddf2e196034a131a262a45c4423d61b0bc42bee`。

| 输入报告 | 本轮读取 SHA-256 |
|---|---|
| M2_REVIEW_r13.md | `9d5f13acd8acab7243681f967703d69bf25b7f979145de64ecd09f845f09cddb` |
| M3_REVIEW_r12.md | `e4bff8628d1095ee4aab10b3dc0c6fbfce23ea520af83bcc812341fbd07333e7` |
| M4_REVIEW_r12.md | `2c351cf27f431a3c14919fb4a0a9bb597c419a984e848c8c00b571550638dcca` |
| M5_REVIEW_r13.md | `d36c8d4d9ad0f298a9ad655ae9b108254cca554f224137b9b544414abed8ebc0` |
| M6_REVIEW_r12.md | `05ef3b4909f70d53ed1caab11672317a05a8175dedb95a079d979c1a6bb87c43` |
| M7_REVIEW_r12.md | `89e7849dd8573376acbbd00c387cb11a68ce5b1b92523eececcb25bdeec1f72c` |

置信度：报告所述失败事实及下列当前源码调用关系 **高**；共用设计方向 **高**；新增 Splash 实现的运行兼容性、固定发行宿主的新增原语可用性 **未知，必须原生验证**。当前工具无法确认/切换主会话为指定 gpt-6.1-sol 或 Codex Router，也没有取得线程 createdAt/设置标题的工具；未声称完成这些操作。

### 必须先明确的技术边界

1. **tmp 写入、主文件直接覆盖、读回一致，不是原子替换。版本重读、owner 文件读写，不是 CAS 或跨上下文互斥。** 当前 `_acquireTaskLock` 自述能力未具备；只改 Splash 的这些顺序操作不能关闭 D-M2-05/D-M4-03。
2. 本地参考宿主 `runtime/native-build/makepad/widgets/src/splash_storage.rs:242–415` 注册 read/read_bytes/write/append/exists/remove/mkdir/list；write 在 :331–332 使用直接 `std::fs::write`，该注册块没有 rename、持有期锁或 CAS。它是参考源码证据，不能冒充发行二进制已支持同名 API。main.splash 的 fs.rename/fs.mkdirs 注释与参考注册表存在差异，**能力只能用固定二进制探针实证，不能照注释推定**。
3. 原子替换与持有期锁属于 M2 轮的技术前置。优先使用经核验的宿主能力；缺失时由平台能力提供方补齐，再冻结新宿主。**本计划不授权改宿主、新增后台服务、装 Python/Rust 到作品包或改部署路线。** 若执行范围仍仅 main.splash 且固定宿主不提供能力，安全拒写并保源可以实施，两个原子缺陷必须继续 OPEN/BLOCKED，不得降成建议或宣称闭合。
4. 三个文件分别原子替换仍不是三文件事务。本计划选“完整 redo 日志 + 原子提交决定 + 同一持有期锁 + 恢复屏障”，使 task/receipt/event 可恢复为完整提交；提交前不能写业务投影，恢复未齐不能放行普通读写/显示成功。
5. 界面、布局、控件结构、样式、尺寸和位置一律不动。只把真实 outcome/恢复原因接到现有反馈出口；不增加控件、不绕过登录。保留 P0、38 业务、12 UI 与原门禁；本文不签任何模块 PASS。

## 1. 缺陷归并与关闭条件

| 共用底层（全部在 M2 轮实现） | 共用根因 | 对应缺陷 | 最后接入/复验轮次 |
|---|---|---|---|
| H1 严格 JSON 解码与 schema 校验 | 宽容 parse、只看括号、码点与字符串比较、任意非空对象充当记录 | D-M2-01/07、D-M3-02、R-M7-02；支撑 M5/M6 存储验证 | M2 正负例；M3 有效输入；M7 load/keep/overwrite |
| H2 不覆盖的来源保护 | 可读旧 bak 被当本次备份；固定 latest/第二备份槽被覆盖；失败后无条件回滚 | D-M2-01/07、R-M7-02；支撑 D-M2-03、D-M5-04 | M2；M5/M7 对各自来源验证 |
| H3 统一原子写、严格读回、类型一致的全内容比较 | 多套直接覆盖 writer、仅三字段/len 校验、保存/清理失败未消费 | D-M2-03、D-M4-03、D-M5-04-B；支撑 R-M7-02 | M2 底层；M4/M5/M7 调用点 |
| H4 持有期锁与可恢复提交事务 | 检查与写入分离、整盘旧快照覆盖、pending 无完整 after/event、放锁后另写事件 | D-M2-03/05、D-M4-03；支撑 M5 任务/索引恢复 | M2 核心；M4 预约/技工冲突；M5 投影恢复 |
| H5 权威 outcome 与精确原动作查询 | bool/non-nil 当成功；原结果与当前状态混同；只按 task 查最后确认动作 | D-M2-02 | M2 生产/查询；M3 两条真实按钮消费路径 |
| H6 来源与日志 schema 契约 | task 来源快照混用 ref schema；数组默认表达式丢 refs；诊断污染出处 | D-M6-03-B1/B2/C | M2 定义契约/纯函数；M6 全部生产/恢复/消费 |
| H7 完整件比较与算法明确的指纹契约 | 指纹仅有移植断言、原生 actual 未执行；索引比较隐式转换 | D-M5-04-C（及 B 的比较支撑） | M2 通用字节/值比较；M5 算法及真实件实证 |

完整必修清单：D-M2-01、D-M2-02、D-M2-03、D-M2-05、D-M2-07；D-M3-02；D-M4-03；D-M5-04；D-M6-03-B1、D-M6-03-B2、D-M6-03-C；R-M7-02。表中 `/07`、B1/B2/C 等均是这些原编号的简写，不新增缺陷编号。

“关闭”要求调用点全部接入且相应原生证据通过；新增 helper、作者静态断言、CLEAN、宿主 rc0 都不能单独关闭。D-M5-04 的当前根因包含**验证未执行**，没有本轮证据支持“仍恒零/仍误判”；先运行新匹配候选，再针对 actual 最小修复。

## 2. H1：严格 JSON 与 schema（M2 共用底层）

### 现有入口及必须替换的判据

| 当前函数/行号 | 现状 | 接入方式与负责轮次 |
|---|---|---|
| `loadViewState()` :544–637，完整性 :565–575 | parse 后看对象与首尾；`_charAtSafe` 返回码点却与字符串比较 | **M2** 去掉局部 `_complete`，使用 `hf_parse_json(text, "view_state")`；成功后保留现有逐字段偏好并入，actor/session 永不恢复 |
| `_textLenSafe(s)` :1995；`_charAtSafe(s,i)` :2003 | 字符长度与码点接口容易被误用 | **M2** 为 JSON 扫描新增明确数字码点游标；不全局改这些 helper 的既有契约，不牵连 UI 截断函数 |
| `_m2_history_record_ok(v)` :1092；`_m2_ndjson_line_ok(s)` :1105 | 非空对象/首尾大括号不够 | **M2** 变成严格 JSON + 按 path 选择 action/event 的兼容 schema；不再接纳只含 action_id 的残缺回执 |
| `loadJsonlLines(path)` :1154；`_m2_parseRecordsLoose(text)` :1728；`migrateJsonlLegacy(path)` :1764 | 整数组和逐行/bak 判据分叉 | **M2** 都委托 `hf_parse_history(text, record_kind)`；主/bak 相同；不对已识别的非法数组改走 NDJSON 宽容兜底 |
| `load()` :1584–1683 | 迁移后又直接 parse 再并入 | **M2** 迁移成功也通过同一严格 loader 读取，删除第二条宽容通道 |
| `readTaskByIdFromDisk(taskId)` :4947、`latestTaskVersion(taskId)` :4959；`_m4_disk_tech_conflict` :5102；`commitBound` :5475 | 权威读盘另用 parse_json | **M2** 通用权威读改为严格任务读取并返回明确 read_error/not_found；**M4** 冲突扫描接入此 API，不能把不可读当无冲突 |
| `m7_tasks_strict_parse(raw_text)` :1391–1418 | 首尾 `[]` 后仍可接受尾随垃圾 | **M2** 因它是全模块任务读底层，先把函数体换为 `hf_parse_json(raw_text, "tasks")` 的薄包装，保持 `{success,value,why}`；**M7** 再收口恢复调用点，不另写 parser |
| `m5_index_items_from_raw(raw)` :9593；loader :9700；reconcile 读回 :10130 | shape 核验不含原始全文完整性 | **M5** 使用 `hf_parse_json(raw_text,"m5_index")`，后续 extraction 必须消费已验证值 |
| `m6_load_history_view` :4294；`m6_restore_ai_requests_log` :7392 | 宽容解码后局部 schema | **M6** 使用 `hf_parse_json` + H6 契约；不跳过非法中间项 |

### 新增签名及返回协议

以下为**拟新增接口，不是现有宿主 API，不是已编译实现**。全部定义在 main.splash 的共用底层区，先声明低层函数，再声明包装，初始化仍留脚本尾部；不要在后续函数尚未定义时执行顶层恢复。

```text
fn hf_json_decode_complete(raw_text)
fn hf_json_scan_step(cursor, token_budget)
fn hf_schema_validate(schema_key, value)
fn hf_parse_json(raw_text, schema_key)
fn hf_parse_history(raw_text, record_kind)
fn hf_record_kind_for_path(path)
fn hf_value_equal(schema_key, expected, actual)
```

`hf_record_kind_for_path` 只把受控 actions/events 路径映射为各自 schema，未知 path 明确拒绝。若保留旧 helper 而不是删除其旧实现，替换签名为 `fn _m2_history_record_ok(v, record_kind)`、`fn _m2_ndjson_line_ok(s, record_kind)`、`fn _m2_parseRecordsLoose(text, record_kind)`。M2 同轮更新全部调用：:1117/:1180/:1192/:1740/:1823 的记录判定；:1210/:1755/:1858 的行判定；:1776/:1787/:1872/:1898/:1933 的主/bak解析。loadJsonlLines(path) 与 migrateJsonlLegacy(path) 的外层签名可保留，入栈先算 record_kind 并传递。:1195/:1228 的部分 clean/parsed 不能再作为权威成功返回；损坏源可单独保留诊断信息，但完整 loader 返回失败。

- JSON 结果统一 `{success, value, why, error_offset, consumed}`；失败 value=nil，不能把 partial 对象返回为可用值。使用 `success`，不引入宿主有已知解析风险的 `ok` 字段名。
- `hf_json_decode_complete` 必须完整实现/调用已实证的严格 JSON：object/array/string/number/true/false/null；全部非空白输入恰好消费一次。拒绝缺值、截断、额外根、尾随垃圾、尾逗号、裸键、非法转义、非法数值和重复对象键。外层空白只认可 JSON 的空格/Tab/CR/LF。
- 字符访问只走 **to_chars 得到的数值码点**，比较数字或同型码点，不能与 `"{"`/`"}"` 字符串直接比较。字符串要正确处理转义、中文、emoji、`\u` 和代理对；不能按 UTF-8 字节下标取字符。
- 采用显式栈/游标避免深递归与长文件一次回调超预算；长度、深度、数值表示上限要明确，超限返回独立原因并保源。`hf_json_scan_step` 返回 pending 时，调用者只能进入“加载未完成/禁写”，不能落默认值。完成后才公开 value。
- 若使用“严格扫描 + 宿主 parse_json”组合，必须证明宿主对扫描认可的全部 token 不丢键/不改类型/不截数；无法证明则由严格 decoder 按 token 构造值，不能仅因扫描通过信任宽容结果。序列化后长度相等、括号计数或 round-trip 字符串相等都不能替代严格语法。
- `hf_schema_validate` 是语法之后的第二闸；H1 的核心 schemas 由 M2 提供，H6 结构契约也在 M2 提供。模块只写业务语义校验和使用者。
- `view_state`：顶层对象；兼容缺省偏好与已有“单字段类型非法就不并入”的行为，不因未提供新字段拒整个合法旧 view。非空 intent 须验证 id/actor/project/command/key/payload/phase/at 的结构与 payload 完整 JSON；它只用于重试绑定，绝不建立可信会话。action_keys_by_task 保留完整对象，未知扩展字段不静默删除。
- `tasks`：沿用 :1353 的必需字段/已知状态/严格数值门禁，再核任务 ID 唯一、版本整数与合法范围；不因本轮新增底层强制丢弃合法旧业务字段。
- `actions/events`：分别核 schema，不能共用“非空对象”。兼容现有 pending/rejected/final/final_recovered/needs_verify 等分支及旧合法记录，按状态定义必需字段；final 必须有可核完整 result，pending 新格式有 tx 引用。旧无完整 after 的 pending 保留为旧未知，不能升级 final。事件要求 at/kind/actor/task_id/task_version/after；历史无 action_id 的合法旧事件可保留，但不能充当新事务关联成功证据。
- `hf_parse_history` 明确识别整体数组或旧 NDJSON（逐行只跳过纯空白行）。任意行语法/schema 失败，**整份拒绝、报告行号、保留全文**；不返回可写的部分记录。合法 `[]` 不再迁移，合法单/多行及嵌套结果保全。
- `hf_value_equal` 按 schema 和实际类型递归比较全部字段/数组顺序；对象键顺序不决定业务相等。不用隐式数值运算把 `true`、`"1"`、`1` 视为相同；数值往返有差异先原生定位，不能字符串化掩盖类型错。原始文件读回仍同时做精确文本/字节相等。

### 原生验证 H1（M2 开始，M3/M7 复用）

正例：ASCII/中文/转义引号/换行/emoji/外层空白 view、合法空任务数组、两条完整中文任务、合法1/4条NDJSON及嵌套 result。反例至少包括 `{"action_id":"rv-invalid", "result":}`、未闭合对象、`[] ignored-empty-tail ]`、合法任务数组后垃圾仍以 `]` 结束、缺值/尾逗号/第二根/重复键/非法转义/错误数值类型。

比较原生 actual：success/why/consumed/各字段与类型；合法 view 的 pending_input、confirm_intent_id、confirm_intent.payload、动作 key 精确恢复，无新“损坏备份”、无自动登录；坏源整份拒，原盘不变。每组冷开业务 **解析错误=0、运行错误=0**，实际包 digest/源码 hash 匹配。Python 严格解析仅作夹具独立 oracle，不能代替宿主结果。

关闭：M2 接入并实证后可关闭 D-M2-01/07 的解析根因；M3 正例与真实输入恢复通过才关闭 D-M3-02；M7 恢复三入口及普通写保护通过才关闭 R-M7-02。

## 3. H2：备份是精确来源保护，不是自动覆盖许可（M2）

现有：`loadViewState` :578–612；`_m2_write_diag_file` :1122；`migrateJsonlLegacy` :1764–1972；`m7_tasks_mark_corrupt` :1422；`m7_tasks_explicit_recover` :1476；M5 loader :9700 的 tmp 兜底。当前 view 已增加精确旧 bak 比对及备用槽，**保留改善**，统一时不要退回“可读旧备份即成功”。固定 `.corrupt.latest`/`.legacy2.bak`/`.recover.bak` 仍不应无限覆写来源。

```text
fn hf_preserve_source(path, raw_text, reason, guard)
fn hf_read_source(path, schema_key)
fn hf_recovery_select(primary_result, backup_results, recovery_policy)
```

- 保存返回 `{success, backup_path, exact_match, why}`。以真实读取的当前全文为准；已有备份全字节相等才能复用，否则保旧另建唯一来源槽，**所有创建与分配都在 H4 保护下**，不能 exists→write 竞争覆盖。备份内容允许是坏 JSON，因为目的为保源，不是合法事实。
- 槽名包含本次来源标识/不重复序号；已有任何不同内容都不覆盖。配额或槽位满时停止本次恢复/覆盖，不无限创建文件。读失败只能报告原文件不可读，不能拿空串假充本次坏源，也不能声称已备份。
- 来源副本独立读回与 raw_text 全等后才返回 success；状态只显示真实成功的路径。保源状态与合法事实状态分开。
- 主文件合法则优先主文件，不能因旧 bak 合法而回退较旧历史。缺主与主损坏、读失败三者独立处理；主损坏先保当前全文。严格合法 bak 也只证明内容可解，不证明它最新；现有旧备份缺 generation 时只在既有明确恢复策略下使用，并报告来源/未确定的新旧关系，不能把“从旧快照恢复”说成原最新动作已完成。
- 事务恢复只用同 tx_id 的已验证 redo 数据和提交决定。孤立 tmp 或较旧 bak 不参与“猜最新”；不同 generation/无提交证明的 tmp 保留待核验。
- 替换/读回失败后**不得无条件 fs.write(path, old_text) 回滚**：这可能盖掉第三方新提交或再次截断唯一正本。必须仍持同 guard、检查 H3 expected 全盘字节/版本；不成立就 freeze/unknown、保留源副本，由 H4 恢复。

调用点：M2 的 view/diag/迁移换此 helper；M5 的 tmp 读取改为有出处的候选，禁止盲覆主；M7 的 corrupt/latest/显式恢复备份用它，不覆盖更早 recover。M3/M6 复用保源结果，不新建一套 bak 逻辑。

原生验证：不同旧 bak、相同 bak、新 bak、bak 为目录、槽满、写失败/读回不等/目录读失败；逐文件核**旧来源和本次全文均在**，失败主字节不动且禁写。复跑 M2 r13 的 corrupt_view_stale_readable_backup、truncated_nonempty_view、bad_source_diag_directory，以及 M3 正负例和 M7 preserve_old_recover/backup_slots_are_dirs。关闭 D-M2-01/07 与 R-M7-02 的保源子项；事务完整性仍需 H4。

## 4. H3：单文件原子写与严格写后核对（M2）

现有 writer：`saveState` :999（:1006直接写）、`saveTasks` :1011、`saveReceipts` :1024、`saveEvents` :1040；`commitBound` :5533/5543；M5 `m5_save_attach_index` :9613、`m5_attach_index_tmp_clear` :9664、`m5_save_attach_index_commit` :9670；M6 `m6_save_history_view` :4028、`_persistAiLog` :7450；M7 overwrite :1502。

```text
fn hf_storage_caps()
fn hf_atomic_write_json(path, value, schema_key, expected_raw, guard, write_id)
fn hf_atomic_write_text(path, body, expected_raw, guard, write_id)
fn hf_verify_written(path, expected_body, schema_key)
fn hf_cleanup_stage(stage_ref, guard)
```

`hf_storage_caps()` 返回已实证的 strict_decode/atomic_replace/durable_sync/held_lock 或等效事务能力；未具备返回 false，不能调用臆造的 fs 方法。下面的 replace/lock 是**能力要求**，由适配器绑定已验证 API，不是声称现有 `fs.rename` 能实现。

流程严格固定：

1. 持有效 guard；读取当前原文，读取失败不当不存在。核 expected_raw（全盘内容，不只目标任务 version），防整盘陈旧写；新建明确使用“未存在”期望。
2. 生成 body，严格 JSON/schema 核验；目标原文需保护时 H2 完成后才继续。stage 与目标在相同原子替换域，使用唯一 write_id；拒目录/路径越界，不共享固定 tmp。
3. stage 创建/写入/持久化；独立读取 stage，body 精确一致且严格 schema 成立。失败留可核 stage/源副本，目标未动。
4. 经实证的同文件系统**原子替换**发布 stage；持久化目标与必要目录元数据。不得用“先删目标再改名”或“读 tmp 后直接 write 主”替代。
5. 独立读回目标：精确 body、严格完整 JSON、schema、全值/全成员比较均通过才返回 `{success:true, published:true, verified:true,...}`。替换已发生但读回失败返回 published/unknown，绝不能声称未写、自动重做。
6. stage/marker 清理有明确返回并独立核验。清理失败不抹掉已证明的业务提交，但留下可恢复记录/cleanup_pending；不能因清理失败盲回滚，更不能吞异常后说已清理。

替换/同步原语还必须维持宿主 jail、目录/链接检查、文件大小/总配额/entry 限制。prepare 的完整快照、备份、stage、commit 决定都占配额，提交决定发布前预检并在同 guard 下确保可完成的空间；不足则保源拒绝。不能绕过配额让新协议可写，也不能为腾空间删除唯一未完成恢复依据。

采用 `{success, published, verified, kind, why, stage_ref, cleanup_pending}`，区分未写 rejected、已发布但未知、完整核验成功。单文件发布成功不能直接等于 task+receipt+event 成功。

调用调整：

| 轮次 | 调用点 | 调整 |
|---|---|---|
| M2 | saveState | 保留 `_VIEW_STATE_OK`/禁止恢复主体；用 H3，返回真实结果；新意图保存失败不得继续发业务动作；读失败/扫描 pending 不覆原输入 |
| M2 | saveTasks/saveReceipts/saveEvents、迁移、commitBound | 普通业务写进入 H4；这些兼容函数仅在授权的 guard/事务或明确维护上下文调用 H3，禁止脱离锁整盘覆盖；维护迁移也持同 guard |
| M5 | m5_save_attach_index、commit 包装、tmp_clear、reconcile :10130–10189 | 统一 H3；把提取、schema、全成员比较和 cleanup 结果贯通；只有真正核验成功才清 stage，不凭 len/三字段判整份成功 |
| M6 | m6_save_history_view、_persistAiLog | H3 保存明确 schema；读取/恢复未决不覆盖已有文件。recordModelMeta 必须消费日志保存结果；缓存未获出处持久化证明不得宣称可重开 |
| M7 | m7_tasks_explicit_recover(false) | 在 H2 保源+H4 恢复维护 guard 下 H3；严格读回全等才清 pending，失败保持保护 |

原生验证：stage 写/读/校验失败、replace 失败、发布后读回失败/不等、清理失败、目录目标与配额不足；磁盘实际 body 与返回 published/verified 对应。所有错误保源，未发布不得改变主，已发布但未知不报成功。H3 不能单独关闭并发或多文件事务。

## 5. H4：持有期互斥与可恢复关联提交（M2 底层，M4/M5 接入）

### 现有根因与替换范围

- `_acquireTaskLock()` :4994–5064，普通 fs.write :5048/读回 :5055；`_releaseTaskLock()` :5065–5095；`load()` :1539–1576 启动按 TTL 清锁。这些都是 advisory 文件协议，不是线性化点。
- `runCommandBound(cmd,t,params,expected_version)` :5161–5321，拒绝分支及抢不到锁分支仍直接 saveReceipts；`runCommand` :8333、`recordReceipt` :5851 先写 pending。
- `commitBound(t,expected_version,cmd,result)` :5408–5612，放锁 :5610 后 caller 才 logEvent；`commit(t)` :5945、`commitSucceeded()` :6003；`bootReconcilePending()` :5632；`_setReceiptStatusFinal` :5369。
- 完整 after 比较 :5566/:5704 已有改善，**保留、不退回三字段比较**。不足在于准备日志不完整、事件在外层、没有原子锁与共同恢复协议。

### 拟新增签名

```text
fn hf_guard_acquire(scope, owner_context)
fn hf_guard_release(guard)
fn hf_read_authority(guard)
fn hf_begin_command(cmd, task_id, params, expected_version, intent_key)
fn hf_bind_commit_spec(event_spec, derived_writes)
fn hf_commit_command(tx, after_task, event_spec, derived_writes)
fn hf_recover_commits(guard)
fn hf_verify_action_bundle(action_id, guard)
```

guard 覆盖**整个应用权威 Store**，不是单任务文件：跨任务/跨项目同技工预约扫描和整盘写必须同锁。锁的 owner_context 来自宿主独立实例；业务 tx 另绑定真实会话，不能从 state 伪造。互斥与业务授权分开：未登录的偏好加载/保源/既有格式迁移可以获得受限存储维护 guard，但它不给任务命令、任务覆盖恢复或 final 升级授权。优先选 OS 持有期锁（进程退出自动释放）；若平台采用原子 CAS + fencing，必须在**实际发布点**校验 fence，不能只在提交前读一次。

TTL 只用于诊断，不能剥夺仍有写权的活持有者。崩溃回收先获得同一真实锁，再核未完成日志；释放只释放自己持有的实际句柄/fence，不能写空别人的锁文件。旧 tasks.lock 保留为兼容诊断，不能继续按 TTL 清空来代真实回收。

### 事务协议与线性化点

1. `hf_begin_command` 获得 guard、恢复屏障通过、严格重读全盘；重新校验主体/角色/到期/撤权、项目、幂等、expected_version、源状态。跨任务冲突参数保留到发布点。所有 reject receipt 也由同边界写，不允许锁外保存旧 RECEIPTS 整数组。
2. 原键/同 fp 的 final 先返回历史 outcome，**在当前源状态/版本拒绝之前查原动作**；同 key 异 fp 在 pending/unknown/final 等占用状态全部冲突。未提交的 rejected/orphan 重试条件仍必须核查事务决定，不能仅靠内存状态。
3. 从锁内最新 before 生成隔离 after，再合并到本次严格重读的全盘，只更新目标任务；禁止直接落调用者陈旧 TASKS。保全无关任务更新。caller 提前 mutate 的对象只是候选，不在提交成立前公开成权威状态；失败/unknown 必须回读或进入恢复屏障，不能把已经 mutate 的快照“回滚”成成功事实。
4. 新准备日志 `tx/<tx_id>.prepare.json` 至少包含：schema_version、tx_id/action_id、intent_key/fp、actor/project、cmd、真实 params、expected_version、**完整 before/after、完整原 result、精确 event、全盘前后投影内容、附加派生写描述**。action_id 在准备时固定，原事件 at/字段也固定；不要恢复时用新时间/`cmd_recovered` 猜出另一个事件。
5. 准备文件 H3 发布并独立严格核验/持久化。此时 tasks/actions/events **尚未修改**。准备写失败可明确 rejected；准备已写但响应未知，则用固定 tx_id 查询，不生成新动作。
6. 再核提交前主体/权限与业务冲突。通过后原子发布 `tx/<tx_id>.commit.json`，含准备文件标识及完整内容一致性绑定（不能依赖 M5 指纹）。**commit 决定是本动作线性化点**；它必须持久化且能严格读回。每 Store 同时最多一个待投影事务，避免跳过未恢复提交继续新动作。
7. 决定已存在，H3 幂等发布 task/receipt/event 的投影。三者共享同 action_id；receipt 的 final/result 和原 event 来自准备记录。每个投影失败留下持久 redo 及恢复未决，禁止后续普通命令、禁止成功提示。决策前崩溃不会有业务投影变化；决策后崩溃必须 redo 收敛，不能当成未提交重做。
8. 完整事实独立读回，`hf_verify_action_bundle` 核全部 after、原 result、同 action event 与事务决定一致；通过才发布 applied 标记并解除屏障、返回 new_commit。日志 cleanup 独立处理，不能删唯一恢复依据。原 result/历史动作依据须保留到明确的安全归档，不能清理后用当前较新任务猜旧动作。
9. 启动及每次权威读取先检查恢复决定。拿真实 guard 后幂等补完缺失投影；读取者在恢复完成前也必须通过屏障，不能读三文件半套。原始文件的旧/新 reader、查询、boot 迁移都接同边界；无认证不得借业务恢复写绕过权限，未登录可保持恢复未决并阻断，登录授权后收敛。

日志是提交/恢复依据，不是另一套独立可修改业务库；禁止后台和 UI 各写一份“权威”。现有 tasks/actions/events 文件名可保留，所有应用消费者必须经过上述决定/恢复屏障。只加 WAL 而不改读者/旧写者不算完成。

旧 pending 无完整 after/event 时继续 unknown，不能推定 final；版本相同也不能证明动作没执行，尤其 togglePin 不增业务版本。保留 M6 收藏专用核验，H4 接入不得误改其语义。

### 兼容与逐模块责任

- **M2** 保留现有 `runCommandBound(...)`、`commitBound(...)`、`commit(t)` 的外层签名作薄适配；内部统一使用 `_HF_TX`，不再拿 `_PENDING_*`/LAST_ACTION_ID 猜事务。`runCommandBound` 只开始/校验命令，不单独写半套 pending。`commitBound` 委托 H4，需要预绑定 event_spec。
- **M2** `recordReceipt`、`_setReceiptStatusFinal`、`finalizeLastReceipt` :5333 不再提供按当前 task/cmd 的兜底 final；按固定 action_id/tx_id 写。`bootReconcilePending` 委托 H4，不再按 version 推断未知，也不凭 final 名称补造事件。
- **M2** `logEvent` 的“关联业务事件”改为验证已在该事务提交的精确 event，不能再放锁后追加。独立审计事件有独立受锁保护的追加事务，不能误用上一动作 ID。
- 模块 caller 要在 commit **之前**调用 `hf_bind_commit_spec({kind,after,...}, derived_writes)`，把现有 logEvent 的完整参数前移；既有 payload、命令权限和业务规则不变。成功只能来自 H4 outcome；不能用“先 commit 成功，稍后 logEvent”保留双写。
- **未接入 event_spec 的旧 caller 必须 fail-closed，不退回旧 writer**。M2 候选只能验收已经接入的范围；M3–M7 待其轮次接线和独立验收，不能因为共用函数已合入给后续模块 PASS。
- **M4** 把同技工跨任务冲突 spec 放入 tx，扫描锁内最新全盘且发布前复核；权限/设备/预约 token/版本等原守卫保留。
- **M5** 附件字节与 canonical 先 staging/核验；提交日志记录附件 ID/位置/内容绑定，task+receipt+event 为主事务，索引为可从权威 task 重建的派生投影。无法核验/恢复索引时禁止 READY/完工/验收成功；不把 orphan/foreign/tmp 直接升级权威件。保留既有轮次、固定集合、canonical 主闸与隔离规则。

### 原生验证 H4

必须有驱动内的**两个独立认证原生上下文共享同一个隔离 Store**，在“读旧版本后”“冲突核验后”“实际发布前”设屏障。接单竞争唯一赢家；不同任务同技工重叠预约唯一成功，相邻均成功；无关任务更新不丢。再覆盖活持有者超过 TTL、持有者崩溃释放、同 actor 不同实例、旧 fence 迟到发布、抢不到锁时 reject 历史不丢。

逐点注入：prepare 写/读回/持久化；commit 决定发布前后；task/receipt/event 任一投影写前后、读回失败；applied/cleanup；丢响应；相同 Store 退出后重开。决策前主事实不动，决策后完整恢复同 action/result/event；重复恢复不增加业务 version/事件，不生成第二任务。较新任务也可查询旧 v1 动作 result，不能要求仍 OPEN。关闭 D-M2-03/05 与 D-M4-03 必须有这些原生证据，不接受两个独立 Store 或 Python 文件协议替身。

## 6. H5：统一 outcome 与原动作查询（M2 生产，M3 消费）

现有：`receiptFor` :5819、`findReceiptByKey` :5886；`m2ReplayAtTop` :8289；`_authorityCheckConfirmedOpen` :8377、`_authorityHistoricalConfirm` :8425；`confirmDraft` :8463；`createDraftFromPanel` :7771；`confirmDraftModelBound` :7468。

当前源码与 M2-r13 冻结候选应区分：

- 空面板 :7493–7523 已核 commit_ok/final_action_id 并接历史标志，不再单凭 non-nil 成功，保留这项修复，补动态验证。
- 正常有内容 :7727–7733 仍要求 confirmed_open=true；创建重放 :7891 返回 historical_confirmed=true/confirmed_open=false，仍会被正常外层拒绝。
- 历史 helper :8426–8460 返回 confirmed/action_id，没有完整 original_result；按 task/command 扫“最后 final”也不足以证明是该原意图确认动作。

```text
fn hf_action_outcome(kind, action_bundle, current_task, reason)
fn hf_query_original_action(actor, intent_key, command, task_id, fp)
fn hf_confirm_outcome(intent_ref)
fn hf_outcome_is_success(outcome)
```

outcome 固定为 `{kind:new_commit|historical|unknown|rejected, task_id, action_id, original_result, current_task, current_status, reason, tx_id, retry_key}`。只有完整权威 action bundle 允许 new_commit/historical；unknown 的非空对象没有成功含义。当前任务读失败但旧动作可证时，current_task=nil/当前状态未知，不能用内存值冒充另读结果，也不能抹掉原动作成功。

`hf_query_original_action` 刷新可信授权后按 actor/intent_key/cmd/task/fp 精确定位；create 与 confirm 两动作在 intent 记录固定关联 ID/key。历史校验必须匹配**该 action_id 的完整 result/event**，不是同 task 的任何一条 final。同 key 异参一律 conflict/rejected；未知保持原 key/原文/不可变 payload，不清 intent、不换新 key、不创建空草稿。

调用点：

| 轮次 | 位置 | 修改 |
|---|---|---|
| M2 | createDraftFromPanel :7805–7809 | H3 保存不可变意图成功才发命令，保存失败明确拒绝；原键与原 payload 不重建 |
| M2 | createDraftFromPanel :7844–7920/8056–8096 | 新提交/创建已成功但确认未知/历史推进均返回统一 outcome；create+confirm 可作为两个可恢复动作，intent 保留阶段；不把后者未知误当整项成功 |
| M2 | confirmDraft、m2ReplayAtTop、receiptFor/查询 helpers | H4/H5 查固定原动作，完整传递 original_result；new_commit 也核完整事件，历史不要求当前 OPEN |
| M3 | confirmDraftModelBound :7493–7534 与 :7715–7762 | 保持 `fn confirmDraftModelBound()` 形参签名，目标返回统一 outcome，替换 bool 返回协议；两条分支同判据，historical 与 new_commit 成功，unknown/rejected 保输入与键；成功清理也消费 saveState 结果，不因清理失败再做业务 |
| M3 | draft_submit_btn :13002，confirm 调用 :13009 | 保持按钮/布局；将 `_submit_ok` 布尔分支改为 outcome.kind 消费，unknown 显示待核验而非成功，拒绝显示原原因；保留已删除固定 OPEN/当前选中任务推断的修复，未知不清输入 |

原生验证：真实按钮空/有内容，正常一次、双击、丢响应、同 Store 重开；原 v1 final 后任务推进 v9/ACCEPTED；所有占用状态同 key 异参；相同内容新独立意图。核 task 数量/version/action/event 次数、完整 original_result、当前状态、屏幕反馈和原输入/key。D-M2-02 只在 M2 权威生产与 M3 两条真实消费都通过后关闭。

## 7. H6：来源 schema 与请求日志分型（M2 定契约，M6 接入）

### 现有位置

阶段 `m6_cmd_request_phase` :3959–4023，:4005 把 `m6_ref_snapshot("task",t.id)` 放 source_versions；引用快照 :4160，历史来源快照 :4171，来源漂移 :4195、refs 漂移 :4218、共同来源闸 :4245。loader :4339–4342 使用 `refs: (_irefs or [])`。日志生产 `m6_request_device_history` :2348、`m6_request_phase_meaning` :2583；`recordModelMeta` :7339/7379；恢复 :7392/:7424 强制全部 rid 非空；保存 :7450。

### M2 新增共用契约签名

```text
fn hf_source_version(task_id, task_version, evidence_version)
fn hf_reference(ref_type, ref_id, task_version, evidence_version)
fn hf_validate_sources(source_versions)
fn hf_validate_refs(refs, allow_empty)
fn hf_validate_history_cache(value)
fn hf_normalize_ai_log_entry(entry, legacy_mode)
fn hf_ai_log_is_provenance(entry, binding)
```

这些是纯结构构造/校验，不从当前 UI/任务自动补来源。实际版本读取、权限/漂移、真实 provider 调用仍由 M6 实施并验证。

- **SourceVersion**：`{task_id,task_version,evidence_version}`。只用于实际送模的来源任务集合，阶段至少包含本任务送模时的快照。不能用 `{ref_type,ref_id}` 替代 task_id。
- **Reference**：`{ref_type,ref_id,task_version,evidence_version}`，ref_type 仅 task/asset/space；task 引用核任务/证据版本，asset/space 按既有 facts_version 闸。source_versions 与 refs 是明确不同的 schema，统一的是各自产生/保存/恢复/读取契约，不是强行合成一种对象。
- **HistoryCache**：明确 schema_version，保留既有 task_id/kind/ts/items/actor/project/task_version/request_id/expires_at_ms/facts_version/evidence_version/source_versions。suggestion items 必须有完整非空 refs；manual 可以显式空 refs。解析完整合法但旧缺快照时保源、按未知，不能用当前版本填造旧模型出处。
- **AILogEntry v2**：`{schema_version,entry_kind,entry_id,at,request_id,result_kind,task_id,project_id,actor,...原诊断字段}`。entry_kind=request_result|diagnostic。真正请求结果要非空 request_id；成功与 STALE 仍有严格绑定。未发请求的 NO_SERVICE 是 diagnostic，有 entry_id、request_id 允许空且不得作为 provenance。
- 旧日志兼容：无 entry_kind 且 result_kind=NO_SERVICE/request_id 空、其余必需字段类型合法，明确规范化为 diagnostic；保留原文，不补造请求 ID。其他缺 rid 的成功/STALE、坏 at、非法中间项一律整份拒绝并保源。不得用“所有缺 rid 都算 diagnostic”放宽。
- `hf_ai_log_is_provenance` 只认可绑定一致的合法 request_result 成功，STALE 同 rid 作废优先；diagnostic 永不证明缓存有出处。一条合法 diagnostic 不毒化其他合法请求结果。

### M6 各调用点如何改

| 子项/当前调用点 | 接入与必须保留的约束 |
|---|---|
| B1：m6_request_phase_meaning :2574、cmd :4005 | 送模前固定 SourceVersion；生产 stage cache 用该 snapshot，不在回包后补当前版本。保存/来源闸使用 hf_validate_sources；m6_ref_snapshot 仅用于 refs |
| 历史生产 m6_request_device_history :2331、m6_history_source_snapshot :4171 | 从实际送模历史集合采快照并复用 hf_source_version；保完整集合，不省掉第二来源，不补造非送模任务 |
| refs 生产/消费 :4160/:4218/:4047/:4245 | 复用 Reference 契约；load/render 保留逐引用可见性、事实/证据版本、到期、主体/项目与出处双闸 |
| B2：m6_load_history_view :4311/:4339–4342 | H1 严格 parse + HistoryCache schema；显式 `let kept_refs=nil`，确认数组后原值赋给 kept_refs；suggestion 缺/坏/空 refs 明确拒，manual 明确空数组；**不用数组 or []，不悄悄跳过非法项** |
| C：两个 NO_SERVICE producer :2348/:2583 与 recordModelMeta | 写显式 diagnostic；真正 provider 请求写 request_result；共享规范化/validator 在写入和恢复两侧同时用；recordModelMeta 消费 H3 日志保存结果 |
| C：m6_restore_ai_requests_log :7392 | H1 完整解码、全部项分型验证，再一次性并入；读失败保持未恢复/冻结已有文件，不能 :7394 先置 restored=true 再允许后续保存覆盖旧日志；恢复成功或确定缺文件才置 restored |
| C：_persistAiLog :7450、m6_history_provenance_ok :4124 | H3 保存相同 schema；读恢复未决/损坏不写；provenance 过滤 diagnostic，成功/STALE/绑定规则保留；不删除门禁换显示 |
| 保存与 render：m6_save_history_view :4028、m6_history_view_usable :4447 | 写入前同 schema，读回严格；load/render 用同 validator 与现有语义重核；成功日志未落盘缓存不能宣称可恢复 |

原生验证：阶段真实双引用生成→保存→退出→同 Store 重开→可信登录后正常正文/两引用全字段；phase_producer_cache/history_source_cache 冷 seed 仅核加载数组保值，不能代真实重开链。只改变/撤权第二引用即失效，无残留建议。应用实际产生“成功→NO_SERVICE→成功”再重开，成功出处恢复，诊断不验证缓存；STALE 否定、坏 at、缺 rid 成功、非法中间项、截断及读失败保源。需观测 AI_LOG_RESTORED/AI_LOG_CORRUPT、恢复条目和实际消费结果，盘字节不变不等于内存恢复成功。全部通过才关闭 B1/B2/C。

## 8. H7：M5 全成员核验与完整件指纹（M2 通用比较，M5 实证）

当前 M5-r13 审的是旧冻结 M5-r10，八场未执行 writer/probe；当前 main :9836–9845 已有 M6 移入的位运算语法适配。它不能代新 M5 候选独立复验。D-M5-04-B/C 沿原编号保持，先拿实际原生值，不预判算法仍坏。

现有函数：`m5_index_field_eq(a,b)` :9680（减法隐式转换/字符串回退）；`m5_reconcile_attach_index` :9913，逐成员核 :10162–10165 只比 id/round/lifecycle；`m5_xor8` :9411、`m5_fnv_mix_byte` :9429、`m5_hex32` :9441、`m5_fingerprint` :9455；probe :9729；`m5_read_content_signature` :9536、`m5_content_signature_equal` :9548；上传 :9252，open :10276、verify :10389。

拟新增 M5 适配签名（**M5 轮的调用/领域包装，不重复实现共用底层**）：

```text
fn m5_index_verify_complete(expected_items, stored_items)
fn m5_verify_registered_content(item, expected_task_id, expected_round)
```

- B：index_verify 委托 H1/H3 `hf_value_equal("m5_index",...)` 核**全部成员/字段**，包括 task_id、project、uploader、文件/canonical位置、size、指纹、轮次、生命周期、验证时间及已有扩展字段。parse/extract/len/type/每成员 actual 记录在测试根；不能把所有 numeric-like 值强转后视为同一类型。writer 成功、全成员/字节成功之后才 cleanup，清理失败独立挂待处理，失败副本保全。
- 旧顶层数组与 v3 信封都严格认可，v3 校验 format/version/items，不把任意带 items 的对象当 v3。迁移保存原字段与原文；invalid/foreign/orphan 保原分类，不升 READY。
- C：保留当前指纹算法及现有 `sha` 字段的兼容语义，它实际是代码声明的**码点分类序列 FNV 辅证，不是 SHA，也不是标准 UTF-8 字节 FNV**。不要把它用到 H2 来源证明/H4 提交决定或拿它替代 canonical 全内容主闸。本轮不要求批改历史 sha、不追认坏件、不扩展二进制附件能力。
- m5_verify_registered_content 统一现有 open/verify 的任务/权限/轮次/canonical 全内容判据；M2 的精确比较可复用，M5 仍负责文件内容与轮次规则。read 失败不是空文件成功；非 UTF-8 件若当前文字 IO 无法无损处理，明确拒绝，不宣称支持。
- 上传存盘+canonical 独立读回后再登记；READY 只有主内容、canonical、登记 size、完整 fingerprint、任务/轮次与索引持久验证均成立。:10480 的保存结果必须消费，索引写未知时不能 :10481 返回干净 success。m5_open_attach_bound 的所有生命周期保存出口同样消费结果。

原生验证 B：新候选冷开解析/运行零错误后跑旧数组/v3两成员、退回 tmp、foreign/orphan、恢复失败、完整成员字段差异/类型差异。核 m5_save_verify 的 read/parse/extract/len/members actual 与实际全盘、cleanup 返回和审计；不是改成功旗标让测试过。

原生验证 C：先跑 literal 分步 xor8、hex32(1)、offset、一次 mix、乘法/模、ASCII/中文/控制字符完整遍历，与独立 oracle 比对。源码注释中的预期值须独立重算，不能照抄当实测。再真实上传新完整件→主/canonical读回→open与verify都成功；中间内容同长度篡改、丢主/丢canonical、登记指纹不等、跨任务、轮次不等，两入口都拒信。完整件不得仅因指纹实现错误被误归 CORRUPTED，坏件不得靠更新登记摘要“修复”。B/C actual 齐全才关闭 D-M5-04。

## 9. 模块调用点清单（先底层，再本模块）

H1–H7 的共用函数、结果类型、能力适配与纯结构 schema **全部由 M2 轮负责**。下列模块不得另建 JSON/backup/lock/txn/outcome 底层。新发现 helper 缺口应退回 M2 共用修订并触发受影响回归，不能在 M4/M5 各复制一套。

| 模块 | 当前入口/行号（本轮 main） | 本轮后续实施责任 |
|---|---|---|
| M2 | loadViewState :544；saveState :999；history helpers :1092–1232/:1728–1972；load :1539 | H1/H2/H3 接入偏好、历史迁移/恢复、严格权威读取；不清原意图，不还原会话 |
| M2 | 锁/命令/提交 :4994/:5065/:5161/:5408；pending/final :5333/:5369/:5851；boot :5632 | H4 唯一 guard/提交/恢复边界；拒绝回执也在该边界；清除旧宽容 fallback |
| M2 | createDraftFromPanel :7771；confirmDraft :8463；cancelTask :11296；重放/查询 :5819/:5886/:8289/:8377/:8425 | H5 权威结果；create :8056 前绑定 create_draft 事件（原 :8070）；confirm :8501 前绑定 confirm_draft（原 :8507）；cancel :11316 前绑定 cancel（原 :11318）；固定原 action/完整原 result；其他模块 caller 未接线就拒写 |
| M3 | confirmDraftModelBound :7468；TextInput pending 恢复 :13807；draft_submit_btn :13002 | 有/无内容共用 outcome；有效输入/intent/key 正常恢复；只接反馈与状态，不改控件/布局；H1/H5 均复用 |
| M4 | acceptTask :8521、assignTask :8545、bindAsset :8592、unbindAsset :8663 | 现有 commit/logEvent 对：:8534/8536、:8581/8583、:8651/8653、:8681/8683。将原完整 event payload 在 commit 前绑定，事件作为同一 H4 提交；保守卫、消费 outcome |
| M4 | proposeAppointment :8693、confirmAppointment :8772、rejectAppointment :8838、cancelAppointment :8882、rescheduleAppointmentFromForm :8933 | 对应 commit/logEvent :8760/8762、:8818/8820、:8863/8865、:8913/8915、:9025/9027 前移 payload；冲突 spec 由 tx 持有，同一 Store guard 内全盘扫描/发布，保跨项目冲突及相邻规则 |
| M4 | startProgress :9040、recordProgress :9094、reassign :11327；_m4_disk_tech_conflict :5102 | commit/logEvent :9085/9087、:9112/9114、:11360/11362 接 H4；盘未知拒绝，不锁外直接写事件；角色/设备绑定变化原规则保留 |
| M5 | writer/load/reconcile :9613/:9700/:9913；open/verify :10276/:10389 | H1/H2/H3/H7 全内容核验、失败副本/cleanup；原生算法 actual；两个附件消费入口保存结果全消费 |
| M5 | addEvidence :10738；quarantineEvidence :10803；submitCompletion :10841；acceptCompletion :11040；rejectCompletion :11157 | 原主 commit/logEvent :10786/10789、:10831/10833、:10987/11025、:11133/11141、:11233/11284：预绑定事件，附索引派生写描述；保 canonical、固定引用/轮次。:11003/:11260 的 rollback 与 :11017/:11275 的失败审计走独立受锁审计事务，不假借原 final action；unknown 不做盲反向业务写 |
| M5 | boot 审计事件 :10084、legacy清理事件 :10851 | 明确维护/审计语义，不复用上一 `_LAST_ACTION_ID`，不升级为新业务成功；只在合法维护 guard/恢复上下文写 |
| M6 | phase/history/refs/source/log 入口见 §7 | B1/B2/C 接 H6；H1/H3 保存恢复；不碰布局，不重复底层。收藏 togglePin :11375/:11473 原不增业务版本，保持 marker 专用协议；若事件接 H4，必须带完整偏好事实，不能套 task version+1 判据 |
| M7 | m7_tasks_mark_corrupt :1422；m7_tasks_explicit_recover :1460；commands :1529/:1534；load :1595 | H1 共用任务 parser 已由 M2替换；本轮收口 H2备份/H3受控替换/H4维护guard、keep合法性复验；失败保持pending，普通save/command/create守卫不撤销 |

表中行号为入口锚点；构建方要核函数内**所有**保存返回、错误/未知/清理出口。接入不包括旧 WAgent/backend/contracts 重写，也不启动旧服务补原生能力。

## 10. 按模块轮次的实施顺序与每步门禁

**每一行完成之后：交同字节新候选，由外部驱动原生加载，业务解析错误必须为 0，且运行/type/scope 错误为 0。非零就停在该步，不把后续结果写成通过。** 当前没有执行这些步骤，以下是构建方/驱动后续任务。

| 顺序 | 所属轮次 | 实施内容 | 本步原生验证/退出条件 |
|---|---|---|---|
| 0 | M2 | 冻结当前工作树实际源码/包/digest/宿主/harness；纳入已有最小语法修复，保留他人修改；能力探针 | 冷开真正作品包，登录页渲染，解析0；严格解码、码点/类型、IO/替换/持有锁实际值齐全。无原子能力明确技术阻塞 |
| 1 | M2 | H1 严格 decoder/分步扫描/schema/value_equal；统一 tasks parser 薄包装 | 正负 corpus actual；合法 JSON 不误拒、尾随/缺值/截断全部拒；解析0 |
| 2 | M2 | H2 精确保源与来源选择；H3 writer/读回/cleanup 适配（原子部分依赖步骤0） | 旧bak/新源/目录/槽满保源、每个写失败出口真实；解析0；原子未具备不得宣称H3完成 |
| 3 | M2 | view/history/迁移/所有权威读接 H1–H3 | 重跑 M2 r13 冷恢复/非法行、M3合法view正例、M7 closed_junk；原文/intent/key/嵌套结果与冻结源一致，坏源禁写；解析0 |
| 4 | M2 | H4 持有期guard +完整 prepare/commit决定/恢复屏障；H5 outcome/query；H6纯schema构造；H7通用比较 | 同盘真竞争、逐点故障/丢响应/重开；纯schema正反例；缺控制分别BLOCKED，不造PASS；解析0 |
| 5 | M2 | 本模块 create/confirm/cancel、查询/拒绝回执/boot/维护入口接新边界；旧 writer fail-closed | 核任务/原回执/精确事件完整一次；旧pending不误final；未知保键，后续版本查原result；解析0；D02的M3消费仍待其轮次 |
| 6 | M3 | 两条确认按钮 outcome 消费；有效持久输入恢复消费 | ASCII/中文/转义/emoji原文、intent/payload/key恢复；可信登录后控件恢复；历史v9/未知两分支不假成功，真实重试不重复；解析0 |
| 7 | M4 | 本模块接单/指派/绑定/预约/开工/进度/改派预绑定事件，冲突spec用同guard/tx | 真实M3创建→M4动作主链；同盘接单与重叠预约唯一赢家/相邻成功，权限变化发布前复核；解析0；关闭D-M4-03需原子动态 |
| 8 | M5 | 新匹配候选先复验冷开，然后index全成员writer、content/probe、附件/完工/退回caller接线 | 不能再交M5-r10旧冻结包；B的每成员 actual与C算法/真实完整坏件双入口证据；正常/退回/重开恢复；解析0 |
| 9 | M6 | sources/refs/cache/diagnostic日志全部生产+保存+恢复+消费接H6/H1/H3 | 双refs不丢、阶段source字段一致，第二来源变更失效；实际成功/NO_SERVICE/成功重开不毒化，STALE及坏源拒信；解析0 |
| 10 | M7 | keep/overwrite恢复/备份/普通写禁写最后收口 | closed_junk两反例、合法修复keep、受控overwrite严格读回、每故障保持pending，同Store重开；解析0 |
| 11 | M7 | 当前最终候选串行回归与独立Review证据索引 | 六模块hardfix及原P0/38业务/12UI保留；没有执行的分项仍NOT_RUN/BLOCKED，不用本计划签通过，不公开发布 |

步骤0–5只由 M2 轮修改共用区域与 M2 caller。M3–M7 每轮只修改表中本模块 caller/适配与验证资料。即使共用函数物理位于 M7 命名块（如 tasks parser），它的**底层改动归 M2 轮**；后面模块复用，不重新修一份。

### Splash 语法约束（每一步都适用）

- **禁止 `(表达式).方法()`。先算变量，再对变量调用方法。** 同样把本次触及的多级临时返回链拆开，尤其 serializer、mix/hash/probe。
- 不使用 `is_password`。不添加/修改密码控件或布局。
- 使用已实证普通字段 `success`；失败捕获优先 bare `catch`，不引入已有 `catch _` 的 scope 风险；新变量名不能遮蔽内建。
- 不假设 typeof、数组 `or []`、隐式数字转换符合常见语言；依赖实际类型/数值/码点探针。
- 主脚本函数定义与启动调用顺序必须校核。try/catch 不能兜解析期错误；grep 静态检查不能代原生解析。

示意（只说明合法表达形态，不是已运行的代码）：

```text
let env_value = m5_index_envelope(arr)
let body = env_value.to_json()
let mixed_value = m5_fnv_mix_byte(seed_value, byte_value)
let mixed_text = mixed_value.to_string()
```

## 11. 原生 harness 交付方式及明确的控制缺口

本轮没有写请求、准备夹具、签包或启动任何宿主。后续仍采用两段式：构建方/审查方准备明确请求和候选，**驱动在 agent 沙箱外执行**，返回 summary/result/log/盘面/PNG/MANIFEST，再由独立审查读证据裁决。不得自行启动/kill宿主，也不因某次预检rc而伪造业务阻塞。

本轮读取当前 `driver/harness/native_harness.py` SHA-256 `8141b4de36e8a248a1b7ed0b9d430fa3ee464ccbc65fc927ef1de40be5ef34c8`，request.schema.json SHA-256 `d5d79a63eafa7ebf2165c7fd8489feea30f91525730b86968cea82714fb08281`。固定报告宿主 SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；这里只引用报告，不宣称本轮执行该二进制。

当前 schema 接受 `module/requester/scenarios`，每请求最多32场、每批8场；seed 是复制到**fresh Store**，harness :578/:591–595 与 :859–869 逐场串行。可用 launch-hub/capture 证明真实包冷开/恢复分支；当前二进制 type/key 未实现，不能把 schema 允许字符串当已可输入。当前 schema 有受驱动控制的 ui_actions，是否使用取决于该后续请求的现有授权/禁令；本计划不调用系统自动化、不扩大授权。

| 所需能力 | 目前可表达的范围 | 后续技术交付条件 |
|---|---|---|
| 严格解析/来源/冷恢复 | fresh Store seed + launch-hub/capture，可跑负例及合法加载 | 有效签名catalog/运输包/运行资源与候选逐字匹配；actual诊断与盘面齐全 |
| 真实可信输入/确认 | fixed host type/key不可用；schema提供驱动ui_actions，但不是本轮执行授权 | 使用后续明确获准输入通道；禁止伪SESSION/手工造final，不需要读真实凭据，可用隔离合成账号 |
| 同Store跨进程重开 | 当前每场fresh复制，不是同盘生命周期测试 | 驱动新增受控 lifecycle/复开机制；与该原始Store连续运行，不把两个seed副本称重开 |
| 同盘真竞争 | 当前单宿主串行，且.launch.lock约束外部调度 | 驱动受限双上下文共享Store+同步屏障，保进程组回收/隔离；不是在既有schema偷偷加未定义字段 |
| 精确故障/丢响应/锁迟到 | 当前schema没有业务写点barrier/fault接口 | 宿主/驱动提供受控写点注入、readback拒绝、决定发布前后暂停和丢响应；测试通道只在隔离测试态，不能变生产授权绕过口 |
| 内存来源/读回actual | state可见部分缓存；AI日志恢复标志无现成完整观测口 | 隔离harness观测恢复结果/类型/全refs/日志分类，结果只写测试根，不暴露凭据/provider key |

这些是**能力需求，不是已存在的请求字段/已实现的 API**。在能力尚未交付时，相应动态测试 BLOCKED，产品源码缺陷仍 OPEN/FAIL；可以先完成可表达的正负例，不能据此签完整原子执行通过。

每轮返回材料最低包括：candidate_id/base、当前 main SHA、包资源清单/digest、宿主/harness/schema SHA、REQUEST 原文与摘要、实际运行资源匹配、完整业务 host.log（不只tail）、summary/result、逐场前后源/备份/stage/事务/投影文件字节及结构、PNG、MANIFEST、probes/隔离/回收结果。CLEAN只支持隔离/回收；日志解析0、UI渲染、事实提交、重开、并发、模型成功分别计证据。

## 12. 本轮完成与未完成

已完成：逐项核对指定报告与10:40汇总，定位当前源码调用点；归并 H1–H7、给出拟新增接口/协议/模块归属/逐调用点修改与原生验证顺序；明确原子能力和harness控制缺口。

未完成：全部业务实现、宿主能力补齐、原生解析/业务测试、模型请求、缺陷关闭、模块验收及公开发布。本文不是构建完成报告。下一位构建方从 M2 步骤0开始，完成编码后交独立 Review；界面和布局保持原样。
