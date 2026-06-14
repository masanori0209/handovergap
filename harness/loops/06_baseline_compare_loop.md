# Loop 06: Baseline Compare

## Objective

Add naive_rag and hybrid_rag baselines for comparison.

## Input Files

- `docs/07_evaluation_metrics.md`
- `docs/13_competitor_analysis.md`

## Output Files

- `src/handovergap/core/baselines.py`
- `src/handovergap/core/evaluator.py`
- `tests/test_baselines.py`

## Forbidden Changes

- Do not change HandoverGap output format unless needed.
- Do not add TiDB.
- Do not add Streamlit.

## Validation Commands

```bash
pytest tests/test_baselines.py
handovergap evaluate --compare
```

## Stop Condition

Comparison table includes naive_rag, hybrid_rag, and handovergap.
