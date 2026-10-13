# M7 独立 Review r2

- 最终结论：**BLOCKED**。候选 `M7-r2-worktree`；base `M7-r1-worktree`。D-M7-01/02/03 均闭合；没有新增 P1。核心同版本目标 launcher 运行缺口 B-M7-01 仍未解阻，不能仅因静态/准入全绿判 PASS。
- 审查者 / 日期：本主会话唯一独立审查方，2026-10-10 Asia/Shanghai；未派代理。置信度：字节/准入/Store/重建 **高**；真实桌面/业务/模型 **未知**。工具未暴露可核主会话路由、自身 createdAt 或设置标题能力，不能确认 Router/gpt-6.1-sol 或声称实际改名。
- 作者报告：`reports/M7_IMPLEMENTATION_r2.md`；交接 `runtime/optimization/2026-10-09/M7/r2/CANDIDATE.json`。按 GATES 的 candidate_id + implementation_report 锁定 r2，未按文件时间选择。
- 被审 HEAD：`8d730569546cb57310944bb299695134df773b9d`，dirty。工作区主源 SHA-256 `5c12041e419de1137c6e525bd74e5dc885e684932818c0230d62d606849e31db` / 283910 字节；最终主源 `ed9107f14fb56d0fb4a135d6c4238700d792ccda70f6c00ac5763493470998f6` / 283933 字节。差异仅 :3584 一行注释，实际增加 **23** 字节，不是报告的 4 字节。
- 最终目录：`runtime/optimization/2026-10-09/M7/r2/release/octosense-repair-0.1.0-c/`（12 文件）及 `release/release-materials/`（5 文件，含摘要证明本身）。官方 BLAKE3 `a7451d34d7aa808bc534df0350b5e501cc5fc83a9861f296e9ea4574c9b2ea10`。
- 审查起止：包、材料、主源内容/大小完全一致；保存 start-status、start-dirty.diff、逐文件/宿主哈希与 end-audit。两份空目录重建连包外材料均与交接逐字节一致。没有 reset/stash/修业务代码。
- 前置：M6_REVIEW_r2 为 FAIL，D-M6-02/03/04 保留。依本次用户明确挂账授权执行 M7；不将未通过前序改成 PASS，也不单因其 FAIL 拒收。M6 主源基线准确定位，M7 仅注释/包装差异，不扩审前序。
- 目标宿主：指定 r3 提取 `OctoSense.app/Contents/MacOS/octosense` SHA-256 `3e1279635cc736483ce5b628886b47b63f96b66cbedae13ec900f90cb7fe2c90`；kernel `a3e46a4557bae8f2bc41b945d1129dca9d2f5780f3735f9966d1d07de5c6e152`。两版 Hub 和官方 Store 探针哈希保存在 start-audit，未用 standalone card-host 冒充 launcher。
- 阅读范围：AGENTS、M7 CONTEXT、r1 Review 缺陷与相关定义快照、r2 报告/清单/生成脚本/最终材料、04 模板；补核 02 和 M7 硬验收段落。00/01及根基线沿 CONTEXT/r1 归纳，遵守修复轮不重通读要求。原64定义与当前 ACCEPTANCE 逐个比较一致。
- 已运行：新隔离预检；两版 unsigned check/独立副本 stamp；当前 digest 离线 catalog verify、官方 Store install_staged/重建 may_run、篡改拒绝/恢复；临时公钥 signed check；两空目录重建与篡改 digest 检测；作者静态 acceptance 25/25 和 consistency 27/27 独立重放；异常 CLI 私钥清理注入；scan 生成及七问独立范围判定。
- 未运行：launcher/真实桌面 UI/实际业务命令权威回读/正常及退回重做/重复及失败业务链/业务重启/真实模型。静态 52 项不代替原64验收，也没有把作者 M6 188 条升级为独立 PASS。
- 证据根：`runtime/optimization/2026-10-09/M7/review-r2/`；下表证据相对此根。测试 HOME/CFFIXED_USER_HOME/TMPDIR/XDG data/config/cache/OCTOSENSE_HOME/app-data/Metal cache 全重定向到此根，见 env.json；仅操作副本与合成 catalog，不改作者候选/原始业务数据。没有联网、publish、listing、push、Issue、消息或 provider/身份配置。首个工具调用按上级记忆流程做过项目外记忆索引只读检索（范围例外），没有项目外写入，其后项目审查限定项目内。

