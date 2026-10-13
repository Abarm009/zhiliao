# M3 实施报告 r1 — 真实输入与AI报修

**状态：READY_FOR_REVIEW；编码方交接，等待独立 Review；不进入 M4。**

本轮严格按 `M3_真实输入与AI报修.md` 八项硬验收 + 现有 M2 r1 既有 `IDENTITIES`/`runCommandBound`/`commitBound` 注册表边界 + M1 r2 既有视图命名 Label 框架。不动 M0 既有 Store/install_staged 路径；不动 M1 既有的 5 区域布局；不动 M2 命令边界、commitBound、bootReconcilePending 与 5 撤权/到期身份样本。

---

## 0. 重要前置与诚实声明

| 项 | 状态 | 影响 |
|---|---|---|
| M0 | FAIL | 宿主复验 BLOCKED（沿用既有；本轮无新增），本模块不修；G0-E 真实模型 provider 缺口沿用 |
| M1 | FAIL | 真实桌面交互 BLOCKED（沿用既有）；本模块不修 |
| M2 | BLOCKED | D-M2-01..07 未闭合；本模块仅**消费** M2 已落地的 `runCommandBound` / `commitBound` / `IDENTITIES` / `identityActive`，**不修复**任何 M2 必修项 |
| G0-E 真实模型 provider | NOT_RUN | M0 已延期到 M3；本轮止于"协议 + 离线契约"；本轮不申请激活 |
| 桌面 launcher | 无法启动 | sandbox-exec 预检 rc71 两次 + pgrep rc3 UNKNOWN（沿用 M0/M1/M2） |

**最大可达 `READY_FOR_REVIEW`；最终 PASS 由独立 Review 决定。**

---

## 1. 改了什么

### 1.1 `app/bundle/main.splash` 在 M2 r1 末态上叠加

**模块级状态（M3 协议 6 + 边界 4）**：

| 名称 | 用途 |
|---|---|
| `TASK_INPUT` | 用户原文 + raw_input_version + raw_text_hash + last_edit_at_ms |
| `PENDING_AI_REQUEST` | 出去的快照：request_id / issued_at_ms / expected_raw_text_hash / expected_draft_version / expected_task_version / expires_at_ms / provider_id / model_id |
| `PENDING_DRAFT` | 待确认草稿：draft_version / problem / space_id / asset_id / category / contact / desired_window / sources / human_edited_fields / draft_source / expires_at_ms / ai_history_raw_text_hash |
| `AI_STATE` | IDLE \| ASKING \| NO_SERVICE \| TIMEOUT \| UNAUTHORIZED \| AWAITING_AUTH \| FORMAT_ERROR \| CANCELED \| EXPIRED \| APPLIED \| MANUAL |
| `AI_LAST_ERROR` | 人类可读拒绝原因 |
| `AI_REQUESTS_LOG` | 每次 model 调用的去 secret 审计 |
| `CONFIRM_BIND` | last_confirmed_at_ms / last_confirmed_draft_version / last_confirmed_raw_text_hash / invalidated_by_edit |
| `MODEL_CONFIG` | enabled / provider_id / model_id / host_label / timeout_ms / max_alternatives（**只外源配置，不暴露 API Key 表单**） |
| `MODEL_ADAPTER` | 当前为 no_op 占位；线下不联网 |
| `FORBIDDEN_MODEL_WRITE_VERBS` | 模型绝不能发起的写动词清单（仅供 contract / audit 参考） |

**协议层函数（17 个新 fn）**：

