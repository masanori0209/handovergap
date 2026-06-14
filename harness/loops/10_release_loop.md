# Loop 10: Release Loop

## Objective

Prepare package for TestPyPI / PyPI release.

## Input Files

- `docs/08_pypi_package_design.md`
- `README.md`
- `pyproject.toml`

## Output Files

- `.github/workflows/ci.yml`
- `.github/workflows/publish.yml`
- release checklist

## Forbidden Changes

- Do not publish without human approval.
- Do not include secrets.
- Do not upload broken distributions.

## Validation Commands

```bash
python -m build
twine check dist/*
pytest
```

## Stop Condition

Build artifacts pass twine check and tests pass.
