# Winning Strategy

## Reality Check

There is no guaranteed way to win a contest.

However, the project can be designed to maximize the probability of winning by optimizing for the likely judging signals:

- originality
- implementation depth
- reproducibility
- TiDB relevance
- usefulness to engineers
- clarity of article narrative
- demo impact
- honest limitations
- package completeness
- benchmark/evaluation evidence

The goal is not just to build a RAG app.

The goal is to publish a small but credible research-grade engineering artifact:

> A PyPI-installable toolkit and mini benchmark for detecting tacit context gaps in handover-oriented RAG.

## Winning Thesis

The article must be built around one sharp claim:

> RAG can retrieve correct and relevant memories, but those memories may still be unsafe to transfer to another person because tacit operational context is missing.

Do not dilute the message with generic agent memory, generic RAG quality, or generic knowledge management.

## Why This Can Win

Most competing articles are likely to focus on:

- building a RAG app
- using TiDB Vector Search
- adding agent long-term memory
- showing mem9 integration
- building a demo
- measuring retrieval quality
- memory security or poisoning

HandoverGap RAG wins by creating a new evaluation axis:

```text
Correctness != Transferability
```

## Winning Artifact Stack

```text
1. Concept
   valid-but-non-transferable memory

2. Method
   successor-profile-conditioned slot filling

3. Infrastructure
   TiDB-backed slot/evidence/gap audit store

4. Benchmark
   HandoverGapBench mini

5. Package
   pip install handovergap

6. CLI
   handovergap detect / evaluate / serve

7. Demo
   Naive RAG answers; HandoverGap RAG asks questions

8. Article
   clear narrative + code + metrics + limitations
```

## The Winning Reader Experience

The reader should feel this sequence:

1. "This handover problem happens."
2. "Normal RAG would answer too confidently."
3. "Correctness and transferability are different."
4. "The slot schema makes the method concrete."
5. "The benchmark makes it measurable."
6. "The TiDB schema is not decoration."
7. "I can run this with pip install."
8. "This is not just another RAG demo."

## Final Positioning Statement

> HandoverGap RAG is a TiDB-backed evaluation toolkit for detecting when a retrieved organizational memory is correct but not yet transferable to a successor.
