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

## Role-conditioned Gap Accuracy

Whether the method detects different gaps for different successor roles.

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

Performs role-conditioned slot filling and gap detection.

Expected:

- higher gap recall
- higher unsafe transfer prevention

## Reporting Table

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage |
|---|---:|---:|---:|
| naive_rag | 0.xx | 0.xx | 0.xx |
| hybrid_rag | 0.xx | 0.xx | 0.xx |
| handovergap | 0.xx | 0.xx | 0.xx |
