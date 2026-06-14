# Loop 03: Sample Dataset

## Objective

Add built-in HandoverGapBench mini sample data.

## Input Files

- `docs/06_handover_gap_bench.md`
- `docs/05_slot_schema.md`

## Output Files

- `src/handovergap/data/handover_gap_bench.json`
- `tests/test_dataset.py`

## Forbidden Changes

- Do not include real data.
- Do not exceed MVP scope.
- Do not add LLM.

## Validation Commands

```bash
pytest tests/test_dataset.py
```

## Stop Condition

Dataset has at least 10 scenarios, 3 roles, and 5 gap types.
