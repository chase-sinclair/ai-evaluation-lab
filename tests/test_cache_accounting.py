import copy
import json

import httpx
import openai
import pytest
from pydantic import ValidationError
from test_budget import live_spec

from eval_lab.contracts import CachePricing, CacheUsage, ModelResponse, Pricing, Usage
from eval_lab.core.budgets import (
    cost,
    cost_details,
    estimate_cost,
    estimate_input_tokens,
    preflight,
)
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run
from eval_lab.providers.openai_adapter import OpenAIProvider, normalize_usage


@pytest.fixture
def pricing():
    return Pricing(
        version="test-rates-v1",
        verified_date="2026-11-04",
        source_url="https://example.test",
        model="test-model",
        input_usd_per_million=1,
        output_usd_per_million=5,
        cache=CachePricing(
            service_tier="default",
            read_usd_per_million=0.1,
            write_usd_per_million={"30m": 1.25, "12h": 2.5},
        ),
    )


def raw_usage():
    return {
        "service_tier": "default",
        "prompt_cache_retention": "24h",
        "prompt_cache_options": {"ttl": "30m"},
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 100,
            "output_tokens_details": {"reasoning_tokens": 40},
            "input_tokens_details": {
                "cached_tokens": 200,
                "cache_write_tokens": 500,
                "cache_write_tokens_details": {"ttl_30m_tokens": 400, "ttl_12h_tokens": 100},
            },
        },
    }


def test_mixed_lifetimes_are_partitioned_once(pricing):
    usage = normalize_usage(raw_usage())
    assert usage.uncached_input_tokens == 300
    details = cost_details(usage, pricing)
    assert details["component_costs_usd"] == pytest.approx(
        {
            "uncached_input": 0.0003,
            "cached_read": 0.00002,
            "cache_write": 0.00075,
            "output": 0.0005,
        }
    )
    assert cost(usage, pricing) == pytest.approx(0.00157)
    assert details["minimum_ttl"] == "30m" and details["maximum_retention"] == "24h"
    assert details["writes_by_ttl"] == {"30m": 400, "12h": 100}
    assert details["pricing_version"] == "test-rates-v1"
    assert details["pricing_service_tier"] == "default"


@pytest.mark.parametrize(
    "change,issue",
    [
        ("counts", "missing_cache_counters"),
        ("ttl", "missing_write_lifetime_breakdown"),
        ("tier", "unknown_or_mismatched_service_tier"),
        ("prices", "missing_cache_prices"),
        ("rate", "missing_write_lifetime_price"),
    ],
)
def test_unknowns_are_not_zero_cost(pricing, change, issue):
    raw = raw_usage()
    details = raw["usage"]["input_tokens_details"]
    if change == "counts":
        del details["cached_tokens"]
    elif change == "ttl":
        del details["cache_write_tokens_details"]
    elif change == "tier":
        raw["service_tier"] = "priority"
    elif change == "prices":
        pricing = pricing.model_copy(update={"cache": None})
    else:
        pricing = pricing.model_copy(
            update={
                "cache": pricing.cache.model_copy(update={"write_usd_per_million": {"30m": 1.25}})
            }
        )
    result = cost_details(normalize_usage(raw), pricing)
    assert result["estimated_cost_usd"] is None and result["issue"] == issue


@pytest.mark.parametrize("value", [-1, True, 1.5, "100"])
def test_invalid_counter_types_preserve_raw_and_abstain(value):
    raw = raw_usage()
    raw["usage"]["input_tokens_details"]["cached_tokens"] = value
    original = copy.deepcopy(raw)
    assert normalize_usage(raw) is None and raw == original


def test_inconsistent_counters_and_unknown_ttl():
    raw = raw_usage()
    raw["usage"]["input_tokens_details"]["cache_write_tokens"] = 501
    assert normalize_usage(raw) is None
    raw = raw_usage()
    raw["usage"]["input_tokens"] = 100
    assert normalize_usage(raw) is None
    raw = raw_usage()
    raw["usage"]["input_tokens_details"]["cache_write_tokens_details"]["ttl_24h_tokens"] = 1
    assert normalize_usage(raw) is None
    with pytest.raises(ValidationError):
        Usage(input_tokens=10, output_tokens=0, cache=CacheUsage(read_tokens=11))


def test_no_cache_and_legacy_serialization(pricing):
    legacy = pricing.model_copy(update={"cache": None})
    assert "cache" not in legacy.model_dump()
    usage = Usage(
        input_tokens=100,
        output_tokens=10,
        cache=CacheUsage(read_tokens=0, write_tokens=0, service_tier="default"),
    )
    assert cost(usage, legacy) == pytest.approx(0.00015)
    assert (
        cost_details(Usage(input_tokens=100, output_tokens=10), legacy)["basis"]
        == "legacy_totals_only"
    )


def test_preflight_reserves_highest_write_rate(pricing, experiment, cases):
    request = experiment.build_request(cases["invoice"], experiment.spec.conditions[0])
    assert estimate_cost(request, pricing) == pytest.approx(
        (estimate_input_tokens(request) * 2.5 + request.max_output_tokens * 5) / 1e6
    )


def test_cache_pricing_requires_usage_details_and_complete_reserve(pricing, experiment):
    assert cost(Usage(input_tokens=100, output_tokens=10), pricing) is None
    spec = live_spec(experiment).model_copy(
        update={
            "pricing": pricing.model_copy(
                update={
                    "cache": pricing.cache.model_copy(
                        update={"write_usd_per_million": {"30m": 1.25}}
                    )
                }
            )
        }
    )
    with pytest.raises(ValueError, match="both write lifetimes"):
        preflight(spec, [], "live", True)


def test_sdk_cache_fields_survive_locked_sdk(experiment, cases, pricing):
    raw = {
        **raw_usage(),
        "id": "resp_fake",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "test-model",
        "output": [],
    }
    with openai.OpenAI(
        api_key="fake",
        max_retries=0,
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda _: httpx.Response(200, json=raw))
        ),
    ) as client:
        response = OpenAIProvider(live=True, client=client).generate(
            experiment.build_request(cases["invoice"], experiment.spec.conditions[0])
        )
    assert cost(response.usage, pricing) == pytest.approx(0.00157)
    assert response.effective_options["reported"]["prompt_cache_options"]["ttl"] == "30m"


def test_live_uncertain_cache_cost_stops_and_preserves_record(experiment, tmp_path):
    experiment.spec = live_spec(experiment)

    class Fake:
        def generate(self, request):
            return ModelResponse(
                parsed={"tool_calls": []}, raw=raw_usage(), usage=normalize_usage(raw_usage())
            )

    result = run(experiment, results=tmp_path, mode="live", live=True, provider_factory=Fake)
    assert result["recorded"] == 1 and result["run_status"] == "failed"
    assert result["estimated_cost_usd"] is None
    records, _ = read_records(tmp_path / result["run_id"])
    assert records[0].cost_details["issue"] == "missing_cache_prices"
    assert records[0].response.raw == raw_usage()
    assert result["known_cache_write_tokens"] == 500
    assert result["cache_partition_records"] == 1
    assert (
        json.loads((tmp_path / result["run_id"] / "manifest.json").read_text())["status"]
        == "failed"
    )
