"""BFCL treatment construction/validation within the existing tool-selection experiment."""

import json

from eval_lab.contracts import Condition, ExperimentSpec, ModelRequest, ModelResponse
from eval_lab.contracts import TestCase as Case
from eval_lab.core.hashes import canonical, digest

from . import bfcl_data as data
from . import bfcl_grader as grader

PROMPT_VERSION = "bfcl-selection-v1"
PROMPT = (
    "Select the appropriate function with exact arguments. If none applies, "
    "make no function call. Do not substitute a different task."
)
RECORDS = (
    "invoice customer ticket order warehouse shipment supplier purchase_order inventory product "
    "employee department expense refund subscription contract quote payment project timesheet "
    "asset location tax_code currency_rate campaign lead appointment service_plan audit_event"
).split()


def distractors() -> list[dict]:
    return [
        {
            "type": "function",
            "name": f"lookup_record_{name}",
            "description": (
                f"Read an existing {name} business record by its identifier. Returns stored "
                "fields only; does not calculate, solve, integrate, differentiate, or execute code."
            ),
            "parameters": {
                "type": "object",
                "properties": {"record_id": {"type": "string"}},
                "required": ["record_id"],
                "additionalProperties": False,
            },
            "strict": False,
        }
        for name in RECORDS
    ]


def build_request(case: Case, condition: Condition, spec: ExperimentSpec) -> ModelRequest:
    # Ground truth and provenance are intentionally never consulted by this path.
    tools = [data.convert_tool(case.task_input["function"])]
    tools += distractors()[: condition.variables["tool_count"] - 1]
    if len({t["name"] for t in tools}) != len(tools):
        raise ValueError("Function name conversion collision")
    tools.sort(key=lambda t: digest([spec.seed, case.id, t["name"]]))
    return ModelRequest(
        model=condition.model,
        messages=[{"role": "system", "content": PROMPT}, *case.task_input["messages"]],
        tools=tools,
        options=condition.options,
        max_output_tokens=spec.max_output_tokens,
    )


def validate(cases: list[Case], spec: ExperimentSpec) -> None:
    if spec.grader_id != "bfcl-python-subset" or spec.grader_version != grader.VERSION:
        raise ValueError("Unknown BFCL grader/version")
    if tuple(case.id for case in cases) != data.SELECTED_IDS:
        raise ValueError("BFCL subset must contain exactly the audited 18 IDs in frozen order")
    if [c.variables for c in spec.conditions] != [{"tool_count": n} for n in (5, 15, 30)] or len(
        {(c.provider, c.model, canonical(c.options)) for c in spec.conditions}
    ) != 1:
        raise ValueError("BFCL treatments must be 5/15/30 with fixed provider/model/options")
    if spec.repetitions != 1:
        raise ValueError("Development pilot freezes one repetition")
    lock = json.loads((data.DIRECTORY / "sources.lock.json").read_text(encoding="utf-8"))
    originals = [case.provenance["original_row"] for case in cases]
    answers = [case.provenance["original_answer"] for case in cases if case.ground_truth["bfcl"]]
    rebuilt = data.make_cases(originals, answers, lock)
    if cases != rebuilt:
        raise ValueError("Case/provenance does not reproduce pinned import")
    for case in cases:
        if digest(case.provenance["original_row"]) != lock["selected_rows"][case.id]["input"]:
            raise ValueError("Unpinned input row")
        if digest(case.provenance["original_answer"]) != lock["selected_rows"][case.id]["answer"]:
            raise ValueError("Unpinned answer row")
        for condition in spec.conditions:
            request = build_request(case, condition, spec)
            for variant in grader.answer_variants(case):
                if not grader.grade(case, ModelResponse(parsed=variant), request.tools).passed:
                    raise ValueError(f"Incompatible answer alternative: {case.id}")


def grade(case: Case, response: ModelResponse, *, request: ModelRequest):
    return grader.grade(case, response, request.tools)
