from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "examples" / "claim_followup_questions.py"
_SPEC = spec_from_file_location("claim_followup_questions", _EXAMPLE_PATH)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
review_claim = _MODULE.review_claim


def test_claim_followup_generates_second_round_questions() -> None:
    review = review_claim(
        [
            "I designed the rollout plan and owned the backend migration. "
            "The cost dashboard and monthly report showed the reduction."
        ]
    )

    assert review["action"] == "retrieve_more"
    assert review["gaps"] == ["scope_boundary", "constraints_tradeoffs"]
    assert any("Which parts were in your scope" in question for question in review["questions"])
    assert any(query["slot_name"] == "scope_boundary" for query in review["retrieval_queries"])


def test_claim_followup_allows_when_answer_fills_remaining_context() -> None:
    review = review_claim(
        [
            "I designed the rollout plan and owned the backend migration. "
            "The cost dashboard and monthly report showed the reduction.",
            "My scope was backend only; the data pipeline was handled by another team. "
            "The main tradeoff was temporary dual writes during migration.",
        ]
    )

    assert review["status"] == "transferable"
    assert review["action"] == "answer"
    assert review["gaps"] == []
    assert review["questions"] == []
