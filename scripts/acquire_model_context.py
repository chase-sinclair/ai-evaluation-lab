"""One-shot Experiment 006 acquisition. Grading and review are separate and offline.

Sends the 432 frozen single-turn requests once, in order. Before each request the accounted
spend plus that request's worst-case cost must stay within the approved cap.
"""

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
from experiments.finops_sql.episode import final
from experiments.model_context.accounting import charge
from experiments.model_context.proposal import CAP, FROZEN, MODELS, REPO, build
from scripts.acquire_recovery import WireGuard, require

# Filled from the frozen proposal. A change to any source the proposal hashes changes these.
APPROVAL = "f9fd35762130871a80c4a24d28dae47a3bf9f500c5d4f7185cb77fe21ba458f0"
SHA = "ee5915f50fc4c4b433a50d7e016d249e1f0ba370be95d8bdc4cfe476af024a6d"
ARRAY = "f019425b0b4072066009579f758fb7b60bedc6fecb616ba5a6b8223c85e57c58"
# Last accepted Lab checkpoint. Only the files below may differ at the reviewed revision.
BASE = "709da2b"
EXTENSIONS = {
    "docs/PROGRESS.md",
    "docs/verification.md",
    "docs/experiment06_model_context_design.md",
    "experiments/model_context/README.md",
    "experiments/model_context/proposal.py",
    "experiments/model_context/accounting.py",
    "experiments/model_context/analysis.py",
    "experiments/model_context/protocol.md",
    "experiments/model_context/proposals/r1/manifest.json",
    "experiments/model_context/proposals/r1/bodies.json.gz",
    "scripts/acquire_model_context.py",
    "tests/test_model_context.py",
}
RUN = REPO / "results/meridian-model-context-r1-once"


def preflight(auth):
    require(auth == APPROVAL, "external approval")
    data = (FROZEN / "manifest.json").read_bytes()
    require(hashlib.sha256(data).hexdigest() == SHA, "manifest file")
    manifest = json.loads(data)
    stored = manifest.pop("proposal_digest")
    plan, bodies = build()
    require(stored == digest(plan) == APPROVAL and plan == manifest, "source or manifest drift")
    require(
        digest(bodies) == ARRAY
        and json.loads(gzip.decompress((FROZEN / "bodies.json.gz").read_bytes())) == bodies,
        "frozen bodies",
    )
    return plan, bodies


def timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=10, write=30, pool=10, read=900)


def checkout(reviewed):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()

    require(reviewed == git("rev-parse", "HEAD") and not git("status", "--porcelain"), "checkout")
    git("merge-base", "--is-ancestor", BASE, reviewed)
    require(
        set(git("diff", "--name-only", BASE, reviewed).splitlines()) <= EXTENSIONS,
        "extension scope",
    )
    require(
        git("remote", "get-url", "origin").removesuffix(".git")
        == "https://github.com/chase-sinclair/ai-evaluation-lab",
        "repository",
    )


def save(path, value):
    with path.open("xb") as f:
        f.write(canonical(value).encode())


def exhausted(raw, payload) -> bool:
    return (
        raw.get("status") == "incomplete"
        and raw.get("error") is None
        and (raw.get("incomplete_details") or {}).get("reason") == "max_output_tokens"
        and raw["usage"]["output_tokens"] == payload["max_output_tokens"]
    )


def acquire(auth, reviewed, allowance, *, mock=None, dest=RUN):
    plan, bodies = preflight(auth)
    largest = max(Decimal(r["worst_case_usd"]) for r in plan["requests"])
    require(
        allowance.is_finite() and largest <= allowance <= CAP and not dest.exists(),
        "budget or used destination",
    )
    if mock is None:
        require(dest == RUN, "fixed live destination")
        checkout(reviewed)
        with openai.OpenAI(max_retries=0, base_url="https://api.openai.com/v1") as lookup:
            for model in MODELS.values():
                require(lookup.models.retrieve(model).id == model, "model access")
    else:
        require(isinstance(mock, httpx.MockTransport), "mock transport required")
    dest.mkdir(parents=True, exist_ok=False)
    guard = WireGuard()
    spent = Decimal(0)
    ids = set()
    sent = finished = exhaustions = accounted = 0
    failure = stop = None

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
            for row, payload in zip(plan["requests"], bodies, strict=True):
                require(digest(payload) == row["body_hash"], "body binding")
                require(len(canonical(payload).encode()) + 256 <= row["input_bound"], "input bound")
                require(sent < plan["request_ceiling"], "request ceiling")
                if spent + Decimal(row["worst_case_usd"]) > allowance:
                    stop = "spending_guard"
                    break
                sent += 1
                prefix = f"{sent:03}"
                save(
                    dest / (prefix + ".request"),
                    dict(body=payload, hash=row["body_hash"], id=row["id"]),
                )
                guard.pending = {"body": payload, "body_sha256": row["body_hash"]}
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
                        body_hash=row["body_hash"],
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
                cost = charge(raw, payload["model"], row["input_bound"])
                spent += cost
                accounted += 1
                require(spent <= allowance, "accounting breach")
                event = {"cost": str(cost), "model_latency": latency, "served_model": raw["model"]}
                if exhausted(raw, payload):
                    exhaustions += 1
                    save(dest / (prefix + ".event"), event | {"outcome": "output_exhaustion"})
                    continue
                require(
                    raw.get("status") == "completed"
                    and not raw.get("error")
                    and not raw.get("incomplete_details"),
                    "incomplete or failed",
                )
                calls = [
                    x
                    for x in raw.get("output", [])
                    if isinstance(x, dict) and x.get("type") == "function_call"
                ]
                text = reply.parse().output_text
                answer = (
                    {"kind": "invalid_proposals"}
                    if calls
                    else final(text)
                    if text
                    else {"kind": "missing"}
                )
                save(dest / (prefix + ".event"), event | {"final": answer})
                finished += 1
        if stop is None:
            require(finished + exhaustions == len(bodies), "final reconciliation")
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
                stop=stop,
                requests_attempted=sent,
                finished=finished,
                exhausted=exhaustions,
                unsent=len(bodies) - sent,
                planned=len(bodies),
                accounted_usd=str(spent),
                allowance_usd=str(allowance),
                attempts_without_accounting=sent - accounted,
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--approval", required=True)
    parser.add_argument("--reviewed-revision", required=True)
    parser.add_argument("--cap-usd", type=Decimal, required=True)
    parser.add_argument(
        "--confirm-current-standard-rates",
        required=True,
        choices=["luna 0.10/0.01/0.125/0.50 sol 2.00/0.10/2.50/10.00"],
    )
    parser.add_argument("--confirm-credit-and-project-limits", action="store_true", required=True)
    args = parser.parse_args()
    acquire(args.approval, args.reviewed_revision, args.cap_usd)
