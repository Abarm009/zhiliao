# 知了基线（ZHILIAO_BASELINE）

> 来源：Abram 2026-10-09 晚的语音和聊天交代，由知了整理。更新时间：2026-10-10 13:56（北京时间）。  
> 硬性规则：基线每次都必须单独落成一份文件，不能只靠 WORKFLOW_RULES.md 或知了自己的记忆。规则有变化就同步更新本文件。

## 1. 职责与边界

- 知了专门负责知了OctoSense 项目（`/Users/abeam/一些尝试/知了OctoSense`）。
- 驱动脚本：`runtime/optimization/2026-10-09/driver/run.py`；进度看 `driver/driver.log` 和 `docs/optimization/2026-10-09-desktop/GATES.json`。
- 只动这个文件夹；不 publish、不 git push、不改 provider 和 CC Switch、不碰其他项目；每个模块最多 3 轮。

## 2. 沟通

- Abram 只跟知了沟通，不直接跟 Codex、Kimi、MiniMax 沟通。
- Abram 的 Mac 会一直在线，有问题就在聊天里找他。
- 模型断掉时，按 Abram 定的规则处理，处理结果同时写进知了的记忆和聊天。

## 3. 分工

- **MiniMax 是唯一写代码的一方。** 在 CC Switch 里它现在叫「MiniMax m3」，所以 `claude-minimax` 脚本找不到它。脚本直接调用 `claude`，开建前先确认 CC Switch 当前的 claude 供应商是 MiniMax，不是就停；CC Switch 本身不改。
- **Kimi 是第一核查人**，调用方式是 `kimi -p`（不能加 `--auto` 或 `-y`，否则会报错）。Kimi 只给建议，而且要极尽详细：缺陷编号、文件和行号、证据、根因、具体改法、改完后怎么验证。MiniMax 必须严格照改。
- **Codex 只做 review**，固定用 `gpt-6.1-sol`（high 档），不用 Astra（Mac 上 Codex 的默认模型是 `gpt-6-astra`，必须显式指定 gpt-6.1-sol）。Codex 只在两种情况下出场：
  1. Kimi 判 PASS 之后做终检；
  2. 连续 3 轮没过时介入，给出修改意见，MiniMax 再按意见改一轮。
- gpt-6.1-sol 介入后再改一轮还不过，就停下来等 Abram。
- **测试启动宿主的规矩**：MiniMax 测试时启动 OctoSense 宿主启动器（launcher，路径 `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/OctoSense.app`），这是 M0 预期内的测试动作。但必须在后台启动，测完立刻关闭；禁止用 `--help` 参数探测，因为 `--help` 会弹出窗口，而不是打印帮助后退出，进程会卡住并占着桌面。Abram 报告 2026-10-09 已经弹出了四个窗口，MiniMax 的测试方式需要改进。
- 工具一启动就报错时直接停，不算作一轮，不空烧轮次。
- 在 Mac 上启动循环必须完全脱离当前终端会话（双 fork 加 setsid），只用 nohup 会随着会话结束被一起杀掉。

## 4. 决策权限

- 必须 Abram 同意的只有三件事：AppHub publish（要联网、签名、上架）、配置真实模型 provider、确定业务身份来源。
- **Abram 2026-10-10 03:02 授权（方案 A）**：允许在 `runtime/optimization/2026-10-09/` 下的隔离测试目录生成离线签名 catalog，只对当前 bundle digest 有效、只在 sandbox 内有效；不联网、不上传、不 publish、不上架；测完删除私钥，并在报告里留下删除证据。AppHub 公开发布和签名上架仍然必须 Abram 同意。
- **Abram 2026-10-10 06:55 裁决**：业务身份来源（G0-B / 可信双主体）和真实模型 provider（G0-E）作为他认可的已知延期缺口，延后到 M2/M3 再定，不阻塞 M0，循环继续跑。
- 其他事情知了可以站在普通用户的角度自己判断、往下推进。
- 知了是编排者：看到 MiniMax 做坏了，可以跳过 Kimi，直接打回重改；尽量不插手执行细节。

