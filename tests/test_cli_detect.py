from typer.testing import CliRunner

from handovergap.cli import app


def test_detect_cli_prints_transferability_evidence() -> None:
    result = CliRunner().invoke(app, ["detect", "--scenario", "S001", "--role", "CS"])

    assert result.exit_code == 0
    assert "Memory:" in result.output
    assert "Detected Gaps:" in result.output
    assert "communication_gap" in result.output
    assert "Clarification Questions:" in result.output
    assert "Transferability:" in result.output
    assert "blocked" in result.output
