# Loop 04: Detect CLI

## Objective

Implement `handovergap detect --scenario S001 --profile CS`.

## Input Files

- `docs/09_cli_and_api_spec.md`
- `src/handovergap/data/handover_gap_bench.json`

## Output Files

- `src/handovergap/cli.py`
- `src/handovergap/core/detector.py`
- `tests/test_cli_detect.py`

## Forbidden Changes

- Do not add TiDB.
- Do not add OpenAI.
- Do not change dataset format.

## Validation Commands

```bash
pytest tests/test_cli_detect.py
handovergap detect --scenario S001 --profile CS
```

## Stop Condition

CLI prints memory, detected gaps, clarification questions, and transferability status.
