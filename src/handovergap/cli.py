from __future__ import annotations

import subprocess
import sys
from importlib import resources

import typer
from rich.console import Console
from rich.table import Table

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBStore

app = typer.Typer(help="Detect tacit context gaps in handover-oriented RAG memories.")
console = Console(width=120)


def _build_detector() -> HandoverGapDetector:
    return HandoverGapDetector(store=InMemoryStore.from_builtin_dataset())


def _print_detection(result) -> None:
    console.print("[bold]Memory:[/bold]")
    console.print(result.memory)
    console.print()
    console.print("[bold]Detected Gaps:[/bold]")
    if not result.gaps:
        console.print("No high-risk tacit context gaps detected.")
    for gap in result.gaps:
        console.print(f"[{gap.severity}] {gap.gap_type}")
        console.print(f"  {gap.description}")
    console.print()
    console.print("[bold]Clarification Questions:[/bold]")
    if not result.questions:
        console.print("No clarification questions needed.")
    for index, question in enumerate(result.questions, start=1):
        console.print(f"{index}. {question.question}")
    console.print()
    console.print(f"[bold]Transferability:[/bold] {result.transferability_status}")
    console.print(f"[bold]Score:[/bold] {result.transferability_score:.2f}")


@app.command()
def demo() -> None:
    """Run the built-in valid-but-non-transferable memory demo."""
    result = _build_detector().detect(scenario_id="S001", successor_role="CS")
    _print_detection(result)


@app.command()
def detect(
    scenario: str = typer.Option(..., "--scenario", "-s", help="Built-in scenario id, e.g. S001."),
    role: str = typer.Option(..., "--role", "-r", help="Successor role: CS, Engineer, or Sales."),
) -> None:
    """Detect role-conditioned tacit context gaps for one scenario."""
    result = _build_detector().detect(scenario_id=scenario, successor_role=role)
    _print_detection(result)


@app.command()
def evaluate(
    compare: bool = typer.Option(False, "--compare", help="Compare HandoverGap with naive and hybrid baselines."),
) -> None:
    """Evaluate on HandoverGapBench mini."""
    evaluator = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset())
    rows = evaluator.compare() if compare else [evaluator.evaluate_method("handovergap")]

    table = Table(title="HandoverGapBench mini")
    table.add_column("Method")
    table.add_column("Scenarios", justify="right")
    table.add_column("Tacit Gap Recall", justify="right", no_wrap=True)
    table.add_column("Unsafe Transfer Prevention", justify="right", no_wrap=True)
    table.add_column("Question Coverage", justify="right", no_wrap=True)
    for metrics in rows:
        table.add_row(
            metrics.method,
            str(metrics.scenarios),
            f"{metrics.tacit_gap_recall:.2f}",
            f"{metrics.unsafe_transfer_prevention:.2f}",
            f"{metrics.question_coverage:.2f}",
        )
    console.print(table)


@app.command()
def schema(
    dialect: str = typer.Option("tidb", "--dialect", help="Schema dialect to print. Only 'tidb' is bundled."),
) -> None:
    """Print the optional TiDB schema without requiring a TiDB runtime."""
    if dialect.lower() != "tidb":
        raise typer.BadParameter("Only --dialect tidb is currently supported.")
    console.print(TiDBStore.schema_sql())


@app.command()
def serve(
    port: int = typer.Option(8501, "--port", help="Port for the local Streamlit demo."),
    host: str = typer.Option("127.0.0.1", "--host", help="Host for the local Streamlit demo."),
) -> None:
    """Launch the optional bilingual Streamlit comparison demo."""
    try:
        import streamlit  # noqa: F401
    except ImportError:
        console.print('Streamlit is optional. Install it with: pip install "handovergap[demo]"')
        raise typer.Exit(code=1)

    app_file = resources.files("handovergap").joinpath("demo_app.py")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.address",
        host,
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    ]
    raise typer.Exit(code=subprocess.call(command))


@app.command()
def init(path: str | None = typer.Argument(None, help="Reserved for future sample project creation.")) -> None:
    """Show first-run guidance."""
    target = path or "."
    console.print(f"HandoverGap sample project target: {target}")
    console.print("Try: handovergap demo")
    console.print("Then: handovergap evaluate --compare")


if __name__ == "__main__":
    app()
