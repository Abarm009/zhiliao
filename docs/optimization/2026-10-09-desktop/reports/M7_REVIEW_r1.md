# M7 独立 Review r1

- 最终结论：**FAIL**；候选 `M7-r1-worktree`，base `M6-r2-worktree`。置信度：字节/准入/安装实测**高**；真实桌面/业务/模型结果**未知**。
- 审查者/日期：本主会话唯一独立审查方，2026-10-10 Asia/Shanghai。未派子代理。工具不提供主会话模型路由、自身 createdAt 或标题设置接口，无法确认 Router/gpt-6.1-sol；未声称完成切换或标题设置。
- 作者报告：`reports/M7_IMPLEMENTATION_r1.md`；交接清单 `runtime/optimization/2026-10-09/M7/r1/CANDIDATE.json`。仅此一个M7交接候选，非按文件时间猜版本；没有上一轮M7 Review，本轮首审。
- 被审HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty工作区；主源SHA-256=`5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db`，283910字节。
- 最终包：`runtime/optimization/2026-10-09/M7/r1/release/octosense-repair-0.1.0-c/`，17文件；官方工具在独立副本stamp所得BLAKE3=`ce493c56648e46b02dd4ae6e4a0a784a60fcd2f01f5b6ad58faf38755f64e404`，与交接manifest一致。
- 起止快照：17文件内容/大小一致，工作区主源与交接主源一致。审查另存 `results/start-status.txt`、`start-dirty.diff`、全部最终文件/宿主SHA；未reset/stash/修改业务代码。
- 前置：M6独立r2为FAIL，D-M6-02/03/04仍OPEN；按本次Abram 13:54挂账授权继续M7，**不单因M6未PASS拒收**，不改前序状态。
- 宿主：指定launcher octosense SHA=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`，kernel SHA=`a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。旧standalone card-host与此launcher不同，不混称。旧Hub、新固定Hub、Store探针哈希见candidate-audit。
- 已读：AGENTS；M7 CONTEXT；00/01/02/M7/04；作者报告、候选、脚本及结果；M6 r2 Review；既有05/09/10验收定义、ACCEPTANCE；发布入口/隐私/许可/来源；10-08旧回执；项目内固定官方准入/Store源码。依CONTEXT复用基线，不扩审前序业务。
- 已运行：干净隔离预检；两版Hub check；独立副本离线sign-manifest/catalog、verify、官方Store install_staged/重建后may_run/篡改拒绝/恢复；作者静态cases独立重放33/33及23/23。
- 未运行：launcher、实际UI、业务命令权威回读、正常/退回/失败/重复/业务重启、真实模型、实际scan审阅及外部动作。56条静态检查不是64项总验收；没有重跑作者M6的188条，更不把作者计数当独立M6 PASS。
- 证据根：`runtime/optimization/2026-10-09/M7/review-r1/`。测试HOME/CFFIXED_USER_HOME/TMPDIR/XDG data/config/cache/OCTOSENSE_HOME/app-data/Metal cache全在此；两私钥已删除。未联网/publish/push/Issue/消息/provider或身份配置。开始时按上级记忆流程做过一次项目外记忆索引只读检索；没有项目外写入，其后项目审查读写限定项目内，记录此读取范围例外。

## 必需检查

