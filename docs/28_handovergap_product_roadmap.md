# HandoverGap Product Roadmap

## Product Thesis

Correct memories are not always transferable.

HandoverGap should be a reusable readiness gate for RAG and agent systems. It checks whether a retrieved memory can be safely used by a selected profile in a selected task context. If not, it returns missing context gaps and clarification questions instead of encouraging the application to answer from incomplete context.

The library should be useful beyond handover workflows. Handover remains the clearest example, but the product contract is broader:

- define a `profile`
- define profile-required `slots`
- map retrieved memory and evidence to supported slots
- run the gate before answer or action generation
- route `transferable`, `needs_clarification`, and `blocked`
- optionally persist the decision path for audit

## v1.0.0 Goal

Make HandoverGap practical for teams that already have RAG or agent memory systems.

v1 should prove that a developer can install the package, define a custom profile, connect retrieved evidence, run the gate, and decide whether to answer, ask, or block without requiring OpenAI or TiDB.

Optional OpenAI and TiDB paths should remain valuable, but they must not be required for the core runtime.

## Primary Users

### RAG Application Developer

They have a retriever and answer generator. They need a pre-answer gate that turns missing operational context into structured questions.

Success means they can copy an integration pattern, map their retrieved data into the API, and handle the result in their product.

### AI Agent Developer

They have agent memories and tool actions. They need a guard before the agent reuses memory for an action that depends on role, authority, scope, or fallback context.

Success means the gate returns a clear route: proceed, ask, or block.

### Operations / Support Team

They need to define role-specific readiness checks for support replies, incident handoff, account renewal, runbook execution, or customer messaging.

Success means they can maintain YAML profiles and review generated questions without changing library code.

## v1 Product Requirements

### 1. Stable Public API

The public API should make the gate contract boring and reliable.

Stable inputs:

- `memory`
- `profile`
- `task_context`
- `evidence`
- `provided_slots`
- `evidence_slots`
- `scenario_id`
- `memory_type`

Stable outputs:

- `transferability_status`
- `transferability_score`
- `gaps`
- `questions`
- `scenario_id`
- `profile`
- `memory`
- `task_context`

The API should work without external services by default.

### 2. Evidence-To-Slot Mapping Contract

Real integrations start with retrieved snippets, documents, issues, CRM notes, or agent memories. The docs and examples must explain how those become slot support.

The contract should distinguish:

- `provided_slots`: context already explicit in the memory itself
- `evidence_slots`: context supported by retrieved evidence
- optional semantic slot filling: model-assisted extraction from evidence

This is the most important bridge between a demo and a usable library.

### 3. Product Routing Semantics

Applications need recommended behavior for each status.

| Status | Recommended Product Behavior |
| --- | --- |
| `transferable` | Continue to answer or action generation. |
| `needs_clarification` | Ask the returned questions before finalizing the answer. |
| `blocked` | Withhold the answer/action and show gaps plus required questions to the responsible user. |

The response shape should be easy to wrap in an API:

```python
{
    "status": result.transferability_status,
    "reason": [gap.description for gap in result.gaps],
    "questions": [question.question for question in result.questions],
}
```

### 4. Custom Profile Validation

Custom profiles are the path from a handover example to a general library.

v1 should include a validation command for profile YAML:

```bash
handovergap profiles validate examples/profiles/incident_readiness.yml
```

Validation should catch:

- missing profile names
- empty `required_slots`
- duplicate slots
- invalid severity values
- missing questions for high-risk slots
- malformed YAML

### 5. End-To-End Integration Example

The project needs one complete, runnable example that feels like a real first adoption path.

The example should show:

1. fictional source events
2. a retrieved memory
3. evidence snippets
4. slot support mapping
5. `TransferabilityGate.check()`
6. product response routing
7. returned gaps and questions

It should not require OpenAI or TiDB.

### 6. Evaluation Workflow For User Data

Bundled datasets should remain reproducibility fixtures, not production-accuracy claims.

v1 should provide a workflow for users to evaluate their own anonymized data:

```text
export or prepare anonymized records
→ annotate expected missing context
→ run HandoverGap
→ report metrics and examples
→ inspect disagreements
```

Reports should clearly label:

- bundled synthetic fixtures
- anonymized user-provided evaluation
- model-dependent LLM slot filling runs
- deterministic runs

### 7. Optional Audit Store

TiDB is useful when users need durable auditability:

- source events
- memory chunks
- slot fill attempts
- context gaps
- clarification questions
- transfer assessments

The core library must keep working without TiDB. The TiDB path should be documented as an optional audit store for teams that need to explain why an answer or action was withheld.

### 8. Security And Privacy Defaults

v1 should make the safe default obvious:

- no OpenAI call unless explicitly configured
- no TiDB write unless explicitly configured
- no bundled real company data
- no employee scoring workflows
- no secret values in reports or logs

## Current Priority Order

The v1 tracker is the source of truth for implementation order:

1. Stabilize the public API contract.
2. Define evidence-to-slot mapping for real integrations.
3. Define answer / ask / block routing semantics.
4. Add one complete runnable integration example.
5. Add custom profile validation.
6. Expand integration recipes.
7. Clarify deterministic, user-provided, and optional LLM slot filling modes.
8. Add user-dataset annotation and evaluation workflow.
9. Stabilize the optional TiDB audit store lifecycle.
10. Split GitHub Pages into task-oriented library documentation.
11. Improve actionable errors.
12. Formalize security, privacy, and versioning.

## Non-Goals For v1

- require OpenAI at runtime
- require TiDB at runtime
- bundle real company data
- build a full web application
- support employee scoring or surveillance workflows
- claim production accuracy from bundled synthetic fixtures

## Definition Of Done

HandoverGap is v1-ready when a new user can:

1. install the package
2. define a custom profile
3. validate that profile
4. map retrieved memory and evidence into slot support
5. run the gate
6. route answer / ask / block
7. review gaps and questions
8. optionally persist the audit path
9. evaluate behavior on their own anonymized data

The core value should be clear without reading project history: HandoverGap helps applications avoid using correct-but-not-ready context.
