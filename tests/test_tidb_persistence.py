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
                "successor_role": "CS",
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
