"""MCP server 入口 —— 把 7 个 KG 工具挂到 Model Context Protocol。

用法：
    kg-mcp                 # stdio（默认，配 Claude Code / Claude Desktop / 任意 MCP 客户端）
    kg-mcp --http          # streamable-http，默认 127.0.0.1:8765
    kg-mcp --http --host 0.0.0.0 --port 9000

每个工具的 schema 由函数签名生成（扁平参数，客户端好调），
实现统一走 kg_tools.run_tool，与进程内直调、OpenAI function calling 同源。
"""

from __future__ import annotations

import argparse
from typing import Literal

from mcp.server.mcpserver import MCPServer

from wagent_backend.tools.kg_tools import run_tool

mcp = MCPServer(
    name="wagent-kg",
    instructions=(
        "设备台账知识图谱：设备/人员/空间/部门/供应商的实体与关系查询。"
        "建议先调 kg_get_schema 了解本体，再用 kg_search_entities 定位实体，"
        "数量统计类问题直接用 kg_count_entities，"
        "最后用 kg_get_relations / kg_get_space_chain / kg_find_path 回答问题。"
    ),
)


@mcp.tool()
def kg_get_schema() -> dict:
    """获取知识图谱本体：8 类节点（设备/人员/部门/供应商/项目/楼栋/楼层/空间）与 8 种关系的定义。回答图谱问题前先调它。"""
    return run_tool("kg_get_schema")


@mcp.tool()
def kg_search_entities(
    keyword: str | None = None,
    entity_type: str | None = None,
    limit: int = 10,
) -> dict:
    """按关键词（实体ID/名称/别名，子串模糊）和节点类型搜索实体，返回候选列表。不确定 ID 时先用它。"""
    return run_tool(
        "kg_search_entities", keyword=keyword, entity_type=entity_type, limit=limit
    )


@mcp.tool()
def kg_get_entity(entity_id: str) -> dict:
    """获取单个实体的全部属性（设备编号/品牌/规格/日期/价值/状态等登记表字段）。"""
    return run_tool("kg_get_entity", entity_id=entity_id)


@mcp.tool()
def kg_get_relations(
    entity_id: str,
    direction: Literal["out", "in", "both"] = "both",
    relation: str | None = None,
    limit: int = 20,
) -> dict:
    """查某实体的一跳关系（可按方向/关系类型过滤）。回答『谁负责/供应商是谁/这房间有哪些设备』这类问题。"""
    return run_tool(
        "kg_get_relations",
        entity_id=entity_id,
        direction=direction,
        relation=relation,
        limit=limit,
    )


@mcp.tool()
def kg_find_path(source_id: str, target_id: str, max_hops: int = 4) -> dict:
    """找两个实体之间的最短关系路径（忽略方向）。回答『X 和 Y 是什么关系』。"""
    return run_tool(
        "kg_find_path", source_id=source_id, target_id=target_id, max_hops=max_hops
    )


@mcp.tool()
def kg_get_space_chain(entity_id: str) -> dict:
    """获取设备/空间的完整空间定位链：设备 →(位于) 房间 →(属于) 楼层 → 楼栋 → 项目。回答『这设备在哪』。"""
    return run_tool("kg_get_space_chain", entity_id=entity_id)


@mcp.tool()
def kg_count_entities(
    keyword: str,
    entity_type: str = "Device",
    scope: str | None = None,
    location_keyword: str | None = None,
) -> dict:
    """跨区域聚合统计：按关键词统计某范围（楼栋/楼层/空间，可限定所在空间类型）内的实体数量。回答『A栋男洗手间有多少个马桶』这类数量问题。"""
    return run_tool(
        "kg_count_entities",
        keyword=keyword,
        entity_type=entity_type,
        scope=scope,
        location_keyword=location_keyword,
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="kg-mcp", description="wagent-kg MCP server")
    parser.add_argument(
        "--http", action="store_true", help="用 streamable-http 而非 stdio"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
