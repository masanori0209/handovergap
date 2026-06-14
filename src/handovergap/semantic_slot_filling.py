from __future__ import annotations

import json
from typing import Any

from handovergap.slot_rules import ROLE_REQUIRED_SLOTS

SLOT_FILL_CRITERIA = {
    "communication_status": (
        "Filled only when the evidence states who has already been informed, what was communicated, "
        "and whether the communication is complete enough for the successor's next action."
    ),
    "scope": (
        "Filled only when the applicable objects, customers, releases, screens, jobs, or time window are explicit. "
        "A vague plan or task label is not enough."
    ),
    "authority": (
        "Filled only when the successor's decision or response authority is explicit, including what they may "
        "and may not say or decide."
    ),
    "fallback_plan": "Filled only when a concrete alternate action is given for failure, exception, or customer pushback.",
    "escalation_path": "Filled only when the evidence names a concrete team, owner, channel, or procedure to escalate to.",
    "customer_facing_wording": (
        "Filled only when reusable external wording or a customer-safe message is provided. "
        "An internal instruction such as 'explain the tentative cause' is not enough."
    ),
    "rationale": "Filled only when the evidence states why the decision was made, not merely what action to take.",
    "technical_constraint": (
        "Filled only when the actual technical limitation or prerequisite is stated. "
        "A reference to a runbook or issue is not enough unless the constraint itself is included."
    ),
    "implementation_scope": "Filled only when the implementation boundary, target, and non-target are explicit.",
    "trigger_for_reconsideration": (
        "Filled only when the condition that should cause a change of plan or reconsideration is explicit. "
        "A fallback action after failure is not enough unless it explicitly says when to reconsider the plan, "
        "move to another implementation strategy, or reopen the decision."
    ),
    "related_issue": "Filled only when a concrete ticket, issue, document id, runbook id, or traceable record is provided.",
    "failure_modes": "Filled only when likely failure patterns, symptoms, or detection conditions are explicit.",
    "contract_impact": (
        "Filled only when confirmed contract or commercial impact is stated. "
        "A pending legal check or planned quote is not enough."
    ),
    "promise_boundary": (
        "Filled only when the customer commitment boundary is explicit: what can be promised, under what "
        "conditions, and what must not be promised."
    ),
    "customer_expectation": (
        "Filled only when the customer's current expectation is explicit, not merely what the company plans."
    ),
    "timeline_confidence": (
        "Filled only when the evidence gives a date/window plus confidence, certainty, risk, or conditions."
    ),
    "negotiation_status": "Filled only when current agreement state, open issues, and approval/legal status are explicit.",
}


def default_prompt_profile(model: str) -> str:
    return "gpt5_strict" if model.startswith("gpt-5") else "baseline"


def build_slot_fill_prompt(scenario: Any, required_slots: list[str], prompt_profile: str) -> str:
    base = f"""
You are a strict handover safety reviewer.

Task:
Decide which required slots are explicitly filled well enough for the successor to act safely.
Do not infer missing authority, promise boundaries, escalation paths, or customer communication status from vague text.
Return only slots that are directly supported by the memory or evidence.

Successor role: {scenario.successor_role}
Handover task: {scenario.handover_task}
Required slots: {required_slots}

Memory:
{scenario.memory}

Evidence events:
{json.dumps([event.model_dump() for event in scenario.evidence_events], ensure_ascii=False)}
"""
    if prompt_profile == "baseline":
        return base

    criteria = {slot: SLOT_FILL_CRITERIA[slot] for slot in required_slots}
    return f"""{base}

GPT-5 strict evidence profile:
- Treat "filled" as a high bar: the successor can reuse the information without guessing, asking a teammate, opening an unspecified document, or inventing wording.
- Mark a slot false when the evidence only says that a decision is planned, pending, under investigation, in a runbook/issue/CRM note, or available somewhere else without giving the actual value needed for handover.
- For this validation dataset, evidence event contents are summaries of available handover artifacts. If a summary explicitly says a required item itself is documented or recorded, treat that as direct support. Do not apply this when the summary says the item is pending, unconfirmed, not recorded, or merely planned.
- Do not treat an internal plan as customer-safe wording.
- Do not treat "legal/SRE/owner will decide later" as contract impact, authority, promise boundary, or escalation path.
- Do not fill a slot from general role knowledge, likely workflow, implied next steps, or your own synthesis.
- If the evidence is ambiguous, partial, or says the item is not yet confirmed, set filled=false.

Slot-specific acceptance criteria:
{json.dumps(criteria, ensure_ascii=False, indent=2)}
"""


def fill_slots_with_openai(
    client: Any,
    model: str,
    scenario: Any,
    max_output_tokens: int = 4000,
    prompt_profile: str | None = None,
) -> dict[str, Any]:
    prompt_profile = prompt_profile or default_prompt_profile(model)
    required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
    response = client.responses.create(
        model=model,
        input=build_slot_fill_prompt(scenario, required_slots, prompt_profile),
        text={
            "format": {
                "type": "json_schema",
                "name": "handover_slot_fill",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "filled_slots": {
                            "type": "array",
                            "items": {"type": "string", "enum": required_slots},
                        },
                        "slot_rationales": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "slot_name": {"type": "string", "enum": required_slots},
                                    "filled": {"type": "boolean"},
                                    "reason": {"type": "string"},
                                },
                                "required": ["slot_name", "filled", "reason"],
                            },
                        },
                    },
                    "required": ["filled_slots", "slot_rationales"],
                },
            }
        },
        max_output_tokens=max_output_tokens,
    )
    if not response.output_text:
        raise RuntimeError(
            f"OpenAI response did not contain output_text for scenario {scenario.scenario_id}; "
            f"status={getattr(response, 'status', None)} incomplete={getattr(response, 'incomplete_details', None)}"
        )
    payload = json.loads(response.output_text)
    usage = getattr(response, "usage", None)
    return {
        "filled_slots": sorted(set(payload["filled_slots"]) & set(required_slots)),
        "slot_rationales": payload["slot_rationales"],
        "usage": usage.model_dump() if usage else {},
        "prompt_profile": prompt_profile,
    }


def usage_summary(usage: dict[str, Any]) -> dict[str, int]:
    output_details = usage.get("output_tokens_details") or {}
    return {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "reasoning_tokens": output_details.get("reasoning_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }
