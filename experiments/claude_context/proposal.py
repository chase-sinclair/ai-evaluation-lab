"""Freeze the Experiment 007 Claude replication proposal. No network transport.

Every request is derived mechanically from the frozen Experiment 006 request in the same
position: the 006 developer text becomes the system text and the 006 user text becomes the
user message, byte for byte. Only the model, the Messages API envelope and the cache marker
differ.
"""

import argparse
import gzip
import json
from decimal import Decimal
from pathlib import Path

from eval_lab.core.hashes import canonical, digest
from experiments.model_context.proposal import FROZEN as PARENT_FROZEN
from experiments.model_context.proposal import cell_id, sha

HERE = Path(__file__).parent
REPO = HERE.parents[1]
FROZEN = HERE / "proposals" / "r1"
NAME = "meridian-claude-context-r1-once"
PARENT_DIGEST = "f9fd35762130871a80c4a24d28dae47a3bf9f500c5d4f7185cb77fe21ba458f0"
PARENT_BODIES = "f019425b0b4072066009579f758fb7b60bedc6fecb616ba5a6b8223c85e57c58"

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}
# Each Claude model takes the 006 model's slot at the same price.
COUNTERPART = {"luna": "haiku", "sol": "sonnet"}
OUTPUT = 25_000
EFFORT = "medium"
CAP = Decimal("15.00")
PRICING_DATE = "2026-11-15"
PRICING_SOURCE = "https://platform.claude.com/docs/en/about-claude/pricing"
# Standard rates, global routing, prompts up to 100,000 tokens. USD per million tokens.
PRICES = {
    "claude-haiku-5-5": {
        "input": "0.10",
        "cache_read": "0.01",
        "5m_write": "0.125",
        "output": "0.50",
    },
    "claude-sonnet-5-5": {
        "input": "2.00",
        "cache_read": "0.10",
        "5m_write": "2.50",
        "output": "10.00",
    },
}
HAIKU_THRESHOLD = 100_000
SOURCES = [
    "experiments/claude_context/proposal.py",
    "experiments/claude_context/accounting.py",
    "experiments/claude_context/analysis.py",
    "experiments/claude_context/protocol.md",
    "experiments/model_context/proposal.py",
    "experiments/model_context/analysis.py",
    "experiments/finops_sql/episode.py",
    "experiments/finops_sql/grading.py",
    "experiments/finops_sql/compare.py",
    "experiments/finops_sql/checkpoint.py",
    "experiments/finops_sql/oracle-bindings-v2.json",
    "experiments/finops_sql/v3/grading.py",
    "experiments/finops_sql/v3/worker.py",
    "experiments/finops_sql/v3/Dockerfile",
]


def reserve(model: str, input_bound: int) -> Decimal:
    """Worst case for one request: every input byte priced as a cache write, full output."""
    p = PRICES[model]
    return (Decimal(p["5m_write"]) * input_bound + Decimal(p["output"]) * OUTPUT) / 1_000_000


def parent() -> tuple[dict, list[dict]]:
    """The frozen, approved Experiment 006 proposal."""
    manifest = json.loads((PARENT_FROZEN / "manifest.json").read_bytes())
    stored = manifest.pop("proposal_digest")
    if stored != PARENT_DIGEST or digest(manifest) != PARENT_DIGEST:
        raise ValueError("Experiment 006 proposal changed")
    bodies = json.loads(gzip.decompress((PARENT_FROZEN / "bodies.json.gz").read_bytes()))
    if digest(bodies) != PARENT_BODIES or manifest["bodies_sha256"] != PARENT_BODIES:
        raise ValueError("Experiment 006 bodies changed")
    return manifest, bodies


def translate(model: str, source: dict) -> dict:
    """One 006 Responses body to the equivalent Messages body. Texts are copied unchanged."""
    roles = [m["role"] for m in source["input"]]
    if roles != ["developer", "user"] or not all(
        isinstance(m["content"], str) for m in source["input"]
    ):
        raise ValueError("unexpected 006 body shape")
    if (
        source["max_output_tokens"] != OUTPUT
        or source["reasoning"] != {"effort": EFFORT}
        or source["service_tier"] != "default"
    ):
        raise ValueError("006 settings differ from the mapped settings")
    developer, user = (m["content"] for m in source["input"])
    return {
        "model": model,
        "max_tokens": OUTPUT,
        "system": [{"type": "text", "text": developer, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": EFFORT},
        # Explicit, so a workspace default of US-only routing (1.1x prices) cannot apply.
        "inference_geo": "global",
    }


def build() -> tuple[dict, list[dict]]:
    old, old_bodies = parent()
    rows, bodies = [], []
    worst = {f"{m}-{a}": Decimal(0) for m in MODELS for a in ("A", "B")}
    for row, source in zip(old["requests"], old_bodies, strict=True):
        model = COUNTERPART[row["model"]]
        payload = translate(MODELS[model], source)
        bound = len(canonical(payload).encode()) + 256
        cost = reserve(MODELS[model], bound)
        worst[f"{model}-{row['arm']}"] += cost
        rows.append(
            dict(
                id=cell_id(row["question"], model, row["arm"], row["draw"]),
                question=row["question"],
                model=model,
                arm=row["arm"],
                draw=row["draw"],
                parent_id=row["id"],
                parent_body_hash=row["body_hash"],
                body_hash=digest(payload),
                input_bound=bound,
                worst_case_usd=str(cost),
            )
        )
        bodies.append(payload)
    if len(rows) != 432 or len({r["id"] for r in rows}) != 432:
        raise ValueError("request inventory")
    plan = {
        "version": NAME,
        "result_directory": "results/" + NAME,
        "design": "docs/experiment07_claude_replication_design.md",
        "parent_proposal": PARENT_DIGEST,
        "parent_bodies_sha256": PARENT_BODIES,
        "models": MODELS,
        "counterparts": COUNTERPART,
        "arms": ["A", "B"],
        "draws": 3,
        "thinking": "adaptive",
        "effort": EFFORT,
        "output_per_request": OUTPUT,
        "cache": "ephemeral 5-minute marker on the system block",
        "fallbacks": "none",
        "inference_geo": "global, set explicitly",
        "sdk_retries": 0,
        "http_timeout_seconds": {"read": 900, "connect": 10, "write": 30, "pool": 10},
        "request_ceiling": len(rows),
        "requests": rows,
        "bodies_sha256": digest(bodies),
        "usd_per_million": PRICES,
        "haiku_higher_price_threshold_tokens": HAIKU_THRESHOLD,
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
