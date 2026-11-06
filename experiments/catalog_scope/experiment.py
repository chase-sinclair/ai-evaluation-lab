"""Experiment 02: one proposed call or a no-call decision at a fictional freight desk."""

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from eval_lab.contracts import Condition, ExperimentSpec, GradeResult, ModelRequest, ModelResponse
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical, digest

PROMPT = (
    "You work at the Northline Freight operations desk. Use at most one function "
    "when the user requests a record lookup or an authorized change. Use the supplied "
    "identifiers and literal values. Never invent a missing value. If a function is "
    "unnecessary or required information is missing, answer or ask for clarification "
    "without calling a function."
)
VERSION = "1.0.0"


class Experiment:
    def __init__(self, spec: ExperimentSpec, directory: Path):
        self.spec, self.directory = spec, directory
        tiers = yaml.safe_load((directory / "catalog.yaml").read_text(encoding="utf8"))
        self.tools = []
        for tier, size in (("base", 5), ("adjacent", 5), ("near", 10)):
            if len(tiers[tier]) != size:
                raise ValueError(f"Wrong size for {tier}")
            for name, description, fields in tiers[tier]:
                self.tools.append(
                    {
                        "type": "function",
                        "strict": True,
                        "name": name,
                        "description": description,
                        "parameters": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": fields,
                            "properties": {field: {"type": "string"} for field in fields},
                        },
                    }
                )

    def load_cases(self) -> list[Case]:
        dataset = self.spec.dataset
        rows = yaml.safe_load((self.directory / dataset.path).read_text(encoding="utf8"))
        cases = []
        for row in rows:
            if ("args" in row) == ("no_call" in row):
                raise ValueError("Specify arguments or a no-call rationale")
            expected = [{"name": row["focus"], "arguments": row["args"]}] if "args" in row else []
            cases.append(
                Case(
                    id=row["id"],
                    dataset_id=dataset.id,
                    dataset_version=dataset.version,
                    task_input={"text": row["text"]},
                    ground_truth={"tool_calls": expected},
                    split="authored",
                    provenance={
                        "focus": row["focus"],
                        "slot": row["slot"],
                        "no_call": row.get("no_call"),
                    },
                )
            )
        return cases

    def validate(self, cases: list[Case]) -> None:
        conditions = self.spec.conditions
        if (
            [c.variables for c in conditions] != [{"tool_count": n} for n in (5, 10, 20)]
            or len({(c.model, c.provider, canonical(c.options)) for c in conditions}) != 1
            or self.spec.repetitions != 1
            or self.spec.grader_version != VERSION
        ):
            raise ValueError("Expected three paired conditions and one fixed configuration")
        names = [t["name"] for t in self.tools]
        if len(set(names)) != 20 or len(cases) != 12:
            raise ValueError("Invalid experimental design")
        for tool in self.tools:
            Draft202012Validator.check_schema(tool["parameters"])
        slots = []
        for case in cases:
            focus, slot = case.provenance["focus"], case.provenance["slot"]
            if focus not in names[:5] or type(slot) is not int or not 0 <= slot < 8:
                raise ValueError("Invalid layout assignment")
            calls = case.ground_truth["tool_calls"]
            if calls:
                slots.append(slot)
                Draft202012Validator(self.tools[names.index(focus)]["parameters"]).validate(
                    calls[0]["arguments"]
                )
            elif not case.provenance["no_call"]:
                raise ValueError("Missing no-call rationale")
        if sorted(slots) != list(range(8)):
            raise ValueError("Required calls must cover all eight position strata")

    def build_request(self, case: Case, condition: Condition) -> ModelRequest:
        count = condition.variables["tool_count"]
        focus = case.provenance["focus"]
        ordered = sorted(
            self.tools[:count], key=lambda t: digest([self.spec.seed, case.id, t["name"]])
        )
        target = next(t for t in ordered if t["name"] == focus)
        ordered.remove(target)
        # Midpoint of one of eight equal-width rank strata. Same quantile for each case.
        ordered.insert((2 * case.provenance["slot"] + 1) * count // 16, target)
        return ModelRequest(
            model=condition.model,
            max_output_tokens=self.spec.max_output_tokens,
            tools=ordered,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": case.task_input["text"]},
            ],
        )

    def grade(self, case: Case, response: ModelResponse, *, request: ModelRequest) -> GradeResult:
        expected = case.ground_truth["tool_calls"]
        calls = response.parsed.get("tool_calls") if isinstance(response.parsed, dict) else None
        schemas = {t["name"]: t["parameters"] for t in request.tools}
        metrics = {}
        diagnostics = []
        outputs = response.raw.get("output", [])
        refused = any(
            c.get("type") == "refusal" for item in outputs for c in (item.get("content") or [])
        )
        malformed = not isinstance(calls, list) or not all(
            isinstance(c, dict) and isinstance(c.get("name"), str) for c in calls
        )
        if response.error or response.finish_status != "completed" or refused or malformed:
            diagnostics.append("invalid_response")
            return GradeResult(
                passed=False,
                valid_output=False,
                score=0,
                diagnostics=diagnostics,
                grader_version=VERSION,
            )
        if not calls and "output" in response.raw and not response.parsed.get("text", "").strip():
            return GradeResult(
                passed=False,
                valid_output=False,
                score=0,
                diagnostics=["empty_response"],
                grader_version=VERSION,
            )
        valid = True
        for call in calls:
            if call["name"] not in schemas:
                valid = False
                diagnostics.append("unoffered_tool")
            elif not Draft202012Validator(schemas[call["name"]]).is_valid(call.get("arguments")):
                valid = False
                diagnostics.append("invalid_arguments")
        if calls:
            metrics["offered_schema_valid"] = valid
        if len(calls) > 1:
            valid = False
            diagnostics.append("multiple_calls")
        if expected:
            identity = len(calls) == 1 and calls[0]["name"] == expected[0]["name"]
            metrics["correct_tool_on_required"] = identity
            if identity:
                metrics["exact_arguments_given_correct_tool"] = canonical(
                    calls[0].get("arguments")
                ) == canonical(expected[0]["arguments"])
            if not identity:
                diagnostics.append("wrong_tool_or_count" if calls else "missed_call")
            elif not metrics["exact_arguments_given_correct_tool"]:
                diagnostics.append("wrong_arguments")
        else:
            metrics["unnecessary_call_on_no_call"] = bool(calls)
            if calls:
                diagnostics.append("unnecessary_call")
        passed = valid and not diagnostics
        return GradeResult(
            passed=passed,
            valid_output=valid,
            score=float(passed),
            submetrics=metrics,
            diagnostics=diagnostics,
            grader_version=VERSION,
        )
