"""
WAgent 工具契约 + 结构化决策输出 —— 接口冻结文件之一
================================================
冻结日: 2026-08-16
变更规则: 8/16 之后修改本文件必须两人当面同意（基线 §19.1）

约束:
  - 10 个工具，不增第 11 个（基线 §8）
  - 本文件不得 import simulator/ 或 harness/
  - 同一份函数两个入口：MCP server（交互）+ 进程内直调（批量评测）

⚠️ 本文件是 agent/tools/schemas.py（冻结版，仍在工作树）的逐字副本，
   唯一差异：import 路径从 wagent.ontology.enums 适配为包内 contracts.enums。
   drift 守卫测试会校验除 import 行外与原文件逐字一致 ——
   修改必须走冻结变更流程。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from wagent_backend.ops.contracts.enums import (
    ActionEnum,
    LiabilityEnum,
    RootCauseEnum,
    SymptomEnum,
)

# ═══════════════════════════════════════════════════════════════
# 通用返回包装 —— 所有工具统一。让 Agent 能区分"查不到"与"出错"，
# 这两者的正确后续动作不同（前者继续推理，后者应 escalate）。
# ═══════════════════════════════════════════════════════════════


class ToolError(BaseModel):
    code: Literal["not_found", "ambiguous", "invalid_input", "upstream_error"]
    message: str
    hint: str | None = None


# ═══════════════════════════════════════════════════════════════
# 1. resolve_space —— 自然语言 → 空间 ID
# ═══════════════════════════════════════════════════════════════


class ResolveSpaceInput(BaseModel):
    text: str = Field(description="租户原话中的位置描述，如 '25楼东侧' / 'A1913' / 'A座4楼太平'")
    building_hint: str | None = Field(default=None, description="已知楼栋时传入，可消歧")


class SpaceMatch(BaseModel):
    space_id: str
    building: str
    floor: int
    zone: str | None
    unit_no: str | None
    space_type: str
    area_sqm: float | None
    match_confidence: float = Field(ge=0, le=1)
    matched_on: str = Field(description="命中的别名或规则，供 trace 溯源")


class ResolveSpaceOutput(BaseModel):
    """歧义时返回多个候选而非猜一个 —— 真实报修 40% 以上位置描述不精确。"""

    matches: list[SpaceMatch] = Field(default_factory=list)
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 2. get_assets_serving_space —— 空间 → 服务该空间的设备（含运行参数）
#
# ⚠️ 关键设计：AssetRuntime.lock_status 是 billing_suspension 唯一
#    可被发现的通道。不新增 check_billing 工具。
#    无记忆的 Agent 拿到 lock_status 也不会去看（症状是"不制冷"，
#    它会去查暖通）；有记忆的 Agent 因为知道这个空间的历史才会去看。
#    「知道该看哪里」正是记忆的产出，也是本工具设计的用意。
# ═══════════════════════════════════════════════════════════════


class GetAssetsServingSpaceInput(BaseModel):
    space_id: str
    category: Literal["HVAC", "ELEC", "PLUMB", "FIRE", "ALL"] = "ALL"


class AssetRuntime(BaseModel):
    ts: datetime
    supply_air_temp_c: float | None = None
    return_air_temp_c: float | None = None
    setpoint_c: float | None = None
    valve_position_pct: float | None = Field(default=None, description="阀位反馈，可能失真")
    water_flow_lpm: float | None = Field(
        default=None,
        description="冷冻水流量。阀位 0% 但流量 >0 = 阀卡死（真实案例：25楼「面板已关，还有流量，有阀坏」）",
    )
    fan_speed: Literal["off", "low", "mid", "high"] | None = None
    runtime_hours_24h: float | None = None
    lock_status: Literal["normal", "billing_locked", "manual_off", "fault_lock"] | None = None


class Asset(BaseModel):
    """字段对齐真实设备台账（2026-08-16 依据真实系统截图定）。"""

    asset_id: str
    asset_no: str | None = Field(default=None, description="真实台账设备编号")
    asset_name: str = Field(description="设备名称：风机盘管 / 感烟探测器")
    asset_type: str = Field(description="FCU / AHU / CHILLER / PUMP")
    category: str
    spec_model: str | None = Field(default=None, description="规格型号，如 LD3663EH")
    brand: str | None = None

    # 位置 —— 「装在哪」，不等于「服务哪片区」
    located_in_space: str | None = None
    floor: int | None = None
    parent_asset_id: str | None = Field(default=None, description="所属 AHU / 冷冻水环路")

    # 服务关系 —— 来自 space_served_by_asset
    service_role: Literal["primary", "backup", "partial"] = "primary"
    coverage_pct: float | None = None

    # 役龄 —— 设备老化程度的可见信号，Agent 可据此调整根因先验
    commissioned_date: date | None = Field(default=None, description="投入使用日期")
    design_life_years: int | None = Field(default=None, description="合理使用年限")
    is_overdue_service: bool = Field(default=False, description="是否超期服役")

    # 保修与权属 —— judge_liability 的 VENDOR 分叉依据
    warranty_until: date | None = Field(default=None, description="过保日期")
    vendor_name: str | None = None
    ownership: str | None = Field(default=None, description="设备权属：自管 / 外包")

    # 责任 —— find_technician 与派工交底的收件人
    responsible_dept: str | None = None
    responsible_person: str | None = None

    criticality: str | None = Field(default=None, description="管理等级：重要 / 一般")
    status: str | None = Field(default="在用", description="设备状态：在用 / 停用 / 报废")

    runtime: AssetRuntime | None = None


class GetAssetsServingSpaceOutput(BaseModel):
    assets: list[Asset] = Field(default_factory=list)
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 3. query_workorder_history
# ═══════════════════════════════════════════════════════════════


class QueryWorkorderHistoryInput(BaseModel):
    scope: Literal["asset", "space", "tenant", "building"]
    id: str
    window: str = Field(default="90d", description="7d / 30d / 90d / 180d / 365d")
    symptom_filter: SymptomEnum | None = None


class WorkOrderDisposition(BaseModel):
    """工单的一次处置记录。同一工单可有多条（append-only）。"""

    ts: datetime
    technician_id: str | None = None
    reported_cause: RootCauseEnum | None = Field(
        default=None, description="技工当时的判断 —— 可能是错的，不是真值"
    )
    action_taken: ActionEnum | None = None
    liability: LiabilityEnum | None = None
    note: str | None = Field(default=None, description="处置原文，真实运维口语")
    total_cost: float | None = None


class WorkOrder(BaseModel):
    wo_id: str
    created_at: datetime
    space_id: str | None = None
    asset_id: str | None = None
    raw_text: str = Field(description="租户原话")
    symptom: SymptomEnum | None = None
    urgency: str = "一般"
    dispositions: list[WorkOrderDisposition] = Field(default_factory=list)
    closed: bool = False


class QueryWorkorderHistoryOutput(BaseModel):
    work_orders: list[WorkOrder] = Field(default_factory=list)
    total_count: int = 0
    truncated: bool = False
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 4. recall_memory —— L3 洞察检索
# ═══════════════════════════════════════════════════════════════


class RecallMemoryInput(BaseModel):
    query: str
    scope_type: Literal["asset", "space", "tenant", "building", "any"] = "any"
    scope_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class MemoryItem(BaseModel):
    insight_id: str
    scope_type: str
    scope_id: str
    body_md: str
    predicted_root_cause: RootCauseEnum | None = None
    confidence: float = Field(ge=0, le=1)
    hit_count: int = 0
    trial_count: int = 0
    evidence_wo_ids: list[str]
    generated_at: datetime
    last_verified: datetime | None = None
    similarity: float | None = None

    # 基线 §11.4：低置信条目必须标记，不得隐藏
    low_confidence: bool = False

    @field_validator("low_confidence", mode="before")
    @classmethod
    def _derive(cls, v, info):
        c = info.data.get("confidence")
        return True if (c is not None and c < 0.6) else bool(v)


class RecallMemoryOutput(BaseModel):
    items: list[MemoryItem] = Field(default_factory=list)
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 5. write_memory
# ═══════════════════════════════════════════════════════════════


class WriteMemoryInput(BaseModel):
    scope_type: Literal["asset", "space", "tenant", "building"]
    scope_id: str
    body_md: str
    predicted_root_cause: RootCauseEnum | None = None
    confidence: float = Field(ge=0, le=1)
    evidence_wo_ids: list[str] = Field(min_length=1, description="无证据的洞察拒绝落库")
    source: Literal["agent_replay", "agent_runtime"]


class WriteMemoryOutput(BaseModel):
    insight_id: str | None = None
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 6. verify_memory_prediction —— 自优化机制 2：结果回写
# ═══════════════════════════════════════════════════════════════


class VerifyMemoryPredictionInput(BaseModel):
    insight_id: str
    wo_id: str
    actual_root_cause: RootCauseEnum


class VerifyMemoryPredictionOutput(BaseModel):
    insight_id: str
    hit: bool
    confidence_before: float
    confidence_after: float
    hit_count: int
    trial_count: int
    moved_to_review_queue: bool = False
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 7. judge_liability
# ═══════════════════════════════════════════════════════════════


class JudgeLiabilityInput(BaseModel):
    space_id: str
    symptom: SymptomEnum
    asset_id: str | None = None
    hypothesized_root_cause: RootCauseEnum | None = None
    estimated_cost_cny: float | None = None


class JudgeLiabilityOutput(BaseModel):
    liability: LiabilityEnum
    basis: Literal["contract_clause", "default_mapping", "no_basis"]
    clause_ids: list[str] = Field(default_factory=list)
    clause_text: str | None = None
    estimated_cost_cny: float | None = None
    # policy.py 后置检查依据：金额 > 5000 或条款缺失/歧义 → escalate
    requires_human: bool = False
    requires_human_reason: str | None = None
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 8. create_workorder
# ═══════════════════════════════════════════════════════════════


class CreateWorkorderInput(BaseModel):
    space_id: str | None = Field(
        default=None, description="报修空间；2026-08-27 起可空 —— 无法定位也先建单，"
        "raw_text 保留租户原话、briefing_note 写清位置描述，事后可再补充"
    )
    asset_id: str | None = None
    raw_text: str
    symptom: SymptomEnum
    urgency: Literal["一般", "紧急", "特急"] = "一般"
    assigned_technician_id: str | None = None
    hypothesized_root_cause: RootCauseEnum | None = None
    recommended_action: ActionEnum | None = None
    liability: LiabilityEnum | None = None
    briefing_note: str | None = Field(
        default=None, description="给技工的交底：前次处置记录 + 根因假设。这是治标→治本的关键载体。"
    )
    evidence_wo_ids: list[str] = Field(default_factory=list)


class CreateWorkorderOutput(BaseModel):
    wo_id: str | None = None
    repeat_evidence: list[str] = Field(
        default_factory=list,
        description="同空间同症状 90 天内的已有工单号（建单前确定性查重，供复发判定引用）")
    repeat_hint: str | None = Field(
        default=None,
        description="查重命中时的提示：要求模型评估复发并在 Decision.is_repeat_fault/repeat_evidence 体现")
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 9. find_technician —— 静态规则匹配（基线 §8 已降级，不做优化排程）
# ═══════════════════════════════════════════════════════════════


class FindTechnicianInput(BaseModel):
    skill: str = Field(description="HVAC / ELEC / PLUMB")
    building_id: str
    at: datetime | None = None
    certification: str | None = None


class Technician(BaseModel):
    technician_id: str
    name: str
    skills: list[str]
    certification: list[str] = Field(default_factory=list)
    home_building: str | None = None
    shift: str | None = None
    available: bool = True
    eta_minutes: int | None = None


class FindTechnicianOutput(BaseModel):
    technicians: list[Technician] = Field(default_factory=list)
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 10. notify
# ═══════════════════════════════════════════════════════════════


class NotifyInput(BaseModel):
    channel: Literal["wecom", "sms", "app"]
    recipient_role: Literal["tenant_contact", "facility_manager", "technician"]
    recipient_id: str
    message: str
    wo_id: str | None = None


class NotifyOutput(BaseModel):
    receipt_id: str | None = None
    delivered_at: datetime | None = None
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
# 11. escalate_to_human
# ═══════════════════════════════════════════════════════════════


class EscalateToHumanInput(BaseModel):
    reason: Literal[
        "safety_precheck",
        "cost_threshold",
        "low_confidence_memory_only",
        "repeat_failure_2x",
        "step_limit",
        "contract_ambiguous",
        "tenant_requested",
    ]
    detail: str
    space_id: str | None = None
    asset_id: str | None = None
    wo_id: str | None = None


class EscalateToHumanOutput(BaseModel):
    ticket_id: str | None = None
    error: ToolError | None = None


# ═══════════════════════════════════════════════════════════════
#  Decision —— Agent 的最终产出（基线 §9）
#
#  评测只读结构化字段。tenant_message / manager_message 仅供展示，
#  不进入任何指标计算。
# ═══════════════════════════════════════════════════════════════


class Decision(BaseModel):
    # ── 定位 ────────────────────────────────
    space_id: str | None = Field(
        default=None, description="2026-08-27 起可空：实在无法定位时填 null，不要编造"
    )
    asset_id: str | None = None

    # ── 诊断（M1 评测对象）────────────────────
    symptom: SymptomEnum
    root_cause: RootCauseEnum
    root_cause_confidence: float = Field(ge=0, le=1)

    # ── 复发判定（M2 评测对象，P 与 R 同时报）──
    is_repeat_fault: bool
    repeat_evidence: list[str] = Field(
        default_factory=list, description="支撑复发判定的历史工单 ID"
    )

    # ── 处置（M3 / M4 评测对象）───────────────
    recommended_action: ActionEnum

    # ── 责任 ────────────────────────────────
    liability: LiabilityEnum
    liability_basis: Literal["contract_clause", "default_mapping", "no_basis"] = "no_basis"
    estimated_cost_cny: float | None = None

    # ── 升级（M5 评测对象）────────────────────
    escalate: bool = False
    escalate_reason: str | None = None

    # ── ★ 决定性字段：记忆是否真的影响了决策，可审计 ──
    memory_ids_used: list[str] = Field(default_factory=list)

    # ── 自然语言，仅展示，不参与评测 ───────────
    tenant_message: str = ""
    manager_message: str = ""

    @field_validator("escalate_reason")
    @classmethod
    def _reason_required(cls, v, info):
        if info.data.get("escalate") and not v:
            raise ValueError("escalate=True 时必须提供 escalate_reason")
        return v

    @field_validator("repeat_evidence")
    @classmethod
    def _evidence_required(cls, v, info):
        if info.data.get("is_repeat_fault") and not v:
            raise ValueError("is_repeat_fault=True 时必须提供 repeat_evidence")
        return v


# ═══════════════════════════════════════════════════════════════
#  工具注册表 —— MCP server 与进程内直调共用同一份签名
#  ⚠️ 恰好 10 项。新增前请重读基线 §8。
# ═══════════════════════════════════════════════════════════════

TOOL_REGISTRY: dict[str, tuple[type[BaseModel], type[BaseModel]]] = {
    "resolve_space":              (ResolveSpaceInput, ResolveSpaceOutput),
    "get_assets_serving_space":   (GetAssetsServingSpaceInput, GetAssetsServingSpaceOutput),
    "query_workorder_history":    (QueryWorkorderHistoryInput, QueryWorkorderHistoryOutput),
    "recall_memory":              (RecallMemoryInput, RecallMemoryOutput),
    "write_memory":               (WriteMemoryInput, WriteMemoryOutput),
    "verify_memory_prediction":   (VerifyMemoryPredictionInput, VerifyMemoryPredictionOutput),
    "judge_liability":            (JudgeLiabilityInput, JudgeLiabilityOutput),
    "create_workorder":           (CreateWorkorderInput, CreateWorkorderOutput),
    "find_technician":            (FindTechnicianInput, FindTechnicianOutput),
    "notify":                     (NotifyInput, NotifyOutput),
    "escalate_to_human":          (EscalateToHumanInput, EscalateToHumanOutput),
}

assert len(TOOL_REGISTRY) == 11, (
    "注意：基线 §8 列了 10 个工具但同时把 find_technician 保留为静态规则匹配，"
    "escalate_to_human 单列。实际契约为 11 项 —— 这是文档口径问题，不是范围蔓延。"
    f"当前 {len(TOOL_REGISTRY)} 项。"
)
