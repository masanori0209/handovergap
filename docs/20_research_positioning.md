# Research Positioning

## Problem

RAG systems usually optimize for:

- retrieval relevance
- answer faithfulness
- freshness
- conflict resolution
- memory persistence

These do not guarantee handover readiness.

## New Axis

```text
Transferability
```

A memory is transferable when the selected profile can safely act on it for a given task context.

## Core Definition

### Valid-but-Non-Transferable Memory

A memory item is valid-but-non-transferable when:

1. The memory is factually correct.
2. The memory is relevant to the task.
3. The memory is not obviously stale or contradictory.
4. The selected profile still lacks implicit context required for safe action.

## Formalization

Let:

```text
m = memory
p = profile
t = task context
E = evidence set
S(m) = required slots for memory type
R(p, type(m)) = profile-conditioned required slots
F(m, E, s) = slot filling function
```

Then:

```text
RequiredSlots = S(type(m)) ∪ R(p, type(m))

Gap(m, p, t) = {
  s ∈ RequiredSlots
  | F(m, E, s) is missing or weak
}
```

Transferability:

```text
Transferable(m, p, t) =
  no critical gaps exist
  and transferability_score >= threshold
```

## Contribution Claim

1. Define valid-but-non-transferable memory.
2. Propose profile-conditioned tacit context gap detection.
3. Implement a TiDB-backed slot/evidence/gap audit store with blocked-transfer SQL.
4. Provide HandoverGapBench mini and baseline comparison.

Avoid claiming a fully general or production-ready solution.
