from __future__ import annotations

from handovergap.core.baselines import BASELINES, BaselinePrediction
from handovergap.core.detector import HandoverGapDetector
from handovergap.schemas import EvalMetrics
from handovergap.store import InMemoryStore


class HandoverGapEvaluator:
    def __init__(self, store: InMemoryStore, slot_profile: str = "provided"):
        self.store = store
        self.slot_profile = slot_profile

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
        safe_total = 0
        safe_allowed = 0
        safe_with_clarification = 0
        blocked_total = 0
        blocked_unsafe = 0

        for scenario in scenarios:
            profiled_scenario = _scenario_for_profile(scenario, self.slot_profile)
            prediction = self._predict(method, profiled_scenario)
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
            else:
                safe_total += 1
                if not prediction.blocked:
                    safe_allowed += 1
                if prediction.question_slots:
                    safe_with_clarification += 1
            if prediction.blocked:
                blocked_total += 1
                if scenario.unsafe_transfer_label:
                    blocked_unsafe += 1

        return EvalMetrics(
            method=method,
            scenarios=len(scenarios),
            tacit_gap_recall=_ratio(detected_gold_gaps, total_gold_gaps),
            unsafe_transfer_prevention=_ratio(unsafe_blocked, unsafe_total),
            question_coverage=_ratio(covered_gold_questions, total_gold_questions),
            safe_transfer_allowance=_ratio(safe_allowed, safe_total),
            blocked_precision=_ratio(blocked_unsafe, blocked_total),
            false_clarification_rate=_ratio(safe_with_clarification, safe_total),
        )

    def _predict(self, method: str, scenario) -> BaselinePrediction:
        if method in BASELINES:
            return BASELINES[method].predict(scenario)
        if method == "handovergap":
            result = HandoverGapDetector(store=self.store).detect_scenario(scenario)
            return BaselinePrediction(
                method=method,
                gap_slots={gap.slot_name for gap in result.gaps},
                question_slots={question.slot_name for question in result.questions},
                blocked=result.transferability_status != "transferable",
                rationale=(
                    "Performs profile-conditioned slot filling and blocks unsafe transfer "
                    "when required slots are missing."
                ),
            )
        raise ValueError(f"Unknown evaluation method: {method}")


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _scenario_for_profile(scenario, slot_profile: str):
    if slot_profile == "provided":
        return scenario
    try:
        provided_slots = scenario.slot_fill_profiles[slot_profile]
    except KeyError as exc:
        if not scenario.slot_fill_profiles:
            return scenario
        available = ", ".join(["provided", *scenario.slot_fill_profiles])
        raise ValueError(
            f"Scenario {scenario.scenario_id} has no slot fill profile '{slot_profile}'. Available: {available}"
        ) from exc
    return scenario.model_copy(update={"provided_slots": provided_slots})