## 必需检查

|检查|独立操作|期望|实际|结果|证据|
|---|---|---|---|---|---|
|旧 D-M7-01 准入|两版 Hub 对最终目录 check，沙箱签名后提供临时公钥 check|真正准入通过|两 unsigned rc0；signed 不带公钥 rc1，带沙箱公钥 rc0；只在测试上下文供钥，未注册公开身份|旧缺陷 CLOSED，准入子项 PASS|results/admission.json、signed-check.json、local-store-validation.json|
|旧 D-M7-02 冻结|逐文件 SHA/size、两版 stamp、两空目录重建、篡改/恢复|字节可定位且摘要一致|12 包文件及4被摘要的材料零失配；证明自身在包外单独保存 SHA；两重建全部17文件一致|旧缺陷 CLOSED，字节子项 PASS|results/start-audit.json、cold-rebuild.json、end-audit.json|
|旧 D-M7-03 口径|与当前原64定义逐条对照、重放静态代码|编号目的保留，静态不冒充运行|原64保留未测，静态另用M7R2；25/25及27/27仅子项|旧缺陷 CLOSED；文案建议见 A03|results/acceptance-matrix.json、static-replay.json|
|硬1 全门槛实证|逐项审核当前64证据适用范围|核心原生结果实证|无同候选原生实操；沿B01不能取得|BLOCKED|preflight.json、acceptance-matrix.json|
|硬2 正常/退回/失败/重启/模型|先预检隔离及清理，再决定后台启动|目标 launcher 安全运行与权威回读|sandbox rc71、pgrep rc3，未启动；模型OFFLINE|BLOCKED；模型 NOT_RUN|preflight.json、原64表|
|硬3 材料一致|核最终文件/旧图/说明/源差异|当前字节对应截图与演示|包与源码差异定位准确；六图与r1旧图一致且已披露；无当前演示|字节子项 PASS；同版本桌面材料 BLOCKED|start-audit.json、end-audit.json、listing.json|
|硬4 准入/审阅/干净运行|check、scan、本地catalog install_staged、Store重建|准入与实际运行均成立|check/安装/Store重建成立；scan七问本主审route=human-review；干净启动未跑|功能子项 PASS；总体 BLOCKED|admission.json、scan-run.json、scan-independent-review.json、local-store-validation.json|
|隔离离线签名/失败恢复|当前digest造离线catalog；tamper不重新stamp；恢复重试；CLI异常注入|拒绝篡改，恢复可用，私钥清空|catalog verify rc0；安装/Store重建rc0；tamper rc1；恢复rc0；两签名key删除，异常注入两key也清空|PASS（沙箱本地安装路线）|local_store.py、local-store-validation.json、cleanup-injection-run.json、end-audit.json|
|硬5 四种交付状态|读本候选清单和历史回执引用|分开本地/发布/赛事/收录|本候选无外部回执，不执行被禁止动作；旧0.1.0-b回执仍只属历史|状态区分子项 PASS；外部 NOT_RUN|CANDIDATE、原64表、GATES历史|

`python3` 首次运行 Store 脚本因缺 cryptography 导入失败，尚未创建私钥；改用项目既有 `backend/.venv/bin/python -B` 成功，不安装依赖、不联网。完整命令/stdout/stderr 保存在 store-run*.json。Store 探针调用官方固定源码接口，不是启动 launcher；Store重建也不是业务重启。scan 未配置工具 --reviewer，没有把退出0当审阅PASS。

## 相关既有用例逐项复核

下表沿原定义；历史是旧台账状态，不认可自动适用于 M7。修复轮逐项复核证据及受影响项；环境阻塞项没有实际执行。完整结构化表见 results/acceptance-matrix.json。

