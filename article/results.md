# HandoverGapBench mini Results

Command:

```bash
handovergap evaluate --compare
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 20 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| hybrid_rag | 20 | 0.21 | 0.59 | 0.21 | 0.67 | 0.91 |
| handovergap | 20 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

## Holdout And Slot Filling Stress

Command:

```bash
handovergap evaluate --dataset holdout --stress-filling
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|---:|
| handovergap/provided | 6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| handovergap/conservative | 6 | 1.00 | 1.00 | 1.00 | 0.67 | 0.75 |
| handovergap/optimistic | 6 | 0.64 | 1.00 | 0.64 | 1.00 | 1.00 |

## Adversarial And Sanitized Splits

The adversarial split breaks the structural alignment between slot-filler output and gold gaps. After evidence-backed slot reconciliation in `0.1.5`, HandoverGap still has low recall on this split, but it no longer over-asks on safe cases.

| Dataset | Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| adversarial | handovergap | 6 | 0.38 | 0.67 | 0.38 | 1.00 | 1.00 | 0.00 |
| sanitized | handovergap | 6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

The sanitized split is still synthetic, but it is written like anonymized CRM notes, incident timelines, runbooks, release checklists, and deal reviews. It is meant to be more realistic than the mini benchmark without introducing real company or customer data.

## Live OpenAI Semantic Slot Filling

Command:

```bash
python harness/validation/openai_slot_filling_check.py --dataset holdout --persist-tidb
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|
| handovergap/openai-slot-fill/gpt-4.1-mini | 6 | 0.91 | 0.33 | 0.67 | 0.50 |
| handovergap/openai-slot-fill/gpt-5-mini | 6 | 0.45 | 0.33 | 0.67 | 0.50 |
| handovergap/openai-slot-fill/gpt-5-mini/gpt5_strict | 6 | 1.00 | 0.67 | 1.00 | 1.00 |

The detailed per-scenario outputs are stored in `article/openai_slot_filling_results.json`, `article/openai_slot_filling_results_gpt5mini.json`, and `article/openai_slot_filling_results_gpt5mini_strict.json`.

The `gpt-5-mini` run used 1,901 input tokens and 8,136 output tokens, including 5,184 reasoning tokens. At the observed GPT-5 mini text pricing of $0.25 per 1M input tokens and $2.00 per 1M output tokens, this six-scenario validation cost about `$0.0167`.

The tuned `gpt5_strict` prompt used 4,351 input tokens and 8,803 output tokens, including 6,400 reasoning tokens, for about `$0.0187`.

## Interpretation

- `naive_rag` returns retrieved memories without checking transferability.
- `hybrid_rag` can identify one explicit risk and blocks only when that risk is high severity.
- `handovergap` checks every slot required by the successor responsibility profile.
- `handovergap/optimistic` simulates an LLM over-filling ambiguous slots; recall drops because some truly missing slots are treated as filled.
- Live OpenAI semantic slot filling is model-sensitive. `gpt-4.1-mini` improves recall versus the optimistic simulation, while the first `gpt-5-mini` prompt drops recall to 0.45. A model-specific strict-evidence prompt raises `gpt-5-mini` recall to 1.00 on this holdout split by preventing optimistic filling of ambiguous slots.
- The strict prompt still over-asks in at least one safe case (`U006`: `timeline_confidence`). Current headline metrics punish unsafe blocking, but do not fully penalize unnecessary clarification.

## Important Limitation

These are results on small synthetic benchmarks. The holdout split, slot-filling stress profiles, and live OpenAI check expose real limitations, but they are still not a substitute for independent real-world annotation or online production validation.

## Live Demo Smoke Check

The Streamlit demo has two modes and defaults to Japanese copy:

- `ローカルサンプル` / `Local sample`: runs the deterministic HandoverGap detector against fictional handover cases without OpenAI or TiDB.
- `実LLM + TiDB` / `Live OpenAI + TiDB`: fills profile-required slots with OpenAI, runs HandoverGap on the filled slots, and persists slot-fill attempts, context gaps, and transfer assessments to TiDB.

The packaged `CS`, `Engineer`, and `Sales` values are preset IDs, not a fixed industry taxonomy. The UI presents them as handover profiles: support handover, engineering operations handover, and sales handover.

Observed after the `0.1.3` patch:

| Check | Result |
|---|---|
| TiDB Cloud API project lookup | 1 project, 1 cluster |
| Cluster | `handovergap-free-dev` |
| Cluster status | `AVAILABLE` |
| SQL connection | `8.0.11-TiDB-v8.5.3-serverless` |
| Existing HandoverGap tables | 11/11 present |
| Live demo OpenAI run | `gpt-5-mini` succeeded |
| Live demo TiDB persistence | 8 rows inserted |

## TiDB Audit Query

`handovergap audit-sql` prints the packaged blocked-transfer audit query. It joins `transfer_assessments`, `memory_items`, `context_gaps`, `slot_fill_attempts`, `source_events`, and `clarification_questions` so a blocked result can be explained from the transfer decision back to missing profile-required slots, checked evidence, and generated questions.

Observed live on TiDB Cloud with the `sanitized` split:

| Item | Value |
|---|---:|
| Scenarios persisted | 6 |
| Source events | 10 |
| Slot-fill attempts | 34 |
| Context gaps | 7 |
| Clarification questions | 7 |
| Transfer assessments | 6 |
| Audit query result rows | 7 |
| Query iterations | 30 |
| p50 audit query latency | `22.166 ms` |
| p95 audit query latency | `30.117 ms` |

See `article/tidb_audit_query_results.md` and `article/tidb_audit_query_results.json` for the sample rows and EXPLAIN output.
