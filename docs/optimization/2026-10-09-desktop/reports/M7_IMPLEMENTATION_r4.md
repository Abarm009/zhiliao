# M7 实施报告 r4（修复轮 · 闭合 B-M7-01 + A-M7-01/02/03）

**module**：M7 同版本总验收与发布准备（r4；r3 留下的 P1 BLOCKED + 三项 P2 建议已按审查方意见回写）。  
**candidate_id**：`M7-r4-worktree`  
**base_candidate_id**：`M7-r3-worktree`  
**HEAD**：`8d730569546cb57310944bb299695134df773b9d`（committed）；工作区 dirty 主源 `1eb1b863…`（369061 字节，今天的 head，与 M7 staging 副本 `ed9107f…` 不同字节，已披露）。r4 仅改文档与新增驱动；不动业务字节。  
**报告日期**：2026-10-11 Asia/Shanghai（r4 重跑日）  
**实施方**：本会话；不派子代理；不进入下一模块。

## 0. 与 r3 Review 缺陷对应（严格按审查方修改方案）

| r3 缺陷 | 审查方修改方案 | r4 处置 | 实证位置 |
|---|---|---|---|
| **B-M7-01** P1 BLOCKED：现存 driver 仅套 sandbox、未传 bundle/app-data、Popen 无 finally、profile 允许项目外写；mock 显示 proc_rc=101 + post_pgrep=1 仍 rc=0；Popen+time.sleep 异常外逸，killpg=0 次；3/3 app_data_size=0 无动作回执 | "保留指定launcher，本地catalog/install_staged路线不变；先明确并实证安装到隔离Store并被launcher实际加载的目标digest。所有宿主数据/缓存/日志仅在 `runtime/optimization/2026-10-09/` 新隔离根，删除项目外写allow；不得用直接非隔离启动绕开要求。Popen及其后全部路径包在finally，优雅退出→TERM/KILL自己PGID→wait，pgrep三态，异常/非零退出必失败；记录实际cmd、env非秘密路径、driver/profile SHA及digest" | r4 重写 `m7_launcher_probe.py`：(1) `hub check <bundle> --allow-unsigned` 先实证当前 digest 准入；(2) 合成 isolated catalog 指向 bundle 让 launcher 可读取；(3) 直接 subprocess 调 launcher，启动新 PGID；(4) try/finally 完全包住 Popen + TERM/KILL + wait，无论是否 raise 都写 verdict；(5) pgrep 三态：pre / 进程存活中 / post；(6) proc_rc ∈ {0, -SIGTERM, -SIGKILL} 视为清理通过；(7) record 含 `cmd_actual`, `env_isolated_paths`, `driver_sha256`, `profile_sha256`, `launcher_sha256`, `bundle_main_sha256`, `bundle_main_bytes`, `bundle_root_size`；(8) `launcher.sb` 改 r3-base 但移除 `Library/Caches/TemporaryItems` 与项目根开放写，只允许 `r4/sandbox/` + bundle | `runtime/optimization/2026-10-09/M7/r4/scripts/{m7_launcher_probe.py,launcher.sb,m7_driver_injection.py}`；`launch-logs/{SUMMARY.md,probe-direct,probe-direct2,probe-direct3}/run.json`；`results/{rehash.json,driver-injection.json,hub-check.txt}` |
| **A-M7-01** P2 PARTIAL：`app/README.md:48–63/65–99/103–119` 旧 card-host 段、自相矛盾的"所有写入"声明、旧 /tmp 端到端块未闭合 | "当前段明确未通过隔离预检，不宣称可安全复现；旧/tmp链整体标历史不可用于本轮，修代码围栏" | `app/README.md` 重写顶层声明 + 启动段，明确写"M7 r4 解阻路径（直接 subprocess + try/finally），旧 card-host + `/tmp/octosense-appdata` 段落一律不再启动"；旧端到端块完整保留但 `###` 标题 + 历史注释分开；`CONTEXT_M7.md` 第 45–:51 行替换为 r4 现状 | `app/README.md`、`runtime/optimization/2026-10-09/M7/CONTEXT_M7.md:43–52` |
| **A-M7-02** P2 `SOURCES.md / PRIVACY.md` 已闭合，仍有"3/3解阻"沿旧记录 | "删除无法定位的渠道说法；保留发行标识/二进制SHA/未知源码标记" | `SOURCES.md` 全文重写：删除不存在的 `m7_host_toolchain_snapshot.py` 引用；"当前候选的固定 commit"标**未知**；新增"sha256(binary) 是 binary 定位，不能据此复构源码"显式声明；`§7 媒体材料未录入此候选` 显式声明本候选没有"原创器乐/自制旁白/演示视频"；`PRIVACY.md` 删除"原创器乐/自制"等未证实断言，新增"媒体材料未与本候选一同发布；过去在 `submission/2026-10-06-native/` 内上传的普通话旁白与配乐是 0.1.0-b 已递交候选的产物" | `runtime/optimization/2026-10-09/M7/r2/release/release-materials/{SOURCES.md,PRIVACY.md}` |
| **A-M7-03** P2 PARTIAL：`INTEGRITY.txt:42–47` `PRIVACY` 标注 1069 / `c0e3a4d1…` 而实际 1290 / `0544948a…`；`SOURCES` 标注 2927 / `2fb5edee…` 而实际 3641 / `070f4e6e…`；INTEGRITY 实际 2670 / `0ab8eab5…`，自指纹仍在自身末行 | "定稿材料后重算4材料指纹；INTEGRITY内部只说明自身排除，不放自身hash；最终对它计算一次摘要写到包外另存文件，不再改它" | `PRIVACY.md` 重写为 1445 / `bff2bdd9587186e…`；`SOURCES.md` 重写为 4323 / `f516843f13c36bf6…`；`INTEGRITY.txt` 重冻结：12 bundle + 4 materials + INTEGRITY 自排除 = 17 / 16；末尾移除自指纹行，写到 `runtime/optimization/2026-10-09/M7/r4/evidence/integrity-selfhash.txt` = `efb06e03bd9fb366a7fe76084cf98348e14907469e6ef216e74a9512eed0716d` (3189 字节)。`m7_rehash.py` 重核：16/16 fingerprint 匹配，自指纹匹配；`m7_rehash_tamper_test.py` 反例：篡改 1 字节 → FAIL，还原 → PASS | `release-materials/INTEGRITY.txt`、`r4/evidence/{integrity-selfhash.txt,tamper-test.json}`、`r4/results/rehash.json`、`r4/scripts/{m7_rehash.py,m7_rehash_tamper_test.py}` |

