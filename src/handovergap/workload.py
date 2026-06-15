from __future__ import annotations

from time import perf_counter

from pydantic import BaseModel

from handovergap.core.detector import HandoverGapDetector
from handovergap.schemas import EvidenceEvent, HandoverScenario
from handovergap.slot_rules import PROFILE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore


class WorkloadBenchmarkResult(BaseModel):
    scenarios: int
    iterations: int
    transfer_assessments_per_run: int
    context_gaps_per_run: int
    clarification_questions_per_run: int
    blocked_assessments_per_run: int
    p50_ms: float
    p95_ms: float


def generate_workload_scenarios(count: int = 1000) -> list[HandoverScenario]:
    profiles = list(PROFILE_REQUIRED_SLOTS)
    scenarios = []
    for index in range(count):
        profile = profiles[index % len(profiles)]
        required_slots = PROFILE_REQUIRED_SLOTS[profile]
        filled_count = index % (len(required_slots) + 1)
        provided_slots = required_slots[:filled_count]
        scenario_id = f"W{index + 1:04d}"
        scenarios.append(
            HandoverScenario(
                scenario_id=scenario_id,
                memory=f"Generated workload memory {scenario_id}: proceed with the recorded plan for profile {profile}.",
                profile=profile,
                memory_type="task",
                task_context=f"Generated readiness check {scenario_id}",
                evidence_events=[
                    EvidenceEvent(
                        source_type="generated_note",
                        title=f"Generated evidence {scenario_id}",
                        content=f"Profile {profile} has recorded slots: {', '.join(provided_slots) or 'none'}.",
                        metadata={"synthetic": True, "workload_id": scenario_id},
                    )
                ],
                provided_slots=provided_slots,
                evidence_slots=provided_slots,
                unsafe_transfer_label=filled_count < len(required_slots),
            )
        )
    return scenarios


def benchmark_generated_workload(count: int = 1000, iterations: int = 5) -> WorkloadBenchmarkResult:
    scenarios = generate_workload_scenarios(count)
    store = InMemoryStore(scenarios)
    detector = HandoverGapDetector(store=store)
    durations = []
    last_results = []
    for _ in range(iterations):
        start = perf_counter()
        last_results = [detector.detect_scenario(scenario) for scenario in scenarios]
        durations.append((perf_counter() - start) * 1000)
    gap_rows = [gap for result in last_results for gap in result.gaps]
    question_rows = [question for result in last_results for question in result.questions]
    blocked = [result for result in last_results if result.transferability_status == "blocked"]
    return WorkloadBenchmarkResult(
        scenarios=count,
        iterations=iterations,
        transfer_assessments_per_run=len(last_results),
        context_gaps_per_run=len(gap_rows),
        clarification_questions_per_run=len(question_rows),
        blocked_assessments_per_run=len(blocked),
        p50_ms=_percentile(durations, 0.50),
        p95_ms=_percentile(durations, 0.95),
    )


def _percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * ratio)))
    return ordered[index]
