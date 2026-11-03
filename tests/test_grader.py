import pytest

from eval_lab.contracts import ModelResponse


@pytest.mark.parametrize(
    "prediction,diagnostic",
    [
        (
            {"tool_calls": [{"name": "customer_status", "arguments": {"invoice_id": "INV-1042"}}]},
            "wrong_name",
        ),
        (
            {"tool_calls": [{"name": "lookup_invoice", "arguments": {"invoice_id": "INV-wrong"}}]},
            "wrong_arguments",
        ),
        ({"tool_calls": []}, "missing_call"),
        (
            {
                "tool_calls": [
                    {"name": "lookup_invoice", "arguments": {"invoice_id": "INV-1042"}},
                    {"name": "lookup_invoice", "arguments": {"invoice_id": "INV-1042"}},
                ]
            },
            "extra_call",
        ),
        ({"tool_calls": [{"name": "lookup_invoice", "arguments": "{broken"}]}, "malformed_call"),
        ({"tool_calls": None}, "malformed_call"),
        ("I would call lookup_invoice", "malformed_call"),
        ({}, "malformed_call"),
        ({"tool_calls": [{"name": "unoffered", "arguments": {}}]}, "invalid_call"),
    ],
)
def test_failures(experiment, cases, prediction, diagnostic):
    result = experiment.grade(cases["invoice"], ModelResponse(parsed=prediction))
    assert not result.passed
    assert diagnostic in result.diagnostics


def test_no_call_and_correct_call(experiment, cases):
    for case_id in ("invoice", "no_call"):
        case = cases[case_id]
        assert experiment.grade(case, ModelResponse(parsed=case.ground_truth)).passed
    result = experiment.grade(cases["no_call"], ModelResponse(parsed=cases["invoice"].ground_truth))
    assert not result.passed and "extra_call" in result.diagnostics


@pytest.mark.parametrize("value", ["2", True, 2.0, None])
def test_typed_arguments(experiment, cases, value):
    prediction = {
        "tool_calls": [
            {
                "name": "search_orders",
                "arguments": {
                    "limit": value,
                    "customer_id": "CUS-208",
                },
            }
        ]
    }
    assert not experiment.grade(cases["orders"], ModelResponse(parsed=prediction)).passed


def test_object_key_order_equivalence(experiment, cases):
    prediction = {
        "tool_calls": [
            {"arguments": {"limit": 2, "customer_id": "CUS-208"}, "name": "search_orders"}
        ]
    }
    assert experiment.grade(cases["orders"], ModelResponse(parsed=prediction)).passed
