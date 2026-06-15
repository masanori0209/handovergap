# Risks and Notes

## Risk: Looks Like Prompt Engineering

If the implementation only asks an LLM "what is missing?", it is weak.

Mitigation:

- Use memory type schemas
- Use successor responsibility profile requirements
- Use semantic slot filling
- Persist slot fill attempts
- Compare baselines

## Risk: Too Abstract

The concepts can become too academic.

Mitigation:

Start article with concrete example:

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

Then show why it is insufficient for CS.

## Risk: TiDB Feels Like Storage Only

Mitigation:

Show TiDB as a slot/evidence/gap audit store.

Include:

- schema
- SQL
- vector search for slot evidence
- full-text search for names/issue IDs
- slot fill attempts table

## Risk: Surveillance Impression

Do not frame ownership as person scoring.

Bad:

```text
Sato is a single point of failure.
```

Better:

```text
This memory depends on context currently held by Sato and needs clarification before transfer.
```

## Risk: Overbuilding

Do not attempt full Slack/GitHub integrations first.

MVP should use synthetic sample data.

## Risk: PyPI Package Too Thin

PyPI is useful only if:

- CLI works
- sample data exists
- evaluate command works
- README is clear
- tests pass
