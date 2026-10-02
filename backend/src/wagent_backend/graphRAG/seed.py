"""种子数据 —— 唯一数据来源：用户提供的「设备信息登记表」截图（2026-08-20）。

⚠️ 示例值声明：截图上以下字段被打码/未填写，本文件用示例值填充，
   仅用于演示图谱结构：设备编号、主要参数、品牌、规格型号、人名、
   供应商名称、日期、使用周期、巡检结果、价值。
   截图可读的值（设备名称、A座、AB1F、气体灭火气瓶间、工程部、在用）
   原样录入。

移交人登记为"/"（未登记）→ 不建 handed_over_by 边，忠于原图。
"""

from __future__ import annotations

from wagent_backend.graphRAG.store import GraphStore

# 实体 ID（图内主键，稳定可引用）
DEV = "DEV-HFC227-001"      # 七氟丙烷驱动气瓶
PRJ = "PRJ-001"             # 项目部
BLD = "BLD-A"               # A座
FLR = "FLR-A-B1"            # AB1F
ROOM = "RM-A-B1-01"         # 气体灭火气瓶间
DEPT = "DEPT-ENG"           # 工程部
VENDOR = "VND-001"          # 供应商
P_RESP = "P-RESP-01"        # 责任人
P_RECV = "P-RECV-01"        # 接收人
P_MGR = "P-MGR-01"          # 管理责任人


# ── 公共设施层：与 ops 台账（ops/data/seed.py facility_rows）同源同步 ──
# 为保持 graphRAG 与 ops 两包隔离，此处有意复制楼层/设备型号常量；
# 设备 entity_id 直接采用 ops asset_id（图谱节点可直达 /asset/{id} 维修页）。
_FACILITY_FLOORS = (("A", range(1, 31)), ("B", range(1, 7)))
_FACILITY_TYPES = [  # (ID前缀, 名称, asset_type, 品牌, 型号)
    ("FAU", "水龙头", "FAUCET", "九牧", "LT-2010"),
    ("FLV", "冲洗阀", "FLV", "箭牌", "CF-3301"),
    ("DRN", "地漏", "DRAIN", "潜水艇", "DL-50"),
    ("DRY", "干手器", "DRYER", "松下", "FJ-T09"),
    ("EXF", "排风扇", "EXFAN", "正野", "APB-25"),
]
_FACILITY_TYPE_CATEGORY = {"FAUCET": "PLUMB", "FLV": "PLUMB", "DRAIN": "PLUMB",
                           "DRYER": "ELEC", "EXFAN": "HVAC", "DSP": "PLUMB",
                           "URINAL": "PLUMB", "TOILET": "PLUMB"}
# 卫生间洁具配置：男卫 3 小便池 + 3 马桶；女卫 3 马桶（与 ops facility_rows 同源）
_FIXTURE_SPECS = [  # (room_tag, ID前缀, 名称, asset_type_id, 型号, 品牌, 数量)
    ("M", "URI", "小便池", "URINAL", "U-750", "箭牌", 3),
    ("M", "TOI", "马桶", "TOILET", "C-1100", "恒洁", 3),
    ("F", "TOI", "马桶", "TOILET", "C-1100", "恒洁", 3),
]
# 供应商为仿真数据（打标示意，非真实公司）
_FACILITY_VENDORS = {
    "PLUMB": ("VND-SIM-PLUMB", "恒洁卫浴维保（仿真）"),
    "ELEC": ("VND-SIM-ELEC", "迅捷机电服务（仿真）"),
    "HVAC": ("VND-SIM-HVAC", "正野环境科技（仿真）"),
}
_FAC_SRC = {"source": "台账同步"}


