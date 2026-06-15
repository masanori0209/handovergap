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


def test_holdout_dataset_has_unknown_ids_and_annotation_metadata() -> None:
    scenarios = InMemoryStore.from_builtin_dataset("holdout").list_scenarios()

    assert len(scenarios) >= 6
    assert all(scenario.scenario_id.startswith("U") for scenario in scenarios)
    assert any(scenario.unsafe_transfer_label is False for scenario in scenarios)
    assert all(scenario.annotator_gap_slots for scenario in scenarios)
    assert all("optimistic" in scenario.slot_fill_profiles for scenario in scenarios)


def test_adversarial_dataset_breaks_slot_gold_structural_alignment() -> None:
    scenarios = InMemoryStore.from_builtin_dataset("adversarial").list_scenarios()

    assert len(scenarios) >= 6
    assert all(scenario.scenario_id.startswith("A") for scenario in scenarios)
    assert any(
        scenario.unsafe_transfer_label is False
        and not scenario.gold_gaps
        and set(scenario.provided_slots) != set(scenario.evidence_slots)
        for scenario in scenarios
    )
    assert any(
        scenario.unsafe_transfer_label is True
        and not ({gap.slot_name for gap in scenario.gold_gaps} <= set(scenario.provided_slots))
        for scenario in scenarios
    )


def test_sanitized_dataset_looks_like_anonymized_work_notes() -> None:
    scenarios = InMemoryStore.from_builtin_dataset("sanitized").list_scenarios()

    assert len(scenarios) >= 6
    assert all(scenario.scenario_id.startswith("R") for scenario in scenarios)
    assert {scenario.successor_role for scenario in scenarios} == {"CS", "Engineer", "Sales"}
    assert any(scenario.unsafe_transfer_label is False for scenario in scenarios)
    assert all(scenario.evidence_events for scenario in scenarios)
    assert all("reviewer_a" in scenario.annotator_gap_slots for scenario in scenarios)
    assert all("株式会社" not in scenario.memory for scenario in scenarios)
