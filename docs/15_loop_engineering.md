# Loop Engineering

## Definition

Loop engineering is the design of a closed development system for AI agents.

It is not a checklist.

It specifies how the agent:

```text
Plan
→ Act
→ Observe
→ Validate
→ Reflect
→ Update Context
→ Handoff
```

## Why This Project Needs It

HandoverGap RAG has three risks:

1. The agent may overbuild a generic RAG app.
2. The agent may skip evaluation and only build demos.
3. The agent may drift away from the thesis.

Loop engineering prevents this by forcing each step to produce validated output.

## Loop Contract

Every loop must specify:

- objective
- input files
- output files
- forbidden changes
- validation commands
- failure handling
- context update rule
- stop condition

## Example Loop

```md
# Task Contract

## Objective

Implement `handovergap detect`.

## Input Files

- `src/handovergap/cli.py`
- `src/handovergap/core/detector.py`
- `src/handovergap/data/handover_gap_bench.json`

## Output Files

- `src/handovergap/cli.py`
- `tests/test_cli_detect.py`

## Forbidden Changes

- Do not add TiDB dependency.
- Do not call external LLM.
- Do not change dataset format.

## Validation Commands

```bash
pytest tests/test_cli_detect.py
handovergap detect --scenario S001 --profile CS
```

## Stop Condition

CLI prints memory, gaps, clarification questions, and transferability status.
```

## Human Review Points

Human review is required when:

- public CLI changes
- schema changes
- benchmark format changes
- article thesis changes
- external dependency is added
- PyPI release is prepared

## Agent Handoff

After each loop, the agent must write:

- what changed
- what was validated
- what failed
- what should be done next
