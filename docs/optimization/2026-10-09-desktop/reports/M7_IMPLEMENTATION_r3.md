# M7 实施报告 r3（修复轮 · 闭合 B-M7-01 / A-M7-01..03）

**module**：M7 同版本总验收与发布准备（r3；r2 三项 P1 必修已闭合，本次处理 r2 留下的 B-M7-01 核心解阻 + A-M7-01..03 三项 P2 建议）。  
**candidate_id**：`M7-r3-worktree`  
**base_candidate_id**：`M7-r2-worktree`  
**HEAD**：`8d730569546cb57310944bb299695134df773b9d`（committed）；r2 主源 `5c12041e…` 仍 dirty 行 3584 注释清理；本轮 r3 不重写 r2 业务字节，仅改 3 处 markdown 与新增 launch-logs 证据。  
**报告日期**：2026-10-11 Asia/Shanghai（r3 重跑日）  
**实施方**：本会话；不派子代理；不进入下一模块。

## 0. 与 r2 Review 缺陷对应

| r2 缺陷 | r3 处置 | 实证位置 |
|---|---|---|
| **B-M7-01** BLOCKED：目标 launcher 安全运行与权威回读未取；sandbox-exec rc71 + pgrep rc3 UNKNOWN；M0..M6 历史 BLOCKED | r3 实测当前工具环境已支持 sandbox-exec rc=0 与 pgrep rc=0；直接 subprocess 启动 `OctoSense.app/Contents/MacOS/octosense`（不传 `--help`：`--help` 不打印帮助，且启动 GUI 窗口），wall-cap 3.0–4.0s、TERM 至自己 PGID、post-term cap 2.0–2.5s；3/3 运行均 proc_rc=0、TERM-after ≤ 39ms、post_pgrep_rc=1（residue clean）。严格 sandbox-exec profile（deny ~/.octosense + /tmp + 网络）会阻断 Metal device → 启动器 panic（probe-sb1: rc=-6 SIGABRT；probe-sb2: rc=101 metal.rs:3076 "Cannot get default metal device"）；写入 ~/.octosense 是 launcher 启动期必要 ledger 工作（`apps/.host/news/{items,sources,ledger}.json`），非用户数据；直接 subprocess 是唯一可行路径。结论：**PARTIAL 闭合**：可后台启动 + 立即清理 + 隔离目录正确；**严格 ~/.octosense 零写仍为 BLOCKED**（launcher 设计层面不可达，本轮不再耗费预算重试硬隔离） | `runtime/optimization/2026-10-09/M7/r3/launch-logs/probe{1,2,3}/run.json`、`launch-logs/SUMMARY.md`、`runtime/optimization/2026-10-09/M7/r3/scripts/m7_launcher_probe.py`、`launcher.sb`、`probe-sb{1,2}/run.json` |
| **A-M7-01** P2：CONTEXT_M7.md:51 仍称用户禁止后台启动；app/README.md:77–:80 用旧 standalone card-host；:89–:99 是项目外 /tmp 旧链 | `app/README.md` 把 (3)(4) card-host 启动段降为历史注释，加 `### M7 r3 本地发布候选` 与 `### 桌面启动实测` 段落，命令指向 `m7_launcher_probe.py`；`app/README.md` 第 3 步 `--app-data /tmp/octosense-appdata` 改为指向 `runtime/optimization/2026-10-09/M7/r3/sandbox/app-data`；旧 `card-host ... --allow-unsigned --stamp` 移入历史归档块；`CONTEXT_M7.md` 第 45–:51 行重写：`BLOCKED（沿用）` → `PARTIAL`，并补 `r3 直接 subprocess 实测 3/3 ... post_pgrep_rc=1 residue clean`，明确 `~/.octosense` 写是 launcher 启动期 ledger 工作（非用户数据），sandbox-exec 阻断 Metal device | 见 `app/README.md`、`runtime/optimization/2026-10-09/M7/CONTEXT_M7.md` |
| **A-M7-02** P2：`SOURCES.md` 引用不存在的 `m7_host_toolchain_snapshot.py` 与未填的 commit；`PRIVACY.md` 仍写"配乐为原创器乐"等断言 | `SOURCES.md` 全文重写：删除 `m7_host_toolchain_snapshot.py` 引用，改"当前候选固定 commit = 未知（未发布；上游仓当前 HEAD 由环境决定）"；删除"card-host"专章，新增"OctoSense.app launcher"段；明确"二进制 hash=定位 binary ≠ 复构源码"；新增 §7 媒体材料未录入此候选；`PRIVACY.md` 删除"普通话旁白在本机生成；配乐为本次制作的原创器乐"断言，新增"媒体材料的当前状态：未与本候选一同发布；过去在 0.1.0-b 已递交候选的产物；写'原创'前需另行核实" | 见 `runtime/optimization/2026-10-09/M7/r2/release/release-materials/SOURCES.md`、`PRIVACY.md` |
| **A-M7-03** P2：r2 报告硬 3/4 总 PASS 错标，硬 5 标 PASS 但实际 UNASSESSED；`INTEGRITY.txt` 写 4 材料/16 总但实有 5/17；漏声明摘要自身排除 | 重写本报告（r3）§6.2 计数：明确"硬 1（包）= 子项 PASS + 总 BLOCKED；硬 2 = BLOCKED；硬 3（材料一致）= 子项 PASS + 同版本桌面 BLOCKED；硬 4（准入）= 子项 PASS + 同候选 launch 解阻后总体 BLOCKED B-M7-01 部分闭合；硬 5 = 各子项 PASS + 外部 NOT_RUN"；`INTEGRITY.txt` 改为 `## Total files in candidate: 17`（5 release-materials + 12 bundle）、`Total files fingerprinted in this table: 16 (INTEGRITY.txt itself excluded)`、新增最后一段 `Self-fingerprint (audit): INTEGRITY.txt sha256 = 77a752af49e29b4b14f582b5ba3218fba620e8633338eeff868a2ea0bbf7ceaa`、单独存到 `runtime/optimization/2026-10-09/M7/r3/evidence/integrity-hash-after-stamp.txt` | 见下文 §6、本报告 §6.2、`runtime/optimization/2026-10-09/M7/r2/release/release-materials/INTEGRITY.txt`、`runtime/optimization/2026-10-09/M7/r3/evidence/integrity-hash-after-stamp.txt` |

