from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.workload import benchmark_generated_workload, generate_workload_scenarios


def test_generate_workload_scenarios_creates_profile_mix() -> None:
    scenarios = generate_workload_scenarios(9)

    assert len(scenarios) == 9
    assert {scenario.profile for scenario in scenarios} == {"CS", "Engineer", "Sales"}


def test_benchmark_generated_workload_returns_row_counts() -> None:
    result = benchmark_generated_workload(count=12, iterations=2)

    assert result.scenarios == 12
    assert result.transfer_assessments_per_run == 12
    assert result.context_gaps_per_run > 0


def test_workload_benchmark_cli_runs() -> None:
    result = CliRunner().invoke(app, ["workload-benchmark", "--scenarios", "12", "--iterations", "1"])

    assert result.exit_code == 0
    assert "Generated workload benchmark" in result.output
    assert "not a TiDB latency claim" in result.output
