import copy
import importlib
import json

import httpx
import openai
import pytest
import yaml

from eval_lab.contracts import ModelResponse
from eval_lab.core.hashes import digest
from eval_lab.core.runner import run, validate
from eval_lab.providers.openai_adapter import OpenAIProvider


@pytest.fixture
def bfcl(experiment):
    # Use the same repository discovery/package boundary as the shared runner.
    prepare = importlib.import_module("_eval_experiment_tool_selection.prepare_bfcl")
    return prepare.load_experiment()


def module(name):
    return importlib.import_module(f"_eval_experiment_tool_selection.{name}")


def test_subset_provenance_and_reimport(bfcl):
    data = module("bfcl_data")
    cases = bfcl.load_cases()
    lock = json.loads((data.DIRECTORY / "sources.lock.json").read_text())
    rows = [case.provenance["original_row"] for case in cases]
    answers = [c.provenance["original_answer"] for c in cases if c.ground_truth["bfcl"]]
    assert data.make_cases(list(reversed(rows)), list(reversed(answers)), lock) == cases
    assert len(cases) == 18 and sum(not c.ground_truth["bfcl"] for c in cases) == 4
    assert not set(data.EXCLUDED) & {c.id for c in cases}
    for case in cases:
        assert case.provenance["source_revision"] == data.REVISION
        assert case.provenance["source_row_sha256"] == digest(case.provenance["original_row"])
        assert case.provenance["license"] == "Apache-2.0"
    with pytest.raises(ValueError, match="Duplicate"):
        data.make_cases(rows + rows[:1], answers, lock)
    with pytest.raises(ValueError, match="Missing"):
        data.make_cases(rows[1:], answers, lock)
    with pytest.raises(ValueError, match="Missing"):
        data.make_cases(rows, answers[1:], lock)
    with pytest.raises(ValueError, match="revision"):
        data.make_cases(rows, answers, {**lock, "revision": "main"})


