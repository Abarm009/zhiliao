"""GraphStore —— networkx 内存图 + JSON 文件持久化。

设计取舍：
- 内存图 + 单 JSON 文件，零外部服务（数据规模：节点百级、边千级内最佳）
- 建边时校验类型与端点，坏数据在建图阶段就报错，不留给查询层
- 持久化按 id/关系排序后落盘，文件对 git diff 友好，可直接人读
- 对外接口（工具层唯一依赖的形状）：
    search / neighbors / find_path / space_chain / entity / stats
  换存储（Neo4j/SQLite）时只需重写本文件，其余层不动。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import networkx as nx

from wagent_backend.graphRAG.schema import (
    NODE_TYPES,
    RELATION_TYPES,
    GraphIntegrityError,
)

DEFAULT_DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "kg.json"

# 空间链允许的起始类型（其余类型不在空间层级上）
_SPACE_CHAIN_TYPES = {"Device", "Room", "Floor", "Building", "Project"}

# 查询词口语同义词归一：图谱规范名用「洗手间」，查询里的「卫生间/厕所」先归一再匹配
_QUERY_SYNS = ("卫生间", "厕所")


def _query_variants(kw: str) -> list[str]:
    """查询词变体：原词 + 同义词归一后的形式（「男卫生间」→「男洗手间」）。"""
    out = [kw]
    for syn in _QUERY_SYNS:
        if syn in kw:
            out.append(kw.replace(syn, "洗手间"))
    return out


class GraphStore:
    def __init__(self) -> None:
        self._g = nx.MultiDiGraph()

    # ── 建图 ────────────────────────────────────────────────

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        aliases: list[str] | None = None,
        **attrs: str,
    ) -> None:
        if entity_type not in NODE_TYPES:
            raise GraphIntegrityError(
                f"未知节点类型 {entity_type!r}，可选：{sorted(NODE_TYPES)}"
            )
        if entity_id in self._g:
            raise GraphIntegrityError(f"实体 ID 重复：{entity_id}")
        self._g.add_node(
            entity_id,
            entity_type=entity_type,
            name=name,
            aliases=list(aliases or []),
            attrs={k: v for k, v in attrs.items() if v is not None},
        )

    def add_relation(
        self, src: str, dst: str, relation: str, **edge_attrs: Any
    ) -> None:
        if relation not in RELATION_TYPES:
            raise GraphIntegrityError(
                f"未知关系类型 {relation!r}，可选：{sorted(RELATION_TYPES)}"
            )
        for endpoint in (src, dst):
            if endpoint not in self._g:
                raise GraphIntegrityError(
                    f"关系 {relation} 的端点 {endpoint!r} 不存在，请先 add_entity"
                )
        self._g.add_edge(src, dst, relation=relation, **edge_attrs)

    def has_relation(self, src: str, dst: str, relation: str) -> bool:
        """已存在同向同类型边？（抽取器去重用）"""
        return any(
            ed["relation"] == relation
            for _, d, ed in self._g.out_edges(src, data=True, keys=False)
            if d == dst
        ) if self._g.has_edge(src, dst) else False

    # ── 手工编辑（图谱页 UI 用）─────────────────────────────

    def remove_entity(self, entity_id: str) -> dict[str, Any]:
        """硬删除节点（连带所有出入边）；返回被删节点与连带边清单。"""
        if entity_id not in self._g:
            raise GraphIntegrityError(f"实体不存在：{entity_id}")
        entity = self.entity(entity_id)
        edges = [
            {"from": a, "to": b, "relation": ed["relation"]}
            for a, b, ed in list(self._g.out_edges(entity_id, data=True))
            + list(self._g.in_edges(entity_id, data=True))
        ]
        self._g.remove_node(entity_id)
        return {"entity": entity, "edges": edges}

    def update_entity(
        self,
        entity_id: str,
        name: str | None = None,
        attrs: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """合并更新名称/属性；类型不可改（改了会破坏已有边的端点约束）。

        attrs 约定：提交的键覆盖/新增，未提交的键不动；值为空字符串表示删除该键。
        """
        if entity_id not in self._g:
            raise GraphIntegrityError(f"实体不存在：{entity_id}")
        d = self._g.nodes[entity_id]
        if name is not None:
            name = name.strip()
            if not name:
                raise GraphIntegrityError("名称不能为空")
            d["name"] = name
        for k, v in (attrs or {}).items():
            k = str(k).strip()
            if not k:
                continue
            if v is None or str(v).strip() == "":
                d["attrs"].pop(k, None)
            else:
                d["attrs"][k] = str(v)
        return self.entity(entity_id)

    # ── 查询 ────────────────────────────────────────────────

    def has_entity(self, entity_id: str) -> bool:
        return entity_id in self._g

    def entity(self, entity_id: str) -> dict[str, Any]:
        """返回节点数据（entity_id/type/type_label/name/aliases/attrs）；不存在抛 KeyError。"""
        if entity_id not in self._g:
            raise KeyError(entity_id)
        d = self._g.nodes[entity_id]
        return {
            "entity_id": entity_id,
            "entity_type": d["entity_type"],
            "type_label": NODE_TYPES[d["entity_type"]]["label"],
            "name": d["name"],
            "aliases": list(d["aliases"]),
            "attrs": dict(d["attrs"]),
        }

    def type_of(self, entity_id: str) -> str:
        return self.entity(entity_id)["entity_type"]

    def find_by_name(self, name: str, entity_type: str | None = None) -> list[str]:
        """名称/别名精确匹配（抽取器做实体链接用）。"""
        kw = name.strip().casefold()
        hits = []
        for node_id, d in self._g.nodes(data=True):
            if entity_type and d["entity_type"] != entity_type:
                continue
            if kw == d["name"].casefold() or kw in {a.casefold() for a in d["aliases"]}:
                hits.append(node_id)
        return hits

    def descendants(self, entity_id: str) -> set[str]:
        """空间层级向下闭包：entity_id 的全部子孙（沿 part_of/located_in 反向走）。

        层级边方向是 子 → 父（Room part_of Floor、Device located_in Room），
        所以子孙 = 沿入边 BFS。聚合统计（如「A栋男卫生间马桶数量」）用。
        """
        if entity_id not in self._g:
            raise KeyError(entity_id)
        seen: set[str] = set()
        frontier = [entity_id]
        while frontier:
            nxt: list[str] = []
            for node in frontier:
                for src, _, ed in self._g.in_edges(node, data=True):
                    if ed["relation"] in ("part_of", "located_in") and src not in seen:
                        seen.add(src)
                        nxt.append(src)
            frontier = nxt
        return seen

    def next_entity_id(self, entity_type: str) -> str:
        """为抽取新建实体生成不冲突的 ID：EXT-{类型缩写}-{序号}。"""
        prefix = f"EXT-{entity_type[:3].upper()}-"
        n = len({i for i in self._g.nodes if i.startswith(prefix)}) + 1
        while f"{prefix}{n:03d}" in self._g:
            n += 1
        return f"{prefix}{n:03d}"

    def search(
        self,
        keyword: str | None = None,
        entity_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """按 关键词（id/名称/别名，子串模糊）+ 类型 过滤。无关键词返回该类型全部。"""
        if entity_type is not None and entity_type not in NODE_TYPES:
            raise GraphIntegrityError(
                f"未知节点类型 {entity_type!r}，可选：{sorted(NODE_TYPES)}"
            )
        kw = (keyword or "").strip().casefold()
        kws = _query_variants(kw)
        hits: list[tuple[int, dict[str, Any]]] = []
        for node_id, d in self._g.nodes(data=True):
            if entity_type and d["entity_type"] != entity_type:
                continue
            if not kw:
                hits.append((3, self.entity(node_id)))
                continue
            tier = self._match_tier(node_id, d, kws)
            if tier is not None:
                hits.append((tier, self.entity(node_id)))
        # tier 大者优先（精确 > 别名精确 > 子串），同 tier 按 id 稳定排序
        hits.sort(key=lambda t: (-t[0], t[1]["entity_id"]))
        return [h for _, h in hits[:limit]]

    @staticmethod
    def _match_tier(node_id: str, d: dict, kws: list[str]) -> int | None:
        best: int | None = None
        for kw in kws:
            if kw == node_id.casefold() or kw == d["name"].casefold():
                tier = 3
            elif any(kw == a.casefold() for a in d["aliases"]):
                tier = 2
            else:
                hay = [node_id, d["name"], *d["aliases"]]
                tier = 1 if any(kw in h.casefold() for h in hay) else None
            if tier is not None and (best is None or tier > best):
                best = tier
        return best

    def neighbors(
        self,
        entity_id: str,
        direction: str = "both",
        relation: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """一跳邻居。direction: out/in/both（站在 entity_id 视角）。"""
        if entity_id not in self._g:
            raise KeyError(entity_id)
        if direction not in ("out", "in", "both"):
            raise ValueError(f"direction 取值应为 out/in/both，收到 {direction!r}")
        if relation is not None and relation not in RELATION_TYPES:
            raise GraphIntegrityError(
                f"未知关系类型 {relation!r}，可选：{sorted(RELATION_TYPES)}"
            )
        out: list[dict[str, Any]] = []
        if direction in ("out", "both"):
            for _, dst, ed in self._g.out_edges(entity_id, data=True):
                if relation and ed["relation"] != relation:
                    continue
                out.append(
                    {"relation": ed["relation"], "direction": "out", "other": dst}
                )
        if direction in ("in", "both"):
            for src, _, ed in self._g.in_edges(entity_id, data=True):
                if relation and ed["relation"] != relation:
                    continue
                out.append(
                    {"relation": ed["relation"], "direction": "in", "other": src}
                )
        out.sort(key=lambda e: (e["direction"], e["relation"], e["other"]))
        return out[:limit]

    def find_path(self, src: str, dst: str, max_hops: int = 4) -> list[dict] | None:
        """忽略边方向找最短路径；返回逐跳 [{relation, from, to, from_name, to_name}]。"""
        for endpoint in (src, dst):
            if endpoint not in self._g:
                raise KeyError(endpoint)
        und = self._g.to_undirected(as_view=True)
        try:
            nodes = nx.shortest_path(und, src, dst)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
        if len(nodes) - 1 > max_hops:
            return None
        hops: list[dict] = []
        for a, b in zip(nodes, nodes[1:]):
            hops.append(
                {
                    "relation": self._edge_relation_any_direction(a, b),
                    "from": a,
                    "to": b,
                    "from_name": self._g.nodes[a]["name"],
                    "to_name": self._g.nodes[b]["name"],
                }
            )
        return hops

    def _edge_relation_any_direction(self, a: str, b: str) -> str:
        if self._g.has_edge(a, b):
            return self._g.edges[a, b, 0]["relation"]
        return self._g.edges[b, a, 0]["relation"]

    def space_chain(self, entity_id: str) -> list[dict[str, Any]]:
        """设备/空间的完整空间定位链：Device →(位于) Room →(属于) Floor → Building → Project。

        非空间链上的实体（人员/部门/供应商）抛 ValueError。
        """
        if entity_id not in self._g:
            raise KeyError(entity_id)
        if self.type_of(entity_id) not in _SPACE_CHAIN_TYPES:
            raise ValueError(
                f"{entity_id}（{self.type_of(entity_id)}）不在空间层级上，无法生成空间链；"
                f"可改用 kg_get_relations 查看其关系"
            )
        chain: list[dict[str, Any]] = []
        cur = entity_id
        while True:
            chain.append(self.entity(cur))
            nxt = self._next_up(cur)
            if nxt is None:
                break
            cur = nxt
        return chain

    def _next_up(self, node_id: str) -> str | None:
        """空间链的下一跳：设备先走 located_in，之后沿 part_of 上行，Project 到顶。"""
        etype = self.type_of(node_id)
        if etype == "Device":
            want = "located_in"
        elif etype in ("Room", "Floor", "Building"):
            want = "part_of"
        else:  # Project：链顶
            return None
        for _, dst, ed in self._g.out_edges(node_id, data=True):
            if ed["relation"] == want:
                return dst
        return None

    def stats(self) -> dict[str, Any]:
        by_type: dict[str, int] = {}
        for _, d in self._g.nodes(data=True):
            by_type[d["entity_type"]] = by_type.get(d["entity_type"], 0) + 1
        by_rel: dict[str, int] = {}
        for _, _, ed in self._g.edges(data=True):
            by_rel[ed["relation"]] = by_rel.get(ed["relation"], 0) + 1
        return {
            "node_count": self._g.number_of_nodes(),
            "edge_count": self._g.number_of_edges(),
            "nodes_by_type": by_type,
            "edges_by_relation": by_rel,
        }

    # ── 持久化 ──────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        nodes = []
        for node_id, d in self._g.nodes(data=True):
            nodes.append(
                {
                    "entity_id": node_id,
                    "entity_type": d["entity_type"],
                    "name": d["name"],
                    "aliases": d["aliases"],
                    "attrs": d["attrs"],
                }
            )
        edges = []
        for a, b, ed in self._g.edges(data=True):
            attrs = {k: v for k, v in ed.items() if k != "relation"}
            edges.append(
                {"from": a, "to": b, "relation": ed["relation"], "attrs": attrs}
            )
        # 排序落盘：同图同文件，便于 diff 与校验
        nodes.sort(key=lambda n: n["entity_id"])
        edges.sort(key=lambda e: (e["from"], e["relation"], e["to"]))
        return {"nodes": nodes, "edges": edges}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GraphStore:
        store = cls()
        for n in data["nodes"]:
            store.add_entity(
                n["entity_id"],
                n["entity_type"],
                n["name"],
                aliases=n.get("aliases") or [],
                **n.get("attrs") or {},
            )
        for e in data["edges"]:
            store.add_relation(
                e["from"], e["to"], e["relation"], **e.get("attrs") or {}
            )
        return store

    def save(self, path: Path | str | None = None) -> Path:
        path = Path(path or data_file())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path

    @classmethod
    def load(cls, path: Path | str | None = None) -> GraphStore:
        path = Path(path or data_file())
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


def data_file() -> Path:
    return Path(os.environ.get("WAGENT_KG_DATA", DEFAULT_DATA_FILE))


_store: GraphStore | None = None


def get_store(rebuild: bool = False) -> GraphStore:
    """进程级单例：有数据文件则加载，否则从 seed 构建并落盘。"""
    global _store
    if _store is None or rebuild:
        from wagent_backend.graphRAG.seed import build_seed_graph

        if rebuild or not data_file().exists():
            _store = build_seed_graph()
            _store.save()
        else:
            _store = GraphStore.load()
    return _store
