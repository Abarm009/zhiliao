# 官方资料本地快照

用途：只读参考、版本定位及后续构建准备。不是我们的应用源码，也不随应用 bundle 提交。

## 2026-09-29 当前参考版本

|仓库|当前检出完整SHA|提交时间（仓库原时区）|
|---|---|---|
|OctoSense-App-Hub|`6741dea8d6b5e1a6062dfc23ae6b0d4240bcc747`|2026-09-28T17:20:10-07:00|
|OctoScript-App-Design-Flow|`9586a12044873267dddc39c3b56d7e94f3c6abfe`|2026-09-28T17:20:16-07:00|

更新前检查工作树干净，抓取main后检出上述固定提交，当前均为detached HEAD且工作树干净。原本地main及下列9月27日提交保留。未修改上游内容，未运行安装器、构建、原生应用或模型。

开发指南当前锁定Octoscript-Makepad `b33f494b963759088edf5785fc626cb8593818ee`；相关Makepad `4fdcfccc127b700f1fc01aa1a5488af938dd7f3d`、Octoscript `68f6a9df55692b5d8ef8873a12721e279a3f40d6`只是版本记录，未检出/验证。Shell检查版本为`a5d847a2a5091c1274d68dd0de1f43c8b0215bf1`，其锁定Hub为`e8601b80ce104db2e48208094714bdcffdce6b5a`；与此处独立Hub不同，不能自动互换。没有新增Shell完整克隆，只读取10个固定版本公开文件；文件URL、字节数及SHA-256见[源码证据索引](course2-source-evidence.json)。

最新结论见[14课程 #2与制作发布核对](../docs/implementation/14_COURSE2_LATEST_GUIDE_REVIEW.md)。尤其注意：Design-Flow入口中的AI状态落后于Shell源码，不能把该README的9月27日判断视作9月29日实际能力。

## 2026-09-27 历史快照（以下为当时记录）

|仓库|本地目录|2026-09-27检出的完整SHA|提交时间（仓库原时区）|
|---|---|---|---|
|[OctoSense-App-Hub](https://github.com/OctoSense-org/OctoSense-App-Hub)|`OctoSense-App-Hub/`|`46d67e51b62827a1224b1aacddc2a7b9e69185fc`|2026-09-26T19:01:18-07:00|
|[OctoScript-App-Design-Flow](https://github.com/OctoSense-org/OctoScript-App-Design-Flow)|`OctoScript-App-Design-Flow/`|`7ddf8a16ab30bf8e095d55e5ceebe0478c1a8386`|2026-09-26T19:23:47-07:00|

两者均从公开仓库以 `--depth 1` 克隆，分支main；本轮未修改仓库内容。第二个是Hub直接指向的官方开发流程与脚本API资料。开发流程仓库约642 MiB，含大量上游设计证据，不要把它复制进作品。根目录忽略规则排除这两个参考克隆；本说明保留版本来源，迁移时可按上表重新取得。

本轮未运行上游安装器、构建、原生应用或模型。Makepad等三个同级运行时目录尚未准备；开发流程锁定的Octoscript-Makepad版本为`99c1e5ee7925060ced59c66d6f8763c22217e4ad`，不表示已经检出或验证。后续固定各运行时完整SHA、工具链和锁文件，再构建。

评审结论见[13 Hub提交规范与架构差异](../docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md)。更新参考仓库前检查工作树，保留本次SHA及评审记录；不要自动追随main覆盖已冻结交付依据。
