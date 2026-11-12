"""One-shot Meridian v3 full evaluation. All billing and business replay are separate."""

import argparse
import gzip
import hashlib
import json
import subprocess
from decimal import Decimal
from time import perf_counter

import httpx
import openai

from eval_lab.core.hashes import canonical, digest
from experiments.finops_sql.episode import Discovery, final
from experiments.finops_sql.evaluation_r1.proposal import build
from experiments.finops_sql.packages import QUESTIONS, ROOT, tokens
from experiments.finops_sql.pilot_v3_1.accounting import charge
from experiments.finops_sql.v3.accounting import timeout
from experiments.finops_sql.v3.proposal import body, reserve
from scripts.acquire_recovery import WireGuard, require

REV = "a145d01d326a2d9242a3e1b7071fb9ac07fedede"
APPROVAL = "4eb6e593374585e11b349cc1341c82bda22048eb2a6ff69560dc7a82d214d36f"
SHA = "9ec95361740e39ac9cc7dbe5ca0fa3361fb2167ace3d4f816c0415c48beb7a50"
ARRAY = "78a96d669a01f0509a4add647df452daf6126e5709316ff7c646544a84bdb986"
REPO = ROOT.parents[1]
RUN = REPO / "results/meridian-v3-evaluation-r1-once"
RESERVE = Decimal("5.008329")
EXTENSIONS = {
    ".github/workflows/finops-checkpoint.yml",
    "scripts/acquire_finops_evaluation.py",
    "tests/test_acquire_finops_evaluation.py",
    "docs/finops_evaluation_dispatch.md",
    "docs/PROGRESS.md",
    "docs/verification.md",
    "experiments/finops_sql/evaluation_r1/proposal.py",
    "experiments/finops_sql/evaluation_r1/analysis.py",
    "experiments/finops_sql/evaluation_r1/protocol.md",
    "experiments/finops_sql/proposals/v3/evaluation-r1/manifest.json",
    "experiments/finops_sql/proposals/v3/evaluation-r1/bodies.json.gz",
}


def preflight(auth):
    require(auth == APPROVAL, "external approval")
    folder = ROOT / "proposals/v3/evaluation-r1"
    data = (folder / "manifest.json").read_bytes()
    require(hashlib.sha256(data).hexdigest() == SHA, "manifest file")
    manifest = json.loads(data)
    stored = manifest.pop("proposal_digest")
    plan, bodies = build()
    require(stored == digest(plan) == APPROVAL and plan == manifest, "source or manifest drift")
    require(
        digest(bodies) == ARRAY
        and json.loads(gzip.decompress((folder / "bodies.json.gz").read_bytes())) == bodies,
        "frozen bodies",
    )
    require(Decimal(plan["reserve_usd"]) == RESERVE, "reserve drift")
    return plan, bodies


def checkout(reviewed):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()

    require(reviewed == git("rev-parse", "HEAD") and not git("status", "--porcelain"), "checkout")
    git("merge-base", "--is-ancestor", REV, reviewed)
    require(
        set(git("diff", "--name-only", REV, reviewed).splitlines()) <= EXTENSIONS, "extension scope"
    )
    require(
        git("remote", "get-url", "origin").removesuffix(".git")
        == "https://github.com/chase-sinclair/ai-evaluation-lab",
        "repository",
    )


def save(path, value):
    with path.open("xb") as f:
        f.write(canonical(value).encode())


