"""Read-only replay and scoring of the sealed Experiment 007 run.

Grading reuses Experiment 006's frozen worksheet and scoring functions unchanged. The
clarification reviewer receives only the masked worksheet. Items whose question and wording
exactly match an owner-accepted Experiment 006 judgment carry that judgment over.
"""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from eval_lab.core.hashes import digest
from experiments.model_context.analysis import score, worksheet
from experiments.model_context.proposal import cell_id

from .accounting import charge, terminal
from .proposal import MODELS

QUESTION_IDS = [f"Q{n:02}" for n in range(1, 37)]
CELLS = [(m, a) for m in MODELS for a in ("A", "B")]
PAIRS = {
    # Pre-registered headline: cheap model with context against expensive model without.
    "haiku-B_vs_sonnet-A": ("sonnet-A", "haiku-B"),
    "sonnet-B_vs_haiku-B": ("haiku-B", "sonnet-B"),
    "sonnet-A_vs_haiku-A": ("haiku-A", "sonnet-A"),
    "haiku-B_vs_haiku-A": ("haiku-A", "haiku-B"),
    "sonnet-B_vs_sonnet-A": ("sonnet-A", "sonnet-B"),
}


def require(test, message):
    if not test:
        raise ValueError(message)


def load(path: Path):
    return json.loads(path.read_bytes())


def replay(folder: Path):
    """Verify the sealed ledger. Returns terminal answers, per-cell telemetry, served models."""
    from scripts.acquire_claude_context import APPROVAL, preflight

    plan, bodies = preflight(APPROVAL)
    seal = load(folder / "seal.json")
    hashes = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in folder.iterdir()
        if f.name != "seal.json"
    }
    require(hashes == seal["files"] and digest(hashes) == seal["ledger_hash"], "ledger integrity")
    require(load(folder / "plan.json")["digest"] == APPROVAL, "proposal identity")
    ends, stats, served = {}, defaultdict(Counter), defaultdict(set)
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
        headers = load(prefix.with_suffix(".request-headers"))
        require(set(headers) <= {"anthropic-version", "anthropic-beta", "content-type"}, "headers")
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
        stats[cell].update(
            dict(
                requests=1,
                input=u["input_tokens"],
                cache_read=u["cache_read_input_tokens"],
                cache_write=u["cache_creation_input_tokens"],
                output=u["output_tokens"],
                thinking=(u.get("output_tokens_details") or {}).get("thinking_tokens") or 0,
                cost=cost,
                api_seconds=receipt["latency"],
            )
        )
        served[cell].add(raw["model"])
        answer = terminal(raw)
        if answer["kind"] == "output_exhaustion":
            require(event.get("outcome") == "output_exhaustion", "exhaustion evidence")
        elif answer["kind"] == "refusal":
            require(
                event.get("outcome") == "refusal" and event["final"] == answer, "refusal evidence"
            )
        else:
            require(answer == event["final"], "terminal evidence")
        ends[key] = answer
    kinds = Counter(a["kind"] for a in ends.values())
    require(
        spent == Decimal(seal["accounted_usd"])
        and kinds["output_exhaustion"] == seal["exhausted"]
        and kinds["refusal"] == seal["refused"]
        and kinds["unsent"] == len(bodies) - seal["requests_attempted"],
        "seal counts",
    )
    return ends, stats, {k: sorted(v) for k, v in served.items()}


def prefill(sheet: dict, accepted: dict) -> tuple[dict, list[str]]:
    """Carry over owner-accepted judgments for identical question and wording pairs."""
    out, reused = {}, []
    for key, item in sheet.items():
        prior = accepted.get(key)
        if prior is not None:
            require(
                {k: prior[k] for k in ("question", "wording")}
                == {k: item[k] for k in ("question", "wording")}
                and type(prior["adequate"]) is bool,
                "prior judgment binding",
            )
            out[key] = item | {"adequate": prior["adequate"]}
            reused.append(key)
        else:
            out[key] = item
    return out, reused


