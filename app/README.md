# OctoSense Repair

> **2026-10-06 当前入口**：运行与最新结果见 [根 README](../README.md) 和 [本次提交材料](../submission/2026-10-06/README.md)。下文主要为 10-01/10-02 历史实现及审查记录，不能用旧测试数字或旧截图判断当前版本。原生闭环仍未通过；本地 Web/后端验证与原生展示分别记录。

> **2026-10-14 M7 当前桌面发布候选（本地 staging，仅在隔离沙箱中可重现）**：**0.1.0-i**，见 [M7 r10 staging](../../runtime/optimization/2026-10-09/M7/r10/release/octosense-repair-0.1.0-i/)（上方旧 r4/r2 路径为历史候选，勿再引用）。stamp blake3 由 hub CLI 实时计算并写入 `INTEGRITY.txt`（位于 `release/release-materials/`）；LICENSE/PRIVACY/SOURCES 在 bundle 外的 release-materials/。当前目标宿主 = **rc.6**（`runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app`，哈希见 `host-rc6/sha256.txt`；2026-10-13 16:45 前的 M0/r3 rc.1 宿主仅为历史定位）。最新独立 Review 结论见 [M7_REVIEW_r13](../docs/optimization/2026-10-09-desktop/reports/M7_REVIEW_r13.md)：**BLOCKED**——R-M7-02 严格 JSON 加载反例已闭合，但认证后恢复链、同 Store 原生业务进程重开、精确写点故障缺 harness 控制证据；正常/退回/真实模型完整链 NOT_RUN。不发布、不递交、不上架。

> 石墨主题 Hub 脚本应用 + L2-L6 扩展后端。设计流程：报修 → 技工接单 → 设备确认 → 预约 → 处理 → 完工 → 独立验收 → 退回重做，沿本地事实源走完整闭环。**注意**：该完整闭环仅在历史 Web/后端层实证过；当前原生候选 0.1.0-i 的完整业务链尚未实证（M7_REVIEW_r13：正常/退回链 NOT_RUN），不能用本段表述判断当前原生版本状态。

## 这是什么

OctoSense Repair 是 `Agentic App 2026` 比赛的提交项目。

- **bundle**（`app/bundle/`）：OctoScript 脚本应用，由 card-host 在原生隔离沙箱内解释执行。石墨主题，维修工作台：声明 11 个业务按钮 + 4 个角色按钮；**运行时只实例化 13 个按钮，"退回 / 重置演示"与任务列表面板、状态行在视口外被丢弃**；fs jail 内 `state.json` + `events.jsonl` 写入，重启只回读 STATE，任务本体丢失。
- **后端**（`backend/src/octosense_backend/`）：Python + FastAPI + SQLite，独立任务内核（12 表 / 27 命令 / 29 应用路由 / 原子事务 / 幂等 / 版本 / 事件 / 回执 / 设备绑定 / 证据附件 / 收藏 / 历史建议 / 记录处置 / 任务列表）。

## 已通过的验证

> **2026-10-02 review 后更新**：下表 10-01 的自评已部分改判。当前台账为
> **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**；问题与修复顺序见
> [../docs/build-loop/REVIEW_2026-10-02.md](../docs/build-loop/REVIEW_2026-10-02.md)。

| 项 | 状态 |
|---|---|
| G0-A 固定版本 + 原生构建 + admit + 截屏 | PASS（但 3 张截图是 L0 三按钮版，与当前 main.splash 不同版本） |
| 原生 UI 闭环（按钮渲染 → 点击 → fs.write → kill → restart） | **部分**：state.json 回读成功、任务本体丢失；声明 23 节点只实例化 15 个 |
| L1 后端单元测试（命令 / 状态机 / 权限 / 预约 / 改派 / 退回链） | PASS（11 项，原写 14） |
| L2-L7 扩展单元测试（设备 / 证据 / 列表 / 收藏 / 历史建议 / 记录处置） | PASS（23 项） |
| HTTP 端到端 curl 13 步（DRAFT → COMPLETED 含 reject + 二次 record_progress） | PASS（10-02 独立端口 + 独立 DB 复跑仍 PASS） |
| HTTP 边界 E2E（T02 / T04 / T05 / T15 / T18 / T30 / T31） | **部分改判**：T02 "同 key 不同内容"不返 409；T05 跨项目可接单；T18 `get_task` 无授权 |
| demo-web 三角色浏览器点击 | **FAIL**：报修人在 SCHEDULED 无"确认预约"入口，web 路径走不到 COMPLETED |
| 单测总数 | **39 PASS**（11 核心 + 4 预约改派 + 23 扩展 + 1 dummy） |
| `hub stamp` + `hub check` + `hub scan` | PASS |
| ACCEPTANCE.json | **24 / 64 PASS，8 FAIL**，见 [../docs/build-loop/ACCEPTANCE.json](../docs/build-loop/ACCEPTANCE.json) |


## 启动

```sh
# 1) 安装后端依赖
cd backend && uv sync --frozen && cd ..

# 2) 跑后端 API（端口 8712；推荐用环境变量指定 db 路径，便于 E2E）
OCTOSENSE_PORT=8712 OCTOSENSE_DB=runtime/octosense.db \
backend/.venv/bin/python -m uvicorn --app-dir backend/src \
  octosense_backend.api:make_app --factory --host 127.0.0.1 --port 8712
#   （如果不想用环境变量，make_app() 默认 db 路径 = runtime/octosense.db）

# (历史) 启动 — 卡片宿主 card-host 路径
#
# M7 r3 起桌面发布候选已迁移到 `OctoSense.app`（r3 提取 /
# `runtime/optimization/2026-10-09/M0/r3/host/app-extracted/`）。
# card-host 路径保留为 10-08 提交对应的 legacy 入口，
# 仅在 P06P07P08 外部递交流程中作为历史参考保留，不是当前目标宿主。
#
# 旧命令（2026-10-06 提交时使用；不再启动）：
#
#   MAKEPAD_REMOTE=8155 \
#   runtime/native-build/OctoSense-App-Hub/target/release/card-host \
#     --bundle app/bundle --app-data /tmp/octosense-appdata \
#     --allow-unsigned --stamp
#
# 历史遗留：splash 验证用 `curl http://127.0.0.1:8155/snap` 与
# `curl http://127.0.0.1:8155/g?raw=1`，留给 archival purposes only。

### M7 r4 本地发布候选（staging + 桌面启动实测）

不替代 0.1.0-b 已递交候选；用于同版本号不同字节差异时的本地复检与 hub stamp 验证。
本节实测命令已按 B-M7-01 审查意见回到当前解阻路径（直接 subprocess + try/finally），旧 card-host + `/tmp/octosense-appdata` 段落一律不再启动。

```sh
# 隔离 staging：只能在自己的隔离目录运行；不复写工作区 app/bundle
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_review_driver.py

# 沙箱内 hub stamp + 私钥 try/finally 销毁
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_sandbox_sign.py

# 静态 acceptance（M7R2-NN 自有编号；原 64 项含义保留）
python3 runtime/optimization/2026-10-09/M7/r2/scripts/m7_acceptance_run.py

# A-M7-03 重冻结后材料自指纹重核 + 篡改测试
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_rehash.py
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_rehash_tamper_test.py

# B-M7-01 驱动控制流反例（内存 mock，不启动宿主）：3/3 PASS
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_driver_injection.py
```

桌面启动实测（B-M7-01 r4 修复版：直接 subprocess + 隔离 + try/finally）：

```sh
# 直接 subprocess（strict sandbox-exec 当前 Metal panic，未冒充 PASS）。
# 所有写入重定向到 M7/r4/sandbox/；HOME/TMPDIR/CFFIXED_USER_HOME/
# XDG data/config/cache 全在隔离根。
python3 runtime/optimization/2026-10-09/M7/r4/scripts/m7_launcher_probe.py \
  --bundle runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c \
  --label probe-direct --wall-cap 4.0 --post-term-cap 2.0
# 证据：runtime/optimization/2026-10-09/M7/r4/launch-logs/probe-direct*/run.json
# 3/3 OK：wall ≈ 4.0s；TERM-after ≤ 23ms；proc_rc=0；post_pgrep_rc=1；residue_clean=true
# 注入测试：m7_driver_injection.py 三个反例 + clean baseline 通过
```

P06（递交）/P07（收录）/P08（赛事回执）保持 UNASSESSED；本轮不自动发出、不 push、不上架、不配置真实 provider。

### 端到端复跑（curl）

