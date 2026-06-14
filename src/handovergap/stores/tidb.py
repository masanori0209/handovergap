from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from typing import Any


class TiDBDependencyError(RuntimeError):
    """Raised when a live TiDB operation is requested without the optional extra."""


@dataclass(frozen=True)
class TiDBStore:
    """Optional TiDB-backed persistence adapter.

    Constructing and importing this class does not require SQLAlchemy or a live
    TiDB connection. Optional dependencies are loaded only for live operations.
    """

    database_url: str

    @staticmethod
    def schema_sql() -> str:
        return resources.files("handovergap.data").joinpath("schema.sql").read_text()

    def create_engine(self, **kwargs: Any) -> Any:
        sqlalchemy = _load_sqlalchemy()
        return sqlalchemy.create_engine(self.database_url, **kwargs)

    def create_schema(self, engine: Any | None = None) -> None:
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        statements = _split_sql_statements(self.schema_sql())
        with active_engine.begin() as connection:
            for statement in statements:
                connection.execute(sqlalchemy.text(_make_create_table_idempotent(statement)))

    def persist_slot_fill_attempts(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO slot_fill_attempts (
              memory_item_id, successor_role, slot_name, query_text,
              retrieved_event_ids, selected_event_id, fill_result, confidence, status
            ) VALUES (
              :memory_item_id, :successor_role, :slot_name, :query_text,
              :retrieved_event_ids, :selected_event_id, :fill_result, :confidence, :status
            )
            """,
            rows,
            engine,
        )

    def persist_context_gaps(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO context_gaps (
              memory_item_id, successor_role, task_context, gap_type, slot_name,
              description, severity, required_evidence_type, status
            ) VALUES (
              :memory_item_id, :successor_role, :task_context, :gap_type, :slot_name,
              :description, :severity, :required_evidence_type, :status
            )
            """,
            rows,
            engine,
        )

    def persist_transfer_assessments(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO transfer_assessments (
              memory_item_id, successor_role, task_context, transferability_score,
              unsafe_reason, required_gaps_count, status
            ) VALUES (
              :memory_item_id, :successor_role, :task_context, :transferability_score,
              :unsafe_reason, :required_gaps_count, :status
            )
            """,
            rows,
            engine,
        )

    def persist_evaluation_runs(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO evaluation_runs (
              method_name, dataset_name, metrics_json
            ) VALUES (
              :method_name, :dataset_name, :metrics_json
            )
            """,
            rows,
            engine,
        )

    def _insert_rows(self, statement: str, rows: Iterable[dict[str, Any]], engine: Any | None) -> int:
        payload = list(rows)
        if not payload:
            return 0
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        with active_engine.begin() as connection:
            connection.execute(sqlalchemy.text(statement), payload)
        return len(payload)


def _load_sqlalchemy() -> Any:
    try:
        import sqlalchemy
    except ImportError as exc:
        raise TiDBDependencyError(
            'Live TiDB operations require the optional extra: pip install "handovergap[tidb]"'
        ) from exc
    return sqlalchemy


def _split_sql_statements(schema_sql: str) -> list[str]:
    statements = []
    current_lines = []
    for line in schema_sql.splitlines():
        if line.lstrip().startswith("--"):
            continue
        current_lines.append(line)
        if line.rstrip().endswith(";"):
            statement = "\n".join(current_lines).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            current_lines = []
    trailing = "\n".join(current_lines).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _make_create_table_idempotent(statement: str) -> str:
    if statement.lstrip().upper().startswith("CREATE TABLE "):
        return statement.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
    return statement
