# Versioning Policy

HandoverGap `1.0.0` is the first stable public-contract release. Earlier `0.x.y` releases were allowed to clean up API names, CLI names, profile schema, result fields, and TiDB schema details when the change improved product readiness.

The project still treats every release as a user-facing package release: breaking changes must be called out in the changelog, migration notes, and release checklist.

## Pre-v1 Policy

- `0.x.y` minor releases may include breaking changes.
- Breaking changes must be explicitly listed under `Breaking Changes` in `CHANGELOG.md`.
- The release notes must name the affected surface: Python API, CLI, profile YAML, result model, TiDB schema, dataset format, or report format.
- If a migration is needed, the release notes should include the old pattern, the new pattern, and the safest migration path.
- Core runtime must continue to avoid required OpenAI, TiDB, Slack, GitHub, or web app dependencies.

## v1 Stable Surfaces

Starting with `1.0.0`, the following surfaces are stable integration contracts.

| Surface | Stable contract |
| --- | --- |
| Python API | `TransferabilityGate.check(...)`, `TransferabilityGate.from_profile_file(...)`, `route_transferability_result(...)`, deployment modes, retrieval modes, follow-up retrieval query planning, `map_evidence_slots_by_keywords(...)`, public result fields, and public enum/string status values. |
| CLI | Commands used by the MVP loop: `demo`, `detect`, `evaluate`, `report`, `profiles validate`, `datasets export-template`, `datasets import-labels`, `privacy-check`, `schema`, `audit-sql`, `audit-example`, `audit-benchmark`, `retrieve-evidence`, `workload-benchmark`, and `serve`. |
| Profile YAML | `profiles`, profile names, `required_slots`, `slot_name`, `gap_type`, `description`, `question`, `severity`, and `high_risk`. |
| Result models | `transferability_status`, `transferability_score`, `gaps`, `questions`, `scenario_id`, `profile`, `memory`, `task_context`, gap fields, question fields, follow-up retrieval query fields, and product route fields such as `action`, `recommended_action`, `deployment_mode`, `retrieval_mode`, `enforcement`, `should_interrupt`, and `next_step`. |
| Routing semantics | Default `ask_first`: `transferable -> answer`, `needs_clarification -> ask`, and `blocked -> block`. Optional `expand_before_ask`: missing-slot results can route to `retrieve_more` before user clarification. |
| Evaluation inputs | Bundled dataset names, `--dataset-file` local reviewed dataset shape, and slot-fill mode labels. |
| TiDB audit store | Packaged table purposes, write methods for audit rows, and audit SQL expectations for tracing slot attempts, gaps, questions, and transfer assessments. |

## Major Version Triggers After v1

After `1.0.0`, use a major version for changes that would make a working integration behave differently or fail without caller changes.

- Rename or remove public Python API functions, classes, fields, or status values.
- Rename CLI commands, options, or output fields used for automation.
- Change profile YAML required keys or severity semantics.
- Change `DetectionResult`, gap, question, or product route field meanings.
- Change answer/ask/block routing semantics.
- Change `--dataset-file` requirements or evaluation metric definitions in a non-compatible way.
- Change TiDB schema expectations in a way that requires migration or makes older audit rows unreadable by the documented audit query.
- Add a required OpenAI, TiDB, Slack, GitHub, Streamlit, or web-app dependency to the core runtime.

## Minor And Patch Releases After v1

- Minor releases may add optional APIs, CLI options, profile fields, metrics, integrations, or audit columns when existing integrations continue to work.
- Patch releases should fix bugs, improve docs, add tests, or make compatible behavior more reliable.
- Deprecations should be documented for at least one minor release before removal.

## Release Checklist Additions

Before every release, answer:

1. Did any public Python API, CLI command, profile YAML field, result model field, route status, dataset shape, metric definition, or TiDB schema expectation change?
2. If yes, is it allowed pre-v1, or does it require a major version after v1?
3. Is the change listed under `Breaking Changes` or `Deprecated` in `CHANGELOG.md`?
4. Do README, GitHub Pages, and examples use the new contract?
5. Do tests cover the compatibility contract or migration path?

## Current Name Review

Current names are intentionally profile- and task-oriented rather than handover-only:

- Use `profile`, not `role`, so teams can model people, operating modes, reviewer modes, or agents.
- Use `task_context`, not only handover text, so the same gate can apply to support replies, incident response, legal review, renewal workflows, and agent memory checks.
- Use `TransferabilityGate` for the user-facing gate and keep `ContextReadinessGate` as an alias-level concept.
- Use `provided_slots` and `evidence_slots` to make the trust boundary explicit instead of treating raw retrieved text as complete context.