以下证据路径相对本轮证据根。

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/字节|逐文件SHA、官方stamp独立副本、核宿主哈希|可定位且材料一致|源码及官方digest成立；附带INTEGRITY的manifest SHA/size过期|FAIL D02|candidate-audit.json、local-store-validation.json、end-audit.json（均在results）|
|硬验收1 全量门槛证据|逐项对照原64编号、重放静态cases|不以静态/旧版本代替实测|报告改写G0/P含义，运行没有实证|FAIL D03；运行BLOCKED/NOT_RUN|results/original-acceptance-definitions.json、author-static-replay.json|
|硬验收2 同候选正常/退回/恢复/重启/模型|先执行隔离/清理预检|安全后台启动目标launcher实操|sandbox rc71、pgrep rc3，未启动|BLOCKED B01|results/preflight-and-admission.json|
|硬验收3 包布局/秘密/图/描述|清点17文件、旧图哈希、校验摘要|全部材料对应最终字节|无开发垃圾/私钥入包；六图全旧，已披露但非同版本；摘要失配|FAIL D02；当前图BLOCKED|results/candidate-audit.json、final INTEGRITY/listing|
|硬验收4 准入/干净启动|两版check及本地catalog Store验证|准入合规、启动可复现|check均拒绝；Store安装/重建/篡改/恢复通过；launcher未跑|FAIL D01；启动BLOCKED|results/preflight-and-admission.json、local-store-validation.json|
|离线签名隔离与删除|只在审查副本生成两key，finally销毁|当前digest，sandbox内有效|verify/安装rc0，篡改rc1，恢复rc0；两key已删除|PASS（功能子项）|local_store.py、results/local-store-validation.json、end-audit.json|
|硬验收5 四种交付状态|核当前清单与历史回执版本|本地/发布/赛事/收录分开|本候选无外部回执；旧Issue仅属于0.1.0-b|PASS（状态区分子项）|作者CANDIDATE；submission/2026-10-08-hub/RECEIPT.md|
|旧服务/连接器/边界|独立重放扫描、清点包|无意外依赖和绕过|未见Python服务/已知HTTP调用；运行绕过检查没跑|静态子项PASS；完整T24/T27 BLOCKED|results/author-static-replay.json、candidate-audit.json|

## 相关既有用例逐项复核

原定义取ACCEPTANCE.json并对照05/09/10；“历史”仅为原台账状态，不认可其适用于M7。BLOCKED/NOT_RUN是当前实证状态，不把前序全部挂账重新拉成本轮必修。

|编号|原定义|原台账历史|本轮结论|实际范围/证据|
|---|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|PASS|BLOCKED|源码/host/官方digest已核；真实启动B01 BLOCKED，摘要材料D02失配。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|BLOCKED|identities为demo registry；可信身份/独立会话未跑，M2挂账。|
|G0-C|唯一事实源、原子一致性、并发与恢复|PASS|BLOCKED|任务事务/原子性/真实并发/恢复未跑；Store目录重建不代替业务恢复。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|BLOCKED|原定义真实附件；实际写入/回读/归属/恢复未跑，不能用隔离目录代替。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|BLOCKED|提醒/官方意图视图未跑；M6 D02挂账，前台检查不等于后台恢复。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。 M6 D03/D02/D04分别仍FAIL，仅保留挂账、不在本轮关账。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|NOT_RUN|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。 M6 D03/D02/D04分别仍FAIL，仅保留挂账、不在本轮关账。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|BLOCKED|包无Python/Web服务/已知HTTP调用静态子项成立；旧runner绕过写边界实测未跑。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|PASS|BLOCKED|manifest仅storage且已知调用扫描为空；本用例本地独立完工验收部分未跑。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|FAIL|BLOCKED|官方Store安装/重建子项PASS；实际同task_id操作/回读/重开未跑。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|FAIL|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。 M6 D03/D02/D04分别仍FAIL，仅保留挂账、不在本轮关账。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|PASS|BLOCKED|B01：当前launcher未启动；本候选实操/权威回执/失败恢复未测，历史证据不升级为M7 PASS。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|BLOCKED|旧配对可显式版本化替换，授权安全目的不能删；现无原生替代链实证，不默认N/A/PASS。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|NOT_RUN|真实模型及对应建议/故障链未调用，enabled=false；静态probe不能替代。前序相关缺陷挂账。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|NOT_RUN|BLOCKED|B01：当前原生UI未跑；旧六图字节与当前主源版本不对应，不能证明本项。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|NOT_RUN|当前字节2–3分钟真实操作/权威结果/失败或空态演示缺失，旧图不代替。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|PASS|BLOCKED|正常/退回/重开业务链均未跑；stamp/Store不代替。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|PASS|FAIL|D02最终checksum材料失配；作者未存完整dirty diff，本轮另存定位；干净启动B01 BLOCKED。|
|P03|最终包准入check及实际scan审阅通过|PASS|FAIL|D01两版check REFUSED；实际scan独立审阅NOT_RUN；Store子项PASS。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|PASS|BLOCKED|当前截图/演示未跑；旧图已披露但不同字节；来源/隐私/许可已读，A02建议挂账。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|PASS|FAIL|D02摘要失配、D03原编号含义被替换；前序缺陷依授权挂账，不伪造全量实证。|
|P06|固定公开源码与Hub Issue实际递交回执|BLOCKED|NOT_RUN|M7 0.1.0-c没有外部回执且本轮禁止动作；保留GATES external原UNASSESSED。|
|P07|维护者商店收录结果|BLOCKED|NOT_RUN|M7 0.1.0-c没有外部回执且本轮禁止动作；保留GATES external原UNASSESSED。|
|P08|赛事正式提交入口回执|BLOCKED|NOT_RUN|M7 0.1.0-c没有外部回执且本轮禁止动作；保留GATES external原UNASSESSED。|

