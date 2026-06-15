# Loop Report

## Objective

Add YAML-based custom profiles so HandoverGap can evaluate non-handover readiness contexts without changing source code.

## Files Changed

- `pyproject.toml`
- `src/handovergap/profiles.py`
- `src/handovergap/core/detector.py`
- `src/handovergap/core/gate.py`
- `src/handovergap/schemas/models.py`
- `src/handovergap/store.py`
- `src/handovergap/cli.py`
- `src/handovergap/__init__.py`
- `examples/profiles/incident_readiness.yml`
- `README.md`
- `docs/28_handovergap_product_roadmap.md`
- `tests/test_custom_profiles.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile IncidentCommander --profile-file examples/profiles/incident_readiness.yml`
- [x] `.venv/bin/handovergap evaluate --compare`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] custom profiles define required slots and questions, not gold labels
- [x] limitations were not weakened

## Observations

- `ProfileCatalog` now owns required slot policy for both built-in and YAML profiles.
- `TransferabilityGate.from_profile_file(...)` enables non-handover use cases such as incident readiness.
- The CLI can run a built-in scenario memory against a custom profile with `--profile-file`.

## Failures

- None.

## Next Recommended Loop

Issue #4: add TiDB vector evidence retrieval for slot-level search.
