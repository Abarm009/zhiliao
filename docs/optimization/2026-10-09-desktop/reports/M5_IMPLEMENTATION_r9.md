# M5 实施报告 r9

- 模块 / 目标：M5 真实附件完工与独立验收 —— r9 修复轮，唯一修复依据 = M5_REVIEW_r10 缺陷清单（D-M5-04 唯一 OPEN P1 的 A/B/C 三项），只修清单项及其直接依赖，不发散。
- candidate_id / base_candidate_id：`M5-r9-worktree` / `M5-r8-worktree`
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树 dirty（含 M2/M3/M4 后续轮次与他人改动，全部保留未撤）；`app/bundle/main.splash` 659343 B，SHA-256=`f0ba6a3f9972527cc35b8d3294fff9123f8601359848b06b29518b1405ce4983`；bundle digest=`d4e702380e758e329fa7c64997732c2ac668f6aa34b140332e7880f075011b5f`。
- 目标宿主 / 二进制来源与哈希 / 依赖：沿用固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，与 r10 Review 同一宿主）；harness 由驱动在沙箱外执行，构建方未启动宿主。
- 实际模型路由检查结果：本模块 needs_model=false，0 次模型调用；未冒称主会话路由切换。
- 已检查的前置 PASS 报告：无新前置；M4 FAIL 挂账沿用（仅消费既有契约），M2/M3 挂账沿用。
- 本轮修改文件与原因：
  - `app/bundle/main.splash`：仅 D-M5-04 A/B/C 及直接依赖（见下）。
  - `runtime/optimization/2026-10-09/M5/native/prepare_build_r9.py`：r9 检查/seed/离线签名/请求生成脚本。
  - 其余为报告/清单/GATES/CONTEXT（仅 M5 字段）。
- 桌面 UI/交互变化：无（本轮不修布局/样式/控件命名）。
- 接口 / 数据迁移 / 旧数据恢复方式：索引格式不变（v3 信封 + 旧顶层数组兼容加载）；指纹算法输出与修复前逐值相同，既有登记 sha 无需迁移；无任何旧数据被改写或追认。
- 已有别人修改的保留与适配：M7 r8 把 tasks 加载重构进 `m7_tasks_strict_parse`（同型码点闭合判定保留在其中）——r9 检查脚本相应改指该函数；M2/M3/M4/M6/M7 代码均未触碰。适配点仅一处：`_strSlice` 中央修复同时修正了日期解析等其它模块调用方此前收到的十进制串（行为从"错误的数字串"变为"正确子串"，无调用方依赖旧错误值）。
- 启动步骤 / 隔离数据位置：全部原生运行经 harness 请求 `runtime/optimization/2026-10-09/M5/native/REQUEST_build_r9.json`，输出钉扎 `M5/native-runs/build_r9_REQUEST_build_r9/`；构建方未启动 launcher。
- 应用运行模型/provider：无（needs_model=false）。
- 覆盖的既有验收项与证据运行形态：G0-D/T19/T21/T22/T28/U06/U07/U08 的启动恢复子项（本轮原生验证待驱动执行）；真实上传/双入口拒/可信验收链仍 NOT_RUN（通道缺口沿用 r10 Review BLOCKED 子项，不属本轮缺陷清单）。

## 缺陷修复明细（按 M5_REVIEW_r10 编号回写）

**D-M5-04 A（路径字符切片把码点拼成十进制）**
- 根因：`_strSlice` 用 `out = out + chars[i]` 拼接 U32 码点 → 十进制串（实测 `"a/b.txt"→"9846116120116"`）。
- 修法（按清单"最小改法"）：裁剪 `to_chars()` 返回的原 U32 数组（`pop`/`remove(0)` 保持 U32 存储），再整体 `to_string()` —— 宿主 array.rs U32 分支 `char::from_u32` 回转字符；宿主自带测试断言 `"hi".to_chars().to_string()=="hi"`。不把码点 `.to_string()` 当字符转换。所有调用方中央修复。
- 位置：`app/bundle/main.splash` `fn _strSlice`（约 :2002）；basename/resolver/重建相对路径随中央修复生效。

**D-M5-04 B（旧顶层数组索引不能完成兼容加载与恢复）**
- 修法（按清单）：`m5_index_items_from_raw` 先判形状再取字段 —— `m7_is_array_value`（合法任务加载同款、宿主实证）命中旧数组直接返回；对象须过 `m7_is_object_value` 且 `items` 为数组才接受；标量/无 items 对象/非数组 items 拒绝；加载失败保全原盘、不改写、不转空数组。catch 全部改用宿主实证的无绑定 bare catch（依据 M7_REVIEW_r7 R-M7-02 实测 + 本工程注释 :1263）；覆盖 loader/save/probe/reconcile/open/verify/attach_from_path/read_content_signature/move_to_quarantine/ensure_inbox_root 共 11 个 M5 函数（56 处）。
- 位置：`fn m5_index_items_from_raw`、`fn m5_load_attach_index` 及 M5 链各函数。

