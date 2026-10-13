# M3 独立 Review r5 · harness 两段式重审

最终结论：**FAIL**。本审查者选择的两个原生场景均加载了同字节当前源码，但客户区空白，每份宿主日志有 **50 条解析错误**。报修输入、AI 建议、人工确认与权威回读均未运行成立。harness **CLEAN 只代表隔离与回收通过**。D-M3-01/03/04/05/06 的核心问题未闭合；保留已改善子项，不修业务、不进入下一模块。

- 审查者 / 日期：本会话唯一 Codex 独立审查方，2026-10-11（Asia/Shanghai），未委派代理。实际主会话 Router/gpt-6.1-sol 路由和 createdAt/标题能力不可核验，未声称切换或改名。
- 交接 candidate_id：`M3-r4-worktree`；base=`M3-r3-worktree`。GATES、实施报告、候选清单三处定位一致，不按文件时间选版本。作者报告：`reports/M3_IMPLEMENTATION_r4.md`。
- 本次用户明确授权 SKIP_FIRST_BUILD_ALL 对当前代码重审；精确审查快照为 **`M3-harness-r1-1309-current`**，不是作者新交接的 M3-r5。HEAD=`8d730569546cb57310944bb299695134df773b9d`，dirty。当前 main 375436 字节，SHA256=`8b7d84e7bc58022aad991c7fc9f0e60b58dd1dbe437fe3dcb18ca7d9d70f2269`；原 r4 main=`1a2773cf446a13db70af1ac5f74f61ec0e171aadb939f775ee8195c40ab001b4`。
- 新增差异、内容清单与函数核对：`runtime/optimization/2026-10-09/M3/native/review_r1_1309/`（下称 **S/**）中的 start-snapshot.json、main.splash.snapshot、M3-r4-to-current.diff、function-delta.json、source-traces.json。大部分 M3 关键函数与 r4 完全相同；确认失效恢复来自 M4 修改，创建提前主写改善来自 M2 r5，不能把合并后代码冒称新 M3 实施候选。
- 前置：M2=`M2-r5-worktree` / **FAIL**，独立报告 `reports/M2_REVIEW_r6.md`，不存在已接受的 M2 PASS 基线。按用户前序挂账裁决继续局部复审；本轮只定向核其界面加载、创建/确认/回执依赖，不修 M2、不改其门禁。
- 实际宿主：驱动在 agent 沙箱外执行审查者请求；二进制 `M0/r3/host/app-extracted/OctoSense.app/Contents/MacOS/octosense`，SHA256=`3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`。配置为 MiniMax/MiniMax-M3；**本轮实际模型请求 0**，没有模型效果结论或付款错误。
- 原生证据根：`runtime/optimization/2026-10-09/M3/native-runs/review_r1_1309_REQUEST_review_r1_1309/`（下称 **H/**）。独立请求 `M3/native/REQUEST_review_r1_1309.json`，阶段笔记 `M3/native/REVIEW_NOTES_r1_1309.md`；执行窗口 **14:03:40–14:04:13 CST**。独立重算结果为 **S/native-evidence-audit.json**（下称 **A**）。
- 阅读/运行范围：阶段1所列 AGENTS、CONTEXT、00/01/02/M3/04、前轮原编号、作者报告/清单/证据、受影响源码与 M2 依赖；阶段2读取全部 summary/result/profile/denials/host.log、逐张查看两份最终帧、重算完整 MANIFEST、核实际 jail 与所有目标运行副本。未扩大到后续模块业务。
- 快照一致：阶段1→本轮定稿前 main、manifest、model_config、identities、GATES、ACCEPTANCE 摘要一致；两场景目标 export/installed/.running 各三份主源均与冻结 main 一致。定稿后仅有本报告、新审查证据与 GATES 的 M3 审查字段变化，结束自检另存 S/report-verification.json。
- 数据/秘密：业务盘和账号均为另造隔离夹具，未造已认证 SESSION，未读/打印/改原明文凭据或模型密钥，未改原业务数据。未启动自己的 launcher、未做 sandbox-exec/pgrep 预检，未用 --help/osascript/辅助功能/自动化。无 publish/公开签名/listing/push/issue/评论/消息/公网部署。
- 过程偏差披露：阶段1开场只读搜索项目外 MEMORY.md，另读项目外标题技能；此后停止，未写项目外，未据其代签候选结果。本轮第2段读取/写入均在项目内部。该偏差是审查过程记录，不伪装成业务缺陷。
- 置信度：证据摘要、隔离回收、原生空白/解析错误及确定源码分支 **高**；真实模型、新输入交错、业务提交/权限/故障恢复 **未知或未运行**。

## 必需检查

|检查|独立操作步骤|期望|实际|结果|证据|
|---|---|---|---|---|---|
|候选及证据完整性|重算清单、请求/summary、宿主、seed、export/install/.running与冻结源|同请求、同内容、证据完整|MANIFEST **321项**全部匹配，遗漏0；请求/驱动/template一致；两场景目标源均匹配|PASS（对象/证据范围）|H/MANIFEST.sha256；A；S快照/差异|
|隔离与回收|核 profile/SHA、读写探针、env、前后进程、退出及写入清单|只写新run目录、黑名单不可读、无进程残留|两场景 profile_probes.ok=true，apply rc0，越界写rc1且未创建，五项黑名单读rc1；pre/post rc1 NONE，pgid_members_after=[]，CLEAN；quit_http，host rc0|PASS（原生隔离/回收）|H/*/result.json、profile.sb、denials；A|
|本地安装路线|复用同源码已授权离线Store，核原 install_staged/verify/may_run与本轮实际加载|无需公開发布，当前字节可本地安装/加载|继承安装证据rc0；本轮launch-hub及375436字节eval，运行复制SHA一致；应用解析失败|PASS安装/加载字节；FAIL应用运行|S/reused-store-evidence.json；H/*/logs/host.log:38–45；A|
|原生报修入口/手工面板|空盘1280×800、独立tap/capture|可见可操作表单，支持实际输入和错误出口|真实PNG为空白客户区；50条[E]；tap被调度但没有业务控件可命中|FAIL / D01相关加载依赖|H/fresh_manual_entry/frames、host.log:39、44–93|
|AI来源/歧义面板|980×760，预置synthetic DRAFT、伪来源/恶意原文，独立tap/capture|按权限读投影，来源不提升为权威事实|同样空白、50条[E]；预置业务文件不变，没有来源/权限逻辑执行证明|FAIL界面；实际来源/权限判断NOT_RUN|H/ai_provenance_untrusted/frames、logs；A|
|硬1 三组新真实输入|现场另选滴水歧义、位置未知断电、无历史排风/恶意原文；追实际适配body|真实建议随事实/症状变化、缺项追问|未键入/请求，源仍漏事实/绑定/代理地址/HTTP许可实证|FAIL D01源码；模型NOT_RUN|阶段笔记三组描述；S/source-traces；manifest/model_config|
|硬2 AI确认链|追 apply→confirmDraftModelBound→createDraftFromPanel→M2确认；查实际盘|确认前不OPEN；精确final/action/event/任务可回读重开|没有AI执行；源码只查task_id/status，返回创建action_id且按内存OPEN判成功；盘与seed相同|FAIL D05源码；AI业务NOT_RUN|S/source-traces、function-delta；H实际jail；M2 r6|
|硬2/4 手工链|独立空盘原生入口，追手工字段→同确认边界|无模型仍能合法提交并权威回读|没有手工输入/建单；空白界面、同D05；空盘无新增不证明拒绝守卫执行|FAIL界面/D05；手工业务NOT_RUN|H/fresh_manual_entry；S/source-traces|
|硬3 展示/采纳/确认失效|复核前轮三种输入交错及版本/撤权/事实/证据守卫|旧建议不能展示、覆盖或执行|关键函数未改；APPLIED编辑后采纳谓词仍成立；确认仅按版本进展放行；当前task/事实/证据版本未完整校验|FAIL D03源码；动态交错NOT_RUN；通道BLOCKED见下|S/function-delta、source-traces；当前UI handler|
|硬4 恶意返回/字段来源|追假ID、真实B项目、非法状态、伪来源分支及手工兜底|假事实/越权拒；合法来源可核|事实守卫改善保留；来源仍只验类型/非空，未有实际恶意provider返回或主体矩阵|FAIL D04/D06源码；动态NOT_RUN|S/source-traces；前轮证据保持原运行范围|
|硬5 桌面输入/取消/重试及审计|看真实帧、日志、审计字段|真实输入可用，失败可继续，秘密不落盘|UI空白；未到输入/错误/重试路径；recordModelMeta原白名单保留，无新增秘密证据|FAIL原生UI；真实审计路径NOT_RUN|H/两帧及logs；S/source-traces.recordModelMeta|
|受影响M2回归|同源码原生加载及创建/确认差异核对|可信会话与可靠最终提交作为M3基础|重现M2 r6解析/空白；提前主写/提示改善认可，关联提交/原动作恢复仍缺|FAIL（阻断M3的依赖）；不改变M2结论|本轮H；M2_REVIEW_r6；function-delta|

### 证据边界与核验细节

1. 两份最终PNG均逐张目视，尺寸均 **2800×1718像素**；请求分别为1280×800、980×760，不能据这些实际同尺寸空白画面宣称响应式布局通过。各 `.part.png` 与对应最终PNG字节相同，核摘要后不算额外业务步骤。最终SHA分别为 `8e7bc62b5d4eb0325428f3d1b7530e76f0dee700ce31bcf735b20bdeda817841`、`49fac6fb66b3e574d942644e194be3baa65058fbf0d806a3e7673884a2230716`。
2. 两场景每份写入清单123项，全在各自run内且文件存在；HOME/app-data/cache/tmp/config/data及其他路径env均受限。家目录mtime记录前后相同，Library扫描新写0。完整拒绝日志有443外联、Metal缓存以及首场景/dev/dtracehelper拒写；重算汇总与result一致（含日志的duplicate-report行计数，不能当实际尝试总次数）。这些是**被拒**行为，不是成功外联/越界写。profile另允许本地Unix socket，按原模板如实保留，没有将其写成只有TCP规则。
3. pre/post NONE、无残留、CLEAN/quit_http、launched/eval及无panic均已核；**eval标记不能说明脚本成功**。两份host.log:44起到:93为50条[E]，:80/:85为保留名，:90–93为表达式解析错误。内部源码坐标比真实main偏移约3行，逐处对照源码，不机械照搬日志坐标。
4. 正确业务jail是 `home/.octosense/apps/octosense-repair/`。tasks/actions/events/state/隔离accounts与seed逐字节相同；首场景tasks为空，次场景仅原synthetic DRAFT，actions/events均为预置空数组，**没有新工单、回执、事件或实际拒绝记录**。文件不变说明业务未运行，不能判权限、恶意原文拒绝或恢复成功。
5. 两场景 needs_model=false，model_proxy_stats/model_proxy字段不存在、模型env未注入、billing_error为空；代码未发真实请求。本轮0次，历史作者3次仍是r3 Python来源，不升格为本轮G0-E或3组新描述成功。当前本地bundle digest=`f7564df1086823a72df132b49f4a76e235505a620cf2749f5a72078c00b86edb`，原工作目录manifest旧digest不同；本地签名副本保持业务字节，原包未改。hub check仍resource-scan REFUSED，不写完整准入PASS；native日志虽记录1 capability/1 host，不证明 http.fetch API或MiniMax访问已获准。
6. 本轮未生成私钥；原M2离线签名两私钥删除证据保留，阶段2再核keys目录为空；新seed/store无私钥。无需公開发布，也无402/欠费事实，NEEDS_ABRAM=no。
7. 独立审计第一次把宿主 `.system/*/main.splash` 也纳入业务源相等断言而失败，随后明确筛选签名export/install/.running的目标源，全部一致。没有修改源或证据以使断言通过；细节留于A.audit_correction。

### 相关既有用例逐项复核

|用例|结论与精确范围|
|---|---|
|G0-E|FAIL D01源码接线；当前原生真实MiniMax/关闭/拒绝/失败路径NOT_RUN，0请求。|
|T01|FAIL D01/D03/D06；三组独立新输入仅选定，未实际键入；真实提取、追问及未确认不OPEN业务NOT_RUN。|
|T03|事实最终guard接线保留；无空间/跨项目/缺联系人真实拒绝、输入保留及合法对照NOT_RUN。|
|T25|NOT_RUN真实恶意/矛盾provider；预置恶意原文未被处理，不能写“不改角色”已实测。假ID/主体状态拒分支仅源码范围。|
|T26|FAIL无可用原生手工界面且D05共用缺口；真实模型失败后人工成功与回读NOT_RUN。|
|T33|NOT_RUN真实同义/不同症状效果；不能用历史Python或合成DRAFT替代。|
|T34|FAIL D04伪来源/D06歧义；真实未知空间/无历史追问及可核来源对照NOT_RUN。|
|T35|FAIL D03源码；迟到/切项目/撤权/任务与事实版本变化交错NOT_RUN，白名单缺模型延迟/回包控制。|
|T36|NOT_RUN真实/假适配白名单运行；manifest仅storage，http.fetch与目标endpoint授权未证明；不假定octos替换已实现。|
|T37|FAIL D05精确最终回执/回读源码；真实读回超时/丢响应/原键重试/高版本恢复NOT_RUN，精确故障及连续同盘重开通道BLOCKED。|
|T38|固定快照/宿主/配置/seed与运行字节已核；同候选真实成功/失败全链NOT_RUN。|
|U02|FAIL原生空白及D03/D06；真实原话→补歧义→编辑→人工确认→回读NOT_RUN。|
|U07|FAIL无可用表单/重试出口，D05共用；真实重复点击/响应丢失/版本冲突/身份稳定NOT_RUN，精确控制不覆盖。|
|U08|FAIL空白UI无可见错误/无权限/过期恢复出口；真实状态恢复未执行。|
|U11|FAIL客户区空白；键入/滚动/面板切换稳定性NOT_RUN，不能据shell渲染/正常退出判应用交互通过。|

## 缺陷：只复核原编号及受影响回归

### D-M3-01 — P1 / 必修 / 未闭合：原生解析阻断，真实模型接线仍缺

- **文件/行**：`app/bundle/main.splash:248–330`（`ok:`结果对象/相关访问）、`:851、1047`（`let ok`）、`:1511`（三元表达式）；模型 `:202–222、244、271–330、3038–3059、3688–3782`；`manifest.json:2–3`、`model_config.json:47`。
- **触发**：本轮两场景按固定catalog `launch-hub`→tap→capture；加载失败无需登录/真实调用即可复现。接通加载后，任意新描述追真实HTTP body。
- **实际/预期**：两真实窗口均空白、50条解析错误。`ok`保留名及表达式不兼容固定宿主；模型body与r4相同，丢弃spaces/assets参数，未发送真实事实/绑定，未使用OCTOSENSE_MODEL_ENDPOINT，HTTP能力无实证。预期先可操作加载，再从授权新输入经代理产生合法、可核建议。
- **根因/影响**：Python契约不等于固定宿主语法/API；调用点存在不等于真实接线。阻断AI和人工全部桌面核心路径。加载相关M2/M6位置仅作为直接依赖回归，不开展后续业务审查。
- **证据**：H两帧、两host.log:44–93（保留名:80/:85）；S/source-traces、function-delta；A；M2 r6 D01。
- **具体改法**：在固定宿主支持语法内修保留名/对象字段及访问、三元表达式；核http.fetch真实API与最小许可，用proxy endpoint override发同源授权事实/不可变绑定，不读取实际密钥到宿主，不放开公网直连。
- **验证**：新同字节候选harness无parser错误且表单可操作；受支持输入通道实际提交阶段笔记三组新描述，含歧义/缺项/无历史及恶意原文；总请求≤10、付款错误立即停，核请求事实、来源及UI失败出口。当前授权足够。

### D-M3-02 — 部分闭合保留；剩余并入 D03/D05，输入运行未成立

- **文件/行**：main`:3656–3685、7214–7257`。相同文本no-op、按钮前同步与r4相同，认可已改善。
- **证据/实际**：当前帧无TextInput，未实际中文输入；按按钮同步不能证明回包时同步。根因及修法分别归D03/D05，不重复新增独立P1。
- **验证**：表单可运行后做真实编辑/取消/重试、同文no-op和AI/人工权威确认；目前不声明完整闭合。

### D-M3-03 — P1 / 必修 / 未闭合：展示、采纳与首次确认缺当前绑定守卫

- **文件/行**：main`:3246–3341、3656–3670、3749–3767、3930–3955、7236–7247`。
- **触发**：A请求迟到期间只键入B；APPLIED(A)后改B→采纳→首次确认；任务/权限/事实变化后采纳。
- **实际/预期**：源码回包门只查旧TASK_INPUT且自动apply；editRawText清active/rid不清APPLIED，UI采纳谓词仍true。新确认恢复仅看版本超过失效快照，不重新核AI原文/请求绑定。task_version只比请求快照，事实/证据版本未接当前值。预期展示/采纳/执行三处对当前输入与完整上下文核验。
- **根因/影响**：建议与已采纳草稿未分离，编辑进展不等于合法重新确认；旧建议能被当新输入建议的源码路径尚在。**本轮未执行动态交错**，不声称新原生旧建议已落库。
- **证据**：S/source-traces、function-delta（确认变化明确）；H表单未运行。
- **具体改法**：独立暂存建议，回包检查实际控件；编辑废旧建议，采纳/首次确认共用当前输入/请求/草稿/任务/项目/主体/事实/证据/到期守卫，明确转人工重新确认可继续。
- **验证**：三种交错逐步核截图、草稿与命令/回执；合法未改对照可继续，旧回包不展示/覆盖/执行；再测切项目/撤权/改任务与事实。

### D-M3-04 — P1 / 必修 / 部分闭合：事实守卫保留，来源仍不可核

- **文件/行**：main`:3113–3141、3157–3223、3502–3525、3912–3918`。
- **触发**：合法候选ID配不存在的巡检/维修日志来源，经解析/采纳/确认；合法可核来源作对照。
- **实际/预期**：sources只验对象/非空；没有事实/版本/原文引用关系检查。假ID/跨项目/停用/服务关系守卫与最终确认接线保留，认可子项改善。预期来源可定位且符合当前授权，未知明确unknown。
- **根因/影响**：schema代替证据校验，阻断“有来源”核心目标。预置伪来源本轮未被业务解析，不当成新动态接受反例。
- **证据**：S/source-traces.parseModelReturn/_validateDraftFacts；function-delta相同；H次场景仅synthetic seed保留。
- **具体改法**：用同源事实ID/版本/原文范围结构，核存在性、权限及关联；陈旧/不存在/越权引用拒绝或标未知，不当确认依据。
- **验证**：合法来源、伪来源、假设备、存在的B项目事实、非法状态、恶意原文分别跑，核UI/草稿/主体/零事件；采纳后撤用也应拒。

### D-M3-05 — P1 / 必修 / 部分改善：AI/手工仍无权威最终成功协议

- **文件/行**：main`:3957–3976、3989–4075、4221–4238`；M2关联提交`:2666–2731`及M2 r6 D02/03/04。
- **触发**：OPEN内存状态但最终确认失败/未知、关联事件失败、丢响应后再次确认、较高版本原动作查询；AI和人工分别测。
- **实际/预期**：confirm仅验task_id/status就关面板/写CONFIRM_BIND；不核commit_ok/confirmed_open/确认final/事件。create已删除提前saveTasks/成功提示，认可；仍先newId，返回创建rid而非确认final，根据内存t.status包装成功。确认先改OPEN再commit，失败时内存OPEN不足以证明权威成功。预期精确最终action/final/event与任务读回成立才成功，未知可按原键恢复。
- **根因/影响**：创建/确认和结果消费未统一持久意图及关联恢复，AI/人工共同受影响。**本轮业务未运行，无新增实际部分提交反例**。
- **证据**：S/source-traces.confirmDraftModelBound/createDraftFromPanel及差异；当前confirmDraft；M2 r6；A业务seed不变。
- **具体改法**：持久不可变确认意图，返回实际确认action/final/unknown/rejected；查精确原动作与完整关联事实后成功，原键对账不newId重建；只修阻断本模块的最小依赖。
- **验证**：AI/人工各成功+读回失败+丢响应+重复确认+事件失败+同盘重开，核一任务/唯一事件/匹配final，不以flags替代权威查询。

### D-M3-06 — P1 / 必修 / 部分闭合：默认候选被当人工解决歧义

- **文件/行**：main`:3346–3401、3900–3977、4023–4029`。
- **触发**：模型默认chosen_asset在alternatives，用户未选择；设备/空间定位缺项但problem非空；确认未解决核心定位歧义。
- **实际/预期**：helper把默认候选视为已解决所有ambiguous字段；部分定位缺项可因problem文字已填而resolved，确认不阻断剩余核心歧义。预期只按对应字段实际人工补充/选择解决。
- **根因/影响**：自动值冒充人工决定，报修对象不能可靠确认。时间保留改善不回退；真实时间解析未测，不新开无关缺陷。
- **证据**：S/source-traces._computeResolvedFields/_computeResolvedAmbiguous/confirmDraftModelBound；function-delta全部helper相同。
- **具体改法**：逐字段维护未解项及人工选择记录，确认核剩余核心定位歧义；沿用空间合法而设备可未知的旧人工报修规则，不扩大为空asset一律拒。
- **验证**：未选默认备选拒核心歧义确认、有效选择可继续、撤销再失效；未知空间追问、合法人工无设备及合法时间编辑有对照。

### D-M3-07 — 源码范围闭合保留；真实审计路径 NOT_RUN

- **文件/行**：main`:3844–3882`；recordModelMeta与r4相同，白名单不含raw_text/preview/key。
- **证据/判断**：无新增源码泄密证据；本轮未输入凭据/调用模型，不能宣称真实秘密路径已测。无需重复P1；运行后核真实审计/日志/缓存，不能把零调用作为脱敏通过。

## 判定

- **最终结论：FAIL**。范围为明确历史交接加用户授权当前快照的原编号闭合、独立原生加载和受影响回归；不是原r4字节的新全量测试，也不是后续模块验收。
- 必修：**D-M3-01、D-M3-03、D-M3-04、D-M3-05、D-M3-06**。均阻断当前核心功能；没有因视觉/锦上添花建议判FAIL。D02/D07改善保留，不重复要求修已闭合根因。
- 原生加载/空白UI是 **FAIL**；因加载失败未到达的新输入、模型、权限、采纳、建单与恢复业务为 **NOT_RUN**。**没有ABORT**，不再引用沙箱rc71/pgrep rc3当BLOCKED。
- 仅测试通道记 **BLOCKED**：固定发行宿主此前独立M2 r5记录拒 `type:`（该报告“证据边界”及host.log:40/42来源），当前白名单未提供已验证替代中文/登录输入、模型延迟/受控回包注入、逐写点中断/读回故障/丢响应、原key/payload注入和连续同盘重开。这些必须由构建/驱动提供受支持能力；本轮没有重复未知动作或自己改harness/业务来造通过。属于技术缺口，NEEDS_ABRAM=no。
- M2定向回归：本轮同源码再次复现空白/解析问题；创建提前主写改善已核，确认与可靠回执依赖仍缺；**不改M2门禁**。M0/M1/其他模块继续挂账，不开展无关扩审。
- 门禁：`docs/optimization/2026-10-09-desktop/GATES.json` 只更新M3审查字段并保留旧Review来源；历史candidate_id不冒改为作者新候选，新增review_candidate_id/快照摘要记录当前实际对象。原38业务/12UI/P0台账不删改，本轮未形成可提升业务状态的新PASS，ACCEPTANCE.json保持原样。
- 不允许执行下一模块。修复顺序：固定宿主可操作加载→授权MiniMax代理/事实/绑定→旧建议和来源/歧义守卫→AI与人工的精确最终回执/回读；逐项按上面原编号复验，不发散。
- 身份与provider已裁决、隔离离线签名已授权，本地安装可行；0模型请求、无欠费/402事实、无需公开发布。**NEEDS_ABRAM=no**。