## 缺陷

只以下3项列P1必修，均阻断M7可复现、材料一致发布准备。前序业务缺陷继续挂账。

### D-M7-01 / P1 / 必修：最终包准入失败，复建材料不完整，Store成功被当作check成功

- 文件行：M7实施报告:127、:131、:132；`runtime/optimization/2026-10-09/M7/r1/scripts/m7_release_stage.py:24`、:41；最终包`LICENSE:1`、`PRIVACY.md:11`、`SOURCES.md:8`、`main.splash:3584`。
- 触发：对交接原目录分别运行旧Hub和固定r7 Hub的`check <STAGE> --allow-unsigned`。
- 实际/预期：均rc1。旧版四条拒绝：LICENSE无扩展名、PRIVACY/SOURCES文档URL、main.splash注释越界路径；新版两条拒绝：LICENSE、注释。报告只写“仅历史注释问题”不准确，LICENSE等由M7新增。预期最终包通过所选适用准入，失败完整登记；不得把Store功能PASS等同CLI gate PASS。
- 根因：只看日志尾部一条；混同安装策略/摘要/签名验证和全部gate检查。官方client.rs:421的install_staged不是CLI完整gate。stage脚本只覆盖6文件/六图/INTAKE，没有生成LICENSE、PRIVACY、SOURCES，不能从空目录复建已交接17文件。
- 影响：核心包装准入/可复现性不成立；离线Store自签安装通过没有消除内容拒绝。
- 证据：results/preflight-and-admission.json完整stdout；local-store-validation.json（安装PASS但signed_check rc1）；stage脚本。
- 具体改法：构建方固定Hub/launcher版本，只修包装和说明；许可用合法后缀如LICENSE.txt，来源/隐私放发布材料外层或采用所选gate合法表达；必要非行为注释清理单列diff，不改业务逻辑。复建脚本在空隔离目录生成全部确定文件；分别记check与Store结果。沿已有授权本地catalog，不publish，不再申请离线签名授权。
- 验证：空目录复建全文件一致；固定工具check合规；新digest重新安装/Store重建/篡改拒绝恢复/删key。若采用替代准入标准，明确依据，不能把自签Store接受写成官方公开准入通过。

### D-M7-02 / P1 / 必修：冻结后的校验清单过期，SHA-256被叫作BLAKE3等价

