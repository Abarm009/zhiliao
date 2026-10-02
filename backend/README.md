# wagent-backend —— 设备台账知识图谱 · 设施运维 Agent

两大功能，同一进程：

1. **GraphRAG**：从「设备信息登记表」出发的知识图谱服务，图谱会随工单**自己长大**。
2. **ops 设施运维 Agent**（`wagent_backend.ops`）：11 个冻结契约工具 + 三层记忆（台账 / 90 天工单原文 / 归纳洞察）+ 三栏回放台（租户企微视角 / 工具流水 / 设施经理视角）。

- **存储**：图谱 networkx + JSON；ops 用 SQLite（`data/ops.db`，自动建库灌种子）——零外部服务
- **模型**：qwen3.7-flash（OpenAI 兼容协议，任何兼容网关都可替换）；向量 DashScope text-embedding-v3（1024 维，离线自动回落本地哈希）
- **入口**：Web 可视化 · MCP server × 2 · CLI

## 快速开始

```bash
cd agent
uv sync                  # 建环境装依赖（含 pytest 等开发工具，一条命令全齐）

# 1) 配置模型：编辑 .env，填入你的 DashScope key（文件已 gitignore，不会进仓库）
#    LLM_API_KEY=sk-xxxxxx
#    LLM_MODEL / LLM_BASE_URL 有默认值（qwen3.7-flash @ DashScope），不用动

# 2) 起 Web 界面
uv run kg-web            # http://127.0.0.1:8700        设施运维 Agent 三栏回放台（默认首页）
#                           http://127.0.0.1:8700/graph 设备台账知识图谱 + 智能查询 + 抽取
#                                                      （层级展开：默认只到楼层，单击楼层→房间→设备逐层展开，
#                                                       环散布 + 顶栏一键收起；echarts 已本地化，离线可用；
#                                                       力导动画常驻，不做定格）

# 3) 其他入口
uv run kg-demo           # CLI：图谱统计 + kg_* 工具逐一人话示例（无需 key）
uv run kg-demo --chat    # 终端 LLM 问答（读同一个 .env）
uv run kg-mcp            # 图谱 MCP server（stdio）
uv run ops-mcp           # 运维 11 工具 MCP server（stdio；--http 起 8766）
uv run pytest            # 183 个测试（假 LLM 只在测试里，运行时全是真模型）
uv run python tests/e2e_ops_real.py   # 真实模型端到端冒烟（3 个故事）
```

> 运行时（聊天/抽取/运维 Agent）**永远调用真实模型**，没有任何假实现；
> 假的 LLM 函数只出现在 tests/ 里，用于离线跑测试。

## 目录结构（解耦分层）

