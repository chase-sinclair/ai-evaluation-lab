"""Receipt checks, usage pricing and terminal classification for Claude Messages responses.

No provider client. Field names follow the pinned `anthropic` 2.8.0 SDK types.
"""

from decimal import Decimal

from experiments.finops_sql.episode import final
from experiments.model_context.accounting import served_as

from .proposal import HAIKU_THRESHOLD, OUTPUT, PRICES

READABLE = {"text", "thinking", "redacted_thinking"}


def _count(value) -> bool:
    return type(value) is int and value >= 0


def charge(raw: dict, requested: str, input_bound: int) -> Decimal:
    """Verify one receipt and return its usage-priced cost. Raises on any doubt."""
    if requested not in PRICES:
        raise ValueError("unpriced model")
    if raw.get("type") != "message" or raw.get("role") != "assistant":
        raise ValueError("not a message receipt")
    if not served_as(raw.get("model"), requested):
        raise ValueError("unpriced model or tier")
    u = raw.get("usage")
    if not isinstance(u, dict):
        raise ValueError("missing usage")
    i, o = u.get("input_tokens"), u.get("output_tokens")
    write, read = u.get("cache_creation_input_tokens"), u.get("cache_read_input_tokens")
    if not all(_count(n) for n in (i, o, write, read)):
        raise ValueError("token accounting")
    if (
        u.get("service_tier") not in (None, "standard")
        or u.get("speed") not in (None, "standard")
        or u.get("inference_geo") not in (None, "global")
        or u.get("server_tool_use")
    ):
        raise ValueError("unpriced tier, speed, region or tool use")
    split = u.get("cache_creation")
    if split is not None and (
        not isinstance(split, dict)
        or split.get("ephemeral_1h_input_tokens") != 0
        or split.get("ephemeral_5m_input_tokens") != write
    ):
        raise ValueError("unpriced cache lifetime")
    prompt = i + write + read
    if prompt > input_bound or prompt > HAIKU_THRESHOLD or o > OUTPUT:
        raise ValueError("token accounting")
    thinking = (u.get("output_tokens_details") or {}).get("thinking_tokens")
    if thinking is not None and (not _count(thinking) or thinking > o):
        raise ValueError("token accounting")
    p = {k: Decimal(v) for k, v in PRICES[requested].items()}
    return (p["input"] * i + p["cache_read"] * read + p["5m_write"] * write + p["output"] * o) / (
        1_000_000
    )


def terminal(raw: dict) -> dict:
    """Classify an accounted receipt. Raises when the run must stop globally."""
    blocks = raw.get("content")
    if not isinstance(blocks, list) or not all(isinstance(b, dict) for b in blocks):
        raise ValueError("malformed content")
    reason = raw.get("stop_reason")
    if reason == "max_tokens":
        if raw["usage"]["output_tokens"] != OUTPUT:
            raise ValueError("max_tokens below the frozen ceiling")
        return {"kind": "output_exhaustion"}
    if reason == "refusal":
        details = raw.get("stop_details") or {}
        return {"kind": "refusal", "category": details.get("category")}
    if reason != "end_turn":
        raise ValueError(f"unexpected stop reason {reason!r}")
    if any(b.get("type") not in READABLE for b in blocks):
        return {"kind": "invalid_proposals"}
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    return final(text) if text.strip() else {"kind": "missing"}
