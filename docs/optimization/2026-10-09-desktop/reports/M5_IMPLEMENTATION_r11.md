# M5 实施报告 r11

- 模块 / 目标：M5 真实附件完工与独立验收 —— 修复轮，唯一依据 `reports/M5_REVIEW_r13.md` 缺陷清单（B-M5-01、D-M5-04 B/C，仅有的 OPEN P1）；只修清单项，不发散。
- candidate_id / base_candidate_id：`M5-r11-worktree` / `M5-r10-worktree`
- HEAD / 未提交差异 / 源文件哈希清单：HEAD `8d730569546cb57310944bb299695134df773b9d` + 工作树既有未提交改动（M2/M3/M4/M6/M7 后续轮次与他人改动，全部保留，未撤未改）。候选冻结源 `app/bundle/main.splash` = **771176 B，SHA-256 `05c9ea2484eb3c2ee1dc5a97dde37e1f489501a42385dfd81b5803914dfe6365`**（本轮 21:37 工作树快照；冻结副本 `M5/native/build_r11/main.splash.snapshot`，逐字节一致）。bundle digest `5bde47daba3ff19a98a9b0e079bbd9cd06eb16ae0d4b133dc45206395ab63544`，版本 0.1.0-b。
- 目标宿主 / 二进制来源与哈希 / 依赖：host-rc6 `runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA-256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`（Abram 16:45 批准的 harness 默认宿主）；harness `driver/harness/native_harness.py` 与 `request.schema.json` 已纳入 watched 快照（`build_r11/start-snapshot.json`），准备全程未变。
- 实际模型路由检查结果（开发会话）：本模块 needs_model=false，模型调用 0 次；未读取 `runtime/secrets` 与任何明文凭据。
- 已检查的前置 PASS 报告：无新增（M4 仍 FAIL 挂账，按既有裁决继续局部修复，不修 M4、不冒称前置满足）。
- 本轮修改文件与原因：**业务代码 0 改动**。B-M5-01 的代码修复（两处探针表达式：`(2166136261 & 0xFFFFFFFF).to_string()` / `(32 >> 4).to_string()` → 宿主已实证同构形 `_bbn = (_bbn ^ 0) & 0xFFFFFFFF` / `_shn = _shn >> 4`，见 main.splash:11200-11210 及注释）已由 M6 在共享工作树完成（M6_IMPLEMENTATION_r9:11-18）；r13 清单对本项的改法要求是「把该最小修复纳入明确的新 M5 候选交接：列差异、完整资源摘要、匹配签名安装包、零解析冷启动证据」，本轮即执行该交接动作。D-M5-04 B/C 的修复代码（r10 轮：m5_save_verify.json 分步探针、m5_index_field_eq、tmp 延迟清理；m5_xor8/m5_fnv_mix_byte/m5_hex32 指纹重算）在当前源中完整保留（静态断言 85/85 覆盖），其缺口是「从未原生实际运行」，本轮用同组场景在新候选上请求实际运行。
- 桌面 UI/交互变化：无（布局/样式/控件一律未动）。
- 接口 / 数据迁移 / 旧数据恢复方式：无变化；v3 信封与旧顶层数组兼容路径、tmp 崩溃副本回退、canonical 全字节主闸全部沿用。
- 已有别人修改的保留与适配：M6 的 `_strIndexOf` 改为宿主原生 split 实现（无保留字标识符，B-M5-01 语义保持），本轮仅适配静态检查到新形态，未改其代码；M2 hf_* 底层、M6/M7 各轮改动原样保留。
- 启动步骤 / 隔离数据位置：构建方不启动宿主。原生运行由驱动在沙箱外执行 `M5/native/REQUEST_build_r11.json`（5 场：cold_fresh、submit_split_round、reject_marker_split、rebuild_intact_orphan、rebuild_no_canonical_corrupt），输出钉扎 `M5/native-runs/build_r11_REQUEST_build_r11/`；每场 fresh Store 含 apps/catalog.json 与同源预装包。
- 应用运行模型/provider（适用时；无秘密）：不涉及，needs_model=false。
- 覆盖的既有验收项与证据运行形态：本轮只覆盖 B-M5-01（冷启动零解析+渲染）与 D-M5-04 B/C（恢复/核验/指纹实际值）；G0-D/T18-T22/T28/T31/T35/U03/U06/U07/U08/U11 的可信输入链、双入口负例、同 Store 重开仍 NOT_RUN/BLOCKED（通道缺口沿用 r13 Review 裁决，需驱动补，不需 Abram 新授权）。

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|候选与签名包同源|冻结源 vs 安装包 main.splash 逐字节|一致|一致（sha 05c9ea24 双侧相同）|PASS|M5/native/build_r11/offline-store-evidence.json、build-validation.json|
|离线签名验装|hub keygen/certify/stamp/sign-manifest/verify + install_probe|rc0|全 rc0；私钥 2 把已删且复核不存在|PASS（沙箱内，授权A）|同上（private_keys_deleted / remaining_key_files=[]）|
|静态回归（含 r7-r10 全部修复层 + B-M5-01 新形态）|85 项源码断言|全过|85/85|PASS|M5/r11/results/r11-fix-checks.json|
|解析风险形态|全源码剥注释扫 `(`…`&`/`>>`…`)`.方法|0 处|0 处（仅注释中残留引用，不参与解析）|PASS|同上（B-M5-01(r13) 两项）|
|reconcile 移植仿真|4 场夹具副本跑 Python 移植|submit/reject 轮次修复持久化、孤儿保留、丢 canonical 保持 CORRUPTED 不造基准|4/4 符合|PASS（仿真，不替代原生）|同上 sim 段|
|指纹算法等价|200k 随机 (h,b) + 探针串 + r11 384B 诊断件|与声明 FNV-1a 32 位逐值一致；50ce396a / 7bedec07|一致|PASS（独立 oracle）|同上|
|冷启动零解析 + 工作台渲染（本候选）|驱动执行 REQUEST_build_r11 后核 host.log [E]=0 与截图|0 解析错误、登录/工作台可见|**NOT_RUN（等驱动执行）**|待核|M5/native-runs/build_r11_REQUEST_build_r11/（执行后填）|
|D-M5-04 B 实际值（save_verify/audit/tmp）|5 场原生恢复|rb_ok=true、index_saved=true、tmp 核验后清空|**NOT_RUN（等驱动执行）**|待核|同上各场 m5-test/|
|D-M5-04 C 实际值（指纹探针/好坏件分类）|cold_fresh 探针 + 坏件场|50ce396a 等参考值；完整件 READY、坏件 CORRUPTED|**NOT_RUN（等驱动执行）**|待核|同上|
|可信主体正常/退回/重启链、上传后双入口负例|真实输入/重开/精确中断通道|—|NOT_RUN；通道 BLOCKED（驱动补）|BLOCKED|r13 Review「仅以下白名单…记BLOCKED」|

