"""Domain-agnostic sequential execution with durable per-trial records."""

import hashlib
import importlib.metadata
import platform
import random
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from eval_lab.analysis.summary import summarize
from eval_lab.contracts import ModelResponse, RunManifest, RunRecord
from eval_lab.core.budgets import cost_details, estimate_cost, estimate_input_tokens, preflight
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.registry import Experiment
from eval_lab.core.result_store import ResultStore
from eval_lab.providers.mock import MockProvider


def now() -> str:
    return datetime.now(UTC).isoformat()


def validate(experiment: Experiment):
    spec = experiment.spec
    if any(c.options for c in spec.conditions):
        raise ValueError("Current providers support no optional inference settings")
    cases = experiment.load_cases()
    if not cases or len({c.id for c in cases}) != len(cases):
        raise ValueError("Cases must be nonempty and IDs unique")
    if any(
        c.dataset_id != spec.dataset.id or c.dataset_version != spec.dataset.version for c in cases
    ):
        raise ValueError("Case dataset IDs/versions must match config")
    experiment.validate(cases)
    trials = []
    for case in cases:
        for condition in spec.conditions:
            for repeat in range(spec.repetitions):
                request = experiment.build_request(case, condition)
                if request.model != condition.model or request.options != condition.options:
                    raise ValueError("Request must preserve configured model/options")
                if request.max_output_tokens != spec.max_output_tokens:
                    raise ValueError("Request must preserve the output limit")
                trials.append((case, condition, repeat, request))
    random.Random(spec.seed).shuffle(trials)
    return cases, trials


def git_state(directory: Path):
    try:

        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(directory), *args],
                stderr=subprocess.DEVNULL,
                timeout=5,
                text=True,
            ).strip()

        return git("rev-parse", "HEAD"), bool(git("status", "--porcelain"))
    except (OSError, subprocess.SubprocessError):
        return None, None


def source_hashes(experiment: Experiment):
    files = list(experiment.directory.rglob("*.py"))
    files += list(experiment.directory.glob("*.yaml"))
    engine = Path(__file__).resolve().parents[1]
    files += list(engine.rglob("*.py"))
    root = experiment.directory.parent.parent
    files += [p for p in (root / "uv.lock", root / "pyproject.toml") if p.exists()]
    return {
        str(p.relative_to(root) if p.is_relative_to(root) else p): hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
        for p in sorted(files)
    }


