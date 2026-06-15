from __future__ import annotations

import subprocess
import sys
from collections import Counter
from importlib import resources
from time import perf_counter

import typer
from rich.console import Console
from rich.table import Table

from handovergap.audit import TRANSFER_AUDIT_EXPLANATION, transfer_audit_example_rows, transfer_audit_sql
from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBStore

app = typer.Typer(help="Detect tacit context gaps in handover-oriented RAG memories.")
console = Console(width=160)


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
    dataset: str = typer.Option(
        "mini",
        "--dataset",
        help="Built-in dataset: mini, holdout, adversarial, sanitized, or all.",
    ),
    slot_profile: str = typer.Option(
        "provided",
        "--slot-profile",
        help="Slot filling profile: provided, conservative, or optimistic.",
    ),
    stress_filling: bool = typer.Option(
        False,
        "--stress-filling",
        help="Evaluate HandoverGap across provided, conservative, and optimistic slot filling profiles.",
    ),
) -> None:
    """Evaluate on HandoverGapBench mini."""
    if stress_filling:
        rows = []
        for profile in ["provided", "conservative", "optimistic"]:
            evaluator = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset(dataset), slot_profile=profile)
            metrics = evaluator.evaluate_method("handovergap")
            rows.append(metrics.model_copy(update={"method": f"handovergap/{profile}"}))
        title = f"HandoverGapBench {dataset} / slot filling stress"
    else:
        evaluator = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset(dataset), slot_profile=slot_profile)
        rows = evaluator.compare() if compare else [evaluator.evaluate_method("handovergap")]
        title = f"HandoverGapBench {dataset} / slot-profile={slot_profile}"

    table = Table(title=title)
    table.add_column("Method", no_wrap=True)
    table.add_column("Scenarios", justify="right", no_wrap=True)
    table.add_column("Tacit Gap Recall", justify="right", no_wrap=True)
    table.add_column("Unsafe Transfer Prevention", justify="right", no_wrap=True)
    table.add_column("Question Coverage", justify="right", no_wrap=True)
    table.add_column("Safe Transfer Allowance", justify="right", no_wrap=True)
    table.add_column("Blocked Precision", justify="right", no_wrap=True)
    table.add_column("False Clarification Rate", justify="right", no_wrap=True)
    for metrics in rows:
        table.add_row(
            metrics.method,
            str(metrics.scenarios),
            f"{metrics.tacit_gap_recall:.2f}",
            f"{metrics.unsafe_transfer_prevention:.2f}",
            f"{metrics.question_coverage:.2f}",
            f"{metrics.safe_transfer_allowance:.2f}",
            f"{metrics.blocked_precision:.2f}",
            f"{metrics.false_clarification_rate:.2f}",
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


@app.command("audit-sql")
def audit_sql() -> None:
    """Print the TiDB query that explains why transfers were blocked."""
    console.print(f"[bold]Purpose:[/bold] {TRANSFER_AUDIT_EXPLANATION}")
    console.print()
    console.print(transfer_audit_sql())


@app.command("audit-example")
def audit_example() -> None:
    """Show a compact example of blocked-transfer audit query results."""
    table = Table(title="Example TiDB blocked-transfer audit result")
    table.add_column("status", no_wrap=True)
    table.add_column("scenario", no_wrap=True)
    table.add_column("profile", no_wrap=True)
    table.add_column("missing slot", no_wrap=True)
    table.add_column("severity", no_wrap=True)
    table.add_column("checked evidence")
    table.add_column("clarification question")
    for row in transfer_audit_example_rows():
        table.add_row(
            row["transfer_status"],
            row["scenario_id"],
            row["successor_role"],
            row["slot_name"],
            row["severity"],
            row["selected_evidence_title"],
            row["question"],
        )
    console.print(table)


@app.command("audit-benchmark")
def audit_benchmark(
    dataset: str = typer.Option("all", "--dataset", help="Built-in dataset: mini, holdout, adversarial, sanitized, or all."),
    iterations: int = typer.Option(100, "--iterations", min=1, help="Repeated local runs for timing."),
) -> None:
    """Measure local audit-row materialization for the bundled scenarios."""
    store = InMemoryStore.from_builtin_dataset(dataset)
    scenarios = store.list_scenarios()
    detector = HandoverGapDetector(store=store)

    run_durations_ms: list[float] = []
    last_results = []
    for _ in range(iterations):
        start = perf_counter()
        last_results = [detector.detect_scenario(scenario) for scenario in scenarios]
        run_durations_ms.append((perf_counter() - start) * 1000)

    status_counts = Counter(result.transferability_status for result in last_results)
    gap_rows = [gap for result in last_results for gap in result.gaps]
    question_rows = [question for result in last_results for question in result.questions]
    blocked_gap_rows = [
        gap
        for result in last_results
        if result.transferability_status == "blocked"
        for gap in result.gaps
    ]
    slot_counts = Counter(gap.slot_name for gap in blocked_gap_rows)

    table = Table(title=f"Audit materialization benchmark / dataset={dataset}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Scenarios", str(len(scenarios)))
    table.add_row("Iterations", str(iterations))
    table.add_row("Transfer assessments / run", str(len(last_results)))
    table.add_row("Blocked assessments / run", str(status_counts["blocked"]))
    table.add_row("Context gap rows / run", str(len(gap_rows)))
    table.add_row("Blocked context gap rows / run", str(len(blocked_gap_rows)))
    table.add_row("Clarification question rows / run", str(len(question_rows)))
    table.add_row("p50 local materialization ms / run", f"{_percentile(run_durations_ms, 0.50):.3f}")
    table.add_row("p95 local materialization ms / run", f"{_percentile(run_durations_ms, 0.95):.3f}")
    console.print(table)

    slot_table = Table(title="Top missing slots in blocked transfers")
    slot_table.add_column("Slot")
    slot_table.add_column("Rows", justify="right")
    for slot, count in slot_counts.most_common(6):
        slot_table.add_row(slot, str(count))
    console.print(slot_table)


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


def _percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * ratio)))
    return ordered[index]


if __name__ == "__main__":
    app()
