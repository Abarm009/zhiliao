"""ops —— 正式设施运维 Agent（报修 → 定位 → 诊断 → 判责 → 派工 → 通知 → 归档）。

与 graphRAG/kg_* 台账演示完全隔离（工具说明 §0：kg_* 不进正式 Agent 注册表）。
分层依赖：web → agent → tools → data ← contracts(冻结) ← llm(注入)。
"""
