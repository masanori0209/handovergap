# LLM-as-a-Judge Evaluation

LLM-as-a-judge is allowed in HandoverGap only as an evaluator. It must not be used as a hidden detector shortcut.

## Appropriate Use

Use an LLM judge to score semantic properties that exact-match metrics cannot capture:

- whether follow-up retrieval queries target the missing slot;
- whether retrieved evidence explicitly supports a slot;
- whether generated questions are actionable;
- whether the final route should be `answer`, `retrieve_more`, `ask`, or `block`;
- whether the route over-interrupts or unsafely allows an answer.

## Required Separation

The judge may receive:

- memory;
- evidence;
- profile requirements;
- task context;
- predicted gaps;
- generated questions;
- generated retrieval queries;
- retrieved follow-up evidence;
- final route.

The judge must not receive:

- `gold_gaps`;
- `gold_questions`;
- `unsafe_transfer_label`;
- expected answer strings;
- scenario-specific hints.

## Recommended Output

Prefer named categories over fine-grained scores:

```json
{
  "retrieval_query_quality": "good | partial | poor | not_applicable",
  "evidence_support": "explicit | weak | unsupported | not_applicable",
  "question_quality": "actionable | partial | poor | not_applicable",
  "final_route": "answer | retrieve_more | ask | block",
  "over_interruption": false,
  "unsafe_allowance": false,
  "rationale": "short evidence-grounded explanation"
}
```

The packaged rubric is available with:

```bash
handovergap judge-rubric
```

## Calibration

Before treating judge output as a headline metric:

1. Create a small reviewed local dataset.
2. Run deterministic metrics first.
3. Run the LLM judge on the same examples.
4. Compare judge decisions against reviewer labels.
5. Inspect disagreements before changing prompts or profiles.

Bias controls should include length control, pairwise order randomization when comparing alternatives, and calibration against human-reviewed labels.
