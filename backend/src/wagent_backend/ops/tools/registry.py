"""registry —— 11 个正式工具的注册表与统一调用入口（双入口之一：进程内直调）。

    run_tool(name, ctx, **kwargs) -> dict
        成功：Output 模型 dump（mode=json，datetime 已序列化）——验收要求
              「所有成功返回都能通过对应 Output 模型校验」
        失败：{"error": {code, message, hint}} 统一信封
              （§14.4 记录的契约缺口：verify/judge 有必填业务字段，
               无法在纯错误场景构造合法 Output —— 返回 error 信封是
               双方约定的过渡协议，不用假值填充业务字段）
    as_openai_tools(names) -> OpenAI function calling schema

事务：成功 commit、失败 rollback —— 写工具（create/notify/escalate/
write/verify）的多条写入天然原子，不留半条记录。
"""

from __future__ import annotations

import json
from typing import Any, Callable

from pydantic import BaseModel, ValidationError

from wagent_backend.ops.contracts import TOOL_REGISTRY
from wagent_backend.ops.tools.context import ToolContext
from wagent_backend.ops.tools.impl import (
    ToolFailure,
    create_workorder,
    escalate_to_human,
    find_technician,
    get_assets_serving_space,
    judge_liability,
    notify,
    query_workorder_history,
    recall_memory,
    resolve_space,
    verify_memory_prediction,
    write_memory,
)

TOOL_DESCRIPTIONS: dict[str, str] = {
    "resolve_space": "将租户原话中的位置描述解析为一个或多个空间候选，返回空间 ID、结构化位置和匹配依据；存在歧义时返回候选，不自行猜测。",
    "get_assets_serving_space": "查询服务指定空间的设备、服务关系、设备台账信息和最新运行参数，可按设备专业（HVAC/ELEC/PLUMB/FIRE）过滤。注意这是服务关系，不是设备安装位置。",
    "query_workorder_history": "按设备、空间、租户或楼栋查询指定时间窗口内的历史工单及其处置流水，可按症状过滤。返回历史记录本身，不替你归纳根因。",
    "recall_memory": "根据自然语言查询和可选作用域检索已归纳的历史洞察，返回洞察正文、证据工单、置信度和相似度。低置信洞察会明确标记。",
    "write_memory": "将你有历史工单证据支持的归纳洞察写入记忆库并生成检索向量。无证据的洞察会被拒绝。",
    "verify_memory_prediction": "在工单闭环后，将已确认根因与洞察预测比较，记录命中并更新置信度与审核状态。",
    "judge_liability": "根据空间合同、设备保修与权属、根因假设和默认责任映射，返回责任方（业主/租户/共同/供应商/不明确）、判定依据及是否需人工确认。",
    "create_workorder": "创建设施运维工单并记录空间、设备、症状、紧急度、技工分配、根因假设、推荐处置和历史证据交底（briefing_note 是治标转治本的关键载体）。",
    "find_technician": "按技能、楼栋、时间匹配可派技工候选（静态规则匹配，不做排程优化）。building_id 用 BLD-A / BLD-B（也接受 A栋/B座 这类名称）。",
    "notify": "向租户联系人、设施经理或技工发送工单相关通知（确定性模拟发送），返回可审计的送达回执。",
    "escalate_to_human": "因安全事件、金额阈值、低置信记忆、重复失败、步骤上限、合同歧义或租户要求，将任务升级给人工并返回票据 ID。",
}

TOOL_IMPLS: dict[str, Callable[..., Any]] = {
    "resolve_space": resolve_space,
    "get_assets_serving_space": get_assets_serving_space,
    "query_workorder_history": query_workorder_history,
    "recall_memory": recall_memory,
    "write_memory": write_memory,
    "verify_memory_prediction": verify_memory_prediction,
    "judge_liability": judge_liability,
    "create_workorder": create_workorder,
    "find_technician": find_technician,
    "notify": notify,
    "escalate_to_human": escalate_to_human,
}

assert set(TOOL_IMPLS) == set(TOOL_REGISTRY) == set(TOOL_DESCRIPTIONS), (
    "实现、契约注册表、描述三者必须恰好覆盖同 11 个工具"
)


def run_tool(name: str, ctx: ToolContext, **kwargs: Any) -> dict[str, Any]:
    if name not in TOOL_IMPLS:
        return {"error": {"code": "invalid_input", "message": f"未知工具：{name}",
                          "hint": None}}
    input_model, output_model = TOOL_REGISTRY[name]
    try:
        inp = input_model(**kwargs)
    except ValidationError as e:
        first = e.errors()[0]
        loc = ".".join(str(x) for x in first["loc"])
        return {"error": {
            "code": "invalid_input",
            "message": f"参数校验失败：{loc} {first['msg']}",
            "hint": None,
        }}
    try:
        out = TOOL_IMPLS[name](ctx, inp)
    except ToolFailure as f:
        ctx.conn.rollback()
        return {"error": {"code": f.code, "message": f.message, "hint": f.hint}}
    except Exception as e:  # 数据库等上游异常 → upstream_error，不中断循环
        ctx.conn.rollback()
        return {"error": {"code": "upstream_error", "message": f"{type(e).__name__}: {e}",
                          "hint": None}}
    ctx.conn.commit()
    if isinstance(out, BaseModel):
        return out.model_dump(mode="json")
    return out


def as_openai_tools(names: list[str] | None = None) -> list[dict[str, Any]]:
    """导出 OpenAI function calling schema（只暴露 names 指定的子集）。"""
    out: list[dict[str, Any]] = []
    for name in names or list(TOOL_REGISTRY):
        input_model, _ = TOOL_REGISTRY[name]
        schema = input_model.model_json_schema()
        for drop in ("title", "additionalProperties"):
            schema.pop(drop, None)
        out.append({
            "type": "function",
            "function": {
                "name": name,
                "description": TOOL_DESCRIPTIONS[name],
                "parameters": schema,
            },
        })
    return out


def dump_result(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, default=str)
