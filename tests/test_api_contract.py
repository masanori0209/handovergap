from __future__ import annotations

import inspect
from typing import get_args

from handovergap import ContextReadinessGate, TransferabilityGate, map_evidence_slots_by_keywords
from handovergap.schemas import DetectionResult


def test_transferability_gate_check_signature_is_stable() -> None:
    signature = inspect.signature(TransferabilityGate.check)

    assert list(signature.parameters) == [
        "self",
        "memory",
        "profile",
        "task_context",
        "evidence",
        "provided_slots",
        "evidence_slots",
        "scenario_id",
        "memory_type",
    ]
    assert signature.parameters["memory"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["profile"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["task_context"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["scenario_id"].default == "inline"
    assert signature.parameters["memory_type"].default == "task"


def test_detection_result_contract_fields_are_stable() -> None:
    assert set(DetectionResult.model_fields) == {
        "scenario_id",
        "profile",
        "memory",
        "task_context",
        "gaps",
        "questions",
        "transferability_score",
        "transferability_status",
    }

    status_annotation = DetectionResult.model_fields["transferability_status"].annotation
    assert set(get_args(status_annotation)) == {"transferable", "needs_clarification", "blocked"}


def test_transferability_gate_contract_output_shape() -> None:
    result = TransferabilityGate().check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        evidence=["CSV workaround approved for the release."],
        provided_slots=["scope"],
        evidence_slots=["scope"],
    )

    payload = result.model_dump()
    assert payload["scenario_id"] == "inline"
    assert payload["profile"] == "CS"
    assert payload["memory"].startswith("Use CSV")
    assert payload["task_context"] == "Answer customer questions about the workaround."
    assert payload["transferability_status"] in {"transferable", "needs_clarification", "blocked"}
    assert isinstance(payload["transferability_score"], float)
    assert isinstance(payload["gaps"], list)
    assert isinstance(payload["questions"], list)


def test_context_readiness_gate_alias_is_stable() -> None:
    assert ContextReadinessGate is TransferabilityGate


def test_evidence_slot_mapping_helper_is_public() -> None:
    assert callable(map_evidence_slots_by_keywords)
