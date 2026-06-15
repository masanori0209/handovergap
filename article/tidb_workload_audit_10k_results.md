# TiDB Generated Workload Audit Result

- Observed at: 2026-06-15
- Scale label: `10k-chunked`
- Live TiDB scenarios persisted: 10000
- Memory chunks included: `True`
- Insert duration: `57861.309 ms`
- Audit query result rows: 25007
- Iterations: 10
- p50 latency: `1374.01 ms`
- p95 latency: `1478.298 ms`

This is a live TiDB Cloud validation result for generated workload auditability, not a load-test claim.

## Inserted Rows

| Table | Rows |
|---|---:|
| `source_events` | 10000 |
| `memory_items` | 10000 |
| `memory_chunks` | 20000 |
| `slot_fill_attempts` | 56667 |
| `context_gaps` | 25007 |
| `clarification_questions` | 25007 |
| `transfer_assessments` | 10000 |

## Local Workload Scale

| Scenarios | Assessments | Gaps | Questions | Blocked | p50 local ms | p95 local ms |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 100 | 254 | 254 | 24 | 0.830 | 0.938 |
| 1000 | 1000 | 2505 | 2505 | 238 | 7.206 | 8.671 |
| 10000 | 10000 | 25007 | 25007 | 2382 | 110.323 | 122.158 |

## Sample Blocked Audit Rows

| Scenario | Profile | Missing slot | Severity | Evidence | Question |
|---|---|---|---|---|---|
| WORKLOAD-20260615150408-W9549 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9549 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9501 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9501 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9531 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9531 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9525 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9525 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9591 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9591 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9567 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9567 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9585 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9585 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150408-W9519 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150408-W9519 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
