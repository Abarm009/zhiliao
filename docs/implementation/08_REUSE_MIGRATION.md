# 既有代码复用与改造清单

> **2026-09-27 Hub实证修订**：先读[13提交规范与架构差异](13_APP_HUB_SUBMISSION_REVIEW.md)。Hub版优先验证`main.splash`脚本应用；旧Rust broker＋本机Python配对不能作为可安装路线。保留业务规则与UI视觉；任务权威、身份、模型和持久化须G0裁决，未批准公网部署或降低多人验收。下文涉及旧宿主实现的内容仅作历史/条件设计。

> **研讨课 #1 后续修订（设计v1.2）**：先读[逐字稿与基线差异](11_COURSE1_BASELINE_REVIEW.md)。原robrix2为唯一P0宿主的前提已撤回，改以OctoSense原生持久应用为主选，App Card为意图视图；旧宿主/配对实现仍属条件设计。以下领域规则继续保留，宿主专属细节须G0复核。

核对日期：2026-09-26。来源：当前独立副本；Router DeepSeek代理只读盘点，主会话确定迁移边界。没有访问旧WAgent目录，没有运行真实模型。本文件描述源码存在性与设计改法，不证明今天端到端运行通过。

## 1. 已有能力怎样保留

|已有模块/函数|继承的业务价值|新工程具体改法|必须验证|
|---|---|---|---|
|ops/tools/impl.py：resolve_space、get_assets_serving_space|原话定位空间；设备安装与服务关系分开|包入ScopedQueries；可信项目范围在检索前生效；导入repair台账时保留来源映射|同名跨项目不串数据；缺少服务关系不猜设备|
|query_workorder_history、ops/data/repo.py|查历史工单及处置事件|旧历史通过显式导入的只读快照或只读适配访问；统一映射source_ref，不向旧库写新任务|旧work_order_id、新task_id、外部id分开|
|recall_memory、write_memory|语义召回、引用存在性和时间有效性校验|保留召回算法参考，按用户范围和时间过滤；P0不暴露裸模型写经验工具|越权引用拒绝；无依据经验标未知；测试真值不入检索|
|judge_liability、find_technician、policy.py|有依据的建议与确定性停机守卫|保留规则思想，重新核对本届字段/角色；建议不等于派工、验收或正式责任认定|模型不能覆盖规则；技能/项目匹配由服务器判定|
|llm/client.py、assembler.py|模型调用与流式内容组装|复用客户端，接AgentRuntimePort；模型配置、错误和用量可追溯|断流/结构化输出错误不产生假成功|
|ops/agent/events.py、session.py、store.py、projections.py|对话事件、会话恢复、surface投影|保留为模型会话与排障链路，以task_id关联；业务权威仍是repair表和事务事件|清除或压缩聊天不能丢业务任务|
|compaction.py、pruner.py|上下文长度管理|复用机制并测试新建议/来源保留；不是业务记录删除器|压缩后不丢待确认对象与来源引用|
|graphRAG/与旧Web|已有图谱查询和历史回归入口|保留依赖闭包；contest入口禁用未迁移写操作；不扩建第二套图谱主库|新路由不因旧依赖暴露reset/写图谱|

当前工具代码里存在通知/升级处理，不等于真实短信、企微或外部工单已接通；新界面只展示有回执证明的范围。

## 2. 不能原样照搬的旧行为

|旧位置|冲突|修改方式|
|---|---|---|
|create_workorder|旧建单直接写旧工单；按90天同空间/症状查重|新流程用create_draft/submit_report；幂等按来源事件与请求键，不用旧语义查重阻止新故障；旧查询可提示历史|
|tools/registry.py、runner.py|工具提交事务、自动建单提示及其他后置写路径|执行器独占新事务；新agent_service隔离自动写行为；旧入口未收敛前contest禁用|
|web/routes_ops.py人工派单/判责|不等于新的可信身份、抢单、版本与幂等|旧路由按调用方兼容封装或禁用；新命令用服务器身份和expected_version|
|tools/mcp.py、ToolContext.as_of|裸工具与调用方时钟不能作为新权限边界|新上下文由后端生成；生产业务当前时间不可由模型传入；历史回放时钟只允许离线测试|
|verify_memory_prediction|actual_root_cause来自调用参数；存在closed事件不证明根因可信|保留旧contracts原样作回归；新反馈端口从completion/acceptance的可信记录读取。不能静默删旧入参或把模型自报值作为真值|

工具数量、工具分组和旧prompt属于旧实现。不能把“11个工具”或tier_tools当本届永久限制，更不能把工具可见性当认证授权。

## 3. 反馈能力的真实边界

`ops/tools/impl.py`中的verify_memory_prediction会核对历史工单/关闭事件，并用传入的actual_root_cause与预测比较，更新置信度；对应契约在ops/contracts/schemas.py。它证明存在反馈记账机制，不证明实际根因被独立证实。

当前核对未发现新业务的完工/验收写入口；旧closed历史主要由种子/仿真导入产生。相关测试传入预定根因并检查计算，不能作为真实学习实验。新闭环必须补上现场处置、来源证据和独立验收，再讨论有版本的经验更新。

禁止三种迁移捷径：把旧JSONL会话事件当新任务事务库；把as_of从模型输入直接用于真实预约；为了方便删改ops/contracts原接口而不记录兼容迁移。

## 4. 当前缺口

只读检索未发现backend/src中新维修任务/预约实现，也未发现本工程Rust源文件或Cargo.toml；integrations/octosense只有说明。新任务表、并发接单、预约双确认、完工验收、项目角色权限、统一执行、原生broker均待实现。设计SQL/OpenAPI不算服务实现。

下一步编码按职责分工：A保护契约与导入映射；B实现领域规则/执行器；C负责宿主；D只做必要API与Web配对；E复用旧Agent并加入运行端口/Verifier；F独立回归。每个文件只有一个主写者。

## 5. 验证和回退

1. 保留migration-manifest.json作为来源，不更新哈希掩盖修改。9/26本轮仍匹配79文件、3,591,754字节。
2. 有意修改旧文件时在变更记录写调用方、旧行为、新行为与测试，旧contracts默认不变。
3. 新库通过版本迁移安装，导入记录带源ID/版本与来源；新旧数据不双主写入。
4. 先跑离线契约/事务/权限测试，再跑原生与真实模型。原234项通过是9/21历史记录，本轮未重跑。
5. 如果以后移植Rust，使用相同JSON输入、时钟和预期事件验证语义一致；不要求重写所有旧模块。