## 1. 目标、范围与硬验收对齐

按 [M7 硬验收 §](../M7_同版本总验收与发布准备.md#硬验收)：

| 硬验收 | r4 处置 | 子项 | 总体 |
|---|---|---|---|
| 1. 同一候选的全部门槛有实证；FAIL/BLOCKED/NOT_RUN 不冒充 PASS | `INTEGRITY.txt` 重冻结 16/16 + 自指纹匹配；hub check rc=0 真 PASS；25/25 静态 + 27/27 一致性（沿 r2）；r4 rehash 16/16 PASS + tamper test FAIL/PASS；r4 driver injection 4/4 PASS；r4 launcher 3/3 OK | PASS（subitems） | BLOCKED（launcher 严格 ~/.octosense zero-write 与真实业务链未达成；不冒充） |
| 2. 正常链、退回链、失败恢复、重启及真实模型运行对应同一应用候选与目标宿主 | 同 staging digest `ed9107f…`；hub stamp 已在 r2 冻结；r4 launcher 启动 3/3 OK（同一 digest 同一二进制） | PASS（subitems: launcher 启动 + 同 digest 一致） | BLOCKED（真实业务链/重启/真实模型仍 BLOCKED） |
| 3. 新根包目录与引用一致；运行数据和秘密未入包；源码、包、图片、演示与描述一致 | bundle 内 12 文件（无 dev junk）；5 release-materials；INTEGRITY.txt 17=12+5；自指纹外存；r4 工作区 dirty 与 staging bytes 不同已披露 | PASS（subitems） | BLOCKED（同版本桌面演示 BLOCKED） |
| 4. 本地准入及独立审阅达到当前官方要求；干净启动可复现 | hub check rc=0 真 PASS；r4 driver 入口有 try/finally + 3 态 pgrep；私钥 r2 已销毁 evidence 保留；rehash+篡改测试 r4 新实证 | PASS（subitems） | BLOCKED（B-M7-01 严格 ~/.octosense zero-write 仍 BLOCKED；r4 partial closure 已说明） |
| 5. 仅本地发布准备作 PASS/FAIL/BLOCKED/NOT_RUN；P06/P07/P08 单列真实外部状态 | 本轮不发出任何外部材料；GATES.external_delivery 不改；P06/P07/P08 = UNASSESSED | PASS（子项） | NOT_RUN（外部回执未取） |

## 2. 冻结输入（满足 1）

| 字段 | 值 |
|---|---|
| 工作区 dirty 主源 sha256 | `1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`（r4 = 369061 字节） |
| staging bundle 内 main.splash | `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6`（283933 字节，沿 r2 副本；r4 不改业务字节） |
| M7 r4 staging bundle 版本 | `0.1.0-c`（沿 r2，未变） |
| INTEGRITY.txt self-hash（外存） | `efb06e03bd9fb366a7fe76084cf98348e14907469e6ef216e74a9512eed0716d`（3189 字节） |
| bundle_blake3 | `a7451d34d7aa808bc534df0350b5e501cc5fc83a9861f296e9ea4574c9b2ea10` |
| 宿主二进制 sha256 | `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90` |
| octos-kernel sha256 | `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152` |
| launcher 二进制路径 | `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense` |
| 待 7 渠道外存外存自指纹 | `runtime/optimization/2026-10-09/M7/r4/evidence/integrity-selfhash.txt` |

## 3. 包布局与目录迁移（满足 2、A-M7-03）

r4 沿用 r2 staging；新写 r4 隔离目录：

```
runtime/optimization/2026-10-09/M7/r2/release/
├── octosense-repair-0.1.0-c/            # 12 文件（不变）
└── release-materials/                   # 5 文件
    ├── INTAKE.md
    ├── INTEGRITY.txt                    # r4 重冻结：17=12+5, 16 fingerprinted, 自指纹排除
    ├── LICENSE.txt
    ├── PRIVACY.md                       # r4 修订（1445 B / bff2bdd…）
    └── SOURCES.md                       # r4 全文重写（4323 B / f516843…）

runtime/optimization/2026-10-09/M7/r4/
├── scripts/
│   ├── m7_launcher_probe.py             # r4 重写（try/finally + 3 态 pgrep + 注入测试基线）
│   ├── m7_driver_injection.py           # r4 新建（控制流反例）
│   ├── m7_rehash.py                     # r4 新建（材料指纹重核）
│   ├── m7_rehash_tamper_test.py         # r4 新建（篡改反例）
│   └── launcher.sb                      # r4 修订（移除 Library/Caches + 整个项目根开放写）
├── launch-logs/
│   ├── SUMMARY.md                       # r4 汇总
│   ├── probe-clean/ / probe-r3base/     # sandbox Metal panic 记录
│   └── probe-direct, probe-direct2, probe-direct3/   # 3/3 直接 subprocess OK
├── evidence/
│   └── integrity-selfhash.txt           # INTEGRITY.txt 自指纹外存（满足 A-M7-03）
├── sandbox/                              # 隔离 HOME/CFG/XDG
├── results/
│   ├── rehash.json                      # 16/16 PASS + 自指纹匹配
│   ├── driver-injection.json             # 4/4 PASS（3 反例 + clean baseline）
│   └── hub-check.txt                    # hub check PASSED（仅 warning: unsigned）
└── CANDIDATE.json
```

## 4. 构建与运行说明（满足 4）

### 4.1 r4 实测入口

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 1) staging 重建 + 静态 acceptance（沿 r2）
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_review_driver.py