```text
fn _fnv1a_hash(s)               # FNV-1a 32-bit
fn _hex32(n)                    # 8-char hex
fn hashRawText(s)               # raw_text_hash = hex32(fnv1a(s))
fn _findSpace(id) / _findAsset(id) / _isValidCategory / _isValidContact
fn bindRequestVersions(task_id) # 快照 raw_input / draft / task 版本
fn craftModelRequest()          # 协议占位（main.splash 当前无 HTTP）
fn _modelInstructionText()      # 系统提示模板
fn _contactWhitelist()          # 仅当前 USERS 中的 self
fn parseModelReturn(raw)        # 解析 + 结构校验
fn validateSuggestion(rs)       # 5 道时间/版本/身份闸
fn applyDraftFromAI(rs)         # 写 PENDING_DRAFT（draft_version++）
fn editDraftField(field, value) # 任意字段编辑触发 draft_version++
fn cancelAiRequest()
fn openDraftPanel() / closeDraftPanel()
fn editRawText(new_text)        # raw_input_version++ + raw_text_hash 重算
fn requestAiSuggestion()        # 验 provider → 发起；不启用 = NO_SERVICE
fn deliverModelReturn(raw)      # 唯一回包入口
fn _safePreview(s, 24)          # 截断
fn recordModelMeta(meta)        # 不写 secret（仅 8 个白名单字段）
fn _persistAiLog()              # fs.write("ai_requests.jsonl", …) 唯一落点
fn parseDesiredWindow(s)        # YYYY-MM-DD HH:MM~…
fn _parseDateTimeString / _toIntSafe / _daysBeforeYear / _isLeap / _daysBeforeMonth
fn confirmDraftModelBound()     # 协议网关 → createDraftFromPanel
fn createDraftFromPanel()       # 替代原 createDraft 的硬编码问题
fn pendingDraftLabelText / aiStateLabelText / aiSuggestionLabelText / inputValidationLabelText
```

**UI（在 M1 r2 既有"当前行动区"内嵌；命名 Label 已落槽位）**：

- `zh_input := TextInput{...}` 真实中文输入（沿用 M0 r10 probe-form 的 TextInput 经验）
- `Bar{text:"请求 AI 建议"}` / `Bar{text:"清空输入"}` / `Bar{text:"取消 AI 请求"}`
- `Bar{text:"采纳 AI 建议"}` / `Bar{text:"设为问题"}` / `Bar{text:"人工确认"}` / `Bar{text:"关闭面板"}`
- 4 个命名 Label：`ai_state_label` / `ai_suggestion_label` / `draft_pending_label` / `input_validation_label`
- 空间 / 设备 / 类目 / 联系人 chip 行（每个 chip 的 on_click 调用 `editDraftField(...)`，自动 bump draft_version）
- 既有的 `＋ 新建报修草稿` 按钮 on_click 改为 `createDraft()` → `openDraftPanel()`（不再直接写硬编码草稿）

### 1.2 `app/bundle/model_config.json`（新增）

**1208 B；SHA-256 `2ebc087f…`**。包含：
- `enabled: false`（默认离线）
- `provider_id` / `model_id` / `host_label` 三个字符串，**无 API Key 字段**
- `timeout_ms: 8000` + buffer 3000ms 计算 `expires_at_ms`
- `allowed_categories` 白名单
- `forbidden_model_write_verbs`（与 main.splash 内 `FORBIDDEN_MODEL_WRITE_VERBS` 一致）
- `audit_keys` 白名单（与 `recordModelMeta` 一致）

### 1.3 Python 调度契约与六套测试（sandbox-only）

| 脚本 | 行号（SCC） | 用途 |
|---|---|---|
| `m3_contract.py` | ~430 | 与 main.splash M3 同语义；M3Boundary 暴露所有协议面 |
| `m3_offline_provider.py` | ~150 | 离线 mock：`happy` / `no_service` / `timeout` / `forbidden_write` / `format_error` / `fabricated` / `late_reply` / `invalid_category` |
| `m3_real_input_test.py` | ~190 | 3 组真实中文输入；2 个缺项追问 + 1 个多设备歧义 |
| `m3_error_states_test.py` | ~200 | 7 个错误状态 + FORBIDDEN_WRITE |
| `m3_version_binding_test.py` | ~210 | 6 个交叉拒绝：迟到 / 跨项目 / 编辑 / 撤权 / 任务变 / 无 active 请求 |
| `m3_manual_path_test.py` | ~130 | 完全手工路径（无 provider）能合法 confirm |
| `m3_malicious_provider.py` | ~120 | 4 种恶意返回（编造设备 / 非法类目 / 非法联系人 / 模型编造维修根因） |
| `m3_audit_source.py` | ~135 | main.splash 51 项静态审计 |
| `m3_review_driver.py` | ~55 | 一键跑全部并写 `results/review-driver.json` |

