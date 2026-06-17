from handovergap import TransferabilityGate, map_evidence_slots_by_keywords


def test_keyword_mapping_turns_raw_evidence_into_supported_slots() -> None:
    evidence = [
        "Customer notice was sent with approved wording.",
        {"source_type": "runbook", "content": "Fallback is manual upload. Escalate in the support channel."},
    ]
    slot_keywords = {
        "communication_status": ["notice was sent"],
        "fallback_plan": ["fallback", "manual upload"],
        "escalation_path": ["escalate", "support channel"],
        "customer_facing_wording": ["approved wording"],
    }

    assert map_evidence_slots_by_keywords(evidence, slot_keywords) == [
        "communication_status",
        "fallback_plan",
        "escalation_path",
        "customer_facing_wording",
    ]


def test_evidence_slot_mapping_reconciles_false_clarification() -> None:
    memory = "Use CSV for this release; API support is deferred."
    evidence = [
        "Customer notice was sent on Monday with approved wording.",
        "Support can answer standard questions, but must not promise API dates.",
        "If CSV import fails, use the manual upload fallback and escalate in the support channel.",
    ]
    slot_keywords = {
        "communication_status": ["notice was sent", "customer notice"],
        "authority": ["can answer", "must not promise"],
        "fallback_plan": ["fallback", "manual upload"],
        "escalation_path": ["escalate", "support channel"],
        "customer_facing_wording": ["approved wording"],
    }
    gate = TransferabilityGate()

    without_evidence_slots = gate.check(
        memory=memory,
        profile="CS",
        task_context="Answer customer questions without overpromising.",
        evidence=evidence,
        provided_slots=["scope"],
    )
    evidence_slots = map_evidence_slots_by_keywords(evidence, slot_keywords)
    with_evidence_slots = gate.check(
        memory=memory,
        profile="CS",
        task_context="Answer customer questions without overpromising.",
        evidence=evidence,
        provided_slots=["scope"],
        evidence_slots=evidence_slots,
    )

    assert without_evidence_slots.transferability_status == "blocked"
    assert {question.slot_name for question in without_evidence_slots.questions} >= {"communication_status"}
    assert with_evidence_slots.transferability_status == "transferable"
    assert with_evidence_slots.questions == []
