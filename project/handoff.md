# Handoff

## Current State

P0 through release preparation are implemented and locally validated.

## Completed

- Installable Python package and Typer CLI
- Pydantic schemas and 20-scenario synthetic benchmark
- Role-conditioned detector and deterministic baselines
- Evaluation metrics and comparison table
- Optional TiDB schema, store, and persistence methods
- Japanese-first bilingual Streamlit demo
- English PyPI README and Japanese README
- Zenn article draft and results note
- CI, TestPyPI, and PyPI Trusted Publishing workflows
- MIT license and release checklist

## Validated

- `ruff check .`
- `pytest` with 18 passing tests
- `python -m build`
- `twine check dist/*`
- Clean wheel installation
- CLI help, demo, evaluate, and schema commands
- Streamlit AppTest for Japanese and English

## Not Validated

- Live TiDB connection
- GitHub Actions on the remote repository
- TestPyPI publication
- PyPI publication
- Hosted demo or recorded video

## Important Decisions

- English is primary for PyPI.
- Japanese is default for the demo and article.
- External LLM and TiDB remain optional.
- Perfect benchmark scores are described as consistency checks, not generalization.

## Next Task Contract

1. Create the initial commit and push `main`.
2. Confirm GitHub Actions.
3. Configure TestPyPI Trusted Publishing and run the manual workflow.
4. Install from TestPyPI and rerun MVP commands.
5. Publish `v0.1.0` after human approval.
6. Add final GitHub, PyPI, and demo links to the Zenn article.
