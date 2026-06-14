# Prompt: Fill Slot

Given a memory item, a slot definition, and retrieved evidence, determine whether the slot can be filled.

Return JSON:

- slot_name
- status: filled | weak | missing
- slot_value
- confidence
- evidence_quote
- reason

Do not invent context.
If the evidence does not support the slot, mark it missing.
