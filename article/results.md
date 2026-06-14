# HandoverGapBench mini Results

Command:

```bash
handovergap evaluate --compare
```

Observed on June 14, 2026:

| Method | Scenarios | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage |
|---|---:|---:|---:|---:|
| naive_rag | 20 | 0.00 | 0.00 | 0.00 |
| hybrid_rag | 20 | 0.26 | 0.59 | 0.26 |
| handovergap | 20 | 1.00 | 1.00 | 1.00 |

## Interpretation

- `naive_rag` returns retrieved memories without checking transferability.
- `hybrid_rag` can identify one explicit risk and blocks only when that risk is high severity.
- `handovergap` checks every slot required by the successor role.

## Important Limitation

These are deterministic results on a small synthetic benchmark. The dataset and rule-based detector were designed together, so the `1.00` values are implementation checks, not evidence of production accuracy or generalization.
