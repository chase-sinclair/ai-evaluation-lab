import pytest

from eval_lab.analysis.summary import summarize
from eval_lab.core.result_store import read_records
from eval_lab.core.runner import run


def fixture_records(experiment, tmp_path):
    result = run(experiment, results=tmp_path)
    return read_records(tmp_path / result["run_id"])[0]


def test_condition_denominators_and_pairing(experiment, tmp_path):
    rows = fixture_records(experiment, tmp_path)
    result = summarize(rows, 15, {"tools_5": 5, "tools_15": 5, "tools_30": 5})
    assert result["correct"] == 10
    assert result["conditions"]["tools_5"]["accuracy"] == 0.8
    assert result["conditions"]["tools_15"]["invalid_output_rate"] == 0.2
    pair = next(
        p
        for p in result["paired_comparisons"]
        if p["left"] == "tools_15" and p["right"] == "tools_5"
    )
    assert pair["matched_cases"] == 5 and pair["accuracy_difference"] == 0.2
    partial = summarize([], 15, {"tools_5": 5, "tools_15": 5, "tools_30": 5})
    assert partial["conditions"]["tools_5"]["accuracy"] == 0
    assert partial["paired_comparisons"][0]["accuracy_difference"] is None


def test_repeats_are_averaged_within_case_and_missing_not_imputed(experiment, tmp_path):
    base = fixture_records(experiment, tmp_path)[0]
    rows = []
    for case, repeats in [("a", 1), ("b", 3)]:
        for condition in ["left", "right"]:
            for repeat in range(repeats):
                rows.append(
                    base.model_copy(
                        update={
                            "case_id": case,
                            "condition_id": condition,
                            "repeat": repeat,
                            "status": "task_failed"
                            if case == "a" and condition == "left"
                            else "passed",
                            "estimated_cost_usd": None if case == "a" else 0,
                        }
                    )
                )
    result = summarize(rows, 8)
    pair = result["paired_comparisons"][0]
    assert pair["matched_cases"] == 2 and pair["accuracy_difference"] == 0.5
    assert pair["cost_paired_cases"] == 1
    assert result["estimated_cost_usd"] is None
    partial = summarize(rows[:-1], 8)["paired_comparisons"][0]
    assert partial["matched_cases"] == 1 and partial["excluded_cases"] == 1
    with pytest.raises(ValueError, match="Duplicate"):
        summarize(rows + rows[:1], 9)


def test_provider_failure_rates_and_dataset_identity(experiment, tmp_path):
    base = fixture_records(experiment, tmp_path)[0]
    rows = [
        base.model_copy(update={"condition_id": "a", "status": "provider_error"}),
        base.model_copy(update={"condition_id": "b", "dataset_version": "different"}),
    ]
    result = summarize(rows, 4, {"a": 2, "b": 2})
    assert result["conditions"]["a"]["provider_error_rate"] == 0.5
    assert result["paired_comparisons"][0]["matched_cases"] == 0
