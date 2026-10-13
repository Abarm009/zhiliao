# 原生桌面测试环境方案（NATIVE_TEST_ENV_PLAN，2026-10-11）

> 性质：只做调查和方案。本次没有改任何项目文件，没有改 run2.py、CC Switch、~/.codex，没有重启循环，也没有联网发布。
> 本次只新建了两处：本文件，以及实验目录 `runtime/optimization/2026-10-09/env-probe/`。
> 时间均为 Asia/Shanghai（CST, UTC+8）。

## 1. 结论（一句话）

rc71 和 rc3 都是 **Codex CLI 自身的 Seatbelt 沙箱**造成的，与 Mac、宿主或权限设置无关：审查用的 `codex exec --sandbox workspace-write` 会把审查方的所有命令放进 Seatbelt。macOS 不允许已在沙箱里的进程再调用 `sandbox_apply`，所以嵌套 `sandbox-exec` 一律 rc71。Codex 的基础策略又禁止 mach-lookup 到 `com.apple.sysmond`，并且只允许查看同一沙箱内的 process-info，所以 `pgrep` 一律 rc3。同一台机器在沙箱外跑这两条命令都正常；用沙箱外驱动的方式启动和回收宿主，已实测可行。

## 2. 根因调查与证据

### 2.1 普通 shell（不在 Codex 沙箱里，2026-10-11 11:3x）

| 命令 | 结果 |
|---|---|
| `sandbox-exec -p '(version 1)(allow default)' /usr/bin/true` | **rc=0** |
| `pgrep -l launchd` | rc=1（无输出）。原因是 macOS 的 pgrep **默认排除自身及所有祖先进程**，launchd（PID 1）就是祖先。这不是权限问题。 |
| `pgrep -a -l -x launchd` | **rc=0**，`1 launchd` |
| `pgrep -l codex` | rc=0（能列出进程） |

### 2.2 在 Codex 沙箱里复现（`codex sandbox -P <内置 profile> -- …`，codex-cli 0.162.0-alpha.17.2，macOS 26.6.2）

| profile | 嵌套 sandbox-exec | pgrep | 其他 |
|---|---|---|---|
| `:workspace`（即 workspace-write） | **rc=71** `sandbox_apply: Operation not permitted` | **rc=3** `sysmon request failed with error: sysmond service not found` / `pgrep: Cannot get process list` | `/bin/ps` 也 `Operation not permitted` |
| `:read-only` | rc=71 | rc=3 | — |
| `:danger-full-access` | rc=0 | rc=0 | 即不加沙箱 |

报错原文与 M2_REVIEW_r4（第 13 行）、M7_REVIEW_r4（第 37–38 行）、M3_REVIEW_r2（第 15 行）**逐字一致**，可以确定审查方遇到的就是这个沙箱。codex 二进制里的 Seatbelt 基础策略含 `(deny mach-lookup (xpc-service-name-prefix ""))`，mach-lookup 白名单里没有 sysmond，另有 `(allow process-info* (target same-sandbox))`，两者和上述现象吻合。

### 2.3 构建方（Claude CLI）其实不在沙箱里

