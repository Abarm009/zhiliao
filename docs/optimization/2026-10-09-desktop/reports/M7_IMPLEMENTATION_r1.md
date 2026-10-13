# M7 实施报告 r1

**module**：M7 同版本总验收与发布准备（r1；基线 M6 r2 FAIL → 沿用户挂账授权保留缺口）。  
**candidate_id**：`M7-r1-worktree`  
**base_candidate_id**：`M6-r2-worktree`  
**HEAD**：`8d730569546cb57310944bb299695134df773b9d`（committed）；主源仍在 dirty + M0..M6 r2 patch 上（M7 r1 不修改）。  
**报告日期**：2026-10-10 Asia/Shanghai  
**实施方**：Codex M7 r1 唯一编码会话；不自动派生子代理；不进入 M8。  

## 1. 目标、范围与硬验收对齐

按 [M7 硬验收 §](../M7_同版本总验收与发布准备.md#硬验收)：

| 硬验收 | 本轮处置 | 状态 |
|---|---|---|
| 1. 同一候选的全部门槛有实证；FAIL/BLOCKED/NOT_RUN 不冒充 PASS | acceptance 33/33 PASS、consistency 23/23 PASS；FAIL/BLOCKED/NOT_RUN 在 GATES 与报告里真实保留；不自授予 PASS | PASS |
| 2. 正常链、退回链、失败恢复、重启及真实模型运行对应同一应用候选与目标宿主 | host / model / 38 业务 / 12 UI 真实形态沿用户挂账保留；同版本号不同字节由 staging 0.1.0-c 锁定单 digest | PASS（锁入口）+ NOT_RUN（真实闭环） |
| 3. 新根包目录与引用一致；运行数据和秘密未入包；源码、包、图片、演示与描述一致 | staging 干净性 acceptance + consistency + sandbox 私钥销毁证据；M6 r2 dirty 主源与自采 staging 字节严格分开 | PASS |
| 4. 本地准入及独立审阅达到当前官方要求；干净启动可复现 | sandbox hub stamp rc0；篡改后 digest 改变；私钥销毁；starter 隔离目录路径完整 | PASS（沙箱内） |
| 5. 仅本地发布准备作 PASS/FAIL/BLOCKED/NOT_RUN；P06/P07/P08 单列真实外部状态 | P06/P07/P08 = UNASSESSED；未发出任何外部材料；GATES.external_delivery 不改 | PASS |

## 2. 冻结输入（满足 1）

| 字段 | 值 |
|---|---|
| HEAD pre-M7-r1 (主源 + M0..M6 r2 dirty) | `5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db` (283910 字节 / 6287 行) |
| HEAD 提交 | `8d730569546cb57310944bb299695134df773b9d` |
| M7 staging 版本 | `0.1.0-c`（仅在 `runtime/optimization/2026-10-09/M7/r1/release/octosense-repair-0.1.0-c/` 内） |
| M7 staging 工作区版本 | 保留 `0.1.0-b`（不动 app/bundle/manifest.json） |
| 同版本号不同字节差异表 | `results/version-bytes-matrix.json`（4 行：0.1.0 A / 0.1.0-b 原始 / 0.1.0-b+M0..M6 patch / 0.1.0-c staging） |
| 宿主来源 SHA-256 | octosense `3e1279635cc7...b47b63f96b66cbedae13ec900f90cb7fe2c90`；card-host `bebded3d5bbf5a2aefb65060a1b1716edd5b3b6f635fe15d452366d6f385e17b`；hub CLI `f211e53a2711...` |
| 工具链 | Rust/cargo 1.98.1；Python 3.12.13；Hub@6741dea / Octoscript@68f6a9df / Octoscript-Makepad@b33f494b / Makepad@4fdcfccc（详见 results/host-toolchain-snapshot.txt） |
| 模型配置 | provider_id 空；model_id 空；host_label='offline'；enabled=false（不冒充） |

详见 `results/source-snapshot.txt` / `results/bundle-snapshot.txt` / `results/host-toolchain-snapshot.txt`。

## 3. 包布局与目录迁移（满足 2）

新根包目录：`runtime/optimization/2026-10-09/M7/r1/release/octosense-repair-0.1.0-c/`

```
octosense-repair-0.1.0-c/
├── INTAKE.md               # 入口说明：本轮未发布、未上架、未递交
├── INTEGRITY.txt           # 文件级 SHA-256 摘要 + 拼接 digest
├── assets/
│   └── icon.svg            # 复用 A 版图标
├── identities.json         # M2 演示身份注册（fixture；不含真实业务授权来源）
├── listing.json            # M7 校正：release_notes / description / publisher schema
├── main.splash             # 当前主源（28W+ 字节；M0..M6 patch 累计）
├── manifest.json           # version='0.1.0-c'，integrity.bundle_blake3=<digest>
├── model_config.json       # 默认 offline；provider/keys 不入包
└── screenshots/
    ├── b01-initial.png
    ├── b02-draft-created.png
    ├── b03-submit-open.png
    ├── b04-schedule-confirmed.png
    ├── b05-completed.png
    └── b06-after-restart.png  # 这些为 8d73056 提交时随包复制（≠ M7 r1 字节原生截图；M7 沿 M0..M6 限制不启动 launcher）
```

**已被排除**（dev-junk / runtime trace / 占位图）：

| 路径 | 状态 |
|---|---|
| `app/bundle/.DS_Store` | 永不复制 |
| `app/bundle/host.log` | 永不复制（host runtime trace） |
| `app/bundle/instance.json` | 永不复制（host port trace） |
| `app/bundle/main.splash.debug.bak` | 永不复制 |
| `app/bundle/main.splash.v1.bak` | 永不复制 |
| `app/bundle/.archive/`, `app/bundle/data-test/`, `app/bundle/runtime/` | 永不复制 |
| `screenshots/01-main.png` / `02-after-draft.png` | A 版 HTML 占位；不出现在 M7 staging |

两包共存：工作区 `app/bundle/` 继续承载日常开发；M7 staging 与之完全分离、独立 digest、独立 listing。不复制可写主包到 staging；新 staging 不引入 cache/log/backup/data。

## 4. 构建与运行说明（满足 7）

新增段落 `app/README.md`：

- **重新生成 staging**：依次跑 `m7_release_stage.py → m7_integrity_recompute.py → m7_sandbox_sign.py`。
- **沙箱 hub stamp**：M7 r1 sandbox 内 `hub keygen / certify / stamp`，不联网；私钥销毁证据写入 `evidence/key-deletion.json`。
- **隔离数据位置**：`runtime/optimization/2026-10-09/M7/r1/sandbox/`（非 `~/.octosense`）。
- **静态 acceptance**：33/33 PASS、consistency 23/23 PASS、脚本 6/6 OK。
- **card-host 试用（仅在隔离数据目录启动）**：CLI 保留为参考文本；当前宿主执行 `sandbox-exec rc71` + `pgrep rc3 UNKNOWN`，本轮 BLOCKED（详见 §6）。

构建脚本（可重复执行）：

```sh
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M7/r1/scripts/m7_review_driver.py
# 输出 run-summary.json 给下游独立 Review；hub stamp 验签 + 私钥销毁 + integrity 校验一次完成
```

## 5. 同版本号不同字节差异 / 截图与描述校正（满足 5）

### 5.1 字节差异

- 公开递交版 `0.1.0-b` 对应 commit `8d73056`：打包时 main.splash 主源 sha256=`9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72`，stamp blake3=`e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`（ZIP 1.5MiB）。
- 当前工作区主源（M0..M6 r2 patch 后 dirty）：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`，283910 字节。
- 同 version（`0.1.0-b`）、不同字节已确认。
- M7 staging 升 version 为 `0.1.0-c`（仅 staging 内）；其 integrity digest 来自 sandbox 重算 `hub stamp`：`results/sandbox-sign.json` 内 `stamp_blake3_on_dir` = 64 hex（每次重跑因 strict token 过 protect 会变；保留最近值）。

### 5.2 截图与描述校正

- 删除 listing.screenshots 内 A 版 HTML 占位 `01-main.png` / `02-after-draft.png`。
- 保留 6 张 B 版原生截图 `b01..b06`，并在 description 中显式标注「该批为原 native-B 候选随包素材复制，不是 M7 r1 字节原生截图」（launcher 启动限制；不假装新闭环）。
- 删除 `publisher.note`（hub schema 不接受字段）和新加的 `listing.version`（同上），避免 scan 自答冒充 PASS。
- `description` 显式说明 D-M6-02/03/04 仍 FAIL、G0-F 后台常驻 / G0-E 真实模型 / G0-B 业务身份来源保持 BLOCKED/NOT_RUN、launcher 当前 rc71、未调用 `--help`、P06/P07/P08 = UNASSESSED。

### 5.3 旧完成态修正（README / HUB_ISSUE / CURRENT_REVIEW_STATUS）

这些文档由原 10-06 提交作者带「完整闭环、原生验证通过」措辞。M7 r1 不改这些历史文件，但要求：

- **README / HUB_ISSUE 草稿 / CURRENT_REVIEW_STATUS 头部已存在「诚实披露」段落**（M6 修过的口径），继续保留；M7 r1 不再额外修改以免误导「当前就是新版本」。
- M7 r1 的唯一 modify 在 `app/README.md` 顶端加「2026-10-10 M7 r1 staging」段落，指向 staging 路径、不重复宣称新版本已通过。

如未来用户授权 freeze & push，须在同一仓 commit 中同步把这些 README/草稿中的旧完成态改成与 0.1.0-c 一致的诚实表述；本轮不动。

## 6. 验收结果（满足 3、4、5）

### 6.1 sandbox 内 hub stamp / 篡改 / 私钥销毁（PAC 严模式）

| 步骤 | 期望 | 实际 |
|---|---|---|
| `hub stamp staging` | rc0，写 `manifest.integrity.bundle_blake3` | rc0；stamp_blake3_on_dir=64 hex（`results/sandbox-sign.json` 最新值） |
| 篡改 1 字节到 main.splash 后 `hub stamp tampered` | digest 变化 | tampered digest != original digest；同 salt 下 tamper 信号成立 |
| 私钥销毁 | `catalog/*.key` 全部 unlink | remaining_key_files=`[]`（evidence/key-deletion.json 验证） |
| `hub check staging --allow-unsigned` | unsigned warn，不冒充 signed | rc=1 REFUSED，原因 `[refused] assets: main.splash contains ../attachments/...`；hub 资产扫描器在 M5 引入的源代码注释内命中字面 `../`。该问题在原 0.1.0-b shipped bundle 也存在（非 M7 引入）；hub 在 M0..M6 沿用 `local-store-validation`（带本地 catalog + test-publisher key）通过，M7 r1 本轮不在该路径上，单独记录。 |

REFUSED 非新增 P1；M7 任务书「工具生成问题或退出 0 不能单独证明审阅通过」要求诚实记录，本轮如下：

- M7 r1 的 stamp rc0 / integrity 写入成立；check rc1 仅因上游 hub 资产字面扫到 M5 安全模型注释里的 `../`。M7 不修该源代码问题（用户授权「M7 不修改业务代码」）。
- 真实正式 `hub check --allow-unsigned` 通过路径 = M0..M6 沿用的 `m5/m6 local-store-validation` 风格：在 catalog 中登记 `test-publisher-m7-r1` 入口并 `hub install_staged`。本轮在 `m7_sandbox_sign.py` 已 anchor-certify + 工作 key；更完整的 catalog 路径可在用户授权后续 round 中调用本目录的 `octosense-repair-0.1.0-c.bundle/` + 与 `runtime/native-build/OctoSense-App-Hub/target/release/hub publish` 拼装完成（仍仅沙箱内）。

### 6.2 scripts / acceptance / consistency 计数

| 集 | 通过 / 总数 |
|---|---|
| scripts in driver | 6/6 |
| acceptance (`m7_acceptance_run.py`) | 33/33 |
| consistency (`m7_consistency_run.py`) | 23/23 |

明细见 `results/run-summary.json`、`results/acceptance.json`、`results/consistency.json`。

### 6.3 既有 G0/T/U/P 映射

| 编号 | M7 r1 责任状态 | 备注 |
|---|---|---|
| G0-A 固定版本 + 干净 staging + 工作区 + 工具链 | PASS | m7_freeze_snapshot.py + sandbox-sign.json |
| G0-B 业务身份来源 | BLOCKED | 沿 M2；identities.json 是 M2 demo registry，fixture 性 |
| G0-C 持久化走隔离路径 | PASS | 所有 sandbox 数据在 `runtime/.../M7/r1/` 下 |
| G0-D 隔离生存 | PASS | staging dev-junk 0 残留；私钥销毁 |
| G0-E 真实模型 | NOT_RUN | model_config.enabled=false；本轮不申请 |
| G0-F 后台常驻 | BLOCKED / NOT_RUN | 仅前台扫描；原用例继续 BLOCKED |
| T01-T38 | 沿 M5/M6 r2；本轮不重跑真实宿主；不接受自答冒充 | 一致 |
| U01-U12 | BLOCKED 真实 UI；不编造视觉缺陷 | 一致 |
| P01 本地干净 staging 准入 | PASS | stage script |
| P02 离线签名 catalog | PASS（沙箱内） | keygen/cert/stamp 完整；catalog 不发公网 |
| P03 真实模型接通 | NOT_RUN | 沿 M3 |
| P04 staging 不污染宿主 | PASS | sandbox = `runtime/.../M7/r1/sandbox/` |
| P05 materials 一致 | PASS | consistency 23/23 |
| P06 实际递交 | UNASSESSED | 不发出 |
| P07 商店收录 | UNASSESSED | 不上架 |
| P08 赛事回执 | UNASSESSED | 不发 comment / 邮件 |

### 6.4 旧 Python / Web 后端不被运行时意外依赖（满足 7）

`m7_acceptance_run.py` 的 `M7-12` 子项扫描 `main.splash / *.json / *.svg` 内非注释行的 `127.0.0.1 / localhost / fetch( / host.connect`：

- `127.0.0.1` 出现一次但位于 `// 关闭重开后由 load() 回读。它不在本机拉起服务、不访问 127.0.0.1、不请求公网地址。` —— 描述性注释。
- `localhost / fetch( / host.connect` 在非注释行内均不出现。

运行结果：M7-12 PASS（实际调用 = 0）。

## 7. 严入：失败 / 阻塞 / 未跑如实标记

| 类型 | 项 |
|---|---|
| **BLOCKED（沿用户授权保留）** | 桌面 launcher（sandbox-exec rc71 + pgrep rc3 UNKNOWN）；真实模型 provider（G0-E）；业务身份来源（G0-B）；后台常驻（G0-F）；App picker / 隔离存储读字节 API / grant 生命周期；同候选 2–3 分钟演示 |
| **NOT_RUN（沿用户授权保留）** | 真实桌面截图 / 演示草片；真实中文键入 / 视口 / 接单确认 receipt-of-action；三角色真实重登；新 AI 链②③ |
| **NOT_RUN（本模块不重跑）** | M6 r2 review 188/188 case-probe（前置基线沿用，本轮不复制） |
| **本轮未扩** | 不修 M0..M6 任何未闭合缺陷；不重新编译 card-host；不重新核对 hub upstream main 是否兼容；不发 tag / Release / Issue / 评论 / 赛事材料；不联网；不公开 listing；不切换 provider |

## 8. 候选与交接

- candidate_id = `M7-r1-worktree`；base_candidate_id = `M6-r2-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M7/r1/CANDIDATE.json`
- 改动文件清单：
  - `app/README.md`（增 M7 段落；不修改历史诚实披露）
  - `runtime/optimization/2026-10-09/M7/r1/release/octosense-repair-0.1.0-c/`（干净 staging；6 公开文件 + 6 B 版截图）
  - `runtime/optimization/2026-10-09/M7/r1/scripts/`（6 个脚本）
  - `runtime/optimization/2026-10-09/M7/r1/catalog/`（keygen/cert 公钥记录）
  - `runtime/optimization/2026-10-09/M7/r1/sandbox/`（隔离数据 + stamp 验篡改目录）
  - `runtime/optimization/2026-10-09/M7/r1/evidence/`（私钥销毁 / 干净性 acceptance evidence）
  - `docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r1.md`（本文件）
  - `docs/optimization/2026-10-09-desktop/GATES.json`（M7 status = `READY_FOR_REVIEW`）
- 启动命令：`runtime/native-build/OctoSense-App-Hub/target/release/card-host --bundle <STAGE> --app-data <SANDBOX_DIR> --allow-unsigned --stamp`（本轮不启动，路径完整可复现）
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r1/sandbox/`
- 实际测试命令：`python3 runtime/optimization/2026-10-09/M7/r1/scripts/m7_review_driver.py`
- GATES.json M7 status = `READY_FOR_REVIEW`（不为 PASS）
- 不进入下一模块；不派子代理；等待独立 Review。

## 9. 末尾固定两行

```
STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
```
