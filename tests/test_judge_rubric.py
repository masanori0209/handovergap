from typer.testing import CliRunner

from handovergap import load_llm_judge_rubric
from handovergap.cli import app


def test_llm_judge_rubric_documents_allowed_and_forbidden_inputs() -> None:
    rubric = load_llm_judge_rubric()

    assert rubric["name"] == "handovergap_transferability_judge_v1"
    assert "gold_gaps" in rubric["forbidden_inputs"]
    assert "generated_retrieval_queries" in rubric["allowed_inputs"]
    assert "final_route" in rubric["output_schema"]
    assert "Use the judge only in evaluator/reporting code" in " ".join(rubric["bias_controls"])


def test_judge_rubric_cli_prints_json() -> None:
    result = CliRunner().invoke(app, ["judge-rubric"])

    assert result.exit_code == 0
    assert "handovergap_transferability_judge_v1" in result.output
    assert "forbidden_inputs" in result.output