def run(
    experiment: Experiment,
    *,
    results: Path,
    mode: str = "mock",
    dry_run: bool = False,
    live: bool = False,
    run_id: str | None = None,
    provider_factory=None,
    trial_order: list[tuple[str, str, int]] | None = None,
) -> dict:
    cases, trials = validate(experiment)
    if trial_order is not None:
        indexed = {
            (c.id, condition.id, repeat): (c, condition, repeat, request)
            for c, condition, repeat, request in trials
        }
        if len(trial_order) != len(indexed) or set(trial_order) != set(indexed):
            raise ValueError("Explicit trial order must be an exact permutation of planned trials")
        trials = [indexed[key] for key in trial_order]
    spec = experiment.spec
    requests = [t[3] for t in trials]
    projected = preflight(spec, requests, mode, live)
    preflight_report = {
        "dry_run": dry_run,
        "planned_trials": len(trials),
        "mode": mode,
        "projected_cost_usd": projected,
        "estimated_input_tokens": sum(estimate_input_tokens(r) for r in requests),
        "output_token_ceiling": len(trials) * spec.max_output_tokens,
        "provider_calls": 0,
    }
    if dry_run:
        return preflight_report
    run_id = run_id or f"{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:12]}"
    revision, dirty = git_state(experiment.directory)
    packages = ("ai-evaluation-lab", "pydantic", "typer", "PyYAML", "jsonschema")
    environment = {"python": sys.version, "platform": platform.platform()}
    for package in (*packages, "openai"):
        try:
            environment[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            environment[package] = "not installed"
    manifest = RunManifest(
        run_id=run_id,
        experiment=spec,
        mode=mode,
        config_hash=digest(spec),
        dataset_hash=digest([c.model_dump() for c in cases]),
        source_hashes=source_hashes(experiment),
        git_revision=revision,
        git_dirty=dirty,
        pricing_version=spec.pricing.version if mode == "live" else "offline-zero-cost-v1",
        prompt_hashes=[digest(r.messages) for r in requests],
        request_hashes=[digest(r) for r in requests],
        environment=environment,
        started_at=now(),
        planned_trials=len(trials),
        projected_cost_usd=projected,
        warnings=["Mock outcomes are software tests, not research evidence."]
        if mode == "mock"
        else ["Estimated costs and budget cap are best-effort, not a billing guarantee."],
    )
    store = ResultStore(results, run_id)
    store.write(
        "plan.json",
        {
            "manifest": manifest.model_dump(mode="json"),
            "trials": [
                {
                    "case": c.model_dump(),
                    "condition_id": condition.id,
                    "repeat": repeat,
                    "request": request.model_dump(),
                }
                for c, condition, repeat, request in trials
            ],
        },
    )
    records, spent, status, error = [], 0.0, "completed", None
    try:
        if provider_factory is not None:
            provider = provider_factory()
        elif mode == "mock":
            provider = MockProvider(spec.seed)
        else:
            from eval_lab.providers.openai_adapter import OpenAIProvider

            provider = OpenAIProvider(live=live)
        for case, condition, repeat, request in trials:
            if mode == "live" and spent + estimate_cost(request, spec.pricing) > spec.max_spend_usd:
                status, error = "budget_stopped", "Insufficient remaining estimated budget"
                break
            start = time.perf_counter()
            grade, trial_error, trial_status = None, None, "provider_error"
            interrupted = False
            try:
                response = provider.generate(request)
            except KeyboardInterrupt:
                interrupted = True
                response = ModelResponse(finish_status="interrupted", error="KeyboardInterrupt")
            except Exception as exc:
                # Exception strings can contain credentials or complete request bodies.
                response = ModelResponse(finish_status="error", error=type(exc).__name__)
            response = response.model_copy(
                update={"latency_ms": (time.perf_counter() - start) * 1000}
            )
            if interrupted:
                trial_status, trial_error = "interrupted", "KeyboardInterrupt"
            elif response.error:
                trial_error = response.error
            elif response.finish_status != "completed":
                trial_status, trial_error = (
                    "invalid_output",
                    f"finish_status:{response.finish_status}",
                )
            else:
                try:
                    grade = experiment.grade(case, response, request=request)
                    if grade.grader_version != spec.grader_version:
                        raise ValueError("Grader version does not match config")
                    trial_status = "passed" if grade.passed else "task_failed"
                    if not grade.valid_output:
                        trial_status = "invalid_output"
                except Exception as exc:
                    grade = None
                    trial_status, trial_error = "grader_error", type(exc).__name__
            accounting = (
                cost_details(response.usage, spec.pricing)
                if mode == "live" and response.usage
                else {}
            )
            estimated_cost = 0.0 if mode == "mock" else accounting.get("estimated_cost_usd")
            record = RunRecord(
                run_id=run_id,
                trial_id=f"{case.id}/{condition.id}/{repeat}",
                case_id=case.id,
                condition_id=condition.id,
                repeat=repeat,
                dataset_id=case.dataset_id,
                dataset_version=case.dataset_version,
                ground_truth_ref=f"{case.dataset_id}@{case.dataset_version}#{case.id}",
                ground_truth=case.ground_truth,
                request_hash=digest(request),
                prompt_hash=digest(request.messages),
                request=request,
                provider=condition.provider,
                model=request.model,
                offered_tool_ids=[t["name"] for t in request.tools],
                tool_definition_bytes=len(canonical(request.tools).encode("utf-8")),
                estimated_input_tokens=estimate_input_tokens(request),
                response=response,
                grade=grade,
                status=trial_status,
                error=trial_error,
                estimated_cost_usd=estimated_cost,
                cost_basis="offline_no_charge"
                if mode == "mock"
                else "reported_usage_times_snapshot",
                cost_details=accounting,
            )
            store.append(record)
            records.append(record)
            spent += estimated_cost or 0
            if interrupted:
                raise KeyboardInterrupt
            if mode == "live" and (response.error or estimated_cost is None):
                status, error = "failed", "Live usage/cost uncertain; no further requests scheduled"
                break
    except KeyboardInterrupt:
        status, error = "interrupted", "KeyboardInterrupt"
    except Exception as exc:
        status, error = "failed", type(exc).__name__
    finally:
        if status == "completed" and any(
            r.status in {"provider_error", "grader_error"} for r in records
        ):
            status = "completed_with_errors"
        summary = summarize(
            records, len(trials), {c.id: len(cases) * spec.repetitions for c in spec.conditions}
        )
        summary.update({"run_id": run_id, "run_status": status, "mode": mode})
        manifest = manifest.model_copy(
            update={
                "ended_at": now(),
                "status": status,
                "totals": summary,
                "error": error,
            }
        )
        store.write("manifest.json", manifest)
        store.write("summary.json", summary)
    return {"run_id": run_id, "path": str(store.path), **summary}
