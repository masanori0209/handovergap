from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from handovergap.schemas import EvidenceEvent, HandoverScenario


class SourceEventRecord(BaseModel):
    source_type: str
    content: str
    title: str | None = None
    source_url: str | None = None
    actor_name: str | None = None
    project_name: str | None = None
    occurred_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_evidence_event(self) -> EvidenceEvent:
        return EvidenceEvent(
            source_type=self.source_type,
            title=self.title,
            source_url=self.source_url,
            actor_name=self.actor_name,
            project_name=self.project_name,
            occurred_at=self.occurred_at,
            content=self.content,
            metadata=self.metadata,
        )


def load_source_events_jsonl(path: str | Path) -> list[SourceEventRecord]:
    records = []
    for line_number, line in enumerate(Path(path).read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
        try:
            records.append(SourceEventRecord.model_validate(payload))
        except ValidationError as exc:
            missing = sorted(
                ".".join(str(part) for part in error["loc"])
                for error in exc.errors()
                if error["type"] == "missing"
            )
            detail = f" Missing required fields: {', '.join(missing)}." if missing else ""
            raise ValueError(
                f"Invalid source event at line {line_number}: expected fields include 'source_type' and 'content'.{detail}"
            ) from exc
    return records


def scenario_from_jsonl(
    path: str | Path,
    *,
    scenario_id: str,
    memory: str,
    profile: str,
    task_context: str,
    memory_type: Literal["decision", "procedure", "risk", "task"] = "task",
    provided_slots: list[str] | None = None,
    evidence_slots: list[str] | None = None,
) -> HandoverScenario:
    return HandoverScenario(
        scenario_id=scenario_id,
        memory=memory,
        profile=profile,
        task_context=task_context,
        memory_type=memory_type,
        evidence_events=[record.to_evidence_event() for record in load_source_events_jsonl(path)],
        provided_slots=provided_slots or [],
        evidence_slots=evidence_slots or [],
        unsafe_transfer_label=False,
    )
