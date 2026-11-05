"""Optional single-call Responses adapter. Construction requires explicit live opt-in."""

import json
import os
import re

from pydantic import ValidationError

from eval_lab.contracts import CacheUsage, ModelRequest, ModelResponse, Usage


def normalize_usage(raw: dict) -> Usage | None:
    """Read additive SDK fields from raw JSON; preserve unknowns and reject bad totals."""
    usage = raw.get("usage")
    if not usage:
        return None
    try:
        details = usage.get("input_tokens_details") or {}
        writes = details.get("cache_write_tokens_details")
        if writes is not None:
            # Require both counters; an omitted/new lifetime must not be priced as zero.
            if set(writes) != {"ttl_30m_tokens", "ttl_12h_tokens"}:
                return None
            writes = {"30m": writes["ttl_30m_tokens"], "12h": writes["ttl_12h_tokens"]}
        return Usage(
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
            cache=CacheUsage(
                read_tokens=details.get("cached_tokens"),
                write_tokens=details.get("cache_write_tokens"),
                writes_by_ttl=writes,
                minimum_ttl=(raw.get("prompt_cache_options") or {}).get("ttl"),
                maximum_retention=raw.get("prompt_cache_retention"),
                service_tier=raw.get("service_tier"),
            ),
        )
    except (KeyError, TypeError, AttributeError, ValidationError):
        return None  # Raw usage remains available for review; runner stops on uncertainty.


def parse_arguments(text):
    def reject_constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON argument key")
            result[key] = value
        return result

    return json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_object)


def sanitize(value):
    """Remove credentials; retain response payloads, never headers or exception bodies."""
    secret = os.environ.get("OPENAI_API_KEY", "")
    if isinstance(value, dict):
        return {
            k: "[REDACTED]"
            if k.lower() in {"api_key", "authorization", "access_token"}
            else sanitize(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        value = value.replace(secret, "[REDACTED]") if secret else value
        return re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED]", value)
    return value


def request_payload(request: ModelRequest) -> dict:
    """Exact Responses body, also inspectable offline before an approved execution."""
    if request.options:
        raise ValueError("Optional inference parameters are unsupported; none are discarded")
    kwargs = {
        "model": request.model,
        "input": request.messages,
        "max_output_tokens": request.max_output_tokens,
        "store": False,
        "service_tier": "default",  # Explicit standard tier for the verified price snapshot.
    }
    if request.tools:
        kwargs["tools"] = request.tools
        kwargs["tool_choice"] = "auto"
        kwargs["parallel_tool_calls"] = False
    return kwargs


class OpenAIProvider:
    def __init__(self, *, live: bool, client=None):
        if not live:
            raise ValueError("Explicit live opt-in required")
        if client is None:
            from openai import OpenAI

            client = OpenAI(max_retries=0, timeout=60.0)
        self.client = client

    def payload(self, request: ModelRequest) -> dict:
        return request_payload(request)

    def generate(self, request: ModelRequest) -> ModelResponse:
        kwargs = self.payload(request)
        response = self.client.responses.create(**kwargs)
        raw = sanitize(response.model_dump(mode="json"))
        calls = []
        for item in raw.get("output", []):
            if item.get("type") == "function_call":
                arguments = item.get("arguments")
                try:
                    arguments = parse_arguments(arguments)
                except (TypeError, ValueError):
                    pass  # Grader sees malformed arguments, never silently converts to no-call.
                calls.append({"name": item.get("name"), "arguments": arguments})
        parsed = {"tool_calls": calls, "text": getattr(response, "output_text", "")}
        if request.output_format == "text":
            parsed = parsed["text"]
        return ModelResponse(
            raw=raw,
            parsed=sanitize(parsed),
            finish_status="unexpected_tool_calls"
            if request.output_format == "text" and calls
            else raw.get("status", "unknown"),
            usage=normalize_usage(raw),
            request_id=getattr(response, "_request_id", None),
            model=raw.get("model"),
            effective_options={
                "sent": {k: v for k, v in kwargs.items() if k not in {"input", "tools"}},
                "reported": {
                    k: raw[k]
                    for k in (
                        "temperature",
                        "top_p",
                        "reasoning",
                        "max_output_tokens",
                        "parallel_tool_calls",
                        "service_tier",
                        "prompt_cache_options",
                        "prompt_cache_retention",
                    )
                    if k in raw
                },
            },
            error="provider_response_error" if raw.get("error") else None,
        )
