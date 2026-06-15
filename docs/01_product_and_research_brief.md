# Product and Research Brief

## Product Name

HandoverGap RAG

## Package Name Candidate

`handovergap`

## One-line Summary

A TiDB-backed RAG evaluation toolkit that detects tacit context gaps in valid but non-transferable organizational memories.

## Core Claim

RAG can retrieve correct and relevant information, but organizational handover requires another property: transferability.

A memory is transferable only when a successor can safely act on it.

## Example

Memory:

```text
A社は今回だけCSVで対応し、APIは次フェーズにする。
```

For CS successor, missing context:

- Was the customer informed?
- Can CS mention next phase timing?
- What does "this time" mean?
- Who handles escalation?
- What if CSV fails?

For Engineer successor, missing context:

- What technical constraints drove the decision?
- What issue tracks API integration?
- What is the trigger to resume API work?
- What temporary CSV behavior must be implemented?

Same memory, different successor, different gaps.

## Why This Matters

Most RAG systems optimize for:

- relevance
- faithfulness
- groundedness
- freshness
- conflict handling

HandoverGap RAG focuses on:

- transferability
- tacit context gaps
- successor responsibility profile
- handover task
- unsafe transfer prevention

## Intended Article Position

This is not "another RAG app."

This is a mini research/tooling article:

- Defines valid-but-non-transferable memory
- Defines Tacit Context Gap types
- Implements successor-profile-conditioned slot filling
- Provides HandoverGapBench mini
- Compares against naive and hybrid RAG
- Publishes PyPI package
- Uses TiDB as a slot/evidence/gap audit store

## Success Criteria

The article should make readers think:

> RAG can be correct and still unsafe for handover.
