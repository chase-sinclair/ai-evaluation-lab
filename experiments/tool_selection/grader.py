"""Frozen equivalence: object key order ignored; scalar types and strings exact."""

from eval_lab.contracts import GradeResult, ModelResponse
from eval_lab.contracts import TestCase as Case

VERSION = "0.1.0"


def typed_equal(left, right) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(
            typed_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return left == right


def grade(case: Case, response: ModelResponse) -> GradeResult:
    expected = case.ground_truth["tool_calls"]
    prediction = response.parsed
    diagnostics = []
    calls = prediction.get("tool_calls") if isinstance(prediction, dict) else None
    valid = isinstance(calls, list) and all(
        isinstance(c, dict)
        and set(c) == {"name", "arguments"}
        and isinstance(c["name"], str)
        and isinstance(c["arguments"], dict)
        for c in calls
    )
    if not valid:
        diagnostics.append("malformed_call")
        count_ok = name_ok = args_ok = False
    else:
        count_ok = len(calls) == len(expected)
        if len(calls) < len(expected):
            diagnostics.append("missing_call")
        if len(calls) > len(expected):
            diagnostics.append("extra_call")
        name_ok = count_ok and all(
            a["name"] == b["name"] for a, b in zip(calls, expected, strict=True)
        )
        args_ok = count_ok and all(
            typed_equal(a["arguments"], b["arguments"])
            for a, b in zip(calls, expected, strict=True)
        )
        if count_ok and not name_ok:
            diagnostics.append("wrong_name")
        if count_ok and not args_ok:
            diagnostics.append("wrong_arguments")
    passed = valid and count_ok and name_ok and args_ok
    return GradeResult(
        passed=passed,
        valid_output=valid,
        score=float(passed),
        grader_version=VERSION,
        submetrics={
            "well_formed": valid,
            "call_count": count_ok,
            "tool_name": name_ok,
            "arguments": args_ok,
            "full_call": passed,
        },
        diagnostics=diagnostics,
    )
