"""Build an exclusive offline proposal directory; this module has no provider client."""

import argparse
import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path
from random import Random

from eval_lab.core.hashes import canonical, digest

from .episode import HISTORY_LIMIT, body
from .packages import FILES, QUESTIONS, ROOT, package, source, tokens


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build():
    questions = QUESTIONS.copy()
    Random(5005).shuffle(questions)
    bodies = []
    rows = []
    allowances = {arm: 0 for arm in "ABCD"}
    fileinfo = {}
    for name in ["questions.json", *sum(FILES.values(), [])]:
        value = source(name)
        fileinfo[name] = {
            "bytes": len(value.encode()),
            "tokens": tokens(value),
            "sha256": sha(value.encode()),
        }
    for i, q in enumerate(questions):
        order = "ABCD"[i % 4 :] + "ABCD"[: i % 4]
        for arm in order:
            b = body(arm, q)
            size = len(canonical(b).encode())
            bounds = [size + 256]
            if arm == "D":
                # Six canonical history messages, each bounded encoded bytes including comma.
                # Final tools are removed. Byte ceiling intentionally covers every proxy token.
                final = len(canonical(body("D", q, [{}] * 6)).encode()) - 6 * len(
                    ("," + canonical({"role": "user", "content": "Discovery record {}"})).encode()
                )
                bounds += [size + HISTORY_LIMIT * n + 256 for n in range(1, 6)] + [
                    final + HISTORY_LIMIT * 6 + 256
                ]
            allowances[arm] += sum(bounds)
            rows.append(
                {
                    "question": q["id"],
                    "arm": arm,
                    "body_hash": digest(b),
                    "bytes": size,
                    "serialized_tokens": tokens(b),
                    "turn_input_bounds": bounds,
                }
            )
            bodies.append(b)
    costs = {
        arm: str(
            (
                Decimal(n) * Decimal(".125")
                + Decimal(36 * (7 if arm == "D" else 1) * 2048) * Decimal(".50")
            )
            / 1000000
        )
        for arm, n in allowances.items()
    }
    plan = {
        "version": "meridian-context-v2",
        "model": "gpt-6-luna",
        "source_locations": {
            name: (
                "schema.sql"
                if name == "schema.sql"
                else f"public/{'v2' if name == 'questions.json' else 'v1'}/{name}"
            )
            for name in fileinfo
        },
        "discovery_history": {
            "mode": "stateless user-role discovery records",
            "max_records": 6,
            "max_escaped_bytes_per_record": HISTORY_LIMIT,
            "final_tools_disabled": True,
            "constructor_sha256": sha((ROOT / "episode.py").read_text(encoding="utf8").encode()),
        },
        "request_ceiling": 360,
        "tool_ceiling": 216,
        "output_per_turn": 2048,
        "sources": fileinfo,
        "oracle_bindings_sha256": sha(
            (ROOT / "oracle-bindings-v2.json").read_text(encoding="utf8").encode()
        ),
        "package_order": FILES,
        "context_sha256": {arm: sha(package(arm).encode()) for arm in "ABCD"},
        "requests": rows,
        "input_by_arm": allowances,
        "cost_by_arm": costs,
        "reserve_usd": str(sum(map(Decimal, costs.values()))),
        "proposed_cap_usd": "1.00",
        "pricing_date": "2026-11-10",
        "usd_per_million": {
            "input": "0.10",
            "cached": "0.01",
            "30m_write": "0.125",
            "output": "0.50",
        },
        "bodies_sha256": digest(bodies),
        "implementation_sha256": {
            p.name: sha(p.read_text(encoding="utf8").encode()) for p in sorted(ROOT.glob("*.py"))
        },
    }
    return plan, bodies


def write(dest: Path):
    plan, bodies = build()
    dest.mkdir(exist_ok=False, parents=True)
    (dest / "manifest.json").write_bytes(
        (json.dumps({**plan, "proposal_digest": digest(plan)}, indent=2) + "\n").encode()
    )
    with (
        (dest / "bodies.json.gz").open("xb") as out,
        gzip.GzipFile(filename="", fileobj=out, mode="wb", mtime=0) as pack,
    ):
        pack.write(canonical(bodies).encode())
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    print(write(parser.parse_args().destination)["reserve_usd"])
