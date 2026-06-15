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

After removing direct label access from predictors and reconciling explicit evidence slots before asking questions:

| Dataset / Mode | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision | False Clarification Rate |
|---|---:|---:|---:|---:|---:|---:|
| mini / handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| holdout / provided | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| holdout / conservative | 1.00 | 1.00 | 1.00 | 0.67 | 0.75 | 0.33 |
| holdout / optimistic | 0.64 | 1.00 | 0.64 | 1.00 | 1.00 | 0.00 |
| adversarial / handovergap | 0.38 | 0.67 | 0.38 | 1.00 | 1.00 | 0.00 |
| sanitized / handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |
| holdout / OpenAI slot fill / gpt-4.1-mini | 0.91 | 0.33 | n/a | 0.67 | 0.50 |
| holdout / OpenAI slot fill / gpt-5-mini | 0.45 | 0.33 | n/a | 0.67 | 0.50 |
| holdout / OpenAI slot fill / gpt-5-mini / gpt5_strict | 1.00 | 0.67 | n/a | 1.00 | 1.00 |

## Interpretation

The mechanism is still useful as a successor-profile-conditioned missing-slot checker, but the mini and holdout splits remain too structurally aligned for production claims.

The adversarial split is the stricter signal: recall stays low at `0.38`, while evidence-backed slot reconciliation reduces false clarification from the earlier `0.67` failure mode to `0.00`. This is a better article claim than pretending the mini benchmark proves production accuracy.

The sanitized split adds field-realistic, anonymized CRM, incident, runbook, release-checklist, and deal-review style notes. It is still synthetic and contains no real company or customer data, but it exercises more realistic handover phrasing than the original mini dataset.

The `gpt-5-mini` live run used 1,901 input tokens and 8,136 output tokens, including 5,184 reasoning tokens, for an estimated cost of `$0.0167` at the observed GPT-5 mini pricing.

The tuned `gpt5_strict` prompt improved `gpt-5-mini` by adding slot-specific acceptance criteria and a policy for treating synthetic evidence summaries as direct support when they explicitly say a required item is documented. This is useful evidence that prompt calibration matters, but it is also closer to the holdout annotation protocol. It should not be treated as independent production accuracy.

The strict prompt still produced an unnecessary clarification in safe scenario `U006` (`timeline_confidence`). False Clarification Rate now makes this visible.

The next useful improvement is not more scenarios with the same `provided_slots` structure. It is a stricter input pipeline:

- derive `provided_slots` from evidence with a calibrated slot-filling model;
- keep `gold_gaps` and `unsafe_transfer_label` evaluation-only;
- tune the block policy without reading labels;
- run the audit query against live TiDB with a larger anonymized workload and record p50/p95 query latency.
