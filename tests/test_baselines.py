from handovergap.core.baselines import HybridRAGBaseline, NaiveRAGBaseline
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.store import InMemoryStore


def test_naive_rag_baseline_does_not_detect_transfer_gaps() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")

    prediction = NaiveRAGBaseline().predict(scenario)

    assert prediction.method == "naive_rag"
    assert prediction.gap_slots == set()
    assert prediction.question_slots == set()
    assert prediction.blocked is False


def test_hybrid_rag_baseline_detects_only_one_explicit_risk() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")

    prediction = HybridRAGBaseline().predict(scenario)

    assert prediction.method == "hybrid_rag"
    assert prediction.gap_slots == {"communication_status"}
    assert prediction.question_slots == {"communication_status"}
    assert prediction.blocked is True


def test_compare_keeps_article_ready_method_order() -> None:
    rows = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset()).compare()

    assert [row.method for row in rows] == ["naive_rag", "hybrid_rag", "handovergap"]
    assert rows[0].tacit_gap_recall < rows[1].tacit_gap_recall < rows[2].tacit_gap_recall
