# Agent Operating Contract

## Applies To

- Claude Code
- Codex
- Cursor
- Any agentic coding tool

## Mandatory Context Files

Agents must read:

1. `AGENTS.md`
2. `LOOP_ENGINEERING.md`
3. `project/tasks.md`
4. relevant `.cursor/rules/*.mdc` files when using Cursor

## Task Discipline

Agents must not start implementation from a vague request.

They must first produce or follow a task contract.

## Small Diff Rule

Prefer a small diff that passes validation over a large diff that looks complete.

## Test First Preference

When feasible:

1. add failing test
2. implement
3. pass test

## Validation Before Claim

Do not claim something works unless the validation command was run.

Acceptable language:

```text
Implemented and validated with pytest tests/test_detector.py.
```

If not run:

```text
Implemented but not validated because ...
```

## Scope Boundaries

P0 must not include:

- TiDB required runtime
- OpenAI required runtime
- Slack/GitHub integrations
- Streamlit-first architecture
- employee scoring
- real business data

## Documentation Update Rule

Update docs when:

- CLI behavior changes
- schema changes
- dataset format changes
- evaluation metrics change
- package installation changes

## Failure Report

Use this when blocked:

```md
# Failure Report

## Intended Objective
...

## Command Failed
...

## Error
...

## Likely Cause
...

## Minimal Fix Attempted
...

## Next Step
...
```
