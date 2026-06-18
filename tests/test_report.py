from pathlib import Path

from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.reporting import generate_evaluation_report


def test_generate_evaluation_report_contains_metrics_and_integrity() -> None:
    report = generate_evaluation_report("mini")

    assert "# HandoverGap Evaluation Report" in report
    assert "| mini | handovergap |" in report
    assert "Slot Fill Mode" in report
    assert "scenario.provided_slots" in report
    assert "Optional LLM slot filling must be labeled" in report
    assert "Question Quality" in report
    assert "Follow-up Retrieval Metrics" in report
    assert "Retrieve More Success" in report
    assert "Evaluation Integrity" in report
    assert "gold_gaps" in report


def test_report_cli_writes_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "evaluation.md"

    result = CliRunner().invoke(app, ["report", "--dataset", "mini", "--output", str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert "HandoverGap Evaluation Report" in output_path.read_text()


def test_report_cli_accepts_user_dataset_file(tmp_path: Path) -> None:
    dataset_path = tmp_path / "reviewed.jsonl"
    dataset_path.write_text(
        """
{"scenario_id":"USER-001","memory":"Use CSV fallback.","evidence_events":[],"profile":"CS","memory_type":"decision","task_context":"Support reply","provided_slots":["scope"],"evidence_slots":["fallback_plan"],"gold_gaps":[{"gap_type":"communication_gap","slot_name":"communication_status","description":"Missing communication status","severity":"HIGH"}],"gold_questions":[{"slot_name":"communication_status","question":"関係者または顧客には説明済みですか？"}],"unsafe_transfer_label":true}
""".strip()
        + "\n"
    )

    result = CliRunner().invoke(app, ["report", "--dataset-file", str(dataset_path)])

    assert result.exit_code == 0
    assert "user-provided local dataset" in result.output
    assert "| user | handovergap |" in result.output
