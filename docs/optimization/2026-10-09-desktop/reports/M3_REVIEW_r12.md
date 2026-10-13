# M3 独立 Review r12

**最终结论：FAIL。受审候选 M3-r9-worktree。** 八场独立原生运行均 CLEAN，实际加载本候选、解析/运行错误为 0、登录页可渲染；损坏源精确保全和备份失败冻结子项通过。但有效 ASCII/中文 JSON 都被当作损坏，未提交原文、确认意图和原动作键没有恢复，沿 **D-M3-02 保留 P1 必修**。AI 与手工合法创建/回执/回读完整链分别 NOT_RUN；没有真实模型成功证据，不能放行。

## 审查对象与范围

- 审查者/日期：本主会话唯一独立审查者，2026-10-13，Asia/Shanghai，无子代理；不修业务代码。主会话实际 Router 路由与指定模型无当前接口核实/切换，未冒称切换；没有当前线程 createdAt/标题写入接口，未冒称已设置标题。
- 正式 candidate_id/base：**M3-r9-worktree / M3-r8-worktree**。作者报告 `reports/M3_IMPLEMENTATION_r9.md`，候选清单 `runtime/optimization/2026-10-09/M3/r9/CANDIDATE.json`；由用户交接、GATES、实施报告与候选关系定位，不按文件时间选版。
- HEAD **8d730569546cb57310944bb299695134df773b9d**，dirty；main **657584 B / SHA256 c37e31e6b7705277dc133e8ef61b9ab77b30d1a6b9d4c16a856dc90f4816e421**。四个 frozen_objects、r9 冻结源码、审查冻结源码与当前文件一致；准备/本段审计的 12 个保护输入和 180 个 seed/mirror 文件未变。门禁写前后保护核查另存，GATES 的本轮授权变更单列。
- 运输 digest **77b95f2eb1ecc5c97cc109e46cda7ccbb3276ac52f99b4f840cad8150d1adf6b**。每场 signed mirror、installed 和唯一 `.running` 的全部 14 个运行资源相同，共 112 个实际运行资源比较匹配。未签名工作树 manifest 与运输 manifest 的 integrity/signature 差别分开保留，不混记 SHA。
- 固定宿主 SHA256 **3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90**；harness **226df8dd61409cb0c82a7e70a931c2637362445d8a4a9e5232254da29188d11a**；profile 模板 **80dacdd17d73429ea82782d7dbd541492f5c6cade55d73003de3713ce6bbbbe7**。实际宿主位于项目 M0/r3/host/app-extracted 内，没有审查方自行启动宿主或做 sandbox-exec/pgrep 预检。
- 前置 M2 **FAIL / M2-r10-worktree / reports/M2_REVIEW_r12.md**，没有已接受 PASS 候选。按用户前序挂账裁决进行本模块局部复核；不制造 M2 PASS，也不把本轮恢复回归代成 M2 整模块验收。
- 两段式请求 `M3/native/REQUEST_review_r2_0002.json`，SHA256 **6ab33ec1091b51f3e8fa17fade9473a363beba60271c1bbc1b818f292742189c**；阶段笔记 `M3/native/REVIEW_NOTES_r2_0002.md`。驱动沙箱外执行 **02:28:17–02:30:30 +08:00**，八场 CLEAN、无 ABORT，逐场 15.17–15.43 秒、quit_http/rc0。
- 已阅读：实际 AGENTS/CONTEXT、00/01/02/M3/04、r9 实施/清单/验证脚本、上一轮 r11 缺陷、M2 r12 直接依赖、相关 G0/T/U 定义、r11 共享源码到 r9 的差异、相关函数、schema/harness 和本轮所有原生证据。只核原 D01–07/B01 及直接受影响恢复，无无关扩审。
- 实际执行：第 1 段新隔离 seed/request 准备；驱动八场 launch-hub/capture/退出；本段运行 `M3/native/review_r2_0002/audit_phase2.py` 核全部证据并目视所有不同图像内容。没有重新执行作者测试覆盖作者结果。
- 未运行：可信登录后现场中文键入、三组原生真实 MiniMax、迟到/恶意模型回包、合法来源采纳与人工解歧义、AI/手工合法确认/回执/回读/重开及精确提交点故障。预存输入与伪持久身份只用于冷开负例，不充当实际输入或成功会话。
- 模型配置仍 MiniMax/MiniMax-M3/anthropic messages；八场 needs_model=false，本轮真实请求 **0 次**，无代理、无 billing error。历史 r3 Python 3 次只作为作者旧记录，不代当前原生调用实证。

