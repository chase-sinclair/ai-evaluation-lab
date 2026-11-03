import json
from pathlib import Path
from typing import Annotated

import typer

from eval_lab.analysis.summary import summarize as aggregate
from eval_lab.core.registry import discover, load
from eval_lab.core.result_store import read_records, run_path
from eval_lab.core.runner import run as execute
from eval_lab.core.runner import validate as validate_experiment

app = typer.Typer(no_args_is_help=True, help="Offline-first reproducible evaluation lab.")
Root = Annotated[Path, typer.Option(help="Directory containing trusted experiment modules.")]
Results = Annotated[Path, typer.Option(help="Run storage directory.")]


def emit(value):
    typer.echo(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False))


@app.command("list")
def list_experiments(experiments: Root = Path("experiments")):
    """List available local experiments."""
    for name in discover(experiments):
        typer.echo(name)


@app.command()
def validate(name: str, experiments: Root = Path("experiments")):
    """Validate config, cases, schemas, grader version, and controlled treatments."""
    try:
        experiment = load(name, experiments)
        cases, trials = validate_experiment(experiment)
        if len(trials) > experiment.spec.max_requests:
            raise ValueError("Planned trials exceed max_requests")
        emit({"valid": True, "cases": len(cases), "trials": len(trials)})
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def run(
    name: str,
    experiments: Root = Path("experiments"),
    results: Results = Path("results"),
    mode: Annotated[str, typer.Option(help="mock (default) or live")] = "mock",
    dry_run: Annotated[
        bool, typer.Option(help="Validate and estimate; zero provider calls.")
    ] = False,
    live: Annotated[
        bool, typer.Option(help="Explicit opt-in; needs approved live config.")
    ] = False,
):
    """Execute a bounded run, offline unless explicitly configured and opted in."""
    try:
        outcome = execute(
            load(name, experiments), results=results, mode=mode, dry_run=dry_run, live=live
        )
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    emit(outcome)
    if outcome.get("run_status") in {
        "failed",
        "interrupted",
        "budget_stopped",
        "completed_with_errors",
    }:
        raise typer.Exit(1)


@app.command()
def summarize(run_id: str, results: Results = Path("results")):
    """Recompute outcomes from durable records, including partial runs; never overwrite."""
    try:
        path = run_path(results, run_id)
        records, warnings = read_records(path)
        if (path / "manifest.json").exists():
            manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        else:
            manifest = json.loads((path / "plan.json").read_text(encoding="utf-8"))["manifest"]
            warnings.append("No final manifest: run is active or was interrupted")
        summary = aggregate(records, manifest["planned_trials"])
        summary.update(
            {
                "run_id": run_id,
                "run_status": manifest["status"],
                "mode": manifest["mode"],
                "warnings": warnings,
            }
        )
        emit(summary)
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc
