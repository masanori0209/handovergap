from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from handovergap.planning import FollowupRetrievalQuery, build_followup_retrieval_queries
from handovergap.schemas import DetectionResult

DeploymentMode = Literal["shadow", "soft", "hard"]
RetrievalMode = Literal["ask_first", "expand_before_ask"]
SafetyPolicy = Literal["strict", "balanced", "exploratory"]
RouteAction = Literal["answer", "retrieve_more", "ask", "block"]
NextStep = Literal["answer", "run_followup_retrieval", "ask_user", "block"]


class ProductRoute(BaseModel):
    status: Literal["transferable", "needs_clarification", "blocked"]
    action: RouteAction
    recommended_action: RouteAction
    deployment_mode: DeploymentMode = "hard"
    retrieval_mode: RetrievalMode = "ask_first"
    safety_policy: SafetyPolicy = "strict"
    enforcement: Literal["observe", "warn", "enforce"] = "enforce"
    should_interrupt: bool = True
    next_step: NextStep
    reason: list[str]
    questions: list[str]
    retrieval_queries: list[FollowupRetrievalQuery] = Field(default_factory=list)
    safe_context: str | None = None


def route_transferability_result(
    result: DetectionResult,
    *,
    safe_context: str | None = None,
    deployment_mode: DeploymentMode = "hard",
    retrieval_mode: RetrievalMode = "ask_first",
    safety_policy: SafetyPolicy = "strict",
    max_retrieval_queries: int = 3,
) -> ProductRoute:
    """Convert a DetectionResult into a product-facing answer/ask/block route."""

    if retrieval_mode not in {"ask_first", "expand_before_ask"}:
        raise ValueError(
            "Invalid retrieval_mode " f"'{retrieval_mode}'. Expected one of: ask_first, expand_before_ask."
        )
    if safety_policy not in {"strict", "balanced", "exploratory"}:
        raise ValueError(
            "Invalid safety_policy " f"'{safety_policy}'. Expected one of: strict, balanced, exploratory."
        )
    retrieval_queries = build_followup_retrieval_queries(result, max_queries=max_retrieval_queries)
    if result.transferability_status == "transferable":
        recommended_action: RouteAction = "answer"
    elif result.transferability_status == "needs_clarification":
        recommended_action = "retrieve_more" if retrieval_mode == "expand_before_ask" and retrieval_queries else "ask"
    elif result.transferability_status == "blocked":
        recommended_action = "retrieve_more" if retrieval_mode == "expand_before_ask" and retrieval_queries else "block"
    else:
        raise ValueError(
            "Invalid transferability_status "
            f"'{result.transferability_status}'. Expected one of: transferable, needs_clarification, blocked."
        )
    policy_reasons, policy_questions = _safety_policy_findings(result, safety_policy)
    if recommended_action == "answer" and policy_reasons:
        recommended_action = "ask"
    next_step = _next_step_for_action(recommended_action)
    if deployment_mode == "hard":
        action = recommended_action
        enforcement = "enforce"
        should_interrupt = action != "answer"
        routed_safe_context = safe_context if action == "answer" else None
    elif deployment_mode == "soft":
        action = "answer"
        enforcement = "warn"
        should_interrupt = False
        routed_safe_context = safe_context
    elif deployment_mode == "shadow":
        action = "answer"
        enforcement = "observe"
        should_interrupt = False
        routed_safe_context = safe_context
    else:
        raise ValueError("Invalid deployment_mode " f"'{deployment_mode}'. Expected one of: shadow, soft, hard.")

    return ProductRoute(
        status=result.transferability_status,
        action=action,
        recommended_action=recommended_action,
        deployment_mode=deployment_mode,
        retrieval_mode=retrieval_mode,
        safety_policy=safety_policy,
        enforcement=enforcement,
        should_interrupt=should_interrupt,
        next_step=next_step,
        reason=[gap.description for gap in result.gaps] + policy_reasons,
        questions=[question.question for question in result.questions] + policy_questions,
        retrieval_queries=retrieval_queries,
        safe_context=routed_safe_context,
    )


def _safety_policy_findings(result: DetectionResult, safety_policy: SafetyPolicy) -> tuple[list[str], list[str]]:
    if safety_policy != "strict":
        return [], []
    if not result.evidence_slots:
        return [], []

    supported_slots = set(result.evidence_slots)
    gap_slots = {gap.slot_name for gap in result.gaps}
    high_risk_slots = set(result.high_risk_slots)
    slots_needing_support = sorted(high_risk_slots - supported_slots - gap_slots)
    reasons = [
        f"High-risk slot '{slot}' is filled only by provided context; explicit evidence support is required."
        for slot in slots_needing_support
    ]
    questions = [
        f"Please provide explicit evidence supporting the high-risk slot '{slot}' before answering."
        for slot in slots_needing_support
    ]
    return reasons, questions


def _next_step_for_action(action: RouteAction) -> NextStep:
    if action == "answer":
        return "answer"
    if action == "retrieve_more":
        return "run_followup_retrieval"
    if action == "ask":
        return "ask_user"
    if action == "block":
        return "block"
    raise ValueError(f"Invalid route action '{action}'.")
