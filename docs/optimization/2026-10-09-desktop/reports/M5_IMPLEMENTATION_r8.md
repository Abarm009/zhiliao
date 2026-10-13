# M5 实施报告 r8

- 模块 / 目标：M5 真实附件完工与独立验收 · r8 修复轮，唯一依据 = `M5_REVIEW_r9.md` 缺陷清单（D-M5-04，唯一 OPEN P1；D-M5-05 已 SOURCE-CLOSED 不重复修改）。只修清单项。
- candidate_id / base_candidate_id：`M5-r8-worktree` / `M5-r7-worktree`（注意：当前工作树已含 M4-r8 运输件与他人改动，r9 冻结快照 SHA=`982b7c35…`/562062B；本轮在其上叠加，未撤未覆盖任何他人改动）。
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d` + 既有未提交改动（保留）+ 本轮 r8 修复层；`app/bundle/main.splash` SHA-256=`6a7176e84a6f3692690d1d566129a0c57ea747f0c3fc5b943b9039a8b298d4c4`；bundle digest=`08c64f5600244854a63df93eb76ce3a2d1ca46f74d8f9195e00a32b43f1fd441`。快照与受影响函数哈希：`runtime/optimization/2026-10-09/M5/native/build_r8/{main.splash.snapshot,start-snapshot.json,affected-functions.json,source-traces/}`。
- 目标宿主 / 二进制：`M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA-256=`3e127963…`，本轮未变，构建方未启动）。
- 模型路由：本轮 needs_model=false，模型调用 0；未触碰 MiniMax 配置/密钥。
- 前置：M4=FAIL 挂账（M4_REVIEW_r10），按用户裁决不修 M4；但 r9 明确 B-M4-01 的加载首尾判定错误是阻断 M5 的最小依赖，授权仅修该判定，不扩审 M4 其他流程。

## 本轮修改文件与原因（严格逐条对 r9 清单「具体改法」）

全部在 `app/bundle/main.splash`：

1. **合法任务加载（最小前置依赖，:1310 附近）**：首尾闭合判定 `_tchars[0] == "["` 恒类型不匹配（宿主 to_chars 产 U32 码点，r9 引宿主源码实证），7 个合法任务盘全被误判未闭合 → TASKS 未加载 → 恢复未到达。改为与 `"[".to_chars()[0]` / `"]".to_chars()[0]` 同型比较。trim、M7 schema 门禁、pending 拒写、.recover 备份全部保留，未清盘、未移除守卫。
2. **同类字符串转换（r9 点名 basename）**：`m5_basename`、`m5_extension`、`m5_path_contains_parent_seg` 中码点==字符串字面量（`"/"` / `"."`）的比较全部改为同型码点比较。旧 basename 永远找不到 `/`，是 r8 恢复回退链产出错误路径的直接原因。
3. **索引 writer 弃用 fs.rename**：D-M4-03（r4）已确认宿主无真 rename 原子语义；r8 原生 7 场证据（tmp 0 字节、目标不变、同目录 audit 写成功）高度指向 rename 链路失败。新协议 = 宿主实证可用协议（与 `m5_reconcile_audit.json` 同款）：信封 map `to_json` → tmp 写 + 读回串比对 → 目标直接写 + 读回串比对 → 成功才清 tmp。失败保留 tmp 完整内容，`m5_load_attach_index` 回退读 tmp 恢复。
4. **索引序列化改信封 map**：`{format:"m5-evidence-index",version:3,saved_ms,items}`（map 的 `to_json` 原生实证可用；parse_json 产出的顶层数组直接 `to_json` 未实证）。loader 经 `m5_index_items_from_raw` 兼容信封与旧顶层数组（seed 仍写旧数组，兼作兼容测试）。
5. **resolver 相对优先**：可信任务登记的相对路径优先（宿主 jail 内相对语义实证），绝对路径次选，`attachments/<basename>` 兜底；相对路径同样拒 `[Error` 错误值与 `..` 父段。reconcile 重建项派生 `stored_rel`；既有索引项路径不可读时重解析修平；`m5_open_attach_bound` / `m5_verify_attach_bound` 判 MISSING 前先重解析。
6. **宿主原语探针（r9 要求的小 probe）**：boot 末尾新增 `m5_fs_probe`（仅测试根 `m5-test` 运行），分步记录 fs.mkdirs/write/read/exists/rename、`to_json` 三种变体（原生数组 / parse_json 数组 / STATE.attach_items）、to_chars 元素类型（`to_string` 区分码点 91 与串 `[`）、basename/slice 实际输出、登记附件绝对/相对路径 exists 对比，逐步落盘 `m5-test/m5_fs_probe.json`。审查方可据此直接定位原语，不再凭 0 字节 tmp 推测。

