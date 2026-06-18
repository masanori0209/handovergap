# PyPI Release Playbook

## Required User Journey

```bash
pip install handovergap
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate
```

This should work without:

- TiDB account
- OpenAI API key
- external dataset
- manual configuration

## TiDB Mode

```bash
handovergap schema --dialect tidb
python harness/validation/tidb_live_check.py --reset-schema
python harness/validation/tidb_audit_query_check.py --reset-schema --dataset sanitized --iterations 10
```

Use `--reset-schema` only for validation databases with no user data. The validation scripts call `destructive_reset_schema(..., confirm=RESET_CONFIRMATION)`.

## Release Checklist

### Package

- [ ] pyproject.toml complete
- [ ] README renders on PyPI
- [ ] LICENSE present
- [ ] CLI entrypoint works
- [ ] package data included
- [ ] version in `pyproject.toml`, `src/handovergap/__init__.py`, README, docs, and tests is aligned
- [ ] optional dependencies separated

### Compatibility

- [ ] Public Python API changes reviewed against `docs/31_versioning_policy.md`
- [ ] CLI command and option changes reviewed against the MVP command contract
- [ ] Profile YAML field changes reviewed against the v1 stable schema target
- [ ] Result model fields and answer/ask/block routing semantics reviewed
- [ ] TiDB audit-store schema and audit SQL expectations reviewed
- [ ] Dataset shape, metric definition, and report output changes reviewed
- [ ] Breaking changes are listed under `Breaking Changes` in `CHANGELOG.md`
- [ ] Migration notes name the old pattern, new pattern, and safest migration path

### Validation

```bash
pip install -e ".[dev]"
pytest
handovergap demo
handovergap evaluate
handovergap privacy-check
python -m build
twine check dist/*
```

## Avoid

- dependency bloat
- requiring OpenAI by default
- requiring TiDB by default
- empty package with only sample script
- undocumented CLI
