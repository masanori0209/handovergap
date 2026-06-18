# Evaluation Metrics

## Tacit Gap Recall

How many gold gaps were detected.

```text
TGR = detected_gold_gaps / total_gold_gaps
```

## Unsafe Transfer Prevention

How often unsafe memories were prevented from being treated as safe.

```text
UTP = blocked_unsafe_transfers / total_unsafe_transfer_cases
```

## Clarification Question Coverage

How many gold questions or their semantic equivalents were generated.

```text
CQC = covered_gold_questions / total_gold_questions
```

## Follow-up Retrieval Metrics

These metrics evaluate `retrieval_mode="expand_before_ask"`. They are not model-quality scores; they measure whether an additional bounded retrieval round improves the route before asking a user.

By default they use `safety_policy="strict"`. Strict mode requires high-risk profile slots to be explicitly supported by `evidence_slots` before the final route can answer. This makes `unsafe_answer_rate` the primary guardrail metric when a follow-up retrieval pass adds evidence. Use `--safety-policy balanced` to inspect the tradeoff when caller-provided slots are trusted after local review.

### Retrieve More Success Rate

How often follow-up evidence reduces the number of missing slots after an initial `retrieve_more` recommendation.

```text
retrieve_more_success_rate = cases_with_fewer_gaps_after_followup / retrieve_more_cases
```

### Ask Reduction Rate

How often the second pass reduces user-facing clarification questions among cases that would initially interrupt.

```text
ask_reduction_rate = cases_with_fewer_questions_after_followup / initially_interrupted_cases
```

### Unsafe Answer Rate

How often the final route allows an answer for an unsafe-transfer case. Lower is better.

```text
unsafe_answer_rate = unsafe_cases_finally_answered / unsafe_transfer_cases
```

### Extra Retrieval Cost

Average number of generated follow-up retrieval queries per scenario.

```text
extra_retrieval_cost = generated_followup_queries / scenarios
```

### Final Route Accuracy

Whether the final route matches the reviewed safe/unsafe label after follow-up evidence is applied.

```text
final_route_accuracy = correct_final_routes / scenarios
```

For bundled datasets, follow-up retrieval is simulated by first withholding `evidence_slots`, then adding them back for the second pass. For user datasets, the same metric is only as strong as the reviewed `evidence_slots`.

Example:

```bash
handovergap evaluate --dataset adversarial --retrieval-mode expand-before-ask
handovergap evaluate --dataset adversarial --retrieval-mode expand-before-ask --safety-policy balanced
```

On the packaged adversarial split, strict mode is expected to lower unsafe answers by refusing to answer when high-risk slots are filled only by optimistic `provided_slots`.

## Profile-Conditioned Gap Accuracy

Whether the method detects different gaps for different profiles.

Example:

Same memory:

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

CS should detect:

- communication_gap
- authority_gap
- fallback_gap

Engineer should detect:

- rationale_gap
- trigger_gap
- implementation_scope_gap

## Baseline Methods

### naive_rag

Returns the memory as answer.

Expected:

- low gap recall
- low unsafe transfer prevention

### hybrid_rag

Returns memory plus relevant evidence.

Expected:

- better grounding
- still weak at tacit gap detection

### handovergap

Performs profile-conditioned slot filling and gap detection.

Expected:

- higher gap recall
- higher unsafe transfer prevention

## Reporting Table

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Allowance | Blocked Precision | False Clarification |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx |
| hybrid_rag | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx |
| handovergap | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx | 0.xx |

Follow-up retrieval metrics are reported separately because they evaluate a two-pass retrieval plan rather than a single detector prediction.