```
agent/src/wagent_backend/
├── graphRAG/              ← 知识图谱核心（无 web/LLM 依赖，只被依赖）
│   ├── schema.py          #   本体：8 类节点 + 8 种关系 + pydantic 模型
│   ├── store.py           #   GraphStore：networkx + JSON 持久化 + 全部查询接口
│   ├── seed.py            #   登记表种子数据（唯一原始数据源）
│   └── extractor.py       #   TripleExtractor：LLM 抽三元组 → 本体校验 → 入图
├── ops/                   ← 设施运维 Agent（与图谱完全隔离的子包）
│   ├── contracts/         #   冻结契约内嵌副本（enums + schemas + 11 工具注册表）
│   ├── data/              #   SQLite L1/L2/L3 建库 + 演示种子 + SQL 仓储
│   ├── tools/             #   11 个工具实现 + 注册表 + 中文摘要 + MCP 第二入口
│   └── agent/             #   会话 = 事件日志（dsh 五层记忆）+ 流式主循环 + 压缩/裁剪
│       ├── events.py      #     L0 追加型日志 + L1 surface 投影（模型可见面）
│       ├── surface.py     #     3 类 surface 事件强制 surfaceOp（append/replace）
│       ├── store.py       #     L4 持久化：首行 session 头 JSONL + 写-behind + 撕裂尾容忍
│       ├── projections.py #     L2 投影注册表（整值/同引用零通知/水位 cell）
│       ├── pruner.py      #     工具结果中段裁剪（8192/4096/1024 + 单 marker）
│       ├── compaction.py  #     L3 压力压缩（0.8×窗口触发，dsh checkpoint 模板）
│       ├── runner.py      #     流式主循环（chunk 留痕 → 组装 → 工具 → Decision）
│       └── prompts.py     #     记忆档位提示词（off/l1/l1l2/full）
├── llm/
│   ├── client.py          ← OpenAI 兼容客户端（qwen3.7-flash，env 可配；stream → StreamChunk）
│   ├── assembler.py       ← StreamChunk 块组装器（dsh 判别联合 + 流尾契约）
│   └── embedder.py        ← 1024 维向量（DashScope 真实 / 本地哈希兜底）
├── tools/                 ← 图谱 LLM 工具层
│   ├── kg_tools.py        #   7 个 kg_* 工具 + 注册表 + OpenAI schema 导出
│   ├── mcp_server.py      #   MCP 入口（stdio / streamable-http）
│   └── demo.py            #   CLI 演示
├── agent/
│   └── loop.py            ← function-calling 循环（web 聊天与 CLI 共用）
└── web/                   ← 交付层（只做协议转换）
    ├── app.py             #   FastAPI 应用 + kg-web 入口
    ├── deps.py            #   依赖注入点（测试在此替换 LLM）
    ├── routes_graph.py    #   /api/graph：可视化数据 / 实体详情 / 手工编辑（增删改+建边）/ 重置
    │                      #   + space_id 只读桥接：entity/{id}/workorders、by-space/{space_id}
    │                      #   （关联键=节点 attrs.space_id；桥接只在 web 层，graphRAG 仍不 import ops）
    ├── routes_chat.py     #   /api/chat：LLM + 工具问答
    ├── routes_extract.py  #   /api/extract：工单文本/截图 → 三元组 → 入图
    ├── routes_ops.py      #   /api/ops：会话聊天 / SSE 回放 / 跨会话检索 / 工单溯源 / 派单 / 责任方调整 / 洞察 / 重置
    └── static/            #   index.html（图谱）/ ops.html（三栏回放台）/ asset.html（设备 360）
```

依赖方向：`web → agent → tools → data ← contracts(冻结) ← llm(注入)`；子包之间互不知道对方存在。
换存储只改 `data/`；加新工具在 `tools/` 注册；换模型只改 `llm/`。

## 知识图谱本体

### 节点（8 类）

| 类型 | 中文 | 来源登记表字段 |
|---|---|---|
| `Device` | 设备 | 设备名称/编号（属性含 参数/品牌/规格/日期/价值/状态） |
| `Person` | 人员 | 责任人 / 接收人 / 移交人 / 管理责任人 |
| `Department` | 部门 | 责任部门（工程部） |
| `Vendor` | 供应商 | 供应商名称 |
| `Project` | 项目 | 关联项目部 |
| `Building` | 楼栋 | 关联楼栋（A座） |
| `Floor` | 楼层 | 关联楼层（AB1F） |
| `Room` | 空间 | 关联空间/房源（气体灭火气瓶间） |

命名口径：卫生间类空间的规范名统一为「男洗手间 / 女洗手间」，别名收全口语说法（男卫生间/男厕所/女卫生间/女厕所/无性别前缀的「N楼洗手间」等）；`kg_search_entities`、`kg_count_entities` 与工单抽取的实体链接都会先把「卫生间/厕所」归一到「洗手间」再匹配——三种叫法查到的是同一个节点。

### 关系（8 种）

| 关系 | 中文 | 方向 | 语义 |
|---|---|---|---|
| `located_in` | 位于 | Device→Room | 设备安装位置 |
| `part_of` | 属于 | Room→Floor→Building→Project | 空间层级链 |
| `supplied_by` | 供应商 | Device→Vendor | 供货关系 |
| `managed_by_dept` | 责任部门 | Device→Department | 部门责任 |
| `has_responsible_person` | 责任人 | Device→Person | 台账责任人 |
| `received_by` | 接收人 | Device→Person | 移交接收方 |
| `handed_over_by` | 移交人 | Device→Person | 移交方（样例登记表为"/"，未建边） |
| `has_manage_person` | 管理责任人 | Device→Person | 日常管理 |

> 种子数据：截图可读值原样录入；打码字段用示例值（见 `seed.py` 顶部声明）。

## 7 个 LLM 工具（tools/kg_tools.py）

