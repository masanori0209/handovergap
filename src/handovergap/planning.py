from __future__ import annotations

from pydantic import BaseModel

from handovergap.schemas import DetectionResult


class FollowupRetrievalQuery(BaseModel):
    slot_name: str
    query: str
    question: str
    severity: str
    reason: str


def build_followup_retrieval_queries(
    result: DetectionResult,
    *,
    max_queries: int = 3,
) -> list[FollowupRetrievalQuery]:
    """Turn detected missing slots into bounded follow-up retrieval queries."""

    question_by_slot = {question.slot_name: question.question for question in result.questions}
    queries: list[FollowupRetrievalQuery] = []
    seen_slots: set[str] = set()

    for gap in result.gaps:
        if gap.slot_name in seen_slots:
            continue
        seen_slots.add(gap.slot_name)
        question = question_by_slot.get(gap.slot_name, f"What evidence confirms {gap.slot_name}?")
        query = (
            f"profile={result.profile}; task={result.task_context}; "
            f"missing_slot={gap.slot_name}; evidence_needed={gap.description}; "
            f"clarification_question={question}"
        )
        queries.append(
            FollowupRetrievalQuery(
                slot_name=gap.slot_name,
                query=query,
                question=question,
                severity=gap.severity,
                reason=gap.description,
            )
        )
        if len(queries) >= max_queries:
            break

    return queries
