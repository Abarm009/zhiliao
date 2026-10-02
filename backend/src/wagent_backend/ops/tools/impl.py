"""11 个正式工具的实现（业务规则层）。

约定（工具说明 §1）：
    - 实体存在但窗口无记录 → 空列表 + error=None（不是错误）
    - 实体不存在 → not_found；参数非法 → invalid_input
    - 失败统一抛 ToolFailure；成功返回对应 Output 模型实例
    - 本层不 commit（registry 统一 commit/rollback → 写工具天然事务）
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta

from wagent_backend.ops.contracts import (
    DEFAULT_LIABILITY,
    Asset,
    AssetRuntime,
    CreateWorkorderInput,
    CreateWorkorderOutput,
    EscalateToHumanInput,
    EscalateToHumanOutput,
    FindTechnicianInput,
    FindTechnicianOutput,
    GetAssetsServingSpaceInput,
    GetAssetsServingSpaceOutput,
    JudgeLiabilityInput,
    JudgeLiabilityOutput,
    LiabilityEnum,
    MemoryItem,
    NotifyInput,
    NotifyOutput,
    QueryWorkorderHistoryInput,
    QueryWorkorderHistoryOutput,
    RecallMemoryInput,
    RecallMemoryOutput,
    ResolveSpaceInput,
    ResolveSpaceOutput,
    RootCauseEnum,
    SpaceMatch,
    SymptomEnum,
    Technician,
    ToolError,
    VerifyMemoryPredictionInput,
    VerifyMemoryPredictionOutput,
    WorkOrder,
    WorkOrderDisposition,
    WriteMemoryInput,
    WriteMemoryOutput,
)
from wagent_backend.ops.data import repo
from wagent_backend.ops.data.db import iso, jload
from wagent_backend.ops.data.seed import FACILITY_MANAGERS
from wagent_backend.ops.tools.context import ToolContext

# 黑客松演示口径（2026-08-26 定案，见工具说明 §14 确认记录）：
#   命中：c' = c + 0.10 * (1 - c)     —— 置信向 1 收敛，步长随置信递减
#   未命中：c' = c * 0.85             —— 温和衰减
VERIFY_HIT_GAIN = 0.10
VERIFY_MISS_DECAY = 0.85
REVIEW_CONF_THRESHOLD = 0.6
WO_RETURN_LIMIT = 100
COST_REQUIRES_HUMAN = 5000.0

# 班组预判（2026-08-27 演示口径：全盘接受业主报修，按症状建议三个固定班组）
#   水渍/卫生 → 环境；吸烟/人员聚集 → 秩序；其余（几乎一切维修）→ 工程
SUGGESTED_TEAM = {
    SymptomEnum.WATER_LEAK: "环境",
    SymptomEnum.SANITATION: "环境",
    SymptomEnum.SMOKING: "秩序",
    SymptomEnum.OVERCROWDING: "秩序",
}


def suggest_team(symptom: SymptomEnum) -> str:
    """按症状建议接单班组（确定性规则，不经模型）。"""
    return SUGGESTED_TEAM.get(symptom, "工程")


# 班组 → 成员技能归组（项目经理派单卡的数据源；秩序/环境/工程为固定演示口径）
TEAMS = ("秩序", "环境", "工程")
TEAM_SKILLS = {
    "工程": {"HVAC", "ELEC", "PLUMB"},
    "环境": {"CLEAN"},
    "秩序": {"SECURITY"},
}

VALID_WINDOWS = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "365d": 365}

_ZONE_KEYWORDS = (("东侧", "东"), ("西侧", "西"), ("南侧", "南"), ("北侧", "北"), ("核心筒", "核心筒"),
                  ("男", "男"), ("女", "女"))  # 卫生间 zone 就是 男/女，与 runner._ZONE_KWS 口径对齐

# 空间类型口语同义词（洗手间/厕所 → 卫生间 …）：既用于匹配前的文本归一，
# 也支撑「楼层+类型」收敛档——「13楼洗手间」无男女时收敛到男/女卫两个候选交上层确认
_SPACE_TYPE_SYNS = {
    "卫生间": ("卫生间", "洗手间", "厕所", "卫浴"),
    "电梯厅": ("电梯厅", "电梯", "轿厢"),
    "停车场": ("停车场", "车库", "车位"),
}


class ToolFailure(Exception):
    """工具级失败 —— registry 捕获后转成 {"error": ToolError} 信封。"""

    def __init__(self, code: str, message: str, hint: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint


def _err(code: str, message: str, hint: str | None = None) -> ToolError:
    return ToolError(code=code, message=message, hint=hint)


# ═══════════════════════════════════════════════════════════════
# 1. resolve_space
# ═══════════════════════════════════════════════════════════════

def _alias_in_text(alias_low: str, low: str) -> bool:
    """别名是否为文本子串（数字边界守卫：「3楼男卫生间」不得误中「13楼…」）。"""
    i = low.find(alias_low)
    while i != -1:
        head_ok = not (alias_low[0].isdigit() and i > 0 and low[i - 1].isdigit())
        tail = i + len(alias_low)
        tail_ok = not (alias_low[-1].isdigit() and tail < len(low) and low[tail].isdigit())
        if head_ok and tail_ok:
            return True
        i = low.find(alias_low, i + 1)
    return False


def resolve_space(ctx: ToolContext, inp: ResolveSpaceInput) -> ResolveSpaceOutput:
    text = (inp.text or "").strip()
    if not text:
        raise ToolFailure("invalid_input", "text 不能为空", "传入租户原话中的位置描述")

    hint_bld = None
    if inp.building_hint:
        hint_bld = repo.resolve_building_hint(ctx.conn, inp.building_hint.strip())
        if hint_bld is None:
            raise ToolFailure("not_found", f"楼栋不存在：{inp.building_hint}",
                              "确认 building_hint 是楼栋 ID（BLD-A）或名称（A栋）")

    floor_hit = re.search(r"(\d+)\s*楼|座?(\d+)\s*F", text, re.IGNORECASE)
    want_floor = int(floor_hit.group(1) or floor_hit.group(2)) if floor_hit else None
    want_zone = next((full for full, kw in _ZONE_KEYWORDS if full in text), None)
    want_type = next((c for c, syns in _SPACE_TYPE_SYNS.items()
                      if any(s in text for s in syns)), None)
    digits = re.findall(r"\d+", text)
    # 匹配前归一：同义词替换为库内规范名（「男洗手间」→「男卫生间」，别名子串档才能命中）
    low = text.lower()
    for canon, syns in _SPACE_TYPE_SYNS.items():
        for s in syns:
            if s != canon:
                low = low.replace(s, canon)

    cands: list[tuple[float, str, object]] = []  # (confidence, matched_on, space row)
    for row in repo.spaces_all(ctx.conn):
        if hint_bld and row["building_id"] != hint_bld:
            continue
        aliases = [a for a in (jload(row["aliases"], []) or []) if a]
        if row["space_id"].lower() == low:
            cands.append((0.95, f"space_id:{row['space_id']}", row))
        elif any(a.lower() == low for a in aliases):
            hit_alias = next(a for a in aliases if a.lower() == low)
            cands.append((0.90, f"alias:{hit_alias}", row))
        elif any(len(a) >= 2 and _alias_in_text(a.lower(), low) for a in aliases):
            # 别名子串包含：「a栋13楼男卫生间」⊃「13楼男卫生间」——口语带楼栋/现象后缀也能命中
            hit_alias = next(a for a in aliases
                             if len(a) >= 2 and _alias_in_text(a.lower(), low))
            cands.append((0.85, f"alias~:{hit_alias}", row))
        elif row["unit_no"] and row["unit_no"] in digits:
            cands.append((0.75, f"unit_no:{row['unit_no']}", row))
        elif want_floor is not None and row["floor"] == want_floor and want_zone and row["zone"] == want_zone:
            cands.append((0.50, f"floor+zone:{want_floor}F/{want_zone}", row))
        elif (want_zone is None and want_floor is not None and row["floor"] == want_floor
              and want_type and row["space_type"] == want_type):
            # 楼层+类型收敛（仅在没有方位/男女词时启用，否则高置信命中会被
            # 同层异性/异区候选拖成歧义）：「13楼洗手间」→ 男/女卫两个候选交上层确认
            cands.append((0.45, f"floor+type:{want_floor}F/{want_type}", row))
        elif want_floor is None and row["unit_no"] and any(
                d and row["unit_no"].startswith(d) for d in digits):
            # 'B19' 类门牌前缀描述（没提楼层）—— 低置信候选；
            # 提了楼层就不走前缀，避免「25楼东侧」误吸 2501 设备房
            cands.append((0.35, f"unit_prefix:{row['unit_no']}", row))

    # 稳定排序：精确 ID/别名 > 单元号 > 楼层+区域模糊（工具说明 §2）
    cands.sort(key=lambda c: (-c[0], c[2]["space_id"]))
    dedup: dict[str, tuple[float, str, object]] = {}
    for conf, matched, row in cands:
        dedup.setdefault(row["space_id"], (conf, matched, row))

    matches = [
        SpaceMatch(
            space_id=row["space_id"],
            building=repo.building_name(ctx.conn, row["building_id"]),
            floor=row["floor"],
            zone=row["zone"],
            unit_no=row["unit_no"],
            space_type=row["space_type"],
            area_sqm=row["area_sqm"],
            match_confidence=conf,
            matched_on=matched,
        )
        for sid, (conf, matched, row) in sorted(
            dedup.items(), key=lambda kv: (-kv[1][0], kv[0])
        )
    ]

    if not matches:
        raise ToolFailure("not_found", f"空间库中无匹配：{text}",
                          "换用门牌号（如 A1913）或楼栋+楼层描述重试")
    if len(matches) > 1:
        return ResolveSpaceOutput(
            matches=matches,
            error=_err("ambiguous", f"命中 {len(matches)} 个候选，不能替用户选择",
                       "向租户确认楼栋/门牌号，或带 building_hint 重查"),
        )
    return ResolveSpaceOutput(matches=matches)


# ═══════════════════════════════════════════════════════════════
# 2. get_assets_serving_space
# ═══════════════════════════════════════════════════════════════

def get_assets_serving_space(
    ctx: ToolContext, inp: GetAssetsServingSpaceInput
) -> GetAssetsServingSpaceOutput:
    if repo.space_get(ctx.conn, inp.space_id) is None:
        raise ToolFailure("not_found", f"空间不存在：{inp.space_id}",
                          "先用 resolve_space 解析正式 space_id")

    assets: list[Asset] = []
    for r in repo.assets_serving(ctx.conn, inp.space_id, ctx.as_of):
        if inp.category != "ALL" and r["_category"] != inp.category:
            continue
        rt_row = repo.runtime_latest(ctx.conn, r["asset_id"], ctx.as_of)
        runtime = None
        if rt_row is not None:
            runtime = AssetRuntime(
                ts=datetime.fromisoformat(rt_row["ts"]),
                supply_air_temp_c=rt_row["supply_air_temp_c"],
                return_air_temp_c=rt_row["return_air_temp_c"],
                setpoint_c=rt_row["setpoint_c"],
                valve_position_pct=rt_row["valve_position_pct"],
                water_flow_lpm=rt_row["water_flow_lpm"],
                fan_speed=rt_row["fan_speed"],
                runtime_hours_24h=rt_row["runtime_hours_24h"],
                lock_status=rt_row["lock_status"],
            )
        assets.append(
            Asset(
                asset_id=r["asset_id"],
                asset_no=r["asset_no"],
                asset_name=r["asset_name"],
                asset_type=r["asset_type_id"],
                category=r["_category"],
                spec_model=r["spec_model"],
                brand=r["brand"],
                located_in_space=r["located_in"],
                floor=r["floor"],
                parent_asset_id=r["parent_asset_id"],
                service_role=r["_service_role"],
                coverage_pct=r["_coverage_pct"],
                commissioned_date=date.fromisoformat(r["commissioned_date"])
                if r["commissioned_date"] else None,
                design_life_years=r["design_life_years"],
                is_overdue_service=bool(r["is_overdue_service"]),
                warranty_until=date.fromisoformat(r["warranty_until"])
                if r["warranty_until"] else None,
                vendor_name=r["vendor_name"],
                ownership=r["ownership"],
                responsible_dept=r["responsible_dept"],
                responsible_person=r["responsible_person"],
                criticality=r["criticality"],
                status=r["status"],
                runtime=runtime,
            )
        )
    assets.sort(key=lambda a: (a.service_role, a.asset_id))
    return GetAssetsServingSpaceOutput(assets=assets)


# ═══════════════════════════════════════════════════════════════
# 3. query_workorder_history
# ═══════════════════════════════════════════════════════════════

def _wo_dispositions(conn, wo_id: str) -> list[WorkOrderDisposition]:
    out: list[WorkOrderDisposition] = []
    for e in repo.wo_events(conn, wo_id):
        has_content = any(
            e[k] is not None
            for k in ("reported_cause", "action_taken", "liability", "note",
                      "material_cost", "labor_cost")
        )
        if not has_content:
            continue  # 纯生命周期事件（无内容派工/关闭）不作为处置（工具说明 §4）
        costs = [c for c in (e["material_cost"], e["labor_cost"]) if c is not None]
        out.append(
            WorkOrderDisposition(
                ts=datetime.fromisoformat(e["ts"]),
                technician_id=e["technician_id"],
                reported_cause=RootCauseEnum(e["reported_cause"])
                if e["reported_cause"] else None,
                action_taken=e["action_taken"],
                liability=LiabilityEnum(e["liability"]) if e["liability"] else None,
                note=e["note"],
                total_cost=sum(costs) if costs else None,
            )
        )
    return out


def query_workorder_history(
    ctx: ToolContext, inp: QueryWorkorderHistoryInput
) -> QueryWorkorderHistoryOutput:
    if inp.window not in VALID_WINDOWS:
        raise ToolFailure("invalid_input", f"window 非法：{inp.window}",
                          "允许 7d / 30d / 90d / 180d / 365d")
    exists = {
        "asset": lambda: repo.asset_get(ctx.conn, inp.id) is not None,
        "space": lambda: repo.space_get(ctx.conn, inp.id) is not None,
        "building": lambda: repo.building_exists(ctx.conn, inp.id),
        "tenant": lambda: repo.tenant_exists(ctx.conn, inp.id),
    }[inp.scope]()
    if not exists:
        raise ToolFailure("not_found", f"{inp.scope} 不存在：{inp.id}",
                          "换 scope 或先解析实体 ID")

    start = ctx.as_of - timedelta(days=VALID_WINDOWS[inp.window])
    rows = repo.wo_list_by_scope(ctx.conn, inp.scope, inp.id, start, ctx.as_of)
    if inp.symptom_filter is not None:
        rows = [r for r in rows if r["symptom"] == inp.symptom_filter.value]

    total = len(rows)
    truncated = total > WO_RETURN_LIMIT
    work_orders = [
        WorkOrder(
            wo_id=r["wo_id"],
            created_at=datetime.fromisoformat(r["created_at"]),
            space_id=r["space_id"],
            asset_id=r["asset_id"],
            raw_text=r["raw_text"],
            symptom=SymptomEnum(r["symptom"]) if r["symptom"] else None,
            urgency=r["urgency"],
            dispositions=_wo_dispositions(ctx.conn, r["wo_id"]),
            closed=any(e["event_type"] == "closed"
                       for e in repo.wo_events(ctx.conn, r["wo_id"])),
        )
        for r in rows[:WO_RETURN_LIMIT]
    ]
    return QueryWorkorderHistoryOutput(
        work_orders=work_orders, total_count=total, truncated=truncated
    )


# ═══════════════════════════════════════════════════════════════
# 4. recall_memory
# ═══════════════════════════════════════════════════════════════

def _check_scope_entity(ctx: ToolContext, scope_type: str, scope_id: str) -> None:
    ok = {
        "asset": lambda: repo.asset_get(ctx.conn, scope_id) is not None,
        "space": lambda: repo.space_get(ctx.conn, scope_id) is not None,
        "building": lambda: repo.building_exists(ctx.conn, scope_id),
        "tenant": lambda: repo.tenant_exists(ctx.conn, scope_id),
    }.get(scope_type, lambda: False)()
    if not ok:
        raise ToolFailure("not_found", f"{scope_type} 不存在：{scope_id}",
                          "确认作用域 ID 后重查")


def recall_memory(ctx: ToolContext, inp: RecallMemoryInput) -> RecallMemoryOutput:
    if not (inp.query or "").strip():
        raise ToolFailure("invalid_input", "query 不能为空")
    if inp.scope_type == "any" and inp.scope_id:
        raise ToolFailure("invalid_input", "scope_type=any 时不应传 scope_id")
    if inp.scope_type != "any" and not inp.scope_id:
        raise ToolFailure("invalid_input", f"scope_type={inp.scope_type} 必须同时给 scope_id")
    if inp.scope_type != "any":
        _check_scope_entity(ctx, inp.scope_type, inp.scope_id)

    try:
        qvec = ctx.embedder(inp.query)
    except Exception as e:  # 向量服务不可用
        raise ToolFailure("upstream_error", f"向量服务不可用：{e}") from e

    from wagent_backend.llm.embedder import cosine

    items: list[MemoryItem] = []
    for row in repo.insight_list(ctx.conn, inp.scope_type, inp.scope_id):
        gen = datetime.fromisoformat(row["generated_at"])
        if gen > ctx.as_of:
            continue  # 不得返回未来洞察（工具说明 §5）
        sim = cosine(qvec, jload(row["embedding"], []) or [])
        items.append(
            MemoryItem(
                insight_id=row["insight_id"],
                scope_type=row["scope_type"],
                scope_id=row["scope_id"],
                body_md=row["body_md"],
                predicted_root_cause=RootCauseEnum(row["predicted_root_cause"])
                if row["predicted_root_cause"] else None,
                confidence=row["confidence"],
                hit_count=row["hit_count"],
                trial_count=row["trial_count"],
                evidence_wo_ids=jload(row["evidence_wo_ids"], []),
                generated_at=gen,
                last_verified=datetime.fromisoformat(row["last_verified"])
                if row["last_verified"] else None,
                similarity=round(sim, 4),
            )
        )
    items.sort(key=lambda m: (-(m.similarity or 0), -m.confidence,
                              m.generated_at, m.insight_id))
    return RecallMemoryOutput(items=items[: inp.top_k])


# ═══════════════════════════════════════════════════════════════
# 5. write_memory
# ═══════════════════════════════════════════════════════════════

def write_memory(ctx: ToolContext, inp: WriteMemoryInput) -> WriteMemoryOutput:
    _check_scope_entity(ctx, inp.scope_type, inp.scope_id)

    latest = repo.latest_evidence_ts(ctx.conn, inp.evidence_wo_ids)
    if latest is None:
        raise ToolFailure("not_found", "存在不存在的证据工单",
                          "evidence_wo_ids 必须全部是历史工单 ID")
    if latest > ctx.as_of:
        raise ToolFailure("invalid_input", "时间旅行：证据工单晚于洞察生成时间",
                          "只能引用已发生（created_at <= 当前场景时间）的工单")

    try:
        vec = ctx.embedder(inp.body_md)
    except Exception as e:
        raise ToolFailure("upstream_error", f"向量服务不可用，写入中止：{e}") from e

    insight_id = repo.next_insight_id(ctx.conn)
    repo.insert_insight(
        ctx.conn, insight_id, inp.scope_type, inp.scope_id, inp.body_md, vec,
        inp.predicted_root_cause.value if inp.predicted_root_cause else None,
        inp.confidence, inp.evidence_wo_ids, ctx.as_of, inp.source,
    )
    return WriteMemoryOutput(insight_id=insight_id)


# ═══════════════════════════════════════════════════════════════
# 6. verify_memory_prediction
# ═══════════════════════════════════════════════════════════════

def verify_memory_prediction(
    ctx: ToolContext, inp: VerifyMemoryPredictionInput
) -> VerifyMemoryPredictionOutput:
    ins = repo.insight_get(ctx.conn, inp.insight_id)
    if ins is None:
        raise ToolFailure("not_found", f"洞察不存在：{inp.insight_id}")
    wo = repo.wo_get(ctx.conn, inp.wo_id)
    if wo is None:
        raise ToolFailure("not_found", f"工单不存在：{inp.wo_id}")
    if not any(e["event_type"] == "closed" for e in repo.wo_events(ctx.conn, inp.wo_id)):
        raise ToolFailure("invalid_input", "工单未闭环，不能验证",
                          "只能对已存在 closed 事件的工单回写结果")
    predicted = RootCauseEnum(ins["predicted_root_cause"]) if ins["predicted_root_cause"] else None
    if predicted is None:
        raise ToolFailure("invalid_input", "洞察没有 predicted_root_cause，无法验证")
    if repo.verification_exists(ctx.conn, inp.insight_id, inp.wo_id):
        raise ToolFailure("invalid_input", "同一洞察对同一工单重复验证")

    hit = predicted == inp.actual_root_cause
    before = float(ins["confidence"])
    after = before + VERIFY_HIT_GAIN * (1 - before) if hit else before * VERIFY_MISS_DECAY
    after = round(min(1.0, max(0.0, after)), 4)
    hit_count = ins["hit_count"] + (1 if hit else 0)
    trial_count = ins["trial_count"] + 1

    repo.insert_verification(
        ctx.conn, inp.insight_id, inp.wo_id, predicted.value,
        inp.actual_root_cause.value, hit, before, after, ctx.as_of,
    )
    repo.update_insight_stats(
        ctx.conn, inp.insight_id, after, hit_count, trial_count, ctx.as_of
    )
    moved = False
    if after < REVIEW_CONF_THRESHOLD:
        moved = repo.enqueue_review(
            ctx.conn, inp.insight_id, "low_confidence", ctx.as_of
        )
    return VerifyMemoryPredictionOutput(
        insight_id=inp.insight_id,
        hit=hit,
        confidence_before=before,
        confidence_after=after,
        hit_count=hit_count,
        trial_count=trial_count,
        moved_to_review_queue=moved,
    )


# ═══════════════════════════════════════════════════════════════
# 7. judge_liability
# ═══════════════════════════════════════════════════════════════

def judge_liability(ctx: ToolContext, inp: JudgeLiabilityInput) -> JudgeLiabilityOutput:
    if repo.space_get(ctx.conn, inp.space_id) is None:
        raise ToolFailure("not_found", f"空间不存在：{inp.space_id}")
    asset_row = None
    if inp.asset_id:
        asset_row = repo.asset_get(ctx.conn, inp.asset_id)
        if asset_row is None:
            raise ToolFailure("not_found", f"设备不存在：{inp.asset_id}")
    if inp.estimated_cost_cny is not None and inp.estimated_cost_cny < 0:
        raise ToolFailure("invalid_input", "estimated_cost_cny 不能为负")

    requires_human = False
    reason: list[str] = []
    clause_ids: list[str] = []
    clause_text: str | None = None
    hypo = inp.hypothesized_root_cause

    clauses = repo.clauses_valid(ctx.conn, inp.space_id, ctx.as_of.date())
    if hypo is not None:
        applicable = [c for c in clauses
                      if hypo.value in (jload(c["applies_to_root_causes"], []) or [])]
        distinct = {c["determines_liability"] for c in applicable}
        if len(distinct) > 1:
            # 条款冲突：可解释的业务结果，不是系统错误（工具说明 §8）
            clause_ids = [c["clause_id"] for c in applicable]
            clause_text = " ‖ ".join(c["text"] for c in applicable)
            return JudgeLiabilityOutput(
                liability=LiabilityEnum.UNCLEAR,
                basis="no_basis",
                clause_ids=clause_ids,
                clause_text=clause_text,
                estimated_cost_cny=inp.estimated_cost_cny,
                requires_human=True,
                requires_human_reason="合同条款冲突，无法判责",
            )
        if len(distinct) == 1:
            c = applicable[0]
            return JudgeLiabilityOutput(
                liability=LiabilityEnum(c["determines_liability"]),
                basis="contract_clause",
                clause_ids=[c["clause_id"]],
                clause_text=c["text"],
                estimated_cost_cny=inp.estimated_cost_cny,
                requires_human=(inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN,
                requires_human_reason=(
                    "预计费用超过 5000 元阈值"
                    if (inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN else None
                ),
            )

    # 无适用条款：保修/外包 → vendor 分叉（§14.7 已定案：basis 暂归 default_mapping）
    if asset_row is not None and asset_row["ownership"] == "外包":
        wu = asset_row["warranty_until"]
        if wu and wu >= ctx.as_of.date().isoformat():
            return JudgeLiabilityOutput(
                liability=LiabilityEnum.VENDOR,
                basis="default_mapping",
                clause_ids=[],
                clause_text=None,
                estimated_cost_cny=inp.estimated_cost_cny,
                requires_human=(inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN,
                requires_human_reason=(
                    "预计费用超过 5000 元阈值"
                    if (inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN else None
                ),
            )

    if hypo is not None and hypo in DEFAULT_LIABILITY:
        liability = DEFAULT_LIABILITY[hypo]
        return JudgeLiabilityOutput(
            liability=liability,
            basis="default_mapping",
            estimated_cost_cny=inp.estimated_cost_cny,
            requires_human=(inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN,
            requires_human_reason=(
                "预计费用超过 5000 元阈值"
                if (inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN else None
            ),
        )

    reason.append("无根因假设或无映射依据，无法判责")
    if (inp.estimated_cost_cny or 0) > COST_REQUIRES_HUMAN:
        reason.append("预计费用超过 5000 元阈值")
    return JudgeLiabilityOutput(
        liability=LiabilityEnum.UNCLEAR,
        basis="no_basis",
        estimated_cost_cny=inp.estimated_cost_cny,
        requires_human=True,
        requires_human_reason="；".join(reason) or None,
    )


# ═══════════════════════════════════════════════════════════════
# 8. create_workorder
# ═══════════════════════════════════════════════════════════════

def _blank_to_none(v: str | None) -> str | None:
    """模型常把「无」写成 "" / "None" / "null" —— 归一化为 None，避免外键误撞空串。"""
    if v is None:
        return None
    s = str(v).strip()
    return None if s.lower() in ("", "none", "null") else s


def create_workorder(ctx: ToolContext, inp: CreateWorkorderInput) -> CreateWorkorderOutput:
    # 2026-08-27 起 space_id 可空：全盘接受报修，无法定位也先建单
    inp = inp.model_copy(update={
        "space_id": _blank_to_none(inp.space_id),
        "asset_id": _blank_to_none(inp.asset_id),
        "assigned_technician_id": _blank_to_none(inp.assigned_technician_id),
    })
    if inp.space_id is not None and repo.space_get(ctx.conn, inp.space_id) is None:
        raise ToolFailure("not_found", f"空间不存在：{inp.space_id}")
    if not (inp.raw_text or "").strip():
        raise ToolFailure("invalid_input", "raw_text 不能为空")
    if inp.asset_id:
        if inp.space_id is None:
            raise ToolFailure("invalid_input",
                              "关联设备前必须先确定空间（space_id）",
                              "先解析/补充空间，或不带 asset_id 建单")
        if repo.asset_get(ctx.conn, inp.asset_id) is None:
            raise ToolFailure("not_found", f"设备不存在：{inp.asset_id}")
        serving = {r["asset_id"] for r in
                   repo.assets_serving(ctx.conn, inp.space_id, ctx.as_of)}
        if inp.asset_id not in serving:
            raise ToolFailure("invalid_input",
                              f"设备 {inp.asset_id} 与空间 {inp.space_id} 无当前有效服务关系",
                              "核对 asset_id，或用 get_assets_serving_space 查询")
    if inp.assigned_technician_id and repo.technician_get(
        ctx.conn, inp.assigned_technician_id
    ) is None:
        raise ToolFailure("not_found", f"技工不存在：{inp.assigned_technician_id}")
    # 建单前确定性查重：同空间同症状 90 天内已有工单 → 随返回注入给模型，
    # 复发判定不再依赖租户说「又」字（2026-08-31 需求）。
    # 先算出来：证据单号校验失败的 hint 也要带这份清单，让模型一步自纠
    repeats: list[str] = []
    repeat_hint = None
    if inp.space_id is not None:
        repeats = [
            w["wo_id"] for w in repo.wo_list_by_scope(
                ctx.conn, "space", inp.space_id,
                ctx.as_of - timedelta(days=90), ctx.as_of)
            if w["symptom"] == inp.symptom.value
        ]
        if repeats:
            repeat_hint = (
                f"该位置 90 天内已有 {len(repeats)} 张同类工单（{inp.symptom.value}）："
                f"{'、'.join(repeats)}。请评估是否复发——若是，Decision.is_repeat_fault=true "
                f"且 repeat_evidence 填上述单号。"
            )

    for wo_id in inp.evidence_wo_ids:
        if repo.wo_get(ctx.conn, wo_id) is None:
            raise ToolFailure(
                "not_found", f"证据工单不存在：{wo_id}",
                "evidence_wo_ids 必须逐字取自工具返回的单号，不要凭记忆拼写。"
                + (f"该位置 90 天内同症状工单：{'、'.join(repeats)}" if repeats
                   else "可先 query_workorder_history 查该空间的真实单号"))

    wo_id = repo.next_wo_id(ctx.conn, ctx.as_of)
    repo.insert_workorder(
        ctx.conn, wo_id, ctx.as_of, inp.space_id, inp.asset_id, None,
        inp.raw_text, inp.symptom.value, inp.urgency,
    )
    if inp.assigned_technician_id:
        repo.insert_wo_event(
            ctx.conn, wo_id, ctx.as_of, "dispatched",
            technician_id=inp.assigned_technician_id, note=inp.briefing_note,
        )
    # Agent 审计信息 → event_log.payload（工具说明 §9 数据模型缺口的处理建议）
    repo.insert_event_log(
        ctx.conn, ctx.as_of, "agent",
        {
            "kind": "workorder_created",
            "wo_id": wo_id,
            "hypothesized_root_cause": inp.hypothesized_root_cause.value
            if inp.hypothesized_root_cause else None,
            "recommended_action": inp.recommended_action.value
            if inp.recommended_action else None,
            "liability": inp.liability.value if inp.liability else None,
            "evidence_wo_ids": inp.evidence_wo_ids,
            "briefing_note": inp.briefing_note,
            "suggested_team": suggest_team(inp.symptom),
        },
        asset_id=inp.asset_id, space_id=inp.space_id,
    )
    return CreateWorkorderOutput(wo_id=wo_id, repeat_evidence=repeats,
                                 repeat_hint=repeat_hint)


# ═══════════════════════════════════════════════════════════════
# 9. find_technician
# ═══════════════════════════════════════════════════════════════

def find_technician(ctx: ToolContext, inp: FindTechnicianInput) -> FindTechnicianOutput:
    if not (inp.skill or "").strip():
        raise ToolFailure("invalid_input", "skill 不能为空")
    bld = repo.resolve_building_hint(ctx.conn, inp.building_id)
    if bld is None:
        raise ToolFailure(
            "not_found", f"楼栋不存在：{inp.building_id}",
            "building_id 用 BLD-A / BLD-B，或楼栋名称（A栋/B座）",
        )

    at = inp.at or ctx.as_of
    daytime = 8 <= at.hour < 20
    want_cert = inp.certification.strip() if inp.certification else None

    out: list[Technician] = []
    for r in repo.technicians_all(ctx.conn):
        skills = [s.upper() for s in jload(r["skills"], [])]
        certs = jload(r["certification"], []) or []
        if inp.skill.upper() not in skills:
            continue
        if want_cert and want_cert not in certs:
            continue
        shift = r["shift"]
        out.append(
            Technician(
                technician_id=r["technician_id"],
                name=r["name"],
                skills=jload(r["skills"], []),
                certification=certs,
                home_building=r["home_building"],
                shift=shift,
                available=(shift == ("day" if daytime else "night")),
                eta_minutes=None,  # 无可靠 ETA 数据，不编造（工具说明 §10）
            )
        )
    out.sort(key=lambda t: (not t.available, t.home_building != bld,
                            t.technician_id))
    return FindTechnicianOutput(technicians=out)


# ═══════════════════════════════════════════════════════════════
# 10. notify（确定性模拟发送 + 可审计回执）
# ═══════════════════════════════════════════════════════════════

def notify(ctx: ToolContext, inp: NotifyInput) -> NotifyOutput:
    if not (inp.message or "").strip():
        raise ToolFailure("invalid_input", "message 不能为空")
    if inp.recipient_role == "tenant_contact":
        if repo.contact_get(ctx.conn, inp.recipient_id) is None:
            raise ToolFailure("not_found", f"联系人不存在：{inp.recipient_id}")
    elif inp.recipient_role == "technician":
        if repo.technician_get(ctx.conn, inp.recipient_id) is None:
            raise ToolFailure("not_found", f"技工不存在：{inp.recipient_id}")
    elif inp.recipient_role == "facility_manager":
        if inp.recipient_id not in FACILITY_MANAGERS:
            raise ToolFailure("not_found", f"设施经理不存在：{inp.recipient_id}",
                              f"可用：{', '.join(FACILITY_MANAGERS)}")
    if inp.wo_id and repo.wo_get(ctx.conn, inp.wo_id) is None:
        raise ToolFailure("not_found", f"工单不存在：{inp.wo_id}")

    seq = repo.event_log_seq(ctx.conn, f"notify:{inp.channel}", "RCPT-")
    receipt_id = f"RCPT-{seq:04d}"
    repo.insert_event_log(
        ctx.conn, ctx.as_of, f"notify:{inp.channel}",
        {
            "kind": "notify_receipt",
            "receipt_id": receipt_id,
            "channel": inp.channel,
            "recipient_role": inp.recipient_role,
            "recipient_id": inp.recipient_id,
            "message": inp.message,
            "wo_id": inp.wo_id,
            "delivered_at": iso(ctx.as_of),
        },
    )
    return NotifyOutput(receipt_id=receipt_id, delivered_at=ctx.as_of)


# ═══════════════════════════════════════════════════════════════
# 11. escalate_to_human
# ═══════════════════════════════════════════════════════════════

def escalate_to_human(ctx: ToolContext, inp: EscalateToHumanInput) -> EscalateToHumanOutput:
    if not (inp.detail or "").strip():
        raise ToolFailure("invalid_input", "detail 不能为空", "写明具体升级原因")
    if inp.space_id and repo.space_get(ctx.conn, inp.space_id) is None:
        raise ToolFailure("not_found", f"空间不存在：{inp.space_id}")
    if inp.asset_id and repo.asset_get(ctx.conn, inp.asset_id) is None:
        raise ToolFailure("not_found", f"设备不存在：{inp.asset_id}")
    if inp.wo_id and repo.wo_get(ctx.conn, inp.wo_id) is None:
        raise ToolFailure("not_found", f"工单不存在：{inp.wo_id}")

    seq = repo.event_log_seq(ctx.conn, "escalation", "TKT-")
    ticket_id = f"TKT-{seq:04d}"
    repo.insert_event_log(
        ctx.conn, ctx.as_of, "escalation",
        {
            "kind": "escalation_ticket",
            "ticket_id": ticket_id,
            "reason": inp.reason,
            "detail": inp.detail,
            "space_id": inp.space_id,
            "asset_id": inp.asset_id,
            "wo_id": inp.wo_id,
            "created_at": iso(ctx.as_of),
        },
        asset_id=inp.asset_id, space_id=inp.space_id,
    )
    return EscalateToHumanOutput(ticket_id=ticket_id)
