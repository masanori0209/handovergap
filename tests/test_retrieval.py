from typer.testing import CliRunner

from handovergap.cli import app
from handovergap.retrieval import (
    EMBEDDING_DIMENSIONS,
    chunk_rows_for_scenario,
    embedding_literal,
    hash_embedding,
    reciprocal_rank_fusion,
    retrieve_slot_evidence_full_text_local,
    retrieve_slot_evidence_hybrid_local,
    retrieve_slot_evidence_local,
    slot_query_text,
)
from handovergap.store import InMemoryStore


def test_hash_embedding_is_deterministic_and_tidb_serializable() -> None:
    first = hash_embedding("customer communication status")
    second = hash_embedding("customer communication status")

    assert first == second
    assert len(first) == EMBEDDING_DIMENSIONS
    assert embedding_literal(first).startswith("[")


def test_local_slot_evidence_retrieval_ranks_chunks() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")

    chunks = retrieve_slot_evidence_local(scenario, "communication_status", top_k=2)

    assert len(chunks) == 2
    assert chunks[0].distance <= chunks[1].distance
    assert chunks[0].source_event_id is not None


def test_local_full_text_and_hybrid_retrieval_return_chunks() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")

    full_text_chunks = retrieve_slot_evidence_full_text_local(scenario, "communication_status", top_k=2)
    hybrid_chunks = retrieve_slot_evidence_hybrid_local(scenario, "communication_status", top_k=2)

    assert len(full_text_chunks) == 2
    assert len(hybrid_chunks) == 2
    assert hybrid_chunks[0].distance <= hybrid_chunks[1].distance


def test_reciprocal_rank_fusion_merges_vector_and_full_text_results() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")
    vector_chunks = retrieve_slot_evidence_local(scenario, "communication_status", top_k=2)
    full_text_chunks = list(reversed(vector_chunks))

    merged = reciprocal_rank_fusion(vector_chunks, full_text_chunks, top_k=2)

    assert {chunk.chunk_id for chunk in merged} == {chunk.chunk_id for chunk in vector_chunks}


def test_chunk_rows_for_scenario_include_memory_and_evidence_vectors() -> None:
    scenario = InMemoryStore.from_builtin_dataset().get_scenario("S001", "CS")

    rows = chunk_rows_for_scenario(scenario, memory_item_id=101)

    assert len(rows) == 1 + len(scenario.evidence_events)
    assert rows[0]["chunk_kind"] == "memory"
    assert rows[1]["chunk_kind"] == "evidence"
    assert rows[1]["embedding"].startswith("[")


def test_retrieve_evidence_cli_prints_ranked_chunks() -> None:
    result = CliRunner().invoke(
        app,
        ["retrieve-evidence", "--scenario", "S001", "--profile", "CS", "--slot", "communication_status", "--mode", "hybrid"],
    )

    assert result.exit_code == 0
    assert "Slot evidence" in result.output
    assert "retrieved_event_ids" in result.output


def test_slot_query_text_includes_profile_task_and_slot() -> None:
    query = slot_query_text(slot_name="authority", profile="CS", task_context="Answer customer")

    assert "profile=CS" in query
    assert "required_slot=authority" in query
