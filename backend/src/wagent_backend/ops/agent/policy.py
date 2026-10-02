"""policy —— 确定性策略（模型不参与，基线 §10）。

前置：报修文本命中 SAFETY_PRECHECK_KEYWORDS 即直接走 escalate 路径，
不进入 LLM 推理。

后置：judge_liability 判"必须人工"时的硬停强制升级，但只限两类确定性场景
（金额超阈 / 条款真冲突）；「无根因可判」不硬停（日常保洁/秩序事项没有
判责对象，见 judge_liability_escalation docstring）。

另有 create_workorder 后置硬停：同空间同症状的未闭环工单堆到阈值、
租户还在报同一问题 → 强制转人工（repeat_failure_2x）。

这是「确定性规则优先于模型判断」的演示点之一。
"""

from __future__ import annotations

from wagent_backend.ops.contracts.enums import SAFETY_PRECHECK_KEYWORDS
from wagent_backend.ops.tools.impl import COST_REQUIRES_HUMAN

# 同空间同症状「未闭环」工单达 3 张、租户再次报修同一问题 → 强制转人工。
# 只数未闭环：故事线种子的历史工单均已闭环，首报节拍（检出复发 → 治本建议）
# 不受影响；演示现场连续重复提报时，第 4 张单落地即触发。
REPEAT_OPEN_REQUIRES_HUMAN = 3


def safety_hit(text: str) -> str | None:
    """返回命中的第一个关键词；未命中返回 None。"""
    for kw in SAFETY_PRECHECK_KEYWORDS:
        if kw in text:
            return kw
    return None


def judge_liability_escalation(result: dict) -> tuple[str, str] | None:
    """judge_liability 结果的后置硬停规则。

    requires_human=true 时才考虑硬停，且只硬停两类确定性场景：
        金额超阈（estimated_cost_cny > 5000）→ cost_threshold
        条款真冲突（命中多条结论不一的有效条款，clause_ids 非空）→ contract_ambiguous
    「无根因假设、无映射依据」（basis=no_basis 且无命中条款）**不硬停** ——
    环境/秩序类日常事项本就没有责任判定对象（2026-08-27 全盘接受口径），
    由模型按提示词自行决定是否升级（requires_human 字段照常透传给模型）。
    只读结构化字段，不解析中文 reason 文案。
    """
    if result.get("requires_human") is not True:
        return None
    detail = result.get("requires_human_reason") or "judge_liability 判定需人工确认"
    cost = result.get("estimated_cost_cny")
    if cost is not None and cost > COST_REQUIRES_HUMAN:
        return "cost_threshold", detail
    if result.get("clause_ids"):
        return "contract_ambiguous", detail
    return None


def repeat_escalation(open_repeat_ids: list[str]) -> tuple[str, str] | None:
    """create_workorder 结果的后置硬停规则：同空间同症状未闭环工单堆单复发。

    open_repeat_ids = 同空间同症状、窗口内未闭环的其他工单号（不含刚建的那张）。
    只数未闭环单 —— 历史已闭环的复发链是「治本建议」的素材，不该硬停；
    未闭环还反复报，说明处置没被感知，人工必须介入。
    """
    if len(open_repeat_ids) >= REPEAT_OPEN_REQUIRES_HUMAN:
        return ("repeat_failure_2x",
                f"同位置同症状已有 {len(open_repeat_ids)} 张未闭环工单"
                f"（{'、'.join(open_repeat_ids)}），租户再次报修同一问题，"
                "强制升级人工复盘处置效率")
    return None
