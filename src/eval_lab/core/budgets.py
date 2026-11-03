"""Conservative preflight estimates and sequential best-effort limits."""

from eval_lab.contracts import ExperimentSpec, ModelRequest, Pricing, Usage
from eval_lab.core.hashes import canonical


def estimate_input_tokens(request: ModelRequest) -> int:
    # Deliberately conservative heuristic; includes serialized schemas and framing reserve.
    return len(canonical(request).encode("utf-8")) + 256


def cost(usage: Usage, pricing: Pricing) -> float:
    return (
        usage.input_tokens * pricing.input_usd_per_million
        + usage.output_tokens * pricing.output_usd_per_million
    ) / 1_000_000


def estimate_cost(request: ModelRequest, pricing: Pricing | None) -> float:
    if pricing is None:
        return 0.0
    return cost(
        Usage(input_tokens=estimate_input_tokens(request), output_tokens=request.max_output_tokens),
        pricing,
    )


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
    estimate = sum(estimate_cost(r, spec.pricing) for r in requests)
    if estimate > spec.max_spend_usd:
        raise ValueError("Projected spend exceeds max_spend_usd")
    return estimate