## 0. 最新决定（覆盖下文中冲突的部分）
- **13:53 主审换人**：主审改为 Codex `gpt-6.1-sol`（high 档），Kimi 退出审核；MiniMax 仍然是唯一写代码的一方。由 gpt-6.1-sol 审查通过（返回码为 0、有报告、状态 PASS）就算放行，不再单独做终检。
- **13:54 完成比完美重要**：目标是 M0 到 M7 全部跑完。审查只把真正阻断核心功能或违反安全、隔离约束的问题列为必修，其余列为建议并挂账。每个模块最多 2 轮（M0 允许在 gpt-6.1-sol 介入后再修最后一轮），还没过就把缺陷记进 `driver/CARRYOVER.md`，然后进入下一个模块，不停机。需要 Abram 授权的事也改为记进 CARRYOVER，不停机。
- 修复时限：构建 35 分钟，审查 25 分钟。

## 5. 当前状态（2026-10-10 11:36）
- **驱动脚本已换成 v2：`driver/run2.py`**（旧版 `run.py` 保留，并备份为 `run.py.bak-v1-1135`）。Abram 11:32 同意。v2 的改动：
  - 放行前要同时满足：返回码为 0、本轮报告已生成、状态为 PASS；Kimi 审和 gpt-6.1-sol 终检都要通过；按 depends_on 校验前置模块。
  - 身份来源的延期到 M2 失效，模型 provider 的延期到 M3 失效。
  - 硬超时：构建 40 分钟，审查 25 分钟，终检 25 分钟；每 5 分钟写一次心跳；超时就清掉整个进程组。
  - 轮次保存在 `driver/state.json`，重启后接着数；每一步结束后自动清掉残留的启动器。
  - 修复轮只读 Kimi 的清单和 `CONTEXT_Mx.md`；用 `caffeinate` 防止 Mac 休眠；claude 和 kimi 的日志改为流式输出。
- 启动方式：在 driver 目录下按 05 文档的双 fork 方式运行 `['caffeinate','-dimsu','python3','run2.py']`；可选环境变量 `ADOPT_PID`/`ADOPT_LOG`（接管一个正在跑的构建）和 `SKIP_FIRST_BUILD=Mx`。
- 目标（Abram 11:32）：约 7 小时内（到 18:30 左右）跑到 M4。
- 10:55 Kimi 审 r7，结论 FAIL（`M0_REVIEW_r6.md`）：r5 的五条已经闭合；新增 D-R6-1（业务工作台从没在宿主里跑起来过）和 D-R6-2（中文表单没有原生证据）。11:14 MiniMax 开始第 2 轮修复；11:33 由 v2 接管。

### 更早（2026-10-10 10:56）
- 03:51 M0 r7 构建完成后，因身份来源和模型 provider 两项需要 Abram 授权而停下；06:55 Abram 裁决先挂起；Mac 在 05:00 到 10:55 之间断连；10:56 按裁决重启，首轮跳过构建，直接由 Kimi 审 r7。

### 更早（2026-10-10 03:04）
- 23:14 M0 r5 构建完成：隔离宿主已能真实启动，GATES 中 M0 为 READY_FOR_REVIEW；因本地 install_staged 需要签名 catalog，循环停下等待 Abram。03:02 Abram 选择方案 A，03:04 重启循环。

### 更早的状态（2026-10-09 22:57）

- 22:39 按新规则重启，但那个进程在 22:56 之前悄悄退出了，没有产出；22:56 已改成完全脱离的方式重新启动（父进程为 1），MiniMax 正在做 M0 的修复轮。M0 原来的卡点是本地可信 catalog，可能需要 Abram 裁决。
- 原来的脚本备份为 `run.py.bak-codexbuild` 和 `run.py.bak-2238`；第一次启动失败时空跑留下的日志放在 `driver/failed-2237/`。
- 知了每小时的 :12、:32、:52 只读巡检一次，有实质变化才在聊天里汇报。

## 相关文件

- 工作流规则：`docs/optimization/2026-10-09-desktop/WORKFLOW_RULES.md`

## 2026-10-11 07:05 更新（北京时间）
- Abram 2026-10-10 23:04–23:07 语音裁决，两个授权缺口关闭：业务身份来源 = 5 个真实账号（gpt-6.1-sol 当次授权实现，23:33 完成，数据在 runtime/identity/，明文凭据只在 CREDENTIALS_FOR_ABRAM.md，权限 600）；真实模型 provider = MiniMax（配置 app/bundle/model_config.json，密钥 runtime/secrets/minimax_provider.env）。
- MiniMax 余额不足、欠费或额度用完时，立刻在聊天里叫 Abram，不重试硬跑。
- 07:04 起 run2.py 从 M2 开始重跑到 M7（state 已重置，备份为 state.json.bak-20261011 和 run2.py.bak-20261011），NEEDS_ABRAM 只剩 MiniMax 余额这一项。
- 教训：10-10 夜里 Abram 锁屏后 Mac 睡眠，local-exec 断连，巡检又被暂停，导致 M2 重跑没能接上。以后启动长任务都要套 caffeinate，巡检保持开着。