未改：业务门槛、profile/权限、D-M5-05 已删除分支、其他模块代码（除上述加载判定最小依赖）、`docs/build-loop/ACCEPTANCE.json`。

## 桌面 UI/交互变化

无新增 UI。修复后附件 tab 的失败提示（含「evidence_index 落盘/读回失败：保持拒绝态，可安全重启重试」）可随真实恢复结果渲染。

## 接口 / 数据迁移 / 旧数据恢复

`evidence_index.json` 旧顶层数组格式继续可读（loader 兼容）；新写入为 v3 信封。tmp 崩溃副本仅在目标缺失/损坏时回退使用。旧任务字节/历史不动。

## 已有别人修改的保留与适配

当前工作树含 M4-r8 运输件及其他模块改动；本轮 diff 仅触及上述函数（见 `affected-functions.json` / `source-traces/`），未撤未覆盖他人改动。不 reset/stash。

## 启动步骤 / 隔离数据位置

构建方不启动宿主（Abram 10-11 12:12 裁决）。原生验证请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r8.json`（5 场，needs_model=false），驱动输出钉扎 `M5/native-runs/build_r8_REQUEST_build_r8/`。夹具绝对 stored_abs 钉扎该目录，且相对派生路径同样可达（双重验证）。

## 覆盖的既有验收项与证据运行形态

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|静态源码断言（47 项）|prepare_build_r8.py 静态检查|全过|47/47|PASS（源码级，不代原生）|M5/r8/results/r8-fix-checks.json|
|reconcile Python 移植仿真|4 夹具副本跑 r8 逻辑移植|轮次/marker/READY 重建/孤儿保留/CORRUPTED 不追认|4/4|PASS（移植仿真，不代原生）|同上 sim 段|
|离线签名 + install_staged|hub keygen/certify/stamp/sign-manifest/verify + r10_install_probe|当前 digest 验签安装通过，源一致|rc0 全过|PASS|build_r8/offline-store-evidence.json|
|私钥销毁|签名后删除|keys 目录空|0 残留|PASS|同上 private_keys_deleted|
|真实桌面操作（冷启动零 parser/恢复/probe）|REQUEST_build_r8.json 5 场|零 parser；pending=false；index v3 落盘读回；probe 落盘|待驱动执行|NOT_RUN（等驱动）|M5/native/REQUEST_build_r8.json|
|权威状态与回执|真实上传/完工/验收命令|—|可信文本输入通道仍 BLOCKED（r9 记录）|NOT_RUN|—|
|失败与重试|保存后变更/双入口拒|—|保存后注入通道 BLOCKED|NOT_RUN|—|
|重启恢复（同盘跨进程）|同盘重开|—|通道 BLOCKED|NOT_RUN|—|
|受影响先前模块回归|m4/m6 初始化共用 STATE 根|不回归|静态断言覆盖；原生待驱动冷启动|NOT_RUN（原生）|REQUEST cold_fresh 场|

## 尚未完成

- 原生 5 场（冷启动零 parser、合法任务加载、writer/resolver/probe 实证）= NOT_RUN，等驱动执行 REQUEST_build_r8.json。
- 真实上传→保存后变更→完工/验收双入口拒、正常链/退回链、同盘重开、精确提交点故障、模型交错 = NOT_RUN（r9 记录的通道 BLOCKED：可信键入/登录、保存后变更、精确中断、同盘重开通道需驱动/宿主补齐，不需 Abram 新授权）。
- 本地 `octoscript check` 语法检查不可用：其语法与宿主 Splash 语法不同（拒绝 r7 已被宿主接受的既有代码），未作为证据；解析零错误由驱动冷启动实证。
- m5_fingerprint 在码点语义下对非 printable 字节的区分度可能退化（`_ascii_byte_value` 走字符串表反查）；canonical 全字节比对仍是完整性主闸，本轮不扩修，如实记录。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M5/r8/CANDIDATE.json`；源快照/函数轨迹：`M5/native/build_r8/`。
- 原生请求：`M5/native/REQUEST_build_r8.json`（5 场；每场均应产出 `m5-test/m5_fs_probe.json`、`m5-test/m5_reconcile_audit.json`、v3 信封 `evidence_index.json`、state.json `m5_last_reconcile`）。
- 实际测试命令：`PYTHONDONTWRITEBYTECODE=1 python3 runtime/optimization/2026-10-09/M5/native/prepare_build_r8.py`（静态 47/47 + 仿真 4/4 + 离线签名验装）。
- 编码方只标 READY_FOR_REVIEW；PASS 等独立 Review。不进入下一模块。
