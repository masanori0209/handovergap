from contextlib import contextmanager

import handovergap.stores.tidb as tidb_module
from handovergap import TiDBStore


class FakeSQLAlchemy:
    @staticmethod
    def text(statement: str) -> str:
        return statement


class FakeConnection:
    def __init__(self) -> None:
        self.calls = []

    def execute(self, statement, payload=None) -> None:
        self.calls.append((statement, payload))
        return FakeResult()


class FakeResult:
    def mappings(self):
        return self

    def all(self):
        return [
            {
                "chunk_id": 10,
                "memory_item_id": 1,
                "source_event_id": 7,
                "chunk_kind": "evidence",
                "content": "chat: customer was informed",
                "distance": 0.12,
                "score": 0.88,
            }
        ]


class FakeEngine:
    def __init__(self) -> None:
        self.connection = FakeConnection()

    @contextmanager
    def begin(self):
        yield self.connection


def test_persist_gap_workflow_batches(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    inserted = store.persist_context_gaps(
        [
            {
                "memory_item_id": 1,
                "profile": "CS",
                "task_context": "customer support",
                "gap_type": "authority_gap",
                "slot_name": "authority",
                "description": "answer boundary is missing",
                "severity": "HIGH",
                "required_evidence_type": "approval",
                "status": "open",
            }
        ],
        engine=engine,
    )

    assert inserted == 1
    assert "INSERT INTO context_gaps" in engine.connection.calls[0][0]


def test_empty_persistence_batch_does_not_connect() -> None:
    store = TiDBStore("mysql+pymysql://unused")

    assert store.persist_slot_fill_attempts([]) == 0
    assert store.persist_transfer_assessments([]) == 0


def test_persist_memory_chunks_batches(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    inserted = store.persist_memory_chunks(
        [
            {
                "memory_item_id": 1,
                "source_event_id": 7,
                "content": "chat: customer was informed",
                "embedding": "[0.1,0.2]",
                "chunk_kind": "evidence",
                "metadata": '{"source_type":"chat"}',
            }
        ],
        engine=engine,
    )

    assert inserted == 1
    assert "INSERT INTO memory_chunks" in engine.connection.calls[0][0]


def test_reset_schema_drops_packaged_tables_in_reverse_order(monkeypatch) -> None:
    engine = FakeEngine()
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())

    TiDBStore("mysql://example").reset_schema(engine)

    statements = [call[0] for call in engine.connection.calls]
    assert statements[0] == "DROP TABLE IF EXISTS evaluation_runs"
    assert statements[-1] == "DROP TABLE IF EXISTS source_events"


def test_retrieve_memory_chunks_by_vector_uses_tidb_cosine_distance(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    chunks = store.retrieve_memory_chunks_by_vector([0.1, 0.2], top_k=1, memory_item_id=1, engine=engine)

    statement, params = engine.connection.calls[0]
    assert "VEC_COSINE_DISTANCE" in statement
    assert "ORDER BY distance ASC" in statement
    assert params["top_k"] == 1
    assert chunks[0].chunk_id == "10"


def test_retrieve_memory_chunks_by_full_text_uses_match_against(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    chunks = store.retrieve_memory_chunks_by_full_text("API延期 S001", top_k=1, memory_item_id=1, engine=engine)

    statement, params = engine.connection.calls[0]
    assert "MATCH(content) AGAINST (:query_text)" in statement
    assert "ORDER BY score DESC" in statement
    assert params["query_text"] == "API延期 S001"
    assert chunks[0].chunk_id == "10"


def test_retrieve_memory_chunks_hybrid_merges_vector_and_full_text(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    chunks = store.retrieve_memory_chunks_hybrid("API延期 S001", [0.1, 0.2], top_k=1, memory_item_id=1, engine=engine)

    assert len(engine.connection.calls) == 2
    assert chunks[0].chunk_id == "10"


def test_persist_evaluation_runs(monkeypatch) -> None:
    monkeypatch.setattr(tidb_module, "_load_sqlalchemy", lambda: FakeSQLAlchemy())
    store = TiDBStore("mysql+pymysql://unused")
    engine = FakeEngine()

    inserted = store.persist_evaluation_runs(
        [
            {
                "method_name": "handovergap/optimistic",
                "dataset_name": "HandoverGapBench holdout",
                "metrics_json": '{"tacit_gap_recall":0.64}',
            }
        ],
        engine=engine,
    )

    assert inserted == 1
    assert "INSERT INTO evaluation_runs" in engine.connection.calls[0][0]