| 工具 | 用途 |
|---|---|
| `kg_get_schema` | 图谱本体（LLM 先调它了解可查什么） |
| `kg_search_entities` | 关键词/类型模糊搜索实体 |
| `kg_get_entity` | 实体全部台账属性 |
| `kg_get_relations` | 一跳关系（方向/关系过滤，支持反向查"房间里有啥设备"） |
| `kg_find_path` | 两实体间最短路径（"X 和 Y 什么关系"） |
| `kg_get_space_chain` | 完整空间定位链：设备→房间→楼层→楼栋→项目 |
| `kg_count_entities` | 跨区域聚合统计：按范围（楼栋/楼层/空间）+所在空间类型统计实体数量（如「A栋男卫生间马桶数量」），数量类问题一次出答案 |

三入口同源：MCP（`kg-mcp`）/ OpenAI function calling（`as_openai_tools()`）/ 进程内（`run_tool()`）。

## 「图谱会自己长大」怎么工作（graphRAG/extractor.py）

```
工单文本/截图 → qwen3.7-flash（prompt 内嵌本体，只允许 8+8 类型）
             → JSON 三元组 → 本体校验（关系端点类型匹配）
             → 实体链接（同名/别名对到已有节点，对不上才建 EXT-* 新节点）
             → 边 MERGE 去重 → 落盘 kg.json → 返回生长报告（新增节点/边/跳过原因）
```

前端「工单抽取」页贴一段工单（或上传登记表截图）→ 图上实时多出金色高亮的新节点。

图谱节点支持**手工编辑**（仅人工 UI，不进 kg 工具/MCP）：点击节点可 编辑名称与属性 / 从此新增关联节点 / 与已有节点建边 / 删除（连带边）。编辑与删除二次确认；关系选项按两端节点类型与箭头方向动态过滤（本体强制，如 `located_in` 只能 Device→Room），后端路由层终验。

Claude Code 挂载 MCP：

```bash
claude mcp add wagent-kg -- d:/git-project/wagent/agent/.venv/Scripts/kg-mcp.exe
```

## ops 设施运维 Agent（wagent_backend.ops）

按 `docs/工具说明.md` 实现：**11 个冻结契约工具** + 三层记忆 + 四档记忆消融 + 确定性安全前置。

### 11 个工具（contracts/ 冻结，tools/impl.py 实现）

| 工具 | 一句话 |
|---|---|
| `resolve_space` | 租户原话 → 空间候选（歧义返回候选不猜） |
| `get_assets_serving_space` | 服务该空间的设备 + 台账 + 最新运行参数（阀位/流量/lock_status） |
| `query_workorder_history` | 设备/空间/租户/楼栋 × 时间窗的工单原文 + 处置流水 |
| `recall_memory` | 检索已归纳洞察（相似度 × 置信度，低置信标记） |
| `write_memory` | 有证据工单支撑才能写入的洞察（防手写、防时间旅行） |
| `verify_memory_prediction` | 闭环回写：命中 +0.10·(1-c)，未命中 ×0.85，<0.6 进审核队列 |
| `judge_liability` | 合同条款 > 保修/外包 > 默认映射；条款冲突 → unclear + 需人工 |
| `create_workorder` | 建单 + 技工派工 + briefing_note 现场交底 + 证据工单引用 |
| `find_technician` | 技能/楼栋/班次静态匹配（不编造 ETA） |
| `notify` | 确定性模拟发送 + RCPT- 可审计回执 |
| `escalate_to_human` | TKT- 升级票据（安全/金额/步数上限/合同歧义…） |

统一错误协议：`not_found`/`ambiguous`/`invalid_input` 是正常业务结果；`upstream_error` 才是系统故障；「实体存在但窗口无记录」= 空列表不是错误。失败统一 `{"error":{code,message,hint}}` 信封，绝不炸循环。

### 记忆四档（页面顶部切换）

| 档位 | 可见 | 工具数 |
|---|---|---|
| off 无记忆 | 仅当次文本 | 7 |
| l1 仅设备台账 | + 运行参数 | 7 |
| l1l2 台账+90天工单原文 | + 工单历史（自己通读原文） | 8 |
| full 台账+工单+归纳洞察 | + recall/write/verify | 11 |

### 会话记忆与通讯（严格对齐 deepseek-harness）

**一切皆事件**：会话 = 追加型事件日志（`seq` 即行号，`data` 在追加点 JSON 快照），LLM 看到的 messages 与前端三栏都是它的投影。五层：

