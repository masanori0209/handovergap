# Production Adoption Guide

HandoverGap is an alpha readiness gate for RAG memories. The safe production posture is to start with observation and audit, not automatic blocking in critical workflows.

## Recommended Rollout

1. Run `TransferabilityGate` in shadow mode before final answer generation.
2. Store predicted gaps, generated questions, retrieved evidence ids, and transfer decisions.
3. Review false clarifications and missed gaps with domain reviewers.
4. Define custom YAML profiles for each operational context.
5. Promote blocking only after profile requirements and question quality are reviewed.

## Data Requirements

- Use `profile` and `task_context` as the primary product concepts.
- Keep `gold_gaps`, `gold_questions`, and unsafe labels out of runtime inputs.
- For JSONL ingest, include only redacted source events.
- Preserve source metadata needed for audit, but remove secrets and direct personal identifiers.

## Security Checklist

- [ ] `.env` is ignored and never committed.
- [ ] API keys are injected by environment or secret manager.
- [ ] Source events are redacted before ingest.
- [ ] TiDB access is scoped to the target database.
- [ ] Audit retention period is defined.
- [ ] Generated clarification questions are reviewed before customer-facing use.

## Evaluation Checklist

- [ ] Run `handovergap report --dataset all`.
- [ ] Run adversarial and sanitized splits.
- [ ] Track question actionability and redundancy.
- [ ] Compare optional LLM slot filling across model/prompt versions.
- [ ] Do not claim production accuracy from synthetic mini/holdout scores alone.

## Optional TiDB Path

TiDB is useful when you need one auditable store for:

- source events
- memory chunks with vectors
- profile requirements
- slot fill attempts
- context gaps
- clarification questions
- transfer assessments
- evaluation runs

Use `handovergap schema --dialect tidb`, `handovergap audit-sql`, and live validation scripts after credentials are configured.

For alpha validation databases that may contain an older HandoverGap schema, the validation scripts support `--reset-schema`. This drops and recreates the packaged HandoverGap tables, so do not use it against a database that contains user data.
