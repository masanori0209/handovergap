# Loop Engineering Harness

This document defines the operating loop for AI coding agents working on HandoverGap RAG.

## What Loop Engineering Means Here

Loop engineering is not a task list.

It is the design of a closed development loop where an AI agent repeatedly:

```text
Plan
→ Act
→ Observe
→ Validate
→ Reflect
→ Update Context
→ Handoff
```

The goal is to prevent the agent from drifting into broad, unverified implementation.

Every loop must have:

- objective
- input files
- output files
- forbidden changes
- validation commands
- failure handling
- context update rule
- handoff format
- stop condition

## Global Loop Contract

For every task, the agent must:

1. Read the task contract.
2. Restate the loop objective in one sentence.
3. Inspect only the necessary files first.
4. Prefer tests before implementation when possible.
5. Implement the smallest useful change.
6. Run the validation commands.
7. If validation fails, fix the smallest cause only.
8. Update docs or task status if behavior changed.
9. Write a loop report.
10. Stop.

## Forbidden Behavior

The agent must not:

- implement multiple loops in one pass
- introduce external LLM dependency in P0
- require TiDB for local MVP
- use real company or customer data
- create employee scoring or surveillance features
- silently change public CLI behavior
- skip validation commands
- hide failing tests
- broaden the architecture without updating docs

## Loop Types

### Research Loop

Purpose: Verify positioning and novelty.

```text
Hypothesis
→ Related work / competitor check
→ Difference statement
→ Article thesis update
→ Risk note
```

Output:

- `docs/13_competitor_analysis.md`
- `article/key_phrases.md`
- `article/zenn_outline.md`

### Product Loop

Purpose: Improve 5-minute package experience.

```text
CLI idea
→ Implement
→ Run quickstart
→ Observe friction
→ Simplify
→ Update README
```

Output:

- CLI command
- README quickstart
- smoke test

### Evaluation Loop

Purpose: Make the claim measurable.

```text
Scenario
→ Gold gaps
→ Run baseline
→ Run proposed method
→ Compare
→ Inspect failure
→ Improve schema
```

Output:

- benchmark scenarios
- metrics
- result table

### Engineering Loop

Purpose: Keep code maintainable.

```text
Test
→ Implement
→ Lint
→ Smoke test
→ Docs update
→ Handoff
```

Output:

- passing tests
- small diff
- loop report

### Article Loop

Purpose: Turn implementation results into article content.

```text
Draft claim
→ Link to implementation result
→ Add table/screenshot
→ Remove unsupported claim
→ Update article
```

Output:

- article section
- result table
- screenshot checklist

## Validation Levels

### L0: Local Smoke

```bash
handovergap --help
handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate
```

### L1: Test

```bash
pytest
```

### L2: Quality

```bash
ruff check .
mypy src
```

### L3: Package

```bash
python -m build
twine check dist/*
```

## Failure Handling

### If tests fail

Do not add new features.

1. Identify the failing test.
2. Explain the likely cause.
3. Fix the smallest cause.
4. Rerun the exact failing test.
5. Rerun full tests if fixed.

### If CLI UX is confusing

1. Simplify command.
2. Update README.
3. Add smoke test.
4. Do not add a new command unless necessary.

### If novelty claim is unsupported

1. Downgrade the claim.
2. Add limitation.
3. Add evaluation or evidence.
4. Update article wording.

### If TiDB integration blocks progress

1. Keep InMemoryStore working.
2. Add a clear TODO.
3. Isolate TiDB-specific code.
4. Do not break local MVP.

## Loop Report Format

At the end of every loop, produce:

```md
## Loop Report

### Objective
...

### Files Changed
- ...

### Validation
- [ ] command: result

### Observations
...

### Failures
...

### Next Recommended Loop
...
```

## Stop Rule

Stop after one loop.

If tempted to continue, write the next loop contract instead.