| 层 | 模块 | 机制 |
|---|---|---|
| L0 事件日志 | `events.py` | append-only；追加即发布（SSE 钩子）；seq 连续性契约 |
| L1 surface | `surface.py` | 只有 user/message、assistant/message、tool/result 三类进模型历史，**必须**带事件级 `surfaceOp`（`"append"` 或 `{"op":"replace","start","end"}`）；压缩/裁剪用 replace 型新事件**遮蔽**旧节点，日志永不改写；`derive_messages` 增量缓存（replace_generation 失效水位） |
| L2 投影 | `projections.py` | `ProjectionDefinition{key,init,apply,view,state_version}` 注册表；整值规则 + **同引用=零通知**（不感兴趣的事件原对象返回）+ 水位 cell 惰性补折；meta（会话列表/摘要）就是注册在表上的第一个单元 |
| L3 压缩/裁剪 | `compaction.py` + `pruner.py` | 每步前压力检查：≥0.8×窗口先跑模型无关的工具结果中段裁剪（>8192 字符保头 4096 + 尾 1024 + 单 `[... tool result middle pruned ...]` marker，原全文永留日志），复测仍超才摘要压缩（dsh 逐字英文八段 checkpoint 模板 + `<compacted-summary>` 包裹；恰好 4 事件事务；摘要必须更小；失败 fail-closed 留痕不中断轮次）；区段选择头锚定、尾部保留 0.16×窗口、**工具配对永不切分**；上下文溢出错误自动强制压缩后重试一次 |
| L4 持久化 | `store.py` | 每会话一个 JSONL，**首行 session 头（version=1）**；写-behind（200ms/64 条，模块级单 flusher 线程）；轮末 `flush()` 屏障；撕裂尾行容忍丢弃；版本不符拒读——**旧格式会话文件需清空 `data/sessions/`** |

**流式通讯**（dsh 同款）：模型永远走流式（qwen3 thinking 仅流式可用）。每个 token chunk 先落 `assistant/chunk` 事件（回放保真），`BlockAssembler` 边收边组，流尾发 `assistant/message`（`sourceEventSeqs`=chunk seqs，usage 搭车）；每轮首步发 `request/header`（initial/resume/change，含 system 全文 + 工具清单）与 `request/context`（首次与变化时）——回放能还原「模型当时看到什么」。`assistant/message.content` 是块数组（text/reasoning/tool-call 按流序）；`tool/result` 是 ToolResultMessage（单 tool-result 块，错误信封在内容文本内部）。

事件词表（type → data → surface?）：

| type | data 要点 | surface |
|---|---|---|
| *(文件首行)* session header | `{type:"session",version:1,id,createdAt,tier,as_of}` | — |
| `session/start` `turn/start` | 会话/轮开始 | 否 |
| `user/message` | data 即完整消息；`source:{kind:"user"}` 或 `{kind:"plugin",plugin:"location-nudge"/"format-nudge"/"wo-nudge"/"empty-reply-nudge"/"compaction"}` | **是** |
| `request/header` | `{header:{config,system 全文,tools},reason:initial/resume/change}` | 否 |
| `request/context` | `{provider,model,contextWindow}`（首次+变化） | 否 |
| `assistant/chunk` | `{turn,step,chunk:<StreamChunk>}`（逐 token，log-only） | 否 |
| `assistant/message` | `{turn,step,message:{content:[块…按流序],source:{kind:"model",…}},usage?}` | **是** |
| `tool/call` | `{turn,step,callId,name,arguments 原始串}`（log-only） | 否 |
| `tool/result` | `{turn,step,message:<ToolResultMessage>,meta:{name,digest,duration_ms}}` | **是** |
| `decision` | `{turn,decision}` | 否 |
| `compaction/start/summary/prune/end` | 压缩事务（shadowedRange/shadowedSeqs/摘要/错误） | 否 |
| `turn/end` | `{turn,reason:completed/awaiting_input/safety/policy_escalate/step_limit/max_rounds/parse_failed/llm_error,needs?,location_hint?,detail?}` | 否 |

跨会话检索（dsh L5）在 wagent 是纯 Web 端点 `GET /api/ops/sessions/search?q=`（扫用户原文与工具摘要），**不做成第 12 个模型工具**。

### 三栏回放台（/ 与 /ops）

