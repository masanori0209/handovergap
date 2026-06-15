from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["CS", "Engineer", "Sales"]


class EvidenceEvent(BaseModel):
    source_type: str
    content: str


class HandoverGap(BaseModel):
    gap_type: str
    slot_name: str
    description: str
    severity: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"


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
    successor_role: Role
    memory_type: Literal["decision", "procedure", "risk", "task"]
    handover_task: str
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
    successor_role: Role
    memory: str
    handover_task: str
    gaps: list[HandoverGap]
    questions: list[ClarificationQuestion]
    transferability_score: float = Field(ge=0.0, le=1.0)
    transferability_status: Literal["transferable", "needs_clarification", "blocked"]


HandoverGapResult = DetectionResult


class EvalMetrics(BaseModel):
    method: str
    scenarios: int
    tacit_gap_recall: float = Field(ge=0.0, le=1.0)
    unsafe_transfer_prevention: float = Field(ge=0.0, le=1.0)
    question_coverage: float = Field(ge=0.0, le=1.0)
    safe_transfer_allowance: float = Field(ge=0.0, le=1.0)
    blocked_precision: float = Field(ge=0.0, le=1.0)
    false_clarification_rate: float = Field(ge=0.0, le=1.0)
