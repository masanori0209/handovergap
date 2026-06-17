# Competitor Battlecard

## Long-term Memory Store

Their claim:

> We implemented long-term memory for agents using TiDB.

HandoverGap position:

> Long-term memory stores help agents remember. HandoverGap evaluates whether those memories are safely transferable to another person or role.

```text
Memory Store:
  Can the agent remember?

HandoverGap:
  Can a successor safely act on that memory?
```

## RAG Freshness / Quality

Their claim:

> We measured RAG freshness or retrieval quality.

HandoverGap position:

> Freshness and faithfulness are necessary but insufficient. A memory can be fresh and faithful but still non-transferable.

```text
Freshness:
  Is the memory up to date?

Faithfulness:
  Is the answer grounded?

Transferability:
  Does the successor have enough context to act safely?
```

## Auditable AI Memory

Their claim:

> We built an auditable memory architecture with lineage and approval history.

HandoverGap position:

> Auditability explains where a memory came from. HandoverGap asks whether the memory has enough role-specific operational context for handover.

```text
Auditability:
  Where did this memory come from?

HandoverGap:
  What context is still missing before someone else can use it?
```

## Memory Security / Poisoning

Their claim:

> We protect agent memory from malicious or contaminated inputs.

HandoverGap position:

> Memory security protects what enters memory. HandoverGap protects what gets transferred out of memory into action.

```text
Memory Guard:
  Should this memory be stored?

HandoverGap:
  Should this memory be acted on by this successor?
```

## Battle-tested One-liner

> Existing RAG systems optimize whether information can be found. HandoverGap evaluates whether the found information can be safely handed over.
