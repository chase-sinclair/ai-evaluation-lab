"""Conservative preflight estimates and sequential best-effort limits."""

from eval_lab.contracts import ExperimentSpec, ModelRequest, Pricing, Usage
from eval_lab.core.hashes import canonical


def estimate_input_tokens(request: ModelRequest) -> int:
    # Deliberately conservative heuristic; includes serialized schemas and framing reserve.
    return len(canonical(request).encode("utf-8")) + 256


def cost_details(usage: Usage, pricing: Pricing) -> dict:
    """Partition input once. Unknown counters/rates never silently become free tokens."""
    result = {
        "pricing_version": pricing.version,
        "pricing_source_url": pricing.source_url,
        "pricing_verified_date": pricing.verified_date,
        "pricing_service_tier": pricing.cache.service_tier if pricing.cache else None,
        "estimated_cost_usd": None,
    }
    c = usage.cache
    if c is None:
        if pricing.cache is not None:
            return {**result, "issue": "missing_cache_counters"}
        # Compatibility for legacy records and providers with totals-only contracts.
        result.update(
            basis="legacy_totals_only",
            estimated_cost_usd=(
                usage.input_tokens * pricing.input_usd_per_million
                + usage.output_tokens * pricing.output_usd_per_million
            )
            / 1e6,
        )
        return result
    result.update(
        basis="reported_cache_partition",
        service_tier=c.service_tier,
        minimum_ttl=c.minimum_ttl,
        maximum_retention=c.maximum_retention,
        uncached_input_tokens=usage.uncached_input_tokens,
        cached_read_tokens=c.read_tokens,
        cache_write_tokens=c.write_tokens,
        writes_by_ttl=c.writes_by_ttl,
        output_tokens=usage.output_tokens,
    )
    if usage.uncached_input_tokens is None:
        return {**result, "issue": "missing_cache_counters"}
    if c.service_tier != (pricing.cache.service_tier if pricing.cache else "default"):
        return {**result, "issue": "unknown_or_mismatched_service_tier"}
    if (c.read_tokens or c.write_tokens) and pricing.cache is None:
        return {**result, "issue": "missing_cache_prices"}
    writes = c.writes_by_ttl
    if c.write_tokens and writes is None:
        # A response-level TTL is not proof that every explicit breakpoint used it.
        return {**result, "issue": "missing_write_lifetime_breakdown"}
    writes = writes or {}
    if pricing.cache and any(ttl not in pricing.cache.write_usd_per_million for ttl in writes):
        return {**result, "issue": "missing_write_lifetime_price"}
    components = {
        "uncached_input": usage.uncached_input_tokens * pricing.input_usd_per_million / 1e6,
        "cached_read": c.read_tokens * pricing.cache.read_usd_per_million / 1e6
        if pricing.cache
        else 0.0,
        "cache_write": sum(
            n * pricing.cache.write_usd_per_million[ttl] for ttl, n in writes.items()
        )
        / 1e6
        if pricing.cache
        else 0.0,
        "output": usage.output_tokens * pricing.output_usd_per_million / 1e6,
    }
    return {
        **result,
        "writes_by_ttl": writes,
        "component_costs_usd": components,
        "estimated_cost_usd": sum(components.values()),
    }


def cost(usage: Usage, pricing: Pricing) -> float | None:
    return cost_details(usage, pricing)["estimated_cost_usd"]


def estimate_cost(request: ModelRequest, pricing: Pricing | None) -> float:
    if pricing is None:
        return 0.0
    input_rate = max(
        [pricing.input_usd_per_million]
        + (list(pricing.cache.write_usd_per_million.values()) if pricing.cache else [])
    )
    return (
        estimate_input_tokens(request) * input_rate
        + request.max_output_tokens * pricing.output_usd_per_million
    ) / 1e6


def preflight(spec: ExperimentSpec, requests: list[ModelRequest], mode: str, live: bool) -> float:
    if mode not in {"mock", "live"}:
        raise ValueError("Mode must be mock or live")
    if live and mode != "live":
        raise ValueError("--live requires --mode live")
    if len(requests) > spec.max_requests:
        raise ValueError("Planned trials exceed max_requests")
    if mode == "mock":
        if any(c.provider != "mock" or c.model != "deterministic-fixture" for c in spec.conditions):
            raise ValueError("Mock mode requires explicitly configured mock conditions")
        return 0.0
    if not live:
        raise ValueError("Live execution requires explicit --live opt-in")
    if spec.max_spend_usd <= 0 or spec.pricing is None:
        raise ValueError("Live mode requires positive finite spend and a pricing snapshot")
    if any(c.provider != "openai" for c in spec.conditions):
        raise ValueError("Live mode requires openai conditions")
    if any(r.model != spec.pricing.model for r in requests):
        raise ValueError("Pricing snapshot must match every exact model ID")
    if any(r.options for r in requests):
        raise ValueError("This adapter does not support optional inference settings yet")
    if spec.pricing.cache and (
        spec.pricing.cache.service_tier != "default"
        or set(spec.pricing.cache.write_usd_per_million) != {"30m", "12h"}
    ):
        raise ValueError("Cache pricing must cover the standard tier and both write lifetimes")
    estimate = sum(estimate_cost(r, spec.pricing) for r in requests)
    if estimate > spec.max_spend_usd:
        raise ValueError("Projected spend exceeds max_spend_usd")
    return estimate
