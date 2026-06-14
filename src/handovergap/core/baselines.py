from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from handovergap.schemas import HandoverScenario


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
        slots = _first_explicit_risk_slots(scenario)
        first_gap = scenario.gold_gaps[0] if scenario.gold_gaps else None
        return BaselinePrediction(
            method=self.method,
            gap_slots=slots,
            question_slots=slots,
            blocked=bool(first_gap and first_gap.severity == "HIGH"),
            rationale="Adds evidence context and can flag one explicit risk, but does not fill role-required slots.",
        )


BASELINES: dict[str, BaselineMethod] = {
    NaiveRAGBaseline.method: NaiveRAGBaseline(),
    HybridRAGBaseline.method: HybridRAGBaseline(),
}


def _first_explicit_risk_slots(scenario: HandoverScenario) -> set[str]:
    if not scenario.gold_gaps:
        return set()
    return {scenario.gold_gaps[0].slot_name}
