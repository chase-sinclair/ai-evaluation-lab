"""Offline freeze check and separately authorized, single-use live entry point."""

import argparse
import json
from pathlib import Path

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.budgets import preflight
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.registry import load
from eval_lab.core.runner import run, validate
from eval_lab.providers.openai_adapter import OpenAIProvider, request_payload

from .experiment import REFERRAL

HERE = Path(__file__).resolve().parent
FILE = HERE / "manifest.json"


def build():
    exp = load(HERE.name, HERE.parent)
    cfg = exp.spec.model_dump()
    model = "gpt-6-luna"
    for c in cfg["conditions"]:
        c.update(provider="openai", model=model)
    cfg.update(
        max_spend_usd=0.05,
        pricing=dict(
            version="standard-short-2026-11-09",
            verified_date="2026-11-09",
            source_url="https://developers.openai.com/api/docs/pricing",
            model=model,
            input_usd_per_million=0.10,
            output_usd_per_million=0.50,
            cache=dict(
                service_tier="default",
                read_usd_per_million=0.01,
                write_usd_per_million={"30m": 0.125, "12h": 0.25},
            ),
        ),
    )
    exp.spec = ExperimentSpec.model_validate(cfg)
    cases, trials = validate(exp)
    requests = [r for _, _, _, r in trials]
    preflight(exp.spec, requests, "live", True)
    trials.sort(key=lambda t: (t[0].id, (t[1].id == "gate") == bool(int(t[0].id[1:]) % 2)))
    rows = []
    for case, condition, _, req in trials:
        body = request_payload(req)
        rows.append(
            dict(
                case=case.id,
                stage=condition.id,
                body=body,
                body_hash=digest(body),
                request_hash=digest(req),
                input_allowance=len(canonical(body).encode()) + 256,
            )
        )
    reserve = round(
        sum(r["input_allowance"] * 0.25 + r["body"]["max_output_tokens"] * 0.5 for r in rows) / 1e6,
        10,
    )
    if reserve > exp.spec.max_spend_usd or len(rows) != 48:
        raise ValueError("Plan outside limits")
    return exp, dict(
        spec=cfg,
        dataset_hash=digest(cases_as_dict(cases)),
        referral=REFERRAL,
        rows=rows,
        reserve=reserve,
    )


def cases_as_dict(cases):
    return [c.model_dump() for c in cases]


def verify():
    exp, plan = build()
    if plan != json.loads(FILE.read_bytes()):
        raise ValueError("Changed freeze")
    return exp, plan


def execute(approval, results, client):
    exp, plan = verify()
    if approval != digest(plan):
        raise ValueError("Wrong approval digest")
    rows = iter(plan["rows"])
    allowances = {r["request_hash"]: r["input_allowance"] for r in plan["rows"]}

    class FrozenProvider(OpenAIProvider):
        def payload(self, request):
            row = next(rows)
            body = super().payload(request)
            if digest(request) != row["request_hash"] or digest(body) != row["body_hash"]:
                raise ValueError("Frozen body mismatch")
            return body

    def accounting(record):
        response = record.response
        usage = response.usage
        amount = record.estimated_cost_usd
        if (
            record.status not in ("passed", "task_failed")
            or response.model != record.model
            or usage is None
            or usage.cache is None
            or usage.cache.service_tier != "default"
            or amount is None
            or usage.input_tokens > allowances[record.request_hash]
            or usage.output_tokens > record.request.max_output_tokens
        ):
            return max(plan["reserve"], amount or 0), "Stage or accounting failure"
        return amount, None

    return run(
        exp,
        results=results,
        run_id="alder-v1-once",
        mode="live",
        live=True,
        trial_order=[(r["case"], r["stage"], 0) for r in plan["rows"]],
        provider_factory=lambda: FrozenProvider(live=True, client=client),
        live_record_policy=accounting,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--approval-digest")
    args = parser.parse_args()
    _, plan = verify()
    print(digest(plan), plan["reserve"])
    if args.live:
        if args.approval_digest != digest(plan):
            parser.error("Exact approval digest required")
        from openai import OpenAI

        with OpenAI(base_url="https://api.openai.com/v1", timeout=60, max_retries=0) as client:
            result = execute(args.approval_digest, HERE.parents[1] / "results", client)
        print(result["path"], result["run_status"])
        if result["run_status"] != "completed":
            raise SystemExit(1)
