# AGENTS.md

All agents must optimize for contest-winning evidence, not feature volume.

## Core Thesis

Correct memories are not always transferable.

## Required Work Loop

Plan -> Act -> Observe -> Validate -> Reflect -> Update Context -> Handoff

Work one loop at a time.

## Winning Filter

Before implementing any feature, answer:

```text
Which article claim, evaluation metric, TiDB-specific learning, PyPI first-run experience, or demo clarity does this improve?
```

If the answer is unclear, do not implement it.

## Forbidden in P0

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
