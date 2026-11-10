"""Offline audit and local business simulation of the sealed Experiment 004 acquisition."""

import json
from collections import Counter
from decimal import Decimal
from statistics import median

from eval_lab.core.hashes import digest
from experiments.recovery import offline, rules, study
from scripts import acquire_recovery as live


def read(path):
    return json.loads(path.read_bytes())


def audit(directory):
    plan = live.preflight(live.APPROVAL)
    seal = read(directory / "seal.json")
    approval = read(directory / "approval.json")
    live.require(
        approval["digest"] == live.APPROVAL
        and approval["file_hash"] == live.FILE_HASH
        and approval["planned"] == seal["planned"] == 24
        and approval["retries"] == 0,
        "approval",
    )
    live.require(
        seal["attempts"] == len(list(directory.glob("intent-*.json")))
        and len(seal["receipts"]) <= seal["attempts"] <= 24,
        "attempt count",
    )
    rows = plan["requests"]
    cases = {r["id"]: r for r in study.inventory()}
    hashes = seal["receipts"]
    live.require(
        digest(hashes) == seal["ledger_sha256"]
        and len(hashes) == len(list(directory.glob("receipt-*.json"))),
        "receipt ledger",
    )
    records, details = [], []
    ids = set()
    total = Decimal(0)
    totals = Counter()
    received = []
    for n, row in enumerate(rows):
        case = cases[row["case"]]
        source, checkpoint = study.checkpoint(case)
        view = source["public"]
        for arm, p in (("A", rules.stop(rules.status(view))), ("B", rules.decide(view))):
            records.append(offline.replay(case, source, arm, p, 0))
        if n >= len(hashes):
            continue
        r = read(directory / f"receipt-{n:02}.json")
        raw = r["raw"]
        bound = dict(index=n, case=case["id"], body_hash=row["body_sha256"], checkpoint=checkpoint)
        live.require(
            read(directory / f"intent-{n:02}.json") == bound
            and all(r[k] == v for k, v in bound.items())
            and digest(r) == hashes[n],
            "receipt binding",
        )
        live.require(raw["id"] not in ids, "duplicate response ID")
        ids.add(raw["id"])
        usage = raw["usage"]
        cache = usage["input_tokens_details"]
        i, o = usage["input_tokens"], usage["output_tokens"]
        read_count, write_count = cache["cached_tokens"], cache["cache_write_tokens"]
        live.require(
            0 <= read_count + write_count <= i <= row["input_allowance"]
            and 0 <= o <= 512
            and i + o == usage["total_tokens"],
            "observed usage",
        )
        live.require(
            raw["model"] == live.MODEL
            and raw["service_tier"] == "default"
            and (raw.get("prompt_cache_options") or {}).get("ttl") in (None, "30m")
            and (cache.get("cache_write_tokens_details") or {}).get("ttl_12h_tokens", 0) == 0,
            "observed policy",
        )
        observed_cost = (
            Decimal(".1") * (i - read_count - write_count)
            + Decimal(".01") * read_count
            + Decimal(".125") * write_count
            + Decimal(".5") * o
        ) / 1000000
        received.append(
            dict(
                case=row["case"],
                id=raw["id"],
                http_id=r["http_request_id"],
                status=raw["status"],
                reason=raw.get("incomplete_details"),
                latency_ms=r["latency_ms"],
                cost=str(observed_cost),
                usage=usage,
            )
        )
        totals.update(
            input=i,
            output=o,
            read=read_count,
            write=write_count,
            reasoning=usage["output_tokens_details"]["reasoning_tokens"],
        )
        if raw["status"] != "completed":
            live.require(n == len(hashes) - 1 and seal["status"] == "interrupted", "bad receipt")
            continue
        amount = live.account(raw, row)
        total += amount
        p = live.proposal(raw)
        entry = offline.replay(case, source, "C", p, 0, raw)
        records.append(entry)

        details.append(
            dict(
                case=case["id"],
                correct=entry["correct"],
                status=entry["status"],
                proposal=p,
                rejection=entry["rejection"],
                syntax_valid=entry["syntax_valid"],
                outcome=entry["outcome"],
                latency_ms=r["latency_ms"],
                usage=usage,
                cost=str(amount),
            )
        )
    live.require(total == Decimal(seal["validated_cost_usd"]), "spending reconciliation")
    summary = offline.summarize(records)
    for arm in "ABC":
        for mock_field in (
            "local_decision_ms",
            "mock_requests",
            "estimated_inference_usd",
            "observed_model_tokens",
            "paid_requests",
        ):
            summary[arm].pop(mock_field)
    times = [r["latency_ms"] for r in received]
    return dict(
        paired=summary,
        cases=details,
        records=records,
        attempts=seal["attempts"],
        validated=len(details),
        tokens=dict(totals),
        received=received,
        completed_cost=str(total),
        cost=str(sum(Decimal(r["cost"]) for r in received)),
        provider_invoice=None,
        latency_ms=dict(total=sum(times), median=median(times), min=min(times), max=max(times))
        if times
        else None,
        ledger=seal["ledger_sha256"],
        seal_sha256=digest(seal),
    )


if __name__ == "__main__":
    report = audit(live.ROOT / "results" / live.RUN)
    live.require(
        report["seal_sha256"] == "4ef114dd718e78c1641820656bd75aab039b9a646853f9d320332494ca759c59",
        "historical seal",
    )
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2))
