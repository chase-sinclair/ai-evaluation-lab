"""Offline descriptive audit. Prints the development appendix; never constructs requests."""

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

from experiments.entity_matching.ror.core import ABSTAIN, decision, features

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments/entity_matching/ror"
SEED = 31006
DRAWS = 20000


@dataclass(frozen=True)
class Visible:
    case: str
    top: float
    margin: float
    distance: float
    prediction: str


def orders(rows: list[Visible]) -> dict[str, list[str]]:
    keys = {
        "Frozen distance": lambda r: r.distance,
        "Narrowest margin": lambda r: r.margin,
        "Weakest leader": lambda r: r.top,
        "Abstentions first": lambda r: (r.prediction != ABSTAIN, r.distance),
    }
    return {
        name: [r.case for r in sorted(rows, key=lambda r: (key(r), r.case))]
        for name, key in keys.items()
    }


def read_inputs():
    data = json.loads((DATA / "dataset.json").read_text(encoding="utf8"))
    baseline = json.loads((DATA / "baseline.json").read_text(encoding="utf8"))
    manifest = json.loads((DATA / "phase3e_requests.json").read_text(encoding="utf8"))
    expected = {r["id"]: r for r in baseline["query_decisions"]}
    visible = []
    audit = {}
    for r in data["rows"]:
        if r["review"] == "excluded":
            continue
        seq = r["seq_no"]
        case = f"cr-{seq}"
        top, margin = features(r)
        p, d = decision(r, baseline["calibration"]["thresholds"])
        visible.append(Visible(case, top, margin, d, p))
        y = next(iter(r["output"]), ABSTAIN)
        offered = [c["id"] for c in r["candidates"]]
        if (p, y, y in offered) != (
            expected[seq]["prediction"],
            expected[seq]["target"],
            expected[seq]["available"],
        ):
            raise ValueError(f"Mismatch with frozen grade: {case}")
        audit[case] = dict(
            query=r["query"],
            prediction=p,
            target=y,
            rank=r["full_registry_target_rank"],
            error=p != y,
            correctable=p != y and (y == ABSTAIN or y in offered),
        )
    if len(expected) != len(visible):
        raise ValueError("Baseline population mismatch")
    return (
        visible,
        audit,
        {r["case_id"] for r in manifest["requests"][: manifest["executable_prefix"]]},
    )


def counts(ids, audit):
    return (sum(audit[i]["error"] for i in ids), sum(audit[i]["correctable"] for i in ids))


def random_reference(ids, audit, ks):
    rng = random.Random(SEED)
    # A single without-replacement permutation per draw keeps all budgets nested.
    population = sorted(ids)
    samples = {k: [[], []] for k in ks}
    for _ in range(DRAWS):
        draw = rng.sample(population, len(population))
        for k in ks:
            for sample, n in zip(samples[k], counts(draw[:k], audit), strict=True):
                sample.append(n)
    return {
        k: [
            (
                sum(a) / DRAWS,
                sorted(a)[math.ceil(0.025 * DRAWS) - 1],
                sorted(a)[math.ceil(0.975 * DRAWS) - 1],
            )
            for a in both
        ]
        for k, both in samples.items()
    }


def appendix():
    rows, audit, pilot = read_inputs()
    out = [
        "# Development allocation audit",
        "",
        "E counts selected baseline errors. C counts selected errors whose correct action is "
        "available (an offered true ID or abstention). G counts correct baseline decisions "
        "exposed to possible regression. Every measurement in these tables is offline.",
        "",
    ]
    for title, subset in (
        ("All development queries", rows),
        ("Four acquired cases omitted", [r for r in rows if r.case not in pilot]),
    ):
        order = orders(subset)
        n = len(subset)
        ids = order["Frozen distance"]
        ks = [n // 4, n // 2]
        out.extend(
            [
                f"## {title}",
                "",
                "| Ordering | Calls | E | C | G | C per call |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for name, ranking in order.items():
            for k in ks:
                e, c = counts(ranking[:k], audit)
                out.append(f"| {name} | {k} | {e} | {c} | {k - e} | {c / k:.3f} |")
        out.extend(
            [
                "",
                "| Random calls | Exact expected E / C | Simulated E, mean [central 95%] "
                "| Simulated C, mean [central 95%] |",
                "|---:|---:|---:|---:|",
            ]
        )
        for k, (e, c) in random_reference(ids, audit, ks).items():
            te, tc = counts(ids, audit)
            out.append(
                f"| {k} | {k * te / n:.3f} / {k * tc / n:.3f} | "
                f"{e[0]:.3f} [{e[1]}, {e[2]}] | {c[0]:.3f} [{c[1]}, {c[2]}] |"
            )
        out.append("")
    out.extend(
        [
            "## All 38 in frozen escalation order",
            "",
            "Target rank is the position in the full-registry retrieval. Ranks 1–5 were offered. "
            "A dash denotes a reviewed no-match. Scores are rounded for display. "
            "Sorting used the frozen precision.",
            "",
            "| Rank | ID | Deposited name | Leader | Runner-up | Gap | Distance | "
            "Baseline | Target rank | Assessment |",
            "|---:|---|---|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    by_id = {r.case: r for r in rows}
    for rank, i in enumerate(orders(rows)["Frozen distance"], 1):
        v = by_id[i]
        a = audit[i]
        assessment = (
            "correct"
            if not a["error"]
            else "selection error"
            if a["correctable"]
            else "retrieval miss"
        )
        pred = "abstain" if v.prediction == ABSTAIN else "link"
        out.append(
            f"| {rank} | {i} | {a['query']} | {v.top:.4f} | {v.top - v.margin:.4f} | "
            f"{v.margin:.4f} | {v.distance:.4f} | {pred} | {a['rank'] or '—'} | {assessment} |"
        )
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    print(appendix(), end="")
