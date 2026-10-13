### App id

octosense-repair

### Version

0.1.0-b

### Repository URL

https://github.com/Abarm009/zhiliao

### Tag

octosense-repair-b-v0.1.0

### Full commit SHA

8d730569546cb57310944bb299695134df773b9d

### Bundle path

app/bundle/

### Bundle BLAKE3 digest

e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579

### Publisher id

Abarm009

### Publisher public key

unsigned

### Privacy policy URL

https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/docs/PRIVACY.md

### Support contact

https://github.com/Abarm009/zhiliao/issues

### Platforms tested

macos：macOS Apple Silicon，本地旧版 card-host（历史记录 Hub@6741dea / Shell@a5d847a）。此前部分 DRAFT→OPEN→ACCEPTED→SCHEDULED 真实点击、身份可见性和无真实证据时完工阻断有实测。IN_PROGRESS 的部分验证使用合成状态。最新候选之后未重跑完整业务独立复验；当前正式发行版、商店安装和其他平台未验证。

### App Hub revision the gate ran on

6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747（历史构建记录，当前二进制来源未独立核实，详见 What is not verified）

### Gate output

```text
$ hub check app/bundle --allow-unsigned
octosense-repair 0.1.0-b — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none

2026-10-08 Asia/Shanghai，在已推送标签的全新克隆上执行；克隆HEAD：8d730569546cb57310944bb299695134df773b9d。包检查不等于业务验收。
```

### Scan answers

2026-10-08 在已推送标签的全新克隆上重新生成 packet，7 项；未指定 reviewer，以下为发布者答复，不是独立审核结论。

1. Does the app do what its name, subtitle and description claim? Cite the text in its source.
部分实现。app/bundle/main.splash 中有维修状态机及 createDraft、acceptTask、confirmAppointment、submitCompletion、acceptCompletion 等动作。已有部分 DRAFT→OPEN→ACCEPTED→SCHEDULED 实测；真实附件、完整完工验收闭环未通过。app/bundle/listing.json 中“全闭环通过”的描述过期，需要修正，不据此申请直接 pass。

2. Do the listing's platforms and category fit an app of this kind?
app/bundle/listing.json 声明 macos、productivity。只在 macOS Apple Silicon 固定旧版 card-host 上有部分实测，未验证其他平台或当前发行宿主。

3. Do the granted capabilities match what the app visibly does? For a script app, name every host it requests and why. Name any grant nothing on screen needs.
app/bundle/manifest.json 仅声明 storage。main.splash 使用 fs 读写任务、状态、回执及事件。check 输出 hosts 为空、agent none；无模型和网络调用，无额外网络主机。

4. Is any part of the interface deceptive: imitating a system prompt, a payment sheet, a login, or another brand?
main.splash 使用维修协作自有界面，无密码、付款、外部登录表单。setActor 为演示角色切换，不是生产认证授权。

5. Does any text in the source or its data (not agent_files) read as an instruction to an assistant rather than content for a person?
本包没有应用 AGENT.md、tools.json 或 skills，也未调用模型。main.splash 含开发注释、UI 文本和业务函数，不把用户输入当模型指令执行。请人工复核最终源码。

6. Is any wording abusive, or aimed at a private individual?
main.splash 演示角色和状态提示为中性业务用语，未发现针对真实个人的攻击性文字。

7. Route: pass, human-review, or reject. Give reasons a publisher can act on.
human-review。首次 unsigned 候选，存在 listing/README 过期结论、真实附件与模型未接通、动态幂等及旧事件迁移未完整复验、最新宿主未验收。请人工检查并反馈，生成 packet 和创建 Issue 不代表审核或收录。

### Screenshots

以下均为合成/虚构演示数据；旧截图不证明当前完整闭环。
- [b01-initial.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b01-initial.png)
- [b02-draft-created.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b02-draft-created.png)
- [b03-submit-open.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b03-submit-open.png)
- [b04-schedule-confirmed.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b04-schedule-confirmed.png)
- [b05-completed.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b05-completed.png) — 历史演示快照，不能作为当前完成验收证据
- [b06-after-restart.png](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/app/bundle/screenshots/b06-after-restart.png)

独立复验的无真实证据完工阻断截图：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/screenshots/15-independent-legacy-blocked.png

### What is not verified

知了 · 维修任务协作，首次候选递交，申请 human-review。

真实附件（文件选择、字节持久化、摘要校验）、真实模型接入、完整原生 IN_PROGRESS→AWAITING_ACCEPTANCE→COMPLETED、稳定 key 动态幂等、grant 申请/撤销/到期、生产认证与租户隔离、最新官方宿主安装及全部38业务/12UI验收均未通过或未验证。旧 JSONL 事件备份不等于活动事件已迁移恢复。最新公开提交后没有重跑完整业务独立复验。

固定源码的 listing、README、旧草稿和扫描旧答复仍有“全闭环通过”“scan 通过”等过期表述。旧 COMPLETED 截图来自历史演示，不证明当前候选闭环。请以本正文和当前候选状态为准，把文案不一致作为待修问题。

工具构建来源：历史 SOURCES.md 记录 Hub@6741dea，官方该提交完整 SHA 为 6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747。本地二进制 mtime 为2026-10-01，当前工具目录无.git，无法通过当前 checkout 的 HEAD 独立证明二进制构建来源；本次未重编当前未修改的官方 main。因此表单中的 Hub revision 是历史记录引用，不声称最新/未修改构建已验收。

标签沿用原候选计划名称 octosense-repair-b-v0.1.0，实际 manifest version 为0.1.0-b；已回读确认指向固定SHA，不移动标签。标签名与表单建议 v<version> 格式不同，请人工反馈是否需下一版本调整。

应用包仅使用宿主隔离存储，不依赖Python/Web服务；后端演示测试不能替代原生验收。

当前候选状态：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/CURRENT_REVIEW_STATUS.md
已知限制：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/KNOWN_LIMITATIONS.md
组件来源：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/SOURCES.md
前轮独立复验（先前审查快照）：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/docs/build-loop/RECHECK_NATIVE_B_FINAL_2026-10-06.md
候选 Pre-release：https://github.com/Abarm009/zhiliao/releases/tag/octosense-repair-b-v0.1.0
ZIP：https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip
ZIP SHA256：6a58e27ade7255760e19b6b7229d744eb92799958fd84c728bf0d46c4de1fa12，大小1,544,808字节，解压包根 bundle/；12文件逐字节匹配固定提交源码包。

本次只申请候选人工审核，不声称维护者批准或商店收录。

### Confirmations

- [x] My bundle contains no passwords, API keys, tokens or other secrets.
- [x] I will not move, delete or recreate the tag.
- [x] I took the gate output above from a fresh clone of the pushed tag.
