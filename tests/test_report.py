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
    assert "Evaluation Integrity" in report
    assert "gold_gaps" in report


def test_report_cli_writes_markdown(tmp_path: Path) -> None:
    output_path = tmp_path / "evaluation.md"

    result = CliRunner().invoke(app, ["report", "--dataset", "mini", "--output", str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert "HandoverGap Evaluation Report" in output_path.read_text()
