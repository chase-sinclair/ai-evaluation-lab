import importlib
import json
from pathlib import Path

import httpx
import openai
import pytest

from eval_lab.contracts import ModelResponse
from eval_lab.core.hashes import digest
from eval_lab.core.registry import load

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def exp():
    return load("catalog_scope", ROOT / "experiments")


def test_frozen_treatments_and_order(exp, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    freeze = importlib.import_module("experiments.catalog_scope.freeze")
    plan = freeze.build()
    assert plan == json.loads(freeze.FILE.read_bytes())
    assert 0 < plan["conservative_reserve_usd"] <= plan["spec"]["max_spend_usd"]
    assert len(plan["trials_in_run_order"]) == plan["spec"]["max_requests"] == 36
    assert exp.spec.max_spend_usd == 0
    cases = exp.load_cases()
    positions = {5: [], 10: [], 20: []}
    for case in cases:
        previous = {}
        for cond in exp.spec.conditions:
            request = exp.build_request(case, cond)
            # Replacing the answer key cannot change any request.
            hidden = case.model_copy(update={"ground_truth": {}})
            assert exp.build_request(hidden, cond) == request
            tools = {t["name"]: t for t in request.tools}
            n = cond.variables["tool_count"]
            assert len(tools) == len(request.tools) == n
            assert all(tools[name] == schema for name, schema in previous.items())
            assert request.messages[-1] == {"role": "user", "content": case.task_input["text"]}
            if case.ground_truth["tool_calls"]:
                positions[n].append(list(tools).index(case.provenance["focus"]))
            previous = tools
    for n, ranks in positions.items():
        assert sorted(ranks) == [(2 * i + 1) * n // 16 for i in range(8)]
    assert len({r["body_sha256"] for r in plan["trials_in_run_order"]}) == 36


@pytest.mark.parametrize(
    ("case_id", "name", "args", "expected", "valid"),
    [
        ("arrival-west", "shipment_eta", {"shipment_id": "SH-214"}, None, True),
        ("arrival-west", "shipment_eta", {"shipment_id": "SH-215"}, "wrong_arguments", True),
        ("arrival-west", "shipment_eta", {"shipment_id": 214}, "invalid_arguments", False),
        ("arrival-west", "shipment_eta", "broken JSON", "invalid_arguments", False),
        ("arrival-west", "invoice_balance", {"invoice_id": "FI-771"}, "wrong_tool_or_count", True),
        ("arrival-west", "shipment_carrier", {"shipment_id": "SH-214"}, "unoffered_tool", False),
        ("arrival-west", None, None, "missed_call", True),
        ("draft-only", None, None, None, True),
        ("draft-only", "shipment_eta", {"shipment_id": "SH-460"}, "unnecessary_call", True),
    ],
)
def test_actual_calls_and_exact_keys(exp, case_id, name, args, expected, valid):
    case = next(c for c in exp.load_cases() if c.id == case_id)
    calls = [{"name": name, "arguments": args}] if name else []
    response = ModelResponse(parsed={"tool_calls": calls, "text": "I would call shipment_eta"})
    result = exp.grade(case, response, request=exp.build_request(case, exp.spec.conditions[0]))
    assert result.passed == (expected is None)
    assert result.valid_output == valid
    if expected:
        assert expected in result.diagnostics


@pytest.mark.parametrize(
    "response",
    [
        ModelResponse(parsed={"tool_calls": []}, raw={"output": []}),
        ModelResponse(
            parsed={"tool_calls": []}, raw={"output": [{"content": [{"type": "refusal"}]}]}
        ),
        ModelResponse(parsed={"tool_calls": []}, finish_status="incomplete"),
        ModelResponse(parsed={"tool_calls": "none"}),
        ModelResponse(
            parsed={"tool_calls": [{"name": "shipment_eta", "arguments": {"shipment_id": "X"}}] * 2}
        ),
    ],
)
def test_invalid_responses_never_pass_no_call(exp, response):
    case = next(c for c in exp.load_cases() if c.id == "conditional-hold")
    result = exp.grade(case, response, request=exp.build_request(case, exp.spec.conditions[0]))
    assert not result.passed and not result.valid_output


@pytest.mark.parametrize("wrong_model", [False, True])
def test_frozen_sdk_transport_and_reporting(exp, tmp_path, monkeypatch, wrong_model):
    """Script SDK responses locally; no model, account or tool is invoked."""
    plan = json.loads((exp.directory / "request-manifest.json").read_bytes())
    monkeypatch.syspath_prepend(str(ROOT))
    execute = importlib.import_module("experiments.catalog_scope.approved_run").execute
    cases = {c.id: c for c in exp.load_cases()}
    seen = []

    def transport(req):
        row = plan["trials_in_run_order"][len(seen)]
        body = json.loads(req.content)
        expected_body = dict(
            plan["body_settings"],
            input=plan["messages_by_case"][row["case"]],
            tools=[plan["functions_by_name"][name] for name in row["tools"]],
        )
        assert body == expected_body and digest(body) == row["body_sha256"]
        assert body["parallel_tool_calls"] is False and body["tool_choice"] == "auto"
        seen.append(row["case"])
        calls = cases[row["case"]].ground_truth["tool_calls"]
        if calls:
            output = [
                {
                    "type": "function_call",
                    "name": calls[0]["name"],
                    "arguments": json.dumps(calls[0]["arguments"]),
                    "call_id": "test",
                    "id": "fc_test",
                    "status": "completed",
                }
            ]
        else:
            output = [
                {
                    "type": "message",
                    "role": "assistant",
                    "id": "msg_test",
                    "status": "completed",
                    "content": [
                        {"type": "output_text", "text": "Local no-call fixture.", "annotations": []}
                    ],
                }
            ]
        return httpx.Response(
            200,
            json={
                "object": "response",
                "id": "resp_fixture",
                "created_at": 0,
                "model": "unexpected-model" if wrong_model else body["model"],
                "status": "completed",
                "output": output,
                "service_tier": "default",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "total_tokens": 120,
                    "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
                },
            },
        )

    with openai.OpenAI(
        api_key="local-fixture",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(transport)),
    ) as client:
        with pytest.raises(ValueError, match="digest"):
            execute("unapproved", tmp_path, client)
        assert not seen
        summary = execute(digest(plan), tmp_path, client)
        with pytest.raises(FileExistsError):
            execute(digest(plan), tmp_path, client)
    if wrong_model:
        assert len(seen) == 1 and summary["run_status"] == "failed"
        return
    assert len(seen) == 36 and summary["correct"] == 36
    assert len(summary["paired_comparisons"]) == 3
    for metrics in summary["conditions"].values():
        assert metrics["unique_cases_recorded"] == 12
        assert metrics["known_input_tokens"] == 1200 and metrics["known_output_tokens"] == 240
        assert metrics["estimated_cost_usd"] == pytest.approx(0.00024)
        assert metrics["diagnostic_metrics"]["unnecessary_call_on_no_call"]["measured_records"] == 4
        assert metrics["diagnostic_metrics"]["correct_tool_on_required"]["measured_records"] == 8
