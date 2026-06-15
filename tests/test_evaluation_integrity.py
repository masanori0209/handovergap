from handovergap.semantic_slot_filling import build_slot_fill_prompt
from handovergap.slot_rules import PROFILE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore


def test_llm_slot_fill_prompt_does_not_receive_gold_labels() -> None:
    scenario = InMemoryStore.from_builtin_dataset("holdout").list_scenarios()[0]

    prompt = build_slot_fill_prompt(
        scenario,
        PROFILE_REQUIRED_SLOTS[scenario.profile],
        prompt_profile="gpt5_strict",
    )

    assert "gold_gaps" not in prompt
    assert "gold_questions" not in prompt
    assert "unsafe_transfer_label" not in prompt
    assert scenario.scenario_id not in prompt
