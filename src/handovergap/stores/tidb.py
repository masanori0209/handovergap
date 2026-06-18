from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from handovergap.audit import transfer_audit_sql
from handovergap.retrieval import EvidenceChunk, embedding_literal, reciprocal_rank_fusion

SCHEMA_NAME = "handovergap"
SCHEMA_VERSION = "1"
RESET_CONFIRMATION = "drop-handovergap-tables"


class TiDBDependencyError(RuntimeError):
    """Raised when a live TiDB operation is requested without the optional extra."""


class TiDBStoreOperationError(RuntimeError):
    """Raised when TiDB rejects or cannot complete a live store operation."""


@dataclass(frozen=True)
class TiDBSchemaState:
    """Observed packaged-schema metadata from a TiDB database."""

    schema_name: str
    schema_version: str | None
    expected_schema_version: str
    is_current: bool


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

    @staticmethod
    def transfer_audit_sql() -> str:
        return transfer_audit_sql()

    def create_engine(self, **kwargs: Any) -> Any:
        sqlalchemy = _load_sqlalchemy()
        try:
            return sqlalchemy.create_engine(self.database_url, **kwargs)
        except Exception as exc:  # pragma: no cover - exercised with fake errors in tests
            raise TiDBStoreOperationError(
                f"Could not create TiDB engine for {_redact_database_url(str(self.database_url))}. "
                "Check HANDOVERGAP_TIDB_URL or TIDB_HOST/TIDB_USER/TIDB_PASSWORD."
            ) from exc

    def create_schema(self, engine: Any | None = None) -> None:
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        statements = _split_sql_statements(self.schema_sql())
        try:
            with active_engine.begin() as connection:
                for statement in statements:
                    connection.execute(sqlalchemy.text(_make_create_table_idempotent(statement)))
                _write_schema_metadata(connection, sqlalchemy)
        except Exception as exc:
            raise _operation_error("create schema", self.database_url, exc) from exc

    def schema_state(self, engine: Any | None = None) -> TiDBSchemaState:
        """Read packaged-schema metadata from TiDB.

        Missing metadata means the schema was not created by a lifecycle-aware
        HandoverGap release or the database still needs `create_schema(...)`.
        """

        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        try:
            with active_engine.begin() as connection:
                row = (
                    connection.execute(
                        sqlalchemy.text(
                            """
                            SELECT schema_name, schema_version
                            FROM handovergap_schema_metadata
                            WHERE schema_name = :schema_name
                            """
                        ),
                        {"schema_name": SCHEMA_NAME},
                    )
                    .mappings()
                    .first()
                )
        except Exception as exc:
            raise _operation_error("read schema metadata", self.database_url, exc) from exc
        if row is None:
            return TiDBSchemaState(
                schema_name=SCHEMA_NAME,
                schema_version=None,
                expected_schema_version=SCHEMA_VERSION,
                is_current=False,
            )
        schema_version = str(row["schema_version"])
        return TiDBSchemaState(
            schema_name=str(row["schema_name"]),
            schema_version=schema_version,
            expected_schema_version=SCHEMA_VERSION,
            is_current=schema_version == SCHEMA_VERSION,
        )

    def reset_schema(self, engine: Any | None = None) -> None:
        """Drop packaged HandoverGap tables.

        This compatibility alias is intended for validation-only resets. Prefer
        `destructive_reset_schema(..., confirm="drop-handovergap-tables")` in
        scripts so destructive intent is visible at the call site.
        """

        self.destructive_reset_schema(engine=engine, confirm=RESET_CONFIRMATION)

    def destructive_reset_schema(self, engine: Any | None = None, *, confirm: str) -> None:
        """Drop packaged HandoverGap tables after explicit confirmation.

        Use only on validation databases without user data. This removes
        the packaged audit tables and schema metadata.
        """

        if confirm != RESET_CONFIRMATION:
            raise ValueError(f'destructive_reset_schema requires confirm="{RESET_CONFIRMATION}"')
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        try:
            with active_engine.begin() as connection:
                for table_name in reversed(_schema_table_names(self.schema_sql())):
                    connection.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table_name}"))
        except Exception as exc:
            raise _operation_error("reset schema", self.database_url, exc) from exc

    def persist_memory_item(
        self,
        row: dict[str, Any],
        engine: Any | None = None,
        *,
        on_duplicate: str = "update",
    ) -> int:
        """Insert one memory item and return its id.

        `scenario_id` is unique in the packaged schema. The default duplicate
        policy updates mutable fields and returns the existing id, which makes
        repeated validation runs with the same scenario id safe.
        """

        if on_duplicate not in {"update", "ignore", "error"}:
            raise ValueError("on_duplicate must be one of: update, ignore, error")
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        statement = _memory_item_insert_sql(on_duplicate=on_duplicate)
        try:
            with active_engine.begin() as connection:
                connection.execute(sqlalchemy.text(statement), row)
                result = connection.execute(
                    sqlalchemy.text("SELECT id FROM memory_items WHERE scenario_id = :scenario_id"),
                    {"scenario_id": row["scenario_id"]},
                )
                return int(result.scalar_one())
        except Exception as exc:
            raise _operation_error("persist memory item", self.database_url, exc) from exc

    def persist_slot_fill_attempts(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO slot_fill_attempts (
              memory_item_id, profile, slot_name, query_text,
              retrieved_event_ids, selected_event_id, fill_result, confidence, status
            ) VALUES (
              :memory_item_id, :profile, :slot_name, :query_text,
              :retrieved_event_ids, :selected_event_id, :fill_result, :confidence, :status
            )
            """,
            rows,
            engine,
        )

    def persist_memory_chunks(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO memory_chunks (
              memory_item_id, source_event_id, content, embedding, chunk_kind, metadata
            ) VALUES (
              :memory_item_id, :source_event_id, :content, :embedding, :chunk_kind, :metadata
            )
            """,
            rows,
            engine,
        )

    def retrieve_memory_chunks_by_vector(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        memory_item_id: int | None = None,
        engine: Any | None = None,
    ) -> list[EvidenceChunk]:
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        query_vector = embedding_literal(query_embedding)
        statement = _memory_chunk_vector_search_sql(memory_item_id=memory_item_id)
        params = {"query_vector": query_vector, "top_k": top_k}
        if memory_item_id is not None:
            params["memory_item_id"] = memory_item_id
        try:
            with active_engine.begin() as connection:
                rows = connection.execute(sqlalchemy.text(statement), params).mappings().all()
        except Exception as exc:
            raise _operation_error("retrieve memory chunks by vector", self.database_url, exc) from exc
        return [
            EvidenceChunk(
                chunk_id=str(row["chunk_id"]),
                memory_item_id=row["memory_item_id"],
                source_event_id=row["source_event_id"],
                source_type=row["chunk_kind"],
                content=row["content"],
                distance=float(row["distance"]),
            )
            for row in rows
        ]

    def retrieve_memory_chunks_by_full_text(
        self,
        query_text: str,
        *,
        top_k: int = 5,
        memory_item_id: int | None = None,
        engine: Any | None = None,
    ) -> list[EvidenceChunk]:
        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        statement = _memory_chunk_full_text_search_sql(memory_item_id=memory_item_id)
        params = {"query_text": query_text, "top_k": top_k}
        if memory_item_id is not None:
            params["memory_item_id"] = memory_item_id
        try:
            with active_engine.begin() as connection:
                rows = connection.execute(sqlalchemy.text(statement), params).mappings().all()
        except Exception as exc:
            raise _operation_error("retrieve memory chunks by full text", self.database_url, exc) from exc
        return [
            EvidenceChunk(
                chunk_id=str(row["chunk_id"]),
                memory_item_id=row["memory_item_id"],
                source_event_id=row["source_event_id"],
                source_type=row["chunk_kind"],
                content=row["content"],
                distance=1.0 - float(row["score"] or 0.0),
            )
            for row in rows
        ]

    def retrieve_memory_chunks_hybrid(
        self,
        query_text: str,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        memory_item_id: int | None = None,
        engine: Any | None = None,
    ) -> list[EvidenceChunk]:
        vector_chunks = self.retrieve_memory_chunks_by_vector(
            query_embedding,
            top_k=max(top_k * 2, top_k),
            memory_item_id=memory_item_id,
            engine=engine,
        )
        full_text_chunks = self.retrieve_memory_chunks_by_full_text(
            query_text,
            top_k=max(top_k * 2, top_k),
            memory_item_id=memory_item_id,
            engine=engine,
        )
        return reciprocal_rank_fusion(vector_chunks, full_text_chunks, top_k=top_k)

    def persist_context_gaps(self, rows: Iterable[dict[str, Any]], engine: Any | None = None) -> int:
        return self._insert_rows(
            """
            INSERT INTO context_gaps (
              memory_item_id, profile, task_context, gap_type, slot_name,
              description, severity, required_evidence_type, status
            ) VALUES (
              :memory_item_id, :profile, :task_context, :gap_type, :slot_name,
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
              memory_item_id, profile, task_context, transferability_score,
              unsafe_reason, required_gaps_count, status
            ) VALUES (
              :memory_item_id, :profile, :task_context, :transferability_score,
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
        try:
            with active_engine.begin() as connection:
                connection.execute(sqlalchemy.text(statement), payload)
        except Exception as exc:
            raise _operation_error("insert audit rows", self.database_url, exc) from exc
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


def _schema_table_names(schema_sql: str) -> list[str]:
    table_names = []
    for statement in _split_sql_statements(schema_sql):
        parts = statement.split()
        if len(parts) >= 3 and parts[0].upper() == "CREATE" and parts[1].upper() == "TABLE":
            table_names.append(parts[2].strip("`"))
    return table_names


def _write_schema_metadata(connection: Any, sqlalchemy: Any) -> None:
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO handovergap_schema_metadata (
              schema_name, schema_version, package_name, metadata
            ) VALUES (
              :schema_name, :schema_version, :package_name, :metadata
            )
            ON DUPLICATE KEY UPDATE
              schema_version = VALUES(schema_version),
              package_name = VALUES(package_name),
              metadata = VALUES(metadata),
              applied_at = CURRENT_TIMESTAMP
            """
        ),
        {
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "package_name": "handovergap",
            "metadata": '{"purpose":"audit_store"}',
        },
    )


