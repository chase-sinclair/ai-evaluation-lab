"""Freeze independent evaluation and development proposals. No network transport."""

import argparse
import gzip
import json
from decimal import Decimal
from pathlib import Path
from typing import Literal

from eval_lab.core.hashes import canonical, digest

from ..checkpoint import SNAPSHOTS
from ..controls import DEVELOPMENT
from ..episode import HISTORY_LIMIT, INSTRUCTIONS, history_bytes
from ..episode import body as previous_body
from ..packages import QUESTIONS, ROOT, package, tokens
from ..proposal import sha

Scope = Literal["evaluation", "development"]
HERE = Path(__file__).parent
PARENT = "82539bc63c44e9bced2111989c9fcd59f7b867941d70b3e3d943479778e31733"
REPORTING = (HERE / "reporting.md").read_text(encoding="utf8")
OUTPUT = 25_000
READ_TIMEOUT = 900
CAP = {"evaluation": Decimal("5.50"), "development": Decimal("0.17")}
DEV_FIELDS = [
    "cost",
    "repeats",
    "cost",
    "center_id allocated total",
    "team_id share",
    "change",
    "resource_id",
    "cost",
]
DEV_QUESTIONS = {
    key: {"id": key, "question": text, "fields": fields.split()}
    for (key, (text, _)), fields in zip(DEVELOPMENT.items(), DEV_FIELDS, strict=True)
}
PILOT = [("D01", "A"), ("D03", "B"), ("D04", "C"), ("D06", "D"), ("D08", "B")]


def body(arm: str, question: dict, history=()) -> dict:
    if any(history_bytes(record) > HISTORY_LIMIT for record in history):
        raise ValueError("oversized discovery history")
    payload = previous_body(arm, question, history)
    payload["input"][0]["content"] = REPORTING + payload["input"][0]["content"]
    payload["max_output_tokens"] = OUTPUT
    return payload


def reserve(inputs: int, turns: int) -> Decimal:
    return (Decimal(".125") * inputs + Decimal(".50") * OUTPUT * turns) / 1_000_000


def turn_bounds(arm: str, q: dict, initial: dict) -> list[int]:
    initial_bound = len(canonical(initial).encode()) + 256
    if arm != "D":
        return [initial_bound]
    # Strip the six placeholder messages to measure the final tools-disabled envelope.
    last = body(arm, q, [{}] * 6)
    last["input"] = last["input"][:2]
    return [initial_bound + n * HISTORY_LIMIT for n in range(6)] + [
        len(canonical(last).encode()) + 256 + 6 * HISTORY_LIMIT
    ]


def build(scope: Scope) -> tuple[dict, list[dict]]:
    old = json.loads((ROOT / "proposals/v2/manifest.json").read_bytes())
    if old.pop("proposal_digest") != PARENT or digest(old) != PARENT:
        raise ValueError("historical proposal binding")
    if scope == "development":
        order, questions = PILOT, DEV_QUESTIONS
    elif scope == "evaluation":
        order = [(r["question"], r["arm"]) for r in old["requests"]]
        questions = {q["id"]: q for q in QUESTIONS}
    else:
        raise ValueError("unknown cohort")
    bodies, rows = [], []
    totals = {arm: {"input": 0, "turns": 0} for arm in "ABCD"}
    for key, arm in order:
        initial = body(arm, questions[key])
        bounds = turn_bounds(arm, questions[key], initial)
        bodies.append(initial)
        rows.append(
            dict(
                question=key,
                arm=arm,
                body_hash=digest(initial),
                serialized_tokens=tokens(initial),
                turn_input_bounds=bounds,
            )
        )
        totals[arm]["input"] += sum(bounds)
        totals[arm]["turns"] += len(bounds)
    requests = sum(v["turns"] for v in totals.values())
    costs = {a: reserve(v["input"], v["turns"]) for a, v in totals.items()}
    total = sum(costs.values())
    if total > CAP[scope]:
        raise ValueError(f"{scope} reserve {total} exceeds {CAP[scope]}")
    files = [
        *ROOT.glob("*.py"),
        ROOT / "Dockerfile",
        ROOT / "oracle-bindings-v2.json",
        *HERE.glob("*.py"),
        HERE / "Dockerfile",
        HERE / "reporting.md",
        HERE / "protocol.md",
        *(ROOT / name for name in old["source_locations"].values()),
    ]
    plan = {
        "version": f"meridian-v3-{scope}-once",
        "result_directory": f"results/meridian-v3-{scope}-once",
        "historical_proposal": PARENT,
        "source_sha256": {
            p.relative_to(ROOT).as_posix(): sha(p.read_text(encoding="utf8").encode())
            for p in sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())
        },
        # C and D can see samples from the development export in either cohort.
        "snapshot_manifests": {
            k: v for k, v in SNAPSHOTS.items() if scope == "evaluation" or k == "development"
        },
        "developer_message_sha256": {
            a: sha((REPORTING + INSTRUCTIONS + package(a)).encode()) for a in "ABCD"
        },
        "model": "gpt-6-luna",
        "reasoning": "medium",
        "service_tier": "default",
        "output_per_turn": OUTPUT,
        "discovery_calls_per_episode": 6,
        "max_escaped_bytes_per_record": HISTORY_LIMIT,
        "tool_free_final_turn": True,
        "http_timeout_seconds": {"read": READ_TIMEOUT, "connect": 10, "write": 30, "pool": 10},
        "sdk_retries": 0,
        "request_ceiling": requests,
        "tool_ceiling": requests - len(rows),
        "requests": rows,
        "bodies_sha256": digest(bodies),
        "bounds_by_arm": totals,
        "cost_by_arm_usd": {arm: str(cost) for arm, cost in costs.items()},
        "usd_per_million": old["usd_per_million"],
        "pricing_date": "2026-11-11",
        "reserve_usd": str(total),
        "proposed_cap_usd": str(CAP[scope]),
    }
    return plan, bodies


def write(scope: Scope, destination: Path) -> dict:
    plan, bodies = build(scope)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "manifest.json").write_bytes(
        (json.dumps(plan | {"proposal_digest": digest(plan)}, indent=2) + "\n").encode()
    )
    with (
        (destination / "bodies.json.gz").open("xb") as out,
        gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0) as archive,
    ):
        archive.write(canonical(bodies).encode())
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=CAP)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(write(args.scope, args.destination)["reserve_usd"])
