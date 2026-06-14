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
| handovergap | 20 | 1.00 | 0.65 | 1.00 | 1.00 | 1.00 |

## Holdout And Slot Filling Stress

Command:

```bash
handovergap evaluate --dataset holdout --stress-filling
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|---:|
| handovergap/provided | 6 | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 |
| handovergap/conservative | 6 | 1.00 | 0.67 | 1.00 | 0.67 | 0.67 |
| handovergap/optimistic | 6 | 0.64 | 0.67 | 0.64 | 1.00 | 1.00 |

## Live OpenAI Slot Filling

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
- `handovergap` checks every slot required by the successor role.
- `handovergap/optimistic` simulates an LLM over-filling ambiguous slots; recall drops because some truly missing slots are treated as filled.
- Live OpenAI slot filling is model-sensitive. `gpt-4.1-mini` improves recall versus the optimistic simulation, while the first `gpt-5-mini` prompt drops recall to 0.45. A model-specific strict-evidence prompt raises `gpt-5-mini` recall to 1.00 on this holdout split by preventing optimistic slot filling.
- The strict prompt still over-asks in at least one safe case (`U006`: `timeline_confidence`). Current headline metrics punish unsafe blocking, but do not fully penalize unnecessary clarification.

## Important Limitation

These are results on small synthetic benchmarks. The holdout split, slot-filling stress profiles, and live OpenAI check expose real limitations, but they are still not a substitute for independent real-world annotation or online production validation.
