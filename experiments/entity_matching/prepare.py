"""Regenerate the development receipt and freeze a proposal without provider access."""

import argparse
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

import yaml

from eval_lab.contracts import ExperimentSpec
from eval_lab.contracts import TestCase as Case
from eval_lab.core.budgets import estimate_input_tokens, preflight
from eval_lab.core.hashes import digest
from eval_lab.core.runner import validate
from eval_lab.providers.openai_adapter import request_payload

from .experiment import LIMITS, PROMPT, THRESHOLD, Experiment, score, uncertainty
from .fetch_validation import BASE, CACHE, member
from .policies import metrics

DIR = Path(__file__).resolve().parent
FROZEN = DIR / "development.json"
SHAS = {
    20: "0dc43fadc5754e18c3fbaaf34977e0b91d8cc825e664039e0f527c617df0fdfe",
    50: "64764bc43ff4686c9ff6683b141d8af1e01faa7a5a9d072378dbf3d84c64302c",
    80: "892e8d39cc8230dce5039a4bded16be1237d5c5c37b94a37404226d349ef3df8",
}


def group(row):
    return (
        "match"
        if row["label"]
        else "hard_negative"
        if row["is_hard_negative"]
        else "other_negative"
    )


def select(rows, key, quotas, seen):
    remaining = quotas.copy()
    chosen = []
    for row in sorted(rows, key=lambda r: digest([key, r["pair_id"]])):
        a, b = row["id_left"], row["id_right"]
        g = group(row)
        if a == b or a in seen or b in seen or not remaining[g]:
            continue
        seen.update((a, b))
        remaining[g] -= 1
        chosen.append(row)
    if any(remaining.values()):
        raise ValueError("Insufficient disjoint eligible pairs")
    return chosen


def prepare(cache: Path = CACHE) -> tuple[dict, Experiment]:
    spec = ExperimentSpec.model_validate(yaml.safe_load((DIR / "pilot.yaml").read_text()))
    sources = []
    cohort = []
    pilots = []
    seen = set()
    buckets = {}
    for t, sha in SHAS.items():
        name = member(t)
        path = cache / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise ValueError("Validation file hash mismatch")
        with gzip.open(path, "rt", encoding="utf8") as stream:
            rows = list(map(json.loads, stream))
        counts = Counter(map(group, rows))
        if counts != {"match": 500, "hard_negative": 1000, "other_negative": 1000}:
            raise ValueError("Unexpected validation strata")
        sources.append(
            dict(
                member=name,
                archive=BASE + f"{t}pair.zip",
                sha256=sha,
                rows=len(rows),
                groups=counts,
            )
        )
        chosen = select(
            rows, "dev-v1", {"match": 12, "hard_negative": 24, "other_negative": 24}, seen
        )
        pilot_ids = {
            r["pair_id"]
            for r in select(
                chosen, "pilot-v1", {"match": 1, "hard_negative": 2, "other_negative": 1}, set()
            )
        }
        for r in chosen:
            source_id = r["pair_id"]
            assert source_id == f"{r['id_left']}#{r['id_right']}"
            y = r["label"]
            meta = dict(
                pair_id=source_id,
                id_left=r["id_left"],
                id_right=r["id_right"],
                cluster_id_left=r["cluster_id_left"],
                cluster_id_right=r["cluster_id_right"],
                is_hard_negative=r["is_hard_negative"],
                group=group(r),
                mixture=t,
                source_row_sha256=digest(r),
            )
            case = Case(
                id="wdc-" + source_id.replace("#", "-"),
                dataset_id=spec.dataset.id,
                dataset_version=spec.dataset.version,
                split="validation",
                provenance=meta,
                ground_truth={"label": y},
                task_input={
                    side: {k: r[f"{k}_{side}"] for k in LIMITS} for side in ("left", "right")
                },
            )
            s = score(case.task_input)
            pred = int(s >= THRESHOLD)
            for g in ("overall", str(t), group(r)):
                buckets.setdefault(g, []).append((y, pred))
            cohort.append(
                dict(**meta, label=y, score=s, uncertainty=uncertainty(s), prediction=pred)
            )
            if source_id in pilot_ids:
                pilots.append(case)
    exp = Experiment(spec, DIR, pilots)
    _, trials = validate(exp)
    requests = [req for *_, req in trials]
    reserve = preflight(spec, requests, "live", True)
    receipt = dict(
        version="wdc-matching-v1",
        sources=sources,
        prompt_sha256=digest(PROMPT),
        config_sha256=digest(spec),
        threshold=THRESHOLD,
        cohort=cohort,
        baseline={k: metrics(v) for k, v in buckets.items()},
        pilot=[
            dict(
                pair_id=c.provenance["pair_id"],
                request_sha256=digest(req),
                body_sha256=digest(request_payload(req)),
                input_token_reserve=estimate_input_tokens(req),
            )
            for c, _, _, req in trials
        ],
        projected_api_reserve_usd=reserve,
    )
    return receipt, exp


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the committed receipt")
    args = parser.parse_args()
    data, _ = prepare()
    if args.check:
        if data != json.loads(FROZEN.read_text()):
            raise SystemExit("Frozen receipt mismatch")
    else:
        with FROZEN.open("x", encoding="utf8", newline="\n") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    print(
        json.dumps(
            {
                "pairs": len(data["cohort"]),
                "baseline": data["baseline"],
                "reserve": data["projected_api_reserve_usd"],
            }
        )
    )
