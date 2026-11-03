import pytest
from pydantic import ValidationError

from eval_lab.contracts import ExperimentSpec
from eval_lab.core.runner import validate


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_spend_usd", float("nan")),
        ("max_spend_usd", float("inf")),
        ("max_spend_usd", -1),
        ("max_requests", 0),
        ("max_requests", True),
        ("max_output_tokens", 0),
        ("repetitions", 0),
        ("unexpected", 1),
    ],
)
def test_reject_invalid_config(experiment, field, value):
    data = experiment.spec.model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        ExperimentSpec.model_validate(data)


def test_duplicate_condition(experiment):
    data = experiment.spec.model_dump()
    data["conditions"].append(data["conditions"][0])
    with pytest.raises(ValidationError):
        ExperimentSpec.model_validate(data)


def test_control_and_dataset_validation(experiment, monkeypatch):
    cases = experiment.load_cases()
    monkeypatch.setattr(experiment, "load_cases", lambda: cases + [cases[0]])
    with pytest.raises(ValueError, match="unique"):
        validate(experiment)
    monkeypatch.setattr(
        experiment, "load_cases", lambda: [cases[0].model_copy(update={"dataset_version": "wrong"})]
    )
    with pytest.raises(ValueError, match="versions"):
        validate(experiment)


def test_controls_are_nested_and_target_unchanged(experiment, cases):
    validate(experiment)
    for case in cases.values():
        requests = [experiment.build_request(case, c) for c in experiment.spec.conditions]
        assert [len(r.tools) for r in requests] == [5, 15, 30]
        assert all(r.messages == requests[0].messages for r in requests)
        for smaller, larger in zip(requests, requests[1:], strict=False):
            large_map = {t["name"]: t for t in larger.tools}
            assert all(t == large_map[t["name"]] for t in smaller.tools)
            assert [t for t in larger.tools if t in smaller.tools] == smaller.tools
        assert "ground_truth" not in requests[0].model_dump()


def test_schema_and_grader_version_checked(experiment, cases):
    broken = cases["orders"].model_copy(
        update={
            "ground_truth": {
                "tool_calls": [
                    {"name": "search_orders", "arguments": {"customer_id": "x", "limit": "two"}}
                ]
            }
        }
    )
    with pytest.raises(Exception, match="integer"):
        experiment.validate([broken])
    experiment.spec = experiment.spec.model_copy(update={"grader_version": "unknown"})
    with pytest.raises(ValueError, match="grader"):
        experiment.validate(list(cases.values()))