|编号|原定义|历史|本轮|实际范围|
|---|---|---|---|---|
|G0-A|固定版本、原生脚本构建与真实启动|PASS|BLOCKED|两版 check、digest 与干净包重建子项 PASS；原生启动 B01 BLOCKED。|
|G0-B|真实可信身份、授权与独立会话|NOT_RUN|BLOCKED|演示身份 fixture，沿 M2 挂账；可信来源及独立会话未执行。|
|G0-C|唯一事实源、原子一致性、并发与恢复|PASS|BLOCKED|Store 重建通过仅是安装恢复；业务唯一事实源/事务/并发/恢复未执行。|
|G0-D|真实附件写入、回读、归属及失败恢复|NOT_RUN|BLOCKED|真实附件写入/回读/归属/失败恢复未执行；隔离签名不替代此项。|
|G0-E|系统助手实际调用与能力关闭/拒绝/失败路径|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|G0-F|提醒恢复、去重与官方任务意图视图路线|NOT_RUN|BLOCKED|提醒恢复/去重/官方意图视图未执行；M6 D02 保留。|
|T01|真实模型将报修原话提取为草稿；原文保留；缺失位置要求补充；未确认不OPEN|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T02|同创建key重发返回同一task_id；同key不同内容409；同文本不同源事件允许新建|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T03|无空间/跨项目空间/缺联系人提交失败，草稿内容不丢|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T04|两个独立连接同时接同一OPEN任务，只一个成功；一个承接者、一条成功接单事件|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T05|技能不匹配或无项目权限拒绝；经理分配事件记录经理身份|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T06|经理改派SCHEDULED任务，旧预约取消、新承接者有效、任务ACCEPTED；旧技工不能开工|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T07|编码与asset:载荷解析到相同设备；伪造ID、其他项目ID、归档设备拒绝|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T08|机房安装设备可绑定其有效服务房间；仅同安装位置但无服务关系不能误绑定|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T09|未绑定设备不能开工；IN_PROGRESS技工不能自行换设备，经理更正有旧值/新值/理由|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T10|技工提议不会直接SCHEDULED；非报修人不能确认预约|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T11|同技工两任务并发确认重叠区间，仅一成功；相邻区间都可确认；跨项目同技工仍查冲突|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T12|改约提议待确认时旧预约有效；新确认后旧SUPERSEDED；拒绝新提议仍保留旧确认|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T13|过期提议410；定时器未运行时仍拒绝过期确认；客户端伪造当前时间无效|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T14|Asia/Shanghai输入换算UTC毫秒准确；“明天下午”必须核对具体日期；end<=start拒绝|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T15|旧task.version操作409并刷新；前端不自动覆盖；阶段不可写任意百分比|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T16|提交成功但响应丢失，同key重试返回原action_id；任务版本不重复增加|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T17|SSE断线期间发生动作，重连/全量回读获得最新状态；不回放为第二次业务写|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T18|用户只能看到可见任务事件；无权task_id不能通过列表/搜索/事件/附件探测数据|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。 M6 D02/D03/D04 原独立结论保留，不在本轮关账。|
|T19|无证据/他人任务附件/QUARANTINED附件不能完工；合法附件实际可下载|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T20|技工完工后仅AWAITING_ACCEPTANCE；验收人不能为当前承接者，多角色也不能绕过；经理代验收无理由拒绝|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T21|验收退回IN_PROGRESS，旧证据保留；第二次完工有新completion_id，再验收COMPLETED|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T22|在任务/预约/事件写入间注入异常，全部回滚；不存在已接单但无回执记录|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T23|进程在预约提醒前重启，作业恢复；重复执行只一份站内通知；已改约旧作业不误触发|NOT_RUN|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。 M6 D02/D03/D04 原独立结论保留，不在本轮关账。|
|T24|直接调用旧Web、旧MCP、runner内部写路径不能绕过；比赛模式图谱写/reset不可用|NOT_RUN|BLOCKED|静态包无 Python 服务及已知本地 HTTP 调用子项成立；旧边界绕过/本地完整验收未执行。|
|T25|工具数据缺失/相矛盾时模型标未知；伪造状态输出不能写任务；恶意原文不能改角色|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T26|模型失败有明确错误与人工兜底；真实模型测试标失败，不以假模型成功替代|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T27|未配置连接器无网络请求，无external_id，无SUCCEEDED；本地可独立完工验收|PASS|BLOCKED|静态包无 Python 服务及已知本地 HTTP 调用子项成立；旧边界绕过/本地完整验收未执行。|
|T28|原生宿主打开同一task_id、操作并回读、重开状态保留；仅Web成功不能通过此项|FAIL|BLOCKED|当前 digest 的 Store install_staged/重建/may_run 子项 PASS；原生任务操作/回读/重开 BLOCKED。|
|T29|原生grant关闭/退出/到期后不能继续调用；共享卡不能继承发送者授权|FAIL|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T30|自己收藏任务重登后仍在；其他用户收藏不互相影响，task.version不变|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。 M6 D02/D03/D04 原独立结论保留，不在本轮关账。|
|T31|取消释放预约并保持事件；终态不能再次开工/验收；再次故障新建关联任务|PASS|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T32|配对码过期/重复消费/错误poll_secret拒绝；Web审批绑定当前用户；应用脚本拿不到token|NOT_RUN|BLOCKED|B-M7-01：未启动目标 launcher；同候选实际操作、权威结果及失败/重启路径无实证。|
|T33|同一维修意图的多种说法得到同一类合法操作；不同地点/症状不能强行归成同一模板|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T34|未知空间、多个设备候选、无历史经验时主动补充；引用不存在则拒绝建议|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T35|模型生成期间任务被改派/改约，旧建议不得沿用旧角色或旧版本执行|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T36|假适配器和真实配置均只能使用白名单；未来octos适配器按同组契约回归，不假定已实现|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T37|模型声称成功但无回执判失败；真实提交后回读超时标待核验，重试不重复写；更高版本不误判旧成功|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|T38|保存模型/提示/数据/宿主版本；同一组成功与失败场景可重跑，真值不泄漏给Agent|NOT_RUN|NOT_RUN|model_config.enabled=false；真实模型成功/失败链未执行；前序挂账，不用静态 probe 替代。|
|U01|三角色分别能从首屏找到自己的待处理事项，说明当前阶段和下一处理人|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U02|从原话到结构化草稿可修改、补歧义、保留原文；模型失败可人工继续|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U03|同一任务在三角色中事实一致，动作按权限变化，承接者不能自验|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U04|当前预约与改约提议清楚区分；冲突、过期不显示成功|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U05|设备安装位置与服务空间分开展示，来源和选择依据可读|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U06|进度、完工、验收不同；退回后历史与附件保留|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U07|重复点击、响应丢失、版本冲突、离线等情况下输入和任务身份不乱|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U08|空态、骨架、长文本、附件失败、无权限、过期建议都有可继续操作的出口|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U09|1280×800及窄窗布局、文字放大后主要动作/错误信息无裁切或覆盖|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U10|键盘完成主要流程，焦点清楚；颜色不能成为唯一状态线索；记录对比实测|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U11|真实宿主中滚动、输入、面板切换稳定，动效不阻塞操作，不出现假的进度反馈|NOT_RUN|BLOCKED|当前原生桌面 UI 未执行；六图 SHA 与 r1 旧图完全一致，已披露；不证明当前 UI。|
|U12|独立人员根据2–3分钟演示能说明完整操作、实际结果与一个失败/空状态；证据对应同一版本|NOT_RUN|NOT_RUN|同版本 2–3 分钟正常结果与失败/空态演示缺失，NOT_RUN。|
|P01|同一候选版本成功链、退回链及重开恢复独立复跑|PASS|BLOCKED|正常链/退回重做/业务重开均未执行；安装恢复不替代。|
|P02|完整源码和依赖版本、干净环境启动/构建说明|PASS|BLOCKED|两空目录重建、全部文件摘要和 dirty 定位子项 PASS；目标宿主干净启动仍 BLOCKED，完整依赖来源不能由 mtime 推断。|
|P03|最终包准入check及实际scan审阅通过|PASS|BLOCKED|两版 unsigned check 及沙箱 signed check PASS；scan 已生成，本主审七问结论 human-review，真实行为证据缺口未闭合。|
|P04|真实演示、两张关键截图、需求/数据来源/限制/隐私/许可材料|PASS|BLOCKED|本候选截图/演示缺失；旧素材已披露但不证明同版本。来源/媒体断言 A02 建议保留。|
|P05|源码与包摘要一致，全部必需缺陷关闭，交付清单齐全|PASS|BLOCKED|源码/包摘要、交接与三项旧 P1 修复子项 PASS；核心运行 B01 仍未闭合。|
|P06|固定公开源码与Hub Issue实际递交回执|BLOCKED|NOT_RUN|本候选无对应外部回执；本轮禁止动作，NOT_RUN；原台账及 GATES external_delivery 历史保留。|
|P07|维护者商店收录结果|BLOCKED|NOT_RUN|本候选无对应外部回执；本轮禁止动作，NOT_RUN；原台账及 GATES external_delivery 历史保留。|
|P08|赛事正式提交入口回执|BLOCKED|NOT_RUN|本候选无对应外部回执；本轮禁止动作，NOT_RUN；原台账及 GATES external_delivery 历史保留。|

