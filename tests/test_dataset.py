from handovergap.store import InMemoryStore


def test_builtin_dataset_has_mvp_coverage() -> None:
    scenarios = InMemoryStore.from_builtin_dataset().list_scenarios()

    assert len(scenarios) >= 20
    assert {scenario.successor_role for scenario in scenarios} == {"CS", "Engineer", "Sales"}
    gap_types = {gap.gap_type for scenario in scenarios for gap in scenario.gold_gaps}
    assert len(gap_types) >= 5


def test_builtin_dataset_uses_synthetic_sources() -> None:
    scenarios = InMemoryStore.from_builtin_dataset().list_scenarios()

    assert all(scenario.scenario_id.startswith("S") for scenario in scenarios)
    assert all(not scenario.memory.startswith("株式会社") for scenario in scenarios)
