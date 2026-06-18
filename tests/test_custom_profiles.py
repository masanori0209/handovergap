from typer.testing import CliRunner

from handovergap import TransferabilityGate
from handovergap.cli import app
from handovergap.profiles import ProfileCatalog, validate_profile_file


def test_profile_catalog_loads_yaml_profile() -> None:
    catalog = ProfileCatalog.from_yaml("examples/profiles/incident_readiness.yml")

    assert catalog.required_slots("IncidentCommander") == [
        "blast_radius",
        "rollback_owner",
        "customer_message",
    ]
    assert catalog.slot_policy("IncidentCommander", "blast_radius").high_risk is True
    assert catalog.slot_policy("IncidentCommander", "blast_radius").retrieval_hints.preferred_source_types == [
        "incident_note",
        "status_update",
        "monitoring_dashboard",
    ]
    assert "blast radius" in catalog.slot_policy("IncidentCommander", "blast_radius").retrieval_hints.search_terms


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


def test_validate_profile_file_accepts_valid_yaml() -> None:
    result = validate_profile_file("examples/profiles/incident_readiness.yml")

    assert result.is_valid
    assert result.profiles == ["IncidentCommander"]
    assert result.errors == []


def test_profiles_validate_cli_accepts_valid_yaml() -> None:
    result = CliRunner().invoke(app, ["profiles", "validate", "examples/profiles/incident_readiness.yml"])

    assert result.exit_code == 0
    assert "Valid profile file" in result.output
    assert "IncidentCommander" in result.output


def test_profiles_validate_cli_reports_actionable_errors(tmp_path) -> None:
    profile_path = tmp_path / "broken.yml"
    profile_path.write_text(
        """
profiles:
  IncidentCommander:
    required_slots:
      - slot_name: blast_radius
        severity: CRITICAL
      - slot_name: blast_radius
        question: Who owns the blast radius check?
        high_risk: maybe
        retrieval_hints:
          preferred_source_types: incident_note
          search_terms:
            - ""
  EmptyProfile:
    required_slots: []
""".strip()
    )

    result = CliRunner().invoke(app, ["profiles", "validate", str(profile_path)])
    normalized_output = " ".join(result.output.split())

    assert result.exit_code == 1
    assert "Invalid profile file" in normalized_output
    assert "IncidentCommander" in normalized_output
    assert "slot 'blast_radius'" in normalized_output
    assert "missing required key 'question'" in normalized_output
    assert "severity must be one of LOW, MEDIUM, HIGH" in normalized_output
    assert "retrieval_hints.preferred_source_types must be a list" in normalized_output
    assert "retrieval_hints.search_terms[0] must be a non-empty string" in normalized_output
    assert "duplicate slot_name 'blast_radius'" in normalized_output
    assert "EmptyProfile" in normalized_output
    assert "required_slots must be a non-empty list" in normalized_output
