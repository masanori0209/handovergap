from __future__ import annotations

from handovergap import TransferabilityGate


def main() -> None:
    # Replace this list with LlamaIndex retriever/query engine source nodes, for example:
    # nodes = retriever.retrieve(query)
    source_nodes = [
        {"source_type": "issue", "content": "API integration is postponed."},
        {"source_type": "crm_note", "content": "Customer accepted CSV for this release."},
    ]

    gate = TransferabilityGate()
    result = gate.check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        evidence=source_nodes,
        provided_slots=["scope"],
        evidence_slots=["scope"],
    )

    if result.transferability_status != "transferable":
        print("Do not call the final synthesizer yet.")
        for question in result.questions:
            print(f"- {question.question}")
        return

    print("Safe to call the final synthesizer.")


if __name__ == "__main__":
    main()
