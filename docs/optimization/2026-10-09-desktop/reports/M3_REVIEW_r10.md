# M3 独立 Review r10

**最终结论：BLOCKED。** 正式候选 M3-r8 的四场独立原生冷启动均渲染工作台，解析/运行错误为0；原文、确认意图和动作键保留，空历史不损坏，坏历史及有效备份保全，未认证的伪主体不能获得权限。上一轮 D-M3-04 的来源默认版本自拒分支已修复。但固定宿主明确拒识 `type:` / `key:`，真实输入、三组 MiniMax 建议、展示/采纳交错及 AI/手工合法确认回读仍未执行，核心功能没有足够真实证据，不能 PASS。没有以建议项判 FAIL，也没有以 CLEAN 代签业务成功。

## 审查对象、前置与实际范围

- 审查者/日期：本主会话唯一独立审查者，2026-10-12，Asia/Shanghai，无子代理；未改业务代码。无法核实主会话实际 Router/model，未冒称指定模型已切换；没有 thread createdAt/标题写入工具，未冒称完成命名。
- candidate_id/base：**M3-r8-worktree / M3-r7-worktree**；HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty。作者报告 `reports/M3_IMPLEMENTATION_r8.md`，清单 `runtime/optimization/2026-10-09/M3/r8/CANDIDATE.json`。按用户提供的构建证据关联定位，未按mtime选版。
- 冻结main **552591 B**，SHA256 **cc193cf0a5015d8475167403a125def3a183efb17dd13336453de47f4d0fe7e8**。四项清单对象与工作树一致；原生每场mirror/installed/唯一.running资源与本轮签名运输包逐字节相同。
- 包digest **fbcb68672e3c1fa85f48cce4667303c5df562c73dc8c27b00eaa4c8d8370e4f0**。本轮复用用户已授权的隔离离线签名包，不公开发布。实际修复比较基线为上一轮r9的0fb141f9诊断快照；差异 E/r9-to-r8.diff，原tracked差异 E/tracked.diff，未把共享改动误归为本轮新增。
- 固定宿主 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness SHA256 **12e3c5901760a5e03eac841609de37a68bd10114ba269bbb4014cc3cbb1b11d9**。
- M2前置仍 **FAIL / M2_REVIEW_r10**，没有已接受PASS；该报告运行对象是M2-r8，GATES作者字段仍M2-r7，二者不混记。按用户前序挂账裁决继续M3本轮局部审查，不自动把M2改PASS。
- 独立请求 `M3/native/REQUEST_review_r2_0937.json`，SHA256 **2a1a333ef6b26888fe64032d11ffddfad9c75435aad03b442e0a0ef225ac5244**。驱动沙箱外执行 **10:01:33–10:02:56 +08:00**；四场CLEAN，无ABORT。
- 第1段读取实际AGENTS、CONTEXT、00/01/02/M3/04、r8交接及作者证据、r9原缺陷、M2前置与相关G0/T/U定义；第2段核全部summary/result/profile/probes/完整日志/denials/MANIFEST、业务盘与所有PNG摘要，并目视全部3种不同PNG内容。只复核原D01～07及直接受影响回归。
- 实际执行：第1段审查材料准备和请求校验；驱动四场原生；第2段 `python3 runtime/optimization/2026-10-09/M3/native/review_r2_0937/audit_phase2.py`，rc0。审查方没有自行启动launcher/harness、sandbox-exec/pgrep预检、--help、osascript/辅助功能或其它UI自动化。
- 真实 MiniMax调用本轮 **0**；模型代理未启用。未读取provider secret或真实明文凭据，未修改原业务数据。历史作者Python3次是历史来源，不代签本轮原生，后续调用前须核总账≤10。
- 审查起止：写门禁前13个保护输入、96个seed/mirror均未变化。门禁改动另存前态并核仅M3审查字段变化。

