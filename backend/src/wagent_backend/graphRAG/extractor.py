"""TripleExtractor —— LLM 从工单文本/截图实时抽取三元组并入图（"图谱会自己长大"）。

流程：
    工单文本/图片 → LLM（本体约束 prompt，只允许 8 类节点/8 种关系）
                  → JSON 三元组 → 本体校验 → 实体链接（同名/别名对到已有节点）
                  → 新实体建 ID 入图 → 新边 MERGE 去重 → 落盘 → 返回生长报告

解耦：不依赖具体 LLM 客户端。构造时注入 complete(messages) -> str 的可调用，
     web 层用 qwen3.7-flash 实现，测试用假函数。graphRAG 保持无 openai 依赖。
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field

from wagent_backend.graphRAG.schema import (
    NODE_TYPES,
    RELATION_TYPES,
    Entity,
)
from wagent_backend.graphRAG.store import GraphStore

# 注入的 LLM 调用形状：OpenAI 风格 messages → 纯文本回复
CompleteFn = Callable[[list[dict[str, Any]]], str]

_SYSTEM_PROMPT = """你是设备运维知识图谱的三元组抽取引擎。

## 本体（只能使用这些类型，抽不出来的直接跳过，禁止编造类型）

节点类型：
{node_types}

关系类型（subject_type → object_type 为允许的端点类型，竖线分隔多选）：
{relation_types}

## 输出格式
只输出一个 JSON 数组，不要任何解释、不要 markdown 代码块。数组元素：
{{
  "subject": {{"name": "...", "type": "节点类型key"}},
  "predicate": "关系类型key",
  "object": {{"name": "...", "type": "节点类型key"}},
  "attrs": {{"属性名": "属性值"}}   // 可选，只挂在 subject 上，如 设备编号/故障现象
}}

