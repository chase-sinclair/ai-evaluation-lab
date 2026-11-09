"""Prepare, verify or dispatch exactly one separately approved stage."""

import argparse
import hashlib
import json
from pathlib import Path

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.budgets import preflight
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.registry import load
from eval_lab.core.result_store import read_records, write_once
from eval_lab.core.runner import run, validate
from eval_lab.providers.openai_adapter import OpenAIProvider, request_payload

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1] / "results"
FIRST = HERE / "stage1.json"
MODEL = "gpt-6-luna"
CAP = 0.10
PRICING = dict(
    model=MODEL,
    version="standard-short-2026-11-09",
    verified_date="2026-11-09",
    source_url="https://developers.openai.com/api/docs/pricing",
    input_usd_per_million=0.10,
    output_usd_per_million=0.50,
    cache=dict(
        service_tier="default",
        read_usd_per_million=0.01,
        write_usd_per_million={"30m": 0.125, "12h": 0.25},
    ),
)


def run_dir(root, stage):
    return root / f"enterprise-rag-stage{stage}-once"


def ledger(path):
    return hashlib.sha256((path / "records.jsonl").read_bytes()).hexdigest()


def build(stage, root):
    if stage not in (1, 2):
        raise ValueError("Unknown stage")
    exp = load(HERE.name, HERE.parent)
    prior = 0.0
    sources = {}
    parent = None
    if stage == 2:
        _, first = verified_first(root)
        path = run_dir(root, 1)
        seal = json.loads((path / "seal.json").read_bytes())
        records, warnings = read_records(path)
        if warnings or seal != {"approval": digest(first), "records_sha256": ledger(path)}:
            raise ValueError("Unsealed or changed stage one")
        for row, r in zip(first["rows"], records, strict=True):
            if (r.case_id, r.condition_id, r.status, digest(r.request)) != (
                row["case"],
                row["stage"],
                "passed",
                row["request_hash"],
            ):
                raise ValueError("Invalid source receipt")
            prior += r.estimated_cost_usd
            if r.condition_id == "generator":
                exp.answers[r.case_id] = r.response.parsed
                sources[r.case_id] = dict(
                    receipt_hash=digest(r),
                    response_id=r.response.raw["id"],
                    text_sha256=hashlib.sha256(r.response.parsed.encode()).hexdigest(),
                    request_hash=r.request_hash,
                )
        parent = seal
    stages = ("generator", "gate") if stage == 1 else ("verifier",)
    cfg = exp.spec.model_dump()
    cfg.update(
        conditions=[
            dict(id=s, variables={"stage": s}, provider="openai", model=MODEL) for s in stages
        ],
        max_requests=36 * len(stages),
        max_output_tokens=512 if stage == 1 else 256,
        max_spend_usd=min(0.055224 if stage == 1 else 0.037008, round(CAP - prior, 12)),
        pricing=PRICING,
    )
    exp.spec = ExperimentSpec.model_validate(cfg)
    _, trials = validate(exp)
    trials.sort(key=lambda t: (t[0].id, (t[1].id == "gate") == bool(int(t[0].id[1:]) % 2)))
    preflight(exp.spec, [r for _, _, _, r in trials], "live", True)
    rows = []
    for case, cond, _, req in trials:
        body = request_payload(req)
        size = len(canonical(body).encode())
        if size + 256 > (2300 if stage == 1 else 3600):
            raise ValueError("Input envelope exceeded")
        rows.append(
            dict(
                case=case.id,
                stage=cond.id,
                body=body,
                bytes=size,
                body_hash=digest(body),
                request_hash=digest(req),
                source=sources.get(case.id),
            )
        )
    reserve = round(
        sum((r["bytes"] + 256) * 0.25 + r["body"]["max_output_tokens"] * 0.5 for r in rows) / 1e6,
        12,
    )
    if reserve > exp.spec.max_spend_usd or prior + reserve > CAP:
        raise ValueError("Reserve exceeds budget")
    return exp, dict(
        stage=stage,
        protocol_hash=digest(exp.protocol),
        spec=exp.spec.model_dump(),
        parent=parent,
        stage_one_spend=prior,
        cumulative_cap=CAP,
        reserve=reserve,
        rows=rows,
    )


def verified_first(root):
    exp, plan = build(1, root)
    if plan != json.loads(FIRST.read_bytes()):
        raise ValueError("Stage one freeze changed")
    return exp, plan


def manifest_path(root, stage):
    return FIRST if stage == 1 else run_dir(root, 1) / "stage2-proposal.json"


def execute(stage, approval, root, client):
    exp, plan = build(stage, root)
    if plan != json.loads(manifest_path(root, stage).read_bytes()) or approval != digest(plan):
        raise ValueError("Stage manifest or approval digest mismatch")
    if client.max_retries != 0:
        raise ValueError("Retries must be disabled")
    rows = iter(plan["rows"])
    limits = {r["request_hash"]: r["bytes"] + 256 for r in plan["rows"]}

    class Frozen(OpenAIProvider):
        def payload(self, request):
            row = next(rows)
            body = super().payload(request)
            if digest(body) != row["body_hash"] or digest(request) != row["request_hash"]:
                raise ValueError("Body mismatch")
            return body

    seen = set()

    def accounting(r):
        u = r.response.usage
        rid = r.response.raw.get("id")
        if (
            r.status != "passed"
            or not rid
            or rid in seen
            or r.response.model != MODEL
            or not u
            or not u.cache
            or u.cache.service_tier != "default"
            or r.estimated_cost_usd is None
            or u.input_tokens > limits[r.request_hash]
            or u.output_tokens > r.request.max_output_tokens
        ):
            return max(
                plan["reserve"], r.estimated_cost_usd or 0
            ), "Invalid stage receipt or accounting"
        seen.add(rid)
        return r.estimated_cost_usd, None

    path = run_dir(root, stage)
    result = run(
        exp,
        results=root,
        run_id=path.name,
        mode="live",
        live=True,
        trial_order=[(r["case"], r["stage"], 0) for r in plan["rows"]],
        provider_factory=lambda: Frozen(live=True, client=client),
        live_record_policy=accounting,
    )
    if result["run_status"] == "completed":
        write_once(path / "seal.json", dict(approval=approval, records_sha256=ledger(path)))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["verify", "materialize", "execute"])
    parser.add_argument("--stage", type=int, choices=[1, 2], required=True)
    parser.add_argument("--approval-digest")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    _, plan = build(args.stage, RESULTS)
    file = manifest_path(RESULTS, args.stage)
    if args.action == "materialize":
        if args.stage != 2 or args.live:
            parser.error("Materialize stage two offline only")
        write_once(file, plan)
    if plan != json.loads(file.read_bytes()):
        parser.error("Manifest mismatch")
    print(digest(plan), plan["reserve"])
    if args.action == "execute":
        if not args.live or args.approval_digest != digest(plan):
            parser.error("Explicit stage approval required")
        from openai import OpenAI

        with OpenAI(base_url="https://api.openai.com/v1", max_retries=0, timeout=60) as client:
            result = execute(args.stage, args.approval_digest, RESULTS, client)
        print(result["run_status"])
        if result["run_status"] != "completed":
            raise SystemExit(1)
