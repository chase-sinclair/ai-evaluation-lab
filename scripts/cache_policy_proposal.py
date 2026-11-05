"""Offline-only Phase 3A policy calculator; deliberately not wired into live execution.

Reported-usage estimates, policy assumptions and spending reserves stay separate.
This module cannot send a request or authorize a run.
"""

from typing import Any

from eval_lab.contracts import CacheUsage, Pricing, Usage
from eval_lab.core.budgets import cost
from eval_lab.core.hashes import canonical, digest
from eval_lab.providers.openai_adapter import normalize_usage

POLICY_VERSION = "phase3a-implicit-30m-v1-proposed"


def request_policy_valid(
    payload: dict, approved_hash: str, pricing: Pricing, *, text_only=False
) -> bool:
    """Freeze the complete actual wire body; allow only the reviewed stateless form."""
    allowed = {
        "model",
        "input",
        "tools",
        "max_output_tokens",
        "store",
        "service_tier",
        "tool_choice",
        "parallel_tool_calls",
        "prompt_cache_options",
    }

    def has_breakpoint(value: Any) -> bool:
        if isinstance(value, dict):
            return "prompt_cache_breakpoint" in value or any(
                has_breakpoint(v) for v in value.values()
            )
        return isinstance(value, list) and any(has_breakpoint(v) for v in value)

    if text_only:
        shape_valid = set(payload) == {
            "model",
            "input",
            "max_output_tokens",
            "store",
            "service_tier",
            "prompt_cache_options",
        }
    else:
        shape_valid = (
            payload.get("parallel_tool_calls") is False
            and payload.get("tool_choice") == "auto"
            and isinstance(payload.get("tools"), list)
            and bool(payload["tools"])
            and all(isinstance(t, dict) and t.get("type") == "function" for t in payload["tools"])
        )
    return (
        digest(payload) == approved_hash
        and len(canonical(payload).encode()) <= 8_000
        and not set(payload) - allowed
        and payload.get("model") == pricing.model
        and payload.get("service_tier") == "default"
        and payload.get("prompt_cache_options") == {"mode": "implicit", "ttl": "30m"}
        and payload.get("store") is False
        and shape_valid
        and type(payload.get("max_output_tokens")) is int
        and 16 <= payload["max_output_tokens"] <= 4096
        and isinstance(payload.get("input"), list)
        and bool(payload["input"])
        and not has_breakpoint(payload)
        and pricing.cache is not None
        and pricing.cache.service_tier == "default"
        and set(pricing.cache.write_usd_per_million) == {"30m", "12h"}
    )


def assess(
    payload: dict, raw: dict, pricing: Pricing, approved_hash: str, *, text_only=False
) -> dict:
    """A testable proposal, not a replacement for the runner's current fail-closed policy."""
    result = {
        "policy_version": POLICY_VERSION,
        "request_hash": digest(payload),
        "pricing_version": pricing.version,
        "provider_reported_cost_usd": None,
        "usage_priced_estimate_usd": None,
        "policy_estimate_usd": None,
        "spending_charge_usd": None,
        "continue_eligible": False,
    }
    if not request_policy_valid(payload, approved_hash, pricing, text_only=text_only):
        return {**result, "stop_reason": "request_or_pricing_policy_violation"}
    rate = max(pricing.input_usd_per_million, *pricing.cache.write_usd_per_million.values())
    reserved = (
        (len(canonical(payload).encode()) + 256) * rate
        + payload["max_output_tokens"] * pricing.output_usd_per_million
    ) / 1e6
    result.update(frozen_request_reserve_usd=reserved, spending_charge_usd=reserved)
    usage = normalize_usage(raw)
    if usage is None or usage.uncached_input_tokens is None:
        return {**result, "stop_reason": "missing_or_inconsistent_usage"}
    result["spending_charge_usd"] = max(
        reserved,
        (usage.input_tokens * rate + usage.output_tokens * pricing.output_usd_per_million) / 1e6,
    )
    result["usage_priced_estimate_usd"] = cost(usage, pricing)
    if usage.output_tokens > payload["max_output_tokens"]:
        return {**result, "stop_reason": "observed_output_limit_violation"}
    if raw.get("status") != "completed" or raw.get("error"):
        return {**result, "stop_reason": "response_not_completed"}
    c = usage.cache
    if c.service_tier != "default":
        return {**result, "stop_reason": "observed_service_tier_violation"}
    options = raw.get("prompt_cache_options") or {}
    if (
        not isinstance(options, dict)
        or options.get("ttl") not in (None, "30m")
        or options.get("mode") not in (None, "implicit")
        or options.get("prewarm") not in (None, False)
        or (c.writes_by_ttl or {}).get("12h", 0) > 0
    ):
        return {**result, "stop_reason": "observed_cache_policy_violation"}
    # Separate counterfactual pricing object; never mutate provider usage or claim inferred TTL.
    assumed = Usage(
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cache=CacheUsage(
            read_tokens=c.read_tokens,
            write_tokens=c.write_tokens,
            writes_by_ttl={"30m": c.write_tokens, "12h": 0},
            minimum_ttl="30m",
            maximum_retention=c.maximum_retention,
            service_tier="default",
        ),
    )
    result.update(
        policy_estimate_usd=cost(assumed, pricing),
        continue_eligible=True,
        assumption=(
            "All writes follow the explicitly requested 30m policy; no explicit breakpoints."
        ),
        reported_minimum_ttl=c.minimum_ttl,
        reported_maximum_retention=c.maximum_retention,
        write_lifetime_evidence="reported_breakdown" if c.writes_by_ttl is not None else "unknown",
    )
    return result
