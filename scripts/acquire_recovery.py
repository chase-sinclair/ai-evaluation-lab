"""Single-use Experiment 004 dispatcher. Run as a module from the clean checkout."""

import argparse
import hashlib
import subprocess
from decimal import Decimal
from time import perf_counter

import httpx
import openai

from eval_lab.core.hashes import digest
from eval_lab.core.result_store import ResultStore
from eval_lab.providers.openai_adapter import normalize_usage, parse_arguments
from experiments.recovery import plan, study

BASE = "b8a6fca69d0210152db4c2f38a9ecbb990401f73"
APPROVAL = "9448447d08eecc717aa695b7a677bc9142ae2724669b940c3e1f5fd42b7673e3"
FILE_HASH = "0263bfd4ab8ceab1b8107a499e456e5e0212575d7599a78e62be827066209813"
RUN = "recovery-live-once"
ROOT = study.HERE.parents[1]
MODEL = "gpt-6-luna"
CAP = Decimal(".025")
URL = "https://api.openai.com/v1/responses"


def require(test, message):
    if not test:
        raise ValueError(message)


def reserve(row):
    return (Decimal(".125") * row["input_allowance"] + 256) / 1000000


def within_budget(spent, remaining):
    require(spent + sum(map(reserve, remaining)) <= CAP, "remaining budget exceeded")


def preflight(approval):
    require(approval == APPROVAL, "explicit digest approval required")
    require(hashlib.sha256(plan.FILE.read_bytes()).hexdigest() == FILE_HASH, "manifest file hash")
    frozen = plan.verify()
    require(digest(frozen) == APPROVAL, "manifest approval mismatch")
    rows = frozen["requests"]
    cases = {r["id"]: r for r in study.inventory()}
    require(len(rows) == 24 and {r["case"] for r in rows} == cases.keys(), "case inventory")
    for row in rows:
        source, seal = study.checkpoint(cases[row["case"]])
        b = plan.body(plan.request(source["public"]))
        require(
            b == row["body"]
            and digest(b) == row["body_sha256"]
            and seal == row["checkpoint_sha256"],
            "request or checkpoint binding",
        )
        require(
            b["model"] == MODEL
            and b["max_output_tokens"] == 512
            and b["service_tier"] == "default"
            and b["prompt_cache_options"] == {"ttl": "30m"}
            and all(t["type"] == "function" for t in b["tools"]),
            "request settings",
        )
    require(sum(map(reserve, rows)) == Decimal(".019850"), "reserve")
    within_budget(Decimal(0), rows)
    return frozen


def checkout():
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

    require(not git("status", "--porcelain"), "dirty checkout")
    require(
        git("remote", "get-url", "origin").removesuffix(".git")
        == "https://github.com/chase-sinclair/ai-evaluation-lab",
        "repository",
    )
    require(git("rev-parse", "HEAD^") == BASE, "dispatcher must directly extend approved commit")
    additions = {"scripts/acquire_recovery.py", "tests/test_acquire_recovery.py"}
    require(
        set(git("diff", "--name-only", BASE, "HEAD").splitlines()) == additions, "source revision"
    )
    return git("rev-parse", "HEAD")


