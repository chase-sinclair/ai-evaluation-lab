"""Offline entry points for the frozen Crossref experiment."""

import argparse
import json
from pathlib import Path

from eval_lab.contracts import ModelResponse
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records, write_once
from eval_lab.core.runner import run

from .core import ABSTAIN
from .prepare import build, experiment, load
from .report import replay


class Scripted:
    """Exercise all outcomes independently of source labels."""

    def generate(self, request):
        item = json.loads(request.messages[1]["content"])
        choice = int(digest(item["name"])[:8], 16) % 10
        if choice == 0:
            return ModelResponse(parsed="not a ROR response", model=request.model)
        if choice == 1:
            return ModelResponse(parsed=ABSTAIN, finish_status="incomplete", model=request.model)
        if choice in (2, 3):
            return ModelResponse(parsed=ABSTAIN, model=request.model)
        return ModelResponse(parsed=item["candidates"][int(choice == 4)]["id"], model=request.model)


def analyze(path):
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf8"))
    exp = experiment(manifest["mode"] == "live")
    if manifest["config_hash"] != digest(exp.spec) or manifest["dataset_hash"] != digest(
        [c.model_dump() for c in exp.load_cases()]
    ):
        raise ValueError("Run does not match this frozen cohort")
    records, warnings = read_records(path)
    report = replay(
        exp,
        records,
        exp.spec.conditions[0].variables["calibration"],
        proposal=load("proposal.json"),
    )
    return {
        "run_id": manifest["run_id"],
        "mode": manifest["mode"],
        "warnings": warnings,
        "policies": report,
    }


def demo(root):
    path = Path(run(experiment(), results=root, provider_factory=Scripted)["path"])
    report = analyze(path)
    write_once(path / "resolution_policies.json", report)
    return path, report


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("baseline")
    commands.add_parser("demo").add_argument("--results", type=Path, default=Path("results"))
    commands.add_parser("replay").add_argument("run_directory", type=Path)
    args = cli.parse_args()
    if args.command == "check":
        build(True)
    elif args.command == "baseline":
        print(json.dumps(load("baseline.json"), indent=2))
    elif args.command == "replay":
        print(json.dumps(analyze(args.run_directory), indent=2))
    else:
        path, reports = demo(args.results)
        print(path)
        for r in reports["policies"]:
            print(r["percent"], r["metrics"], r["fallbacks"])
