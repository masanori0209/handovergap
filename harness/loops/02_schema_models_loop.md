# Loop 02: Schema Models

## Objective

Implement Pydantic models for scenarios, gaps, questions, and detection results.

## Input Files

- `docs/06_handover_gap_bench.md`
- `docs/09_cli_and_api_spec.md`

## Output Files

- `src/handovergap/schemas/*.py`
- `tests/test_schemas.py`

## Forbidden Changes

- Do not implement CLI detect yet.
- Do not add TiDB.
- Do not call external LLM.

## Validation Commands

```bash
pytest tests/test_schemas.py
```

## Stop Condition

Models validate representative scenario data.
