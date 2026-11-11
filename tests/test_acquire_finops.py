import json
from decimal import Decimal

import httpx
import openai
import pytest

from experiments.finops_sql.packages import OBJECTS, SAMPLES
from scripts import acquire_finops as run


@pytest.mark.parametrize(
    "fault",
    [
        "none",
        "http",
        "usage",
        "inconsistent",
        "input_bound",
        "cache",
        "duplicate",
        "incomplete",
        "model",
        "tier",
        "tokens",
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
        actual = json.loads(request.content)
        expected = dict(bodies[episode], input=bodies[episode]["input"] + messages)
        if depth == 6:
            for key in ("tools", "tool_choice", "parallel_tool_calls"):
                expected.pop(key)
        assert actual == expected
        raw = dict(
            id=f"r{n}",
            status="completed",
            model="gpt-6-luna",
            service_tier="default",
            output=[],
            usage=dict(
                input_tokens=120,
                output_tokens=15,
                total_tokens=135,
                input_tokens_details=dict(cached_tokens=10, cache_write_tokens=5),
                output_tokens_details=dict(reasoning_tokens=2),
            ),
        )
        if plan["requests"][episode]["arm"] == "D" and depth < 6:
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
            assert "tools" not in actual
            if episode % 4 == 1:
                raw["output"] = [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "invalid JSON"}],
                    }
                ]
            elif episode % 4 == 2:
                raw["output"] = [
                    {
                        "type": "function_call",
                        "name": "catalog",
                        "arguments": "{}",
                        "call_id": f"c{j}",
                    }
                    for j in range(2)
                ]
            elif episode % 4 == 3:
                raw["output"] = [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "output_text",
                                "text": run.canonical({"kind": "sql", "query": "SELECT 1"}),
                            }
                        ],
                    }
                ]
            episode += 1
            depth = 0
            messages.clear()
        if n == 2:
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
                raw["id"] = "r1"
            if fault == "incomplete":
                raw["status"] = "incomplete"
            if fault == "model":
                raw["model"] = "other"
            if fault == "tier":
                raw["service_tier"] = "priority"
            if fault == "tokens":
                raw["usage"]["output_tokens"] = 2049
        return httpx.Response(200, json=raw)

    def invoke():
        run.acquire(run.APPROVAL, "mock", Decimal(1), mock=httpx.MockTransport(handler), dest=dest)

    if fault == "none":
        invoke()
    else:
        with pytest.raises((ValueError, openai.APIError)):
            invoke()
    seal = json.loads((dest / "seal.json").read_bytes())
    assert n == seal["requests_attempted"] == (360 if fault == "none" else 2)
    assert (seal["failure"] is None) == (fault == "none")
    if fault == "none":
        assert seal["finished"] == 144 and seal["tools"] == 216
        finals = [json.loads(p.read_bytes()).get("final") for p in dest.glob("*.event")]
        assert {x["kind"] for x in finals if x} == {
            "missing",
            "malformed",
            "invalid_proposals",
            "sql",
        }
    with pytest.raises((ValueError, openai.APIError)):
        invoke()


def test_no_authority_or_budget(tmp_path):
    def forbidden(request):
        pytest.fail("unapproved HTTP")

    for auth, amount in [("wrong", Decimal(1)), (run.APPROVAL, run.RESERVE - Decimal(".000001"))]:
        with pytest.raises(ValueError):
            run.acquire(
                auth, "mock", amount, mock=httpx.MockTransport(forbidden), dest=tmp_path / "once"
            )
        assert not (tmp_path / "once").exists()
