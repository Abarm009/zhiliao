"""MCP server —— 11 个正式工具的第二个调用入口（stdio / streamable-http）。

用法：
    ops-mcp                 # stdio（Claude Code / Desktop / 任意 MCP 客户端）
    ops-mcp --http          # streamable-http，默认 127.0.0.1:8766
    ops-mcp --http --port 9000

与进程内直调同源（tools.registry.run_tool）；
每个工具带可选 as_of 参数注入场景时间（缺省 = 系统时间，即交互演示口径）。
"""

from __future__ import annotations

import argparse
from datetime import datetime

from mcp.server.mcpserver import MCPServer

from wagent_backend.llm.embedder import get_embedder
from wagent_backend.ops.data.db import connect, init_db, is_empty
from wagent_backend.ops.data.seed import seed
from wagent_backend.ops.tools.context import ToolContext
from wagent_backend.ops.tools.registry import run_tool

mcp = MCPServer(
    name="wagent-ops",
    instructions=(
        "甲级写字楼设施运维 Agent 的 11 个正式工具：空间解析、设备与运行参数、"
        "工单历史、L3 记忆（召回/写入/验证）、责任判定、建单派工、技工匹配、"
        "通知与人工升级。建议链路：resolve_space → get_assets_serving_space → "
        "query_workorder_history / recall_memory → judge_liability → "
        "find_technician → create_workorder → notify。"
    ),
)


def _ctx(as_of: str | None = None) -> ToolContext:
    conn = connect()
    if is_empty(conn):
        init_db(conn)
        seed(conn, get_embedder())
    ts = datetime.fromisoformat(as_of) if as_of else datetime.now()
    return ToolContext(as_of=ts, conn=conn, embedder=get_embedder())


@mcp.tool()
def resolve_space(text: str, building_hint: str | None = None, as_of: str | None = None) -> dict:
    """将租户原话中的位置描述解析为空间候选；歧义时返回候选，不自行猜测。"""
    return run_tool("resolve_space", _ctx(as_of), text=text, building_hint=building_hint)


@mcp.tool()
def get_assets_serving_space(space_id: str, category: str = "ALL",
                             as_of: str | None = None) -> dict:
    """查询服务指定空间的设备、台账与最新运行参数（服务关系，非安装位置）。"""
    return run_tool("get_assets_serving_space", _ctx(as_of), space_id=space_id, category=category)


@mcp.tool()
def query_workorder_history(scope: str, id: str, window: str = "90d",
                            symptom_filter: str | None = None,
                            as_of: str | None = None) -> dict:
    """按设备/空间/租户/楼栋查询时间窗口内的历史工单及处置流水。"""
    return run_tool("query_workorder_history", _ctx(as_of), scope=scope, id=id,
                    window=window, symptom_filter=symptom_filter)


@mcp.tool()
def recall_memory(query: str, scope_type: str = "any", scope_id: str | None = None,
                  top_k: int = 5, as_of: str | None = None) -> dict:
    """检索已归纳的历史洞察（正文/证据/置信度/相似度）；低置信会明确标记。"""
    return run_tool("recall_memory", _ctx(as_of), query=query, scope_type=scope_type,
                    scope_id=scope_id, top_k=top_k)


@mcp.tool()
def write_memory(scope_type: str, scope_id: str, body_md: str, confidence: float,
                 evidence_wo_ids: list[str], source: str = "agent_runtime",
                 predicted_root_cause: str | None = None,
                 as_of: str | None = None) -> dict:
    """写入有证据工单支持的记忆洞察；无证据或手写来源会被拒绝。"""
    return run_tool("write_memory", _ctx(as_of), scope_type=scope_type, scope_id=scope_id,
                    body_md=body_md, confidence=confidence,
                    evidence_wo_ids=evidence_wo_ids, source=source,
                    predicted_root_cause=predicted_root_cause)


@mcp.tool()
def verify_memory_prediction(insight_id: str, wo_id: str, actual_root_cause: str,
                             as_of: str | None = None) -> dict:
    """工单闭环后回写洞察预测结果，更新置信度与命中统计。"""
    return run_tool("verify_memory_prediction", _ctx(as_of), insight_id=insight_id,
                    wo_id=wo_id, actual_root_cause=actual_root_cause)


@mcp.tool()
def judge_liability(space_id: str, symptom: str, asset_id: str | None = None,
                    hypothesized_root_cause: str | None = None,
                    estimated_cost_cny: float | None = None,
                    as_of: str | None = None) -> dict:
    """判定责任方（业主/租户/共同/供应商/不明确）及依据；合同冲突返回需人工。"""
    return run_tool("judge_liability", _ctx(as_of), space_id=space_id, symptom=symptom,
                    asset_id=asset_id, hypothesized_root_cause=hypothesized_root_cause,
                    estimated_cost_cny=estimated_cost_cny)


@mcp.tool()
def create_workorder(space_id: str | None = None, raw_text: str = "", symptom: str = "", urgency: str = "一般",
                     asset_id: str | None = None,
                     assigned_technician_id: str | None = None,
                     hypothesized_root_cause: str | None = None,
                     recommended_action: str | None = None,
                     liability: str | None = None, briefing_note: str | None = None,
                     evidence_wo_ids: list[str] | None = None,
                     as_of: str | None = None) -> dict:
    """创建工单并记录技工分配、根因假设、推荐处置与历史证据交底。"""
    return run_tool("create_workorder", _ctx(as_of), space_id=space_id, raw_text=raw_text,
                    symptom=symptom, urgency=urgency, asset_id=asset_id,
                    assigned_technician_id=assigned_technician_id,
                    hypothesized_root_cause=hypothesized_root_cause,
                    recommended_action=recommended_action, liability=liability,
                    briefing_note=briefing_note, evidence_wo_ids=evidence_wo_ids or [])


@mcp.tool()
def find_technician(skill: str, building_id: str, at: str | None = None,
                    certification: str | None = None, as_of: str | None = None) -> dict:
    """按技能/楼栋/时间匹配技工候选（静态规则，不做排程优化）。"""
    return run_tool("find_technician", _ctx(as_of), skill=skill, building_id=building_id,
                    at=datetime.fromisoformat(at) if at else None,
                    certification=certification)


@mcp.tool()
def notify(channel: str, recipient_role: str, recipient_id: str, message: str,
           wo_id: str | None = None, as_of: str | None = None) -> dict:
    """发送工单通知（确定性模拟），返回可审计的送达回执。"""
    return run_tool("notify", _ctx(as_of), channel=channel, recipient_role=recipient_role,
                    recipient_id=recipient_id, message=message, wo_id=wo_id)


@mcp.tool()
def escalate_to_human(reason: str, detail: str, space_id: str | None = None,
                      asset_id: str | None = None, wo_id: str | None = None,
                      as_of: str | None = None) -> dict:
    """将任务升级给人工（安全/金额/低置信/重复失败/步数上限/合同歧义/租户要求）。"""
    return run_tool("escalate_to_human", _ctx(as_of), reason=reason, detail=detail,
                    space_id=space_id, asset_id=asset_id, wo_id=wo_id)


def main() -> None:
    parser = argparse.ArgumentParser(prog="ops-mcp", description="wagent-ops MCP server")
    parser.add_argument("--http", action="store_true", help="用 streamable-http 而非 stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