def summarize(cases: dict, ends: dict, stats: dict) -> dict:
    """Pure aggregation over per-request correctness. No grading or I/O."""
    cells = {}
    for model, arm in CELLS:
        cell = f"{model}-{arm}"
        per_draw = {}
        for d in (1, 2, 3):
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
            got = [cases[cell_id(q, model, arm, d)] for d in (1, 2, 3)]
            if None in got:
                stability["incomplete"] += 1
            else:
                stability[{3: "all_draws", 0: "no_draws"}.get(sum(got), "some_draws")] += 1
        total = sum(v["correct"][0] for v in per_draw.values())
        cost = stats.get(cell, Counter()).get("cost", Decimal(0))
        cells[cell] = dict(
            model=MODELS[model],
            context={"A": "schema", "B": "curated"}[arm],
            draws=per_draw,
            complete_draw_scores=complete,
            mean_correct=str(Decimal(sum(complete)) / len(complete)) if complete else None,
            range=[min(complete), max(complete)] if complete else None,
            stability=stability,
            usd=str(cost),
            usd_per_correct=str(cost / total) if total else None,
            telemetry=stats.get(cell, Counter()),
        )
    paired = {}
    for name, (base, other) in PAIRS.items():
        counts, rows = Counter(), {}
        for d in (1, 2, 3):
            for q in QUESTION_IDS:
                x = cases[cell_id(q, *base.split("-"), d)]
                y = cases[cell_id(q, *other.split("-"), d)]
                outcome = (
                    "unpaired" if None in (x, y) else "tie" if x == y else "gain" if y else "loss"
                )
                counts[outcome] += 1
                rows[f"{q}-{d}"] = outcome
        paired[name] = dict(baseline=base, comparison=other, counts=counts, cases=rows)
    return dict(cells=cells, paired=paired, replication=criteria(cells, paired))


def criteria(cells: dict, paired: dict) -> dict:
    """The design's pre-registered replication criteria, evaluated per draw."""

    def scores(cell):
        return [cells[cell]["draws"][d]["correct"][0] for d in (1, 2, 3)]

    complete = all(cells[c]["draws"][d]["acquired"] == 36 for c in cells for d in (1, 2, 3))
    cheap, rich = scores("haiku-B"), scores("sonnet-A")
    head = paired["haiku-B_vs_sonnet-A"]["counts"]
    primary = all(x > y for x, y in zip(cheap, rich, strict=True))
    context = all(
        b > a for m in MODELS for a, b in zip(scores(f"{m}-A"), scores(f"{m}-B"), strict=True)
    )
    return dict(
        all_draws_complete=complete,
        primary_haiku_curated_beats_sonnet_schema_every_draw=primary,
        primary_draws=dict(haiku_B=cheap, sonnet_A=rich),
        secondary_context_raises_each_model_every_draw=context,
        secondary_paired_gains_exceed_losses=head["gain"] > head["loss"],
        paired_counts=head,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--prior-review", type=Path, help="owner-accepted 006 judgments")
    parser.add_argument("--review", type=Path, help="completed 007 worksheet")
    parser.add_argument("--snapshots", type=Path)
    args = parser.parse_args()
    if args.review is not None and args.snapshots is None:
        parser.error("--review requires --snapshots")
    ends, stats, served = replay(args.folder)
    if args.review is None:
        sheet = worksheet(ends)
        accepted = load(args.prior_review) if args.prior_review else {}
        result, reused = prefill(sheet, accepted)
        result = {"items": result, "reused_from_006": reused}
    else:
        cases = score(ends, args.snapshots, load(args.review))
        result = summarize(cases, ends, stats) | {"served_models": served}
        seal_path = args.folder / "seal.json"
        seal = load(seal_path)
        result["acquisition"] = {k: v for k, v in seal.items() if k != "files"}
        result["acquisition"]["seal_sha256"] = hashlib.sha256(seal_path.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2, default=str))