def acquire(auth, reviewed, allowance, *, mock=None, dest=RUN):
    plan, bodies = preflight(auth)
    require(
        allowance.is_finite() and RESERVE <= allowance <= Decimal("5.50") and not dest.exists(),
        "budget or used destination",
    )
    if mock is None:
        require(dest == RUN, "fixed live destination")
        checkout(reviewed)
        with openai.OpenAI(max_retries=0, base_url="https://api.openai.com/v1") as lookup:
            require(lookup.models.retrieve(plan["model"]).id == plan["model"], "model access")
    else:
        require(isinstance(mock, httpx.MockTransport), "mock transport required")
    dest.mkdir(parents=True, exist_ok=False)
    guard = WireGuard()
    spent = Decimal(0)
    remaining = RESERVE
    ids = set()
    sent = tools = finished = exhausted = 0
    failure = None
    accounted = 0

    def verify_wire(request):
        guard.check(request)
        with (dest / f"{sent:03}.request-body").open("xb") as wire:
            wire.write(request.content)

    try:
        save(dest / "plan.json", dict(digest=auth, revision=reviewed, allowance=str(allowance)))
        with (
            httpx.Client(
                transport=mock,
                follow_redirects=False,
                trust_env=False,
                event_hooks={"request": [verify_wire]},
            ) as http,
            openai.OpenAI(
                api_key="mock" if mock else None,
                base_url="https://api.openai.com/v1",
                http_client=http,
                max_retries=0,
                timeout=timeout(),
            ) as client,
        ):
            for row, initial in zip(plan["requests"], bodies, strict=True):
                arm = row["arm"]
                q = next(q for q in QUESTIONS if q["id"] == row["question"])
                state = Discovery()
                bounds = row["turn_input_bounds"]
                for turn, bound in enumerate(bounds):
                    payload = body(arm, q, state.history)
                    h = digest(payload)
                    require(
                        turn or (payload == initial and h == row["body_hash"]), "initial binding"
                    )
                    require(len(canonical(payload).encode()) + 256 <= bound, "input allowance")
                    require(
                        sent < plan["request_ceiling"] and spent + remaining <= allowance,
                        "budget or count",
                    )
                    sent += 1
                    prefix = f"{sent:03}"
                    save(
                        dest / (prefix + ".request"),
                        dict(
                            body=payload,
                            hash=h,
                            arm=arm,
                            question=q["id"],
                            prior_history=digest(state.history),
                        ),
                    )
                    guard.pending = {"body": payload, "body_sha256": h}
                    start = perf_counter()
                    reply = client.responses.with_raw_response.create(**payload)
                    latency = perf_counter() - start
                    with (dest / (prefix + ".response-body")).open("xb") as original:
                        original.write(reply.http_response.content)
                    raw = reply.http_response.json()
                    save(
                        dest / (prefix + ".response"),
                        dict(
                            raw=raw,
                            latency=latency,
                            body_hash=h,
                            request_id=reply.headers.get("x-request-id"),
                        ),
                    )
                    rid = raw.get("id")
                    require(
                        isinstance(rid, str)
                        and rid.startswith("resp_")
                        and len(rid) > 5
                        and rid.isascii()
                        and not any(c.isspace() for c in rid)
                        and rid not in ids,
                        "response ID",
                    )
                    ids.add(rid)
                    cost = charge(raw, bound)
                    spent += cost
                    accounted += 1
                    remaining -= reserve(bound, 1)
                    require(spent + remaining <= allowance, "accounting breach")
                    future = reserve(sum(bounds[turn + 1 :]), len(bounds[turn + 1 :]))
                    if (
                        raw.get("status") == "incomplete"
                        and raw.get("error") is None
                        and (raw.get("incomplete_details") or {}).get("reason")
                        == "max_output_tokens"
                        and raw["usage"]["output_tokens"] == payload["max_output_tokens"]
                    ):
                        exhausted += 1
                        remaining -= future
                        save(
                            dest / (prefix + ".event"),
                            dict(
                                outcome="output_exhaustion",
                                cost=str(cost),
                                model_latency=latency,
                                depth=turn,
                                released_future_usd=str(future),
                            ),
                        )
                        break
                    require(
                        raw.get("status") == "completed"
                        and not raw.get("error")
                        and not raw.get("incomplete_details"),
                        "incomplete or failed",
                    )
                    effort = (raw.get("reasoning") or {}).get("effort")
                    require(effort in (None, "medium"), "unexpected reasoning effort")
                    output = raw.get("output", [])
                    calls = [
                        x
                        for x in output
                        if isinstance(x, dict) and x.get("type") == "function_call"
                    ]
                    text = reply.parse().output_text
                    event = {"cost": str(cost), "model_latency": latency}
                    if calls and payload.get("tools") and len(calls) == 1 and not text.strip():
                        require(tools < plan["tool_ceiling"], "discovery limit")
                        tools += 1
                        start = perf_counter()
                        record = state.select(calls[0].get("name"), calls[0].get("arguments"))
                        event.update(
                            record=record,
                            discovery_latency=perf_counter() - start,
                            tokens=tokens(record.get("result", record)),
                            history=digest(state.history),
                        )
                        save(dest / (prefix + ".event"), event)
                        continue
                    result = (
                        {"kind": "invalid_proposals"}
                        if calls
                        else final(text)
                        if text
                        else {"kind": "missing"}
                    )
                    event.update(final=result, depth=len(state.history))
                    save(dest / (prefix + ".event"), event)
                    finished += 1
                    remaining -= future
                    break
        require(remaining == 0 and finished + exhausted == len(bodies), "final reconciliation")
    except BaseException as exc:
        failure = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        if isinstance(exc, openai.APIStatusError):
            with (dest / f"{sent:03}.response-body").open("xb") as original:
                original.write(exc.response.content)
            save(
                dest / "provider-error.json",
                dict(status=exc.status_code, body=exc.body, request_id=exc.request_id),
            )
        raise
    finally:
        hashes = {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.iterdir())
        }
        save(
            dest / "seal.json",
            dict(
                files=hashes,
                ledger_hash=digest(hashes),
                failure=failure,
                requests_attempted=sent,
                tools=tools,
                finished=finished,
                exhausted=exhausted,
                remaining_reserve_usd=str(remaining),
                planned=len(bodies),
                accounted_usd=str(spent),
                attempts_without_accounting=sent - accounted,
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval", required=True)
    parser.add_argument("--reviewed-revision", required=True)
    parser.add_argument("--available-usd", type=Decimal, required=True)
    parser.add_argument(
        "--confirm-current-standard-rates", required=True, choices=["0.10/0.01/0.125/0.50"]
    )
    parser.add_argument("--confirm-credit-and-project-limits", action="store_true", required=True)
    args = parser.parse_args()
    acquire(args.approval, args.reviewed_revision, args.available_usd)
