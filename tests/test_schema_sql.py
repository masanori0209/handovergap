from handovergap import TiDBStore
from handovergap.stores.tidb import _split_sql_statements


def test_tidb_store_is_importable_without_live_connection() -> None:
    store = TiDBStore("mysql+pymysql://user:password@localhost:4000/handovergap")

    assert store.database_url.startswith("mysql+pymysql://")


def test_tidb_schema_models_slot_evidence_gap_workflow() -> None:
    schema = TiDBStore.schema_sql()

    required_tables = {
        "source_events",
        "memory_items",
        "memory_chunks",
        "memory_type_schemas",
        "successor_role_requirements",
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
    assert "retrieved_event_ids JSON" in schema


def test_tidb_schema_can_be_split_for_transactional_install() -> None:
    statements = _split_sql_statements(TiDBStore.schema_sql())

    assert len(statements) == 11
    assert all(statement.startswith("CREATE TABLE") for statement in statements)
