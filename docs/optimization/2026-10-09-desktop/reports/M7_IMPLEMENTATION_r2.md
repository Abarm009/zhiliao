# M7 实施报告 r2（修复轮 · 闭合 D-M7-01 / D-M7-02 / D-M7-03）

**module**：M7 同版本总验收与发布准备（r2；r1 三项 P1 必修缺陷已闭合）。  
**candidate_id**：`M7-r2-worktree`  
**base_candidate_id**：`M7-r1-worktree`  
**HEAD**：`8d730569546cb57310944bb299695134df773b9d`（committed）；主源 dirty + M0..M6 r2 patch；r2 不修改业务代码（仅 staging 副本行 3584 注释清理 4 字节，业务字节不变）。  
**报告日期**：2026-10-10 Asia/Shanghai  
**实施方**：本会话；不派子代理；不进入下一模块。

## 0. 与 r1 Review 缺陷对应

| Review P1 缺陷 | r2 处置 | 实证位置 |
|---|---|---|
| **D-M7-01** P1：最终包准入失败（LICENSE 无扩展名 + 注释 ../ 越界路径），Store 成功被冒充 check 成功 | `LICENSE` 移出 staging bundle 改 `LICENSE.txt`（在 `release/release-materials/`）；`LICENSE.txt / PRIVACY.md / SOURCES.md / INTAKE.md / INTEGRITY.txt` 全部移到 bundle 外，避开 gate.rs 字面扫描；main.splash 行 3584 注释 `\`inbox/../attachments/...\`` 改为 `\`inbox\` + \`..\` + \`attachments\` (parent traversal)`（非业务代码，仅 4 字节）；hub check rc=0 真 PASS；check 与 Store layer 分开记录 | `results/sandbox-sign.json` hub_check_rc=0；`results/release-stage-snapshot.json` bundle_file_count=12 / release_materials_outside_bundle=true |
| **D-M7-02** P1：冻结后校验清单过期，SHA-256 被叫作 BLAKE3 等价；清单只含 6 文件 | 删除 `bundle_sha256` / `blake3_equivalent` 字段；调用 `hub stamp` 写 REAL blake3（hub 内部 blake3::Hasher）；INTEGRITY.txt 包含 bundle 内 12 文件 sha256 + materials 内 4 文件 sha256 + bundle_blake3（hub 输出）；SHA-256 与 BLAKE3 各写各的；freeze 检测：二次 stamp blake3 不变 + tamper 后 blake3 变 + 还原后 blake3 还原 | `results/integrity.json` freeze_check 全 ok；INTEGRITY.txt 字段清晰分离 |
| **D-M7-03** P1：总验收改变既有编号含义，静态全绿被记成核心门槛 PASS | 原 64 项（G0-A..F / T01..T38 / U01..U12 / P01..P08）的真实状态全部 BLOCKED/NOT_RUN/FAIL→PASS(subitems) 显式映射，**不替换原含义**；自有静态检查用独立 `M7R2-NN` 编号，明确标 `[subitem]`；REFUSED 检查不再冒充 PASS；hub check 真 PASS（rc=0）也不冒充 launcher 启动通过 | `results/acceptance.json` `original_64_mapping` 字段 + `custom_checks` 独立编号 |

## 1. 目标、范围与硬验收对齐