## 缺陷闭合、阻塞与建议

### D-M7-01 / 原P1 / CLOSED

定位：r2 `scripts/m7_release_stage.py:48`（注释替换）、`:151`（包外材料）；最终 `main.splash:3584`。原触发：最终 Hub check 拒绝 LICENSE 无扩展名及注释中的越界字面路径。当前两版 check 均 rc0，移出的材料可定位；signed副本仅未供临时公钥时拒绝，提供本地测试公钥后rc0。原根因及影响是包装扫描拒绝，已修；未要求业务改动。回归证据 admission/signed-check/local-store-validation；继续保持 check、Store、原生实操分别记录。

### D-M7-02 / 原P1 / CLOSED

定位：r2 `scripts/m7_integrity_recompute.py:32` 真实stamp、`:96` 包外材料摘要；最终 INTEGRITY:4/:12/:30。原根因是先冻结再改manifest且SHA冒称BLAKE3。当前所有记录 SHA/size匹配，真实digest正确，冷重建两次等字节，篡改变化/恢复成立。摘要证明自己不自引用，其 SHA 在本审 start/end-audit 中另存；不是缺一项包内文件。继续以最终write后冻结与全文件对比验证。

### D-M7-03 / 原P1 / CLOSED（残余文案 A-M7-03 建议）

