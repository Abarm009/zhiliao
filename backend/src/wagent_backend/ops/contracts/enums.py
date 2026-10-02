"""
WAgent 领域闭集枚举 —— 接口冻结文件之一
================================================
冻结日: 2026-08-16
变更规则: 本文件与 ontology/schema.sql 于 8/16 冻结。
         之后任何修改必须两人当面同意并共同评估返工量（基线 §19.1）。

设计依据: 全部枚举项均可追溯到真实脱敏工单证据（40,123 条，
         其中空调类 841 条）。见每项后的 [证据] 注释。
         无真实证据的枚举项一律不得进入本文件。

关键设计: 症状与根因是「多对多」，且刻意保留歧义。
         这不是建模瑕疵，是评测能成立的前提 ——
         若症状与根因一一对应，M1（根因命中率）对任何 Agent
         都趋近 100%，消融四档会全部打平，指标失去分辨力。

⚠️ 本文件是 git 历史 d0a9f93:ontology/enums.py 的逐字副本（原文件已从
   工作树删除）。drift 守卫测试会校验一致性 —— 修改必须走冻结变更流程。
"""

from enum import Enum


# ══════════════════════════════════════════════════════════════
# 1. Symptom —— 租户/报修人可观测的现象
#    只描述"看到什么"，不含任何诊断结论
# ══════════════════════════════════════════════════════════════

class SymptomEnum(str, Enum):
    NO_COOLING        = "no_cooling"         # [证据] 131条 "不制冷/不凉/不够冷"
    NO_HEATING        = "no_heating"         # [证据] 11条  "空调不制热"
    UNIT_WONT_START   = "unit_wont_start"    # [证据] 66条  "开不了/启动不了/没电/锁机"
    WEAK_AIRFLOW      = "weak_airflow"       # [证据] 35条  "风量不够/堵风/出风小"
    WATER_LEAK        = "water_leak"         # [证据] 132条 "漏水/滴水/凝水"
    ABNORMAL_NOISE    = "abnormal_noise"     # [证据] 43条  "异响/噪音"
    TEMP_UNEVEN       = "temp_uneven"        # [证据] "有的是凉风" "其它风口温度正常"
    ODOR              = "odor"               # [证据] "空调出风口排有烟味"
    # "客户反馈室内空调气味异常（有臭味）"
    # 2026-08-16 人工审词表时发现。映射到现有根因（滤网脏 / 接水盘发霉），
    # 不新增根因，故为纯追加的非破坏性变更。
    # 2026-08-27 非设备类报修（全盘接受业主问题，Abram 同意）：
    SANITATION        = "sanitation"         # 垃圾/保洁/卫生 —— 建议班组：环境
    SMOKING           = "smoking"            # 工区吸烟 —— 建议班组：秩序
    OVERCROWDING      = "overcrowding"       # 人员过多/聚集 —— 建议班组：秩序


# ══════════════════════════════════════════════════════════════
# 2. RootCause —— 真实根因（仿真器持有真值，Agent 需推断）
#    分三组：设备磨损类 / 系统与配置类 / 非设备类
# ══════════════════════════════════════════════════════════════

