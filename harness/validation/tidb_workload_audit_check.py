from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from handovergap.workload import benchmark_generated_workload, generate_workload_scenarios

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness.validation.tidb_audit_query_check import (  # noqa: E402
    _connect_args,
    _explain_audit_query,
    _load_dotenv_if_available,
    _load_sqlalchemy,
    _measure_audit_query,
    _percentile,
    _persist_dataset,
    _store_from_env,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist generated workload scenarios to live TiDB and measure the audit query.")
    parser.add_argument("--scenarios", type=int, default=100, help="Generated scenarios to persist to TiDB.")
    parser.add_argument("--iterations", type=int, default=10, help="Repeated audit SELECT runs for p50/p95 timing.")
    parser.add_argument("--persist-batch-size", type=int, default=10, help="Scenarios per TiDB transaction.")
    parser.add_argument("--local-scale", default="100,1000,10000", help="Comma-separated local workload sizes to summarize.")
    parser.add_argument("--create-schema", action="store_true", help="Create the packaged HandoverGap schema first.")
    parser.add_argument(
        "--reset-schema",
        action="store_true",
        help="Drop packaged HandoverGap tables before creating them. Intended for alpha validation DBs only.",
    )
    parser.add_argument("--output-json", default="article/tidb_workload_audit_results.json")
    parser.add_argument("--output-md", default="article/tidb_workload_audit_results.md")
    args = parser.parse_args()

    _load_dotenv_if_available()
    _, _, URL = _load_sqlalchemy()
    store = _store_from_env(URL)
    engine = store.create_engine(pool_recycle=300, connect_args=_connect_args())
    if args.reset_schema:
        store.reset_schema(engine)
        args.create_schema = True
    if args.create_schema:
        store.create_schema(engine)

    run_id = "WORKLOAD-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    scenarios = generate_workload_scenarios(args.scenarios)
    from sqlalchemy import text

    inserted = _persist_in_batches(engine, text, scenarios, run_id, args.persist_batch_size)
    timings, rows = _measure_audit_query(engine, text, run_id, args.iterations)
    explain_rows = _explain_audit_query(engine, text, run_id)
    local_scale = _local_scale_results(args.local_scale)

    result = {
        "status": "ok",
        "run_id": run_id,
        "dataset": "generated_workload",
        "scenario_count": len(scenarios),
        "inserted": inserted,
        "audit_query": {
            "iterations": args.iterations,
            "result_rows": len(rows),
            "p50_ms": round(_percentile(timings, 0.50), 3),
            "p95_ms": round(_percentile(timings, 0.95), 3),
            "min_ms": round(min(timings), 3),
            "max_ms": round(max(timings), 3),
        },
        "local_scale": local_scale,
        "sample_rows": rows[:10],
        "explain_rows": explain_rows,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_render_markdown(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _local_scale_results(local_scale: str) -> list[dict[str, Any]]:
    rows = []
    for raw_count in local_scale.split(","):
        raw_count = raw_count.strip()
        if not raw_count:
            continue
        count = int(raw_count)
        result = benchmark_generated_workload(count=count, iterations=2)
        rows.append(result.model_dump())
    return rows


def _persist_in_batches(engine: Any, text: Any, scenarios: list[Any], run_id: str, batch_size: int) -> dict[str, int]:
    totals = {
        "source_events": 0,
        "memory_items": 0,
        "memory_chunks": 0,
        "slot_fill_attempts": 0,
        "context_gaps": 0,
        "clarification_questions": 0,
        "transfer_assessments": 0,
    }
    batch_size = max(batch_size, 1)
    for start in range(0, len(scenarios), batch_size):
        batch = scenarios[start : start + batch_size]
        inserted = _persist_dataset(engine, text, batch, run_id)
        for key, count in inserted.items():
            totals[key] += count
    return totals


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# TiDB Generated Workload Audit Result",
        "",
        f"- Observed at: {datetime.now(timezone.utc).date().isoformat()}",
        f"- Live TiDB scenarios persisted: {result['scenario_count']}",
        f"- Audit query result rows: {result['audit_query']['result_rows']}",
        f"- Iterations: {result['audit_query']['iterations']}",
        f"- p50 latency: `{result['audit_query']['p50_ms']} ms`",
        f"- p95 latency: `{result['audit_query']['p95_ms']} ms`",
        "",
        "This is a live TiDB Cloud validation result for generated workload auditability, not a load-test claim.",
        "",
        "## Inserted Rows",
        "",
        "| Table | Rows |",
        "|---|---:|",
    ]
    for table, count in result["inserted"].items():
        lines.append(f"| `{table}` | {count} |")
    lines.extend(
        [
            "",
            "## Local Workload Scale",
            "",
            "| Scenarios | Assessments | Gaps | Questions | Blocked | p50 local ms | p95 local ms |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["local_scale"]:
        lines.append(
            "| {scenarios} | {transfer_assessments_per_run} | {context_gaps_per_run} | "
            "{clarification_questions_per_run} | {blocked_assessments_per_run} | {p50_ms:.3f} | {p95_ms:.3f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Sample Blocked Audit Rows",
            "",
            "| Scenario | Profile | Missing slot | Severity | Evidence | Question |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in result["sample_rows"][:8]:
        lines.append(
            "| {scenario_id} | {profile} | {slot_name} | {severity} | {selected_evidence_title} | {question} |".format(
                scenario_id=row.get("scenario_id", ""),
                profile=row.get("profile", ""),
                slot_name=row.get("slot_name", ""),
                severity=row.get("severity", ""),
                selected_evidence_title=(row.get("selected_evidence_title") or "").replace("|", "/"),
                question=(row.get("question") or "").replace("|", "/"),
            )
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
