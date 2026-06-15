# Loop Report

## Objective

Add a README comparison visual that makes the product difference visible immediately: naive RAG answers directly, HandoverGap blocks and asks profile-required questions.

## Files Changed

- `docs/assets/naive-vs-handovergap.svg`
- `README.md`
- `tests/test_docs_assets.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/ruff check .`

## Evaluation Integrity

- [x] visual does not claim live OpenAI or TiDB execution
- [x] visual reflects the S001-style deterministic flow
- [x] no benchmark score or gold label is used in the visual

## Observations

- The visual is intentionally static and lightweight so README readers can inspect the core behavior without running the demo.
- A future screenshot/GIF can replace or complement it after the live demo is refreshed.

## Failures

- None.

## Next Recommended Loop

Issue #11: add TiDB 1k generated workload benchmark.
