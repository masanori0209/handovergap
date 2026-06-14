# CLAUDE.md

## Mission

Build HandoverGap RAG as a contest-grade, PyPI-installable toolkit and mini benchmark.

## Core Thesis

Correct memories are not always transferable.

## Working Contract

For every task:

1. State objective.
2. Inspect required files.
3. Implement smallest useful change.
4. Validate.
5. Update docs/tasks if behavior changed.
6. Produce loop report.
7. Stop.

## Winning Mode

Optimize for:

- article claim
- evaluation metric
- TiDB-specific learning
- PyPI first-run experience
- demo clarity

Do not optimize for feature count.

## Required Framing

Do not describe this as a generic RAG app.

Describe it as:

> A TiDB-backed evaluation toolkit for detecting when a retrieved organizational memory is correct but not yet transferable to a successor.

## MVP Focus

P0:

- CLI
- sample dataset
- rule-based detector
- baseline comparison
- evaluation metrics
- tests

P1:

- TiDB schema and optional store
- Streamlit demo
- PyPI package
- article assets

## Loop Report Format

```md
## Loop Report

### Objective
...

### Files Changed
...

### Validation
...

### What This Improves for the Article
...

### Next Recommended Loop
...
```
