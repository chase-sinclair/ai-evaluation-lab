"""Single-use entry point for an owner-approved manifest; no default live action."""

import argparse
import json
from pathlib import Path

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.hashes import digest
from eval_lab.core.registry import load
from eval_lab.core.runner import run
from eval_lab.providers.openai_adapter import OpenAIProvider

from .freeze import FILE, HERE, build


def execute(approval: str, results: Path, client):
    plan = build()
    if plan != json.loads(FILE.read_bytes()) or digest(plan) != approval:
        raise ValueError("Approval digest or frozen manifest mismatch")
    exp = load(HERE.name, HERE.parent)
    exp.spec = ExperimentSpec.model_validate(plan["spec"])
    rows = plan["trials_in_run_order"]
    sequence = iter(rows)

    class FrozenProvider(OpenAIProvider):
        def payload(self, request):
            body = super().payload(request)
            row = next(sequence)
            if digest(request) != row["logical_sha256"] or digest(body) != row["body_sha256"]:
                raise ValueError("Refusing changed request before transmission")
            return body

    allowances = {r["logical_sha256"]: r["body_bytes"] + 256 for r in rows}

    def accounting(record):
        usage = record.response.usage
        amount = record.estimated_cost_usd
        if record.response.error or record.response.model != record.model:
            return plan["conservative_reserve_usd"], "Provider error or unexpected model"
        if usage is None or amount is None or record.status == "grader_error":
            return plan["conservative_reserve_usd"], "Missing accounting or grading failure"
        if (
            usage.input_tokens > allowances[record.request_hash]
            or usage.output_tokens > exp.spec.max_output_tokens
        ):
            return max(plan["conservative_reserve_usd"], amount), "Token allowance exceeded"
        return amount, None

    return run(
        exp,
        results=results,
        run_id="northline-catalog-v1-once",
        mode="live",
        live=True,
        live_record_policy=accounting,
        trial_order=[(r["case"], r["condition"], 0) for r in rows],
        provider_factory=lambda: FrozenProvider(live=True, client=client),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--approval-digest", required=True)
    args = parser.parse_args()
    from openai import OpenAI

    with OpenAI(base_url="https://api.openai.com/v1", max_retries=0, timeout=60) as client:
        result = execute(args.approval_digest, HERE.parents[1] / "results", client)
    print(result["path"], result["run_status"])
    if result["run_status"] != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
