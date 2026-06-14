from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime

from handovergap import TiDBStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate live TiDB persistence for HandoverGap.")
    parser.add_argument("--create-schema", action="store_true", help="Create the packaged HandoverGap schema first.")
    args = parser.parse_args()

    _load_dotenv_if_available()

    try:
        from sqlalchemy import URL, text
    except ImportError as exc:
        raise SystemExit('Missing TiDB dependencies. Run: pip install -e ".[tidb]"') from exc

    database_url = os.getenv("HANDOVERGAP_TIDB_URL")
    if database_url:
        store = TiDBStore(database_url)
    else:
        store = TiDBStore(
            URL.create(
                drivername="mysql+pymysql",
                username=_required_env("TIDB_USER"),
                password=_required_env("TIDB_PASSWORD"),
                host=_required_env("TIDB_HOST"),
                port=int(os.getenv("TIDB_PORT", "4000")),
                database=os.getenv("TIDB_DB_NAME", "test"),
            )
        )

    connect_args = _connect_args()
    engine = store.create_engine(pool_recycle=300, connect_args=connect_args)

    if args.create_schema:
        store.create_schema(engine)

    scenario_id = "LIVE-TIDB-" + datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    with engine.begin() as connection:
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
                "scenario_id": scenario_id,
                "subject": "Synthetic TiDB live validation",
                "memory_type": "customer_release_decision",
                "content": "Synthetic memory: use CSV for this release; API is next phase.",
                "source_person_name": "synthetic",
                "project_name": "handovergap-live-check",
                "status": "active",
                "confidence": 0.99,
            },
        )
        memory_item_id = connection.execute(
            text("SELECT id FROM memory_items WHERE scenario_id = :scenario_id"),
            {"scenario_id": scenario_id},
        ).scalar_one()

    slot_rows = [
        {
            "memory_item_id": memory_item_id,
            "successor_role": "CS",
            "slot_name": "customer_notification_status",
            "query_text": "Was the customer informed about CSV-only support?",
            "retrieved_event_ids": json.dumps([]),
            "selected_event_id": None,
            "fill_result": None,
            "confidence": 0.0,
            "status": "missing",
        }
    ]
    gap_rows = [
        {
            "memory_item_id": memory_item_id,
            "successor_role": "CS",
            "task_context": "Answering a customer-support handover question.",
            "gap_type": "missing_required_slot",
            "slot_name": "customer_notification_status",
            "description": "The retrieved memory is correct but lacks customer communication status.",
            "severity": "high",
            "required_evidence_type": "customer_notification_record",
            "status": "open",
        }
    ]
    assessment_rows = [
        {
            "memory_item_id": memory_item_id,
            "successor_role": "CS",
            "task_context": "Answering a customer-support handover question.",
            "transferability_score": 0.0,
            "unsafe_reason": "Missing customer notification status.",
            "required_gaps_count": 1,
            "status": "blocked",
        }
    ]

    inserted = {
        "slot_fill_attempts": store.persist_slot_fill_attempts(slot_rows, engine),
        "context_gaps": store.persist_context_gaps(gap_rows, engine),
        "transfer_assessments": store.persist_transfer_assessments(assessment_rows, engine),
    }
    counts = _counts(engine, memory_item_id)

    print(
        json.dumps(
            {
                "status": "ok",
                "scenario_id": scenario_id,
                "memory_item_id": memory_item_id,
                "inserted": inserted,
                "counts": counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _connect_args() -> dict[str, object]:
    ca_path = os.getenv("TIDB_CA_PATH") or os.getenv("CA_PATH")
    if not ca_path:
        return {}
    return {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
        "ssl_ca": ca_path,
    }


def _counts(engine: object, memory_item_id: int) -> dict[str, int]:
    from sqlalchemy import text

    tables = ["slot_fill_attempts", "context_gaps", "transfer_assessments"]
    with engine.connect() as connection:
        return {
            table: connection.execute(
                text(f"SELECT COUNT(*) FROM {table} WHERE memory_item_id = :memory_item_id"),
                {"memory_item_id": memory_item_id},
            ).scalar_one()
            for table in tables
        }


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
