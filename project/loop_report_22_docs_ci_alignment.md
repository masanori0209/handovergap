# Loop 22: Docs and CI Alignment

Date: 2026-06-15

## Plan

Improve demo clarity and PyPI first-run confidence by aligning documentation, demo labels, CLI examples, and CI coverage with the product-generalized `profile` / `task_context` surface.

Winning filter:

- Article claim: HandoverGap is a profile-conditioned readiness gate, not a hard-coded handover-only classifier.
- Evaluation metric: question/gap outputs should not depend on old "successor role" wording.
- PyPI first-run experience: CI should run the same commands a first-time user sees.
- Demo clarity: labels should avoid implying that the library only works by business department.

## Act

- Updated Japanese README, article outlines, key phrases, demo design notes, and product roadmap wording from successor-role phrasing to `profile` / `task_context`.
- Replaced old API examples using `result.blocked` and `audit_id` with the current `transferability_status` and `questions` surface.
- Generalized built-in authority question and gap descriptions from "successor" wording to "this profile" wording.
- Updated Streamlit demo labels from handover-specific department names to "Support response", "Engineering operations", and "Deal review".
- Expanded CI beyond unit tests to run detect, evaluate, hybrid retrieval, JSONL ingest, report generation, workload benchmark, and RAG framework examples.

## Observe

The only remaining old successor/handover wording found by search is either:

- raw OpenAI observation JSON, which should remain immutable evidence, or
- intentional article framing about handover as the first use case.

## Validate

- `ruff check .`
- `pytest`
- `handovergap demo`
- `handovergap detect --scenario S001 --profile CS`
- `handovergap evaluate --compare`
- `handovergap retrieve-evidence --scenario S001 --profile CS --slot communication_status --mode hybrid`

## Reflect

This loop reduces the risk that reviewers interpret HandoverGap as a department-specific demo instead of a reusable readiness gate. It also makes CI protect the newer contest evidence: TiDB-style hybrid retrieval, report reproducibility, JSONL ingest, and framework examples.

## Update Context

Use `profile` and `task_context` consistently for new docs and examples. Handover remains the primary contest story, but the implementation should be described as checking whether a retrieved memory is safe for a specific profile and task context.

## Handoff

Remaining high-value work is live TiDB latency/evidence screenshots and optional issue closure after pushing this batch.