统计 driver/*_build.log 里构建方自己执行的 `sandbox-exec`/`pgrep` 调用：M0 r3/r4、M1 r1/r2、M5、M7 r1/r2 共 41 次，**0 次 rc71、0 次 rc3**。M0_IMPLEMENTATION_r10 也记录了构建方用 `sandbox-exec -f isolation-r10.sb` 启动 rc.1 宿主成功、pgrep rc=1 NONE。M2/M3 r4 的实施报告写的「sandbox-exec rc71 / pgrep rc3」是**照搬审查方结论**（原文是「沿用 M0/M1/M2 历史 BLOCKED」），并没有重新实测。所以「构建也跑在沙箱里」这个前提不成立，卡点只在审查方。

### 2.4 Codex CLI 有没有开关能放行这两项

- `codex exec` 只有 `-s/--sandbox {read-only, workspace-write, danger-full-access}`、`--add-dir`、`--dangerously-bypass-approvals-and-sandbox`、`-c key=value`、`-p/--profile`。
- workspace-write 能配置的只有 `[sandbox_workspace_write]` 下的 `writable_roots`、`network_access`、`exclude_tmpdir_env_var`、`exclude_slash_tmp`。新式 permission profile（`default_permissions` + `[permissions.<name>.filesystem/.network]`，`network.allow_unix_sockets`）同样**只管文件系统和网络**。
- 没有任何开关能放开 mach-lookup（sysmond）、跨沙箱 process-info，或嵌套 `sandbox_apply`。嵌套 `sandbox_apply` 是 macOS 内核层面的限制，任何 Seatbelt 内部都做不到。
- 结论：要在审查进程**内部**同时拿到这两项能力，只能用 `danger-full-access` 或 `--dangerously-bypass-approvals-and-sandbox`，也就是去掉沙箱，不推荐（见第 5 节）。可行的路线是让**沙箱外的驱动**负责启动和回收，审查方只读取驱动产出的证据。

## 3. 隔离实验（env-probe，共 2 次，均在沙箱外的普通 shell 执行）

- 位置：`runtime/optimization/2026-10-09/env-probe/`
  - `probe.sb`：Seatbelt profile，内容为 `(allow default)(deny file-write*)`，只放行 env-probe 子树和 /dev/null 的写入；`(deny network-outbound)`，只放行 `localhost:8839`（makepad-remote 控制口）和 unix socket。
  - `run_probe.py`：实验脚本。
  - `results/*.json`、`results/*-sandbox-denials.log`、`logs/host-*.log`、`logs/frame-*.png`：证据文件。
- 环境（白名单，不继承 os.environ）：HOME、CFFIXED_USER_HOME、TMPDIR、XDG_CACHE/CONFIG/DATA_HOME、OCTOSENSE_HOME、OCTOSENSE_APP_DATA、OCTOS_HOME、RINX_DATA_DIR、MTL_SHADER_CACHE_DIR、OCTOSENSE_HUB 全部指向 env-probe 下；`MAKEPAD_HIDE_WINDOWS=1`；`MAKEPAD_REMOTE=8839`。
- 命令：`sandbox-exec -f probe.sb <M0/r3/.../MacOS/octosense> --size 1024x700 --test-action capture:<env-probe/logs/frame-*.png>`。**没有加 --help**。用 `Popen(start_new_session=True)` 后台启动，每次运行硬上限 20 秒。
- 宿主二进制 SHA-256：`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`

| | run1-sandboxed（11:38:16） | run2-sandboxed-noquit（11:38:52） |
|---|---|---|
| 启动前 pgrep `MacOS/octosense\|MacOS/octos-kernel` | rc=1（无） | rc=1（无） |
| sandbox-exec 预检（沙箱外） | rc=0 | rc=0 |
| 运行中 | PID=PGID=81252，进程组 1 个成员，pgrep rc=0 | PID=PGID=81518，1 个成员 |
| 渲染证据 | capture 帧 2800×1706 PNG，是完整 OctoSense 桌面和 Dock | capture 帧存在 |
| 退出方式 | `GET 127.0.0.1:8839/quit` → `[makepad-remote] remote quit`，rc=0 | 故意不发 quit（模拟宿主卡死）；14.0 s 时 `killpg(PGID, SIGTERM)` → rc=0，没有用到 SIGKILL |
| 墙钟 | 10.43 s | 14.09 s |
| 结束后进程组成员 / pgrep | 0 / rc=1 | 0 / rc=1 |
| `~/.octosense` mtime | 前后不变（Oct 9 22:58:31） | 不变 |
| 判定 | **CLEAN** | **CLEAN** |

被内核拒绝的写入和联网（来自 `log show` 的 Sandbox 记录，证明隔离确实生效）：
- `file-write-data $DARWIN_USER_CACHE_DIR/org.octosense.desktop/com.apple.metal/.../functions.list|libraries.list`：Metal 着色器缓存，Metal 不认 MTL_SHADER_CACHE_DIR。被拒后宿主照常渲染。这个目录的 mtime 还是 Oct 9 21:38，说明本次没有写入；目录本身是早先未加沙箱的运行留下的。
- `network-outbound remote:*:443`：宿主自带的 news 等系统服务尝试联网，被拒。
- `file-write-data /dev/dtracehelper`：无害。
- 另有一条 `appleeventsd deny file-read-data <octosense 二进制>`，属于系统服务自己的沙箱，与本实验无关。
- 在 ~/Library/{Preferences,Caches,Application Support,HTTPStorages,WebKit} 下检查实验时间窗内新建或修改的 octo/makepad 文件：0 个。

实验结论：

(a) 在沙箱外可以施加「只允许写项目内目录、禁止外联」的 Seatbelt profile，宿主能在其中正常初始化 GUI/Metal 并渲染。M7 r4 记录的 rc=101 Metal panic 是那份 profile 自身过严导致的，不说明这条路走不通。

(b) 能后台启动，能按 PGID 回收，回收后可清点为 0。

(c) `octos-kernel` 是首次使用时才拉起，本次没有出现。harness 仍须按名称和 PGID 一并清点。

## 4. 推荐方案：驱动在沙箱外提供受控的启动和回收 harness

### 4.1 组成

1. **`native_harness.py`**（放在 driver/ 下，由驱动在沙箱外执行，构建方和审查方都**不直接**启动 launcher）：
   - 输入：一个场景请求 JSON（`{mid}/native/REQUEST_<who>_<tag>.json`）。字段只允许白名单内容：`app_id`、`--test-action` 列表（launch-hub / taps / capture 等，禁止 `--help` 和任意参数）、每个场景的最长秒数（≤60，默认 20）、需要预先装入隔离 Store 的 bundle 路径和期望 digest。
   - 每个场景新建 `runtime/optimization/2026-10-09/{mid}/native-runs/<tag>/<scenario>/`，在其中放 HOME/app-data/cache/tmp/config/data/logs，环境变量照抄 env-probe 的白名单。
   - 用 profile 模板生成本次 `.sb`：只放行本场景目录和 /dev/null 的写入，只放行 localhost:<分配的端口> 的外联。M3 真实模型例外，见 6.3。记录 profile 的 SHA。
   - 启动前门禁：沙箱外 `sandbox-exec -f <sb> /usr/bin/true` 须 rc=0；`pgrep -fl 'MacOS/octosense|MacOS/octos-kernel'` 须 rc=1。rc=0 视为有残留，rc 为其他值视为未知。任何一项不满足就**失败关闭**，不启动，并写 `verdict=ABORT_*`。
   - 启动方式：`Popen(start_new_session=True)`，不加 `--help`，`MAKEPAD_HIDE_WINDOWS=1`，用全局文件锁保证同一时刻只有一个宿主。
   - 回收顺序：先 HTTP `/quit` → 等待 4 s → `killpg TERM` → 等待 3 s → `killpg KILL`。所有路径都放在 `finally` 里执行，任何异常一律判 FAIL。
   - 产出证据 `result.json`：命令、环境、二进制 SHA、bundle digest、profile 文本和 SHA、预检 rc、PID/PGID、进程组成员、退出方式、墙钟、回收后进程组成员、启动前后 pgrep 原文、`~/.octosense` mtime 前后值、隔离目录内写入的文件清单、`log show` 的 Sandbox deny 摘要、launcher 日志尾部、capture 帧路径和 SHA，以及 verdict（CLEAN / FAIL / ABORT_*）。此外写一份 `MANIFEST.sha256`，覆盖本次所有证据文件。
2. **只读给审查方**：证据落在项目内，codex workspace-write 可以直接读取并复核哈希，不需要任何 Codex 配置改动。
3. **两段式审查**，用来满足「审查者独立复现」：
   - 第 1 段：审查方照常审查，并写出自己的 `REQUEST_review_<tag>.json`，场景由审查方自己选，不用作者的。
   - 驱动在沙箱外执行 harness。
   - 第 2 段：用 `codex exec resume --last`（或带上请求的新一轮审查）读取证据后定稿。
   - 构建方的场景请求只用来自测，审查方不得拿它代替自己的复现。

### 4.2 怎样满足 02_Review与交接规则 和 run2.py COMMON 的隔离要求

| 要求 | 出处 | 满足方式 |
|---|---|---|
| 测试在隔离合成数据中进行；不发消息、不部署、不发布 | 02 §1 第 12 行 | 每个场景一个全新的隔离目录，内容是合成数据；profile 禁止外联 |
| 宿主的 HOME/app-data/日志/缓存只能在 runtime/optimization/2026-10-09/ 下，不得写 ~/.octosense 或项目外 | run2 COMMON 第 14 行 | 环境变量做重定向，**再加内核级 Seatbelt `deny file-write*`** 兜底；附 deny 日志和 `~/.octosense` mtime 作为证据 |
| 后台启动、测完立即关闭、无残留窗口；禁止 --help | run2 COMMON 第 23 行 | harness 只接受白名单参数；PGID 回收；回收后 pgrep 和进程组清点为 0；`HIDE_WINDOWS=1`，进程清点为 0 即意味着没有窗口 |
| 审查环境不能运行原生时记 BLOCKED，不拿作者报告替代 | 02 第 24 行 | 原生运行由中立的驱动执行，场景由审查方自选；不满足门禁时 harness 返回 ABORT，审查方照实记 BLOCKED |
| 截图、磁盘、回执各自举证，证据类型不能混用 | 02 第 64 行 | result.json 把 capture 帧、隔离目录写入清单和 launcher 日志分字段记录，并有哈希清单 |
| 审查者独立复现；只操作隔离数据；不改生产代码 | 02 第 68–69 行 | 两段式审查；harness 只读候选，写入只发生在场景目录 |
| 不全局盲杀他人进程 | M0 r10 / M7 r4 审查意见 | 只按自己的 PGID 回收。现有 `cleanup_launchers()` 的全局 `pkill -f` 要改掉，见第 5 节 |

## 5. run2.py 需要修改的地方（只列清单，本次未改）

1. **新增 `native_phase(mid, who, tag)`**：位于 `build()`（第 90–94 行）之后、`review()` 之前，以及第 1 段审查之后。功能是扫描 `{mid}/native/REQUEST_{who}_{tag}.json`，逐个场景调用 `driver/native_harness.py`（沙箱外子进程，带超时），把结果路径写进日志和 state.json。
2. **审查循环（第 154–160 行）改成两段式**：第 1 段 `review()` → `native_phase(mid,"review",tag)` → 第 2 段（`codex exec resume --last` 或带证据路径的新 prompt）。第 2 段的报告才计入 `newest_report`。harness 本身出错时，不触发第 73–75 行的「tool failure」停机逻辑，而是单独记录。
3. **`cleanup_launchers()`（第 50–52 行）**：去掉全局 `pkill -f LAUNCHER`，改为调用 harness 的「清点 + 按记录的 PGID 回收」。清点到不属于本循环的 octosense 进程时，只记日志，不杀。
4. **COMMON 第 23 行（宿主启动规矩）和第 14 行**：改成「构建方和审查方都不得直接启动 launcher，只能写场景请求文件，由驱动通过 harness 执行；harness 证据中的 sandbox 预检 rc0、profile SHA、deny 日志、pgrep 前后 rc1、进程组清点为 0，即视为满足隔离与回收要求；Codex 沙箱内的 sandbox-exec rc71 和 pgrep rc3 是审查环境的已知限制，不作为启动条件」。同时写明请求文件的 JSON schema 和白名单 test-action。
5. **REVIEW_ROLE / SOL_REVIEW（第 95、97 行）**：增加两点。第 1 段须写出自选场景的请求；第 2 段须逐项核对 result.json、MANIFEST 哈希、capture 帧和隔离目录写入清单，原生必需项据此判 PASS/FAIL；只有 harness 返回 ABORT 时才记 BLOCKED。
6. **`run()`（第 56–77 行）**：增加一个启动前断言，确认驱动本身不在沙箱里，例如 `sandbox-exec -p '(version 1)(allow default)' /usr/bin/true` 须为 0，否则立即停机并提示「请在普通终端里运行 run2.py」。这样可以防止有人从 Codex 或 Claude 会话里拉起驱动，把整个循环都关进沙箱。
7. **state.json / CARRYOVER**：记录每轮 harness 的 verdict 和证据目录。M2–M7 现在挂账的「原生 BLOCKED」项，须在 harness 可用后重审才能解挂。
8. 新增文件（不在本次范围）：`driver/native_harness.py`、`driver/native_profile.sb.tmpl`、请求 schema `driver/native_request.schema.json`。可以直接以 env-probe 的 `run_probe.py` / `probe.sb` 为原型。

## 6. 风险

1. **`(allow default)` 只限制写入和网络，不限制读取**：宿主仍能读取家目录下的文件（例如 runtime/identity、runtime/secrets）。如有需要，可以在 profile 里对 `runtime/secrets`、`runtime/identity/CREDENTIALS_FOR_ABRAM.md`、`~/.ssh`、`~/.codex` 等追加 `(deny file-read* …)`。每加一条都要实测 GUI 能否正常初始化，M7 r4 收紧过度就导致了 Metal panic。
2. **XPC 代写**：cfprefsd、MTLCompilerService、LaunchServices 等系统服务替宿主写入时，不受宿主沙箱约束。本次检查没有发现新文件，但不能当作永久保证，所以 harness 每次都要做 ~/Library 时间窗扫描并留证。
3. **Metal 缓存**：`$DARWIN_USER_CACHE_DIR/org.octosense.desktop` 的写入被拒，只影响着色器缓存，渲染不受影响。该目录已经存在（Oct 9 21:38），是早先未加沙箱的运行写下的。
4. **网络**：SBPL 不能按域名放行。M3 的 MiniMax 真实请求要么在该场景放开 `*:443`（等于放开全部外联），要么让 harness 在 localhost 起一个只转发到 api.minimax.cn 的代理，profile 只放行 localhost。推荐用代理，并且请求次数 ≤10、遇到 402 立即停止。
5. **UI 交互能力**：`--test-action taps/capture` 和 makepad-remote 都不需要系统授权。如果要用 osascript 或 System Events 模拟真实键入、滚动或点击（M0 记录的 -1743），需要授予权限，见第 7 节。
6. **两段式审查的独立性**：场景必须由审查方选，harness 只执行不判定；否则相当于用作者证据代签。
7. **驱动被误放进沙箱**：如果 run2.py 是从 Codex 或 Claude 会话里启动的，harness 同样会 rc71。第 5 节第 6 条的自检用来拦截这种情况。
8. **端口和并发**：makepad-remote 端口须分配且加锁，避免和 Abram 手动打开的宿主冲突。harness 只按自己的 PGID 回收，绝不按名称杀进程。
9. **不推荐的替代路线**：
   - 审查方改用 `--sandbox danger-full-access` 或 `--dangerously-bypass-approvals-and-sandbox`：审查方会获得整机读写和联网能力，违背「审查只写报告」的约束。
   - 在审查进程外再套一层 sandbox-exec，并在内部 bypass：内层依然不能嵌套 sandbox-exec，codex 还需要写 ~/.codex 和访问 127.0.0.1:4202 router，配置复杂，收益也不如 harness。
   - unix-socket 代理让审查方同步调用 harness：需要改 Codex permission profile 并开 `allow_unix_sockets`，等于在沙箱上开一个口子，暂不推荐。

## 7. 需要 Abram 决定或授权的事项

1. **是否采纳「驱动在沙箱外运行 harness + 两段式审查」**，以及是否授权修改 run2.py（第 5 节清单）并新增 harness、profile 模板、schema 三个文件。
2. **确认 run2.py 从普通终端（Terminal/iTerm）启动**，而不是在 Codex 或 Claude 会话里启动。
3. **M3 真实模型的联网方式**：本地转发代理（推荐），还是在 M3 场景的 profile 里放开 `*:443`。
4. **真实 UI 交互是否需要系统权限**：如果要在 test-action/makepad-remote 之外做真实键盘、滚动、点击，需要在「系统设置 → 隐私与安全性」里给运行驱动的终端 App 授予**辅助功能**，以及对 System Events 的**自动化**权限（解决 -1743）。如果以后要截取宿主之外的屏幕内容，还要授予**屏幕录制**。只用宿主内置的 capture 则不需要任何授权。
5. **M2–M7 是否在 harness 就绪后重新走一轮审查**，以解除目前挂账的「原生 BLOCKED」项。
6. **env-probe 实验目录**（约 7.5 MB：合成数据、截图、日志）是保留作为证据，还是在方案落地后删除。
7. 是否把 `runtime/secrets`、`runtime/identity` 等敏感路径加入 profile 的读取黑名单（风险第 1 条），需要接受可能要多试一两轮 GUI 初始化。

## 8. Abram 裁决（2026-10-11 12:12）

- **采纳**本方案：由驱动在 agent 沙箱外运行 harness，审查改为两段式（`codex exec resume`）；harness 就绪后**重审 M2–M7**。
- **MiniMax 联网**：走本机代理，只转发到 `api.minimax.cn:443`，**不放开全部 443**。代理只在需要模型的 harness 场景中启动，用完即关；密钥只从 `runtime/secrets/minimax_provider.env` 读取，由代理注入，不写进任何日志或报告。沙箱只放行到 127.0.0.1 代理端口的连接。
- **读取黑名单（第 7 节第 7 项）要加**，至少覆盖：`runtime/secrets`、`runtime/identity/CREDENTIALS_FOR_ABRAM.md`、`~/.codex`、`~/.cc-switch`、`~/.ssh`。
- **env-probe 目录保留**。
- **辅助功能和自动化权限这次不申请**，只用宿主内置的 `--test-action` 和截图。
- run2.py 按第 5 节清单修改（先备份为 `run2.py.bak-harness`），并新增 `SKIP_FIRST_BUILD_ALL=1`：每个模块第 1 轮跳过构建，直接用当前代码走两段式重审，不通过就进入正常修复轮；每个模块最多 2 轮、完成优先、记入挂账等规则不变。业务代码 `app/bundle/main.splash` 只能由 MiniMax 修改。

## 2026-10-12 11:50 更新：harness 支持真实键鼠输入（ui_actions）

- **授权**：Abram 2026-10-12 11:50 给 Grok Bot 应用开了「辅助功能」和「自动化 → System Events」。TCC 按发起进程树的 responsible app 归属，驱动 run2.py（PID 2029，从 Grok Bot 启动、已被 launchd 收养）拉起的 harness 同样适用；已用 `native_harness.py ui-probe` 在一个同样脱离父进程（ppid=1）的进程里实测通过。若以后改从 Terminal 启动驱动，需要给 Terminal 同样授权，先跑 `ui-probe` 确认。
- **原因**：固定宿主不认 `type:`/`key:`（M3_REVIEW_r10 B-M3-01），白名单 test_actions 无法真实输入。
- **用法**：场景新增可选字段 `ui_actions`（和 `ui_start_after_s`），详见 `driver/harness/request.schema.json`。宿主自己的 test_actions 先跑完（截图都已存在），harness 再按顺序执行：`sys-click:X,Y`（宿主窗口内坐标，单位 point；grab 截图是 2 倍像素，要除以 2）、`sys-click-snap:查询`、`sys-type:文本`（任意文本含中文，一律走剪贴板 + cmd+v，事后恢复原剪贴板，不受输入法影响）、`sys-keystroke:ASCII`（逐键真实按键，会经过当前输入法；Abram 的 Mac 默认是拼音，会变成未上屏的拼音组合，一般不要用）、`sys-key:Return|Tab|Escape|Backspace|方向键…`（只允许 shift+ 和 cmd+a/c/v/x/z 组合）、`sys-wait:毫秒`、`grab:名字.png`（经宿主控制口 /g 截图）、`snap:查询`（记录控件坐标）。
- **只打进自己的宿主**：每个输入动作在同一次 osascript 调用里先把 harness 启动的那个宿主 PID 置前，再核对前台进程 PID 等于它，不等就拒绝并跳过后续动作。点击用 CGEvent 真实鼠标事件（System Events 的 `click at` 对 Makepad 窗口无效），坐标越出宿主窗口也拒绝。带 ui_actions 的场景不设 `MAKEPAD_HIDE_WINDOWS`，窗口真实可见。
- **串行化**：原有 `.launch.lock` 已让所有 harness 请求串行；另加 `.ui-input.lock`，键鼠场景独占，最多等 180 秒，拿不到判 `ABORT_UI_LOCK_BUSY`。
- **证据**：result.json 新增 `ui_probe`、`ui_lock`、`ui_window`、`ui_started_s`、`ui_actions_log`（每个动作的时间、目标 PID、方法、rc、输出、剪贴板前后摘要），以及独立于隔离判定 `verdict` 的 `ui_verdict`（OK/REFUSED/ERROR/INCOMPLETE/NOT_RUN）；summary.json 每个场景也带 `ui_verdict`。grab 截图也列进 `captures`。隔离、Seatbelt、按 PGID 回收的逻辑不变。
- **自测**（2026-10-12 11:53，无模型、无真实凭据）：在 M3 种子工作台的「账号 ID」框粘贴「测试中文输入：三号楼空调漏水」，在「口令」框粘贴 `abc123`，截图里文字完整出现；verdict=CLEAN，ui_verdict=OK，post_pgrep=NONE，剪贴板已恢复。证据在 `runtime/optimization/2026-10-09/driver/harness/uiinput-selftest-20261012/type_zh/`。
- **限制**：键鼠场景运行时会真实抢占前台，Abram 那段时间不要操作电脑，否则 guard 会拒绝或者误点。截图只经宿主 /g，不需要屏幕录制权限。run2.py 的 COMMON 仍然写着「不使用 osascript、辅助功能、自动化（未授权）」，这次没有改 run2.py，需要在重审 M3 的提示词里另外说明可以使用 ui_actions。
