# Loop 01: Package Skeleton

## Objective

Create an installable Python package skeleton with a working CLI help command.

## Input Files

- `CODEX.md`
- `docs/08_pypi_package_design.md`
- `docs/09_cli_and_api_spec.md`

## Output Files

- `pyproject.toml`
- `src/handovergap/__init__.py`
- `src/handovergap/cli.py`
- `tests/test_cli_help.py`

## Forbidden Changes

- Do not implement detector logic.
- Do not add TiDB.
- Do not add external LLM dependency.

## Validation Commands

```bash
pip install -e ".[dev]"
handovergap --help
pytest tests/test_cli_help.py
```

## Stop Condition

`handovergap --help` works and test passes.
