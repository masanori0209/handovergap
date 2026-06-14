# Loop Report

## Objective

Add a TiDB schema command and optional `TiDBStore` without requiring TiDB for the local MVP.

## Winning Gate

This improves TiDB-specific evidence. The schema models slot-level evidence retrieval, fill attempts, detected gaps, clarification questions, transfer assessments, and evaluation runs.

## Files Changed

- `src/handovergap/data/schema.sql`
- `src/handovergap/stores/tidb.py`
- `src/handovergap/stores/__init__.py`
- `src/handovergap/__init__.py`
- `src/handovergap/cli.py`
- `tests/test_schema_sql.py`

## Validation

- [x] `.venv/bin/pytest tests/test_schema_sql.py`
- [x] `.venv/bin/handovergap schema --dialect tidb`
- [x] `.venv/bin/pytest`
- [x] Wheel contains `handovergap/data/schema.sql`

## Observations

- Importing and constructing `TiDBStore` does not import SQLAlchemy or open a connection.
- Live schema installation loads the `tidb` optional dependencies only when requested.
- The schema uses SQL, JSON, vector storage, indexes, and relational workflow tables.

## Failures

- No implementation failures.
- A live TiDB connection was intentionally not required or tested in this loop.

## Context Updates

- `src/handovergap/data/schema.sql` is the canonical packaged TiDB schema.
- Live TiDB integration remains optional and is outside normal test execution.

## Next Recommended Loop

Loop 08: Streamlit comparison demo.
