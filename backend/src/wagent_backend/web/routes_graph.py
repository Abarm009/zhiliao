"""图谱路由 —— 可视化数据、实体详情、重置、手工编辑。"""

from __future__ import annotations

import sqlite3
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from wagent_backend.graphRAG.schema import (
    NODE_TYPES,
    RELATION_TYPES,
    GraphIntegrityError,
)
from wagent_backend.graphRAG.store import GraphStore
from wagent_backend.tools.kg_tools import run_tool
from wagent_backend.web.deps import get_store_dep

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("")
def get_graph(store: GraphStore = Depends(get_store_dep)) -> dict:
    """全量图谱数据（前端可视化渲染用）。"""
    data = store.to_dict()
    return {
        "stats": store.stats(),
        "categories": [
            {"key": k, "name": v["label"]} for k, v in NODE_TYPES.items()
        ],
        "nodes": [
            {
                "id": n["entity_id"],
                "name": n["name"],
                "type": n["entity_type"],
                "category": NODE_TYPES[n["entity_type"]]["label"],
                "aliases": n["aliases"],
                "attrs": n["attrs"],
            }
            for n in data["nodes"]
        ],
        "edges": [
            {
                "from": e["from"],
                "to": e["to"],
                "relation": e["relation"],
                "label": RELATION_TYPES[e["relation"]]["label"],
            }
            for e in data["edges"]
        ],
    }


@router.get("/entity/{entity_id}")
def get_entity(entity_id: str) -> dict:
    """实体详情 + 全部关系（复用工具层，保证与 LLM 看到的一致）。"""
    detail = run_tool("kg_get_entity", entity_id=entity_id)
    relations = run_tool("kg_get_relations", entity_id=entity_id, limit=50)
    for r in (detail, relations):
        if r.get("error"):
            raise HTTPException(status_code=404, detail=r["error"]["message"])
    return {"entity": detail["entity"], "edges": relations["edges"]}


@router.post("/reset")
def reset_graph() -> dict:
    """清空并重灌种子图谱（危险操作，前端需二次确认）。"""
    from wagent_backend.graphRAG.store import get_store

    return get_store(rebuild=True).stats()


# ── 手工编辑（仅人工 UI 入口，不进 kg_tools / MCP）──────────────


class EntityPatch(BaseModel):
    name: str | None = None
    attrs: dict[str, str] | None = None  # 覆盖/新增提交的键；空字符串值=删除该键


class LinkSpec(BaseModel):
    target_id: str
    relation: str
    # direction 站在新节点视角：out=新节点→目标，in=目标→新节点
    direction: Literal["out", "in"] = "out"


class EntityCreate(BaseModel):
    type: str
    name: str
    attrs: dict[str, str] = {}
    link: LinkSpec | None = None


class RelationCreate(BaseModel):
    src: str
    dst: str
    relation: str


def _relation_def(relation: str) -> dict:
    """取关系定义，未知关系抛 400。"""
    if relation not in RELATION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"未知关系类型 {relation!r}，可选：{sorted(RELATION_TYPES)}",
        )
    return RELATION_TYPES[relation]


def _check_endpoint_types(rel_def: dict, src_type: str, dst_type: str) -> None:
    """端点类型符合本体？失败抛 400（中文错误信息）。"""
    if src_type not in rel_def["subject"].split("|"):
        raise HTTPException(
            status_code=400,
            detail=f"关系「{rel_def['label']}」的主体应为 {rel_def['subject']}，收到 {src_type}",
        )
    if dst_type not in rel_def["object"].split("|"):
        raise HTTPException(
            status_code=400,
            detail=f"关系「{rel_def['label']}」的客体应为 {rel_def['object']}，收到 {dst_type}",
        )


def _check_relation(store: GraphStore, src: str, dst: str, relation: str) -> None:
    """建边最终校验：关系存在、端点存在、端点类型符合本体。失败抛 400/404。"""
    rel_def = _relation_def(relation)
    for endpoint in (src, dst):
        if not store.has_entity(endpoint):
            raise HTTPException(status_code=404, detail=f"实体不存在：{endpoint}")
    _check_endpoint_types(rel_def, store.type_of(src), store.type_of(dst))


@router.get("/schema")
def get_schema() -> dict:
    """节点类型与关系规则（前端表单按端点类型过滤关系选项用）。"""
    return {
        "node_types": {k: {"label": v["label"], "desc": v["desc"]} for k, v in NODE_TYPES.items()},
        "relation_types": {
            k: {"label": v["label"], "subject": v["subject"], "object": v["object"]}
            for k, v in RELATION_TYPES.items()
        },
    }