## 2026-10-11 harness 更新（Abram 12:12 裁决）

- 根因：以前每个模块的原生桌面验证都被标为 BLOCKED，是因为审查方运行在 `codex exec --sandbox workspace-write` 的 Seatbelt 沙箱里：沙箱里不能再套一层 sandbox-exec（rc71），也拿不到进程列表（pgrep rc3）。这不是宿主或 Mac 本身的问题。详见 reports/NATIVE_TEST_ENV_PLAN_2026-10-11.md。
- 新增 `runtime/optimization/2026-10-09/driver/harness/`：
  - native_harness.py：由驱动在沙箱外执行。它为每个场景新建隔离目录，并用 Seatbelt 限制宿主：写入只能落在该目录；禁止读取 runtime/secrets、runtime/identity/CREDENTIALS_FOR_ABRAM.md、~/.codex、~/.cc-switch、~/.ssh；对外连接只放行本机控制口和 MiniMax 代理。宿主在后台启动，按 /quit → TERM → KILL 的顺序回收它自己的进程组，并在启动前后用 pgrep 清点；同时产出 result.json、截图、sandbox 拒绝日志和 MANIFEST.sha256。
  - minimax_proxy.py：只监听 127.0.0.1，只转发到 api.minimax.cn:443。密钥由代理从 runtime/secrets 读取后注入请求，宿主只拿到占位符；单次最多 10 个请求；一旦遇到 402 或余额不足就立即停止。代理只在 needs_model 场景中启动，用完即关。
  - profile.sb.tmpl（沙箱配置模板）、request.schema.json（请求格式定义）。
- run2.py 改为 v3（备份为 run2.py.bak-harness）：
  - 新增 native_phase：构建和审查结束后，驱动在沙箱外执行 harness 请求，结果记入 state.json。
  - 审查改为两段式：第 1 段写自选场景的 harness 请求，驱动执行后，第 2 段用 `codex exec resume <session>` 读取证据并定稿。
  - cleanup_launchers 去掉了全局 `pkill -f`，改为只回收 harness 登记过的进程组。
  - run() 和启动时都会检查驱动本身不在沙箱里。
  - 提示词第 14、23 条以及审查 prompt 改为要求构建方和审查方通过 harness 做原生验证。
  - 新增 SKIP_FIRST_BUILD_ALL=1：每个模块第 1 轮跳过构建，直接用当前代码走两段式重审。
  - 为规避 Python 3.9 处理超长中文行的 tokenizer bug，文件头加了 `# -*- coding: utf-8 -*-`。
- 自测（2026-10-11 13:07）：
  - harness 空场景结果为 CLEAN：profile 探针全部通过（项目外写入被拒、5 个黑名单路径的读取被拒）；10.6 s 后经 /quit 退出；进程组残留 0，pgrep 结果为 NONE；~/.octosense 未被改动；~/Library 无新增文件。
  - 经代理向 MiniMax 发了 1 次最小请求：HTTP 200，回复 "pong"，没有计费错误；产出文件中没有出现密钥。
- 未改业务代码 app/bundle/main.splash（业务代码只由 MiniMax 修改）。注意：bundle 目前直连 model_config.json 里的 api.minimax.cn 地址，这在 harness 沙箱里会被拦截。需要由 MiniMax 让 bundle 在环境变量 OCTOSENSE_MODEL_ENDPOINT 存在时改用它，并接受 MM_KEY 占位符。
- 13:09 起以 SKIP_FIRST_BUILD_ALL=1 重审 M2–M7；state 备份为 state.json.bak-harness，CARRYOVER 新增小节「2026-10-11 harness 重审」。
- 文件指纹：
  - `runtime/optimization/2026-10-09/driver/run2.py` SHA-256 `6ac1072b17e21463955714350bbb33c43946608576cfcc3712022764e947d999`
  - `runtime/optimization/2026-10-09/driver/harness/native_harness.py` SHA-256 `12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9`
  - `runtime/optimization/2026-10-09/driver/harness/minimax_proxy.py` SHA-256 `2fdfa29ff66145114f7744d70e7758adfd99744a0c4cfe11bb2577f125c22f2b`
  - `runtime/optimization/2026-10-09/driver/harness/profile.sb.tmpl` SHA-256 `80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7`
  - `runtime/optimization/2026-10-09/driver/harness/request.schema.json` SHA-256 `dd73a650796273e91755bb17ecd002fabcb276fbfbde430e6b092b300bc70076`

