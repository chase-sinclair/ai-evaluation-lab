"""Offline Responses workflow. Only a caller-supplied mock HTTP handler can dispatch."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

import httpx
from openai import APIError, OpenAI

from eval_lab.contracts import ModelRequest
from eval_lab.core.hashes import canonical, digest
from eval_lab.providers.openai_adapter import parse_arguments, request_payload

from .packages import OBJECTS, ROOT, SAMPLES, package, tokens

HISTORY_LIMIT = 2048

INSTRUCTIONS = """
You are an analyst for Meridian Cloud Services. Use DuckDB 1.4.4 and UTC as of January 31,
2026. Return exactly one JSON object. For a supported request return
{"kind":"sql","query":"..."} with one read-only SELECT or WITH query. Use the listed report
field aliases in order when returning SQL. Return numeric IDs, amounts in USD, counts in
units, percentages as percent of the stated base and fractions on a 0–1 scale. Use NULL for
undefined ratios. Identify before/after phases with 0/1. Break ranking ties by ascending ID.
For an ambiguous request ask one focused question using
{"kind":"clarify","dimensions":[...],"question":"..."}. Allowed dimensions are period,
cost_basis, scope, savings_basis, denominator and sku. Use only the supplied material. Where
tools are offered you may inspect metadata or examples, one call per turn, up to six. Finish
as soon as ready. Catalog returns public IDs. Describe and examples require an ID previously
returned by catalog or an explicit glossary cross-reference. A discovery history is a record
of local tool interactions. No SQL execution feedback is available."""
TOOLS = []
for name, description, key, prop in [
    (
        "catalog",
        "Search catalog terms; empty search lists tables and grains.",
        "query",
        {"type": "string"},
    ),
    (
        "describe",
        "Describe one to three previously discovered objects.",
        "ids",
        {"type": "array", "items": {"type": "string"}},
    ),
    (
        "examples",
        "Inspect at most three development export records of a discovered table.",
        "table",
        {"type": "string"},
    ),
]:
    TOOLS.append(
        {
            "type": "function",
            "name": name,
            "description": description,
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {key: prop},
                "required": [key],
                "additionalProperties": False,
            },
        }
    )


def body(arm, question, history=()):
    if arm not in "ABCD" or len(arm) != 1 or (history and arm != "D") or len(history) > 6:
        raise ValueError("invalid workflow")
    messages = [
        {"role": "developer", "content": INSTRUCTIONS + package(arm)},
        {
            "role": "user",
            "content": canonical(
                {"question": question["question"], "sql_report_fields": question["fields"]}
            ),
        },
    ]
    for item in history:
        messages.append({"role": "user", "content": "Discovery record " + canonical(item)})
    req = ModelRequest(
        model="gpt-6-luna",
        max_output_tokens=2048,
        messages=messages,
        tools=TOOLS if arm == "D" and len(history) < 6 else [],
    )
    return {
        **request_payload(req),
        "prompt_cache_options": {"ttl": "30m"},
        "reasoning": {"effort": "medium"},
    }


@dataclass
class Discovery:
    known: set[str] = field(default_factory=set)
    history: list = field(default_factory=list)

    def select(self, name, arguments):
        if len(self.history) >= 6:
            raise ValueError("discovery exhausted")
        disclosed = set()
        try:
            if not isinstance(arguments, str) or len(arguments.encode()) > 256:
                raise ValueError
            args = parse_arguments(arguments)
            if not isinstance(args, dict):
                raise ValueError
            if name == "catalog" and set(args) == {"query"} and isinstance(args["query"], str):
                from .packages import catalog

                result = catalog(args["query"], OBJECTS)
                disclosed = set(result)
            elif name == "describe" and set(args) == {"ids"} and isinstance(args["ids"], list):
                ids = args["ids"]
                if (
                    not 1 <= len(ids) <= 3
                    or len(set(ids)) != len(ids)
                    or not set(ids) <= self.known
                ):
                    raise ValueError
                result = {k: OBJECTS[k] for k in ids}
                disclosed = {ref for v in result.values() for ref in v.get("glossary", ())}
            elif name == "examples" and set(args) == {"table"} and args["table"] in self.known:
                result = SAMPLES[args["table"]]
            else:
                raise ValueError
            record = {"tool": name, "arguments": args, "result": result}
            if tokens(result) > 800 or history_bytes(record) > HISTORY_LIMIT:
                raise ValueError
        except (KeyError, TypeError, ValueError):
            record = {
                "error": "Invalid or oversized discovery request",
                "tool": name if name in {t["name"] for t in TOOLS} else "unknown",
            }
            disclosed = set()
        self.known.update(disclosed)
        self.history.append(record)
        return record


def history_bytes(record):
    return (
        len(
            canonical({"role": "user", "content": "Discovery record " + canonical(record)}).encode()
        )
        + 1
    )


def final(text):
    try:
        obj = parse_arguments(text)
        if (
            isinstance(obj, dict)
            and set(obj) == {"kind", "query"}
            and obj["kind"] == "sql"
            and isinstance(obj["query"], str)
            and obj["query"].strip()
        ):
            return obj
        if (
            isinstance(obj, dict)
            and set(obj) == {"kind", "dimensions", "question"}
            and obj["kind"] == "clarify"
            and isinstance(obj["question"], str)
            and obj["question"].strip()
            and isinstance(obj["dimensions"], list)
            and obj["dimensions"]
            and len(set(obj["dimensions"])) == len(obj["dimensions"])
            and set(obj["dimensions"])
            <= {"period", "cost_basis", "scope", "savings_basis", "denominator", "sku"}
        ):
            return obj
    except (ValueError, TypeError):
        pass
    return {"kind": "malformed"}


def save_receipt(destination, turn, receipt):
    with (destination / f"{turn + 1:02}.json").open("x", encoding="utf8") as f:
        json.dump(receipt, f, ensure_ascii=False)


def mock_episode(arm, question, handler, destination: Path):
    frozen = json.loads((ROOT / "proposals/v2/manifest.json").read_bytes())
    seal = frozen.pop("proposal_digest")
    if digest(frozen) != seal:
        raise ValueError("proposal digest mismatch")
    bound = next(
        r for r in frozen["requests"] if r["arm"] == arm and r["question"] == question["id"]
    )
    if digest(body(arm, question)) != bound["body_hash"]:
        raise ValueError("initial body mismatch")
    destination.mkdir(parents=True, exist_ok=False)
    discovery = Discovery()
    with OpenAI(
        api_key="offline",
        base_url="https://offline.invalid/v1",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        for turn in range(7 if arm == "D" else 1):
            payload = body(arm, question, discovery.history)
            if len(canonical(payload).encode()) + 256 > bound["turn_input_bounds"][turn]:
                raise ValueError("turn exceeded proposal allowance")
            receipt = {
                "body": payload,
                "body_hash": digest(payload),
                "turn": turn + 1,
                "proposal_digest": seal,
                "prior_transcript_hash": digest(discovery.history),
            }
            (destination / f"{turn + 1:02}.request").write_bytes(canonical(payload).encode())

            try:
                response = client.responses.create(**payload)
            except APIError as exc:
                receipt["failure"] = type(exc).__name__
                save_receipt(destination, turn, receipt)
                return {"kind": "provider_error"}
            raw = response.model_dump(mode="json")
            receipt["response"] = raw
            if raw["status"] != "completed":
                save_receipt(destination, turn, receipt)
                return {"kind": "incomplete"}
            calls = [x for x in raw["output"] if x["type"] == "function_call"]
            if not calls:
                save_receipt(destination, turn, receipt)
                return final(response.output_text) if response.output_text else {"kind": "missing"}
            if not payload.get("tools") or len(calls) != 1 or response.output_text.strip():
                save_receipt(destination, turn, receipt)
                return {"kind": "invalid_proposals"}
            item = calls[0]
            started = perf_counter()
            record = discovery.select(item["name"], item["arguments"])
            receipt.update(
                discovery=record,
                discovery_seconds=perf_counter() - started,
                arguments_bytes=len(item["arguments"].encode())
                if isinstance(item["arguments"], str)
                else None,
                result_bytes=len(canonical(record.get("result", record)).encode()),
                result_tokens=tokens(record.get("result", record)),
                transcript_hash=digest(discovery.history),
                result_hash=digest(record.get("result", record)),
            )
            save_receipt(destination, turn, receipt)
    raise AssertionError("unreachable")
