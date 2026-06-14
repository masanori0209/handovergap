from handovergap.schemas import HandoverScenario


def test_scenario_schema_validates_representative_data() -> None:
    scenario = HandoverScenario.model_validate(
        {
            "scenario_id": "S999",
            "memory": "A社は今回だけCSVで対応する",
            "evidence_events": [{"source_type": "chat", "content": "今回だけCSV"}],
            "successor_role": "CS",
            "memory_type": "decision",
            "handover_task": "問い合わせ対応",
            "provided_slots": ["scope"],
            "evidence_slots": ["scope"],
            "gold_gaps": [
                {
                    "gap_type": "communication_gap",
                    "slot_name": "communication_status",
                    "description": "説明済みか不明",
                    "severity": "HIGH",
                }
            ],
            "gold_questions": [{"slot_name": "communication_status", "question": "説明済みですか？"}],
            "unsafe_transfer_label": True,
        }
    )

    assert scenario.successor_role == "CS"
    assert scenario.gold_gaps[0].slot_name == "communication_status"
