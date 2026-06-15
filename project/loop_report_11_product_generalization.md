# Loop Report

## Objective

Prevent evaluation leakage/hard-coded benchmark optimization, then make the first product-generalization step by adding neutral `profile` / `task_context` aliases without breaking the handover MVP.

## Files Changed

- `CODEX.md`
- `LOOP_ENGINEERING.md`
- `docs/27_evaluation_audit.md`
- `src/handovergap/schemas/models.py`
- `src/handovergap/store.py`
- `src/handovergap/core/detector.py`
- `README.md`
- `README.ja.md`
- `tests/test_evaluation_integrity.py`
- `tests/test_profile_aliases.py`
- `tests/test_schemas.py`

## Validation

- [x] `.venv/bin/pytest tests/test_evaluation_integrity.py tests/test_baselines.py`
- [x] `.venv/bin/pytest tests/test_schemas.py tests/test_profile_aliases.py tests/test_evaluation_integrity.py tests/test_baselines.py tests/test_cli_detect.py`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap evaluate --compare`
- [x] `.venv/bin/pytest`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] semantic scoring policy now requires a rubric or independent annotation
- [x] limitations were updated where evaluation integrity is documented

## Observations

- LLM-as-a-judge is a valid evaluation pattern for this project when used as a rubric-based evaluator, not as a hidden detector shortcut.
- The current implementation now accepts `profile` and `task_context` as neutral aliases while preserving `profile` and `task_context`.
- Built-in profiles remain `CS`, `Engineer`, and `Sales`; fully custom profiles belong in the next YAML profile loop.

## Failures

- Host `pytest` was not on PATH. Validation used the repo-local `.venv/bin/pytest`.

## Next Recommended Loop

Issue #13: clean up remaining role-specific public surface in docs, examples, and user-facing wording while preserving the existing MVP commands.
