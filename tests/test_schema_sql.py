from handovergap import TiDBStore
from handovergap.stores.tidb import _make_create_table_idempotent, _split_sql_statements


def test_tidb_store_is_importable_without_live_connection() -> None:
    store = TiDBStore("mysql+pymysql://user:password@localhost:4000/handovergap")

    assert store.database_url.startswith("mysql+pymysql://")


def test_tidb_schema_models_slot_evidence_gap_workflow() -> None:
    schema = TiDBStore.schema_sql()

    required_tables = {
        "handovergap_schema_metadata",
        "source_events",
        "memory_items",
        "memory_chunks",
        "memory_type_schemas",
        "profile_requirements",
        "memory_slots",
        "slot_fill_attempts",
        "context_gaps",
        "clarification_questions",
        "transfer_assessments",
        "evaluation_runs",
    }
    assert all(f"CREATE TABLE {table}" in schema for table in required_tables)
    assert "VECTOR(1536)" in schema
    assert "metadata JSON" in schema
    assert "source_event_id BIGINT" in schema
    assert "chunk_kind VARCHAR(50)" in schema
    assert "FULLTEXT INDEX idx_memory_chunks_content" in schema
    assert "retrieved_event_ids JSON" in schema


def test_tidb_transfer_audit_sql_joins_decision_to_evidence() -> None:
    query = TiDBStore.transfer_audit_sql()

    assert "FROM transfer_assessments ta" in query
    assert "JOIN memory_items mi" in query
    assert "LEFT JOIN context_gaps cg" in query
    assert "LEFT JOIN slot_fill_attempts sfa" in query
    assert "LEFT JOIN clarification_questions cq" in query
    assert "WHERE ta.status = 'blocked'" in query


def test_tidb_schema_can_be_split_for_transactional_install() -> None:
    statements = _split_sql_statements(TiDBStore.schema_sql())

    assert len(statements) == 12
    assert all(statement.startswith("CREATE TABLE") for statement in statements)


def test_create_table_statements_can_be_made_idempotent() -> None:
    statement = "CREATE TABLE source_events (id BIGINT PRIMARY KEY)"

    assert _make_create_table_idempotent(statement).startswith("CREATE TABLE IF NOT EXISTS source_events")
