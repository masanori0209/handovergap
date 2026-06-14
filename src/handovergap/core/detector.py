from __future__ import annotations

from handovergap.schemas import ClarificationQuestion, DetectionResult, HandoverGap
from handovergap.slot_rules import GAP_TYPE_BY_SLOT, QUESTION_BY_SLOT, ROLE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore


class HandoverGapDetector:
    """Deterministic role-conditioned slot-gap detector for the MVP."""

    def __init__(self, store: InMemoryStore):
        self.store = store

    def detect(self, scenario_id: str, successor_role: str) -> DetectionResult:
        scenario = self.store.get_scenario(scenario_id=scenario_id, successor_role=successor_role)
        return self.detect_scenario(scenario)

    def detect_scenario(self, scenario) -> DetectionResult:
        required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
        missing_slots = [slot for slot in required_slots if slot not in scenario.provided_slots]

        gaps = [
            HandoverGap(
                gap_type=GAP_TYPE_BY_SLOT.get(slot, f"{slot}_gap"),
                slot_name=slot,
                description=_describe_gap(slot),
                severity=_severity_for_slot(slot),
            )
            for slot in missing_slots
        ]
        questions = [
            ClarificationQuestion(slot_name=slot, question=QUESTION_BY_SLOT[slot])
            for slot in missing_slots
            if slot in QUESTION_BY_SLOT
        ]
        transferability_score = max(0.0, 1.0 - (len(missing_slots) / max(len(required_slots), 1)))
        status = "blocked" if scenario.unsafe_transfer_label and missing_slots else "transferable"
        if 0 < transferability_score < 0.75 and status != "blocked":
            status = "needs_clarification"

        return DetectionResult(
            scenario_id=scenario.scenario_id,
            successor_role=scenario.successor_role,
            memory=scenario.memory,
            handover_task=scenario.handover_task,
            gaps=gaps,
            questions=questions,
            transferability_score=transferability_score,
            transferability_status=status,
        )


def _severity_for_slot(slot: str) -> str:
    if slot in {"authority", "communication_status", "fallback_plan", "escalation_path", "contract_impact"}:
        return "HIGH"
    return "MEDIUM"


def _describe_gap(slot: str) -> str:
    descriptions = {
        "scope": "引き継ぎ先が適用範囲を判断するための情報が不足しています",
        "communication_status": "関係者または顧客に説明済みか不明です",
        "authority": "後任が回答または判断してよい範囲が不明です",
        "fallback_plan": "想定外の場合の代替手段が不明です",
        "escalation_path": "問題発生時の相談先またはエスカレーション先が不明です",
        "customer_facing_wording": "外部向けに使ってよい説明文が不明です",
        "rationale": "なぜその判断になったかが不明です",
        "technical_constraint": "技術的制約または前提条件が不明です",
        "implementation_scope": "実装対象と対象外の境界が不明です",
        "trigger_for_reconsideration": "再検討が必要になる条件が不明です",
        "related_issue": "関連するチケットや追跡先が不明です",
        "failure_modes": "失敗パターンと観測方法が不明です",
        "contract_impact": "契約や商談への影響が不明です",
        "promise_boundary": "顧客に約束してよい範囲が不明です",
        "customer_expectation": "顧客期待値が調整済みか不明です",
        "timeline_confidence": "提示できる時期の確度が不明です",
        "negotiation_status": "交渉状況と未合意点が不明です",
    }
    return descriptions.get(slot, f"{slot} が不足しています")
