from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from handovergap import (
    TransferabilityGate,
    map_evidence_slots_by_keywords,
    route_transferability_result,
)


@dataclass(frozen=True)
class RetrievedMemory:
    text: str
    slots: list[str]


@dataclass(frozen=True)
class RetrievedEvidence:
    title: str
    text: str

    def as_event(self) -> dict[str, Any]:
        return {
            "source_type": "retrieved_note",
            "title": self.title,
            "content": self.text,
        }


class DemoRetriever:
    """Small stand-in for an existing RAG retriever."""

    def search_memory(self, user_question: str) -> RetrievedMemory:
        return RetrievedMemory(
            text=(
                "For the current import limitation, recommend the CSV workaround. "
                "This applies only to the managed onboarding flow."
            ),
            slots=["scope"],
        )

    def search_evidence(self, user_question: str, *, include_runbook: bool) -> list[RetrievedEvidence]:
        evidence = [
            RetrievedEvidence(
                title="Customer update",
                text=(
                    "A customer notice was sent on Monday with approved wording: "
                    "'Use CSV import while API import is deferred for this release.'"
                ),
            ),
            RetrievedEvidence(
                title="Support policy",
                text=(
                    "Support can answer standard workaround questions, but must not promise "
                    "API delivery dates."
                ),
            ),
        ]
        if include_runbook:
            evidence.append(
                RetrievedEvidence(
                    title="Fallback and escalation runbook",
                    text=(
                        "If CSV import fails, use the manual upload fallback. Escalate urgent "
                        "onboarding blockers to the support lead queue."
                    ),
                )
            )
        return evidence


SLOT_KEYWORDS = {
    "communication_status": ["customer notice was sent", "customer update"],
    "authority": ["support can answer", "must not promise"],
    "fallback_plan": ["manual upload fallback", "fallback"],
    "escalation_path": ["escalate", "support lead queue"],
    "customer_facing_wording": ["approved wording"],
}


def run_flow(*, include_runbook: bool) -> dict[str, object]:
    retriever = DemoRetriever()
    user_question = "Can I tell the customer to use the CSV workaround?"
    memory = retriever.search_memory(user_question)
    evidence = retriever.search_evidence(user_question, include_runbook=include_runbook)
    evidence_events = [item.as_event() for item in evidence]
    evidence_slots = map_evidence_slots_by_keywords(evidence_events, SLOT_KEYWORDS)

    result = TransferabilityGate().check(
        scenario_id="rag-customer-import-workaround",
        memory=memory.text,
        profile="CS",
        task_context="Answer a customer question about the import workaround without overpromising.",
        evidence=evidence_events,
        provided_slots=memory.slots,
        evidence_slots=evidence_slots,
    )
    route = route_transferability_result(result, safe_context=memory.text)

    return {
        "retrieved_memory": memory.text,
        "retrieved_evidence_titles": [item.title for item in evidence],
        "provided_slots": memory.slots,
        "evidence_slots": evidence_slots,
        "status": route.status,
        "action": route.action,
        "gaps": [gap.slot_name for gap in result.gaps],
        "questions": route.questions,
        "safe_context": route.safe_context,
    }


def print_flow(name: str, flow: dict[str, object]) -> None:
    print(f"== {name} ==")
    print(f"provided_slots={','.join(flow['provided_slots'])}")
    print(f"evidence_slots={','.join(flow['evidence_slots'])}")
    print(f"status={flow['status']} action={flow['action']}")
    print(f"gaps={','.join(flow['gaps']) or 'none'}")
    questions = flow["questions"]
    if questions:
        print("questions:")
        for question in questions:
            print(f"- {question}")
    else:
        print("questions=none")
    if flow["safe_context"]:
        print("safe_context=available")
    else:
        print("safe_context=withheld")


def main() -> None:
    print_flow("first retrieval", run_flow(include_runbook=False))
    print()
    print_flow("after retrieving runbook evidence", run_flow(include_runbook=True))
    print()
    print("Optional extensions: replace keyword slot mapping with LLM slot filling,")
    print("or persist DetectionResult/ProductRoute to the TiDB audit store.")


if __name__ == "__main__":
    main()
