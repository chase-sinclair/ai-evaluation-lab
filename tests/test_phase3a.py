import copy
import importlib
from pathlib import Path

import httpx
import openai
import pytest

from eval_lab.contracts import CachePricing, Pricing
from eval_lab.core.hashes import digest


@pytest.fixture
def assess(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("scripts.cache_policy_proposal").assess


@pytest.fixture
def audit_phase3a(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    return importlib.import_module("scripts.audit_phase3a")


@pytest.fixture
def pricing():
    return Pricing(
        version="proposal-test",
        verified_date="2026-11-04",
        source_url="https://developers.openai.com/api/docs/pricing",
        model="gpt-6-luna",
        input_usd_per_million=0.1,
        output_usd_per_million=0.5,
        cache=CachePricing(
            service_tier="default",
            read_usd_per_million=0.01,
            write_usd_per_million={"30m": 0.125, "12h": 0.25},
        ),
    )


@pytest.fixture
def payload():
    return {
        "model": "gpt-6-luna",
        "input": [{"role": "user", "content": "test only"}],
        "tools": [{"type": "function", "name": "test", "parameters": {"type": "object"}}],
        "service_tier": "default",
        "store": False,
        "max_output_tokens": 4096,
        "parallel_tool_calls": False,
        "tool_choice": "auto",
        "prompt_cache_options": {"mode": "implicit", "ttl": "30m"},
    }


def response():
    return {
        "id": "resp_fake",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "gpt-6-luna",
        "output": [],
        "service_tier": "default",
        "prompt_cache_retention": "24h",
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 100,
            "input_tokens_details": {"cached_tokens": 200, "cache_write_tokens": 500},
        },
    }


def test_policy_estimate_never_becomes_reported_usage_or_cost(payload, pricing, assess):
    raw = response()
    original = copy.deepcopy(raw)
    result = assess(payload, raw, pricing, digest(payload))
    assert result["continue_eligible"]
    assert result["provider_reported_cost_usd"] is None
    assert result["usage_priced_estimate_usd"] is None
    assert result["policy_estimate_usd"] == pytest.approx(0.0001445)
    assert result["write_lifetime_evidence"] == "unknown"
    assert result["reported_minimum_ttl"] is None
    assert result["reported_maximum_retention"] == "24h"
    assert result["spending_charge_usd"] >= 0.0003
    assert result["spending_charge_usd"] >= result["frozen_request_reserve_usd"]
    assert raw == original


def test_reported_breakdown_and_large_actual_usage(payload, pricing, assess):
    raw = response()
    raw["usage"]["input_tokens_details"]["cache_write_tokens_details"] = {
        "ttl_30m_tokens": 500,
        "ttl_12h_tokens": 0,
    }
    result = assess(payload, raw, pricing, digest(payload))
    assert result["usage_priced_estimate_usd"] == pytest.approx(0.0001445)
    assert result["write_lifetime_evidence"] == "reported_breakdown"
    raw["usage"]["input_tokens"] = 1_000_000
    assert assess(payload, raw, pricing, digest(payload))["spending_charge_usd"] >= 0.25


@pytest.mark.parametrize(
    "change", ["ttl", "breakpoint", "tier", "hash", "previous", "hosted", "size"]
)
def test_actual_request_policy_violations_stop(payload, pricing, change, assess):
    if change == "ttl":
        payload["prompt_cache_options"]["ttl"] = "12h"
    elif change == "breakpoint":
        payload["input"][0]["prompt_cache_breakpoint"] = {"ttl": "12h"}
    elif change == "tier":
        payload["service_tier"] = "priority"
    elif change == "previous":
        payload["previous_response_id"] = "previous"
    elif change == "hosted":
        payload["tools"] = [{"type": "web_search"}]
    elif change == "size":
        payload["input"][0]["content"] = "x" * 8_001
    approved = "mismatch" if change == "hash" else digest(payload)
    result = assess(payload, response(), pricing, approved)
    assert not result["continue_eligible"]
    assert result["stop_reason"] == "request_or_pricing_policy_violation"


@pytest.mark.parametrize(
    "change",
    [
        "tier",
        "missing_tier",
        "ttl",
        "writes",
        "unknown_usage",
        "bad_total",
        "incomplete",
        "output",
        "prewarm",
    ],
)
def test_observed_policy_violations_or_unknown_counters_stop(payload, pricing, change, assess):
    raw = response()
    if change == "tier":
        raw["service_tier"] = "priority"
    elif change == "missing_tier":
        del raw["service_tier"]
    elif change == "ttl":
        raw["prompt_cache_options"] = {"ttl": "12h"}
    elif change == "writes":
        raw["usage"]["input_tokens_details"]["cache_write_tokens_details"] = {
            "ttl_30m_tokens": 499,
            "ttl_12h_tokens": 1,
        }
    elif change == "unknown_usage":
        raw["usage"] = None
    elif change == "bad_total":
        raw["usage"]["input_tokens"] = 2
    elif change == "output":
        raw["usage"]["output_tokens"] = 4097
    elif change == "prewarm":
        raw["prompt_cache_options"] = {"ttl": "30m", "mode": "implicit", "prewarm": True}
    else:
        raw["status"] = "incomplete"
    result = assess(payload, raw, pricing, digest(payload))
    assert not result["continue_eligible"] and result["policy_estimate_usd"] is None
    assert result["spending_charge_usd"] >= result["frozen_request_reserve_usd"]


def test_locked_sdk_sends_explicit_30m_without_breakpoints(payload, pricing, assess):
    import json

    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=response())

    with openai.OpenAI(
        api_key="fake-local-only",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        raw = client.responses.create(**payload).model_dump(mode="json")
    assert captured == [payload]
    assert assess(captured[0], raw, pricing, digest(payload))["continue_eligible"]


def test_bounded_source_audit_reproduces_frozen_evidence(audit_phase3a):
    assert audit_phase3a.audit() == audit_phase3a.load("summary.json")


def test_catalog_cannot_silently_drop_native_tools(monkeypatch, audit_phase3a):
    original = audit_phase3a.load

    def changed(name):
        data = original(name)
        if name == "catalogs.json":
            data["catalogs"][0]["near"].remove("57:1")
        return data

    monkeypatch.setattr(audit_phase3a, "load", changed)
    with pytest.raises(AssertionError):
        audit_phase3a.audit()


def test_source_cache_drift_is_rejected(audit_phase3a, tmp_path):
    (tmp_path / "BFCL_v4_multiple.json").write_text("{}\n")
    with pytest.raises(AssertionError, match="hash mismatch"):
        audit_phase3a.verify_source_cache(tmp_path)
