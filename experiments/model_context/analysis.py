"""Read-only replay and scoring of the sealed Experiment 006 run.

The clarification reviewer receives only the masked worksheet: question and wording,
never model, context or draw.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from eval_lab.core.hashes import digest
from experiments.finops_sql.checkpoint import verify_sources
from experiments.finops_sql.episode import final
from experiments.finops_sql.grading import DIMENSIONS, grade
from experiments.finops_sql.packages import QUESTIONS
from experiments.finops_sql.v3.grading import sandbox

from .accounting import charge
from .proposal import CELLS, DRAWS, MODELS, cell_id

PAIRS = {
    # Headline: cheap model with context against expensive model without it.
    "luna-B_vs_sol-A": ("sol-A", "luna-B"),
    "sol-B_vs_luna-B": ("luna-B", "sol-B"),
    "sol-A_vs_luna-A": ("luna-A", "sol-A"),
    "luna-B_vs_luna-A": ("luna-A", "luna-B"),
    "sol-B_vs_sol-A": ("sol-A", "sol-B"),
}
QUESTION_IDS = [f"Q{n:02}" for n in range(1, 37)]


def require(test, message):
    if not test:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_bytes())


def answer_text(raw: dict) -> str:
    return "".join(
        c["text"]
        for x in raw.get("output", [])
        if x.get("type") == "message"
        for c in x.get("content", [])
        if c.get("type") == "output_text"
    )


def replay(folder: Path):
    """Verify the sealed ledger and return terminal answers and per-cell telemetry."""
    from scripts.acquire_model_context import APPROVAL, preflight

    plan, bodies = preflight(APPROVAL)
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
    served = defaultdict(set)
    seen = set()
    spent = Decimal(0)
    for i, (row, payload) in enumerate(zip(plan["requests"], bodies, strict=True), start=1):
        key = row["id"]
        cell = f"{row['model']}-{row['arm']}"
        if i > seal["requests_attempted"]:
            ends[key] = {"kind": "unsent"}
            continue
        ends[key] = {"kind": "interrupted"}
        prefix = folder / f"{i:03}"
        require(
            load(prefix.with_suffix(".request"))
            == dict(body=payload, hash=row["body_hash"], id=key)
            and load(prefix.with_suffix(".request-body")) == payload,
            "request binding",
        )
        event_path = prefix.with_suffix(".event")
        if not event_path.exists():
            # Only the last attempted request of a failed run can lack an event.
            require(
                i == seal["requests_attempted"] and seal["failure"] is not None, "missing event"
            )
            continue
        raw = load(prefix.with_suffix(".response-body"))
        receipt = load(prefix.with_suffix(".response"))
        require(
            receipt["raw"] == raw
            and receipt["body_hash"] == row["body_hash"]
            and raw["id"] not in seen,
            "response identity",
        )
        seen.add(raw["id"])
        cost = charge(raw, payload["model"], row["input_bound"])
        spent += cost
        event = load(event_path)
        require(
            Decimal(event["cost"]) == cost and event["model_latency"] == receipt["latency"],
            "event accounting",
        )
        u = raw["usage"]
        d = u["input_tokens_details"]
        stats[cell].update(
            dict(
                requests=1,
                input=u["input_tokens"],
                output=u["output_tokens"],
                reasoning=u["output_tokens_details"]["reasoning_tokens"],
                cache_read=d["cached_tokens"],
                cache_write=d["cache_write_tokens"],
                cost=cost,
                api_seconds=receipt["latency"],
            )
        )
        served[cell].add(raw["model"])
        if event.get("outcome") == "output_exhaustion":
            require(
                raw["status"] == "incomplete"
                and (raw.get("incomplete_details") or {}).get("reason") == "max_output_tokens"
                and raw.get("error") is None
                and u["output_tokens"] == payload["max_output_tokens"],
                "exhaustion evidence",
            )
            ends[key] = {"kind": "output_exhaustion"}
            continue
        require(
            raw["status"] == "completed"
            and not raw.get("incomplete_details")
            and not raw.get("error"),
            "completion evidence",
        )
        calls = [x for x in raw.get("output", []) if x.get("type") == "function_call"]
        text = answer_text(raw)
        answer = (
            {"kind": "invalid_proposals"} if calls else final(text) if text else {"kind": "missing"}
        )
        require(answer == event["final"], "terminal evidence")
        ends[key] = answer
    kinds = Counter(a["kind"] for a in ends.values())
    require(
        spent == Decimal(seal["accounted_usd"])
        and kinds["output_exhaustion"] == seal["exhausted"]
        and kinds["unsent"] == len(bodies) - seal["requests_attempted"],
        "seal counts",
    )
    return ends, stats, {k: sorted(v) for k, v in served.items()}


def worksheet(ends: dict) -> dict:
    """Distinct clarification wordings that need human adequacy review, fully masked."""
    items = {}
    for key, a in ends.items():
        n = int(key[1:3])
        if a["kind"] == "clarify" and n in DIMENSIONS and set(a["dimensions"]) == DIMENSIONS[n]:
            item = dict(question=QUESTIONS[n - 1]["question"], wording=a["question"])
            items[digest(item)] = item | {"adequate": None}
    return dict(sorted(items.items()))


def score(ends: dict, root: Path, review: dict, run_sql=sandbox) -> dict:
    """Business correctness per request id. None marks an unsent or interrupted request."""
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
        folder = root / name
        before = verify_sources(folder)
        runs[name] = run_sql(folder, sql) if sql else {}
        require(verify_sources(folder) == before, "snapshot drift")
    cases = {}
    for key, a in ends.items():
        if a["kind"] in ("unsent", "interrupted"):
            cases[key] = None
            continue
        n = int(key[1:3])
        g = grade(n, a, root, execute=lambda f, _, k=key: {"candidate": runs[f.name][k]})
        passed = g["business_correct"]
        if passed is None:
            passed = review[
                digest(dict(question=QUESTIONS[n - 1]["question"], wording=a["question"]))
            ]["adequate"]
        cases[key] = bool(passed)
    return cases


def summarize(cases: dict, ends: dict, stats: dict) -> dict:
    """Pure aggregation over per-request correctness. No grading or I/O."""
    cells = {}
    for model, arm in CELLS:
        cell = f"{model}-{arm}"
        per_draw = {}
        for d in range(1, DRAWS + 1):
            keys = [cell_id(q, model, arm, d) for q in QUESTION_IDS]
            outcomes = [cases[k] for k in keys]
            per_draw[d] = dict(
                correct=[sum(1 for x in outcomes if x), 36],
                acquired=sum(1 for x in outcomes if x is not None),
                kinds=Counter(ends[k]["kind"] for k in keys),
            )
        complete = [v["correct"][0] for v in per_draw.values() if v["acquired"] == 36]
        stability = Counter()
        for q in QUESTION_IDS:
            got = [cases[cell_id(q, model, arm, d)] for d in range(1, DRAWS + 1)]
            if None in got:
                stability["incomplete"] += 1
            else:
                stability[{DRAWS: "all_draws", 0: "no_draws"}.get(sum(got), "some_draws")] += 1
        total = sum(v["correct"][0] for v in per_draw.values())
        cost = stats.get(cell, Counter()).get("cost", Decimal(0))
        cells[cell] = dict(
            model=MODELS[model],
            context={"A": "schema", "B": "curated"}[arm],
            draws=per_draw,
            complete_draw_scores=complete,
            mean_correct=(str(Decimal(sum(complete)) / len(complete)) if complete else None),
            range=[min(complete), max(complete)] if complete else None,
            stability=stability,
            usd=str(cost),
            usd_per_correct=str(cost / total) if total else None,
            telemetry=stats.get(cell, Counter()),
        )
    paired = {}
    for name, (base, other) in PAIRS.items():
        counts = Counter()
        rows = {}
        for d in range(1, DRAWS + 1):
            for q in QUESTION_IDS:
                x = cases[cell_id(q, *base.split("-"), d)]
                y = cases[cell_id(q, *other.split("-"), d)]
                outcome = (
                    "unpaired" if None in (x, y) else "tie" if x == y else "gain" if y else "loss"
                )
                counts[outcome] += 1
                rows[f"{q}-{d}"] = outcome
        paired[name] = dict(baseline=base, comparison=other, counts=counts, cases=rows)
    return dict(cells=cells, paired=paired)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--snapshots", type=Path)
    args = parser.parse_args()
    if args.review is not None and args.snapshots is None:
        parser.error("--review requires --snapshots")
    ends, stats, served = replay(args.folder)
    if args.review is None:
        result = worksheet(ends)
    else:
        cases = score(ends, args.snapshots, load(args.review))
        result = summarize(cases, ends, stats) | {"served_models": served}
        seal_path = args.folder / "seal.json"
        seal = load(seal_path)
        result["acquisition"] = {k: v for k, v in seal.items() if k != "files"}
        result["acquisition"]["seal_sha256"] = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2, default=str))
