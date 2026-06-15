from __future__ import annotations

from handovergap import TransferabilityGate


def main() -> None:
    # Replace this list with LangChain retriever output, for example:
    # docs = retriever.invoke(query)
    retrieved_docs = [
        "CSV workaround is approved for this release.",
        "API support moved to the next phase.",
    ]

    gate = TransferabilityGate()
    result = gate.check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        evidence=retrieved_docs,
        provided_slots=["scope"],
        evidence_slots=["scope"],
    )

    if result.transferability_status == "transferable":
        print("Generate the final RAG answer.")
    else:
        print("Ask clarification questions before answering:")
        for question in result.questions:
            print(f"- {question.question}")


if __name__ == "__main__":
    main()
