import pytest

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
    assert route.recommended_action == "answer"
    assert route.deployment_mode == "hard"
    assert route.retrieval_mode == "ask_first"
    assert route.safety_policy == "strict"
    assert route.enforcement == "enforce"
    assert route.should_interrupt is False
    assert route.next_step == "answer"
    assert route.reason == []
    assert route.questions == []
    assert route.retrieval_queries == []
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
    assert route.recommended_action == "ask"
    assert route.deployment_mode == "hard"
    assert route.retrieval_mode == "ask_first"
    assert route.enforcement == "enforce"
    assert route.should_interrupt is True
    assert route.next_step == "ask_user"
    assert route.reason
    assert route.questions
    assert route.retrieval_queries
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
    assert route.recommended_action == "block"
    assert route.deployment_mode == "hard"
    assert route.retrieval_mode == "ask_first"
    assert route.enforcement == "enforce"
    assert route.should_interrupt is True
    assert route.next_step == "block"
    assert any("説明済み" in reason for reason in route.reason)
    assert route.questions
    assert route.retrieval_queries
    assert route.safe_context is None


def test_route_expand_before_ask_recommends_followup_retrieval() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    route = route_transferability_result(
        result,
        safe_context=result.memory,
        retrieval_mode="expand_before_ask",
        max_retrieval_queries=2,
    )

    assert route.status == "blocked"
    assert route.recommended_action == "retrieve_more"
    assert route.action == "retrieve_more"
    assert route.retrieval_mode == "expand_before_ask"
    assert route.next_step == "run_followup_retrieval"
    assert route.should_interrupt is True
    assert len(route.retrieval_queries) == 2
    assert route.safe_context is None


def test_route_shadow_mode_observes_without_interrupting() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    route = route_transferability_result(result, safe_context=result.memory, deployment_mode="shadow")

    assert route.status == "blocked"
    assert route.recommended_action == "block"
    assert route.action == "answer"
    assert route.deployment_mode == "shadow"
    assert route.retrieval_mode == "ask_first"
    assert route.enforcement == "observe"
    assert route.should_interrupt is False
    assert route.next_step == "block"
    assert route.reason
    assert route.questions
    assert route.safe_context == result.memory


def test_route_soft_mode_warns_without_interrupting() -> None:
    result = TransferabilityGate().check(
        memory="The nightly job can be rerun manually.",
        profile="Engineer",
        task_context="Recover a failed nightly job.",
        provided_slots=["related_issue", "failure_modes"],
    )

    route = route_transferability_result(result, safe_context=result.memory, deployment_mode="soft")

    assert route.status == "needs_clarification"
    assert route.recommended_action == "ask"
    assert route.action == "answer"
    assert route.deployment_mode == "soft"
    assert route.retrieval_mode == "ask_first"
    assert route.enforcement == "warn"
    assert route.should_interrupt is False
    assert route.next_step == "ask_user"
    assert route.safe_context == result.memory


def test_route_shadow_expand_before_ask_observes_retrieval_plan_without_interrupting() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    route = route_transferability_result(
        result,
        safe_context=result.memory,
        deployment_mode="shadow",
        retrieval_mode="expand_before_ask",
    )

    assert route.recommended_action == "retrieve_more"
    assert route.action == "answer"
    assert route.enforcement == "observe"
    assert route.should_interrupt is False
    assert route.next_step == "run_followup_retrieval"
    assert route.retrieval_queries
    assert route.safe_context == result.memory


def test_strict_safety_policy_requires_evidence_for_high_risk_slots() -> None:
    result = TransferabilityGate().check(
        memory="The renewal can use the old price.",
        profile="Sales",
        task_context="Prepare renewal response.",
        provided_slots=[
            "contract_impact",
            "promise_boundary",
            "customer_expectation",
            "timeline_confidence",
            "negotiation_status",
        ],
        evidence_slots=["customer_expectation", "timeline_confidence"],
    )

    route = route_transferability_result(result)

    assert result.transferability_status == "transferable"
    assert route.safety_policy == "strict"
    assert route.recommended_action == "ask"
    assert route.action == "ask"
    assert route.should_interrupt is True
    assert any("High-risk slot 'contract_impact'" in reason for reason in route.reason)
    assert any("explicit evidence" in question for question in route.questions)
    assert route.safe_context is None


def test_balanced_safety_policy_allows_provided_high_risk_slots() -> None:
    result = TransferabilityGate().check(
        memory="The renewal can use the old price.",
        profile="Sales",
        task_context="Prepare renewal response.",
        provided_slots=[
            "contract_impact",
            "promise_boundary",
            "customer_expectation",
            "timeline_confidence",
            "negotiation_status",
        ],
        evidence_slots=["customer_expectation", "timeline_confidence"],
    )

    route = route_transferability_result(result, safe_context=result.memory, safety_policy="balanced")

    assert route.safety_policy == "balanced"
    assert route.recommended_action == "answer"
    assert route.action == "answer"
    assert route.safe_context == result.memory


def test_route_invalid_status_reports_expected_values() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    ).model_copy(update={"transferability_status": "paused"})

    with pytest.raises(ValueError) as exc_info:
        route_transferability_result(result)

    message = str(exc_info.value)
    assert "Invalid transferability_status 'paused'" in message
    assert "transferable, needs_clarification, blocked" in message


def test_route_invalid_deployment_mode_reports_expected_values() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    with pytest.raises(ValueError) as exc_info:
        route_transferability_result(result, deployment_mode="audit-only")  # type: ignore[arg-type]

    message = str(exc_info.value)
    assert "Invalid deployment_mode 'audit-only'" in message
    assert "shadow, soft, hard" in message


def test_route_invalid_retrieval_mode_reports_expected_values() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    with pytest.raises(ValueError) as exc_info:
        route_transferability_result(result, retrieval_mode="search_forever")  # type: ignore[arg-type]

    message = str(exc_info.value)
    assert "Invalid retrieval_mode 'search_forever'" in message
    assert "ask_first, expand_before_ask" in message


def test_route_invalid_safety_policy_reports_expected_values() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        provided_slots=["scope"],
    )

    with pytest.raises(ValueError) as exc_info:
        route_transferability_result(result, safety_policy="reckless")  # type: ignore[arg-type]

    message = str(exc_info.value)
    assert "Invalid safety_policy 'reckless'" in message
    assert "strict, balanced, exploratory" in message
