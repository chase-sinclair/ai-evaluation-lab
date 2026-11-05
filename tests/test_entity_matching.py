import importlib
from pathlib import Path

import pytest

from eval_lab.contracts import ModelResponse
from eval_lab.core.registry import load
from eval_lab.core.result_store import read_records

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    return tuple(
        importlib.import_module("experiments.entity_matching." + name)
        for name in ("experiment", "policies", "demo")
    )


def test_baseline_and_model_input_exclude_metadata(modules):
    model, _, _ = modules
    exp = load("entity_matching", ROOT / "experiments")
    a = exp.load_cases()[0]
    swapped = {"left": a.task_input["right"], "right": a.task_input["left"]}
    assert model.score(a.task_input) == model.score(swapped)
    condition = exp.spec.conditions[0]
    poisoned = a.model_copy(
        update={
            "task_input": {**a.task_input, "label": 1, "cluster_id": "secret"},
            "ground_truth": {"label": 1},
            "provenance": {"group": "secret"},
        }
    )
    assert exp.build_request(poisoned, condition) == exp.build_request(a, condition)
    assert model.score(a.task_input) == model.score(poisoned.task_input)
    assert model.uncertainty(model.THRESHOLD) > model.uncertainty(1)


@pytest.mark.parametrize(
    "parsed,finish,expected",
    [
        (" MATCH ", "completed", 1),
        ("NON_MATCH", "completed", 0),
        ("MATCH", "incomplete", None),
        ({"label": 1}, "completed", None),
        ("maybe MATCH", "completed", None),
    ],
)
def test_binary_predictions(modules, parsed, finish, expected):
    assert modules[0].prediction(ModelResponse(parsed=parsed, finish_status=finish)) == expected


def test_shared_runner_and_paired_replay(tmp_path, modules):
    _, policy, workflow = modules
    path, report = workflow.demo(tmp_path)
    records, warnings = read_records(path)
    assert not warnings and len(records) == 4
    assert [r["metrics"]["f1"] for r in report] == [0.8, 0.8, 1, 1]
    assert [len(r["selected_ids"]) for r in report] == [0, 1, 2, 4]
    assert report[3]["selected_ids"][:2] == report[2]["selected_ids"]
    assert report[3]["fallbacks"] == {"invalid_output": 1}
    assert all(r["estimated_api_usd"] == 0 and r["incremental_f1_per_usd"] is None for r in report)
    exp = load("entity_matching", ROOT / "experiments")
    partial = policy.replay(exp, records[1:])
    assert partial[-1]["fallbacks"]["missing_record"] == 1
    assert partial[-1]["estimated_api_usd"] is None and partial[-1]["metrics"]["n"] == 4
    with pytest.raises(ValueError, match="Duplicate"):
        policy.replay(exp, records + [records[0]])
    with pytest.raises(ValueError, match="incompatible"):
        policy.replay(exp, [records[0].model_copy(update={"request_hash": "incorrect"})])
    priced = [r.model_copy(update={"estimated_cost_usd": 0.001}) for r in records]
    assert policy.replay(exp, priced)[2]["incremental_f1_per_usd"] == pytest.approx(200)
