from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from handovergap.schemas import HandoverScenario
from handovergap.slot_rules import HIGH_RISK_SLOTS, ROLE_REQUIRED_SLOTS


@dataclass(frozen=True)
class BaselinePrediction:
    method: str
    gap_slots: set[str]
    question_slots: set[str]
    blocked: bool
    rationale: str


class BaselineMethod(Protocol):
    method: str

    def predict(self, scenario: HandoverScenario) -> BaselinePrediction:
        ...


class NaiveRAGBaseline:
    method = "naive_rag"

    def predict(self, scenario: HandoverScenario) -> BaselinePrediction:
        return BaselinePrediction(
            method=self.method,
            gap_slots=set(),
            question_slots=set(),
            blocked=False,
            rationale="Returns the retrieved memory as an answer without checking transferability.",
        )


class HybridRAGBaseline:
    method = "hybrid_rag"

    def predict(self, scenario: HandoverScenario) -> BaselinePrediction:
        slots = _first_evidence_missing_required_slot(scenario)
        return BaselinePrediction(
            method=self.method,
            gap_slots=slots,
            question_slots=slots,
            blocked=bool(slots & HIGH_RISK_SLOTS),
            rationale="Adds evidence context and can flag one explicit risk, but does not fill profile-required slots.",
        )


BASELINES: dict[str, BaselineMethod] = {
    NaiveRAGBaseline.method: NaiveRAGBaseline(),
    HybridRAGBaseline.method: HybridRAGBaseline(),
}


def _first_evidence_missing_required_slot(scenario: HandoverScenario) -> set[str]:
    required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
    for slot in required_slots:
        if slot not in scenario.evidence_slots:
            return {slot}
    return set()