- 文件行：`m7_integrity_recompute.py:36`、:64、:68、:76、:88；`m7_sandbox_sign.py:67`；最终`INTEGRITY.txt:3`、:4、:13（脚本均在M7/r1/scripts下）；CANDIDATE的staging_integrity字段还占位。
- 触发：实际SHA-256/大小对比INTEGRITY和results/integrity.json；独立副本官方stamp。
- 实际/预期：记录manifest 202字节/SHA `7e442753...`，最终249字节/SHA `c34931f51024bda31e6729079a2daf6e616493d0d25b064921623bb12ee190e1`；INTEGRITY声称bundle_blake3=`fbf9df3a...`，实际及独立stamp=`ce493c56648e46b02dd4ae6e4a0a784a60fcd2f01f5b6ad58faf38755f64e404`。清单只含6文件，缺其余11文件。应最终字节全部覆盖，真实BLAKE3与SHA各写各的。
- 根因：先算manifest再改manifest，后续stamp再次改字节；六文件拼接SHA与官方目录BLAKE3算法/范围不同。未在最后写入后freeze，自身入包摘要还有顺序自引用问题。
- 影响：发布证明与最终包不一致。官方manifest digest自身正确，不意味着附件清单也正确。
- 证据：results/candidate-audit.json的recorded_integrity_mismatches；local-store-validation.json的author_digest_matches=true；最终INTEGRITY及作者integrity.json。
- 具体改法：删除SHA→BLAKE3等价字段；确定所有包内容后官方stamp、离线签名、freeze；完整SHA/size和真实digest放包外证明目录，覆盖每个文件避免自引用；同步真实HEAD/dirty diff/未跟踪源码内容清单、host/toolchain，不动业务代码。
- 验证：两份空目录重建一致，逐文件零失配；任意后续字节变化必须触发freeze检测失败；审查起止快照一致。

### D-M7-03 / P1 / 必修：总验收改变既有编号含义，静态全绿被记成核心门槛PASS

- 文件行：M7实施报告:148–:160（每项各行）；`m7_acceptance_run.py:118`把已知REFUSED当成功断言；最终listing.json:28称真stamp写在过期INTEGRITY（各文件位于已定位r1目录）。
- 触发：原台账G0/P标题对照作者映射；重放作者cases。
- 实际/预期：33/33及23/23确为静态PASS，但只查路径、字段、64hex及日志。G0-D“真实附件”改成“隔离生存”；P01成功/退回/重开变“干净staging”；P02源码依赖/启动变“离线签名catalog”；P03准入/实际scan变“模型接通”；P04当前截图/演示/材料变“不污染宿主”。缺原生/scan证据仍硬验收1/3/4 PASS。预期原64项含义不变，静态结果明确为子项，缺运行项BLOCKED/NOT_RUN。
- 根因：私有M7静态检查替换原用例目的，将“诚实披露未测”误当“硬验收成立”。作者M6 188条也不能取代M6独立FAIL结论。
- 影响：最终发布总验收无法判读实际完成范围，属于M7核心证据质量问题。
- 证据：results/original-acceptance-definitions.json、author-static-replay.json及本报告逐项表；M6_REVIEW_r2。
- 具体改法：只改验收材料/生成逻辑，逐项沿原含义写实测、子项、未测及前序挂账来源；自定义静态检查用M7独立编号；不得因计数全绿把check拒绝或未跑原生链升为PASS。没有要求在M7重写全部前序业务。
- 验证：64编号/标题逐个一致；每项PASS有同candidate/host的真实权威证据；缺证据项不能被汇总数字覆盖。

## 阻塞与建议

### B-M7-01 / BLOCKED：当前无法安全运行最终launcher并取得同版本桌面证据

- 定位：`CONTEXT_M7.md:51`、`app/README.md:74`–:77；本轮isolation.sb、results/preflight-and-admission.json。
- 最小复现：`/usr/bin/sandbox-exec -f <review-r1/isolation.sb> /usr/bin/true`返回71（sandbox_apply Operation not permitted）；`/usr/bin/pgrep -fl <指定launcher Contents/MacOS>`返回3（Cannot get process list）。两条本轮独立重跑。
- 根因/实际/预期：执行环境不能施加写隔离和枚举清理；HOME重定向不能单独保证native所有缓存都在项目内。预期可安全后台启动、立即关闭、核窗口，再实操。当前真实UI具体表现未知，不编造崩溃或裁切。
- 影响/解阻：即使D01–03修完，也不能自动PASS。换到可执行隔离、禁网络、枚举/结束进程和检查窗口的测试环境，先通过相同预检，再后台启动用户指定launcher，所有HOME/app-data/log/cache在M7新隔离根。正常/退回/失败/重复/业务重启、真实中文/视口/权威回读存证，立即kill核新增窗口清零。此动作已经授权，不需Abram再批准；不能换旧card-host冒充目标launcher。
- 本轮未启动launcher，未用--help，未创建宿主窗口；旧有窗口因枚举失败**UNKNOWN**，不声称桌面无残留，不盲杀他人不可定位进程。

