"""演示 CLI。

    kg-demo            # 无需任何 API key：图谱统计 + 6 个工具逐一人话示例
    kg-demo --chat     # 终端 LLM 问答（qwen3.7-flash，读环境变量）
    kg-demo --reseed   # 从 seed.py 重建 data/kg.json

环境变量（--chat 与 Web 聊天共用）：
    LLM_API_KEY / LLM_BASE_URL / LLM_MODEL（默认 qwen3.7-flash）
"""

from __future__ import annotations

import argparse
import json
import sys

from wagent_backend.agent import loop as agent_loop
from wagent_backend.graphRAG.store import get_store
from wagent_backend.tools.kg_tools import run_tool


def _p(title: str, result: dict, keys: tuple[str, ...] = ()) -> None:
    print(f"\n{'─' * 60}\n◆ {title}\n{'─' * 60}")
    if keys:
        result = {k: result[k] for k in keys if k in result}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def run_examples() -> None:
    store = get_store()
    stats = store.stats()
    print("═" * 60)
    print("WAgent 设备台账知识图谱 —— 演示")
    print("═" * 60)
    print(f"节点 {stats['node_count']} 个 / 关系 {stats['edge_count']} 条")
    print(f"节点分布: {json.dumps(stats['nodes_by_type'], ensure_ascii=False)}")
    print(f"关系分布: {json.dumps(stats['edges_by_relation'], ensure_ascii=False)}")

    _p(
        "① kg_get_schema —— 图谱里有什么可查（节选 node_types）",
        run_tool("kg_get_schema"),
        keys=("node_types",),
    )
    _p("② kg_search_entities —— 搜『气瓶』", run_tool("kg_search_entities", keyword="气瓶"))
    _p(
        "③ kg_get_entity —— 七氟丙烷驱动气瓶的台账属性",
        run_tool("kg_get_entity", entity_id="七氟丙烷驱动气瓶"),
        keys=("entity",),
    )
    _p(
        "④ kg_get_relations —— 这台设备都有谁/什么在关联（责任、供应、位置）",
        run_tool("kg_get_relations", entity_id="DEV-HFC227-001"),
        keys=("edges",),
    )
    _p(
        "⑤ kg_get_relations —— 气体灭火气瓶间里装了哪些设备（反向查询）",
        run_tool(
            "kg_get_relations",
            entity_id="气瓶间",
            direction="in",
            relation="located_in",
        ),
        keys=("edges",),
    )
    _p(
        "⑥ kg_find_path —— 这台设备和『工程部』是什么关系",
        run_tool("kg_find_path", source_id="DEV-HFC227-001", target_id="工程部"),
        keys=("found", "hops"),
    )
    _p(
        "⑦ kg_get_space_chain —— 这台设备装在哪（完整空间链）",
        run_tool("kg_get_space_chain", entity_id="DEV-HFC227-001"),
        keys=("chain",),
    )

    print(
        f"\n{'═' * 60}\n演示完毕。Web 界面：uv run kg-web  |  "
        f"LLM 终端问答：uv run kg-demo --chat  |  MCP：uv run kg-mcp\n"
    )


def run_chat() -> None:
    from wagent_backend.llm import client

    print(f"知识图谱问答（模型 {client.model_name()}，输入空行退出）。")
    print("可以问：七氟丙烷驱动气瓶在哪？谁负责它？")
    history: list[dict[str, str]] = []
    while True:
        try:
            question = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break
        try:
            result = agent_loop.run(client.complete_msg, question, history)
        except client.LLMConfigError as e:
            print(f"\n[配置缺失] {e}")
            break
        for t in result.tool_calls:
            print(f"  [tool] {t.name}({t.arguments})")
        print(f"\n助手: {result.reply}")
        history += [
            {"role": "user", "content": question},
            {"role": "assistant", "content": result.reply},
        ]


def main() -> None:
    # Windows 控制台默认 GBK，强制 UTF-8 保证中文/制表符不乱码
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="kg-demo", description="wagent-kg 演示")
    parser.add_argument("--chat", action="store_true", help="进入 LLM 问答")
    parser.add_argument("--reseed", action="store_true", help="从 seed 重建 data/kg.json")
    args = parser.parse_args()

    if args.reseed:
        path = get_store(rebuild=True).save()
        print(f"已重建: {path}")
        return
    if args.chat:
        run_chat()
        return
    run_examples()


if __name__ == "__main__":
    main()
