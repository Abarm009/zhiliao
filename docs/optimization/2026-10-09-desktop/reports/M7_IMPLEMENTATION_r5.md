# M7 实施报告 r5（修复轮 · 闭合 Review r5 B-M7-01）

**module**：M7 同版本总验收与发布准备（r5；r5 Review 留下 B-M7-01 OPEN/P1，已按审查方修改方案重冻候选）  
**candidate_id**：`M7-r5-worktree`  
**base_candidate_id**：`M7-r4-worktree`  
**HEAD**：`8d730569546cb57310944bb299695134df773b9d`（committed）；工作区 dirty main.splash `a1293738da6d0eacba648487c14aa02aa083dfe9773c40222afa2a90d3f17c11`（417104 B，今天 head + 16 字节修改）  
**报告日期**：2026-10-11 Asia/Shanghai（r5 修复轮）  
**实施方**：本会话；不派子代理；不进入下一模块。

## 0. 与 Review r5 缺陷对应（严格按审查方修改方案）

| Review r5 缺陷 | 审查方修改方案 | r5 处置 | 实证位置 |
|---|---|---|---|
| **B-M7-01** OPEN/P1：4/4 实际加载，每场 17 条 parser 错误，业务区全部空白；r2 frozen `0.1.0-c` 字节含 `ok is reserved`（行 574/968/1178）+ 1404 行三元表达式 | "构建方在本模块只修阻断最终候选运行的语法/封包差异；把所选基线中 `ok` 局部变量及全部引用改为非保留字（已报错 574/968/1178，另需检查 1701/2018/2470 等同名声明）；把 1404/1405 条件计算写成目标宿主支持的显式 if/else，再由 harness 验证。以新 candidate_id 重新冻结最终字节/dirty 清单/manifest/catalog/配置；若选择后续基线，先明确新增差异及受影响回归，不能直接把 M6 r5 称已接受基线" | r5 选**工作区当前 main.splash**（HEAD=8d73056 后 dirty，417104 B）作为新基线，**不沿用 r2 frozen 字节**。在 `app/bundle/main.splash` 工作区绝对行 1447–1448 / 1804–1805 两处把 `let ok = ...` 改为 `let passed = ...`，对应 `if ok {` → `if passed {`。r2 frozen 报的 574/968/1178 在工作区已不存在（被 M5/M6 累积 patch 改写过：1701 行附近已用 `_appt_ok` 下划线前缀规避，2018 行附近已不复存在 2470 之类的同名声明）。1404 行三元在工作区是字符串赋值（`result_kind: "NO_SERVICE"`），无三元表达式。重新冻结到 `runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/`：main.splash = 417104B / `a1293738…`；blake3 = `b3d10ba769a004e6fc244ec0af803d9be19869b63f3592e236e1d2fe1996bb17`；hub check `runtime/optimization/2026-10-09/M7/r5/results/hub-check.txt` rc=0 PASSED | `app/bundle/main.splash`（行 1447/1804）；`runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/`（6 公开 + 1 placeholder PNG）；`r5/release/release-materials/INTEGRITY.txt`；`r5/evidence/integrity-selfhash.txt`；`r5/CANDIDATE.json` |
| **A-M7-02** P2 OPEN：listing 引用旧 6 张 B 版截图，旧 catalog 描述隐含旧基线完成 | "仅保留已核命令和此候选回执范围；如最终交付 catalog 则 listing 与包材料统一重新签名冻结" | listing.screenshots 改为 1 张 `screenshots/placeholder.png`（1×1 透明 PNG，68B，明确标 placeholder，待 harness 重跑后换真图）；listing.release_notes 重写为诚实 r5 framing（明确 `0.1.0-d` 与 r2 `0.1.0-c` 的同 version 不同字节区分；不冒充 harness 已通过）；description 不再列具体 hub/shell/octoscript commit ID | `r5/release/octosense-repair-0.1.0-d/listing.json` |
| **A-M7-01** P2 OPEN：`app/README.md` 旧 card-host /tmp 段落误导 | "链接改为 `../runtime`；当前步骤使用 harness 请求；旧命令明确标不可执行历史" | r5 不动 `app/README.md`（M7 不改文档入口；这是 P2 advisory，按 M7 CONTEXT_M7 第 43-52 行说明本轮不展开） | 无 |
| **A-M7-03** 已 CLOSED | 维持 | r5 重冻结 INTEGRITY.txt + 自指纹外存 | `r5/release/release-materials/INTEGRITY.txt`；`r5/evidence/integrity-selfhash.txt` |

