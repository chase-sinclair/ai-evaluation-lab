"""Audit the sealed GPT and Claude context ledgers without changing their frozen analyzers."""

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal

from eval_lab.core.hashes import digest
from experiments.claude_context import accounting as claude
from experiments.finops_sql.episode import final
from scripts import acquire_claude_context, acquire_model_context

from . import accounting as gpt
from .analysis import answer_text, load, require

type Provider = Literal["gpt", "claude"]
type Usage = Counter[str]


def gpt_terminal(raw: dict, payload: dict) -> dict:
    if acquire_model_context.exhausted(raw, payload):
        return {"kind": "output_exhaustion"}
    require(
        raw.get("status") == "completed"
        and not raw.get("incomplete_details")
        and not raw.get("error"),
        "completion evidence",
    )
    if any(item.get("type") == "function_call" for item in raw.get("output", [])):
        return {"kind": "invalid_proposals"}
    text = answer_text(raw)
    return final(text) if text else {"kind": "missing"}


def gpt_usage(usage: dict) -> dict:
    details = usage["input_tokens_details"]
    return dict(
        reasoning=usage["output_tokens_details"]["reasoning_tokens"],
        cache_read=details["cached_tokens"],
        cache_write=details["cache_write_tokens"],
    )


def claude_usage(usage: dict) -> dict:
    return dict(
        thinking=(usage.get("output_tokens_details") or {}).get("thinking_tokens") or 0,
        cache_read=usage["cache_read_input_tokens"],
        cache_write=usage["cache_creation_input_tokens"],
    )


@dataclass(frozen=True)
class ReceiptProtocol:
    charge: Callable[[dict, str, int], Decimal]
    terminal: Callable[[dict, dict], dict]
    usage_details: Callable[[dict], dict]
    id_prefix: str
    kept_headers: tuple[str, ...] = ()


PROTOCOLS: dict[Provider, ReceiptProtocol] = {
    "gpt": ReceiptProtocol(gpt.charge, gpt_terminal, gpt_usage, "resp_"),
    "claude": ReceiptProtocol(
        claude.charge,
        lambda raw, _: claude.terminal(raw),
        claude_usage,
        "msg_",
        acquire_claude_context.KEPT_HEADERS,
    ),
}


def check_event(event: dict, answer: dict, receipt: dict, cost: Decimal) -> None:
    require(
        Decimal(event["cost"]) == cost
        and event["model_latency"] == receipt["latency"]
        and event["served_model"] == receipt["raw"]["model"],
        "event accounting",
    )
    kind = answer["kind"]
    expected_outcome = kind if kind in {"output_exhaustion", "refusal"} else None
    require(event.get("outcome") == expected_outcome, "event outcome")
    if kind != "output_exhaustion":
        require(event["final"] == answer, "terminal evidence")


def replay(
    folder: Path, provider: Provider
) -> tuple[dict[str, dict], dict[str, Usage], dict[str, list[str]]]:
    """Verify bound receipts and costs, including a charged but unfinished last attempt."""
    acquisition = {"gpt": acquire_model_context, "claude": acquire_claude_context}[provider]
    protocol = PROTOCOLS[provider]
    plan, bodies = acquisition.preflight(acquisition.APPROVAL)
    seal = load(folder / "seal.json")
    hashes = {
        file.name: hashlib.sha256(file.read_bytes()).hexdigest()
        for file in folder.iterdir()
        if file.name != "seal.json"
    }
    require(hashes == seal["files"] and digest(hashes) == seal["ledger_hash"], "ledger integrity")
    require(load(folder / "plan.json")["digest"] == acquisition.APPROVAL, "proposal identity")
    attempted = seal["requests_attempted"]
    unaccounted = seal["attempts_without_accounting"]
    require(
        type(attempted) is int
        and 0 <= attempted <= len(bodies) == seal["planned"]
        and type(unaccounted) is int
        and 0 <= unaccounted <= min(attempted, 1),
        "seal inventory",
    )
    ends = {}
    stats = defaultdict(Counter)
    served = defaultdict(set)
    response_ids = set()
    for i, (row, payload) in enumerate(zip(plan["requests"], bodies, strict=True), start=1):
        key = row["id"]
        if i > attempted:
            ends[key] = {"kind": "unsent"}
            continue
        cell = f"{row['model']}-{row['arm']}"
        prefix = folder / f"{i:03}"
        require(
            load(prefix.with_suffix(".request"))
            == dict(body=payload, hash=row["body_hash"], id=key)
            and load(prefix.with_suffix(".request-body")) == payload,
            "request binding",
        )
        if protocol.kept_headers:
            headers = load(prefix.with_suffix(".request-headers"))
            require(set(headers) <= set(protocol.kept_headers), "headers")
        event_path = prefix.with_suffix(".event")
        has_event = event_path.exists()
        if not has_event:
            require(i == attempted and seal["failure"] is not None, "missing event")
            ends[key] = {"kind": "interrupted"}
            if unaccounted:
                continue
        raw = load(prefix.with_suffix(".response-body"))
        receipt = load(prefix.with_suffix(".response"))
        response_id = raw["id"]
        require(
            receipt["raw"] == raw
            and receipt["body_hash"] == row["body_hash"]
            and isinstance(response_id, str)
            and response_id.startswith(protocol.id_prefix)
            and len(response_id) > len(protocol.id_prefix)
            and response_id.isascii()
            and not any(char.isspace() for char in response_id)
            and response_id not in response_ids,
            "response identity",
        )
        cost = protocol.charge(raw, payload["model"], row["input_bound"])
        response_ids.add(response_id)
        usage = raw["usage"]
        stats[cell].update(
            dict(
                requests=1,
                input=usage["input_tokens"],
                output=usage["output_tokens"],
                cost=cost,
                api_seconds=receipt["latency"],
                **protocol.usage_details(usage),
            )
        )
        served[cell].add(raw["model"])
        if has_event:
            answer = protocol.terminal(raw, payload)
            check_event(load(event_path), answer, receipt, cost)
            ends[key] = answer
    kinds = Counter(answer["kind"] for answer in ends.values())
    require(
        sum(usage["cost"] for usage in stats.values()) == Decimal(seal["accounted_usd"])
        and attempted - len(response_ids) == unaccounted
        and kinds["unsent"] == seal["unsent"]
        and kinds["output_exhaustion"] == seal["exhausted"]
        and kinds["refusal"] == seal.get("refused", 0)
        and attempted - kinds["interrupted"] - kinds["output_exhaustion"] - kinds["refusal"]
        == seal["finished"],
        "seal counts",
    )
    return ends, stats, {cell: sorted(models) for cell, models in served.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=tuple(PROTOCOLS))
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    ends, stats, served = replay(args.folder, args.provider)
    report = {
        "outcomes": Counter(answer["kind"] for answer in ends.values()),
        "accounted_usd": str(sum(usage["cost"] for usage in stats.values())),
        "attempts_without_accounting": sum(answer["kind"] != "unsent" for answer in ends.values())
        - sum(usage["requests"] for usage in stats.values()),
        "telemetry": stats,
        "served_models": served,
    }
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