左＝租户企微视角（气泡 + 可点工单号 + 内嵌补全卡片）；中＝**Agent 时间线**：顶部吸顶**节点画布**（当前档位开放的工具各一节点 + 「📄 决策归档」，四档状态：未调用灰 / 调用过暗淡 / 已完成亮 / 调用中最亮+呼吸闪动；角标 ×N，栏头计数「已调用 · 未调用」）＋下方时间线（用户消息浅蓝气泡、模型正文、工具行 = 图标+一行输出摘要+耗时、`📄 Decision` 摘要行；**代码与思考过程不展示**——思考状态由打字条「第 N 步 · 已执行 M 次工具」承担，trace 仍完整落盘）；右＝**项目经理视角（对话流）**：默认空态与租户视角一致，每轮判定追加一个完整对话包「决策摘要 → 涉及设备（无则显示不涉及）→ 接单信息（可派单，交底高亮块内嵌）」；升级结局追加红框告警包；底部有演示占位输入框（输入仅回显并提示"功能暂未开放，本视角为演示视角"）。

**交互卡片**（左栏内嵌，仅实时流弹出，回放不弹）：

- **位置补充卡**：`resolve_space` 失败/歧义且模型追问时弹出（定位失败却直接出 Decision 会被 runner 拦截一次——location-nudge 强制先追问，第二次才放行，防止"位置待定"单静默完结）。后端从对话抽取已知位置随 `turn/end.location_hint` 下发——楼栋（building_hint /「B座」/ 门牌字母前缀 a1010→A栋）、楼层（「25楼」/ 门牌前两位）、位置类型与区域（洗手间/电梯厅/东侧/男女卫）。卡片**逐级自动预选**：楼栋、楼层直接选中，位置在空间库过滤后唯一命中才选中（宁缺毋滥），均可手动改；级联禁用——未选楼栋不可选楼层，未选楼层不可选位置。`resolve_space` 匹配档位：精确 ID/完整别名 > 别名子串包含（带数字边界守卫）> 单位号 > 楼层+区域（区域词含男女卫）> 楼层+类型收敛（无区域词时「13楼洗手间」收敛到男/女卫候选）；匹配前做类型同义词归一（洗手间/厕所→卫生间 等）
- **建单硬拦截（wo-nudge）**：报修轮输出 Decision 但本轮未实际调用 `create_workorder`（且未升级人工、`recommended_action` 非豁免项——豁免仅 `restore_after_payment` 缴费恢复不派工）时，runner 注入「建单提醒」退回模型重试一次，第二次仍违规则放行留痕（防死循环）——杜绝 tenant_message 声称「已受理/师傅上门」但经理视角无工单、责任方无从调整的口径分裂
- **安全补全卡**：报修命中安全关键词（煤气/困人/着火…）时模型不参与、直接升级人工，同时弹红色主题补全卡——位置四级联动（同样带预选）+ **手机号必填**（11 位校验，不通过红框抖动拦截）+ 备注；提交后右栏最近对话包**红框呼吸告警**并插入租户补充的位置与电话
- **联系方式补全卡**：任何升级（模型自行升级/判责冲突/步数上限等）都会在结局追问手机号（必填）+ 备注，提交后同步右栏最近对话包；**升级场景的派单卡先挂起**（接单信息显示「待租户补全联系方式后开放派单」），提交联系方式后才开放派单与自动派单倒计时
- **紧急工单自动派单**：urgency ∈ {特急, 紧急} 的派单卡挂 3 分钟倒计时（「⏱ 特别情况：mm:ss 内未派单将自动匹配处理人」）；超时未手动派单则自动调 dispatch 接口——优先 Agent 建议人选，否则建议班组自派；手动派单即取消计时；仅实时流计时，回放不触发
- **责任方手动调整**：经理决策包与工单溯源弹窗的责任方下拉（不明确/租户/外部/物业——owner 对客口径即「物业」）切换即保存——append-only 写 `liability_adjusted` 事件留痕，不改原判定记录（`POST /api/ops/wo/{id}/liability`；`shared` 由判责产出不手选）
- **图谱 ↔ 工单互查**（space_id 只读桥接）：图谱节点 attrs 带 `space_id` 时详情面板列出该空间关联工单；工单卡片/溯源弹窗有绑定图谱节点时显示「图谱节点 ↗」（新标签页打开）。桥接只在 web 层（`/api/graph/entity/{id}/workorders`、`/api/graph/by-space/{space_id}`），graphRAG 与 ops 两包的隔离不变
- **设备 360 视图**：`/asset/{asset_id}`（数据 `GET /api/ops/asset/{id}`）——台账全字段 + 最新运行快照 + 该设备工单列表；工单状态从处置流水推导（无事件=待派单 / 有 dispatched=维修中 / 有 closed=已完成），不新增状态字段。入口：工单卡「涉及设备」、经理对话包设备行、图谱 Device 节点详情。种子含公共设施层（A/B 全楼层：男女卫各 水龙头/冲洗阀/地漏/干手器/排风扇 + 男卫 3 小便池 3 马桶、女卫 3 马桶 + 电梯厅饮水机，共 720 台，`seed.facility_rows()` 生成；图谱侧由 `graphRAG/seed.build_facility_subgraph` 同源镜像，楼层/卫生间/电梯厅 Room 带 `space_id` 桥接、Device 节点 ID 即 ops asset_id，人员沿用现有责任人，供应商为仿真生成）
- **设备设施智能查询**（图谱页聊天）：kg_* 工具调用过程不展示，等待时「理解问题→检索图谱→生成回答」过场提示，回答打字机式流出（后端一次返回、前端逐字渲染）
- **图谱交互契约**：选中节点后关联节点金框亮起、关系线加粗，背景节点淡化且 **silent**（不响应悬停/点击，点它=点空白=退出选中）；搜索点亮全部命中——少量命中（≤12）展开祖先链逐个点亮，大量命中（如「马桶」216 个）只点亮其所在楼层锚点防卡死；节点尺寸按 项目>楼栋>楼层>空间>设备 递减；**选中/展开状态下两页发送键均变为红色 ■ 终止键**（图谱页 abort 请求、回放台 cancel SSE 流，回车不触发终止）
- **工单抽取不建供应商**：京东等购买渠道不是台账供应商——抽取提示词不含 Vendor 类型，`extractor.apply()` 硬规则跳过含 Vendor 的三元组（存量垃圾节点已清理）

