# 知了OctoSense 优化循环工作流规则

> 来源：Abram 2026-10-09 晚的语音和聊天交代，由知了整理。最后更新：2026-10-09 23:02（北京时间）。
> 本文与 GATES.json、driver/run.py 冲突时，以本文为准；本文与 Abram 的最新指示冲突时，以 Abram 为准。知了的基线另存在 `ZHILIAO_BASELINE.md`，两份保持一致。

## 1. 角色与沟通

- **知了**是整个循环的中枢和编排者。**Abram 以后只跟知了沟通**，不直接跟 Codex、Kimi、MiniMax 沟通。
- 知了随时要能回答 Abram 这些问题：MiniMax 的构建进展如何；Kimi 的审核结论是什么；gpt-6.1-sol 终检或介入了几次、分别是什么时候。依据是 driver.log、各轮的 build/review/finalcheck/sol 日志、reports/ 和 GATES.json。
- 知了每小时的 :12、:32、:52 只读巡检一次；有实质变化（换轮、出报告、卡住、进程退出、模型报错）才去聊天里报告。Abram 的 Mac 会一直在线，有问题就在聊天里找他。

## 2. 分工

| 角色 | 工具 | 职责 | 能否写代码 |
|---|---|---|---|
| 实现方 | MiniMax（`claude -p`，用的是 CC Switch 当前的供应商「MiniMax m3」） | 唯一写代码的一方；修复时必须严格逐条按照 Kimi 的建议改 | **能，而且只有它能** |
| 第一核查人 | Kimi（`kimi -p`） | MiniMax 写完后的第一道审查；只给建议，每条建议都要极尽详细：缺陷编号、文件和行号、证据、根因、具体改法、改完后怎么验证 | 不能 |
| 终检和介入 | Codex `gpt-6.1-sol`（high 档，`codex exec -m gpt-6.1-sol`） | 只做 review：Kimi 判 PASS 后做终检；或者在连续 3 轮没过时介入，给出修改意见 | 不能 |

- MiniMax 开建前，脚本先确认 CC Switch 当前的 claude 供应商名字里含 MiniMax，不是就停。CC Switch 本身不改。`claude-minimax` 脚本按旧名字「MiniMax」去找供应商，现在找不到，所以不用它。
- `kimi -p` 不能和 `--auto` 或 `-y` 一起用，否则会报错。
- Codex 很少用，因为太贵。**Astra 不要用**，Codex 默认的 `gpt-6-astra` 一律显式指定成 `gpt-6.1-sol`。
- Codex 和 Kimi 都只做 review。

## 3. 知了的介入权

- 知了已经看出 MiniMax 做得不好时，可以跳过 Kimi，直接打回给 MiniMax 重改。
- 知了尽量不插手执行细节，但看到确实有问题的地方必须介入，因为知了是编排者。

## 4. 决策权限与停止条件

- 大多数情况下，知了不用等 Abram 点头，可以站在一个普通用户的角度自己判断、往下推进。
- **必须 Abram 明确同意才能做的事：**
  1. AppHub publish（要联网、签名、上架，对外公开且不能撤回）。
  2. 配置真实模型 provider（这是已知缺口）。
  3. 确定业务身份来源（这是已知缺口）。
- **循环自动停下来等 Abram 的情况：**
  - 审查或构建认定剩下的阻塞必须 Abram 授权才能解决，也就是在日志里写了 `NEEDS_ABRAM=yes`。
  - 某个模块连续 3 轮没过，gpt-6.1-sol 介入给出意见，MiniMax 再改一轮之后还是没过。
  - 工具一启动就报错。这种情况直接停，不算作一轮。
- 始终有效的约束：只动本项目文件夹；不 git push；不改 CC Switch；不碰其他项目。

## 5. 流程资产与当前状态

- 流程包放在 `docs/optimization/2026-10-09-desktop/`，状态门禁由同目录下的 `GATES.json` 管理。
- 驱动脚本是 `runtime/optimization/2026-10-09/driver/run.py`，日志是 `driver/driver.log`。旧版本备份为 `run.py.bak-codexbuild`（Codex 建）和 `run.py.bak-2238`。
- 每轮的顺序：MiniMax 建 → Kimi 审 → 没过就由 MiniMax 严格按 Kimi 的建议修，进入下一轮 → 连续 3 轮没过时，由 gpt-6.1-sol 介入出意见，MiniMax 再改一轮 → Kimi 判 PASS 后，由 gpt-6.1-sol 终检 → 终检也通过，才进入下一个模块。
- 历史：M0 第 4 轮由 Codex 建（当时用的是默认的 Astra）、Claude Code 审，结论 **BLOCKED**，22:30 自动停下。报告见 `reports/M0_IMPLEMENTATION_r4.md` 和 `reports/M0_REVIEW_r4.md`。主要卡点：本地可信 catalog 还没有；双主体认证、文件和提醒这几项能力还没实测。
- 现状（23:02）：22:56 按新规则重新启动，进程已完全脱离终端会话。22:39 那次启动没有产出就退出了，第一次空跑留下的日志放在 `driver/failed-2237/`。MiniMax 正在做 M0 的修复轮，证据写在 `runtime/optimization/2026-10-09/M0/r5/`。`GATES.json` 里 M0 仍然是上一轮的 BLOCKED，要等这一轮交接后再更新。
