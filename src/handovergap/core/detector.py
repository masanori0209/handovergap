from __future__ import annotations

from handovergap.profiles import ProfileCatalog
from handovergap.schemas import ClarificationQuestion, DetectionResult, HandoverGap
from handovergap.store import InMemoryStore


class HandoverGapDetector:
    """Deterministic profile-conditioned slot-gap detector for the MVP."""

    def __init__(self, store: InMemoryStore, profiles: ProfileCatalog | None = None):
        self.store = store
        self.profiles = profiles or ProfileCatalog.builtins()

    def detect(
        self,
        scenario_id: str,
        profile: str | None = None,
    ) -> DetectionResult:
        scenario = self.store.get_scenario(scenario_id=scenario_id, profile=profile)
        return self.detect_scenario(scenario)

    def detect_scenario(self, scenario) -> DetectionResult:
        required_slots = self.profiles.required_slots(scenario.profile)
        filled_slots = set(scenario.provided_slots) | set(scenario.evidence_slots)
        missing_slots = [slot for slot in required_slots if slot not in filled_slots]
        high_risk_slots = [
            slot for slot in required_slots if self.profiles.slot_policy(scenario.profile, slot).high_risk
        ]

        gaps = [
            HandoverGap(
                gap_type=self.profiles.slot_policy(scenario.profile, slot).gap_type or f"{slot}_gap",
                slot_name=slot,
                description=self.profiles.slot_policy(scenario.profile, slot).description or f"{slot} が不足しています",
                severity=self.profiles.slot_policy(scenario.profile, slot).severity,
            )
            for slot in missing_slots
        ]
        questions = [
            ClarificationQuestion(slot_name=slot, question=question)
            for slot in missing_slots
            if (question := self.profiles.slot_policy(scenario.profile, slot).question)
        ]
        transferability_score = max(0.0, 1.0 - (len(missing_slots) / max(len(required_slots), 1)))
        if not missing_slots:
            status = "transferable"
        elif any(self.profiles.slot_policy(scenario.profile, slot).high_risk for slot in missing_slots):
            status = "blocked"
        else:
            status = "needs_clarification"

        return DetectionResult(
            scenario_id=scenario.scenario_id,
            profile=scenario.profile,
            memory=scenario.memory,
            task_context=scenario.task_context,
            required_slots=required_slots,
            provided_slots=scenario.provided_slots,
            evidence_slots=scenario.evidence_slots,
            high_risk_slots=high_risk_slots,
            gaps=gaps,
            questions=questions,
            transferability_score=transferability_score,
            transferability_status=status,
        )
