"""One-shot Experiment 007 acquisition on the Claude Messages API.

Sends the 432 frozen single-turn requests once, in order. Before each request the accounted
spend plus that request's worst-case cost must stay within the approved cap. Grading and
review are separate and offline.

Credentials come only from the caller's environment (ANTHROPIC_API_KEY, or an
`ant auth login` profile). Nothing here reads, stores or logs them.
"""

import argparse
import gzip
import hashlib
import json
import subprocess
from decimal import Decimal
from time import perf_counter

import anthropic
import httpx2

from eval_lab.core.hashes import canonical, digest
from experiments.claude_context.accounting import charge, terminal
from experiments.claude_context.proposal import CAP, FROZEN, MODELS, REPO, build

# Filled from the frozen proposal. A change to any source the proposal hashes changes these.
APPROVAL = "1d0f60453140362f1f0ddc50a089066d80b093ccac14e2c063d3074447affdef"
SHA = "933936714bb02dee4b6cac4479c4c1c5ea9d6bfa683fb1d8432648f7b162cb3a"
ARRAY = "fdd81300b540c3d66d2792d3a6a7f55835b85be2cfad9939930be8f8775324fa"
# Last Lab checkpoint before this experiment's implementation.
BASE = "5ac9d1a"
EXTENSIONS = {
    "pyproject.toml",
    "uv.lock",
    "docs/PROGRESS.md",
    "docs/verification.md",
    "docs/experiment07_claude_replication_design.md",
    "experiments/claude_context/README.md",
    "experiments/claude_context/proposal.py",
    "experiments/claude_context/accounting.py",
    "experiments/claude_context/analysis.py",
    "experiments/claude_context/protocol.md",
    "experiments/claude_context/proposals/r1/manifest.json",
    "experiments/claude_context/proposals/r1/bodies.json.gz",
    "scripts/acquire_claude_context.py",
    "tests/test_claude_context.py",
}
RUN = REPO / "results/meridian-claude-context-r1-once"
BASE_URL = "https://api.anthropic.com"
URL = BASE_URL + "/v1/messages"
# Request headers worth keeping. Authentication headers are never recorded.
KEPT_HEADERS = ("anthropic-version", "anthropic-beta", "content-type")


def require(test, message):
    if not test:
        raise ValueError(message)


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


def timeout() -> httpx2.Timeout:
    return httpx2.Timeout(connect=10, write=30, pool=10, read=900)


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


class WireGuard:
    """Only the pending frozen body may leave, only to the Messages endpoint."""

    def __init__(self):
        self.pending = None

    def check(self, request):
        row = self.pending
        self.pending = None
        require(
            row is not None and request.method == "POST" and str(request.url) == URL,
            "unapproved HTTP",
        )
        outgoing = json.loads(request.content)
        require(
            outgoing == row["body"] and digest(outgoing) == row["body_sha256"],
            "wire body mismatch",
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
        with anthropic.Anthropic(base_url=BASE_URL, max_retries=0, timeout=30) as lookup:
            for model in MODELS.values():
                require(lookup.models.retrieve(model).id == model, "model access")
    else:
        require(isinstance(mock, httpx2.MockTransport), "mock transport required")
    dest.mkdir(parents=True, exist_ok=False)
    guard = WireGuard()
    spent = Decimal(0)
    ids = set()
    sent = finished = exhaustions = refusals = accounted = 0
    failure = stop = None

    def verify_wire(request):
        guard.check(request)
        with (dest / f"{sent:03}.request-body").open("xb") as wire:
            wire.write(request.content)
        save(
            dest / f"{sent:03}.request-headers",
            {k: request.headers.get(k) for k in KEPT_HEADERS},
        )

    try:
        save(dest / "plan.json", dict(digest=auth, revision=reviewed, allowance=str(allowance)))
        with (
            httpx2.Client(
                transport=mock,
                follow_redirects=False,
                trust_env=False,
                event_hooks={"request": [verify_wire]},
            ) as http,
            anthropic.Anthropic(
                api_key="mock" if mock else None,
                base_url=BASE_URL,
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
                reply = client.messages.with_raw_response.create(**payload)
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
                        request_id=reply.headers.get("request-id"),
                    ),
                )
                rid = raw.get("id")
                require(
                    isinstance(rid, str)
                    and rid.startswith("msg_")
                    and len(rid) > 4
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
                answer = terminal(raw)
                event = {"cost": str(cost), "model_latency": latency, "served_model": raw["model"]}
                if answer["kind"] == "output_exhaustion":
                    exhaustions += 1
                    save(dest / (prefix + ".event"), event | {"outcome": "output_exhaustion"})
                    continue
                if answer["kind"] == "refusal":
                    refusals += 1
                    save(
                        dest / (prefix + ".event"), event | {"outcome": "refusal", "final": answer}
                    )
                    continue
                save(dest / (prefix + ".event"), event | {"final": answer})
                finished += 1
        if stop is None:
            require(finished + exhaustions + refusals == len(bodies), "final reconciliation")
    except BaseException as exc:
        failure = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        if isinstance(exc, anthropic.APIStatusError):
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
                refused=refusals,
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
        choices=["haiku 0.10/0.01/0.125/0.50 sonnet 2.00/0.10/2.50/10.00"],
    )
    parser.add_argument("--confirm-credit-and-workspace-limits", action="store_true", required=True)
    args = parser.parse_args()
    acquire(args.approval, args.reviewed_revision, args.cap_usd)