def build_facility_subgraph(kg: GraphStore) -> None:
    """公共设施层：楼层/卫生间/电梯厅 Room（attrs.space_id 桥接 ops）+ 设备节点。

    人员沿用现有责任人（P-RESP-01）与工程部（DEPT-ENG）；供应商为仿真生成。
    幂等：已有节点跳过（供种子构建与运行库增量补图共用）。
    """
    if not kg.has_entity("BLD-B"):
        kg.add_entity("BLD-B", "Building", "B座", aliases=["B栋", "B塔"])
    if not kg.has_relation("BLD-B", PRJ, "part_of"):
        kg.add_relation("BLD-B", PRJ, "part_of", **_FAC_SRC)
    for _vid, vname in _FACILITY_VENDORS.values():
        if not kg.has_entity(_vid):
            kg.add_entity(_vid, "Vendor", vname)

    for bld, floors in _FACILITY_FLOORS:
        bld_id = f"BLD-{bld}"
        for f in floors:
            flr = f"FLR-{bld}-{f:02d}"
            if not kg.has_entity(flr):
                kg.add_entity(flr, "Floor", f"{bld}栋{f}F",
                            aliases=[f"{bld}栋{f}层", f"{bld}座{f}楼"])
                kg.add_relation(flr, bld_id, "part_of", **_FAC_SRC)
            for wc, wc_name in (("WCM", "男洗手间"), ("WCF", "女洗手间"), ("EH", "电梯厅")):
                sp = f"SP-{bld}-{f:02d}-{wc}"
                room = f"RM-{bld}-{f:02d}-{wc}"
                if not kg.has_entity(room):
                    # 规范名统一用「洗手间」；别名收全口语说法（卫生间/厕所/有无性别前缀），
                    # 工单抽取与图谱搜索按名称/别名链接，缺别名会抽出游离 EXT-* 重复节点
                    aliases = [f"{f}楼{wc_name}"]
                    if wc != "EH":
                        g = wc_name[0]   # 男 / 女
                        aliases += [f"{f}楼{g}卫生间", f"{f}楼{g}厕所",
                                    f"{f}楼洗手间", f"{f}楼卫生间", f"{f}楼厕所"]
                    kg.add_entity(room, "Room", f"{bld}栋{f}层{wc_name}",
                                  aliases=aliases,
                                  空间类型=wc_name, space_id=sp)
                    kg.add_relation(room, flr, "part_of", **_FAC_SRC)
            for wc, tag, wc_name in (("WCM", "M", "男洗手间"), ("WCF", "F", "女洗手间")):
                room = f"RM-{bld}-{f:02d}-{wc}"
                for code, name, tid, brand, model in _FACILITY_TYPES:
                    dev = f"{code}-{bld}{f:02d}-{tag}"
                    if kg.has_entity(dev):
                        continue
                    kg.add_entity(dev, "Device", f"{f}层{wc_name}{name}",
                                品牌=brand, 规格型号=model, 设备类型=name)
                    kg.add_relation(dev, room, "located_in", **_FAC_SRC)
                    kg.add_relation(dev, P_RESP, "has_responsible_person", **_FAC_SRC)
                    kg.add_relation(dev, DEPT, "managed_by_dept", **_FAC_SRC)
                    kg.add_relation(dev, _FACILITY_VENDORS[_FACILITY_TYPE_CATEGORY[tid]][0],
                                    "supplied_by", **_FAC_SRC)
                # 洁具：男卫 3 小便池 + 3 马桶；女卫 3 马桶
                for ftag, code, name, tid, model, brand, n in _FIXTURE_SPECS:
                    if ftag != tag:
                        continue
                    for i in range(1, n + 1):
                        dev = f"{code}-{bld}{f:02d}-{tag}{i}"
                        if kg.has_entity(dev):
                            continue
                        kg.add_entity(dev, "Device", f"{f}层{wc_name}{name}{i}号",
                                    品牌=brand, 规格型号=model, 设备类型=name)
                        kg.add_relation(dev, room, "located_in", **_FAC_SRC)
                        kg.add_relation(dev, P_RESP, "has_responsible_person", **_FAC_SRC)
                        kg.add_relation(dev, DEPT, "managed_by_dept", **_FAC_SRC)
                        kg.add_relation(dev, _FACILITY_VENDORS[_FACILITY_TYPE_CATEGORY[tid]][0],
                                        "supplied_by", **_FAC_SRC)
            eh_room = f"RM-{bld}-{f:02d}-EH"
            dsp = f"DSP-{bld}{f:02d}-EH"
            if not kg.has_entity(dsp):
                kg.add_entity(dsp, "Device", f"{f}层电梯厅饮水机",
                            品牌="沁园", 规格型号="RO-400", 设备类型="饮水机")
                kg.add_relation(dsp, eh_room, "located_in", **_FAC_SRC)
                kg.add_relation(dsp, P_RESP, "has_responsible_person", **_FAC_SRC)
                kg.add_relation(dsp, DEPT, "managed_by_dept", **_FAC_SRC)
                kg.add_relation(dsp, _FACILITY_VENDORS["PLUMB"][0], "supplied_by", **_FAC_SRC)

