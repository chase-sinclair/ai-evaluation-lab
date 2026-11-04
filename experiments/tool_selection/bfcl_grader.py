"""Subset compatibility with pinned BFCL Python AST rules; never executes answers.

Independent narrow adaptation of Gorilla's Apache-2.0 checker; see bfcl/NOTICE.md.
Unsupported schema/answer families are rejected at import/validation, not generalized.
"""

import itertools
import math
import re
from typing import Any

from jsonschema import Draft202012Validator

from eval_lab.contracts import GradeResult, ModelResponse
from eval_lab.contracts import TestCase as Case

from .bfcl_data import wire_name

VERSION = "0.2.1"
TYPES = {"integer": int, "float": float, "string": str, "boolean": bool, "array": list}


def normalize(value: Any) -> Any:
    if type(value) is str:
        return re.sub(r"[ \,\.\/\-\_\*\^]", "", value).lower().replace("'", '"')
    if type(value) is list:
        return [normalize(item) for item in value]
    return value


def compatible_type(value: Any, schema: dict, *, nested: bool = False) -> bool:
    kind = schema["type"]
    if kind == "float" and type(value) is int and not nested:
        return True  # Official top-level Python int -> float coercion.
    if type(value) is not TYPES[kind]:
        return False
    if kind == "float" and not math.isfinite(value):
        return False
    if kind == "array":
        return all(compatible_type(item, schema["items"], nested=True) for item in value)
    return True


def valid_arguments(arguments: dict, schema: dict) -> bool:
    properties = schema["properties"]
    return set(schema["required"]) <= arguments.keys() <= properties.keys() and all(
        compatible_type(value, properties[key]) for key, value in arguments.items()
    )


def answer_variants(case: Case) -> list[dict]:
    """Enumerate allowed omissions and representations for offline validation only."""
    expected = case.ground_truth["bfcl"]
    if not expected:
        return [{"tool_calls": []}]
    function = case.task_input["function"]
    alternatives = expected[0][function["name"]]
    required = function["parameters"]["required"]
    variants = []
    for values in itertools.product(*alternatives.values()):
        arguments = dict(zip(alternatives, values, strict=True))
        # Empty string means optional absence, not a request to inject a blank argument.
        arguments = {k: v for k, v in arguments.items() if v != "" or k in required}
        variants.append(
            {"tool_calls": [{"name": wire_name(function["name"]), "arguments": arguments}]}
        )
    return variants


def _grade_exact(case: Case, response: ModelResponse, offered: list[dict]) -> GradeResult:
    def result(passed: bool, valid: bool, reason: str) -> GradeResult:
        return GradeResult(
            passed=passed,
            score=float(passed),
            valid_output=valid,
            grader_version=VERSION,
            submetrics={"full_call": passed, "well_formed": valid},
            diagnostics=[] if passed else [reason],
        )

    parsed = response.parsed
    if response.error or response.finish_status != "completed":
        return result(False, False, "response_not_completed")
    if any(
        content.get("type") == "refusal"
        for item in response.raw.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
    ):
        return result(False, False, "refusal")
    if (
        type(parsed) is not dict
        or set(parsed) - {"tool_calls", "text"}
        or "tool_calls" not in parsed
        or ("text" in parsed and type(parsed["text"]) is not str)
        or type(parsed["tool_calls"]) is not list
    ):
        return result(False, False, "malformed_response")
    calls = parsed["tool_calls"]
    offered_names = {tool["name"] for tool in offered}
    original = case.task_input["function"]
    target = wire_name(original["name"])
    for call in calls:
        if (
            type(call) is not dict
            or set(call) != {"name", "arguments"}
            or type(call["name"]) is not str
            or type(call["arguments"]) is not dict
        ):
            return result(False, False, "malformed_call")
        if call["name"] not in offered_names:
            return result(False, False, "unoffered_function")
        schema = (
            original["parameters"]
            if call["name"] == target
            else {"properties": {"record_id": {"type": "string"}}, "required": ["record_id"]}
        )
        if not valid_arguments(call["arguments"], schema):
            return result(False, False, "invalid_arguments")
    expected = case.ground_truth["bfcl"]
    if not expected:
        return result(not calls, True, "expected_no_call")
    if len(calls) != 1 or calls[0]["name"] != target:
        return result(False, True, "wrong_call_count_or_function")
    arguments = calls[0]["arguments"]
    alternatives = expected[0][original["name"]]
    for key, allowed in alternatives.items():
        if key not in arguments:
            if "" not in allowed:
                return result(False, True, "missing_answer_argument")
        elif not any(normalize(arguments[key]) == normalize(value) for value in allowed):
            return result(False, True, "incorrect_argument")
    return result(True, True, "")


def grade(case: Case, response: ModelResponse, offered: list[dict]) -> GradeResult:
    """Prospective diagnostics v1; strict primary grader 0.2.1 is unchanged."""
    exact = _grade_exact(case, response, offered)
    parsed = response.parsed
    envelope = (
        response.finish_status == "completed"
        and not response.error
        and type(parsed) is dict
        and not set(parsed) - {"tool_calls", "text"}
        and ("text" not in parsed or type(parsed["text"]) is str)
        and type(parsed.get("tool_calls")) is list
        and "refusal" not in exact.diagnostics
    )
    calls = parsed["tool_calls"] if envelope else []
    named = envelope and all(
        type(c) is dict and set(c) == {"name", "arguments"} and type(c["name"]) is str
        for c in calls
    )
    schemas = {t["name"]: t["parameters"] for t in offered}
    schema_valid = named and all(
        c["name"] in schemas
        and type(c["arguments"]) is dict
        and Draft202012Validator(schemas[c["name"]]).is_valid(c["arguments"])
        for c in calls
    )
    expected_names = (
        [wire_name(case.task_input["function"]["name"])] if case.ground_truth["bfcl"] else []
    )
    selected = (
        named
        and all(c["name"] in schemas for c in calls)
        and ([c["name"] for c in calls] == expected_names)
    )
    return exact.model_copy(
        update={
            "diagnostics_version": "bfcl-diagnostics-v1",
            "submetrics": {
                **exact.submetrics,
                "schema_valid_arguments": bool(schema_valid),
                "tool_selection_correct": bool(selected),
                "benchmark_exact_correct": exact.passed,
            },
        }
    )