class RootCauseEnum(str, Enum):
    # ── A. 设备磨损类（仿真器「退化状态机 w」驱动）────────────
    VALVE_ACTUATOR_FAILURE = "valve_actuator_failure"
    # [证据] "空调电动阀阀坏，手动开启电动阀，恢复供冷"(B座5楼)
    #        "更换空调电磁阀"(18楼) / "空调面板已关，还有流量，有阀坏"(25楼)

    COMPRESSOR_FAULT = "compressor_fault"
    # [证据] "空调压缩机已烧坏，现在已换新压缩机"(A栋17楼)
    #        "外机压缩机坏，需更换"(B栋16楼女卫)

    FAN_MOTOR_FAULT = "fan_motor_fault"
    # [证据] "电机轴承异响，已喷润滑"(A1608) / "更换接水盘、风机"(A座711/1608)
    #        "电机没有了高中低档"(内勤室)

    FILTER_CLOGGED = "filter_clogged"
    # [证据] "拆了空调过滤网，租户洗好后为其安装上去，有些效果"(A1106)
    #        "已建议租户清洗下空调过滤网"(B-1112-1114)

    CONDENSATE_DRAIN_BLOCKED = "condensate_drain_blocked"
    # [证据] "接水盘堵塞漏水，已疏通恢复正常"(A座4楼) / 冷凝水 43次

    PIPE_INSULATION_FAILURE = "pipe_insulation_failure"
    # [证据] "空调冷水管道包保温棉" / "已经更换漏水管道" / "更换波纹管"
    #        冷冻水管保温层失效 → 管壁结露滴水。全库水管 205 次。
    #        ★ 与 CONDENSATE_DRAIN_BLOCKED 症状相同（WATER_LEAK）但处置
    #          完全不同：一个是疏通，一个是包保温。混淆 = 必然复发。

    CONTROL_PANEL_FAULT = "control_panel_fault"
    # [证据] "空调面板显示代号C0。启动不了" / "空调面板有电，就是点不动"
    #        "暂无面板更换" / "张红面板更换等租客买"。全库面板 102 次。
    #        ★ 与 SENSOR_DRIFT 的区别：面板本身坏（无响应/报错码） vs
    #          面板显示正常但读数失真。前者可见，后者不可见 —— 这正是
    #          SENSOR_DRIFT 需要历史才能识别的原因。

    DUCT_DAMAGE = "duct_damage"
    # [证据] "排风管断了。" / 风管 18 次
    #        与 TENANT_MODIFICATION 的区别：损坏 vs 人为改造，责任方不同。

    SENSOR_DRIFT = "sensor_drift"
    # [证据] "空调面板正常，就是不出凉风"(A-1109，面板显示与实际不符，102次面板类)

    POWER_SUPPLY_FAULT = "power_supply_fault"
    # [证据] "食堂空调面板没电故障 → 线路老化,重新规整修复线路"
    #        "A601空调电跳闸" / "1608空调没反应 → 跳闸"
    #        全库空开 116 / 配电箱 66 / 跳闸 266 次。
    #        ★ 与 BILLING_SUSPENSION 共享症状 UNIT_WONT_START —— 这是
    #          "空调开不了"最重要的一组歧义：欠费锁机 vs 空开跳闸。
    #          两者的处置、责任、成本完全不同，靠症状文本无法区分。

    # ── B. 系统与配置类 ──────────────────────────────────────
    CHILLED_WATER_SUPPLY = "chilled_water_supply"
    # [证据] "一台主机运行"(A栋17楼) / "主机没起，陈工会来处理"(A1309)
    #        本楼为中央空调冷冻水系统，末端为风机盘管

    SETPOINT_MISCONFIGURED = "setpoint_misconfigured"
    # [证据] "未开制冷，现已开"(B17楼) / "开启阀门，空调正常供冷"(A座2楼)
    #        "昨天1809房东请外方检修时他们关了的"(1811A)

    REFRIGERANT_LOW = "refrigerant_low"
    # [证据] 弱。全库"冷媒"仅 2 次。仅适用于少数分体机区域（外机 28 次）。
    #        ⚠️ 不得用作中央空调末端的根因 —— 冷冻水盘管无冷媒回路。
    #        保留是为了让 Agent 有机会犯这个错（它是 LLM 的常见先验）。

    # ── C. 非设备类（仿真器独立状态机驱动，非磨损）────────────
    BILLING_SUSPENSION = "billing_suspension"
    # [证据] 96 条 (11.4%) 充值/欠费/锁机/送电。"欠费停机"(A1106)
    #        A1006 八次工单中五次为费用类。这是真实第一高频"故障"。

    TENANT_MODIFICATION = "tenant_modification"
    # [证据] "空调风管末端接了排风管，并且管子过长，影响温度及风速"(B1913)
    #        "应租户要求拆除出风口栅栏"(B-1211)

    CAPACITY_UNDERSIZED = "capacity_undersized"
    # [证据] "两个打通的房间，只有两个出风口，已告知租户用风扇吸下"(B1810-1820)

    TENANT_LOAD_EXCESS = "tenant_load_excess"
    # [证据] 机房/密集工位超设计负荷。⚠️ 真实数据支撑较弱，保留为低频项。

    NO_FAULT_TENANT_PERCEPTION = "no_fault_tenant_perception"
    # [证据] 21.3% 处置记录为"空调正常/没问题/无异常"。
    #        "出风口温度17度左右"(B-1211) —— 设备正常，是租户预期问题。
    #        ⚠️ 必须存在此项，否则 Agent 永远假设有故障，M3 治标率失真。


