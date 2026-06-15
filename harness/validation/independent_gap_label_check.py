from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from handovergap.store import InMemoryStore

DEFAULT_LABELS = "src/handovergap/data/slack_observed_gap_labels.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare independent reviewer-style gap labels with bundled gold gaps.")
    parser.add_argument("--labels", default=DEFAULT_LABELS, help="Anonymized independent label JSON.")
    parser.add_argument("--dataset", default="sanitized", help="Built-in dataset to compare against.")
    parser.add_argument("--output-json", default="article/independent_gap_label_review.json")
    parser.add_argument("--output-md", default="article/independent_gap_label_review.md")
    args = parser.parse_args()

    labels = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    scenarios = {scenario.scenario_id: scenario for scenario in InMemoryStore.from_builtin_dataset(args.dataset).list_scenarios()}

    rows = []
    for observation in labels["observations"]:
        scenario_id = observation["mapped_scenario_id"]
        scenario = scenarios[scenario_id]
        reviewer_slots = set(observation["reviewer_gap_slots"])
        gold_slots = {gap.slot_name for gap in scenario.gold_gaps}
        intersection = sorted(reviewer_slots & gold_slots)
        reviewer_only = sorted(reviewer_slots - gold_slots)
        gold_only = sorted(gold_slots - reviewer_slots)
        union = reviewer_slots | gold_slots
        rows.append(
            {
                "observation_id": observation["observation_id"],
                "scenario_id": scenario_id,
                "profile": scenario.profile,
                "reviewer_gap_slots": sorted(reviewer_slots),
                "gold_gap_slots": sorted(gold_slots),
                "intersection": intersection,
                "reviewer_only": reviewer_only,
                "gold_only": gold_only,
                "jaccard": round(len(intersection) / len(union), 3) if union else 1.0,
                "pattern_summary": observation["pattern_summary"],
                "reviewer_note": observation["reviewer_note"],
            }
        )

    result = {
        "status": "ok",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "dataset": args.dataset,
        "source_method": labels["source_method"],
        "privacy_filters": labels["privacy_filters"],
        "label_protocol": labels["label_protocol"],
        "observation_count": len(rows),
        "mean_jaccard": round(sum(row["jaccard"] for row in rows) / len(rows), 3) if rows else 0.0,
        "exact_match_count": sum(1 for row in rows if not row["reviewer_only"] and not row["gold_only"]),
        "rows": rows,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(_render_markdown(result), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Independent Gap Label Review",
        "",
        f"- Observed at: {datetime.now(timezone.utc).date().isoformat()}",
        f"- Dataset compared: `{result['dataset']}`",
        f"- Observation count: {result['observation_count']}",
        f"- Exact matches: {result['exact_match_count']}",
        f"- Mean Jaccard agreement: `{result['mean_jaccard']}`",
        "",
        "Raw Slack messages are not stored. The review keeps only anonymized pattern summaries and reviewer-style gap labels.",
        "",
        "## Privacy Filters",
        "",
    ]
    for privacy_filter in result["privacy_filters"]:
        lines.append(f"- {privacy_filter}")
    lines.extend(
        [
            "",
            "## Reviewer Labels vs Existing Gold Gaps",
            "",
            "| Observation | Scenario | Profile | Reviewer slots | Gold slots | Reviewer-only | Gold-only | Jaccard |",
            "|---|---|---|---|---|---|---|---:|",
        ]
    )
    for row in result["rows"]:
        lines.append(
            "| {observation_id} | {scenario_id} | {profile} | {reviewer_gap_slots} | {gold_gap_slots} | {reviewer_only} | {gold_only} | {jaccard:.3f} |".format(
                observation_id=row["observation_id"],
                scenario_id=row["scenario_id"],
                profile=row["profile"],
                reviewer_gap_slots=", ".join(row["reviewer_gap_slots"]) or "-",
                gold_gap_slots=", ".join(row["gold_gap_slots"]) or "-",
                reviewer_only=", ".join(row["reviewer_only"]) or "-",
                gold_only=", ".join(row["gold_only"]) or "-",
                jaccard=row["jaccard"],
            )
        )
    lines.extend(["", "## Disagreement Examples", ""])
    for row in [candidate for candidate in result["rows"] if candidate["reviewer_only"] or candidate["gold_only"]][:3]:
        lines.append(f"### {row['observation_id']} / {row['scenario_id']}")
        lines.append("")
        lines.append(row["pattern_summary"])
        lines.append("")
        lines.append(f"- Reviewer-only: {', '.join(row['reviewer_only']) or '-'}")
        lines.append(f"- Gold-only: {', '.join(row['gold_only']) or '-'}")
        lines.append(f"- Note: {row['reviewer_note']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
