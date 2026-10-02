"""知识图谱本体定义 —— 节点类型、关系类型、通用返回模型。

来源：2026-08-20 用户提供的「设备信息登记表」截图（七氟丙烷驱动气瓶）。
登记表的每个关联字段对应图中一条边；设备属性字段落在 Device 节点上。

依赖方向（解耦约定）：
    graphRAG 不 import web / tools / llm，只被它们依赖。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════
# 节点类型（8 类）
# ═══════════════════════════════════════════════════════════════

NODE_TYPES: dict[str, dict[str, str]] = {
    "Device": {
        "label": "设备",
        "source": "设备名称 / 设备编号",
        "desc": "台账登记的设备本体，属性最全：编号、参数、品牌、规格、日期、价值、状态",
    },
    "Person": {
        "label": "人员",
        "source": "责任人 / 接收人 / 移交人 / 管理责任人",
        "desc": "自然人，通过不同关系类型区分其在设备生命周期中的角色",
    },
    "Department": {
        "label": "部门",
        "source": "责任部门（如 工程部）",
        "desc": "楼宇内部组织",
    },
    "Vendor": {
        "label": "供应商",
        "source": "供应商名称",
        "desc": "设备供货/维保的外部单位",
    },
    "Project": {
        "label": "项目",
        "source": "关联项目部",
        "desc": "空间层级根节点",
    },
    "Building": {
        "label": "楼栋",
        "source": "关联楼栋（如 A座）",
        "desc": "项目下的物理楼栋",
    },
    "Floor": {
        "label": "楼层",
        "source": "关联楼层（如 AB1F）",
        "desc": "楼栋内的楼层",
    },
    "Room": {
        "label": "空间",
        "source": "关联空间/房源（如 气体灭火气瓶间）",
        "desc": "楼层内的房间/功能区，设备的直接安装位置",
    },
}


# ═══════════════════════════════════════════════════════════════
# 关系类型（8 种）
# ═══════════════════════════════════════════════════════════════

RELATION_TYPES: dict[str, dict[str, str]] = {
    "located_in": {
        "label": "位于",
        "subject": "Device",
        "object": "Room",
        "source": "关联空间/房源",
        "desc": "设备装在哪。⚠️ 只表达安装位置，不表达服务范围",
    },
    "part_of": {
        "label": "属于",
        "subject": "Room|Floor|Building",
        "object": "Floor|Building|Project",
        "source": "关联楼层/楼栋/项目部",
        "desc": "空间层级：Room→Floor→Building→Project",
    },
    "supplied_by": {
        "label": "供应商",
        "subject": "Device",
        "object": "Vendor",
        "source": "供应商名称",
        "desc": "供货关系",
    },
    "managed_by_dept": {
        "label": "责任部门",
        "subject": "Device",
        "object": "Department",
        "source": "责任部门",
        "desc": "设备由哪个部门负责",
    },
    "has_responsible_person": {
        "label": "责任人",
        "subject": "Device",
        "object": "Person",
        "source": "责任人",
        "desc": "设备责任人",
    },
    "received_by": {
        "label": "接收人",
        "subject": "Device",
        "object": "Person",
        "source": "接收人姓名",
        "desc": "设备接收移交时的接收方",
    },
    "handed_over_by": {
        "label": "移交人",
        "subject": "Device",
        "object": "Person",
        "source": "移交人姓名",
        "desc": "设备移交时的移交方（样例登记表为“/”，未建边）",
    },
    "has_manage_person": {
        "label": "管理责任人",
        "subject": "Device",
        "object": "Person",
        "source": "管理责任人",
        "desc": "日常管理责任人",
    },
}


class GraphIntegrityError(ValueError):
    """建图数据违反本体约束（未知类型 / 端点缺失 / 类型不符）。"""


# ═══════════════════════════════════════════════════════════════
# pydantic 模型 —— 图谱查询与抽取的通用结构
# ═══════════════════════════════════════════════════════════════


class Entity(BaseModel):
    """图中一个实体的概要（搜索/邻居返回用），详情用 kg_get_entity。"""

    entity_id: str = Field(description="实体 ID，图内唯一")
    entity_type: str = Field(description="节点类型 key，见 kg_get_schema")
    type_label: str = Field(description="类型中文标签")
    name: str = Field(description="实体名称")
    aliases: list[str] = Field(default_factory=list, description="别名，搜索可命中")


class EntityDetail(Entity):
    """实体详情：登记表字段全部落在 attrs 里。"""

    attrs: dict[str, str] = Field(
        default_factory=dict,
        description="实体属性（登记表字段原样保留：设备编号/品牌/规格/日期/价值/状态等）",
    )


class RelationEdge(BaseModel):
    """一条有向边。direction 站在查询主体视角：

    - "out"：主体 —关系→ 对端（如 设备 —责任人→ 张三）
    - "in"：对端 —关系→ 主体（如 查 Room 的入边：设备 —位于→ 本房间）
    """

    relation: str = Field(description="关系类型 key，见 kg_get_schema")
    relation_label: str = Field(description="关系中文谓词")
    direction: Literal["out", "in"]
    other: Entity = Field(description="对端实体概要")


class PathHop(BaseModel):
    """路径中的一跳。"""

    relation: str
    relation_label: str
    from_id: str
    from_name: str
    to_id: str
    to_name: str
