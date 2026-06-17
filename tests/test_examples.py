import subprocess
import sys


def test_langchain_gate_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/langchain_gate.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "route=blocked action=block" in result.stdout
    assert "clarification questions" in result.stdout


def test_llamaindex_gate_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/llamaindex_gate.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "route=blocked action=block" in result.stdout
    assert "final synthesizer" in result.stdout


def test_evidence_to_slot_mapping_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/evidence_to_slot_mapping.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "without_evidence_slots=blocked" in result.stdout
    assert "with_evidence_slots=transferable" in result.stdout


def test_product_routing_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/product_routing.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "support: action=block status=blocked" in result.stdout
    assert "incident: action=ask status=needs_clarification" in result.stdout
    assert "agent: action=answer status=transferable" in result.stdout


def test_end_to_end_integration_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/end_to_end_integration.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "== first retrieval ==" in result.stdout
    assert "status=blocked action=block" in result.stdout
    assert "gaps=fallback_plan,escalation_path" in result.stdout
    assert "== after retrieving runbook evidence ==" in result.stdout
    assert "status=transferable action=answer" in result.stdout
    assert "safe_context=available" in result.stdout
