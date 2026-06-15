# Loop Report

## Objective

Add explicit `naive_rag` and `hybrid_rag` baseline implementations for article-ready comparison.

## Winning Gate

This improves evaluation evidence and competitor positioning: HandoverGap is compared against retrieval-only and evidence-augmented retrieval baselines without adding external services.

## Files Changed

- `src/handovergap/core/baselines.py`
- `src/handovergap/core/evaluator.py`
- `tests/test_baselines.py`

## Validation

- [x] `.venv/bin/pytest tests/test_baselines.py`
- [x] `.venv/bin/handovergap evaluate --compare`
- [x] `.venv/bin/pytest`

## Observations

- `naive_rag` returns the memory without detecting transferability risk.
- `hybrid_rag` can flag one explicit risk from evidence context, but still lacks profile-conditioned slot filling.
- `handovergap` remains the only method that checks all role-required slots.

## Failures

- None.

## Context Updates

- Keep baselines deterministic in P1 so article results are reproducible.

## Next Recommended Loop

Loop 07: TiDB schema command and optional store design, without requiring a local TiDB runtime.
