from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.store import InMemoryStore


def test_evaluator_scores_handovergap_above_baselines() -> None:
    evaluator = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset())
    rows = {metrics.method: metrics for metrics in evaluator.compare()}

    assert rows["handovergap"].scenarios >= 20
    assert rows["handovergap"].tacit_gap_recall > rows["hybrid_rag"].tacit_gap_recall
    assert rows["hybrid_rag"].tacit_gap_recall > rows["naive_rag"].tacit_gap_recall
    assert rows["handovergap"].unsafe_transfer_prevention == 1.0


def test_evaluate_cli_outputs_required_metrics() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--compare"])

    assert result.exit_code == 0
    assert "HandoverGapBench mini" in result.output
    assert "Tacit Gap Recall" in result.output
    assert "Unsafe Transfer Prevention" in result.output
    assert "Question Coverage" in result.output
    assert "Safe Transfer Allowance" in result.output


def test_holdout_optimistic_slot_filling_exposes_recall_drop() -> None:
    provided = HandoverGapEvaluator(
        store=InMemoryStore.from_builtin_dataset("holdout"),
        slot_profile="provided",
    ).evaluate_method("handovergap")
    optimistic = HandoverGapEvaluator(
        store=InMemoryStore.from_builtin_dataset("holdout"),
        slot_profile="optimistic",
    ).evaluate_method("handovergap")

    assert provided.tacit_gap_recall == 1.0
    assert optimistic.tacit_gap_recall < provided.tacit_gap_recall
    assert optimistic.unsafe_transfer_prevention == 1.0
    assert optimistic.safe_transfer_allowance == 1.0


def test_evaluate_cli_outputs_slot_filling_stress() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--dataset", "holdout", "--stress-filling"])

    assert result.exit_code == 0
    assert "slot filling stress" in result.output
    assert "handovergap/optimistic" in result.output
