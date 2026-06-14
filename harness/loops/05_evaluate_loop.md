# Loop 05: Evaluate CLI

## Objective

Implement `handovergap evaluate`.

## Input Files

- `docs/07_evaluation_metrics.md`
- `docs/06_handover_gap_bench.md`

## Output Files

- `src/handovergap/core/evaluator.py`
- `src/handovergap/cli.py`
- `tests/test_evaluate.py`

## Forbidden Changes

- Do not implement Streamlit.
- Do not require TiDB.
- Do not add LLM.

## Validation Commands

```bash
pytest tests/test_evaluate.py
handovergap evaluate
```

## Stop Condition

Evaluation prints Tacit Gap Recall, Unsafe Transfer Prevention, and Question Coverage.
