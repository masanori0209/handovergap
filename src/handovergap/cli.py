from __future__ import annotations

import subprocess
import sys
from collections import Counter
from importlib import resources
from pathlib import Path
from time import perf_counter

import typer
from rich.console import Console
from rich.table import Table

from handovergap import __version__
from handovergap.audit import TRANSFER_AUDIT_EXPLANATION, transfer_audit_example_rows, transfer_audit_sql
from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.ingest import scenario_from_jsonl
from handovergap.profiles import ProfileCatalog, validate_profile_file
from handovergap.reporting import generate_evaluation_report
from handovergap.retrieval import (
    retrieve_slot_evidence_full_text_local,
    retrieve_slot_evidence_hybrid_local,
    retrieve_slot_evidence_local,
)
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBStore
from handovergap.workload import benchmark_generated_workload

app = typer.Typer(help="Detect profile-conditioned context gaps in RAG memories.")
profiles_app = typer.Typer(help="Inspect and validate custom profile files.")
app.add_typer(profiles_app, name="profiles")
console = Console(width=160)


def _version_callback(value: bool) -> None:
    if value:
        console.print(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the installed handovergap version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Detect profile-conditioned context gaps in RAG memories."""


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
    result = _build_detector().detect(scenario_id="S001", profile="CS")
    _print_detection(result)


@app.command()
def detect(
    scenario: str = typer.Option(..., "--scenario", "-s", help="Built-in scenario id, e.g. S001."),
    profile: str = typer.Option(..., "--profile", "-p", help="Profile preset: CS, Engineer, or Sales."),
    profile_file: str | None = typer.Option(None, "--profile-file", help="YAML file with custom profile requirements."),
) -> None:
    """Detect profile-conditioned tacit context gaps for one scenario."""
    store = InMemoryStore.from_builtin_dataset()
    profiles = ProfileCatalog.from_yaml(profile_file) if profile_file else ProfileCatalog.builtins()
    if profile_file:
        scenario_input = store.get_scenario_by_id(scenario).model_copy(update={"profile": profile})
        result = HandoverGapDetector(store=InMemoryStore([scenario_input]), profiles=profiles).detect_scenario(scenario_input)
    else:
        result = HandoverGapDetector(store=store, profiles=profiles).detect(scenario_id=scenario, profile=profile)
    _print_detection(result)


@profiles_app.command("validate")
def validate_profiles(
    path: str = typer.Argument(..., help="YAML file with custom profile requirements."),
) -> None:
    """Validate a custom profile YAML file before using it."""
    result = validate_profile_file(path)
    if result.is_valid:
        console.print(f"Valid profile file: {result.path}")
        console.print(f"Profiles: {', '.join(result.profiles)}")
        return

    console.print(f"Invalid profile file: {result.path}")
    for error in result.errors:
        console.print(f"- {error}")
    raise typer.Exit(code=1)


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
def report(
    dataset: str = typer.Option("all", "--dataset", help="Dataset: mini, holdout, adversarial, sanitized, or all."),
    output: str | None = typer.Option(None, "--output", "-o", help="Write markdown report to this path."),
) -> None:
    """Generate a reproducible markdown evaluation report."""
    markdown = generate_evaluation_report(dataset)
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown)
        console.print(f"Wrote evaluation report: {output_path}")
    else:
        console.print(markdown)


@app.command()
def ingest(
    path: str = typer.Argument(..., help="JSONL source-event file."),
    memory: str = typer.Option(..., "--memory", help="Retrieved memory text to check."),
    profile: str = typer.Option(..., "--profile", "-p", help="Profile preset or custom profile name."),
    task_context: str = typer.Option(..., "--task-context", help="Task context for the readiness check."),
    scenario: str = typer.Option("jsonl", "--scenario", "-s", help="Scenario id for the in-memory check."),
    profile_file: str | None = typer.Option(None, "--profile-file", help="YAML file with custom profile requirements."),
) -> None:
    """Load JSONL source events and run a profile-conditioned readiness check."""
    profiles = ProfileCatalog.from_yaml(profile_file) if profile_file else ProfileCatalog.builtins()
    scenario_input = scenario_from_jsonl(
        path,
        scenario_id=scenario,
        memory=memory,
        profile=profile,
        task_context=task_context,
    )
    result = HandoverGapDetector(store=InMemoryStore([scenario_input]), profiles=profiles).detect_scenario(scenario_input)
    console.print(f"Loaded source events: {len(scenario_input.evidence_events)}")
    _print_detection(result)


@app.command("retrieve-evidence")
def retrieve_evidence(
    scenario: str = typer.Option(..., "--scenario", "-s", help="Built-in scenario id, e.g. S001."),
    profile: str = typer.Option(..., "--profile", "-p", help="Profile preset or custom profile name."),
    slot: str = typer.Option(..., "--slot", help="Required slot to retrieve evidence for."),
    top_k: int = typer.Option(3, "--top-k", min=1, help="Number of evidence chunks to return."),
    mode: str = typer.Option("hybrid", "--mode", help="Retrieval mode: vector, fulltext, or hybrid."),
) -> None:
    """Retrieve slot-level evidence chunks with deterministic local retrieval."""
    store = InMemoryStore.from_builtin_dataset()
    scenario_input = store.get_scenario(scenario, profile)
    if mode == "vector":
        chunks = retrieve_slot_evidence_local(scenario_input, slot, top_k=top_k)
    elif mode == "fulltext":
        chunks = retrieve_slot_evidence_full_text_local(scenario_input, slot, top_k=top_k)
    elif mode == "hybrid":
        chunks = retrieve_slot_evidence_hybrid_local(scenario_input, slot, top_k=top_k)
    else:
        raise typer.BadParameter("mode must be one of: vector, fulltext, hybrid")

    table = Table(title=f"Slot evidence / mode={mode} / scenario={scenario} / profile={profile} / slot={slot}")
    table.add_column("rank", justify="right")
    table.add_column("chunk_id", no_wrap=True)
    table.add_column("source", no_wrap=True)
    table.add_column("distance", justify="right", no_wrap=True)
    table.add_column("content")
    for index, chunk in enumerate(chunks, start=1):
        table.add_row(
            str(index),
            chunk.chunk_id,
            chunk.source_type or "",
            f"{chunk.distance:.4f}",
            chunk.content,
        )
    console.print(table)
    console.print(f"retrieved_event_ids={[chunk.source_event_id for chunk in chunks if chunk.source_event_id is not None]}")


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
            row["profile"],
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


@app.command("workload-benchmark")
def workload_benchmark(
    scenarios: int = typer.Option(1000, "--scenarios", min=1, help="Generated scenario count."),
    iterations: int = typer.Option(5, "--iterations", min=1, help="Repeated local runs for timing."),
) -> None:
    """Benchmark generated workload materialization without requiring live TiDB."""
    result = benchmark_generated_workload(count=scenarios, iterations=iterations)
    table = Table(title="Generated workload benchmark")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for key, value in result.model_dump().items():
        if key.endswith("_ms"):
            table.add_row(key, f"{value:.3f}")
        else:
            table.add_row(key, str(value))
    console.print(table)
    console.print("This is a generated local workload sizing check, not a TiDB latency claim.")


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