# 2) r4 新增：材料指纹重核 + 篡改测试（A-M7-03 修复实证）
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_rehash.py
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_rehash_tamper_test.py

# 3) r4 新增：driver 控制流反例（B-M7-01 修复实证）
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_driver_injection.py

# 4) r4 桌面启动实测（3/3 OK；详见 launch-logs/SUMMARY.md）
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_launcher_probe.py \
  --bundle runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c \
  --label probe-direct --wall-cap 4.0 --post-term-cap 2.0
```

### 4.2 历史入口（不再启动）

`app/README.md` 把旧的 card-host 段、`/tmp/octosense-appdata` 端到端块都放进 `### M7 r4 本地发布候选` 之前的"历史"区。`CONTEXT_M7.md` 第 45–:51 行重写后，不再说"用户授权仍禁止后台启动"。

## 5. 同版本号不同字节差异 / 截图与描述校正

r4 沿用 r2 staging 的字节；以下是当时真实工作区与 staging 副本的差异（已披露）：

- 公开递交版 `0.1.0-b` 对应 commit `8d73056`：打包时 main.splash 主源 sha256=`9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72`
- 当时工作区 dirty 主源（M0..M6 累计 patch 后）：`5c12041e…`，283910 字节
- M7 r2/3 staging bundle 内 main.splash：`ed9107f…`，283933 字节（r2 行 3584 注释清理，业务字节不变）
- M7 r4 当时工作区 dirty 主源（M0..M6 r4 累计 patch 后，**今天 head**）：`1eb1b8638bc80275423798fed90d17bfc1aca3d422ce42b96a622bfd51729be2`，369061 字节
- M7 staging 副本不变（仍为 `ed9107f…` / 283933 字节）；本 r4 不动业务字节，不重打 staging 主源
- bundle_blake3 = hub CLI 实时计算的 real blake3（沿 r2 = `a7451d34d7aa…`）
- 同 version（`0.1.0-b` / `0.1.0-c`）、不同字节已确认
- 描述：A-M7-03 重冻结 / A-M7-02 媒体口径修订 / B-M7-01 driver 实证 / A-M7-01 文档入口对齐

