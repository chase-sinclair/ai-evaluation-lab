"""Receipt checks and bounded transport settings for the proposed protocol."""

from decimal import Decimal

import httpx

from eval_lab.providers.openai_adapter import normalize_usage

from .proposal import OUTPUT, READ_TIMEOUT


def timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=10, write=30, pool=10, read=READ_TIMEOUT)


def charge(raw: dict, input_bound: int) -> Decimal:
    if (raw.get("model"), raw.get("service_tier"), raw.get("max_output_tokens")) != (
        "gpt-6-luna",
        "default",
        OUTPUT,
    ) or (raw.get("reasoning") or {}).get("effort") != "medium":
        raise ValueError("response configuration drift")
    cache = raw.get("prompt_cache_options") or {}
    if (
        cache.get("ttl") != "30m"
        or cache.get("mode") not in (None, "implicit")
        or cache.get("prewarm")
    ):
        raise ValueError("cache policy")
    usage = normalize_usage(raw)
    if usage is None or usage.uncached_input_tokens is None:
        raise ValueError("missing or inconsistent usage")
    u = raw["usage"]
    i, o = u["input_tokens"], u["output_tokens"]
    read = u["input_tokens_details"]["cached_tokens"]
    write = u["input_tokens_details"]["cache_write_tokens"]
    reasoning = (u.get("output_tokens_details") or {}).get("reasoning_tokens")
    if (
        not all(
            type(n) is int and n >= 0 for n in (i, o, read, write, reasoning, u.get("total_tokens"))
        )
        or i + o != u["total_tokens"]
        or read + write > i
        or i > input_bound
        or o > OUTPUT
        or reasoning > o
    ):
        raise ValueError("token accounting")
    split = usage.cache.writes_by_ttl
    if split is not None and split != {"30m": write, "12h": 0}:
        raise ValueError("unpriced cache lifetime")
    return (
        Decimal(".10") * (i - read - write)
        + Decimal(".01") * read
        + Decimal(".125") * write
        + Decimal(".50") * o
    ) / 1_000_000
