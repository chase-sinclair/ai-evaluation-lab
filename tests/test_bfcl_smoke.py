import importlib
import json

import httpx
import openai
import pytest

from eval_lab.contracts import ModelResponse
from eval_lab.core.hashes import digest
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run, validate
from eval_lab.providers.openai_adapter import OpenAIProvider, request_payload


@pytest.fixture
def smoke_module(experiment):
    return importlib.import_module("_eval_experiment_tool_selection.smoke_bfcl")


@pytest.fixture
def smoke(smoke_module):
    return smoke_module.SmokeExperiment()


@pytest.mark.parametrize("count,valid", [(5, False), (30, True)])
def test_offered_context_changes_classification(smoke, count, valid):
    case = next(c for c in smoke.load_cases() if c.id == "simple_python_0")
    condition = next(c for c in smoke.spec.conditions if c.variables["tool_count"] == count)
    request = smoke.build_request(case, condition)
    response = ModelResponse(
        parsed={
            "tool_calls": [{"name": "lookup_record_warehouse", "arguments": {"record_id": "X"}}]
        }
    )
    result = smoke.grade(case, response, request=request)
    assert result.valid_output is valid and not result.passed
    if not valid:
        assert result.diagnostics == ["unoffered_function"]
    with pytest.raises(ValueError, match="actual request"):
        smoke.grade(case, response)


@pytest.mark.parametrize("arguments", ["{}", {}, {"base": True, "height": 5}])
def test_offered_target_malformed_arguments(smoke, arguments):
    case = next(c for c in smoke.load_cases() if c.id == "simple_python_0")
    request = smoke.build_request(case, smoke.spec.conditions[0])
    result = smoke.grade(
        case,
        ModelResponse(
            parsed={"tool_calls": [{"name": "calculate_triangle_area", "arguments": arguments}]}
        ),
        request=request,
    )
    assert not result.valid_output and not result.passed


def test_preflight_is_exact_frozen_six_and_never_constructs_provider(smoke_module, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Preflight constructed live provider")

    monkeypatch.setattr(smoke_module, "live_provider", forbidden)
    monkeypatch.setattr("sys.argv", ["smoke_bfcl", "--preflight"])
    smoke_module.main()
    report = smoke_module.preflight_report(smoke_module.SmokeExperiment())
    smoke_module.verify_readiness(report)
    assert report["planned_trials"] == 6 and report["provider_calls"] == 0
    assert report["projected_cost_usd"] == pytest.approx(0.016662)
    assert report["cache_write_conservative_cost_usd"] < 0.05
    assert report["output_token_ceiling"] == 6 * 4096
    report["requests"][0]["responses_body_hash"] = "changed"
    with pytest.raises(ValueError, match="readiness"):
        smoke_module.verify_readiness(report)


def test_smoke_refuses_config_or_request_drift(smoke, tmp_path):
    case = smoke.load_cases()[0].model_copy(deep=True)
    case.task_input["messages"][0]["content"] = "changed"
    with pytest.raises(ValueError, match="frozen payload"):
        smoke.build_request(case, smoke.spec.conditions[0])
    with pytest.raises(ValueError, match="opt-in"):
        run(smoke, results=tmp_path, mode="live", dry_run=True)
    smoke.spec = smoke.spec.model_copy(update={"max_requests": 54})
    with pytest.raises(ValueError, match="configuration changed"):
        validate(smoke)


@pytest.mark.parametrize("bad_order", [[], [("irrelevance_0", "tools_30", 0)] * 6])
def test_explicit_order_cannot_drop_duplicate_or_add_trials(smoke, tmp_path, bad_order):
    with pytest.raises(ValueError, match="exact permutation"):
        run(smoke, results=tmp_path, mode="live", live=True, dry_run=True, trial_order=bad_order)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("wrong_tool", [False, True])
def test_six_real_sdk_transport_calls_through_runner(smoke, smoke_module, tmp_path, wrong_tool):
    # Real SDK, local transport, scripted outputs only. No remote requests or paid usage.
    cases = {c.id: c for c in smoke.load_cases()}
    grader = importlib.import_module("_eval_experiment_tool_selection.bfcl_grader")
    expected_bodies = []
    for case_id, condition_id, _ in smoke.trial_order:
        condition = next(c for c in smoke.spec.conditions if c.id == condition_id)
        expected_bodies.append(request_payload(smoke.build_request(cases[case_id], condition)))
    captured = []

    def handler(request):
        index = len(captured)
        body = json.loads(request.content)
        captured.append(body)
        assert body == expected_bodies[index]
        assert request.url.path == "/v1/responses"
        assert body["service_tier"] == "default"
        assert body["store"] is False and body["parallel_tool_calls"] is False
        case = cases[smoke.trial_order[index][0]]
        calls = grader.answer_variants(case)[0]["tool_calls"]
        if wrong_tool:
            calls = [{"name": "lookup_record_warehouse", "arguments": {"record_id": "X"}}]
        return httpx.Response(
            200,
            json={
                "id": "resp_fake",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "gpt-6-luna",
                "output": [
                    {
                        "type": "function_call",
                        "id": "fc_fake",
                        "call_id": "call_fake",
                        "name": c["name"],
                        "arguments": json.dumps(c["arguments"]),
                        "status": "completed",
                    }
                    for c in calls
                ],
                "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
            },
        )

    with openai.OpenAI(
        api_key="fake-local-test",
        max_retries=0,
        timeout=60,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        report = run(
            smoke,
            results=tmp_path,
            mode="live",
            live=True,
            run_id=smoke_module.RUN_ID,
            trial_order=smoke.trial_order,
            provider_factory=lambda: OpenAIProvider(live=True, client=client),
        )
        with pytest.raises(FileExistsError):
            run(
                smoke,
                results=tmp_path,
                mode="live",
                live=True,
                run_id=smoke_module.RUN_ID,
                trial_order=smoke.trial_order,
                provider_factory=lambda: OpenAIProvider(live=True, client=client),
            )
    assert len(captured) == 6 and report["recorded"] == 6
    assert report["status_counts"] == (
        {"invalid_output": 3, "task_failed": 3} if wrong_tool else {"passed": 6}
    )
    records, warnings = read_records(tmp_path / smoke_module.RUN_ID)
    assert not warnings
    assert [(r.case_id, r.condition_id, r.repeat) for r in records] == smoke.trial_order
    assert all(r.grade.grader_version == "0.2.1" for r in records)
    readiness = smoke_module.preflight_report(smoke)
    assert [digest(body) for body in captured] == [
        row["responses_body_hash"] for row in readiness["requests"]
    ]
