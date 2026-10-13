# M5 实施报告 r10

- 模块 / 目标：M5 真实附件完工与独立验收 —— r10 修复轮，唯一修复依据 = M5_REVIEW_r11 缺陷清单（D-M5-04 唯一 OPEN P1 的 B/C 两项；A 已在 r11 闭合），只修清单项及其直接依赖，不发散。
- candidate_id / base_candidate_id：`M5-r10-worktree` / `M5-r9-worktree`
- HEAD / 未提交差异 / 源文件哈希：HEAD=`8d730569546cb57310944bb299695134df773b9d`，工作树 dirty（含 M2/M3/M4/M7 后续轮次与他人改动，全部保留未撤）；`app/bundle/main.splash` 668712 B，SHA-256=`5e8bc1a7224f1d9c5ef3175c6a592ef3d222a8e50d50c444a52fb65f4222b690`；bundle digest=`1c5651b763df91ac70a60adbb51f7ff36f153f84286dda96f368479084420b19`。
- 目标宿主 / 二进制来源与哈希 / 依赖：沿用固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，与 r11 Review 同一宿主）；harness 由驱动在沙箱外执行，构建方未启动宿主。
- 实际模型路由检查结果：本模块 needs_model=false，0 次模型调用；未冒称主会话路由切换。
- 已检查的前置 PASS 报告：无新前置；M4 FAIL 挂账沿用（仅消费既有契约），M2/M3 挂账沿用。
- 本轮修改文件与原因：
  - `app/bundle/main.splash`：仅 D-M5-04 B/C 及直接依赖（见下）。
  - `runtime/optimization/2026-10-09/M5/native/prepare_build_r10.py`：r10 检查/seed/离线签名/请求生成脚本。
  - 其余为报告/清单/GATES/CONTEXT（仅 M5 字段）。
- 桌面 UI/交互变化：无（本轮不修布局/样式/控件命名）。
- 接口 / 数据迁移 / 旧数据恢复方式：索引格式不变（v3 信封 + 旧顶层数组兼容加载）；指纹算法输出与声明算法逐值一致，既有登记 sha 无需迁移；tmp 崩溃恢复副本语义改为「核验整体通过才清空」，loader 回退读 tmp 的行为不变；无任何旧数据被改写或追认。
- 已有别人修改的保留与适配：M2/M3/M4/M6/M7 代码均未触碰；`_hex32`（M3 hashRawText 使用）保持原样未改，指纹改用独立的 `m5_hex32`，避免影响其它模块。
- 启动步骤 / 隔离数据位置：全部原生运行经 harness 请求 `runtime/optimization/2026-10-09/M5/native/REQUEST_build_r10.json`，输出钉扎 `M5/native-runs/build_r10_REQUEST_build_r10/`；构建方未启动 launcher。
- 应用运行模型/provider：无（needs_model=false）。
- 覆盖的既有验收项与证据运行形态：G0-D/T19/T21/T22/T28/U06/U07/U08 的启动恢复子项（本轮原生验证待驱动执行）；真实上传/双入口拒/可信验收链仍 NOT_RUN（通道缺口沿用 r11 Review BLOCKED 子项，不属本轮缺陷清单）。

## 缺陷修复明细（按 M5_REVIEW_r11 编号回写）