## 2026-10-11 21:05 更新（北京时间）
- Abram 21:03：比赛方提供了 Kimi 会员，写代码改由 Kimi-K3（kimi -m kimi-code/k3 -p，非交互模式下能自动改文件、跑命令），MiniMax 停止写代码。审核仍由 gpt-6.1-sol 负责，要求加快。业务内的真实模型 provider 仍然是 MiniMax，这件事没变。
- run2.py 的 build() 已改用 Kimi-K3，备份为 run2.py.bak-kimi 和 state.json.bak-kimi。COMMON 里加了最高优先的一条：先把宿主解析错误清零、让界面真正渲染出来。M2–M7 重置后从 M2 重跑（第 1 轮不跳过构建），启动脚本是 relaunch_kimi.py，驱动 PID 56915。
- 11-10 晚 harness 重审结果：M2–M7 全部 FAIL，共同阻断是解析错误导致业务区空白（M7 时还剩每场 3 条）。
- 2026-10-12 11:50 Abram 授权辅助功能和自动化权限，harness 已支持真实键鼠输入。

## 2026-10-12 晚间变更摘要（Grok Bot，19:57–21:46）
- **驱动 / M7**：state.json 备份为 state.json.bak-20261012-1958，并把 M7.skip_used 复位为 false。用 SKIP_FIRST_BUILD=M7 重启 run2.py M7（PID 93891，ppid=1），第 2 轮没有重新构建，直接审查。审查期间 native 8 个场景都 CLEAN。结论 FAIL，已挂账，报告是 docs/optimization/2026-10-09-desktop/reports/M7_REVIEW_r10.md（B-M7-01 解析错误回归 17 条，R-M7-02 合法加载被误拒、恢复保护不成立；R-M7-03 已关闭）。驱动 20:24 写出 ALL DONE。run2.py 没有改动。
- **harness**（driver/harness/native_harness.py，备份为 .bak-quote-batch-20261012；request.schema.json 也有同名备份）：render_profile 只放行内部用整数端口生成的代理规则，RUN_DIR、ROOT、HOME 这些路径仍然拒绝双引号、反斜杠和换行；场景超过 8 个时按每批 8 个串行分批跑（summary.batches），上限 32 个，id 不能重复。自测都在 fix-selftest-20261012/：selftest、needs_model+代理端口（0 次真实请求）、9 个场景分 2 批，三项都 CLEAN；带引号的路径仍报 unsafe path。
- **UI**（ui-redesign-20261012/，改前完整备份在 bundle-before/）：
  - 第 0 批：sol 把通用 parser 的返回字段 ok 改名为 success，共 8 行，解析错误从 17 降到 0。
  - 第 1 批：令牌、基础控件、按钮层级与分组。
  - 第 2 批：矮屏滚动布局，加固定的详情底部主操作。
  - 外部补丁：去掉口令框的 is_password，因为宿主会显示 "Apps can't ask for passwords" 并拒绝输入；恢复四个按钮文案里的「恢复」前缀；顶栏高度从 56 改到 64。
  - 最终版本：app/bundle 与 snap-batch2c 一致，main.splash sha256 ef05b62f…
- **验证**：verify/b2final-2143 冷启动 1280×800 和 1280×616 都是 CLEAN，parser 0，没有其他 [E]。ui_actions 真实点击和输入：账号、口令都能读到文字，登录按钮点击后执行了回调。登录后的两条 [E]（script instruction limit exceeded @KDF，以及 list_pick_ids not found）在改前的 snap-batch0 上完全一样（verify/b0c-2142），是原有缺陷，不是这次引入的。因为 KDF 超过指令上限，登录后的会话建立不起来，所以登录后的任务列表、详情和报修表单没能实测；报修输入框（zh_input）的真实输入也没测到。
- **演示**：runtime/optimization/2026-10-09/demo-ui-20261012/launch_demo.py，使用新版 bundle 的离线签名本地 mirror（密钥已删除），到 22:45 自动回收。关闭命令：python3 launch_demo.py stop

