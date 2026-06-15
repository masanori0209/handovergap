# Loop 24: TiDB Workload Audit Evidence

Date: 2026-06-15

## Plan

Strengthen the contest evidence for TiDB as an AI decision audit store, not merely a vector store. The target is Issue #15.

Winning filter:

- TiDB-specific learning: persisted slot attempts, gaps, clarification questions, transfer assessments, source events, and memory chunks can be joined to explain blocked transfer decisions.
- Article claim: HandoverGap adds auditability to profile-conditioned readiness decisions.
- Evaluation evidence: generated workload size should show audit row growth without using gold labels in runtime detection.

## Act

- Added `harness/validation/tidb_workload_audit_check.py`.
- Added batched TiDB persistence for generated workload validation via `--persist-batch-size`.
- Persisted generated workload scenarios to live TiDB Cloud and measured the audit query.
- Saved results to `article/tidb_workload_audit_results.json` and `article/tidb_workload_audit_results.md`.
- Reflected the results in README, README.ja, GitHub Pages, `article/results.md`, and `article/zenn_draft.md`.

## Observe

Persisting 100 scenarios in one transaction lost the TiDB connection from the client side. Batching the workload in groups of 10 scenarios completed successfully.

## Validate

- `.venv/bin/python harness/validation/tidb_workload_audit_check.py --reset-schema --scenarios 100 --iterations 10 --persist-batch-size 10 --local-scale 100,1000,10000`
- Live TiDB inserted rows:
  - source_events: 100
  - memory_items: 100
  - memory_chunks: 200
  - slot_fill_attempts: 567
  - context_gaps: 254
  - clarification_questions: 254
  - transfer_assessments: 100
- Audit query:
  - result rows: 254
  - p50: 38.818 ms
  - p95: 574.713 ms
- Local generated workload scale:
  - 100 scenarios: 254 gaps/questions
  - 1,000 scenarios: 2,505 gaps/questions
  - 10,000 scenarios: 25,007 gaps/questions
- `.venv/bin/ruff check .`
- `.venv/bin/pytest`

## Reflect

This should not be framed as a TiDB load benchmark. The stronger claim is that TiDB can hold and query the evidence chain behind profile-conditioned transfer decisions: memory, source events, slot attempts, gaps, questions, and final assessment.

## Update Context

For live generated workloads, use `--persist-batch-size 10` on the Developer Tier to avoid a large single transaction.

## Handoff

Issue #15 can be closed after this branch is pushed and CI remains green.
