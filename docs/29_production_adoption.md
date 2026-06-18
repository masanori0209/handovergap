# Production Adoption Guide

HandoverGap is a stable public-contract readiness gate for RAG memories. The safe production adoption posture is still to start with observation and audit, not automatic blocking in critical workflows.

## Recommended Rollout

1. Run `TransferabilityGate` with `deployment_mode="shadow"` before final answer generation.
2. Store predicted gaps, generated questions, retrieved evidence ids, and transfer decisions.
3. Review false clarifications and missed gaps with domain reviewers.
4. Define custom YAML profiles for each operational context.
5. Promote blocking only after profile requirements and question quality are reviewed.

## Deployment Modes

Use `route_transferability_result(...)` to separate the gate recommendation from the action your product applies during rollout.

| Mode | Applied action | Stored/reviewed signal | Recommended rollout stage |
| --- | --- | --- | --- |
| `shadow` | Always `answer` | `recommended_action`, gaps, questions, score, evidence ids | First production observation period |
| `soft` | Always `answer` | Same as shadow, plus a visible warning or review badge | User-facing trial after reviewer calibration |
| `hard` | Apply `answer`, `ask`, or `block` | Enforced interruptions and their audit path | Only after local evaluation and review |

```python
from handovergap import TransferabilityGate, route_transferability_result

result = TransferabilityGate().check(
    memory=retrieved_memory,
    evidence=retrieved_evidence,
    profile=profile,
    task_context=task_context,
    evidence_slots=evidence_slots,
)
route = route_transferability_result(
    result,
    safe_context=retrieved_memory,
    deployment_mode="shadow",
)

audit_log.write(
    {
        "status": route.status,
        "action": route.action,
        "recommended_action": route.recommended_action,
        "deployment_mode": route.deployment_mode,
        "questions": route.questions,
        "reason": route.reason,
    }
)
```

For `shadow` and `soft`, your existing RAG answer can continue while HandoverGap records what it would have asked or blocked. For `hard`, `should_interrupt=True` means the product should ask questions or withhold the answer before final delivery.

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
- [ ] Compare reviewer labels against gold gaps and inspect disagreement examples.
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

For validation databases that may contain an older HandoverGap schema, the validation scripts support `--reset-schema`. This calls `destructive_reset_schema(..., confirm=RESET_CONFIRMATION)`, drops the packaged HandoverGap tables, and recreates them, so do not use it against a database that contains user data.