定位：r2 `scripts/m7_acceptance_run.py:22` 独立静态编号；`results/acceptance.json` 原64mapping；实施报告 §6.3。原触发是用静态PATH检查替换真实业务定义，REFUSED当PASS。当前自有检查独立编号、真实check已通过、原64未冒充运行PASS；本审表沿权威定义逐个保留。计数全绿仍不证明M7核心运行，B01持续。无需重写前序业务。

### B-M7-01 / BLOCKED / 核心运行与隔离解阻

- 文件行：`CONTEXT_M7.md:45`/:51、`app/README.md:77`/:80；本审 `isolation.sb:3`–:5、`results/preflight.json`（完整命令/结果）。
- 触发：`sandbox-exec -f <review-r2/isolation.sb> /usr/bin/true` → rc71，`sandbox_apply: Operation not permitted`；`pgrep -fl <指定launcher Contents/MacOS>` → rc3，`Cannot get process list`。本轮新执行，不沿用作者声称。
- 实际/预期：不能施加native文件写隔离、枚举进程并确认清理。仅设HOME不能证明全部系统缓存均项目内；按最高隔离约束不启动。期望先满足写入全部项目内、禁网络、后台进程可结束且新增窗口可核验，再运行当前候选。UI和业务实际表现未知，不杜撰崩溃/裁切/成功。
- 根因：当前工具执行环境拒绝sandbox_apply和进程枚举；不是缺公开发布权限。核心影响：G0-A/T28/P01及全部实际UI证据无法取得，M7可复现桌面候选目标未成立，即使无新增P1仍不能PASS。
- 具体解阻：在能施加相同项目写隔离及禁网络、枚举/终止进程和检查窗口的本地执行环境重跑预检；用指定launcher后台启动，HOME/app-data/log/cache全部进入 `runtime/optimization/2026-10-09/M7/` 新隔离根，不用 --help。对最终digest操作正常、退回重做、失败、重复与业务重启，保存实际命令/权威回读、真实桌面及影响T/U证据；立即结束本轮进程，确认本轮窗口归零。
- 不修挂账前序缺陷、不切真实provider/身份来源；如后续证明必须变更这些授权边界，再单独记录 NEEDS_ABRAM。当前本地安装路线实证可行，**NEEDS_ABRAM=no**。
- 本轮未启动launcher、未新增宿主窗口；现存他人窗口因枚举失败仍 UNKNOWN，未盲杀，不能写“桌面已无残留”。

