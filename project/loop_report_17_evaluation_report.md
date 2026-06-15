# Loop Report

## Objective

Add a reproducible markdown evaluation report generator for bundled datasets and integrity notes.

## Files Changed

- `src/handovergap/reporting.py`
- `src/handovergap/cli.py`
- `README.md`
- `README.ja.md`
- `docs/28_handovergap_product_roadmap.md`
- `tests/test_report.py`
- `tests/test_cli_help.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/ruff check .`
- [x] `.venv/bin/handovergap report --dataset mini --output /tmp/handovergap_report.md`

## Evaluation Integrity

- [x] predictors did not read gold labels
- [x] no scenario-specific or expected-string matching was added
- [x] report includes an Evaluation Integrity section
- [x] limitations are stated as synthetic/reproducibility, not production accuracy

## Observations

- `handovergap report --dataset all --output reports/evaluation-latest.md` now creates a deterministic markdown report across bundled datasets.
- The first report version includes local metrics only. Live TiDB/OpenAI sections should stay optional so first-run usage remains no-key.

## Failures

- `ruff` requested replacing `.format(...)` with f-strings in `reporting.py`; fixed.

## Next Recommended Loop

Issue #7: add JSONL ingest for Slack/Issue/CRM-style source events.
