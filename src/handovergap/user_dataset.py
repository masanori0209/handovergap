from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from handovergap.schemas import GoldQuestion, HandoverGap, HandoverScenario
from handovergap.slot_rules import GAP_TYPE_BY_SLOT, HIGH_RISK_SLOTS, PROFILE_REQUIRED_SLOTS, QUESTION_BY_SLOT
from handovergap.store import InMemoryStore

ANNOTATION_COLUMNS = [
    "scenario_id",
    "profile",
    "memory_type",
    "task_context",
    "required_slots",
    "provided_slots",
    "evidence_slots",
    "gold_gap_slots",
    "gold_question_slots",
    "unsafe_transfer_label",
    "annotation_notes",
]


def load_user_dataset(path: str | Path, require_reviewed_labels: bool = True) -> InMemoryStore:
    source = Path(path)
    rows = _read_records(source)
    scenarios = []
    for index, row in enumerate(rows, start=1):
        try:
            scenarios.append(HandoverScenario.model_validate(_normalize_record(row, require_reviewed_labels)))
        except ValueError as exc:
            raise ValueError(f"Invalid scenario at row {index} in {source}: {exc}") from exc
        except ValidationError as exc:
            raise ValueError(f"Invalid scenario at row {index} in {source}: {exc.errors()[0]['msg']}") from exc
    if not scenarios:
        raise ValueError(f"No scenarios found in {source}.")
    return InMemoryStore(scenarios)


def export_annotation_template(input_path: str | Path, output_path: str | Path) -> int:
    scenarios = load_user_dataset(input_path, require_reviewed_labels=False).list_scenarios()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_COLUMNS)
        writer.writeheader()
        for scenario in scenarios:
            writer.writerow(_annotation_row(scenario))
    return len(scenarios)


def import_reviewed_labels(input_path: str | Path, labels_path: str | Path, output_path: str | Path) -> int:
    scenarios = load_user_dataset(input_path, require_reviewed_labels=False).list_scenarios()
    labels = _read_label_rows(labels_path)
    reviewed = []
    for scenario in scenarios:
        label = labels.get(scenario.scenario_id)
        if label is None:
            raise ValueError(f"No reviewed label row found for scenario '{scenario.scenario_id}'.")
        reviewed.append(_merge_labels(scenario, label))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w") as handle:
        for scenario in reviewed:
            handle.write(json.dumps(scenario.model_dump(), ensure_ascii=False) + "\n")
    return len(reviewed)


def _read_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        records = []
        with path.open() as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at line {line_number} in {path}: {exc.msg}") from exc
        return records
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text())
        if isinstance(payload, dict) and "scenarios" in payload:
            payload = payload["scenarios"]
        if not isinstance(payload, list):
            raise ValueError(f"JSON dataset must be a list or an object with a 'scenarios' list: {path}")
        return payload
    if path.suffix.lower() == ".csv":
        with path.open(newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported dataset format: {path}. Use .json, .jsonl, or .csv.")


def _normalize_record(row: dict[str, Any], require_reviewed_labels: bool) -> dict[str, Any]:
    normalized = dict(row)
    for key in ["provided_slots", "evidence_slots"]:
        normalized[key] = _parse_list(normalized.get(key))
    if "gold_gap_slots" in normalized and "gold_gaps" not in normalized:
        normalized["gold_gaps"] = [_gap_for_slot(slot) for slot in _parse_list(normalized.get("gold_gap_slots"))]
    if "gold_question_slots" in normalized and "gold_questions" not in normalized:
        normalized["gold_questions"] = [
            _question_for_slot(slot) for slot in _parse_list(normalized.get("gold_question_slots"))
        ]
    for key in ["evidence_events", "gold_gaps", "gold_questions", "slot_fill_profiles", "annotator_gap_slots"]:
        if isinstance(normalized.get(key), str):
            normalized[key] = _parse_json_field(normalized[key], default=[] if key != "slot_fill_profiles" else {})
    if "unsafe_transfer_label" in normalized and str(normalized["unsafe_transfer_label"]).strip():
        normalized["unsafe_transfer_label"] = _parse_bool(normalized["unsafe_transfer_label"])
    elif require_reviewed_labels:
        raise ValueError("Reviewed user datasets must include unsafe_transfer_label for every scenario.")
    else:
        normalized["unsafe_transfer_label"] = False
    return normalized


def _read_label_rows(path: str | Path) -> dict[str, dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() != ".csv":
        raise ValueError(f"Reviewed labels must be a CSV file: {source}")
    with source.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    labels = {}
    for row in rows:
        scenario_id = (row.get("scenario_id") or "").strip()
        if not scenario_id:
            raise ValueError(f"Reviewed label row is missing scenario_id in {source}.")
        labels[scenario_id] = row
    return labels


def _annotation_row(scenario: HandoverScenario) -> dict[str, str]:
    return {
        "scenario_id": scenario.scenario_id,
        "profile": scenario.profile,
        "memory_type": scenario.memory_type,
        "task_context": scenario.task_context,
        "required_slots": ";".join(PROFILE_REQUIRED_SLOTS.get(scenario.profile, [])),
        "provided_slots": ";".join(scenario.provided_slots),
        "evidence_slots": ";".join(scenario.evidence_slots),
        "gold_gap_slots": ";".join(gap.slot_name for gap in scenario.gold_gaps),
        "gold_question_slots": ";".join(question.slot_name for question in scenario.gold_questions),
        "unsafe_transfer_label": str(scenario.unsafe_transfer_label).lower(),
        "annotation_notes": scenario.annotation_notes or "",
    }


def _merge_labels(scenario: HandoverScenario, label: dict[str, Any]) -> HandoverScenario:
    gap_slots = _parse_list(label.get("gold_gap_slots"))
    question_slots = _parse_list(label.get("gold_question_slots")) or gap_slots
    unsafe = _parse_bool(label.get("unsafe_transfer_label"))
    notes = str(label.get("annotation_notes") or "").strip() or None
    return scenario.model_copy(
        update={
            "gold_gaps": [_gap_for_slot(slot) for slot in gap_slots],
            "gold_questions": [_question_for_slot(slot) for slot in question_slots],
            "unsafe_transfer_label": unsafe,
            "annotation_notes": notes,
            "annotator_gap_slots": {"reviewed": gap_slots},
        }
    )


def _gap_for_slot(slot: str) -> HandoverGap:
    severity = "HIGH" if slot in HIGH_RISK_SLOTS else "MEDIUM"
    return HandoverGap(
        gap_type=GAP_TYPE_BY_SLOT.get(slot, "context_gap"),
        slot_name=slot,
        description=f"Reviewer marked '{slot}' as missing for safe transfer.",
        severity=severity,
    )


def _question_for_slot(slot: str) -> GoldQuestion:
    return GoldQuestion(slot_name=slot, question=QUESTION_BY_SLOT.get(slot, f"What is the missing context for {slot}?"))


def _parse_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    if text.startswith("["):
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise ValueError(f"Expected a JSON list, got: {text}")
        return [str(item).strip() for item in parsed if str(item).strip()]
    separator = ";" if ";" in text else ","
    return [item.strip() for item in text.split(separator) if item.strip()]


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Expected boolean value, got: {value!r}")


def _parse_json_field(value: str, default: Any) -> Any:
    if not value.strip():
        return default
    return json.loads(value)
