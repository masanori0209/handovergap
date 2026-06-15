# Changelog

## Unreleased

### Notes

- No unreleased changes yet.

## 0.1.7 - 2026-06-16

### Added

- `handovergap --version`.
- An anonymized Slack-observed independent gap label review.
- 10k and 100k live TiDB generated workload audit validation outputs.

### Changed

- Bulked the live TiDB workload validation harness for larger audit-table runs.

## 0.1.6 - 2026-06-15

### Changed

- Replaced the public `successor_role` / `handover_task` vocabulary with `profile` / `task_context`.
- Replaced CLI `--role` with `--profile`.
- Generalized the product position from handover-only RAG to profile-conditioned context readiness.

### Added

- `TransferabilityGate` and `ContextReadinessGate` public APIs.
- YAML custom profiles via `TransferabilityGate.from_profile_file(...)` and `--profile-file`.
- JSONL source event ingest via `handovergap ingest`.
- Slot-level evidence retrieval via `handovergap retrieve-evidence`.
- TiDB vector retrieval SQL path using `VEC_COSINE_DISTANCE`.
- TiDB full-text retrieval SQL path using `MATCH(content) AGAINST (...)`.
- Hybrid retrieval with reciprocal rank fusion.
- Reproducible markdown report generation via `handovergap report`.
- Deterministic question-quality metrics.
- Generated workload benchmark via `handovergap workload-benchmark`.
- Security policy and production adoption guide.

### Notes

- This is alpha software. Breaking changes are allowed while the product vocabulary and evaluation methodology are being hardened.
