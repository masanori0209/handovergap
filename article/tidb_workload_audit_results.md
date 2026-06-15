# TiDB Generated Workload Audit Result

- Observed at: 2026-06-15
- Live TiDB scenarios persisted: 100
- Audit query result rows: 254
- Iterations: 10
- p50 latency: `38.818 ms`
- p95 latency: `574.713 ms`

This is a live TiDB Cloud validation result for generated workload auditability, not a load-test claim.

## Inserted Rows

| Table | Rows |
|---|---:|
| `source_events` | 100 |
| `memory_items` | 100 |
| `memory_chunks` | 200 |
| `slot_fill_attempts` | 567 |
| `context_gaps` | 254 |
| `clarification_questions` | 254 |
| `transfer_assessments` | 100 |

## Local Workload Scale

| Scenarios | Assessments | Gaps | Questions | Blocked | p50 local ms | p95 local ms |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 100 | 254 | 254 | 24 | 2.522 | 3.140 |
| 1000 | 1000 | 2505 | 2505 | 238 | 13.386 | 18.147 |
| 10000 | 10000 | 25007 | 25007 | 2382 | 143.003 | 143.636 |

## Sample Blocked Audit Rows

| Scenario | Profile | Missing slot | Severity | Evidence | Question |
|---|---|---|---|---|---|
| WORKLOAD-20260615144032-W0100 | CS | customer_facing_wording | MEDIUM | W0100 evidence 1: generated_note | 外部向けにはどの表現で説明すべきですか？ |
| WORKLOAD-20260615144032-W0100 | CS | scope | MEDIUM | W0100 evidence 1: generated_note | この判断の適用範囲はどこまでですか？ |
| WORKLOAD-20260615144032-W0100 | CS | authority | HIGH | W0100 evidence 1: generated_note | このプロファイルが回答または判断してよい範囲はどこまでですか？ |
| WORKLOAD-20260615144032-W0100 | CS | escalation_path | HIGH | W0100 evidence 1: generated_note | 問題が起きた場合のエスカレーション先は誰ですか？ |
| WORKLOAD-20260615144032-W0100 | CS | fallback_plan | HIGH | W0100 evidence 1: generated_note | 想定外の場合の代替手段は何ですか？ |
| WORKLOAD-20260615144032-W0099 | Sales | customer_expectation | MEDIUM | W0099 evidence 1: generated_note | 顧客の期待値はどの状態に調整されていますか？ |
| WORKLOAD-20260615144032-W0097 | CS | customer_facing_wording | MEDIUM | W0097 evidence 1: generated_note | 外部向けにはどの表現で説明すべきですか？ |
| WORKLOAD-20260615144032-W0095 | Engineer | failure_modes | MEDIUM | W0095 evidence 1: generated_note | 想定される失敗パターンと検知方法は何ですか？ |