# ══════════════════════════════════════════════════════════════
# 3. Action —— 推荐处置
# ══════════════════════════════════════════════════════════════

class ActionEnum(str, Enum):
    # 治本类
    REPLACE_VALVE_ACTUATOR   = "replace_valve_actuator"      # [证据] "更换空调电磁阀"
    REPLACE_COMPRESSOR       = "replace_compressor"          # [证据] "已换新压缩机"
    REPLACE_FAN_MOTOR        = "replace_fan_motor"           # [证据] "更换接水盘、风机"
    CLEAN_REPLACE_FILTER     = "clean_replace_filter"        # [证据] "清洗空调过滤网"
    CLEAR_CONDENSATE_DRAIN   = "clear_condensate_drain"      # [证据] "接水盘堵塞，已疏通"
    RECALIBRATE_SENSOR       = "recalibrate_sensor"
    REPAIR_POWER_CIRCUIT     = "repair_power_circuit"        # [证据] "线路老化,重新规整修复线路"
    REPLACE_CONTROL_PANEL    = "replace_control_panel"       # [证据] "面板更换"
    REINSULATE_PIPING        = "reinsulate_piping"           # [证据] "空调冷水管道包保温棉"
    REPAIR_DUCT              = "repair_duct"                 # [证据] "排风管断了"
    ESCALATE_CENTRAL_PLANT   = "escalate_central_plant"      # [证据] "陈工会来处理"（主机侧）
    ADJUST_SETPOINT          = "adjust_setpoint"             # [证据] "未开制冷，现已开"
    RECHARGE_REFRIGERANT     = "recharge_refrigerant"
    RESTORE_AFTER_PAYMENT    = "restore_after_payment"       # [证据] "充值空调费" → 解锁
    RECTIFY_TENANT_MODIFICATION = "rectify_tenant_modification"  # [证据] B1913 风管整改
    REDESIGN_AIRFLOW_CAPACITY   = "redesign_airflow_capacity"    # [证据] B1810 增加风口
    NO_ACTION_TENANT_SIDE    = "no_action_tenant_side"       # 设备正常时的正确处置

    # 治标类 —— 全部来自真实处置记录，是当前 SOP 的实际行为
    TEMPORARY_VALVE_OVERRIDE = "temporary_valve_override"
    # [证据] "空调电动阀阀坏，手动开启电动阀，恢复供冷" —— 阀没换，必然复发
    CLOSE_AS_NORMAL          = "close_as_normal"
    # [证据] 21.3% —— "空调正常" 直接关单
    EXPLAIN_TO_TENANT        = "explain_to_tenant"
    # [证据] 9.8% —— "已和租户说明" / "已告知租户用风扇吸下"
    DISPATCH_HVAC_VENDOR     = "dispatch_hvac_vendor"
    # [证据] "已联系厂家维保处理" —— 转手，不构成处置结论
    SCHEDULE_OVERHAUL        = "schedule_overhaul"           # 纳入大修计划（不解决当次）


class LiabilityEnum(str, Enum):
    OWNER   = "owner"
    TENANT  = "tenant"
    SHARED  = "shared"
    VENDOR  = "vendor"     # [证据] dutyParty 字段存在"外方责任"(43条)
    UNCLEAR = "unclear"


# ══════════════════════════════════════════════════════════════
# 4. 治本映射 —— M3「治标率」的判定依据
#
# ⚠️ 修正基线 §16.1 的规格错误：
#    基线定义 M3 = "推荐处置 ∉ 治本集合的比例"（一个扁平集合）。
#    这是错的 —— 治本与否依赖真实根因。
#    ADJUST_SETPOINT 对 SETPOINT_MISCONFIGURED 是治本，
#    对 VALVE_ACTUATOR_FAILURE 就是治标。
#    因此必须是条件映射：CURATIVE_ACTIONS[true_root_cause]
#
# M3 = |{ d : d.recommended_action ∉ CURATIVE_ACTIONS[truth.root_cause] }| / N
# ══════════════════════════════════════════════════════════════

R = RootCauseEnum
A = ActionEnum

