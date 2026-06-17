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
    assert rows["handovergap"].unsafe_transfer_prevention > rows["hybrid_rag"].unsafe_transfer_prevention
    assert rows["handovergap"].blocked_precision == 1.0


def test_evaluate_cli_outputs_required_metrics() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--compare"])

    assert result.exit_code == 0
    assert "HandoverGapBench mini" in result.output
    assert "slot-fill-mode=user_provided" in result.output
    assert "Slot fill summary" in result.output
    assert "scenario.provided_slots" in result.output
    assert "Tacit Gap" in result.output
    assert "Unsafe Transfer" in result.output
    assert "Question Cover" in result.output
    assert "Safe Transfer" in result.output
    assert "False Clarification" in result.output


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
    assert optimistic.unsafe_transfer_prevention == provided.unsafe_transfer_prevention
    assert optimistic.safe_transfer_allowance == 1.0


def test_evaluate_cli_outputs_slot_filling_stress() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--dataset", "holdout", "--stress-filling"])

    assert result.exit_code == 0
    assert "slot filling stress" in result.output
    assert "handovergap/optimist" in result.output
    assert "optional_llm" in result.output
    assert "simulated" in result.output


def test_evaluate_cli_requires_model_for_optional_llm_mode() -> None:
    result = CliRunner().invoke(app, ["evaluate", "--slot-fill-mode", "optional_llm"])

    assert result.exit_code == 2


def test_evaluate_cli_labels_optional_llm_mode() -> None:
    result = CliRunner().invoke(
        app,
        ["evaluate", "--slot-fill-mode", "optional_llm", "--model", "gpt-example", "--prompt-profile", "strict"],
    )

    assert result.exit_code == 0
    assert "optional_llm" in result.output
    assert "gpt-example" in result.output


def test_adversarial_dataset_exposes_false_clarifications_and_recall_drop() -> None:
    metrics = HandoverGapEvaluator(
        store=InMemoryStore.from_builtin_dataset("adversarial"),
        slot_profile="provided",
    ).evaluate_method("handovergap")

    assert metrics.tacit_gap_recall < 1.0
    assert metrics.false_clarification_rate == 0.0
    assert metrics.safe_transfer_allowance == 1.0


def test_sanitized_dataset_has_field_realistic_signal() -> None:
    metrics = HandoverGapEvaluator(
        store=InMemoryStore.from_builtin_dataset("sanitized"),
        slot_profile="provided",
    ).evaluate_method("handovergap")

    assert metrics.scenarios >= 6
    assert metrics.tacit_gap_recall >= 0.8
    assert metrics.false_clarification_rate == 0.0