def _memory_item_insert_sql(*, on_duplicate: str) -> str:
    base = """
        INSERT INTO memory_items (
          scenario_id, subject, memory_type, content,
          source_person_name, project_name, status, confidence
        ) VALUES (
          :scenario_id, :subject, :memory_type, :content,
          :source_person_name, :project_name, :status, :confidence
        )
    """
    if on_duplicate == "error":
        return base
    if on_duplicate == "ignore":
        return base.replace("INSERT INTO", "INSERT IGNORE INTO", 1)
    return (
        base
        + """
        ON DUPLICATE KEY UPDATE
          subject = VALUES(subject),
          memory_type = VALUES(memory_type),
          content = VALUES(content),
          source_person_name = VALUES(source_person_name),
          project_name = VALUES(project_name),
          status = VALUES(status),
          confidence = VALUES(confidence)
        """
    )


def _operation_error(operation: str, database_url: object, exc: Exception) -> TiDBStoreOperationError:
    return TiDBStoreOperationError(
        f"TiDB {operation} failed for {_redact_database_url(str(database_url))}. "
        "Check credentials, host allowlist, database name, TLS/CA settings, and whether the packaged schema exists."
    )


def _redact_database_url(database_url: str) -> str:
    try:
        parts = urlsplit(database_url)
    except ValueError:
        return "<redacted-database-url>"
    if not parts.netloc:
        return "<redacted-database-url>"
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    username = parts.username or ""
    auth = f"{username}:***@" if username else ""
    return urlunsplit((parts.scheme, f"{auth}{host}{port}", parts.path, "", ""))


def _memory_chunk_vector_search_sql(*, memory_item_id: int | None = None) -> str:
    where = "WHERE embedding IS NOT NULL"
    if memory_item_id is not None:
        where += " AND memory_item_id = :memory_item_id"
    return f"""
        SELECT
          id AS chunk_id,
          memory_item_id,
          source_event_id,
          chunk_kind,
          content,
          VEC_COSINE_DISTANCE(embedding, :query_vector) AS distance
        FROM memory_chunks
        {where}
        ORDER BY distance ASC
        LIMIT :top_k
    """


def _memory_chunk_full_text_search_sql(*, memory_item_id: int | None = None) -> str:
    where = "WHERE MATCH(content) AGAINST (:query_text)"
    if memory_item_id is not None:
        where += " AND memory_item_id = :memory_item_id"
    return f"""
        SELECT
          id AS chunk_id,
          memory_item_id,
          source_event_id,
          chunk_kind,
          content,
          MATCH(content) AGAINST (:query_text) AS score
        FROM memory_chunks
        {where}
        ORDER BY score DESC
        LIMIT :top_k
    """
