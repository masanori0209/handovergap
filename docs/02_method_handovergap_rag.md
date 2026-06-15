# HandoverGap RAG Method

## Overview

HandoverGap RAG detects missing implicit context required for a selected profile to safely use a retrieved memory in a task context.

## Pipeline

```text
Readiness Scenario
  -> Retrieve memory and evidence
  -> Classify memory type
  -> Load profile-conditioned required slots
  -> Fill slots from evidence
  -> Detect missing or weak slots
  -> Generate clarification questions
  -> Assess transferability
```

## Inputs

- memory item
- source evidence events
- profile
- task context

## Outputs

- filled slots
- missing slots
- context gaps
- clarification questions
- transferability score
- safe / needs_confirmation / unsafe

## Gap Types

| Gap | Meaning |
|---|---|
| scope_gap | Scope of application is unclear |
| rationale_gap | Decision rationale is unclear |
| trigger_gap | Reconsideration trigger is unclear |
| authority_gap | Decision authority is unclear |
| exception_gap | Exception conditions are unclear |
| communication_gap | Communication status is unclear |
| fallback_gap | Escalation or fallback path is unclear |

## Transferability Score

A simple MVP formula:

```text
score =
  filled_required_slot_ratio * 0.45
+ evidence_confidence_avg * 0.25
+ profile_requirement_satisfaction * 0.20
- critical_gap_penalty * 0.10
```

This score is not a human performance score.  
It is a memory transfer readiness score.

## Unsafe Transfer

A memory should be marked unsafe if:

- critical required slots are missing
- required evidence is absent
- selected profile cannot act safely
- clarification questions are mandatory before use

## Clarification-first Design

The system should not hallucinate missing context.

If a critical gap is detected, generate questions instead of pretending the memory is complete.
