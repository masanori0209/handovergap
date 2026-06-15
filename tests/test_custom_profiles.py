from typer.testing import CliRunner

from handovergap import TransferabilityGate
from handovergap.cli import app
from handovergap.profiles import ProfileCatalog


def test_profile_catalog_loads_yaml_profile() -> None:
    catalog = ProfileCatalog.from_yaml("examples/profiles/incident_readiness.yml")

    assert catalog.required_slots("IncidentCommander") == [
        "blast_radius",
        "rollback_owner",
        "customer_message",
    ]
    assert catalog.slot_policy("IncidentCommander", "blast_radius").high_risk is True


def test_transferability_gate_uses_custom_yaml_profile() -> None:
    gate = TransferabilityGate.from_profile_file("examples/profiles/incident_readiness.yml")

    result = gate.check(
        memory="The checkout incident is mitigated by disabling the new queue worker.",
        profile="IncidentCommander",
        task_context="Decide whether to declare customer-facing mitigation complete.",
        evidence=["The new queue worker was disabled."],
        provided_slots=["rollback_owner"],
    )

    assert result.transferability_status == "blocked"
    assert {gap.slot_name for gap in result.gaps} == {"blast_radius", "customer_message"}
    assert {question.slot_name for question in result.questions} == {"blast_radius", "customer_message"}


def test_detect_cli_accepts_profile_file() -> None:
    result = CliRunner().invoke(
        app,
        [
            "detect",
            "--scenario",
            "S001",
            "--profile",
            "IncidentCommander",
            "--profile-file",
            "examples/profiles/incident_readiness.yml",
        ],
    )

    assert result.exit_code == 0
    assert "blast_radius_gap" in result.output
