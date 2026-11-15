"""Freeze the Experiment 006 model-by-context proposal. No network transport.

Luna request bodies are the accepted Experiment 005 v3 evaluation bodies for arms A and B,
byte for byte. Sol bodies differ only in the model field.
"""

import argparse
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from random import Random

from eval_lab.core.hashes import canonical, digest
from experiments.finops_sql.packages import QUESTIONS
from experiments.finops_sql.packages import ROOT as FINOPS
from experiments.finops_sql.v3.proposal import OUTPUT, body

HERE = Path(__file__).parent
REPO = HERE.parents[1]
FROZEN = HERE / "proposals" / "r1"
NAME = "meridian-model-context-r1-once"
PARENT = FINOPS / "proposals/v3/evaluation-r1"
PARENT_DIGEST = "4eb6e593374585e11b349cc1341c82bda22048eb2a6ff69560dc7a82d214d36f"

MODELS = {"luna": "gpt-6-luna", "sol": "gpt-6.1-sol"}
ARMS = ("A", "B")
CELLS = [(m, a) for m in MODELS for a in ARMS]
DRAWS = 3
SEED = 6006
CAP = Decimal("15.00")
PRICING_DATE = "2026-11-15"
PRICING_SOURCE = "https://developers.openai.com/api/docs/pricing"
# Standard tier, short context, USD per million tokens.
PRICES = {
    "gpt-6-luna": {"input": "0.10", "cached": "0.01", "30m_write": "0.125", "output": "0.50"},
    "gpt-6.1-sol": {"input": "2.00", "cached": "0.10", "30m_write": "2.50", "output": "10.00"},
}
SOURCES = [
    "experiments/model_context/proposal.py",
    "experiments/model_context/accounting.py",
    "experiments/model_context/analysis.py",
    "experiments/model_context/protocol.md",
    "experiments/finops_sql/episode.py",
    "experiments/finops_sql/packages.py",
    "experiments/finops_sql/grading.py",
    "experiments/finops_sql/compare.py",
    "experiments/finops_sql/checkpoint.py",
    "experiments/finops_sql/oracle-bindings-v2.json",
    "experiments/finops_sql/v3/proposal.py",
    "experiments/finops_sql/v3/grading.py",
    "experiments/finops_sql/v3/worker.py",
    "experiments/finops_sql/v3/Dockerfile",
    "experiments/finops_sql/v3/reporting.md",
    "experiments/finops_sql/public/v2/questions.json",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cell_id(question: str, model: str, arm: str, draw: int) -> str:
    return f"{question}-{model}-{arm}-{draw}"


def reserve(model: str, input_bound: int) -> Decimal:
    """Worst case for one request: every input byte priced as a cache write, full output."""
    p = PRICES[model]
    return (Decimal(p["30m_write"]) * input_bound + Decimal(p["output"]) * OUTPUT) / 1_000_000


def parent_bodies() -> dict[tuple[str, str], dict]:
    """Accepted 005 evaluation bodies for arms A and B, keyed by question and arm."""
    manifest = json.loads((PARENT / "manifest.json").read_bytes())
    stored = manifest.pop("proposal_digest")
    if stored != PARENT_DIGEST or digest(manifest) != PARENT_DIGEST:
        raise ValueError("Experiment 005 evaluation proposal changed")
    bodies = json.loads(gzip.decompress((PARENT / "bodies.json.gz").read_bytes()))
    if digest(bodies) != manifest["bodies_sha256"]:
        raise ValueError("Experiment 005 bodies changed")
    out = {}
    for row, initial in zip(manifest["requests"], bodies, strict=True):
        if row["arm"] in ARMS:
            if digest(initial) != row["body_hash"]:
                raise ValueError("Experiment 005 body binding")
            out[(row["question"], row["arm"])] = initial
    return out


def request_body(model: str, arm: str, question: dict, parents: dict) -> dict:
    payload = body(arm, question)
    if payload != parents[(question["id"], arm)]:
        raise ValueError("Luna body differs from the accepted Experiment 005 body")
    return payload | {"model": MODELS[model]}


def build() -> tuple[dict, list[dict]]:
    parents = parent_bodies()
    questions = {q["id"]: q for q in QUESTIONS}
    if sorted(questions) != [f"Q{n:02}" for n in range(1, 37)]:
        raise ValueError("question inventory")
    rows, bodies = [], []
    worst = {f"{m}-{a}": Decimal(0) for m, a in CELLS}
    for draw in range(1, DRAWS + 1):
        order = sorted(questions)
        Random(SEED * 10 + draw).shuffle(order)
        for i, key in enumerate(order):
            for model, arm in CELLS[i % 4 :] + CELLS[: i % 4]:
                payload = request_body(model, arm, questions[key], parents)
                bound = len(canonical(payload).encode()) + 256
                cost = reserve(MODELS[model], bound)
                worst[f"{model}-{arm}"] += cost
                rows.append(
                    dict(
                        id=cell_id(key, model, arm, draw),
                        question=key,
                        model=model,
                        arm=arm,
                        draw=draw,
                        body_hash=digest(payload),
                        input_bound=bound,
                        worst_case_usd=str(cost),
                    )
                )
                bodies.append(payload)
    if len(rows) != 432 or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("request inventory")
    plan = {
        "version": NAME,
        "result_directory": "results/" + NAME,
        "design": "docs/experiment06_model_context_design.md",
        "parent_evaluation_proposal": PARENT_DIGEST,
        "models": MODELS,
        "arms": list(ARMS),
        "draws": DRAWS,
        "order_seed": SEED,
        "reasoning": "medium",
        "service_tier": "default",
        "output_per_request": OUTPUT,
        "sdk_retries": 0,
        "http_timeout_seconds": {"read": 900, "connect": 10, "write": 30, "pool": 10},
        "request_ceiling": len(rows),
        "requests": rows,
        "bodies_sha256": digest(bodies),
        "usd_per_million": PRICES,
        "pricing_date": PRICING_DATE,
        "pricing_source": PRICING_SOURCE,
        "worst_case_by_cell_usd": {k: str(v) for k, v in worst.items()},
        "worst_case_reserve_usd": str(sum(worst.values())),
        "spending_guard": "send only if accounted spend plus this request's worst case <= cap",
        "proposed_cap_usd": str(CAP),
        "source_sha256": {
            name: sha((REPO / name).read_text(encoding="utf8").replace("\r\n", "\n").encode())
            for name in SOURCES
        },
    }
    return plan, bodies


def write(destination: Path = FROZEN) -> dict:
    plan, bodies = build()
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
    parser.add_argument("destination", type=Path, nargs="?", default=FROZEN)
    args = parser.parse_args()
    plan = write(args.destination)
    print(plan["worst_case_reserve_usd"], digest(plan))
