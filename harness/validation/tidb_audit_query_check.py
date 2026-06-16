from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Any

from handovergap.audit import diverse_audit_sample_rows
from handovergap import TiDBStore
from handovergap.core.detector import HandoverGapDetector
from handovergap.retrieval import chunk_rows_for_scenario
from handovergap.slot_rules import PROFILE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the HandoverGap blocked-transfer audit query on live TiDB.")
    parser.add_argument("--dataset", default="sanitized", help="Built-in dataset to persist: sanitized, adversarial, holdout, mini, or all.")
    parser.add_argument("--iterations", type=int, default=30, help="Repeated SELECT runs for p50/p95 timing.")
    parser.add_argument("--create-schema", action="store_true", help="Create the packaged HandoverGap schema first.")
    parser.add_argument(
        "--reset-schema",
        action="store_true",
        help="Drop packaged HandoverGap tables before creating them. Intended for alpha validation DBs only.",
    )
    parser.add_argument("--output-json", default="article/tidb_audit_query_results.json", help="Path for JSON results.")
    parser.add_argument("--output-md", default="article/tidb_audit_query_results.md", help="Path for markdown summary.")
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

    run_id = "AUDIT-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    scenarios = InMemoryStore.from_builtin_dataset(args.dataset).list_scenarios()
    inserted = _persist_dataset(engine, text, scenarios, run_id)
    timings, rows = _measure_audit_query(engine, text, run_id, args.iterations)
    explain_rows = _explain_audit_query(engine, text, run_id)

    result = {
        "status": "ok",
        "run_id": run_id,
        "dataset": args.dataset,
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
        "sample_rows": diverse_audit_sample_rows(rows, limit=8),
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


def _persist_dataset(engine: Any, text: Any, scenarios: list[Any], run_id: str) -> dict[str, int]:
    detector = HandoverGapDetector(store=InMemoryStore(scenarios))
    counts = {
        "source_events": 0,
        "memory_items": 0,
        "memory_chunks": 0,
        "slot_fill_attempts": 0,
        "context_gaps": 0,
        "clarification_questions": 0,
        "transfer_assessments": 0,
    }
    with engine.begin() as connection:
        for scenario in scenarios:
            scenario_key = f"{run_id}-{scenario.scenario_id}"
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
                {
                    "scenario_id": scenario_key,
                    "subject": f"Anonymized handover {scenario.scenario_id}",
                    "memory_type": scenario.memory_type,
                    "content": scenario.memory,
                    "source_person_name": "anonymized",
                    "project_name": "handovergap-live-audit",
                    "status": "active",
                    "confidence": 0.95,
                },
            )
            counts["memory_items"] += 1
            memory_item_id = connection.execute(
                text("SELECT id FROM memory_items WHERE scenario_id = :scenario_id"),
                {"scenario_id": scenario_key},
            ).scalar_one()

            evidence_ids = []
            for index, event in enumerate(scenario.evidence_events, start=1):
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
                    {
                        "source_type": event.source_type,
                        "title": f"{scenario.scenario_id} evidence {index}: {event.source_type}",
                        "content": event.content,
                        "actor_name": "anonymized",
                        "project_name": "handovergap-live-audit",
                        "metadata": json.dumps({"run_id": run_id, "scenario_id": scenario.scenario_id}),
                    },
                )
                event_id = connection.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
                evidence_ids.append(event_id)
                counts["source_events"] += 1

            chunk_rows = chunk_rows_for_scenario(scenario, memory_item_id)
            event_id_by_index = {index: event_id for index, event_id in enumerate(evidence_ids, start=1)}
            for row in chunk_rows:
                if row["source_event_id"] is not None:
                    row["source_event_id"] = event_id_by_index[row["source_event_id"]]
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

            filled_slots = set(scenario.provided_slots) | set(scenario.evidence_slots)
            selected_event_id = evidence_ids[0] if evidence_ids else None
            for slot in PROFILE_REQUIRED_SLOTS[scenario.profile]:
                status = "filled" if slot in filled_slots else "missing"
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
                    {
                        "memory_item_id": memory_item_id,
                        "profile": scenario.profile,
                        "slot_name": slot,
                        "query_text": f"Find evidence for {slot} in anonymized handover {scenario.scenario_id}.",
                        "retrieved_event_ids": json.dumps(evidence_ids),
                        "selected_event_id": selected_event_id,
                        "fill_result": f"{slot} is {status} for this handover.",
                        "confidence": 0.92 if status == "filled" else 0.15,
                        "status": status,
                    },
                )
                counts["slot_fill_attempts"] += 1

            result = detector.detect_scenario(scenario)
            gap_id_by_slot = {}
            for gap in result.gaps:
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
                    },
                )
                gap_id = connection.execute(text("SELECT LAST_INSERT_ID()")).scalar_one()
                gap_id_by_slot[gap.slot_name] = gap_id
                counts["context_gaps"] += 1

            for question in result.questions:
                gap_id = gap_id_by_slot.get(question.slot_name)
                if gap_id is None:
                    continue
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
                    {
                        "context_gap_id": gap_id,
                        "question": question.question,
                        "target_person_name": "handover owner",
                        "priority": "high" if question.slot_name in {"authority", "communication_status"} else "medium",
                        "status": "open",
                    },
                )
                counts["clarification_questions"] += 1

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
                {
                    "memory_item_id": memory_item_id,
                    "profile": scenario.profile,
                    "task_context": scenario.task_context,
                    "transferability_score": result.transferability_score,
                    "unsafe_reason": "profile-required slots still need clarification" if result.gaps else None,
                    "required_gaps_count": len(result.gaps),
                    "status": "blocked" if result.transferability_status != "transferable" else "transferable",
                },
            )
            counts["transfer_assessments"] += 1
    return counts


