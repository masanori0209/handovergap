from __future__ import annotations

from handovergap import TransferabilityGate, route_transferability_result


def route_support_reply() -> dict[str, object]:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions without overpromising.",
        provided_slots=["scope"],
    )
    return route_transferability_result(result).model_dump()


def route_incident_response() -> dict[str, object]:
    result = TransferabilityGate().check(
        memory="The nightly job can be rerun manually.",
        profile="Engineer",
        task_context="Recover a failed nightly job.",
        provided_slots=["related_issue", "failure_modes"],
    )
    return route_transferability_result(result).model_dump()


def route_agent_action() -> dict[str, object]:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Let an agent answer standard CSV workaround questions.",
        provided_slots=[
            "scope",
            "communication_status",
            "authority",
            "fallback_plan",
            "escalation_path",
            "customer_facing_wording",
        ],
    )
    return route_transferability_result(result, safe_context=result.memory).model_dump()


def main() -> None:
    for name, route in [
        ("support", route_support_reply()),
        ("incident", route_incident_response()),
        ("agent", route_agent_action()),
    ]:
        print(f"{name}: action={route['action']} status={route['status']}")


if __name__ == "__main__":
    main()