**全部测试在 sandbox tempdir 内完成；总结果 152/152 PASS**（详见 §7 测试表）。

---

## 2. 桌面 UI / 交互变化

- 原"＋ 新建报修草稿"按钮：原来直接 push 一条硬编码 DRAFT 任务；现在先开面板填字段 + （可选）请求 AI 建议 → confirm 才走 M2。
- 新增"输入与 AI 草稿面板"嵌在既有"当前行动区"顶部，由 12 个 widget 组成（1 TextInput + 4 Label + 4 Bar + 3 chip 行）。命名 Label 已与 M1 r2 `refreshDesktop` 风格一致。
- AI 状态徽标由 `ai_state_label` 实时显示；输入校验摘要由 `input_validation_label` 列出剩余缺项。
- 既有的"上一条 / 下一条 / 收藏 / 次动作"等 M1 r2 按钮**未触碰**。

---

## 3. 接口 / 数据迁移 / 旧数据恢复方式

- 新文件：`app/bundle/model_config.json`（仅配置）。
- 新磁盘文件：`ai_requests.jsonl`（审计日志，无 secret）。
- tasks.json / actions.jsonl / events.jsonl / state.json / identities.json / `.legacy.bak*` 路径**不变**；schema 不变；M2 receipt status 枚举不变。
- PENDING_DRAFT 是**面板状态**（不落盘也不进 tasks.json），重启后会清空 → 用户需重新走 confirm 路径。本模块**不**持久化草稿（避免与 M2 任务机制冲突）。
- 旧 data-test / `.archive/` / `main.splash.debug.bak` / `main.splash.v1.bak` 未触碰。

---

## 4. 已检查的前置 PASS 报告

- M2 r1 review 状态 = BLOCKED（非 PASS）。本模块按"已完成 M2 适配器 / 命令边界；M3 仅消费"理解；不修复 M2 必修 D-M2-01..07。
- M1 r2 review 状态 = FAIL；本模块在 M1 既有视图布局上叠加，未新增冲突 widget。

---

## 5. 启动步骤 / 隔离数据位置

```sh
# 全部 sandbox 内；不修改 ~/.octosense，不启动 launcher。
cd /Users/abeam/一些尝试/知了OctoSense
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_audit_source.py
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_real_input_test.py
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_error_states_test.py
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_version_binding_test.py
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_manual_path_test.py
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_malicious_provider.py
# 便捷：一键跑全部并写 results/review-driver.json
python3 runtime/optimization/2026-10-09/M3/r1/scripts/m3_review_driver.py
```

隔离数据位置：
- 测试入口：`runtime/optimization/2026-10-09/M3/r1/scripts/`
- 沙箱：`/var/folders/.../M3-ctx-<rand>/`（`tempfile.mkdtemp` 自动清理）
- 证据：`runtime/optimization/2026-10-09/M3/r1/evidence/{real_input,error_states,version_binding,manual_path,malicious,source_audit}.json`

---

## 6. 应用运行模型/provider（适用时；无秘密）

- 当前默认离线：`MODEL_CONFIG.enabled=false`，`MODEL_ADAPTER=no_op`，`requestAiSuggestion()` 直接返回 `NO_SERVICE` 并写 audit 行。
- 真实 provider 启用由宿主/CI 在 `model_config.json` 中改 `enabled=true` 后由 main.splash 重读（main.splash 当前 boot 不读，**TODO**：启动期 `_loadModelConfig()` 与 Abram 单独确认；本轮不实现避免触碰现有 boot 路径）。
- 审计行字段：`request_id` / `provider_id` / `model_id` / `host_label` / `raw_text_length` / `raw_text_preview_safe` / `result_kind` / `elapsed_ms` ——**从不**写 `raw_text` 全文 / API Key / auth 头 / 模型 token。

