from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from typing import Any

from handovergap.audit import transfer_audit_sql
from handovergap.retrieval import EvidenceChunk, embedding_literal, reciprocal_rank_fusion


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

    @staticmethod
    def transfer_audit_sql() -> str:
        return transfer_audit_sql()

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

    def reset_schema(self, engine: Any | None = None) -> None:
        """Drop packaged HandoverGap tables.

        This is intended for alpha validation environments only. Production
        deployments should use explicit migrations once the schema stabilizes.
        """

        sqlalchemy = _load_sqlalchemy()
        active_engine = engine or self.create_engine()
        with active_engine.begin() as connection:
            for table_name in reversed(_schema_table_names(self.schema_sql())):
                connection.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table_name}"))

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
        with active_engine.begin() as connection:
            rows = connection.execute(sqlalchemy.text(statement), params).mappings().all()
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
        with active_engine.begin() as connection:
            rows = connection.execute(sqlalchemy.text(statement), params).mappings().all()
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


def _schema_table_names(schema_sql: str) -> list[str]:
    table_names = []
    for statement in _split_sql_statements(schema_sql):
        parts = statement.split()
        if len(parts) >= 3 and parts[0].upper() == "CREATE" and parts[1].upper() == "TABLE":
            table_names.append(parts[2].strip("`"))
    return table_names


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
