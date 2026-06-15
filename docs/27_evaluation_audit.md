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

A small independent reviewer-style label pass now uses public Slack keyword search only to observe handover-like patterns. Raw Slack messages, channel names, user names, customer names, URLs, IDs, and quoted text are not stored. The anonymized pattern labels are compared with the existing `sanitized` gold gaps:

| Observation count | Exact matches | Mean Jaccard agreement |
|---:|---:|---:|
| 5 | 2 | 0.533 |

The disagreement examples are useful evidence that gold gaps are partly subjective. This weakens the "synthetic labels only" concern without pretending the current labels are production ground truth.

Live TiDB Cloud generated workload validation was expanded beyond the earlier 100-scenario run:

| Scale | Scenarios | Memory chunks | Slot-fill attempts | Context gaps | Questions | Assessments | Audit rows | p50 query | p95 query |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10k chunked | 10,000 | 20,000 | 56,667 | 25,007 | 25,007 | 10,000 | 25,007 | 1374.01 ms | 1478.298 ms |
| 100k audit tables | 100,000 | 0 | 566,667 | 250,004 | 250,004 | 100,000 | 250,004 | 14236.62 ms | 15074.449 ms |

The 100k run skips `memory_chunks` to avoid free-tier storage growth from VECTOR rows. It is evidence that the audit JOIN path scales to larger persisted audit tables, not a general TiDB performance benchmark.

The `gpt-5-mini` live run used 1,901 input tokens and 8,136 output tokens, including 5,184 reasoning tokens, for an estimated cost of `$0.0167` at the observed GPT-5 mini pricing.

The tuned `gpt5_strict` prompt improved `gpt-5-mini` by adding slot-specific acceptance criteria and a policy for treating synthetic evidence summaries as direct support when they explicitly say a required item is documented. This is useful evidence that prompt calibration matters, but it is also closer to the holdout annotation protocol. It should not be treated as independent production accuracy.

The strict prompt still produced an unnecessary clarification in safe scenario `U006` (`timeline_confidence`). False Clarification Rate now makes this visible.

The next useful improvement is not more scenarios with the same `provided_slots` structure. It is a stricter input pipeline:

- derive `provided_slots` from evidence with a calibrated slot-filling model;
- keep `gold_gaps` and `unsafe_transfer_label` evaluation-only;
- tune the block policy without reading labels;
- keep adding independent reviewer labels and disagreement analysis.

## Evaluation Integrity Policy

Future improvements must not maximize scores by hard-coding the benchmark.

Do not:

- read `gold_gaps`, `gold_questions`, or `unsafe_transfer_label` from detector, retriever, slot filler, baseline, or demo code;
- detect a gap by matching scenario ids, expected slot labels, expected answer strings, or the wording of bundled gold annotations;
- tune prompts against the exact gold annotation phrasing and then present the result as independent generalization;
- use structurally aligned mini/holdout scores as production-accuracy evidence.

Do:

- keep gold labels inside evaluator/reporting code only;
- separate slot filling, gap prediction, question generation, and scoring;
- use adversarial/holdout/sanitized splits to expose failure modes;
- report prompt and model variance when an LLM is involved;
- treat improved mini scores as implementation consistency unless supported by independent annotation or rubric-based semantic scoring.

## LLM-as-a-Judge Evaluation

LLM-as-a-judge is acceptable here, but only as an evaluator, not as a hidden detector shortcut.

Recommended use:

1. Give the judge the source evidence, profile requirements, task context, predicted gaps, generated questions, and transfer decision.
2. Do not give the judge gold labels, scenario ids, or expected strings as hints.
3. Ask for structured JSON scores with a written rubric.
4. Score dimensions such as missing-context validity, evidence grounding, question actionability, over-clarification, and transfer readiness.
5. Compare judge scores against gold labels or human annotations only in evaluator/reporting code to calibrate the rubric.

This is closer to common LLM evaluation practice than exact string matching. Exact matching is still useful for narrow schema checks, but it is the wrong primary metric for tacit context gaps because the same missing context can be phrased many ways.
