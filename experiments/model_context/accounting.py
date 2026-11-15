"""Receipt checks and usage pricing for both models. No provider client."""

import re
from decimal import Decimal

from eval_lab.providers.openai_adapter import normalize_usage
from experiments.finops_sql.v3.proposal import OUTPUT

from .proposal import PRICES

SNAPSHOT = re.compile(r"-\d{4}-\d{2}-\d{2}")


def served_as(raw_model, requested: str) -> bool:
    """The alias itself or one of its dated snapshots, such as gpt-6.1-sol-2026-10-01."""
    if not isinstance(raw_model, str):
        return False
    return raw_model == requested or (
        raw_model.startswith(requested) and SNAPSHOT.fullmatch(raw_model[len(requested) :])
    )


def charge(raw: dict, requested: str, input_bound: int) -> Decimal:
    if requested not in PRICES:
        raise ValueError("unpriced model")
    if not served_as(raw.get("model"), requested) or raw.get("service_tier") != "default":
        raise ValueError("unpriced model or tier")
    reasoning = raw.get("reasoning")
    cache = raw.get("prompt_cache_options")
    if reasoning is None:
        reasoning = {}
    if cache is None:
        cache = {}
    if (
        raw.get("max_output_tokens") not in (None, OUTPUT)
        or not isinstance(reasoning, dict)
        or reasoning.get("effort") not in (None, "medium")
        or not isinstance(cache, dict)
        or cache.get("ttl") not in (None, "30m")
        or cache.get("mode") not in (None, "implicit")
        or cache.get("prewarm")
    ):
        raise ValueError("contradictory configuration")
    usage = normalize_usage(raw)
    if usage is None or usage.uncached_input_tokens is None:
        raise ValueError("missing or inconsistent usage")
    u = raw["usage"]
    i, o = u["input_tokens"], u["output_tokens"]
    read = u["input_tokens_details"]["cached_tokens"]
    write = u["input_tokens_details"]["cache_write_tokens"]
    reasoning_tokens = (u.get("output_tokens_details") or {}).get("reasoning_tokens")
    if (
        not all(
            type(n) is int and n >= 0
            for n in (i, o, read, write, reasoning_tokens, u.get("total_tokens"))
        )
        or i + o != u["total_tokens"]
        or read + write > i
        or i > input_bound
        or o > OUTPUT
        or reasoning_tokens > o
    ):
        raise ValueError("token accounting")
    details = u["input_tokens_details"].get("cache_write_tokens_details")
    if details is not None and any(type(n) is not int or n < 0 for n in details.values()):
        raise ValueError("invalid lifetime counters")
    split = usage.cache.writes_by_ttl
    if split is not None and split != {"30m": write, "12h": 0}:
        raise ValueError("unpriced cache lifetime")
    p = {k: Decimal(v) for k, v in PRICES[requested].items()}
    return (
        p["input"] * (i - read - write)
        + p["cached"] * read
        + p["30m_write"] * write
        + p["output"] * o
    ) / 1_000_000
