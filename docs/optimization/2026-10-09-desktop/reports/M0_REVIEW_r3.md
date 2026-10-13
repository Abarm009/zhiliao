# M0 独立 Review r3 — 官方发行包验证轮复核

- 审查者 / 日期：独立 Review 会话（Kimi Code CLI），2026-10-09 22:05 CST（Asia/Shanghai）
- candidate_id：`M0-r3-worktree`；base：`B-candidate-8d73056`；HEAD 不变（`8d73056…`）
- 性质：r3 为官方发行包（desktop-v0.1.0-rc.1）可行性验证轮。本轮复核其证据真实性、隔离边界与结论正确性。
- 审查方独立证据：本轮以复算哈希、重读日志原文、宿主源码对照为主，未重新下载、未重复启动官方 launcher（其证据链完整且可逐条核对；重跑价值低）。

## 现场与隔离核查

- `app/bundle/main.splash` sha256 `8aa1022c…7e4e3cab`（55,781B）与 r2 一致 ✅
- `app/bundle/manifest.json` stamp `46f100dc…`（r2 复打后保持）✅；git status 仍 17 项，无新增仓库内改动 ✅
- `runtime/optimization/2026-10-09/M0/{r1,r2,review-r1,review-r2}/` 目录存在且未被 r3 产物覆盖 ✅
- `runtime/optimization/2026-10-09/M0/r3/host/app-data/` 为空目录 ✅（launcher 未加载业务 bundle，与"加载失败"结论自洽）
- `~/.octosense/{apps,logs,octos-home,secrets,wm}` 确为官方 launcher 于本日 21:38–21:50 自建的宿主管理目录，属 launcher 自管数据，不违反业务隔离要求；记录在案。

## r3 关键主张逐条独立复核

| # | 主张 | 复核方式 | 结果 |
|---|---|---|---|
| 1 | 发行包逐字节校验通过 | 复算 `network/` 三件本机 sha256 并对照官方 `SHA256SUMS` | ✅ `ac1ab668…` / `9fb11761…` / `38bd755b…` 三项逐一吻合；SHA256SUMS 还列出 dmg/deb/exe/AppImage 等未下载件（只下载了 macOS 所需三件，合理） |
| 2 | 来源为官方 | 读 `network/network-probes.log` 与 `rc1-release.json` | ✅ 全部 URL 指向官方 `github.com/OctoSense-org/OctoSense`，tag `desktop-v0.1.0-rc.1`，commit `933abbcf…`。注意：provenance 自述 macOS 件为 "manual fallback: local macOS" 装配（非 CI 产物），来源可信度属"官方账号发布的手工装配包"，已如实记录 |
| 3 | launcher 启动后 5 项服务注册 | 重读 `run-notes-app.log` 原文 | ✅ 五行日志逐字存在：kernel ready / llm profile 路径 / `model: service registered` / contained apps (Consent) / modules linked（含 reminders） |
| 4 | catalog schema 拒收 splash bundle | 重读 `run-apps.log` / `run-source-field.log` / `run-mf-file.log` / `run-testapp.log` 原文 | ✅ 报错原文逐字存在（unknown field 'kind' / unknown source / manifest-path must be Cargo.toml / build failed exit 101）——**但该结论的适用范围被过度推广，见缺陷 D8** |
| 5 | consent sheet 真实 | 查看 `notes-cjk-typed.png`（2.8MB 原图） | ✅ 真实桌面窗口截图：Notes 模块 + "Let Notes's agent start?" 首次同意面板（列明 octos.session.open/turn.start 等工具与 Allow/Don't allow） |
| 6 | CJK 输入/滚动能力 | 截图 + `notes-after-typed.json` | ✅ TextInput/PortalList/NotesTap 存在且 enabled；PingFang SC 字体加载日志存在 |
| 7 | 模型 BLOCKED（profile 未配置） | `run-dev.log:51-53` 原文 | ✅ `profile '_main' is not configured` + 全部内置 agent `profile_unresolved` 逐字存在；未伪造模型调用 |
| 8 | 业务文件零变更 | 复算哈希 + git status | ✅（manifest 变化发生在 r2 而非 r3，见 D9） |

## 缺陷

