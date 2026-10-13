# M0 独立 Review r2 — 修复复核（原缺陷编号，新候选）

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-09 21:07 CST（Asia/Shanghai）
- candidate_id：`M0-r2-worktree`；base：`B-candidate-8d73056`；HEAD 不变（`8d73056…`）
- 性质：r1 结论为 BLOCKED（非 FAIL），r2 是实现方对 r1 报告缺陷 D1–D5 与代码缺陷 D6 的修复轮。本轮为**针对性复核**，不重开全部探针；M0 唯一剩余 blocker（宿主路线 C 用户授权）不变。
- 审查开始/结束快照一致：bundle 两文件哈希不变（main.splash `8aa1022c…7e4e3cab`，55,781B；manifest.json 维持 M0-start stamp `44743e24…`）；git status 条目与 r1 审查时相同；无 card-host 残留进程。
- 审查方独立证据：`runtime/optimization/2026-10-09/M0/review-r2/`（bundle 副本 + 隔离 app-data + boot.log），原 `app/bundle/` 未被审查运行修改。

## r1 缺陷逐条复核

| 缺陷 | 复核方式 | 结果 | 证据 |
|---|---|---|---|
| D1（P2）git log 误读来源 | 读 r2 报告 §"目标宿主" 与 D1 修复段 | **已修复**：r2 明确该树无 `.git`，来源论证改为 sha256+mtime+SOURCES.md 主张，并点名 r1 原句为误读 | M0_IMPLEMENTATION_r2.md L31、L100–105 |
| D2（P3）model"静默悬挂" | 读 r2 更正段 | **已修复**：改为显式两级 `is_ok=false` 错误语义 | r2 报告 §D2、能力矩阵表 |
| D3（P3）滚动不可测 | 读 r2 更正段 | **已修复**：`/m?k=scroll` 可用、ScrollYView 真实滚动已写入 | r2 报告 §D3 |
| D4（P3）fs.write 静默吞掉 | 读 r2 更正段 | **已修复**：改为 trap+部分写入风险表述 | r2 报告 §D4 |
| D5（P2）硬验收3 探针缺失 | 读 r2 更正段 | **已修复**：审查方 DesignInput 中文 round-trip 证据已并入，结论回到"能力 PASS / 业务表单属 M1/M3" | r2 报告 L114–118 |
| D6（P1）重复 `fn isReporter` | 静态+运行双重复核 | **已修复**：现仅 line 113 一个 `fn isReporter(t,u)`；line 1020 改为 `fn isReporterMe(t)`，4 个 v2-helper 调用点（1050/1116/1124/1148）同步；15 处 2-arg 守卫调用保持原状。审查方独立启动 r2 bundle 副本：`eval: 55781 bytes` 无 trap；新建草稿→提交 OPEN（走 2-arg 守卫 line 433）落盘成功；`next_step_title`/`visible_count` 等命名 Label（走 isReporterMe 路径）正常重算 | `review-r2/logs/boot.log`、隔离 app-data tasks.json、grep 输出 |

## r2 新增主张抽查（route C 依据，仅只读核对）

- `crates/ai-host/src/lib.rs` 确有 `octosense_llm_service::register_model(...)`（实测在 :333，报告写 :328，行号微差不影响结论）— **属实**。
- `crates/ai-host/src/contained.rs` 确有 `CONSENT: OnceLock<fn(&str)->bool>` 与首次同意语义（:42–50，报告写 :38–44）— **属实**。
- `octos.turn.start` 服务名存在于 ai-host 测试（contained/tests.rs:188 等）— **属实**。
- "Shell 无现成 OS-level scheduler/notification"：全文 grep 仅命中 kernel 协议内部的 JSON-RPC notification，非 OS 级用户提醒 — **属实**，M6 提醒仍需第三方路径。
- 未构建、未联网：`runtime/native-build/OctoSense-Shell/` 仍无 `target/`、无 `.sources/`；git status 无新增构建产物 — **硬限定遵守确认**。

## 判定

- 最终结论：**BLOCKED**（维持；性质从"报告缺陷+路线未决"收敛为"仅剩路线未决"）
- 本次结论的精确范围：r2 修复轮复核；不构成对 B 包、后端台账或后续模块的判定。
- 已解：D1–D6 全部关闭。硬验收 1–4 维持 r1 的 PASS 记录（#3 能力证据已入册）。
- 唯一剩余 blocker（解阻条件）：**用户书面授权路线 C**（联网拉取 + 离线构建 OctoSense-Shell@a5d847a，构建后补源码 SHA/lockfile/二进制哈希/启动方法并重交 M0 审查）。若用户不授权 C，按实现方结论 M0 永久 BLOCKED——card-host 路线结构性无法支撑 M2/M3/M6 硬验收，本审查方独立确认该判断成立。
- 受影响先前模块复验：无前置模块；`docs/build-loop/ACCEPTANCE.json` 不改动，历史来源保留。
- 门禁更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（status=BLOCKED，review_report 指向本文件，reviewed_at 更新）。
- 是否允许进入下一模块：**否**。