def test_importer_rejects_wrong_hash_and_oversize_before_parsing(bfcl, tmp_path):
    data = module("bfcl_data")
    path = tmp_path / data.INPUT_PATH
    path.parent.mkdir(parents=True)
    path.write_text("{}\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        data.import_cache(tmp_path)
    path.write_bytes(b" " * (data.MAX_SOURCE_BYTES + 1))
    with pytest.raises(ValueError, match="bounded"):
        data.import_cache(tmp_path)


def test_converter_preserves_optional_fields_and_rejects_unsupported_types(bfcl):
    data = module("bfcl_data")
    original = bfcl.load_cases()[0].task_input["function"]
    converted = data.convert_tool(original)
    assert converted["parameters"]["required"] == ["base", "height"]
    assert converted["strict"] is False
    assert converted["description"] == original["description"]
    with pytest.raises(ValueError, match="Unsupported"):
        data.convert_schema({"type": "tuple"}, root=False)
    assert data.wire_name("math.factorial") == "math_factorial"
    with pytest.raises(ValueError, match="name"):
        data.wire_name("bad/name")


def test_official_checker_conformance_vectors(bfcl):
    cases = {c.id: c for c in bfcl.load_cases()}
    evidence = json.loads((bfcl.directory / "bfcl/conformance.json").read_text())
    lock = json.loads((bfcl.directory / "bfcl/sources.lock.json").read_text())
    assert evidence["source_sha256"] == lock["checker_sha256"]
    assert len(evidence["vectors"]) == 388
    for vector in evidence["vectors"]:
        grade = bfcl.grade(
            cases[vector["case_id"]], ModelResponse(parsed={"tool_calls": [vector["call"]]})
        )
        assert grade.passed == vector["official_passed"], vector


def test_all_answer_variants_and_target_invariance(bfcl):
    data, grader = module("bfcl_data"), module("bfcl_grader")
    cases, trials = validate(bfcl)
    assert len(trials) == 54
    for case in cases:
        previous_order = []
        original = data.convert_tool(case.task_input["function"])
        for condition in bfcl.spec.conditions:
            request = bfcl.build_request(case, condition)
            assert len(request.tools) == condition.variables["tool_count"]
            assert next(t for t in request.tools if t["name"] == original["name"]) == original
            order = [tool["name"] for tool in request.tools]
            assert [name for name in order if name in previous_order] == previous_order
            previous_order = order
            for variant in grader.answer_variants(case):
                assert grader.grade(case, ModelResponse(parsed=variant), request.tools).passed


def test_request_builder_cannot_leak_ground_truth_or_provenance(bfcl):
    for case in bfcl.load_cases():
        poisoned = case.model_copy(
            update={
                "ground_truth": {"secret_label": "GROUND_TRUTH_SENTINEL"},
                "provenance": {"secret_label": "PROVENANCE_SENTINEL"},
            }
        )
        for condition in bfcl.spec.conditions:
            assert bfcl.build_request(poisoned, condition) == bfcl.build_request(case, condition)


@pytest.mark.parametrize(
    "parsed",
    [None, "", {}, {"tool_calls": None}, {"tool_calls": [{"name": "x", "arguments": "{"}]}],
)
def test_malformed_is_never_no_call_success(bfcl, parsed):
    case = next(c for c in bfcl.load_cases() if c.id == "irrelevance_0")
    result = bfcl.grade(case, ModelResponse(parsed=parsed))
    assert not result.passed and not result.valid_output


def test_no_call_completed_only_and_refusal_failure(bfcl):
    case = bfcl.load_cases()[-1]
    assert bfcl.grade(
        case, ModelResponse(parsed={"tool_calls": [], "text": "No tool fits."})
    ).passed
    for status in ("incomplete", "error", "unknown"):
        assert not bfcl.grade(
            case, ModelResponse(parsed={"tool_calls": []}, finish_status=status)
        ).passed
    refusal = ModelResponse(
        parsed={"tool_calls": []},
        raw={"output": [{"type": "message", "content": [{"type": "refusal", "refusal": "No"}]}]},
    )
    assert not bfcl.grade(case, refusal).passed
    call = {"name": "lookup_record_invoice", "arguments": {"record_id": "1"}}
    result = bfcl.grade(case, ModelResponse(parsed={"tool_calls": [call]}))
    assert not result.passed and result.valid_output


def test_optional_units_wrong_values_types_extra_calls_and_float_rules(bfcl):
    grader = module("bfcl_grader")
    cases = {c.id: c for c in bfcl.load_cases()}
    case = cases["simple_python_7"]

    def result(args):
        return bfcl.grade(
            case,
            ModelResponse(
                parsed={"tool_calls": [{"name": "calculate_circumference", "arguments": args}]}
            ),
        )

    assert result({"radius": 4, "unit": "IN"}).passed
    assert not result({"radius": 4}).passed  # Schema optional; specified in question/gold.
    assert not result({"radius": 4, "unit": "cm"}).passed
    assert not result({"radius": True, "unit": "in"}).valid_output
    assert not result({"radius": 4.0, "unit": "in"}).valid_output
    variant = grader.answer_variants(case)[0]
    variant["tool_calls"] *= 2
    assert not bfcl.grade(case, ModelResponse(parsed=variant)).passed
    assert grader.compatible_type(2, {"type": "float"})
    assert not grader.compatible_type(True, {"type": "float"})
    assert not grader.compatible_type([1, 3], {"type": "array", "items": {"type": "float"}})


def test_tampered_dataset_rejected_and_live_remains_blocked(bfcl, tmp_path):
    cases = bfcl.load_cases()
    corrupt = copy.deepcopy(cases)
    corrupt[0].task_input["function"]["description"] = "tampered"
    with pytest.raises(ValueError, match="reproduce"):
        bfcl.validate(corrupt)
    with pytest.raises(ValueError, match="opt-in"):
        run(bfcl, results=tmp_path, mode="live", dry_run=True)
    with pytest.raises(ValueError, match="positive finite spend"):
        run(bfcl, results=tmp_path, mode="live", live=True, dry_run=True)


def test_frozen_manifest_reproduces_offline(bfcl):
    prepare = module("prepare_bfcl")
    actual = prepare.prepare()
    frozen = json.loads(prepare.MANIFEST.read_text(encoding="utf-8"))
    assert actual == frozen
    assert len(actual["requests"]) == 54 and actual["provider_calls"] == 0
    assert sum(row["smoke_proposal"] for row in actual["requests"]) == 6
    for row in actual["requests"]:
        assert row["request_hash"] == digest(row["request"])
        assert row["tool_order"] == [tool["name"] for tool in row["request"]["tools"]]
        assert "bfcl" not in row["request"] and "ground_truth" not in row["request"]


def test_smoke_proposal_matches_frozen_requests_and_budget(bfcl):
    prepare = module("prepare_bfcl")
    manifest = json.loads(prepare.MANIFEST.read_text(encoding="utf-8"))
    proposal = yaml.safe_load((bfcl.directory / "bfcl/smoke_proposal.yaml").read_text())
    rows = [r for r in manifest["requests"] if r["smoke_proposal"]]
    assert len(rows) == proposal["max_requests"] == 6
    assert {r["case_id"] for r in rows} == set(proposal["case_ids"])
    assert {r["tool_count"] for r in rows} == set(proposal["tool_counts"])
    assert (
        sum(r["conservative_input_tokens"] for r in rows)
        == proposal["conservative_input_tokens_total"]
    )
    assert sum(r["conservative_cost_usd"] for r in rows) == pytest.approx(
        proposal["conservative_standard_cost_usd"]
    )
    assert all(r["request"]["model"] == proposal["model"] for r in rows)
    assert proposal["owner_approval_required"] is True
    assert 2 * proposal["conservative_cache_write_cost_usd"] < proposal["max_spend_usd"]


def test_full_bfcl_matrix_runs_through_unchanged_engine_offline(bfcl, tmp_path):
    # Scripted answers test integration only, not performance. No network/credentials.
    conditions = [
        c.model_copy(update={"provider": "mock", "model": "deterministic-fixture"})
        for c in bfcl.spec.conditions
    ]
    bfcl.spec = bfcl.spec.model_copy(update={"conditions": conditions})
    grader = module("bfcl_grader")
    answers = {
        c.task_input["messages"][0]["content"]: grader.answer_variants(c)[0]
        for c in bfcl.load_cases()
    }

    class ScriptedProvider:
        def generate(self, request):
            return ModelResponse(parsed=answers[request.messages[-1]["content"]])

    report = run(bfcl, results=tmp_path, provider_factory=ScriptedProvider)
    assert report["run_status"] == "completed"
    from pathlib import Path

    records = [
        json.loads(line)
        for line in (Path(report["path"]) / "records.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(records) == 54
    assert all(r["status"] == "passed" for r in records)
    assert all(r["grade"]["grader_version"] == "0.2.0" for r in records)
    assert all(r["estimated_cost_usd"] == 0 for r in records)


@pytest.mark.parametrize("identifier", ["simple_python_0", "simple_python_13", "irrelevance_0"])
def test_bfcl_real_sdk_offline_transport(bfcl, identifier):
    case = next(c for c in bfcl.load_cases() if c.id == identifier)
    parsed = module("bfcl_grader").answer_variants(case)[0]
    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        calls = [
            {
                "type": "function_call",
                "id": "fc_local",
                "call_id": "call_local",
                "name": call["name"],
                "arguments": json.dumps(call["arguments"]),
                "status": "completed",
            }
            for call in parsed["tool_calls"]
        ]
        return httpx.Response(
            200,
            json={
                "id": "resp_local",
                "object": "response",
                "created_at": 0,
                "status": "completed",
                "model": "gpt-6-luna",
                "output": calls,
                "usage": {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
            },
        )

    with openai.OpenAI(
        api_key="fake-local-test",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        request = bfcl.build_request(case, bfcl.spec.conditions[0])
        response = OpenAIProvider(live=True, client=client).generate(request)
    assert bfcl.grade(case, response).passed
    assert all(tool["strict"] is False for tool in captured[0]["tools"])
    assert captured[0]["tool_choice"] == "auto"
    assert captured[0]["parallel_tool_calls"] is False
    assert captured[0]["store"] is False
    assert captured[0]["max_output_tokens"] == 4096
