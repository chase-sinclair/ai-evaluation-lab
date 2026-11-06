import importlib
import json
from pathlib import Path

import httpx
import openai
import pytest

from eval_lab.core.hashes import digest
from eval_lab.core.registry import load

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def exp():
    return load("catalog_scope_v2", ROOT / "experiments")


@pytest.mark.parametrize("wrong_model", [False, True])
def test_frozen_sdk_transport_and_reporting(exp, tmp_path, monkeypatch, wrong_model):
    """Script SDK responses locally; no model, account or tool is invoked."""
    plan = json.loads((exp.directory / "request-manifest.json").read_bytes())
    monkeypatch.syspath_prepend(str(ROOT))
    execute = importlib.import_module("experiments.catalog_scope_v2.approved_run").execute
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
        if calls and calls[0]["name"] in row["tools"]:
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
    assert len(seen) == 216 and summary["correct"] == 216
    report = importlib.import_module("experiments.catalog_scope_v2.report").report(
        Path(summary["path"])
    )
    cohorts = report["cohorts"]
    assert [g["scenario_count"] for g in cohorts.values()] == [12, 18, 6]
    assert cohorts["capability"]["catalogs"][10]["coverage"]["outcomes"] == {
        "safe_abstention": 8,
        "fulfilled": 4,
    }
    assert cohorts["primary"]["paired_changes"]["5_to_20"] == {"unchanged": 36}
    assert cohorts["primary"]["scenarios"]["N03"][5] == {"A": "passed", "B": "passed"}


def test_control_parity_mirrors_and_unsupported_write(exp):
    from eval_lab.contracts import ModelResponse

    originals = {c.id: c for c in exp.v1.load_cases()}
    cases = {c.id: c for c in exp.load_cases()}
    for case in cases.values():
        for a, b in zip(exp.spec.conditions[::2], exp.spec.conditions[1::2], strict=True):
            first = exp.build_request(case, a)
            second = exp.build_request(case, b)
            assert first.tools == second.tools[::-1] and first.messages == second.messages
            if case.id in originals:
                assert first == exp.v1.build_request(originals[case.id], a)
                assert case.ground_truth == originals[case.id].ground_truth
    c = cases["C03"]
    req = exp.build_request(c, exp.spec.conditions[0])
    wrong = {"name": "move_dock_slot", "arguments": c.ground_truth["tool_calls"][0]["arguments"]}
    g = exp.grade(c, ModelResponse(parsed={"tool_calls": [wrong]}), request=req)
    assert (
        not g.passed and g.submetrics["unsafe_substitution"] and g.submetrics["unauthorized_write"]
    )
    assert not g.submetrics["fulfilled"]
    assert all(cases[k].ground_truth == {"tool_calls": []} for k in ("N03", "N05"))