def _measure_audit_query(engine: Any, text: Any, run_id: str, iterations: int) -> tuple[list[float], list[dict[str, Any]]]:
    query = _scoped_audit_query()
    timings = []
    last_rows: list[dict[str, Any]] = []
    with engine.connect() as connection:
        for _ in range(iterations):
            start = perf_counter()
            rows = connection.execute(text(query), {"scenario_prefix": f"{run_id}-%"}).mappings().all()
            timings.append((perf_counter() - start) * 1000)
            last_rows = [_serializable_row(row) for row in rows]
    return timings, last_rows


def _explain_audit_query(engine: Any, text: Any, run_id: str) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        rows = connection.execute(text("EXPLAIN " + _scoped_audit_query()), {"scenario_prefix": f"{run_id}-%"}).mappings().all()
    return [_serializable_row(row) for row in rows[:12]]


def _scoped_audit_query() -> str:
    return """
SELECT
  ta.status AS transfer_status,
  ta.transferability_score,
  mi.scenario_id,
  mi.subject,
  ta.profile,
  cg.gap_type,
  cg.slot_name,
  cg.severity,
  sfa.status AS slot_fill_status,
  sfa.confidence AS slot_fill_confidence,
  se.title AS selected_evidence_title,
  cq.question
FROM transfer_assessments ta
JOIN memory_items mi
  ON mi.id = ta.memory_item_id
LEFT JOIN context_gaps cg
  ON cg.memory_item_id = ta.memory_item_id
 AND cg.profile = ta.profile
 AND cg.status = 'open'
LEFT JOIN slot_fill_attempts sfa
  ON sfa.memory_item_id = cg.memory_item_id
 AND sfa.profile = cg.profile
 AND sfa.slot_name = cg.slot_name
LEFT JOIN source_events se
  ON se.id = sfa.selected_event_id
LEFT JOIN clarification_questions cq
  ON cq.context_gap_id = cg.id
WHERE ta.status = 'blocked'
  AND mi.scenario_id LIKE :scenario_prefix
ORDER BY ta.created_at DESC, cg.severity DESC, cg.slot_name
"""


def _render_markdown(result: dict[str, Any]) -> str:
    rows = result["sample_rows"][:6]
    lines = [
        "# TiDB Audit Query Live Result",
        "",
        f"- Observed at: {datetime.now(timezone.utc).date().isoformat()}",
        f"- Dataset: `{result['dataset']}`",
        f"- Scenarios persisted: {result['scenario_count']}",
        f"- Audit query result rows: {result['audit_query']['result_rows']}",
        f"- Iterations: {result['audit_query']['iterations']}",
        f"- p50 latency: `{result['audit_query']['p50_ms']} ms`",
        f"- p95 latency: `{result['audit_query']['p95_ms']} ms`",
        "",
        "This is a live TiDB Cloud validation result for the blocked-transfer audit query, not a load-test claim.",
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
            "## Sample Audit Rows",
            "",
            "| Scenario | Profile | Missing slot | Severity | Slot-fill status | Evidence | Question |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| {scenario_id} | {profile} | {slot_name} | {severity} | {slot_fill_status} | {selected_evidence_title} | {question} |".format(
                scenario_id=row.get("scenario_id", ""),
                profile=row.get("profile", ""),
                slot_name=row.get("slot_name", ""),
                severity=row.get("severity", ""),
                slot_fill_status=row.get("slot_fill_status", ""),
                selected_evidence_title=(row.get("selected_evidence_title") or "").replace("|", "/"),
                question=(row.get("question") or "").replace("|", "/"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def _serializable_row(row: Any) -> dict[str, Any]:
    return {key: _json_value(row[key]) for key in row.keys()}


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * ratio)))
    return ordered[index]


def _connect_args() -> dict[str, object]:
    ca_path = os.getenv("TIDB_CA_PATH") or os.getenv("CA_PATH")
    if not ca_path:
        return {}
    return {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
        "ssl_ca": ca_path,
    }


def _store_from_env(URL: Any) -> TiDBStore:
    database_url = os.getenv("HANDOVERGAP_TIDB_URL")
    if database_url:
        return TiDBStore(database_url)
    return TiDBStore(
        URL.create(
            drivername="mysql+pymysql",
            username=_required_env("TIDB_USER"),
            password=_required_env("TIDB_PASSWORD"),
            host=_required_env("TIDB_HOST"),
            port=int(os.getenv("TIDB_PORT", "4000")),
            database=os.getenv("TIDB_DB_NAME", "test"),
        )
    )


def _load_sqlalchemy() -> tuple[Any, Any, Any]:
    try:
        import sqlalchemy
        from sqlalchemy import URL, text
    except ImportError as exc:
        raise SystemExit('Missing TiDB dependencies. Run: pip install -e ".[tidb]"') from exc
    return sqlalchemy, text, URL


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


if __name__ == "__main__":
    raise SystemExit(main())
