from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from handovergap.core.detector import HandoverGapDetector
from handovergap.slot_rules import ROLE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore

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
    "fallback_plan": (
        "Filled only when a concrete alternate action is given for failure, exception, or customer pushback."
    ),
    "escalation_path": (
        "Filled only when the evidence names a concrete team, owner, channel, or procedure to escalate to."
    ),
    "customer_facing_wording": (
        "Filled only when reusable external wording or a customer-safe message is provided. "
        "An internal instruction such as 'explain the tentative cause' is not enough."
    ),
    "rationale": (
        "Filled only when the evidence states why the decision was made, not merely what action to take."
    ),
    "technical_constraint": (
        "Filled only when the actual technical limitation or prerequisite is stated. "
        "A reference to a runbook or issue is not enough unless the constraint itself is included."
    ),
    "implementation_scope": (
        "Filled only when the implementation boundary, target, and non-target are explicit."
    ),
    "trigger_for_reconsideration": (
        "Filled only when the condition that should cause a change of plan or reconsideration is explicit. "
        "A fallback action after failure is not enough unless it explicitly says when to reconsider the plan, "
        "move to another implementation strategy, or reopen the decision."
    ),
    "related_issue": (
        "Filled only when a concrete ticket, issue, document id, runbook id, or traceable record is provided."
    ),
    "failure_modes": (
        "Filled only when likely failure patterns, symptoms, or detection conditions are explicit."
    ),
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
    "negotiation_status": (
        "Filled only when current agreement state, open issues, and approval/legal status are explicit."
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run optional OpenAI semantic slot-filling validation.")
    parser.add_argument("--dataset", default="holdout", help="Built-in dataset to evaluate.")
    parser.add_argument("--model", default=os.getenv("OPENAI_SLOT_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--max-output-tokens", type=int, default=4000)
    parser.add_argument(
        "--prompt-profile",
        choices=["baseline", "gpt5_strict"],
        default=None,
        help="Prompt variant. Defaults to gpt5_strict for GPT-5 models and baseline otherwise.",
    )
    parser.add_argument("--persist-tidb", action="store_true", help="Persist aggregate metrics to TiDB evaluation_runs.")
    parser.add_argument("--output", default="article/openai_slot_filling_results.json")
    args = parser.parse_args()
    prompt_profile = args.prompt_profile or _default_prompt_profile(args.model)

    _load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY. Add it to .env or the environment.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    store = InMemoryStore.from_builtin_dataset(args.dataset)
    detector = HandoverGapDetector(store)
    scenario_rows = []

    for scenario in store.list_scenarios():
        fill = _fill_slots(client, args.model, scenario, args.max_output_tokens, prompt_profile)
        profiled = scenario.model_copy(update={"provided_slots": fill["filled_slots"]})
        result = detector.detect_scenario(profiled)
        gold_slots = {gap.slot_name for gap in scenario.gold_gaps}
        predicted_gap_slots = {gap.slot_name for gap in result.gaps}
        scenario_rows.append(
            {
                "scenario_id": scenario.scenario_id,
                "successor_role": scenario.successor_role,
                "unsafe_transfer_label": scenario.unsafe_transfer_label,
                "llm_filled_slots": fill["filled_slots"],
                "gold_gap_slots": sorted(gold_slots),
                "predicted_gap_slots": sorted(predicted_gap_slots),
                "missed_gold_gap_slots": sorted(gold_slots - predicted_gap_slots),
                "transferability_status": result.transferability_status,
                "slot_rationales": fill["slot_rationales"],
                "usage": fill["usage"],
            }
        )

    metrics = _metrics_from_rows(scenario_rows)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": args.dataset,
        "model": args.model,
        "prompt_profile": prompt_profile,
        "metrics": metrics,
        "usage": _usage_from_rows(scenario_rows),
        "scenarios": scenario_rows,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    if args.persist_tidb:
        _persist_metrics_to_tidb(args.dataset, args.model, metrics)

    print(json.dumps({"status": "ok", **payload, "scenarios": len(scenario_rows)}, ensure_ascii=False, indent=2))
    return 0


def _fill_slots(
    client: Any,
    model: str,
    scenario: Any,
    max_output_tokens: int,
    prompt_profile: str,
) -> dict[str, Any]:
    required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
    prompt = _build_prompt(scenario, required_slots, prompt_profile)
    response = client.responses.create(
        model=model,
        input=prompt,
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
    filled = sorted(set(payload["filled_slots"]) & set(required_slots))
    usage = getattr(response, "usage", None)
    return {
        "filled_slots": filled,
        "slot_rationales": payload["slot_rationales"],
        "usage": usage.model_dump() if usage else {},
    }


def _default_prompt_profile(model: str) -> str:
    return "gpt5_strict" if model.startswith("gpt-5") else "baseline"


def _build_prompt(scenario: Any, required_slots: list[str], prompt_profile: str) -> str:
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


def _metrics_from_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    total_gold = sum(len(row["gold_gap_slots"]) for row in rows)
    detected_gold = sum(
        len(set(row["gold_gap_slots"]) & set(row["predicted_gap_slots"]))
        for row in rows
    )
    unsafe_rows = [row for row in rows if row["unsafe_transfer_label"]]
    safe_rows = [row for row in rows if not row["unsafe_transfer_label"]]
    blocked_rows = [row for row in rows if row["transferability_status"] == "blocked"]
    return {
        "scenarios": len(rows),
        "tacit_gap_recall": _ratio(detected_gold, total_gold),
        "unsafe_transfer_prevention": _ratio(
            sum(row["transferability_status"] == "blocked" for row in unsafe_rows),
            len(unsafe_rows),
        ),
        "safe_transfer_allowance": _ratio(
            sum(row["transferability_status"] != "blocked" for row in safe_rows),
            len(safe_rows),
        ),
        "blocked_precision": _ratio(
            sum(row["unsafe_transfer_label"] for row in blocked_rows),
            len(blocked_rows),
        ),
    }


def _usage_from_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    totals = {"input_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "total_tokens": 0}
    for row in rows:
        usage = row.get("usage", {})
        totals["input_tokens"] += usage.get("input_tokens", 0)
        totals["output_tokens"] += usage.get("output_tokens", 0)
        totals["total_tokens"] += usage.get("total_tokens", 0)
        output_details = usage.get("output_tokens_details") or {}
        totals["reasoning_tokens"] += output_details.get("reasoning_tokens", 0)
    return totals


def _persist_metrics_to_tidb(dataset: str, model: str, metrics: dict[str, float]) -> None:
    from handovergap import TiDBStore

    _load_dotenv()
    database_url = os.getenv("HANDOVERGAP_TIDB_URL")
    if not database_url:
        from sqlalchemy import URL

        database_url = URL.create(
            drivername="mysql+pymysql",
            username=_required_env("TIDB_USER"),
            password=_required_env("TIDB_PASSWORD"),
            host=_required_env("TIDB_HOST"),
            port=int(os.getenv("TIDB_PORT", "4000")),
            database=os.getenv("TIDB_DB_NAME", "test"),
        )
    store = TiDBStore(database_url)
    engine = store.create_engine(pool_recycle=300)
    store.persist_evaluation_runs(
        [
            {
                "method_name": f"handovergap/openai-slot-fill/{model}",
                "dataset_name": f"HandoverGapBench {dataset}",
                "metrics_json": json.dumps(metrics, ensure_ascii=False),
            }
        ],
        engine,
    )


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(".env")


if __name__ == "__main__":
    raise SystemExit(main())