```sh
# 启动后端（db 路径可改）
test -f /tmp/octosense.db && unlink /tmp/octosense.db
cat > /tmp/run_api.py <<'EOF'
import os, sys
sys.path.insert(0, '/Users/abeam/一些尝试/知了OctoSense/backend/src')
from octosense_backend.api import make_app
import uvicorn
app = make_app(os.environ.get("OCTOSENSE_DB", "/tmp/octosense.db"))
uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("OCTOSENSE_PORT", "8713")), log_level="warning")
EOF
OCTOSENSE_PORT=8713 OCTOSENSE_DB=/tmp/octosense.db \
  backend/.venv/bin/python /tmp/run_api.py > /tmp/octosense-e2e.log 2>&1 &
sleep 2
bash backend/scripts/e2e_full_chain.sh
```

## 固定版本 / 来源

| 仓库 | SHA |
|---|---|
| OctoSense-App-Hub | `6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747` |
| Octoscript-Makepad | `b33f494b963759088edf5785fc6266cb8593818ee` |
| Makepad | `4fdcfccc127b700f1fc01aa1a5488af938dd7f3d` |
| Octoscript | `68f6a9df55692b5d8ef8873a12721e279a3f40d6` |
| rustc / cargo | 1.98.1 |
| Python | 3.12.13 |
| 后端 | octosense_backend 0.2.0 |
| Bundle | octosense-repair 0.1.0（blake3 `c066a517776438e1e4593f3f106f6a5ba24c5eb6668be7e18a2bded4bdbbaf82`） |

## 已知限制

- 后端 demo 身份通过 `X-Actor-Id` 请求头读取；生产必须从可信会话或原生 host Bearer 取得 actor。
- **`_check_actor_role` 不按 project 校验角色**：跨项目用户可建档/接单（R-P0-2）；`GET /tasks/{id}` 无授权校验，任意 actor 可读全量（R-P0-3）。
- 真实模型接入（G0-E / T25 / T26）未做；UI 明确标记"离线演示，原话保留"，不冒充模型成功，不写任务状态。
- Jobs / scheduler / 提醒（T13 / T23）未实现；依赖 G0-F 与 Shell 兼容 deadline。
- 原生 App Card / glance 视图（F / T29）未做；依赖 Shell 编译和 pairing code（T32）。
- card-host 沙箱内 splash 不发起网络请求；按钮 on_click 触发 fs.write；后端 HTTP 由外部 uvicorn 进程提供。
- **splash 只持久化 STATE**（actor/page/selectedIdx/status），不持久化任务本体；重启后 TASKS 为空，且任务 id 用 `TASKS.len()` 生成，会与 events.jsonl 里的旧 id 重复（R-P1-1）。
- **splash 声明 23 个节点，运行时只实例化 15 个**："退回 / 重置演示 / 任务列表 / 状态行"在 412×816 视口外被整体丢弃，点不到也看不到（R-P0-1）。
- demo-web `/task/{task_id}` 返回 500（`task.html` 不存在）；`u-tech-2` 登录即 `PERMISSION_DENIED`；`record_advice` 同 key 重放返 500（R-P1-2 / R-P1-3 / R-P1-4）。
- 真实人工 UI 验收（U01-U12）：1280×800、窄窗、文字放大、键盘焦点、长中文、滚动稳定性、对比度、2–3 分钟演示脚本，需要真人或独立测试驱动；本轮仅完成结构化 + 真实持久化 + 真实验证。

## 演示素材

- `runtime/build-loop/l0-shots/L0-A-{1-initial,2-after-click,3-after-restart}.png`（首次 G0-A）
- `runtime/build-loop/l2-shots/L2-workbench-{1-initial,2-after-flow,3-after-restart}.png`（L2 工作台）

## 递交材料

详见 `docs/build-loop/SUBMISSION.md` 与 `app/build/review.json`（hub scan 输出）。
# 2026-10-10 五账号身份子范围

真实账号表和初始凭据仅在项目 `runtime/identity/`，不随 bundle 分发。演示 identities/USERS 已退出授权路径；新会话未登录时失败关闭。当前 launcher 安全登录未接通，完整源码/包及原生隔离仍有阻塞，不能将五账号创建或无窗口 VM 测试视为应用原生可用。安装、同步、验证与限制见 [M2 五账号记录](../docs/optimization/2026-10-09-desktop/reports/M2_ACCOUNTS_SOL_2026-10-10.md)。
