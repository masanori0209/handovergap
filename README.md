# HandoverGap RAG

[![CI](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml/badge.svg)](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

[日本語](#日本語) | Repository version: [README.ja.md](https://github.com/masanori0209/handovergap/blob/main/README.ja.md)

HandoverGap RAG detects tacit context that is missing from otherwise correct organizational memories.

> Correct memories are not always transferable.

PyPI: https://pypi.org/project/handovergap/

Latest tested release: `handovergap==0.1.17`

Usage guide: https://masanori0209.github.io/handovergap/

A normal RAG system may retrieve:

```text
For Company A, use CSV for this release. The API will come in the next phase.
```

The statement can be correct while still being unsafe for a specific profile and task context. The person or agent acting on it may not know:

- whether the customer was informed;
- what “this release” covers;
- what the selected profile is authorized to promise;
- what fallback or escalation path to use.

HandoverGap performs profile-conditioned context readiness checks, blocks unsafe transfer, and generates clarification questions. The packaged dataset uses Support, Engineering, and Sales handover presets as examples; the thesis is not limited to those business functions or to handover workflows.

![Naive RAG answers directly while HandoverGap blocks and asks profile-required questions](docs/assets/naive-vs-handovergap.svg)

## What HandoverGap Adds

| Approach | What it optimizes | What it misses |
|---|---|---|
| Naive RAG | Return a relevant memory | Whether a profile can safely act on it |
| Hybrid RAG | Add related evidence or risk warnings | Profile-specific missing context |
| General context engineering | Better prompts and context packaging | A durable audit trail for why an answer was withheld |
| HandoverGap RAG | Check profile-required slots before answering | Production tuning still needs real organizational annotation |

The practical pattern is:

1. Treat correctness and transferability as separate checks.
2. Define required slots per profile and task context.
3. Do not invent missing context; turn missing slots into questions.
4. Store the slot attempts, gaps, questions, and transfer decision so the stop reason is explainable.

## Quickstart

```bash
pip install handovergap

handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
```

No TiDB account, OpenAI key, or external dataset is required.

## Demo

Install the optional Streamlit UI:

```bash
pip install "handovergap[demo]"
handovergap serve
```

The demo defaults to Japanese and includes an English language switch. The default local-sample mode runs the real deterministic HandoverGap detector against bundled fictional operational cases. It compares:

- `naive_rag`: answers directly;
- `hybrid_rag`: adds related evidence;
- `handovergap`: withholds unsafe answers and asks questions.

For a live semantic slot-filling demo with OpenAI and TiDB audit persistence:

```bash
pip install "handovergap[live]"
handovergap serve
```

Set `OPENAI_API_KEY` plus either `HANDOVERGAP_TIDB_URL` or the `TIDB_HOST` / `TIDB_USER` / `TIDB_PASSWORD` environment variables. In **Live OpenAI + TiDB** mode, the app asks the selected model to fill profile-required slots, runs HandoverGap on those filled slots, and persists slot-fill attempts, context gaps, and transfer assessments to TiDB.

In the current MVP, `CS`, `Engineer`, and `Sales` are built-in profile presets used to demonstrate different profile-specific responsibilities. They are not meant to imply that HandoverGap only works for those departments; custom profile/slot taxonomies are the natural extension point beyond the packaged benchmark.

## Evaluation

`handovergap evaluate --compare` runs the bundled synthetic HandoverGapBench mini dataset.

To generate a reproducible markdown report across all bundled datasets:

```bash
handovergap report --dataset all --output reports/evaluation-latest.md
```

The report includes deterministic comparison metrics and a question-quality section for slot coverage, actionability, and redundancy.

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.21 | 0.59 | 0.21 | 0.67 | 0.91 | 1.00 |
| handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

These are deterministic results from the bundled 20-scenario dataset. The benchmark is synthetic and intentionally small; it demonstrates reproducible behavior rather than production accuracy.

For a small unknown holdout set with adjudicated synthetic reviewer labels and slot-filling stress profiles:

```bash
handovergap evaluate --dataset holdout --stress-filling
```

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---:|---:|---:|---:|---:|---:|
| handovergap/provided | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 0.00 |
| handovergap/conservative | 1.00 | 0.67 | 1.00 | 0.67 | 0.67 | 1.00 |
| handovergap/optimistic | 0.64 | 0.67 | 0.64 | 1.00 | 1.00 | 0.00 |

The optimistic profile simulates an LLM over-filling ambiguous slots. It shows a real failure mode: recall drops, while unsafe-transfer prevention stays incomplete at `0.67`.

The adversarial split breaks the structural alignment between `provided_slots` and `gold_gaps`:

```bash
handovergap evaluate --dataset adversarial --compare
```

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.25 | 0.67 | 0.25 | 1.00 | 1.00 | 0.00 |
| handovergap | 0.38 | 0.67 | 0.38 | 1.00 | 1.00 | 0.00 |

This is intentionally harder. It shows that simply increasing scenario count is not enough when labels and detector inputs share the same structure. In `0.1.5`, HandoverGap also treats explicit evidence slots as filled, which reduces the adversarial false clarification rate from `0.67` to `0.00` without pretending recall is solved.

For a field-realistic but still non-sensitive dataset, use the sanitized split:

```bash
handovergap evaluate --dataset sanitized --compare
```

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.71 | 0.20 | 0.71 | 1.00 | 1.00 | 0.00 |
| handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

The sanitized split is synthetic, but it is written like anonymized CRM notes, incident timelines, runbooks, release checklists, and deal reviews. It does not include real company, employee, customer, ticket, or account data.

With optional live OpenAI semantic slot filling:

```bash
python harness/validation/openai_slot_filling_check.py --dataset holdout --persist-tidb
```

Observed with `gpt-4.1-mini`: tacit gap recall `0.91`, unsafe transfer prevention `0.33`, safe transfer allowance `0.67`, blocked precision `0.50`. The detailed per-scenario output is saved to `article/openai_slot_filling_results.json`.

Observed with `gpt-5-mini`: tacit gap recall `0.45`, unsafe transfer prevention `0.33`, safe transfer allowance `0.67`, blocked precision `0.50`. The run used 1,901 input tokens and 8,136 output tokens, including 5,184 reasoning tokens, for an estimated cost of about `$0.0167`. This lower recall is intentional evidence in the repository: semantic slot filling is model- and prompt-sensitive, so HandoverGap should report the sensitivity instead of hiding it.

With the tuned `gpt5_strict` prompt profile for `gpt-5-mini`: tacit gap recall `1.00`, unsafe transfer prevention `0.67`, safe transfer allowance `1.00`, blocked precision `1.00`. This prompt is calibrated to the holdout evidence-summary protocol, so it is useful model-specific evidence rather than a production accuracy claim.

![Japanese Streamlit demo](https://raw.githubusercontent.com/masanori0209/handovergap/main/docs/assets/demo-ja.png)

## Optional TiDB Store

```bash
pip install "handovergap[tidb]"
handovergap schema --dialect tidb
```

```python
from handovergap import TiDBStore

store = TiDBStore("mysql+pymysql://user:password@host:4000/handovergap")
store.create_schema()
```

The packaged schema models source evidence, memories, profile requirements, vectorized memory chunks, slot-fill attempts, context gaps, clarification questions, transfer assessments, and evaluation runs. Live persistence methods are available for memory chunks, slot-fill attempts, context gaps, transfer assessments, and evaluation runs.

Slot-level evidence retrieval can be inspected without a live database:

```bash
handovergap retrieve-evidence \
  --scenario S001 \
  --profile CS \
  --slot communication_status \
  --mode hybrid
```

The dry-run path uses deterministic local embeddings and token matching so first-run behavior is reproducible. The TiDB store exposes the matching live path with `memory_chunks.embedding VECTOR(1536)`, `VEC_COSINE_DISTANCE(embedding, :query_vector) ORDER BY distance ASC LIMIT :top_k`, and `MATCH(content) AGAINST (:query_text)` for exact names, issue IDs, and runbook references. Hybrid retrieval merges vector and full-text candidates with reciprocal rank fusion.

The TiDB-specific value is not only vector search. HandoverGap stores the whole decision path so a blocked answer can be traced with SQL:

```bash
handovergap audit-sql
handovergap audit-example
handovergap audit-benchmark --dataset all --iterations 100
```

That query joins `transfer_assessments`, `memory_items`, `context_gaps`, `slot_fill_attempts`, `source_events`, and `clarification_questions`. It answers the operational question: “this memory was retrieved, so exactly which required slot was missing, what evidence was checked, and what should we ask before handing it over?”

`audit-example` prints a compact blocked-transfer result table so the audit path can be reviewed without a live TiDB connection.

`audit-benchmark` measures local audit-row materialization for the bundled scenarios and reports row counts, blocked-transfer counts, top missing slots, and p50/p95 local runtime. It is not a TiDB latency claim; it sizes the audit workload that TiDB stores and queries.

For a larger generated workload sizing check:

```bash
handovergap workload-benchmark --scenarios 1000 --iterations 5
```

This reports local materialization counts and p50/p95 runtime for generated synthetic scenarios. It is not a live TiDB load test.

Live TiDB Cloud validation result for the blocked-transfer audit query:

| Item | Observed value |
|---|---:|
| Dataset persisted | `sanitized` |
| Scenarios | 6 |
| Source events | 10 |
| Slot-fill attempts | 34 |
| Context gaps | 7 |
| Clarification questions | 7 |
| Transfer assessments | 6 |
| Audit query result rows | 7 |
| Query iterations | 10 |
| p50 audit query latency | `48.408 ms` |
| p95 audit query latency | `1510.413 ms` |

This is a live TiDB Cloud validation result over 10 iterations, not a load-test claim. The p95 includes cold/variable cloud latency and should be read as proof that the audit path runs on a real database, not as a performance benchmark. The detailed output is saved in [`article/tidb_audit_query_results.md`](article/tidb_audit_query_results.md).

Generated workload validation on live TiDB Cloud:

| Item | Observed value |
|---|---:|
| Generated scenarios persisted | 10,000 |
| Source events | 10,000 |
| Memory chunks | 20,000 |
| Slot-fill attempts | 56,667 |
| Context gaps | 25,007 |
| Clarification questions | 25,007 |
| Transfer assessments | 10,000 |
| Audit query result rows | 25,007 |
| Query iterations | 10 |
| p50 audit query latency | `1374.01 ms` |
| p95 audit query latency | `1478.298 ms` |

Free-tier 100k audit-table validation also succeeded with VECTOR/full-text chunk rows disabled to avoid unnecessary storage growth:

| Item | Observed value |
|---|---:|
| Generated scenarios persisted | 100,000 |
| Source events | 100,000 |
| Memory chunks | 0 |
| Slot-fill attempts | 566,667 |
| Context gaps | 250,004 |
| Clarification questions | 250,004 |
| Transfer assessments | 100,000 |
| Audit query result rows | 250,004 |
| Query iterations | 10 |
| p50 audit query latency | `14236.62 ms` |
| p95 audit query latency | `15074.449 ms` |

The 10k and 100k generated workload results are saved in [`article/tidb_workload_audit_10k_results.md`](article/tidb_workload_audit_10k_results.md) and [`article/tidb_workload_audit_100k_results.md`](article/tidb_workload_audit_100k_results.md). These are live TiDB audit-path validations, not load-test claims.

Independent reviewer-style labels derived from anonymized Slack-observed handover patterns are saved in [`article/independent_gap_label_review.md`](article/independent_gap_label_review.md). Raw Slack messages, names, customer names, URLs, and IDs are not stored.

### Live TiDB Validation

After creating a TiDB Cloud cluster, open **Connect**, choose a public Python/SQLAlchemy-compatible connection, generate or reset the password, and export the connection values locally:

```bash
export TIDB_HOST="..."
export TIDB_PORT="4000"
export TIDB_USER="..."
export TIDB_PASSWORD="..."
export TIDB_DB_NAME="test"
export TIDB_CA_PATH="/path/to/ca-certificates.crt"
```

Then run:

```bash
python harness/validation/tidb_live_check.py --reset-schema
python harness/validation/tidb_audit_query_check.py --reset-schema --dataset sanitized --iterations 10
```

The check recreates the packaged schema, writes synthetic memory and evidence rows, persists slot-fill attempts, context gaps, transfer assessments, and evaluation runs, then prints row counts as JSON. `--reset-schema` drops packaged HandoverGap tables first, so use it only for alpha validation databases without user data. Do not commit `.env` files or TiDB credentials.

## Python API

```python
from handovergap import TransferabilityGate

gate = TransferabilityGate()
result = gate.check(
    memory="Use CSV for this release; API support is deferred.",
    profile="CS",
    task_context="Answer customer questions about the workaround.",
    evidence=["CSV workaround approved for the release."],
    provided_slots=["scope"],
    evidence_slots=["scope"],
)

print(result.transferability_status)
print(result.gaps)
print(result.questions)
```

Use `TransferabilityGate.from_builtin_dataset().check_builtin("S001", profile="CS")` to inspect the packaged scenarios. The current built-in presets use `CS`, `Engineer`, and `Sales`, but the public data model is intentionally named around `profile` and `task_context` so custom domains can define their own readiness checks.

### API Contract

The stable integration surface is `TransferabilityGate.check(...)`. The core API works without OpenAI or TiDB.

Stable inputs:

| Input | Meaning |
| --- | --- |
| `memory` | Retrieved memory, note, decision, runbook line, or agent memory to check. |
| `profile` | Role or operating mode that wants to use the memory. |
| `task_context` | What the profile is trying to do with the memory. |
| `evidence` | Optional supporting snippets as strings, dictionaries, or `EvidenceEvent` objects. |
| `provided_slots` | Required slots already explicit in the memory. |
| `evidence_slots` | Required slots supported by retrieved evidence. |
| `scenario_id` | Optional caller-provided identifier, defaulting to `inline`. |
| `memory_type` | One of `decision`, `procedure`, `risk`, or `task`. |

Stable outputs:

| Output | Meaning |
| --- | --- |
| `transferability_status` | One of `transferable`, `needs_clarification`, or `blocked`. |
| `transferability_score` | Readiness score between 0 and 1. |
| `gaps` | Missing profile-required context. |
| `questions` | Clarification questions that turn missing context into next actions. |
| `scenario_id`, `profile`, `memory`, `task_context` | Echoed context for routing and audit. |

### End-To-End Integration Example

Run the framework-neutral example when you want to see the full adoption path:

```bash
python examples/end_to_end_integration.py
```

It simulates an existing RAG pipeline:

1. Retrieve a candidate memory and evidence snippets.
2. Map retrieved evidence to supported slots.
3. Call `TransferabilityGate.check(...)`.
4. Convert the result into an `answer`, `ask`, or `block` product route.

Expected shape:

```text
== first retrieval ==
provided_slots=scope
evidence_slots=communication_status,authority,customer_facing_wording
status=blocked action=block
gaps=fallback_plan,escalation_path
questions:
- 想定外の場合の代替手段は何ですか？
- 問題が起きた場合のエスカレーション先は誰ですか？
safe_context=withheld

== after retrieving runbook evidence ==
provided_slots=scope
evidence_slots=communication_status,authority,fallback_plan,escalation_path,customer_facing_wording
status=transferable action=answer
gaps=none
questions=none
safe_context=available
```

Use this example as the day-one integration pattern. OpenAI slot filling can replace
the deterministic keyword mapper, and TiDB can persist the resulting audit trail,
but neither is required by the core runtime.

### Evidence-To-Slot Mapping

The gate does not treat raw evidence text as automatically true. Integrations should pass slot support explicitly:

- `provided_slots`: required context already explicit in the retrieved memory.
- `evidence_slots`: required context supported by retrieved evidence.

For a first deterministic integration, map raw snippets to slots with keyword rules:

```python
from handovergap import TransferabilityGate, map_evidence_slots_by_keywords

evidence = [
    "Customer notice was sent on Monday with approved wording.",
    "Support can answer standard questions, but must not promise API dates.",
    "If CSV import fails, use the manual upload fallback and escalate in the support channel.",
]
slot_keywords = {
    "communication_status": ["notice was sent", "customer notice"],
    "authority": ["can answer", "must not promise"],
    "fallback_plan": ["fallback", "manual upload"],
    "escalation_path": ["escalate", "support channel"],
    "customer_facing_wording": ["approved wording"],
}

evidence_slots = map_evidence_slots_by_keywords(evidence, slot_keywords)

result = TransferabilityGate().check(
    memory="Use CSV for this release; API support is deferred.",
    profile="CS",
    task_context="Answer customer questions without overpromising.",
    evidence=evidence,
    provided_slots=["scope"],
    evidence_slots=evidence_slots,
)
```

Manual mapping, deterministic rules, and optional LLM slot filling can all feed the same `evidence_slots` contract. The core API does not require an LLM.

### Slot Filling Modes

HandoverGap is a gate over slots, not an LLM-only extractor. Integrations can choose one of three slot input modes:

| Mode | Best for | Runtime dependency | Reporting expectation |
| --- | --- | --- | --- |
| `user_provided` | Reviewed slots from your own workflow, annotations, forms, or upstream tools | None | Treat as caller-owned evidence |
| `deterministic_rules` | Keyword, parser, schema, or ETL-derived slots | None | Version the rule set in your app |
| `optional_llm` | Semantic extraction from messy notes or retrieved evidence | Optional model client | Report model and prompt profile |

The benchmark CLI labels the selected mode so results do not look more certain than they are:

```bash
handovergap evaluate --compare --slot-fill-mode user_provided
handovergap evaluate --slot-fill-mode optional_llm --model gpt-example --prompt-profile strict
```

### User Dataset Annotation Workflow

Bundled datasets are fictional and useful for reproducibility, but production adoption needs local evaluation on your own anonymized data. HandoverGap supports a local `annotate -> import labels -> evaluate -> report` loop without committing private data to the repository.

Prepare a JSONL, JSON, or CSV file with anonymized scenarios. Each scenario should include `scenario_id`, `memory`, `profile`, `memory_type`, `task_context`, `provided_slots`, and `evidence_slots`. Then export a review template:

```bash
handovergap datasets export-template ./local/anonymized_scenarios.jsonl --output ./local/labels.csv
```

The template includes scenario id, profile, task context, required slots, and slot columns, but it does not copy raw memory or evidence text. Reviewers fill `gold_gap_slots`, `gold_question_slots`, `unsafe_transfer_label`, and `annotation_notes` locally.

Merge reviewed labels and evaluate:

```bash
handovergap datasets import-labels ./local/anonymized_scenarios.jsonl \
  --labels ./local/labels.csv \
  --output ./local/reviewed_scenarios.jsonl

handovergap evaluate --dataset-file ./local/reviewed_scenarios.jsonl --compare
handovergap report --dataset-file ./local/reviewed_scenarios.jsonl --output ./local/evaluation.md
```

Reports generated with `--dataset-file` are labeled as user-provided local evaluation artifacts so they are not confused with bundled synthetic benchmark results.

### Privacy Defaults

The core package runs locally by default. `demo`, `detect`, `evaluate`, `report`, `ingest`, `profiles validate`, and `privacy-check` do not call OpenAI, TiDB, Slack, GitHub, or other external services. OpenAI slot filling, TiDB persistence, and Streamlit live mode are optional paths that require explicit extras and credentials.

Before publishing docs, examples, or packaged data, run:

```bash
handovergap privacy-check
```

For user datasets, keep raw files and reviewed labels outside git, for example under `local/`, and remove real company names, customer names, employee names, channel names, direct user IDs, URLs, email addresses, payment details, and secrets.

### Product Routing

Use `route_transferability_result(...)` when your application needs a structured answer/ask/block response.

| `transferability_status` | `action` | Product behavior |
| --- | --- | --- |
| `transferable` | `answer` | Continue to answer or action generation. |
| `needs_clarification` | `ask` | Ask the returned questions before finalizing the answer. |
| `blocked` | `block` | Withhold the answer/action and show the missing context questions to the responsible user. |

```python
from handovergap import TransferabilityGate, route_transferability_result

result = TransferabilityGate().check(
    memory="Use CSV for this release; API support is deferred.",
    profile="CS",
    task_context="Answer customer questions without overpromising.",
    provided_slots=["scope"],
)

route = route_transferability_result(result, safe_context=result.memory)

return {
    "status": route.status,
    "action": route.action,
    "reason": route.reason,
    "questions": route.questions,
    "safe_context": route.safe_context,
}
```

`safe_context` is only returned for `transferable` results. Clarification and blocked routes omit it so applications do not accidentally expose context that is not ready to use.

### Custom Profiles

```python
from handovergap import TransferabilityGate

gate = TransferabilityGate.from_profile_file("examples/profiles/incident_readiness.yml")
result = gate.check(
    memory="The checkout incident is mitigated by disabling the new queue worker.",
    profile="IncidentCommander",
    task_context="Decide whether customer-facing mitigation is complete.",
    provided_slots=["rollback_owner"],
)
```

The same profile file can be used from the CLI:

```bash
handovergap profiles validate examples/profiles/incident_readiness.yml

handovergap detect \
  --scenario S001 \
  --profile IncidentCommander \
  --profile-file examples/profiles/incident_readiness.yml
```

`profiles validate` checks required keys, duplicate slots, severity values, and missing questions before you use the profile in a gate.

### Actionable Errors

Common configuration mistakes are reported without echoing raw evidence payloads:

| Mistake | Message includes |
| --- | --- |
| Unknown profile | The requested profile and available profile names. |
| Unknown slot | The requested slot and available slots for that profile. |
| Malformed evidence | The evidence item index and required field names such as `source_type` and `content`. |
| Invalid profile YAML | The file path, profile name, slot name, and validation rule to fix. |
| Invalid route status | The accepted status values: `transferable`, `needs_clarification`, `blocked`. |

### JSONL Source Events

Use JSONL when you want to test Slack/Issue/CRM-style records without adding direct integrations:

```bash
handovergap ingest examples/source_events/customer_escalation.jsonl \
  --memory "Use CSV for this release; API support is deferred." \
  --profile CS \
  --task-context "Answer customer questions about the workaround."
```

Each line is a source event with `source_type`, `content`, and optional `title`, `source_url`, `actor_name`, `project_name`, `occurred_at`, and `metadata`.

### RAG Framework Examples

Copyable recipes are in [RAG Integration Recipes](docs/30_rag_integration_recipes.md).

Runnable examples show where to place the gate before final answer generation:

```bash
python examples/end_to_end_integration.py
python examples/langchain_gate.py
python examples/llamaindex_gate.py
```

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,demo]"
.venv/bin/pytest
```

## Production And Security

- [Production adoption guide](docs/29_production_adoption.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Limitations

- The bundled detector and baselines are deterministic rules, not learned models.
- HandoverGapBench mini and holdout contain synthetic scenarios; the sanitized split is field-realistic but still synthetic and non-sensitive.
- Adding more scenarios alone does not prove production accuracy if required slots and gold gaps are structurally aligned; independent annotation is the next step.
- Slot-filling stress profiles simulate LLM variance; they are not a replacement for a live LLM evaluation.
- Live OpenAI slot filling is optional and not required for first-run usage.
- Live OpenAI slot filling is model-sensitive; current holdout results differ materially between `gpt-4.1-mini` and `gpt-5-mini`.
- The Streamlit demo uses fictional operational cases. Live OpenAI + TiDB mode exercises OpenAI slot filling and TiDB audit persistence, but it is still a local demo rather than a production retrieval service.
- Semantic equivalence scoring for generated questions is not implemented in the MVP.
- Live TiDB integration requires the optional `tidb` extra and a configured database.

## License

MIT

## 日本語

HandoverGap RAGは、正しい業務記憶に不足している暗黙前提を、プロファイルと作業文脈ごとに検出します。

> 正しい記憶でも、引き継げるとは限らない。

```bash
pip install handovergap
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
```

Streamlitデモは日本語がデフォルトで、英語へ切り替えられます。

```bash
pip install "handovergap[demo]"
handovergap serve
```

詳細な日本語ドキュメントは[README.ja.md](https://github.com/masanori0209/handovergap/blob/main/README.ja.md)を参照してください。
