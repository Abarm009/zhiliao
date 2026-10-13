## 知了 · 维修任务协作 — 首次候选递交

本次递交 `octosense-repair 0.1.0-b`，申请 **human-review（人工审核）**。这是固定版本的原生候选，尚未完成全部业务验收，不声称完整原生闭环、真实模型接入或商店安装已通过。

### 仓库、版本与发布者

- 队伍：知了；GitHub 提交账号：`Abarm009`。
- App ID：`octosense-repair`；manifest version：`0.1.0-b`。
- 公开仓库：https://github.com/Abarm009/zhiliao
- 固定标签：[`octosense-repair-b-v0.1.0`](https://github.com/Abarm009/zhiliao/releases/tag/octosense-repair-b-v0.1.0)，已发布为 Pre-release 并回读确认指向下述 SHA。
- 完整提交 SHA：`8d730569546cb57310944bb299695134df773b9d`。
- 应用包目录：[`app/bundle/`](https://github.com/Abarm009/zhiliao/tree/8d730569546cb57310944bb299695134df773b9d/app/bundle)，入口 `main.splash`。
- ZIP：[octosense-repair-0.1.0-b.zip](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/bundle/octosense-repair-0.1.0-b.zip)。解压后的应用包根为 `bundle/`。
- 发布者 ID（首次 unsigned）：`Abarm009`。
- 签名方式：**unsigned，首次提交**，无已登记的发布者公钥。 listing 的发布者署名为 `Abram / OctoSense (Local Dev)`；GitHub 账号为 `Abarm009`。
- bundle blake3：`e5b477c73bbee2b7a779661c6845d061e8ec53ff46d9b75dd47435702da16579`。
- ZIP SHA256：`6a58e27ade7255760e19b6b7229d744eb92799958fd84c728bf0d46c4de1fa12`；大小：1,544,808 字节。
- [隐私说明](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/docs/PRIVACY.md)；许可证 Apache-2.0。

### 功能与验证范围

围绕一项维修任务组织报修人、技工与项目经理的报修、接单、设备关联、预约、处置、完工及独立验收。当前为本机演示候选，角色切换用于演示，不代表已实现生产认证或租户隔离。

此前在固定旧版本 card-host 上实测了 DRAFT → OPEN → ACCEPTED → SCHEDULED 的部分主路径，以及身份可见性和无真实证据时拒绝完工的路径。IN_PROGRESS 的部分验证使用合成状态；完整 IN_PROGRESS → AWAITING_ACCEPTANCE → COMPLETED 流程尚未验证通过。最新公开提交之后未重跑完整业务独立复验。

应用包只声明 `storage`，不拉起 Python 服务、不访问网络、不调用模型。仓库中的 Python/Web 演示和视频是单独材料，其测试结果不能替代本原生候选验收。

**历史材料更正：** 固定提交中的 listing、README、旧 Issue 草稿和扫描答复仍有“全闭环通过”“scan 通过”等过期表述；旧 COMPLETED 截图来自此前演示快照，不是当前候选完整验收的证明。本次正文与[当前候选状态](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/CURRENT_REVIEW_STATUS.md)说明当前范围。请将这些文案不一致作为待修问题审阅，勿据此认定已完整通过。

### 完整 hub check 输出

2026-10-08（Asia/Shanghai）再次对与上述固定提交一致的 `app/bundle/` 执行：

```text
$ hub check app/bundle --allow-unsigned
octosense-repair 0.1.0-b — PASSED
  [warning] publisher-signature: unsigned: accountability rests on the hub alone
  grants: capabilities {"storage"}, hosts {}, storage 16777216 bytes, agent none
```

工具为本地既有 `hub`（记录来源 Hub@6741dea；构建版本来源见下方）。本次 ZIP 内的 12 个文件逐字节匹配源码包，源码包与固定 Git 提交无差异。此检查仅为包准入检查，未执行完整业务测试，也不证明最新官方发行宿主兼容。

### 扫描问题答复（本次更正版本）

既有[扫描 packet](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/check/03-scan-packet.json)由旧版本 CLI 生成，含 7 项问题。以下答复覆盖过期的旧自答；生成 packet 不等于独立 reviewer 批准。若当前 Hub 增加问题，请补充反馈。

1. **是否实现名称和描述所声称的功能？** 部分实现。维修状态机和动作函数存在，部分原生主路径有实测；真实附件、完整完工验收闭环未通过。listing 的完整闭环描述需要修正，故本次不申请直接判 pass。
2. **platforms/category 是否合适？** 本候选仅在 macOS 本机固定旧版 card-host 上验证，listing 声明 `macos`、`productivity`。其他平台和当前商店宿主尚未验收。
3. **权限是否匹配可见行为？** 仅声明 storage，供任务、回执、状态和事件文件读写。check 输出 hosts 为空、agent none；脚本没有模型或外部网络调用。身份演示切换不是认证授权。
4. **是否冒充系统、登录、支付或其他品牌？** 应用采用自己的维修协作界面；未设置密码、付款或外部登录表单。身份按钮明确是演示角色切换。
5. **是否存在面向助手的运行指令？** 本包未声明应用 Agent、工具或 skills，也未调用模型；业务脚本包含开发注释和 UI 文本。未以用户输入作为模型指令执行。请按最终源码人工复核。
6. **是否有辱骂或针对个人的措辞？** 本次提交文案和演示角色使用中性业务用语，未发现针对个人的攻击性文字。
7. **审核路径与理由？** **human-review**。首次 unsigned 候选存在文案不一致、真实附件和模型未接通、旧事件迁移和动态幂等尚待完整复验、最新宿主兼容未验收；请人工检查并反馈，不能把本次提交当作已审核或已收录。

### 已知缺口与公开证据

- **真实附件：** 当前候选未完成文件选择、实际字节持久化和摘要校验；`addEvidence` 生成 demo/non-READY 占位，无可读证据时应拒绝完工。
- **真实模型：** 未接入；本次不是 AI 能力已验证的提交。
- **幂等与旧数据：** 动态稳定 key 的完整验证尚未完成；旧 JSONL 事件的备份不等于活动事件已迁移恢复，最新保护修改尚待完整独立复验。
- **授权与身份：** grant 申请、撤销、到期以及生产认证/租户隔离未通过验收。
- **宿主兼容与完整流程：** 旧版宿主存在已记录的开工时序、布局问题；最新版官方宿主和全部 38 业务 / 12 UI 验收未完成。不能从源码推断所有问题均由宿主导致。
- [已知限制](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/KNOWN_LIMITATIONS.md)
- [组件版本来源](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/SOURCES.md)
- [第三轮独立复验（对应之前审查快照）](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/docs/build-loop/RECHECK_NATIVE_B_FINAL_2026-10-06.md)
- [旧演示假 READY 阻断截图](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/screenshots/15-independent-legacy-blocked.png)
- [独立点击结果](https://github.com/Abarm009/zhiliao/blob/8d730569546cb57310944bb299695134df773b9d/submission/2026-10-06-native/check/independent-final-results.json)

赛事源码仓库登记已另行完成：[赛事 Issue #13 登记评论](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5945671513)。本 Issue 是首次 App Hub 候选递交，提交成功与维护者审核、商店收录分别记录。