**确定性查重（复发不再依赖租户说"又"）**：`create_workorder` 建单前自动查同空间同症状 90 天内已有工单，随返回注入 `repeat_evidence`（工单号列表）+ `repeat_hint`（要求模型据此判复发）；`CreateWorkorderOutput` 契约已同步（冻结文件已落章）。**复发堆单硬停**：同空间同症状的**未闭环**工单达 3 张、租户再报同一问题时，建单落地即策略硬停强制转人工（`repeat_failure_2x`，不依赖模型自觉）——只数未闭环单，历史已闭环的复发链仍是「治本建议」的素材，不影响各故事线首报节拍。

**中断可见**：格式提醒会带上 Decision 契约校验的具体失败原因转告模型自纠；`parse_failed` / `llm_error` / SSE 静默中断都会在时间线 banner + 租户气泡给出明确提示，决策节点标红。

**实时流式**：发送走 `POST /api/ops/chat/stream`（SSE）——事件每产生一条就推一条（`__start` → 事件流 → `__done`），工具先出虚线「⏳ 执行中」卡、结果到达后原地回填；打字条实时显示「第 N 步 · 已执行 M 次工具」。**工作中发送键变红色 ■ 终止键**（cancel SSE 流，回车不触发，防误触）。历史会话回放仍是批量渲染同一份事件流（对 `assistant/chunk` 逐事件重放同一折叠器，回放与直播同一代码路径）。单轮上限 40 次工具调用 / 30 轮模型往返，超限自动升级人工。

