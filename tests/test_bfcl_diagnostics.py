import importlib

import pytest

from eval_lab.analysis.summary import summarize
from eval_lab.contracts import ModelResponse
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run


@pytest.fixture
def bfcl(experiment):
    return importlib.import_module("_eval_experiment_tool_selection.prepare_bfcl").load_experiment()


@pytest.mark.parametrize(
    "interval,schema,exact",
    [
        ([1, 3], True, False),
        ([1.0, 3.0], True, True),
        ([1.0, 4.0], True, False),
        ([True, 3], False, False),
        ("1,3", False, False),
    ],
)
def test_selection_schema_and_benchmark_are_distinct(bfcl, interval, schema, exact):
    case = next(c for c in bfcl.load_cases() if c.id == "simple_python_13")
    request = bfcl.build_request(case, bfcl.spec.conditions[0])
    response = ModelResponse(
        parsed={
            "tool_calls": [
                {
                    "name": "calculate_area_under_curve",
                    "arguments": {"function": "x**2", "interval": interval},
                }
            ]
        }
    )
    result = bfcl.grade(case, response, request=request)
    assert result.passed is exact
    assert result.submetrics["benchmark_exact_correct"] is exact
    assert result.submetrics["schema_valid_arguments"] is schema
    assert result.submetrics["tool_selection_correct"] is True
    assert result.grader_version == "0.2.1"
    assert result.diagnostics_version == "bfcl-diagnostics-v1"


@pytest.mark.parametrize(
    "parsed,selection,schema",
    [
        ({"tool_calls": []}, False, True),
        ({"tool_calls": [{"name": "calculate_triangle_area", "arguments": "broken"}]}, True, False),
        ({"tool_calls": [{"name": "unoffered", "arguments": {}}]}, False, False),
        (
            {"tool_calls": [{"name": "calculate_triangle_area", "arguments": {}, "extra": 1}]},
            False,
            False,
        ),
        ({"tool_calls": [], "extra": 1}, False, False),
        (None, False, False),
    ],
)
def test_diagnostics_malformed_and_unoffered(bfcl, parsed, selection, schema):
    case = next(c for c in bfcl.load_cases() if c.id == "simple_python_0")
    request = bfcl.build_request(case, bfcl.spec.conditions[0])
    result = bfcl.grade(case, ModelResponse(parsed=parsed), request=request)
    assert result.submetrics["tool_selection_correct"] is selection
    assert result.submetrics["schema_valid_arguments"] is schema


def test_no_call_and_incomplete_diagnostics(bfcl):
    case = next(c for c in bfcl.load_cases() if c.id == "irrelevance_0")
    request = bfcl.build_request(case, bfcl.spec.conditions[0])
    for status in ["completed", "incomplete"]:
        result = bfcl.grade(
            case, ModelResponse(parsed={"tool_calls": []}, finish_status=status), request=request
        )
        assert all(value is (status == "completed") for value in result.submetrics.values())


def test_summary_diagnostics_do_not_change_primary_or_invent_missing_metrics(experiment, tmp_path):
    result = run(experiment, results=tmp_path)
    records, _ = read_records(tmp_path / result["run_id"])
    row = records[0]
    augmented = row.model_copy(
        update={
            "grade": row.grade.model_copy(
                update={
                    "submetrics": {
                        "tool_selection_correct": True,
                        "benchmark_exact_correct": False,
                    },
                    "diagnostics_version": "test-v1",
                }
            )
        }
    )
    rows = [augmented, records[1]]
    summary = summarize(rows, 3)
    metric = summary["diagnostic_metrics"]["tool_selection_correct"]
    assert metric == {"measured_records": 1, "unmeasured_records": 1, "mean": 1}
    assert summary["correct"] == sum(r.status == "passed" for r in rows)
    assert summary["known_cached_read_tokens"] is None
    assert summary["unknown_cache_partition_records"] == 2
    assert (
        summary["conditions"][row.condition_id]["diagnostic_metrics"]["benchmark_exact_correct"][
            "mean"
        ]
        == 0
    )
