# M4 实施报告 r7

- 模块：M4 接单设备与预约桌面流程；轮次：r7 修复轮（Kimi-K3，2026-10-12，Asia/Shanghai）。
- 审查输入：`docs/optimization/2026-10-09-desktop/reports/M4_REVIEW_r7.md`（FAIL；必修 B-M4-01、D-M4-03；D-M4-04 已 SOURCE-CLOSED 仅保回归）。
- 候选：`runtime/optimization/2026-10-09/M4/r7/CANDIDATE.json`（candidate_id=M4-r7-worktree，base=M4-r6-worktree）。
- 主源：`app/bundle/main.splash` SHA-256=`5430cc10579426429505dcc83db5d37cdc2b90ddf947755e05373d79167a6931`，480580 字节，10018 行；base=`37d1b1ca…`（477432 字节，与审查方冻结源 review_r1_2104/main.splash.frozen 逐字节一致）。
- 差异：`runtime/optimization/2026-10-09/M4/r7/evidence/r6-to-r7.diff`（886 行 unified diff，仅本清单两项必修 + 直接关联注释更新）。

## 本轮修改文件与原因（严格按审查方修改方案）

只改 `app/bundle/main.splash`；新增核验脚本与构建脚本（不动业务以外源码）：

1. **B-M4-01（渲染阻断）**：审查方改法 = 「先在固定宿主验证实际字符串/数组 API，替换不可用方法，空串直接返回且异常不进入错误循环；保证业务根挂载与 UI 句柄供初始化/周期刷新使用」。
   - 宿主方法表取证：发行宿主二进制内嵌源路径 `.sources/makepad/platform/script/...` ↔ `runtime/native-build/OctoSense-Shell/runtime-patches.lock.json` pin（rev 4fdcfccc，两 patch 不触碰 platform/script）↔ 本仓库 vendored `runtime/native-build/makepad/platform/script/src/` 逐文件一致。权威方法表（string.rs:65 起 / array.rs:535 起 / object.rs:664 起）：string 有 `len`(字节)/`to_f64`/`to_bytes`/`to_chars`/`parse_json`/`trim`/`strip_prefix`/`strip_suffix`/`split`/`search`/`match_str`/`match_all`/`replace`/`url_*`；**无** `index_of`/`slice`/`to_int`/`starts_with`/`ends_with`/`to_lowercase`；array **无** `join`/`index_of`；map **无** `has`。旧注释「Splash 宿主实测确认 index_of/slice（见 M2 r2 探针）」为虚假声明，已改写。
   - 清零调用点：`index_of`/`slice`/`to_int`/`starts_with`/`ends_with`/`to_lowercase`/`_substringSafe`(未定义)/`join`/`has` 全部替换（静态核验确认一处不剩）。
   - 新增字符语义 helper（只用已注册原语）：`_strSlice`/`_strIndexOf`/`_strArrContains`/`_strHasPrefix`/`_strHasSuffix`/`_strJoin`；`_splitJsonlLines` 改用宿主 `split("\n")`+弹尾空段；`_textLenSafe`=`to_chars().len()`；`_charAtSafe`=to_chars 索引；`_toIntSafe` 严格化（非数字字符→nil 拒绝，不再当 0 累计）。
   - `m5_byte_len` 改用宿主 `len()`（本来就是字节数，语义修正）；`m5_fingerprint`/`m5_basename`/路径守卫/`m5_prefix32/suffix32` 改 to_chars 数组。
   - `m5_detect_mime` 去掉不存在的 `to_lowercase`：精确大小写匹配，大小写归一需宿主原语（当前不提供，注释如实记录）。
   - `meta.has(k)` → `meta[k] != nil`（缺失键读 nil，两分支结果一致）。
   - `tick()` 周期刷新整体 try/catch：单次刷新失败不进入 1Hz 错误循环，不阻断后续 tick；输入恢复仍在首个 tick（视图安装后）执行，恢复路径不清空 STATE.pending_input。