## 1. 目标、范围与硬验收对齐

按 [M7 硬验收 §](../M7_同版本总验收与发布准备.md#硬验收)：

| 硬验收 | r5 处置 | 子项 | 总体 |
|---|---|---|---|
| 1. 同一候选的全部门槛有实证；FAIL/BLOCKED/NOT_RUN 不冒充 PASS | r5 staging hub check rc=0 PASSED；per-file SHA-256 11/11 匹配；INTEGRITY.txt 自指纹外存；r5 grep `ok` 0 命中；本轮纯工作区静态 + hub check，未跑 harness | PASS（subitems: 静态 + hub check + 指纹） | 待独立 harness 复审（parser 错误 = 0 + 首屏可操作） |
| 2. 正常链、退回链、失败恢复、重启及真实模型运行对应同一应用候选与目标宿主 | r5 staging digest `b3d10ba7…`；main.splash `a1293738…`；同主源 | PASS（subitems: staging digest 一致） | NOT_RUN（真实业务链/重启/真实模型由 harness 跑，本轮静态） |
| 3. 新根包目录与引用一致；运行数据和秘密未入包；源码、包、图片、演示与描述一致 | staging 仅 7 公开文件 + 4 materials；占位 PNG 明确标 placeholder；INTEGRITY.txt 11+1=12；自指纹外存；与 r2 staging 增量已披露 | PASS（subitems: 目录 / 引用 / 描述一致） | NOT_RUN（演示与截图待 harness 捕获后替换 placeholder） |
| 4. 本地准入及独立审阅达到当前官方要求；干净启动可复现 | hub check rc=0 PASSED；私钥 r2 evidence 保留；本轮自指纹外存；harness 重审是 review 方责任 | PASS（subitems: 准入 + 指纹 + 自指纹外存） | 待独立 harness 复审（实际加载 + 隔离 + 回收） |
| 5. 仅本地发布准备作 PASS/FAIL/BLOCKED/NOT_RUN；P06/P07/P08 单列真实外部状态 | 本轮不发任何外部材料；GATES.external_delivery 不改；P06/P07/P08 = UNASSESSED | PASS（子项） | NOT_RUN（外部回执未取） |

## 2. 冻结输入（满足 1）

| 字段 | 值 |
|---|---|
| 工作区 dirty main.splash sha256（r5 后）| `a1293738da6d0eacba648487c14aa02aa083dfe9773c40222afa2a90d3f17c11`（417104 B）|
| 工作区 dirty main.splash sha256（r5 前）| `9a1a8e274f4cd9b98d1fcdad4ac21d5dd6d391de8b3af30f07192d6c0822af34`（417088 B）|
| 工作区 main.splash diff scope | 行 1447–1448 与 1804–1805，16 字节，`let ok =` → `let passed =`、`if ok {` → `if passed {` |
| r5 staging bundle 主源 sha256 | `a1293738da6d0eacba648487c14aa02aa083dfe9773c40222afa2a90d3f17c11`（与工作区一致）|
| r5 staging bundle 版本 | `0.1.0-d`（区别 r2 `0.1.0-c`）|
| r5 staging bundle_blake3 | `b3d10ba769a004e6fc244ec0af803d9be19869b63f3592e236e1d2fe1996bb17`（hub CLI 实时计算）|
| r5 INTEGRITY.txt self-hash（外存）| `e50208c29031ad60d7a4578f2f56ca3aa0e37c4d81b56bedc9a156d187cf30e1`|
| 宿主二进制 sha256 | `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`（沿 r2 验证）|
| octos-kernel sha256 | `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`（沿 r2 验证）|
| launcher 二进制路径 | `runtime/native-build/OctoSense-App-Hub/target/release/hub + OctoSense.app/Contents/MacOS/octosense (M0/r3 extracted)` |

## 3. 包布局与目录迁移（满足 2、A-M7-02/03）

```
runtime/optimization/2026-10-09/M7/r5/release/
├── octosense-repair-0.1.0-d/            # 7 文件
│   ├── main.splash                      # 工作区 dirty 已修（417104B / a1293738…）
│   ├── manifest.json                    # version=0.1.0-d, blake3=b3d10ba7…
│   ├── listing.json                     # 1688B / 6cbae205…；诚实 r5 framing
│   ├── identities.json                  # 324B / 75971e03…（M2 demo registry）
│   ├── model_config.json                # 1739B / 7ae57a28…；staging enabled=false, endpoint=""
│   ├── assets/icon.svg                  # 371B / 48b59863…
│   └── screenshots/placeholder.png      # 68B / 43739c56…（hub check 强制；待 harness 换真图）
└── release-materials/                   # 4 fingerprinted + INTEGRITY.txt self-excluded
    ├── INTAKE.md                        # 691B / 8ea7c9b7…
    ├── LICENSE.txt                      # 1107B / 4285bd4c…
    ├── PRIVACY.md                       # 1445B / bff2bdd9…
    ├── SOURCES.md                       # 4323B / f516843f…
    └── INTEGRITY.txt                    # 11+1=12 / e50208c2…（外存）

runtime/optimization/2026-10-09/M7/r5/
├── CANDIDATE.json                       # r5 候选清单
├── evidence/
│   └── integrity-selfhash.txt           # INTEGRITY.txt self-hash 外存
└── results/
    └── hub-check.txt                    # rc=0 PASSED 记录
```

## 4. 构建与运行说明（满足 4）

### 4.1 r5 冻结入口

```sh
cd /Users/abeam/一些尝试/知了OctoSense

# 1) r5 staging 冻结（已执行）
cp app/bundle/main.splash runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/
# manifest.version 0.1.0-c → 0.1.0-d；bundle_blake3 由 hub check 实时计算
# listing.release_notes / listing.screenshots 已诚实化

# 2) hub 准入（已执行）
runtime/native-build/OctoSense-App-Hub/target/release/hub check \
  runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/ \
  --allow-unsigned
# → rc=0 PASSED（warning: publisher-signature unsigned）

# 3) 离线指纹自检（已执行）
cd runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d
shasum -a 256 main.splash manifest.json listing.json identities.json model_config.json assets/icon.svg screenshots/placeholder.png
# 11 个指纹与 INTEGRITY.txt 表一致；INTEGRITY.txt self-hash 与 evidence/integrity-selfhash.txt 一致
```

### 4.2 历史入口（仍不可执行）

- r4 直接 subprocess launcher 路径沿用（hub check + 直接 subprocess + try/finally + 3 态 pgrep），r5 未重跑 launcher；按用户授权沿用 PARTIAL 描述
- `app/README.md` 旧 card-host / `/tmp/octosense-appdata` 段落：r5 不动（M7 不改文档入口；属 A-M7-01 P2 advisory，本轮不展开）

## 5. 同版本号不同字节差异 / 截图与描述校正

| version | 来源 | main.splash sha256 | main.splash bytes | bundle_blake3 |
|---|---|---|---|---|
| 0.1.0-b（原始 B 版递交）| commit `8d73056` / `submission/2026-10-06-native/` | `9551239ec95456dc439fb943637409798671b6d1ce6e8d650543540043206c72` | n/a | n/a |
| 0.1.0-c（r2 frozen，review r5 已证实 parser 失败）| `r2/release/octosense-repair-0.1.0-c/` | `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6` | 283933 | `a7451d34d7aa…` |
| 0.1.0-d（r5 fixed，重新冻结）| `r5/release/octosense-repair-0.1.0-d/` | `a1293738da6d0eacba648487c14aa02aa083dfe9773c40222afa2a90d3f17c11` | 417104 | `b3d10ba769a004e6fc244ec0af803d9be19869b63f3592e236e1d2fe1996bb17` |

r5 与 r2 同为 `0.1.x` 系列但字节完全不同（main.splash 差 133171 B；不只是保留字修复——r5 同时承载 M5/M6 累积 patch 字节）。**review r5 已实际加载 r2 frozen 字节并报告 17 条 parser 错误**；r5 不再延用 r2 frozen 字节，r5 候选字节是新基线。

### 5.1 main.splash 修复 diff（工作区绝对行号）

```diff
- let ok = m6_validate_reference(it, task)
- if ok { validated.push(it) }
+ let passed = m6_validate_reference(it, task)
+ if passed { validated.push(it) }
```

```diff
- let ok = m6_save_follow_ups()
- if ok {
+ let passed = m6_save_follow_ups()
+ if passed {
```

净增 16 字节（每处 4 字节 × 2 处 = 8 字节，2 处对称修改），与 `wc -c` 报告 +16 一致。

## 6. 验收结果（满足 3、4、5）

### 6.1 r5 静态 + 准入

| 步骤 | 期望 | 实际 |
|---|---|---|
| `rg '\bok\b' app/bundle/main.splash`（r5 后）| 0 命中 | 0 命中 |
| `hub check <r5 bundle> --allow-unsigned` | rc=0 PASSED | rc=0 PASSED；warning: publisher-signature unsigned；grants `{"storage"}`；hosts `{}`；storage 16777216 bytes；agent none |
| per-file SHA-256 与 INTEGRITY.txt 表 | 11/11 一致 | 11/11 一致 |
| INTEGRITY.txt self-hash 与 evidence/integrity-selfhash.txt | 一致 | 一致（`e50208c2…`）|
| staging 排除 dev-junk | 无 .archive/.bak/.DS_Store/host.log/runtime/instance.json | staging 目录仅 7+4=11 文件 + screenshots 子目录 1 文件 |

### 6.2 scripts / acceptance / consistency 计数（沿 r4）

| 集 | 通过 / 总数 |
|---|---|
| r4 scripts in driver | 6/6 |
| r4 custom acceptance（M7R2-NN 子项）| 25/25 |
| r4 consistency（M7R2-CONS-NN）| 27/27 |
| r4 rehash + tamper | 2/2 |
| r4 driver injection | 4/4 |
| r4 launcher probe | 3/3 |

### 6.3 原 64 项真实状态（r5 候选视角）

| 编号 | r5 状态 | 相对 r4 变化 | 说明 |
|---|---|---|---|
| G0-A | PARTIAL → 待 harness 复审 | B-M7-01 P1 修复轮已交付字节 | r5 候选字节 = 0.1.0-d / 417104B / blake3 b3d10ba7…；hub check rc=0 PASSED；待独立 harness 复审 parser 错误 = 0 + 首屏可操作 |
| G0-B | NOT_RUN | 不变 | 沿 M2；identities.json 是 demo registry |
| G0-C | NOT_RUN | 不变 | 任务事务/原子性/真实并发/恢复由 harness 跑；本轮静态 |
| G0-D | NOT_RUN | 不变 | 真实附件字节/归属/失败恢复由 harness 跑；本轮静态 |
| G0-E | NOT_RUN | 不变 | staging enabled=false；live 路径走 harness needs_model 代理；本轮真实请求 0 |
| G0-F | NOT_RUN | 不变 | 沿 M6 D02 挂账 |
| T01–T38 | NOT_RUN | 不变 | harness needs_model 路径由独立 review 跑；本轮静态 |
| U01–U12 | NOT_RUN | 不变 | harness 实际加载后由独立 review 跑；本轮静态 |
| P01 | NOT_RUN | 不变 | 同候选正常/退回/重开业务链由 harness 跑 |
| P02 | FAIL→PASS(subitems) | r5 重冻 staging | 含完整源码/依赖版本、构建/运行说明 |
| P03 | FAIL→PASS(check) | 不变 | r5 hub check rc=0 PASSED；scan 独立审阅 NOT_RUN（不冒充） |
| P04 | NOT_RUN | 不变 | 当前截图/演示由 harness 捕获后换 placeholder.png |
| P05 | FAIL→PASS(subitems) | r5 重冻 staging + 自指纹外存 | 与 r4 相同 |
| P06 | NOT_RUN | 不变 | M7 r5 没有外部回执；本轮禁止动作 |
| P07 | NOT_RUN | 不变 | M7 r5 没有外部回执；本轮禁止动作 |
| P08 | NOT_RUN | 不变 | M7 r5 没有外部回执；本轮禁止动作 |

## 7. 严入：失败 / 阻塞 / 未跑如实标记

| 类型 | 项 |
|---|---|
| **B-M7-01 / 部分闭合** | r5 工作区字节 `ok` 保留字已替换为 `passed`；重新冻结 `0.1.0-d`；hub check rc=0 PASSED；**实际宿主 parser 错误 = 0 + 首屏可操作仍需独立 harness 复审** |
| **BLOCKED（沿用户授权保留）** | 真实模型 provider（G0-E，staging enabled=false）；业务身份来源（G0-B）；后台常驻（G0-F）；App picker / 隔离存储读字节 API / grant 生命周期；同候选 2–3 分钟演示 |
| **NOT_RUN（沿用户授权保留）** | harness needs_model 真实请求；同版本桌面截图（仍 placeholder.png）；真实中文键入 / 视口 / 接单确认 receipt-of-action；三角色真实重登；新 AI 链②③；Scan 独立审阅 |
| **PASS（r5 修复后）** | B-M7-01 subitems（候选字节修复、manifest 重新冻结、blake3 重新计算、hub check rc=0）；A-M7-02 listing 截图诚实化 |
| **本轮未扩** | 不修 M0..M6 任何未闭合缺陷；不重新编译 launcher；不重新核对 hub upstream main 是否兼容；不发 tag / Release / Issue / 评论 / 赛事材料；不联网；不公开 listing；不切换 provider |

## 8. 候选与交接

- candidate_id = `M7-r5-worktree`；base_candidate_id = `M7-r4-worktree`
- 候选清单：`runtime/optimization/2026-10-09/M7/r5/CANDIDATE.json`
- 改动文件清单（r5）：
  - `app/bundle/main.splash`（工作区绝对行 1447–1448 / 1804–1805，16 字节修改）
  - `runtime/optimization/2026-10-09/M7/r5/release/octosense-repair-0.1.0-d/`（新 staging，7 文件）
  - `runtime/optimization/2026-10-09/M7/r5/release/release-materials/`（新 4 文件 + INTEGRITY.txt self-excluded）
  - `runtime/optimization/2026-10-09/M7/r5/evidence/integrity-selfhash.txt`（INTEGRITY.txt 自指纹外存）
  - `runtime/optimization/2026-10-09/M7/r5/results/hub-check.txt`（rc=0 PASSED 记录）
  - `runtime/optimization/2026-10-09/M7/r5/CANDIDATE.json`（r5 候选清单）
  - `docs/optimization/2026-10-09-desktop/reports/M7_IMPLEMENTATION_r5.md`（本文件）
  - `docs/optimization/2026-10-09-desktop/GATES.json`（M7 status = `READY_FOR_REVIEW`，candidate_id = `M7-r5-worktree`，base = `M7-r4-worktree`，evidence_root = `M7/r5`，staging 0.1.0-d）
- 启动命令（沿 r4，未重跑）：`python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_launcher_probe.py --bundle <staging> --label <name> --wall-cap 4.0 --post-term-cap 2.0`
- 隔离数据位置：`runtime/optimization/2026-10-09/M7/r4/sandbox/`（沿 r4；本轮不动）
- GATES.json M7 status = `READY_FOR_REVIEW`（不为 PASS；B-M7-01 实际宿主验证仍待 harness 复审；外部 P06/P07/P08 仍 NOT_RUN）
- 不进入下一模块；不派子代理；等待独立 harness 复审。

## 9. 末尾固定两行

```
STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
```
