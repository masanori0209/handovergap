# Independent Gap Label Review

- Observed at: 2026-06-15
- Dataset compared: `sanitized`
- Observation count: 5
- Exact matches: 2
- Mean Jaccard agreement: `0.533`

Raw Slack messages are not stored. The review keeps only anonymized pattern summaries and reviewer-style gap labels.

## Privacy Filters

- replace people with role placeholders
- replace customer and company names with tenant placeholders
- remove URLs, account IDs, ticket IDs, campaign IDs, and dates that can identify a specific conversation
- store pattern summaries and reviewer labels only

## Reviewer Labels vs Existing Gold Gaps

| Observation | Scenario | Profile | Reviewer slots | Gold slots | Reviewer-only | Gold-only | Jaccard |
|---|---|---|---|---|---|---|---:|
| SLACK-PATTERN-001 | R001 | CS | authority, communication_status | customer_facing_wording | authority, communication_status | customer_facing_wording | 0.000 |
| SLACK-PATTERN-002 | R002 | Engineer | escalation_path, technical_constraint, trigger_for_reconsideration | trigger_for_reconsideration | escalation_path, technical_constraint | - | 0.333 |
| SLACK-PATTERN-003 | R003 | Sales | contract_impact, negotiation_status, promise_boundary | contract_impact, negotiation_status, promise_boundary | - | - | 1.000 |
| SLACK-PATTERN-004 | R004 | CS | - | - | - | - | 1.000 |
| SLACK-PATTERN-005 | R005 | Engineer | failure_modes, rationale, trigger_for_reconsideration | rationale | failure_modes, trigger_for_reconsideration | - | 0.333 |

## Disagreement Examples

### SLACK-PATTERN-001 / R001

A successor sees that a handover explanation may not have been given, while ownership and assignment rules are inferred from a business system rather than explicitly transferred.

- Reviewer-only: authority, communication_status
- Gold-only: customer_facing_wording
- Note: Even if a workaround is known, the successor still needs to know whether stakeholders were told and who may answer.

### SLACK-PATTERN-002 / R002

A customer-facing question is urgent, but the technical fact, customer-facing wording, and escalation boundary are mixed in a single thread.

- Reviewer-only: escalation_path, technical_constraint
- Gold-only: -
- Note: The missing handover risk is not only retrieval; it is separating what is known, what can be said, and when to stop.

### SLACK-PATTERN-005 / R005

A checklist or operating rule exists, but the handover reveals that parts of the checklist were not consistently applied.

- Reviewer-only: failure_modes, trigger_for_reconsideration
- Gold-only: -
- Note: The gap is operational transferability: the next actor needs the reason, the failure mode, and the condition for reconsideration.
