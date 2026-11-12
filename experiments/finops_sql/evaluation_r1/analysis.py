"""Read-only replay of a sealed full evaluation. The reviewer receives only the worksheet."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from eval_lab.core.hashes import digest
from scripts.acquire_recovery import require

from ..checkpoint import verify_sources
from ..episode import Discovery, final
from ..grading import DIMENSIONS, grade
from ..packages import QUESTIONS
from ..pilot_v3_1.accounting import charge
from ..v3.grading import sandbox
from ..v3.proposal import body, reserve


def load(path):
    return json.loads(path.read_bytes())


def replay(folder):
    from scripts.acquire_finops_evaluation import APPROVAL, preflight

    plan, initials = preflight(APPROVAL)
    seal = load(folder / "seal.json")
    hashes = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in folder.iterdir()
        if f.name != "seal.json"
    }
    require(hashes == seal["files"] and digest(hashes) == seal["ledger_hash"], "ledger integrity")
    require(load(folder / "plan.json")["digest"] == APPROVAL, "proposal identity")
    ends = {}
    stats = defaultdict(Counter)
    depths = {}
    seen = set()
    i = 0
    accounted = 0
    remaining = Decimal(plan["reserve_usd"])
    questions = {q["id"]: q for q in QUESTIONS}
    for row, initial in zip(plan["requests"], initials, strict=True):
        arm = row["arm"]
        q = row["question"]
        key = q + arm
        t = stats[arm]
        state = Discovery()
        bounds = row["turn_input_bounds"]
        ends[key] = {"kind": "unsent"}
        for turn, bound in enumerate(bounds):
            if i >= seal["requests_attempted"]:
                break
            i += 1
            t["requests"] += 1
            ends[key] = {"kind": "interrupted"}
            prefix = folder / f"{i:03}"

            def get(suffix, path=prefix):
                return load(path.with_suffix(suffix))

            payload = body(arm, questions[q], state.history)
            require(turn or initial == payload, "initial binding")
            if prefix.with_suffix(".request").exists():
                require(
                    get(".request")
                    == dict(
                        body=payload,
                        hash=digest(payload),
                        arm=arm,
                        question=q,
                        prior_history=digest(state.history),
                    ),
                    "request binding",
                )
            if prefix.with_suffix(".request-body").exists():
                require(get(".request-body") == payload, "wire binding")
            event_path = prefix.with_suffix(".event")
            if not event_path.exists():
                require(
                    i == seal["requests_attempted"] and seal["failure"] is not None, "missing event"
                )
                if seal["attempts_without_accounting"]:
                    break
            require(
                prefix.with_suffix(".request-body").exists()
                and prefix.with_suffix(".request").exists(),
                "missing bound request",
            )
            raw = get(".response-body")
            receipt = get(".response")
            require(
                receipt["raw"] == raw
                and receipt["body_hash"] == digest(payload)
                and raw["id"] not in seen,
                "response identity",
            )
            seen.add(raw["id"])
            cost = charge(raw, bound)
            accounted += 1
            remaining -= reserve(bound, 1)
            u = raw["usage"]
            d = u["input_tokens_details"]
            t.update(
                dict(
                    input=u["input_tokens"],
                    output=u["output_tokens"],
                    reasoning=u["output_tokens_details"]["reasoning_tokens"],
                    cache_read=d["cached_tokens"],
                    cache_write=d["cache_write_tokens"],
                    cost=cost,
                    api_seconds=receipt["latency"],
                )
            )
            if not event_path.exists():
                break
            e = get(".event")
            require(
                cost == Decimal(e["cost"]) and receipt["latency"] == e["model_latency"],
                "event accounting",
            )
            future = reserve(sum(bounds[turn + 1 :]), len(bounds[turn + 1 :]))
            if e.get("outcome") == "output_exhaustion":
                require(
                    raw["status"] == "incomplete"
                    and raw["incomplete_details"]["reason"] == "max_output_tokens"
                    and raw.get("error") is None
                    and u["output_tokens"] == 25000
                    and Decimal(e["released_future_usd"]) == future,
                    "exhaustion evidence",
                )
                ends[key] = {"kind": "output_exhaustion"}
            else:
                require(
                    raw["status"] == "completed"
                    and not raw.get("incomplete_details")
                    and not raw.get("error"),
                    "completion evidence",
                )
                calls = [x for x in raw["output"] if x["type"] == "function_call"]
                text = "".join(
                    c["text"]
                    for x in raw["output"]
                    if x["type"] == "message"
                    for c in x["content"]
                    if c["type"] == "output_text"
                )
                if "record" in e:
                    require(
                        payload.get("tools") and len(calls) == 1 and not text.strip(), "tool turn"
                    )
                    rec = state.select(calls[0]["name"], calls[0]["arguments"])
                    require(
                        rec == e["record"] and digest(state.history) == e["history"],
                        "discovery provenance",
                    )
                    t.update(
                        tools=1,
                        invalid_tools=int("error" in rec),
                        tool_seconds=e["discovery_latency"],
                    )
                    depths[key] = len(state.history)
                    continue
                ans = (
                    {"kind": "invalid_proposals"}
                    if calls
                    else final(text)
                    if text
                    else {"kind": "missing"}
                )
                require(ans == e["final"], "terminal evidence")
                ends[key] = ans
            require(e["depth"] == turn, "terminal depth")
            remaining -= future
            break
    kinds = Counter(a["kind"] for a in ends.values())
    require(
        sum(t["cost"] for t in stats.values()) == Decimal(seal["accounted_usd"])
        and remaining == Decimal(seal["remaining_reserve_usd"])
        and i - accounted == seal["attempts_without_accounting"]
        and i == seal["requests_attempted"]
        and sum(depths.values()) == seal["tools"]
        and kinds["output_exhaustion"] == seal["exhausted"]
        and len(ends) - sum(kinds[k] for k in ("output_exhaustion", "interrupted", "unsent"))
        == seal["finished"],
        "seal counts",
    )
    return (
        ends,
        stats,
        {k: depths.get(k, 0) for k in ends if k.endswith("D") and ends[k]["kind"] != "unsent"},
    )


def worksheet(ends):
    items = {}
    for key, a in ends.items():
        n = int(key[1:3])
        if a["kind"] == "clarify" and n in DIMENSIONS:
            item = dict(question=QUESTIONS[n - 1]["question"], wording=a["question"])
            items[digest(item)] = item | {"adequate": None}
    return dict(sorted(items.items()))


def report(ends, stats, depths, root, review):
    sheet = worksheet(ends)
    require(set(sheet) == set(review), "incomplete review inventory")
    for k, item in sheet.items():
        require(
            type(review[k].get("adequate")) is bool
            and review[k] == item | {"adequate": review[k]["adequate"]},
            "review binding",
        )
    sql = {k: a["query"] for k, a in ends.items() if a["kind"] == "sql"}
    runs = {}
    for name in ("evaluation_a", "evaluation_b"):
        f = root / name
        before = verify_sources(f)
        runs[name] = sandbox(f, sql) if sql else {}
        require(verify_sources(f) == before, "snapshot drift")
    cases = {}
    arms = {}
    for arm in "ABCD":
        c = Counter()
        correct = sql_ok = clar_ok = sensitivity = 0
        for n in range(1, 37):
            key = f"Q{n:02}{arm}"
            a = ends[key]
            kind = a["kind"]
            g = grade(n, a, root, execute=lambda f, _, k=key: {"candidate": runs[f.name][k]})
            passed = g["business_correct"]
            if passed is None:
                item = dict(question=QUESTIONS[n - 1]["question"], wording=a["question"])
                passed = review[digest(item)]["adequate"]
            c[kind] += 1
            c["sql_valid"] += int(g["sql_valid"] is True)
            c["sql_executed"] += int(g["execution_success"] is True)
            c["wrong_financial"] += int(n <= 32 and g["execution_success"] is True and not passed)
            c["over_refusal"] += int(n <= 32 and kind == "clarify")
            c["inappropriate_sql"] += int(n > 32 and kind == "sql")
            c["incomplete_clarification"] += int(n > 32 and kind == "clarify" and not passed)
            correct += passed
            sql_ok += passed and n <= 32
            clar_ok += passed and n > 32
            sensitivity += passed and n != 16
            cases[key] = g | {
                "business_correct": passed if kind not in ("unsent", "interrupted") else None
            }
        arms[arm] = dict(
            policy=[correct, 36],
            financial_sql=[sql_ok, 32],
            clarification=[clar_ok, 4],
            without_Q16=[sensitivity, 35],
            acquired=36 - c["unsent"] - c["interrupted"],
            counts=c,
            telemetry=stats[arm],
        )

    def pairs(a, b):
        rows = {}
        for n in range(1, 37):
            q = f"Q{n:02}"
            x, y = (cases[q + arm]["business_correct"] for arm in (a, b))
            rows[q] = "unpaired" if None in (x, y) else "tie" if x == y else "gain" if y else "loss"
        return dict(counts=Counter(rows.values()), questions=rows)

    return dict(
        arms=arms,
        cases=cases,
        discovery_depth=depths,
        paired={a + b: pairs(a, b) for a, b in ("AB", "AC", "BC")},
        discovery_vs_preloaded=pairs("B", "D"),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--snapshots", type=Path)
    args = parser.parse_args()
    if args.review is not None and args.snapshots is None:
        parser.error("--review requires --snapshots")
    ends, stats, depths = replay(args.folder)
    result = (
        worksheet(ends)
        if args.review is None
        else report(ends, stats, depths, args.snapshots, load(args.review))
    )
    if args.review is not None:
        seal_path = args.folder / "seal.json"
        seal = load(seal_path)
        result["acquisition"] = {k: v for k, v in seal.items() if k != "files"}
        result["acquisition"]["seal_sha256"] = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2, default=str))
