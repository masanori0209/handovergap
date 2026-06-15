# Loop 23: Live TiDB Schema Reset Validation

Date: 2026-06-15

## Plan

Close the remaining live TiDB evidence gap without increasing free-tier usage. Use the smallest live validation path: one persistence check and one sanitized audit-query check.

Winning filter:

- TiDB-specific learning: existing alpha tables can hide schema drift when `CREATE TABLE IF NOT EXISTS` is used.
- Article claim: blocked answers can be explained by SQL across assessments, gaps, slot attempts, evidence, and questions.
- Evaluation evidence: live TiDB rows should prove the audit path, not claim load-test performance.

## Act

- Added `TiDBStore.reset_schema(...)` for alpha validation databases.
- Added `--reset-schema` to `harness/validation/tidb_live_check.py`.
- Added `--reset-schema` to `harness/validation/tidb_audit_query_check.py`.
- Re-ran live TiDB validation with the current schema.
- Updated docs and article results with the latest live validation metrics.

## Observe

The first live run failed because the existing TiDB database still had old tables without `profile` and `source_event_id` columns. `CREATE TABLE IF NOT EXISTS` did not upgrade those tables, so the validation scripts needed an explicit reset path.

## Validate

- `.venv/bin/python harness/validation/tidb_live_check.py --reset-schema`
  - status: ok
  - inserted: 1 slot fill attempt, 1 context gap, 1 transfer assessment, 3 evaluation runs
- `.venv/bin/python harness/validation/tidb_audit_query_check.py --reset-schema --dataset sanitized --iterations 10`
  - status: ok
  - scenarios persisted: 6
  - audit query result rows: 7
  - inserted rows: 10 source events, 6 memory items, 16 memory chunks, 34 slot attempts, 7 gaps, 7 questions, 6 assessments
  - p50: 48.408 ms
  - p95: 1510.413 ms

## Reflect

The high p95 should not be framed as TiDB latency performance. It is useful as honest live validation evidence that the SQL audit path works on TiDB Cloud. The more important implementation insight is that alpha schema drift must be handled explicitly when validating against a reused cloud database.

## Update Context

For alpha live validation, use `--reset-schema` when the TiDB database may contain old HandoverGap tables. Do not run reset against a database that contains user data.

## Handoff

Remaining work is issue closure, full test pass, and commit/push/release decision.
