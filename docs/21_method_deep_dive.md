# Method Deep Dive

## Method Name

HandoverGap RAG

## Design Principle

Naive RAG should answer.  
HandoverGap RAG should hesitate when critical context is missing.

The hesitation is the feature.

## Step 1: Memory Type Classification

Classify memory into:

- decision
- procedure
- task
- risk
- assumption
- communication
- constraint

MVP can use rule-based classification.

## Step 2: Required Slot Loading

Base decision slots:

- decision_content
- scope
- rationale
- effective_period
- authority
- trigger_for_reconsideration
- communication_status
- fallback_plan

## Step 3: Role-conditioned Requirements

For CS:

- communication_status
- scope
- authority
- fallback_plan
- customer-facing wording

For Engineer:

- rationale
- implementation_scope
- technical_constraint
- trigger_for_reconsideration
- related_issue

For Sales:

- contract_impact
- promise_boundary
- timeline_confidence
- customer_expectation

## Step 4: Slot-level Evidence Retrieval

Do not retrieve once for the whole answer.

Retrieve per slot.

Example:

```text
Slot: communication_status
Query terms:
- 顧客に説明済み
- 合意済み
- API延期
- CSV暫定
```

## Step 5: Slot Filling

Each slot becomes:

```text
filled | weak | missing
```

## Step 6: Gap Detection

Map weak/missing critical slots to gap types.

```text
communication_status missing
→ communication_gap
```

## Step 7: Clarification Question Generation

Generate questions from gaps.

Do not answer missing context.

## Step 8: Transferability Assessment

Statuses:

- transferable
- needs_clarification
- unsafe_to_transfer

## Traceability

Every result should be explainable:

```text
Gap
→ Missing slot
→ Required by role
→ Evidence searched
→ Evidence found/not found
→ Question generated
```