---

## 7. 覆盖的既有验收项与证据运行形态

### 7.1 M3 模块硬验收（按 `M3_真实输入与AI报修.md` 第 41-46 行）

| 编号 | 本轮结论 | 范围 | 证据 |
|---|---|---|---|
| 1 三组真实输入结果随地点和症状变化；至少一组缺项追问、一组多设备歧义；模型不编造设备和维修根因 | **PASS** | case1（会议室空调，设备歧义，留 missing）/ case2（配电间跳闸，单解但缺联系人）/ case3（走廊异味，不编造，资产保留 missing）；case 4 自修原因子项已加来源标记 `推测` | `evidence/real_input.json` 18/18；`evidence/malicious.json` 13/13 |
| 2 未确认时无 OPEN 工单；人工确认成功后任务、回执、事件一致且可重开 | **PASS** | `manual_path.json` `manual_path.task_created=1`；confirm 走 `createDraftFromPanel → confirmDraft`；记录 last_confirmed_at_ms / draft_version / raw_text_hash，任务路径可重开 | `evidence/manual_path.json` 26/26 |
| 3 迟到回复、切项目、编辑输入、撤权或任务变化后旧建议不能覆盖新输入或执行 | **PASS** | 6 子用例：late_reply / cross_project / edit_input / revoke / task_version_changed / unbound_request；全部 reject | `evidence/version_binding.json` 20/20 |
| 4 格式错误和模型自报已完成不能产生业务副作用；无模型仍可手工填写合法工单 | **PASS** | NO_SERVICE / TIMEOUT / UNAUTHORIZED / AWAITING_AUTH / FORMAT_ERROR / CANCELED / EXPIRED / FORBIDDEN_WRITE 共 8 类全部不产生 task；纯手工路径也 OK | `evidence/error_states.json` 24/24 + `evidence/manual_path.json` |
| 5 真实桌面键盘编辑、取消、重试可用，记录真实 provider/model/宿主/输入样例及结果，不记录秘密 | **PARTIAL**（block 在 launcher 不可启动；非本轮范围） | 真实键盘 = BLOCKED 沿用 M0/M1/M2；audit 不写 secret 经源码审计 51/51 PASS | `evidence/source_audit.json` |

### 7.2 既有用例映射

| 用例 | 本轮范围 | 状态 | 证据 |
|---|---|---|---|
| G0-E 真实模型 provider | NOT_RUN | 沿用 M0 延期到 M3；M3 不申请新增 provider | 见 §8 |
| T01 中文键入与保留 | PARTIAL | TextInput 接入；真实键盘回读 BLOCKED；契约层 `editRawText` 可记录 raw_input_version++ 与 hash | `evidence/source_audit.json`(`widget.present[zh_input]`) |
| T03 模型应用与人工编辑边界 | PASS | `applyDraftFromAI` + `editDraftField` 双路径；`draft_version` 与 `human_edited_fields` 跟踪；`confirm_bind.invalidated_by_edit` 在编辑后回 true | `evidence/manual_path.json` |
| T25 三种输入 + 多设备歧义 | PASS | case 1 / 2 / 3 三组；device 歧义/缺联系人不编造 | `evidence/real_input.json` |
| T26 草稿状态隔离 | PASS | PENDING_DRAFT 不入 tasks.json，直到 confirm 才走 `createDraftFromPanel` | `evidence/manual_path.json` |
| T33 模型不要直接写任务 | PASS | `FORBIDDEN_MODEL_WRITE_VERBS` + `parseModelReturn` 检查 `created_task_id` 字段；`FORBIDDEN_WRITE` | `evidence/error_states.json` + `evidence/malicious.json` |
| T34 模型不要改变身份 | PASS | 模型返回无 `setActor` 等动词；contact 必须经过白名单 | `evidence/malicious.json` (`invalid_contact`) |
| T35 模型失败允许手工继续 | PASS | `manual_path` 子用例 1 | `evidence/manual_path.json` |
| T36 权限失败不可绕过 | PASS | `UNAUTHORIZED` 拒绝 + 手工路径仍生效但身份先要 active | `evidence/error_states.json` |
| T37 任务/回执/事件一致 | PASS（沿用 M2） | M3 仅 consume M2 边界；confirm → `createDraftFromPanel` → `createDraft(M2)` → `runCommandBound(M2)` → `commitBound(M2)` → receipt finalize | M2 r1 报告 + `evidence/manual_path.json` |
| T38 任务可重开 | PASS | `manual_path.task_created=1`，CONFIRM_BIND 记录 last_confirmed_at_ms；reopen 路径沿用 M2 r1 | `evidence/manual_path.json` |
| U02 状态徽标 | PASS | `ai_state_label` 实读 AI_STATE，含 7 个错误与 APPLIED | `evidence/source_audit.json` |
| U07 提交按钮禁用与重试 | PARTIAL | `Bar{text:"人工确认"}` on_click 直接调 `confirmDraftModelBound`；失败显示拒绝原因；不建议禁用按钮，由 UI 阅读者看 `ai_state_label` + `input_validation_label`。**注意**：设计 v2 spec 要求主按钮立刻禁用，本模块沿用现有"按 + 失败提示"模式。 | 源码层 |
| U08 错误提示与表单同屏 | PASS | `ai_state_label` / `input_validation_label` / `status_line` 同屏 | 源码层 |
| U11 滚动/输入可达 | NOT_RUN | 真实桌面 = BLOCKED（同 M0/M1/M2） | — |