2. **D-M4-03（锁解析失败误清 + 实例互斥）**：审查方改法 = 「用宿主支持的数字转换并对解析失败明确拒绝，不能默认 stale；非过期/未知归属锁不清空；owner 采用独立持有实例 token；锁读取失败不能按无锁继续」。
   - `load()` boot 恢复：进程启动重置 `STATE.m2_lock_token=""`；戳解析改 `_parts[1].to_f64()`（NaN→`>0` 为假）；读失败/格式未知/解析失败 → `unknown_kept` **保留原锁不清空**并写 status；只有解析成功且 `now-ms >= 300000` 才回收。
   - `_acquireTaskLock`：锁读失败 → `read_failed` 显式拒（不再 fail-open）；重入仅当锁内容 == 本进程完整 token（`actor@ms@nonce` 全等），同 actor 另一独立上下文不再放行；未知戳 → `held_by_other_unknown` 拒且不清；获取成功才写 `STATE.m2_lock_token = stamp`。
   - `_releaseTaskLock`：无 token/读失败/内容不全等 → 不动锁（`not_owner`/`read_failed`）；仅全等才清空并清 token。
   - `commitBound`：提交前锁读失败 → `needs_verify` 不写盘；锁非空且不等于本进程 token → `needs_verify` 不写盘（替换原 actor 前缀检查）。
   - 真跨进程原子互斥仍 **HOST_PRIMITIVE_BLOCKED**（宿主 fs 无 O_EXCL/flock/rename 原子），本轮 owner token 化只缩小竞争窗口，不冒充已解阻；如需宿主原语另交最小复现与方案，不擅增服务。
3. **D-M4-04**：上轮 SOURCE-CLOSED；本轮静态回归保留（epoch 集合失效重置、恢复路径只消费 epoch 集合），未再改业务逻辑。

## 桌面 UI/交互变化

无新增 UI 结构变化；本轮是让既有登录/任务/表单界面在真实宿主上首次可渲染（此前业务 eval view=false、客户区空白）。

## 接口 / 数据迁移

无协议/契约变更。`tasks.lock` 内容格式不变（`actor@ms@nonce`）；新增内存字段 `STATE.m2_lock_token`（随 state.json 持久化但进程启动即重置，不作跨进程依据）。

## 已有别人修改的保留与适配

base 为审查方冻结的 M4-r6 源；本轮 diff 仅叠加上述 hunks，未 reset/stash/删除他人改动；M3/M5/M6 区域仅替换不可用方法调用（同类机械替换），业务语义不变。

## 启动步骤 / 隔离数据位置

构建方不启动宿主（Abram 2026-10-11 12:12 裁决）。离线签名 catalog 与安装产物：`runtime/optimization/2026-10-09/M4/native/build_r7/`（私钥已删，删除证据 `offline-store-evidence.json`：working.key/anchor.key exists_after=false，keys 目录空；hub keygen/certify/stamp/sign-manifest/verify/install_probe 七步 rc 全 0）。原生验证请求：`runtime/optimization/2026-10-09/M4/native/REQUEST_build_r7.json`（3 场，新 digest `7ca55c1f…`，anchor `0f70a909…`），待驱动沙箱外执行，证据落 `M4/native-runs/build_r7_*/`。

## 应用运行模型/provider

needs_model=false；本轮模型 0 调用，无 402/欠费。

## 覆盖的既有验收项与证据运行形态

- 静态核验：`runtime/optimization/2026-10-09/M4/r7/scripts/m4_r7_fix_verifier.py` → 26/26（`r7/evidence/fix_verifier.json`）：括号粗平衡、不可用方法清零、helper 只用已注册原语、D-M4-03 六项锁语义、D-M4-03a/b 保持、D-M4-04 回归、tick 异常隔离。
- 原生（待驱动执行 REQUEST_build_r7）：
  - `r7_cold_empty_history_input`：零 parser/零 method-not-found、业务 view=true、登录/任务界面渲染、预存中文原文恢复到 TASK_INPUT/zh_input 且权威盘不清空（B-M4-01 + T14/U07 子项）。
  - `r7_corrupt_authority_manager_hint`：坏盘显式拒绝出口就位、截断 tasks.json 原样保留（D-M4-03b + U07 子项）。
  - `r7_foreign_lock_expired_tech_hint`：他人非过期锁（未来时间戳戳）冷启动后 tasks.lock **原样保留**，host.log 无 to_int 错误（D-M4-03 核心反例）。
- T04/T11 真同盘并发、T35 模型交错：白名单通道缺双上下文同盘同步/受控故障，沿用审查 BLOCKED 判定，本轮不冒充。

## 尚未完成

- 原生结果待驱动执行 REQUEST_build_r7 后回读；本报告不预判。
- HOST_PRIMITIVE_BLOCKED：跨进程原子互斥需宿主 fs 原语。
- type/key/wait 输入通道宿主 unknown（M4_REVIEW_r7 实证）：真实键入 BLOCKED 沿用。
- M3 D-M3-01 等前序挂账不修；M2 BLOCKED 不修。

## 交接

- GATES.json：M4 status → READY_FOR_REVIEW（编码方不自判 PASS）。
- 候选/证据/请求路径见上；完成后停止，等待独立 Review，不进入下一模块。
