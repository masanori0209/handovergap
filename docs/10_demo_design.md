# Demo Design

## Goal

Show the difference between:

- Naive RAG
- Hybrid RAG
- HandoverGap RAG

## Recommended Demo

Streamlit app.

## Screens

### 1. Scenario Selector

Inputs:

- scenario
- profile
- task context
- method

Example:

```text
Scenario: S001
Memory: A社は今回だけCSVで対応し、APIは次フェーズ
Profile: CS
Task context: 顧客問い合わせ対応
```

### 2. Retrieved Memory

Shows original memory and evidence.

### 3. Slot Filling View

Table:

| Slot | Status | Evidence | Confidence |
|---|---|---|---|
| scope | missing | - | 0.00 |
| rationale | filled | Issue #42 | 0.72 |
| communication_status | missing | - | 0.00 |
| authority | missing | - | 0.00 |
| fallback_plan | missing | - | 0.00 |

### 4. Detected Gaps

Shows:

- scope_gap
- communication_gap
- authority_gap
- fallback_gap

### 5. Clarification Questions

Shows generated questions.

### 6. Method Comparison

| Method | Output |
|---|---|
| Naive RAG | Answers directly |
| Hybrid RAG | Adds related evidence |
| HandoverGap RAG | Blocks unsafe transfer and asks questions |

## Demo Message

The demo should clearly show:

> Naive RAG answers, HandoverGap RAG hesitates.

That hesitation is the feature.