下文 **H/**=`runtime/optimization/2026-10-09/M3/native-runs/review_r2_0002_REQUEST_review_r2_0002/`，**E/**=`runtime/optimization/2026-10-09/M3/native/review_r2_0002/`；**A**=E/native-evidence-audit-r12.json，**V**=E/visual-observations-r12.json。源码行号指 E/source.main.splash，与受审 app/bundle/main.splash 相同。

置信度：候选、隔离/回收记录、恢复盘面与 D02 失败 **高**；新增完整性门禁中究竟哪个宿主原语导致误判 **未知**；未执行的真实模型效果与可信业务链 **未知/NOT_RUN**。

## 必需检查

|检查|独立步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选/宿主/请求/资源一致|重算清单、请求、冻结源码及 mirror/installed/.running 全资源|同正式候选、实际业务加载|四个源码清单一致，八场唯一运行本包 14 资源一致；657584 B eval view=true|PASS，仅版本与运行一致|A、phase1-start、r11-shared-to-r9.diff、H各log:43|
|隔离与回收|核完整 profile/probes/env/pre/post/pgid/denials|写限本场，禁读生效，无残留|八场 probes.ok=true、pre/post NONE、pgid_members_after=[]、CLEAN/rc0|PASS，驱动记录范围|A、H各result/profile/denials|
|D01零错误冷开|读八份完整日志、核八张 final PNG|解析/运行错误 0，业务根可见|八场零[E]/panic，均见登录页；无业务区空白/未打开提示|PASS冷开/登录页；工作台NOT_RUN|A、V、H各frames/logs|
|D02有效ASCII恢复|新804 B有效view冷开，核主/备份/原文/intent/key|正常并入、原字段保留、不备份为坏源|主覆为2207 B默认态，原文/intent/key为空；804 B精确boot-bak存在|FAIL，核心P1|H/valid_ascii_view、A.view_compare|
|D02有效中文恢复|新1004 B完整中文/引号/换行/emoji/空白view冷开|逐字恢复、intent/key不丢|同样误判坏，主2207 B、字段空；1004 B精确boot-bak存在|FAIL，核心P1|H/valid_unicode_view、A|
|D02闭合非法JSON保源|独立226 B首尾括号闭合但值非法|不部分恢复后覆盖唯一来源|完整226 B源在boot-bak；主默认态；业务盘不写|PASS本例保源；可见诊断建议挂账|H/closed_invalid_json、V|
|D02截断+不同旧bak|202 B新坏源、77 B无关旧bak|精确新副本，旧bak不动|新corrupt-bak逐字相等、旧77 B不变|PASS本例来源保全；可见诊断建议挂账|H/truncated_different_old_backup|
|D02备份位满|独立坏源、三个旧副本均占用|冻结主源、旧备份不变、人工出口可见|主202 B不变、三旧副本不变；截图有冻结/人工修复说明|PASS此失败恢复保护|H/all_backup_slots_occupied、V|
|D02备份路径为目录|三备份路径均目录|原坏源/目录不动，冻结及提示|主224 B和三目录不变，截图同冻结说明|PASS此失败恢复保护|H/backup_slots_are_directories、V|
|未认证权限负例|伪保存经理/session、跨项目DRAFT/假设备/恶意原文冷开|不得建立可信身份或写业务|仍登录页，active actor/session为空；tasks/actions/events原字节不变|PASS该冷盘负例；有效view恢复仍FAIL|H/forged_saved_subject|
|坏events保全与提示|新好坏好295 B事件源+旧事件bak，另有有效view|原事件/旧bak保全，准确冻结提示|源/旧bak不变，bad_lines等完整295 B源；截图有修复出口|PASS事件保护；有效view原文/intent/key恢复FAIL|H/damaged_events_valid_view|
|硬1：三组真实建议|现场新描述/同义句、追问/多候选/无历史|随事实变化，不编造设备与根因|只有计划和预存输入，0请求|NOT_RUN；实际文本动作覆盖BLOCKED|E/independent-descriptions、B01|
|硬2：AI成功权威链|真实建议→编辑→人确认→M2 final/事件/回读/重开|成功来自权威结果|未执行；D05外层消费源码改善|NOT_RUN|D05、B01|
|硬2/4：手工链|无模型实际填写合法工单→确认/回读|合法人工仍可创建，未确认不OPEN|未执行合法手工链；冷开仅原预装DRAFT，无新增OPEN/回执|手工NOT_RUN；未认证无OPEN子项PASS|A、H权威盘|
|硬3：展示/采纳双层失效|A请求中改B、迟到A；展示后改上下文再采纳|两层拒旧建议、无副作用|源码守卫保持，实际交错未执行|BLOCKED，仅有效输入/受控回复动作缺口|D03、B01|
|硬4：恶意/格式/自报成功与错误恢复|假设备/越权/status/恶意原文实际回包|拒绝且不写任务，人工可继续|冷盘负例已测；真实回包/错误路径未测|NOT_RUN；受控回包机制BLOCKED|D04/D06/D07/B01|
|硬5：真实编辑/取消/重试/元信息|可信桌面键入、取消、重试、原生provider结果|真实操作可用、输入保留、秘密不落盘|只有冷开；有效持久输入恢复FAIL，文本/取消/重试未运行|恢复FAIL；其余NOT_RUN/文本通道BLOCKED|D02、B01|

## 原生证据逐项核验

审计 **5820 项一致性检查、0 不匹配**，**1309 项 MANIFEST** 重算匹配，180 个准备文件未变。这些数量是证据记录核对数，不是业务用例 PASS 数。

1. **summary/result/请求/命令**：八场 ID、purpose、size、seed、digest、实际 cmd、batch、结论/时长/退出逐项一致。实际仅 launch-hub 与 capture，没有 ui_actions、type/key、--help 或额外自动化。每个 seed/apps/catalog.json 都存在；没有 no catalog/未打开应用警告，不重复 M2 r12 审查夹具错误。
2. **profile/probes**：按已钉模板、每场目录和记录中的端口/禁读路径重新构造，八份逐字相同且 SHA 匹配。外写探针 created=false；5 类禁读均拒绝、probes.ok=true。HOME/app-data/tmp/cache/config/log 范围限本场；本轮不授权模型代理端口。只核探针记录，未读取禁读目标。模板保留 /dev/null 和本机 unix/control 例外，未扩大为任意外联。
3. **进程/退出**：pre/post class=NONE、pgid_members_after=[]，运行成员属本场进程组；host_returncode=0、quit_http、library_scan无新增，驱动记录真实HOME目录mtime前后相等。未自行运行 pgrep/sandbox-exec；没有 ABORT，不将 agent rc71/rc3 用作 BLOCKED 理由。
4. **captures/PNG**：8/8请求final存在且SHA匹配，另8个part有效，共16张，全部2800×1696。5种不同字节内容均目视，并以相同SHA映射其余图：正常登录页（钟面不同形成3种）、备份失败冻结警告、坏events冻结警告。closed_invalid 的part/final钟面不同，均已覆盖；不要求二者逐字相同。没有登录后草稿/工作台证据；启动1280×800不能代签客户区布局/键盘验收。
5. **files_written_in_run_dir**：逐项核排序/唯一性/路径限制/存在/计数；每场125–128。含运行资源、图像和日志，是驱动mtime清单，不是业务写次数或全系统写审计。
6. **sandbox_denials**：八份全文已读取并重算摘要，与result一致。包括外部443、项目外Metal缓存与/dev/dtracehelper写拒绝；没有记录证明越界写成功。宿主news外联失败不当作MiniMax调用；重复日志不是独立系统调用次数。
7. **host_log_markers**：全文重算 listening/quit/launched/eval/panic/app_not_opened、bytes/tail，与result相同；八場657584 B业务eval view=true，另809 B为宿主其它视图。[E]/panic/unknown test-action均0。四场冷开有260–316 ms ui-hang记录；没有执行输入，不据此新增核心交互P1。
8. **model_proxy_stats**：八场needs_model=false，统计/代理字段不存在、环境无MM_KEY/模型endpoint，summary billing_error=null。这是未启代理的合法缺字段，0新请求；不虚构余额或调用成功。
9. **权威盘**：八场tasks/actions/events及合成账号表与seed原字节一致。只有预装合成DRAFT，无新增OPEN、confirm final回执或关联确认事件。合法view四场原文/intent/key被清空但精确源备份存在；坏源可备份时保源、不可备份时原主不变；坏events源保全与可见提示成立。
10. **运输/私钥**：mirror/installed/.running全部资源一致，digest在seed/catalog，log未打印digest已明确区分。复用r9本地已签名catalog，没有生成新私钥；build_r9/keys为空，原working/anchor删除证据可定位。本地安装加载成立，不需要公开发布解阻。

## 缺陷及原编号复核

### D-M3-02 — P1 / 必修 / OPEN：有效持久输入被误判损坏，原文与确认意图没有恢复

- **文件行**：main:560–568 新 `_complete` 判定；594–600 判坏后以默认态继续；607–625正常并入；999–1003 saveState放行默认覆盖；12977–12994真实TextInput恢复消费。相关类型探针1265–1272、字符辅助1983–2000。
- **独立触发**：valid_ascii_view 的804 B完整有效JSON，valid_unicode_view的1004 B完整有效JSON（中文/引号/换行/emoji/外部空白），均含非空pending_input、confirm_intent_id、confirm_intent及action_keys_by_task。用本请求在全新隔离Store冷开、capture、退出。
- **实际**：两场主文件均被改为2207 B默认态；原pending_input/confirm_intent_id变空，confirm_intent变nil、action_keys_by_task变空对象；磁盘status为“损坏/不完整……以默认偏好继续”。boot-bak分别精确保留原804/1004 B源字节。forged_saved_subject及damaged_events_valid_view两个有效view也未恢复四字段。**不是源字节不可逆丢失，也没有观察到已登录后的输入控件清空；独立确定的是有效未提交输入/原意图无法正常恢复。**
- **预期**：合法view正常恢复原文与不可变意图/原key，不建立会话，不生成损坏备份。真正坏源精确保全或冻结；修坏源不能导致所有合法输入退出后无法继续。
- **根因**：r9新增完整性门禁在选定宿主上错误地落入损坏分支；置_VIEW_STATE_OK=true后，正常保存把默认偏好覆成主文件，首tick自然没有原文可恢复。根因已定位到新增门禁及其消费，具体哪一项trim/长度/字符/对象探针原语导致false仍未知，不捏造返回类型。仅首尾括号也不能证明严格JSON合法；本轮非法闭合例保源成立，并不证明此通用校验正确。
- **影响**：用户未提交报修在重启后不能继续，原确认意图/动作键不恢复；与核心输入保留、同意图恢复直接相关，按用户“只因核心/P1判FAIL”的要求保留必修。没有把视觉提示问题当本轮FAIL理由。
- **证据**：H/valid_ascii_view和valid_unicode_view的result/log/frame/主文件/boot-bak；E/seeds同名原文件；A各view_compare四项false、原/现字节和精确备份记录；冻结source和r11-shared-to-r9.diff。源码与独立盘面相互印证，置信度高。
- **具体改法**：先用固定宿主最小正负例确定m7_is_object_value/text.trim/_textLenSafe/_charAtSafe的实际行为；采用能在本宿主认可完整合法JSON且拒截断/非法值的验证，失败时保持精确保源/冻结。合法路径必须进入逐字段并入并保留原文/intent/key，不能只删除坏源保护来让正例通过；备份失败和旧备份不覆写的已通过逻辑保持。不要改布局或扩展其他模块。
- **验证方式**：重跑本轮有效ASCII/中文/空白/emoji、闭合非法值、截断+不同旧bak、备份满/目录，核原文/intent/payload/key精确恢复、坏源/旧源不丢、正常无损坏备份；可信登录后再核控件恢复及同原意图重试。先附冷启动零错误结果与截图，再交新候选/差异/哈希；Python等价或字符串断言不能代原生正例。

### D-M3-05 — 源码原根因修复认可；动态验收 NOT_RUN

r9在main:6877–6912恢复分支显式消费commit_ok/confirmed_open/final_action_id，unknown不再因非nil即return true；历史动作与当前阶段文案分开。main:7140正常成功文案取outcome.task_id；12174–12186真实按钮删除currentTask()/固定OPEN覆盖。这关闭了r11点名的**源码分支根因子项**，不沿用已修复源码的FAIL，也不虚构新的P1。

本轮没有认证或点确认；没有真实final/关联事件/回读。因此D05完整业务闭合仍 **NOT_RUN**。下一次在允许的有效控制通道下分别覆盖nil、unknown、缺事件/缺final id、完整final、历史已推进和同键重试；核真正task_id、屏幕文案与权威盘。当前唯一已运行必修为D02；D05剩余是核心验证缺口，不要求无证据的额外业务改动。

### 其余编号

|编号|本轮结论|保留范围|
|---|---|---|
|D-M3-01|CLOSED_SUBITEM：八场零错误、业务根与登录页渲染PASS|登录后工作台NOT_RUN，不扩大冷开结论|
|D-M3-02坏源子项|本次226 B非法闭合、202 B截断保源及旧bak不变PASS；备份满/目录冻结与提示PASS|有效恢复P1仍OPEN；手动修复/重开未执行|
|D-M3-03|源码守卫保留，伪持久主体冷盘无写子项PASS|迟到/改输入/切项目/撤权/task/facts/evidence交错BLOCKED于允许动作覆盖|
|D-M3-04|来源version_present修复保持，冷盘假设备/跨项目不获会话子项PASS|真实parse→展示→采纳→确认来源正负例NOT_RUN|
|D-M3-06|逐字段补歧义源码保留|现场追问、多候选人工选择与无历史真实路径NOT_RUN|
|D-M3-07|配置/代理覆盖/net准入源码保留，0调用|原生真实MiniMax三组输入效果/元信息NOT_RUN|

**B-M3-01 / 具体白名单覆盖 BLOCKED**：schema虽有ui_actions，但本次明确禁止其osascript/辅助功能/自动化实现；固定宿主type/key先前原生日志已实证unknown。本次允许launch/tap/capture不能完成有效登录与现场文本键入，也不能安排受控迟到/恶意模型返回、精确提交点故障或同Store中途重开。只把这些动作的验证机制记BLOCKED；普通未执行业务项记NOT_RUN，已运行D02失败记FAIL。没有ABORT，不以rc71/rc3判阻塞。解阻需要驱动/宿主在当前授权范围内提供有效文本输入和响应/提交控制，并实证动作生效；身份/provider不用再裁决，未知余额不算NEEDS_ABRAM。

**A-M3-R12-01 / P2 建议挂账**：main:594–595备份成功仅写STATE.status，未像失败分支598那样设置M2_RECOVERY_NOTICE；12941登录提示只消费该notice。closed_invalid/truncated已精确保源，但截图只见登录说明，无“已备份、如何恢复”的诊断。建议补可见保源/恢复说明；验证坏源副本和同屏文字。本建议不单独导致FAIL，不改布局。

## 既有验收逐项复核

|项|本轮精确结果|
|---|---|
|G0-E|NOT_RUN：0原生真实请求，配置/net/本地catalog不代模型实证|
|T01|真实提取/追问/编辑NOT_RUN；持久原文恢复子项FAIL（D02），未认证无OPEN子项PASS|
|T03|合法/无空间/越权/缺联系人实际提交NOT_RUN；未认证冷盘业务不写子项PASS|
|T25|真实恶意模型返回/伪状态/矛盾工具数据NOT_RUN；伪保存经理/跨项目假设备冷盘保护PASS子项|
|T26|真实模型失败状态与合法手工兜底NOT_RUN；没有用假模型成功替代|
|T33|三组真实描述/同义表达泛化NOT_RUN；独立描述只是计划及预存夹具|
|T34|合法/恶意来源及人工解歧义动态NOT_RUN；旧version_present源码改善保持|
|T35|BLOCKED：允许动作不支持有效文本和受控返回交错；两层源码检查不代运行|
|T36|真实适配器/白名单错误回包NOT_RUN；受控恶意回包机制BLOCKED|
|T37|D05原源码根因修复子项认可；AI/手工final/事件/回读/未知恢复动态NOT_RUN；原intent/key恢复FAIL（D02）|
|T38|当前候选/宿主/请求/seed/运输可固定且独立冷开可复核；真实模型成功/失败同条件复跑NOT_RUN|
|U02|FAIL：有效未提交原文不能正常恢复；实际AI草稿编辑/补歧义/手工兜底NOT_RUN|
|U07|FAIL：有效view的原intent/payload/key没有恢复；重复点击/丢响应/冲突/离线完整链NOT_RUN|
|U08|备份满/目录、坏events的保源与可见人工出口PASS子项；完整模型/权限/过期/附件错误出口NOT_RUN；成功备份说明缺失为P2建议|
|U11|零错误冷开/登录页PASS子项，恢复输入状态FAIL子项；实际滚动/键入/面板/取消/重试NOT_RUN，键入动作覆盖BLOCKED|

## 判定

- **最终结论：FAIL**。精确范围：正式M3-r9候选，按r11原编号复核和直接受影响恢复；不是全模块核心成功链已经运行，也不是因为CLEAN就通过。
- 必修：**D-M3-02**有效view误判坏与原文/原意图/key恢复。保留本轮坏源保全/冻结的已通过子项；先固定宿主原生正例验证，不扩展后续模块。
- 核心未测：D05可信按钮/权威回执、AI和手工成功链分别NOT_RUN，三组真实原生MiniMaxNOT_RUN；B01只列确实不被允许动作覆盖的具体验证机制。M2前置仍FAIL并挂账，不伪造通过。
- 受影响前序：恢复view、坏events、未认证权限和本地安装/冷开已做本轮针对性回归；有效view失败，其余上述限定子项通过；不代签M2整体。
- GATES只更新M3 status、review_report/reviewed_at和review_*字段，指向本r12及正式r9候选；旧审查完整字段追加review_history，写前备份E/GATES.before-review-r12.json。构建candidate/base/implementation/evidence/needs_abram等字段及其他模块保持。
- ACCEPTANCE.json不改：没有新的完整业务PASS，不覆盖38业务/12UI/P0历史；本轮逐项结果存报告与M3.review_acceptance，并保留旧审查来源。写后核验E/final-verification-r12.json。
- **不允许下一模块，不给下一模块入口。** 构建方只修D02及实证所需最小范围，交新候选、零错误冷开、真实恢复/确认结果，再独立复审。P2建议挂账，不因它单独FAIL。
- 第2段仅项目内读写，无宿主自启动、业务代码/原数据修改、秘密读取、消息、网络/公开签名/发布/push/Issue或部署。第1段一次项目外memory注册表读取的偏差已在阶段笔记记明，本报告不抹除它。本轮0模型调用，没有观察到余额不足/402或公开发布需求；剩余修复与控制缺口是技术问题，**NEEDS_ABRAM=no**。

STATUS=FAIL
NEEDS_ABRAM=no
