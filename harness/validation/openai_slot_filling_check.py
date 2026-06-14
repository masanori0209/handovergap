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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run optional OpenAI semantic slot-filling validation.")
    parser.add_argument("--dataset", default="holdout", help="Built-in dataset to evaluate.")
    parser.add_argument("--model", default=os.getenv("OPENAI_SLOT_MODEL", "gpt-4.1-mini"))
    parser.add_argument("--persist-tidb", action="store_true", help="Persist aggregate metrics to TiDB evaluation_runs.")
    parser.add_argument("--output", default="article/openai_slot_filling_results.json")
    args = parser.parse_args()

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
        fill = _fill_slots(client, args.model, scenario)
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
            }
        )

    metrics = _metrics_from_rows(scenario_rows)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": args.dataset,
        "model": args.model,
        "metrics": metrics,
        "scenarios": scenario_rows,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    if args.persist_tidb:
        _persist_metrics_to_tidb(args.dataset, args.model, metrics)

    print(json.dumps({"status": "ok", **payload, "scenarios": len(scenario_rows)}, ensure_ascii=False, indent=2))
    return 0


def _fill_slots(client: Any, model: str, scenario: Any) -> dict[str, Any]:
    required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
    prompt = f"""
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
        max_output_tokens=1200,
    )
    payload = json.loads(response.output_text)
    filled = sorted(set(payload["filled_slots"]) & set(required_slots))
    return {"filled_slots": filled, "slot_rationales": payload["slot_rationales"]}


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
