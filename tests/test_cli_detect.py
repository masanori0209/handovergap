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
    assert "Retrieval Mode: ask_first" in result.output
    assert "Safety Policy: strict" in result.output
    assert "Recommended Action: block" in result.output
    assert "Applied Action: block" in result.output
    assert "Next Step: block" in result.output


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


def test_detect_cli_supports_followup_retrieval_mode() -> None:
    result = CliRunner().invoke(
        app,
        [
            "detect",
            "--scenario",
            "S001",
            "--profile",
            "CS",
            "--retrieval-mode",
            "expand-before-ask",
        ],
    )

    assert result.exit_code == 0
    assert "Retrieval Mode: expand_before_ask" in result.output
    assert "Recommended Action: retrieve_more" in result.output
    assert "Applied Action: retrieve_more" in result.output
    assert "Next Step: run_followup_retrieval" in result.output
    assert "Follow-up Retrieval Queries:" in result.output


def test_detect_cli_supports_safety_policy() -> None:
    result = CliRunner().invoke(
        app,
        [
            "detect",
            "--scenario",
            "S001",
            "--profile",
            "CS",
            "--safety-policy",
            "balanced",
        ],
    )

    assert result.exit_code == 0
    assert "Safety Policy: balanced" in result.output


def test_detect_cli_rejects_unknown_deployment_mode() -> None:
    result = CliRunner().invoke(
        app,
        ["detect", "--scenario", "S001", "--profile", "CS", "--deployment-mode", "audit-only"],
    )

    assert result.exit_code == 2


def test_detect_cli_rejects_unknown_retrieval_mode() -> None:
    result = CliRunner().invoke(
        app,
        ["detect", "--scenario", "S001", "--profile", "CS", "--retrieval-mode", "search-forever"],
    )

    assert result.exit_code == 2


def test_detect_cli_rejects_unknown_safety_policy() -> None:
    result = CliRunner().invoke(
        app,
        ["detect", "--scenario", "S001", "--profile", "CS", "--safety-policy", "reckless"],
    )

    assert result.exit_code == 2