**时间线展示**（2026-08-31 精简后）：中栏展示模型每步正文、工具调用行（点开完整 IN/OUT JSON）、`@ 上下文注入` 行（来自真实 `request/header` 事件，点开见 system 全文与工具清单；**注入完成后自动隐藏**）、压缩/裁剪出 `🗜 checkpoint` 与 `✂️ 裁剪` 行、最终回复整段 + `📄 Decision` 折叠行。思考过程不渲染——`assistant/chunk` 仅留痕事件流，状态由打字条承担；思考绝不回灌模型消息列表（`derive_messages` 只投影 text/tool-call 块，有测试守卫）。左栏不再展示送达回执——`wecom → tenant_contact:C-003`、`RCPT-xxxx` 这类内部口径（渠道/联系人 ID/回执号/工单号）只对运营侧有意义，回执仍在中栏工具行与事件流留痕可查。
演示三条故事（种子数据内置）：**A** 25楼东侧阀执行器复发链（3 单治标 → 洞察 INS-REPLAY-001 → 直接换阀）；**B** A1106 欠费锁机（lock_status 唯一可见通道 → 缴费恢复不派工）；**C** 同一报修在 l1 档无记忆对照。
⚠️ 注意：A座25楼东侧（SP-A-25-E）另挂两条结论冲突的有效合同条款（CL-004 业主 vs CL-005 租户，同覆盖阀执行器故障），`judge_liability` 命中即 `unclear + requires_human`，判责硬停策略强制转人工、**不会建单**——这是「条款冲突不替用户拍板」的设计演示，不是故障。想演示直接建单请换地址（如 A1913 / A1608）。

### 仿真测试数据（data/simseed/）

在演示故事之上，还灌入了仿真器（仓库历史 `git show d0a9f93:simulator/`）
确定性生成的整套测试数据：**216 空间 / 276 设备 / 206 租户 / 12 技工 / 3086 张工单**
（373 天，时间轴终点与回放基准同为 2026-08-23）。要点：

- 复发是涌现的：治标不重置部件磨损 → 复发；治本 → 归零。数据里有大量真实的复发链可挖
- 技工判断可能是错的（误诊率 40% 且按根因分层）——L2 的 `reported_cause` 不可全信
- 导入时从 L2 聚合生成 `INS-SIM-*` 洞察（同设备同判断复发 ≥3 次），供 recall_memory 演示
- **真值隔离**：仿真器的 `ground_truth.jsonl` 有意不入仓、不入库（`truth_leak_check` 守卫）
- 再生成方式与字段映射见 `data/simseed/PROVENANCE.md`；默认不灌入（演示库只留汇金广场），`WAGENT_OPS_SIMSEED=1` 显式打开

### 铁律

- **真值隔离**：库与 prompt 中无 ground_truth/true_*；`SYMPTOM_CANDIDATE_CAUSES`、`CURATIVE_ACTIONS` 禁止进 prompt（测试守卫）
- **as_of 注入**：回放 = 场景时间，交互 = 系统时间；工具不读系统时钟、不返回未来洞察
- **append-only**：work_order / work_order_event / event_log 有触发器禁改禁删
- 一切皆事件：会话 = JSONL 事件流（dsh 五层记忆：事件日志 / surface / 投影 / 压缩 / 持久化），LLM 消息列表与前端三栏都是它的投影

## 数据与环境变量

| 变量 | 默认 | 说明 |
|---|---|---|
| `LLM_API_KEY` | （无） | 必填才能用聊天/抽取/运维 Agent；回落 `OPENAI_API_KEY` |
| `LLM_BASE_URL` | DashScope compatible-mode | 任何 OpenAI 兼容网关 |
| `LLM_MODEL` | `qwen3.7-flash` | 模型名 |
| `LLM_THINKING` | `1` | qwen3 思考输出（`enable_thinking`，流式），页面流式展示 🧠 Think 行；`0` 关闭 |
| `WAGENT_KG_DATA` | `agent/data/kg.json` | 图谱数据文件（抽取结果会持久化在这里） |
| `WAGENT_OPS_DB` | `agent/data/ops.db` | 运维 SQLite（首次访问自动建库灌种子） |
| `WAGENT_SESSIONS_DIR` | `agent/data/sessions` | 会话事件流 JSONL 目录（首行 session 头 v1；**旧格式文件会被拒读，需清空该目录**） |
| `WAGENT_COMPACTION` | `1` | L3 压缩/裁剪开关；`0` 关闭（演示对照用） |
| `WAGENT_CONTEXT_WINDOW` | `32768` | 压力阈值口径（0.8×窗口触发压缩；演示可调小逼出压缩，如 `4000`） |
| `WAGENT_OPS_SIMSEED` | `0` | 仿真测试数据不随种子灌入；`1` 打开（单测里显式开） |
| `WAGENT_EMBEDDING` | `auto` | `api`（DashScope text-embedding-v3）/ `local`（离线哈希）/ `auto`（有 key 用 api） |

重置图谱：Web 右上角「重置为种子」或 `uv run kg-demo --reseed`。
重置运维库：/ops 页右上角「重置数据」。
