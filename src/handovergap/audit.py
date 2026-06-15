from __future__ import annotations

from typing import TypedDict


class AuditExampleRow(TypedDict):
    transfer_status: str
    scenario_id: str
    successor_role: str
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
  ta.successor_role,
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
 AND cg.successor_role = ta.successor_role
 AND cg.status = 'open'
LEFT JOIN slot_fill_attempts sfa
  ON sfa.memory_item_id = cg.memory_item_id
 AND sfa.successor_role = cg.successor_role
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


def transfer_audit_example_rows() -> list[AuditExampleRow]:
    """Return a compact example of what the TiDB audit query explains."""
    return [
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "successor_role": "CS",
            "slot_name": "communication_status",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Slack: CSV fallback agreement",
            "question": "顧客にはAPI延期を説明済みですか？",
        },
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "successor_role": "CS",
            "slot_name": "authority",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Issue: API integration postponed",
            "question": "次フェーズ時期を顧客向けに回答してよい範囲はどこまでですか？",
        },
        {
            "transfer_status": "blocked",
            "scenario_id": "S001",
            "successor_role": "CS",
            "slot_name": "fallback_plan",
            "severity": "HIGH",
            "slot_fill_status": "missing",
            "selected_evidence_title": "Issue: CSV import workaround",
            "question": "CSV対応が失敗した場合の代替手段は何ですか？",
        },
    ]
