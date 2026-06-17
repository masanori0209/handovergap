import pytest

from handovergap import ContextReadinessGate, TransferabilityGate
from handovergap.schemas import EvidenceEvent


def test_transferability_gate_checks_inline_memory() -> None:
    gate = TransferabilityGate()

    result = gate.check(
        memory="Use CSV for this release; API support is deferred.",
        profile="CS",
        task_context="Answer customer questions about the workaround.",
        evidence=["CSV workaround approved for the release."],
        provided_slots=["scope"],
        evidence_slots=["scope"],
    )

    assert result.scenario_id == "inline"
    assert result.profile == "CS"
    assert result.task_context == "Answer customer questions about the workaround."
    assert result.transferability_status == "blocked"
    assert {gap.slot_name for gap in result.gaps} >= {"communication_status", "authority"}


def test_context_readiness_gate_alias_and_structured_evidence() -> None:
    gate = ContextReadinessGate()

    result = gate.check(
        memory="The nightly job can be rerun manually.",
        profile="Engineer",
        task_context="Recover a failed nightly job.",
        evidence=[EvidenceEvent(source_type="runbook", content="Manual rerun is documented.")],
        provided_slots=["failure_modes"],
        evidence_slots=["failure_modes"],
    )

    assert result.profile == "Engineer"
    assert result.gaps


def test_transferability_gate_checks_builtin_dataset() -> None:
    gate = TransferabilityGate.from_builtin_dataset()

    result = gate.check_builtin("S001", profile="CS")

    assert result.transferability_status == "blocked"


def test_transferability_gate_reports_malformed_evidence_without_leaking_payload() -> None:
    gate = TransferabilityGate()

    with pytest.raises(ValueError) as exc_info:
        gate.check(
            memory="Use CSV for this release; API support is deferred.",
            profile="CS",
            task_context="Answer customer questions about the workaround.",
            evidence=[{"source_type": "crm_note", "content": "secret-token-123"}, {"source_type": "issue"}],
            provided_slots=["scope"],
        )

    message = str(exc_info.value)
    assert "Invalid evidence item at index 2" in message
    assert "source_type" in message
    assert "content" in message
    assert "secret-token-123" not in message
