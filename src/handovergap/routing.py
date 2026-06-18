from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from handovergap.schemas import DetectionResult

DeploymentMode = Literal["shadow", "soft", "hard"]
RouteAction = Literal["answer", "ask", "block"]


class ProductRoute(BaseModel):
    status: Literal["transferable", "needs_clarification", "blocked"]
    action: RouteAction
    recommended_action: RouteAction
    deployment_mode: DeploymentMode = "hard"
    enforcement: Literal["observe", "warn", "enforce"] = "enforce"
    should_interrupt: bool = True
    reason: list[str]
    questions: list[str]
    safe_context: str | None = None


def route_transferability_result(
    result: DetectionResult,
    *,
    safe_context: str | None = None,
    deployment_mode: DeploymentMode = "hard",
) -> ProductRoute:
    """Convert a DetectionResult into a product-facing answer/ask/block route."""

    if result.transferability_status == "transferable":
        recommended_action: RouteAction = "answer"
    elif result.transferability_status == "needs_clarification":
        recommended_action = "ask"
    elif result.transferability_status == "blocked":
        recommended_action = "block"
    else:
        raise ValueError(
            "Invalid transferability_status "
            f"'{result.transferability_status}'. Expected one of: transferable, needs_clarification, blocked."
        )
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
        enforcement=enforcement,
        should_interrupt=should_interrupt,
        reason=[gap.description for gap in result.gaps],
        questions=[question.question for question in result.questions],
        safe_context=routed_safe_context,
    )