## 规则
1. 名称用原文里的叫法，不要改写；人名保持原样
2. predicate 必须是上面列出的关系 key；subject/object 的 type 必须与该关系允许的端点类型匹配
3. 一段工单通常能抽 1~6 条；宁缺毋滥，没有就输出 []
4. attrs 的 key 用中文（如 现象/处置/日期），值从原文摘录
5. **禁止抽供应商（Vendor）**：工单里出现的公司/商家名（购买渠道、电商、品牌方等）不是设备台账供应商，一律不抽
"""


# 空间口语同义词归一（实体链接用）：规范名为「洗手间」，工单里「13楼男卫生间/
# 13楼男厕所」应链接到已有的「A栋13层男洗手间」（RM-A-13-WCM），而不是新建
# 游离的 EXT-ROO 节点。
_ROOM_NAME_SYNS = {"卫生间": "洗手间", "厕所": "洗手间"}


def _normalize_room_name(name: str) -> str:
    for src, canon in _ROOM_NAME_SYNS.items():
        name = name.replace(src, canon)
    return name


class ExtractedTriple(BaseModel):
    subject_name: str
    subject_type: str
    predicate: str
    object_name: str
    object_type: str
    attrs: dict[str, str] = Field(default_factory=dict)


class ExtractionReport(BaseModel):
    """一次抽取入图的完整报告（前端用来展示"图谱长大了多少"）。"""

    triples_raw: int = 0                       # LLM 返回的三元组数
    added_nodes: list[Entity] = Field(default_factory=list)
    added_edges: list[dict[str, str]] = Field(default_factory=list)  # {from,to,relation,label}
    skipped: list[dict[str, str]] = Field(default_factory=list)      # {reason, triple}
    grown: bool = False                        # 图是否真的变大


class TripleExtractor:
    def __init__(self, complete: CompleteFn):
        self._complete = complete

    # ── 第一步：LLM 抽取 ───────────────────────────────────

    def extract(
        self,
        text: str | None = None,
        image_b64: str | None = None,
        image_mime: str = "image/png",
    ) -> list[ExtractedTriple]:
        if not text and not image_b64:
            raise ValueError("text 与 image_b64 至少给一个")
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt()}
        ]
        user_content: list[dict[str, Any]] = []
        if image_b64:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{image_mime};base64,{image_b64}"},
                }
            )
        user_content.append(
            {
                "type": "text",
                "text": f"从下面的设备运维工单/台账截图中抽取三元组：\n\n{text or '（见图片）'}",
            }
        )
        messages.append({"role": "user", "content": user_content})
        raw = self._complete(messages)
        return self._parse(raw)

    def _system_prompt(self) -> str:
        # Vendor 不进抽取提示词：工单不承载供应商（京东等购买渠道曾被误抽）
        node_types = json.dumps(
            {k: v["label"] for k, v in NODE_TYPES.items() if k != "Vendor"},
            ensure_ascii=False,
        )
        relation_types = json.dumps(
            {
                k: f'{v["label"]}（{v["subject"]} → {v["object"]}）'
                for k, v in RELATION_TYPES.items()
            },
            ensure_ascii=False,
        )
        return _SYSTEM_PROMPT.format(
            node_types=node_types, relation_types=relation_types
        )

    @staticmethod
    def _parse(raw: str) -> list[ExtractedTriple]:
        """容错解析：去掉 <think>、代码围栏，截取第一个 JSON 数组。"""
        cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
        m = re.search(r"\[.*\]", cleaned, flags=re.S)
        if not m:
            raise ValueError(f"LLM 未返回 JSON 数组：{raw[:200]}")
        items = json.loads(m.group(0))
        triples = []
        for it in items:
            try:
                triples.append(
                    ExtractedTriple(
                        subject_name=str(it["subject"]["name"]).strip(),
                        subject_type=it["subject"]["type"],
                        predicate=it["predicate"],
                        object_name=str(it["object"]["name"]).strip(),
                        object_type=it["object"]["type"],
                        attrs={str(k): str(v) for k, v in (it.get("attrs") or {}).items()},
                    )
                )
            except (KeyError, TypeError):
                continue  # 结构不完整的三元组直接丢弃
        return triples

    # ── 第二步：本体校验 + 实体链接 + 入图 ──────────────────

    def apply(self, store: GraphStore, triples: list[ExtractedTriple]) -> ExtractionReport:
        report = ExtractionReport(triples_raw=len(triples))
        id_of: dict[tuple[str, str], str] = {}  # (name, type) -> entity_id 缓存

        def link_or_create(name: str, etype: str) -> tuple[str | None, str | None]:
            """返回 (entity_id, None) 或 (None, 跳过原因)。"""
            key = (name, etype)
            if key in id_of:
                return id_of[key], None
            hits = store.find_by_name(name, entity_type=etype)
            if not hits and etype == "Room":
                # 口语同义词归一后再链一次（「13楼男洗手间」≈「13楼男卫生间」）
                normed = _normalize_room_name(name)
                if normed != name:
                    hits = store.find_by_name(normed, entity_type=etype)
            if hits:
                id_of[key] = hits[0]
                return hits[0], None
            # 同名但类型不同 → 也复用（人员被抽成 Person 最常见，防重复建人）
            loose = store.find_by_name(name)
            if loose:
                id_of[key] = loose[0]
                return loose[0], None
            if etype not in NODE_TYPES:
                return None, f"未知节点类型 {etype}"
            new_id = store.next_entity_id(etype)
            store.add_entity(new_id, etype, name, 来源="工单抽取")
            id_of[key] = new_id
            report.added_nodes.append(Entity(**store.entity(new_id)))
            return new_id, None

        for t in triples:
            # 硬规则：工单不承载供应商（京东等购买渠道不是台账供应商）——
            # 提示词约束的代码兜底，抽到即跳过
            if "Vendor" in (t.subject_type, t.object_type):
                report.skipped.append(
                    {"reason": "工单抽取不建供应商节点", "triple": t.model_dump_json()}
                )
                continue
            # 关系本体校验
            rel_def = RELATION_TYPES.get(t.predicate)
            if rel_def is None:
                report.skipped.append(
                    {"reason": f"未知关系 {t.predicate}", "triple": t.model_dump_json()}
                )
                continue
            if t.subject_type not in rel_def["subject"].split("|"):
                report.skipped.append(
                    {"reason": f"{t.predicate} 的主体应为 {rel_def['subject']}，"
                               f"收到 {t.subject_type}", "triple": t.model_dump_json()}
                )
                continue
            if t.object_type not in rel_def["object"].split("|"):
                report.skipped.append(
                    {"reason": f"{t.predicate} 的客体应为 {rel_def['object']}，"
                               f"收到 {t.object_type}", "triple": t.model_dump_json()}
                )
                continue

            src, err = link_or_create(t.subject_name, t.subject_type)
            if err:
                report.skipped.append({"reason": err, "triple": t.model_dump_json()})
                continue
            dst, err = link_or_create(t.object_name, t.object_type)
            if err:
                report.skipped.append({"reason": err, "triple": t.model_dump_json()})
                continue
            if src == dst:
                report.skipped.append(
                    {"reason": "两端为同一实体", "triple": t.model_dump_json()}
                )
                continue

            # MERGE：已有同向同类型边就不重复加
            if not store.has_relation(src, dst, t.predicate):
                store.add_relation(src, dst, t.predicate, source="工单抽取")
                report.added_edges.append(
                    {
                        "from": src,
                        "to": dst,
                        "relation": t.predicate,
                        "label": rel_def["label"],
                    }
                )
            # 附加属性合并到 subject（不覆盖已有值）
            if t.attrs:
                d = store._g.nodes[src]  # noqa: SLF001 图生长是 store 的正当协作者
                for k, v in t.attrs.items():
                    d["attrs"].setdefault(k, v)

        report.grown = bool(report.added_nodes or report.added_edges)
        if report.grown:
            store.save()
        return report
