# M2 五账号实施记录 · 2026-10-10

**结果：五个独立凭据账号已创建；D-M2-01 的会话/授权代码和无窗口契约验证已完成，原生登录闭环仍 BLOCKED。GATES 的 M2 保持 BLOCKED，没有 PASS，也没有进入下一模块。**

本报告文件名按 Abram 指定保留 SOL。工具接口不能独立核验主会话实际模型/Router，不能把文件名解释为已经证明使用 gpt-6.1-sol。没有子代理。用户本轮授权五账号实施，不构成发布、上传或其他模块修复授权。

置信度：账号生成、文件权限、标准库哈希对照、实际 Splash 函数与本地宿主 fs 源码的 VM 执行结果 **高**；当前发行 launcher 中的登录、UI、会话与命令端到端结果 **未知 / BLOCKED**。

## 账号与凭据

|账号 ID|名称|项目与角色|技能|
|---|---|---|---|
|u-reporter-1|报修人一|prj-A REPORTER|—|
|u-reporter-2|报修人二|prj-B REPORTER|—|
|u-tech-1|技工甲（HVAC）|prj-A TECHNICIAN|HVAC|
|u-tech-2|技工乙（电气）|prj-A、prj-B TECHNICIAN|ELECTRICAL|
|u-manager|经理丙|prj-A MANAGER|—|

保留原 ID，既有 task.reporter / assignee / 回执归属无需重写。这里创建的是有独立凭据的本地账号记录；没有把它们说成已经原生登录成功的五名用户。

- 随机源：Python `secrets.token_bytes`，每账号 32 字节随机令牌、16 字节独立随机盐。五个令牌、盐、哈希均独立；实际初始凭据与各自哈希已在内存中逐项核验，未打印令牌。
- 哈希：`pbkdf2-sha256-token-v1`，PBKDF2-HMAC-SHA256 / 4096 轮 / 32 字节输出。Splash 使用经 VM 向量核验的纯脚本 SHA-256/HMAC/PBKDF2，没有用 FNV、时间戳或演示账号 ID 当凭据。
- 这是 **256 位随机令牌方案**。4096 轮不能当作人工短口令的足够配置；不提供把任意人工口令保存为这些账号凭据的接口。未发现当前 Splash 可调用的原生慢哈希或安全随机 API，随机生成在本地管理脚本完成。
- 生命周期：`enabled`、`revoked_at`、`expires_at`、`credential_epoch` 与项目角色。初始有效期从实际生成时刻计算为 365 天；内存会话有效期 8 小时。`revoked_at != 0` 立即失效；未来撤权时间也不暂时放行。缺失/畸形字段失败关闭。
- 凭据轮次变化使既有会话失效；本轮没有额外实现口令轮换 UI。

## 存放与安装/同步

1. `runtime/identity/accounts.json`：权威账号表，仅含慢哈希、盐、角色、撤权等元数据，权限 **400**。
2. `runtime/identity/CREDENTIALS_FOR_ABRAM.md`：唯一写入五个初始明文令牌的文件，从首次创建起权限 **600**，目录 `runtime/identity` 为 **700**。本报告不含令牌。
3. `runtime/identity/installations.json`：已登记的本地应用数据目录，权限 600。
4. 本轮已安装/读回 `runtime/identity/host-data/identity/accounts.json`，权限 400；这是准备好的本地数据目录，**不是已经由 launcher 加载的证明**。

`.gitignore` 已包含 `runtime/`；`git check-ignore` 已核验账号表和初始凭据路径。没有把账号表或哈希放进 git 跟踪的应用/文档文件；`identities.json` 已替换为无账号、无 default_actor 的 `retired_demo_fixture` 说明文件，运行代码不读取它。