**H/**=`runtime/optimization/2026-10-09/M3/native-runs/review_r2_0937_REQUEST_review_r2_0937/`；**E/**=`runtime/optimization/2026-10-09/M3/native/review_r2_0937/`；**A**=E/native-evidence-audit-r10.json。以下源码行均指E/source.main.splash，不能套用旧r7/r9行号。

置信度：版本、隔离记录、日志及盘面、高；D04精确源码修复、高；真实模型效果、可信登录后编辑/确认及交错动态结果、未知。

## 必需检查

|检查|独立操作/期望|实际结果|判定/证据|
|---|---|---|---|
|候选/宿主一致|核请求、清单、seed、manifest及三份运行资源|643条MANIFEST匹配，13保护输入/96seed未变；各场资源对应cc193cf0/fbcb|PASS，A及保护/seed清单|
|隔离与回收|逐场profile/probes、环境路径、进程组和退出|probes.ok=true，pre/post NONE，pgid_members_after=[]，quit_http/rc0，CLEAN|PASS，限驱动记录范围；各result/profile|
|原生冷启动|新原文与四种隔离盘；日志零错误、业务根可见|四场552591 B view=true，0 parser/0运行错误，工作台可见|PASS，H各host.log/frames；D01原诊断已消失|
|原文/意图恢复|比seed与盘，含多设备/未知空间/恶意原文|四场原文、confirm_intent_id及action_keys原值保留，tick_exception_count=0|PASS磁盘/错误子项；登录后可编辑控件恢复NOT_RUN，D02|
|空/坏历史恢复|空字符串、[]、好坏好events+有效bak|空历史原字节保持；坏主/bak均保持，bad_lines复制原主，state写冻结|PASS盘面保全子项；完整可见恢复出口NOT_RUN，A/H-corrupt|
|主体/权限负例|伪saved经理+跨项目DRAFT+假设备/来源，无SESSION|actor清null，task/actions/events不变，图任务不可见|PASS此未认证负例；不是实际恶意模型返回，A/H-forged|
|硬1：真实三组建议|现场A/B/C及同义句，追问/多候选/无历史不编造|只有预存原文；type/key明确unknown；0模型调用|NOT_RUN；真实输入触发BLOCKED，B-M3-01|
|硬2：AI确认|合法来源→编辑→人确认→M2 final/事件/回读/重开|D04源码分支已修复；没有AI提交或final回执|AI路径NOT_RUN；入口控制BLOCKED，D04/D05|
|硬2/4：手工确认|无模型手工补齐，独立核M2权威链|未成功登录/填写，0新增OPEN，0成功confirm回执|手工路径NOT_RUN；0 OPEN只是未认证负例|
|硬3：展示/采纳失效|A请求期间键入B，迟到A；展示后上下文漂移再采纳|守卫源码保持，未发生真实交错|BLOCKED于白名单真实输入/返回/途中控制，D03|
|硬4：恶意/错误返回|假设备、越权项目、非法status/角色、恶意原文、格式错误/失败恢复|恶意seed只检冷开权限；不是模型返回；手工兜底未执行|NOT_RUN；不虚构攻击已拒，D04/D06/D07|
|硬5：键盘/取消/重试|原生可编辑表单与错误恢复、provider元信息|unknown type/key；图未登录态；无provider结果|BLOCKED真实输入控制；业务动态NOT_RUN，B-M3-01|
|受影响M2回归|原文/意图/key/空历史/坏历史/未登录共享边界|以上测试子项成立；M2其它提交/幂等/并发未执行|局部PASS，不代签M2整模块|

## 原生证据逐项核对

审计 **2202项证据一致性检查，0失败**，不是2202个业务用例PASS。

1. **summary/result**：请求结构、四场ID/目的、size/动作、seed/digest与实际cmd对应。时长19.32～19.34秒，退出quit_http/rc0，与summary一致；无ABORT。
2. **MANIFEST**：643条逐项SHA256重算、唯一性/目录范围及文件集合完整性检查全匹配，无遗漏。harness/template/binary摘要与当前冻结对象相符。
3. **profile/probes**：模板按每场目录和控制端口重建后逐字相同。五禁读探针拒绝、场景外写探针拒绝，probes.ok=true。HOME、app-data、缓存、日志与tmp均限各场景目录；未访问真实HOME另做复验。
4. **进程与回收**：pre/post NONE，最终pgid成员为空；library_scan无新增，驱动记的真实home目录mtime未变。运行中multi场列出一个osascript子进程，最终已回收；记录没有参数/用途，保留旧A-M3-R9-02建议，不据名称宣称成功越界或补作已授权外部自动化。审查者未调用它。
5. **captures/sha256**：请求9个capture，最终4个存在、5个缺失；metadata的exists/hash与盘一致。8个PNG含4个part，各part与对应final相同，3种不同内容均目视。实际图2560×1230全屏，size启动参数不能证明紧凑布局验收。缺图覆盖子项FAIL，属于证据建议，不凭此单独判业务FAIL。
6. **图像内容**：四场均未登录/无可见任务，forged显示“当前任务不在可见范围”；corrupt最终图与unknown图相同，未显示对应坏历史恢复出口的证据。未覆盖可见区域不作“绝无提示”推断。multi最终图没有“已退出”反馈，空登录图缺失，tap日志只证明安排点击，不能确认登录/退出处理器触达，也不能据此判产品登录失败。
7. **files_written_in_run_dir**：multi/unknown/forged各124项，corrupt125项，逐项存在、唯一、有序且在场景内，与count一致；这是驱动mtime文件清单，含资源/PNG，不能当124次业务写。
8. **sandbox_denials**：全文读取并重算摘要匹配。443外联、项目外Metal缓存、部分/dev/dtracehelper写被拒；另有appleeventsd读取宿主文件被拒记录。拒绝尝试不等于成功越界/成功MiniMax调用；聚合duplicate reports不作精确系统调用计数。没有已知成功违反隔离的证据。
9. **host.log/markers**：四份全文字节数/tail/markers重算一致；各有552591 B业务view=true，809 B属于宿主另一视图；无[E]/panic，tick错误计数0。unknown场第40/41行明确 `unknown --test-action type:…`、`key:Tab`，这是具体白名单覆盖阻断依据，不是rc71/rc3。
10. **model_proxy_stats**：四场needs_model=false，result没有model_proxy_stats/model_proxy字段，env无代理endpoint/MM_KEY；summary各billing_error=null。缺字段符合未启代理模式，不杜撰统计对象；本轮无真实调用/402/欠费错误，NEEDS_ABRAM=no。
11. **运输件与权威盘**：每场mirror、installed、唯一.running包资源全匹配。tasks/actions/events及合成账号表全与seed原字节相同，无新增OPEN、成功confirm final回执或关联confirm事件。corrupt旧主和有效bak保留，bad_lines为完整原主。saved主体清除与来源seed不执行模型返回/来源确认函数，不能代替D04动态正负例。
12. **私钥/授权**：本轮没生成新私钥；作者build_r8两把隔离测试私钥路径均不存在且keys目录空，删除证据仍可定位。只复用本地授权签名catalog和已安装运输件，无publish/listing/push/issue/消息/公网部署。

## 原缺陷复核与解阻建议

### D-M3-01 — 本轮原生冷启动项关闭

- 文件行：source:6731～6765 `_authorityHistoricalConfirm`、末位root。
- 原触发：旧r9保留字ok字段产生4解析诊断；实际本轮四场诊断0、业务view=true，图均渲染。
- 根因修复：字段改confirmed；当前helper无消费点如实保留。未新增视觉建议为P1。
- 验证：H全部host.log/PNG、A；这一结论只关闭旧空白与诊断，不代签完整报修交互。

### D-M3-02 — 原文/意图盘面及恢复异常关闭子项；控件恢复待验

- 文件行：source:11288～11309 tick恢复；本轮四场state及日志。
- 原触发/实际：持久中文冷开；旧catch _错误消失，原文/意图/key精确保留，tick_exception_count=0。
- 预期/影响：登录后可编辑控件也应显示相同原文；目前只有磁盘保留、未认证图，没有可信控件操作证据，完整闭合未知。
- 具体后续：先解B-M3-01，再核登录后原文、编辑、取消/重试与重开；不要通过清空原文或伪造SESSION制造成功。
- 严重性：本轮没有重新证实业务P1；剩余是必须完成的验证项，不凭未知失败编造缺陷。

### D-M3-04 — 原P1自拒根因源码修复成立；完整功能动态未闭合

- 文件行：source:4782默认version_present=false、4800原声明才置true、4859～4864确认重核条件回传；5919确认消费。
- 原触发：合法space/asset省略version/quote，首次verified后因规范化version=0而确认自拒。
- 实际/预期：本轮仅原声明存在才重新传version，旧精确自拒分支消除；应实际parse→apply→confirm正例通过且M2权威链完整，伪版本/quote/假ID/越权/停用/stale仍降级或拒。
- 证据：E/r9-to-r8.diff、冻结源码；作者Python复刻仅参考；本轮forged来源是预置task，**不是函数动态执行**。
- 根因已修复，不再把旧源码P1写成仍存在；动态合法/恶意来源确认仍NOT_RUN。不要求无依据重写业务代码。
- 验证方式：space/asset各一组无version/quote正例，声明0/999、假quote、跨项目/停用/stale负例；通过合规UI实际操作，读对应task、final action与同action_id事件。须先解B-M3-01。

### D-M3-03 / D-M3-05 / D-M3-06 / D-M3-07 — 改善保持，动态证据仍缺

|编号/文件行|实际与影响|具体后续验证|
|---|---|---|
|D03：3512/5058/5783/5919|回包、采纳与确认绑定守卫保留；未执行迟到交错，未知动态效果|有效正例；A改B迟到；展示后主体/项目/task/facts/evidence漂移逐项核展示、草稿与权威盘|
|D05：5919～6146、6683|只有commit_ok/confirmed_open/final_action_id/OPEN后写CONFIRMED的消费保留；0真实提交|AI与手工各独立确认/回读；丢响应、同key重试、同盘重开、较新任务版本。历史核验helper未使用及当前OPEN前提的旧建议保留，不扩审M2|
|D06：5276/5919|逐字段缺项/歧义守卫保持；冷盘假设备保护不等于人工解歧义成功|无选择、只选设备、只选空间、完整补齐四组；实际拒绝或成功权威链|
|D07：model_config/manifest及模型适配/审计|配置与net准入相符，0真实调用；没有真实provider审计链|needs_model代理下三组新描述，当前候选原生请求/结果审计；仅额度总≤10，欠费立停|

以上未测项不被包装成已观察到的业务事故；不新增无关P1，保留原编号与来源。

### B-M3-01 — 必需验证阻断：固定宿主白名单无法输入

- 文件/行：H/restore_unknown_empty_arrays/logs/host.log:**40–41**；固定宿主二进制摘要见上；harness request.schema.json允许请求type/key，但实际宿主拒识。
- 触发：本轮合法白名单请求type新恶意原文C、key:Tab。
- 实际/预期：日志unknown，截图仍未登录，盘仍原文B；期望合规内置动作可在真实原生控件输入测试账号/原文并触发业务。不是应用所有输入功能已坏的证明。
- 根因范围：请求schema能力与固定宿主实际能力不一致确定；没有测试成功登录、真实中文、受控迟到返回的可用通道。不能通过agent沙箱预检或作者等价脚本补足。
- 影响：核心真实模型及AI/手工确认、编辑、取消/重试、双层交错不能独立执行，模块不能放行。
- 解阻条件：驱动/宿主在既有授权白名单内提供有效账号/文本键入、延迟回复/中途上下文改变、同Store重开/精确失败控制；先用实际反馈证明动作有效，再走本轮同候选。审查方不自行改宿主、业务代码或引入未授权自动化。
- 严重性/归类：阻断核心验证，必需解阻；不是新增已证明的业务P1。没有ABORT，BLOCKED仅用于这类白名单无法覆盖的动作。

### 建议挂账

- **A-M3-R10-01 / P2 / 建议**：9次capture只产4次最终图；H各result.captures与host.log捕获动作。完整中间状态期望可回读，实际5图缺失，影响入口/操作覆盖。驱动需让capture完成后再推进下一次capture/tap并明确状态反馈；验证9图齐全、摘要可核、真实按钮反馈可見。不能以计划坐标代替命中证据；不因建议项单独FAIL。
- **A-M3-R9-02 延续 / P2**：multi运行中osascript子进程参数/用途未记录，最终清理成立。补内置capture来源/参数证据，区分内部机制与额外自动化；未凭缺参数认定安全P1。
- 旧A-M3-R9-01交接不明已解决：本轮正式r8报告、清单与实际运行对应，不能再称未交接0fb诊断快照。

## 相关既有用例逐项结果

|用例|本轮精确判定|
|---|---|
|G0-E|NOT_RUN：0真实MiniMax调用；实际输入触发通道BLOCKED，不认配置/net准入为通过|
|T01|NOT_RUN完整真实提取/追问/编辑；原文磁盘保留与未确认无OPEN子项PASS|
|T03|NOT_RUN合法/缺项/越权空间提交；未认证盘不写负例PASS，不能代签联系人校验|
|T25|NOT_RUN真实恶意模型返回/状态权限；伪saved主体+跨项目敌意冷盘保护子项PASS|
|T26|NOT_RUN模型错误与合法手工兜底；输入通道BLOCKED|
|T33|NOT_RUN真实意图泛化；独立A/B/C及同义句已固定，不算已输入/调用|
|T34|D04旧自拒根因源码修复成立；真实依据、追问、多候选/无历史与来源正负例NOT_RUN|
|T35|BLOCKED：实际type/key拒识，白名单无有效迟到/途中上下文控制；双层源码守卫不代签|
|T36|NOT_RUN真实适配器/错误返回白名单动态；net安装准入只是已证子项|
|T37|NOT_RUN：AI/手工final/事件/回读/丢响应/较新版本核验未发生|
|T38|固定候选/配置/宿主/请求/seed可定位复跑子项PASS；完整成功/失败业务复跑NOT_RUN|
|U02|NOT_RUN完整可编辑草稿与手工继续；原文保留PASS子项，控制通道BLOCKED|
|U07|输入/意图/key冷开保持PASS子项；真实重复提交、丢响应/冲突恢复NOT_RUN|
|U08|未登录/不可见任务空态PASS子项；坏历史盘面保全PASS子项；完整可继续恢复出口NOT_RUN|
|U11|原生根/零错误冷启动PASS子项；真实输入BLOCKED，滚动/面板/取消重试NOT_RUN|

## 判定与交接

- **最终结论：BLOCKED**，精确范围为正式M3-r8候选原D01～07复核及直接依赖回归。本轮没有已确认仍存在的新增业务P1，也没有证据证明核心AI/手工路径成功；因此不能按“无P1”单独PASS。
- 原解析/空白及恢复回调错误关闭；D04旧自拒根因源码修复成立，完整来源确认动态未验收。必需工作是B-M3-01解阻并补核心原生证据；P2建议保留挂账，不因建议FAIL。
- 先解合规输入/测试控制，成功合成账号登录后，分别运行三组新描述与来源正负例、迟到展示/采纳失效、AI确认与手工确认、M2 final回执/同action事件/权威回读/重开。不能伪造SESSION、预置OPEN或用模型文字充当完成。
- M2正式FAIL继续保留；当前输入/意图/key/空历史/坏历史回归子项不替M2整模块验收，也不修前序挂账代码。
- 更新仅 `docs/optimization/2026-10-09-desktop/GATES.json` 的M3 status和审查字段，review_report指本报告；旧审查字段完整追加history并保存门禁前态。作者candidate/base/implementation/build_summary、其他模块与external_delivery不改。
- `docs/build-loop/ACCEPTANCE.json`不改：没有新增完整核心业务PASS；逐项结果写GATES.review_acceptance，保留原台账证据形态及历史，不把历史后端PASS解释成原生PASS。
- 不允许进入下一模块，不提供下一模块入口，不执行下一模块。
- **NEEDS_ABRAM=no**：身份、MiniMax、隔离离线签名与本地安装已授权；无公开发布需求或实测欠费。剩余是技术通道与验证缺口。

STATUS=BLOCKED
NEEDS_ABRAM=no
