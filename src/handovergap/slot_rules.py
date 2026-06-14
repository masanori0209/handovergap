ROLE_REQUIRED_SLOTS = {
    "CS": [
        "communication_status",
        "scope",
        "authority",
        "fallback_plan",
        "escalation_path",
        "customer_facing_wording",
    ],
    "Engineer": [
        "rationale",
        "technical_constraint",
        "implementation_scope",
        "trigger_for_reconsideration",
        "related_issue",
        "failure_modes",
    ],
    "Sales": [
        "contract_impact",
        "promise_boundary",
        "customer_expectation",
        "timeline_confidence",
        "negotiation_status",
    ],
}

HIGH_RISK_SLOTS = {
    "authority",
    "communication_status",
    "fallback_plan",
    "escalation_path",
    "contract_impact",
}

GAP_TYPE_BY_SLOT = {
    "scope": "scope_gap",
    "communication_status": "communication_gap",
    "authority": "authority_gap",
    "fallback_plan": "fallback_gap",
    "escalation_path": "escalation_gap",
    "customer_facing_wording": "wording_gap",
    "rationale": "rationale_gap",
    "technical_constraint": "technical_constraint_gap",
    "implementation_scope": "implementation_scope_gap",
    "trigger_for_reconsideration": "trigger_gap",
    "related_issue": "traceability_gap",
    "failure_modes": "failure_mode_gap",
    "contract_impact": "contract_gap",
    "promise_boundary": "promise_boundary_gap",
    "customer_expectation": "expectation_gap",
    "timeline_confidence": "timeline_gap",
    "negotiation_status": "negotiation_gap",
}

QUESTION_BY_SLOT = {
    "scope": "この判断の適用範囲はどこまでですか？",
    "communication_status": "関係者または顧客には説明済みですか？",
    "authority": "後任が回答または判断してよい範囲はどこまでですか？",
    "fallback_plan": "想定外の場合の代替手段は何ですか？",
    "escalation_path": "問題が起きた場合のエスカレーション先は誰ですか？",
    "customer_facing_wording": "外部向けにはどの表現で説明すべきですか？",
    "rationale": "この判断に至った理由は何ですか？",
    "technical_constraint": "技術的な制約や前提条件は何ですか？",
    "implementation_scope": "実装対象と対象外の境界はどこですか？",
    "trigger_for_reconsideration": "どの条件になったら再検討しますか？",
    "related_issue": "関連するチケットや追跡先はどこですか？",
    "failure_modes": "想定される失敗パターンと検知方法は何ですか？",
    "contract_impact": "契約や商談への影響はありますか？",
    "promise_boundary": "顧客に約束してよい範囲はどこまでですか？",
    "customer_expectation": "顧客の期待値はどの状態に調整されていますか？",
    "timeline_confidence": "提示できる時期の確度はどの程度ですか？",
    "negotiation_status": "交渉状況と未合意点は何ですか？",
}
