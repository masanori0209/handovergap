from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

from handovergap.schemas import HandoverScenario

EMBEDDING_DIMENSIONS = 1536


@dataclass(frozen=True)
class EvidenceChunk:
    chunk_id: str
    memory_item_id: int | None
    source_event_id: int | None
    content: str
    distance: float
    source_type: str | None = None


def slot_query_text(*, slot_name: str, profile: str, task_context: str) -> str:
    return f"profile={profile}; task={task_context}; required_slot={slot_name}"


def hash_embedding(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Create a deterministic lightweight embedding for tests and dry-run demos.

    This is not a semantic production embedding. It gives the package a no-key,
    reproducible retrieval path while live systems can pass model embeddings.
    """

    vector = [0.0] * dimensions
    for token in _tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embedding_literal(embedding: list[float]) -> str:
    return json.dumps([round(value, 8) for value in embedding], separators=(",", ":"))


def retrieve_slot_evidence_local(
    scenario: HandoverScenario,
    slot_name: str,
    *,
    top_k: int = 3,
    memory_item_id: int | None = None,
) -> list[EvidenceChunk]:
    query = slot_query_text(slot_name=slot_name, profile=scenario.profile, task_context=scenario.task_context)
    query_embedding = hash_embedding(query)
    chunks = []
    for index, event in enumerate(scenario.evidence_events, start=1):
        distance = cosine_distance(query_embedding, hash_embedding(f"{event.source_type}: {event.content}"))
        chunks.append(
            EvidenceChunk(
                chunk_id=f"{scenario.scenario_id}:event:{index}",
                memory_item_id=memory_item_id,
                source_event_id=index,
                source_type=event.source_type,
                content=event.content,
                distance=distance,
            )
        )
    return sorted(chunks, key=lambda chunk: (chunk.distance, chunk.chunk_id))[:top_k]


def retrieve_slot_evidence_full_text_local(
    scenario: HandoverScenario,
    slot_name: str,
    *,
    top_k: int = 3,
    memory_item_id: int | None = None,
) -> list[EvidenceChunk]:
    query_tokens = set(_tokens(slot_query_text(slot_name=slot_name, profile=scenario.profile, task_context=scenario.task_context)))
    chunks = []
    for index, event in enumerate(scenario.evidence_events, start=1):
        content_tokens = set(_tokens(f"{event.source_type} {event.content}"))
        overlap = len(query_tokens & content_tokens)
        score = overlap / max(len(query_tokens), 1)
        chunks.append(
            EvidenceChunk(
                chunk_id=f"{scenario.scenario_id}:event:{index}",
                memory_item_id=memory_item_id,
                source_event_id=index,
                source_type=event.source_type,
                content=event.content,
                distance=1.0 - score,
            )
        )
    return sorted(chunks, key=lambda chunk: (chunk.distance, chunk.chunk_id))[:top_k]


def retrieve_slot_evidence_hybrid_local(
    scenario: HandoverScenario,
    slot_name: str,
    *,
    top_k: int = 3,
    memory_item_id: int | None = None,
) -> list[EvidenceChunk]:
    vector_chunks = retrieve_slot_evidence_local(
        scenario,
        slot_name,
        top_k=max(top_k * 2, top_k),
        memory_item_id=memory_item_id,
    )
    full_text_chunks = retrieve_slot_evidence_full_text_local(
        scenario,
        slot_name,
        top_k=max(top_k * 2, top_k),
        memory_item_id=memory_item_id,
    )
    return reciprocal_rank_fusion(vector_chunks, full_text_chunks, top_k=top_k)


def reciprocal_rank_fusion(
    vector_chunks: list[EvidenceChunk],
    full_text_chunks: list[EvidenceChunk],
    *,
    top_k: int,
    rank_constant: int = 60,
) -> list[EvidenceChunk]:
    by_id: dict[str, EvidenceChunk] = {}
    scores: dict[str, float] = {}
    for ranked_chunks in [vector_chunks, full_text_chunks]:
        for rank, chunk in enumerate(ranked_chunks, start=1):
            by_id.setdefault(chunk.chunk_id, chunk)
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (rank_constant + rank)
    merged = []
    for chunk_id, score in scores.items():
        chunk = by_id[chunk_id]
        merged.append(
            EvidenceChunk(
                chunk_id=chunk.chunk_id,
                memory_item_id=chunk.memory_item_id,
                source_event_id=chunk.source_event_id,
                source_type=chunk.source_type,
                content=chunk.content,
                distance=1.0 - score,
            )
        )
    return sorted(merged, key=lambda chunk: (chunk.distance, chunk.chunk_id))[:top_k]


def cosine_distance(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 1.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 1.0
    return 1.0 - (dot / (left_norm * right_norm))


def chunk_rows_for_scenario(scenario: HandoverScenario, memory_item_id: int) -> list[dict[str, Any]]:
    rows = [
        {
            "memory_item_id": memory_item_id,
            "source_event_id": None,
            "content": scenario.memory,
            "embedding": embedding_literal(hash_embedding(scenario.memory)),
            "chunk_kind": "memory",
            "metadata": json.dumps({"scenario_id": scenario.scenario_id}, ensure_ascii=False),
        }
    ]
    for index, event in enumerate(scenario.evidence_events, start=1):
        content = f"{event.source_type}: {event.content}"
        rows.append(
            {
                "memory_item_id": memory_item_id,
                "source_event_id": index,
                "content": content,
                "embedding": embedding_literal(hash_embedding(content)),
                "chunk_kind": "evidence",
                "metadata": json.dumps(
                    {"scenario_id": scenario.scenario_id, "source_type": event.source_type},
                    ensure_ascii=False,
                ),
            }
        )
    return rows


def _tokens(text: str) -> list[str]:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in text)
    return [token for token in normalized.split() if token]
