# Loop Report

## Objective

Clean the public surface by making `profile` and `task_context` the canonical schema/API/CLI vocabulary, with no compatibility shim for `successor_role`, `handover_task`, or `--role`.

## Files Changed

- `AGENTS.md`
- `CODEX.md`
- `LOOP_ENGINEERING.md`
- `README.md`
- `README.ja.md`
- `docs/index.html`
- `docs/02_method_handovergap_rag.md`
- `docs/07_evaluation_metrics.md`
- `docs/20_research_positioning.md`
- `article/results.md`
- `src/handovergap/schemas/models.py`
- `src/handovergap/store.py`
- `src/handovergap/core/detector.py`
- `src/handovergap/core/evaluator.py`
- `src/handovergap/cli.py`
- `src/handovergap/demo_app.py`
- `src/handovergap/semantic_slot_filling.py`
- `src/handovergap/slot_rules.py`
- `src/handovergap/data/*.json`
- `src/handovergap/data/schema.sql`
- `src/handovergap/stores/tidb.py`
- `src/handovergap/audit.py`
- `tests/*`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap evaluate --compare`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] no evaluation metric behavior was changed
- [x] limitations were not weakened

## Observations

- The package now has one canonical vocabulary: `profile`, `task_context`, and `profile_requirements`.
- The old CLI option `--role` is intentionally removed for alpha cleanliness.
- The built-in demo still uses handover-shaped cases, but its public framing is now profile-conditioned readiness rather than department-only handover.

## Failures

- A first bulk replacement command failed because the file list was passed incorrectly; it made no changes. The replacement was rerun with `xargs`.

## Next Recommended Loop

Issue #1: add a small `TransferabilityGate` public API for existing RAG pipelines.
