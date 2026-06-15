from __future__ import annotations

from dataclasses import dataclass

from handovergap.schemas import ClarificationQuestion


@dataclass(frozen=True)
class QuestionQualityMetrics:
    questions: int
    unique_slots: int
    actionable_questions: int
    duplicate_questions: int
    slot_coverage: float
    actionability: float
    redundancy_rate: float


def evaluate_question_quality(
    questions: list[ClarificationQuestion],
    required_gap_slots: set[str],
) -> QuestionQualityMetrics:
    normalized_questions = [_normalize(question.question) for question in questions]
    duplicate_count = len(normalized_questions) - len(set(normalized_questions))
    question_slots = {question.slot_name for question in questions}
    actionable = sum(_is_actionable(question.question) for question in questions)
    return QuestionQualityMetrics(
        questions=len(questions),
        unique_slots=len(question_slots),
        actionable_questions=actionable,
        duplicate_questions=duplicate_count,
        slot_coverage=_ratio(len(question_slots & required_gap_slots), len(required_gap_slots)),
        actionability=_ratio(actionable, len(questions)),
        redundancy_rate=_ratio(duplicate_count, len(questions)),
    )


def _is_actionable(question: str) -> bool:
    stripped = question.strip()
    if not stripped:
        return False
    if not (stripped.endswith("?") or stripped.endswith("？")):
        return False
    vague_terms = {"確認してください", "教えてください", "Please clarify", "Clarify this"}
    return stripped not in vague_terms and len(stripped) >= 12


def _normalize(question: str) -> str:
    return " ".join(question.strip().lower().split())


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