宿主路径证据：本地 `splash_storage.rs::resolve_jailed` 将绝对路径也解释为应用数据目录内的路径，拒绝 `..` 越过根；不是 macOS 绝对路径。源码中的根绑定由 Rust 按 VM heap 设置。无窗口探针使用该文件的实际实现（只适配 import）执行 fs 读写，已验证 `/absolute-probe.json` 与 `absolute-probe.json` 指向同一隔离文件，父目录逃逸拒绝，权限 400 的账号表不能被脚本覆盖。

应用只读 `identity/accounts.json`。确定宿主实际 jail 后，将其作为 **精确数据目录** 传入安装脚本；不是传 bundle 根，也不是传 jail 的父目录。例如本轮已执行：

```sh
python3 scripts/manage_identity.py install --data-dir runtime/identity/host-data
```

脚本只接受本项目 `runtime/` 下的非符号链接路径。源码契约中 card-host 的 jail 是 `--app-data` 根追加 app_id；这不是 launcher 的已验证启动参数。当前 launcher 无法按本轮规则启动，实际 launcher 的目标数据目录没有在本轮运行确认。不得拿上述 staging 路径冒充安装成功，也不得猜测写进 `~/.octosense`。后续由可强制隔离的宿主配置指定项目内 jail，再用同一安装命令安装到该精确目录并进行原生读回。

变更授权必须通过本地管理入口，同步到 **所有已登记目录**，例如：

```sh
python3 scripts/manage_identity.py change u-tech-1 --revoke
python3 scripts/manage_identity.py change u-tech-2 --expires-at-ms 1
python3 scripts/manage_identity.py change u-tech-2 --remove-project prj-B
python3 scripts/manage_identity.py sync
```

这些是操作示例；本轮没有对五个真实账号执行撤权/到期/移项目。所有生命周期破坏测试使用合成副本。

管理脚本使用管理员文件锁，先将全部安装副本原子替换为不可授权的 `sync_in_progress`，再更新源表与各副本，逐一读回。中断发生在发布阶段时，尚未同步成功的目录保持拒绝状态，不沿用旧授权。全部目录完成失效标记前，源表尚未提交新授权；CLI 失败不宣称撤权成功。修改源表后不执行同步不会自动更新另一份独立副本，因此不得把手工编辑源表视为已经生效的撤权。应用每次操作重新读取的权威文件是 **当前 jail 的安装表**。

信任边界是本机管理员控制的只读账号表与应用代码。管理脚本可以替换它；普通 Splash fs.write 不能写权限 400 的表。拥有 macOS 账号权限并主动 chmod/改源码的人仍是本地管理员，不由该应用鉴别。这不是生产认证或租户隔离已经完成的声明。

## 防冒用和失败关闭

- `SESSION`、`AUTH_JOB` 只在 VM 内存里；`loadViewState` 不加载会话，丢弃 state.actor。重启初始主体为空。业务中 `STATE.actor` 读取全部移除；保留的一处赋值只用于清空磁盘视图字段。
- `authBegin` 读取账号表，验证独立令牌的 PBKDF2；`authStep` 完成后再次读取账号，核对撤权/到期、凭据轮次及原盐/哈希，才由权威账号记录设置主体。账号 ID 单独不能建立会话。
- 派生按一次回调一轮处理；登录未完成、失败、超时或退出时都没有业务主体。凭据/派生材料不写 state、事件或日志。
- `getMe` 每次从当前账号表刷新；不再回退 USERS。失效返回空主体/空角色。名单、分配目标、联系人校验均从真实账号表派生；目标账号也重新核验有效性、项目角色和技能。
- `runAction`、`runCommandBound`、`runCommand` 和创建路径增加有效身份/项目/命令角色核验。`runCommandBound` 在取锁和旧 final 回执查询之前授权，`commitBound` 在业务盘写前再次授权；失效拒绝不会新增拒绝回执或碰任务/事件。
- `receiptFor`、M6 历史/摘要/历史计数入口重新核验会话和任务可见性。移出项目后，即使仍持有旧 final 回执，也得到 denied。状态所选项目只是视图选择，必须满足真实项目角色。
- `setActorM2` 只保留兼容展示标签，不改变 SESSION。原演示身份切换栏已退出正式桌面。
- **当前 UI 显示“宿主安全登录待接入”，没有秘密输入框，也没有将已保存的某个 ID 自动登录。** 本轮没有绕过宿主禁止应用收集口令的策略。`authBegin` 尚未接到当前 launcher 的可信安全凭据入口，因此正常打开当前应用依旧无主体、禁止业务写入。

