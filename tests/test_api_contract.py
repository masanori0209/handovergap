from __future__ import annotations

import inspect
from typing import get_args

from handovergap import (
    ContextReadinessGate,
    ProductRoute,
    ProfileValidationResult,
    RetrievalHints,
    TransferabilityGate,
    map_evidence_slots_by_keywords,
    route_transferability_result,
    validate_profile_file,
)
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
        "required_slots",
        "provided_slots",
        "evidence_slots",
        "high_risk_slots",
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
    assert isinstance(payload["required_slots"], list)
    assert isinstance(payload["provided_slots"], list)
    assert isinstance(payload["evidence_slots"], list)
    assert isinstance(payload["high_risk_slots"], list)
    assert isinstance(payload["gaps"], list)
    assert isinstance(payload["questions"], list)
    assert "retrieval_hints" in payload["gaps"][0]


def test_context_readiness_gate_alias_is_stable() -> None:
    assert ContextReadinessGate is TransferabilityGate


def test_evidence_slot_mapping_helper_is_public() -> None:
    assert callable(map_evidence_slots_by_keywords)


def test_retrieval_hints_model_is_public() -> None:
    hints = RetrievalHints(preferred_source_types=["runbook"], search_terms=["fallback"])

    assert hints.preferred_source_types == ["runbook"]
    assert hints.search_terms == ["fallback"]


def test_product_routing_helper_is_public() -> None:
    assert callable(route_transferability_result)
    assert set(ProductRoute.model_fields) == {
        "status",
        "action",
        "recommended_action",
        "deployment_mode",
        "retrieval_mode",
        "safety_policy",
        "enforcement",
        "should_interrupt",
        "next_step",
        "reason",
        "questions",
        "retrieval_queries",
        "safe_context",
    }


def test_profile_validation_helper_is_public() -> None:
    assert callable(validate_profile_file)
    assert set(ProfileValidationResult.model_fields) == {"path", "profiles", "errors"}