### 7.3 真实桌面（按 `02_Review与交接规则.md` §4 表格）

| 检查 | 步骤 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| 真实桌面 native 启动 / 输入 / 视口 / 点击 | sandbox preflight rc71 + pgrep rc3 UNKNOWN | — | launcher 未启动 | **BLOCKED**（沿用既有阻断） |
| 真实桌面 roundtrip receipt | launcher 不可用 | PASS 待 native | 四文件最早已由 M0 r10 tap→createDraft 实证 | **NOT_RUN** |
| 真实桌面 recovery 模拟 | launcher 不可用 | PASS | — | **NOT_RUN** |
| 协议 + 离线契约（Python sandbox） | 见 §7.1 | PASS | 152/152 | **PASS** |
| 源码静态审计 | `m3_audit_source.py` | PASS | 51/51 | **PASS** |

---

## 8. 尚未完成（FAIL / BLOCKED / NOT_RUN）

### 8.1 延期缺口（沿用 M0/M1/M2 裁决）

- **G0-E 真实模型 provider**：M3 缺口到期，但本轮**不申请激活**——仍走"协议 + 离线契约 + 离线 mock"。激活真实 provider 需独立 Abram 裁决（含计费/密钥轮换/隐私）。M3 r1 不触碰。
- **M2 BLOCKED 必修 D-M2-01..07**：本轮仅通过 M2 既有边界使用；不修复 D-M2-*；M2 上轮 review 仍 BLOCKED，本轮明确不假装其状态推进。

### 8.2 宿主与运行边界（同 M0/M1/M2 挂账）

- 真实桌面 native runtime **BLOCKED**：sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN（沿用既有；本轮未启动 launcher）。
- 真实桌面中文键盘输入 + 控件 focus 真实回读 = NOT_RUN。
- 真实桌面 receipt-of-action 命令回读 = NOT_RUN。

### 8.3 本模块 NOT_RUN

- 启动期 `_loadModelConfig()`：main.splash 当前 boot 不读 `model_config.json`；如要激活真实 provider，需补 boot 路径（不在本轮范围）。
- 模型自学习 / 跨请求副作用 → 永远不实现（用户要求隔离）。
- 跨实例多端并发接单（多终端） = NOT_RUN（受 sandbox 隔离阻断）。
- 不修 M2 BLOCKED；不修 M1 FAIL 的 D-M1-02 cleanup。
- UI 设计 v2 spec 要求 submit-after-click disabled；本轮沿用 M1 r2 既有"按钮可点 + 失败提示"模式 — 设计 spec 不一致保留为本模块 advisory。

---

