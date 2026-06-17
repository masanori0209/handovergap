from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Literal

from pydantic import ValidationError

from handovergap.core.detector import HandoverGapDetector
from handovergap.profiles import ProfileCatalog
from handovergap.schemas import DetectionResult, EvidenceEvent, HandoverScenario
from handovergap.store import InMemoryStore


class TransferabilityGate:
    """Small public API for checking whether retrieved memory is ready to use."""

    def __init__(self, store: InMemoryStore | None = None, profiles: ProfileCatalog | None = None):
        self.store = store
        self.profiles = profiles or ProfileCatalog.builtins()

    @classmethod
    def from_builtin_dataset(cls, dataset: str = "mini") -> TransferabilityGate:
        return cls(store=InMemoryStore.from_builtin_dataset(dataset))

    @classmethod
    def from_profile_file(cls, path: str) -> TransferabilityGate:
        return cls(profiles=ProfileCatalog.from_yaml(path))

    def check(
        self,
        *,
        memory: str,
        profile: str,
        task_context: str,
        evidence: Iterable[str | dict[str, Any] | EvidenceEvent] = (),
        provided_slots: Iterable[str] = (),
        evidence_slots: Iterable[str] = (),
        scenario_id: str = "inline",
        memory_type: Literal["decision", "procedure", "risk", "task"] = "task",
    ) -> DetectionResult:
        scenario = HandoverScenario(
            scenario_id=scenario_id,
            memory=memory,
            evidence_events=[_coerce_evidence_event(item, index=index) for index, item in enumerate(evidence, start=1)],
            profile=profile,
            memory_type=memory_type,
            task_context=task_context,
            provided_slots=list(provided_slots),
            evidence_slots=list(evidence_slots),
            unsafe_transfer_label=False,
        )
        return self.check_scenario(scenario)

    def check_scenario(self, scenario: HandoverScenario) -> DetectionResult:
        store = self.store or InMemoryStore([scenario])
        return HandoverGapDetector(store=store, profiles=self.profiles).detect_scenario(scenario)

    def check_builtin(self, scenario_id: str, profile: str) -> DetectionResult:
        if self.store is None:
            store = InMemoryStore.from_builtin_dataset()
        else:
            store = self.store
        return HandoverGapDetector(store=store, profiles=self.profiles).detect(scenario_id=scenario_id, profile=profile)


ContextReadinessGate = TransferabilityGate


def _coerce_evidence_event(item: str | dict[str, Any] | EvidenceEvent, *, index: int) -> EvidenceEvent:
    if isinstance(item, EvidenceEvent):
        return item
    if isinstance(item, str):
        return EvidenceEvent(source_type="text", content=item)
    if not isinstance(item, dict):
        raise ValueError(
            f"Invalid evidence item at index {index}: expected a string, dict, or EvidenceEvent; "
            f"got {type(item).__name__}."
        )
    try:
        return EvidenceEvent.model_validate(item)
    except ValidationError as exc:
        missing = sorted(
            ".".join(str(part) for part in error["loc"])
            for error in exc.errors()
            if error["type"] == "missing"
        )
        detail = f" Missing required fields: {', '.join(missing)}." if missing else ""
        raise ValueError(
            f"Invalid evidence item at index {index}: expected fields include 'source_type' and 'content'.{detail}"
        ) from exc