## 2026-10-12 21:46–23:45 登录修复 + 按 Apple HIG 重做界面（Grok Bot）
- **模型**：登录修复用 gpt-6.1-sol（high）。界面设计和实现按 Abram 21:47 的指示改用 gpt-6-astra（high），共 3 轮；第一次让 sol 同时做登录和界面的那轮还没改文件就停掉了。
- **登录**：原来在一次求值里同步跑完 PBKDF2 的 4096 轮，超出脚本指令上限。改成每 10 ms tick 推进一轮，单次求值最多约 9.5 万条指令，离上限还有约 53% 余量；算法、迭代次数和 accounts.json 格式都没变，真实账号的哈希也没动。补上了 STATE.list_pick_ids 的初始值。用隔离目录里新造的测试账号实测：真实输入后约 45 秒登录成功。报告：ui-redesign-20261012/LOGIN_FIX_r1.md。
- **界面**：做了独立居中的登录卡片；登录后顶栏左侧只写一次「知了·维修协作」，右侧显示用户名·角色和退出；主体改成 macOS 风格三栏（侧栏导航+筛选、任务列表、详情加页签选中指示）；浅色中性底，唯一强调色 #007AFF；详情和报修的主按钮固定在底部；报修改成独立页面。去掉了工程字样和占位文案。口令框不能用 is_password：宿主会显示 "Apps can't ask for passwords" 并拒收输入，所以用普通输入框。报告：APPLE_DESIGN_astra.md、APPLE_IMPL_astra_r1/r2/r3.md。
- **验证**：verify/ar3-2337，parser 0，[E] 0，tick 异常 0，没有新增控件查找错误。改前备份在 snap-before-apple/。
- **遗留**：顶栏角色前多一个「·」；详情卡标题「确认并提交报修」和底部按钮重复；地点、设备为空时显示「（未选）」和「设备：」；报修页滚动区最后一行仍被固定操作区盖住半行；分页写成「首页 无下一页 仅一页」，太啰嗦；harness 的 size 参数改不了应用窗口内容区（实际约 990×603），1280×616 和 1280×800 两种尺寸没能分别实测；Abram 的真实账号没有测（不读明文凭据）。
- **演示**：runtime/optimization/2026-10-09/demo-apple-20261012/，保留 90 分钟，关闭用 python3 launch_demo.py stop。

## 2026-10-13 收尾
- 驱动 08:39 ALL DONE。M2–M7 均为 FAIL 挂账；M2、M5 已用修好的夹具补审（r13，仍为 FAIL）。硬缺陷清单见 driver/CARRYOVER.md 的 10:40 汇总。
- 夹具：harness 会自动补齐缺失的 apps/catalog.json，宿主拒绝打开 app 时会标出来（R-M2-TEST-01）。
- 界面：astra r5 修好了「设备与预约」的空字段（改为显示「尚未选择设备」等）。bundle 快照 snap-astra-r5。
- 验证 verify/v3final5：3 个场景都 CLEAN，解析错误为 0；真实输入登录 u-reporter-1、打开详情、新建报修并输入中文都通过。v3 截图 4 张。
- 演示：demo-v3-20261013，10:36 开始，12:06 自动停止。

## 2026-10-13 12:40 run2.py 最小改动
- 改动：`T_BUILD=int(os.environ.get("T_BUILD_MIN","35"))*60`，默认值不变。
- 理由：Kimi 服务端慢，导致构建连续 35 分钟超时；新驱动用 T_BUILD_MIN=60 启动。
- 时机和备份：在驱动停下之后才改；备份为 run2.py.bak-tbuild-*。

## 2026-10-13 13:14
- 【Abram 2026-10-13 13:14 硬规则：不扩展功能，把已有的做实】禁止新增功能、新入口、新页面、新字段。只允许两件事：把已有功能修到真正可用、可靠；关闭已列出的硬缺陷。审查方：发现新增功能或入口，直接列为缺陷（P1），并要求回退；不许提新功能建议，只核对已有内容是否做实。
- 2026-10-13 16:4x（Abram 16:45 批准）：native_harness.py 默认宿主 BIN 由 M0/r3 rc.1 改为 host-rc6/app-extracted/OctoSense.app（rc.6，kernel sha256 3bb242ac…，见 host-rc6/sha256.txt）；备份 native_harness.py.bak-rc6-1646。