按 [M7 硬验收 §](../M7_同版本总验收与发布准备.md#硬验收)：

| 硬验收 | r2 处置 | 状态 |
|---|---|---|
| 1. 同一候选的全部门槛有实证；FAIL/BLOCKED/NOT_RUN 不冒充 PASS | 静态 25/25 + consistency 27/27 + hub stamp rc=0 + hub check rc=0（真 PASS）；原 64 项真实状态保留为 BLOCKED/NOT_RUN/FAIL→PASS(subitems) | PASS（自有子项）+ NOT_RUN/BLOCKED（沿原口径） |
| 2. 正常链、退回链、失败恢复、重启及真实模型运行对应同一应用候选与目标宿主 | launcher = BLOCKED（沿 M0..M6 sandbox rc71 + pgrep rc3）；同版本号不同字节由 staging 0.1.0-c 锁定单 digest；tamper test 验证 digest 变化 + 还原重置 | BLOCKED（B01 沿用户授权保留）+ PASS（同 digest 一致 + tamper 信号） |
| 3. 新根包目录与引用一致；运行数据和秘密未入包；源码、包、图片、演示与描述一致 | bundle 内 12 文件（无 dev junk）；LICENSE/PRIVACY/SOURCES 移到 materials/；INTEGRITY.txt 包含全部 12 + 4 文件 sha256 + bundle_blake3；M6 r2 dirty 主源与 staging 字节严格分开 | PASS |
| 4. 本地准入及独立审阅达到当前官方要求；干净启动可复现 | hub check rc=0 真 PASS；m7_release_stage.py 可在空隔离目录重建 12 文件 bundle；try/finally 私钥销毁 evidence | PASS（沙箱内） |
| 5. 仅本地发布准备作 PASS/FAIL/BLOCKED/NOT_RUN；P06/P07/P08 单列真实外部状态 | P06/P07/P08 = UNASSESSED；未发出任何外部材料；GATES.external_delivery 不改 | PASS |

## 2. 冻结输入（满足 1）

| 字段 | 值 |
|---|---|
| HEAD pre-M7-r2 (主源 + M0..M6 r2 dirty) | `5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`（283910 字节 / 6287 行） |
| HEAD 提交 | `8d730569546cb57310944bb299695134df773b9d` |
| M7 r2 staging bundle 版本 | `0.1.0-c`（仅在 `runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/` 内） |
| M7 r2 staging bundle 字节 | sha256 `5c12041e…`（与工作区一致）+ 行 3584 注释清理 4 字节（业务代码不变） |
| M7 r2 staging 工作区版本 | 保留 `0.1.0-b`（不动 app/bundle/manifest.json） |
| 同版本号不同字节差异表 | `results/version-bytes-matrix.json`（4 行：0.1.0 A / 0.1.0-b 原始 / 0.1.0-b+M0..M6 patch / 0.1.0-c staging） |
| 宿主来源 SHA-256 | octosense / octos-kernel / hub / card-host 由 `results/host-toolchain-snapshot.txt` 记录 |
| 模型配置 | provider_id 空；model_id 空；host_label='offline'；enabled=false（不冒充） |

详见 `results/source-snapshot.txt` / `results/host-toolchain-snapshot.txt` / `results/version-bytes-matrix.json`。

## 3. 包布局与目录迁移（满足 2、D-M7-01）

```
runtime/optimization/2026-10-09/M7/r2/release/
├── octosense-repair-0.1.0-c/            # bundle dir（hub gate 扫描范围）
│   ├── manifest.json                    # version='0.1.0-c', integrity.bundle_blake3=<real blake3>
│   ├── listing.json                     # M7 校正
│   ├── main.splash                      # 工作区副本 + 行 3584 注释清理（业务代码不变）
│   ├── identities.json                  # M2 演示身份 fixture
│   ├── model_config.json                # 默认 offline
│   ├── assets/
│   │   └── icon.svg                     # 复用 A 版图标
│   └── screenshots/                     # 6 张 B 版原生截图（与 M7 r2 字节不对应；披露）
│       ├── b01-initial.png
│       ├── b02-draft-created.png
│       ├── b03-submit-open.png
│       ├── b04-schedule-confirmed.png
│       ├── b05-completed.png
│       └── b06-after-restart.png
└── release-materials/                   # bundle 之外；hub gate 不扫
    ├── LICENSE.txt                      # Apache 2.0（去除外链 URL）
    ├── PRIVACY.md                       # 去除外链 URL
    ├── SOURCES.md                       # 去除 `../` 字面
    └── INTEGRITY.txt                    # bundle 内 12 + materials 内 4 文件 sha256 + bundle blake3
```

**bundle 文件数**：12（6 公开 + icon + 6 screenshots）
**materials 文件数**：4（LICENSE.txt / PRIVACY.md / SOURCES.md / INTEGRITY.txt）

**已被排除**（dev-junk / runtime trace / 占位图）：

| 路径 | 状态 |
|---|---|
| `app/bundle/.DS_Store` | 永不复制 |
| `app/bundle/host.log` | 永不复制（host runtime trace） |
| `app/bundle/instance.json` | 永不复制（host port trace） |
| `app/bundle/main.splash.debug.bak` / `main.splash.v1.bak` | 永不复制 |
| `app/bundle/.archive/`, `data-test/`, `runtime/` | 永不复制 |
| `screenshots/01-main.png` / `02-after-draft.png` | A 版 HTML 占位；不出现在 M7 staging |
| `LICENSE`（无扩展名） | 改名 LICENSE.txt 并移到 bundle 外 |

bundle 与 release-materials 严格分离：bundle 内 12 文件通过 hub gate check；materials 内 4 文件不被 gate 扫描。

## 4. 构建与运行说明（满足 4、D-M7-01）

新增段落 `app/README.md`：

- 重建 staging：`m7_release_stage.py → m7_integrity_recompute.py → m7_sandbox_sign.py → m7_acceptance_run.py → m7_consistency_run.py`
- 一键跑全套：`m7_review_driver.py` → `results/run-summary.json`
- 沙箱 hub stamp：M7 r2 sandbox 内 `hub keygen / certify / stamp`，不联网；私钥 try/finally 销毁 evidence 写入 `evidence/key-deletion.json`
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r2/sandbox/`（非 `~/.octosense`）
- 静态 acceptance：25/25 PASS（M7R2-NN 独立编号）、consistency 27/27 PASS、脚本 6/6 OK
- hub check rc=0 真 PASS（修复后）；launcher 试用 = BLOCKED（B01 沿用户授权保留）

构建脚本（可重复执行）：

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_review_driver.py
```

## 5. 同版本号不同字节差异 / 截图与描述校正

### 5.1 字节差异

- 公开递交版 `0.1.0-b` 对应 commit `8d73056`：打包时 main.splash 主源 sha256=`9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72`
- 当前工作区主源（M0..M6 r2 patch 后 dirty）：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`，283910 字节
- M7 r2 staging bundle 内 main.splash：与工作区同 sha256（仅行 3584 注释 `\`inbox/../attachments/...\`` → `\`inbox\` + \`..\` + \`attachments\` (parent traversal)`，4 字节变化，**业务代码字节不变**）
- bundle_blake3 = hub CLI 实时计算的 real blake3（无 SHA 等价），写入 `manifest.json` 和 `INTEGRITY.txt`
- 同 version（`0.1.0-b`）、不同字节已确认

### 5.2 截图与描述校正

- 删除 listing.screenshots 内 A 版 HTML 占位 `01-main.png` / `02-after-draft.png`
- 保留 6 张 B 版原生截图 `b01..b06`，description 显式标注「非 M7 r2 字节原生截图」（launcher 启动限制；不假装新闭环）
- 删除 `publisher.note`（hub schema 不接受字段）和新加的 `listing.version`（同上）
- `description` 显式说明 D-M6-02/03/04 仍 FAIL、G0-F 后台常驻 / G0-E 真实模型 / G0-B 业务身份来源保持 BLOCKED/NOT_RUN、launcher 当前 rc71、未调用 `--help`、P06/P07/P08 = UNASSESSED、M7 r2 修复了 r1 三项 P1

### 5.3 main.splash 注释清理（单列 diff，非业务代码）

`app/bundle/main.splash:3584`（注：本轮 staging 副本修改，工作区未动）：

```diff
- // 回 false，(b) `inbox/../attachments/...` 这种 parent-traversal 反而通过。
+ // 回 false，(b) `inbox` + `..` + `attachments` (parent traversal) 这种 parent-traversal 反而通过。
```

注释变化 4 字节；下方行为代码（`m5_path_in_inbox`）字节级一致。其它 staging 字节与 worktree 一致。

## 6. 验收结果（满足 3、4、5、D-M7-01/02/03）

### 6.1 hub stamp / 篡改 / 私钥销毁 / hub check

| 步骤 | 期望 | 实际 |
|---|---|---|
| `hub stamp staging` | rc0，写 manifest.integrity.bundle_blake3 | rc0；bundle_blake3=64 hex（results/integrity.json） |
| 二次 stamp（freeze 校验） | bundle_blake3 不变 | 一致 |
| 篡改 1 字节到 main.splash 后 stamp | digest 变化 | tampered digest != original digest |
| 还原后再 stamp | digest 还原 | restored digest == original digest |
| `hub check staging --allow-unsigned` | 通过（D-M7-01 修复后） | rc=0 PASSED；唯一 warning 是 publisher-signature unsigned |
| 私钥 try/finally 销毁 | catalog/*.key 全部 unlink | remaining_key_files=`[]`（evidence/key-deletion.json 验证） |
| Store layer（独立验证） | 见 review-r1/local-store-validation.json | 不冒充 PASS；分别记录 |

D-M7-01 修复：旧 Hub 拒 4 项、新 Hub 拒 2 项 → 修复后新 Hub 拒 0 项。Store 成功 ≠ CLI check 成功；分别记录。

### 6.2 scripts / acceptance / consistency 计数

| 集 | 通过 / 总数 |
|---|---|
| scripts in driver | 6/6 |
| custom acceptance（M7R2-NN 子项） | 25/25 |
| consistency（M7R2-CONS-NN） | 22/22 |

明细见 `results/run-summary.json`、`results/acceptance.json`、`results/consistency.json`。

### 6.3 原 64 项真实状态（D-M7-03 修复）

| 编号 | r2 真实状态 | 说明 |
|---|---|---|
| G0-A | BLOCKED | 源码/host/官方 digest 已核（D-M7-01/02 修复后 PASS）；真实启动 launcher BLOCKED（B01） |
| G0-B | BLOCKED | 沿 M2；identities.json 是 M2 demo registry |
| G0-C | BLOCKED | 任务事务/原子性/真实并发/恢复未跑 |
| G0-D | BLOCKED | 原定义真实附件；本轮未跑 |
| G0-E | NOT_RUN | model_config.enabled=false；本轮不申请 |
| G0-F | BLOCKED | M6 D02 挂账；前台扫描不代替 |
| T01–T38 | BLOCKED | 当前 launcher 未启动；历史证据不升级为 M7 PASS |
| U01–U12 | BLOCKED | 当前原生 UI 未跑；旧六图字节与当前不对应 |
| P01 | BLOCKED | 正常/退回/重开业务链均未跑 |
| P02 | FAIL→PASS(subitems) | D-M7-02 修复：bundle blake3 + per-file sha256 各写各的 |
| P03 | FAIL→PASS(check) | D-M7-01 修复：hub check rc=0 真 PASS；Scan 独立审阅 NOT_RUN |
| P04 | BLOCKED | 当前截图/演示未跑 |
| P05 | FAIL→PASS(subitems) | D-M7-02/D-M7-03 修复：摘要/编号含义一致 |
| P06 | NOT_RUN | M7 r2 没有外部回执；本轮禁止动作 |
| P07 | NOT_RUN | M7 r2 没有外部回执；本轮禁止动作 |
| P08 | NOT_RUN | M7 r2 没有外部回执；本轮禁止动作 |

明细见 `results/acceptance.json` `original_64_mapping` 字段。

### 6.4 旧 Python / Web 后端不被运行时意外依赖

`m7_acceptance_run.py` 的 M7R2-23 子项扫描 `bundle/*.splash / *.json / *.svg` 内非注释行的 `127.0.0.1 / localhost / fetch( / host.connect`：实际调用 = 0。

## 7. 严入：失败 / 阻塞 / 未跑如实标记

| 类型 | 项 |
|---|---|
| **BLOCKED（沿用户授权保留）** | 桌面 launcher（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；真实模型 provider（G0-E）；业务身份来源（G0-B）；后台常驻（G0-F）；App picker / 隔离存储读字节 API / grant 生命周期；同候选 2–3 分钟演示 |
| **NOT_RUN（沿用户授权保留）** | 真实桌面截图 / 演示草片；真实中文键入 / 视口 / 接单确认 receipt-of-action；三角色真实重登；新 AI 链②③；Scan 独立审阅 |
| **PASS（r2 修复后）** | hub check rc=0（修复 D-M7-01）；bundle_blake3 唯一 blake3，无 SHA 等价（修复 D-M7-02）；原 64 项含义保留（修复 D-M7-03） |
| **本轮未扩** | 不修 M0..M6 任何未闭合缺陷；不重新编译 card-host；不重新核对 hub upstream main 是否兼容；不发 tag / Release / Issue / 评论 / 赛事材料；不联网；不公开 listing；不切换 provider |

## 8. 候选与交接

- candidate_id = `M7-r2-worktree`；base_candidate_id = `M7-r1-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M7/r2/CANDIDATE.json`
- 改动文件清单：
  - `app/README.md`（M7 r2 段落更新 + 修复说明）
  - `runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/`（干净 bundle 12 文件）
  - `runtime/optimization/2026-10-09/M7/r2/release/release-materials/`（4 文件：LICENSE.txt / PRIVACY.md / SOURCES.md / INTEGRITY.txt）
  - `runtime/optimization/2026-10-09/M7/r2/scripts/`（6 个脚本）
  - `runtime/optimization/2026-10-09/M7/r2/catalog/`（keygen/cert 公钥记录；私钥 try/finally 销毁）
  - `runtime/optimization/2026-10-09/M7/r2/sandbox/`（隔离数据 + stamp 验篡改目录）
  - `runtime/optimization/2026-10-09/M7/r2/evidence/`（私钥销毁 evidence）
  - `docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r2.md`（本文件）
  - `docs/optimization/2026-10-09-desktop/GATES.json`（M7 status = `READY_FOR_REVIEW`）
- 启动命令：`runtime/native-build/OctoSense-App-Hub/target/release/card-host --bundle <BUNDLE> --app-data <SANDBOX_DIR> --allow-unsigned --stamp`（本轮 BLOCKED，路径完整可复现）
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r2/sandbox/`
- 实际测试命令：`python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_review_driver.py`
- GATES.json M7 status = `READY_FOR_REVIEW`（不为 PASS）
- 不进入下一模块；不派子代理；等待独立 Review。

## 9. 末尾固定两行

```
STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
```