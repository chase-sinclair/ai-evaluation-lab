"""Rebuild and check the normalized live manifest without constructing a provider."""

import argparse
import json
from pathlib import Path

import yaml

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.budgets import preflight
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.registry import load
from eval_lab.core.runner import validate
from eval_lab.providers.openai_adapter import request_payload

HERE = Path(__file__).resolve().parent
FILE = HERE / "request-manifest.json"


def build():
    exp = load(HERE.name, HERE.parent)
    proposal = yaml.safe_load((HERE / "live-proposal.yaml").read_text(encoding="utf8"))
    config = exp.spec.model_dump()
    for c in config["conditions"]:
        c.update(provider="openai", model=proposal["model"])
    config.update({k: proposal[k] for k in ("max_spend_usd", "max_requests", "pricing")})
    exp.spec = ExperimentSpec.model_validate(config)
    cases, trials = validate(exp)
    requests = [r for _, _, _, r in trials]
    runner_reserve = preflight(exp.spec, requests, "live", True)
    rows = []
    messages = {}
    body_settings = {}
    input_ceiling = 0
    for case, condition, _, req in trials:
        body = request_payload(req)
        body_bytes = len(canonical(body).encode())
        input_ceiling += body_bytes + 256
        body_settings = {k: v for k, v in body.items() if k not in ("input", "tools")}
        messages[case.id] = req.messages
        rows.append(
            {
                "case": case.id,
                "condition": condition.id,
                "tools": [t["name"] for t in req.tools],
                "schema_bytes": len(canonical(req.tools).encode()),
                "body_bytes": body_bytes,
                "logical_sha256": digest(req),
                "body_sha256": digest(body),
            }
        )
    pricing = exp.spec.pricing
    output_ceiling = len(rows) * exp.spec.max_output_tokens
    input_rate = max(pricing.input_usd_per_million, *pricing.cache.write_usd_per_million.values())
    reserve = (input_ceiling * input_rate + output_ceiling * pricing.output_usd_per_million) / 1e6
    reserve = round(max(reserve, runner_reserve), 10)
    if reserve > exp.spec.max_spend_usd:
        raise ValueError("Full-body reserve exceeds proposed cap")
    return {
        "spec": config,
        "dataset_sha256": digest([c.model_dump() for c in cases]),
        "body_settings": body_settings,
        "messages_by_case": dict(sorted(messages.items())),
        "functions_by_name": {t["name"]: t for t in exp.tools},
        "trials_in_run_order": rows,
        "input_token_allowance": input_ceiling,
        "output_token_ceiling": output_ceiling,
        "conservative_reserve_usd": reserve,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write a new freeze for review")
    args = parser.parse_args()
    plan = build()
    if args.write:
        FILE.write_text(
            json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf8", newline="\n"
        )
    if json.loads(FILE.read_bytes()) != plan:
        raise SystemExit("Frozen manifest differs from current inputs")
    print(
        f"{len(plan['trials_in_run_order'])} requests; ${plan['conservative_reserve_usd']:.8f} "
        f"reserve; SHA-256 {digest(plan)}"
    )


if __name__ == "__main__":
    main()
