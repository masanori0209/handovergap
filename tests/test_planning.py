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


def test_build_followup_retrieval_queries_respects_limit() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    queries = build_followup_retrieval_queries(result, max_queries=1)

    assert len(queries) == 1
