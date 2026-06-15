# TiDB Audit Query Live Result

- Observed at: 2026-06-15
- Dataset: `sanitized`
- Scenarios persisted: 6
- Audit query result rows: 7
- Iterations: 10
- p50 latency: `48.408 ms`
- p95 latency: `1510.413 ms`

This is a live TiDB Cloud smoke result for the blocked-transfer audit query, not a load-test claim.

## Inserted Rows

| Table | Rows |
|---|---:|
| `source_events` | 10 |
| `memory_items` | 6 |
| `memory_chunks` | 16 |
| `slot_fill_attempts` | 34 |
| `context_gaps` | 7 |
| `clarification_questions` | 7 |
| `transfer_assessments` | 6 |

## Sample Audit Rows

| Scenario | Profile | Missing slot | Severity | Slot-fill status | Evidence | Question |
|---|---|---|---|---|---|---|
| AUDIT-20260615135741-R006 | Sales | timeline_confidence | MEDIUM | missing | R006 evidence 1: crm_note | 提示できる時期の確度はどの程度ですか？ |
| AUDIT-20260615135741-R005 | Engineer | rationale | MEDIUM | missing | R005 evidence 1: ops_note | この判断に至った理由は何ですか？ |
| AUDIT-20260615135741-R003 | Sales | negotiation_status | MEDIUM | missing | R003 evidence 1: crm_note | 交渉状況と未合意点は何ですか？ |
| AUDIT-20260615135741-R003 | Sales | promise_boundary | MEDIUM | missing | R003 evidence 1: crm_note | 顧客に約束してよい範囲はどこまでですか？ |
| AUDIT-20260615135741-R003 | Sales | contract_impact | HIGH | missing | R003 evidence 1: crm_note | 契約や商談への影響はありますか？ |
| AUDIT-20260615135741-R002 | Engineer | trigger_for_reconsideration | MEDIUM | missing | R002 evidence 1: incident_timeline | どの条件になったら再検討しますか？ |
