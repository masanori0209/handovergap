from __future__ import annotations

from handovergap.core.baselines import BASELINES, BaselinePrediction
from handovergap.core.detector import HandoverGapDetector
from handovergap.routing import route_transferability_result
from handovergap.schemas import EvalMetrics, FollowupRetrievalMetrics
from handovergap.slot_filling_modes import SlotFillMode, mode_for_slot_profile, source_for_slot_profile
from handovergap.store import InMemoryStore


class HandoverGapEvaluator:
    def __init__(
        self,
        store: InMemoryStore,
        slot_profile: str = "provided",
        slot_fill_mode: SlotFillMode | None = None,
        slot_fill_source: str | None = None,
        model_name: str | None = None,
        prompt_profile: str | None = None,
    ):
        self.store = store
        self.slot_profile = slot_profile
        self.slot_fill_mode = slot_fill_mode or mode_for_slot_profile(slot_profile)
        self.slot_fill_source = slot_fill_source or source_for_slot_profile(slot_profile)
        self.model_name = model_name
        self.prompt_profile = prompt_profile

    def compare(self) -> list[EvalMetrics]:
        return [
            self.evaluate_method("naive_rag"),
            self.evaluate_method("hybrid_rag"),
            self.evaluate_method("handovergap"),
        ]

    def evaluate_followup_retrieval(self, *, max_retrieval_queries: int = 3) -> FollowupRetrievalMetrics:
        scenarios = self.store.list_scenarios()
        detector = HandoverGapDetector(store=self.store)
        retrieve_more_cases = 0
        successful_retrievals = 0
        ask_reduction_cases = 0
        initially_interrupted_cases = 0
        unsafe_total = 0
        unsafe_answered = 0
        accurate_final_routes = 0
        generated_queries = 0

        for scenario in scenarios:
            initial_scenario = scenario.model_copy(update={"evidence_slots": []})
            initial_result = detector.detect_scenario(initial_scenario)
            initial_route = route_transferability_result(
                initial_result,
                retrieval_mode="expand_before_ask",
                max_retrieval_queries=max_retrieval_queries,
            )
            initial_ask_first_route = route_transferability_result(initial_result)

            final_result = detector.detect_scenario(scenario)
            final_route = route_transferability_result(final_result)

            if initial_route.recommended_action == "retrieve_more":
                retrieve_more_cases += 1
                generated_queries += len(initial_route.retrieval_queries)
                if len(final_result.gaps) < len(initial_result.gaps):
                    successful_retrievals += 1

            if initial_ask_first_route.action != "answer":
                initially_interrupted_cases += 1
                if len(final_route.questions) < len(initial_ask_first_route.questions):
                    ask_reduction_cases += 1

            if scenario.unsafe_transfer_label:
                unsafe_total += 1
                if final_route.action == "answer":
                    unsafe_answered += 1

            final_answered = final_route.action == "answer"
            if (scenario.unsafe_transfer_label and not final_answered) or (not scenario.unsafe_transfer_label and final_answered):
                accurate_final_routes += 1

        return FollowupRetrievalMetrics(
            scenarios=len(scenarios),
            retrieve_more_cases=retrieve_more_cases,
            retrieve_more_success_rate=_ratio(successful_retrievals, retrieve_more_cases),
            ask_reduction_rate=_ratio(ask_reduction_cases, initially_interrupted_cases),
            unsafe_answer_rate=_ratio(unsafe_answered, unsafe_total),
            extra_retrieval_cost=_ratio(generated_queries, len(scenarios)),
            final_route_accuracy=_ratio(accurate_final_routes, len(scenarios)),
        )

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
            slot_fill_mode=self.slot_fill_mode,
            slot_fill_source=self.slot_fill_source,
            model_name=self.model_name,
            prompt_profile=self.prompt_profile,
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
