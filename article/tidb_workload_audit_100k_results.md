# TiDB Generated Workload Audit Result

- Observed at: 2026-06-15
- Scale label: `100k-audit-tables`
- Live TiDB scenarios persisted: 100000
- Memory chunks included: `False`
- Insert duration: `140809.576 ms`
- Audit query result rows: 250004
- Iterations: 10
- p50 latency: `14236.62 ms`
- p95 latency: `15074.449 ms`

This is a live TiDB Cloud validation result for generated workload auditability, not a load-test claim.

## Inserted Rows

| Table | Rows |
|---|---:|
| `source_events` | 100000 |
| `memory_items` | 100000 |
| `memory_chunks` | 0 |
| `slot_fill_attempts` | 566667 |
| `context_gaps` | 250004 |
| `clarification_questions` | 250004 |
| `transfer_assessments` | 100000 |

## Local Workload Scale

| Scenarios | Assessments | Gaps | Questions | Blocked | p50 local ms | p95 local ms |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 100 | 254 | 254 | 24 | 0.770 | 0.910 |
| 1000 | 1000 | 2505 | 2505 | 238 | 7.206 | 8.218 |
| 10000 | 10000 | 25007 | 25007 | 2382 | 74.322 | 77.139 |

## Sample Blocked Audit Rows

| Scenario | Profile | Missing slot | Severity | Evidence | Question |
|---|---|---|---|---|---|
| WORKLOAD-20260615150539-W99921 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99921 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99003 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99003 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99933 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99933 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99939 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99939 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99927 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99927 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99009 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99009 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99915 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99915 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615150539-W99015 | Sales | customer_expectation | MEDIUM | WORKLOAD-20260615150539-W99015 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
