"""Run the authored offline acquisition once and save its paired policy replay."""

import argparse
import json
from pathlib import Path

from eval_lab.contracts import ModelResponse
from eval_lab.core.registry import load
from eval_lab.core.result_store import read_records, write_once
from eval_lab.core.runner import run

from .policies import replay


class ScriptedProvider:
    def generate(self, request):
        title = json.loads(request.messages[-1]["content"])["left"]["title"]
        outputs = {
            "Arbor desk lamp D12 white": "NON_MATCH",
            "Cobalt USB hub H4": "MATCH",
            "Finch filter three pack": "UNKNOWN",
            "Orbit recorder O4 portable": "MATCH",
        }
        return ModelResponse(parsed=outputs[title], model=request.model)


def demo(root: Path) -> tuple[Path, list[dict]]:
    exp = load("entity_matching", Path(__file__).resolve().parent.parent)
    path = Path(run(exp, results=root, provider_factory=ScriptedProvider)["path"])
    records, warnings = read_records(path)
    if warnings:
        raise ValueError(warnings)
    reports = replay(exp, records)
    write_once(path / "policies.json", reports)
    return path, reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results"))
    path, reports = demo(parser.parse_args().results)
    print(path)
    for r in reports:
        print(r["percent"], r["metrics"], r["fallbacks"])
