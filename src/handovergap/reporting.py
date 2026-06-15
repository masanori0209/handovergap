from __future__ import annotations

from datetime import datetime, timezone

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.question_quality import evaluate_question_quality
from handovergap.store import InMemoryStore

REPORT_DATASETS = ["mini", "holdout", "adversarial", "sanitized"]


def generate_evaluation_report(dataset: str = "all") -> str:
    datasets = REPORT_DATASETS if dataset == "all" else [dataset]
    lines = [
        "# HandoverGap Evaluation Report",
        "",
        f"Generated at: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "This report is generated from bundled fictional/synthetic datasets. It is a reproducibility artifact, not a production accuracy claim.",
        "",
        "## Metrics",
        "",
        "| Dataset | Method | Scenarios | TGR | UTP | Question Coverage | Safe Allowance | Blocked Precision | False Clarification |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    quality_rows = [
        "",
        "## Question Quality",
        "",
        "| Dataset | Questions | Slot Coverage | Actionability | Redundancy Rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for dataset_name in datasets:
        store = InMemoryStore.from_builtin_dataset(dataset_name)
        evaluator = HandoverGapEvaluator(store=store)
        for metrics in evaluator.compare():
            lines.append(
                f"| {dataset_name} | {metrics.method} | {metrics.scenarios} | "
                f"{metrics.tacit_gap_recall:.2f} | {metrics.unsafe_transfer_prevention:.2f} | "
                f"{metrics.question_coverage:.2f} | {metrics.safe_transfer_allowance:.2f} | "
                f"{metrics.blocked_precision:.2f} | {metrics.false_clarification_rate:.2f} |"
            )
        detector = HandoverGapDetector(store=store)
        predicted_questions = []
        required_gap_slots = set()
        for scenario in store.list_scenarios():
            result = detector.detect_scenario(scenario)
            predicted_questions.extend(result.questions)
            required_gap_slots.update(gap.slot_name for gap in result.gaps)
        quality = evaluate_question_quality(predicted_questions, required_gap_slots)
        quality_rows.append(
            f"| {dataset_name} | {quality.questions} | {quality.slot_coverage:.2f} | "
            f"{quality.actionability:.2f} | {quality.redundancy_rate:.2f} |"
        )
    lines.extend(quality_rows)
    lines.extend(
        [
            "",
            "## Evaluation Integrity",
            "",
            "- Predictors must not read `gold_gaps`, `gold_questions`, or `unsafe_transfer_label`.",
            "- No scenario-specific or expected-string matching should be used to improve benchmark scores.",
            "- Mini and holdout scores are consistency checks when required slots and labels are structurally aligned.",
            "- Adversarial and sanitized splits are stronger signals for failure analysis, but still synthetic.",
            "",
            "## Reproduce",
            "",
            "```bash",
            f"handovergap report --dataset {dataset}",
            "handovergap evaluate --compare",
            "pytest",
            "```",
        ]
    )
    return "\n".join(lines) + "\n"