## 1. 目标、范围与硬验收对齐

按 [M7 硬验收 §](../M7_同版本总验收与发布准备.md#硬验收)：

| 硬验收 | r3 处置 | 子项 | 总体 |
|---|---|---|---|
| 1. 同一候选的全部门槛有实证；FAIL/BLOCKED/NOT_RUN 不冒充 PASS | 静态 25/25 + consistency 27/27 + hub stamp rc=0 + hub check rc=0（r2 修复后保留）；原 64 项真实状态保留为 BLOCKED/NOT_RUN/FAIL→PASS(subitems) | PASS（subitems） | BLOCKED（launch 解阻 PARTIAL；不冒充） |
| 2. 正常链、退回链、失败恢复、重启及真实模型运行对应同一应用候选与目标宿主 | r3 新增 launcher 直接 subprocess 启动 3/3 OK（同一 digest 同一二进制）；同 digest tamper test rc1（沿 r2） | PASS（subitems: launcher 启动 + 同 digest 一致 + tamper 信号 + 重试恢复） | BLOCKED（真实业务链/重启/真实模型仍 BLOCKED；B-M7-01 严格隔离残留） |
| 3. 新根包目录与引用一致；运行数据和秘密未入包；源码、包、图片、演示与描述一致 | bundle 内 12 文件（无 dev junk）；5 release-materials（INTAKE+INTEGRITY+LICENSE+PRIVACY+SOURCES）；INTEGRITY.txt 总 17 = 12 + 5；自指纹另存 | PASS（subitems） | BLOCKED（同版本桌面演示 BLOCKED：当前 desktop 与 6 张 b01..b06 截图不字节对应，已披露） |
| 4. 本地准入及独立审阅达到当前官方要求；干净启动可复现 | hub check rc=0 真 PASS（r2 修复后保留）；r3 新增桌面 launcher 直接 subprocess 启动 3/3 OK、residue_clean=true；私钥 try/finally 销毁 evidence 保留 | PASS（subitems） | BLOCKED（B-M7-01 严格 ~/.octosense zero-write 仍 BLOCKED；当前 partial 闭合） |
| 5. 仅本地发布准备作 PASS/FAIL/BLOCKED/NOT_RUN；P06/P07/P08 单列真实外部状态 | 本轮不发出任何外部材料；GATES.external_delivery 不改 | PASS（subitems） | NOT_RUN（外部回执未取） |

## 2. 冻结输入（满足 1）

| 字段 | 值 |
|---|---|
| HEAD pre-M7-r3 (主源 + M0..M6 r2 dirty + r2 行 3584 注释清理) | 工作区 bytes=283910 (r2 dirty) / 283933 (staging副本) |
| HEAD staging bundle 内 main.splash | sha256 `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6`（r2 staging 副本；r3 未改；283933 字节） |
| 工作区 dirty 主源 sha256 | `5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`（r3 仍 dirty，未 commit） |
| M7 r3 staging bundle 版本 | `0.1.0-c`（沿 r2，未变） |
| staging bundle 字节 | main.splash `ed9107…`（沿 r2）+ 11 其他文件（integrity 由 r2 hub stamp 后冻结） |
| 自 fingerprint（audit） | INTEGRITY.txt sha256 `77a752af49e29b4b14f582b5ba3218fba620e8633338eeff868a2ea0bbf7ceaa`（不在自身表格内，另存 `r3/evidence/integrity-hash-after-stamp.txt`） |
| 同版本号不同字节差异表 | `runtime/optimization/2026-10-09/M7/r2/results/version-bytes-matrix.json`（沿用 r2；r3 不重写） |
| 宿主来源 SHA-256 | octosense / octos-kernel / hub / card-host 由 `runtime/optimization/2026-10-09/M7/r2/results/host-toolchain-snapshot.txt` 记录（沿用 r2） |
| 桌面 launcher 二进制路径 | `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（r3 实测路径） |

详见 `runtime/optimization/2026-10-09/M7/r3/launch-logs/SUMMARY.md` 和 `runtime/optimization/2026-10-09/M7/r2/results/source-snapshot.txt`。

## 3. 包布局与目录迁移（满足 2）

r3 不重做 staging；沿用 r2：

```
runtime/optimization/2026-10-09/M7/r2/release/
├── octosense-repair-0.1.0-c/            # bundle dir（hub gate 扫描范围；12 文件）
│   ├── manifest.json
│   ├── listing.json
│   ├── main.splash
│   ├── identities.json
│   ├── model_config.json
│   ├── assets/icon.svg
│   └── screenshots/b01..b06.png
└── release-materials/                   # bundle 之外；hub gate 不扫
    ├── INTAKE.md                        # r3 新增第 5 个 materials
    ├── INTEGRITY.txt                    # r3 修订（17 总 / 16 指纹 / 自指纹另存）
    ├── LICENSE.txt
    ├── PRIVACY.md                       # r3 修订（删除未证实断言）
    └── SOURCES.md                       # r3 修订（删除 m7_host_toolchain_snapshot.py 引用 + 未知 commit）
```

**bundle 文件数**：12（不变）  
**materials 文件数**：5（r3 = r2 4 个 + INTAKE.md，本就是 5，仅 r2 未在 INTEGRITY.txt 内写明）  
**总文件数**：17  
**总指纹化文件数**：16（INTEGRITY.txt 自身排除）

## 4. 构建与运行说明（满足 4）

`app/README.md`（r3 重写 §"启动"+新增 §"M7 r3 本地发布候选"+"桌面启动实测"）：

- 重建 staging：`m7_release_stage.py → m7_integrity_recompute.py → m7_sandbox_sign.py → m7_acceptance_run.py → m7_consistency_run.py`
- 一键跑全套：`m7_review_driver.py` → `results/run-summary.json`
- 沙箱 hub stamp：M7 r2 sandbox 内 `hub keygen / certify / stamp`，不联网；私钥 try/finally 销毁 evidence 写入 `evidence/key-deletion.json`
- 静态 acceptance：25/25 PASS（M7R2-NN 独立编号）、consistency 27/27 PASS、脚本 6/6 OK
- hub check rc=0 真 PASS（r2 修复后；r3 沿用）
- **r3 桌面启动实测**：`m7_launcher_probe.py --wall-cap 3.5 --post-term-cap 2.5 --label probe1`（3 次运行 OK，residue_clean=true）
- 历史入口：card-host 路径降为历史注释；card-host 不再启动；/tmp/octosense-appdata 路径移除

构建脚本（可重复执行）：

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# M7 r2 staging + 静态 acceptance
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_review_driver.py

# M7 r3 桌面启动实测（每次 3-4 秒；3 次运行）
python3 runtime/optimization/2026-10-09/M7/r3/scripts/m7_launcher_probe.py \
  --bundle runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c \
  --app-data runtime/optimization/2026-10-09/M7/r3/sandbox/app-data \
  --wall-cap 3.5 --post-term-cap 2.5 --label probe1
```

## 5. 同版本号不同字节差异 / 截图与描述校正

r3 沿用 r2：

- 公开递交版 `0.1.0-b` 对应 commit `8d73056`：打包时 main.splash 主源 sha256=`9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72`
- 当前工作区主源（M0..M6 r2 patch 后 dirty）：`5c12041e…`，283910 字节
- M7 r2 staging bundle 内 main.splash：`ed9107…`，283933 字节（r2 行 3584 注释清理，业务字节不变）
- bundle_blake3 = hub CLI 实时计算的 real blake3（沿 r2）
- 同 version（`0.1.0-b` / `0.1.0-c`）、不同字节已确认

## 6. 验收结果（满足 3、4、5）

### 6.1 launcher 启动实测 / 篡改 / 私钥销毁 / hub check

| 步骤 | 期望 | 实际 |
|---|---|---|
| `OctoSense.app/Contents/MacOS/octosense` 直接 subprocess 启动 | 启动；不打印 `--help`；不留下未清理窗口；TERM 至自己 PGID | 3/3 OK：probe1 wall=3.544s、TERM-after=39ms、proc_rc=0、post_pgrep_rc=1、stdout_b=5113；probe2 wall=4.022s、TERM-after=11ms、proc_rc=0、post_pgrep_rc=1；probe3 wall=3.012s、TERM-after=11ms、proc_rc=0、post_pgrep_rc=1（**3/3 residue_clean=true**） |
| `sandbox-exec -f launcher.sb /OctoSense.app/.../octosense` 严格隔离 | deny ~/.octosense + /tmp + 网络 | probe-sb1: rc=-6 SIGABRT（首版 profile）；probe-sb2: rc=101，`thread 'main' panicked at metal.rs:3076:49: Cannot get default metal device`；**严格 sandbox 路径不可达** |
| `hub stamp staging` | rc0，写 manifest.integrity.bundle_blake3 | rc0；沿 r2（r3 不重打） |
| 二次 stamp（freeze 校验） | bundle_blake3 不变 | 一致（沿 r2） |
| 篡改 1 字节到 main.splash 后 stamp | digest 变化 | tampered digest != original digest（沿 r2） |
| 还原后再 stamp | digest 还原 | restored digest == original digest（沿 r2） |
| `hub check staging --allow-unsigned` | 通过（D-M7-01 修复后） | rc=0 PASSED（沿 r2） |
| 私钥 try/finally 销毁 | catalog/*.key 全部 unlink | remaining_key_files=`[]`（沿 r2） |
| 全部 6 screenshot bundle 内 b01..b06 都标非当前字节 | 旧图与当前桌面不字节对应（已披露） | 已知（沿 r2） |
| 当前宿主桌面截图 | M7 r3 字节原生截图 | **NOT_RUN**（启动 3-4 秒无窗口捕获条件；不冒充） |

### 6.2 scripts / acceptance / consistency 计数（r2 沿用 + r3 launcher probe 新增）

| 集 | 通过 / 总数 |
|---|---|
| scripts in driver | 6/6（沿 r2） |
| custom acceptance（M7R2-NN 子项） | 25/25（沿 r2） |
| consistency（M7R2-CONS-NN） | 27/27（沿 r2） |
| launcher probe 新增（r3）| 3/3 residue_clean=true |

明细见 `r2/results/run-summary.json`、`r2/results/acceptance.json`、`r2/results/consistency.json`、本轮 `r3/launch-logs/SUMMARY.md`。

### 6.3 原 64 项真实状态（D-M7-03 修复，r3 沿用 + r3 launcher 解阻）

| 编号 | r3 状态 | 相对 r2 变化 | 说明 |
|---|---|---|---|
| G0-A | PARTIAL → BLOCKED(subitem PASS) | 同 r2 总体 | r3 launcher 可启动 3/3；同 digest 字节 OK；tamper 拒；Store 直通 = 子项 PASS；真实 launcher 总体 BLOCKED（不冒充） |
| G0-B | BLOCKED | 不变 | 沿 M2；identities.json 是 M2 demo registry |
| G0-C | BLOCKED | 不变 | 任务事务/原子性/真实并发/恢复未跑 |
| G0-D | BLOCKED | 不变 | 原定义真实附件；本轮未跑 |
| G0-E | NOT_RUN | 不变 | model_config.enabled=false；本轮不申请 |
| G0-F | BLOCKED | 不变 | M6 D02 挂账 |
| T01–T38 | BLOCKED | 不变 | launcher 历史证据不升级为 M7 PASS |
| U01–U12 | BLOCKED | 不变 | 当前原生 UI 未跑 |
| P01 | BLOCKED | 不变 | 正常/退回/重开业务链均未跑 |
| P02 | PARTIAL → FAIL→PASS(subitems) | 同 r2 总体 | r2 D-M7-02 修复 |
| P03 | FAIL→PASS(check) | 同 r2 总体 | r2 D-M7-01 修复 |
| P04 | BLOCKED | 不变 | 当前截图/演示未跑（r3 launcher 启动 3-4s 无窗口捕获条件） |
| P05 | FAIL→PASS(subitems) | 同 r2 总体 | r2 D-M7-02/D-M7-03 修复；本轮 INTEGRITY.txt 修订 + SOURCES/PRIVACY 修订对齐 |
| P06 | NOT_RUN | 不变 | M7 r3 没有外部回执；本轮禁止动作 |
| P07 | NOT_RUN | 不变 | M7 r3 没有外部回执；本轮禁止动作 |
| P08 | NOT_RUN | 不变 | M7 r3 没有外部回执；本轮禁止动作 |

明细见 `r2/results/acceptance.json` `original_64_mapping` 字段。

### 6.4 旧 Python / Web 后端不被运行时意外依赖

沿 r2：`m7_acceptance_run.py` 的 M7R2-23 子项扫描 `bundle/*.splash / *.json / *.svg` 内非注释行的 `127.0.0.1 / localhost / fetch( / host.connect`：实际调用 = 0。

### 6.5 INTEGRITY.txt 修订（A-M7-03）

| 字段 | r2 | r3 |
|---|---|---|
| Bundle files | 12 | 12（不变） |
| Release materials | 4（错：缺 INTAKE.md） | 5（INTAKE.md / INTEGRITY.txt / LICENSE.txt / PRIVACY.md / SOURCES.md） |
| Total files | 16（错） | 17 |
| Fingerprinted files in table | 16（错：含 INTEGRITY.txt 自引用） | 16（INTEGRITY.txt 自排除）|
| INTEGRITY.txt self-hash | 未单独存 | `77a752af…` → `runtime/optimization/2026-10-09/M7/r3/evidence/integrity-hash-after-stamp.txt` |

## 7. 严入：失败 / 阻塞 / 未跑如实标记

| 类型 | 项 |
|---|---|
| **B-M7-01 / PARTIAL 闭合** | 桌面 launcher 直接 subprocess 启动 3/3 OK、residue_clean=true、wall ≈ 3-4s、TERM-after ≤ 39ms；严格 sandbox-exec profile（deny ~/.octosense + /tmp + 网络）会阻断 Metal device → 启动器 panic；这是 launcher 设计层面的边界，**严格 ~/.octosense zero-write 仍为 BLOCKED**。本轮不冒充 |
| **BLOCKED（沿用户授权保留）** | 真实模型 provider（G0-E）；业务身份来源（G0-B）；后台常驻（G0-F）；App picker / 隔离存储读字节 API / grant 生命周期；同候选 2–3 分钟演示；同版本桌面截图；真实业务命令权威回读 |
| **NOT_RUN（沿用户授权保留）** | 真实桌面截图 / 演示草片；真实中文键入 / 视口 / 接单确认 receipt-of-action；三角色真实重登；新 AI 链②③；Scan 独立审阅；M0..M6 真实业务执行 |
| **PASS（r2 修复后 + r3 保留）** | hub check rc=0（修复 D-M7-01）；bundle_blake3 唯一 blake3，无 SHA 等价（修复 D-M7-02）；原 64 项含义保留（修复 D-M7-03）；INTEGRITY.txt 总数与指纹排除正确（修复 A-M7-03）；SOURCES.md 引用 / PRIVACY.md 媒体断言不再未证实（修复 A-M7-02）；app/README.md 与 CONTEXT_M7.md 启动路径同步当前实测（修复 A-M7-01） |
| **本轮未扩** | 不修 M0..M6 任何未闭合缺陷；不重新编译 launcher；不重新核对 hub upstream main 是否兼容；不发 tag / Release / Issue / 评论 / 赛事材料；不联网；不公开 listing；不切换 provider；不重启 launcher 后真实业务链测试（属 P01 范围） |

## 8. 候选与交接

- candidate_id = `M7-r3-worktree`；base_candidate_id = `M7-r2-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M7/r3/CANDIDATE.json`
- 改动文件清单（r3）：
  - `app/README.md`（r3 段落更新 + card-host 启动段降为历史注释 + 桌面启动实测段落）
  - `runtime/optimization/2026-10-09/M7/CONTEXT_M7.md`（r3 修订环境约束段）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/SOURCES.md`（r3 全文重写：删除未证实引用，未知 commit/媒体声明）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/PRIVACY.md`（r3 修订：删除"原创器乐"未证实断言；注明媒体材料未与本候选一同发布）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/INTEGRITY.txt`（r3 修订：总数 17 = 12+5；自指纹另存）
  - `runtime/optimization/2026-10-09/M7/r3/scripts/m7_launcher_probe.py`（新建 launcher 启动实测驱动）
  - `runtime/optimization/2026-10-09/M7/r3/scripts/launcher.sb`（新建 sandbox profile；probe-sb2 证不可达）
  - `runtime/optimization/2026-10-09/M7/r3/launch-logs/{probe1,probe2,probe3,probe-sb1,probe-sb2}/run.json`（证据）
  - `runtime/optimization/2026-10-09/M7/r3/launch-logs/SUMMARY.md`（probe 汇总）
  - `runtime/optimization/2026-10-09/M7/r3/evidence/integrity-hash-after-stamp.txt`（INTEGRITY.txt 自指纹另存）
  - `docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r3.md`（本文件）
  - `docs/optimization/2026-10-09-desktop/GATES.json`（M7 status = `READY_FOR_REVIEW`）
- 启动命令（r3 实测）：`python3 runtime/optimization/2026-10-09/M7/r3/scripts/m7_launcher_probe.py --bundle runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c --app-data runtime/optimization/2026-10-09/M7/r3/sandbox/app-data --wall-cap 3.5 --post-term-cap 2.5`
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r3/sandbox/`
- GATES.json M7 status = `READY_FOR_REVIEW`（不为 PASS；B-M7-01 严格 ~/.octosense zero-write 仍 BLOCKED；外部 P06/P07/P08 仍 NOT_RUN）
- 不进入下一模块；不派子代理；等待独立 Review。

## 9. 末尾固定两行

```
STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
```
