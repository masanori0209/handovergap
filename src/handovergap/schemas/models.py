from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Profile = str


class EvidenceEvent(BaseModel):
    source_type: str
    content: str
    title: str | None = None
    source_url: str | None = None
    actor_name: str | None = None
    project_name: str | None = None
    occurred_at: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class RetrievalHints(BaseModel):
    preferred_source_types: list[str] = Field(default_factory=list)
    search_terms: list[str] = Field(default_factory=list)


class HandoverGap(BaseModel):
    gap_type: str
    slot_name: str
    description: str
    severity: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    retrieval_hints: RetrievalHints = Field(default_factory=RetrievalHints)


class GoldQuestion(BaseModel):
    slot_name: str
    question: str


class ClarificationQuestion(BaseModel):
    slot_name: str
    question: str


class HandoverScenario(BaseModel):
    scenario_id: str
    memory: str
    evidence_events: list[EvidenceEvent] = Field(default_factory=list)
    profile: Profile
    memory_type: Literal["decision", "procedure", "risk", "task"]
    task_context: str
    provided_slots: list[str] = Field(default_factory=list)
    evidence_slots: list[str] = Field(default_factory=list)
    slot_fill_profiles: dict[str, list[str]] = Field(default_factory=dict)
    annotator_gap_slots: dict[str, list[str]] = Field(default_factory=dict)
    annotation_notes: str | None = None
    gold_gaps: list[HandoverGap] = Field(default_factory=list)
    gold_questions: list[GoldQuestion] = Field(default_factory=list)
    unsafe_transfer_label: bool


class DetectionResult(BaseModel):
    scenario_id: str
    profile: Profile
    memory: str
    task_context: str
    required_slots: list[str] = Field(default_factory=list)
    provided_slots: list[str] = Field(default_factory=list)
    evidence_slots: list[str] = Field(default_factory=list)
    high_risk_slots: list[str] = Field(default_factory=list)
    gaps: list[HandoverGap]
    questions: list[ClarificationQuestion]
    transferability_score: float = Field(ge=0.0, le=1.0)
    transferability_status: Literal["transferable", "needs_clarification", "blocked"]


HandoverGapResult = DetectionResult


class EvalMetrics(BaseModel):
    method: str
    scenarios: int
    slot_fill_mode: Literal["user_provided", "deterministic_rules", "optional_llm"] = "user_provided"
    slot_fill_source: str = "scenario.provided_slots"
    model_name: str | None = None
    prompt_profile: str | None = None
    tacit_gap_recall: float = Field(ge=0.0, le=1.0)
    unsafe_transfer_prevention: float = Field(ge=0.0, le=1.0)
    question_coverage: float = Field(ge=0.0, le=1.0)
    safe_transfer_allowance: float = Field(ge=0.0, le=1.0)
    blocked_precision: float = Field(ge=0.0, le=1.0)
    false_clarification_rate: float = Field(ge=0.0, le=1.0)


class FollowupRetrievalMetrics(BaseModel):
    method: str = "handovergap/followup_retrieval"
    scenarios: int
    safety_policy: Literal["strict", "balanced", "exploratory"] = "strict"
    retrieve_more_cases: int
    retrieve_more_success_rate: float = Field(ge=0.0, le=1.0)
    ask_reduction_rate: float = Field(ge=0.0, le=1.0)
    unsafe_answer_rate: float = Field(ge=0.0, le=1.0)
    extra_retrieval_cost: float = Field(ge=0.0)
    final_route_accuracy: float = Field(ge=0.0, le=1.0)
