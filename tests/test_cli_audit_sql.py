from typer.testing import CliRunner

from handovergap.cli import app


def test_cli_audit_sql_prints_tidb_explanation_query() -> None:
    result = CliRunner().invoke(app, ["audit-sql"])

    assert result.exit_code == 0
    assert "Trace blocked transfer assessments" in result.output
    assert "FROM transfer_assessments ta" in result.output
    assert "LEFT JOIN slot_fill_attempts sfa" in result.output
    assert "LEFT JOIN clarification_questions cq" in result.output


def test_cli_audit_example_prints_blocked_transfer_rows() -> None:
    result = CliRunner().invoke(app, ["audit-example"])

    assert result.exit_code == 0
    assert "Example TiDB blocked-transfer audit result" in result.output
    assert "communication_status" in result.output
    assert "顧客にはAPI延期を説明済みですか？" in result.output


def test_cli_audit_benchmark_prints_materialization_summary() -> None:
    result = CliRunner().invoke(app, ["audit-benchmark", "--dataset", "holdout", "--iterations", "2"])

    assert result.exit_code == 0
    assert "Audit materialization benchmark" in result.output
    assert "dataset=holdout" in result.output
    assert "Context gap rows / run" in result.output
    assert "fallback_plan" in result.output
