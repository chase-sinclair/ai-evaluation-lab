import json
from pathlib import Path

from jsonschema import Draft202012Validator

from eval_lab.contracts import Condition, ExperimentSpec, ModelRequest, ModelResponse
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import digest

from . import bfcl_integration
from .bfcl_data import DATASET_ID
from .grader import VERSION, grade


def tool(name, description, properties):
    return {
        "type": "function",
        "name": name,
        "description": description,
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": False,
        },
    }


STRING = {"type": "string"}
TARGETS = [
    tool("lookup_invoice", "Read an invoice by its identifier.", {"invoice_id": STRING}),
    tool("customer_status", "Read a customer's account status.", {"customer_id": STRING}),
    tool(
        "create_ticket",
        "Create a support ticket.",
        {"title": STRING, "priority": {"type": "string", "enum": ["low", "high"]}},
    ),
    tool(
        "search_orders",
        "Read a customer's orders, limited to the requested count.",
        {"customer_id": STRING, "limit": {"type": "integer", "minimum": 1}},
    ),
]
DISTRACTORS = [
    tool(
        f"read_{name}", f"Read the {name.replace('_', ' ')} business record.", {"record_id": STRING}
    )
    for name in (
        "warehouse",
        "shipment",
        "supplier",
        "purchase_order",
        "inventory",
        "product",
        "employee",
        "department",
        "expense",
        "refund",
        "subscription",
        "contract",
        "quote",
        "payment",
        "project",
        "timesheet",
        "asset",
        "location",
        "tax_code",
        "currency_rate",
        "campaign",
        "lead",
        "appointment",
        "service_plan",
        "audit_event",
        "stock_transfer",
    )
]


class Experiment:
    def __init__(self, spec: ExperimentSpec, directory: Path):
        self.spec, self.directory = spec, directory

    def load_cases(self) -> list[Case]:
        path = (self.directory / self.spec.dataset.path).resolve()
        if not path.is_relative_to(self.directory):
            raise ValueError("Fixture must be inside experiment directory")
        return [
            Case.model_validate(json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
        ]

    def build_request(self, case: Case, condition: Condition) -> ModelRequest:
        if self.spec.dataset.id == DATASET_ID:
            return bfcl_integration.build_request(case, condition, self.spec)
        count = condition.variables["tool_count"]
        tools = TARGETS + DISTRACTORS[: count - len(TARGETS)]
        # One ranking per case: increasing counts add tools and preserve relative target order.
        tools = sorted(tools, key=lambda t: digest([self.spec.seed, case.id, t["name"]]))
        return ModelRequest(
            model=condition.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Select the appropriate function with exact arguments. If none applies, "
                        "make no function call. Do not substitute a different task."
                    ),
                },
                {"role": "user", "content": case.task_input["text"]},
            ],
            tools=tools,
            options=condition.options,
            max_output_tokens=self.spec.max_output_tokens,
        )

    def validate(self, cases: list[Case]) -> None:
        if self.spec.dataset.id == DATASET_ID:
            bfcl_integration.validate(cases, self.spec)
            return
        if self.spec.grader_id != "structured-tool-call" or self.spec.grader_version != VERSION:
            raise ValueError("Unknown grader or version")
        settings = {
            (c.provider, c.model, json.dumps(c.options, sort_keys=True))
            for c in self.spec.conditions
        }
        if len(settings) != 1:
            raise ValueError("Tool-count treatments must hold provider/model/options fixed")
        counts = []
        for condition in self.spec.conditions:
            count = condition.variables.get("tool_count")
            if type(count) is not int or not 5 <= count <= 30:
                raise ValueError("tool_count must be an integer from 5 through 30")
            if set(condition.variables) != {"tool_count"}:
                raise ValueError("Only tool_count may vary")
            counts.append(count)
        if len(set(counts)) != len(counts):
            raise ValueError("Tool-count conditions must be distinct")
        schemas = {t["name"]: t for t in TARGETS + DISTRACTORS}
        for schema in schemas.values():
            Draft202012Validator.check_schema(schema["parameters"])
        for case in cases:
            if set(case.task_input) != {"text"} or not isinstance(case.task_input["text"], str):
                raise ValueError("Expected one text input")
            if set(case.ground_truth) != {"tool_calls"}:
                raise ValueError("Expected structured answer key")
            expected = case.ground_truth["tool_calls"]
            probe = grade(case, ModelResponse(parsed={"tool_calls": expected}))
            if not probe.passed:
                raise ValueError("Malformed answer key")
            if not expected and not case.provenance.get("no_call_review"):
                raise ValueError("No-call case requires documented semantic review")
            for call in expected:
                if call["name"] not in {t["name"] for t in TARGETS}:
                    raise ValueError("Target not offered in every condition")
                Draft202012Validator(schemas[call["name"]]["parameters"]).validate(
                    call["arguments"]
                )

    def grade(self, case: Case, response: ModelResponse, *, request: ModelRequest | None = None):
        if self.spec.dataset.id == DATASET_ID:
            if request is None:
                raise ValueError("BFCL grading requires the actual request")
            return bfcl_integration.grade(case, response, request=request)
        result = grade(case, response)
        if result.submetrics["well_formed"]:
            schemas = {t["name"]: t["parameters"] for t in TARGETS + DISTRACTORS}
            for call in response.parsed["tool_calls"]:
                if call["name"] not in schemas or not Draft202012Validator(
                    schemas[call["name"]]
                ).is_valid(call["arguments"]):
                    return result.model_copy(
                        update={
                            "passed": False,
                            "valid_output": False,
                            "score": 0.0,
                            "diagnostics": [*result.diagnostics, "invalid_call"],
                            "submetrics": {
                                **result.submetrics,
                                "schema_valid": False,
                                "full_call": False,
                            },
                        }
                    )
        return result
