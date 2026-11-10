"""Single-use Experiment 004 dispatcher. Run as a module from the clean checkout."""

import argparse
import hashlib
import json
import subprocess
from decimal import Decimal
from time import perf_counter

import httpx
import openai

from eval_lab.core.hashes import canonical, digest
from eval_lab.core.result_store import ResultStore
from eval_lab.providers.openai_adapter import normalize_usage
from experiments.recovery import study
from scripts import acquire_recovery as original

BASE = "ae4c116cf23860b2f44d4bcd90c0ca22353fb70b"
APPROVAL = "68575ca194e925d3ace007b08f98b6704ff4bcbd84e011be6d9ece2df96bcb24"
FILE_HASH = "6f8b6e914a1f06f5b024d77e643d60ce8f19e3d788589c7b56977cdde60554c1"
RUN = "recovery-followup-2048-once"
ROOT = study.HERE.parents[1]
MODEL = "gpt-6-luna"
CAP = Decimal(".05")
URL = "https://api.openai.com/v1/responses"


def require(test, message):
    if not test:
        raise ValueError(message)


def reserve(row):
    return (Decimal(".125") * row["input_allowance"] + 1024) / 1000000


def within_budget(spent, remaining):
    require(spent + sum(map(reserve, remaining)) <= CAP, "remaining budget exceeded")


def preflight(approval):
    require(approval == APPROVAL, "explicit digest approval required")
    file = study.HERE / "request-manifest-2048.json"
    require(hashlib.sha256(file.read_bytes()).hexdigest() == FILE_HASH, "manifest file hash")
    frozen = json.loads(file.read_bytes())
    require(digest(frozen) == APPROVAL, "manifest approval mismatch")
    parent = original.preflight(original.APPROVAL)
    rows = frozen["requests"]
    for row, first in zip(rows, parent["requests"], strict=True):
        expected = first["body"] | {"max_output_tokens": 2048}
        size = len(canonical(expected).encode())
        require(
            row
            == first
            | {
                "body": expected,
                "body_sha256": digest(expected),
                "serialized_bytes": size,
                "input_allowance": size + 256,
                "output_allowance": 2048,
            },
            "parent body or binding mismatch",
        )
    require(sum(map(reserve, rows)) == Decimal("0.038285"), "reserve")
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
    additions = {
        "scripts/acquire_recovery_followup.py",
        "tests/test_acquire_recovery_followup.py",
        "experiments/recovery/request-manifest-2048.json",
        "docs/experiment04_followup_plan.md",
        "docs/PROGRESS.md",
        "docs/verification.md",
    }
    require(
        set(git("diff", "--name-only", BASE, "HEAD").splitlines()) == additions, "source revision"
    )
    return git("rev-parse", "HEAD")


def account(raw, row):
    require(raw.get("model") == MODEL and raw.get("service_tier") == "default", "model or tier")
    require(raw.get("max_output_tokens", 2048) == 2048, "unexpected output setting")
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
        and o <= 2048,
        "token accounting",
    )
    reasoning = (u.get("output_tokens_details") or {}).get("reasoning_tokens")
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
    require(
        raw.get("status") == "completed"
        and not raw.get("incomplete_details")
        and not raw.get("error"),
        "ineligible for replay",
    )
    return original.proposal(raw)


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
            reserve="00.038285",
            cap="0.05",
        ),
    )
    guard = original.WireGuard()
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
                require(
                    raw.get("status") == "completed"
                    and not raw.get("error")
                    and not raw.get("incomplete_details"),
                    "response incomplete or failed",
                )
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
