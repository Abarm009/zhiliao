"""LLM 工具层 —— 7 个知识图谱查询工具。

约定（沿用主项目 agent/tools/schemas.py 的惯例）：
- 每个工具 = pydantic 入参模型 + 出参模型 + 纯函数
- 统一返回包装：error 字段区分「查不到」（Agent 应继续推理）与「入参错」
  （Agent 应修正参数重试），不抛异常打断调用方
- 三个消费入口共享本注册表：MCP server / OpenAI function calling / 进程内直调
- 本层只依赖 graphRAG 的查询接口，不知道存储是 networkx 还是别的
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from wagent_backend.graphRAG.schema import (
    RELATION_TYPES,
    Entity,
    EntityDetail,
    GraphIntegrityError,
    PathHop,
    RelationEdge,
)
from wagent_backend.graphRAG.store import GraphStore, get_store

# ═══════════════════════════════════════════════════════════════
# 通用返回包装
# ═══════════════════════════════════════════════════════════════


class ToolError(BaseModel):
    code: Literal["not_found", "ambiguous", "invalid_input"]
    message: str
    hint: str | None = None


# ═══════════════════════════════════════════════════════════════
# 1. kg_get_schema —— LLM 先调这个，了解图谱里有什么可查
# ═══════════════════════════════════════════════════════════════


class KgGetSchemaInput(BaseModel):
    pass  # 无入参


class KgGetSchemaOutput(BaseModel):
    node_types: dict[str, dict[str, str]] = Field(description="节点类型 → 定义")
    relation_types: dict[str, dict[str, str]] = Field(description="关系类型 → 定义")
    example_questions: list[str] = Field(description="可回答的典型问题")
    error: ToolError | None = None


def _get_schema() -> KgGetSchemaOutput:
    from wagent_backend.graphRAG.schema import NODE_TYPES

    return KgGetSchemaOutput(
        node_types=NODE_TYPES,
        relation_types=RELATION_TYPES,
        example_questions=[
            "七氟丙烷驱动气瓶装在哪？（kg_get_space_chain）",
            "谁负责/管理这台设备？供应商是谁？（kg_get_relations）",
            "这台设备和工程部是什么关系？（kg_find_path）",
            "A座 AB1F 有哪些设备？（kg_get_relations 查 Room/Floor 的入边）",
            "A栋男卫生间一共有多少个马桶？（kg_count_entities，统计类问题不要逐层翻）",
        ],
    )


# ═══════════════════════════════════════════════════════════════
# 2. kg_search_entities —— 关键词/类型搜索实体
# ═══════════════════════════════════════════════════════════════


class KgSearchEntitiesInput(BaseModel):
    keyword: str | None = Field(
        default=None, description="按 实体ID/名称/别名 子串模糊匹配，如 '气瓶' / 'A座' / '王'"
    )
    entity_type: str | None = Field(
        default=None,
        description="限定节点类型 key：Device/Person/Department/Vendor/Project/Building/Floor/Room",
    )
    limit: int = Field(default=10, ge=1, le=50)


class KgSearchEntitiesOutput(BaseModel):
    matches: list[Entity] = Field(default_factory=list)
    error: ToolError | None = None


def _search_entities(
    keyword: str | None = None, entity_type: str | None = None, limit: int = 10
) -> KgSearchEntitiesOutput:
    store = get_store()
    try:
        rows = store.search(keyword=keyword, entity_type=entity_type, limit=limit)
    except GraphIntegrityError as e:
        return KgSearchEntitiesOutput(error=ToolError(code="invalid_input", message=str(e)))
    if not rows:
        return KgSearchEntitiesOutput(
            error=ToolError(
                code="not_found",
                message=f"没有匹配的实体（keyword={keyword!r}, entity_type={entity_type!r}）",
                hint="先调 kg_get_schema 看可用类型，或放宽关键词",
            )
        )
    return KgSearchEntitiesOutput(matches=[Entity(**r) for r in rows])


# ═══════════════════════════════════════════════════════════════
# 实体引用解析（ID 或 名称/别名 精确匹配）—— 3/4/5/6 号工具共用
# ═══════════════════════════════════════════════════════════════


def _resolve(store: GraphStore, ref: str) -> tuple[str | None, ToolError | None]:
    """ref 可以是实体 ID，也可以是名称/别名的精确匹配。"""
    if store.has_entity(ref):
        return ref, None
    exact = store.find_by_name(ref)
    if len(exact) == 1:
        return exact[0], None
    if len(exact) > 1:
        cand = "、".join(f"{i}({store.entity(i)['name']})" for i in exact[:5])
        return None, ToolError(
            code="ambiguous", message=f"'{ref}' 命中多个实体：{cand}", hint="改用唯一 entity_id"
        )
    return None, ToolError(
        code="not_found",
        message=f"实体 {ref!r} 不存在",
        hint="用 kg_search_entities 模糊搜索拿候选",
    )


# ═══════════════════════════════════════════════════════════════
# 3. kg_get_entity —— 实体详情
# ═══════════════════════════════════════════════════════════════


class KgGetEntityInput(BaseModel):
    entity_id: str = Field(description="实体 ID 或其名称/别名（精确）")


class KgGetEntityOutput(BaseModel):
    entity: EntityDetail | None = None
    error: ToolError | None = None


def _get_entity(entity_id: str) -> KgGetEntityOutput:
    store = get_store()
    resolved, err = _resolve(store, entity_id)
    if err:
        return KgGetEntityOutput(error=err)
    return KgGetEntityOutput(entity=EntityDetail(**store.entity(resolved)))


# ═══════════════════════════════════════════════════════════════
# 4. kg_get_relations —— 一跳关系
# ═══════════════════════════════════════════════════════════════


class KgGetRelationsInput(BaseModel):
    entity_id: str = Field(description="实体 ID 或其名称/别名（精确）")
    direction: Literal["out", "in", "both"] = Field(
        default="both",
        description="out=该实体指向别人；in=别人指向该实体（如查房间里的设备用 in+located_in）",
    )
    relation: str | None = Field(
        default=None, description="限定关系类型 key，见 kg_get_schema"
    )
    limit: int = Field(default=20, ge=1, le=100)


class KgGetRelationsOutput(BaseModel):
    entity: Entity | None = Field(default=None, description="查询主体")
    edges: list[RelationEdge] = Field(default_factory=list)
    error: ToolError | None = None


def _get_relations(
    entity_id: str,
    direction: Literal["out", "in", "both"] = "both",
    relation: str | None = None,
    limit: int = 20,
) -> KgGetRelationsOutput:
    store = get_store()
    resolved, err = _resolve(store, entity_id)
    if err:
        return KgGetRelationsOutput(error=err)
    try:
        rows = store.neighbors(
            resolved, direction=direction, relation=relation, limit=limit
        )
    except (GraphIntegrityError, ValueError) as e:
        return KgGetRelationsOutput(error=ToolError(code="invalid_input", message=str(e)))
    return KgGetRelationsOutput(
        entity=Entity(**store.entity(resolved)),
        edges=[
            RelationEdge(
                relation=r["relation"],
                relation_label=RELATION_TYPES[r["relation"]]["label"],
                direction=r["direction"],
                other=Entity(**store.entity(r["other"])),
            )
            for r in rows
        ],
    )


# ═══════════════════════════════════════════════════════════════
# 5. kg_find_path —— 两实体间路径
# ═══════════════════════════════════════════════════════════════


class KgFindPathInput(BaseModel):
    source_id: str = Field(description="起点实体 ID/名称")
    target_id: str = Field(description="终点实体 ID/名称")
    max_hops: int = Field(default=4, ge=1, le=6)


class KgFindPathOutput(BaseModel):
    found: bool = False
    hops: list[PathHop] = Field(default_factory=list)
    error: ToolError | None = None


def _find_path(source_id: str, target_id: str, max_hops: int = 4) -> KgFindPathOutput:
    store = get_store()
    resolved = []
    for ref in (source_id, target_id):
        rid, err = _resolve(store, ref)
        if err:
            return KgFindPathOutput(error=err)
        resolved.append(rid)
    src, dst = resolved
    hops = store.find_path(src, dst, max_hops=max_hops)
    if hops is None:
        return KgFindPathOutput(
            error=ToolError(
                code="not_found",
                message=f"{src} 与 {dst} 之间 {max_hops} 跳内无路径",
                hint="调 kg_get_schema 确认两者是否有共同邻居，或放宽 max_hops",
            )
        )
    return KgFindPathOutput(
        found=True,
        hops=[
            PathHop(
                relation=h["relation"],
                relation_label=RELATION_TYPES[h["relation"]]["label"],
                from_id=h["from"],
                from_name=h["from_name"],
                to_id=h["to"],
                to_name=h["to_name"],
            )
            for h in hops
        ],
    )


# ═══════════════════════════════════════════════════════════════
# 6. kg_get_space_chain —— 设备/空间的完整空间定位链
# ═══════════════════════════════════════════════════════════════


class KgGetSpaceChainInput(BaseModel):
    entity_id: str = Field(description="设备或空间实体的 ID/名称")


class KgGetSpaceChainOutput(BaseModel):
    chain: list[Entity] = Field(
        default_factory=list,
        description="从该实体到项目根的有序空间链：设备 → 房间 → 楼层 → 楼栋 → 项目",
    )
    error: ToolError | None = None


def _get_space_chain(entity_id: str) -> KgGetSpaceChainOutput:
    store = get_store()
    resolved, err = _resolve(store, entity_id)
    if err:
        return KgGetSpaceChainOutput(error=err)
    try:
        chain = store.space_chain(resolved)
    except ValueError as e:
        return KgGetSpaceChainOutput(
            error=ToolError(code="invalid_input", message=str(e), hint="改用 kg_get_relations")
        )
    return KgGetSpaceChainOutput(chain=[Entity(**c) for c in chain])


# ═══════════════════════════════════════════════════════════════
# 7. kg_count_entities —— 跨区域聚合统计（数量类问题一次出答案）
# ═══════════════════════════════════════════════════════════════

# 匹配上限：统计类问题只要数量，清单截断防上下文爆炸
_COUNT_LIST_LIMIT = 100

# 位置口语同义词（「男卫生间/男厕所」→ 规范名「男洗手间」，与图谱命名口径一致）
_LOC_SYNS = {"卫生间": "洗手间", "厕所": "洗手间"}


class KgCountEntitiesInput(BaseModel):
    keyword: str = Field(
        description="实体名称/设备类型关键词，如 '马桶' / '水龙头' / '风机盘管'"
    )
    entity_type: str = Field(
        default="Device",
        description="限定节点类型 key（默认 Device）；统计空间时传 Room/Floor 等",
    )
    scope: str | None = Field(
        default=None,
        description="统计范围：楼栋/楼层/空间的 ID 或名称（如 'A栋' / 'A座25楼'）；不传=全图",
    )
    location_keyword: str | None = Field(
        default=None,
        description="只统计名称含该词的空间内的实体（如 '男卫生间'；口语同义词自动归一）",
    )


class KgCountEntitiesOutput(BaseModel):
    count: int = Field(default=0, description="命中实体总数（不受 matched 截断影响）")
    scope: Entity | None = Field(default=None, description="统计范围实体（未传 scope 为 null）")
    matched: list[Entity] = Field(
        default_factory=list,
        description=f"命中实体清单（最多列 {_COUNT_LIST_LIMIT} 个，超出截断）",
    )
    truncated: bool = False
    error: ToolError | None = None


def _count_entities(
    keyword: str,
    entity_type: str = "Device",
    scope: str | None = None,
    location_keyword: str | None = None,
) -> KgCountEntitiesOutput:
    from wagent_backend.graphRAG.schema import NODE_TYPES

    store = get_store()
    if not (keyword or "").strip():
        return KgCountEntitiesOutput(
            error=ToolError(code="invalid_input", message="keyword 不能为空"))
    if entity_type not in NODE_TYPES:
        return KgCountEntitiesOutput(
            error=ToolError(code="invalid_input",
                            message=f"未知节点类型 {entity_type!r}，可选：{sorted(NODE_TYPES)}"))
    scope_id = None
    scope_entity = None
    if scope and scope.strip():
        scope_id, err = _resolve(store, scope.strip())
        if err:
            return KgCountEntitiesOutput(error=err)
        scope_entity = Entity(**store.entity(scope_id))

    universe = store.descendants(scope_id) if scope_id else {
        n for n, _ in store._g.nodes(data=True)
    }
    kw = keyword.strip().casefold()
    loc_kw = (location_keyword or "").strip()
    for src, canon in _LOC_SYNS.items():
        loc_kw = loc_kw.replace(src, canon)
    loc_kw = loc_kw.casefold()

    def kw_hit(node_id: str) -> bool:
        d = store._g.nodes[node_id]
        hay = [d["name"], *d["aliases"], d["attrs"].get("设备类型", "")]
        return any(kw in h.casefold() for h in hay)

    def loc_hit(node_id: str) -> bool:
        if not loc_kw:
            return True
        if store._g.nodes[node_id]["entity_type"] == "Room":
            rooms = [node_id]
        else:
            # 设备等非空间实体：取 located_in 指向的空间名做过滤
            rooms = [
                dst for _, dst, ed in store._g.out_edges(node_id, data=True)
                if ed["relation"] == "located_in"
            ]
        return any(
            loc_kw in store._g.nodes[r]["name"].casefold()
            or any(loc_kw in a.casefold() for a in store._g.nodes[r]["aliases"])
            for r in rooms
        )

    matched_ids = sorted(
        n for n in universe
        if store._g.nodes[n]["entity_type"] == entity_type
        and kw_hit(n) and loc_hit(n)
    )
    return KgCountEntitiesOutput(
        count=len(matched_ids),
        scope=scope_entity,
        matched=[Entity(**store.entity(i)) for i in matched_ids[:_COUNT_LIST_LIMIT]],
        truncated=len(matched_ids) > _COUNT_LIST_LIMIT,
    )


# ═══════════════════════════════════════════════════════════════
# 注册表与统一执行入口
# ═══════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    fn: Callable[..., BaseModel]


KG_TOOL_REGISTRY: dict[str, ToolSpec] = {
    spec.name: spec
    for spec in [
        ToolSpec(
            name="kg_get_schema",
            description="获取知识图谱本体：8 类节点（设备/人员/部门/供应商/项目/楼栋/楼层/空间）与 8 种关系的定义。回答图谱问题前先调它。",
            input_model=KgGetSchemaInput,
            output_model=KgGetSchemaOutput,
            fn=_get_schema,
        ),
        ToolSpec(
            name="kg_search_entities",
            description="按关键词（实体ID/名称/别名，子串模糊）和节点类型搜索实体，返回候选列表。不确定 ID 时先用它。",
            input_model=KgSearchEntitiesInput,
            output_model=KgSearchEntitiesOutput,
            fn=_search_entities,
        ),
        ToolSpec(
            name="kg_get_entity",
            description="获取单个实体的全部属性（设备编号/品牌/规格/日期/价值/状态等登记表字段）。",
            input_model=KgGetEntityInput,
            output_model=KgGetEntityOutput,
            fn=_get_entity,
        ),
        ToolSpec(
            name="kg_get_relations",
            description="查某实体的一跳关系（可按方向/关系类型过滤）。回答『谁负责/供应商是谁/这房间有哪些设备』这类问题。",
            input_model=KgGetRelationsInput,
            output_model=KgGetRelationsOutput,
            fn=_get_relations,
        ),
        ToolSpec(
            name="kg_find_path",
            description="找两个实体之间的最短关系路径（忽略方向）。回答『X 和 Y 是什么关系』。",
            input_model=KgFindPathInput,
            output_model=KgFindPathOutput,
            fn=_find_path,
        ),
        ToolSpec(
            name="kg_get_space_chain",
            description="获取设备/空间的完整空间定位链：设备 →(位于) 房间 →(属于) 楼层 → 楼栋 → 项目。回答『这设备在哪』。",
            input_model=KgGetSpaceChainInput,
            output_model=KgGetSpaceChainOutput,
            fn=_get_space_chain,
        ),
        ToolSpec(
            name="kg_count_entities",
            description="跨区域聚合统计：按关键词统计某范围（楼栋/楼层/空间，可再限定所在空间类型）内的实体数量，一次调用直接出总数。回答『A栋男洗手间有多少个马桶』这类数量问题必须用它，不要逐楼层/逐房间翻关系。",
            input_model=KgCountEntitiesInput,
            output_model=KgCountEntitiesOutput,
            fn=_count_entities,
        ),
    ]
}


def run_tool(name: str, **kwargs: object) -> dict:
    """进程内直调入口：入参经 pydantic 校验，出参 model_dump。

    入参不合法时返回 invalid_input 的在带错误（与查询失败同构），
    调用方（LLM 循环 / MCP）无需 try/except。
    """
    spec = KG_TOOL_REGISTRY.get(name)
    if spec is None:
        return {
            "error": ToolError(
                code="invalid_input",
                message=f"未知工具 {name!r}，可选：{sorted(KG_TOOL_REGISTRY)}",
            ).model_dump()
        }
    try:
        args = spec.input_model.model_validate(kwargs)
    except ValidationError as e:
        return {
            "error": ToolError(
                code="invalid_input", message=f"入参校验失败：{e}"
            ).model_dump()
        }
    result = spec.fn(**args.model_dump())
    return result.model_dump()


def as_openai_tools() -> list[dict]:
    """导出 OpenAI Chat Completions 的 tools 参数（function calling）。"""
    return [
        {
            "type": "function",
            "function": {
                "name": spec.name,
                "description": spec.description,
                "parameters": spec.input_model.model_json_schema(),
            },
        }
        for spec in KG_TOOL_REGISTRY.values()
    ]
