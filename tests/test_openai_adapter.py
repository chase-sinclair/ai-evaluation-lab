import json
from types import SimpleNamespace

import pytest

from eval_lab.providers.openai_adapter import OpenAIProvider, parse_arguments, sanitize


@pytest.mark.parametrize("text", ['{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}'])
def test_nonstandard_or_ambiguous_json_is_rejected(text):
    with pytest.raises(ValueError):
        parse_arguments(text)


def payload(arguments='{"invoice_id":"INV-1042"}'):
    return {
        "id": "resp_local",
        "object": "response",
        "created_at": 0,
        "status": "completed",
        "model": "exact-test-model",
        "output": [
            {
                "type": "function_call",
                "id": "fc_local",
                "call_id": "call_local",
                "name": "lookup_invoice",
                "arguments": arguments,
                "status": "completed",
            }
        ],
        "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
        "parallel_tool_calls": False,
        "temperature": 1.0,
    }


def test_structured_response_and_malformed_arguments(experiment, cases):
    request = experiment.build_request(cases["invoice"], experiment.spec.conditions[0])
    captured = []

    def create(**kwargs):
        captured.append(kwargs)
        raw = payload("{broken")
        return SimpleNamespace(model_dump=lambda **_: raw, _request_id="req_local", output_text="")

    provider = OpenAIProvider(
        live=True, client=SimpleNamespace(responses=SimpleNamespace(create=create))
    )
    result = provider.generate(request)
    assert result.parsed["tool_calls"][0]["arguments"] == "{broken"
    assert result.usage.input_tokens == 100 and result.request_id == "req_local"
    assert "malformed_call" in experiment.grade(cases["invoice"], result).diagnostics
    assert captured[0]["store"] is False and captured[0]["parallel_tool_calls"] is False
    assert captured[0]["tools"] == request.tools
    assert "temperature" not in captured[0]
    with pytest.raises(ValueError, match="unsupported"):
        provider.generate(request.model_copy(update={"options": {"temperature": 0}}))
    with pytest.raises(ValueError, match="opt-in"):
        OpenAIProvider(live=False)


def test_real_sdk_local_transport(experiment, cases):
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx")
    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json=payload(), headers={"x-request-id": "req_fake"})

    with openai.OpenAI(
        api_key="fake-local-test",
        max_retries=0,
        timeout=60,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        provider = OpenAIProvider(live=True, client=client)
        request = experiment.build_request(cases["invoice"], experiment.spec.conditions[0])
        response = provider.generate(request)
    assert experiment.grade(cases["invoice"], response).passed
    assert response.request_id == "req_fake" and len(captured) == 1


def test_sdk_errors_do_not_retry(experiment, cases):
    openai = pytest.importorskip("openai")
    httpx = pytest.importorskip("httpx")
    attempts = []

    def handler(request):
        attempts.append(request)
        return httpx.Response(429, json={"error": {"message": "test", "type": "rate_limit_error"}})

    with openai.OpenAI(
        api_key="fake",
        max_retries=0,
        timeout=60,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        provider = OpenAIProvider(live=True, client=client)
        request = experiment.build_request(cases["invoice"], experiment.spec.conditions[0])
        with pytest.raises(openai.RateLimitError):
            provider.generate(request)
    assert len(attempts) == 1


def test_secret_sanitization(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    assert sanitize({"api_key": "x", "nested": ["echo test-secret sk-abcdef"]}) == {
        "api_key": "[REDACTED]",
        "nested": ["echo [REDACTED] [REDACTED]"],
    }
