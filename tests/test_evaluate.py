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