CURATIVE_ACTIONS: dict[RootCauseEnum, set[ActionEnum]] = {
    R.VALVE_ACTUATOR_FAILURE:     {A.REPLACE_VALVE_ACTUATOR},
    R.COMPRESSOR_FAULT:           {A.REPLACE_COMPRESSOR},
    R.FAN_MOTOR_FAULT:            {A.REPLACE_FAN_MOTOR},
    R.FILTER_CLOGGED:             {A.CLEAN_REPLACE_FILTER},
    R.CONDENSATE_DRAIN_BLOCKED:   {A.CLEAR_CONDENSATE_DRAIN},
    R.SENSOR_DRIFT:               {A.RECALIBRATE_SENSOR},
    R.POWER_SUPPLY_FAULT:         {A.REPAIR_POWER_CIRCUIT},
    R.CONTROL_PANEL_FAULT:        {A.REPLACE_CONTROL_PANEL},
    R.PIPE_INSULATION_FAILURE:    {A.REINSULATE_PIPING},
    R.DUCT_DAMAGE:                {A.REPAIR_DUCT},
    R.CHILLED_WATER_SUPPLY:       {A.ESCALATE_CENTRAL_PLANT},
    R.SETPOINT_MISCONFIGURED:     {A.ADJUST_SETPOINT},
    R.REFRIGERANT_LOW:            {A.RECHARGE_REFRIGERANT},
    R.BILLING_SUSPENSION:         {A.RESTORE_AFTER_PAYMENT},
    R.TENANT_MODIFICATION:        {A.RECTIFY_TENANT_MODIFICATION},
    R.CAPACITY_UNDERSIZED:        {A.REDESIGN_AIRFLOW_CAPACITY},
    R.TENANT_LOAD_EXCESS:         {A.REDESIGN_AIRFLOW_CAPACITY, A.EXPLAIN_TO_TENANT},
    R.NO_FAULT_TENANT_PERCEPTION: {A.NO_ACTION_TENANT_SIDE, A.EXPLAIN_TO_TENANT},
}

# 恒为治标的处置 —— 无论真因为何都不解决问题（用于交叉校验）
ALWAYS_PALLIATIVE: set[ActionEnum] = {
    A.TEMPORARY_VALVE_OVERRIDE,
    A.CLOSE_AS_NORMAL,
    A.DISPATCH_HVAC_VENDOR,
    A.SCHEDULE_OVERHAUL,
}

# ══════════════════════════════════════════════════════════════
# 5. 默认责任归属 —— judge_liability 的基准，可被合同条款覆写
#
# ⚠️ 真实数据无法校准此映射：dutyParty 字段 40,080/40,123 全部
#    填「公司责任」，43 条填「外方责任」，无一条「租户责任」。
#    也就是说责任判定字段在生产系统里是废字段、默认值。
#    这既是本项目的机会（§5 决策层），也是一个必须承认的
#    校准缺口 —— 涉及 liability 的指标可信度低于 M1/M3。
# ══════════════════════════════════════════════════════════════

DEFAULT_LIABILITY: dict[RootCauseEnum, LiabilityEnum] = {
    R.VALVE_ACTUATOR_FAILURE:     LiabilityEnum.OWNER,
    R.COMPRESSOR_FAULT:           LiabilityEnum.OWNER,
    R.FAN_MOTOR_FAULT:            LiabilityEnum.OWNER,
    R.CONDENSATE_DRAIN_BLOCKED:   LiabilityEnum.OWNER,
    R.SENSOR_DRIFT:               LiabilityEnum.OWNER,
    R.POWER_SUPPLY_FAULT:         LiabilityEnum.OWNER,
    R.CONTROL_PANEL_FAULT:        LiabilityEnum.OWNER,
    R.PIPE_INSULATION_FAILURE:    LiabilityEnum.OWNER,
    R.DUCT_DAMAGE:                LiabilityEnum.OWNER,
    R.CHILLED_WATER_SUPPLY:       LiabilityEnum.OWNER,
    R.REFRIGERANT_LOW:            LiabilityEnum.OWNER,
    R.FILTER_CLOGGED:             LiabilityEnum.SHARED,   # 清洗周期常约定在租约
    R.SETPOINT_MISCONFIGURED:     LiabilityEnum.SHARED,
    R.BILLING_SUSPENSION:         LiabilityEnum.TENANT,
    R.TENANT_MODIFICATION:        LiabilityEnum.TENANT,
    R.TENANT_LOAD_EXCESS:         LiabilityEnum.TENANT,
    R.CAPACITY_UNDERSIZED:        LiabilityEnum.OWNER,    # 交付标准不足
    R.NO_FAULT_TENANT_PERCEPTION: LiabilityEnum.UNCLEAR,
}

