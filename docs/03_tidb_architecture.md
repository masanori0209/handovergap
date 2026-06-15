# TiDB Architecture

## Why TiDB

HandoverGap RAG needs to store and query:

- source logs
- memories
- embeddings
- full-text searchable content
- role requirements
- slot filling attempts
- detected gaps
- clarification questions
- evaluation results

TiDB is used as a unified SQL-backed store for these.

## Not Just a Vector Store

The key claim:

> TiDB is used as a slot/evidence/gap evaluation store, not merely as a vector store.

The practical TiDB-specific learning is that the retrieval result, semantic slot-fill attempt,
missing gap, clarification question, and final transfer assessment can be queried together.
This is what makes the system explainable after it withholds an answer.

## TiDB Usage

| Feature | Usage |
|---|---|
| SQL | profile, task, slot, status, score management |
| Vector Search | retrieve semantically relevant evidence for a slot |
| Full-text Search | retrieve exact names, issue IDs, customer/project names |
| JSON | store source-specific metadata |
| Transactions | update gap status, questions, assessments |
| Relational schema | represent evidence-state relationships |

## Slot-level Retrieval

Instead of one RAG query, perform retrieval per slot.

Example:

```text
Memory:
A社は今回だけCSVで対応し、APIは次フェーズにする

Slot: communication_status
Search:
- 顧客に説明済み
- 合意済み
- API延期
- CSV暫定対応
```

This makes the retrieval process auditable.

The implemented dry-run command is:

```bash
handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status --mode hybrid
```

For live TiDB retrieval, the store writes evidence chunks into `memory_chunks.embedding VECTOR(1536)` and retrieves top-k candidates with:

```sql
SELECT
  id AS chunk_id,
  memory_item_id,
  source_event_id,
  content,
  VEC_COSINE_DISTANCE(embedding, :query_vector) AS distance
FROM memory_chunks
WHERE embedding IS NOT NULL
ORDER BY distance ASC
LIMIT :top_k;
```

The selected chunk/source ids are then persisted in `slot_fill_attempts.retrieved_event_ids` so the blocked-transfer audit query can show what evidence was checked.

For exact identifiers, runbook names, and issue IDs, the full-text path uses:

```sql
SELECT
  id AS chunk_id,
  memory_item_id,
  source_event_id,
  content,
  MATCH(content) AGAINST (:query_text) AS score
FROM memory_chunks
WHERE MATCH(content) AGAINST (:query_text)
ORDER BY score DESC
LIMIT :top_k;
```

Hybrid retrieval merges vector and full-text candidates with reciprocal rank fusion. This keeps semantic matches and exact references in one auditable TiDB-backed result set.

## Implementation Tables

Core tables:

- source_events
- memory_items
- memory_chunks
- memory_type_schemas
- profile_requirements
- memory_slots
- slot_fill_attempts
- context_gaps
- clarification_questions
- transfer_assessments
- evaluation_runs

## Blocked Transfer Audit Query

The package exposes the audit query with:

```bash
handovergap audit-sql
```

The query joins:

- `transfer_assessments`
- `memory_items`
- `context_gaps`
- `slot_fill_attempts`
- `source_events`
- `clarification_questions`

It answers: if the memory was retrieved, which profile-required slot was still missing,
what evidence was checked, and what clarification question should be asked before handover.
