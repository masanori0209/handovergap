# Loop Report

## Objective

Add slot-level vector evidence retrieval so HandoverGap can show how TiDB Vector Search supports profile-required slot checks.

## Files Changed

- `src/handovergap/retrieval.py`
- `src/handovergap/stores/tidb.py`
- `src/handovergap/cli.py`
- `src/handovergap/data/schema.sql`
- `docs/04_tidb_schema.sql`
- `docs/03_tidb_architecture.md`
- `docs/28_handovergap_product_roadmap.md`
- `README.md`
- `harness/validation/tidb_audit_query_check.py`
- `tests/test_retrieval.py`
- `tests/test_tidb_persistence.py`
- `tests/test_schema_sql.py`
- `tests/test_cli_help.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/ruff check .`
- [x] `.venv/bin/handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap evaluate --compare`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] vector retrieval returns candidate evidence only; scoring still happens in evaluator/reporting code
- [x] limitations were not weakened

## Observations

- `memory_chunks` now stores `source_event_id`, `chunk_kind`, metadata, and `embedding VECTOR(1536)`.
- `TiDBStore.persist_memory_chunks(...)` and `TiDBStore.retrieve_memory_chunks_by_vector(...)` provide the live TiDB path using `VEC_COSINE_DISTANCE`.
- `handovergap retrieve-evidence` gives a deterministic local vector dry-run so users can inspect slot-level evidence retrieval without TiDB or OpenAI.
- Live TiDB p50/p95 latency is still intentionally left as a separate validation task because existing alpha schemas may need migration or a fresh database.

## Failures

- None.

## Next Recommended Loop

Issue #5: add TiDB full-text evidence lookup and hybrid merge.
