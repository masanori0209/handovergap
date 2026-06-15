# Loop Report

## Objective

Add TiDB full-text evidence lookup and hybrid merge so exact IDs, runbook names, and named entities can complement vector evidence retrieval.

## Files Changed

- `src/handovergap/retrieval.py`
- `src/handovergap/stores/tidb.py`
- `src/handovergap/cli.py`
- `src/handovergap/data/schema.sql`
- `docs/04_tidb_schema.sql`
- `docs/03_tidb_architecture.md`
- `docs/28_handovergap_product_roadmap.md`
- `README.md`
- `tests/test_retrieval.py`
- `tests/test_tidb_persistence.py`
- `tests/test_schema_sql.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/ruff check .`
- [x] `.venv/bin/handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status --mode vector`
- [x] `.venv/bin/handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status --mode fulltext`
- [x] `.venv/bin/handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status --mode hybrid`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] hybrid retrieval only ranks candidate evidence; evaluator labels remain separate
- [x] limitations were not weakened

## Observations

- `memory_chunks.content` now has a TiDB `FULLTEXT` index.
- `TiDBStore.retrieve_memory_chunks_by_full_text(...)` uses `MATCH(content) AGAINST (:query_text)`.
- `TiDBStore.retrieve_memory_chunks_hybrid(...)` merges vector and full-text candidates with reciprocal rank fusion.
- `handovergap retrieve-evidence` now supports `--mode vector`, `--mode fulltext`, and `--mode hybrid`.

## Failures

- `ruff` required import reordering in `tests/test_retrieval.py`; fixed with `ruff --fix`.

## Next Recommended Loop

Issue #6: add a reproducible evaluation report generator.
