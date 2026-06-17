# Changelog

## Unreleased

### Notes

- No unreleased changes yet.

## 0.1.11 - 2026-06-18

### Added

- `examples/end_to_end_integration.py`, a complete framework-neutral path from retrieved memory and evidence to slot mapping, gate checking, and product routing.
- README, README.ja, and GitHub Pages documentation for the end-to-end integration path.
- Example test coverage so the first practical integration path stays runnable.

## 0.1.10 - 2026-06-18

### Added

- `ProductRoute` and `route_transferability_result(...)` for answer / ask / block product routing.
- A runnable `examples/product_routing.py` example covering support reply, incident response, and agent action routing.
- Tests for `transferable`, `needs_clarification`, and `blocked` route semantics.
- README and GitHub Pages documentation for product routing behavior and `safe_context`.

## 0.1.9 - 2026-06-17

### Added

- `map_evidence_slots_by_keywords(...)` for deterministic first-pass evidence-to-slot mapping.
- A runnable `examples/evidence_to_slot_mapping.py` integration example.
- Tests showing evidence-backed slot reconciliation can change a blocked transfer into a transferable one when evidence supports the missing slots.
- README and GitHub Pages documentation for `provided_slots` versus `evidence_slots`.

## 0.1.8 - 2026-06-17

### Added

- API contract tests for `TransferabilityGate.check(...)` and `DetectionResult`.
- GitHub Pages documentation for stable API inputs, outputs, and status values.

### Changed

- Reframed public documentation and agent instructions around v1 product readiness instead of legacy launch planning.
- Moved legacy strategy documents out of user-facing `docs/` and into `project/archive/legacy_docs/`.
- Rewrote the product roadmap around real RAG integration, evidence-to-slot mapping, product routing semantics, custom profiles, evaluation honesty, and privacy-safe defaults.

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
