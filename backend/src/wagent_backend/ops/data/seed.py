"""演示种子数据 —— L1/L2/L3 三层，围绕三条可演示的故事线：

故事 A（复发链 · 治标→治本）：A座25楼东侧 FCU-A25-01，60 天内 3 次不制冷。
    前两次处置分别是洗滤网、手动开阀（temporary_valve_override，治标），
    运行快照「阀位 0% 但流量 >0」是阀执行器损坏的机关。
    L3 已有一条 replay 归纳的洞察（INS-REPLAY-001）。
    → full 档 Agent 应 recall 命中 → 判复发 → 直接换阀（治本）。

故事 B（欠费锁机）：A1106 两次「开不了机」实为欠费停机。
    唯一可见通道是 AssetRuntime.lock_status=billing_locked。
    L3 洞察 INS-REPLAY-002 置信度 0.58（<0.6，低置信必须标记）。

故事 C（合同）：SP-A-25-E 有两条同时有效、结论冲突的责任条款
    （CL-004 业主 vs CL-005 租户）→ judge_liability 返回 unclear + 转人工。

空间结构：汇金广场单项目，A栋 30 层（地下 2 层）+ B栋 6 层；
每层 4 户房源 + 电梯厅 + 男女卫生间，公区/房源由 _l1 程序化生成，
故事空间（SP-A-25-E 等）作为各层额外空间手工维护。
电梯录为资产（ELV-A-01..06 / ELV-B-01..03），服务本栋各层电梯厅。

时间基准：BASE = 2026-08-23 09:00（固定值，保证种子确定性；
所有相对时间由此推算）。时间旅行约束：洞察 generated_at 晚于全部证据工单。

insight.embedding 由调用方注入的 embedder 现算（与运行时同一向量空间）。
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime, timedelta

from wagent_backend.ops.data.db import iso, jdump
from wagent_backend.ops.data.simdata import import_sim_seed

BASE = datetime(2026, 8, 23, 9, 0, 0)

EmbedFn = Callable[[str], list[float]]

# 设施经理（冻结 DDL 无专表 —— 工具说明 §14.5 的演示种子配置）
FACILITY_MANAGERS: dict[str, str] = {"FM-001": "吴敏（设施经理）", "FM-002": "郑凯（值班主管）"}


def days_ago(n: int, hour: int = 10, minute: int = 0) -> str:
    return iso(BASE - timedelta(days=n, hours=BASE.hour - hour, minutes=BASE.minute - minute))


def seed(conn: sqlite3.Connection, embedder: EmbedFn) -> None:
    """灌入全套演示数据（假定空库；reset 流程会先删库重建）。"""
    _l1(conn)
    _l2(conn)
    _l3(conn, embedder)
    import_sim_seed(conn, embedder)   # 仿真测试数据（WAGENT_OPS_SIMSEED=0 可关）
    conn.commit()


# ── 公共设施层（客户可感知设备，报修语言的真实载体）──────────────

# (ID前缀, 名称, asset_type_id, 品牌, 型号, 设计寿命)
FACILITY_TYPES = [
    ("FAU", "水龙头", "FAUCET", "九牧", "LT-2010", 8),
    ("FLV", "冲洗阀", "FLV", "箭牌", "CF-3301", 10),
    ("DRN", "地漏", "DRAIN", "潜水艇", "DL-50", 15),
    ("DRY", "干手器", "DRYER", "松下", "FJ-T09", 8),
    ("EXF", "排风扇", "EXFAN", "正野", "APB-25", 10),
]
# 铺设楼层：A/B 全楼层（A 栋 1–30 层、B 栋 1–6 层；地下层无卫生间/电梯厅不铺）
FACILITY_FLOORS = (("A", range(1, 31)), ("B", range(1, 7)))

# asset_type 补充行（FAUCET 在专业样板区已单独登记）
FACILITY_ASSET_TYPES = [
    ("FLV", "冲洗阀", "PLUMB"),
    ("DRAIN", "地漏", "PLUMB"),
    ("DSP", "饮水机", "PLUMB"),
    ("DRYER", "干手器", "ELEC"),
    ("EXFAN", "排风扇", "HVAC"),
    ("URINAL", "小便池", "PLUMB"),
    ("TOILET", "马桶", "PLUMB"),
]

# 卫生间洁具配置：男卫 3 小便池 + 3 马桶；女卫 3 马桶
_FIXTURE_SPECS = [  # (room_tag, ID前缀, 名称, asset_type_id, 数量)
    ("M", "URI", "小便池", "URINAL", 3),
    ("M", "TOI", "马桶", "TOILET", 3),
    ("F", "TOI", "马桶", "TOILET", 3),
]


def facility_rows() -> tuple[list[tuple], list[tuple]]:
    """公共设施层种子（asset + space_served_by_asset 行）。

    每层男/女卫各 水龙头/冲洗阀/地漏/干手器/排风扇，电梯厅一台饮水机，
    设备即服务所挂空间（公区设施 located_in == served）。
    模块级独立函数：seed() 灌库与运行库增量补数据共用同一份。
    """
    assets: list[tuple] = []
    serves: list[tuple] = []

    def _add(asset_id, asset_no, name, tid, model, brand, bld, floor, sp, note):
        assets.append((asset_id, asset_no, name, tid, model, brand,
                       f"BLD-{bld}", floor, sp, None, "2019-09-01", None, 0,
                       None, None, None, "自管", "工程部", "陈国强", None,
                       "一般", "在用", note))
        serves.append((sp, asset_id, "primary", 1.00, "2016-01-01", None,
                       iso(BASE), "ledger"))

    for bld, floors in FACILITY_FLOORS:
        for f in floors:
            for wc, tag, wc_name in (("WCM", "M", "男卫"), ("WCF", "F", "女卫")):
                sp = f"SP-{bld}-{f:02d}-{wc}"
                for code, name, tid, brand, model, life in FACILITY_TYPES:
                    _add(f"{code}-{bld}{f:02d}-{tag}", f"SB-{code}-{bld}{f:02d}{tag}",
                         name, tid, model, brand, bld, f, sp,
                         f"{bld}栋{f}层{wc_name}{name}")
                # 洁具：男卫 3 小便池 + 3 马桶；女卫 3 马桶
                for ftag, code, name, tid, n in _FIXTURE_SPECS:
                    if ftag != tag:
                        continue
                    model, brand = (("U-750", "箭牌") if tid == "URINAL"
                                    else ("C-1100", "恒洁"))
                    for i in range(1, n + 1):
                        _add(f"{code}-{bld}{f:02d}-{tag}{i}",
                             f"SB-{code}-{bld}{f:02d}{tag}{i}",
                             name, tid, model, brand, bld, f, sp,
                             f"{bld}栋{f}层{wc_name}{name}{i}号")
            eh = f"SP-{bld}-{f:02d}-EH"
            _add(f"DSP-{bld}{f:02d}-EH", f"SB-DSP-{bld}{f:02d}", "饮水机", "DSP",
                 "RO-400", "沁园", bld, f, eh, f"{bld}栋{f}层电梯厅饮水机")
    return assets, serves


# ── L1 事实 ───────────────────────────────────────────────────

def _l1(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO property VALUES (?,?,?,?)", ("PRP-001", "汇金广场", "杭州", "甲级")
    )
    conn.executemany(
        "INSERT INTO building VALUES (?,?,?,?,?)",
        [
            ("BLD-A", "PRP-001", "A栋", 30, 2),
            ("BLD-B", "PRP-001", "B栋", 6, 0),
        ],
    )
    # 空间 = 程序化生成的公区/房源 + 手工维护的故事空间（演示剧情锚点）
    spaces: list[tuple] = []
    for bld, n_floors in (("A", 30), ("B", 6)):
        for f in range(1, n_floors + 1):
            for u in range(1, 5):   # 每层 4 户房源（房号 = 楼层+序号，同 1106 惯例）
                unit = f"{f * 100 + u:04d}"
                spaces.append((
                    f"SP-{bld}-{f:02d}-{unit}", f"BLD-{bld}", f, None, unit,
                    "房源", 80.0, None, jdump([f"{bld}{unit}", f"{bld}-{unit}"]),
                ))
            spaces.append((
                f"SP-{bld}-{f:02d}-EH", f"BLD-{bld}", f, None, None,
                "电梯厅", 40.0, None,
                jdump([f"{f}楼电梯厅", f"{bld}座{f}楼电梯厅", f"{bld}栋{f}楼电梯厅"]),
            ))
            for g in ("男", "女"):
                spaces.append((
                    f"SP-{bld}-{f:02d}-WC{'M' if g == '男' else 'F'}", f"BLD-{bld}",
                    f, g, None, "卫生间", 15.0, None,
                    jdump([f"{f}楼{g}卫生间", f"{f}楼{g}厕"]),
                ))
    # A栋地下：-1 停车场；-2 停车场 + 3 个设备间
    spaces += [
        ("SP-A-B1-P", "BLD-A", -1, None, None, "停车场", 2000.0, None,
         jdump(["负一层停车场", "B1停车场"])),
        ("SP-A-B2-P", "BLD-A", -2, None, None, "停车场", 2000.0, None,
         jdump(["负二层停车场", "B2停车场"])),
        *[(f"SP-A-B2-{i:02d}", "BLD-A", -2, None, None, "设备间", 60.0, None,
           jdump([f"负二层设备间{i}"])) for i in range(1, 4)],
    ]
    # 故事空间（剧情锚点；原 B 栋迁至 A 栋，楼层不变）——与每层 01–04 户不冲突
    spaces += [
        # space_id, building, floor, zone, unit_no, type, area, merged_from, aliases
        ("SP-A-25-E", "BLD-A", 25, "东侧", None, "房源", 320.0, None,
         jdump(["A25东", "25楼东侧", "A座25楼东侧", "A-25F东"])),
        ("SP-A-25-01", "BLD-A", 25, None, "2501", "设备房", 45.0, None,
         jdump(["A25设备房", "25楼空调机房"])),
        ("SP-A-19-1913", "BLD-A", 19, None, "1913", "房源", 186.0, None,
         jdump(["A1913", "A-1913", "1913"])),
        ("SP-A-11-1106", "BLD-A", 11, None, "1106", "房源", 120.0,
         jdump(["SP-A-11-1105", "SP-A-11-1107"]), jdump(["A1106", "A-1106"])),
        ("SP-A-16-1608", "BLD-A", 16, None, "1608", "房源", 98.0, None,
         jdump(["A1608", "A-1608"])),
    ]
    conn.executemany("INSERT INTO space VALUES (?,?,?,?,?,?,?,?,?)", spaces)
    conn.executemany(
        "INSERT INTO asset_type VALUES (?,?,?)",
        [
            ("FCU", "风机盘管", "HVAC"),
            ("AHU", "组合式空调机组", "HVAC"),
            ("PUMP", "冷冻水泵", "PLUMB"),
            ("FAUCET", "水龙头", "PLUMB"),
            ("SMOKE", "感烟探测器", "FIRE"),
            ("ELEV", "乘客电梯", "VERT"),
            *FACILITY_ASSET_TYPES,
        ],
    )
    assets = [
        # 15 字段对齐真实台账（冻结 DDL 注释）
        # （AHU 先插 —— FCU-A25-01 的 parent_asset_id 指向它，FK 立即校验）
        ("AHU-A-25", "SB-AHU-0007", "组合式空调机组", "AHU", "ZK-12", "天加",
         "BLD-A", 25, "SP-A-25-01", None,
         "2016-06-30", 15, 0, "2026-06-30", "天加空调系统有限公司", None, "外包",
         "工程部", "陈国强", None, "重要", "在用", "服务25楼东侧的新风+冷量"),
        ("FCU-A25-01", "SB-FCU-0221", "风机盘管", "FCU", "LD3663EH", "约克",
         "BLD-A", 25, "SP-A-25-E", "AHU-A-25",
         "2016-12-28", 10, 1, "2019-12-28", "约克商用空调服务", None, "自管",
         "工程部", "陈国强", None, "一般", "在用", "A座25楼东侧片区末端"),
        ("FCU-A19-13", "SB-FCU-1103", "风机盘管", "FCU", "FP-102", "约克",
         "BLD-A", 19, "SP-A-19-1913", None,
         "2019-03-15", 10, 0, None, None, None, "自管",
         "工程部", "陈国强", None, "一般", "在用", None),
        ("FCU-A11-06", "SB-FCU-0482", "风机盘管", "FCU", "LD2363EH", "约克",
         "BLD-A", 11, "SP-A-11-1106", None,
         "2018-05-20", 10, 0, None, None, None, "自管",
         "工程部", "陈国强", None, "一般", "在用", None),
        ("FCU-A16-08", "SB-FCU-0509", "风机盘管", "FCU", "LD2363EH", "约克",
         "BLD-A", 16, "SP-A-16-1608", None,
         "2018-05-20", 10, 0, None, None, None, "自管",
         "工程部", "陈国强", None, "一般", "在用", None),
        ("SD-A25-01", "SB-SD-2531", "感烟探测器", "SMOKE", "JTY-GD", "海湾",
         "BLD-A", 25, "SP-A-25-E", None,
         None, None, 0, None, None, None, "自管",
         "安保部", "王强", None, "重要", "在用", None),
        # 13楼男卫生间洗手盆龙头（对应图谱 EXT-DEV-001，漏水报修的设备载体）
        ("FAUCET-A13-01", "SB-FCT-1301", "水龙头", "FAUCET", "LT-2010", "九牧",
         "BLD-A", 13, "SP-A-13-WCM", None,
         "2019-09-01", 8, 0, None, None, None, "自管",
         "工程部", "陈国强", None, "一般", "在用", "13楼男卫生间洗手盆龙头"),
    ]
    # 电梯：A栋 6 部 / B栋 3 部，挂在 1 楼电梯厅，服务关系见 space_served_by_asset
    assets += [
        (f"ELV-{bld}-{i:02d}", f"SB-ELV-{bld}{i:02d}", "乘客电梯", "ELEV",
         "GPS-III", "三菱", f"BLD-{bld}", 1, f"SP-{bld}-01-EH", None,
         commissioned, 15, 0, None, None, None, "外包",
         "工程部", "陈国强", None, "重要", "在用", f"{bld}栋{i}号梯")
        for bld, n, commissioned in (("A", 6, "2016-06-30"), ("B", 3, "2018-01-15"))
        for i in range(1, n + 1)
    ]
    conn.executemany("INSERT INTO asset VALUES (" + ",".join(["?"] * 23) + ")", assets)
    fac_assets, fac_serves = facility_rows()
    conn.executemany("INSERT INTO asset VALUES (" + ",".join(["?"] * 23) + ")", fac_assets)
    vf = "2016-01-01"
    rec = iso(BASE)
    serves = [
        # ⚠️ AHU 装在设备房(2501)但服务 25 楼东侧 —— located_in ≠ served
        ("SP-A-25-E", "FCU-A25-01", "primary", 0.60, vf, None, rec, "ledger"),
        ("SP-A-25-E", "AHU-A-25", "partial", 0.40, vf, None, rec, "drawing"),
        ("SP-A-25-E", "SD-A25-01", "partial", 1.00, vf, None, rec, "ledger"),
        ("SP-A-19-1913", "FCU-A19-13", "primary", 1.00, vf, None, rec, "ledger"),
        ("SP-A-11-1106", "FCU-A11-06", "primary", 1.00, vf, None, rec, "ledger"),
        ("SP-A-16-1608", "FCU-A16-08", "primary", 1.00, vf, None, rec, "ledger"),
        ("SP-A-13-WCM", "FAUCET-A13-01", "primary", 1.00, vf, None, rec, "ledger"),
    ]
    # 每部电梯服务本栋各层电梯厅
    for bld, n_elv, n_floors in (("A", 6, 30), ("B", 3, 6)):
        for i in range(1, n_elv + 1):
            for f in range(1, n_floors + 1):
                serves.append((f"SP-{bld}-{f:02d}-EH", f"ELV-{bld}-{i:02d}",
                               "primary", round(1 / n_elv, 2), vf, None, rec, "ledger"))
    conn.executemany(
        "INSERT INTO space_served_by_asset VALUES (?,?,?,?,?,?,?,?)", serves,
    )
    conn.executemany(
        "INSERT INTO space_served_by_asset VALUES (?,?,?,?,?,?,?,?)", fac_serves,
    )
    conn.executemany(
        "INSERT INTO asset_runtime VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            # ★ 机关 1：阀位反馈 0% 但冷冻水流量 12.4 → 阀执行器坏（故事 A）
            ("FCU-A25-01", days_ago(0, 8, 30), 24.6, 27.2, 22.0, 0.0, 12.4, "mid", 9.2, "normal"),
            ("AHU-A-25", days_ago(0, 8, 30), 12.1, 17.5, 12.0, 68.0, 210.0, "high", 20.5, "normal"),
            # ★ 机关 2：lock_status=billing_locked —— 欠费停机唯一可见通道（故事 B）
            ("FCU-A11-06", days_ago(0, 8, 30), 26.8, 27.4, 22.0, 0.0, 0.0, "off", 0.0, "billing_locked"),
            ("FCU-A19-13", days_ago(0, 8, 30), 19.8, 23.1, 20.0, 45.0, 8.2, "mid", 7.8, "normal"),
            ("FCU-A16-08", days_ago(0, 8, 30), 20.2, 23.6, 22.0, 52.0, 9.0, "mid", 8.1, "normal"),
        ],
    )
    conn.executemany(
        "INSERT INTO tenant VALUES (?,?,?)",
        [
            ("TEN-001", "华宸律师事务所", "法律"),
            ("TEN-002", "启润贸易", "贸易"),
            ("TEN-003", "静修瑜伽馆", "教育培训"),
        ],
    )
    conn.executemany(
        "INSERT INTO contact VALUES (?,?,?,?,?)",
        [
            ("C-001", "TEN-001", "张女士", "行政", "wecom"),
            ("C-002", "TEN-002", "王先生", "前台", "wecom"),
            ("C-003", "TEN-003", "李老师", "店长", "sms"),
        ],
    )
    conn.executemany(
        "INSERT INTO tenant_occupies_space VALUES (?,?,?,?,?)",
        [
            ("TEN-002", "SP-A-25-E", "2024-06-01", None, rec),
            ("TEN-001", "SP-A-19-1913", "2023-01-15", None, rec),
            ("TEN-003", "SP-A-11-1106", "2025-04-01", None, rec),
        ],
    )
    # 产权人 ≠ 使用人 ≠ 缴费人（SP-A-19-1913）
    conn.executemany(
        "INSERT INTO space_party VALUES (?,?,?,?,?)",
        [
            ("SP-A-19-1913", "owner", "汇金置业", "2020-01-01", None),
            ("SP-A-19-1913", "occupier", "华宸律师事务所", "2023-01-15", None),
            ("SP-A-19-1913", "payer", "华宸律师事务所", "2023-01-15", None),
        ],
    )
    conn.executemany(
        "INSERT INTO contract_clause VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            ("CL-001", "SP-A-19-1913", "hvac_maintenance",
             "租赁期内中央空调主机及末端设备的维修、更换费用由出租方承担。",
             "owner", jdump(["compressor_fault", "chilled_water_supply", "duct_damage",
                             "pipe_insulation_failure"]), 2, "2025-01-01", None, rec),
            ("CL-002", "SP-A-19-1913", "filter_cleaning",
             "风机盘管过滤网清洗由承租方负责，每季度不少于一次。",
             "tenant", jdump(["filter_clogged"]), 1, "2023-02-01", None, rec),
            ("CL-003", "SP-A-11-1106", "renovation",
             "承租方自行装修、改造（含风管/电路改动）引起的问题及修复费用由承租方承担。",
             "tenant", jdump(["tenant_modification"]), 1, "2025-04-01", None, rec),
            # 故事 C：同一空间两条同时有效、结论冲突的条款
            ("CL-004", "SP-A-25-E", "hvac_maintenance",
             "公共区域及末端空调设备的维修费用由业主方承担。",
             "owner", jdump(["valve_actuator_failure", "compressor_fault",
                             "fan_motor_fault"]), 1, "2025-01-01", None, rec),
            ("CL-005", "SP-A-25-E", "hvac_maintenance",
             "入驻单位区域内空调末端（含电动阀）日常维护由入驻单位负责。",
             "tenant", jdump(["valve_actuator_failure"]), 1, "2025-06-01", None, rec),
        ],
    )
    conn.executemany(
        "INSERT INTO technician VALUES (?,?,?,?,?,?)",
        [
            ("TEC-001", "陈国强", jdump(["HVAC"]), jdump(["制冷设备维修工"]), "BLD-B", "day"),
            ("TEC-002", "刘志明", jdump(["HVAC"]), jdump([]), "BLD-B", "night"),
            ("TEC-003", "赵永刚", jdump(["ELEC"]), jdump(["高压电工证"]), "BLD-A", "day"),
            ("TEC-004", "孙水旺", jdump(["PLUMB"]), jdump([]), "BLD-B", "day"),
            ("TEC-005", "周敏", jdump(["HVAC", "ELEC"]), jdump([]), "BLD-A", "day"),
            # 2026-08-27 三班组制：环境（保洁）与秩序（安保）班组人员
            ("TEC-006", "马秀兰", jdump(["CLEAN"]), jdump([]), "BLD-B", "day"),
            ("TEC-007", "吴桂芳", jdump(["CLEAN"]), jdump([]), "BLD-A", "day"),
            ("TEC-008", "张建国", jdump(["SECURITY"]), jdump([]), "BLD-B", "day"),
            ("TEC-009", "何卫东", jdump(["SECURITY"]), jdump([]), "BLD-A", "night"),
        ],
    )


# ── L2 事件（append-only）─────────────────────────────────────

def _l2(conn: sqlite3.Connection) -> None:
    def wo(wo_id, created, space, asset, reporter, raw, symptom, urgency="一般"):
        conn.execute(
            "INSERT INTO work_order VALUES (?,?,?,?,?,?,?,?)",
            (wo_id, created, space, asset, reporter, raw, symptom, urgency),
        )

    def ev(wo_id, days, hour, **kw):
        conn.execute(
            "INSERT INTO work_order_event (wo_id,ts,event_type,technician_id,"
            "reported_cause,action_taken,liability,note,material_cost,labor_cost) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (wo_id, days_ago(days, hour), kw["type"], kw.get("tec"), kw.get("cause"),
             kw.get("action"), kw.get("liability"), kw.get("note"),
             kw.get("material"), kw.get("labor")),
        )

    # 故事 A：FCU-A25-01 复发链（3 单，前两单治标）
    wo("WO-B25-0624", days_ago(60, 10, 12), "SP-A-25-E", "FCU-A25-01", "C-002",
       "25楼东侧空调不制冷，风吹出来不怎么凉", "no_cooling")
    ev("WO-B25-0624", 60, 12, type="dispatched", tec="TEC-001")
    ev("WO-B25-0624", 60, 14, type="diagnosed", tec="TEC-001",
       cause="filter_clogged", action="clean_replace_filter",
       note="拆下过滤网清洗干净后装回，出风略有改善", labor=80)
    ev("WO-B25-0624", 60, 15, type="closed")

    wo("WO-B25-0720", days_ago(34, 9, 40), "SP-A-25-E", "FCU-A25-01", "C-002",
       "A座25楼东侧空调还是不冷，和上次一个毛病", "no_cooling")
    ev("WO-B25-0720", 34, 11, type="dispatched", tec="TEC-001")
    ev("WO-B25-0720", 34, 13, type="diagnosed", tec="TEC-001",
       cause="valve_actuator_failure", action="temporary_valve_override",
       note="空调电动阀阀坏，手动开启电动阀，恢复供冷。建议择期换阀", labor=120)
    ev("WO-B25-0720", 34, 14, type="closed")

    wo("WO-B25-0811", days_ago(12, 9, 5), "SP-A-25-E", "FCU-A25-01", "C-002",
       "25楼东侧空调又不制冷了，这已经是第三次报修了", "no_cooling", "紧急")
    ev("WO-B25-0811", 12, 10, type="dispatched", tec="TEC-002")
    ev("WO-B25-0811", 12, 12, type="diagnosed", tec="TEC-002",
       cause="valve_actuator_failure", action="temporary_valve_override",
       note="阀又卡死，再次手动开阀。反复出问题，强烈建议更换执行器", labor=120)
    ev("WO-B25-0811", 12, 13, type="closed")

    # 故事 B：A1106 欠费锁机（2 单）
    wo("WO-A11-0709", days_ago(45, 10, 3), "SP-A-11-1106", "FCU-A11-06", "C-003",
       "A1106空调开不了，面板没反应", "unit_wont_start")
    ev("WO-A11-0709", 45, 12, type="dispatched", tec="TEC-003")
    ev("WO-A11-0709", 45, 14, type="diagnosed", tec="TEC-003",
       cause="power_supply_fault", note="现场检查供电线路正常，面板无电，疑似锁机", labor=60)
    ev("WO-A11-0709", 44, 9, type="revisit",
       note="次日租户充值空调费后自行恢复，确认为欠费停机")
    ev("WO-A11-0709", 44, 9, type="closed")

    wo("WO-A11-0803", days_ago(20, 11, 20), "SP-A-11-1106", "FCU-A11-06", "C-003",
       "A1106空调又开不了，跟上次一样没反应", "unit_wont_start")
    ev("WO-A11-0803", 20, 13, type="dispatched", tec="TEC-003")
    ev("WO-A11-0803", 20, 15, type="diagnosed", tec="TEC-003",
       cause="power_supply_fault", note="到场面板仍无电，测线路正常，疑似锁机", labor=60)
    ev("WO-A11-0803", 20, 16, type="closed", note="租户随后充值恢复，未再复访")

    # 其余背景工单
    wo("WO-B19-0704", days_ago(50, 9, 30), "SP-A-19-1913", "FCU-A19-13", "C-001",
       "A1913空调风量很小，去年装修改过风管", "weak_airflow")
    ev("WO-B19-0704", 50, 11, type="dispatched", tec="TEC-001")
    ev("WO-B19-0704", 50, 13, type="diagnosed", tec="TEC-001",
       cause="tenant_modification", action="explain_to_tenant", labor=0,
       note="空调风管末端接了排风管，并且管子过长，影响温度及风速。已向租户说明需自行整改")
    ev("WO-B19-0704", 50, 14, type="closed")

    wo("WO-A16-0614", days_ago(70, 10, 0), "SP-A-16-1608", "FCU-A16-08", None,
       "A1608空调有异响，嗡嗡的", "abnormal_noise")
    ev("WO-A16-0614", 70, 12, type="dispatched", tec="TEC-005")
    ev("WO-A16-0614", 70, 14, type="diagnosed", tec="TEC-005",
       cause="fan_motor_fault", note="电机轴承异响，已喷润滑处理，持续观察", labor=40)
    ev("WO-A16-0614", 70, 15, type="closed")


# ── L3 洞察（source=agent_replay：由历史回放归纳）────────────

def _l3(conn: sqlite3.Connection, embedder: EmbedFn) -> None:
    ins_1 = (
        "该风机盘管 60 天内因「不制冷」报修 3 次（WO-B25-0624 / WO-B25-0720 / "
        "WO-B25-0811）：首次按滤网脏清洗处置，后两次技工均判断为电动阀执行器故障，"
        "但都只做了手动开阀的临时措施，未换阀。运行快照特征：**阀位反馈 0% 而冷冻水"
        "流量仍 >0**（阀卡死/执行器损坏）。再接到该点位报修时应直接安排更换阀位执行器，"
        "不再重复临时开阀——临时开阀不换阀必然复发。"
    )
    conn.execute(
        "INSERT INTO insight VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("INS-REPLAY-001", "asset", "FCU-A25-01", ins_1, jdump(embedder(ins_1)),
         "valve_actuator_failure", 0.82, 1, 1,
         jdump(["WO-B25-0624", "WO-B25-0720", "WO-B25-0811"]),
         days_ago(11, 18, 0), days_ago(11, 18, 30), "agent_replay"),
    )
    conn.execute(
        "INSERT INTO insight_verification "
        "(insight_id,wo_id,predicted,actual,hit,confidence_before,confidence_after,verified_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        ("INS-REPLAY-001", "WO-B25-0811", "valve_actuator_failure",
         "valve_actuator_failure", 1, 0.70, 0.82, days_ago(11, 18, 30)),
    )

    ins_2 = (
        "该空间两次「空调开不了机」工单（WO-A11-0709 / WO-A11-0803）最终均为"
        "欠费停机，而非供电故障。特征：面板无电但线路检测正常，运行快照 "
        "lock_status=billing_locked。处置前应先查运行参数中的 lock_status；"
        "确认欠费后通知租户充值恢复（restore_after_payment），避免无效派工。"
    )
    conn.execute(
        "INSERT INTO insight VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("INS-REPLAY-002", "space", "SP-A-11-1106", ins_2, jdump(embedder(ins_2)),
         "billing_suspension", 0.58, 0, 0,
         jdump(["WO-A11-0709", "WO-A11-0803"]),
         days_ago(18, 17, 0), None, "agent_replay"),
    )


def reset(conn: sqlite3.Connection, embedder: EmbedFn) -> None:
    """删库重建 + 灌种子（Web「重置」按钮用）。"""
    conn.execute("PRAGMA foreign_keys = OFF")
    for t in ("insight_review_queue", "insight_verification", "insight",
              "event_log", "work_order_event", "work_order",
              "technician", "contract_clause", "space_party", "tenant_occupies_space",
              "contact", "tenant", "asset_runtime", "space_served_by_asset",
              "asset", "asset_type", "space", "building", "property"):
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    from wagent_backend.ops.data.db import init_db

    init_db(conn)
    seed(conn, embedder)
