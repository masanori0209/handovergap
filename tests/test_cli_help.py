from typer.testing import CliRunner

from handovergap.cli import app


def test_cli_help() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Detect tacit context gaps" in result.output
    assert "demo" in result.output
    assert "detect" in result.output
    assert "evaluate" in result.output
    assert "schema" in result.output
    assert "audit-sql" in result.output
    assert "audit-example" in result.output
    assert "audit-benchmark" in result.output
    assert "serve" in result.output