- **D7（P1，必需修复·映射错位）** — 文件：`reports/M0_IMPLEMENTATION_r3.md` §"r3 测试表"（L237–250）。触发：对照 `docs/implementation/05_IMPLEMENTATION_ACCEPTANCE.md` L82–86 与 `10_UI_UX_SPEC.md` L181/183。预期：既有条目的语义按原定义引用。实际：测试表整体标签错位——T28 实为"原生宿主同一 task_id 回读/重开保留"（被标为"中文原生表单"且记 PASS）；T29 实为"grant 关闭/退出/到期"（被标为"多端一致"）；T32 实为"配对码/token"（被标为"共享任务"）；U09 实为"1280×800 布局无裁切"（被标为"滚动可达"且记 PASS）；U11 实为"真实宿主滚动/输入/面板稳定"（被标为"AI 报修"）；P02 实为"完整源码+依赖+启动说明"（被标为"提醒恢复"）；G0-B/C/F 标签同样偏离原义。影响：把 CJK/滚动能力证据错挂到语义不符的既有条目上，造成"既有验收项已被推进"的假象；按原定义，业务 bundle 未在官方 launcher 加载时，T28/U09 在该宿主下只能记 NOT_RUN/BLOCKED。最小修复：按原定义重写测试表条目名与状态（能力证据可保留，但只能标为宿主能力事实，不得占用既有条目编号）。
- **D8（P1，必需修复·路线结论错误）** — 文件：同上 §"官方 launcher 加载失败证据"结论与 §"提交给独立 Review 的关键问题"。触发：对照宿主源码 `OctoSense-Shell/crates/shell/src/octosense/catalog.rs:1–110`、`OctoSense-App-Hub/crates/app-hub/src/client.rs:202–230`、`crates/shell/src/apps.rs:186–198`。预期：路线分析区分两条加载路径。实际：r3 把"dev 注册表 apps.json 拒收 splash bundle"推广为"第三方 splash bundle 在当前 launcher 下不可加载、AppHub 流最终也强制 Cargo crate 形态"。源码事实相反：① apps.json 是 dev 客户端注册表，`source` 只接受 `makepad`、`manifest` 指向 Cargo.toml 是**该注册表内进程应用**的协议；② AppHub 安装路径（`install_staged` → `<root>/<app_id>/bundle/`）接收的正是 manifest.json+main.splash 的 **splash bundle 原形态**，由 launcher 内 `card` 模块进程内托管——与 card-host 同一运行时，且与 ai-host 的 model/consent/kernel 服务**同进程**；③ catalog 还有 `executable` 字段（直接二进制路径）r3 未尝试。影响：选项 (a) 中"cargo crate 形态加载"的描述错误，选项 (b)"重写为 Cargo crate"建立在该错误之上、实非必要；用户若按 r3 的路线描述裁决会被误导。最小修复：重写路线分析——真正的开放问题是"是否有本地 catalog/免公网 publish 的安装路径"（`app-hub/src/remote.rs` 目前只见远端 base URL 取 catalog；未查是否有本地目录/文件源），以及 publish 授权；而非"Cargo crate 形态"。
- **D9（P2，必需修复·审查方自纠）** — 我的 `M0_REVIEW_r2.md` 写"manifest.json 维持 M0-start stamp `44743e24…`"。实际：实现方 r2 的 host-stage 用 `--stamp` 对**真实** `app/bundle/manifest.json` 复打为 `46f100dc…`（r2 boot.log L8 为证），我 r2 复核时只重算了 main.splash、漏算 manifest。处理：本条即更正；r2 复打行为本身属"为启动阻断作有证据的最小修复"边界内（digest 46f100dc 与 D6 后 bundle 内容自洽），但 r1 遗留的"stamp 与 digest 不一致"blocker 自此已实质解除，GATES.json 该条 blocker 可关闭。

无需变更的发现不编造缺陷：r3 的下载校验、服务注册、加载失败原文、consent 截图、模型 BLOCKED、隔离边界均经独立复核属实。

## 判定

- 最终结论：**BLOCKED**（维持）
- 本次结论的精确范围：r3 官方发行包验证轮的证据真实性与结论正确性；不构成对 B 包、后端台账或后续模块的判定。
- 必修项（重交前完成）：
  1. 修复 D7：测试表按既有条目原定义重写，能力证据与条目编号脱钩。
  2. 修复 D8：路线分析按"dev 注册表 vs AppHub 安装（splash bundle 原形态、card 模块进程内、同进程 ai-host 服务）"重写；补查本地 catalog/免公网安装的可行性后再向用户呈现路线选项。
  3. GATES.json 关闭"manifest stamp 与 digest 不一致"条目（D9 已证其解除）。
- 阻塞与未测项（维持）：业务 splash bundle 在官方 launcher 内未加载；真实模型调用（`_main` profile 未配置，待用户授权 provider）；OS 级通知（launcher 内置 toast ≠ UNUserNotificationCenter，未实测）；reminders 模块端到端（未拉起）；本地安装路径可行性（未查）。
- 路线裁决（更新后提交用户，替代 r3 的四选项）：核心问题收敛为——**是否授权 AppHub publish 流程（联网+签名+listing），或是否存在本地安装路径**；若走通，官方 launcher 即同进程提供 model/consent/kernel，r1/r2 的模型/身份缺口随之消解；"重写为 Cargo crate"不成立，应从选项中删除。
- 受影响先前模块复验：无前置模块；`docs/build-loop/ACCEPTANCE.json` 不改动。
- 门禁更新位置：`docs/optimization/2026-10-09-desktop/GATES.json` M0 条目（review_report 指向本文件，reviewed_at 更新，status 维持 BLOCKED）。
- 是否允许进入下一模块：**否**。
