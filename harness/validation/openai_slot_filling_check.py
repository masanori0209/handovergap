from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from handovergap.core.detector import HandoverGapDetector
from handovergap.semantic_slot_filling import default_prompt_profile, fill_slots_with_openai, usage_summary
from handovergap.store import InMemoryStore


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
    prompt_profile = args.prompt_profile or default_prompt_profile(args.model)

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
        fill = fill_slots_with_openai(client, args.model, scenario, args.max_output_tokens, prompt_profile)
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
        usage = usage_summary(row.get("usage", {}))
        totals["input_tokens"] += usage["input_tokens"]
        totals["output_tokens"] += usage["output_tokens"]
        totals["total_tokens"] += usage["total_tokens"]
        totals["reasoning_tokens"] += usage["reasoning_tokens"]
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
