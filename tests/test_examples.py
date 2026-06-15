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
    assert "clarification questions" in result.stdout


def test_llamaindex_gate_example_runs() -> None:
    result = subprocess.run(
        [sys.executable, "examples/llamaindex_gate.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "final synthesizer" in result.stdout
