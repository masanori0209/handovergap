from handovergap import TransferabilityGate, route_transferability_result


def test_route_transferable_result_allows_answer_with_safe_context() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions without overpromising.",
        provided_slots=[
            "scope",
            "communication_status",
            "authority",
            "fallback_plan",
            "escalation_path",
            "customer_facing_wording",
        ],
    )

    route = route_transferability_result(result, safe_context=result.memory)

    assert route.status == "transferable"
    assert route.action == "answer"
    assert route.reason == []
    assert route.questions == []
    assert route.safe_context == result.memory


def test_route_needs_clarification_result_asks_questions_without_safe_context() -> None:
    result = TransferabilityGate().check(
        memory="The nightly job can be rerun manually.",
        profile="Engineer",
        task_context="Recover a failed nightly job.",
        provided_slots=["related_issue", "failure_modes"],
    )

    route = route_transferability_result(result, safe_context=result.memory)

    assert route.status == "needs_clarification"
    assert route.action == "ask"
    assert route.reason
    assert route.questions
    assert route.safe_context is None


def test_route_blocked_result_blocks_without_exposing_safe_context() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    route = route_transferability_result(result, safe_context=result.memory)

    assert route.status == "blocked"
    assert route.action == "block"
    assert any("説明済み" in reason for reason in route.reason)
    assert route.questions
    assert route.safe_context is None