# ── 演示故事线子图：四条主线（A25东/A1913/A1106/A1608）的空间与设备 ──
# 与 ops 台账（ops/data/seed.py 故事空间/故事设备段）同源同步：
# Room attrs 带 space_id（图谱 ↔ 工单互查的桥接键），
# Device entity_id 直接采用 ops asset_id（节点详情可直达 /asset/{id} 设备 360）。
_STORY_ROOMS = [  # (room_id, space_id, 名称, 楼层, 空间类型, aliases)
    ("RM-A-25-E", "SP-A-25-E", "A座25楼东侧片区", 25, "房源",
     ["A25东", "25楼东侧", "A座25楼东侧", "A-25F东", "25楼东侧会议室"]),
    ("RM-A-25-01", "SP-A-25-01", "A座25层空调设备房", 25, "设备房",
     ["A25设备房", "25楼空调机房"]),
    ("RM-A-19-1913", "SP-A-19-1913", "A座19层1913室", 19, "房源",
     ["A1913", "A-1913", "1913"]),
    ("RM-A-11-1106", "SP-A-11-1106", "A座11层1106室", 11, "房源",
     ["A1106", "A-1106", "1106", "1106瑜伽馆"]),
    ("RM-A-16-1608", "SP-A-16-1608", "A座16层1608室", 16, "房源",
     ["A1608", "A-1608", "1608"]),
]
_STORY_DEVICES = [  # (asset_id, 名称, 设备类型, 品牌, 型号, 设备编号, room_id, 供应商类别)
    ("FCU-A25-01", "25楼东侧风机盘管", "风机盘管", "约克", "LD3663EH",
     "SB-FCU-0221", "RM-A-25-E", "HVAC"),
    ("AHU-A-25", "25楼组合式空调机组", "组合式空调机组", "天加", "ZK-12",
     "SB-AHU-0007", "RM-A-25-01", "HVAC"),
    ("SD-A25-01", "25楼东侧感烟探测器", "感烟探测器", "海湾", "JTY-GD",
     "SB-SD-2531", "RM-A-25-E", "FIRE"),
    ("FCU-A19-13", "1913室风机盘管", "风机盘管", "约克", "FP-102",
     "SB-FCU-1103", "RM-A-19-1913", "HVAC"),
    ("FCU-A11-06", "1106室风机盘管", "风机盘管", "约克", "LD2363EH",
     "SB-FCU-0482", "RM-A-11-1106", "HVAC"),
    ("FCU-A16-08", "1608室风机盘管", "风机盘管", "约克", "LD2363EH",
     "SB-FCU-0509", "RM-A-16-1608", "HVAC"),
]
_STORY_VENDORS = {
    "HVAC": ("VND-SIM-HVAC", "正野环境科技（仿真）"),
    "FIRE": ("VND-SIM-FIRE", "海湾消防技术服务（仿真）"),
}


def build_storyline_subgraph(kg: GraphStore) -> None:
    """演示故事线子图：四条演示主线的房源空间 + 空调/消防设备。

    人员/部门沿用现有责任人（P-RESP-01）与工程部（DEPT-ENG），同公共设施层约定。
    幂等：已有节点跳过（供种子构建与运行库增量补图共用）。
    """
    for _vid, vname in _STORY_VENDORS.values():
        if not kg.has_entity(_vid):
            kg.add_entity(_vid, "Vendor", vname)

    for room_id, sp, name, floor, rtype, aliases in _STORY_ROOMS:
        flr = f"FLR-A-{floor:02d}"
        if not kg.has_entity(flr):
            kg.add_entity(flr, "Floor", f"A栋{floor}F",
                          aliases=[f"A栋{floor}层", f"A座{floor}楼"])
            kg.add_relation(flr, BLD, "part_of", **_FAC_SRC)
        if kg.has_entity(room_id):
            continue
        kg.add_entity(room_id, "Room", name, aliases=aliases,
                      空间类型=rtype, space_id=sp)
        kg.add_relation(room_id, flr, "part_of", **_FAC_SRC)

    for dev, name, dtype, brand, model, dev_no, room, vend in _STORY_DEVICES:
        if kg.has_entity(dev):
            continue
        kg.add_entity(dev, "Device", name,
                      品牌=brand, 规格型号=model, 设备类型=dtype, 设备编号=dev_no)
        kg.add_relation(dev, room, "located_in", **_FAC_SRC)
        kg.add_relation(dev, P_RESP, "has_responsible_person", **_FAC_SRC)
        kg.add_relation(dev, DEPT, "managed_by_dept", **_FAC_SRC)
        kg.add_relation(dev, _STORY_VENDORS[vend][0], "supplied_by", **_FAC_SRC)


