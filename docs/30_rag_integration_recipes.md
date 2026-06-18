# RAG Integration Recipes

HandoverGap sits after retrieval and before answer or action generation.

The core integration contract is:

1. Retrieve candidate memory and supporting evidence with your existing RAG stack.
2. Decide which required slots are explicit in the memory as `provided_slots`.
3. Decide which required slots are supported by evidence as `evidence_slots`.
4. Run `TransferabilityGate.check(...)`.
5. Convert the result with `route_transferability_result(...)`.
6. If `route.action == "retrieve_more"`, run bounded follow-up retrieval and check again.
7. Only call the final generator when `route.action == "answer"`.

The core runtime does not require OpenAI, TiDB, LangChain, or LlamaIndex.

## Framework-Neutral

Run:

```bash
python examples/end_to_end_integration.py
```

This is the first practical path to copy. It simulates a retriever, maps evidence
to slots, checks the gate, and returns `answer` / `ask` / `block` routing.

```python
from handovergap import (
    TransferabilityGate,
    map_evidence_slots_by_keywords,
    route_transferability_result,
)

memory = retriever.search_memory(user_question)
evidence = retriever.search_evidence(user_question)
evidence_slots = map_evidence_slots_by_keywords(evidence, slot_keywords)

result = TransferabilityGate().check(
    memory=memory.text,
    profile="CS",
    task_context="Answer a customer question without overpromising.",
    evidence=evidence,
    provided_slots=memory.slots,
    evidence_slots=evidence_slots,
)
route = route_transferability_result(
    result,
    safe_context=memory.text,
    retrieval_mode="expand_before_ask",
    safety_policy="strict",
)

if route.action == "retrieve_more":
    extra_evidence = []
    for query in route.retrieval_queries:
        extra_evidence.extend(retriever.search_evidence(query.query, top_k=3))
    extra_slots = map_evidence_slots_by_keywords(extra_evidence, slot_keywords)
    result = TransferabilityGate().check(
        memory=memory.text,
        profile="CS",
        task_context="Answer a customer question without overpromising.",
        evidence=[*evidence, *extra_evidence],
        provided_slots=memory.slots,
        evidence_slots=[*evidence_slots, *extra_slots],
    )
    route = route_transferability_result(result, safe_context=memory.text, safety_policy="strict")

if route.action != "answer":
    return {
        "status": route.status,
        "action": route.action,
        "reason": route.reason,
        "questions": route.questions,
    }

return llm.answer(user_question, context=route.safe_context)
```

Keep follow-up retrieval bounded. A practical default is one follow-up round, at most three generated queries, and explicit evidence support before adding `evidence_slots`.

The default `strict` safety policy requires high-risk profile slots to be present in `evidence_slots` before answering. If your application intentionally trusts reviewed caller-provided slots, pass `safety_policy="balanced"` and track `unsafe_answer_rate` before enforcing it in production.

## LangChain

Run:

```bash
python examples/langchain_gate.py
```

Use this pattern after `retriever.invoke(query)` and before the final answer chain:

```python
docs = retriever.invoke(query)
evidence = [
    {"source_type": "langchain_document", "content": doc.page_content, "metadata": doc.metadata}
    for doc in docs
]
evidence_slots = map_evidence_slots_by_keywords(evidence, slot_keywords)

result = gate.check(
    memory=retrieved_memory.text,
    profile="CS",
    task_context="Answer customer questions about the workaround.",
    evidence=evidence,
    provided_slots=retrieved_memory.slots,
    evidence_slots=evidence_slots,
)
route = route_transferability_result(result, safe_context=retrieved_memory.text)

if route.action != "answer":
    return {"questions": route.questions, "status": route.status}
```

## LlamaIndex

Run:

```bash
python examples/llamaindex_gate.py
```

Use this pattern after `retriever.retrieve(query)` and before the final synthesizer:

```python
nodes = retriever.retrieve(query)
evidence = [
    {"source_type": "llamaindex_node", "content": node.get_content(), "metadata": node.metadata}
    for node in nodes
]
evidence_slots = map_evidence_slots_by_keywords(evidence, slot_keywords)

result = gate.check(
    memory=retrieved_memory.text,
    profile="CS",
    task_context="Answer customer questions about the workaround.",
    evidence=evidence,
    provided_slots=retrieved_memory.slots,
    evidence_slots=evidence_slots,
)
route = route_transferability_result(result, safe_context=retrieved_memory.text)

if route.action != "answer":
    return {"questions": route.questions, "status": route.status}
```

## Optional Extensions

- Replace deterministic keyword mapping with OpenAI or another LLM slot filling step.
- Persist `DetectionResult` and `ProductRoute` to TiDB for audit.
- Use a custom profile file when `CS`, `Engineer`, or `Sales` do not match your workflow.
