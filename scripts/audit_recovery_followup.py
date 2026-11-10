"""Reconstruct the separately approved 2048-token acquisition offline."""

import json
from collections import Counter
from decimal import Decimal
from statistics import median

from eval_lab.core.hashes import digest
from experiments.recovery import offline, rules, study
from scripts import acquire_recovery_followup as live


def audit(directory):
    def read(name):
        return json.loads((directory / name).read_bytes())

    plan = live.preflight(live.APPROVAL)
    seal = read("seal.json")
    approved = read("approval.json")
    live.require(
        {**approved, "reserve": Decimal(approved["reserve"])}
        == dict(
            cap="0.05",
            digest=live.APPROVAL,
            file_hash=live.FILE_HASH,
            planned=24,
            reserve=Decimal("0.038285"),
            retries=0,
            revision="8a4074b632fdf6546ef078274161debe8f560906",
        ),
        "approval",
    )
    hashes = seal["receipts"]
    live.require(
        len(hashes) == len(list(directory.glob("receipt-*.json")))
        and seal["attempts"] == len(list(directory.glob("intent-*.json")))
        and len(hashes) <= seal["attempts"] <= seal["planned"] == 24
        and digest(hashes) == seal["ledger_sha256"],
        "ledger",
    )
    if seal["status"] == "completed":
        live.require(len(hashes) == 24, "incomplete ledger")
    inventory = {r["id"]: r for r in study.inventory()}
    records, receipts = [], []
    ids = set()
    http_ids = set()
    tokens = Counter()
    cost = Decimal(0)
    for n, row in enumerate(plan["requests"]):
        case = inventory[row["case"]]
        src, checkpoint = study.checkpoint(case)
        view = src["public"]
        for arm, action in (("A", rules.stop(rules.status(view))), ("B", rules.decide(view))):
            records.append(offline.replay(case, src, arm, action, 0))
        bound = dict(index=n, case=row["case"], body_hash=row["body_sha256"], checkpoint=checkpoint)
        if n < seal["attempts"]:
            live.require(read(f"intent-{n:02}.json") == bound, "intent")
        if n >= len(hashes):
            continue
        r = read(f"receipt-{n:02}.json")
        raw = r["raw"]
        live.require(all(r[k] == v for k, v in bound.items()) and digest(r) == hashes[n], "binding")
        live.require(
            raw["id"]
            and raw["id"] not in ids
            and r["http_request_id"]
            and r["http_request_id"] not in http_ids,
            "response identity",
        )
        ids.add(raw["id"])
        http_ids.add(r["http_request_id"])
        amount = live.account(raw, row)
        cost += amount
        u = raw["usage"]
        cache = u["input_tokens_details"]
        tokens.update(
            input=u["input_tokens"],
            output=u["output_tokens"],
            reasoning=u["output_tokens_details"]["reasoning_tokens"],
            read=cache["cached_tokens"],
            write=cache["cache_write_tokens"],
        )
        receipts.append(
            dict(
                case=row["case"],
                status=raw["status"],
                reason=raw.get("incomplete_details"),
                cost=str(amount),
                ms=r["latency_ms"],
                usage=u,
                hash=hashes[n],
            )
        )
        if raw["status"] == "completed":
            records.append(offline.replay(case, src, "C", live.proposal(raw), 0, raw))
        else:
            live.require(
                seal["status"] == "interrupted" and n == len(hashes) - 1, "continued after stop"
            )
    live.require(cost == Decimal(seal["validated_cost_usd"]) <= live.CAP, "cost reconciliation")
    summary = offline.summarize(records)
    for arm in "ABC":
        for field in (
            "mock_requests",
            "paid_requests",
            "estimated_inference_usd",
            "local_decision_ms",
            "observed_model_tokens",
        ):
            summary[arm].pop(field)
    times = [x["ms"] for x in receipts]
    return dict(
        summary=summary,
        records=records,
        receipts=receipts,
        tokens=dict(tokens),
        cost=str(cost),
        ms={"total": sum(times), "median": median(times), "min": min(times), "max": max(times)}
        if times
        else {},
        seal=digest(seal),
        ledger=seal["ledger_sha256"],
    )


if __name__ == "__main__":
    r = audit(live.ROOT / "results" / live.RUN)
    live.require(
        r["seal"] == "29c351eb5543708b3957e54235a9064084b467397566244a8d25a643bb96bd70",
        "historical seal",
    )
    print(json.dumps(r, indent=2))
