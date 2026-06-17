# AGENTS.md

All agents must optimize for v1 product readiness, not feature volume.

## Core Thesis

Correct memories are not always transferable.

## Required Work Loop

Plan -> Act -> Observe -> Validate -> Reflect -> Update Context -> Handoff

Work one loop at a time.

## Product Readiness Filter

Before implementing any feature, answer:

```text
Which user-facing integration path, API contract, evaluation trust signal, privacy guarantee, or operational adoption problem does this improve?
```

If the answer is unclear, do not implement it.

## Forbidden in Core Runtime

- real company data
- employee scoring
- OpenAI-required runtime
- TiDB-required runtime
- full web app
- Slack/GitHub integration
- broad refactors without validation

## MVP Commands

```bash
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
pytest
```