**D-M5-04 C（指纹把 U32 传入字符串方法）**
- 修法（按清单"直接消费实测数值码点"）：`m5_fingerprint` 循环内 `c = chars[i]` 为数值，printable(32..126) 混合 `c-32`（与旧 alpha 表位置逐值相同），其余走原 fallback `((i*7)^85)&255`（旧 nibble 表全是 printable 字符，对非 printable 恒 -1 从未混入，故逐值相同）。已显式注释码点语义（非 UTF-8 字节循环）；canonical 全字节比对仍是主闸；未删除任何指纹/内容闸。等价性由 prepare_build_r9.py 探针语料（含 1..127 全字节、控制字节、高频字节）双向校验通过。
- 位置：`fn m5_fingerprint`（约 :8805）；`_ascii_byte_value`/`_nibble_of_byte_*` 保留但不再被指纹调用。

**探针扩展**：`m5_fs_probe` 新增 `chars_roundtrip` / `fingerprint_probe` / `basename_probe_zh` / `slice_probe_zh`，在固定宿主实证新转换（A/C 验证要求：basename_probe=="b.txt"、slice_probe=="bc"、中文不损坏）。

## 检查结果

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|静态断言 65 项|prepare_build_r9.py 源码级检查（A/B/C 修复在位 + r8/r7/r6 回归守卫 + bare catch 覆盖 11 函数 + 指纹等价）|全过|65/65|PASS|runtime/optimization/2026-10-09/M5/r9/results/r9-fix-checks.json|
|reconcile Python 移植仿真|4 场夹具（submit 分裂/reject marker/索引缺项+孤儿/丢 canonical 坏件）|轮次修平+落盘/孤儿保留/READY 字节重建/CORRUPTED 不造基准|4/4 符合|PASS（仿真，非原生）|同上 sim 段|
|结构平衡|字符串/注释感知全文件大括号扫描|深度归零|depth=0 无未闭合|PASS|本报告运行记录|
|离线签名与安装|沙箱内 keygen/certify/stamp/sign-manifest/verify/install_probe；私钥删除|PREPARED、源码一致、私钥清零|全部成立|PASS|native/build_r9/offline-store-evidence.json、build-validation.json|
|schema/请求校验|REQUEST_build_r9.json 过 validate_schema + 白名单动作检查|PASS|PASS（5 场）|PASS|native/build_r9/build-validation.json|
|真实桌面操作（冷启动零解析错误+工作台渲染、5 场恢复）|harness 驱动沙箱外执行|见 REQUEST note|待驱动执行|NOT_RUN（构建方不启动宿主）|REQUEST_build_r9.json|
|权威状态与回执|同上|—|—|NOT_RUN|—|
|失败与重试|同上|—|—|NOT_RUN|—|
|重启恢复|同上|—|—|NOT_RUN|—|
|受影响先前模块回归|冷启动场景含解析回归守卫|—|待驱动|NOT_RUN|—|

## 尚未完成

- 原生 5 场（cold_fresh 零解析+渲染 / submit 分裂 / reject marker / 索引缺项+孤儿 / 丢 canonical 坏件）：NOT_RUN，等驱动执行 REQUEST_build_r9.json。
- r10 Review 记 BLOCKED 的通道（可信登录/文本表单输入、真实保存后变更、同盘跨进程重开、精确提交点中断）本轮未新增：仍 NOT_RUN/BLOCKED，属驱动/宿主通道缺口，NEEDS_ABRAM=no。
- 指纹为码点语义；多字节 UTF-8 内容下与逐字节参考值可能不同 —— 主闸为 canonical 全字节比对，不受影响；登记与复验自洽。
- `_ascii_byte_value` / `_nibble_of_byte_low/high` 已无调用方，保留未删（不删他人/历史代码）。
- M4/M3/M2 前序 FAIL 挂账不改；未进入 M6。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M5/r9/CANDIDATE.json`
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r9.json`（钉扎输出 `M5/native-runs/build_r9_REQUEST_build_r9/`）
- 证据：`runtime/optimization/2026-10-09/M5/r9/results/r9-fix-checks.json`、`native/build_r9/`（offline-store-evidence.json、build-validation.json、fixtures.json、seeds、store、source-traces、affected-functions.json、start-snapshot.json）
- 实际测试命令：`cd runtime/optimization/2026-10-09/M5/native && PYTHONDONTWRITEBYTECODE=1 python3 prepare_build_r9.py`（65/65）
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。
