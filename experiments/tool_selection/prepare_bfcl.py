"""Render/check the frozen BFCL request matrix offline; has no execution mode."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.budgets import estimate_cost, estimate_input_tokens
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.runner import validate

from . import bfcl_data as data
from .bfcl_grader import VERSION as GRADER_VERSION
from .bfcl_integration import PROMPT_VERSION
from .experiment import Experiment

DIRECTORY = Path(__file__).resolve().parent
MANIFEST = DIRECTORY / "bfcl" / "development_requests.json"
SMOKE_CASES = ("simple_python_0", "simple_python_13", "irrelevance_0")
FROZEN_DIGEST = "c28821663e194956db707d6b595b0c1ee93356aacefabb8193098bdac583833b"


def load_experiment() -> Experiment:
    spec = ExperimentSpec.model_validate(
        yaml.safe_load((DIRECTORY / "bfcl_development.yaml").read_text(encoding="utf-8"))
    )
    # Historical config/manifest stay immutable; current execution records the corrected grader.
    return Experiment(spec.model_copy(update={"grader_version": GRADER_VERSION}), DIRECTORY)


def prepare() -> dict:
    experiment = load_experiment()
    cases, trials = validate(experiment)
    rows = []
    for case, condition, repeat, request in trials:
        name = data.wire_name(case.task_input["function"]["name"])
        target = next(t for t in request.tools if t["name"] == name)
        rows.append(
            {
                "case_id": case.id,
                "condition_id": condition.id,
                "repeat": repeat,
                "request": request.model_dump(mode="json"),
                "request_hash": digest(request),
                "prompt_hash": digest(request.messages),
                "answer_hash": digest(case.ground_truth),
                "source_row_hash": case.provenance["source_row_sha256"],
                "tool_count": len(request.tools),
                "tool_order": [t["name"] for t in request.tools],
                "original_function_hash": digest(case.task_input["function"]),
                "target_schema_hash": digest(target),
                "original_function_position_zero_based": request.tools.index(target),
                "tool_definition_bytes": len(canonical(request.tools).encode("utf-8")),
                "conservative_input_tokens": estimate_input_tokens(request),
                "conservative_cost_usd": estimate_cost(request, experiment.spec.pricing),
                "smoke_proposal": case.id in SMOKE_CASES and len(request.tools) in (5, 30),
            }
        )
    # LF-normalized text hashes make frozen manifests reproducible on Windows and Linux.
    root = DIRECTORY.parents[1]
    files = sorted(DIRECTORY.glob("*.py")) + sorted((root / "src/eval_lab").rglob("*.py"))
    source_hashes = {
        path.relative_to(root).as_posix(): hashlib.sha256(
            path.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest()
        for path in files
    }
    return {
        "kind": "offline-development-requests-not-results",
        "version": data.VERSION,
        "source_revision": data.REVISION,
        "dataset_hash": digest([case.model_dump() for case in cases]),
        "config": experiment.spec.model_dump(mode="json"),
        "config_hash": digest(experiment.spec),
        "prompt_version": PROMPT_VERSION,
        "grader_version": GRADER_VERSION,
        "source_hashes_lf_utf8": source_hashes,
        "independent_case_claim": False,
        "distinct_case_ids": len(cases),
        "repetitions_per_case_condition": 1,
        "no_call_cases": sum(not c.ground_truth["bfcl"] for c in cases),
        "excluded": data.EXCLUDED,
        "provider_calls": 0,
        "requests": rows,
    }


def verify_frozen() -> dict:
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if digest(frozen) != FROZEN_DIGEST:
        raise ValueError("Frozen Phase 2 manifest changed")
    current = prepare()
    # Historical source/grader metadata is retained, not rewritten to pretend it is current.
    for key in frozen.keys() - {"source_hashes_lf_utf8", "grader_version", "config", "config_hash"}:
        if frozen[key] != current[key]:
            raise ValueError(f"Frozen request manifest differs: {key}")
    expected_config = {**frozen["config"], "grader_version": GRADER_VERSION}
    if current["config"] != expected_config or current["config_hash"] != digest(expected_config):
        raise ValueError("Unexpected development configuration change")
    return frozen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = prepare()
    if args.check:
        verify_frozen()
    else:
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(canonical(manifest) + "\n")
    print(f"Validated {len(manifest['requests'])} requests; zero provider/network calls.")


if __name__ == "__main__":
    main()
