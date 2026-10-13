# M3 实施报告 r8

- 模块 / 目标：M3「真实输入与AI报修」修复轮 —— 严格按 M3_REVIEW_r9 缺陷清单修复，只修清单项，不发散。
- candidate_id / base_candidate_id：**M3-r8-worktree** / M3-r7-worktree（冻结清单 `runtime/optimization/2026-10-09/M3/r8/CANDIDATE.json`）。
- HEAD / 未提交差异 / 源文件哈希清单：HEAD `8d730569546cb57310944bb299695134df773b9d`，dirty（含其他模块共享改动，全部保留）。
  - `app/bundle/main.splash`：552591 B / SHA256 `cc193cf0a5015d8475167403a125def3a183efb17dd13336453de47f4d0fe7e8`（r9 审查快照 0fb141f9 之上仅本轮 3 处修复；冻结副本 `M3/r8/source.main.splash`）
  - `app/bundle/manifest.json`：`53b50ea2…`（未变）
  - `app/bundle/model_config.json`：`55b41c80…`（未变）
  - `app/bundle/identities.json`：`75971e03…`（未变）
- 目标宿主 / 二进制来源与哈希 / 依赖：固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`（SHA256 `3e127963…`，沿用审查轮同一二进制）；本构建方不启动宿主，原生运行由驱动在沙箱外经 harness 执行。
- 实际模型路由检查结果（开发会话）：当前构建方为 Kimi-K3（Abram 2026-10-11 21:03 裁决）；本接口不能验证主会话 Router 实际路由，不声称已切换。
- 已检查的前置 PASS 报告：M2 仍 FAIL（M2_REVIEW_r10），按用户前序挂账裁决继续本模块，不伪造前置满足、不改 M2 结论。
- 本轮修改文件与原因（仅 `app/bundle/main.splash` 三处，逐条对应 r9 清单）：
  1. **D-M3-04（必修 P1）合法来源重核自拒**：`_validateSourceEntry` 归一化输出新增 `version_present` 元信息（默认 false；仅 `entry.version != nil` 时置 true），区分"未声明 version"与归一化默认值 0；`_validateSourcesSnapshot` 确认重核改为只在原声明存在时回传 version（旧快照缺 `version_present` 字段时 version 非 0 才视为曾声明，兼容既有持久草稿）。合法无版本 space/asset 正例首次 verified → 落草稿 → 确认重核仍 verified；伪 version999、非空伪 quote、假 ID、跨项目、停用、版本不一致负例仍降 unverified_text 或拒绝。守卫未删除、未放行任意 version。
  2. **D-M3-01 残余（P2）解析诊断**：`_authorityHistoricalConfirm` 返回字段 `ok` 被固定宿主解析器当语法操作（r9 每场 4 条 parser 诊断来源，冻结源 6718/6750），改名 `confirmed`；该 helper 当前**无消费点**（历史核验路径经 `_authorityCheckConfirmedOpen`），已注释如实说明用途；全文件不再有 `ok:` 对象字段。
  3. **D-M3-02 残余（P2）首 tick 恢复回调异常**：tick 恢复分支 `catch _` 绑定（实测报 `variable _ not found in scope`）改 bare catch；`_ZH_RESTORED` 只在控件实际恢复成功后置位，失败保留原文、下个 tick 重试并写可见诊断（"输入恢复重试中：控件暂未就绪，原文已保留"）；无持久原文路径直接置位不循环；不以清空原文/吞错规避。
- 桌面 UI/交互变化：无新增 UI；恢复失败时状态行出现重试诊断。
- 接口 / 数据迁移 / 旧数据恢复方式：`PENDING_DRAFT.sources.*` 快照新增 `version_present` 字段；旧快照无该字段时按"version 非 0 才视为曾声明"兼容处理，不清空既有草稿。
- 已有别人修改的保留与适配：r9→r8 间共享文件含 M2/M4–M7 后续修改（如 `_currentFactsVersion` 的 services 拼接被 M4 改为 `_strJoin`，语义保留）——全部保留未动；r7 验证脚本对该点断言按字面匹配已过时（25/26），语义不变，不是回归。未 reset/stash/删除任何他人改动。
- 启动步骤 / 隔离数据位置：不自行启动宿主；harness 请求 `runtime/optimization/2026-10-09/M3/native/REQUEST_build_r8.json`（4 场景，均 needs_model=false），证据由驱动写 `M3/native-runs/build_r8_REQUEST_build_r8/`。
- 应用运行模型/provider（无秘密）：MiniMax / MiniMax-M3 / anthropic messages（`model_config.json`，密钥仅 harness 代理从 runtime/secrets 注入，宿主只拿占位符）。本轮 0 真实模型请求（历史累计 r3 Python 3 次 ≤10）。
- 覆盖的既有验收项与证据运行形态：

|检查|输入与步骤|预期|实际|结论|证据路径|
|---|---|---|---|---|---|
|真实桌面操作|REQUEST_build_r8 四场景冷启动+tap/capture|解析诊断清零、view=true、原文恢复无回调错误|待驱动执行|NOT_RUN（构建方不启动宿主）|`M3/native-runs/build_r8_REQUEST_build_r8/`（待生成）|
|权威状态与回执|合法来源草稿确认至 M2 回执|正例确认成立、负例拒绝|源码修复 + Python 等价正负例 10/10；原生未跑|PARTIAL（源码级）|`M3/r8/evidence/r8_fix_verification.json`|
|失败与重试|伪 version/quote/假 ID/停用/stale 负例|降级或拒绝，无业务副作用|等价语义执行通过；原生未跑|PARTIAL（源码级）|同上|
|重启恢复|预存 pending_input 冷启动|原文保留、恢复回调无 `variable _` 错误、不假成功|待驱动执行|NOT_RUN|`M3/native-runs/build_r8_REQUEST_build_r8/`（待生成）|
|受影响先前模块回归|r7 修复不回退静态核对|26 项中 25 项保持（1 项为 M4 `_strJoin` 字面断言过时，语义保留）|通过|PASS（静态）|`M3/r8/evidence/r8_fix_verification.json`、`M3/r7/evidence/r7_fix_verification.json`|

## 本轮验证已执行（构建方）

- `M3/r8/scripts/m3_r8_fix_verification.py` → **23/23 PASS**（`M3/r8/evidence/r8_fix_verification.json`），含 D-M3-04 十组功能等价正/负例：
  - 正例：space/asset 无 version/quote 首次 verified 且确认重核通过；声明 version 与事实一致通过；旧快照 version=0 无 version_present 按未声明处理通过。
  - 负例：伪 version999、伪 quote 降 unverified_text；假 ID unknown_fact、停用 inactive、版本不一致 stale 均确认拒绝；快照 verified 但事实版本已变重核 stale 拒绝。
- `M3/r8/evidence/r8_static_check.json` → pass:true（无 `ok:` 字段、tick 恢复分支 bare catch、根表达式/内联模式不回退）。
- vendored parser（`octoscript-core` 测试 `m2_r7_bundle_parse`，VM 兼容模式解析当前 main.splash）→ **PASS**。
- r7 回归脚本重跑 25/26（唯一失败为 M4 `_strJoin` 字面匹配过时，语义保留，非回归）。
- 离线签名 catalog/store 重建：`prepare_build_r8.py` 全步骤 rc0（verify + install_staged 探针），anchor `c1c515ad…`、digest `fbcb6867…`；**两把私钥已删**（`M3/native/build_r8/offline-store-evidence.json` 记录删除证据，keys 目录为空）。不联网、不 publish、不 listing。

## 尚未完成

- **harness 冷启动证据：NOT_RUN** —— 请求已冻结（`REQUEST_build_r8.json`，4 场景），由驱动在本阶段结束后沙箱外执行；结果与截图路径待写 `M3/native-runs/build_r8_REQUEST_build_r8/`。本报告不预称解析清零或渲染通过；r9 审查对当前 0fb 快照的 4 场冷启动（view=true、4 parser + 1 恢复错误/场）是修复前基线。
- **三组真实 MiniMax 建议、真实恶意模型返回、AI/手工合法确认至权威回读、展示/采纳交错、精确提交故障/重开：NOT_RUN** —— 固定宿主 type/key 被明确拒识（r8/r9 review 实证），属白名单通道 BLOCKED，非 rc71/rc3；本模块不能用未授权自动化绕过。
- D-M3-03/05/06/07 源码改善保留，动态闭合待通道解阻。
- `_authorityHistoricalConfirm` 改名后仍无调用方（r9 清单已注明此情形），如实交接。

## 交接

- 候选清单：`runtime/optimization/2026-10-09/M3/r8/CANDIDATE.json`（candidate_id=M3-r8-worktree，base=M3-r7-worktree，四项冻结对象 SHA256/字节数）。
- 冻结源副本：`M3/r8/source.main.splash`。
- 证据：`M3/r8/evidence/r8_fix_verification.json`（23/23）、`r8_static_check.json`（pass）、`M3/native/build_r8/offline-store-evidence.json`（验签/install rc0、私钥删除）。
- harness 请求：`M3/native/REQUEST_build_r8.json`；截图/日志待驱动产出。
- 实际测试命令：`python3 runtime/optimization/2026-10-09/M3/r8/scripts/m3_r8_fix_verification.py`、`python3 runtime/optimization/2026-10-09/M3/native/prepare_build_r8.py`。
- 编码方仅将 GATES.json 的 M3 置 READY_FOR_REVIEW；PASS 等待独立审查。

STATUS=READY_FOR_REVIEW
NEEDS_ABRAM=no
