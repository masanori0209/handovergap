PROFILE_REQUIRED_SLOTS = {
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
    "authority": "このプロファイルが回答または判断してよい範囲はどこまでですか？",
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

RETRIEVAL_HINTS_BY_SLOT = {
    "scope": {
        "preferred_source_types": ["decision_note", "requirements_doc", "project_brief"],
        "search_terms": ["scope", "applies to", "out of scope", "対象範囲", "適用範囲"],
    },
    "communication_status": {
        "preferred_source_types": ["customer_update", "support_note", "announcement", "crm_note"],
        "search_terms": ["notified", "sent", "customer update", "告知済み", "説明済み"],
    },
    "authority": {
        "preferred_source_types": ["policy", "approval_note", "support_playbook", "decision_log"],
        "search_terms": ["approved", "can answer", "must not promise", "権限", "承認"],
    },
    "fallback_plan": {
        "preferred_source_types": ["runbook", "incident_note", "support_playbook", "escalation_doc"],
        "search_terms": ["fallback", "workaround", "rollback", "manual recovery", "代替手段"],
    },
    "escalation_path": {
        "preferred_source_types": ["runbook", "escalation_doc", "incident_note", "oncall_note"],
        "search_terms": ["escalate", "owner", "support lead", "on-call", "エスカレーション"],
    },
    "customer_facing_wording": {
        "preferred_source_types": ["customer_update", "faq", "support_macro", "approved_wording"],
        "search_terms": ["approved wording", "customer-facing", "FAQ", "外部向け", "文面"],
    },
    "rationale": {
        "preferred_source_types": ["decision_log", "design_doc", "architecture_note"],
        "search_terms": ["because", "rationale", "tradeoff", "decision", "理由"],
    },
    "technical_constraint": {
        "preferred_source_types": ["design_doc", "architecture_note", "incident_note", "runbook"],
        "search_terms": ["constraint", "limitation", "dependency", "前提条件", "制約"],
    },
    "implementation_scope": {
        "preferred_source_types": ["ticket", "design_doc", "release_plan", "pull_request"],
        "search_terms": ["implementation scope", "included", "excluded", "実装対象", "対象外"],
    },
    "trigger_for_reconsideration": {
        "preferred_source_types": ["decision_log", "runbook", "monitoring_note", "experiment_plan"],
        "search_terms": ["reconsider", "trigger", "threshold", "再検討", "条件"],
    },
    "related_issue": {
        "preferred_source_types": ["ticket", "issue", "pull_request", "incident_note"],
        "search_terms": ["issue", "ticket", "PR", "tracking", "チケット"],
    },
    "failure_modes": {
        "preferred_source_types": ["runbook", "incident_note", "test_plan", "postmortem"],
        "search_terms": ["failure mode", "risk", "monitoring", "失敗パターン", "検知"],
    },
    "contract_impact": {
        "preferred_source_types": ["crm_note", "deal_review", "legal_review", "contract_doc"],
        "search_terms": ["contract impact", "renewal", "exception terms", "legal approval", "契約影響"],
    },
    "promise_boundary": {
        "preferred_source_types": ["deal_review", "legal_review", "customer_update", "crm_note"],
        "search_terms": ["promise", "commitment", "must not promise", "約束", "合意範囲"],
    },
    "customer_expectation": {
        "preferred_source_types": ["crm_note", "customer_update", "meeting_note", "support_note"],
        "search_terms": ["expectation", "aligned", "customer understands", "期待値", "調整済み"],
    },
    "timeline_confidence": {
        "preferred_source_types": ["roadmap", "release_plan", "deal_review", "status_update"],
        "search_terms": ["timeline", "ETA", "confidence", "時期", "確度"],
    },
    "negotiation_status": {
        "preferred_source_types": ["crm_note", "deal_review", "meeting_note", "renewal_note"],
        "search_terms": ["negotiation", "open point", "agreed", "交渉状況", "未合意"],
    },
}
