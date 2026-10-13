# M3 实施报告 r9（修复轮）

- 模块：M3「真实输入与AI报修」；构建方 Kimi-K3；日期 2026-10-13（Asia/Shanghai）。
- 依据审查：`docs/optimization/2026-10-09-desktop/reports/M3_REVIEW_r11.md`（FAIL）。严格按审查方修改方案修必修清单，只修清单项，未发散。
- 候选：**M3-r9-worktree**（base M3-r8-worktree）；HEAD 8d730569546cb57310944bb299695134df773b9d（dirty，含他人共享改动，未覆盖/未撤销）。
- 运行对象源码：app/bundle/main.splash **657584 B / SHA256 c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421**（在 r11 受审的当前共享 244a180c 之上仅加本轮两处修复）。
- 清单：`runtime/optimization/2026-10-09/M3/r9/CANDIDATE.json`；冻结源副本 `M3/r9/source.main.splash`。

## 修复项（按原缺陷编号回写）

### D-M3-02（P1，必修）坏 view 被部分恢复后静默覆写、原来源未保全

按审查方「具体改法建议」落地（app/bundle/main.splash `loadViewState`，当前 545–626 行区域）：

1. **完整 JSON 验证**：不再只判 `m7_is_object_value(raw)`；trim 后逐字符核验首字符 `{`、末字符 `}`（`_charAtSafe`/`_textLenSafe`，宿主无 ends_with）。截断/不完整一律走损坏分支，**不并入部分字段**。
2. **独立诊断副本**：损坏时把本次全部源字节写入不覆盖既有文件的第一个空位（`state.json.boot-bak` → `state.json.corrupt-bak` → `state.json.corrupt-bak.2`），写后读回逐字相等才算保源成立。
3. **旧 bak 不冒充**：既有 boot-bak 必须与本文字节相等才计为有效备份（旧代码只要求"可读"）。
4. **冻结与出口**：备份失败保持 `_VIEW_STATE_OK=false`（saveState 拒写已有 state.json）、置 `M2_RECOVERY_NOTICE` 与可见人工出口文案；备份成立才放行以默认偏好继续并显示明确诊断。

### D-M3-05（P1，必修）恢复确认结果绕过权威消费

按审查方「具体改法建议」落地（`confirmDraftModelBound` 恢复分支与成功尾、真实按钮）：

1. 恢复分支不再"返回对象非 nil 即 return true"：与正常确认共用显式 outcome 消费——`commit_ok` / `confirmed_open` / `final_action_id` 逐项核验。
2. **unknown/needs_verify**：保留待核验、保留原意图键与原文，`AI_LAST_ERROR` 如实说明，`return false`，不显示成功。
3. **历史 final 成功**（`historical_confirmed`）：与任务当前阶段分开显示（"原确认动作已完成（action_id=…）；工单 … 当前状态=…（另读）；未重复执行"），不包装为当前 OPEN。
4. 成功文案的 task_id 只来自权威结果（恢复分支 `_rr.task_id`、正常路径 `outcome.task_id`）；正常路径成功文案移入函数内设置。
5. 真实按钮（`draft_submit_btn`）删除固定 `"✓ 已确认；OPEN 工单 = " + currentTask().id` 覆盖，只消费 `_submit_ok` 失败分支。

## 验证证据（本沙箱内实际执行）

| 项 | 结果 | 证据 |
|---|---|---|
| vendored 解析（octoscript-core m2_r7_bundle_parse） | PASS（1 passed，0 诊断） | 本轮 cargo test 输出；`M3/r9/evidence/r9_static_check.json` |
| r9 修复验证（源码断言 + 功能等价） | **30/30 PASS** | `M3/r9/scripts/m3_r9_fix_verification.py` → `M3/r9/evidence/r9_fix_verification.json`（D02 六组等价：截断+不同旧 bak/无 bak/备份位满/重复冷开/非对象/有效回归；D05 六组等价：nil/commit 失败/unknown/完整 final/历史已推进/缺 final id） |
| r8 回归脚本 | 22/23 | 唯一失败为"M3-01 helper 仍无调用方"字面断言过时——M2-r10 共享源码（7269/7860 行）已给 `_authorityHistoricalConfirm` 增加调用方，先于本轮改动存在，非本轮回归 |
| 离线签名 store（授权 A） | PREPARED；hub verify rc0；install_probe rc0；私钥已删（evidence 内 `exists_after=false`） | `M3/native/build_r9/offline-store-evidence.json`；anchor=2b75df7e0034275c4db1af10fba00c1c3e2d8b6ff406afbbfc84f49c336d10e3；digest=77b95f2eb1ecc5c97cc109e46cda7ccbb3276ac52f99b4f840cad8150d1adf6b |

## 原生验证（驱动沙箱外执行）

- 请求：`M3/native/REQUEST_build_r9.json`（4 场，needs_model=false）：
  1. `cold_root_view` 冷启动回归（零解析/运行错误、登录页渲染不回归）；
  2. `broken_view_preserve` D-M3-02 原生验证（截断 210B + 不同旧 bak 843B：核独立诊断副本逐字保全、旧 bak 不动、可见诊断）；
  3. `pending_input_restore` 有效 view 恢复回归；
  4. `untrusted_existing_draft` 权限负例回归。
- 结果：**PENDING_DRIVER**（待写入 `M3/native-runs/build_r9_REQUEST_build_r9/`）。本轮不含 ui_actions（M3_REVIEW_r11 注明本次用户明确禁止 osascript/辅助功能/自动化）。

## 未执行 / 阻塞（如实标记）

- 固定宿主无 `type:`/`key:` 输入通道（r10 host.log:40–41 实证 unknown action），且 ui_actions 本轮不可用：可信登录后真实中文键入、三组真实 MiniMax 建议、受控迟到/恶意回包、AI/手工合法确认完整链、取消/重试动态 = **NOT_RUN / BLOCKED（通道缺口）**。解阻需驱动/宿主在当前授权范围内提供有效输入/控制通道。
- 真实 MiniMax 调用本轮 0 次（历史累计 r3 Python 3 次 ≤10）；无 402/欠费。
- M2 前置仍 FAIL（M2_REVIEW_r12）挂账沿用；未修 M2/M1/M0/M4–M7 缺陷。
- D-M3-03/04/06/07 动态闭合依赖上述通道，本轮源码守卫保持。

## 交接

- GATES：M3 status 置 READY_FOR_REVIEW（编码方不给自己 PASS）；candidate_id=M3-r9-worktree，base=M3-r8-worktree，implementation_report 指本报告，evidence_root=M3/r9。review_* 字段与其他模块未动。
- ACCEPTANCE.json 未改。
- 无 publish/listing/push/issue/消息/公网部署；未读取明文凭据/provider 密钥。

NEEDS_ABRAM=no
