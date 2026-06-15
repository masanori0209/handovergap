# CODEX.md

## Mission

Implement `handovergap`, a Python package and CLI for detecting tacit context gaps in handover-oriented RAG.

The flagship use case is handover, but the product mechanism is broader:
a profile-conditioned context readiness gate that can decide whether retrieved
memory is sufficient to answer, or should be converted into clarification
questions first.

## Priority Order

1. CLI first-run experience
2. evaluation reproducibility
3. baseline comparison
4. TiDB-specific implementation
5. article assets
6. demo polish

## Core Commands

```bash
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
handovergap schema --dialect tidb
```

## Constraints

- Python >= 3.10
- Typer CLI
- Pydantic v2
- Rich output
- pytest
- no required external LLM in P0
- no required TiDB in local MVP
- synthetic data only

## Evaluation Integrity Contract

Do not optimize reported accuracy by hard-coding dataset artifacts.

Forbidden:

- reading `gold_gaps`, `gold_questions`, or `unsafe_transfer_label` inside predictors, detectors, retrievers, slot fillers, demos, or baselines
- detecting a GoldGap by matching the expected answer string, expected slot label, or scenario id
- tuning prompts to the exact wording of bundled gold annotations
- adding scenario-specific branches to improve benchmark numbers
- reporting mini/holdout scores as production accuracy when required slots and gold labels are structurally aligned

Allowed:

- using gold labels only inside evaluator/reporting code
- using LLM slot filling as an optional input pipeline when the prompt only sees source evidence, profile requirements, and task context
- using LLM-as-a-judge as an optional evaluator when it grades outputs with a written rubric instead of matching gold strings
- comparing LLM judge scores against gold labels or human annotations as calibration, not as detector input

Preferred evaluation shape:

1. Predict missing context without access to gold labels.
2. Generate clarification questions from predicted gaps.
3. Evaluate with both label metrics and rubric metrics.
4. Report failures, false clarifications, and prompt/model variance.

## Stop Rule

Do not move to the next loop automatically.  
End with a loop report.
