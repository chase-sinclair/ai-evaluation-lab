"""One-shot Meridian v2 acquisition. All billing and business replay are separate."""

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
from experiments.finops_sql.episode import Discovery, body, final
from experiments.finops_sql.packages import QUESTIONS, ROOT, tokens
from experiments.finops_sql.proposal import build
from scripts.acquire_recovery import WireGuard, require
from scripts.acquire_recovery_followup import account

REV = "50ef8bee917ec80bd69c0f0a5109f17fde4ec6d1"
APPROVAL = "82539bc63c44e9bced2111989c9fcd59f7b867941d70b3e3d943479778e31733"
SHA = "abfa3681186734b32a1211a027bcf73e36bd1ff77da9fec1a2530db4c4924f9c"
ARRAY = "c12b6d4dfa80eb767e1427b71bd788e10a59d36e658b598b8a6bde2b49cc0183"
REPO = ROOT.parents[1]
RUN = REPO / "results/meridian-v2-once"
RESERVE = Decimal(".843264")
EXTENSIONS = {
    "scripts/acquire_finops.py",
    "tests/test_acquire_finops.py",
    "docs/finops_dispatch.md",
    "docs/PROGRESS.md",
    "docs/verification.md",
}


def preflight(auth):
    require(auth == APPROVAL, "external approval")
    folder = ROOT / "proposals/v2"
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
    require(RESERVE <= allowance <= 1 and not dest.exists(), "budget or used destination")
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
    sent = tools = finished = 0
    failure = None

    def reserve(bound):
        return (Decimal(".125") * bound + 1024) / 1000000

    try:
        save(dest / "plan.json", dict(digest=auth, revision=reviewed, allowance=str(allowance)))
        with (
            httpx.Client(
                transport=mock,
                follow_redirects=False,
                trust_env=False,
                event_hooks={"request": [guard.check]},
            ) as http,
            openai.OpenAI(
                api_key="mock" if mock else None,
                base_url="https://api.openai.com/v1",
                http_client=http,
                max_retries=0,
                timeout=60,
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
                    require(sent < 360 and spent + remaining <= allowance, "budget or count")
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
                    require(isinstance(rid, str) and rid and rid not in ids, "response ID")
                    ids.add(rid)
                    charge = account(raw, {"input_allowance": bound})
                    spent += charge
                    remaining -= reserve(bound)
                    require(spent + remaining <= allowance, "accounting breach")
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
                    event = {"cost": str(charge), "model_latency": latency}
                    if calls and payload.get("tools") and len(calls) == 1 and not text.strip():
                        require(tools < 216, "discovery limit")
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
                    remaining -= sum(map(reserve, bounds[turn + 1 :]))
                    break
    except BaseException as exc:
        failure = type(exc).__name__
        if isinstance(exc, openai.APIStatusError):
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
                planned=144,
                accounted_usd=str(spent),
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
    args = parser.parse_args()
    acquire(args.approval, args.reviewed_revision, args.available_usd)
