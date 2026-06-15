# Failure Modes

## Failure Mode 1: LLM-only Gap Detection

Bad:

```text
Prompt: "What context is missing?"
```

Fix:

- schema-driven slots
- role requirements
- evidence-backed slot filling
- stored slot_fill_attempts

## Failure Mode 2: TiDB as Replaceable Storage

Bad:

```text
Store JSON in TiDB and call it done.
```

Fix:

- SQL for roles/status
- vector search for slot evidence
- full-text for exact entities
- JSON metadata
- retrieval attempt logs

## Failure Mode 3: Demo Without Benchmark

Bad:

```text
Streamlit app only.
```

Fix:

- HandoverGapBench mini
- baseline comparison
- metrics table

## Failure Mode 4: Overclaiming Novelty

Bad:

```text
We solved organizational memory transfer.
```

Better:

```text
We propose a small, reproducible framework for detecting profile-conditioned tacit context gaps in handover-oriented RAG.
```

## Failure Mode 5: Surveillance Framing

Bad:

```text
This detects who is a bottleneck.
```

Better:

```text
This detects which memories need clarification before transfer.
```

## Failure Mode 6: Too Many Features

Bad:

- Slack integration
- GitHub integration
- full web app
- LLM agents
- multi-user auth
- dashboards

Fix:

P0 must be:

- CLI
- sample dataset
- detector
- evaluate
- tests
