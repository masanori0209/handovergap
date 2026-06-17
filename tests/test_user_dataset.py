import csv
import json
from pathlib import Path

from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.user_dataset import export_annotation_template, import_reviewed_labels, load_user_dataset


def _write_unreviewed_dataset(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "scenario_id": "USER-001",
                "memory": "Use the reviewed CSV fallback for the anonymized account segment.",
                "evidence_events": [{"source_type": "note", "content": "Fallback exists, but escalation owner is not recorded."}],
                "profile": "CS",
                "memory_type": "decision",
                "task_context": "Answer a support question for an anonymized customer.",
                "provided_slots": ["scope"],
                "evidence_slots": ["fallback_plan"],
            }
        )
        + "\n"
    )


def test_export_annotation_template_omits_raw_memory(tmp_path: Path) -> None:
    dataset_path = tmp_path / "user.jsonl"
    template_path = tmp_path / "labels.csv"
    _write_unreviewed_dataset(dataset_path)

    count = export_annotation_template(dataset_path, template_path)

    assert count == 1
    text = template_path.read_text()
    assert "USER-001" in text
    assert "communication_status" in text
    assert "Use the reviewed CSV fallback" not in text
    assert "Fallback exists" not in text


def test_import_reviewed_labels_and_evaluate_user_dataset(tmp_path: Path) -> None:
    dataset_path = tmp_path / "user.jsonl"
    labels_path = tmp_path / "labels.csv"
    reviewed_path = tmp_path / "reviewed.jsonl"
    _write_unreviewed_dataset(dataset_path)
    export_annotation_template(dataset_path, labels_path)

    rows = list(csv.DictReader(labels_path.open()))
    rows[0]["gold_gap_slots"] = "communication_status;escalation_path"
    rows[0]["gold_question_slots"] = "communication_status;escalation_path"
    rows[0]["unsafe_transfer_label"] = "true"
    rows[0]["annotation_notes"] = "Reviewed after anonymization."
    with labels_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    count = import_reviewed_labels(dataset_path, labels_path, reviewed_path)
    store = load_user_dataset(reviewed_path)
    metrics_result = CliRunner().invoke(app, ["evaluate", "--dataset-file", str(reviewed_path), "--compare"])

    assert count == 1
    scenario = store.list_scenarios()[0]
    assert {gap.slot_name for gap in scenario.gold_gaps} == {"communication_status", "escalation_path"}
    assert scenario.annotator_gap_slots == {"reviewed": ["communication_status", "escalation_path"]}
    assert metrics_result.exit_code == 0
    assert "user dataset" in metrics_result.output
    assert "naive_rag" in metrics_result.output


def test_evaluate_user_dataset_requires_reviewed_labels(tmp_path: Path) -> None:
    dataset_path = tmp_path / "user.jsonl"
    _write_unreviewed_dataset(dataset_path)

    result = CliRunner().invoke(app, ["evaluate", "--dataset-file", str(dataset_path)])

    assert result.exit_code != 0
