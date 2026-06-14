# Prompt: Generate Clarification Questions

Given detected context gaps, generate clarification questions.

Rules:

- Questions should be concrete.
- Questions should be directed to the likely original owner or source person.
- Do not answer the questions.
- Do not assume missing context.

Return JSON:

- gap_type
- question
- target_person_name
- priority
