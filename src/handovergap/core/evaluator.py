from __future__ import annotations

from handovergap.core.baselines import BASELINES, BaselinePrediction
from handovergap.core.detector import HandoverGapDetector
from handovergap.schemas import EvalMetrics
from handovergap.store import InMemoryStore


class HandoverGapEvaluator:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def compare(self) -> list[EvalMetrics]:
        return [
            self.evaluate_method("naive_rag"),
            self.evaluate_method("hybrid_rag"),
            self.evaluate_method("handovergap"),
        ]

    def evaluate_method(self, method: str = "handovergap") -> EvalMetrics:
        scenarios = self.store.list_scenarios()
        total_gold_gaps = 0
        detected_gold_gaps = 0
        unsafe_total = 0
        unsafe_blocked = 0
        total_gold_questions = 0
        covered_gold_questions = 0

        for scenario in scenarios:
            prediction = self._predict(method, scenario.scenario_id, scenario.successor_role)
            gold_slots = {gap.slot_name for gap in scenario.gold_gaps}
            gold_question_slots = {question.slot_name for question in scenario.gold_questions}

            total_gold_gaps += len(gold_slots)
            detected_gold_gaps += len(gold_slots & prediction.gap_slots)
            total_gold_questions += len(gold_question_slots)
            covered_gold_questions += len(gold_question_slots & prediction.question_slots)

            if scenario.unsafe_transfer_label:
                unsafe_total += 1
                if prediction.blocked:
                    unsafe_blocked += 1

        return EvalMetrics(
            method=method,
            scenarios=len(scenarios),
            tacit_gap_recall=_ratio(detected_gold_gaps, total_gold_gaps),
            unsafe_transfer_prevention=_ratio(unsafe_blocked, unsafe_total),
            question_coverage=_ratio(covered_gold_questions, total_gold_questions),
        )

    def _predict(self, method: str, scenario_id: str, role: str) -> BaselinePrediction:
        scenario = self.store.get_scenario(scenario_id, role)
        if method in BASELINES:
            return BASELINES[method].predict(scenario)
        if method == "handovergap":
            result = HandoverGapDetector(store=self.store).detect(scenario_id, role)
            return BaselinePrediction(
                method=method,
                gap_slots={gap.slot_name for gap in result.gaps},
                question_slots={question.slot_name for question in result.questions},
                blocked=result.transferability_status == "blocked",
                rationale=(
                    "Performs role-conditioned slot filling and blocks unsafe transfer "
                    "when required slots are missing."
                ),
            )
        raise ValueError(f"Unknown evaluation method: {method}")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