## 尚未完成
- 原生 5 场尚未执行（构建方不得自启宿主；REQUEST 已交付驱动）。B-M5-01 与 D-M5-04 B/C 的关闭须由独立 Review 依据该运行证据裁决，本报告不预判结果。
- 可信文本输入、保存后运行中变更、同 Store 跨进程重开、精确提交点中断：通道 BLOCKED 沿用（驱动补通道，不需 Abram 新授权）。
- M2/M3/M4/M6/M7 各自挂账缺陷不修、不扩。

## 交接
- 候选清单：`runtime/optimization/2026-10-09/M5/r11/CANDIDATE.json`（schema=3）。
- 原生请求：`runtime/optimization/2026-10-09/M5/native/REQUEST_build_r11.json`；期望实际值与判定标准见请求 note。
- 准备与证据：`M5/native/build_r11/`（start-snapshot / main.splash.snapshot / affected-functions / fixtures / offline-store-evidence / build-validation / seeds / store）。
- 静态+仿真结果：`M5/r11/results/r11-fix-checks.json`（85/85 + 4/4）。
- 准备脚本：`M5/native/prepare_build_r11.py`（可复跑，幂等）。
- 审查注意：r13 审的 M5-r10 冻结包（digest 1c5651b7）已作废；请只审本候选（digest 5bde47da）；审查 seed 须带 apps/catalog.json（本候选 seeds 均已带）。
- 编码方最多标 READY_FOR_REVIEW；最终 PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
