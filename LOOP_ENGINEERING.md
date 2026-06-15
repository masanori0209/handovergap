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
- evaluation integrity check, when metrics or prompts are touched

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
9. For evaluation-affecting work, run the evaluation integrity check.
10. Write a loop report.
11. Stop.

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
- improve benchmark scores by matching scenario ids, gold labels, expected slot names, or expected answer strings
- let predictors, detectors, slot fillers, retrievers, demos, or baselines read `gold_gaps`, `gold_questions`, or `unsafe_transfer_label`
- tune prompts to the exact wording of bundled gold annotations instead of profile requirements and source evidence

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
→ Independent annotation or rubric
→ Run baseline without labels
→ Run proposed method without labels
→ Compare with label metrics and rubric metrics
→ Inspect failure
→ Improve schema or prompt
```

Output:

- benchmark scenarios
- metrics
- result table
- integrity notes

Rules:

- Gold labels are evaluator-only data.
- The detector must not read `gold_gaps`, `gold_questions`, or `unsafe_transfer_label`.
- Do not detect gaps by matching the expected answer string.
- If a score improves, explain which model behavior changed and why it is not label leakage.
- Treat structurally aligned mini/holdout scores as consistency checks unless an independent annotation, adversarial split, or rubric-based judge supports the claim.

LLM-as-a-judge is allowed for semantic evaluation when:

- it receives source evidence, profile requirements, task context, predicted gaps, and generated questions
- it grades with a written rubric, preferably returning structured JSON
- it does not receive scenario ids or gold labels as hints
- it is calibrated against gold labels or human annotations only in evaluator/reporting code
- its prompt and model name are recorded with the report

Recommended rubric dimensions:

- missing-context validity
- evidence grounding
- clarification question actionability
- over-clarification on safe cases
- transfer readiness decision quality

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
handovergap detect --scenario S001 --profile CS
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

### If evaluation improvement looks too good

1. Inspect whether predictors read labels or scenario-specific strings.
2. Add or update a leakage regression test.
3. Re-run an adversarial or holdout split.
4. Add an LLM-as-a-judge or human-rubric check if the improvement is semantic.
5. Downgrade the article claim if the improvement only holds on structurally aligned data.

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

### Evaluation Integrity
- [ ] predictors did not read gold labels
- [ ] no scenario-specific or expected-string matching was added
- [ ] semantic scores used a rubric or independent annotation
- [ ] limitations were updated if scores changed

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
