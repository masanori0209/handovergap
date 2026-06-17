from __future__ import annotations

from dataclasses import dataclass

from handovergap import TransferabilityGate, map_evidence_slots_by_keywords, route_transferability_result


@dataclass(frozen=True)
class SourceNode:
    text: str
    metadata: dict[str, object]


SLOT_KEYWORDS = {
    "communication_status": ["customer accepted"],
    "authority": ["support can answer", "do not promise"],
    "fallback_plan": ["manual upload fallback"],
    "escalation_path": ["support lead queue"],
    "customer_facing_wording": ["approved customer wording"],
}


def main() -> None:
    # Replace this list with LlamaIndex retriever/query engine source nodes:
    # nodes = retriever.retrieve(query)
    source_nodes = [
        SourceNode(
            text="API integration is postponed. Customer accepted CSV for this release.",
            metadata={"source_type": "crm_note"},
        ),
        SourceNode(
            text="Approved customer wording: use CSV import while API import is deferred.",
            metadata={"source_type": "support_macro"},
        ),
    ]
    evidence = [
        {"source_type": str(node.metadata["source_type"]), "content": node.text, "metadata": node.metadata}
        for node in source_nodes
    ]
    evidence_slots = map_evidence_slots_by_keywords(evidence, SLOT_KEYWORDS)

    gate = TransferabilityGate()
    result = gate.check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        evidence=evidence,
        provided_slots=["scope"],
        evidence_slots=evidence_slots,
    )
    route = route_transferability_result(result, safe_context=result.memory)

    print(f"route={route.status} action={route.action}")
    if route.action != "answer":
        print("Do not call the final synthesizer yet.")
        for question in route.questions:
            print(f"- {question}")
        return

    print("Safe to call the final synthesizer.")


if __name__ == "__main__":
    main()
