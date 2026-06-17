from __future__ import annotations

from handovergap import TransferabilityGate, map_evidence_slots_by_keywords


def main() -> None:
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

    print(f"without_evidence_slots={without_evidence_slots.transferability_status}")
    print(f"evidence_slots={','.join(evidence_slots)}")
    print(f"with_evidence_slots={with_evidence_slots.transferability_status}")


if __name__ == "__main__":
    main()