### A-M7-01 / P2 / 建议挂账（沿r1，仍OPEN）

定位：`CONTEXT_M7.md:51`仍称用户禁止后台启动；`app/README.md:77`–:80 使用旧standalone card-host，:89–:99仍是项目外/tmp旧链。根因是旧章节/授权摘要未同步。触发是按文档复跑；预期当前段落写已授权指定launcher后台测试及明确预检，实际旧命令不满足本次隔离。影响为阅读/启动误导；本轮没有执行这些旧命令，无已发生越界。建议同步当前入口，旧段标历史，禁止把旧card-host换名当目标launcher；解析路径并检查全部输出均项目内。只建议，不因此FAIL。

### A-M7-02 / P2 / 建议挂账（沿r1，PARTIAL）

定位：release-materials `SOURCES.md:8`/:10（尚待填commit与不存在的m7_host_toolchain_snapshot.py名称）；`PRIVACY.md:8`仍断言旁白/原创配乐。来源/媒体断言仍未证实；hash能定位binary，不等于源码commit可复构。实际私钥正常及异常路径均删除，清理部分已关闭（CLI异常注入证据）；剩余根因为旧来源/媒体文案复制。建议只写可核来源及同版本媒体，未知注明未知；验证回读源码固定标识、定位媒体和音轨，不需扩做媒体作品。本轮无同版本媒体，未发布，不新增P1。

### A-M7-03 / P2 / 建议：实施报告仍有汇总口径及计数笔误

定位：`M7_IMPLEMENTATION_r2.md:26`–:27（硬3/4总PASS）、:34/:37（HEAD误标内容hash、最终SHA仍写工作区hash）、§3/§6.2（4文件/22计数）；`INTEGRITY.txt:25`/:35（4材料/16总数，不注明排除证明自身）。触发：报告与最终目录、static-replay、start-audit逐项比较。实际为包12+材料5=17，27条consistency，注释增23字节，最终SHA ed9107…；干净包重建PASS不能称launcher干净启动PASS，旧图也不能使完整硬3PASS。根因是表格沿旧草稿未同步。具体改法：写清各子项/总体BLOCKED、准确SHA/字节和计数、声明摘要自身排除并另存hash。验证使用目录清点、SHA和实际测试结果自动核表。不据此判FAIL；原64mapping已保留未测且冻结实物一致。

## 判定

|对象|结论|范围|
|---|---|---|
|M7本地发布准备|**BLOCKED**|三项旧P1闭合；包装/冻结/安装成立；目标launcher核心实际运行未成立|
|外部发布/Hub递交|**NOT_RUN**|本候选无实际回执；不沿用旧0.1.0-b Issue证明新版本递交|
|赛事正式提交|**NOT_RUN**|本候选无赛事回执；未执行|
|维护者商店收录|**NOT_RUN**|本候选无收录回执；本地离线catalog及安装不等于收录|

- 必修P1：无新增；D-M7-01/02/03 CLOSED。唯一本轮核心阻塞 B-M7-01，解阻条件已给出；建议不作为FAIL理由。没有把前序所有挂账拉回本轮修复。
- 受影响回归：同主源注释差异核定、当前包准入/摘要/冷重建/本地安装完整复验；M0–M6独立结论及原ACCEPTANCE历史保留，没有重跑且不宣称通过。
- 门禁：仅写 GATES 的 M7 status/审查字段/历史；本轮 review_report 指向 reports/M7_REVIEW_r2.md；作者实施字段与其他模块/external_delivery不改。完整原64状态放本报告及审查字段，不改原ACCEPTANCE来制造PASS。
- 下一模块：**不允许**，不给下一模块入口。留在M7取得已授权的安全隔离目标launcher实证；无需公开publish/新provider/新身份配置授权。源/包若变化，重冻新candidate_id并定向复验，不能把当前安装成功当未来包已通过。

STATUS=BLOCKED
NEEDS_ABRAM=no
