# HandoverGapBench mini Results

Command:

```bash
handovergap evaluate --compare
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 20 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| hybrid_rag | 20 | 0.26 | 0.59 | 0.26 | 1.00 | 1.00 |
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
| handovergap/conservative | 6 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| handovergap/optimistic | 6 | 0.64 | 1.00 | 0.64 | 1.00 | 1.00 |

## Interpretation

- `naive_rag` returns retrieved memories without checking transferability.
- `hybrid_rag` can identify one explicit risk and blocks only when that risk is high severity.
- `handovergap` checks every slot required by the successor role.
- `handovergap/optimistic` simulates an LLM over-filling ambiguous slots; recall drops because some truly missing slots are treated as filled.

## Important Limitation

These are deterministic results on small synthetic benchmarks. The holdout split and slot-filling stress profiles expose one real limitation, but they are still not a substitute for independent real-world annotation or online production validation.
