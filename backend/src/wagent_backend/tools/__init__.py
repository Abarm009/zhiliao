"""tools —— LLM 工具层：kg_* 工具契约与注册表、MCP server、演示 CLI。

只做两件事：把 graphRAG 的能力包装成大模型可调用的工具；
把工具暴露给三种消费方（MCP / OpenAI function calling / 进程内）。
"""
