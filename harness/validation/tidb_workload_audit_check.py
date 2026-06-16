from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from handovergap.audit import diverse_audit_sample_rows
from handovergap.retrieval import chunk_rows_for_scenario
from handovergap.slot_rules import PROFILE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore
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
    _store_from_env,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist generated workload scenarios to live TiDB and measure the audit query.")
    parser.add_argument("--scenarios", type=int, default=100, help="Generated scenarios to persist to TiDB.")
    parser.add_argument("--iterations", type=int, default=10, help="Repeated audit SELECT runs for p50/p95 timing.")
    parser.add_argument("--persist-batch-size", type=int, default=500, help="Scenarios per TiDB transaction.")
    parser.add_argument("--local-scale", default="100,1000,10000", help="Comma-separated local workload sizes to summarize.")
    parser.add_argument(
        "--skip-memory-chunks",
        action="store_true",
        help="Skip VECTOR/full-text chunk rows. Use this for free-tier 100k audit-table validation.",
    )
    parser.add_argument("--scale-label", default=None, help="Optional label such as 10k or 100k for output metadata.")
    parser.add_argument("--progress-every", type=int, default=5000, help="Print progress every N persisted scenarios.")
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
    sqlalchemy, text, URL = _load_sqlalchemy()
    store = _store_from_env(URL)
    engine = store.create_engine(pool_recycle=300, connect_args=_connect_args())
    if args.reset_schema:
        store.reset_schema(engine)
        args.create_schema = True
    if args.create_schema:
        store.create_schema(engine)

    run_id = "WORKLOAD-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    scenarios = generate_workload_scenarios(args.scenarios)

    insert_start = perf_counter()
    inserted = _persist_in_batches(
        engine,
        sqlalchemy,
        text,
        scenarios,
        run_id,
        args.persist_batch_size,
        include_memory_chunks=not args.skip_memory_chunks,
        progress_every=args.progress_every,
    )
    insert_duration_ms = (perf_counter() - insert_start) * 1000
    timings, rows = _measure_audit_query(engine, text, run_id, args.iterations)
    explain_rows = _explain_audit_query(engine, text, run_id)
    local_scale = _local_scale_results(args.local_scale)

    result = {
        "status": "ok",
        "run_id": run_id,
        "dataset": "generated_workload",
        "scale_label": args.scale_label,
        "scenario_count": len(scenarios),
        "include_memory_chunks": not args.skip_memory_chunks,
        "insert_duration_ms": round(insert_duration_ms, 3),
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
        "sample_rows": diverse_audit_sample_rows(rows, limit=10),
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


def _persist_in_batches(
    engine: Any,
    sqlalchemy: Any,
    text: Any,
    scenarios: list[Any],
    run_id: str,
    batch_size: int,
    *,
    include_memory_chunks: bool,
    progress_every: int,
) -> dict[str, int]:
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
    persisted = 0
    for start in range(0, len(scenarios), batch_size):
        batch = scenarios[start : start + batch_size]
        inserted = _persist_dataset_bulk(
            engine,
            sqlalchemy,
            text,
            batch,
            run_id,
            include_memory_chunks=include_memory_chunks,
        )
        for key, count in inserted.items():
            totals[key] += count
        persisted += len(batch)
        if progress_every > 0 and (persisted == len(scenarios) or persisted % progress_every == 0):
            print(f"persisted {persisted}/{len(scenarios)} scenarios", file=sys.stderr)
    return totals


def _persist_dataset_bulk(
    engine: Any,
    sqlalchemy: Any,
    text: Any,
    scenarios: list[Any],
    run_id: str,
    *,
    include_memory_chunks: bool,
) -> dict[str, int]:
    counts = {
        "source_events": 0,
        "memory_items": 0,
        "memory_chunks": 0,
        "slot_fill_attempts": 0,
        "context_gaps": 0,
        "clarification_questions": 0,
        "transfer_assessments": 0,
    }
    if not scenarios:
        return counts

    detector = HandoverGapDetector(store=InMemoryStore(scenarios))
    scenario_keys = {scenario.scenario_id: f"{run_id}-{scenario.scenario_id}" for scenario in scenarios}

    with engine.begin() as connection:
        memory_rows = [
            {
                "scenario_id": scenario_keys[scenario.scenario_id],
                "subject": f"Anonymized workload handover {scenario.scenario_id}",
                "memory_type": scenario.memory_type,
                "content": scenario.memory,
                "source_person_name": "anonymized",
                "project_name": "handovergap-live-scale",
                "status": "active",
                "confidence": 0.95,
            }
            for scenario in scenarios
        ]
        connection.execute(
            text(
                """
                INSERT INTO memory_items (
                  scenario_id, subject, memory_type, content,
                  source_person_name, project_name, status, confidence
                ) VALUES (
                  :scenario_id, :subject, :memory_type, :content,
                  :source_person_name, :project_name, :status, :confidence
                )
                """
            ),
            memory_rows,
        )
        counts["memory_items"] += len(memory_rows)

        memory_ids = _select_id_map(
            connection,
            sqlalchemy,
            text,
            "memory_items",
            "scenario_id",
            [scenario_keys[scenario.scenario_id] for scenario in scenarios],
        )

        source_rows = []
        source_title_by_scenario_index: dict[tuple[str, int], str] = {}
        for scenario in scenarios:
            scenario_key = scenario_keys[scenario.scenario_id]
            for index, event in enumerate(scenario.evidence_events, start=1):
                title = f"{scenario_key} evidence {index}: {event.source_type}"
                source_title_by_scenario_index[(scenario.scenario_id, index)] = title
                source_rows.append(
                    {
                        "source_type": event.source_type,
                        "title": title,
                        "content": event.content,
                        "actor_name": "anonymized",
                        "project_name": "handovergap-live-scale",
                        "metadata": json.dumps({"run_id": run_id, "scenario_id": scenario.scenario_id}),
                    }
                )
        if source_rows:
            connection.execute(
                text(
                    """
                    INSERT INTO source_events (
                      source_type, title, content, actor_name, project_name, metadata
                    ) VALUES (
                      :source_type, :title, :content, :actor_name, :project_name, :metadata
                    )
                    """
                ),
                source_rows,
            )
            counts["source_events"] += len(source_rows)
        source_ids = _select_id_map(
            connection,
            sqlalchemy,
            text,
            "source_events",
            "title",
            [row["title"] for row in source_rows],
        )

        chunk_rows: list[dict[str, Any]] = []
        slot_rows: list[dict[str, Any]] = []
        gap_rows: list[dict[str, Any]] = []
        question_candidates: list[dict[str, Any]] = []
        transfer_rows: list[dict[str, Any]] = []

        for scenario in scenarios:
            memory_item_id = memory_ids[scenario_keys[scenario.scenario_id]]
            event_ids = [
                source_ids[source_title_by_scenario_index[(scenario.scenario_id, index)]]
                for index in range(1, len(scenario.evidence_events) + 1)
            ]
            selected_event_id = event_ids[0] if event_ids else None

            if include_memory_chunks:
                event_id_by_index = {index: event_id for index, event_id in enumerate(event_ids, start=1)}
                for row in chunk_rows_for_scenario(scenario, memory_item_id):
                    if row["source_event_id"] is not None:
                        row["source_event_id"] = event_id_by_index[row["source_event_id"]]
                    chunk_rows.append(row)

            filled_slots = set(scenario.provided_slots) | set(scenario.evidence_slots)
            for slot in PROFILE_REQUIRED_SLOTS[scenario.profile]:
                status = "filled" if slot in filled_slots else "missing"
                slot_rows.append(
                    {
                        "memory_item_id": memory_item_id,
                        "profile": scenario.profile,
                        "slot_name": slot,
                        "query_text": f"Find evidence for {slot} in anonymized workload handover {scenario.scenario_id}.",
                        "retrieved_event_ids": json.dumps(event_ids),
                        "selected_event_id": selected_event_id,
                        "fill_result": f"{slot} is {status} for this handover.",
                        "confidence": 0.92 if status == "filled" else 0.15,
                        "status": status,
                    }
                )

            result = detector.detect_scenario(scenario)
            for gap in result.gaps:
                gap_rows.append(
                    {
                        "memory_item_id": memory_item_id,
                        "profile": scenario.profile,
                        "task_context": scenario.task_context,
                        "gap_type": gap.gap_type,
                        "slot_name": gap.slot_name,
                        "description": gap.description,
                        "severity": gap.severity,
                        "required_evidence_type": f"{gap.slot_name}_evidence",
                        "status": "open",
                    }
                )
            for question in result.questions:
                question_candidates.append(
                    {
                        "memory_item_id": memory_item_id,
                        "profile": scenario.profile,
                        "slot_name": question.slot_name,
                        "question": question.question,
                        "target_person_name": "handover owner",
                        "priority": "high" if question.slot_name in {"authority", "communication_status"} else "medium",
                        "status": "open",
                    }
                )
            transfer_rows.append(
                {
                    "memory_item_id": memory_item_id,
                    "profile": scenario.profile,
                    "task_context": scenario.task_context,
                    "transferability_score": result.transferability_score,
                    "unsafe_reason": "profile-required slots still need clarification" if result.gaps else None,
                    "required_gaps_count": len(result.gaps),
                    "status": "blocked" if result.transferability_status != "transferable" else "transferable",
                }
            )

        if chunk_rows:
            connection.execute(
                text(
                    """
                    INSERT INTO memory_chunks (
                      memory_item_id, source_event_id, content, embedding, chunk_kind, metadata
                    ) VALUES (
                      :memory_item_id, :source_event_id, :content, :embedding, :chunk_kind, :metadata
                    )
                    """
                ),
                chunk_rows,
            )
            counts["memory_chunks"] += len(chunk_rows)

        connection.execute(
            text(
                """
                INSERT INTO slot_fill_attempts (
                  memory_item_id, profile, slot_name, query_text,
                  retrieved_event_ids, selected_event_id, fill_result, confidence, status
                ) VALUES (
                  :memory_item_id, :profile, :slot_name, :query_text,
                  :retrieved_event_ids, :selected_event_id, :fill_result, :confidence, :status
                )
                """
            ),
            slot_rows,
        )
        counts["slot_fill_attempts"] += len(slot_rows)

        if gap_rows:
            connection.execute(
                text(
                    """
                    INSERT INTO context_gaps (
                      memory_item_id, profile, task_context, gap_type, slot_name,
                      description, severity, required_evidence_type, status
                    ) VALUES (
                      :memory_item_id, :profile, :task_context, :gap_type, :slot_name,
                      :description, :severity, :required_evidence_type, :status
                    )
                    """
                ),
                gap_rows,
            )
            counts["context_gaps"] += len(gap_rows)

        gap_ids = _select_gap_ids(connection, sqlalchemy, text, [row["memory_item_id"] for row in gap_rows])
        question_rows = []
        for question in question_candidates:
            gap_id = gap_ids.get((question["memory_item_id"], question["profile"], question["slot_name"]))
            if gap_id is None:
                continue
            question_rows.append(
                {
                    "context_gap_id": gap_id,
                    "question": question["question"],
                    "target_person_name": question["target_person_name"],
                    "priority": question["priority"],
                    "status": question["status"],
                }
            )
        if question_rows:
            connection.execute(
                text(
                    """
                    INSERT INTO clarification_questions (
                      context_gap_id, question, target_person_name, priority, status
                    ) VALUES (
                      :context_gap_id, :question, :target_person_name, :priority, :status
                    )
                    """
                ),
                question_rows,
            )
            counts["clarification_questions"] += len(question_rows)

        connection.execute(
            text(
                """
                INSERT INTO transfer_assessments (
                  memory_item_id, profile, task_context, transferability_score,
                  unsafe_reason, required_gaps_count, status
                ) VALUES (
                  :memory_item_id, :profile, :task_context, :transferability_score,
                  :unsafe_reason, :required_gaps_count, :status
                )
                """
            ),
            transfer_rows,
        )
        counts["transfer_assessments"] += len(transfer_rows)
    return counts


def _select_id_map(connection: Any, sqlalchemy: Any, text: Any, table_name: str, key_name: str, keys: list[str]) -> dict[str, int]:
    if not keys:
        return {}
    statement = text(f"SELECT id, {key_name} FROM {table_name} WHERE {key_name} IN :keys").bindparams(
        sqlalchemy.bindparam("keys", expanding=True)
    )
    rows = connection.execute(statement, {"keys": keys}).mappings().all()
    return {row[key_name]: row["id"] for row in rows}


def _select_gap_ids(
    connection: Any,
    sqlalchemy: Any,
    text: Any,
    memory_item_ids: list[int],
) -> dict[tuple[int, str, str], int]:
    if not memory_item_ids:
        return {}
    statement = text(
        """
        SELECT id, memory_item_id, profile, slot_name
        FROM context_gaps
        WHERE memory_item_id IN :memory_item_ids
          AND status = 'open'
        """
    ).bindparams(sqlalchemy.bindparam("memory_item_ids", expanding=True))
    rows = connection.execute(statement, {"memory_item_ids": list(set(memory_item_ids))}).mappings().all()
    return {(row["memory_item_id"], row["profile"], row["slot_name"]): row["id"] for row in rows}


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# TiDB Generated Workload Audit Result",
        "",
        f"- Observed at: {datetime.now(timezone.utc).date().isoformat()}",
        f"- Scale label: `{result.get('scale_label') or 'n/a'}`",
        f"- Live TiDB scenarios persisted: {result['scenario_count']}",
        f"- Memory chunks included: `{result['include_memory_chunks']}`",
        f"- Insert duration: `{result['insert_duration_ms']} ms`",
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