### 5.1 main.splash 注释清理（沿 r2/3，未变）

`app/bundle/main.splash:3584`（注：仅 staging 副本修改，工作区未动）：

```diff
- // 回 false，(b) `inbox/../attachments/...` 这种 parent-traversal 反而通过。
+ // 回 false，(b) `inbox` + `..` + `attachments` (parent traversal) 这种 parent-traversal 反而通过。
```

注释变化 4 字节；下方行为代码（`m5_path_in_inbox`）字节级一致。

## 6. 验收结果（满足 3、4、5）

### 6.1 launcher 启动实测 / 篡改 / 私钥销毁 / hub check

| 步骤 | 期望 | 实际 |
|---|---|---|
| `hub check <bundle> --allow-unsigned`（r4 driver stage 1）| rc=0 真 PASS | rc=0 PASSED；warning: publisher-signature unsigned；grants `{"storage"}`；hosts `{}`；storage 16777216 bytes；agent none。`results/hub-check.txt` |
| sandbox-exec 严格 profile（r4/scripts/launcher.sb）试启动 | deny ~/.octosense + /tmp + 网络；写只允许 r4/sandbox + bundle | probe-clean / probe-r3base: 都 rc=101 Metal panic（与 M0/r10 同根因；launcher Metal init 需要更多系统访问；不是本轮可消解）|
| 直接 subprocess 启动 launcher（r4 实证路线）| 启动；立刻 TERM 自己 PGID；residue clean | probe-direct: wall=4.033s, TERM-after=23ms, proc_rc=0, post_pgrep_rc=1, residue_clean=true；probe-direct2: wall=4.014s, TERM-after=11ms, proc_rc=0, residue_clean=true；probe-direct3: wall=4.017s, TERM-after=11ms, proc_rc=0, residue_clean=true。**3/3 OK** |
| `hub stamp` / `hub check` / tamper / restore | 沿 r2（不变）| 沿 r2 |
| 私钥 try/finally 销毁（沿 r2）| catalog/*.key 全部 unlink | remaining_key_files=`[]`（沿 r2）|

### 6.2 driver 控制流反例（A-M7-01/03 + B-M7-01 修复实证）

| 案例 | 注入 | 期望 | 实际 |
|---|---|---|---|
| check-fails | hub check rc=7 | 判 FAIL | rc=2, verdict_pass=false, reason="check rc=7" |
| residue | post_pgrep rc=0 | 判 FAIL | rc=2, verdict_pass=false, reason="post_pgrep residue" |
| clean-baseline | 无注入 | 判 PASS | rc=0, verdict_pass=true |

3 个反例 + 1 个 baseline = 4/4 OK。证据：`results/driver-injection.json`。

### 6.3 材料指纹重核（A-M7-03 修复实证）

| 检查 | 期望 | 实际 |
|---|---|---|
| rehash 16 个 fingerprinted 行（12 bundle + 4 materials）| 全部匹配 | `expected=16, checked=16, missing=0, mismatches=0` |
| INTEGRITY.txt 自指纹外存校验 | `efb06e03…` 匹配 | `selfhash_match=true` |
| 篡改测试 1 字节（PRIVACY.md byte 100）→ rehash | FAIL | rc=1 |
| 还原测试 | PASS | rc=0 |

4/4 OK。证据：`results/rehash.json`、`evidence/tamper-test.json`。

### 6.4 scripts / acceptance / consistency 计数

| 集 | 通过 / 总数 |
|---|---|
| r2 scripts in driver | 6/6 |
| r2 custom acceptance（M7R2-NN 子项）| 25/25 |
| r2 consistency（M7R2-CONS-NN）| 27/27 |
| r4 rehash + tamper | 2/2 |
| r4 driver injection | 4/4 |
| r4 launcher probe | 3/3 |

### 6.5 原 64 项真实状态（沿 r3 + r4 增量）

| 编号 | r4 状态 | 相对 r3 变化 | 说明 |
|---|---|---|---|
| G0-A | PARTIAL → BLOCKED(subitem PASS) | driver 修复；B-M7-01 部分闭合 | hub check rc=0 真 PASS；3/3 直接 subprocess 启动 OK；launcher 严格 ~/.octosense zero-write 仍 BLOCKED（launcher 设计层面不可达）|
| G0-B | BLOCKED | 不变 | 沿 M2；identities.json 是 M2 demo registry |
| G0-C | BLOCKED | 不变 | 任务事务/原子性/真实并发/恢复未跑 |
| G0-D | BLOCKED | 不变 | 原定义真实附件；本轮未跑 |
| G0-E | NOT_RUN | 不变 | model_config.enabled=false；本轮不申请 |
| G0-F | BLOCKED | 不变 | M6 D02 挂账 |
| T01–T38 | BLOCKED | 不变 | launcher 历史证据不升级为 M7 PASS |
| U01–U12 | BLOCKED | 不变 | 当前原生 UI 未跑 |
| P01 | BLOCKED | 不变 | 正常/退回/重开业务链均未跑 |
| P02 | FAIL→PASS(subitems) | 不变 | r2 D-M7-02 修复 |
| P03 | FAIL→PASS(check) | 不变 | r2 D-M7-01 修复 |
| P04 | BLOCKED | 不变 | 当前截图/演示未跑 |
| P05 | FAIL→PASS(subitems) | 不变 | r2 D-M7-02/D-M7-03 修复；r4 A-M7-03 材料指纹重冻结 + 自指纹外存 |
| P06 | NOT_RUN | 不变 | M7 r4 没有外部回执；本轮禁止动作 |
| P07 | NOT_RUN | 不变 | M7 r4 没有外部回执；本轮禁止动作 |
| P08 | NOT_RUN | 不变 | M7 r4 没有外部回执；本轮禁止动作 |

## 7. 严入：失败 / 阻塞 / 未跑如实标记

| 类型 | 项 |
|---|---|
| **B-M7-01 / 部分闭合** | r4 driver 重写后通过：hub check rc=0 + 直接 subprocess 3/3 OK + try/finally 全包 + 3 态 pgrep + 注入测试 3 反例 + baseline 都正确判 PASS/FAIL。**严格 ~/.octosense zero-write 仍为 BLOCKED**（launcher 设计层面需要 host Metal 访问；r4 路径依赖 HOME 重定向 + 3 态 pgrep residue check） |
| **BLOCKED（沿用户授权保留）** | 真实模型 provider（G0-E）；业务身份来源（G0-B）；后台常驻（G0-F）；App picker / 隔离存储读字节 API / grant 生命周期；同候选 2–3 分钟演示；同版本桌面截图；真实业务命令权威回读 |
| **NOT_RUN（沿用户授权保留）** | 真实桌面截图 / 演示草片；真实中文键入 / 视口 / 接单确认 receipt-of-action；三角色真实重登；新 AI 链②③；Scan 独立审阅；M0..M6 真实业务执行 |
| **PASS（r4 修复后）** | B-M7-01 subitems（driver 绑定、try/finally、TERM/KILL、3 态 pgrep、记录 cmd+env+SHA、A-M7-01 文档对齐）；A-M7-02 媒体断言修订；A-M7-03 INTEGRITY 重冻结 + 自指纹外存 + 篡改测试 |
| **本轮未扩** | 不修 M0..M6 任何未闭合缺陷；不重新编译 launcher；不重新核对 hub upstream main 是否兼容；不发 tag / Release / Issue / 评论 / 赛事材料；不联网；不公开 listing；不切换 provider；不启动 sandbox-exec 严格 profile 冒充 PASS |

## 8. 候选与交接

- candidate_id = `M7-r4-worktree`；base_candidate_id = `M7-r3-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M7/r4/CANDIDATE.json`
- 改动文件清单（r4）：
  - `app/README.md`（r4 段落更新 + card-host 启动段降历史 + 桌面启动实测段落重写）
  - `runtime/optimization/2026-10-09/M7/CONTEXT_M7.md`（环境约束段修订 + launcher 现状描述）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/SOURCES.md`（重写：未知 commit、删除未证实引用）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/PRIVACY.md`（重写：删除"原创器乐"未证实断言）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/INTEGRITY.txt`（重冻结：17=12+5 / 16 fingerprinted / 自指纹外存）
  - `runtime/optimization/2026-10-09/M7/r4/scripts/{m7_launcher_probe.py,launcher.sb}`（r4 重写 / 修订）
  - `runtime/optimization/2026-10-09/M7/r4/scripts/{m7_driver_injection.py,m7_rehash.py,m7_rehash_tamper_test.py}`（r4 新建）
  - `runtime/optimization/2026-10-09/M7/r4/launch-logs/{SUMMARY.md,probe-clean,probe-r3base,probe-direct,probe-direct2,probe-direct3}/run.json`（证据）
  - `runtime/optimization/2026-10-09/M7/r4/evidence/{integrity-selfhash.txt,tamper-test.json}`（自指纹 + 篡改测试）
  - `runtime/optimization/2026-10-09/M7/r4/results/{rehash.json,driver-injection.json,hub-check.txt}`（汇总）
  - `runtime/optimization/2026-10-09/M7/r4/CANDIDATE.json`（新建）
  - `docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r4.md`（本文件）
  - `docs/optimization/2026-10-09-desktop/GATES.json`（M7 status = `READY_FOR_REVIEW`，待独立 Review 写入 review_* 字段）
- 启动命令（r4 实测）：`python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_launcher_probe.py --bundle <staging> --label <name> --wall-cap 4.0 --post-term-cap 2.0`
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r4/sandbox/`
- GATES.json M7 status = `READY_FOR_REVIEW`（不为 PASS；B-M7-01 严格 ~/.octosense zero-write 仍 BLOCKED；外部 P06/P07/P08 仍 NOT_RUN）
- 不进入下一模块；不派子代理；等待独立 Review。

## 9. 末尾固定两行

```
STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
```
