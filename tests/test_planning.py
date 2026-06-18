from handovergap import TransferabilityGate, build_followup_retrieval_queries


def test_build_followup_retrieval_queries_from_missing_slots() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    queries = build_followup_retrieval_queries(result, max_queries=2)

    assert len(queries) == 2
    assert queries[0].slot_name == result.gaps[0].slot_name
    assert "profile=CS" in queries[0].query
    assert "missing_slot=" in queries[0].query
    assert queries[0].question
    assert queries[0].reason
    assert queries[0].preferred_source_types
    assert queries[0].search_terms
    assert "preferred_source_types=" in queries[0].query
    assert "search_terms=" in queries[0].query


def test_followup_retrieval_query_includes_slot_specific_hints() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=[
            "scope",
            "communication_status",
            "authority",
            "escalation_path",
            "customer_facing_wording",
        ],
    )

    query = build_followup_retrieval_queries(result, max_queries=1)[0]

    assert query.slot_name == "fallback_plan"
    assert "runbook" in query.preferred_source_types
    assert "support_playbook" in query.preferred_source_types
    assert "fallback" in query.search_terms
    assert "workaround" in query.search_terms


def test_build_followup_retrieval_queries_respects_limit() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    queries = build_followup_retrieval_queries(result, max_queries=1)

    assert len(queries) == 1
