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

The detailed per-scenario output is stored in `article/openai_slot_filling_results.json`.

## Interpretation

- `naive_rag` returns retrieved memories without checking transferability.
- `hybrid_rag` can identify one explicit risk and blocks only when that risk is high severity.
- `handovergap` checks every slot required by the successor role.
- `handovergap/optimistic` simulates an LLM over-filling ambiguous slots; recall drops because some truly missing slots are treated as filled.
- Live OpenAI slot filling improves recall versus the optimistic simulation, but lowers unsafe-transfer prevention because some unsafe slots are filled too optimistically.

## Important Limitation

These are results on small synthetic benchmarks. The holdout split, slot-filling stress profiles, and live OpenAI check expose real limitations, but they are still not a substitute for independent real-world annotation or online production validation.
