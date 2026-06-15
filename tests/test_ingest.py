import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.ingest import load_source_events_jsonl, scenario_from_jsonl


def test_load_source_events_jsonl() -> None:
    records = load_source_events_jsonl("examples/source_events/customer_escalation.jsonl")

    assert len(records) == 3
    assert records[0].source_type == "crm_note"
    assert records[1].metadata["issue_key"] == "DEMO-42"


def test_scenario_from_jsonl_maps_records_to_evidence_events() -> None:
    scenario = scenario_from_jsonl(
        "examples/source_events/customer_escalation.jsonl",
        scenario_id="J001",
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
    )

    assert scenario.scenario_id == "J001"
    assert len(scenario.evidence_events) == 3
    assert scenario.evidence_events[1].title == "API integration postponed"


def test_load_source_events_jsonl_reports_line_errors(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(json.dumps({"source_type": "issue"}) + "\n")

    with pytest.raises(ValueError, match="line 1"):
        load_source_events_jsonl(path)


def test_ingest_cli_runs_detection_from_jsonl() -> None:
    result = CliRunner().invoke(
        app,
        [
            "ingest",
            "examples/source_events/customer_escalation.jsonl",
            "--memory",
            "Use CSV for this release; API support is deferred.",
            "--profile",
            "CS",
            "--task-context",
            "Answer customer questions about the workaround.",
        ],
    )

    assert result.exit_code == 0
    assert "Loaded source events: 3" in result.output
    assert "Detected Gaps:" in result.output