**D-M5-04 B（写入成功后的权威核验仍报告失败）**
- 现象（r11 实测）：六场恢复目标索引已写成有效 v3、磁盘 items 与最终 state.attach_items 结构全等、tmp 已清空，audit/state 却 index_saved=false / index_save_failed=true。
- 修法（按清单「先在固定宿主记录分步实际值，用已实证原语修正最小链；失败副本保留到整个核验成功；不把失败旗标硬改为成功」）：
  1. 分步探针：reconcile 读回核验链逐步记录到 `m5-test/m5_save_verify.json`（仅 m5-test 根落盘）——writer 实际返回值、fs.read 是否抛出、parse_json 是否抛出、extractor 是否 nil、两侧长度、逐成员 attach_id / evidence_round / lifecycle 的实际比较结果、首个失配详情（含两侧 to_string 实际值）。
  2. 字段比较：`!=` 跨 parse_json/to_json 往返的严格类型语义未经宿主实证，改用 `m5_index_field_eq` —— 先数值（`a-b` 后 `==0/<0/>0` 关系运算，宿主实证；错误值三判全假或直接抛出则自动回退），再字符串 `to_string` 相等；任一侧无法取值 = 失配（安全失败，不放行、不硬改旗标）。
  3. tmp 生命周期：writer 不再在末尾清 tmp；崩溃恢复副本保留到整个核验通过，由 reconcile 在 rb_ok 后调 `m5_attach_index_tmp_clear()` 清空；核验失败 tmp 持有最近一次完整内容，loader 回退读 tmp 恢复。非 reconcile 路径（open/verify 8+8 处、upload、quarantine、submit、reject 共 20 处调用点）改经 `m5_save_attach_index_commit()`，保持原「字节级读回一致即成功并清 tmp」对外行为。
- 位置：`app/bundle/main.splash` `fn m5_save_attach_index`（:9005）、`fn m5_attach_index_tmp_clear` / `fn m5_save_attach_index_commit` / `fn m5_index_field_eq`（新增）、`fn m5_reconcile_attach_index` 核验段（约 :9455–9560）。

**D-M5-04 C（指纹原生探针全零，完整诊断附件被标 CORRUPTED）**
- 现象（r11 实测）：11 场 `m5_fingerprint("M5 probe ABC xyz 123")` 全输出 `00000000`；声明算法独立参考 `50ce396a`；384 B 完整诊断件字节/canonical 一致却因指纹不符被判 CORRUPTED。
- 根因判断：旧实装依赖 `& 0xFFFFFFFF` / `>>` / `& 255` 与超 i32 字面量（2166136261、0xFFFFFFFF），这些原语在固定宿主上不可靠（具体宿主内部原因未断言；本轮 `band_big_probe` / `shift_probe` 在固定宿主记录旧运算实际行为作对照）。
- 修法（按清单「先分步 probe 确定原语后仅修此直接依赖；保留 canonical 全内容比对；摘要语义不变更不迁移」）：
  1. `m5_xor8`：8 位 XOR 用 `% 2` / `/ 2` 展开，不用位运算。
  2. `m5_fnv_mix_byte`：b<256 只影响低 8 位（高位保留 + 低 8 位 xor8）；乘 16777619 mod 2^32 用 16 位分片（xlo*16777619 + ((xhi*16777619)%65536)*65536）% 2^32，所有中间值 < 2^53 精确整数；大常量拆写 `4000000000 + 294967296`。
  3. `m5_hex32`：`% 16` 取 nibble + `_strSlice` 查表，不用 `& 0xF` / `>> 4`；`_hex32`（M3 使用）保持原样。
  4. `m5_fingerprint`：混入序列与声明算法相同（`i % 256`、printable `c-32`、非 printable `m5_xor8((i*7)%256, 85)`），初始值 `2000000000 + 166136261`。
- 等价性证据（非原生，原生待驱动）：Python 移植与声明 FNV-1a 32 位算法 200000 组随机 (h,b) 逐值一致；探针串→`50ce396a`、r11 384 B 诊断件→`7bedec07`（只读交叉复核）；中文/控制字符语料 fp2==fp。既有登记 sha 语义不变、不迁移、不把现存文件追认为基准；canonical 全字节比对仍是主闸。

**探针扩展**（按 C 清单「分步 probe 核 _hex32(1)/初始值/一次 mix/乘法/掩码/移位和实际 ASCII/中文/控制字符摘要」）：`m5_fs_probe` 新增 `hex32_of_1`（参考 00000001）/ `fnv_offset_probe`（2166136261）/ `mod32_probe`（2166136261）/ `mul_probe`（83886095）/ `xor8_probe`（170）/ `mix_probe`（3289118412）/ `fingerprint_zh`（0a6e9c79）/ `fingerprint_ctrl`（65496f3a），并保留 `band_big_probe` / `shift_probe` 记录旧位运算实际行为。

