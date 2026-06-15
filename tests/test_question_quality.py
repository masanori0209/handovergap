from handovergap.question_quality import evaluate_question_quality
from handovergap.schemas import ClarificationQuestion


def test_question_quality_scores_actionable_non_duplicate_questions() -> None:
    metrics = evaluate_question_quality(
        [
            ClarificationQuestion(slot_name="authority", question="Who is authorized to answer the customer?"),
            ClarificationQuestion(slot_name="fallback_plan", question="What should happen if CSV import fails?"),
        ],
        {"authority", "fallback_plan"},
    )

    assert metrics.slot_coverage == 1.0
    assert metrics.actionability == 1.0
    assert metrics.redundancy_rate == 0.0


def test_question_quality_flags_vague_and_duplicate_questions() -> None:
    metrics = evaluate_question_quality(
        [
            ClarificationQuestion(slot_name="authority", question="Please clarify"),
            ClarificationQuestion(slot_name="authority", question="Please clarify"),
        ],
        {"authority", "fallback_plan"},
    )

    assert metrics.slot_coverage == 0.5
    assert metrics.actionability == 0.0
    assert metrics.redundancy_rate == 0.5
