"""Build or verify the acquisition proposal offline. No live dispatch path."""

import argparse
import hashlib
import json
from decimal import Decimal
from random import Random

from eval_lab.contracts import ModelRequest
from eval_lab.core.hashes import canonical, digest
from eval_lab.core.result_store import write_once
from eval_lab.providers.openai_adapter import request_payload

from .rules import MANUAL, STATUSES
from .study import HERE, checkpoint, inventory

FREEZE = "491abff8797ed268a4b9ff18a49b754dbcce50d3"
FILE = HERE / "request-manifest.json"


def checksum(p):
    return hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def request(view):
    tools = []
    for name in [*view["catalog"], "stop"]:
        props = (
            {"status": {"type": "string", "enum": list(STATUSES)}}
            if name == "stop"
            else {k: {"type": "string"} for k in ("tenant", "caller", "key", "payload")}
        )
        tools.append(
            dict(
                type="function",
                name=name,
                description=(
                    "End without a business write."
                    if name == "stop"
                    else f"Propose {name.replace('_', ' ')}. Use a serialized JSON payload."
                ),
                parameters=dict(
                    type="object",
                    properties=props,
                    required=list(props),
                    additionalProperties=False,
                ),
                strict=True,
            )
        )
    return ModelRequest(
        model="gpt-6-luna",
        max_output_tokens=512,
        tools=tools,
        messages=[
            {"role": "developer", "content": MANUAL},
            {"role": "user", "content": canonical(view)},
        ],
    )


def body(req):
    return request_payload(req) | {"prompt_cache_options": {"ttl": "30m"}}


def build():
    frozen = json.loads((HERE / "rules-freeze.json").read_bytes())
    root = HERE.parents[1]
    if frozen["revision"] != FREEZE or any(
        checksum(root / k) != v for k, v in frozen["files"].items()
    ):
        raise ValueError("Rules freeze mismatch")
    rows = inventory()
    Random(4004).shuffle(rows)
    ordered = []
    for row in rows:
        source, seal = checkpoint(row)
        b = body(request(source["public"]))
        size = len(canonical(b).encode())
        ordered.append(
            dict(
                case=row["id"],
                checkpoint_sha256=seal,
                body=b,
                body_sha256=digest(b),
                serialized_bytes=size,
                input_allowance=size + 256,
            )
        )
    reserve = (
        sum(Decimal(r["input_allowance"]) * Decimal(".125") + 512 * Decimal(".50") for r in ordered)
        / 1000000
    )
    if reserve > Decimal(".025") or len(ordered) != 24:
        raise ValueError("Proposed budget exceeded")
    return {
        "rules": frozen,
        "fixture_sha256": checksum(HERE / "episodes.json"),
        "sources": {p.name: checksum(p) for p in sorted(HERE.glob("*.py"))},
        "model": "gpt-6-luna",
        "requests": ordered,
        "max_requests": 24,
        "zero_retries": True,
        "price_date": "2026-11-10",
        "pricing_usd_per_million": {
            "input": 0.10,
            "cached_read": 0.01,
            "cache_write_30m": 0.125,
            "output": 0.50,
        },
        "reserve_usd": str(reserve),
        "proposed_cap_usd": "0.025",
        "dispatch_authorized": False,
        "abort": [
            "changed manifest, body, revision or source binding",
            "used run directory",
            "provider, model, standard tier or 30m policy mismatch",
            "incomplete response, missing accounting or allowance exceeded",
            "remaining reserve exceeds remaining cap",
        ],
    }


def verify():
    plan = build()
    if plan != json.loads(FILE.read_bytes()):
        raise ValueError("Frozen request manifest mismatch")
    return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    if args.freeze:
        write_once(FILE, build())
    plan = verify()
    print(digest(plan), plan["reserve_usd"])
