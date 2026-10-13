# M6 独立 Review r14

**最终结论：BLOCKED。M6-r12 的人工记录恢复回归 D-M6-03-B2 已经独立原生关闭于冷启加载子项；坏引用整份保护、多引用/来源快照保留、零解析启动、本地签名包一致性和隔离回收均 PASS。D-M6-03-C 原诊断出处隔离的源码缺口已修，动态日志恢复及认证后出处消费无法由本轮白名单和现有观测口判定，不能代签 PASS。本轮未证实新的业务 P1，不因建议或前序 BLOCKED-HOST 判 FAIL。**

- 审查者 / 日期：当前主会话唯一主审，2026-10-14，Asia/Shanghai；无子代理。Router/gpt-6.1-sol 路由无可核验接口，未声称切换；无会话 createdAt/改标题工具，未用当前日期改标题。
- candidate_id / base：**M6-r12-worktree / M6-r11-worktree**；用户指定请求及回交证据与清单、实施报告、GATES 一致，不按文件时间择版。
- HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty 工作树保留。源码 809344 B / 15833 行，SHA256 `72dc9c8d634b84054b2fdb12d91c8e3b29bad6d6ec65349e198e442854170ed7`；bundle digest `1a94e5cc5f571ec2ce76ab71fffb005754ec5c363618f057764387d7f72d53f1`。
- 开始/结束快照：第 1 段冻结、当前工作树、21 场实际 installed/mirror/running 全文件相符；source/manifest/model config/identities/harness/schema/template/宿主/ACCEPTANCE/GATES 在落本轮门禁前全部摘要未变。报告落盘后仅修改 M6 status 和 review*/reviewed* 字段，不覆盖作者候选字段或其他模块。
- 作者报告：`docs/optimization/2026-10-09-desktop/reports/M6_IMPLEMENTATION_r12.md`；清单：`runtime/optimization/2026-10-09/M6/r12/CANDIDATE.json`；上轮独立报告 M6_REVIEW_r13=FAIL。作者 15 场只作参考，本结论用独立 21 场。
- 前置：M5 当前 FAIL / M5-r11-worktree / M5_REVIEW_r15.md，未满足原始整体 PASS 前置。按用户挂账裁决继续 M6 局部重审，未修复/复审 M5 附件业务。D-M2-05、D-M4-03 保留 BLOCKED-HOST，未作为 FAIL/P1。
- 实际宿主：rc.6，`runtime/optimization/2026-10-09/host-rc6/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 `2686e39980a841daa987de7c02f8c7253c1af96ed2c3bad7366568cc7af9c10a`。作者 start-snapshot 的 rc.1 路径为过期元数据，建议挂账，不冒充实际运行版本。
- 已阅读范围：第 1 段实际 AGENTS/CONTEXT/00/01/02/模块/04 模板、r13 缺陷、r12 实施和冻结差异；本段全部独立 summary/result/profile/probes/denials/完整 host.log/MANIFEST、实际包、隔离盘和全部 PNG 结构，6 种独特画面均目视。只复核原缺陷与直接回归，不扩业务。
- 实际运行：驱动于 **01:33:03–01:38:34 +08:00** 沙箱外执行 21 场 / 3 批，均 quit_http、host rc0、CLEAN，无 ABORT。审查方未启动 launcher，也未执行 sandbox-exec/pgrep/osascript 预检。
- 实际证据审计命令：`python3 -B runtime/optimization/2026-10-09/M6/native/review_r2_1659/audit_phase2_r14.py`，rc0，**54842 项一致性检查、0 不一致**。这是证据核对数，不是业务用例通过数。审计器首次误将 loader 在纯人工缓存中补 `source_versions:null` 当不一致；核清既有缺值规范化后修正审计预期并重跑，没有改应用或原证据。
- 模型：21 场 needs_model=false，真实请求 0 次，无 model_proxy_stats/代理文件/模型 endpoint/MM_KEY 注入、无实际402或余额错误，NEEDS_ABRAM=no。合成缓存不算真模型效果或事实准确性证明。
- 合规：本段显式读写限项目、未读秘密/原凭据、未改原业务数据/业务源/harness、无 publish/listing/push/issue/消息/部署。本轮新私钥 0；作者 anchor.key / working.key 已核不存在，删除证据见 E/offline-verify.json。第 1 段曾误读项目外记忆索引，已披露并在阶段笔记留痕；本段未续读。原生 CLEAN 不抹去这一程序偏差。
- 置信度：候选/原生加载/人工恢复/整份保护/隔离回收 **高**；诊断恢复内存、认证后出处、可信完整角色与真实模型流程 **未知**。

## 证据索引与核验范围

路径均相对项目根：H=`runtime/optimization/2026-10-09/M6/native-runs/review_r2_1659_REQUEST_review_r2_1659/`；E=`runtime/optimization/2026-10-09/M6/native/review_r2_1659/`；R=`runtime/optimization/2026-10-09/M6/native/REQUEST_review_r2_1659.json`；N=`runtime/optimization/2026-10-09/M6/native/REVIEW_NOTES_r2_1659.md`；A=E/native-evidence-audit-r14.json；F=E/fixtures-and-expectations.json。
请求 SHA256 `e1bcef9a14696c82ed7c99c8ae22cdf0b9b64f39c74ebbbfa6f3d04d24849856`；summary/MANIFEST 摘要保存于 A 和本轮 GATES.review_summary。

1. summary.request 与 R 完整相同，场景顺序、3 批及每条 summary/result 对应字段一致；**4594 项 MANIFEST**完整文件集合、摘要、路径范围/无链接/无重复均重算。
2. 21 个 profile 按冻结模板和实际目录/控制端口重建，字节及 sha256 全相同。probes.apply rc0、ok=true、外写探针拒且 created=false、5 禁读项均拒、osascript 内核拒执行。只读驱动记录，未自行访问禁读位置。
3. 21 场 pre/post_pgrep 均 rc1、NONE、空 out/err；pgid_members_after=[]，host_returncode=0、quit_http；运行采样完整 argv 未见 osascript。HOME/app-data/cache/log/tmp 全位于各新场目录。原 HOME mtime 不变、Library scan 空只引用驱动记录，不访问项目外检查。
4. **770 项种子文件比较、882 项 actual mirror/installed/running 包文件比较**一致；catalog 齐全，唯一实际 running 包完整等于已验签运输包，无 HOST_DID_NOT_OPEN_APP。运输 manifest 含 integrity，与未 stamp 的工作树 manifest 各自核对，不混称两者字节相同。
5. files_written_in_run_dir 逐项核路径、存在、唯一、排序、数量一致且未达400项截断；21 场总记录 **3802 项**，20 场各181项、reminder_bad_middle 182项。这是按 mtime 统计的文件，不是业务写次数。种子除 state 的所有文件原字节保全，任务/回执/事件仍为空，没有新增已执行业务。
6. 每场完整 sandbox-denials.log 与记录 summary 重算一致。聚合：osascript process-exec 拒192条、443外联拒71条、Metal外缓存拒181条、/dev/dtracehelper写拒42条。采集时间窗口可重复，**不是独立尝试次数，也不是成功外联/外写/自动化**。不放宽沙箱换成功。
7. 全部 host.log 的字节数/tail/markers/digest 标志重算一致。21 场实际加载809344 B作品 view=true、零 `[E]` / ScriptError / parse error / instruction limit / unknown-action / panic，tick_exception_count=0；正常系统小 view 不是作品加载证明。
8. captures 的 path/exists/sha256 全匹配；21 个请求截图全部存在，加 `.part.png` 共 **42 张**，PNG签名/每块CRC/结束与完整长度全核；6 种摘要全部目视，均为2800×1696真实登录画面。没有工作台或缓存正文；三种 `--size` 实际命令成立，但固定外层图尺寸不证明真实客户区布局或150%达标。
9. 21 场 actor=null、selected_task_id空，没有伪造可信 SESSION/grant。人工 phase/device、[]控制与混合缓存正文、manual标记、原序和3项refs原字段完整保留；纯人工载入补 source_versions=null，原缓存仍无该字段且原盘未变，不是模型出处丢失。
10. manual_object_refs / suggestion_missing_second / suggestion_boolean_refs 均整份 kind=none/items=[]，原盘保全；坏项前的好项没有被单独恢复，加载保护 PASS。
11. reminder_bad_middle 整份列表拒绝、m6_followups_dirty/pending_recovery=true，`.recover` 与原文件逐字节相等，PASS保护/备份子项；未认证恢复按钮未执行。pin_marker_bad_binding 缺合法 receipt_id，只证明坏marker和业务盘保全，**不证明匹配回执消费者或真实收藏对账**。
12. 10 个 AI 日志场：两合法对照、六非法诊断、STALE及非法kind均成功启动、原盘保全，但相同 suggestion 缓存都可在未认证boot载入。日志全局没有观测口，未进入认证后的出处闸；**不能把非法/STALE场缓存仍存在判作泄漏FAIL，也不能把它们CLEAN判作出处PASS**。
13. 全部 needs_model=false、代理/密钥占位符与统计缺失符合预期，0次真实模型。没有发生计费错误，不要求 Abram 余额授权。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/本地安装|冻结→已签包→新Store→全包/命令读回|同候选及rc.6、作品确实加载|21场全文件一致、作品view=true|PASS子项|R；H各result/包；A；E/offline-verify.json|
|隔离与回收|profile重建/probes/完整argv/NONE/PGID/denials|只在新场目录、无遗留|21场均满足|PASS；R-M6-02保持关闭|H profile/result/denials；A|
|冷启动/零解析|21种独立冷盘→日志/截图/state|解析/运行无回归|零错误、真实登录渲染|PASS启动子项|H日志/42PNG；A|
|B2纯人工恢复|phase/device无refs＋[]对照→冷启state|保留正文/manual，原盘不变|三场均相符|PASS，关闭r13加载回归|H manual_* state/缓存；F/A|
|B2混合、多引用/B1来源|模型在前＋两人工、三refs/来源→冷启|顺序/每项/来源原字段保留|全部保留|PASS加载回归；producer完整链NOT_RUN|H mixed_model_first/phase_three_refs；A|
|B2坏成员整份保护|人工对象refs/第二建议缺refs/布尔refs|整份未知、原盘保持|符合|PASS保护子项|H三个坏refs场；A|
|C诊断出处源码|恢复/出处/旧成功及STALE分支对照|diagnostic不证明成功/不作废成功，严格非法诊断拒|实现已改，旧枚举及STALE保留|PASS源码子项|main.splash:5442/5452/8775/8816；E/source-traces/r11-to-r12.diff|
|C诊断恢复/出处动态|10日志场→全局结果或认证后消费|合法成功恢复；坏诊断拒；STALE撤销|仅未认证载入/保源，内存与消费未观测|BLOCKED：白名单不提供全局读取/可用可信输入|H各日志场/state；R/schema；N/F/A|
|D02提醒保护/实际恢复|坏中间项→原盘/备份/flags；需点恢复|保护成立、两分支可恢复|保护成立，按钮未执行|PASS保护子项；实际恢复NOT_RUN，可信输入步骤BLOCKED|H reminder_bad_middle；A|
|D04收藏隔离/对账|坏marker→业务盘；需原key/真实角色|不盲改且恢复一致|仅保源负例|PASS保源子项；完整NOT_RUN，可信输入/故障调度BLOCKED|H pin_marker_bad_binding；A|
|三角色/提醒去重/撤权跳回|可信登录→真实同任务→复开/撤权/跳回|持续使用及权限重核|未执行，无可信业务任务|NOT_RUN；具体可信输入/同盘复开/撤权步骤BLOCKED|21场state/PNG；schema/N|
|三真AI链/人工继续|真实建议→失败人工→保存重开|有据、不虚构、不直接写业务|0次真模型，只有人工加载子项|NOT_RUN完整；可信输入步骤BLOCKED|R；H；F/A|
|原生视觉/键盘|三客户区/150%/长文/焦点/滚动|动作与恢复可达|只有登录页；未操作工作台|PASS登录渲染子项；完整NOT_RUN，键盘/放大步骤BLOCKED|42PNG/实际cmd/schema|

## 原缺陷闭合与具体阻塞

|编号|本轮状态与责任|
|---|---|
|D-M6-01 / D-M6-05|保留之前已关的精确子项；未因登录图扩签完整业务/UI。|
|D-M6-02|源码原函数保持；独立坏中间提醒整份拒/备份/flags PASS；实际恢复两分支/保存失败尚未验证。|
|D-M6-03-B1|原来源schema修复保持，三引用/source_versions加载PASS；真实阶段producer/认证后链NOT_RUN。|
|D-M6-03-B2|**r13人工writer无refs恢复回归已独立原生关闭**；phase/device、[]控制/混合顺序/三引用与坏成员保护成立。真实输入→保存→同Store重开仍NOT_RUN，不扩大关闭范围。|
|D-M6-03-C|**原源码诊断准入/成功出处错配已修**；动态恢复、全局标志/认证后消费仍BLOCKED，不能关闭完整安全必需项。|
|D-M6-04|源码不变；坏marker原盘保全PASS，真实收藏隔离/固定key未知结果对账NOT_RUN。|
|R-M6-01 / R-M6-02|本地签名安装/实际全包一致、内核禁osascript、隔离回收PASS子项。|
|A-M6-01～03|继续建议挂账，不因建议判FAIL；过期宿主元数据、固定外层截图尺寸属于证据说明。|

**业务必修 P1：本轮未证实仍需改代码的 P1。** 不凭未认证缓存存在或缺观测编造业务故障；原 r13 两项代码修改已落实，不要求构建方继续无依据重写。

### B-M6-R14-OBS · BLOCKED / 必需证据：诊断恢复与出处消费缺少合规观测

- 文件与行：`app/bundle/main.splash:8775` 恢复函数及 `:5442` 出处函数；`:5736`附近未认证早返，出处分支在`:5770`附近；请求能力以 `driver/harness/request.schema.json` 的 test_actions 描述及实际 R 为准。
- 触发：本轮合法诊断对照、六个非法诊断中间项、同rid STALE、非法kind，冷启后检查出处或恢复内存。
- 实际/预期：全部只有actor=null的boot state和保源日志；AI_REQUESTS_LOG、AI_LOG_CORRUPT不在result/state中，出处闸未触发。预期有直接只读全局结果，或经真实认证后消费得到明确拒绝/可用与绑定证据。
- 原因：现有允许内置launch/tap/capture动作不能读任意脚本全局，固定宿主type/key已知不实现，本次禁止osascript/辅助功能/ui_actions；没有可验证的可信输入通道。harness本轮没有ABORT；不是sandbox-exec rc71/pgrep rc3阻断。
- 影响：D03-C动态安全必需项无法判PASS/FAIL，硬2/5的核心依据消费未闭合。**这是测试观测阻塞，不是已证明应用仍有P1或实际泄漏。**
- 证据：H十场的result/state/原ai_requests.jsonl/host.log、R（无ui_actions、needs_model=false）、F/A、源码未认证早返与出处调用条件。各非法场缓存仍在不构成闸被绕过的实证。
- 解阻最小条件：提供在同候选rc.6及隔离目录内、遵守本次白名单的既有宿主只读观测/可用可信输入能力；或驱动通过已允许内置动作完成真实认证后消费并交回完整绑定证据。不得改业务代码加产品入口，不伪造SESSION/grant，不改计费/公开发布。若现有能力确实无路，维持BLOCKED，不继续空跑同类登录图。
- 验证方式：直接观察合法成功＋NO_SERVICE对照恢复、六非法诊断整份拒且持久原盘保全、同rid STALE撤销；同时核当前主体/project/task/版本/refs/source_versions。操作后的明确结果才可闭合，不以“不报错”代替。

三角色、真实人工输入/恢复按钮/收藏与模型按钮、键盘/150%、同Store跨进程复开、运行中撤权/精确写故障与飞行交错，同样只对白名单确实无法执行的具体步骤标BLOCKED；其余没有运行的流程记NOT_RUN。没有缺额外 Abram 授权的事实，NEEDS_ABRAM=no。

## 全部硬验收及相关既有用例

|硬验收|本轮精确结果|
|---|---|
|1 三角色持续追踪/搜索/收藏/重登/项目|NOT_RUN完整；可信输入步骤BLOCKED，原代码未改。|
|2 三真AI链/失败人工出口|PASS人工加载及C源码子项；C动态出处BLOCKED；三真链及真实手工输入完整链NOT_RUN。|
|3 提醒恢复/去重/旧作业/跳回|PASS坏盘整份保护/备份；实际恢复/去重/旧约/跳回NOT_RUN；同盘复开/撤权调度具体步骤BLOCKED，后台常驻未证实。|
|4 视口/放大/键盘|PASS登录原生渲染；完整工作台客户区/150%/键盘NOT_RUN，具体键盘/设置步骤BLOCKED。|
|5 输入/选择/滚动/恢复一致、P0/38/12归属|PASS人工schema及坏成员保护回归；C动态出处BLOCKED；其余完整跨模块NOT_RUN，原标准/历史归属保留。|

|编号|本轮精确复核|
|---|---|
|G0-F|坏提醒整份保护/备份PASS子项；真实后台/通知/去重/跳回NOT_RUN。|
|T17|NOT_RUN断线重连不二次写；冷启不代替断线业务。|
|T18|未认证截图无正文PASS负例；可信可见列表/事件/搜索/附件权限NOT_RUN。|
|T23|提醒保护PASS；同Store重开/通知去重/旧约取消NOT_RUN，复开调度步骤BLOCKED。|
|T25|C源码隔离PASS子项、动态消费BLOCKED；真模型不得虚构/写任务/改角色NOT_RUN。|
|T26|人工writer形缓存恢复PASS子项；实际模型失败/人工填写保存全链NOT_RUN。|
|T28|签名包启动/实际包读回PASS子项；真实同task动作/权威回执/同盘重开NOT_RUN，复开步骤BLOCKED。|
|T29|真实grant撤销/退出/到期/跳回NOT_RUN；运行中撤权与可信消费具体步骤BLOCKED。|
|T30|真实收藏隔离/重登/version不变NOT_RUN；坏marker保源只是负例。|
|T33|NOT_RUN真实新描述泛化，0模型不代签。|
|T34|三refs/source_versions保留和坏refs整份拒PASS子项；C动态出处BLOCKED；真引用事实准确性NOT_RUN。|
|T35|既有来源/版本/过期闸保持；飞行交错NOT_RUN，调度步骤BLOCKED。|
|T36|未改内核或适配白名单；真实工具链NOT_RUN。|
|T38|当前候选/宿主/请求/数据冻结及运行一致PASS子项；真模型固定组复跑NOT_RUN。|
|U01|三角色首屏当前任务/下一步NOT_RUN，42张图都未登录。|
|U02|真实草稿编辑/补歧义/人工继续NOT_RUN，前序挂账保留。|
|U03|可信角色事实/权限/独立验收NOT_RUN，不扩M5业务。|
|U04|真实预约/改约冲突/过期NOT_RUN，原精确结论保留。|
|U05|可信设备位置/服务空间/来源详情UI NOT_RUN。|
|U06|进度/完工/退回与历史附件NOT_RUN，前序挂账保留。|
|U07|重复/丢响应/离线/冲突/固定key对账NOT_RUN；精确故障调度步骤BLOCKED。|
|U08|人工加载/坏引用保护PASS；C出处动态BLOCKED；实际恢复出口/长文/附件失败等完整NOT_RUN。|
|U09|三size实际启动PASS子项；工作台客户区/150%主动作可达NOT_RUN，不以2800×1696外层图代签。|
|U10|键盘焦点/对比/非单色状态完整NOT_RUN；键盘/放大设置步骤BLOCKED。|
|U11|真宿主登录渲染PASS子项；真实工作台输入/滚动/面板稳定完整NOT_RUN。|
|U12|同候选原生证据/权威加载PASS子项；可信完整2–3分钟演示NOT_RUN。|

## 判定

- **最终结论：BLOCKED。** 精确范围是 M6-r12 对 r13 两项残余及直接回归的独立重审。人工恢复冷启回归关闭；诊断源码缺口关闭于源码范围，动态安全边界缺合规观测，不给“基本通过”或整体PASS。未发现新业务P1，不以建议/缺完整演示/前序BLOCKED-HOST判FAIL。
- 必修代码：本轮无新证实项；构建方保留现有最小修复与所有安全拒绝/保源门禁。优先补已有能力的运行证据，不新增功能、入口、页面或字段。
- 解阻条件：见 B-M6-R14-OBS；在同候选、同rc.6、隔离盘上获得合规真实认证消费或只读恢复内存结果。原生环境已运行，不再用agent沙箱rc71/rc3作理由。公开发布、额外身份/provider裁决与计费切换都不是本轮解阻条件。
- 受影响前序回归：21场零解析/零运行错误确认当前候选启动不回归，M5附件/M2–M4业务未复审；原挂账来源保持。
- 门禁：`docs/optimization/2026-10-09-desktop/GATES.json` 仅更新M6 status及review*/reviewed*字段，review_report指本报告，旧审查字段归档review_history，完整更新前备份 E/GATES.before-r14.json。作者候选/实施字段和其他模块不改。
- 既有验收台账：`docs/build-loop/ACCEPTANCE.json`未改，原P0/38业务/12UI及历史后端来源保留；本报告/门禁仅增加本轮原生精确子项，不把它们替代全量历史结论。
- **不允许进入下一模块；留在M6补证/解阻，不执行M7。**

STATUS=BLOCKED
NEEDS_ABRAM=no