## 检查结果

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|静态断言 83 项|prepare_build_r10.py 源码级检查（B/C 修复在位 + r8/r9/r7/r6 回归守卫 + bare catch 覆盖 16 函数 + 指纹无位运算/大字面量 + tmp 仅在核验通过后清空）|全过|83/83|PASS|runtime/optimization/2026-10-09/M5/r10/results/r10-fix-checks.json|
|指纹等价|声明算法 vs 无位运算移植：200000 组随机 (h,b) + 语料（1..127 全字节、探针串、中文、控制字符）+ 双参考值（50ce396a / 7bedec07）|逐值一致|全部一致|PASS（移植，非原生）|同上 checks 段|
|reconcile Python 移植仿真|4 场夹具（submit 分裂/reject marker/索引缺项+孤儿/丢 canonical 坏件），sim_save 按新协议（核验通过才清 tmp）|轮次修平+落盘/孤儿保留/READY 字节重建/CORRUPTED 不造基准|4/4 符合|PASS（仿真，非原生）|同上 sim 段|
|结构平衡|字符串/注释感知全文件大括号扫描|深度归零|depth=0、min=0|PASS|本报告运行记录|
|离线签名与安装|沙箱内 keygen/certify/stamp/sign-manifest/verify/install_probe；私钥删除|PREPARED、源码一致、私钥清零|全部成立|PASS|native/build_r10/offline-store-evidence.json、build-validation.json|
|schema/请求校验|REQUEST_build_r10.json 过 validate_schema + 白名单动作检查|PASS|PASS（5 场）|PASS|native/build_r10/build-validation.json|
|真实桌面操作（冷启动零解析+渲染、5 场恢复、m5_save_verify/m5_fs_probe 分步探针值）|harness 驱动沙箱外执行|见 REQUEST note|待驱动执行|NOT_RUN（构建方不启动宿主）|REQUEST_build_r10.json|
|权威状态与回执|同上|—|—|NOT_RUN|—|
|失败与重试|同上|—|—|NOT_RUN|—|
|重启恢复|同上|—|—|NOT_RUN|—|
|受影响先前模块回归|冷启动场景含解析回归守卫|—|待驱动|NOT_RUN|—|

## 尚未完成

- 原生 5 场（cold_fresh 零解析+渲染 / submit 分裂 / reject marker / 索引缺项+孤儿 / 丢 canonical 坏件，含 m5_save_verify.json rb_ok=="true"、fingerprint_probe=="50ce396a" 等探针期望值）：NOT_RUN，等驱动执行 REQUEST_build_r10.json。
- r11 Review 记 BLOCKED 的通道（可信登录/文本表单输入、真实保存后变更、同盘跨进程重开、精确提交点中断）本轮未新增：仍 NOT_RUN/BLOCKED，属驱动/宿主通道缺口，NEEDS_ABRAM=no。
- B 的根因以分步探针实证为准：若 r12 Review 的原生 m5_save_verify.json 显示失败点在 parse/extract 而非字段比较，需按实测值再修（本轮 field-eq 不放宽任何放行条件）。
- 指纹为码点语义；多字节 UTF-8 内容下与逐字节参考值可能不同 —— 主闸为 canonical 全字节比对，不受影响；登记与复验自洽。
- `_ascii_byte_value` / `_nibble_of_byte_low/high` / `_hex32`（M3 在用）保留未删（不删他人/历史代码）。
- M4/M3/M2 前序 FAIL 挂账不改；未进入 M6。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M5/r10/CANDIDATE.json`
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r10.json`（钉扎输出 `M5/native-runs/build_r10_REQUEST_build_r10/`）
- 证据：`runtime/optimization/2026-10-09/M5/r10/results/r10-fix-checks.json`、`native/build_r10/`（offline-store-evidence.json、build-validation.json、fixtures.json、seeds、store、source-traces、affected-functions.json、start-snapshot.json）
- 实际测试命令：`cd runtime/optimization/2026-10-09/M5/native && PYTHONDONTWRITEBYTECODE=1 python3 prepare_build_r10.py`（83/83）
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。
