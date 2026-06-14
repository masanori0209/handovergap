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

## TiDB Usage

| Feature | Usage |
|---|---|
| SQL | role, task, slot, status, score management |
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

## Implementation Tables

Core tables:

- source_events
- memory_items
- memory_chunks
- memory_type_schemas
- successor_role_requirements
- memory_slots
- slot_fill_attempts
- context_gaps
- clarification_questions
- transfer_assessments
- evaluation_runs
- evaluation_results
