from __future__ import annotations

from dataclasses import dataclass

from handovergap import TransferabilityGate, map_evidence_slots_by_keywords, route_transferability_result


@dataclass(frozen=True)
class Document:
    page_content: str
    metadata: dict[str, object]


SLOT_KEYWORDS = {
    "communication_status": ["customer notice", "sent on monday"],
    "authority": ["support can answer", "must not promise"],
    "fallback_plan": ["manual upload fallback"],
    "escalation_path": ["support lead queue"],
    "customer_facing_wording": ["approved wording"],
}


def main() -> None:
    # Replace this list with LangChain retriever output:
    # docs = retriever.invoke(query)
    retrieved_docs = [
        Document(
            page_content=(
                "Customer notice was sent on Monday with approved wording. "
                "Support can answer workaround questions, but must not promise API delivery dates."
            ),
            metadata={"source": "customer-update"},
        ),
        Document(
            page_content="API support moved to the next phase.",
            metadata={"source": "release-note"},
        ),
    ]
    evidence = [
        {"source_type": "langchain_document", "content": doc.page_content, "metadata": doc.metadata}
        for doc in retrieved_docs
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
    if route.action == "answer":
        print("Generate the final RAG answer.")
        return

    print("Ask clarification questions before answering:")
    for question in route.questions:
        print(f"- {question}")


if __name__ == "__main__":
    main()