### A-M7-01 / P2 / 建议挂账：历史入口和授权摘要过时

- 文件行/触发：根README:42、:62仍“原生验证通过+待递交”，头部:5–:7却已递交/未完整验收；app/README:5的staging链接多一层`../`；CONTEXT:51称用户禁止后台启动。
- 实际/预期/影响：读入口会遇到冲突状态、坏链接及旧授权解释；应分历史版本，当前说明一致。listing已披露旧图/未通过，故不因历史段落另加P1。
- 根因/改法：新披露叠在顶部，旧章节未同步；仅修当前发布入口、相对链接（app目录到runtime用`../runtime/...`）与授权摘要，旧文保留来源。不必等push授权才修本地说明。
- 验证：从app/README解析链接确实存在；当前章节状态一致，launcher说明写清已授权后台测试、预检失败才BLOCKED。

### A-M7-02 / P2 / 建议挂账：来源/隐私存在未证实断言，脚本异常清理不保证

- 文件行/触发：最终SOURCES:9称旧工具目录`.git`已pin，但实际目录不含.git、10-08回执也披露此来源缺口；PRIVACY:8称视频有旁白/原创配乐，本候选无同字节媒体证据；SOURCES:34称finally清理，但m7_sandbox_sign:99只在正常路径unlink，没有finally。
- 实际/预期/影响：旧媒体和构建推测混入材料，应标历史/未知；当前私钥实际已删除，未观察泄密。
- 根因/改法：复制历史文案；补可核构建/发行来源，媒体声明绑定真实媒体和版本，未知直接写未知；key清理使用try/finally，无需业务改造。
- 验证：来源可本地回读，媒体可定位；隔离注入CLI失败后私钥目录仍为空。

## 判定

|对象|结论|精确范围|
|---|---|---|
|M7本地发布准备|**FAIL**|3项包装/冻结/总验收口径P1；真实原生运行另BLOCKED|
|M7外部发布/Hub递交|**NOT_RUN**|0.1.0-c无回执，未执行外部动作；10-08旧0.1.0-b Issue回执仅历史本地读取，未联网刷新|
|赛事正式提交|**NOT_RUN**|无本候选赛事回执|
|维护者商店收录|**NOT_RUN**|无本候选收录证据；离线catalog/Issue不等于收录|

- 本轮安装路线实证可行：当前digest安装/Store重建rc0，篡改rc1，恢复rc0；两私钥已删，keys目录为空。Store重建不等于业务重启，更不是目标launcher运行。
- 受影响先前门槛：核M6 base源码一致及当前安装副本一致；M7没有改业务源，不扩审M0–M6；其历史与缺陷保留，不宣布关闭。
- 门禁：只写GATES的M7 status/审查字段/审查历史，保留作者字段与其他模块/external_delivery；ACCEPTANCE不改，原定义历史保留来源。
- 本模块修复交接：D01→D02→D03定向修包装/冻结/报告；B01预检通过后取得同版本目标launcher实证；重新freeze新candidate_id，再独立复验受影响项。不给下一模块入口，不执行下一模块。
- NEEDS_ABRAM=no：本地路线已实证可行，离线签名已授权；当前代码/材料修复和运行环境缺口不需要新授权。真实provider/身份来源保持前序挂账，本轮未配置，未确证修这3项必须新增此类配置；没有要求公开发布。

STATUS=FAIL
NEEDS_ABRAM=no
