# Changelog

## Unreleased

### Breaking Changes

- None.

### Added

- Deployment modes for product routing: `shadow`, `soft`, and `hard`.
- Product route fields for rollout control: `recommended_action`, `deployment_mode`, `enforcement`, and `should_interrupt`.
- `handovergap detect --deployment-mode ...` for checking rollout behavior from the CLI.
- Follow-up retrieval planning for missing slots via `retrieval_mode="expand_before_ask"`.
- `FollowupRetrievalQuery` and `build_followup_retrieval_queries(...)` for bounded RAG expansion before asking a user.
- `handovergap detect --retrieval-mode expand-before-ask` for inspecting generated follow-up retrieval queries.

### Changed

- None.

### Deprecated

- None.

### Removed

- None.

### Fixed

- None.

### Security

- None.

### Notes

- `hard` and `ask_first` remain the default routing modes, so existing answer/ask/block behavior remains unchanged unless callers opt into `shadow`, `soft`, or `expand_before_ask`.

## 1.0.0 - 2026-06-18

### Added

- First stable public-contract release for HandoverGap as a profile-conditioned readiness gate for RAG and agent memory systems.
- Stable v1 contract for `TransferabilityGate.check(...)`, custom profile YAML, result fields, answer/ask/block routing, local user-dataset evaluation, and optional TiDB audit-store expectations.
- Public documentation paths for quickstart, CLI usage, Python API, profile YAML, RAG integration, TiDB audit store, evaluation, security/privacy, and versioning.

### Changed

- Package metadata now declares the v1 stable release and updates the project description beyond handover-only wording.
- User-facing docs now describe `1.0.0` as the stable public-contract baseline while preserving production-accuracy caveats.

### Security

- Core runtime remains local by default and does not require OpenAI, TiDB, Slack, GitHub, Streamlit, or any web app.
- Bundled datasets remain fictional/synthetic; user data evaluation should use anonymized local files.

### Notes

- v1 stability covers integration contracts, not a claim that bundled synthetic metrics predict production accuracy.
- TiDB and OpenAI remain optional integrations.

## 0.1.20 - 2026-06-18

### Added

- TiDB packaged schema metadata table, `TiDBStore.schema_state()`, and public `TiDBSchemaState`.
- `TiDBStore.destructive_reset_schema(..., confirm="drop-handovergap-tables")` for explicit alpha-only destructive resets.
- `TiDBStore.persist_memory_item(...)` for repeated validation runs with duplicate `scenario_id` values.
- `TiDBStoreOperationError` with credential-redacted operation failure messages.

### Changed

- `create_schema()` now writes packaged schema metadata after idempotent table creation.
- Live TiDB validation scripts now call the explicitly destructive reset API.
- README and GitHub Pages document TiDB lifecycle behavior and alpha-only reset safety.

## 0.1.19 - 2026-06-18

### Added

- `docs/31_versioning_policy.md` defining pre-v1 flexibility, v1 stable surfaces, post-v1 major-version triggers, and release checklist additions.
- GitHub Pages and README links for the versioning policy.

### Changed

- Release playbook now includes API, CLI, profile YAML, result model, routing, dataset, metric, and TiDB audit compatibility checks.
- Changelog now keeps a v1-ready `Unreleased` structure for breaking changes, additions, changes, deprecations, removals, fixes, and security notes.

## 0.1.18 - 2026-06-18

### Changed

- Reworked GitHub Pages into task-oriented library documentation sections for quickstart, CLI, Python API, profile YAML, RAG integration, TiDB audit, evaluation, and security/privacy.
- Added README and Japanese README shortcuts to the main documentation sections.
- Strengthened public docs language so bundled synthetic scores are not presented as production accuracy claims.

### Added

- Documentation regression tests for required GitHub Pages sections and production-accuracy caveats.

## 0.1.17 - 2026-06-18

### Added

- `handovergap privacy-check` for scanning public docs, examples, and packaged data for obvious secrets and direct identifiers.
- Public `scan_privacy(...)` and `PrivacyFinding` helpers.
- Tests for privacy scanning and redacted findings.

### Changed

- Expanded `.gitignore` for local user-dataset evaluation artifacts.
- Security and documentation now describe default offline data flow and optional OpenAI/TiDB/Streamlit paths.

## 0.1.16 - 2026-06-18

### Added

- `handovergap datasets export-template` for creating local annotation CSVs from anonymized user datasets.
- `handovergap datasets import-labels` for merging reviewed labels back into a local JSONL dataset.
- `handovergap evaluate --dataset-file` and `handovergap report --dataset-file` for local user-provided evaluation.
- Public `load_user_dataset(...)`, `export_annotation_template(...)`, and `import_reviewed_labels(...)` helpers.

### Changed

- Evaluation reports now distinguish bundled synthetic datasets from user-provided local datasets.
- Annotation templates omit raw memory and evidence text by default.

## 0.1.15 - 2026-06-18

### Added

- Public slot filling mode metadata for `user_provided`, `deterministic_rules`, and `optional_llm`.
- Evaluation output now labels slot fill mode, slot source, model, and prompt profile.
- Evaluation reports now document slot fill modes and LLM reporting expectations.

### Changed

- CLI evaluation rejects `--slot-fill-mode optional_llm` unless a `--model` label is supplied.
- README, Japanese README, and GitHub Pages now clarify that core runtime does not require OpenAI.

## 0.1.14 - 2026-06-18

### Changed

- Improved unknown profile, unknown slot, malformed evidence, invalid JSONL source event, and invalid route status errors.
- Avoided echoing raw evidence or source-event payloads in malformed input errors.
- Documented common actionable errors in README and GitHub Pages.

### Added

- Tests for representative invalid inputs and payload non-disclosure.

## 0.1.13 - 2026-06-18

### Added

- `handovergap profiles validate <path>` to validate custom profile YAML before use.
- Public `validate_profile_file(...)` and `ProfileValidationResult` helpers.
- Tests for valid profile files and actionable validation errors.
- README and GitHub Pages documentation for validating custom profiles.

## 0.1.12 - 2026-06-18

### Added

- `docs/30_rag_integration_recipes.md` with framework-neutral, LangChain, and LlamaIndex integration recipes.
- README, README.ja, and GitHub Pages links to the RAG integration recipes.

### Changed

- Expanded `examples/langchain_gate.py` and `examples/llamaindex_gate.py` to map framework outputs into evidence events and product routes.
- Strengthened example tests to assert answer/ask/block route output.

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
