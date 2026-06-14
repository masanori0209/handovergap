# Loop 08: Streamlit Demo

## Objective

Add optional Streamlit demo.

## Input Files

- `docs/10_demo_design.md`
- `docs/09_cli_and_api_spec.md`

## Output Files

- `examples/streamlit_app.py`
- `src/handovergap/cli.py`
- `tests/test_serve_command.py`

## Forbidden Changes

- Do not make Streamlit a core dependency.
- Do not require TiDB.
- Do not remove CLI-first flow.

## Validation Commands

```bash
pip install -e ".[demo]"
handovergap serve --help
```

## Stop Condition

`handovergap serve` command exists and demo can be launched manually.