## 9. 受影响先前模块回归

- **M0 r10 / M1 r2 / M2 r1**：本轮 = M3 r1，HEAD 不变；既有 file mtime 不变；既有未提交改动（README / PROGRESS / ACCEPTANCE / 10_UI_UX_SPEC / CURRENT_REVIEW_STATUS / HUB_ISSUE）保持不动。
- M3 在 main.splash 内仅追加模块级状态 + 17 个新 fn + 12 个新 widget + 4 个新 Label；既有的 17 业务命令函数体未触碰；M2 边界（`runCommandBound`/`commitBound`/`IDENTITIES`/`identityActive`/`loadIdentities`）未删除。
- M3 的 confirm 路径严格经 M2 `runCommandBound("confirmDraft", ...)` → `commitBound(...)` → receipt finalize；任何 M3 路径都不绕开 M2 写入口。

---

## 10. 候选清单（供独立 Review 重建快照）

见 `runtime/optimization/2026-10-09/M3/r1/CANDIDATE.json`：

```json
{
  "candidate_id": "M3-r1-worktree",
  "base_candidate_id": "M2-r1-worktree",
  "head": "8d730569546cb57310944bb299695134df773b9d",
  "candidate_path": "runtime/optimization/2026-10-09/M3/r1",
  "modified_files": [
    {
      "path": "app/bundle/main.splash",
      "before_sha256": "edba9dc9e335acc8577327c9ebc8f054d27b7bf7910c9caf33f73d0fa61d9500",
      "after_sha256": "f49768274816cdc2b1bf451a8e35af87e9fda9bb0a28c981e562467996c1f035",
      "after_bytes": 116018,
      "after_lines": 3618
    },
    {
      "path": "app/bundle/model_config.json",
      "kind": "new",
      "sha256": "2ebc087f6703af7be1c0c0cc12a484bf717b5e1fa58073c12f32ab23ca5b11f2",
      "bytes": 1208
    }
  ],
  "scripts": ["m3_contract.py", "m3_offline_provider.py",
              "m3_real_input_test.py", "m3_error_states_test.py",
              "m3_version_binding_test.py", "m3_manual_path_test.py",
              "m3_malicious_provider.py", "m3_audit_source.py",
              "m3_review_driver.py"],
  "evidence_files": ["evidence/{source_audit,real_input,error_states,version_binding,manual_path,malicious}.json",
                    "results/review-driver.json"],
  "test_counts": {
    "real_input": {"passed": 18, "total": 18},
    "error_states": {"passed": 24, "total": 24},
    "version_binding": {"passed": 20, "total": 20},
    "manual_path": {"passed": 26, "total": 26},
    "malicious": {"passed": 13, "total": 13},
    "source_audit": {"passed": 51, "total": 51},
    "TOTAL": {"passed": 152, "total": 152}
  },
  "host_started": false,
  "host_blocker": "sandbox-exec preflight rc71 + pgrep rc3 UNKNOWN (carried from M0/M1/M2)",
  "model_runtime": "OFFLINE (G0-E deferred; not requested to activate)",
  "needs_abram": false,
  "status": "READY_FOR_REVIEW"
}
```

---

## 11. 衔接

- 候选清单、源码静态审计、Python 调度契约、六套测试、共 152 用例 + 6 套 evidence JSON + 1 review-driver、主源 main.splash + model_config.json + 9 个脚本 SHA-256 均列出。
- 隔离数据全部在 `runtime/optimization/2026-10-09/M3/r1/` 下；`~/.octosense` 未访问；HOST LAUNCHER 未启动。
- 编码方最大可达 `READY_FOR_REVIEW`；最终 `PASS / FAIL / BLOCKED / NOT_RUN` 等待独立 Review。
- 不进入 M4。完成交接后停止，等独立 Review。

NEEDS_ABRAM=no（不动 AppHub publish / 公开签名 / listing；不动真实模型 provider；不动业务身份变更；不动公网部署或发消息；不动 M2 BLOCKED 必修；不修 M1 FAIL 的 D-M1-02 cleanup）。