## 实际验证

证据均在 `runtime/identity/evidence/`。VM harness 无窗口、无网络，直接执行从最终 `main.splash` 提取的生产函数与本地 Makepad 的实际 jailed fs。测试令牌是独立合成夹具，不是五个初始令牌。两位报修人的测试运行于不同 OS 进程，三个其他角色另有独立进程。

|检查|实际结果|证明范围 / 证据|
|---|---|---|
|五个真实账号、独立初始令牌、权限/忽略规则|通过；五项真实哈希均与指定凭据文件内的对应令牌一致|本地创建/读回；`provision-check.json`，不含令牌|
|SHA-256 空串/abc；HMAC/PBKDF2 3 与 4096 轮标准库对照|通过；4096 轮无预算 VM 约 3.459 秒|实际 Splash VM；`crypto-probe.log`、`crypto-4096.log`|
|A/B 独立会话；三种其他账号角色登录|五个夹具进程 rc0；角色允许/拒绝符合预期|实际生产认证/角色函数；`contract-results.json`、五份 probe 日志|
|盘上 state.actor/伪造 subject/session；展示切换|不改变经凭据核验的主体；不能借经理权限|两个报修人 VM；命令入口拒绝错误角色|
|错令牌、退出、会话到期|拒绝命令和旧回执查询|两个报修人 VM，实际 KDF|
|撤权、账号到期、移出项目、角色改变、凭据轮次改变|下一次命令、旧回执、历史/摘要/计数及提交前检查均拒绝；取锁次数仍 0|同一存活 VM 中通过 harness 管理员入口原子改变真实隔离盘上的账号表|
|缺字段/重复账号表|失败关闭；清空缓存，不沿用启动名单|实际 Splash VM|
|盘事实不变|五个测试进程的 tasks/actions/events 前后 SHA-256 一致|仅合成隔离事实盘，不是原生真实按钮成功证据|
|权限 400、防路径逃逸、绝对路径映射|通过|实际宿主 fs 源码移植执行；不证明本轮 launcher 加载|
|管理同步两个目录、发布中断|两个副本均读回撤权；中断后均不能授权；恢复后读回一致|Python 管理脚本、合成副本；`admin-results.json`|
|单次起步 20 万指令预算|通过|`entry-budget.log`；不代表完整 UI 回调已验收|
|完整 KDF 2000 万累计指令预算|**失败：instruction limit exceeded**|`session-budget.log`；默认受限策略中不能宣称可用|
|当前完整源码解析|**16 个错误；开始快照同样 16 个**|同一本地 Makepad parser，仅解析未执行；`full-source-syntax.log`、`baseline-syntax.log`|
|当前完整 bundle Hub check|**REFUSED**|`bundle-check.log`；既有 .DS_Store/log/bak 和资源引用问题未扩修；本轮没有秘密输入框违规|
|原生 launcher / 原生 A/B / 登录按钮 / 原生命令与旧回执查询|**BLOCKED / NOT_RUN**|隔离 rc71、进程枚举 rc3；`preflight.json`；host_started=false|

复现无窗口契约探针：

```sh
python3 scripts/test_identity.py
```

本轮实际离线构建了 `runtime/identity/evidence/vm` 下的 Rust 测试 harness（使用项目内 Makepad 源码）；它不在应用包里，也不是新桌面壳。harness 源文件、Cargo.lock、构建日志保留在证据目录。生产认证函数与 scripts 中的模板字节一致由测试核验。五个真实账号的实际令牌只用 Python 在内存中核对哈希，没有写进 probe 源文件或日志。