@router.post("/entity", status_code=201)
def create_entity(body: EntityCreate, store: GraphStore = Depends(get_store_dep)) -> dict:
    """新建节点，可选同时与已有节点建一条关系。"""
    if body.type not in NODE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"未知节点类型 {body.type!r}，可选：{sorted(NODE_TYPES)}",
        )
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="名称不能为空")
    entity_id = store.next_entity_id(body.type)
    src = dst = None
    if body.link is not None:
        # direction 站在新节点视角：out=新节点→目标，in=目标→新节点
        src, dst = (
            (entity_id, body.link.target_id)
            if body.link.direction == "out"
            else (body.link.target_id, entity_id)
        )
        # 先校验后落图，失败不留半截节点
        rel_def = _relation_def(body.link.relation)
        if not store.has_entity(body.link.target_id):
            raise HTTPException(
                status_code=404, detail=f"实体不存在：{body.link.target_id}"
            )
        target_type = store.type_of(body.link.target_id)
        src_type, dst_type = (
            (body.type, target_type)
            if body.link.direction == "out"
            else (target_type, body.type)
        )
        _check_endpoint_types(rel_def, src_type, dst_type)
    try:
        store.add_entity(entity_id, body.type, name, **body.attrs)
        if body.link is not None:
            store.add_relation(src, dst, body.link.relation, source="手工编辑")
    except GraphIntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    store.save()
    result: dict = {"entity": store.entity(entity_id)}
    if body.link is not None:
        result["edge"] = {"from": src, "to": dst, "relation": body.link.relation}
    return result


@router.patch("/entity/{entity_id}")
def update_entity(
    entity_id: str, body: EntityPatch, store: GraphStore = Depends(get_store_dep)
) -> dict:
    """编辑名称与属性（合并语义）；类型不可改。"""
    try:
        entity = store.update_entity(entity_id, name=body.name, attrs=body.attrs)
    except GraphIntegrityError as e:
        status = 404 if "不存在" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e)) from e
    store.save()
    return {"entity": entity}


@router.delete("/entity/{entity_id}")
def delete_entity(entity_id: str, store: GraphStore = Depends(get_store_dep)) -> dict:
    """硬删除节点（连带所有出入边），返回连带边清单。"""
    try:
        removed = store.remove_entity(entity_id)
    except GraphIntegrityError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    store.save()
    return {
        "deleted": removed["entity"],
        "removed_edges": removed["edges"],
        "edge_count": len(removed["edges"]),
    }


@router.post("/relation", status_code=201)
def create_relation(body: RelationCreate, store: GraphStore = Depends(get_store_dep)) -> dict:
    """两个已有节点之间建边（最终校验端点类型，重复边拒绝）。"""
    _check_relation(store, body.src, body.dst, body.relation)
    if store.has_relation(body.src, body.dst, body.relation):
        raise HTTPException(status_code=400, detail="两节点间已存在相同关系，无需重复创建")
    store.add_relation(body.src, body.dst, body.relation, source="手工编辑")
    store.save()
    return {"edge": {"from": body.src, "to": body.dst, "relation": body.relation}}


# ── space_id 桥接（只读）：图谱 ↔ ops 工单互查 ──────────────
# 关联键是节点 attrs 里的 space_id（ops.db space 表主键）。桥接只发生在
# web 路由层（本就同时依赖两侧），graphRAG 包保持不 import ops，不动任何写路径。


def _ops_conn_ro() -> sqlite3.Connection | None:
    """只读打开 ops.db；库不存在返回 None（视为无工单）。"""
    from wagent_backend.ops.data.db import db_path

    p = db_path()
    if not p.exists():
        return None
    conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/entity/{entity_id}/workorders")
def get_entity_workorders(
    entity_id: str, store: GraphStore = Depends(get_store_dep)
) -> dict:
    """按节点 attrs.space_id 反查 ops 工单（只读；无 space_id 属性返回空列表）。"""
    if not store.has_entity(entity_id):
        raise HTTPException(status_code=404, detail=f"实体不存在：{entity_id}")
    space_id = (store.entity(entity_id).get("attrs") or {}).get("space_id")
    if not space_id:
        return {"space_id": None, "workorders": []}
    conn = _ops_conn_ro()
    if conn is None:
        return {"space_id": space_id, "workorders": []}
    try:
        rows = conn.execute(
            "SELECT wo_id, created_at, symptom, urgency, raw_text"
            " FROM work_order WHERE space_id = ? ORDER BY created_at DESC LIMIT 50",
            (space_id,),
        ).fetchall()
    finally:
        conn.close()
    return {
        "space_id": space_id,
        "workorders": [
            {
                "wo_id": r["wo_id"],
                "created_at": r["created_at"],
                "symptom": r["symptom"],
                "urgency": r["urgency"],
                "raw_text": r["raw_text"][:80],
            }
            for r in rows
        ],
    }


@router.get("/by-space/{space_id}")
def get_entity_by_space(space_id: str, store: GraphStore = Depends(get_store_dep)) -> dict:
    """反查：ops space_id → 持有该属性的图谱节点（无绑定则 404）。"""
    for n in store.to_dict()["nodes"]:
        if (n["attrs"] or {}).get("space_id") == space_id:
            return {"entity": store.entity(n["entity_id"])}
    raise HTTPException(status_code=404, detail=f"无图谱节点绑定空间：{space_id}")