def account(raw, row):
    require(
        raw.get("status") == "completed"
        and not raw.get("error")
        and not raw.get("incomplete_details"),
        "response incomplete or failed",
    )
    require(raw.get("model") == MODEL and raw.get("service_tier") == "default", "model or tier")
    require(raw.get("max_output_tokens", 512) == 512, "unexpected output setting")
    options = raw.get("prompt_cache_options") or {}
    require(
        options.get("ttl") in (None, "30m")
        and options.get("mode") in (None, "implicit")
        and not options.get("prewarm"),
        "cache policy",
    )
    usage = normalize_usage(raw)
    require(usage is not None and usage.uncached_input_tokens is not None, "usage partition")
    u = raw["usage"]
    detail = u["input_tokens_details"]
    i, o, read, write = (
        u["input_tokens"],
        u["output_tokens"],
        detail["cached_tokens"],
        detail["cache_write_tokens"],
    )
    require(
        all(type(v) is int and v >= 0 for v in (i, o, read, write, u["total_tokens"]))
        and read + write <= i
        and i + o == u["total_tokens"]
        and i <= row["input_allowance"]
        and o <= 512,
        "token accounting",
    )
    reasoning = (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
    require(type(reasoning) is int and 0 <= reasoning <= o, "reasoning tokens")
    splits = usage.cache.writes_by_ttl
    require(splits is None or (splits["12h"] == 0 and splits["30m"] == write), "write lifetime")
    return (
        Decimal(".10") * (i - read - write)
        + Decimal(".01") * read
        + Decimal(".125") * write
        + Decimal(".50") * o
    ) / 1000000


def proposal(raw):
    calls = [x for x in raw["output"] if x.get("type") == "function_call"]
    if len(calls) != 1:
        return None
    call = calls[0]
    try:
        args = parse_arguments(call["arguments"])
    except (TypeError, ValueError, KeyError):
        args = None
    return {"name": call.get("name"), "arguments": args}


class WireGuard:
    def __init__(self):
        self.pending = None

    def check(self, req):
        row = self.pending
        self.pending = None
        require(row is not None and req.method == "POST" and str(req.url) == URL, "unapproved HTTP")
        outgoing = parse_arguments(req.content)
        require(
            outgoing == row["body"] and digest(outgoing) == row["body_sha256"], "wire body mismatch"
        )


def acquire(approval, results, *, mock_transport=None):
    frozen = preflight(approval)
    rows = frozen["requests"]
    require(not (results / RUN).exists(), "run directory already used")
    if mock_transport is None:
        require(results.resolve() == (ROOT / "results").resolve(), "fixed live directory")
        revision = checkout()
        with openai.OpenAI(
            base_url="https://api.openai.com/v1", max_retries=0, timeout=30
        ) as access:
            require(access.models.retrieve(MODEL).id == MODEL, "model access")
    else:
        require(isinstance(mock_transport, httpx.MockTransport), "local test transport only")
        revision = "mock"
    store = ResultStore(results, RUN)
    store.write(
        "approval.json",
        dict(
            revision=revision,
            digest=approval,
            file_hash=FILE_HASH,
            planned=24,
            retries=0,
            reserve="0.019850",
            cap="0.025",
        ),
    )
    guard = WireGuard()
    spent = Decimal(0)
    seals = []
    ids = set()
    status = "interrupted"
    attempts = 0
    try:
        with (
            httpx.Client(
                transport=mock_transport,
                event_hooks={"request": [guard.check]},
                follow_redirects=False,
            ) as http,
            openai.OpenAI(
                api_key="offline" if mock_transport else None,
                base_url="https://api.openai.com/v1",
                http_client=http,
                max_retries=0,
                timeout=60,
            ) as client,
        ):
            for n, row in enumerate(rows):
                within_budget(spent, rows[n:])
                bound = dict(
                    index=n,
                    case=row["case"],
                    body_hash=row["body_sha256"],
                    checkpoint=row["checkpoint_sha256"],
                )
                store.write(f"intent-{n:02}.json", bound)
                attempts += 1
                guard.pending = row
                start = perf_counter()
                # The exact frozen body bypasses SDK parameter defaults and retains cache TTL.
                response = client.responses.with_raw_response.create(**row["body"])
                elapsed = (perf_counter() - start) * 1000
                raw = response.http_response.json()
                rec = {
                    **bound,
                    "raw": raw,
                    "http_request_id": response.headers.get("x-request-id"),
                    "latency_ms": elapsed,
                }
                store.write(f"receipt-{n:02}.json", rec)
                seals.append(digest(rec))
                require(guard.pending is None, "wire check bypassed")
                require(
                    isinstance(raw.get("id"), str) and raw["id"] and raw["id"] not in ids,
                    "missing or duplicate response ID",
                )
                ids.add(raw["id"])
                spent += account(raw, row)
                within_budget(spent, rows[n + 1 :])
        status = "completed"
    except BaseException as exc:
        if isinstance(exc, openai.APIStatusError):
            store.write(
                "http-error.json",
                {
                    "status": exc.status_code,
                    "http_request_id": exc.request_id,
                    "body": exc.response.text,
                    "index": attempts - 1,
                },
            )
        store.write(
            "failure.json",
            {
                "exception": type(exc).__name__,
                "reason": str(exc) if isinstance(exc, ValueError) else "acquisition interrupted",
            },
        )
        raise
    finally:
        store.write(
            "seal.json",
            dict(
                status=status,
                planned=24,
                attempts=attempts,
                receipts=seals,
                ledger_sha256=digest(seals),
                validated_cost_usd=str(spent),
            ),
        )
    return store.path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", required=True)
    parser.add_argument("--approval-digest", required=True)
    args = parser.parse_args()
    print(acquire(args.approval_digest, ROOT / "results"))
