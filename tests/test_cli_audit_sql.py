from typer.testing import CliRunner

from handovergap.audit import diverse_audit_sample_rows
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


def test_diverse_audit_sample_rows_prefers_one_scenario_with_many_gaps() -> None:
    rows = [
        {"scenario_id": "W0099", "profile": "Sales", "slot_name": "customer_expectation", "severity": "MEDIUM", "question": "q1"},
        {"scenario_id": "W0099", "profile": "Sales", "slot_name": "timeline_confidence", "severity": "MEDIUM", "question": "q2"},
        {"scenario_id": "W0100", "profile": "CS", "slot_name": "authority", "severity": "HIGH", "question": "q3"},
        {"scenario_id": "W0100", "profile": "CS", "slot_name": "fallback_plan", "severity": "HIGH", "question": "q4"},
        {"scenario_id": "W0100", "profile": "CS", "slot_name": "scope", "severity": "MEDIUM", "question": "q5"},
        {"scenario_id": "W0095", "profile": "Engineer", "slot_name": "failure_modes", "severity": "MEDIUM", "question": "q6"},
    ]

    sample = diverse_audit_sample_rows(rows, limit=6)

    assert len(sample) == 6
    assert sum(1 for row in sample if row["scenario_id"] == "W0100") >= 3
    assert {row["profile"] for row in sample} == {"CS", "Sales", "Engineer"}
