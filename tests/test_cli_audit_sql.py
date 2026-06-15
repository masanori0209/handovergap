from typer.testing import CliRunner

from handovergap.cli import app


def test_cli_audit_sql_prints_tidb_explanation_query() -> None:
    result = CliRunner().invoke(app, ["audit-sql"])

    assert result.exit_code == 0
    assert "Trace blocked transfer assessments" in result.output
    assert "FROM transfer_assessments ta" in result.output
    assert "LEFT JOIN slot_fill_attempts sfa" in result.output
    assert "LEFT JOIN clarification_questions cq" in result.output