# 边的溯源属性
_SRC = {"source": "设备信息登记表"}


def build_seed_graph() -> GraphStore:
    kg = GraphStore()

    # ── 空间层级：项目部 → A座 → AB1F → 气体灭火气瓶间 ──
    kg.add_entity(
        PRJ, "Project", "示范广场项目部",
        aliases=["示范广场", "项目部"],
    )
    kg.add_entity(
        BLD, "Building", "A座",
        aliases=["A栋", "A塔"],
    )
    kg.add_entity(
        FLR, "Floor", "AB1F",
        aliases=["A座B1层", "A座负一层", "负一层"],
    )
    kg.add_entity(
        ROOM, "Room", "气体灭火气瓶间",
        aliases=["气瓶间", "消防气瓶间"],
        空间类型="设备用房",
    )

    # ── 设备：七氟丙烷驱动气瓶（登记表主记录）──
    kg.add_entity(
        DEV, "Device", "七氟丙烷驱动气瓶",
        aliases=["驱动气瓶", "七氟丙烷气瓶", "HFC-227ea 驱动气瓶"],
        设备编号="XF-A-B1-0158（示例）",
        主要参数="容积 7L / 充装压力 4.2MPa / 介质 七氟丙烷（示例）",
        品牌="安盾（示例）",
        规格型号="QYP7-4.2（示例）",
        生产日期="2021-06-15（示例）",
        投入使用日期="2021-09-01（示例）",
        使用周期="10 年（示例）",
        巡检结果="正常（示例）",
        原价值="4500（示例）",
        现估价值="3200（示例）",
        使用状态="在用",
    )

    # ── 组织与人员 ──
    kg.add_entity(DEPT, "Department", "工程部", aliases=["工程管理部"])
    kg.add_entity(
        VENDOR, "Vendor", "华消消防设备有限公司",
        aliases=["华消消防"],
    )
    kg.add_entity(P_RESP, "Person", "王建国", aliases=["王工"], 角色="责任人（示例）")
    kg.add_entity(P_RECV, "Person", "李明", aliases=[], 角色="接收人（示例）")
    kg.add_entity(P_MGR, "Person", "赵芳", aliases=[], 角色="管理责任人（示例）")

    # ── 关系 ──
    # 空间层级
    kg.add_relation(ROOM, FLR, "part_of", **_SRC)
    kg.add_relation(FLR, BLD, "part_of", **_SRC)
    kg.add_relation(BLD, PRJ, "part_of", **_SRC)
    # 设备 → 空间/组织/人员/供应商
    kg.add_relation(DEV, ROOM, "located_in", **_SRC)
    kg.add_relation(DEV, DEPT, "managed_by_dept", **_SRC)
    kg.add_relation(DEV, VENDOR, "supplied_by", **_SRC)
    kg.add_relation(DEV, P_RESP, "has_responsible_person", **_SRC)
    kg.add_relation(DEV, P_RECV, "received_by", **_SRC)
    kg.add_relation(DEV, P_MGR, "has_manage_person", **_SRC)
    # handed_over_by：登记表移交人为"/"，未建边

    # 公共设施层（全楼层卫生间/电梯厅 + 设备，与 ops 台账同源）
    build_facility_subgraph(kg)
    # 演示故事线子图（A25东/A1913/A1106/A1608 空间与设备，与 ops 台账同源）
    build_storyline_subgraph(kg)

    return kg
