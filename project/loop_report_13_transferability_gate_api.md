# Loop Report

## Objective

Add a small `TransferabilityGate` public API that existing RAG pipelines can call before answer generation.

## Files Changed

- `src/handovergap/core/gate.py`
- `src/handovergap/__init__.py`
- `src/handovergap/core/__init__.py`
- `README.md`
- `docs/index.html`
- `docs/09_cli_and_api_spec.md`
- `docs/28_handovergap_product_roadmap.md`
- `tests/test_transferability_gate.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap evaluate --compare`
- [x] direct `TransferabilityGate().check(...)` import check

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] no metric behavior was changed
- [x] limitations were not weakened

## Observations

- `TransferabilityGate.check(...)` now accepts inline memory, profile, task context, evidence, provided slots, and evidence slots.
- `ContextReadinessGate` is exported as a neutral alias for non-handover positioning.
- `TransferabilityGate.from_builtin_dataset().check_builtin(...)` keeps packaged scenario inspection simple without exposing low-level store setup first.

## Failures

- None.

## Next Recommended Loop

Issue #3: add YAML-based custom profiles and transferability policies.
