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

Use `--reset-schema` only for alpha validation databases with no user data.

## Release Checklist

### Package

- [ ] pyproject.toml complete
- [ ] README renders on PyPI
- [ ] LICENSE present
- [ ] CLI entrypoint works
- [ ] package data included
- [ ] version is 0.1.0
- [ ] optional dependencies separated

### Validation

```bash
pip install -e ".[dev]"
pytest
handovergap demo
handovergap evaluate
python -m build
twine check dist/*
```

## Avoid

- dependency bloat
- requiring OpenAI by default
- requiring TiDB by default
- empty package with only sample script
- undocumented CLI
