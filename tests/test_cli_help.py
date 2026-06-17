from typer.testing import CliRunner

from handovergap.cli import app


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Detect profile-conditioned context gaps" in result.output
    assert "demo" in result.output
    assert "detect" in result.output
    assert "evaluate" in result.output
    assert "datasets" in result.output
    assert "profiles" in result.output
    assert "privacy-check" in result.output
    assert "ingest" in result.output
    assert "report" in result.output
    assert "schema" in result.output
    assert "audit-sql" in result.output
    assert "audit-example" in result.output
    assert "audit-benchmark" in result.output
    assert "retrieve-evidence" in result.output
    assert "workload-benchmark" in result.output
    assert "serve" in result.output


def test_cli_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == "0.1.20"
