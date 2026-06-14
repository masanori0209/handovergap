# Evaluation Audit

Date: 2026-06-15

## Finding

The earlier evaluation overstated HandoverGap's unsafe-transfer prevention.

Two label leaks were found and removed:

- `HandoverGapDetector.detect_scenario()` used `unsafe_transfer_label` to decide `blocked`.
- `HybridRAGBaseline` used `gold_gaps[0]` to decide its detected slot and block status.

The bundled datasets are also structurally aligned with the deterministic detector:

- `HandoverGapBench mini`: `required_slots - provided_slots == gold_gaps` for 20/20 scenarios.
- `HandoverGapBench holdout`: `required_slots - provided_slots == gold_gaps` for 6/6 scenarios.

This means `Tacit Gap Recall = 1.00` is best interpreted as an implementation consistency check, not independent evidence of production detection quality.

## Post-Fix Results

After removing direct label access from predictors:

| Dataset / Mode | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|
| mini / handovergap | 1.00 | 0.65 | 1.00 | 1.00 | 1.00 |
| holdout / provided | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 |
| holdout / conservative | 1.00 | 0.67 | 1.00 | 0.67 | 0.67 |
| holdout / optimistic | 0.64 | 0.67 | 0.64 | 1.00 | 1.00 |
| holdout / OpenAI slot fill / gpt-4.1-mini | 0.91 | 0.33 | n/a | 0.67 | 0.50 |

## Interpretation

The mechanism is still useful as a role-conditioned missing-slot checker, but the previous `1.00` unsafe-transfer claim depended on evaluation leakage.

The next useful improvement is not more scenarios with the same `provided_slots` structure. It is a stricter input pipeline:

- derive `provided_slots` from evidence with a calibrated slot-filling model;
- keep `gold_gaps` and `unsafe_transfer_label` evaluation-only;
- tune the block policy without reading labels;
- add adversarial safe cases where some slots are ambiguous but transfer should not be blocked.
