# Slot Schema Design

## Memory Types

### decision

Required base slots:

- decision_content
- scope
- rationale
- effective_period
- authority
- trigger_for_reconsideration
- communication_status
- fallback_plan

### procedure

Required base slots:

- steps
- preconditions
- owner
- required_tools
- exception_handling
- escalation_path
- failure_modes

### risk

Required base slots:

- risk_condition
- impact
- mitigation
- monitor_signal
- owner
- escalation_threshold

### task

Required base slots:

- task_content
- assignee
- deadline
- completion_condition
- dependency
- escalation_path

## Role Requirements

### CS

CS needs:

- communication_status
- scope
- authority
- fallback_plan
- escalation_path
- customer-facing wording

### Engineer

Engineer needs:

- rationale
- technical_constraint
- implementation_scope
- trigger_for_reconsideration
- related_issue
- failure_modes

### Sales

Sales needs:

- contract_impact
- promise_boundary
- customer_expectation
- timeline_confidence
- negotiation_status

## Example

Memory:

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

For CS:

Missing likely slots:

- scope
- communication_status
- authority
- fallback_plan

For Engineer:

Missing likely slots:

- rationale
- implementation_scope
- trigger_for_reconsideration
- related_issue

For Sales:

Missing likely slots:

- contract_impact
- promise_boundary
- timeline_confidence
