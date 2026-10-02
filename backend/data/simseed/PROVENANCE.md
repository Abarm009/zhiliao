# 仿真测试数据（simseed）来源声明

| 文件 | 内容 | 大小 |
|---|---|---|
| `l1_seed.json` | L1 事实层快照：216 空间 / 276 设备 / 206 租户 / 12 技工 + 服务关系 | 301 KB |
| `l2_events.jsonl` | L2 事件流：3086 条工单（含租户原话、技工处置流水） | 1.3 MB |

## 生成方式

由仓库历史中的仿真器（`git show d0a9f93:simulator/`，2026-08-17 交付，
三条并行生成器：部件磨损退化 / 账务锁机 / 租户装修）确定性生成：

```bash
git archive d0a9f93 ontology simulator | tar -x -C /tmp/simgen/wagent
cd /tmp/simgen
python -m wagent.simulator.engine --days 373 --seed 42 --start 2025-08-16 --out out
# 只取 out/l1_seed.json 与 out/l2_events.jsonl
```

- `--seed 42`：同 seed 同输出（仿真器验收 V1）
- `--days 373 --start 2025-08-16`：时间轴终点恰为 **2026-08-23**，
  与 ops 回放基准 `seed.BASE` 同日对齐，90 天工单窗口能覆盖尾部数据

## ⚠️ 真值隔离

仿真器同时产出 `ground_truth.jsonl`（每单的真实根因 / 复发标记）——
**该文件被有意排除在本目录之外**，永不进入 Agent 可见的任何表。
库中不存在 `true_*` / `ground_truth` 列（`truth_leak_check()` 守卫）。

## 数据特征（来自仿真器验收记录）

- 复发是涌现的：治标不重置部件磨损 → 30 天内复发率 ~29.5%；治本 → 0%
- 症状歧义：`no_cooling` 对应 14 种根因，无送分症状
- 技工误诊率 40%，且按根因分层（结构性盲区）——L2 的 `reported_cause`
  是技工当时的判断，**可能是错的**，这正是 L3 洞察要纠正的东西
- 租户名已白名单法脱敏（详见 SIMULATOR_2026-08-17.md §5）

## 导入

`wagent_backend.ops.data.simdata.import_sim_seed()` 在建库/重置时随
演示种子一起灌入（`WAGENT_OPS_SIMSEED=0` 可关闭，测试默认关闭）。
