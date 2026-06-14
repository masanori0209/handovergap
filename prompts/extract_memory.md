# Prompt: Extract Memory

You are extracting organizational memories from source events.

Extract only information that can become one of:

- decision
- procedure
- task
- risk
- assumption
- constraint
- communication

Return JSON with:

- subject
- memory_type
- content
- source_person_name
- project_name
- confidence
- evidence_quote

Do not infer missing context.
If information is missing, leave it missing.
