from __future__ import annotations

from collections import defaultdict
from typing import Any, TypedDict


class AuditExampleRow(TypedDict):
    transfer_status: str
    scenario_id: str
    profile: str
    slot_name: str
    severity: str
    slot_fill_status: str
    selected_evidence_title: str
    question: str


TRANSFER_AUDIT_SQL = """\
SELECT
  ta.id AS assessment_id,
  ta.status AS transfer_status,
  ta.transferability_score,
  ta.unsafe_reason,
  mi.scenario_id,
  mi.subject,
  mi.memory_type,
  ta.profile,
  cg.gap_type,
  cg.slot_name,
  cg.severity,
  cg.description AS gap_description,
  sfa.status AS slot_fill_status,
  sfa.confidence AS slot_fill_confidence,
  sfa.fill_result,
  sfa.retrieved_event_ids,
  se.title AS selected_evidence_title,
  se.source_url AS selected_evidence_url,
  cq.question,
  cq.priority AS question_priority
FROM transfer_assessments ta
JOIN memory_items mi
  ON mi.id = ta.memory_item_id
LEFT JOIN context_gaps cg
  ON cg.memory_item_id = ta.memory_item_id
 AND cg.profile = ta.profile
 AND cg.status = 'open'
LEFT JOIN slot_fill_attempts sfa
  ON sfa.memory_item_id = cg.memory_item_id
 AND sfa.profile = cg.profile
 AND sfa.slot_name = cg.slot_name
LEFT JOIN source_events se
  ON se.id = sfa.selected_event_id
LEFT JOIN clarification_questions cq
  ON cq.context_gap_id = cg.id
WHERE ta.status = 'blocked'
ORDER BY ta.created_at DESC, cg.severity DESC, cg.slot_name;
"""

TRANSFER_AUDIT_EXPLANATION = (
    "Trace blocked transfer assessments to the memory, missing profile-required slots, "
    "slot-fill evidence, and clarification questions. This is the concrete TiDB audit path "
    "behind the HandoverGap claim: correct memories may still be unsafe to transfer."
)


def transfer_audit_sql() -> str:
    return TRANSFER_AUDIT_SQL


def diverse_audit_sample_rows(rows: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    """Pick audit rows that show one blocked scenario fanning out across slots."""
    if not rows or limit <= 0:
        return []

    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

    def sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
        return (
            severity_rank.get(str(row.get("severity", "")), 9),
            str(row.get("slot_name", "")),
            str(row.get("scenario_id", "")),
        )

    by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_scenario[str(row.get("scenario_id", ""))].append(row)

    anchor_scenario = max(by_scenario, key=lambda scenario_id: len(by_scenario[scenario_id]))
    anchor_rows = sorted(by_scenario[anchor_scenario], key=sort_key)
    sample = anchor_rows[: min(max(limit - 2, 1), len(anchor_rows))]

    seen_profiles = {str(row.get("profile", "")) for row in sample}
    for row in sorted(rows, key=sort_key):
        if len(sample) >= limit:
            break
        profile = str(row.get("profile", ""))
        if profile in seen_profiles:
            continue
        sample.append(row)
        seen_profiles.add(profile)

    if len(sample) < limit:
        seen_keys = {
            (str(row.get("scenario_id", "")), str(row.get("slot_name", "")))
            for row in sample
        }
        for row in sorted(rows, key=sort_key):
            if len(sample) >= limit:
                break
            key = (str(row.get("scenario_id", "")), str(row.get("slot_name", "")))
            if key in seen_keys:
                continue
            sample.append(row)
            seen_keys.add(key)

    return sample[:limit]


def transfer_audit_example_rows() -> list[AuditExampleRow]:
    """Return a compact example of what the TiDB audit query explains."""
    return [
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "profile": "CS",
            "slot_name": "communication_status",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Slack: CSV fallback agreement",
            "question": "顧客にはAPI延期を説明済みですか？",
        },
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "profile": "CS",
            "slot_name": "authority",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Issue: API integration postponed",
            "question": "次フェーズ時期を顧客向けに回答してよい範囲はどこまでですか？",
        },
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "profile": "CS",
            "slot_name": "fallback_plan",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Issue: CSV import workaround",
            "question": "CSV対応が失敗した場合の代替手段は何ですか？",
        },
    ]
