"""Evidence-seeking follow-up questions for a claim.

This example does not score candidates, infer honesty, or make hiring decisions.
It only demonstrates how to ask for missing evidence and scope details.
"""

from __future__ import annotations

from handovergap import (
    ProfileCatalog,
    ProfileDefinition,
    RetrievalHints,
    SlotPolicy,
    TransferabilityGate,
    map_evidence_slots_by_keywords,
    route_transferability_result,
)

CLAIM_PROFILE = ProfileCatalog(
    [
        ProfileDefinition(
            profile="ClaimReview",
            required_slots=[
                SlotPolicy(
                    slot_name="personal_contribution",
                    description="The candidate's own contribution is not specific enough.",
                    question="What did you personally decide, build, or own in this result?",
                    gap_type="personal_contribution_gap",
                    severity="HIGH",
                    high_risk=True,
                    retrieval_hints=RetrievalHints(
                        preferred_source_types=["candidate_answer", "interview_transcript", "work_sample"],
                        search_terms=["I owned", "I decided", "my role", "personally contributed"],
                    ),
                ),
                SlotPolicy(
                    slot_name="evidence_basis",
                    description="The claim lacks evidence that can be checked or discussed.",
                    question="What artifact, metric, dashboard, or stakeholder can substantiate this claim?",
                    gap_type="evidence_basis_gap",
                    severity="HIGH",
                    high_risk=True,
                    retrieval_hints=RetrievalHints(
                        preferred_source_types=["candidate_answer", "portfolio", "interview_transcript"],
                        search_terms=["dashboard", "metric", "artifact", "review", "stakeholder"],
                    ),
                ),
                SlotPolicy(
                    slot_name="scope_boundary",
                    description="The scope and non-scope of the achievement are not explicit.",
                    question="Which parts were in your scope, and which parts were handled by others?",
                    gap_type="scope_boundary_gap",
                    severity="MEDIUM",
                    retrieval_hints=RetrievalHints(
                        preferred_source_types=["candidate_answer", "interview_transcript"],
                        search_terms=["scope", "handled by others", "not responsible", "team owned"],
                    ),
                ),
                SlotPolicy(
                    slot_name="constraints_tradeoffs",
                    description="The constraints and tradeoffs behind the claimed result are not explicit.",
                    question="What constraints or tradeoffs made this work difficult?",
                    gap_type="constraints_tradeoffs_gap",
                    severity="MEDIUM",
                    retrieval_hints=RetrievalHints(
                        preferred_source_types=["candidate_answer", "case_study_answer", "interview_transcript"],
                        search_terms=["tradeoff", "constraint", "risk", "alternative"],
                    ),
                ),
                SlotPolicy(
                    slot_name="measurable_outcome",
                    description="The measurable outcome is not explicit.",
                    question="What metric changed, over what time period, and from what baseline?",
                    gap_type="measurable_outcome_gap",
                    severity="MEDIUM",
                    retrieval_hints=RetrievalHints(
                        preferred_source_types=["candidate_answer", "resume", "portfolio"],
                        search_terms=["reduced", "increased", "baseline", "metric", "period"],
                    ),
                ),
            ],
        )
    ]
)


SLOT_KEYWORDS = {
    "personal_contribution": ["i owned", "i designed", "i decided", "my role"],
    "evidence_basis": ["dashboard", "monthly report", "artifact", "stakeholder"],
    "scope_boundary": ["backend only", "excluded", "handled by"],
    "constraints_tradeoffs": ["tradeoff", "constraint", "dual writes", "risk"],
    "measurable_outcome": ["35%", "reduced", "baseline", "over two quarters"],
}


def review_claim(candidate_answers: list[str]) -> dict[str, object]:
    claim = "I led a migration that reduced infrastructure cost by 35%."
    evidence_events = [
        {"source_type": "candidate_answer", "content": answer}
        for answer in candidate_answers
    ]
    evidence_slots = map_evidence_slots_by_keywords(evidence_events, SLOT_KEYWORDS)
    result = TransferabilityGate(profiles=CLAIM_PROFILE).check(
        memory=claim,
        profile="ClaimReview",
        task_context="Prepare evidence-seeking follow-up questions for a resume claim. Do not make a hiring decision.",
        evidence=evidence_events,
        provided_slots=["measurable_outcome"],
        evidence_slots=evidence_slots,
    )
    route = route_transferability_result(result, retrieval_mode="expand_before_ask", safety_policy="strict")
    return {
        "status": route.status,
        "action": route.action,
        "gaps": [gap.slot_name for gap in result.gaps],
        "questions": route.questions,
        "retrieval_queries": [query.model_dump() for query in route.retrieval_queries],
    }


def main() -> None:
    first_answer = (
        "I designed the rollout plan and owned the backend migration. "
        "The cost dashboard and monthly report showed the reduction."
    )
    second_answer = (
        "My scope was backend only; the data pipeline was handled by another team. "
        "The main tradeoff was temporary dual writes during migration."
    )

    for label, answers in [
        ("after first answer", [first_answer]),
        ("after second answer", [first_answer, second_answer]),
    ]:
        review = review_claim(answers)
        print(f"== {label} ==")
        print(f"status={review['status']} action={review['action']}")
        print(f"gaps={','.join(review['gaps']) or 'none'}")
        if review["questions"]:
            print("questions:")
            for question in review["questions"]:
                print(f"- {question}")
        else:
            print("questions=none")
        if review["retrieval_queries"]:
            print("retrieval_hints:")
            for query in review["retrieval_queries"]:
                print(f"- {query['slot_name']}: sources={','.join(query['preferred_source_types'])}")
        print()


if __name__ == "__main__":
    main()
