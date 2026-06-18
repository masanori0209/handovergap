from typer.testing import CliRunner

from handovergap.cli import app


def test_detect_cli_prints_transferability_evidence() -> None:
    result = CliRunner().invoke(app, ["detect", "--scenario", "S001", "--profile", "CS"])

    assert result.exit_code == 0
    assert "Memory:" in result.output
    assert "Detected Gaps:" in result.output
    assert "communication_gap" in result.output
    assert "Clarification Questions:" in result.output
    assert "Transferability:" in result.output
    assert "blocked" in result.output
    assert "Product Route:" in result.output
    assert "Deployment Mode: hard" in result.output
    assert "Recommended Action: block" in result.output
    assert "Applied Action: block" in result.output


def test_detect_cli_supports_shadow_deployment_mode() -> None:
    result = CliRunner().invoke(
        app,
        ["detect", "--scenario", "S001", "--profile", "CS", "--deployment-mode", "shadow"],
    )

    assert result.exit_code == 0
    assert "Deployment Mode: shadow" in result.output
    assert "Recommended Action: block" in result.output
    assert "Applied Action: answer" in result.output
    assert "Enforcement: observe" in result.output
    assert "Should Interrupt: False" in result.output


def test_detect_cli_rejects_unknown_deployment_mode() -> None:
    result = CliRunner().invoke(
        app,
        ["detect", "--scenario", "S001", "--profile", "CS", "--deployment-mode", "audit-only"],
    )

    assert result.exit_code == 2