## 候选与文件改动

- candidate_id：`M2-accounts-20261010-worktree`。这是账号子范围候选，不是全部 M2 缺陷已经修好的交接。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`；工作树原有大量 M3–M6 等改动，不以 HEAD 冒充候选内容。
- 开始 main SHA-256：`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`。不是 r2 报告的历史字节快照。
- 最终 main SHA-256：`a7e7443547422f80f84b0214e55f0cfad4a86e4a4dc553f811ab2d197a64d18b`。
- 完整清单：`candidate-manifest.json`；本轮 main 差异：`identity-only.diff`；开始的 main/identities/GATES 副本均保留。秘密不进入候选清单或应用包。

|文件|改动|
|---|---|
|app/bundle/main.splash|嵌入已验证认证模块；移除业务 STATE.actor/USERS 兜底；刷新授权与读/写守卫；禁用尚未接通的原生登录；保留既有业务改动|
|app/bundle/identities.json|退出授权，清空演示账号/default_actor，说明真实数据位置|
|app/bundle/manifest.json|用本地 hub stamp 重算当前 bundle 摘要；不是安装、签名或发布成功|
|scripts/manage_identity.py|安全生成、权限、安装登记、管理员同步与生命周期变更；不输出秘密|
|scripts/identity_crypto.splash|可对照的纯脚本密码哈希模块，与 main 中模块一致|
|scripts/identity_auth.splash|可对照的会话与动态授权模块，与 main 中模块一致|
|scripts/test_identity.py|实际生产函数与 jailed fs 的无窗口验证；所有破坏测试使用合成副本|
|GATES.json|只更新 M2 的账号候选 BLOCKED 交接；旧 r2 状态快照归档，其他模块完全未变|
|app/README.md、docs/VERIFICATION.md|增加本轮入口及明确未接通项|
|本报告|本轮实施/证据/阻塞记录|
|runtime/identity/|账号、唯一初始凭据、安装表/副本与测试证据；全部忽略入库|

本轮真实账号哈希表只在 runtime 中，不修改旧 WAgent、后端旧契约、CC Switch 或其他工具。没有 git push、publish、上传、模型调用、发消息或网络请求。没有启动 launcher，没有调用其 --help。

## 尚未闭合

1. 当前宿主受限应用不允许秘密输入。需要真实宿主安全凭据接口/经核验的本地可信适配，才能接通原生登录；本轮不虚构该接口存在。
2. 4096 轮 KDF 超过当前默认 2000 万累计预算。高预算 system 策略是另一个准入范围，未在本轮将应用改成 system app，也没有通过降轮数隐藏问题。
3. 当前强制隔离/进程回收预检失败；即使前两项修复，也须先满足 launcher 后台启动、立即回收与独立原生核验规则。
4. 主文件的既有全源语法问题和当前完整包的 Hub 拒绝项仍阻止将局部 VM 结果解释为可运行候选。
5. D-M2-02～07 没有在本轮重新修复或验收；原独立审查记录保留。38 业务 / 12 UI / P0 及 M0/M1 状态未降低，也未沿用历史 Store 安装结果作本轮成功证明。

因此：**账号创建完成，编码子范围交接待 Review；D-M2-01 的原生闭环未完整闭合，M2 不放行。** 解阻需要实际宿主能力和代码修复，不需要再询问本次“五账号”授权。

补充检查：候选清单逐文件读回一致；五个真实初始令牌在指定凭据文件之外的本轮源文件/文档/证据中出现次数为 0，见 `final-audit.json`。Python 编译检查首次受到继承的外部缓存目录配置影响，尝试建缓存目录被权限拒绝；随后显式将编译缓存限定在项目 runtime 下重新运行。未在项目外创建该缓存。

操作范围偏差：启动时按环境指令只读了项目外 MEMORY.md 和两个技能文件，随后停止项目外资料读取；未写项目外文件。没有可用的会话 createdAt/标题变更工具，因此未猜日期或声称已设置标题。