# ══════════════════════════════════════════════════════════════
# 6. 症状 → 候选根因（多对多，刻意保留歧义）
#    ⚠️ 此表仅供仿真器与评测分析使用，禁止注入 Agent 的 prompt。
#       否则等同于把答案交给 Agent。
# ══════════════════════════════════════════════════════════════

SYMPTOM_CANDIDATE_CAUSES: dict[SymptomEnum, set[RootCauseEnum]] = {
    SymptomEnum.NO_COOLING: {
        R.VALVE_ACTUATOR_FAILURE, R.COMPRESSOR_FAULT, R.FILTER_CLOGGED,
        R.SENSOR_DRIFT, R.CHILLED_WATER_SUPPLY, R.SETPOINT_MISCONFIGURED,
        R.REFRIGERANT_LOW, R.BILLING_SUSPENSION, R.TENANT_MODIFICATION,
        R.CAPACITY_UNDERSIZED, R.TENANT_LOAD_EXCESS, R.CONTROL_PANEL_FAULT,
        R.NO_FAULT_TENANT_PERCEPTION,
    },  # ← 13 个候选根因共享同一个症状。这就是问题的难度所在。
    SymptomEnum.UNIT_WONT_START: {
        R.BILLING_SUSPENSION, R.POWER_SUPPLY_FAULT, R.SETPOINT_MISCONFIGURED,
        R.VALVE_ACTUATOR_FAILURE, R.COMPRESSOR_FAULT, R.CHILLED_WATER_SUPPLY,
        R.SENSOR_DRIFT, R.CONTROL_PANEL_FAULT,
    },  # ← 欠费锁机 vs 空开跳闸：症状文本完全相同，处置与责任完全不同
    SymptomEnum.NO_HEATING: {
        R.VALVE_ACTUATOR_FAILURE, R.CHILLED_WATER_SUPPLY, R.COMPRESSOR_FAULT,
        R.SETPOINT_MISCONFIGURED, R.SENSOR_DRIFT,
    },
    SymptomEnum.WEAK_AIRFLOW: {
        R.FILTER_CLOGGED, R.FAN_MOTOR_FAULT, R.TENANT_MODIFICATION,
        R.CAPACITY_UNDERSIZED, R.DUCT_DAMAGE,
    },
    SymptomEnum.WATER_LEAK: {
        R.CONDENSATE_DRAIN_BLOCKED, R.PIPE_INSULATION_FAILURE,
        R.VALVE_ACTUATOR_FAILURE, R.TENANT_MODIFICATION,
    },  # ← 疏通 vs 包保温：症状相同，处置相反
    SymptomEnum.ABNORMAL_NOISE: {
        R.FAN_MOTOR_FAULT, R.VALVE_ACTUATOR_FAILURE, R.COMPRESSOR_FAULT,
    },
    SymptomEnum.TEMP_UNEVEN: {
        R.CAPACITY_UNDERSIZED, R.TENANT_MODIFICATION, R.VALVE_ACTUATOR_FAILURE,
        R.SENSOR_DRIFT,
    },
    SymptomEnum.ODOR: {
        R.FILTER_CLOGGED, R.CONDENSATE_DRAIN_BLOCKED, R.DUCT_DAMAGE,
    },  # 滤网积尘 / 接水盘积水发霉 / 风管串味
    # 非设备类报修（2026-08-27）：无设备根因候选，Agent 也不会看到这张表
    SymptomEnum.SANITATION: set(),
    SymptomEnum.SMOKING: set(),
    SymptomEnum.OVERCROWDING: set(),
}


# ══════════════════════════════════════════════════════════════
# 7. 安全类前置拦截关键词 —— policy.py 使用，模型不参与判断
#    基线 §10。命中即 escalate，不进入模型推理路径。
# ══════════════════════════════════════════════════════════════

SAFETY_PRECHECK_KEYWORDS: tuple[str, ...] = (
    "困人", "关人", "被困",            # 电梯困人
    "火警", "着火", "冒烟", "烟感",     # 消防
    "燃气", "煤气", "天然气",
    "触电", "漏电",
    "坠落", "掉落", "高空",
    "坍塌", "裂缝", "结构", "沉降",
    "爆管", "喷水", "水浸", "淹",
    "有人受伤", "受伤", "晕倒",
)
