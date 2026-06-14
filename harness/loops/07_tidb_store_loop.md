# Loop 07: TiDB Store

## Objective

Add TiDB schema and optional TiDBStore.

## Input Files

- `docs/03_tidb_architecture.md`
- `docs/04_tidb_schema.sql`

## Output Files

- `src/handovergap/data/schema.sql`
- `src/handovergap/stores/tidb.py`
- `tests/test_schema_sql.py`

## Forbidden Changes

- Do not make TiDB required for local MVP.
- Do not break InMemoryStore.
- Do not require live TiDB in normal tests.

## Validation Commands

```bash
pytest tests/test_schema_sql.py
handovergap schema --dialect tidb
```

## Stop Condition

Schema can be printed and TiDBStore is importable without live connection.
