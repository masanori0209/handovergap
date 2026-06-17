from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from handovergap.schemas import DetectionResult


class ProductRoute(BaseModel):
    status: Literal["transferable", "needs_clarification", "blocked"]
    action: Literal["answer", "ask", "block"]
    reason: list[str]
    questions: list[str]
    safe_context: str | None = None


def route_transferability_result(
    result: DetectionResult,
    *,
    safe_context: str | None = None,
) -> ProductRoute:
    """Convert a DetectionResult into a product-facing answer/ask/block route."""

    if result.transferability_status == "transferable":
        action = "answer"
        routed_safe_context = safe_context
    elif result.transferability_status == "needs_clarification":
        action = "ask"
        routed_safe_context = None
    else:
        action = "block"
        routed_safe_context = None

    return ProductRoute(
        status=result.transferability_status,
        action=action,
        reason=[gap.description for gap in result.gaps],
        questions=[question.question for question in result.questions],
        safe_context=routed_safe_context,
    )
