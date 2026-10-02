"""MCP stdio 冒烟：真实子进程拉起 kg-mcp，走 MCP 协议 list_tools + call_tool。"""

from __future__ import annotations

import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


async def test_stdio_server_list_and_call():
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "wagent_backend.tools.mcp_server"]
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listed = await session.list_tools()
            names = {t.name for t in listed.tools}
            assert {
                "kg_get_schema",
                "kg_search_entities",
                "kg_get_entity",
                "kg_get_relations",
                "kg_find_path",
                "kg_get_space_chain",
            } <= names

            result = await session.call_tool(
                "kg_get_space_chain", {"entity_id": "七氟丙烷驱动气瓶"}
            )
            assert not result.is_error
            text = result.content[0].text
            assert "气体灭火气瓶间" in text and "汇金广场" in text
