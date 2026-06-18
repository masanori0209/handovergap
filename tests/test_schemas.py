from handovergap.schemas import HandoverScenario


def test_scenario_schema_validates_representative_data() -> None:
    scenario = HandoverScenario.model_validate(
        {
            "scenario_id": "S999",
            "memory": "A社は今回だけCSVで対応する",
            "evidence_events": [{"source_type": "chat", "content": "今回だけCSV"}],
            "profile": "CS",
            "memory_type": "decision",
            "task_context": "問い合わせ対応",
            "provided_slots": ["scope"],
            "evidence_slots": ["scope"],
            "gold_gaps": [
                {
                    "gap_type": "communication_gap",
                    "slot_name": "communication_status",
                    "description": "説明済みか不明",
                    "severity": "HIGH",
                    "retrieval_hints": {
                        "preferred_source_types": ["support_note"],
                        "search_terms": ["説明済み"],
                    },
                }
            ],
            "gold_questions": [{"slot_name": "communication_status", "question": "説明済みですか？"}],
            "unsafe_transfer_label": True,
        }
    )

    assert scenario.profile == "CS"
    assert scenario.gold_gaps[0].slot_name == "communication_status"
    assert scenario.gold_gaps[0].retrieval_hints.preferred_source_types == ["support_note"]


def test_scenario_schema_uses_profile_and_task_context() -> None:
    scenario = HandoverScenario.model_validate(
        {
            "scenario_id": "S998",
            "memory": "Release can proceed only after the rollback owner is confirmed.",
            "evidence_events": [],
            "profile": "Engineer",
            "memory_type": "risk",
            "task_context": "Release readiness review",
            "provided_slots": ["scope"],
            "unsafe_transfer_label": True,
        }
    )

    assert scenario.profile == "Engineer"
    assert scenario.task_context == "Release readiness review"
