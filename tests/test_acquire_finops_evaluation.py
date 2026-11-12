import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path

import httpx
import openai
import pytest

from experiments.finops_sql.evaluation_r1.analysis import replay, report, worksheet
from experiments.finops_sql.packages import OBJECTS, SAMPLES
from experiments.finops_sql.references import QUERIES
from scripts import acquire_finops_evaluation as run


@pytest.fixture(scope="module")
def verified_proposal():
    # Rebuild once, then reuse the read-only plan across transport fault injections.
    return run.preflight(run.APPROVAL)


@pytest.fixture(autouse=True)
def reuse_verified_build(monkeypatch, verified_proposal):
    monkeypatch.setattr(run, "build", lambda: verified_proposal)


@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "http",
        "timeout",
        "missing_tier",
        "missing_reasoning",
        "usage",
        "inconsistent",
        "input_bound",
        "cache",
        "duplicate",
        "incomplete",
        "model",
        "tier",
        "tokens",
        "limit_echo",
        "effort_echo",
        "ttl_split",
        "early",
        "exhaust",
    ],
)
def test_acquisition(tmp_path, fault):
    dest = tmp_path / "once"
    plan, bodies = run.preflight(run.APPROVAL)
    n = episode = depth = 0
    messages = []

    def handler(request):
        nonlocal n, episode, depth
        n += 1
        assert request.extensions["timeout"]["read"] == 900
        assert (dest / f"{n:03}.request-body").read_bytes() == request.content
        actual = json.loads(request.content)
        expected = dict(bodies[episode], input=bodies[episode]["input"] + messages)
        if depth == 6:
            for key in ("tools", "tool_choice", "parallel_tool_calls"):
                expected.pop(key)
        assert actual == expected
        raw = dict(
            id=f"resp_{n}",
            status="completed",
            model="gpt-6-luna",
            service_tier="default",
            output=[],
            usage=dict(
                input_tokens=120,
                output_tokens=15,
                total_tokens=135,
                input_tokens_details=dict(
                    cached_tokens=10,
                    cache_write_tokens=5,
                    cache_write_tokens_details={"ttl_30m_tokens": 5, "ttl_12h_tokens": 0},
                ),
                output_tokens_details=dict(reasoning_tokens=2),
            ),
        )
        if plan["requests"][episode]["arm"] == "D" and depth < (1 if fault == "early" else 6):
            assert actual["tools"]
            name, args = [
                ("catalog", {"query": ""}),
                ("describe", {"ids": ["invoice"]}),
                ("examples", {"table": "invoice"}),
            ][depth % 3]
            raw["output"] = [
                dict(type="function_call", name=name, arguments=json.dumps(args), call_id=f"c{n}")
            ]
            results = {
                "catalog": {k: v["grain"] for k, v in OBJECTS.items() if "grain" in v},
                "describe": {"invoice": OBJECTS["invoice"]},
                "examples": SAMPLES["invoice"],
            }
            record = {"tool": name, "arguments": args, "result": results[name]}
            messages.append(
                {"role": "user", "content": "Discovery record " + run.canonical(record)}
            )
            depth += 1
        else:
            assert not actual.get("tools") or fault == "early"
            q = plan["requests"][episode]["question"]
            answer = {"kind": "clarify", "dimensions": ["scope"], "question": "Which center?"}
            if q == "Q01":
                answer = {"kind": "sql", "query": QUERIES[1]}
            raw["output"] = [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": run.canonical(answer)}],
                }
            ]
            episode += 1
            depth = 0
            messages.clear()
        if fault == "exhaust" and n == 4:
            assert depth == 1 and plan["requests"][episode]["arm"] == "D"
            raw.update(
                status="incomplete", incomplete_details={"reason": "max_output_tokens"}, output=[]
            )
            raw["usage"].update(
                output_tokens=25000,
                total_tokens=25120,
                output_tokens_details={"reasoning_tokens": 25000},
            )
            episode += 1
            depth = 0
            messages.clear()
        if n == 2:
            if fault == "limit_echo":
                raw["max_output_tokens"] = 2048
            if fault == "effort_echo":
                raw["reasoning"] = {"effort": "low"}
            if fault == "ttl_split":
                raw["usage"]["input_tokens_details"]["cache_write_tokens_details"] = {
                    "ttl_30m_tokens": 0,
                    "ttl_12h_tokens": 5,
                }
            if fault == "timeout":
                raise httpx.ReadTimeout("scripted timeout", request=request)
            if fault == "missing_tier":
                raw.pop("service_tier")
            if fault == "missing_reasoning":
                raw["usage"].pop("output_tokens_details")
            if fault == "http":
                return httpx.Response(503, json={"error": {"message": "mock"}})
            if fault == "usage":
                raw.pop("usage")
            if fault == "inconsistent":
                raw["usage"]["total_tokens"] -= 1
            if fault == "input_bound":
                raw["usage"].update(input_tokens=100000, total_tokens=100015)
            if fault == "cache":
                raw["prompt_cache_options"] = {"ttl": "12h"}
            if fault == "duplicate":
                raw["id"] = "resp_1"
            if fault == "incomplete":
                raw["status"] = "incomplete"
                raw["incomplete_details"] = {"reason": "other"}
                raw["usage"].update(
                    output_tokens=25000,
                    total_tokens=25120,
                    output_tokens_details={"reasoning_tokens": 25000},
                )
            if fault == "model":
                raw["model"] = "other"
            if fault == "tier":
                raw["service_tier"] = "priority"
            if fault == "tokens":
                raw["usage"]["output_tokens"] = 25001
        return httpx.Response(200, json=raw)

    def invoke():
        run.acquire(
            run.APPROVAL, "mock", Decimal("5.50"), mock=httpx.MockTransport(handler), dest=dest
        )

    if fault in ("none", "early", "exhaust"):
        invoke()
    else:
        with pytest.raises((ValueError, openai.APIError)):
            invoke()
    seal = json.loads((dest / "seal.json").read_bytes())
    assert (
        n
        == seal["requests_attempted"]
        == ({"none": 360, "early": 180, "exhaust": 354}.get(fault, 2))
    )
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in dest.iterdir()
        if p.name != "seal.json"
    }
    assert hashes == seal["files"] and run.digest(hashes) == seal["ledger_hash"]
    assert (seal["failure"] is None) == (fault in ("none", "early", "exhaust"))
    if fault in ("none", "early", "exhaust"):
        assert seal["finished"] == (143 if fault == "exhaust" else 144)
        assert seal["tools"] == {"none": 216, "early": 36, "exhaust": 210}[fault]
        assert Decimal(seal["remaining_reserve_usd"]) == 0
        assert seal["attempts_without_accounting"] == 0

    ends, stats, depths = replay(dest)
    if fault == "exhaust":
        row = plan["requests"][3]
        assert ends[row["question"] + "D"] == {"kind": "output_exhaustion"}
        event = json.loads((dest / "004.event").read_bytes())
        assert Decimal(event["cost"]) == Decimal(".012511225")
        assert Decimal(event["released_future_usd"]) == run.reserve(
            sum(row["turn_input_bounds"][1:]), 6
        )
        assert seal["exhausted"] == 1 and episode == 144

        if os.getenv("FINOPS_VERIFIED_ROOT"):
            sheet = worksheet(ends)
            assert all(set(item) == {"wording", "question", "adequate"} for item in sheet.values())
            review = {k: item | {"adequate": True} for k, item in sheet.items()}
            summary = report(ends, stats, depths, Path(os.environ["FINOPS_VERIFIED_ROOT"]), review)
            for arm in "ABCD":
                assert summary["arms"][arm]["financial_sql"] == [1, 32]
                assert summary["arms"][arm]["clarification"] == [1, 4]
    if fault == "incomplete":
        assert Decimal(seal["accounted_usd"]) == Decimal(".01252995")
    with pytest.raises((ValueError, openai.APIError)):
        invoke()


def test_no_authority_or_budget(tmp_path):
    def forbidden(request):
        pytest.fail("unapproved HTTP")

    for auth, amount in [
        ("wrong", Decimal("5.50")),
        (run.APPROVAL, run.RESERVE - Decimal(".000001")),
    ]:
        with pytest.raises(ValueError):
            run.acquire(
                auth, "mock", amount, mock=httpx.MockTransport(forbidden), dest=tmp_path / "once"
            )
        assert not (tmp_path / "once").exists()
